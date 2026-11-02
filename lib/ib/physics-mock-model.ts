import catalog from "@/content/ib/physics-mocks.json";
import type { IbQuestion } from "./question";

export type PhysicsQuestion = Extract<IbQuestion, { subject: "physics-hl" }>;
export type MockPaper = "1" | "2";
export type PhysicsMock = typeof catalog[number];
export const PHYSICS_MOCKS = catalog;
export type MockItem = { question: PhysicsQuestion; section: "1A" | "1B" | "2"; number: number };
export type MockAnswers = Record<string, string>;
export type SelfMarks = Record<string, number>;
export const answerKey = (id: string, part = "") => part ? `${id}:${part}` : id;
export function paperSpec(course: string, paper: MockPaper) {
  return paper === "1"
    ? { minutes: course === "sl" ? 90 : 120, marks: course === "sl" ? 45 : 60, label: "Paper 1A + 1B" }
    : { minutes: course === "sl" ? 90 : 150, marks: course === "sl" ? 55 : 90, label: "Paper 2" };
}
export function cleanAnswers(items: MockItem[], input: unknown): MockAnswers {
  if (!input || typeof input !== "object" || Array.isArray(input)) throw new Error("Invalid answers.");
  const source = input as Record<string, unknown>;
  const output: MockAnswers = {};
  for (const { question: q } of items) {
    const keys = q.questionType === "multiple-choice" ? [q.id] : q.parts.map(p => answerKey(q.id, p.label));
    for (const key of keys) {
      const value = source[key] ?? "";
      if (typeof value !== "string" || value.length > 12000) throw new Error("An answer is too long or invalid.");
      if (q.questionType === "multiple-choice" && !["", "A", "B", "C", "D"].includes(value)) throw new Error("Invalid choice.");
      output[key] = value;
    }
  }
  return output;
}
export function validateSelfMarks(items: MockItem[], input: unknown): SelfMarks {
  if (!input || typeof input !== "object" || Array.isArray(input)) throw new Error("Enter a mark for every written part.");
  const source = input as Record<string, unknown>;
  const output: SelfMarks = {};
  for (const { question: q } of items) for (const part of q.parts) {
    const key = answerKey(q.id, part.label);
    const value = source[key];
    if (typeof value !== "number" || !Number.isInteger(value) || value < 0 || value > part.marks) {
      throw new Error(`Enter a whole-number mark from 0 to ${part.marks} for each written part.`);
    }
    output[key] = value;
  }
  return output;
}
export function scoreMock(items: MockItem[], answers: MockAnswers, marks: SelfMarks | null) {
  let mcq = 0, written = 0;
  const rows = items.map(({ question: q, section, number }) => {
    const automatic = q.questionType === "multiple-choice";
    const score = automatic ? Number(answers[q.id] === q.correctOption)
      : marks ? q.parts.reduce((sum, part) => sum + marks[answerKey(q.id, part.label)], 0) : null;
    if (automatic) mcq += score ?? 0; else written += score ?? 0;
    return { id: q.id, label: `${section} Q${number}`, topic: q.subtopic, code: q.syllabusCode,
      score, max: q.marks, marking: automatic ? "automatic" : "self-assessed",
      answer: automatic ? answers[q.id] || "Unanswered" : "Written response",
      correct: automatic ? q.correctOption : undefined };
  });
  const topics = [...new Set(rows.map(row => row.code))].map(code => {
    const group = rows.filter(row => row.code === code);
    return { code, title: group[0].topic, score: group.some(r => r.score === null) ? null : group.reduce((s,r) => s+(r.score ?? 0),0), max: group.reduce((s,r) => s+r.max,0) };
  });
  return { mcq, written: marks ? written : null, total: marks ? mcq + written : null,
    maximum: rows.reduce((s,r) => s+r.max,0), rows, topics };
}
export type MockScore = ReturnType<typeof scoreMock>;
export type MockReview = {
  id: string; submittedAt: string; elapsed: number; answers: MockAnswers; selfMarks: SelfMarks | null;
  score: MockScore;
  solutions: { id: string; label: string; parts: PhysicsQuestion["parts"]; markScheme: PhysicsQuestion["markScheme"]; correctOption?: string; diagram?: string; diagramCaption?: string }[];
};

export function reportPayload(mock: PhysicsMock, paper: MockPaper, review: MockReview, email: string, name: string, origin: string) {
  const spec = paperSpec(mock.course, paper);
  const analysis = [
    "Written marks are self-assessed using the worked mark scheme. MCQs are automatically marked.",
    "This is independent practice, not an official IB grade prediction. Internal assessment is not included.",
    `Time used: ${Math.round(review.elapsed / 60)} / ${spec.minutes} minutes.`,
    ...review.score.rows.map(r => `${r.label}: ${r.score ?? "pending"}/${r.max} (${r.marking})${r.correct ? `; chosen ${r.answer}; correct ${r.correct}` : ""}`),
    "", "Topic breakdown:", ...review.score.topics.map(t => `${t.code} ${t.title}: ${t.score ?? "pending"}/${t.max}`),
  ].join("\n");
  return { name: name.trim() || "Student", test_title: `${mock.title} · ${spec.label}`,
    to_email: email, student_email: email, session: "IB Physics mock series · self-assessed written marks",
    score: `${review.score.total} / ${review.score.maximum}`, timestamp: new Date(review.submittedAt).toISOString(),
    incorrect: review.score.rows.filter(r => r.score !== r.max).map(r => r.label).join(", ") || "None",
    paper1: paper === "1" ? analysis : "Paper 1 was not included in this attempt.",
    paper2: paper === "2" ? analysis : "Paper 2 is a separate attempt.",
    solution_link: `${origin}/ib/mocks/${mock.id}/${paper}?attempt=${review.id}` };
}
