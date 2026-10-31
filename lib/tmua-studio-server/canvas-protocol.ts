// Adapted from zicojiao/ai-math-tutor. See THIRD_PARTY_NOTICES.md.
import { z } from 'zod/v3';

const CoordinateSchema = z.number().finite();

export const PointSchema = z.object({
  x: CoordinateSchema,
  y: CoordinateSchema,
});

export const CanvasShapeSchema = z.object({
  id: z.string().min(1),
  type: z.string().min(1),
  x: CoordinateSchema,
  y: CoordinateSchema,
  w: z.number().finite().optional(),
  h: z.number().finite().optional(),
  text: z.string().optional(),
  latex: z.string().optional(),
  owner: z.enum(['student', 'ai', 'system']).default('student'),
});

export const CanvasEventSchema = z.object({
  type: z.enum(['shape_created', 'shape_updated', 'shape_deleted', 'selection_changed']),
  shapeId: z.string().optional(),
  at: z.string().datetime(),
});

export const BoardStepSchema = z.object({
  id: z.string().min(1),
  shapeId: z.string().min(1),
  role: z.enum(['problem', 'student_step', 'scratch']),
  index: z.number().int().positive(),
  text: z.string().max(240).optional(),
  x: CoordinateSchema,
  y: CoordinateSchema,
  w: z.number().finite().positive(),
  h: z.number().finite().positive(),
});

export const BoardUnderstandingSchema = z.object({
  activeStepId: z.string().min(1).optional(),
  steps: z.array(BoardStepSchema).max(80),
});

export const TutorTurnStateSchema = z.object({
  phase: z.enum(['observing', 'waiting_for_student', 'student_responded']),
  targetShapeId: z.string().optional(),
  question: z.string().max(300).optional(),
  waitingSince: z.string().datetime().optional(),
  lastStudentEventAt: z.string().datetime().optional(),
});

export const CanvasContextSchema = z.object({
  roomName: z.string().min(1),
  viewport: z.object({
    x: CoordinateSchema,
    y: CoordinateSchema,
    w: z.number().finite().positive(),
    h: z.number().finite().positive(),
    zoom: z.number().finite().positive(),
  }),
  selectedShapeIds: z.array(z.string()),
  recentEvents: z.array(CanvasEventSchema).max(80),
  shapes: z.array(CanvasShapeSchema).max(400),
  board: BoardUnderstandingSchema.optional(),
  tutorTurn: TutorTurnStateSchema.optional(),
  screenshotDataUrl: z.string().startsWith('data:image/').optional(),
});

const WriteTextActionSchema = z.object({
  type: z.literal('write_text'),
  text: z.string().min(1).max(600),
  x: CoordinateSchema,
  y: CoordinateSchema,
  targetShapeId: z.string().optional(),
  color: z.enum(['ink', 'red', 'green', 'blue']).default('ink').optional(),
});

const WriteFormulaActionSchema = z.object({
  type: z.literal('write_formula'),
  latex: z.string().min(1).max(500),
  x: CoordinateSchema,
  y: CoordinateSchema,
  targetShapeId: z.string().optional(),
  color: z.enum(['ink', 'red', 'green', 'blue']).default('ink').optional(),
});

const HintCardActionSchema = z.object({
  type: z.literal('hint_card'),
  title: z.string().min(1).max(80),
  body: z.string().min(1).max(360),
  equation: z.string().max(300).optional(),
  x: CoordinateSchema.optional(),
  y: CoordinateSchema.optional(),
  targetShapeId: z.string().optional(),
  color: z.enum(['blue', 'green', 'red']).default('blue').optional(),
});

const HighlightActionSchema = z.object({
  type: z.literal('highlight'),
  x: CoordinateSchema,
  y: CoordinateSchema,
  w: z.number().finite().positive(),
  h: z.number().finite().positive(),
  color: z.enum(['yellow', 'red', 'green']),
  label: z.string().max(160).optional(),
});

const DrawArrowActionSchema = z.object({
  type: z.literal('draw_arrow'),
  from: PointSchema,
  to: PointSchema,
  label: z.string().max(160).optional(),
});

const MarkWrongActionSchema = z.object({
  type: z.literal('mark_wrong'),
  x: CoordinateSchema,
  y: CoordinateSchema,
  targetShapeId: z.string().optional(),
  reason: z.string().min(1).max(300),
});

const MarkCorrectActionSchema = z.object({
  type: z.literal('mark_correct'),
  x: CoordinateSchema,
  y: CoordinateSchema,
  targetShapeId: z.string().optional(),
  note: z.string().max(180).optional(),
});

const CorrectStepActionSchema = z.object({
  type: z.literal('correct_step'),
  targetShapeId: z.string().min(1),
  reason: z.string().min(1).max(300),
  latex: z.string().min(1).max(500),
});

const AskStudentActionSchema = z.object({
  type: z.literal('ask_student'),
  question: z.string().min(1).max(300),
  targetShapeId: z.string().optional(),
  x: CoordinateSchema.optional(),
  y: CoordinateSchema.optional(),
});

const ClearAiAnnotationsActionSchema = z.object({
  type: z.literal('clear_ai_annotations'),
});

export const TutorCanvasActionSchema = z.discriminatedUnion('type', [
  WriteTextActionSchema,
  WriteFormulaActionSchema,
  HintCardActionSchema,
  HighlightActionSchema,
  DrawArrowActionSchema,
  MarkWrongActionSchema,
  MarkCorrectActionSchema,
  CorrectStepActionSchema,
  AskStudentActionSchema,
  ClearAiAnnotationsActionSchema,
]);

export const TutorCanvasCommandSchema = z.object({
  narration: z.string().max(1200).optional(),
  actions: z.array(TutorCanvasActionSchema).min(1).max(24),
});

export type Point = z.infer<typeof PointSchema>;
export type CanvasEvent = z.infer<typeof CanvasEventSchema>;
export type CanvasShape = z.infer<typeof CanvasShapeSchema>;
export type BoardStep = z.infer<typeof BoardStepSchema>;
export type BoardUnderstanding = z.infer<typeof BoardUnderstandingSchema>;
export type TutorTurnState = z.infer<typeof TutorTurnStateSchema>;
export type CanvasContext = z.infer<typeof CanvasContextSchema>;
export type TutorCanvasAction = z.infer<typeof TutorCanvasActionSchema>;
export type TutorCanvasCommand = z.infer<typeof TutorCanvasCommandSchema>;

const MIN_COORD = 0;
const MAX_COORD = 4000;

function clampCoordinate(value: number) {
  return Math.max(MIN_COORD, Math.min(MAX_COORD, value));
}

function clampPoint(point: Point): Point {
  return {
    x: clampCoordinate(point.x),
    y: clampCoordinate(point.y),
  };
}

function normalizeAction(action: TutorCanvasAction): TutorCanvasAction {
  switch (action.type) {
    case 'write_text':
    case 'write_formula':
    case 'mark_wrong':
    case 'mark_correct':
      return {
        ...action,
        x: clampCoordinate(action.x),
        y: clampCoordinate(action.y),
      };
    case 'hint_card':
      return {
        ...action,
        ...(typeof action.x === 'number' ? { x: clampCoordinate(action.x) } : {}),
        ...(typeof action.y === 'number' ? { y: clampCoordinate(action.y) } : {}),
      };
    case 'highlight':
      return {
        ...action,
        x: clampCoordinate(action.x),
        y: clampCoordinate(action.y),
        w: Math.min(MAX_COORD, action.w),
        h: Math.min(MAX_COORD, action.h),
      };
    case 'draw_arrow':
      return {
        ...action,
        from: clampPoint(action.from),
        to: clampPoint(action.to),
      };
    case 'correct_step':
      return action;
    case 'ask_student':
      return {
        ...action,
        ...(typeof action.x === 'number' ? { x: clampCoordinate(action.x) } : {}),
        ...(typeof action.y === 'number' ? { y: clampCoordinate(action.y) } : {}),
      };
    case 'clear_ai_annotations':
      return action;
  }
}

export function normalizeTutorCommand(input: unknown): TutorCanvasCommand {
  const command = TutorCanvasCommandSchema.parse(input);
  const narration = command.narration?.trim();
  return {
    ...(narration ? { narration } : {}),
    actions: command.actions.map(normalizeAction),
  };
}
