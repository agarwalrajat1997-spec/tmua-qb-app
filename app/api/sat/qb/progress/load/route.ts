import { NextResponse } from "next/server";
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

async function supabaseServer() {
  const cookieStore = await cookies();
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL!;
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
  return createServerClient(url, key, {
    cookies: {
      getAll() {
        return cookieStore.getAll();
      },
      setAll(cookiesToSet) {
        cookiesToSet.forEach(({ name, value, options }) => {
          cookieStore.set({ name, value, ...options });
        });
      },
    },
  });
}

function jsonErr(status: number, error: string, extra?: unknown) {
  return NextResponse.json({ error, ...(extra ? { extra } : {}) }, { status });
}

type ProgressRecord = {
  status: string | null;
  selected_answer: string | null;
  flagged: boolean;
  time_spent: number;
  last_seen_at: string;
  updated_at: string;
};

function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : String(error);
}

export async function GET() {
  try {
    const supabase = await supabaseServer();

    const { data: auth, error: authErr } = await supabase.auth.getUser();
    if (authErr || !auth?.user) return jsonErr(401, "Not authenticated");

    const { data, error } = await supabase
      .from("sat_qb_progress")
      .select("question_id,status,selected_answer,flagged,time_spent,last_seen_at,updated_at")
      .eq("user_id", auth.user.id)
      .eq("product", "sat-question-bank");

    if (error) {
      return jsonErr(500, "Supabase load failed", { message: error.message });
    }

    const progress: Record<string, ProgressRecord> = {};
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

    return NextResponse.json({ ok: true, product: "sat-question-bank", progress });
  } catch (error: unknown) {
    return NextResponse.json(
      {
        error: "Unhandled error in /api/sat/qb/progress/load",
        message: errorMessage(error),
      },
      { status: 500 }
    );
  }
}
