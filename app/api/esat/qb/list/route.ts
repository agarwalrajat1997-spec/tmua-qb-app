import {
  ESAT_TABLE_CANDIDATES,
  adminClient,
  cleanRows,
  json,
  normaliseQuestion,
  requireESATAccess,
} from "../_server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET() {
  const access = await requireESATAccess();
  if (!access.ok) return access.response;

  const supabase = adminClient();

  let lastError: any = null;

  for (const table of ESAT_TABLE_CANDIDATES) {
    const { data, error } = await supabase
      .from(table)
      .select("*")
      .limit(3000);

    if (error) {
      lastError = error;
      continue;
    }

    const sorted = cleanRows(data || []);

    const questions = sorted.map((row: any, index: number) => {
      const q = normaliseQuestion(row, index);

      return {
        qid: q.qid,
        id: q.id,
        display_order: index + 1,
        original_index: index + 1,
        db_display_order: q.display_order,
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

  console.error("ESAT list load failed. Tried tables:", ESAT_TABLE_CANDIDATES, lastError);

  return json({
    ok: false,
    error: "Could not load ESAT questions. Check ESAT table name.",
    tried_tables: ESAT_TABLE_CANDIDATES,
    details: lastError?.message || String(lastError || ""),
  }, 500);
}
