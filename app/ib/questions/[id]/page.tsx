import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { requireIbUser } from "@/lib/ib/auth";
import { ibHref, ibCourseLevel, ibCourseHref } from "@/lib/ib/catalog";
import { getIbQuestion } from "@/lib/ib/content";
import { getIbCollection, questionPrompt } from "@/lib/ib/question";
import ExamShell from "../../components/ExamShell";
import ExamInstructions from "../../components/ExamInstructions";
import QuestionBody, { QuestionBadges } from "../../components/QuestionBody";
import styles from "../../questions.module.css";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "IB Question | Thriving Scholars", robots: { index: false, follow: false } };
export default async function QuestionPage({ params, searchParams }: { params: Promise<{ id: string }>; searchParams?: Promise<Record<string, string | string[] | undefined>> }) {
  const [{ id }, raw] = await Promise.all([params, searchParams]);
  const courseLevel = ibCourseLevel(raw?.course);
  const pathname = `/ib/questions/${encodeURIComponent(id)}`;
  const user = await requireIbUser(ibCourseHref(pathname, id.startsWith("ib-chem-") ? "chemistry" : "math-aa-hl", courseLevel));
  const stored = getIbQuestion(id, courseLevel);
  if (!stored) notFound();
  const q = questionPrompt(stored);
  const collection = getIbCollection(q.collectionId)!;
  const bankPath = `/ib/question-bank/${collection.id}`;
  return <ExamShell email={user.email} subject={q.subject} courseLevel={courseLevel} courseLinks={{ sl: ibCourseHref(q.subject === "chemistry" && q.level === "ahl" ? bankPath : pathname, q.subject, "sl"), hl: ibCourseHref(pathname, q.subject, "hl") }}>
    <nav className={styles.breadcrumb} aria-label="Breadcrumb"><Link href={ibHref(q.subject, "questions", courseLevel)}>Question bank</Link><span>/</span><Link href={ibCourseHref(bankPath, q.subject, courseLevel)}>{collection.title}</Link><span>/</span><span>Question {q.number}</span></nav>
    <ExamInstructions subject={q.subject} />
    <article className={styles.questionCard}><header className={styles.questionHeader}><div><h1 className={styles.questionNumber}>Question {q.number}</h1><span className={styles.subtopic}>{q.subtopic}</span></div><QuestionBadges question={q} /></header><div className={styles.questionContent}><QuestionBody question={q} /><aside className={styles.questionActions}><Link href={ibCourseHref(`/ib/mark-scheme/${q.id}`, q.subject, courseLevel)} target="_blank" rel="noopener noreferrer" prefetch={false} className={styles.schemeButton}>Mark scheme ↗<span className={styles.srOnly}> (opens in a new tab)</span></Link><span>Written solution<br />with mark allocations</span></aside></div></article>
  </ExamShell>;
}
