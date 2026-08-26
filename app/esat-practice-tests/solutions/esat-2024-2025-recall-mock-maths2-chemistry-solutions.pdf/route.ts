const SOURCE = "https://pnkzxzigpkvhlmhsmzdd.supabase.co/storage/v1/object/public/esat-recall-solutions/esat-2024-2025-recall-mock-maths2-chemistry-solutions.pdf";
const FILENAME = "esat-2024-2025-recall-mock-maths2-chemistry-solutions.pdf";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  const upstream = await fetch(SOURCE, { cache: "force-cache" });
  if (!upstream.ok || !upstream.body) return new Response("Solution PDF unavailable", { status: 502 });
  const headers = new Headers({
    "Content-Type": "application/pdf",
    "Content-Disposition": `inline; filename="${FILENAME}"`,
    "Cache-Control": "public, max-age=3600, s-maxage=86400, stale-while-revalidate=604800",
    "X-Content-Type-Options": "nosniff",
  });
  const length = upstream.headers.get("content-length");
  if (length) headers.set("Content-Length", length);
  return new Response(upstream.body, { status: 200, headers });
}
