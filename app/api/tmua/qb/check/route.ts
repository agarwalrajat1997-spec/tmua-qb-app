import { adminClient, json, requireTmuaAccess } from "../_server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function POST(req: Request) {
  const access = await requireTmuaAccess();
  if (!access.ok) return access.response;

  const body = await req.json().catch(() => null);

  const qid = String(body?.qid || "").trim();
  const selected = String(body?.selected || "").trim();

  if (!qid || !selected) {
    return json({ ok: false, error: "Missing qid or selected answer" }, 400);
  }

  const supabase = adminClient();

  const { data, error } = await supabase
    .from("tmua_qb_questions")
    .select("qid, answer, solution_html")
    .eq("qid", qid)
    .eq("is_active", true)
    .single();

  if (error || !data) {
    console.error("TMUA answer check failed:", error);
    return json({ ok: false, error: "Question not found" }, 404);
  }

  const isCorrect = selected === data.answer;

  return json({
    ok: true,
    qid,
    selected,
    isCorrect,
    answer: data.answer,
    solution_html: data.solution_html || "",
  });
}
