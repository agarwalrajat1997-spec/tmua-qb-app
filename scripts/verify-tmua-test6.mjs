import fs from "node:fs";
import path from "node:path";

const dashboardPath = path.join(
  "app",
  "dashboard",
  "DashboardClient.tsx"
);

const testPath = path.join(
  "public",
  "practice-tests",
  "tests",
  "p2-mock-06-all-topics.html"
);

const solutionPath = path.join(
  "public",
  "tmua-solutions",
  "tmua-mock-test-6-paper-2-solutions.pdf"
);

const dashboard =
  fs.readFileSync(dashboardPath, "utf8");

const testHtml =
  fs.readFileSync(testPath, "utf8");

function fail(message) {
  throw new Error(
    `[TMUA Test 6 guard] ${message}`
  );
}

const blockMatch = dashboard.match(
  /\{\s*id:\s*"p2-mock-06"\s*,[\s\S]*?file:\s*"p2-mock-06-all-topics\.html"\s*,[\s\S]*?\}\s*,/
);

if (!blockMatch) {
  fail("Dashboard Test 6 block is missing.");
}

const block = blockMatch[0];

for (const required of [
  'test_id: "p2-mock-06-all-topics"',
  'section: "topic"',
  'badge: "PAPER 2"',
  'duration_minutes: 75',
  'solution_url: "/tmua-solutions/tmua-mock-test-6-paper-2-solutions.pdf"'
]) {
  if (!block.includes(required)) {
    fail(`Dashboard Test 6 block is missing: ${required}`);
  }
}

if (
  !fs.existsSync(solutionPath) ||
  fs.statSync(solutionPath).size < 10000
) {
  fail("Hosted Test 6 solution PDF is missing or too small.");
}

for (const required of [
  "/api/practice-tests/submit",
  "p2-mock-06-all-topics",
  "https://apps.thrivingscholars.com/tmua-solutions/tmua-mock-test-6-paper-2-solutions.pdf",
  "/shared/test-fullscreen.js?v=20260805-2",
  "TS_TMUA_TEST6_PORTAL_START",
  "Open Solution Book"
]) {
  if (!testHtml.includes(required)) {
    fail(`Test 6 HTML is missing: ${required}`);
  }
}

if (
  /file:\/\//i.test(testHtml) ||
  /[A-Za-z]:\\/.test(testHtml)
) {
  fail("Test 6 still contains a local file path.");
}

if (
  !/(start|begin)/i.test(testHtml) ||
  !/(submit|finish|complete)/i.test(testHtml)
) {
  fail("Test 6 Start or Submit controls could not be verified.");
}

console.log(
  "TMUA Test 6 verification passed: Topic-test placement, attempt ID, public solution PDF, embedded solution link and fullscreen are protected."
);