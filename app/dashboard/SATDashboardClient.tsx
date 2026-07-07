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

const TESTS = [
  {
    title: "SAT Full-Length Test 1",
    badge: "Full-Length",
    href: "/sat-practice-tests/tests/sat-full-length-1/index.html",
    meta: "Reading & Writing + Math",
  },
  {
    title: "SAT Full-Length Test 2",
    badge: "Full-Length",
    href: "/sat-practice-tests/tests/sat-full-length-2/index.html",
    meta: "Reading & Writing + Math",
  },
  {
    title: "SAT Math Test 1",
    badge: "Math",
    href: "/sat-practice-tests/tests/sat-math-1/index.html",
    meta: "Calculator-style SAT Math practice",
  },
  {
    title: "SAT Math Test 2",
    badge: "Math",
    href: "/sat-practice-tests/tests/sat-math-2/index.html",
    meta: "Advanced SAT Math practice",
  },
  {
    title: "SAT Reading Test 1",
    badge: "Reading",
    href: "/sat-practice-tests/tests/sat-reading-1/index.html",
    meta: "Reading and Writing practice",
  },
  {
    title: "SAT Reading Test 2",
    badge: "Reading",
    href: "/sat-practice-tests/tests/sat-reading-2/index.html",
    meta: "Reading and Writing practice",
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
            SAT question bank + 6 practice tests. Clean, focused, tracked.
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
                  <span className={styles.dot} /> 6 Tests
                </div>
                <div className={styles.meta}>2 Full-Length</div>
                <div className={styles.meta}>2 Math · 2 Reading</div>
              </div>

              <div className={styles.card}>
                <div className={styles.cardTitle}>Practice test set</div>
                <div className={styles.muted}>
                  Includes 2 full-length SAT tests, 2 SAT Math tests and 2 SAT Reading and Writing tests.
                </div>

                <div className={styles.grid}>
                  {TESTS.map((t) => (
                    <div key={t.href} className={styles.test}>
                      <div className={styles.testTitle}>{t.title}</div>
                      <div className={styles.testMeta}>
                        <span>{t.badge}</span>
                        <span> · </span>
                        <span>{t.meta}</span>
                      </div>

                      <div style={{ marginTop: 10 }}>
                        <button className={styles.go} type="button" onClick={() => (window.location.href = t.href)}>
                          Start →
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
