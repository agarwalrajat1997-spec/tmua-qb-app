import { useEffect, useRef, useState } from "react";
import { X } from "lucide-react";
import type { Annotation } from "../lib/annotations";
import type { Board } from "../types";
import { strokePath } from "../lib/ink";
import { MathText } from "./MathHtml";
import { TutorDiagram } from "./TutorDiagram";
import { studentErrorMessage } from "../lib/student-content";
export function FeedbackDetail({
  annotation: a,
  board,
  onClose,
  onClarify,
  busy,
}: {
  annotation: Annotation;
  board: Board;
  onClose: () => void;
  onClarify?: (regionIds: string[], text: string) => Promise<void>;
  busy?: boolean;
}) {
  const [text, setText] = useState(""),
    [error, setError] = useState("");
  const panel = useRef<HTMLElement>(null);
  useEffect(() => {
    const previous = document.activeElement;
    panel.current?.focus({ preventScroll: true });
    return () => {
      if (previous instanceof HTMLElement && previous.isConnected)
        previous.focus({ preventScroll: true });
    };
  }, []);
  useEffect(() => {
    const close = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        e.stopPropagation();
        onClose();
      }
    };
    document.addEventListener("keydown", close);
    return () => document.removeEventListener("keydown", close);
  }, [onClose]);
  const crop = a.sourceArea ?? a.anchor;
  return (
    <section
      ref={panel}
      tabIndex={-1}
      className={`feedback-detail ${a.color}`}
      aria-label="Focused feedback on your whiteboard"
      onPointerDown={(e) => e.stopPropagation()}
    >
      <button
        className="feedback-close"
        aria-label="Close enlarged feedback"
        onClick={onClose}
      >
        <X size={17} />
      </button>
      <strong>
        <MathText text={`${a.marker ? a.marker + ". " : ""}${a.title}`} />
      </strong>
      {a.status === "uncertain" && crop && (
        <svg
          className="clarification-crop"
          viewBox={`${crop.x - 12} ${crop.y - 12} ${crop.w + 24} ${crop.h + 24}`}
          role="img"
          aria-label="Original working in the unclear area"
        >
          <rect
            x={crop.x - 12}
            y={crop.y - 12}
            width={crop.w + 24}
            height={crop.h + 24}
            fill="white"
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
          {board.strokes.map((s) => (
            <path
              key={s.id}
              d={strokePath(s)}
              fill={s.color}
              opacity={s.tool === "highlighter" ? 0.3 : 1}
            />
          ))}
        </svg>
      )}
      <MathText text={a.text} inline={false} />
      {a.visual && <TutorDiagram visual={a.visual} />}
      {a.status === "uncertain" && onClarify && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (!text.trim() || busy) return;
            setError("");
            void onClarify(a.regionIds ?? [], text.trim())
              .then(onClose)
              .catch((e) => setError(e.message));
          }}
        >
          <label htmlFor={`clarify-${a.id}`}>
            What does your original working say here?
          </label>
          <textarea
            id={`clarify-${a.id}`}
            value={text}
            onChange={(e) => setText(e.target.value)}
            maxLength={700}
            disabled={busy}
            placeholder="For example: the exponent is 3, not 2."
          />
          <small>
            Your ink stays unchanged. The tutor will reassess the complete
            attempt with this clarification.
          </small>
          {error && <p role="alert">{studentErrorMessage(error)}</p>}
          <button
            className="primary"
            type="submit"
            disabled={busy || !text.trim()}
          >
            {busy ? "Reviewing…" : "Clarify & review"}
          </button>
        </form>
      )}
    </section>
  );
}
