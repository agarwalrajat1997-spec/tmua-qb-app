import { NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { getIbAccessState } from "@/lib/ib/access";
import { getMathsMockPaper } from "@/lib/ib/maths-mocks";
import { getMathsMock, cleanMathsAnswers, validateMathsMarks, scoreMathsMock, type MathsMockPaper, type MathsMockReview } from "@/lib/ib/maths-mock-model";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const fields = "id,mock_id,student_name,answers,elapsed_seconds,submitted_at,self_marks,marked_at";
type Row = { id: string; mock_id: string; student_name: string; answers: unknown; elapsed_seconds: number; submitted_at: string; self_marks: unknown; marked_at: string | null };
function json(value: unknown, status = 200) { return NextResponse.json(value, { status, headers: { "Cache-Control": "private, no-store" } }); }
function review(row: Row, paper: MathsMockPaper): MathsMockReview {
  const answers = cleanMathsAnswers(paper.questions, row.answers), selfMarks = row.self_marks === null ? null : validateMathsMarks(paper.questions, row.self_marks);
  return { id: row.id, submittedAt: row.submitted_at, name: row.student_name, elapsed: row.elapsed_seconds,
    answers, selfMarks, score: scoreMathsMock(paper.questions, selfMarks), solutions: paper.questions };
}
export async function GET(req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!getMathsMock(id)) return json({ error: "Mock not found." }, 404);
  const db = await createSupabaseServerClient();
  const { data: { user }, error: authError } = await db.auth.getUser();
  if (authError || !user?.email) return json({ error: "Please sign in to view your attempts." }, 401);
  const access = await getIbAccessState();
  if (access !== "active") return json({ error: access === "unavailable" ? "Access check is temporarily unavailable. Please retry." : "Your IB trial has ended or access is required.", access_url: "/ib-access" }, access === "unavailable" ? 503 : 403);
  const attempt = new URL(req.url).searchParams.get("attempt");
  if (!attempt) {
    const { data, error } = await db.from("ib_maths_mock_attempts").select("id,submitted_at,marked_at").eq("user_id", user.id).eq("mock_id", id).order("submitted_at", { ascending: false }).limit(30);
    return error ? json({ error: "Attempt history is temporarily unavailable." }, 503) : json({ attempts: data });
  }
  if (!uuid.test(attempt)) return json({ error: "Invalid attempt." }, 400);
  const { data, error } = await db.from("ib_maths_mock_attempts").select(fields).eq("user_id", user.id).eq("mock_id", id).eq("id", attempt).maybeSingle();
  if (error) return json({ error: "We could not load this attempt. Please retry." }, 503);
  if (!data) return json({ error: "Attempt not found." }, 404);
  try { const paper = await getMathsMockPaper(id); return paper ? json({ review: review(data as Row, paper) }) : json({ error: "Paper not found." }, 404); }
  catch { return json({ error: "This paper is temporarily unavailable. Please retry." }, 503); }
}
export async function POST(req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params, meta = getMathsMock(id);
  if (!meta) return json({ error: "Mock not found." }, 404);
  const origin = req.headers.get("origin");
  if (origin && origin !== new URL(req.url).origin) return json({ error: "Invalid request origin." }, 403);
  const db = await createSupabaseServerClient();
  const { data: { user }, error: authError } = await db.auth.getUser();
  if (authError || !user?.email) return json({ error: "Your responses remain on this device. Sign in again, then retry." }, 401);
  const access = await getIbAccessState();
  if (access !== "active") return json({ error: access === "unavailable" ? "Access check is temporarily unavailable. Please retry." : "Your IB trial has ended or access is required.", access_url: "/ib-access" }, access === "unavailable" ? 503 : 403);
  let body;
  try { const raw = await req.text(); if (raw.length > 600000) return json({ error: "Response is too large." }, 413); body = JSON.parse(raw); }
  catch { return json({ error: "Invalid request." }, 400); }
  if (!body || typeof body !== "object" || !uuid.test(body.attemptId ?? "")) return json({ error: "Invalid attempt." }, 400);
  let paper: MathsMockPaper | undefined;
  try { paper = await getMathsMockPaper(id); } catch { return json({ error: "This paper is temporarily unavailable. Your responses remain on this device." }, 503); }
  if (!paper) return json({ error: "Paper not found." }, 404);
  if (body.action === "submit") {
    let answers;
    try { answers = cleanMathsAnswers(paper.questions, body.answers); } catch (e) { return json({ error: (e as Error).message }, 400); }
    if (!Number.isInteger(body.elapsed) || body.elapsed < 0 || body.elapsed > meta.minutes * 60) return json({ error: "Invalid elapsed time." }, 400);
    if (typeof body.name !== "string" || body.name.length > 100) return json({ error: "Invalid report name." }, 400);
    const { error } = await db.from("ib_maths_mock_attempts").insert({ id: body.attemptId, user_id: user.id, mock_id: id,
      student_name: body.name.trim(), answers, elapsed_seconds: body.elapsed });
    if (error && error.code !== "23505") return json({ error: "Your responses remain on this device. The server could not save them; please retry." }, 503);
    // A retry can only read the first immutable submission, never replace it.
  } else if (body.action === "mark") {
    let selfMarks;
    try { selfMarks = validateMathsMarks(paper.questions, body.selfMarks); } catch (e) { return json({ error: (e as Error).message }, 400); }
    const { error } = await db.from("ib_maths_mock_attempts").update({ self_marks: selfMarks, marked_at: new Date().toISOString() })
      .eq("user_id", user.id).eq("mock_id", id).eq("id", body.attemptId).is("self_marks", null);
    if (error) return json({ error: "Marks could not be saved. Please retry." }, 503);
  } else return json({ error: "Unknown action." }, 400);
  const { data, error } = await db.from("ib_maths_mock_attempts").select(fields).eq("user_id", user.id).eq("mock_id", id).eq("id", body.attemptId).maybeSingle();
  if (error) return json({ error: "Saved attempt could not be loaded. Retry to recover your original submission." }, 503);
  if (!data) return json({ error: "Attempt not found." }, 404);
  try { return json({ review: review(data as Row, paper) }); } catch { return json({ error: "Stored marking data needs review. Please contact your tutor." }, 422); }
}
