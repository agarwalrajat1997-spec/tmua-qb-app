import { NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { readTmuaPastPaperSettings } from "@/lib/tmua/past-paper-settings";
import { hasStandardTimePolicy, practiceSpec, readTrustedPracticeResult, type Conversion } from "@/lib/server/practice-standard-time";
import { TMUA_PREDICTIVE_2026_ID } from "@/lib/server/tmua-predictive-2026";
import { readPredictiveAttemptId } from "@/lib/tmua/attempt-identity";

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
  const recoveryId = url.searchParams.get("client_attempt_id");
  // A retry checks the authenticated student's exact saved report, not a
  // similar answer array or the first 50 historical attempts. No writes occur.
  if (recoveryId !== null) {
    try {
      if (testId !== TMUA_PREDICTIVE_2026_ID || !readPredictiveAttemptId(recoveryId)) throw new Error("Invalid predictive recovery request.");
    } catch {
      return NextResponse.json({ error: "Invalid predictive recovery request." }, { status: 400 });
    }
    const { data, error } = await supabase.from("practice_test_attempts")
      .select("id,test_id,submitted_at,score,total_questions")
      .eq("user_id", user.id).eq("test_id", testId)
      .eq("predictor_metadata->>tmua_predictive_client_attempt_id", recoveryId)
      .order("submitted_at", { ascending: false }).limit(1).maybeSingle().retry(false);
    if (error) return NextResponse.json({ error: "Saved report lookup is temporarily unavailable." }, {
      status: 503, headers: { "Cache-Control": "no-store", "Retry-After": "30" },
    });
    return NextResponse.json({ ok: true, saved: !!data, client_attempt_id: recoveryId, attempt: data ?? null }, {
      headers: { "Cache-Control": "no-store" },
    });
  }

  async function conversionsFor(rows: { test_id: string; predictor_metadata: unknown }[]) {
    const result = new Map<string, Conversion>();
    if (!rows.some(row => hasStandardTimePolicy(row.predictor_metadata) && row.test_id !== TMUA_PREDICTIVE_2026_ID &&
      practiceSpec(row.test_id)?.exam === "tmua" && practiceSpec(row.test_id)?.canonical.expectedQuestions === 40)) return result;
    const [catalogue, profiles] = await Promise.all([
      supabase.from("tmua_test_catalog").select("test_id,score_conversion_profile"),
      supabase.from("tmua_score_conversion_profiles").select("profile,conversion_version,score_values"),
    ]);
    if (catalogue.error || profiles.error) return result;
    for (const test of catalogue.data ?? []) {
      const profile = (profiles.data ?? []).find(profile => profile.profile === test.score_conversion_profile);
      if (profile) result.set(test.test_id, profile as Conversion);
    }
    return result;
  }

  if (testId) {
    const { data, error } = await supabase
      .from("practice_test_attempts")
      .select("id, test_id, test_title, paper, total_questions, score, tmua_score9, submitted_at, incorrect, time_spent, answers, correct_answers, flags, predictor_metadata")
      .eq("user_id", user.id)
      .eq("test_id", testId)
      .order("submitted_at", { ascending: true })
      .limit(50);

    if (error) {
      return NextResponse.json({ error: error.message, fingerprint: FINGERPRINT }, { status: 500 });
    }

    const conversions = await conversionsFor(data ?? []);
    const attempts = (data ?? []).map(({ predictor_metadata, ...row }, idx) => ({
      ...row,
      attempt_settings: readTmuaPastPaperSettings(row.test_id, predictor_metadata),
      ...readTrustedPracticeResult(row.test_id, predictor_metadata, row.answers, row.score, conversions.get(row.test_id)),
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
    .select("id, test_id, test_title, paper, total_questions, score, tmua_score9, submitted_at, predictor_metadata")
    .eq("user_id", user.id)
    .order("submitted_at", { ascending: false })
    .limit(500);

  if (error) {
    return NextResponse.json({ error: error.message, fingerprint: FINGERPRINT }, { status: 500 });
  }

  const counts: Record<string, number> = {};
  const latestByTest: Record<string, NonNullable<typeof data>[number] & { answers?: unknown }> = {};

  for (const row of (data ?? [])) {
    counts[row.test_id] = (counts[row.test_id] ?? 0) + 1;
    if (!latestByTest[row.test_id]) latestByTest[row.test_id] = row;
  }

  const latestRows = Object.values(latestByTest);
  const conversions = await conversionsFor(latestRows);
  // Only the latest explicitly new-policy rows need canonical answer checks.
  // Do not expand the legacy 500-row summary into hundreds of answer arrays.
  const markedIds = latestRows.filter(row => hasStandardTimePolicy(row.predictor_metadata)).map(row => row.id);
  const canonicalAnswers = new Map<string, unknown>();
  if (markedIds.length) {
    const detail = await supabase.from("practice_test_attempts").select("id,answers")
      .eq("user_id", user.id).in("id", markedIds);
    if (!detail.error) for (const row of detail.data ?? []) canonicalAnswers.set(row.id, row.answers);
  }
  const latest = latestRows.map(({ predictor_metadata, answers, ...row }) => {
    // Keep detail-only answer arrays out of the lightweight public summary.
    void answers;
    return {
      ...row,
      attempt_settings: readTmuaPastPaperSettings(row.test_id, predictor_metadata),
      ...readTrustedPracticeResult(row.test_id, predictor_metadata, canonicalAnswers.get(row.id), row.score, conversions.get(row.test_id)),
      attempt_no: counts[row.test_id] ?? null,
      total_attempts: counts[row.test_id] ?? 0,
    };
  });

  return NextResponse.json({ ok: true, fingerprint: FINGERPRINT, latest, counts });
}
