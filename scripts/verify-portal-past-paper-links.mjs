import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const read = (file) => readFileSync(join(root, file), "utf8");
const expectedUrl =
  "https://www.thrivingscholars.com/post/free-tmua-esat-maths-past-paper-practice";
const destination = read("lib/past-paper-practice.ts");
const link = read("app/components/PastPaperPracticeLink.tsx");
const amc = read("app/dashboard/AMCDashboardClient.tsx");
const amcRoute = read("app/amc/page.tsx");
const nextConfig = read("next.config.ts");

assert.equal(
  destination.match(/export\s+const\s+PAST_PAPER_PRACTICE_URL\s*=\s*["']([^"']+)["']/)?.[1],
  expectedUrl,
  "Past-paper practice must point to the requested public maths practice page.",
);
assert.match(
  link,
  /import\s*\{\s*PAST_PAPER_PRACTICE_URL\s*\}\s*from\s*["']@\/lib\/past-paper-practice["']/,
  "The shared practice link must use the canonical destination.",
);

const anchor = link.match(/<a\b[^>]*>/)?.[0];
assert.ok(anchor, "The practice action must be an accessible anchor.");
assert.match(anchor, /href=\{PAST_PAPER_PRACTICE_URL\}/);
assert.match(anchor, /target=["']_blank["']/);
const rel = anchor.match(/rel=["']([^"']+)["']/)?.[1].split(/\s+/) ?? [];
assert.ok(rel.includes("noopener") && rel.includes("noreferrer"), "The new-tab practice link must include noopener and noreferrer.");
assert.match(link, /Want to focus on maths past papers\?/, "The practice action must have its descriptive title.");
assert.doesNotMatch(link, /<iframe\b/i, "The shared practice action must link to the page without embedding it.");

// Locate the whole question-bank card, including its nested action row, so a
// link moved elsewhere in the portal cannot accidentally satisfy this check.
function questionBankCard(source, buttonLabel, portalName) {
  const buttonPosition = source.indexOf(buttonLabel);
  assert.ok(buttonPosition >= 0, `${portalName} question-bank entry button is missing.`);
  const start = source.lastIndexOf("<div className={styles.card}>", buttonPosition);
  assert.ok(start >= 0, `${portalName} question-bank action card is missing.`);

  let depth = 0;
  for (const token of source.slice(start).matchAll(/<div(?=\s|>)|<\/div\s*>/g)) {
    depth += token[0].startsWith("</") ? -1 : 1;
    if (depth === 0) {
      const end = start + token.index + token[0].length;
      assert.ok(end > buttonPosition, `${portalName} entry button must remain inside its card.`);
      return source.slice(start, end);
    }
  }
  assert.fail(`${portalName} question-bank action card is not closed.`);
}

for (const portal of [
  { name: "AMC", file: "app/dashboard/AMCDashboardClient.tsx", button: "Open {activePaper?.paper} Question Bank" },
  { name: "TMUA", file: "app/dashboard/DashboardClient.tsx", button: "Open TMUA Question Bank" },
  { name: "ESAT", file: "app/esat/ESATDashboardClient.tsx", button: "Open ESAT Question Bank" },
]) {
  const source = read(portal.file);
  assert.match(source, /import\s+PastPaperPracticeLink\s+from\s+["'][^"']*\/PastPaperPracticeLink["']/);
  assert.equal((source.match(/<PastPaperPracticeLink\b/g) ?? []).length, 1, `${portal.name} must render one shared practice link.`);
  assert.match(
    questionBankCard(source, portal.button, portal.name),
    /<PastPaperPracticeLink\b/,
    `${portal.name} must place the practice link with its question-bank entry button.`,
  );
}

assert.doesNotMatch(amc, /["']Past Papers["']|["']past-papers["']|>\s*(?:AMC\s+)?Past Papers\s*</, "AMC must not retain its removed Past Papers view or navigation.");
assert.doesNotMatch(amc, /amc-past-paper-practice|pastPaperFrame|<iframe\b/, "AMC must not retain the embedded archive section.");
for (const preserved of ["Practice Tests", "Resources", "AMC 8", "AMC 10", "AMC 12"]) {
  assert.ok(amc.includes(preserved), `AMC must preserve ${preserved}.`);
}

assert.match(amcRoute, /import\s*\{\s*PAST_PAPER_PRACTICE_URL\s*\}\s*from\s*["']@\/lib\/past-paper-practice["']/);
const legacyRedirect = amcRoute.match(/if\s*\(section\s*===\s*["']past-papers["']\)\s*(?:\{\s*)?redirect\(PAST_PAPER_PRACTICE_URL\)/);
assert.ok(legacyRedirect, "Saved AMC past-papers section links must redirect to the public practice page.");
const authPosition = amcRoute.indexOf("await supabaseServer()");
assert.ok(authPosition >= 0 && legacyRedirect.index < authPosition, "The old past-papers link must redirect before authentication.");
const initialSection = amcRoute.slice(amcRoute.indexOf("initialSection={"));
assert.doesNotMatch(initialSection, /["']past-papers["']/, "The removed section must not be passed to the AMC dashboard.");

assert.match(
  nextConfig,
  /import\s*\{\s*PAST_PAPER_PRACTICE_URL\s*\}\s*from\s*["']\.\/lib\/past-paper-practice["']/,
  "The pre-authentication redirect must use the same canonical practice destination.",
);
const redirects = nextConfig.match(/async\s+redirects\s*\(\)\s*\{\s*return\s*\[([\s\S]*?)\]\s*;?\s*\}/)?.[1];
assert.ok(redirects, "Next configuration must provide redirects before the authentication proxy runs.");
assert.match(
  redirects,
  /\{\s*source\s*:\s*["']\/amc["']\s*,\s*has\s*:\s*\[\s*\{\s*type\s*:\s*["']query["']\s*,\s*key\s*:\s*["']section["']\s*,\s*value\s*:\s*["']past-papers["']\s*,?\s*\}\s*,?\s*\]\s*,\s*destination\s*:\s*PAST_PAPER_PRACTICE_URL\s*,\s*permanent\s*:\s*true\s*,?\s*\}/,
  "The permanent pre-authentication redirect must match only /amc with section=past-papers.",
);

const retiredArchivePages = ["/amc-past-paper-practice", "/amc-past-paper-practice/index.html"];
for (const source of retiredArchivePages) {
  const escaped = source.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  assert.match(
    redirects,
    new RegExp(`\\{\\s*source\\s*:\\s*["']${escaped}["']\\s*,\\s*destination\\s*:\\s*PAST_PAPER_PRACTICE_URL\\s*,\\s*permanent\\s*:\\s*true\\s*,?\\s*\\}`),
    `The retired ${source} page must redirect permanently to the canonical practice page.`,
  );
}
for (const [, source] of redirects.matchAll(/source\s*:\s*["']([^"']+)["']/g)) {
  if (source.startsWith("/amc-past-paper-practice")) {
    assert.ok(retiredArchivePages.includes(source), "AMC archive redirects must not capture assets or other archive data.");
  }
}

console.log("Portal past-paper links verified: all three question-bank cards, AMC navigation removal and public legacy redirect.");
