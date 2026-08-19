import { createHash } from "node:crypto";

import {
  applyTmuaHighScoreEvidenceGate,
} from "./tmua-predictor-v1_1-policy.ts";
import { ESAT_CANONICAL_KEY_VERSION } from "./esat-canonical-tests.ts";
import { ESAT_SCORE_ESTIMATE_VERSION } from "./esat-score-estimates.ts";
import {
  calculateTmuaPredictorV1,
  type TmuaPredictorQbEvent,
  type TmuaPredictorResult,
  type TmuaPredictorTestAttempt,
} from "./tmua-predictor-v1-engine.ts";

export const ESAT_PREDICTOR_V1_MODEL_VERSION =
  "esat-predictor-v1.0.0" as const;

export type EsatPredictorTestAttempt = {
  testId: string;
  attemptId: string;
  attemptNumber: number | null;
  evaluatedAt: string;
  predictorEligible: boolean;
  predictedCombinedPracticeScore: number | null;
  effectiveWeight: number | null;
};

export type EsatPredictorQbEvent = TmuaPredictorQbEvent;

export type EsatPredictorInput = {
  testAttempts: EsatPredictorTestAttempt[];
  qbEvents: EsatPredictorQbEvent[];
  activeTopics: string[];
};

export type EsatPredictorResult = Omit<
  TmuaPredictorResult,
  "modelVersion" |
  "predictedTmuaScore9" |
  "testSignalScore9" |
  "conversionSetHash" |
  "inputHash"
> & {
  modelVersion: typeof ESAT_PREDICTOR_V1_MODEL_VERSION;
  predictedEsatPracticeScore: number | null;
  testSignalPracticeScore: number | null;
  calibrationSetHash: string;
  inputHash: string;
};

/*
 * The underlying TMUA engine is deliberately reused for evidence
 * aggregation only. Its raw-mark conversions are never used: every ESAT
 * attempt enters as an already module-equated 1-9 practice score.
 * This keeps retake collapse, QB weighting, confidence and range rules
 * identical to the production TMUA predictor without importing TMUA raw
 * conversion tables into ESAT scoring.
 */
const UNUSED_CONVERSION_PROFILES = Array.from(
  { length: 12 },
  (_, profileIndex) => ({
    profileId: `esat-unused-${String(profileIndex + 1).padStart(2, "0")}`,
    scores: Array.from(
      { length: 41 },
      (_, raw) => 1 + (8 * raw) / 40,
    ),
  }),
);

function esatHash(value: string): string {
  return createHash("sha256")
    .update(`${ESAT_PREDICTOR_V1_MODEL_VERSION}\n${value}`, "utf8")
    .digest("hex");
}

const CALIBRATION_SET_HASH = createHash("sha256")
  .update(
    `${ESAT_SCORE_ESTIMATE_VERSION}\n${ESAT_CANONICAL_KEY_VERSION}`,
    "utf8",
  )
  .digest("hex");

export function calculateEsatPredictorV1(
  input: EsatPredictorInput,
): EsatPredictorResult {
  const testAttempts: TmuaPredictorTestAttempt[] =
    input.testAttempts.map((attempt) => ({
      testId: attempt.testId,
      attemptId: attempt.attemptId,
      attemptNumber: attempt.attemptNumber,
      evaluatedAt: attempt.evaluatedAt,
      predictorEligible: attempt.predictorEligible,
      topicBreadth: "full_syllabus",
      combinedScoreEligible: true,
      authoritativeTmuaScore9:
        attempt.predictedCombinedPracticeScore,
      effectiveWeight: attempt.effectiveWeight,
      paper1RawScore: null,
      paper1EffectiveWeight: null,
      paper2RawScore: null,
      paper2EffectiveWeight: null,
    }));

  const base = applyTmuaHighScoreEvidenceGate(
    calculateTmuaPredictorV1({
      conversionProfiles: UNUSED_CONVERSION_PROFILES,
      activeTopics: input.activeTopics,
      testAttempts,
      qbEvents: input.qbEvents,
    }),
  );

  const {
    predictedTmuaScore9,
    testSignalScore9,
    conversionSetHash: _unusedConversionSetHash,
    ...shared
  } = base;

  void _unusedConversionSetHash;

  return {
    ...shared,
    modelVersion: ESAT_PREDICTOR_V1_MODEL_VERSION,
    predictedEsatPracticeScore: predictedTmuaScore9,
    testSignalPracticeScore: testSignalScore9,
    calibrationSetHash: CALIBRATION_SET_HASH,
    inputHash: esatHash(base.inputHash),
  };
}
