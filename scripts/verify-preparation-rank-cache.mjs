import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import ts from "typescript";

// Exercise the real cache coordinator, without credentials, student data or
// network calls. PostgreSQL lease/privacy contracts are also checked below.
const source = readFileSync("lib/server/preparation-rank-cache.ts", "utf8");
const compiled = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
}).outputText;
const sql = readFileSync("supabase/migrations/20261020090000_portal_preparation_rank_refresh.sql", "utf8");
const MODEL = {
  tmua: "tmua-preparation-rank-v1-20260810",
  esat: "esat-preparation-rank-v1-20260819",
};
const deferred = () => {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
};

function harness() {
  let now = Date.parse("2026-10-20T12:00:00Z");
  let sequence = 0;
  const state = {
    calls: [], workers: [], after: [], logs: [], runs: new Map(),
    coordination: new Map(), snapshots: new Map(),
    rpcErrors: new Map(), rpcThrows: new Map(), workerHooks: new Map(),
    finishFalse: false, missingRank: false,
  };
  class Clock extends Date {
    constructor(...args) { super(...(args.length ? args : [now])); }
    static now() { return now; }
  }
  const coordination = programme => {
    if (!state.coordination.has(programme)) state.coordination.set(programme, {
      token: null, leaseUntil: 0, nextAttempt: 0, refreshedAt: null, runId: null,
    });
    return state.coordination.get(programme);
  };
  async function execute(name, args) {
    if (state.rpcThrows.has(name)) throw state.rpcThrows.get(name);
    if (state.rpcErrors.has(name)) return { data: null, error: state.rpcErrors.get(name) };
    const item = coordination(args.p_programme);
    if (name === "read_portal_preparation_rank") {
      if (state.missingRank) return { data: null, error: null };
      const key = [args.p_programme, args.p_user_id, args.p_email].join(":");
      return { data: state.snapshots.get(key) ?? {
        modelVersion: MODEL[args.p_programme], status: "temporarily_unavailable",
        hasGenuinePreparationEvidence: false, score: null, rank: null,
        cohortSize: 0, components: null, calculatedAt: new Clock().toISOString(),
      }, error: null };
    }
    if (name === "claim_portal_rank_refresh") {
      if (item.leaseUntil > now || item.nextAttempt > now ||
          (item.refreshedAt !== null && item.refreshedAt > now - 30 * 60_000)) {
        return { data: null, error: null };
      }
      item.token = `lease-${++sequence}`;
      item.leaseUntil = now + 10 * 60_000;
      return { data: item.token, error: null };
    }
    if (name === "finish_portal_rank_refresh") {
      const run = state.runs.get(args.p_run_id);
      assert.ok(run?.complete, "Only a successfully completed worker run may be published");
      assert.equal(run.programme, args.p_programme, "Never publish another programme's cohort");
      if (state.finishFalse || item.token !== args.p_token) return { data: false, error: null };
      item.runId = args.p_run_id;
      item.refreshedAt = now;
      item.token = null;
      item.leaseUntil = 0;
      item.nextAttempt = 0;
      return { data: true, error: null };
    }
    if (name === "fail_portal_rank_refresh") {
      if (item.token === args.p_token) {
        item.token = null;
        item.leaseUntil = 0;
        item.nextAttempt = now + 5 * 60_000;
      }
      return { data: null, error: null };
    }
    throw new Error(`Unexpected RPC ${name}`);
  }
  const admin = { rpc(name, args) {
    const call = { name, args: structuredClone(args), retry: null };
    state.calls.push(call);
    return { retry(enabled) {
      assert.equal(enabled, false, "Database operations explicitly disable SDK retries");
      call.retry = enabled;
      return execute(name, args);
    } };
  } };
  const worker = programme => async receivedAdmin => {
    assert.equal(receivedAdmin, admin);
    state.workers.push(programme);
    const hook = state.workerHooks.get(programme);
    if (hook) await hook();
    const runId = `${programme}-run-${++sequence}`;
    state.runs.set(runId, { programme, complete: true });
    return { runId, cohortSize: programme === "tmua" ? 17 : 11,
      calculatedAt: new Clock().toISOString() };
  };
  const dependencies = {
    "next/server": { after: callback => state.after.push(callback) },
    "./tmua-preparation-rank-refresh": { refreshTmuaPreparationRank: worker("tmua") },
    "./esat-preparation-rank-refresh": { refreshEsatPreparationRank: worker("esat") },
  };
  const exports = {};
  vm.runInNewContext(compiled, {
    exports, Date: Clock,
    require: name => {
      assert.ok(dependencies[name], `Unexpected runtime dependency ${name}`);
      return dependencies[name];
    },
    console: { error: (...args) => state.logs.push(args), info: (...args) => state.logs.push(args) },
  });
  return { ...exports, state, admin, coordination, advance: ms => { now += ms; } };
}

// The page's response is not blocked by any cohort query. Next's post-response
// lifecycle owns the work and the database, not browser memory, owns the lease.
const background = harness();
assert.equal(background.requestPreparationRankRefresh(background.admin, "tmua"), undefined);
assert.equal(background.state.calls.length, 0);
assert.equal(background.state.workers.length, 0);
assert.equal(background.state.after.length, 1);
await background.state.after[0]();
assert.deepEqual(background.state.workers, ["tmua"]);
assert.ok(background.coordination("tmua").runId);

// Concurrent tabs/instances all claim through the same atomic database lease.
const concurrent = harness(), entered = deferred(), release = deferred();
concurrent.state.workerHooks.set("esat", async () => { entered.resolve(); await release.promise; });
const requests = Array.from({ length: 12 }, () => concurrent.refreshPreparationRankIfDue(concurrent.admin, "esat"));
await entered.promise;
assert.equal(concurrent.state.workers.length, 1);
assert.equal(concurrent.state.calls.some(call => call.name === "finish_portal_rank_refresh"), false,
  "A running worker must not advance the complete-run pointer");
release.resolve();
const results = await Promise.all(requests);
assert.equal(results.filter(result => result.refreshed).length, 1);
assert.equal((await concurrent.refreshPreparationRankIfDue(concurrent.admin, "esat")).refreshed, false,
  "Fresh snapshots do not trigger another cohort scan");
assert.equal(concurrent.state.workers.length, 1);
await concurrent.refreshPreparationRankIfDue(concurrent.admin, "tmua");
assert.deepEqual(concurrent.state.workers, ["esat", "tmua"], "Programmes have independent leases and workers");
concurrent.advance(30 * 60_000 + 1);
assert.equal((await concurrent.refreshPreparationRankIfDue(concurrent.admin, "esat")).refreshed, true);

// A failed refresh neither erases nor replaces the last complete cohort.
const failure = harness();
Object.assign(failure.coordination("tmua"), { runId: "old-complete", refreshedAt: Date.parse("2026-10-20T10:00:00Z") });
failure.state.workerHooks.set("tmua", async () => { throw new Error("fixture incomplete evidence"); });
await assert.rejects(failure.refreshPreparationRankIfDue(failure.admin, "tmua"), /incomplete evidence/);
assert.equal(failure.coordination("tmua").runId, "old-complete");
assert.equal(failure.coordination("tmua").refreshedAt, Date.parse("2026-10-20T10:00:00Z"));
assert.equal(failure.coordination("tmua").token, null);
assert.equal(failure.state.calls.some(call => call.name === "finish_portal_rank_refresh"), false);
assert.equal((await failure.refreshPreparationRankIfDue(failure.admin, "tmua")).refreshed, false,
  "Failures receive five-minute backoff");
failure.advance(5 * 60_000 + 1);
failure.state.workerHooks.delete("tmua");
assert.equal((await failure.refreshPreparationRankIfDue(failure.admin, "tmua")).refreshed, true);

// A late worker cannot overwrite the complete pointer or release a newer lease.
const late = harness(), lateEntered = deferred(), lateRelease = deferred();
Object.assign(late.coordination("esat"), { runId: "previous-esat-run" });
late.state.workerHooks.set("esat", async () => { lateEntered.resolve(); await lateRelease.promise; });
const lateJob = late.refreshPreparationRankIfDue(late.admin, "esat");
await lateEntered.promise;
late.coordination("esat").token = "newer-lease";
lateRelease.resolve();
await assert.rejects(lateJob, /lease expired/);
assert.equal(late.coordination("esat").runId, "previous-esat-run");
assert.equal(late.coordination("esat").token, "newer-lease");

// Completion RPC failure is also fail-closed; background failures are caught.
const completionFailure = harness();
completionFailure.state.rpcErrors.set("finish_portal_rank_refresh", new Error("completion unavailable"));
await assert.rejects(completionFailure.refreshPreparationRankIfDue(completionFailure.admin, "esat"), /completion unavailable/);
assert.equal(completionFailure.coordination("esat").runId, null);
assert.equal(completionFailure.coordination("esat").token, null);
const backgroundFailure = harness();
backgroundFailure.state.rpcErrors.set("claim_portal_rank_refresh", new Error("claim unavailable"));
backgroundFailure.requestPreparationRankRefresh(backgroundFailure.admin, "tmua");
await backgroundFailure.state.after[0]();
assert.equal(backgroundFailure.state.workers.length, 0);
assert.ok(backgroundFailure.state.logs.some(args => String(args[0]).includes("refresh failed")));

// If even lease release is offline, preserve the actual cause and rely on the
// bounded lease expiry; never clear the previous completed snapshot locally.
const releaseFailure = harness();
releaseFailure.coordination("tmua").runId = "last-good-run";
releaseFailure.state.workerHooks.set("tmua", async () => { throw new Error("original worker failure"); });
releaseFailure.state.rpcThrows.set("fail_portal_rank_refresh", new Error("lease release offline"));
await assert.rejects(releaseFailure.refreshPreparationRankIfDue(releaseFailure.admin, "tmua"), /original worker failure/);
assert.equal(releaseFailure.coordination("tmua").runId, "last-good-run");
assert.equal((await releaseFailure.refreshPreparationRankIfDue(releaseFailure.admin, "tmua")).refreshed, false);
releaseFailure.advance(10 * 60_000 + 1);
releaseFailure.state.workerHooks.delete("tmua");
releaseFailure.state.rpcThrows.delete("fail_portal_rank_refresh");
assert.equal((await releaseFailure.refreshPreparationRankIfDue(releaseFailure.admin, "tmua")).refreshed, true);

// The verified identity and programme are supplied on EVERY read, never kept
// in a shared cross-user cache or derived from browser request parameters.
const reads = harness();
const own = { modelVersion: MODEL.tmua, rank: 3, cohortSize: 17, score: 81 };
const other = { modelVersion: MODEL.esat, rank: 7, cohortSize: 11, score: 60 };
reads.state.snapshots.set("tmua:student-a:a@example.invalid", own);
reads.state.snapshots.set("esat:student-b:b@example.invalid", other);
assert.equal(await reads.readPreparationRankSnapshot(reads.admin, "student-a", "tmua", "a@example.invalid"), own);
assert.equal(await reads.readPreparationRankSnapshot(reads.admin, "student-b", "esat", "b@example.invalid"), other);
assert.equal((await reads.readPreparationRankSnapshot(reads.admin, "student-b", "tmua", "b@example.invalid")).rank, null);
await reads.readPreparationRankSnapshot(reads.admin, "student-a", "tmua", undefined);
assert.equal(reads.state.calls.at(-1).args.p_email, "", "Absent verified email fails closed");
for (const mode of ["rpc-error", "missing-row", "network-throw"]) {
  const broken = harness();
  if (mode === "rpc-error") broken.state.rpcErrors.set("read_portal_preparation_rank", new Error("fixture outage"));
  if (mode === "missing-row") broken.state.missingRank = true;
  if (mode === "network-throw") broken.state.rpcThrows.set("read_portal_preparation_rank", new Error("fixture network outage"));
  const rank = await broken.readPreparationRankSnapshot(broken.admin, "student-a", "esat", "a@example.invalid");
  assert.equal(rank.modelVersion, MODEL.esat);
  assert.equal(rank.status, "temporarily_unavailable");
  assert.equal(rank.hasGenuinePreparationEvidence, false);
  assert.equal(rank.rank, null); assert.equal(rank.score, null); assert.equal(rank.cohortSize, 0);
}

// Verify the actual SQL declarations behind the mock lease contract.
assert.match(sql, /alter table public\.portal_preparation_rank_refresh enable row level security/i);
assert.match(sql, /revoke all on public\.portal_preparation_rank_refresh from public, anon, authenticated, service_role;/);
assert.match(sql, /grant select, insert, update on public\.portal_preparation_rank_refresh to service_role;/);
assert.doesNotMatch(sql, /security\s+definer/i);
for (const signature of [
  "claim_portal_rank_refresh(text)", "finish_portal_rank_refresh(text,uuid,uuid)",
  "fail_portal_rank_refresh(text,uuid)", "read_portal_preparation_rank(text,uuid,text)",
]) {
  assert.ok(sql.includes(`revoke all on function public.${signature} from public,anon,authenticated;`), signature);
  assert.ok(sql.includes(`grant execute on function public.${signature} to service_role;`), signature);
}
assert.equal((sql.match(/security invoker set search_path = ''/g) ?? []).length, 4);
assert.match(sql, /lease_until <= now\(\) and next_attempt_at <= now\(\)/);
assert.match(sql, /refreshed_at <= now\(\) - interval '30 minutes'/);
assert.match(sql, /v_count <> v_run\.active_cohort_size then raise exception 'Incomplete ranking run'/);
assert.match(sql, /where programme = p_programme and lease_token = p_token/);
const failedSql = sql.slice(sql.indexOf("create function public.fail_portal_rank_refresh"), sql.indexOf("-- Invoked only"));
assert.match(failedSql, /interval '5 minutes'/);
assert.doesNotMatch(failedSql, /set\s+run_id|refreshed_at\s*=/);
assert.match(sql, /a\.approved is true/);
assert.match(sql, /a\.expires_at is null or a\.expires_at > now\(\)/);
assert.match(sql, /lower\(trim\(a\.email\)\) = lower\(trim\(p_email\)\)/);
assert.match(sql, /where run_id=v_state\.run_id and user_id=p_user_id and model_version=v_model/);
assert.match(sql, /v_state\.refreshed_at < now\(\) - interval '24 hours'/);
assert.doesNotMatch(sql, /grant\s+(?:all|execute).*?to\s+(?:anon|authenticated|public)/i);
console.log("Preparation-rank cache verified: nonblocking post-response work, atomic per-programme leases, no duplicate scans, complete-run publication, failure backoff/pointer preservation, stale-token safety, per-user verified identity, fail-closed reads, and service-role-only SQL boundaries.");
