import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { createServerClient } from "@supabase/ssr";
import {
  decodeLoginDestination,
  LOGIN_DESTINATION_COOKIE,
  safeLoginDestination,
} from "@/lib/auth/login-destination";

export async function GET(req: Request) {
  const url = new URL(req.url);
  const code = url.searchParams.get("code");

  if (!code) {
    return NextResponse.redirect(new URL("/login?e=missing_code", url.origin));
  }

  const cookieStore = await cookies();
  const cookieDestination = decodeLoginDestination(
    cookieStore.get(LOGIN_DESTINATION_COOKIE)?.value,
  );
  const next = safeLoginDestination(
    url.searchParams.get("next") ?? cookieDestination,
  );

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseAnon =
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;

  if (!supabaseUrl || !supabaseAnon) {
    return NextResponse.redirect(new URL("/login?e=missing_env", url.origin));
  }

  // IMPORTANT: We must return a response object that receives set-cookie updates
  const res = NextResponse.redirect(new URL(next, url.origin));

  const supabase = createServerClient(supabaseUrl, supabaseAnon, {
    cookies: {
      getAll() {
        return cookieStore.getAll();
      },
      setAll(cookiesToSet) {
        cookiesToSet.forEach(({ name, value, options }) => {
          // Set cookies both ways: on the outgoing response + store (Next expects this pattern)
          res.cookies.set(name, value, options);
          cookieStore.set(name, value, options);
        });
      },
    },
  });

  const { error } = await supabase.auth.exchangeCodeForSession(code);

  if (error) {
    return NextResponse.redirect(new URL("/login?e=callback_exchange_failed", url.origin));
  }

  res.cookies.delete(LOGIN_DESTINATION_COOKIE);
  res.headers.set("Cache-Control", "private, no-store");

  return res;
}
