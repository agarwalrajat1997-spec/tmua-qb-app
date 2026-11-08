import type { StoredSolution } from "./types";
import type { SourceQuestion } from "./question-reference";
export function storedSolution(q: SourceQuestion): StoredSolution {
  const proof = (q.audited_reference as { concise_proof?: unknown } | undefined)?.concise_proof;
  const solutionHtml = q.solution_html?.trim() ? q.solution_html :
    typeof proof === "string" ? proof.split(/\r?\n/).filter(Boolean).map(line =>
      "<p>" + line.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;") + "</p>"
    ).join("") : "";
  return {
    qid: q.qid,
    answer: q.answer,
    solutionHtml,
    updatedAt: q.updated_at,
    shortcuts:
      q.shortcut_available && q.nice_tip_html
        ? [{ title: "Stored shortcut / alternative", html: q.nice_tip_html }]
        : [],
  };
}
