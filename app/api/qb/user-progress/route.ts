import { NextRequest } from "next/server";
import { supabaseServer } from "@/utils/supabase/server";

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
    data: { user },
  } = await supabase.auth.getUser();

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
    .limit(1);

  if (error) {
    console.error("Progress access check failed:", { email, product, error });
    return false;
  }

  return !!data && data.length > 0;
}

export async function GET(req: NextRequest) {
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
    .maybeSingle();

  if (error) {
    console.error("Load user progress failed:", error);
    return json({ ok: false, error: error.message }, 500);
  }

  return json({
    ok: true,
    user_id: user.id,
    email,
    product,
    key,
    data: data?.data || null,
    updated_at: data?.updated_at || null,
  });
}

export async function POST(req: NextRequest) {
  const { supabase, user, email } = await getAuthedUser();

  if (!user || !email) {
    return json({ ok: false, error: "Not signed in" }, 401);
  }

  const body = await req.json().catch(() => null);

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
