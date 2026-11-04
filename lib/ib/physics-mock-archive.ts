import "server-only";
import { getMockItems } from "./physics-mock-legacy";
import { cleanAnswers, validateSelfMarks, scoreMock, paperSpec, type MockPaper } from "./physics-mock-legacy-model";
export type LegacyPhysicsRow = {
    id: string;
    mock_id: string;
    paper: MockPaper;
    answers: unknown;
    elapsed_seconds: number;
    submitted_at: string;
    self_marks: unknown;
};
export function legacyReview(row: LegacyPhysicsRow) {
    const items = getMockItems(row.mock_id, row.paper), answers = cleanAnswers(items, row.answers), selfMarks = row.self_marks === null ? null : validateSelfMarks(items, row.self_marks);
    return { id: row.id, submittedAt: row.submitted_at, elapsed: row.elapsed_seconds, answers, selfMarks, score: scoreMock(items, answers, selfMarks), spec: paperSpec(row.mock_id.includes("-sl-") ? "sl" : "hl", row.paper), solutions: items.map(({ question: q, section, number }) => ({ id: q.id, label: `${section} Q${number}`, parts: q.parts, markScheme: q.markScheme, correctOption: q.correctOption })) };
}
