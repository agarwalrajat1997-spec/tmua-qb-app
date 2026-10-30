import type { ReactNode } from "react";
import Link from "next/link";
import { IB_COURSES, ibHasCourseChoice, ibHref, ibCourseLabel, type IbCourseLevel, type IbSubject } from "@/lib/ib/catalog";
import ChemistryCourseSwitch, { type ChemistryCourseLinks } from "./ChemistryCourseSwitch";
import IbBrand from "../IbBrand";
import portal from "../ib.module.css";
import styles from "../questions.module.css";

export default function ExamShell({ children, email, subject, courseLevel = "hl", courseLinks }: { children: ReactNode; email: string; subject: IbSubject; courseLevel?: IbCourseLevel; courseLinks?: ChemistryCourseLinks }) {
  const portalHref = ibHref(subject, "questions", courseLevel);
  return <div className={`${portal.app} ${styles.examApp}`}>
    <a href="#ib-question-content" className={portal.skipLink}>Skip to questions</a>
    <header className={portal.topbar}><Link href={portalHref} className={portal.brandLink} aria-label="Thriving Scholars IB home"><IbBrand /></Link><div className={portal.account}><span className={portal.email}>{email}</span><Link className={portal.logout} href={portalHref}>My portal ↗</Link></div></header>
    <div className={styles.subjectBar}><nav aria-label="Subject">{(Object.keys(IB_COURSES) as IbSubject[]).map(id => <Link key={id} href={ibHref(id, "questions", courseLevel)} aria-current={subject === id ? "page" : undefined}><span aria-hidden="true">{IB_COURSES[id].symbol} &nbsp;</span> {IB_COURSES[id].label}</Link>)}</nav><span>WRITTEN QUESTIONS & MARK SCHEMES</span></div>
    <main id="ib-question-content" className={styles.examMain}>{ibHasCourseChoice(subject) ? <ChemistryCourseSwitch subject={subject} course={courseLevel} links={courseLinks ?? { sl: ibHref(subject, "questions", "sl"), hl: ibHref(subject, "questions", "hl") }} /> : null}{children}</main>
    <footer className={styles.examFooter}><strong>THRIVING SCHOLARS</strong><span>Independent practice material · {ibCourseLabel(subject, courseLevel)}</span></footer>
  </div>;
}
