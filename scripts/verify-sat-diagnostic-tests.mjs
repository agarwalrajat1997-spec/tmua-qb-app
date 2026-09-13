import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

for (const testNumber of [1, 2, 3, 4]) {
  const html = await readFile(
    new URL(`../public/sat-test-${testNumber}/index.html`, import.meta.url),
    "utf8",
  );
  const route = await readFile(
    new URL(`../app/sat-test-${testNumber}/route.ts`, import.meta.url),
    "utf8",
  );

  assert.match(html, new RegExp(`Digital SAT Math Test ${testNumber}`));
  assert.match(html, /Module 1:<\/strong> Math, 22 questions, 35 minutes/);
  assert.match(html, /Module 2:<\/strong> Math, 22 questions, 35 minutes/);
  assert.match(html, /predicted Math score out of 800/);
  assert.match(html, /www\.desmos\.com\/api/);
  assert.match(html, /emailjs\.send\(/);
  assert.match(route, new RegExp(`/sat-test-${testNumber}/index\\.html`));
}

const standardFullLengthHtml = await readFile(
  new URL("../public/sat-test-6/index.html", import.meta.url),
  "utf8",
);
const standardFullLengthRoute = await readFile(
  new URL("../app/sat-test-6/route.ts", import.meta.url),
  "utf8",
);
const hardFullLengthHtml = await readFile(
  new URL("../public/sat-test-5/index.html", import.meta.url),
  "utf8",
);
const hardFullLengthRoute = await readFile(
  new URL("../app/sat-test-5/route.ts", import.meta.url),
  "utf8",
);
const miniHtml = await readFile(
  new URL("../public/sat-mini-diagnostic/index.html", import.meta.url),
  "utf8",
);
const miniRoute = await readFile(
  new URL("../app/sat-mini-diagnostic/route.ts", import.meta.url),
  "utf8",
);
const dashboard = await readFile(
  new URL("../app/dashboard/SATDashboardClient.tsx", import.meta.url),
  "utf8",
);

assert.match(standardFullLengthHtml, /SAT Diagnostic Test 6 — Standard/);
assert.match(standardFullLengthHtml, /Reading &amp; Writing, 27 questions, 32 minutes<\/li>/);
assert.match(standardFullLengthHtml, /Math, 22 questions, 35 minutes<\/li>/);
assert.doesNotMatch(standardFullLengthHtml, /32 minutes — (?:hard|harder|standard|challenging)/i);
assert.doesNotMatch(standardFullLengthHtml, /35 minutes — (?:hard|harder|standard|challenging)/i);
assert.match(standardFullLengthHtml, /emailjs\.send\(/);
assert.match(standardFullLengthRoute, /\/sat-test-6\/index\.html/);

assert.match(hardFullLengthHtml, /SAT Diagnostic Test 5 — Advanced/);
assert.match(hardFullLengthHtml, /Reading &amp; Writing, 27 questions, 32 minutes — hard/);
assert.match(hardFullLengthHtml, /Math, 22 questions, 35 minutes — harder/);
assert.match(hardFullLengthHtml, /emailjs\.send\(/);
assert.match(hardFullLengthRoute, /\/sat-test-5\/index\.html/);

assert.match(miniHtml, /mini SAT-style diagnostic with 33 Reading and Writing questions and 27 Math questions/);
assert.match(miniHtml, /predicted SAT score out of 1600/);
assert.match(miniHtml, /emailjs\.send\(/);
assert.match(miniRoute, /\/sat-mini-diagnostic\/index\.html/);

for (const href of [
  "/sat-mini-diagnostic",
  "/sat-test-1",
  "/sat-test-2",
  "/sat-test-3",
  "/sat-test-4",
  "/sat-test-5",
  "/sat-test-6",
]) {
  assert.match(dashboard, new RegExp(href.replaceAll("/", "\\/")));
}

assert.doesNotMatch(dashboard, /sat-practice-tests\/tests\/sat-/);

assert.match(dashboard, /7 Verified Tests/);
assert.match(dashboard, /2 Full-Length/);
assert.match(dashboard, /SAT Diagnostic Test 5 — Advanced/);
assert.match(dashboard, /SAT Diagnostic Test 6/);

console.log("Seven verified SAT diagnostics are restored, catalogued by difficulty, and routable.");
