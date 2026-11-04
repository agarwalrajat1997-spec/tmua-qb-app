import { NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { getIbAccessState } from "@/lib/ib/access";
export const dynamic = "force-dynamic";
function json(value: unknown, status = 200) { return NextResponse.json(value, { status, headers: { "Cache-Control": "private, no-store" } }); }
export async function GET(req: Request) {
    const course = new URL(req.url).searchParams.get("course");
    if (course !== "sl" && course !== "hl")
        return json({ error: "Invalid course." }, 400);
    const db = await createSupabaseServerClient(), { data: { user }, error: authError } = await db.auth.getUser();
    if (authError || !user?.email)
        return json({ error: "Please sign in to view saved attempts." }, 401);
    const access = await getIbAccessState();
    if (access !== "active")
        return json({ error: access === "unavailable" ? "Access check is temporarily unavailable." : "IB access is required.", access_url: "/ib-access" }, access === "unavailable" ? 503 : 403);
    const { data, error } = await db.from("ib_physics_mock_attempts").select("id,mock_id,paper,submitted_at,marked_at").eq("user_id", user.id).in("mock_id", [1, 2, 3].map(n => `physics-${course}-mock-0${n}`)).order("submitted_at", { ascending: false }).limit(30);
    return error ? json({ error: "Earlier saved attempts are temporarily unavailable." }, 503) : json({ attempts: data });
}
