import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { requireIbUser } from "@/lib/ib/auth";
import { getIbQuestion } from "@/lib/ib/content";
import { getIbCollection, questionPrompt } from "@/lib/ib/question";
import ExamShell from "../../components/ExamShell";
import QuestionBody, { QuestionBadges, QuestionDiagram } from "../../components/QuestionBody";
import MathContent from "../../components/MathContent";
import PrintButton from "../../components/PrintButton";
import styles from "../../questions.module.css";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "IB Maths AA HL Mark Scheme | Thriving Scholars", robots: { index: false, follow: false } };
export default async function MarkScheme({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const user = await requireIbUser(`/ib/mark-scheme/${encodeURIComponent(id)}`);
  const q = getIbQuestion(id);
  if (!q) notFound();
  const collection = getIbCollection(q.collectionId)!;
  return <ExamShell email={user.email}>
    <div className={styles.schemeToolbar}><nav className={styles.breadcrumb} aria-label="Breadcrumb"><Link href={`/ib/question-bank/${collection.id}`}>{collection.title}</Link><span>/</span><span>Question {q.number}</span></nav><PrintButton /></div>
    <header className={styles.schemeTitle}><div><span className={styles.overline}>IB MATHS AA HL · {collection.title.toUpperCase()}</span><h1>Question {q.number} — Mark scheme</h1></div><QuestionBadges question={questionPrompt(q)} /></header>
    <div className={styles.schemeColumns}>
      <section className={styles.schemeQuestion}><h2>Question</h2><QuestionBody question={questionPrompt(q)} /></section>
      <section className={styles.schemeSolution}><h2>Worked solution & mark allocation</h2>
        <div className={styles.markLegend}><span><b>M</b> Method</span><span><b>A</b> Accuracy</span><span><b>R</b> Reasoning</span></div>
        {q.markScheme.map(group => <section className={styles.schemePart} key={group.part || "whole"}>
          {group.part ? <h3>Part ({group.part})<span>[{q.parts.find(p => p.label === group.part)?.marks} marks]</span></h3> : null}
          <ol className={styles.markSteps}>{group.steps.map((step, index) => <li key={index}><MathContent>{step.text}</MathContent><strong className={styles.markCode}>{step.code}</strong></li>)}</ol>
        </section>)}
        <QuestionDiagram svg={q.markSchemeDiagramSvg} caption={`Worked solution diagram for question ${q.number}`} />
        <div className={styles.schemeTotal}>Total <strong>{q.marks} marks</strong></div>
        <p className={styles.markNote}>Accept equivalent exact forms and valid alternative methods unless a method is specified. Accuracy marks depend on the relevant method where indicated. Follow-through is awarded only where stated. AG indicates an answer given in the question and earns no marks.</p>
      </section>
    </div>
  </ExamShell>;
}
