import { requireTmuaAccess, adminClient } from "../qb/_server";
import { z } from "zod/v3";
import { catalogue, canonicalQid, publicQuestion, questionGuide, resolveQuestion } from "@/lib/tmua-studio-server/catalogue";
import { assertOrigin, assertViewer, isDevelopmentPreview, readBody, StudioError, studioJson } from "@/lib/tmua-studio-server/http";
import { loadNotebook, saveNotebook } from "@/lib/tmua-studio-server/notebooks";
import { isConfigured, reviewStatus, startReview } from "@/lib/tmua-studio-server/reviews";
import { ReviewRequest } from "@/lib/tmua-studio-server/contracts";
import { storedSolution } from "@/lib/tmua-studio-server/solution";
import { TutorError } from "@/lib/tmua-studio-server/tutor";

export const dynamic="force-dynamic";
export const runtime="nodejs";
export const maxDuration=120;
const qidSchema=z.string().min(1).max(160);
const versionSchema=z.string().min(1).max(200);

async function handler(request:Request){
  // Both auth identity and current entitlement are checked for every action, including polling and cloud reads.
  const access=await requireTmuaAccess();
  if(!access.ok){access.response.headers.set("Cache-Control","private, no-store, max-age=0");return access.response;}
  const developmentPreview=isDevelopmentPreview(process.env);
  if(!developmentPreview&&(!("id" in access.user)||typeof access.user.id!=="string"||!access.user.email)) return studioJson({error:"Sign in to use Study Studio."},401);
  const user=developmentPreview?{id:"00000000-0000-4000-8000-000000000001",email:"local-preview@thrivingscholars.com"}:{id:(access.user as {id:string}).id,email:access.user.email!};
  const url=new URL(request.url);let body:Record<string,unknown>={};
  if(request.method!=="GET"){
    assertOrigin(request);body=await readBody(request);
    if(!body||typeof body!=="object"||Array.isArray(body))throw new StudioError(400,"Invalid request.");
    assertViewer(body.expectedUserId,user.id);
  } else if(url.searchParams.has("expectedUserId"))assertViewer(url.searchParams.get("expectedUserId"),user.id);
  const action=String(body.action??url.searchParams.get("action")??"");
  // Preview never obtains a service client and cannot send AI calls or write real notebooks.
  if(developmentPreview&&["notebook","review","review-status"].includes(action))throw new StudioError(503,"Cloud notebooks and AI feedback are disabled in this local preview.","not_configured");
  const db=developmentPreview?null:adminClient();
  if(request.method==="GET"&&action==="catalogue") return studioJson({viewerId:user.id,count:catalogue.length,excluded:22,questions:catalogue,configured:!developmentPreview&&isConfigured()});
  if(request.method==="GET"&&action==="notebook")return studioJson(await loadNotebook(db!,user.id,url.searchParams.get("key")));
  if(request.method==="PUT"&&action==="notebook"){
    const {action:_action,expectedUserId:_viewer,...input}=body;
    return studioJson(await saveNotebook(db!,user,input));
  }
  if(request.method==="GET"&&action==="review-status")return studioJson(await reviewStatus(db!,user,url.searchParams.get("id")));

  const qid=qidSchema.parse(body.qid??url.searchParams.get("qid"));
  const rawVersion=body.contentVersion??url.searchParams.get("contentVersion");
  const version=rawVersion==null?undefined:versionSchema.parse(rawVersion);
  const question=resolveQuestion(qid,version);
  if(!question)throw new StudioError(404,"This exact audited question version is unavailable.");
  const bankId=canonicalQid(question.qid);
  if(db){
    const {data:live,error}=await db.from("tmua_qb_questions").select("qid").eq("qid",bankId).eq("is_active",true).maybeSingle().retry(false);
    if(error)throw new StudioError(503,"The question bank is temporarily unavailable.");
    if(!live)throw new StudioError(404,"This question is no longer available for TMUA practice.");
  }

  if(request.method==="GET"){
    if(action==="question")return studioJson({viewerId:user.id,question:publicQuestion(question),guide:questionGuide(question),configured:!developmentPreview&&isConfigured()});
    if(action==="guide")return studioJson({guide:questionGuide(question)});
    if(action==="solution")return studioJson({...storedSolution(question),qid:bankId,contentVersion:question.content_version});
  }
  if(request.method==="POST"&&(action==="answer"||action==="answers")){
    if(!version)throw new StudioError(400,"The question version is required.");
    const answer=z.string().min(1).max(40).parse(body.answer).trim();
    const options=question.options as {label:string}[];
    if(!options.some(o=>o.label===answer))throw new StudioError(400,"Choose one of this question's answers.");
    return studioJson({ok:true,qid:bankId,contentVersion:question.content_version,correct:answer===question.answer,answer:question.answer});
  }
  if(request.method==="POST"&&action==="review"){
    if(!version)throw new StudioError(400,"The question version is required.");
    const {action:_action,expectedUserId:_viewer,...raw}=body;
    const input=ReviewRequest.parse(raw);
    if(input.exam!=="tmua")throw new StudioError(400,"This Studio is for TMUA questions.");
    const result=await startReview(db!,user,input,question);
    return studioJson(result.body,result.httpStatus);
  }
  throw new StudioError(400,"Unknown Study Studio action.");
}
async function respond(request:Request){
  try{return await handler(request);}catch(error){
    if(error instanceof StudioError||error instanceof TutorError)return studioJson({error:error.message,...(error.code?{code:error.code}:{}),...(error.code==="NOTEBOOK_CONFLICT"?{conflict:true}:{})},error.status);
    if(error instanceof z.ZodError)return studioJson({error:"The request format was invalid. Your saved working is unchanged."},400);
    // Log no student content, provider payloads, credentials or identifiers.
    console.error("TMUA Studio service unavailable",error instanceof Error?error.name:"Unknown error");
    return studioJson({error:"Study Studio is temporarily unavailable. Your device copy is safe; please retry."},503);
  }
}
export const GET=respond;
export const POST=respond;
export const PUT=respond;
