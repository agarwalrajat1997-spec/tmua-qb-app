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

export const config = {
  matcher: ["/tmua-question-bank/:path*", "/practice-tests/:path*"],
};

export async function proxy(req: NextRequest) {
  const pathname = req.nextUrl.pathname;

  if (isPublicPath(pathname)) return NextResponse.next();

  const required = requiredProductForPath(pathname);
  if (!required) return NextResponse.next();

  const res = NextResponse.next();

  const url = process.env.NEXT_PUBLIC_SUPABASE_URL!;
  const key = ((process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY) || process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY)!;

  const supabase = createServerClient(url, key, {
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
  });

  // ✅ Use getUser() (more reliable in proxy than getSession for this case)
  const { data: userData } = await supabase.auth.getUser();
  const user = userData?.user;

  if (!user?.email) {
    const loginUrl = req.nextUrl.clone();
    loginUrl.pathname = "/login";
    loginUrl.searchParams.set("next", pathname + req.nextUrl.search);
    return NextResponse.redirect(loginUrl);
  }

  const email = user.email.toLowerCase();
  const ok = await hasApproval(supabase, email, required);

  if (!ok) {
    const u = req.nextUrl.clone();
    u.pathname = "/pending";
    u.search = "";
    return NextResponse.redirect(u);
  }

  return res;
}

