import "server-only";
import manifest from "@/content/ib/catalog.json";
import algebra from "@/content/ib/math-aa-hl/number-algebra.json";
import functions from "@/content/ib/math-aa-hl/functions.json";
import geometry from "@/content/ib/math-aa-hl/geometry-trigonometry.json";
import statistics from "@/content/ib/math-aa-hl/statistics-probability.json";
import calculus1 from "@/content/ib/math-aa-hl/calculus-1.json";
import calculus2 from "@/content/ib/math-aa-hl/calculus-2.json";
import { IB_COURSES, type IbSubject, type IbSummary } from "./catalog";
import { IB_COLLECTIONS, ibQuestionSchema, type IbQuestion } from "./question";

// Validation fails closed. Drafts never reach any student route or count.
const allQuestions: IbQuestion[] = [...algebra, ...functions, ...geometry, ...statistics, ...calculus1, ...calculus2]
  .map(value => ibQuestionSchema.parse(value));
const published = allQuestions.filter(q => q.status === "published");
const byId = new Map(published.map(q => [q.id, q]));
if (new Set(allQuestions.map(q => q.id)).size !== allQuestions.length) throw new Error("Duplicate IB question IDs");

export function getIbQuestions(collectionId?: string) {
  return collectionId ? published.filter(q => q.collectionId === collectionId) : published;
}
export function getIbQuestion(id: string) {
  return byId.get(id);
}
export function getIbSummary(): IbSummary {
  const summary = {} as IbSummary;
  for (const subject of Object.keys(IB_COURSES) as IbSubject[]) {
    const questions = published.filter(q => q.subject === subject);
    summary[subject] = {
      questions: questions.length,
      mocks: (manifest.mockTests as {subject: string; status: string}[]).filter(t => t.subject === subject && t.status === "published").length,
      topics: Object.fromEntries(IB_COURSES[subject].topics.map(topic => [topic.id, questions.filter(q => q.topicId === topic.id).length])),
      collections: subject === "math-aa-hl" ? IB_COLLECTIONS.map(collection => {
        const items = questions.filter(q => q.collectionId === collection.id);
        return { ...collection, count: items.length, subtopics: [...new Set(items.map(q => q.subtopic))].sort() };
      }) : [],
    };
  }
  return summary;
}
