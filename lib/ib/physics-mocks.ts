import "server-only";
import { z } from "zod";
import { safeDiagram } from "./question";
import { getPhysicsPaperMeta, paperSpec, type MockPaper, type PhysicsMockPaper, type PhysicsPaperMeta, type PhysicsMockPrompt, type PhysicsQuestion, type PhysicsPromptQuestion, type PhysicsSolution } from "./physics-mock-model";
const text = z.string().min(1).max(50000);
const part = z.object({ label: z.string().min(1).max(24), prompt: text, marks: z.number().int().positive().max(10) });
const question = z.object({ id: z.string().regex(/^phy-(hl|sl)-[abc]-(1a|1b|2)-\d{2}$/), section: z.enum(["1A", "1B", "2"]), number: z.number().int().positive(), title: text, syllabusCode: z.string().regex(/^[A-E]\.[1-5]$/), syllabusRefs: z.array(text).min(1).max(30), level: z.enum(["core", "ahl"]), subtopic: text, difficulty: z.literal("hard"), questionType: z.enum(["multiple-choice", "data-based", "structured"]), marks: z.number().int().positive().max(10), stem: text, parts: z.array(part).max(20), options: z.array(z.object({ label: z.enum(["A", "B", "C", "D"]), text })).optional(), correctOption: z.enum(["A", "B", "C", "D"]).optional(), markScheme: z.array(z.object({ part: z.string().max(24), steps: z.array(z.object({ code: z.string().regex(/^[MARBC][1-9]\d?$/), text })).min(1) })).min(1), answerSummary: text, diagramSvg: z.string().max(300000).optional(), diagramCaption: z.string().max(2000).optional(), sourceAnchors: z.array(z.object({ document: text, page: z.number().int().positive(), question: text, focus: text })).min(1), changeNotes: text, cognitiveDemand: text, verification: z.object({ method: text, notes: text }) });
const schema = z.object({ id: text, mockId: text, course: z.enum(["sl", "hl"]), set: z.enum(["A", "B", "C"]), paper: z.enum(["1", "2"]), title: text, minutes: z.number().int().positive(), marks: z.number().int().positive(), calculator: z.literal(true), questions: z.array(question).min(1).max(42) });
export function validatePhysicsMockPaper(input: unknown, meta: PhysicsPaperMeta): PhysicsMockPaper {
    const p = schema.parse(input), spec = paperSpec(meta.course, meta.paper);
    for (const key of ["id", "mockId", "course", "set", "paper", "minutes", "marks", "calculator"] as const)
        if (p[key] !== meta[key])
            throw new Error(`Physics metadata differs: ${key}.`);
    if (p.minutes !== spec.minutes || p.marks !== spec.marks || p.questions.length !== meta.questionCount || p.questions.reduce((s, q) => s + q.marks, 0) !== p.marks)
        throw new Error("Physics paper specification differs.");
    if (new Set(p.questions.map(q => q.id)).size !== p.questions.length)
        throw new Error("Duplicate Physics question IDs.");
    const sections = p.paper === "1" ? ["1A", "1B"] : ["2"], counts = p.paper === "1" ? [p.course === "hl" ? 40 : 25, 2] : [p.course === "hl" ? 9 : 6];
    if (p.questions.some((q, i) => q.section !== (p.paper === "1" && i < counts[0] ? "1A" : p.paper === "1" ? "1B" : "2")))
        throw new Error("Questions must follow section order.");
    sections.forEach((section, index) => { const qs = p.questions.filter(q => q.section === section); if (qs.length !== counts[index] || qs.some((q, i) => q.number !== i + 1))
        throw new Error("Invalid Physics section numbering/count."); });
    for (const q of p.questions) {
        if (q.id !== `phy-${p.course}-${p.set.toLowerCase()}-${q.section.toLowerCase()}-${String(q.number).padStart(2, "0")}`)
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
            if (q.marks !== (q.section === "1B" || p.course === "hl" ? 10 : q.number < 5 ? 8 : 9))
                throw new Error(`Wrong question weighting: ${q.id}.`);
        }
    }
    for (const section of p.paper === "1" ? ["1A"] : ["2"])
        if (new Set(p.questions.filter(q => q.section === section).map(q => q.syllabusCode[0])).size !== 5)
            throw new Error("Paper must cover all five themes.");
    return p;
}
const loaders = {
    "physics-hl-set-a-paper-1": () => import("@/content/ib/physics-mocks-2026/papers/physics-hl-set-a-paper-1.json"),
    "physics-hl-set-a-paper-2": () => import("@/content/ib/physics-mocks-2026/papers/physics-hl-set-a-paper-2.json"),
    "physics-hl-set-b-paper-1": () => import("@/content/ib/physics-mocks-2026/papers/physics-hl-set-b-paper-1.json"),
    "physics-hl-set-b-paper-2": () => import("@/content/ib/physics-mocks-2026/papers/physics-hl-set-b-paper-2.json"),
    "physics-hl-set-c-paper-1": () => import("@/content/ib/physics-mocks-2026/papers/physics-hl-set-c-paper-1.json"),
    "physics-hl-set-c-paper-2": () => import("@/content/ib/physics-mocks-2026/papers/physics-hl-set-c-paper-2.json"),
    "physics-sl-set-a-paper-1": () => import("@/content/ib/physics-mocks-2026/papers/physics-sl-set-a-paper-1.json"),
    "physics-sl-set-a-paper-2": () => import("@/content/ib/physics-mocks-2026/papers/physics-sl-set-a-paper-2.json"),
    "physics-sl-set-b-paper-1": () => import("@/content/ib/physics-mocks-2026/papers/physics-sl-set-b-paper-1.json"),
    "physics-sl-set-b-paper-2": () => import("@/content/ib/physics-mocks-2026/papers/physics-sl-set-b-paper-2.json"),
};
const cache = new Map<string, Promise<PhysicsMockPaper>>();
export async function getPhysicsMockPaper(id: string, paper: MockPaper) {
    const meta = getPhysicsPaperMeta(id, paper), loader = meta && loaders[meta.id as keyof typeof loaders];
    if (!meta || !loader)
        return undefined;
    if (!cache.has(meta.id))
        cache.set(meta.id, loader().then(m => validatePhysicsMockPaper(m.default, meta)).catch(e => { cache.delete(meta.id); throw e; }));
    return cache.get(meta.id);
}
function promptQuestion(q: PhysicsQuestion): PhysicsPromptQuestion {
    return { id: q.id, section: q.section, number: q.number, title: q.title, marks: q.marks, stem: q.stem, parts: q.parts, questionType: q.questionType, ...(q.options ? { options: q.options } : {}), ...(q.diagramSvg ? { diagramUrl: `data:image/svg+xml;base64,${Buffer.from(q.diagramSvg).toString("base64")}` } : {}), ...(q.diagramCaption ? { diagramCaption: q.diagramCaption } : {}) };
}
export function physicsMockPrompt(paper: PhysicsMockPaper, meta: PhysicsPaperMeta): PhysicsMockPrompt { return { ...meta, questions: paper.questions.map(promptQuestion) }; }
export function physicsMockSolutions(paper: PhysicsMockPaper): PhysicsSolution[] { return paper.questions.map(q => ({ ...promptQuestion(q), correctOption: q.correctOption, answerSummary: q.answerSummary, markScheme: q.markScheme })); }
