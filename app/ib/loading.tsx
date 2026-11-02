import styles from "./questions.module.css";

export default function Loading() {
  return <div className={styles.loading} role="status" aria-live="polite">
    <span>THRIVING SCHOLARS · IB</span>
    <p>Loading your practice…</p>
  </div>;
}
