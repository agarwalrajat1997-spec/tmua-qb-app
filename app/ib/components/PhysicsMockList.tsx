"use client";
import Link from "next/link";
import { useState } from "react";
import { PHYSICS_MOCKS, paperSpec } from "@/lib/ib/physics-mock-model";
import styles from "../mocks/mocks.module.css";
type Attempt = {id:string;paper:"1"|"2";submitted_at:string;marked_at:string|null};
function History({id}:{id:string}) {
  const [attempts,setAttempts] = useState<Attempt[]|null>(null);
  const [error,setError] = useState("");
  const [busy,setBusy] = useState(false);
  async function load() {
    setBusy(true); setError("");
    try { const res=await fetch(`/api/ib/mocks/${id}`,{cache:"no-store"}); const data=await res.json(); if(!res.ok)throw new Error(data.error);setAttempts(data.attempts); }
    catch(e){setError(e instanceof Error?e.message:"Could not load attempts.");}finally{setBusy(false);}
  }
  return <div><button className={styles.secondary} onClick={load} disabled={busy}>{busy?"Loading…":"View saved attempts"}</button>{error?<p role="alert">{error}</p>:null}{attempts?<ul className={styles.history}>{attempts.length?attempts.map(a=><li key={a.id}><Link href={`/ib/mocks/${id}/${a.paper}?attempt=${a.id}`}>Paper {a.paper} · {new Date(a.submitted_at).toLocaleDateString()} · {a.marked_at?"View report":"Finish self-assessment"} ↗</Link></li>):<li>No submitted attempts yet.</li>}</ul>:null}</div>;
}
export default function PhysicsMockList({course}:{course:"sl"|"hl"}) {
  return <section className={styles.catalog} aria-label={`Physics ${course.toUpperCase()} mock tests`}>
    <div className={styles.intro}><span>YOUR EXAM PRACTICE SERIES</span><h2>Build confidence, paper by paper.</h2><p>Three complete mocks covering all five themes. Original questions compiled from your Physics bank, with diagrams and worked mark schemes. Questions do not repeat across this series; you may have seen them in topic practice.</p><p>Paper 1A and 1B share one uninterrupted timer. Paper 2 is a separate sitting. Calculators and a clean Physics data booklet are permitted. Written marks are self-assessed and identified in your emailed report.</p></div>
    <div className={styles.cards}>{PHYSICS_MOCKS.filter(m=>m.course===course).map((m,index)=><article className={styles.card} key={m.id}>
      <span className={styles.tag}>MOCK {String(index+1).padStart(2,"0")} · {course.toUpperCase()}</span><h3>{m.title}</h3><p>Motion · Matter · Waves · Fields · Nuclear physics</p>
      {(["1","2"] as const).map(p=>{const s=paperSpec(course,p);return <Link className={styles.paperLink} href={`/ib/mocks/${m.id}/${p}`} key={p}><strong>{s.label}<small>{s.minutes} minutes · {s.marks} marks</small></strong><span>Start ↗</span></Link>;})}
      <History id={m.id}/>
    </article>)}</div>
    <p className={styles.note}>Independent Thriving Scholars practice for the syllabus first assessed in 2025. These are not official IB papers or grade predictions.</p>
  </section>;
}
