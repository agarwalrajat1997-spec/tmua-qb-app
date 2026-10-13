// One campaign and one end instant across React, the API and static portal pages.
// Expiry is exclusive: the reminder runs through Friday, 16 October 2026 (IST).
export const TMUA_FINAL_REMINDER_CAMPAIGN_KEY = "tmua-final-warmup-2026-10-13";
export const TMUA_FINAL_REMINDER_START = "2026-10-13T00:00:00+05:30";
export const TMUA_FINAL_REMINDER_END = "2026-10-17T00:00:00+05:30";

export function isTmuaFinalReminderActive(now = Date.now()): boolean {
  return now >= Date.parse(TMUA_FINAL_REMINDER_START) && now < Date.parse(TMUA_FINAL_REMINDER_END);
}
