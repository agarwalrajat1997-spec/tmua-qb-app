import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import ts from "typescript";
import * as policy from "../lib/esat-predictions.ts";

const source = fs.readFileSync("app/api/esat/module-predictions/route.ts", "utf8");
const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } }).outputText;
const modules = ["Mathematics 1", "Mathematics 2", "Physics"];
const predictions = modules.map((module, i) => ({ module, score: 6.5, confidence: i === 2 ? "low" : "high", guaranteeEligible: i !== 2 }));
function harness({ signedIn = true, access = true } = {}) {
  const calls = [];
  const admin = {
    from(table) {
      const operations = [];
      const builder = {};
      for (const method of ["select","ilike","in","eq","or","limit","retry","upsert"]) builder[method] = (...args) => { operations.push([method,...args]); return builder; };
      builder.then = resolve => { calls.push({ table, operations }); return Promise.resolve({ data: table === "student_access" ? (access ? [{ product:"esat-question-bank" }] : []) : null, error:null }).then(resolve); };
      return builder;
    },
    async rpc(name, args) { calls.push({name,args}); return {data:null,error:null}; },
  };
  const dependencies = {
    "@/app/api/esat/qb/_server": { adminClient:()=>admin,json:(body,status=200)=>Response.json(body,{status}) },
    "@/lib/supabase/server": { createSupabaseServerClient:async()=>({auth:{getUser:async()=>({data:{user:signedIn?{id:"verified-user",email:"student_a@example.com"}:null},error:null})}}) },
    "@/lib/auth/service-recovery": { isMissingSession:()=>false,withServiceTimeout:promise=>promise },
    "@/lib/esat-predictions": policy,
    "@/lib/server/esat-module-prediction-service": {
      getEsatModuleOverview:async(_,userId)=>{calls.push({overviewUser:userId});return{ok:true,predictions};},
      readEsatPredictionPlan:async(_,userId)=>{calls.push({lockUser:userId});return{plan:{exam_date:"2026-01-01"},lock:{predictions}};},
    },
  };
  const exports={}; vm.runInNewContext(compiled,{exports,require:name=>{assert.ok(dependencies[name],name);return dependencies[name];},Response,Request,URL,Date,Intl,console});
  return{...exports,calls};
}
const request = (method, body, origin="https://apps.thrivingscholars.com") => new Request("https://apps.thrivingscholars.com/api/esat/module-predictions",{method,headers:{"content-type":"application/json",origin},body:JSON.stringify(body)});
assert.equal((await harness({signedIn:false}).GET()).status,401);
assert.equal((await harness({access:false}).GET()).status,403);
assert.equal((await harness().PUT(request("PUT",{},"https://unrelated.example"))).status,403);
const valid=harness();
assert.equal((await valid.PUT(request("PUT",{userId:"forged-user",modules,examDate:"2099-01-10",predictions:[{score:9}]}))).status,200);
const rpc=valid.calls.find(call=>call.name==="esat_save_exam_plan");
assert.equal(rpc.args.p_user_id,"verified-user"); assert.equal(rpc.args.p_predictions,undefined);
assert.ok(valid.calls.find(call=>call.table==="student_access").operations.some(op=>op[0]==="ilike" && op[2]==="student\\_a@example.com"));
assert.equal((await harness().PUT(request("PUT",{modules:["Mathematics 1","Physics","Physics"],examDate:"2099-01-10"}))).status,400);
assert.equal((await harness().PUT(request("PUT",{modules,examDate:"2020-01-01"}))).status,400);
const result=harness();
assert.equal((await result.POST(request("POST",{userId:"forged-user",predictions:[{score:9}],actualScores:{"Mathematics 1":5.9,"Mathematics 2":6,Physics:1}}))).status,200);
const written=result.calls.find(call=>call.table==="esat_result_submissions").operations.find(op=>op[0]==="upsert")[1];
assert.equal(written.user_id,"verified-user"); assert.equal(written.verification_status,"pending");
assert.equal(written.assessment.missedCount,1); assert.equal(written.assessment.meetsScoreCondition,false);
const eligible=harness();
assert.equal((await eligible.POST(request("POST",{actualScores:{"Mathematics 1":5.9,"Mathematics 2":5.9,Physics:8}}))).status,200);
assert.equal(eligible.calls.find(call=>call.table==="esat_result_submissions").operations.find(op=>op[0]==="upsert")[1].assessment.meetsScoreCondition,true);
console.log("PASS: module API authentication, entitlements, request origin, server-owned identity/predictions and locked-score result evaluation.");
