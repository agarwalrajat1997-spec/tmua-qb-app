import { memo, useEffect, useRef, useState } from "react";
import DOMPurify from "dompurify";
import { queueMath } from "../lib/mathjax";
import { revealMath } from "../lib/reveal-math";
export function escapeMathText(text: string) {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
// Escape AI/student text before MathJax; only curated question HTML is sanitized.
export const MathHtml = memo(function MathHtml({
  html,
  className = "",
  inline = false,
  onTypeset,
  reveal = false,
  revealAt = 0,
}: {
  html: string;
  className?: string;
  inline?: boolean;
  onTypeset?: () => void;
  reveal?: boolean;
  revealAt?: number;
}) {
  const ref = useRef<HTMLElement>(null);
  const [error, setError] = useState(false);
  useEffect(() => {
    let active = true;
    const node = ref.current;
    if (!node) return;
    const clean = DOMPurify.sanitize(html, {
      USE_PROFILES: { html: true },
      FORBID_TAGS: ["style", "iframe", "form", "input"],
      FORBID_ATTR: ["style"],
    });
    setError(false);
    void queueMath(async (math) => {
      if (!active) return;
      math.typesetClear([node]);
      if (reveal) node.dataset.revealPending = "true";
      node.innerHTML = clean;
      await math.typesetPromise([node]);
      if (active) {
        if (reveal) revealMath(node, revealAt);
        delete node.dataset.revealPending;
        onTypeset?.();
      }
    }).catch(() => {
      if (active) {
        node.innerHTML = clean;
        delete node.dataset.revealPending;
        setError(true);
      }
    });
    return () => {
      active = false;
      void queueMath((math) => math.typesetClear([node])).catch(() => {});
    };
  }, [html, onTypeset, reveal, revealAt]);
  const Tag = inline ? "span" : "div";
  return (
    <Tag
      ref={ref as never}
      className={`math-html ${className}`}
      data-math-error={error || undefined}
      title={
        error
          ? "Math formatting could not load; original notation is shown."
          : undefined
      }
    />
  );
});
export function MathText({
  text,
  className = "",
  inline = true,
  onTypeset,
  reveal = false,
}: {
  text: string;
  className?: string;
  inline?: boolean;
  onTypeset?: () => void;
  reveal?: boolean;
}) {
  return (
    <MathHtml
      html={escapeMathText(text).replaceAll("\n", "<br />")}
      inline={inline}
      className={className}
      onTypeset={onTypeset}
      reveal={reveal}
    />
  );
}
