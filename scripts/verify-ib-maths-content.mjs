import assert from 'node:assert/strict';
import {readFileSync,readdirSync,existsSync} from 'node:fs';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
import {unified} from 'unified';
import remarkParse from 'remark-parse';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import katex from 'katex';
import {ibQuestionSchema,questionPrompt,safeDiagram} from '../lib/ib/question.ts';

const args=process.argv.slice(2),complete=args.includes('--complete'),requireCdn=args.includes('--require-cdn');
const courses=args.find(arg=>arg.startsWith('--course='))?.slice(9).split(',')??['math-aa-sl','math-ai-sl','math-aa-hl'];
const expectedHl={'number-algebra':249,functions:149,'geometry-trigonometry':202,'statistics-probability':169,'calculus-1':146,'calculus-2':167};
const legacyHl={'number-algebra':229,functions:129,'geometry-trigonometry':182,'statistics-probability':149,'calculus-1':126,'calculus-2':147};
const topics=['number-algebra','functions','geometry-trigonometry','statistics-probability','calculus'];
const parser=unified().use(remarkParse).use(remarkGfm).use(remarkMath);
const manifestPath='content/ib/maths-diagram-manifest.json';
const manifest=existsSync(manifestPath)?JSON.parse(readFileSync(manifestPath,'utf8')):{assets:{}};
const blueprint=JSON.parse(readFileSync('docs/ib-maths-reviews/syllabus-blueprint.json','utf8'));
const errors=[],ids=new Set(),fingerprints=new Map(),summary={};
let formulae=0,diagrams=0,tables=0;
function checkText(text,label) {
  if(/[\u0000-\u0009\u000b-\u001f]/.test(text))errors.push(`${label}: control character`);
  if(/\b(?:TODO|TBD|placeholder solution|INSERT SOLUTION)\b/i.test(text))errors.push(`${label}: unfinished text`);
  const lines=text.split(/\r?\n/);
  for(let i=0;i<lines.length;i++) {
    if(!/^\s*\|/.test(lines[i])||!/^\s*\|[\s:|\-]+\|\s*$/.test(lines[i+1]??''))continue;
    const arity=line=>(line.match(/(?<!\\)\|/g)??[]).length;
    const width=arity(lines[i]);
    for(let j=i+1;j<lines.length&&/^\s*\|/.test(lines[j]);j++)if(arity(lines[j])!==width||!/\|\s*$/.test(lines[j]))errors.push(`${label}: table row has inconsistent cells or attached paragraph`);
  }
  function visit(node) {
    if(node.type==='math'||node.type==='inlineMath') {
      try{katex.renderToString(node.value,{throwOnError:true,strict:'ignore',trust:false});formulae++;}catch(error){errors.push(`${label}: ${error.message}`);}
      if(node.type==='inlineMath'&&node.value.includes('\n'))errors.push(`${label}: newline inside inline formula`);
    }
    if(node.type==='table')tables++;
    if(node.type==='text'&&node.value.includes('$')&&node.position) {
      const raw=text.slice(node.position.start.offset,node.position.end.offset);
      if(/(?<!\\)\$/.test(raw))errors.push(`${label}: unparsed formula delimiter`);
    }
    node.children?.forEach(visit);
  }
  visit(parser.parse(text));
}
for(const course of courses) {
  assert.ok(['math-aa-sl','math-ai-sl','math-aa-hl'].includes(course));
  const directory=resolve('content/ib',course),files=existsSync(directory)?readdirSync(directory).filter(f=>f.endsWith('.json')):[];
  const report={questions:0,marks:0,collections:{},difficulty:{easy:0,medium:0,hard:0},calculator:{yes:0,no:0},styles:{},diagrams:0};
  summary[course]=report;
  const wanted=course==='math-aa-hl'?expectedHl:Object.fromEntries(topics.map(topic=>[topic,80]));
  for(const [topic,total] of Object.entries(wanted)) {
    const file=`${topic}.json`;
    if(!files.includes(file)){if(complete)errors.push(`${course}: missing ${file}`);continue;}
    const values=JSON.parse(readFileSync(resolve(directory,file),'utf8'));
    assert.ok(Array.isArray(values));report.collections[topic]=values.length;
    const numbers=new Set(values.map(q=>q.number));
    if(complete&&values.length!==total)errors.push(`${course}/${file}: ${values.length}/${total}`);
    if(complete)for(let n=1;n<=total;n++)if(!numbers.has(n))errors.push(`${course}/${file}: missing ${n}`);
    for(const input of values) {
      const parsed=ibQuestionSchema.safeParse(input);
      if(!parsed.success){errors.push(`${input.id}: ${parsed.error.message}`);continue;}
      const q=parsed.data;
      if(q.subject!==course)errors.push(`${q.id}: wrong course`);
      if(q.collectionId!==(course==='math-aa-hl'?topic:`${course==='math-aa-sl'?'aa-sl':'ai-sl'}-${topic}`))errors.push(`${q.id}: wrong file`);
      if(ids.has(q.id))errors.push(`${q.id}: duplicate ID`);ids.add(q.id);
      if(complete&&(q.status!=='published'||!q.syllabusCode||!q.level||!q.examStyle))errors.push(`${q.id}: incomplete publication metadata`);
      if(q.syllabusCode){
        const [theme,section]=q.syllabusCode.split('.'),bounds=blueprint.courses[course].allowedCodeRanges[theme];
        if(!bounds||Number(section)<bounds[0]||Number(section)>bounds[1])errors.push(`${q.id}: code outside this course's current syllabus`);
      }
      if(course!=='math-aa-hl'||q.number>legacyHl[topic])if(q.source.document!=='Independent syllabus-authored practice')errors.push(`${q.id}: new question needs independent authorship provenance`);
      if(course!=='math-aa-hl'&&q.level!=='sl')errors.push(`${q.id}: SL bank contains AHL content`);
      const fingerprint=createHash('sha256').update(q.stem+'\n'+q.parts.map(p=>p.prompt).join('\n')+'\n'+(q.diagramSvg??'')).digest('hex');
      if(fingerprints.has(fingerprint))errors.push(`${q.id}: identical question to ${fingerprints.get(fingerprint)}`);fingerprints.set(fingerprint,q.id);
      checkText(q.stem,`${q.id} stem`);q.parts.forEach(p=>checkText(p.prompt,`${q.id} (${p.label})`));
      for(const group of q.markScheme){
        const markedSteps=group.steps.filter(s=>s.code!=='AG');
        if(new Set(markedSteps.map(s=>s.text)).size!==markedSteps.length)errors.push(`${q.id} (${group.part}): repeated marking criterion`);
      }
      q.markScheme.forEach(g=>g.steps.forEach((s,i)=>checkText(s.text,`${q.id} scheme ${g.part}/${i+1}`)));
      for(const svg of [q.diagramSvg,q.markSchemeDiagramSvg].filter(Boolean)) {
        if(!safeDiagram(svg))errors.push(`${q.id}: unsafe SVG`);
        const hash=createHash('sha256').update(svg).digest('hex');
        if(requireCdn&&(manifest.origin!=='https://media.thrivingscholars.com'||manifest.assets[hash]?.key!==`ib/maths/2026-10-30/${hash}.svg`||manifest.assets[hash]?.bytes!==Buffer.byteLength(svg)))errors.push(`${q.id}: diagram not verified on Cloudflare`);
        diagrams++;report.diagrams++;
      }
      const prompt=questionPrompt(q);
      for(const key of ['markScheme','markSchemeDiagramSvg','markSchemeDiagramUrl','markSchemeDiagramCaption','answerSummary','source','verification','correctOption'])if(key in prompt)errors.push(`${q.id}: private ${key} in prompt`);
      report.questions++;report.marks+=q.marks;report.difficulty[q.difficulty]++;report.calculator[q.calculator?'yes':'no']++;report.styles[q.examStyle??'unclassified']=(report.styles[q.examStyle??'unclassified']??0)+1;
    }
  }
  if(complete&&course!=='math-ai-sl'&&(!report.calculator.yes||!report.calculator.no))errors.push(`${course}: missing calculator/no-calculator practice`);
  if(complete&&(!report.difficulty.easy||!report.difficulty.medium||!report.difficulty.hard))errors.push(`${course}: missing difficulty level`);
}
if(errors.length){console.error(errors.join('\n'));process.exitCode=1;}
else console.log(JSON.stringify({status:'passed',courses:summary,formulae,diagrams,tables,checks:'Distinct course schema, numbering, syllabus metadata, per-part marking totals, no identical prompts or marking points, full KaTeX/GFM rendering, safe diagrams, private solution separation'+(requireCdn?', verified Cloudflare images':'')}));
