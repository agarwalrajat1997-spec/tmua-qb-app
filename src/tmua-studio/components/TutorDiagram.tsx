import { useId } from "react";
import type { TutorVisual } from "../lib/tutor-visual";
import { plotCurve } from "../lib/tutor-visual";
import { MathText } from "./MathHtml";

export function TutorDiagram({ visual: v }: { visual: TutorVisual }) {
  const id = useId();
  const x = (n: number) => 24 + ((n - v.xMin) / (v.xMax - v.xMin)) * 352;
  const y = (n: number) => 224 - ((n - v.yMin) / (v.yMax - v.yMin)) * 200;
  return (
    <svg
      className="tutor-diagram"
      viewBox="0 0 400 260"
      role="img"
      aria-labelledby={id}
    >
      <title id={id}>
        {v.title}. {v.caption}
      </title>
      {v.axes && (
        <g stroke="currentColor" strokeWidth="1" opacity=".6">
          {v.yMin <= 0 && v.yMax >= 0 && <path d={`M24,${y(0)}H376`} />}
          {v.xMin <= 0 && v.xMax >= 0 && <path d={`M${x(0)},24V224`} />}
        </g>
      )}
      {v.curves.map((c, i) => (
        <path
          key={`curve-${i}`}
          d={plotCurve(c.coefficients, v)}
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
        />
      ))}
      {v.segments.map((s, i) => (
        <path
          key={`segment-${i}`}
          d={`M${x(s.from.x)},${y(s.from.y)}L${x(s.to.x)},${y(s.to.y)}`}
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeDasharray={s.dashed ? "5 4" : undefined}
        />
      ))}
      {v.labels.map((l, i) => (
        <foreignObject
          key={`label-${i}`}
          x={Math.min(280, Math.max(0, x(l.at.x) - 10))}
          y={Math.min(230, Math.max(0, y(l.at.y) - 24))}
          width="120"
          height="50"
          overflow="visible"
        >
          <div style={{ fontSize: 22 }}>
            <MathText text={l.text} />
          </div>
        </foreignObject>
      ))}
    </svg>
  );
}
