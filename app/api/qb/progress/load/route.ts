import { NextResponse } from "next/server";
/* eslint-disable @typescript-eslint/no-explicit-any */
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import { isMissingSession, serviceFetch, withServiceTimeout } from "@/lib/auth/service-recovery";

async function supabaseServer() {
  const cookieStore = await cookies();
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL!;
  const key =
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!;
  return createServerClient(url, key, {
    global: { fetch: serviceFetch },
    cookies: {
      get(name: string) {
        return cookieStore.get(name)?.value;
      },
      set(name: string, value: string, options: any) {
        cookieStore.set({ name, value, ...options });
      },
      remove(name: string, options: any) {
        cookieStore.set({ name, value: "", ...options });
      },
    },
  });
}

function jsonErr(status: number, error: string, extra?: any) {
  return NextResponse.json({ error, ...(extra ? { extra } : {}) }, { status, headers: { "Cache-Control": "no-store", ...(status === 503 ? { "Retry-After": "30" } : {}) } });
}

export async function GET(req: Request) {
  try {
    const supabase = await supabaseServer();

    const { data: auth, error: authErr } = await withServiceTimeout(supabase.auth.getUser());
    if (authErr && !isMissingSession(authErr)) return jsonErr(503, "Progress service temporarily unavailable");
    if (authErr || !auth?.user) return jsonErr(401, "Not authenticated");

    const url = new URL(req.url);
    const requestedProduct = String(url.searchParams.get("product") || "tmua-question-bank");

    const allowedProducts = new Set([
      "tmua-question-bank",
      "esat-question-bank"
    ]);

    const product = allowedProducts.has(requestedProduct)
      ? requestedProduct
      : "tmua-question-bank";

    // PostgREST defaults to 1,000 rows. Always page so students with a larger
    // history do not see their remaining completed questions become incomplete.
    const data: any[] = [];
    const pageSize = 1000;
    const maxRows = 20_000;
    for (let from = 0; ; from += pageSize) {
      if (from >= maxRows) return jsonErr(503, "Progress history temporarily unavailable");
      const { data: page, error } = await supabase
        .from("qb_progress")
        .select("question_id,status,selected_answer,flagged,time_spent,last_seen_at,updated_at,email,submission_id,answer_elapsed_seconds,answer_submitted_at")
        .eq("user_id", auth.user.id)
        .eq("product", product)
        .order("question_id", { ascending: true })
        .range(from, from + pageSize - 1)
        .retry(false);
      if (error) return jsonErr(503, "Progress service temporarily unavailable");
      data.push(...(page || []));
      if (!page || page.length < pageSize) break;
    }

    const progress: Record<string, any> = {};
    for (const row of data || []) {
      progress[row.question_id] = {
        status: row.status,
        selected_answer: row.selected_answer,
        flagged: row.flagged,
        time_spent: row.time_spent,
        last_seen_at: row.last_seen_at,
        updated_at: row.updated_at,
        submission_id: row.submission_id,
        answer_elapsed_seconds: row.answer_elapsed_seconds,
        answer_submitted_at: row.answer_submitted_at,
      };
    }

    return NextResponse.json({ ok: true, user_id: auth.user.id, product, progress },
      { headers: { "Cache-Control": "no-store" } });
  } catch (e: any) {
    console.error("Question-bank progress load unavailable", e);
    return jsonErr(503, "Progress service temporarily unavailable");
  }
}

