import type { IbQuestion } from "./question";

/** Correct publication metadata without rewriting the separately frozen author/reviewer evidence. */
export function applySyllabusAmendments(q: IbQuestion): IbQuestion {
  if (q.id === "ib-aihl-na-702" && q.subject === "math-ai-hl" && q.syllabusCode === "1.11") {
    // The limiting sum of the annually planted cohorts uses AHL 1.11.
    return { ...q, level: "ahl" };
  }
  return q;
}
