// Actual components, synthetic local user fixtures, static review files only.
// This helper launches no browser and adds no application route or auth bypass.
import {readFileSync,readdirSync,mkdirSync,writeFileSync,cpSync} from 'node:fs';
import {resolve} from 'node:path';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {ibHarness} from './ib-component-harness.mjs';
const output=resolve(process.argv[2]||'../biology-review');
mkdirSync(output,{recursive:true});
cpSync('node_modules/katex/dist',resolve(output,'katex'),{recursive:true});
const questions=readdirSync('content/ib/biology').filter(f=>f.endsWith('.json'))
 .flatMap(f=>JSON.parse(readFileSync('content/ib/biology/'+f,'utf8')));
const css=['app/ib/ib.module.css','app/ib/questions.module.css']
 .map(f=>readFileSync(f,'utf8').replace(/:global\(([^)]+)\)/g,'$1')).join('\n');
const pages=[];
function save(name,element){
 writeFileSync(resolve(output,name+'.html'),`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Biology portal visual review</title><link rel="stylesheet" href="/katex/katex.min.css"><style>${css}</style></head><body>${renderToStaticMarkup(element)}</body></html>`);
 pages.push(name+'.html');
}
for(const course of ['sl','hl']){
 const h=ibHarness({questions,useContentModule:true,query:'subject=biology&course='+course});
 const content=h.load('lib/ib/content.ts');
 save('overview-'+course,React.createElement(h.load('app/ib/IBPortalClient.tsx').default,{email:'visual-review@example.invalid',summary:content.getIbSummary(course)}));
 const bank=h.load('app/ib/question-bank/[collection]/page.tsx').default;
 const scheme=h.load('app/ib/mark-scheme/[id]/page.tsx').default;
 for(const c of h.model.IB_COLLECTIONS.filter(c=>c.subject==='biology')){
  save(c.id+'-'+course,await bank({params:Promise.resolve({collection:c.id}),searchParams:Promise.resolve({course})}));
 }
 for(const [name,predicate] of [
  ['plant-cell',q=>q.id==='ib-bio-a-049'],
  ['alveolar-barrier',q=>q.id==='ib-bio-b-085'],
  ['data-response',q=>q.questionType==='data-based'&&q.diagramSvg],
  ['solution-figure',q=>q.markSchemeDiagramSvg],
  ['hard-inheritance',q=>q.syllabusCode==='D3.2'&&q.difficulty==='hard']]){
  const q=content.getIbQuestions(undefined,course).find(predicate);
  if(q)save(name+'-'+course,await scheme({params:Promise.resolve({id:q.id}),searchParams:Promise.resolve({course})}));
 }
 const login=ibHarness({query:'next='+encodeURIComponent('/ib/question-bank/biology-continuity-change?course='+course)});
 save('login-'+course,React.createElement(login.load('app/ib-login/IBLoginClient.tsx').default));
}
writeFileSync(resolve(output,'index.html'),'<!doctype html><title>Biology review pages</title><h1>Local component review</h1><ul>'+pages.map(p=>'<li><a href="/'+p+'">'+p+'</a></li>').join('')+'</ul>');
console.log(JSON.stringify({output,questions:questions.length,pages:pages.length}));
