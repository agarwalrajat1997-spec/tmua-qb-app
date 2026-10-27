import { createHash } from "node:crypto";
import { ESAT_MODULES, normaliseEsatModule, qualifiesForEsatGuarantee, type EsatModule, type EsatModulePrediction } from "../esat-predictions.ts";
import { getCanonicalEsatTest } from "./esat-canonical-tests.ts";
import { estimateEsatTestScores, getEsatTestProfile } from "./esat-score-estimates.ts";
import { estimateOctober2026EsatScores } from "./esat-october-2026-tests.ts";
import { createStandardTimeEstimate, hasStandardTimePolicy, readPracticeResult } from "./practice-standard-time.ts";
import { calculateEsatPredictorV1, type EsatPredictorTestAttempt, type EsatPredictorQbEvent } from "./esat-predictor-v1-engine.ts";

export const ESAT_MODULE_MODEL_VERSION = "esat-module-predictor-v1-20261027";
export type EvidenceRow = Record<string, unknown>;
const before = (value: unknown, cutoff: number) => Number.isFinite(Date.parse(String(value))) && Date.parse(String(value)) <= cutoff;

export function buildEsatModuleTestEvidence(rows: EvidenceRow[], cutoff: number) {
  const evidence: Record<EsatModule, EsatPredictorTestAttempt[]> = { "Mathematics 1": [], "Mathematics 2": [], Physics: [], Chemistry: [], Biology: [] };
  for (const row of rows) {
    const testId = String(row.test_id ?? "");
    const canonical = getCanonicalEsatTest(testId);
    if (!canonical || !Array.isArray(row.answers) || row.answers.length !== canonical.expectedQuestions || !before(row.submitted_at, cutoff)) continue;
    const answers = row.answers.map(answer => String(answer ?? "").trim().toUpperCase());
    const raw = canonical.sectionRanges.map(([start, end]) => answers.slice(start, end)
      .reduce((sum, answer, index) => sum + Number(Boolean(answer) && answer === canonical.answers[start + index]), 0));
    const estimate = estimateOctober2026EsatScores(testId, raw) ?? (getEsatTestProfile(testId) ? estimateEsatTestScores(testId, raw) : null);
    if (!estimate) continue;
    const practice = readPracticeResult(testId, row.predictor_metadata, answers, raw.reduce((sum, value) => sum + value, 0));
    if (hasStandardTimePolicy(row.predictor_metadata) && !practice.practice_settings) continue;
    const standard = practice.practice_settings ? createStandardTimeEstimate(testId, answers, practice.practice_settings) : null;
    estimate.modules.forEach((module, index) => {
      const [start, end] = canonical.sectionRanges[index];
      // A blank section is not evidence that the student is taking that module.
      if (!answers.slice(start, end).some(Boolean)) return;
      const score = standard ? standard.units[index].estimated_score : module.estimatedScore;
      if (score == null) return;
      // Recombined pathways reuse module papers. Count their shared source once,
      // even when the student sat it under several different pathway IDs.
      const family = module.calibrationId ?? `october-2026:${module.module}`;
      evidence[module.module].push({
        testId: `${module.module}:${family}`, attemptId: String(row.id), attemptNumber: null,
        evaluatedAt: String(row.submitted_at), predictorEligible: true,
        predictedCombinedPracticeScore: score, effectiveWeight: 1.5,
      });
    });
  }
  return evidence;
}

/** Infer the practiced pathway without requiring an exam plan or guessing subjects. */
export function inferEsatPathway(predictions: EsatModulePrediction[]) {
  const optional = predictions.filter(prediction => prediction.module !== "Mathematics 1" &&
    (prediction.independentTestCount > 0 || prediction.qbUniqueQuestions >= 30));
  const strength = (prediction: EsatModulePrediction) =>
    prediction.independentTestCount * 2 + Math.min(prediction.qbUniqueQuestions / 30, 3);
  optional.sort((a, b) => strength(b) - strength(a) || ESAT_MODULES.indexOf(a.module) - ESAT_MODULES.indexOf(b.module));
  // When several pathways have been explored, require a clear evidence lead.
  // Equal evidence must not silently choose Physics over Chemistry, for example.
  const inferred = optional.length === 2 ||
    (optional.length > 2 && strength(optional[1]) > strength(optional[2]) * 1.25);
  const selected = inferred ? optional.slice(0, 2) : optional;
  const modules = ESAT_MODULES.filter(module => module === "Mathematics 1" || selected.some(item => item.module === module));
  return { status: inferred ? "inferred" as const : "building" as const, modules };
}

export function calculateEsatModulePredictions(input: {
  modules: EsatModule[]; attempts: EvidenceRow[]; questions: EvidenceRow[]; qbRows: EvidenceRow[]; asOf: string;
}): EsatModulePrediction[] {
  const cutoff = Date.parse(input.asOf);
  if (!Number.isFinite(cutoff)) throw new Error("A valid prediction cutoff is required.");
  const tests = buildEsatModuleTestEvidence(input.attempts, cutoff);
  const questionMap = new Map(input.questions.map(question => [String(question.qid), question]));
  return input.modules.map(module => {
    const questions = input.questions.filter(question => question.is_active === true && normaliseEsatModule(question.paper) === module);
    const activeTopics = [...new Set(questions.map(question => String(question.topic ?? "").trim()).filter(Boolean))].sort();
    const qbEvents: EsatPredictorQbEvent[] = input.qbRows.flatMap(row => {
      const metadata = row.metadata && typeof row.metadata === "object" ? row.metadata as Record<string, unknown> : {};
      const qid = String(metadata.canonical_qid ?? row.question_id ?? "").trim();
      const question = questionMap.get(qid);
      if (!question || normaliseEsatModule(question.paper) !== module || !before(row.attempted_at, cutoff)) return [];
      return [{
        id: String(row.id), source: String(row.source), historyQuality: String(row.history_quality),
        predictorEligible: row.predictor_eligible === true, canonicalQid: qid, canonicalActive: question.is_active === true,
        selectedAnswer: row.selected_answer == null ? null : String(row.selected_answer),
        canonicalAnswer: question.answer == null ? null : String(question.answer),
        canonicalTopic: question.topic == null ? null : String(question.topic), attemptedAt: String(row.attempted_at),
      }];
    });
    // Reuse the established evidence/confidence policy independently per subject.
    // No evidence from another module enters this calculation.
    const result = calculateEsatPredictorV1({ testAttempts: tests[module], qbEvents, activeTopics });
    const rawScore = result.predictedEsatPracticeScore;
    const score = rawScore !== null && rawScore >= 3.5 ? Math.round(rawScore * 10) / 10 : null;
    const confidence = score === null ? null : result.confidence;
    return {
      module, score, confidence,
      lowerBound: score === null || result.lowerBound === null ? null : Math.round(result.lowerBound * 10) / 10,
      upperBound: score === null || result.upperBound === null ? null : Math.round(result.upperBound * 10) / 10,
      independentTestCount: result.independentTestCount, qbUniqueQuestions: result.qbUniqueQuestions, qbTopicCoverage: result.qbTopicCoverage,
      guaranteeEligible: qualifiesForEsatGuarantee(score, confidence),
      inputHash: createHash("sha256").update(`${ESAT_MODULE_MODEL_VERSION}:${module}:${result.inputHash}`).digest("hex"),
    };
  });
}
