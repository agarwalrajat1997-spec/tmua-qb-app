import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { createRequire } from "node:module";
import path from "node:path";
import vm from "node:vm";
import {
  TMUA_PREDICTIVE_2026_ID as ID,
  TMUA_PREDICTIVE_2026_CANONICAL as canonical,
  TMUA_PREDICTIVE_2026_SCORES as scores,
  evaluateTmuaPredictive2026Attempt,
  buildTmuaPredictive2026Evaluations,
} from "../lib/server/tmua-predictive-2026.ts";
import { getCanonicalTmuaTest } from "../lib/server/tmua-canonical-tests.ts";
import { adaptTmuaTestEvaluation } from "../lib/server/tmua-predictor-v1-evidence-adapter.ts";
import { calculateTmuaPredictorV1 } from "../lib/server/tmua-predictor-v1-engine.ts";

const html = readFileSync(canonical.sourceFile,"utf8");
const data = JSON.parse(html.match(/<script[^>]*id="tmua-data"[^>]*>([\s\S]*?)<\/script>/)[1]);
const sourceAnswers = data.papers.flatMap(p => p.questions.map(q => q.correctAnswer));
assert.equal(data.id,ID);
assert.deepEqual([...canonical.answers],sourceAnswers);
assert.equal(canonical.canonicalSha256,createHash("sha256").update(JSON.stringify(sourceAnswers)).digest("hex"));
assert.deepEqual([...scores],data.predictor.table);
assert.equal(scores[24],4.8);assert.equal(scores[33],7);
assert.equal(getCanonicalTmuaTest(ID),canonical);

const answersFor = raw => sourceAnswers.map((a,i) => i < raw ? a : a === "A" ? "B" : "A");
const row = (raw=33, extra={}) => ({id:"qa-new-1",user_id:"qa-user",test_id:ID,submitted_at:"2026-09-20T00:00:00Z",answers:answersFor(raw),time_spent:Array(40).fill(150),...extra});
const valid = evaluateTmuaPredictive2026Attempt(row());
assert.equal(valid.authoritative_tmua_score9,7);
assert.equal(valid.effective_weight,0.95);
assert.equal(valid.combined_score_eligible,true);
assert.equal(evaluateTmuaPredictive2026Attempt(row(24)).authoritative_tmua_score9,4.8);
assert.equal(evaluateTmuaPredictive2026Attempt(row(33,{time_spent:Array(40).fill(1)})).predictor_eligible,false);
assert.equal(evaluateTmuaPredictive2026Attempt(row(33,{predictor_metadata:{tmua_predictive_2026_complete:false}})),null);
assert.equal(evaluateTmuaPredictive2026Attempt(row(33,{answers:Array(39).fill("A")})),null);
assert.equal(evaluateTmuaPredictive2026Attempt(row(33,{time_spent:Array(39).fill(150)})),null);
const partialAnswers = answersFor(33);partialAnswers[18]=null;partialAnswers[19]=null;partialAnswers[17]=null;
const partial = evaluateTmuaPredictive2026Attempt(row(33,{answers:partialAnswers}));
assert.equal(partial.combined_score_eligible,false);
assert.equal(partial.authoritative_tmua_score9,null,"Partial paper must never receive the custom full-paper /9 conversion.");

const profiles = Array.from({length:12},(_,i)=>({profileId:`test-profile-${i}`,scores:Array.from({length:41},(_,raw)=>1+raw/5)}));
const retakes = buildTmuaPredictive2026Evaluations([
  row(33,{id:"qa-latest",submitted_at:"2026-09-21T00:00:00Z"}),
  row(24,{id:"qa-first"}),
]);
const predicted = calculateTmuaPredictorV1({conversionProfiles:profiles,activeTopics:["Algebra"],qbEvents:[],testAttempts:retakes.map(adaptTmuaTestEvaluation)});
assert.equal(predicted.independentTestCount,1);
assert.equal(predicted.predictedTmuaScore9,5.35,"Retakes retain 75% first / 25% latest.");
assert.equal(predicted.testWeight,0.95);

// Exercise actual API handlers with in-memory Supabase/NextResponse adapters.
// No requests, emails, database writes, or deployment are performed.
const require = createRequire(import.meta.url), ts=require("typescript"), cwd=process.cwd();
let db, authorised=true;
const environment={NEXT_PUBLIC_SUPABASE_URL:"https://qa.invalid",SUPABASE_SERVICE_ROLE_KEY:"qa-in-memory"};
const cache=new Map();
function load(file){
  const filename=path.resolve(cwd,file);if(cache.has(filename))return cache.get(filename).exports;
  const mod={exports:{}};cache.set(filename,mod);
  const js=ts.transpileModule(readFileSync(filename,"utf8"),{compilerOptions:{target:ts.ScriptTarget.ES2020,module:ts.ModuleKind.CommonJS}}).outputText;
  function localRequire(id){
    if(id==="next/server")return {NextResponse:{json:(body,options={})=>({body,status:options.status??200})}};
    if(id==="@/lib/supabase/server")return {createSupabaseServerClient:async()=>({auth:{getUser:async()=>({data:{user:authorised?{id:"qa-user",email:"qa@example.invalid"}:null},error:null})},from:(...args)=>db.from(...args)})};
    if(id==="@supabase/supabase-js")return {createClient:()=>db};
    const resolved=id.startsWith("@/")?path.join(cwd,id.slice(2)):id.startsWith(".")?path.resolve(path.dirname(filename),id):null;
    if(resolved)return load(resolved.endsWith(".ts")?resolved:resolved+".ts");
    return require(id);
  }
  vm.runInNewContext(js,{exports:mod.exports,module:mod,require:localRequire,console,process:{env:environment},Date,JSON,Math,Number,String,Object,Array,Set,Map,URL,AbortController,setTimeout,clearTimeout},{filename});
  return mod.exports;
}
function database(attemptRows=[]){
  const calls=[],inserts=[];
  const tables={
    tmua_score_conversion_profiles:profiles.map(p=>({profile:p.profileId,score_values:p.scores})),
    tmua_test_catalog:[],tmua_test_attempt_evaluations:[],
    tmua_qb_questions:[{qid:"qa-q",answer:"A",topic:"Algebra",is_active:true}],
    tmua_qb_attempt_events:[],practice_test_attempts:attemptRows,
    student_access:[{email:"qa@example.invalid",product:"practice-tests",approved:true,expires_at:null}],
    tmua_preparation_rank_exclusions:[],
  };
  const result={calls,inserts,tables,auth:{admin:{listUsers:async()=>({data:{users:[{id:"qa-user",email:"qa@example.invalid",last_sign_in_at:new Date().toISOString()}]},error:null})}}};
  result.from=table=>{
    const call={table,filters:[],columns:null};calls.push(call);let inserted;
    const rows=()=>{let values=tables[table]??[];for(const [field,value] of call.filters)values=values.filter(r=>r[field]===value);return values;};
    const q={select(columns){call.columns=columns;return q;},eq(field,value){call.filters.push([field,value]);return q;},in(){return q;},gt(){return q;},lte(){return q;},order(){return q;},range(){return q;},limit(){return q;},
      insert(value){inserted=value;inserts.push({table,value});tables[table]??=[];tables[table].push(...(Array.isArray(value)?value:[{id:"qa-inserted",...value}]));return q;},
      async maybeSingle(){return {data:inserted?{id:"qa-inserted",...inserted}:rows()[0]??null,error:null};},
      async single(){return {data:inserted?{id:"qa-inserted",...inserted}:rows()[0]??null,error:null};},
      then(resolve,reject){return Promise.resolve({data:rows(),error:null,count:rows().length}).then(resolve,reject);}};
    return q;
  };return result;
}

const {POST}=load("app/api/practice-tests/submit/route.ts");
db=database();
const submitted=await POST({json:async()=>({test_id:ID,score:40,correct_answers:Array(40).fill("H"),answers:answersFor(33),time_spent:Array(40).fill(150),complete:true})});
assert.equal(submitted.status,200);
const saved=db.inserts.find(i=>i.table==="practice_test_attempts").value;
assert.equal(saved.score,33);assert.equal(saved.tmua_score9,7);assert.equal(saved.is_full_timed_attempt,true);
assert.equal(saved.correct_answers.join(""),sourceAnswers.join(""));
assert.equal(saved.predictor_metadata.client_correct_answers_match_canonical,false);
assert.equal(saved.predictor_metadata.client_score_matches_authoritative,false);

const {GET}=load("app/api/tmua/overview/route.ts");
db=database([row(),row(40,{id:"other-user-attempt",user_id:"other-user"})]);
const overview=await GET();
assert.equal(overview.status,200);
assert.equal(overview.body.predictor.independentTestCount,1);
assert.equal(overview.body.predictor.score,6.75,"Existing one-paper high-score gate is preserved.");
assert.equal(overview.body.preparationRank.score,null,"Default mode must retain lightweight rank fallback.");
assert.equal(db.calls.some(c=>["student_access","tmua_preparation_rank_exclusions"].includes(c.table)),false,"Default must not enter cohort reads.");
for(const call of db.calls.filter(c=>["practice_test_attempts","tmua_test_attempt_evaluations","tmua_qb_attempt_events"].includes(c.table))){
  assert.ok(call.filters.some(([field,value])=>field==="user_id"&&value==="qa-user"),`${call.table} must stay current-user scoped`);
}
authorised=false;db=database();const unauthorised=await GET();assert.equal(unauthorised.status,401);assert.equal(db.calls.length,0);authorised=true;

// The full mode must also use the same evidence and cannot double-count a
// stale database evaluation for this code-owned paper.
environment.TMUA_OVERVIEW_FULL_MODE="enabled";
db=database([row()]);db.tables.tmua_test_attempt_evaluations=[{...valid,authoritative_tmua_score9:9}];
const full=await GET();
assert.equal(full.status,200);
assert.equal(full.body.predictor.independentTestCount,1);
assert.equal(full.body.predictor.score,6.75);
assert.ok(db.calls.some(c=>c.table==="student_access"));
assert.equal(full.body.preparationRank.cohortSize,1);
console.log("TMUA 2026 predictive verification passed: exact40-question canonical key and strict41-point scale; validity/retakes; forged-score rejection; historical attempts; current-user-only default overview; matching full-mode evidence and no duplicate evaluation.");
