import { getCanonicalEsatTest } from "./esat-canonical-tests.ts";
import {
  estimateOctober2026EsatScores,
  getEsatPredictorFamilyId,
} from "./esat-october-2026-tests.ts";
import type { EsatPredictorTestAttempt } from "./esat-predictor-v1-engine.ts";
import { estimateEsatTestScores, getEsatTestProfile } from "./esat-score-estimates.ts";

type StoredEsatAttempt = {
  id?: unknown;
  test_id?: unknown;
  answers?: unknown;
  attempt_number?: unknown;
  submitted_at?: unknown;
};

/** Re-evaluate saved answers, including historical October attempts. Never use
 * a client score or stale saved predictor eligibility as scoring authority.
 */
export function buildEsatTestEvidence(rows: readonly StoredEsatAttempt[]): EsatPredictorTestAttempt[] {
  return rows.flatMap((row) => {
    const testId = String(row.test_id ?? "").trim();
    const canonical = getCanonicalEsatTest(testId);
    const submitted = Array.isArray(row.answers) ? row.answers : [];
    const evaluatedAt = new Date(String(row.submitted_at ?? ""));

    if (!canonical || submitted.length !== canonical.expectedQuestions ||
        !Number.isFinite(evaluatedAt.valueOf())) {
      return [];
    }

    const answers = submitted.map(value => String(value ?? "").trim().toUpperCase());
    const sectionScores = canonical.sectionRanges.map(([start, end]) => {
      let correct = 0;
      for (let index = start; index < end; index += 1) {
        if (answers[index] && answers[index] === canonical.answers[index]) correct += 1;
      }
      return correct;
    });
    const estimate = estimateOctober2026EsatScores(testId, sectionScores) ??
      (getEsatTestProfile(testId) ? estimateEsatTestScores(testId, sectionScores) : null);
    if (!estimate) return [];

    const familyId = getEsatPredictorFamilyId(testId);
    return [{
      testId: familyId,
      attemptId: String(row.id),
      // Pathway attempt numbers are separate sequences. Use dates to select
      // the first/latest across all versions of the shared October papers.
      attemptNumber: familyId !== testId ? null :
        Number.isInteger(Number(row.attempt_number)) && Number(row.attempt_number) > 0
          ? Number(row.attempt_number) : null,
      evaluatedAt: evaluatedAt.toISOString(),
      predictorEligible: true,
      predictedCombinedPracticeScore: estimate.predictedCombinedPracticeScore,
      effectiveWeight: 1.5,
    }];
  });
}
