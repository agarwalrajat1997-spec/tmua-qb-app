import assert from 'node:assert/strict';
import {readFileSync,readdirSync,writeFileSync,mkdirSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import React from 'react';
import {renderToStaticMarkup as render} from 'react-dom/server';
import {ibHarness} from './ib-component-harness.mjs';
const baseline='0c6d458dfd664936be2d89d0f75c8d7d825b1dd6';
const root='content/ib/chemistry-2026-expansion';
const additions=['structure','periodicity','reactivity','mechanisms'].flatMap(b=>JSON.parse(readFileSync(`${root}/${b}.json`,'utf8')));
const hash=b=>createHash('sha256').update(b).digest('hex');
const lf=b=>b.toString('utf8').replace(/\r\n/g,'\n');
assert.equal(additions.length,200);assert.equal(new Set(additions.map(q=>q.id)).size,200);
const imports=[],real=ibHarness({onModule:n=>imports.push(n)}),content=real.load('lib/ib/content.ts');
const catalog=real.load('lib/ib/catalog.ts'),grouping=real.load('lib/ib/topic-groups.ts');
const bodyImports=()=>imports.filter(n=>/^@\/content\/ib\/(?:[^/]+\/[^/]+|(?:math|chemistry)-2026-expansion\/by-collection\/[^/]+)\.json$/.test(n));
assert.equal(bodyImports().length,0);const hlSummary=content.getIbSummary('hl'),slSummary=content.getIbSummary('sl');assert.equal(bodyImports().length,0);
const index=JSON.parse(readFileSync('content/ib/content-index.json','utf8'));
const frozen=[],collections=[];let oldHL=0,oldSL=0;
for(const c of real.model.IB_COLLECTIONS.filter(c=>c.subject==='chemistry')){
 const file=`content/ib/chemistry/${c.topicId}.json`,bytes=readFileSync(file),original=execFileSync('git',['show',`${baseline}:${file}`],{maxBuffer:15_000_000});
 assert.equal(lf(bytes),lf(original),'original600 content changed: '+file);frozen.push({file,sha256:hash(lf(bytes)),normalization:'LF only; Windows checkout line endings ignored'});
 const old=JSON.parse(bytes).filter(q=>q.status==='published'),extra=additions.filter(q=>q.collectionId===c.id);
 oldHL+=old.length;oldSL+=old.filter(q=>q.level==='sl').length;
 const before=bodyImports().length;
 const [all,sl,one,repeat]=await Promise.all([content.getIbQuestions(c.id,'hl'),content.getIbQuestions(c.id,'sl'),content.getIbQuestion(extra[0].id,'hl'),content.getIbQuestions(c.id,'hl')]);
 assert.equal(bodyImports().length-before,2,'one original plus one small addition bank');assert.equal(all,repeat);assert.equal(one,all.find(q=>q.id===extra[0].id));
 assert.deepEqual(Array.from(all,q=>q.id),[...old,...extra].map(q=>q.id));
 assert.deepEqual(Array.from(sl,q=>q.id),[...old,...extra].filter(q=>q.level==='sl').map(q=>q.id));
 assert.equal(readFileSync(`${root}/by-collection/${c.id}.json`,'utf8'),JSON.stringify(extra.map(q=>real.model.ibQuestionSchema.parse(q)))+'\n');
 const groups=grouping.ibTopicGroups(c,all,'hl');
 for(const q of extra){
  assert.equal(index.questionCollections[q.id],c.id);assert.equal(await content.getIbQuestion(q.id,'hl'),all.find(x=>x.id===q.id));
  assert.equal(Boolean(await content.getIbQuestion(q.id,'sl')),q.level==='sl','SL gating '+q.id);
  assert.ok(groups.some(g=>grouping.questionInTopicGroup(q,g)),'category coverage '+q.id);
 }
 collections.push({id:c.id,legacy:old.length,added:extra.length,total:all.length,sl:sl.length});
}
assert.equal(oldHL,600);assert.equal(hlSummary.chemistry.questions,800);assert.equal(slSummary.chemistry.questions,oldSL+80);
assert.equal(readdirSync(root+'/by-collection').filter(f=>f.endsWith('.json')).length,6);
for(const id of ['missing','__proto__','constructor','../../escape'])assert.equal(await content.getIbQuestion(id),undefined);
const fixtures=structuredClone(additions),canary='CHEM_SOLUTION_CANARY_',privateCanary='CHEM_REVIEW_CANARY_';
for(const q of fixtures){q.markScheme[0].steps[0].text+=' '+canary+q.id;q.verification.notes=privateCanary+q.id;}
const auth=[],h=ibHarness({questions:fixtures,useContentModule:true,onAuth:p=>auth.push(p)}),fc=h.load('lib/ib/content.ts');
assert.equal((await fc.getIbQuestions()).length,200);assert.equal((await fc.getIbQuestions(undefined,'sl')).length,80);
const question=h.load('app/ib/questions/[id]/page.tsx').default,scheme=h.load('app/ib/mark-scheme/[id]/page.tsx').default,bank=h.load('app/ib/question-bank/[collection]/page.tsx').default;
const args=(id,course='hl')=>({params:Promise.resolve({id}),searchParams:Promise.resolve({course})});
const articles=html=>Array.from(html.matchAll(/<article\b[^>]*id="([^"]+)"/g),m=>m[1]);
let views=0;const filters=[];
for(const q of fixtures){
 let html=render(await question(args(q.id)));views++;assert.ok(!html.includes(canary)&&!html.includes(privateCanary));assert.ok(!html.includes('katex-error'));
 assert.match(html,/target="_blank"/);assert.match(html,new RegExp('/ib/mark-scheme/'+q.id+'\\?course=hl'));
 html=render(await scheme(args(q.id)));views++;assert.ok(html.includes(canary+q.id));assert.ok(!html.includes(privateCanary));assert.match(html,/Worked solution &amp; mark allocation/);
 if(q.level==='ahl'){
  await assert.rejects(()=>question(args(q.id,'sl')),/NOT_FOUND/);await assert.rejects(()=>scheme(args(q.id,'sl')),/NOT_FOUND/);
 }else{assert.ok(render(await question(args(q.id,'sl'))).includes('Question '+q.number));views++;}
}
for(const c of collections){
 const rows=fixtures.filter(q=>q.collectionId===c.id),q=rows[0],group=grouping.ibTopicGroups(real.model.getIbCollection(c.id),rows,'hl').find(g=>grouping.questionInTopicGroup(q,g));
 const query={course:'hl',q:q.id,difficulty:'hard',level:q.level,type:q.questionType,category:group.id};
 let html=render(await bank({params:Promise.resolve({collection:c.id}),searchParams:Promise.resolve(query)}));views++;
 assert.deepEqual(articles(html),[q.id]);assert.match(html,/Filters update automatically/);assert.doesNotMatch(html,/>Apply(?: filters?)?</i);assert.ok(!html.includes(canary)&&!html.includes(privateCanary));
 const dest=new URL(auth.at(-1),'https://example.invalid');for(const [k,v]of Object.entries(query))assert.equal(dest.searchParams.get(k),v);
 for(const change of [{difficulty:'easy'},{type:'multiple-choice'},{q:canary+q.id}]){
  html=render(await bank({params:Promise.resolve({collection:c.id}),searchParams:Promise.resolve({...query,...change})}));views++;assert.deepEqual(articles(html),[]);
 }
 filters.push({collection:c.id,id:q.id,query,status:'passed'});
}
const blockedImports=[],blocked=ibHarness({questions:fixtures,useContentModule:true,user:null,onModule:n=>blockedImports.push(n)});let blockedRoutes=0;
for(const c of collections){
 const q=fixtures.find(q=>q.collectionId===c.id);
 for(const route of ['questions','mark-scheme']){await assert.rejects(()=>blocked.load(`app/ib/${route}/[id]/page.tsx`).default(args(q.id)),/AUTH_REQUIRED/);blockedRoutes++;}
 await assert.rejects(()=>blocked.load('app/ib/question-bank/[collection]/page.tsx').default({params:Promise.resolve({collection:c.id}),searchParams:Promise.resolve({})}),/AUTH_REQUIRED/);blockedRoutes++;
}
assert.equal(blockedImports.filter(n=>n.includes('/by-collection/')).length,0);
const report={status:'passed',baseline,questionsAdded:200,canonicalResolved:200,totalChemistryHL:800,totalChemistrySL:slSummary.chemistry.questions,addedSL:80,addedAHL:120,overviewBodyImports:0,firstTopicChunks:2,cachedPromiseShared:true,frozenLegacy:{questions:600,files:frozen},collections,filters,routeViews:views,authentication:{unsignedRoutesRejected:blockedRoutes,all120AHLQuestionAndSchemeRoutesRejectSL:true},privacy:'Per-question canaries visible only in authenticated worked schemes; absent from question/bank views and search.',provenance:'Original syllabus-authored questions; no claim of official IB origin or human examiner moderation.'};
mkdirSync('docs/ib-2026-chemistry',{recursive:true});writeFileSync('docs/ib-2026-chemistry/portal-checks.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({status:'passed',questions:200,hl:800,sl:slSummary.chemistry.questions,routeViews:views,SLblockedAHL:120,authRoutes:blockedRoutes,overviewBodyImports:0,frozenLegacy:600}));
