import Link from "next/link";
import type { IbCourseLevel } from "@/lib/ib/catalog";
import styles from "../ib.module.css";

export type ChemistryCourseLinks = Record<IbCourseLevel, string>;

export default function ChemistryCourseSwitch({ course, links }: { course: IbCourseLevel; links: ChemistryCourseLinks }) {
  return <div className={styles.chemistryCourse}>
    <div><span className={styles.eyebrow}>CHEMISTRY COURSE</span><p>{course === "sl" ? "SL content only" : "SL content and additional HL"}</p></div>
    <nav aria-label="Chemistry course" className={styles.courseSwitch}>
      <Link href={links.sl} prefetch={false} aria-current={course === "sl" ? "page" : undefined}><strong>SL</strong><span>Standard Level</span></Link>
      <Link href={links.hl} prefetch={false} aria-current={course === "hl" ? "page" : undefined}><strong>HL</strong><span>Higher Level</span></Link>
    </nav>
  </div>;
}
