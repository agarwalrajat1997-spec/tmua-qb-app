import { adminClient, json, requireAMCAccess } from "../_server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function POST(req: Request) {
  const access = await requireAMCAccess();
  if (!access.ok) return access.response;

  const body = await req.json().catch(() => null);

  const qid = String(body?.qid || "").trim();
  const selected = String(body?.selected || body?.answer || "").trim().toUpperCase();

  if (!qid || !selected) {
    return json({ ok: false, error: "Missing qid or selected answer" }, 400);
  }

  const supabase = adminClient();

  const { data, error } = await supabase
    .from("amc_questions")
    .select("qid, answer, solution_html, nice_tip_html")
    .eq("qid", qid)
    .eq("is_active", true)
    .single();

  if (error || !data) {
    console.error("AMC answer check failed:", error);
    return json({ ok: false, error: "Question not found" }, 404);
  }

  const isCorrect = selected === data.answer;

  return json({
    ok: true,
    qid,
    selected,
    isCorrect,
    correct: isCorrect,
    answer: data.answer,
    solution_html: data.solution_html || "",
    nice_tip_html: data.nice_tip_html || "",
  });
}
