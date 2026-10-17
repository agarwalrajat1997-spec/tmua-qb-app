import assert from "node:assert/strict";
import {
  JANUARY_EXAM_DATE,
  JANUARY_EXAM_DATE_LABEL,
  JANUARY_EXAM_TIMESTAMP,
  getRemainingExamSeconds,
  splitCountdownSeconds,
} from "../lib/exam-countdown.ts";

assert.equal(JANUARY_EXAM_DATE, "2027-01-04");
assert.equal(JANUARY_EXAM_DATE_LABEL, "4 January 2027");
assert.equal(JANUARY_EXAM_TIMESTAMP, Date.UTC(2027, 0, 4));

const countdownAt = (instant) =>
  splitCountdownSeconds(getRemainingExamSeconds(Date.parse(instant)));

assert.deepEqual(countdownAt("2027-01-02T22:57:56Z"), {
  days: 1, hours: 1, minutes: 2, seconds: 4,
});
assert.deepEqual(countdownAt("2027-01-03T00:00:00Z"), {
  days: 1, hours: 0, minutes: 0, seconds: 0,
});
assert.deepEqual(countdownAt("2027-01-03T00:00:01Z"), {
  days: 0, hours: 23, minutes: 59, seconds: 59,
});
assert.deepEqual(countdownAt("2027-01-03T23:59:00Z"), {
  days: 0, hours: 0, minutes: 1, seconds: 0,
});
assert.deepEqual(countdownAt("2027-01-03T23:59:01Z"), {
  days: 0, hours: 0, minutes: 0, seconds: 59,
});
assert.equal(getRemainingExamSeconds(JANUARY_EXAM_TIMESTAMP - 1), 1);
assert.equal(getRemainingExamSeconds(JANUARY_EXAM_TIMESTAMP), 0);
assert.equal(getRemainingExamSeconds(JANUARY_EXAM_TIMESTAMP + 86400000), 0);

// Local time-zone representations must all resolve to the same UK deadline.
for (const instant of [
  "2027-01-04T05:30:00+05:30",
  "2027-01-03T16:00:00-08:00",
  "2027-01-04T11:00:00+11:00",
]) {
  assert.equal(getRemainingExamSeconds(Date.parse(instant)), 0);
}

console.log("January countdown: deadline, rollovers, expiry and time zones passed.");
