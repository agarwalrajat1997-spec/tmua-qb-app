import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import React from 'react';
import {renderToStaticMarkup as render} from 'react-dom/server';
import {ibHarness} from './ib-component-harness.mjs';
const banks=Object.fromEntries(['math-ai-hl','economics','business-management','physics-hl'].map(subject=>[subject,readdirSync('content/ib/'+subject).filter(f=>f.endsWith('.json')).flatMap(f=>JSON.parse(readFileSync(`content/ib/${subject}/${f}`,'utf8')))]));
const select=(subject,predicate)=>structuredClone(banks[subject].find(predicate));
const ai=select('math-ai-hl',q=>q.examStyle==='problem-solving');
const econSl=select('economics',q=>q.level==='sl'&&q.examStyle==='paper-2');
const econHl=select('economics',q=>q.examStyle==='paper-3'&&q.marks===30);
const bmSl=select('business-management',q=>q.level==='sl'&&q.examStyle==='paper-1');
const bmHl=select('business-management',q=>q.examStyle==='paper-3');
const physicsSl=select('physics-hl',q=>q.level==='core'&&q.number===201);
const physicsHl=select('physics-hl',q=>q.level==='ahl');
const questions=[ai,econSl,econHl,bmSl,bmHl,physicsSl,physicsHl];
for(const q of questions){assert.ok(q);q.markScheme[0].steps[0].text+=' EXPANSION-PRIVATE-SOLUTION-CANARY';q.verification.notes='EXPANSION-PRIVATE-VERIFICATION';}
const auth=[],h=ibHarness({questions,useContentModule:true,onAuth:destination=>auth.push(destination)}),catalog=h.load('lib/ib/catalog.ts'),content=h.load('lib/ib/content.ts');
const bank=h.load('app/ib/question-bank/[collection]/page.tsx').default,question=h.load('app/ib/questions/[id]/page.tsx').default,scheme=h.load('app/ib/mark-scheme/[id]/page.tsx').default;
const args=(q,course='hl',query={})=>({params:Promise.resolve({collection:q.collectionId}),searchParams:Promise.resolve({course,...query})});
const detail=(q,course)=>({params:Promise.resolve({id:q.id}),searchParams:Promise.resolve({course})});
for(const q of questions)assert.equal(h.model.ibQuestionSchema.safeParse(q).success,true,q.id);
assert.equal(catalog.IB_MATH_SUBJECTS.length,4);assert.equal(catalog.ibNavigationSubjects('math-ai-hl').length,6);
assert.equal(catalog.ibQualification('math-ai-hl'),'Higher Level');
assert.equal(catalog.ibMathCourseHref('math-ai-hl','calculus'),'/ib/question-bank/ai-hl-calculus');
assert.equal(catalog.ibSubjectForPath('/ib/mark-scheme/ib-aihl-sp-001'),'math-ai-hl');
for(const subject of ['physics-hl','economics','business-management']){
 assert.equal(catalog.ibHasCourseChoice(subject),true);
 assert.equal(catalog.ibQualification(subject,'sl'),'Standard Level');
 assert.match(catalog.ibHref(subject,'questions','sl'),/course=sl/);
 const sl=questions.find(q=>q.subject===subject&&q.level!=='ahl'),hl=questions.find(q=>q.subject===subject&&q.level==='ahl');
 assert.ok(content.getIbQuestion(sl.id,'sl'));assert.equal(content.getIbQuestion(hl.id,'sl'),undefined);
 assert.equal(content.getIbSummary('sl')[subject].questions,1);assert.equal(content.getIbSummary('hl')[subject].questions,2);
 let html=render(await bank(args(sl,'sl')));
 assert.match(html,/Standard Level/);assert.match(html,/name="course" value="sl"/);assert.match(html,/target="_blank" rel="noopener noreferrer"/);assert.match(html,/difficultyBars/);
 assert.doesNotMatch(html,/EXPANSION-PRIVATE|Video solution|AI feedback/);
 html=render(await question(detail(sl,'sl')));assert.doesNotMatch(html,/EXPANSION-PRIVATE/);
 html=render(await scheme(detail(sl,'sl')));assert.match(html,/EXPANSION-PRIVATE-SOLUTION-CANARY/);assert.doesNotMatch(html,/EXPANSION-PRIVATE-VERIFICATION/);
 assert.match(auth.at(-1),/course=sl/);
 for(const route of [question,scheme])await assert.rejects(()=>route(detail(hl,'sl')),/NOT_FOUND/);
 const prompt=h.model.questionPrompt(hl);assert.ok(!JSON.stringify(prompt).includes('EXPANSION-PRIVATE'));
}
let html=render(await bank(args(ai,'hl',{style:'problem-solving'})));
assert.match(html,/AI HL/);assert.match(html,/Problem solving/);assert.doesNotMatch(html,/EXPANSION-PRIVATE/);
html=render(await scheme(detail(bmHl,'hl')));
assert.match(html,/Indicative answer and reasoning/);assert.match(html,/17 marks/);assert.match(html,/<caption>A: Use of resource materials/);assert.match(html,/<caption>B:/);assert.match(html,/<caption>C:/);assert.match(html,/<caption>D:/);assert.doesNotMatch(html,/>IND</);
html=render(await scheme(detail(econHl,'hl')));assert.match(html,/Mark band|Marks/);assert.match(html,/Indicative answer and reasoning/);
for(const subject of ['economics','business-management']){
 const q=questions.find(q=>q.subject===subject&&q.level==='ahl');
 html=render(await bank(args(q,'hl',{style:'paper-3'})));assert.match(html,/Paper 3/);assert.match(auth.at(-1),/style=paper-3/);
 html=render(await bank(args(q,'sl',{style:'paper-3',level:'ahl'})));assert.doesNotMatch(html,/Additional HL<\/option>|EXPANSION-PRIVATE/);
}
assert.equal(h.model.ibQuestionSchema.safeParse({...bmSl,level:'ahl'}).success,false,'Business Paper 1 excludes AHL extensions');
const invalid=structuredClone(bmHl),group=invalid.markScheme.find(g=>g.rubric?.criteria);
group.rubric.criteria[0].maxMarks++;assert.equal(h.model.ibQuestionSchema.safeParse(invalid).success,false,'criterion maxima must sum to17');
const badBand=structuredClone(econHl),rubric=badBand.markScheme.find(g=>g.rubric?.bands)?.rubric;
assert.ok(rubric);rubric.bands[0].min=1;assert.equal(h.model.ibQuestionSchema.safeParse(badBand).success,false,'bands must include0');
for(const q of [ai,econSl,bmSl,physicsSl]){
 const blocked=ibHarness({questions:[q],user:null});
 for(const path of ['questions','mark-scheme'])await assert.rejects(()=>blocked.load(`app/ib/${path}/[id]/page.tsx`).default(detail(q,'sl')),/AUTH_REQUIRED/);
}
console.log('IB expansion portal passed: four Maths courses, six subjects; Physics/Economics/Business SL/HL counts and access boundaries; paper filters; protected deep links; private rubric content; validated best-fit/analytic allocations; separate written mark-scheme tabs. Local fixtures only.');
