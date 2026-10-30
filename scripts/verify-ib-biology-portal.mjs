import assert from 'node:assert/strict';
import React from 'react';
import {renderToStaticMarkup as render} from 'react-dom/server';
import {ibHarness} from './ib-component-harness.mjs';

// Route-level fixtures exercise actual components and the actual course-content module.
const shared={id:'ib-bio-a-001',subject:'biology',topicId:'unity-diversity',collectionId:'biology-unity-diversity',number:1,title:'Synthetic water test',subtopic:'Water',syllabusCode:'A1.1',level:'sl',questionType:'multiple-choice',difficulty:'easy',calculator:true,marks:1,stem:'Which property helps water buffer temperature changes?',parts:[],options:[{label:'A',text:'High specific heat capacity'},{label:'B',text:'No intermolecular attractions'},{label:'C',text:'No polarity'},{label:'D',text:'No thermal energy'}],correctOption:'A',markScheme:[{part:'',steps:[{code:'A1',text:'BIOLOGY-SOLUTION-CANARY A. Hydrogen bonding contributes to high specific heat capacity.'}]}],answerSummary:'PRIVATE-BIOLOGY-ANSWER',source:{document:'Independent syllabus-authored practice',question:1},verification:{method:'Synthetic fixture',notes:'PRIVATE-BIOLOGY-REVIEW'},status:'published'};
const ahl={...shared,id:'ib-bio-a-002',number:2,title:'Synthetic additional HL cells',subtopic:'Origins of cells',syllabusCode:'A2.1',level:'ahl',questionType:'structured',difficulty:'hard',marks:2,options:undefined,correctOption:undefined,markScheme:[{part:'',steps:[{code:'A1',text:'BIOLOGY-AHL-CANARY First independent point.'},{code:'R1',text:'Second independent point.'}]}],source:{...shared.source,question:2}};
const data={...ahl,id:'ib-bio-a-003',number:3,title:'Synthetic water dataset',subtopic:'Water',syllabusCode:'A1.1',level:'sl',questionType:'data-based',difficulty:'medium',source:{...shared.source,question:3}};
const draft={...shared,id:'ib-bio-a-004',number:4,status:'draft',source:{...shared.source,question:4}};
const seed=ibHarness(),catalog=seed.load('lib/ib/catalog.ts');
const collections=seed.model.IB_COLLECTIONS.filter(c=>c.subject==='biology');
assert.equal(collections.length,4);assert.equal(catalog.biologySyllabusSubtopics().length,40);assert.equal(catalog.biologySyllabusSubtopics(undefined,'sl').length,34);
assert.deepEqual(Array.from(catalog.biologySyllabusSubtopics().filter(s=>s.additionalHlOnly),s=>s.code),['A2.1','A2.3','A3.2','B3.3','C2.1','D2.2']);
assert.equal(catalog.ibHref('biology','questions','sl'),'/ib?subject=biology&view=questions&course=sl');
assert.equal(catalog.ibQualification('biology','sl'),'Standard Level');
assert.equal(catalog.ibCourseHref('/ib/questions/ib-bio-a-001?q=x','biology','sl'),'/ib/questions/ib-bio-a-001?q=x&course=sl');
const themes=collections.slice(1).map(c=>({...shared,id:`ib-bio-${c.code.toLowerCase()}-001`,topicId:c.topicId,collectionId:c.id,syllabusCode:c.code+'1.1',title:c.title}));
const questions=[shared,ahl,data,draft,...themes],auth=[];
const h=ibHarness({questions,useContentModule:true,onAuth:next=>auth.push(next)}),content=h.load('lib/ib/content.ts');
for(const q of questions)assert.equal(h.model.ibQuestionSchema.safeParse(q).success,true,q.id);
for(const q of [{...ahl,level:'sl'},{...shared,calculator:false},{...shared,id:'ib-bio-b-001'},{...shared,syllabusCode:'C1.1'},{...shared,level:'core'},{...shared,correctOption:undefined},{...shared,marks:2}])assert.equal(h.model.ibQuestionSchema.safeParse(q).success,false);
assert.equal(content.getIbSummary('hl').biology.questions,6);assert.equal(content.getIbSummary('sl').biology.questions,5);
assert.equal(content.getIbQuestion(ahl.id,'sl'),undefined);assert.equal(content.getIbQuestion(draft.id),undefined);
assert.equal(content.getIbQuestion(shared.id,'sl'),content.getIbQuestion(shared.id,'hl'));
const bank=h.load('app/ib/question-bank/[collection]/page.tsx').default;
const qpage=h.load('app/ib/questions/[id]/page.tsx').default,scheme=h.load('app/ib/mark-scheme/[id]/page.tsx').default;
const bankArgs=(query={},collection=shared.collectionId)=>({params:Promise.resolve({collection}),searchParams:Promise.resolve(query)});
const detail=(id,course='hl')=>({params:Promise.resolve({id}),searchParams:Promise.resolve({course})});
for(const course of ['sl','hl']){
 for(const c of collections){
  const html=render(await bank(bankArgs({course},c.id)));
  assert.match(html,new RegExp('IB BIOLOGY '+course.toUpperCase()));assert.match(html,/aria-label="Biology course"/);assert.match(html,/aria-label="Biology themes"/);
  assert.match(html,new RegExp('name="course" value="'+course+'"'));assert.match(html,/calculator may be used for every question/);
  assert.doesNotMatch(html,/BIOLOGY-SOLUTION-CANARY|BIOLOGY-AHL-CANARY|PRIVATE-BIOLOGY|Video solution|AI feedback/);
 }
 let html=render(await qpage(detail(shared.id,course)));
 assert.match(html,/target="_blank" rel="noopener noreferrer"/);assert.match(html,new RegExp('/ib/mark-scheme/ib-bio-a-001\\?course='+course));
 assert.doesNotMatch(html,/BIOLOGY-SOLUTION-CANARY|PRIVATE-BIOLOGY/);
 html=render(await scheme(detail(shared.id,course)));assert.match(html,/BIOLOGY-SOLUTION-CANARY/);assert.match(html,/biology behind the choice/);assert.doesNotMatch(html,/PRIVATE-BIOLOGY/);
 assert.equal(auth.at(-1),`/ib/mark-scheme/${shared.id}?course=${course}`);
 const overview=ibHarness({questions,useContentModule:true,query:'subject=biology&course='+course});
 html=render(React.createElement(overview.load('app/ib/IBPortalClient.tsx').default,{email:'review@example.invalid',summary:content.getIbSummary(course)}));
 assert.match(html,new RegExp('<strong>'+(course==='sl'?5:6)+'</strong><span>Questions available'));
 assert.equal((html.match(/\?syllabus=/g)||[]).length,course==='sl'?34:40);
}
let html=render(await bank(bankArgs({course:'hl',level:'ahl',difficulty:'hard',syllabus:'A2.1'})));
assert.match(html,/id="ib-bio-a-002"/);assert.doesNotMatch(html,/id="ib-bio-a-001"/);
html=render(await bank(bankArgs({course:'sl',level:'ahl',syllabus:'A2.1',type:'forged'})));
assert.doesNotMatch(html,/id="ib-bio-a-002"|Additional HL<\/option>/);assert.match(html,/All SL content/);
html=render(await bank(bankArgs({course:'hl',q:'BIOLOGY-SOLUTION-CANARY'})));assert.match(html,/No matching questions/);
for(const route of [qpage,scheme]){
 await assert.rejects(()=>route(detail(ahl.id,'sl')),/NOT_FOUND/);
 await assert.rejects(()=>route(detail(draft.id)),/NOT_FOUND/);
 await assert.rejects(()=>route(detail('ib-bio-a-999')),/NOT_FOUND/);
 html=render(await route(detail(ahl.id)));assert.match(html,/Additional HL/);assert.match(html,/href="\/ib\/question-bank\/biology-unity-diversity\?course=sl"/);
}
const blocked=ibHarness({questions,useContentModule:true,user:null,onAuth:next=>auth.push(next)});
for(const route of ['app/ib/questions/[id]/page.tsx','app/ib/mark-scheme/[id]/page.tsx']){
 await assert.rejects(()=>blocked.load(route).default(detail(ahl.id,'sl')),/AUTH_REQUIRED/);
 assert.match(auth.at(-1),/ib-bio-a-002\?course=sl$/);
}
const many=Array.from({length:10},(_,i)=>({...shared,id:`ib-bio-a-${String(i+1).padStart(3,'0')}`,number:i+1,source:{...shared.source,question:i+1}}));
const paging=ibHarness({questions:many,useContentModule:true}).load('app/ib/question-bank/[collection]/page.tsx').default;
html=render(await paging(bankArgs({course:'sl',syllabus:'A1.1',type:'multiple-choice'})));assert.match(html,/Page 1 of 2/);assert.match(html,/course=sl&amp;syllabus=A1.1&amp;type=multiple-choice&amp;page=2/);
html=render(await paging(bankArgs({course:'sl',page:'999'})));assert.match(html,/Page 2 of 2/);
for(const pathname of ['/ib/question-bank/biology-unity-diversity','/ib/questions/ib-bio-a-001','/ib/mark-scheme/ib-bio-a-001']){
 assert.equal(catalog.ibSubjectForPath(pathname),'biology');
 const login=ibHarness({query:'next='+encodeURIComponent(pathname+'?course=sl')}).load('app/ib-login/IBLoginClient.tsx').default;
 html=render(React.createElement(login));assert.match(html,/STANDARD LEVEL/);assert.match(html,/aria-label="Biology course"/);
}
const publicQ=h.model.questionPrompt({...shared,diagramCaption:'Public illustration credit',markSchemeDiagramCaption:'PRIVATE-SOLUTION-CAPTION'});
assert.equal(publicQ.diagramCaption,'Public illustration credit');
for(const hidden of ['markScheme','markSchemeDiagramSvg','markSchemeDiagramUrl','markSchemeDiagramCaption','correctOption','source','verification','answerSummary'])assert.equal(hidden in publicQ,false,hidden);
const Image=h.load('app/ib/components/DiagramImage.tsx').default;
const raster=Image({src:'https://media.thrivingscholars.com/synthetic.png',fallback:'/ib-assets/biology/synthetic.png',caption:'Synthetic fallback check'});
let resolvedSrc=raster.props.src,requests=0;
const target={baseURI:'https://apps.thrivingscholars.com/ib/questions/synthetic',get src(){return resolvedSrc;},set src(value){requests++;resolvedSrc=new URL(value,this.baseURI).href;}};
raster.props.onError({currentTarget:target});raster.props.onError({currentTarget:target});
assert.equal(requests,1,'A failed relative raster fallback must not trigger an endless retry');
assert.equal(resolvedSrc,'https://apps.thrivingscholars.com/ib-assets/biology/synthetic.png');
console.log('IB Biology portal passed: four themes, 40 HL / 34 SL subtopics, canonical shared records, AHL denial in SL, authenticated routes, course-preserving filters and pagination, written schemes in separate tabs, private solution separation and Biology sign-in returns.');
