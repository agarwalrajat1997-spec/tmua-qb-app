import { adminClient, json, requireTmuaAccess } from "../_server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET() {
  const access = await requireTmuaAccess();
  if (!access.ok) return access.response;

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
      tags
    `)
    .eq("is_active", true)
    .order("display_order", { ascending: true });

  if (error) {
    console.error("TMUA list load failed:", error);
    return json({ ok: false, error: error.message }, 500);
  }

  return json({
    ok: true,
    questions: data ?? [],
  });
}
