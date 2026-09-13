import { NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase/server";

export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  const supabase = await createSupabaseServerClient();

  const {
    data: { user },
    error: userErr,
  } = await supabase.auth.getUser();

  if (userErr || !user) {
    return NextResponse.json({ error: "Not logged in" }, { status: 401 });
  }

  const url = new URL(req.url);
  const testId = url.searchParams.get("test_id");

  let query = supabase
    .from("esat_practice_test_attempts")
    .select("id,test_id,test_title,total_questions,score,submitted_at")
    .eq("user_id", user.id)
    .order("submitted_at", { ascending: false });

  if (testId) {
    query = query.eq("test_id", testId);
  }

  const { data, error } = await query;

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  const attempts = data || [];

  const latestByTest: Record<string, any> = {};

  for (const row of attempts) {
    if (!row?.test_id) continue;
    if (!latestByTest[row.test_id]) latestByTest[row.test_id] = row;
  }

  return NextResponse.json({
    ok: true,
    attempts,
    latest: Object.values(latestByTest),
  });
}
