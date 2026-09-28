import { createClient } from "@supabase/supabase-js";
import { supabaseServer } from "@/utils/supabase/server";
import { isMissingSession, serviceFetch, withServiceTimeout } from "@/lib/auth/service-recovery";

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY!;

export function json(data: unknown, status = 200) {
  return Response.json(data, {
    status,
    headers: {
      "Cache-Control": "no-store, no-cache, must-revalidate",
      ...(status === 503 ? { "Retry-After": "30" } : {}),
    },
  });
}

export function adminClient() {
  return createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
    global: { fetch: serviceFetch },
    auth: {
      persistSession: false,
      autoRefreshToken: false,
    },
  });
}

export async function requireESATAccess() {
  try {
    return await checkESATAccess();
  } catch (error) {
    console.error("ESAT access service unavailable", error);
    return {
      ok: false as const,
      response: json({ ok: false, error: "Access service temporarily unavailable" }, 503),
    };
  }
}

async function checkESATAccess() {
  const supabase = await supabaseServer();

  const {
    data: { user }, error: authError,
  } = await withServiceTimeout(supabase.auth.getUser());
  if (authError && !isMissingSession(authError)) {
    throw new Error("Authentication service temporarily unavailable");
  }

  if (!user || !user.email) {
    return {
      ok: false as const,
      response: json({ ok: false, error: "Not signed in" }, 401),
    };
  }

  const email = user.email.toLowerCase();
  const nowIso = new Date().toISOString();

  const { data, error } = await supabase
    .from("student_access")
    .select("email, product, approved, expires_at")
    .ilike("email", email)
    .eq("product", "esat-question-bank")
    .eq("approved", true)
    .or(`expires_at.is.null,expires_at.gt.${nowIso}`)
    .limit(1)
    .retry(false);

  if (error) {
    console.error("ESAT access check failed:", { email, error });
    return {
      ok: false as const,
      response: json({ ok: false, error: "Access service temporarily unavailable" }, 503),
    };
  }

  if (!data || data.length === 0) {
    return {
      ok: false as const,
      response: json({ ok: false, error: "No ESAT access" }, 403),
    };
  }

  return {
    ok: true as const,
    user,
    email,
  };
}

export const ESAT_TABLE_CANDIDATES = [
  "esat_qb_questions",
  "esat_questions",
  "esat_qb_public_questions",
  "esat_question_bank",
];

export function cleanRows(rows: any[]) {
  return (rows || [])
    .filter((row) => row && row.is_active !== false)
    .sort((a, b) => {
      const topicA = String(a.topic || "").toLowerCase();
      const topicB = String(b.topic || "").toLowerCase();

      if (topicA !== topicB) return topicA.localeCompare(topicB);

      const diffA = Number(a.difficulty ?? 999);
      const diffB = Number(b.difficulty ?? 999);

      if (Number.isFinite(diffA) && Number.isFinite(diffB) && diffA !== diffB) {
        return diffA - diffB;
      }

      const orderA = Number(a.display_order ?? a.original_index ?? 999999);
      const orderB = Number(b.display_order ?? b.original_index ?? 999999);

      return orderA - orderB;
    });
}

export function normaliseQuestion(row: any, index = 0) {
  const qid = String(row.qid ?? row.id ?? row.question_id ?? index + 1);

  return {
    ...row,
    qid,
    id: row.id ?? qid,
    display_order: Number(row.display_order ?? row.original_index ?? index + 1),
    original_index: Number(row.original_index ?? row.display_order ?? index + 1),
    paper: row.paper ?? row.esat_paper ?? row.module ?? "ESAT",
    topic: row.topic ?? row.category ?? "",
    subtopic: row.subtopic ?? row.sub_topic ?? "",
    difficulty: row.difficulty ?? row.difficulty_level ?? "",
    prompt_html: row.prompt_html ?? row.question_html ?? row.prompt ?? "",
    options: row.options ?? [],
    answer: row.answer ?? row.correct_answer ?? row.correct_option ?? "",
    solution_html: row.solution_html ?? row.explanation_html ?? row.solution ?? "",
    nice_tip_html: row.nice_tip_html ?? row.hint_html ?? row.tip_html ?? "",
    page_assets: row.page_assets ?? [],
    question_assets: row.question_assets ?? [],
  };
}

