import fs from "node:fs";
import path from "node:path";

const root = process.cwd();

const htmlPath = path.join(
  root,
  "public",
  "esat-question-bank",
  "index.html"
);

const questionRoutePath = path.join(
  root,
  "app",
  "api",
  "esat",
  "qb",
  "question",
  "route.ts"
);

const listRoutePath = path.join(
  root,
  "app",
  "api",
  "esat",
  "qb",
  "list",
  "route.ts"
);

const progressSaveRoutePath = path.join(
  root,
  "app",
  "api",
  "qb",
  "progress",
  "save",
  "route.ts"
);

const html = fs.readFileSync(htmlPath, "utf8");
const questionRoute = fs.readFileSync(
  questionRoutePath,
  "utf8"
);
const listRoute = fs.readFileSync(listRoutePath, "utf8");
const progressSaveRoute = fs.readFileSync(
  progressSaveRoutePath,
  "utf8"
);

function fail(message) {
  throw new Error(`[ESAT identity guard] ${message}`);
}

function requireText(source, text, label) {
  if (!source.includes(text)) {
    fail(`Missing ${label}: ${text}`);
  }
}

function rejectText(source, text, label) {
  if (source.includes(text)) {
    fail(`Forbidden ${label}: ${text}`);
  }
}

function requireMatch(source, regex, label) {
  if (!regex.test(source)) {
    fail(`Missing ${label}: ${regex}`);
  }
}

/*
 * Server lock:
 * The full-question API accepts only qid/id. It must never
 * interpret display_order as a row position.
 */
requireText(
  questionRoute,
  "TS_ESAT_STRICT_IDENTITY_V1",
  "strict server marker"
);

requireText(
  questionRoute,
  'code: "QID_REQUIRED"',
  "missing-identity rejection"
);

requireText(
  questionRoute,
  "Positional question lookup is disabled",
  "positional-lookup rejection"
);

requireMatch(
  questionRoute,
  /searchParams\.get\("qid"\)[\s\S]{0,160}?searchParams\.get\("id"\)/,
  "qid/id request parsing"
);

rejectText(
  questionRoute,
  'searchParams.get("display_order")',
  "server display_order request"
);

rejectText(
  questionRoute,
  'searchParams.get("db_display_order")',
  "server database-order request"
);

rejectText(
  questionRoute,
  "cleanRows(",
  "full-list positional sorting"
);

rejectText(
  questionRoute,
  "sorted[displayOrder - 1]",
  "array-position lookup"
);

/*
 * Metadata source lock:
 * The API listâ€”not a particular frontend formatting styleâ€”is
 * responsible for supplying the real qid. The frontend may keep
 * the returned rows directly or map them.
 */
requireMatch(
  listRoute,
  /\bqid\s*:\s*q\.qid\b/,
  "real qid in the ESAT list response"
);

requireMatch(
  listRoute,
  /\bdb_display_order\s*:\s*q\.display_order\b/,
  "database display order in the ESAT list response"
);

/*
 * Frontend load lock:
 * Rendering passes the complete metadata object. loadQuestion()
 * derives a stable identity from id/qid and validates the returned
 * record before it is shown.
 */
requireText(
  html,
  "TS_ESAT_IDENTITY_LOCK_V1",
  "frontend identity-lock marker"
);

requireText(
  html,
  "currentQuestion = await loadQuestion(meta);",
  "metadata-based render call"
);

requireMatch(
  html,
  /async function loadQuestion\(meta\)\s*\{[\s\S]{0,1800}?meta\.id\s*\|\|\s*meta\.qid[\s\S]{0,1800}?returnedIdentities\.includes\(expectedIdentity\)/,
  "stable loadQuestion identity validation"
);

rejectText(
  html,
  "currentQuestion = await loadQuestion(meta.display_order);",
  "positional render call"
);

/*
 * RPC bridge lock:
 * Both question loading and answer checking are intercepted by the
 * same strict resolver. It may use body.id/body.qid only.
 */
requireText(
  html,
  "TS_ESAT_NO_IDENTITY_FALLBACK_V1",
  "strict resolver marker"
);

requireMatch(
  html,
  /async function resolveQuestion\(body\)\s*\{[\s\S]{0,700}?body\.id\s*\|\|\s*body\.qid[\s\S]{0,700}?return getQuestionByQid\(identity\)/,
  "strict resolver implementation"
);

rejectText(
  html,
  "return getQuestionByDisplayOrder(displayOrder);",
  "ordinal fallback call"
);

rejectText(
  html,
  "Fall through to the ordered identifiers for compatibility.",
  "compatibility fallback"
);

/*
 * Request payload lock:
 * Question loading and answer checking must both send the stable
 * id/qid pair. This does not depend on how loadAllMeta() is written.
 */
requireMatch(
  html,
  /esat_qb_public_question[\s\S]{0,500}?id\s*:\s*meta\.id\s*\|\|\s*null[\s\S]{0,300}?qid\s*:\s*meta\.qid\s*\|\|\s*null/,
  "question-loading id/qid payload"
);

requireMatch(
  html,
  /esat_qb_public_check[\s\S]{0,500}?id\s*:\s*meta\.id\s*\|\|\s*null[\s\S]{0,300}?qid\s*:\s*meta\.qid\s*\|\|\s*null/,
  "answer-checking id/qid payload"
);

/*
 * The old synthetic qid caused positional identity to masquerade
 * as a stable identifier. It must never return.
 */
rejectText(
  html,
  'qid: "SB-" + String(q.display_order)',
  "synthetic positional qid"
);

/*
 * Progress identity lock:
 * Question content and student progress must use the same canonical qid.
 * Numeric display positions are allowed only as read-only legacy aliases
 * during hydration and must never be used for a new save.
 */
requireText(
  html,
  "TS_ESAT_PROGRESS_QID_V1",
  "canonical progress marker"
);

requireText(
  html,
  "TS_ESAT_PROGRESS_BRIDGE_V1",
  "cross-script metadata bridge"
);

requireMatch(
  html,
  /function questionKey\(meta\)\s*\{[\s\S]{0,180}?meta\.qid\s*\|\|\s*meta\.id/,
  "canonical main-state key"
);

rejectText(
  html,
  "return String(meta.display_order);",
  "positional main-state key"
);

requireMatch(
  html,
  /function getQuestionKeys\(\)[\s\S]{0,500}?meta\.qid[\s\S]{0,160}?meta\.display_order/,
  "qid-first progress lookup"
);

requireText(
  html,
  'identity_version: PROGRESS_IDENTITY_VERSION',
  "canonical progress save version"
);

requireText(
  html,
  "await hydrateCanonicalProgress();",
  "server-authoritative canonical hydration"
);

requireText(
  html,
  "TS_ESAT_LEGACY_NUMERIC_UPLOAD_DISABLED_V1",
  "legacy numeric upload block"
);

requireText(
  progressSaveRoute,
  'const ESAT_PROGRESS_IDENTITY_VERSION = "esat-qid-v1";',
  "server ESAT progress identity version"
);

requireText(
  progressSaveRoute,
  'code: "ESAT_IDENTITY_VERSION_REQUIRED"',
  "stale-client rejection"
);

requireText(
  progressSaveRoute,
  'code: "ESAT_CANONICAL_QID_REQUIRED"',
  "noncanonical progress rejection"
);

console.log(
  "ESAT identity verification passed: question loading and progress persistence both use canonical qids."
);