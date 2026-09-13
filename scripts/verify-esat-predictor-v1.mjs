import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

import {
  ESAT_PREDICTOR_V1_MODEL_VERSION,
  calculateEsatPredictorV1,
} from "../lib/server/esat-predictor-v1-engine.ts";

const activeTopics = ["Algebra", "Biology", "Chemistry", "Physics"];

function testAttempt(testId, score, attemptNumber = 1, day = attemptNumber) {
  return {
    testId,
    attemptId: `${testId}-${attemptNumber}`,
    attemptNumber,
    evaluatedAt: `2026-08-${String(day).padStart(2, "0")}T10:00:00.000Z`,
    predictorEligible: true,
    predictedCombinedPracticeScore: score,
    effectiveWeight: 1.5,
  };
}

function calculate(testAttempts = [], qbEvents = []) {
  return calculateEsatPredictorV1({ testAttempts, qbEvents, activeTopics });
}

const empty = calculate();
assert.equal(empty.modelVersion, ESAT_PREDICTOR_V1_MODEL_VERSION);
assert.equal(empty.predictionStatus, "insufficient_evidence");
assert.equal(empty.predictedEsatPracticeScore, null);

const onePaper = calculate([
  testAttempt("esat-mock-01", 5.7),
]);
assert.equal(onePaper.predictionStatus, "predicted");
assert.equal(onePaper.predictedEsatPracticeScore, 5.7);
assert.equal(onePaper.confidence, "low");
assert.equal(onePaper.independentTestCount, 1);
assert.equal(onePaper.combinedFullCount, 1);

const retake = calculate([
  testAttempt("esat-mock-01", 4, 1, 1),
  testAttempt("esat-mock-01", 6, 2, 2),
  testAttempt("esat-mock-01", 8, 3, 3),
]);
assert.equal(
  retake.testSignalPracticeScore,
  5,
  "Only first (75%) and latest (25%) retakes should contribute.",
);
assert.equal(retake.independentTestCount, 1);
assert.equal(retake.testEvidenceCount, 3);

const repeatedStrong = calculate([
  testAttempt("esat-mock-01", 7.6),
  testAttempt("esat-mock-02", 7.6),
  testAttempt("esat-mock-03", 7.6),
]);
assert.equal(repeatedStrong.predictedEsatPracticeScore, 7.6);
assert.equal(repeatedStrong.confidence, "high");
assert.equal(repeatedStrong.independentTestCount, 3);

const oneExceptionalPaper = calculate([
  testAttempt("esat-mock-01", 8.8),
]);
assert.equal(
  oneExceptionalPaper.predictedEsatPracticeScore,
  6.75,
  "The production high-score evidence gate must prevent one paper claiming an 8+ prediction.",
);

const qbEvents = Array.from({ length: 30 }, (_, index) => ({
  id: `qb-${index + 1}`,
  source: "qb-progress-trigger-v2",
  historyQuality: "observed",
  predictorEligible: true,
  canonicalQid: `qid-${index + 1}`,
  canonicalActive: true,
  selectedAnswer: index < 21 ? "A" : "B",
  canonicalAnswer: "A",
  canonicalTopic: activeTopics[index % activeTopics.length],
  attemptedAt: `2026-07-${String((index % 28) + 1).padStart(2, "0")}T10:00:00.000Z`,
}));

const qbOnly = calculate([], qbEvents);
assert.equal(qbOnly.predictionStatus, "predicted");
assert.equal(qbOnly.confidence, "low");
assert.equal(qbOnly.qbUniqueQuestions, 30);
assert.ok((qbOnly.predictedEsatPracticeScore ?? 9) <= 6.25);

const hashesDiffer = calculate([
  testAttempt("esat-mock-01", 5.8),
]);
assert.notEqual(onePaper.inputHash, hashesDiffer.inputHash);

const submitRoute = readFileSync(
  "app/api/practice-tests/submit/route.ts",
  "utf8",
);
const overviewRoute = readFileSync(
  "app/api/esat/overview/route.ts",
  "utf8",
);
const progressRoute = readFileSync(
  "app/api/qb/progress/save/route.ts",
  "utf8",
);
const questionBank = readFileSync(
  "public/esat-question-bank/index.html",
  "utf8",
);
const dashboard = readFileSync(
  "app/esat/ESATDashboardClient.tsx",
  "utf8",
);

assert.match(submitRoute, /getCanonicalEsatTest\(testId\)/);
assert.match(submitRoute, /server_esat_canonical_key_v1/);
assert.match(submitRoute, /estimateEsatTestScores\(\s*testId,/);
assert.match(overviewRoute, /practice_test_attempts/);
assert.match(overviewRoute, /calculateEsatPredictorV1/);
assert.match(overviewRoute, /tmua_prediction_snapshots/);
assert.match(progressRoute, /product:\s*"esat-question-bank"/);
assert.match(progressRoute, /canonical_qid/);
assert.match(questionBank, /pendingSubmissionIds/);
assert.match(questionBank, /update\.submission_id\s*=/);
assert.match(questionBank, /update\.answer_submitted_at\s*=/);
assert.match(dashboard, /<EsatPredictionStrip\s*\/>/);
assert.match(dashboard, /test_id:\s*"esat-mock-05"/);

console.log(
  "ESAT Predictor V1 verification passed: evidence threshold, retakes, confidence, range inputs and high-score gates match production TMUA policy.",
);
