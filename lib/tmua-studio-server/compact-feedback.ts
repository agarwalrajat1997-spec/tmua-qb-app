import { z } from "zod/v3";
import { VISUAL_JSON_SCHEMA } from "./visual-json-schema";
import { TutorVisualSchema } from "./tutor-visual";
import { LineSchema, validateFeedback } from "./contracts";
import type { ReviewRegion } from "./types";
const Compact = z
  .object({
    summary: z.string(),
    visual: TutorVisualSchema.nullable().default(null),
    lines: z.array(
      z
        .object({
          n: z.number(),
          t: z.string(),
          s: z.enum(["correct", "incorrect", "uncertain", "not_checked"]),
          c: z.number(),
          m: z.number().optional(),
          e: z.string(),
          b: LineSchema.shape.box.optional(),
          r: z.string().nullable().optional(),
        })
        .strict(),
    ),
    nextStep: z.string(),
    coverage: z.enum(["complete", "partial", "unreadable"]).default("complete"),
    answerLine: z.number().nullable().default(null),
    alternative: z
      .object({ line: z.number(), text: z.string() })
      .strict()
      .nullable()
      .default(null),
  })
  .strict();
export function expandReview(
  value: unknown,
  revision: number,
  regions: ReviewRegion[] = [],
) {
  const r = Compact.parse(value);
  return validateFeedback(
    {
      summary: r.summary,
      visual: r.visual,
      nextStep: r.nextStep,
      coverage: r.coverage,
      answerLine: r.answerLine,
      alternative: r.alternative,
      firstErrorLine: null,
      lines: r.lines.map((l) => {
        const region = l.r
          ? regions.find((region) => region.id === l.r)
          : undefined;
        if (l.r && !region) throw new Error("Unknown annotation region");
        return {
          line: l.n,
          transcription: l.t,
          status: l.s,
          confidence: l.c,
          mathConfidence: l.m ?? 1,
          explanation: l.e,
          hint: "",
          regionId: l.r ?? null,
          box:
            region?.kind === "ink"
              ? region.box
              : regions.length
                ? null
                : (l.b ?? null),
        };
      }),
    },
    revision,
  );
}
export const COMPACT_REVIEW_SCHEMA = {
  type: "object",
  additionalProperties: false,
  required: [
    "summary",
    "lines",
    "nextStep",
    "coverage",
    "answerLine",
    "alternative",
    "visual",
  ],
  properties: {
    summary: { type: "string" },
    visual: { anyOf: [{ type: "null" }, VISUAL_JSON_SCHEMA] },
    nextStep: { type: "string" },
    coverage: { type: "string", enum: ["complete", "partial", "unreadable"] },
    answerLine: { type: ["integer", "null"] },
    alternative: {
      anyOf: [
        { type: "null" },
        {
          type: "object",
          additionalProperties: false,
          required: ["line", "text"],
          properties: { line: { type: "integer" }, text: { type: "string" } },
        },
      ],
    },
    lines: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        required: ["n", "t", "s", "c", "m", "e", "r"],
        properties: {
          n: { type: "integer" },
          t: { type: "string" },
          s: {
            type: "string",
            enum: ["correct", "incorrect", "uncertain", "not_checked"],
          },
          c: { type: "number" },
          m: { type: "number" },
          e: { type: "string" },
          r: { type: ["string", "null"] },
        },
      },
    },
  },
};
