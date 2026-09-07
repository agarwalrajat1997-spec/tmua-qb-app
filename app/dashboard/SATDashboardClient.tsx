"use client";

import { useEffect, useState, type CSSProperties } from "react";
import styles from "./dashboard.module.css";

type Props = {
  email?: string | null;
  hasSatBank?: boolean;
  hasSatTests?: boolean;
  hasAmc?: boolean;
  hasTmua?: boolean;
};

type SATTab = "bank" | "tests" | "resources";

type SATResource = {
  title: string;
  description: string;
  kind: string;
  pages: number;
  level: string;
  href: string;
};

const TEST_GROUPS = [
  {
    id: "quick-diagnostic",
    title: "Quick diagnostic",
    description: "Start here for a shorter baseline across Reading and Writing and Math.",
    tests: [
      {
        title: "Mini Digital SAT Diagnostic",
        badge: "Introductory",
        href: "/sat-mini-diagnostic",
        meta: "60 questions · Reading and Writing + Math",
      },
    ],
  },
  {
    id: "math-diagnostics",
    title: "Math diagnostics",
    description:
      "Four complete Math diagnostics, arranged from an initial skills check to the most demanding paper.",
    tests: [
      {
        title: "SAT Math Diagnostic Test 1",
        badge: "Foundation → Standard",
        href: "/sat-test-1",
        meta: "44 questions · 70 minutes · Predicted score /800",
      },
      {
        title: "SAT Math Diagnostic Test 2",
        badge: "Standard",
        href: "/sat-test-2",
        meta: "44 questions · 70 minutes · Predicted score /800",
      },
      {
        title: "SAT Math Diagnostic Test 3",
        badge: "Standard → Challenging",
        href: "/sat-test-3",
        meta: "44 questions · 70 minutes · Predicted score /800",
      },
      {
        title: "SAT Math Diagnostic Test 4",
        badge: "Hard → Very hard",
        href: "/sat-test-4",
        meta: "44 questions · 70 minutes · Predicted score /800",
      },
    ],
  },
  {
    id: "full-length",
    title: "Full-length diagnostics",
    description: "Choose a standard exam-level paper or a more demanding advanced paper.",
    tests: [
      {
        title: "SAT Diagnostic Test 6",
        badge: "Standard",
        href: "/sat-test-6",
        meta: "98 questions · 134 minutes · Predicted score /1600",
      },
      {
        title: "SAT Diagnostic Test 5 — Advanced",
        badge: "Hard",
        href: "/sat-test-5",
        meta: "98 questions · 134 minutes · Predicted score /1600",
      },
    ],
  },
] as const;

const SAT_RESOURCE_SECTIONS: Array<{
  heading: string;
  description: string;
  resources: SATResource[];
}> = [
  {
    heading: "Digital SAT Reference Guides",
    description:
      "Concise Thriving Scholars revision guides for the Reading and Writing and Math sections.",
    resources: [
      {
        title: "Digital SAT Reading & Writing",
        description:
          "A 6-page guide covering sentence boundaries, punctuation, grammar, claims and evidence, words in context, transitions and rhetorical synthesis.",
        kind: "Revision guide",
        pages: 6,
        level: "Reading & Writing",
        href: "/sat-resources/digital-sat-reading-writing-thriving-scholars.pdf",
      },
      {
        title: "Digital SAT Math Reference",
        description:
          "A 12-page reference covering linear equations, quadratics, functions, ratios, data, geometry, trigonometry and practical Desmos workflows.",
        kind: "Quick reference",
        pages: 12,
        level: "Math",
        href: "/sat-resources/digital-sat-math-reference-thriving-scholars.pdf",
      },
    ],
  },
];

export default function SATDashboardClient({
  email,
  hasSatBank = false,
  hasSatTests = false,
  hasAmc = false,
  hasTmua = false,
}: Props) {
  const [active, setActive] = useState<SATTab>(hasSatBank ? "bank" : "tests");

  useEffect(() => {
    const requestedSection = new URLSearchParams(window.location.search).get("section");

    if (requestedSection === "resources") {
      setActive("resources");
      return;
    }

    if (requestedSection === "tests" && hasSatTests) {
      setActive("tests");
      return;
    }

    if (requestedSection === "bank" && hasSatBank) {
      setActive("bank");
    }
  }, [hasSatBank, hasSatTests]);

  useEffect(() => {
    if (active === "bank" && !hasSatBank && hasSatTests) setActive("tests");
    if (active === "tests" && !hasSatTests && hasSatBank) setActive("bank");
  }, [active, hasSatBank, hasSatTests]);

  const lockStyle: CSSProperties = { opacity: 0.45, cursor: "not-allowed" };

  function selectTab(tab: SATTab) {
    if (tab === "bank" && !hasSatBank) return;
    if (tab === "tests" && !hasSatTests) return;

    setActive(tab);

    const url = new URL(window.location.href);
    if (tab === "resources") url.searchParams.set("section", "resources");
    else if (tab === "tests") url.searchParams.set("section", "tests");
    else url.searchParams.delete("section");

    window.history.replaceState({}, "", url);
  }

  function logout() {
    window.location.href = "/api/logout";
  }

  return (
    <div className={styles.page} data-ui="TS_SAT_DASH_PORTAL_V2">
      <div className={styles.topbar}>
        <div className={styles.brand}>
          <div className={styles.brandName}>Thriving Scholars</div>
          <div className={styles.brandTag}>SAT Student Portal</div>
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
            Your SAT
            <br />
            Workspace
          </div>

          <div className={styles.sideSub}>
            SAT question bank, verified diagnostic tests and concise revision resources in one
            focused workspace.
          </div>

          <ul className={styles.nav}>
            <li>
              <button
                className={`${styles.navBtn} ${active === "bank" ? styles.navBtnOn : ""}`}
                onClick={() => selectTab("bank")}
                type="button"
                disabled={!hasSatBank}
                aria-disabled={!hasSatBank}
                style={!hasSatBank ? lockStyle : undefined}
                title={!hasSatBank ? "Locked: sat-question-bank not enabled" : "SAT Question Bank"}
              >
                <span className={styles.step}>1</span>
                <span className={styles.navLabel}>SAT Question Bank</span>
              </button>
            </li>

            <li>
              <button
                className={`${styles.navBtn} ${active === "tests" ? styles.navBtnOn : ""}`}
                onClick={() => selectTab("tests")}
                type="button"
                disabled={!hasSatTests}
                aria-disabled={!hasSatTests}
                style={!hasSatTests ? lockStyle : undefined}
                title={!hasSatTests ? "Locked: sat-practice-tests not enabled" : "SAT Practice Tests"}
              >
                <span className={styles.step}>2</span>
                <span className={styles.navLabel}>SAT Practice Tests</span>
              </button>
            </li>

            <li>
              <button
                className={`${styles.navBtn} ${active === "resources" ? styles.navBtnOn : ""}`}
                onClick={() => selectTab("resources")}
                type="button"
                title="SAT Resources"
              >
                <span className={styles.step}>3</span>
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

          {(hasAmc || hasTmua) && (
            <div className={styles.card} style={{ margin: "12px 18px 0" }}>
              <div className={styles.cardTitle}>Other access</div>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 10 }}>
                {hasAmc && (
                  <button
                    className={styles.btn}
                    type="button"
                    onClick={() => (window.location.href = "/dashboard?view=amc")}
                  >
                    Open AMC
                  </button>
                )}
                {hasTmua && (
                  <button
                    className={styles.btn}
                    type="button"
                    onClick={() => (window.location.href = "/dashboard?view=tmua")}
                  >
                    Open TMUA
                  </button>
                )}
              </div>
            </div>
          )}
        </aside>

        <main className={styles.main}>
          <nav className={styles.mobileNav} aria-label="SAT workspace sections">
            <button
              className={`${styles.mobileNavBtn} ${
                active === "bank" ? styles.mobileNavBtnOn : ""
              }`}
              onClick={() => selectTab("bank")}
              type="button"
              disabled={!hasSatBank}
              aria-disabled={!hasSatBank}
              style={!hasSatBank ? lockStyle : undefined}
            >
              Question Bank
            </button>
            <button
              className={`${styles.mobileNavBtn} ${
                active === "tests" ? styles.mobileNavBtnOn : ""
              }`}
              onClick={() => selectTab("tests")}
              type="button"
              disabled={!hasSatTests}
              aria-disabled={!hasSatTests}
              style={!hasSatTests ? lockStyle : undefined}
            >
              Practice Tests
            </button>
            <button
              className={`${styles.mobileNavBtn} ${
                active === "resources" ? styles.mobileNavBtnOn : ""
              }`}
              onClick={() => selectTab("resources")}
              type="button"
            >
              Resources
            </button>
          </nav>

          {active === "bank" ? (
            <>
              <div className={styles.h1}>SAT Question Bank</div>

              <div className={styles.metaRow}>
                <div className={styles.meta}>
                  <span className={styles.dot} /> SAT
                </div>
                <div className={styles.meta}>Question Bank</div>
                <div className={styles.meta}>Practice · Track · Review</div>
              </div>

              <div className={styles.card}>
                <div className={styles.cardTitle}>Open SAT Question Bank</div>
                <div className={styles.muted}>
                  Your SAT question bank access is enabled. Open the bank to practise by section,
                  topic and difficulty.
                </div>

                <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 14 }}>
                  <button
                    className={`${styles.btn} ${styles.btnPrimary}`}
                    type="button"
                    onClick={() => (window.location.href = "/sat-question-bank")}
                  >
                    Open SAT Question Bank
                  </button>
                </div>
              </div>
            </>
          ) : active === "tests" ? (
            <>
              <div className={styles.h1}>SAT Practice Tests</div>

              <div className={styles.metaRow}>
                <div className={styles.meta}>
                  <span className={styles.dot} /> 7 Verified Tests
                </div>
                <div className={styles.meta}>1 Mini · 4 Math</div>
                <div className={styles.meta}>2 Full-Length</div>
              </div>

              <div className={styles.testLibrary}>
                {TEST_GROUPS.map((group) => (
                  <section id={group.id} key={group.id} className={styles.testSection}>
                    <div className={styles.sectionIntro}>
                      <h2 className={styles.sectionTitle}>{group.title}</h2>
                      <p className={styles.sectionDescription}>{group.description}</p>
                    </div>

                    <div className={styles.testGrid}>
                      {group.tests.map((test) => (
                        <article key={test.href} className={styles.test}>
                          <div className={styles.testTitle}>{test.title}</div>
                          <div className={styles.tags}>
                            <span className={styles.tag}>{test.badge}</span>
                          </div>
                          <div className={styles.testMeta}>{test.meta}</div>
                          <a className={styles.go} href={test.href}>
                            Start test →
                          </a>
                        </article>
                      ))}
                    </div>
                  </section>
                ))}
              </div>
            </>
          ) : (
            <>
              <div className={styles.h1}>SAT Resources</div>

              <div className={styles.metaRow}>
                <div className={styles.meta}>
                  <span className={styles.dot} /> Downloadable SAT PDFs
                </div>
                <div className={styles.meta}>Reading & Writing · Math</div>
                <div className={styles.meta}>Quick reference guides</div>
              </div>

              <div className={styles.card}>
                <div className={styles.cardTitle}>Build your SAT revision library</div>
                <div className={styles.muted}>
                  Use the Reading & Writing guide for grammar, evidence and rhetorical questions,
                  and the Math reference for formulas, data, geometry and Desmos. These resources
                  are for personal study use.
                </div>
              </div>

              <div className={styles.resourceLibrary}>
                {SAT_RESOURCE_SECTIONS.map((section) => (
                  <section className={styles.testSection} key={section.heading}>
                    <div className={styles.sectionIntro}>
                      <h2 className={styles.sectionTitle}>{section.heading}</h2>
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
                            <span className={styles.resourceLevel}>{resource.level}</span>
                            <span className={styles.resourceAction}>Download PDF →</span>
                          </div>
                        </a>
                      ))}
                    </div>
                  </section>
                ))}
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
