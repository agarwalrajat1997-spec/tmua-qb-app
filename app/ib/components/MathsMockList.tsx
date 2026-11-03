"use client";
import { useState } from "react";
import Link from "next/link";
import { MATHS_MOCKS, type MathsMockMeta } from "@/lib/ib/maths-mock-model";
import styles from "../maths-mocks/maths-mocks.module.css";

type Attempt = { id: string; submitted_at: string; marked_at: string | null };
function MathsMockHistory({ paper }: { paper: MathsMockMeta }) {
  const [attempts, setAttempts] = useState<Attempt[] | null>(null), [busy, setBusy] = useState(false), [error, setError] = useState("");
  async function load() {
    setBusy(true); setError("");
    try { const response = await fetch(`/api/ib/maths-mocks/${paper.id}`, { cache: "no-store" }); const data = await response.json(); if (!response.ok) throw new Error(data.error || "History unavailable."); setAttempts(data.attempts); }
    catch (e) { setError(e instanceof Error ? e.message : "Could not load your attempts."); } finally { setBusy(false); }
  }
  return <div className={styles.historyBlock}><button className={styles.secondary} onClick={load} disabled={busy}>{busy ? "Loading…" : `Paper ${paper.paper} saved attempts`}</button>{error ? <p role="alert">{error}</p> : null}{attempts ? <ul className={styles.history}>{attempts.length ? attempts.map(a => <li key={a.id}><Link href={`/ib/maths-mocks/${paper.id}?attempt=${a.id}`}>{new Date(a.submitted_at).toLocaleDateString()} · {a.marked_at ? "View report and solution book" : "View submission and finish marking"} ↗</Link></li>) : <li>No submitted attempts yet.</li>}</ul> : null}</div>;
}
export default function MathsMockList({ course }: { course: "sl" | "hl" }) {
  const papers = MATHS_MOCKS.filter(p => p.course === course && p.status === "published");
  return <section className={styles.catalog} aria-label={`Mathematics AA ${course.toUpperCase()} mock exams`}>
    <div className={styles.intro}><span>YOUR MATHEMATICS EXAM PRACTICE</span><h2>Work through a complete paper.</h2><p>Two mock sets with carefully reconstructed question papers, diagrams and worked solution books. Each paper has its own exam timer, question navigator and saved attempt history.</p><p>Paper 1 is without a calculator. A graphic display calculator is required for Papers 2{course === "hl" ? " and 3" : ""}. Use a clean Mathematics formula booklet and retain your written working for self-assessment.</p></div>
    <div className={styles.cards}>{(["A", "B"] as const).map(set => <article className={styles.card} key={set}><span className={styles.tag}>MATHEMATICS AA {course.toUpperCase()} · {papers.find(p => p.set === set)?.year ?? 2025}</span><h3>Mock Set {set}</h3><p>{course === "hl" ? "Three separate paper sittings" : "Two separate paper sittings"} · Written mathematics</p>{papers.filter(p => p.set === set).map(p => <div key={p.id}><Link className={styles.paperLink} href={`/ib/maths-mocks/${p.id}`}><strong>Paper {p.paper}<small>{p.minutes} minutes · {p.marks} marks · {p.calculator ? "GDC required" : "No calculator"}</small></strong><span>Start ↗</span></Link><MathsMockHistory paper={p} /></div>)}</article>)}</div>
    <p className={styles.note}>After submission, open the combined PDF: question paper first, then worked solutions. The same PDF link appears in your completion email. Written marks are self-assessed; no official IB grade is calculated.</p>
  </section>;
}
