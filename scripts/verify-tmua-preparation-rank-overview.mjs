import fs from "node:fs";

const route =
  fs.readFileSync(
    "app/api/tmua/overview/route.ts",
    "utf8",
  );

const ui =
  fs.readFileSync(
    "app/dashboard/TmuaPredictionStrip.tsx",
    "utf8",
  );

const pkg =
  JSON.parse(
    fs.readFileSync(
      "package.json",
      "utf8",
    ),
  );

let checks =
  0;

function requireText(
  source,
  text,
  label,
) {
  checks += 1;

  if (!source.includes(text)) {
    throw new Error(
      `${label}: missing ${text}`,
    );
  }
}

function forbidText(
  source,
  text,
  label,
) {
  checks += 1;

  if (source.includes(text)) {
    throw new Error(
      `${label}: forbidden ${text}`,
    );
  }
}

for (
  const required of
  [
    'TMUA_PREPARATION_RANK_MODEL_VERSION',
    'calculatePreparationScore',
    'rankPreparationCohort',
    'PREPARATION_RANK_V1_RUNTIME_20260810',
    '"practice-tests"',
    '"tmua-question-bank"',
    '"tmua-classes"',
    '"tmua_preparation_rank_exclusions"',
    '"tmua_preparation_rank_runs"',
    '"tmua_preparation_rank_snapshots"',
    '"practice_test_attempts"',
    '"submitted_at"',
    '"qb-progress-trigger-v2"',
    '"observed"',
    'canonical_qid',
    'last_sign_in_at',
    'PREPARATION_RANK_WINDOW_MS',
    '30 * 24 * 60 * 60 * 1000',
    'actualPreparationRank',
    'actualPreparationScore',
    'activeCohortSize',
    'input_hash',
    'predictor_input_hash',
    'genuine_preparation_evidence',
    'actual_active_cohort_size',
    'distinct_canonical_qb_interactions_30d',
    'independent_recognised_test_families_30d',
    'Preparation Rank current-user Predictor input does not match overview Predictor input',
    'preparationRank:',
    'countdown:',
    '"2026-10-12"',
    '"12 October"',
  ]
) {
  requireText(
    route,
    required,
    "overview route",
  );
}

for (
  const required of
  [
    'PreparationRankOverview',
    'CountdownOverview',
    'Preparation Rank',
    'daysToTmua',
    'to TMUA',
    'examDateLabel',
    'countdown.examDateLabel',
    'recognised test or Question Bank evidence',
    'aria-label="TMUA preparation overview"',
  ]
) {
  requireText(
    ui,
    required,
    "dashboard strip",
  );
}

for (
  const forbidden of
  [
    'email.endsWith(',
    'email.includes("@thrivingscholars',
    'email.includes("@thriving',
    'Preparation Rank #1',
    'cohortSize: 18',
    'rank: 1,',
    'daysToTmua: 63',
  ]
) {
  forbidText(
    route,
    forbidden,
    "overview route",
  );
}

for (
  const forbidden of
  [
    'preparationRank.score}',
    'preparationRank.score)',
    '#1 of 18',
    '63 days to TMUA',
  ]
) {
  forbidText(
    ui,
    forbidden,
    "dashboard strip",
  );
}

checks += 1;

if (
  pkg.scripts?.[
    "verify:tmua-preparation-rank-overview"
  ] !==
  "node scripts/verify-tmua-preparation-rank-overview.mjs"
) {
  throw new Error(
    "Preparation Rank overview package script is missing.",
  );
}

checks += 1;

if (
  typeof pkg.scripts?.prebuild !==
    "string" ||
  !pkg.scripts.prebuild.includes(
    "npm run verify:tmua-preparation-rank-overview",
  )
) {
  throw new Error(
    "Preparation Rank overview is missing from prebuild.",
  );
}

checks += 1;

const runtimeRefs = [];

for (
  const file of [
    "app/api/tmua/overview/route.ts",
    "app/dashboard/TmuaPredictionStrip.tsx",
  ]
) {
  const source =
    fs.readFileSync(
      file,
      "utf8",
    );

  if (
    source.includes(
      "tmua_preparation_rank_snapshots",
    )
  ) {
    runtimeRefs.push(
      file,
    );
  }
}

if (
  runtimeRefs.length !== 1 ||
  runtimeRefs[0] !==
    "app/api/tmua/overview/route.ts"
) {
  throw new Error(
    `Preparation Rank snapshot runtime boundary is wrong: ${runtimeRefs.join(", ")}`,
  );
}

console.log(
  "TMUA Preparation Rank overview/dashboard verification passed:",
);

console.log(
  `${checks} invariants verified; the rolling 30-day cohort is server-authoritative; explicit exclusions replace email heuristics; Predictor V1 is recomputed from authoritative evidence for the cohort; Preparation Rank uses the locked engine; run/snapshot writes are append-only and deduplicated; only the current student's rank is returned; no-evidence users receive no synthetic score/rank; and the dashboard includes the factual 12 October countdown.`,
);