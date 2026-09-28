import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';

// Execute the shipped scripts with deterministic DOM, clock and network boundaries.
// The test-only facades expose closure state; no production functions are replaced.
const html = readFileSync('public/tmua-question-bank/index.html', 'utf8');
const scripts = [...html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)];
for (const [, attrs, source] of scripts) {
  if (!/type=["']application\//.test(attrs)) new vm.Script(source);
}
const block = id => scripts.find(([ , attrs]) => attrs.includes(`id="${id}"`))[2];
const expose = (source, code) => source.replace(/\}\)\(\);\s*$/, `${code}\n})();`);
const plain = value => JSON.parse(JSON.stringify(value));
const flush = async () => { for (let i = 0; i < 35; i++) await Promise.resolve(); };
const deferred = () => { let resolve, reject; const promise = new Promise((a,b) => { resolve=a; reject=b; }); return {promise,resolve,reject}; };
const response = value => ({ok:true, status:200, json:async()=>plain(value), text:async()=>JSON.stringify(value)});

function harness(saved = {}) {
  let clock = 100_000;
  const listeners = new Map();
  const saves = [], checks = [], questions = new Map(), pendingChecks = new Map(), blockedSaves = new Map();
  const storage = new Map(Object.entries(saved));
  const nodes = new Map();
  for (const id of ['qTitle','posCounter','qOptions','metaStatus','qFeedback','qPrompt','emptyState','qCard']) {
    nodes.set(id, {style:{},textContent:'',innerHTML:'',classList:{add(){},remove(){}},querySelector(selector) {
      if (!selector.includes(':checked')) return null;
      const tag = this.innerHTML.match(/<input\b[^>]*\bchecked\b[^>]*>/)?.[0];
      return tag ? {value:tag.match(/\bvalue="([^"]+)"/)[1]} : null;
    },querySelectorAll(){return [];}});
  }
  const addEventListener = (name, fn) => { const list=listeners.get(name)||[]; list.push(fn); listeners.set(name,list); };
  const ctx = vm.createContext({console,Promise,URL,Map,Set,Number,JSON,Math,
    Date:class extends Date {constructor(...a){super(...(a.length?a:[clock]));}static now(){return clock;}},
    Event:class {constructor(type){this.type=type;}},
    CustomEvent:class {constructor(type,opts){this.type=type;this.detail=opts.detail;}},
    localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,String(v))},
    location:{pathname:'/tmua-question-bank/index.html'},
    crypto:{randomUUID:()=>`test-${checks.length}-${saves.length}`},
    addEventListener,dispatchEvent:event=>{for(const fn of listeners.get(event.type)||[])fn(event);},
    setTimeout:()=>1,clearTimeout(){},setInterval:()=>1,clearInterval(){},alert(){},
    document:{visibilityState:'visible',addEventListener,getElementById:id=>nodes.get(id)||null,
      querySelector:selector=>selector.startsWith('#')?nodes.get(selector.slice(1))||null:null,
      querySelectorAll:()=>[]},
    fetch:async (url,init) => {
      const body=init?.body ? JSON.parse(init.body) : {};
      if (url.includes('tmua_qb_public_question')) {
        const pending=questions.get(body.p_display_order);
        if (pending) return response(await pending.promise);
        return response({display_order:body.p_display_order,options:'ABCDEFGH'.split('').map(label=>({label,html:label}))});
      }
      if (url.includes('tmua_qb_public_check')) {
        checks.push(body);
        const pending=pendingChecks.get(body.p_display_order);
        return response(pending ? await pending.promise : {display_order:body.p_display_order,is_correct:true,answer:body.p_selected});
      }
      if (url.includes('/progress/save')) {
        const pending = blockedSaves.get(saves.length);
        saves.push(body);
        if (pending) await pending.promise;
        return response({ok:true});
      }
      return response({ok:true,progress:{}});
    }
  });
  ctx.window=ctx;
  vm.runInContext(expose(block('ts-per-question-progress-sync-v1'), `window.progressTest={
    primaryQuestionId,saveProgress,findProgressForCurrent,buildMergedUpdate,
    setRows: rows=>{progressMap=rows;}, getRows:()=>progressMap};`),ctx);
  const main=scripts.find(([, ,s])=>s.includes('let allMeta = []'))[2];
  vm.runInContext(expose(main,`window.mainTest={render,loadState,answerFor,
    configure:(rows,answers={})=>{allMeta=rows;visibleList=rows;currentIndex=0;state.answers=answers;},
    navigate:i=>{currentIndex=i;return render();},
    filter:rows=>{visibleList=rows;currentIndex=0;return render();},
    state:()=>state};`),ctx);
  vm.runInContext(expose(block('ts-qb-question-timer-v1'),`window.timerTest={
    currentQuestionId,serverRow,effectiveStatus,newEntryForQuestion,currentElapsedMs,
    syncCurrentQuestion,resetWrongForImmediateRetry,checkpointUnattemptedToServer,
    pauseQuestion,resumeQuestion,loadLocalState,
    setRows:rows=>{serverProgress=rows;serverProgressLoaded=true;},
    entries:()=>entries,active:()=>activeQid,local:()=>localState};`),ctx);
  vm.runInContext(expose(block('ts-localstorage-to-qb-progress-migration-v1'),
    'window.migrationTest={collectLocalProgress,mergeWithServer};'),ctx);
  return {ctx,nodes,saves,checks,questions,pendingChecks,blockedSaves,storage,advance:ms=>{clock+=ms;}};
}

const meta = (id, number, topic='1_Algebra & Functions') => ({display_order:id,global_number:number,qid:`SB-${id}`,topic});
const olderAnswer={selected:'A',checked:true,isCorrect:true,flagged:true};
const h=harness({
  'ts_tmua_supabase_exact_ui_v4':JSON.stringify({answers:{397:olderAnswer}}),
  'ts_qb_question_timer_state_v1:tmua-question-bank':JSON.stringify({pendingMs:{1824:90000},finalSeconds:{397:50}})
});
await flush();
const {ctx:c}=h;
const rows=[meta(1824,397),meta(2074,398),meta(397,1)];
c.mainTest.configure(rows,{397:olderAnswer});
await c.mainTest.render(); await flush();
assert.equal(h.nodes.get('qTitle').textContent,'Question 397');
assert.equal(h.nodes.get('posCounter').textContent,'1');
assert.equal(c.TS_TMUA_QB.currentQuestionId(),'1824');
assert.equal(c.progressTest.primaryQuestionId(),'1824');
assert.equal(c.timerTest.currentQuestionId(),'1824');
assert.deepEqual(plain(c.TS_TMUA_QB.getAnswer('1824')),{});
assert.equal(h.nodes.get('metaStatus').textContent,'Unattempted');
assert.deepEqual(plain(c.TS_TMUA_QB.getAnswer('397')),olderAnswer);
assert.deepEqual(plain(c.timerTest.local()),{pendingMs:{},finalSeconds:{}});
assert.equal(h.saves[0].updates[0].question_id,'1824');
assert.equal(h.saves[0].updates[0].flagged,false);

// DOM positions and ambiguous legacy timer rows never override the stable answer state.
c.timerTest.setRows({'1824':{status:'correct',time_spent:88},'397':{status:'correct',time_spent:55}});
c.progressTest.setRows({'1824':{status:'correct',selected_answer:'B',flagged:true}});
assert.equal(c.timerTest.serverRow('1824'),null);
assert.equal(c.timerTest.effectiveStatus('1824'),'');
assert.equal(c.progressTest.findProgressForCurrent(),null);
assert.equal(c.timerTest.newEntryForQuestion('397').missingHistoricalTime,true);
assert.equal(c.timerTest.newEntryForQuestion('397').frozen,true);
assert.equal(c.TS_TMUA_TIMER.submissionSeconds('1824'),null);
assert.equal(c.progressTest.buildMergedUpdate('1824','correct','H',false,'check').answer_elapsed_seconds,null);
const beforeLegacy=plain(c.progressTest.getRows());
c.progressTest.saveProgress('seen'); await flush();
assert.deepEqual(plain(c.progressTest.getRows()),beforeLegacy);

// Navigation and an empty filter pause the actual question, and returning resumes its elapsed time.
h.advance(7000);
await c.mainTest.navigate(1); await flush();
assert.equal(c.timerTest.entries()['1824'].running,false);
assert.equal(c.timerTest.entries()['1824'].accumulatedMs,7000);
h.advance(3000);
await c.mainTest.filter([]); await flush();
assert.equal(c.timerTest.active(),'');
assert.equal(c.timerTest.entries()['2074'].running,false);
h.advance(9000);
await c.mainTest.filter(rows); await flush();
assert.equal(c.timerTest.currentElapsedMs(c.timerTest.entries()['1824']),7000);

// Slow question fetches cannot paint an earlier navigation over the current record.
const slow=deferred(); h.questions.set(2075,slow);
const pendingRender=c.mainTest.filter([meta(2075,999)]);
assert.equal(c.TS_TMUA_QB.currentQuestionId(),'');
await c.mainTest.filter(rows);
slow.resolve({display_order:2075,options:[]}); await pendingRender;
assert.equal(c.TS_TMUA_QB.currentQuestionId(),'1824');

// A successful H answer stays attached to 1824 even while 2074 is on screen.
c.ACTIONS.setSelected('H'); await flush();
const slowCheck=deferred(); h.pendingChecks.set(1824,slowCheck);
h.advance(4000);
const pending=c.ACTIONS.checkAnswer();
assert.equal(c.timerTest.entries()['1824'].running,false);
assert.equal(c.timerTest.entries()['1824'].frozen,true);
await c.ACTIONS.checkAnswer(); // duplicate click while the first request is in flight
assert.equal(h.checks.length,1);
await c.mainTest.navigate(1); await flush();
h.advance(12000);
slowCheck.resolve({display_order:1824,is_correct:true,answer:'H',solution_html:'Worked answer'});
await pending; await flush();
const checkSave=h.saves.find(s=>s.event_name==='check');
assert.equal(checkSave.updates[0].question_id,'1824');
assert.equal(checkSave.updates[0].selected_answer,'H');
assert.equal(checkSave.updates[0].status,'correct');
assert.equal(checkSave.updates[0].time_spent,11);
assert.equal(checkSave.updates[0].answer_elapsed_seconds,11);
assert.match(checkSave.updates[0].submission_id,/^tmua-stable-v1\|1824\|/);
assert.equal(c.TS_TMUA_QB.getAnswer('1824').isCorrect,true);
assert.deepEqual(plain(c.TS_TMUA_QB.getAnswer('2074')),{});
assert.equal(c.timerTest.active(),'2074');
assert.equal(c.timerTest.entries()['2074'].running,true);
assert.equal(c.timerTest.local().finalSeconds['1824'],11);

// Incorrect attempts freeze, keep duration for analytics, and restart at zero on a real retry.
c.ACTIONS.setSelected('F'); await flush();
const wrong=deferred();h.pendingChecks.set(2074,wrong);
const wrongPromise=c.ACTIONS.checkAnswer();
wrong.resolve({display_order:2074,is_correct:false,answer:'G'});
await wrongPromise;await flush();
const wrongSave=h.saves.filter(s=>s.event_name==='check').at(-1).updates[0];
assert.equal(wrongSave.question_id,'2074');assert.equal(wrongSave.time_spent,null);
assert.equal(typeof wrongSave.answer_elapsed_seconds,'number');
assert.equal(c.timerTest.entries()['2074'].submittedWrong,true);
c.ACTIONS.setSelected('G');await flush();
assert.equal(c.timerTest.entries()['2074'].frozen,false);
assert.equal(c.timerTest.currentElapsedMs(c.timerTest.entries()['2074']),0);

// A failed Check after navigation must not restart a background question timer.
const failure=deferred();h.pendingChecks.set(2074,failure);
const failedPromise=c.ACTIONS.checkAnswer();
const failedAssertion=assert.rejects(failedPromise,/network failure/);
await c.mainTest.navigate(0);await flush();
failure.reject(new Error('network failure'));await failedAssertion;
assert.notEqual(c.timerTest.entries()['2074']?.running,true);
assert.deepEqual(JSON.parse(h.storage.get('ts_tmua_supabase_exact_ui_v4')).answers['397'],olderAnswer);
assert.ok(h.storage.has('ts_qb_question_timer_state_v1:tmua-question-bank'));

// Local migration accepts only known keys inside the existing answers dictionary.
const migrated=c.migrationTest.collectLocalProgress({answers:{'2074':{selected:'H',checked:true,isCorrect:true},'SB-2074':olderAnswer},random:{'1':olderAnswer}});
assert.equal(migrated.length,1);assert.equal(migrated[0].question_id,'2074');
assert.equal(migrated[0].selected_answer,'H');
assert.equal(c.migrationTest.mergeWithServer(migrated,{'2074':{status:'wrong'}}).length,0);

// Timer hooks hand every save immediately to the shared durable transport.
// Shared transport ordering/reload behavior is exercised by verify-qb-durable-sync.
const queued=harness();await flush();
queued.ctx.mainTest.configure([meta(2074,1)]);await queued.ctx.mainTest.render();await flush();
queued.advance(13000);queued.ctx.ACTIONS.setSelected('G');await flush();
const hold=deferred();queued.blockedSaves.set(queued.saves.length,hold);
await queued.ctx.ACTIONS.checkAnswer();await flush();
const countBeforeFlags=queued.saves.length;
queued.ctx.ACTIONS.toggleFlag();await flush();
queued.ctx.ACTIONS.toggleFlag();await flush();
assert.equal(queued.saves.length,countBeforeFlags+2);
hold.resolve();await flush();
const savedCheck=queued.saves.find(s=>s.event_name==='check').updates[0];
const savedFlags=queued.saves.filter(s=>s.event_name==='flag');
assert.equal(savedFlags.length,2);
for (const flag of savedFlags) {
  assert.equal(flag.updates[0].submission_id,savedCheck.submission_id);
  assert.equal(flag.updates[0].answer_elapsed_seconds,13);
  assert.equal(flag.updates[0].time_spent,13);
}
assert.equal(savedFlags.at(-1).updates[0].flagged,false);

const unfinished=harness();await flush();
unfinished.ctx.mainTest.configure([meta(2074,1),meta(2075,2)]);
await unfinished.ctx.mainTest.render();await flush();unfinished.advance(17000);
await unfinished.ctx.mainTest.navigate(1);await flush();
await unfinished.ctx.mainTest.navigate(0);await flush();
assert.equal(unfinished.saves.filter(s=>s.event_name==='seen'&&s.updates[0].question_id==='2074').at(-1).updates[0].time_spent,17);

// Execute the actual API handler with an authenticated, isolated Supabase stub.
const route=readFileSync('app/api/qb/progress/save/route.ts','utf8');
const js=ts.transpileModule(route,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
const written=[];
const db={auth:{getUser:async()=>({data:{user:{id:'student-test',email:'student@example.test'}},error:null})},
  from:table=>({upsert:async rows=>{written.push({table,rows});return {error:null};}})};
const adminDb={from:()=>({select:()=>({in:(_column,values)=>({retry:async enabled=>{assert.equal(enabled,false);return {data:values.filter(qid=>String(qid).startsWith('ESAT-')).map(qid=>({qid})),error:null};}})})})};
const api=vm.createContext({exports:{},process:{env:{}},console,Date,
  require:name=>name==='next/server'?{NextResponse:{json:(body,options)=>({body,status:options?.status||200})}}:
    name==='@supabase/ssr'?{createServerClient:()=>db}:
    name==='next/headers'?{cookies:async()=>({get(){},set(){}})}:
    name==='@/lib/auth/service-recovery'?{withServiceTimeout:p=>p,isMissingSession:e=>e?.name==='AuthSessionMissingError',serviceFetch:()=>{throw new Error('Unexpected network')}}:
    {ESAT_TABLE_CANDIDATES:['esat_qb_questions'],adminClient:()=>adminDb}});
vm.runInContext(js,api);
const post=body=>api.exports.POST({json:async()=>body});
assert.equal((await post({product:'tmua-question-bank',updates:[{question_id:'1'}]})).status,409);
assert.equal(written.length,0);
assert.equal((await post({product:'tmua-question-bank',identity_version:'tmua-display-order-v1',updates:[{question_id:'SB-1824'}]})).status,400);
assert.equal((await post({product:'tmua-question-bank',identity_version:'tmua-display-order-v1',updates:[{question_id:'1824',selected_answer:'H',status:'correct'}]})).status,200);
assert.equal(written[0].rows[0].user_id,'student-test');
assert.equal(written[0].rows[0].question_id,'1824');
assert.equal(written[0].rows[0].selected_answer,'H');
assert.equal((await post({product:'esat-question-bank',updates:[{question_id:'ESAT-001',status:'seen'}]})).status,409);
assert.equal((await post({product:'esat-question-bank',identity_version:'esat-qid-v1',updates:[{question_id:'1530',status:'seen'}]})).status,400);
assert.equal((await post({product:'esat-question-bank',identity_version:'esat-qid-v1',updates:[{question_id:'ESAT-001',status:'seen'}]})).status,200);
console.log('PASS: Actual TMUA scripts preserve stable IDs across renumbering, filters, delayed fetch/check, duplicate clicks, F–H answers, wrong retry, failed submission, legacy storage and API version guards.');
