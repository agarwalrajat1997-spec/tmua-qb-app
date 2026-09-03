"use client";

import { useEffect, useState } from "react";
import styles from "./dashboard.module.css";

type Props = {
  email?: string | null;
  hasSatBank?: boolean;
  hasSatTests?: boolean;
  hasAmc?: boolean;
  hasTmua?: boolean;
};

type SATTab = "bank" | "tests";

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
    description: "Four complete Math diagnostics, arranged from an initial skills check to the most demanding paper.",
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
    title: "Full-length diagnostic",
    description: "A four-module Digital SAT paper for students ready for an advanced timed test.",
    tests: [
      {
        title: "SAT Diagnostic Test 6",
        badge: "Hard → Harder",
        href: "/sat-test-6",
        meta: "98 questions · 134 minutes · Predicted score /1600",
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
    if (active === "bank" && !hasSatBank && hasSatTests) setActive("tests");
    if (active === "tests" && !hasSatTests && hasSatBank) setActive("bank");
  }, [active, hasSatBank, hasSatTests]);

  const lockStyle: React.CSSProperties = { opacity: 0.45, cursor: "not-allowed" };

  function logout() {
    window.location.href = "/api/logout";
  }

  return (
    <div className={styles.page} data-ui="TS_SAT_DASH_PORTAL_V1">
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
            SAT question bank + verified diagnostic tests. Clean, focused, tracked.
          </div>

          <ul className={styles.nav}>
            <li>
              <button
                className={`${styles.navBtn} ${active === "bank" ? styles.navBtnOn : ""}`}
                onClick={() => hasSatBank && setActive("bank")}
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
                onClick={() => hasSatTests && setActive("tests")}
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
                  <button className={styles.btn} type="button" onClick={() => (window.location.href = "/dashboard?view=amc")}>
                    Open AMC
                  </button>
                )}
                {hasTmua && (
                  <button className={styles.btn} type="button" onClick={() => (window.location.href = "/dashboard?view=tmua")}>
                    Open TMUA
                  </button>
                )}
              </div>
            </div>
          )}
        </aside>

        <main className={styles.main}>
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
                  Your SAT question bank access is enabled. Open the bank to practise by section, topic and difficulty.
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
          ) : (
            <>
              <div className={styles.h1}>SAT Practice Tests</div>

              <div className={styles.metaRow}>
                <div className={styles.meta}>
                  <span className={styles.dot} /> 6 Verified Tests
                </div>
                <div className={styles.meta}>1 Mini · 4 Math</div>
                <div className={styles.meta}>1 Full-Length</div>
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
          )}
        </main>
      </div>
    </div>
  );
}
