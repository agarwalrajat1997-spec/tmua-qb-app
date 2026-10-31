import Link from "next/link";
import { IB_MATH_SUBJECTS, ibMathCourseHref, type IbMathSubject } from "@/lib/ib/catalog";
import styles from "../ib.module.css";

export default function MathsCourseSwitch({ subject, topicId, links }: { subject: IbMathSubject; topicId?: string; links?: Record<IbMathSubject, string> }) {
  return <div className={`${styles.chemistryCourse} ${styles.mathsCourse}`}>
    <div><span className={styles.eyebrow}>MATHEMATICS COURSE</span><p>Choose the course you study</p></div>
    <nav aria-label="Mathematics course" className={`${styles.courseSwitch} ${styles.mathsCourseSwitch}`}>
      {IB_MATH_SUBJECTS.map(id => <Link key={id} href={links?.[id] ?? ibMathCourseHref(id, topicId)} prefetch={false} aria-current={id === subject ? "page" : undefined}>
        <strong>{id.startsWith("math-ai-") ? "AI" : "AA"} {id.endsWith("-sl") ? "SL" : "HL"}</strong>
        <span>{id.startsWith("math-ai-") ? "Applications & Interpretation" : "Analysis & Approaches"}</span>
      </Link>)}
    </nav>
  </div>;
}
