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

for (const [name, file] of banks) {

  const html =
    fs.readFileSync(file, "utf8");

  const match =
    html.match(
      /<script id="ts-qb-question-timer-v1">([\s\S]*?)<\/script>/
    );

  assert.ok(
    match,
    `${name}: timer V1 script missing`
  );

  const timer =
    match[1];

  assert.ok(
    timer.includes(
      "TS_QB_TIMER_STOP_ON_CHECK_V1_FIX"
    ),
    `${name}: stop-on-Check hotfix missing`
  );

  assert.ok(
    timer.includes(
      "settleSubmissionOutcome"
    ),
    `${name}: outcome settlement missing`
  );

  /*
   * PRESS CHECK
   *
   * Timer must immediately become:
   *
   * running = false
   * frozen  = true
   */
  assert.ok(
    /function freezeForSubmission[\s\S]*?entry\.running\s*=\s*false[\s\S]*?entry\.frozen\s*=\s*true/.test(
      timer
    ),
    `${name}: Check does not immediately freeze timer`
  );

  /*
   * After the hotfix, resumeAfterFailedSubmission()
   * may occur only:
   *
   * 1. function declaration
   * 2. genuine catch(error) path
   *
   * It must NEVER be part of a successful Check fallback.
   */
  assert.equal(
    (
      timer.match(
        /resumeAfterFailedSubmission\s*\(/g
      ) || []
    ).length,
    2,
    `${name}: successful Check still has a timer restart path`
  );

  assert.ok(
    /catch \(error\)[\s\S]{0,300}resumeAfterFailedSubmission\s*\(\s*qid\s*\)/.test(
      timer
    ),
    `${name}: genuine failed submission resume path missing`
  );

  /*
   * Correct answer:
   * frozen final question time is retained.
   */
  assert.ok(
    timer.includes(
      "persistFinalLocal"
    ),
    `${name}: correct final timer persistence missing`
  );

  assert.ok(
    /serverProgress\[qid\]\.time_spent\s*=\s*seconds/.test(
      timer
    ),
    `${name}: correct time_spent persistence missing`
  );

  /*
   * Wrong answer:
   * this attempt freezes, but canonical question
   * time remains empty.
   */
  assert.ok(
    /serverProgress\[qid\]\.time_spent\s*=\s*null/.test(
      timer
    ),
    `${name}: incorrect attempt incorrectly retains final time`
  );

  /*
   * New retry after wrong answer starts from zero.
   */
  assert.ok(
    /function resetWrongForImmediateRetry\(\)[\s\S]*?accumulatedMs:\s*0/.test(
      timer
    ),
    `${name}: incorrect retry does not restart from 00:00`
  );

  /*
   * Individual attempt duration still available
   * for analytics / predictor evidence.
   */
  assert.ok(
    timer.includes(
      "answer_elapsed_seconds"
    ),
    `${name}: attempt-duration analytics missing`
  );
}

console.log("");
console.log(
  "PASS: TMUA + ESAT stop the timer after every completed Check."
);
console.log(
  "Correct -> final time persists."
);
console.log(
  "Incorrect -> attempt freezes; next retry begins at 00:00."
);
console.log(
  "Actual submission error -> timer may resume."
);