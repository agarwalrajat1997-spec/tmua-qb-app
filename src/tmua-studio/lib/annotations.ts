import type { Board, Feedback, Rect, ReviewRegion } from "../types";
import { pageRect, sourceObstacles, unionRects } from "./board-preparation";
export const TEACHER_INK = { red: "#e4262f", blue: "#0659d8" };
export type Annotation = {
  id: string;
  title: string;
  text: string;
  color: "red" | "blue";
  dashed: boolean;
  final: boolean;
  anchor: Rect | null;
  sourceArea?: Rect | null;
  visual?: Feedback["visual"];
  overview?: boolean;
  marker?: string;
  status?: Feedback["lines"][number]["status"];
  priority?: boolean;
  regionIds?: string[];
};
export const pad = (r: Rect, n: number): Rect => ({
  x: r.x - n,
  y: r.y - n,
  w: r.w + 2 * n,
  h: r.h + 2 * n,
});
export const intersects = (a: Rect, b: Rect) =>
  a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
export function regionWorld(r: ReviewRegion, capture: Rect): Rect {
  return {
    x: capture.x + (r.box.x * capture.w) / 1000,
    y: capture.y + (r.box.y * capture.h) / 1000,
    w: (r.box.w * capture.w) / 1000,
    h: (r.box.h * capture.h) / 1000,
  };
}
export function reviewAnnotations(
  feedback: Feedback,
  typedBoxes: Record<string, Rect> = {},
): Annotation[] {
  const regionMap = new Map(
    feedback.source?.regions.map((r) => [r.id, r]) ?? [],
  );
  const anchorFor = (line: Feedback["lines"][number]) => {
    const r = line.regionId ? regionMap.get(line.regionId) : null;
    return r?.kind === "typed"
      ? (typedBoxes[r.id] ?? null)
      : r && feedback.source
        ? regionWorld(r, feedback.source.capture)
        : line.box
          ? regionWorld({ id: "legacy", kind: "ink", box: line.box }, pageRect)
          : null;
  };
  const out: Annotation[] = [];
  if (feedback.groups) {
    const groupAnchor = (regionIds: string[]) => {
      const rects = regionIds
        .map((id) => {
          const r = regionMap.get(id);
          return r?.kind === "typed"
            ? typedBoxes[id]
            : r && feedback.source
              ? regionWorld(r, feedback.source.capture)
              : undefined;
        })
        .filter((r): r is Rect => !!r);
      return rects.length ? unionRects(rects) : null;
    };
    for (const [i, g] of feedback.groups.entries()) {
      const marker = String.fromCharCode(65 + i),
        label = feedback.lines[i]?.transcription || "Working";
      const unclear = g.status === "uncertain" || g.status === "not_checked";
      out.push({
        id: g.id,
        marker,
        title: `${g.status === "correct" ? "✓ Correct" : g.status === "incorrect" ? (feedback.firstErrorLine === i + 1 ? "Fix first" : "Correction") : g.status === "uncertain" ? "Please clarify" : "Follow-through"} · ${label}`,
        status: g.status,
        priority: feedback.firstErrorLine === i + 1,
        regionIds: g.regionIds,
        text:
          [g.good, g.explanation].filter(Boolean).join("\n") ||
          (g.status === "correct"
            ? "This part is correct."
            : "This part needs another look."),
        color: g.status === "incorrect" ? "red" : "blue",
        dashed: unclear,
        final: false,
        anchor: groupAnchor(g.regionIds),
      });
    }
    if (feedback.alternative)
      out.push({
        id: "alternative",
        title: "Another route",
        text: feedback.alternative.text,
        color: "blue",
        dashed: true,
        final: false,
        anchor: null,
      });
    if (feedback.visual)
      out.push({
        id: "visual",
        title: feedback.visual.title,
        text: feedback.visual.caption,
        color: "blue",
        dashed: false,
        final: false,
        anchor: null,
        visual: feedback.visual,
      });
    out.push({
      id: "overview",
      overview: true,
      title:
        feedback.coverage === "unreadable"
          ? "Clearer working needed"
          : feedback.coverage === "partial"
            ? "Overall feedback · some working unverified"
            : "Overall feedback",
      text: [
        feedback.summary,
        feedback.answer?.text,
        feedback.groups.find((g) => g.good)?.good
          ? "Good: " + feedback.groups.find((g) => g.good)!.good
          : "",
        feedback.firstErrorLine
          ? "Fix first: " +
            (feedback.groups[feedback.firstErrorLine - 1]?.explanation ?? "")
          : "",
        feedback.nextStep ? "Next: " + feedback.nextStep : "",
      ]
        .filter(Boolean)
        .join("\n"),
      color: "blue",
      dashed: feedback.coverage !== "complete",
      final: false,
      anchor: null,
    });
    return out;
  }
  for (const line of feedback.lines) {
    const final = feedback.answerLine === line.line,
      red = line.status === "incorrect",
      dashed = line.status === "uncertain" || line.status === "not_checked";
    if (line.status === "correct" && !line.explanation && !final) continue;
    const title = final
      ? red
        ? "× Check final answer"
        : line.status === "correct"
          ? "✓ Final answer"
          : "? Answer unverified"
      : red
        ? "× Correction"
        : line.status === "uncertain"
          ? "? Please clarify"
          : line.status === "not_checked"
            ? "↳ Check after the earlier step"
            : "✓ Good step";
    const anchor = line.status === "uncertain" ? null : anchorFor(line);
    const text =
      line.explanation ||
      (line.status === "correct"
        ? "This result is correct."
        : line.status === "not_checked"
          ? "Revisit this after correcting the earlier step."
          : "Please clarify this part of your working.");
    out.push({
      id: `line-${line.line}`,
      status: line.status,
      priority: line.line === feedback.firstErrorLine,
      regionIds: line.regionId ? [line.regionId] : [],
      title,
      text: anchor ? text : `${line.transcription}\n${text}`,
      color: red ? "red" : "blue",
      dashed,
      final,
      anchor,
      sourceArea:
        line.regionId && regionMap.has(line.regionId) ? anchorFor(line) : null,
    });
  }
  if (feedback.alternative) {
    const line = feedback.lines.find(
      (l) => l.line === feedback.alternative!.line,
    );
    if (line)
      out.push({
        id: "alternative",
        title: "↗ Another route",
        text: feedback.alternative.text,
        color: "blue",
        dashed: true,
        final: false,
        anchor: anchorFor(line),
      });
  }
  if (feedback.visual) {
    const line = feedback.lines.find((l) => l.line === feedback.visual!.line);
    if (line)
      out.push({
        id: "visual",
        title: feedback.visual.title,
        text: feedback.visual.caption,
        color: "blue",
        dashed: false,
        final: false,
        anchor: anchorFor(line),
        visual: feedback.visual,
      });
  }
  const last =
    feedback.lines.find((l) => l.line === feedback.firstErrorLine) ??
    feedback.lines.at(-1);
  out.push({
    id: "overview",
    overview: true,
    title:
      feedback.coverage === "unreadable"
        ? "? Clearer working needed"
        : feedback.coverage === "partial"
          ? "↳ Some working needs another look"
          : "Whole-attempt review",
    text:
      feedback.summary +
      (feedback.nextStep ? "\nNext: " + feedback.nextStep : ""),
    color: "blue",
    dashed: feedback.coverage !== "complete",
    final: false,
    anchor: null,
  });
  return out.sort(
    (a, b) => Number(b.color === "red") - Number(a.color === "red"),
  );
}
export type PlacedAnnotation = {
  annotation: Annotation;
  anchor: Rect | null;
  note: Rect;
  number: number;
  connector: string | null;
};
export function layoutAnnotations(
  annotations: Annotation[],
  obstacles: Rect[],
  sizes: Record<string, { w: number; h: number }>,
  fontSize: number,
) {
  const placed: PlacedAnnotation[] = [],
    used = obstacles.map((r) => pad(r, 14));
  let bounds = unionRects([pageRect, ...obstacles]);
  for (const [i, a] of annotations.entries()) {
    const anchor = a.anchor ? pad(a.anchor, 10) : null;
    const size = sizes[a.id] ?? {
      w: a.overview ? 1100 : fontSize * 16,
      h:
        fontSize * (3 + Math.ceil(a.text.length / 24)) * 1.4 +
        (a.visual ? fontSize * 9 : 0),
    };
    const occupied = [...used, ...placed.map((p) => pad(p.note, 32))];
    const candidates: Rect[] = [];
    if (anchor && !a.overview)
      for (const gap of [28, 70])
        candidates.push(
          { x: anchor.x + anchor.w + gap, y: anchor.y, w: size.w, h: size.h },
          { x: anchor.x - size.w - gap, y: anchor.y, w: size.w, h: size.h },
          { x: anchor.x, y: anchor.y + anchor.h + gap, w: size.w, h: size.h },
        );
    let note = candidates.find(
      (r) =>
        r.x >= 0 &&
        r.y >= 0 &&
        r.x + r.w <= pageRect.w &&
        r.y + r.h <= pageRect.h &&
        !occupied.some((o) => intersects(r, o)),
    );
    if (!note) {
      const bottom = Math.max(pageRect.h, ...occupied.map((r) => r.y + r.h));
      note = {
        x: 32,
        y: bottom + (a.overview ? 60 : 40),
        w: size.w,
        h: size.h,
      };
    }
    bounds = unionRects([bounds, pad(note, 24), ...(anchor ? [anchor] : [])]);
    let connector: string | null = null;
    if (anchor) {
      const start = { x: anchor.x + anchor.w, y: anchor.y + anchor.h / 2 },
        end = { x: note.x, y: note.y + fontSize };
      const corridor = {
        x: Math.min(start.x, end.x) - 3,
        y: Math.min(start.y, end.y) - 3,
        w: Math.abs(start.x - end.x) + 6,
        h: Math.abs(start.y - end.y) + 6,
      };
      if (!occupied.some((o) => intersects(corridor, o)))
        connector = `M ${start.x} ${start.y} Q ${end.x} ${start.y} ${end.x} ${end.y}`;
    }
    placed.push({ annotation: a, anchor, note, number: i + 1, connector });
  }
  return { placed, bounds };
}
export function sourceWorldBounds(board: Board) {
  return unionRects([pageRect, ...sourceObstacles(board)]);
}
