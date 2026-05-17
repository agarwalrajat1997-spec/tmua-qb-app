import { NextRequest, NextResponse } from "next/server";
import { supabaseServer } from "@/utils/supabase/server"; export const runtime = "nodejs"; export async function GET(req: NextRequest) { const supabase = await supabaseServer(); try { await supabase.auth.signOut(); } catch {} return NextResponse.redirect(new URL("/login?loggedout=1", req.url));
}