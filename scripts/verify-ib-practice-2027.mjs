import assert from 'node:assert/strict';
import fs from 'node:fs';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import katex from 'katex';
import {ibHarness} from './ib-component-harness.mjs';
const h=ibHarness(), bank=h.load('lib/ib/content.ts'), cat=h.load('lib/ib/practice-catalog.ts');
const real=h.load('lib/ib/practice-papers.ts');
const paperService=ibHarness({moduleMocks:{'@/lib/ib/content':bank}}).load('lib/ib/practice-papers.ts');
const maths=h.load('lib/ib/maths-mocks.ts'), mathcat=h.load('lib/ib/maths-mock-model.ts');
const read=file=>JSON.parse(fs.readFileSync(file,'utf8'));
const all=await bank.getIbQuestions();
const dir='content/ib/practice-2027', topics=read(dir+'/topic-tests.json'), business=read(dir+'/business-catalog.json'), ai=read(dir+'/ai-catalog.json');
const index=read('content/ib/content-index.json');
assert.equal(index.summaries.hl['math-ai-hl'].mocks,12);
assert.equal(index.summaries.sl['business-management'].mocks,4);assert.equal(index.summaries.hl['business-management'].mocks,6);
const primary=new Set(all.filter(q=>q.subject==='math-aa-hl').map(q=>q.syllabusCode));
for(const [i,max] of [16,16,18,14,19].entries())for(let n=1;n<=max;n++)assert(primary.has(`${i+1}.${n}`));
for(const [id,code] of [['ib-aa-sp-008','4.10'],['ib-aa-sp-021','4.11'],['ib-aa-c2-017','5.10']])assert.equal((await bank.getIbQuestion(id)).syllabusCode,code);
let formulae=0,parts=0;const svgs=new Set();
function formula(text){
 const segments=(text??'').split('$');assert.equal(segments.length%2,1,text);
 for(let n=1;n<segments.length;n+=2){katex.renderToString(segments[n],{throwOnError:true,strict:false});formulae++;}
}
function verify(q){
 formula(q.stem);if(q.diagramSvg){assert(h.model.safeDiagram(q.diagramSvg));svgs.add(q.diagramSvg);}
 for(const [i,p] of q.parts.entries()){
   formula(p.prompt);const s=q.markScheme[i];assert.equal(s.part,p.label);
   assert.equal(s.steps.reduce((acc,t)=>acc+Number(t.code.slice(1)),0),p.marks);
   for(const point of s.steps)formula(point.text);
   parts++;
 }
}
function pdf(path){const data=fs.readFileSync('public'+path);assert.equal(data.subarray(0,5).toString(),'%PDF-');assert(data.length>3000);}
for(const p of ai){
 const paper=await maths.getMathsMockPaper(p.id);
 assert.equal(paper.questions.length,2);assert.equal(paper.minutes,75);assert.equal(paper.marks,55);
 for(const q of paper.questions){verify(q);assert(q.syllabusRefs.length>=2);}
 const prompt=maths.mathsMockPrompt(paper,mathcat.getMathsMock(p.id));
 assert(prompt.questions.every(q=>!('markScheme' in q)));pdf(p.pdfUrl);pdf(p.questionPdfUrl);
}
for(const entry of [...business,...topics]){
 const p=await paperService.loadPracticePaper(entry.id);assert(p);p.questions.forEach(verify);for(const r of p.resources)formula(r.text);
 const prompt=real.practicePrompt(p);assert(prompt.questions.every(q=>!('markScheme' in q)));
 let opts=p.questions.flatMap((q,i)=>q.optional?[i]:[]);if(!opts.length)opts=[null];
 for(const opt of opts){const max=cat.activeParts(prompt,opt).reduce((a,b)=>a+b.max,0);assert.equal(max,entry.marks);}
 Object.values(cat.practiceFiles(entry.id)).forEach(pdf);
}
pdf('/ib-practice-2027/business-a-pre-release.pdf');
pdf('/ib-practice-2027/business-b-pre-release.pdf');
for(const q of all.filter(q=>q.number>=841&&q.number<=844&&q.subject.startsWith('math-aa-')))verify(q);
assert.equal(svgs.size,4);
// Independent numeric checks for all four AI investigations.
const near=(a,b,tol=1e-5)=>assert(Math.abs(a-b)<tol,`${a} differs from ${b}`);
let a=480,b=120;
for(let n=1;n<=7;n++){[a,b]=[0.7*a+0.2*b,0.3*a+0.8*b];near(a+b,600);near(a,240+240*0.5**n);assert.equal(Math.abs(a-240)<=5,n>=6);}
const inflow=t=>-1+4*Math.sin(Math.PI*t/6);
const volume=t=>18-t+24/Math.PI*(1-Math.cos(Math.PI*t/6));
let net=0, actual=18, spill=0;const dt=0.001;
for(let i=0;i<12000;i++){const dv=inflow((i+0.5)*dt)*dt;net+=dv;actual+=dv;if(actual>25){spill+=actual-25;actual=25;}}
near(net,-12);near(spill,2.518874,2e-5);near(actual,3.481126,2e-5);near(volume(3.820156),25);
const probe=t=>15.5+0.5*t+18.5*Math.exp(-0.2*t);
let euler=34;for(const t of [0,4])euler+=4*(-0.2*(euler-18-0.5*t));
near(euler,20.24);near(probe(8)-euler,2.995086);near(probe(5*Math.log(7.4)),18+2.5*Math.log(7.4));
const poolProb=(n,k)=>{let choose=1;for(let i=1;i<=k;i++)choose*=((n-i+1)/i);return choose*0.04**k*0.96**(n-k);};
for(const noisy of [false,true]){
 const totals=[];for(let n=2;n<=10;n++){let expected=0;for(let k=0;k<=n;k++)expected+=poolProb(n,k)*(1+n*(k?(noisy?0.95:1):(noisy?0.02:0)));totals.push(expected/n);}
 assert.equal(totals.indexOf(Math.min(...totals))+2,6);
}
near(0.95*(1-0.96**5)/(0.95*(1-0.96**5)+0.02*0.96**5),0.914934);
// Recalculate the regression from sums of centred observations and the Business Paper 2 cash flows.
const xs=[2,4,5,7,8,10],ys=[3,4,7,6,9,10],sx=xs.map(x=>x-6),sy=ys.map(y=>y-6.5);
const dot=(u,v)=>u.reduce((s,x,i)=>s+x*v[i],0);
near(dot(sx,sy)/dot(sx,sx),0.880952);near(dot(sx,sy)/dot(sy,sy),0.986667);
near(55000*.909+65000*.826+70000*.751-150000,6255);near((150000-55000*.909-65000*.826)/.751,61671.10519);
near(540000/300000,1.8);near((540000-210000)/300000,1.1);
near(4600+12800-15100-4000,-1700);near(-1700+16500-14200,600);
near((135000*.98-128000*.95)*1.2-8000,4840);near(3000*(28-14)-6000,36000);
// Check diagram coordinates, units, directions and symmetry independently of raster review.
const rateSvg=[...svgs].find(s=>s.includes('Net rate'));
assert(rateSvg);const coords=rateSvg.match(/<polyline points="([^"]+)"/)[1].split(' ').map(p=>p.split(',').map(Number));
assert.deepEqual(coords.map(([x,y])=>[(x-65)/49,(164-y)/18]),[[0,2],[2,6],[5,0],[7,-4],[8,0]]);
const circle=[...svgs].find(s=>s.includes('reflection of P'));
const points=[...circle.matchAll(/<circle cx="([\d.]+)" cy="([\d.]+)" r="4"/g)].map(m=>[+m[1],+m[2]]);
near(points[0][0]+points[1][0],490);near(points[0][1],points[1][1]);near(Math.hypot(points[0][0]-245,points[0][1]-125),85);
const fleet=[...svgs].find(s=>s.includes('30% of depot A'));assert(fleet.includes('20% of depot B')&&fleet.includes('H464')&&fleet.includes('H146'));
const pool=[...svgs].find(s=>s.includes('No follow-up tests'));assert(pool.includes('Negative')&&pool.includes('Positive')&&pool.includes('Test each seedling separately'));
const View=h.load('app/ib/components/PracticePaperList.tsx').default;
for(const level of ['sl','hl']){
 const html=renderToStaticMarkup(React.createElement(View,{subject:'business-management',course:level}));
 assert.equal((html.match(/Open timed paper/g)||[]).length,level==='sl'?4:6);assert(!html.includes('-solutions.pdf'));assert(html.includes('business-a-pre-release.pdf')&&html.includes('business-b-pre-release.pdf'));
 const aa=renderToStaticMarkup(React.createElement(View,{subject:'math-aa-'+level,course:level}));assert.equal((aa.match(/Open timed paper/g)||[]).length,2);
}
const formatQuestions=[];
for(const collection of ['physics-fields','chemistry-structure-2','economics-macroeconomics']){
 for(const q of read(dir+'/formats/'+collection+'.json')){
  assert.equal((await bank.getIbQuestion(q.id,'sl')).id,q.id);
  assert.equal((await bank.getIbQuestion(q.id,'hl')).id,q.id);
  const publishedPrompt=h.model.questionPrompt(q);assert(!('markSchemeDiagramSvg' in publishedPrompt));
  if(q.subject==='economics'){
   assert.equal(q.examStyle,'paper-1');assert.equal(q.calculator,false);assert.equal(q.syllabusCode,'3.6');
   assert.deepEqual(q.parts.map(p=>p.marks),[10,15]);assert.deepEqual(q.markScheme.map(g=>g.rubric.maxMarks),[10,15]);
   assert(q.markScheme[1].steps.some(s=>s.text.includes('12.9%')&&s.text.includes('13.6%')));
  }else{
   assert.equal(q.syllabusCode,q.subject==='physics-hl'?'D.3':'S2.3');assert.equal(q.questionType,'data-based');verify(q);
  }
  if(q.markSchemeDiagramSvg){assert(h.model.safeDiagram(q.markSchemeDiagramSvg));svgs.add(q.markSchemeDiagramSvg);}
  formatQuestions.push(q);
 }
}
assert.equal(formatQuestions.length,7);assert.equal(svgs.size,6);
for(const k of ['questions','solutions'])pdf('/ib-practice-2027/science-and-economics-'+k+'.pdf');
const [curvature, , , , , , fiscal]=formatQuestions;
const measured=[20,25,40,50].map((B,i)=>[Math.round((1/(B/1000))*100)/100,[10,8.1,5,4.1][i]]);
const svgPoints=s=>Array.from(s.matchAll(/<circle cx="([\d.]+)" cy="([\d.]+)"/g),m=>[+m[1],+m[2]]);
const pointsOfCurve=svgPoints(curvature.markSchemeDiagramSvg);
for(const [i,[x,y]] of pointsOfCurve.entries()){near((x-62)/7,measured[i][0]);near((230-y)/17,measured[i][1]);}
const eqPoints=svgPoints(fiscal.markSchemeDiagramSvg);
for(const [i,[x,y]] of eqPoints.entries()){
 near(y,268-0.4*x);near(y,(i?-20:70)+0.5*x);assert(x<405);
}
assert(eqPoints[0][0]<eqPoints[1][0]&&eqPoints[0][1]>eqPoints[1][1]);
near(400000/(0.025*0.081)/1e8,1.97530864);
near((5.3-(-4.3))/2,4.8);near((5.3+(-4.3))/2,0.5);
near((2*0.0048/(0.08/2e5)**2)/(40/0.02)/1e7,3);
near((5400-2400)/(0.010-0.004),5e5);near((2400-5e5*.004)/5e5,.0008);
near(100*(453.7-336.5)/453.7,25.8,.05);near(36/20,1.8);
near((648+651+651)/3,650);near((658+661+661)/3,660);
near(100*((216000/96)/(192000/80)-1),-6.25);
near((200-60)*18-2400,120);near(Math.ceil((2400+60*18)/18),194);
near(9000-5400+3000-5400,1200);near(9000+9000-10800,7200);
near((390000/750000)*100,52);near(15000-150000*.08,3000);
near((.6*80000+.4*35000)*3.31-180000,25220);near((.6*45000+.4*32000)*3.31-100000,31738);
near((18600-1200)/(30000-1200+6000),.5);near((30000-18600+6000)*.6/.4-(18600-1200),8700);
console.log(JSON.stringify({aiPapers:ai.length,businessPapers:business.length,topicTests:topics.length,scienceAndEconomicsQuestions:formatQuestions.length,aaHlPrimaryCodes:primary.size,markAllocationsChecked:parts,formulae,distinctFigures:svgs.size}));
