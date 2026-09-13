import { NextRequest, NextResponse } from "next/server";
import { normalizeExam, requireAmcAccess } from "../../../../lib/amcAccess";

export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  const access = await requireAmcAccess();
  if (!access.ok) return access.response;

  const body = await req.json().catch(() => null);

  const exam = normalizeExam(body?.exam || null);
  const qid = body?.qid;
  const selected = String(body?.selected || "").trim().toUpperCase();

  if (!exam) {
    return NextResponse.json({ error: "Invalid exam" }, { status: 400 });
  }

  if (!qid || !selected) {
    return NextResponse.json({ error: "Missing qid or selected answer" }, { status: 400 });
  }

  const { data, error } = await access.admin
    .from("amc_questions")
    .select("qid,answer,solution_html,nice_tip_html")
    .eq("is_active", true)
    .eq(exam.column, true)
    .eq("qid", qid)
    .maybeSingle();

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  if (!data) {
    return NextResponse.json({ error: "Question not found" }, { status: 404 });
  }

  return NextResponse.json({
    correct: selected === data.answer,
    answer: data.answer,
    solution_html: data.solution_html,
    nice_tip_html: data.nice_tip_html,
  });
}
