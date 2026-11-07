import biologyMocks from "@/content/ib/biology-mocks-2025/catalog.json";
import chemistryMocks from "@/content/ib/chemistry-mocks-2025/catalog.json";
import manifest from "@/content/ib/catalog.json";
import physicsMocks from "@/content/ib/physics-mocks-2026/catalog.json";
import mathsMocks from "@/content/ib/aa-mocks-2026/catalog.json";
import aiMathsMocks from "@/content/ib/ai-mocks-2026/catalog.json";
import { IB_COURSES, ibIsMathSubject, ibSyllabusSubtopics, ibTopicVisible, ibTopicsForCourse, type IbCourseLevel, type IbSubject, type IbSummary } from "./catalog";
import { IB_COLLECTIONS, questionAvailableForCourse, type IbQuestion } from "./question";
import { ibTopicGroups } from "./topic-groups";

/** Build-time navigation metadata. Never include prompts, diagrams or answers. */
export function buildIbContentIndex(all: IbQuestion[]) {
  if (new Set(all.map(q => q.id)).size !== all.length) throw new Error("Duplicate IB question IDs");
  const published = all.filter(q => q.status === "published");
  function summary(course: IbCourseLevel): IbSummary {
    const result = {} as IbSummary;
    for (const subject of Object.keys(IB_COURSES) as IbSubject[]) {
      const questions = published.filter(q => q.subject === subject && questionAvailableForCourse(q, course));
      result[subject] = {
        questions: questions.length,
        mocks: subject === "biology" ? biologyMocks.filter(t => t.course === course && t.status === "published").reduce((sum,t) => sum+t.papers.filter(p => p.status === "published").length,0) : subject === "chemistry" ? chemistryMocks.filter(t => t.course === course && t.status === "published").reduce((sum,t) => sum+t.papers.filter(p => p.status === "published").length,0) : subject === "physics-hl" ? physicsMocks.filter(t => t.course === course && t.status === "published").reduce((sum, t) => sum + t.papers.filter(p => p.status === "published").length, 0) : subject === "math-aa-hl" || subject === "math-aa-sl" ? mathsMocks.filter(t => t.course === (subject === "math-aa-sl" ? "sl" : "hl") && t.status === "published").length : subject === "math-ai-hl" ? aiMathsMocks.filter(t => t.status === "published").length : (manifest.mockTests as { subject: string; status: string }[]).filter(t => t.subject === subject && t.status === "published").length,
        topics: Object.fromEntries(ibTopicsForCourse(subject, course).map(topic => [topic.id, questions.filter(q => q.topicId === topic.id).length])),
        collections: IB_COLLECTIONS.filter(c => c.subject === subject && ibTopicVisible(subject, c.topicId, course)).map(collection => {
          const items = questions.filter(q => q.collectionId === collection.id);
          return { ...collection, groups: ibTopicGroups(collection, items, course), count: items.length, subtopics: [...new Set(items.map(q => q.subtopic))].sort(),
            ...(!ibIsMathSubject(subject) ? { syllabus: ibSyllabusSubtopics(subject, collection.topicId, course).map(topic => ({ ...topic, count: items.filter(q => q.syllabusCode === topic.code).length })) } : {}) };
        }),
      };
    }
    return result;
  }
  return { questionCollections: Object.fromEntries(published.map(q => [q.id, q.collectionId])), summaries: { sl: summary("sl"), hl: summary("hl") } };
}
