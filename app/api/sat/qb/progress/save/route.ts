import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import { NextResponse } from "next/server";

type ProgressValue = {
  status?: unknown;
  selected_answer?: unknown;
  selectedAnswer?: unknown;
  flagged?: unknown;
  time_spent?: unknown;
  timeSpent?: unknown;
  last_seen_at?: unknown;
  lastSeenAt?: unknown;
};

type NormalUpdate = ProgressValue & { question_id: unknown };
type CompatibilityUpdate = { key: unknown; value: unknown };
type ProgressRow = {
  user_id: string;
  product: "sat-question-bank";
  question_id: string;
  status?: string | null;
  selected_answer?: string | null;
  flagged?: boolean;
  time_spent?: number;
  last_seen_at: string;
  updated_at: string;
};

async function supabaseServer() {
  const cookieStore = await cookies();
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL!;
  const key =
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!;

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

function isRecord(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === "object" && !Array.isArray(value);
}

function nullableString(value: unknown): string | null {
  if (value === null || value === undefined || value === "") return null;
  return String(value).slice(0, 100);
}

function nullableNumber(value: unknown): number | null {
  if (value === null || value === undefined || value === "") return null;
  const number = Number(value);
  return Number.isFinite(number) ? Math.max(0, Math.round(number)) : null;
}

function toIsoOrNull(value: unknown): string | null {
  if (!value) return null;
  const date = new Date(String(value));
  return Number.isNaN(date.getTime()) ? null : date.toISOString();
}

function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : String(error);
}

function normaliseUpdate(
  update: NormalUpdate | CompatibilityUpdate,
  userId: string,
  nowIso: string
): ProgressRow | null {
  let qid = "";
  let value: ProgressValue;

  if ("key" in update) {
    qid = String(update.key || "").trim();
    if (!isRecord(update.value)) return null;
    value = update.value;
  } else {
    qid = String(update.question_id || "").trim();
    value = update;
  }

  if (!qid) return null;

  const selected = value.selected_answer ?? value.selectedAnswer;
  const timeSpent = value.time_spent ?? value.timeSpent;
  const lastSeen = value.last_seen_at ?? value.lastSeenAt;

  const row: ProgressRow = {
    user_id: userId,
    product: "sat-question-bank",
    question_id: qid,
    last_seen_at: toIsoOrNull(lastSeen) || nowIso,
    updated_at: nowIso,
  };

  if (value.status !== undefined) row.status = nullableString(value.status);
  if (selected !== undefined) row.selected_answer = nullableString(selected);
  if (typeof value.flagged === "boolean") row.flagged = value.flagged;
  const seconds = nullableNumber(timeSpent);
  if (seconds !== null) row.time_spent = seconds;

  return row;
}

export async function POST(req: Request) {
  try {
    const supabase = await supabaseServer();
    const { data: auth, error: authError } = await supabase.auth.getUser();

    if (authError || !auth?.user) return jsonErr(401, "Not authenticated");

    const body: unknown = await req.json().catch(() => null);
    const rawUpdates = isRecord(body) ? body.updates : null;

    if (!Array.isArray(rawUpdates) || rawUpdates.length === 0) {
      return jsonErr(400, "updates is required");
    }

    const nowIso = new Date().toISOString();
    const rows = rawUpdates
      .filter(isRecord)
      .map((update) =>
        normaliseUpdate(
          update as NormalUpdate | CompatibilityUpdate,
          auth.user.id,
          nowIso
        )
      )
      .filter((row): row is ProgressRow => row !== null);

    if (rows.length === 0) {
      return jsonErr(400, "No valid updates (missing question_id or value object)");
    }

    const { error } = await supabase
      .from("sat_qb_progress")
      .upsert(rows, {
        onConflict: "user_id,product,question_id",
        defaultToNull: false,
      });

    if (error) {
      return jsonErr(500, "Supabase upsert failed", { message: error.message });
    }

    return NextResponse.json({ ok: true, saved: rows.length });
  } catch (error: unknown) {
    return NextResponse.json(
      {
        error: "Unhandled error in /api/sat/qb/progress/save",
        message: errorMessage(error),
      },
      { status: 500 }
    );
  }
}
