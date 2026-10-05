import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import vm from "node:vm";
import { validatePracticeSettings } from "../lib/practice-settings.ts";
import { TMUA_CANONICAL_TESTS, getCanonicalTmuaTest } from "../lib/server/tmua-canonical-tests.ts";
import { ESAT_CANONICAL_TESTS } from "../lib/server/esat-canonical-tests.ts";
import { TMUA_PREDICTIVE_2026_ID, TMUA_PREDICTIVE_2026_SCORES } from "../lib/server/tmua-predictive-2026.ts";
import { createStandardTimeEstimate, practiceSpec, readPracticeResult, readTrustedPracticeResult, resolvePracticeSettings } from "../lib/server/practice-standard-time.ts";
import { applyStandardTimeTmuaEvaluations } from "../lib/server/practice-predictor-overlay.ts";
import { buildEsatTestEvidence } from "../lib/server/esat-predictor-evidence.ts";
import { TMUA_TOPIC_SCORE_PROFILES } from "../lib/server/tmua-topic-score-estimates.ts";

const copy = value => JSON.parse(JSON.stringify(value));
const conversion = { profile: "qa-linear", conversion_version: "qa-v1", score_values: Array.from({ length: 41 }, (_, raw) => 1 + raw / 5) };
const ids = [...Object.keys(TMUA_CANONICAL_TESTS), TMUA_PREDICTIVE_2026_ID, ...Object.keys(ESAT_CANONICAL_TESTS)];
function settings(testId, multiplier = 1, order = "sequential") {
  const spec = practiceSpec(testId);
  let offset = 0;
  return { version: 1, order, time_multiplier: multiplier,
    question_order: spec.sections.flatMap(size => {
      const indices = Array.from({ length: size }, (_, index) => index + offset); offset += size;
      return order === "randomised" ? indices.reverse() : indices;
    }), section_sizes: spec.sections, base_seconds_per_section: spec.seconds };
}
function metadata(testId, answers, multiplier = 1, order = "sequential") {
  const practice_settings = settings(testId, multiplier, order);
  return { practice_settings, standard_time_estimate: createStandardTimeEstimate(testId, answers, practice_settings, conversion) };
}

let combinations = 0;
for (const id of ids) for (const multiplier of [1, 1.25, 1.5]) for (const order of ["sequential", "randomised"]) {
  const spec = practiceSpec(id), selected = [...spec.canonical.answers];
  const original = copy(selected), input = settings(id, multiplier, order);
  assert.deepEqual(resolvePracticeSettings(id, input), input);
  const result = createStandardTimeEstimate(id, selected, input, conversion);
  assert.deepEqual(selected, original, "Display order never reorders submitted answer identities.");
  assert.equal(result.actual_raw, spec.canonical.expectedQuestions);
  const per40 = multiplier === 1.25 ? 3 : multiplier === 1.5 ? 5 : 0;
  const unitSizes = spec.exam === "esat" ? [27, 27, 27] : [selected.length];
  assert.deepEqual(result.units.map(unit => unit.deduction), unitSizes.map(size => Math.round(per40 * size / 40)));
  assert.equal(result.adjusted_raw, selected.length - result.units.reduce((sum, unit) => sum + unit.deduction, 0));
  assert.equal(result.provisional, true); assert.equal(result.official, false);
  assert.match(result.note, /not validated.*not an official result.*raw marks are unchanged/);
  if (spec.exam === "tmua") {
    const table = id === TMUA_PREDICTIVE_2026_ID ? TMUA_PREDICTIVE_2026_SCORES : selected.length === 20 ? TMUA_TOPIC_SCORE_PROFILES[id].scores : conversion.score_values;
    assert.equal(result.estimated_score, table[result.adjusted_raw]);
  }
  const stored = { practice_settings: input, standard_time_estimate: result };
  assert.deepEqual(readPracticeResult(id, stored, selected, selected.length).standard_time_estimate, result);
  const zero = createStandardTimeEstimate(id, Array(selected.length).fill(null), input, conversion);
  assert.equal(zero.actual_raw, 0); assert.equal(zero.adjusted_raw, 0);
  assert(zero.units.every(unit => unit.adjusted_raw === 0));
  combinations += 1;
}

const tmuaId = "full-official-2016", canonical = getCanonicalTmuaTest(tmuaId), allCorrect = [...canonical.answers];
const valid = settings(tmuaId, 1.25, "randomised");
for (const invalid of [null, [], {}, { ...valid, version: "1" }, { ...valid, order: ["randomised"] },
  { ...valid, order: "random" }, { ...valid, time_multiplier: "1.25" }, { ...valid, time_multiplier: 2 },
  { ...valid, section_sizes: [40] }, { ...valid, base_seconds_per_section: 2400 },
  { ...valid, question_order: Array(40).fill(0) }, { ...valid, question_order: valid.question_order.slice(1) },
  { ...valid, question_order: Array.from({ length: 40 }, (_, i) => 39 - i) }, { ...valid, order: "sequential" }]) {
  assert.throws(() => validatePracticeSettings(invalid, [20, 20], 4500));
}
for (const id of ["unknown", "__proto__", "constructor"]) assert.throws(() => resolvePracticeSettings(id, valid));
assert.equal(resolvePracticeSettings(tmuaId, undefined), null);
const historical = { tmua_past_paper_settings: { version: 1, time_multiplier: 1.25 } };
assert.equal(readPracticeResult(tmuaId, historical, allCorrect, 40).standard_time_estimate, null,
  "Old presentation settings must never opt historical rows into the new policy.");
const goodMetadata = metadata(tmuaId, allCorrect, 1.5);
for (const mutate of [m => { m.standard_time_estimate.canonical_key_sha256 = "stale"; },
  m => { m.standard_time_estimate.answers_sha256 = "wrong"; }, m => { m.standard_time_estimate.actual_raw = 39; },
  m => { m.standard_time_estimate.units[0].adjusted_raw = 40; }, m => { m.practice_settings.time_multiplier = 1; }]) {
  const bad = copy(goodMetadata); mutate(bad);
  assert.equal(readPracticeResult(tmuaId, bad, allCorrect, 40).standard_time_estimate, null);
}
const forgedNumeric = copy(goodMetadata);
forgedNumeric.standard_time_estimate.estimated_score = 9;
forgedNumeric.standard_time_estimate.units[0].estimated_score = 9;
forgedNumeric.standard_time_estimate.note = "Forged official result";
const trusted = readTrustedPracticeResult(tmuaId, forgedNumeric, allCorrect, 40, conversion).standard_time_estimate;
assert.equal(trusted.estimated_score, 8); assert.match(trusted.note, /not an official result/);
assert.equal(readTrustedPracticeResult(tmuaId, goodMetadata, allCorrect, 40).standard_time_estimate.estimated_score, null,
  "Missing trusted full-test conversion cannot fall back to the stored scaled score.");

const evaluation = { attempt_id: "qa", test_id: tmuaId, predictor_eligible: true, combined_score_eligible: true,
  effective_weight: .9, authoritative_tmua_score9: 9, paper_1_raw_score: 20, paper_2_raw_score: 20,
  paper_1_effective_weight: .675, paper_2_effective_weight: .675 };
const catalogue = [{ test_id: tmuaId, score_conversion_profile: conversion.profile, base_weight: 1,
  minimum_partial_answered: 12, minimum_full_weight_answered: 18, minimum_average_seconds: 10 }];
const row = { id: "qa", test_id: tmuaId, answers: allCorrect, time_spent: Array(40).fill(6750 / 20), predictor_metadata: goodMetadata };
const overlaid = applyStandardTimeTmuaEvaluations([evaluation], [row], [conversion], catalogue)[0];
assert.equal(overlaid.effective_weight, 1, "Declared +50% time is not penalised a second time by the legacy .9 timing factor.");
assert.equal(overlaid.authoritative_tmua_score9, 8);
assert.equal(overlaid.paper_1_raw_score + overlaid.paper_2_raw_score, 35, "One /40 deduction, never two /20 roundings.");
assert.equal(evaluation.effective_weight, .9); assert.equal(evaluation.paper_1_raw_score, 20, "No database/raw evaluation mutation.");
assert.equal(applyStandardTimeTmuaEvaluations([evaluation], [{ ...row, predictor_metadata: historical }], [conversion], catalogue)[0], evaluation);
for (const bad of [{ ...row, time_spent: [] }, { ...row, predictor_metadata: { ...goodMetadata, standard_time_estimate: { ...goodMetadata.standard_time_estimate, canonical_key_sha256: "bad" } } }]) {
  const excluded = applyStandardTimeTmuaEvaluations([evaluation], [bad], [conversion], catalogue)[0];
  assert.equal(excluded.predictor_eligible, false); assert.equal(excluded.effective_weight, 0);
}
for (const raw of [0, 1, 2, 3, 4, 5, 20, 33, 40]) for (const multiplier of [1, 1.25, 1.5]) {
  const answers = allCorrect.map((answer, index) => index < raw ? answer : null);
  const meta = metadata(tmuaId, answers, multiplier);
  const result = applyStandardTimeTmuaEvaluations([evaluation], [{ ...row, answers, predictor_metadata: meta }], [conversion], catalogue)[0];
  assert.equal(result.paper_1_raw_score + result.paper_2_raw_score, meta.standard_time_estimate.adjusted_raw);
  assert(result.paper_1_raw_score >= 0 && result.paper_2_raw_score >= 0);
}
const paperId = Object.keys(TMUA_CANONICAL_TESTS).find(id => getCanonicalTmuaTest(id).expectedQuestions === 20);
const paperSpec = practiceSpec(paperId), paperMeta = metadata(paperId, paperSpec.canonical.answers, 1.5);
const paperResult = applyStandardTimeTmuaEvaluations([{ ...evaluation, test_id: paperId }], [{ ...row, test_id: paperId,
  answers: [...paperSpec.canonical.answers], time_spent: Array(20).fill(6750 / 20), predictor_metadata: paperMeta }], [conversion],
  [{ ...catalogue[0], test_id: paperId }])[0];
assert.equal(paperResult.paper_1_raw_score + paperResult.paper_2_raw_score, 17);
assert.equal(paperMeta.standard_time_estimate.estimated_score, TMUA_TOPIC_SCORE_PROFILES[paperId].scores[17]);
for (const [id, profile] of Object.entries(TMUA_TOPIC_SCORE_PROFILES)) {
  const html = readFileSync(getCanonicalTmuaTest(id).sourceFile, "utf8");
  const table = html.match(/scoreMap:Object\.freeze\((\[[^\]]+\])/);
  if (table) assert.deepEqual(profile.scores, JSON.parse(table[1]), `${id}: source score map drift`);
  else {
    assert.match(html, /thresholdRaw = 6/);
    assert.deepEqual(profile.scores, Array.from({ length: 21 }, (_, raw) => raw <= 6 ? 1 : Math.round((1 + 8 * (raw - 6) / 14) * 10) / 10));
  }
}

for (const id of Object.keys(ESAT_CANONICAL_TESTS)) {
  const answers = [...practiceSpec(id).canonical.answers], meta = metadata(id, answers, 1.5);
  const base = { id: "qa-esat", test_id: id, answers, submitted_at: "2026-10-05T00:00:00.000Z" };
  const evidence = buildEsatTestEvidence([{ ...base, predictor_metadata: meta }]);
  assert.equal(evidence[0].predictedCombinedPracticeScore, meta.standard_time_estimate.estimated_score);
  assert.equal(meta.standard_time_estimate.adjusted_raw, 72);
  const bad = copy(meta); bad.standard_time_estimate.answers_sha256 = "wrong";
  assert.deepEqual(buildEsatTestEvidence([{ ...base, predictor_metadata: bad }]), []);
  assert.deepEqual(buildEsatTestEvidence([{ ...base, predictor_metadata: historical }]), buildEsatTestEvidence([base]));
}

// Real submit/history/calculator handlers, with an entirely in-memory database.
// No network, real account, database write, email, or production state involved.
const require = createRequire(import.meta.url), ts = require("typescript"), cache = new Map();
let db, authorised = true;
function load(file) {
  const filename = path.resolve(file); if (cache.has(filename)) return cache.get(filename).exports;
  const module = { exports: {} }; cache.set(filename, module);
  const js = ts.transpileModule(readFileSync(filename, "utf8"), { compilerOptions: { target: ts.ScriptTarget.ES2020, module: ts.ModuleKind.CommonJS } }).outputText;
  function localRequire(id) {
    if (id === "next/server") return { NextResponse: { json: (body, options = {}) => ({ body, status: options.status ?? 200 }) } };
    if (id === "@/lib/supabase/server") return { createSupabaseServerClient: async () => ({
      auth: { getUser: async () => ({ data: { user: authorised ? { id: "qa-user", email: "qa@example.invalid" } : null }, error: null }) }, from: (...args) => db.from(...args) }) };
    const target = id.startsWith("@/") ? path.resolve(id.slice(2)) : id.startsWith(".") ? path.resolve(path.dirname(filename), id) : null;
    return target ? load(target.endsWith(".ts") ? target : `${target}.ts`) : require(id);
  }
  vm.runInNewContext(js, { exports: module.exports, module, require: localRequire, console, Date, JSON, Math, Number, String, Object, Array, Set, Map, URL }, { filename });
  return module.exports;
}
function database() {
  const inserts = [], calls = [], errors = {}, tables = {
    tmua_test_catalog: ids.filter(id => practiceSpec(id).exam === "tmua").map(id => ({ test_id: id, title: id,
      paper: practiceSpec(id).canonical.structure === "full" ? "full" : practiceSpec(id).canonical.structure === "paper1" ? "1" : "2",
      expected_questions: practiceSpec(id).canonical.expectedQuestions, score_conversion_profile: practiceSpec(id).canonical.expectedQuestions === 20 ? null : conversion.profile })),
    tmua_score_conversion_profiles: [copy(conversion)], practice_test_attempts: [], tmua_test_attempt_evaluations: [],
  };
  return { inserts, calls, errors, tables, from(table) {
    const filters = [], call = { table, filters }; calls.push(call); let inserted;
    const rows = () => (tables[table] ?? []).filter(row => filters.every(([key, values]) => values.includes(row[key])));
    const query = { select(columns) { call.columns = columns; return query; }, eq(key, value) { filters.push([key, [value]]); return query; },
      in(key, values) { filters.push([key, values]); return query; }, order() { return query; }, limit() { return query; },
      insert(value) { call.insert = true; inserted = { id: `qa-${inserts.length}`, ...value }; inserts.push(inserted); tables[table].push(inserted); return query; },
      async maybeSingle() { return { data: errors[table] ? null : inserted ?? rows()[0] ?? null, error: errors[table] ?? null }; }, async single() { return { data: inserted ?? rows()[0] ?? null, error: errors[table] ?? null }; },
      then(resolve, reject) { return Promise.resolve({ data: errors[table] ? null : rows(), count: rows().length, error: errors[table] ?? null }).then(resolve, reject); } };
    return query;
  } };
}
const { POST } = load("app/api/practice-tests/submit/route.ts"), { GET } = load("app/api/practice-tests/attempts/route.ts");
const calculator = load("app/api/esat/score-estimate/route.ts").POST;
for (const id of ids) for (const multiplier of [1, 1.25, 1.5]) {
  db = database(); const spec = practiceSpec(id), answers = [...spec.canonical.answers], input = settings(id, multiplier, "randomised");
  const response = await POST({ json: async () => ({ test_id: id, answers, time_spent: Array(answers.length).fill(150), complete: true,
    score: 999, correct_answers: Array(answers.length).fill("X"), practice_settings: input,
    predictor_metadata: { standard_time_estimate: { estimated_score: 9 } } }) });
  assert.equal(response.status, 200, `${id}: save failed: ${JSON.stringify(response.body)}`);
  assert.equal(db.inserts[0].score, answers.length); assert.deepEqual(copy(db.inserts[0].answers), answers);
  assert.deepEqual(copy(db.inserts[0].correct_answers), [...spec.canonical.answers]);
  assert.deepEqual(copy(response.body.practice_settings), input);
  assert.equal(response.body.standard_time_estimate.actual_raw, answers.length);
  assert.equal(db.inserts[0].predictor_metadata.standard_time_estimate.policy_version, "ts-standard-time-equivalent-v1");
  const history = await GET({ url: `https://qa.invalid/api/practice-tests/attempts?test_id=${id}` });
  assert.equal(history.status, 200);
  assert.deepEqual(copy(history.body.attempts[0].standard_time_estimate), copy(response.body.standard_time_estimate));
  const summary = await GET({ url: "https://qa.invalid/api/practice-tests/attempts" });
  assert.equal(summary.status, 200);
  assert.deepEqual(copy(summary.body.latest[0].standard_time_estimate), copy(response.body.standard_time_estimate));
  assert.equal("answers" in summary.body.latest[0], false); assert.equal("predictor_metadata" in summary.body.latest[0], false);
  assert(db.calls.filter(call => call.table === "practice_test_attempts" && call.columns && !call.insert).every(call =>
    call.filters.some(([key, values]) => key === "user_id" && values.includes("qa-user")) || call.filters.some(([key]) => key === "id")), "History stays owner-scoped.");
}
for (const mode of ["missing", "unavailable"]) {
  db = database();
  if (mode === "missing") db.tables.tmua_score_conversion_profiles = [];
  else db.errors.tmua_score_conversion_profiles = { message: "QA conversion table temporarily unavailable" };
  const saved = await POST({ json: async () => ({ test_id: tmuaId, answers: allCorrect, practice_settings: valid }) });
  assert.equal(saved.status, 200); assert.equal(db.inserts.length, 1, "A conversion outage saves the canonical raw attempt exactly once.");
  assert.equal(db.inserts[0].score, 40); assert.equal(saved.body.standard_time_estimate.adjusted_raw, 37);
  assert.equal(saved.body.standard_time_estimate.estimated_score, null);
  assert.match(saved.body.standard_time_estimate.note, /temporarily unavailable.*estimate is pending/);
  const hidden = await GET({ url: `https://qa.invalid/api/practice-tests/attempts?test_id=${tmuaId}` });
  assert.equal(hidden.body.attempts[0].standard_time_estimate.estimated_score, null);
  db.tables.tmua_score_conversion_profiles = [copy(conversion)]; delete db.errors.tmua_score_conversion_profiles;
  const recovered = await GET({ url: `https://qa.invalid/api/practice-tests/attempts?test_id=${tmuaId}` });
  assert.equal(recovered.body.attempts[0].standard_time_estimate.estimated_score, conversion.score_values[37]);
  assert.equal(db.inserts.length, 1); assert.equal(db.inserts[0].predictor_metadata.standard_time_estimate.estimated_score, null,
    "Recovery recalculates in memory, without rewriting the stored attempt.");
}
db = database();
assert.equal((await POST({ json: async () => ({ test_id: tmuaId, answers: allCorrect }) })).status, 200);
assert.equal(db.inserts[0].predictor_metadata.standard_time_estimate, undefined);
db = database();
assert.equal((await POST({ json: async () => ({ test_id: tmuaId, answers: allCorrect, practice_settings: { ...valid, section_sizes: [40] } }) })).status, 400);
assert.equal(db.inserts.length, 0);
const esatId = "esat-mock-01", esatAnswers = [...practiceSpec(esatId).canonical.answers];
const calculated = await calculator({ json: async () => ({ test_id: esatId, raw_scores: [0, 0, 0], answers: esatAnswers, practice_settings: settings(esatId, 1.5) }) });
assert.equal(calculated.status, 200); assert.equal(calculated.body.standard_time_estimate.actual_raw, 81); assert.equal(calculated.body.standard_time_estimate.adjusted_raw, 72);
assert.equal((await calculator({ json: async () => ({ test_id: esatId, raw_scores: [27, 27, 27] }) })).body.standard_time_estimate, null);
assert.equal((await calculator({ json: async () => ({ test_id: esatId, raw_scores: [27, 27, 27], practice_settings: settings(esatId, 1.5) }) })).status, 400);
authorised = false; db = database();
assert.equal((await POST({ json: async () => ({}) })).status, 401);
assert.equal((await GET({ url: "https://qa.invalid/api/practice-tests/attempts" })).status, 401);
assert.equal(db.calls.length, 0);
console.log(`Practice standard-time policy: ${ids.length} canonical tests, ${combinations} settings/estimate combinations, canonical save/history/calculator paths, historical isolation, corruption guards and single-penalty predictors verified.`);
