import { createClient } from "@supabase/supabase-js";
import { createHash } from "node:crypto";

function unavailable(status, message) {
  return Response.json({ error: message }, { status, headers: { "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" } });
}

// Call only from routes covered by the TMUA Classes entitlement gate.
export async function serveClassHomework({ filename, objectPath, size, sha256 }) {
  try {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_SERVICE_KEY;
    if (!url || !key) return unavailable(503, "Homework storage is unavailable.");
    const supabase = createClient(url, key, { auth: { persistSession: false, autoRefreshToken: false } });
    const { data, error } = await supabase.storage.from("tmua-class-homework").download(objectPath);
    if (error || !data) return unavailable(404, "This homework PDF has not been published yet.");
    const bytes = new Uint8Array(await data.arrayBuffer());
    if (bytes.byteLength !== size || createHash("sha256").update(bytes).digest("hex") !== sha256) return unavailable(503, "The homework file could not be verified.");
    return new Response(bytes, { headers: {
      "Content-Type": "application/pdf",
      "Content-Length": String(bytes.byteLength),
      "Content-Disposition": 'inline; filename="' + filename + '"',
      "Cache-Control": "private, no-store",
      "X-Content-Type-Options": "nosniff"
    } });
  } catch {
    return unavailable(503, "The homework file is temporarily unavailable.");
  }
}
