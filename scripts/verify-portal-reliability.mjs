import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';

const flush = async () => { for (let n = 0; n < 40; n++) await Promise.resolve(); };
const deferred = () => { let resolve, reject; const promise = new Promise((a,b) => { resolve=a; reject=b; }); return {promise,resolve,reject}; };
const plain = x => JSON.parse(JSON.stringify(x));
const ok = value => Response.json({ok:true,...value});
const storageKey = 'ts_tmua_supabase_exact_ui_v4';
function browser(fetcher, saved = {}) {
  let clock = 100000, id = 0;
  const timers = new Map(), listeners = new Map(), values = new Map(Object.entries(saved));
  class Storage { getItem(k){return values.get(k)||null;} setItem(k,v){values.set(k,String(v));} }
  const listen=(name,fn)=>{const list=listeners.get(name)||[];list.push(fn);listeners.set(name,list);};
  const context=vm.createContext({console:{warn(){},error(){}},JSON,Math,Map,Set,Promise,URL,Response,Request,AbortController,
    Date:class extends Date {static now(){return clock;}},
    Storage,localStorage:new Storage(),
    setTimeout:(fn,ms)=>{timers.set(++id,{fn,at:clock+ms});return id;},clearTimeout:n=>timers.delete(n),
    addEventListener:listen,
    dispatchEvent:e=>{for(const f of listeners.get(e.type)||[])f(e);},
    CustomEvent:class {constructor(type,options){this.type=type;this.detail=options.detail;}},
    location:{origin:'https://portal.test',href:'https://portal.test/tmua-question-bank'},
    document:{visibilityState:'visible',addEventListener:listen,getElementById:()=>({style:{}})},
    fetch:fetcher
  });
  context.window=context;
  const run=file=>vm.runInContext(readFileSync(file,'utf8'),context);
  return {context,values,run,advance:async ms=>{
    clock+=ms;
    for (const [n,t] of [...timers]) if(t.at<=clock){timers.delete(n);t.fn();}
    await flush();
  }};
}

// Overlapping reads deduplicate; all progress writes share the same queue.
const blocked=deferred();let active=0,maxActive=0,calls=[];
const network=browser(async (url,init)=>{
  calls.push({url,init});maxActive=Math.max(maxActive,++active);
  if(calls.length===1)await blocked.promise;
  active--;return ok({progress:{}});
});
network.run('public/qb-progress-transport.js');
const a=network.context.fetch('/api/qb/progress/load?product=tmua-question-bank');
await network.advance(1500);
const b=network.context.fetch('/api/qb/progress/load?product=tmua-question-bank');
const c=network.context.fetch('/api/qb/progress/save',{method:'POST',body:'{"submission_id":"same-id"}'});
await flush();assert.equal(calls.length,1);
blocked.resolve();await Promise.all([a,b,c]);assert.equal(calls.length,2);assert.equal(maxActive,1);
assert.equal((await a).bodyUsed,false);assert.equal((await b).bodyUsed,false);

// Failed requests back off, respect Retry-After, and retry the immutable submission.
let attempts=[];
const outage=browser(async (_url,init)=>{
  attempts.push(init.body);
  return attempts.length===1 ? new Response('{}',{status:503,headers:{'Retry-After':'30'}}) : ok({});
});
outage.run('public/qb-progress-transport.js');
const retry=outage.context.fetch('/api/qb/progress/save',{method:'POST',body:'{"submission_id":"original"}'});
await flush();assert.equal(attempts.length,1);
await outage.advance(29000);assert.equal(attempts.length,1);
await outage.advance(2000);await retry;
assert.deepEqual(attempts,['{"submission_id":"original"}','{"submission_id":"original"}']);

const helpers=browser(async()=>ok({}));helpers.run('public/qb-compact-sync.js');
const {compact,delta,merge}=helpers.context.TS_QB_COMPACT;
const rich={answers:Object.fromEntries(Array.from({length:100},(_,i)=>[String(i+1),{
  selected:'A',checked:true,isCorrect:true,flagged:i===0,time_spent:47,solution_html:'x'.repeat(4096)
}])),filters:{topics:['Algebra']}};
const small=compact(rich);
assert.ok(JSON.stringify(small).length<JSON.stringify(rich).length*0.04);
assert.equal(small.answers['1'].time_spent,47);assert.equal(small.answers['1'].flagged,true);
assert.equal(rich.answers['1'].solution_html.length,4096);
const changed=plain(small);changed.answers['2'].selected='B';
assert.deepEqual(plain(delta(small,changed)),{answers:{'2':changed.answers['2']}});
assert.deepEqual(plain(merge(small,{answers:{'101':{selected:'H'}}})).answers['1'],plain(small.answers['1']));

// A slow initial cloud read cannot replace work completed while it was in flight.
const cloudRead=deferred(), firstSave=deferred();const sent=[];
const client=browser(async (_url,init)=>{
  if(!init?.body)return cloudRead.promise;
  sent.push(JSON.parse(init.body));
  if(sent.length===1)return firstSave.promise;
  return ok({saved:{updated_at:'v3'}});
},{[storageKey]:JSON.stringify({answers:{},filters:{}})});
client.run('public/qb-compact-sync.js');
const engine=client.context.TS_QB_COMPACT.start('tmua-question-bank',storageKey);
const initial=engine.sync();await flush();
client.context.localStorage.setItem(storageKey,JSON.stringify({answers:{'8':{selected:'H',checked:true,isCorrect:true,solution_html:'keep locally'}},filters:{}}));
cloudRead.resolve(ok({data:{parsed:{answers:{'7':{selected:'B',checked:true,flagged:true}},filters:{}}},updated_at:'v1'}));
await flush();
const restored=JSON.parse(client.values.get(storageKey));
assert.equal(restored.answers['7'].flagged,true);assert.equal(restored.answers['8'].selected,'H');
assert.equal(sent.length,1);assert.deepEqual(Object.keys(sent[0].patch.answers),['8']);
assert.equal(sent[0].patch.answers['8'].solution_html,undefined);
assert.equal(JSON.parse(client.values.get(storageKey+'__pending_delta_v2')).answers['8'].selected,'H');
restored.answers['9']={selected:'F'};
client.context.localStorage.setItem(storageKey,JSON.stringify(restored));
await engine.sync();assert.equal(sent.length,1);
firstSave.resolve(ok({saved:{updated_at:'v2'}}));await initial;
await engine.sync();assert.equal(sent.length,2);assert.deepEqual(Object.keys(sent[1].patch.answers),['9']);

// Offline work survives a reload: acknowledgement never advances on a failed save.
const offline=browser(async (_url,init)=> init?.body ? new Response('{}',{status:503})
  :ok({data:{parsed:small},updated_at:'v1'}),{[storageKey]:JSON.stringify(changed),[storageKey+'__compact_ack_v2']:JSON.stringify(small)});
offline.run('public/qb-compact-sync.js');
await offline.context.TS_QB_COMPACT.start('tmua-question-bank',storageKey).sync();
assert.equal(JSON.parse(offline.values.get(storageKey+'__compact_ack_v2')).answers['2'].selected,'A');
const resumed=[];
const recovery=browser(async (_url,init)=>{
  if(init?.body){resumed.push(JSON.parse(init.body));return ok({saved:{}});}
  return ok({data:{parsed:small},updated_at:'v1'});
},Object.fromEntries(offline.values));
recovery.run('public/qb-compact-sync.js');
await recovery.context.TS_QB_COMPACT.start('tmua-question-bank',storageKey).sync();
assert.equal(resumed.length,1);assert.deepEqual(Object.keys(resumed[0].patch.answers),['2']);
assert.equal(resumed[0].patch.answers['2'].selected,'B');

// A first-upgrade tab closed before its initial cloud read also retains known local edits.
const firstOffline=browser(async()=>{throw Error('offline');},{[storageKey]:JSON.stringify(small)});
firstOffline.run('public/qb-compact-sync.js');
const firstEngine=firstOffline.context.TS_QB_COMPACT.start('tmua-question-bank',storageKey);
firstOffline.context.localStorage.setItem(storageKey,JSON.stringify(changed));
await firstEngine.sync();
const firstRecovered=[];
const firstReconnect=browser(async(_url,init)=>{
  if(init?.body){firstRecovered.push(JSON.parse(init.body));return ok({saved:{}});}
  return ok({data:{parsed:small},updated_at:'new-server-version'});
},Object.fromEntries(firstOffline.values));
firstReconnect.run('public/qb-compact-sync.js');
await firstReconnect.context.TS_QB_COMPACT.start('tmua-question-bank',storageKey).sync();
assert.equal(firstRecovered[0].patch.answers['2'].selected,'B');

// Execute real TS route handlers with a scoped Supabase double.
function moduleAt(file,imports={}) {
  const code=ts.transpileModule(readFileSync(file,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
  const ctx=vm.createContext({exports:{},require:name=>{if(!(name in imports))throw Error(name);return imports[name];},
    console:{error(){}},process:{env:{}},Response,Request,URL,Date,JSON,AbortSignal,fetch,setTimeout,clearTimeout});
  vm.runInContext(code,ctx);return ctx.exports;
}
const recoveryModule=moduleAt('lib/auth/service-recovery.ts');
const compactModule=moduleAt('lib/qb/compact-progress.ts');
assert.deepEqual(plain(compactModule.compactProgressState(rich)),plain(small));
let authError=null,accessError=null,allowed=true,rpcArgs;
const db={auth:{getUser:async()=>({data:{user:{id:'isolated-user',email:'student@example.test'}},error:authError})},
  from:table=>{
    const q={select:()=>q,ilike:()=>q,eq:()=>q,or:()=>q,limit:async()=>({data:allowed?[{approved:true}]:[],error:accessError}),
      maybeSingle:async()=>({data:{data:{parsed:rich}},error:null})};return q;
  },rpc:async(name,args)=>{rpcArgs={name,args};return {data:'2026-09-20T17:00:00Z',error:null};}};
const api=moduleAt('app/api/qb/user-progress/route.ts',{
  '@/utils/supabase/server':{supabaseServer:async()=>db},
  '@/lib/qb/compact-progress':compactModule,'@/lib/auth/service-recovery':recoveryModule
});
const req=()=>new Request('https://portal.test/api/qb/user-progress?product=tmua-question-bank&format=compact-v2');
authError={name:'AuthRetryableFetchError'};assert.equal((await api.GET(req())).status,503);
authError=null;accessError={message:'Database timeout'};assert.equal((await api.GET(req())).status,503);
accessError=null;allowed=false;assert.equal((await api.GET(req())).status,403);
allowed=true;const read=await api.GET(req());assert.equal(read.status,200);
const data=await read.json();assert.equal(data.data.raw,undefined);assert.equal(data.data.parsed.answers['1'].solution_html,undefined);
const write=await api.POST(new Request('https://portal.test/api/qb/user-progress',{method:'POST',body:JSON.stringify({
  product:'tmua-question-bank',version:2,patch:{answers:{'8':{selected:'H',solution_html:'not stored'}}}
})}));
assert.equal(write.status,200);assert.equal(rpcArgs.name,'save_qb_app_state_v2');
assert.deepEqual(plain(rpcArgs.args.p_patch),{answers:{'8':{selected:'H'}}});

// The real access proxy never calls a database outage "pending approval".
const replies={
  next:()=>({kind:'next',cookies:{set(){}}}),
  redirect:url=>({kind:'redirect',url}),
  rewrite:(url,options)=>({kind:'rewrite',url,...options})
};
const proxy=moduleAt('proxy.ts',{'@supabase/ssr':{createServerClient:()=>db},
  'next/server':{NextResponse:replies},'@/lib/auth/service-recovery':recoveryModule});
const proxyRequest=path=>{
  const url=new URL(path,'https://portal.test');url.clone=()=>new URL(url);
  return {nextUrl:url,cookies:{getAll:()=>[],set(){}}};
};
authError={name:'AuthRetryableFetchError'};
let routed=await proxy.proxy(proxyRequest('/tmua-question-bank/index.html'));
assert.equal(routed.status,503);assert.equal(routed.url.pathname,'/service-unavailable');
assert.equal(routed.url.searchParams.get('next'),'/tmua-question-bank/index.html');
authError=null;accessError={message:'timeout'};
assert.equal((await proxy.proxy(proxyRequest('/esat-question-bank/index.html'))).status,503);
accessError=null;allowed=false;
assert.equal((await proxy.proxy(proxyRequest('/esat-question-bank/index.html'))).url.pathname,'/pending');
allowed=true;
assert.equal((await proxy.proxy(proxyRequest('/esat-question-bank/index.html'))).kind,'next');
assert.equal((await proxy.proxy(proxyRequest('/practice-tests/solutions/test.pdf'))).kind,'next');
console.log('PASS: Compact deltas preserve answers/flags/timers; slow reads and offline reloads preserve new work; sync is serialized, deduplicated and backed off; transient access errors are 503, genuine denials remain 403.');
