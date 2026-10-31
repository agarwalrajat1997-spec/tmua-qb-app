import {
  memo,
  forwardRef,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
  useCallback,
} from "react";
import {
  PenLine,
  Highlighter,
  Eraser,
  Undo2,
  Redo2,
  ImagePlus,
  Download,
  Trash2,
  Hand,
  ZoomIn,
  ZoomOut,
  Maximize,
  RotateCw,
} from "lucide-react";
import type { Board, Feedback, Point, Stroke, Rect } from "../types";
import { emptyBoard } from "../types";
import {
  loadBoard,
  saveBoard,
  loadReview,
  saveReview,
  loadPadView,
  savePadView,
} from "../lib/storage";
import { eraseInk, screenEraserRadius } from "../lib/ink-geometry";
import {
  boardImage,
  boundedPoint,
  HEIGHT,
  preparePhoto,
  strokePath,
  WIDTH,
} from "../lib/ink";
import { MathText } from "./MathHtml";
import { useDialogFocus } from "../lib/useDialogFocus";
import {
  prepareBoard,
  contentHash,
  createPreparationCache,
  type PreparedBoard,
} from "../lib/board-preparation";
import { BoardAnnotations } from "./BoardAnnotations";
import type { PlacedAnnotation, Annotation } from "../lib/annotations";
import { FeedbackDetail } from "./FeedbackDetail";
import { studentErrorMessage } from "../lib/student-content";
export type BoardHandle = {
  snapshot: () => Promise<PreparedBoard>;
  freeze: () => Promise<PreparedBoard>;
  releaseUnsubmitted: () => void;
  isCurrent: (snapshot: PreparedBoard) => boolean;
  hasWork: () => boolean;
};
type Props = {
  storageKey: string;
  feedback: Feedback | null;
  readOnly?: boolean;
  onRevision: (n: number) => void;
  onStatus: (s: string) => void;
  checking?: boolean;
  reviewStage?: "preparing" | "queued" | "reviewing";
  reviewError?: string;
  allowReview?: boolean;
  animateFeedback?: boolean;
  onClarify?: (regionIds: string[], text: string) => Promise<void>;
};
const InkStroke = memo(function InkStroke({ stroke: s }: { stroke: Stroke }) {
  return (
    <path
      d={strokePath(s)}
      fill={s.color}
      opacity={s.tool === "highlighter" ? 0.3 : 1}
    />
  );
});
export const InkBoard = forwardRef<BoardHandle, Props>(function InkBoard(
  {
    storageKey,
    feedback,
    readOnly: externalReadOnly = false,
    onRevision,
    onStatus,
    checking = false,
    reviewStage = "reviewing",
    reviewError = "",
    allowReview = true,
    animateFeedback = false,
    onClarify,
  },
  ref,
) {
  const [frozen, setFrozen] = useState(false);
  const [selectedAnnotation, setSelectedAnnotation] =
    useState<Annotation | null>(null);
  const closeDetail = useCallback(() => setSelectedAnnotation(null), []);
  useEffect(() => setSelectedAnnotation(null), [feedback]);
  const readOnly = externalReadOnly || frozen;
  const locked = useRef(readOnly);
  locked.current = readOnly;
  const wrap = useRef<HTMLDivElement>(null);
  const [board, setBoard] = useState<Board>(emptyBoard);
  const current = useRef(board);
  current.current = board;
  const preparation = useRef(createPreparationCache(prepareBoard));
  const [savedFeedback, setSavedFeedback] = useState<Feedback | null>(null);
  const [showNotes, setShowNotes] = useState(true);
  const [annotationBounds, setAnnotationBounds] = useState<Rect>({
    x: 0,
    y: 0,
    w: WIDTH,
    h: HEIGHT,
  });
  const [noteFont, setNoteFont] = useState(36);
  const [loaded, setLoaded] = useState(false);
  const [tool, setTool] = useState<"pen" | "highlighter" | "eraser" | "hand">(
    "pen",
  );
  const [color, setColor] = useState("#172033");
  const [penOnly, setPenOnly] = useState(false);
  const [erasing, setErasing] = useState<Stroke[] | null>(null);
  const eraseRef = useRef<{
    strokes: Stroke[];
    last: Point;
    radius: number;
  } | null>(null);
  const eraserCursor = useRef<SVGCircleElement>(null);
  const [active, setActive] = useState<Stroke | null>(null);
  const strokeRef = useRef<Stroke | null>(null);
  const pointer = useRef<number | null>(null);
  const svg = useRef<SVGSVGElement>(null);
  const input = useRef<HTMLInputElement>(null);
  const photoGeneration = useRef(0);
  const photoPending = useRef(false);
  const undo = useRef<Board[]>([]),
    redo = useRef<Board[]>([]);
  const [version, setVersion] = useState(0);
  const [view, setView] = useState({ x: 0, y: 0, w: WIDTH, h: HEIGHT });
  const viewRef = useRef(view);
  viewRef.current = view;
  const restoreScroll = useRef<{ top: number; left: number } | null>(null);
  const scrollPosition = useRef({ top: 0, left: 0 });
  const scrollSaveTimer = useRef<ReturnType<typeof setTimeout> | undefined>(
    undefined,
  );
  const persistView = () =>
    savePadView(storageKey, {
      view: viewRef.current,
      ...scrollPosition.current,
    });
  const pan = useRef<{ x: number; y: number; vx: number; vy: number } | null>(
    null,
  );
  const [error, setError] = useState("");
  const [clearOpen, setClearOpen] = useState(false);
  useDialogFocus(clearOpen, () => setClearOpen(false));
  useEffect(() => {
    let ignore = false;
    Promise.all([loadBoard(storageKey), loadPadView(storageKey)])
      .then(([b, savedView]) => {
        if (!ignore) {
          if (b) setBoard(b);
          if (savedView) {
            setView(savedView.view);
            restoreScroll.current = {
              top: savedView.top,
              left: savedView.left,
            };
            scrollPosition.current = {
              top: savedView.top,
              left: savedView.left,
            };
          }
          setLoaded(true);
        }
      })
      .catch(() => {
        if (!ignore) {
          setLoaded(true);
          setError(
            "Device storage is unavailable. Export your work before leaving.",
          );
        }
      });
    return () => {
      ignore = true;
    };
  }, [storageKey]);
  useEffect(() => {
    if (!loaded) return;
    const pending = restoreScroll.current;
    if (pending && wrap.current) {
      wrap.current.scrollTop = pending.top;
      wrap.current.scrollLeft = pending.left;
      if (wrap.current.scrollHeight - wrap.current.clientHeight >= pending.top)
        restoreScroll.current = null;
    }
  }, [loaded, readOnly, annotationBounds]);
  useEffect(
    () => () => {
      clearTimeout(scrollSaveTimer.current);
      if (!restoreScroll.current) void persistView();
    },
    [storageKey],
  );
  useEffect(() => {
    if (loaded && !restoreScroll.current) void persistView();
  }, [loaded, view, storageKey]);
  useEffect(() => {
    if (!loaded) return;
    onRevision(board.revision);
    onStatus("Saving…");
    const value = board;
    const timer = setTimeout(() => {
      saveBoard(storageKey, value)
        .then(() => onStatus("Saved on this device"))
        .catch(() => onStatus("Save failed · export your work"));
    }, 250);
    return () => {
      clearTimeout(timer);
      void saveBoard(storageKey, value).catch(() => {});
    };
  }, [board, loaded, storageKey, onRevision, onStatus]);
  useEffect(() => {
    if (!loaded || readOnly) return;
    let cancelled = false,
      idle: number | undefined;
    const timer = setTimeout(() => {
      const work = () => {
        if (!cancelled && pointer.current === null)
          void preparation.current.get(board).catch(() => {});
      };
      if ("requestIdleCallback" in window)
        idle = window.requestIdleCallback(work, { timeout: 2000 });
      else work();
    }, 1100);
    return () => {
      cancelled = true;
      clearTimeout(timer);
      if (idle !== undefined) window.cancelIdleCallback(idle);
    };
  }, [board, loaded, readOnly]);
  useEffect(() => {
    if (!loaded || !allowReview) return;
    let cancelled = false;
    const source = current.current;
    void loadReview(storageKey)
      .then(async (review) => {
        if (!review?.source || source.revision !== review.revision) return;
        const hash = await contentHash(source);
        if (
          !cancelled &&
          current.current === source &&
          review.source.hash === hash
        )
          setSavedFeedback(review);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [storageKey, loaded, allowReview]);
  useEffect(() => {
    if (!feedback?.source || feedback.revision !== current.current.revision)
      return;
    setSavedFeedback(feedback);
    setShowNotes(true);
    const scale = svg.current?.getScreenCTM()?.a ?? 0.5;
    setNoteFont(Math.max(20, Math.min(100, 18 / Math.abs(scale || 0.5))));
    void saveReview(storageKey, feedback).catch(() => {});
  }, [feedback, storageKey]);
  const onAnnotationLayout = useCallback(
    (items: PlacedAnnotation[], bounds: Rect) => {
      setAnnotationBounds(bounds);
    },
    [],
  );
  const review = allowReview ? (feedback ?? savedFeedback) : null;
  useEffect(() => {
    if (!review) return;
    const scale = svg.current?.getScreenCTM()?.a ?? 0.5;
    setNoteFont(Math.max(20, Math.min(100, 18 / Math.abs(scale || 0.5))));
  }, [review, readOnly]);
  function commit(next: Board) {
    undo.current.push(current.current);
    if (undo.current.length > 50) undo.current.shift();
    redo.current = [];
    const value = { ...next, revision: current.current.revision + 1 };
    current.current = value;
    setBoard(value);
    setVersion((v) => v + 1);
  }
  function history(direction: "undo" | "redo") {
    if (locked.current) return;
    const source = direction === "undo" ? undo : redo,
      dest = direction === "undo" ? redo : undo;
    const next = source.current.pop();
    if (next) {
      dest.current.push(current.current);
      const value = { ...next, revision: current.current.revision + 1 };
      current.current = value;
      setBoard(value);
      setVersion((v) => v + 1);
    }
  }
  function point(
    e: Pick<PointerEvent, "clientX" | "clientY" | "pressure" | "pointerType">,
    bounded = true,
  ): Point {
    const m = svg.current!.getScreenCTM();
    if (!m) return [0, 0, 0.5];
    const inv = m.inverse();
    const x = inv.a * e.clientX + inv.c * e.clientY + inv.e,
      y = inv.b * e.clientX + inv.d * e.clientY + inv.f;
    const pressure =
      e.pointerType === "pen" && e.pressure > 0 ? e.pressure : 0.5;
    return bounded ? boundedPoint(x, y, pressure) : [x, y, pressure];
  }
  // Use the actual input, so a tablet with a mouse still gets precise desktop ink.
  function radius(pointerType: string) {
    const m = svg.current?.getScreenCTM();
    return screenEraserRadius(
      pointerType === "mouse" ? 8 : 12,
      m ? Math.hypot(m.a, m.b) : 1,
    );
  }
  function showCursor(e: React.PointerEvent<SVGSVGElement>) {
    const cursor = eraserCursor.current;
    if (!cursor) return;
    if (tool !== "eraser" || readOnly) {
      cursor.setAttribute("visibility", "hidden");
      return;
    }
    const p = point(e, false);
    cursor.setAttribute("cx", String(p[0]));
    cursor.setAttribute("cy", String(p[1]));
    cursor.setAttribute(
      "r",
      String(eraseRef.current?.radius ?? radius(e.pointerType)),
    );
    cursor.setAttribute("visibility", "visible");
  }
  function eraseTo(p: Point) {
    const g = eraseRef.current;
    if (!g) return;
    try {
      const strokes = eraseInk(g.strokes, g.last, p, g.radius);
      g.last = p;
      if (strokes !== g.strokes) {
        g.strokes = strokes;
        setErasing(strokes);
      }
    } catch {
      setError(
        "That erase could not be completed. Your existing ink is safe; try a smaller drag.",
      );
    }
  }
  function finish(save: boolean) {
    if (
      save &&
      eraseRef.current &&
      eraseRef.current.strokes !== current.current.strokes
    )
      commit({ ...current.current, strokes: eraseRef.current.strokes });
    else if (save && strokeRef.current)
      commit({
        ...current.current,
        strokes: [...current.current.strokes, strokeRef.current],
      });
    eraseRef.current = null;
    setErasing(null);
    strokeRef.current = null;
    setActive(null);
    pointer.current = null;
    pan.current = null;
  }
  useEffect(() => {
    if (readOnly) finish(false);
  }, [readOnly]);
  function selectTool(next: typeof tool) {
    finish(true);
    setTool(next);
    eraserCursor.current?.setAttribute("visibility", "hidden");
  }
  function shortcuts(e: React.KeyboardEvent<HTMLDivElement>) {
    const target = e.target as HTMLElement;
    if (
      readOnly ||
      pointer.current !== null ||
      target.closest('input,textarea,select,[contenteditable="true"]')
    )
      return;
    const key = e.key.toLowerCase();
    if ((e.ctrlKey || e.metaKey) && !e.altKey) {
      if (key === "z" || key === "y") {
        e.preventDefault();
        history(key === "y" || e.shiftKey ? "redo" : "undo");
      }
      return;
    }
    if (e.altKey || e.ctrlKey || e.metaKey) return;
    if (key === "p" || key === "e" || key === "h") {
      e.preventDefault();
      selectTool(key === "p" ? "pen" : key === "e" ? "eraser" : "hand");
    }
  }
  function down(e: React.PointerEvent<SVGSVGElement>) {
    if (
      (locked.current && tool !== "hand") ||
      !loaded ||
      pointer.current !== null ||
      e.button !== 0
    )
      return;
    if (penOnly && e.pointerType === "touch" && tool !== "hand") return;
    const raw = point(e, false);
    if (
      tool !== "hand" &&
      (raw[0] < 0 || raw[1] < 0 || raw[0] > WIDTH || raw[1] > HEIGHT)
    )
      return;
    e.preventDefault();
    e.currentTarget.focus({ preventScroll: true });
    pointer.current = e.pointerId;
    e.currentTarget.setPointerCapture(e.pointerId);
    if (tool === "hand") {
      pan.current = {
        x: e.clientX,
        y: e.clientY,
        vx: readOnly ? wrap.current!.scrollLeft : view.x,
        vy: readOnly ? wrap.current!.scrollTop : view.y,
      };
      return;
    }
    const p = point(e);
    if (tool === "eraser") {
      eraseRef.current = {
        strokes: current.current.strokes,
        last: p,
        radius: radius(e.pointerType),
      };
      setErasing(current.current.strokes);
      eraseTo(p);
      showCursor(e);
      return;
    }
    const s: Stroke = {
      id: crypto.randomUUID(),
      points: [p],
      color: tool === "highlighter" ? "#ffd166" : color,
      size: tool === "highlighter" ? 24 : 3.8,
      tool,
      renderVersion: 2,
    };
    strokeRef.current = s;
    setActive(s);
  }
  function move(e: React.PointerEvent<SVGSVGElement>) {
    showCursor(e);
    if (pointer.current !== e.pointerId) return;
    if (pan.current && svg.current) {
      if (readOnly && wrap.current) {
        wrap.current.scrollLeft = pan.current.vx - (e.clientX - pan.current.x);
        wrap.current.scrollTop = pan.current.vy - (e.clientY - pan.current.y);
        return;
      }
      const m = svg.current.getScreenCTM();
      const scale = m ? Math.hypot(m.a, m.b) : 1;
      setView({
        ...view,
        x: pan.current.vx - (e.clientX - pan.current.x) / scale,
        y: pan.current.vy - (e.clientY - pan.current.y) / scale,
      });
      return;
    }
    const coalesced = e.nativeEvent.getCoalescedEvents?.() ?? [];
    const events = coalesced.length ? coalesced : [e.nativeEvent];
    if (eraseRef.current) {
      for (const sample of events) eraseTo(point(sample, false));
      return;
    }
    if (!strokeRef.current) return;
    const s = {
      ...strokeRef.current,
      points: [
        ...strokeRef.current.points,
        ...events.map((sample) => point(sample)),
      ],
    };
    strokeRef.current = s;
    setActive(s);
  }
  function up(e: React.PointerEvent<SVGSVGElement>) {
    if (pointer.current !== e.pointerId) return;
    if (eraseRef.current) eraseTo(point(e, false));
    else if (strokeRef.current) {
      const p = point(e);
      p[2] = strokeRef.current.points.at(-1)![2];
      strokeRef.current = {
        ...strokeRef.current,
        points: [...strokeRef.current.points, p],
      };
    }
    finish(!readOnly);
    if (e.currentTarget.hasPointerCapture(e.pointerId))
      e.currentTarget.releasePointerCapture(e.pointerId);
  }
  function cancel(e: React.PointerEvent<SVGSVGElement>) {
    if (pointer.current !== e.pointerId) return;
    finish(false);
    if (e.currentTarget.hasPointerCapture(e.pointerId))
      e.currentTarget.releasePointerCapture(e.pointerId);
    eraserCursor.current?.setAttribute("visibility", "hidden");
  }
  useImperativeHandle(
    ref,
    () => ({
      hasWork: () =>
        !!(
          strokeRef.current ||
          current.current.strokes.length ||
          current.current.photo ||
          current.current.note.trim()
        ),
      isCurrent: (snapshot) =>
        current.current === snapshot.board &&
        !strokeRef.current &&
        !eraseRef.current &&
        !photoPending.current,
      releaseUnsubmitted: () => {
        locked.current = false;
        setFrozen(false);
      },
      freeze: async () => {
        if (photoPending.current)
          throw Error("Wait for the photo to finish loading, then submit.");
        finish(true);
        locked.current = true;
        setFrozen(true);
        try {
          return await preparation.current.get(current.current);
        } catch (e) {
          locked.current = false;
          setFrozen(false);
          throw e;
        }
      },
      snapshot: async () => {
        if (photoPending.current)
          throw new Error(
            "Your photo is still being prepared. Submit once it appears on the board.",
          );
        finish(true);
        return preparation.current.get(current.current);
      },
    }),
    [],
  );
  async function upload(file?: File) {
    if (!file || locked.current) return;
    const generation = ++photoGeneration.current;
    photoPending.current = true;
    try {
      const photo = await preparePhoto(file);
      if (generation !== photoGeneration.current || locked.current) return;
      commit({ ...current.current, photo });
      setError("");
    } catch (e) {
      if (generation === photoGeneration.current)
        setError((e as Error).message);
    } finally {
      if (generation === photoGeneration.current) photoPending.current = false;
    }
  }
  async function download() {
    try {
      const a = document.createElement("a");
      a.href = await boardImage(current.current);
      a.download = "thriving-scholars-working.jpg";
      a.click();
    } catch {
      setError("Could not export. Please try again.");
    }
  }
  const visible =
    !!review &&
    review.revision === board.revision &&
    !active &&
    !erasing &&
    !checking &&
    showNotes;
  const paperX = Math.min(0, annotationBounds.x),
    paperY = Math.min(0, annotationBounds.y);
  const paperWidth =
    Math.max(WIDTH, annotationBounds.x + annotationBounds.w) - paperX;
  const paperHeight =
    Math.max(
      HEIGHT,
      visible ? annotationBounds.y + annotationBounds.h + 40 : HEIGHT,
    ) - paperY;
  const displayedStrokes = erasing ?? board.strokes;
  const blank = !displayedStrokes.length && !board.photo && !active && !visible;
  return (
    <div className="ink-workspace" onKeyDown={shortcuts}>
      <div className="board-tools">
        <div className="tool-group">
          {(
            [
              { id: "pen", label: "Pen (P)", Icon: PenLine },
              { id: "highlighter", label: "Highlighter", Icon: Highlighter },
              { id: "eraser", label: "Eraser (E)", Icon: Eraser },
              { id: "hand", label: "Pan (H)", Icon: Hand },
            ] as const
          ).map(({ id, label, Icon }) => (
            <button
              key={id}
              title={label}
              aria-label={label}
              aria-pressed={tool === id}
              className={tool === id ? "tool active" : "tool"}
              onClick={() => selectTool(id)}
              disabled={readOnly && id !== "hand"}
            >
              <Icon size={18} />
            </button>
          ))}
        </div>
        <div className="tool-group colors">
          {["#172033", "#0b3a78", "#7d1108", "#287464"].map((c) => (
            <button
              key={c}
              aria-label={`Ink ${c}`}
              title={`Ink ${c}`}
              className={color === c ? "swatch selected" : "swatch"}
              style={{ background: c }}
              onClick={() => {
                setColor(c);
                selectTool("pen");
              }}
              disabled={readOnly}
            />
          ))}
        </div>
        <div className="tool-group">
          <button
            className="tool"
            title="Undo"
            aria-label="Undo"
            disabled={readOnly || !undo.current.length}
            onClick={() => history("undo")}
          >
            <Undo2 size={18} />
          </button>
          <button
            className="tool"
            title="Redo"
            aria-label="Redo"
            disabled={readOnly || !redo.current.length}
            onClick={() => history("redo")}
          >
            <Redo2 size={18} />
          </button>
        </div>
        <button
          className="upload-tool"
          onClick={() => input.current?.click()}
          disabled={readOnly}
        >
          <ImagePlus size={17} />
          <span>Add photo</span>
        </button>
        <input
          ref={input}
          hidden
          type="file"
          disabled={readOnly}
          accept="image/jpeg,image/png,image/webp"
          onChange={(e) => {
            void upload(e.target.files?.[0]);
            e.target.value = "";
          }}
        />
        <div className="board-tools-end">
          <label className="pen-toggle">
            <input
              type="checkbox"
              checked={penOnly}
              onChange={(e) => setPenOnly(e.target.checked)}
            />
            Stylus only
          </label>
          <button
            className="tool"
            aria-label="Export original working"
            title="Export original working"
            onClick={download}
          >
            <Download size={17} />
          </button>
          <button
            className="tool"
            aria-label="Clear board"
            title="Clear board"
            onClick={() => setClearOpen(true)}
            disabled={readOnly || blank}
          >
            <Trash2 size={17} />
          </button>
        </div>
      </div>
      <div className="board-review-status" role="status" aria-live="polite">
        {checking ? (
          <span className="reviewing-indicator">
            <i aria-hidden="true" />
            {reviewStage === "queued"
              ? "Waiting for the current review…"
              : reviewStage === "preparing"
                ? "Preparing your complete working…"
                : "Reviewing your complete working…"}
          </span>
        ) : reviewError ? (
          <span className="review-error">{studentErrorMessage(reviewError)}</span>
        ) : review && review.revision !== board.revision ? (
          <span>Working changed · submit again for updated notes.</span>
        ) : (
          review && (
            <>
              <button type="button" onClick={() => setShowNotes((v) => !v)}>
                {showNotes ? "Hide notes" : "Show notes"}
              </button>
              {showNotes && (
                <span className="annotation-legend">
                  <i className="red" />
                  Corrections <i className="blue" />
                  Checks · scroll for feedback
                </span>
              )}
            </>
          )
        )}
      </div>
      {error && (
        <div role="alert" className="inline-error">
          {studentErrorMessage(error)}
        </div>
      )}
      <div className="canvas-stage">
        <div
          ref={wrap}
          className={`canvas-wrap ${readOnly ? "review-scroll" : ""}`}
          onScroll={(e) => {
            if (!restoreScroll.current) {
              scrollPosition.current = {
                top: e.currentTarget.scrollTop,
                left: e.currentTarget.scrollLeft,
              };
              clearTimeout(scrollSaveTimer.current);
              scrollSaveTimer.current = setTimeout(
                () => void persistView(),
                200,
              );
            }
          }}
          aria-label={
            readOnly ? "Submitted pad, scroll to read feedback" : undefined
          }
        >
          <svg
            ref={svg}
            className={`ink-canvas ${tool} ${readOnly ? "read-only" : ""}`}
            viewBox={
              readOnly
                ? `${paperX} ${paperY} ${paperWidth} ${paperHeight}`
                : `${view.x} ${view.y} ${view.w} ${view.h}`
            }
            style={
              readOnly
                ? {
                    position: "relative",
                    width: `${(paperWidth / view.w) * 100}%`,
                    height: "auto",
                    aspectRatio: `${paperWidth} / ${paperHeight}`,
                  }
                : undefined
            }
            onPointerDown={down}
            onPointerMove={move}
            onPointerUp={up}
            onPointerCancel={cancel}
            onLostPointerCapture={cancel}
            onPointerLeave={() =>
              eraserCursor.current?.setAttribute("visibility", "hidden")
            }
            tabIndex={0}
            aria-label="Your writing canvas. Use a stylus, mouse or touch. You can also type your working below."
            role="group"
          >
            <defs>
              <pattern
                id="dots"
                width="24"
                height="24"
                patternUnits="userSpaceOnUse"
              >
                <circle cx="1" cy="1" r="1" fill="#d9dde4" />
              </pattern>
            </defs>
            <rect
              x="-5000"
              y="-5000"
              width="11000"
              height="11000"
              fill="#f9fafb"
            />
            <rect
              x={Math.min(0, annotationBounds.x)}
              y={Math.min(0, annotationBounds.y)}
              width={
                Math.max(WIDTH, annotationBounds.x + annotationBounds.w) -
                Math.min(0, annotationBounds.x)
              }
              height={
                Math.max(HEIGHT, annotationBounds.y + annotationBounds.h) -
                Math.min(0, annotationBounds.y)
              }
              fill="white"
            />
            <rect
              width={Math.max(WIDTH, annotationBounds.x + annotationBounds.w)}
              height={Math.max(HEIGHT, annotationBounds.y + annotationBounds.h)}
              fill="url(#dots)"
            />
            {board.photo && (
              <image
                href={board.photo.data}
                x={board.photo.x}
                y={board.photo.y}
                width={board.photo.w}
                height={board.photo.h}
                transform={`rotate(${board.photo.rotation} ${board.photo.x + board.photo.w / 2} ${board.photo.y + board.photo.h / 2})`}
              />
            )}
            {[...displayedStrokes, ...(active ? [active] : [])].map((s) => (
              <InkStroke key={s.id} stroke={s} />
            ))}
            {visible && review && (
              <BoardAnnotations
                key={`${review.source?.hash ?? review.revision}:${review.reviewId ?? ""}`}
                feedback={review}
                board={board}
                fontSize={noteFont}
                onLayout={onAnnotationLayout}
                animate={animateFeedback}
                reviewKey={storageKey}
                onSelect={setSelectedAnnotation}
                selectedId={selectedAnnotation?.id}
              />
            )}
            <circle
              ref={eraserCursor}
              className="eraser-cursor"
              cx="0"
              cy="0"
              r="0"
              visibility="hidden"
              pointerEvents="none"
              vectorEffect="non-scaling-stroke"
            />
          </svg>
          {blank && (
            <div className="canvas-placeholder">
              <div className="placeholder-pen">
                <PenLine size={28} />
              </div>
              <h3>A little working goes a long way.</h3>
              <p>
                Write here with your pen, or add a photo
                <br />
                of your working to get started.
              </p>
              <span>YOUR SPACE TO THINK</span>
            </div>
          )}
          <div className="canvas-caption">
            {readOnly ? "Submitted working" : "Your working"}
            <span>•</span>
            {board.strokes.length} strokes
          </div>
          <div className="zoom-tools">
            <button
              aria-label="Zoom out"
              onClick={() =>
                setView((v) => ({
                  ...v,
                  w: Math.min(WIDTH * 2, v.w * 1.2),
                  h: Math.min(HEIGHT * 2, v.h * 1.2),
                }))
              }
            >
              <ZoomOut size={16} />
            </button>
            <span>{Math.round((WIDTH / view.w) * 100)}%</span>
            <button
              aria-label="Zoom in"
              onClick={() =>
                setView((v) => ({
                  ...v,
                  w: Math.max(300, v.w / 1.2),
                  h: Math.max(225, v.h / 1.2),
                }))
              }
            >
              <ZoomIn size={16} />
            </button>
            <button
              aria-label="Fit page"
              onClick={() => setView({ x: 0, y: 0, w: WIDTH, h: HEIGHT })}
            >
              <Maximize size={15} />
            </button>
            {board.photo && (
              <button
                aria-label="Rotate photo"
                title="Rotate photo"
                disabled={readOnly}
                onClick={() =>
                  commit({
                    ...board,
                    photo: {
                      ...board.photo!,
                      rotation: (board.photo!.rotation + 90) % 360,
                    },
                  })
                }
              >
                <RotateCw size={16} />
              </button>
            )}
          </div>
        </div>
        {visible && selectedAnnotation && (
          <FeedbackDetail
            key={selectedAnnotation.id}
            annotation={selectedAnnotation}
            board={board}
            onClose={closeDetail}
            onClarify={onClarify}
            busy={checking}
          />
        )}
      </div>
      <div
        className={`typed-working ${readOnly ? "submitted-typed" : ""} ${readOnly && visible ? "source-on-board" : ""}`}
      >
        <label htmlFor={`notes-${storageKey}`}>Prefer to type?</label>
        <textarea
          id={`notes-${storageKey}`}
          placeholder="Add equations or explain a step…"
          value={board.note}
          disabled={readOnly}
          maxLength={5000}
          onChange={(e) => {
            if (locked.current) return;
            const next = {
              ...current.current,
              note: e.target.value,
              revision: current.current.revision + 1,
            };
            current.current = next;
            setBoard(next);
          }}
        />
        {board.note.trim() && (
          <details className="typed-preview">
            <summary>Preview maths · use \( \) for equations</summary>
            <MathText text={board.note} inline={false} />
          </details>
        )}
      </div>
      {clearOpen && (
        <div className="modal-backdrop">
          <section
            role="dialog"
            aria-modal="true"
            aria-labelledby="clear-title"
            className="dialog"
          >
            <h2 id="clear-title">Clear this page?</h2>
            <p>
              This removes your pen strokes, photo and typed working. You can
              undo it while this page is open.
            </p>
            <div className="dialog-actions">
              <button className="secondary" onClick={() => setClearOpen(false)}>
                Keep working
              </button>
              <button
                className="primary"
                onClick={() => {
                  photoGeneration.current++;
                  photoPending.current = false;
                  commit(emptyBoard());
                  setClearOpen(false);
                }}
              >
                Clear page
              </button>
            </div>
          </section>
        </div>
      )}
    </div>
  );
});
