import { z } from "zod";

export const IB_COLLECTIONS = [
  { id: "number-algebra", topicId: "number-algebra", code: "01", title: "Number & algebra", description: "Sequences, logarithms, binomial expansion, complex numbers and proof." },
  { id: "functions", topicId: "functions", code: "02", title: "Functions", description: "Graphs, transformations, inverses, equations and mathematical models." },
  { id: "geometry-trigonometry", topicId: "geometry-trigonometry", code: "03", title: "Geometry & trigonometry", description: "Triangles, circles, trigonometric functions, vectors, lines and planes." },
  { id: "statistics-probability", topicId: "statistics-probability", code: "04", title: "Statistics & probability", description: "Data, probability, random variables and statistical distributions." },
  { id: "calculus-1", topicId: "calculus", code: "05A", title: "Calculus I", description: "Differentiation, tangents, optimisation, related rates and limits." },
  { id: "calculus-2", topicId: "calculus", code: "05B", title: "Calculus II", description: "Integration, areas, volumes, differential equations and series." },
] as const;
export type IbCollectionId = typeof IB_COLLECTIONS[number]["id"];
export type IbCollectionSummary = { id: string; title: string; code: string; description: string; count: number; subtopics: string[] };
export function getIbCollection(id: string) {
  return IB_COLLECTIONS.find(collection => collection.id === id);
}
export function markValue(code: string) {
  return code === "AG" ? 0 : Number(code.slice(1));
}
export function safeDiagram(svg: string) {
  return svg.length <= 300_000 && /^\s*<svg\b/.test(svg) && /viewBox\s*=/.test(svg)
    && /<\/svg>\s*$/.test(svg)
    && !/<(?:script|foreignObject|iframe|object|embed|image|style|animate|set)\b|\bon\w+\s*=|(?:href|src)\s*=|url\s*\(|<!DOCTYPE|<!ENTITY/i.test(svg);
}
const text = z.string().trim().min(1);
const diagram = z.string().refine(safeDiagram, "Diagram must be self-contained, non-interactive SVG with a viewBox").optional();
export const ibQuestionSchema = z.object({
  id: z.string().regex(/^ib-aa-(?:na|fn|gt|sp|c1|c2)-\d{3}$/),
  subject: z.literal("math-aa-hl"),
  topicId: z.enum(["number-algebra", "functions", "geometry-trigonometry", "statistics-probability", "calculus"]),
  collectionId: z.enum(["number-algebra", "functions", "geometry-trigonometry", "statistics-probability", "calculus-1", "calculus-2"]),
  number: z.number().int().positive(), title: text, subtopic: text,
  difficulty: z.enum(["easy", "medium", "hard"]), calculator: z.boolean(), marks: z.number().int().min(1).max(60), stem: text,
  parts: z.array(z.object({ label: text, prompt: text, marks: z.number().int().positive() })),
  markScheme: z.array(z.object({ part: z.string(), steps: z.array(z.object({ code: z.string().regex(/^(?:[MAR][1-9]|AG)$/), text })).min(1) })).min(1),
  diagramSvg: diagram, markSchemeDiagramSvg: diagram, answerSummary: z.string().optional(),
  source: z.object({ document: text, question: z.number().int().positive() }),
  verification: z.object({ method: text, notes: text }), status: z.enum(["draft", "published"]),
}).superRefine((q, ctx) => {
  const fail = (message: string) => ctx.addIssue({ code: "custom", message });
  if (getIbCollection(q.collectionId)?.topicId !== q.topicId) fail("Collection and syllabus topic disagree");
  if (q.number !== q.source.question) fail("Question numbering must retain its reference mapping");
  const stepTotal = q.markScheme.reduce((total, group) => total + group.steps.reduce((sum, step) => sum + markValue(step.code), 0), 0);
  if (stepTotal !== q.marks) fail(`Scheme awards ${stepTotal}, question awards ${q.marks}`);
  if (new Set(q.parts.map(p => p.label)).size !== q.parts.length) fail("Duplicate part labels");
  if (new Set(q.markScheme.map(p => p.part)).size !== q.markScheme.length) fail("Duplicate scheme groups");
  if (q.parts.length) {
    if (q.parts.reduce((sum, part) => sum + part.marks, 0) !== q.marks) fail("Part totals disagree with question marks");
    if (q.markScheme.length !== q.parts.length) fail("Every part needs one scheme group");
    for (const part of q.parts) {
      const group = q.markScheme.find(g => g.part === part.label);
      if (!group || group.steps.reduce((sum, step) => sum + markValue(step.code), 0) !== part.marks) fail(`Incorrect allocation for part ${part.label}`);
    }
  } else if (q.markScheme.length !== 1 || q.markScheme[0].part !== "") fail("Unparted question requires one unlabelled scheme group");
});
export type IbQuestion = z.infer<typeof ibQuestionSchema>;
export type IbQuestionPrompt = Omit<IbQuestion, "markScheme" | "markSchemeDiagramSvg" | "answerSummary" | "source" | "verification">;
/** The question view never receives solutions or private authoring metadata. */
export function questionPrompt(q: IbQuestion): IbQuestionPrompt {
  return { id: q.id, subject: q.subject, topicId: q.topicId, collectionId: q.collectionId, number: q.number,
    title: q.title, subtopic: q.subtopic, difficulty: q.difficulty, calculator: q.calculator, marks: q.marks,
    stem: q.stem, parts: q.parts, diagramSvg: q.diagramSvg, status: q.status };
}
