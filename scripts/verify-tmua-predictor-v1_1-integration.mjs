import fs from "node:fs";

import {
  applyTmuaHighScoreEvidenceGate,
} from "../lib/server/tmua-predictor-v1_1-policy.ts";

const route =
  fs.readFileSync(
    "app/api/tmua/overview/route.ts",
    "utf8",
  );

const pkg =
  JSON.parse(
    fs.readFileSync(
      "package.json",
      "utf8",
    ),
  );

let checks = 0;

function assert(
  condition,
  message,
) {
  checks += 1;

  if (!condition) {
    throw new Error(message);
  }
}

function countMatches(
  source,
  pattern,
) {
  return (
    source.match(pattern) ?? []
  ).length;
}

function routeChecks(
  source,
) {
  return {
    currentV11:
      /const\s+rawPredictorResult\s*=\s*calculateTmuaPredictorV1\s*\([\s\S]*?\)\s*;\s*const\s+result\s*=\s*applyTmuaHighScoreEvidenceGate\s*\(\s*rawPredictorResult\s*,?\s*\)\s*;/.test(
        source,
      ),

    cohortV11:
      /const\s+rawPredictorForRank\s*=\s*calculateTmuaPredictorV1\s*\([\s\S]*?\)\s*;\s*const\s+predictor\s*=\s*applyTmuaHighScoreEvidenceGate\s*\(\s*rawPredictorForRank\s*,?\s*\)\s*;\s*const\s+predictorSnapshot\s*=\s*buildTmuaPredictionSnapshotInsert/.test(
        source,
      ),

    modelGuard:
      /predictor\.modelVersion\s*!==\s*currentPredictorResult\.modelVersion/.test(
        source,
      ),

    hashGuard:
      /predictorSnapshot\.inputHash\s*!==\s*currentPredictorSnapshot\.inputHash/.test(
        source,
      ),

    scoreGuard:
      /predictor\.predictedTmuaScore9\s*!==\s*currentPredictorResult\.predictedTmuaScore9/.test(
        source,
      ),
  };
}

assert(
  route.includes(
    'import { applyTmuaHighScoreEvidenceGate } from "@/lib/server/tmua-predictor-v1_1-policy";',
  ),
  "Overview must import the V1.1 high-score gate.",
);

assert(
  countMatches(
    route,
    /applyTmuaHighScoreEvidenceGate\s*\(/g,
  ) === 2,
  "Overview must apply V1.1 exactly twice: current user and Preparation Rank cohort.",
);

const liveChecks =
  routeChecks(route);

assert(
  liveChecks.currentV11,
  "Current-user Predictor must flow through V1 then V1.1.",
);

assert(
  liveChecks.cohortV11,
  "Preparation Rank cohort Predictor must flow through V1 then V1.1 before snapshot/ranking.",
);

assert(
  liveChecks.modelGuard,
  "Preparation Rank must fail closed if current-user Predictor model versions differ.",
);

assert(
  liveChecks.hashGuard,
  "Preparation Rank must fail closed if current-user V1.1 input hashes differ.",
);

assert(
  liveChecks.scoreGuard,
  "Preparation Rank must fail closed if current-user V1.1 scores differ.",
);

/*
  Regression against the exact failure that blocked the previous
  Vercel candidate: the structural assertions must behave the same
  under LF and CRLF checkouts.
*/
const crlfRoute =
  route
    .replace(/\r\n/g, "\n")
    .replace(/\n/g, "\r\n");

const crlfChecks =
  routeChecks(crlfRoute);

assert(
  JSON.stringify(crlfChecks) ===
    JSON.stringify(liveChecks),
  "V1.1 integration verification must be invariant to LF/CRLF line endings.",
);

assert(
  route.includes(
    "Preparation Rank current-user Predictor input does not match overview Predictor input",
  ),
  "Runtime V1.1 hash mismatch error must remain explicit.",
);

assert(
  route.includes(
    "Preparation Rank current-user Predictor score does not match overview Predictor score",
  ),
  "Runtime V1.1 score mismatch error must remain explicit.",
);

assert(
  route.includes(
    "Preparation Rank current-user Predictor model version does not match overview Predictor model version",
  ),
  "Runtime V1.1 model-version mismatch error must remain explicit.",
);

/*
  Determinism regression: when current-user overview and
  Preparation Rank receive the same raw Predictor evidence result,
  V1.1 must produce exactly the same model identity, input hash and
  score in both call sites.
*/
const rawFixture = {
  modelVersion:
    "tmua-predictor-v1.0.0",

  inputHash:
    "4".repeat(64),

  predictionStatus:
    "predicted",

  predictedTmuaScore9:
    8.4,

  lowerBound:
    7.5,

  upperBound:
    8.8,

  testSignalScore9:
    8.4,

  independentTestCount:
    3,

  combinedFullCount:
    2,

  qbWeight:
    0.5,

  evidenceDetails: {},
};

const currentUserV11 =
  applyTmuaHighScoreEvidenceGate({
    ...rawFixture,
  });

const preparationRankV11 =
  applyTmuaHighScoreEvidenceGate({
    ...rawFixture,
  });

assert(
  currentUserV11.modelVersion ===
    preparationRankV11.modelVersion,
  "Current-user and Preparation Rank V1.1 model versions must be identical for identical evidence.",
);

assert(
  currentUserV11.inputHash ===
    preparationRankV11.inputHash,
  "Current-user V1.1 hash must equal the hash used inside Preparation Rank for identical evidence.",
);

assert(
  currentUserV11.predictedTmuaScore9 ===
    preparationRankV11.predictedTmuaScore9,
  "Current-user V1.1 score must equal the score used inside Preparation Rank for identical evidence.",
);

assert(
  pkg.scripts?.[
    "verify:tmua-predictor-v1_1-policy"
  ] ===
    "node scripts/verify-tmua-predictor-v1_1-policy.mjs",
  "V1.1 policy verifier package script is missing.",
);

assert(
  pkg.scripts?.[
    "verify:tmua-predictor-v1_1-integration"
  ] ===
    "node scripts/verify-tmua-predictor-v1_1-integration.mjs",
  "V1.1 integration verifier package script is missing.",
);

assert(
  typeof pkg.scripts?.prebuild ===
    "string" &&
    pkg.scripts.prebuild.includes(
      "npm run verify:tmua-predictor-v1_1-policy",
    ),
  "V1.1 policy verifier must run in prebuild.",
);

assert(
  typeof pkg.scripts?.prebuild ===
    "string" &&
    pkg.scripts.prebuild.includes(
      "npm run verify:tmua-predictor-v1_1-integration",
    ),
  "V1.1 integration verifier must run in prebuild.",
);

assert(
  pkg.scripts.prebuild.indexOf(
    "npm run verify:tmua-predictor-v1_1-policy",
  ) <
    pkg.scripts.prebuild.indexOf(
      "npm run verify:tmua-predictor-v1_1-integration",
    ),
  "V1.1 policy verifier must run before V1.1 integration verifier.",
);

console.log(
  "TMUA Predictor V1.1 / Preparation Rank integration verification passed:",
);

console.log(
  String(checks) +
    " invariants verified; current-user and cohort predictors both use V1.1; " +
    "model version, input hash and score are fail-closed equal for the current user; " +
    "identical evidence produces identical V1.1 hash/score in both paths; " +
    "LF and CRLF checkouts are both protected; " +
    "the V1.1 policy and integration checks are protected by prebuild.",
);