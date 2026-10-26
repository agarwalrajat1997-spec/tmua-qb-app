import { adminClient, json } from "@/app/api/esat/qb/_server";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { isMissingSession, withServiceTimeout } from "@/lib/auth/service-recovery";
import { assessEsatResults, esatLockAt, validateEsatModules } from "@/lib/esat-predictions";
import { getEsatModuleOverview, readEsatPredictionPlan } from "@/lib/server/esat-module-prediction-service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 60;

async function authorised() {
  const session = await createSupabaseServerClient();
  const { data: { user }, error } = await withServiceTimeout(session.auth.getUser());
  if (error && !isMissingSession(error)) throw error;
  if (!user?.id || !user.email) return { response: json({ ok: false, error: "Sign in to see your ESAT predictions." }, 401) };
  const admin = adminClient();
  const email = user.email.trim().toLowerCase().replace(/[\\%_]/g, "\\$&");
  const access = await admin.from("student_access").select("product")
    .ilike("email", email).in("product", ["esat-practice-tests", "esat-question-bank", "esat-classes"])
    .eq("approved", true).or(`expires_at.is.null,expires_at.gt.${new Date().toISOString()}`).limit(1).retry(false);
  if (access.error) throw access.error;
  if (!access.data?.length) return { response: json({ ok: false, error: "ESAT access is required." }, 403) };
  return { admin, user };
}

function failure(error: unknown) {
  const code = (error as { code?: string })?.code;
  if (code === "P0001" || code === "22023") return json({ ok: false, error: (error as { message: string }).message }, 409);
  console.error("ESAT module predictions unavailable", error);
  return json({ ok: false, error: "Your module predictions are temporarily unavailable. Please try again.", retryable: true }, 503);
}

function sameOrigin(request: Request) {
  const origin = request.headers.get("origin");
  return !origin || origin === new URL(request.url).origin;
}

export async function GET() {
  try {
    const auth = await authorised();
    if (auth.response) return auth.response;
    return json(await getEsatModuleOverview(auth.admin!, auth.user!.id));
  } catch (error) { return failure(error); }
}

export async function PUT(request: Request) {
  if (!sameOrigin(request)) return json({ ok: false, error: "Invalid request origin." }, 403);
  try {
    const auth = await authorised();
    if (auth.response) return auth.response;
    let body;
    try { body = await request.json(); } catch { return json({ ok: false, error: "Invalid request." }, 400); }
    let modules;
    try {
      modules = validateEsatModules(body.modules);
      if (typeof body.examDate !== "string" || Date.parse(esatLockAt(body.examDate)) <= Date.now()) {
        throw new Error("Save your booked exam date before its prediction lock date, two days before the exam.");
      }
    } catch (error) { return json({ ok: false, error: (error as Error).message }, 400); }
    const result = await auth.admin!.rpc("esat_save_exam_plan", { p_user_id: auth.user!.id, p_exam_date: body.examDate, p_modules: modules });
    if (result.error) throw result.error;
    return json(await getEsatModuleOverview(auth.admin!, auth.user!.id));
  } catch (error) { return failure(error); }
}

export async function POST(request: Request) {
  if (!sameOrigin(request)) return json({ ok: false, error: "Invalid request origin." }, 403);
  try {
    const auth = await authorised();
    if (auth.response) return auth.response;
    const { plan, lock } = await readEsatPredictionPlan(auth.admin!, auth.user!.id);
    const today = new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/London" }).format(new Date());
    if (!plan || !lock || today < plan.exam_date) return json({ ok: false, error: "You can record official results after your booked exam date." }, 409);
    let actual, assessment;
    try {
      const body = await request.json();
      if (!body.actualScores || typeof body.actualScores !== "object" || Array.isArray(body.actualScores)) throw new Error("Enter all three official module scores.");
      assessment = assessEsatResults(lock.predictions, body.actualScores);
      actual = Object.fromEntries(assessment.modules.map(module => [module.module, module.actual]));
    } catch (error) { return json({ ok: false, error: (error as Error).message }, 400); }
    const saved = await auth.admin!.from("esat_result_submissions").upsert({
      user_id: auth.user!.id, exam_date: plan.exam_date, actual_scores: actual, assessment,
      submitted_at: new Date().toISOString(), verification_status: "pending",
    }, { onConflict: "user_id,exam_date" }).retry(false);
    if (saved.error) throw saved.error;
    return json(await getEsatModuleOverview(auth.admin!, auth.user!.id));
  } catch (error) { return failure(error); }
}
