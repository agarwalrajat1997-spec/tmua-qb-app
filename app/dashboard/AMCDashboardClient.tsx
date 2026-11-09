"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import styles from "../ib/ib.module.css";
import { PAST_PAPER_PRACTICE_URL } from "@/lib/past-paper-practice";
import { PRACTICE_TESTS, AMC_RESOURCE_SECTIONS, AMC12_ARCHIVE } from "./amc-catalogue";

const exams = ["8", "10", "12"] as const;
type Exam = typeof exams[number];
const sections = [
  ["questions", "Question bank", "Build understanding by topic", "▤"],
  ["practice-tests", "Practice tests", "Practise under timed conditions", "◷"],
  ["resources", "Resources", "Download your revision library", "▧"],
] as const;
type Section = typeof sections[number][0];
type Props = { email?: string | null; hasTmua?: boolean; initialSection?: Section | null };
const href = (exam: Exam, view: Section) => "/amc?exam=" + exam + (view === "questions" ? "" : "&section=" + view);
const bank = (exam: Exam, topic: string) => "/amc-" + exam + "-question-bank/index.html?topic=" + encodeURIComponent(topic);
type Topic = { topic: string; count: number; examples: string[] };
type Summary = { exam: string; topics: Topic[]; count: number };

export default function AMCDashboardClient({ email, hasTmua, initialSection }: Props) {
  const params = useSearchParams();
  const exam: Exam = exams.find(x => x === params.get("exam")) || "8";
  const view: Section = sections.find(x => x[0] === (params.get("section") || initialSection))?.[0] || "questions";
  const [query, setQuery] = useState("");
  const [summary, setSummary] = useState<Summary | null>(null);
  const [failure, setFailure] = useState("");
  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/amc/qb/list?paper=AMC%20" + exam + "&summary=1", { signal: controller.signal, cache: "no-store" })
      .then(async r => { if (!r.ok) throw Error(String(r.status)); const data = await r.json(); if (!Array.isArray(data.topics)) throw Error("Invalid topic list"); return data; })
      .then(data => { if (!controller.signal.aborted) setSummary({ exam, topics: data.topics, count: data.total }); })
      .catch(() => { if (!controller.signal.aborted) setFailure(exam); });
    return () => controller.abort();
  }, [exam]);
  const live = summary?.exam === exam ? summary : null;
  const tests = PRACTICE_TESTS.filter(t => t.exam === exam);
  const resources = AMC_RESOURCE_SECTIONS.find(s => s.heading === "AMC " + exam)!;
  const heading = sections.find(s => s[0] === view)![1];
  const filtered = (live?.topics || []).filter(t => [t.topic, ...t.examples].join(" ").toLowerCase().includes(query.trim().toLowerCase()));
  const card = (url: string, label: string, title: string, detail: string, action: string, meta: string) => (
    <article className={styles.topicCard} key={url}><a href={url} className={styles.collectionLink}>
      <div className={styles.cardTop}><span className={styles.topicCount}>{label}</span></div><h3>{title}</h3><p>{detail}</p>
      <div className={styles.cardBottom}><span>{meta}</span><span className={styles.cardAction}>{action} ↗</span></div>
    </a></article>);
  return <div className={styles.app}>
    <a href="#amc-main" className={styles.skipLink}>Skip to content</a>
    <header className={styles.topbar}><Link href={href(exam,"questions")} className={styles.brandLink}><span className={styles.brand}><span className={styles.brandMark}>ts<span>↗</span></span><span>Thriving Scholars<small>AMC STUDENT PORTAL</small></span></span></Link>
      <div className={styles.account}><span className={styles.email}>{email}</span><a className={styles.logout} href="/api/logout">Sign out ↗</a></div></header>
    <div className={styles.shell}><aside className={styles.sidebar}><div className={styles.sidebarHeading}>YOUR LEARNING SPACE</div>
      <nav aria-label="AMC workspace">{sections.map(([id, name, detail, icon]) => <Link key={id} href={href(exam,id)} className={styles.navItem + (view === id ? " " + styles.navActive : "")} aria-current={view === id ? "page" : undefined}><span className={styles.navIcon} aria-hidden="true">{icon}</span><span>{name}<small>{detail}</small></span></Link>)}</nav>
      <div className={styles.sidebarNote}><span className={styles.noteRule}/><strong>A little practice.<br/>A lot of possibility.</strong><p>Work through one question, then use its solution to try another approach.</p></div>
      <div className={styles.sidebarFooter}><span className={styles.statusDot}/> AMC preparation<small><a href="mailto:outreach@thrivingscholars.com">Contact student support ↗</a></small>{hasTmua && <small><a href="/dashboard?view=tmua">Open TMUA portal ↗</a></small>}</div></aside>
      <main id="amc-main" className={styles.main}><div className={styles.courseBar}><span className={styles.eyebrow}>CHOOSE YOUR EXAM</span><nav className={styles.subjectSwitch} style={{gridTemplateColumns:"repeat(3,minmax(0,1fr))"}} aria-label="Exam">{exams.map(e => <Link href={href(e,view)} key={e} onClick={() => setQuery("")} aria-current={exam === e ? "page" : undefined} className={exam === e ? styles.subjectActive : ""}>AMC {e}</Link>)}</nav></div>
      <section className={styles.hero}><div><span className={styles.heroLabel}>AMC {exam} <span>CONTEST PREPARATION</span></span><h1>{heading}<span className={styles.headingDot}>.</span></h1><p>{view === "questions" ? "Choose a topic, solve a problem and review the worked solution." : view === "practice-tests" ? "Choose a paper and review your answers when you finish." : resources.description}</p></div><div aria-hidden="true" className={styles.heroArt}><span className={styles.artRing}/><span className={styles.artRingTwo}/><span className={styles.artSymbol}>{exam}</span><span className={styles.artSpark}>✦</span></div></section>
      <div className={styles.stats}><div><strong>{live?.count ?? "—"}</strong><span>Bank questions</span></div><div><strong>{exam === "12" ? AMC12_ARCHIVE.length : tests.length}</strong><span>{exam === "12" ? "Past papers" : "Digital tests"}</span></div><div><strong>{resources.resources.length}</strong><span>Revision resources</span></div></div>
      {view === "questions" && <><div className={styles.sectionHeading}><div><span className={styles.eyebrow}>START WITH A TOPIC</span><h2>Explore AMC {exam}</h2></div><label className={styles.search}><span aria-hidden="true">⌕</span><span className={styles.srOnly}>Search topics</span><input type="search" placeholder="Search topics" value={query} onChange={e => setQuery(e.target.value)}/></label></div>
        {!live && <p role="status">{failure === exam ? "The topic counts could not be loaded." : "Loading topics…"}</p>}
        {live && !filtered.length && <p role="status">No matching topics. Try a different search.</p>}
        <div className={styles.topicGrid}>{filtered.map(t => card(bank(exam,t.topic),t.count + " questions",t.topic.replace(/^\d+[_\s-]*/, ""),t.examples.slice(0,3).join(" · "),"Practise topic","AMC " + exam))}</div>
        <p style={{margin:"20px 0"}}><a className={styles.cardAction} href={PAST_PAPER_PRACTICE_URL} target="_blank" rel="noopener noreferrer">Practise with past papers <span aria-hidden="true">↗</span><span className={styles.srOnly}> (opens in a new tab)</span></a></p></>}
      {view === "practice-tests" && <><div className={styles.sectionHeading}><div><span className={styles.eyebrow}>TIMED PRACTICE</span><h2>AMC {exam} papers</h2></div></div><div className={styles.topicGrid}>{[...tests].sort((a,b) => Number(!/Diagnostic|Pre-AMC/.test(a.title)) - Number(!/Diagnostic|Pre-AMC/.test(b.title))).map(t => card(t.href,t.tags.slice(0,2).join(" · "),t.title,t.detail,"Start test",t.level))}
        {exam === "12" && AMC12_ARCHIVE.map(p => <article key={p.title} className={styles.topicCard}><div className={styles.collectionLink}><div className={styles.cardTop}><span className={styles.topicCount}>25 questions · 75 minutes</span></div><h3>{p.title}</h3><p>Past paper · Self-marked. {"note" in p ? p.note : "Use the printed key when you finish."}</p><div className={styles.cardBottom}><a href={resources.resources[1].href+"#page="+p.keyPage}>Answer key · p. {p.keyPage}</a><a className={styles.cardAction} href={resources.resources[1].href+"#page="+p.page}>Open paper · p. {p.page} ↗</a></div></div></article>)}</div>{exam === "12" && <p className={styles.emptyCaption}>These papers open in the AMC 12 compendium. They do not submit a digital score.</p>}</>}
      {view === "resources" && <><div className={styles.sectionHeading}><div><span className={styles.eyebrow}>REVISION LIBRARY</span><h2>AMC {exam} resources</h2></div></div><div className={styles.topicGrid}>{resources.resources.map(r => card(r.href,r.kind,r.title,r.description,"Open PDF",r.pages+" pages"))}</div></>}
      <footer className={styles.footer}><span>THRIVING SCHOLARS</span><span>Learn with purpose. Practise with confidence.</span></footer></main></div></div>;
}
