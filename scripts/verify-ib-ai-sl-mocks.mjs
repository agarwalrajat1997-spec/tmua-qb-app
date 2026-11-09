import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {ibHarness} from './ib-component-harness.mjs';
const h=ibHarness(), m=h.load('lib/ib/maths-mock-model.ts'), server=h.load('lib/ib/maths-mocks.ts'), paths=h.load('lib/ib/catalog.ts');
const ids=['a','b'].flatMap(set=>['1','2'].map(p=>'ai-sl-set-'+set+'-paper-'+p)),norm=x=>JSON.parse(JSON.stringify(x));
assert.deepEqual(norm(m.AI_SL_MATHS_MOCKS.map(p=>p.id)),ids);assert.equal(m.getMathsMock('ai-sl-set-a-paper-3'),undefined);
const List=h.load('app/ib/components/MathsMockList.tsx').default,html=renderToStaticMarkup(React.createElement(List,{course:'sl',strand:'ai'}));
assert(!html.includes('ai-hl-set-'));assert(!html.includes('aa-sl-set-'));assert(!html.includes('Paper 3'));assert.match(html,/Paper 2 follows connected problems/);
const index=JSON.parse(readFileSync('content/ib/content-index.json','utf8'));assert.equal(index.summaries.sl['math-ai-sl'].mocks,4);assert.equal(index.summaries.hl['math-ai-hl'].mocks,12);
let parts=0,figures=0;const unique=new Set(),submax=[8,6,6,11,8];
for(const id of ids){
 const meta=m.getMathsMock(id),p=await server.getMathsMockPaper(id);assert(p);
 assert.equal(paths.ibSubjectForPath('/ib/maths-mocks/'+id),'math-ai-sl');assert.equal(meta.minutes,90);assert.equal(meta.marks,80);assert.equal(meta.calculator,true);
 assert.equal(p.questions.length,meta.paper==='1'?12:4);assert(html.includes('/ib/maths-mocks/'+id));assert(html.includes(meta.questionPdfUrl));assert(!html.includes('href="'+meta.pdfUrl+'"'));
 const prompt=server.mathsMockPrompt(p,meta);assert(!/markScheme|answerSummary|syllabusRefs|cognitiveDemand/.test(JSON.stringify(prompt.questions)));
 const topics=new Set();
 for(const q of p.questions){
  assert(!unique.has(q.stem));unique.add(q.stem);assert.equal(q.section,'');parts+=q.parts.length;
  if(q.diagramSvg){assert(prompt.questions[q.number-1].diagramUrl.startsWith('data:image/svg+xml;base64,'));figures++;}
  for(const ref of q.syllabusRefs){const hit=/^SL ([1-5])\.(\d+)$/.exec(ref);assert(hit);assert(+hit[2]>=1 && +hit[2]<=submax[+hit[1]-1],ref);topics.add(+hit[1]);}
 }
 if(meta.paper==='1')assert.equal(topics.size,5);
 for(const url of [meta.questionPdfUrl,meta.pdfUrl])assert.equal(readFileSync('public'+url).subarray(0,5).toString(),'%PDF-');
 const marks=Object.fromEntries(p.questions.flatMap(q=>q.parts.map(part=>[m.mathsAnswerKey(q.number,part.label),part.marks]))),valid=m.validateMathsMarks(p.questions,marks),score=m.scoreMathsMock(p.questions,valid);
 assert.equal(score.total,80);assert.equal(score.maximum,80);assert.throws(()=>m.validateMathsMarks(p.questions,{...marks,'1:a':99}));
 const send=m.mathsReportPayload(meta,{name:'Offline QA',id:'qa',submittedAt:'2026-11-08T00:00:00Z',elapsed:5400,answers:{},selfMarks:valid,score,solutions:p.questions},'offline@example.invalid','https://example.invalid');
 assert.equal(send.solution_link,'https://example.invalid'+meta.pdfUrl);assert.match(send.session,/AI SL/);assert.match(send.score,/80 \/ 80/);
 assert.throws(()=>server.validateMathsMockPaper({...p,course:'hl'},meta));
}
assert.equal(unique.size,32);assert.equal(figures,4);console.log('AI SL: 4 timed papers, 320 marks, '+parts+' parts, 4 figures, 8 PDFs, isolated SL navigation, scoring and report links verified.');
