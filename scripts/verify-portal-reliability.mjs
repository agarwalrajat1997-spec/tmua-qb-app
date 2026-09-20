import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';

// Execute the real shared browser scripts, with authenticated account ownership,
// durable outboxes, storage events, quota failures and outage/reload scenarios.
await import('./verify-qb-durable-sync.mjs');
const plain = value => JSON.parse(JSON.stringify(value));
const rich = { answers: Object.fromEntries(Array.from({ length: 100 }, (_, i) => [String(i + 1), {
  selected: 'A', checked: true, isCorrect: true, flagged: i === 0,
  time_spent: 47, solution_html: 'x'.repeat(4096)
}])), filters: { topics: ['Algebra'] } };
const small = plain(rich);
for (const answer of Object.values(small.answers)) delete answer.solution_html;

// Execute real TS route handlers with a scoped Supabase double.
function moduleAt(file,imports={}) {
  const code=ts.transpileModule(readFileSync(file,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
  const ctx=vm.createContext({exports:{},require:name=>{if(!(name in imports))throw Error(name);return imports[name];},
    console:{error(){}},process:{env:{}},Response,Request,URL,Date,JSON,AbortSignal,DOMException,fetch,setTimeout,clearTimeout});
  vm.runInContext(code,ctx);return ctx.exports;
}
const recoveryModule=moduleAt('lib/auth/service-recovery.ts');
const compactModule=moduleAt('lib/qb/compact-progress.ts');
assert.deepEqual(plain(compactModule.compactProgressState(rich)),plain(small));
let authError=null,accessError=null,allowed=true,rpcArgs;
const db={auth:{getUser:async()=>({data:{user:{id:'isolated-user',email:'student@example.test'}},error:authError})},
  from:table=>{
    const q={select:()=>q,ilike:()=>q,eq:()=>q,or:()=>q,
      limit:()=>({retry:async enabled=>{assert.equal(enabled,false);return {data:allowed?[{approved:true}]:[],error:accessError};}}),
      maybeSingle:()=>({retry:async enabled=>{assert.equal(enabled,false);return {data:{data:{parsed:rich}},error:null};}})};return q;
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
  next:()=>({kind:'next',cookies:{set(){},getAll:()=>[]}}),
  redirect:url=>({kind:'redirect',url,cookies:{set(){},getAll:()=>[]}}),
  rewrite:(url,options)=>({kind:'rewrite',url,...options,cookies:{set(){},getAll:()=>[]}})
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
