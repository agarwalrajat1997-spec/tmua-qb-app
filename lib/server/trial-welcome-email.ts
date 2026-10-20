const EMAILJS_SEND_URL = "https://api.emailjs.com/api/v1.0/email/send";
const DEFAULT_EMAILJS_SERVICE_ID = "service_5l4w8x2";
const DEFAULT_EMAILJS_TEMPLATE_ID = "template_whjida8";
const DEFAULT_EMAILJS_PUBLIC_KEY = "9jjn3yBHl6S88hITy";
const WORKSPACE_IMAGE =
  "https://assets.thrivingscholars.com/images/tmua/ada627ec-3463-4939-9614-054780611760.png";

export type TrialProgram = "tmua" | "esat";
type TrialWelcomeEmailInput = {
  program: TrialProgram;
  studentName: string;
  studentEmail: string;
  expiresAt: string | null;
};
const PROGRAM_DETAILS = {
  tmua: {
    examName: "TMUA", portalLabel: "TMUA Dashboard",
    loginUrl: "https://apps.thrivingscholars.com/dashboard",
    programmeUrl: "https://www.thrivingscholars.com/tmua",
    featureOne: "TMUA Question Bank", featureTwo: "TMUA Practice Tests",
    featureThree: "Worked solutions and progress tools",
  },
  esat: {
    examName: "ESAT", portalLabel: "ESAT Prep Portal",
    loginUrl: "https://apps.thrivingscholars.com/esat",
    programmeUrl: "https://www.thrivingscholars.com/esat",
    featureOne: "ESAT Question Bank", featureTwo: "ESAT Classes",
    featureThree: "Worked solutions and learning resources",
  },
} as const;

function expiryLabel(expiresAt: string | null) {
  const expiry = expiresAt ? new Date(expiresAt) : null;
  if (!expiry || Number.isNaN(expiry.getTime())) return "2 days after activation";
  return new Intl.DateTimeFormat("en-GB", {
    day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit",
    hourCycle: "h23", timeZone: "UTC", timeZoneName: "short",
  }).format(expiry);
}

export function trialEmailTemplateParams(input: TrialWelcomeEmailInput) {
  const programme = PROGRAM_DETAILS[input.program];
  return {
    to_email: input.studentEmail, student_name: input.studentName || "Student",
    student_email: input.studentEmail, exam_name: programme.examName,
    portal_label: programme.portalLabel, login_url: programme.loginUrl,
    programme_url: programme.programmeUrl, workspace_image: WORKSPACE_IMAGE,
    access_duration: "2 days", expires_at: expiryLabel(input.expiresAt),
    feature_one: programme.featureOne, feature_two: programme.featureTwo,
    feature_three: programme.featureThree, current_year: String(new Date().getUTCFullYear()),
  };
}

export async function sendTrialWelcomeEmail(input: TrialWelcomeEmailInput) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 8_000);
  try {
    const payload: Record<string, unknown> = {
      service_id: process.env.EMAILJS_TRIAL_SERVICE_ID || DEFAULT_EMAILJS_SERVICE_ID,
      template_id: process.env.EMAILJS_TRIAL_TEMPLATE_ID || DEFAULT_EMAILJS_TEMPLATE_ID,
      user_id: process.env.EMAILJS_PUBLIC_KEY || DEFAULT_EMAILJS_PUBLIC_KEY,
      template_params: trialEmailTemplateParams(input),
    };
    if (process.env.EMAILJS_PRIVATE_KEY) payload.accessToken = process.env.EMAILJS_PRIVATE_KEY;
    const response = await fetch(EMAILJS_SEND_URL, {
      method: "POST", headers: { "Content-Type": "application/json", Origin: "https://www.thrivingscholars.com" },
      body: JSON.stringify(payload), cache: "no-store", signal: controller.signal,
    });
    if (!response.ok) {
      // Provider bodies may echo applicants' data. Log status only.
      console.error("Trial welcome email failed", { status: response.status });
      return { ok: false } as const;
    }
    return { ok: true } as const;
  } catch (error) {
    console.error("Trial welcome email failed", { reason: error instanceof Error ? error.name : "Unknown error" });
    return { ok: false } as const;
  } finally { clearTimeout(timeout); }
}
