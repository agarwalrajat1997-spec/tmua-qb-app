import { createClient } from "@supabase/supabase-js";
import { createHash, timingSafeEqual } from "node:crypto";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 60;

// Short-lived publication capability, limited to this exact approved workbook.
// The raw token is never stored in source. No other object can be read or changed.
const TOKEN_HASH = "df237e616ba75912ee61ddae037d6043b2e807a9e4a6ed7c25c06d4484eb996f";
const EXPIRES_AT = Date.parse("2026-11-14T18:16:06Z");
const FILE_HASH = "6e2453369cefa54d986fa58d0916e5b309d2dbaa07991db44e2d802f2405e855";
const FILE_SIZE = 162983;
const FILENAME = "TMUA_Functions_and_Graphs_Notes_and_15_Questions.pdf";
const BUCKET = "tmua-class-homework";
const OBJECT_PATH = "2026-11-14-session-5/" + FILENAME;
const SESSION_ID = "7be98ab9-f054-4079-9aac-c33ea6475d5a";
const SESSION_START = "2026-11-14T11:30:00.000Z";

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
