import { createClient } from "@supabase/supabase-js";
import { createHash } from "node:crypto";
import { gunzipSync } from "node:zlib";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 60;

const RELEASE_TOKEN = "esat_release_v3_20260827_B8qR2mV7xK4pN9cF5hL1tY6wS3dJ0aZu";
const BUCKET = "esat-recall-tests";
const MAX_CHUNK_BYTES = 600_000;
const SLUGS = new Set([
  "esat-recall-2024-25-engineering",
  "esat-recall-2024-25-physics-chemistry",
  "esat-recall-2024-25-physics-biology",
  "esat-recall-2024-25-maths2-chemistry",
  "esat-recall-2024-25-maths2-biology",
  "esat-recall-2024-25-chemistry-biology",
]);

type Part = { name: string; bytes: number; sha256: string };
type Manifest = {
  version: number;
  slug: string;
  question_count: number;
  section_size: number;
  modules: string[];
  parts: Part[];
  gzip_bytes: number;
  gzip_sha256: string;
  html_bytes: number;
  html_sha256: string;
};

function reply(body: unknown, status = 200) {
  return Response.json(body, {
    status,
    headers: { "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" },
  });
}

function adminClient() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL ?? process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY ?? process.env.SUPABASE_SERVICE_KEY;
  if (!url || !key) return null;
  return createClient(url, key, { auth: { persistSession: false, autoRefreshToken: false } });
}

function sha256(bytes: Uint8Array) {
  return createHash("sha256").update(bytes).digest("hex");
}

function validHash(value: unknown): value is string {
  return typeof value === "string" && /^[a-f0-9]{64}$/.test(value);
}

export async function POST(request: Request) {
  if (request.headers.get("authorization") !== `Bearer ${RELEASE_TOKEN}`) {
    return reply({ error: "Unauthorized" }, 401);
  }
  const admin = adminClient();
  if (!admin) return reply({ error: "Storage configuration unavailable" }, 500);

  const action = request.headers.get("x-esat-action") ?? "part";
  const slug = request.headers.get("x-esat-slug")?.trim() ?? "";
  if (!SLUGS.has(slug)) return reply({ error: "Invalid slug" }, 400);

  if (action === "part") {
    const name = request.headers.get("x-esat-part")?.trim() ?? "";
    if (!(name === "manifest.json" || /^part-\d{3}\.bin$/.test(name))) {
      return reply({ error: "Invalid part name" }, 400);
    }
    const bytes = new Uint8Array(await request.arrayBuffer());
    if (bytes.byteLength < 2 || bytes.byteLength > MAX_CHUNK_BYTES) {
      return reply({ error: "Invalid part size", bytes: bytes.byteLength }, 400);
    }
    const path = `staging/${slug}/${name}`;
    const contentType = name === "manifest.json" ? "application/json" : "application/octet-stream";
    const { error } = await admin.storage.from(BUCKET).upload(path, bytes, {
      contentType,
      cacheControl: "3600",
      upsert: true,
    });
    if (error) return reply({ error: error.message }, 500);
    return reply({ ok: true, path, bytes: bytes.byteLength, sha256: sha256(bytes) });
  }

  if (action !== "finalize") return reply({ error: "Invalid action" }, 400);

  const manifestPath = `staging/${slug}/manifest.json`;
  const { data: manifestBlob, error: manifestError } = await admin.storage.from(BUCKET).download(manifestPath);
  if (manifestError || !manifestBlob) return reply({ error: manifestError?.message ?? "Manifest missing" }, 500);

  let manifest: Manifest;
  try {
    manifest = JSON.parse(await manifestBlob.text()) as Manifest;
  } catch {
    return reply({ error: "Invalid manifest JSON" }, 400);
  }
  if (
    manifest.version !== 1 || manifest.slug !== slug || manifest.question_count !== 81 ||
    manifest.section_size !== 27 || !Array.isArray(manifest.modules) || manifest.modules.length !== 3 ||
    !Array.isArray(manifest.parts) || manifest.parts.length < 1 || manifest.parts.length > 20 ||
    !validHash(manifest.gzip_sha256) || !validHash(manifest.html_sha256) ||
    !Number.isInteger(manifest.gzip_bytes) || !Number.isInteger(manifest.html_bytes)
  ) return reply({ error: "Manifest validation failed" }, 400);

  const chunks: Uint8Array[] = [];
  const cleanup = [manifestPath];
  let total = 0;
  for (const part of manifest.parts) {
    if (!/^part-\d{3}\.bin$/.test(part.name) || !Number.isInteger(part.bytes) || !validHash(part.sha256)) {
      return reply({ error: `Invalid part metadata: ${part.name}` }, 400);
    }
    const path = `staging/${slug}/${part.name}`;
    const { data: blob, error } = await admin.storage.from(BUCKET).download(path);
    if (error || !blob) return reply({ error: error?.message ?? `Missing ${part.name}` }, 500);
    const bytes = new Uint8Array(await blob.arrayBuffer());
    if (bytes.byteLength !== part.bytes || sha256(bytes) !== part.sha256) {
      return reply({ error: `Part checksum mismatch: ${part.name}` }, 400);
    }
    chunks.push(bytes);
    cleanup.push(path);
    total += bytes.byteLength;
  }

  if (total !== manifest.gzip_bytes) return reply({ error: "Gzip byte count mismatch" }, 400);
  const gzipBytes = new Uint8Array(total);
  let offset = 0;
  for (const chunk of chunks) { gzipBytes.set(chunk, offset); offset += chunk.byteLength; }
  if (sha256(gzipBytes) !== manifest.gzip_sha256) return reply({ error: "Gzip checksum mismatch" }, 400);

  let htmlBytes: Uint8Array;
  try { htmlBytes = new Uint8Array(gunzipSync(gzipBytes)); }
  catch { return reply({ error: "Gzip decompression failed" }, 400); }
  if (htmlBytes.byteLength !== manifest.html_bytes || sha256(htmlBytes) !== manifest.html_sha256) {
    return reply({ error: "HTML checksum mismatch" }, 400);
  }
  const html = new TextDecoder().decode(htmlBytes);
  const required = [
    "correctAnswers", "SECTION_SIZE", "SECTION_SECONDS", "BREAK_SECONDS",
    "esat-score-result-hook", "solutionPDF", "81",
  ];
  if (!required.every((token) => html.includes(token))) return reply({ error: "HTML structural validation failed" }, 400);

  const finalPath = `tests/${slug}.html.gz`;
  const { error: uploadError } = await admin.storage.from(BUCKET).upload(finalPath, gzipBytes, {
    contentType: "application/gzip",
    cacheControl: "3600",
    upsert: true,
  });
  if (uploadError) return reply({ error: uploadError.message }, 500);
  await admin.storage.from(BUCKET).remove(cleanup);

  return reply({
    ok: true,
    slug,
    path: finalPath,
    gzip_bytes: gzipBytes.byteLength,
    gzip_sha256: manifest.gzip_sha256,
    html_bytes: htmlBytes.byteLength,
    html_sha256: manifest.html_sha256,
    question_count: manifest.question_count,
    modules: manifest.modules,
  });
}

export function GET() {
  return new Response("Not found", { status: 404, headers: { "Cache-Control": "no-store" } });
}
