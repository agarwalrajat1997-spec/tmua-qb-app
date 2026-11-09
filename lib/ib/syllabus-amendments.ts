import type { IbQuestion } from "./question";

// Reverse regression, formal independence and integration by inspection.
const revisedCodes: Record<string,string> = {"ib-aa-sp-008":"4.10","ib-aa-sp-021":"4.11","ib-aa-c2-017":"5.10"};
/** Correct publication metadata without rewriting the separately frozen author/reviewer evidence. */
export function applySyllabusAmendments(q: IbQuestion): IbQuestion {
  if (q.subject === "math-aa-hl" && revisedCodes[q.id]) return {...q, syllabusCode:revisedCodes[q.id]};
  if (q.id === "ib-aihl-na-702" && q.subject === "math-ai-hl" && q.syllabusCode === "1.11") {
    // The limiting sum of the annually planted cohorts uses AHL 1.11.
    return { ...q, level: "ahl" };
  }
  return q;
}
