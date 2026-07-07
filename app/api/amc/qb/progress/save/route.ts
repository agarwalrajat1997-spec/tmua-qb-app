import { NextResponse } from "next/server";
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

type QBUpdate =
  | {
      question_id: string;
      status?: string | null;
      selected_answer?: string | null;
      flagged?: boolean | null;
      time_spent?: number | null;
      last_seen_at?: string | null;
    }
  | { key: string; value: any }; // compatibility: value should be an object with fields above

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

function toIsoOrNull(x: any): string | null {
  if (!x) return null;
  const s = String(x);
  const d = new Date(s);
  if (Number.isNaN(d.getTime())) return null;
  return d.toISOString();
}

export async function POST(req: Request) {
  try {
    const supabase = await supabaseServer();

    const { data: auth, error: authErr } = await supabase.auth.getUser();
    if (authErr || !auth?.user) return jsonErr(401, "Not authenticated");

    const body = await req.json().catch(() => null);
    const updates = body?.updates as QBUpdate[] | undefined;

    const email = String(auth.user.email || "").toLowerCase();

    if (!Array.isArray(updates) || updates.length === 0) {
      return jsonErr(400, "updates is required");
    }

    // Build upsert rows
    const nowIso = new Date().toISOString();
    const rows: any[] = [];

    for (const u of updates) {
      // Compatibility path: { key, value }
      if ((u as any)?.key && typeof (u as any)?.key === "string") {
        const qid = String((u as any).key || "").trim();
        const v = (u as any).value;
        if (!qid) continue;
        if (!v || typeof v !== "object") continue; // can't store a string blob in this schema

        rows.push({
          user_id: auth.user.id,
          email,
          product: "amc-question-bank",
          question_id: qid,
          status: v.status ?? null,
          selected_answer: v.selected_answer ?? v.selectedAnswer ?? null,
          flagged: typeof v.flagged === "boolean" ? v.flagged : null,
          time_spent: Number.isFinite(Number(v.time_spent)) ? Number(v.time_spent) : (Number.isFinite(Number(v.timeSpent)) ? Number(v.timeSpent) : null),
          last_seen_at: toIsoOrNull(v.last_seen_at ?? v.lastSeenAt) ?? null,
          updated_at: nowIso,
        });
        continue;
      }

      // Normal path: { question_id, ... }
      const qid = String((u as any).question_id || "").trim();
      if (!qid) continue;

      rows.push({
        user_id: auth.user.id,
          email,
        product: "amc-question-bank",
        question_id: qid,
        status: (u as any).status ?? null,
        selected_answer: (u as any).selected_answer ?? null,
        flagged: typeof (u as any).flagged === "boolean" ? (u as any).flagged : null,
        time_spent: Number.isFinite(Number((u as any).time_spent)) ? Number((u as any).time_spent) : null,
        last_seen_at: toIsoOrNull((u as any).last_seen_at) ?? null,
        updated_at: nowIso,
      });
    }

    if (rows.length === 0) {
      return jsonErr(400, "No valid updates (missing question_id or value object)");
    }

    const { error } = await supabase
      .from("amc_qb_progress")
      .upsert(rows, { onConflict: "user_id,product,question_id" });

    if (error) {
      return jsonErr(500, "Supabase upsert failed", { message: error.message });
    }

    return NextResponse.json({ ok: true, saved: rows.length });
  } catch (e: any) {
    return NextResponse.json(
      { error: "Unhandled error in /api/qb/progress/save", message: String(e?.message || e), stack: String(e?.stack || "") },
      { status: 500 }
    );
  }
}


