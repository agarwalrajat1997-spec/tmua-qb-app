import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import vm from "node:vm";

import {
  ESAT_CANONICAL_KEY_VERSION,
  ESAT_CANONICAL_TESTS,
} from "../lib/server/esat-canonical-tests.ts";
import {
  ESAT_TEST_PROFILES,
} from "../lib/server/esat-score-estimates.ts";
import {
  ESAT_OCTOBER_2026_SEEDS,
  ESAT_OCTOBER_2026_KEY_VERSION,
  estimateOctober2026EsatScores,
} from "../lib/server/esat-october-2026-tests.ts";

assert.equal(
  ESAT_CANONICAL_KEY_VERSION,
  "esat-canonical-keys-20260819-v1",
);
assert.equal(Object.keys(ESAT_CANONICAL_TESTS).length, 32);
assert.deepEqual(
  Object.keys(ESAT_CANONICAL_TESTS).filter((id) => !ESAT_OCTOBER_2026_SEEDS[id]).sort(),
  Object.keys(ESAT_TEST_PROFILES).sort(),
  "Existing calibrated ESAT profiles must retain exactly their original canonical coverage.",
);

for (const [testId, canonical] of Object.entries(ESAT_CANONICAL_TESTS)) {
  assert.equal(canonical.testId, testId);
  assert.equal(canonical.expectedQuestions, 81);
  assert.equal(canonical.answers.length, 81);
  const profile = ESAT_TEST_PROFILES[testId] ?? ESAT_OCTOBER_2026_SEEDS[testId];
  assert.deepEqual(canonical.modules, profile.modules);
  assert.ok(canonical.answers.every((answer) => /^[A-H]$/.test(answer)));

  const source = readFileSync(resolve(canonical.sourceFile), "utf8");
  const embeddedData = source.match(/<script\b[^>]*id="test-data"[^>]*>([\s\S]*?)<\/script>/)?.[1];
  const sourceData = embeddedData ? JSON.parse(embeddedData) : null;
  const sourceId = sourceData?.id ?? source.match(/const testId\s*=\s*"([^"]+)"/)?.[1];
  const answerLiteral = source.match(
    /const correctAnswers\s*=\s*(\[[\s\S]*?\]);/,
  )?.[1];

  assert.equal(sourceId, testId, `${canonical.sourceFile} testId mismatch`);
  assert.ok(answerLiteral || sourceData, `${canonical.sourceFile} has no answer key`);

  const sourceAnswers = sourceData
    ? sourceData.modules.flatMap((module) => module.questions.map((q) => q.correctAnswer))
    : [...vm.runInNewContext(answerLiteral)];
  assert.deepEqual(
    sourceAnswers,
    [...canonical.answers],
    `${testId} server key differs from the deployed paper`,
  );

  const sourceHash = createHash("sha256")
    .update(JSON.stringify(sourceAnswers), "utf8")
    .digest("hex");

  assert.equal(
    canonical.canonicalSha256,
    sourceHash,
    `${testId} canonical provenance hash mismatch`,
  );
}

const thresholds = {
  "Mathematics 1": [[13,4.5],[14,5],[17,6],[20,7],[23,8],[26,9],[27,9]],
  "Mathematics 2": [[11,4.5],[12,5],[15,6],[18,7],[22,8],[25,9],[26,9],[27,9]],
  Physics: [[15,4.5],[16,5],[19,6],[22,7],[24,8],[27,9]],
  Chemistry: [[16,4.5],[17,5],[20,6],[23,7],[25,8],[27,9]],
  Biology: [[18,4.5],[19,5],[22,6],[24,7],[26,8],[27,9]],
};
for (const [testId, seed] of Object.entries(ESAT_OCTOBER_2026_SEEDS)) {
  assert.equal(ESAT_CANONICAL_TESTS[testId].keyVersion, ESAT_OCTOBER_2026_KEY_VERSION);
  assert.equal(ESAT_TEST_PROFILES[testId], undefined, "Provisional papers must retain their separate conversion tables.");
  for (const [index, module] of seed.modules.entries()) {
    for (const [raw, expected] of thresholds[module]) {
      const marks = [0, 0, 0]; marks[index] = raw;
      const estimate = estimateOctober2026EsatScores(testId, marks);
      assert.equal(estimate.modules[index].estimatedScore, expected, `${testId} ${module} ${raw}/27`);
      assert.equal(estimate.rawTotal, raw);
      assert.equal(estimate.status, "provisional_uncalibrated");
      assert.equal(estimate.predictorEligible, true);
      assert.equal(estimate.predictedCombinedPracticeScore, Math.round((expected + 2) / 3 * 10) / 10);
      assert.equal(estimate.averageModuleEstimate, estimate.predictedCombinedPracticeScore);
      assert.equal(estimate.combinedScoreOfficial, false);
    }
  }
  assert.throws(() => estimateOctober2026EsatScores(testId, [1, 2]));
  assert.throws(() => estimateOctober2026EsatScores(testId, [1, -1, 2]));
  assert.throws(() => estimateOctober2026EsatScores(testId, [1, 28, 2]));
}
assert.equal(estimateOctober2026EsatScores("esat-mock-01", [1,2,3]), null);

console.log(
  "ESAT canonical-key verification passed: 32 full papers and 2,592 source answers match; the six October papers retain separate provisional module scores and contribute their mean to the dashboard without changing legacy calibration.",
);
