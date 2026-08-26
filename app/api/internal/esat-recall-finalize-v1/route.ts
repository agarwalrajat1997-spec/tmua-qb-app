import { createClient } from "@supabase/supabase-js";
import { createHash } from "node:crypto";
import { gunzipSync } from "node:zlib";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 60;

const TOKEN = "esat_finalize_v1_20260827_F8qN3mR7xK5pT2cV9hL4wY6sD1jB0aZu";
const BUCKET = "esat-recall-tests";
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

function digest(bytes: Buffer) {
  return createHash("sha256").update(bytes).digest("hex");
}

function isHash(value: unknown): value is string {
  return typeof value === "string" && /^[a-f0-9]{64}$/.test(value);
}

export async function POST(request: Request) {
  if (request.headers.get("authorization") !== `Bearer ${TOKEN}`) {
    return reply({ error: "Unauthorized" }, 401);
  }

  const slug = request.headers.get("x-esat-slug")?.trim() ?? "";
  if (!SLUGS.has(slug)) return reply({ error: "Invalid slug" }, 400);

  const url = process.env.NEXT_PUBLIC_SUPABASE_URL ?? process.env.SUPABASE_URL;
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY ?? process.env.SUPABASE_SERVICE_KEY;
  if (!url || !serviceKey) return reply({ error: "Storage configuration unavailable" }, 500);

  const admin = createClient(url, serviceKey, {
    auth: { persistSession: false, autoRefreshToken: false },
  });
  const manifestPath = `staging/${slug}/manifest.json`;
  const { data: manifestBlob, error: manifestError } = await admin.storage.from(BUCKET).download(manifestPath);
  if (manifestError || !manifestBlob) {
    return reply({ error: manifestError?.message ?? "Manifest missing" }, 500);
  }

  let manifest: any;
  try {
    manifest = JSON.parse(await manifestBlob.text());
  } catch {
    return reply({ error: "Invalid manifest JSON" }, 400);
  }

  if (
    manifest?.version !== 1 ||
    manifest?.slug !== slug ||
    manifest?.question_count !== 81 ||
    manifest?.section_size !== 27 ||
    !Array.isArray(manifest?.modules) ||
    manifest.modules.length !== 3 ||
    !Array.isArray(manifest?.parts) ||
    manifest.parts.length < 1 ||
    manifest.parts.length > 20 ||
    !Number.isInteger(manifest?.gzip_bytes) ||
    !Number.isInteger(manifest?.html_bytes) ||
    !isHash(manifest?.gzip_sha256) ||
    !isHash(manifest?.html_sha256)
  ) {
    return reply({ error: "Manifest validation failed" }, 400);
  }

  const chunks: Buffer[] = [];
  const cleanupPaths = [manifestPath];
  let totalBytes = 0;
  for (const part of manifest.parts) {
    if (
      typeof part?.name !== "string" ||
      !/^part-\d{3}\.bin$/.test(part.name) ||
      !Number.isInteger(part?.bytes) ||
      !isHash(part?.sha256)
    ) {
      return reply({ error: "Invalid part metadata" }, 400);
    }

    const partPath = `staging/${slug}/${part.name}`;
    const { data: partBlob, error: partError } = await admin.storage.from(BUCKET).download(partPath);
    if (partError || !partBlob) {
      return reply({ error: partError?.message ?? `Missing ${part.name}` }, 500);
    }
    const partBuffer = Buffer.from(await partBlob.arrayBuffer());
    if (partBuffer.byteLength !== part.bytes || digest(partBuffer) !== part.sha256) {
      return reply({ error: `Part checksum mismatch: ${part.name}` }, 400);
    }
    chunks.push(partBuffer);
    cleanupPaths.push(partPath);
    totalBytes += partBuffer.byteLength;
  }

  const gzipBuffer = Buffer.concat(chunks);
  if (
    gzipBuffer.byteLength !== totalBytes ||
    gzipBuffer.byteLength !== manifest.gzip_bytes ||
    digest(gzipBuffer) !== manifest.gzip_sha256
  ) {
    return reply({ error: "Compressed payload checksum mismatch" }, 400);
  }

  let htmlBuffer: Buffer;
  try {
    htmlBuffer = gunzipSync(gzipBuffer);
  } catch {
    return reply({ error: "Gzip decompression failed" }, 400);
  }
  if (
    htmlBuffer.byteLength !== manifest.html_bytes ||
    digest(htmlBuffer) !== manifest.html_sha256
  ) {
    return reply({ error: "HTML checksum mismatch" }, 400);
  }

  const html = htmlBuffer.toString("utf8");
  const requiredTokens = [
    "const questions",
    "correctAnswers",
    "SECTION_SIZE = 27",
    "SECTION_SECONDS = 40 * 60",
    "BREAK_SECONDS = 5 * 60",
    "esat-score-result-hook",
    "solutionPDF",
  ];
  if (!requiredTokens.every((token) => html.includes(token))) {
    return reply({ error: "HTML structural validation failed" }, 400);
  }

  const finalPath = `tests/${slug}.html.gz`;
  const { error: uploadError } = await admin.storage.from(BUCKET).upload(finalPath, gzipBuffer, {
    contentType: "application/gzip",
    cacheControl: "3600",
    upsert: true,
  });
  if (uploadError) return reply({ error: uploadError.message }, 500);

  await admin.storage.from(BUCKET).remove(cleanupPaths);

  return reply({
    ok: true,
    slug,
    path: finalPath,
    modules: manifest.modules,
    question_count: manifest.question_count,
    gzip_bytes: gzipBuffer.byteLength,
    gzip_sha256: manifest.gzip_sha256,
    html_bytes: htmlBuffer.byteLength,
    html_sha256: manifest.html_sha256,
  });
}

export function GET() {
  return new Response("Not found", {
    status: 404,
    headers: { "Cache-Control": "no-store" },
  });
}
