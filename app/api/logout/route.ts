import { NextRequest, NextResponse } from "next/server";
import { supabaseServer } from "@/utils/supabase/server";

export const runtime = "nodejs";

function logoutDestination(req: NextRequest) {
  const referer = req.headers.get("referer");

  if (referer) {
    try {
      const pathname = new URL(referer).pathname;

      if (pathname === "/amc" || pathname.startsWith("/amc/")) {
        return "/amc-login?loggedout=1";
      }

      if (pathname === "/sat" || pathname.startsWith("/sat/")) {
        return "/sat-login?loggedout=1";
      }
    } catch {
      // Ignore an invalid Referer and preserve the existing TMUA destination.
    }
  }

  return "/login?loggedout=1";
}

export async function GET(req: NextRequest) {
  const supabase = await supabaseServer();

  try {
    await supabase.auth.signOut();
  } catch {}

  return NextResponse.redirect(new URL(logoutDestination(req), req.url));
}
