import type { ReactNode } from "react";
import Link from "next/link";
import IbBrand from "../IbBrand";
import portal from "../ib.module.css";
import styles from "../questions.module.css";

export default function ExamShell({ children, email }: { children: ReactNode; email: string }) {
  return <div className={`${portal.app} ${styles.examApp}`}>
    <a href="#ib-question-content" className={portal.skipLink}>Skip to questions</a>
    <header className={portal.topbar}><Link href="/ib?subject=math-aa-hl&view=questions" className={portal.brandLink} aria-label="Thriving Scholars IB home"><IbBrand /></Link><div className={portal.account}><span className={portal.email}>{email}</span><Link className={portal.logout} href="/ib">My portal ↗</Link></div></header>
    <div className={styles.subjectBar}><nav aria-label="Subject"><Link href="/ib?subject=math-aa-hl&view=questions" aria-current="page">ƒ &nbsp; Maths AA HL</Link><Link href="/ib?subject=physics-hl&view=questions">λ &nbsp; Physics HL</Link></nav><span>WRITTEN QUESTIONS & MARK SCHEMES</span></div>
    <main id="ib-question-content" className={styles.examMain}>{children}</main>
    <footer className={styles.examFooter}><strong>THRIVING SCHOLARS</strong><span>Independent practice material · Maths AA HL</span></footer>
  </div>;
}
