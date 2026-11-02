import assert from 'node:assert/strict';
import {readFileSync,readdirSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {unified} from 'unified';
import remarkParse from 'remark-parse';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import katex from 'katex';
import {ibHarness} from './ib-component-harness.mjs';
const model=ibHarness().model;
const parser=unified().use(remarkParse).use(remarkMath).use(remarkGfm);
const errors=[],ids=new Set(),prompts=new Map(),reports={};
const hash=x=>createHash('sha256').update(x).digest('hex');
const dir='content/ib/math-2026-expansion';
const courseArg=process.argv.find(x=>x.startsWith('--course='))?.split('=')[1];
const courses=courseArg?[courseArg]:['aa-sl','aa-hl','ai-sl','ai-hl'];
let formulae=0;
function markdown(text,label){
 if(/[\u0000-\u0009\u000b-\u001f]/.test(text))errors.push(label+': control character');
 if(/\b(?:TODO|TBD|placeholder|insert solution)\b/i.test(text))errors.push(label+': unfinished text');
 function visit(n){
  if(n.type==='inlineMath'||n.type==='math'){
   try{katex.renderToString(n.value,{throwOnError:true,strict:'ignore',trust:false});formulae++;}
   catch(e){errors.push(label+': '+e.message);}
  }
  if(n.type==='text'&&n.value.includes('$')&&n.position&&/(?<!\\)\$/.test(text.slice(n.position.start.offset,n.position.end.offset)))errors.push(label+': unparsed math delimiter');
  n.children?.forEach(visit);
 }
 visit(parser.parse(text));
}
for(const c of courses){
 const file=dir+'/'+c+'.json',bytes=readFileSync(file);
 const qs=JSON.parse(bytes),r={questions:qs.length,diagrams:0,topics:{},difficulty:{medium:0,hard:0},calculator:{yes:0,no:0},marks:0,sha256:hash(bytes)};
 assert.equal(qs.length,100,c+' must contain 100 new questions');
 for(const input of qs){
  const parsed=model.ibQuestionSchema.safeParse(input);
  if(!parsed.success){errors.push(input.id+': '+parsed.error.message);continue;}
  const q=parsed.data;
  assert.equal(q.subject,'math-'+c);
  assert.equal(q.source.document,'Independent syllabus-authored practice');
  assert.ok(q.number>=701&&q.number<=720);
  assert.ok(!ids.has(q.id),'Duplicate ID '+q.id);ids.add(q.id);
  assert.equal(q.status,'published');
  assert.ok(q.difficulty==='medium'||q.difficulty==='hard');
  assert.ok(q.parts.length>=2,'Substantive structured reasoning required: '+q.id);
  assert.ok(q.markScheme.some(g=>g.steps.some(s=>s.code.startsWith('M')||s.code.startsWith('R'))));
  const fp=q.stem+'\n'+q.parts.map(p=>p.prompt).join('\n');
  assert.ok(!prompts.has(fp),'Exact repeated prompt '+q.id);prompts.set(fp,q.id);
  r.topics[q.topicId]=(r.topics[q.topicId]??0)+1;r.difficulty[q.difficulty]++;r.marks+=q.marks;r.calculator[q.calculator?'yes':'no']++;
  markdown(q.stem,q.id+' stem');q.parts.forEach(p=>markdown(p.prompt,q.id+' '+p.label));
  q.markScheme.forEach(g=>g.steps.forEach(s=>markdown(s.text,q.id+' solution '+g.part)));
  if(q.diagramSvg){assert.ok(model.safeDiagram(q.diagramSvg));r.diagrams++;}
  const prompt=JSON.stringify(model.questionPrompt(q));
  assert.ok(!prompt.includes('verification')&&!prompt.includes('answerSummary')&&!prompt.includes('markScheme'),q.id+' private data exposure');
  const [topic,code]=q.syllabusCode.split('.').map(Number);
  const ranges=c==='ai-sl'?{1:8,2:6,3:6,4:11,5:8}:c==='aa-sl'?{1:9,2:11,3:8,4:12,5:11}:c==='aa-hl'?{1:16,2:16,3:18,4:14,5:19}:{1:15,2:10,3:16,4:19,5:18};
  assert.ok(code>=1&&code<=ranges[topic],q.id+' syllabus range');
 }
 assert.ok(r.diagrams>=80,c+' requires at least 80 diagram-based questions');
 assert.deepEqual(Object.values(r.topics),[20,20,20,20,20],c+' must add 20 questions to each topic');
 reports[c]=r;
}
if(errors.length){console.error(errors.join('\n'));process.exit(1);}
const report={status:'passed',method:'Actual production schema, part/mark totals, ID/source identity, syllabus ranges, distinct prompts, full Markdown/KaTeX parsing, safe diagrams and answer privacy',formulae,courses:reports};
if(!courseArg){mkdirSync('docs/ib-2026-maths',{recursive:true});writeFileSync('docs/ib-2026-maths/content-checks.json',JSON.stringify(report,null,2)+'\n');}
console.log(JSON.stringify(report));
