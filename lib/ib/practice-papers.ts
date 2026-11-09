import "server-only";
import topics from "@/content/ib/practice-2027/topic-tests.json";
import { getIbQuestion } from "./content";
import { practiceMeta, type PracticePaper, type PracticePrompt } from "./practice-catalog";

const businessLoaders = {
  "business-a-paper-1": () => import("@/content/ib/practice-2027/business/business-a-paper-1.json"),
  "business-sl-a-paper-2": () => import("@/content/ib/practice-2027/business/business-sl-a-paper-2.json"),
  "business-hl-a-paper-2": () => import("@/content/ib/practice-2027/business/business-hl-a-paper-2.json"),
  "business-hl-a-paper-3": () => import("@/content/ib/practice-2027/business/business-hl-a-paper-3.json"),
};
export async function loadPracticePaper(id: string): Promise<PracticePaper | undefined> {
  const meta = practiceMeta(id);
  if (!meta) return;
  const load = businessLoaders[id as keyof typeof businessLoaders];
  if (load) {
    const { default: paper } = await load();
    return {meta, questions: paper.questions, resources: paper.resources};
  }
  const test = topics.find(t => t.id === id);
  if (!test) return;
  const questions = await Promise.all(test.ids.map(async qid => {
    const q = await getIbQuestion(qid);
    if (!q || q.subject !== meta.subject) throw new Error("The topic test has an invalid question.");
    return {title:q.title, stem:q.stem, diagramSvg:q.diagramSvg, parts:q.parts, markScheme:q.markScheme};
  }));
  return {meta,questions,resources:[]};
}
export function practicePrompt(paper: PracticePaper): PracticePrompt {
  return {...paper, questions: paper.questions.map(({markScheme: _scheme,...q})=>q)};
}
