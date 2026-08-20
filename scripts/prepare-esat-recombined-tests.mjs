import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const testsRoot = path.join(root, "public", "esat-practice-tests", "tests");
const fullscreenVersion = "20260820-4";

const pathways = [
  "physics-chemistry",
  "physics-biology",
  "maths2-chemistry",
  "maths2-biology",
  "chemistry-biology",
];

const testIds = pathways.flatMap((pathway) =>
  [0, 1, 2].map((level) => `esat-${pathway}-level-${level}`),
);

const directPaper2 = 'paper2: `${analyses[1]}\\n\\n${analyses[2]}`';
const fullscreenSrc = `/shared/test-fullscreen.js?v=${fullscreenVersion}`;
const failures = [];
let changedFiles = 0;

for (const testId of testIds) {
  const htmlPath = path.join(testsRoot, testId, "index.html");
  if (!fs.existsSync(htmlPath)) {
    failures.push(`${testId}: index.html is missing.`);
    continue;
  }

  let html = fs.readFileSync(htmlPath, "utf8");
  const original = html;

  // Force the 15 generated papers to request the current shared controller.
  // Their old static query string otherwise allows a browser/CDN to keep an
  // earlier fullscreen/report controller even after the shared file changes.
  const fullscreenPattern = /\/shared\/test-fullscreen\.js(?:\?v=[^"'<>\s]*)?/g;
  const fullscreenMatches = html.match(fullscreenPattern) || [];
  if (!fullscreenMatches.length) {
    failures.push(`${testId}: shared fullscreen script reference is missing.`);
  } else {
    html = html.replace(fullscreenPattern, fullscreenSrc);
  }

  // Match the architecture of the five working Engineering tests: put the
  // third analysis into paper2 at the source instead of depending on a
  // runtime EmailJS monkey-patch. The current EmailJS template renders
  // paper1 and paper2, so this guarantees all three modules are present.
  if (!html.includes(directPaper2)) {
    const legacyPaper2 = /paper2:\s*analyses\[1\](?=\s*,)/;
    if (!legacyPaper2.test(html)) {
      failures.push(`${testId}: could not locate the legacy paper2 email payload.`);
    } else {
      html = html.replace(legacyPaper2, directPaper2);
    }
  }

  if (!html.includes("paper3: analyses[2]")) {
    failures.push(`${testId}: paper3 email payload is missing.`);
  }

  // Make the emailed Solution Book URL absolute using the host that actually
  // served the test. This avoids coupling reports to a hard-coded hostname.
  if (!/solution_link:\s*new URL\((?:solutionPDF|SOLUTION_LINK),\s*window\.location\.origin\)\.href/.test(html)) {
    const legacySolutionLink = /solution_link:\s*(solutionPDF|SOLUTION_LINK)\b/;
    const match = html.match(legacySolutionLink);
    if (!match) {
      failures.push(`${testId}: could not locate the Solution Book email field.`);
    } else {
      const variable = match[1];
      html = html.replace(
        legacySolutionLink,
        `solution_link: new URL(${variable}, window.location.origin).href`,
      );
    }
  }

  // Postconditions are deliberately strict: fail the build rather than ship
  // another green deployment with the old two-section email/runtime script.
  if (!html.includes(fullscreenSrc)) {
    failures.push(`${testId}: fullscreen controller cache-bust was not applied.`);
  }
  if (!html.includes(directPaper2)) {
    failures.push(`${testId}: section 3 was not folded into the rendered email payload.`);
  }
  if (!/solution_link:\s*new URL\((?:solutionPDF|SOLUTION_LINK),\s*window\.location\.origin\)\.href/.test(html)) {
    failures.push(`${testId}: Solution Book email URL is not absolute.`);
  }

  if (html !== original) {
    fs.writeFileSync(htmlPath, html, "utf8");
    changedFiles += 1;
  }
}

if (failures.length) {
  console.error("Recombined ESAT runtime preparation failed:");
  failures.forEach((failure) => console.error(`- ${failure}`));
  process.exit(1);
}

console.log(
  `Prepared ${testIds.length} recombined ESAT tests (${changedFiles} files updated) ` +
  `with direct 3-section email payloads and fullscreen controller ${fullscreenVersion}.`,
);
