import { createClient } from "@supabase/supabase-js";
import { createHash } from "node:crypto";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const RELEASE_TOKEN = "esat_release_v2_20260827_R4mX8pL2qV7nC5tK9wB3dF6hJ1sY0aZu";
const BUCKET = "esat-recall-tests";
const MAX_BYTES = 4_250_000;
const ALLOWED = new Set([
  "esat-recall-2024-25-engineering.html.gz",
  "esat-recall-2024-25-physics-chemistry.html.gz",
  "esat-recall-2024-25-physics-biology.html.gz",
  "esat-recall-2024-25-maths2-chemistry.html.gz",
  "esat-recall-2024-25-maths2-biology.html.gz",
  "esat-recall-2024-25-chemistry-biology.html.gz",
]);

function reply(body: unknown, status = 200) {
  return Response.json(body, { status, headers: { "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" } });
}

export async function POST(request: Request) {
  if (request.headers.get("authorization") !== `Bearer ${RELEASE_TOKEN}`) return reply({ error: "Unauthorized" }, 401);
  const objectName = request.headers.get("x-esat-object")?.trim() ?? "";
  if (!ALLOWED.has(objectName)) return reply({ error: "Invalid object" }, 400);
  const bytes = new Uint8Array(await request.arrayBuffer());
  if (bytes.byteLength < 100_000 || bytes.byteLength > MAX_BYTES) return reply({ error: "Invalid size", bytes: bytes.byteLength }, 400);
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL ?? process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY ?? process.env.SUPABASE_SERVICE_KEY;
  if (!url || !key) return reply({ error: "Storage configuration unavailable" }, 500);
  const admin = createClient(url, key, { auth: { persistSession: false, autoRefreshToken: false } });
  const path = `tests/${objectName}`;
  const { error } = await admin.storage.from(BUCKET).upload(path, bytes, { contentType: "application/gzip", cacheControl: "3600", upsert: true });
  if (error) return reply({ error: error.message }, 500);
  return reply({ ok: true, path, bytes: bytes.byteLength, sha256: createHash("sha256").update(bytes).digest("hex") });
}

export function GET() {
  return new Response("Not found", { status: 404, headers: { "Cache-Control": "no-store" } });
}
