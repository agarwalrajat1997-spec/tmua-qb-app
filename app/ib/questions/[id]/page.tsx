import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { requireIbUser } from "@/lib/ib/auth";
import { ibHref } from "@/lib/ib/catalog";
import { getIbQuestion } from "@/lib/ib/content";
import { getIbCollection, questionPrompt } from "@/lib/ib/question";
import ExamShell from "../../components/ExamShell";
import ExamInstructions from "../../components/ExamInstructions";
import QuestionBody, { QuestionBadges } from "../../components/QuestionBody";
import styles from "../../questions.module.css";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "IB HL Question | Thriving Scholars", robots: { index: false, follow: false } };
export default async function QuestionPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const user = await requireIbUser(`/ib/questions/${encodeURIComponent(id)}`);
  const stored = getIbQuestion(id);
  if (!stored) notFound();
  const q = questionPrompt(stored);
  const collection = getIbCollection(q.collectionId)!;
  return <ExamShell email={user.email} subject={q.subject}>
    <nav className={styles.breadcrumb} aria-label="Breadcrumb"><Link href={ibHref(q.subject)}>Question bank</Link><span>/</span><Link href={`/ib/question-bank/${collection.id}`}>{collection.title}</Link><span>/</span><span>Question {q.number}</span></nav>
    <ExamInstructions subject={q.subject} />
    <article className={styles.questionCard}><header className={styles.questionHeader}><div><h1 className={styles.questionNumber}>Question {q.number}</h1><span className={styles.subtopic}>{q.subtopic}</span></div><QuestionBadges question={q} /></header><div className={styles.questionContent}><QuestionBody question={q} /><aside className={styles.questionActions}><Link href={`/ib/mark-scheme/${q.id}`} target="_blank" rel="noopener noreferrer" prefetch={false} className={styles.schemeButton}>Mark scheme ↗<span className={styles.srOnly}> (opens in a new tab)</span></Link><span>Written solution<br />with mark allocations</span></aside></div></article>
  </ExamShell>;
}
