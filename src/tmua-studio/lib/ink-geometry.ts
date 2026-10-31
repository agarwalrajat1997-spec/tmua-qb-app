import { getStroke } from "perfect-freehand";
import polygonClipping from "polygon-clipping";
import type { InkGeometry, Point, Stroke } from "../types";
type XY = [number, number];
const shapes = new WeakMap<
  Stroke,
  {
    geometry: InkGeometry;
    bounds: { x: number; y: number; w: number; h: number };
  }
>();
function shape(stroke: Stroke) {
  let cached = shapes.get(stroke);
  if (cached) return cached;
  const outline = stroke.outline ?? [
    [
      getStroke(stroke.points, {
        size: stroke.size,
        thinning: stroke.tool === "highlighter" ? 0 : 0.45,
        smoothing: stroke.renderVersion === 2 ? 0.55 : 0.65,
        streamline: stroke.renderVersion === 2 ? 0.2 : 0.5,
        last: stroke.renderVersion === 2,
        simulatePressure: false,
      }) as XY[],
    ],
  ];
  let x = Infinity,
    y = Infinity,
    right = -Infinity,
    bottom = -Infinity;
  for (const polygon of outline)
    for (const ring of polygon)
      for (const p of ring) {
        x = Math.min(x, p[0]);
        y = Math.min(y, p[1]);
        right = Math.max(right, p[0]);
        bottom = Math.max(bottom, p[1]);
      }
  const geometry = Number.isFinite(x) ? outline : [];
  cached = {
    geometry,
    bounds: geometry.length
      ? { x, y, w: right - x, h: bottom - y }
      : { x: 0, y: 0, w: 0, h: 0 },
  };
  shapes.set(stroke, cached);
  return cached;
}
export const strokeGeometry = (stroke: Stroke) => shape(stroke).geometry;
export const strokeBounds = (stroke: Stroke) => shape(stroke).bounds;
export function geometryPath(geometry: InkGeometry) {
  return geometry
    .flatMap((p) =>
      p.map((r) =>
        r.length
          ? `M ${r.map(([x, y]) => `${x.toFixed(3)},${y.toFixed(3)}`).join(" L ")} Z`
          : "",
      ),
    )
    .join(" ");
}
// A swept circle catches the complete drag, even if the browser delivered only
// two distant pointer positions. Subtract from visible ink, never from the photo.
export function eraserSweep(
  from: Point,
  to: Point,
  radius: number,
): InkGeometry {
  const angle = Math.atan2(to[1] - from[1], to[0] - from[0]);
  const ring: XY[] = [];
  for (let i = 0; i <= 20; i++) {
    const a = angle - Math.PI / 2 + (i * Math.PI) / 20;
    ring.push([to[0] + radius * Math.cos(a), to[1] + radius * Math.sin(a)]);
  }
  for (let i = 0; i <= 20; i++) {
    const a = angle + Math.PI / 2 + (i * Math.PI) / 20;
    ring.push([from[0] + radius * Math.cos(a), from[1] + radius * Math.sin(a)]);
  }
  return [[ring]];
}
export function eraseInk(
  strokes: Stroke[],
  from: Point,
  to: Point,
  radius: number,
): Stroke[] {
  if (!Number.isFinite(radius) || radius <= 0) return strokes;
  const left = Math.min(from[0], to[0]) - radius,
    right = Math.max(from[0], to[0]) + radius;
  const top = Math.min(from[1], to[1]) - radius,
    bottom = Math.max(from[1], to[1]) + radius;
  const cut = eraserSweep(from, to, radius);
  let changed = false;
  const next: Stroke[] = [];
  for (const stroke of strokes) {
    const { geometry, bounds: b } = shape(stroke);
    if (
      b.x > right ||
      b.x + b.w < left ||
      b.y > bottom ||
      b.y + b.h < top ||
      !polygonClipping.intersection(geometry, cut).length
    ) {
      next.push(stroke);
      continue;
    }
    changed = true;
    const outline = polygonClipping.difference(geometry, cut);
    if (outline.length) next.push({ ...stroke, outline });
  }
  return changed ? next : strokes;
}
export function screenEraserRadius(diameter: number, screenScale: number) {
  return diameter / (2 * Math.max(0.0001, Math.abs(screenScale)));
}
