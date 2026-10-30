"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { supabaseBrowser } from "@/utils/supabase/browser";
import { safeLoginDestination } from "@/lib/auth/login-destination";
import { loginErrorMessage } from "@/lib/auth/login-error";
import { IB_COURSES, ibSubject, ibSubjectForPath, ibHref, ibView, ibCourseLevel, ibQualification, type IbSubject } from "@/lib/ib/catalog";
import IbBrand from "../ib/IbBrand";
import ChemistryCourseSwitch from "../ib/components/ChemistryCourseSwitch";
import styles from "../ib/ib.module.css";

export default function IBLoginClient() {
  const search = useSearchParams();
  const safeNext = safeLoginDestination(search.get("next"));
  const parsed = new URL(safeNext, "https://apps.thrivingscholars.com");
  const isIbDestination = parsed.pathname === "/ib" || parsed.pathname.startsWith("/ib/");
  const subject = ibSubject(search.get("subject") ?? (isIbDestination ? parsed.searchParams.get("subject") ?? ibSubjectForPath(parsed.pathname) : null));
  const view = ibView(isIbDestination ? parsed.searchParams.get("view") : null);
  const courseLevel = ibCourseLevel(search.get("course") ?? (isIbDestination ? parsed.searchParams.get("course") : null));
  const next = isIbDestination && !search.has("subject") && !search.has("course") ? safeNext : ibHref(subject, view, courseLevel);
  const supabase = useMemo(() => supabaseBrowser(), []);
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [sentTo, setSentTo] = useState("");
  const [error, setError] = useState("");
  const [cooldown, setCooldown] = useState(false);
  const callbackError = search.get("e");
  useEffect(() => {
    let active = true;
    void supabase.auth.getUser().then(({ data }) => {
      if (active && data.user) window.location.replace(next);
    }).catch(() => { /* Keep the form available when there is no session. */ });
    return () => { active = false; };
  }, [next, supabase]);
  useEffect(() => {
    if (!cooldown) return;
    const timer = window.setTimeout(() => setCooldown(false), 60_000);
    return () => window.clearTimeout(timer);
  }, [cooldown]);

  async function sendLink(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy || cooldown) return;
    setBusy(true);
    setError("");
    const address = email.trim().toLowerCase();
    try {
      const intent = await fetch("/api/auth/login-intent", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ next }), cache: "no-store" });
      if (!intent.ok) throw new Error("We could not prepare your sign-in. Please try again.");
      const { error: authError } = await supabase.auth.signInWithOtp({ email: address, options: { emailRedirectTo: `${window.location.origin}/auth/callback` } });
      if (authError) throw authError;
      setSentTo(address);
      setCooldown(true);
    } catch (err) {
      setError(loginErrorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return <div className={styles.app}>
    <header className={styles.topbar}><Link href="/ib-login" className={styles.brandLink} aria-label="Thriving Scholars IB home"><IbBrand /></Link><span className={styles.loginHeaderTag}>YOUR NEXT CHAPTER STARTS HERE</span></header>
    <main className={styles.loginMain}>
      <section className={styles.loginIntro}><span className={styles.eyebrow}>IB DIPLOMA PROGRAMME · {ibQualification(subject, courseLevel).toUpperCase()}</span><h1>Big ideas.<br />Steady progress.<br /><span>Your IB journey.</span></h1><p>A dedicated space for Maths AA HL, Physics HL and Chemistry SL/HL. Build understanding, question by question.</p><div className={styles.loginFeatures}><div><span aria-hidden="true">▤</span><strong>Topic by topic</strong><p>A clear path through your question bank.</p></div><div><span aria-hidden="true">✎</span><strong>Every step matters</strong><p>Written mark schemes for deeper understanding.</p></div></div><div className={styles.loginStatus}><span className={styles.statusDot} /><span>Original questions · Separate written mark schemes</span></div></section>
      <section className={styles.loginCard} aria-labelledby="signin-title"><span className={styles.cardEyebrow}>WELCOME TO YOUR LEARNING SPACE</span><h2 id="signin-title">Let’s get started<span className={styles.headingDot}>.</span></h2><p>Choose your subject and sign in with your email.</p><nav className={styles.subjectSwitch} aria-label="Subject">{(Object.keys(IB_COURSES) as IbSubject[]).map(id => <Link key={id} href={`/ib-login?next=${encodeURIComponent(ibHref(id, view, courseLevel))}`} prefetch={false} aria-current={subject === id ? "page" : undefined} className={id === subject ? styles.subjectActive : ""}><span aria-hidden="true">{IB_COURSES[id].symbol}</span>{IB_COURSES[id].label}</Link>)}</nav>
        {subject === "chemistry" ? <ChemistryCourseSwitch course={courseLevel} links={{ sl: `/ib-login?next=${encodeURIComponent(ibHref(subject, view, "sl"))}`, hl: `/ib-login?next=${encodeURIComponent(ibHref(subject, view, "hl"))}` }} /> : null}
        <form onSubmit={sendLink}><label className={styles.emailLabel} htmlFor="ib-email">Email address</label><input id="ib-email" className={styles.emailInput} type="email" autoComplete="email" inputMode="email" required maxLength={254} placeholder="you@example.com" value={email} onChange={event => setEmail(event.target.value)} disabled={busy} /><button className={styles.primaryButton} type="submit" disabled={busy || cooldown}>{busy ? "Sending your link…" : cooldown ? "Link sent — check your inbox" : sentTo ? "Send a new sign-in link" : "Email me a sign-in link"}<span aria-hidden="true">↗</span></button></form>
        {error ? <p role="alert" className={styles.error}>{error}</p> : callbackError && !sentTo ? <p role="alert" className={styles.error}>{callbackError === "missing_env" ? "Sign-in is temporarily unavailable. Please try again shortly." : "That link has expired or has already been used. Request a new sign-in link below."}</p> : null}
        {sentTo ? <div role="status" className={styles.success}><strong>Check your inbox</strong><p>We sent a sign-in link to <b>{sentTo}</b>. Check spam too, and open the newest link in this browser and on this device.</p><p>You can request another link after one minute.</p></div> : null}
        <div className={styles.loginHint}><span aria-hidden="true">◇</span><p>No password to remember. We’ll email you a secure, one-time sign-in link.</p></div><div className={styles.loginCardFooter}>One Thriving Scholars account. All your IB subjects.</div>
      </section>
    </main><footer className={`${styles.footer} ${styles.loginFooter}`}><span>THRIVING SCHOLARS</span><span>Learn with purpose. Practise with confidence.</span></footer>
  </div>;
}
