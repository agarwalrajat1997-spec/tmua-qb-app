import {
  SAT_QUESTIONS_TABLE,
  adminClient,
  json,
  requireSATAccess,
} from "../_server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const MAX_REPORT_LENGTH = 4000;

export async function POST(req: Request) {
  const access = await requireSATAccess();
  if (!access.ok) return access.response;

  const body = await req.json().catch(() => null);
  const qid = String(body?.qid || "").trim();
  const reportText = String(body?.report_text || "").trim();

  if (!qid || reportText.length < 5) {
    return json(
      { ok: false, error: "Choose a question and add a short description." },
      400
    );
  }

  if (reportText.length > MAX_REPORT_LENGTH) {
    return json(
      {
        ok: false,
        error: `Report must be ${MAX_REPORT_LENGTH} characters or fewer.`,
      },
      400
    );
  }

  const supabase = adminClient();
  const { data: question, error: questionError } = await supabase
    .from(SAT_QUESTIONS_TABLE)
    .select("qid, display_order, paper, topic, subtopic, difficulty")
    .eq("qid", qid)
    .eq("is_active", true)
    .maybeSingle();

  if (questionError || !question) {
    return json({ ok: false, error: "Active question not found." }, 404);
  }

  const context = {
    display_order: question.display_order,
    paper: question.paper,
    topic: question.topic,
    subtopic: question.subtopic,
    difficulty: question.difficulty,
    selected_answer: String(body?.selected_answer || "").slice(0, 20),
    checked_status: String(body?.checked_status || "").slice(0, 40),
    page_url: String(body?.page_url || "").slice(0, 1000),
    user_agent: String(req.headers.get("user-agent") || "").slice(0, 1000),
  };

  const { data: report, error } = await supabase
    .from("sat_question_reports")
    .insert({
      user_id: access.user.id || null,
      user_email: access.email,
      qid,
      report_text: reportText,
      context,
    })
    .select("id, created_at")
    .single();

  if (error) {
    console.error("SAT question report insert failed:", error);
    return json({ ok: false, error: "Could not save the report." }, 500);
  }

  return json({ ok: true, report_id: report.id, created_at: report.created_at });
}
