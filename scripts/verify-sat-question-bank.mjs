import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");

const html = read("public/sat-qb-app/index.html");
const pageRoute = read("app/sat-question-bank/page.tsx");
const proxy = read("proxy.ts");
const listRoute = read("app/api/sat/qb/list/route.ts");
const questionRoute = read("app/api/sat/qb/question/route.ts");
const checkRoute = read("app/api/sat/qb/check/route.ts");
const reportRoute = read("app/api/sat/qb/report/route.ts");
const adminAuth = read("app/api/sat/qb/admin/_server.ts");
const adminListRoute = read("app/api/sat/qb/admin/reports/route.ts");
const adminUpdateRoute = read("app/api/sat/qb/admin/reports/[id]/route.ts");
const adminPage = read("app/sat-question-bank/admin/page.tsx");
const adminClient = read(
  "app/sat-question-bank/admin/AdminReportsClient.tsx"
);
const loadRoute = read("app/api/sat/qb/progress/load/route.ts");
const saveRoute = read("app/api/sat/qb/progress/save/route.ts");
const migration = read(
  "supabase/migrations/20260902053000_sat_qb_publish_and_reports.sql"
);
const publishRepairMigration = read(
  "supabase/migrations/20260902054600_fix_sat_qb_publish_where.sql"
);
const releasePython = read(
  "scripts/sat-qb-release/publish_sat_qb_release.py"
);
const releasePowerShell = read(
  "scripts/sat-qb-release/Publish-SAT-Question-Bank.ps1"
);

for (const marker of [
  "/api/sat/qb/list",
  "/api/sat/qb/question",
  "/api/sat/qb/check",
  "/api/sat/qb/progress/load",
  "/api/sat/qb/progress/save",
  "/api/sat/qb/report",
  "Report a problem",
  "nice_tip_html",
]) {
  assert.match(html, new RegExp(marker.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
}

assert.match(html, /Reading and Writing/);
assert.match(html, /<option>Math<\/option>/);
assert.match(html, /class="question-stage"/);
assert.match(html, /id="navigatorGrid"/);
assert.match(html, /id="flagButton"/);
assert.doesNotMatch(html, /EMAILJS_(PUBLIC_KEY|SERVICE_ID|TEMPLATE_ID)/);
assert.match(pageRoute, /src="\/sat-qb-app\/index\.html"/);
assert.doesNotMatch(pageRoute, /src="\/sat-question-bank\/index\.html"/);
assert.match(proxy, /prefix: "\/sat-qb-app", product: "sat-question-bank"/);
assert.match(proxy, /"\/sat-qb-app\/:path\*"/);

const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)]
  .map((match) => match[1])
  .filter((source) => source.trim());
assert.ok(scripts.length >= 2, "Expected MathJax config and SAT application scripts");
for (const source of scripts) new Function(source);

for (const route of [listRoute, questionRoute, checkRoute]) {
  assert.match(route, /sat_qb_questions/);
  assert.doesNotMatch(route, /SAT_qb_questions/);
}
assert.match(listRoute, /"Math", "Reading and Writing"/);
assert.match(loadRoute, /\.from\("sat_qb_progress"\)/);
assert.match(saveRoute, /\.from\("sat_qb_progress"\)/);
assert.match(reportRoute, /requireSATAccess/);
assert.match(reportRoute, /\.from\("sat_question_reports"\)/);
assert.match(adminAuth, /SAT_QB_ADMIN_EMAILS/);
assert.match(adminAuth, /agarwalrajat1997@gmail\.com/);
assert.match(adminListRoute, /requireSATAdmin/);
assert.match(adminListRoute, /\.from\("sat_question_reports"\)/);
assert.match(adminUpdateRoute, /moderation_history/);
assert.match(adminUpdateRoute, /\.eq\("id", id\)/);
assert.match(adminPage, /requireSATAdmin/);
assert.match(adminClient, /Export CSV/);
assert.match(adminClient, /Mark reviewing/);
assert.match(adminClient, /Resolve/);

assert.match(migration, /enable row level security/i);
assert.match(migration, /revoke all on table public\.sat_question_reports from anon, authenticated/i);
assert.match(migration, /publish_sat_qb_release/i);
assert.match(migration, /embedded image data remains/i);
assert.match(migration, /grant execute on function[\s\S]*to service_role/i);
for (const sql of [migration, publishRepairMigration]) {
  assert.match(
    sql,
    /update public\.sat_qb_questions[\s\S]*where is_active is distinct from true[\s\S]*or answer_verified is distinct from true/i
  );
}

assert.match(releasePython, /EXPECTED_AUTO_PASS = 230/);
assert.match(releasePython, /EXPECTED_CORRECTED = 265/);
assert.match(releasePython, /EXPECTED_FINAL = 595/);
assert.match(releasePython, /EXPECTED_EMBEDDED_IMAGES = 24/);
assert.match(releasePython, /publish_sat_qb_release/);
assert.match(releasePython, /data:image\//);
assert.match(releasePython, /sat-qb-manual-batch-\{batch_number:02d\}-of-06-reviewed\.json/);
assert.match(releasePowerShell, /PUBLISH-595-SAT-QUESTIONS/);
assert.match(releasePowerShell, /Read-Host[^\n]+-AsSecureString/);
assert.doesNotMatch(releasePowerShell, /\$LASTEXITCODE:/);

console.log(
  "SAT Question Bank verifier passed: client, lowercase Supabase tables, secure reports, and guarded publication contract."
);
