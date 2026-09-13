import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const dashboardPath = path.join(root, "app", "dashboard", "SATDashboardClient.tsx");
const packagePath = path.join(root, "package.json");

const resources = [
  {
    title: "Digital SAT Reading & Writing",
    href: "/sat-resources/digital-sat-reading-writing-thriving-scholars.pdf",
    file: "digital-sat-reading-writing-thriving-scholars.pdf",
    pages: 6,
    bytes: 329652,
    sha256: "93f8bd5294c84e59622542bf5fe2fc1d9a46db6c7ce9e77f8e0417dd5392f9fe",
  },
  {
    title: "Digital SAT Math Reference",
    href: "/sat-resources/digital-sat-math-reference-thriving-scholars.pdf",
    file: "digital-sat-math-reference-thriving-scholars.pdf",
    pages: 12,
    bytes: 967619,
    sha256: "03ad71b794275070fb0678a12fdcb12b07cad3492800008fb43d394fbbbc4287",
  },
];

assert.ok(fs.existsSync(dashboardPath), "SATDashboardClient.tsx is missing.");
const dashboard = fs.readFileSync(dashboardPath, "utf8");

for (const required of [
  'type SATTab = "bank" | "tests" | "resources";',
  'data-ui="TS_SAT_DASH_PORTAL_V2"',
  'SAT Resources',
  'SAT_RESOURCE_SECTIONS',
  'active === "resources"',
  'selectTab("resources")',
  'styles.resourceLibrary',
  'styles.resourceGrid',
  'styles.resourceCard',
  'styles.mobileNav',
  'These resources',
  'personal study use',
]) {
  assert.ok(dashboard.includes(required), `SAT resources UI is missing: ${required}`);
}

for (const resource of resources) {
  assert.ok(dashboard.includes(resource.title), `Dashboard is missing ${resource.title}.`);
  assert.ok(dashboard.includes(resource.href), `Dashboard is missing ${resource.href}.`);
  assert.ok(
    dashboard.includes(`pages: ${resource.pages}`),
    `${resource.title} does not display the verified ${resource.pages}-page count.`,
  );

  const pdfPath = path.join(root, "public", "sat-resources", resource.file);
  assert.ok(fs.existsSync(pdfPath), `Missing SAT resource PDF: ${pdfPath}`);

  const bytes = fs.readFileSync(pdfPath);
  assert.equal(bytes.subarray(0, 5).toString("ascii"), "%PDF-", `${resource.file} is not a PDF.`);
  assert.equal(bytes.length, resource.bytes, `${resource.file} byte size changed.`);
  assert.equal(
    crypto.createHash("sha256").update(bytes).digest("hex"),
    resource.sha256,
    `${resource.file} checksum changed.`,
  );
}

const packageJson = JSON.parse(fs.readFileSync(packagePath, "utf8"));
assert.equal(
  packageJson.scripts?.["verify:sat-resources"],
  "node scripts/verify-sat-resources.mjs",
  "package.json is missing verify:sat-resources.",
);
assert.ok(
  String(packageJson.scripts?.prebuild || "").includes("npm run verify:sat-resources"),
  "The SAT resource verifier is not protected by prebuild.",
);

console.log(
  "SAT resources verification passed: 2 verified PDFs, 18 pages, shared resource-card UI, mobile navigation and prebuild protection.",
);
