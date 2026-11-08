import catalog from "@/content/ib/psychology-mocks-2027/catalog.json";
export type MockPaper = "1" | "2" | "3";
export type PsychologyPart = {label: string; marks: number; prompt: string};
export type PsychologyPromptQuestion = {id: string; section: MockPaper; division: string; number: number; title: string; optional: boolean; stimulusUrl?: string; stimulusCaption?: string; marks: number; stem: string; parts: PsychologyPart[]};
export type PsychologySolution = PsychologyPromptQuestion & {
    markScheme: {part: string; steps: {code: string; text: string}[]}[];
};
export type PsychologyQuestion = PsychologySolution & {syllabusCode: string; subtopic: string; stimulusSvg?: string};
export type PsychologyPaperMeta = {
    id: string;
    mockId: string;
    course: "sl" | "hl";
    set: "A" | "B";
    paper: MockPaper;
    title: string;
    minutes: number;
    marks: number;
    pdfUrl: string;
    questionBooklets: {label: string; url: string}[];
    status: "published" | "draft";
    year: number;
    questionCount: number;
};
export type PsychologyMock = {
    id: string;
    course: "sl" | "hl";
    set: "A" | "B";
    title: string;
    status: "published" | "draft";
    year: number;
    papers: PsychologyPaperMeta[];
};
export type PsychologyResource = {number:number;title:string;text:string;caption?:string};
export type PsychologyMockPaper = Pick<PsychologyPaperMeta, "id" | "mockId" | "course" | "set" | "paper" | "title" | "minutes" | "marks"> & {
    questions: PsychologyQuestion[];
    resources:(PsychologyResource & {svg?:string})[];
};
export type PsychologyMockPrompt = PsychologyPaperMeta & {
    questions: PsychologyPromptQuestion[];
    resources:(PsychologyResource & {figureUrl?:string})[];
};
export const PSYCHOLOGY_MOCKS = catalog as PsychologyMock[];
export function getPsychologyMock(id: string) { return PSYCHOLOGY_MOCKS.find(m => m.id === id && m.status === "published"); }
export function getPsychologyPaperMeta(id: string, paper: MockPaper) { return getPsychologyMock(id)?.papers.find(p => p.paper === paper && p.status === "published"); }
export const answerKey = (id: string, part = "") => part ? `${id}:${part}` : id;
export function paperSpec(paper: MockPaper) {
    return {minutes: paper === "3" ? 105 : 90, marks: paper === "3" ? 30 : 35};
}
export function psychologyPdfUrl(meta: PsychologyPaperMeta, origin?: string) { const path = `/ib-psychology-mocks/${meta.id}-solutions.pdf`; if (meta.pdfUrl !== path)
    throw new Error("The solution PDF does not match this paper."); return origin ? new URL(path, origin).href : path; }
export type MockAnswers = Record<string, string>;
export type SelfMarks = Record<string, number>;

export function selectedQuestions<T extends Pick<PsychologyPromptQuestion, "id" | "optional">>(
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
        throw new Error("Choose one Section C essay.");
    return questions.filter(q => !q.optional || ids.includes(q.id));
}
export function sectionTitle(q: Pick<PsychologyPromptQuestion, "section" | "division">) {
    return q.division === "R" ? "Paper 3" : "Section " + q.division;
}
export function cleanAnswers(questions: PsychologyPromptQuestion[], input: unknown): MockAnswers {
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
export function validateSelfMarks(questions: PsychologyPromptQuestion[], input: unknown): SelfMarks {
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
export function scoreMock(questions: PsychologyQuestion[], answers: MockAnswers, marks: SelfMarks | null) {
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
    solutions: PsychologySolution[];
};
export type PsychologyMockDraft = {
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
export function restorePsychologyDraft(raw: string, paper: PsychologyMockPrompt): PsychologyMockDraft | null {
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
        return d as PsychologyMockDraft;
    }
    catch {
        return null;
    }
}
export function reportPayload(meta: PsychologyPaperMeta, review: MockReview, email: string, origin: string) {
    const scored = review.score.total !== null;
    const score = scored ? String(review.score.total) + " / " + meta.marks + " (self-assessed)" : "Written marking pending";
    const saved = new URL("/ib/psychology-mocks/" + meta.mockId + "/" + meta.paper + "?attempt=" + review.id, origin).href;
    const details = [meta.title, score, "Time used: " + Math.floor(review.elapsed / 60) + " min " + review.elapsed % 60 + " s.",
        ...review.score.rows.map(row => row.label + " · " + row.topic + ": " + (row.score ?? "pending") + " / " + row.max),
        "Saved attempt: " + saved, "Worked mark scheme: " + psychologyPdfUrl(meta, origin)].join("\n");
    return {name: review.name.trim() || "Student", to_email: email, student_email: email, test_title: meta.title, session: meta.title,
        attempt_id: review.id, timestamp: review.submittedAt, score, incorrect: scored ? review.score.rows.filter(row=>row.score!==row.max).map(row=>row.label).join(", ") || "None" : "Written marking pending",
        paper1: meta.paper === "1" ? details : "See the report for Paper " + meta.paper + " below.", paper2: meta.paper === "1" ? "" : details,
        paper3: meta.paper === "3" ? details : "", solution_link: psychologyPdfUrl(meta, origin), solution_note: "Use the worked scheme and best-fit markbands to assess your answers."};
}
