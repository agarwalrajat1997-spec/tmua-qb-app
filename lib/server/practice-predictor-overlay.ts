import { getCanonicalTmuaTest } from "./tmua-canonical-tests.ts";
import { TMUA_PREDICTIVE_2026_ID } from "./tmua-predictive-2026.ts";
import { createStandardTimeEstimate, hasStandardTimePolicy, rawDeduction, readPracticeResult, type Conversion } from "./practice-standard-time.ts";

type Evaluation = {
  attempt_id: unknown; test_id: unknown;
  [key: string]: unknown;
};
type Attempt = {
  id: unknown; test_id: unknown; answers?: unknown; time_spent?: unknown;
  predictor_metadata?: unknown;
};
type Catalogue = {
  test_id: string; score_conversion_profile?: string | null;
  base_weight?: number | string; minimum_partial_answered?: number | string;
  minimum_full_weight_answered?: number | string; minimum_average_seconds?: number | string;
};

function completion(answered: number, partial: number, full: number) {
  return answered < partial ? 0 : answered < full - 2 ? .35 : answered < full ? .7 : 1;
}
function timing(seconds: number, answered: number, expected: number, minimumAverage: number) {
  if (!answered || seconds <= 0 || seconds / answered < minimumAverage) return 0;
  const ratio = seconds / expected;
  return ratio < .15 ? 0 : ratio < .25 ? .15 : ratio < .35 ? .45 : ratio < .5 ? .75 : ratio <= 1.35 ? 1 : ratio <= 2 ? .9 : .75;
}
const round4 = (value: number) => Math.round(value * 10000) / 10000;

/** In-memory overlay only. Actual marks and database evaluations are immutable
 * here, and old attempts without the explicit submission policy marker pass
 * through byte-for-byte. New evidence is rebuilt from canonical answers.
 */
export function applyStandardTimeTmuaEvaluations<T extends Evaluation>(
  evaluations: readonly T[], attempts: readonly Attempt[], profiles: readonly Conversion[], catalogue: readonly Catalogue[],
): T[] {
  const byAttempt = new Map(attempts.map(attempt => [String(attempt.id), attempt]));
  const byTest = new Map(catalogue.map(test => [test.test_id, test]));
  return evaluations.map(evaluation => {
    const attempt = byAttempt.get(String(evaluation.attempt_id));
    if (!attempt || attempt.test_id !== evaluation.test_id) return evaluation;
    const testId = String(attempt.test_id);
    const canonical = getCanonicalTmuaTest(testId);
    const practice = readPracticeResult(testId, attempt.predictor_metadata, attempt.answers);
    const exclude = () => ({ ...evaluation, predictor_eligible: false, combined_score_eligible: false, effective_weight: 0,
      paper_1_effective_weight: 0, paper_2_effective_weight: 0, authoritative_tmua_score9: null });
    if (hasStandardTimePolicy(attempt.predictor_metadata) && !practice.practice_settings) return exclude();
    if (!practice.practice_settings) return evaluation;
    if (!canonical || !Array.isArray(attempt.answers) || !Array.isArray(attempt.time_spent) ||
        attempt.time_spent.length !== canonical.expectedQuestions || attempt.time_spent.some(time => !Number.isFinite(Number(time)) || Number(time) < 0)) return exclude();
    const test = byTest.get(testId);
    if (!test) return exclude();
    const conversion = profiles.find(profile => profile.profile === test.score_conversion_profile);
    let estimate;
    try { estimate = createStandardTimeEstimate(testId, attempt.answers, practice.practice_settings, conversion); }
    catch { return { ...evaluation, predictor_eligible: false, combined_score_eligible: false, effective_weight: 0,
      paper_1_effective_weight: 0, paper_2_effective_weight: 0, authoritative_tmua_score9: null }; }

    const answers = attempt.answers.map(answer => String(answer ?? "").trim().toUpperCase());
    const times = attempt.time_spent.map(Number);
    const base = Number(test.base_weight ?? (testId === TMUA_PREDICTIVE_2026_ID ? .95 : 0));
    const partial = Number(test.minimum_partial_answered ?? 12);
    const full = Number(test.minimum_full_weight_answered ?? 18);
    const minimumAverage = Number(test.minimum_average_seconds ?? 10);
    const multiplier = practice.practice_settings.time_multiplier;
    const papers = (canonical.expectedQuestions === 40 ? [0, 20] : [0]).map(offset => {
      const selected = answers.slice(offset, offset + 20);
      const answered = selected.filter(Boolean).length;
      const actual = selected.reduce((sum, answer, index) => sum + Number(Boolean(answer) && answer === canonical.answers[offset + index]), 0);
      const elapsed = times.slice(offset, offset + 20).reduce((sum, value) => sum + value, 0);
      const validity = completion(answered, partial, full) * timing(elapsed, answered, 4500 * multiplier, minimumAverage);
      return { answered, validity, actual, raw: actual,
        weight: round4(base * (canonical.expectedQuestions === 40 ? .75 : 1) * validity) };
    });
    if (papers.length === 2) {
      // Full tests have ONE /40 deduction, including when the predictor uses
      // partial paper evidence. Allocate its clamped integer deduction across
      // the two actual raw marks proportionally; their adjusted sum exactly
      // matches the full-test adjusted mark (never a second /20 rounding).
      const deducted = estimate.actual_raw - estimate.adjusted_raw;
      const first = estimate.actual_raw ? Math.round(deducted * papers[0].actual / estimate.actual_raw) : 0;
      papers[0].raw = papers[0].actual - first;
      papers[1].raw = papers[1].actual - (deducted - first);
    } else {
      papers[0].raw = Math.max(0, papers[0].actual - rawDeduction(multiplier, 20));
    }
    const combined = papers.length === 2 && papers.every(paper => paper.answered >= full && paper.validity >= .75);
    const effective = round4(combined ? base * (papers[0].validity + papers[1].validity) / 2 : Math.max(...papers.map(paper => paper.weight)));
    const p1 = canonical.structure === "paper2" ? null : papers[0];
    const p2 = canonical.structure === "full" ? papers[1] : canonical.structure === "paper2" ? papers[0] : null;
    return { ...evaluation,
      predictor_eligible: effective > 0, combined_score_eligible: combined,
      authoritative_tmua_score9: combined ? estimate.estimated_score : null, effective_weight: effective,
      paper_1_raw_score: p1?.raw ?? 0, paper_2_raw_score: p2?.raw ?? 0,
      paper_1_effective_weight: p1?.weight ?? 0, paper_2_effective_weight: p2?.weight ?? 0,
    };
  });
}
