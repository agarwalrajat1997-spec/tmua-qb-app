import Link from "next/link";
import { IB_COURSES, type IbCourseLevel, type IbSubject } from "@/lib/ib/catalog";
import styles from "../ib.module.css";

export type ChemistryCourseLinks = Record<IbCourseLevel, string>;

export default function ChemistryCourseSwitch({ course, links, subject = "chemistry" }: { subject?: IbSubject; course: IbCourseLevel; links: ChemistryCourseLinks }) {
  return <div className={styles.chemistryCourse}>
    <div><span className={styles.eyebrow}>{IB_COURSES[subject].label.toUpperCase()} COURSE</span><p>{course === "sl" ? "SL content only" : "SL content and additional HL"}</p></div>
    <nav aria-label={`${IB_COURSES[subject].label} course`} className={styles.courseSwitch}>
      <Link href={links.sl} prefetch={false} aria-current={course === "sl" ? "page" : undefined}><strong>SL</strong><span>Standard Level</span></Link>
      <Link href={links.hl} prefetch={false} aria-current={course === "hl" ? "page" : undefined}><strong>HL</strong><span>Higher Level</span></Link>
    </nav>
  </div>;
}
