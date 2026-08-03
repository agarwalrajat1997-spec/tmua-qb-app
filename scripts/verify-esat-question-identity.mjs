import fs from "node:fs";
import path from "node:path";

const root = process.cwd();

const htmlPath = path.join(
  root,
  "public",
  "esat-question-bank",
  "index.html"
);

const routePath = path.join(
  root,
  "app",
  "api",
  "esat",
  "qb",
  "question",
  "route.ts"
);

const html = fs.readFileSync(htmlPath, "utf8");
const route = fs.readFileSync(routePath, "utf8");

function requireText(source, text, label) {
  if (!source.includes(text)) {
    throw new Error(
      `[ESAT identity guard] Missing ${label}: ${text}`
    );
  }
}

function rejectText(source, text, label) {
  if (source.includes(text)) {
    throw new Error(
      `[ESAT identity guard] Forbidden ${label}: ${text}`
    );
  }
}

function occurrenceCount(source, text) {
  return source.split(text).length - 1;
}

requireText(
  route,
  "TS_ESAT_STRICT_IDENTITY_V1",
  "strict server-route marker"
);

requireText(
  route,
  'code: "QID_REQUIRED"',
  "missing-identity rejection"
);

requireText(
  route,
  "Positional question lookup is disabled",
  "positional lookup rejection"
);

rejectText(
  route,
  'searchParams.get("display_order")',
  "server display_order lookup"
);

rejectText(
  route,
  "cleanRows(",
  "full-table positional sorting"
);

rejectText(
  route,
  ".limit(3000)",
  "full-table positional loading"
);

rejectText(
  route,
  "sorted[displayOrder - 1]",
  "array-position question loading"
);

requireText(
  html,
  "TS_ESAT_IDENTITY_LOCK_V1",
  "frontend identity-lock marker"
);

requireText(
  html,
  "TS_ESAT_NO_IDENTITY_FALLBACK_V1",
  "strict RPC resolver marker"
);

requireText(
  html,
  "qid: q.qid || null",
  "real qid metadata mapping"
);

requireText(
  html,
  "id: q.id || null",
  "database id metadata mapping"
);

requireText(
  html,
  "currentQuestion = await loadQuestion(meta);",
  "identity-based render call"
);

rejectText(
  html,
  "currentQuestion = await loadQuestion(meta.display_order);",
  "positional render call"
);

rejectText(
  html,
  "return getQuestionByDisplayOrder(displayOrder);",
  "silent ordinal fallback"
);

rejectText(
  html,
  "Fall through to the ordered identifiers for compatibility.",
  "silent compatibility fallback"
);

if (
  occurrenceCount(html, "id: meta.id || null") < 2 ||
  occurrenceCount(html, "qid: meta.qid || null") < 2
) {
  throw new Error(
    "[ESAT identity guard] Both question loading and answer checking must send id/qid."
  );
}

console.log(
  "ESAT identity verification passed: stable id/qid loading is enforced."
);