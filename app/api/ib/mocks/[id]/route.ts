import { NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { getIbAccessState } from "@/lib/ib/access";
import { getPhysicsMockPaper, physicsMockSolutions } from "@/lib/ib/physics-mocks";
import { getPhysicsMock, getPhysicsPaperMeta, cleanAnswers, validateSelfMarks, scoreMock, type MockPaper, type PhysicsMockPaper, type MockReview } from "@/lib/ib/physics-mock-model";
export const runtime = "nodejs";
export const dynamic = "force-dynamic";
const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const fields = "id,mock_id,paper,student_name,answers,elapsed_seconds,submitted_at,self_marks,marked_at";
type Row = {
    id: string;
    mock_id: string;
    paper: MockPaper;
    student_name: string;
    answers: unknown;
    elapsed_seconds: number;
    submitted_at: string;
    self_marks: unknown;
    marked_at: string | null;
};
function json(value: unknown, status = 200) { return NextResponse.json(value, { status, headers: { "Cache-Control": "private, no-store" } }); }
function review(row: Row, paper: PhysicsMockPaper): MockReview { const answers = cleanAnswers(paper.questions, row.answers), selfMarks = row.self_marks === null ? null : validateSelfMarks(paper.questions, row.self_marks); return { id: row.id, submittedAt: row.submitted_at, name: row.student_name, elapsed: row.elapsed_seconds, answers, selfMarks, score: scoreMock(paper.questions, answers, selfMarks), solutions: physicsMockSolutions(paper) }; }
const isArchive = (id: string) => /^physics-(sl|hl)-mock-0[1-3]$/.test(id);
export async function GET(req: Request, { params }: {
    params: Promise<{
        id: string;
    }>;
}) {
    const { id } = await params;
    if (!getPhysicsMock(id) && !isArchive(id))
        return json({ error: "Mock not found." }, 404);
    const db = await createSupabaseServerClient(), { data: { user }, error: authError } = await db.auth.getUser();
    if (authError || !user?.email)
        return json({ error: "Please sign in to view your attempts." }, 401);
    const access = await getIbAccessState();
    if (access !== "active")
        return json({ error: access === "unavailable" ? "Access check is temporarily unavailable. Please retry." : "Your IB trial has ended or access is required.", access_url: "/ib-access" }, access === "unavailable" ? 503 : 403);
    const url = new URL(req.url), attempt = url.searchParams.get("attempt"), requestedPaper = url.searchParams.get("paper");
    if (attempt && !uuid.test(attempt))
        return json({ error: "Invalid attempt." }, 400);
    const table = isArchive(id) ? "ib_physics_mock_attempts" : "ib_physics_challenge_attempts";
    if (!attempt) {
        const { data, error } = await db.from(table).select("id,paper,submitted_at,marked_at").eq("user_id", user.id).eq("mock_id", id).order("submitted_at", { ascending: false }).limit(30);
        return error ? json({ error: "Attempt history is temporarily unavailable." }, 503) : json({ attempts: data });
    }
    let query = db.from(table).select(isArchive(id) ? "id,mock_id,paper,answers,elapsed_seconds,submitted_at,self_marks" : fields).eq("user_id", user.id).eq("mock_id", id).eq("id", attempt);
    if (requestedPaper) {
        if (!["1", "2"].includes(requestedPaper))
            return json({ error: "Invalid paper." }, 400);
        query = query.eq("paper", requestedPaper);
    }
    const { data, error } = await query.maybeSingle();
    if (error)
        return json({ error: "We could not load this attempt. Please retry." }, 503);
    if (!data)
        return json({ error: "Attempt not found." }, 404);
    const row = data as unknown as Row;
    try {
        // The bank-backed archive is loaded only after an owned saved row exists.
        if (isArchive(id)) {
            const { legacyReview } = await import("@/lib/ib/physics-mock-archive");
            return json({ review: legacyReview(row), paper: row.paper, archived: true });
        }
        const paper = await getPhysicsMockPaper(id, row.paper);
        return paper ? json({ review: review(row, paper), paper: row.paper }) : json({ error: "Paper not found." }, 404);
    }
    catch {
        return json({ error: "This paper is temporarily unavailable. Please retry." }, 503);
    }
}
export async function POST(req: Request, { params }: {
    params: Promise<{
        id: string;
    }>;
}) {
    const { id } = await params;
    if (!getPhysicsMock(id))
        return json({ error: isArchive(id) ? "This earlier series is archived. Open an existing saved attempt or choose a new paper." : "Mock not found." }, isArchive(id) ? 410 : 404);
    const origin = req.headers.get("origin");
    if (origin && origin !== new URL(req.url).origin)
        return json({ error: "Invalid request origin." }, 403);
    const db = await createSupabaseServerClient(), { data: { user }, error: authError } = await db.auth.getUser();
    if (authError || !user?.email)
        return json({ error: "Your responses remain on this device. Sign in again, then retry." }, 401);
    const access = await getIbAccessState();
    if (access !== "active")
        return json({ error: access === "unavailable" ? "Access check is temporarily unavailable. Please retry." : "Your IB trial has ended or access is required.", access_url: "/ib-access" }, access === "unavailable" ? 503 : 403);
    let body;
    try {
        const raw = await req.text();
        if (raw.length > 600000)
            return json({ error: "Response is too large." }, 413);
        body = JSON.parse(raw);
    }
    catch {
        return json({ error: "Invalid request." }, 400);
    }
    if (!body || typeof body !== "object" || !uuid.test(body.attemptId ?? "") || !["1", "2"].includes(body.paper))
        return json({ error: "Invalid attempt." }, 400);
    const meta = getPhysicsPaperMeta(id, body.paper);
    if (!meta)
        return json({ error: "Paper not found." }, 404);
    let paper: PhysicsMockPaper | undefined;
    try {
        paper = await getPhysicsMockPaper(id, body.paper);
    }
    catch {
        return json({ error: "This paper is temporarily unavailable. Your responses remain on this device." }, 503);
    }
    if (!paper)
        return json({ error: "Paper not found." }, 404);
    if (body.action === "submit") {
        let answers;
        try {
            answers = cleanAnswers(paper.questions, body.answers);
        }
        catch (e) {
            return json({ error: (e as Error).message }, 400);
        }
        if (!Number.isInteger(body.elapsed) || body.elapsed < 0 || body.elapsed > meta.minutes * 60)
            return json({ error: "Invalid elapsed time." }, 400);
        if (typeof body.name !== "string" || body.name.length > 100)
            return json({ error: "Invalid report name." }, 400);
        const { error } = await db.from("ib_physics_challenge_attempts").insert({ id: body.attemptId, user_id: user.id, mock_id: id, paper: body.paper, student_name: body.name.trim(), answers, elapsed_seconds: body.elapsed });
        if (error && error.code !== "23505")
            return json({ error: "Your responses remain on this device. The server could not save them; please retry." }, 503);
    }
    else if (body.action === "mark") {
        let selfMarks;
        try {
            selfMarks = validateSelfMarks(paper.questions, body.selfMarks);
        }
        catch (e) {
            return json({ error: (e as Error).message }, 400);
        }
        const { error } = await db.from("ib_physics_challenge_attempts").update({ self_marks: selfMarks, marked_at: new Date().toISOString() }).eq("user_id", user.id).eq("mock_id", id).eq("paper", body.paper).eq("id", body.attemptId).is("self_marks", null);
        if (error)
            return json({ error: "Marks could not be saved. Please retry." }, 503);
    }
    else
        return json({ error: "Unknown action." }, 400);
    const { data, error } = await db.from("ib_physics_challenge_attempts").select(fields).eq("user_id", user.id).eq("mock_id", id).eq("paper", body.paper).eq("id", body.attemptId).maybeSingle();
    if (error)
        return json({ error: "Saved attempt could not be loaded. Retry to recover your original submission." }, 503);
    if (!data)
        return json({ error: "Attempt not found." }, 404);
    try {
        return json({ review: review(data as Row, paper), paper: data.paper });
    }
    catch {
        return json({ error: "Stored marking data needs review. Please contact your tutor." }, 422);
    }
}
