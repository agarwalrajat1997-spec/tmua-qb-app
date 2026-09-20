import type { TmuaCanonicalTest } from "./tmua-canonical-tests";
import type { TmuaDatabaseTestEvaluationRow } from "./tmua-predictor-v1-evidence-adapter";

export const TMUA_PREDICTIVE_2026_ID = "tmua-2026-predictive-paper";
export const TMUA_PREDICTIVE_2026_PROFILE = "ts-tmua-strict-24-33-v1-20260919";
export const TMUA_PREDICTIVE_2026_SCORES = Object.freeze([
  1,1.1,1.2,1.3,1.4,1.6,1.8,2,2.2,2.4,2.5,2.7,2.9,3,3.2,3.3,3.5,3.7,3.8,4,
  4.2,4.3,4.5,4.6,4.8,5,5.3,5.5,5.8,6,6.3,6.5,6.8,7,7.3,7.6,7.9,8.1,8.4,8.7,9,
]);
export const TMUA_PREDICTIVE_2026_CANONICAL: TmuaCanonicalTest = Object.freeze({
  testId: TMUA_PREDICTIVE_2026_ID,
  keyVersion: "tmua-predictive-2026-keys-20260920-v1",
  sourceCommit: "018e9b9",
  sourceFile: "public/practice-tests/tests/tmua-2026-predictive-paper/index.html",
  structure: "full",
  expectedQuestions: 40,
  paper1Range: [0,20] as const,
  paper2Range: [20,40] as const,
  canonicalSha256: "c2895da5b2ff2f79c24edcbfc52582b9e54e0025ccb8eb9ef3951fca46412995",
  answers: Object.freeze("CCEADDADEBACDCBDDECAEEBCCCCDDBEDDDABBAEA".split("")),
});
// Kept outside the twelve historical conversion curves: this is an
// owner-selected practice scale, not another historical reference prior.
export const TMUA_PREDICTIVE_2026_CATALOG = Object.freeze({
  test_id: TMUA_PREDICTIVE_2026_ID,
  title: "TMUA 2026 Predictive Practice Test",
  paper: "full" as const,
  expected_questions: 40,
  score_conversion_profile: TMUA_PREDICTIVE_2026_PROFILE,
  topic_breadth: "full_syllabus",
  predictor_enabled: true,
  leaderboard_enabled: true,
});

export function scoreTmuaPredictive2026(raw: number): number {
  if (!Number.isInteger(raw) || raw < 0 || raw > 40) throw new Error("Expected an integer raw TMUA mark from 0 to 40.");
  return TMUA_PREDICTIVE_2026_SCORES[raw];
}

export type TmuaPredictive2026AttemptRow = {
  id: unknown;
  user_id: unknown;
  test_id: unknown;
  submitted_at: unknown;
  answers: unknown;
  time_spent: unknown;
  predictor_metadata?: Record<string, unknown> | null;
};

// These factors mirror the existing tmua_completion_factor and
// tmua_timing_factor policy, using the mock-full base weight of 0.95.
function completion(answered: number) {
  return answered < 12 ? 0 : answered < 16 ? 0.35 : answered < 18 ? 0.7 : 1;
}
function timing(seconds: number, answered: number) {
  if (answered <= 0 || seconds <= 0 || seconds / answered < 10) return 0;
  const proportion = seconds / 4500;
  return proportion < 0.15 ? 0 : proportion < 0.25 ? 0.15 : proportion < 0.35 ? 0.45
    : proportion < 0.5 ? 0.75 : proportion <= 1.35 ? 1 : proportion <= 2 ? 0.9 : 0.75;
}
const round4 = (n: number) => Math.round(n * 10000) / 10000;

export function evaluateTmuaPredictive2026Attempt(row: TmuaPredictive2026AttemptRow): TmuaDatabaseTestEvaluationRow | null {
  if (row.test_id !== TMUA_PREDICTIVE_2026_ID || !String(row.id ?? "").trim() || !String(row.user_id ?? "").trim()) return null;
  if (!Array.isArray(row.answers) || row.answers.length !== 40 || !Array.isArray(row.time_spent) || row.time_spent.length !== 40) return null;
  const evaluatedAt = new Date(String(row.submitted_at ?? ""));
  if (!Number.isFinite(evaluatedAt.valueOf())) return null;
  if (row.predictor_metadata?.tmua_predictive_2026_complete === false) return null;
  const answers = row.answers.map(a => a == null ? null : String(a).trim().toUpperCase() || null);
  if (answers.some(a => a !== null && !/^[A-H]$/.test(a))) return null;
  const times = row.time_spent.map(Number);
  if (times.some(t => !Number.isFinite(t) || t < 0)) return null;
  const papers = [0,20].map(offset => {
    const slice = answers.slice(offset,offset + 20);
    const answered = slice.filter(a => a !== null).length;
    const raw = slice.reduce<number>((n,a,i) => n + (a === TMUA_PREDICTIVE_2026_CANONICAL.answers[offset + i] ? 1 : 0),0);
    const elapsed = times.slice(offset,offset + 20).reduce((n,t) => n + t,0);
    const validity = completion(answered) * timing(elapsed,answered);
    return { answered, raw, validity, weight: round4(0.95 * 0.75 * validity) };
  });
  const combined = papers.every(p => p.answered >= 18 && p.validity >= 0.75);
  const weight = round4(combined ? 0.95 * (papers[0].validity + papers[1].validity) / 2 : Math.max(papers[0].weight,papers[1].weight));
  return {
    user_id: String(row.user_id), test_id: TMUA_PREDICTIVE_2026_ID, attempt_id: String(row.id),
    attempt_number: null, evaluated_at: evaluatedAt.toISOString(), predictor_eligible: weight > 0,
    topic_breadth: "full_syllabus", combined_score_eligible: combined,
    authoritative_tmua_score9: combined ? scoreTmuaPredictive2026(papers[0].raw + papers[1].raw) : null,
    effective_weight: weight, paper_1_raw_score: papers[0].raw, paper_2_raw_score: papers[1].raw,
    paper_1_effective_weight: papers[0].weight, paper_2_effective_weight: papers[1].weight,
  };
}

export function buildTmuaPredictive2026Evaluations(rows: readonly TmuaPredictive2026AttemptRow[]) {
  const evaluations = rows.map(evaluateTmuaPredictive2026Attempt).filter((row): row is TmuaDatabaseTestEvaluationRow => row !== null);
  evaluations.sort((a,b) => a.user_id.localeCompare(b.user_id) || Date.parse(a.evaluated_at) - Date.parse(b.evaluated_at) || a.attempt_id.localeCompare(b.attempt_id));
  const counts = new Map<string,number>();
  return evaluations.map(row => {
    const attemptNumber = (counts.get(row.user_id) ?? 0) + 1;
    counts.set(row.user_id,attemptNumber);
    return { ...row, attempt_number: attemptNumber };
  });
}
