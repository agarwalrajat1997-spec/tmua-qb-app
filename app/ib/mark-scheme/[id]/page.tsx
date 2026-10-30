import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { requireIbUser } from "@/lib/ib/auth";
import { ibHref, ibSubjectForPath, ibCourseLevel, ibCourseHref, ibCourseLabel } from "@/lib/ib/catalog";
import { getIbQuestion } from "@/lib/ib/content";
import { getIbCollection, questionPrompt, isScienceQuestion } from "@/lib/ib/question";
import ExamShell from "../../components/ExamShell";
import QuestionBody, { QuestionBadges, QuestionDiagram } from "../../components/QuestionBody";
import MathContent from "../../components/MathContent";
import PrintButton from "../../components/PrintButton";
import styles from "../../questions.module.css";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "IB Mark Scheme | Thriving Scholars", robots: { index: false, follow: false } };
export default async function MarkScheme({ params, searchParams }: { params: Promise<{ id: string }>; searchParams?: Promise<Record<string, string | string[] | undefined>> }) {
  const [{ id }, raw] = await Promise.all([params, searchParams]);
  const courseLevel = ibCourseLevel(raw?.course);
  const pathname = `/ib/mark-scheme/${encodeURIComponent(id)}`;
  const user = await requireIbUser(ibCourseHref(pathname, ibSubjectForPath(pathname), courseLevel));
  const q = getIbQuestion(id, courseLevel);
  if (!q) notFound();
  const collection = getIbCollection(q.collectionId)!;
  const bankPath = `/ib/question-bank/${collection.id}`;
  return <ExamShell email={user.email} subject={q.subject} courseLevel={courseLevel} mathsTopicId={q.topicId} courseLinks={{ sl: ibCourseHref((q.subject === "chemistry" || q.subject === "biology") && q.level === "ahl" ? bankPath : pathname, q.subject, "sl"), hl: ibCourseHref(pathname, q.subject, "hl") }}>
    <div className={styles.schemeToolbar}><nav className={styles.breadcrumb} aria-label="Breadcrumb"><Link href={ibHref(q.subject, "questions", courseLevel)}>Question bank</Link><span>/</span><Link href={ibCourseHref(bankPath, q.subject, courseLevel)}>{collection.title}</Link><span>/</span><Link href={ibCourseHref(`/ib/questions/${q.id}`, q.subject, courseLevel)}>Question {q.number}</Link></nav><PrintButton /></div>
    <header className={styles.schemeTitle}><div><span className={styles.overline}>IB {ibCourseLabel(q.subject, courseLevel).toUpperCase()} · {collection.title.toUpperCase()}</span><h1>Question {q.number} — Mark scheme</h1></div><QuestionBadges question={questionPrompt(q)} /></header>
    <div className={styles.schemeColumns}>
      <section className={styles.schemeQuestion}><h2>Question</h2><QuestionBody question={questionPrompt(q)} /></section>
      <section className={styles.schemeSolution}><h2>Worked solution & mark allocation</h2>
        <div className={styles.markLegend}><span><b>M</b> Method</span><span><b>A</b> Accuracy</span><span><b>R</b> Reasoning</span></div>
        {q.markScheme.map(group => <section className={styles.schemePart} key={group.part || "whole"}>
          {group.part ? <h3>Part ({group.part})<span>[{q.parts.find(p => p.label === group.part)?.marks} {q.parts.find(p => p.label === group.part)?.marks === 1 ? "mark" : "marks"}]</span></h3> : null}
          <ol className={styles.markSteps}>{group.steps.map((step, index) => <li key={index}><MathContent>{step.text}</MathContent><strong className={styles.markCode}>{step.code}</strong></li>)}</ol>
        </section>)}
        <QuestionDiagram svg={q.markSchemeDiagramSvg} url={q.markSchemeDiagramUrl} caption={`Worked solution diagram for question ${q.number}`} credit={q.markSchemeDiagramCaption} />
        <div className={styles.schemeTotal}>Total <strong>{q.marks} {q.marks === 1 ? "mark" : "marks"}</strong></div>
        <p className={styles.markNote}>{isScienceQuestion(q)
          ? q.questionType === "multiple-choice" ? `Award one mark for the correct option. The explanation develops the ${q.subject === "biology" ? "biology" : q.subject === "chemistry" ? "chemistry" : "physics"} behind the choice and does not earn additional marks.`
            : `Accept equivalent ${q.subject === "biology" ? "biological" : q.subject === "chemistry" ? "chemical" : "physics"} reasoning and valid alternative methods unless a method is specified. Award the separate marking points up to the stated maximum. Apply error carried forward, unit requirements and significant-figure penalties only where the individual marking note states them.`
          : "Accept equivalent exact forms and valid alternative methods unless a method is specified. Accuracy marks depend on the relevant method where indicated. Follow-through is awarded only where stated. AG indicates an answer given in the question and earns no marks."}</p>
      </section>
    </div>
  </ExamShell>;
}
