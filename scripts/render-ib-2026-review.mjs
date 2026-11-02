import {readFileSync,writeFileSync,mkdirSync,copyFileSync,cpSync} from 'node:fs';
import {resolve} from 'node:path';
import React from 'react';
import {renderToStaticMarkup as render} from 'react-dom/server';
import sharp from 'sharp';
import assert from 'node:assert/strict';
import {ibHarness} from './ib-component-harness.mjs';
const out=resolve('work/ib-2026-preview');mkdirSync(out,{recursive:true});
const qs=['aa-sl','aa-hl','ai-sl','ai-hl'].flatMap(c=>JSON.parse(readFileSync('content/ib/math-2026-expansion/'+c+'.json','utf8')));
const h=ibHarness({questions:qs});
const question=h.load('app/ib/questions/[id]/page.tsx').default,scheme=h.load('app/ib/mark-scheme/[id]/page.tsx').default;
const css=readFileSync('app/ib/ib.module.css','utf8')+'\n'+readFileSync('app/ib/questions.module.css','utf8');
writeFileSync(out+'/review.css',css);
cpSync('node_modules/katex/dist/fonts',out+'/fonts',{recursive:true});
copyFileSync('node_modules/katex/dist/katex.min.css',out+'/katex.min.css');
const wrap=(title,html)=>'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+title+'</title><link rel="stylesheet" href="review.css"><link rel="stylesheet" href="katex.min.css"></head><body>'+html+'</body></html>';
let diagrams=0;const links=[];
for(const q of qs){
 const params={params:Promise.resolve({id:q.id}),searchParams:Promise.resolve({})};
 const a=render(await question(params)),b=render(await scheme(params));
 assert.ok(!a.includes('katex-error')&&!b.includes('katex-error'),q.id+' mathematical rendering');
 assert.ok(b.includes('Worked solution &amp; mark allocation')&&b.includes('schemeTotal'),q.id+' full scheme');
 assert.ok(a.includes('target="_blank"'),q.id+' scheme opens separately');
 writeFileSync(out+'/'+q.id+'.html',wrap(q.title,a));
 writeFileSync(out+'/'+q.id+'-scheme.html',wrap(q.title+' — mark scheme',b));
 if(q.diagramSvg){await sharp(Buffer.from(q.diagramSvg)).resize(640,380,{fit:'contain',background:'#fff'}).png().toFile(out+'/'+q.id+'.png');diagrams++;}
 links.push('<li><a href="'+q.id+'.html">'+q.id+' — '+q.title+'</a> · <a href="'+q.id+'-scheme.html">Mark scheme</a></li>');
}
// All routes must demand authentication even though this isolated renderer uses
// a test user for layout; there is no bypass in application code.
const noUser=ibHarness({questions:qs,user:null});
for(const path of ['app/ib/questions/[id]/page.tsx','app/ib/mark-scheme/[id]/page.tsx']){
 const route=noUser.load(path).default;
 await assert.rejects(()=>route({params:Promise.resolve({id:qs[0].id}),searchParams:Promise.resolve({})}),/AUTH_REQUIRED/);
}
writeFileSync(out+'/index.html',wrap('400-question review','<main style="padding:28px"><h1>IB Maths — 400 original additions</h1><p>Local layout review. Production authentication is unchanged.</p><ul>'+links.join('')+'</ul></main>'));
for(const course of ['aa-sl','aa-hl','ai-sl','ai-hl']){
 const items=qs.filter(q=>q.subject==='math-'+course&&q.diagramSvg);
 for(let start=0;start<items.length;start+=20){
  const subset=items.slice(start,start+20),layers=[];
  for(let i=0;i<subset.length;i++){
   const left=(i%4)*330,top=Math.floor(i/4)*224;
   const img=await sharp(out+'/'+subset[i].id+'.png').resize(320,190).png().toBuffer();
   const label=Buffer.from('<svg width="320" height="26"><rect width="320" height="26" fill="#eee"/><text x="8" y="18" font-size="13" font-family="Arial">'+subset[i].id+'</text></svg>');
   layers.push({input:img,left:left+5,top:top+30},{input:label,left:left+5,top:top+3});
  }
  await sharp({create:{width:1320,height:Math.ceil(subset.length/4)*224,channels:3,background:'#ddd'}}).composite(layers).png().toFile(out+'/'+course+'-contact-'+(start/20+1)+'.png');
 }
}
console.log(JSON.stringify({status:'passed',questions:qs.length,schemeViews:qs.length,diagrams,auth:'question and scheme reject unsigned user',out}));
