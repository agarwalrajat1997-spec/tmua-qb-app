import { NextResponse } from "next/server";
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

async function supabaseServer() {
  const cookieStore = await cookies();
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL!;
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
  return createServerClient(url, key, {
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
  return NextResponse.json({ error, ...(extra ? { extra } : {}) }, { status });
}

export async function GET(req: Request) {
  try {
    const supabase = await supabaseServer();

    const { data: auth, error: authErr } = await supabase.auth.getUser();
    if (authErr || !auth?.user) return jsonErr(401, "Not authenticated");

    const { data, error } = await supabase
      .from("qb_progress")
      .select("question_id,status,selected_answer,flagged,time_spent,last_seen_at,updated_at")
      .eq("user_id", auth.user.id)
      .eq("product", "tmua-question-bank");

    if (error) {
      return jsonErr(500, "Supabase load failed", { message: error.message });
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
      };
    }

    return NextResponse.json({ ok: true, product: "tmua-question-bank", progress });
  } catch (e: any) {
    return NextResponse.json(
      { error: "Unhandled error in /api/qb/progress/load", message: String(e?.message || e), stack: String(e?.stack || "") },
      { status: 500 }
    );
  }
}
