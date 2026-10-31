import test from "node:test";
import assert from "node:assert/strict";
import type { SupabaseClient } from "@supabase/supabase-js";
import { catalogue, questionGuide, resolveQuestion, publicQuestion } from "./catalogue";
import { assertOrigin, assertViewer, isDevelopmentPreview, StudioError } from "./http";
import { loadNotebook, saveNotebook } from "./notebooks";
import { tutorConfig } from "./tutor";
import { ReviewRequest } from "./contracts";
import { startReview, reviewStatus } from "./reviews";
import { readFileSync } from "node:fs";

test("all 2178 eligible questions have unique stable identity, exact guide version/hash and easy-first order",()=>{
  assert.equal(catalogue.length,2178);
  assert.equal(new Set(catalogue.map(q=>q.qid)).size,2178);
  assert.equal(new Set(catalogue.map(q=>q.display_order)).size,2178);
  for(const [i,metadata] of catalogue.entries()){
    assert.ok(Number.isSafeInteger(metadata.display_order)&&metadata.display_order>0);
    const q=resolveQuestion(metadata.qid,metadata.content_version)!;
    const guide=questionGuide(q);
    assert.equal(guide.qid,metadata.qid);assert.equal(guide.version_id,metadata.content_version);assert.equal(guide.source_sha256,metadata.source_sha256);
    assert.equal(resolveQuestion(metadata.audit_qid,metadata.content_version),q);
    assert.equal(resolveQuestion(metadata.qid,"wrong-version"),undefined);
    const visible=publicQuestion(q);
    assert.ok(!("answer" in visible)&&!("solution_html" in visible)&&!("audited_reference" in visible));
    if(i&&catalogue[i-1].topic===metadata.topic)assert.ok(catalogue[i-1].difficulty<=metadata.difficulty);
  }
  const eligibility=JSON.parse(readFileSync("content/tmua-studio/eligibility.json","utf8"));
  assert.equal(eligibility.excluded_ids.length,22);
  for(const qid of eligibility.excluded_ids)assert.equal(resolveQuestion(qid),undefined);
});
test("trusted difficulty always selects the requested high reasoning model",()=>{
  for(let difficulty=1;difficulty<=5;difficulty++){
    const config=tutorConfig({OPENAI_API_KEY:"test-only",OPENAI_MODEL:"ignored",OPENAI_REASONING_EFFORT:"xhigh"},{exam:"tmua",difficulty});
    assert.equal(config.model,difficulty<=2?"gpt-6.1-terra":"gpt-6-astra");assert.equal(config.effort,"high");
  }
});
test("mutations reject other origins and account changes",()=>{
  assert.throws(()=>assertOrigin(new Request("https://apps.thrivingscholars.com/api/tmua/studio",{headers:{Origin:"https://other.example","X-TS-Studio":"1"}})),StudioError);
  assert.throws(()=>assertOrigin(new Request("https://apps.thrivingscholars.com/api/tmua/studio")),StudioError);
  assert.throws(()=>assertViewer("alice","bob"),StudioError);
  assertOrigin(new Request("https://apps.thrivingscholars.com/api/tmua/studio",{headers:{Origin:"https://apps.thrivingscholars.com","X-TS-Studio":"1"}}));
});
test("origin follows incoming Host through Next internal URLs without allowing cross-origin writes",()=>{
  const localHeaders={Origin:"http://127.0.0.1:8450",Host:"127.0.0.1:8450","X-TS-Studio":"1"};
  assertOrigin(new Request("http://localhost:8450/api/tmua/studio",{headers:localHeaders}),{});
  assert.throws(()=>assertOrigin(new Request("http://localhost:8450/api/tmua/studio",{headers:{...localHeaders,Origin:"http://other.example:8450"}}),{}),StudioError);
  assert.throws(()=>assertOrigin(new Request("http://localhost:8450/api/tmua/studio",{headers:{...localHeaders,Origin:"http://127.0.0.1:8451"}}),{}),StudioError);
  const publicHeaders={Origin:"https://apps.thrivingscholars.com",Host:"apps.thrivingscholars.com","X-TS-Studio":"1","X-Forwarded-Proto":"https"};
  assertOrigin(new Request("http://localhost:3000/api/tmua/studio",{headers:publicHeaders}),{VERCEL:"1"});
  assertOrigin(new Request("https://apps.thrivingscholars.com/api/tmua/studio",{headers:publicHeaders}),{});
  assert.throws(()=>assertOrigin(new Request("http://localhost:3000/api/tmua/studio",{headers:publicHeaders}),{}),StudioError);
  assert.throws(()=>assertOrigin(new Request("http://localhost:3000/api/tmua/studio",{headers:{...publicHeaders,Origin:"https://evil.example","X-Forwarded-Host":"evil.example"}}),{VERCEL:"1"}),StudioError);
  assert.throws(()=>assertOrigin(new Request("https://apps.thrivingscholars.com/api/tmua/studio",{headers:{...publicHeaders,Host:"apps.thrivingscholars.com,evil.example"}}),{}),StudioError);
  assert.throws(()=>assertOrigin(new Request("https://apps.thrivingscholars.com/api/tmua/studio",{headers:{...publicHeaders,"Sec-Fetch-Site":"cross-site"}}),{}),StudioError);
});
test("production never permits the local read-only preview",()=>{
  assert.equal(isDevelopmentPreview({NODE_ENV:"production",DEV_BYPASS_TMUA_ACCESS:"1"}),false);
  assert.equal(isDevelopmentPreview({NODE_ENV:"development",DEV_BYPASS_TMUA_ACCESS:"1"}),true);
  assert.equal(isDevelopmentPreview({NODE_ENV:"development"}),false);
});
test("review schema rejects attempted model/user injection",()=>{
  assert.equal(ReviewRequest.safeParse({exam:"tmua",qid:"qid",requestId:crypto.randomUUID(),revision:0,note:"work",structure:{},model:"cheap",userId:"victim"}).success,false);
});
function fakeDb(){
  const rows=new Map<string,any>();
  const db={from(table:string){assert.equal(table,"user_progress");let mode="select",payload:any,filters:[string,unknown][]=[];
    const query:any={select(){return query;},eq(k:string,v:unknown){filters.push([k,v]);return query;},insert(row:any){mode="insert";payload=row;return query;},update(row:any){mode="update";payload=row;return query;},maybeSingle(){return query;},retry(){
      const key=mode==="insert"?`${payload.user_id}|${payload.product}|${payload.key}`:filters.filter(([k])=>["user_id","product","key"].includes(k)).map(([,v])=>v).join("|");
      const old=rows.get(key);
      if(mode==="insert"){if(old)return Promise.resolve({data:null,error:{code:"23505"}});rows.set(key,payload);return Promise.resolve({data:payload,error:null});}
      if(mode==="update"){const version=filters.find(([k])=>k==="data->>version")?.[1];if(!old||String(old.data.version)!==version)return Promise.resolve({data:null,error:null});const next={...old,...payload};rows.set(key,next);return Promise.resolve({data:next,error:null});}
      return Promise.resolve({data:old??null,error:null});
    }};return query;}} as unknown as SupabaseClient;
  return db;
}
test("notebooks are user scoped and compare-and-swap prevents lost updates",async()=>{
  const db=fakeDb(),alice={id:"alice",email:"alice@example.com"},bob={id:"bob",email:"bob@example.com"};const key="board:user:alice:practice:tmua:Q@v1";
  assert.deepEqual(await loadNotebook(db,alice.id,key),{version:0});
  assert.equal((await saveNotebook(db,alice,{key,baseVersion:0,value:{note:"first"}})).version,1);
  const writes=await Promise.allSettled([saveNotebook(db,alice,{key,baseVersion:1,value:{note:"second"}}),saveNotebook(db,alice,{key,baseVersion:1,value:{note:"competing"}})]);
  assert.equal(writes.filter(x=>x.status==="fulfilled").length,1);
  assert.equal((await loadNotebook(db,alice.id,key) as any).value.note,"second");
  await assert.rejects(()=>loadNotebook(db,bob.id,key),StudioError);
  await assert.rejects(()=>saveNotebook(db,bob,{key,baseVersion:2,value:{note:"hijack"}}),StudioError);
});
function fakeReviewDb(){
  const rows:any[]=[];
  const db={
    rpc(_name:string,p:any){return {retry(){
      const old=rows.find(x=>x.user_id===p.p_user&&x.request_id===p.p_request);
      if(old)return Promise.resolve({error:null,data:old.payload_hash===p.p_hash?{status:old.status,id:old.id,result:old.result}:{status:"conflict"}});
      if(rows.some(x=>x.user_id===p.p_user&&["reserved","pending"].includes(x.status)))return Promise.resolve({error:null,data:{status:"busy"}});
      const row={id:crypto.randomUUID(),user_id:p.p_user,request_id:p.p_request,payload_hash:p.p_hash,status:"reserved",model:p.p_model,review_context:p.p_context,created_at:new Date().toISOString()};rows.push(row);
      return Promise.resolve({error:null,data:{status:"claimed",id:row.id}});
    }};},
    from(table:string){assert.equal(table,"tmua_studio_review_jobs");const filters:[string,any][]=[];let update:any;
      const query:any={select(){return query;},eq(k:string,v:any){filters.push([k,v]);return query;},in(k:string,v:any[]){filters.push([k,v]);return query;},update(v:any){update=v;return query;},maybeSingle(){return query;},retry(){
        const row=rows.find(x=>filters.every(([k,v])=>Array.isArray(v)?v.includes(x[k]):x[k]===v));if(update&&row)Object.assign(row,update);return Promise.resolve({data:row??null,error:null});
      }};return query;
    },
  } as unknown as SupabaseClient;
  return {db,rows};
}
test("accepted review recovers across requests without a second paid call and is isolated by user",async()=>{
  const oldFetch=globalThis.fetch,oldKey=process.env.OPENAI_API_KEY,oldEnable=process.env.ENABLE_AI;
  process.env.OPENAI_API_KEY="test-only-never-sent";process.env.ENABLE_AI="true";
  let posts=0,finished=false;
  globalThis.fetch=async (_url,init)=>{
    if(init?.method==="POST"){posts++;return Response.json({id:"resp_test",status:"queued"});}
    if(init?.method==="DELETE")return Response.json({deleted:true});
    if(!finished)return Response.json({id:"resp_test",status:"in_progress"});
    return Response.json({id:"resp_test",status:"completed",model:"gpt-6.1-terra",output:[{type:"message",content:[{type:"output_text",text:JSON.stringify({summary:"Checked",lines:[{n:1,t:"x=2",s:"correct",c:1,m:1,e:"",r:null}],nextStep:"Continue",coverage:"complete",answerLine:null,alternative:null,visual:null})}]}]});
  };
  try{
    const {db}=fakeReviewDb(),user={id:"alice",email:"alice@example.com"},q=resolveQuestion(catalogue[0].qid)!;
    const input=ReviewRequest.parse({exam:"tmua",qid:catalogue[0].qid,contentVersion:q.content_version,requestId:crypto.randomUUID(),revision:2,note:"x=2",structure:{steps:[]}});
    assert.equal((await startReview(db,user,input,q)).httpStatus,202);
    assert.equal((await startReview(db,user,input,q)).httpStatus,202);assert.equal(posts,1);
    assert.equal((await reviewStatus(db,{id:"bob",email:"bob@example.com"},input.requestId)).status,"missing");
    delete process.env.OPENAI_API_KEY;
    assert.equal((await startReview(db,user,input,q)).httpStatus,202);assert.equal(posts,1);
    process.env.OPENAI_API_KEY="test-only-never-sent";finished=true;
    assert.equal((await reviewStatus(db,user,input.requestId)).status,"complete");
    const cached=await startReview(db,user,{...input,revision:3},q);assert.equal(cached.httpStatus,200);assert.equal((cached.body as any).revision,3);assert.equal(posts,1);
  }finally{globalThis.fetch=oldFetch;if(oldKey===undefined)delete process.env.OPENAI_API_KEY;else process.env.OPENAI_API_KEY=oldKey;if(oldEnable===undefined)delete process.env.ENABLE_AI;else process.env.ENABLE_AI=oldEnable;}
});
test("ambiguous provider failure is durable and never automatically retried",async()=>{
  const oldFetch=globalThis.fetch,oldKey=process.env.OPENAI_API_KEY,oldEnable=process.env.ENABLE_AI;
  process.env.OPENAI_API_KEY="test-only-never-sent";process.env.ENABLE_AI="true";let posts=0;
  globalThis.fetch=async()=>{posts++;throw new Error("connection lost after possible acceptance");};
  try{
    const {db}=fakeReviewDb(),user={id:"alice",email:"alice@example.com"},q=resolveQuestion(catalogue[0].qid)!;
    const input=ReviewRequest.parse({exam:"tmua",qid:q.qid,contentVersion:q.content_version,requestId:crypto.randomUUID(),revision:0,note:"x=2",structure:{steps:[]}});
    await assert.rejects(()=>startReview(db,user,input,q),StudioError);
    assert.equal((await reviewStatus(db,user,input.requestId)).status,"failed");
    assert.equal((await startReview(db,user,input,q)).httpStatus,409);assert.equal(posts,1);
  }finally{globalThis.fetch=oldFetch;if(oldKey===undefined)delete process.env.OPENAI_API_KEY;else process.env.OPENAI_API_KEY=oldKey;if(oldEnable===undefined)delete process.env.ENABLE_AI;else process.env.ENABLE_AI=oldEnable;}
});
