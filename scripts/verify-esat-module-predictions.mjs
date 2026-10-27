import assert from "node:assert/strict";
import { getCanonicalEsatTest } from "../lib/server/esat-canonical-tests.ts";
import { calculateEsatModulePredictions, buildEsatModuleTestEvidence, inferEsatPathway } from "../lib/server/esat-module-predictor.ts";
import { assessEsatResults, esatLockAt, validateEsatModules, ESAT_MODULES } from "../lib/esat-predictions.ts";

const modules = ["Mathematics 1", "Mathematics 2", "Physics"];
const asOf = "2026-10-01T00:00:00Z";
function attempt(testId, scores = [18, 15, 20], date = "2026-09-20T12:00:00Z") {
  const test = getCanonicalEsatTest(testId);
  return { id: `${testId}:${date}`, test_id: testId, submitted_at: date, attempt_number: 1,
    answers: test.answers.map((answer, index) => index % 27 < scores[Math.floor(index / 27)] ? answer : null) };
}
const calculate = (attempts = [], questions = [], qbRows = [], selected = modules) => calculateEsatModulePredictions({ modules: selected, attempts, questions, qbRows, asOf });
assert.deepEqual(validateEsatModules(["Physics", "Mathematics 1", "Biology"]), ["Mathematics 1", "Physics", "Biology"]);
assert.throws(() => validateEsatModules(["Physics", "Chemistry", "Biology"]));
assert.throws(() => validateEsatModules(["Mathematics 1", "Physics", "Physics"]));
assert.throws(() => esatLockAt("2027-02-30"));
assert.equal(esatLockAt("2027-01-04"), "2027-01-02T00:00:00.000Z");
assert.equal(esatLockAt("2026-10-13"), "2026-10-10T23:00:00.000Z");
assert.equal(esatLockAt("2026-10-27"), "2026-10-24T23:00:00.000Z", "BST cutoff on the clock-change day");
assert.equal(esatLockAt("2026-10-28"), "2026-10-26T00:00:00.000Z", "GMT cutoff after the clock change");

const empty = calculate();
assert.ok(empty.every(prediction => prediction.score === null && !prediction.guaranteeEligible));
const one = calculate([attempt("esat-mock-01", [27, 8, 20])]);
assert.notEqual(one[0].score, one[2].score);
assert.equal(one[2].score, null, "Below-3.5 predictions stay building (legacy mock order is M1, Physics, M2)");
assert.equal(one[0].confidence, "low");
const noChemistry = calculate([attempt("esat-mock-01")], [], [], ["Mathematics 1", "Physics", "Chemistry"]);
assert.equal(noChemistry[2].score, null, "Engineering test evidence cannot predict Chemistry");
assert.equal(noChemistry[2].independentTestCount, 0);
const high = calculate(["esat-mock-01", "esat-mock-03", "esat-mock-05"].map(id => attempt(id, [27,27,27])));
assert.ok(high.every(prediction => prediction.confidence === "high" && prediction.guaranteeEligible));

const questions = Array.from({ length: 30 }, (_, i) => ({ qid: `phy-${i}`, paper: "ESAT Physics", topic: `Topic ${i % 3}`, answer: "A", is_active: true }));
const qbRows = questions.map((q, i) => ({ id: `evt-${i}`, question_id: q.qid, metadata: { canonical_qid: q.qid }, source: "qb-progress-trigger-v2", history_quality: "observed", predictor_eligible: true, selected_answer: i < 24 ? "A" : "B", attempted_at: "2026-09-18T12:00:00Z" }));
const qb = calculate([], questions, qbRows);
assert.equal(qb[0].score, null); assert.equal(qb[1].score, null);
assert.equal(qb[2].qbUniqueQuestions, 30); assert.notEqual(qb[2].score, null); assert.equal(qb[2].confidence, "low");
assert.equal(calculate([], questions, qbRows.slice(1))[2].score, null);
const dup = calculate([], questions, [...qbRows, ...qbRows.map(row => ({ ...row, id: `repeat:${row.id}` }))]);
assert.equal(dup[2].qbUniqueQuestions, 30);
const future = calculate([attempt("esat-mock-01", [27, 27, 27], "2026-10-02T00:00:00Z")]);
assert.ok(future.every(prediction => prediction.score === null), "Post-cutoff evidence is excluded");

const pathways = [attempt("esat-october-2026-engineering"), attempt("esat-october-2026-physics-chemistry", [18,20,20], "2026-09-21T12:00:00Z")];
const reused = calculate(pathways);
assert.equal(reused[0].independentTestCount, 1, "Shared Mathematics 1 paper counts once across pathways");
assert.equal(reused[2].independentTestCount, 1, "Shared Physics paper counts once across pathways");
const legacyShared = calculate([attempt("esat-mock-01"), attempt("esat-physics-chemistry-level-0", [18,20,20], "2026-09-21T12:00:00Z")]);
assert.equal(legacyShared[0].independentTestCount, 1, "Recombined legacy Mathematics 1 paper counts once");

const timed = attempt("esat-mock-01", [20,20,20]);
timed.predictor_metadata = { practice_settings: { version: 1, order: "sequential", time_multiplier: 1.25, question_order: Array.from({length:81}, (_,i)=>i), section_sizes:[27,27,27], base_seconds_per_section:2400 } };
// Use the actual persisted practice-result schema for extra-time evidence.
const { createStandardTimeEstimate } = await import("../lib/server/practice-standard-time.ts");
const standard = createStandardTimeEstimate(timed.test_id, timed.answers, timed.predictor_metadata.practice_settings);
timed.predictor_metadata.standard_time_estimate = standard;
const adjusted = buildEsatModuleTestEvidence([timed], Date.parse(asOf));
for (const module of modules) assert.equal(adjusted[module][0].predictedCombinedPracticeScore, standard.units.find(unit => unit.label === module).estimated_score);

const locked = empty.map((prediction, i) => ({ ...prediction, score: 6.5, confidence: i === 2 ? "low" : "medium", guaranteeEligible: i !== 2 }));
assert.equal(assessEsatResults(locked, { "Mathematics 1": 6, "Mathematics 2": 6, Physics: 3 }).meetsScoreCondition, false, "Exactly 0.5 and low confidence do not qualify");
const twoMisses = assessEsatResults(locked, { "Mathematics 1": 5.9, "Mathematics 2": 5.8, Physics: 8 });
assert.equal(twoMisses.missedCount, 2); assert.equal(twoMisses.meetsScoreCondition, true);
assert.equal(assessEsatResults(locked, { "Mathematics 1": 5.9, "Mathematics 2": 6.5, Physics: 3 }).meetsScoreCondition, false);
assert.throws(() => assessEsatResults(locked, { "Mathematics 1": 5.91, "Mathematics 2": 6, Physics: 7 }));
assert.throws(() => assessEsatResults(locked, { "Mathematics 1": 5.9, "Mathematics 2": 6 }));
assert.deepEqual(ESAT_MODULES.length, 5);
console.log("PASS: ESAT module isolation, per-module QB thresholds, reused papers, timing adjustment, DST cutoffs and guarantee boundaries.");

const predictAll = (attempts = [], qs = [], events = []) => calculate(attempts, qs, events, [...ESAT_MODULES]);
assert.deepEqual(inferEsatPathway(predictAll()), { status: "building", modules: ["Mathematics 1"] });
assert.deepEqual(inferEsatPathway(predictAll([attempt("esat-mock-01")])), { status: "inferred", modules });
for (const [id, expected] of [
  ["physics-chemistry", ["Mathematics 1", "Physics", "Chemistry"]],
  ["physics-biology", ["Mathematics 1", "Physics", "Biology"]],
  ["maths2-chemistry", ["Mathematics 1", "Mathematics 2", "Chemistry"]],
  ["maths2-biology", ["Mathematics 1", "Mathematics 2", "Biology"]],
  ["chemistry-biology", ["Mathematics 1", "Chemistry", "Biology"]],
]) assert.deepEqual(inferEsatPathway(predictAll([attempt(`esat-${id}-level-0`)])), { status: "inferred", modules: expected });
assert.deepEqual(inferEsatPathway(predictAll([attempt("esat-mock-01", [18,0,0])])), { status: "building", modules: ["Mathematics 1"] }, "Blank sections cannot imply a pathway");
assert.equal(inferEsatPathway(predictAll([attempt("esat-mock-01"), attempt("esat-chemistry-biology-level-0")])).status, "building", "Mixed pathways remain uncertain");
assert.deepEqual(inferEsatPathway(predictAll([], questions, qbRows)), { status: "building", modules: ["Mathematics 1", "Physics"] });
const chemQuestions = questions.map(q => ({ ...q, qid:q.qid.replace("phy", "chem"), paper:"ESAT Chemistry" }));
const chemRows = qbRows.map(row => ({ ...row, id:`chem:${row.id}`, question_id:row.question_id.replace("phy", "chem"), metadata:{canonical_qid:row.question_id.replace("phy", "chem")} }));
assert.deepEqual(inferEsatPathway(predictAll([], [...questions, ...chemQuestions], [...qbRows, ...chemRows])), { status:"inferred", modules:["Mathematics 1", "Physics", "Chemistry"] }, "Question Bank alone can identify both optional modules");
assert.deepEqual(inferEsatPathway(predictAll([], [...questions, ...chemQuestions], [...qbRows, ...chemRows.slice(1)])), { status:"building", modules:["Mathematics 1", "Physics"] }, "Under-threshold optional modules are not guessed");
const strongEngineering = predictAll([attempt("esat-mock-01"), attempt("esat-mock-03"), attempt("esat-physics-chemistry-level-0")]);
assert.deepEqual(inferEsatPathway(strongEngineering), { status:"inferred", modules }, "Clear dominant practice wins over one exploratory module");
console.log("PASS: all six pathways, no setup, QB-only, partial/blank evidence, ambiguity and dominant practice.");
