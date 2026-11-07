import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {ibHarness} from './ib-component-harness.mjs';
const biologyFixture=meta=>JSON.parse(readFileSync('content/ib/biology-mocks-2025/papers/'+meta.id+'.json','utf8'));
const infra=process.argv.includes('--infrastructure-only'),root=ibHarness(),m=root.load('lib/ib/biology-mock-model.ts'),server=root.load('lib/ib/biology-mocks.ts');
const {BIOLOGY_MOCKS,answerKey,cleanAnswers,validateSelfMarks,scoreMock,biologyPdfUrl,reportPayload,restoreBiologyDraft,secondsRemaining}=m;
const metas=BIOLOGY_MOCKS.flatMap(s=>s.papers),fixtures=new Map(),copy=v=>JSON.parse(JSON.stringify(v));
assert.equal(BIOLOGY_MOCKS.length,4);assert.equal(metas.length,8);assert.equal(metas.reduce((s,p)=>s+p.questionCount,0),182);assert.equal(metas.reduce((s,p)=>s+p.marks,0),520);
for(const course of ['sl','hl'])assert.equal(metas.filter(p=>p.course===course).length,4);
let actualQuestions=0,actualDiagrams=0;const unique=new Set();
for(const meta of metas){
 assert.equal(meta.status,'published');assert.equal(meta.calculator,true);assert.equal(meta.minutes,m.paperSpec(meta.course,meta.paper).minutes);assert.equal(meta.marks,m.paperSpec(meta.course,meta.paper).marks);assert.equal(biologyPdfUrl(meta),`/ib-biology-mocks/${meta.id}-solutions.pdf`);assert.throws(()=>biologyPdfUrl({...meta,pdfUrl:'https://evil.invalid'}));
 const p=server.validateBiologyMockPaper(biologyFixture(meta),meta);fixtures.set(meta.id,p);
 const marks=Object.fromEntries(p.questions.flatMap(q=>q.parts.map(part=>[answerKey(q.id,part.label),part.marks]))),answers=Object.fromEntries(p.questions.flatMap(q=>q.questionType==='multiple-choice'?[[q.id,q.correctOption]]:q.parts.map(part=>[answerKey(q.id,part.label),'Written working'])));
 const cleaned=cleanAnswers(p.questions,{...answers,unknown:'discard'});const eligible=m.selectedQuestions(p.questions,cleaned.__sectionB);assert(!('unknown'in cleaned));assert.equal(scoreMock(eligible,cleaned,validateSelfMarks(eligible,marks)).total,meta.marks);assert.equal(scoreMock(eligible,cleaned,null).total,null);assert.equal(scoreMock(eligible,cleaned,null).mcqMaximum,meta.paper==='1'?(meta.course==='sl'?30:40):0);
 for(const value of [-1,999,.5,'1',null])assert.throws(()=>validateSelfMarks(p.questions,{...marks,[Object.keys(marks)[0]]:value}));assert.throws(()=>validateSelfMarks(p.questions,{}));assert.throws(()=>cleanAnswers(p.questions,null));assert.throws(()=>cleanAnswers(p.questions,{[Object.keys(answers)[0]]:'x'.repeat(12001)}));if(meta.paper==='1')assert.throws(()=>cleanAnswers(p.questions,{[p.questions[0].id]:'Z'}));
 if(meta.paper==="2"){
    const extended=p.questions.filter(q=>q.sectionB);
    for(const omitted of extended){
      const chosen=extended.filter(q=>q.id!==omitted.id);
      const candidate=cleanAnswers(p.questions,{...answers,__sectionB:chosen.map(q=>q.id).join(",")});
      const subset=m.selectedQuestions(p.questions,candidate.__sectionB);
      assert.equal(subset.length,p.questions.length-1);
      assert(!Object.keys(candidate).some(k=>k.startsWith(omitted.id)));
      const mark=validateSelfMarks(subset,marks);
      assert(!Object.keys(mark).some(k=>k.startsWith(omitted.id)));
      assert.equal(scoreMock(subset,candidate,mark).total,meta.marks);
      assert.equal(subset.filter(q=>q.sectionB).length,meta.course==="sl"?1:2);
    }
    for(const invalid of ["", "wrong", extended.map(q=>q.id).join(","), [extended[0].id]])
      assert.throws(()=>cleanAnswers(p.questions,{...answers,__sectionB:invalid}));
 }
 const prompt=server.biologyMockPrompt(p,meta),solutions=server.biologyMockSolutions(p);assert.doesNotMatch(JSON.stringify(prompt),/PRIVATE_|markScheme|answerSummary|correctOption|sourceAnchors|changeNotes|verification|cognitiveDemand|diagramSvg/);assert.doesNotMatch(JSON.stringify(solutions),/PRIVATE_(SOURCE|FOCUS|CHANGE|DEMAND|METHOD|VERIFICATION)|sourceAnchors|changeNotes|verification|cognitiveDemand|diagramSvg/);
 const review={id:'22222222-2222-4222-8222-222222222222',name:'Student',elapsed:25,submittedAt:'2026-11-04T00:00:00Z',answers:cleaned,selfMarks:null,score:scoreMock(eligible,cleaned,null),solutions},pending=reportPayload(meta,review,'student@example.invalid','https://example.invalid'),scored=reportPayload(meta,{...review,selfMarks:marks,score:scoreMock(eligible,cleaned,marks)},'student@example.invalid','https://example.invalid');assert.match(pending.score,/pending/);assert.doesNotMatch(pending.score,/null|NaN/);assert.match(scored.score,/self-assessed/);assert.equal(pending.solution_link,biologyPdfUrl(meta,'https://example.invalid'));assert.equal(scored.solution_link,pending.solution_link);assert.match(pending.paper1+pending.paper2,/Written marking is pending/);
 const d={version:2,attemptId:review.id,name:'Student',startedAt:100000,deadline:100000+meta.minutes*60000,elapsed:0,stage:'running',index:0,answers:cleaned,flags:{[p.questions[0].id]:true},marks:{}};assert.equal(restoreBiologyDraft(JSON.stringify(d),prompt).deadline,d.deadline);assert.equal(secondsRemaining(d.deadline,d.startedAt+25000,meta.minutes*60),meta.minutes*60-25);assert.equal(secondsRemaining(0,1,10),0);for(const patch of [{index:-1},{deadline:d.deadline+1},{attemptId:'bad'},{answers:[]},{marks:{unknown:1}},{flags:{unknown:true}},{answers:{unknown:'x'}}])assert.equal(restoreBiologyDraft(JSON.stringify({...d,...patch}),prompt),null);
 for(const change of [p=>p.questions[0].marks++,p=>p.questions[0].markScheme[0].steps[0].code='N1',p=>p.questions[0].diagramSvg='<svg viewBox="0 0 10 10"><script>alert(1)</script></svg>',p=>p.questions[1].id=p.questions[0].id,p=>p.questions[0].number=99]){const bad=copy(p);change(bad);assert.throws(()=>server.validateBiologyMockPaper(bad,meta));}
 if(!infra){const path=`content/ib/biology-mocks-2025/papers/${meta.id}.json`;assert(existsSync(path),`Missing ${path}`);const actual=server.validateBiologyMockPaper(JSON.parse(readFileSync(path,'utf8')),meta);for(const q of actual.questions){assert(!unique.has(q.id));unique.add(q.id);actualQuestions++;actualDiagrams+=Number(!!q.diagramSvg||!!q.diagramJpeg);}assert(existsSync(`public${meta.pdfUrl}`),`Missing PDF ${meta.id}`);}
}
const owner={id:'11111111-1111-4111-8111-111111111111',email:'student@example.invalid'};let user=owner,access='active',outage=false,loads=0,queries=0,writes=0;const rows=new Map();
const db={auth:{getUser:async()=>({data:{user},error:null})},from(table){queries++;assert(['ib_biology_challenge_attempts','ib_biology_mock_attempts'].includes(table));let action='select',patch,filters=[];const matching=()=>[...rows.values()].filter(r=>r.table===table&&filters.every(([k,v])=>(v&&typeof v==='object'&&Array.isArray(v.includes)?v.includes.includes(r[k]):r[k]===v)));const q={select(){return q;},eq(k,v){filters.push([k,v]);return q;},is(k,v){filters.push([k,v]);return q;},in(k,values){filters.push([k,{includes:values}]);return q;},order(){return q;},limit(){return q;},insert:async r=>{writes++;if(outage)return {error:{code:'503'}};if(rows.has(r.id))return {error:{code:'23505'}};rows.set(r.id,{...r,table,submitted_at:'2026-11-04T00:00:00Z',self_marks:null,marked_at:null});return {error:null};},update(p){writes++;patch=p;action='update';return q;},async maybeSingle(){return outage?{data:null,error:{code:'503'}}:{data:matching()[0]??null,error:null};},then(resolve){if(outage)return resolve({error:{code:'503'}});const found=matching();if(action==='update')for(const r of found)Object.assign(r,patch);resolve({data:found,error:null});}};return q;}};
let archiveLoads=0;
const modules={'@/lib/supabase/server':{createSupabaseServerClient:async()=>db},'@/lib/ib/access':{getIbAccessState:async()=>access},'@/lib/ib/biology-mocks':{...server,getBiologyMockPaper:async(id,p)=>{loads++;return fixtures.get(m.getBiologyPaperMeta(id,p)?.id);}},'@/lib/ib/biology-mock-archive':{legacyReview:row=>{archiveLoads++;return {id:row.id,spec:{minutes:90,marks:55}};}}};
const api=ibHarness({moduleMocks:modules}).load('app/api/ib/biology-mocks/[id]/route.ts'),meta=metas[0],attempt='33333333-3333-4333-8333-333333333333';
const ctx=id=>({params:Promise.resolve({id})}),url=id=>`https://example.invalid/api/ib/biology-mocks/${id}`,body={action:'submit',paper:'1',attemptId:attempt,name:'Student',elapsed:30,answers:{[fixtures.get(meta.id).questions[0].id]:fixtures.get(meta.id).questions[0].correctOption}};
const post=(b=body,id=meta.mockId,origin='https://example.invalid')=>api.POST(new Request(url(id),{method:'POST',headers:{origin},body:JSON.stringify(b)}),ctx(id));const get=(suffix='',id=meta.mockId)=>api.GET(new Request(url(id)+suffix),ctx(id));
assert.equal((await post(body,meta.mockId,'https://evil.invalid')).status,403);assert.equal(writes,0);user=null;assert.equal((await post()).status,401);assert.equal((await get()).status,401);user=owner;
for(const state of ['trial_required','trial_expired','unavailable','unexpected_state']){access=state;const before={loads,queries,writes};assert.equal((await get('?attempt='+attempt)).status,state==='unavailable'?503:403);assert.equal((await post()).status,state==='unavailable'?503:403);assert.deepEqual({loads,queries,writes},before);}access='active';
outage=true;assert.equal((await post()).status,503);assert.equal(rows.size,0);outage=false;let res=await post();assert.equal(res.status,200);let data=await res.json();assert.equal(data.review.name,'Student');assert.equal(data.review.score.mcq,1);assert.equal(data.review.score.total,null);assert.doesNotMatch(JSON.stringify(data),/PRIVATE_(SOURCE|CHANGE|VERIFICATION|DEMAND|METHOD|FOCUS)/);assert.equal(res.headers.get('cache-control'),'private, no-store');
assert.equal((await post({...body,name:'Changed',answers:{}})).status,200);assert.equal(rows.get(attempt).student_name,'Student');assert.equal((await get('?attempt='+attempt+'&paper=2')).status,404);assert.equal((await post({...body,paper:'2'})).status,404);assert.equal(rows.get(attempt).paper,'1');
const p=fixtures.get(meta.id),marks=Object.fromEntries(p.questions.flatMap(q=>q.parts.map(part=>[answerKey(q.id,part.label),part.marks])));assert.equal((await post({action:'mark',paper:'1',attemptId:attempt,selfMarks:{}})).status,400);assert.equal((await post({action:'mark',paper:'1',attemptId:attempt,selfMarks:marks})).status,200);const firstMarks=copy(rows.get(attempt).self_marks);assert.equal((await post({action:'mark',paper:'1',attemptId:attempt,selfMarks:Object.fromEntries(Object.keys(marks).map(k=>[k,0]))})).status,200);assert.deepEqual(copy(rows.get(attempt).self_marks),firstMarks);
user={id:'44444444-4444-4444-8444-444444444444',email:'other@example.invalid'};assert.equal((await get('?attempt='+attempt)).status,404);assert.equal((await post()).status,404);assert.equal((await post({action:'mark',paper:'1',attemptId:attempt,selfMarks:marks})).status,404);user=owner;
assert.equal((await get()).status,200);assert.equal((await post({...body,elapsed:7201})).status,400);assert.equal((await post({...body,name:'x'.repeat(101)})).status,400);
// Persist a non-default Paper 2 choice, then attempt to substitute marks for an excluded response.
const optionalPaper=fixtures.get(metas[1].id);
const optionalQuestions=optionalPaper.questions.filter(q=>q.sectionB);
const last=optionalQuestions.at(-1), first=optionalQuestions[0];
const secondAttempt="77777777-7777-4777-8777-777777777777";
const submission={...body,attemptId:secondAttempt,paper:"2",answers:{__sectionB:last.id,[first.id+":a"]:"excluded",[last.id+":a"]:"saved answer"}};
let optionalResult=await (await post(submission)).json();
assert.equal(optionalResult.review.score.maximum,50);
assert.equal(optionalResult.review.answers[last.id+":a"],"saved answer");
assert(!(first.id+":a" in optionalResult.review.answers));
assert(!optionalResult.review.solutions.some(q=>q.id===first.id));
const optionMarks=Object.fromEntries(optionalResult.review.solutions.flatMap(q=>q.parts.map(part=>[answerKey(q.id,part.label),part.marks])));
const wrongMarks={...optionMarks,[first.id+":a"]:3};delete wrongMarks[last.id+":a"];
assert.equal((await post({action:"mark",paper:"2",attemptId:secondAttempt,selfMarks:wrongMarks})).status,400);
optionalResult=await (await post({action:"mark",paper:"2",attemptId:secondAttempt,selfMarks:optionMarks})).json();
assert.equal(optionalResult.review.score.total,50);
let authCalls=0,pageLoads=0;const page=ibHarness({user:owner,onAuth:()=>authCalls++,moduleMocks:{...modules,'@/lib/ib/biology-mocks':{...server,getBiologyMockPaper:async()=>{assert(authCalls>0);pageLoads++;return p;}}}}).load('app/ib/biology-mocks/[id]/[paper]/page.tsx').default;const tree=await page({params:Promise.resolve({id:meta.mockId,paper:'1'}),searchParams:Promise.resolve({})});assert.equal(pageLoads,1);assert.equal(tree.props.paper.id,meta.id);assert.doesNotMatch(JSON.stringify(tree.props.paper),/PRIVATE_|correctOption|markScheme/);
for(const file of ['lib/ib/biology-mock-model.ts','lib/ib/biology-mocks.ts','app/ib/biology-mocks/BiologyMockRunner.tsx'])assert.doesNotMatch(readFileSync(file,'utf8'),/content\/ib\/biology-hl\/|biology-mocks\.json|IbQuestion|ibQuestionSchema/);
const runner=readFileSync('app/ib/biology-mocks/BiologyMockRunner.tsx','utf8');assert.match(runner,/deliverEmail\(result, "completion"\)/);assert.match(runner,/deliverEmail\(data.review, "scored"\)/);assert.match(runner,/biologyPdfUrl\(paper\)/);assert.match(runner,/if \(pdfOpen|pdfOpen \?/);assert.match(runner,/ts:ib-biology:v2:\$\{accountId\}:\$\{paper.id\}/);
const index=ibHarness().load('lib/ib/build-content-index.ts').buildIbContentIndex([]);assert.equal(index.summaries.hl['biology'].mocks,4);assert.equal(index.summaries.sl['biology'].mocks,4);
const sql=readFileSync('supabase/migrations/20261107171308_ib_biology_challenge_attempts.sql','utf8');assert.match(sql,/enable row level security/i);assert.match(sql,/grant insert \(id, user_id, mock_id, paper, student_name, answers, elapsed_seconds\)/i);assert.match(sql,/Saved self-assessment is immutable/);assert.doesNotMatch(sql,/alter table public\.ib_biology_mock_attempts/i);

assert.equal(actualQuestions,182);assert.equal(actualDiagrams,9);for(const meta of metas)for(const b of meta.questionBooklets)assert(existsSync('public'+b.url));console.log('Verified all 182 question appearances, 520 marks, nine figures, 20 PDFs, scoring, auth, ownership, idempotency, saved reports and SQL guards.');
