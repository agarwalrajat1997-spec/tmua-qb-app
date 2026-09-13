import fs from "node:fs";
import path from "node:path";

const root = process.cwd();

const migrationPath =
  path.join(
    root,
    "supabase",
    "migrations",
    "20260810050000_tmua_preparation_rank_persistence.sql",
  );

const packagePath =
  path.join(
    root,
    "package.json",
  );

let checks = 0;

function check(
  condition,
  message,
) {
  checks += 1;

  if (!condition) {
    throw new Error(message);
  }
}

function contains(
  source,
  token,
  message,
) {
  check(
    source.includes(token),
    message,
  );
}

check(
  fs.existsSync(migrationPath),
  "Preparation Rank migration must exist",
);

const sql =
  fs.readFileSync(
    migrationPath,
    "utf8",
  ).replace(/\r\n/g, "\n");

contains(
  sql,
  "create table public.tmua_preparation_rank_exclusions",
  "explicit exclusion source is required",
);

contains(
  sql,
  "create table public.tmua_preparation_rank_runs",
  "rank-run table is required",
);

contains(
  sql,
  "create table public.tmua_preparation_rank_snapshots",
  "rank-snapshot table is required",
);

contains(
  sql,
  "decision in (",
  "exclusion decisions are constrained",
);

contains(
  sql,
  "'exclude'",
  "exclude decision exists",
);

contains(
  sql,
  "'include'",
  "include decision exists",
);

contains(
  sql,
  "Latest event per user wins",
  "exclusion source is explicitly event-based",
);

check(
  !sql.toLowerCase().includes(
    "email like",
  ),
  "email heuristics must not be used",
);

check(
  !sql.toLowerCase().includes(
    "email ilike",
  ),
  "email ILIKE heuristics must not be used",
);

contains(
  sql,
  "input_hash ~ '^[0-9a-f]{64}$'",
  "run input hash must be deterministic SHA-256 format",
);

contains(
  sql,
  "window_start =",
  "rank run must constrain cohort window",
);

contains(
  sql,
  "cohort_as_of - interval '30 days'",
  "cohort window is exactly 30 days",
);

contains(
  sql,
  "rankable_count <= active_cohort_size",
  "rankable population cannot exceed active cohort",
);

contains(
  sql,
  "unique (",
  "migration contains uniqueness protection",
);

contains(
  sql,
  "model_version,",
  "run dedupe includes model version",
);

contains(
  sql,
  "input_hash",
  "run dedupe includes input hash",
);

contains(
  sql,
  "actual_preparation_score double precision",
  "unrounded Preparation Score is persisted",
);

contains(
  sql,
  "actual_preparation_rank integer",
  "factual Preparation Rank is persisted",
);

contains(
  sql,
  "actual_active_cohort_size integer not null",
  "factual active cohort denominator is persisted",
);

contains(
  sql,
  "performance_component double precision not null",
  "performance component is persisted",
);

contains(
  sql,
  "breadth_component double precision not null",
  "breadth component is persisted",
);

contains(
  sql,
  "evidence_depth_component double precision not null",
  "depth component is persisted",
);

contains(
  sql,
  "recent_activity_component double precision not null",
  "activity component is persisted",
);

contains(
  sql,
  "consistency_component double precision not null",
  "consistency component is persisted",
);

contains(
  sql,
  "recovery_component double precision not null",
  "recovery component is persisted",
);

contains(
  sql,
  "predicted_tmua_score9 double precision",
  "Predictor contribution is auditable",
);

contains(
  sql,
  "predictor_input_hash text",
  "Predictor provenance can be linked",
);

contains(
  sql,
  "trusted_unique_first_exposures integer not null",
  "trusted QB depth evidence is persisted",
);

contains(
  sql,
  "trusted_canonical_topic_coverage double precision not null",
  "canonical QB breadth is persisted",
);

contains(
  sql,
  "distinct_canonical_qb_interactions_30d integer not null",
  "canonical QB activity count is persisted",
);

contains(
  sql,
  "independent_recognised_test_families_30d integer not null",
  "recognised test activity count is persisted",
);

contains(
  sql,
  "genuine_preparation_evidence boolean not null",
  "rank eligibility evidence state is explicit",
);

contains(
  sql,
  "genuine_preparation_evidence is false",
  "no-evidence state is constrained",
);

contains(
  sql,
  "actual_preparation_score is null",
  "no-evidence users cannot receive fake score",
);

contains(
  sql,
  "actual_preparation_rank is null",
  "no-evidence users cannot receive fake rank",
);

contains(
  sql,
  "actual_preparation_rank <=",
  "rank is constrained by cohort denominator",
);

contains(
  sql,
  "references public.tmua_preparation_rank_runs(id)",
  "snapshots belong to immutable runs",
);

contains(
  sql,
  "on delete restrict",
  "run deletion cannot cascade through snapshots",
);

contains(
  sql,
  "unique (\n            run_id,\n            user_id",
  "one snapshot per student per run",
);

for (const table of [
  "tmua_preparation_rank_exclusions",
  "tmua_preparation_rank_runs",
  "tmua_preparation_rank_snapshots",
]) {
  contains(
    sql,
    `alter table public.${table}\n    enable row level security`,
    `${table} must have RLS`,
  );
}

contains(
  sql,
  "revoke all on table public.tmua_preparation_rank_exclusions",
  "exclusion privileges start closed",
);

contains(
  sql,
  "revoke all on table public.tmua_preparation_rank_runs",
  "run privileges start closed",
);

contains(
  sql,
  "revoke all on table public.tmua_preparation_rank_snapshots",
  "snapshot privileges start closed",
);

contains(
  sql,
  "grant select, insert\n    on table public.tmua_preparation_rank_exclusions\n    to service_role",
  "service role may append exclusion decisions",
);

contains(
  sql,
  "grant select, insert\n    on table public.tmua_preparation_rank_runs\n    to service_role",
  "service role may append runs",
);

contains(
  sql,
  "grant select, insert\n    on table public.tmua_preparation_rank_snapshots\n    to service_role",
  "service role may append snapshots",
);

contains(
  sql,
  "grant select\n    on table public.tmua_preparation_rank_snapshots\n    to authenticated",
  "authenticated students may read snapshots",
);

contains(
  sql,
  "create policy tmua_preparation_rank_snapshots_select_own",
  "own-row SELECT policy must exist",
);

contains(
  sql,
  "auth.uid() = user_id",
  "own-row policy must scope to auth uid",
);

check(
  !/grant\s+(?:update|delete|all)[\s\S]{0,200}to\s+authenticated/i.test(
    sql,
  ),
  "authenticated mutation grants are forbidden",
);

check(
  !/grant\s+(?:update|delete|all)[\s\S]{0,200}to\s+service_role/i.test(
    sql,
  ),
  "service-role UPDATE/DELETE grants are forbidden",
);

check(
  !/create\s+policy[\s\S]{0,300}for\s+(?:insert|update|delete)[\s\S]{0,300}to\s+authenticated/i.test(
    sql,
  ),
  "authenticated mutation policies are forbidden",
);

check(
  !sql.includes(
    "tmua_prediction_snapshots",
  ),
  "Preparation Rank schema must not mutate Predictor snapshots",
);

check(
  !sql.includes(
    "alter table public.tmua_test_attempt_evaluations",
  ),
  "Preparation Rank schema must not alter authoritative test evidence",
);

check(
  !sql.includes(
    "alter table public.tmua_qb_attempt_events",
  ),
  "Preparation Rank schema must not alter QB evidence",
);

const pkg =
  JSON.parse(
    fs.readFileSync(
      packagePath,
      "utf8",
    ),
  );

check(
  pkg.scripts[
    "verify:tmua-preparation-rank-schema"
  ] ===
    "node scripts/verify-tmua-preparation-rank-schema.mjs",
  "package schema verifier command is locked",
);

const token =
  "npm run verify:tmua-preparation-rank-schema";

check(
  pkg.scripts.prebuild
    .split(token)
    .length - 1 === 1,
  "schema verifier must occur exactly once in prebuild",
);

console.log(
  "TMUA Preparation Rank persistence-schema verification passed:",
);

console.log(
  `${checks} invariants verified; ` +
  "exclusions are explicit append-only decisions; " +
  "runs and student snapshots are immutable at application-role level; " +
  "the cohort window is exactly 30 days; " +
  "students can read only their own snapshots; " +
  "service role has SELECT+INSERT but no UPDATE/DELETE grants; " +
  "login-only/no-evidence users cannot receive synthetic score or rank; " +
  "Preparation Rank persistence remains separate from Predictor V1.",
);
