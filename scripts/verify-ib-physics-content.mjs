import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
import {unified} from 'unified';
import remarkParse from 'remark-parse';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import katex from 'katex';
import {ibQuestionSchema,questionPrompt,safeDiagram} from '../lib/ib/question.ts';
import {physicsSyllabusSubtopics} from '../lib/ib/catalog.ts';

const expected={'space-time-motion':220,'particulate-matter':140,'wave-behaviour':140,fields:120,'nuclear-quantum':120};
const directory=resolve('content/ib/physics-hl');
const parser=unified().use(remarkParse).use(remarkGfm).use(remarkMath);
const complete=process.argv.includes('--complete');
const requireCdn=process.argv.includes('--require-cdn');
const cdnManifest=JSON.parse(readFileSync(resolve('content/ib/physics-diagram-manifest.json'),'utf8'));
const expansionManifest=JSON.parse(readFileSync('content/ib/expansion-diagram-manifest.json','utf8'));
const errors=[],ids=new Set(),fingerprints=new Map(),counts={},coverage={},difficulty={},types={};
let questions=0,formulae=0,questionDiagrams=0,solutionDiagrams=0,marks=0;
function mathCheck(source,label){
 if(/[\u0000-\u0009\u000b-\u001f]/.test(source))errors.push(label+': control character, possibly an escaped LaTeX command');
 if(/\\\\[A-Za-z]/.test(source))errors.push(label+': doubled LaTeX command escape');
 if(/\b(?:TODO|TBD|INSERT SOLUTION|placeholder solution)\b/i.test(source))errors.push(label+': unfinished content');
 function visit(node){
  if(node.type==='math'||node.type==='inlineMath'){
   if(node.type==='inlineMath'&&node.value.includes('\n'))errors.push(label+': newline inside inline mathematics');
   try{katex.renderToString(node.value,{throwOnError:true,trust:false,strict:'ignore'});formulae++;}catch(e){errors.push(label+': '+e.message);}
  }
  if(node.type==='text'&&node.value.includes('$')&&node.position){const raw=source.slice(node.position.start.offset,node.position.end.offset);if(/(?<!\\)\$/.test(raw))errors.push(label+': unparsed dollar delimiter near '+raw.slice(0,100));}
  if(node.children)node.children.forEach(visit);
 }
 visit(parser.parse(source));
}
for(const [name,total] of Object.entries(expected)){
 const file=resolve(directory,name+'.json');
 if(!readdirSync(directory).includes(name+'.json')){if(complete)errors.push(name+': missing collection');continue;}
 const data=JSON.parse(readFileSync(file,'utf8'));assert.ok(Array.isArray(data));counts[name]=data.length;
 if(complete&&data.length!==total)errors.push(`${name}: ${data.length}/${total} questions`);
 const numbers=new Set();
 for(const record of data){
  const parsed=ibQuestionSchema.safeParse(record);
  if(!parsed.success){errors.push(`${record.id}: ${parsed.error.message}`);continue;}
  const q=parsed.data;
  if(q.subject!=='physics-hl')errors.push(q.id+': incorrect subject');
  if(q.topicId!==name)errors.push(q.id+': incorrect theme file');
  if(ids.has(q.id))errors.push(q.id+': duplicate ID');ids.add(q.id);
  if(numbers.has(q.number))errors.push(q.id+': duplicate number');numbers.add(q.number);
  if(complete&&q.status!=='published')errors.push(q.id+': unpublished draft');
  const syllabus=physicsSyllabusSubtopics(q.topicId).find(s=>s.code===q.syllabusCode);
  if(!syllabus||syllabus.title!==q.subtopic)errors.push(q.id+': syllabus code/title mismatch');
  coverage[q.syllabusCode]=(coverage[q.syllabusCode]||0)+1;
  difficulty[q.difficulty]=(difficulty[q.difficulty]||0)+1;types[q.questionType]=(types[q.questionType]||0)+1;
  const prompt=q.stem+'\n'+q.parts.map(p=>p.prompt).join('\n')+'\n'+(q.options||[]).map(o=>o.text).join('\n');
  const fingerprint=createHash('sha256').update(prompt+'\n'+(q.diagramSvg??'')).digest('hex');
  if(fingerprints.has(fingerprint))errors.push(q.id+': exact duplicate of '+fingerprints.get(fingerprint));fingerprints.set(fingerprint,q.id);
  mathCheck(q.stem,q.id+' stem');q.parts.forEach(p=>mathCheck(p.prompt,q.id+' part '+p.label));
  q.markScheme.forEach(g=>g.steps.forEach((s,i)=>mathCheck(s.text,q.id+' scheme '+g.part+'/'+i)));
  (q.options||[]).forEach(o=>mathCheck(o.text,q.id+' option '+o.label));
  if(q.options){
   const normal=q.options.map(o=>o.text.toLowerCase().replace(/\s+/g,' ').trim());
   if(new Set(normal).size!==4)errors.push(q.id+': duplicate multiple-choice options');
   if(!q.markScheme[0].steps[0].text.includes(q.correctOption))errors.push(q.id+': scheme missing selected answer letter');
  }
  for(const key of ['diagramSvg','markSchemeDiagramSvg'])if(q[key]){
   if(!safeDiagram(q[key]))errors.push(q.id+': unsafe '+key);
   if(requireCdn){
    const hash=createHash('sha256').update(q[key]).digest('hex');
    const asset=cdnManifest.assets?.[hash]??expansionManifest.assets?.[hash];
    if(cdnManifest.origin!=='https://media.thrivingscholars.com'||!asset||!([`ib/physics-hl/2026-10-30/${hash}.svg`,`ib/expansion/2026-10-31/${hash}.svg`].includes(asset.key))||asset.bytes!==Buffer.byteLength(q[key]))errors.push(q.id+': missing or stale verified Cloudflare '+key);
   }
   if(key==='diagramSvg')questionDiagrams++;else solutionDiagrams++;
  }
  const publicQ=questionPrompt(q);
  for(const hidden of ['correctOption','markScheme','markSchemeDiagramSvg','markSchemeDiagramUrl','answerSummary','source','verification'])if(hidden in publicQ)errors.push(q.id+': leaked '+hidden);
  questions++;marks+=q.marks;
 }
 for(let n=1;n<=data.length;n++)if(!numbers.has(n))errors.push(name+': missing number '+n);
 if(complete)for(const s of physicsSyllabusSubtopics(name))if(!(coverage[s.code]>0))errors.push(name+': empty syllabus topic '+s.code);
}
if(errors.length){console.error(errors.join('\n'));process.exitCode=1;}
else console.log(JSON.stringify({status:'passed',questions,marks,formulae,questionDiagrams,solutionDiagrams,collections:counts,coverage,difficulty,types,complete,cloudflareRequired:requireCdn,checks:'Physics schema, all syllabus groups, unique IDs and prompts, exact part and scheme allocations, MCQ options and privacy, full Markdown/KaTeX rendering, safe vector diagrams and optional verified Cloudflare coverage'}));
