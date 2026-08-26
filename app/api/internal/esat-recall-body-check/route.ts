export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const TOKEN = "esat_body_check_20260827_P4xN8mR2qV7cK5hL1tY6wS3dF9jB0aZu";

export async function POST(request: Request) {
  if (request.headers.get("authorization") !== `Bearer ${TOKEN}`) {
    return Response.json({ error: "Unauthorized" }, { status: 401, headers: { "Cache-Control": "no-store" } });
  }
  const bytes = new Uint8Array(await request.arrayBuffer());
  return Response.json({ ok: true, bytes: bytes.byteLength }, { headers: { "Cache-Control": "no-store" } });
}

export function GET() {
  return new Response("Not found", { status: 404, headers: { "Cache-Control": "no-store" } });
}
