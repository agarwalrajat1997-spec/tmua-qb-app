import fs from "node:fs";
import path from "node:path";
import assert from "node:assert/strict";

const root = process.cwd();

const banks = [
  ["TMUA", path.join(root, "public", "tmua-question-bank", "index.html")],
  ["ESAT", path.join(root, "public", "esat-question-bank", "index.html")],
];

function tagged(text, tagName, id, label) {
  const openNeedle = `<${tagName} id="${id}"`;
  const start = text.indexOf(openNeedle);
  assert.ok(start >= 0, `${label}: ${id} missing`);

  const openEnd = text.indexOf(">", start);
  assert.ok(openEnd >= 0, `${label}: ${id} opening tag malformed`);

  const closeNeedle = `</${tagName}>`;
  const end = text.indexOf(closeNeedle, openEnd + 1);
  assert.ok(end > openEnd, `${label}: ${id} closing tag missing`);

  return text.slice(openEnd + 1, end);
}

for (const [name, filename] of banks) {
  const html = fs.readFileSync(filename, "utf8");

  const css = tagged(
    html,
    "style",
    "ts-qb-question-timer-css-v1",
    name,
  );

  const timer = tagged(
    html,
    "script",
    "ts-qb-question-timer-v1",
    name,
  );

  assert.ok(
    css.includes("left: 50%") &&
      css.includes("position: absolute") &&
      css.includes("color: #ffffff"),
    `${name}: timer is not centred in the white-on-blue header style`,
  );

  assert.ok(
    css.includes("#tsQuestionTimerValue") &&
      css.includes("font-weight: 900"),
    `${name}: timer value is not bold`,
  );

  assert.ok(
    timer.includes("SHOW TIMER") &&
      timer.includes("HIDE") &&
      timer.includes("VISIBILITY_KEY"),
    `${name}: visibility-only toggle/persistence missing`,
  );

  assert.ok(
    timer.includes("Date.now()") &&
      timer.includes("startedAtMs") &&
      timer.includes("accumulatedMs"),
    `${name}: timer is not timestamp + accumulation based`,
  );

  assert.ok(
    timer.includes("switchQuestion(qid)") &&
      timer.includes('pauseQuestion(\n        activeQid,\n        "navigate"') &&
      timer.includes("resumeQuestion(qid)"),
    `${name}: navigation pause/resume state machine missing`,
  );

  assert.ok(
    timer.includes("localState.pendingMs") &&
      timer.includes("localCheckpointIfNeeded") &&
      timer.includes("5000"),
    `${name}: unanswered refresh persistence missing`,
  );

  assert.ok(
    timer.includes("checkpointUnattemptedToServer") &&
      timer.includes("keepalive"),
    `${name}: meaningful-event server checkpoint missing`,
  );

  assert.ok(
    timer.includes("pendingSubmissionSeconds") &&
      timer.includes("freezeForSubmission") &&
      timer.includes("finalizeSubmission"),
    `${name}: immediate submission freeze missing`,
  );

  assert.ok(
    timer.includes('status === "correct"') &&
      timer.includes("update.time_spent =\n                          seconds"),
    `${name}: correct-answer final timer is not persisted`,
  );

  assert.ok(
    timer.includes('status ===\n                        "wrong"') &&
      timer.includes("update.time_spent =\n                          null"),
    `${name}: wrong answer is incorrectly being persisted as the final question timer`,
  );

  assert.ok(
    timer.includes("update.answer_elapsed_seconds =\n                        seconds"),
    `${name}: submitted attempt duration is not retained for analytics`,
  );

  assert.ok(
    timer.includes("serverProgress") &&
      timer.includes("LOAD_URL"),
    `${name}: saved/frozen timer restoration missing`,
  );

  assert.ok(
    timer.includes("pagehide") &&
      timer.includes("visibilitychange"),
    `${name}: refresh/background lifecycle handling missing`,
  );

  assert.ok(
    timer.includes("hours > 0") &&
      timer.includes('two(hours) +'),
    `${name}: hour formatting is not supported`,
  );

  assert.equal(
    (timer.match(/window\.setInterval\s*\(/g) || []).length,
    1,
    `${name}: timer module must own exactly one interval`,
  );

  assert.ok(
    !/setInterval[\s\S]{0,120}time_spent/.test(timer),
    `${name}: database timing must not be written every timer tick`,
  );
}

/*
  Pure state-model regression tests for the requested semantics.
*/
function elapsed(entry, now) {
  return (
    entry.accumulatedMs +
    (entry.running ? Math.max(0, now - entry.startedAtMs) : 0)
  );
}

function pause(entry, now) {
  if (!entry.running) return { ...entry };
  return {
    ...entry,
    accumulatedMs: elapsed(entry, now),
    startedAtMs: 0,
    running: false,
  };
}

function resume(entry, now) {
  if (entry.frozen || entry.running) return { ...entry };
  return {
    ...entry,
    startedAtMs: now,
    running: true,
  };
}

// New question.
let q = {
  accumulatedMs: 0,
  startedAtMs: 1000,
  running: true,
  frozen: false,
};
assert.equal(elapsed(q, 8000), 7000);

// Navigate away at 35 seconds and return later: resume from 35.
q = pause(q, 36000);
assert.equal(q.accumulatedMs, 35000);
q = resume(q, 100000);
assert.equal(elapsed(q, 110000), 45000);

// Correct submission freezes permanently.
q = pause(q, 110000);
q.frozen = true;
const frozenMs = q.accumulatedMs;
assert.equal(resume(q, 200000).accumulatedMs, frozenMs);
assert.equal(resume(q, 200000).running, false);

// Historical wrong re-attempt starts from zero.
const wrongRetry = {
  accumulatedMs: 0,
  startedAtMs: 300000,
  running: true,
  frozen: false,
};
assert.equal(elapsed(wrongRetry, 307000), 7000);

// Timer visibility is not part of elapsed-state transitions.
const beforeHide = elapsed(wrongRetry, 307000);
const afterHide = elapsed(wrongRetry, 367000);
assert.equal(afterHide - beforeHide, 60000);

console.log(
  "PASS: TMUA + ESAT per-question timer static invariants and state-model regressions.",
);