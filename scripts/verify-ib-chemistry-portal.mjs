import assert from 'node:assert/strict';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { ibHarness } from './ib-component-harness.mjs';

// Fixtures exercise the real content module and authenticated components, without live accounts or messages.
const chemistry={id:'ib-chem-s1-001',subject:'chemistry',topicId:'structure-1',collectionId:'chemistry-structure-1',number:1,title:'Synthetic helium atom',subtopic:'The nuclear atom',syllabusCode:'S1.2',level:'sl',questionType:'multiple-choice',difficulty:'easy',calculator:true,marks:1,stem:'A neutral helium atom has two protons. How many electrons does it contain?',parts:[],options:[{label:'A',text:'One'},{label:'B',text:'Two'},{label:'C',text:'Three'},{label:'D',text:'Four'}],correctOption:'B',markScheme:[{part:'',steps:[{code:'A1',text:'CHEMISTRY-SOLUTION-CANARY B. A neutral atom contains equal numbers of protons and electrons.'}]}],source:{document:'Independent syllabus-authored practice',question:1},verification:{method:'Synthetic route fixture',notes:'PRIVATE-CHEMISTRY-VERIFICATION'},answerSummary:'PRIVATE-CHEMISTRY-ANSWER',status:'published'};
const ahl={...chemistry,id:'ib-chem-s1-002',number:2,title:'Synthetic additional HL',subtopic:'Electron configurations',syllabusCode:'S1.3',level:'ahl',questionType:'structured',difficulty:'hard',options:undefined,correctOption:undefined,marks:2,markScheme:[{part:'',steps:[{code:'M1',text:'CHEMISTRY-AHL-METHOD'},{code:'A1',text:'CHEMISTRY-AHL-ANSWER'}]}],source:{...chemistry.source,question:2}};
const dataBased={...ahl,id:'ib-chem-s1-003',number:3,title:'Synthetic data response',syllabusCode:'S1.2',subtopic:'The nuclear atom',level:'sl',questionType:'data-based',difficulty:'medium',source:{...chemistry.source,question:3}};
const draft={...chemistry,id:'ib-chem-s1-004',number:4,status:'draft',source:{...chemistry.source,question:4}};
const seed=ibHarness();
const catalog=seed.load('lib/ib/catalog.ts');
const collections=seed.model.IB_COLLECTIONS.filter(c=>c.subject==='chemistry');
assert.equal(collections.length,6);
assert.equal(catalog.chemistrySyllabusSubtopics().length,22);
assert.equal(catalog.chemistrySyllabusSubtopics(undefined,'sl').length,21);
assert.deepEqual(Array.from(catalog.chemistrySyllabusSubtopics().filter(s=>s.additionalHlOnly),s=>s.code),['R1.4']);
assert.equal(catalog.ibSubject('chemistry'),'chemistry');
assert.equal(catalog.ibCourseLevel(undefined),'hl');
assert.equal(catalog.ibCourseLevel('forged'),'hl');
assert.equal(catalog.ibCourseLevel('sl'),'sl');
assert.equal(catalog.ibHref('physics-hl'),'/ib?subject=physics-hl&view=questions');
assert.equal(catalog.ibHref('math-aa-hl'),'/ib?subject=math-aa-hl&view=questions');
assert.equal(catalog.ibHref('chemistry','questions','sl'),'/ib?subject=chemistry&view=questions&course=sl');
assert.equal(catalog.ibCourseHref('/ib/question-bank/chemistry-structure-1?syllabus=S1.2','chemistry','sl'),'/ib/question-bank/chemistry-structure-1?syllabus=S1.2&course=sl');
const themes=collections.slice(1).map(c=>({...chemistry,id:'ib-chem-'+c.code.toLowerCase()+'-001',topicId:c.topicId,collectionId:c.id,syllabusCode:c.code+'.1',title:c.title}));
const entropy={...ahl,id:'ib-chem-r1-002',topicId:'reactivity-1',collectionId:'chemistry-reactivity-1',syllabusCode:'R1.4',subtopic:'Entropy and spontaneity'};
const questions=[chemistry,ahl,dataBased,draft,...themes,entropy];
const authCalls=[];
const harness=ibHarness({questions,useContentModule:true,onAuth:next=>authCalls.push(next)});
const content=harness.load('lib/ib/content.ts');
const bank=harness.load('app/ib/question-bank/[collection]/page.tsx').default;
const questionPage=harness.load('app/ib/questions/[id]/page.tsx').default;
const schemePage=harness.load('app/ib/mark-scheme/[id]/page.tsx').default;
const bankRequest=(query={},collection=chemistry.collectionId)=>({params:Promise.resolve({collection}),searchParams:Promise.resolve(query)});
const detailRequest=(id,course)=>({params:Promise.resolve({id}),searchParams:Promise.resolve(course?{course}:{})});
assert.equal(content.getIbSummary('hl').chemistry.questions,9);
assert.equal(content.getIbSummary('sl').chemistry.questions,7);
assert.equal(content.getIbQuestions(chemistry.collectionId,'hl').length,3);
assert.equal(content.getIbQuestions(chemistry.collectionId,'sl').length,2);
assert.equal(content.getIbQuestion(ahl.id,'sl'),undefined);
assert.equal(content.getIbQuestion(chemistry.id,'sl'),content.getIbQuestion(chemistry.id,'hl'));
assert.equal(content.getIbQuestion(draft.id),undefined);
const slR1=content.getIbSummary('sl').chemistry.collections.find(c=>c.id==='chemistry-reactivity-1');
assert.equal(slR1.count,1);
assert.equal(slR1.syllabus.length,3);
assert.ok(!slR1.syllabus.some(s=>s.code==='R1.4'));
for(const fixture of questions)assert.equal(harness.model.ibQuestionSchema.safeParse(fixture).success,true,fixture.id);
for(const bad of [
  {...chemistry,level:'core'},{...chemistry,level:'hl'},{...chemistry,calculator:false},
  {...chemistry,syllabusCode:'R1.2'},{...chemistry,topicId:'structure-2'},
  {...chemistry,id:'ib-chem-s2-001'},{...chemistry,collectionId:'number-algebra'},
  {...chemistry,marks:2},{...chemistry,correctOption:undefined},{...chemistry,options:chemistry.options.slice(0,3)},
  {...chemistry,options:chemistry.options.map(o=>({...o,label:'A'}))},{...ahl,options:chemistry.options},
  {...entropy,level:'sl'},{...chemistry,source:{...chemistry.source,document:'Copied source'}},
])assert.equal(harness.model.ibQuestionSchema.safeParse(bad).success,false,JSON.stringify(bad));
const prompt=harness.model.questionPrompt(chemistry);
for(const hidden of ['markScheme','markSchemeDiagramSvg','markSchemeDiagramUrl','answerSummary','source','verification','correctOption'])assert.equal(hidden in prompt,false,hidden);

let html;
for(const collection of collections){
  html=renderToStaticMarkup(await bank(bankRequest({course:'sl'},collection.id)));
  assert.match(html,/IB CHEMISTRY SL/);assert.match(html,/aria-label="Chemistry themes"/);assert.match(html,/aria-label="Chemistry course"/);
  assert.match(html,/aria-current="page" href="\/ib\?subject=chemistry&amp;view=questions&amp;course=sl"/);
  assert.match(html,/name="course" value="sl"/);assert.match(html,/calculator may be used for every question/);
  assert.match(html,/SL content/);assert.match(html,/Difficulty: /);assert.match(html,/class="difficultyBars" aria-hidden="true"/);
  assert.match(html,/target="_blank" rel="noopener noreferrer"/);
  assert.doesNotMatch(html,/CHEMISTRY-SOLUTION-CANARY|CHEMISTRY-AHL-ANSWER|PRIVATE-CHEMISTRY|Independent syllabus-authored practice|Angles are in radians|9\.81|Video|AI Feedback/);
}
html=renderToStaticMarkup(await bank(bankRequest({course:'sl'})));
assert.match(html,/Question 1</);assert.match(html,/Question 3</);assert.doesNotMatch(html,/Question 2<|Question 4</);
assert.match(html,/href="\/ib\/questions\/ib-chem-s1-001\?course=sl"/);
assert.match(html,/href="\/ib\/mark-scheme\/ib-chem-s1-001\?course=sl"/);
assert.match(html,/class="reset" href="\/ib\/question-bank\/chemistry-structure-1\?course=sl"/);
html=renderToStaticMarkup(await bank(bankRequest({course:'hl',level:'ahl',type:'structured',syllabus:'S1.3',difficulty:'hard'})));
assert.match(html,/Question 2</);assert.doesNotMatch(html,/Question 1<|Question 3</);assert.match(authCalls.at(-1),/course=hl/);
html=renderToStaticMarkup(await bank(bankRequest({course:'sl',level:'ahl',syllabus:'R1.4'},'chemistry-reactivity-1')));
assert.doesNotMatch(html,/R1\.4|Question 2</);assert.match(html,/Question 1</);
html=renderToStaticMarkup(await bank(bankRequest({course:'sl',q:'CHEMISTRY-SOLUTION-CANARY'})));
assert.match(html,/No questions match these filters/);

for(const course of ['sl','hl']){
  html=renderToStaticMarkup(await questionPage(detailRequest(chemistry.id,course)));
  assert.match(html,/Multiple-choice options/);assert.match(html,/SL content/);assert.match(html,new RegExp('href="/ib/mark-scheme/ib-chem-s1-001\\?course='+course+'"'));
  assert.doesNotMatch(html,/CHEMISTRY-SOLUTION-CANARY|PRIVATE-CHEMISTRY/);
  html=renderToStaticMarkup(await schemePage(detailRequest(chemistry.id,course)));
  assert.match(html,/CHEMISTRY-SOLUTION-CANARY/);assert.match(html,/Total <strong>1 mark/);assert.match(html,/chemistry behind the choice/);
  assert.doesNotMatch(html,/PRIVATE-CHEMISTRY|Independent syllabus-authored practice/);
  assert.match(authCalls.at(-1),new RegExp('/ib/mark-scheme/ib-chem-s1-001\\?course='+course));
}
for(const route of [questionPage,schemePage]){
  await assert.rejects(()=>route(detailRequest(ahl.id,'sl')),/NOT_FOUND/);
  await assert.rejects(()=>route(detailRequest(entropy.id,'sl')),/NOT_FOUND/);
  await assert.rejects(()=>route(detailRequest(draft.id,'hl')),/NOT_FOUND/);
  await assert.rejects(()=>route(detailRequest('ib-chem-s1-999','hl')),/NOT_FOUND/);
  html=renderToStaticMarkup(await route(detailRequest(ahl.id,'hl')));assert.match(html,/Additional HL/);
  html=renderToStaticMarkup(await route(detailRequest(ahl.id)));assert.match(html,/Additional HL/);
  assert.match(html,/href="\/ib\/question-bank\/chemistry-structure-1\?course=sl"/);
}
const blocked=ibHarness({questions,useContentModule:true,user:null,onAuth:next=>authCalls.push(next)});
for(const route of ['app/ib/questions/[id]/page.tsx','app/ib/mark-scheme/[id]/page.tsx']){
  await assert.rejects(()=>blocked.load(route).default(detailRequest(ahl.id,'sl')),/AUTH_REQUIRED/);
  assert.match(authCalls.at(-1),/ib-chem-s1-002\?course=sl$/);
}
await assert.rejects(()=>blocked.load('app/ib/question-bank/[collection]/page.tsx').default(bankRequest({course:'sl',syllabus:'S1.2',type:'multiple-choice'})),/AUTH_REQUIRED/);
assert.match(authCalls.at(-1),/course=sl/);

const many=Array.from({length:10},(_,index)=>({...chemistry,id:'ib-chem-s1-'+String(index+1).padStart(3,'0'),number:index+1,source:{...chemistry.source,question:index+1}}));
const paging=ibHarness({questions:many,useContentModule:true}).load('app/ib/question-bank/[collection]/page.tsx').default;
html=renderToStaticMarkup(await paging(bankRequest({course:'sl',syllabus:'S1.2',level:'sl',type:'multiple-choice'})));
assert.match(html,/Page 1 of 2/);assert.match(html,/course=sl&amp;syllabus=S1.2&amp;level=sl&amp;type=multiple-choice&amp;page=2/);
html=renderToStaticMarkup(await paging(bankRequest({course:'sl',page:'999'})));
assert.match(html,/Page 2 of 2/);assert.match(html,/Question 10</);

for(const course of ['sl','hl']){
  const overviewHarness=ibHarness({questions,useContentModule:true,query:'subject=chemistry&course='+course});
  const overview=overviewHarness.load('app/ib/IBPortalClient.tsx').default;
  const summary=content.getIbSummary(course);
  html=renderToStaticMarkup(React.createElement(overview,{email:'review@example.invalid',summary}));
  for(const collection of collections)assert.ok(html.includes('href="/ib/question-bank/'+collection.id+'?course='+course+'"'));
  assert.equal((html.match(/\?syllabus=/g)||[]).length,course==='sl'?21:22);
  assert.match(html,new RegExp('IB CHEMISTRY '+course.toUpperCase()));
  assert.match(html,course==='sl'?/STANDARD LEVEL/:/HIGHER LEVEL/);
  assert.match(html,new RegExp('<strong>'+(course==='sl'?7:9)+'</strong><span>Questions available'));
  const portalPage=overviewHarness.load('app/ib/page.tsx').default;
  html=renderToStaticMarkup(await portalPage({searchParams:Promise.resolve({subject:'chemistry',course})}));
  assert.match(html,new RegExp('<strong>'+(course==='sl'?7:9)+'</strong><span>Questions available'));
}
const destinations=[];
const blockedPortal=ibHarness({questions,useContentModule:true,user:null,onDestination:url=>destinations.push(url)}).load('app/ib/page.tsx').default;
await assert.rejects(()=>blockedPortal({searchParams:Promise.resolve({subject:'chemistry',course:'sl',view:'questions'})}),/REDIRECT/);
assert.equal(destinations.at(-1),'/ib-login?next='+encodeURIComponent('/ib?subject=chemistry&view=questions&course=sl'));
for(const path of ['/ib/question-bank/chemistry-structure-1','/ib/questions/ib-chem-s1-001','/ib/mark-scheme/ib-chem-s1-001']){
  assert.equal(catalog.ibSubjectForPath(path),'chemistry');
  const login=ibHarness({query:'next='+encodeURIComponent(path+'?course=sl')}).load('app/ib-login/IBLoginClient.tsx').default;
  html=renderToStaticMarkup(React.createElement(login));
  assert.match(html,/STANDARD LEVEL/);assert.match(html,/aria-label="Chemistry course"/);
  assert.match(html,/aria-current="page" class="subjectActive"[^>]*>.*Chemistry/);
  assert.doesNotMatch(html,/Physics content coming soon|Both IB subjects/);
}
console.log('IB Chemistry portal passed: six themes and 22 syllabus destinations; real per-course counts; shared SL/HL records; authenticated AHL denial in SL mode; course-preserving filters, pagination and sign-in returns; private answer separation; written-only schemes; accessible course controls. Synthetic fixtures only; no emails or database writes.');
