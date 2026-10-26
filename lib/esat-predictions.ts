export const ESAT_MODULES = ["Mathematics 1", "Mathematics 2", "Physics", "Chemistry", "Biology"] as const;
export type EsatModule = typeof ESAT_MODULES[number];
export type EsatConfidence = "low" | "medium" | "high";
export const ESAT_GUARANTEE_POLICY = "esat-two-modules-half-point-v1";

export type EsatModulePrediction = {
  module: EsatModule;
  score: number | null;
  confidence: EsatConfidence | null;
  lowerBound: number | null;
  upperBound: number | null;
  independentTestCount: number;
  qbUniqueQuestions: number;
  qbTopicCoverage: number;
  guaranteeEligible: boolean;
  inputHash: string;
};

export function normaliseEsatModule(value: unknown): EsatModule | null {
  const name = String(value ?? "").trim().replace(/^ESAT\s+/i, "");
  return ESAT_MODULES.find(module => module.toLowerCase() === name.toLowerCase()) ?? null;
}

export function validateEsatModules(value: unknown): EsatModule[] {
  if (!Array.isArray(value) || value.length !== 3 || new Set(value).size !== 3 ||
      !value.includes("Mathematics 1") || value.some(module => !ESAT_MODULES.includes(module))) {
    throw new Error("Choose Mathematics 1 and exactly two other ESAT modules.");
  }
  return ESAT_MODULES.filter(module => value.includes(module));
}

/** Midnight in London, two calendar days before the booked exam date. */
export function esatLockAt(examDate: string): string {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(examDate)) throw new Error("Enter your booked exam date.");
  const date = new Date(`${examDate}T00:00:00Z`);
  if (!Number.isFinite(date.valueOf()) || date.toISOString().slice(0, 10) !== examDate) throw new Error("Enter a valid exam date.");
  const midnight = new Date(date.valueOf() - 2 * 86400000);
  const zone = new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/London", timeZoneName: "longOffset" })
    .formatToParts(midnight).find(part => part.type === "timeZoneName")?.value;
  const offset = zone?.match(/GMT([+-])(\d{2}):(\d{2})/);
  const minutes = offset ? (Number(offset[2]) * 60 + Number(offset[3])) * (offset[1] === "+" ? 1 : -1) : 0;
  return new Date(midnight.valueOf() - minutes * 60000).toISOString();
}

export function qualifiesForEsatGuarantee(score: number | null, confidence: EsatConfidence | null): boolean {
  return score !== null && score >= 3.5 && (confidence === "medium" || confidence === "high");
}

export function assessEsatResults(predictions: EsatModulePrediction[], actual: Record<string, unknown>) {
  if (predictions.length !== 3) throw new Error("Three locked module predictions are required.");
  validateEsatModules(predictions.map(prediction => prediction.module));
  const modules = predictions.map(prediction => {
    const score = actual[prediction.module];
    if (typeof score !== "number" || !Number.isFinite(score) || score < 1 || score > 9 ||
        Math.abs(score * 10 - Math.round(score * 10)) > 1e-8) {
      throw new Error(`Enter the official ${prediction.module} result from 1.0 to 9.0, with at most one decimal place.`);
    }
    const eligible = qualifiesForEsatGuarantee(prediction.score, prediction.confidence);
    // Compare the same one-decimal prediction the student saw. Exactly 0.5 is not a miss.
    const missed = eligible && Math.round(prediction.score! * 10) - Math.round(score * 10) > 5;
    return { module: prediction.module, predicted: prediction.score, actual: score, confidence: prediction.confidence, eligible, missed };
  });
  const missedCount = modules.filter(module => module.missed).length;
  return { policyVersion: ESAT_GUARANTEE_POLICY, modules, missedCount, meetsScoreCondition: missedCount >= 2 };
}
