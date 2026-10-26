import type { adminClient } from "../../app/api/esat/qb/_server";
import { ESAT_CANONICAL_TESTS } from "./esat-canonical-tests.ts";
import { calculateEsatModulePredictions, ESAT_MODULE_MODEL_VERSION, type EvidenceRow } from "./esat-module-predictor.ts";
import { ESAT_GUARANTEE_POLICY, type EsatModule, type EsatModulePrediction } from "../esat-predictions.ts";

type Admin = ReturnType<typeof adminClient>;
export type EsatExamPlan = {
  user_id: string; exam_date: string; modules: EsatModule[]; lock_at: string; revision: string;
  predictions: EsatModulePrediction[] | null; prediction_saved_at: string | null;
  model_version: string | null; updated_at: string;
};
export type EsatPredictionLock = {
  exam_date: string; modules: EsatModule[]; lock_at: string; locked_at: string;
  predictions: EsatModulePrediction[]; prediction_saved_at: string | null; model_version: string | null; policy_version: string;
};

async function readAll(query: (from: number, to: number) => PromiseLike<{ data: EvidenceRow[] | null; error: unknown }>) {
  const rows: EvidenceRow[] = [];
  for (let from = 0; from <= 10000; from += 1000) {
    const result = await query(from, from + 999);
    if (result.error) throw result.error;
    const page = result.data ?? [];
    if (rows.length + page.length > 10000) throw new Error("ESAT prediction evidence exceeded the safety limit.");
    rows.push(...page);
    if (page.length < 1000) return rows;
  }
  throw new Error("ESAT prediction evidence is incomplete.");
}

export async function readEsatPredictionPlan(admin: Admin, userId: string) {
  // The database owns the clock and makes freezing idempotent. This also
  // covers a delayed scheduler without allowing post-cutoff predictions in.
  const freeze = await admin.rpc("esat_lock_due_predictions", { p_user_id: userId });
  if (freeze.error) throw freeze.error;
  const { data: plan, error } = await admin.from("esat_exam_plans").select("*").eq("user_id", userId).maybeSingle().retry(false);
  if (error) throw error;
  if (!plan) return { plan: null, lock: null };
  const frozen = await admin.from("esat_prediction_locks").select("*").eq("user_id", userId).eq("exam_date", plan.exam_date).maybeSingle().retry(false);
  if (frozen.error) throw frozen.error;
  return { plan: plan as EsatExamPlan, lock: frozen.data as EsatPredictionLock | null };
}

export async function getEsatModuleOverview(admin: Admin, userId: string) {
  let { plan, lock } = await readEsatPredictionPlan(admin, userId);
  if (plan && !lock && Date.now() < Date.parse(plan.lock_at)) {
    const asOf = new Date().toISOString();
    const [attempts, questions, qbRows] = await Promise.all([
      readAll((from, to) => admin.from("practice_test_attempts")
        .select("id,test_id,answers,attempt_number,submitted_at,predictor_metadata")
        .eq("user_id", userId).in("test_id", Object.keys(ESAT_CANONICAL_TESTS)).lte("submitted_at", asOf)
        .order("submitted_at").order("id").range(from, to).retry(false)),
      readAll((from, to) => admin.from("esat_qb_questions").select("qid,paper,topic,answer,is_active")
        .eq("is_active", true).order("qid").range(from, to).retry(false)),
      readAll((from, to) => admin.from("tmua_qb_attempt_events")
        .select("id,question_id,source,history_quality,predictor_eligible,metadata,selected_answer,attempted_at")
        .eq("user_id", userId).eq("product", "esat-question-bank").eq("source", "qb-progress-trigger-v2").eq("history_quality", "observed")
        .lte("attempted_at", asOf).order("attempted_at").order("id").range(from, to).retry(false)),
    ]);
    const predictions = calculateEsatModulePredictions({ modules: plan.modules, attempts, questions, qbRows, asOf });
    const saved = await admin.rpc("esat_save_module_predictions", {
      p_user_id: userId, p_revision: plan.revision, p_predictions: predictions,
      p_model_version: ESAT_MODULE_MODEL_VERSION, p_evidence_at: asOf,
    });
    if (saved.error) throw saved.error;
    ({ plan, lock } = await readEsatPredictionPlan(admin, userId));
  }
  const result = plan ? await admin.from("esat_result_submissions").select("actual_scores,assessment,submitted_at")
    .eq("user_id", userId).eq("exam_date", plan.exam_date).maybeSingle().retry(false) : null;
  if (result?.error) throw result.error;
  return {
    ok: true, plan, locked: Boolean(lock), predictions: lock?.predictions ?? plan?.predictions ?? [],
    predictionSavedAt: lock?.prediction_saved_at ?? plan?.prediction_saved_at ?? null,
    lockedAt: lock?.locked_at ?? null, policyVersion: lock?.policy_version ?? ESAT_GUARANTEE_POLICY,
    results: result?.data ?? null,
  };
}
