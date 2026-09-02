import { adminClient, json } from "../../../_server";
import { requireSATAdmin } from "../../_server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const ALLOWED_STATUSES = new Set([
  "open",
  "reviewing",
  "resolved",
  "dismissed",
]);

function isRecord(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === "object" && !Array.isArray(value);
}

export async function PATCH(
  req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const access = await requireSATAdmin();
  if (!access.ok) return access.response;

  const { id } = await params;
  const body: unknown = await req.json().catch(() => null);
  const status = isRecord(body) ? String(body.status || "").trim() : "";

  if (!id || !ALLOWED_STATUSES.has(status)) {
    return json({ ok: false, error: "Invalid report status update" }, 400);
  }

  const supabase = adminClient();
  const { data: existing, error: loadError } = await supabase
    .from("sat_question_reports")
    .select("id,context")
    .eq("id", id)
    .maybeSingle();

  if (loadError) {
    console.error("SAT admin report lookup failed:", loadError);
    return json({ ok: false, error: "Could not load the report" }, 500);
  }
  if (!existing) return json({ ok: false, error: "Report not found" }, 404);

  const now = new Date().toISOString();
  const context = isRecord(existing.context) ? existing.context : {};
  const previousHistory = Array.isArray(context.moderation_history)
    ? context.moderation_history.filter(isRecord).slice(-49)
    : [];
  const nextContext = {
    ...context,
    moderation_history: [
      ...previousHistory,
      { status, updated_at: now, updated_by: access.email },
    ],
  };

  const { data, error } = await supabase
    .from("sat_question_reports")
    .update({
      status,
      resolved_at:
        status === "resolved" || status === "dismissed" ? now : null,
      context: nextContext,
    })
    .eq("id", id)
    .select("id,status,resolved_at,context")
    .maybeSingle();

  if (error) {
    console.error("SAT admin report update failed:", error);
    return json({ ok: false, error: "Could not update the report" }, 500);
  }
  if (!data) return json({ ok: false, error: "Report not found" }, 404);

  return json({ ok: true, report: data });
}
