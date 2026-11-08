import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {renderToStaticMarkup as render} from 'react-dom/server';
import {parseDocument} from 'htmlparser2';
import {ibHarness} from './ib-component-harness.mjs';

const seed=ibHarness(),model=seed.model,catalog=seed.load('lib/ib/catalog.ts'),psychology=seed.load('lib/ib/psychology-catalog.ts');
const svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 180"><rect x="20" y="40" width="180" height="90" fill="white" stroke="black"/><text x="30" y="85">SIMULATED DESIGN STIMULUS</text></svg>';
function fixture(section,number=1,topicId=section.startsWith('p3-')?'culture':'biological-approach') {
  const topic=psychology.psychologyTopic(topicId),spec=psychology.PSYCHOLOGY_SECTIONS[section];
  return {id:`ib-psy-${topic.token}-${String(number).padStart(3,'0')}`,subject:'psychology',firstAssessment:2027,topicId,collectionId:`psychology-${topicId}`,number,title:`Synthetic review fixture ${number}`,subtopic:topic.subtopics[0].title,syllabusCode:topic.subtopics[0].code,level:topic.additionalHlOnly?'ahl':'sl',difficulty:number%2?'medium':'hard',calculator:false,marks:spec.marks,examStyle:spec.paper,examSection:section,questionType:spec.questionType,context:section==='p1-a'?'general':'health-wellbeing',concepts:['bias','responsibility'],stem:`Explain the methodological choice in synthetic fixture ${number}. This is a simulated practice stimulus.`,parts:[],diagramSvg:svg,markSchemeDiagramSvg:svg.replace('SIMULATED DESIGN STIMULUS','PRIVATE-SCHEME-DIAGRAM'),markScheme:[{part:'',steps:[{code:'IND',text:'PRIVATE-SOLUTION: discuss the specific control, its explanation and an alternative interpretation.'}],rubric:{maxMarks:spec.marks,bands:psychology.PSYCHOLOGY_BAND_RANGES[spec.marks].map(([min,max])=>({min,max,descriptor:min===0?'No relevant response.':'Apply relevant knowledge and explain the judgement in the stated context.'}))}}],answerSummary:'PRIVATE-ANSWER',source:{document:'Independent syllabus-authored practice',question:number},verification:{method:'Synthetic fixture only',notes:'PRIVATE-VERIFICATION'},status:'published'};
}
const sections=Object.keys(psychology.PSYCHOLOGY_SECTIONS),questions=sections.map((s,i)=>fixture(s,i+1));
questions.push(...Array.from({length:12},(_,i)=>fixture(i%2?'p1-b':'p1-a',i+20)));
for(const q of questions)assert.equal(model.ibQuestionSchema.safeParse(q).success,true,q.id);
const base=fixture('p1-a');
let negativeChecks=0;
function invalid(mutator,label){const q=structuredClone(base);mutator(q);assert.equal(model.ibQuestionSchema.safeParse(q).success,false,label);negativeChecks++;}
invalid(q=>q.firstAssessment=2026,'reject earlier cohort');
invalid(q=>q.subject='psychology-hl','one subject with course selection');
invalid(q=>q.id='ib-psy-bio-002','identity and number agree');
invalid(q=>q.source.question=2,'source mapping agrees');
invalid(q=>q.collectionId='psychology-culture','collection belongs to topic');
invalid(q=>q.syllabusCode='CUL.01','content code belongs to topic');
invalid(q=>q.subtopic='Not the mapped content area','exact mapped title');
invalid(q=>q.level='ahl','shared section is not AHL');
invalid(q=>q.examStyle='paper-3','section determines paper');
invalid(q=>q.examSection='p1-b','section determines marks/type/context');
invalid(q=>q.questionType='data-response','section determines response type');
invalid(q=>q.marks=6,'section determines marks');
invalid(q=>q.calculator=true,'no unsubstantiated calculator policy');
invalid(q=>q.difficulty='easy','medium and hard only');
invalid(q=>q.context='health-wellbeing','P1A general context');
invalid(q=>q.concepts=['bias','bias'],'unique concepts');
invalid(q=>q.concepts=[],'at least one concept');
invalid(q=>q.parts=[{label:'a',marks:4,prompt:'A new part'}],'individual unparted practice items');
invalid(q=>q.markScheme[0].steps[0].code='A1','holistic indicative content only');
invalid(q=>delete q.markScheme[0].rubric,'rubric required');
invalid(q=>q.markScheme[0].rubric.bands[0].min=1,'bands include zero');
invalid(q=>q.markScheme[0].rubric.bands[1].min=0,'bands do not overlap');
invalid(q=>q.markScheme[0].rubric.maxMarks=5,'rubric allocation agrees');
invalid(q=>q.markScheme[0].rubric.bands=[{min:0,max:0,descriptor:'No answer'},{min:1,max:4,descriptor:'One contiguous but incorrect band'}],'authentic boundaries, not merely contiguous coverage');
invalid(q=>{delete q.markScheme[0].rubric.bands;q.markScheme[0].rubric.criteria=[{id:'A',title:'Analytic',maxMarks:4,bands:[{min:0,max:0,descriptor:'None'},{min:1,max:4,descriptor:'Relevant'}]}];},'best-fit bands rather than analytic criteria');
invalid(q=>q.diagramSvg='<svg viewBox="0 0 10 10"><script>alert(1)</script></svg>','noninteractive SVG only');
for(const section of ['p1-b','p2-b','p3-data']){const q=fixture(section);q.context='general';assert.equal(model.ibQuestionSchema.safeParse(q).success,false,'general is exclusive to P1A');negativeChecks++;}

const auth=[],h=ibHarness({questions,onAuth:destination=>auth.push(destination)});
const bank=h.load('app/ib/question-bank/[collection]/page.tsx').default,detail=h.load('app/ib/questions/[id]/page.tsx').default,scheme=h.load('app/ib/mark-scheme/[id]/page.tsx').default;
const listArgs=(collection,query={})=>({params:Promise.resolve({collection}),searchParams:Promise.resolve(query)});
const detailArgs=(q,course='hl')=>({params:Promise.resolve({id:q.id}),searchParams:Promise.resolve({course})});
function elements(html,predicate){const found=[];function visit(node){if(predicate(node))found.push(node);for(const child of node.children??[])visit(child);}visit(parseDocument(html));return found;}
const ids=html=>elements(html,n=>n.name==='article'&&n.attribs.class==='questionCard').map(n=>n.attribs.id);
assert.equal(catalog.ibSubject('psychology'),'psychology');
assert.equal(catalog.ibSubject('psychology-hl'),'math-aa-hl');
assert.equal(catalog.ibHasCourseChoice('psychology'),true);
assert.equal(catalog.ibNavigationSubjects('psychology').at(-1),'psychology');
assert.equal(catalog.ibTopicsForCourse('psychology','sl').length,4);
assert.equal(catalog.ibTopicsForCourse('psychology','hl').length,7);
assert.equal(catalog.ibSyllabusSubtopics('psychology',undefined,'sl').length,35);
assert.equal(catalog.ibSyllabusSubtopics('psychology',undefined,'hl').length,47);
assert.equal(catalog.ibSubjectForPath('/ib/mark-scheme/ib-psy-cul-001'),'psychology');
assert.equal(catalog.ibSubjectForPath('/ib/question-bank/psychology-culture'),'psychology');
assert.match(catalog.ibHref('psychology','questions','sl'),/subject=psychology.*course=sl/);
const index=h.load('lib/ib/build-content-index.ts').buildIbContentIndex(questions);
assert.equal(index.summaries.sl.psychology.collections.length,4);
assert.equal(index.summaries.hl.psychology.collections.length,7);
assert.equal(index.summaries.sl.psychology.questions,questions.filter(q=>q.level==='sl').length);
assert.equal(index.summaries.hl.psychology.questions,questions.length);
const PsychologyMocks=h.load('app/ib/components/PsychologyMockList.tsx').default;
for(const [course,total] of [['sl',4],['hl',6]]){
  assert.equal(index.summaries[course].psychology.mocks,total);
  const page=render(PsychologyMocks({course}));
  const links=elements(page,n=>n.name==='a'&&n.attribs.href?.startsWith('/ib/psychology-mocks/'));
  assert.equal(links.length,total);
  assert(links.every(n=>catalog.ibSubjectForPath(n.attribs.href)==='psychology'));
  assert.equal(elements(page,n=>n.name==='a'&&n.attribs.href?.endsWith('-resources.pdf')).length,course==='hl'?2:0);
}
for(const q of questions){const prompt=model.questionPrompt(q);for(const key of ['markScheme','markSchemeDiagramSvg','answerSummary','verification','source'])assert.ok(!(key in prompt));assert.equal(prompt.firstAssessment,2027);assert.equal(prompt.examSection,q.examSection);}
let html=render(await bank(listArgs(base.collectionId,{course:'sl'})));
assert.match(html,/First assessment 2027/);assert.match(html,/Content areas/);assert.match(html,/No calculator needed/);assert.match(html,/not official IB syllabus numbering/);
assert.doesNotMatch(html,/PRIVATE-|Apply filters|Calculator may be used|radians/);
assert.equal(elements(html,n=>n.name==='a'&&n.attribs.href?.includes('/ib/question-bank/psychology-culture')).length,0,'SL navigation hides HL extension collections');
assert.match(html,/Response type/);assert.match(html,/Exam paper/);
html=render(await bank(listArgs(base.collectionId,{course:'sl',difficulty:'hard',style:'paper-1',type:'scenario-response'})));
const wanted=questions.filter(q=>q.collectionId===base.collectionId&&q.difficulty==='hard'&&q.examStyle==='paper-1'&&q.questionType==='scenario-response');
assert.deepEqual(ids(html),wanted.slice(0,8).map(q=>q.id));
assert.match(auth.at(-1),/course=sl/);assert.match(auth.at(-1),/type=scenario-response/);
html=render(await bank(listArgs(base.collectionId,{course:'sl',page:'2'})));
assert.deepEqual(ids(html),questions.filter(q=>q.collectionId===base.collectionId).slice(8,16).map(q=>q.id),'pagination uses eight questions');
for(const q of [questions[0],questions.find(q=>q.level==='ahl')]){
  html=render(await detail(detailArgs(q)));assert.doesNotMatch(html,/PRIVATE-/);assert.match(html,/First assessment 2027/);
  html=render(await scheme(detailArgs(q)));assert.match(html,/PRIVATE-SOLUTION/);assert.doesNotMatch(html,/PRIVATE-VERIFICATION|>IND</);assert.match(html,/Holistic best-fit bands/);assert.match(html,/Best-fit mark bands/);
}
const ahl=questions.find(q=>q.level==='ahl');
for(const route of [detail,scheme])await assert.rejects(()=>route(detailArgs(ahl,'sl')),/NOT_FOUND/);
html=render(await bank(listArgs(ahl.collectionId,{course:'sl',level:'ahl',style:'paper-3'})));assert.equal(ids(html).length,0);assert.doesNotMatch(html,/PRIVATE-/);
const blocked=ibHarness({questions,user:null});
await assert.rejects(()=>blocked.load('app/ib/question-bank/[collection]/page.tsx').default(listArgs(base.collectionId,{course:'sl',difficulty:['medium','hard']})),/AUTH_REQUIRED/);
for(const path of ['questions','mark-scheme'])await assert.rejects(()=>blocked.load(`app/ib/${path}/[id]/page.tsx`).default(detailArgs(base,'sl')),/AUTH_REQUIRED/);
assert.match(readFileSync('lib/ib/auth.ts','utf8'),/access !== "active"/,'same current access guard as every bank route');
assert.match(readFileSync('scripts/generate-ib-content-index.mjs','utf8'),/IB_COLLECTIONS\.map/,'the ordinary metadata generator includes the new collections');
console.log(JSON.stringify({status:'passed',schemaSections:sections.length,negativeChecks,fixtureQuestions:questions.length,checks:'2027 cohort, authentic section/type/mark/level rules, holistic bands, private solutions, course isolation, hidden SL extension navigation, paper/type/difficulty auto filters, pagination and authenticated deep links; no live writes'}));
