import { PAST_PAPER_PRACTICE_URL } from "@/lib/past-paper-practice";
import styles from "./PastPaperPracticeLink.module.css";

export default function PastPaperPracticeLink() {
  return (
    <aside className={styles.panel} aria-label="Free maths past-paper practice">
      <div className={styles.copy}>
        <span className={styles.label}>Free · All-in-one resource</span>
        <h3>Want to focus on maths past papers?</h3>
        <p>
          Explore TMUA, MAT, ENGAA, NSAA, AMC 8 and AMC 10 questions by paper or
          topic, with answers and available worked solutions.
        </p>
      </div>
      <a
        className={styles.link}
        href={PAST_PAPER_PRACTICE_URL}
        target="_blank"
        rel="noopener noreferrer"
      >
        Explore past-paper practice <span aria-hidden="true">↗</span>
        <span className={styles.srOnly}> (opens in a new tab)</span>
      </a>
    </aside>
  );
}
