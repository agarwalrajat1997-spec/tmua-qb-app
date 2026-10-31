const number = { type: "number" };
const text = { type: "string" };
const object = (properties: Record<string, unknown>) => ({
  type: "object",
  additionalProperties: false,
  required: Object.keys(properties),
  properties,
});
const point = object({ x: number, y: number });
export const VISUAL_JSON_SCHEMA = object({
  line: { type: "integer" },
  title: text,
  caption: text,
  xMin: number,
  xMax: number,
  yMin: number,
  yMax: number,
  axes: { type: "boolean" },
  curves: {
    type: "array",
    items: object({ coefficients: { type: "array", items: number } }),
  },
  segments: {
    type: "array",
    items: object({ from: point, to: point, dashed: { type: "boolean" } }),
  },
  labels: { type: "array", items: object({ at: point, text }) },
});
