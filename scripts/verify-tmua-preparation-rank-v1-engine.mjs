import assert from "node:assert/strict";

import {
  calculatePreparationScore,
  preparationBreadth,
  preparationConsistency,
  preparationEvidenceDepth,
  preparationPerformance,
  preparationRecentActivity,
  preparationRecovery,
  rankPreparationCohort,
  weightedPopulationSd,
} from "../lib/server/tmua-preparation-rank-v1-engine.ts";

let checks = 0;

function check(
  condition,
  message,
) {
  checks += 1;
  assert.ok(
    condition,
    message,
  );
}

function equal(
  actual,
  expected,
  message,
) {
  checks += 1;
  assert.equal(
    actual,
    expected,
    message,
  );
}

function approx(
  actual,
  expected,
  message,
  tolerance = 1e-9,
) {
  checks += 1;

  assert.ok(
    Number.isFinite(actual) &&
      Math.abs(
        actual - expected,
      ) <= tolerance,
    `${message}: expected ${expected}, got ${actual}`,
  );
}

approx(
  preparationPerformance(1),
  0,
  "TMUA 1 gives zero performance",
);

approx(
  preparationPerformance(5),
  0.5,
  "TMUA 5 gives half performance",
);

approx(
  preparationPerformance(9),
  1,
  "TMUA 9 gives full performance",
);

approx(
  preparationPerformance(null),
  0,
  "missing prediction gives zero performance",
);

approx(
  preparationBreadth({
    broadOrFullIndependentTestFamilies: 1,
    trustedCanonicalTopicCoverage: 0.5,
  }),
  0.75,
  "breadth combines complementary evidence",
);

approx(
  preparationBreadth({
    broadOrFullIndependentTestFamilies: 2,
    trustedCanonicalTopicCoverage: 0,
  }),
  1,
  "two broad families saturate test breadth",
);

approx(
  preparationEvidenceDepth({
    predictorTestWeight: 1,
    trustedUniqueFirstExposures: 75,
  }),
  0.75,
  "depth combines test and QB evidence",
);

approx(
  preparationEvidenceDepth({
    predictorTestWeight: 2,
    trustedUniqueFirstExposures: 0,
  }),
  1,
  "test depth saturates at two",
);

approx(
  preparationEvidenceDepth({
    predictorTestWeight: 0,
    trustedUniqueFirstExposures: 150,
  }),
  1,
  "QB depth saturates at 150",
);

approx(
  preparationRecentActivity({
    distinctCanonicalQbInteractions30d: 30,
    independentRecognisedTestFamilies30d: 1,
  }),
  0.5,
  "half QB and test activity gives half activity",
);

approx(
  preparationRecentActivity({
    distinctCanonicalQbInteractions30d: 60,
    independentRecognisedTestFamilies30d: 2,
  }),
  1,
  "activity saturates at one",
);

approx(
  weightedPopulationSd([
    {
      score9: 5,
      weight: 1,
    },
    {
      score9: 5,
      weight: 1,
    },
  ]),
  0,
  "identical family scores have zero SD",
);

approx(
  weightedPopulationSd([
    {
      score9: 4,
      weight: 1,
    },
    {
      score9: 6,
      weight: 1,
    },
  ]),
  1,
  "4 and 6 equally weighted have population SD one",
);

approx(
  weightedPopulationSd([
    {
      score9: 4,
      weight: 1,
    },
    {
      score9: 6,
      weight: 3,
    },
  ]),
  Math.sqrt(0.75),
  "weighted population SD is deterministic",
);

equal(
  weightedPopulationSd([
    {
      score9: 5,
      weight: 1,
    },
  ]),
  null,
  "one family has no SD",
);

approx(
  preparationConsistency({
    hasGenuinePreparationEvidence: false,
    testFamilySignals: [],
  }),
  0,
  "zero evidence gets no consistency",
);

approx(
  preparationConsistency({
    hasGenuinePreparationEvidence: true,
    testFamilySignals: [],
  }),
  0.5,
  "genuine evidence with fewer than two families is neutral",
);

approx(
  preparationConsistency({
    hasGenuinePreparationEvidence: true,
    testFamilySignals: [
      {
        score9: 5,
        weight: 1,
      },
      {
        score9: 5,
        weight: 1,
      },
    ],
  }),
  1,
  "consistent family scores get maximum consistency",
);

approx(
  preparationRecovery({
    hasGenuineQbEvidence: false,
    recovery: null,
  }),
  0,
  "no QB evidence gets zero recovery",
);

approx(
  preparationRecovery({
    hasGenuineQbEvidence: true,
    recovery: null,
  }),
  0.5,
  "QB evidence without opportunity gets neutral recovery",
);

approx(
  preparationRecovery({
    hasGenuineQbEvidence: true,
    recovery: 0.8,
  }),
  0.8,
  "trusted recovery passes through",
);

const noEvidence =
  calculatePreparationScore({
    predictedTmuaScore9: null,
    broadOrFullIndependentTestFamilies: 0,
    predictorTestWeight: 0,
    trustedUniqueFirstExposures: 0,
    trustedCanonicalTopicCoverage: 0,
    distinctCanonicalQbInteractions30d: 60,
    independentRecognisedTestFamilies30d: 0,
    testFamilySignals: [],
    hasGenuineTestEvidence: false,
    hasGenuineQbEvidence: false,
    recovery: null,
  });

equal(
  noEvidence.actualPreparationScore,
  null,
  "login/activity-only user has no Preparation Score",
);

equal(
  noEvidence.hasGenuinePreparationEvidence,
  false,
  "login-only user has no genuine preparation evidence",
);

const qbOnlyBelowPredictor =
  calculatePreparationScore({
    predictedTmuaScore9: null,
    broadOrFullIndependentTestFamilies: 0,
    predictorTestWeight: 0,
    trustedUniqueFirstExposures: 20,
    trustedCanonicalTopicCoverage: 0.25,
    distinctCanonicalQbInteractions30d: 20,
    independentRecognisedTestFamilies30d: 0,
    testFamilySignals: [],
    hasGenuineTestEvidence: false,
    hasGenuineQbEvidence: true,
    recovery: null,
  });

check(
  qbOnlyBelowPredictor.actualPreparationScore !== null,
  "trusted QB evidence can create Preparation Score before Predictor activation",
);

check(
  qbOnlyBelowPredictor.actualPreparationScore > 0,
  "QB evidence creates positive preparation progress",
);

check(
  qbOnlyBelowPredictor.actualPreparationScore < 20,
  "small QB evidence cannot create a large Preparation Score",
);

const balanced =
  calculatePreparationScore({
    predictedTmuaScore9: 5,
    broadOrFullIndependentTestFamilies: 1,
    predictorTestWeight: 1,
    trustedUniqueFirstExposures: 75,
    trustedCanonicalTopicCoverage: 0.5,
    distinctCanonicalQbInteractions30d: 30,
    independentRecognisedTestFamilies30d: 1,
    testFamilySignals: [
      {
        score9: 5,
        weight: 1,
      },
    ],
    hasGenuineTestEvidence: true,
    hasGenuineQbEvidence: true,
    recovery: 0.8,
  });

approx(
  balanced.actualPreparationScore,
  55.4,
  "locked balanced fixture score",
);

const cohort =
  rankPreparationCohort([
    {
      userId: "a",
      active: true,
      score: {
        ...balanced,
        actualPreparationScore: 80.0001,
      },
    },
    {
      userId: "b",
      active: true,
      score: {
        ...balanced,
        actualPreparationScore: 80,
      },
    },
    {
      userId: "c",
      active: true,
      score: {
        ...balanced,
        actualPreparationScore: 80,
      },
    },
    {
      userId: "d",
      active: true,
      score: {
        ...balanced,
        actualPreparationScore: 79.9999,
      },
    },
    {
      userId: "login-only",
      active: true,
      score: noEvidence,
    },
    {
      userId: "inactive",
      active: false,
      score: {
        ...balanced,
        actualPreparationScore: 99,
      },
    },
  ]);

const byId =
  new Map(
    cohort.map(
      (row) => [
        row.userId,
        row,
      ],
    ),
  );

equal(
  byId.get("a").actualPreparationRank,
  1,
  "top active rank",
);

equal(
  byId.get("b").actualPreparationRank,
  2,
  "first tied rank",
);

equal(
  byId.get("c").actualPreparationRank,
  2,
  "second tied rank",
);

equal(
  byId.get("d").actualPreparationRank,
  4,
  "competition tie skips rank three",
);

equal(
  byId.get("login-only").actualPreparationRank,
  null,
  "login-only active user gets no rank",
);

equal(
  byId.get("inactive").actualPreparationRank,
  null,
  "inactive user gets no rank",
);

equal(
  byId.get("a").actualActiveCohortSize,
  5,
  "denominator counts every active user including login-only",
);

equal(
  byId.get("login-only").actualActiveCohortSize,
  5,
  "login-only user remains in active denominator",
);

check(
  byId.get("a").actualPreparationRank !==
    byId.get("b").actualPreparationRank,
  "scores that only round to same display value do not tie",
);

let negativeRejected = false;

try {
  preparationRecentActivity({
    distinctCanonicalQbInteractions30d: -1,
    independentRecognisedTestFamilies30d: 0,
  });
} catch {
  negativeRejected = true;
}

equal(
  negativeRejected,
  true,
  "negative evidence counts fail closed",
);

let invalidWeightRejected = false;

try {
  weightedPopulationSd([
    {
      score9: 5,
      weight: -1,
    },
    {
      score9: 6,
      weight: 1,
    },
  ]);
} catch {
  invalidWeightRejected = true;
}

equal(
  invalidWeightRejected,
  true,
  "negative family weights fail closed",
);

console.log(
  "TMUA Preparation Rank V1 engine verification passed:",
);

console.log(
  `${checks} invariants/fixtures verified; ` +
  "the engine is pure and database-independent; " +
  "weights remain 70/10/8/6/3/3; " +
  "missing Predictor score creates no fake baseline; " +
  "activity alone creates no Preparation Score; " +
  "weighted population SD drives consistency; " +
  "rank uses unrounded scores with competition ties; " +
  "login-only active users count in the denominator but receive no rank.",
);
