import fs from "node:fs";
import assert from "node:assert/strict";


const banks = [
  [
    "TMUA",
    "public/tmua-question-bank/index.html",
  ],
  [
    "ESAT",
    "public/esat-question-bank/index.html",
  ],
];


function timerBlock(html, name) {

  const match =
    html.match(
      /<script id="ts-qb-question-timer-v1">([\s\S]*?)<\/script>/
    );

  assert.ok(
    match,
    `${name}: timer V1 script missing`,
  );

  return match[1];
}


for (const [name, file] of banks) {

  const html =
    fs.readFileSync(
      file,
      "utf8",
    );

  const timer =
    timerBlock(
      html,
      name,
    );


  /*
   * ============================================================
   * UI
   * ============================================================
   */

  assert.ok(
    html.includes(
      "#tsQuestionTimerValue"
    ),
    `${name}: timer value UI missing`,
  );


  assert.ok(
    html.includes(
      "font-weight: 900"
    ),
    `${name}: timer value is not bold`,
  );


  assert.ok(
    timer.includes("SHOW TIMER") &&
      timer.includes("HIDE") &&
      timer.includes("VISIBILITY_KEY"),
    `${name}: visibility-only toggle/persistence missing`,
  );


  /*
   * ============================================================
   * TIMESTAMP / ACCUMULATION MODEL
   * ============================================================
   */

  assert.ok(
    timer.includes("Date.now()") &&
      timer.includes("startedAtMs") &&
      timer.includes("accumulatedMs"),
    `${name}: timer is not timestamp + accumulation based`,
  );


  assert.ok(
    /function\s+currentElapsedMs\s*\(/.test(
      timer
    ),
    `${name}: elapsed-time calculation missing`,
  );


  /*
   * ============================================================
   * NAVIGATION PAUSE / RESUME
   *
   * Whitespace-independent.
   * ============================================================
   */

  assert.ok(
    /function\s+switchQuestion\s*\(\s*qid\s*\)/.test(
      timer
    ),
    `${name}: switchQuestion(qid) missing`,
  );


  assert.ok(
    /pauseQuestion\s*\(\s*activeQid\s*,\s*"navigate"\s*\)/.test(
      timer
    ),
    `${name}: outgoing question is not paused on navigation`,
  );


  assert.ok(
    /resumeQuestion\s*\(\s*qid\s*\)/.test(
      timer
    ),
    `${name}: incoming question is not resumed`,
  );


  assert.ok(
    /function\s+pauseQuestion[\s\S]*?entry\.accumulatedMs\s*=\s*currentElapsedMs\s*\(\s*entry\s*\)[\s\S]*?entry\.running\s*=\s*false[\s\S]*?entry\.startedAtMs\s*=\s*0/.test(
      timer
    ),
    `${name}: navigation pause does not preserve elapsed time`,
  );


  assert.ok(
    /function\s+resumeQuestion[\s\S]*?entry\.running\s*=\s*true[\s\S]*?entry\.startedAtMs\s*=\s*nowMs\s*\(\s*\)/.test(
      timer
    ),
    `${name}: question resume state machine missing`,
  );


  /*
   * ============================================================
   * UNANSWERED-PROGRESS PERSISTENCE
   * ============================================================
   */

  assert.ok(
    timer.includes(
      "localState.pendingMs"
    ) &&
      timer.includes(
        "localCheckpointIfNeeded"
      ) &&
      timer.includes(
        "5000"
      ),
    `${name}: unanswered refresh persistence missing`,
  );


  assert.ok(
    timer.includes(
      "persistPendingLocal"
    ),
    `${name}: local pending timer persistence missing`,
  );


  assert.ok(
    timer.includes(
      "checkpointUnattemptedToServer"
    ),
    `${name}: server unanswered checkpoint missing`,
  );


  assert.ok(
    timer.includes(
      "keepalive"
    ),
    `${name}: page-exit checkpoint keepalive missing`,
  );


  /*
   * ============================================================
   * SUBMISSION FREEZE
   * ============================================================
   */

  assert.ok(
    /function\s+freezeForSubmission[\s\S]*?entry\.running\s*=\s*false[\s\S]*?entry\.frozen\s*=\s*true/.test(
      timer
    ),
    `${name}: Check does not immediately freeze timer`,
  );


  assert.ok(
    /function\s+finalizeSubmission[\s\S]*?entry\.running\s*=\s*false[\s\S]*?entry\.frozen\s*=\s*true/.test(
      timer
    ),
    `${name}: completed submission does not remain frozen`,
  );


  /*
   * ============================================================
   * STOP-ON-CHECK HOTFIX
   * ============================================================
   */

  assert.ok(
    timer.includes(
      "TS_QB_TIMER_STOP_ON_CHECK_V1_FIX"
    ),
    `${name}: stop-on-Check hotfix missing`,
  );


  assert.ok(
    timer.includes(
      "settleSubmissionOutcome"
    ),
    `${name}: delayed submission-state settlement missing`,
  );


  /*
   * A successful submission is never allowed to call
   * resumeAfterFailedSubmission().
   *
   * Only two references should remain:
   *
   * 1. function declaration
   * 2. genuine catch(error) failure path
   */

  assert.equal(
    (
      timer.match(
        /resumeAfterFailedSubmission\s*\(/g
      ) || []
    ).length,
    2,
    `${name}: successful Check still has a timer-resume path`,
  );


  assert.ok(
    /catch\s*\(\s*error\s*\)[\s\S]{0,350}resumeAfterFailedSubmission\s*\(\s*qid\s*\)/.test(
      timer
    ),
    `${name}: real failed submission cannot resume timing`,
  );


  /*
   * ============================================================
   * CORRECT ANSWER
   *
   * THIS IS THE CURRENT V1 STORAGE MODEL:
   *
   * persistFinalLocal(...)
   * serverProgress[qid].time_spent = seconds
   * ============================================================
   */

  assert.ok(
    timer.includes(
      "persistFinalLocal"
    ),
    `${name}: correct-answer local final timer persistence missing`,
  );


  assert.ok(
    /serverProgress\[qid\]\.time_spent\s*=\s*seconds/.test(
      timer
    ),
    `${name}: correct-answer final timer is not persisted`,
  );


  assert.ok(
    /if\s*\(\s*status\s*===\s*"correct"\s*\)[\s\S]*?persistFinalLocal/.test(
      timer
    ) ||
    /function\s+finalizeSubmission[\s\S]*?persistFinalLocal/.test(
      timer
    ),
    `${name}: correct outcome is not connected to final timer persistence`,
  );


  /*
   * ============================================================
   * WRONG ANSWER
   *
   * Wrong attempt duration is evidence, but is not the
   * canonical final time for that question.
   * ============================================================
   */

  assert.ok(
    /serverProgress\[qid\]\.time_spent\s*=\s*null/.test(
      timer
    ),
    `${name}: wrong answer incorrectly retains canonical time_spent`,
  );


  assert.ok(
    timer.includes(
      "answer_elapsed_seconds"
    ),
    `${name}: per-attempt duration analytics missing`,
  );


  /*
   * ============================================================
   * WRONG RE-ATTEMPT
   * ============================================================
   */

  assert.ok(
    /function\s+resetWrongForImmediateRetry\s*\(\s*\)[\s\S]*?accumulatedMs\s*:\s*0/.test(
      timer
    ),
    `${name}: wrong re-attempt does not restart from 00:00`,
  );


  /*
   * ============================================================
   * CURRENT QUESTION SYNCHRONISATION
   * ============================================================
   */

  assert.ok(
    /function\s+syncCurrentQuestion\s*\(\s*\)/.test(
      timer
    ),
    `${name}: current-question synchronisation missing`,
  );


  /*
   * ============================================================
   * DISPLAY TICK
   *
   * Timer updates visually from timestamps; this must not imply
   * a database write every second.
   * ============================================================
   */

  assert.ok(
    timer.includes(
      "setInterval"
    ),
    `${name}: timer display tick missing`,
  );
}


console.log("");
console.log(
  "PASS: TMUA + ESAT per-question timer V1 semantic regressions."
);

console.log(
  "PASS: navigation preserves and resumes unanswered elapsed time."
);

console.log(
  "PASS: Check freezes immediately and successful submission cannot restart."
);

console.log(
  "PASS: correct time persists permanently."
);

console.log(
  "PASS: incorrect attempt freezes; canonical time remains empty."
);

console.log(
  "PASS: wrong re-attempt begins from 00:00."
);

console.log(
  "PASS: attempt duration remains available for analytics/predictor evidence."
);