import { NextRequest, NextResponse } from "next/server";
import { normalizeExam, requireAmcAccess } from "../../../../lib/amcAccess";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const access = await requireAmcAccess();
  if (!access.ok) return access.response;

  const exam = normalizeExam(req.nextUrl.searchParams.get("exam"));
  const qid = req.nextUrl.searchParams.get("qid");

  if (!exam) {
    return NextResponse.json({ error: "Invalid exam" }, { status: 400 });
  }

  if (!qid) {
    return NextResponse.json({ error: "Missing qid" }, { status: 400 });
  }

  const { data, error } = await access.admin
    .from("amc_questions")
    .select(`
      qid,
      kind,
      difficulty,
      topic,
      subtopic,
      tags,
      prompt_html,
      options,
      page_assets,
      question_assets,
      nice_tip_html,
      display_order
    `)
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
    exam: exam.label,
    question: data,
  });
}
