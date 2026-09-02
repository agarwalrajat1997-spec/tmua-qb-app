import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { createClient } from "@supabase/supabase-js";
import { createServerClient } from "@supabase/ssr";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export const SAT_QUESTIONS_TABLE = "sat_qb_questions";
export const SAT_PROGRESS_TABLE = "sat_qb_progress";

const NO_STORE_HEADERS = {
  "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
};

function requiredEnv(name: string) {
  const value = process.env[name];
  if (!value) throw new Error(`Missing environment variable: ${name}`);
  return value;
}

function anonOrPublishableKey() {
  return (
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY ||
    requiredEnv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
  );
}

export function json(data: unknown, status = 200) {
  return NextResponse.json(data, {
    status,
    headers: NO_STORE_HEADERS,
  });
}

export function adminClient() {
  return createClient(
    requiredEnv("NEXT_PUBLIC_SUPABASE_URL"),
    requiredEnv("SUPABASE_SERVICE_ROLE_KEY"),
    {
      auth: {
        persistSession: false,
        autoRefreshToken: false,
      },
    }
  );
}

async function getUser() {
  const cookieStore = await cookies();

  const supabase = createServerClient(
    requiredEnv("NEXT_PUBLIC_SUPABASE_URL"),
    anonOrPublishableKey(),
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll() {
          // Read-only in this route helper.
        },
      },
    }
  );

  const { data, error } = await supabase.auth.getUser();
  if (error || !data.user) return null;
  return data.user;
}

export async function requireSATAccess() {
  // Local-only bypass so you can test the Supabase-backed question bank
  // without needing magic-link login on localhost.
  if (
    process.env.NODE_ENV !== "production" &&
    process.env.DEV_BYPASS_SAT_ACCESS === "1"
  ) {
    return {
      ok: true as const,
      user: { id: null, email: "local-dev@thrivingscholars.com" },
      email: "local-dev@thrivingscholars.com",
    };
  }

  const user = await getUser();

  if (!user?.email) {
    return {
      ok: false as const,
      response: json({ ok: false, error: "Not signed in" }, 401),
    };
  }

  const email = user.email.toLowerCase();
  const supabase = adminClient();
  const nowIso = new Date().toISOString();

  const { data, error } = await supabase
    .from("student_access")
    .select("approved, expires_at")
    .ilike("email", email)
    .eq("product", "sat-question-bank")
    .eq("approved", true)
    .or(`expires_at.is.null,expires_at.gt.${nowIso}`)
    .limit(1);

  if (error) {
    console.error("SAT access check failed:", error);
    return {
      ok: false as const,
      response: json({ ok: false, error: "Access check failed" }, 500),
    };
  }

  if (!data || data.length === 0) {
    return {
      ok: false as const,
      response: json({ ok: false, error: "No SAT Question Bank access" }, 403),
    };
  }

  return {
    ok: true as const,
    user,
    email,
  };
}
