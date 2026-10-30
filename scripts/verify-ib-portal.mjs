import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { ibHarness } from './ib-component-harness.mjs';
import './verify-ib-chemistry-portal.mjs';

const base={id:'ib-aa-na-001',subject:'math-aa-hl',topicId:'number-algebra',collectionId:'number-algebra',number:1,title:'Expand a binomial',subtopic:'Binomial theorem',difficulty:'easy',calculator:false,marks:2,stem:'Expand $(x+3)^2$.',parts:[],markScheme:[{part:'',steps:[{code:'M1',text:'Use the binomial theorem.'},{code:'A1',text:'SECRET-SOLUTION-CANARY $x^2+6x+9$.'}]}],source:{document:'Synthetic test only',question:1},verification:{method:'symbolic',notes:'Synthetic fixture'},status:'published'};
const other={...base,id:'ib-aa-na-002',number:2,title:'A logarithm',subtopic:'Logarithms',difficulty:'hard',calculator:true,stem:'Find $\\log_3 7$.',source:{...base.source,question:2}};
const draft={...base,id:'ib-aa-na-003',number:3,status:'draft',source:{...base.source,question:3}};
const authCalls=[];
const harness=ibHarness({questions:[base,other,draft],onAuth:next=>authCalls.push(next)});
const page=harness.load('app/ib/question-bank/[collection]/page.tsx').default;
const questionPage=harness.load('app/ib/questions/[id]/page.tsx').default;
const schemePage=harness.load('app/ib/mark-scheme/[id]/page.tsx').default;
const request=query=>({params:Promise.resolve({collection:'number-algebra'}),searchParams:Promise.resolve(query)});
let html=renderToStaticMarkup(await page(request({})));
assert.match(html,/Question 1/);assert.match(html,/Question 2/);assert.doesNotMatch(html,/Question 3|SECRET-SOLUTION-CANARY|Synthetic test only|Video|AI Feedback/);
assert.match(html,/target="_blank"/);assert.match(html,/rel="noopener noreferrer"/);assert.match(html,/katex/);
html=renderToStaticMarkup(await page(request({difficulty:'hard',calculator:'yes'})));
assert.match(html,/Question 2/);assert.doesNotMatch(html,/Question 1/);
assert.match(authCalls.at(-1),/difficulty=hard&calculator=yes/);
html=renderToStaticMarkup(await page(request({subtopic:'Binomial theorem',q:'binomial'})));
assert.match(html,/Question 1/);assert.doesNotMatch(html,/Question 2/);
html=renderToStaticMarkup(await page(request({q:'nonexistent',page:'99999999'})));
assert.match(html,/No questions match these filters/);assert.doesNotMatch(html,/SECRET-SOLUTION-CANARY/);
html=renderToStaticMarkup(await page(request({difficulty:'forged',calculator:'forged',page:'NaN'})));
assert.match(html,/Question 1/);assert.match(html,/Question 2/);
html=renderToStaticMarkup(await questionPage({params:Promise.resolve({id:base.id})}));
assert.match(html,/Maximum mark/);assert.doesNotMatch(html,/SECRET-SOLUTION-CANARY|Synthetic test only/);
html=renderToStaticMarkup(await schemePage({params:Promise.resolve({id:base.id})}));
assert.match(html,/SECRET-SOLUTION-CANARY/);assert.match(html,/M1/);assert.match(html,/A1/);assert.doesNotMatch(html,/Synthetic test only/);
await assert.rejects(()=>schemePage({params:Promise.resolve({id:draft.id})}),/NOT_FOUND/);
await assert.rejects(()=>questionPage({params:Promise.resolve({id:'missing'})}),/NOT_FOUND/);

const blocked=ibHarness({questions:[base],user:null});
for(const route of ['app/ib/questions/[id]/page.tsx','app/ib/mark-scheme/[id]/page.tsx']) await assert.rejects(()=>blocked.load(route).default({params:Promise.resolve({id:base.id})}),/AUTH_REQUIRED/);
await assert.rejects(()=>blocked.load('app/ib/question-bank/[collection]/page.tsx').default(request({})),/AUTH_REQUIRED/);
assert.equal(harness.model.safeDiagram('<svg viewBox="0 0 10 10"><script>alert(1)</script></svg>'),false);
assert.equal(harness.model.safeDiagram('<svg viewBox="0 0 10 10"><image href="https://external.invalid/a"/></svg>'),false);
assert.equal(harness.model.safeDiagram('<svg viewBox="0 0 10 10"><path d="M0 0L10 10"/></svg>'),true);
for(const bad of [{...base,marks:3},{...base,calculator:'yes'},{...base,markScheme:[]},{...base,topicId:'calculus'}]) assert.equal(harness.model.ibQuestionSchema.safeParse(bad).success,false);
assert.match(readFileSync('lib/ib/content.ts','utf8'),/^import "server-only"/);
assert.match(readFileSync('app/ib-login/IBLoginClient.tsx','utf8'),/parsed\.pathname\.startsWith\("\/ib\/"\)/);

// Exercise the real page-level guard as well as the routes' dependency boundary.
let guardUser={email:'synthetic@example.invalid'},guardError=null,verifiedCalls=0;
const guardCode=ts.transpileModule(readFileSync('lib/ib/auth.ts','utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
const guardImports={
  'server-only':{},'react':{cache:fn=>fn},
  'next/navigation':{redirect:destination=>{throw new Error(`LOGIN:${destination}`);}},
  '@/lib/auth/login-destination':harness.load('lib/auth/login-destination.ts'),
  '@/utils/supabase/server':{supabaseServer:async()=>({auth:{getUser:async()=>{verifiedCalls++;return {data:{user:guardUser},error:guardError};}}})},
};
const guardContext=vm.createContext({exports:{},require:name=>{assert.ok(name in guardImports);return guardImports[name];},encodeURIComponent});
vm.runInContext(guardCode,guardContext);
const guard=guardContext.exports.requireIbUser;
assert.equal((await guard('/ib/questions/ib-aa-na-001')).email,guardUser.email);
for(const failure of ['no-user','no-email','provider-error']) {
  guardUser=failure==='no-user'?null:failure==='no-email'?{}:{email:'synthetic@example.invalid'};
  guardError=failure==='provider-error'?{message:'synthetic error'}:null;
  await assert.rejects(()=>guard('/ib/mark-scheme/ib-aa-na-001'),/LOGIN:\/ib-login\?next=%2Fib%2Fmark-scheme%2Fib-aa-na-001/);
}
assert.equal(verifiedCalls,4);

// Physics uses the same authenticated routes and prompt-only projection.
const svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 60"><path d="M10 50L90 10"/><text x="12" y="12">v / m s-1</text></svg>';
const solutionSvg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 60"><text x="2" y="20">PRIVATE-SOLUTION-GRAPH</text></svg>';
const physics={...base,id:'ib-phy-a-001',subject:'physics-hl',topicId:'space-time-motion',collectionId:'physics-space-time-motion',syllabusCode:'A.1',level:'core',questionType:'multiple-choice',calculator:true,marks:1,title:'Trolley momentum',subtopic:'Kinematics',stem:'A trolley of mass $1.0\\,\\mathrm{kg}$ moves at $2.0\\,\\mathrm{m\\,s^{-1}}$. Which is its momentum?',options:[{label:'A',text:'$1.0\\,\\mathrm{kg\\,m\\,s^{-1}}$'},{label:'B',text:'$2.0\\,\\mathrm{kg\\,m\\,s^{-1}}$'},{label:'C',text:'$3.0\\,\\mathrm{kg\\,m\\,s^{-1}}$'},{label:'D',text:'$4.0\\,\\mathrm{kg\\,m\\,s^{-1}}$'}],correctOption:'B',markScheme:[{part:'',steps:[{code:'A1',text:'PHYSICS-SOLUTION-CANARY B. Momentum is mass multiplied by velocity, so $p=mv=2.0\\,\\mathrm{kg\\,m\\,s^{-1}}$.'}]}],diagramSvg:svg,markSchemeDiagramSvg:solutionSvg,answerSummary:'PRIVATE-ANSWER-SUMMARY',source:{document:'Independent syllabus-authored practice',question:1},verification:{method:'Synthetic check',notes:'PRIVATE-VERIFICATION-NOTES'}};
const structured={...physics,id:'ib-phy-a-002',number:2,title:'Wheel acceleration',subtopic:'Rigid body mechanics',syllabusCode:'A.4',level:'ahl',questionType:'structured',difficulty:'hard',options:undefined,correctOption:undefined,marks:2,markScheme:base.markScheme,source:{...physics.source,question:2}};
const dataBased={...structured,id:'ib-phy-a-003',number:3,title:'Motion graph',subtopic:'Kinematics',syllabusCode:'A.1',level:'core',questionType:'data-based',difficulty:'medium',source:{...physics.source,question:3}};
const physicsDraft={...physics,id:'ib-phy-a-004',number:4,status:'draft',source:{...physics.source,question:4}};
const physicsThemes=harness.model.IB_COLLECTIONS.filter(c=>c.subject==='physics-hl');
assert.equal(physicsThemes.length,5);
assert.deepEqual(Array.from(harness.model.IB_COLLECTIONS.filter(c=>c.subject==='math-aa-hl'),c=>c.id),['number-algebra','functions','geometry-trigonometry','statistics-probability','calculus-1','calculus-2']);
const themes=physicsThemes.slice(1).map(c=>({...physics,id:'ib-phy-'+c.code.toLowerCase()+'-001',topicId:c.topicId,collectionId:c.id,syllabusCode:c.code+'.1',title:c.title}));
const physicsCalls=[];
const physicsHarness=ibHarness({questions:[base,physics,structured,dataBased,physicsDraft,...themes],onAuth:next=>physicsCalls.push(next)});
const physicsBank=physicsHarness.load('app/ib/question-bank/[collection]/page.tsx').default;
const physicsQuestion=physicsHarness.load('app/ib/questions/[id]/page.tsx').default;
const physicsScheme=physicsHarness.load('app/ib/mark-scheme/[id]/page.tsx').default;
const physicsRequest=(query={},collection=physics.collectionId)=>({params:Promise.resolve({collection}),searchParams:Promise.resolve(query)});
for(const fixture of [physics,structured,dataBased,...themes]) assert.equal(physicsHarness.model.ibQuestionSchema.safeParse(fixture).success,true,fixture.id);
const physicsPrompt=physicsHarness.model.questionPrompt(physics);
for(const hidden of ['markScheme','markSchemeDiagramSvg','markSchemeDiagramUrl','answerSummary','source','verification','correctOption']) assert.equal(hidden in physicsPrompt,false,hidden);
assert.equal(physicsPrompt.options.length,4);
for(const collection of physicsThemes) {
  html=renderToStaticMarkup(await physicsBank(physicsRequest({},collection.id)));
  assert.match(html,/IB PHYSICS HL/);assert.match(html,/aria-label="Physics themes"/);assert.match(html,/9\.81/);
  assert.match(html,/aria-current="page" href="\/ib\?subject=physics-hl&amp;view=questions"/);
  assert.doesNotMatch(html,/Angles are in radians|PHYSICS-SOLUTION-CANARY|PRIVATE-ANSWER|PRIVATE-VERIFICATION|PRIVATE-SOLUTION-GRAPH|Question 4/);
  assert.ok(!html.includes(Buffer.from(solutionSvg).toString('base64')));
  assert.match(html,/aria-label="Multiple-choice options"/);assert.match(html,/Difficulty: /);assert.match(html,/class="difficultyBars" aria-hidden="true"/);
  assert.match(html,/target="_blank" rel="noopener noreferrer"/);
}
html=renderToStaticMarkup(await physicsBank(physicsRequest({syllabus:'A.4',level:'ahl',type:'structured',difficulty:'hard'})));
assert.match(html,/Question 2/);assert.doesNotMatch(html,/Question 1|Question 3/);
assert.match(physicsCalls.at(-1),/syllabus=A.4&level=ahl&type=structured/);
html=renderToStaticMarkup(await physicsBank(physicsRequest({type:'data-based'})));
assert.match(html,/Question 3/);assert.doesNotMatch(html,/Question 1|Question 2/);
html=renderToStaticMarkup(await physicsBank(physicsRequest({syllabus:'B.1',level:'forged',type:'forged',calculator:'no'})));
assert.match(html,/Question 1/);assert.match(html,/Question 2/);assert.match(html,/Question 3/);
html=renderToStaticMarkup(await physicsBank(physicsRequest({q:'PHYSICS-SOLUTION-CANARY'})));
assert.match(html,/No questions match these filters/);
html=renderToStaticMarkup(await physicsQuestion({params:Promise.resolve({id:physics.id})}));
assert.match(html,/Multiple-choice options/);assert.doesNotMatch(html,/PHYSICS-SOLUTION-CANARY|PRIVATE-ANSWER|PRIVATE-VERIFICATION/);
html=renderToStaticMarkup(await physicsScheme({params:Promise.resolve({id:physics.id})}));
assert.match(html,/PHYSICS-SOLUTION-CANARY/);assert.match(html,/Total <strong>1 mark/);assert.match(html,/does not earn additional marks/);
assert.ok(html.includes(Buffer.from(solutionSvg).toString('base64')));
assert.doesNotMatch(html,/PRIVATE-ANSWER-SUMMARY|PRIVATE-VERIFICATION-NOTES/);
for(const route of [physicsQuestion,physicsScheme]) await assert.rejects(()=>route({params:Promise.resolve({id:physicsDraft.id})}),/NOT_FOUND/);
await assert.rejects(()=>physicsBank(physicsRequest({},'unknown-physics-theme')),/NOT_FOUND/);
const blockedPhysics=ibHarness({questions:[physics],user:null});
for(const route of ['app/ib/questions/[id]/page.tsx','app/ib/mark-scheme/[id]/page.tsx']) await assert.rejects(()=>blockedPhysics.load(route).default({params:Promise.resolve({id:physics.id})}),/AUTH_REQUIRED/);
await assert.rejects(()=>blockedPhysics.load('app/ib/question-bank/[collection]/page.tsx').default(physicsRequest({syllabus:'A.1',type:'multiple-choice'})),/AUTH_REQUIRED/);
for(const bad of [
  {...physics,marks:2},{...physics,calculator:false},{...physics,correctOption:undefined},
  {...physics,options:physics.options.slice(0,3)},{...physics,options:physics.options.map(o=>({...o,label:'A'}))},
  {...physics,syllabusCode:'B.1'},{...physics,collectionId:'number-algebra'},
  {...physics,id:'ib-phy-b-001'},{...structured,level:'core'},
  {...physics,markScheme:[{part:'',steps:[{code:'M1',text:'Wrong type of single mark.'}]}]},
  {...structured,options:physics.options},{...physics,source:{...physics.source,document:'Unapproved copied questions'}},
]) assert.equal(physicsHarness.model.ibQuestionSchema.safeParse(bad).success,false,JSON.stringify(bad));

// Pagination retains all Physics filters and clamps out-of-range pages.
const many=Array.from({length:10},(_,index)=>({...physics,id:'ib-phy-a-'+String(index+1).padStart(3,'0'),number:index+1,source:{...physics.source,question:index+1}}));
const paging=ibHarness({questions:many}).load('app/ib/question-bank/[collection]/page.tsx').default;
html=renderToStaticMarkup(await paging(physicsRequest({syllabus:'A.1',level:'core',type:'multiple-choice'})));
assert.match(html,/Page 1 of 2/);assert.match(html,/syllabus=A.1&amp;level=core&amp;type=multiple-choice&amp;page=2/);
assert.doesNotMatch(html,/Question 9</);
html=renderToStaticMarkup(await paging(physicsRequest({syllabus:'A.1',page:'999'})));
assert.match(html,/Page 2 of 2/);assert.match(html,/Question 9</);assert.match(html,/Question 10</);

// All five overview cards and all 24 syllabus links are real destinations.
const courses=physicsHarness.load('lib/ib/catalog.ts');
const summary=Object.fromEntries(Object.keys(courses.IB_COURSES).map(subject=>[subject,{questions:subject==='physics-hl'?7:1,mocks:0,topics:{},collections:physicsHarness.model.IB_COLLECTIONS.filter(c=>c.subject===subject).map(c=>({...c,count:1,subtopics:[],...(subject==='physics-hl'?{syllabus:courses.physicsSyllabusSubtopics(c.topicId).map(s=>({...s,count:1}))}:{})}))}]));
const overview=ibHarness({query:'subject=physics-hl'}).load('app/ib/IBPortalClient.tsx').default;
html=renderToStaticMarkup(React.createElement(overview,{email:'synthetic@example.invalid',summary}));
for(const collection of physicsThemes) assert.ok(html.includes('href="/ib/question-bank/'+collection.id+'"'));
assert.equal((html.match(/\?syllabus=/g)||[]).length,24);assert.doesNotMatch(html,/CONTENT COMING SOON|Questions and written mark schemes will appear/);

// CDN images are opt-in, origin-restricted, and retain the authenticated SVG fallback.
const originalOrigin=process.env.IB_DIAGRAM_CDN_ORIGIN;
try {
  delete process.env.IB_DIAGRAM_CDN_ORIGIN;
  assert.equal(physicsHarness.model.safeDiagramUrl('https://diagrams.example.invalid/a.svg'),false);
  process.env.IB_DIAGRAM_CDN_ORIGIN='https://diagrams.example.invalid';
  const trusted='https://diagrams.example.invalid/a.svg';
  assert.equal(physicsHarness.model.safeDiagramUrl(trusted),true);
  for(const bad of ['http://diagrams.example.invalid/a.svg','https://diagrams.example.invalid.evil.invalid/a.svg','https://user:password@diagrams.example.invalid/a.svg','//diagrams.example.invalid/a.svg','data:image/svg+xml,hello','https://untrusted.example.invalid/a.svg']) {
    assert.equal(physicsHarness.model.safeDiagramUrl(bad),false,bad);
    assert.equal(physicsHarness.model.ibQuestionSchema.safeParse({...physics,diagramUrl:bad}).success,false,bad);
  }
  const withAssets=physicsHarness.model.ibQuestionSchema.parse({...physics,diagramUrl:trusted,markSchemeDiagramUrl:trusted.replace('a.svg','answer.svg')});
  assert.equal('markSchemeDiagramUrl' in physicsHarness.model.questionPrompt(withAssets),false);
  const Diagram=physicsHarness.load('app/ib/components/QuestionBody.tsx').QuestionDiagram;
  html=renderToStaticMarkup(React.createElement(Diagram,{svg,url:trusted,caption:'Synthetic graph'}));
  assert.match(html,/src="https:\/\/diagrams.example.invalid\/a.svg"/);
  html=renderToStaticMarkup(React.createElement(Diagram,{svg,url:'https://untrusted.example.invalid/a.svg',caption:'Synthetic graph'}));
  assert.match(html,/src="data:image\/svg\+xml;base64,/);assert.doesNotMatch(html,/untrusted/);
  const Image=physicsHarness.load('app/ib/components/DiagramImage.tsx').default;
  const fallback='data:image/svg+xml;base64,'+Buffer.from(svg).toString('base64');
  const imageElement=Image({src:trusted,fallback,caption:'Synthetic graph'});
  const event={currentTarget:{src:trusted}};imageElement.props.onError(event);assert.equal(event.currentTarget.src,fallback);
  imageElement.props.onError(event);assert.equal(event.currentTarget.src,fallback);
  const MathContent=physicsHarness.load('app/ib/components/MathContent.tsx').default;
  html=renderToStaticMarkup(React.createElement(MathContent,null,'![External](https://untrusted.example.invalid/a.svg)'));
  assert.doesNotMatch(html,/untrusted.example.invalid|<img/);
} finally { if(originalOrigin===undefined)delete process.env.IB_DIAGRAM_CDN_ORIGIN;else process.env.IB_DIAGRAM_CDN_ORIGIN=originalOrigin; }
console.log('IB portal passed: Maths regressions; five Physics themes and 24 syllabus destinations; filters/pagination; MCQ one-mark validation; accessible difficulty bars; real Markdown/KaTeX; independent authorization; private-answer and solution-image separation; draft/unknown IDs withheld; trusted-CDN restriction with SVG fallback. Synthetic fixtures only; no emails or database writes.');
