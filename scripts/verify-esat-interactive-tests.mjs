import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const testsRoot = path.join(
  root,
  "public",
  "esat-practice-tests",
  "tests",
);
const solutionsRoot = path.join(
  root,
  "public",
  "esat-practice-tests",
  "solutions",
);

const pathways = [
  ["physics-chemistry", ["Mathematics 1", "Physics", "Chemistry"]],
  ["physics-biology", ["Mathematics 1", "Physics", "Biology"]],
  ["maths2-chemistry", ["Mathematics 1", "Mathematics 2", "Chemistry"]],
  ["maths2-biology", ["Mathematics 1", "Mathematics 2", "Biology"]],
  ["chemistry-biology", ["Mathematics 1", "Chemistry", "Biology"]],
];

const expectedTests = pathways.flatMap(([pathway, modules]) =>
  [0, 1, 2].map((level) => ({
    testId: `esat-${pathway}-level-${level}`,
    modules,
  })),
);

const engineeringTests = [
  {
    folder: "esat-mock-01",
    testId: "esat-mock-01",
    solutionUrl: "https://www.thrivingscholars.com/_files/ugd/98f2c5_c93aaad4b62f4ad88b94adc4c190aaec.pdf",
  },
  {
    folder: "esat-mock-02",
    testId: "esat-mock-02",
    solutionUrl: "https://www.thrivingscholars.com/_files/ugd/98f2c5_c0a40b1e8699422eb30c2c72f7e29b6c.pdf",
  },
  {
    folder: "esat-mock-03",
    testId: "esat-mock-03",
    solutionUrl: "https://www.thrivingscholars.com/_files/ugd/98f2c5_3d9e1cd4a1df423183eed281e2afd28b.pdf",
  },
  {
    folder: "esat-mock-04",
    testId: "esat-mock-04",
    solutionUrl: "/esat-practice-tests/solutions/esat-mock-04-solutions.pdf",
  },
  {
    folder: "esat-mock-13",
    testId: "esat-mock-05",
    solutionUrl: "https://www.thrivingscholars.com/_files/ugd/98f2c5_b1abc3e8fdd54180b56d226cfa280892.pdf",
  },
];

const failures = [];

function requireMatch(content, expression, label) {
  const match = content.match(expression);
  if (!match) {
    failures.push(`Missing ${label}.`);
    return null;
  }
  return match[1];
}

for (const { testId, modules } of expectedTests) {
  const htmlPath = path.join(testsRoot, testId, "index.html");
  if (!fs.existsSync(htmlPath)) {
    failures.push(`${testId}: index.html is missing.`);
    continue;
  }

  const content = fs.readFileSync(htmlPath, "utf8");
  const questionsJson = requireMatch(
    content,
    /const questions = (\[[\s\S]*?\]);\s*\n\s*const totalQuestions/,
    `${testId} questions array`,
  );
  const answersJson = requireMatch(
    content,
    /const correctAnswers = (\[[\s\S]*?\]);\s*\n\s*const answerKeyBySection/,
    `${testId} answer array`,
  );
  const sectionsJson = requireMatch(
    content,
    /const sectionNames = (\[[^;]+\]);/,
    `${testId} section names`,
  );

  if (!questionsJson || !answersJson || !sectionsJson) continue;

  let questions;
  let answers;
  let sectionNames;
  try {
    questions = JSON.parse(questionsJson);
    answers = JSON.parse(answersJson);
    sectionNames = JSON.parse(sectionsJson);
  } catch (error) {
    failures.push(`${testId}: invalid generated JSON (${error.message}).`);
    continue;
  }

  if (questions.length !== 81 || answers.length !== 81) {
    failures.push(`${testId}: expected 81 questions and answers; found ${questions.length}/${answers.length}.`);
  }
  if (JSON.stringify(sectionNames) !== JSON.stringify(modules)) {
    failures.push(`${testId}: section order does not match the pathway.`);
  }

  const inputGroups = new Set();
  questions.forEach((question, index) => {
    const expectedGroup = String(index + 1);
    const names = [...question.matchAll(/name=["']q(\d+)["']/g)].map((match) => match[1]);
    names.forEach((name) => inputGroups.add(name));
    if (!names.length || names.some((name) => name !== expectedGroup)) {
      failures.push(`${testId}: Q${index + 1} has an incorrect radio group.`);
    }
    const answer = answers[index];
    if (!new RegExp(`value=["']${answer}["']`).test(question)) {
      failures.push(`${testId}: Q${index + 1} answer ${answer} is not an option.`);
    }
    if (/<img[^>]+src=["']https?:\/\//i.test(question)) {
      failures.push(`${testId}: Q${index + 1} retains a remote image.`);
    }
  });
  if (inputGroups.size !== 81) {
    failures.push(`${testId}: expected 81 unique radio groups; found ${inputGroups.size}.`);
  }

  for (let section = 0; section < 3; section += 1) {
    const start = section * 27;
    if (questions.slice(start, start + 27).length !== 27) {
      failures.push(`${testId}: section ${section + 1} is not 27 questions.`);
    }
  }

  const expectedSolution = `/esat-practice-tests/solutions/${testId}-solutions.pdf`;
  if (!content.includes(`const solutionPDF = "${expectedSolution}";`)) {
    failures.push(`${testId}: solution PDF URL is incorrect.`);
  }
  if (!content.includes("/shared/esat-score-estimates.js")) {
    failures.push(`${testId}: ESAT score-estimate UI is missing.`);
  }
  if (!content.includes("/shared/mathjax-tex-mml-chtml.js")) {
    failures.push(`${testId}: local MathJax is missing.`);
  }

  const pdfPath = path.join(solutionsRoot, `${testId}-solutions.pdf`);
  if (!fs.existsSync(pdfPath) || fs.statSync(pdfPath).size < 100_000) {
    failures.push(`${testId}: solution PDF is missing or unexpectedly small.`);
  } else {
    const signature = fs.readFileSync(pdfPath).subarray(0, 5).toString("ascii");
    if (signature !== "%PDF-") {
      failures.push(`${testId}: solution file is not a PDF.`);
    }
  }
}

for (const { folder, testId, solutionUrl } of engineeringTests) {
  const content = fs.readFileSync(path.join(testsRoot, folder, "index.html"), "utf8");
  for (const sharedAsset of [
    "/shared/esat-score-estimates.css",
    "/shared/esat-score-estimates.js",
    "/shared/esat-score-result-hook.js",
    "/shared/mathjax-tex-mml-chtml.js",
  ]) {
    if (!content.includes(sharedAsset)) {
      failures.push(`${folder}: missing ${sharedAsset}.`);
    }
  }
  if (!content.includes(`const testId = "${testId}";`)) {
    failures.push(`${folder}: predictor test ID does not match ${testId}.`);
  }
  if (!content.includes(`const solutionPDF = "${solutionUrl}";`)) {
    failures.push(`${folder}: solution PDF URL is missing or incorrect.`);
  }
}

const dashboard = fs.readFileSync(
  path.join(root, "app", "esat", "ESATDashboardClient.tsx"),
  "utf8",
);
for (const { folder, solutionUrl } of engineeringTests) {
  if (!dashboard.includes(`href: "/esat-practice-tests/tests/${folder}/index.html"`) ||
      !dashboard.includes(`solutionUrl: "${solutionUrl}"`)) {
    failures.push(`${folder}: dashboard test or solution link is missing.`);
  }
}

if (failures.length) {
  console.error("ESAT interactive-test verification failed:");
  failures.forEach((failure) => console.error(`- ${failure}`));
  process.exit(1);
}

console.log(
  `ESAT interactive-test verification passed: ${expectedTests.length} tests, ` +
  `${expectedTests.length * 81} questions, 15 local PDFs, and 5 Engineering predictor/solution hooks.`,
);
