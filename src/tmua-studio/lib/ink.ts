import type { Stroke, Board, Rect } from "../types";
import { geometryPath, strokeGeometry } from "./ink-geometry";
export const WIDTH = 1200,
  HEIGHT = 900;
export function strokePath(stroke: Stroke) {
  return geometryPath(strokeGeometry(stroke));
}
export function boundedPoint(
  x: number,
  y: number,
  p: number,
): [number, number, number] {
  return [
    Math.max(0, Math.min(WIDTH, x)),
    Math.max(0, Math.min(HEIGHT, y)),
    Math.max(0.1, Math.min(1, p || 0.5)),
  ];
}
function readImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const im = new Image();
    im.onload = () => resolve(im);
    im.onerror = () => reject(new Error("Could not read this image."));
    im.src = src;
  });
}
export async function preparePhoto(file: File) {
  if (!["image/jpeg", "image/png", "image/webp"].includes(file.type))
    throw new Error("Choose a JPEG, PNG or WebP photo.");
  if (file.size > 10 * 1024 * 1024)
    throw new Error("Choose a photo smaller than 10 MB.");
  const url = URL.createObjectURL(file);
  try {
    const im = await readImage(url);
    if (im.width * im.height > 32_000_000)
      throw new Error("This photo is too large. Crop or resize it first.");
    const ratio = Math.min(1600 / im.width, 1600 / im.height, 1);
    const canvas = document.createElement("canvas");
    canvas.width = im.width * ratio;
    canvas.height = im.height * ratio;
    const ctx = canvas.getContext("2d")!;
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(im, 0, 0, canvas.width, canvas.height);
    const fit = Math.min(1080 / canvas.width, 780 / canvas.height);
    return {
      id: crypto.randomUUID(),
      data: canvas.toDataURL("image/jpeg", 0.86),
      rotation: 0,
      x: 60,
      y: 60,
      w: canvas.width * fit,
      h: canvas.height * fit,
    };
  } finally {
    URL.revokeObjectURL(url);
  }
}
export async function renderBoard(
  board: Board,
  capture: Rect = { x: 0, y: 0, w: WIDTH, h: HEIGHT },
) {
  const canvas = document.createElement("canvas");
  canvas.width = Math.ceil(capture.w);
  canvas.height = Math.ceil(capture.h);
  const ctx = canvas.getContext("2d")!;
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.translate(-capture.x, -capture.y);
  if (board.photo) {
    const p = board.photo;
    const im = await readImage(p.data);
    ctx.save();
    ctx.translate(p.x + p.w / 2, p.y + p.h / 2);
    ctx.rotate((p.rotation * Math.PI) / 180);
    ctx.drawImage(im, -p.w / 2, -p.h / 2, p.w, p.h);
    ctx.restore();
  }
  for (const stroke of board.strokes) {
    ctx.globalAlpha = stroke.tool === "highlighter" ? 0.3 : 1;
    ctx.fillStyle = stroke.color;
    ctx.fill(new Path2D(strokePath(stroke)));
  }
  ctx.globalAlpha = 1;
  return canvas;
}
export async function boardImage(board: Board) {
  return (await renderBoard(board)).toDataURL("image/jpeg", 0.88);
}
