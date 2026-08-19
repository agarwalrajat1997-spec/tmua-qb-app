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
import { createSupabaseServerClient } from "@/lib/supabase/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const PAGE_SIZE = 1000;
const MAX_ROWS = 10000;

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
      // Identical full-paper mass to a recognised full TMUA mock.
      effectiveWeight: 1.5,
    }];
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

    const [attemptRows, questionRows, qbRows] = await Promise.all([
      readAll((from, to) =>
        admin
          .from("practice_test_attempts")
          .select("id,test_id,answers,attempt_number,submitted_at")
          .eq("user_id", user.id)
          .in("test_id", recognisedIds)
          .order("submitted_at", { ascending: true })
          .range(from, to),
      ),
      readActiveQuestions(admin),
      readAll((from, to) =>
        admin
          .from("tmua_qb_attempt_events")
          .select(
            "id,question_id,source,history_quality,predictor_eligible,metadata,selected_answer,attempted_at",
          )
          .eq("user_id", user.id)
          .eq("product", "esat-question-bank")
          .eq("source", "qb-progress-trigger-v2")
          .eq("history_quality", "observed")
          .order("attempted_at", { ascending: true })
          .range(from, to),
      ),
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

    const qbEvents: EsatPredictorQbEvent[] = qbRows.map((row) => {
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

    const result = calculateEsatPredictorV1({
      testAttempts: buildTestEvidence(attemptRows),
      qbEvents,
      activeTopics: [...activeTopicSet].sort((a, b) => a.localeCompare(b)),
    });

    const calculatedAt = new Date().toISOString();

    // The deployed TMUA snapshot store is model-version keyed and already
    // supplies the required append-only/RLS guarantees. ESAT uses a distinct
    // model version and input hash, so the two evidence histories cannot mix.
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
        diagnostics: result.diagnostics,
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
