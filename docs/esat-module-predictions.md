# ESAT module predictions and guarantee

The ESAT dashboard asks the student to save their booked exam date and three
modules: Mathematics 1 plus two of Mathematics 2, Physics, Chemistry and Biology.
Each selected module gets its own score, likely range, confidence and evidence
counts. The previous combined model remains internal to preparation ranking.
TMUA is unchanged.

## Evidence

Recognised tests are rescored from canonical answers and converted separately
for each module. Existing extra-time adjustments apply separately to each module.
Repeated source papers across pathways share an evidence family. Question-bank
questions are selected using the canonical paper field, not user-supplied labels.
Unknown modules never contribute to another subject. Each module independently
uses the existing confidence and high-score evidence rules: question-bank
contributions begin at 30 eligible unique questions; recognised tests can
produce a prediction independently. Scores below 3.5 remain in the building state.

Scores are saved to one decimal place, matching the displayed values and the
official-result comparison. Confidence is based on evidence, not score bands.

## Locking

The lock is at midnight Europe/London two calendar days before the booked date.
This is a calendar-date policy, with British summer time handled explicitly.
The latest server-saved dashboard snapshot before the cutoff is frozen, including
its confidence levels, evidence timestamp, model version and guarantee policy.
The dashboard saves on load, focus and once a minute while visible. It displays
the evidence save time. This is the latest saved prediction, not a retrospective
reconstruction using later evidence or revised calibration.

The database's `esat-lock-module-predictions` cron runs every minute, including
when the student is offline. Reads and writes also enforce the cutoff. An
in-flight prediction cannot overwrite a lock. Locks are immutable and retained
by student and exam date. Missing predictions lock as unavailable and cannot
qualify retrospectively. New exam settings cannot replace a locked sitting
before that sitting has passed. A later sitting retains earlier locked records.

## Guarantee score condition

For each of the three booked modules, compare the official result with the
locked displayed prediction. A module counts as a miss only when:

- Its locked confidence was Medium or High and it had a numerical prediction.
- Its official result is **more than 0.5** below that prediction.

Two or three qualifying misses meet the score condition for a full refund to the
original payment method. Exactly 0.5 is not a miss. Low confidence and building
states do not count. Strong results in another module do not offset a miss.

The results form stores self-reported module scores and a provisional assessment.
Official results, booked modules/date and purchase eligibility require verification.
No refund or payment is executed by these endpoints.

## Storage and verification

`esat_exam_plans` contains the current booking and latest predictions.
`esat_prediction_locks` contains immutable sitting-specific snapshots.
`esat_result_submissions` contains submitted results and their assessment.
RLS allows students to read only their own records; all writes use the server,
verified session identity and ESAT entitlements. Public/authenticated RPC execution
and direct client writes are revoked.

Run `npm run verify:esat-module-predictions` for module isolation, duplicate-paper
handling, extra time, DST dates, guarantee boundaries and authenticated API tests.
The SQL regression runs in a transaction and rolls back all test records.
