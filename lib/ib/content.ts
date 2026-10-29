import "server-only";
import manifest from "@/content/ib/catalog.json";
import { IB_COURSES, type IbSubject, type IbSummary } from "./catalog";

/** Import contract for the next content phase. Content stays on the server. */
export type IbQuestion = {
  id: string;
  subject: IbSubject;
  topicId: string;
  subtopic: string;
  difficulty: "easy" | "medium" | "hard";
  paper: string;
  marks: number;
  questionMarkdown: string;
  markScheme: { marks: number; explanationMarkdown: string }[];
  status: "draft" | "published";
};
export type IbMockTest = {
  id: string;
  subject: IbSubject;
  title: string;
  paper: string;
  durationMinutes: number;
  questionIds: string[];
  status: "draft" | "published";
};
type IbManifest = { version: number; questions: IbQuestion[]; mockTests: IbMockTest[] };

// Deliberately empty at launch. The content phase will add validation, delivery
// routes, and the practice player before any record is marked published.
const content: IbManifest = manifest;

export function getIbSummary(): IbSummary {
  const summary = {} as IbSummary;
  for (const subject of Object.keys(IB_COURSES) as IbSubject[]) {
    const questions = content.questions.filter(q => q.subject === subject && q.status === "published");
    summary[subject] = {
      questions: questions.length,
      mocks: content.mockTests.filter(t => t.subject === subject && t.status === "published").length,
      topics: Object.fromEntries(IB_COURSES[subject].topics.map(topic => [topic.id, questions.filter(q => q.topicId === topic.id).length])),
    };
  }
  return summary;
}
