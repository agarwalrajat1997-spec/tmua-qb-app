import { createClient } from "@supabase/supabase-js";
import { createHash } from "node:crypto";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 30;

// /tmua-classes/:path* is protected by the existing proxy.ts class entitlement gate.
// Storage stays private; neither a public object URL nor service credentials leave the server.
const NAME = "TMUA_Quantifiers_Conditions_30_Questions.pdf";
const PATH = "2026-11-01-session-2/" + NAME;
const HASH = "baa34d611150514b804de461ad9ab3835457d02230a2952333e1bb2d6aa46428";

function unavailable(status, message) {
  return Response.json({ error: message }, { status, headers: { "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" } });
}

export async function GET() {
  try {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_SERVICE_KEY;
    if (!url || !key) return unavailable(503, "Homework storage is unavailable.");
    const supabase = createClient(url, key, { auth: { persistSession: false, autoRefreshToken: false } });
    const { data, error } = await supabase.storage.from("tmua-class-homework").download(PATH);
    if (error || !data) return unavailable(404, "This homework PDF has not been published yet.");
    const bytes = new Uint8Array(await data.arrayBuffer());
    if (bytes.byteLength !== 855748 || createHash("sha256").update(bytes).digest("hex") !== HASH) return unavailable(503, "The homework file could not be verified.");
    return new Response(bytes, { headers: {
      "Content-Type": "application/pdf",
      "Content-Length": String(bytes.byteLength),
      "Content-Disposition": 'inline; filename="' + NAME + '"',
      "Cache-Control": "private, no-store",
      "X-Content-Type-Options": "nosniff"
    } });
  } catch {
    return unavailable(503, "The homework file is temporarily unavailable.");
  }
}
