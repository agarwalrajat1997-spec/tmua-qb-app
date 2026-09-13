"use client";

import React, { useEffect, useMemo, useState } from "react";
import { supabaseBrowser } from "@/utils/supabase/browser";
import styles from "../dashboard/dashboard.module.css";

type EsatProduct = "esat-practice-tests" | "esat-question-bank" | "esat-classes";
type Section = "practice" | "bank" | "classes" | "resources";
type ResourcePdf = {
  title: string;
  description: string;
  href: string;
};

const ESAT_RESOURCE_PDFS: ResourcePdf[] = [
  {
    title: "ESAT Mathematics 1 Formula Sheet",
    description: "Compact formula and revision reference for ESAT Mathematics 1.",
    href: "/esat-resources/esat-mathematics-1-formula-sheet.pdf",
  },
  {
    title: "ESAT Mathematics 2 Formula Sheet",
    description: "Compact formula and revision reference for ESAT Mathematics 2.",
    href: "/esat-resources/esat-mathematics-2-formula-sheet.pdf",
  },
  {
    title: "ESAT Physics Formula Sheet",
    description: "Key Physics formulas and things to remember for ESAT.",
    href: "/esat-resources/esat-physics-formula-sheet.pdf",
  },
  {
    title: "ESAT Chemistry Formula Sheet",
    description: "Key Chemistry formulas and things to remember for ESAT.",
    href: "/esat-resources/esat-chemistry-formula-sheet.pdf",
  },
  {
    title: "ESAT Biology Formula Sheet",
    description: "Key Biology facts and things to remember for ESAT.",
    href: "/esat-resources/esat-biology-formula-sheet.pdf",
  },
  {
    title: "ESAT Content Specification",
    description: "Official ESAT specification and subject coverage reference.",
    href: "/esat-resources/esat-content-specification.pdf",
  },
];
type TrackKey = "engineering" | "physical" | "life";

type MockTile = {
  test_id: string;
  title: string;
  badge: string;
  duration_minutes: number;
  subjects: string;
  href: string;
  solutionUrl?: string | null;
};

type Track = {
  key: TrackKey;
  label: string;
  subjects: string;
  mocks: MockTile[];
};

type AttemptSummary = {
  id: string;
  test_id: string;
  test_title?: string | null;
  total_questions?: number | null;
  score?: number | null;
  submitted_at?: string | null;
};

const TRACKS: Track[] = [
  {
    key: "engineering",
    label: "Engineering",
    subjects: "Math 1 + Physics + Math 2",
    mocks: [
      { test_id: "esat-mock-01", title: "ESAT Mock Test 1", badge: "ENGINEERING", duration_minutes: 120, subjects: "Math 1 + Physics + Math 2", href: "/esat-practice-tests/tests/esat-mock-01/index.html" },
      { test_id: "esat-mock-02", title: "ESAT Mock Test 2", badge: "ENGINEERING", duration_minutes: 120, subjects: "Math 1 + Physics + Math 2", href: "/esat-practice-tests/tests/esat-mock-02/index.html" },
      { test_id: "esat-mock-03", title: "ESAT Mock Test 3", badge: "ENGINEERING", duration_minutes: 120, subjects: "Math 1 + Physics + Math 2", href: "/esat-practice-tests/tests/esat-mock-03/index.html" },
      { test_id: "esat-mock-04", title: "ESAT Mock Test 4", badge: "ENGINEERING", duration_minutes: 120, subjects: "Math 1 + Physics + Math 2", href: "/esat-practice-tests/tests/esat-mock-04/index.html" },
    ],
  },
  {
    key: "physical",
    label: "Physical Sciences",
    subjects: "Math 1 + Physics + Chemistry",
    mocks: [
      { test_id: "esat-mock-05", title: "ESAT Mock Test 5", badge: "PHYSICAL SCIENCES", duration_minutes: 120, subjects: "Math 1 + Physics + Chemistry", href: "/esat-practice-tests/tests/esat-mock-05/index.html" },
      { test_id: "esat-mock-06", title: "ESAT Mock Test 6", badge: "PHYSICAL SCIENCES", duration_minutes: 120, subjects: "Math 1 + Physics + Chemistry", href: "/esat-practice-tests/tests/esat-mock-06/index.html" },
      { test_id: "esat-mock-07", title: "ESAT Mock Test 7", badge: "PHYSICAL SCIENCES", duration_minutes: 120, subjects: "Math 1 + Physics + Chemistry", href: "/esat-practice-tests/tests/esat-mock-07/index.html" },
      { test_id: "esat-mock-08", title: "ESAT Mock Test 8", badge: "PHYSICAL SCIENCES", duration_minutes: 120, subjects: "Math 1 + Physics + Chemistry", href: "/esat-practice-tests/tests/esat-mock-08/index.html" },
    ],
  },
  {
    key: "life",
    label: "Life Sciences",
    subjects: "Math 1 + Chemistry + Biology",
    mocks: [
      { test_id: "esat-mock-09", title: "ESAT Mock Test 9", badge: "LIFE SCIENCES", duration_minutes: 120, subjects: "Math 1 + Chemistry + Biology", href: "/esat-practice-tests/tests/esat-mock-09/index.html" },
      { test_id: "esat-mock-10", title: "ESAT Mock Test 10", badge: "LIFE SCIENCES", duration_minutes: 120, subjects: "Math 1 + Chemistry + Biology", href: "/esat-practice-tests/tests/esat-mock-10/index.html" },
      { test_id: "esat-mock-11", title: "ESAT Mock Test 11", badge: "LIFE SCIENCES", duration_minutes: 120, subjects: "Math 1 + Chemistry + Biology", href: "/esat-practice-tests/tests/esat-mock-11/index.html" },
      { test_id: "esat-mock-12", title: "ESAT Mock Test 12", badge: "LIFE SCIENCES", duration_minutes: 120, subjects: "Math 1 + Chemistry + Biology", href: "/esat-practice-tests/tests/esat-mock-12/index.html" },
    ],
  },
];

function fmtDate(value?: string | null) {
  if (!value) return "";
  try {
    return new Intl.DateTimeFormat("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    }).format(new Date(value));
  } catch {
    return "";
  }
}

export default function ESATDashboardClient({ uiMark }: { uiMark: string }) {
  const supabase = useMemo(() => supabaseBrowser(), []);

  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(true);
  const [active, setActive] = useState<Section>("practice");
  const [activeTrack, setActiveTrack] = useState<TrackKey>("engineering");
  const [products, setProducts] = useState<EsatProduct[]>([]);
  const [err, setErr] = useState<string | null>(null);

  const [latestByTestId, setLatestByTestId] = useState<Record<string, AttemptSummary>>({});
  const [attemptsLoading, setAttemptsLoading] = useState(false);
  const [attemptsErr, setAttemptsErr] = useState<string | null>(null);

  const [modalOpen, setModalOpen] = useState(false);
  const [modalTitle, setModalTitle] = useState("");
  const [modalAttempts, setModalAttempts] = useState<AttemptSummary[]>([]);
  const [modalLoading, setModalLoading] = useState(false);
  const [modalErr, setModalErr] = useState<string | null>(null);

  const [solOpen, setSolOpen] = useState(false);
  const [solTitle, setSolTitle] = useState("");
  const [solUrl, setSolUrl] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function run() {
      try {
        const {
          data: { user },
          error: userErr,
        } = await supabase.auth.getUser();

        if (userErr || !user?.email) {
          window.location.href = "/login?next=/esat";
          return;
        }

        setEmail(user.email);

        const { data, error } = await supabase
          .from("student_access")
          .select("product, approved, expires_at")
          .ilike("email", user.email)
          .eq("approved", true);

        if (cancelled) return;

        if (error) {
          setErr(error.message || "Could not load ESAT access.");
          setProducts([]);
          setLoading(false);
          return;
        }

        const now = Date.now();

        const ps = (data || [])
          .filter((r: any) => {
            if (!r?.approved) return false;
            if (!r?.expires_at) return true;
            return new Date(r.expires_at).getTime() > now;
          })
          .map((r: any) => String(r.product || ""))
          .filter(
            (p): p is EsatProduct =>
              p === "esat-practice-tests" ||
              p === "esat-question-bank" ||
              p === "esat-classes"
          );

        const unique = Array.from(new Set(ps));
        setProducts(unique);

        if (unique.includes("esat-practice-tests")) setActive("practice");
        else if (unique.includes("esat-question-bank")) setActive("bank");
        else if (unique.includes("esat-classes")) setActive("classes");
        else setActive("practice");

        setLoading(false);
      } catch (e: any) {
        setErr(String(e?.message || e));
        setLoading(false);
      }
    }

    run();

    return () => {
      cancelled = true;
    };
  }, [supabase]);

  const hasPractice = products.includes("esat-practice-tests");
  const hasBank = products.includes("esat-question-bank");
  const hasClasses = products.includes("esat-classes");

  useEffect(() => {
    if (loading) return;
    if (!hasPractice) return;

    let cancelled = false;

    async function loadAttempts() {
      setAttemptsLoading(true);
      setAttemptsErr(null);

      try {
        const res = await fetch("/api/practice-tests/attempts", {
          method: "GET",
          credentials: "include",
        });

        const json = await res.json();

        if (!res.ok) throw new Error(json?.error || "Failed to load attempts.");

        const map: Record<string, AttemptSummary> = {};

        for (const row of json?.latest || []) {
          if (row?.test_id) map[row.test_id] = row;
        }

        if (!cancelled) setLatestByTestId(map);
      } catch (e: any) {
        if (!cancelled) {
          setLatestByTestId({});
          setAttemptsErr(e?.message || "Failed to load attempts.");
        }
      } finally {
        if (!cancelled) setAttemptsLoading(false);
      }
    }

    loadAttempts();

    return () => {
      cancelled = true;
    };
  }, [loading, hasPractice]);

  const showNoAccess = !loading && !hasPractice && !hasBank && !hasClasses;
  const lockStyle: React.CSSProperties = { opacity: 0.45, cursor: "not-allowed" };
  const currentTrack = TRACKS.find((t) => t.key === activeTrack) || TRACKS[0];

  function openTest(t: MockTile) {
    window.location.href = t.href;
  }

  async function openAttempts(t: MockTile) {
    setModalOpen(true);
    setModalTitle(`${t.title} Attempts`);
    setModalAttempts([]);
    setModalLoading(true);
    setModalErr(null);

    try {
      const res = await fetch(`/api/practice-tests/attempts?test_id=${encodeURIComponent(t.test_id)}`, {
        credentials: "include",
      });

      const json = await res.json();

      if (!res.ok) throw new Error(json?.error || "Failed to load attempts.");

      setModalAttempts((json?.attempts || []) as AttemptSummary[]);
    } catch (e: any) {
      setModalErr(e?.message || "Failed to load attempts.");
      setModalAttempts([]);
    } finally {
      setModalLoading(false);
    }
  }

  function openSolutions(t: MockTile) {
    setSolTitle(`${t.title} Solutions`);
    setSolUrl(t.solutionUrl || null);
    setSolOpen(true);
  }

  if (loading) {
    return (
      <div className={styles.page} data-ui={uiMark}>
        <div className={styles.topbar}>
          <div className={styles.brand}>
            <div className={styles.brandName}>Thriving Scholars</div>
            <div className={styles.brandTag}>ESAT Student Portal</div>
          </div>
          <div className={styles.right}>
            <div className={styles.pill}>Loading...</div>
          </div>
        </div>

        <div className={styles.main}>
          <div className={styles.card}>
            <div className={styles.cardTitle}>Loading your ESAT portal...</div>
            <div className={styles.muted}>Checking your ESAT product access.</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page} data-ui={uiMark}>
      <div className={styles.topbar}>
        <div className={styles.brand}>
          <div className={styles.brandName}>Thriving Scholars</div>
          <div className={styles.brandTag}>ESAT Student Portal</div>
        </div>

        <div className={styles.right}>
          <div className={styles.pill}>Signed in as {email || "student"}</div>
          <a className={styles.btn} href="/api/logout">
            Logout
          </a>
        </div>
      </div>

      <div className={styles.shell}>
        <aside className={styles.sidebar}>
          <div className={styles.sideTitle}>
            Your ESAT
            <br />
            Workspace
          </div>

          <div className={styles.sideSub}>
            Practice tests + question bank + live classes.
          </div>

          <ul className={styles.nav}>
            <li>
              <button
                className={`${styles.navBtn} ${active === "practice" ? styles.navBtnOn : ""}`}
                onClick={() => hasPractice && setActive("practice")}
                type="button"
                aria-disabled={!hasPractice}
                disabled={!hasPractice}
                style={!hasPractice ? lockStyle : undefined}
                title={!hasPractice ? "Locked: esat-practice-tests not enabled" : "Practice Tests"}
              >
                <span className={styles.step}>1</span>
                <span className={styles.navLabel}>Practice Tests</span>
              </button>
            </li>

            <li>
              <button
                className={`${styles.navBtn} ${active === "bank" ? styles.navBtnOn : ""}`}
                onClick={() => hasBank && setActive("bank")}
                type="button"
                aria-disabled={!hasBank}
                disabled={!hasBank}
                style={!hasBank ? lockStyle : undefined}
                title={!hasBank ? "Locked: esat-question-bank not enabled" : "Question Bank"}
              >
                <span className={styles.step}>2</span>
                <span className={styles.navLabel}>Question Bank</span>
              </button>
            </li>

            <li>
              <button
                className={`${styles.navBtn} ${active === "classes" ? styles.navBtnOn : ""}`}
                onClick={() => hasClasses && setActive("classes")}
                type="button"
                aria-disabled={!hasClasses}
                disabled={!hasClasses}
                style={!hasClasses ? lockStyle : undefined}
                title={!hasClasses ? "Locked: esat-classes not enabled" : "Classes"}
              >
                <span className={styles.step}>3</span>
                <span className={styles.navLabel}>Classes</span>
              </button>
            </li>
            <li
              style={{
                marginTop: 22,
                paddingTop: 18,
                borderTop: "1px solid #E5E7EB",
              }}
            >
              <button
                onClick={() => setActive("resources")}
                type="button"
                title="ESAT Resources"
                style={{
                  width: "100%",
                  border: active === "resources" ? "1px solid #D0D5DD" : "1px solid #E5E7EB",
                  borderLeft: active === "resources" ? "5px solid #98A2B3" : "1px solid #E5E7EB",
                  background: active === "resources" ? "#F2F4F7" : "#FFFFFF",
                  color: "#344054",
                  borderRadius: 18,
                  padding: "14px 16px",
                  display: "flex",
                  alignItems: "center",
                  gap: 14,
                  cursor: "pointer",
                  fontWeight: 950,
                  fontSize: 20,
                  boxShadow: active === "resources" ? "0 10px 24px rgba(16,24,39,.06)" : "none",
                }}
              >
                <span
                  style={{
                    width: 38,
                    height: 38,
                    borderRadius: 999,
                    display: "grid",
                    placeItems: "center",
                    background: "#F9FAFB",
                    border: "1px solid #D0D5DD",
                    color: "#667085",
                    fontSize: 17,
                    flex: "0 0 auto",
                  }}
                >
                  📁
                </span>
                <span>Resources</span>
              </button>
            </li>
          </ul>
        </aside>

        <main className={styles.main}>
          {showNoAccess ? (
            <div className={styles.card}>
              <div className={styles.cardTitle}>No ESAT products enabled</div>
              <div className={styles.muted}>
                Signed in as <b>{email}</b>, but no active ESAT product access was found.
                {err ? (
                  <>
                    <br />
                    Error: <b>{err}</b>
                  </>
                ) : null}
              </div>
            </div>
          ) : active === "practice" ? (
            <>
              <div className={styles.h1}>Practice Tests</div>

              <div className={styles.metaRow}>
                <div className={styles.meta}>
                  <span className={styles.dot} /> {currentTrack.subjects}
                </div>
                <div className={styles.meta}>4 full mock tests</div>
                {attemptsLoading ? <div className={styles.meta}>Loading attempts...</div> : null}
                {attemptsErr ? <div className={styles.meta}>Attempts not connected yet</div> : null}
              </div>

              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  gap: 10,
                  margin: "0 0 18px",
                }}
              >
                {TRACKS.map((track) => (
                  <button
                    key={track.key}
                    type="button"
                    onClick={() => setActiveTrack(track.key)}
                    style={{
                      border: activeTrack === track.key ? "2px solid #7A1F24" : "2px solid rgba(0,0,0,.14)",
                      background: activeTrack === track.key ? "#FFF3D1" : "#ffffff",
                      color: "#141414",
                      borderRadius: 999,
                      padding: "10px 14px",
                      fontWeight: 950,
                      cursor: "pointer",
                      fontSize: 13,
                      letterSpacing: ".02em",
                    }}
                  >
                    {track.label}
                  </button>
                ))}
              </div>

              <section
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(330px, 1fr))",
                  gap: 12,
                  maxWidth: 1120,
                }}
              >
                {currentTrack.mocks.map((mock) => {
                  const latest = latestByTestId[mock.test_id];
                  const attempted = !!latest;
                  const total = latest?.total_questions || 0;
                  const score = latest?.score ?? 0;
                  const date = fmtDate(latest?.submitted_at);

                  return (
                    <article
                      key={mock.test_id}
                      style={{
                        background: "#ffffff",
                        border: "1px solid #E5E7EB",
                        borderRadius: 16,
                        padding: 14,
                        minHeight: 185,
                        boxShadow: "0 1px 0 rgba(0,0,0,.04)",
                      }}
                    >
                      <h3
                        style={{
                          margin: "0 0 10px",
                          fontSize: 17,
                          lineHeight: 1.25,
                          fontWeight: 950,
                          letterSpacing: "-.01em",
                        }}
                      >
                        {mock.title}
                      </h3>

                      <div
                        style={{
                          fontSize: 12,
                          fontWeight: 950,
                          color: "#4B5563",
                          textTransform: "uppercase",
                          letterSpacing: ".03em",
                          marginBottom: 10,
                        }}
                      >
                        {mock.badge} · {mock.duration_minutes} min
                      </div>

                      <div
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          border: "1px solid #E5E7EB",
                          borderRadius: 999,
                          padding: "7px 10px",
                          fontSize: 12,
                          fontWeight: 950,
                          marginBottom: 12,
                          background: "#fff",
                        }}
                      >
                        {mock.subjects}
                      </div>

                      <div
                        style={{
                          fontSize: 12,
                          fontWeight: 900,
                          color: "#5E5E5E",
                          marginBottom: 16,
                          minHeight: 18,
                        }}
                      >
                        {attempted
                          ? `Attempt 1 · Score ${score}/${total || 81}${date ? ` · ${date}` : ""}`
                          : "Not attempted yet"}
                      </div>

                      <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                        <button
                          type="button"
                          onClick={() => openTest(mock)}
                          style={{
                            border: 0,
                            background: "#FEC94F",
                            color: "#141414",
                            borderRadius: 12,
                            padding: "11px 13px",
                            fontSize: 13,
                            fontWeight: 950,
                            cursor: "pointer",
                          }}
                        >
                          {attempted ? "Retake →" : "Start →"}
                        </button>

                        <button
                          type="button"
                          onClick={() => openAttempts(mock)}
                          style={{
                            border: "1px solid #E5E7EB",
                            background: "#ffffff",
                            color: "#141414",
                            borderRadius: 12,
                            padding: "11px 13px",
                            fontSize: 13,
                            fontWeight: 950,
                            cursor: "pointer",
                          }}
                        >
                          View attempts
                        </button>

                        <button
                          type="button"
                          onClick={() => openSolutions(mock)}
                          style={{
                            border: "1px solid #E5E7EB",
                            background: "#ffffff",
                            color: "#141414",
                            borderRadius: 12,
                            padding: "11px 13px",
                            fontSize: 13,
                            fontWeight: 950,
                            cursor: "pointer",
                          }}
                        >
                          Solutions
                        </button>
                      </div>
                    </article>
                  );
                })}
              </section>
            </>
          ) : active === "bank" ? (
            <>
              <div className={styles.h1}>Question Bank</div>

              <div className={styles.metaRow}>
                <div className={styles.meta}>
                  <span className={styles.dot} /> ESAT Question Bank
                </div>
                <div className={styles.meta}>Topic practice · Difficulty filters · Solutions</div>
              </div>

              <div className={styles.card}>
                <div className={styles.cardTitle}>ESAT Digital Question Bank</div>
                <div className={styles.muted} style={{ marginBottom: 14 }}>
                  Practise ESAT-style Maths questions with filters, navigator, checking, and worked solutions.
                </div>

                <button
                  className={`${styles.btn} ${styles.btnPrimary}`}
                  onClick={() => (window.location.href = "/esat-question-bank")}
                >
                  Open ESAT Question Bank
                </button>
              </div>
            </>
          ) : active === "resources" ? (
            <>
              <div className={styles.h1}>Resources</div>

              <div className={styles.metaRow}>
                <div className={styles.meta}>
                  <span className={styles.dot} /> Downloadable ESAT PDFs
                </div>
                <div className={styles.meta}>Formula sheets · Specification · Subject guides</div>
              </div>

              <section
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(270px, 1fr))",
                  gap: 14,
                  maxWidth: 980,
                }}
              >
                {ESAT_RESOURCE_PDFS.map((pdf) => (
                  <a
                    key={pdf.href}
                    href={pdf.href}
                    target="_blank"
                    rel="noreferrer"
                    download
                    style={{
                      display: "block",
                      background: "#ffffff",
                      border: "1px solid #E5E7EB",
                      borderRadius: 18,
                      padding: 18,
                      color: "#141414",
                      textDecoration: "none",
                      boxShadow: "0 1px 0 rgba(0,0,0,.04)",
                    }}
                  >
                    <div
                      style={{
                        width: 44,
                        height: 44,
                        borderRadius: 14,
                        display: "grid",
                        placeItems: "center",
                        background: "#FFF3D1",
                        border: "1px solid #F0DC8C",
                        fontSize: 22,
                        marginBottom: 14,
                      }}
                    >
                      📄
                    </div>

                    <div
                      style={{
                        fontSize: 20,
                        fontWeight: 950,
                        letterSpacing: "-.02em",
                        marginBottom: 8,
                        lineHeight: 1.15,
                      }}
                    >
                      {pdf.title}
                    </div>

                    <div
                      style={{
                        color: "#667085",
                        fontSize: 13,
                        fontWeight: 750,
                        lineHeight: 1.45,
                        marginBottom: 14,
                      }}
                    >
                      {pdf.description}
                    </div>

                    <div
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        borderRadius: 999,
                        padding: "9px 12px",
                        background: "#FEC94F",
                        color: "#141414",
                        fontSize: 12,
                        fontWeight: 950,
                        textTransform: "uppercase",
                        letterSpacing: ".06em",
                      }}
                    >
                      Download PDF →
                    </div>
                  </a>
                ))}
              </section>
            </>
          ) : (
            <>
              <div className={styles.h1}>Classes</div>

              <div className={styles.metaRow}>
                <div className={styles.meta}>
                  <span className={styles.dot} /> ESAT Live Classes
                </div>
                <div className={styles.meta}>Batches · Schedule · Join Zoom</div>
              </div>

              <div className={styles.card}>
                <div className={styles.cardTitle}>ESAT Group Sessions</div>
                <div className={styles.muted} style={{ marginBottom: 14 }}>
                  View the upcoming ESAT schedule below.
                </div>

                <div
                  style={{
                    width: "100%",
                    height: "78vh",
                    border: "1px solid #e5e7eb",
                    borderRadius: 14,
                    overflow: "hidden",
                    background: "#fff",
                  }}
                >
                  <iframe
                    src="/esat-classes/index.html"
                    title="ESAT Classes Schedule"
                    style={{
                      width: "100%",
                      height: "100%",
                      border: "none",
                      display: "block",
                      background: "white",
                    }}
                    allow="clipboard-read; clipboard-write; fullscreen"
                  />
                </div>
              </div>
            </>
          )}
        </main>
      </div>

      {modalOpen ? (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(17,24,39,.45)",
            display: "grid",
            placeItems: "center",
            zIndex: 1000,
            padding: 20,
          }}
          onClick={() => setModalOpen(false)}
        >
          <div
            style={{
              width: "min(720px, 100%)",
              maxHeight: "78vh",
              overflow: "auto",
              background: "#fff",
              borderRadius: 18,
              border: "1px solid #E5E7EB",
              padding: 20,
              boxShadow: "0 18px 50px rgba(0,0,0,.18)",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: "flex", justifyContent: "space-between", gap: 14, alignItems: "center" }}>
              <h2 style={{ margin: 0, fontSize: 22 }}>{modalTitle}</h2>
              <button className={styles.btn} type="button" onClick={() => setModalOpen(false)}>
                Close
              </button>
            </div>

            <div style={{ marginTop: 16 }}>
              {modalLoading ? (
                <div className={styles.muted}>Loading attempts...</div>
              ) : modalErr ? (
                <div className={styles.muted}>{modalErr}</div>
              ) : modalAttempts.length === 0 ? (
                <div className={styles.muted}>No attempts found yet.</div>
              ) : (
                modalAttempts.map((a, index) => (
                  <div
                    key={a.id || `${a.test_id}-${index}`}
                    style={{
                      border: "1px solid #E5E7EB",
                      borderRadius: 12,
                      padding: 12,
                      marginTop: 10,
                    }}
                  >
                    <b>Attempt {modalAttempts.length - index}</b>
                    <div className={styles.muted}>
                      Score {a.score ?? 0}/{a.total_questions || 81}
                      {a.submitted_at ? ` · ${fmtDate(a.submitted_at)}` : ""}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      ) : null}

      {solOpen ? (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(17,24,39,.45)",
            display: "grid",
            placeItems: "center",
            zIndex: 1000,
            padding: 20,
          }}
          onClick={() => setSolOpen(false)}
        >
          <div
            style={{
              width: "min(920px, 100%)",
              height: solUrl ? "78vh" : "auto",
              background: "#fff",
              borderRadius: 18,
              border: "1px solid #E5E7EB",
              padding: 20,
              boxShadow: "0 18px 50px rgba(0,0,0,.18)",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: "flex", justifyContent: "space-between", gap: 14, alignItems: "center" }}>
              <h2 style={{ margin: 0, fontSize: 22 }}>{solTitle}</h2>
              <button className={styles.btn} type="button" onClick={() => setSolOpen(false)}>
                Close
              </button>
            </div>

            {solUrl ? (
              <iframe
                src={solUrl}
                title={solTitle}
                style={{
                  width: "100%",
                  height: "calc(100% - 52px)",
                  border: "1px solid #E5E7EB",
                  borderRadius: 12,
                  marginTop: 14,
                }}
              />
            ) : (
              <div className={styles.muted} style={{ marginTop: 16 }}>
                Solutions will be attached here once the ESAT mock solutions are uploaded.
              </div>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
}


