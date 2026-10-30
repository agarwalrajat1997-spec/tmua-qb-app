import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { requireIbUser } from "@/lib/ib/auth";
import { getIbQuestions } from "@/lib/ib/content";
import { getIbCollection, questionPrompt } from "@/lib/ib/question";
import ExamShell from "../../components/ExamShell";
import QuestionBody, { QuestionBadges } from "../../components/QuestionBody";
import styles from "../../questions.module.css";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Maths AA HL Question Bank | Thriving Scholars", robots: { index: false, follow: false } };
type Query = Record<string, string | string[] | undefined>;
const single = (value: string | string[] | undefined) => typeof value === "string" ? value : "";
const PAGE_SIZE = 8;

export default async function QuestionBank({ params, searchParams }: { params: Promise<{ collection: string }>; searchParams: Promise<Query> }) {
  const [{ collection: id }, raw] = await Promise.all([params, searchParams]);
  const collection = getIbCollection(id);
  if (!collection) notFound();
  const paramsForLogin = new URLSearchParams();
  for (const key of ["q", "difficulty", "calculator", "subtopic", "page"]) if (single(raw[key])) paramsForLogin.set(key, single(raw[key]).slice(0, 160));
  const pathname = `/ib/question-bank/${collection.id}`;
  const user = await requireIbUser(`${pathname}${paramsForLogin.size ? `?${paramsForLogin}` : ""}`);
  const all = getIbQuestions(id);
  const subtopics = [...new Set(all.map(q => q.subtopic))].sort();
  const search = single(raw.q).trim().slice(0, 160);
  const difficulty = ["easy", "medium", "hard"].includes(single(raw.difficulty)) ? single(raw.difficulty) : "";
  const calculator = ["yes", "no"].includes(single(raw.calculator)) ? single(raw.calculator) : "";
  const subtopic = subtopics.includes(single(raw.subtopic)) ? single(raw.subtopic) : "";
  const matches = all.filter(q => (!difficulty || q.difficulty === difficulty)
    && (!calculator || q.calculator === (calculator === "yes")) && (!subtopic || q.subtopic === subtopic)
    && (!search || `${q.number} ${q.id} ${q.title} ${q.subtopic} ${q.stem} ${q.parts.map(p => p.prompt).join(" ")}`.toLowerCase().includes(search.toLowerCase())));
  const pages = Math.max(1, Math.ceil(matches.length / PAGE_SIZE));
  const requestedPage = Number(single(raw.page) || 1);
  const page = Number.isSafeInteger(requestedPage) ? Math.min(pages, Math.max(1, requestedPage)) : 1;
  const visible = matches.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  function pageHref(number: number) {
    const query = new URLSearchParams();
    for (const [key, value] of Object.entries({ q: search, difficulty, calculator, subtopic, page: String(number) })) if (value) query.set(key, value);
    return `${pathname}?${query}`;
  }

  return <ExamShell email={user.email}>
    <nav className={styles.breadcrumb} aria-label="Breadcrumb"><Link href="/ib?subject=math-aa-hl&view=questions">Question bank</Link><span>/</span><span>{collection.title}</span></nav>
    <div className={styles.bankHeading}><div><span className={styles.overline}>IB MATHS AA HL · TOPIC {collection.code}</span><h1>{collection.title}<span>.</span></h1><p>{collection.description}</p></div><div className={styles.bankCount}><strong>{all.length}</strong><span>questions</span></div></div>
    <p className={styles.examInstructions}>Unless stated otherwise, give exact answers or non-exact numerical answers to three significant figures. Show your working. Angles are in radians unless degrees are indicated.</p>
    <form className={styles.filters} method="GET" action={pathname}>
      <label className={styles.searchFilter}>Search questions<input name="q" type="search" defaultValue={search} placeholder="Keyword or question number" maxLength={160} /></label>
      <label>Subtopic<select name="subtopic" defaultValue={subtopic}><option value="">All subtopics</option>{subtopics.map(s => <option key={s}>{s}</option>)}</select></label>
      <label>Difficulty<select name="difficulty" defaultValue={difficulty}><option value="">All difficulties</option><option value="easy">Easy</option><option value="medium">Medium</option><option value="hard">Hard</option></select></label>
      <label>Calculator<select name="calculator" defaultValue={calculator}><option value="">All questions</option><option value="no">No calculator</option><option value="yes">Calculator</option></select></label>
      <button type="submit">Apply filters</button><Link href={pathname} className={styles.reset}>Reset</Link>
    </form>
    <div className={styles.resultsLine}><span>{matches.length ? `${(page - 1) * PAGE_SIZE + 1}–${Math.min(page * PAGE_SIZE, matches.length)} of ${matches.length} questions` : "No matching questions"}</span><span>Mark schemes open in a new tab ↗</span></div>
    <div className={styles.questionList}>{visible.map(question => {
      const q = questionPrompt(question);
      return <article className={styles.questionCard} id={q.id} key={q.id}>
        <header className={styles.questionHeader}><div><Link href={`/ib/questions/${q.id}`} prefetch={false} className={styles.questionNumber}>Question {q.number}</Link><span className={styles.subtopic}>{q.subtopic}</span></div><QuestionBadges question={q} /></header>
        <div className={styles.questionContent}><QuestionBody question={q} /><aside className={styles.questionActions}><Link href={`/ib/mark-scheme/${q.id}`} target="_blank" rel="noopener noreferrer" prefetch={false} className={styles.schemeButton}>Mark scheme <span aria-hidden="true">↗</span><span className={styles.srOnly}> for question {q.number} (opens in a new tab)</span></Link><span>Written solution<br />with mark allocations</span></aside></div>
      </article>;
    })}</div>
    {!matches.length ? <section className={styles.noResults}><h2>No questions match these filters.</h2><p>Try another keyword, difficulty or subtopic.</p><Link href={pathname}>Clear filters</Link></section> : null}
    {pages > 1 ? <nav className={styles.pagination} aria-label="Question pages">{page > 1 ? <Link href={pageHref(page - 1)} prefetch={false}>← Previous</Link> : <span /> }<span>Page {page} of {pages}</span>{page < pages ? <Link href={pageHref(page + 1)} prefetch={false}>Next →</Link> : <span />}</nav> : null}
  </ExamShell>;
}
