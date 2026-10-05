import { NextResponse } from "next/server";
import { estimateEsatTestScores } from "@/lib/server/esat-score-estimates";
import { estimateOctober2026EsatScores } from "@/lib/server/esat-october-2026-tests";
import { createStandardTimeEstimate, practiceSpec, resolvePracticeSettings } from "@/lib/server/practice-standard-time";

export const runtime = "nodejs";

export async function POST(request: Request) {
  let body: unknown;

  try {
    body = await request.json();
  } catch {
    return NextResponse.json(
      { error: "Invalid JSON." },
      { status: 400 },
    );
  }

  const payload = body as {
    test_id?: unknown;
    raw_scores?: unknown;
    answers?: unknown;
    practice_settings?: unknown;
  };
  const testId = String(payload?.test_id ?? "").trim();

  if (!testId) {
    return NextResponse.json(
      { error: "test_id is required." },
      { status: 400 },
    );
  }

  try {
    const settings = resolvePracticeSettings(testId, payload?.practice_settings);
    if (settings && (practiceSpec(testId)?.exam !== "esat" || !Array.isArray(payload.answers))) {
      throw new Error("Canonical ESAT answers are required when practice settings are supplied.");
    }
    const standardTimeEstimate = settings ? createStandardTimeEstimate(testId, payload.answers as unknown[], settings) : null;
    const rawScores = standardTimeEstimate ? standardTimeEstimate.units.map(unit => unit.actual_raw) :
      Array.isArray(payload?.raw_scores) ? payload.raw_scores : [];
    const estimate = estimateOctober2026EsatScores(testId, rawScores) ??
      estimateEsatTestScores(testId, rawScores);

    return NextResponse.json({
      ok: true,
      estimate,
      practice_settings: settings,
      standard_time_estimate: standardTimeEstimate,
    });
  } catch (error) {
    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? error.message
            : "Unable to calculate ESAT estimate.",
      },
      { status: 400 },
    );
  }
}
