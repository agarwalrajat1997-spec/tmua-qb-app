import { createClient } from "@supabase/supabase-js";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 60;

const TOKEN = "esat_release_v5_20260827_N7qR3mV8xK5pT2cF9hL4wY6sD1jB0aZu";
const BUCKET = "esat-recall-tests";
const MAX_BYTES = 600_000;
const SLUGS = new Set([
  "esat-recall-2024-25-engineering",
  "esat-recall-2024-25-physics-chemistry",
  "esat-recall-2024-25-physics-biology",
  "esat-recall-2024-25-maths2-chemistry",
  "esat-recall-2024-25-maths2-biology",
  "esat-recall-2024-25-chemistry-biology",
]);

function reply(body: unknown, status = 200) {
  return Response.json(body, {
    status,
    headers: {
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
    },
  });
}

export async function POST(request: Request) {
  if (request.headers.get("authorization") !== `Bearer ${TOKEN}`) {
    return reply({ error: "Unauthorized" }, 401);
  }

  const slug = request.headers.get("x-esat-slug")?.trim() ?? "";
  const partName = request.headers.get("x-esat-part")?.trim() ?? "";
  if (!SLUGS.has(slug)) return reply({ error: "Invalid slug" }, 400);
  if (!(partName === "manifest.json" || /^part-\d{3}\.bin$/.test(partName))) {
    return reply({ error: "Invalid part name" }, 400);
  }

  const bytes = Buffer.from(await request.arrayBuffer());
  if (bytes.byteLength < 2 || bytes.byteLength > MAX_BYTES) {
    return reply({ error: "Invalid part size", bytes: bytes.byteLength }, 400);
  }

  const url = process.env.NEXT_PUBLIC_SUPABASE_URL ?? process.env.SUPABASE_URL;
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY ?? process.env.SUPABASE_SERVICE_KEY;
  if (!url || !serviceKey) return reply({ error: "Storage configuration unavailable" }, 500);

  const admin = createClient(url, serviceKey, {
    auth: { persistSession: false, autoRefreshToken: false },
  });
  const path = `staging/${slug}/${partName}`;
  const { error } = await admin.storage.from(BUCKET).upload(path, bytes, {
    contentType: partName === "manifest.json" ? "application/json" : "application/octet-stream",
    cacheControl: "3600",
    upsert: true,
  });
  if (error) return reply({ error: error.message }, 500);

  return reply({ ok: true, path, bytes: bytes.byteLength });
}

export function GET() {
  return new Response("Not found", {
    status: 404,
    headers: { "Cache-Control": "no-store" },
  });
}
