import { createClient } from "@supabase/supabase-js";
import { createHash, randomBytes, timingSafeEqual } from "node:crypto";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 60;

// A narrowly scoped publication capability: one exact, user-approved workbook.
// The upload secret is never included in the page/source; only its hash is stored.
const TOKEN_HASH = "52a92e3ea5acf7840450e3e86cd81b451dcf38b0b01ce77e2f060835ae5ccc51";
const EXPIRES_AT = Date.parse("2026-11-10T23:59:59Z");
const FILE_HASH = "baa34d611150514b804de461ad9ab3835457d02230a2952333e1bb2d6aa46428";
const FILE_SIZE = 855748;
const FILENAME = "TMUA_Quantifiers_Conditions_30_Questions.pdf";
const BUCKET = "tmua-class-homework";
const OBJECT_PATH = "2026-11-01-session-2/" + FILENAME;
const PDF_PATH = "/api/tmua/homework/session-2.pdf";
const SESSION_ID = "286c67d0-2bc6-4029-939a-ecacf2605a47";
const SESSION_START = "2026-11-01T11:30:00.000Z";
const LINK = "[Homework: Logic & Quantifiers - 30 Questions](" + PDF_PATH + ")";
const HOMEWORK_NOTE = "Session 2 homework: complete Questions 1–30. Attempt the questions before checking the worked solutions at the back.";

function json(data, status = 200) {
  return Response.json(data, { status, headers: { "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" } });
}

function projectUrl() {
  const value = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
  if (!value) throw new Error("Storage configuration unavailable");
  return value.replace(/\/$/, "");
}

function adminClient() {
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_SERVICE_KEY;
  if (!key) throw new Error("Storage configuration unavailable");
  return createClient(projectUrl(), key, { auth: { persistSession: false, autoRefreshToken: false } });
}

function uploadPage() {
  const nonce = randomBytes(18).toString("base64");
  const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Publish Session 2 Homework | Thriving Scholars</title><style>body{margin:0;background:#fffaf0;color:#25211f;font:16px/1.6 system-ui,sans-serif}main{max-width:650px;margin:8vh auto;padding:32px;background:white;border:1px solid #eee0c4;border-radius:16px}.brand{font-size:13px;font-weight:800;letter-spacing:.12em;color:#861c2b}h1{font-size:28px;line-height:1.2}label{display:block;font-weight:700;margin:24px 0 8px}input{max-width:100%;font:inherit}button{display:block;margin:24px 0 12px;padding:12px 20px;background:#861c2b;color:white;border:0;border-radius:8px;font:700 16px system-ui;cursor:pointer}button:disabled{opacity:.5;cursor:default}.small{font-size:14px;color:#625e58}#status{white-space:pre-wrap}a{color:#861c2b}#links[hidden]{display:none}@media(max-width:720px){main{margin:20px 12px;padding:24px}}</style></head><body><main><div class="brand">THRIVING SCHOLARS</div><h1>Publish Session 2 homework</h1><p><strong>Paper 2: Logic &amp; Quantifiers</strong><br>Sunday 1 November 2026 · 11:30 am UK</p><p>Select the original 30-question PDF. Publishing will add its download button to this session’s Homework section. The workbook and solutions are kept unchanged.</p><form id="form"><label for="file">TMUA_Quantifiers_Conditions_30_Questions (1).pdf</label><input id="file" type="file" accept="application/pdf,.pdf" required><button id="publish" type="submit" disabled>Publish homework</button></form><p id="status" role="status" aria-live="polite"></p><p id="links" hidden><a href="${PDF_PATH}" target="_blank" rel="noopener">Open published PDF</a> · <a href="/tmua-classes/index.html#homework-heading">View class homework</a></p><p class="small">This private upload link accepts only the exact workbook supplied to ChatGPT. It expires after 10 November 2026. The student PDF link does not expire.</p></main><script nonce="${nonce}">const token=new URLSearchParams(location.hash.slice(1)).get('token')||'';history.replaceState(null,'',location.pathname+location.search);const form=document.getElementById('form'),button=document.getElementById('publish'),status=document.getElementById('status');button.disabled=!token;if(!token)status.textContent='Open the private upload link provided in ChatGPT to enable publishing.';form.addEventListener('submit',async(event)=>{event.preventDefault();const file=document.getElementById('file').files[0];if(!file)return;button.disabled=true;try{if(file.size!==${FILE_SIZE})throw new Error('Please select the original 30-question PDF supplied in the chat.');const bytes=await file.arrayBuffer();const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');if(digest!=='${FILE_HASH}')throw new Error('This is a different file. Select the original TMUA Quantifiers & Conditions 30 Questions PDF.');status.textContent='Publishing your workbook…';const response=await fetch('${PDF_PATH}',{method:'POST',headers:{'Content-Type':'application/pdf','Authorization':'Bearer '+token},body:bytes});const result=await response.json();if(!response.ok)throw new Error(result.error||'Publication failed. Please retry.');status.textContent='Published. The PDF is now linked under Session 2 homework.';document.getElementById('links').hidden=false;button.textContent='Published';}catch(error){status.textContent=error.message||'Could not publish. Please retry.';button.disabled=false;}});</script></body></html>`;
  return new Response(html, { headers: {
    "Content-Type": "text/html; charset=utf-8",
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; script-src 'nonce-" + nonce + "'; connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
  } });
}

export async function GET(request) {
  if (new URL(request.url).searchParams.get("upload") === "1") return uploadPage();
  try {
    const response = await fetch(projectUrl() + "/storage/v1/object/public/" + BUCKET + "/" + OBJECT_PATH, { cache: "no-store", signal: AbortSignal.timeout(15000) });
    if (!response.ok) return json({ error: "This homework PDF has not been published yet." }, response.status === 404 || response.status === 400 ? 404 : 503);
    return new Response(response.body, { headers: {
      "Content-Type": "application/pdf",
      "Content-Disposition": 'inline; filename="' + FILENAME + '"',
      "Cache-Control": "public, max-age=3600",
      "X-Content-Type-Options": "nosniff"
    } });
  } catch {
    return json({ error: "The homework file is temporarily unavailable." }, 503);
  }
}

export async function POST(request) {
  if (Date.now() > EXPIRES_AT) return json({ error: "This upload link has expired." }, 410);
  const supplied = request.headers.get("authorization") || "";
  if (!supplied.startsWith("Bearer ") || supplied.length > 200) return json({ error: "A private upload link is required." }, 401);
  const hash = createHash("sha256").update(supplied.slice(7)).digest();
  if (!timingSafeEqual(hash, Buffer.from(TOKEN_HASH, "hex"))) return json({ error: "Invalid upload link." }, 403);
  const origin = request.headers.get("origin");
  if (origin && origin !== new URL(request.url).origin) return json({ error: "Upload from the provided page." }, 403);
  if (request.headers.get("content-type")?.split(";")[0] !== "application/pdf") return json({ error: "A PDF is required." }, 415);
  if (request.headers.has("content-length") && Number(request.headers.get("content-length")) !== FILE_SIZE) return json({ error: "Select the original workbook." }, 400);

  try {
    const reader = request.body?.getReader();
    if (!reader) return json({ error: "No file received." }, 400);
    const chunks = [];
    let size = 0;
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > FILE_SIZE) { await reader.cancel(); return json({ error: "Select the original workbook." }, 413); }
      chunks.push(Buffer.from(value));
    }
    const bytes = Buffer.concat(chunks);
    if (size !== FILE_SIZE || createHash("sha256").update(bytes).digest("hex") !== FILE_HASH) return json({ error: "This is not the original approved workbook." }, 400);

    const supabase = adminClient();
    const { data: session, error: sessionError } = await supabase.from("tmua_class_sessions").select("id,starts_at,description").eq("id", SESSION_ID).single();
    if (sessionError || !session || new Date(session.starts_at).toISOString() !== SESSION_START) return json({ error: "The session could not be verified. No homework link was changed." }, 409);

    const { data: bucket } = await supabase.storage.getBucket(BUCKET);
    if (!bucket) {
      const { error } = await supabase.storage.createBucket(BUCKET, { public: true, fileSizeLimit: 1048576, allowedMimeTypes: ["application/pdf"] });
      if (error) {
        const check = await supabase.storage.getBucket(BUCKET);
        if (!check.data?.public) return json({ error: "Could not prepare homework storage. Please retry." }, 503);
      }
    } else if (!bucket.public) return json({ error: "Homework storage is not configured for sharing." }, 409);

    const { error: uploadError } = await supabase.storage.from(BUCKET).upload(OBJECT_PATH, bytes, { contentType: "application/pdf", cacheControl: "3600", upsert: false });
    // Retrying is safe: an existing file must match exactly, never be overwritten.
    const saved = await supabase.storage.from(BUCKET).download(OBJECT_PATH);
    if (saved.error || !saved.data) return json({ error: uploadError ? "Could not store the workbook. Please retry." : "Could not verify the saved workbook. Please retry." }, 503);
    const savedBytes = new Uint8Array(await saved.data.arrayBuffer());
    if (savedBytes.byteLength !== FILE_SIZE || createHash("sha256").update(savedBytes).digest("hex") !== FILE_HASH) return json({ error: "The stored file did not match. No homework link was published." }, 409);

    const previous = session.description || "";
    const description = previous.includes(LINK) ? previous : previous.trim() + "\n\n" + HOMEWORK_NOTE + "\n" + LINK;
    let update = supabase.from("tmua_class_sessions").update({ description, updated_at: new Date().toISOString() }).eq("id", SESSION_ID);
    update = session.description === null ? update.is("description", null) : update.eq("description", session.description);
    const linked = await update.select("id,description").single();
    if (linked.error || !linked.data?.description?.includes(LINK)) return json({ error: "The PDF was saved, but the session changed. Click Publish again to finish linking it." }, 409);
    return json({ ok: true, pdfUrl: PDF_PATH, session: "Sunday 1 November 2026 — Session 2: Paper 2 Logic & Quantifiers", sha256: FILE_HASH });
  } catch {
    return json({ error: "Publication could not be completed. Retrying will not overwrite another file." }, 503);
  }
}
