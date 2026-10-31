import type { StoredSolution } from "./types";
import type { SourceQuestion } from "./question-reference";
export function storedSolution(q: SourceQuestion): StoredSolution {
  return {
    qid: q.qid,
    answer: q.answer,
    solutionHtml: q.solution_html,
    updatedAt: q.updated_at,
    shortcuts:
      q.shortcut_available && q.nice_tip_html
        ? [{ title: "Stored shortcut / alternative", html: q.nice_tip_html }]
        : [],
  };
}
