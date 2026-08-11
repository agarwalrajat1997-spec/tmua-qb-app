import assert from "node:assert/strict";

import {
  applyTmuaHighScoreEvidenceGate,
  TMUA_PREDICTOR_V11_MODEL_VERSION,
} from "../lib/server/tmua-predictor-v1_1-policy.ts";

function base(overrides = {}) {
  return {
    modelVersion:
      "tmua-predictor-v1.0.0",

    inputHash:
      "0".repeat(64),

    predictionStatus:
      "predicted",

    predictedTmuaScore9:
      7,

    lowerBound:
      5.8,

    upperBound:
      8.2,

    testSignalScore9:
      7,

    independentTestCount:
      1,

    combinedFullCount:
      0,

    qbWeight:
      0,

    evidenceDetails: {},

    ...overrides,
  };
}

const qbOnly =
  applyTmuaHighScoreEvidenceGate(
    base({
      predictedTmuaScore9: 8.5,
      testSignalScore9: null,
      independentTestCount: 0,
      combinedFullCount: 0,
      qbWeight: 1,
    }),
  );

assert.equal(
  qbOnly.predictedTmuaScore9,
  6.25,
);

const oneTest =
  applyTmuaHighScoreEvidenceGate(
    base({
      predictedTmuaScore9: 8.25,
      testSignalScore9: 8.25,
      independentTestCount: 1,
      combinedFullCount: 0,
    }),
  );

assert.equal(
  oneTest.predictedTmuaScore9,
  6.75,
);

const twoNoFull =
  applyTmuaHighScoreEvidenceGate(
    base({
      predictedTmuaScore9: 8.34,
      testSignalScore9: 8.34,
      independentTestCount: 2,
      combinedFullCount: 0,
    }),
  );

assert.equal(
  twoNoFull.predictedTmuaScore9,
  6.95,
);

const twoWithFull =
  applyTmuaHighScoreEvidenceGate(
    base({
      predictedTmuaScore9: 7.6,
      testSignalScore9: 7.4,
      independentTestCount: 2,
      combinedFullCount: 1,
    }),
  );

assert.equal(
  twoWithFull.predictedTmuaScore9,
  7.6,
);

const threePapers =
  applyTmuaHighScoreEvidenceGate(
    base({
      predictedTmuaScore9: 7.7,
      testSignalScore9: 7.6,
      independentTestCount: 3,
      combinedFullCount: 0,
    }),
  );

assert.equal(
  threePapers.predictedTmuaScore9,
  7.7,
);

const notEnoughForEight =
  applyTmuaHighScoreEvidenceGate(
    base({
      predictedTmuaScore9: 8.4,
      testSignalScore9: 8.4,
      independentTestCount: 3,
      combinedFullCount: 1,
    }),
  );

assert.equal(
  notEnoughForEight.predictedTmuaScore9,
  8,
);

const enoughForEight =
  applyTmuaHighScoreEvidenceGate(
    base({
      predictedTmuaScore9: 8.4,
      testSignalScore9: 8.4,
      independentTestCount: 3,
      combinedFullCount: 2,
    }),
  );

assert.equal(
  enoughForEight.predictedTmuaScore9,
  8.4,
);

const qbBoost =
  applyTmuaHighScoreEvidenceGate(
    base({
      predictedTmuaScore9: 7.9,
      testSignalScore9: 7.2,
      independentTestCount: 3,
      combinedFullCount: 2,
      qbWeight: 0.8,
    }),
  );

assert.equal(
  qbBoost.predictedTmuaScore9,
  7.45,
);

const qbCannotPullUp =
  applyTmuaHighScoreEvidenceGate(
    base({
      predictedTmuaScore9: 6.5,
      testSignalScore9: 7.5,
      independentTestCount: 3,
      combinedFullCount: 2,
      qbWeight: 1,
    }),
  );

assert.equal(
  qbCannotPullUp.predictedTmuaScore9,
  6.5,
);

const insufficient =
  applyTmuaHighScoreEvidenceGate(
    base({
      predictionStatus:
        "insufficient_evidence",
      predictedTmuaScore9: null,
      lowerBound: null,
      upperBound: null,
      testSignalScore9: null,
      independentTestCount: 0,
      combinedFullCount: 0,
    }),
  );

assert.equal(
  insufficient.predictedTmuaScore9,
  null,
);

assert.equal(
  oneTest.modelVersion,
  TMUA_PREDICTOR_V11_MODEL_VERSION,
);

assert.match(
  oneTest.inputHash,
  /^[0-9a-f]{64}$/,
);

assert.notEqual(
  oneTest.inputHash,
  "0".repeat(64),
);

console.log(
  "TMUA Predictor V1.1 high-score evidence policy verification passed:",
);

console.log(
  "QB-only <= 6.25; one test <= 6.75; two tests without a full <= 6.95; " +
  "7+ requires repeated strong test evidence; 8+ requires 3 families + 2 full tests; " +
  "QB upward contribution is capped at +0.25 from demonstrated test signal.",
);