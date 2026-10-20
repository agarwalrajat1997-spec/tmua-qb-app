import fs from "node:fs";

import {
  applyTmuaHighScoreEvidenceGate,
} from "../lib/server/tmua-predictor-v1_1-policy.ts";

const route =
  fs.readFileSync(
    "app/api/tmua/overview/route.ts",
    "utf8",
  );

const refresh = fs.readFileSync(
  "lib/server/tmua-preparation-rank-refresh.ts", "utf8",
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
  cohort,
) {
  return {
    currentV11:
      /const\s+rawPredictorResult\s*=\s*calculateTmuaPredictorV1\s*\([\s\S]*?\)\s*;\s*const\s+result\s*=\s*applyTmuaHighScoreEvidenceGate\s*\(\s*rawPredictorResult\s*,?\s*\)\s*;/.test(
        source,
      ),

    cohortV11:
      /const\s+rawPredictorForRank\s*=\s*calculateTmuaPredictorV1\s*\([\s\S]*?\)\s*;\s*const\s+predictor\s*=\s*applyTmuaHighScoreEvidenceGate\s*\(\s*rawPredictorForRank\s*,?\s*\)\s*;\s*const\s+predictorSnapshot\s*=\s*buildTmuaPredictionSnapshotInsert/.test(
        cohort,
      ),

    modelGuard:
      /buildTmuaPredictionSnapshotInsert\s*\(\s*userId\s*,\s*predictor\s*,\s*asOfIso\s*,?\s*\)/.test(
        cohort,
      ),

    hashGuard:
      /predictor_input_hash\s*:\s*record\s*\.predictorSnapshot\s*\.inputHash/.test(
        cohort,
      ),

    scoreGuard:
      /predicted_tmua_score9\s*:\s*record\.predictor\s*\.predictedTmuaScore9/.test(
        cohort,
      ),
  };
}

assert(
  [route, refresh].every(source => source.includes(
    'import { applyTmuaHighScoreEvidenceGate } from "@/lib/server/tmua-predictor-v1_1-policy";',
  )),
  "Overview and background cohort worker must import the same V1.1 high-score gate.",
);

assert(
  [route, refresh].every(source => countMatches(
    source,
    /applyTmuaHighScoreEvidenceGate\s*\(/g,
  ) === 1),
  "Each path must apply V1.1 exactly once: current-user overview and background Preparation Rank cohort.",
);

const liveChecks =
  routeChecks(route, refresh);

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
  "Preparation Rank must build its model identity through the same protected snapshot mapper and gated result.",
);

assert(
  liveChecks.hashGuard,
  "Preparation Rank must persist the exact V1.1 predictor snapshot input hash.",
);

assert(
  liveChecks.scoreGuard,
  "Preparation Rank must persist the exact V1.1 predictor score.",
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
  routeChecks(crlfRoute, refresh.replace(/\r\n/g, "\n").replace(/\n/g, "\r\n"));

assert(
  JSON.stringify(crlfChecks) ===
    JSON.stringify(liveChecks),
  "V1.1 integration verification must be invariant to LF/CRLF line endings.",
);

assert(
  route.includes('readPreparationRankSnapshot(admin, user.id, "tmua", user.email)'),
  "Current-user route must return only its verified identity's complete saved cohort snapshot.",
);

assert(
  refresh.includes("Preparation Rank run is missing an active-user snapshot"),
  "Background cohort publication must fail closed if any active student's snapshot is missing.",
);

assert(
  !route.includes("rankPreparationCohort") && !route.includes("listUsers"),
  "Student overview must never rebuild the cohort while serving its own predictor.",
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
    "cohort snapshots preserve the gated model identity, input hash and score; " +
    "identical evidence produces identical V1.1 hash/score in both paths; " +
    "LF and CRLF checkouts are both protected; " +
    "the V1.1 policy and integration checks are protected by prebuild.",
);
