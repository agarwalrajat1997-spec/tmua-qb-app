// Public game entry point. Does not alter portal authentication or existing routes.
export const dynamic = "force-dynamic";

export function GET(request: Request) {
  const url = new URL(request.url);
  url.pathname = "/bluff/index.html";
  return Response.redirect(url, 307);
}
