import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {unified} from 'unified';
import remarkParse from 'remark-parse';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import katex from 'katex';
import {ibHarness} from './ib-component-harness.mjs';
const harness=ibHarness(),model=harness.model,catalog=harness.load('lib/ib/catalog.ts'),parser=unified().use(remarkParse).use(remarkMath).use(remarkGfm);
const batches={'unity-diversity':50,'form-function':50,'interaction-interdependence':50,'continuity-change':50};
const selected=process.argv.find(x=>x.startsWith('--batch='))?.split('=')[1];
const ids=new Set(),prompts=new Set(),report={status:'passed',questions:0,diagrams:0,solutionDiagrams:0,sl:0,ahl:0,themes:{},batches:{},formulae:0};
const errors=[];
function markdown(text,label){
 assert.ok(!/[\u0000-\u0009\u000b-\u001f]/.test(text),label+' control character');
 assert.ok(!/\b(?:TODO|TBD|placeholder|insert solution)\b/i.test(text),label+' unfinished');
 function visit(n){
  if(n.type==='inlineMath'||n.type==='math'){try{katex.renderToString(n.value,{throwOnError:true,strict:'ignore',trust:false});report.formulae++;}catch(e){errors.push(label+': '+e.message);}}
  n.children?.forEach(visit);
 }
 visit(parser.parse(text));
}
for(const batch of selected?[selected]:Object.keys(batches)){
 const file='content/ib/biology-2026-expansion/'+batch+'.json',bytes=readFileSync(file),qs=JSON.parse(bytes);
 assert.equal(qs.length,batches[batch]);report.batches[batch]={questions:qs.length,sha256:createHash('sha256').update(bytes).digest('hex')};
 for(const input of qs){
  const q=model.ibQuestionSchema.parse(input);assert.equal(q.subject,'biology');assert.equal(q.difficulty,'hard');assert.equal(q.status,'published');
  assert.ok(q.number>=701&&q.number<=750);assert.ok(q.parts.length>=2);assert.ok(q.marks>=6);
  assert.ok(!ids.has(q.id));ids.add(q.id);const fp=q.stem+'\n'+q.parts.map(p=>p.prompt).join('\n');assert.ok(!prompts.has(fp));prompts.add(fp);
  assert.ok(q.markScheme.some(g=>g.steps.some(s=>s.code[0]==='R'||s.code[0]==='M')),q.id+' reasoning marking points');
  markdown(q.stem,q.id);q.parts.forEach(p=>markdown(p.prompt,q.id));q.markScheme.forEach(g=>g.steps.forEach(s=>markdown(s.text,q.id)));
  assert.equal(q.subtopic,catalog.ibSyllabusSubtopics('biology',q.topicId).find(s=>s.code===q.syllabusCode)?.title,q.id+' exact syllabus title');
  const prompt=model.questionPrompt(q);for(const k of ['markScheme','answerSummary','verification','source','markSchemeDiagramSvg','markSchemeDiagramUrl'])assert.ok(!(k in prompt),q.id+' privacy '+k);
  if(q.diagramSvg){assert.ok(model.safeDiagram(q.diagramSvg));report.diagrams++;}if(q.markSchemeDiagramSvg){assert.ok(model.safeDiagram(q.markSchemeDiagramSvg));report.solutionDiagrams++;}
  report.questions++;report[q.level]++;report.themes[q.topicId]=(report.themes[q.topicId]??0)+1;
 }
}
if(!selected){assert.equal(report.questions,200);assert.equal(report.sl,80);assert.equal(report.ahl,120);assert.ok(report.diagrams>=180);assert.deepEqual(Object.values(report.themes),[50,50,50,50]);}
if(errors.length)throw new Error(errors.join('\n'));
if(!selected){mkdirSync('docs/ib-2026-biology',{recursive:true});writeFileSync('docs/ib-2026-biology/content-checks.json',JSON.stringify(report,null,2)+'\n');}
console.log(JSON.stringify(report));
