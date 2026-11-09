import assert from 'node:assert/strict';
import {readFileSync,readdirSync,writeFileSync,mkdirSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import React from 'react';
import {renderToStaticMarkup as render} from 'react-dom/server';
import {ibHarness} from './ib-component-harness.mjs';

// Integration evidence uses real asynchronous production loaders and real route
// components. Only authentication and framework surfaces are local test doubles.
// No student account, live database, mail or authentication bypass is created.
const baseline='1b21e2e26747b864c870bc8fb1c07ec7ad237931';
const courses=['aa-sl','aa-hl','ai-sl','ai-hl'];
const root='content/ib/math-2026-expansion';
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const canonical=Object.fromEntries(courses.map(c=>[c,JSON.parse(readFileSync(`${root}/${c}.json`,'utf8'))]));
const additions=courses.flatMap(c=>canonical[c]);
assert.equal(additions.length,400);
const fileHashes=Object.fromEntries(courses.map(c=>[c,hash(readFileSync(`${root}/${c}.json`))]));
const ids=new Set(additions.map(q=>q.id));
assert.equal(ids.size,400);
const imports=[],real=ibHarness({onModule:name=>imports.push(name)});
const content=real.load('lib/ib/content.ts');
const catalog=real.load('lib/ib/catalog.ts');
const grouping=real.load('lib/ib/topic-groups.ts');
const legacyImport=name=>/^@\/content\/ib\/math-(?:aa|ai)-(?:sl|hl)\/[^/]+\.json$/.test(name);
const extraImport=name=>name.startsWith('@/content/ib/math-2026-expansion/by-collection/');
const bodyImports=()=>imports.filter(name=>legacyImport(name)||extraImport(name));
assert.equal(bodyImports().length,0,'navigation import loads zero question bodies');
const summaries=content.getIbSummary('hl');
assert.equal(content.getIbSummary('hl'),summaries,'overview reuses immutable metadata');
assert.equal(bodyImports().length,0,'all-course overview loads zero question banks');

const index=JSON.parse(readFileSync('content/ib/content-index.json','utf8'));
function inspectMetadata(value){
 if(!value||typeof value!=='object')return;
 for(const [key,item] of Object.entries(value)){
  assert.ok(!['stem','parts','markScheme','diagramSvg','diagramUrl','answerSummary','verification','source'].includes(key),'question/answer body leaked into navigation index: '+key);
  inspectMetadata(item);
 }
}
inspectMetadata(index);
for(const id of ['missing','__proto__','constructor','../../outside']){
 assert.equal(await content.getIbQuestion(id),undefined);
 assert.equal((await content.getIbQuestions(id)).length,0);
}
assert.equal(bodyImports().length,0,'unrecognized identifiers cannot trigger content imports');

const first=additions[0];
const firstCollection=real.model.IB_COLLECTIONS.find(c=>c.id===first.collectionId);
const [bank,detail,again]=await Promise.all([
 content.getIbQuestions(first.collectionId),
 content.getIbQuestion(first.id),
 content.getIbQuestions(first.collectionId),
]);
assert.equal(bank,again,'parallel requests share a validated immutable bank');
assert.equal(detail,bank.find(q=>q.id===first.id));
assert.equal(imports.filter(legacyImport).length,1,'one legacy topic bank imported');
assert.equal(imports.filter(extraImport).length,1,'only its own small addition chunk imported');
assert.ok(bank.every(q=>q.collectionId===firstCollection.id));

const frozen=[],courseResults={},groupsChecked=[],collectionResults=[];
for(const course of courses){
 const subject='math-'+course;
 const old=[];
 for(const name of readdirSync('content/ib/'+subject).filter(f=>f.endsWith('.json')).sort()){
  const path=`content/ib/${subject}/${name}`;
  const bytes=readFileSync(path);
  const original=execFileSync('git',['show',`${baseline}:${path}`],{maxBuffer:15_000_000});
  assert.ok(bytes.equals(original),'frozen original bank changed: '+path);
  frozen.push({path,sha256:hash(bytes)});
  old.push(...JSON.parse(bytes));
 }
 const newQuestions=canonical[course];
 assert.equal(newQuestions.length,100);
 const topicCounts=Object.fromEntries(catalog.IB_COURSES[subject].topics.map(t=>[t.id,newQuestions.filter(q=>q.topicId===t.id).length]));
 assert.deepEqual(Object.values(topicCounts),[20,20,20,20,20],'exactly20 additions per specification topic');
 const practice=course.startsWith('aa-')?JSON.parse(readFileSync('content/ib/aa-functions-practice/'+course.slice(3)+'.json','utf8')):[];
 assert.equal(summaries[subject].questions,old.filter(q=>q.status==='published').length+100+practice.length);
 assert.equal(content.getIbSummary('sl')[subject].questions,summaries[subject].questions,'four separate Maths streams retain their own course bank');
 for(const collection of real.model.IB_COLLECTIONS.filter(c=>c.subject===subject)){
  const enrich=newQuestions.filter(q=>q.collectionId===collection.id);
  const derivedPath=`${root}/by-collection/${collection.id}.json`;
  const normalizedChunk=JSON.stringify(enrich.map(q=>real.model.ibQuestionSchema.parse(q)))+'\n';
  assert.equal(hash(readFileSync(derivedPath)),hash(normalizedChunk),'topicwise derived chunk is stale: '+derivedPath);
  const actual=await content.getIbQuestions(collection.id);
  const expected=[...old.filter(q=>q.collectionId===collection.id&&q.status==='published'),...enrich,...practice.filter(q=>q.collectionId===collection.id)];
  assert.deepEqual(Array.from(actual,q=>q.id),expected.map(q=>q.id),'legacy ordering followed by this topic additions only');
  assert.equal(new Set(actual.map(q=>q.id)).size,actual.length,'no repeated merged record');
  const groups=grouping.ibTopicGroups(collection,actual);
  for(const q of enrich){
   assert.equal(index.questionCollections[q.id],collection.id,'generated index maps every new identifier');
   const resolved=await content.getIbQuestion(q.id);
   assert.equal(resolved,actual.find(a=>a.id===q.id),'new detail resolves same cached topic object');
   assert.equal(JSON.stringify(resolved),JSON.stringify(real.model.ibQuestionSchema.parse(q)),'loaded new record equals validated canonical content');
   const matches=groups.filter(g=>grouping.questionInTopicGroup(q,g));
   assert.ok(matches.length,'new subtopic is discoverable through a category: '+q.id);
   groupsChecked.push({id:q.id,categories:matches.map(g=>g.id)});
   const prompt=real.model.questionPrompt(resolved);
   for(const privateKey of ['markScheme','answerSummary','verification','source','markSchemeDiagramSvg','markSchemeDiagramUrl']){
    assert.ok(!(privateKey in prompt),'private field in question payload '+q.id+':'+privateKey);
   }
  }
  collectionResults.push({course,collection:collection.id,old:expected.length-enrich.length,added:enrich.length,total:actual.length});
 }
 courseResults[course]={questionsAdded:100,oldQuestions:old.length,newTotal:summaries[subject].questions,topicCounts};
}
assert.equal(imports.filter(legacyImport).length,21,'Maths loads21 original topic chunks, not a monolithic body import');
assert.equal(imports.filter(extraImport).length,21,'Maths loads21 own-topic enrichment chunks');
const derivedFiles=readdirSync(root+'/by-collection').filter(f=>f.endsWith('.json')).sort();
assert.deepEqual(derivedFiles,collectionResults.map(c=>c.collection+'.json').sort(),'only expected topic enrichment chunks exist');

// The fixture harness feeds canonical additions through the same async content
// implementation. Its legacy-bank mock deliberately owns the complete fixture;
// the generated additions import returns [] so records are never counted twice.
const solutionPrefix='PORTAL_SOLUTION_CANARY_';
const secretPrefix='PORTAL_PRIVATE_VERIFICATION_';
const summaryPrefix='PORTAL_PRIVATE_SUMMARY_';
const fixtures=structuredClone(additions);
for(const q of fixtures){
 q.markScheme[0].steps[0].text+=' '+solutionPrefix+q.id;
 q.verification.notes=secretPrefix+q.id;
 q.answerSummary=summaryPrefix+q.id;
}
const auth=[],fixture=ibHarness({questions:fixtures,useContentModule:true,onAuth:path=>auth.push(path)});
const fc=fixture.load('lib/ib/content.ts');
for(const course of courses)assert.equal(fc.getIbSummary()['math-'+course].questions,100,'canonical addition fixture summary');
assert.equal((await fc.getIbQuestions()).length,400,'async fixture does not merge additions twice');
const routeBank=fixture.load('app/ib/question-bank/[collection]/page.tsx').default;
const routeQuestion=fixture.load('app/ib/questions/[id]/page.tsx').default;
const routeScheme=fixture.load('app/ib/mark-scheme/[id]/page.tsx').default;
const bankArgs=(collection,query={})=>({params:Promise.resolve({collection}),searchParams:Promise.resolve(query)});
const detailArgs=id=>({params:Promise.resolve({id}),searchParams:Promise.resolve({})});
const articleIds=html=>Array.from(html.matchAll(/<article\b[^>]*id="([^"]+)"/g),m=>m[1]);
const containsOnly=(html,predicate,label)=>{
 const visible=articleIds(html);
 assert.ok(visible.length,label+' should show at least one matching question');
 assert.ok(visible.every(id=>predicate(fixtures.find(q=>q.id===id))),label+' returned a question outside its filter');
 return visible.length;
};
const noPrivate=html=>assert.ok(!html.includes(solutionPrefix)&&!html.includes(secretPrefix)&&!html.includes(summaryPrefix),'student prompt rendered private content');
const newTabLink=(html,id)=>{
 const anchor=Array.from(html.matchAll(/<a\b[^>]*>/g),m=>m[0]).find(tag=>tag.includes(`href="/ib/mark-scheme/${id}"`));
 assert.ok(anchor,'mark scheme link exists for '+id);
 assert.match(anchor,/target="_blank"/);
 assert.match(anchor,/rel="noopener noreferrer"/);
};
const filterChecks=[];
let routeViews=0;
for(const c of collectionResults){
 const collection=fixture.model.IB_COLLECTIONS.find(x=>x.id===c.collection);
 const rows=fixtures.filter(q=>q.collectionId===c.collection);
 const groups=grouping.ibTopicGroups(collection,rows);
 for(const difficulty of ['medium','hard']){
  const q=rows.find(q=>q.difficulty===difficulty);
  if(!q)continue;
  const category=groups.find(g=>grouping.questionInTopicGroup(q,g));
  const query={q:q.id,difficulty,calculator:q.calculator?'yes':'no',subtopic:q.subtopic,category:category.id,style:q.examStyle};
  const html=render(await routeBank(bankArgs(c.collection,query)));routeViews++;
  assert.deepEqual(articleIds(html),[q.id],'combined filters preserve the new question '+q.id);
  assert.match(html,/Filters update automatically/);
  assert.doesNotMatch(html,/>Apply(?: filters?)?</i);
  newTabLink(html,q.id);
  noPrivate(html);
  const destination=new URL(auth.at(-1),'https://local-review.invalid');
  for(const key of ['q','difficulty','calculator','subtopic','category','style'])assert.equal(destination.searchParams.get(key),query[key],'login return link preserves '+key);
  filterChecks.push({course:c.course,topic:collection.topicId,collection:c.collection,difficulty,id:q.id,category:category.id,status:'passed'});
 }
 const q=rows[0];
 let html=render(await routeBank(bankArgs(c.collection,{q:q.id,difficulty:q.difficulty==='hard'?'medium':'hard'})));routeViews++;
 assert.equal(articleIds(html).length,0,'opposite difficulty excludes the exact new ID');
 html=render(await routeBank(bankArgs(c.collection,{q:q.id,calculator:q.calculator?'no':'yes'})));routeViews++;
 assert.equal(articleIds(html).length,0,'opposite calculator requirement excludes the exact new ID');
 html=render(await routeBank(bankArgs(c.collection,{difficulty:['medium','hard']})));routeViews++;
 containsOnly(html,q=>['medium','hard'].includes(q.difficulty),'difficulty multiselect OR');
 noPrivate(html);
 const other=rows.find(r=>r.subtopic!==q.subtopic);
 if(other){
  html=render(await routeBank(bankArgs(c.collection,{q:q.id,subtopic:other.subtopic})));routeViews++;
  assert.equal(articleIds(html).length,0,'an incompatible specific subtopic excludes the exact new ID');
 }
 html=render(await routeQuestion(detailArgs(q.id)));routeViews++;
 noPrivate(html);
 newTabLink(html,q.id);
 assert.equal(auth.at(-1),'/ib/questions/'+q.id);
 html=render(await routeScheme(detailArgs(q.id)));routeViews++;
 assert.ok(html.includes(solutionPrefix+q.id),'scheme includes this question worked solution');
 assert.ok(!html.includes(secretPrefix)&&!html.includes(summaryPrefix),'scheme keeps internal review metadata private');
 assert.match(html,/Worked solution &amp; mark allocation/);
 assert.equal(auth.at(-1),'/ib/mark-scheme/'+q.id);
}
for(const course of courses){
 const q=fixtures.find(q=>q.subject==='math-'+course);
 const html=render(await routeBank(bankArgs(q.collectionId,{q:solutionPrefix+q.id})));routeViews++;
 assert.equal(articleIds(html).length,0,'search excludes private solution text');
}

const blockedImports=[],blocked=ibHarness({questions:fixtures,useContentModule:true,user:null,onModule:name=>blockedImports.push(name)});
let blockedRoutes=0;
for(const course of courses){
 const q=fixtures.find(q=>q.subject==='math-'+course);
 for(const route of ['questions','mark-scheme']){
  const page=blocked.load(`app/ib/${route}/[id]/page.tsx`).default;
  await assert.rejects(()=>page(detailArgs(q.id)),/AUTH_REQUIRED/);blockedRoutes++;
 }
 const page=blocked.load('app/ib/question-bank/[collection]/page.tsx').default;
 await assert.rejects(()=>page(bankArgs(q.collectionId,{q:q.id})),/AUTH_REQUIRED/);blockedRoutes++;
}
assert.equal(blockedImports.filter(name=>legacyImport(name)||extraImport(name)).length,0,'authentication guard runs before a question bank is fetched');
const draft=structuredClone(fixtures[0]);
draft.id=draft.id.slice(0,-3)+'799';draft.number=799;draft.source.question=799;draft.status='draft';
const draftHarness=ibHarness({questions:[...fixtures,draft],useContentModule:true});
const draftContent=draftHarness.load('lib/ib/content.ts');
assert.equal(await draftContent.getIbQuestion(draft.id),undefined,'draft new content cannot resolve');
assert.equal((await draftContent.getIbQuestions()).length,400,'drafts excluded from all visible banks');

// Verify code-generated files without mutating source during a check.
const generationCheck=execFileSync(process.execPath,['--import','tsx','scripts/generate-ib-content-index.mjs','--check'],{encoding:'utf8',maxBuffer:1_000_000});
const report={
 status:'passed',method:'Real asynchronous content loading plus isolated production server-component routes; authentication mocked locally; no live student data.',
 canonicalSha256:fileHashes,questionsAdded:400,questionsResolved:400,courseResults,collectionResults,
 overview:{questionBodyImports:0,indexBytes:Buffer.byteLength(JSON.stringify(index)),noPromptDiagramOrSolutionFields:true},
 chunking:{originalMathsChunks:21,additionChunks:21,firstCollectionOriginalChunks:1,firstCollectionAdditionChunks:1,parallelCacheShared:true},
 frozenLegacy:{baseline,files:frozen.length,records:frozen},
 categoryCoverage:{questions:groupsChecked.length,records:groupsChecked},
 filters:{status:'passed',difficulty:true,calculator:true,specificSubtopic:true,studyCategory:true,responseStyle:true,multipleSelections:true,automaticFilterForm:true,loginQueryPreserved:true,records:filterChecks},
 routeViews,questionSchemeNewTab:true,privateCanaries:'Question/bank payloads exclude solution, answer summary and internal review metadata; schemes expose only worked solutions.',
 authentication:{unsignedRoutesRejected:blockedRoutes,questionBanksFetchedBeforeRejection:0,draftsHidden:true},
 fixtureAsyncLoader:{canonicalAdditions:400,visibleRecords:400,duplicateMerges:0},
 generatedFiles:generationCheck.trim(),
 limitations:['Isolated route checks do not measure network latency or execute browser checkbox events.','Live authenticated browser checks and deployment status are recorded separately by the release owner.']
};
mkdirSync('docs/ib-2026-maths',{recursive:true});
writeFileSync('docs/ib-2026-maths/portal-checks.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({status:'passed',questionsResolved:400,mathsCollections:collectionResults.length,courseTopics:20,filterCombinations:filterChecks.length,routeViews,authRoutes:blockedRoutes,overviewBodyImports:0,frozenLegacyFiles:frozen.length,report:'docs/ib-2026-maths/portal-checks.json'}));
