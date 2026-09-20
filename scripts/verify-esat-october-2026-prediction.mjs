import assert from "node:assert/strict";

import { getCanonicalEsatTest } from "../lib/server/esat-canonical-tests.ts";
import { buildEsatTestEvidence } from "../lib/server/esat-predictor-evidence.ts";
import { calculateEsatPredictorV1 } from "../lib/server/esat-predictor-v1-engine.ts";
import {
  ESAT_OCTOBER_2026_SEEDS,
  estimateOctober2026EsatScores,
  getEsatPredictorFamilyId,
} from "../lib/server/esat-october-2026-tests.ts";
import { estimateEsatTestScores } from "../lib/server/esat-score-estimates.ts";

// Uses saved-row shaped fixtures and canonical keys only. No database, network,
// browser, or email access is involved in this regression gate.
const octoberIds = Object.keys(ESAT_OCTOBER_2026_SEEDS);
const activeTopics = ["Algebra", "Biology", "Chemistry", "Physics"];
const thresholds = {
  "Mathematics 1": { "4.5": 13, "5": 14, "7": 20, "9": 27 },
  "Mathematics 2": { "4.5": 11, "5": 12, "7": 18, "9": 27 },
  Physics: { "4.5": 15, "5": 16, "7": 22, "9": 27 },
  Chemistry: { "4.5": 16, "5": 17, "7": 23, "9": 27 },
  Biology: { "4.5": 18, "5": 19, "7": 24, "9": 27 },
};

function marksFor(testId, score) {
  return getCanonicalEsatTest(testId).modules.map(
    (module) => thresholds[module][String(score)],
  );
}

function row(testId, marks, day = 1, attemptNumber = 1, extra = {}) {
  const canonical = getCanonicalEsatTest(testId);
  assert.ok(canonical);
  const answers = canonical.answers.map((answer, index) =>
    index % 27 < marks[Math.floor(index / 27)] ? answer : null,
  );
  return {
    id: `${testId}-day${day}-attempt${attemptNumber}`,
    test_id: testId,
    submitted_at: `2026-09-${String(day).padStart(2, "0")}T12:00:00.000Z`,
    attempt_number: attemptNumber,
    total_questions: 81,
    answers,
    // Deliberately forged historical summary/key values. Neither is authority.
    score: 81,
    correct_answers: Array(81).fill("A"),
    predictor_metadata: {
      esat_predictor_eligible: false,
      esat_predicted_combined_practice_score: 9,
      esat_score_status: "provisional_uncalibrated",
    },
    ...extra,
  };
}

function predict(savedRows) {
  return calculateEsatPredictorV1({
    testAttempts: buildEsatTestEvidence(savedRows),
    qbEvents: [],
    activeTopics,
  });
}

assert.equal(octoberIds.length, 6);
const sharedFamily = getEsatPredictorFamilyId(octoberIds[0]);
assert.ok(sharedFamily);
assert.notEqual(sharedFamily, octoberIds[0]);
assert.equal(getEsatPredictorFamilyId("esat-mock-01"), "esat-mock-01");

for (const testId of octoberIds) {
  assert.equal(getEsatPredictorFamilyId(testId), sharedFamily);
  const marks = marksFor(testId, 7);
  const saved = row(testId, marks);
  const evidence = buildEsatTestEvidence([saved]);
  assert.equal(evidence.length, 1, `${testId} must contribute`);
  assert.equal(evidence[0].testId, sharedFamily);
  assert.equal(evidence[0].attemptId, saved.id);
  assert.equal(evidence[0].attemptNumber, null,
    "Per-pathway attempt numbers must not override cross-pathway chronology.");
  assert.equal(evidence[0].effectiveWeight, 1.5);
  assert.equal(evidence[0].predictorEligible, true);
  assert.equal(evidence[0].predictedCombinedPracticeScore, 7,
    "Re-score canonical answers, not row.score, client key, or old metadata.");
  assert.equal(saved.predictor_metadata.esat_predictor_eligible, false,
    "Reading historical evidence must not mutate stored-row fixtures.");

  const estimate = estimateOctober2026EsatScores(testId, marks);
  assert.deepEqual(estimate.modules.map((m) => m.estimatedScore), [7, 7, 7]);
  assert.equal(estimate.predictorEligible, true);
  assert.equal(estimate.predictedCombinedPracticeScore, 7);
  assert.equal(estimate.combinedScoreOfficial, false);
  const prediction = predict([saved]);
  assert.equal(prediction.predictionStatus, "predicted");
  assert.equal(prediction.independentTestCount, 1);
  assert.equal(prediction.combinedFullCount, 1);
  assert.equal(prediction.testWeight, 1.5);
  assert.equal(prediction.confidence, "low");
  assert.equal(prediction.testSignalPracticeScore, 7);
  assert.equal(prediction.predictedEsatPracticeScore, 6.75,
    "New papers retain the existing one-independent-paper high-score ceiling.");

  // Null responses are valid blank answers, not missing question evidence.
  const blank = buildEsatTestEvidence([row(testId, [0, 0, 0])]);
  assert.equal(blank.length, 1);
  assert.equal(blank[0].predictedCombinedPracticeScore, 1);
}

const canonicalFixture = row(octoberIds[0], marksFor(octoberIds[0], 5));
const invalidRows = [
  { ...canonicalFixture, test_id: "esat-not-a-published-test" },
  { ...canonicalFixture, answers: canonicalFixture.answers.slice(0, 80) },
  { ...canonicalFixture, answers: [...canonicalFixture.answers, "A"] },
  { ...canonicalFixture, answers: null },
  { ...canonicalFixture, submitted_at: "not-a-date" },
  { ...canonicalFixture, submitted_at: "" },
];
assert.deepEqual(buildEsatTestEvidence(invalidRows), [],
  "Unknown tests, malformed answer counts and invalid dates fail closed.");

const engineId = "esat-october-2026-engineering";
const alternateId = "esat-october-2026-physics-chemistry";
const chronologicalRows = [
  row(engineId, marksFor(engineId, 4.5), 1, 1),
  row(engineId, marksFor(engineId, 9), 2, 2),
  row(alternateId, marksFor(alternateId, 5), 3, 1),
];
const retakes = predict(chronologicalRows);
assert.equal(retakes.independentTestCount, 1);
assert.equal(retakes.combinedFullCount, 1);
assert.equal(retakes.testEvidenceCount, 3);
assert.equal(retakes.testWeight, 1.5);
assert.equal(retakes.diagnostics.testFamilies[0].signal, 4.625,
  "First 4.5 at 75% + chronologically latest 5.0 at 25%; ignore middle 9.0.");
assert.equal(predict([...chronologicalRows].reverse()).inputHash, retakes.inputHash,
  "Database row order must not change the evidence family or its signal.");

const sixStrong = predict(octoberIds.map((testId, index) =>
  row(testId, [27, 27, 27], index + 1),
));
assert.equal(sixStrong.testEvidenceCount, 6);
assert.equal(sixStrong.independentTestCount, 1);
assert.equal(sixStrong.combinedFullCount, 1);
assert.equal(sixStrong.testWeight, 1.5);
assert.equal(sixStrong.confidence, "low");
assert.equal(sixStrong.predictedEsatPracticeScore, 6.75,
  "Reused pathway modules must not manufacture six independent high-score papers.");

const legacyId = "esat-mock-01";
const legacyMarks = [13, 14, 15];
const legacyRow = row(legacyId, legacyMarks, 5, 2);
const legacyScore = estimateEsatTestScores(legacyId, legacyMarks)
  .predictedCombinedPracticeScore;
const legacyEvidence = buildEsatTestEvidence([legacyRow]);
assert.equal(legacyEvidence[0].testId, legacyId);
assert.equal(legacyEvidence[0].attemptNumber, 2);
assert.equal(legacyEvidence[0].effectiveWeight, 1.5);
assert.equal(legacyEvidence[0].predictedCombinedPracticeScore, legacyScore);
const mixed = predict([legacyRow, chronologicalRows[0]]);
assert.equal(mixed.independentTestCount, 2);
assert.equal(mixed.combinedFullCount, 2);
assert.equal(mixed.testWeight, 3);
assert.equal(mixed.testSignalPracticeScore,
  Math.round(((legacyScore + 4.5) / 2) * 100) / 100,
  "Legacy and October independent families retain the same 1.5 evidence weight.");

const concentrated = buildEsatTestEvidence([row(engineId, [27, 0, 0])])[0];
const distributed = buildEsatTestEvidence([row(engineId, [9, 9, 9])])[0];
assert.notEqual(concentrated.predictedCombinedPracticeScore,
  distributed.predictedCombinedPracticeScore,
  "Equal raw totals /81 may have different module conversions; never use a generic /81 curve.");
assert.equal(concentrated.predictedCombinedPracticeScore, 3.7);
assert.equal(distributed.predictedCombinedPracticeScore, 3.5);

console.log(
  "ESAT October prediction integration passed: all six pathways feed canonical module scores; " +
  "shared-module evidence remains one independent family; chronological 75/25 retakes, " +
  "legacy 1.5 weights and confidence/high-score gates are unchanged; " +
  "historical false metadata and forged scores cannot override canonical answers.",
);
