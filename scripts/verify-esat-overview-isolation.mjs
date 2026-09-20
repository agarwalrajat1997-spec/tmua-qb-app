import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import ts from "typescript";
import * as canonical from "../lib/server/esat-canonical-tests.ts";
import * as predictor from "../lib/server/esat-predictor-v1-engine.ts";
import * as evidence from "../lib/server/esat-predictor-evidence.ts";
import * as october from "../lib/server/esat-october-2026-tests.ts";
import * as preparation from "../lib/server/tmua-preparation-rank-v1-engine.ts";
import * as recovery from "../lib/auth/service-recovery.ts";

// Execute the production GET handler against an instrumented, in-memory Data
// API. No live credentials, users, database mutations or network requests.
const source = readFileSync("app/api/esat/overview/route.ts", "utf8");
const compiled = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
}).outputText;
const NOW = Date.parse("2026-09-20T16:30:00Z");
const users = {
  a: { id: "student-a", email: "student_a@example.com" },
  b: { id: "student-b", email: "student-b@example.com" },
};
const topics = ["Algebra", "Biology", "Chemistry", "Physics"];
const questions = Array.from({ length: 32 }, (_, i) => ({
  qid: `ESAT-FIXTURE-${String(i).padStart(4, "0")}`,
  topic: topics[i % topics.length], answer: "A", is_active: true,
}));
function savedAttempt(user, testId, correctPerModule, suffix = "first", date = "2026-09-17T12:00:00Z") {
  const test = canonical.getCanonicalEsatTest(testId);
  return {
    id: `${user.id}-${testId}-${suffix}`, user_id: user.id, test_id: testId,
    answers: test.answers.map((answer, i) => i % 27 < correctPerModule ? answer : null),
    attempt_number: suffix === "first" ? 1 : 2, submitted_at: date,
  };
}
const aAttempts = Object.keys(canonical.ESAT_CANONICAL_TESTS).map(
  id => savedAttempt(users.a, id, 17),
);
aAttempts.push(savedAttempt(users.a, "esat-mock-01", 21, "latest", "2026-09-19T12:00:00Z"));
const bAttempts = [savedAttempt(users.b, "esat-mock-01", 5)];
function qbRows(user, right) {
  return questions.map((q, i) => ({
    id: `${user.id}-qb-${i}`, user_id: user.id,
    product: "esat-question-bank", question_id: String(i + 1),
    source: "qb-progress-trigger-v2", history_quality: "observed", predictor_eligible: true,
    metadata: { canonical_qid: q.qid }, selected_answer: i < right ? "A" : "B",
    attempted_at: `2026-09-${String(1 + i % 15).padStart(2, "0")}T12:00:00Z`,
  }));
}
const aQb = qbRows(users.a, 22);
const bQb = qbRows(users.b, 3);
const unescapeLike = text => text.replace(/\\([\\%_])/g, "$1");

function harness(overrides = {}) {
  let now = NOW;
  const state = { user: users.a, authError: null, failTable: null, failCode: "57014", ...overrides };
  const tables = {
    practice_test_attempts: structuredClone([...aAttempts, ...bAttempts]),
    tmua_qb_attempt_events: structuredClone([...aQb, ...bQb]),
    esat_qb_questions: structuredClone(questions),
    student_access: Object.values(users).map(user => ({
      email: user.email, product: "esat-question-bank", approved: true, expires_at: null,
    })),
  };
  const queries = [], snapshots = [], errors = [];
  class Clock extends Date {
    constructor(...args) { super(...(args.length ? args : [now])); }
    static now() { return now; }
  }
  function from(table) {
    const ops = [];
    let written = null, writeOptions = null;
    const builder = {};
    for (const method of ["select", "eq", "ilike", "in", "or", "order", "range", "limit", "retry"]) {
      builder[method] = (...args) => { ops.push([method, ...args]); return builder; };
    }
    builder.upsert = (row, options) => { written = row; writeOptions = options; return builder; };
    builder.then = (resolve, reject) => Promise.resolve().then(() => {
      queries.push({ table, ops: structuredClone(ops), written: !!written });
      assert.ok(ops.some(op => op[0] === "retry" && op[1] === false), "Every overview query explicitly disables SDK retries");
      if (state.failTable === table) return { data: null, error: { code: state.failCode, message: "fixture service failure" } };
      if (written) {
        assert.equal(table, "tmua_prediction_snapshots");
        assert.equal(writeOptions.ignoreDuplicates, true);
        assert.equal(writeOptions.onConflict, "user_id,model_version,input_hash");
        snapshots.push(structuredClone(written));
        return { data: null, error: null };
      }
      if (["practice_test_attempts", "tmua_qb_attempt_events"].includes(table)) {
        assert.ok(ops.some(op => op[0] === "eq" && op[1] === "user_id"), "A student request must never read cohort evidence");
        assert.ok(ops.some(op => op[0] === "order" && op[1] === "id"), "Pagination needs a deterministic tie-breaker");
      }
      if (table === "student_access") {
        assert.ok(ops.some(op => op[0] === "ilike" && op[1] === "email"), "Entitlements must be email-scoped");
        assert.ok(ops.some(op => op[0] === "limit" && op[1] === 1));
      }
      let rows = [...(tables[table] ?? [])];
      for (const [op, key, value] of ops) {
        if (op === "eq") rows = rows.filter(row => row[key] === value);
        if (op === "ilike") rows = rows.filter(row => row[key].toLowerCase() === unescapeLike(value).toLowerCase());
        if (op === "in") rows = rows.filter(row => value.includes(row[key]));
        if (op === "or") rows = rows.filter(row => row.expires_at == null || Date.parse(row.expires_at) > now);
      }
      const orders = ops.filter(op => op[0] === "order");
      rows.sort((a, b) => {
        for (const [, key] of orders) {
          const result = String(a[key]).localeCompare(String(b[key]));
          if (result) return result;
        }
        return 0;
      });
      for (const [op, a, b] of ops) {
        if (op === "range") rows = rows.slice(a, b + 1);
        if (op === "limit") rows = rows.slice(0, a);
      }
      return { data: rows, error: null };
    }).then(resolve, reject);
    return builder;
  }
  const exports = {};
  const dependencies = {
    "@/app/api/esat/qb/_server": {
      ESAT_TABLE_CANDIDATES: ["esat_qb_questions", "esat_questions"],
      adminClient: () => ({ from, auth: { admin: { listUsers: () => { throw new Error("Auth enumeration is forbidden"); } } } }),
      json: (data, status = 200) => Response.json(data, { status }),
    },
    "@/lib/server/esat-canonical-tests": canonical,
    "@/lib/server/esat-predictor-v1-engine": predictor,
    "@/lib/server/esat-predictor-evidence": evidence,
    "@/lib/server/esat-october-2026-tests": october,
    "@/lib/server/tmua-preparation-rank-v1-engine": preparation,
    "@/lib/auth/service-recovery": recovery,
    "@/lib/supabase/server": {
      createSupabaseServerClient: async () => ({ auth: { getUser: async () => ({ data: { user: state.user }, error: state.authError }) } }),
    },
  };
  vm.runInNewContext(compiled, {
    exports, require: name => {
      assert.ok(dependencies[name], `Unexpected dependency ${name}`);
      return dependencies[name];
    },
    Date: Clock, Response, console: { error: (...args) => errors.push(args) },
  });
  return { GET: exports.GET, state, tables, queries, snapshots, errors, advance: ms => { now += ms; } };
}
function expected(attemptRows, qb) {
  return predictor.calculateEsatPredictorV1({
    testAttempts: evidence.buildEsatTestEvidence(attemptRows),
    qbEvents: qb.map(row => {
      const q = questions.find(question => question.qid === row.metadata.canonical_qid);
      return {
        id: row.id, source: row.source, historyQuality: row.history_quality,
        predictorEligible: row.predictor_eligible, canonicalQid: q.qid, canonicalActive: true,
        selectedAnswer: row.selected_answer, canonicalAnswer: q.answer, canonicalTopic: q.topic,
        attemptedAt: row.attempted_at,
      };
    }),
    activeTopics: topics,
  });
}
function assertParity(body, result, snapshot) {
  for (const [out, field] of Object.entries({
    modelVersion: "modelVersion", status: "predictionStatus", score: "predictedEsatPracticeScore",
    lowerBound: "lowerBound", upperBound: "upperBound", confidence: "confidence",
    testEvidenceCount: "testEvidenceCount", independentTestCount: "independentTestCount",
    qbUniqueQuestions: "qbUniqueQuestions", qbTopicCoverage: "qbTopicCoverage",
  })) assert.deepEqual(body.predictor[out], result[field], `Exact prediction parity: ${out}`);
  assert.equal(snapshot.input_hash, result.inputHash, "All predictor input, calibration and canonical-topic hashes match");
  assert.equal(snapshot.test_weight, result.testWeight);
  assert.equal(snapshot.qb_weight, result.qbWeight);
  assert.equal(snapshot.test_signal_score9, result.testSignalPracticeScore);
  assert.equal(snapshot.qb_signal_score9, result.qbSignalScore9);
  assert.equal(body.preparationRank.rank, null, "Never fabricate a singleton rank");
  assert.equal(body.preparationRank.status, "temporarily_unavailable");
}

const h = harness();
const concurrent = await Promise.all(Array.from({ length: 8 }, () => h.GET()));
for (const response of concurrent) assert.equal(response.status, 200);
const bodyA = await concurrent[0].json();
assertParity(bodyA, expected(aAttempts, aQb), h.snapshots[0]);
assert.equal(h.queries.filter(q => q.table === "practice_test_attempts").length, 1, "Concurrent tabs share one current-user evidence read");
assert.equal(h.queries.filter(q => q.table === "tmua_qb_attempt_events").length, 1);
assert.equal(h.queries.filter(q => q.table === "esat_qb_questions").length, 1);
assert.equal(h.snapshots.length, 1, "Concurrent refreshes create one idempotent snapshot write");
assert.equal(h.queries.filter(q => q.table === "student_access").length, 8, "Do not cache authorization");
assert.ok(bodyA.preparationRank.score > 0, "Keep own preparation score and components");
assert.equal(bodyA.predictor.testEvidenceCount, aAttempts.length, "Every registered legacy/recall/October pathway remains evidence");
const queryCount = h.queries.length;
assert.equal((await h.GET()).status, 200);
assert.equal(h.queries.length, queryCount + 1, "Within30s only own entitlement is rechecked");
const emailPredicate = h.queries.find(q => q.table === "student_access").ops.find(op => op[0] === "ilike");
assert.equal(emailPredicate[2], "student\\_a@example.com", "LIKE wildcard in email is escaped");

h.state.user = users.b;
const responseB = await h.GET();
assert.equal(responseB.status, 200);
const bodyB = await responseB.json();
assertParity(bodyB, expected(bAttempts, bQb), h.snapshots[1]);
assert.notEqual(bodyA.predictor.score, bodyB.predictor.score, "Another student's cached score must never leak");
assert.equal(h.queries.filter(q => q.table === "esat_qb_questions").length, 1, "Only canonical metadata is shared between users");

h.state.user = users.a;
h.tables.student_access[0].approved = false;
assert.equal((await h.GET()).status, 403, "Revocation wins immediately over cached overview");
h.tables.student_access[0].approved = true;
h.tables.student_access[0].expires_at = "2026-09-20T16:29:59Z";
assert.equal((await h.GET()).status, 403, "Expired access is never served from cache");
h.tables.student_access[0].expires_at = null;
h.advance(31_000);
h.tables.practice_test_attempts.push(savedAttempt(users.a, "esat-mock-02", 27, "latest", "2026-09-20T16:30:15Z"));
assert.equal((await h.GET()).status, 200);
assert.equal(h.snapshots.length, 3, "New results refresh after bounded30s cache lifetime");
assert.notEqual(h.snapshots[2].input_hash, h.snapshots[0].input_hash);

for (const failTable of ["student_access", "practice_test_attempts", "tmua_qb_attempt_events", "esat_qb_questions"]) {
  const failed = harness({ failTable });
  const response = await failed.GET();
  assert.equal(response.status, 503, `${failTable} failure must be recoverable`);
  assert.equal(response.headers.get("Retry-After"), "30");
  assert.equal((await response.json()).retryable, true);
  assert.equal(failed.queries.filter(q => q.table === "esat_questions").length, 0, "Outage must not scan all aliases");
  failed.state.failTable = null;
  assert.equal((await failed.GET()).status, 200, "A failed in-flight calculation must be cleared for retry");
}
const transient = harness({ authError: { name: "AuthRetryableFetchError", status: 503 } });
assert.equal((await transient.GET()).status, 503, "Transient Auth errors are not missing sessions");
assert.equal(transient.queries.length, 0);
const signedOut = harness({ user: null, authError: { name: "AuthSessionMissingError" } });
assert.equal((await signedOut.GET()).status, 401);
assert.equal(signedOut.queries.length, 0);

const paginated = harness();
paginated.tables.tmua_qb_attempt_events = Array.from({ length: 1002 }, (_, i) => ({ ...aQb[i % aQb.length], id: `page-${String(i).padStart(5, "0")}` }));
const paginatedResponse = await paginated.GET();
assert.equal(paginatedResponse.status, 200);
assertParity(await paginatedResponse.json(), expected(aAttempts, paginated.tables.tmua_qb_attempt_events), paginated.snapshots[0]);
assert.equal(paginated.queries.filter(q => q.table === "tmua_qb_attempt_events").length, 2, "Keep evidence beyond the first page");
const overflow = harness();
overflow.tables.tmua_qb_attempt_events = Array.from({ length: 10_001 }, (_, i) => ({ ...aQb[i % aQb.length], id: `overflow-${String(i).padStart(5, "0")}` }));
assert.equal((await overflow.GET()).status, 503, "A safety cap must not publish a truncated prediction");
assert.equal(overflow.snapshots.length, 0);
assert.doesNotMatch(source, /readAuthUsers|listUsers|rankPreparationCohort/);
const strip = readFileSync("app/esat/EsatPredictionStrip.tsx", "utf8");
assert.match(strip, /Ranking is temporarily unavailable\. Your practice score still updates\./);
console.log("ESAT overview isolation verified: exact score/range/hash parity across all papers, current-user queries only, concurrent request coalescing, bounded caches, fresh entitlements, paginated evidence, no truncation, and retryable outages.");
