export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  return Response.redirect(
    new URL("/sat-test-3/index.html", request.url),
    307,
  );
}
