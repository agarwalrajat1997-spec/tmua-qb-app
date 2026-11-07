import "server-only";
import { z } from "zod";
import { safeDiagram } from "./question";
import { getBiologyPaperMeta, paperSpec, type MockPaper, type BiologyMockPaper, type BiologyPaperMeta, type BiologyMockPrompt, type BiologyQuestion, type BiologyPromptQuestion, type BiologySolution } from "./biology-mock-model";
const text = z.string().min(1).max(50000);
const part = z.object({ label: z.string().min(1).max(24), prompt: text, marks: z.number().int().positive().max(10) });
const question = z.object({ id: z.string().regex(/^bio-(hl|sl)-[ab]-(1a|1b|2)-\d{2}$/), section: z.enum(["1A", "1B", "2"]), sectionB: z.literal(true).optional(), number: z.number().int().positive(), title: text, syllabusCode: z.string().regex(/^[ABCD][1-4]\.[1-4]$/), syllabusRefs: z.array(text).min(1).max(30), level: z.enum(["core", "ahl"]), subtopic: text, difficulty: z.literal("hard"), questionType: z.enum(["multiple-choice", "data-based", "structured"]), marks: z.number().int().positive().max(20), stem: text, parts: z.array(part).max(20), options: z.array(z.object({ label: z.enum(["A", "B", "C", "D"]), text })).optional(), correctOption: z.enum(["A", "B", "C", "D"]).optional(), markScheme: z.array(z.object({ part: z.string().max(24), steps: z.array(z.object({ code: z.string().regex(/^[MARBC][1-9]\d?$/), text })).min(1) })).min(1), answerSummary: text, diagramJpeg: z.string().startsWith("/9j/").regex(/^[A-Za-z0-9+/=]+$/).max(260000).optional(), diagramSvg: z.string().max(300000).optional(), diagramCaption: z.string().max(2000).optional(), sourceAnchors: z.array(z.object({ document: text, page: z.number().int().positive(), question: text, focus: text })).min(1), changeNotes: text, cognitiveDemand: text, verification: z.object({ method: text, notes: text }) });
const schema = z.object({ id: text, mockId: text, course: z.enum(["sl", "hl"]), set: z.enum(["A", "B"]), paper: z.enum(["1", "2"]), title: text, minutes: z.number().int().positive(), marks: z.number().int().positive(), calculator: z.literal(true), questions: z.array(question).min(1).max(44) });
export function validateBiologyMockPaper(input: unknown, meta: BiologyPaperMeta): BiologyMockPaper {
    const p = schema.parse(input), spec = paperSpec(meta.course, meta.paper);
    for (const key of ["id", "mockId", "course", "set", "paper", "minutes", "marks", "calculator"] as const)
        if (p[key] !== meta[key])
            throw new Error(`Biology metadata differs: ${key}.`);
    if (p.minutes !== spec.minutes || p.marks !== spec.marks || p.questions.length !== meta.questionCount || p.questions.reduce((s, q) => s + q.marks, 0) !== p.marks + (p.paper === "2" ? 16 : 0))
        throw new Error("Biology paper specification differs.");
    if (new Set(p.questions.map(q => q.id)).size !== p.questions.length)
        throw new Error("Duplicate Biology question IDs.");
    const sections = p.paper === "1" ? ["1A", "1B"] : ["2"], counts = p.paper === "1" ? [p.course === "hl" ? 40 : 30, 4] : [p.course === "hl" ? 7 : 6];
    if (p.questions.some((q, i) => q.section !== (p.paper === "1" && i < counts[0] ? "1A" : p.paper === "1" ? "1B" : "2")))
        throw new Error("Questions must follow section order.");
    sections.forEach((section, index) => { const qs = p.questions.filter(q => q.section === section); if (qs.length !== counts[index] || qs.some((q, i) => q.number !== i + 1))
        throw new Error("Invalid Biology section numbering/count."); });
    for (const q of p.questions) {
        if (q.id !== `bio-${p.course}-${p.set.toLowerCase()}-${q.section.toLowerCase()}-${String(q.number).padStart(2, "0")}`)
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
            if ((q.section === "1B" && q.questionType !== "data-based") || q.section === "1A" || q.options || q.correctOption || !q.parts.length || q.parts.reduce((s, x) => s + x.marks, 0) !== q.marks || new Set(q.parts.map(x => x.label)).size !== q.parts.length || q.markScheme.length !== q.parts.length || new Set(q.markScheme.map(g => g.part)).size !== q.markScheme.length)
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
    const optional = p.questions.filter(q => q.sectionB);
    if (p.paper === "1") {
        const themes = p.questions.filter(q => q.section === "1B").map(q => q.syllabusCode[0]);
        if (optional.length || new Set(themes).size !== 4) throw new Error("Paper 1B must cover all four themes.");
    } else if (optional.length !== (p.course === "hl" ? 3 : 2) ||
        optional.some(q => q.number <= 4 || q.marks !== 16 || q.parts.at(-1)?.label !== "quality" || q.parts.at(-1)?.marks !== 1)) {
        throw new Error("Invalid Paper 2 Section B allocation.");
    }
    return p;
}
const loaders = {
    "biology-hl-set-a-paper-1": () => import("@/content/ib/biology-mocks-2025/papers/biology-hl-set-a-paper-1.json"),
    "biology-hl-set-a-paper-2": () => import("@/content/ib/biology-mocks-2025/papers/biology-hl-set-a-paper-2.json"),
    "biology-hl-set-b-paper-1": () => import("@/content/ib/biology-mocks-2025/papers/biology-hl-set-b-paper-1.json"),
    "biology-hl-set-b-paper-2": () => import("@/content/ib/biology-mocks-2025/papers/biology-hl-set-b-paper-2.json"),
    "biology-sl-set-a-paper-1": () => import("@/content/ib/biology-mocks-2025/papers/biology-sl-set-a-paper-1.json"),
    "biology-sl-set-a-paper-2": () => import("@/content/ib/biology-mocks-2025/papers/biology-sl-set-a-paper-2.json"),
    "biology-sl-set-b-paper-1": () => import("@/content/ib/biology-mocks-2025/papers/biology-sl-set-b-paper-1.json"),
    "biology-sl-set-b-paper-2": () => import("@/content/ib/biology-mocks-2025/papers/biology-sl-set-b-paper-2.json"),
};
const cache = new Map<string, Promise<BiologyMockPaper>>();
export async function getBiologyMockPaper(id: string, paper: MockPaper) {
    const meta = getBiologyPaperMeta(id, paper), loader = meta && loaders[meta.id as keyof typeof loaders];
    if (!meta || !loader)
        return undefined;
    if (!cache.has(meta.id))
        cache.set(meta.id, loader().then(m => validateBiologyMockPaper(m.default, meta)).catch(e => { cache.delete(meta.id); throw e; }));
    return cache.get(meta.id);
}
function promptQuestion(q: BiologyQuestion): BiologyPromptQuestion {
    return { id: q.id, section: q.section, ...(q.sectionB ? {sectionB: true} : {}), number: q.number, title: q.title, marks: q.marks, stem: q.stem, parts: q.parts, questionType: q.questionType, ...(q.options ? { options: q.options } : {}), ...(q.diagramJpeg ? {diagramUrl: `data:image/jpeg;base64,${q.diagramJpeg}`} : {}), ...(q.diagramSvg ? { diagramUrl: `data:image/svg+xml;base64,${Buffer.from(q.diagramSvg).toString("base64")}` } : {}), ...(q.diagramCaption ? { diagramCaption: q.diagramCaption } : {}) };
}
export function biologyMockPrompt(paper: BiologyMockPaper, meta: BiologyPaperMeta): BiologyMockPrompt { return { ...meta, questions: paper.questions.map(promptQuestion) }; }
export function biologyMockSolutions(paper: BiologyMockPaper): BiologySolution[] { return paper.questions.map(q => ({ ...promptQuestion(q), correctOption: q.correctOption, answerSummary: q.answerSummary, markScheme: q.markScheme })); }
