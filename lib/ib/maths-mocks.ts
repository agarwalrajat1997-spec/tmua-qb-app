import "server-only";
import { z } from "zod";
import { safeDiagram } from "./question";
import { getMathsMock, mathsStrand, type MathsMockMeta, type MathsMockPaper, type MathsMockPrompt } from "./maths-mock-model";

const text = z.string().min(1).max(50000);
const part = z.object({ label: z.string().max(24), prompt: z.string().max(30000), marks: z.number().int().positive().max(110) });
const question = z.object({ number: z.number().int().positive(), section: z.enum(["A", "B", ""]), marks: z.number().int().positive().max(110),
  stem: z.string().max(50000), parts: z.array(part).min(1).max(40), diagramSvg: z.string().max(300000).optional(),
  answerSummary: z.string().max(50000).optional(),
  syllabusRefs: z.array(z.string().min(1).max(100)).max(30).optional(), cognitiveDemand: z.string().max(1000).optional(),
  markScheme: z.array(z.object({ part: z.string().max(24), steps: z.array(z.object({ code: z.string().regex(/^[MAR][1-9]\d?$/), text })).min(1) })).min(1) });
const schema = z.object({ id: text, strand: z.enum(["aa", "ai"]).optional(), course: z.enum(["sl", "hl"]), set: z.enum(["A", "B", "C", "D"]), paper: z.enum(["1", "2", "3"]),
  title: text, minutes: z.number().int().positive().max(180), marks: z.number().int().positive().max(200), calculator: z.boolean(), questions: z.array(question).min(1).max(40) });

export function validateMathsMockPaper(input: unknown, meta: MathsMockMeta): MathsMockPaper {
  const p = schema.parse(input);
  for (const key of ["id", "course", "set", "paper", "minutes", "marks", "calculator"] as const) if (p[key] !== meta[key]) throw new Error(`Mock metadata differs: ${key}.`);
  if (mathsStrand(p) !== mathsStrand(meta)) throw new Error("The mathematics strand does not match the catalogue.");
  if (p.course === "sl" && p.paper === "3") throw new Error("SL has no Paper 3.");
  if (p.calculator !== (mathsStrand(meta) === "ai" || p.paper !== "1")) throw new Error("The calculator rule does not match the paper.");
  if (mathsStrand(meta) === "ai" && (p.strand !== "ai" || p.questions.some(q => q.section !== ""))) throw new Error("AI papers have no Sections A and B.");
  if (mathsStrand(meta) === "ai" && p.course === "sl" && (p.minutes !== 90 || p.marks !== 80)) throw new Error("AI SL papers require 90 minutes and 80 marks for this course.");
  if (meta.questionCount !== undefined && p.questions.length !== meta.questionCount) throw new Error("The question count does not match the catalogue.");
  if (new Set(p.questions.map(q => q.number)).size !== p.questions.length || p.questions.some((q, i) => q.number !== i + 1)) throw new Error("Questions must be numbered consecutively.");
  if (p.questions.reduce((total, q) => total + q.marks, 0) !== p.marks) throw new Error("Question marks do not match the paper total.");
  for (const q of p.questions) {
    if (q.parts.reduce((total, part) => total + part.marks, 0) !== q.marks || new Set(q.parts.map(part => part.label)).size !== q.parts.length) throw new Error(`Invalid parts in question ${q.number}.`);
    if (q.markScheme.length !== q.parts.length || new Set(q.markScheme.map(g => g.part)).size !== q.markScheme.length) throw new Error(`Invalid mark scheme in question ${q.number}.`);
    for (const part of q.parts) {
      const group = q.markScheme.find(group => group.part === part.label);
      if (!group) throw new Error(`Missing scheme for question ${q.number}.`);
      if (group.steps.reduce((total, step) => total + Number(step.code.slice(1)), 0) !== part.marks) throw new Error(`Marking points do not match Question ${q.number} (${part.label}).`);
    }
    if (q.diagramSvg && !safeDiagram(q.diagramSvg)) throw new Error(`Unsafe diagram in question ${q.number}.`);
  }
  return p;
}
const loaders = {
  "ai-sl-set-a-paper-1": () => import("@/content/ib/ai-sl-mocks-2026/papers/ai-sl-set-a-paper-1.json"),
  "ai-sl-set-a-paper-2": () => import("@/content/ib/ai-sl-mocks-2026/papers/ai-sl-set-a-paper-2.json"),
  "ai-sl-set-b-paper-1": () => import("@/content/ib/ai-sl-mocks-2026/papers/ai-sl-set-b-paper-1.json"),
  "ai-sl-set-b-paper-2": () => import("@/content/ib/ai-sl-mocks-2026/papers/ai-sl-set-b-paper-2.json"),
  "aa-hl-set-a-paper-1": () => import("@/content/ib/aa-mocks-2026/papers/aa-hl-set-a-paper-1.json"),
  "aa-hl-set-a-paper-2": () => import("@/content/ib/aa-mocks-2026/papers/aa-hl-set-a-paper-2.json"),
  "aa-hl-set-a-paper-3": () => import("@/content/ib/aa-mocks-2026/papers/aa-hl-set-a-paper-3.json"),
  "aa-sl-set-a-paper-1": () => import("@/content/ib/aa-mocks-2026/papers/aa-sl-set-a-paper-1.json"),
  "aa-sl-set-a-paper-2": () => import("@/content/ib/aa-mocks-2026/papers/aa-sl-set-a-paper-2.json"),
  "aa-hl-set-b-paper-1": () => import("@/content/ib/aa-mocks-2026/papers/aa-hl-set-b-paper-1.json"),
  "aa-hl-set-b-paper-2": () => import("@/content/ib/aa-mocks-2026/papers/aa-hl-set-b-paper-2.json"),
  "aa-hl-set-b-paper-3": () => import("@/content/ib/aa-mocks-2026/papers/aa-hl-set-b-paper-3.json"),
  "aa-sl-set-b-paper-1": () => import("@/content/ib/aa-mocks-2026/papers/aa-sl-set-b-paper-1.json"),
  "aa-sl-set-b-paper-2": () => import("@/content/ib/aa-mocks-2026/papers/aa-sl-set-b-paper-2.json"),
  "ai-hl-set-a-paper-1": () => import("@/content/ib/ai-mocks-2026/papers/ai-hl-set-a-paper-1.json"),
  "ai-hl-set-a-paper-2": () => import("@/content/ib/ai-mocks-2026/papers/ai-hl-set-a-paper-2.json"),
  "ai-hl-set-a-paper-3": () => import("@/content/ib/ai-mocks-2026/papers/ai-hl-set-a-paper-3.json"),
  "ai-hl-set-b-paper-1": () => import("@/content/ib/ai-mocks-2026/papers/ai-hl-set-b-paper-1.json"),
  "ai-hl-set-b-paper-2": () => import("@/content/ib/ai-mocks-2026/papers/ai-hl-set-b-paper-2.json"),
  "ai-hl-set-b-paper-3": () => import("@/content/ib/ai-mocks-2026/papers/ai-hl-set-b-paper-3.json"),
  "ai-hl-set-c-paper-1": () => import("@/content/ib/ai-mocks-2026/papers/ai-hl-set-c-paper-1.json"),
  "ai-hl-set-c-paper-2": () => import("@/content/ib/ai-mocks-2026/papers/ai-hl-set-c-paper-2.json"),
  "ai-hl-set-d-paper-1": () => import("@/content/ib/ai-mocks-2026/papers/ai-hl-set-d-paper-1.json"),
  "ai-hl-set-d-paper-2": () => import("@/content/ib/ai-mocks-2026/papers/ai-hl-set-d-paper-2.json"),
};
const cache = new Map<string, Promise<MathsMockPaper>>();
export async function getMathsMockPaper(id: string): Promise<MathsMockPaper | undefined> {
  const meta = getMathsMock(id), loader = loaders[id as keyof typeof loaders];
  if (!meta || !loader) return undefined;
  if (!cache.has(id)) cache.set(id, loader().then(module => validateMathsMockPaper(module.default, meta)).catch(error => { cache.delete(id); throw error; }));
  return cache.get(id);
}
export function mathsMockPrompt(paper: MathsMockPaper, meta: MathsMockMeta): MathsMockPrompt {
  return { ...meta, questions: paper.questions.map(q => ({ number: q.number, section: q.section, marks: q.marks, stem: q.stem, parts: q.parts,
    ...(q.diagramSvg ? { diagramUrl: `data:image/svg+xml;base64,${Buffer.from(q.diagramSvg).toString("base64")}` } : {}) })) };
}
