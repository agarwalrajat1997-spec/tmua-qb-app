import { NextResponse } from "next/server";
import {
  LOGIN_DESTINATION_COOKIE,
  LOGIN_DESTINATION_MAX_AGE_SECONDS,
  safeLoginDestination,
} from "@/lib/auth/login-destination";

export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const origin = req.headers.get("origin");
  const forwardedHost = req.headers
    .get("x-forwarded-host")
    ?.split(",")[0]
    ?.trim();
  const host = forwardedHost || req.headers.get("host");
  const forwardedProtocol = req.headers
    .get("x-forwarded-proto")
    ?.split(",")[0]
    ?.trim();
  const protocol = forwardedProtocol || new URL(req.url).protocol.slice(0, -1);
  const requestOrigin = host ? `${protocol}://${host}` : null;

  if (origin && requestOrigin && origin !== requestOrigin) {
    return NextResponse.json(
      { error: "Invalid login-intent origin." },
      { status: 403 },
    );
  }

  let body: { next?: unknown };

  try {
    body = await req.json();
  } catch {
    body = {};
  }

  const next = safeLoginDestination(body.next);
  const res = NextResponse.json({ next });

  res.cookies.set({
    name: LOGIN_DESTINATION_COOKIE,
    value: next,
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: LOGIN_DESTINATION_MAX_AGE_SECONDS,
  });
  res.headers.set("Cache-Control", "private, no-store");

  return res;
}
