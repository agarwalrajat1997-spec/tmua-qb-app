import { NextResponse } from "next/server";
import { estimateEsatTestScores } from "@/lib/server/esat-score-estimates";

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
  };
  const testId = String(payload?.test_id ?? "").trim();

  if (!testId) {
    return NextResponse.json(
      { error: "test_id is required." },
      { status: 400 },
    );
  }

  try {
    const estimate = estimateEsatTestScores(
      testId,
      Array.isArray(payload?.raw_scores)
        ? payload.raw_scores
        : [],
    );

    return NextResponse.json({
      ok: true,
      estimate,
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

