import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {ibHarness} from './ib-component-harness.mjs';
const h=ibHarness(),m=h.load('lib/ib/economics-mock-model.ts'),server=h.load('lib/ib/economics-mocks.ts');
const fixtures=new Map(),metas=m.ECONOMICS_MOCKS.flatMap(g=>g.papers);
assert.equal(metas.length,10);assert.equal(metas.reduce((n,p)=>n+p.marks,0),380);
const full=(qs)=>Object.fromEntries(qs.flatMap(q=>q.parts.map(a=>[m.answerKey(q.id,a.label),a.marks])));
for(const meta of metas){
 const p=JSON.parse(readFileSync('content/ib/economics-mocks-2022/papers/'+meta.id+'.json','utf8'));
 fixtures.set(meta.id,server.validateEconomicsMockPaper(p,meta));
 const prompt=server.economicsMockPrompt(p,meta);
 assert.doesNotMatch(JSON.stringify(prompt),/markScheme|solutionSvg|worked recommendation|Markband|sourceAnchor|figureKey/);
 assert.equal(p.minutes,p.paper==='1'?75:105);
 assert.equal(p.calculator,p.paper!=='1');
 assert.equal(m.economicsPdfUrl(meta),meta.pdfUrl);
 assert(existsSync('public'+meta.pdfUrl)&&existsSync('public'+meta.questionBooklets[0].url));
 const cases=p.paper==='3'?[null]:p.questions.map(q=>q.id);
 for(const choice of cases){
   const all=Object.fromEntries(p.questions.flatMap(q=>q.parts.map(a=>[m.answerKey(q.id,a.label),'Retained answer'])));
   const answers=m.cleanAnswers(p.questions,choice?{...all,__choice:choice}:all);
   const qs=m.selectedQuestions(p.questions,answers.__choice);
   assert.equal(qs.length,p.paper==='3'?2:1);
   for(const q of p.questions.filter(q=>!qs.includes(q)))assert(!Object.keys(answers).some(k=>k.startsWith(q.id)));
   const marks=m.validateSelfMarks(qs,full(qs));assert.equal(m.scoreMock(qs,answers,marks).total,meta.marks);
   assert.equal(m.scoreMock(qs,answers,null).total,null);
   const first=Object.keys(marks)[0];
   for(const v of [-1,'2',2.5,99,null])assert.throws(()=>m.validateSelfMarks(qs,{...marks,[first]:v}));
   assert.throws(()=>m.cleanAnswers(p.questions,{...answers,[first]:'x'.repeat(12001)}));
   assert.throws(()=>m.cleanAnswers(p.questions,{...answers,__choice:'unlisted'}));
   const id='cccccccc-cccc-4ccc-8ccc-cccccccccccc',draft={version:2,attemptId:id,name:'Practice',startedAt:10000,deadline:10000+meta.minutes*60000,index:0,elapsed:0,stage:'running',flags:{},answers,marks:{}};
   assert.equal(m.restoreEconomicsDraft(JSON.stringify(draft),prompt).deadline,draft.deadline);
   assert.equal(m.restoreEconomicsDraft(JSON.stringify({...draft,deadline:0}),prompt),null);
   const review={id,name:'Practice',submittedAt:'2026-11-07T00:00:00Z',elapsed:35,answers,selfMarks:marks,score:m.scoreMock(qs,answers,marks),solutions:server.economicsMockSolutions({...p,questions:qs})};
   const report=m.reportPayload(meta,review,'student@example.invalid','https://example.invalid');
   assert.equal(report.solution_link,'https://example.invalid'+meta.pdfUrl);assert.match(report.score,new RegExp(meta.marks+' / '+meta.marks));assert((report.paper1+report.paper2).includes(id));
 }
 const bad=structuredClone(p);bad.questions[0].parts[0].marks++;assert.throws(()=>server.validateEconomicsMockPaper(bad,meta));
 const attack=structuredClone(p);attack.questions[0].solutionSvg='<svg viewBox="0 0 9 9"><script>evil()</script></svg>';assert.throws(()=>server.validateEconomicsMockPaper(attack,meta));
}
for(const set of ['a','b']){
 const short=fixtures.get('economics-sl-set-'+set+'-paper-2'),higher=fixtures.get('economics-hl-set-'+set+'-paper-2');
 for(let i=0;i<2;i++){assert.equal(short.questions[i].stem,higher.questions[i].stem);assert.deepEqual(short.questions[i].parts,higher.questions[i].parts);}
}
const catalog=h.load('lib/ib/catalog.ts');const index=h.load('lib/ib/build-content-index.ts').buildIbContentIndex([]);
assert.equal(index.summaries.hl.economics.mocks,6);assert.equal(index.summaries.sl.economics.mocks,4);
const owner={id:'11111111-1111-4111-8111-111111111111',email:'student@example.invalid'};let user=owner,access='active',outage=false,loads=0,queries=0,writes=0;const rows=new Map();
const db={auth:{getUser:async()=>({data:{user},error:null})},from(table){queries++;assert(['ib_economics_challenge_attempts','ib_economics_mock_attempts'].includes(table));let action='select',patch,filters=[];const matching=()=>[...rows.values()].filter(r=>r.table===table&&filters.every(([k,v])=>(v&&typeof v==='object'&&Array.isArray(v.includes)?v.includes.includes(r[k]):r[k]===v)));const q={select(){return q;},eq(k,v){filters.push([k,v]);return q;},is(k,v){filters.push([k,v]);return q;},in(k,values){filters.push([k,{includes:values}]);return q;},order(){return q;},limit(){return q;},insert:async r=>{writes++;if(outage)return {error:{code:'503'}};if(rows.has(r.id))return {error:{code:'23505'}};rows.set(r.id,{...r,table,submitted_at:'2026-11-04T00:00:00Z',self_marks:null,marked_at:null});return {error:null};},update(p){writes++;patch=p;action='update';return q;},async maybeSingle(){return outage?{data:null,error:{code:'503'}}:{data:matching()[0]??null,error:null};},then(resolve){if(outage)return resolve({error:{code:'503'}});const found=matching();if(action==='update')for(const r of found)Object.assign(r,patch);resolve({data:found,error:null});}};return q;}};

const modules={'@/lib/supabase/server':{createSupabaseServerClient:async()=>db},'@/lib/ib/access':{getIbAccessState:async()=>access},'@/lib/ib/economics-mocks':{...server,getEconomicsMockPaper:async(id,paper)=>fixtures.get(m.getEconomicsPaperMeta(id,paper)?.id)}};
const api=ibHarness({moduleMocks:modules}).load('app/api/ib/economics-mocks/[id]/route.ts');
const set=m.ECONOMICS_MOCKS.find(s=>s.id==='economics-hl-challenge-b'),id='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';
const ctx={params:Promise.resolve({id:set.id})},url='https://example.invalid/api/ib/economics-mocks/'+set.id;
const post=(body,origin='https://example.invalid')=>api.POST(new Request(url,{method:'POST',headers:{origin},body:JSON.stringify(body)}),ctx);
const get=suffix=>api.GET(new Request(url+suffix),ctx);
for(const paper of ['1','2','3']){
 const p=fixtures.get(m.getEconomicsPaperMeta(set.id,paper).id),qs=paper==='3'?p.questions:[p.questions.at(-1)],attempt=id.slice(0,-1)+paper;
 const answers=paper==='3'?{}:{__choice:qs[0].id};for(const q of p.questions)answers[q.id+':'+q.parts[0].label]='My reasoning';
 const body={action:'submit',paper,attemptId:attempt,name:'Test',elapsed:75,answers};
 assert.equal((await post(body,'https://foreign.invalid')).status,403);
 user=null;assert.equal((await post(body)).status,401);user=owner;access='trial_expired';assert.equal((await post(body)).status,403);access='active';
 assert.equal((await post({...body,elapsed:p.minutes*60+1})).status,400);outage=true;assert.equal((await post(body)).status,503);outage=false;
 let res=await post(body);assert.equal(res.status,200);let review=(await res.json()).review;
 assert.equal(review.score.maximum,p.marks);assert.equal(review.solutions.length,qs.length);assert.equal(review.score.total,null);
 assert.equal((await post({...body,name:'Overwrite'})).status,200);assert.equal(rows.get(attempt).student_name,'Test');
 assert.equal((await post({action:'mark',paper,attemptId:attempt,selfMarks:{}})).status,400);
 res=await post({action:'mark',paper,attemptId:attempt,selfMarks:full(qs)});assert.equal(res.status,200);assert.equal((await res.json()).review.score.total,p.marks);
 res=await post({action:'mark',paper,attemptId:attempt,selfMarks:Object.fromEntries(Object.keys(full(qs)).map(k=>[k,0]))});assert.equal((await res.json()).review.score.total,p.marks);
 user={id:'44444444-4444-4444-8444-444444444444',email:'other@example.invalid'};assert.equal((await get('?attempt='+attempt)).status,404);user=owner;
 assert.equal((await get('?paper='+paper+'&attempt='+attempt)).status,200);
}
console.log('Passed 10 Economics sittings, all choices, 380 marks, 20 PDF links, report payloads, authenticated submit/review, draft recovery, retry and one-time marking.');
