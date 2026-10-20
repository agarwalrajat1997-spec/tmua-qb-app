import { createClient } from "@supabase/supabase-js";
import { serviceFetch } from "@/lib/auth/service-recovery";
import { sendTrialWelcomeEmail, type TrialProgram } from "@/lib/server/trial-welcome-email";

const PRODUCTION_ORIGINS = new Set([
  "https://www.thrivingscholars.com",
  "https://thrivingscholars.com",
]);
const EMAIL_PATTERN = /^[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}$/i;
const MAX_BODY_BYTES = 4_096;
const EMAIL_COOLDOWN_SECONDS = 300;
const PROGRAMMES = {
  tmua: { dashboard: "/dashboard", grant: "grant_tmua_free_trial", table: "tmua_free_trials",
    marker: "mark_tmua_trial_started_email_sent" },
  esat: { dashboard: "/esat", grant: "grant_esat_free_trial", table: "esat_free_trials",
    marker: "mark_esat_trial_started_email_sent" },
} as const;

type TrialResult = {
  out_status?: "invalid_email" | "trial_started" | "trial_already_active" | "trial_already_used";
  out_started_at?: string | null;
  out_expires_at?: string | null;
};

function requiredEnv(name: string) {
  const value = process.env[name];
  if (!value) throw new Error(`Missing environment variable: ${name}`);
  return value;
}

function trialClients() {
  const url = requiredEnv("NEXT_PUBLIC_SUPABASE_URL");
  const serviceKey = requiredEnv("SUPABASE_SERVICE_ROLE_KEY");
  const publicKey = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY ||
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || requiredEnv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY");
  const options = { global: { fetch: serviceFetch },
    auth: { persistSession: false, autoRefreshToken: false } };
  return { admin: createClient(url, serviceKey, options), auth: createClient(url, publicKey, options) };
}

function allowedOrigin(request: Request) {
  const origin = request.headers.get("origin");
  if (origin && PRODUCTION_ORIGINS.has(origin)) return origin;
  if (origin && process.env.NODE_ENV !== "production" &&
    /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origin)) return origin;
  return null;
}

function responseHeaders(origin: string | null) {
  const headers: Record<string, string> = {
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Content-Type": "application/json; charset=utf-8",
    Vary: "Origin",
  };
  if (origin) Object.assign(headers, {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "600",
  });
  return headers;
}

function json(origin: string | null, body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: responseHeaders(origin) });
}

// Bound streamed requests too: Content-Length alone does not protect chunked bodies.
async function readBody(request: Request): Promise<Record<string, unknown>> {
  const reader = request.body?.getReader();
  const chunks: Uint8Array[] = [];
  let size = 0;
  if (reader) {
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        size += value.byteLength;
        if (size > MAX_BODY_BYTES) {
          await reader.cancel();
          throw new RangeError("Request too large");
        }
        chunks.push(value);
      }
    } finally {
      reader.releaseLock();
    }
  }
  const bytes = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length; }
  const parsed: unknown = JSON.parse(new TextDecoder().decode(bytes));
  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) throw new Error("Invalid JSON object");
  return parsed as Record<string, unknown>;
}

export function createTrialHandlers(program: TrialProgram) {
  const programme = PROGRAMMES[program];
  const name = program.toUpperCase();
  const dashboardUrl = `https://apps.thrivingscholars.com${programme.dashboard}`;
  const redirectUrl = `https://apps.thrivingscholars.com/auth/callback?next=${encodeURIComponent(programme.dashboard)}`;

  async function OPTIONS(request: Request) {
    const origin = allowedOrigin(request);
    return origin ? new Response(null, { status: 204, headers: responseHeaders(origin) })
      : json(null, { ok: false, message: "Origin not allowed." }, 403);
  }

  async function POST(request: Request) {
    const origin = allowedOrigin(request);
    if (!origin) return json(null, { ok: false, message: "Origin not allowed." }, 403);
    if (!(request.headers.get("content-type") || "").toLowerCase().startsWith("application/json")) {
      return json(origin, { ok: false, message: "Send the request as JSON." }, 415);
    }
    if (Number(request.headers.get("content-length") || "0") > MAX_BODY_BYTES) {
      return json(origin, { ok: false, message: "The request is too large." }, 413);
    }
    let body: Record<string, unknown>;
    try { body = await readBody(request); } catch (error) {
      return json(origin, { ok: false, message: error instanceof RangeError
        ? "The request is too large." : "The request is not valid JSON." }, error instanceof RangeError ? 413 : 400);
    }
    const email = typeof body.email === "string" ? body.email.trim().toLowerCase() : "";
    const rawName = typeof body.student_name === "string" ? body.student_name : "";
    const studentName = rawName.trim().replace(/\s+/g, " ");
    if (!email || email.length > 254 || !EMAIL_PATTERN.test(email)) {
      return json(origin, { ok: false, message: "Please enter a valid email address." }, 400);
    }
    if (studentName.length > 120 || /[\u0000-\u001f\u007f]/.test(rawName)) {
      return json(origin, { ok: false, message: "Please enter a shorter student name." }, 400);
    }
    if (body.program !== undefined && body.program !== program) {
      return json(origin, { ok: false, message: `This form is for the ${name} trial.` }, 400);
    }

    try {
      const { admin, auth } = trialClients();
      // The existing TWO-argument functions own expiry and paid-access preservation.
      // Never use the legacy one-argument TMUA grant or write student_access here.
      const grant = () => admin.rpc(programme.grant, {
        p_email: email, p_student_name: studentName || null,
      }).retry(false);
      let grantResponse = await grant();
      // A simultaneous first signup can lose the unique-email insert. Re-read via
      // the same idempotent RPC once; never reset or extend a previous trial.
      if (grantResponse.error?.code === "23505") grantResponse = await grant();
      if (grantResponse.error) {
        console.error(`${name} trial grant failed`, { code: grantResponse.error.code });
        return json(origin, { ok: false, message: "Could not start the free trial. Please try again." }, 500);
      }
      const result = ((grantResponse.data as TrialResult[] | null)?.[0] || {}) as TrialResult;
      const status = result.out_status;
      if (status === "invalid_email") {
        return json(origin, { ok: false, message: "Please enter a valid email address." }, 400);
      }
      if (status === "trial_already_used") {
        return json(origin, { ok: false, status,
          message: "This email has already used its free trial. Contact Thriving Scholars if you need help with access." }, 409);
      }
      if ((status !== "trial_started" && status !== "trial_already_active") ||
        !result.out_expires_at || !Number.isFinite(Date.parse(result.out_expires_at))) {
        return json(origin, { ok: false, message: "Could not confirm the free trial. Please try again." }, 500);
      }
      const active = { ok: true, status, expires_at: result.out_expires_at, dashboard_url: dashboardUrl };
      const now = new Date();
      // Existing trial metadata supplies a distributed, atomic resend claim.
      // A new grant has updated_at = started_at (both DB now()). Later requests
      // must wait five minutes. Metadata-only: expiry and entitlements are untouched.
      // Other legitimate metadata updates may conservatively prolong the cooldown.
      let claim = admin.from(programme.table).update({ updated_at: now.toISOString() })
        .eq("email", email).eq("status", "active").gt("expires_at", now.toISOString());
      if (status === "trial_started") {
        if (!result.out_started_at) throw new Error("Missing trial activation timestamp");
        claim = claim.eq("updated_at", result.out_started_at);
      } else {
        claim = claim.lt("updated_at", new Date(now.getTime() - EMAIL_COOLDOWN_SECONDS * 1_000).toISOString());
      }
      const claimed = await claim.select("id").retry(false);
      if (claimed.error) {
        console.error(`${name} trial email claim failed`, { code: claimed.error.code });
        return json(origin, { ...active, login_email_sent: false, welcome_email_sent: false,
          message: `Your two-day ${name} trial is active, but we could not send the emails right now. Open the dashboard and request a sign-in link using the same email address.` });
      }
      if (!claimed.data?.length) {
        return json(origin, { ...active, login_email_sent: false, welcome_email_sent: false,
          email_resend_limited: true, retry_after_seconds: EMAIL_COOLDOWN_SECONDS,
          message: `Your ${name} trial is already active. We have not sent another email. Check your inbox and spam folder, or open the dashboard to sign in. Please wait five minutes before requesting another trial email.` });
      }
      if (claimed.data.length !== 1) throw new Error("Unexpected trial email claim count");

      let loginEmailSent = false;
      try {
        const { error } = await auth.auth.signInWithOtp({
          email, options: { emailRedirectTo: redirectUrl, shouldCreateUser: true },
        });
        loginEmailSent = !error;
        if (error) console.error(`${name} trial login email failed`, { code: error.code });
      } catch { console.error(`${name} trial login email unavailable`); }
      if (loginEmailSent) {
        try {
          const marked = await admin.rpc(programme.marker, { p_email: email }).retry(false);
          if (marked.error) console.error(`${name} trial email marker failed`, { code: marked.error.code });
        } catch { console.error(`${name} trial email marker unavailable`); }
      }
      const welcomeEmail = await sendTrialWelcomeEmail({
        program, studentName, studentEmail: email, expiresAt: result.out_expires_at,
      });
      return json(origin, { ...active, login_email_sent: loginEmailSent, welcome_email_sent: welcomeEmail.ok,
        message: loginEmailSent && welcomeEmail.ok
          ? `Your two-day ${name} trial is active. We emailed your secure sign-in link and trial guide.`
          : loginEmailSent ? `Your two-day ${name} trial is active. We emailed you a secure sign-in link.`
          : welcomeEmail.ok ? `Your two-day ${name} trial is active. We emailed your trial guide. Open the dashboard and request a sign-in link using the same email address.`
          : `Your two-day ${name} trial is active. Open the dashboard and request a sign-in link using the same email address.`,
      });
    } catch {
      console.error(`${name} free-trial endpoint unavailable`);
      return json(origin, { ok: false, message: "Could not start the free trial. Please try again." }, 500);
    }
  }
  return { OPTIONS, POST };
}
