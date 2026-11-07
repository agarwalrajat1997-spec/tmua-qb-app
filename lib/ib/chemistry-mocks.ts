import "server-only";
import { z } from "zod";
import { safeDiagram } from "./question";
import { getChemistryPaperMeta, paperSpec, type MockPaper, type ChemistryMockPaper, type ChemistryPaperMeta, type ChemistryMockPrompt, type ChemistryQuestion, type ChemistryPromptQuestion, type ChemistrySolution } from "./chemistry-mock-model";
const text = z.string().min(1).max(50000);
const part = z.object({ label: z.string().min(1).max(24), prompt: text, marks: z.number().int().positive().max(10) });
const question = z.object({ id: z.string().regex(/^chem-(hl|sl)-[ab]-(1a|1b|2)-\d{2}$/), section: z.enum(["1A", "1B", "2"]), number: z.number().int().positive(), title: text, syllabusCode: z.string().regex(/^[SR][1-3]\.[1-5]$/), syllabusRefs: z.array(text).min(1).max(30), level: z.enum(["core", "ahl"]), subtopic: text, difficulty: z.literal("hard"), questionType: z.enum(["multiple-choice", "data-based", "structured"]), marks: z.number().int().positive().max(20), stem: text, parts: z.array(part).max(20), options: z.array(z.object({ label: z.enum(["A", "B", "C", "D"]), text })).optional(), correctOption: z.enum(["A", "B", "C", "D"]).optional(), markScheme: z.array(z.object({ part: z.string().max(24), steps: z.array(z.object({ code: z.string().regex(/^[MARBC][1-9]\d?$/), text })).min(1) })).min(1), answerSummary: text, diagramPng: z.string().regex(/^iVBORw0KGgo[A-Za-z0-9+/=]+$/).max(180000).optional(), diagramSvg: z.string().max(300000).optional(), diagramCaption: z.string().max(2000).optional(), sourceAnchors: z.array(z.object({ document: text, page: z.number().int().positive(), question: text, focus: text })).min(1), changeNotes: text, cognitiveDemand: text, verification: z.object({ method: text, notes: text }) });
const schema = z.object({ id: text, mockId: text, course: z.enum(["sl", "hl"]), set: z.enum(["A", "B"]), paper: z.enum(["1", "2"]), title: text, minutes: z.number().int().positive(), marks: z.number().int().positive(), calculator: z.literal(true), questions: z.array(question).min(1).max(43) });
export function validateChemistryMockPaper(input: unknown, meta: ChemistryPaperMeta): ChemistryMockPaper {
    const p = schema.parse(input), spec = paperSpec(meta.course, meta.paper);
    for (const key of ["id", "mockId", "course", "set", "paper", "minutes", "marks", "calculator"] as const)
        if (p[key] !== meta[key])
            throw new Error(`Chemistry metadata differs: ${key}.`);
    if (p.minutes !== spec.minutes || p.marks !== spec.marks || p.questions.length !== meta.questionCount || p.questions.reduce((s, q) => s + q.marks, 0) !== p.marks)
        throw new Error("Chemistry paper specification differs.");
    if (new Set(p.questions.map(q => q.id)).size !== p.questions.length)
        throw new Error("Duplicate Chemistry question IDs.");
    const sections = p.paper === "1" ? ["1A", "1B"] : ["2"], counts = p.paper === "1" ? [p.course === "hl" ? 40 : 30, p.course === "hl" ? 3 : 2] : [p.course === "hl" ? 6 : 5];
    if (p.questions.some((q, i) => q.section !== (p.paper === "1" && i < counts[0] ? "1A" : p.paper === "1" ? "1B" : "2")))
        throw new Error("Questions must follow section order.");
    sections.forEach((section, index) => { const qs = p.questions.filter(q => q.section === section); if (qs.length !== counts[index] || qs.some((q, i) => q.number !== i + 1))
        throw new Error("Invalid Chemistry section numbering/count."); });
    for (const q of p.questions) {
        if (q.id !== `chem-${p.course}-${p.set.toLowerCase()}-${q.section.toLowerCase()}-${String(q.number).padStart(2, "0")}`)
            throw new Error("Question ID does not match its paper.");
        if (p.course === "sl" && q.level !== "core")
            throw new Error("SL includes an AHL question.");
        if (q.diagramSvg && !safeDiagram(q.diagramSvg))
            throw new Error(`Unsafe diagram: ${q.id}.`);
        if (q.questionType === "multiple-choice") {
            if (q.section !== "1A" || q.marks !== 1 || q.parts.length || q.options?.map(o => o.label).join("") !== "ABCD" || !q.correctOption || q.markScheme.length !== 1 || q.markScheme[0].part !== "" || q.markScheme[0].steps.reduce((s, x) => s + Number(x.code.slice(1)), 0) !== 1)
                throw new Error(`Invalid MCQ: ${q.id}.`);
        }
        else {
            if (q.questionType !== (q.section === "1B" ? "data-based" : "structured") || q.section === "1A" || q.options || q.correctOption || !q.parts.length || q.parts.reduce((s, x) => s + x.marks, 0) !== q.marks || new Set(q.parts.map(x => x.label)).size !== q.parts.length || q.markScheme.length !== q.parts.length || new Set(q.markScheme.map(g => g.part)).size !== q.markScheme.length)
                throw new Error(`Invalid written question: ${q.id}.`);
            for (const part of q.parts) {
                const group = q.markScheme.find(g => g.part === part.label);
                if (!group || group.steps.reduce((s, x) => s + Number(x.code.slice(1)), 0) !== part.marks)
                    throw new Error(`Invalid marking points: ${q.id} (${part.label}).`);
            }
        }
    }
    if (p.paper === "1" && p.questions.filter(q => q.section === "1B").reduce((sum,q) => sum+q.marks,0) !== (p.course === "hl" ? 35 : 25))
        throw new Error("Experimental section has the wrong mark total.");
    return p;
}
const loaders = {
    "chemistry-hl-set-a-paper-1": () => import("@/content/ib/chemistry-mocks-2025/papers/chemistry-hl-set-a-paper-1.json"),
    "chemistry-hl-set-a-paper-2": () => import("@/content/ib/chemistry-mocks-2025/papers/chemistry-hl-set-a-paper-2.json"),
    "chemistry-hl-set-b-paper-1": () => import("@/content/ib/chemistry-mocks-2025/papers/chemistry-hl-set-b-paper-1.json"),
    "chemistry-hl-set-b-paper-2": () => import("@/content/ib/chemistry-mocks-2025/papers/chemistry-hl-set-b-paper-2.json"),
    "chemistry-sl-set-a-paper-1": () => import("@/content/ib/chemistry-mocks-2025/papers/chemistry-sl-set-a-paper-1.json"),
    "chemistry-sl-set-a-paper-2": () => import("@/content/ib/chemistry-mocks-2025/papers/chemistry-sl-set-a-paper-2.json"),
    "chemistry-sl-set-b-paper-1": () => import("@/content/ib/chemistry-mocks-2025/papers/chemistry-sl-set-b-paper-1.json"),
    "chemistry-sl-set-b-paper-2": () => import("@/content/ib/chemistry-mocks-2025/papers/chemistry-sl-set-b-paper-2.json"),
};
const cache = new Map<string, Promise<ChemistryMockPaper>>();
export async function getChemistryMockPaper(id: string, paper: MockPaper) {
    const meta = getChemistryPaperMeta(id, paper), loader = meta && loaders[meta.id as keyof typeof loaders];
    if (!meta || !loader)
        return undefined;
    if (!cache.has(meta.id))
        cache.set(meta.id, loader().then(m => validateChemistryMockPaper(m.default, meta)).catch(e => { cache.delete(meta.id); throw e; }));
    return cache.get(meta.id);
}
function promptQuestion(q: ChemistryQuestion): ChemistryPromptQuestion {
    return { id: q.id, section: q.section, number: q.number, title: q.title, marks: q.marks, stem: q.stem, parts: q.parts, questionType: q.questionType, ...(q.options ? { options: q.options } : {}), ...(q.diagramPng ? {diagramUrl: `data:image/png;base64,${q.diagramPng}`} : {}), ...(q.diagramSvg ? { diagramUrl: `data:image/svg+xml;base64,${Buffer.from(q.diagramSvg).toString("base64")}` } : {}), ...(q.diagramCaption ? { diagramCaption: q.diagramCaption } : {}) };
}
export function chemistryMockPrompt(paper: ChemistryMockPaper, meta: ChemistryPaperMeta): ChemistryMockPrompt { return { ...meta, questions: paper.questions.map(promptQuestion) }; }
export function chemistryMockSolutions(paper: ChemistryMockPaper): ChemistrySolution[] { return paper.questions.map(q => ({ ...promptQuestion(q), correctOption: q.correctOption, answerSummary: q.answerSummary, markScheme: q.markScheme })); }
