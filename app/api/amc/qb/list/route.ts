import { adminClient, json, requireAMCAccess } from "../_server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

function norm(v: unknown) {
  return String(v || "")
    .toUpperCase()
    .replace(/[^A-Z0-9]/g, "");
}

function examFromPaper(raw: string | null) {
  const s = norm(raw || "AMC 8");

  if (s.includes("AMC12") || s.includes("12")) {
    return { paper: "AMC 12", column: "amc_12" };
  }

  if (s.includes("AMC10") || s.includes("10")) {
    return { paper: "AMC 10", column: "amc_10" };
  }

  return { paper: "AMC 8", column: "amc_8" };
}

function topicNumber(topic: unknown) {
  const s = String(topic || "").trim();
  const match = s.match(/^(\d+)/);
  return match ? Number(match[1]) : 999;
}

function topicName(topic: unknown) {
  return String(topic || "")
    .toLowerCase()
    .replace(/^\d+[_\-\s]*/, "")
    .trim();
}

function difficultyNumber(value: unknown) {
  const n = Number(value);
  return Number.isFinite(n) ? n : 999;
}

function dbOrder(row: any) {
  const n = Number(row.display_order ?? row.original_index ?? 999999);
  return Number.isFinite(n) ? n : 999999;
}

function amcOriginalOrder(a: any, b: any) {
  const topicNoA = topicNumber(a.topic);
  const topicNoB = topicNumber(b.topic);

  if (topicNoA !== topicNoB) {
    return topicNoA - topicNoB;
  }

  const topicNameA = topicName(a.topic);
  const topicNameB = topicName(b.topic);

  if (topicNameA !== topicNameB) {
    return topicNameA.localeCompare(topicNameB);
  }

  const diffA = difficultyNumber(a.difficulty);
  const diffB = difficultyNumber(b.difficulty);

  if (diffA !== diffB) {
    return diffA - diffB;
  }

  return dbOrder(a) - dbOrder(b);
}

export async function GET(req: Request) {
  const access = await requireAMCAccess();
  if (!access.ok) return access.response;

  const { searchParams } = new URL(req.url);
  const exam = examFromPaper(searchParams.get("paper") || searchParams.get("exam"));

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
      amc_exams,
      amc_categories,
      amc_primary,
      amc_8,
      amc_10,
      amc_12
    `)
    .eq("is_active", true)
    .eq(exam.column, true)
    .order("display_order", { ascending: true });

  if (error) {
    console.error("AMC list load failed:", error);
    return json({ ok: false, error: error.message }, 500);
  }

  const sortedRows = [...(data || [])].sort(amcOriginalOrder);

  const cleaned = sortedRows.map((row: any, index: number) => ({
    qid: row.qid,

    // This is now the AMC view order:
    // topic -> difficulty -> original DB order
    display_order: index + 1,
    original_index: index + 1,
    view_order: index + 1,

    // Keep original DB order for debugging only
    db_display_order: row.display_order,
    db_original_index: row.original_index,

    kind: row.kind,
    paper: exam.paper,
    topic: row.topic,
    subtopic: row.subtopic,
    difficulty: row.difficulty,
    tags: row.tags,
    amc_exams: row.amc_exams,
    amc_categories: row.amc_categories,
    amc_primary: row.amc_primary,
  }));

  return json({
    ok: true,
    paper: exam.paper,
    total: cleaned.length,
    questions: cleaned,
    items: cleaned,
  });
}
