import definitions from "@/content/ib/topic-groups.json";
import { ibSyllabusSubtopics, type IbSubject, type IbCourseLevel } from "./catalog";

type GroupDefinition = { id: string; title: string; subtopics?: string[]; syllabusCodes?: string[] };
type TopicQuestion = { subtopic: string; syllabusCode?: string };
export type IbTopicGroup = { id: string; title: string; subtopics: string[]; syllabusCodes: string[]; count: number };
const taxonomy: Record<string, GroupDefinition[]> = definitions;

export function questionInTopicGroup(question: TopicQuestion, group: Pick<IbTopicGroup, "subtopics" | "syllabusCodes">) {
  return group.subtopics.includes(question.subtopic) || (!!question.syllabusCode && group.syllabusCodes.includes(question.syllabusCode));
}

/** Presentation categories only: original syllabus codes and question records stay intact. */
export function ibTopicGroups(collection: { id: string; subject: IbSubject; topicId: string }, questions: TopicQuestion[], course: IbCourseLevel = "hl"): IbTopicGroup[] {
  const syllabus = ibSyllabusSubtopics(collection.subject, collection.topicId, course);
  const availableCodes = new Set(syllabus.map(topic => topic.code));
  const availableSubtopics = new Set(questions.map(question => question.subtopic));
  const groups = (taxonomy[`${collection.id}:${course}`] ?? taxonomy[collection.id] ?? []).flatMap(definition => {
    const syllabusCodes = (definition.syllabusCodes ?? []).filter(code => availableCodes.has(code));
    const subtopics = (definition.subtopics ?? []).filter(title => availableSubtopics.has(title));
    if (!syllabusCodes.length && !subtopics.length) return [];
    const group = { id: definition.id, title: definition.title, syllabusCodes, subtopics, count: 0 };
    group.count = questions.filter(question => questionInTopicGroup(question, group)).length;
    return [group];
  });
  // Newly added content remains discoverable until its curated category is assigned.
  const coveredCodes = new Set(groups.flatMap(group => group.syllabusCodes));
  const coveredSubtopics = new Set(groups.flatMap(group => group.subtopics));
  if (syllabus.length) {
    for (const topic of syllabus.filter(topic => !coveredCodes.has(topic.code))) {
      groups.push({ id: "syllabus:" + topic.code, title: topic.title, syllabusCodes: [topic.code], subtopics: [], count: questions.filter(q => q.syllabusCode === topic.code).length });
    }
  } else {
    for (const subtopic of [...availableSubtopics].filter(title => !coveredSubtopics.has(title)).sort()) {
      groups.push({ id: "subtopic:" + subtopic, title: subtopic, subtopics: [subtopic], syllabusCodes: [], count: questions.filter(q => q.subtopic === subtopic).length });
    }
  }
  return groups;
}
