// Render actual authenticated components with synthetic local-only user fixtures.
// This creates no route in the deployed application and is never imported there.
import {readFileSync,readdirSync,mkdirSync,writeFileSync,cpSync} from 'node:fs';
import {resolve} from 'node:path';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {ibHarness} from './ib-component-harness.mjs';
const output=resolve(process.argv[2]||'../physics-review');
mkdirSync(output,{recursive:true});
cpSync('node_modules/katex/dist',resolve(output,'katex'),{recursive:true});
const questions=readdirSync('content/ib/physics-hl').filter(f=>f.endsWith('.json')).flatMap(f=>JSON.parse(readFileSync('content/ib/physics-hl/'+f,'utf8')));
const harness=ibHarness({questions,query:'subject=physics-hl&view=questions'});
const collections=harness.model.IB_COLLECTIONS.filter(c=>c.subject==='physics-hl');
const css=['app/ib/ib.module.css','app/ib/questions.module.css'].map(f=>readFileSync(f,'utf8').replace(/:global\(([^)]+)\)/g,'$1')).join('\n');
function save(name,element){writeFileSync(resolve(output,name+'.html'),`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Physics portal visual review</title><link rel="stylesheet" href="/katex/katex.min.css"><style>${css}</style></head><body>${renderToStaticMarkup(element)}</body></html>`);}
const summary={'math-aa-hl':{questions:962,mocks:0,topics:{},collections:[]},'physics-hl':{questions:questions.length,mocks:0,topics:{},collections:collections.map(c=>{const qs=questions.filter(q=>q.collectionId===c.id);return {...c,count:qs.length,subtopics:[...new Set(qs.map(q=>q.subtopic))].sort(),syllabus:harness.load('lib/ib/catalog.ts').physicsSyllabusSubtopics(c.topicId).map(s=>({...s,count:qs.filter(q=>q.syllabusCode===s.code).length}))};})}};
save('index',React.createElement(harness.load('app/ib/IBPortalClient.tsx').default,{email:'visual-review@example.invalid',summary}));
const bank=harness.load('app/ib/question-bank/[collection]/page.tsx').default;
const scheme=harness.load('app/ib/mark-scheme/[id]/page.tsx').default;
for(const c of collections){
 save(c.id,await bank({params:Promise.resolve({collection:c.id}),searchParams:Promise.resolve({})}));
 for(const type of ['multiple-choice','structured','data-based']){
  const sample=questions.find(q=>q.collectionId===c.id&&q.questionType===type&&(type==='multiple-choice'||q.diagramSvg));
  if(sample)save(c.id+'-'+type,await scheme({params:Promise.resolve({id:sample.id})}));
 }
 const hard=questions.find(q=>q.collectionId===c.id&&q.difficulty==='hard'&&q.markSchemeDiagramSvg);
 if(hard)save(c.id+'-hard-scheme',await scheme({params:Promise.resolve({id:hard.id})}));
}
console.log(JSON.stringify({output,questions:questions.length,pages:readdirSync(output).filter(f=>f.endsWith('.html')).length}));
