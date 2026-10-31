import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { Board, Feedback, Rect } from "../types";
import {
  layoutAnnotations,
  reviewAnnotations,
  regionWorld,
  TEACHER_INK,
  type PlacedAnnotation,
  type Annotation,
} from "../lib/annotations";
import { sourceObstacles } from "../lib/board-preparation";
import { MathHtml, MathText, escapeMathText } from "./MathHtml";
import { TutorDiagram } from "./TutorDiagram";
import { scheduleMathReveal } from "../lib/reveal-math";
const revealed = new Set<string>();

function InkNote({
  item,
  fontSize,
  onMeasure,
  animate = false,
  revealAt = 0,
  onSelect,
  selected = false,
}: {
  animate?: boolean;
  revealAt?: number;
  onSelect?: (annotation: Annotation) => void;
  selected?: boolean;
  item: PlacedAnnotation;
  fontSize: number;
  onMeasure: (id: string, size: { w: number; h: number }) => void;
}) {
  const ref = useRef<HTMLDivElement>(null),
    { annotation: a, note: n, number } = item;
  const noteSize = a.overview ? fontSize * 0.88 : fontSize;
  const width = a.overview ? 1100 : fontSize * 16;
  const [entered, setEntered] = useState(!animate);
  useEffect(() => {
    const node = ref.current;
    if (!animate || !node) return;
    const show = () => {
      scheduleMathReveal(node, revealAt);
      setEntered(true);
    };
    if (typeof IntersectionObserver === "undefined") {
      show();
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          show();
          observer.disconnect();
        }
      },
      { root: node.closest(".review-scroll"), threshold: 0 },
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, [animate, revealAt]);
  // One MathJax pass per note, instead of separate title/body passes.
  const noteHtml = `<strong class="note-heading">${a.marker ? escapeMathText(a.marker) + ". " : ""}${escapeMathText(a.title)}</strong><div>${escapeMathText(a.text).replaceAll("\n", "<br />")}</div>`;
  const measure = useCallback(() => {
    const node = ref.current;
    if (!node) return;
    const h = node.scrollHeight,
      w = Math.max(node.scrollWidth, width);
    if (h > 0) onMeasure(a.id, { w: w + 4, h: h + 8 });
  }, [a.id, width, onMeasure]);
  useEffect(() => {
    measure();
    let active = true;
    void document.fonts?.ready.then(() => {
      if (active) measure();
    });
    if (typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(measure);
    if (ref.current) observer.observe(ref.current);
    return () => {
      active = false;
      observer.disconnect();
    };
  }, [measure]);
  return (
    <foreignObject
      x={n.x}
      y={n.y}
      width={n.w}
      height={n.h}
      overflow="visible"
      pointerEvents={onSelect ? "all" : "none"}
    >
      <div
        ref={ref}
        data-reveal-waiting={!entered || undefined}
        className={`teacher-note ${a.color} ${a.overview ? "overview-note" : ""} ${a.priority ? "priority-note" : ""} ${selected ? "selected-note" : ""}`}
        role={onSelect ? "button" : undefined}
        tabIndex={onSelect ? 0 : undefined}
        aria-label={onSelect ? `Read feedback: ${a.title}` : undefined}
        onPointerDown={(e) => e.stopPropagation()}
        onClick={() => onSelect?.(a)}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            e.stopPropagation();
            onSelect?.(a);
          }
        }}
        style={{
          fontSize: noteSize,
          width,
          transform: `rotate(${number % 2 ? -0.6 : 0.6}deg)`,
        }}
      >
        <MathHtml
          html={noteHtml}
          onTypeset={measure}
          reveal={animate}
          revealAt={revealAt}
        />
        {a.visual && (
          <div className={animate ? "feedback-visual-enter" : ""}>
            <TutorDiagram visual={a.visual} />
          </div>
        )}
      </div>
    </foreignObject>
  );
}
export function BoardAnnotations({
  feedback,
  board,
  fontSize,
  onLayout,
  animate = false,
  reviewKey = "",
  onSelect,
  selectedId,
}: {
  reviewKey?: string;
  onSelect?: (annotation: Annotation) => void;
  selectedId?: string;
  animate?: boolean;
  feedback: Feedback;
  board: Board;
  fontSize: number;
  onLayout: (items: PlacedAnnotation[], bounds: Rect, review: Feedback) => void;
}) {
  const revealKey = `${reviewKey}:${feedback.source?.hash ?? feedback.revision}:${feedback.reviewId ?? ""}`;
  const firstReveal = useRef(animate && !revealed.has(revealKey));
  const startedAt = useRef(performance.now());
  useEffect(() => {
    revealed.add(revealKey);
  }, [revealKey]);
  const [sizes, setSizes] = useState<Record<string, { w: number; h: number }>>(
    {},
  );
  const [typedSizes, setTypedSizes] = useState<
    Record<string, { w: number; h: number }>
  >({});
  const measure = useCallback(
    (id: string, size: { w: number; h: number }) =>
      setSizes((old) =>
        old[id]?.w === size.w && old[id]?.h === size.h
          ? old
          : { ...old, [id]: size },
      ),
    [],
  );
  const source = useMemo(() => sourceObstacles(board), [board]);
  const typed = useMemo(() => {
    let y = Math.max(900, ...source.map((r) => r.y + r.h)) + 40;
    return (
      feedback.source?.regions.filter((r) => r.kind === "typed") ?? []
    ).map((r) => {
      const size = typedSizes[r.id] ?? {
        w: 1100,
        h: fontSize * (2 + Math.ceil((r.text?.length ?? 0) / 45)),
      };
      const box = { x: 24, y, w: size.w, h: size.h };
      y += size.h + 20;
      return { ...r, box };
    });
  }, [feedback, source, typedSizes, fontSize]);
  const layout = useMemo(
    () =>
      layoutAnnotations(
        reviewAnnotations(
          feedback,
          Object.fromEntries(typed.map((r) => [r.id, r.box])),
        ),
        [...source, ...typed.map((r) => r.box)],
        sizes,
        fontSize,
      ),
    [feedback, typed, source, sizes, fontSize],
  );
  useEffect(() => {
    onLayout(layout.placed, layout.bounds, feedback);
  }, [layout, onLayout, feedback]);
  const known = new Set(layout.placed.map((p) => p.annotation.id));
  const markedRegions = new Set(
    feedback.lines
      .filter((l) => l.status !== "correct" || known.has(`line-${l.line}`))
      .map((l) => l.regionId),
  );
  return (
    <g
      className="teacher-layer"
      data-ai-review="true"
      role="group"
      aria-label="Tutor annotations on your working"
      pointerEvents="none"
    >
      {typed.map((r) => (
        <TypedSource
          key={r.id}
          id={r.id}
          box={r.box}
          text={r.text ?? ""}
          fontSize={fontSize}
          onMeasure={(id, size) =>
            setTypedSizes((old) =>
              old[id]?.w === size.w && old[id]?.h === size.h
                ? old
                : { ...old, [id]: size },
            )
          }
        />
      ))}
      {(feedback.groups ? [] : feedback.lines)
        .filter(
          (l) =>
            l.status === "correct" &&
            !known.has(`line-${l.line}`) &&
            !markedRegions.has(l.regionId),
        )
        .map((l) => {
          const region = feedback.source?.regions.find(
            (r) => r.id === l.regionId,
          );
          if (!region || region.kind !== "ink" || !feedback.source) return null;
          const b = regionWorld(region, feedback.source.capture);
          return (
            <g key={`check-${l.line}`}>
              <title>Correct: {l.transcription}</title>
              <rect
                x={b.x - 5}
                y={b.y - 5}
                width={b.w + 10}
                height={b.h + 10}
                fill="none"
                stroke={TEACHER_INK.blue}
                strokeWidth="1.5"
                vectorEffect="non-scaling-stroke"
              />
              <text
                x={b.x + b.w + 8}
                y={b.y + b.h}
                fill={TEACHER_INK.blue}
                fontFamily="Kalam"
                fontSize={fontSize}
              >
                ✓
              </text>
            </g>
          );
        })}
      {layout.placed.map((item, index) => {
        const { annotation: a, anchor: r, number } = item,
          color = TEACHER_INK[a.color];
        const delay = Math.min(index, 6) * 120;
        const boxEnd = delay + 520;
        const drawClass = firstReveal.current
          ? a.dashed
            ? "feedback-mark-enter"
            : "feedback-box-draw"
          : undefined;
        return (
          <g
            key={a.id}
            data-annotation-id={a.id}
            data-priority={a.priority || undefined}
            style={
              {
                "--feedback-delay": `${delay}ms`,
                "--feedback-note-delay": `${boxEnd + 70}ms`,
              } as React.CSSProperties
            }
          >
            <title>
              {a.title}: {a.text}
            </title>
            {r && (
              <>
                <rect
                  className={drawClass}
                  pathLength={firstReveal.current && !a.dashed ? 1 : undefined}
                  x={r.x}
                  y={r.y}
                  width={r.w}
                  height={r.h}
                  fill={
                    selectedId === a.id ? "rgba(255,177,77,.10)" : "transparent"
                  }
                  stroke={color}
                  strokeWidth={
                    selectedId === a.id || a.priority
                      ? 3.2
                      : a.final
                        ? 2.4
                        : a.status === "correct"
                          ? 1.2
                          : 1.7
                  }
                  pointerEvents="all"
                  role="button"
                  tabIndex={0}
                  aria-label={`Read feedback: ${a.title}`}
                  style={{ cursor: "pointer" }}
                  onPointerDown={(e) => e.stopPropagation()}
                  onClick={() => onSelect?.(a)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      e.stopPropagation();
                      onSelect?.(a);
                    }
                  }}
                  strokeDasharray={a.dashed ? "6 5" : undefined}
                  vectorEffect="non-scaling-stroke"
                />
                {a.final && (
                  <rect
                    className={drawClass}
                    pathLength={
                      firstReveal.current && !a.dashed ? 1 : undefined
                    }
                    x={r.x - 5}
                    y={r.y - 5}
                    width={r.w + 10}
                    height={r.h + 10}
                    fill="none"
                    stroke={color}
                    strokeWidth="1"
                    strokeDasharray={a.dashed ? "6 5" : undefined}
                    vectorEffect="non-scaling-stroke"
                  />
                )}
                <text
                  className={
                    firstReveal.current ? "feedback-marker-enter" : undefined
                  }
                  x={r.x - fontSize * 0.65}
                  y={r.y + fontSize * 0.75}
                  fill={color}
                  fontSize={fontSize * 0.65}
                  fontFamily="Kalam"
                >
                  {a.marker ?? number}
                </text>
              </>
            )}
            {item.connector && (
              <path
                className={
                  firstReveal.current ? "feedback-connector-draw" : undefined
                }
                pathLength={firstReveal.current ? 1 : undefined}
                d={item.connector}
                stroke={color}
                fill="none"
                strokeWidth="1.5"
                vectorEffect="non-scaling-stroke"
              />
            )}
            <InkNote
              item={item}
              fontSize={fontSize}
              onMeasure={measure}
              animate={firstReveal.current}
              revealAt={startedAt.current + boxEnd + 70}
              onSelect={onSelect}
              selected={selectedId === a.id}
            />
          </g>
        );
      })}
    </g>
  );
}
function TypedSource({
  id,
  box,
  text,
  fontSize,
  onMeasure,
}: {
  id: string;
  box: Rect;
  text: string;
  fontSize: number;
  onMeasure: (id: string, size: { w: number; h: number }) => void;
}) {
  const ref = useRef<HTMLDivElement>(null),
    latest = useRef(onMeasure);
  latest.current = onMeasure;
  const measure = useCallback(() => {
    const n = ref.current;
    if (n?.scrollHeight)
      latest.current(id, {
        w: Math.max(1100, n.scrollWidth),
        h: n.scrollHeight + 8,
      });
  }, [id]);
  return (
    <foreignObject
      x={box.x}
      y={box.y}
      width={box.w}
      height={box.h}
      overflow="visible"
    >
      <div
        ref={ref}
        className="board-typed-source"
        style={{ fontSize, width: 1100 }}
      >
        <MathText text={text} inline={false} onTypeset={measure} />
      </div>
    </foreignObject>
  );
}
