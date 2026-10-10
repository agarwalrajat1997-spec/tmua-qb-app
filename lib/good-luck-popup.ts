// Keep this key stable: a receipt suppresses the message in BOTH portals forever.
export const GOOD_LUCK_CAMPAIGN_KEY = "pre-exam-good-luck-2026-10-10";
// Saturday 10 October, in the owner's account timezone (Asia/Kolkata).
export const GOOD_LUCK_START = Date.parse("2026-10-10T00:00:00+05:30");
export const GOOD_LUCK_END = Date.parse("2026-10-11T00:00:00+05:30");

export function isGoodLuckCampaignActive(now = Date.now()) {
  return now >= GOOD_LUCK_START && now < GOOD_LUCK_END;
}
