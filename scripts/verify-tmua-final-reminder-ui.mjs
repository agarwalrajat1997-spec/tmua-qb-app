import assert from "node:assert/strict";
import { existsSync, mkdtempSync, readFileSync } from "node:fs";
import { createServer } from "node:http";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

// Serve the production assets over loopback; every student API request is mocked.
// No real portal, student session, database, or external service is contacted.
const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const outputDir = mkdtempSync(join(tmpdir(), "tmua-final-reminder-ui-"));
const API = "/api/student/tmua-final-reminder";
const PDF = "/tmua-resources/tmua-2026-mathematical-reasoning-practice.pdf";
const KEY = "tmua-final-warmup-2026-10-13";
const NOW = "2026-10-14T12:00:00+05:30";
const START = "2026-10-13T00:00:00+05:30";
const END = "2026-10-17T00:00:00+05:30";
const SELECTOR = "dialog.ts-final-reminder";
const errors = [];
let pdfRequests = 0;

const server = createServer((request, response) => {
  const url = new URL(request.url, "http://127.0.0.1");
  response.setHeader("Cache-Control", "no-store");
  if (["/tmua-final-reminder.js", "/tmua-final-reminder.css"].includes(url.pathname)) {
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
  if (url.pathname === API) {
    response.writeHead(500, { "Content-Type": "application/json" });
    response.end(JSON.stringify({ error: "Every API call must be intercepted by the test." }));
    return;
  }
  response.setHeader("Content-Type", "text/html; charset=utf-8");
  const audience = url.searchParams.get("fixtureAudience") === "1" ? " data-tmua-reminder-audience" : "";
  const iframe = url.pathname === "/fixture-frame-host" ? '<iframe title="TMUA embedded fixture" src="/tmua-question-bank/index.html"></iframe>' : "";
  response.end(`<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Reminder isolated fixture</title><style>body{margin:0;background:#eef1f5;font-family:Arial,sans-serif}main{padding:24px}button{font:inherit}iframe{width:90vw;height:400px}</style></head><body><main${audience}><h1>TMUA fixture</h1><button id="return-focus" autofocus>Continue studying</button>${iframe}</main><script src="/tmua-final-reminder.js" defer></script></body></html>`);
});

await new Promise((resolveListen, reject) => {
  server.once("error", reject);
  server.listen(0, "127.0.0.1", resolveListen);
});
const baseUrl = `http://127.0.0.1:${server.address().port}`;
const executablePath = [
  process.env.TMUA_REMINDER_CHROME,
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
].find((candidate) => candidate && existsSync(candidate));
let browser;

async function fixture({ authenticated = true, receipt = { dismissed: false }, date = NOW, viewport = { width: 1440, height: 1000 }, runningClock = false, postDelay = 0 } = {}) {
  const context = await browser.newContext({ viewport });
  const calls = { gets: 0, posts: 0, bodies: [] };
  await context.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    // Opening a PDF also loads Chromium's bundled viewer, which is not a
    // network service. Keep the external HTTP(S) boundary strict below.
    if (["chrome-extension:", "chrome:", "data:", "blob:"].includes(url.protocol)) {
      await route.continue();
      return;
    }
    if (url.origin !== baseUrl) {
      errors.push(`Unexpected external request: ${url.href}`);
      await route.abort();
      return;
    }
    if (url.pathname !== API) {
      await route.continue();
      return;
    }
    const method = route.request().method();
    if (method === "POST") {
      calls.posts += 1;
      calls.bodies.push(route.request().postDataJSON());
      if (postDelay) await new Promise((resolveDelay) => setTimeout(resolveDelay, postDelay));
      if (authenticated) receipt.dismissed = true;
      await route.fulfill({ status: authenticated ? 200 : 401, json: { dismissed: authenticated } });
    } else {
      calls.gets += 1;
      await route.fulfill({ status: authenticated ? 200 : 401, json: { active: true, authenticated, dismissed: receipt.dismissed, show: !receipt.dismissed } });
    }
  });
  const page = await context.newPage();
  page.on("pageerror", (error) => errors.push(error.message));
  if (runningClock) await page.clock.install({ time: new Date(date) });
  else await page.clock.setFixedTime(new Date(date));
  async function goto(path) {
    await page.goto(`${baseUrl}${path}`, { waitUntil: "load" });
  }
  async function visible() {
    await page.locator(SELECTOR).waitFor({ state: "visible", timeout: 7000 });
    assert.equal(await page.locator(`${SELECTOR}[open]`).count(), 1, "One accessible modal must be open");
  }
  async function absent(delay = 1200) {
    await page.waitForTimeout(delay);
    assert.equal(await page.locator(SELECTOR).count(), 0, `Reminder must stay absent at ${page.url()}`);
  }
  return { context, page, calls, goto, visible, absent, close: () => context.close() };
}

async function test(name, run) {
  await run();
  console.log(`PASS ${name}`);
}

try {
  browser = await chromium.launch({ ...(executablePath ? { executablePath } : {}), headless: true });

  await test("authenticated viewing and PDF click do not dismiss; one dismissal persists locally and on another device", async () => {
    const receipt = { dismissed: false };
    const f = await fixture({ receipt, postDelay: 150 });
    try {
      await f.goto("/dashboard?fixtureAudience=1&view=tmua");
      await f.visible();
      assert.equal(f.calls.posts, 0);
      assert.equal(await f.page.evaluate((key) => localStorage.getItem(key), KEY), null);
      await f.page.getByRole("heading", { name: "Your final TMUA warm-up." }).waitFor();
      const pdf = f.page.getByRole("link", { name: "Try 10 extra practice questions" });
      assert.equal(await pdf.getAttribute("href"), PDF);
      assert.equal(await pdf.getAttribute("target"), "_blank");
      assert.match(await pdf.getAttribute("rel"), /noopener/);
      const requestCount = pdfRequests;
      const popupPromise = f.context.waitForEvent("page");
      await pdf.click();
      const pdfPage = await popupPromise;
      await f.page.waitForTimeout(300);
      assert.ok(pdfRequests > requestCount, "PDF click must request the public PDF");
      await pdfPage.close();
      await f.page.bringToFront();
      await f.visible();
      assert.equal(f.calls.posts, 0, "PDF click must not save a dismissal");
      assert.equal(await f.page.evaluate((key) => localStorage.getItem(key), KEY), null);
      await f.page.screenshot({ path: join(outputDir, "desktop.png"), fullPage: true });
      await f.page.getByRole("button", { name: "Got it — don’t show again" }).click();
      await f.absent(500);
      assert.equal(f.calls.posts, 1);
      assert.deepEqual(f.calls.bodies, [{ action: "dismiss" }]);
      assert.equal(await f.page.evaluate((key) => localStorage.getItem(key), KEY), "dismissed");
      assert.equal(await f.page.evaluate((key) => localStorage.getItem(`${key}-pending`), KEY), null);
      assert.equal(await f.page.locator("#return-focus").evaluate((el) => el === document.activeElement), true);
      await f.page.reload({ waitUntil: "load" });
      await f.absent();
      assert.equal(f.calls.posts, 1, "Refresh must not resave an acknowledged dismissal");
      const anotherDevice = await fixture({ receipt });
      try {
        await anotherDevice.goto("/tmua-question-bank");
        await anotherDevice.absent();
        assert.ok(anotherDevice.calls.gets > 0, "A new device must consult the server receipt");
        assert.equal(anotherDevice.calls.posts, 0);
      } finally { await anotherDevice.close(); }
    } finally { await f.close(); }
  });

  await test("anonymous Escape dismissal stays local and survives refresh", async () => {
    const f = await fixture({ authenticated: false });
    try {
      await f.goto("/login");
      await f.visible();
      await f.page.keyboard.press("Escape");
      await f.absent(200);
      assert.equal(f.calls.posts, 0);
      assert.equal(await f.page.evaluate((key) => localStorage.getItem(key), KEY), "dismissed");
      await f.page.reload({ waitUntil: "load" });
      await f.absent();
      assert.equal(f.calls.posts, 0);
    } finally { await f.close(); }
  });

  const eligibleRoutes = [
    "/tmua", "/tmua-question-bank", "/tmua-question-bank/", "/tmua-question-bank/index.html",
    "/question-bank-tmua", "/practice-tests", "/practice-tests/index.html", "/tmua-classes",
    "/tmua-classes/index.html", "/tmua-solutions", "/tmua-solutions/index.html",
    "/login", "/login?next=%2Ftmua-question-bank", "/login?next=%2Fdashboard%3Fview%3Dtmua",
    "/dashboard?fixtureAudience=1", "/dashboard?view=tmua&fixtureAudience=1",
  ];
  await test(`all ${eligibleRoutes.length} intended TMUA route variants show`, async () => {
    for (let index = 0; index < eligibleRoutes.length; index += 4) {
      await Promise.all(eligibleRoutes.slice(index, index + 4).map(async (path) => {
        const f = await fixture();
        try { await f.goto(path); await f.visible(); } finally { await f.close(); }
      }));
    }
  });

  const excludedRoutes = [
    "/dashboard", "/dashboard?view=tmua", "/dashboard?view=sat&fixtureAudience=1",
    "/dashboard?view=amc&fixtureAudience=1", "/dashboard?view=esat&fixtureAudience=1",
    "/dashboard?view=SAT&fixtureAudience=1", "/esat", "/esat-login", "/esat-question-bank",
    "/esat-practice-tests", "/sat", "/sat-login", "/sat-question-bank", "/sat-practice-tests",
    "/amc", "/amc-login", "/amc-question-bank", "/amc-practice-tests", "/pending",
    "/practice-tests/tests/full-official-2023.html", "/practice-tests/tests/tmua-2026-predictive-paper/index.html",
    "/tmua-tests/topic-test-1/index.html", "/tmua-question-bank-unrelated", "/tmua-classes/unknown",
    "/login?next=%2Fesat", "/login?next=%2Fesat-question-bank", "/login?next=%2Fsat-question-bank",
    "/login?next=%2Famc-question-bank", "/login?next=%2Fdashboard%3Fview%3Dsat",
    "/login?next=%2Fdashboard%3Fview%3Damc", "/login?next=%2Fdashboard%3Fview%3Desat",
    "/login?next=%2Fpractice-tests%2Ftests%2Ffull-official-2023.html",
    "/login?next=https%3A%2F%2Fforeign.invalid%2Fdashboard", "/login?next=%2F%2Fforeign.invalid%2Ftmua-question-bank",
    "/login?next=javascript%3Aalert(1)", "/login?next=http%3A%2F%2F%5B",
  ];
  await test(`all ${excludedRoutes.length} non-TMUA, unresolved dashboard, test and foreign-next routes stay untouched`, async () => {
    for (let index = 0; index < excludedRoutes.length; index += 4) {
      await Promise.all(excludedRoutes.slice(index, index + 4).map(async (path) => {
        const f = await fixture();
        try {
          await f.goto(path);
          await f.absent();
          assert.equal(f.calls.gets, 0, `Excluded route must not consult the reminder API: ${path}`);
        } finally { await f.close(); }
      }));
    }
  });

  await test("dashboard waits for its audience marker, then hides if the view changes", async () => {
    const f = await fixture();
    try {
      await f.goto("/dashboard");
      await f.absent();
      await f.page.locator("main").evaluate((el) => {
        const marker = document.createElement("span");
        marker.dataset.tmuaReminderAudience = "true";
        el.appendChild(marker);
      });
      await f.visible();
      await f.page.evaluate(() => {
        history.pushState({}, "", "/dashboard?view=sat");
        window.dispatchEvent(new Event("tmua-reminder-route"));
      });
      await f.absent(100);
      assert.equal(f.calls.posts, 0, "Leaving the TMUA view must not count as dismissal");
    } finally { await f.close(); }
  });

  await test("embedded TMUA pages cannot open duplicate reminders", async () => {
    const f = await fixture();
    try {
      await f.goto("/fixture-frame-host");
      await f.absent();
      assert.equal(await f.page.frameLocator("iframe").locator(SELECTOR).count(), 0);
      assert.equal(f.calls.gets, 0);
    } finally { await f.close(); }
  });

  await test("pre-campaign and expired visits stay hidden", async () => {
    for (const date of [new Date(Date.parse(START) - 1).toISOString(), END, "2026-10-18T12:00:00+05:30"]) {
      const f = await fixture({ date });
      try {
        await f.goto("/tmua-question-bank");
        await f.absent();
        assert.equal(f.calls.gets, 0);
      } finally { await f.close(); }
    }
  });

  await test("an already-open reminder closes at campaign expiry without saving dismissal", async () => {
    const f = await fixture({ date: new Date(Date.parse(END) - 10000).toISOString(), runningClock: true });
    try {
      await f.goto("/tmua-question-bank");
      await f.visible();
      await f.page.clock.fastForward(11000);
      await f.absent(50);
      assert.equal(f.calls.posts, 0);
      assert.equal(await f.page.evaluate((key) => localStorage.getItem(key), KEY), null);
    } finally { await f.close(); }
  });

  await test("an existing modal is respected before showing the reminder", async () => {
    const f = await fixture();
    try {
      await f.goto("/tmua-question-bank");
      await f.page.evaluate(() => {
        const other = document.createElement("dialog");
        other.id = "existing-dialog";
        other.textContent = "Another portal message";
        document.body.appendChild(other);
        other.showModal();
      });
      await f.absent();
      await f.page.locator("#existing-dialog").evaluate((el) => { el.close(); el.remove(); });
      await f.visible();
    } finally { await f.close(); }
  });

  await test("mobile reminder and buttons remain readable without horizontal overflow", async () => {
    for (const viewport of [{ width: 320, height: 568 }, { width: 390, height: 844 }]) {
      const f = await fixture({ viewport });
      try {
        await f.goto("/login");
        await f.visible();
        const metrics = await f.page.locator(SELECTOR).evaluate((dialog) => {
          const rect = dialog.getBoundingClientRect();
          return { left: rect.left, right: rect.right, top: rect.top, bottom: rect.bottom, scrollWidth: dialog.scrollWidth, clientWidth: dialog.clientWidth, pageWidth: document.documentElement.scrollWidth, viewportWidth: innerWidth, viewportHeight: innerHeight };
        });
        assert.ok(metrics.left >= 0 && metrics.right <= viewport.width, JSON.stringify(metrics));
        assert.ok(metrics.top >= 0 && metrics.bottom <= viewport.height, JSON.stringify(metrics));
        assert.ok(metrics.scrollWidth <= metrics.clientWidth + 1, "Dialog must have no horizontal scrollbar");
        assert.ok(metrics.pageWidth <= metrics.viewportWidth, "Page must have no horizontal scrollbar");
        const controls = [f.page.locator(".ts-final-close"), f.page.locator(".ts-final-pdf"), f.page.locator(".ts-final-dismiss")];
        for (const control of controls) {
          await control.scrollIntoViewIfNeeded();
          const dimensions = await control.evaluate((element) => {
            const rect = element.getBoundingClientRect();
            return { left: rect.left, right: rect.right, height: rect.height, fontSize: Number.parseFloat(getComputedStyle(element).fontSize), label: (element.getAttribute("aria-label") || element.textContent || "").trim(), clipped: element.scrollWidth > element.clientWidth + 2 };
          });
          assert.ok(dimensions.left >= 0 && dimensions.right <= viewport.width, JSON.stringify(dimensions));
          assert.ok(dimensions.fontSize >= 13 && dimensions.height >= 36, JSON.stringify(dimensions));
          assert.ok(dimensions.label.length > 1 && !dimensions.clipped, JSON.stringify(dimensions));
        }
        await f.page.locator(SELECTOR).evaluate((dialog) => { dialog.scrollTop = 0; });
        await f.page.screenshot({ path: join(outputDir, `mobile-${viewport.width}-top.png`), fullPage: true });
        await f.page.locator(".ts-final-dismiss").scrollIntoViewIfNeeded();
        await f.page.screenshot({ path: join(outputDir, `mobile-${viewport.width}-actions.png`), fullPage: true });
        await f.page.locator(".ts-final-close").click();
        await f.absent(250);
        assert.equal(f.calls.posts, 1);
      } finally { await f.close(); }
    }
  });

  assert.deepEqual(errors, [], "Browser must not throw errors or request external services");
  console.log(`TMUA final reminder UI verification passed. Screenshots: ${outputDir}`);
} finally {
  if (browser) await browser.close();
  await new Promise((resolveClose, reject) => server.close((error) => error ? reject(error) : resolveClose()));
}
