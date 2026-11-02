import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { ibHarness } from './ib-component-harness.mjs';

const harness=ibHarness();
const model=harness.load('lib/ib/physics-mock-model.ts');
const content=harness.load('lib/ib/physics-mocks.ts');
const {PHYSICS_MOCKS,cleanAnswers,validateSelfMarks,scoreMock,paperSpec,reportPayload,answerKey}=model;
assert.equal(PHYSICS_MOCKS.length,6);
const seen=new Set();let diagrams=0;
for(const m of PHYSICS_MOCKS){
  for(const paper of ['1','2']){
    const items=content.getMockItems(m.id,paper), spec=paperSpec(m.course,paper);
    assert.equal(items.reduce((s,{question:q})=>s+q.marks,0),spec.marks);
    for(const {question:q} of items){assert(!seen.has(q.id),q.id);seen.add(q.id);assert.equal(q.source.document,'Independent syllabus-authored practice');if(m.course==='sl')assert.equal(q.level,'core');if(q.diagramSvg||q.diagramUrl)diagrams++;}
    for(const section of new Set(items.map(i=>i.section))){const sectionItems=items.filter(i=>i.section===section);assert.deepEqual(Array.from(sectionItems,i=>i.number),Array.from({length:sectionItems.length},(_,n)=>n+1));}
    const full=Object.fromEntries(items.flatMap(({question:q})=>q.questionType==='multiple-choice'?[[q.id,q.correctOption]]:q.parts.map(p=>[answerKey(q.id,p.label),'Worked response'])));
    const allMarks=Object.fromEntries(items.flatMap(({question:q})=>q.parts.map(p=>[answerKey(q.id,p.label),p.marks])));
    const answers=cleanAnswers(items,full), marks=validateSelfMarks(items,allMarks);
    assert.equal(scoreMock(items,answers,marks).total,spec.marks);
    assert.equal(scoreMock(items,cleanAnswers(items,{}),Object.fromEntries(Object.keys(allMarks).map(k=>[k,0]))).total,0);
    assert.equal(scoreMock(items,answers,null).total,null);
    assert.throws(()=>validateSelfMarks(items,{}));
    const key=Object.keys(allMarks)[0];for(const invalid of [-1,100,0.5,'1',null])assert.throws(()=>validateSelfMarks(items,{...allMarks,[key]:invalid}));
    const review={id:'11111111-1111-4111-8111-111111111111',submittedAt:'2026-11-02T12:00:00Z',elapsed:120,answers,selfMarks:marks,score:scoreMock(items,answers,marks),solutions:[]};
    const report=reportPayload(m,paper,review,'student@example.invalid','Student','https://example.invalid');
    assert.equal(report.to_email,'student@example.invalid');assert.match(report.test_title,new RegExp(m.course.toUpperCase()));assert.match(report.paper1+report.paper2,/self-assessed/);assert.match(report.score,new RegExp(`${spec.marks} / ${spec.marks}`));assert.match(report.solution_link,/\?attempt=/);
  }
  const a=content.getMockItems(m.id,'1').filter(i=>i.section==='1A');
  assert.equal(a.length,m.course==='sl'?25:40);
  assert.equal(new Set(a.map(i=>i.question.syllabusCode)).size,m.course==='sl'?19:24);
  const b=content.getMockItems(m.id,'1').filter(i=>i.section==='1B');assert.equal(b.reduce((s,i)=>s+i.question.marks,0),20);assert(b.every(i=>i.question.questionType==='data-based'));
  const p2=content.getMockItems(m.id,'2');assert.equal(new Set(p2.map(i=>i.question.syllabusCode[0])).size,5);
  if(m.course==='hl')assert(p2.filter(i=>i.question.level==='ahl').length>=3);
}
assert.equal(seen.size,282);assert(diagrams>50);

// Exercise the actual route handlers with an in-memory DB adapter. No network or emails.
let user={id:'11111111-1111-4111-8111-111111111111',email:'student@example.invalid'};
let dbFailure=false;const rows=new Map();
const db={auth:{getUser:async()=>({data:{user},error:null})},from(table){assert.equal(table,'ib_physics_mock_attempts');let action='select',patch=null,filters=[];
  const query={select(){return query;},eq(k,v){filters.push([k,v]);return query;},order(){return query;},limit(){return query;},
    insert:async row=>{if(dbFailure)return {error:{code:'503'}};if(rows.has(row.id))return {error:{code:'23505'}};rows.set(row.id,{...row,submitted_at:'2026-11-02T12:00:00Z',self_marks:null});return {error:null};},
    update(value){action='update';patch=value;return query;},
    async maybeSingle(){if(dbFailure)return {data:null,error:{code:'503'}};return {data:[...rows.values()].find(row=>filters.every(([k,v])=>row[k]===v))??null,error:null};},
    then(resolve,reject){try{if(dbFailure)return resolve({error:{code:'503'}});const found=[...rows.values()].filter(row=>filters.every(([k,v])=>row[k]===v));if(action==='update')for(const row of found)Object.assign(row,patch);resolve({data:found,error:null});}catch(e){reject(e);}}
  };return query;
}};
const api=ibHarness({moduleMocks:{'@/lib/supabase/server':{createSupabaseServerClient:async()=>db}}}).load('app/api/ib/mocks/[id]/route.ts');
const m=PHYSICS_MOCKS[0],id='22222222-2222-4222-8222-222222222222',items=content.getMockItems(m.id,'1');
const correct=Object.fromEntries(items.filter(i=>i.question.correctOption).map(i=>[i.question.id,i.question.correctOption]));
const body={action:'submit',attemptId:id,paper:'1',answers:correct,elapsed:100};
const post=(value,origin='https://example.invalid')=>api.POST(new Request(`https://example.invalid/api/ib/mocks/${m.id}`,{method:'POST',headers:{origin,'Content-Type':'application/json'},body:JSON.stringify(value)}),{params:Promise.resolve({id:m.id})});
const get=()=>api.GET(new Request(`https://example.invalid/api/ib/mocks/${m.id}?attempt=${id}`),{params:Promise.resolve({id:m.id})});
assert.equal((await post(body,'https://evil.invalid')).status,403);
const account=user;user=null;assert.equal((await post(body)).status,401);assert.equal((await get()).status,401);user=account;
assert.equal((await post({...body,answers:{[items[0].question.id]:'E'}})).status,400);
assert.equal((await post({...body,elapsed:99999})).status,400);
dbFailure=true;assert.equal((await post(body)).status,503);dbFailure=false;
let response=await post(body);assert.equal(response.status,200);let data=await response.json();assert.equal(data.review.score.mcq,25);assert.equal(data.review.score.total,null);assert(data.review.solutions.length>25);
response=await post({...body,answers:{}});assert.equal((await response.json()).review.score.mcq,25,'Retry must not replace answers');assert.equal(rows.size,1);
user={id:'33333333-3333-4333-8333-333333333333',email:'other@example.invalid'};assert.equal((await get()).status,404);assert.equal((await post(body)).status,404);user=account;
assert.equal((await post({...body,action:'mark',selfMarks:{}})).status,400);
const marks=Object.fromEntries(items.flatMap(({question:q})=>q.parts.map(p=>[answerKey(q.id,p.label),p.marks])));
response=await post({...body,action:'mark',selfMarks:marks});assert.equal(response.status,200);assert.equal((await response.json()).review.score.total,45);
assert.equal((await get()).status,200);
const migration=readFileSync('supabase/migrations/20261102090000_ib_physics_mock_attempts.sql','utf8');assert.match(migration,/enable row level security/);assert.match(migration,/grant update\(self_marks, marked_at\)/);assert.doesNotMatch(migration,/grant update on/);
console.log(JSON.stringify({status:'passed',mocks:6,paperSittings:12,uniqueQuestions:seen.size,diagrams,checks:'Exact IB totals/timings; all applicable Paper 1A subtopics; SL/HL separation; unique numbering; automatic scoring; bounded self-marks; private API; immutable retry; history; EmailJS payload; no live mail sent'}));
