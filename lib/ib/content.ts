import "server-only";
import { applySyllabusAmendments } from "./syllabus-amendments";
import { IB_BANK_LOADERS } from "./bank-loaders";
import { collectionForQuestion } from "./content-index";
import { ibQuestionSchema, questionAvailableForCourse, type IbQuestion } from "./question";
import type { IbCourseLevel } from "./catalog";
export { getIbSummary } from "./content-index";

type Bank = { hl: IbQuestion[]; sl: IbQuestion[]; byId: Map<string, IbQuestion> };
// Immutable, deployment-bundled content only. No sessions or student data are cached.
const banks = new Map<string, Promise<Bank>>();
const empty: IbQuestion[] = [];
function loadBank(id: string): Promise<Bank> | undefined {
  if (!Object.hasOwn(IB_BANK_LOADERS, id)) return undefined;
  let promise = banks.get(id);
  if (!promise) {
    promise = IB_BANK_LOADERS[id as keyof typeof IB_BANK_LOADERS]().then(module => {
      const all = module.default.map(value => applySyllabusAmendments(ibQuestionSchema.parse(value)));
      if (all.some(q => q.collectionId !== id) || new Set(all.map(q => q.id)).size !== all.length) throw new Error("Invalid IB bank identity");
      const hl = all.filter(q => q.status === "published");
      return { hl, sl: hl.filter(q => questionAvailableForCourse(q, "sl")), byId: new Map(hl.map(q => [q.id, q])) };
    }).catch(error => { banks.delete(id); throw error; });
    banks.set(id, promise);
  }
  return promise;
}
export async function getIbQuestions(collectionId?: string, course: IbCourseLevel = "hl"): Promise<IbQuestion[]> {
  if (!collectionId) return (await Promise.all(Object.keys(IB_BANK_LOADERS).map(id => getIbQuestions(id, course)))).flat();
  return (await loadBank(collectionId))?.[course] ?? empty;
}
export async function getIbQuestion(id: string, course: IbCourseLevel = "hl") {
  const collectionId = collectionForQuestion(id);
  if (!collectionId) return undefined;
  const question = (await loadBank(collectionId))?.byId.get(id);
  return question && questionAvailableForCourse(question, course) ? question : undefined;
}
