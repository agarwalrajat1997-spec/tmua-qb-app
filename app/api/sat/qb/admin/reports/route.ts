import { adminClient, json } from "../../_server";
import { requireSATAdmin } from "../_server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const QUESTION_FIELDS = [
  "qid",
  "display_order",
  "paper",
  "topic",
  "subtopic",
  "difficulty",
  "prompt_html",
  "options",
  "page_assets",
  "answer",
  "solution_html",
  "nice_tip_html",
].join(",");

export async function GET() {
  const access = await requireSATAdmin();
  if (!access.ok) return access.response;

  const supabase = adminClient();
  const { data: reports, error } = await supabase
    .from("sat_question_reports")
    .select(
      "id,user_id,user_email,qid,report_text,context,status,created_at,resolved_at"
    )
    .order("created_at", { ascending: false })
    .limit(1000);

  if (error) {
    console.error("SAT admin report load failed:", error);
    return json({ ok: false, error: "Could not load SAT reports" }, 500);
  }

  const qids = [...new Set((reports || []).map((report) => report.qid))];
  let questions: Record<string, unknown>[] = [];

  if (qids.length > 0) {
    const { data, error: questionError } = await supabase
      .from("sat_qb_questions")
      .select(QUESTION_FIELDS)
      .in("qid", qids);

    if (questionError) {
      console.error("SAT admin question preview load failed:", questionError);
      return json({ ok: false, error: "Could not load question previews" }, 500);
    }
    questions = (data || []) as unknown as Record<string, unknown>[];
  }

  const questionByQid = new Map(
    questions.map((question) => [String(question.qid), question])
  );

  return json({
    ok: true,
    admin_email: access.email,
    reports: (reports || []).map((report) => ({
      ...report,
      question: questionByQid.get(report.qid) || null,
    })),
  });
}
