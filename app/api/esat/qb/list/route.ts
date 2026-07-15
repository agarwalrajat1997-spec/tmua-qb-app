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

const PAGE_SIZE = 1000;
const MAX_ROWS = 5000;

async function loadAllActiveRows(supabase: any, table: string) {
  const allRows: any[] = [];

  for (let from = 0; from < MAX_ROWS; from += PAGE_SIZE) {
    const to = from + PAGE_SIZE - 1;

    const { data, error } = await supabase
      .from(table)
      .select(ESAT_META_COLUMNS)
      .eq("is_active", true)
      .order("display_order", { ascending: true })
      .order("qid", { ascending: true })
      .range(from, to);

    if (error) {
      return { rows: null, error };
    }

    const batch = data || [];
    allRows.push(...batch);

    if (batch.length < PAGE_SIZE) break;
  }

  return { rows: allRows, error: null };
}

export async function GET() {
  const access = await requireESATAccess();
  if (!access.ok) return access.response;

  const supabase = adminClient();
  let lastError: any = null;

  for (const table of ESAT_TABLE_CANDIDATES) {
    const { rows, error } = await loadAllActiveRows(supabase, table);

    if (error) {
      lastError = error;
      continue;
    }

    const questions = (rows || []).map((row: any, index: number) => {
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
