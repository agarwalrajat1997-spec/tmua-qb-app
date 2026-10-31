import { z } from "zod/v3";

const coordinate = z.number().finite().min(-1e6).max(1e6);
const point = z.object({ x: coordinate, y: coordinate }).strict();
// A bounded drawing recipe, never generated HTML, executable code or a remote URL.
export const TutorVisualSchema = z
  .object({
    line: z.number().int().min(1).max(40),
    title: z.string().min(1).max(80),
    caption: z.string().max(300),
    xMin: coordinate,
    xMax: coordinate,
    yMin: coordinate,
    yMax: coordinate,
    axes: z.boolean(),
    curves: z
      .array(
        z.object({ coefficients: z.array(coordinate).min(1).max(7) }).strict(),
      )
      .max(3),
    segments: z
      .array(z.object({ from: point, to: point, dashed: z.boolean() }).strict())
      .max(12),
    labels: z
      .array(z.object({ at: point, text: z.string().min(1).max(80) }).strict())
      .max(8),
  })
  .strict()
  .superRefine((v, ctx) => {
    if (v.xMax - v.xMin < 0.000001 || v.yMax - v.yMin < 0.000001)
      ctx.addIssue({ code: "custom", message: "Invalid visual range" });
    if (!v.curves.length && !v.segments.length)
      ctx.addIssue({ code: "custom", message: "Visual has no content" });
    for (const p of [
      ...v.segments.flatMap((s) => [s.from, s.to]),
      ...v.labels.map((l) => l.at),
    ])
      if (p.x < v.xMin || p.x > v.xMax || p.y < v.yMin || p.y > v.yMax)
        ctx.addIssue({
          code: "custom",
          message: "Visual point outside its range",
        });
  });
export type TutorVisual = z.infer<typeof TutorVisualSchema>;
export function polynomialValue(coefficients: number[], x: number) {
  return coefficients.reduceRight((y, c) => y * x + c, 0);
}
export function plotCurve(
  coefficients: number[],
  v: Pick<TutorVisual, "xMin" | "xMax" | "yMin" | "yMax">,
) {
  let path = "",
    drawing = false;
  for (let i = 0; i <= 240; i++) {
    const x = v.xMin + ((v.xMax - v.xMin) * i) / 240,
      y = polynomialValue(coefficients, x);
    if (!Number.isFinite(y) || y < v.yMin || y > v.yMax) {
      drawing = false;
      continue;
    }
    const px = 24 + ((x - v.xMin) / (v.xMax - v.xMin)) * 352,
      py = 224 - ((y - v.yMin) / (v.yMax - v.yMin)) * 200;
    path += `${drawing ? "L" : "M"}${px.toFixed(2)},${py.toFixed(2)} `;
    drawing = true;
  }
  return path;
}
