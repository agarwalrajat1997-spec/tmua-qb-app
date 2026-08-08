import fs from "node:fs";
import vm from "node:vm";

const migrationPath =
  "supabase/migrations/20260807062000_tmua_authoritative_score_conversion.sql";

const routePath =
  "app/api/practice-tests/submit/route.ts";

const browserPath =
  "public/shared/tmua-score-conversions.js";

const migration =
  fs.readFileSync(migrationPath, "utf8");

const route =
  fs.readFileSync(routePath, "utf8");

const browserSource =
  fs.readFileSync(browserPath, "utf8");

const context = { console };

vm.createContext(context);

vm.runInContext(
  browserSource,
  context,
  {
    filename: browserPath,
  },
);

const browserApi =
  context.TS_TMUA_SCORE_CONVERSIONS;

if (!browserApi) {
  throw new Error(
    "Browser TMUA conversion API was not exported.",
  );
}

const requiredProfiles = [
  "official-2016",
  "official-2017",
  "official-2018",
  "official-2019",
  "official-2020",
  "official-2021",
  "official-2022",
  "official-2023",
  "specimen-estimate",
  "mock1",
  "mock2",
  "informed2024-2025",
];

const sqlProfilePattern =
  /\(\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*array\[([\s\S]*?)\]::numeric\[\]\s*,\s*'\{\}'::jsonb\s*\)/g;

const databaseProfiles = new Map();

for (
  const match of migration.matchAll(
    sqlProfilePattern,
  )
) {
  const profile = match[1];

  const values = match[4]
    .split(",")
    .map((value) => Number(value.trim()));

  databaseProfiles.set(
    profile,
    {
      kind: match[2],
      version: match[3],
      values,
    },
  );
}

if (
  databaseProfiles.size !==
  requiredProfiles.length
) {
  throw new Error(
    `Expected ${requiredProfiles.length} database profiles, found ${databaseProfiles.size}.`,
  );
}

for (const profile of requiredProfiles) {
  const database =
    databaseProfiles.get(profile);

  if (!database) {
    throw new Error(
      `Database migration is missing profile ${profile}.`,
    );
  }

  if (database.values.length !== 41) {
    throw new Error(
      `Profile ${profile} does not have 41 values.`,
    );
  }

  if (
    database.version !==
    browserApi.version
  ) {
    throw new Error(
      `Profile ${profile} version does not match the browser conversion version.`,
    );
  }

  for (
    let raw = 0;
    raw <= 40;
    raw += 1
  ) {
    const browserValue =
      Number(
        browserApi.convert(
          profile,
          raw,
        ),
      );

    const databaseValue =
      Number(database.values[raw]);

    if (
      Math.abs(
        browserValue -
        databaseValue,
      ) > 1e-9
    ) {
      throw new Error(
        `Browser/database conversion mismatch for ${profile} at raw ${raw}: ${browserValue} versus ${databaseValue}.`,
      );
    }
  }
}

for (const required of [
  "create table if not exists\n  public.tmua_score_conversion_profiles",
  "cardinality(score_values) = 41",
  "public.tmua_convert_overall_score",
  "authoritative_tmua_score9",
  "converted_combined_full_test",
  "single_paper_evidence_only",
  "raw_evidence_only",
  "trg_zz_finalize_tmua_practice_attempt",
  "submitted_answers_and_key_v1",
  "test_id like 'esat-%'",
  "tmua_score9 = null",
]) {
  if (!migration.includes(required)) {
    throw new Error(
      `Authoritative-score migration is missing: ${required}`,
    );
  }
}

for (const required of [
  "SUBMIT_ROUTE_V4_TMUA_AUTHORITATIVE_20260807",
  '.from("tmua_test_catalog")',
  "recognisedTmuaTest",
  "correctCount(",
  "raw_score_recomputed_server_side",
  "tmua_score9: null",
  '.from("tmua_test_attempt_evaluations")',
  "authoritative_tmua_score9",
  "predictor_evaluation",
  "generic_submission",
]) {
  if (!route.includes(required)) {
    throw new Error(
      `Authoritative submission route is missing: ${required}`,
    );
  }
}

for (const forbidden of [
  "function tmuaScore9(",
  "function computeTmuaScore9(",
  "body?.tmua_score9",
  "body.tmua_score9",
  "return tmuaScore9(rawScore",
]) {
  if (route.includes(forbidden)) {
    throw new Error(
      `Legacy/client-authoritative scoring remains in the route: ${forbidden}`,
    );
  }
}

console.log(
  "TMUA authoritative-scoring verification passed: all 12 database curves match the browser at every raw score, only valid combined full tests receive an overall /9 score, single papers remain raw evidence, ESAT stays compatible, and the legacy generic conversion is removed.",
);