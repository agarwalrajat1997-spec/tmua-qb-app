import { createClient } from "@supabase/supabase-js";
import { createHash, timingSafeEqual } from "node:crypto";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 60;

// Short-lived publication capability, limited to this exact approved workbook.
// The raw token is never stored in source. No other object can be read or changed.
const TOKEN_HASH = "7553aaa9a3db24353e1a0b7e3782c49e290144a6d926d2623e8786f4dee63fd5";
const EXPIRES_AT = Date.parse("2026-11-23T16:51:19Z");
const FILE_HASH = "faf3195ab4e52e273f3d5c9a648680fd1bf02625d84076c013f0f5014692795e";
const FILE_SIZE = 868011;
const FILENAME = "TMUA_Coordinate_Geometry_Notes_and_Practice.pdf";
const BUCKET = "tmua-class-homework";
const OBJECT_PATH = "2026-11-21-session-7/" + FILENAME;
const SESSION_ID = "3aa1704a-6154-4464-a340-f924387c873b";
const SESSION_START = "2026-11-21T11:30:00.000Z";

function json(data, status = 200) {
  return Response.json(data, {
    status,
    headers: { "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" },
  });
}

export async function POST(request) {
  if (Date.now() > EXPIRES_AT) return json({ error: "This publication capability has expired." }, 410);
  const target = new URL(request.url);
  if (target.hostname !== "apps.thrivingscholars.com") return json({ error: "Use the TMUA portal." }, 403);
  const supplied = request.headers.get("authorization") || "";
  if (!supplied.startsWith("Bearer ") || supplied.length > 200) return json({ error: "Publication authorization is required." }, 401);
  const tokenHash = createHash("sha256").update(supplied.slice(7)).digest();
  if (!timingSafeEqual(tokenHash, Buffer.from(TOKEN_HASH, "hex"))) return json({ error: "Invalid publication authorization." }, 403);
  const origin = request.headers.get("origin");
  if (origin && origin !== target.origin) return json({ error: "Invalid request origin." }, 403);
  if (request.headers.get("content-type")?.split(";")[0] !== "application/pdf") return json({ error: "A PDF is required." }, 415);
  if (request.headers.has("content-length") && Number(request.headers.get("content-length")) !== FILE_SIZE) return json({ error: "Use the approved workbook." }, 400);

  try {
    const reader = request.body?.getReader();
    if (!reader) return json({ error: "No file received." }, 400);
    const chunks = [];
    let size = 0;
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > FILE_SIZE) {
        await reader.cancel();
        return json({ error: "Use the approved workbook." }, 413);
      }
      chunks.push(Buffer.from(value));
    }
    const bytes = Buffer.concat(chunks);
    if (size !== FILE_SIZE || createHash("sha256").update(bytes).digest("hex") !== FILE_HASH) return json({ error: "The file does not match the approved workbook." }, 400);

    const url = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_SERVICE_KEY;
    if (!url || !key || new URL(url).origin !== "https://pnkzxzigpkvhlmhsmzdd.supabase.co") return json({ error: "Homework storage is unavailable." }, 503);
    const supabase = createClient(url, key, { auth: { persistSession: false, autoRefreshToken: false } });
    const session = await supabase.from("tmua_class_sessions").select("id,starts_at").eq("id", SESSION_ID).single();
    if (session.error || !session.data || new Date(session.data.starts_at).toISOString() !== SESSION_START) return json({ error: "The target session could not be verified." }, 409);
    const bucket = await supabase.storage.getBucket(BUCKET);
    if (bucket.error || !bucket.data || bucket.data.public) return json({ error: "Private homework storage could not be verified." }, 409);

    // Never overwrite any object, including an earlier successful publication.
    const uploaded = await supabase.storage.from(BUCKET).upload(OBJECT_PATH, bytes, { contentType: "application/pdf", cacheControl: "3600", upsert: false });
    const saved = await supabase.storage.from(BUCKET).download(OBJECT_PATH);
    if (saved.error || !saved.data) return json({ error: uploaded.error ? "The workbook could not be stored." : "The stored workbook could not be checked." }, 503);
    const savedBytes = new Uint8Array(await saved.data.arrayBuffer());
    const savedHash = createHash("sha256").update(savedBytes).digest("hex");
    if (savedBytes.byteLength !== FILE_SIZE || savedHash !== FILE_HASH) return json({ error: "The stored workbook did not match." }, 409);
    return json({ ok: true, size: savedBytes.byteLength, sha256: savedHash, pdfUrl: "/tmua-classes/homework/" + FILENAME });
  } catch {
    return json({ error: "Publication could not be completed." }, 503);
  }
}
