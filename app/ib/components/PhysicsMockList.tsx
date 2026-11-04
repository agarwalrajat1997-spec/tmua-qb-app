"use client";
import Link from "next/link";
import { useState } from "react";
import { PHYSICS_MOCKS } from "@/lib/ib/physics-mock-model";
import styles from "../mocks/mocks.module.css";
type Attempt = {
    id: string;
    mock_id?: string;
    paper: "1" | "2";
    submitted_at: string;
    marked_at: string | null;
};
function History({ id, course }: {
    id?: string;
    course?: "sl" | "hl";
}) {
    const [attempts, setAttempts] = useState<Attempt[] | null>(null), [error, setError] = useState(""), [busy, setBusy] = useState(false);
    async function load() { setBusy(true); setError(""); try {
        const res = await fetch(id ? `/api/ib/mocks/${id}` : `/api/ib/mocks/archive?course=${course}`, { cache: "no-store" }), data = await res.json();
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
    return <div><button className={styles.secondary} onClick={load} disabled={busy}>{busy ? "Loading…" : id ? "View saved attempts" : "View earlier saved attempts"}</button>{error ? <p role="alert">{error}</p> : null}{attempts ? <ul className={styles.history}>{attempts.length ? attempts.map(a => <li key={a.id}><Link href={`/ib/mocks/${id ?? a.mock_id}/${a.paper}?attempt=${a.id}`}>Paper {a.paper} · {new Date(a.submitted_at).toLocaleDateString()} · {a.marked_at ? "View report" : id ? "Finish self-assessment" : "View saved attempt"} ↗</Link></li>) : <li>No submitted attempts yet.</li>}</ul> : null}</div>;
}
export default function PhysicsMockList({ course }: {
    course: "sl" | "hl";
}) {
    const mocks = PHYSICS_MOCKS.filter(m => m.course === course && m.status === "published");
    return <section className={styles.catalog} aria-label={`Physics ${course.toUpperCase()} mock tests`}><div className={styles.intro}><span>YOUR EXAM PRACTICE SERIES</span><h2>Build confidence, paper by paper.</h2><p>{mocks.length * 2} timed papers in {mocks.length} complete sets. Independent, challenging Physics questions with diagrams, experimental data and worked mark schemes.</p><p>Paper 1A and 1B share one uninterrupted timer. Paper 2 is a separate sitting. Calculators and a clean Physics data booklet are permitted. Multiple-choice answers are marked automatically; written marks are self-assessed. Submitted attempts include a combined question-and-solution PDF and emailed reports.</p></div><div className={styles.cards}>{mocks.map(m => <article className={styles.card} key={m.id}><span className={styles.tag}>SET {m.set} · {course.toUpperCase()}</span><h3>{m.title}</h3><p>Motion · Matter · Waves · Fields · Nuclear physics</p>{m.papers.filter(p => p.status === "published").map(p => <Link className={styles.paperLink} href={`/ib/mocks/${m.id}/${p.paper}`} key={p.id}><strong>{p.paper === "1" ? "Paper 1A + 1B" : "Paper 2"}<small>{p.minutes} minutes · {p.marks} marks</small></strong><span>Start ↗</span></Link>)}<History id={m.id}/></article>)}</div><p className={styles.note}>Independent Thriving Scholars practice for the syllabus first assessed in 2025. These are not official IB papers or grade predictions.</p><History course={course}/></section>;
}
