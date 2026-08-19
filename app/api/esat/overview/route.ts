/* eslint-disable @typescript-eslint/no-explicit-any */

import {
  ESAT_TABLE_CANDIDATES,
  adminClient,
  json,
} from "@/app/api/esat/qb/_server";
import {
  ESAT_CANONICAL_TESTS,
  getCanonicalEsatTest,
} from "@/lib/server/esat-canonical-tests";
import {
  calculateEsatPredictorV1,
  type EsatPredictorQbEvent,
  type EsatPredictorTestAttempt,
} from "@/lib/server/esat-predictor-v1-engine";
import { estimateEsatTestScores } from "@/lib/server/esat-score-estimates";
import {
  calculatePreparationScore,
  rankPreparationCohort,
} from "@/lib/server/tmua-preparation-rank-v1-engine";
import { createSupabaseServerClient } from "@/lib/supabase/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const PAGE_SIZE = 1000;
const MAX_ROWS = 10000;
const ESAT_ACTIVE_WINDOW_MS = 30 * 24 * 60 * 60 * 1000;
const ESAT_EXAM_DATE = "2026-10-12";
const ESAT_EXAM_DATE_LABEL = "12 October";
const ESAT_PREPARATION_RANK_MODEL_VERSION =
  "esat-preparation-rank-v1-20260819";
const ESAT_ACCESS_PRODUCTS = [
  "esat-practice-tests",
  "esat-question-bank",
  "esat-classes",
] as const;

async function readAll(
  queryPage: (from: number, to: number) => PromiseLike<{
    data: any[] | null;
    error: any;
  }>,
): Promise<any[]> {
  const rows: any[] = [];

  for (let from = 0; from < MAX_ROWS; from += PAGE_SIZE) {
    const { data, error } = await queryPage(
      from,
      from + PAGE_SIZE - 1,
    );

    if (error) {
      throw new Error(error.message ?? String(error));
    }

    const page = data ?? [];
    rows.push(...page);

    if (page.length < PAGE_SIZE) {
      break;
    }
  }

  return rows;
}

async function readAuthUsers(
  admin: ReturnType<typeof adminClient>,
): Promise<any[]> {
  const users: any[] = [];
  const maxPages = Math.ceil(MAX_ROWS / PAGE_SIZE);

  for (let page = 1; page <= maxPages; page += 1) {
    const response = await admin.auth.admin.listUsers({
      page,
      perPage: PAGE_SIZE,
    });

    if (response.error) {
      throw new Error(
        `ESAT active cohort auth users: ${response.error.message ?? "query failed"}`,
      );
    }

    const pageUsers = Array.isArray(response.data?.users)
      ? response.data.users
      : [];

    users.push(...pageUsers);

    if (pageUsers.length < PAGE_SIZE) {
      return users;
    }
  }

  throw new Error("ESAT active cohort auth-user pagination exceeded safety limit");
}

function normaliseAnswer(value: unknown): string | null {
  const answer = String(value ?? "").trim().toUpperCase();
  return answer || null;
}

function canonicalQid(metadata: unknown, fallback: unknown): string | null {
  if (metadata && typeof metadata === "object" && !Array.isArray(metadata)) {
    const value = (metadata as Record<string, unknown>).canonical_qid;
    const qid = String(value ?? "").trim();

    if (qid) {
      return qid;
    }
  }

  const qid = String(fallback ?? "").trim();
  return qid || null;
}

function withinWindow(
  value: unknown,
  windowStartMs: number,
  asOfMs: number,
): boolean {
  if (value == null) {
    return false;
  }

  const time = Date.parse(String(value));
  return Number.isFinite(time) && time > windowStartMs && time <= asOfMs;
}

function londonDayUtc(date: Date): number {
  const parts = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Europe/London",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(date);

  const values = new Map(parts.map((part) => [part.type, part.value]));
  const year = Number(values.get("year"));
  const month = Number(values.get("month"));
  const day = Number(values.get("day"));

  if (
    !Number.isInteger(year) ||
    !Number.isInteger(month) ||
    !Number.isInteger(day)
  ) {
    throw new Error("Unable to resolve London calendar date");
  }

  return Date.UTC(year, month - 1, day);
}

function esatCountdown(asOf: Date) {
  const today = londonDayUtc(asOf);
  const exam = Date.UTC(2026, 9, 12);
  const daysToEsat = Math.max(
    0,
    Math.round((exam - today) / (24 * 60 * 60 * 1000)),
  );

  return {
    daysToEsat,
    examDate: ESAT_EXAM_DATE,
    examDateLabel: ESAT_EXAM_DATE_LABEL,
  };
}

function pushByUser(
  map: Map<string, any[]>,
  userId: string,
  row: any,
): void {
  const rows = map.get(userId);

  if (rows) {
    rows.push(row);
  }
  else {
    map.set(userId, [row]);
  }
}

function buildTestEvidence(rows: any[]): EsatPredictorTestAttempt[] {
  return rows.flatMap((row) => {
    const testId = String(row.test_id ?? "").trim();
    const canonical = getCanonicalEsatTest(testId);
    const submitted = Array.isArray(row.answers) ? row.answers : [];

    if (!canonical || submitted.length !== canonical.expectedQuestions) {
      return [];
    }

    const answers = submitted.map(normaliseAnswer);
    const sectionScores = canonical.sectionRanges.map(([start, end]) => {
      let correct = 0;

      for (let index = start; index < end; index += 1) {
        if (
          answers[index] !== null &&
          answers[index] === canonical.answers[index]
        ) {
          correct += 1;
        }
      }

      return correct;
    });

    const estimate = estimateEsatTestScores(testId, sectionScores);
    const evaluatedAt = new Date(String(row.submitted_at ?? ""));

    if (!Number.isFinite(evaluatedAt.valueOf())) {
      return [];
    }

    return [{
      testId,
      attemptId: String(row.id),
      attemptNumber:
        Number.isInteger(Number(row.attempt_number)) &&
        Number(row.attempt_number) > 0
          ? Number(row.attempt_number)
          : null,
      evaluatedAt: evaluatedAt.toISOString(),
      predictorEligible: true,
      predictedCombinedPracticeScore:
        estimate.predictedCombinedPracticeScore,
      effectiveWeight: 1.5,
    }];
  });
}

function buildQbEvents(
  rows: any[],
  questionByQid: Map<string, any>,
): EsatPredictorQbEvent[] {
  return rows.map((row) => {
    const qid = canonicalQid(row.metadata, row.question_id);
    const question = qid ? questionByQid.get(qid) : null;

    return {
      id: String(row.id),
      source: String(row.source),
      historyQuality: String(row.history_quality),
      predictorEligible: Boolean(row.predictor_eligible),
      canonicalQid: qid,
      canonicalActive: Boolean(question?.is_active),
      selectedAnswer:
        row.selected_answer == null
          ? null
          : String(row.selected_answer),
      canonicalAnswer:
        question?.answer == null
          ? null
          : String(question.answer),
      canonicalTopic:
        question?.topic == null
          ? null
          : String(question.topic),
      attemptedAt: String(row.attempted_at),
    };
  });
}

function buildTestFamilySignals(
  attempts: EsatPredictorTestAttempt[],
) {
  const byTest = new Map<string, EsatPredictorTestAttempt[]>();

  for (const attempt of attempts) {
    if (
      attempt.predictorEligible !== true ||
      attempt.predictedCombinedPracticeScore == null
    ) {
      continue;
    }

    const existing = byTest.get(attempt.testId);
    if (existing) {
      existing.push(attempt);
    }
    else {
      byTest.set(attempt.testId, [attempt]);
    }
  }

  return [...byTest.values()].flatMap((familyAttempts) => {
    const usable = [...familyAttempts].sort(
      (a, b) => Date.parse(a.evaluatedAt) - Date.parse(b.evaluatedAt),
    );

    if (usable.length === 0) {
      return [];
    }

    const first = usable[0].predictedCombinedPracticeScore as number;
    const latest = usable[usable.length - 1]
      .predictedCombinedPracticeScore as number;
    const score9 = usable.length === 1
      ? first
      : 0.75 * first + 0.25 * latest;

    return [{ score9, weight: 1.5 }];
  });
}

async function readActiveQuestions(admin: ReturnType<typeof adminClient>) {
  let lastError: any = null;

  for (const table of ESAT_TABLE_CANDIDATES) {
    try {
      const rows = await readAll((from, to) =>
        admin
          .from(table)
          .select("qid,topic,answer,is_active")
          .eq("is_active", true)
          .order("qid", { ascending: true })
          .range(from, to),
      );

      return rows;
    }
    catch (error) {
      lastError = error;
    }
  }

  throw lastError ?? new Error("No ESAT question table is available.");
}

export async function GET() {
  try {
    const session = await createSupabaseServerClient();
    const {
      data: { user },
      error: userError,
    } = await session.auth.getUser();

    if (userError || !user) {
      return json({ ok: false, error: "Unauthorized" }, 401);
    }

    const admin = adminClient();
    const recognisedIds = Object.keys(ESAT_CANONICAL_TESTS);
    const asOf = new Date();
    const asOfMs = asOf.getTime();
    const windowStartMs = asOfMs - ESAT_ACTIVE_WINDOW_MS;

    const [attemptRows, questionRows, qbRows, accessRows, authUsers] =
      await Promise.all([
        readAll((from, to) =>
          admin
            .from("practice_test_attempts")
            .select("id,user_id,test_id,answers,attempt_number,submitted_at")
            .in("test_id", recognisedIds)
            .order("submitted_at", { ascending: true })
            .range(from, to),
        ),
        readActiveQuestions(admin),
        readAll((from, to) =>
          admin
            .from("tmua_qb_attempt_events")
            .select(
              "id,user_id,question_id,source,history_quality,predictor_eligible,metadata,selected_answer,attempted_at",
            )
            .eq("product", "esat-question-bank")
            .eq("source", "qb-progress-trigger-v2")
            .eq("history_quality", "observed")
            .order("attempted_at", { ascending: true })
            .range(from, to),
        ),
        readAll((from, to) =>
          admin
            .from("student_access")
            .select("email,product,approved,expires_at")
            .in("product", [...ESAT_ACCESS_PRODUCTS])
            .eq("approved", true)
            .range(from, to),
        ),
        readAuthUsers(admin),
      ]);

    const questionByQid = new Map<string, any>();
    const activeTopicSet = new Set<string>();

    for (const row of questionRows) {
      const qid = String(row.qid ?? "").trim();
      const topic = String(row.topic ?? "").trim();

      if (qid) {
        questionByQid.set(qid, row);
      }

      if (topic) {
        activeTopicSet.add(topic);
      }
    }

    const activeTopics = [...activeTopicSet].sort((a, b) => a.localeCompare(b));
    const attemptsByUser = new Map<string, any[]>();
    const qbRowsByUser = new Map<string, any[]>();

    for (const row of attemptRows) {
      const userId = String(row.user_id ?? "").trim();
      if (userId) {
        pushByUser(attemptsByUser, userId, row);
      }
    }

    for (const row of qbRows) {
      const userId = String(row.user_id ?? "").trim();
      if (userId) {
        pushByUser(qbRowsByUser, userId, row);
      }
    }

    const entitledEmails = new Set<string>();

    for (const row of accessRows) {
      if (row.approved !== true) {
        continue;
      }

      if (row.expires_at != null) {
        const expires = Date.parse(String(row.expires_at));
        if (!Number.isFinite(expires) || expires <= asOfMs) {
          continue;
        }
      }

      const email = String(row.email ?? "").trim().toLowerCase();
      if (email) {
        entitledEmails.add(email);
      }
    }

    const entitledUsers = authUsers.filter((authUser) => {
      const email = String(authUser.email ?? "").trim().toLowerCase();
      return email.length > 0 && entitledEmails.has(email);
    });

    const preparationRecords: Array<{
      userId: string;
      active: boolean;
      preparation: ReturnType<typeof calculatePreparationScore>;
    }> = [];

    let currentPredictorResult: ReturnType<typeof calculateEsatPredictorV1> | null = null;

    for (const authUser of entitledUsers) {
      const userId = String(authUser.id);
      const userAttemptRows = attemptsByUser.get(userId) ?? [];
      const userQbRows = qbRowsByUser.get(userId) ?? [];
      const testEvidence = buildTestEvidence(userAttemptRows);
      const userQbEvents = buildQbEvents(userQbRows, questionByQid);
      const predictor = calculateEsatPredictorV1({
        testAttempts: testEvidence,
        qbEvents: userQbEvents,
        activeTopics,
      });

      if (userId === user.id) {
        currentPredictorResult = predictor;
      }

      const recentTests = new Set<string>();
      for (const row of userAttemptRows) {
        if (withinWindow(row.submitted_at, windowStartMs, asOfMs)) {
          const testId = String(row.test_id ?? "").trim();
          if (recognisedIds.includes(testId)) {
            recentTests.add(testId);
          }
        }
      }

      const recentQb = new Set<string>();
      for (const row of userQbRows) {
        if (!withinWindow(row.attempted_at, windowStartMs, asOfMs)) {
          continue;
        }

        const qid = canonicalQid(row.metadata, row.question_id);
        if (qid && questionByQid.has(qid)) {
          recentQb.add(qid);
        }
      }

      const loginActive = withinWindow(
        authUser.last_sign_in_at,
        windowStartMs,
        asOfMs,
      );
      const testActive = recentTests.size > 0;
      const qbActive = recentQb.size > 0;
      const active = loginActive || testActive || qbActive;

      const preparation = calculatePreparationScore({
        predictedTmuaScore9: predictor.predictedEsatPracticeScore,
        broadOrFullIndependentTestFamilies: predictor.independentTestCount,
        predictorTestWeight: predictor.testWeight,
        trustedUniqueFirstExposures: predictor.qbUniqueQuestions,
        trustedCanonicalTopicCoverage: predictor.qbTopicCoverage,
        distinctCanonicalQbInteractions30d: recentQb.size,
        independentRecognisedTestFamilies30d: recentTests.size,
        testFamilySignals: buildTestFamilySignals(testEvidence),
        hasGenuineTestEvidence: testEvidence.length > 0,
        hasGenuineQbEvidence: predictor.qbUniqueQuestions > 0,
        recovery: null,
      });

      preparationRecords.push({
        userId,
        active,
        preparation,
      });
    }

    if (!currentPredictorResult) {
      const currentAttemptRows = attemptsByUser.get(user.id) ?? [];
      const currentQbRows = qbRowsByUser.get(user.id) ?? [];
      currentPredictorResult = calculateEsatPredictorV1({
        testAttempts: buildTestEvidence(currentAttemptRows),
        qbEvents: buildQbEvents(currentQbRows, questionByQid),
        activeTopics,
      });
    }

    const ranked = rankPreparationCohort(
      preparationRecords.map((record) => ({
        userId: record.userId,
        active: record.active,
        score: record.preparation,
      })),
    );

    const currentRank = ranked.find((row) => row.userId === user.id) ?? null;
    const currentPreparation =
      preparationRecords.find((row) => row.userId === user.id)?.preparation ?? null;
    const activeCohortSize = preparationRecords.filter((row) => row.active).length;
    const result = currentPredictorResult;
    const calculatedAt = asOf.toISOString();

    const snapshotRow = {
      user_id: user.id,
      model_version: result.modelVersion,
      input_hash: result.inputHash,
      prediction_status: result.predictionStatus,
      predicted_tmua_score9: result.predictedEsatPracticeScore,
      lower_bound: result.lowerBound,
      upper_bound: result.upperBound,
      confidence: result.confidence,
      test_signal_score9: result.testSignalPracticeScore,
      test_weight: result.testWeight,
      test_evidence_count: result.testEvidenceCount,
      independent_test_count: result.independentTestCount,
      combined_full_count: result.combinedFullCount,
      qb_signal_score9: result.qbSignalScore9,
      qb_weight: result.qbWeight,
      qb_unique_questions: result.qbUniqueQuestions,
      qb_topic_coverage: result.qbTopicCoverage,
      conversion_set_hash: result.calibrationSetHash,
      active_topic_set_hash: result.activeTopicSetHash,
      evidence_details: {
        product: "esat",
        combined_score_official: false,
        predictor_model_version: result.modelVersion,
        active_cohort_window_days: 30,
      },
      calculated_at: calculatedAt,
    };

    const { error: snapshotError } = await admin
      .from("tmua_prediction_snapshots")
      .insert(snapshotRow);

    if (snapshotError && snapshotError.code !== "23505") {
      throw new Error(`Snapshot insert failed: ${snapshotError.message}`);
    }

    return json({
      ok: true,
      predictor: {
        modelVersion: result.modelVersion,
        status: result.predictionStatus,
        score: result.predictedEsatPracticeScore,
        lowerBound: result.lowerBound,
        upperBound: result.upperBound,
        confidence: result.confidence,
        testEvidenceCount: result.testEvidenceCount,
        independentTestCount: result.independentTestCount,
        qbUniqueQuestions: result.qbUniqueQuestions,
        qbTopicCoverage: result.qbTopicCoverage,
        calculatedAt,
        combinedScoreOfficial: false,
      },
      preparationRank: {
        modelVersion: ESAT_PREPARATION_RANK_MODEL_VERSION,
        hasGenuinePreparationEvidence:
          currentPreparation?.hasGenuinePreparationEvidence ?? false,
        score: currentRank?.actualPreparationScore ?? null,
        rank: currentRank?.actualPreparationRank ?? null,
        cohortSize: activeCohortSize,
        components: currentPreparation?.components ?? null,
        calculatedAt,
      },
      countdown: esatCountdown(asOf),
    });
  }
  catch (error) {
    console.error("ESAT overview failed", error);

    return json(
      { ok: false, error: "Unable to calculate ESAT overview" },
      500,
    );
  }
}
