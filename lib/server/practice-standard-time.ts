import { createHash } from "node:crypto";
import { validatePracticeSettings, type PracticeSettings, type StandardTimeUnit, type StandardTimeEstimate } from "../practice-settings.ts";
export type { StandardTimeUnit, StandardTimeEstimate } from "../practice-settings.ts";
import { getCanonicalTmuaTest } from "./tmua-canonical-tests.ts";
import { getCanonicalEsatTest } from "./esat-canonical-tests.ts";
import { estimateEsatTestScores } from "./esat-score-estimates.ts";
import { estimateOctober2026EsatScores } from "./esat-october-2026-tests.ts";
import { TMUA_PREDICTIVE_2026_ID, TMUA_PREDICTIVE_2026_SCORES } from "./tmua-predictive-2026.ts";
import type { TmuaPastPaperSettings } from "../tmua/past-paper-settings.ts";
import { estimateTmuaTopicScore } from "./tmua-topic-score-estimates.ts";

export const STANDARD_TIME_POLICY_VERSION = "ts-standard-time-equivalent-v1";
export const STANDARD_TIME_LABEL = "Estimated standard-time equivalent";
export type Conversion = { profile: string; conversion_version?: string; score_values: readonly (number | string)[] };

export function practiceSpec(testId: string) {
  const tmua = getCanonicalTmuaTest(testId);
  if (tmua && [20, 40].includes(tmua.expectedQuestions) && Array.isArray(tmua.answers)) return { exam: "tmua" as const, canonical: tmua, sections: tmua.expectedQuestions === 40 ? [20, 20] : [20], seconds: 4500 };
  const esat = getCanonicalEsatTest(testId);
  return esat?.expectedQuestions === 81 && Array.isArray(esat.answers) ? { exam: "esat" as const, canonical: esat, sections: [27, 27, 27], seconds: 2400 } : null;
}

export function resolvePracticeSettings(testId: string, value: unknown, legacy?: TmuaPastPaperSettings | null): PracticeSettings | null {
  if (value === undefined && !legacy) return null;
  const spec = practiceSpec(testId);
  if (!spec) throw new Error("Practice settings are supported only for recognised TMUA and ESAT tests.");
  const resolved = validatePracticeSettings(value === undefined && legacy ? {
    version: 1, order: legacy.order, time_multiplier: legacy.time_multiplier,
    question_order: legacy.question_order, section_sizes: spec.sections,
    base_seconds_per_section: spec.seconds,
  } : value, spec.sections, spec.seconds);
  if (resolved && legacy && (resolved.order !== legacy.order || resolved.time_multiplier !== legacy.time_multiplier ||
      resolved.question_order.some((value, i) => value !== legacy.question_order[i]))) throw new Error("Legacy and universal practice settings disagree.");
  return resolved;
}

const normaliseAnswers = (answers: readonly unknown[]) => answers.map(value => String(value ?? "").trim().toUpperCase());
const answersHash = (answers: readonly unknown[]) => createHash("sha256").update(JSON.stringify(normaliseAnswers(answers))).digest("hex");
export const rawDeduction = (multiplier: PracticeSettings["time_multiplier"], size: number) =>
  Math.round((multiplier === 1.25 ? 3 : multiplier === 1.5 ? 5 : 0) * size / 40);

export function hasStandardTimePolicy(metadata: unknown): boolean {
  if (!metadata || typeof metadata !== "object" || Array.isArray(metadata)) return false;
  const stored = (metadata as Record<string, unknown>).standard_time_estimate;
  return Boolean(stored && typeof stored === "object" &&
    (stored as Record<string, unknown>).policy_version === STANDARD_TIME_POLICY_VERSION);
}

export function createStandardTimeEstimate(testId: string, answers: readonly unknown[], settings: PracticeSettings, conversion?: Conversion | null, allowMissingConversion = false): StandardTimeEstimate {
  const spec = practiceSpec(testId);
  if (!spec || answers.length !== spec.canonical.expectedQuestions) throw new Error("Canonical answers are required for the standard-time estimate.");
  validatePracticeSettings(settings, spec.sections, spec.seconds);
  const selected = normaliseAnswers(answers);
  const count = (start: number, size: number) => selected.slice(start, start + size)
    .reduce((sum, answer, index) => sum + Number(Boolean(answer) && answer === spec.canonical.answers[start + index]), 0);
  const actualRaw = count(0, selected.length);
  const sizes = spec.exam === "tmua" ? [selected.length] : spec.sections;
  let offset = 0;
  const units: StandardTimeUnit[] = sizes.map((size, index) => {
    const actual = count(offset, size); offset += size;
    const deduction = rawDeduction(settings.time_multiplier, size);
    return { label: spec.exam === "esat" ? getCanonicalEsatTest(testId)!.modules[index] : size === 40 ? "Full test" : "Paper",
      actual_raw: actual, total_questions: size, deduction, adjusted_raw: Math.max(0, actual - deduction), estimated_score: null };
  });
  let estimatedScore: number | null = null;
  let conversionProfile: string | null = null;
  let conversionVersion: string | null = null;
  if (spec.exam === "esat") {
    const marks = units.map(unit => unit.adjusted_raw);
    const estimate = estimateOctober2026EsatScores(testId, marks) ?? estimateEsatTestScores(testId, marks);
    units.forEach((unit, index) => { unit.estimated_score = estimate.modules[index].estimatedScore; });
    estimatedScore = estimate.predictedCombinedPracticeScore;
    conversionVersion = estimate.version;
  } else if (selected.length === 20) {
    const topic = estimateTmuaTopicScore(testId, units[0].adjusted_raw);
    estimatedScore = topic.score;
    units[0].estimated_score = estimatedScore;
    conversionProfile = topic.profile;
    conversionVersion = topic.profile;
  } else if (selected.length === 40) {
    const scores = testId === TMUA_PREDICTIVE_2026_ID ? TMUA_PREDICTIVE_2026_SCORES : conversion?.score_values;
    const validScores = Array.isArray(scores) && scores.length === 41 && !scores.some((score, index) =>
      !Number.isFinite(Number(score)) || Number(score) < 1 || Number(score) > 9 || (index > 0 && Number(score) < Number(scores[index - 1])));
    if (!validScores) {
      if (!allowMissingConversion) throw new Error("A trusted TMUA conversion profile is required for this estimate.");
    } else {
      estimatedScore = Number(scores![units[0].adjusted_raw]);
      units[0].estimated_score = estimatedScore;
    }
    conversionProfile = testId === TMUA_PREDICTIVE_2026_ID ? "ts-tmua-strict-24-33-v1-20260919" : conversion?.profile ?? null;
    conversionVersion = testId === TMUA_PREDICTIVE_2026_ID ? conversionProfile : conversion?.conversion_version ?? null;
  }
  const deductionPer40 = settings.time_multiplier === 1.25 ? 3 : settings.time_multiplier === 1.5 ? 5 : 0;
  return {
    policy_version: STANDARD_TIME_POLICY_VERSION, label: STANDARD_TIME_LABEL,
    provisional: true, official: false, test_id: testId, time_multiplier: settings.time_multiplier,
    actual_raw: actualRaw, total_questions: selected.length, deduction_per_40: deductionPer40,
    adjusted_raw: units.reduce((sum, unit) => sum + unit.adjusted_raw, 0), estimated_score: estimatedScore, units,
    note: `Provisional practice estimate, not validated against exam outcomes and not an official result. Actual raw marks are unchanged. The ${deductionPer40}-mark allowance per 40 questions is rounded separately for each scoring unit (${units.map(unit => `${unit.deduction}/${unit.total_questions}`).join(", ")}) and adjusted marks are clamped at zero.${spec.exam === "esat" ? " ESAT module estimates are separate; their mean is only a TS practice signal." : selected.length === 20 ? " This uses the standalone test's own practice conversion, not an official overall TMUA score." : estimatedScore === null ? " The trusted score conversion is temporarily unavailable. Raw marks and settings are saved; the converted estimate is pending until the conversion is available." : ""}`,
    canonical_key_sha256: spec.canonical.canonicalSha256, answers_sha256: answersHash(answers),
    conversion_profile: conversionProfile, conversion_version: conversionVersion,
  };
}

/** New-policy rows only. Historical v1 presentation metadata never opts a row in. */
export function readPracticeResult(testId: string, metadata: unknown, answers?: unknown, actualRaw?: unknown): { practice_settings: PracticeSettings | null; standard_time_estimate: StandardTimeEstimate | null } {
  const empty = { practice_settings: null, standard_time_estimate: null };
  if (!metadata || typeof metadata !== "object" || Array.isArray(metadata)) return empty;
  const source = metadata as Record<string, unknown>;
  const stored = source.standard_time_estimate as StandardTimeEstimate | undefined;
  if (!stored || stored.policy_version !== STANDARD_TIME_POLICY_VERSION || stored.test_id !== testId) return empty;
  try {
    const settings = resolvePracticeSettings(testId, source.practice_settings);
    const spec = practiceSpec(testId);
    if (!settings || !spec || stored.canonical_key_sha256 !== spec.canonical.canonicalSha256 ||
        stored.time_multiplier !== settings.time_multiplier || stored.total_questions !== spec.canonical.expectedQuestions ||
        stored.deduction_per_40 !== rawDeduction(settings.time_multiplier, 40) ||
        stored.provisional !== true || stored.official !== false || stored.label !== STANDARD_TIME_LABEL ||
        !Array.isArray(stored.units) || (actualRaw !== undefined && Number(actualRaw) !== stored.actual_raw)) return empty;
    if (answers !== undefined && (!Array.isArray(answers) || answers.length !== spec.canonical.expectedQuestions || stored.answers_sha256 !== answersHash(answers))) return empty;
    const sizes = spec.exam === "tmua" ? [spec.canonical.expectedQuestions] : spec.sections;
    if (stored.units.length !== sizes.length || stored.units.some((unit, index) =>
      unit.total_questions !== sizes[index] || !Number.isInteger(unit.actual_raw) || unit.actual_raw < 0 || unit.actual_raw > sizes[index] ||
      unit.deduction !== rawDeduction(settings.time_multiplier, sizes[index]) || unit.adjusted_raw !== Math.max(0, unit.actual_raw - unit.deduction) ||
      (unit.estimated_score !== null && (!Number.isFinite(unit.estimated_score) || unit.estimated_score < 1 || unit.estimated_score > 9)))) return empty;
    if (stored.actual_raw !== stored.units.reduce((sum, unit) => sum + unit.actual_raw, 0) ||
        stored.adjusted_raw !== stored.units.reduce((sum, unit) => sum + unit.adjusted_raw, 0) ||
        (stored.estimated_score !== null && (!Number.isFinite(stored.estimated_score) || stored.estimated_score < 1 || stored.estimated_score > 9))) return empty;
    if (Array.isArray(answers)) {
      const selected = normaliseAnswers(answers);
      let offset = 0;
      for (const unit of stored.units) {
        const correct = selected.slice(offset, offset + unit.total_questions)
          .reduce((sum, answer, index) => sum + Number(Boolean(answer) && answer === spec.canonical.answers[offset + index]), 0);
        if (correct !== unit.actual_raw) return empty;
        offset += unit.total_questions;
      }
    }
    return { practice_settings: settings, standard_time_estimate: stored };
  } catch { return empty; }
}

/** History display, like predictor evidence, recomputes the numeric estimate.
 * A stored client-editable snapshot is not authority for its own scaled score.
 * Unavailable conversions hide the scaled score instead of returning a raw score
 * under an adjusted label; the separately returned actual marks remain intact.
 */
export function readTrustedPracticeResult(testId: string, metadata: unknown, answers: unknown, actualRaw: unknown, conversion?: Conversion | null) {
  const result = readPracticeResult(testId, metadata, answers, actualRaw);
  if (!result.practice_settings || !Array.isArray(answers)) return { practice_settings: null, standard_time_estimate: null };
  try {
    return { practice_settings: result.practice_settings,
      standard_time_estimate: createStandardTimeEstimate(testId, answers, result.practice_settings, conversion, true) };
  } catch { return { practice_settings: result.practice_settings, standard_time_estimate: null }; }
}
