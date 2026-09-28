import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
const sources = Object.fromEntries(['qb-compact-sync','qb-progress-transport'].map(name=>[name,readFileSync(`public/${name}.js`,'utf8')]));
const flush = async()=>{for(let n=0;n<8;n++)await new Promise(resolve=>setImmediate(resolve));};
const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};};
const ok=data=>Response.json({ok:true,...data});
const plain=value=>JSON.parse(JSON.stringify(value));
const key='ts_tmua_supabase_exact_ui_v4';
const scope=user=>`${key}__account_v3:${user}:`;
function harness(fetcher,shared=new Map(),locks=new Map()) {
  let clock=Date.parse("2026-09-20T18:00:00Z"),id=0;const timers=new Map(),listeners=new Map();
  class Storage {
    get length(){return shared.size;} key(index){return [...shared.keys()][index]??null;}
    getItem(k){return shared.get(String(k))??null;}
    setItem(k,v){const oldValue=shared.get(String(k));shared.set(String(k),String(v));if(oldValue!==String(v)&&shared.notify)shared.notify({source:context,key:String(k),oldValue,newValue:String(v)});}
    removeItem(k){const oldValue=shared.get(String(k));shared.delete(String(k));if(oldValue!==undefined&&shared.notify)shared.notify({source:context,key:String(k),oldValue,newValue:null});}
  }
  const add=(type,fn)=>{if(!listeners.has(type))listeners.set(type,new Set());listeners.get(type).add(fn);};
  const dispatch=event=>{for(const fn of listeners.get(event.type)||[])fn(event);};
  const context=vm.createContext({console:{warn(){},error(){}},JSON,Map,Set,Promise,URL,Response,Request,AbortController,DOMException,
    Math:Object.assign(Object.create(Math),{random:()=>0.15}),
    Date:class extends Date {static now(){return clock;}},Storage,localStorage:new Storage(),
    setTimeout:(fn,ms=0)=>{timers.set(++id,{fn,at:clock+ms});return id;},clearTimeout:n=>timers.delete(n),setInterval:()=>++id,clearInterval(){},
    addEventListener:add,removeEventListener:(type,fn)=>listeners.get(type)?.delete(fn),dispatchEvent:dispatch,
    CustomEvent:class {constructor(type,options){this.type=type;this.detail=options.detail;}},
    crypto:{randomUUID:()=>`id-${++id}-${Math.random()}`},
    navigator:{locks:{request:(name,fn)=>{const job=(locks.get(name)||Promise.resolve()).then(fn);locks.set(name,job.catch(()=>{}));return job;}}},
    location:{origin:'https://portal.test',href:'https://portal.test/tmua-question-bank'},
    document:{visibilityState:'visible',addEventListener:add,querySelector:()=>null,querySelectorAll:()=>[],getElementById:()=>({style:{},setAttribute(){}})},fetch:fetcher});
  context.window=context;
  return {context,shared,dispatch,run:name=>vm.runInContext(sources[name],context),
    advance:async ms=>{clock+=ms;for(const [n,t] of [...timers])if(t.at<=clock){timers.delete(n);t.fn();}await flush();}};
}
const saveBody={product:'tmua-question-bank',identity_version:'tmua-display-order-v1',event_name:'check',updates:[{
 question_id:'189',status:'correct',selected_answer:'E',submission_id:'tmua-stable-v1|189|immutable',answer_elapsed_seconds:48.2,answer_submitted_at:'2026-09-20T18:00:00Z',flagged:true}]};
const save=client=>client.context.fetch('/api/qb/progress/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(saveBody)});
const load=client=>client.context.fetch('/api/qb/progress/load?product=tmua-question-bank');
const outbox=shared=>[...shared.keys()].filter(k=>k.startsWith('ts_qb_submission_outbox_v3:A:'));

// Authenticated read is shared; writes cannot run until it establishes an owner.
const identity=deferred();let active=0,maxActive=0;const calls=[];
const first=harness(async(url,init)=>{calls.push({url,init});maxActive=Math.max(maxActive,++active);if(!init?.body)await identity.promise;active--;return ok({user_id:'A',progress:{}});});
first.run('qb-progress-transport');
const a=load(first),b=load(first),early=save(first);await flush();assert.equal(calls.length,1);
identity.resolve();await Promise.all([a,b,early]);assert.equal(calls.length,2);assert.equal(maxActive,1);
assert.equal(JSON.parse(calls[1].init.body).expected_user_id,'A');
assert.equal(outbox(first.shared).length,0);
await load(first);assert.equal(calls.length,3,'a successful write invalidates cached reads');

// Exhausting retries does not discard an immutable canonical submission.
let down=false;const failures=[];
const outage=harness(async(_url,init)=>{if(init?.body){failures.push(JSON.parse(init.body));if(down)return new Response('{}',{status:503,headers:{'Retry-After':'30'}});}return ok({user_id:'A',progress:{}});});
outage.run('qb-progress-transport');await load(outage);down=true;
const failing=save(outage);await flush();assert.equal(failures.length,1);
await outage.advance(29000);assert.equal(failures.length,1,'Retry-After respected');
await outage.advance(2000);assert.equal(failures.length,2);
await outage.advance(100000);assert.equal((await failing).status,503);assert.equal(failures.length,3);assert.equal(outbox(outage.shared).length,1);
assert.equal(failures[0].updates[0].submission_id,saveBody.updates[0].submission_id);
assert.equal(failures[2].updates[0].answer_elapsed_seconds,48.2);

// Reloading as B cannot replay A's saved requests; signing back in as A replays exactly once.
const otherCalls=[];const other=harness(async(url,init)=>{otherCalls.push({url,init});return ok({user_id:'B',progress:{}});},outage.shared);
other.run('qb-progress-transport');await load(other);assert.deepEqual(plain(other.context.TS_QB_TRANSPORT.pendingUpdates('tmua-question-bank')),[]);await other.advance(0);assert.equal(otherCalls.length,1);assert.equal(outbox(outage.shared).length,1);
const recovered=[];const resume=harness(async(url,init)=>{if(init?.body)recovered.push(JSON.parse(init.body));return ok({user_id:'A',progress:{}});},outage.shared);
resume.run('qb-progress-transport');await load(resume);await resume.advance(0);
assert.equal(recovered.length,1);assert.deepEqual(recovered[0],failures[0]);assert.equal(outbox(outage.shared).length,0);

// Every queued check is durable before an earlier blocked request can finish.
const stuck=deferred();const waiting=harness(async(_url,init)=>init?.body?stuck.promise:ok({user_id:'A',progress:{}}));
waiting.run('qb-progress-transport');await load(waiting);void save(waiting);await flush();
const secondBody=plain(saveBody);secondBody.updates[0].question_id='190';secondBody.updates[0].submission_id='tmua-stable-v1|190|second';
void waiting.context.fetch('/api/qb/progress/save',{method:'POST',body:JSON.stringify(secondBody)});
const thirdBody=plain(saveBody);thirdBody.updates[0].question_id='191';thirdBody.updates[0].submission_id='tmua-stable-v1|191|third';
void waiting.context.fetch('/api/qb/progress/save',{method:'POST',body:JSON.stringify(thirdBody)});
assert.equal(outbox(waiting.shared).length,3);
const afterClose=[];const restoredQueue=harness(async(_url,init)=>{if(init?.body)afterClose.push(JSON.parse(init.body));return ok({user_id:'A',progress:{}});},waiting.shared);
restoredQueue.run('qb-progress-transport');await load(restoredQueue);await restoredQueue.advance(0);
assert.deepEqual(afterClose.map(b=>b.updates[0].submission_id),[saveBody.updates[0].submission_id,secondBody.updates[0].submission_id,thirdBody.updates[0].submission_id]);
assert.equal(outbox(waiting.shared).length,0);

// A session switch between queuing and dispatch pauses both write and read recovery.
let switched=false;const switcher=harness(async(_url,init)=>init?.body?new Response(JSON.stringify({ok:false,code:'ACCOUNT_CHANGED'}),{status:409}):ok({user_id:switched?'B':'A',progress:{}}));
switcher.run('qb-progress-transport');await load(switcher);assert.equal((await save(switcher)).status,409);
assert.equal(switcher.context.TS_QB_TRANSPORT.paused(),true);assert.equal(outbox(switcher.shared).length,1);

// Stale identity-version records stay recoverable without blocking valid new work.
let identityPosts=0;const obsolete=harness(async(_url,init)=>{if(init?.body&&++identityPosts===1)return Response.json({error:'Reload',extra:{code:'TMUA_IDENTITY_VERSION_REQUIRED'}},{status:409});return ok({user_id:'A',progress:{}});});
obsolete.run('qb-progress-transport');await load(obsolete);assert.equal((await save(obsolete)).status,409);
assert.equal(outbox(obsolete.shared).length,0);assert.ok([...obsolete.shared.keys()].some(k=>k.startsWith('ts_qb_submission_rejected_v3:A:')));
assert.equal((await save(obsolete)).status,200);assert.equal(identityPosts,2);

// A hanging network request is aborted before another retry starts.
let aborts=0;const hangs=harness(async(_url,init)=>new Promise((resolve,reject)=>init.signal.addEventListener('abort',()=>{aborts++;reject(new DOMException('Timed out','AbortError'));},{once:true})));
hangs.run('qb-progress-transport');const hung=load(hangs).then(()=>null,error=>error);await flush();
await hangs.advance(16000);await hangs.advance(10000);await hangs.advance(16000);await hangs.advance(10000);await hangs.advance(16000);
assert.equal(aborts,3);assert.equal((await hung).name,'AbortError');

// A fresh read after a different sign-in never returns the other account's rows.
let remoteOwner='A';const readSwitch=harness(async()=>ok({user_id:remoteOwner,progress:{secret:remoteOwner}}));
readSwitch.run('qb-progress-transport');await load(readSwitch);remoteOwner='B';await readSwitch.advance(11000);
const changedAccount=await load(readSwitch);assert.equal(changedAccount.status,409);assert.equal((await changedAccount.json()).progress,undefined);

// Unowned legacy browser state remains recoverable but never enters another account.
const legacy={answers:{'999':{selected:'H',checked:true,solution_html:'old student solution'}},filters:{}};
const old=new Map([[key,JSON.stringify(legacy)],[key+'__pending_delta_v2',JSON.stringify(legacy)]]);const compactWrites=[];
const unowned=harness(async(_url,init)=>{if(init?.body)compactWrites.push(JSON.parse(init.body));return ok({user_id:'B',data:{parsed:{answers:{'12':{selected:'B',checked:true}}}}});},old);
unowned.run('qb-compact-sync');const clean=unowned.context.TS_QB_COMPACT.start('tmua-question-bank',key);
assert.deepEqual(JSON.parse(unowned.context.localStorage.getItem(key)).answers,{});assert.deepEqual(plain(clean.pendingAnswers()),{});
await clean.sync();assert.equal(compactWrites.length,0);assert.equal(JSON.parse(unowned.context.localStorage.getItem(key)).answers['999'],undefined);
assert.equal(JSON.parse(old.get(key+'__unassigned_legacy_v3')).raw_key,key);
assert.equal(old.get(key),JSON.stringify(legacy),'legacy data stays recoverable without another quota-heavy copy');

// Compact edits made during a slow POST survive acknowledgement and reload.
const hold=deferred();let compactDown=false;const patches=[];
const compactClient=harness(async(_url,init)=>{if(!init?.body)return ok({user_id:'A',data:{parsed:{answers:{'1':{selected:'A',checked:true}},filters:{}}}});patches.push(JSON.parse(init.body));if(compactDown)return new Response('{}',{status:503});return hold.promise;});
compactClient.run('qb-compact-sync');const engine=compactClient.context.TS_QB_COMPACT.start('tmua-question-bank',key);await engine.sync();
function edit(client,qid,selected){const state=JSON.parse(client.context.localStorage.getItem(key));state.answers[qid]={selected,checked:true,solution_html:'large'.repeat(1000),time_spent:29};client.context.localStorage.setItem(key,JSON.stringify(state));}
edit(compactClient,'2','B');const pending=engine.sync();await flush();edit(compactClient,'3','C');
hold.resolve(ok({saved:{user_id:'A'}}));await pending;compactDown=true;await engine.sync();
assert.equal(patches[0].patch.answers['2'].solution_html,undefined);assert.equal(patches[0].patch.answers['2'].time_spent,29);
assert.deepEqual(Object.keys(patches[0].patch.answers),['2']);assert.deepEqual(Object.keys(patches[1].patch.answers),['3']);
const resumedPatches=[];const compactReload=harness(async(_url,init)=>{if(init?.body){resumedPatches.push(JSON.parse(init.body));return ok({saved:{user_id:'A'}});}return ok({user_id:'A',data:{parsed:{answers:{'1':{selected:'A',checked:true},'2':{selected:'B',checked:true,time_spent:29}},filters:{}}}});},compactClient.shared);
compactReload.run('qb-compact-sync');await compactReload.context.TS_QB_COMPACT.start('tmua-question-bank',key).sync();
assert.equal(resumedPatches.length,1);assert.equal(resumedPatches[0].patch.answers['3'].selected,'C');
assert.equal(resumedPatches[0].expected_user_id,'A');

// Concurrent tabs preserve disjoint canonical question IDs in one atomic delta.
const shared=new Map(),locks=new Map(),cloud={answers:{},filters:{}},multi=[],notifications=[];
shared.notify=event=>notifications.push(event);
const network=async(_url,init)=>{if(init?.body){const body=JSON.parse(init.body);multi.push(body);Object.assign(cloud.answers,body.patch.answers);return ok({saved:{user_id:'A'}});}return ok({user_id:'A',data:{parsed:plain(cloud)}});};
const one=harness(network,shared,locks),two=harness(network,shared,locks);one.run('qb-compact-sync');two.run('qb-compact-sync');
const oneEngine=one.context.TS_QB_COMPACT.start('tmua-question-bank',key),twoEngine=two.context.TS_QB_COMPACT.start('tmua-question-bank',key);
await oneEngine.sync();await twoEngine.sync();notifications.length=0;edit(one,'42','D');edit(two,'81','F');await Promise.all([oneEngine.sync(),twoEngine.sync()]);
assert.equal(cloud.answers['42'].selected,'D');assert.equal(cloud.answers['81'].selected,'F');
assert.equal(shared.get(scope('A')+'state').includes('solution_html'),false);
edit(one,'99','A');edit(two,'99','B');
let delivered=0;while(notifications.length&&delivered<100){const event=notifications.shift();for(const browser of [one,two])if(browser.context!==event.source)browser.dispatch({type:'storage',...event});delivered++;}
assert.ok(delivered<100,'storage events must not bounce between tabs forever');assert.equal(notifications.length,0);
// An older tab must not recreate a journal already acknowledged by another tab.
edit(one,'91','A');await two.advance(10);edit(two,'91','B');
await twoEngine.sync();await oneEngine.sync();assert.equal(cloud.answers['91'].selected,'B');
const oldSnapshot=new Map([[scope('A')+'state',JSON.stringify({answers:{'91':{selected:'OLD'}}})],[scope('A')+'ack',JSON.stringify({answers:{'91':{selected:'NEW'}}})]]);
let staleWrites=0;const stale=harness(async(_url,init)=>{if(init?.body)staleWrites++;return ok({user_id:'A',data:{parsed:{answers:{'91':{selected:'CLOUD'}}}}});},oldSnapshot);
stale.run('qb-compact-sync');await stale.context.TS_QB_COMPACT.start('tmua-question-bank',key).sync();
assert.equal(staleWrites,0);assert.equal(JSON.parse(stale.context.localStorage.getItem(key)).answers['91'].selected,'CLOUD');
// A journal created between send-snapshot and bookkeeping must never be acknowledged unseen.
const interleaved=new Map(),wire=[];let inject=false;const nativeSet=interleaved.set.bind(interleaved);
interleaved.set=(name,value)=>{const result=nativeSet(name,value);if(inject&&name.includes(':pending:')&&JSON.parse(value).patch?.answers?.['22']){inject=false;nativeSet(scope('A')+'pending:late',JSON.stringify({at:100002,patch:{answers:{'33':{selected:'G'}}}}));}return result;};
const race=harness(async(_url,init)=>{if(init?.body){wire.push(JSON.parse(init.body));return ok({saved:{user_id:'A'}});}return ok({user_id:'A',data:{parsed:{answers:{}}}});},interleaved);
race.run('qb-compact-sync');const raceEngine=race.context.TS_QB_COMPACT.start('tmua-question-bank',key);await raceEngine.sync();edit(race,'11','A');
nativeSet(scope('A')+'pending:other',JSON.stringify({at:100001,patch:{answers:{'22':{selected:'B'}}}}));inject=true;await raceEngine.sync();
assert.equal(wire[0].patch.answers['33'],undefined);assert.ok(interleaved.has(scope('A')+'pending:late'),'unsent late journal retained');
await raceEngine.sync();assert.equal(wire[1].patch.answers['33'].selected,'G');

// Canonical submissions also retry from memory if browser storage is full.
let quotaDown=false,quotaCalls=0;const quotaTransport=harness(async(_url,init)=>{if(init?.body){quotaCalls++;return quotaDown?new Response('{}',{status:503}):ok({saved:{user_id:'A'}});}return ok({user_id:'A',progress:{}});});
quotaTransport.context.Storage.prototype.setItem=function(){throw Error('QuotaExceededError');};
quotaTransport.run('qb-progress-transport');await load(quotaTransport);quotaDown=true;const quotaWrite=save(quotaTransport);await flush();
await quotaTransport.advance(10000);await quotaTransport.advance(20000);assert.equal((await quotaWrite).status,503);assert.equal(quotaCalls,3);
quotaDown=false;await quotaTransport.advance(70000);assert.equal(quotaCalls,4);assert.equal(quotaTransport.context.TS_QB_LOCAL_STORAGE_UNAVAILABLE,true);

// A full local-storage quota warns clearly but does not break online saving.
const quotaPatches=[];const quota=harness(async(_url,init)=>{if(init?.body){quotaPatches.push(JSON.parse(init.body));return ok({saved:{user_id:'A'}});}return ok({user_id:'A',data:{parsed:{answers:{}}}});});
quota.context.Storage.prototype.setItem=function(){throw new Error('QuotaExceededError');};
quota.run('qb-compact-sync');const quotaEngine=quota.context.TS_QB_COMPACT.start('tmua-question-bank',key);await quotaEngine.sync();
edit(quota,'55','E');await quotaEngine.sync();assert.equal(quotaPatches[0].patch.answers['55'].selected,'E');
assert.equal(quota.context.TS_QB_LOCAL_STORAGE_UNAVAILABLE,true);
// Execute both shipped timer scripts around the real shared transport. A timer
// hook must hand later submissions to the durable outbox while the first waits.
for (const exam of ['tmua','esat']) {
  const page=readFileSync(`public/${exam}-question-bank/index.html`,'utf8');
  const timerSource=page.match(/<script id="ts-qb-question-timer-v1">([\s\S]*?)<\/script>/)[1];
  const timerKey=(exam==='tmua'?'ts_qb_question_timer_state_v2_stable:':'ts_qb_question_timer_state_v1:')+exam+'-question-bank';
  const accountKey=timerKey+':account-v3:A', oldTimer=JSON.stringify({pendingMs:{45:999000},finalSeconds:{46:999}});
  const timerStorage=new Map([[timerKey,oldTimer],[accountKey,JSON.stringify({pendingMs:{45:9000},finalSeconds:{46:120}})]]);
  const authWait=deferred(),deliveryWait=deferred();let timerWrites=0;
  const timerBrowser=harness(async(_url,init)=>{if(init?.body){timerWrites++;return deliveryWait.promise;}return authWait.promise;},timerStorage);
  timerBrowser.context.location.pathname=`/${exam}-question-bank/index.html`;
  timerBrowser.run('qb-progress-transport');
  vm.runInContext(timerSource.replace(/\}\)\(\);\s*$/,`window.__timerProbe={local:()=>localState,save:saveLocalState,pending:(qid,ms)=>{localState.pendingMs[qid]=ms;}};})();`),timerBrowser.context);
  assert.deepEqual(plain(timerBrowser.context.__timerProbe.local()),{pendingMs:{},finalSeconds:{}});
  timerBrowser.context.__timerProbe.pending('45',5000);timerBrowser.context.__timerProbe.save();
  authWait.resolve(ok({user_id:'A',progress:{}}));await flush();
  assert.equal(timerBrowser.context.__timerProbe.local().pendingMs['45'],14000);
  assert.equal(timerBrowser.context.__timerProbe.local().finalSeconds['46'],120);
  assert.equal(timerStorage.get(timerKey),oldTimer,'legacy timer retained, never assigned');
  const actualBody=plain(saveBody);actualBody.product=exam+'-question-bank';
  actualBody.identity_version=exam==='tmua'?'tmua-display-order-v1':'esat-qid-v1';
  if(exam==='esat')actualBody.updates[0].question_id='ESAT-PHY-0026';
  const actualFirst=timerBrowser.context.fetch('/api/qb/progress/save',{method:'POST',body:JSON.stringify(actualBody)});
  await flush();actualBody.updates[0].submission_id+='-next';actualBody.updates[0].question_id=exam==='tmua'?'190':'ESAT-PHY-0027';
  const actualSecond=timerBrowser.context.fetch('/api/qb/progress/save',{method:'POST',body:JSON.stringify(actualBody)});
  assert.equal(outbox(timerStorage).length,2,exam+' timer must not hide a queued submission in memory');assert.equal(timerWrites,1);
  deliveryWait.resolve(ok({saved:{user_id:'A'}}));await Promise.all([actualFirst,actualSecond]);assert.equal(timerWrites,2);
  timerBrowser.dispatch({type:'ts-qb-account-changed',detail:{user_id:'A'}});assert.equal(timerBrowser.context.__timerProbe.save(),false);
}
console.log('PASS: durable owner-bound submissions, immutable IDs/times, reload recovery, retry backoff, cache invalidation, legacy isolation, in-flight edits and multi-tab deltas.');
