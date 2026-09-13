import { NextResponse, type NextRequest } from "next/server";
import { createServerClient } from "@supabase/ssr";

const PUBLIC_PREFIXES = [
  "/login",
  "/auth/callback",
  "/logout",
  "/api",
  "/_next",
  "/favicon.ico",
  "/robots.txt",
  "/sitemap.xml",
];

function isPublic(pathname: string) {
  if (pathname === "/") return true;
  return PUBLIC_PREFIXES.some((p) => pathname === p || pathname.startsWith(p + "/") || pathname.startsWith(p));
}

function isStaticFile(pathname: string) {
  return /\.(?:png|jpg|jpeg|gif|webp|svg|ico|css|js|map|txt|xml|json|woff|woff2|ttf|eot)$/.test(pathname);
}

function requiredProductForPath(pathname: string): string | null {
  if (pathname.startsWith("/tmua-question-bank")) return "tmua-question-bank";
  if (pathname.startsWith("/practice-tests")) return "practice-tests";

  // If you also serve practice tests from /tmua/*, uncomment:
  // if (pathname.startsWith("/tmua")) return "practice-tests";

  return null; // other authenticated pages (e.g. dashboard) only need login
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

export async function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;

  // Always allow public routes + static assets
  if (isPublic(pathname) || isStaticFile(pathname)) {
    return NextResponse.next();
  }

  // Everything else requires login (and maybe approval)
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

  // 1) Must be signed in
  const { data: sessionData } = await supabase.auth.getSession();
  const session = sessionData?.session;

  if (!session) {
    const loginUrl = req.nextUrl.clone();
    loginUrl.pathname = "/login";
    loginUrl.searchParams.set("next", pathname + req.nextUrl.search);
    return NextResponse.redirect(loginUrl);
  }

  // 2) Product gating (only for product paths)
  const email = session.user.email || "";
  const required = requiredProductForPath(pathname);

  if (required) {
    const ok = await hasApproval(supabase, email, required);
    if (!ok) {
      const u = req.nextUrl.clone();
      u.pathname = "/pending";
      u.search = "";
      return NextResponse.redirect(u);
    }
  }

  return res;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image).*)"],
};
