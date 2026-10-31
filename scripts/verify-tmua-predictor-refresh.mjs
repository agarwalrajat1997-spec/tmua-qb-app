import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import { createRequire } from "node:module";

// Execute the production component/controller with a controlled clock and fetch.
// No Supabase calls, real browser sessions, snapshots or network requests.
const require = createRequire(import.meta.url);
const ts = require("typescript");
const source = fs.readFileSync("app/dashboard/TmuaPredictionStrip.tsx", "utf8");
let effect;
const stateWrites = [];
const module = { exports: {} };
const context = vm.createContext({
  module, exports: module.exports, console, AbortController,
  require(id) {
    if (id === "react") return { useEffect(fn) { effect = fn; }, useState(value) { return [value, next => stateWrites.push(next)]; }, useId: () => "qa-id" };
    if (id === "react/jsx-runtime") return require(id);
    if (id.endsWith(".module.css")) return {};
    if (id === "@/app/_components/ExamCountdown") return () => null;
    throw new Error(`Unexpected component dependency: ${id}`);
  },
});
vm.runInContext(ts.transpileModule(source, { compilerOptions: {
  target: ts.ScriptTarget.ES2020, module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX,
} }).outputText, context);
const createController = module.exports.createTmuaOverviewRefresh;
assert.equal(typeof createController, "function");
const flush = async () => { for (let i = 0; i < 10; i++) await Promise.resolve(); };
const body = (viewerId = "viewer-a", score = 5) => ({ ok: true, viewerId, predictor: { status: "predicted", score } });

function fixture() {
  let now = 0, sequence = 0, settled = 0;
  const timers = new Map(), requests = [], displayed = [];
  const clock = {
    schedule(callback, delay) { const id = ++sequence; timers.set(id, { at: now + delay, callback }); return id; },
    cancel(id) { timers.delete(id); },
    now: () => now,
    tick(ms) {
      const until = now + ms;
      let count = 0;
      while (true) {
        const next = [...timers.entries()].filter(([, t]) => t.at <= until).sort((a, b) => a[1].at - b[1].at)[0];
        if (!next) break;
        assert(++count < 100, "Refresh must never poll in a timer loop");
        now = next[1].at; timers.delete(next[0]); next[1].callback();
      }
      now = until;
    },
  };
  const fetcher = (url, options) => new Promise((resolve, reject) => requests.push({ url, options, resolve, reject }));
  const controller = createController({ ...clock, fetcher, onOverview: value => displayed.push(value), onSettled: () => settled++ });
  return {
    controller, clock, fetcher, requests, displayed, timers,
    settled: () => settled,
    async respond(index, value = body(), status = 200) { requests[index].resolve({ ok: status >= 200 && status < 300, status, json: async () => value }); await flush(); },
    async tick(ms) { clock.tick(ms); await flush(); },
  };
}
async function loaded() { const h = fixture(); h.controller.start(); await h.respond(0); return h; }
let scenarios = 0;

for (const failure of [500, "network"]) {
  const h = fixture(); h.controller.start();
  if (failure === "network") { h.requests[0].reject(new Error("Offline")); await flush(); }
  else await h.respond(0, { ok: false }, failure);
  h.controller.saved({ viewerId: "viewer-a", submissionId: "retry-after-initial-failure" });
  await h.tick(500); assert.equal(h.requests.length, 2, "A new saved answer retries a failed initial read");
  assert.equal(h.requests[1].url, "/api/tmua/overview", "Unverified event owner cannot become expectedUserId");
  await h.respond(1, body("viewer-a", 5.4));
  assert.equal(h.displayed.at(-1).predictor.score, 5.4, "A read started after the save can display immediately");
  await h.tick(1000); assert.equal(h.requests.length, 2, "Recovery must not trigger a redundant third read");
  scenarios++;
}

for (const firstReadFailure of [500, "timeout"]) {
  const h = fixture(); h.controller.start();
  h.controller.saved({ viewerId: "viewer-a", submissionId: `saved-during-initial-${firstReadFailure}` });
  await h.tick(500);
  if (firstReadFailure === "timeout") await h.tick(29_500);
  else await h.respond(0, { ok: false }, firstReadFailure);
  await h.tick(0);
  assert.equal(h.requests.length, 2, "An unverified save is not lost when the in-flight initial read fails");
  assert.equal(h.requests[1].url, "/api/tmua/overview", "Queued event never supplies an unverified owner");
  await h.respond(1, body("viewer-a", 5.5));
  assert.equal(h.displayed.at(-1).predictor.score, 5.5);
  await h.tick(60_000); assert.equal(h.requests.length, 2, "Only the pending saved answer causes a follow-up");
  scenarios++;
}

for (const stalledPart of ["fetch", "body"]) {
  const h = await loaded();
  h.controller.saved({ viewerId: "viewer-a", submissionId: `start-stalled-${stalledPart}` }); await h.tick(500);
  let resolveBody;
  if (stalledPart === "body") {
    h.requests[1].resolve({ ok: true, status: 200, json: () => new Promise(resolve => { resolveBody = resolve; }) });
    await flush();
  }
  h.controller.saved({ viewerId: "viewer-a", submissionId: `saved-during-stalled-${stalledPart}` });
  await h.tick(30_000);
  assert.equal(h.requests[1].options.signal.aborted, true, `${stalledPart} deadline aborts request`);
  assert.equal(h.displayed.at(-1).predictor.score, 5, "Deadline retains last verified score");
  await h.tick(0); assert.equal(h.requests.length, 3, "One pending saved answer gets a fresh request after deadline");
  await h.respond(2, body("viewer-a", 5.7));
  if (stalledPart === "body") { resolveBody(body("viewer-a", 3)); await flush(); }
  else await h.respond(1, body("viewer-a", 3));
  assert.equal(h.displayed.at(-1).predictor.score, 5.7, "Late timed-out completion cannot overwrite fresh result");
  assert.equal(h.timers.size, 0, "Successful request clears its deadline");
  scenarios++;
}
{
  const h = fixture(); h.controller.start();
  await h.tick(30_000); await h.tick(60_000);
  assert.equal(h.requests.length, 1, "A deadline without a pending action does not auto-retry");
  assert.equal(h.timers.size, 0);
  h.controller.saved({ viewerId: "viewer-a", submissionId: "fresh-save-after-timeout" });
  await h.tick(500); await h.respond(1, body("viewer-a", 5.6));
  assert.equal(h.displayed.at(-1).predictor.score, 5.6);
  scenarios++;
}

{
  const h = await loaded();
  assert.equal(h.requests[0].url, "/api/tmua/overview");
  assert.equal(h.requests[0].options.cache, "no-store");
  assert.equal(h.requests[0].options.credentials, "same-origin");
  h.controller.saved({ viewerId: "viewer-a", submissionId: "new-answer-1" });
  await h.tick(499); assert.equal(h.requests.length, 1);
  await h.tick(1); assert.equal(h.requests.length, 2);
  assert.equal(h.requests[1].url, "/api/tmua/overview?expectedUserId=viewer-a");
  await h.respond(1, body("viewer-a", 5.1));
  assert.equal(h.displayed.at(-1).predictor.score, 5.1);
  scenarios++;
}
{
  const h = await loaded();
  for (const submissionId of ["one", "two", "three", "three"]) h.controller.saved({ viewerId: "viewer-a", submissionId });
  await h.tick(500); assert.equal(h.requests.length, 2, "Burst/replay must coalesce");
  await h.respond(1);
  h.controller.saved({ viewerId: "viewer-a", submissionId: "three" });
  await h.tick(60_000); assert.equal(h.requests.length, 2, "No polling or duplicate refresh");
  scenarios++;
}
{
  const h = fixture(); h.controller.start();
  h.controller.saved({ viewerId: "viewer-a", submissionId: "during-first-read" });
  await h.respond(0, body("viewer-a", 4));
  assert.equal(h.displayed.length, 0, "Initial response before saved answer must not overwrite newer evidence");
  await h.tick(500); assert.equal(h.requests.length, 2);
  await h.respond(1, body("viewer-a", 5));
  assert.equal(h.displayed.at(-1).predictor.score, 5);
  scenarios++;
}
{
  const h = await loaded();
  h.controller.saved({ viewerId: "viewer-a", submissionId: "first" }); await h.tick(500);
  h.controller.saved({ viewerId: "viewer-a", submissionId: "second" }); await h.tick(500);
  assert.equal(h.requests.length, 2, "Only one read may be in flight");
  await h.respond(1, body("viewer-a", 4));
  assert.equal(h.displayed.at(-1).predictor.score, 5, "Stale in-flight read cannot overwrite display");
  await h.tick(0); assert.equal(h.requests.length, 3, "Saved answer during request gets one follow-up");
  await h.respond(2, body("viewer-a", 5.2));
  assert.equal(h.displayed.at(-1).predictor.score, 5.2);
  scenarios++;
}
{
  const h = await loaded();
  h.controller.saved({ viewerId: "viewer-b", submissionId: "not-this-account" });
  h.controller.saved({ viewerId: "viewer-a" });
  h.controller.saved(null);
  await h.tick(1000); assert.equal(h.requests.length, 1, "Wrong-account/malformed events ignored");
  scenarios++;
}
{
  const h = fixture(); h.controller.start();
  h.controller.saved({ viewerId: "viewer-b", submissionId: "before-owner-known" });
  await h.respond(0, body("viewer-a")); await h.tick(1000);
  assert.equal(h.requests.length, 1); assert.equal(h.displayed.at(-1).viewerId, "viewer-a");
  scenarios++;
}
for (const status of [401, 403, 409]) {
  const h = await loaded();
  h.controller.saved({ viewerId: "viewer-a", submissionId: "after-account-change" }); await h.tick(500);
  await h.respond(1, { ok: false, code: "ACCOUNT_CHANGED" }, status);
  assert.equal(h.displayed.at(-1), null, `HTTP${status} clears old account's display`);
  h.controller.saved({ viewerId: "viewer-a", submissionId: "blocked" });
  await h.tick(30_000); h.controller.refresh(); await h.tick(500);
  assert.equal(h.requests.length, 2, "Account boundary needs remount, not blind retries");
  scenarios++;
}
{
  const h = await loaded();
  h.controller.saved({ viewerId: "viewer-a", submissionId: "owner-response-check" }); await h.tick(500);
  await h.respond(1, body("viewer-b", 8));
  assert.equal(h.displayed.at(-1), null, "A different response owner never reaches the display");
  scenarios++;
}
{
  const h = await loaded();
  h.controller.saved({ viewerId: "viewer-a", submissionId: "temporary-error" }); await h.tick(500);
  await h.respond(1, { ok: false }, 503);
  assert.equal(h.displayed.at(-1).predictor.score, 5, "Temporary service failure keeps verified overview");
  await h.tick(60_000); assert.equal(h.requests.length, 2, "No automatic retries on503");
  h.controller.refresh(); h.controller.refresh(); await h.tick(500); assert.equal(h.requests.length, 3);
  await h.respond(2, body("viewer-a", 5.3));
  h.controller.refresh(); await h.tick(500); assert.equal(h.requests.length, 3, "Focus/visibility pair is throttled");
  scenarios++;
}
{
  const h = await loaded();
  h.controller.saved({ viewerId: "viewer-a", submissionId: "unmount-pending" });
  h.controller.dispose(); await h.tick(1000);
  assert.equal(h.requests.length, 1); assert.equal(h.timers.size, 0);
  const active = fixture(); active.controller.start(); active.controller.dispose();
  assert.equal(active.requests[0].options.signal.aborted, true); assert.equal(active.timers.size, 0, "Unmount clears deadline timer");
  await active.respond(0);
  assert.equal(active.displayed.length, 0); assert.equal(active.settled(), 0);
  scenarios++;
}
{
  class Target {
    listeners = new Map();
    addEventListener(name, fn) { this.listeners.set(name, fn); }
    removeEventListener(name, fn) { assert.equal(this.listeners.get(name), fn); this.listeners.delete(name); }
    dispatch(name, detail) { this.listeners.get(name)?.({ detail }); }
  }
  const h = fixture(), win = new Target(), doc = new Target(); doc.hidden = false;
  win.setTimeout = h.clock.schedule; win.clearTimeout = h.clock.cancel;
  context.window = win; context.document = doc; context.fetch = h.fetcher;
  context.Date = { now: h.clock.now };
  module.exports.default(); const cleanup = effect();
  await h.respond(0);
  assert.equal(win.listeners.size, 2); assert.equal(doc.listeners.size, 1);
  win.dispatch("ts-tmua-attempt-saved", { viewerId: "viewer-a", submissionId: "actual-hook-save" });
  await h.tick(500); assert.equal(h.requests.length, 2, "Actual hook wires saved event into controller");
  await h.respond(1);
  await h.tick(15_000); doc.hidden = true; doc.dispatch("visibilitychange"); win.dispatch("focus");
  await h.tick(500); assert.equal(h.requests.length, 2, "Hidden tab does not refresh");
  doc.hidden = false; doc.dispatch("visibilitychange"); win.dispatch("focus");
  await h.tick(500); assert.equal(h.requests.length, 3);
  cleanup(); await h.respond(2);
  assert.equal(win.listeners.size, 0); assert.equal(doc.listeners.size, 0);
  scenarios++;
}
console.log(`PASS TMUA predictor refresh: ${scenarios} actual-controller/hook scenarios; owner-scoped saves, debounce, in-flight updates, stale response rejection, auth boundaries, focus/visibility, temporary failures, stalled fetch/body deadlines and unmount cleanup. No network or real records.`);
