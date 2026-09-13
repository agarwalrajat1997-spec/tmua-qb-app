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

assert.equal(
  ESAT_CANONICAL_KEY_VERSION,
  "esat-canonical-keys-20260819-v1",
);
assert.equal(Object.keys(ESAT_CANONICAL_TESTS).length, 26);
assert.deepEqual(
  Object.keys(ESAT_CANONICAL_TESTS).sort(),
  Object.keys(ESAT_TEST_PROFILES).sort(),
  "Canonical server keys and calibrated ESAT profiles must cover the same papers.",
);

for (const [testId, canonical] of Object.entries(ESAT_CANONICAL_TESTS)) {
  assert.equal(canonical.testId, testId);
  assert.equal(canonical.expectedQuestions, 81);
  assert.equal(canonical.answers.length, 81);
  assert.deepEqual(canonical.modules, ESAT_TEST_PROFILES[testId].modules);
  assert.ok(canonical.answers.every((answer) => /^[A-H]$/.test(answer)));

  const source = readFileSync(resolve(canonical.sourceFile), "utf8");
  const sourceId = source.match(/const testId\s*=\s*"([^"]+)"/)?.[1];
  const answerLiteral = source.match(
    /const correctAnswers\s*=\s*(\[[\s\S]*?\]);/,
  )?.[1];

  assert.equal(sourceId, testId, `${canonical.sourceFile} testId mismatch`);
  assert.ok(answerLiteral, `${canonical.sourceFile} has no answer key`);

  const sourceAnswers = [...vm.runInNewContext(answerLiteral)];
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

console.log(
  "ESAT canonical-key verification passed: 26 full papers and 2,106 answers match their source HTML exactly.",
);
