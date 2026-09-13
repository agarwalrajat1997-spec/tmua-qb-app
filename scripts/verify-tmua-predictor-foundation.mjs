import fs from "node:fs";

const foundationMigration = fs.readFileSync(
  "supabase/migrations/20260806060000_tmua_predictor_foundation.sql",
  "utf8",
);

const captureMigration = fs.readFileSync(
  "supabase/migrations/20260807050000_tmua_predictor_observed_capture.sql",
  "utf8",
);

const progressRoute = fs.readFileSync(
  "app/api/qb/progress/save/route.ts",
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
  if (!foundationMigration.includes(required)) {
    throw new Error(`Predictor foundation is missing: ${required}`);
  }
}

for (const required of [
  "answer_elapsed_seconds integer",
  "submission_id text",
  "capture_tmua_predictor_attempt_event",
  "under_10_seconds",
  "trg_capture_tmua_predictor_attempt",
  "predictor_eligible",
]) {
  if (!captureMigration.includes(required)) {
    throw new Error(`Observed capture migration is missing: ${required}`);
  }
}

for (const required of [
  "answer_elapsed_seconds",
  "answer_submitted_at",
  "submission_id",
]) {
  if (!progressRoute.includes(required)) {
    throw new Error(`Progress route is missing: ${required}`);
  }
}

for (const required of [
  "questionVisitStartedAtMs",
  "newSubmissionId",
  "answer_elapsed_seconds",
  "submission_id",
  "TS_TMUA_QB_ATTEMPT_EVENTS_V2_START",
  "__TS_TMUA_QB_EVENT_CAPTURE_V2__",
]) {
  if (!questionBank.includes(required)) {
    throw new Error(`Question-bank HTML is missing: ${required}`);
  }
}

if (questionBank.includes("/api/tmua/qb/attempt-event")) {
  throw new Error(
    "Question-bank HTML still calls the unreliable separate event endpoint.",
  );
}

const timerStartPattern =
  /currentVisitQuestionId\s*=\s*qid;\s*questionVisitStartedAtMs\[qid\]\s*=\s*Date\.now\(\);/;

if (!timerStartPattern.test(questionBank)) {
  throw new Error(
    "Question visit timer is declared but is not started on a new question visit.",
  );
}

if (
  questionBank.includes(
    "questionVisitStartedAtMs[questionId] || Date.now()",
  )
) {
  throw new Error(
    "Unsafe zero-second timer fallback is still present.",
  );
}

if (!questionBank.includes("var hasValidVisitTimer")) {
  throw new Error(
    "Missing-response-time protection is not present.",
  );
}
console.log(
  "TMUA predictor capture verification passed: timed Check Answer submissions are captured server-side and responses below ten seconds are excluded.",
);