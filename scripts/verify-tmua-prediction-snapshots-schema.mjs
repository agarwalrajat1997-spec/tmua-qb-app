import fs from "node:fs";
import path from "node:path";

const root = process.cwd();

const migrationName =
  "20260810043000_tmua_prediction_snapshots.sql";

const migrationPath =
  path.join(
    root,
    "supabase",
    "migrations",
    migrationName,
  );

const specPath =
  path.join(
    root,
    "lib",
    "server",
    "tmua-predictor-v1-spec.json",
  );

let assertions = 0;

function assert(condition, message) {
  assertions += 1;

  if (!condition) {
    throw new Error(message);
  }
}

function normalized(text) {
  return text
    .replace(/^\uFEFF/, "")
    .replace(/\r\n/g, "\n");
}

function compact(text) {
  return normalized(text)
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();
}

function has(fragment, message) {
  assert(
    sqlCompact.includes(
      fragment
        .replace(/\s+/g, " ")
        .trim()
        .toLowerCase(),
    ),
    message,
  );
}

assert(
  fs.existsSync(migrationPath),
  `Missing migration ${migrationName}`,
);

const migrationBytes =
  fs.readFileSync(migrationPath);

assert(
  !(
    migrationBytes.length >= 3 &&
    migrationBytes[0] === 0xef &&
    migrationBytes[1] === 0xbb &&
    migrationBytes[2] === 0xbf
  ),
  "Snapshot migration must be UTF-8 without BOM",
);

const sql =
  normalized(
    migrationBytes.toString("utf8"),
  );

const sqlCompact =
  compact(sql);

const spec =
  JSON.parse(
    normalized(
      fs.readFileSync(
        specPath,
        "utf8",
      ),
    ),
  );

/*
 * ==========================================================
 * SPEC ↔ SCHEMA IDENTITY
 * ==========================================================
 */

assert(
  spec.snapshot_policy.future_table ===
    "tmua_prediction_snapshots",
  "Predictor V1 spec future table changed unexpectedly",
);

assert(
  spec.snapshot_policy.append_only === true,
  "Predictor V1 snapshots must remain append-only",
);

assert(
  spec.snapshot_policy
    .deduplicate_identical_inputs === true,
  "Predictor V1 must deduplicate identical inputs",
);

assert(
  JSON.stringify(
    spec.snapshot_policy.deduplication_key,
  ) ===
    JSON.stringify([
      "user_id",
      "model_version",
      "input_hash",
    ]),
  "Snapshot deduplication key changed unexpectedly",
);

/*
 * ==========================================================
 * EXACT MIGRATION IDENTITY
 * ==========================================================
 */

const migrationsDir =
  path.join(
    root,
    "supabase",
    "migrations",
  );

const snapshotMigrations =
  fs.readdirSync(migrationsDir)
    .filter(
      (name) =>
        name.endsWith(".sql") &&
        name.includes(
          "tmua_prediction_snapshot",
        ),
    );

assert(
  snapshotMigrations.length === 1,
  `Expected exactly one TMUA prediction-snapshot migration; found ${snapshotMigrations.length}`,
);

assert(
  snapshotMigrations[0] ===
    migrationName,
  "Unexpected TMUA prediction-snapshot migration filename",
);

/*
 * ==========================================================
 * REQUIRED TABLE + TYPED PROVENANCE
 * ==========================================================
 */

has(
  "create table public.tmua_prediction_snapshots",
  "Snapshot table must fail closed if it already exists",
);

for (
  const column of [
    "id uuid primary key default gen_random_uuid()",
    "user_id uuid not null",
    "model_version text not null",
    "input_hash text not null",
    "prediction_status text not null",
    "predicted_tmua_score9 numeric(4,2)",
    "lower_bound numeric(4,2)",
    "upper_bound numeric(4,2)",
    "confidence text",
    "test_signal_score9 numeric(4,2)",
    "test_weight numeric(9,4)",
    "test_evidence_count integer",
    "independent_test_count integer",
    "combined_full_count integer",
    "qb_signal_score9 numeric(4,2)",
    "qb_weight numeric(9,4)",
    "qb_unique_questions integer",
    "qb_topic_coverage numeric(7,4)",
    "conversion_set_hash text not null",
    "active_topic_set_hash text not null",
    "evidence_details jsonb",
    "calculated_at timestamptz",
    "created_at timestamptz",
  ]
) {
  has(
    column,
    `Missing required snapshot column contract: ${column}`,
  );
}

has(
  "references auth.users(id) on delete cascade",
  "Snapshot rows must retain authenticated-user ownership",
);

/*
 * ==========================================================
 * NO FAKE PREDICTIONS
 * ==========================================================
 */

has(
  "prediction_status in ( 'predicted', 'insufficient_evidence' )",
  "Prediction status must be constrained",
);

has(
  "prediction_status = 'insufficient_evidence' and predicted_tmua_score9 is null",
  "Insufficient evidence must not receive a synthetic score",
);

has(
  "prediction_status = 'predicted' and predicted_tmua_score9 is not null",
  "Predicted snapshots require an actual prediction",
);

has(
  "lower_bound <= predicted_tmua_score9",
  "Prediction must remain above its lower bound",
);

has(
  "predicted_tmua_score9 <= upper_bound",
  "Prediction must remain below its upper bound",
);

/*
 * ==========================================================
 * SCORE / EVIDENCE CONSTRAINTS
 * ==========================================================
 */

has(
  "predicted_tmua_score9 between 1 and 9",
  "Predicted TMUA score must remain on 1-9 scale",
);

has(
  "test_signal_score9 between 1 and 9",
  "Test signal must remain on 1-9 scale",
);

has(
  "qb_signal_score9 between 2.5 and 8.5",
  "QB signal must respect Predictor V1 clamp",
);

has(
  "qb_topic_coverage >= 0 and qb_topic_coverage <= 1",
  "QB topic coverage must remain bounded",
);

has(
  "independent_test_count <= test_evidence_count",
  "Independent tests cannot exceed contributing test evidence",
);

has(
  "combined_full_count <= independent_test_count",
  "Combined full families cannot exceed independent test families",
);

has(
  "qb_unique_questions < 30 and qb_signal_score9 is null and qb_weight = 0",
  "QB cannot influence prediction below 30 unique questions",
);

has(
  "qb_unique_questions >= 30 and qb_signal_score9 is not null and qb_weight > 0",
  "Activated QB evidence requires a positive model weight",
);

/*
 * ==========================================================
 * DEDUP + QUERY INDEXES
 * ==========================================================
 */

has(
  "unique ( user_id, model_version, input_hash )",
  "Identical model inputs must deduplicate per user",
);

has(
  "tmua_prediction_snapshots_user_calculated_idx on public.tmua_prediction_snapshots ( user_id, calculated_at desc )",
  "Missing current/history user index",
);

has(
  "tmua_prediction_snapshots_model_calculated_idx on public.tmua_prediction_snapshots ( model_version, calculated_at desc )",
  "Missing model shadow-analysis index",
);

/*
 * ==========================================================
 * RLS / APPEND-ONLY APPLICATION CONTRACT
 * ==========================================================
 */

has(
  "alter table public.tmua_prediction_snapshots enable row level security",
  "Prediction snapshots must have RLS enabled",
);

has(
  "create policy tmua_prediction_snapshots_select_own on public.tmua_prediction_snapshots for select to authenticated using ( auth.uid() = user_id )",
  "Students must only read their own snapshots",
);

has(
  "revoke all on table public.tmua_prediction_snapshots from anon",
  "Anonymous users must receive no snapshot table privileges",
);

has(
  "revoke all on table public.tmua_prediction_snapshots from authenticated",
  "Authenticated default write privileges must be removed",
);

has(
  "grant select on table public.tmua_prediction_snapshots to authenticated",
  "Authenticated students need own-row SELECT access",
);

has(
  "revoke all on table public.tmua_prediction_snapshots from service_role",
  "Service-role default mutation privileges must be reset",
);

has(
  "grant select, insert on table public.tmua_prediction_snapshots to service_role",
  "Server may only SELECT and append snapshots",
);

assert(
  !sqlCompact.includes(
    "grant update",
  ),
  "No application role may be granted snapshot UPDATE",
);

assert(
  !sqlCompact.includes(
    "grant delete",
  ),
  "No application role may be granted snapshot DELETE",
);

const policyBlocks =
  [
    ...sql.matchAll(
      /create\s+policy[\s\S]*?;/gi,
    ),
  ].map(
    (match) =>
      compact(match[0]),
  );

assert(
  policyBlocks.length === 1,
  `Expected exactly one RLS policy; found ${policyBlocks.length}`,
);

assert(
  policyBlocks[0].includes(
    "for select",
  ),
  "The sole RLS policy must be SELECT-only",
);

for (
  const forbidden of [
    "for insert",
    "for update",
    "for delete",
    "for all",
  ]
) {
  assert(
    !policyBlocks[0].includes(
      forbidden,
    ),
    `Forbidden snapshot policy capability: ${forbidden}`,
  );
}

/*
 * ==========================================================
 * SCHEMA-ONLY STAGE
 * ==========================================================
 */

function walk(directory) {
  if (!fs.existsSync(directory)) {
    return [];
  }

  const results = [];

  for (
    const entry of
    fs.readdirSync(
      directory,
      {
        withFileTypes: true,
      },
    )
  ) {
    const full =
      path.join(
        directory,
        entry.name,
      );

    if (entry.isDirectory()) {
      if (
        entry.name === "node_modules" ||
        entry.name === ".next"
      ) {
        continue;
      }

      results.push(
        ...walk(full),
      );

      continue;
    }

    if (
      /\.(?:ts|tsx|js|mjs)$/.test(
        entry.name,
      )
    ) {
      results.push(full);
    }
  }

  return results;
}

const forbiddenRuntimeReferences = [];

for (
  const file of [
    ...walk(
      path.join(
        root,
        "app",
      ),
    ),
    ...walk(
      path.join(
        root,
        "lib",
      ),
    ),
  ]
) {
  const relative =
    path
      .relative(
        root,
        file,
      )
      .replace(/\\/g, "/");

  if (
    relative ===
      "lib/server/tmua-predictor-v1-spec.json"
  ) {
    continue;
  }

  const source =
    fs.readFileSync(
      file,
      "utf8",
    );

  if (
    source.includes(
      "tmua_prediction_snapshots",
    )
  ) {
    forbiddenRuntimeReferences.push(
      relative,
    );
  }
}

assert(
  forbiddenRuntimeReferences.length === 0,
  "Phase 3B1-A must remain schema-only; runtime snapshot references found in: " +
    forbiddenRuntimeReferences.join(", "),
);

console.log(
  "TMUA prediction-snapshot schema verification passed:",
);

console.log(
  `${assertions} invariants verified; ` +
  "snapshots are append-only at application-role level; " +
  "students have own-row read access only; " +
  "insufficient evidence cannot receive a synthetic score; " +
  "scores, weights and counts are constrained; " +
  "QB cannot activate below 30 unique questions; " +
  "typed provenance and deterministic deduplication are protected; " +
  "Phase 3B1-A remains schema-only.",
);