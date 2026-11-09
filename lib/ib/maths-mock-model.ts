import catalog from "@/content/ib/aa-mocks-2026/catalog.json";
import aiCatalog from "@/content/ib/ai-mocks-2026/catalog.json";

import extraAi from "@/content/ib/practice-2027/ai-catalog.json";
import aiSlCatalog from "@/content/ib/ai-sl-mocks-2026/catalog.json";

export type MathsMockStrand = "aa" | "ai";
export type MathsMockMeta = {
  id: string; strand?: MathsMockStrand; course: "sl" | "hl"; set: "A" | "B" | "C" | "D"; paper: "1" | "2" | "3";
  title: string; minutes: number; marks: number; calculator: boolean;
  pdfUrl: string; questionPdfUrl?: string; status: "published" | "draft"; questionCount?: number; year: number; sections: ("A" | "B")[];
};
export type MathsMockPart = { label: string; prompt: string; marks: number };
export type MathsMockQuestion = {
  number: number; section: "A" | "B" | ""; marks: number; stem: string;
  parts: MathsMockPart[]; diagramSvg?: string; answerSummary?: string;
  markScheme: { part: string; steps: { code: string; text: string }[] }[];
  syllabusRefs?: string[]; cognitiveDemand?: string;
};
export type MathsMockPaper = Pick<MathsMockMeta, "id" | "strand" | "course" | "set" | "paper" | "title" | "minutes" | "marks" | "calculator"> & { questions: MathsMockQuestion[] };
export type MathsMockPromptQuestion = Omit<MathsMockQuestion, "diagramSvg" | "markScheme" | "answerSummary"> & { diagramUrl?: string };
export type MathsMockPrompt = MathsMockMeta & { questions: MathsMockPromptQuestion[] };
export type MathsMockAnswers = Record<string, string>;
export type MathsMockMarks = Record<string, number>;
export type MathsMockStage = "instructions" | "running" | "pending" | "review";
export type MathsMockDraft = { version: 1; attemptId: string; name: string; startedAt: number; deadline: number; elapsed: number; stage: MathsMockStage; index: number; answers: MathsMockAnswers; flags: Record<number, boolean>; marks: MathsMockMarks };
export const MATHS_MOCKS = catalog as MathsMockMeta[];
export const AI_MATHS_MOCKS = [...aiCatalog, ...extraAi].sort((a,b)=>a.id.localeCompare(b.id)) as MathsMockMeta[];
export const AI_SL_MATHS_MOCKS = aiSlCatalog as MathsMockMeta[];
export const ALL_MATHS_MOCKS = [...MATHS_MOCKS, ...AI_MATHS_MOCKS, ...AI_SL_MATHS_MOCKS];
export const mathsStrand = (paper: Pick<MathsMockMeta, "strand">): MathsMockStrand => paper.strand ?? "aa";
export const mathsStrandName = (paper: Pick<MathsMockMeta, "strand">) => mathsStrand(paper) === "ai" ? "Applications and interpretation" : "Analysis and approaches";
export const mathsAnswerKey = (number: number, part: string) => `${number}:${part || "whole"}`;
export const mathsSubject = (course: "sl" | "hl", strand: MathsMockStrand = "aa") => `math-${strand}-${course}` as const;
export function mathsSecondsRemaining(deadline: number, now: number, maximum: number) { return Math.min(maximum, Math.max(0, Math.ceil((deadline - now) / 1000))); }
export function restoreMathsMockDraft(raw: string, paper: MathsMockPrompt): MathsMockDraft | null {
  try {
    const d = JSON.parse(raw), object = (v: unknown) => !!v && typeof v === "object" && !Array.isArray(v);
    if (d.version !== 1 || !["instructions", "running", "pending", "review"].includes(d.stage) || !Number.isInteger(d.index) || d.index < 0 || d.index >= paper.questions.length || typeof d.name !== "string" || d.name.length > 100 || !object(d.answers) || !object(d.flags) || !object(d.marks)) return null;
    const maxima = new Map(paper.questions.flatMap(q => q.parts.map(p => [mathsAnswerKey(q.number, p.label), p.marks] as const)));
    if (Object.entries(d.answers).some(([key, value]) => !maxima.has(key) || typeof value !== "string" || value.length > 12000)) return null;
    if (Object.entries(d.marks).some(([key, value]) => !maxima.has(key) || typeof value !== "number" || !Number.isInteger(value) || value < 0 || value > maxima.get(key)!)) return null;
    if (Object.entries(d.flags).some(([key, value]) => !paper.questions.some(q => String(q.number) === key) || typeof value !== "boolean")) return null;
    if (d.stage !== "instructions" && (!/^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(d.attemptId) || !Number.isFinite(d.startedAt) || !Number.isFinite(d.deadline) || d.deadline - d.startedAt !== paper.minutes * 60000 || !Number.isInteger(d.elapsed) || d.elapsed < 0 || d.elapsed > paper.minutes * 60)) return null;
    return d as MathsMockDraft;
  } catch { return null; }
}
export function getMathsMock(id: string) { return ALL_MATHS_MOCKS.find(m => m.id === id && m.status === "published"); }
export function mathsPdfUrl(meta: MathsMockMeta, origin?: string) {
  // This is one public solution asset, shared by the submitted UI and email.
  const expected = `/ib-mock-solutions/${meta.id}.pdf`;
  if (meta.pdfUrl !== expected) throw new Error("The solution PDF does not match this paper.");
  return origin ? new URL(expected, origin).href : expected;
}
export function cleanMathsAnswers(questions: Pick<MathsMockPaper, "questions">["questions"], input: unknown): MathsMockAnswers {
  if (!input || typeof input !== "object" || Array.isArray(input)) throw new Error("Invalid answers.");
  const source = input as Record<string, unknown>, output: MathsMockAnswers = {};
  for (const q of questions) for (const part of q.parts) {
    const key = mathsAnswerKey(q.number, part.label), value = source[key] ?? "";
    if (typeof value !== "string" || value.length > 12000) throw new Error("Each response must be text of no more than 12,000 characters.");
    output[key] = value;
  }
  return output;
}
export function validateMathsMarks(questions: MathsMockQuestion[], input: unknown): MathsMockMarks {
  if (!input || typeof input !== "object" || Array.isArray(input)) throw new Error("Enter a mark for every part.");
  const source = input as Record<string, unknown>, output: MathsMockMarks = {};
  for (const q of questions) for (const part of q.parts) {
    const key = mathsAnswerKey(q.number, part.label), value = source[key];
    if (typeof value !== "number" || !Number.isInteger(value) || value < 0 || value > part.marks) throw new Error(`Enter a whole-number mark from 0 to ${part.marks} for each part.`);
    output[key] = value;
  }
  return output;
}
export function scoreMathsMock(questions: MathsMockQuestion[], marks: MathsMockMarks | null) {
  const rows = questions.map(q => ({ number: q.number, section: q.section, max: q.marks,
    score: marks ? q.parts.reduce((total, p) => total + marks[mathsAnswerKey(q.number, p.label)], 0) : null }));
  return { total: marks ? rows.reduce((total, q) => total + (q.score ?? 0), 0) : null,
    maximum: rows.reduce((total, q) => total + q.max, 0), rows };
}
export type MathsMockReview = {
  id: string; submittedAt: string; name: string; elapsed: number; answers: MathsMockAnswers;
  selfMarks: MathsMockMarks | null; score: ReturnType<typeof scoreMathsMock>;
  solutions: MathsMockQuestion[];
};
export function mathsReportPayload(meta: MathsMockMeta, review: MathsMockReview, email: string, origin: string) {
  const scored = review.score.total !== null;
  const details = [
    `${meta.title}. ${meta.minutes} minutes; ${meta.marks} marks.`,
    `Time used: ${Math.floor(review.elapsed / 60)} min ${review.elapsed % 60} s.`,
    scored ? "Written marks are self-assessed using the supplied worked mark scheme."
      : "Your responses have been saved. Marking is pending: open the paper and solution book, then self-assess each part in the portal.",
    "This report is independent practice, not an official IB grade prediction. Internal assessment is not included.",
    ...review.score.rows.map(q => `Question ${q.number}${q.section ? ` (Section ${q.section})` : ""}: ${q.score ?? "pending"} / ${q.max}`),
    "", `Paper and solution book: ${mathsPdfUrl(meta, origin)}`,
  ].join("\n");
  return {
    name: review.name.trim() || "Student", to_email: email, student_email: email,
    test_title: meta.title, session: `IB Mathematics ${mathsStrand(meta).toUpperCase()} ${meta.course.toUpperCase()} · Set ${meta.set} · Paper ${meta.paper}`,
    attempt_id: review.id, timestamp: review.submittedAt,
    score: scored ? `${review.score.total} / ${review.score.maximum} (self-assessed)` : "Submitted — self-assessment pending",
    incorrect: scored ? review.score.rows.filter(q => q.score !== q.max).map(q => `Q${q.number}`).join(", ") || "None" : "Not yet marked",
    // The established template displays paper1 and paper2. Keep Paper3 visible too.
    paper1: meta.paper === "2" ? "This attempt contains Paper 2 only." : details,
    paper2: meta.paper === "2" ? details : "Other papers are separate timed attempts.",
    paper3: meta.paper === "3" ? details : "", solution_link: mathsPdfUrl(meta, origin),
    solution_note: "The PDF begins with the question paper, followed by the worked solution book.",
  };
}
