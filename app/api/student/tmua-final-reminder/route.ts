import { NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { isMissingSession } from "@/lib/auth/service-recovery";
import { isTmuaFinalReminderActive, TMUA_FINAL_REMINDER_CAMPAIGN_KEY } from "@/lib/tmua-final-reminder";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function response(show: boolean, status = 200, dismissed = false, authenticated = false) {
  const active = isTmuaFinalReminderActive();
  return NextResponse.json(
    { show: active && show, dismissed, active, authenticated },
    { status, headers: { "Cache-Control": "private, no-store" } },
  );
}

export async function GET() {
  // The server clock is authoritative. Expired campaigns do not make any auth
  // or database requests, and an in-flight check cannot revive an expired popup.
  if (!isTmuaFinalReminderActive()) return response(false);
  try {
    const supabase = await createSupabaseServerClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError) return response(false, isMissingSession(authError) ? 401 : 503);
    if (!user) return response(false, 401);

    // Merely displaying the reminder or opening its PDF must not dismiss it.
    const { data, error } = await supabase
      .from("student_popup_receipts")
      .select("campaign_key")
      .eq("user_id", user.id)
      .eq("campaign_key", TMUA_FINAL_REMINDER_CAMPAIGN_KEY)
      .maybeSingle();
    if (error) return response(false, 503, false, true);
    return response(!data, 200, !!data, true);
  } catch {
    return response(false, 503);
  }
}

export async function POST(request: Request) {
  // Use the incoming Host rather than request.url, which may use an internal
  // hostname behind Vercel's proxy. Browser requests cannot override Host.
  const origin = request.headers.get("origin");
  let sameOrigin = false;
  try {
    const parsed = new URL(origin || "");
    const host = request.headers.get("host") || new URL(request.url).host;
    sameOrigin = (parsed.protocol === "https:" || parsed.protocol === "http:") &&
      parsed.origin === origin && parsed.host.toLowerCase() === host.toLowerCase();
  } catch {
    // Missing, opaque and malformed Origin headers are not valid dismissals.
  }
  if (!sameOrigin) return response(false, 403);

  const body = await request.json().catch(() => null);
  if (body?.action !== "dismiss") return response(false, 400);
  if (!isTmuaFinalReminderActive()) return response(false);

  try {
    const supabase = await createSupabaseServerClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError) return response(false, isMissingSession(authError) ? 401 : 503);
    if (!user) return response(false, 401);
    if (!isTmuaFinalReminderActive()) return response(false, 200, false, true);

    // This campaign has its own receipt. Never trust an identity supplied by
    // the browser and never overwrite a receipt for an earlier campaign.
    const { error } = await supabase
      .from("student_popup_receipts")
      .upsert(
        { user_id: user.id, campaign_key: TMUA_FINAL_REMINDER_CAMPAIGN_KEY },
        { onConflict: "user_id,campaign_key", ignoreDuplicates: true },
      );
    if (error) {
      console.error("TMUA final reminder dismissal could not be saved", error.code);
      return response(false, 503, false, true);
    }
    return response(false, 200, true, true);
  } catch {
    return response(false, 503);
  }
}
