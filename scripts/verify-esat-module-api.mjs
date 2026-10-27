import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import ts from "typescript";
import * as predictor from "../lib/server/esat-module-predictor.ts";
import * as policy from "../lib/esat-predictions.ts";
import * as canonical from "../lib/server/esat-canonical-tests.ts";

function load(path, dependencies) {
  const compiled = ts.transpileModule(fs.readFileSync(path, "utf8"), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } }).outputText;
  const exports = {};
  vm.runInNewContext(compiled, { exports, require: name => { assert.ok(dependencies[name], name); return dependencies[name]; }, Response, Date, console });
  return exports;
}
const service = load("lib/server/esat-module-prediction-service.ts", {
  "./esat-canonical-tests.ts": canonical, "./esat-module-predictor.ts": predictor, "../esat-predictions.ts": policy,
});
function harness({ signedIn = true, access = true, failEvidence = false } = {}) {
  const calls = [];
  const test = canonical.getCanonicalEsatTest("esat-chemistry-biology-level-0");
  const admin = {
    from(table) {
      assert.ok(["student_access", "practice_test_attempts", "esat_qb_questions", "tmua_qb_attempt_events"].includes(table), "No exam plan, lock, result or other student data may be accessed");
      const operations = [];
      const builder = {};
      for (const method of ["select", "ilike", "in", "eq", "or", "limit", "retry", "lte", "order", "range"]) builder[method] = (...args) => { operations.push([method, ...args]); return builder; };
      builder.then = resolve => {
        calls.push({ table, operations });
        const data = table === "student_access" ? (access ? [{ product: "esat-question-bank" }] : [])
          : table === "practice_test_attempts" ? [{ id: "attempt-1", test_id: test.testId, answers: [...test.answers], submitted_at: "2026-09-01T00:00:00Z" }] : [];
        return Promise.resolve({ data, error: failEvidence && table === "practice_test_attempts" ? new Error("Evidence unavailable") : null }).then(resolve);
      };
      return builder;
    },
    rpc() { assert.fail("No locking or persistence RPC is allowed"); },
  };
  const route = load("app/api/esat/module-predictions/route.ts", {
    "@/app/api/esat/qb/_server": { adminClient: () => admin, json: (body, status = 200) => Response.json(body, { status }) },
    "@/lib/supabase/server": { createSupabaseServerClient: async () => ({ auth: { getUser: async () => ({ data: { user: signedIn ? { id: "verified-user", email: "student_a@example.com" } : null }, error: null }) } }) },
    "@/lib/auth/service-recovery": { isMissingSession: () => false, withServiceTimeout: promise => promise },
    "@/lib/server/esat-module-prediction-service": service,
  });
  return { ...route, calls };
}
assert.equal((await harness({ signedIn: false }).GET()).status, 401);
assert.equal((await harness({ access: false }).GET()).status, 403);
const valid = harness();
const response = await valid.GET();
assert.equal(response.status, 200);
const body = await response.json();
assert.deepEqual(body.pathway, { status: "inferred", modules: ["Mathematics 1", "Chemistry", "Biology"] });
assert.ok(body.predictions.every(item => item.score !== null && item.confidence === "low"));
assert.equal(body.plan, undefined); assert.equal(body.locked, undefined);
assert.ok(body.predictions.every(item => item.guaranteeEligible === undefined));
for (const table of ["practice_test_attempts", "tmua_qb_attempt_events"]) {
  assert.ok(valid.calls.find(call => call.table === table).operations.some(op => op[0] === "eq" && op[1] === "user_id" && op[2] === "verified-user"));
}
assert.ok(valid.calls.find(call => call.table === "student_access").operations.some(op => op[0] === "ilike" && op[2] === "student\\_a@example.com"));
assert.equal(valid.PUT, undefined); assert.equal(valid.POST, undefined);
assert.equal((await harness({ failEvidence: true }).GET()).status, 503);
console.log("PASS: read-only module API, verified identity/access, pathway inference without setup, no locking/writes, and evidence failures.");
