import type { Board, Rect, ReviewRegion, WorkingGroup } from "../types";
import { workingGroups } from "./working-groups";
import { WIDTH, HEIGHT, renderBoard } from "./ink";
import { strokeBounds } from "./ink-geometry";
export const pageRect: Rect = { x: 0, y: 0, w: WIDTH, h: HEIGHT };
export function unionRects(rects: Rect[]): Rect {
  const x = Math.min(...rects.map((r) => r.x)),
    y = Math.min(...rects.map((r) => r.y));
  return {
    x,
    y,
    w: Math.max(...rects.map((r) => r.x + r.w)) - x,
    h: Math.max(...rects.map((r) => r.y + r.h)) - y,
  };
}
export function sourceObstacles(board: Board): Rect[] {
  const boxes = board.strokes.map(strokeBounds);
  if (board.photo) {
    const p = board.photo,
      a = (p.rotation * Math.PI) / 180,
      w = Math.abs(Math.cos(a)) * p.w + Math.abs(Math.sin(a)) * p.h,
      h = Math.abs(Math.sin(a)) * p.w + Math.abs(Math.cos(a)) * p.h;
    boxes.push({ x: p.x + p.w / 2 - w / 2, y: p.y + p.h / 2 - h / 2, w, h });
  }
  return boxes;
}
export function captureBounds(board: Board): Rect {
  const boxes = sourceObstacles(board);
  if (!boxes.length) return pageRect;
  const b = unionRects(boxes),
    x = Math.floor(b.x - 24),
    y = Math.floor(b.y - 24);
  return {
    x,
    y,
    w: Math.max(120, Math.ceil(b.x + b.w + 24) - x),
    h: Math.max(80, Math.ceil(b.y + b.h + 24) - y),
  };
}
// Spatial regions are locators, never claims about reading order or mathematics.
// No OCR/model call is involved. Scan the clean raster, including imported photos.
export function rasterRegions(
  data: Uint8ClampedArray,
  width: number,
  height: number,
): ReviewRegion[] {
  const rows: Array<{ y: number; left: number; right: number; count: number }> =
    [];
  for (let y = 0; y < height; y++) {
    let count = 0,
      left = width,
      right = -1;
    for (let x = 0; x < width; x++) {
      const i = (y * width + x) * 4;
      if (
        data[i + 3] > 80 &&
        Math.min(data[i], data[i + 1], data[i + 2]) < 180
      ) {
        left = Math.min(left, x);
        right = x;
        count++;
      }
    }
    if (right >= left) rows.push({ y, left, right, count });
  }
  const bands: Rect[] = [];
  for (const row of rows) {
    const last = bands.at(-1);
    if (last && row.y <= last.y + last.h + 14) {
      const right = Math.max(last.x + last.w, row.right + 1);
      last.x = Math.min(last.x, row.left);
      last.w = right - last.x;
      last.h = row.y + 1 - last.y;
    } else
      bands.push({ x: row.left, y: row.y, w: row.right - row.left + 1, h: 1 });
  }
  // Sparse connecting pen marks can join several stages into one giant band.
  // Split only tall bands at sustained density valleys, retaining every pixel row.
  for (let i = bands.length - 1; i >= 0; i--) {
    const b = bands[i];
    if (b.h < Math.max(100, height * 0.13)) continue;
    const inside = rows.filter((r) => r.y >= b.y && r.y < b.y + b.h);
    const counts = inside.map((r) => r.count).sort((a, b) => a - b);
    const threshold = Math.max(
      5,
      counts[Math.floor(counts.length * 0.8)] * 0.3,
    );
    const dense = inside.filter((r) => r.count >= threshold),
      cuts: number[] = [];
    for (let j = 1; j < dense.length; j++)
      if (
        dense[j].y - dense[j - 1].y >= 18 &&
        dense[j - 1].y - b.y >= 18 &&
        b.y + b.h - dense[j].y >= 18
      )
        cuts.push(Math.floor((dense[j].y + dense[j - 1].y) / 2));
    if (!cuts.length) continue;
    const boundaries = [b.y, ...cuts, b.y + b.h],
      pieces: Rect[] = [];
    for (let j = 1; j < boundaries.length; j++) {
      const part = inside.filter(
        (r) => r.y >= boundaries[j - 1] && r.y < boundaries[j],
      );
      if (!part.length) continue;
      const x = Math.min(...part.map((r) => r.left)),
        right = Math.max(...part.map((r) => r.right));
      pieces.push({
        x,
        y: part[0].y,
        w: right - x + 1,
        h: part.at(-1)!.y + 1 - part[0].y,
      });
    }
    bands.splice(i, 1, ...pieces);
  }
  // If a page is unusually dense, keep all content in coarse regions instead of truncating it.
  while (bands.length > 60) {
    let at = 0,
      gap = Infinity;
    for (let i = 0; i < bands.length - 1; i++) {
      const d = bands[i + 1].y - bands[i].y - bands[i].h;
      if (d < gap) {
        gap = d;
        at = i;
      }
    }
    bands.splice(at, 2, unionRects(bands.slice(at, at + 2)));
  }
  return bands.map((b, i) => ({
    id: `ink-${i + 1}`,
    kind: "ink",
    box: {
      x: (b.x / width) * 1000,
      y: (b.y / height) * 1000,
      w: (b.w / width) * 1000,
      h: (b.h / height) * 1000,
    },
  }));
}
export function typedRegions(note: string): ReviewRegion[] {
  const lines = note
    .split(/\n/)
    .map((t) => t.trim())
    .filter(Boolean);
  // Long typed attempts are passed intact even when region granularity is reduced.
  const chunks =
    lines.length <= 20
      ? lines
      : Array.from({ length: 20 }, (_, i) =>
          lines
            .slice(
              Math.floor((i * lines.length) / 20),
              Math.floor(((i + 1) * lines.length) / 20),
            )
            .join("\n"),
        );
  return chunks.map((text, i) => ({
    id: `typed-${i + 1}`,
    kind: "typed",
    box: { x: 0, y: 0, w: 1, h: 1 },
    text,
  }));
}
export async function contentHash(board: Board) {
  const bytes = new TextEncoder().encode(
    JSON.stringify({
      strokes: board.strokes,
      photo: board.photo,
      note: board.note,
    }),
  );
  return Array.from(
    new Uint8Array(await crypto.subtle.digest("SHA-256", bytes)),
  )
    .map((n) => n.toString(16).padStart(2, "0"))
    .join("");
}
export type PreparedBoard = {
  board: Board;
  image: string;
  capture: Rect;
  regions: ReviewRegion[];
  groups?: WorkingGroup[];
  hash: string;
  structure: { steps: [] };
};
export async function prepareBoard(board: Board): Promise<PreparedBoard> {
  const capture = captureBounds(board),
    hashPromise = contentHash(board);
  let image = "",
    regions: ReviewRegion[] = [];
  if (board.strokes.length || board.photo) {
    const canvas = await renderBoard(board, capture),
      ctx = canvas.getContext("2d")!;
    regions = rasterRegions(
      ctx.getImageData(0, 0, canvas.width, canvas.height).data,
      canvas.width,
      canvas.height,
    );
    image = canvas.toDataURL("image/png");
    if (image.length > 4_300_000) image = canvas.toDataURL("image/jpeg", 0.94);
  }
  const allRegions = [...regions, ...typedRegions(board.note)];
  return {
    board,
    image,
    capture,
    regions: allRegions,
    groups: workingGroups(allRegions),
    hash: await hashPromise,
    structure: { steps: [] },
  };
}
// One bounded cache. An old task may finish, but cannot replace a newer revision.
export function createPreparationCache<T extends object, R>(
  prepare: (source: T) => Promise<R>,
) {
  let source: T | undefined, pending: Promise<R> | undefined;
  return {
    get(value: T) {
      if (source === value && pending) return pending;
      source = value;
      const task = Promise.resolve().then(() => prepare(value));
      pending = task;
      void task.catch(() => {
        if (pending === task) {
          source = undefined;
          pending = undefined;
        }
      });
      return task;
    },
    clear() {
      source = undefined;
      pending = undefined;
    },
  };
}
