import { NextRequest } from "next/server";
import { supabaseServer } from "@/utils/supabase/server";
import { compactProgressState, progressStateFromEnvelope } from "@/lib/qb/compact-progress";
import { isMissingSession, withServiceTimeout } from "@/lib/auth/service-recovery";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

function json(data: unknown, status = 200) {
  return Response.json(data, {
    status,
    headers: {
      "Cache-Control": "no-store, no-cache, must-revalidate",
    },
  });
}

const ALLOWED_PRODUCTS = new Set([
  "tmua-question-bank",
  "esat-question-bank",
  "amc-question-bank",
  "sat-question-bank",
]);

async function getAuthedUser() {
  const supabase = await supabaseServer();

  const {
    data: { user }, error,
  } = await withServiceTimeout(supabase.auth.getUser());
  if (error && !isMissingSession(error)) throw new Error("Authentication service unavailable");

  if (!user || !user.email) {
    return { supabase, user: null, email: null };
  }

  return {
    supabase,
    user,
    email: user.email.toLowerCase(),
  };
}

async function hasProductAccess(
  supabase: Awaited<ReturnType<typeof supabaseServer>>,
  email: string,
  product: string
) {
  const nowIso = new Date().toISOString();

  const { data, error } = await supabase
    .from("student_access")
    .select("email, product, approved, expires_at")
    .ilike("email", email)
    .eq("product", product)
    .eq("approved", true)
    .or(`expires_at.is.null,expires_at.gt.${nowIso}`)
    .limit(1)
    .retry(false);

  if (error) {
    console.error("Progress access check failed:", { email, product, error });
    throw new Error("Access service unavailable");
  }

  return !!data && data.length > 0;
}

async function getProgress(req: NextRequest) {
  const { supabase, user, email } = await getAuthedUser();

  if (!user || !email) {
    return json({ ok: false, error: "Not signed in" }, 401);
  }

  const { searchParams } = new URL(req.url);
  const product = searchParams.get("product") || "";
  const key = searchParams.get("key") || "app_state";

  if (!ALLOWED_PRODUCTS.has(product)) {
    return json({ ok: false, error: "Invalid product" }, 400);
  }

  const allowed = await hasProductAccess(supabase, email, product);

  if (!allowed) {
    return json({ ok: false, error: "No access for this product" }, 403);
  }

  const { data, error } = await supabase
    .from("user_progress")
    .select("user_id, email, product, key, data, updated_at")
    .eq("user_id", user.id)
    .eq("product", product)
    .eq("key", key)
    .maybeSingle()
    .retry(false);

  if (error) {
    console.error("Load user progress failed:", error);
    return json({ ok: false, error: error.message }, 500);
  }

  let envelope = data?.data || null;
  if (envelope && ["tmua-question-bank", "esat-question-bank"].includes(product) && key === "app_state") {
    const parsed = progressStateFromEnvelope(envelope);
    envelope = { version: 2, storage_key: envelope.storage_key, parsed };
    // Older open tabs still expect raw; v2 clients receive only one compact copy.
    if (searchParams.get("format") !== "compact-v2") envelope.raw = JSON.stringify(parsed);
  }
  return json({
    ok: true,
    user_id: user.id,
    email,
    product,
    key,
    data: envelope,
    updated_at: data?.updated_at || null,
  });
}

async function postProgress(req: NextRequest) {
  const { supabase, user, email } = await getAuthedUser();

  if (!user || !email) {
    return json({ ok: false, error: "Not signed in" }, 401);
  }

  const body = await req.json().catch(() => null);

  // An offline write belongs to the account that created it, even if another
  // person has since signed in on this browser. Legacy clients omit this field.
  if (body?.expected_user_id !== undefined && body.expected_user_id !== user.id) {
    return json({ ok: false, error: "ACCOUNT_CHANGED", code: "ACCOUNT_CHANGED" }, 409);
  }

  const product = String(body?.product || "");
  const key = String(body?.key || "app_state");
  const data = body?.data ?? null;

  if (!ALLOWED_PRODUCTS.has(product)) {
    return json({ ok: false, error: "Invalid product" }, 400);
  }

  const allowed = await hasProductAccess(supabase, email, product);

  if (!allowed) {
    return json({ ok: false, error: "No access for this product" }, 403);
  }

  if (["tmua-question-bank", "esat-question-bank"].includes(product) && key === "app_state") {
    let patch;
    try {
      patch = body?.version === 2 ? compactProgressState(body.patch) : progressStateFromEnvelope(data);
      if (JSON.stringify(patch).length > 1_000_000) return json({ ok: false, error: "Progress update too large" }, 413);
    } catch {
      return json({ ok: false, error: "Invalid progress state" }, 400);
    }
    const storageKey = product === "tmua-question-bank" ? "ts_tmua_supabase_exact_ui_v4" : "ts_esat_supabase_exact_ui_v1";
    const { data: updated, error } = await supabase.rpc("save_qb_app_state_v2", {
      p_product: product, p_patch: patch, p_storage_key: storageKey,
    });
    if (error) throw new Error("Progress save temporarily unavailable");
    return json({ ok: true, saved: { user_id: user.id, product, key, updated_at: updated } });
  }

  if (data === null || typeof data !== "object") {
    return json({ ok: false, error: "Missing progress data object" }, 400);
  }

  const payload = {
    user_id: user.id,
    email,
    product,
    key,
    data,
    updated_at: new Date().toISOString(),
  };

  const { data: saved, error } = await supabase
    .from("user_progress")
    .upsert(payload, {
      onConflict: "user_id,product,key",
    })
    .select("user_id, email, product, key, updated_at")
    .single();

  if (error) {
    console.error("Save user progress failed:", error);
    return json({ ok: false, error: error.message }, 500);
  }

  return json({
    ok: true,
    saved,
  });
}

export async function GET(req: NextRequest) {
  try { return await getProgress(req); }
  catch (error) { console.error("Progress service unavailable", error); return unavailable(); }
}

export async function POST(req: NextRequest) {
  try { return await postProgress(req); }
  catch (error) { console.error("Progress service unavailable", error); return unavailable(); }
}

function unavailable() {
  return Response.json({ ok: false, error: "Progress is temporarily unavailable. Your local work is retained; please retry." },
    { status: 503, headers: { "Cache-Control": "no-store", "Retry-After": "30" } });
}
