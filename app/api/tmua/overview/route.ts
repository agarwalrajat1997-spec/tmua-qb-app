import { NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

import { createSupabaseServerClient } from "@/lib/supabase/server";

import {
  adaptTmuaConversionProfiles,
  adaptTmuaQbEvent,
  adaptTmuaTestEvaluation,
} from "@/lib/server/tmua-predictor-v1-evidence-adapter";

import {
  calculateTmuaPredictorV1,
} from "@/lib/server/tmua-predictor-v1-engine";

import {
  buildTmuaPredictionSnapshotInsert,
} from "@/lib/server/tmua-predictor-v1-snapshot";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

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
      headers:
        NO_STORE_HEADERS,
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
    ) => PromiseLike<any>,
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

    const {
      data,
      error,
    } =
      await fetchPage(
        from,
        to,
      );

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
      await supabase.auth.getUser();

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

    const [
      conversionRows,
      catalogRows,
      evaluationRows,
      questionRows,
      qbRows,
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
                "test_id,topic_breadth,predictor_enabled",
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
      ]);

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

    const result =
      calculateTmuaPredictorV1({
        conversionProfiles,
        activeTopics,
        testAttempts,
        qbEvents,
      });

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