// Local control regression fixture. UI actions are performed through Cua.
// node scripts/serve-ib-filter-regression.mjs --serve-only [--port=3196]
// Uses real ReactDOM/filter components and a synchronously void router recorder.
// This deliberately makes no claim to simulate Next RSC transport or recovery.
import {createServer} from 'node:http';
import {readFileSync,mkdirSync,mkdtempSync} from 'node:fs';
import {resolve,join} from 'node:path';
import {createHash} from 'node:crypto';
import {build} from 'esbuild';

const args=process.argv.slice(2);
if(!args.includes('--serve-only')||args.some(a=>a!=='--serve-only'&&!/^--port=\d+$/.test(a)))throw Error('Use --serve-only [--port=3196]. Browser actions are performed with Cua.');
const port=Number(args.find(a=>a.startsWith('--port='))?.slice(7)||3196);
if(!Number.isInteger(port)||port<1024||port>65535)throw Error('Invalid local port');
const root=process.cwd(),parent=resolve(root,'..','ib-filter-regression');mkdirSync(parent,{recursive:true});
const temp=mkdtempSync(join(parent,'bundle-'));
const sources=['app/ib/components/AutoFilterForm.tsx','app/ib/components/MultiSelectFilter.tsx'];
const hashes=Object.fromEntries(sources.map(p=>[p,createHash('sha256').update(readFileSync(p)).digest('hex')]));
const code=String.raw`
import React,{useEffect,useState} from 'react';
import {createRoot} from 'react-dom/client';
import AutoFilterForm,{AutoSearchInput} from './app/ib/components/AutoFilterForm';
import MultiSelectFilter from './app/ib/components/MultiSelectFilter';

window.__filterCalls=[];window.__filterErrors=[];window.__filterMounts=0;window.__filterUnmounts=0;
window.__filterCase={status:'not run'};
const notify=()=>window.dispatchEvent(new Event('fixture-report'));
window.__ibFilterRouter={replace(href,options){
 window.__filterCalls.push({number:window.__filterCalls.length+1,at:Math.round(performance.now()),href,options,returnType:'undefined (void)'});notify();
 // No Promise, network request or implicit server-prop commit.
}};
window.addEventListener('error',e=>{window.__filterErrors.push(String(e.message));notify();});
window.addEventListener('unhandledrejection',e=>{window.__filterErrors.push(String(e.reason));notify();});
function Life(){useEffect(()=>{window.__filterMounts++;notify();return()=>{window.__filterUnmounts++;notify();};},[]);return null;}
const categories=Array.from({length:24},(_,i)=>({value:'topic-'+(i+1),label:['Differentiation','Integration','Differential equations','Sequences','Proof','Geometry'][i%6]+' '+(i+1),detail:'Original local fixture option; no student or bank data'}));
function App(){
 const [mounted,setMounted]=useState(true),[generation,setGeneration]=useState(0),[committed,setCommitted]=useState('course=hl'),[tick,setTick]=useState(0);
 useEffect(()=>{const update=()=>setTick(t=>t+1);window.addEventListener('fixture-report',update);const timer=setInterval(update,500);return()=>{clearInterval(timer);window.removeEventListener('fixture-report',update);};},[]);
 const params=new URLSearchParams(committed),values=name=>params.getAll(name);
 const form=document.querySelector('form.fixture-form');
 const snapshot=form?[...new FormData(form)].map(([name,value])=>[name,String(value)]):[];
 function reset(event){event?.preventDefault();setCommitted('course=hl');notify();}
 function commit(){const latest=window.__filterCalls.at(-1);if(latest)setCommitted(new URL(latest.href,location.origin).search.slice(1));}
 function runCase(kind){
  const form=document.querySelector('form.fixture-form'),inputs=[...form?.querySelectorAll('input[name=category]')||[]];
  const base=window.__filterCalls.length,checks=[];
  if(!form||committed!=='course=hl'||form.querySelector('[name=q]').value||inputs.some(i=>i.checked)){window.__filterCase={status:'precondition: remount pristine filters first'};notify();return;}
  const menu=inputs[0].closest('details');menu.open=true;menu.querySelector('summary').focus();
  window.__filterCase={kind,status:'running',baseRequests:base,startedAt:Math.round(performance.now())};notify();
  const click=i=>{inputs[i].focus();inputs[i].click();};
  if(kind==='rapid-three'){click(0);setTimeout(()=>click(1),25);setTimeout(()=>click(2),50);}
  else{click(0);setTimeout(()=>form.querySelector('.fixture-reset a').click(),25);}
  setTimeout(()=>{
   const calls=window.__filterCalls.slice(base),liveForm=document.querySelector('form.fixture-form'),checked=[...liveForm?.querySelectorAll('input[name=category]:checked')||[]].map(i=>i.value);
   if(kind==='rapid-three'){
    const p=new URL(calls.at(-1)?.href||location.href,location.origin).searchParams;
    checks.push({name:'one coalesced void-router call',passed:calls.length===1,actual:calls.length,expected:1},{name:'all three category values retained',passed:JSON.stringify(p.getAll('category'))===JSON.stringify(inputs.slice(0,3).map(i=>i.value)),actual:p.getAll('category')},{name:'pagination removed and course retained',passed:!p.has('page')&&p.get('course')==='hl'},{name:'no scrollbar/padding-induced menu dismissal',passed:menu.open});
   }else checks.push({name:'pending selection timer cancelled',passed:calls.length===0,actual:calls.length,expected:0},{name:'same-source optimistic category cleared',passed:checked.length===0,actual:checked},{name:'same-source search empty',passed:liveForm.querySelector('[name=q]').value===''});
   window.__filterCase={kind,status:checks.every(c=>c.passed)?'passed':'failed',checks};notify();
  },500);
 }
 return <main>
  <header><strong>LOCAL IB FILTER REGRESSION</strong><h1>Actual controls, void router</h1><p>No account, network navigation or RSC simulation. The request log records only calls made by the real AutoFilterForm.</p><p><a href='/native-control' target='_blank'>Open plain native-details control (no JavaScript)</a></p></header>
  <section className='test-controls'><button onClick={()=>setMounted(false)}>Unmount filters</button><button onClick={()=>{setGeneration(g=>g+1);setCommitted('course=hl');setMounted(true);}}>Remount pristine filters</button><button onClick={()=>{window.__filterCalls=[];notify();}}>Clear request log</button><button onClick={commit}>Commit latest query to source props</button><button id='outside-focus'>Outside focus target</button><button onClick={()=>runCase('rapid-three')}>Rapid three topic choices</button><button onClick={()=>runCase('immediate-reset')}>Select then reset immediately</button></section>
  {mounted?<section className='filter-surface'><AutoFilterForm key={generation} action='/ib/question-bank/fixture' className='fixture-form'>
    <Life/><input type='hidden' name='course' value='hl'/><input type='hidden' name='page' value='3'/>
    <label className='fixture-search'>Search questions<AutoSearchInput search={params.get('q')||''}/></label>
    <MultiSelectFilter name='category' label='Study categories' options={categories} selected={values('category')} wide/>
    <MultiSelectFilter name='difficulty' label='Difficulty' options={['easy','medium','hard'].map(value=>({value,label:value}))} selected={values('difficulty')}/>
    <div className='fixture-reset'><a href='/ib/question-bank/fixture?course=hl' onClick={reset}>Reset filters</a><p>Reset intentionally retains the same component and may supply the same original source props.</p></div>
  </AutoFilterForm></section>:<p role='status'>Filters unmounted. Pending timers must not add another request.</p>}
  <section className='report' aria-label='Fixture report'><h2>Live report</h2><p>Heartbeat {tick} · mounts {window.__filterMounts} · unmounts {window.__filterUnmounts} · recorded requests {window.__filterCalls.length}</p><p>Committed source query: {committed}</p><p>Current form controls: {JSON.stringify(snapshot)}</p><p>Focus: {document.activeElement?.tagName} {document.activeElement?.getAttribute('name')||''}</p><h3>Deterministic component case</h3><pre>{JSON.stringify(window.__filterCase,null,2)}</pre><h3>Request log</h3><pre>{JSON.stringify(window.__filterCalls,null,2)}</pre><h3>Browser errors</h3><pre>{JSON.stringify(window.__filterErrors,null,2)}</pre></section>
  <section className='cases'><h2>Cases to inspect</h2><ol><li>Open Study categories, focus its summary, then click non-focusable toolbar text/padding. The renderer and menu should remain alive. Scroll the panel and choose labels/checkboxes.</li><li>Make several selections rapidly. They should coalesce into one call after the 180ms selection delay; every checked value and course=hl must remain, and page=3 must be removed.</li><li>Type search: one call after the 300ms search delay. Selecting a facet during typing must retain the current search and all other checked inputs.</li><li>On pristine empty source props, type or select then immediately Reset. No old timer should fire; optimistic input values should clear even when Reset supplies those same empty source props.</li><li>Select then immediately Unmount. No queued navigation should be recorded after unmount. Remount explicitly starts a new control instance.</li><li>Escape should close the menu and return focus to its summary. An outside pointer/focus should close it after focus settles.</li></ol></section>
 </main>;
}
createRoot(document.getElementById('root')).render(<App/>);`;

await build({stdin:{contents:code,resolveDir:root,sourcefile:'ib-filter-local-fixture.tsx',loader:'tsx'},bundle:true,outfile:join(temp,'app.js'),platform:'browser',format:'iife',define:{'process.env.NODE_ENV':'"production"'},plugins:[{name:'void-recorder',setup(b){b.onResolve({filter:/^next\/navigation$/},()=>({path:'router',namespace:'local'}));b.onLoad({filter:/.*/,namespace:'local'},()=>({contents:'export const useRouter=()=>window.__ibFilterRouter;'}));}}]});
const css=`*{box-sizing:border-box}body{margin:0;background:#fbf8f1;color:#292522;font:15px/1.5 Arial,sans-serif}main{max-width:1160px;margin:auto;padding:24px}header{max-width:900px}h1{margin:6px 0}a{color:#74272d}button{font:inherit;padding:9px 12px;background:white;border:1px solid #bcae99;border-radius:5px;cursor:pointer}.test-controls{display:flex;gap:10px;flex-wrap:wrap;margin:22px 0}.filter-surface{padding:24px;background:#fff;border:1px solid #d6c9b5;border-radius:8px;min-height:220px}.fixture-form{display:grid;grid-template-columns:minmax(220px,2fr) minmax(150px,1fr);gap:24px;align-items:start}.fixture-search,.fixture-reset{grid-column:1/-1}.fixture-search{display:grid;gap:6px}.fixture-search input{font:inherit;padding:12px;border:1px solid #bcae99}.fixture-reset p{font-size:12px;margin:4px 0}.report{margin-top:26px;border:1px solid #d6c9b5;background:#fff;padding:18px}.report p{overflow-wrap:anywhere}.report pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f6f1e6;padding:10px;font-size:12px}.cases li{margin:8px 0}.filterStatus{grid-column:1/-1}@media(max-width:600px){main{padding:14px}.fixture-form{grid-template-columns:1fr}.filter-surface{padding:15px}.test-controls button{font-size:12px}}`+readFileSync(join(temp,'app.css'),'utf8');
const html=`<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Local IB filter regression</title><link rel='stylesheet' href='/app.css'></head><body><div id='root'></div><script src='/app.js'></script></body></html>`;
const native=`<!doctype html><html><head><meta charset='utf-8'><title>Native details control</title><style>body{font:18px Arial;padding:35px}details{width:420px;border:1px solid #777;padding:15px}summary{padding:15px;background:#eee}#gap{padding:30px;background:#fff4d1}.scroll{height:160px;overflow:auto;border:1px solid;padding:15px}.scroll p{height:70px}</style></head><body><h1>Plain HTML control: no JavaScript</h1><p>Focus the summary, then click the non-focusable padding below. Scroll, click checkbox labels and outside. This page contains no focus dismissal handler or React.</p><details id='d' open><summary id='s'>Native control summary</summary><label><input type='checkbox'>Native checkbox</label><div id='gap'>Non-focusable inner padding</div><div class='scroll'>${Array.from({length:12},(_,i)=>`<p><label><input type='checkbox'>Scrollable row ${i+1}</label></p>`).join('')}</div></details><p><button>Outside focus target</button></p></body></html>`;
const nativeOld=native.replace('Plain HTML control: no JavaScript','Diagnostic: original synchronous blur handler').replace('This page contains no focus dismissal handler or React.','This isolated page deliberately contains the old synchronous focusout dismissal. It contains no React, router, authentication or network requests.').replace('</body>',`<script>document.addEventListener('focusout',event=>{const d=document.getElementById('d');if(d.contains(event.target)&&!d.contains(event.relatedTarget))d.open=false;});</script></body>`);
const server=createServer((req,res)=>{res.setHeader('Cache-Control','no-store');if(req.method!=='GET'){res.writeHead(405);return res.end();}const path=new URL(req.url,'http://127.0.0.1').pathname;if(path==='/app.js'){res.setHeader('Content-Type','application/javascript');return res.end(readFileSync(join(temp,'app.js')));}if(path==='/app.css'){res.setHeader('Content-Type','text/css');return res.end(css);}if(path==='/favicon.ico'){res.writeHead(204);return res.end();}res.setHeader('Content-Type','text/html; charset=utf-8');res.end(path==='/native-control'?native:path==='/native-old-handler'?nativeOld:html);});
await new Promise((ok,fail)=>{server.once('error',fail);server.listen(port,'127.0.0.1',ok);});
console.log(JSON.stringify({status:'ready',pid:process.pid,url:`http://127.0.0.1:${port}/`,nativeControl:`http://127.0.0.1:${port}/native-control`,oldHandlerDiagnostic:`http://127.0.0.1:${port}/native-old-handler`,mode:'serve-only; Cua browser actions',sourceHashes:hashes,artifacts:temp}));
for(const signal of ['SIGINT','SIGTERM'])process.on(signal,()=>server.close(()=>process.exit(0)));
