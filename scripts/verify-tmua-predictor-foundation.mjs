import fs from "node:fs";

const migration = fs.readFileSync(
  "supabase/migrations/20260806060000_tmua_predictor_foundation.sql",
  "utf8",
);
const route = fs.readFileSync(
  "app/api/tmua/qb/attempt-event/route.ts",
  "utf8",
);
const questionBank = fs.readFileSync(
  "public/tmua-question-bank/index.html",
  "utf8",
);

for (const required of [
  "create table if not exists public.tmua_qb_attempt_events",
  "history_quality text not null default 'observed'",
  "add column if not exists attempt_number integer",
  "add column if not exists prior_question_exposure_percentage",
]) {
  if (!migration.includes(required)) {
    throw new Error(`Predictor migration is missing: ${required}`);
  }
}

for (const required of [
  'from("tmua_qb_attempt_events")',
  'onConflict: "client_event_id"',
  "Authentication required.",
]) {
  if (!route.includes(required)) {
    throw new Error(`Attempt-event route is missing: ${required}`);
  }
}

const markerCount =
  questionBank.split("TS_TMUA_QB_ATTEMPT_EVENTS_V1_START").length - 1;

if (markerCount !== 1) {
  throw new Error(
    `Expected one question-bank event marker; found ${markerCount}.`,
  );
}

for (const required of [
  "/api/tmua/qb/attempt-event",
  "/api/qb/progress/save",
  "__TS_TMUA_QB_EVENT_CAPTURE_V1__",
]) {
  if (!questionBank.includes(required)) {
    throw new Error(`Question-bank HTML is missing: ${required}`);
  }
}

console.log(
  "TMUA predictor foundation verification passed: migration, append-only event route and question-bank capture are protected.",
);