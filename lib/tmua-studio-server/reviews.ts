import { createHash } from "node:crypto";
import type { SupabaseClient } from "@supabase/supabase-js";
import { z } from "zod/v3";
import { ReviewRequest } from "./contracts";
import { canonicalQid, type ReleasedQuestion } from "./catalogue";
import { StudioError } from "./http";
import {
  buildReviewPayload, startBackgroundReview, pollBackgroundReview, deleteProviderReview,
  PROMPT_VERSION, tutorConfig, TutorError, type PendingReview,
} from "./tutor";

const table="tmua_studio_review_jobs";
type User={id:string;email:string};
type Job={id:string;request_id:string;status:"reserved"|"pending"|"complete"|"failed";provider_id:string|null;review_context:PendingReview["context"];result:any;model:string;created_at:string;error_code:string|null};
const selection="id,request_id,status,provider_id,review_context,result,model,created_at,error_code";
export function isConfigured(){return !!process.env.OPENAI_API_KEY?.trim() && process.env.ENABLE_AI!=="false";}
async function load(db:SupabaseClient,userId:string,requestId:string):Promise<Job|null>{
  const {data,error}=await db.from(table).select(selection).eq("user_id",userId).eq("request_id",requestId).maybeSingle().retry(false);
  if(error)throw new StudioError(503,"Your saved review is temporarily unavailable. No new review was sent.");
  return data as Job|null;
}
const pending=(id:string)=>({status:"pending",requestId:id});
const failed=(job:Job)=>({status:"failed",requestId:job.request_id,error:job.result?.error??"This review could not be completed. Your working is saved.",code:job.error_code??"review_failed"});
const view=(job:Job)=>job.status==="complete"?{status:"complete",requestId:job.request_id,feedback:job.result}:job.status==="failed"?failed(job):pending(job.request_id);
function failure(error:unknown){
  return error instanceof TutorError ? {error:error.message,code:error.code,usage:error.usage??null,diagnostics:error.diagnostics??null} : {
    error:"The review connection was interrupted. Your working is saved. No automatic paid retry was sent.",code:"review_uncertain",usage:null,diagnostics:null,
  };
}
async function finishFailure(db:SupabaseClient,userId:string,id:string,error:unknown){
  const value=failure(error);
  const {error:saveError}=await db.from(table).update({status:"failed",result:{error:value.error,code:value.code},error_code:value.code,usage:value.usage,completed_at:new Date().toISOString(),...(value.diagnostics?.responseId?{provider_id:value.diagnostics.responseId}:{})}).eq("id",id).eq("user_id",userId).in("status",["reserved","pending"]).retry(false);
  if(saveError)throw new StudioError(503,"The review status could not be saved. Reopen this saved review later; no automatic paid retry was sent.");
  return value;
}
async function finish(db:SupabaseClient,userId:string,id:string,result:Awaited<ReturnType<typeof pollBackgroundReview>>){
  if(!result)throw new Error("Missing completed review");
  const feedback={...result.feedback,model:result.model,usage:result.usage,timing:result.timing,serviceTier:result.serviceTier,cached:false};
  const {error}=await db.from(table).update({status:"complete",result:feedback,usage:result.usage,model:result.model,completed_at:new Date().toISOString()}).eq("id",id).eq("user_id",userId).in("status",["reserved","pending"]).retry(false);
  if(error)throw new StudioError(503,"Your review finished but could not be saved yet. Reopen this saved review later; no new paid request was sent.");
  return feedback;
}
export async function reviewStatus(db:SupabaseClient,user:User,id:unknown){
  const requestId=z.string().uuid().parse(id);const job=await load(db,user.id,requestId);
  if(!job)return {status:"missing",requestId};
  if(job.status==="complete"||job.status==="failed")return view(job);
  if(job.status==="reserved"&&!job.provider_id){
    if(Date.now()-Date.parse(job.created_at)>120_000){
      await finishFailure(db,user.id,job.id,new Error("Provider acceptance unknown"));
      return view((await load(db,user.id,requestId))!);
    }
    return pending(requestId);
  }
  if(!job.provider_id)return pending(requestId);
  const config={...tutorConfig(process.env),model:job.model,effort:"high" as const};
  try{
    const result=await pollBackgroundReview(job.provider_id,job.review_context,config,Date.parse(job.created_at));
    if(!result)return pending(requestId);
    const feedback=await finish(db,user.id,job.id,result);
    await deleteProviderReview(job.provider_id,config);
    return {status:"complete",requestId,feedback};
  }catch(error){
    // A concurrent poll may already have persisted and removed the provider response.
    const latest=await load(db,user.id,requestId);
    if(latest&&(latest.status==="complete"||latest.status==="failed"))return view(latest);
    if(error instanceof TutorError){
      await finishFailure(db,user.id,job.id,error);
      await deleteProviderReview(job.provider_id,config);
      return view((await load(db,user.id,requestId))!);
    }
    throw error;
  }
}
export async function startReview(db:SupabaseClient,user:User,input:z.infer<typeof ReviewRequest>,question:ReleasedQuestion){
  const notAccepted=(error:string,httpStatus:number)=>({httpStatus,body:{error,code:"review_not_accepted",accepted:false,requestId:input.requestId}});
  if(!isConfigured()){
    // A previously accepted request stays recoverable if the key is later removed.
    const prior=await load(db,user.id,input.requestId);
    if(prior)return {httpStatus:202,body:pending(input.requestId)};
    return notAccepted("AI feedback is not configured yet. Your working remains saved.",503);
  }
  const config=tutorConfig(process.env,question);
  const normalized={...input,exam:"tmua" as const,qid:question.qid,contentVersion:question.content_version};
  // Validate image bytes, all reference images and nonempty working before reserving any allowance.
  buildReviewPayload(normalized,question,config);
  const payloadHash=createHash("sha256").update(JSON.stringify({...normalized,requestId:undefined,revision:undefined,question,prompt:PROMPT_VERSION,model:config.model,effort:config.effort,budget:config.maxOutputTokens})).digest("hex");
  const context={revision:input.revision,regions:input.regions,groups:input.groups,model:config.model,effort:config.effort};
  const {data:claim,error}=await db.rpc("reserve_tmua_studio_review",{p_user:user.id,p_request:input.requestId,p_hash:payloadHash,p_qid:canonicalQid(question.qid),p_version:question.content_version,p_model:config.model,p_context:context}).retry(false);
  if(error)throw new StudioError(503,"The tutor allowance could not be checked. No AI request was sent.");
  if(claim.status==="complete")return {httpStatus:200,body:{...claim.result,revision:input.revision,cached:true}};
  if(claim.status==="limit")return notAccepted("Your tutor allowance is used up for now. Please try again later.",429);
  if(claim.status==="busy")return notAccepted("A review is already running or was just attempted. Reopen it before requesting another.",409);
  if(claim.status==="conflict")throw new StudioError(409,"This review identifier belongs to different working.","review_conflict");
  if(claim.status!=="claimed"){
    const result=await reviewStatus(db,user,input.requestId);
    return result.status==="complete"&&"feedback" in result?{httpStatus:200,body:{...(result.feedback as object),revision:input.revision,cached:true}}:{httpStatus:result.status==="failed"?409:202,body:result};
  }
  let providerAccepted=false;
  try{
    const result=await startBackgroundReview(normalized,question,config);
    providerAccepted=true;
    if("pending" in result){
      const saved=await db.from(table).update({status:"pending",provider_id:result.providerId,review_context:result.context}).eq("id",claim.id).eq("user_id",user.id).eq("status","reserved").select("id").maybeSingle().retry(false);
      if(saved.error||!saved.data)throw new StudioError(503,"The review started but its recovery link could not be saved. Your working is safe; no automatic paid retry was sent.","review_uncertain");
      return {httpStatus:202,body:pending(input.requestId)};
    }
    if(result.completedProviderId){
      const saved=await db.from(table).update({status:"pending",provider_id:result.completedProviderId,review_context:context}).eq("id",claim.id).eq("user_id",user.id).eq("status","reserved").select("id").maybeSingle().retry(false);
      if(saved.error||!saved.data)throw new StudioError(503,"The completed review's recovery link could not be saved. Your working is safe; no automatic paid retry was sent.","review_uncertain");
    }
    const feedback=await finish(db,user.id,claim.id,result);
    if(result.completedProviderId)await deleteProviderReview(result.completedProviderId,config);
    return {httpStatus:200,body:feedback};
  }catch(error){
    // If persistence alone failed, leave its immutable claim for recovery; never resend.
    if(providerAccepted && error instanceof StudioError)throw error;
    const f=await finishFailure(db,user.id,claim.id,error);
    throw new StudioError(error instanceof TutorError?error.status:503,f.error,f.code);
  }
}
