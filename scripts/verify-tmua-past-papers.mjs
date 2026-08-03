import fs from "node:fs";
import path from "node:path";

const root = process.cwd();

const definitions = [
  ...Array.from({ length: 8 }, (_, index) => {
    const year = 2016 + index;

    return {
      testId: `full-official-${year}`,
      file: `full-official-${year}.html`,
      solution: `full-official-${year}-solutions.html`
    };
  }),
  {
    testId: "full-specimen",
    file: "full-specimen.html",
    solution: "full-specimen-solutions.html"
  }
];

const dashboardPath = path.join(root, "app", "dashboard", "DashboardClient.tsx");
const indexPath = path.join(root, "public", "practice-tests", "index.html");
const testsDir = path.join(root, "public", "practice-tests", "tests");
const solutionsDir = path.join(root, "public", "practice-tests", "solutions");
const imagesDir = path.join(root, "public", "practice-tests", "images", "past-papers");

const dashboard = fs.readFileSync(dashboardPath, "utf8");
const legacyIndex = fs.existsSync(indexPath)
  ? fs.readFileSync(indexPath, "utf8")
  : "";

function fail(message) {
  throw new Error(`[TMUA past-paper guard] ${message}`);
}

function count(source, text) {
  return source.split(text).length - 1;
}

for (const definition of definitions) {
  const testPath = path.join(testsDir, definition.file);
  const solutionPath = path.join(solutionsDir, definition.solution);

  if (!fs.existsSync(testPath)) fail(`Missing test file: ${definition.file}`);
  if (fs.statSync(testPath).size < 1000) fail(`Test file is too small: ${definition.file}`);
  if (!fs.existsSync(solutionPath)) fail(`Missing solution file: ${definition.solution}`);
  if (fs.statSync(solutionPath).size < 1000) fail(`Solution file is too small: ${definition.solution}`);

  const testHtml = fs.readFileSync(testPath, "utf8");

  if (!testHtml.includes(`test_id: "${definition.testId}"`)) {
    fail(`Test submit identity is missing or wrong: ${definition.testId}`);
  }

  if (count(dashboard, `test_id: "${definition.testId}"`) !== 1) {
    fail(`Dashboard must contain exactly one card for ${definition.testId}`);
  }

  if (count(dashboard, `file: "${definition.file}"`) !== 1) {
    fail(`Dashboard file mapping is missing or duplicated: ${definition.file}`);
  }

  if (legacyIndex && !legacyIndex.includes(`file: "${definition.file}"`)) {
    fail(`Legacy practice index is missing ${definition.file}`);
  }
}

const dashboardOfficialCount = (
  dashboard.match(/test_id:\s*"full-(?:official-\d{4}|specimen)"/g) || []
).length;

if (dashboardOfficialCount !== definitions.length) {
  fail(`Expected ${definitions.length} dashboard past-paper cards; found ${dashboardOfficialCount}.`);
}

function countFiles(directory) {
  let total = 0;

  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const fullPath = path.join(directory, entry.name);
    total += entry.isDirectory() ? countFiles(fullPath) : 1;
  }

  return total;
}

if (!fs.existsSync(imagesDir)) fail("Past-paper image directory is missing.");

const imageCount = countFiles(imagesDir);

if (imageCount < 50) {
  fail(`Expected at least 50 past-paper image files; found ${imageCount}.`);
}

console.log(
  `TMUA past-paper verification passed: ${definitions.length} tests, ${definitions.length} solution pages and ${imageCount} image files are protected.`
);