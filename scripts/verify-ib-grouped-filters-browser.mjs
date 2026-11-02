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
// Real filter components, with a small async router adapter in place of Next's
// RSC transport. Requests execute the real server page. The form stays mounted;
// delayed/out-of-order responses test optimistic selections without a reload.
const code=`import React,{useEffect}from'react';import{createRoot}from'react-dom/client';
import MultiSelectFilter from './app/ib/components/MultiSelectFilter';
import AutoFilterForm,{AutoSearchInput}from './app/ib/components/AutoFilterForm';
let version=0;window.__requests=[];window.__boot=Math.random();
const original=document.querySelector('form.filters'),mount=document.createElement('div');mount.style.display='contents';original.replaceWith(mount);const root=createRoot(mount);
function App({form}){
 useEffect(()=>{window.__ready=true});
 const fields=[...form.querySelectorAll('.field')].map(field=>{
  const inputs=[...field.querySelectorAll('input[type=checkbox]')];
  return {name:inputs[0].name,label:field.querySelector(':scope>span').textContent,options:inputs.map(input=>{const span=input.parentElement.querySelector('span');return{value:input.value,label:span.firstChild.textContent,detail:span.querySelector('small')?.textContent}}),selected:inputs.filter(i=>i.checked).map(i=>i.value),wide:field.classList.contains('wide')};
 });
 const course=form.querySelector('[name=course]')?.value;
 return <AutoFilterForm key={form.getAttribute('action')+course} action={form.getAttribute('action')} className='filters physicsFilters'>
  {course?<input type='hidden' name='course' value={course}/>:null}
  <label className='searchFilter'>Search questions<AutoSearchInput search={form.querySelector('[name=q]').value}/></label>
  {fields.map(props=><MultiSelectFilter key={props.name} {...props}/>)}
  <div className='filterActions'><a href={form.querySelector('a').getAttribute('href')}>Reset</a></div>
 </AutoFilterForm>;
}
async function navigate(href,mode,options){
 const current=++version;window.__requests.push({href,mode,options});
 const response=await fetch(href,{headers:{'X-Fixture-Navigation':'1'}});if(!response.ok)throw Error(await response.text());
 const html=await response.text();if(current!==version)return;
 const doc=new DOMParser().parseFromString(html,'text/html'),form=doc.querySelector('form.filters');
 // Refresh only server-rendered results/headers, leaving inputs/focus intact.
 while(mount.nextSibling)mount.nextSibling.remove();
 while(form.nextSibling)mount.parentElement.append(form.nextSibling);
 for(const selector of ['.chemistryCourse','.mathsCourse','.bankHeading','.themeNav','.breadcrumb','.filterHint']){
  const old=document.querySelector(selector),next=doc.querySelector(selector);if(old&&next)old.replaceWith(next);
 }
 root.render(<App form={form}/>);
 if(mode==='replace')history.replaceState(null,'',href);else if(mode==='push')history.pushState(null,'',href);
 window.__settled=href;
}
window.__router={replace:(href,options)=>navigate(href,'replace',options)};
document.addEventListener('click',event=>{const link=event.target.closest('a');if(!link||link.target||!link.getAttribute('href')?.startsWith('/ib/question-bank/'))return;event.preventDefault();navigate(link.getAttribute('href'),'push');});
window.addEventListener('popstate',()=>navigate(location.pathname+location.search,'pop'));
root.render(<App form={original}/>);`;
await build({stdin:{contents:code,resolveDir:root,sourcefile:'ib-filter-fixture.tsx',loader:'tsx'},bundle:true,outfile:join(temp,'app.js'),platform:'browser',format:'iife',define:{'process.env.NODE_ENV':'"production"'},plugins:[{name:'fixture-router',setup(b){b.onResolve({filter:/^next\/navigation$/},()=>({path:'router',namespace:'fixture'}));b.onLoad({filter:/.*/,namespace:'fixture'},()=>({contents:'export const useRouter=()=>window.__router;'}));}}]});
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
  if(req.headers['x-fixture-navigation'])await new Promise(resolve=>setTimeout(resolve,url.searchParams.getAll('category').length===1?450:120));
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
 const boot=await page.evaluate(()=>window.__boot);
 assert.equal(await page.getByRole('button',{name:'Apply filters'}).count(),0);
 await page.getByText('Study categories',{exact:true}).locator('..').locator('summary').click();
 await page.getByRole('checkbox',{name:/Motion and relativity/}).check();await page.getByRole('checkbox',{name:/Forces, momentum and rotation/}).check();
 await page.waitForFunction(()=>document.querySelector('form').getAttribute('aria-busy')==='false');
 assert.equal(await page.getByRole('checkbox',{name:/Motion and relativity/}).isChecked(),true,'menu stays open after automatic results');
 await page.keyboard.press('Escape');
 await page.getByText('Difficulty',{exact:true}).locator('..').locator('summary').click();await page.getByRole('checkbox',{name:'Easy',exact:true}).check();await page.getByRole('checkbox',{name:'Hard',exact:true}).check();await page.keyboard.press('Escape');
 await page.getByText('Question type',{exact:true}).locator('..').locator('summary').click();await page.getByRole('checkbox',{name:'Multiple choice',exact:true}).check();await page.getByRole('checkbox',{name:'Structured',exact:true}).check();await page.keyboard.press('Escape');
 await page.waitForURL(url=>url.searchParams.getAll('category').length===2&&url.searchParams.getAll('type').length===2);
 await page.waitForFunction(()=>document.querySelector('form').getAttribute('aria-busy')==='false');
 assert.equal(await page.evaluate(()=>window.__boot),boot,'filters do not reload the document');
 let url=new URL(page.url());assert.deepEqual(url.searchParams.getAll('difficulty'),['easy','hard']);assert.deepEqual(url.searchParams.getAll('type'),['multiple-choice','structured']);
 assert.equal(await page.locator('input[name=category]:checked').count(),2);assert.equal(await page.locator('article.questionCard').count(),8);
 await page.screenshot({path:join(screenshots,'physics-desktop.png'),fullPage:false});
 await Promise.all([page.waitForURL(url=>url.searchParams.get('page')==='2'),page.getByRole('link',{name:'Next →',exact:true}).click()]);
 url=new URL(page.url());assert.equal(url.searchParams.getAll('category').length,2);assert.equal(url.searchParams.getAll('difficulty').length,2);assert.equal(url.searchParams.getAll('type').length,2);
 // Search debounces and resets pagination, including an empty result.
 const search=page.getByRole('searchbox');
 const requestsBeforeSearch=await page.evaluate(()=>window.__requests.length);
 await search.pressSequentially('no-such-question-unique',{delay:20});
 await page.waitForURL(url=>url.searchParams.get('q')==='no-such-question-unique'&&!url.searchParams.has('page'));
 await page.getByRole('heading',{name:'No questions match these filters.'}).waitFor();
 assert.equal(await search.inputValue(),'no-such-question-unique');
 assert.equal(await page.evaluate(()=>window.__requests.length),requestsBeforeSearch+1,'typing is debounced to one request');
 await Promise.all([page.waitForURL(url=>url.search===''),page.getByRole('link',{name:'Reset',exact:true}).click()]);
 await page.waitForFunction(()=>document.querySelectorAll('input[type=checkbox]:checked').length===0);
 assert.equal(await page.getByRole('searchbox').inputValue(),'');
 assert.equal(await page.evaluate(()=>window.__boot),boot,'pagination/search/reset stay in the current document');
 const options=await page.evaluate(()=>window.__requests.filter(r=>r.mode==='replace').map(r=>r.options));assert.ok(options.every(o=>o.scroll===false));
 // Back/forward restores URL-derived controls.
 await page.goBack();await page.waitForFunction(()=>document.querySelector('[name=q]').value==='no-such-question-unique');
 await page.goForward();await page.waitForFunction(()=>document.querySelector('[name=q]').value==='');
 await page.setViewportSize({width:390,height:844});await page.goto(origin+'/ib/question-bank/geometry-trigonometry');await page.waitForFunction(()=>window.__ready);
 const summary=page.getByText('Study categories',{exact:true}).locator('..').locator('summary');await summary.focus();await page.keyboard.press('Enter');
 const box=page.getByRole('checkbox',{name:/Algebraic trigonometric equations/});await box.focus();await page.keyboard.press('Space');assert.equal(await box.isChecked(),true);
 await page.screenshot({path:join(screenshots,'maths-mobile.png'),fullPage:false});
 const overflow=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,offenders:[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>innerWidth+1).slice(0,12).map(e=>({tag:e.tagName,classes:e.className,width:e.getBoundingClientRect().width,right:e.getBoundingClientRect().right}))}));if(overflow.scroll>overflow.width+1)console.log(JSON.stringify(overflow));assert.ok(overflow.scroll<=overflow.width+1,'mobile dropdown fits viewport');
 await page.keyboard.press('Escape');assert.equal(await summary.evaluate(el=>el.parentElement.open),false,'Escape closes dropdown');assert.equal(await summary.evaluate(el=>document.activeElement===el),true,'Escape returns focus');
 await summary.click();await page.getByRole('button',{name:'Clear',exact:true}).click();assert.equal(await box.isChecked(),false,'Clear is scoped to open facet');
 await page.keyboard.press('Escape');
 await page.waitForURL(url=>!url.searchParams.has('category'));
 await page.waitForFunction(()=>document.querySelector('form').getAttribute('aria-busy')==='false');
 assert.equal(await page.locator('input[name=category]:checked').count(),0,'cleared facet remains empty after responses');
 assert.deepEqual(errors,[],'no browser errors');
 console.log(JSON.stringify({status:'passed',checks:['real checkbox component','instant multi-select repeated parameters','rapid out-of-order responses','no Apply button','no document reload','debounced search','page reset','Back/forward','server filtering','pagination','reset','mobile overflow','keyboard selection','Escape and focus','facet clear','no browser errors'],screenshots,account:'synthetic only'}));
}finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
