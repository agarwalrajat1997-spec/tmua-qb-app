import { NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { GOOD_LUCK_CAMPAIGN_KEY } from "@/lib/good-luck-popup";
import { isMissingSession } from "@/lib/auth/service-recovery";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function response(show: boolean, status = 200, dismissed = false) {
  return NextResponse.json({ show, dismissed }, { status, headers: { "Cache-Control": "private, no-store" } });
}

export async function GET() {
  try {
    const supabase = await createSupabaseServerClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError) return response(false, isMissingSession(authError) ? 401 : 503);
    if (!user) return response(false, 401);

    // Reading eligibility must not dismiss the popup. It remains eligible after
    // refresh, navigation or another day until the student explicitly closes it.
    const { data, error } = await supabase
      .from("student_popup_receipts")
      .select("campaign_key")
      .eq("user_id", user.id)
      .eq("campaign_key", GOOD_LUCK_CAMPAIGN_KEY)
      .maybeSingle();
    if (error) return response(false, 503);
    return response(!data, 200, !!data);
  } catch {
    return response(false, 503);
  }
}

export async function POST(request: Request) {
  // A cross-site request must not dismiss someone else's message.
  // Next may construct request.url with an internal hostname behind a proxy.
  // Compare against the incoming Host, which browsers cannot override, rather
  // than that internal URL; still require a well-formed HTTP(S) Origin.
  const origin = request.headers.get("origin");
  let sameOrigin = false;
  try {
    const parsed = new URL(origin || "");
    const host = request.headers.get("host") || new URL(request.url).host;
    sameOrigin = (parsed.protocol === "https:" || parsed.protocol === "http:") &&
      parsed.origin === origin && parsed.host.toLowerCase() === host.toLowerCase();
  } catch {
    // Missing or malformed origins are not browser-initiated portal requests.
  }
  if (!sameOrigin) {
    return response(false, 403);
  }

  // Old deployed clients POSTed on display with no body. Never let those
  // requests create a dismissal after the change in behaviour.
  const body = await request.json().catch(() => null);
  if (body?.action !== "dismiss") return response(false, 400);

  try {
    const supabase = await createSupabaseServerClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError) return response(false, isMissingSession(authError) ? 401 : 503);
    if (!user) return response(false, 401);

    // Save only on explicit close. The unique key makes repeated/concurrent
    // dismissals idempotent and permanent across portals and devices.
    // Never trust a user ID sent from the browser.
    const { error } = await supabase
      .from("student_popup_receipts")
      .upsert(
        { user_id: user.id, campaign_key: GOOD_LUCK_CAMPAIGN_KEY },
        { onConflict: "user_id,campaign_key", ignoreDuplicates: true },
      );

    if (error) {
      console.error("Good-luck popup receipt could not be saved", error.code);
      return response(false, 503);
    }
    return response(false, 200, true);
  } catch {
    // An optional message must never stop a student reaching their dashboard.
    return response(false, 503);
  }
}
