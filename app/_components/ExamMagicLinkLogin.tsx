"use client";

import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { useRouter } from "next/navigation";
import { supabaseBrowser } from "@/utils/supabase/browser";
import styles from "./exam-login.module.css";

type Props = {
  exam: "AMC" | "SAT";
  destination: "/amc" | "/sat";
  uiMark: string;
};

export default function ExamMagicLinkLogin({ exam, destination, uiMark }: Props) {
  const router = useRouter();
  const supabase = useMemo(() => supabaseBrowser(), []);
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    void supabase.auth.getSession().then(({ data }) => {
      if (active && data.session) router.replace(destination);
    });

    return () => {
      active = false;
    };
  }, [destination, router, supabase]);

  async function sendLink(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setMessage(null);

    const normalizedEmail = email.trim().toLowerCase();

    if (!normalizedEmail || !normalizedEmail.includes("@")) {
      setError("Enter a valid email address.");
      return;
    }

    setBusy(true);

    try {
      const intentResponse = await fetch("/api/auth/login-intent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ next: destination }),
        cache: "no-store",
      });

      if (!intentResponse.ok) {
        throw new Error(`Could not save the requested ${exam} portal.`);
      }

      const { error: signInError } = await supabase.auth.signInWithOtp({
        email: normalizedEmail,
        options: {
          emailRedirectTo: `${window.location.origin}/auth/callback`,
        },
      });

      if (signInError) throw signInError;

      setMessage(
        "Login link sent. Check your inbox and spam folder, then open only the newest link.",
      );
    } catch (caught: unknown) {
      setError(
        caught instanceof Error ? caught.message : "Could not send the login link.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className={styles.page} data-ui={uiMark}>
      <header className={styles.topbar}>
        <div>
          <div className={styles.brand}>Thriving Scholars</div>
          <div className={styles.tag}>{exam} Student Portal</div>
        </div>
        <div className={styles.secure}>Paid Access &bull; Secure Login</div>
      </header>

      <main className={styles.main}>
        <section className={styles.card}>
          <div className={styles.kicker}>{exam} PORTAL</div>
          <h1>Sign in with your registered email</h1>
          <p className={styles.lead}>
            Use the email connected to your {exam} access. We will send you a
            secure, single-use login link.
          </p>

          <form onSubmit={sendLink} className={styles.form}>
            <label htmlFor={`${exam.toLowerCase()}-email`}>Email address</label>
            <input
              id={`${exam.toLowerCase()}-email`}
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="name@email.com"
              autoComplete="email"
              inputMode="email"
              required
            />
            <button type="submit" disabled={busy}>
              {busy ? "Sending..." : "Send secure login link"}
            </button>
          </form>

          {error ? <div className={styles.error}>{error}</div> : null}
          {message ? <div className={styles.success}>{message}</div> : null}

          <div className={styles.help}>
            <b>Need help?</b> outreach@thrivingscholars.com
            <br />
            WhatsApp +44 7459 070019
          </div>
          <div className={styles.tip}>
            Login links are single-use. If you request more than one, open only
            the newest email.
          </div>
        </section>
      </main>
    </div>
  );
}
