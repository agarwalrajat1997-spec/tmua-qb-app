import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { createHash } from 'node:crypto';
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import katex from 'katex';
import { ibQuestionSchema, questionPrompt, safeDiagram } from '../lib/ib/question.ts';

const directory = resolve(process.argv.slice(2).find(arg => !arg.startsWith('--')) || 'content/ib/math-aa-hl');
const parser = unified().use(remarkParse).use(remarkGfm).use(remarkMath);
const expected = {'number-algebra':249,functions:149,'geometry-trigonometry':202,'statistics-probability':169,'calculus-1':146,'calculus-2':167};
let count=0, formulae=0, diagrams=0, drafts=0;
const errors=[], identifiers=new Set(), prompts=new Map(), counts={}, numbers={};
function checkMath(markdown, label) {
  if(/[\u0000-\u0009\u000b-\u001f]/.test(markdown)) errors.push(`${label}: control character (possibly a Python LaTeX escape)`);
  assert.ok(!/\b(?:TODO|TBD|INSERT SOLUTION|placeholder solution)\b/i.test(markdown),`${label}: unfinished text`);
  function visit(node) {
    if(node.type==='math'||node.type==='inlineMath') {
      if(node.type==='inlineMath' && node.value.includes('\n')) errors.push(`${label}: newline inside inline math (check escaped \\ne, \\nu or \\nabla)`);
      try { katex.renderToString(node.value,{throwOnError:true,strict:'ignore',trust:false}); formulae++; }
      catch(error) { errors.push(`${label}: ${error.message}`); }
    }
    // An unparsed dollar in authored text almost always means a broken formula.
    if(node.type==='text' && node.value.includes('$') && node.position) {
      const source=markdown.slice(node.position.start.offset,node.position.end.offset);
      if(/(?<!\\)\$/.test(source)) errors.push(`${label}: unparsed dollar delimiter near ${source.slice(0,120)}`);
    }
    if(node.children) node.children.forEach(visit);
  }
  visit(parser.parse(markdown));
}
for(const filename of readdirSync(directory).filter(f=>f.endsWith('.json') && Object.keys(expected).some(c=>f===`${c}.json`))) {
  const values=JSON.parse(readFileSync(resolve(directory,filename),'utf8'));
  assert.ok(Array.isArray(values),`${filename} must contain an array`);
  counts[filename.replace('.json','')]=values.length;
  numbers[filename.replace('.json','')]=new Set(values.map(q=>q.number));
  for(const input of values) {
    const parsed=ibQuestionSchema.safeParse(input);
    if(!parsed.success) { errors.push(`${input.id || filename}: ${parsed.error.message}`);continue; }
    const q=parsed.data;
    assert.ok(!identifiers.has(q.id),`Duplicate ID ${q.id}`); identifiers.add(q.id);
    assert.equal(`${q.collectionId}.json`,filename,`${q.id}: wrong collection file`);
    assert.equal(Number(q.id.slice(-3)),q.number,`${q.id}: unstable source number`);
    assert.equal(q.status==='published' ? q.markScheme.length>0 : true,true);
    const fingerprint=createHash('sha256').update(q.stem+'\n'+q.parts.map(p=>p.prompt).join('\n')).digest('hex');
    if(prompts.has(fingerprint)) errors.push(`${q.id}: duplicates ${prompts.get(fingerprint)}`);
    prompts.set(fingerprint,q.id);
    checkMath(q.stem,`${q.id} stem`);
    q.parts.forEach(p=>checkMath(p.prompt,`${q.id} (${p.label})`));
    q.markScheme.forEach(g=>g.steps.forEach((s,i)=>checkMath(s.text,`${q.id} scheme ${g.part}/${i+1}`)));
    for(const svg of [q.diagramSvg,q.markSchemeDiagramSvg].filter(Boolean)) { assert.ok(safeDiagram(svg),`${q.id}: unsafe diagram`);diagrams++; }
    const publicPrompt=questionPrompt(q);
    for(const hidden of ['markScheme','markSchemeDiagramSvg','answerSummary','source','verification']) assert.ok(!(hidden in publicPrompt),`${q.id}: leaked ${hidden}`);
    if(q.status==='draft')drafts++;
    count++;
  }
}
if(process.argv.includes('--complete')) for(const [collection,total] of Object.entries(expected)) {
  if(counts[collection]!==total) errors.push(`${collection}: ${counts[collection] ?? 0}/${total} reference records`);
  for(let number=1;number<=total;number++) if(!numbers[collection]?.has(number)) errors.push(`${collection}: missing reference question ${number}`);
}
if(process.argv.includes('--complete') && drafts) errors.push(`${drafts} questions still need publication review`);
if(errors.length) { console.error(errors.join('\n')); process.exitCode=1; }
else console.log(JSON.stringify({status:'passed',questions:count,published:count-drafts,drafts,formulae,diagrams,collections:counts,checks:'Schema, IDs, source mapping, no exact duplicates, per-part mark totals, LaTeX render, SVG safety and question/solution separation'}));
