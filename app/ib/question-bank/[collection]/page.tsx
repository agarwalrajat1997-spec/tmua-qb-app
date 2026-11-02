import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { requireIbUser } from "@/lib/ib/auth";
import { ibHref, ibHasCourseChoice, ibCoreLevel, ibIsHumanitiesSubject, ibSyllabusSubtopics, ibCourseLevel, ibCourseLabel, ibCourseHref } from "@/lib/ib/catalog";
import { getIbQuestions } from "@/lib/ib/content";
import { ibTopicGroups, questionInTopicGroup } from "@/lib/ib/topic-groups";
import { ibFilterHref, queryValues, selectedValues, singleQueryValue as single, type IbFilterQuery as Query } from "@/lib/ib/question-filters";
import MultiSelectFilter from "../../components/MultiSelectFilter";
import { variedPracticeOrder } from "@/lib/ib/practice-order";
import { IB_COLLECTIONS, getIbCollection, questionPrompt, isScienceQuestion, isHumanitiesQuestion } from "@/lib/ib/question";
import ExamShell from "../../components/ExamShell";
import ExamInstructions from "../../components/ExamInstructions";
import QuestionBody, { QuestionBadges } from "../../components/QuestionBody";
import styles from "../../questions.module.css";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "IB Question Bank | Thriving Scholars", robots: { index: false, follow: false } };
const PAGE_SIZE = 8;

export default async function QuestionBank({ params, searchParams }: { params: Promise<{ collection: string }>; searchParams: Promise<Query> }) {
  const [{ collection: id }, raw] = await Promise.all([params, searchParams]);
  const collection = getIbCollection(id);
  if (!collection) notFound();
  const physics = collection.subject === "physics-hl";
  const courseChoice = ibHasCourseChoice(collection.subject);
  const science = physics || courseChoice;
  const humanities = ibIsHumanitiesSubject(collection.subject);
  const coreLevel = ibCoreLevel(collection.subject);
  const courseLevel = ibCourseLevel(single(raw.course));
  const courseLabel = ibCourseLabel(collection.subject, courseLevel);
  const paramsForLogin = new URLSearchParams();
  for (const key of ["q", "difficulty", "calculator", "subtopic", "syllabus", "level", "type", "style", "category", "page"]) {
    for (const value of queryValues(raw[key])) if (value) paramsForLogin.append(key, value);
  }
  if (courseChoice) paramsForLogin.set("course", courseLevel);
  const pathname = "/ib/question-bank/" + collection.id;
  const baseHref = ibCourseHref(pathname, collection.subject, courseLevel);
  const user = await requireIbUser(pathname + (paramsForLogin.size ? "?" + paramsForLogin : ""));
  const all = getIbQuestions(id, courseLevel);
  const subtopics = [...new Set(all.map(q => q.subtopic))].sort();
  const syllabusTopics = ibSyllabusSubtopics(collection.subject, collection.topicId, courseLevel);
  const groups = ibTopicGroups(collection, all, courseLevel);
  const search = single(raw.q).trim().slice(0, 160);
  const difficulty = selectedValues(raw.difficulty, ["easy", "medium", "hard"]);
  const calculator = selectedValues(raw.calculator, science ? [] : ["yes", "no"]);
  // Preserve exact legacy links; applying the form carries them as explicit category choices.
  const subtopic = selectedValues(raw.subtopic, subtopics);
  const syllabus = selectedValues(raw.syllabus, syllabusTopics.map(topic => topic.code));
  const specificOptions = [
    ...subtopics.map(title => ({ value: "subtopic:" + title, label: "Specific subtopic: " + title })),
    ...syllabusTopics.map(topic => ({ value: "syllabus:" + topic.code, label: `${topic.code} ${topic.title}` })),
  ];
  const category = selectedValues(raw.category, [...groups.map(group => group.id), ...specificOptions.map(option => option.value)]);
  const selectedCategories = [...new Set([...category, ...subtopic.map(title => "subtopic:" + title), ...syllabus.map(code => "syllabus:" + code)])];
  const selectedGroups = groups.filter(group => selectedCategories.includes(group.id));
  const categoryOptions = [
    ...groups.map(group => ({ value: group.id, label: group.title, detail: [group.syllabusCodes.join(", "), `${group.count} questions`].filter(Boolean).join(" · ") })),
    ...specificOptions.filter(option => selectedCategories.includes(option.value) && !groups.some(group => group.id === option.value)),
  ];
  const allowedLevels = courseChoice ? courseLevel === "sl" ? [coreLevel] : [coreLevel, "ahl"] : [];
  const level = selectedValues(raw.level, allowedLevels);
  const allowedStyles = humanities ? courseLevel === "sl" ? ["paper-1", "paper-2"] : ["paper-1", "paper-2", "paper-3"] : collection.subject === "math-aa-hl" || collection.subject === "math-ai-hl" ? ["short-response", "extended-response", "problem-solving"] : ["short-response", "extended-response"];
  const style = selectedValues(raw.style, !science || humanities ? allowedStyles : []);
  const type = selectedValues(raw.type, science && !humanities ? ["multiple-choice", "structured", "data-based"] : []);
  const filtered = all.filter(q => {
    if (difficulty.length && !difficulty.includes(q.difficulty)) return false;
    if (!isScienceQuestion(q) && style.length && !style.includes(q.examStyle ?? "")) return false;
    if (calculator.length && !calculator.includes(q.calculator ? "yes" : "no")) return false;
    if (selectedCategories.length && !selectedGroups.some(group => questionInTopicGroup(q, group))
      && !selectedCategories.includes("subtopic:" + q.subtopic) && !selectedCategories.includes("syllabus:" + q.syllabusCode)) return false;
    if ((isScienceQuestion(q) || isHumanitiesQuestion(q)) && ((level.length && !level.includes(q.level)) || (type.length && !type.includes(q.questionType)))) return false;
    const scienceTerms = isScienceQuestion(q) ? q.syllabusCode + " " + (q.options?.map(option => option.text).join(" ") ?? "") : q.syllabusCode ?? "";
    return !search || [q.number, q.id, q.title, q.subtopic, q.stem, q.parts.map(p => p.prompt).join(" "), scienceTerms].join(" ").toLowerCase().includes(search.toLowerCase());
  });
  const matches = collection.subject === "math-aa-sl" || collection.subject === "math-ai-sl" ? variedPracticeOrder(filtered) : filtered;
  const pages = Math.max(1, Math.ceil(matches.length / PAGE_SIZE));
  const requestedPage = Number(single(raw.page) || 1);
  const page = Number.isSafeInteger(requestedPage) ? Math.min(pages, Math.max(1, requestedPage)) : 1;
  const visible = matches.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  function filterHref(overrides: Query) {
    return ibFilterHref(pathname, { ...(courseChoice ? { course: courseLevel } : {}), q: search, difficulty, calculator, subtopic, syllabus, level, type, style, category, ...overrides });
  }
  const slQuestions = courseLevel === "sl" ? all : getIbQuestions(id, "sl");
  const slGroups = ibTopicGroups(collection, slQuestions, "sl");
  const slCodes = ibSyllabusSubtopics(collection.subject, collection.topicId, "sl").map(topic => topic.code);
  function categoriesForCourse(target: "sl" | "hl") {
    const targetQuestions = target === "sl" ? slQuestions : getIbQuestions(id, "hl");
    const targetGroups = target === "sl" ? slGroups : ibTopicGroups(collection!, targetQuestions, "hl");
    const targetCodes = ibSyllabusSubtopics(collection!.subject, collection!.topicId, target).map(topic => topic.code);
    return [...new Set([
      ...targetGroups.filter(group => selectedGroups.some(selected => selected.syllabusCodes.some(code => group.syllabusCodes.includes(code)) || selected.subtopics.some(title => group.subtopics.includes(title)))).map(group => group.id),
      ...category.filter(value => targetCodes.some(code => value === "syllabus:" + code) || targetQuestions.some(q => value === "subtopic:" + q.subtopic)),
    ])];
  }
  const slStyles = humanities ? style.filter(value => value !== "paper-3") : style;

  return <ExamShell email={user.email} subject={collection.subject} courseLevel={courseLevel} mathsTopicId={collection.topicId} courseLinks={{ sl: filterHref({ course: "sl", level: level.filter(value => value !== "ahl"), syllabus: syllabus.filter(code => slCodes.includes(code)), subtopic: subtopic.filter(title => slQuestions.some(q => q.subtopic === title)), category: categoriesForCourse("sl"), style: slStyles }), hl: filterHref({ course: "hl", category: categoriesForCourse("hl") }) }}>
    <nav className={styles.breadcrumb} aria-label="Breadcrumb"><Link href={ibHref(collection.subject, "questions", courseLevel)}>Question bank</Link><span>/</span><span>{collection.title}</span></nav>
    <nav className={styles.themeNav} aria-label={`${courseLabel.replace(/ (SL|HL)$/, "")} ${science ? "themes" : "topics"}`}>{IB_COLLECTIONS.filter(item => item.subject === collection.subject).map(item => <Link key={item.id} href={ibCourseHref("/ib/question-bank/" + item.id, collection.subject, courseLevel)} prefetch={false} aria-current={item.id === id ? "page" : undefined}><b>{item.code}</b> {item.title}</Link>)}</nav>
    <div className={styles.bankHeading}><div><span className={styles.overline}>IB {courseLabel.toUpperCase()} · {science ? "THEME" : "TOPIC"} {collection.code}</span><h1>{collection.title}{!/[.!?]$/.test(collection.title) ? <span>.</span> : null}</h1><p>{collection.description}</p></div><div className={styles.bankCount}><strong>{all.length}</strong><span>questions</span></div></div>
    <ExamInstructions subject={collection.subject} />
    <p className={styles.filterHint}>Choose one or more options in each filter. Related subtopics are grouped into {groups.length} study categories.</p>
    <form key={filterHref({})} className={`${styles.filters} ${styles.physicsFilters}`} method="GET" action={pathname}>
      {courseChoice ? <input type="hidden" name="course" value={courseLevel} /> : null}
      <label className={styles.searchFilter}>Search questions<input name="q" type="search" defaultValue={search} placeholder="Keyword or question number" maxLength={160} /></label>
      <MultiSelectFilter name="category" label="Study categories" options={categoryOptions} selected={selectedCategories} allLabel="All categories" wide />
      <MultiSelectFilter name="difficulty" label="Difficulty" selected={difficulty} allLabel="All difficulties" options={[{ value: "easy", label: "Easy" }, { value: "medium", label: "Medium" }, { value: "hard", label: "Hard" }]} />
      {science ? <>
        <MultiSelectFilter name="level" label="Course content" selected={level} allLabel={courseLevel === "sl" ? "All SL content" : "SL + additional HL"} options={[{ value: coreLevel, label: "SL content" }, ...(courseLevel === "hl" ? [{ value: "ahl", label: "Additional HL" }] : [])]} />
        {humanities ? <MultiSelectFilter name="style" label="Exam paper" selected={style} allLabel="All papers" options={allowedStyles.map(value => ({ value, label: "Paper " + value.slice(-1) }))} /> : <MultiSelectFilter name="type" label="Question type" selected={type} allLabel="All question types" options={[{ value: "multiple-choice", label: "Multiple choice" }, { value: "structured", label: "Structured" }, { value: "data-based", label: "Data-based" }]} />}
      </> : <>
        <MultiSelectFilter name="style" label="Response style" selected={style} allLabel="All response styles" options={allowedStyles.map(value => ({ value, label: ({ "short-response": "Short response", "extended-response": "Extended response", "problem-solving": "Problem solving" } as Record<string, string>)[value] }))} />
        <MultiSelectFilter name="calculator" label="Calculator" selected={calculator} allLabel="All questions" options={[{ value: "no", label: "No calculator" }, { value: "yes", label: "Calculator" }]} />
      </>}
      <div className={styles.filterActions}><button type="submit">Apply filters</button><Link href={baseHref} className={styles.reset}>Reset</Link></div>
    </form>
    {selectedCategories.length || difficulty.length || level.length || type.length || style.length || calculator.length ? <div className={styles.activeFilters} aria-label="Applied filters">
      {[...categoryOptions.filter(option => selectedCategories.includes(option.value)).map(option => ({ key: "category", value: option.value, label: option.label })),
        ...Object.entries({ difficulty, level, type, style, calculator }).flatMap(([key, values]) => values.map(value => ({ key, value, label: `${key === "style" ? "Response" : key === "level" ? "Content" : key.charAt(0).toUpperCase() + key.slice(1)}: ${value === "ahl" ? "Additional HL" : value.replaceAll("-", " ")}` })))
      ].map(item => <Link key={`${item.key}:${item.value}`} href={filterHref(item.key === "category" ? { category: selectedCategories.filter(value => value !== item.value), syllabus: [], subtopic: [] } : { [item.key]: ({ difficulty, level, type, style, calculator } as Record<string, string[]>)[item.key].filter(value => value !== item.value) })} prefetch={false} aria-label={`Remove ${item.label}`}>{item.label} <span aria-hidden="true">×</span></Link>)}
    </div> : null}
    <div className={styles.resultsLine}><span>{matches.length ? ((page - 1) * PAGE_SIZE + 1) + "–" + Math.min(page * PAGE_SIZE, matches.length) + " of " + matches.length + " questions" : "No matching questions"}</span><span>Mark schemes open in a new tab ↗</span></div>
    <div className={styles.questionList}>{visible.map(question => {
      const q = questionPrompt(question);
      return <article className={styles.questionCard} id={q.id} key={q.id}>
        <header className={styles.questionHeader}><div><Link href={ibCourseHref("/ib/questions/" + q.id, q.subject, courseLevel)} prefetch={false} className={styles.questionNumber}>Question {q.number}</Link><span className={styles.subtopic}>{q.subtopic}</span></div><QuestionBadges question={q} /></header>
        <div className={styles.questionContent}><QuestionBody question={q} /><aside className={styles.questionActions}><Link href={ibCourseHref("/ib/mark-scheme/" + q.id, q.subject, courseLevel)} target="_blank" rel="noopener noreferrer" prefetch={false} className={styles.schemeButton}>Mark scheme <span aria-hidden="true">↗</span><span className={styles.srOnly}> for question {q.number} (opens in a new tab)</span></Link><span>Written solution<br />with mark allocations</span></aside></div>
      </article>;
    })}</div>
    {!matches.length ? <section className={styles.noResults}><h2>No questions match these filters.</h2><p>Try another keyword, difficulty or category.</p><Link href={baseHref}>Clear filters</Link></section> : null}
    {pages > 1 ? <nav className={styles.pagination} aria-label="Question pages">{page > 1 ? <Link href={filterHref({ page: String(page - 1) })} prefetch={false}>← Previous</Link> : <span /> }<span>Page {page} of {pages}</span>{page < pages ? <Link href={filterHref({ page: String(page + 1) })} prefetch={false}>Next →</Link> : <span />}</nav> : null}
  </ExamShell>;
}
