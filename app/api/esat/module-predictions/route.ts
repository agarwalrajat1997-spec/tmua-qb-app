import { adminClient, json } from "@/app/api/esat/qb/_server";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { isMissingSession, withServiceTimeout } from "@/lib/auth/service-recovery";
import { getEsatModuleOverview } from "@/lib/server/esat-module-prediction-service";

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

export async function GET() {
  try {
    const auth = await authorised();
    if (auth.response) return auth.response;
    return json(await getEsatModuleOverview(auth.admin!, auth.user!.id));
  } catch (error) { return failure(error); }
}
