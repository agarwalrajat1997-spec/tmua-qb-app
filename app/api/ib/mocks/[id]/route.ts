import { getIbAccessState } from "@/lib/ib/access";
import { NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { getPhysicsMock, getMockItems } from "@/lib/ib/physics-mocks";
import { cleanAnswers, validateSelfMarks, scoreMock, paperSpec, type MockPaper, type MockReview } from "@/lib/ib/physics-mock-model";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const fields = "id,mock_id,paper,answers,elapsed_seconds,submitted_at,self_marks";
type Row = { id:string; mock_id:string; paper:MockPaper; answers:unknown; elapsed_seconds:number; submitted_at:string; self_marks:unknown };
function json(value: unknown, status=200) { return NextResponse.json(value,{status,headers:{"Cache-Control":"private, no-store"}}); }
function review(row: Row): MockReview {
  const items = getMockItems(row.mock_id,row.paper);
  const answers = cleanAnswers(items,row.answers);
  const selfMarks = row.self_marks === null ? null : validateSelfMarks(items,row.self_marks);
  return { id:row.id,submittedAt:row.submitted_at,elapsed:row.elapsed_seconds,answers,selfMarks,
    score:scoreMock(items,answers,selfMarks),
    solutions:items.map(({question:q,section,number}) => ({id:q.id,label:`${section} Q${number}`,parts:q.parts,markScheme:q.markScheme,correctOption:q.correctOption,
      diagram:q.markSchemeDiagramSvg?`data:image/svg+xml;base64,${Buffer.from(q.markSchemeDiagramSvg).toString("base64")}`:undefined,diagramCaption:q.markSchemeDiagramCaption})) };
}
export async function GET(req:Request,{params}:{params:Promise<{id:string}>}) {
  const {id} = await params;
  if (!getPhysicsMock(id)) return json({error:"Mock not found."},404);
  const db = await createSupabaseServerClient();
  const {data:{user},error:authError} = await db.auth.getUser();
  if (authError || !user) return json({error:"Please sign in to view your attempts."},401);
  const access = await getIbAccessState();
  if (access !== "active") return json({error: access === "unavailable" ? "Access check is temporarily unavailable. Please retry." : "Your IB trial has ended or access is required.", access_url: "/ib-access"}, access === "unavailable" ? 503 : 403);
  const attempt = new URL(req.url).searchParams.get("attempt");
  if (attempt) {
    if (!uuid.test(attempt)) return json({error:"Invalid attempt."},400);
    const {data,error} = await db.from("ib_physics_mock_attempts").select(fields).eq("user_id",user.id).eq("mock_id",id).eq("id",attempt).maybeSingle();
    if (error) return json({error:"We could not load this attempt. Please retry."},503);
    if (!data) return json({error:"Attempt not found."},404);
    try { return json({review:review(data as Row),paper:data.paper}); }
    catch { return json({error:"This attempt needs a marking review. Please contact your tutor."},422); }
  }
  const {data,error} = await db.from("ib_physics_mock_attempts").select("id,paper,submitted_at,marked_at").eq("user_id",user.id).eq("mock_id",id).order("submitted_at",{ascending:false}).limit(30);
  return error ? json({error:"Attempt history is temporarily unavailable."},503) : json({attempts:data});
}
export async function POST(req:Request,{params}:{params:Promise<{id:string}>}) {
  const {id} = await params;
  const mock = getPhysicsMock(id);
  if (!mock) return json({error:"Mock not found."},404);
  const origin = req.headers.get("origin");
  if (origin && origin !== new URL(req.url).origin) return json({error:"Invalid request origin."},403);
  const db = await createSupabaseServerClient();
  const {data:{user},error:authError} = await db.auth.getUser();
  if (authError || !user) return json({error:"Your answers are kept on this device. Sign in again, then retry."},401);
  const access = await getIbAccessState();
  if (access !== "active") return json({error: access === "unavailable" ? "Access check is temporarily unavailable. Please retry." : "Your IB trial has ended or access is required.", access_url: "/ib-access"}, access === "unavailable" ? 503 : 403);
  let body;
  try {
    const raw = await req.text();
    if (raw.length > 600000) return json({error:"Response is too large."},413);
    body = JSON.parse(raw);
  } catch { return json({error:"Invalid request."},400); }
  if (!body || !uuid.test(body.attemptId ?? "") || !["1","2"].includes(body.paper)) return json({error:"Invalid attempt."},400);
  const paper = body.paper as MockPaper;
  const items = getMockItems(id,paper);
  if (body.action === "submit") {
    let answers;
    try { answers = cleanAnswers(items,body.answers); } catch(e) { return json({error:(e as Error).message},400); }
    if (!Number.isInteger(body.elapsed) || body.elapsed < 0 || body.elapsed > paperSpec(mock.course,paper).minutes*60) return json({error:"Invalid elapsed time."},400);
    const {error} = await db.from("ib_physics_mock_attempts").insert({id:body.attemptId,user_id:user.id,mock_id:id,paper,answers,elapsed_seconds:body.elapsed});
    if (error && error.code !== "23505") return json({error:"Your answers are kept on this device. The server could not save them; please retry."},503);
    // Retries return the first immutable submission, never overwrite it.
  } else if (body.action === "mark") {
    let selfMarks;
    try { selfMarks = validateSelfMarks(items,body.selfMarks); } catch(e) { return json({error:(e as Error).message},400); }
    const {error} = await db.from("ib_physics_mock_attempts").update({self_marks:selfMarks,marked_at:new Date().toISOString()}).eq("user_id",user.id).eq("mock_id",id).eq("paper",paper).eq("id",body.attemptId);
    if (error) return json({error:"Marks could not be saved. Please retry."},503);
  } else return json({error:"Unknown action."},400);
  const {data,error} = await db.from("ib_physics_mock_attempts").select(fields).eq("user_id",user.id).eq("mock_id",id).eq("paper",paper).eq("id",body.attemptId).maybeSingle();
  if (error) return json({error:"Saved attempt could not be loaded. Please retry."},503);
  if (!data) return json({error:"Attempt not found."},404);
  try { return json({review:review(data as Row)}); }
  catch { return json({error:"Invalid stored marking data."},422); }
}
