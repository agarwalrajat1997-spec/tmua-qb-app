// January is GMT in the UK. Keep an explicit offset so every time zone counts
// down to the same instant, rather than midnight on the student's device.
export const JANUARY_EXAM_DATE = "2027-01-04";
export const JANUARY_EXAM_DATE_LABEL = "4 January 2027";
export const JANUARY_EXAM_TIMESTAMP = Date.parse("2027-01-04T00:00:00+00:00");

export function getRemainingExamSeconds(now = Date.now()): number {
  return Math.max(0, Math.ceil((JANUARY_EXAM_TIMESTAMP - now) / 1000));
}

export function splitCountdownSeconds(totalSeconds: number) {
  return {
    days: Math.floor(totalSeconds / 86400),
    hours: Math.floor((totalSeconds % 86400) / 3600),
    minutes: Math.floor((totalSeconds % 3600) / 60),
    seconds: totalSeconds % 60,
  };
}
