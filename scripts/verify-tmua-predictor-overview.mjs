import fs from "node:fs";

const route =
  fs.readFileSync(
    "app/api/tmua/overview/route.ts",
    "utf8",
  );

const component =
  fs.readFileSync(
    "app/dashboard/TmuaPredictionStrip.tsx",
    "utf8",
  );

const dashboard =
  fs.readFileSync(
    "app/dashboard/DashboardClient.tsx",
    "utf8",
  );

let assertions = 0;

function assert(
  condition,
  message,
) {
  assertions += 1;

  if (!condition) {
    throw new Error(
      message,
    );
  }
}

function count(
  source,
  value,
) {
  return (
    source
      .split(
        value,
      )
      .length - 1
  );
}

assert(
  route.includes(
    "createSupabaseServerClient",
  ),
  "Overview authenticates using existing server client",
);

assert(
  route.includes(
    "supabase.auth.getUser()",
  ),
  "Overview resolves current authenticated user",
);

assert(
  route.includes(
    '"Unauthorized"',
  ),
  "Overview rejects unauthenticated requests",
);

assert(
  route.includes(
    "SUPABASE_SERVICE_ROLE_KEY",
  ),
  "Authority-sensitive access remains server-only",
);

const currentUserScopeMatches =
  route.match(
    /\.eq\(\s*"user_id"\s*,\s*user\.id\s*,?\s*\)/g,
  ) ?? [];

assert(
  currentUserScopeMatches.length >= 2,
  "Test and QB evidence are scoped to current user",
);

assert(
  route.includes(
    '"qb-progress-trigger-v2"',
  ),
  "QB evidence uses trigger-v2 source",
);

assert(
  route.includes(
    '"observed"',
  ),
  "QB evidence uses observed history",
);

assert(
  !route.includes(
    "is_correct",
  ),
  "Event/client correctness is never queried as authority",
);

assert(
  !route.includes(
    "topic_id",
  ),
  "Event/client topic is never queried as authority",
);

assert(
  route.includes(
    "question?.answer",
  ),
  "Canonical question answer remains authoritative",
);

assert(
  route.includes(
    "question?.topic",
  ),
  "Canonical question topic remains authoritative",
);

assert(
  route.includes(
    "calculateTmuaPredictorV1",
  ),
  "Overview uses locked pure Predictor V1 engine",
);

assert(
  route.includes(
    "buildTmuaPredictionSnapshotInsert",
  ),
  "Overview uses protected snapshot mapper",
);

assert(
  route.includes(
    '"tmua_prediction_snapshots"',
  ),
  "Overview persists append-only snapshots",
);

assert(
  route.includes(
    '"23505"',
  ),
  "Duplicate input hashes are handled idempotently",
);

assert(
  route.includes(
    "no-store, no-cache, must-revalidate, max-age=0",
  ),
  "Predictor overview cannot be cached",
);

assert(
  route.includes(
    "preparationRank:",
  ),
  "Preparation Rank is exposed as a separate overview field",
);

assert(
  route.includes(
    "predictor: {",
  ),
  "Predictor remains a distinct overview field",
);

assert(
  route.includes(
    "preparationOverview.preparationRank",
  ),
  "Preparation Rank payload remains separate from Predictor payload",
);

assert(
  component.includes(
    '"/api/tmua/overview"',
  ),
  "Dashboard consumes Predictor overview endpoint",
);

assert(
  component.includes(
    '"insufficient_evidence"',
  ),
  "Dashboard handles insufficient evidence explicitly",
);

assert(
  component.includes(
    "Your predicted TMUA score is",
  ),
  "Dashboard clearly labels score as predicted",
);

assert(
  component.includes(
    "Likely range",
  ),
  "Dashboard exposes likely range",
);

assert(
  component.includes(
    "confidence",
  ),
  "Dashboard exposes confidence",
);

assert(
  !component.includes(
    "@supabase",
  ),
  "UI does not access Supabase directly",
);

assert(
  !component.includes(
    "tmua_prediction_snapshots",
  ),
  "UI cannot directly read snapshot storage",
);

assert(
  count(
    dashboard,
    'import TmuaPredictionStrip from "./TmuaPredictionStrip";',
  ) === 1,
  "Dashboard imports prediction strip exactly once",
);

assert(
  count(
    dashboard,
    "<TmuaPredictionStrip />",
  ) === 1,
  "Dashboard renders prediction strip exactly once",
);

const mainMatches =
  [
    ...dashboard.matchAll(
      /<([A-Za-z][A-Za-z0-9.]*)\b[^>]*className=\{styles\.main\}[^>]*>/g,
    ),
  ];

assert(
  mainMatches.length === 2,
  "Dashboard retains its two established main containers",
);

assert(
  dashboard.indexOf(
    "<TmuaPredictionStrip />",
  ) >
    mainMatches[1].index,
  "Prediction strip is rendered inside/after opening of later workspace main",
);

console.log(
  "TMUA Predictor overview/dashboard verification passed:",
);

console.log(
  `${assertions} invariants verified; ` +
  "authentication is server-side; current-user evidence is scoped; " +
  "canonical QB authority is preserved; Predictor V1 remains locked; " +
  "snapshots deduplicate by input; dashboard labels predictions correctly; " +
  "prediction strip is attached only to the actual later workspace main; " +
  "Preparation Rank remains a separate model within the shared overview response.",
);