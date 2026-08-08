import fs from "node:fs";

const migration = fs
  .readFileSync(
    "supabase/migrations/20260807054500_tmua_test_catalog_and_validity.sql",
    "utf8",
  )
  .replace(/\r\n/g, "\n");

const requiredTestIds = [
  "full-mock-01-all-topics",
  "full-mock-02-all-topics",
  "full-official-2016",
  "full-official-2017",
  "full-official-2018",
  "full-official-2019",
  "full-official-2020",
  "full-official-2021",
  "full-official-2022",
  "full-official-2023",
  "full-specimen",
  "p1-mock-01-algebra-sequences-functions-geometry",
  "p1-mock-02-graphs-trig-logs",
  "p1-mock-03-calculus",
  "p2-mock-04-logic-proofs",
  "p1-mock-05-all-topics",
  "p2-mock-06-all-topics",
  "tmua-2024-2025-challenging-mock",
];

for (const testId of requiredTestIds) {
  if (!migration.includes(`'${testId}'`)) {
    throw new Error(`TMUA catalogue is missing ${testId}`);
  }
}

for (const required of [
  "create table if not exists public.tmua_test_catalog",
  "public.tmua_test_attempt_evaluations",
  "public.evaluate_tmua_test_attempt",
  "public.tmua_completion_factor",
  "public.tmua_timing_factor",
  "average_under_10_seconds",
  "minimum_full_weight_answered",
  "paper_1_effective_weight",
  "paper_2_effective_weight",
  "combined_score_eligible",
  "trg_evaluate_tmua_practice_attempt",
  "Unknown tests, including ESAT, are deliberately excluded.",
  "p_minimum_partial_answered integer",
  "p_minimum_full_weight_answered integer",
  "delete from public.tmua_test_attempt_evaluations",
  "0.7500 *",
  "v_p1_validity >= 0.7500",
  "v_p2_validity >= 0.7500",
  "greatest(",
  "'evaluation_version',",
  "'20260807-2'",
]) {
  if (!migration.includes(required)) {
    throw new Error(`TMUA validity migration is missing: ${required}`);
  }
}

for (const forbidden of [
  "'esat-mock-01'",
  "'esat-mock-02'",
  "'esat-mock-03'",
  "'esat-mock-04'",
  "'esat-engineering-full-mock-test-1'",
]) {
  if (migration.includes(forbidden)) {
    throw new Error(
      `ESAT test was incorrectly added to TMUA catalogue: ${forbidden}`,
    );
  }
}

const expectedCatalogueRows =
  (migration.match(/\(\n  '(?:full|p1|p2|tmua-)/g) || []).length;

if (expectedCatalogueRows !== 18) {
  throw new Error(
    `Expected 18 TMUA catalogue rows, found ${expectedCatalogueRows}`,
  );
}


const fullPaperWeightPattern =
  /v_p1_weight\s*:=\s*v_catalog\.base_weight\s*\*\s*0\.7500\s*\*\s*v_p1_validity;/;

if (!fullPaperWeightPattern.test(migration)) {
  throw new Error(
    "A valid Paper 1 from a full test is not protected at 0.75 weight.",
  );
}

const combinedValidityPattern =
  /v_p1_validity\s*>=\s*0\.7500[\s\S]*v_p2_validity\s*>=\s*0\.7500/;

if (!combinedValidityPattern.test(migration)) {
  throw new Error(
    "Combined full-test eligibility does not require both papers to have substantial validity.",
  );
}

const standalonePaperPattern =
  /else greatest\(\s*v_p1_weight,\s*v_p2_weight\s*\)/;

if (!standalonePaperPattern.test(migration)) {
  throw new Error(
    "A valid single paper is not preserved independently when the other paper is invalid.",
  );
}
console.log(
  "TMUA test-catalogue verification passed: 18 recognised tests, independent paper validation, high paper/topic weights, and under-10-second exclusion are protected.",
);