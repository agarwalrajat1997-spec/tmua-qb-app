import fs from "node:fs";
import path from "node:path";

const dashboard = fs.readFileSync(
  path.join("app","dashboard","DashboardClient.tsx"), "utf8"
);
const testsRoot = path.join("public","practice-tests","tests");
const solutionsRoot = path.join("public","practice-tests","solutions");
const challenge = fs.readFileSync(
  path.join(testsRoot,"tmua-2024-2025-challenging-mock","index.html"), "utf8"
);
const fullscreen = fs.readFileSync(
  path.join("public","shared","test-fullscreen.js"), "utf8"
);

const fail = message => {
  throw new Error(`[TMUA practice-test guard] ${message}`);
};
const count = (source, text) => source.split(text).length - 1;

for (const title of [
  "Topic tests",
  "Full-length tests by Thriving Scholars",
  "Official TMUA past papers"
]) {
  if (count(dashboard, `>${title}</div>`) !== 1) {
    fail(`Expected exactly one section: ${title}`);
  }
}

for (const text of [
  'section: "topic" | "thriving" | "official";',
  "const thrivingFullTests",
  "const officialPastPapers",
  "{thrivingFullTests.map(",
  "{officialPastPapers.map(",
  'test_id: "tmua-2024-2025-challenging-mock"',
  'file: "tmua-2024-2025-challenging-mock/index.html"',
  'solution_url: "https://apps.thrivingscholars.com/tmua-solutions/tmua-2024-2025-challenging-full-test-revised-solutions.pdf"'
]) {
  if (!dashboard.includes(text)) fail(`Dashboard missing: ${text}`);
}

const officialIds = [
  ...Array.from({ length: 8 }, (_, i) => `full-official-${2016 + i}`),
  "full-specimen"
];

for (const id of officialIds) {
  if (count(dashboard, `test_id: "${id}"`) !== 1) {
    fail(`Official dashboard entry missing/duplicated: ${id}`);
  }

  const test = id === "full-specimen" ? "full-specimen.html" : `${id}.html`;
  const solution = id === "full-specimen"
    ? "full-specimen-solutions.html"
    : `${id}-solutions.html`;

  if (!fs.existsSync(path.join(testsRoot, test))) fail(`Missing test: ${test}`);
  if (!fs.existsSync(path.join(solutionsRoot, solution))) fail(`Missing solution: ${solution}`);
}

for (const text of [
  "/api/practice-tests/submit",
  "tmua-2024-2025-challenging-mock",
  "https://apps.thrivingscholars.com/tmua-solutions/tmua-2024-2025-challenging-full-test-revised-solutions.pdf",
  "/shared/test-fullscreen.js?v=20260805-2"
]) {
  if (!challenge.includes(text)) fail(`Challenge test missing: ${text}`);
}

const pdf = path.join(
  "public","tmua-solutions",
  "tmua-2024-2025-challenging-full-test-revised-solutions.pdf"
);
if (!fs.existsSync(pdf) || fs.statSync(pdf).size < 10000) {
  fail("Challenge solution PDF is missing or too small.");
}

for (const text of [
  "requestFullscreen",
  "exitFullscreen",
  "skipBreakLabel",
  "skipBreakHandler",
  "/api/practice-tests/submit",
  "MutationObserver",
  "__TS_TEST_FULLSCREEN_V2__"
]) {
  if (!fullscreen.includes(text)) fail(`Fullscreen controller missing: ${text}`);
}

const htmlFiles = [];
const walk = dir => {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) walk(full);
    else if (e.isFile() && e.name.toLowerCase().endsWith(".html")) htmlFiles.push(full);
  }
};
walk(testsRoot);

for (const file of htmlFiles) {
  const html = fs.readFileSync(file, "utf8");
  if (!html.includes("/shared/test-fullscreen.js?v=20260805-2")) {
    fail(`Fullscreen tag missing from: ${file}`);
  }
}

console.log(
  `TMUA practice-test verification passed: 3 sections, 9 official papers, challenge mock, solution PDF and fullscreen across ${htmlFiles.length} HTML tests.`
);
