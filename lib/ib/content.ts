import "server-only";
import manifest from "@/content/ib/catalog.json";
import algebra from "@/content/ib/math-aa-hl/number-algebra.json";
import functions from "@/content/ib/math-aa-hl/functions.json";
import geometry from "@/content/ib/math-aa-hl/geometry-trigonometry.json";
import statistics from "@/content/ib/math-aa-hl/statistics-probability.json";
import calculus1 from "@/content/ib/math-aa-hl/calculus-1.json";
import calculus2 from "@/content/ib/math-aa-hl/calculus-2.json";
import physicsA from "@/content/ib/physics-hl/space-time-motion.json";
import physicsB from "@/content/ib/physics-hl/particulate-matter.json";
import physicsC from "@/content/ib/physics-hl/wave-behaviour.json";
import physicsD from "@/content/ib/physics-hl/fields.json";
import physicsE from "@/content/ib/physics-hl/nuclear-quantum.json";
import chemistryS1 from "@/content/ib/chemistry/structure-1.json";
import chemistryS2 from "@/content/ib/chemistry/structure-2.json";
import chemistryS3 from "@/content/ib/chemistry/structure-3.json";
import chemistryR1 from "@/content/ib/chemistry/reactivity-1.json";
import chemistryR2 from "@/content/ib/chemistry/reactivity-2.json";
import chemistryR3 from "@/content/ib/chemistry/reactivity-3.json";
import { IB_COURSES, ibSyllabusSubtopics, type IbCourseLevel, type IbSubject, type IbSummary } from "./catalog";
import { IB_COLLECTIONS, ibQuestionSchema, questionAvailableForCourse, type IbQuestion } from "./question";

// Validation fails closed. Drafts never reach any student route or count.
const allQuestions: IbQuestion[] = [...algebra, ...functions, ...geometry, ...statistics, ...calculus1, ...calculus2,
  ...physicsA, ...physicsB, ...physicsC, ...physicsD, ...physicsE,
  ...chemistryS1, ...chemistryS2, ...chemistryS3, ...chemistryR1, ...chemistryR2, ...chemistryR3]
  .map(value => ibQuestionSchema.parse(value));
const published = allQuestions.filter(q => q.status === "published");
const byId = new Map(published.map(q => [q.id, q]));
if (new Set(allQuestions.map(q => q.id)).size !== allQuestions.length) throw new Error("Duplicate IB question IDs");

export function getIbQuestions(collectionId?: string, course: IbCourseLevel = "hl") {
  return published.filter(q => (!collectionId || q.collectionId === collectionId) && questionAvailableForCourse(q, course));
}
export function getIbQuestion(id: string, course: IbCourseLevel = "hl") {
  const question = byId.get(id);
  return question && questionAvailableForCourse(question, course) ? question : undefined;
}
export function getIbSummary(course: IbCourseLevel = "hl"): IbSummary {
  const summary = {} as IbSummary;
  for (const subject of Object.keys(IB_COURSES) as IbSubject[]) {
    const questions = published.filter(q => q.subject === subject && questionAvailableForCourse(q, course));
    summary[subject] = {
      questions: questions.length,
      mocks: (manifest.mockTests as {subject: string; status: string}[]).filter(t => t.subject === subject && t.status === "published").length,
      topics: Object.fromEntries(IB_COURSES[subject].topics.map(topic => [topic.id, questions.filter(q => q.topicId === topic.id).length])),
      collections: IB_COLLECTIONS.filter(collection => collection.subject === subject).map(collection => {
        const items = questions.filter(q => q.collectionId === collection.id);
        return { ...collection, count: items.length, subtopics: [...new Set(items.map(q => q.subtopic))].sort(),
          ...(subject !== "math-aa-hl" ? { syllabus: ibSyllabusSubtopics(subject, collection.topicId, course).map(subtopic => ({
            ...subtopic, count: items.filter(q => q.subject !== "math-aa-hl" && q.syllabusCode === subtopic.code).length,
          })) } : {}) };
      }),
    };
  }
  return summary;
}
