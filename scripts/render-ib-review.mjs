// Static visual-review exports of the actual React components. Local QA only.
import { readFileSync, writeFileSync, mkdirSync, readdirSync, cpSync } from 'node:fs';
import { resolve } from 'node:path';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { ibHarness } from './ib-component-harness.mjs';

const input=resolve(process.argv[2] || 'content/ib/math-aa-hl');
const output=resolve(process.argv[3] || '../ib-visual-review');
mkdirSync(`${output}/dist`,{recursive:true});mkdirSync(`${output}/.openai`,{recursive:true});
writeFileSync(`${output}/.openai/hosting.json`,JSON.stringify({static:{directory:'dist'}}));
cpSync('node_modules/katex/dist',`${output}/dist/katex`,{recursive:true});
const questions=readdirSync(input).filter(f=>/^(number-algebra|functions|geometry-trigonometry|statistics-probability|calculus-[12])\.json$/.test(f)).flatMap(f=>JSON.parse(readFileSync(`${input}/${f}`,'utf8')));
const harness=ibHarness({questions});
const collections=harness.model.IB_COLLECTIONS;
const css=['app/ib/ib.module.css','app/ib/questions.module.css'].map(p=>readFileSync(p,'utf8').replace(/:global\(([^)]+)\)/g,'$1')).join('\n');
function save(name,element){writeFileSync(`${output}/dist/${name}.html`,`<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><meta charset="utf-8"><link rel="stylesheet" href="/katex/katex.min.css"><style>${css}</style><title>IB portal visual review</title></head><body>${renderToStaticMarkup(element)}</body></html>`);}
const summary={'math-aa-hl':{questions:questions.length,mocks:0,topics:{},collections:collections.map(c=>{const list=questions.filter(q=>q.collectionId===c.id);return {...c,count:list.length,subtopics:[...new Set(list.map(q=>q.subtopic))].sort()};})},'physics-hl':{questions:0,mocks:0,topics:{},collections:[]}};
save('index',React.createElement(harness.load('app/ib/IBPortalClient.tsx').default,{email:'review@example.invalid',summary}));
const bank=harness.load('app/ib/question-bank/[collection]/page.tsx').default;
const scheme=harness.load('app/ib/mark-scheme/[id]/page.tsx').default;
for(const c of collections){
 if(!questions.some(q=>q.collectionId===c.id))continue;
 save(c.id,await bank({params:Promise.resolve({collection:c.id}),searchParams:Promise.resolve({})}));
 const sample=questions.find(q=>q.collectionId===c.id&&q.number===1);
 if(sample)save(`${c.id}-scheme`,await scheme({params:Promise.resolve({id:sample.id})}));
}
for(const id of ['ib-aa-na-002','ib-aa-na-005','ib-aa-fn-127','ib-aa-sp-149','ib-aa-gt-182','ib-aa-c1-120','ib-aa-c2-127']) {
 if(questions.some(q=>q.id===id)) save(id,await scheme({params:Promise.resolve({id})}));
}
console.log(JSON.stringify({output,files:readdirSync(`${output}/dist`).filter(f=>f.endsWith('.html')),questions:questions.length}));
