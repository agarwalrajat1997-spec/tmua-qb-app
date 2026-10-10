import { NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { GOOD_LUCK_CAMPAIGN_KEY, isGoodLuckCampaignActive } from "@/lib/good-luck-popup";
import { isMissingSession } from "@/lib/auth/service-recovery";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function response(show: boolean, status = 200) {
  return NextResponse.json({ show }, { status, headers: { "Cache-Control": "private, no-store" } });
}

export async function POST(request: Request) {
  // A cross-site request must not consume someone else's one-time message.
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
  if (!isGoodLuckCampaignActive()) return response(false);

  try {
    const supabase = await createSupabaseServerClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError) return response(false, isMissingSession(authError) ? 401 : 503);
    if (!user) return response(false, 401);

    // INSERT ... ON CONFLICT DO NOTHING is an atomic, account-wide claim.
    // Only the winning request gets a row back. Save BEFORE showing the UI so
    // closing offline, refreshing, concurrent tabs and another device cannot
    // resurrect the popup. Never trust a user ID sent from the browser.
    const { data, error } = await supabase
      .from("student_popup_receipts")
      .upsert(
        { user_id: user.id, campaign_key: GOOD_LUCK_CAMPAIGN_KEY },
        { onConflict: "user_id,campaign_key", ignoreDuplicates: true },
      )
      .select("campaign_key");

    if (error) {
      console.error("Good-luck popup receipt could not be saved", error.code);
      return response(false, 503);
    }
    return response(data?.length === 1);
  } catch {
    // An optional message must never stop a student reaching their dashboard.
    return response(false, 503);
  }
}
