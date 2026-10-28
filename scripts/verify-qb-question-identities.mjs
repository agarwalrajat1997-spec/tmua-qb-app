import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import { canonicalQuestionState } from "../lib/qb/question-identities.ts";

const oldId = "TMUA-\u004a\u005a-A-P1-Q17";
const newId = "TMUA-TS-A-P1-Q17";
const attempt = { selected: "B", correct: true, seconds: 72, at: "2026-10-27T12:00:00Z" };
const state = { answers: { [oldId]: attempt }, flagged: [oldId], owner: "student-a", submission_id: `attempt:${oldId}:123` };
const expected = { answers: { [newId]: attempt }, flagged: [newId], owner: "student-a", submission_id: `attempt:${newId}:123` };
assert.deepEqual(canonicalQuestionState(state), expected);
assert.deepEqual(state.answers[oldId], attempt, "original payload remains intact");
assert.deepEqual(canonicalQuestionState({ [oldId]: "older", [newId]: "newer" }), { [newId]: "newer" });
assert.equal(canonicalQuestionState("1700"), "1700");
assert.equal(canonicalQuestionState("7cfb77dd-1b0b-46af-bba8-339d39b599ed"), "7cfb77dd-1b0b-46af-bba8-339d39b599ed");
assert.deepEqual(canonicalQuestionState(canonicalQuestionState(state)), expected);

const data = new Map([
  ["ts_esat_supabase_exact_ui_v1:student-a", JSON.stringify(state)],
  ["ts_qb_submission_outbox_v3:student-a", JSON.stringify({ owner: "student-a", updates: [state] })],
  ["sb-auth-token", JSON.stringify({ token: oldId })],
  ["unrelated", oldId],
  ["ts_esat_invalid", `{${oldId}`],
]);
const storage = {
  get length() { return data.size; }, key: i => [...data.keys()][i],
  getItem: key => data.get(key) ?? null, setItem: (key, value) => data.set(key, value),
};
const context = { window: { localStorage: storage } };
vm.runInNewContext(fs.readFileSync("public/qb-question-identities.js", "utf8"), context);
assert.deepEqual(JSON.parse(data.get("ts_esat_supabase_exact_ui_v1:student-a")), expected);
assert.deepEqual(JSON.parse(data.get("ts_qb_submission_outbox_v3:student-a")), { owner: "student-a", updates: [expected] });
assert.equal(JSON.parse(data.get("sb-auth-token")).token, oldId);
assert.equal(data.get("unrelated"), oldId);
assert.equal(data.get("ts_esat_invalid"), `{${oldId}`);
assert.deepEqual(JSON.parse(JSON.stringify(context.window.TSQuestionIdentities.normalize(state))), expected);
console.log("Question identity migration: answers, account ownership, timers, collisions and queued writes passed.");
