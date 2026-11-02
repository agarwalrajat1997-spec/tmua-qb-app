// Isolated browser acceptance test of the real React runner. Synthetic account,
// local API fixtures and intercepted EmailJS; never contacts students or production.
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {mkdtempSync,readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {build} from 'esbuild';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {chromium} from 'playwright';
import {ibHarness} from './ib-component-harness.mjs';
const root=process.cwd(), temp=mkdtempSync(join(tmpdir(),'ib-physics-browser-'));
const harness=ibHarness(), model=harness.load('lib/ib/physics-mock-model.ts'), content=harness.load('lib/ib/physics-mocks.ts');
const Question=harness.load('app/ib/components/QuestionBody.tsx').default;
const fixtures={};
for(const id of ['physics-sl-mock-01','physics-hl-mock-01'])for(const paper of ['1','2']){
  const mock=content.getPhysicsMock(id),items=content.getMockItems(id,paper);
  fixtures[`${id}/${paper}`]={mock,paper,email:'student@example.invalid',accountId:'browser-fixture-account',items:items.map(({question:q,section,number})=>({id:q.id,section,number,marks:q.marks,parts:q.parts,type:q.questionType})),html:items.map(({question:q,number})=>{
    let html=renderToStaticMarkup(React.createElement(Question,{question:{...harness.model.questionPrompt(q),number}}));
    // Static RSC slots do not hydrate client image handlers in this isolated harness.
    // Use the identical bundled SVG fallback; live fallback handlers have their own portal tests.
    if(q.diagramSvg)html=html.replace(/(<img[^>]*src=")[^"]+/,`$1data:image/svg+xml;base64,${Buffer.from(q.diagramSvg).toString('base64')}`);
    return html;
  })};
}
const code=`import React from 'react';import{createRoot}from'react-dom/client';import Runner from './app/ib/mocks/PhysicsMockRunner';
const f=window.__fixture;createRoot(document.getElementById('root')).render(<Runner {...f} initialAttempt={new URLSearchParams(location.search).get('attempt')||undefined} bodies={f.html.map((h,i)=><div key={i} dangerouslySetInnerHTML={{__html:h}}/>)} />);`;
await build({stdin:{contents:code,resolveDir:root,sourcefile:'ib-browser-fixture.tsx',loader:'tsx'},bundle:true,outfile:join(temp,'app.js'),platform:'browser',format:'iife',define:{'process.env.NODE_ENV':'"production"'},loader:{'.woff2':'dataurl','.woff':'dataurl','.ttf':'dataurl'},plugins:[{name:'next-fixtures',setup(b){b.onResolve({filter:/^next\/(link|script)$/},args=>({path:args.path,namespace:'mock-next'}));b.onLoad({filter:/.*/,namespace:'mock-next'},args=>({contents:args.path==='next/link'?`import React from'react';export default function Link({children,href,prefetch,...p}){return <a href={href} {...p}>{children}</a>}`:`export default function Script(){return null}`,loader:'jsx',resolveDir:root}));}}]});
const css=readFileSync(join(temp,'app.css'),'utf8')+readFileSync('app/ib/questions.module.css','utf8').replace(/:global\(([^)]+)\)/g,'$1')+readFileSync('node_modules/katex/dist/katex.min.css','utf8');
const attempts=new Map();let failSubmit=true;let submissions=0;
function review(row){const items=content.getMockItems(row.mockId,row.paper);return {id:row.id,submittedAt:row.submittedAt,elapsed:row.elapsed,answers:row.answers,selfMarks:row.marks,score:model.scoreMock(items,row.answers,row.marks),solutions:items.map(({question:q,section,number})=>({id:q.id,label:`${section} Q${number}`,parts:q.parts,markScheme:q.markScheme,correctOption:q.correctOption,diagram:q.markSchemeDiagramSvg?`data:image/svg+xml;base64,${Buffer.from(q.markSchemeDiagramSvg).toString('base64')}`:undefined}))};}
const server=createServer(async(req,res)=>{
  try{
    const url=new URL(req.url,'http://localhost');
    if(url.pathname==='/app.js'){res.setHeader('Content-Type','application/javascript');return res.end(readFileSync(join(temp,'app.js')));}
    if(url.pathname==='/app.css'){res.setHeader('Content-Type','text/css');return res.end(css);}
    if(url.pathname.startsWith('/fonts/')){res.setHeader('Content-Type','font/woff2');return res.end(readFileSync(join(root,'node_modules/katex/dist',url.pathname)));}
    if(url.pathname.startsWith('/api/ib/mocks/')){
      res.setHeader('Content-Type','application/json');const mockId=url.pathname.split('/').pop();
      if(req.method==='GET'){const row=attempts.get(url.searchParams.get('attempt'));if(!row){res.statusCode=404;return res.end(JSON.stringify({error:'Attempt missing'}));}return res.end(JSON.stringify({review:review(row),paper:row.paper}));}
      const chunks=[];for await(const chunk of req)chunks.push(chunk);const body=JSON.parse(Buffer.concat(chunks));
      if(body.action==='submit'){
        submissions++;
        if(failSubmit){failSubmit=false;res.statusCode=503;return res.end(JSON.stringify({error:'Temporary test outage. Your answers are kept; retry.'}));}
        if(!attempts.has(body.attemptId))attempts.set(body.attemptId,{id:body.attemptId,mockId,paper:body.paper,answers:model.cleanAnswers(content.getMockItems(mockId,body.paper),body.answers),marks:null,elapsed:body.elapsed,submittedAt:new Date().toISOString()});
      }else{const row=attempts.get(body.attemptId);row.marks=model.validateSelfMarks(content.getMockItems(mockId,row.paper),body.selfMarks);}
      return res.end(JSON.stringify({review:review(attempts.get(body.attemptId))}));
    }
    const key=url.pathname.replace('/ib/mocks/','');const fixture=fixtures[key];
    if(!fixture){res.statusCode=404;return res.end('Not found');}
    res.setHeader('Content-Type','text/html; charset=utf-8');res.end(`<!doctype html><html><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><link rel="stylesheet" href="/app.css"/></head><body><div id="root"></div><script>window.__fixture=${JSON.stringify(fixture).replace(/</g,'\\u003c')};window.__mail=[];window.__mailFail=true;window.emailjs={init(){},async send(service,template,payload){if(window.__mailFail){window.__mailFail=false;throw new Error('Simulated email outage');}window.__mail.push({service,template,payload});}};</script><script src="/app.js"></script></body></html>`);
  }catch(e){res.statusCode=500;res.end(JSON.stringify({error:e.message}));}
});
await new Promise(done=>server.listen(0,'127.0.0.1',done));const origin=`http://127.0.0.1:${server.address().port}`;
const args=process.env.IB_BROWSER_EXECUTABLE?['--no-sandbox','--disable-gpu','--disable-software-rasterizer','--disable-dev-shm-usage','--no-zygote','--single-process']:[];
const browser=await chromium.launch({headless:true,...(process.env.IB_BROWSER_EXECUTABLE?{executablePath:process.env.IB_BROWSER_EXECUTABLE,args}:{})});
const out=resolve('docs/ib-physics-mocks/screenshots');mkdirSync(out,{recursive:true});
try{
  const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.route('https://**/*',route=>route.abort()); // no external services in this test
  page.on('dialog',dialog=>dialog.accept());
  await page.goto(`${origin}/ib/mocks/physics-sl-mock-01/1`);
  await page.getByRole('button',{name:'Start timed paper'}).waitFor();await page.screenshot({path:join(out,'sl-instructions.png'),fullPage:true});
  await page.getByLabel('Your name').fill('Browser Test');await page.getByRole('button',{name:'Start timed paper'}).click();
  await page.getByLabel('A',{exact:true}).check();await page.getByRole('button',{name:'Flag question',exact:true}).click();
  await page.getByRole('button',{name:'Paper 1B question 1',exact:true}).click();await page.locator('textarea').first().fill('Worked on paper: a = 9.81 m s^-2.');
  const before=await page.getByRole('timer').innerText();await page.reload();await page.locator('textarea').first().waitFor();assert.equal(await page.locator('textarea').first().inputValue(),'Worked on paper: a = 9.81 m s^-2.');
  assert(await page.getByRole('button',{name:/Paper 1A question 1, answered, flagged/}).count());
  assert(await page.locator('img').evaluateAll(images=>images.every(img=>img.complete&&img.naturalWidth>0)));await page.screenshot({path:join(out,'sl-data-question.png'),fullPage:true});
  await page.getByRole('button',{name:'Submit paper',exact:true}).click();await page.getByRole('button',{name:'Submit and review'}).click();
  await page.getByRole('button',{name:'Retry submission'}).waitFor();assert.equal(attempts.size,0);
  await page.getByRole('button',{name:'Retry submission'}).click();await page.getByRole('heading',{name:'Mark your written responses'}).waitFor();assert.equal(attempts.size,1);assert.equal(submissions,2);
  for(const select of await page.locator('select').all())await select.selectOption({index:(await select.locator('option').count())-1});
  await page.getByRole('button',{name:'Save marks and email report'}).click();await page.getByRole('button',{name:'Retry email report'}).waitFor();
  await page.getByRole('button',{name:'Retry email report'}).click();await page.getByRole('button',{name:'Report accepted by email service'}).waitFor();
  const sent=await page.evaluate(()=>window.__mail);assert.equal(sent.length,1);assert.equal(sent[0].service,'service_5l4w8x2');assert.equal(sent[0].template,'template_j1jrs4o');assert.equal(sent[0].payload.to_email,'student@example.invalid');assert.match(sent[0].payload.paper1,/self-assessed/);
  await page.screenshot({path:join(out,'sl-report.png'),fullPage:false});
  await page.reload();await page.getByRole('button',{name:'Report accepted by email service'}).waitFor();assert.equal(await page.evaluate(()=>window.__mail.length),0,'Reload must not resend mail');
  // New sitting on mobile, then expire the real wall-clock timer.
  await page.setViewportSize({width:390,height:844});await page.goto(`${origin}/ib/mocks/physics-hl-mock-01/2`);await page.getByRole('button',{name:'Start timed paper'}).click();
  await page.screenshot({path:join(out,'hl-mobile.png'),fullPage:true});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1));
  const key='ts:ib-physics:v1:browser-fixture-account:physics-hl-mock-01:2';
  await page.evaluate(key=>{const d=JSON.parse(localStorage.getItem(key));d.deadline=Date.now()-1000;localStorage.setItem(key,JSON.stringify(d));},key);
  await page.reload();await page.getByRole('heading',{name:'Mark your written responses'}).waitFor();assert.equal([...attempts.values()].at(-1).elapsed,9000);
  assert.deepEqual(errors,[]);
  console.log(JSON.stringify({status:'passed',checks:['Real React runner','Desktop and mobile layout','MCQ and written input','Flags and draft recovery','Failed submission retry','Written rubric validation','EmailJS failure and retry','No resend on reload','Expired timer auto-submit','No browser errors'],mail:'Intercepted fixture only; no email sent',screenshots:out}));
}finally{await browser.close();await new Promise(done=>server.close(done));}
