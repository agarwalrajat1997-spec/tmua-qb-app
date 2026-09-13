import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { createServerClient } from "@supabase/ssr";
import type { EmailOtpType } from "@supabase/supabase-js";
import {
  decodeLoginDestination,
  LOGIN_DESTINATION_COOKIE,
  safeLoginDestination,
} from "@/lib/auth/login-destination";

export async function GET(req: Request) {
  const url = new URL(req.url);
  const code = url.searchParams.get("code");
  const tokenHash = url.searchParams.get("token_hash");
  const requestedType = url.searchParams.get("type");
  const allowedOtpTypes = new Set<EmailOtpType>([
    "email",
    "signup",
    "invite",
    "magiclink",
    "recovery",
    "email_change",
  ]);
  const otpType =
    requestedType && allowedOtpTypes.has(requestedType as EmailOtpType)
      ? (requestedType as EmailOtpType)
      : null;

  if (!code && (!tokenHash || !otpType)) {
    const retryUrl = new URL("/login", url.origin);
    retryUrl.searchParams.set("e", "invalid_or_consumed_link");
    return NextResponse.redirect(retryUrl);
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

  // Support both Supabase flows:
  // 1. PKCE `code` links created by the current browser client.
  // 2. `token_hash` links, which are safe to open on a different device/browser
  //    and avoid failures when a parent requests a link for a student.
  const { error } = code
    ? await supabase.auth.exchangeCodeForSession(code)
    : await supabase.auth.verifyOtp({
        token_hash: tokenHash!,
        type: otpType!,
      });

  if (error) {
    const retryUrl = new URL("/login", url.origin);
    retryUrl.searchParams.set("e", "invalid_or_consumed_link");
    return NextResponse.redirect(retryUrl);
  }

  res.cookies.delete(LOGIN_DESTINATION_COOKIE);
  res.headers.set("Cache-Control", "private, no-store");

  return res;
}
