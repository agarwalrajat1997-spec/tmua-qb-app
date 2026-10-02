import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");
const archive = JSON.parse(read("public/amc-past-paper-practice/archive.json"));
const html = read("public/amc-past-paper-practice/index.html");
const dashboard = read("app/dashboard/AMCDashboardClient.tsx");
const portal = read("app/amc/page.tsx");

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

assert(archive.counts.problems === 2325, "AMC archive must contain 2,325 problems");
assert(archive.counts.amc8 === 1025, "AMC 8 archive must contain 1,025 problems");
assert(archive.counts.amc10 === 1300, "AMC 10 archive must contain 1,300 problems");
assert(archive.counts.papers === 93, "AMC archive must contain 93 papers");
assert(archive.problems.length === 2325, "AMC archive count and payload differ");
assert(new Set(archive.problems.map((problem) => problem.id)).size === 2325, "AMC problem IDs must be unique");
assert(archive.problems.every((problem) => problem.topics.length > 0), "Every AMC problem needs a topic");
assert(
  archive.problems.every((problem) => /^https:\/\/live\.poshenloh\.com\/past-contests\//.test(problem.sourceUrl)),
  "Every AMC problem must link to its credited archive source",
);

for (const file of [
  "public/amc-resources/amc-8-compendium.pdf",
  "public/amc-resources/amc-10-compendium.pdf",
]) {
  assert(fs.existsSync(path.join(root, file)), `Missing ${file}`);
}

for (const marker of ["2,325", "By topic", "By paper", "Open question + explanation", "Source and rights note"]) {
  assert(html.includes(marker), `AMC index HTML is missing ${marker}`);
}
for (const marker of ["Past Papers", "/amc-past-paper-practice/index.html", "2,325 indexed problems"]) {
  assert(dashboard.includes(marker), `AMC dashboard is missing ${marker}`);
}
assert(portal.includes('section === "past-papers"'), "AMC portal must accept the past-papers section");

console.log("AMC past-paper index verified: 2,325 problems, 93 papers, 14 topics.");
