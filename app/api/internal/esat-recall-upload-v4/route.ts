import { createClient } from "@supabase/supabase-js";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const TOKEN = "esat_release_v4_20260827_Q6vN2mR8xK4pT9cF5hL1wY7sD3jB0aZu";
const BUCKET = "esat-recall-tests";
const SLUGS = new Set([
  "esat-recall-2024-25-engineering",
  "esat-recall-2024-25-physics-chemistry",
  "esat-recall-2024-25-physics-biology",
  "esat-recall-2024-25-maths2-chemistry",
  "esat-recall-2024-25-maths2-biology",
  "esat-recall-2024-25-chemistry-biology",
]);

function response(body: unknown, status = 200) {
  return Response.json(body, { status, headers: { "Cache-Control": "no-store" } });
}

export async function POST(request: Request) {
  if (request.headers.get("authorization") !== `Bearer ${TOKEN}`) return response({ error: "Unauthorized" }, 401);
  const slug = request.headers.get("x-esat-slug")?.trim() ?? "";
  const name = request.headers.get("x-esat-part")?.trim() ?? "";
  if (!SLUGS.has(slug)) return response({ error: "Invalid slug" }, 400);
  if (!(name === "manifest.json" || /^part-\d{3}\.bin$/.test(name))) return response({ error: "Invalid part" }, 400);
  const bytes = new Uint8Array(await request.arrayBuffer());
  if (bytes.byteLength < 2 || bytes.byteLength > 600000) return response({ error: "Invalid size", bytes: bytes.byteLength }, 400);
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL ?? process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY ?? process.env.SUPABASE_SERVICE_KEY;
  if (!url || !key) return response({ error: "Storage configuration unavailable" }, 500);
  const admin = createClient(url, key, { auth: { persistSession: false, autoRefreshToken: false } });
  const path = `staging/${slug}/${name}`;
  const { error } = await admin.storage.from(BUCKET).upload(path, bytes, {
    contentType: name === "manifest.json" ? "application/json" : "application/octet-stream",
    cacheControl: "3600",
    upsert: true,
  });
  if (error) return response({ error: error.message }, 500);
  return response({ ok: true, path, bytes: bytes.byteLength });
}

export function GET() {
  return new Response("Not found", { status: 404, headers: { "Cache-Control": "no-store" } });
}
