import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import katex from 'katex';
import {unified} from 'unified';
import remarkParse from 'remark-parse';
import remarkGfm from 'remark-gfm';
import {ibHarness} from '../ib-component-harness.mjs';
const harness=ibHarness(),server=harness.load('lib/ib/physics-mocks.ts'),model=harness.load('lib/ib/physics-mock-model.ts');
const metas=model.PHYSICS_MOCKS.flatMap(s=>s.papers),seen=new Set(),records=[];let questions=0,parts=0,groups=0,marks=0,diagrams=0,occurrences=0,tables=0;const expressions=new Set();
function walk(n,fn){fn(n);for(const c of n.children||[])walk(c,fn);}
for(const meta of metas){
 const name=`content/ib/physics-mocks-2026/papers/${meta.id}.json`,raw=fs.readFileSync(name),paper=server.validatePhysicsMockPaper(JSON.parse(raw),meta);
 const text=[];
 for(const q of paper.questions){
  assert(!seen.has(q.id));seen.add(q.id);questions++;marks+=q.marks;parts+=q.parts.length;groups+=q.markScheme.length;diagrams+=Number(!!q.diagramSvg);
  text.push(q.stem,...q.parts.map(p=>p.prompt),...(q.options||[]).map(o=>o.text),...q.markScheme.flatMap(g=>g.steps.map(s=>s.text)));
  if(meta.course==='sl')assert.equal(q.level,'core');
  assert(q.sourceAnchors.every(a=>!/^ib-phy/.test(a.document)),q.id);
 }
 for(const t of text){
  assert.doesNotMatch(t,/[\u0000-\u0009\u000b-\u001f]/,'Accidental Python string-control escape');
  assert.doesNotMatch(t,/\\n\|/,'Unrenderable literal table row separator');
  for(const m of t.matchAll(/(?<!\\)\$\$([\s\S]*?)(?<!\\)\$\$|(?<!\\)\$([^$\n]+?)(?<!\\)\$/g)){
   const tex=(m[1]||m[2]).trim();katex.renderToString(tex,{throwOnError:true,strict:'error'});expressions.add(tex);occurrences++;
  }
  const tableBlocks=t.split(/\n\s*\n/).filter(b=>b.trim().startsWith('|')&&b.includes('\n|'));
  const ast=unified().use(remarkParse).use(remarkGfm).parse(t);let renderedTables=0;walk(ast,n=>{if(n.type==='table'){
   renderedTables++;const ncols=n.children[0].children.length;assert(n.children.every(row=>row.children.length===ncols),'Inconsistent table cells');
  }});
  assert.equal(renderedTables,tableBlocks.length,`Markdown table failed in ${meta.id}`);tables+=renderedTables;
 }
 if(meta.paper==='1'){
  const key=paper.questions.filter(q=>q.section==='1A').map(q=>q.correctOption).join('');
  for(let period=1;period<=8;period++)assert(![...key].every((c,i)=>c===key[i%period]),`Predictable answer-key cycle: ${meta.id}`);
 }
 records.push({id:paper.id,sha256:crypto.createHash('sha256').update(raw).digest('hex'),questions:paper.questions.length,parts:paper.questions.reduce((s,q)=>s+q.parts.length,0),marks:paper.marks,diagrams:paper.questions.filter(q=>q.diagramSvg).length,passed:true});
}
assert.equal(metas.length,10);assert.equal(questions,219);assert.equal(marks,640);assert(diagrams>=110);
// Exact prompt reuse against the old bank and within this series is forbidden.
const norm=s=>s.replace(/\s+/g,' ').trim();const bankStems=new Set();
for(const file of fs.readdirSync('content/ib/physics-hl').filter(f=>f.endsWith('.json')))
 for(const q of JSON.parse(fs.readFileSync(path.join('content/ib/physics-hl',file),'utf8')))bankStems.add(norm(q.stem));
const stems=new Set();for(const meta of metas){const p=JSON.parse(fs.readFileSync(`content/ib/physics-mocks-2026/papers/${meta.id}.json`));for(const q of p.questions){assert(!bankStems.has(norm(q.stem)),`Bank stem reused: ${q.id}`);assert(!stems.has(norm(q.stem)),`Duplicate new stem: ${q.id}`);stems.add(norm(q.stem));}}
const report={status:'passed',papers:10,questions,parts,markingGroups:groups,marks,diagrams,formulaOccurrences:occurrences,uniqueExpressions:expressions.size,markdownTables:tables,exactBankStemMatches:0,duplicateNewStems:0,records};
fs.writeFileSync('docs/ib-physics-mocks-2026/content-checks.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({...report,records:undefined}));
