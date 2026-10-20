/* eslint-disable @typescript-eslint/no-explicit-any */

import { createHash, randomUUID } from "node:crypto";
import type { adminClient } from "../../app/api/esat/qb/_server";
import { ESAT_CANONICAL_TESTS } from "./esat-canonical-tests.ts";
import { getEsatPredictorFamilyId } from "./esat-october-2026-tests.ts";
import { buildEsatTestEvidence } from "./esat-predictor-evidence.ts";
import {
  calculateEsatPredictorV1,
  type EsatPredictorQbEvent,
  type EsatPredictorTestAttempt,
} from "./esat-predictor-v1-engine.ts";
import {
  calculatePreparationScore,
  rankPreparationCohort,
} from "./tmua-preparation-rank-v1-engine.ts";

type Admin = ReturnType<typeof adminClient>;
type Row = Record<string, any>;

export const ESAT_PREPARATION_RANK_MODEL_VERSION = "esat-preparation-rank-v1-20260819";
const PAGE_SIZE = 1000;
const MAX_ROWS = 100_000;
const ACTIVE_WINDOW_MS = 30 * 24 * 60 * 60 * 1000;
const ACCESS_PRODUCTS = ["esat-practice-tests", "esat-question-bank", "esat-classes"];
// Keep the same canonical-table fallback order as the ESAT QB server. Only a
// missing relation may advance to an alias; an outage must fail the refresh.
const QUESTION_TABLES = ["esat_qb_questions", "esat_questions", "esat_qb_public_questions", "esat_question_bank"];

async function readAll(
  label: string,
  query: (from: number, to: number) => PromiseLike<{ data: any[] | null; error: any }>,
): Promise<Row[]> {
  const rows: Row[] = [];
  // The final sentinel page distinguishes an exact limit from an incomplete
  // read. Never publish a ranking based on silently truncated evidence.
  for (let from = 0; from <= MAX_ROWS; from += PAGE_SIZE) {
    const { data, error } = await query(from, from + PAGE_SIZE - 1);
    if (error) throw error;
    const page = data ?? [];
    if (rows.length + page.length > MAX_ROWS) {
      throw new Error(`${label} exceeded the pagination safety limit`);
    }
    rows.push(...page);
    if (page.length < PAGE_SIZE) return rows;
  }
  throw new Error(`${label} exceeded the pagination safety limit`);
}

async function readAuthUsers(admin: Admin): Promise<Row[]> {
  const users: Row[] = [];
  const seen = new Set<string>();
  let expectedTotal: number | null = null;
  for (let page = 1; page <= MAX_ROWS / PAGE_SIZE + 1; page += 1) {
    const response = await admin.auth.admin.listUsers({ page, perPage: PAGE_SIZE });
    if (response.error) throw new Error(`ESAT cohort auth users: ${response.error.message}`);
    const pageUsers = response.data.users;
    const total = response.data.total;
    if (Number.isInteger(total) && total > 0) {
      if (expectedTotal !== null && total !== expectedTotal) {
        throw new Error("ESAT auth-user cohort changed during pagination; retry the refresh");
      }
      expectedTotal = total;
    }
    for (const user of pageUsers) {
      if (!user.id || seen.has(user.id)) {
        throw new Error("ESAT auth-user pagination returned a missing or duplicate identity");
      }
      seen.add(user.id);
      users.push(user);
    }
    if (users.length > MAX_ROWS) throw new Error("ESAT auth-user pagination exceeded safety limit");
    if (pageUsers.length < PAGE_SIZE) {
      if (expectedTotal !== null && expectedTotal !== users.length) {
        throw new Error("ESAT auth-user pagination did not return the complete cohort");
      }
      return users.sort((a, b) => String(a.id).localeCompare(String(b.id)));
    }
  }
  throw new Error("ESAT auth-user pagination exceeded safety limit");
}

async function readActiveQuestions(admin: Admin): Promise<Row[]> {
  let lastError: unknown;
  for (const table of QUESTION_TABLES) {
    try {
      return await readAll("ESAT canonical questions", (from, to) => admin.from(table)
        .select("qid,topic,answer,is_active")
        .eq("is_active", true).order("qid", { ascending: true })
        .range(from, to).retry(false));
    } catch (error) {
      lastError = error;
      const code = (error as { code?: string })?.code;
      if (code !== "42P01" && code !== "PGRST205") throw error;
    }
  }
  throw lastError ?? new Error("No ESAT canonical question table is available");
}

function canonicalQid(metadata: unknown, fallback: unknown): string | null {
  if (metadata && typeof metadata === "object" && !Array.isArray(metadata)) {
    const qid = String((metadata as Record<string, unknown>).canonical_qid ?? "").trim();
    if (qid) return qid;
  }
  return String(fallback ?? "").trim() || null;
}

function withinWindow(value: unknown, start: number, end: number): boolean {
  if (value == null) return false;
  const time = Date.parse(String(value));
  return Number.isFinite(time) && time > start && time <= end;
}

function buildQbEvents(rows: Row[], questions: Map<string, Row>): EsatPredictorQbEvent[] {
  return rows.map(row => {
    const qid = canonicalQid(row.metadata, row.question_id);
    const question = qid ? questions.get(qid) : null;
    return {
      id: String(row.id), source: String(row.source), historyQuality: String(row.history_quality),
      predictorEligible: Boolean(row.predictor_eligible), canonicalQid: qid,
      canonicalActive: Boolean(question?.is_active),
      selectedAnswer: row.selected_answer == null ? null : String(row.selected_answer),
      canonicalAnswer: question?.answer == null ? null : String(question.answer),
      canonicalTopic: question?.topic == null ? null : String(question.topic),
      attemptedAt: String(row.attempted_at),
    };
  });
}

// Identical to the current ESAT overview consistency input. The canonical
// evidence adapter already collapses pathway IDs into shared paper families.
function buildTestFamilySignals(attempts: EsatPredictorTestAttempt[]) {
  const families = new Map<string, EsatPredictorTestAttempt[]>();
  for (const attempt of attempts) {
    if (attempt.predictorEligible !== true || attempt.predictedCombinedPracticeScore == null) continue;
    const family = families.get(attempt.testId) ?? [];
    family.push(attempt);
    families.set(attempt.testId, family);
  }
  return [...families.values()].map(family => {
    const ordered = [...family].sort((a, b) => Date.parse(a.evaluatedAt) - Date.parse(b.evaluatedAt));
    const first = ordered[0].predictedCombinedPracticeScore as number;
    const latest = ordered[ordered.length - 1].predictedCombinedPracticeScore as number;
    return { score9: ordered.length === 1 ? first : 0.75 * first + 0.25 * latest, weight: 1.5 };
  });
}

function byUser(rows: Row[]): Map<string, Row[]> {
  const grouped = new Map<string, Row[]>();
  for (const row of rows) {
    const userId = String(row.user_id ?? "").trim();
    if (!userId) continue;
    const userRows = grouped.get(userId) ?? [];
    userRows.push(row);
    grouped.set(userId, userRows);
  }
  return grouped;
}

/** Background-only service-role worker. Student overview requests read a
 * completed snapshot instead of running this cohort scan. No scoring formula,
 * evidence rule, entitlement rule or ESAT cohort exclusion is introduced here.
 */
export async function refreshEsatPreparationRank(admin: Admin): Promise<{
  runId: string;
  cohortSize: number;
  calculatedAt: string;
}> {
  const asOf = new Date();
  const asOfMs = asOf.getTime();
  const calculatedAt = asOf.toISOString();
  const windowStartMs = asOfMs - ACTIVE_WINDOW_MS;
  const recognisedIds = Object.keys(ESAT_CANONICAL_TESTS);
  const recognised = new Set(recognisedIds);
  const [attemptRows, qbRows, questions, accessRows, authUsers] = await Promise.all([
    readAll("ESAT test evidence", (from, to) => admin.from("practice_test_attempts")
      .select("id,user_id,test_id,answers,attempt_number,submitted_at,predictor_metadata")
      .in("test_id", recognisedIds).order("submitted_at", { ascending: true })
      .order("id", { ascending: true }).range(from, to).retry(false)),
    readAll("ESAT Question Bank evidence", (from, to) => admin.from("tmua_qb_attempt_events")
      .select("id,user_id,question_id,source,history_quality,predictor_eligible,metadata,selected_answer,attempted_at")
      .eq("product", "esat-question-bank").eq("source", "qb-progress-trigger-v2")
      .eq("history_quality", "observed").order("attempted_at", { ascending: true })
      .order("id", { ascending: true }).range(from, to).retry(false)),
    readActiveQuestions(admin),
    readAll("ESAT entitlements", (from, to) => admin.from("student_access")
      .select("email,product,approved,expires_at").in("product", ACCESS_PRODUCTS)
      .eq("approved", true).order("id", { ascending: true }).range(from, to).retry(false)),
    readAuthUsers(admin),
  ]);

  const questionByQid = new Map<string, Row>();
  const topicSet = new Set<string>();
  for (const question of questions) {
    const qid = String(question.qid ?? "").trim();
    const topic = String(question.topic ?? "").trim();
    if (qid) questionByQid.set(qid, question);
    if (topic) topicSet.add(topic);
  }
  const activeTopics = [...topicSet].sort((a, b) => a.localeCompare(b));
  const entitledEmails = new Set<string>();
  for (const row of accessRows) {
    if (row.approved !== true) continue;
    if (row.expires_at != null) {
      const expires = Date.parse(String(row.expires_at));
      if (!Number.isFinite(expires) || expires <= asOfMs) continue;
    }
    const email = String(row.email ?? "").trim().toLowerCase();
    if (email) entitledEmails.add(email);
  }
  const entitledUsers = authUsers.filter(user => entitledEmails.has(String(user.email ?? "").trim().toLowerCase()));
  const attemptsByUser = byUser(attemptRows);
  const qbByUser = byUser(qbRows);
  const records = entitledUsers.map(user => {
    const userId = String(user.id);
    const userAttempts = attemptsByUser.get(userId) ?? [];
    const userQb = qbByUser.get(userId) ?? [];
    const testEvidence = buildEsatTestEvidence(userAttempts);
    const predictor = calculateEsatPredictorV1({
      testAttempts: testEvidence, qbEvents: buildQbEvents(userQb, questionByQid), activeTopics,
    });
    const recentTests = new Set<string>();
    for (const row of userAttempts) {
      if (!withinWindow(row.submitted_at, windowStartMs, asOfMs)) continue;
      const testId = String(row.test_id ?? "").trim();
      if (recognised.has(testId)) recentTests.add(getEsatPredictorFamilyId(testId));
    }
    const recentQb = new Set<string>();
    for (const row of userQb) {
      if (!withinWindow(row.attempted_at, windowStartMs, asOfMs)) continue;
      const qid = canonicalQid(row.metadata, row.question_id);
      if (qid && questionByQid.has(qid)) recentQb.add(qid);
    }
    const loginActive = withinWindow(user.last_sign_in_at, windowStartMs, asOfMs);
    const testActive = recentTests.size > 0;
    const qbActive = recentQb.size > 0;
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
    return { userId, active: loginActive || testActive || qbActive, loginActive, testActive, qbActive,
      predictor, preparation, recentQbCount: recentQb.size, recentTestCount: recentTests.size };
  });
  const ranking = rankPreparationCohort(records.map(record => ({
    userId: record.userId, active: record.active, score: record.preparation,
  })));
  const rankingByUser = new Map(ranking.map(row => [row.userId, row]));
  const activeRecords = records.filter(record => record.active);
  const cohortSize = activeRecords.length;
  const runId = randomUUID();
  // Include the as-of time and fresh run identity: old content-equal runs must
  // never be reused after the rolling activity window has moved.
  const inputHash = createHash("sha256").update(JSON.stringify({
    model: ESAT_PREPARATION_RANK_MODEL_VERSION, calculatedAt, runId,
    records: records.map(record => ({ userId: record.userId, active: record.active,
      predictorHash: record.predictor.inputHash, score: record.preparation.actualPreparationScore,
      recentQbCount: record.recentQbCount, recentTestCount: record.recentTestCount })),
  })).digest("hex");
  const { error: runError } = await admin.from("tmua_preparation_rank_runs").insert({
    id: runId, model_version: ESAT_PREPARATION_RANK_MODEL_VERSION, input_hash: inputHash,
    cohort_as_of: calculatedAt, window_start: new Date(windowStartMs).toISOString(),
    entitled_auth_user_count: entitledUsers.length, excluded_user_count: 0,
    active_cohort_size: cohortSize,
    rankable_count: ranking.filter(row => row.actualPreparationRank !== null).length,
    cohort_details: { product: "esat", rolling_window_days: 30,
      login_only_active: activeRecords.filter(row => row.loginActive && !row.testActive && !row.qbActive).length,
      prep_active_without_recent_login: activeRecords.filter(row => !row.loginActive && (row.testActive || row.qbActive)).length },
  }).retry(false);
  if (runError) throw new Error(`ESAT rank run insert failed: ${runError.message}`);

  const snapshotRows = activeRecords.map(record => {
    const ranked = rankingByUser.get(record.userId);
    if (!ranked) throw new Error("ESAT rank persistence is missing ranking output");
    const components = record.preparation.components;
    return {
      run_id: runId, user_id: record.userId, model_version: ESAT_PREPARATION_RANK_MODEL_VERSION,
      genuine_preparation_evidence: record.preparation.hasGenuinePreparationEvidence,
      actual_preparation_score: ranked.actualPreparationScore,
      actual_preparation_rank: ranked.actualPreparationRank,
      actual_active_cohort_size: cohortSize,
      performance_component: components.performance, breadth_component: components.breadth,
      evidence_depth_component: components.evidenceDepth, recent_activity_component: components.recentActivity,
      consistency_component: components.consistency, recovery_component: components.recovery,
      predicted_tmua_score9: record.predictor.predictedEsatPracticeScore,
      predictor_input_hash: record.predictor.inputHash,
      broad_or_full_independent_test_families: record.predictor.independentTestCount,
      predictor_test_weight: record.predictor.testWeight,
      trusted_unique_first_exposures: record.predictor.qbUniqueQuestions,
      trusted_canonical_topic_coverage: record.predictor.qbTopicCoverage,
      distinct_canonical_qb_interactions_30d: record.recentQbCount,
      independent_recognised_test_families_30d: record.recentTestCount,
      recovery_value: null,
      evidence_details: { product: "esat", predictor_model_version: record.predictor.modelVersion,
        login_active: record.loginActive, test_active: record.testActive, qb_active: record.qbActive },
      created_at: calculatedAt,
    };
  });
  for (let from = 0; from < snapshotRows.length; from += PAGE_SIZE) {
    const { error } = await admin.from("tmua_preparation_rank_snapshots")
      .insert(snapshotRows.slice(from, from + PAGE_SIZE)).retry(false);
    if (error) throw new Error(`ESAT rank snapshot insert failed: ${error.message}`);
  }
  const { count, error: countError } = await admin.from("tmua_preparation_rank_snapshots")
    .select("id", { count: "exact", head: true }).eq("run_id", runId)
    .eq("model_version", ESAT_PREPARATION_RANK_MODEL_VERSION).retry(false);
  if (countError || count !== cohortSize) {
    throw new Error(`ESAT rank snapshot completeness check failed: ${countError?.message ?? `${count}/${cohortSize}`}`);
  }
  // The caller may publish this run to its completed-cache pointer only now.
  return { runId, cohortSize, calculatedAt };
}
