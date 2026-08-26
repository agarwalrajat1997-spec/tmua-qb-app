import { createClient } from "@supabase/supabase-js";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 60;

const TOKEN = "esat_qa_v1_20260827_H8qR3nV7xK5pT2cF9mL4wY6sD1jB0aZu";
const QA_EMAIL = "esat-release-qa-20260827@thrivingscholars.com";
const QA_PASSWORD = "Esat-Release-QA-2026-08-27!9mR4";

function reply(body: unknown, status = 200) {
  return Response.json(body, { status, headers: { "Cache-Control": "no-store" } });
}

function adminClient() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL ?? process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY ?? process.env.SUPABASE_SERVICE_KEY;
  if (!url || !key) return null;
  return createClient(url, key, { auth: { persistSession: false, autoRefreshToken: false } });
}

function authorized(request: Request) {
  return request.headers.get("authorization") === `Bearer ${TOKEN}`;
}

export async function POST(request: Request) {
  if (!authorized(request)) return reply({ error: "Unauthorized" }, 401);
  const admin = adminClient();
  if (!admin) return reply({ error: "Server configuration unavailable" }, 500);

  const { data: listed, error: listError } = await admin.auth.admin.listUsers({ page: 1, perPage: 1000 });
  if (listError) return reply({ error: listError.message }, 500);
  for (const existing of listed.users) {
    if (existing.email?.toLowerCase() === QA_EMAIL.toLowerCase()) {
      await admin.from("esat_practice_test_attempts").delete().eq("user_id", existing.id);
      await admin.from("student_access").delete().eq("user_id", existing.id);
      await admin.auth.admin.deleteUser(existing.id);
    }
  }

  const { data, error } = await admin.auth.admin.createUser({
    email: QA_EMAIL,
    password: QA_PASSWORD,
    email_confirm: true,
    user_metadata: { release_verifier: "esat-recall-2024-25" },
  });
  if (error || !data.user) return reply({ error: error?.message ?? "User creation failed" }, 500);

  const expires = new Date(Date.now() + 60 * 60 * 1000).toISOString();
  const { error: accessError } = await admin.from("student_access").insert({
    user_id: data.user.id,
    product: "esat-practice-tests",
    approved: true,
    expires_at: expires,
  });
  if (accessError) {
    await admin.auth.admin.deleteUser(data.user.id);
    return reply({ error: accessError.message }, 500);
  }

  return reply({ ok: true, user_id: data.user.id, email: QA_EMAIL, password: QA_PASSWORD, expires_at: expires });
}

export async function DELETE(request: Request) {
  if (!authorized(request)) return reply({ error: "Unauthorized" }, 401);
  const admin = adminClient();
  if (!admin) return reply({ error: "Server configuration unavailable" }, 500);
  const userId = request.headers.get("x-esat-user-id")?.trim() ?? "";
  if (!/^[0-9a-f-]{36}$/i.test(userId)) return reply({ error: "Invalid user id" }, 400);

  await admin.from("esat_practice_test_attempts").delete().eq("user_id", userId);
  await admin.from("student_access").delete().eq("user_id", userId);
  const { error } = await admin.auth.admin.deleteUser(userId);
  if (error && !error.message.toLowerCase().includes("not found")) return reply({ error: error.message }, 500);
  return reply({ ok: true, deleted_user_id: userId });
}

export function GET() {
  return new Response("Not found", { status: 404, headers: { "Cache-Control": "no-store" } });
}
