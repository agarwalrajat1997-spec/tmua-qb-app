import papers from "@/lib/amc-edition/tests.json";
import { adminClient, json, requireAMCAccess } from "../qb/_server";
export const runtime = "nodejs";
export const dynamic = "force-dynamic";
type Paper = { key: string; minutes:number; level:number; version:string; title:string };
const registry:Record<string,Paper> = papers;
const valid = (x:unknown): x is (string|null)[] => Array.isArray(x) && x.length===25 && x.every(v=>v===null || (typeof v==="string" && /^[A-E]$/.test(v)));
const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
export async function POST(req:Request) {
 const access=await requireAMCAccess(); if(!access.ok)return access.response;
 const input=await req.json().catch(()=>null); const email=access.user.email!.toLowerCase();
 if(!input || typeof input.paper!=="string" || !Object.hasOwn(registry,input.paper) || !uuid.test(String(input.id)) || !["start","save","submit"].includes(input.op))return json({error:"Invalid attempt"},400);
 const spec=registry[input.paper];const db=adminClient();const table=()=>db.from("amc_practice_attempts");
 const read=()=>table().select("*").eq("id",input.id).eq("student_email",email).eq("paper",input.paper).maybeSingle();
 if(input.op==="start"){
   const now=Date.now();const {error}=await table().insert({id:input.id,student_email:email,paper:input.paper,level:spec.level,version:spec.version,scoring_key:spec.key,started_at:new Date(now).toISOString(),due_at:new Date(now+spec.minutes*60000).toISOString(),responses:Array(25).fill(null)});
   if(error&&error.code!=="23505")return json({error:"Could not start the saved attempt."},503);
 }
 const {data:row,error}=await read();if(error)return json({error:"Could not read the attempt."},503);if(!row)return json({error:"Attempt not found."},404);
 const receipt=(r:typeof row)=>({id:r.id,testMailbox:email.endsWith("+amc-qa@thrivingscholars.com")?email:null,correct:r.correct,incorrect:r.incorrect,blanks:r.blanks,points:Number(r.points),maximum:r.level===8?25:150,key:r.scoring_key,answers:r.responses,submittedAt:r.submitted_at,solutionPath:"/amc-practice-tests/tests/"+r.paper+"/worked-solutions.pdf"});
 if(row.submitted_at)return json({finished:true,receipt:receipt(row)});
 if(input.op==="start")return json({id:row.id,dueAt:row.due_at,answers:row.responses});
 if(!valid(input.answers))return json({error:"Expected 25 choices or blanks."},400);
 const time=Date.now();const expired=time>Date.parse(row.due_at)+12000;
 if(input.op==="save"){
  if(expired)return json({expired:true},409);
  const {error:saveError}=await table().update({responses:input.answers}).eq("id",row.id).eq("student_email",email).is("submitted_at",null);
  return saveError?json({error:"Could not save choices."},503):json({saved:true});
 }
 // A late/offline submission grades only the responses received before the deadline.
 const answers:(string|null)[]=expired?row.responses:input.answers;const correct=answers.filter((a,i)=>a===row.scoring_key[i]).length,blanks=answers.filter(a=>a===null).length,incorrect=25-correct-blanks;
 const points=row.level===8?correct:6*correct+1.5*blanks;
 const {data:finished,error:endError}=await table().update({responses:answers,submitted_at:new Date(time).toISOString(),correct,incorrect,blanks,points}).eq("id",row.id).eq("student_email",email).is("submitted_at",null).select("*").maybeSingle();
 if(endError)return json({error:"Could not submit the attempt; please retry."},503);
 const final=finished||(await read()).data; if(!final?.submitted_at)return json({error:"Please retry submission."},503);
 return json({finished:true,receipt:receipt(final)});
}
