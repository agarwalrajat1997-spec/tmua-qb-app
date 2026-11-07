import catalog from "@/content/ib/chemistry-mocks-2025/catalog.json";
export type MockPaper = "1" | "2";
export type ChemistryPart = {
    label: string;
    prompt: string;
    marks: number;
};
export type ChemistryPromptQuestion = {
    id: string;
    section: "1A" | "1B" | "2";
    number: number;
    title: string;
    marks: number;
    stem: string;
    parts: ChemistryPart[];
    questionType: "multiple-choice" | "data-based" | "structured";
    options?: {
        label: string;
        text: string;
    }[];
    diagramUrl?: string;
    diagramCaption?: string;
};
export type ChemistryQuestion = Omit<ChemistryPromptQuestion, "diagramUrl"> & {
    diagramSvg?: string;
    diagramPng?: string;
    correctOption?: string;
    answerSummary: string;
    syllabusCode: string;
    syllabusRefs: string[];
    subtopic: string;
    level: "core" | "ahl";
    difficulty: "hard";
    markScheme: {
        part: string;
        steps: {
            code: string;
            text: string;
        }[];
    }[];
    sourceAnchors: {
        document: string;
        page: number;
        question: string;
        focus: string;
    }[];
    changeNotes: string;
    cognitiveDemand: string;
    verification: {
        method: string;
        notes: string;
    };
};
export type ChemistrySolution = ChemistryPromptQuestion & Pick<ChemistryQuestion, "correctOption" | "answerSummary" | "markScheme">;
export type ChemistryPaperMeta = {
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
    sections: ("1A" | "1B" | "2")[];
};
export type ChemistryMock = {
    id: string;
    course: "sl" | "hl";
    set: "A" | "B";
    title: string;
    status: "published" | "draft";
    year: number;
    papers: ChemistryPaperMeta[];
};
export type ChemistryMockPaper = Pick<ChemistryPaperMeta, "id" | "mockId" | "course" | "set" | "paper" | "title" | "minutes" | "marks" | "calculator"> & {
    questions: ChemistryQuestion[];
};
export type ChemistryMockPrompt = ChemistryPaperMeta & {
    questions: ChemistryPromptQuestion[];
};
export const CHEMISTRY_MOCKS = catalog as ChemistryMock[];
export function getChemistryMock(id: string) { return CHEMISTRY_MOCKS.find(m => m.id === id && m.status === "published"); }
export function getChemistryPaperMeta(id: string, paper: MockPaper) { return getChemistryMock(id)?.papers.find(p => p.paper === paper && p.status === "published"); }
export const answerKey = (id: string, part = "") => part ? `${id}:${part}` : id;
export function paperSpec(course: string, paper: MockPaper) { return paper === "1" ? { minutes: course === "sl" ? 90 : 120, marks: course === "sl" ? 55 : 75, label: "Paper 1A + 1B" } : { minutes: course === "sl" ? 90 : 150, marks: course === "sl" ? 50 : 90, label: "Paper 2" }; }
export function chemistryPdfUrl(meta: ChemistryPaperMeta, origin?: string) { const path = `/ib-chemistry-mocks/${meta.id}-solutions.pdf`; if (meta.pdfUrl !== path)
    throw new Error("The solution PDF does not match this paper."); return origin ? new URL(path, origin).href : path; }
export type MockAnswers = Record<string, string>;
export type SelfMarks = Record<string, number>;
export function cleanAnswers(questions: ChemistryPromptQuestion[], input: unknown): MockAnswers {
    if (!input || typeof input !== "object" || Array.isArray(input))
        throw new Error("Invalid answers.");
    const source = input as Record<string, unknown>, output: MockAnswers = {};
    for (const q of questions)
        for (const key of q.questionType === "multiple-choice" ? [q.id] : q.parts.map(p => answerKey(q.id, p.label))) {
            const value = source[key] ?? "";
            if (typeof value !== "string" || value.length > 12000)
                throw new Error("Each response must be text of no more than 12,000 characters.");
            if (q.questionType === "multiple-choice" && !["", "A", "B", "C", "D"].includes(value))
                throw new Error("Invalid choice.");
            output[key] = value;
        }
    return output;
}
export function validateSelfMarks(questions: ChemistryPromptQuestion[], input: unknown): SelfMarks {
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
export function scoreMock(questions: ChemistryQuestion[], answers: MockAnswers, marks: SelfMarks | null) {
    const rows = questions.map(q => ({ id: q.id, label: `${q.section} Q${q.number}`, topic: q.subtopic, code: q.syllabusCode, max: q.marks, score: q.questionType === "multiple-choice" ? Number(answers[q.id] === q.correctOption) : marks ? q.parts.reduce((s, p) => s + marks[answerKey(q.id, p.label)], 0) : null, marking: q.questionType === "multiple-choice" ? "automatic" : "self-assessed", answer: q.questionType === "multiple-choice" ? answers[q.id] || "Unanswered" : "Written response", correct: q.correctOption }));
    const topics = [...new Set(rows.map(q => q.code))].map(code => { const g = rows.filter(q => q.code === code); return { code, title: g[0].topic, score: g.some(q => q.score === null) ? null : g.reduce((s, q) => s + (q.score ?? 0), 0), max: g.reduce((s, q) => s + q.max, 0) }; });
    const mcqs = rows.filter(q => q.marking === "automatic"), mcq = mcqs.reduce((s, q) => s + (q.score ?? 0), 0), mcqMaximum = mcqs.reduce((s, q) => s + q.max, 0), written = marks ? rows.filter(q => q.marking !== "automatic").reduce((s, q) => s + (q.score ?? 0), 0) : null;
    return { mcq, mcqMaximum, written, total: marks ? mcq + (written ?? 0) : null, maximum: rows.reduce((s, q) => s + q.max, 0), rows, topics };
}
export type MockReview = {
    id: string;
    submittedAt: string;
    name: string;
    elapsed: number;
    answers: MockAnswers;
    selfMarks: SelfMarks | null;
    score: ReturnType<typeof scoreMock>;
    solutions: ChemistrySolution[];
};
export type ChemistryMockDraft = {
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
export function restoreChemistryDraft(raw: string, paper: ChemistryMockPrompt): ChemistryMockDraft | null {
    try {
        const d = JSON.parse(raw), object = (v: unknown) => !!v && typeof v === "object" && !Array.isArray(v);
        if (d.version !== 2 || !["instructions", "running", "pending", "review"].includes(d.stage) || !Number.isInteger(d.index) || d.index < 0 || d.index >= paper.questions.length || typeof d.name !== "string" || d.name.length > 100 || !object(d.answers) || !object(d.flags) || !object(d.marks))
            return null;
        const keys = new Set(Object.keys(cleanAnswers(paper.questions, d.answers)));
        if (Object.keys(d.answers).some(key => !keys.has(key)))
            return null;
        const maxima = new Map(paper.questions.flatMap(q => q.parts.map(p => [answerKey(q.id, p.label), p.marks] as const)));
        if (Object.entries(d.marks).some(([k, v]) => !maxima.has(k) || typeof v !== "number" || !Number.isInteger(v) || v < 0 || v > maxima.get(k)!))
            return null;
        if (Object.entries(d.flags).some(([k, v]) => !paper.questions.some(q => q.id === k) || typeof v !== "boolean"))
            return null;
        if (d.stage !== "instructions" && (!/^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(d.attemptId) || !Number.isFinite(d.startedAt) || !Number.isFinite(d.deadline) || d.deadline - d.startedAt !== paper.minutes * 60000 || !Number.isInteger(d.elapsed) || d.elapsed < 0 || d.elapsed > paper.minutes * 60))
            return null;
        return d as ChemistryMockDraft;
    }
    catch {
        return null;
    }
}
export function reportPayload(meta: ChemistryPaperMeta, review: MockReview, email: string, origin: string) {
    const scored = review.score.total !== null, details = [meta.title, `${meta.minutes} minutes; ${meta.marks} marks. Time used: ${Math.floor(review.elapsed / 60)} min ${review.elapsed % 60} s.`, scored ? "MCQs are automatically marked. Written marks are self-assessed using the worked mark scheme." : "Your responses are saved. Written marking is pending: use the solution book and enter your self-assessment in the portal.", ...(review.score.mcqMaximum ? [`Multiple choice: ${review.score.mcq} / ${review.score.mcqMaximum} (automatically marked).`] : []), "Independent practice, not an official IB grade prediction. Internal assessment is not included.", ...review.score.rows.map(q => `${q.label}: ${q.score ?? "pending"} / ${q.max} (${q.marking})${q.correct ? `; chosen ${q.answer}; correct ${q.correct}` : ""}`), "", "Topic breakdown:", ...review.score.topics.map(t => `${t.code} ${t.title}: ${t.score ?? "pending"} / ${t.max}`), "", `Saved attempt: ${new URL(`/ib/chemistry-mocks/${meta.mockId}/${meta.paper}?course=${meta.course}&attempt=${review.id}`,origin).href}`, `Worked mark scheme: ${chemistryPdfUrl(meta, origin)}`].join("\n");
    return { name: review.name.trim() || "Student", to_email: email, student_email: email, test_title: meta.title, session: `IB Chemistry ${meta.course.toUpperCase()} · Set ${meta.set} · Paper ${meta.paper}`, attempt_id: review.id, timestamp: review.submittedAt, score: scored ? `${review.score.total} / ${review.score.maximum} (written marks self-assessed)` : `Submitted — written marking pending${review.score.mcqMaximum ? `; MCQ ${review.score.mcq} / ${review.score.mcqMaximum}` : ""}`, incorrect: scored ? review.score.rows.filter(q => q.score !== q.max).map(q => q.label).join(", ") || "None" : "Written marking pending", paper1: meta.paper === "1" ? details : "Paper 1 is a separate timed attempt.", paper2: meta.paper === "2" ? details : "Paper 2 is a separate timed attempt.", solution_link: chemistryPdfUrl(meta, origin), solution_note: "Open the worked mark scheme to check your responses." };
}
