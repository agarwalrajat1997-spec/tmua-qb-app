import {
  createHash as createNodeHash,
  randomUUID as randomNodeUuid,
} from "node:crypto";

import {
  TMUA_PREPARATION_RANK_MODEL_VERSION,
  calculatePreparationScore,
  rankPreparationCohort,
} from "@/lib/server/tmua-preparation-rank-v1-engine";

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

// PREPARATION_RANK_V1_RUNTIME_20260810

const PREPARATION_RANK_PRODUCTS = [
  "practice-tests",
  "tmua-question-bank",
  "tmua-classes",
] as const;

const PREPARATION_RANK_PAGE_SIZE =
  1000;

const PREPARATION_RANK_MAX_PAGES =
  100;

const PREPARATION_RANK_WINDOW_MS =
  30 * 24 * 60 * 60 * 1000;

const TMUA_EXAM_DATE =
  "2026-10-12";

const TMUA_EXAM_DATE_LABEL =
  "12 October";

async function preparationFetchRows(
  label: string,
  makeQuery: (
    from: number,
    to: number,
  ) => PromiseLike<any>,
): Promise<any[]> {
  const rows: any[] = [];

  for (
    let page = 0;
    page < PREPARATION_RANK_MAX_PAGES;
    page += 1
  ) {
    const from =
      page *
      PREPARATION_RANK_PAGE_SIZE;

    const to =
      from +
      PREPARATION_RANK_PAGE_SIZE -
      1;

    const response =
      await makeQuery(
        from,
        to,
      );

    if (response?.error) {
      throw new Error(
        `${label}: ${response.error.message ?? "query failed"}`,
      );
    }

    const pageRows =
      Array.isArray(
        response?.data,
      )
        ? response.data
        : [];

    rows.push(
      ...pageRows,
    );

    if (
      pageRows.length <
      PREPARATION_RANK_PAGE_SIZE
    ) {
      return rows;
    }
  }

  throw new Error(
    `${label} pagination exceeded safety limit`,
  );
}

async function preparationFetchAuthUsers(
  admin: any,
): Promise<any[]> {
  const users: any[] = [];

  for (
    let page = 1;
    page <= PREPARATION_RANK_MAX_PAGES;
    page += 1
  ) {
    const response =
      await admin.auth.admin.listUsers({
        page,
        perPage:
          PREPARATION_RANK_PAGE_SIZE,
      });

    if (response?.error) {
      throw new Error(
        `Preparation Rank auth users: ${response.error.message ?? "query failed"}`,
      );
    }

    const pageUsers =
      Array.isArray(
        response?.data?.users,
      )
        ? response.data.users
        : [];

    users.push(
      ...pageUsers,
    );

    if (
      pageUsers.length <
      PREPARATION_RANK_PAGE_SIZE
    ) {
      return users;
    }
  }

  throw new Error(
    "Preparation Rank auth-user pagination exceeded safety limit",
  );
}

function preparationCanonicalQid(
  metadata: any,
): string | null {
  if (
    metadata === null ||
    typeof metadata !== "object" ||
    Array.isArray(metadata)
  ) {
    return null;
  }

  const qid =
    String(
      metadata.canonical_qid ??
      "",
    ).trim();

  return qid || null;
}

function preparationFiniteNumber(
  value: unknown,
  label: string,
): number {
  const result =
    Number(value);

  if (!Number.isFinite(result)) {
    throw new Error(
      `${label} must be finite`,
    );
  }

  return result;
}

function preparationInteger(
  value: unknown,
  label: string,
): number {
  const result =
    preparationFiniteNumber(
      value,
      label,
    );

  if (
    !Number.isInteger(result) ||
    result < 0
  ) {
    throw new Error(
      `${label} must be a non-negative integer`,
    );
  }

  return result;
}

function preparationWithinWindow(
  value: unknown,
  windowStartMs: number,
  asOfMs: number,
): boolean {
  if (value == null) {
    return false;
  }

  const time =
    Date.parse(
      String(value),
    );

  return (
    Number.isFinite(time) &&
    time > windowStartMs &&
    time <= asOfMs
  );
}

function preparationAddSetValue(
  map: Map<string, Set<string>>,
  userId: string,
  value: string,
): void {
  let values =
    map.get(userId);

  if (!values) {
    values =
      new Set<string>();

    map.set(
      userId,
      values,
    );
  }

  values.add(value);
}

function preparationPushRow(
  map: Map<string, any[]>,
  userId: string,
  row: any,
): void {
  const rows =
    map.get(userId);

  if (rows) {
    rows.push(row);
    return;
  }

  map.set(
    userId,
    [row],
  );
}

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
    Date.UTC(
      2026,
      9,
      12,
    );

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

function preparationInputHash(
  value: unknown,
): string {
  return createNodeHash(
    "sha256",
  )
    .update(
      JSON.stringify(value),
      "utf8",
    )
    .digest("hex");
}

async function calculateAndPersistPreparationRankV1(
  input: {
    admin: any;

    currentUserId:
      string;

    currentPredictorResult:
      any;

    currentPredictorSnapshot:
      any;
  },
) {
  const {
    admin,
    currentUserId,
    currentPredictorResult,
    currentPredictorSnapshot,
  } = input;

  const asOf =
    new Date();

  const asOfMs =
    asOf.getTime();

  const asOfIso =
    asOf.toISOString();

  const windowStart =
    new Date(
      asOfMs -
      PREPARATION_RANK_WINDOW_MS,
    );

  const windowStartMs =
    windowStart.getTime();

  const windowStartIso =
    windowStart.toISOString();

  const [
    accessRows,
    catalogRows,
    conversionRows,
    evaluationRows,
    questionRows,
    qbRows,
    recentAttemptRows,
    exclusionRows,
    authUsers,
  ] =
    await Promise.all([
      preparationFetchRows(
        "Preparation Rank entitlements",
        (from, to) =>
          admin
            .from(
              "student_access",
            )
            .select(
              "email,product,approved,expires_at",
            )
            .in(
              "product",
              [
                ...PREPARATION_RANK_PRODUCTS,
              ],
            )
            .eq(
              "approved",
              true,
            )
            .range(
              from,
              to,
            ),
      ),

      preparationFetchRows(
        "Preparation Rank test catalogue",
        (from, to) =>
          admin
            .from(
              "tmua_test_catalog",
            )
            .select(
              "test_id,topic_breadth,predictor_enabled,leaderboard_enabled",
            )
            .range(
              from,
              to,
            ),
      ),

      preparationFetchRows(
        "Preparation Rank conversion profiles",
        (from, to) =>
          admin
            .from(
              "tmua_score_conversion_profiles",
            )
            .select(
              "profile,score_values",
            )
            .range(
              from,
              to,
            ),
      ),

      preparationFetchRows(
        "Preparation Rank evaluations",
        (from, to) =>
          admin
            .from(
              "tmua_test_attempt_evaluations",
            )
            .select(
              "user_id,test_id,attempt_id,attempt_number,evaluated_at,predictor_eligible,combined_score_eligible,authoritative_tmua_score9,effective_weight,paper_1_raw_score,paper_1_effective_weight,paper_2_raw_score,paper_2_effective_weight",
            )
            .range(
              from,
              to,
            ),
      ),

      preparationFetchRows(
        "Preparation Rank canonical questions",
        (from, to) =>
          admin
            .from(
              "tmua_qb_questions",
            )
            .select(
              "qid,answer,topic,is_active",
            )
            .eq(
              "is_active",
              true,
            )
            .range(
              from,
              to,
            ),
      ),

      preparationFetchRows(
        "Preparation Rank QB events",
        (from, to) =>
          admin
            .from(
              "tmua_qb_attempt_events",
            )
            .select(
              "user_id,id,product,source,history_quality,predictor_eligible,metadata,selected_answer,attempted_at",
            )
            .eq(
              "product",
              "tmua-question-bank",
            )
            .eq(
              "source",
              "qb-progress-trigger-v2",
            )
            .range(
              from,
              to,
            ),
      ),

      preparationFetchRows(
        "Preparation Rank recent test activity",
        (from, to) =>
          admin
            .from(
              "practice_test_attempts",
            )
            .select(
              "user_id,test_id,submitted_at",
            )
            .gt(
              "submitted_at",
              windowStartIso,
            )
            .lte(
              "submitted_at",
              asOfIso,
            )
            .range(
              from,
              to,
            ),
      ),

      preparationFetchRows(
        "Preparation Rank exclusions",
        (from, to) =>
          admin
            .from(
              "tmua_preparation_rank_exclusions",
            )
            .select(
              "user_id,decision,created_at,id",
            )
            .order(
              "created_at",
              {
                ascending:
                  false,
              },
            )
            .order(
              "id",
              {
                ascending:
                  false,
              },
            )
            .range(
              from,
              to,
            ),
      ),

      preparationFetchAuthUsers(
        admin,
      ),
    ]);

  const entitledEmails =
    new Set<string>();

  for (
    const row of
    accessRows
  ) {
    if (
      row.approved !== true
    ) {
      continue;
    }

    if (
      !PREPARATION_RANK_PRODUCTS.includes(
        String(
          row.product,
        ) as
          typeof PREPARATION_RANK_PRODUCTS[number],
      )
    ) {
      continue;
    }

    if (
      row.expires_at != null
    ) {
      const expires =
        Date.parse(
          String(
            row.expires_at,
          ),
        );

      if (
        !Number.isFinite(expires) ||
        expires <= asOfMs
      ) {
        continue;
      }
    }

    const email =
      String(
        row.email ??
        "",
      )
        .trim()
        .toLowerCase();

    if (email) {
      entitledEmails.add(
        email,
      );
    }
  }

  const entitledUsers =
    authUsers
      .filter(
        (authUser) => {
          const email =
            String(
              authUser.email ??
              "",
            )
              .trim()
              .toLowerCase();

          return (
            email.length > 0 &&
            entitledEmails.has(
              email,
            )
          );
        },
      )
      .sort(
        (a, b) =>
          String(a.id)
            .localeCompare(
              String(b.id),
            ),
      );

  const entitledUserIds =
    new Set(
      entitledUsers.map(
        (authUser) =>
          String(
            authUser.id,
          ),
      ),
    );

  const latestExclusion =
    new Map<
      string,
      string
    >();

  for (
    const row of
    exclusionRows
  ) {
    const userId =
      String(
        row.user_id ??
        "",
      );

    if (
      !userId ||
      latestExclusion.has(
        userId,
      )
    ) {
      continue;
    }

    latestExclusion.set(
      userId,
      String(
        row.decision,
      ),
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
    const testId =
      String(
        row.test_id ??
        "",
      ).trim();

    if (testId) {
      catalogByTestId.set(
        testId,
        row,
      );
    }
  }

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

  const activeTopics =
    [
      ...activeTopicSet,
    ].sort(
      (a, b) =>
        a.localeCompare(b),
    );

  const rankConversionProfiles =
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

  if (
    rankConversionProfiles.length !==
    12
  ) {
    throw new Error(
      `Preparation Rank expected 12 conversion profiles, found ${rankConversionProfiles.length}`,
    );
  }

  if (
    activeTopics.length === 0
  ) {
    throw new Error(
      "Preparation Rank active canonical topic set is empty",
    );
  }

  const recentTestFamilies =
    new Map<
      string,
      Set<string>
    >();

  for (
    const row of
    recentAttemptRows
  ) {
    const userId =
      String(
        row.user_id ??
        "",
      );

    const testId =
      String(
        row.test_id ??
        "",
      );

    if (
      !entitledUserIds.has(
        userId,
      )
    ) {
      continue;
    }

    const catalogue =
      catalogByTestId.get(
        testId,
      );

    if (
      catalogue?.leaderboard_enabled !==
      true
    ) {
      continue;
    }

    if (
      !preparationWithinWindow(
        row.submitted_at,
        windowStartMs,
        asOfMs,
      )
    ) {
      continue;
    }

    preparationAddSetValue(
      recentTestFamilies,
      userId,
      testId,
    );
  }

  const recentQbInteractions =
    new Map<
      string,
      Set<string>
    >();

  const qbRowsByUser =
    new Map<
      string,
      any[]
    >();

  for (
    const row of
    qbRows
  ) {
    const userId =
      String(
        row.user_id ??
        "",
      );

    if (
      !entitledUserIds.has(
        userId,
      )
    ) {
      continue;
    }

    preparationPushRow(
      qbRowsByUser,
      userId,
      row,
    );

    const canonicalQid =
      preparationCanonicalQid(
        row.metadata,
      );

    if (
      !canonicalQid ||
      !questionByQid.has(
        canonicalQid,
      )
    ) {
      continue;
    }

    if (
      !preparationWithinWindow(
        row.attempted_at,
        windowStartMs,
        asOfMs,
      )
    ) {
      continue;
    }

    preparationAddSetValue(
      recentQbInteractions,
      userId,
      canonicalQid,
    );
  }

  const evaluationRowsByUser =
    new Map<
      string,
      any[]
    >();

  for (
    const row of
    evaluationRows
  ) {
    const userId =
      String(
        row.user_id ??
        "",
      );

    if (
      !entitledUserIds.has(
        userId,
      )
    ) {
      continue;
    }

    preparationPushRow(
      evaluationRowsByUser,
      userId,
      row,
    );
  }

  let excludedUserCount =
    0;

  const records: any[] =
    [];

  for (
    const authUser of
    entitledUsers
  ) {
    const userId =
      String(
        authUser.id,
      );

    const excluded =
      latestExclusion.get(
        userId,
      ) ===
      "exclude";

    if (excluded) {
      excludedUserCount +=
        1;

      continue;
    }

    const loginActive =
      preparationWithinWindow(
        authUser.last_sign_in_at,
        windowStartMs,
        asOfMs,
      );

    const recentTests =
      recentTestFamilies.get(
        userId,
      ) ??
      new Set<string>();

    const recentQb =
      recentQbInteractions.get(
        userId,
      ) ??
      new Set<string>();

    const testActive =
      recentTests.size >
      0;

    const qbActive =
      recentQb.size >
      0;

    const active =
      loginActive ||
      testActive ||
      qbActive;

    const testAttempts =
      (
        evaluationRowsByUser.get(
          userId,
        ) ??
        []
      )
        .filter(
          (row) => {
            const catalogue =
              catalogByTestId.get(
                String(
                  row.test_id ??
                  "",
                ),
              );

            return (
              catalogue?.predictor_enabled ===
              true
            );
          },
        )
        .map(
          (row) => {
            const testId =
              String(
                row.test_id,
              );

            const catalogue =
              catalogByTestId.get(
                testId,
              );

            return adaptTmuaTestEvaluation({
              user_id:
                userId,

              test_id:
                testId,

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
                  catalogue.topic_breadth,
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

    const predictorQbEvents =
      (
        qbRowsByUser.get(
          userId,
        ) ??
        []
      )
        .filter(
          (row) =>
            String(
              row.history_quality ??
              "",
            ) ===
            "observed",
        )
        .map(
          (row) => {
            const canonicalQid =
              preparationCanonicalQid(
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
                userId,

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
                row.selected_answer ==
                null
                  ? null
                  : String(
                      row.selected_answer,
                    ),

              canonical_answer:
                question?.answer ==
                null
                  ? null
                  : String(
                      question.answer,
                    ),

              canonical_topic:
                question?.topic ==
                null
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

    const predictor =
      calculateTmuaPredictorV1({
        conversionProfiles:
          rankConversionProfiles,

        activeTopics,

        testAttempts,

        qbEvents:
          predictorQbEvents,
      });

    const predictorSnapshot =
      buildTmuaPredictionSnapshotInsert(
        userId,
        predictor,
        asOfIso,
      );

    if (
      userId ===
      currentUserId
    ) {
      if (
        predictorSnapshot.inputHash !==
        currentPredictorSnapshot.inputHash
      ) {
        throw new Error(
          "Preparation Rank current-user Predictor input does not match overview Predictor input",
        );
      }

      if (
        predictor.predictedTmuaScore9 !==
        currentPredictorResult.predictedTmuaScore9
      ) {
        throw new Error(
          "Preparation Rank current-user Predictor score does not match overview Predictor score",
        );
      }
    }

    const details: any =
      predictorSnapshot.evidenceDetails ??
      {};

    const familyRows =
      Array.isArray(
        details.test_families,
      )
        ? details.test_families
        : [];

    const testFamilySignals =
      familyRows.map(
        (
          family: any,
          index: number,
        ) => ({
          score9:
            preparationFiniteNumber(
              family.signal,
              `test family ${index} signal`,
            ),

          weight:
            preparationFiniteNumber(
              family.weight,
              `test family ${index} weight`,
            ),
        }),
      );

    if (
      testFamilySignals.length !==
      predictor.independentTestCount
    ) {
      throw new Error(
        "Preparation Rank Predictor family-count provenance mismatch",
      );
    }

    const broadFamilyCount =
      preparationInteger(
        details
          .broad_test_family_count ??
          0,
        "broad_test_family_count",
      );

    const firstExposureCount =
      preparationInteger(
        details
          .eligible_first_exposure_count ??
          0,
        "eligible_first_exposure_count",
      );

    if (
      firstExposureCount !==
      predictor.qbUniqueQuestions
    ) {
      throw new Error(
        "Preparation Rank Predictor QB provenance mismatch",
      );
    }

    const recoveryValue =
      details
        .qb_recovery_fraction ==
      null
        ? null
        : preparationFiniteNumber(
            details
              .qb_recovery_fraction,
            "qb_recovery_fraction",
          );

    const hasGenuineTestEvidence =
      predictor.independentTestCount >
      0;

    const hasGenuineQbEvidence =
      firstExposureCount >
      0;

    const preparation =
      calculatePreparationScore({
        predictedTmuaScore9:
          predictor.predictedTmuaScore9,

        broadOrFullIndependentTestFamilies:
          broadFamilyCount,

        predictorTestWeight:
          predictor.testWeight,

        trustedUniqueFirstExposures:
          firstExposureCount,

        trustedCanonicalTopicCoverage:
          predictor.qbTopicCoverage,

        distinctCanonicalQbInteractions30d:
          recentQb.size,

        independentRecognisedTestFamilies30d:
          recentTests.size,

        testFamilySignals,

        hasGenuineTestEvidence,

        hasGenuineQbEvidence,

        recovery:
          recoveryValue,
      });

    records.push({
      userId,

      active,

      loginActive,

      testActive,

      qbActive,

      recentQbCount:
        recentQb.size,

      recentTestCount:
        recentTests.size,

      predictor,

      predictorSnapshot,

      broadFamilyCount,

      firstExposureCount,

      recoveryValue,

      preparation,
    });
  }

  const ranking =
    rankPreparationCohort(
      records.map(
        (record) => ({
          userId:
            record.userId,

          active:
            record.active,

          score:
            record.preparation,
        }),
      ),
    );

  const rankingByUser =
    new Map(
      ranking.map(
        (row) => [
          String(
            row.userId,
          ),
          row,
        ],
      ),
    );

  const activeRecords =
    records
      .filter(
        (record) =>
          record.active,
      )
      .sort(
        (a, b) =>
          a.userId.localeCompare(
            b.userId,
          ),
      );

  const activeCohortSize =
    activeRecords.length;

  const rankableCount =
    activeRecords.filter(
      (record) => {
        const ranked =
          rankingByUser.get(
            record.userId,
          );

        return (
          ranked?.actualPreparationRank !=
          null
        );
      },
    ).length;

  for (
    const record of
    activeRecords
  ) {
    const ranked =
      rankingByUser.get(
        record.userId,
      );

    if (!ranked) {
      throw new Error(
        "Preparation Rank output missing active user",
      );
    }

    if (
      record.preparation
        .hasGenuinePreparationEvidence &&
      ranked.actualPreparationRank ==
        null
    ) {
      throw new Error(
        "Genuine active Preparation Rank evidence received no rank",
      );
    }

    if (
      !record.preparation
        .hasGenuinePreparationEvidence &&
      (
        ranked.actualPreparationRank !=
          null ||
        ranked.actualPreparationScore !=
          null
      )
    ) {
      throw new Error(
        "No-evidence active user received synthetic Preparation Rank data",
      );
    }
  }

  const inputHash =
    preparationInputHash({
      modelVersion:
        TMUA_PREPARATION_RANK_MODEL_VERSION,

      entitledAuthUserCount:
        entitledUsers.length,

      excludedUserCount,

      activeCohortSize,

      activeUsers:
        activeRecords.map(
          (record) => ({
            userId:
              record.userId,

            predictorInputHash:
              record
                .predictorSnapshot
                .inputHash,

            recentQbCount:
              record.recentQbCount,

            recentTestCount:
              record.recentTestCount,

            loginActive:
              record.loginActive,

            testActive:
              record.testActive,

            qbActive:
              record.qbActive,

            genuinePreparationEvidence:
              record.preparation
                .hasGenuinePreparationEvidence,

            actualPreparationScore:
              record.preparation
                .actualPreparationScore,

            components:
              record.preparation
                .components,
          }),
        ),
    });

  const loginOnlyActive =
    activeRecords.filter(
      (record) =>
        record.loginActive &&
        !record.testActive &&
        !record.qbActive,
    ).length;

  const prepActiveWithoutRecentLogin =
    activeRecords.filter(
      (record) =>
        !record.loginActive &&
        (
          record.testActive ||
          record.qbActive
        ),
    ).length;

  const proposedRunId =
    randomNodeUuid();

  const runInsert =
    await admin
      .from(
        "tmua_preparation_rank_runs",
      )
      .insert({
        id:
          proposedRunId,

        model_version:
          TMUA_PREPARATION_RANK_MODEL_VERSION,

        input_hash:
          inputHash,

        cohort_as_of:
          asOfIso,

        window_start:
          windowStartIso,

        entitled_auth_user_count:
          entitledUsers.length,

        excluded_user_count:
          excludedUserCount,

        active_cohort_size:
          activeCohortSize,

        rankable_count:
          rankableCount,

        cohort_details: {
          rolling_window_days:
            30,

          login_only_active:
            loginOnlyActive,

          prep_active_without_recent_login:
            prepActiveWithoutRecentLogin,

          exam_date:
            TMUA_EXAM_DATE,
        },
      })
      .select(
        "id",
      )
      .maybeSingle();

  let runId:
    string;

  if (
    runInsert.error &&
    runInsert.error.code !==
      "23505"
  ) {
    throw new Error(
      `Preparation Rank run insert failed: ${runInsert.error.message}`,
    );
  }

  if (
    !runInsert.error &&
    runInsert.data?.id
  ) {
    runId =
      String(
        runInsert.data.id,
      );
  }
  else {
    const existingRun =
      await admin
        .from(
          "tmua_preparation_rank_runs",
        )
        .select(
          "id",
        )
        .eq(
          "model_version",
          TMUA_PREPARATION_RANK_MODEL_VERSION,
        )
        .eq(
          "input_hash",
          inputHash,
        )
        .single();

    if (
      existingRun.error ||
      !existingRun.data?.id
    ) {
      throw new Error(
        `Preparation Rank deduplicated run lookup failed: ${existingRun.error?.message ?? "missing run"}`,
      );
    }

    runId =
      String(
        existingRun.data.id,
      );
  }

  if (
    activeCohortSize >
    0
  ) {
    const existingSnapshotRows =
      await preparationFetchRows(
        "Preparation Rank existing snapshots",
        (from, to) =>
          admin
            .from(
              "tmua_preparation_rank_snapshots",
            )
            .select(
              "user_id",
            )
            .eq(
              "run_id",
              runId,
            )
            .range(
              from,
              to,
            ),
      );

    const existingUsers =
      new Set(
        existingSnapshotRows.map(
          (row) =>
            String(
              row.user_id,
            ),
        ),
      );

    const missingRows =
      activeRecords
        .filter(
          (record) =>
            !existingUsers.has(
              record.userId,
            ),
        )
        .map(
          (record) => {
            const ranked =
              rankingByUser.get(
                record.userId,
              );

            if (!ranked) {
              throw new Error(
                "Preparation Rank persistence is missing ranking output",
              );
            }

            const components =
              record.preparation
                .components;

            return {
              run_id:
                runId,

              user_id:
                record.userId,

              model_version:
                TMUA_PREPARATION_RANK_MODEL_VERSION,

              genuine_preparation_evidence:
                record.preparation
                  .hasGenuinePreparationEvidence,

              actual_preparation_score:
                ranked
                  .actualPreparationScore,

              actual_preparation_rank:
                ranked
                  .actualPreparationRank,

              actual_active_cohort_size:
                activeCohortSize,

              performance_component:
                components.performance,

              breadth_component:
                components.breadth,

              evidence_depth_component:
                components.evidenceDepth,

              recent_activity_component:
                components.recentActivity,

              consistency_component:
                components.consistency,

              recovery_component:
                components.recovery,

              predicted_tmua_score9:
                record.predictor
                  .predictedTmuaScore9,

              predictor_input_hash:
                record
                  .predictorSnapshot
                  .inputHash,

              independent_test_count:
                record.predictor
                  .independentTestCount,

              predictor_test_family_weight:
                record.predictor
                  .testWeight,

              trusted_unique_first_exposures:
                record.firstExposureCount,

              trusted_canonical_topic_coverage:
                record.predictor
                  .qbTopicCoverage,

              distinct_canonical_qb_interactions_30d:
                record.recentQbCount,

              independent_recognised_test_families_30d:
                record.recentTestCount,

              recovery_value:
                record.recoveryValue,

              evidence_details: {
                broad_or_full_independent_test_families:
                  record.broadFamilyCount,

                login_active:
                  record.loginActive,

                test_active:
                  record.testActive,

                qb_active:
                  record.qbActive,
              },

              created_at:
                asOfIso,
            };
          },
        );

    if (
      missingRows.length >
      0
    ) {
      const snapshotInsert =
        await admin
          .from(
            "tmua_preparation_rank_snapshots",
          )
          .insert(
            missingRows,
          );

      if (
        snapshotInsert.error &&
        snapshotInsert.error.code !==
          "23505"
      ) {
        throw new Error(
          `Preparation Rank snapshot insert failed: ${snapshotInsert.error.message}`,
        );
      }
    }

    const finalSnapshotRows =
      await preparationFetchRows(
        "Preparation Rank persisted snapshots",
        (from, to) =>
          admin
            .from(
              "tmua_preparation_rank_snapshots",
            )
            .select(
              "user_id",
            )
            .eq(
              "run_id",
              runId,
            )
            .range(
              from,
              to,
            ),
      );

    const finalUsers =
      new Set(
        finalSnapshotRows.map(
          (row) =>
            String(
              row.user_id,
            ),
        ),
      );

    for (
      const record of
      activeRecords
    ) {
      if (
        !finalUsers.has(
          record.userId,
        )
      ) {
        throw new Error(
          "Preparation Rank run is missing an active-user snapshot",
        );
      }
    }
  }

  const currentRecord =
    records.find(
      (record) =>
        record.userId ===
        currentUserId,
    );

  const currentRanking =
    currentRecord
      ? rankingByUser.get(
          currentUserId,
        )
      : null;

  const currentIsActive =
    Boolean(
      currentRecord?.active,
    );

  const currentHasEvidence =
    Boolean(
      currentIsActive &&
      currentRecord
        ?.preparation
        ?.hasGenuinePreparationEvidence,
    );

  return {
    preparationRank: {
      modelVersion:
        TMUA_PREPARATION_RANK_MODEL_VERSION,

      hasGenuinePreparationEvidence:
        currentHasEvidence,

      score:
        currentHasEvidence
          ? (
              currentRanking
                ?.actualPreparationScore ??
              null
            )
          : null,

      rank:
        currentHasEvidence
          ? (
              currentRanking
                ?.actualPreparationRank ??
              null
            )
          : null,

      cohortSize:
        activeCohortSize,

      components:
        currentHasEvidence
          ? currentRecord
              .preparation
              .components
          : null,

      calculatedAt:
        asOfIso,
    },

    countdown:
      preparationCountdown(
        asOf,
      ),
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

    const preparationOverview =
      await calculateAndPersistPreparationRankV1({
        admin,

        currentUserId:
          user.id,

        currentPredictorResult:
          result,

        currentPredictorSnapshot:
          snapshot,
      });

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