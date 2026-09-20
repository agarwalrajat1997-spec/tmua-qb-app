import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import vm from "node:vm";
import {
  TMUA_PAST_PAPER_OPTION_COUNTS as counts,
  validateTmuaPastPaperSettings as validate,
  readTmuaPastPaperSettings as readSettings,
  formatTmuaPastPaperSettings as format,
} from "../lib/tmua/past-paper-settings.ts";
import { getCanonicalTmuaTest } from "../lib/server/tmua-canonical-tests.ts";

const copy = value => JSON.parse(JSON.stringify(value));
function settings(testId, multiplier = 1, order = "sequential") {
  const original = Array.from({ length: 40 }, (_, index) => index);
  return {
    version: 1, order, time_multiplier: multiplier, seconds_per_paper: 4500 * multiplier,
    question_order: order === "sequential" ? original : [...original.slice(0, 20).reverse(), ...original.slice(20).reverse()],
    option_order: counts[testId].map((count, index) => {
      const letters = [..."ABCDEFGH".slice(0, count)];
      if (order !== "sequential" && testId === "full-official-2022" && index === 23) return [...letters.slice(0, 4).reverse(), "E"];
      return order === "sequential" ? letters : letters.reverse();
    }),
  };
}

assert.equal(Object.keys(counts).length, 9);
for (const [testId, optionCounts] of Object.entries(counts)) {
  const html = readFileSync(`public/practice-tests/tests/${testId}.html`, "utf8");
  const sourceOptions = Array.from({ length: 40 }, () => []);
  for (const match of html.matchAll(/<input\s+type="radio"\s+name="q(\d+)"\s+value="([A-H])"/g)) {
    sourceOptions[Number(match[1]) - 1].push(match[2]);
  }
  assert.deepEqual(sourceOptions.map(row => row.length), optionCounts, `${testId}: option-count drift`);
  sourceOptions.forEach(row => assert.equal(row.join(""), "ABCDEFGH".slice(0, row.length)));
  for (const multiplier of [1, 1.25, 1.5]) for (const order of ["sequential", "randomised"]) {
    const value = settings(testId, multiplier, order);
    assert.deepEqual(validate(testId, value), value);
    const validated = validate(testId, value);
    value.question_order[0] = 99;
    value.option_order[0][0] = "X";
    assert.notEqual(validated.question_order[0], 99, "Validated metadata must not alias request data.");
    assert.notEqual(validated.option_order[0][0], "X");
  }
}

const testId = "full-official-2016";
const valid = settings(testId, 1.25, "randomised");
assert.match(format(valid), /Randomised questions and options.*\+25% extra time.*93 min 45 sec/);
assert.match(format(settings(testId)), /Original order.*Standard time.*75 min per paper/);
assert.equal(validate(testId, undefined), null);
assert.equal(readSettings(testId, { tmua_past_paper_settings: null }), null);
assert.equal(readSettings(testId, { unrelated: true }), null);

const malformed = [null, [], {}, { ...valid, version: "1" }, { ...valid, order: "random" }, { ...valid, order: ["randomised"] },
  { ...valid, time_multiplier: "1.25" }, { ...valid, time_multiplier: 2 },
  { ...valid, seconds_per_paper: 4500 }, { ...valid, question_order: valid.question_order.slice(1) },
  { ...valid, question_order: Array(40).fill(0) }, { ...valid, question_order: Array.from({length:40}, (_,i)=>39-i) },
  { ...valid, question_order: valid.question_order.map((q,i)=>i===0?0.5:q) },
  { ...valid, option_order: valid.option_order.slice(1) },
  { ...valid, option_order: valid.option_order.map((letters,i)=>i===0?letters.slice(1):letters) },
  { ...valid, option_order: valid.option_order.map((letters,i)=>i===0?Array(letters.length).fill("A"):letters) },
  { ...valid, option_order: valid.option_order.map((letters,i)=>i===0?["X", ...letters.slice(1)]:letters) },
  { ...valid, order: "sequential" }];
for (const value of malformed) assert.throws(() => validate(testId, value));
const movedDependentOption = settings("full-official-2022", 1, "randomised");
movedDependentOption.option_order[23] = ["E", "A", "B", "C", "D"];
assert.throws(() => validate("full-official-2022", movedDependentOption));
for (const unsupported of ["full-mock-01-all-topics", "tmua-2026-predictive-paper", "esat-mock-02", "__proto__", "full-official-2024"]) {
  assert.throws(() => validate(unsupported, valid));
}

// Exercise real handlers against an in-memory database; no network, emails or real rows.
const require = createRequire(import.meta.url);
const ts = require("typescript"), cache = new Map();
let db, authorised = true;
function load(file) {
  const filename = path.resolve(file);
  if (cache.has(filename)) return cache.get(filename).exports;
  const module = { exports: {} }; cache.set(filename, module);
  const js = ts.transpileModule(readFileSync(filename, "utf8"), {
    compilerOptions: { target: ts.ScriptTarget.ES2020, module: ts.ModuleKind.CommonJS },
  }).outputText;
  function localRequire(id) {
    if (id === "next/server") return { NextResponse: { json: (body, options = {}) => ({ body, status: options.status ?? 200 }) } };
    if (id === "@/lib/supabase/server") return { createSupabaseServerClient: async () => ({
      auth: { getUser: async () => ({ data: { user: authorised ? { id: "qa-user", email: "qa@example.invalid" } : null }, error: null }) },
      from: (...args) => db.from(...args),
    }) };
    const target = id.startsWith("@/") ? path.resolve(id.slice(2)) : id.startsWith(".") ? path.resolve(path.dirname(filename), id) : null;
    return target ? load(target.endsWith(".ts") ? target : `${target}.ts`) : require(id);
  }
  vm.runInNewContext(js, { exports: module.exports, module, require: localRequire, Date, JSON, Math, Number, String, Object, Array, Set, Map, URL, console }, { filename });
  return module.exports;
}
function database() {
  const calls = [], inserted = [], tables = {
    tmua_test_catalog: Object.keys(counts).map(id => ({ test_id: id, title: id, paper: "full", expected_questions: 40, score_conversion_profile: "qa-profile" })),
    practice_test_attempts: [], tmua_test_attempt_evaluations: [],
  };
  const result = { calls, inserted, tables, from(table) {
    const call = { table, filters: [] }; calls.push(call);
    let inserting;
    function rows() { return (tables[table] ?? []).filter(row => call.filters.every(([key, value]) => row[key] === value)); }
    const query = {
      select(columns) { call.columns = columns; return query; },
      eq(key, value) { call.filters.push([key, value]); return query; },
      order() { return query; }, limit() { return query; },
      insert(value) { inserting = { id: `qa-${inserted.length}`, ...value }; inserted.push(inserting); tables[table].push(inserting); return query; },
      async maybeSingle() { return { data: inserting ?? rows()[0] ?? null, error: null }; },
      async single() { return { data: inserting ?? rows()[0] ?? null, error: null }; },
      then(resolve, reject) { return Promise.resolve({ data: rows(), error: null, count: rows().length }).then(resolve, reject); },
    };
    return query;
  } };
  return result;
}
const { POST } = load("app/api/practice-tests/submit/route.ts");
const { GET } = load("app/api/practice-tests/attempts/route.ts");
for (const id of Object.keys(counts)) {
  for (const multiplier of [1, 1.25, 1.5]) for (const order of ["sequential", "randomised"]) {
    db = database();
    const canonical = getCanonicalTmuaTest(id);
    const answers = canonical.answers.map((answer, i) => i % 3 === 0 ? null : answer);
    const timeSpent = Array.from({ length: 40 }, (_, i) => 90 + i);
    const flags = Array.from({ length: 40 }, (_, i) => i % 2 === 0);
    const attemptSettings = settings(id, multiplier, order);
    const response = await POST({ json: async () => ({ test_id: id, answers, time_spent: timeSpent, flags,
      correct_answers: Array(40).fill("X"), score: 40, attempt_settings: attemptSettings,
      predictor_metadata: { raw_mark_authority: "client-forged" } }) });
    assert.equal(response.status, 200);
    const saved = copy(db.inserted[0]);
    assert.equal(saved.score, 26, "Shuffling and extra time must not alter canonical raw marks.");
    assert.equal(saved.paper_1_score, 13); assert.equal(saved.paper_2_score, 13);
    assert.deepEqual(saved.correct_answers, [...canonical.answers]);
    assert.deepEqual(saved.answers, answers); assert.deepEqual(saved.time_spent, timeSpent); assert.deepEqual(saved.flags, flags);
    assert.equal(saved.predictor_metadata.raw_mark_authority, "server_canonical_key_v1");
    assert.equal(saved.predictor_metadata.client_correct_answers_match_canonical, false);
    assert.deepEqual(saved.predictor_metadata.tmua_past_paper_settings, attemptSettings);
    const history = await GET({ url: `https://qa.invalid/api/practice-tests/attempts?test_id=${id}` });
    assert.equal(history.status, 200);
    assert.deepEqual(copy(history.body.attempts[0].attempt_settings), attemptSettings);
    assert.equal("predictor_metadata" in history.body.attempts[0], false, "Do not expose unrelated internal predictor metadata.");
    const overview = await GET({ url: "https://qa.invalid/api/practice-tests/attempts" });
    assert.deepEqual(copy(overview.body.latest[0].attempt_settings), attemptSettings);
    assert(db.calls.filter(call => call.table === "practice_test_attempts" && call.columns?.includes("test_title")).every(call =>
      call.filters.some(([key, value]) => key === "user_id" && value === "qa-user")), "History queries remain owner-scoped.");
  }
}
for (const value of malformed) {
  db = database();
  const response = await POST({ json: async () => ({ test_id: testId, answers: getCanonicalTmuaTest(testId).answers, attempt_settings: value }) });
  assert.equal(response.status, 400); assert.equal(db.inserted.length, 0);
}
db = database();
assert.equal((await POST({ json: async () => ({ test_id: "full-official-2022", attempt_settings: movedDependentOption }) })).status, 400);
assert.equal(db.inserted.length, 0);
db = database();
const legacy = await POST({ json: async () => ({ test_id: testId, answers: getCanonicalTmuaTest(testId).answers }) });
assert.equal(legacy.status, 200);
assert.equal(db.inserted[0].predictor_metadata.tmua_past_paper_settings, undefined);
authorised = false;
assert.equal((await POST({ json: async () => ({ test_id: testId }) })).status, 401);
assert.equal((await GET({ url: "https://qa.invalid/api/practice-tests/attempts" })).status, 401);
console.log("TMUA past-paper settings: 360 template option counts, 54 scoring/history combinations, invalid mappings, legacy compatibility and owner-scoped reads verified.");
