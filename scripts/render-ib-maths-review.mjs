// Actual components with a synthetic local user; static visual evidence only.
// No application routes, authentication bypass, external requests or browser automation.
import {readFileSync,readdirSync,mkdirSync,writeFileSync,cpSync} from 'node:fs';
import {resolve} from 'node:path';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {ibHarness} from './ib-component-harness.mjs';
const output=resolve(process.argv[2]??'../maths-review');
mkdirSync(output,{recursive:true});
cpSync('node_modules/katex/dist',resolve(output,'katex'),{recursive:true});
const subjects=['math-aa-sl','math-ai-sl','math-aa-hl'];
const questions=subjects.flatMap(course=>readdirSync('content/ib/'+course).filter(f=>f.endsWith('.json')).flatMap(f=>JSON.parse(readFileSync(`content/ib/${course}/${f}`,'utf8'))));
const css=['app/ib/ib.module.css','app/ib/questions.module.css'].map(f=>readFileSync(f,'utf8').replace(/:global\(([^)]+)\)/g,'$1')).join('\n');
const pages=[];
function save(name,element){
 writeFileSync(resolve(output,name+'.html'),`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Maths portal visual review</title><link rel="stylesheet" href="/katex/katex.min.css"><style>${css}</style></head><body>${renderToStaticMarkup(element)}</body></html>`);
 pages.push(name+'.html');
}
for(const subject of subjects){
 const h=ibHarness({questions,useContentModule:true,query:'subject='+subject});
 const content=h.load('lib/ib/content.ts');
 save(subject+'-overview',React.createElement(h.load('app/ib/IBPortalClient.tsx').default,{email:'visual-review@example.invalid',summary:content.getIbSummary()}));
 const bank=h.load('app/ib/question-bank/[collection]/page.tsx').default;
 const scheme=h.load('app/ib/mark-scheme/[id]/page.tsx').default;
 for(const c of h.model.IB_COLLECTIONS.filter(c=>c.subject===subject))save(c.id,await bank({params:Promise.resolve({collection:c.id}),searchParams:Promise.resolve({})}));
 const items=content.getIbQuestions().filter(q=>q.subject===subject);
 for(const [label,predicate] of [['solution-figure',q=>q.markSchemeDiagramSvg],['hard',q=>q.difficulty==='hard'&&q.calculator],['table',q=>q.stem.includes('|')],['extended',q=>q.examStyle==='extended-response']]){
  const q=items.find(predicate);if(q)save(subject+'-'+label,await scheme({params:Promise.resolve({id:q.id})}));
 }
 for(const id of ['ib-aa-c1-022','ib-aa-c1-120','ib-aisl-gt-061','ib-aisl-ca-005','ib-aasl-fn-065']){
  const q=items.find(q=>q.id===id);if(q)save(id,await scheme({params:Promise.resolve({id:q.id})}));
 }
 const login=ibHarness({query:'next='+encodeURIComponent('/ib/mark-scheme/'+(items[0]?.id??''))});
 save(subject+'-login',React.createElement(login.load('app/ib-login/IBLoginClient.tsx').default));
}
writeFileSync(resolve(output,'index.html'),'<!doctype html><title>Maths review pages</title><h1>Local component review</h1><ul>'+pages.map(p=>'<li><a href="/'+p+'">'+p+'</a></li>').join('')+'</ul>');
console.log(JSON.stringify({output,questions:questions.length,pages:pages.length}));
