import assert from "node:assert/strict";
import { existsSync, mkdtempSync, readFileSync } from "node:fs";
import { createServer } from "node:http";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

// Serve real reminder assets locally; all API requests use synthetic receipts.
// No student sessions, external services or live database writes are involved.
const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const outputDir = mkdtempSync(join(tmpdir(), "esat-final-reminder-ui-"));
const API = "/api/student/esat-final-reminder";
const TMUA_API = "/api/student/tmua-final-reminder";
const PDF = "/esat-resources/esat-2026-extra-practice-pack.pdf";
const KEY = "esat-final-warmup-2026-10-14";
const TMUA_KEY = "tmua-final-warmup-2026-10-13";
const NOW = "2026-10-14T12:00:00+05:30";
const START = "2026-10-14T00:00:00+05:30";
const END = "2026-10-17T00:00:00+05:30";
const SELECTOR = "dialog.ts-final-reminder";
const errors = [];
let pdfRequests = 0;

const server = createServer((request, response) => {
  const url = new URL(request.url, "http://127.0.0.1");
  response.setHeader("Cache-Control", "no-store");
  if (["/esat-final-reminder.js", "/tmua-final-reminder.js", "/tmua-final-reminder.css"].includes(url.pathname)) {
    response.setHeader("Content-Type", url.pathname.endsWith(".js") ? "text/javascript" : "text/css");
    response.end(readFileSync(join(root, "public", url.pathname.slice(1))));
    return;
  }
  if (url.pathname === PDF) {
    pdfRequests += 1;
    response.setHeader("Content-Type", "application/pdf");
    const actualPdf = join(root, "public", PDF.slice(1));
    response.end(existsSync(actualPdf) ? readFileSync(actualPdf) : "%PDF-1.4\n%%EOF\n");
    return;
  }
  if ([API, TMUA_API].includes(url.pathname)) {
    response.writeHead(500, { "Content-Type": "application/json" });
    response.end(JSON.stringify({ error: "Every API call must be intercepted by the test." }));
    return;
  }
  const audience = url.searchParams.get("fixtureAudience") === "1" ? " data-esat-reminder-audience" : "";
  const iframe = url.pathname === "/fixture-frame-host" ? '<iframe title="ESAT embedded fixture" src="/esat-question-bank/index.html"></iframe>' : "";
  const both = url.searchParams.has("both") ? '<script src="/tmua-final-reminder.js" defer></script>' : "";
  response.setHeader("Content-Type", "text/html; charset=utf-8");
  response.end(`<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Reminder isolated fixture</title><style>body{margin:0;background:#eef1f5;font-family:Arial,sans-serif}main{padding:24px}button{font:inherit}iframe{width:90vw;height:400px}</style></head><body><main${audience}><h1>ESAT fixture</h1><button id="return-focus" autofocus>Continue studying</button>${iframe}</main><script src="/esat-final-reminder.js" defer></script>${both}</body></html>`);
});
await new Promise((resolveListen, reject) => {
  server.once("error", reject);
  server.listen(0, "127.0.0.1", resolveListen);
});
const baseUrl = `http://127.0.0.1:${server.address().port}`;
const executablePath = [process.env.ESAT_REMINDER_CHROME, "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe", "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"].find((candidate) => candidate && existsSync(candidate));
let browser;

async function fixture({ authenticated = true, receipt = { dismissed: false }, tmuaReceipt = { dismissed: false }, date = NOW, viewport = { width: 1440, height: 1000 }, runningClock = false, failedPosts = 0, postDelay = 0 } = {}) {
  const context = await browser.newContext({ viewport });
  const calls = { gets: 0, posts: 0, bodies: [], tmuaGets: 0, tmuaPosts: 0 };
  await context.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (["chrome-extension:", "chrome:", "data:", "blob:"].includes(url.protocol)) { await route.continue(); return; }
    if (url.origin !== baseUrl) { errors.push(`Unexpected external request: ${url.href}`); await route.abort(); return; }
    if (![API, TMUA_API].includes(url.pathname)) { await route.continue(); return; }
    const tmua = url.pathname === TMUA_API;
    const currentReceipt = tmua ? tmuaReceipt : receipt;
    if (route.request().method() === "POST") {
      if (tmua) calls.tmuaPosts += 1;
      else { calls.posts += 1; calls.bodies.push(route.request().postDataJSON()); }
      if (postDelay) await new Promise((resolveDelay) => setTimeout(resolveDelay, postDelay));
      if (!tmua && failedPosts > 0) { failedPosts -= 1; await route.fulfill({ status: 503, json: { dismissed: false } }); return; }
      if (authenticated) currentReceipt.dismissed = true;
      await route.fulfill({ status: authenticated ? 200 : 401, json: { dismissed: authenticated } });
    } else {
      if (tmua) calls.tmuaGets += 1; else calls.gets += 1;
      await route.fulfill({ status: authenticated ? 200 : 401, json: { active: true, authenticated, dismissed: currentReceipt.dismissed, show: !currentReceipt.dismissed } });
    }
  });
  const page = await context.newPage();
  page.on("pageerror", (error) => errors.push(error.message));
  if (runningClock) await page.clock.install({ time: new Date(date) });
  else await page.clock.setFixedTime(new Date(date));
  async function goto(path) { await page.goto(`${baseUrl}${path}`, { waitUntil: "load" }); }
  async function visible() {
    await page.locator(SELECTOR).waitFor({ state: "visible", timeout: 7000 });
    assert.equal(await page.locator(`${SELECTOR}[open]`).count(), 1, "One accessible modal must be open");
    assert.match(await page.locator(".ts-final-brand").textContent(), /ESAT/);
  }
  async function absent(delay = 1200) { await page.waitForTimeout(delay); assert.equal(await page.locator(SELECTOR).count(), 0, `Reminder must stay absent at ${page.url()}`); }
  return { context, page, calls, goto, visible, absent, close: () => context.close() };
}
async function test(name, run) { await run(); console.log(`PASS ${name}`); }

try {
  browser = await chromium.launch({ ...(executablePath ? { executablePath } : {}), headless: true });
  await test("authenticated PDF viewing preserves reminder; explicit dismissal persists across visits and devices", async () => {
    const receipt = { dismissed: false };
    const f = await fixture({ receipt, postDelay: 150 });
    try {
      await f.goto("/esat?fixtureAudience=1"); await f.visible();
      assert.equal(f.calls.posts, 0);
      const pdf = f.page.locator(".ts-final-pdf");
      assert.equal(await pdf.getAttribute("href"), PDF);
      assert.equal(await pdf.getAttribute("target"), "_blank");
      assert.match(await pdf.getAttribute("rel"), /noopener/);
      const before = pdfRequests;
      const popupPromise = f.context.waitForEvent("page");
      await pdf.click(); const pdfPage = await popupPromise;
      await f.page.waitForTimeout(300); assert.ok(pdfRequests > before);
      await pdfPage.close(); await f.page.bringToFront(); await f.visible();
      assert.equal(f.calls.posts, 0, "PDF viewing is not dismissal");
      assert.equal(await f.page.evaluate((key) => localStorage.getItem(key), KEY), null);
      await f.page.screenshot({ path: join(outputDir, "desktop.png"), fullPage: true });
      await f.page.locator(".ts-final-dismiss").click(); await f.absent(500);
      assert.equal(f.calls.posts, 1); assert.deepEqual(f.calls.bodies, [{ action: "dismiss" }]);
      assert.equal(await f.page.evaluate((key) => localStorage.getItem(key), KEY), "dismissed");
      assert.equal(await f.page.evaluate((key) => localStorage.getItem(`${key}-pending`), KEY), null);
      assert.equal(await f.page.locator("#return-focus").evaluate((el) => el === document.activeElement), true);
      await f.page.reload({ waitUntil: "load" }); await f.absent(); assert.equal(f.calls.posts, 1);
      const anotherDevice = await fixture({ receipt });
      try { await anotherDevice.goto("/esat-question-bank"); await anotherDevice.absent(); assert.ok(anotherDevice.calls.gets > 0); assert.equal(anotherDevice.calls.posts, 0); }
      finally { await anotherDevice.close(); }
    } finally { await f.close(); }
  });

  await test("anonymous Escape dismissal survives refresh without any account write", async () => {
    const f = await fixture({ authenticated: false });
    try {
      await f.goto("/login?next=%2Fesat"); await f.visible(); await f.page.keyboard.press("Escape"); await f.absent(200);
      assert.equal(f.calls.posts, 0); assert.equal(await f.page.evaluate((key) => localStorage.getItem(key), KEY), "dismissed");
      await f.page.reload({ waitUntil: "load" }); await f.absent(); assert.equal(f.calls.posts, 0);
    } finally { await f.close(); }
  });

  await test("failed receipt save closes locally and retries when online without reopening", async () => {
    const f = await fixture({ failedPosts: 1 });
    try {
      await f.goto("/esat-question-bank"); await f.visible(); await f.page.locator(".ts-final-close").click(); await f.absent(500);
      assert.equal(f.calls.posts, 1); assert.equal(await f.page.evaluate((key) => localStorage.getItem(`${key}-pending`), KEY), "1");
      await f.page.evaluate(() => window.dispatchEvent(new Event("online"))); await f.absent(1500);
      assert.equal(f.calls.posts, 2); assert.equal(await f.page.evaluate((key) => localStorage.getItem(`${key}-pending`), KEY), null);
    } finally { await f.close(); }
  });

  const eligibleRoutes = ["/esat", "/esat/", "/esat?section=bank", "/esat-login", "/esat-question-bank", "/esat-question-bank/", "/esat-question-bank/index.html", "/esat-practice-tests", "/esat-classes", "/esat-classes/index.html", "/login?next=%2Fesat", "/login?next=%2Fesat-question-bank", "/login?next=%2Fesat-question-bank%2Findex.html", "/login?next=%2Fesat-practice-tests"];
  await test(`all ${eligibleRoutes.length} intended ESAT landing variants show`, async () => {
    for (let i = 0; i < eligibleRoutes.length; i += 4) await Promise.all(eligibleRoutes.slice(i, i + 4).map(async (path) => {
      const f = await fixture(); try { await f.goto(path); await f.visible(); } finally { await f.close(); }
    }));
  });
  const excludedRoutes = ["/", "/dashboard", "/dashboard?view=esat", "/dashboard?view=esat&fixtureAudience=1", "/login", "/login?next=%2Fdashboard", "/login?next=%2Fdashboard%3Fview%3Desat", "/tmua", "/tmua-question-bank", "/practice-tests", "/tmua-classes", "/sat", "/sat-login", "/sat-question-bank", "/amc", "/amc-login", "/amc-question-bank", "/pending", "/esat-practice-tests/tests/esat-mock-01/index.html", "/esat-practice-tests/tests/esat-october-2026-engineering/index.html", "/esat-question-bank-unrelated", "/esat-classes/unknown", "/esat-resources/example.pdf", "/login?next=%2Ftmua-question-bank", "/login?next=%2Fsat-question-bank", "/login?next=%2Famc-question-bank", "/login?next=%2Fesat-practice-tests%2Ftests%2Fesat-mock-01%2Findex.html", "/login?next=https%3A%2F%2Fforeign.invalid%2Fesat", "/login?next=%2F%2Fforeign.invalid%2Fesat", "/login?next=javascript%3Aalert(1)", "/login?next=http%3A%2F%2F%5B"];
  await test(`all ${excludedRoutes.length} non-ESAT, unconfirmed, timed-test and unsafe-next routes stay untouched`, async () => {
    for (let i = 0; i < excludedRoutes.length; i += 4) await Promise.all(excludedRoutes.slice(i, i + 4).map(async (path) => {
      const f = await fixture(); try { await f.goto(path); await f.absent(); assert.equal(f.calls.gets, 0, path); } finally { await f.close(); }
    }));
  });

  await test("ESAT route changes show the reminder; leaving ESAT hides without dismissal", async () => {
    const f = await fixture();
    try {
      await f.goto("/dashboard"); await f.absent();
      await f.page.evaluate(() => { history.pushState({}, "", "/esat"); window.dispatchEvent(new Event("esat-reminder-route")); });
      await f.visible();
      await f.page.evaluate(() => { history.pushState({}, "", "/tmua-question-bank"); window.dispatchEvent(new Event("esat-reminder-route")); });
      await f.absent(100); assert.equal(f.calls.posts, 0);
    } finally { await f.close(); }
  });

  await test("TMUA and ESAT campaigns have independent dismissal keys and route audiences", async () => {
    for (const dismissFirst of ["tmua", "esat"]) {
      const f = await fixture();
      try {
        await f.goto(dismissFirst === "tmua" ? "/tmua-question-bank?both=1" : "/esat-question-bank?both=1");
        await f.page.locator(SELECTOR).waitFor({ state: "visible" });
        assert.match(await f.page.locator(".ts-final-brand").textContent(), dismissFirst === "tmua" ? /TMUA/ : /ESAT/);
        assert.equal(dismissFirst === "tmua" ? f.calls.gets : f.calls.tmuaGets, 0);
        await f.page.locator(".ts-final-dismiss").click(); await f.absent(300);
        assert.equal(await f.page.evaluate((key) => localStorage.getItem(key), dismissFirst === "tmua" ? KEY : TMUA_KEY), null);
        await f.goto(dismissFirst === "tmua" ? "/esat-question-bank?both=1" : "/tmua-question-bank?both=1");
        await f.page.locator(SELECTOR).waitFor({ state: "visible" });
        assert.equal(await f.page.locator(SELECTOR).count(), 1);
        assert.match(await f.page.locator(".ts-final-brand").textContent(), dismissFirst === "tmua" ? /ESAT/ : /TMUA/);
      } finally { await f.close(); }
    }
  });

  await test("nested ESAT frames cannot produce duplicate reminders", async () => {
    const f = await fixture();
    try { await f.goto("/fixture-frame-host"); await f.absent(); assert.equal(await f.page.frameLocator("iframe").locator(SELECTOR).count(), 0); assert.equal(f.calls.gets, 0); }
    finally { await f.close(); }
  });
  await test("pre-campaign and expired visits stay hidden", async () => {
    for (const date of [new Date(Date.parse(START) - 1).toISOString(), END, "2026-10-18T12:00:00+05:30"]) {
      const f = await fixture({ date });
      try { await f.goto("/esat-question-bank"); await f.absent(); assert.equal(f.calls.gets, 0); } finally { await f.close(); }
    }
  });
  await test("an open popup closes automatically at the expiry boundary", async () => {
    const f = await fixture({ date: new Date(Date.parse(END) - 10000).toISOString(), runningClock: true });
    try { await f.goto("/esat-question-bank"); await f.visible(); await f.page.clock.fastForward(11000); await f.absent(50); assert.equal(f.calls.posts, 0); }
    finally { await f.close(); }
  });
  await test("existing portal dialogs keep priority", async () => {
    const f = await fixture();
    try {
      await f.goto("/esat-question-bank");
      await f.page.evaluate(() => { const other = document.createElement("dialog"); other.id = "existing-dialog"; other.textContent = "Another portal message"; document.body.appendChild(other); other.showModal(); });
      await f.absent(); await f.page.locator("#existing-dialog").evaluate((el) => { el.close(); el.remove(); }); await f.visible();
    } finally { await f.close(); }
  });
  await test("320px and 390px mobile layouts are readable with reachable controls and no horizontal overflow", async () => {
    for (const viewport of [{ width: 320, height: 568 }, { width: 390, height: 844 }]) {
      const f = await fixture({ viewport });
      try {
        await f.goto("/login?next=%2Fesat"); await f.visible();
        const metrics = await f.page.locator(SELECTOR).evaluate((dialog) => { const r = dialog.getBoundingClientRect(); return { left: r.left, right: r.right, top: r.top, bottom: r.bottom, scrollWidth: dialog.scrollWidth, clientWidth: dialog.clientWidth, pageWidth: document.documentElement.scrollWidth, viewportWidth: innerWidth }; });
        assert.ok(metrics.left >= 0 && metrics.right <= viewport.width && metrics.top >= 0 && metrics.bottom <= viewport.height, JSON.stringify(metrics));
        assert.ok(metrics.scrollWidth <= metrics.clientWidth + 1, "Dialog must not scroll horizontally"); assert.ok(metrics.pageWidth <= metrics.viewportWidth, "Page must not scroll horizontally");
        for (const selector of [".ts-final-close", ".ts-final-pdf", ".ts-final-dismiss"]) {
          const control = f.page.locator(selector); await control.scrollIntoViewIfNeeded();
          const d = await control.evaluate((el) => { const r = el.getBoundingClientRect(); return { left: r.left, right: r.right, height: r.height, fontSize: parseFloat(getComputedStyle(el).fontSize), label: (el.getAttribute("aria-label") || el.textContent || "").trim(), clipped: el.scrollWidth > el.clientWidth + 2 }; });
          assert.ok(d.left >= 0 && d.right <= viewport.width && d.height >= 36 && d.fontSize >= 13 && d.label.length > 1 && !d.clipped, JSON.stringify(d));
        }
        await f.page.locator(SELECTOR).evaluate((el) => { el.scrollTop = 0; }); await f.page.screenshot({ path: join(outputDir, `mobile-${viewport.width}-top.png`), fullPage: true });
        await f.page.locator(".ts-final-dismiss").scrollIntoViewIfNeeded(); await f.page.screenshot({ path: join(outputDir, `mobile-${viewport.width}-actions.png`), fullPage: true });
        await f.page.locator(".ts-final-close").click(); await f.absent(250); assert.equal(f.calls.posts, 1);
      } finally { await f.close(); }
    }
  });
  assert.deepEqual(errors, [], "No browser errors or external requests are permitted");
  console.log(`ESAT final reminder UI verification passed. Screenshots: ${outputDir}`);
} finally {
  if (browser) await browser.close();
  await new Promise((resolveClose, reject) => server.close((error) => error ? reject(error) : resolveClose()));
}
