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

function mergeRows(primaryRows: any[], physicsRows: any[]) {
  const byQid = new Map<string, any>();

  for (const row of primaryRows || []) {
    if (row?.qid) byQid.set(row.qid, row);
  }

  for (const row of physicsRows || []) {
    if (row?.qid) byQid.set(row.qid, row);
  }

  return Array.from(byQid.values()).sort((a, b) => {
    const ao = Number(a.display_order ?? 999999);
    const bo = Number(b.display_order ?? 999999);
    if (ao !== bo) return ao - bo;
    return String(a.qid || "").localeCompare(String(b.qid || ""));
  });
}

export async function GET() {
  const access = await requireESATAccess();
  if (!access.ok) return access.response;

  const supabase = adminClient();
  let lastError: any = null;

  for (const table of ESAT_TABLE_CANDIDATES) {
    const primary = await supabase
      .from(table)
      .select(ESAT_META_COLUMNS)
      .eq("is_active", true)
      .order("display_order", { ascending: true })
      .order("qid", { ascending: true })
      .range(0, 999);

    if (primary.error) {
      lastError = primary.error;
      continue;
    }

    const physics = await supabase
      .from(table)
      .select(ESAT_META_COLUMNS)
      .eq("is_active", true)
      .eq("paper", "ESAT Physics")
      .order("display_order", { ascending: true })
      .order("qid", { ascending: true })
      .range(0, 499);

    if (physics.error) {
      lastError = physics.error;
      continue;
    }

    const rows = mergeRows(primary.data || [], physics.data || []);

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
