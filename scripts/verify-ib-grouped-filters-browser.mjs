// Real filter controls + server-rendered bank, served with a synthetic account.
// The local fixture replaces authentication only; no live sessions or external writes.
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { mkdtempSync, readFileSync, readdirSync, mkdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { build } from 'esbuild';
import { renderToStaticMarkup } from 'react-dom/server';
import { chromium } from 'playwright';
import { ibHarness } from './ib-component-harness.mjs';
const root=process.cwd(),temp=mkdtempSync(join(tmpdir(),'ib-filter-browser-'));
const seed=ibHarness(),catalog=seed.load('lib/ib/catalog.ts');
const questions=Object.keys(catalog.IB_COURSES).flatMap(subject=>readdirSync('content/ib/'+subject).filter(f=>f.endsWith('.json')).flatMap(f=>JSON.parse(readFileSync(`content/ib/${subject}/${f}`,'utf8'))));
const h=ibHarness({questions}),bank=h.load('app/ib/question-bank/[collection]/page.tsx').default;
// Mount the exact client component into its server-rendered form slots. GET
// submission and navigation run through the real server component on each load.
const code=`import React from'react';import{createRoot}from'react-dom/client';import MultiSelectFilter from './app/ib/components/MultiSelectFilter';
for(const field of document.querySelectorAll('.field')){
 const inputs=[...field.querySelectorAll('input[type=checkbox]')];if(!inputs.length)continue;
 const options=inputs.map(input=>{const span=input.parentElement.querySelector('span');return {value:input.value,label:span.firstChild.textContent,detail:span.querySelector('small')?.textContent}});
 const props={name:inputs[0].name,label:field.querySelector(':scope>span').textContent,options,selected:inputs.filter(input=>input.checked).map(input=>input.value),wide:field.classList.contains('wide'),allLabel:field.querySelector('summary>span').textContent.includes('selected')?'All':field.querySelector('summary>span').textContent};
 const mount=document.createElement('div');mount.style.display='contents';field.replaceWith(mount);createRoot(mount).render(<MultiSelectFilter {...props}/>);
}
window.__ready=true;`;
await build({stdin:{contents:code,resolveDir:root,sourcefile:'ib-filter-fixture.tsx',loader:'tsx'},bundle:true,outfile:join(temp,'app.js'),platform:'browser',format:'iife',define:{'process.env.NODE_ENV':'"production"'}});
const css=`*{box-sizing:border-box}body{margin:8px;background:#fbf8f1;color:#292522;font-family:Arial,sans-serif}a{color:inherit;text-decoration:none}button,input{font:inherit}button{cursor:pointer;border:0}p,h1,h2,h3{margin:0}`+
 ['app/ib/ib.module.css','app/ib/questions.module.css'].map(path=>readFileSync(path,'utf8').replace(/:global\(([^)]+)\)/g,'$1')).join('\n')+readFileSync(join(temp,'app.css'),'utf8')+readFileSync('node_modules/katex/dist/katex.min.css','utf8');
const server=createServer(async(req,res)=>{
 try{
  const url=new URL(req.url,'http://localhost');
  if(url.pathname==='/app.js'){res.setHeader('Content-Type','application/javascript');return res.end(readFileSync(join(temp,'app.js')));}
  if(url.pathname.startsWith('/fonts/')){res.setHeader('Content-Type','font/woff2');return res.end(readFileSync(join(root,'node_modules/katex/dist',url.pathname)));}
  if(url.pathname==='/app.css'){res.setHeader('Content-Type','text/css');return res.end(css);}
  if(!url.pathname.startsWith('/ib/question-bank/')){res.statusCode=404;return res.end('Fixture route missing');}
  const query=Object.fromEntries([...new Set(url.searchParams.keys())].map(key=>[key,url.searchParams.getAll(key).length>1?url.searchParams.getAll(key):url.searchParams.get(key)]));
  const page=await bank({params:Promise.resolve({collection:url.pathname.split('/').pop()}),searchParams:Promise.resolve(query)});
  let html=renderToStaticMarkup(page);
  // Avoid external image requests in this control/navigation fixture.
  html=html.replace(/<img\b[^>]*>/g,'');
  res.setHeader('Content-Type','text/html; charset=utf-8');res.end(`<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/app.css"></head><body>${html}<script src="/app.js"></script></body></html>`);
 }catch(error){res.statusCode=500;res.end(String(error.stack));}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const origin=`http://127.0.0.1:${server.address().port}`;
const browser=await chromium.launch({headless:true,...(process.env.IB_BROWSER_EXECUTABLE?{executablePath:process.env.IB_BROWSER_EXECUTABLE,args:['--no-sandbox','--disable-gpu','--disable-software-rasterizer','--disable-dev-shm-usage','--no-zygote','--single-process']}:{})});
const screenshots=resolve(process.env.IB_FILTER_SCREENSHOTS||'/tmp/ib-filter-screenshots');mkdirSync(screenshots,{recursive:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(origin+'/ib/question-bank/physics-space-time-motion');
 await page.waitForFunction(()=>window.__ready);
 await page.getByText('Study categories',{exact:true}).locator('..').locator('summary').click();
 await page.getByRole('checkbox',{name:/Motion and relativity/}).check();await page.getByRole('checkbox',{name:/Forces, momentum and rotation/}).check();
 await page.keyboard.press('Escape');
 await page.getByText('Difficulty',{exact:true}).locator('..').locator('summary').click();await page.getByRole('checkbox',{name:'Easy',exact:true}).check();await page.getByRole('checkbox',{name:'Hard',exact:true}).check();await page.keyboard.press('Escape');
 await page.getByText('Question type',{exact:true}).locator('..').locator('summary').click();await page.getByRole('checkbox',{name:'Multiple choice',exact:true}).check();await page.getByRole('checkbox',{name:'Structured',exact:true}).check();await page.keyboard.press('Escape');
 await Promise.all([page.waitForURL(url=>url.searchParams.getAll('category').length===2),page.getByRole('button',{name:'Apply filters'}).click()]);
 await page.waitForFunction(()=>window.__ready);
 let url=new URL(page.url());assert.deepEqual(url.searchParams.getAll('difficulty'),['easy','hard']);assert.deepEqual(url.searchParams.getAll('type'),['multiple-choice','structured']);
 assert.equal(await page.locator('input[name=category]:checked').count(),2);assert.equal(await page.locator('article.questionCard').count(),8);
 await page.screenshot({path:join(screenshots,'physics-desktop.png'),fullPage:false});
 await Promise.all([page.waitForURL(url=>url.searchParams.get('page')==='2'),page.getByRole('link',{name:'Next →',exact:true}).click()]);
 url=new URL(page.url());assert.equal(url.searchParams.getAll('category').length,2);assert.equal(url.searchParams.getAll('difficulty').length,2);assert.equal(url.searchParams.getAll('type').length,2);
 await Promise.all([page.waitForURL(url=>url.search===''),page.getByRole('link',{name:'Reset',exact:true}).click()]);
 assert.equal(await page.locator('input[type=checkbox]:checked').count(),0);
 await page.setViewportSize({width:390,height:844});await page.goto(origin+'/ib/question-bank/geometry-trigonometry');await page.waitForFunction(()=>window.__ready);
 const summary=page.getByText('Study categories',{exact:true}).locator('..').locator('summary');await summary.focus();await page.keyboard.press('Enter');
 const box=page.getByRole('checkbox',{name:/Algebraic trigonometric equations/});await box.focus();await page.keyboard.press('Space');assert.equal(await box.isChecked(),true);
 await page.screenshot({path:join(screenshots,'maths-mobile.png'),fullPage:false});
 const overflow=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,offenders:[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>innerWidth+1).slice(0,12).map(e=>({tag:e.tagName,classes:e.className,width:e.getBoundingClientRect().width,right:e.getBoundingClientRect().right}))}));if(overflow.scroll>overflow.width+1)console.log(JSON.stringify(overflow));assert.ok(overflow.scroll<=overflow.width+1,'mobile dropdown fits viewport');
 await page.keyboard.press('Escape');assert.equal(await summary.evaluate(el=>el.parentElement.open),false,'Escape closes dropdown');assert.equal(await summary.evaluate(el=>document.activeElement===el),true,'Escape returns focus');
 await summary.click();await page.getByRole('button',{name:'Clear',exact:true}).click();assert.equal(await box.isChecked(),false,'Clear is scoped to open facet');
 await page.keyboard.press('Escape');
 await Promise.all([page.waitForURL(url=>url.searchParams.has('q')),page.getByRole('button',{name:'Apply filters'}).click()]);assert.equal(new URL(page.url()).searchParams.has('category'),false,'clearing submits all categories');
 assert.deepEqual(errors,[],'no browser errors');
 console.log(JSON.stringify({status:'passed',checks:['real checkbox component','GET form repeated parameters','server filtering','pagination','reset','mobile overflow','keyboard selection','Escape and focus','facet clear','no browser errors'],screenshots,account:'synthetic only'}));
}finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
