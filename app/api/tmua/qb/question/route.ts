import { adminClient, json, requireTmuaAccess } from "../_server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET(req: Request) {
  const access = await requireTmuaAccess();
  if (!access.ok) return access.response;

  const { searchParams } = new URL(req.url);
  const qid = searchParams.get("qid");

  if (!qid) {
    return json({ ok: false, error: "Missing qid" }, 400);
  }

  const supabase = adminClient();

  const { data, error } = await supabase
    .from("tmua_qb_questions")
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
    .maybeSingle()
    .retry(false);

  if (error) {
    console.error("TMUA question load temporarily unavailable:", error);
    return json({ ok: false, error: "Question service temporarily unavailable. Please retry." }, 503);
  }
  if (!data) {
    return json({ ok: false, error: "Question not found" }, 404);
  }

  return json({
    ok: true,
    question: data,
  });
}
