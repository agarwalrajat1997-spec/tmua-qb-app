import { z } from "zod/v3";
import type { Feedback, FeedbackGroup, ReviewRegion } from "./types";
import { TutorVisualSchema } from "./tutor-visual";
import { VISUAL_JSON_SCHEMA } from "./visual-json-schema";
const status = z.enum(["correct", "incorrect", "uncertain", "not_checked"]);
const confidence = z.number().min(0).max(1);
const Grouped = z
  .object({
    boxes: z
      .array(
        z
          .object({
            n: z.number().int().min(1).max(6),
            t: z.string().max(100),
            r: z.array(z.string()).max(80),
            s: status,
            c: confidence,
            m: confidence,
            g: z.string().max(400),
            e: z.string().max(700),
          })
          .strict(),
      )
      .min(1)
      .max(6),
    summary: z.string().min(1).max(900),
    nextStep: z.string().max(600),
    coverage: z.enum(["complete", "partial", "unreadable"]),
    answer: z
      .object({
        r: z.string().nullable(),
        s: status,
        t: z.string().max(500),
        c: confidence,
        m: confidence,
      })
      .strict()
      .nullable(),
    alternative: z
      .object({
        line: z.number().int().min(1).max(6),
        text: z.string().max(400),
      })
      .strict()
      .nullable(),
    visual: TutorVisualSchema.nullable(),
  })
  .strict();
export function expandGroupedReview(
  value: unknown,
  revision: number,
  regions: ReviewRegion[],
): Feedback {
  const parsed = Grouped.parse(value),
    known = new Set(regions.map((r) => r.id)),
    assigned = parsed.boxes.flatMap((b) => b.r);
  if (
    new Set(assigned).size !== assigned.length ||
    assigned.some((id) => !known.has(id)) ||
    assigned.length !== known.size
  )
    throw Error("Groups must cover every supplied region exactly once");
  if (
    new Set(parsed.boxes.map((b) => b.n)).size !== parsed.boxes.length ||
    parsed.boxes.some((b, i) => b.n !== i + 1)
  )
    throw Error("Invalid group numbering");
  if (known.size && parsed.boxes.some((b) => !b.r.length))
    throw Error("Empty feedback group");
  if (parsed.answer?.r && !known.has(parsed.answer.r))
    throw Error("Unknown final-answer region");
  if (
    parsed.alternative &&
    !parsed.boxes.some((b) => b.n === parsed.alternative!.line)
  )
    throw Error("Unknown alternative group");
  if (parsed.visual && !parsed.boxes.some((b) => b.n === parsed.visual!.line))
    throw Error("Unknown diagram group");
  const groups: FeedbackGroup[] = parsed.boxes.map((b) => {
    const low = b.c < 0.9 || b.m < 0.9;
    return {
      id: `box-${b.n}`,
      regionIds: b.r,
      status: low ? "uncertain" : b.s,
      good: low ? "" : b.g,
      explanation:
        low && b.s !== "uncertain"
          ? "Please clarify this part before I can verify it."
          : b.e,
    };
  });

  const answer = parsed.answer
    ? {
        regionId: parsed.answer.r,
        status:
          parsed.answer.c < 0.9 || parsed.answer.m < 0.9
            ? ("uncertain" as const)
            : parsed.answer.s,
        text:
          parsed.answer.c < 0.9 || parsed.answer.m < 0.9
            ? "Your final answer needs clarification."
            : parsed.answer.t,
      }
    : null;
  const partial =
    groups.some(
      (g) => g.status === "uncertain" || g.status === "not_checked",
    ) ||
    answer?.status === "uncertain" ||
    answer?.status === "not_checked";
  const downgraded =
    groups.some((g, i) => g.status !== parsed.boxes[i].s) ||
    answer?.status !== parsed.answer?.s;
  const uncertainGroup = (n: number) => groups[n - 1]?.status === "uncertain";
  return {
    revision,
    groups,
    answer,
    summary: downgraded
      ? "Some working needs clarification before the whole attempt can be verified."
      : parsed.summary,
    nextStep: downgraded
      ? "Clarify the marked area when you try the question again."
      : parsed.nextStep,
    coverage:
      partial && parsed.coverage === "complete" ? "partial" : parsed.coverage,
    lines: groups.map((g, i) => ({
      line: i + 1,
      transcription: parsed.boxes[i].t,
      status: g.status,
      explanation: g.explanation,
      hint: g.good,
      box: null,
      regionId: null,
    })),
    firstErrorLine:
      groups.findIndex((g) => g.status === "incorrect") < 0
        ? null
        : groups.findIndex((g) => g.status === "incorrect") + 1,
    answerLine: null,
    alternative:
      parsed.alternative && !uncertainGroup(parsed.alternative.line)
        ? parsed.alternative
        : null,
    visual:
      parsed.visual && !uncertainGroup(parsed.visual.line)
        ? parsed.visual
        : null,
  };
}
const object = (properties: Record<string, unknown>) => ({
  type: "object",
  additionalProperties: false,
  required: Object.keys(properties),
  properties,
});
const text = { type: "string" },
  number = { type: "number" },
  integer = { type: "integer" },
  state = {
    type: "string",
    enum: ["correct", "incorrect", "uncertain", "not_checked"],
  };
const nullable = (schema: unknown) => ({ anyOf: [{ type: "null" }, schema] });
export const GROUPED_REVIEW_SCHEMA = object({
  boxes: {
    type: "array",
    items: object({
      n: integer,
      t: text,
      r: { type: "array", items: text },
      s: state,
      c: number,
      m: number,
      g: text,
      e: text,
    }),
  },
  summary: text,
  nextStep: text,
  coverage: { type: "string", enum: ["complete", "partial", "unreadable"] },
  answer: nullable(
    object({
      r: { type: ["string", "null"] },
      s: state,
      t: text,
      c: number,
      m: number,
    }),
  ),
  alternative: nullable(object({ line: integer, text })),
  visual: nullable(VISUAL_JSON_SCHEMA),
});
