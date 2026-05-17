import { NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase/server";

export const runtime = "nodejs";

const FINGERPRINT = "SUBMIT_ROUTE_PATCH_v3_TMUA_SCORE9_20260306";

function badRequest(msg: string) {
  return NextResponse.json({ error: msg, fingerprint: FINGERPRINT }, { status: 400 });
}

function tmuaScore9(rawCorrect: number, totalQuestions: number, thresholdRaw = 6): number {
  const raw = Number(rawCorrect || 0);
  const total = Number(totalQuestions || 20);
  const thr = Number(thresholdRaw || 6);

  if (!Number.isFinite(raw) || !Number.isFinite(total) || total <= 0) return 1.0;
  if (raw <= thr) return 1.0;

  const frac = (raw - thr) / (total - thr);
  const score9 = 1.0 + frac * 8.0;
  return Math.round(Math.max(1.0, Math.min(9.0, score9)) * 10) / 10;
}

function computeTmuaScore9(body: any): number | null {
  const totalQuestions = Number(body?.total_questions ?? 0);
  const rawScore = Number(body?.score ?? 0);

  const answers = Array.isArray(body?.answers) ? body.answers : [];
  const correctAnswers = Array.isArray(body?.correct_answers) ? body.correct_answers : [];

  // Full test: average Paper 1 and Paper 2 TMUA score9
  if (totalQuestions >= 40 && answers.length >= 40 && correctAnswers.length >= 40) {
    let p1 = 0;
    let p2 = 0;

    for (let i = 0; i < 20; i++) {
      if (answers[i] === correctAnswers[i] && answers[i] != null) p1++;
    }
    for (let i = 20; i < 40; i++) {
      if (answers[i] === correctAnswers[i] && answers[i] != null) p2++;
    }

    const p1s = tmuaScore9(p1, 20, 6);
    const p2s = tmuaScore9(p2, 20, 6);
    return Math.round(((p1s + p2s) / 2) * 10) / 10;
  }

  // Topic / single-paper test
  if (totalQuestions > 0) {
    return tmuaScore9(rawScore, totalQuestions, 6);
  }

  return null;
}

export async function POST(req: Request) {
  const supabase = await createSupabaseServerClient();

  const {
    data: { user },
    error: userErr,
  } = await supabase.auth.getUser();

  if (userErr || !user) {
    return NextResponse.json({ error: "Unauthorized", fingerprint: FINGERPRINT }, { status: 401 });
  }

  let body: any;
  try {
    body = await req.json();
  } catch {
    return badRequest("Invalid JSON");
  }

  const test_id = String(body?.test_id || "").trim();
  if (!test_id) return badRequest("test_id is required");

  const tmua_score9 = computeTmuaScore9(body);

  const payload = {
    user_id: user.id,
    email: user.email ?? null,
    test_id,
    test_title: body?.test_title ?? null,
    paper: body?.paper ?? null,
    total_questions: Number(body?.total_questions ?? 0),
    score: Number(body?.score ?? 0),
    tmua_score9,
    answers: body?.answers ?? [],
    correct_answers: body?.correct_answers ?? [],
    time_spent: body?.time_spent ?? [],
    flags: body?.flags ?? [],
    incorrect: body?.incorrect ?? [],
    session_label: body?.session_label ?? null,
    student_name: body?.student_name ?? null,
    submitted_at: new Date().toISOString(),
  };

  const { data: inserted, error: insErr } = await supabase
    .from("practice_test_attempts")
    .insert(payload)
    .select("id, submitted_at, test_id, tmua_score9")
    .single();

  if (insErr) {
    return NextResponse.json({ error: insErr.message, fingerprint: FINGERPRINT }, { status: 500 });
  }

  const { count, error: countErr } = await supabase
    .from("practice_test_attempts")
    .select("id", { count: "exact", head: true })
    .eq("user_id", user.id)
    .eq("test_id", test_id);

  if (countErr) {
    return NextResponse.json({
      ok: true,
      fingerprint: FINGERPRINT,
      attempt: inserted,
      attempt_no: null,
    });
  }

  return NextResponse.json({
    ok: true,
    fingerprint: FINGERPRINT,
    attempt: inserted,
    attempt_no: count ?? null,
  });
}