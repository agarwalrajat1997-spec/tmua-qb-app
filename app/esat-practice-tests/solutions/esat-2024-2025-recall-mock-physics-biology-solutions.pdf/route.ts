const ASSET_PATH = "/esat-solution-assets/esat-2024-2025-recall-mock-physics-biology-solutions.pdf";
const FILENAME = "esat-2024-2025-recall-mock-physics-biology-solutions.pdf";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const assetUrl = new URL(ASSET_PATH, request.url);
  const upstream = await fetch(assetUrl, { cache: "no-store" });

  if (!upstream.ok || !upstream.body) {
    return new Response("Solution PDF unavailable", {
      status: 502,
      headers: {
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff",
      },
    });
  }

  const headers = new Headers({
    "Content-Type": "application/pdf",
    "Content-Disposition": `inline; filename="${FILENAME}"`,
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
    "X-Robots-Tag": "noindex, nofollow",
  });

  const length = upstream.headers.get("content-length");

  if (length) {
    headers.set("Content-Length", length);
  }

  return new Response(upstream.body, {
    status: 200,
    headers,
  });
}