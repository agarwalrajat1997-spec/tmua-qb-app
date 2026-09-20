/* eslint-disable @typescript-eslint/no-explicit-any */

import {
  ESAT_TABLE_CANDIDATES,
  adminClient,
  json,
} from "@/app/api/esat/qb/_server";
import {
  ESAT_CANONICAL_TESTS,
} from "@/lib/server/esat-canonical-tests";
import {
  calculateEsatPredictorV1,
  type EsatPredictorQbEvent,
  type EsatPredictorTestAttempt,
} from "@/lib/server/esat-predictor-v1-engine";
import { buildEsatTestEvidence } from "@/lib/server/esat-predictor-evidence";
import { getEsatPredictorFamilyId } from "@/lib/server/esat-october-2026-tests";
import {
  calculatePreparationScore,
} from "@/lib/server/tmua-preparation-rank-v1-engine";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { isMissingSession, withServiceTimeout } from "@/lib/auth/service-recovery";

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
      return rows;
    }
  }

  // Never silently calculate a prediction from truncated historical evidence.
  throw new Error("ESAT evidence exceeded the per-user pagination safety limit");
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

// Canonical metadata contains no student data. Coalesce cold concurrent reads,
// and refresh within one minute so answer/topic corrections reach predictions.
let questionCache: { rows: any[]; expiresAt: number } | null = null;
let questionsInFlight: Promise<any[]> | null = null;

async function readActiveQuestions(admin: ReturnType<typeof adminClient>) {
  if (questionCache && questionCache.expiresAt > Date.now()) return questionCache.rows;
  if (questionsInFlight) return questionsInFlight;

  questionsInFlight = (async () => {
    let lastError: any = null;
    for (const table of ESAT_TABLE_CANDIDATES) {
      try {
        const rows = await readAll(async (from, to) => {
          const response = await admin.from(table)
            .select("qid,topic,answer,is_active")
            .eq("is_active", true)
            .order("qid", { ascending: true }).range(from, to).retry(false);
          // Preserve the error code: a service outage must not trigger a scan
          // of every historical table alias in turn.
          if (response.error) throw response.error;
          return response;
        });
        questionCache = { rows, expiresAt: Date.now() + 60_000 };
        return rows;
      } catch (error) {
        lastError = error;
        const code = (error as { code?: string })?.code;
        if (code !== "42P01" && code !== "PGRST205") throw error;
      }
    }
    throw lastError ?? new Error("No ESAT question table is available.");
  })();
  try {
    return await questionsInFlight;
  } finally {
    questionsInFlight = null;
  }
}

// This is a small process-local optimization, not a cohort cache or an access
// cache. Every request must authenticate and recheck its own entitlement first.
// Concurrent tabs share one calculation; successful results live for 30 seconds.
// A cold server still reads only that student's evidence, never all users.
const overviewCache = new Map<string, { body: any; expiresAt: number }>();
const overviewInFlight = new Map<string, Promise<any>>();
const MAX_CACHED_USERS = 128;

async function currentUserOverview(admin: ReturnType<typeof adminClient>, userId: string) {
  const cached = overviewCache.get(userId);
  if (cached && cached.expiresAt > Date.now()) return cached.body;
  const pending = overviewInFlight.get(userId);
  if (pending) return pending;
  if (overviewInFlight.size >= MAX_CACHED_USERS) {
    throw new Error("ESAT overview temporarily busy");
  }
  const calculation = calculateCurrentUserOverview(admin, userId).then((body) => {
    if (overviewCache.size >= MAX_CACHED_USERS) {
      overviewCache.delete(overviewCache.keys().next().value!);
    }
    overviewCache.set(userId, { body, expiresAt: Date.now() + 30_000 });
    return body;
  });
  overviewInFlight.set(userId, calculation);
  try {
    return await calculation;
  } finally {
    overviewInFlight.delete(userId);
  }
}

async function calculateCurrentUserOverview(admin: ReturnType<typeof adminClient>, userId: string) {
  const recognisedIds = Object.keys(ESAT_CANONICAL_TESTS);
  const asOf = new Date();
  const asOfMs = asOf.getTime();
  const windowStartMs = asOfMs - ESAT_ACTIVE_WINDOW_MS;

  const [attemptRows, questionRows, qbRows] = await Promise.all([
    readAll((from, to) => admin.from("practice_test_attempts")
      .select("id,user_id,test_id,answers,attempt_number,submitted_at")
      .eq("user_id", userId)
      .in("test_id", recognisedIds)
      .order("submitted_at", { ascending: true })
      .order("id", { ascending: true }).range(from, to).retry(false)),
    readActiveQuestions(admin),
    readAll((from, to) => admin.from("tmua_qb_attempt_events")
      .select("id,user_id,question_id,source,history_quality,predictor_eligible,metadata,selected_answer,attempted_at")
      .eq("user_id", userId)
      .eq("product", "esat-question-bank")
      .eq("source", "qb-progress-trigger-v2")
      .eq("history_quality", "observed")
      .order("attempted_at", { ascending: true })
      .order("id", { ascending: true }).range(from, to).retry(false)),
  ]);

  const questionByQid = new Map<string, any>();
  const activeTopicSet = new Set<string>();
  for (const row of questionRows) {
    const qid = String(row.qid ?? "").trim();
    const topic = String(row.topic ?? "").trim();
    if (qid) questionByQid.set(qid, row);
    if (topic) activeTopicSet.add(topic);
  }
  const activeTopics = [...activeTopicSet].sort((a, b) => a.localeCompare(b));
  const testEvidence = buildEsatTestEvidence(attemptRows);
  const result = calculateEsatPredictorV1({
    testAttempts: testEvidence,
    qbEvents: buildQbEvents(qbRows, questionByQid),
    activeTopics,
  });

  const recentTests = new Set<string>();
  for (const row of attemptRows) {
    if (withinWindow(row.submitted_at, windowStartMs, asOfMs)) {
      const testId = String(row.test_id ?? "").trim();
      if (recognisedIds.includes(testId)) recentTests.add(getEsatPredictorFamilyId(testId));
    }
  }
  const recentQb = new Set<string>();
  for (const row of qbRows) {
    if (!withinWindow(row.attempted_at, windowStartMs, asOfMs)) continue;
    const qid = canonicalQid(row.metadata, row.question_id);
    if (qid && questionByQid.has(qid)) recentQb.add(qid);
  }
  const currentPreparation = calculatePreparationScore({
    predictedTmuaScore9: result.predictedEsatPracticeScore,
    broadOrFullIndependentTestFamilies: result.independentTestCount,
    predictorTestWeight: result.testWeight,
    trustedUniqueFirstExposures: result.qbUniqueQuestions,
    trustedCanonicalTopicCoverage: result.qbTopicCoverage,
    distinctCanonicalQbInteractions30d: recentQb.size,
    independentRecognisedTestFamilies30d: recentTests.size,
    testFamilySignals: buildTestFamilySignals(testEvidence),
    hasGenuineTestEvidence: testEvidence.length > 0,
    hasGenuineQbEvidence: result.qbUniqueQuestions > 0,
    recovery: null,
  });
  const calculatedAt = asOf.toISOString();

  const snapshotRow = {
    user_id: userId,
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
    .upsert(snapshotRow, {
      onConflict: "user_id,model_version,input_hash",
      ignoreDuplicates: true,
    }).retry(false);

  if (snapshotError && snapshotError.code !== "23505") {
    throw new Error(`Snapshot insert failed: ${snapshotError.message}`);
  }

  return {
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
      score: currentPreparation.actualPreparationScore,
      // Rank needs a separately maintained cohort snapshot. Never run a
      // cohort scan (or claim rank 1 of 1) on a student's dashboard request.
      status: "temporarily_unavailable",
      rank: null,
      cohortSize: 0,
      components: currentPreparation?.components ?? null,
      calculatedAt,
    },
    countdown: esatCountdown(asOf),
  };
}

export async function GET() {
  try {
    const session = await createSupabaseServerClient();
    const { data: { user }, error: userError } = await withServiceTimeout(session.auth.getUser());
    if (userError) {
      if (isMissingSession(userError)) return json({ ok: false, error: "Unauthorized" }, 401);
      throw userError;
    }
    if (!user?.id || !user.email) return json({ ok: false, error: "Unauthorized" }, 401);

    const admin = adminClient();
    // The verified session is the only source of identity. Escape LIKE tokens
    // so an email containing '_' or '%' cannot match someone else's access.
    const email = user.email.trim().toLowerCase().replace(/[\\%_]/g, "\\$&");
    const { data: accessRows, error: accessError } = await admin.from("student_access")
      .select("product,approved,expires_at")
      .ilike("email", email)
      .in("product", [...ESAT_ACCESS_PRODUCTS])
      .eq("approved", true)
      .or(`expires_at.is.null,expires_at.gt.${new Date().toISOString()}`)
      .limit(1).retry(false);
    if (accessError) throw accessError;
    if (!accessRows?.length) return json({ ok: false, error: "No ESAT access" }, 403);

    return json(await currentUserOverview(admin, user.id));
  } catch (error) {
    console.error("ESAT overview failed", error);
    const response = json({
      ok: false,
      error: "Your ESAT overview is temporarily unavailable. Please try again shortly.",
      retryable: true,
    }, 503);
    response.headers.set("Retry-After", "30");
    return response;
  }
}
