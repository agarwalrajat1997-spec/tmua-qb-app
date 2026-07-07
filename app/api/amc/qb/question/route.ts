import { adminClient, json, requireAMCAccess } from "../_server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET(req: Request) {
  const access = await requireAMCAccess();
  if (!access.ok) return access.response;

  const { searchParams } = new URL(req.url);
  const qid = searchParams.get("qid");

  if (!qid) {
    return json({ ok: false, error: "Missing qid" }, 400);
  }

  const supabase = adminClient();

  const { data, error } = await supabase
    .from("amc_questions")
    .select(`
      qid,
      display_order,
      original_index,
      kind,
      topic,
      subtopic,
      difficulty,
      tags,
      prompt_html,
      options,
      answer,
      shortcut_available,
      nice_tip_html,
      amc_exams,
      amc_categories,
      amc_primary
    `)
    .eq("qid", qid)
    .eq("is_active", true)
    .single();

  if (error || !data) {
    console.error("AMC single question load failed:", error);
    return json({ ok: false, error: "Question not found" }, 404);
  }

  return json({
    ok: true,
    question: {
      ...data,

      // Important:
      // Do not send these to the frontend.
      // Prompt images should come only from prompt_html.
      // Option images should come only from options[].html.
      page_assets: [],
      question_assets: [],
      solution_assets: [],
      assets: []
    },
  });
}
