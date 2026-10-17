"use client";

import { useSyncExternalStore } from "react";
import {
  getRemainingExamSeconds,
  splitCountdownSeconds,
} from "@/lib/exam-countdown";
import styles from "./exam-countdown.module.css";

function subscribeToClock(update: () => void) {
  // Recalculate from the absolute deadline each time, including after a tab
  // resumes. Decrementing a stored counter would drift when browsers pause it.
  const interval = window.setInterval(update, 1000);
  window.addEventListener("focus", update);
  document.addEventListener("visibilitychange", update);
  return () => {
    window.clearInterval(interval);
    window.removeEventListener("focus", update);
    document.removeEventListener("visibilitychange", update);
  };
}

function serverSnapshot() {
  return null;
}

export default function ExamCountdown({ exam }: { exam: "TMUA" | "ESAT" }) {
  const remaining = useSyncExternalStore(
    subscribeToClock,
    getRemainingExamSeconds,
    serverSnapshot,
  );
  const time = remaining === null ? null : splitCountdownSeconds(remaining);
  const pad = (value: number | undefined) =>
    value === undefined ? "––" : String(value).padStart(2, "0");

  return (
    <span
      className={styles.countdown}
      role="timer"
      aria-live="off"
      aria-label={time
        ? `${time.days} days, ${time.hours} hours, ${time.minutes} minutes and ${time.seconds} seconds until ${exam}, 4 January 2027 at midnight UK time`
        : `Countdown to ${exam}, 4 January 2027 at midnight UK time`}
    >
      <span className={styles.days} aria-hidden="true">
        <b className={styles.dayNumber}>{time?.days ?? "––"}</b>
        <span>{time?.days === 1 ? "day" : "days"}</span>
      </span>
      <span className={styles.details} aria-hidden="true">
        <span className={styles.target}>to {exam} · 4 Jan 2027</span>
        <span className={styles.clock}>
          <span>{pad(time?.hours)} <small>hrs</small></span>
          <span className={styles.separator}>:</span>
          <span>{pad(time?.minutes)} <small>min</small></span>
          <span className={styles.separator}>:</span>
          <span>{pad(time?.seconds)} <small>sec</small></span>
        </span>
      </span>
    </span>
  );
}
