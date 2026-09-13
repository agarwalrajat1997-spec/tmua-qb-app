import { adminClient, json, requireTmuaAccess } from "../_server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";


function tsSortKey(value: unknown) {
  return String(value || "")
    .toLowerCase()
    .replace(/^\d+[_\-\s]*/, "")
    .trim();
}

function tsDifficultyValue(value: unknown) {
  const n = Number(value);
  return Number.isFinite(n) ? n : 999;
}

function tsDefaultSort(a: any, b: any) {
  const topicA = tsSortKey(a.topic);
  const topicB = tsSortKey(b.topic);

  if (topicA !== topicB) {
    return topicA.localeCompare(topicB);
  }

  const diffA = tsDifficultyValue(a.difficulty);
  const diffB = tsDifficultyValue(b.difficulty);

  if (diffA !== diffB) {
    return diffA - diffB;
  }

  const orderA = Number(a.display_order ?? a.original_index ?? 999999);
  const orderB = Number(b.display_order ?? b.original_index ?? 999999);

  return orderA - orderB;
}

export async function GET() {
  const access = await requireTmuaAccess();
  if (!access.ok) return access.response;

  const supabase = adminClient();

  const pageSize = 1000;
  let from = 0;
  let allQuestions: any[] = [];

  while (true) {
    const to = from + pageSize - 1;

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
      .order("display_order", { ascending: true })
      .range(from, to);

    if (error) {
      console.error("TMUA list load failed:", error);
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
    count: allQuestions.length,
    questions: allQuestions,
  });
}

