import { createServerClient } from "@supabase/ssr";
import { NextRequest, NextResponse } from "next/server";

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

type ProductGate = {
  prefix: string;
  product: string;
};

const PRODUCT_GATES: ProductGate[] = [
  { prefix: "/tmua-question-bank", product: "tmua-question-bank" },
  { prefix: "/practice-tests", product: "practice-tests" },

  { prefix: "/amc-question-bank", product: "amc-question-bank" },
  { prefix: "/amc-8-question-bank", product: "amc-question-bank" },
  { prefix: "/amc-10-question-bank", product: "amc-question-bank" },
  { prefix: "/amc-12-question-bank", product: "amc-question-bank" },

  { prefix: "/sat-question-bank", product: "sat-question-bank" },
  { prefix: "/sat-practice-tests", product: "sat-practice-tests" },

  { prefix: "/classes", product: "classes" },
  { prefix: "/tmua-classes", product: "tmua-classes" },
  { prefix: "/group-sessions", product: "group-sessions" },

  // ESAT
  { prefix: "/esat", product: "esat-question-bank" },
  { prefix: "/esat-question-bank", product: "esat-question-bank" },
];

function matchProductGate(pathname: string) {
  return PRODUCT_GATES.find((gate) => {
    return pathname === gate.prefix || pathname.startsWith(gate.prefix + "/");
  });
}

function loginRedirect(req: NextRequest) {
  const url = req.nextUrl.clone();
  const next = req.nextUrl.pathname + req.nextUrl.search;

  url.pathname = "/login";
  url.search = "";
  url.searchParams.set("next", next);

  return NextResponse.redirect(url);
}

function pendingRedirect(req: NextRequest, product: string) {
  const url = req.nextUrl.clone();

  url.pathname = "/pending";
  url.search = "";
  url.searchParams.set("product", product);

  return NextResponse.redirect(url);
}

export async function proxy(req: NextRequest) {
  let res = NextResponse.next({ request: req });

  const supabase = createServerClient(
    SUPABASE_URL,
    SUPABASE_ANON_KEY,
    {
      cookies: {
        getAll() {
          return req.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) => {
            req.cookies.set(name, value);
          });

          res = NextResponse.next({ request: req });

          cookiesToSet.forEach(({ name, value, options }) => {
            res.cookies.set(name, value, options);
          });
        },
      },
    }
  );

  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user || !user.email) {
    return loginRedirect(req);
  }

  const pathname = req.nextUrl.pathname;
  const gate = matchProductGate(pathname);

  // Dashboard is signed-in only. Product tiles/access should be controlled by the dashboard UI/API.
  if (!gate) {
    return res;
  }

  const email = user.email.toLowerCase();
  const nowIso = new Date().toISOString();

  const { data: accessRows, error } = await supabase
    .from("student_access")
    .select("email, product, approved, expires_at")
    .ilike("email", email)
    .eq("product", gate.product)
    .eq("approved", true)
    .or(`expires_at.is.null,expires_at.gt.${nowIso}`)
    .limit(1);

  if (error) {
    console.error("Access check failed:", {
      email,
      product: gate.product,
      error,
    });

    return pendingRedirect(req, gate.product);
  }

  if (!accessRows || accessRows.length === 0) {
    return pendingRedirect(req, gate.product);
  }

  return res;
}

export const config = {
  matcher: [
    "/dashboard/:path*",

    "/tmua-question-bank/:path*",
    "/practice-tests/:path*",

    "/amc-question-bank/:path*",
    "/amc-8-question-bank/:path*",
    "/amc-10-question-bank/:path*",
    "/amc-12-question-bank/:path*",

    "/sat-question-bank/:path*",
    "/sat-practice-tests/:path*",

    "/classes/:path*",
    "/tmua-classes/:path*",
    "/group-sessions/:path*",

    "/esat/:path*",
    "/esat-question-bank/:path*",
  ],
};
