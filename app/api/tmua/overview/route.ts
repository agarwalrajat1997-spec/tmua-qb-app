import { JANUARY_EXAM_DATE, JANUARY_EXAM_DATE_LABEL, JANUARY_EXAM_TIMESTAMP } from "@/lib/exam-countdown";
import { readPreparationRankSnapshot, requestPreparationRankRefresh } from "@/lib/server/preparation-rank-cache";

import { NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

import { createSupabaseServerClient } from "@/lib/supabase/server";
import { isMissingSession, serviceFetch, withServiceTimeout } from "@/lib/auth/service-recovery";

import {
  adaptTmuaConversionProfiles,
  adaptTmuaQbEvent,
  adaptTmuaTestEvaluation,
} from "@/lib/server/tmua-predictor-v1-evidence-adapter";

import {
  calculateTmuaPredictorV1,
} from "@/lib/server/tmua-predictor-v1-engine";
import { applyTmuaHighScoreEvidenceGate } from "@/lib/server/tmua-predictor-v1_1-policy";
import { applyStandardTimeTmuaEvaluations } from "@/lib/server/practice-predictor-overlay";
import {
  TMUA_PREDICTIVE_2026_ID,
  TMUA_PREDICTIVE_2026_CATALOG,
  buildTmuaPredictive2026Evaluations,
} from "@/lib/server/tmua-predictive-2026";

import {
  buildTmuaPredictionSnapshotInsert,
} from "@/lib/server/tmua-predictor-v1-snapshot";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 300;

const NO_STORE_HEADERS = {
  "Cache-Control":
    "no-store, no-cache, must-revalidate, max-age=0",
};

function json(
  data: unknown,
  status = 200,
) {
  return NextResponse.json(
    data,
    {
      status,
      headers: { ...NO_STORE_HEADERS, ...(status === 503 ? { "Retry-After": "30" } : {}) },
    },
  );
}

function requiredEnv(
  names: string[],
): string {
  for (
    const name of names
  ) {
    const value =
      process.env[name];

    if (value) {
      return value;
    }
  }

  throw new Error(
    `Missing environment variable: ${names.join(" or ")}`,
  );
}

function adminClient() {
  const url =
    requiredEnv([
      "NEXT_PUBLIC_SUPABASE_URL",
      "SUPABASE_URL",
    ]);

  const key =
    requiredEnv([
      "SUPABASE_SERVICE_ROLE_KEY",
      "SUPABASE_SERVICE_KEY",
    ]);

  return createClient(
    url,
    key,
    {
      global: { fetch: serviceFetch },
      auth: {
        persistSession: false,
        autoRefreshToken: false,
      },
    },
  );
}

async function readAll(
  fetchPage:
    (
      from: number,
      to: number,
    ) => PromiseLike<any> & { retry?: (enabled: boolean) => PromiseLike<any> },
): Promise<any[]> {
  const pageSize =
    1000;

  const rows: any[] =
    [];

  let from =
    0;

  while (true) {
    const to =
      from +
      pageSize -
      1;

    const query = fetchPage(from, to);
    const {
      data,
      error,
    } = await withServiceTimeout(typeof query.retry === "function" ? query.retry(false) : query);

    if (error) {
      throw new Error(
        error.message ||
        "Supabase read failed",
      );
    }

    const page =
      Array.isArray(data)
        ? data
        : [];

    rows.push(
      ...page,
    );

    if (
      page.length <
      pageSize
    ) {
      break;
    }

    from +=
      pageSize;

    if (
      from >
      100000
    ) {
      throw new Error(
        "Predictor evidence pagination exceeded safety limit",
      );
    }
  }

  return rows;
}

function canonicalQidFromMetadata(
  metadata: unknown,
): string | null {
  if (
    !metadata ||
    typeof metadata !==
      "object" ||
    Array.isArray(metadata)
  ) {
    return null;
  }

  const value =
    (
      metadata as
        Record<
          string,
          unknown
        >
    ).canonical_qid;

  if (
    typeof value !==
      "string"
  ) {
    return null;
  }

  const normalized =
    value.trim();

  return normalized ||
    null;
}

const TMUA_EXAM_DATE = JANUARY_EXAM_DATE;
const TMUA_EXAM_DATE_LABEL = JANUARY_EXAM_DATE_LABEL;

function preparationLondonDayUtc(
  date: Date,
): number {
  const parts =
    new Intl.DateTimeFormat(
      "en-GB",
      {
        timeZone:
          "Europe/London",

        year:
          "numeric",

        month:
          "2-digit",

        day:
          "2-digit",
      },
    ).formatToParts(date);

  const values =
    new Map(
      parts.map(
        (part) => [
          part.type,
          part.value,
        ],
      ),
    );

  const year =
    Number(
      values.get("year"),
    );

  const month =
    Number(
      values.get("month"),
    );

  const day =
    Number(
      values.get("day"),
    );

  if (
    !Number.isInteger(year) ||
    !Number.isInteger(month) ||
    !Number.isInteger(day)
  ) {
    throw new Error(
      "Unable to resolve London calendar date",
    );
  }

  return Date.UTC(
    year,
    month - 1,
    day,
  );
}

function preparationCountdown(
  asOf: Date,
) {
  const today =
    preparationLondonDayUtc(
      asOf,
    );

  const exam =
    JANUARY_EXAM_TIMESTAMP;

  const daysToTmua =
    Math.max(
      0,
      Math.round(
        (
          exam -
          today
        ) /
        (
          24 *
          60 *
          60 *
          1000
        ),
      ),
    );

  return {
    daysToTmua,

    examDate:
      TMUA_EXAM_DATE,

    examDateLabel:
      TMUA_EXAM_DATE_LABEL,
  };
}

export async function GET() {
  try {
    // Authentication uses the existing user session.
    const supabase =
      await createSupabaseServerClient();

    const {
      data: {
        user,
      },
      error:
        userError,
    } =
      await withServiceTimeout(supabase.auth.getUser());
    if (userError && !isMissingSession(userError)) {
      return json({ ok: false, error: "Authentication service temporarily unavailable" }, 503);
    }

    if (
      userError ||
      !user
    ) {
      return json(
        {
          ok: false,
          error:
            "Unauthorized",
        },
        401,
      );
    }

    // All authority-sensitive reads and snapshot insertion
    // occur server-side using the service role.
    const admin =
      adminClient();

    // Coalesced, leased maintenance runs after the response; never scan the
    // cohort while a student waits for their current-user predictor.
    requestPreparationRankRefresh(admin, "tmua");

    const [
      conversionRows,
      catalogRows,
      evaluationRows,
      questionRows,
      qbRows,
      predictiveAttemptRows,
    ] =
      await Promise.all([
        readAll(
          (from, to) =>
            admin
              .from(
                "tmua_score_conversion_profiles",
              )
              .select(
                "profile,score_values",
              )
              .order(
                "profile",
                {
                  ascending:
                    true,
                },
              )
              .range(
                from,
                to,
              ),
        ),

        readAll(
          (from, to) =>
            admin
              .from(
                "tmua_test_catalog",
              )
              .select(
                "test_id,topic_breadth,predictor_enabled,score_conversion_profile,base_weight,minimum_partial_answered,minimum_full_weight_answered,minimum_average_seconds",
              )
              .eq(
                "predictor_enabled",
                true,
              )
              .order(
                "test_id",
                {
                  ascending:
                    true,
                },
              )
              .range(
                from,
                to,
              ),
        ),

        readAll(
          (from, to) =>
            admin
              .from(
                "tmua_test_attempt_evaluations",
              )
              .select(
                [
                  "user_id",
                  "test_id",
                  "attempt_id",
                  "attempt_number",
                  "evaluated_at",
                  "predictor_eligible",
                  "combined_score_eligible",
                  "authoritative_tmua_score9",
                  "effective_weight",
                  "paper_1_raw_score",
                  "paper_1_effective_weight",
                  "paper_2_raw_score",
                  "paper_2_effective_weight",
                ].join(","),
              )
              .eq(
                "user_id",
                user.id,
              )
              .order(
                "evaluated_at",
                {
                  ascending:
                    true,
                },
              )
              .range(
                from,
                to,
              ),
        ),

        readAll(
          (from, to) =>
            admin
              .from(
                "tmua_qb_questions",
              )
              .select(
                "qid,topic,answer,is_active",
              )
              .eq(
                "is_active",
                true,
              )
              .order(
                "qid",
                {
                  ascending:
                    true,
                },
              )
              .range(
                from,
                to,
              ),
        ),

        readAll(
          (from, to) =>
            admin
              .from(
                "tmua_qb_attempt_events",
              )
              .select(
                [
                  "user_id",
                  "id",
                  "source",
                  "history_quality",
                  "predictor_eligible",
                  "metadata",
                  "selected_answer",
                  "attempted_at",
                ].join(","),
              )
              .eq(
                "user_id",
                user.id,
              )
              .eq(
                "source",
                "qb-progress-trigger-v2",
              )
              .eq(
                "history_quality",
                "observed",
              )
              .order(
                "attempted_at",
                {
                  ascending:
                    true,
                },
              )
              .range(
                from,
                to,
              ),
        ),
        readAll((from, to) => admin.from("practice_test_attempts")
          .select("id,user_id,test_id,submitted_at,answers,time_spent,predictor_metadata")
          .eq("user_id", user.id)
          .or(`test_id.eq.${TMUA_PREDICTIVE_2026_ID},predictor_metadata->standard_time_estimate->>policy_version.eq.ts-standard-time-equivalent-v1`)
          .order("submitted_at", { ascending: true }).range(from, to)),
      ]);

    catalogRows.push(TMUA_PREDICTIVE_2026_CATALOG);
    evaluationRows.splice(0, evaluationRows.length,
      ...evaluationRows.filter(row => row.test_id !== TMUA_PREDICTIVE_2026_ID),
      ...buildTmuaPredictive2026Evaluations(predictiveAttemptRows));
    evaluationRows.splice(0, evaluationRows.length,
      ...applyStandardTimeTmuaEvaluations(evaluationRows, predictiveAttemptRows, conversionRows, catalogRows));

    if (
      conversionRows.length !==
      12
    ) {
      throw new Error(
        `Expected exactly 12 conversion profiles; found ${conversionRows.length}`,
      );
    }

    const catalogByTestId =
      new Map<
        string,
        any
      >();

    for (
      const row of
      catalogRows
    ) {
      if (
        row &&
        typeof row.test_id ===
          "string"
      ) {
        catalogByTestId.set(
          row.test_id,
          row,
        );
      }
    }

    const testAttempts =
      evaluationRows
        .filter(
          (row) =>
            catalogByTestId.has(
              String(
                row.test_id ??
                "",
              ),
            ),
        )
        .map(
          (row) => {
            const catalog =
              catalogByTestId.get(
                String(
                  row.test_id,
                ),
              );

            return adaptTmuaTestEvaluation({
              user_id:
                String(
                  row.user_id,
                ),

              test_id:
                String(
                  row.test_id,
                ),

              attempt_id:
                String(
                  row.attempt_id,
                ),

              attempt_number:
                row.attempt_number,

              evaluated_at:
                String(
                  row.evaluated_at,
                ),

              predictor_eligible:
                Boolean(
                  row.predictor_eligible,
                ),

              topic_breadth:
                String(
                  catalog.topic_breadth,
                ),

              combined_score_eligible:
                Boolean(
                  row.combined_score_eligible,
                ),

              authoritative_tmua_score9:
                row.authoritative_tmua_score9,

              effective_weight:
                row.effective_weight,

              paper_1_raw_score:
                row.paper_1_raw_score,

              paper_1_effective_weight:
                row.paper_1_effective_weight,

              paper_2_raw_score:
                row.paper_2_raw_score,

              paper_2_effective_weight:
                row.paper_2_effective_weight,
            });
          },
        );

    const questionByQid =
      new Map<
        string,
        any
      >();

    const activeTopicSet =
      new Set<string>();

    for (
      const row of
      questionRows
    ) {
      const qid =
        String(
          row.qid ??
          "",
        ).trim();

      if (!qid) {
        continue;
      }

      questionByQid.set(
        qid,
        row,
      );

      const topic =
        String(
          row.topic ??
          "",
        ).trim();

      if (topic) {
        activeTopicSet.add(
          topic,
        );
      }
    }

    const qbEvents =
      qbRows.map(
        (row) => {
          const canonicalQid =
            canonicalQidFromMetadata(
              row.metadata,
            );

          const question =
            canonicalQid
              ? questionByQid.get(
                  canonicalQid,
                )
              : null;

          return adaptTmuaQbEvent({
            user_id:
              String(
                row.user_id,
              ),

            id:
              String(
                row.id,
              ),

            source:
              String(
                row.source,
              ),

            history_quality:
              String(
                row.history_quality,
              ),

            predictor_eligible:
              Boolean(
                row.predictor_eligible,
              ),

            canonical_qid:
              canonicalQid,

            canonical_active:
              Boolean(
                question?.is_active,
              ),

            selected_answer:
              row.selected_answer == null
                ? null
                : String(
                    row.selected_answer,
                  ),

            canonical_answer:
              question?.answer == null
                ? null
                : String(
                    question.answer,
                  ),

            canonical_topic:
              question?.topic == null
                ? null
                : String(
                    question.topic,
                  ),

            attempted_at:
              String(
                row.attempted_at,
              ),
          });
        },
      );

    const conversionProfiles =
      adaptTmuaConversionProfiles(
        conversionRows.map(
          (row) => ({
            profile:
              String(
                row.profile,
              ),

            score_values:
              Array.isArray(
                row.score_values,
              )
                ? row.score_values
                : [],
          }),
        ),
      );

    const activeTopics =
      [
        ...activeTopicSet,
      ].sort(
        (a, b) =>
          a.localeCompare(b),
      );

    const rawPredictorResult =
      calculateTmuaPredictorV1({
        conversionProfiles,
        activeTopics,
        testAttempts,
        qbEvents,
      });

    const result =
      applyTmuaHighScoreEvidenceGate(
        rawPredictorResult,
      );

    const calculatedAt =
      new Date()
        .toISOString();

    const snapshot =
      buildTmuaPredictionSnapshotInsert(
        user.id,
        result,
        calculatedAt,
      );

    const snapshotRow = {
      user_id:
        snapshot.userId,

      model_version:
        snapshot.modelVersion,

      input_hash:
        snapshot.inputHash,

      prediction_status:
        snapshot.predictionStatus,

      predicted_tmua_score9:
        snapshot.predictedTmuaScore9,

      lower_bound:
        snapshot.lowerBound,

      upper_bound:
        snapshot.upperBound,

      confidence:
        snapshot.confidence,

      test_signal_score9:
        snapshot.testSignalScore9,

      test_weight:
        snapshot.testWeight,

      test_evidence_count:
        snapshot.testEvidenceCount,

      independent_test_count:
        snapshot.independentTestCount,

      combined_full_count:
        snapshot.combinedFullCount,

      qb_signal_score9:
        snapshot.qbSignalScore9,

      qb_weight:
        snapshot.qbWeight,

      qb_unique_questions:
        snapshot.qbUniqueQuestions,

      qb_topic_coverage:
        snapshot.qbTopicCoverage,

      conversion_set_hash:
        snapshot.conversionSetHash,

      active_topic_set_hash:
        snapshot.activeTopicSetHash,

      evidence_details:
        snapshot.evidenceDetails,

      calculated_at:
        snapshot.calculatedAt,
    };

    const {
      error:
        snapshotError,
    } =
      await admin
        .from(
          "tmua_prediction_snapshots",
        )
        .insert(
          snapshotRow,
        );

    if (
      snapshotError &&
      snapshotError.code !==
        "23505"
    ) {
      throw new Error(
        `Snapshot insert failed: ${snapshotError.message}`,
      );
    }

    const preparationOverview = {
      preparationRank: await readPreparationRankSnapshot(admin, user.id, "tmua", user.email),
      countdown: preparationCountdown(new Date()),
    };

    return json({
      ok: true,

      predictor: {
        modelVersion:
          result.modelVersion,

        status:
          result.predictionStatus,

        score:
          result.predictedTmuaScore9,

        lowerBound:
          result.lowerBound,

        upperBound:
          result.upperBound,

        confidence:
          result.confidence,

        testEvidenceCount:
          result.testEvidenceCount,

        independentTestCount:
          result.independentTestCount,

        qbUniqueQuestions:
          result.qbUniqueQuestions,

        qbTopicCoverage:
          result.qbTopicCoverage,

        calculatedAt:
          snapshot.calculatedAt,
      },

      preparationRank:
        preparationOverview.preparationRank,

      countdown:
        preparationOverview.countdown,
    });
  }
  catch (error) {
    console.error(
      "TMUA overview failed",
      error,
    );

    return json(
      {
        ok: false,
        error:
          "Unable to calculate TMUA overview",
      },
      500,
    );
  }
}
