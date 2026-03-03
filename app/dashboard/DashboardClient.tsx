"use client";

import React, { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@supabase/supabase-js";
import styles from "./dashboard.module.css";

type PracticeTest = {
  id: string; // stable localStorage key
  title: string;
  section: "topic" | "full";
  badge: "PAPER 1" | "PAPER 2" | "FULL" | "OFFICIAL";
  duration_minutes: number;
  topics: string[];
  file: string; // filename in /public/practice-tests/tests/
};

function getSupabase() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!url || !key) return null;
  return createClient(url, key);
}

function parseHash(hash: string) {
  const h = (hash || "").startsWith("#") ? (hash || "").slice(1) : (hash || "");
  try {
    return new URLSearchParams(h);
  } catch {
    return new URLSearchParams();
  }
}

const ATTEMPT_KEY = "ts_practice_attempted_v1";

function readAttempted(): Record<string, boolean> {
  try {
    return JSON.parse(localStorage.getItem(ATTEMPT_KEY) || "{}");
  } catch {
    return {};
  }
}

function writeAttempted(map: Record<string, boolean>) {
  localStorage.setItem(ATTEMPT_KEY, JSON.stringify(map));
}

type Product = "practice-tests" | "tmua-question-bank";

export default function DashboardClient({ uiMark }: { uiMark: string }) {
  const router = useRouter();
  const supabase = useMemo(() => getSupabase(), []);

  const [email, setEmail] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [active, setActive] = useState<"practice" | "bank">("practice");
  const [err, setErr] = useState<string | null>(null);

  const [attempted, setAttempted] = useState<Record<string, boolean>>({});
  const [products, setProducts] = useState<Product[]>([]);
  const [accessLoading, setAccessLoading] = useState(true);
  const [accessErr, setAccessErr] = useState<string | null>(null);

  const ARROW = "\u2192";

  // ✅ Your actual test files (public/practice-tests/tests/*)
  const TESTS: PracticeTest[] = useMemo(
    () => [
      {
        id: "p1-mock-01",
        title: "TMUA Mock Test 1 (Paper 1)",
        section: "topic",
        badge: "PAPER 1",
        duration_minutes: 75,
        topics: ["Algebra", "Sequences", "Functions", "Geometry"],
        file: "p1-mock-01-algebra-sequences-functions-geometry.html",
      },
      {
        id: "p1-mock-02",
        title: "TMUA Mock Test 2 (Paper 1)",
        section: "topic",
        badge: "PAPER 1",
        duration_minutes: 75,
        topics: ["Graphs", "Trigonometry", "Logarithms"],
        file: "p1-mock-02-graphs-trig-logs.html",
      },
      {
        id: "p1-mock-03",
        title: "TMUA Mock Test 3 (Paper 1)",
        section: "topic",
        badge: "PAPER 1",
        duration_minutes: 75,
        topics: ["Calculus"],
        file: "p1-mock-03-calculus.html",
      },
      {
        id: "p1-mock-05",
        title: "TMUA Mock Test 5 (Paper 1 · All Topics)",
        section: "topic",
        badge: "PAPER 1",
        duration_minutes: 75,
        topics: ["All Topics"],
        file: "p1-mock-05-all-topics.html",
      },
      {
        id: "p2-mock-04",
        title: "TMUA Mock Test 4 (Paper 2 · Logic & Proofs)",
        section: "topic",
        badge: "PAPER 2",
        duration_minutes: 75,
        topics: ["Logic", "Proofs"],
        file: "p2-mock-04-logic-proofs.html",
      },
      {
        id: "p2-mock-06",
        title: "TMUA Mock Test 6 (Paper 2 · All Topics)",
        section: "topic",
        badge: "PAPER 2",
        duration_minutes: 75,
        topics: ["All Topics"],
        file: "p2-mock-06-all-topics.html",
      },
      {
        id: "full-mock-01",
        title: "TMUA Mock Full Test 1 (P1 + P2)",
        section: "full",
        badge: "FULL",
        duration_minutes: 150,
        topics: ["All Topics"],
        file: "full-mock-01-all-topics.html",
      },
      {
        id: "full-mock-02",
        title: "TMUA Mock Full Test 2 (P1 + P2)",
        section: "full",
        badge: "FULL",
        duration_minutes: 150,
        topics: ["All Topics"],
        file: "full-mock-02-all-topics.html",
      },
      {
        id: "full-official-2022",
        title: "TMUA Official 2022 (P1 + P2)",
        section: "full",
        badge: "OFFICIAL",
        duration_minutes: 150,
        topics: ["All Topics"],
        file: "full-official-2022.html",
      },
      {
        id: "full-official-2023",
        title: "TMUA Official 2023 (P1 + P2)",
        section: "full",
        badge: "OFFICIAL",
        duration_minutes: 150,
        topics: ["All Topics"],
        file: "full-official-2023.html",
      },
    ],
    []
  );

  useEffect(() => {
    (async () => {
      setErr(null);

      if (!supabase) {
        setErr("Supabase env vars missing: NEXT_PUBLIC_SUPABASE_URL / NEXT_PUBLIC_SUPABASE_ANON_KEY");
        setLoading(false);
        return;
      }

      // 1) If magic link landed here with tokens in hash, set session
      try {
        const url = new URL(window.location.href);
        const q = url.searchParams;
        const hp = parseHash(url.hash);

        const e = q.get("error") || hp.get("error");
        const ed = q.get("error_description") || hp.get("error_description");
        if (e) {
          router.replace(`/login?e=${encodeURIComponent(ed || e)}`);
          return;
        }

        const code = q.get("code");
        if (code) {
          const { error } = await supabase.auth.exchangeCodeForSession(code);
          if (error) {
            router.replace(`/login?e=${encodeURIComponent(error.message)}`);
            return;
          }
          try {
            window.history.replaceState({}, "", "/dashboard");
          } catch {}
        } else {
          const access_token = hp.get("access_token");
          const refresh_token = hp.get("refresh_token");
          if (access_token && refresh_token) {
            const { error } = await supabase.auth.setSession({ access_token, refresh_token });
            if (error) {
              router.replace(`/login?e=${encodeURIComponent(error.message)}`);
              return;
            }
            try {
              window.history.replaceState({}, "", "/dashboard");
            } catch {}
          }
        }
      } catch {}

      // 2) Require session
      const { data } = await supabase.auth.getSession();
      if (!data.session) {
        router.replace("/login");
        return;
      }

      const userEmail = (data.session.user.email || "").toLowerCase();
      setEmail(userEmail);

      // ✅ load attempted map (local only)
      setAttempted(readAttempted());

      // 3) Load products for this student (from student_access)
      setAccessLoading(true);
      setAccessErr(null);

      try {
        const { data: rows, error } = await supabase
          .from("student_access")
          .select("product,approved")
          .eq("email", userEmail)
          .eq("approved", true);

        if (error) {
          setProducts([]);
          setAccessErr(error.message);
        } else {
          const ps = (rows || [])
            .map((r: any) => r.product as Product)
            .filter((p) => p === "practice-tests" || p === "tmua-question-bank");

          // de-dupe
          const unique = Array.from(new Set(ps));
          setProducts(unique);
        }
      } catch (e: any) {
        setProducts([]);
        setAccessErr(e?.message || "Failed to load access.");
      } finally {
        setAccessLoading(false);
      }

      setLoading(false);
    })();
  }, [router, supabase]);

  const hasPractice = products.includes("practice-tests");
  const hasBank = products.includes("tmua-question-bank");

  // If user only has one product, force active tab to it
  useEffect(() => {
    if (accessLoading) return;

    if (hasPractice && !hasBank) setActive("practice");
    if (!hasPractice && hasBank) setActive("bank");

    // If neither: keep current but UI will show "no access"
  }, [accessLoading, hasPractice, hasBank]);

  const topicTests = useMemo(() => TESTS.filter((t) => t.section === "topic"), [TESTS]);
  const fullTests = useMemo(() => TESTS.filter((t) => t.section === "full"), [TESTS]);

  const doneCount = useMemo(() => TESTS.filter((t) => !!attempted[t.id]).length, [TESTS, attempted]);
  const leftCount = useMemo(() => Math.max(0, TESTS.length - doneCount), [TESTS.length, doneCount]);

  const nextRecommended = useMemo(() => {
    const next = TESTS.find((t) => !attempted[t.id]);
    return next ? `Next recommended: ${next.title}` : "All tests completed.";
  }, [TESTS, attempted]);

  function openTest(t: PracticeTest) {
    // ✅ Mark attempted locally (so card updates immediately)
    const next = { ...attempted, [t.id]: true };
    setAttempted(next);
    writeAttempted(next);

    // ✅ Open real static file under public/
    window.location.href = `/practice-tests/tests/${t.file}`;
  }

  async function logout() {
    if (!supabase) return;
    await supabase.auth.signOut();
    router.replace("/login");
  }

  function resetAttempts() {
    const ok = confirm("Reset Attempted status on this device?");
    if (!ok) return;
    localStorage.removeItem(ATTEMPT_KEY);
    setAttempted({});
  }

  if (loading) {
    return (
      <div className={styles.page} data-ui={uiMark}>
        <div className={styles.topbar}>
          <div className={styles.brand}>
            <div className={styles.brandName}>Thriving Scholars</div>
            <div className={styles.brandTag}>TMUA Student Portal</div>
          </div>
          <div className={styles.right}>
            <div className={styles.pill}>Loading...</div>
          </div>
        </div>
        <div className={styles.main}>
          <div className={styles.card}>
            <div className={styles.cardTitle}>Loading TMUA Student Portal...</div>
            <div className={styles.muted}>If this takes longer than usual, refresh the page and try again.</div>
          </div>
        </div>
      </div>
    );
  }

  const showNoAccess = !accessLoading && !hasPractice && !hasBank;

  return (
    <div className={styles.page} data-ui={uiMark}>
      <div className={styles.topbar}>
        <div className={styles.brand}>
          <div className={styles.brandName}>Thriving Scholars</div>
          <div className={styles.brandTag}>TMUA Student Portal</div>
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
            Your TMUA
            <br />
            Workspace
          </div>
          <div className={styles.sideSub}>Practice tests + question bank. Clean, focused, tracked.</div>

          <ul className={styles.nav}>
            {hasPractice && (
              <li>
                <button
                  className={`${styles.navBtn} ${active === "practice" ? styles.navBtnOn : ""}`}
                  onClick={() => setActive("practice")}
                  type="button"
                >
                  <span className={styles.step}>1</span>
                  <span className={styles.navLabel}>Practice Tests</span>
                </button>
              </li>
            )}

            {hasBank && (
              <li>
                <button
                  className={`${styles.navBtn} ${active === "bank" ? styles.navBtnOn : ""}`}
                  onClick={() => setActive("bank")}
                  type="button"
                >
                  <span className={styles.step}>2</span>
                  <span className={styles.navLabel}>Question Bank</span>
                </button>
              </li>
            )}
          </ul>

          <div className={styles.card} style={{ margin: "16px 18px 0" }}>
            <div className={styles.muted}>
              Support: <b>outreach@thrivingscholars.com</b>
              <br />
              WhatsApp: <b>+44 7459 070019</b>
            </div>
          </div>

          {!accessLoading && accessErr && (
            <div className={styles.card} style={{ margin: "12px 18px 0" }}>
              <div className={styles.cardTitle}>Access status</div>
              <div className={styles.muted}>
                Could not load product access.
                <br />
                <span style={{ opacity: 0.9 }}>{accessErr}</span>
              </div>
            </div>
          )}
        </aside>

        <main className={styles.main}>
          {accessLoading ? (
            <div className={styles.card}>
              <div className={styles.cardTitle}>Loading access...</div>
              <div className={styles.muted}>Checking your purchased products.</div>
            </div>
          ) : showNoAccess ? (
            <div className={styles.card}>
              <div className={styles.cardTitle}>No products enabled</div>
              <div className={styles.muted}>
                Your account is signed in, but no TMUA products are enabled yet.
                <br />
                Please contact <b>outreach@thrivingscholars.com</b> (WhatsApp <b>+44 7459 070019</b>).
              </div>
            </div>
          ) : active === "practice" ? (
            <>
              <div className={styles.h1}>Practice Tests</div>

              <div className={styles.metaRow}>
                <div className={styles.meta}>
                  <span className={styles.dot} /> Done {doneCount}/{TESTS.length}
                </div>
                <div className={styles.meta}>Left {leftCount}</div>
                <div className={styles.meta}>TMUA 2026</div>
              </div>

              <div className={styles.card}>
                <div className={styles.cardTitle}>Roadmap</div>
                <div className={styles.muted}>
                  Topic Tests {ARROW} Full-Length Tests {ARROW} Official (2022/2023) last
                  <div style={{ marginTop: 8 }}>
                    <b>{nextRecommended}</b>
                  </div>

                  <div style={{ marginTop: 12, display: "flex", gap: 10, flexWrap: "wrap" }}>
                    <button className={styles.btn} onClick={resetAttempts} type="button">
                      Reset Attempted Status
                    </button>
                  </div>
                </div>
              </div>

              {err && (
                <div className={styles.card}>
                  <div className={styles.cardTitle}>Supabase status</div>
                  <div className={styles.muted}>{err}</div>
                </div>
              )}

              {/* ✅ Section 1: Topic Tests */}
              <div className={styles.card}>
                <div className={styles.cardTitle}>Topic tests</div>
                <div className={styles.grid}>
                  {topicTests.map((t) => {
                    const isDone = !!attempted[t.id];
                    const status = isDone ? "Attempted" : "Not attempted yet";
                    return (
                      <div key={t.id} className={styles.test}>
                        <div className={styles.testTitle}>{t.title}</div>

                        <div className={styles.testMeta}>
                          <span>{t.badge}</span>
                          <span> · </span>
                          <span>{t.duration_minutes} min</span>
                        </div>

                        <div className={styles.tags}>
                          {(t.topics || []).slice(0, 6).map((x) => (
                            <span className={styles.tag} key={x}>
                              {x}
                            </span>
                          ))}
                        </div>

                        <div className={styles.muted}>{status}</div>

                        <button className={styles.go} onClick={() => openTest(t)}>
                          {isDone ? "Retake" : "Start"} {ARROW}
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* ✅ Section 2: Full Length Tests */}
              <div className={styles.card}>
                <div className={styles.cardTitle}>Full-length tests</div>
                <div className={styles.grid}>
                  {fullTests.map((t) => {
                    const isDone = !!attempted[t.id];
                    const status = isDone ? "Attempted" : "Not attempted yet";
                    return (
                      <div key={t.id} className={styles.test}>
                        <div className={styles.testTitle}>{t.title}</div>

                        <div className={styles.testMeta}>
                          <span>{t.badge}</span>
                          <span> · </span>
                          <span>{t.duration_minutes} min</span>
                        </div>

                        <div className={styles.tags}>
                          {(t.topics || []).slice(0, 6).map((x) => (
                            <span className={styles.tag} key={x}>
                              {x}
                            </span>
                          ))}
                        </div>

                        <div className={styles.muted}>{status}</div>

                        <button className={styles.go} onClick={() => openTest(t)}>
                          {isDone ? "Retake" : "Start"} {ARROW}
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className={styles.card}>
                <div className={styles.cardTitle}>Need help?</div>
                <div className={styles.support}>
                  email <b>outreach@thrivingscholars.com</b> (WhatsApp <b>+44 7459 070019</b>)
                </div>
              </div>
            </>
          ) : (
            <>
              {/* ✅ QUESTION BANK SECTION */}
              <div className={styles.h1}>Question Bank</div>

              <div className={styles.metaRow}>
                <div className={styles.meta}>
                  <span className={styles.dot} /> TMUA Question Bank
                </div>
                <div className={styles.meta}>Filter · Bookmark · Solutions</div>
              </div>

              <div className={styles.card}>
                <div className={styles.cardTitle}>Open the Question Bank</div>
                <div className={styles.muted}></div>

                <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 12 }}>
                  <button
                    className={`${styles.btn} ${styles.btnPrimary}`}
                    onClick={() => (window.location.href = "/tmua-question-bank")}
                  >
                    Open TMUA Question Bank
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