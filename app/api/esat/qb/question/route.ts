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

export async function GET(req: Request) {
  const access = await requireESATAccess();
  if (!access.ok) return access.response;

  const { searchParams } = new URL(req.url);
  const qid = searchParams.get("qid") || searchParams.get("id");
  const displayOrderRaw =
    searchParams.get("display_order") ||
    searchParams.get("original_index") ||
    searchParams.get("order");

  const supabase = adminClient();
  let lastError: any = null;

  for (const table of ESAT_TABLE_CANDIDATES) {
    if (qid) {
      let res = await supabase
        .from(table)
        .select("*")
        .eq("qid", qid)
        .maybeSingle();

      if (res.error && String(res.error.message || "").toLowerCase().includes("column")) {
        res = await supabase
          .from(table)
          .select("*")
          .eq("id", qid)
          .maybeSingle();
      }

      if (res.error) {
        lastError = res.error;
        continue;
      }

      if (res.data) {
        return json({
          ok: true,
          table,
          question: normaliseQuestion(res.data),
        });
      }
    }

    if (displayOrderRaw) {
      const displayOrder = Number(displayOrderRaw);

      if (!Number.isFinite(displayOrder) || displayOrder < 1) {
        return json({ ok: false, error: "Invalid display_order" }, 400);
      }

      const { data, error } = await supabase
        .from(table)
        .select("*")
        .limit(3000);

      if (error) {
        lastError = error;
        continue;
      }

      const sorted = cleanRows(data || []);
      const row = sorted[displayOrder - 1];

      if (row) {
        return json({
          ok: true,
          table,
          question: normaliseQuestion(row, displayOrder - 1),
        });
      }
    }
  }

  return json({
    ok: false,
    error: "Question not found",
    qid,
    display_order: displayOrderRaw,
    details: lastError?.message || String(lastError || ""),
  }, 404);
}
