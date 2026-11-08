// Browser acceptance of the actual runner with synthetic accounts, local APIs,
// and intercepted EmailJS. This never sends email or writes production data.
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,mkdirSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {build} from 'esbuild';
import {chromium} from 'playwright';
import {ibHarness} from './ib-component-harness.mjs';
const psychologyFixture=meta=>JSON.parse(readFileSync('content/ib/psychology-mocks-2027/papers/'+meta.id+'.json','utf8'));
const root=process.cwd(),temp=mkdtempSync(join(process.env.TEMP||tmpdir(),'psychology-independent-browser-')),h=ibHarness(),model=h.load('lib/ib/psychology-mock-model.ts'),content=h.load('lib/ib/psychology-mocks.ts');
const papers=new Map(),fixtures={};for(const set of model.PSYCHOLOGY_MOCKS)for(const meta of set.papers){const p=content.validatePsychologyMockPaper(psychologyFixture(meta),meta);papers.set(meta.id,p);fixtures[`${set.id}/${meta.paper}`]={paper:content.psychologyMockPrompt(p,meta),email:'student@example.invalid',accountId:'browser-fixture-account'};}
const code=`import React from 'react';import{createRoot}from'react-dom/client';import Runner from './app/ib/psychology-mocks/PsychologyMockRunner';createRoot(document.getElementById('root')).render(<Runner {...window.__fixture} initialAttempt={new URLSearchParams(location.search).get('attempt')||undefined}/>);`;
await build({stdin:{contents:code,resolveDir:root,sourcefile:'psychology-browser.tsx',loader:'tsx'},bundle:true,outfile:join(temp,'app.js'),platform:'browser',format:'iife',define:{'process.env.NODE_ENV':'"production"'},loader:{'.woff2':'dataurl','.woff':'dataurl','.ttf':'dataurl'},plugins:[{name:'next-fixtures',setup(b){b.onResolve({filter:/^next\/(link|script)$/},a=>({path:a.path,namespace:'mock-next'}));b.onLoad({filter:/.*/,namespace:'mock-next'},a=>({contents:a.path==='next/link'?`import React from'react';export default function Link({children,href,prefetch,...p}){return <a href={href} {...p}>{children}</a>}`:`export default function Script(){return null}`,loader:'jsx',resolveDir:root}));}}]});
const css=readFileSync(join(temp,'app.css'),'utf8')+readFileSync('node_modules/katex/dist/katex.min.css','utf8'),attempts=new Map();let failSubmit=true,submissions=0;
function review(row){const p=papers.get(row.paperId);return {id:row.id,name:row.name,submittedAt:row.submittedAt,elapsed:row.elapsed,answers:row.answers,selfMarks:row.marks,score:model.scoreMock(model.selectedQuestions(p.questions,row.answers.__choice),row.answers,row.marks),solutions:content.psychologyMockSolutions({...p,questions:model.selectedQuestions(p.questions,row.answers.__choice)})};}
const handler=async(req,res)=>{try{const url=new URL(req.url,'http://localhost');
 if(url.pathname==='/app.js'){res.setHeader('Content-Type','application/javascript');return res.end(readFileSync(join(temp,'app.js')));}if(url.pathname==='/app.css'){res.setHeader('Content-Type','text/css');return res.end(css);}if(url.pathname.startsWith('/fonts/')){res.setHeader('Content-Type','font/woff2');return res.end(readFileSync(join(root,'node_modules/katex/dist',url.pathname)));}
 if(url.pathname.startsWith('/api/ib/psychology-mocks/')){res.setHeader('Content-Type','application/json');const mockId=url.pathname.split('/').pop();if(req.method==='GET'){const row=attempts.get(url.searchParams.get('attempt'));if(!row){res.statusCode=404;return res.end(JSON.stringify({error:'Attempt missing'}));}return res.end(JSON.stringify({review:review(row),paper:row.paper}));}
 const chunks=[];for await(const chunk of req)chunks.push(chunk);const b=JSON.parse(Buffer.concat(chunks)),meta=model.getPsychologyPaperMeta(mockId,b.paper),p=papers.get(meta.id);
 if(b.action==='submit'){submissions++;if(failSubmit){failSubmit=false;res.statusCode=503;return res.end(JSON.stringify({error:'Temporary test outage. Your answers remain saved; retry.'}));}if(!attempts.has(b.attemptId))attempts.set(b.attemptId,{id:b.attemptId,name:b.name,mockId,paper:b.paper,paperId:meta.id,answers:model.cleanAnswers(p.questions,b.answers),marks:null,elapsed:b.elapsed,submittedAt:new Date().toISOString()});}else{const row=attempts.get(b.attemptId);row.marks??=model.validateSelfMarks(model.selectedQuestions(p.questions,row.answers.__choice),b.selfMarks);}const row=attempts.get(b.attemptId);return res.end(JSON.stringify({review:review(row),paper:row.paper}));}
 const f=fixtures[url.pathname.replace('/ib/psychology-mocks/','')];if(!f){res.statusCode=404;return res.end('Not found');}res.setHeader('Content-Type','text/html;charset=utf-8');res.end(`<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/app.css"></head><body><div id="root"></div><script>window.__fixture=${JSON.stringify(f).replace(/</g,'\\u003c')};window.__mail=[];window.__mailFail=true;window.emailjs={init(){},async send(service,template,payload){if(window.__mailFail){window.__mailFail=false;throw new Error('Simulated email outage');}window.__mail.push({service,template,payload});}};</script><script src="/app.js"></script></body></html>`);
 }catch(e){res.statusCode=500;res.end(JSON.stringify({error:e.message}));}};
const origin='https://psychology-fixture.invalid';
const browser=await chromium.launch({headless:true,...(process.env.IB_BROWSER_EXECUTABLE?{executablePath:process.env.IB_BROWSER_EXECUTABLE,args:['--no-sandbox','--disable-gpu','--disable-software-rasterizer','--disable-dev-shm-usage','--no-zygote','--single-process']}:{})});
const out=resolve(process.env.PSYCHOLOGY_SCREENSHOTS||'artifacts/psychology-browser');mkdirSync(out,{recursive:true});
try{const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.route('https://**/*',r=>r.abort());await page.route(origin+'/**',async route=>{const req=route.request(),headers={};let body='',status=200;await handler({url:req.url(),method:req.method(),async *[Symbol.asyncIterator](){if(req.postData())yield Buffer.from(req.postData());}},{setHeader(k,v){headers[k]=v;},get statusCode(){return status;},set statusCode(v){status=v;},end(v=''){body=v;}});await route.fulfill({status,headers,body});});page.on('dialog',d=>d.accept());

 await page.goto(origin+'/ib/psychology-mocks/psychology-sl-challenge-a/1');
 await page.getByLabel('Your name').fill('Psychology Student');
 await page.getByLabel('Selected essay').selectOption('psy-sl-a-1-06');
 await page.getByRole('button',{name:'Start timed paper'}).click();
 await page.getByRole('button',{name:'Paper 1 question 6',exact:true}).click();await page.locator('textarea').fill('Symptom ratings depend on how the construct is operationalised.');
 await page.getByRole('button',{name:'Flag question',exact:true}).click();
 await page.reload();await page.locator('textarea').first().waitFor();
 assert.match(await page.locator('textarea').first().inputValue(),/operationalised/);
 await page.getByText('Section C · Choose one of 2 essays',{exact:true}).click();
 await page.getByLabel('Selected essay').selectOption('psy-sl-a-1-05');
 await page.getByRole('button',{name:'Paper 1 question 5',exact:true}).click();assert.equal(await page.locator('textarea').inputValue(),'');
 await page.getByLabel('Selected essay').selectOption('psy-sl-a-1-06');
 await page.getByRole('button',{name:/Paper 1 question 6/}).click();
 assert.match(await page.locator('textarea').first().inputValue(),/operationalised/);
 await page.getByRole('button',{name:'Submit paper',exact:true}).click();
 await page.getByRole('button',{name:'Submit and review'}).click();
 await page.getByRole('button',{name:'Retry submission'}).waitFor();
 assert.equal(attempts.size,0);assert.equal(await page.getByRole('link',{name:'Open the solutions PDF'}).count(),0);
 await page.getByRole('button',{name:'Retry submission'}).click();
 await page.getByRole('button',{name:'Retry completion report'}).click();
 await page.getByRole('button',{name:'Completion email accepted'}).waitFor();
 assert.equal([...attempts.values()][0].answers.__choice,'psy-sl-a-1-06');
 assert.equal(await page.locator('select').count(),5);
 for(const select of await page.locator('select').all())await select.selectOption({index:(await select.locator('option').count())-1},{force:true});
 await page.getByRole('button',{name:'Save marks and email scored report'}).click();
 await page.getByRole('button',{name:'Scored email accepted'}).waitFor();
 const messages=await page.evaluate(()=>window.__mail);assert.equal(messages.length,2);
 assert.match(messages[1].payload.score,/35 \/ 35/);
 assert.equal(messages[1].payload.solution_link,origin+'/ib-psychology-mocks/psychology-sl-set-a-paper-1-solutions.pdf');
 await page.reload();await page.getByRole('button',{name:'Scored email accepted'}).waitFor();
 assert.equal(await page.evaluate(()=>window.__mail.length),0);
 await page.setViewportSize({width:390,height:844});await page.goto(origin+'/ib/psychology-mocks/psychology-hl-challenge-b/2');

 await page.getByRole('button',{name:'Start timed paper'}).click();await page.locator('textarea').first().waitFor();
 await page.getByRole('button',{name:'Paper 2 question 5',exact:true}).click();assert(await page.locator('textarea').isVisible());assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
 await page.screenshot({path:join(out,'mobile-data.png')});
 await page.goto(origin+'/ib/psychology-mocks/psychology-hl-challenge-b/3');
 await page.getByRole('button',{name:'Start timed paper'}).click();
 assert.equal(await page.getByLabel('Selected essay').count(),0);
 await page.getByRole('button',{name:'Paper 3 question 2',exact:true}).click();
 await page.getByText('Paper 3 resource booklet · Sources 2–5',{exact:true}).click();assert.equal(await page.locator('table:visible').count(),2);await page.getByRole('heading',{name:/Source 5/}).waitFor();const chart=page.getByRole('img',{name:/Perceived responsiveness by conversation condition/});await chart.scrollIntoViewIfNeeded();await chart.waitFor({state:'visible'});await chart.evaluate(el=>el.decode());assert((await chart.boundingBox()).width>160);await page.screenshot({path:join(out,'hl-resources.png')});await page.locator('textarea').fill('The unit of random allocation was the pair.');
 const key='ts:ib-psychology:v2:browser-fixture-account:psychology-hl-set-b-paper-3';
 await page.evaluate(key=>{const d=JSON.parse(localStorage.getItem(key));d.startedAt=Date.now()-6301000;d.deadline=d.startedAt+6300000;localStorage.setItem(key,JSON.stringify(d));},key);
 await page.reload();await page.getByRole('heading',{name:'Your paper is submitted'}).waitFor();
 assert.equal([...attempts.values()].at(-1).elapsed,6300);assert.equal(await page.locator('select').count(),4);
 assert.deepEqual(errors,[]);console.log('Passed desktop and mobile: selection, tables, retained drafts, submission retry, EmailJS completion and scored reports, no repeated email on refresh, HL Paper 3 timer and all four required responses.');
}finally{await browser.close();}
