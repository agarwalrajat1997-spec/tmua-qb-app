export type Exam = "tmua" | "esat";
export type Question = {
  guide_path?: string;
  bank_qid?: string;
  content_version?: string;
  source_sha256?: string;
  app_question_id?: string;
  audited?: boolean;
  followup_only?: boolean;
  skill_search?: string;
  exam: Exam;
  qid: string;
  paper: string;
  topic: string;
  subtopic: string;
  difficulty: number;
  prompt_html: string;
  options: { label: string; html: string }[];
  answer_verified: boolean;
  updated_at: string;
  answer?: string;
  solution_html?: string;
};
export type Point = [number, number, number];
export type Rect = { x: number; y: number; w: number; h: number };
export type ReviewRegion = {
  id: string;
  kind: "ink" | "typed";
  box: Rect;
  text?: string;
};
export type WorkingGroup = { id: string; regionIds: string[] };
export type FeedbackGroup = WorkingGroup & {
  status: FeedbackLine["status"];
  good: string;
  explanation: string;
};
export type StoredSolution = {
  qid: string;
  answer: string;
  solutionHtml: string;
  shortcuts: { title: string; html: string }[];
  updatedAt?: string;
};
export type InkGeometry = [number, number][][][];
export type Stroke = {
  id: string;
  points: Point[];
  color: string;
  size: number;
  tool: "pen" | "highlighter";
  // Legacy strokes keep their original rendering. Erased ink stores its exact outline.
  renderVersion?: 2;
  outline?: InkGeometry;
};
export type Photo = {
  id: string;
  data: string;
  rotation: number;
  x: number;
  y: number;
  w: number;
  h: number;
};
export type Board = {
  revision: number;
  strokes: Stroke[];
  photo: Photo | null;
  note: string;
};
export type FeedbackLine = {
  line: number;
  transcription: string;
  status: "correct" | "incorrect" | "uncertain" | "not_checked";
  explanation: string;
  hint: string;
  box: { x: number; y: number; w: number; h: number } | null;
  regionId?: string | null;
};
export type Feedback = {
  reviewId?: string;
  groups?: FeedbackGroup[];
  answer?: {
    regionId: string | null;
    status: FeedbackLine["status"];
    text: string;
  } | null;
  visual?: import("./tutor-visual").TutorVisual | null;
  coverage?: "complete" | "partial" | "unreadable";
  answerLine?: number | null;
  alternative?: { line: number; text: string } | null;
  source?: {
    hash: string;
    capture: Rect;
    regions: ReviewRegion[];
    groups?: WorkingGroup[];
  };
  model?: string;
  cached?: boolean;
  timing?: { providerMs: number };
  serviceTier?: string;
  usage?: {
    inputTokens: number;
    outputTokens: number;
    reasoningTokens: number;
    cachedInputTokens: number;
    totalTokens: number;
  } | null;
  revision: number;
  summary: string;
  lines: FeedbackLine[];
  firstErrorLine: number | null;
  nextStep: string;
};
export type Progress = {
  contentVersion?: string;
  solutionViewed?: boolean;
  reviewedAt?: string;
  selected?: string;
  submitted?: boolean;
  correct?: boolean;
  bookmarked?: boolean;
  checkedAt?: string;
};
export type MockAttempt = {
  id: string;
  exam: Exam;
  qids: string[];
  contentVersions?: Record<string, string | null>;
  deadline: number;
  answers: Record<string, string>;
  flags: string[];
  submittedAt?: number;
};
export const emptyBoard = (): Board => ({
  revision: 0,
  strokes: [],
  photo: null,
  note: "",
});
export const cleanTopic = (topic: string) =>
  topic.replace(/^\d+[_\s-]*/, "").replaceAll("_", " ");
export const questionKey = (
  q: Pick<Question, "exam" | "qid" | "content_version">,
) => `${q.exam}:${q.qid}${q.content_version ? `@${q.content_version}` : ""}`;
