// Static proofs of actual components with a synthetic local user; never an app auth bypass.
import {readFileSync,readdirSync,mkdirSync,writeFileSync,cpSync} from 'node:fs';
import {resolve} from 'node:path';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {ibHarness} from './ib-component-harness.mjs';
const output=resolve(process.argv[2]??'../expansion-review');mkdirSync(output,{recursive:true});
cpSync('node_modules/katex/dist',resolve(output,'katex'),{recursive:true});
const subjects=['math-ai-hl','physics-hl','economics','business-management'];
const questions=subjects.flatMap(s=>readdirSync(`content/ib/${s}`).filter(f=>f.endsWith('.json')).flatMap(f=>JSON.parse(readFileSync(`content/ib/${s}/${f}`,'utf8'))));
const css=['app/ib/ib.module.css','app/ib/questions.module.css'].map(f=>readFileSync(f,'utf8').replace(/:global\(([^)]+)\)/g,'$1')).join('\n');
const pages=[];
function save(name,element){writeFileSync(resolve(output,name+'.html'),`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Course expansion review</title><link rel="stylesheet" href="/katex/katex.min.css"><style>${css}</style></head><body>${renderToStaticMarkup(element)}</body></html>`);pages.push(name+'.html');}
for(const subject of subjects)for(const course of subject==='math-ai-hl'?['hl']:['sl','hl']){
 const h=ibHarness({questions,useContentModule:true,query:`subject=${subject}&course=${course}`}),content=h.load('lib/ib/content.ts');
 save(`${subject}-${course}-overview`,React.createElement(h.load('app/ib/IBPortalClient.tsx').default,{email:'visual-review@example.invalid',summary:content.getIbSummary(course)}));
 const bank=h.load('app/ib/question-bank/[collection]/page.tsx').default,scheme=h.load('app/ib/mark-scheme/[id]/page.tsx').default;
 for(const c of h.model.IB_COLLECTIONS.filter(c=>c.subject===subject))save(`${c.id}-${course}`,await bank({params:Promise.resolve({collection:c.id}),searchParams:Promise.resolve({course})}));
 const items=content.getIbQuestions(undefined,course).filter(q=>q.subject===subject);
 for(const [name,predicate] of [['diagram',q=>q.diagramSvg],['solution-figure',q=>q.markSchemeDiagramSvg],['hard',q=>q.difficulty==='hard'],['best-fit',q=>q.markScheme.some(g=>g.rubric?.bands)],['analytic',q=>q.markScheme.some(g=>g.rubric?.criteria)]]){
  const q=items.find(predicate);if(q)save(`${subject}-${course}-${name}`,await scheme({params:Promise.resolve({id:q.id}),searchParams:Promise.resolve({course})}));
 }
 const sample=items[0];save(`${subject}-${course}-login`,React.createElement(ibHarness({query:'next='+encodeURIComponent(`/ib/mark-scheme/${sample.id}?course=${course}`)}).load('app/ib-login/IBLoginClient.tsx').default));
}
writeFileSync(resolve(output,'index.html'),'<!doctype html><title>Course review</title><h1>Course component review</h1><ul>'+pages.map(p=>`<li><a href="/${p}">${p}</a></li>`).join('')+'</ul>');
console.log(JSON.stringify({output,questions:questions.length,pages:pages.length}));
