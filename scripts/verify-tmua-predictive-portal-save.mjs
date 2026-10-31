import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const source=readFileSync('public/practice-tests/tests/tmua-2026-predictive-paper/index.html','utf8').replace(/\r\n/g,'\n');
const start=source.indexOf('function updatePortalButton(){'),end=source.indexOf('\nfunction authorPanel()',start);
assert.ok(start>0&&end>start);
const renderStart=source.indexOf("${portalAvailable()?'<button class=\"secondary\" id=\"savePortal\"");
const renderEnd=source.indexOf("</button>':''}",renderStart)+"</button>':''}".length;
assert.ok(renderStart>0&&renderEnd>renderStart);
const buttonExpression=source.slice(renderStart+2,renderEnd-1);
const readStart=source.indexOf('function readSaved(){'),readEnd=source.indexOf('\nfunction freshState(',readStart);
assert.ok(readStart>0&&readEnd>readStart);
const id='5a336ae4-5678-4123-8912-0123456789ab',calls=[];
let nextPost='ok',nextLookup='saved',persisted;
const elements={savePortal:{disabled:false},deliveryStatus:{textContent:''}};
const state={status:'finished',candidate:{email:'student@example.test'},portalState:'idle',attemptId:id};
const context=vm.createContext({state,pack:{id:'tmua-2026-predictive-paper',settings:{portalEndpoint:'/api/practice-tests/submit'}},
  prefs:{},portalAvailable:()=>true,emailConfigured:()=>false,$:key=>elements[key],persist(){},toast(){},
  buildReport:()=>({attemptId:context.state.attemptId,test_id:'tmua-2026-predictive-paper'}),safeUrl:x=>x,
  storageCandidates:()=>[{key:'test',hash:'verified'}],localStorage:{getItem:()=>JSON.stringify({fingerprint:'verified',state:persisted})},practiceOptions:{restore(){},metadata:()=>null},
  AbortController,setTimeout:()=>1,clearTimeout(){},Date,JSON,encodeURIComponent,
  async fetch(url,options){
    calls.push({url,method:options.method??'GET'});
    if(options.method==='POST'){
      const response=nextPost;nextPost='ok';
      if(response==='timeout')throw new DOMException('Timed out','AbortError');
      if(typeof response==='number')return{ok:false,status:response};
      return{ok:true,status:200,async json(){if(response==='malformed')throw Error('Invalid acknowledgement');return{ok:true};}};
    }
    assert.match(url,/client_attempt_id=/);assert.equal(options.credentials,'same-origin');assert.equal(options.cache,'no-store');
    if(nextLookup==='outage')throw Error('offline');
    return{ok:true,async json(){return{ok:true,client_attempt_id:nextLookup==='wrong-id'?'different':id,saved:nextLookup==='saved',attempt:nextLookup==='saved'?{id:'server-attempt',test_id:context.pack.id}:null};}};
  },
});
vm.runInContext(source.slice(start,end)+'\nfunction renderedPortalButton(){return '+buttonExpression+';}\n'+source.slice(readStart,readEnd),context);
await context.sendReport('portal');assert.equal(state.portalState,'saved');assert.equal(calls.filter(x=>x.method==='POST').length,1);
assert.match(context.renderedPortalButton(),/disabled/);assert.match(context.renderedPortalButton(),/Saved to portal/);
elements.savePortal={disabled:false};await context.sendReport('portal');assert.equal(calls.filter(x=>x.method==='POST').length,1,'Rerender must not re-submit a saved attempt.');

// A saved page reload and an interrupted request restore the actual readSaved
// state. Unknown requests can only look up an exact authenticated saved record.
function savedState(portalState){return{...state,portalState,portalAutoAttempted:true,paperIndex:0,questionIndex:0,answers:[Array(20).fill(null),Array(20).fill(null)],flags:[Array(20).fill(false),Array(20).fill(false)],times:[Array(20).fill(0),Array(20).fill(0)],paperEnds:[null,null],paperUsed:[0,0],candidate:{name:'Student',email:'student@example.test'},finishedAt:Date.now()};}
persisted=savedState('saved');context.state=context.readSaved();assert.equal(context.state.portalState,'saved');assert.match(context.renderedPortalButton(),/disabled/);await context.sendReport('portal');assert.equal(calls.filter(x=>x.method==='POST').length,1);
for(const interrupted of ['sending','checking']){
  persisted=savedState(interrupted);context.state=context.readSaved();assert.equal(context.state.portalState,'unknown');assert.equal(context.state.portalAutoAttempted,true);
  assert.match(context.renderedPortalButton(),/Check portal save/);await context.sendReport('portal');assert.equal(context.state.portalState,'saved');assert.equal(calls.filter(x=>x.method==='POST').length,1);
}
for(const failure of ['timeout','malformed',500]){
  context.state={...state,portalState:'idle'};nextPost=failure;const before=calls.filter(x=>x.method==='POST').length;
  await context.sendReport('portal');assert.equal(context.state.portalState,'unknown');nextLookup='saved';await context.sendReport('portal');
  assert.equal(context.state.portalState,'saved');assert.equal(calls.filter(x=>x.method==='POST').length,before+1,'Ambiguous recovery must never blindly POST again.');
}
for(const result of ['no-match','outage','wrong-id']){
  context.state={...state,portalState:'unknown'};nextLookup=result;const before=calls.filter(x=>x.method==='POST').length;
  await context.sendReport('portal');assert.equal(context.state.portalState,'unknown');assert.equal(calls.filter(x=>x.method==='POST').length,before);assert.match(context.state.portalStatus,/downloads remain available/);
}
for(const code of [400,401,403]){
  context.state={...state,portalState:'idle'};nextPost=code;await context.sendReport('portal');assert.equal(context.state.portalState,'rejected');assert.equal(elements.savePortal.disabled,false);
  await context.sendReport('portal');assert.equal(context.state.portalState,'saved','A definite pre-insert rejection may be retried after correction.');
}
context.state={...state,portalState:'unknown',attemptId:undefined};const beforeOld=calls.length;await context.sendReport('portal');assert.equal(calls.length,beforeOld);assert.match(context.state.portalStatus,/older report/);
console.log('PASS: predictive saved handler/render/reload blocks duplicate POST; interrupted saves become lookup-only; timeout/5xx recover by exact ID; no match/other acknowledgement stays unconfirmed; definite400/401/403 can retry; old reports remain downloadable. All networking mocked.');
