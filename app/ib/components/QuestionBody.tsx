import type { IbQuestionPrompt } from "@/lib/ib/question";
import MathContent from "./MathContent";
import styles from "../questions.module.css";

export function QuestionDiagram({ svg, caption }: { svg?: string; caption: string }) {
  if (!svg) return null;
  // SVG loaded as an image is isolated from the page's DOM and script context.
  const src = `data:image/svg+xml;base64,${Buffer.from(svg).toString("base64")}`;
  return <figure className={styles.diagram}>
    {/* eslint-disable-next-line @next/next/no-img-element */}
    <img src={src} alt={caption} />
  </figure>;
}

export function QuestionBadges({ question: q }: { question: IbQuestionPrompt }) {
  return <div className={styles.badges}><span className={styles[q.difficulty]}>{q.difficulty}</span><span>{q.calculator ? "Calculator" : "No calculator"}</span><span>{q.marks} marks</span></div>;
}

export default function QuestionBody({ question: q }: { question: IbQuestionPrompt }) {
  return <div className={styles.questionBody}>
    <p className={styles.maximum}>[Maximum mark: {q.marks}]</p>
    <MathContent>{q.stem}</MathContent>
    <QuestionDiagram svg={q.diagramSvg} caption={`Diagram for question ${q.number}: ${q.title}`} />
    {q.parts.length ? <ol className={styles.parts}>{q.parts.map(part => <li key={part.label}>
      <span className={styles.partLabel}>({part.label})</span><MathContent>{part.prompt}</MathContent><span className={styles.partMarks}>[{part.marks}]</span>
    </li>)}</ol> : null}
  </div>;
}
