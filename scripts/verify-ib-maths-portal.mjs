import assert from 'node:assert/strict';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {ibHarness} from './ib-component-harness.mjs';

const source={document:'Independent syllabus-authored practice',question:1};
const base={id:'ib-aasl-na-001',subject:'math-aa-sl',topicId:'number-algebra',collectionId:'aa-sl-number-algebra',number:1,title:'A finite series',subtopic:'Sequences',syllabusCode:'1.2',level:'sl',examStyle:'short-response',difficulty:'easy',calculator:false,marks:2,stem:'Find the sum $3+6+9+\\cdots+30$.',parts:[],markScheme:[{part:'',steps:[{code:'M1',text:'Use $S_{10}=\\frac{10}{2}(3+30)$.'},{code:'A1',text:'MATHS-PRIVATE-ANSWER $165$.'}]}],source,verification:{method:'Synthetic fixture',notes:'MATHS-PRIVATE-REVIEW'},status:'published'};
const ai={...base,id:'ib-aisl-na-001',subject:'math-ai-sl',collectionId:'ai-sl-number-algebra',calculator:true,title:'Savings target',difficulty:'hard',examStyle:'extended-response'};
const second={...base,id:'ib-aasl-na-002',number:2,difficulty:'hard',calculator:true,examStyle:'extended-response',title:'A different sum',stem:'Find $2+4+6+\\cdots+40$.',source:{...source,question:2}};
const draft={...base,id:'ib-aasl-na-003',number:3,status:'draft',source:{...source,question:3}};
const calls=[];
const harness=ibHarness({questions:[base,ai,second,draft],onAuth:path=>calls.push(path)});
const catalog=harness.load('lib/ib/catalog.ts');
for(const item of [base,ai,second,draft]) assert.equal(harness.model.ibQuestionSchema.safeParse(item).success,true,item.id);
for(const bad of [{...ai,calculator:false},{...base,subject:'math-ai-sl'},{...base,level:'ahl'},{...base,syllabusCode:'3.1'},{...base,examStyle:'problem-solving'},{...base,collectionId:'number-algebra'}]) assert.equal(harness.model.ibQuestionSchema.safeParse(bad).success,false);
for(const subject of ['math-aa-sl','math-ai-sl','math-aa-hl']) {
  assert.equal(catalog.ibSubject(subject),subject);
  assert.equal(catalog.ibNavigationSubjects(subject).length,4);
  assert.equal(catalog.ibNavigationSubjects(subject)[0],subject);
  assert.equal(catalog.ibSubjectLabel(subject),'Maths');
}
assert.equal(catalog.ibQualification('math-aa-sl'),'Standard Level');
assert.equal(catalog.ibQualification('math-ai-sl'),'Standard Level');
assert.equal(catalog.ibQualification('math-aa-hl'),'Higher Level');
assert.equal(catalog.ibMathCourseHref('math-ai-sl','calculus'),'/ib/question-bank/ai-sl-calculus');
assert.equal(catalog.ibMathCourseHref('math-aa-hl','calculus'),'/ib/question-bank/calculus-1');
for(const [prefix,subject] of [['ib-aasl-','math-aa-sl'],['ib-aisl-','math-ai-sl'],['ib-aa-','math-aa-hl']]) {
  for(const route of ['questions','mark-scheme'])assert.equal(catalog.ibSubjectForPath(`/ib/${route}/${prefix}na-001`),subject);
}
const bank=harness.load('app/ib/question-bank/[collection]/page.tsx').default;
const question=harness.load('app/ib/questions/[id]/page.tsx').default;
const scheme=harness.load('app/ib/mark-scheme/[id]/page.tsx').default;
const request=(collection,query={})=>({params:Promise.resolve({collection}),searchParams:Promise.resolve(query)});
for(const item of [base,ai]) {
  let html=renderToStaticMarkup(await bank(request(item.collectionId)));
  assert.match(html,/aria-label="Mathematics course"/);
  assert.match(html,/AA SL/);assert.match(html,/AI SL/);assert.match(html,/AA HL/);
  assert.match(html,/target="_blank" rel="noopener noreferrer"/);
  assert.match(html,/difficultyBars/);assert.match(html,/Calculator|No calculator/);
  assert.doesNotMatch(html,/MATHS-PRIVATE|Question 3|Multiple-choice options|Video solution|AI feedback/);
  assert.match(html,item.subject==='math-ai-sl'?/use degrees for angles/:/Angles are in radians/);
  html=renderToStaticMarkup(await question({params:Promise.resolve({id:item.id})}));
  assert.doesNotMatch(html,/MATHS-PRIVATE/);
  assert.equal(calls.at(-1),`/ib/questions/${item.id}`);
  html=renderToStaticMarkup(await scheme({params:Promise.resolve({id:item.id})}));
  assert.match(html,/MATHS-PRIVATE-ANSWER/);assert.match(html,/Accept equivalent exact forms/);
  assert.doesNotMatch(html,/MATHS-PRIVATE-REVIEW/);
  assert.equal(calls.at(-1),`/ib/mark-scheme/${item.id}`);
  const prompt=harness.model.questionPrompt(item);
  for(const key of ['markScheme','source','verification','answerSummary','markSchemeDiagramSvg'])assert.ok(!(key in prompt));
}
let html=renderToStaticMarkup(await bank(request(base.collectionId,{difficulty:'hard',calculator:'yes'})));
assert.match(html,/Question 2/);assert.doesNotMatch(html,/Question 1/);
html=renderToStaticMarkup(await bank(request(base.collectionId,{style:'extended-response'})));
assert.match(html,/Question 2/);assert.doesNotMatch(html,/Question 1/);assert.match(calls.at(-1),/style=extended-response/);
html=renderToStaticMarkup(await bank(request(base.collectionId,{q:'MATHS-PRIVATE-ANSWER'})));
assert.match(html,/No questions match/);
const blocked=ibHarness({questions:[base,ai],user:null});
for(const item of [base,ai])for(const route of ['questions','mark-scheme'])await assert.rejects(()=>blocked.load(`app/ib/${route}/[id]/page.tsx`).default({params:Promise.resolve({id:item.id})}),/AUTH_REQUIRED/);
console.log('IB Maths portal passed: three distinct course routes, fixed SL/HL labels, calculator rules, topic-preserving course links, private solutions, authenticated deep links and separate written schemes. Synthetic fixtures only.');
