import { createClient } from "@supabase/supabase-js";
import { createHash } from "node:crypto";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 60;

const TOKEN = "esat_bundle_v1_20260827_M8qR3nV7xK5pT2cF9hL4wY6sD1jB0aZu";
const BUCKET = "esat-recall-tests";
const PREFIX = "release/esat-recall-2024-25";
const MAX_PART_BYTES = 600_000;

function reply(body: unknown, status = 200) {
  return Response.json(body, {
    status,
    headers: {
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
    },
  });
}

function hash(bytes: Buffer) {
  return createHash("sha256").update(bytes).digest("hex");
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
  const name = request.headers.get("x-esat-part")?.trim() ?? "";
  if (!(name === "manifest.json" || /^part-\d{3}\.bin$/.test(name))) {
    return reply({ error: "Invalid part name" }, 400);
  }
  const bytes = Buffer.from(await request.arrayBuffer());
  if (bytes.byteLength < 2 || bytes.byteLength > MAX_PART_BYTES) {
    return reply({ error: "Invalid part size", bytes: bytes.byteLength }, 400);
  }
  const admin = adminClient();
  if (!admin) return reply({ error: "Storage configuration unavailable" }, 500);
  const path = `${PREFIX}/${name}`;
  const { error } = await admin.storage.from(BUCKET).upload(path, bytes, {
    contentType: name === "manifest.json" ? "application/json" : "application/octet-stream",
    cacheControl: "3600",
    upsert: true,
  });
  if (error) return reply({ error: error.message }, 500);
  return reply({ ok: true, path, bytes: bytes.byteLength, sha256: hash(bytes) });
}

export async function GET(request: Request) {
  if (!authorized(request)) return reply({ error: "Unauthorized" }, 401);
  const admin = adminClient();
  if (!admin) return reply({ error: "Storage configuration unavailable" }, 500);

  const { data: manifestBlob, error: manifestError } = await admin.storage
    .from(BUCKET)
    .download(`${PREFIX}/manifest.json`);
  if (manifestError || !manifestBlob) return reply({ error: manifestError?.message ?? "Manifest missing" }, 500);

  let manifest: any;
  try { manifest = JSON.parse(await manifestBlob.text()); }
  catch { return reply({ error: "Invalid manifest" }, 400); }
  if (
    manifest?.version !== 1 ||
    manifest?.release !== "esat-recall-2024-25-six-tests" ||
    !Array.isArray(manifest?.parts) ||
    manifest.parts.length < 1 ||
    manifest.parts.length > 20 ||
    !Number.isInteger(manifest?.bytes) ||
    typeof manifest?.sha256 !== "string"
  ) return reply({ error: "Manifest validation failed" }, 400);

  const chunks: Buffer[] = [];
  let total = 0;
  for (const part of manifest.parts) {
    if (
      typeof part?.name !== "string" ||
      !/^part-\d{3}\.bin$/.test(part.name) ||
      !Number.isInteger(part?.bytes) ||
      typeof part?.sha256 !== "string"
    ) return reply({ error: "Invalid part metadata" }, 400);
    const { data: blob, error } = await admin.storage.from(BUCKET).download(`${PREFIX}/${part.name}`);
    if (error || !blob) return reply({ error: error?.message ?? `Missing ${part.name}` }, 500);
    const bytes = Buffer.from(await blob.arrayBuffer());
    if (bytes.byteLength !== part.bytes || hash(bytes) !== part.sha256) {
      return reply({ error: `Checksum mismatch: ${part.name}` }, 400);
    }
    chunks.push(bytes);
    total += bytes.byteLength;
  }

  const bundle = Buffer.concat(chunks);
  if (bundle.byteLength !== total || bundle.byteLength !== manifest.bytes || hash(bundle) !== manifest.sha256) {
    return reply({ error: "Bundle checksum mismatch" }, 400);
  }

  return new Response(bundle, {
    status: 200,
    headers: {
      "Content-Type": "application/gzip",
      "Content-Disposition": "attachment; filename=\"esat-final-release-bundle.tar.gz\"",
      "Content-Length": String(bundle.byteLength),
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
    },
  });
}
