import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const popup = readFileSync(
  join(root, "app", "_components", "ErasableNotepadPopup.tsx"),
  "utf8",
);
const layout = readFileSync(join(root, "app", "layout.tsx"), "utf8");
const dashboardRouter = readFileSync(
  join(root, "app", "dashboard", "DashboardAccessRouterClient.tsx"),
  "utf8",
);

assert.match(popup, /erasable_notepad_promo_2026_09_29_30_dismissed/);
assert.match(popup, /2026-09-29T00:00:00\+05:30/);
assert.match(popup, /2026-10-01T00:00:00\+05:30/);
assert.match(popup, /now >= CAMPAIGN_START && now < CAMPAIGN_END/);
assert.match(popup, /window\.localStorage\.setItem/);
assert.match(popup, /Math\.ceil\(\(CAMPAIGN_END - Date\.now\(\)\) \/ 1000\)/);
assert.match(
  popup,
  /Max-Age=\$\{remainingSeconds\}; Domain=thrivingscholars\.com; Path=\/; SameSite=Lax; Secure/,
);
assert.match(popup, /<dialog/);
assert.match(popup, /onCancel=/);
assert.match(popup, /data-testid="erasable-notepad-popup"/);
assert.match(
  popup,
  /https:\/\/www\.thrivingscholars\.com\/tmua-esat-tara-erasable-practice-notepad/,
);
assert.match(popup, /erasable-practice-notepad-kit\.png/);
assert.match(popup, /erasable-practice-notepad-grid-pages\.png/);
assert.match(layout, /<ErasableNotepadPopup\s*\/>/);
assert.match(
  dashboardRouter,
  /state\.mode === "tmua"[\s\S]*?<ErasableNotepadPopup forcePortal\s*\/>/,
);

console.log("Erasable notepad popup verification passed.");
