import { adminClient, json, requireSATAccess } from "../_server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET(req: Request) {
  const access = await requireSATAccess();
  if (!access.ok) return access.response;

  const { searchParams } = new URL(req.url);
  const qid = searchParams.get("qid");

  if (!qid) {
    return json({ ok: false, error: "Missing qid" }, 400);
  }

  const supabase = adminClient();

  const { data, error } = await supabase
    .from("SAT_qb_questions")
    .select(`
      qid,
      display_order,
      paper_question_number,
      kind,
      paper,
      topic,
      subtopic,
      difficulty,
      tags,
      prompt_html,
      options,
      page_assets,
      shortcut_available,
      nice_tip_html
    `)
    .eq("qid", qid)
    .eq("is_active", true)
    .single();

  if (error || !data) {
    console.error("SAT single question load failed:", error);
    return json({ ok: false, error: "Question not found" }, 404);
  }

  return json({
    ok: true,
    question: data,
  });
}


