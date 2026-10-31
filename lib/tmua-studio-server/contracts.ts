import { z } from "zod/v3";
import { TutorVisualSchema } from "./tutor-visual";
import { BoardUnderstandingSchema } from "./canvas-protocol";
export const ExamSchema = z.enum(["tmua", "esat"]);
export const RegionSchema = z
  .object({
    id: z.string().regex(/^(ink|typed)-[1-9]\d*$/),
    kind: z.enum(["ink", "typed"]),
    box: z
      .object({
        x: z.number().min(0).max(1000),
        y: z.number().min(0).max(1000),
        w: z.number().positive().max(1000),
        h: z.number().positive().max(1000),
      })
      .strict()
      .refine((b) => b.x + b.w <= 1000.000001 && b.y + b.h <= 1000.000001),
    text: z.string().max(5000).optional(),
  })
  .strict();
export const ReviewRequest = z
  .object({
    exam: ExamSchema,
    qid: z.string().min(1).max(160),
    contentVersion: z.string().min(1).max(200).optional(),
    requestId: z.string().uuid(),
    clarifications: z
      .array(
        z
          .object({
            regionIds: z.array(z.string()).max(80),
            text: z.string().trim().min(1).max(700),
          })
          .strict(),
      )
      .max(6)
      .optional(),
    revision: z.number().int().nonnegative(),
    image: z.string().max(4_500_000).optional(),
    note: z.string().max(5000),
    structure: BoardUnderstandingSchema,
    groups: z
      .array(
        z
          .object({
            id: z.string().regex(/^box-[1-6]$/),
            regionIds: z.array(z.string()).min(1).max(80),
          })
          .strict(),
      )
      .max(6)
      .optional(),
    regions: z
      .array(RegionSchema)
      .max(80)
      .optional()
      .refine(
        (rs) => !rs || new Set(rs.map((r) => r.id)).size === rs.length,
        "Duplicate regions",
      ),
  })
  .strict()
  .superRefine((input, ctx) => {
    const regionIds = new Set(input.regions?.map((r) => r.id) ?? []);
    if (
      input.clarifications?.some((c) =>
        c.regionIds.some((id) => !regionIds.has(id)),
      )
    )
      ctx.addIssue({
        code: "custom",
        message: "Clarification region does not exist",
      });
    if (!input.groups) return;
    const known = new Set(input.regions?.map((r) => r.id) ?? []),
      ids = input.groups.flatMap((g) => g.regionIds);
    if (
      new Set(input.groups.map((g) => g.id)).size !== input.groups.length ||
      new Set(ids).size !== ids.length ||
      ids.some((id) => !known.has(id)) ||
      ids.length !== known.size
    )
      ctx.addIssue({
        code: "custom",
        message: "Working groups must cover the supplied regions exactly once",
      });
  });
export const LineSchema = z.object({
  line: z.number().int().min(1).max(40),
  transcription: z.string().max(800),
  status: z.enum(["correct", "incorrect", "uncertain", "not_checked"]),
  confidence: z.number().min(0).max(1),
  mathConfidence: z.number().min(0).max(1).optional(),
  regionId: z.string().nullable().optional(),
  explanation: z.string().max(800),
  hint: z.string().max(500),
  box: z
    .object({
      x: z.number().min(0).max(1000),
      y: z.number().min(0).max(1000),
      w: z.number().positive().max(1000),
      h: z.number().positive().max(1000),
    })
    .refine(
      (b) => b.x + b.w <= 1000.000001 && b.y + b.h <= 1000.000001,
      "Box must be within the snapshot",
    )
    .nullable(),
});
export const ModelReview = z
  .object({
    summary: z.string().min(1).max(1200),
    visual: TutorVisualSchema.nullable().optional(),
    lines: z.array(LineSchema).min(1).max(40),
    firstErrorLine: z.number().int().min(1).max(40).nullable(),
    nextStep: z.string().max(700),
    coverage: z.enum(["complete", "partial", "unreadable"]).optional(),
    answerLine: z.number().int().min(1).max(40).nullable().optional(),
    alternative: z
      .object({
        line: z.number().int().min(1).max(40),
        text: z.string().min(1).max(400),
      })
      .strict()
      .nullable()
      .optional(),
  })
  .strict()
  .superRefine((r, ctx) => {
    const ids = r.lines.map((l) => l.line);
    if (r.visual && !ids.includes(r.visual.line))
      ctx.addIssue({ code: "custom", message: "Visual anchor does not exist" });
    if (new Set(ids).size !== ids.length)
      ctx.addIssue({ code: "custom", message: "Duplicate line numbers" });
    if (r.firstErrorLine !== null && !ids.includes(r.firstErrorLine))
      ctx.addIssue({ code: "custom", message: "First error does not exist" });
    if (r.answerLine != null && !ids.includes(r.answerLine))
      ctx.addIssue({ code: "custom", message: "Answer line does not exist" });
    if (r.alternative && !ids.includes(r.alternative.line))
      ctx.addIssue({
        code: "custom",
        message: "Alternative anchor does not exist",
      });
  });
export function validateFeedback(input: unknown, revision: number) {
  const parsed = ModelReview.parse(input);
  const lines = parsed.lines
    .sort((a, b) => a.line - b.line)
    .map((l) =>
      l.confidence < 0.9 || (l.mathConfidence ?? 1) < 0.9
        ? {
            ...l,
            status: "uncertain" as const,
            box: null,
            regionId: null,
            explanation:
              l.confidence < 0.9
                ? "Could you rewrite this step more clearly?"
                : "I cannot verify this step yet. Please add its justification.",
            hint: "",
          }
        : l,
    );
  return {
    ...parsed,
    revision,
    lines,
    ...(parsed.visual &&
    lines.find((l) => l.line === parsed.visual!.line)?.status === "uncertain"
      ? { visual: null }
      : {}),
    ...(lines.some(
      (l, i) =>
        l.status === "uncertain" && parsed.lines[i].status !== "uncertain",
    )
      ? {
          summary: lines.some((l) => l.status === "incorrect")
            ? "There is a correction to make, and some working needs clarification."
            : "Some working needs clarification before I can verify the complete attempt.",
          nextStep:
            "Clarify the uncertain step, then submit the complete working again.",
        }
      : {}),
    ...(parsed.coverage
      ? {
          coverage:
            lines.some(
              (l) => l.status === "uncertain" || l.status === "not_checked",
            ) && parsed.coverage === "complete"
              ? ("partial" as const)
              : parsed.coverage,
        }
      : {}),
    ...(parsed.alternative &&
    lines.find((l) => l.line === parsed.alternative!.line)?.status ===
      "uncertain"
      ? { alternative: null }
      : {}),
    firstErrorLine: lines.find((l) => l.status === "incorrect")?.line ?? null,
  };
}
export function parseImage(data: string) {
  const match =
    /^data:(image\/(?:jpeg|png));base64,([A-Za-z0-9+/]+={0,2})$/.exec(data);
  if (!match)
    throw new Error("Only base64 JPEG and PNG snapshots are accepted.");
  const bytes = Buffer.from(match[2], "base64");
  if (bytes.length > 3_300_000 || bytes.length < 100)
    throw new Error("Snapshot size is outside the allowed range.");
  const valid =
    match[1] === "image/jpeg"
      ? bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff
      : bytes
          .subarray(0, 8)
          .equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]));
  if (!valid) throw new Error("Snapshot data does not match its image type.");
  return { mimeType: match[1], data: match[2] };
}
export function hasAccess(
  rows: { approved: boolean; expires_at: string | null }[],
  now = Date.now(),
) {
  return rows.some(
    (r) =>
      r.approved && (r.expires_at === null || Date.parse(r.expires_at) > now),
  );
}
const boxSchema = {
  type: "object",
  additionalProperties: false,
  required: ["x", "y", "w", "h"],
  properties: {
    x: { type: "number" },
    y: { type: "number" },
    w: { type: "number" },
    h: { type: "number" },
  },
};
const lineSchema = {
  type: "object",
  additionalProperties: false,
  required: [
    "line",
    "transcription",
    "status",
    "confidence",
    "explanation",
    "hint",
    "box",
  ],
  properties: {
    line: { type: "integer" },
    transcription: { type: "string" },
    status: {
      type: "string",
      enum: ["correct", "incorrect", "uncertain", "not_checked"],
    },
    confidence: { type: "number" },
    explanation: { type: "string" },
    hint: { type: "string" },
    box: { anyOf: [{ type: "null" }, boxSchema] },
  },
};
export const FEEDBACK_JSON_SCHEMA = {
  type: "object",
  additionalProperties: false,
  required: ["summary", "lines", "firstErrorLine", "nextStep"],
  properties: {
    summary: { type: "string" },
    firstErrorLine: { type: ["integer", "null"] },
    nextStep: { type: "string" },
    lines: { type: "array", items: lineSchema },
  },
};
