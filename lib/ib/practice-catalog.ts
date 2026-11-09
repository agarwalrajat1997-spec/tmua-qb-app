import business from "@/content/ib/practice-2027/business-catalog.json";
import topicTests from "@/content/ib/practice-2027/topic-tests.json";

export type PracticeMeta = { id: string; title: string; subject: string; course?: string; number?: number; minutes: number; marks: number; calculator: boolean };
export const businessPapers = (course: string): PracticeMeta[] => business.filter(p => p.course === "both" || p.course === course);
export const topicPapers = (subject: string): PracticeMeta[] => topicTests.filter(p => p.subject === subject);
export function practiceMeta(id: string): PracticeMeta | undefined {
  return [...business, ...topicTests].find(p => p.id === id);
}
export const practiceFiles = (id: string) => ({
  questions: `/ib-practice-2027/${id}-questions.pdf`,
  solutions: `/ib-practice-2027/${id}-solutions.pdf`,
});
export type PracticeQuestion = { title: string; stem: string; optional?: boolean; diagramSvg?: string; parts: {label: string; prompt: string; marks: number}[]; markScheme: {part: string; steps: {code: string; text: string}[]}[] };
export type PracticePaper = { meta: PracticeMeta; questions: PracticeQuestion[]; resources: {title: string; text: string}[] };
export type PracticePrompt = Omit<PracticePaper,"questions"> & { questions: Omit<PracticeQuestion,"markScheme">[] };
export type PracticeAttempt = { id: string; answers: Record<string,string>; choice: number | null; self_marks: Record<string,number> | null; submitted_at: string; elapsed_seconds: number };
export function activeParts(paper: PracticePrompt, choice: number | null) {
  return paper.questions.flatMap((q,i) => q.optional && choice !== i ? [] : q.parts.map(p => ({ key: `${i+1}:${p.label}`, max: p.marks })));
}
