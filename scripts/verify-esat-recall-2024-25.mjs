import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { existsSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import vm from "node:vm";

const root = process.cwd();
const testsRoot = join(root, "public", "esat-practice-tests", "tests");
const cases = [
  {
    "testId": "esat-recall-2024-25-engineering",
    "modules": [
      "Mathematics 1",
      "Mathematics 2",
      "Physics"
    ],
    "solutionFile": "esat-2024-2025-recall-mock-engineering-solutions.pdf",
    "answerHash": "9f80461ac16ccd3c8de0b0ef4887934cecaea58d00ed88b31f9a89f6ea4f9ada"
  },
  {
    "testId": "esat-recall-2024-25-physics-chemistry",
    "modules": [
      "Mathematics 1",
      "Physics",
      "Chemistry"
    ],
    "solutionFile": "esat-2024-2025-recall-mock-physics-chemistry-solutions.pdf",
    "answerHash": "d59f1b7b9c948b66f9bfc5be77a4d9325af490a0ed8afd9ec68dec67b9a02b3c"
  },
  {
    "testId": "esat-recall-2024-25-physics-biology",
    "modules": [
      "Mathematics 1",
      "Physics",
      "Biology"
    ],
    "solutionFile": "esat-2024-2025-recall-mock-physics-biology-solutions.pdf",
    "answerHash": "62aa5660b4ff7d5366c2250e1d81ee97eacc9bfada19d463cb342495963c1b81"
  },
  {
    "testId": "esat-recall-2024-25-maths2-chemistry",
    "modules": [
      "Mathematics 1",
      "Mathematics 2",
      "Chemistry"
    ],
    "solutionFile": "esat-2024-2025-recall-mock-maths2-chemistry-solutions.pdf",
    "answerHash": "f63ecc89d69ef746f2471ce25befe1d405b32a6c4bbe5d4cfe721200762faba4"
  },
  {
    "testId": "esat-recall-2024-25-maths2-biology",
    "modules": [
      "Mathematics 1",
      "Mathematics 2",
      "Biology"
    ],
    "solutionFile": "esat-2024-2025-recall-mock-maths2-biology-solutions.pdf",
    "answerHash": "46a1b27d6c4f64c5057b9fe834a19b89defad964145453c6f92baf374daeb816"
  },
  {
    "testId": "esat-recall-2024-25-chemistry-biology",
    "modules": [
      "Mathematics 1",
      "Chemistry",
      "Biology"
    ],
    "solutionFile": "esat-2024-2025-recall-mock-chemistry-biology-solutions.pdf",
    "answerHash": "3c05386f4b7a723c2f4cf222e1fbd6fdfc7c5c392d6738cdb330f2f98c5e4d1a"
  }
];

function literal(source, expression, label) {
  const match = source.match(expression);
  assert.ok(match, `Missing ${label}.`);
  return match[1];
}

for (const test of cases) {
  const file = join(testsRoot, test.testId, "index.html");
  assert.ok(existsSync(file), `${test.testId}: test HTML is missing.`);
  const source = readFileSync(file, "utf8");
  assert.ok(statSync(file).size > 100_000, `${test.testId}: HTML is unexpectedly small.`);
  assert.ok(!source.includes("__SOLUTION_PDF_URL__"), `${test.testId}: solution placeholder remains.`);

  const sourceId = source.match(/const testId\s*=\s*["']([^"']+)["']/)?.[1];
  assert.equal(sourceId, test.testId, `${test.testId}: testId mismatch.`);
  assert.ok(
    source.includes(`const solutionPDF = "/esat-practice-tests/solutions/${test.solutionFile}";`),
    `${test.testId}: solution URL mismatch.`,
  );
  const sectionNames = vm.runInNewContext(literal(
    source,
    /const sectionNames\s*=\s*(\[[^;]+\]);/,
    `${test.testId} section names`,
  ));
  assert.deepEqual([...sectionNames], test.modules, `${test.testId}: module order mismatch.`);

  const questions = vm.runInNewContext(literal(
    source,
    /const questions\s*=\s*(\[[\s\S]*?\]);\s*\n\s*const (?:correctAnswers|totalQuestions)/,
    `${test.testId} questions`,
  ));
  const answers = vm.runInNewContext(literal(
    source,
    /const correctAnswers\s*=\s*(\[[\s\S]*?\]);/,
    `${test.testId} answers`,
  ));
  assert.equal(questions.length, 81, `${test.testId}: expected 81 questions.`);
  assert.equal(answers.length, 81, `${test.testId}: expected 81 answers.`);
  assert.ok(answers.every((a) => /^[A-H]$/.test(a)), `${test.testId}: invalid answer letter.`);
  const hash = createHash("sha256").update(JSON.stringify([...answers]), "utf8").digest("hex");
  assert.equal(hash, test.answerHash, `${test.testId}: answer-key checksum mismatch.`);

  const groups = new Set();
  questions.forEach((question, index) => {
    const names = [...question.matchAll(/name=["']q(\d+)["']/g)].map((m) => m[1]);
    assert.ok(names.length > 0, `${test.testId}: Q${index + 1} has no radio choices.`);
    assert.ok(names.every((name) => name === String(index + 1)), `${test.testId}: Q${index + 1} radio group mismatch.`);
    names.forEach((name) => groups.add(name));
    assert.match(question, new RegExp(`value=["']${answers[index]}["']`), `${test.testId}: Q${index + 1} answer is not a choice.`);
    assert.doesNotMatch(question, /<img[^>]+src=["']https?:\/\//i, `${test.testId}: Q${index + 1} retains a remote image.`);
  });
  assert.equal(groups.size, 81, `${test.testId}: expected 81 unique radio groups.`);

  for (const token of [
    "const SECTION_SIZE = 27",
    "const SECTION_SECONDS = 40 * 60",
    "const BREAK_SECONDS = 5 * 60",
    "/shared/esat-score-estimates.js",
    "/shared/esat-score-result-hook.js",
    "/shared/mathjax-tex-mml-chtml.js",
    "/shared/test-fullscreen.js",
    "/api/practice-tests/submit",
    "localStorage",
  ]) {
    assert.ok(source.includes(token), `${test.testId}: missing ${token}.`);
  }

  const pdfRoute = join(
    root,
    "app",
    "esat-practice-tests",
    "solutions",
    test.solutionFile,
    "route.ts",
  );
  assert.ok(existsSync(pdfRoute), `${test.testId}: public PDF route is missing.`);
  const pdfRouteSource = readFileSync(pdfRoute, "utf8");
  assert.ok(pdfRouteSource.includes(test.solutionFile), `${test.testId}: PDF route filename mismatch.`);
}

const dashboard = readFileSync(join(root, "app", "esat", "ESATDashboardClient.tsx"), "utf8");
for (const test of cases) {
  assert.ok(dashboard.includes(`test_id: "${test.testId}"`), `${test.testId}: dashboard card is missing.`);
  assert.ok(dashboard.includes(`href: "/esat-practice-tests/tests/${test.testId}/index.html"`), `${test.testId}: dashboard href is missing.`);
  assert.ok(dashboard.includes(`solutionUrl: "/esat-practice-tests/solutions/${test.solutionFile}"`), `${test.testId}: dashboard solution is missing.`);
}

const proxy = readFileSync(join(root, "proxy.ts"), "utf8");
assert.match(proxy, /prefix:\s*"\/esat-practice-tests",\s*product:\s*"esat-practice-tests"/);
assert.match(proxy, /\/esat-practice-tests\/solutions\//);
assert.match(proxy, /"\/esat-practice-tests\/:path\*"/);

const canonical = readFileSync(join(root, "lib", "server", "esat-canonical-tests.ts"), "utf8");
const scoreProfiles = readFileSync(join(root, "lib", "server", "esat-score-estimates.ts"), "utf8");
for (const test of cases) {
  assert.ok(canonical.includes(`"${test.testId}"`), `${test.testId}: canonical key is missing.`);
  assert.ok(scoreProfiles.includes(`"${test.testId}"`), `${test.testId}: score profile is missing.`);
}

console.log("ESAT recall release verification passed: 6 protected dashboard cards, 486 questions, 486 answers, 6 public PDF routes and module-aware score profiles.");
