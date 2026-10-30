import { safeDiagram, safeDiagramUrl, isScienceQuestion, type IbQuestionPrompt } from "@/lib/ib/question";
import { diagramUrlForSvg, diagramFallbackForUrl } from "@/lib/ib/diagram-assets";
import MathContent from "./MathContent";
import DiagramImage from "./DiagramImage";
import styles from "../questions.module.css";

export function QuestionDiagram({ svg, url, caption, credit }: { svg?: string; url?: string; caption: string; credit?: string }) {
  // SVG loaded as an image is isolated from the page's DOM and script context.
  const fallback = svg && safeDiagram(svg) ? `data:image/svg+xml;base64,${Buffer.from(svg).toString("base64")}` : diagramFallbackForUrl(url);
  const candidate = url || diagramUrlForSvg(svg);
  const src = candidate && safeDiagramUrl(candidate) ? candidate : fallback;
  if (!src) return null;
  return <figure className={styles.diagram}>
    <DiagramImage src={src} fallback={fallback} caption={caption} />
    {credit ? <figcaption>{credit}</figcaption> : null}
  </figure>;
}

export function QuestionBadges({ question: q }: { question: IbQuestionPrompt }) {
  const difficulty = { easy: { label: "Easy", bars: 1 }, medium: { label: "Medium", bars: 2 }, hard: { label: "Hard", bars: 3 } }[q.difficulty];
  return <div className={styles.badges}>
    <span className={`${styles.difficultyBadge} ${styles[q.difficulty]}`}><span className={styles.difficultyBars} aria-hidden="true">{[1, 2, 3].map(bar => <i key={bar} data-active={bar <= difficulty.bars ? "true" : "false"} />)}</span><span className={styles.srOnly}>Difficulty: </span>{difficulty.label}</span>
    {isScienceQuestion(q) ? <><span>{q.syllabusCode} · {q.level === "ahl" ? "Additional HL" : q.subject !== "physics-hl" ? "SL content" : "Core"}</span><span>{{ "multiple-choice": "Multiple choice", structured: "Structured", "data-based": "Data-based" }[q.questionType]}</span></> : q.examStyle ? <span>{{ "short-response": "Short response", "extended-response": "Extended response", "problem-solving": "Problem solving" }[q.examStyle]}</span> : null}
    <span>{q.calculator ? "Calculator" : "No calculator"}</span><span>{q.marks} {q.marks === 1 ? "mark" : "marks"}</span>
  </div>;
}

export default function QuestionBody({ question: q }: { question: IbQuestionPrompt }) {
  return <div className={styles.questionBody}>
    <p className={styles.maximum}>[Maximum mark: {q.marks}]</p>
    <MathContent>{q.stem}</MathContent>
    <QuestionDiagram svg={q.diagramSvg} url={q.diagramUrl} caption={`Diagram for question ${q.number}: ${q.title}`} credit={q.diagramCaption} />
    {isScienceQuestion(q) && q.questionType === "multiple-choice" ? <ol className={styles.options} aria-label="Multiple-choice options">{q.options?.map(option => <li key={option.label}><span className={styles.optionLabel}>{option.label}</span><MathContent>{option.text}</MathContent></li>)}</ol> : null}
    {q.parts.length ? <ol className={styles.parts}>{q.parts.map(part => <li key={part.label}>
      <span className={styles.partLabel}>({part.label})</span><MathContent>{part.prompt}</MathContent><span className={styles.partMarks}>[{part.marks}]</span>
    </li>)}</ol> : null}
  </div>;
}
