import catalog from "@/content/ib/economics-mocks-2022/catalog.json";
export type MockPaper = "1" | "2" | "3";
export type EconomicsPart = {label: string; marks: number; prompt: string};
export type EconomicsPromptQuestion = {id: string; section: MockPaper; number: number; title: string; optional: boolean; stimulusUrl?: string; stimulusCaption?: string; marks: number; stem: string; parts: EconomicsPart[]};
export type EconomicsSolution = EconomicsPromptQuestion & {
    solutionUrl: string; background?: {label: string; url: string};
    markScheme: {part: string; steps: {code: string; text: string}[]}[];
};
export type EconomicsQuestion = Omit<EconomicsSolution, "solutionUrl"> & {syllabusCode: string; subtopic: string; solutionSvg: string; stimulusSvg?: string};
export type EconomicsPaperMeta = {
    id: string;
    mockId: string;
    course: "sl" | "hl";
    set: "A" | "B";
    paper: MockPaper;
    title: string;
    minutes: number;
    marks: number;
    calculator: boolean;
    pdfUrl: string;
    questionBooklets: {label: string; url: string}[];
    status: "published" | "draft";
    year: number;
    questionCount: number;
};
export type EconomicsMock = {
    id: string;
    course: "sl" | "hl";
    set: "A" | "B";
    title: string;
    status: "published" | "draft";
    year: number;
    papers: EconomicsPaperMeta[];
};
export type EconomicsMockPaper = Pick<EconomicsPaperMeta, "id" | "mockId" | "course" | "set" | "paper" | "title" | "minutes" | "marks" | "calculator"> & {
    questions: EconomicsQuestion[];
};
export type EconomicsMockPrompt = EconomicsPaperMeta & {
    questions: EconomicsPromptQuestion[];
};
export const ECONOMICS_MOCKS = catalog as EconomicsMock[];
export function getEconomicsMock(id: string) { return ECONOMICS_MOCKS.find(m => m.id === id && m.status === "published"); }
export function getEconomicsPaperMeta(id: string, paper: MockPaper) { return getEconomicsMock(id)?.papers.find(p => p.paper === paper && p.status === "published"); }
export const answerKey = (id: string, part = "") => part ? `${id}:${part}` : id;
export function paperSpec(paper: MockPaper) {
    return {minutes: paper === "1" ? 75 : 105, marks: paper === "1" ? 25 : paper === "2" ? 40 : 60, calculator: paper !== "1"};
}
export function economicsPdfUrl(meta: EconomicsPaperMeta, origin?: string) { const path = `/ib-economics-mocks/${meta.id}-solutions.pdf`; if (meta.pdfUrl !== path)
    throw new Error("The solution PDF does not match this paper."); return origin ? new URL(path, origin).href : path; }
export type MockAnswers = Record<string, string>;
export type SelfMarks = Record<string, number>;

export function selectedQuestions<T extends Pick<EconomicsPromptQuestion, "id" | "optional">>(
    questions: T[], selection: unknown
): T[] {
    const options = questions.filter(question => question.optional);
    if (!options.length) {
        if (selection !== undefined) throw new Error("This paper has no optional section.");
        return questions;
    }
    const count = 1;
    const ids = selection === undefined
        ? options.slice(0, count).map(q => q.id)
        : typeof selection === "string" ? selection.split(",") : [];
    if (ids.length !== count || new Set(ids).size !== count || ids.some(id => !options.some(q => q.id === id)))
        throw new Error("Choose one complete question for this paper.");
    return questions.filter(q => !q.optional || ids.includes(q.id));
}
export function sectionTitle(q: Pick<EconomicsPromptQuestion, "section" | "optional">) {
    return "Paper " + q.section;
}
export function cleanAnswers(questions: EconomicsPromptQuestion[], input: unknown): MockAnswers {
    if (!input || typeof input !== "object" || Array.isArray(input))
        throw new Error("Invalid answers.");
    const source = input as Record<string, unknown>, output: MockAnswers = {};
    const included = selectedQuestions(questions, source.__choice);
    if (questions.some(q => q.optional))
        output.__choice = included.filter(q => q.optional).map(q => q.id).join(",");
    for (const q of included)
        for (const key of q.parts.map(p => answerKey(q.id, p.label))) {
            const value = source[key] ?? "";
            if (typeof value !== "string" || value.length > 12000)
                throw new Error("Each response must be text of no more than 12,000 characters.");
            output[key] = value;
        }
    return output;
}
export function validateSelfMarks(questions: EconomicsPromptQuestion[], input: unknown): SelfMarks {
    if (!input || typeof input !== "object" || Array.isArray(input))
        throw new Error("Enter a mark for every written part.");
    const source = input as Record<string, unknown>, output: SelfMarks = {};
    for (const q of questions)
        for (const p of q.parts) {
            const key = answerKey(q.id, p.label), value = source[key];
            if (typeof value !== "number" || !Number.isInteger(value) || value < 0 || value > p.marks)
                throw new Error(`Enter a whole-number mark from 0 to ${p.marks} for each written part.`);
            output[key] = value;
        }
    return output;
}
export function scoreMock(questions: EconomicsQuestion[], answers: MockAnswers, marks: SelfMarks | null) {
    const rows = questions.map(q => ({
        id: q.id, label: "Paper " + q.section + " Q" + q.number, topic: q.subtopic,
        code: q.syllabusCode, max: q.marks, marking: "self-assessed",
        score: marks ? q.parts.reduce((sum, part) => sum + marks[answerKey(q.id, part.label)], 0) : null
    }));
    const maximum = rows.reduce((sum, row) => sum + row.max, 0);
    const total = marks ? rows.reduce((sum, row) => sum + (row.score ?? 0), 0) : null;
    return {rows, maximum, total, written: total, topics: rows.map(row => ({code:row.code,title:row.topic,score:row.score,max:row.max}))};

}
export type MockReview = {
    id: string;
    submittedAt: string;
    name: string;
    elapsed: number;
    answers: MockAnswers;
    selfMarks: SelfMarks | null;
    score: ReturnType<typeof scoreMock>;
    solutions: EconomicsSolution[];
};
export type EconomicsMockDraft = {
    version: 2;
    attemptId: string;
    name: string;
    startedAt: number;
    deadline: number;
    elapsed: number;
    stage: "instructions" | "running" | "pending" | "review";
    index: number;
    answers: MockAnswers;
    flags: Record<string, boolean>;
    marks: SelfMarks;
};
export function secondsRemaining(deadline: number, now: number, maximum: number) { return Math.min(maximum, Math.max(0, Math.ceil((deadline - now) / 1000))); }
export function restoreEconomicsDraft(raw: string, paper: EconomicsMockPrompt): EconomicsMockDraft | null {
    try {
        const d = JSON.parse(raw), object = (v: unknown) => !!v && typeof v === "object" && !Array.isArray(v);
        if (d.version !== 2 || !["instructions", "running", "pending", "review"].includes(d.stage) || !Number.isInteger(d.index) || d.index < 0 || d.index >= paper.questions.length || typeof d.name !== "string" || d.name.length > 100 || !object(d.answers) || !object(d.flags) || !object(d.marks))
            return null;
        const included = selectedQuestions(paper.questions, d.answers.__choice);
        if (d.index >= included.length) return null;
        const keys = new Set(paper.questions.flatMap(q => q.parts.map(part => answerKey(q.id, part.label))));
        if (paper.questions.some(q => q.optional)) keys.add("__choice");
        cleanAnswers(paper.questions, d.answers);
        if (Object.keys(d.answers).some(key => !keys.has(key)))
            return null;
        const maxima = new Map(paper.questions.flatMap(q => q.parts.map(p => [answerKey(q.id, p.label), p.marks] as const)));
        if (Object.entries(d.marks).some(([k, v]) => !maxima.has(k) || typeof v !== "number" || !Number.isInteger(v) || v < 0 || v > maxima.get(k)!))
            return null;
        if (Object.entries(d.flags).some(([k, v]) => !paper.questions.some(q => q.id === k) || typeof v !== "boolean"))
            return null;
        if (d.stage !== "instructions" && (!/^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(d.attemptId) || !Number.isFinite(d.startedAt) || !Number.isFinite(d.deadline) || d.deadline - d.startedAt !== paper.minutes * 60000 || !Number.isInteger(d.elapsed) || d.elapsed < 0 || d.elapsed > paper.minutes * 60))
            return null;
        return d as EconomicsMockDraft;
    }
    catch {
        return null;
    }
}
export function reportPayload(meta: EconomicsPaperMeta, review: MockReview, email: string, origin: string) {
    const scored = review.score.total !== null;
    const score = scored ? String(review.score.total) + " / " + meta.marks + " (self-assessed)" : "Written marking pending";
    const saved = new URL("/ib/economics-mocks/" + meta.mockId + "/" + meta.paper + "?attempt=" + review.id, origin).href;
    const details = [meta.title, score, "Time used: " + Math.floor(review.elapsed / 60) + " min " + review.elapsed % 60 + " s.",
        ...review.score.rows.map(row => row.label + " · " + row.topic + ": " + (row.score ?? "pending") + " / " + row.max),
        "Saved attempt: " + saved, "Worked mark scheme: " + economicsPdfUrl(meta, origin)].join("\n");
    return {name: review.name.trim() || "Student", to_email: email, student_email: email, test_title: meta.title, session: meta.title,
        attempt_id: review.id, timestamp: review.submittedAt, score, incorrect: scored ? review.score.rows.filter(row=>row.score!==row.max).map(row=>row.label).join(", ") || "None" : "Written marking pending",
        paper1: meta.paper === "1" ? details : "See the report for Paper " + meta.paper + " below.", paper2: meta.paper === "1" ? "" : details,
        paper3: meta.paper === "3" ? details : "", solution_link: economicsPdfUrl(meta, origin), solution_note: "Use the worked scheme and best-fit markbands to assess your answers."};
}
