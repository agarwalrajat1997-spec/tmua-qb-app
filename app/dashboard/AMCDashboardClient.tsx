"use client";

import { useState } from "react";
import styles from "./dashboard.module.css";

type Props = {
  email?: string | null;
  hasTmua?: boolean;
  initialSection?: "practice-tests" | "resources" | null;
};

type AMCPaper = "AMC 8" | "AMC 10" | "AMC 12";
type AMCView = AMCPaper | "Practice Tests" | "Resources";

const PAPERS: Array<{
  paper: AMCPaper;
  label: string;
  step: string;
  description: string;
}> = [
  {
    paper: "AMC 8",
    label: "AMC 8 Question Bank",
    step: "1",
    description: "Middle-school AMC practice with focused problem solving, number sense, geometry and counting.",
  },
  {
    paper: "AMC 10",
    label: "AMC 10 Question Bank",
    step: "2",
    description: "AMC 10 practice for algebra, geometry, combinatorics, probability and contest-style reasoning.",
  },
  {
    paper: "AMC 12",
    label: "AMC 12 Question Bank",
    step: "3",
    description: "AMC 12 practice with higher-level algebra, functions, geometry and advanced contest reasoning.",
  },
];

const PRACTICE_TESTS = [
  {
    title: "AMC 10 Topical Test 1",
    level: "AMC 8 + AMC 10 · Number Theory",
    detail: "Focused number theory practice covering factors, divisibility and sequences.",
    tags: ["25 questions", "75 minutes", "Worked solutions"],
    href: "/amc-practice-tests/tests/amc-10-mock-test-1/index.html",
  },
  {
    title: "AMC 10 Topical Test 2",
    level: "AMC 8 + AMC 10 · Number Theory",
    detail: "A second focused paper covering number patterns, factors and reasoning.",
    tags: ["25 questions", "75 minutes", "Instant score"],
    href: "/amc-practice-tests/tests/amc-10-topical-test-2/index.html",
  },
  {
    title: "AMC 10 Topical Test 3",
    level: "AMC 8 + AMC 10 · Algebra",
    detail: "Arithmetic and algebra questions with original notation preserved.",
    tags: ["25 questions", "75 minutes", "Instant score"],
    href: "/amc-practice-tests/tests/amc-10-topical-test-3/index.html",
  },
  {
    title: "AMC 10 Topical Test 4",
    level: "AMC 8 + AMC 10 · Algebra",
    detail: "A second arithmetic and algebra paper for timed contest practice.",
    tags: ["25 questions", "75 minutes", "Worked solutions"],
    href: "/amc-practice-tests/tests/amc-10-topical-test-4/index.html",
  },
  {
    title: "AMC 10 Topical Test 5",
    level: "AMC 8 + AMC 10 · Geometry",
    detail: "Geometry practice covering angles, circles and spatial reasoning.",
    tags: ["25 questions", "75 minutes", "Instant score"],
    href: "/amc-practice-tests/tests/amc-10-topical-test-5/index.html",
  },
  {
    title: "AMC 10 Topical Test 6",
    level: "AMC 8 + AMC 10 · Geometry",
    detail: "A second geometry paper covering angles, circles and spatial reasoning.",
    tags: ["25 questions", "75 minutes", "Worked solutions"],
    href: "/amc-practice-tests/tests/amc-10-topical-test-6/index.html",
  },
  {
    title: "AMC 10 Topical Test 7",
    level: "AMC 8 + AMC 10 · Combinatorics",
    detail: "Timed combinatorics and probability practice with instant scoring.",
    tags: ["25 questions", "75 minutes", "Instant score"],
    href: "/amc-practice-tests/tests/amc-10-topical-test-7/index.html",
  },
  {
    title: "AMC 10 Topical Test 8",
    level: "AMC 8 + AMC 10 · Logic",
    detail: "Logic and structured reasoning questions with full worked solutions.",
    tags: ["25 questions", "75 minutes", "Worked solutions"],
    href: "/amc-practice-tests/tests/amc-10-topical-test-8/index.html",
  },
  {
    title: "AMC 8 Full Mock Test 1",
    level: "AMC 8 · All Topics",
    detail: "A complete AMC 8-style paper covering the full topic range.",
    tags: ["25 questions", "40 minutes", "Instant score"],
    href: "/amc-practice-tests/tests/amc-8-full-mock-test-1/index.html",
  },
  {
    title: "AMC 8 Full Mock Test 2",
    level: "AMC 8 · All Topics",
    detail: "A second complete AMC 8-style paper with clear diagrams and worked solutions.",
    tags: ["25 questions", "40 minutes", "Worked solutions"],
    href: "/amc-practice-tests/tests/amc-8-full-mock-test-2/index.html",
  },
  {
    title: "Pre-AMC 8 Mock Test",
    level: "AMC 8 Foundations",
    detail: "A full timed foundation paper for students building toward AMC 8.",
    tags: ["25 questions", "75 minutes", "Instant score"],
    href: "/amc-practice-tests/tests/pre-amc-8-mock-test/index.html",
  },
  {
    title: "AMC 10 Diagnostic Test",
    level: "AMC 10 · All Topics",
    detail: "Identify strengths, missed topics and the highest-priority areas to review.",
    tags: ["25 questions", "75 minutes", "Topic analysis"],
    href: "/amc-practice-tests/tests/amc-10-diagnostic-test/index.html",
  },
] as const;

const PRACTICE_TEST_SECTIONS = [
  {
    heading: "Diagnostic Tests",
    description:
      "Start here to identify the right level and the topics to prioritise next.",
    groups: [{ heading: "Pre-AMC 8 & AMC 10", tests: PRACTICE_TESTS.slice(10, 12) }],
  },
  {
    heading: "AMC 8 Full-Length Practice",
    description:
      "Rehearse the complete 25-question AMC 8 format under a 40-minute time limit.",
    groups: [{ heading: "Full Mock Tests", tests: PRACTICE_TESTS.slice(8, 10) }],
  },
  {
    heading: "AMC 10 Topical Practice Tests",
    description:
      "Build one contest skill at a time with eight focused 75-minute papers.",
    groups: [
      { heading: "Number Theory", tests: PRACTICE_TESTS.slice(0, 2) },
      { heading: "Algebra", tests: PRACTICE_TESTS.slice(2, 4) },
      { heading: "Geometry", tests: PRACTICE_TESTS.slice(4, 6) },
      { heading: "Combinatorics & Logic", tests: PRACTICE_TESTS.slice(6, 8) },
    ],
  },
] as const;

const AMC_RESOURCE_SECTIONS = [
  {
    heading: "AMC 8",
    description: "Quick revision and a deep archive for the AMC 8 syllabus.",
    resources: [
      {
        title: "AMC 8 Comprehensive Cheat Sheet",
        description:
          "An 11-page Thriving Scholars quick reference covering core knowledge, high-yield methods and contest strategy.",
        kind: "Quick reference",
        pages: 11,
        href: "/amc-resources/amc-8-comprehensive-cheat-sheet-thriving-scholars.pdf",
      },
      {
        title: "AMC 8 Compendium",
        description:
          "A 307-page AMC 8 problem compendium spanning 1985–2026 for structured long-form practice.",
        kind: "Problem archive",
        pages: 307,
        href: "/amc-resources/amc-8-compendium.pdf",
      },
    ],
  },
  {
    heading: "AMC 10",
    description: "Formula review and an extensive AMC 10 competition archive.",
    resources: [
      {
        title: "AMC 10 Comprehensive Cheat Sheet",
        description:
          "A 10-page Thriving Scholars reference for formulas, recurring structures and late-question techniques.",
        kind: "Quick reference",
        pages: 10,
        href: "/amc-resources/amc-10-comprehensive-cheat-sheet-thriving-scholars.pdf",
      },
      {
        title: "AMC 10 Compendium",
        description:
          "A comprehensive 757-page AMC 10 problem collection for sustained contest preparation.",
        kind: "Problem archive",
        pages: 757,
        href: "/amc-resources/amc-10-compendium.pdf",
      },
    ],
  },
  {
    heading: "AMC 12",
    description: "Advanced revision and past-problem practice for AMC 12.",
    resources: [
      {
        title: "AMC 12 Comprehensive Cheat Sheet",
        description:
          "A 10-page Thriving Scholars toolkit covering algebra, trigonometry, geometry, number theory and combinatorics.",
        kind: "Quick reference",
        pages: 10,
        href: "/amc-resources/amc-12-comprehensive-cheat-sheet-thriving-scholars.pdf",
      },
      {
        title: "AMC 12 Compendium",
        description:
          "A 471-page AMC 12 problem compendium covering the 2008–2025 competition years.",
        kind: "Problem archive",
        pages: 471,
        href: "/amc-resources/amc-12-compendium.pdf",
      },
    ],
  },
] as const;

function bankUrl(paper: AMCPaper) {
  return `/amc-question-bank?paper=${encodeURIComponent(paper)}`;
}

export default function AMCDashboardClient({ email, hasTmua, initialSection }: Props) {
  const [active, setActive] = useState<AMCView>(
    initialSection === "practice-tests"
      ? "Practice Tests"
      : initialSection === "resources"
        ? "Resources"
        : "AMC 8",
  );

  const activePaper =
    active === "Practice Tests" || active === "Resources"
      ? null
      : PAPERS.find((paper) => paper.paper === active) || PAPERS[0];

  function selectView(view: AMCView) {
    setActive(view);

    const url = new URL(window.location.href);
    if (view === "Practice Tests") url.searchParams.set("section", "practice-tests");
    else if (view === "Resources") url.searchParams.set("section", "resources");
    else url.searchParams.delete("section");
    window.history.replaceState({}, "", url);
  }

  function logout() {
    window.location.href = "/api/logout";
  }

  return (
    <div className={styles.page} data-ui="TS_AMC_DASH_PORTAL_V2">
      <div className={styles.topbar}>
        <div className={styles.brand}>
          <div className={styles.brandName}>Thriving Scholars</div>
          <div className={styles.brandTag}>AMC Student Portal</div>
        </div>

        <div className={styles.right}>
          <div className={styles.pill}>
            <b>Signed in:</b> {email || "—"}
          </div>
          <button className={`${styles.btn} ${styles.btnPrimary}`} onClick={logout}>
            Logout
          </button>
        </div>
      </div>

      <div className={styles.shell}>
        <aside className={styles.sidebar}>
          <div className={styles.sideTitle}>
            Your AMC
            <br />
            Workspace
          </div>

          <div className={styles.sideSub}>
            Question banks and timed AMC 8 + AMC 10 practice tests in one focused workspace.
          </div>

          <ul className={styles.nav}>
            {PAPERS.map((p) => (
              <li key={p.paper}>
                <button
                  className={`${styles.navBtn} ${active === p.paper ? styles.navBtnOn : ""}`}
                  onClick={() => selectView(p.paper)}
                  type="button"
                  title={p.label}
                >
                  <span className={styles.step}>{p.step}</span>
                  <span className={styles.navLabel}>{p.label}</span>
                </button>
              </li>
            ))}
            <li>
              <button
                className={`${styles.navBtn} ${active === "Practice Tests" ? styles.navBtnOn : ""}`}
                onClick={() => selectView("Practice Tests")}
                type="button"
                title="AMC Practice Tests"
              >
                <span className={styles.step}>4</span>
                <span className={styles.navLabel}>Practice Tests</span>
              </button>
            </li>
            <li>
              <button
                className={`${styles.navBtn} ${active === "Resources" ? styles.navBtnOn : ""}`}
                onClick={() => selectView("Resources")}
                type="button"
                title="AMC Resources"
              >
                <span className={styles.step}>5</span>
                <span className={styles.navLabel}>Resources</span>
              </button>
            </li>
          </ul>

          <div className={styles.card} style={{ margin: "16px 18px 0" }}>
            <div className={styles.muted}>
              Support: <b>outreach@thrivingscholars.com</b>
              <br />
              WhatsApp: <b>+44 7459 070019</b>
            </div>
          </div>

          {hasTmua ? (
            <div className={styles.card} style={{ margin: "12px 18px 0" }}>
              <div className={styles.cardTitle}>TMUA access</div>
              <div className={styles.muted} style={{ marginBottom: 10 }}>
                Your account also has TMUA access.
              </div>
              <button
                className={styles.btn}
                type="button"
                onClick={() => (window.location.href = "/dashboard?view=tmua")}
              >
                Open TMUA Portal
              </button>
            </div>
          ) : null}
        </aside>

        <main className={styles.main}>
          <nav className={styles.mobileNav} aria-label="AMC workspace sections">
            {PAPERS.map((paper) => (
              <button
                className={`${styles.mobileNavBtn} ${active === paper.paper ? styles.mobileNavBtnOn : ""}`}
                key={paper.paper}
                onClick={() => selectView(paper.paper)}
                type="button"
              >
                {paper.paper}
              </button>
            ))}
            <button
              className={`${styles.mobileNavBtn} ${active === "Practice Tests" ? styles.mobileNavBtnOn : ""}`}
              onClick={() => selectView("Practice Tests")}
              type="button"
            >
              Practice Tests
            </button>
            <button
              className={`${styles.mobileNavBtn} ${active === "Resources" ? styles.mobileNavBtnOn : ""}`}
              onClick={() => selectView("Resources")}
              type="button"
            >
              Resources
            </button>
          </nav>

          {active === "Practice Tests" ? (
            <>
              <div className={styles.h1}>AMC Practice Tests</div>

              <div className={styles.metaRow}>
                <div className={styles.meta}>
                  <span className={styles.dot} /> AMC 8 + AMC 10
                </div>
                <div className={styles.meta}>Timed practice</div>
                <div className={styles.meta}>Score · Analyse · Review</div>
              </div>

              <div className={styles.card}>
                <div className={styles.cardTitle}>Thriving Scholars practice tests</div>
                <div className={styles.muted}>
                  All eight topical tests, both AMC 8 full mocks and two additional digital
                  diagnostics are now together in one distraction-free exam library. Your score
                  and the worked solution booklet appear when you submit.
                </div>
              </div>

              <div className={styles.testLibrary}>
                {PRACTICE_TEST_SECTIONS.map((section) => (
                  <section className={styles.testSection} key={section.heading}>
                    <div className={styles.sectionIntro}>
                      <h2 className={styles.sectionTitle}>{section.heading}</h2>
                      <p className={styles.sectionDescription}>{section.description}</p>
                    </div>

                    {section.groups.map((group) => (
                      <div className={styles.topicGroup} key={group.heading}>
                        <div className={styles.topicHeading}>
                          <h3>{group.heading}</h3>
                          <span aria-hidden="true" />
                        </div>

                        <div className={styles.testGrid}>
                          {group.tests.map((test) => (
                            <article className={styles.test} key={test.href}>
                              <div className={styles.testMeta}>{test.level}</div>
                              <div className={styles.testTitle}>{test.title}</div>
                              <div className={styles.muted}>{test.detail}</div>
                              <div className={styles.tags}>
                                {test.tags.map((tag) => (
                                  <span className={styles.tag} key={tag}>
                                    {tag}
                                  </span>
                                ))}
                              </div>
                              <a className={styles.go} href={test.href}>
                                Start test <span aria-hidden="true">→</span>
                              </a>
                            </article>
                          ))}
                        </div>
                      </div>
                    ))}
                  </section>
                ))}
              </div>
            </>
          ) : active === "Resources" ? (
            <>
              <div className={styles.h1}>AMC Resources</div>

              <div className={styles.metaRow}>
                <div className={styles.meta}>
                  <span className={styles.dot} /> Downloadable AMC PDFs
                </div>
                <div className={styles.meta}>AMC 8 · AMC 10 · AMC 12</div>
                <div className={styles.meta}>Cheat sheets · Compendia</div>
              </div>

              <div className={styles.card}>
                <div className={styles.cardTitle}>Build your revision library</div>
                <div className={styles.muted}>
                  Use the concise cheat sheets for fast recall, then move to the compendia for
                  deeper problem practice. Every resource opens as a downloadable PDF.
                </div>
              </div>

              <div className={styles.resourceLibrary}>
                {AMC_RESOURCE_SECTIONS.map((section) => (
                  <section className={styles.testSection} key={section.heading}>
                    <div className={styles.sectionIntro}>
                      <h2 className={styles.sectionTitle}>{section.heading} Resources</h2>
                      <p className={styles.sectionDescription}>{section.description}</p>
                    </div>

                    <div className={styles.resourceGrid}>
                      {section.resources.map((resource) => (
                        <a
                          className={styles.resourceCard}
                          href={resource.href}
                          key={resource.href}
                          target="_blank"
                          rel="noreferrer"
                          download
                        >
                          <span className={styles.resourceIcon} aria-hidden="true">
                            PDF
                          </span>
                          <div className={styles.resourceType}>
                            {resource.kind} · {resource.pages} pages
                          </div>
                          <div className={styles.resourceTitle}>{resource.title}</div>
                          <p className={styles.resourceDescription}>{resource.description}</p>
                          <div className={styles.resourceFooter}>
                            <span className={styles.resourceLevel}>{section.heading}</span>
                            <span className={styles.resourceAction}>Download PDF →</span>
                          </div>
                        </a>
                      ))}
                    </div>
                  </section>
                ))}
              </div>
            </>
          ) : (
            <>
              <div className={styles.h1}>{activePaper?.label}</div>

              <div className={styles.metaRow}>
                <div className={styles.meta}>
                  <span className={styles.dot} /> {activePaper?.paper}
                </div>
                <div className={styles.meta}>Question Bank</div>
                <div className={styles.meta}>Practice · Track · Review</div>
              </div>

              <div className={styles.card}>
                <div className={styles.cardTitle}>Open {activePaper?.label}</div>
                <div className={styles.muted}>{activePaper?.description}</div>

                <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 14 }}>
                  <button
                    className={`${styles.btn} ${styles.btnPrimary}`}
                    type="button"
                    onClick={() =>
                      activePaper && (window.location.href = bankUrl(activePaper.paper))
                    }
                  >
                    Open {activePaper?.paper} Question Bank
                  </button>
                </div>
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
