import { z } from "zod";
import { ibSyllabusSubtopics, type IbCourseLevel, type IbSubject, type IbSyllabusSubtopic } from "./catalog.ts";

export const IB_COLLECTIONS = [
  { id: "number-algebra", subject: "math-aa-hl", topicId: "number-algebra", code: "01", title: "Number & algebra", description: "Sequences, logarithms, binomial expansion, complex numbers and proof." },
  { id: "functions", subject: "math-aa-hl", topicId: "functions", code: "02", title: "Functions", description: "Graphs, transformations, inverses, equations and mathematical models." },
  { id: "geometry-trigonometry", subject: "math-aa-hl", topicId: "geometry-trigonometry", code: "03", title: "Geometry & trigonometry", description: "Triangles, circles, trigonometric functions, vectors, lines and planes." },
  { id: "statistics-probability", subject: "math-aa-hl", topicId: "statistics-probability", code: "04", title: "Statistics & probability", description: "Data, probability, random variables and statistical distributions." },
  { id: "calculus-1", subject: "math-aa-hl", topicId: "calculus", code: "05A", title: "Calculus I", description: "Differentiation, tangents, optimisation, related rates and limits." },
  { id: "calculus-2", subject: "math-aa-hl", topicId: "calculus", code: "05B", title: "Calculus II", description: "Integration, areas, volumes, differential equations and series." },
  { id: "physics-space-time-motion", subject: "physics-hl", topicId: "space-time-motion", code: "A", title: "Space, time & motion", description: "Kinematics, forces, momentum, energy, rigid bodies and relativity." },
  { id: "physics-particulate-matter", subject: "physics-hl", topicId: "particulate-matter", code: "B", title: "The particulate nature of matter", description: "Thermal transfers, the greenhouse effect, gas laws, thermodynamics and circuits." },
  { id: "physics-wave-behaviour", subject: "physics-hl", topicId: "wave-behaviour", code: "C", title: "Wave behaviour", description: "Oscillations, wave models, interference, standing waves and the Doppler effect." },
  { id: "physics-fields", subject: "physics-hl", topicId: "fields", code: "D", title: "Fields", description: "Gravitational, electric and magnetic fields, charged-particle motion and induction." },
  { id: "physics-nuclear-quantum", subject: "physics-hl", topicId: "nuclear-quantum", code: "E", title: "Nuclear & quantum physics", description: "Atomic structure, quantum physics, radioactivity, fission, fusion and stars." },
  { id: "chemistry-structure-1", subject: "chemistry", topicId: "structure-1", code: "S1", title: "Models of the particulate nature of matter", description: "Particles, atoms, electron configurations, the mole and ideal gases." },
  { id: "chemistry-structure-2", subject: "chemistry", topicId: "structure-2", code: "S2", title: "Models of bonding and structure", description: "Ionic, covalent and metallic models, molecular shapes and materials." },
  { id: "chemistry-structure-3", subject: "chemistry", topicId: "structure-3", code: "S3", title: "Classification of matter", description: "Periodic patterns, functional groups and the classification of organic compounds." },
  { id: "chemistry-reactivity-1", subject: "chemistry", topicId: "reactivity-1", code: "R1", title: "What drives chemical reactions?", description: "Enthalpy changes, energy cycles, fuels, entropy and spontaneity." },
  { id: "chemistry-reactivity-2", subject: "chemistry", topicId: "reactivity-2", code: "R2", title: "How much, how fast and how far?", description: "Amounts of chemical change, reaction rates and equilibrium." },
  { id: "chemistry-reactivity-3", subject: "chemistry", topicId: "reactivity-3", code: "R3", title: "What are the mechanisms of chemical change?", description: "Proton transfer, electron transfer, electron sharing and reaction mechanisms." },
] as const;
export type IbCollectionId = typeof IB_COLLECTIONS[number]["id"];
export type IbCollectionSummary = {
  id: string; subject: IbSubject; title: string; code: string; description: string; count: number; subtopics: string[];
  syllabus?: (IbSyllabusSubtopic & { count: number })[];
};
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
/** Remote diagrams may only use the owned media origin or an explicit HTTPS CDN override. */
export function safeDiagramUrl(value: string, trustedOrigin = process.env.IB_DIAGRAM_CDN_ORIGIN || "https://media.thrivingscholars.com") {
  if (!trustedOrigin) return false;
  try {
    const url = new URL(value);
    const trusted = new URL(trustedOrigin);
    return trusted.protocol === "https:" && trusted.pathname === "/" && !trusted.search && !trusted.hash
      && !trusted.username && !trusted.password && url.protocol === "https:"
      && !url.username && !url.password && url.origin === trusted.origin;
  } catch { return false; }
}
const text = z.string().trim().min(1);
const diagram = z.string().refine(safeDiagram, "Diagram must be self-contained, non-interactive SVG with a viewBox").optional();
const diagramUrl = z.string().url().refine(value => safeDiagramUrl(value), "Diagram URL must use IB_DIAGRAM_CDN_ORIGIN").optional();
const optionLabel = z.enum(["A", "B", "C", "D"]);
const commonQuestion = z.object({
  number: z.number().int().positive(), title: text, subtopic: text,
  difficulty: z.enum(["easy", "medium", "hard"]), calculator: z.boolean(), marks: z.number().int().min(1).max(60), stem: text,
  parts: z.array(z.object({ label: text, prompt: text, marks: z.number().int().positive() })),
  markScheme: z.array(z.object({ part: z.string(), steps: z.array(z.object({ code: z.string().regex(/^(?:[MAR][1-9]|AG)$/), text })).min(1) })).min(1),
  diagramSvg: diagram, markSchemeDiagramSvg: diagram, diagramUrl, markSchemeDiagramUrl: diagramUrl, answerSummary: z.string().optional(),
  source: z.object({ document: text, question: z.number().int().positive() }),
  verification: z.object({ method: text, notes: text }), status: z.enum(["draft", "published"]),
});
const mathsQuestion = commonQuestion.extend({
  id: z.string().regex(/^ib-aa-(?:na|fn|gt|sp|c1|c2)-\d{3}$/),
  subject: z.literal("math-aa-hl"),
  topicId: z.enum(["number-algebra", "functions", "geometry-trigonometry", "statistics-probability", "calculus"]),
  collectionId: z.enum(["number-algebra", "functions", "geometry-trigonometry", "statistics-probability", "calculus-1", "calculus-2"]),
});
const physicsQuestion = commonQuestion.extend({
  id: z.string().regex(/^ib-phy-[abcde]-\d{3}$/),
  subject: z.literal("physics-hl"),
  topicId: z.enum(["space-time-motion", "particulate-matter", "wave-behaviour", "fields", "nuclear-quantum"]),
  collectionId: z.enum(["physics-space-time-motion", "physics-particulate-matter", "physics-wave-behaviour", "physics-fields", "physics-nuclear-quantum"]),
  syllabusCode: z.string().regex(/^[A-E]\.[1-5]$/), level: z.enum(["core", "ahl"]),
  questionType: z.enum(["multiple-choice", "structured", "data-based"]), calculator: z.literal(true),
  options: z.array(z.object({ label: optionLabel, text })).length(4).optional(), correctOption: optionLabel.optional(),
  source: z.object({ document: z.literal("Independent syllabus-authored practice"), question: z.number().int().positive() }),
});
const chemistryQuestion = commonQuestion.extend({
  id: z.string().regex(/^ib-chem-[sr][1-3]-\d{3}$/),
  subject: z.literal("chemistry"),
  topicId: z.enum(["structure-1", "structure-2", "structure-3", "reactivity-1", "reactivity-2", "reactivity-3"]),
  collectionId: z.enum(["chemistry-structure-1", "chemistry-structure-2", "chemistry-structure-3", "chemistry-reactivity-1", "chemistry-reactivity-2", "chemistry-reactivity-3"]),
  syllabusCode: z.string().regex(/^[SR][1-3]\.[1-5]$/), level: z.enum(["sl", "ahl"]),
  questionType: z.enum(["multiple-choice", "structured", "data-based"]), calculator: z.literal(true),
  options: z.array(z.object({ label: optionLabel, text })).length(4).optional(), correctOption: optionLabel.optional(),
  source: z.object({ document: z.literal("Independent syllabus-authored practice"), question: z.number().int().positive() }),
});
export const ibQuestionSchema = z.discriminatedUnion("subject", [mathsQuestion, physicsQuestion, chemistryQuestion]).superRefine((q, ctx) => {
  const fail = (message: string) => ctx.addIssue({ code: "custom", message });
  const collection = getIbCollection(q.collectionId);
  if (collection?.topicId !== q.topicId || collection?.subject !== q.subject) fail("Collection and syllabus topic disagree");
  if (q.number !== q.source.question) fail("Question numbering must retain its reference mapping");
  if (q.subject === "physics-hl" || q.subject === "chemistry") {
    const syllabus = ibSyllabusSubtopics(q.subject, q.topicId).find(item => item.code === q.syllabusCode);
    if (!syllabus) fail("Syllabus code must belong to the question's subject and theme");
    if (syllabus?.additionalHlOnly && q.level !== "ahl") fail("This syllabus subtopic is additional HL only");
    const prefix = q.subject === "chemistry" ? "ib-chem-" : "ib-phy-";
    if (q.id !== prefix + collection?.code.toLowerCase() + "-" + String(q.number).padStart(3, "0")) fail("Question ID must match its theme and question number");
    if (q.questionType === "multiple-choice") {
      if (q.marks !== 1 || q.parts.length) fail("Multiple-choice questions award exactly one mark and have no parts");
      if (!q.options || q.options.map(option => option.label).join("") !== "ABCD" || !q.correctOption) fail("Multiple-choice questions require options A–D in order and a private correct option");
      if (q.markScheme.length !== 1 || q.markScheme[0].steps.length !== 1 || q.markScheme[0].steps[0].code !== "A1") fail("Multiple-choice schemes require a single A1 step with the correct choice and its scientific reasoning");
    } else if (q.options !== undefined || q.correctOption !== undefined) fail("Only multiple-choice questions may define options or a correct option");
  }
  const stepTotal = q.markScheme.reduce((total, group) => total + group.steps.reduce((sum, step) => sum + markValue(step.code), 0), 0);
  if (stepTotal !== q.marks) fail("Scheme awards " + stepTotal + ", question awards " + q.marks);
  if (new Set(q.parts.map(p => p.label)).size !== q.parts.length) fail("Duplicate part labels");
  if (new Set(q.markScheme.map(p => p.part)).size !== q.markScheme.length) fail("Duplicate scheme groups");
  if (q.parts.length) {
    if (q.parts.reduce((sum, part) => sum + part.marks, 0) !== q.marks) fail("Part totals disagree with question marks");
    if (q.markScheme.length !== q.parts.length) fail("Every part needs one scheme group");
    for (const part of q.parts) {
      const group = q.markScheme.find(g => g.part === part.label);
      if (!group || group.steps.reduce((sum, step) => sum + markValue(step.code), 0) !== part.marks) fail("Incorrect allocation for part " + part.label);
    }
  } else if (q.markScheme.length !== 1 || q.markScheme[0].part !== "") fail("Unparted question requires one unlabelled scheme group");
});
export type IbQuestion = z.infer<typeof ibQuestionSchema>;
export function questionAvailableForCourse(q: IbQuestion, course: IbCourseLevel = "hl") {
  return q.subject !== "chemistry" || course === "hl" || q.level === "sl";
}
type PromptOnly<T> = T extends unknown ? Omit<T, "markScheme" | "markSchemeDiagramSvg" | "markSchemeDiagramUrl" | "answerSummary" | "source" | "verification" | "correctOption"> : never;
export type IbQuestionPrompt = PromptOnly<IbQuestion>;
/** An explicit allowlist keeps solutions and private authoring metadata out of question views. */
export function questionPrompt(q: IbQuestion): IbQuestionPrompt {
  const prompt = { id: q.id, topicId: q.topicId, collectionId: q.collectionId, number: q.number,
    title: q.title, subtopic: q.subtopic, difficulty: q.difficulty, calculator: q.calculator, marks: q.marks,
    stem: q.stem, parts: q.parts, diagramSvg: q.diagramSvg, diagramUrl: q.diagramUrl, status: q.status };
  if (q.subject === "physics-hl") return { ...prompt, subject: q.subject, topicId: q.topicId, collectionId: q.collectionId,
    calculator: q.calculator, syllabusCode: q.syllabusCode, level: q.level, questionType: q.questionType, options: q.options };
  if (q.subject === "chemistry") return { ...prompt, subject: q.subject, topicId: q.topicId, collectionId: q.collectionId,
    calculator: q.calculator, syllabusCode: q.syllabusCode, level: q.level, questionType: q.questionType, options: q.options };
  return { ...prompt, subject: q.subject, topicId: q.topicId, collectionId: q.collectionId };
}
