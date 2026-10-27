import type { adminClient } from "../../app/api/esat/qb/_server";
import { ESAT_CANONICAL_TESTS } from "./esat-canonical-tests.ts";
import { calculateEsatModulePredictions, inferEsatPathway, ESAT_MODULE_MODEL_VERSION, type EvidenceRow } from "./esat-module-predictor.ts";
import { ESAT_MODULES } from "../esat-predictions.ts";

type Admin = ReturnType<typeof adminClient>;

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

// Live, read-only predictions: no exam setup, saved plan, lock or refund workflow.
export async function getEsatModuleOverview(admin: Admin, userId: string) {
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
  const allPredictions = calculateEsatModulePredictions({ modules: [...ESAT_MODULES], attempts, questions, qbRows, asOf });
  const pathway = inferEsatPathway(allPredictions);
  return {
    ok: true, modelVersion: ESAT_MODULE_MODEL_VERSION, calculatedAt: asOf, pathway,
    predictions: allPredictions.filter(prediction => pathway.modules.includes(prediction.module))
      .map(({ guaranteeEligible: _guaranteeEligible, inputHash: _inputHash, ...prediction }) => prediction),
  };
}
