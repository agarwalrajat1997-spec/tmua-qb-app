import {
  ESAT_TABLE_CANDIDATES,
  adminClient,
  json,
  normaliseQuestion,
  requireESATAccess,
} from "../_server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const ESAT_META_COLUMNS = [
  "id",
  "qid",
  "display_order",
  "paper_question_number",
  "kind",
  "paper",
  "topic",
  "subtopic",
  "difficulty",
  "tags",
  "is_active",
].join(",");

export async function GET() {
  const access = await requireESATAccess();
  if (!access.ok) return access.response;

  const supabase = adminClient();
  let lastError: any = null;

  for (const table of ESAT_TABLE_CANDIDATES) {
    const { data, error } = await supabase
      .from(table)
      .select(ESAT_META_COLUMNS)
      .eq("is_active", true)
      .order("display_order", { ascending: true })
      .order("qid", { ascending: true })
      .limit(3000);

    if (error) {
      lastError = error;
      continue;
    }

    const rows = data || [];

    const questions = rows.map((row: any, index: number) => {
      const q = normaliseQuestion(row, index);

      return {
        qid: q.qid,
        id: q.id,
        display_order: index + 1,
        original_index: index + 1,
        db_display_order: q.display_order,
        paper_question_number: q.paper_question_number,
        paper: q.paper,
        topic: q.topic,
        subtopic: q.subtopic,
        difficulty: q.difficulty,
        tags: q.tags ?? [],
        kind: q.kind ?? "question",
      };
    });

    return json({
      ok: true,
      table,
      total: questions.length,
      questions,
      items: questions,
    });
  }

  console.error(
    "ESAT list load failed. Tried tables:",
    ESAT_TABLE_CANDIDATES,
    lastError
  );

  return json(
    {
      ok: false,
      error: "Could not load ESAT questions. Check ESAT table name.",
      tried_tables: ESAT_TABLE_CANDIDATES,
      details: lastError?.message || String(lastError || ""),
    },
    500
  );
}
