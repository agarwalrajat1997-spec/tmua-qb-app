import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { requireIbUser } from "@/lib/ib/auth";
import { IB_COURSES, ibHref, physicsSyllabusSubtopics } from "@/lib/ib/catalog";
import { getIbQuestions } from "@/lib/ib/content";
import { IB_COLLECTIONS, getIbCollection, questionPrompt } from "@/lib/ib/question";
import ExamShell from "../../components/ExamShell";
import ExamInstructions from "../../components/ExamInstructions";
import QuestionBody, { QuestionBadges } from "../../components/QuestionBody";
import styles from "../../questions.module.css";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "IB HL Question Bank | Thriving Scholars", robots: { index: false, follow: false } };
type Query = Record<string, string | string[] | undefined>;
const single = (value: string | string[] | undefined) => typeof value === "string" ? value : "";
const PAGE_SIZE = 8;

export default async function QuestionBank({ params, searchParams }: { params: Promise<{ collection: string }>; searchParams: Promise<Query> }) {
  const [{ collection: id }, raw] = await Promise.all([params, searchParams]);
  const collection = getIbCollection(id);
  if (!collection) notFound();
  const physics = collection.subject === "physics-hl";
  const course = IB_COURSES[collection.subject];
  const paramsForLogin = new URLSearchParams();
  for (const key of ["q", "difficulty", "calculator", "subtopic", "syllabus", "level", "type", "page"]) {
    if (single(raw[key])) paramsForLogin.set(key, single(raw[key]).slice(0, 160));
  }
  const pathname = "/ib/question-bank/" + collection.id;
  const user = await requireIbUser(pathname + (paramsForLogin.size ? "?" + paramsForLogin : ""));
  const all = getIbQuestions(id);
  const subtopics = [...new Set(all.map(q => q.subtopic))].sort();
  const syllabusTopics = physics ? physicsSyllabusSubtopics(collection.topicId) : [];
  const search = single(raw.q).trim().slice(0, 160);
  const difficulty = ["easy", "medium", "hard"].includes(single(raw.difficulty)) ? single(raw.difficulty) : "";
  const calculator = !physics && ["yes", "no"].includes(single(raw.calculator)) ? single(raw.calculator) : "";
  const subtopic = subtopics.includes(single(raw.subtopic)) ? single(raw.subtopic) : "";
  const syllabus = syllabusTopics.some(topic => topic.code === single(raw.syllabus)) ? single(raw.syllabus) : "";
  const level = physics && ["core", "ahl"].includes(single(raw.level)) ? single(raw.level) : "";
  const type = physics && ["multiple-choice", "structured", "data-based"].includes(single(raw.type)) ? single(raw.type) : "";
  const matches = all.filter(q => {
    if (difficulty && q.difficulty !== difficulty) return false;
    if (calculator && q.calculator !== (calculator === "yes")) return false;
    if (subtopic && q.subtopic !== subtopic) return false;
    if (q.subject === "physics-hl" && ((syllabus && q.syllabusCode !== syllabus) || (level && q.level !== level) || (type && q.questionType !== type))) return false;
    const physicsTerms = q.subject === "physics-hl" ? q.syllabusCode + " " + (q.options?.map(option => option.text).join(" ") ?? "") : "";
    return !search || [q.number, q.id, q.title, q.subtopic, q.stem, q.parts.map(p => p.prompt).join(" "), physicsTerms].join(" ").toLowerCase().includes(search.toLowerCase());
  });
  const pages = Math.max(1, Math.ceil(matches.length / PAGE_SIZE));
  const requestedPage = Number(single(raw.page) || 1);
  const page = Number.isSafeInteger(requestedPage) ? Math.min(pages, Math.max(1, requestedPage)) : 1;
  const visible = matches.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  function filterHref(overrides: Record<string, string>) {
    const query = new URLSearchParams();
    for (const [key, value] of Object.entries({ q: search, difficulty, calculator, subtopic, syllabus, level, type, ...overrides })) if (value) query.set(key, value);
    return pathname + (query.size ? "?" + query : "");
  }

  return <ExamShell email={user.email} subject={collection.subject}>
    <nav className={styles.breadcrumb} aria-label="Breadcrumb"><Link href={ibHref(collection.subject)}>Question bank</Link><span>/</span><span>{collection.title}</span></nav>
    {physics ? <nav className={styles.themeNav} aria-label="Physics themes">{IB_COLLECTIONS.filter(item => item.subject === "physics-hl").map(item => <Link key={item.id} href={"/ib/question-bank/" + item.id} prefetch={false} aria-current={item.id === id ? "page" : undefined}><b>{item.code}</b> {item.title}</Link>)}</nav> : null}
    <div className={styles.bankHeading}><div><span className={styles.overline}>IB {course.label.toUpperCase()} · {physics ? "THEME" : "TOPIC"} {collection.code}</span><h1>{collection.title}<span>.</span></h1><p>{collection.description}</p></div><div className={styles.bankCount}><strong>{all.length}</strong><span>questions</span></div></div>
    <ExamInstructions subject={collection.subject} />
    {physics ? <nav className={styles.syllabusNav} aria-label="Syllabus subtopics"><Link href={filterHref({ syllabus: "", subtopic: "" })} aria-current={!syllabus ? "page" : undefined} prefetch={false}>All subtopics</Link>{syllabusTopics.map(topic => <Link key={topic.code} href={filterHref({ syllabus: topic.code, subtopic: "" })} aria-current={syllabus === topic.code ? "page" : undefined} prefetch={false}><b>{topic.code}</b> {topic.title}{topic.additionalHlOnly ? <small>Additional HL</small> : null}</Link>)}</nav> : null}
    <form key={filterHref({})} className={styles.filters + (physics ? " " + styles.physicsFilters : "")} method="GET" action={pathname}>
      <label className={styles.searchFilter}>Search questions<input name="q" type="search" defaultValue={search} placeholder="Keyword or question number" maxLength={160} /></label>
      {physics ? <label>Syllabus subtopic<select name="syllabus" defaultValue={syllabus}><option value="">All subtopics</option>{syllabusTopics.map(topic => <option value={topic.code} key={topic.code}>{topic.code} {topic.title}</option>)}</select></label> : <label>Subtopic<select name="subtopic" defaultValue={subtopic}><option value="">All subtopics</option>{subtopics.map(s => <option key={s}>{s}</option>)}</select></label>}
      <label>Difficulty<select name="difficulty" defaultValue={difficulty}><option value="">All difficulties</option><option value="easy">Easy</option><option value="medium">Medium</option><option value="hard">Hard</option></select></label>
      {physics ? <><label>Course content<select name="level" defaultValue={level}><option value="">Core + additional HL</option><option value="core">Core</option><option value="ahl">Additional HL</option></select></label><label>Question type<select name="type" defaultValue={type}><option value="">All question types</option><option value="multiple-choice">Multiple choice</option><option value="structured">Structured</option><option value="data-based">Data-based</option></select></label></> : <label>Calculator<select name="calculator" defaultValue={calculator}><option value="">All questions</option><option value="no">No calculator</option><option value="yes">Calculator</option></select></label>}
      <div className={styles.filterActions}><button type="submit">Apply filters</button><Link href={pathname} className={styles.reset}>Reset</Link></div>
    </form>
    <div className={styles.resultsLine}><span>{matches.length ? ((page - 1) * PAGE_SIZE + 1) + "–" + Math.min(page * PAGE_SIZE, matches.length) + " of " + matches.length + " questions" : "No matching questions"}</span><span>Mark schemes open in a new tab ↗</span></div>
    <div className={styles.questionList}>{visible.map(question => {
      const q = questionPrompt(question);
      return <article className={styles.questionCard} id={q.id} key={q.id}>
        <header className={styles.questionHeader}><div><Link href={"/ib/questions/" + q.id} prefetch={false} className={styles.questionNumber}>Question {q.number}</Link><span className={styles.subtopic}>{q.subtopic}</span></div><QuestionBadges question={q} /></header>
        <div className={styles.questionContent}><QuestionBody question={q} /><aside className={styles.questionActions}><Link href={"/ib/mark-scheme/" + q.id} target="_blank" rel="noopener noreferrer" prefetch={false} className={styles.schemeButton}>Mark scheme <span aria-hidden="true">↗</span><span className={styles.srOnly}> for question {q.number} (opens in a new tab)</span></Link><span>Written solution<br />with mark allocations</span></aside></div>
      </article>;
    })}</div>
    {!matches.length ? <section className={styles.noResults}><h2>No questions match these filters.</h2><p>Try another keyword, difficulty or subtopic.</p><Link href={pathname}>Clear filters</Link></section> : null}
    {pages > 1 ? <nav className={styles.pagination} aria-label="Question pages">{page > 1 ? <Link href={filterHref({ page: String(page - 1) })} prefetch={false}>← Previous</Link> : <span /> }<span>Page {page} of {pages}</span>{page < pages ? <Link href={filterHref({ page: String(page + 1) })} prefetch={false}>Next →</Link> : <span />}</nav> : null}
  </ExamShell>;
}
