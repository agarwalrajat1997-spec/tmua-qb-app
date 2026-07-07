import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { supabaseAdmin } from "./supabaseAdmin";

export function normalizeExam(raw: string | null) {
  const s = String(raw || "").replace(/\s+/g, "").toUpperCase();

  if (s === "AMC8") return { label: "AMC 8", column: "amc_8" as const };
  if (s === "AMC10") return { label: "AMC 10", column: "amc_10" as const };
  if (s === "AMC12") return { label: "AMC 12", column: "amc_12" as const };

  return null;
}

export async function requireAmcAccess() {
  const cookieStore = await cookies();

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) => {
              cookieStore.set(name, value, options);
            });
          } catch {}
        },
      },
    }
  );

  const {
    data: { user },
    error: userError,
  } = await supabase.auth.getUser();

  if (userError || !user?.email) {
    return {
      ok: false as const,
      response: NextResponse.json({ error: "Unauthenticated" }, { status: 401 }),
    };
  }

  const admin = supabaseAdmin();

  const { data, error } = await admin
    .from("student_access")
    .select("email,product,approved")
    .ilike("email", user.email)
    .eq("product", "amc-question-bank")
    .eq("approved", true)
    .maybeSingle();

  if (error) {
    return {
      ok: false as const,
      response: NextResponse.json({ error: error.message }, { status: 500 }),
    };
  }

  if (!data) {
    return {
      ok: false as const,
      response: NextResponse.json({ error: "No AMC question bank access" }, { status: 403 }),
    };
  }

  return {
    ok: true as const,
    user,
    admin,
  };
}
