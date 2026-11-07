"use client";
import Link from "next/link";
import { useState } from "react";
import { ECONOMICS_MOCKS } from "@/lib/ib/economics-mock-model";
import styles from "../mocks/mocks.module.css";
type Attempt = {
    id: string;
    mock_id?: string;
    paper: "1" | "2" | "3";
    submitted_at: string;
    marked_at: string | null;
};
function History({ id }: { id: string }) {
    const [attempts, setAttempts] = useState<Attempt[] | null>(null), [error, setError] = useState(""), [busy, setBusy] = useState(false);
    async function load() { setBusy(true); setError(""); try {
        const res = await fetch(`/api/ib/economics-mocks/${id}`, { cache: "no-store" }), data = await res.json();
        if (!res.ok)
            throw new Error(data.error);
        setAttempts(data.attempts);
    }
    catch (e) {
        setError(e instanceof Error ? e.message : "Could not load attempts.");
    }
    finally {
        setBusy(false);
    } }
    return <div><button className={styles.secondary} onClick={load} disabled={busy}>{busy ? "Loading…" : "View saved attempts"}</button>{error ? <p role="alert">{error}</p> : null}{attempts ? <ul className={styles.history}>{attempts.length ? attempts.map(a => <li key={a.id}><Link href={`/ib/economics-mocks/${id}/${a.paper}?attempt=${a.id}`}>Paper {a.paper} · {new Date(a.submitted_at).toLocaleDateString()} · {a.marked_at ? "View report" : "Finish self-assessment"} ↗</Link></li>) : <li>No submitted attempts yet.</li>}</ul> : null}</div>;
}
export default function EconomicsMockList({ course }: {
    course: "sl" | "hl";
}) {
    const mocks = ECONOMICS_MOCKS.filter(m => m.course === course && m.status === "published");
    return <section className={styles.catalog} aria-label={`Economics ${course.toUpperCase()} mock tests`}><div className={styles.intro}><span>SL / HL MOCK SERIES</span><h2>Economics practice papers</h2><p>{mocks.reduce((n,m) => n + m.papers.length, 0)} timed papers in {mocks.length} complete sets. Essays, data analysis and worked mark schemes.</p><p>Choose one essay in Paper 1 and one data response in Paper 2. {course === "hl" ? "In Paper 3, complete both policy questions. " : ""}Download the question paper before you start. After submission, use the worked scheme to mark your responses and receive your score report.</p></div><div className={styles.cards}>{mocks.map(m => <article className={styles.card} key={m.id}><span className={styles.tag}>SET {m.set} · {course.toUpperCase()}</span><h3>{m.title}</h3><p>Microeconomics · Macroeconomics · The global economy</p>{m.papers.filter(p => p.status === "published").map(p => <div key={p.id}><Link className={styles.paperLink} href={`/ib/economics-mocks/${m.id}/${p.paper}?course=${course}`} key={p.id}><strong>Paper {p.paper} · {p.paper === "1" ? "Extended response" : p.paper === "2" ? "Data response" : "Policy paper"}<small>{p.minutes} minutes · {p.marks} marks</small></strong><span>Start ↗</span></Link><p>{p.questionBooklets.map(b => <a key={b.url} href={b.url} target="_blank" rel="noopener noreferrer" style={{display:"inline-block",marginRight:14}}>{b.label} (PDF) ↗</a>)}</p></div>)}<History id={m.id}/></article>)}</div><p className={styles.note}>Independent Thriving Scholars practice for the syllabus first assessed in 2022. These are not official IB papers or grade predictions.</p></section>;
}
