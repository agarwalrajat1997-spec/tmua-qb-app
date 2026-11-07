import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,cpSync,copyFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import React from 'react';
import {renderToStaticMarkup as render} from 'react-dom/server';
import sharp from 'sharp';
import {ibHarness} from './ib-component-harness.mjs';
const themes=['s1','s2','s3','r1','r2','r3'];
const qs=themes.flatMap(t=>JSON.parse(readFileSync(`content/ib/chemistry-2025-practice/${t}.json`,'utf8')));
const h=ibHarness({questions:qs}),m=h.model,catalog=h.load('lib/ib/catalog.ts');
const old=[...['structure-1','structure-2','structure-3','reactivity-1','reactivity-2','reactivity-3'].flatMap(t=>JSON.parse(readFileSync(`content/ib/chemistry/${t}.json`,'utf8'))),...['structure','periodicity','reactivity','mechanisms'].flatMap(t=>JSON.parse(readFileSync(`content/ib/chemistry-2026-expansion/${t}.json`,'utf8')))];
assert.equal(old.length,800);assert.equal(qs.length,200);
const ids=new Set(old.map(q=>q.id)),prompts=new Set(old.map(q=>q.stem+'\n'+q.parts.map(p=>p.prompt).join('\n')));
const report={status:'passed',questions:qs.length,sl:0,ahl:0,marks:0,types:{},difficulty:{},themes:{},subtopics:{},figures:0,renderedViews:0,files:{},checks:['production Zod schema and per-part mark totals','no duplicate IDs or exact prompts against 800 existing Chemistry questions','exact syllabus titles','SL exclusion of HL-only content','private solutions excluded from question payloads','200 question and 200 solution server-component renderings','safe SVG validation and rasterization','all 22 subtopics covered'],reviewLimit:'Author review and automated checks; no separate human examiner moderation.'};
const out='work/chemistry-2025-preview';mkdirSync(out,{recursive:true});
writeFileSync(out+'/review.css',readFileSync('app/ib/ib.module.css','utf8')+'\n'+readFileSync('app/ib/questions.module.css','utf8').replace(/:global\(([^)]+)\)/g,'$1')+'\nbody{background:#f5f7fb}');
cpSync('node_modules/katex/dist/fonts',out+'/fonts',{recursive:true});copyFileSync('node_modules/katex/dist/katex.min.css',out+'/katex.min.css');
const wrap=(title,html)=>'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+title+'</title><link rel="stylesheet" href="review.css"><link rel="stylesheet" href="katex.min.css"><body>'+html+'</body></html>';
const question=h.load('app/ib/questions/[id]/page.tsx').default,scheme=h.load('app/ib/mark-scheme/[id]/page.tsx').default;
const privateKeys=['markScheme','answerSummary','correctOption','verification','source','markSchemeDiagramSvg'];
const links=[];
for(const raw of qs){
 const q=m.ibQuestionSchema.parse(raw);assert.equal(q.status,'published');assert.equal(q.subject,'chemistry');
 assert.ok(!ids.has(q.id),q.id+' duplicate');ids.add(q.id);
 const fp=q.stem+'\n'+q.parts.map(p=>p.prompt).join('\n');assert.ok(!prompts.has(fp),q.id+' duplicate prompt');prompts.add(fp);
 assert.equal(q.subtopic,catalog.ibSyllabusSubtopics('chemistry',q.topicId).find(s=>s.code===q.syllabusCode)?.title);
 if(q.syllabusCode==='R1.4')assert.equal(q.level,'ahl');
 const prompt=m.questionPrompt(q);for(const k of privateKeys)assert.ok(!(k in prompt),q.id+' answer leak '+k);
 assert.equal(m.questionAvailableForCourse(q,'sl'),q.level==='sl');
 if(q.options)assert.equal(new Set(q.options.map(o=>o.text)).size,4,q.id+' duplicate options');
 const args={params:Promise.resolve({id:q.id}),searchParams:Promise.resolve({course:'hl'})};
 const a=render(await question(args)),b=render(await scheme(args));
 assert.ok(!a.includes('katex-error')&&!b.includes('katex-error'),q.id+' math rendering');
 assert.ok(b.includes('Worked solution &amp; mark allocation'));assert.ok(!a.includes('verification'));
 if(q.level==='ahl'){
  const sl={params:Promise.resolve({id:q.id}),searchParams:Promise.resolve({course:'sl'})};
  await assert.rejects(()=>question(sl),/NOT_FOUND/);await assert.rejects(()=>scheme(sl),/NOT_FOUND/);
 }
 writeFileSync(`${out}/${q.id}.html`,wrap(q.title,a));writeFileSync(`${out}/${q.id}-scheme.html`,wrap(q.title+' — solution',b));report.renderedViews+=2;
 links.push(`<li><a href="${q.id}.html">${q.id}: ${q.title}</a> · <a href="${q.id}-scheme.html">Solution</a></li>`);
 if(q.diagramSvg){assert.ok(m.safeDiagram(q.diagramSvg));await sharp(Buffer.from(q.diagramSvg)).png().toFile(`${out}/${q.id}.png`);report.figures++;}
 report[q.level]++;report.marks+=q.marks;
 for(const [key,value]of [['types',q.questionType],['difficulty',q.difficulty],['themes',q.topicId],['subtopics',q.syllabusCode]])report[key][value]=(report[key][value]??0)+1;
}
assert.equal(Object.keys(report.subtopics).length,22);
for(const t of themes){const bytes=readFileSync(`content/ib/chemistry-2025-practice/${t}.json`);report.files[t]={sha256:createHash('sha256').update(bytes).digest('hex'),questions:qs.filter(q=>q.id.includes('-'+t+'-')).length};}
writeFileSync(out+'/index.html',wrap('200 original Chemistry questions','<main style="padding:30px"><h1>200 original Chemistry questions</h1><ul>'+links.join('')+'</ul></main>'));
const figs=qs.filter(q=>q.diagramSvg);
for(let start=0;start<figs.length;start+=9){
 const part=figs.slice(start,start+9),layers=[];
 for(let i=0;i<part.length;i++){
  const left=(i%3)*730,top=Math.floor(i/3)*430;
  layers.push({input:await sharp(Buffer.from(part[i].diagramSvg)).resize(720,380,{fit:'contain',background:'#fff'}).png().toBuffer(),left:left+5,top:top+40});
  layers.push({input:Buffer.from(`<svg width="720" height="30"><rect width="720" height="30" fill="#e5eaf0"/><text x="12" y="22" font-family="Arial" font-size="18">${part[i].id}: ${part[i].title}</text></svg>`),left:left+5,top:top+5});
 }
 await sharp({create:{width:2190,height:Math.ceil(part.length/3)*430,channels:3,background:'#d9e1eb'}}).composite(layers).png().toFile(`${out}/contact-${start/9+1}.png`);
}
mkdirSync('docs/ib-chemistry-2025-practice',{recursive:true});writeFileSync('docs/ib-chemistry-2025-practice/validation.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
