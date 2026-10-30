"use client";

import { useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { supabaseBrowser } from "@/utils/supabase/browser";
import { IB_COURSES, ibSubject, ibView, ibHref, type IbSubject, type IbSummary } from "@/lib/ib/catalog";
import styles from "./ib.module.css";
import IbBrand from "./IbBrand";

export default function IBPortalClient({ email, summary }: { email: string; summary: IbSummary }) {
  const search = useSearchParams();
  const subject = ibSubject(search.get("subject"));
  const view = ibView(search.get("view"));
  const course = IB_COURSES[subject];
  const counts = summary[subject];
  const [query, setQuery] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const normalizedQuery = query.trim().toLowerCase();
  const collections = counts.collections.filter(c => `${c.title} ${c.subtopics.join(" ")} ${c.syllabus?.map(s => `${s.code} ${s.title}`).join(" ") ?? ""}`.toLowerCase().includes(normalizedQuery));

  async function logout() {
    setBusy(true);
    setError("");
    try {
      const { error: signOutError } = await supabaseBrowser().auth.signOut({ scope: "local" });
      if (signOutError) throw signOutError;
      window.location.replace(`/ib-login?next=${encodeURIComponent(ibHref(subject, view))}`);
    } catch {
      setError("We could not sign you out. Please try again.");
      setBusy(false);
    }
  }

  return <div className={styles.app}>
    <a href="#ib-main" className={styles.skipLink}>Skip to content</a>
    <header className={styles.topbar}>
      <Link href="/ib" className={styles.brandLink} aria-label="Thriving Scholars IB home"><IbBrand /></Link>
      <div className={styles.account}><span className={styles.email} title={email}>{email}</span><button className={styles.logout} onClick={logout} disabled={busy}>{busy ? "Signing out…" : "Sign out"}<span aria-hidden="true"> ↗</span></button></div>
    </header>
    <div className={styles.shell}>
      <aside className={styles.sidebar}>
        <div className={styles.sidebarHeading}>YOUR LEARNING SPACE</div>
        <nav aria-label="IB portal">
          <Link className={`${styles.navItem} ${view === "questions" ? styles.navActive : ""}`} href={ibHref(subject)} prefetch={false} aria-current={view === "questions" ? "page" : undefined}><span className={styles.navIcon} aria-hidden="true">▤</span><span>Question bank<small>Build understanding by topic</small></span><span className={styles.navArrow} aria-hidden="true">↗</span></Link>
          <Link className={`${styles.navItem} ${view === "mocks" ? styles.navActive : ""}`} href={ibHref(subject, "mocks")} prefetch={false} aria-current={view === "mocks" ? "page" : undefined}><span className={styles.navIcon} aria-hidden="true">◷</span><span>Mock tests<small>Put your learning into practice</small></span><span className={styles.navArrow} aria-hidden="true">↗</span></Link>
        </nav>
        <div className={styles.sidebarNote}><span className={styles.noteRule} /><strong>A little practice.<br />A lot of possibility.</strong><p>Your space to work through ideas, one question at a time.</p></div>
        <div className={styles.sidebarFooter}><span className={styles.statusDot} /> IB Diploma Programme<small>Maths AA HL · Physics HL</small></div>
      </aside>
      <main id="ib-main" className={styles.main}>
        <div className={styles.courseBar}><span className={styles.eyebrow}>CHOOSE YOUR SUBJECT</span><nav className={styles.subjectSwitch} aria-label="Subject">{(Object.keys(IB_COURSES) as IbSubject[]).map(id => <Link key={id} href={ibHref(id, view)} prefetch={false} onClick={() => setQuery("")} aria-current={subject === id ? "page" : undefined} className={subject === id ? styles.subjectActive : ""}><span aria-hidden="true">{IB_COURSES[id].symbol}</span>{IB_COURSES[id].label}</Link>)}</nav></div>
        {error ? <p role="alert" className={styles.error}>{error}</p> : null}
        <section className={styles.hero} aria-labelledby="course-heading">
          <div><span className={styles.heroLabel}>IB {course.label.toUpperCase()} <span>HIGHER LEVEL</span></span><h1 id="course-heading">{view === "questions" ? "Question bank" : "Mock tests"}<span className={styles.headingDot}>.</span></h1><p>{course.subtitle}</p></div>
          <div className={styles.heroArt} aria-hidden="true"><span className={styles.artRing} /><span className={styles.artRingTwo} /><span className={styles.artSymbol}>{course.symbol}</span><span className={styles.artSpark}>✦</span></div>
        </section>
        <div className={styles.stats}><div><strong>{view === "questions" ? counts.questions : counts.mocks}</strong><span>{view === "questions" ? "Questions available" : "Mock tests available"}</span></div><div><strong>{course.topics.length}</strong><span>{subject === "physics-hl" ? "Syllabus themes" : "Core topics"}</span></div><div><strong className={styles.statText}>HL</strong><span>Higher Level</span></div></div>
        {view === "questions" ? <>
          <div className={styles.sectionHeading}><div><span className={styles.eyebrow}>START WITH A TOPIC</span><h2>Explore {course.title.toLowerCase()}</h2></div><label className={styles.search}><span aria-hidden="true">⌕</span><span className={styles.srOnly}>Search topics</span><input type="search" placeholder="Search topics or subtopics" value={query} onChange={event => setQuery(event.target.value)} /></label></div>
          <div className={styles.topicGrid} key={subject}>
            {collections.map(collection => <div className={styles.topicCard} key={collection.id}>
              <Link href={`/ib/question-bank/${collection.id}`} prefetch={false} className={styles.collectionLink}><div className={styles.cardTop}><span className={styles.topicNumber}>{collection.code}</span><span className={styles.topicCount}>{collection.count} questions</span></div><h3>{collection.title}</h3><p>{collection.description}</p><div className={styles.cardBottom}><span>{collection.syllabus?.length ?? collection.subtopics.length} subtopics</span><span className={styles.cardAction}>Open question bank ↗</span></div></Link>
              <details className={styles.collectionSubtopics}><summary>Browse subtopics</summary><ul>{collection.syllabus ? collection.syllabus.map(subtopic => <li key={subtopic.code}><Link href={`/ib/question-bank/${collection.id}?syllabus=${encodeURIComponent(subtopic.code)}`} prefetch={false}><b>{subtopic.code}</b> {subtopic.title} <span className={styles.subtopicCount}>{subtopic.count} questions ↗</span></Link></li>) : collection.subtopics.map(subtopic => <li key={subtopic}><Link href={`/ib/question-bank/${collection.id}?subtopic=${encodeURIComponent(subtopic)}`} prefetch={false}>{subtopic} ↗</Link></li>)}</ul></details>
            </div>)}
            {!normalizedQuery && counts.questions === 0 ? <div className={styles.comingCard}><span className={styles.comingIcon} aria-hidden="true">✦</span><h3>Good things are taking shape.</h3><p>Your question bank is on its way. Browse the topics while we prepare your first questions and written mark schemes.</p><span className={styles.comingBadge}>CONTENT COMING SOON</span></div> : null}
          </div>
          {collections.length === 0 ? <div className={styles.emptySearch} role="status"><h3>No matching topics</h3><p>Try a different topic or subtopic.</p><button className={styles.secondaryButton} onClick={() => setQuery("")}>Clear search</button></div> : null}
        </> : <section className={styles.mockEmpty}><div className={styles.mockIcon} aria-hidden="true">◷</div><span className={styles.eyebrow}>{course.label.toUpperCase()} · MOCK TESTS</span><h2>Your next challenge is on its way.</h2><p>Mock tests and their written mark schemes will be available here once released. In the meantime, explore the topics in your question bank.</p><Link className={styles.primaryButton} href={ibHref(subject)}>Explore question bank <span aria-hidden="true">↗</span></Link><span className={styles.emptyCaption}>No mock tests published yet</span></section>}
        <footer className={styles.footer}><span>THRIVING SCHOLARS</span><span>Learn with purpose. Practise with confidence.</span></footer>
      </main>
    </div>
  </div>;
}
