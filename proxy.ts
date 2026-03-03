import { NextResponse, type NextRequest } from "next/server";
import { createServerClient } from "@supabase/ssr";

function isPublicPath(pathname: string) {
  return (
    pathname === "/" ||
    pathname === "/login" ||
    pathname.startsWith("/auth/callback") ||
    pathname === "/logout" ||
    pathname.startsWith("/api") ||
    pathname.startsWith("/_next") ||
    pathname.startsWith("/favicon") ||
    pathname.startsWith("/robots") ||
    pathname.startsWith("/sitemap")
  );
}

function requiredProductForPath(pathname: string): string | null {
  if (pathname.startsWith("/tmua-question-bank")) return "tmua-question-bank";
  if (pathname.startsWith("/practice-tests")) return "practice-tests";
  return null;
}

async function hasApproval(supabase: any, email: string, product: string) {
  const { data, error } = await supabase
    .from("student_access")
    .select("approved")
    .eq("email", email)
    .eq("product", product)
    .maybeSingle();

  if (error) return false;
  return !!data?.approved;
}

export function proxy(req: NextRequest) {
  const pathname = req.nextUrl.pathname;

  // Let public routes through
  if (isPublicPath(pathname)) return NextResponse.next();

  // Only enforce product checks on product paths.
  // (Everything else can be public OR you can add login protection later.)
  const required = requiredProductForPath(pathname);
  if (!required) return NextResponse.next();

  const res = NextResponse.next();

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return req.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) => {
            res.cookies.set(name, value, options);
          });
        },
      },
    }
  );

  // We must return a Promise from the proxy function, so wrap async work:
  return (async () => {
    // 1) Must be logged in
    const { data: sessionData } = await supabase.auth.getSession();
    const session = sessionData?.session;

    if (!session) {
      const loginUrl = req.nextUrl.clone();
      loginUrl.pathname = "/login";
      loginUrl.searchParams.set("next", pathname + req.nextUrl.search);
      return NextResponse.redirect(loginUrl);
    }

    // 2) Must have approval for this product
    const email = session.user.email || "";
    const ok = await hasApproval(supabase, email, required);

    if (!ok) {
      const u = req.nextUrl.clone();
      u.pathname = "/pending";
      u.search = "";
      return NextResponse.redirect(u);
    }

    return res;
  })();
}

export const config = {
  matcher: [
    "/tmua-question-bank/:path*",
    "/practice-tests/:path*",
  ],
};
