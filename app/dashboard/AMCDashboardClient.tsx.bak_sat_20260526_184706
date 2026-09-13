"use client";

import { useState } from "react";
import styles from "./dashboard.module.css";

type Props = {
  email?: string | null;
  hasTmua?: boolean;
};

type AMCPaper = "AMC 8" | "AMC 10" | "AMC 12";

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

function bankUrl(paper: AMCPaper) {
  return `/amc-question-bank?paper=${encodeURIComponent(paper)}`;
}

export default function AMCDashboardClient({ email, hasTmua }: Props) {
  const [active, setActive] = useState<AMCPaper>("AMC 8");

  const activePaper = PAPERS.find((p) => p.paper === active) || PAPERS[0];

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
            AMC 8 + AMC 10 + AMC 12 question banks. Clean, focused, tracked.
          </div>

          <ul className={styles.nav}>
            {PAPERS.map((p) => (
              <li key={p.paper}>
                <button
                  className={`${styles.navBtn} ${active === p.paper ? styles.navBtnOn : ""}`}
                  onClick={() => setActive(p.paper)}
                  type="button"
                  title={p.label}
                >
                  <span className={styles.step}>{p.step}</span>
                  <span className={styles.navLabel}>{p.label}</span>
                </button>
              </li>
            ))}
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
          <div className={styles.h1}>{activePaper.label}</div>

          <div className={styles.metaRow}>
            <div className={styles.meta}>
              <span className={styles.dot} /> {activePaper.paper}
            </div>
            <div className={styles.meta}>Question Bank</div>
            <div className={styles.meta}>Practice · Track · Review</div>
          </div>

          <div className={styles.card}>
            <div className={styles.cardTitle}>Open {activePaper.label}</div>
            <div className={styles.muted}>{activePaper.description}</div>

            <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 14 }}>
              <button
                className={`${styles.btn} ${styles.btnPrimary}`}
                type="button"
                onClick={() => (window.location.href = bankUrl(activePaper.paper))}
              >
                Open {activePaper.paper} Question Bank
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
