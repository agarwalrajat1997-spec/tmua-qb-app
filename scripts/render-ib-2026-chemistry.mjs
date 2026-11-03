import {readFileSync,writeFileSync,mkdirSync,copyFileSync,cpSync,existsSync} from 'node:fs';
import {resolve} from 'node:path';
import React from 'react';
import {renderToStaticMarkup as render} from 'react-dom/server';
import sharp from 'sharp';
import assert from 'node:assert/strict';
import {ibHarness} from './ib-component-harness.mjs';
const out=resolve('work/chem-2026-preview');mkdirSync(out,{recursive:true});
const batches=['structure','periodicity','reactivity','mechanisms'];
const chosen=process.argv.find(x=>x.startsWith('--batch='))?.split('=')[1];
const qs=(chosen?[chosen]:batches).flatMap(c=>JSON.parse(readFileSync('content/ib/chemistry-2026-expansion/'+c+'.json','utf8')));
const h=ibHarness({questions:qs});
const question=h.load('app/ib/questions/[id]/page.tsx').default,scheme=h.load('app/ib/mark-scheme/[id]/page.tsx').default;
writeFileSync(out+'/review.css',readFileSync('app/ib/ib.module.css','utf8')+'\n'+readFileSync('app/ib/questions.module.css','utf8'));
cpSync('node_modules/katex/dist/fonts',out+'/fonts',{recursive:true});
copyFileSync('node_modules/katex/dist/katex.min.css',out+'/katex.min.css');
const wrap=(title,html)=>'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+title+'</title><link rel="stylesheet" href="review.css"><link rel="stylesheet" href="katex.min.css"></head><body>'+html+'</body></html>';
let diagrams=0,solutionDiagrams=0;const links=[];
for(const q of qs){
 const params={params:Promise.resolve({id:q.id}),searchParams:Promise.resolve({})};
 const a=render(await question(params)),b=render(await scheme(params));
 assert.ok(!a.includes('katex-error')&&!b.includes('katex-error'),q.id+' formula rendering');
 assert.ok(b.includes('Worked solution &amp; mark allocation')&&b.includes('schemeTotal'),q.id+' full scheme');
 writeFileSync(out+'/'+q.id+'.html',wrap(q.title,a));writeFileSync(out+'/'+q.id+'-scheme.html',wrap(q.title+' — scheme',b));
 for(const [field,suffix] of [['diagramSvg',''],['markSchemeDiagramSvg','-solution']])if(q[field]){
  await sharp(Buffer.from(q[field])).resize(760,760,{fit:'inside',withoutEnlargement:true}).png().toFile(out+'/'+q.id+suffix+'.png');
  if(suffix)solutionDiagrams++;else diagrams++;
 }
 links.push('<li><a href="'+q.id+'.html">'+q.id+' — '+q.title+'</a> · <a href="'+q.id+'-scheme.html">Mark scheme</a></li>');
}
writeFileSync(out+'/index.html',wrap('Chemistry review','<main style="padding:28px"><h1>IB Chemistry — original hard additions</h1><ul>'+links.join('')+'</ul></main>'));
for(const theme of ['s1','s2','s3','r1','r2','r3']){
 const items=qs.filter(q=>q.id.includes('-'+theme+'-')&&q.diagramSvg);
 for(let start=0;start<items.length;start+=12){
  const subset=items.slice(start,start+12),layers=[];
  for(let i=0;i<subset.length;i++){
   const left=(i%3)*510,top=Math.floor(i/3)*370;
   const img=await sharp(out+'/'+subset[i].id+'.png').resize(500,330,{fit:'contain',background:'#fff'}).png().toBuffer();
   const label=Buffer.from('<svg width="500" height="28"><rect width="500" height="28" fill="#eee"/><text x="8" y="20" font-size="16" font-family="Arial">'+subset[i].id+'</text></svg>');
   layers.push({input:img,left:left+5,top:top+35},{input:label,left:left+5,top:top+3});
  }
  await sharp({create:{width:1530,height:Math.ceil(subset.length/3)*370,channels:3,background:'#ddd'}}).composite(layers).png().toFile(out+'/'+theme+'-contact-'+(start/12+1)+'.png');
 }
}
console.log(JSON.stringify({status:'passed',questions:qs.length,schemeViews:qs.length,diagrams,solutionDiagrams,out}));
