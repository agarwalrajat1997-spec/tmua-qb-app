"use client";

import { useEffect, useId, useRef, useState, type FormEvent } from "react";
import "./ib-trial.css";

type Programme = "tmua" | "esat" | "ib";

type TrialConfirmation = {
  status: "trial_started" | "trial_already_active";
  expiresAt: string;
  loginEmailSent: boolean;
  welcomeEmailSent: boolean;
  resendLimited: boolean;
  retryAfterSeconds: number | null;
};

type FormState =
  | { kind: "idle" | "submitting" }
  | { kind: "error"; message: string }
  | { kind: "success"; confirmation: TrialConfirmation };

const PROGRAMMES = {
  ib: {
    name: "IB",
    access: "Question Banks + Mock Tests + Written Mark Schemes",
    description: "Find your rhythm with two free days inside your IB study space. Explore your subjects at SL or HL and see how clearer practice feels.",
    scope: "Explore the available IB question banks, mock tests and written mark schemes. Live 1:1 tutoring is a separate service.",
    portalUrl: "https://apps.thrivingscholars.com/ib-login?next=%2Fib",
  },
  tmua: {
    name: "TMUA",
    access: "Question Bank + Practice Tests",
    description: "Explore topic practice, worked solutions and digital tests in your TMUA workspace.",
    scope: "Your trial includes the TMUA Question Bank and Practice Tests.",
    portalUrl: "https://apps.thrivingscholars.com/dashboard",
  },
  esat: {
    name: "ESAT",
    access: "Question Bank + Classes",
    description: "Explore the ESAT Question Bank and classes area, with practice across your chosen modules.",
    scope: "Your trial includes the ESAT Question Bank and classes area. Full mock tests are not included in this trial.",
    portalUrl: "https://apps.thrivingscholars.com/esat",
  },
} as const;

function parseConfirmation(data: Record<string, unknown>): TrialConfirmation | null {
  if (
    data.ok !== true ||
    (data.status !== "trial_started" && data.status !== "trial_already_active") ||
    typeof data.expires_at !== "string" ||
    !Number.isFinite(Date.parse(data.expires_at)) ||
    Date.parse(data.expires_at) <= Date.now()
  ) return null;

  return {
    status: data.status,
    expiresAt: new Date(data.expires_at).toISOString(),
    loginEmailSent: data.login_email_sent === true,
    welcomeEmailSent: data.welcome_email_sent === true,
    resendLimited: data.email_resend_limited === true,
    retryAfterSeconds: typeof data.retry_after_seconds === "number" &&
      Number.isFinite(data.retry_after_seconds) && data.retry_after_seconds > 0
      ? Math.ceil(data.retry_after_seconds)
      : null,
  };
}

function emailStatus(confirmation: TrialConfirmation): string {
  if (confirmation.loginEmailSent && confirmation.welcomeEmailSent) {
    return "Your sign-in email and trial welcome email have been sent. Check your inbox and spam folder.";
  }
  if (confirmation.loginEmailSent) {
    return "Your sign-in email has been sent. The separate welcome email was not confirmed as sent; your trial access is still active.";
  }
  if (confirmation.welcomeEmailSent) {
    return "Your trial welcome email has been sent, but the sign-in email was not confirmed as sent. Open the portal to sign in or request a login link.";
  }
  if (confirmation.resendLimited) {
    return "A recent request is within the email resend limit. No new emails were confirmed for this request. Check your inbox and spam folder for an earlier access email, or open the portal to sign in.";
  }
  return "Your trial is active, but we could not confirm that either email was sent. Open the portal to sign in or request a login link.";
}

function requestError(status: number, data: Record<string, unknown>): string {
  const code = data.code ?? data.error ?? data.status;
  if (status === 409 && code === "trial_already_used") {
    return "The free trial for this programme has already been used and cannot be restarted. If you have paid access, sign in to your portal as usual.";
  }
  if (status === 429) {
    return "There have been too many requests. Please wait a few minutes, then try again. If you already requested access, check your inbox first.";
  }
  if (status === 400 || status === 422) {
    return "Please check your name and email address, confirm the consent box, and try again.";
  }
  return "We could not confirm your trial request. It may already have been activated, so check your inbox or open the portal before trying again.";
}

export function IBTrialForm() {
  const programme: Programme = "ib";
  const config = PROGRAMMES[programme];
  const fieldId = useId();
  const [state, setState] = useState<FormState>({ kind: "idle" });
  const requestInFlight = useRef(false);
  const controllerRef = useRef<AbortController | null>(null);
  const resultRef = useRef<HTMLDivElement>(null);
  const endpoint = `https://apps.thrivingscholars.com/api/public/${programme}-free-trial`;
  const busy = state.kind === "submitting";

  useEffect(() => () => controllerRef.current?.abort(), []);
  useEffect(() => {
    if (state.kind === "success" || state.kind === "error") {
      resultRef.current?.focus({ preventScroll: true });
    }
  }, [state]);

  async function submitTrial(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (requestInFlight.current) return;

    const form = event.currentTarget;
    if (!form.reportValidity()) return;
    const fields = new FormData(form);
    const studentName = String(fields.get("student_name") ?? "").trim();
    const email = String(fields.get("email") ?? "").trim();
    if (!studentName || !email || fields.get("consent") !== "yes") {
      setState({ kind: "error", message: "Enter your name and email address, and confirm the consent box to request your trial." });
      return;
    }

    requestInFlight.current = true;
    setState({ kind: "submitting" });
    const controller = new AbortController();
    controllerRef.current = controller;
    const timeout = window.setTimeout(() => controller.abort(), 45000);

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "omit",
        cache: "no-store",
        referrerPolicy: "no-referrer",
        signal: controller.signal,
        body: JSON.stringify({ email, student_name: studentName, program: programme }),
      });
      const raw: unknown = await response.json().catch(() => null);
      const data = raw && typeof raw === "object" && !Array.isArray(raw)
        ? raw as Record<string, unknown>
        : {};
      const confirmation = response.ok ? parseConfirmation(data) : null;

      if (confirmation) {
        setState({ kind: "success", confirmation });
      } else {
        setState({ kind: "error", message: requestError(response.status, data) });
      }
    } catch {
      setState({
        kind: "error",
        message: "We could not confirm the response. Your trial may already be active. Check your inbox or open the portal before trying again.",
      });
    } finally {
      window.clearTimeout(timeout);
      requestInFlight.current = false;
      controllerRef.current = null;
    }
  }

  return (
    <section className="programme-trial-section" id="free-trial" aria-labelledby={`${fieldId}-heading`}>
      <div className="page-width">
        <div className="programme-trial-card">
          <div className="programme-trial-intro">
            <span className="programme-trial-badge">48 hours · Free</span>
            <p className="programme-trial-eyebrow">{config.name} portal trial</p>
            <h2 id={`${fieldId}-heading`}>Try the portal.<br />Find your next step.</h2>
            <p className="programme-trial-description">{config.description}</p>
            <div className="programme-trial-inclusions">
              <span aria-hidden="true">✓</span>
              <div><strong>{config.access}</strong><p>{config.scope}</p></div>
            </div>
            <p className="programme-trial-terms">
              Your 48 hours start when the trial is activated. One trial per programme; it cannot be restarted or extended. Existing paid access stays unchanged.
            </p>
          </div>

          <div className="programme-trial-panel">
            {state.kind === "success" ? (
              <div className="programme-trial-result" ref={resultRef} role="status" tabIndex={-1}>
                <span className="programme-trial-success-icon" aria-hidden="true">✓</span>
                <h3>{state.confirmation.status === "trial_already_active" ? "Your trial is already active." : `Your ${config.name} trial is ready.`}</h3>
                <p className="programme-trial-expiry">
                  Trial access ends<br />
                  <strong><time dateTime={state.confirmation.expiresAt}>{new Intl.DateTimeFormat(undefined, {
                    dateStyle: "medium",
                    timeStyle: "short",
                  }).format(new Date(state.confirmation.expiresAt))}</time></strong>
                  <span>Your local time: {Intl.DateTimeFormat().resolvedOptions().timeZone}</span>
                </p>
                {state.confirmation.status === "trial_already_active" ? (
                  <p>Your original expiry is unchanged. Requesting the trial again does not add another 48 hours.</p>
                ) : null}
                <p>{emailStatus(state.confirmation)}</p>
                {state.confirmation.resendLimited && state.confirmation.retryAfterSeconds ? (
                  <p className="programme-trial-small">Please allow about {Math.ceil(state.confirmation.retryAfterSeconds / 60)} {state.confirmation.retryAfterSeconds <= 60 ? "minute" : "minutes"} before another email request. This will not extend access.</p>
                ) : null}
                <a className="programme-trial-submit" href={config.portalUrl}>Open {config.name} portal <span aria-hidden="true">↗</span></a>
                <p className="programme-trial-small">Use the same email address you entered for this trial. Any existing paid access keeps its original expiry.</p>
              </div>
            ) : (
              <form className="programme-trial-form" onSubmit={submitTrial} method="post" aria-busy={busy}>
                <h3>Start your free {config.name} trial</h3>
                <p className="programme-trial-small">No payment details needed. We’ll request your access and email sign-in instructions.</p>
                <fieldset disabled={busy}>
                  <legend className="programme-trial-sr-only">Your trial details and consent</legend>
                  <div className="programme-trial-field">
                    <label htmlFor={`${fieldId}-name`}>Your name</label>
                    <input id={`${fieldId}-name`} name="student_name" type="text" autoComplete="name" maxLength={120} required placeholder="Full name" />
                  </div>
                  <div className="programme-trial-field">
                    <label htmlFor={`${fieldId}-email`}>Email address</label>
                    <input id={`${fieldId}-email`} name="email" type="email" autoComplete="email" autoCapitalize="none" spellCheck={false} maxLength={254} required placeholder="you@example.com" aria-describedby={`${fieldId}-email-hint`} />
                    <span id={`${fieldId}-email-hint`}>Use the email you’ll use to sign in to the portal.</span>
                  </div>
                  <label className="programme-trial-consent" htmlFor={`${fieldId}-consent`}>
                    <input id={`${fieldId}-consent`} name="consent" type="checkbox" value="yes" required />
                    <span>I agree that Thriving Scholars may process my name, email address, programme, trial expiry and portal link through Supabase and EmailJS to activate my trial and send access emails.</span>
                  </label>
                  <button className="programme-trial-submit" type="submit">
                    {busy ? "Requesting your trial…" : programme === "ib" ? "Start my free 2-day trial" : "Start my 48-hour trial"}
                    {!busy ? <span aria-hidden="true">→</span> : null}
                  </button>
                </fieldset>
                {state.kind === "error" ? (
                  <div className="programme-trial-error" role="alert" ref={resultRef} tabIndex={-1}>{state.message}</div>
                ) : null}
                <p className="programme-trial-signin">Already have access? <a href={config.portalUrl}>Sign in to {config.name} ↗</a></p>
                <noscript><p className="programme-trial-error">Enable JavaScript to request a trial securely, or <a href={config.portalUrl}>open the portal</a> to sign in.</p></noscript>
              </form>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
