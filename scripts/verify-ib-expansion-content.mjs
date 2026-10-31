import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {unified} from 'unified';
import remarkParse from 'remark-parse';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import katex from 'katex';
import {ibQuestionSchema,questionPrompt,safeDiagram,questionAvailableForCourse} from '../lib/ib/question.ts';
const expected={'math-ai-hl':{'number-algebra':100,functions:100,'geometry-trigonometry':100,'statistics-probability':100,calculus:100},economics:{introduction:40,microeconomics:120,macroeconomics:100,'global-economy':100},'business-management':{'introduction-business':80,'human-resources':80,'finance-accounts':80,marketing:80,'operations-management':80}};
const physicsBaseline={'space-time-motion':200,'particulate-matter':120,'wave-behaviour':120,fields:100,'nuclear-quantum':100};
const manifests=['expansion','maths','physics','chemistry','biology'].map(n=>JSON.parse(readFileSync(`content/ib/${n}-diagram-manifest.json`,'utf8')));
const parser=unified().use(remarkParse).use(remarkGfm).use(remarkMath),errors=[],ids=new Set(),fingerprints=new Map(),summary={};
const requireCdn=process.argv.includes('--require-cdn');
let formulae=0,tables=0,diagrams=0,rubrics=0;
function checkText(text,label){
 if(/[\u0000-\u0009\u000b-\u001f]/.test(text))errors.push(label+': control character');
 if(/\b(?:TODO|TBD|placeholder solution|INSERT SOLUTION)\b/i.test(text))errors.push(label+': unfinished content');
 const lines=text.split(/\r?\n/);
 for(let i=0;i<lines.length;i++)if(/^\s*\|/.test(lines[i])&&/^\s*\|[\s:|\-]+\|\s*$/.test(lines[i+1]??'')){
  const arity=line=>(line.match(/(?<!\\)\|/g)??[]).length,width=arity(lines[i]);
  for(let j=i+1;j<lines.length&&/^\s*\|/.test(lines[j]);j++)if(arity(lines[j])!==width||!/\|\s*$/.test(lines[j]))errors.push(label+': malformed table');
 }
 function visit(node){
  if(node.type==='math'||node.type==='inlineMath'){
   try{katex.renderToString(node.value,{throwOnError:true,strict:'ignore',trust:false});formulae++;}catch(e){errors.push(label+': '+e.message);}
   if(node.type==='inlineMath'&&node.value.includes('\n'))errors.push(label+': multiline inline formula');
  }
  if(node.type==='table')tables++;
  if(node.type==='text'&&node.value.includes('$')&&node.position&&/(?<!\\)\$/.test(text.slice(node.position.start.offset,node.position.end.offset)))errors.push(label+': unparsed dollar delimiter');
  node.children?.forEach(visit);
 }
 visit(parser.parse(text));
}
for(const [subject,topics] of Object.entries({...expected,'physics-hl':Object.fromEntries(Object.keys(physicsBaseline).map(t=>[t,20]))})){
 const report={questions:0,marks:0,sl:0,ahl:0,collections:{},difficulty:{easy:0,medium:0,hard:0},styles:{}};summary[subject]=report;
 for(const [topic,count] of Object.entries(topics)){
  const all=JSON.parse(readFileSync(`content/ib/${subject}/${topic}.json`,'utf8'));
  const values=subject==='physics-hl'?all.filter(q=>q.number>physicsBaseline[topic]):all;
  if(values.length!==count)errors.push(`${subject}/${topic}: ${values.length}/${count}`);
  report.collections[topic]=values.length;
  for(const input of values){
   const parsed=ibQuestionSchema.safeParse(input);if(!parsed.success){errors.push(input.id+': '+parsed.error.message);continue;}
   const q=parsed.data;
   if(ids.has(q.id))errors.push(q.id+': duplicate ID');ids.add(q.id);
   if(q.subject!==subject||q.topicId!==topic||q.status!=='published')errors.push(q.id+': incorrect publication metadata');
   if(q.source.document!=='Independent syllabus-authored practice')errors.push(q.id+': incorrect authorship record');
   const fingerprint=createHash('sha256').update(q.stem+'\n'+q.parts.map(p=>p.prompt).join('\n')+'\n'+(q.diagramSvg??'')).digest('hex');
   if(fingerprints.has(fingerprint))errors.push(q.id+': exact duplicate of '+fingerprints.get(fingerprint));fingerprints.set(fingerprint,q.id);
   checkText(q.stem,q.id+' stem');q.parts.forEach(p=>checkText(p.prompt,q.id+' part '+p.label));
   for(const g of q.markScheme){
    const marked=g.steps.filter(s=>!['AG','IND'].includes(s.code));
    if(new Set(marked.map(s=>s.text)).size!==marked.length)errors.push(q.id+': repeated marking point');
    g.steps.forEach(s=>checkText(s.text,q.id+' scheme '+g.part));
    if(g.rubric){rubrics++;for(const band of g.rubric.bands??[])checkText(band.descriptor,q.id+' band');for(const criterion of g.rubric.criteria??[])for(const band of criterion.bands)checkText(band.descriptor,q.id+' criterion');}
   }
   for(const field of ['diagramSvg','markSchemeDiagramSvg'])if(q[field]){
    const svg=q[field],hash=createHash('sha256').update(svg).digest('hex');if(!safeDiagram(svg))errors.push(q.id+': unsafe SVG');diagrams++;
    if(requireCdn&&!manifests.some(m=>m.origin==='https://media.thrivingscholars.com'&&m.assets[hash]?.bytes===Buffer.byteLength(svg)&&m.assets[hash]?.key.endsWith('/'+hash+'.svg')))errors.push(q.id+': diagram not verified on Cloudflare');
   }
   const prompt=questionPrompt(q);
   for(const hidden of ['markScheme','markSchemeDiagramSvg','markSchemeDiagramUrl','markSchemeDiagramCaption','answerSummary','source','verification','correctOption'])if(hidden in prompt)errors.push(q.id+': leaked private '+hidden);
   if(subject==='physics-hl'&&q.level!=='core')errors.push(q.id+': new SL content outside core');
   if(subject==='economics'&&q.examStyle==='paper-2'&&q.level!=='sl')errors.push(q.id+': shared Paper 2 contains AHL-only content');
   if(q.examStyle==='paper-3'&&q.level!=='ahl')errors.push(q.id+': Paper 3 must be HL');
   if(subject==='business-management'&&q.examStyle==='paper-1'&&q.level!=='sl')errors.push(q.id+': shared Business Paper 1 contains AHL content');
   if(subject==='business-management'&&q.examStyle==='paper-3'){
    if(q.marks!==25||q.parts.map(p=>p.marks).join(',')!=='2,6,17')errors.push(q.id+': Paper 3 allocation must be 2+6+17');
    const criteria=q.markScheme.at(-1).rubric?.criteria;
    if(criteria?.map(c=>c.maxMarks).join(',')!=='4,4,6,3')errors.push(q.id+': Paper 3 plan analytic criteria must be 4+4+6+3');
   }
   if(subject==='math-ai-hl'&&(!q.calculator||!/^([1-5])\.\d+$/.test(q.syllabusCode)))errors.push(q.id+': invalid AI HL metadata');
   report.questions++;report.marks+=q.marks;report.difficulty[q.difficulty]++;report.styles[q.examStyle??q.questionType]=(report.styles[q.examStyle??q.questionType]??0)+1;
   if(q.level==='sl'||q.level==='core')report.sl++;else report.ahl++;
  }
 }
}
if(errors.length){console.error(errors.join('\n'));process.exitCode=1;}else console.log(JSON.stringify({status:'passed',courses:summary,formulae,tables,diagrams,rubrics,cloudflareRequired:requireCdn,checks:'Schema and exact mark totals, continuous best-fit/analytic rubric bands, original provenance, nonduplicated prompts/criteria, all formulae/tables, SL/HL availability, Paper 3 allocation, private answers, safe Cloudflare figures'}));
