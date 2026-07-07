import { adminClient, json, requireSATAccess } from "../_server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const ALLOWED_PAPERS = new Set(["SAT 8", "SAT 10", "SAT 12"]);

export async function GET(req: Request) {
  const access = await requireSATAccess();
  if (!access.ok) return access.response;

  const { searchParams } = new URL(req.url);
  const requestedPaper = (searchParams.get("paper") || "").trim();
  const paper = ALLOWED_PAPERS.has(requestedPaper) ? requestedPaper : "";

  const supabase = adminClient();

  const pageSize = 1000;
  let from = 0;
  let allQuestions: any[] = [];

  while (true) {
    const to = from + pageSize - 1;

    let query = supabase
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
        tags
      `)
      .eq("is_active", true);

    if (paper) {
      query = query.eq("paper", paper);
    }

    const { data, error } = await query
      .order("display_order", { ascending: true })
      .range(from, to);

    if (error) {
      console.error("SAT list load failed:", error);
      return json({ ok: false, error: error.message }, 500);
    }

    const rows = data ?? [];
    allQuestions = allQuestions.concat(rows);

    if (rows.length < pageSize) break;

    from += pageSize;

    if (from > 10000) {
      return json({ ok: false, error: "Pagination safety stop reached" }, 500);
    }
  }

  return json({
    ok: true,
    paper: paper || null,
    count: allQuestions.length,
    questions: allQuestions,
  });
}

