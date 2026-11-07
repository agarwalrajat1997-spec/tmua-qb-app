"use client";
import Link from "next/link";
import { useState } from "react";
import { BIOLOGY_MOCKS } from "@/lib/ib/biology-mock-model";
import styles from "../mocks/mocks.module.css";
type Attempt = {
    id: string;
    mock_id?: string;
    paper: "1" | "2";
    submitted_at: string;
    marked_at: string | null;
};
function History({ id }: { id: string }) {
    const [attempts, setAttempts] = useState<Attempt[] | null>(null), [error, setError] = useState(""), [busy, setBusy] = useState(false);
    async function load() { setBusy(true); setError(""); try {
        const res = await fetch(`/api/ib/biology-mocks/${id}`, { cache: "no-store" }), data = await res.json();
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
    return <div><button className={styles.secondary} onClick={load} disabled={busy}>{busy ? "Loading…" : "View saved attempts"}</button>{error ? <p role="alert">{error}</p> : null}{attempts ? <ul className={styles.history}>{attempts.length ? attempts.map(a => <li key={a.id}><Link href={`/ib/biology-mocks/${id}/${a.paper}?attempt=${a.id}`}>Paper {a.paper} · {new Date(a.submitted_at).toLocaleDateString()} · {a.marked_at ? "View report" : "Finish self-assessment"} ↗</Link></li>) : <li>No submitted attempts yet.</li>}</ul> : null}</div>;
}
export default function BiologyMockList({ course }: {
    course: "sl" | "hl";
}) {
    const mocks = BIOLOGY_MOCKS.filter(m => m.course === course && m.status === "published");
    return <section className={styles.catalog} aria-label={`Biology ${course.toUpperCase()} mock tests`}><div className={styles.intro}><span>SL / HL MOCK SERIES</span><h2>Biology practice papers</h2><p>{mocks.length * 2} timed papers in {mocks.length} complete sets. Independent, challenging Biology questions with diagrams, experimental data and worked mark schemes.</p><p>Paper 1A and 1B share one uninterrupted timer. Paper 2 is a separate sitting. Use a calculator. Paper 2 includes a choice of extended responses. Multiple-choice answers are marked automatically; written marks are self-assessed. Print each question booklet below. After submission, open the worked mark scheme and receive your completion and score reports by email.</p></div><div className={styles.cards}>{mocks.map(m => <article className={styles.card} key={m.id}><span className={styles.tag}>SET {m.set} · {course.toUpperCase()}</span><h3>{m.title}</h3><p>Unity and diversity · Form and function · Interaction and interdependence · Continuity and change</p>{m.papers.filter(p => p.status === "published").map(p => <div key={p.id}><Link className={styles.paperLink} href={`/ib/biology-mocks/${m.id}/${p.paper}?course=${course}`} key={p.id}><strong>{p.paper === "1" ? "Paper 1A + 1B" : "Paper 2"}<small>{p.minutes} minutes · {p.marks} marks</small></strong><span>Start ↗</span></Link><p>{p.questionBooklets.map(b => <a key={b.url} href={b.url} target="_blank" rel="noopener noreferrer" style={{display:"inline-block",marginRight:14}}>{b.label} (PDF) ↗</a>)}</p></div>)}<History id={m.id}/></article>)}</div><p className={styles.note}>Independent Thriving Scholars practice for the syllabus first assessed in 2025. These are not official IB papers or grade predictions.</p></section>;
}
