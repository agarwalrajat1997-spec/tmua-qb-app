export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const htmlUrl = new URL("/sat-test-4/index.html", request.url);

  const htmlResponse = await fetch(htmlUrl, {
    cache: "no-store",
    redirect: "follow",
  });

  if (!htmlResponse.ok) {
    return new Response("SAT Test 4 file could not be loaded.", {
      status: 500,
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
      },
    });
  }

  const htmlBytes = await htmlResponse.arrayBuffer();

  return new Response(htmlBytes, {
    status: 200,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
      "Pragma": "no-cache",
      "X-Content-Type-Options": "nosniff",
    },
  });
}