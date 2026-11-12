import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import ts from "typescript";

// Execute the actual route without credentials, student data or network access.
// A production saved read must work even when maintenance has no admin key.
const source = readFileSync("app/api/tmua/overview/route.ts", "utf8");
const compiled = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
}).outputText;
const user = { id: "student-a", email: "a@example.invalid" };
const saved = {
  ok: true,
  viewerId: user.id,
  predictor: {
    modelVersion: "saved-predictor-fixture", status: "predicted", score: 6.4,
    lowerBound: 5.9, upperBound: 6.9, confidence: "medium",
    testEvidenceCount: 3, independentTestCount: 2,
    qbUniqueQuestions: 318, qbTopicCoverage: 0.8,
    calculatedAt: "2026-11-12T00:00:00Z",
  },
  preparationRank: { rank: 8, score: 81, cohortSize: 125 },
};

function harness(options = {}) {
  const state = { authCalls: 0, rpcCalls: [], adminCalls: 0, refreshes: [], tableReads: [], logs: [] };
  const admin = {
    from(table) {
      state.tableReads.push(table);
      throw new Error("Authoritative evidence unavailable in saved-read fixture");
    },
  };
  const supabase = {
    auth: { async getUser() {
      state.authCalls += 1;
      return { data: { user: options.user === undefined ? user : options.user }, error: options.authError ?? null };
    } },
    rpc(name, ...args) {
      const call = { name, args, retry: null };
      state.rpcCalls.push(call);
      return { retry(enabled) {
        call.retry = enabled;
        if (options.rpcThrow) return Promise.reject(new Error("Saved RPC unavailable"));
        return Promise.resolve({
          data: options.saved === undefined ? saved : options.saved,
          error: options.rpcError ?? null,
        });
      } };
    },
  };
  const dependencies = {
    "@/lib/exam-countdown": {
      JANUARY_EXAM_DATE: "2027-01-04", JANUARY_EXAM_DATE_LABEL: "4 January 2027",
      JANUARY_EXAM_TIMESTAMP: Date.parse("2027-01-04T00:00:00Z"),
    },
    "next/server": { NextResponse: { json: (body, { status, headers }) => ({ status, headers, body }) } },
    "@supabase/supabase-js": { createClient() {
      state.adminCalls += 1;
      if (options.adminThrow) throw new Error("Admin client unavailable");
      return admin;
    } },
    "@/lib/supabase/server": { createSupabaseServerClient: async () => supabase },
    "@/lib/auth/service-recovery": {
      withServiceTimeout: async value => await value,
      isMissingSession: error => error?.name === "AuthSessionMissingError",
      serviceFetch() { throw new Error("No network expected"); },
    },
    "@/lib/server/preparation-rank-cache": {
      requestPreparationRankRefresh(receivedAdmin, programme) {
        assert.equal(receivedAdmin, admin);
        state.refreshes.push(programme);
        if (options.refreshThrow) throw new Error("Post-response scheduling unavailable");
      },
      readPreparationRankSnapshot() { throw new Error("Saved read must use the caller-bound overview RPC"); },
    },
  };
  // These algorithms are exercised by their existing dedicated verifiers.
  for (const module of [
    "tmua-predictor-v1-evidence-adapter", "tmua-predictor-v1-engine", "tmua-predictor-v1_1-policy",
    "practice-predictor-overlay", "tmua-predictive-2026", "tmua-predictor-v1-snapshot",
  ]) dependencies[`@/lib/server/${module}`] = {};
  const module = { exports: {} };
  vm.runInNewContext(compiled, {
    module, exports: module.exports, URL, Date, Intl,
    process: { env: { VERCEL: "1", NEXT_PUBLIC_SUPABASE_URL: "https://fixture.invalid", ...options.env } },
    console: { error: (...args) => state.logs.push(args) },
    require(name) {
      assert.ok(dependencies[name], `Unexpected route dependency: ${name}`);
      return dependencies[name];
    },
  });
  return {
    state,
    run: (query = "") => module.exports.GET({ url: `https://fixture.invalid/api/tmua/overview${query}` }),
  };
}

const withoutAdmin = harness();
const response = await withoutAdmin.run();
assert.equal(response.status, 200, "Missing maintenance credentials must not block a saved overview");
assert.equal(response.body.viewerId, user.id);
assert.equal(response.body.predictor, saved.predictor, "Preserve the saved predictor, bounds and confidence exactly");
assert.equal(response.body.preparationRank, saved.preparationRank, "Preparation score and predicted TMUA score stay distinct");
assert.equal(response.body.countdown.examDate, "2027-01-04");
assert.match(response.headers["Cache-Control"], /no-store/);
assert.equal(withoutAdmin.state.authCalls, 1);
assert.equal(withoutAdmin.state.rpcCalls.length, 1);
assert.equal(withoutAdmin.state.rpcCalls[0].name, "get_my_tmua_overview");
assert.equal(withoutAdmin.state.rpcCalls[0].args.length, 0, "No client-supplied identity is passed to the RPC");
assert.equal(withoutAdmin.state.rpcCalls[0].retry, false);
assert.equal(withoutAdmin.state.adminCalls, 0);
assert.equal(withoutAdmin.state.refreshes.length, 0);
assert.equal(withoutAdmin.state.tableReads.length, 0);

const noEvidence = harness({ saved: { ...saved, predictor: { ...saved.predictor, status: "insufficient_evidence", score: null } } });
assert.equal((await noEvidence.run()).body.predictor.score, null, "Missing evidence must not become a synthetic zero score");

const adminEnv = { SUPABASE_SERVICE_ROLE_KEY: "fixture-service-key" };
for (const options of [{}, { refreshThrow: true }, { adminThrow: true }]) {
  const available = harness({ env: adminEnv, ...options });
  const result = await available.run();
  assert.equal(result.status, 200, "Maintenance failures must not change a successful saved response");
  assert.equal(result.body.predictor, saved.predictor);
  assert.equal(available.state.adminCalls, 1);
  assert.equal(available.state.refreshes.length, options.adminThrow ? 0 : 1);
  assert.equal(available.state.tableReads.length, 0, "No evidence/cohort scans run during a saved read");
}

for (const options of [
  { user: null },
  { user: null, authError: { name: "AuthSessionMissingError" } },
  { authError: { name: "AuthServiceUnavailable" } },
]) {
  const unauthenticated = harness(options);
  assert.equal((await unauthenticated.run()).status, options.authError?.name === "AuthServiceUnavailable" ? 503 : 401);
  assert.equal(unauthenticated.state.rpcCalls.length, 0);
  assert.equal(unauthenticated.state.adminCalls, 0);
}
const changed = harness();
assert.equal((await changed.run("?expectedUserId=student-b")).status, 409);
assert.equal(changed.state.rpcCalls.length, 0, "Reject changed accounts before any snapshot lookup");

for (const options of [
  { saved: { ...saved, viewerId: "student-b" } },
  { saved: { ...saved, ok: false } },
  { saved: { ...saved, predictor: null } },
  { saved: { ...saved, predictor: [] } },
  { saved: null },
  { rpcError: { message: "Database unavailable" } },
  { rpcThrow: true },
]) {
  const failed = harness({ env: adminEnv, ...options });
  const result = await failed.run();
  assert.equal(result.status, 503, "Bad or unavailable saved data fails closed");
  assert.equal(result.body.ok, false);
  assert.equal(result.body.predictor, undefined, "Never leak another user's predictor");
  assert.equal(result.headers["Retry-After"], "30");
  assert.equal(failed.state.adminCalls, 0);
  assert.equal(failed.state.tableReads.length, 0, "A failed RPC must not trigger an expensive live fallback");
}

for (const env of [{ VERCEL: "" }, { TMUA_OVERVIEW_FORCE_LIVE: "1" }]) {
  const needsAdmin = harness({ env });
  assert.equal((await needsAdmin.run()).status, 500, "Full calculation still requires service-role credentials");
  assert.equal(needsAdmin.state.rpcCalls.length, 0, "Live mode must not substitute the saved overview");

  const live = harness({ env: { ...adminEnv, ...env } });
  assert.equal((await live.run()).status, 500, "Fixture deliberately stops when authoritative evidence is requested");
  assert.equal(live.state.rpcCalls.length, 0);
  assert.equal(live.state.adminCalls, 1);
  assert.ok(live.state.tableReads.includes("tmua_qb_questions"), "Full mode still enters the authoritative evidence path");
}

console.log("TMUA saved-overview route verified: key-independent bounded reads, authenticated ownership, preserved predictor values, no synthetic zero, noncritical maintenance, fail-closed RPC errors, and unchanged live-mode authority.");
