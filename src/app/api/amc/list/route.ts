import { NextRequest, NextResponse } from "next/server";
import { normalizeExam, requireAmcAccess } from "../../../../lib/amcAccess";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const access = await requireAmcAccess();
  if (!access.ok) return access.response;

  const exam = normalizeExam(req.nextUrl.searchParams.get("exam"));
  if (!exam) {
    return NextResponse.json({ error: "Invalid exam" }, { status: 400 });
  }

  const { data, error } = await access.admin
    .from("amc_questions")
    .select("qid,display_order,difficulty,topic,subtopic,amc_exams")
    .eq("is_active", true)
    .eq(exam.column, true)
    .order("display_order", { ascending: true });

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json({
    exam: exam.label,
    questions: data || [],
  });
}
