import type { Question } from "../types";
import { studioRead, studioViewerId } from "./api";

export type Skill = {
  skill_id: string;
  role: string;
  evidence_in_solution: string;
  learning_objective: string;
  prerequisite_skill_ids: string[];
};
export type Diagnostic = {
  error_id: string;
  skill_ids: string[];
  description: string;
  observable_evidence: string;
  alternative_explanations: string[];
  diagnostic_probe: string;
  expected_probe_answer: string;
  confirmation_rule: string;
  remediation: string;
};
export type Route = {
  route_id: string;
  target_qid: string;
  target_snapshot_id: string;
  target_source_sha256: string;
  target_content_version: string;
  error_ids: string[];
  source_skill_ids: string[];
  relationship: string;
  why_content_matches: string;
  selection_condition: string;
  difficulty_comparison: string;
  diagnostic_gate: {
    evidence_needed: string;
    confirmation_rule: string;
    insufficient_evidence_action: string;
  };
};
export type Guide = {
  route_candidates?: unknown[];
  qid: string;
  version_id: string;
  source_sha256: string;
  skill_labels: Record<string, string | { name: string }>;
  routes: Route[];
  enrichment: {
    ordinary_method: string;
    concise_proof: string;
    exact_answer: string;
    domain_case_checks: string[];
    teaching_note: string;
    skills: Skill[];
    hints: {
      hint_id: string;
      stage: string;
      text: string;
      skill_ids: string[];
    }[];
    solution_steps: {
      step_id: string;
      explanation: string;
      skill_ids: string[];
      check: string;
    }[];
    useful_alternatives: {
      method: string;
      concise_justification: string;
      when_useful: string;
    }[];
    shortcut_assessments: {
      shortcut_id: string;
      classification: string;
      method_here: string;
      conditions_checked: string[];
      best_ordinary_baseline: string;
      work_avoided: string;
      saving_judgment: string;
    }[];
    error_hypotheses: Diagnostic[];
    option_analysis: {
      option_label: string;
      is_correct: boolean;
      why: string;
      possible_error_ids: string[];
      diagnosis_limit: string;
    }[];
    routing_gaps: { skill_id: string; reason: string; fallback: string }[];
    accessibility: {
      diagram_required: boolean;
      diagram_description: string;
      notation_notes: string[];
    };
  };
};
export type GuideEvent = {
  id: string;
  at: string;
  qid: string;
  contentVersion: string;
  type: string;
  detail: Record<string, unknown>;
};

// Preview events remain on this device, version-bound; they do not invent mastery scores.
export function recordGuideEvent(
  q: Question,
  type: string,
  detail: Record<string, unknown> = {},
) {
  const owner = studioViewerId();
  if (!owner) return false;
  const key = `ts-guide-events:user:${owner}:${q.qid}:${q.content_version}`;
  const event: GuideEvent = {
    id: crypto.randomUUID(),
    at: new Date().toISOString(),
    qid: q.qid,
    contentVersion: q.content_version ?? "",
    type,
    detail,
  };
  try {
    const prior: GuideEvent[] = JSON.parse(localStorage.getItem(key) || "[]");
    localStorage.setItem(key, JSON.stringify([...prior, event].slice(-500)));
    return true;
  } catch {
    return false;
  }
}
export function skillName(guide: Guide, id: string) {
  const value = guide.skill_labels[id];
  return typeof value === "string"
    ? value
    : (value?.name ?? id.replaceAll(".", " · ").replaceAll("_", " "));
}
const guideCache = new Map<string, Guide>();
export function cacheGuide(question: Question, guide: Guide) {
  if (guide.qid !== question.qid || guide.version_id !== question.content_version ||
      guide.source_sha256 !== question.source_sha256)
    throw Error("This reference belongs to a different question version. Refresh the app.");
  guideCache.set(`${question.qid}@${question.content_version}`, guide);
}
export async function loadGuide(question: Question): Promise<Guide> {
  const cached = guideCache.get(`${question.qid}@${question.content_version}`);
  if (cached) return cached;
  const { guide } = await studioRead<{ guide: Guide }>("guide", {
    qid: question.qid, contentVersion: question.content_version,
  });
  if (
    guide.qid !== question.qid ||
    guide.version_id !== question.content_version ||
    guide.source_sha256 !== question.source_sha256
  )
    throw Error(
      "This reference belongs to a different question version. Refresh the app.",
    );
  cacheGuide(question, guide);
  return guide;
}
