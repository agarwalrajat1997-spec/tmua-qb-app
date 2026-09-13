import { createHash } from "node:crypto";

export const TMUA_PREDICTOR_V11_MODEL_VERSION =
  "tmua-predictor-v1.1.0" as const;

export const TMUA_PREDICTOR_V11_POLICY = Object.freeze({
  qbOnlyMaximum: 6.25,
  oneIndependentTestMaximum: 6.75,
  twoTestsWithoutFullMaximum: 6.95,
  maximumQbUpwardBoostFromTestSignal: 0.25,
  score7Threshold: 7,
  score8Threshold: 8,
  testsForScore7WithFull: 2,
  fullTestsForScore7: 1,
  alternativeTestsForScore7: 3,
  testsForScore8: 3,
  fullTestsForScore8: 2,
});

type PredictorLike = {
  modelVersion: string;
  inputHash: string;

  predictionStatus:
    | "predicted"
    | "insufficient_evidence";

  predictedTmuaScore9:
    | number
    | null;

  lowerBound:
    | number
    | null;

  upperBound:
    | number
    | null;

  testSignalScore9:
    | number
    | null;

  independentTestCount: number;
  combinedFullCount: number;
  qbWeight: number;

  evidenceDetails?:
    | Record<string, unknown>
    | null;
};

function round2(value: number): number {
  return Math.round(value * 100) / 100;
}

function clampScore(value: number): number {
  return Math.min(
    9,
    Math.max(1, value),
  );
}

function finiteScore(
  value: number | null,
): number | null {
  return (
    typeof value === "number" &&
    Number.isFinite(value)
  )
    ? value
    : null;
}

function v11InputHash(
  previousInputHash: string,
): string {
  return createHash("sha256")
    .update(
      `${TMUA_PREDICTOR_V11_MODEL_VERSION}\n${previousInputHash}`,
      "utf8",
    )
    .digest("hex");
}

function evidenceCeiling(input: {
  independentTestCount: number;
  combinedFullCount: number;
  testSignalScore9: number | null;
}): number {
  const independent =
    Math.max(
      0,
      Math.trunc(
        input.independentTestCount,
      ),
    );

  const full =
    Math.max(
      0,
      Math.trunc(
        input.combinedFullCount,
      ),
    );

  const testSignal =
    finiteScore(
      input.testSignalScore9,
    );

  if (independent === 0) {
    return (
      TMUA_PREDICTOR_V11_POLICY
        .qbOnlyMaximum
    );
  }

  if (independent === 1) {
    return (
      TMUA_PREDICTOR_V11_POLICY
        .oneIndependentTestMaximum
    );
  }

  if (
    independent === 2 &&
    full === 0
  ) {
    return (
      TMUA_PREDICTOR_V11_POLICY
        .twoTestsWithoutFullMaximum
    );
  }

  const demonstratedSeven =
    testSignal !== null &&
    testSignal >=
      TMUA_PREDICTOR_V11_POLICY
        .score7Threshold &&
    (
      (
        independent >=
          TMUA_PREDICTOR_V11_POLICY
            .testsForScore7WithFull &&
        full >=
          TMUA_PREDICTOR_V11_POLICY
            .fullTestsForScore7
      )
      ||
      independent >=
        TMUA_PREDICTOR_V11_POLICY
          .alternativeTestsForScore7
    );

  if (!demonstratedSeven) {
    return (
      TMUA_PREDICTOR_V11_POLICY
        .twoTestsWithoutFullMaximum
    );
  }

  const demonstratedEight =
    testSignal !== null &&
    testSignal >=
      TMUA_PREDICTOR_V11_POLICY
        .score8Threshold &&
    independent >=
      TMUA_PREDICTOR_V11_POLICY
        .testsForScore8 &&
    full >=
      TMUA_PREDICTOR_V11_POLICY
        .fullTestsForScore8;

  return demonstratedEight
    ? 9
    : 8;
}

export function applyTmuaHighScoreEvidenceGate<
  T extends PredictorLike,
>(
  result: T,
): T {
  const nextInputHash =
    v11InputHash(
      result.inputHash,
    );

  const commonEvidence = {
    ...(result.evidenceDetails ?? {}),
    high_score_evidence_gate: {
      version:
        TMUA_PREDICTOR_V11_MODEL_VERSION,

      independent_test_count:
        result.independentTestCount,

      combined_full_count:
        result.combinedFullCount,

      test_signal_score9:
        result.testSignalScore9,
    },
  };

  const rawScore =
    finiteScore(
      result.predictedTmuaScore9,
    );

  if (
    result.predictionStatus !==
      "predicted" ||
    rawScore === null
  ) {
    return {
      ...result,

      modelVersion:
        TMUA_PREDICTOR_V11_MODEL_VERSION,

      inputHash:
        nextInputHash,

      evidenceDetails: {
        ...commonEvidence,

        high_score_evidence_gate: {
          ...(
            commonEvidence
              .high_score_evidence_gate
          ),

          applied: false,
          reason:
            "insufficient_evidence",
        },
      },
    } as T;
  }

  const testSignal =
    finiteScore(
      result.testSignalScore9,
    );

  const evidenceMaximum =
    evidenceCeiling({
      independentTestCount:
        result.independentTestCount,

      combinedFullCount:
        result.combinedFullCount,

      testSignalScore9:
        testSignal,
    });

  const qbBoostMaximum =
    (
      testSignal !== null &&
      result.qbWeight > 0
    )
      ? Math.min(
          9,
          testSignal +
            TMUA_PREDICTOR_V11_POLICY
              .maximumQbUpwardBoostFromTestSignal,
        )
      : 9;

  const finalMaximum =
    Math.min(
      evidenceMaximum,
      qbBoostMaximum,
    );

  const finalScore =
    round2(
      Math.min(
        rawScore,
        finalMaximum,
      ),
    );

  const downwardShift =
    Math.max(
      0,
      rawScore - finalScore,
    );

  const shiftBound = (
    value: number | null,
  ): number | null => {
    if (
      value === null ||
      !Number.isFinite(value)
    ) {
      return null;
    }

    return round2(
      clampScore(
        value - downwardShift,
      ),
    );
  };

  return {
    ...result,

    modelVersion:
      TMUA_PREDICTOR_V11_MODEL_VERSION,

    inputHash:
      nextInputHash,

    predictedTmuaScore9:
      finalScore,

    lowerBound:
      shiftBound(
        result.lowerBound,
      ),

    upperBound:
      shiftBound(
        result.upperBound,
      ),

    evidenceDetails: {
      ...commonEvidence,

      high_score_evidence_gate: {
        ...(
          commonEvidence
            .high_score_evidence_gate
        ),

        applied:
          finalScore < rawScore,

        raw_predicted_tmua_score9:
          rawScore,

        evidence_score_ceiling:
          round2(
            evidenceMaximum,
          ),

        qb_boost_ceiling:
          round2(
            qbBoostMaximum,
          ),

        final_score_ceiling:
          round2(
            finalMaximum,
          ),

        final_predicted_tmua_score9:
          finalScore,
      },
    },
  } as T;
}