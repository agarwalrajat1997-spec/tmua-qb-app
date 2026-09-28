import assert from "node:assert/strict";
import { mkdirSync } from "node:fs";
import { join } from "node:path";
import { chromium } from "playwright";

const baseUrl = process.env.POPUP_TEST_BASE_URL || "http://127.0.0.1:3107";
const outputDir = join(process.cwd(), "tmp", "erasable-notepad-popup-check");
mkdirSync(outputDir, { recursive: true });

const executableCandidates = [
  "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
];

let browser;
let lastLaunchError;

for (const executablePath of executableCandidates) {
  try {
    browser = await chromium.launch({ executablePath, headless: true });
    break;
  } catch (error) {
    lastLaunchError = error;
  }
}

if (!browser) throw lastLaunchError || new Error("No supported browser found.");

const context = await browser.newContext({ viewport: { width: 1440, height: 960 } });
const page = await context.newPage();
const errors = [];

page.on("pageerror", (error) => errors.push(`pageerror: ${error.message}`));
page.on("console", (message) => {
  if (message.type() === "error") errors.push(`console: ${message.text()}`);
});

async function clearDismissal() {
  await page.evaluate(() => {
    localStorage.removeItem("erasable_notepad_promo_dismissed");
    document.cookie =
      "erasable_notepad_promo_dismissed=; Max-Age=0; Path=/; SameSite=Lax";
  });
}

async function popupCount() {
  return page.locator('[data-testid="erasable-notepad-popup"]').count();
}

try {
  await page.goto(`${baseUrl}/login?next=/dashboard`, { waitUntil: "networkidle" });
  await clearDismissal();
  await page.reload({ waitUntil: "networkidle" });

  const popup = page.locator('[data-testid="erasable-notepad-popup"]');
  await popup.waitFor({ state: "visible" });
  await page.getByRole("heading", {
    name: "Make the working surface familiar before test day.",
  }).waitFor();

  const imageResults = await popup.locator("img").evaluateAll((images) =>
    images.map((image) => ({
      complete: image.complete,
      width: image.naturalWidth,
      height: image.naturalHeight,
    })),
  );
  assert.equal(imageResults.length, 2);
  assert.ok(imageResults.every((image) => image.complete && image.width > 0));
  assert.equal(
    await page.locator("[data-nextjs-dialog], .vite-error-overlay").count(),
    0,
  );
  await page.screenshot({
    path: join(outputDir, "desktop.png"),
    fullPage: true,
  });

  await page.getByRole("button", {
    name: "Close and do not show this again",
  }).click();
  assert.equal(
    await page.evaluate(() =>
      localStorage.getItem("erasable_notepad_promo_dismissed"),
    ),
    "1",
  );

  await page.reload({ waitUntil: "networkidle" });
  assert.equal(await popupCount(), 0);

  await page.goto(`${baseUrl}/login?next=/esat`, { waitUntil: "networkidle" });
  assert.equal(await popupCount(), 0);

  await clearDismissal();
  await page.reload({ waitUntil: "networkidle" });
  await page.locator('[data-testid="erasable-notepad-popup"]').waitFor({
    state: "visible",
  });

  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({
    path: join(outputDir, "mobile.png"),
    fullPage: true,
  });
  await page.keyboard.press("Escape");
  assert.equal(await popupCount(), 0);

  await page.goto(`${baseUrl}/sat-login`, { waitUntil: "networkidle" });
  assert.equal(await popupCount(), 0);

  assert.deepEqual(errors, []);
  console.log(
    `Popup browser verification passed. Screenshots: ${outputDir}`,
  );
} finally {
  await browser.close();
}
