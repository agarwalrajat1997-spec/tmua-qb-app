"use client";
import styles from "../questions.module.css";

export default function PrintButton() {
  return <button className={styles.printButton} onClick={() => window.print()}>Print mark scheme</button>;
}
