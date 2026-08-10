import type {
  TmuaPredictorResult,
} from "./tmua-predictor-v1-engine";

export type TmuaPredictionSnapshotInsert = {
  userId: string;

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

  confidence:
    | "low"
    | "medium"
    | "high"
    | null;

  testSignalScore9:
    | number
    | null;

  testWeight: number;
  testEvidenceCount: number;
  independentTestCount: number;
  combinedFullCount: number;

  qbSignalScore9:
    | number
    | null;

  qbWeight: number;
  qbUniqueQuestions: number;
  qbTopicCoverage: number;

  conversionSetHash: string;
  activeTopicSetHash: string;

  evidenceDetails:
    Record<string, unknown>;

  calculatedAt: string;
};

function requireNonEmpty(
  value: string,
  label: string,
): string {
  const normalized =
    value.trim();

  if (!normalized) {
    throw new Error(
      `${label} cannot be empty`,
    );
  }

  return normalized;
}

function canonicalTimestamp(
  value: string,
): string {
  const milliseconds =
    Date.parse(value);

  if (!Number.isFinite(milliseconds)) {
    throw new Error(
      "calculatedAt must be a valid timestamp",
    );
  }

  return new Date(
    milliseconds,
  ).toISOString();
}

export function buildTmuaPredictionSnapshotInsert(
  userId: string,
  result: TmuaPredictorResult,
  calculatedAt: string,
): TmuaPredictionSnapshotInsert {
  const normalizedUserId =
    requireNonEmpty(
      userId,
      "userId",
    );

  const normalizedCalculatedAt =
    canonicalTimestamp(
      calculatedAt,
    );

  return {
    userId:
      normalizedUserId,

    modelVersion:
      requireNonEmpty(
        result.modelVersion,
        "modelVersion",
      ),

    inputHash:
      requireNonEmpty(
        result.inputHash,
        "inputHash",
      ),

    predictionStatus:
      result.predictionStatus,

    predictedTmuaScore9:
      result.predictedTmuaScore9,

    lowerBound:
      result.lowerBound,

    upperBound:
      result.upperBound,

    confidence:
      result.confidence,

    testSignalScore9:
      result.testSignalScore9,

    testWeight:
      result.testWeight,

    testEvidenceCount:
      result.testEvidenceCount,

    independentTestCount:
      result.independentTestCount,

    combinedFullCount:
      result.combinedFullCount,

    qbSignalScore9:
      result.qbSignalScore9,

    qbWeight:
      result.qbWeight,

    qbUniqueQuestions:
      result.qbUniqueQuestions,

    qbTopicCoverage:
      result.qbTopicCoverage,

    conversionSetHash:
      requireNonEmpty(
        result.conversionSetHash,
        "conversionSetHash",
      ),

    activeTopicSetHash:
      requireNonEmpty(
        result.activeTopicSetHash,
        "activeTopicSetHash",
      ),

    evidenceDetails: {
      model_version:
        result.modelVersion,

      input_hash:
        result.inputHash,

      conversion_set_hash:
        result.conversionSetHash,

      active_topic_set_hash:
        result.activeTopicSetHash,

      broad_test_family_count:
        result.diagnostics
          .broadTestFamilyCount,

      test_signal_standard_deviation:
        result.diagnostics
          .testSignalStandardDeviation,

      qb_overall_accuracy:
        result.diagnostics
          .qbOverallAccuracy,

      qb_lower_quartile_topic_accuracy:
        result.diagnostics
          .qbLowerQuartileTopicAccuracy,

      qb_balanced_accuracy:
        result.diagnostics
          .qbBalancedAccuracy,

      qb_recovery_fraction:
        result.diagnostics
          .qbRecoveryFraction,

      qb_recovery_opportunity_count:
        result.diagnostics
          .qbRecoveryOpportunityCount,

      trusted_qb_event_count:
        result.diagnostics
          .trustedQbEventCount,

      eligible_first_exposure_count:
        result.diagnostics
          .eligibleFirstExposureCount,

      test_families:
        result.diagnostics
          .testFamilies,
    },

    calculatedAt:
      normalizedCalculatedAt,
  };
}