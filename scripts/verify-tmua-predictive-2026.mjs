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
const scheduledRefreshes=[];
const environment={NEXT_PUBLIC_SUPABASE_URL:"https://qa.invalid",SUPABASE_SERVICE_ROLE_KEY:"qa-in-memory"};
const cache=new Map();
function load(file){
  const filename=path.resolve(cwd,file);if(cache.has(filename))return cache.get(filename).exports;
  const mod={exports:{}};cache.set(filename,mod);
  const js=ts.transpileModule(readFileSync(filename,"utf8"),{compilerOptions:{target:ts.ScriptTarget.ES2020,module:ts.ModuleKind.CommonJS}}).outputText;
  function localRequire(id){
    if(id==="@/lib/server/preparation-rank-cache")return {
      requestPreparationRankRefresh:(_admin,programme)=>scheduledRefreshes.push(programme),
      readPreparationRankSnapshot:async(_admin,userId,programme,verifiedEmail)=>{
        assert.equal(userId,"qa-user");assert.equal(programme,"tmua");
        assert.equal(verifiedEmail,"qa@example.invalid");
        return {score:null,rank:null,cohortSize:0,status:"temporarily_unavailable"};
      },
    };
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
  const result={calls,inserts,tables,auth:{admin:{listUsers:async()=>({data:{users:[{id:"qa-user",email:"qa@example.invalid",last_sign_in_at:new Date(Date.now()-1000).toISOString()}]},error:null})}}};
  result.from=table=>{
    const call={table,filters:[],orders:[],ranges:[],columns:null};calls.push(call);let inserted,singleRow=false;
    const rows=()=>{let values=tables[table]??[];for(const [field,value] of call.filters)values=values.filter(r=>(field.startsWith('predictor_metadata->>')?r.predictor_metadata?.[field.split('->>')[1]]:r[field])===value);return values;};
    const q={select(columns){call.columns=columns;return q;},eq(field,value){call.filters.push([field,value]);return q;},ilike(field,value){call.filters.push([field,value.toLowerCase()]);return q;},or(){return q;},in(){return q;},gt(){return q;},lte(){return q;},order(field,options){call.orders.push([field,options]);return q;},range(from,to){call.ranges.push([from,to]);return q;},limit(){return q;},
      retry(value){assert.equal(value,false);return q;},
      insert(value){inserted=value;inserts.push({table,value});tables[table]??=[];tables[table].push(...(Array.isArray(value)?value:[{id:"qa-inserted",...value}]));return q;},
      maybeSingle(){singleRow=true;return q;},
      async single(){return {data:inserted?{id:"qa-inserted",...inserted}:rows()[0]??null,error:null};},
      then(resolve,reject){return Promise.resolve({data:singleRow?(inserted?{id:"qa-inserted",...inserted}:rows()[0]??null):rows(),error:null,count:rows().length}).then(resolve,reject);}};
    return q;
  };return result;
}

const {POST}=load("app/api/practice-tests/submit/route.ts");
db=database();
const recoveryId="5a336ae4-5678-4123-8912-0123456789ab";
const submitted=await POST({json:async()=>({test_id:ID,attemptId:recoveryId,score:40,correct_answers:Array(40).fill("H"),answers:answersFor(33),time_spent:Array(40).fill(150),complete:true})});
assert.equal(submitted.status,200);
const saved=db.inserts.find(i=>i.table==="practice_test_attempts").value;
assert.equal(saved.score,33);assert.equal(saved.tmua_score9,7);assert.equal(saved.is_full_timed_attempt,true);
assert.equal(saved.correct_answers.join(""),sourceAnswers.join(""));
assert.equal(saved.predictor_metadata.client_correct_answers_match_canonical,false);
assert.equal(saved.predictor_metadata.client_score_matches_authoritative,false);
assert.equal(saved.predictor_metadata.tmua_predictive_client_attempt_id,recoveryId);
const beforeInvalid=db.inserts.length;
for(const attemptId of ["", "other-owner", "x".repeat(81), {}, "attempt-123-not-hex"]){
  assert.equal((await POST({json:async()=>({test_id:ID,attemptId,answers:answersFor(33)})})).status,400);
}
assert.equal(db.inserts.length,beforeInvalid,"Invalid correlation IDs cannot produce an attempt.");
const {GET:GET_ATTEMPTS}=load("app/api/practice-tests/attempts/route.ts");
const recoveryUrl="https://portal.test/api/practice-tests/attempts?test_id="+ID+"&client_attempt_id="+recoveryId;
db=database([{...row(),predictor_metadata:{tmua_predictive_client_attempt_id:recoveryId}},
  {...row(),id:"other-student",user_id:"other-user",predictor_metadata:{tmua_predictive_client_attempt_id:recoveryId}}]);
let recovered=await GET_ATTEMPTS({url:recoveryUrl});
assert.equal(recovered.status,200);assert.equal(recovered.body.saved,true);assert.notEqual(recovered.body.attempt.id,"other-student");
assert.ok(db.calls.every(c=>c.filters.some(([field,value])=>field==="user_id"&&value==="qa-user")));
assert.ok(db.calls.every(c=>c.filters.some(([field,value])=>field==="predictor_metadata->>tmua_predictive_client_attempt_id"&&value===recoveryId)));
assert.equal(db.inserts.length,0,"Recovery is read-only.");
db=database([{...row(),id:"other-student",user_id:"other-user",predictor_metadata:{tmua_predictive_client_attempt_id:recoveryId}},row()]);
recovered=await GET_ATTEMPTS({url:recoveryUrl});assert.equal(recovered.body.saved,false);assert.equal(recovered.body.attempt,null,"Another owner or old untagged report cannot satisfy recovery.");
assert.equal((await GET_ATTEMPTS({url:recoveryUrl.replace(recoveryId,"invalid")})).status,400);
assert.equal((await GET_ATTEMPTS({url:recoveryUrl.replace(ID,"full-official-2016")})).status,400);
authorised=false;assert.equal((await GET_ATTEMPTS({url:recoveryUrl})).status,401);authorised=true;
await import("./verify-tmua-predictive-portal-save.mjs");

const {GET}=load("app/api/tmua/overview/route.ts");
db=database([row(),row(40,{id:"other-user-attempt",user_id:"other-user"})]);
const overview=await GET();
assert.equal(overview.status,200);
assert.equal(overview.body.predictor.independentTestCount,1);
assert.equal(overview.body.predictor.score,6.75,"Existing one-paper high-score gate is preserved.");
assert.equal(overview.body.preparationRank.score,null,"Missing persisted rank must not fabricate a ranking.");
assert.deepEqual(scheduledRefreshes,["tmua"],"Authenticated request schedules nonblocking maintenance.");
assert.equal(db.calls.some(c=>["student_access","tmua_preparation_rank_exclusions"].includes(c.table)),false,"Default must not enter cohort reads.");
for(const call of db.calls.filter(c=>["practice_test_attempts","tmua_test_attempt_evaluations","tmua_qb_attempt_events"].includes(c.table))){
  assert.ok(call.filters.some(([field,value])=>field==="user_id"&&value==="qa-user"),`${call.table} must stay current-user scoped`);
}
authorised=false;db=database();const unauthorised=await GET();assert.equal(unauthorised.status,401);assert.equal(db.calls.length,0);authorised=true;

// Scheduled maintenance uses exactly the same evidence and cannot double-count
// a stale database evaluation for this code-owned paper.
const {refreshTmuaPreparationRank}=load("lib/server/tmua-preparation-rank-refresh.ts");
db=database([row()]);db.tables.tmua_test_attempt_evaluations=[{...valid,authoritative_tmua_score9:9}];
const refresh=await refreshTmuaPreparationRank(db);
assert.equal(refresh.cohortSize,1);
assert.ok(db.calls.some(c=>c.table==="student_access"));
const rankSnapshot=db.tables.tmua_preparation_rank_snapshots[0];
assert.equal(rankSnapshot.predicted_tmua_score9,6.75);
assert.equal(rankSnapshot.actual_preparation_rank,1);
assert.equal(rankSnapshot.actual_active_cohort_size,1);
assert.equal(rankSnapshot.broad_or_full_independent_test_families,1);
assert.ok(refresh.runId);
// Every paginated cohort read has a deterministic unique key/tie-breaker.
// Primary keys were checked against the production PostgreSQL schema; the
// snapshot user_id is unique inside its already-scoped run_id.
const uniqueOrderKey={student_access:"id",tmua_test_catalog:"test_id",
  tmua_score_conversion_profiles:"profile",tmua_test_attempt_evaluations:"attempt_id",
  tmua_qb_questions:"qid",tmua_qb_attempt_events:"id",practice_test_attempts:"id",
  tmua_preparation_rank_exclusions:"id",tmua_preparation_rank_snapshots:"user_id"};
for(const call of db.calls.filter(call=>call.ranges.length)){
  assert.ok(uniqueOrderKey[call.table],`Unexpected paginated cohort table ${call.table}`);
  assert.ok(call.orders.some(([field])=>field===uniqueOrderKey[call.table]),
    `${call.table} must use its unique ordering key so pages cannot be ambiguously ordered`);
}
console.log("TMUA 2026 predictive verification passed: exact40-question canonical key and strict41-point scale; validity/retakes; forged-score rejection; historical attempts; current-user-only overview; identical background cohort evidence and no duplicate evaluation.");
