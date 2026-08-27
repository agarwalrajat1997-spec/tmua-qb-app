import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const testsRoot = path.join(root, "public", "esat-practice-tests", "tests");
const sharedControllerPath = path.join(root, "public", "shared", "test-fullscreen.js");

const engineeringFolders = [
  "esat-mock-01",
  "esat-mock-02",
  "esat-mock-03",
  "esat-mock-04",
  "esat-mock-13",
];
const pathwayFolders = [
  "physics-chemistry",
  "physics-biology",
  "maths2-chemistry",
  "maths2-biology",
  "chemistry-biology",
].flatMap(pathway => [0, 1, 2].map(level => `esat-${pathway}-level-${level}`));
const recallFolders = [
  "esat-recall-2024-25-engineering",
  "esat-recall-2024-25-physics-chemistry",
  "esat-recall-2024-25-physics-biology",
  "esat-recall-2024-25-maths2-chemistry",
  "esat-recall-2024-25-maths2-biology",
  "esat-recall-2024-25-chemistry-biology",
];
const folders = [...engineeringFolders, ...pathwayFolders, ...recallFolders];
const failures = [];

function emailBlock(content) {
  const start = content.indexOf("function sendResultsEmail");
  if (start < 0) return "";
  const ends = [
    content.indexOf("function statusText", start + 1),
    content.indexOf("async function submitExam", start + 1),
    content.indexOf("function submitExam", start + 1),
  ].filter(index => index > start);
  const end = ends.length ? Math.min(...ends) : content.length;
  return content.slice(start, end);
}

for (const folder of folders) {
  const file = path.join(testsRoot, folder, "index.html");
  if (!fs.existsSync(file)) {
    failures.push(`${folder}: index.html is missing.`);
    continue;
  }
  const content = fs.readFileSync(file, "utf8");
  const block = emailBlock(content);
  if (!block) {
    failures.push(`${folder}: sendResultsEmail is missing.`);
    continue;
  }

  if (!/emailjs\.send\(\s*["']service_5l4w8x2["']\s*,\s*["']template_j1jrs4o["']/.test(block)) {
    failures.push(`${folder}: the production EmailJS service/template call is missing.`);
  }
  if (!/solution_link\s*:\s*new URL\(\s*solutionPDF\s*,\s*window\.location\.origin\s*\)\.href/.test(block)) {
    failures.push(`${folder}: the emailed solution link is not made absolute.`);
  }
  for (const field of ["paper1", "paper2", "paper3"]) {
    if (!new RegExp(`\\b${field}\\s*:`).test(block)) {
      failures.push(`${folder}: ${field} is missing from the EmailJS payload.`);
    }
  }

  // The current EmailJS template renders paper1 and paper2. paper2 must therefore
  // carry analyses for both the second and third modules; paper3 remains populated
  // for compatibility with any future three-block template.
  if (!/paper2\s*:\s*`[\s\S]*?\$\{[^}]+\}\\n\\n\$\{[^}]+\}[\s\S]*?`/.test(block)) {
    failures.push(`${folder}: paper2 does not contain both remaining module analyses.`);
  }

  const namesMatch = content.match(/const sectionNames\s*=\s*(\[[^;]+\]);/);
  if (!namesMatch) {
    failures.push(`${folder}: sectionNames is missing.`);
  } else {
    try {
      const names = JSON.parse(namesMatch[1]);
      if (!Array.isArray(names) || names.length !== 3) {
        failures.push(`${folder}: sectionNames must contain exactly three modules.`);
      }
    } catch (error) {
      failures.push(`${folder}: sectionNames is not valid JSON (${error.message}).`);
    }
  }

  if (!content.includes('/shared/test-fullscreen.js?v=20260827-1')) {
    failures.push(`${folder}: the cache-busted shared report/fullscreen controller is missing.`);
  }

  if (recallFolders.includes(folder)) {
    for (const marker of [
      "const emailAnalyses=sectionNames.map",
      "paper1:emailAnalyses[0]",
      "paper2:`${emailAnalyses[1]}\\n\\n${emailAnalyses[2]}`",
      "paper3:emailAnalyses[2]",
      "payload[`section${i+1}_name`]=name",
      "payload[`section${i+1}_score`]=`${scores[i]} / 27`",
    ]) {
      if (!block.includes(marker)) failures.push(`${folder}: recall report marker is missing: ${marker}`);
    }
  }
}

const shared = fs.readFileSync(sharedControllerPath, "utf8");
for (const marker of [
  "esat-recall-2024-25-",
  "paper2AlreadyContainsPaper3",
  "rawPaper2.includes(rawPaper3)",
  "rawPaper2Only",
  "payload.solution_link = absoluteEsatSolutionUrl(payload.solution_link)",
  "payload.paper2 = `${paper2}\\n\\n${paper3}`",
]) {
  if (!shared.includes(marker)) failures.push(`Shared ESAT email adapter is missing ${marker}.`);
}

if (failures.length) {
  console.error("ESAT email-report verification failed:");
  failures.forEach(failure => console.error(`- ${failure}`));
  process.exit(1);
}

console.log(
  `ESAT email-report verification passed: ${folders.length} tests use absolute solution links, ` +
  `all three module analyses, and an idempotent shared EmailJS adapter.`,
);
