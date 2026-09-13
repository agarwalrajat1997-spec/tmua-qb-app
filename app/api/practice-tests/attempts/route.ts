import { NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase/server";

export const runtime = "nodejs";

const FINGERPRINT = "ATTEMPTS_ROUTE_PATCH_v3_TMUA_SCORE9_20260306";

export async function GET(req: Request) {
  const supabase = await createSupabaseServerClient();

  const { data: { user }, error: userErr } = await supabase.auth.getUser();
  if (userErr || !user) {
    return NextResponse.json({ error: "Unauthorized", fingerprint: FINGERPRINT }, { status: 401 });
  }

  const url = new URL(req.url);
  const testId = url.searchParams.get("test_id");

  if (testId) {
    const { data, error } = await supabase
      .from("practice_test_attempts")
      .select("id, test_id, test_title, paper, total_questions, score, tmua_score9, submitted_at, incorrect, time_spent, answers, correct_answers, flags")
      .eq("user_id", user.id)
      .eq("test_id", testId)
      .order("submitted_at", { ascending: true })
      .limit(50);

    if (error) {
      return NextResponse.json({ error: error.message, fingerprint: FINGERPRINT }, { status: 500 });
    }

    const attempts = (data ?? []).map((row, idx) => ({
      ...row,
      attempt_no: idx + 1,
    }));

    return NextResponse.json({
      ok: true,
      fingerprint: FINGERPRINT,
      test_id: testId,
      total_attempts: attempts.length,
      attempts,
    });
  }

  const { data, error } = await supabase
    .from("practice_test_attempts")
    .select("id, test_id, test_title, paper, total_questions, score, tmua_score9, submitted_at")
    .eq("user_id", user.id)
    .order("submitted_at", { ascending: false })
    .limit(500);

  if (error) {
    return NextResponse.json({ error: error.message, fingerprint: FINGERPRINT }, { status: 500 });
  }

  const counts: Record<string, number> = {};
  const latestByTest: Record<string, any> = {};

  for (const row of (data ?? [])) {
    counts[row.test_id] = (counts[row.test_id] ?? 0) + 1;
    if (!latestByTest[row.test_id]) latestByTest[row.test_id] = row;
  }

  const latest = Object.values(latestByTest).map((row: any) => ({
    ...row,
    attempt_no: counts[row.test_id] ?? null,
    total_attempts: counts[row.test_id] ?? 0,
  }));

  return NextResponse.json({ ok: true, fingerprint: FINGERPRINT, latest, counts });
}