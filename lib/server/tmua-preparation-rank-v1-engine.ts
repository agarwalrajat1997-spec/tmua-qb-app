export const TMUA_PREPARATION_RANK_MODEL_VERSION =
  "tmua-preparation-rank-v1-20260810" as const;

export type PreparationTestFamilySignal = {
  score9: number;
  weight: number;
};

export type PreparationRankEvidence = {
  predictedTmuaScore9: number | null;

  broadOrFullIndependentTestFamilies: number;
  predictorTestWeight: number;

  trustedUniqueFirstExposures: number;
  trustedCanonicalTopicCoverage: number;

  distinctCanonicalQbInteractions30d: number;
  independentRecognisedTestFamilies30d: number;

  testFamilySignals: PreparationTestFamilySignal[];

  hasGenuineTestEvidence: boolean;
  hasGenuineQbEvidence: boolean;

  recovery: number | null;
};

export type PreparationComponents = {
  performance: number;
  breadth: number;
  evidenceDepth: number;
  recentActivity: number;
  consistency: number;
  recovery: number;
};

export type PreparationScoreResult = {
  modelVersion:
    typeof TMUA_PREPARATION_RANK_MODEL_VERSION;

  hasGenuinePreparationEvidence: boolean;

  actualPreparationScore: number | null;

  components: PreparationComponents;
};

export type PreparationRankingInput = {
  userId: string;

  active: boolean;

  score: PreparationScoreResult;
};

export type PreparationRankingResult = {
  userId: string;

  active: boolean;

  actualPreparationScore: number | null;

  actualPreparationRank: number | null;

  actualActiveCohortSize: number;
};

function finiteNumber(
  value: number,
  field: string,
): number {
  if (!Number.isFinite(value)) {
    throw new Error(
      `${field} must be finite`,
    );
  }

  return value;
}

function nonNegative(
  value: number,
  field: string,
): number {
  finiteNumber(
    value,
    field,
  );

  if (value < 0) {
    throw new Error(
      `${field} cannot be negative`,
    );
  }

  return value;
}

export function clamp01(
  value: number,
): number {
  finiteNumber(
    value,
    "clamp01 value",
  );

  return Math.min(
    1,
    Math.max(
      0,
      value,
    ),
  );
}

function unionCoverage(
  left: number,
  right: number,
): number {
  const a =
    clamp01(left);

  const b =
    clamp01(right);

  return (
    1 -
    (1 - a) *
      (1 - b)
  );
}

export function preparationPerformance(
  predictedTmuaScore9: number | null,
): number {
  if (predictedTmuaScore9 == null) {
    return 0;
  }

  finiteNumber(
    predictedTmuaScore9,
    "predictedTmuaScore9",
  );

  return clamp01(
    (predictedTmuaScore9 - 1) / 8,
  );
}

export function preparationBreadth(input: {
  broadOrFullIndependentTestFamilies: number;
  trustedCanonicalTopicCoverage: number;
}): number {
  const families =
    nonNegative(
      input.broadOrFullIndependentTestFamilies,
      "broadOrFullIndependentTestFamilies",
    );

  const testBreadth =
    Math.min(
      1,
      families / 2,
    );

  const qbBreadth =
    clamp01(
      input.trustedCanonicalTopicCoverage,
    );

  return unionCoverage(
    testBreadth,
    qbBreadth,
  );
}

export function preparationEvidenceDepth(input: {
  predictorTestWeight: number;
  trustedUniqueFirstExposures: number;
}): number {
  const testWeight =
    nonNegative(
      input.predictorTestWeight,
      "predictorTestWeight",
    );

  const uniqueQb =
    nonNegative(
      input.trustedUniqueFirstExposures,
      "trustedUniqueFirstExposures",
    );

  const testDepth =
    Math.min(
      1,
      testWeight / 2,
    );

  const qbDepth =
    Math.min(
      1,
      uniqueQb / 150,
    );

  return unionCoverage(
    testDepth,
    qbDepth,
  );
}

export function preparationRecentActivity(input: {
  distinctCanonicalQbInteractions30d: number;
  independentRecognisedTestFamilies30d: number;
}): number {
  const qbInteractions =
    nonNegative(
      input.distinctCanonicalQbInteractions30d,
      "distinctCanonicalQbInteractions30d",
    );

  const testFamilies =
    nonNegative(
      input.independentRecognisedTestFamilies30d,
      "independentRecognisedTestFamilies30d",
    );

  const qbActivity =
    Math.min(
      1,
      qbInteractions / 60,
    );

  const testActivity =
    Math.min(
      1,
      testFamilies / 2,
    );

  return (
    0.70 * qbActivity +
    0.30 * testActivity
  );
}

export function weightedPopulationSd(
  signals: PreparationTestFamilySignal[],
): number | null {
  const usable =
    signals.filter(
      (signal) => {
        finiteNumber(
          signal.score9,
          "testFamilySignals.score9",
        );

        nonNegative(
          signal.weight,
          "testFamilySignals.weight",
        );

        return signal.weight > 0;
      },
    );

  if (usable.length < 2) {
    return null;
  }

  const totalWeight =
    usable.reduce(
      (sum, signal) =>
        sum + signal.weight,
      0,
    );

  if (totalWeight <= 0) {
    return null;
  }

  const mean =
    usable.reduce(
      (sum, signal) =>
        sum +
        signal.score9 *
          signal.weight,
      0,
    ) / totalWeight;

  const variance =
    usable.reduce(
      (sum, signal) => {
        const difference =
          signal.score9 - mean;

        return (
          sum +
          signal.weight *
            difference *
            difference
        );
      },
      0,
    ) / totalWeight;

  return Math.sqrt(
    Math.max(
      0,
      variance,
    ),
  );
}

export function preparationConsistency(input: {
  hasGenuinePreparationEvidence: boolean;
  testFamilySignals: PreparationTestFamilySignal[];
}): number {
  if (
    !input.hasGenuinePreparationEvidence
  ) {
    return 0;
  }

  const usableCount =
    input.testFamilySignals.filter(
      (signal) => {
        finiteNumber(
          signal.score9,
          "testFamilySignals.score9",
        );

        nonNegative(
          signal.weight,
          "testFamilySignals.weight",
        );

        return signal.weight > 0;
      },
    ).length;

  if (usableCount < 2) {
    return 0.5;
  }

  const sd =
    weightedPopulationSd(
      input.testFamilySignals,
    );

  if (sd == null) {
    return 0.5;
  }

  return Math.max(
    0,
    1 - sd / 1.5,
  );
}

export function preparationRecovery(input: {
  hasGenuineQbEvidence: boolean;
  recovery: number | null;
}): number {
  if (!input.hasGenuineQbEvidence) {
    return 0;
  }

  if (input.recovery == null) {
    return 0.5;
  }

  return clamp01(
    input.recovery,
  );
}

export function calculatePreparationScore(
  evidence: PreparationRankEvidence,
): PreparationScoreResult {
  const hasGenuinePreparationEvidence =
    Boolean(
      evidence.hasGenuineTestEvidence ||
      evidence.hasGenuineQbEvidence,
    );

  if (
    !hasGenuinePreparationEvidence
  ) {
    return {
      modelVersion:
        TMUA_PREPARATION_RANK_MODEL_VERSION,

      hasGenuinePreparationEvidence:
        false,

      actualPreparationScore:
        null,

      components: {
        performance: 0,
        breadth: 0,
        evidenceDepth: 0,
        recentActivity: 0,
        consistency: 0,
        recovery: 0,
      },
    };
  }

  const performance =
    preparationPerformance(
      evidence.predictedTmuaScore9,
    );

  const breadth =
    preparationBreadth({
      broadOrFullIndependentTestFamilies:
        evidence.broadOrFullIndependentTestFamilies,

      trustedCanonicalTopicCoverage:
        evidence.trustedCanonicalTopicCoverage,
    });

  const evidenceDepth =
    preparationEvidenceDepth({
      predictorTestWeight:
        evidence.predictorTestWeight,

      trustedUniqueFirstExposures:
        evidence.trustedUniqueFirstExposures,
    });

  const recentActivity =
    preparationRecentActivity({
      distinctCanonicalQbInteractions30d:
        evidence.distinctCanonicalQbInteractions30d,

      independentRecognisedTestFamilies30d:
        evidence.independentRecognisedTestFamilies30d,
    });

  const consistency =
    preparationConsistency({
      hasGenuinePreparationEvidence,
      testFamilySignals:
        evidence.testFamilySignals,
    });

  const recovery =
    preparationRecovery({
      hasGenuineQbEvidence:
        evidence.hasGenuineQbEvidence,

      recovery:
        evidence.recovery,
    });

  const actualPreparationScore =
    100 * (
      0.70 * performance +
      0.10 * breadth +
      0.08 * evidenceDepth +
      0.06 * recentActivity +
      0.03 * consistency +
      0.03 * recovery
    );

  return {
    modelVersion:
      TMUA_PREPARATION_RANK_MODEL_VERSION,

    hasGenuinePreparationEvidence:
      true,

    actualPreparationScore,

    components: {
      performance,
      breadth,
      evidenceDepth,
      recentActivity,
      consistency,
      recovery,
    },
  };
}

export function rankPreparationCohort(
  users: PreparationRankingInput[],
): PreparationRankingResult[] {
  const active =
    users.filter(
      (user) =>
        user.active,
    );

  const actualActiveCohortSize =
    active.length;

  const rankable =
    active
      .filter(
        (user) =>
          user.score.actualPreparationScore !=
          null,
      )
      .sort(
        (left, right) =>
          (
            right.score.actualPreparationScore as number
          ) -
          (
            left.score.actualPreparationScore as number
          ),
      );

  const ranks =
    new Map<
      string,
      number
    >();

  let previousScore:
    | number
    | null =
      null;

  let previousRank = 0;

  rankable.forEach(
    (user, index) => {
      const score =
        user.score.actualPreparationScore as number;

      const rank =
        previousScore !== null &&
        Object.is(
          score,
          previousScore,
        )
          ? previousRank
          : index + 1;

      ranks.set(
        user.userId,
        rank,
      );

      previousScore =
        score;

      previousRank =
        rank;
    },
  );

  return users.map(
    (user) => {
      const score =
        user.active
          ? user.score.actualPreparationScore
          : null;

      return {
        userId:
          user.userId,

        active:
          user.active,

        actualPreparationScore:
          score,

        actualPreparationRank:
          score == null
            ? null
            : (
                ranks.get(
                  user.userId,
                ) ?? null
              ),

        actualActiveCohortSize,
      };
    },
  );
}
