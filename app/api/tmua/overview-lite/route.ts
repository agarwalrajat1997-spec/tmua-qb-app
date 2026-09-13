import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const EXAM_DATE = "2026-10-12";
const EXAM_DATE_LABEL = "12 October";

function daysToTmua(): number {
  const now = new Date();
  const todayUtc = Date.UTC(
    now.getUTCFullYear(),
    now.getUTCMonth(),
    now.getUTCDate(),
  );
  const examUtc = Date.UTC(2026, 9, 12);

  return Math.max(
    0,
    Math.ceil((examUtc - todayUtc) / (24 * 60 * 60 * 1000)),
  );
}

// Emergency load-shed endpoint, 13 Sep 2026.
// Deliberately performs no database reads or writes. The normal TMUA workspace,
// question bank, tests, access rules and Supabase data are untouched.
export async function GET() {
  const calculatedAt = new Date().toISOString();

  return NextResponse.json(
    {
      ok: true,
      predictor: {
        modelVersion: "tmua-overview-emergency-lite-20260913",
        status: "insufficient_evidence",
        score: null,
        lowerBound: null,
        upperBound: null,
        confidence: null,
        testEvidenceCount: 0,
        independentTestCount: 0,
        qbUniqueQuestions: 0,
        qbTopicCoverage: 0,
        calculatedAt,
      },
      preparationRank: {
        modelVersion: "tmua-preparation-rank-emergency-lite-20260913",
        hasGenuinePreparationEvidence: false,
        score: null,
        rank: null,
        cohortSize: 0,
        components: null,
        calculatedAt,
      },
      countdown: {
        daysToTmua: daysToTmua(),
        examDate: EXAM_DATE,
        examDateLabel: EXAM_DATE_LABEL,
      },
    },
    {
      status: 200,
      headers: {
        "Cache-Control": "private, max-age=30",
        "X-TS-Emergency-Load-Shed": "20260913",
      },
    },
  );
}
