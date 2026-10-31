import { z } from "zod";
import { ibSyllabusSubtopics, ibCoreLevel, ibHasCourseChoice, type IbCourseLevel, type IbSubject, type IbSyllabusSubtopic } from "./catalog.ts";

export const IB_COLLECTIONS = [
  { id: "economics-introduction", subject: "economics", topicId: "introduction", code: "1", title: "Introduction to economics", description: "Scarcity, choice, economic models and ways of thinking." },
  { id: "economics-microeconomics", subject: "economics", topicId: "microeconomics", code: "2", title: "Microeconomics", description: "Markets, elasticity, intervention, market failure and market power." },
  { id: "economics-macroeconomics", subject: "economics", topicId: "macroeconomics", code: "3", title: "Macroeconomics", description: "Economic activity, objectives, inequality and policy choices." },
  { id: "economics-global-economy", subject: "economics", topicId: "global-economy", code: "4", title: "The global economy", description: "Trade, exchange rates, development and international policy." },
  { id: "business-introduction-business", subject: "business-management", topicId: "introduction-business", code: "1", title: "Introduction to business management", description: "Business entities, objectives, stakeholders and growth." },
  { id: "business-human-resources", subject: "business-management", topicId: "human-resources", code: "2", title: "Human resource management", description: "People, leadership, motivation, organization and communication." },
  { id: "business-finance-accounts", subject: "business-management", topicId: "finance-accounts", code: "3", title: "Finance and accounts", description: "Finance, accounting, cash flow, ratios and investment decisions." },
  { id: "business-marketing", subject: "business-management", topicId: "marketing", code: "4", title: "Marketing", description: "Planning, research, the marketing mix and international markets." },
  { id: "business-operations-management", subject: "business-management", topicId: "operations-management", code: "5", title: "Operations management", description: "Production, quality, location, break-even and operational decisions." },
  { id: "number-algebra", subject: "math-aa-hl", topicId: "number-algebra", code: "01", title: "Number & algebra", description: "Sequences, logarithms, binomial expansion, complex numbers and proof." },
  { id: "functions", subject: "math-aa-hl", topicId: "functions", code: "02", title: "Functions", description: "Graphs, transformations, inverses, equations and mathematical models." },
  { id: "geometry-trigonometry", subject: "math-aa-hl", topicId: "geometry-trigonometry", code: "03", title: "Geometry & trigonometry", description: "Triangles, circles, trigonometric functions, vectors, lines and planes." },
  { id: "statistics-probability", subject: "math-aa-hl", topicId: "statistics-probability", code: "04", title: "Statistics & probability", description: "Data, probability, random variables and statistical distributions." },
  { id: "calculus-1", subject: "math-aa-hl", topicId: "calculus", code: "05A", title: "Calculus I", description: "Differentiation, tangents, optimisation, related rates and limits." },
  { id: "calculus-2", subject: "math-aa-hl", topicId: "calculus", code: "05B", title: "Calculus II", description: "Integration, areas, volumes, differential equations and series." },
  ...(["aa-sl", "ai-sl", "ai-hl"] as const).flatMap(course => [
    { id: `${course}-number-algebra` as const, subject: course === "aa-sl" ? "math-aa-sl" as const : course === "ai-hl" ? "math-ai-hl" as const : "math-ai-sl" as const, topicId: "number-algebra" as const, code: "01", title: "Number & algebra", description: course === "aa-sl" ? "Sequences, logarithms, binomial expansion and mathematical reasoning." : "Sequences, estimation, financial mathematics and numerical models." },
    { id: `${course}-functions` as const, subject: course === "aa-sl" ? "math-aa-sl" as const : course === "ai-hl" ? "math-ai-hl" as const : "math-ai-sl" as const, topicId: "functions" as const, code: "02", title: "Functions", description: course === "aa-sl" ? "Graphs, transformations, inverses and equations." : "Linear, quadratic, exponential and sinusoidal models in context." },
    { id: `${course}-geometry-trigonometry` as const, subject: course === "aa-sl" ? "math-aa-sl" as const : course === "ai-hl" ? "math-ai-hl" as const : "math-ai-sl" as const, topicId: "geometry-trigonometry" as const, code: "03", title: "Geometry & trigonometry", description: course === "aa-sl" ? "Triangles, radians, circular measure, identities and trigonometric equations." : "Measurement, trigonometry, bearings and Voronoi diagrams." },
    { id: `${course}-statistics-probability` as const, subject: course === "aa-sl" ? "math-aa-sl" as const : course === "ai-hl" ? "math-ai-hl" as const : "math-ai-sl" as const, topicId: "statistics-probability" as const, code: "04", title: "Statistics & probability", description: course === "aa-sl" ? "Data, regression, probability, random variables and distributions." : "Data analysis, probability, distributions and hypothesis testing." },
    { id: `${course}-calculus` as const, subject: course === "aa-sl" ? "math-aa-sl" as const : course === "ai-hl" ? "math-ai-hl" as const : "math-ai-sl" as const, topicId: "calculus" as const, code: "05", title: "Calculus", description: course === "aa-sl" ? "Differentiation, integration, optimisation and kinematics." : "Rates of change, polynomial differentiation, optimisation and integration." },
  ]),
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
  { id: "biology-unity-diversity", subject: "biology", topicId: "unity-diversity", code: "A", title: "Unity and diversity", description: "Molecules, cells, organisms and the origins of biological diversity." },
  { id: "biology-form-function", subject: "biology", topicId: "form-function", code: "B", title: "Form and function", description: "Structure and function from biological molecules to ecological niches." },
  { id: "biology-interaction-interdependence", subject: "biology", topicId: "interaction-interdependence", code: "C", title: "Interaction and interdependence", description: "Metabolism, signalling, body systems and ecological interactions." },
  { id: "biology-continuity-change", subject: "biology", topicId: "continuity-change", code: "D", title: "Continuity and change", description: "Inheritance, reproduction, homeostasis, selection and environmental change." },
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
  return code === "AG" || code === "IND" ? 0 : Number(code.slice(1));
}
export function schemeGroupValue(group: { steps: {code: string}[]; rubric?: {maxMarks: number} }) { return group.rubric?.maxMarks ?? group.steps.reduce((sum, step) => sum + markValue(step.code), 0); }
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
const band = z.object({ min: z.number().int().nonnegative(), max: z.number().int().nonnegative(), descriptor: text });
const rubric = z.object({ maxMarks: z.number().int().positive().max(60), bands: z.array(band).min(2).optional(), criteria: z.array(z.object({id: text,title: text,maxMarks: z.number().int().positive(),bands: z.array(band).min(2)})).min(1).optional() });
const commonQuestion = z.object({
  number: z.number().int().positive(), title: text, subtopic: text,
  difficulty: z.enum(["easy", "medium", "hard"]), calculator: z.boolean(), marks: z.number().int().min(1).max(60), stem: text,
  parts: z.array(z.object({ label: text, prompt: text, marks: z.number().int().positive() })),
  markScheme: z.array(z.object({ part: z.string(), steps: z.array(z.object({ code: z.string().regex(/^(?:[MAR][1-9]|AG|IND)$/), text })).min(1), rubric: rubric.optional() })).min(1),
  diagramSvg: diagram, markSchemeDiagramSvg: diagram, diagramUrl, markSchemeDiagramUrl: diagramUrl, diagramCaption: text.optional(), markSchemeDiagramCaption: text.optional(), answerSummary: z.string().optional(),
  source: z.object({ document: text, question: z.number().int().positive() }),
  verification: z.object({ method: text, notes: text }), status: z.enum(["draft", "published"]),
});
const mathsQuestion = commonQuestion.extend({
  id: z.string().regex(/^ib-aa-(?:na|fn|gt|sp|c1|c2)-\d{3}$/),
  subject: z.literal("math-aa-hl"),
  topicId: z.enum(["number-algebra", "functions", "geometry-trigonometry", "statistics-probability", "calculus"]),
  collectionId: z.enum(["number-algebra", "functions", "geometry-trigonometry", "statistics-probability", "calculus-1", "calculus-2"]),
  syllabusCode: z.string().regex(/^[1-5]\.\d{1,2}$/).optional(), level: z.enum(["sl", "ahl"]).optional(),
  examStyle: z.enum(["short-response", "extended-response", "problem-solving"]).optional(),
});
const mathsSlFields = {
  topicId: z.enum(["number-algebra", "functions", "geometry-trigonometry", "statistics-probability", "calculus"]),
  syllabusCode: z.string().regex(/^[1-5]\.\d{1,2}$/), level: z.literal("sl"),
  examStyle: z.enum(["short-response", "extended-response"]),
  source: z.object({ document: z.literal("Independent syllabus-authored practice"), question: z.number().int().positive() }),
};
const mathsAaSlQuestion = commonQuestion.extend({ ...mathsSlFields,
  id: z.string().regex(/^ib-aasl-(?:na|fn|gt|sp|ca)-\d{3}$/), subject: z.literal("math-aa-sl"),
  collectionId: z.enum(["aa-sl-number-algebra", "aa-sl-functions", "aa-sl-geometry-trigonometry", "aa-sl-statistics-probability", "aa-sl-calculus"]),
});
const mathsAiSlQuestion = commonQuestion.extend({ ...mathsSlFields,
  id: z.string().regex(/^ib-aisl-(?:na|fn|gt|sp|ca)-\d{3}$/), subject: z.literal("math-ai-sl"), calculator: z.literal(true),
  collectionId: z.enum(["ai-sl-number-algebra", "ai-sl-functions", "ai-sl-geometry-trigonometry", "ai-sl-statistics-probability", "ai-sl-calculus"]),
});
const mathsAiHlQuestion = commonQuestion.extend({ ...mathsSlFields,
  id: z.string().regex(/^ib-aihl-(?:na|fn|gt|sp|ca)-\d{3}$/), subject: z.literal("math-ai-hl"), calculator: z.literal(true), level: z.enum(["sl", "ahl"]),
  examStyle: z.enum(["short-response", "extended-response", "problem-solving"]),
  collectionId: z.enum(["ai-hl-number-algebra", "ai-hl-functions", "ai-hl-geometry-trigonometry", "ai-hl-statistics-probability", "ai-hl-calculus"]),
});
const humanitiesFields = { syllabusCode: z.string().regex(/^[1-5]\.\d{1,2}$/), level: z.enum(["sl", "ahl"]), examStyle: z.enum(["paper-1", "paper-2", "paper-3"]), source: z.object({document:z.literal("Independent syllabus-authored practice"),question:z.number().int().positive()}) };
const economicsQuestion = commonQuestion.extend({ ...humanitiesFields,
  id:z.string().regex(/^ib-econ-(?:in|mi|ma|gl)-\d{3}$/),subject:z.literal("economics"),
  topicId:z.enum(["introduction","microeconomics","macroeconomics","global-economy"]),collectionId:z.enum(["economics-introduction","economics-microeconomics","economics-macroeconomics","economics-global-economy"]),
  questionType:z.enum(["structured","data-response","essay","policy-response"]),
});
const businessQuestion = commonQuestion.extend({ ...humanitiesFields,
  id:z.string().regex(/^ib-bm-u[1-5]-\d{3}$/),subject:z.literal("business-management"),calculator:z.literal(true),
  topicId:z.enum(["introduction-business","human-resources","finance-accounts","marketing","operations-management"]),collectionId:z.enum(["business-introduction-business","business-human-resources","business-finance-accounts","business-marketing","business-operations-management"]),
  questionType:z.enum(["structured","case-study","data-response","extended-response"]),
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
const biologyQuestion = commonQuestion.extend({
  id: z.string().regex(/^ib-bio-[abcd]-\d{3}$/), subject: z.literal("biology"),
  topicId: z.enum(["unity-diversity", "form-function", "interaction-interdependence", "continuity-change"]),
  collectionId: z.enum(["biology-unity-diversity", "biology-form-function", "biology-interaction-interdependence", "biology-continuity-change"]),
  syllabusCode: z.string().regex(/^[A-D][1-4]\.[1-3]$/), level: z.enum(["sl", "ahl"]),
  questionType: z.enum(["multiple-choice", "structured", "data-based"]), calculator: z.literal(true),
  options: z.array(z.object({ label: optionLabel, text })).length(4).optional(), correctOption: optionLabel.optional(),
  source: z.object({ document: z.literal("Independent syllabus-authored practice"), question: z.number().int().positive() }),
});
export const ibQuestionSchema = z.discriminatedUnion("subject", [mathsQuestion, mathsAaSlQuestion, mathsAiSlQuestion, mathsAiHlQuestion, economicsQuestion, businessQuestion, physicsQuestion, chemistryQuestion, biologyQuestion]).superRefine((q, ctx) => {
  const fail = (message: string) => ctx.addIssue({ code: "custom", message });
  const collection = getIbCollection(q.collectionId);
  if (collection?.topicId !== q.topicId || collection?.subject !== q.subject) fail("Collection and syllabus topic disagree");
  if (q.number !== q.source.question) fail("Question numbering must retain its reference mapping");
  if (q.subject === "physics-hl" || q.subject === "chemistry" || q.subject === "biology") {
    const syllabus = ibSyllabusSubtopics(q.subject, q.topicId).find(item => item.code === q.syllabusCode);
    if (!syllabus) fail("Syllabus code must belong to the question's subject and theme");
    if (syllabus?.additionalHlOnly && q.level !== "ahl") fail("This syllabus subtopic is additional HL only");
    const prefix = q.subject === "biology" ? "ib-bio-" : q.subject === "chemistry" ? "ib-chem-" : "ib-phy-";
    if (q.id !== prefix + collection?.code.toLowerCase() + "-" + String(q.number).padStart(3, "0")) fail("Question ID must match its theme and question number");
    if (q.questionType === "multiple-choice") {
      if (q.marks !== 1 || q.parts.length) fail("Multiple-choice questions award exactly one mark and have no parts");
      if (!q.options || q.options.map(option => option.label).join("") !== "ABCD" || !q.correctOption) fail("Multiple-choice questions require options A–D in order and a private correct option");
      if (q.markScheme.length !== 1 || q.markScheme[0].steps.length !== 1 || q.markScheme[0].steps[0].code !== "A1") fail("Multiple-choice schemes require a single A1 step with the correct choice and its scientific reasoning");
    } else if (q.options !== undefined || q.correctOption !== undefined) fail("Only multiple-choice questions may define options or a correct option");
  } else if (q.subject === "economics" || q.subject === "business-management") {
    const syllabus = ibSyllabusSubtopics(q.subject, q.topicId).find(item => item.code === q.syllabusCode);
    if (!syllabus || syllabus.additionalHlOnly && q.level !== "ahl") fail("Humanities syllabus code and content level disagree");
    const prefix = q.subject === "economics" ? "ib-econ-" + ({introduction:"in",microeconomics:"mi",macroeconomics:"ma","global-economy":"gl"}[q.topicId]) : "ib-bm-u" + collection?.code;
    if (q.id !== prefix + "-" + String(q.number).padStart(3,"0")) fail("Humanities ID must match course, unit and number");
    if (q.subject === "economics" && q.calculator !== (q.examStyle !== "paper-1")) fail("Economics calculator label must match its paper");
    if (q.subject === "economics" && q.examStyle === "paper-2" && q.level !== "sl") fail("The current shared Economics Paper 2 excludes AHL extensions");
    if (q.examStyle === "paper-3" && q.level !== "ahl") fail("Humanities Paper 3 is HL only");
    if (q.subject === "business-management" && q.examStyle === "paper-1" && q.level !== "sl") fail("The shared Business Paper 1 excludes additional HL content");
  } else {
    const topicNumber = { "number-algebra": 1, functions: 2, "geometry-trigonometry": 3, "statistics-probability": 4, calculus: 5 }[q.topicId];
    // Legacy HL collections include mixed-topic problems, such as optimisation in geometry.
    if ((q.subject === "math-aa-sl" || q.subject === "math-ai-sl") && q.syllabusCode && !q.syllabusCode.startsWith(topicNumber + ".")) fail("Maths syllabus code must belong to its topic");
    const suffix = q.collectionId === "calculus-1" ? "c1" : q.collectionId === "calculus-2" ? "c2" : ({ "number-algebra": "na", functions: "fn", "geometry-trigonometry": "gt", "statistics-probability": "sp", calculus: "ca" }[q.topicId]);
    const prefix = q.subject === "math-aa-sl" ? "ib-aasl-" : q.subject === "math-ai-sl" ? "ib-aisl-" : q.subject === "math-ai-hl" ? "ib-aihl-" : "ib-aa-";
    if (q.id !== prefix + suffix + "-" + String(q.number).padStart(3, "0")) fail("Maths ID must match its course, topic and number");
    if (q.examStyle === "problem-solving" && !q.calculator) fail("HL Maths Paper 3 problem solving requires a calculator");
  }
  function checkBands(bands: {min:number;max:number}[], maximum: number) {
    let next = 0;
    for (const item of bands) { if (item.min !== next || item.max < item.min) fail("Mark bands must cover every integer score without gaps or overlap"); next = item.max + 1; }
    if (next !== maximum + 1) fail("Mark bands do not cover the stated maximum");
  }
  for (const group of q.markScheme) {
    if (group.rubric) {
      if (q.subject !== "economics" && q.subject !== "business-management") fail("Levelled rubrics are reserved for humanities responses");
      if (group.steps.some(step => step.code !== "IND")) fail("Levelled schemes use indicative content, not additive point awards");
      if (Boolean(group.rubric.bands) === Boolean(group.rubric.criteria)) fail("Choose best-fit bands or analytic criteria");
      if (group.rubric.bands) checkBands(group.rubric.bands, group.rubric.maxMarks);
      if (group.rubric.criteria) {
        if (group.rubric.criteria.reduce((sum,c)=>sum+c.maxMarks,0) !== group.rubric.maxMarks) fail("Criterion maxima must add to the part maximum");
        if (new Set(group.rubric.criteria.map(c=>c.id)).size !== group.rubric.criteria.length) fail("Duplicate assessment criterion");
        group.rubric.criteria.forEach(c=>checkBands(c.bands,c.maxMarks));
      }
    } else if (group.steps.some(step => step.code === "IND")) fail("Indicative content requires a levelled rubric");
  }
  const stepTotal = q.markScheme.reduce((total, group) => total + schemeGroupValue(group), 0);
  if (stepTotal !== q.marks) fail("Scheme awards " + stepTotal + ", question awards " + q.marks);
  if (new Set(q.parts.map(p => p.label)).size !== q.parts.length) fail("Duplicate part labels");
  if (new Set(q.markScheme.map(p => p.part)).size !== q.markScheme.length) fail("Duplicate scheme groups");
  if (q.parts.length) {
    if (q.parts.reduce((sum, part) => sum + part.marks, 0) !== q.marks) fail("Part totals disagree with question marks");
    if (q.markScheme.length !== q.parts.length) fail("Every part needs one scheme group");
    for (const part of q.parts) {
      const group = q.markScheme.find(g => g.part === part.label);
      if (!group || schemeGroupValue(group) !== part.marks) fail("Incorrect allocation for part " + part.label);
    }
  } else if (q.markScheme.length !== 1 || q.markScheme[0].part !== "") fail("Unparted question requires one unlabelled scheme group");
});
export type IbQuestion = z.infer<typeof ibQuestionSchema>;
export function questionAvailableForCourse(q: IbQuestion, course: IbCourseLevel = "hl") {
  return !ibHasCourseChoice(q.subject) || course === "hl" || q.level === ibCoreLevel(q.subject);
}
type PromptOnly<T> = T extends unknown ? Omit<T, "markScheme" | "markSchemeDiagramSvg" | "markSchemeDiagramUrl" | "markSchemeDiagramCaption" | "answerSummary" | "source" | "verification" | "correctOption"> : never;
export type IbQuestionPrompt = PromptOnly<IbQuestion>;
export function isScienceQuestion(q: IbQuestion | IbQuestionPrompt): q is Extract<IbQuestion | IbQuestionPrompt, { subject: "physics-hl" | "chemistry" | "biology" }> {
  return q.subject === "physics-hl" || q.subject === "chemistry" || q.subject === "biology";
}
export function isHumanitiesQuestion(q: IbQuestion | IbQuestionPrompt): q is Extract<IbQuestion | IbQuestionPrompt, {subject:"economics" | "business-management"}> { return q.subject === "economics" || q.subject === "business-management"; }
/** An explicit allowlist keeps solutions and private authoring metadata out of question views. */
export function questionPrompt(q: IbQuestion): IbQuestionPrompt {
  const prompt = { id: q.id, topicId: q.topicId, collectionId: q.collectionId, number: q.number,
    title: q.title, subtopic: q.subtopic, difficulty: q.difficulty, calculator: q.calculator, marks: q.marks,
    stem: q.stem, parts: q.parts, diagramSvg: q.diagramSvg, diagramUrl: q.diagramUrl, diagramCaption: q.diagramCaption, status: q.status };
  if (q.subject === "physics-hl") return { ...prompt, subject: q.subject, topicId: q.topicId, collectionId: q.collectionId,
    calculator: q.calculator, syllabusCode: q.syllabusCode, level: q.level, questionType: q.questionType, options: q.options };
  if (q.subject === "chemistry") return { ...prompt, subject: q.subject, topicId: q.topicId, collectionId: q.collectionId,
    calculator: q.calculator, syllabusCode: q.syllabusCode, level: q.level, questionType: q.questionType, options: q.options };
  if (q.subject === "biology") return { ...prompt, subject: q.subject, topicId: q.topicId, collectionId: q.collectionId,
    calculator: q.calculator, syllabusCode: q.syllabusCode, level: q.level, questionType: q.questionType, options: q.options };
  if (q.subject === "math-aa-sl") return { ...prompt, subject: q.subject, topicId: q.topicId, collectionId: q.collectionId,
    syllabusCode: q.syllabusCode, level: q.level, examStyle: q.examStyle };
  if (q.subject === "math-ai-sl") return { ...prompt, subject: q.subject, topicId: q.topicId, collectionId: q.collectionId,
    calculator: q.calculator, syllabusCode: q.syllabusCode, level: q.level, examStyle: q.examStyle };
  if (q.subject === "math-ai-hl") return { ...prompt, subject: q.subject, topicId: q.topicId, collectionId: q.collectionId,
    calculator: q.calculator, syllabusCode: q.syllabusCode, level: q.level, examStyle: q.examStyle };
  if (q.subject === "economics") return { ...prompt, subject:q.subject,topicId:q.topicId,collectionId:q.collectionId,syllabusCode:q.syllabusCode,level:q.level,examStyle:q.examStyle,questionType:q.questionType };
  if (q.subject === "business-management") return { ...prompt, subject:q.subject,topicId:q.topicId,collectionId:q.collectionId,calculator:q.calculator,syllabusCode:q.syllabusCode,level:q.level,examStyle:q.examStyle,questionType:q.questionType };
  return { ...prompt, subject: q.subject, topicId: q.topicId, collectionId: q.collectionId,
    syllabusCode: q.syllabusCode, level: q.level, examStyle: q.examStyle };
}
