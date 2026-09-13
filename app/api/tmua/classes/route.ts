import { NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

export const dynamic = "force-dynamic";

function getSupabaseAdmin() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_SERVICE_KEY;

  if (!url || !key) {
    throw new Error("Missing Supabase URL or service key");
  }

  return createClient(url, key, {
    auth: {
      persistSession: false,
      autoRefreshToken: false,
    },
  });
}

export async function GET() {
  try {
    const supabase = getSupabaseAdmin();

    const { data, error } = await supabase
      .from("tmua_class_sessions")
      .select("id,title,batch_name,description,starts_at,ends_at,timezone,zoom_url,zoom_label,status,recording_url,recording_title,recording_notes,is_visible,sort_order")
      .eq("is_visible", true)
      .order("starts_at", { ascending: true })
      .order("sort_order", { ascending: true });

    if (error) {
      return NextResponse.json({ ok: false, error: error.message }, { status: 500 });
    }

    const now = Date.now();

    const sessions = (data || []).map((s) => {
      const startMs = s.starts_at ? new Date(s.starts_at).getTime() : 0;
      const endMs = s.ends_at ? new Date(s.ends_at).getTime() : startMs;

      let computed_status = s.status || "scheduled";
      if (computed_status === "scheduled" && endMs && endMs < now) {
        computed_status = "completed";
      }

      return { ...s, computed_status };
    });

    const upcoming = sessions
      .filter((s) => s.computed_status === "scheduled")
      .sort((a, b) => new Date(a.starts_at).getTime() - new Date(b.starts_at).getTime());

    const recordings = sessions
      .filter((s) => s.recording_url)
      .sort((a, b) => new Date(b.starts_at).getTime() - new Date(a.starts_at).getTime());

    return NextResponse.json({
      ok: true,
      upcoming,
      recordings,
      all: sessions,
    });
  } catch (e: any) {
    return NextResponse.json(
      { ok: false, error: e?.message || "Could not load TMUA classes" },
      { status: 500 }
    );
  }
}
