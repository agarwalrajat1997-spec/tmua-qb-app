import {
  ESAT_TABLE_CANDIDATES,
  adminClient,
  json,
  normaliseQuestion,
  requireESATAccess,
} from "../_server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

// TS_ESAT_STRICT_IDENTITY_V1
// Full ESAT questions must be loaded by a stable database identity.
// Positional display_order lookup is intentionally not supported.

const ESAT_QUESTION_COLUMNS = [
  "id",
  "qid",
  "original_qid",
  "display_order",
  "paper_question_number",
  "kind",
  "paper",
  "topic",
  "subtopic",
  "difficulty",
  "tags",
  "prompt_html",
  "options",
  "answer",
  "solution_html",
  "page_assets",
  "answer_verified",
  "shortcut_available",
  "nice_tip_html",
  "checker_flags",
  "is_active",
  "updated_at",
].join(",");

function looksLikeUuid(value: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(
    value
  );
}

function success(
  table: string,
  row: any,
  requestedIdentity: string
) {
  return json({
    ok: true,
    table,
    identity_lock: "qid-or-id",
    requested_identity: requestedIdentity,
    question: normaliseQuestion(row),
  });
}

export async function GET(req: Request) {
  const access = await requireESATAccess();

  if (!access.ok) {
    return access.response;
  }

  const { searchParams } = new URL(req.url);

  const identity = (
    searchParams.get("qid") ||
    searchParams.get("id") ||
    ""
  ).trim();

  if (!identity) {
    return json(
      {
        ok: false,
        code: "QID_REQUIRED",
        error:
          "A stable ESAT qid or id is required. Positional question lookup is disabled.",
      },
      400
    );
  }

  const supabase = adminClient();
  let lastError: any = null;

  for (const table of ESAT_TABLE_CANDIDATES) {
    const byQid = await supabase
      .from(table)
      .select(ESAT_QUESTION_COLUMNS)
      .eq("qid", identity)
      .eq("is_active", true)
      .maybeSingle();

    if (byQid.error) {
      lastError = byQid.error;
    } else if (byQid.data) {
      return success(table, byQid.data, identity);
    }

    // The list endpoint also supplies the UUID primary key.
    // Accepting it provides a second stable identity without
    // ever falling back to a list position.
    if (looksLikeUuid(identity)) {
      const byId = await supabase
        .from(table)
        .select(ESAT_QUESTION_COLUMNS)
        .eq("id", identity)
        .eq("is_active", true)
        .maybeSingle();

      if (byId.error) {
        lastError = byId.error;
      } else if (byId.data) {
        return success(table, byId.data, identity);
      }
    }
  }

  return json(
    {
      ok: false,
      code: "ESAT_IDENTITY_NOT_FOUND",
      error: "No active ESAT question matches the supplied identity.",
      requested_identity: identity,
      tried_tables: ESAT_TABLE_CANDIDATES,
      details: lastError?.message || String(lastError || ""),
    },
    404
  );
}