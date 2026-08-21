"use client";

import { useMemo, useState } from "react";
import styles from "./pathway.module.css";

type Answers = Record<string, string | string[]>;
type Option = { value: string; label: string; note?: string; symbol?: string };
type Question = {
  id: string;
  title: string;
  subtitle?: string;
  multi?: boolean;
  max?: number;
  options: Option[];
};

const YEAR_OPTIONS: Option[] = [
  { value: "y6-8", label: "Year 6–8", note: "Explore and build confidence", symbol: "01" },
  { value: "y9", label: "Year 9", note: "Start shaping your direction", symbol: "02" },
  { value: "y10", label: "Year 10", note: "Build strong GCSE foundations", symbol: "03" },
  { value: "y11", label: "Year 11", note: "Prepare for the next academic step", symbol: "04" },
  { value: "y12", label: "Year 12", note: "Turn goals into an application plan", symbol: "05" },
  { value: "y13", label: "Year 13", note: "Focus your final preparation", symbol: "06" },
  { value: "finished", label: "Finished school", note: "Plan the next application cycle", symbol: "07" },
];

const INTERESTS: Option[] = [
  { value: "maths", label: "Mathematics", note: "Patterns, logic and problem-solving", symbol: "∑" },
  { value: "physics", label: "Physics", note: "Forces, systems and how things work", symbol: "φ" },
  { value: "chemistry", label: "Chemistry", note: "Matter, reactions and molecular ideas", symbol: "C" },
  { value: "biology", label: "Biology", note: "Life, health and living systems", symbol: "B" },
  { value: "computing", label: "Computer Science", note: "Algorithms, software and technology", symbol: "<>" },
  { value: "economics", label: "Economics & Business", note: "Markets, decisions and numbers", symbol: "↗" },
  { value: "humanities", label: "Humanities", note: "People, ideas, history and society", symbol: "H" },
  { value: "exploring", label: "I’m still exploring", note: "That is completely fine", symbol: "?" },
];

const DIRECTIONS: Option[] = [
  { value: "engineering", label: "Engineering", note: "Design, systems and applied science", symbol: "E" },
  { value: "computing", label: "Computer Science", note: "Software, algorithms and AI", symbol: "CS" },
  { value: "economics", label: "Economics / Finance", note: "Markets, data and decision-making", symbol: "£" },
  { value: "maths", label: "Mathematics", note: "Pure and applied mathematical thinking", symbol: "π" },
  { value: "medicine", label: "Medicine / Health", note: "Science with direct human impact", symbol: "+" },
  { value: "natural-sciences", label: "Natural Sciences", note: "Keep several sciences open", symbol: "N" },
  { value: "physics", label: "Physics", note: "Fundamental physical systems", symbol: "P" },
  { value: "chemistry", label: "Chemistry", note: "Molecular and material science", symbol: "Ch" },
  { value: "biology", label: "Biology", note: "Life sciences and research", symbol: "Bio" },
  { value: "humanities", label: "Humanities / Social Sciences", note: "Ideas, society and communication", symbol: "HS" },
  { value: "creative", label: "Creative / non-academic route", note: "Design, arts, media or another direction", symbol: "Cr" },
  { value: "unsure", label: "I’m not sure yet", note: "Help me explore rather than decide", symbol: "?" },
];

const AMBITION: Option[] = [
  { value: "high", label: "Explore the most selective universities", note: "Oxford, Cambridge, Imperial, LSE and similar", symbol: "A" },
  { value: "strong", label: "Strong UK universities", note: "Russell Group and other leading choices", symbol: "B" },
  { value: "broad", label: "Keep my options broad", note: "Find a good academic and personal fit", symbol: "C" },
  { value: "unsure", label: "I’m not sure — help me decide", note: "Use my answers to suggest a sensible level", symbol: "?" },
];

const BLOCKERS: Option[] = [
  { value: "hard", label: "Harder questions", note: "I understand lessons but struggle when problems get unfamiliar", symbol: "01" },
  { value: "gaps", label: "Topic gaps", note: "Some foundations need strengthening", symbol: "02" },
  { value: "mistakes", label: "Avoidable mistakes", note: "I often know the method but lose marks", symbol: "03" },
  { value: "timing", label: "Exam timing", note: "Speed and decision-making are the main issue", symbol: "04" },
  { value: "confidence", label: "Confidence", note: "I want to feel more secure and consistent", symbol: "05" },
  { value: "challenge", label: "I need more challenge", note: "School work often feels too comfortable", symbol: "06" },
  { value: "none", label: "Nothing obvious right now", note: "I mainly want direction and a plan", symbol: "07" },
];

const SUPPORT: Option[] = [
  { value: "academic", label: "Getting stronger academically", note: "Raise grades and deepen subject understanding", symbol: "01" },
  { value: "admissions", label: "Preparing for admissions tests", note: "Only where relevant to my target course", symbol: "02" },
  { value: "universities", label: "Choosing universities", note: "Build a sensible shortlist", symbol: "03" },
  { value: "subjects", label: "Choosing subjects", note: "GCSE / A-level / IB subject direction", symbol: "04" },
  { value: "plan", label: "Building an application plan", note: "Know what to do and when", symbol: "05" },
  { value: "organisation", label: "Staying consistent and organised", note: "Turn ambition into weekly progress", symbol: "06" },
  { value: "explore", label: "I’m not sure", note: "Give me useful guidance first", symbol: "07" },
];

const LEARNING: Option[] = [
  { value: "one", label: "Personal 1:1 guidance", note: "A mentor who adapts the plan around me", symbol: "1:1" },
  { value: "group", label: "Small-group learning", note: "Structure plus other motivated students", symbol: "G" },
  { value: "digital", label: "Independent online practice", note: "Flexible practice and progress tracking", symbol: "D" },
  { value: "blend", label: "A combination", note: "Mentoring plus digital work between sessions", symbol: "+" },
  { value: "unsure", label: "I’m not sure yet", note: "Recommend what fits my situation", symbol: "?" },
];

function yearRank(year: string) {
  return ({ "y6-8": 8, y9: 9, y10: 10, y11: 11, y12: 12, y13: 13, finished: 14 } as Record<string, number>)[year] || 8;
}

function makeQuestions(answers: Answers): Question[] {
  const year = String(answers.year || "");
  const rank = yearRank(year);
  const interests = (answers.interests || []) as string[];
  const direction = String(answers.direction || "");
  const mathsHeavy = interests.includes("maths") || interests.includes("physics") || interests.includes("computing") || ["engineering", "computing", "economics", "maths", "physics", "natural-sciences"].includes(direction);

  const questions: Question[] = [
    { id: "year", title: "What year are you currently in?", subtitle: "We’ll adapt the pathway to where you are now.", options: YEAR_OPTIONS },
    { id: "interests", title: "Which subjects excite you most?", subtitle: "Choose up to three. You do not need to have your future figured out.", multi: true, max: 3, options: INTERESTS },
    { id: "direction", title: rank <= 9 ? "Which direction sounds most exciting to explore?" : "What are you currently thinking of studying at university?", subtitle: rank <= 9 ? "This is about curiosity, not committing to a degree." : "Choose the closest fit — you can still keep options open.", options: DIRECTIONS },
    { id: "ambition", title: "How ambitious would you like your university options to be?", subtitle: "This helps us set the level of challenge without pretending admission can be predicted by a quiz.", options: AMBITION },
  ];

  if (rank <= 9) {
    questions.push({
      id: "readiness",
      title: "How are you finding Maths and Science at school?",
      subtitle: "Pick the description that feels most accurate.",
      options: [
        { value: "very-strong", label: "Usually comfortable", note: "I’m often ready for more challenge", symbol: "A" },
        { value: "strong", label: "Doing well", note: "I’m confident but still have room to stretch", symbol: "B" },
        { value: "mixed", label: "It depends on the topic", note: "Some areas are much easier than others", symbol: "C" },
        { value: "building", label: "Some topics feel difficult", note: "I want stronger foundations", symbol: "D" },
      ],
    });
  } else if (rank <= 11) {
    questions.push({
      id: "readiness",
      title: "What grades are you currently working around?",
      subtitle: "A broad range is enough — no need to enter every subject.",
      options: [
        { value: "very-strong", label: "Mostly 8–9", note: "Strong current attainment", symbol: "9" },
        { value: "strong", label: "Mostly 6–7", note: "Good base with room to move higher", symbol: "7" },
        { value: "mixed", label: "Mostly 4–5", note: "Focus first on stronger GCSE foundations", symbol: "5" },
        { value: "building", label: "Mixed / not sure", note: "We’ll keep recommendations practical", symbol: "?" },
      ],
    });
  } else {
    questions.push({
      id: "readiness",
      title: "Where are your current predicted grades?",
      subtitle: "Choose the closest broad band. Requirements vary by university and course.",
      options: [
        { value: "very-strong", label: "A*A*A* / equivalent", note: "Very strong academic position", symbol: "A*" },
        { value: "strong", label: "A*AA–AAA / equivalent", note: "Strong position for many selective courses", symbol: "A" },
        { value: "mixed", label: "AAB–ABB / equivalent", note: "University choice and grade strategy matter", symbol: "B" },
        { value: "building", label: "Below that / not sure", note: "Prioritise academic improvement and fit", symbol: "?" },
      ],
    });
  }

  questions.push(
    { id: "blocker", title: "What tends to hold you back most?", subtitle: "This is often more useful than another grade question.", options: BLOCKERS },
    { id: "support", title: "What would you most like help with right now?", subtitle: "Your final plan should respond to this — not simply advertise every service.", options: SUPPORT },
  );

  if (rank >= 12 && mathsHeavy) {
    questions.push({
      id: "tests",
      title: "How far are you with admissions-test preparation?",
      subtitle: "TMUA or ESAT should only appear in your plan where your eventual course and university actually use them.",
      options: [
        { value: "structured", label: "Already following a structured plan", note: "I want to improve performance and consistency", symbol: "04" },
        { value: "papers", label: "I’ve tried past-paper style questions", note: "I have some exposure but need a clearer system", symbol: "03" },
        { value: "aware", label: "I know about the tests but haven’t started", note: "I need to understand what matters", symbol: "02" },
        { value: "new", label: "I’m new to this", note: "Tell me whether a test is relevant first", symbol: "01" },
      ],
    });
  }

  questions.push({ id: "learning", title: "What kind of support tends to work best for you?", subtitle: "This helps us suggest a realistic way to execute the plan.", options: LEARNING });
  return questions;
}

const UNIVERSITY_SETS: Record<string, { dream: string[]; strong: string[]; explore: string[] }> = {
  engineering: { dream: ["Cambridge", "Imperial"], strong: ["UCL", "Bath", "Bristol"], explore: ["Southampton", "Manchester", "Sheffield"] },
  computing: { dream: ["Oxford", "Cambridge", "Imperial"], strong: ["UCL", "Warwick", "Bath"], explore: ["Bristol", "Southampton", "Manchester"] },
  economics: { dream: ["Cambridge", "LSE", "Oxford"], strong: ["UCL", "Warwick", "Bath"], explore: ["Bristol", "Durham", "Nottingham"] },
  maths: { dream: ["Cambridge", "Oxford", "Imperial"], strong: ["Warwick", "UCL", "Bath"], explore: ["Bristol", "Durham", "Manchester"] },
  medicine: { dream: ["Oxford", "Cambridge", "Imperial"], strong: ["UCL", "King’s", "Bristol"], explore: ["Manchester", "Birmingham", "Southampton"] },
  "natural-sciences": { dream: ["Cambridge", "Oxford", "Imperial"], strong: ["UCL", "Durham", "Bath"], explore: ["Bristol", "Manchester", "York"] },
  physics: { dream: ["Oxford", "Cambridge", "Imperial"], strong: ["UCL", "Durham", "Warwick"], explore: ["Bristol", "Manchester", "Southampton"] },
  chemistry: { dream: ["Oxford", "Cambridge", "Imperial"], strong: ["UCL", "Durham", "Warwick"], explore: ["Bristol", "Manchester", "York"] },
  biology: { dream: ["Oxford", "Cambridge", "Imperial"], strong: ["UCL", "Edinburgh", "Bristol"], explore: ["Manchester", "York", "Nottingham"] },
  humanities: { dream: ["Oxford", "Cambridge", "LSE"], strong: ["UCL", "Durham", "Warwick"], explore: ["Bristol", "Manchester", "Leeds"] },
  creative: { dream: [], strong: [], explore: [] },
  unsure: { dream: [], strong: [], explore: [] },
};

function courseName(direction: string) {
  return ({
    engineering: "Engineering & Technology",
    computing: "Computer Science & Technology",
    economics: "Economics, Finance & Quantitative Social Science",
    maths: "Mathematics",
    medicine: "Medicine & Health Sciences",
    "natural-sciences": "Natural Sciences",
    physics: "Physics",
    chemistry: "Chemistry",
    biology: "Biological Sciences",
    humanities: "Humanities & Social Sciences",
    creative: "Creative / alternative pathways",
    unsure: "Exploration before specialisation",
  } as Record<string, string>)[direction] || "Exploration before specialisation";
}

function buildResult(answers: Answers) {
  const year = String(answers.year || "y6-8");
  const rank = yearRank(year);
  const direction = String(answers.direction || "unsure");
  const readiness = String(answers.readiness || "mixed");
  const ambition = String(answers.ambition || "broad");
  const blocker = String(answers.blocker || "none");
  const support = String(answers.support || "explore");
  const learning = String(answers.learning || "unsure");
  const interests = (answers.interests || []) as string[];
  const mathsInterest = interests.includes("maths") || interests.includes("physics") || interests.includes("computing") || ["engineering", "computing", "economics", "maths", "physics", "natural-sciences"].includes(direction);
  const academicNeed = ["building", "mixed"].includes(readiness) || ["gaps", "confidence", "hard", "mistakes", "timing"].includes(blocker) || support === "academic";
  const strongYoungMaths = rank <= 10 && mathsInterest && ["very-strong", "strong"].includes(readiness);
  const stage = rank <= 9 ? "DISCOVER" : rank <= 11 ? "BUILD" : "APPLY";
  const uni = UNIVERSITY_SETS[direction] || UNIVERSITY_SETS.unsure;

  let headline = "Build a direction before narrowing your options.";
  if (direction !== "unsure" && direction !== "creative") {
    headline = rank <= 9
      ? `You have a promising early direction in ${courseName(direction)}.`
      : `Your answers point toward ${courseName(direction)} with a clear next academic milestone.`;
  } else if (direction === "creative") {
    headline = "Your best next step is exploration, portfolio-building and understanding the routes that fit you.";
  }

  const timeline: string[] = [];
  if (rank <= 9) {
    timeline.push("Explore subjects deeply", mathsInterest ? "Build problem-solving confidence" : "Develop strong core skills", "Choose GCSE subjects thoughtfully", "Keep future pathways open");
  } else if (rank <= 11) {
    timeline.push("Strengthen GCSE performance", "Choose post-16 subjects deliberately", mathsInterest ? "Add stretch problem-solving where useful" : "Build depth in your strongest subjects", "Review university directions after stronger evidence");
  } else {
    timeline.push("Protect predicted grades", "Refine course and university choices", mathsInterest ? "Check current admissions-test requirements" : "Build course-specific evidence", "Prepare applications and interviews strategically");
  }

  const actions: string[] = [];
  if (rank <= 10 && strongYoungMaths) actions.push("Try UKMT-style challenge problems to stretch mathematical reasoning without rushing into university admissions tests.");
  if (rank <= 11 && academicNeed) actions.push("Prioritise GCSE subject mastery first: close topic gaps, improve difficult-question technique and make marks more consistent.");
  if (rank <= 11 && !academicNeed) actions.push("Keep school performance strong while adding stretch work only where it remains enjoyable and useful.");
  if (rank >= 12 && mathsInterest) actions.push("Check the current admissions-test requirements for each exact course before committing time to TMUA or ESAT preparation.");
  if (rank >= 12 && academicNeed) actions.push("Raise academic consistency before letting admissions-test preparation crowd out your core subjects.");
  if (["creative", "unsure"].includes(direction)) actions.push("Explore real courses, careers and sample university modules before paying for specialist tutoring or test preparation.");
  if (support === "universities" || support === "plan") actions.push("Build a shortlist with aspirational, strong-fit and broader options rather than relying on one dream university.");
  if (actions.length < 3) actions.push("Review this pathway again after your next meaningful grade, subject-choice or course decision.");
  while (actions.length < 3) actions.push("Keep a short record of topics and tasks that repeatedly feel difficult so your next intervention targets the real bottleneck.");

  let mentoringTitle = "No tutoring recommendation needed right now";
  let mentoringText = "Your answers suggest that useful guidance and exploration may be more valuable than adding tuition immediately.";
  let tutoringRecommended = false;

  if (direction !== "creative" && academicNeed) {
    tutoringRecommended = true;
    mentoringTitle = rank <= 11 ? "Recommended foundation: personalised subject mentoring" : "Recommended foundation: 1:1 academic mentoring";
    mentoringText = rank <= 11
      ? "A mentor can build a focused GCSE programme around the subjects and weak points that are actually limiting your marks, then increase challenge as confidence improves."
      : "A mentor can protect subject grades, diagnose gaps and coordinate harder problem-solving or admissions preparation around your exact university goals.";
  } else if (strongYoungMaths) {
    tutoringRecommended = true;
    mentoringTitle = "Recommended: maths enrichment and mentoring";
    mentoringText = "The goal is not early exam drilling. A strong mentor can deepen reasoning, introduce UKMT-style problems and keep mathematics challenging without making it feel narrow or repetitive.";
  } else if (rank >= 12 && mathsInterest && support === "admissions") {
    tutoringRecommended = true;
    mentoringTitle = "Recommended: admissions preparation after requirements are confirmed";
    mentoringText = "Once your exact target courses are fixed, structured 1:1 preparation can combine subject depth, timed problem-solving and digital practice for the relevant test rather than pushing both TMUA and ESAT automatically.";
  }

  const testText = rank < 12
    ? (strongYoungMaths ? "UKMT-style enrichment is a sensible stretch goal now. TMUA/ESAT preparation can wait until your university pathway actually requires it." : "Admissions tests are not a priority at this stage. Focus on subject strength, confidence and good choices.")
    : (mathsInterest ? "TMUA or ESAT may become relevant for some selective maths-heavy courses. Requirements change, so confirm the exact current requirement for every university/course before preparing." : "TMUA and ESAT are not a natural priority for the direction you selected unless a specific course later requires one.");

  const universityVisible = !["creative", "unsure"].includes(direction) && rank >= 10;
  const showDream = ambition === "high" || readiness === "very-strong";
  const code = `TS-${direction.slice(0, 3).toUpperCase()}-${year.replace("y", "")}-${Math.abs((direction + year + readiness + blocker).split("").reduce((a, c) => a + c.charCodeAt(0), 0)).toString(36).toUpperCase()}`;

  return { stage, headline, course: courseName(direction), timeline, actions: actions.slice(0, 3), mentoringTitle, mentoringText, tutoringRecommended, testText, uni, universityVisible, showDream, code, learning };
}

export default function PathwayClient() {
  const [answers, setAnswers] = useState<Answers>({});
  const [step, setStep] = useState(-1);
  const [done, setDone] = useState(false);
  const questions = useMemo(() => makeQuestions(answers), [answers]);
  const result = useMemo(() => buildResult(answers), [answers]);

  const current = questions[step];
  const value = current ? answers[current.id] : undefined;
  const canContinue = current ? (current.multi ? Array.isArray(value) && value.length > 0 : Boolean(value)) : true;

  function choose(option: string) {
    if (!current) return;
    if (current.multi) {
      const existing = Array.isArray(value) ? [...value] : [];
      const found = existing.includes(option);
      if (found) setAnswers({ ...answers, [current.id]: existing.filter((v) => v !== option) });
      else if (existing.length < (current.max || 3)) setAnswers({ ...answers, [current.id]: [...existing, option] });
      return;
    }
    setAnswers({ ...answers, [current.id]: option });
  }

  function next() {
    if (step === -1) {
      setStep(0);
      return;
    }
    if (!canContinue) return;
    const updatedQuestions = makeQuestions(answers);
    if (step >= updatedQuestions.length - 1) setDone(true);
    else setStep(step + 1);
  }

  function back() {
    if (done) {
      setDone(false);
      setStep(Math.max(0, questions.length - 1));
      return;
    }
    if (step <= 0) setStep(-1);
    else setStep(step - 1);
  }

  function restart() {
    setAnswers({});
    setStep(-1);
    setDone(false);
  }

  const whatsappText = encodeURIComponent(`Hi Thriving Scholars, I completed the University Pathway tool. My pathway code is ${result.code}. I’d like to discuss the recommendations.`);
  const whatsappUrl = `https://wa.me/447459070019?text=${whatsappText}`;

  return (
    <main className={styles.shell} data-ts-pathway-build="2026-08-22-live-v1">
      <header className={styles.topbar}>
        <a className={styles.brand} href="https://www.thrivingscholars.com" target="_blank" rel="noreferrer">
          <span className={styles.brandMark}>TS</span>
          <span><strong>Thriving Scholars</strong><small>UNIVERSITY PATHWAY</small></span>
        </a>
        {step >= 0 && !done && <div className={styles.progressText}>{Math.min(step + 1, questions.length)} of {questions.length}</div>}
      </header>

      {!done && step >= 0 && <div className={styles.progress}><span style={{ width: `${((step + 1) / questions.length) * 100}%` }} /></div>}

      {step === -1 && !done && (
        <section className={styles.hero}>
          <div className={styles.heroCopy}>
            <div className={styles.eyebrow}>A 2–3 MINUTE PERSONALISED DIAGNOSTIC</div>
            <h1>Where could your future take you?</h1>
            <p>Answer a few thoughtful questions and we’ll build a useful academic and university pathway — based on your stage, interests, ambitions and current needs.</p>
            <div className={styles.heroPoints}>
              <span>No fake acceptance probabilities</span>
              <span>No unnecessary admissions-test pushing</span>
              <span>Useful for students and parents</span>
            </div>
            <button className={styles.primary} onClick={next}>Build my pathway <span>→</span></button>
            <small className={styles.muted}>Exploratory guidance, not an admissions guarantee.</small>
          </div>
          <div className={styles.heroArt} aria-hidden="true">
            <div className={styles.sun} />
            <div className={styles.pathLine} />
            <div className={`${styles.milestone} ${styles.m1}`}>NOW</div>
            <div className={`${styles.milestone} ${styles.m2}`}>BUILD</div>
            <div className={`${styles.milestone} ${styles.m3}`}>APPLY</div>
            <div className={styles.uniIcon}><span /><span /><span /><span /></div>
          </div>
        </section>
      )}

      {!done && step >= 0 && current && (
        <section className={styles.questionWrap}>
          <div className={styles.questionHeader}>
            <div className={styles.eyebrow}>YOUR PATHWAY · {yearRank(String(answers.year || "")) <= 9 ? "DISCOVER" : yearRank(String(answers.year || "")) <= 11 ? "BUILD" : "APPLY"}</div>
            <h2>{current.title}</h2>
            {current.subtitle && <p>{current.subtitle}</p>}
          </div>
          <div className={styles.options}>
            {current.options.map((o) => {
              const selected = current.multi ? Array.isArray(value) && value.includes(o.value) : value === o.value;
              return (
                <button key={o.value} className={`${styles.option} ${selected ? styles.selected : ""}`} onClick={() => choose(o.value)}>
                  <span className={styles.symbol}>{o.symbol || "•"}</span>
                  <span className={styles.optionText}><strong>{o.label}</strong>{o.note && <small>{o.note}</small>}</span>
                  <span className={styles.tick}>{selected ? "✓" : ""}</span>
                </button>
              );
            })}
          </div>
          <div className={styles.navRow}>
            <button className={styles.secondary} onClick={back}>← Back</button>
            <button className={styles.primary} disabled={!canContinue} onClick={next}>{step === questions.length - 1 ? "Build my pathway" : "Continue"} <span>→</span></button>
          </div>
        </section>
      )}

      {done && (
        <section className={styles.report}>
          <div className={styles.reportHero}>
            <div className={styles.eyebrow}>YOUR PERSONALISED PATHWAY · {result.stage}</div>
            <h1>{result.headline}</h1>
            <p className={styles.reportLead}>{result.course}</p>
            <div className={styles.code}>PATHWAY CODE <strong>{result.code}</strong></div>
          </div>

          <div className={styles.sectionCard}>
            <div className={styles.sectionLabel}>YOUR ROADMAP</div>
            <div className={styles.timeline}>
              {result.timeline.map((item, i) => <div key={item} className={styles.timelineItem}><span>{String(i + 1).padStart(2, "0")}</span><strong>{item}</strong></div>)}
            </div>
          </div>

          {result.universityVisible && (
            <div className={styles.sectionCard}>
              <div className={styles.sectionLabel}>UNIVERSITIES TO EXPLORE</div>
              <p className={styles.sectionIntro}>A starting shortlist, not a prediction. Always check current course requirements and fit.</p>
              <div className={styles.uniGrid}>
                {result.showDream && result.uni.dream.length > 0 && <div><small>ASPIRATIONAL</small><strong>{result.uni.dream.join(" · ")}</strong></div>}
                <div><small>STRONG OPTIONS</small><strong>{result.uni.strong.join(" · ")}</strong></div>
                <div><small>EXPLORE</small><strong>{result.uni.explore.join(" · ")}</strong></div>
              </div>
            </div>
          )}

          <div className={styles.sectionCard}>
            <div className={styles.sectionLabel}>ADMISSIONS & ENRICHMENT</div>
            <h3>{result.stage === "APPLY" ? "Use tests selectively." : "Build the right kind of stretch."}</h3>
            <p>{result.testText}</p>
          </div>

          <div className={styles.sectionCard}>
            <div className={styles.sectionLabel}>YOUR NEXT 3 ACTIONS</div>
            <ol className={styles.actions}>{result.actions.map((a) => <li key={a}>{a}</li>)}</ol>
          </div>

          <div className={`${styles.sectionCard} ${styles.mentorCard}`}>
            <div className={styles.sectionLabel}>HOW THRIVING SCHOLARS COULD HELP</div>
            <h3>{result.mentoringTitle}</h3>
            <p>{result.mentoringText}</p>
            {result.tutoringRecommended && <div className={styles.mentorFlow}><span>MENTOR</span><b>→</b><span>TARGETED PRACTICE</span><b>→</b><span>PROGRESS REVIEW</span><b>→</b><span>NEXT PLAN</span></div>}
          </div>

          <div className={styles.contactCard}>
            <div>
              <div className={styles.eyebrow}>TAKE THE NEXT STEP</div>
              <h2>Want to talk through this pathway?</h2>
              <p>Send us your pathway code and we can discuss the student’s subjects, current level and goals in a free consultation.</p>
            </div>
            <div className={styles.contactActions}>
              <a className={styles.whatsapp} href={whatsappUrl} target="_blank" rel="noreferrer">Message on WhatsApp →</a>
              <a className={styles.contactLink} href="tel:+447459070019">+44 7459 070019</a>
              <a className={styles.contactLink} href="https://www.thrivingscholars.com" target="_blank" rel="noreferrer">www.thrivingscholars.com</a>
            </div>
          </div>

          <div className={styles.reportFooter}>
            <button className={styles.secondary} onClick={back}>← Edit last answer</button>
            <button className={styles.secondary} onClick={restart}>Start again</button>
          </div>
        </section>
      )}
    </main>
  );
}
