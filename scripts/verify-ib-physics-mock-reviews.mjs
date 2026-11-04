import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { lstatSync, readFileSync, readdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

export const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
export const CONTENT = 'content/ib/physics-mocks-2026';
export const DOCS = 'docs/ib-physics-mocks-2026';
export const MANIFEST = `${CONTENT}/review-manifest.json`;
export const EXPECTED = new Map(['hl','sl'].flatMap(course => (course === 'hl' ? ['a','b','c'] : ['a','b']).flatMap(set => ['1','2'].map(paper => {
  const id = `physics-${course}-set-${set}-paper-${paper}`;
  return [id,{course,set:set.toUpperCase(),paper,minutes:course === 'sl' ? 90 : paper === '1' ? 120 : 150,marks:course === 'sl' ? paper === '1' ? 45 : 50 : paper === '1' ? 60 : 90,questions:paper === '1' ? course === 'sl' ? 27 : 42 : course === 'sl' ? 6 : 9}];
}))));
export const sha256 = value => createHash('sha256').update(value).digest('hex');
const read = (root,file) => { assert.ok(lstatSync(join(root,file)).isFile(), `${file}: regular file required`); return readFileSync(join(root,file)); };
const json = (root,file) => JSON.parse(read(root,file).toString('utf8'));
const sorted = values => [...values].sort();
const sameSet = (a,b,context) => { assert.equal(new Set(a).size,a.length,`${context}: duplicate identity`); assert.deepEqual(sorted(a),sorted(b),`${context}: missing or unexpected identity`); };
const unique = (records,key,context) => { assert.ok(Array.isArray(records) && records.length,`${context}: missing records`);const map=new Map();for(const r of records){const id=key(r);assert.ok(typeof id==='string' && id && !map.has(id),`${context}: duplicate/invalid ${id}`);map.set(id,r);}return map; };
const passed = (r,c) => assert.equal(r.status,'passed',`${c}: not passed`);
const noFindings = (r,c) => assert.deepEqual(r,[],`${c}: unresolved findings`);
const has = (r,k) => Object.hasOwn(r,k);
const meaningful = (s,c,min=25) => { assert.ok(typeof s==='string' && s.trim().length>=min,`${c}: substantive evidence required`);assert.ok(!/^(?:passed|reviewed|verified|checked|all good|ok|done)[.\s!]*$/i.test(s.trim()),`${c}: canned evidence`); };
const sortObject = v => Array.isArray(v) ? v.map(sortObject) : v && typeof v==='object' ? Object.fromEntries(Object.keys(v).sort().map(k=>[k,sortObject(v[k])])) : v;
export const questionHash = q => sha256(JSON.stringify(sortObject(q)));
const groups = q => q.questionType==='multiple-choice' ? [{label:'',marks:1}] : q.parts;

/** Re-evaluate evidence numerically; a passed badge alone is insufficient. */
export function validateAssertion(check,context) {
  meaningful(check.name ?? check.test,`${context} name`,3);
  if(has(check,'status')) passed(check,context);
  if(has(check,'passed')) assert.equal(check.passed,true,`${context}: assertion failed`);
  const actual=check.actual ?? check.computed ?? check.value, expected=check.expected;
  if(typeof actual==='boolean' || typeof expected==='boolean'){const a=typeof actual==='boolean'?Number(actual):actual,b=typeof expected==='boolean'?Number(expected):expected;assert.ok([0,1].includes(a)&&[0,1].includes(b));assert.equal(a,b,`${context}: physical predicate is false`);assert.ok((check.absoluteTolerance ?? check.tolerance ?? 0)<=1e-7);return 1;}
  assert.ok(typeof actual==='number' && Number.isFinite(actual),`${context}: finite computed value required`);
  assert.ok(typeof expected==='number' && Number.isFinite(expected),`${context}: finite reference value required`);
  const tolerance=check.absoluteTolerance ?? check.tolerance ?? 0;
  assert.ok(typeof tolerance==='number' && Number.isFinite(tolerance) && tolerance>=0,`${context}: invalid tolerance`);
  // Physical quantities span many orders of magnitude. Bound tolerance by its
  // reference scale rather than imposing a dimensionally meaningless fixed cap.
  assert.ok(tolerance <= (expected===0 ? 1e-7 : .02*Math.abs(expected)),`${context}: tolerance would conceal a material numerical error`);
  assert.ok(Math.abs(actual-expected)<=tolerance,`${context}: recorded numerical statement is false`);
  return 1;
}

export function validateMarkdownTables(text,context) {
  assert.ok(!/\\n\|/.test(text),`${context}: literal escaped table newline`);
  const lines=text.split(/\r?\n/);let count=0;
  const cells=line=>line.trim().replace(/^\|/,'').replace(/\|$/,'').split(/(?<!\\)\|/).map(s=>s.trim());
  for(let i=0;i<lines.length;i++) if(/^\s*\|/.test(lines[i])) {
    const rows=[];while(i<lines.length && /^\s*\|/.test(lines[i])) rows.push(cells(lines[i++]));i--;
    assert.ok(rows.length>=3,`${context}: table needs header, delimiter and data`);
    assert.ok(rows[0].length>=2 && rows.every(r=>r.length===rows[0].length),`${context}: inconsistent table columns`);
    assert.ok(rows[1].every(s=>/^:?-{3,}:?$/.test(s)),`${context}: invalid Markdown table delimiter`);count++;
  }
  return count;
}

function bindReports(report,ids,bindings,context) {
  const map=unique(report.papers,r=>r.id,context);sameSet([...map.keys()],ids,context);
  for(const [id,r] of map){assert.equal(r.sha256,bindings.get(id).canonicalSha256,`${id}: changed since ${context}`);if(r.questions!==undefined) assert.equal(r.questions,bindings.get(id).questions);if(r.marks!==undefined) assert.equal(r.marks,bindings.get(id).marks);}
}
function reviewParts(record,q,context) {
  if(has(record,'status')) passed(record,context);
  assert.equal(record.fullStemAndSchemeRead ?? record.fullStemOptionsAndSchemeRead,true,`${context}: full prompt/scheme review missing`);
  const parts=unique(record.parts,p=>p.part || '(unparted)',`${context} parts`);
  sameSet([...parts.keys()],groups(q).map(p=>p.label || '(unparted)'),`${context} exact part coverage`);
  for(const part of groups(q)){const r=parts.get(part.label || '(unparted)');assert.equal(r.marks,part.marks,`${context} part marks`);meaningful(r.reasoning ?? r.review,`${context}(${part.label}) reasoning`);if(has(r,'status')) passed(r,context);}
}
function checkCorrectText(q,text,label,context) {
  assert.equal(typeof text,'string',`${context}: independently solved option text missing`);
  const matches=q.options.filter(o=>o.text===text);assert.equal(matches.length,1,`${context}: independent option text is not unique`);assert.equal(matches[0].label,q.correctOption,`${context}: wrong key`);if(label!==undefined) assert.equal(label,q.correctOption,`${context}: stale key`);
}

function validateHlIndependent(report,ids,papers,bindings,context) {
  passed(report,context);meaningful(report.reviewer,`${context} reviewer`,4);if(has(report,'reviewerDifferentFromAuthor')){assert.equal(report.reviewerDifferentFromAuthor,true);assert.notEqual(report.author,report.reviewer);}else assert.match(report.reviewer,/independent/i,`${context}: independence declaration missing`);meaningful(report.method,`${context} method`);bindReports(report,ids,bindings,context);
  if(has(report,'openFindings')) noFindings(report.openFindings,context);
  if(has(report,'findings')) noFindings(report.findings,context);
  const expected=ids.flatMap(id=>papers.get(id).questions),map=unique(report.questionReviews ?? report.questions,r=>r.questionId,context);
  sameSet([...map.keys()],expected.map(q=>q.id),`${context} questions`);
  const checks=report.checks;assert.ok(Array.isArray(checks) && checks.length>=expected.length,`${context}: scientific assertions missing`);
  let assertions=0,keyAssertions=0;const reasonings=new Set();
  for(const q of expected){const rec=map.get(q.id);reviewParts(rec,q,q.id);const qs=checks.filter(c=>c.questionId===q.id);assert.ok(qs.length,`${q.id}: missing independent evidence`);
    for(const c of qs){if(has(c,'expectedOption')){assert.equal(c.passed,true);checkCorrectText(q,c.expectedOptionText ?? c.expectedCorrectText,c.expectedOption,q.id);keyAssertions++;}else assertions+=validateAssertion(c,q.id);}
    if(q.questionType==='multiple-choice'){const explicitKeys=qs.filter(c=>has(c,'expectedOption'));if(has(rec,'solvedCorrectOptionText')){assert.equal(explicitKeys.length,0);checkCorrectText(q,rec.solvedCorrectOptionText,rec.currentCorrectOptionLabel,q.id);keyAssertions++;}else assert.equal(explicitKeys.length,1,`${q.id}: exactly one reviewed MCQ key required`);}
    for(const part of rec.parts) {const reason=part.reasoning.trim().replace(/\s+/g,' ');assert.ok(!reasonings.has(reason),`${q.id}: repeated/canned per-part review`);reasonings.add(reason);if(has(part,'checkNames')) {assert.ok(Array.isArray(part.checkNames));for(const name of part.checkNames) assert.ok(qs.some(c=>c.name===name),`${q.id}: missing linked calculation ${name}`);}}
  }
  if(has(report,'numericAndKeyAssertions')) assert.equal(report.numericAndKeyAssertions,assertions+keyAssertions,`${context} assertion count`);else assert.equal(report.numericCheckCount,assertions,`${context} numeric count`);assert.equal(keyAssertions,40);
  const figures=report.nativeFigureReviews ?? report.figuresReviewed ?? report.diagrams;assert.ok(Array.isArray(figures),`${context}: native figure ledger missing`);
  validateFigures(figures,expected,`${context} figures`);
  return assertions+keyAssertions;
}
function validateFigures(records,questions,context) {
  const expected=questions.filter(q=>q.diagramSvg),map=unique(records,r=>r.questionId ?? r.id,context);sameSet([...map.keys()],expected.map(q=>q.id),context);
  for(const q of expected){const r=map.get(q.id);passed(r,q.id);assert.equal(r.svgSha256,sha256(q.diagramSvg),`${q.id}: figure changed since scientific inspection`);assert.match(r.nativePngSha256,/^[a-f0-9]{64}$/);assert.equal(r.scientificGeometryChecked ?? r.scientificContentChecked,true);assert.equal(r.legible ?? r.legibilityChecked,true);}
}
function validateSl(scope,numeric,native,ids,papers,bindings) {
  for(const [r,c] of [[scope,'SL scope review'],[numeric,'SL numerical review'],[native,'SL native review']]) passed(r,c);
  meaningful(scope.reviewer,'SL independent reviewer');assert.match(scope.reviewer,/independent/i);meaningful(numeric.scope,'SL numerical independent method');assert.match(numeric.scope,/independent/i);
  bindReports(scope,ids,bindings,'SL scope');bindReports(numeric,ids,bindings,'SL numerical');
  const expected=ids.flatMap(id=>papers.get(id).questions),sm=unique(scope.records,r=>r.questionId,'SL scope'),nm=unique(numeric.records,r=>r.id,'SL numerical');
  sameSet([...sm.keys()],expected.map(q=>q.id),'SL scope question coverage');sameSet([...nm.keys()],expected.map(q=>q.id),'SL numeric question coverage');
  let assertions=0,sanity=0;const reasonings=new Set();
  for(const q of expected){const s=sm.get(q.id),r=nm.get(q.id);passed(s,q.id);passed(r,q.id);reviewParts(s,q,q.id);assert.equal(r.fullStemPartsOptionsAndSchemeRead,true);assert.equal(r.canonicalQuestionSha256,questionHash(q),`${q.id}: numeric reviewer stale`);sameSet(r.partLabelsRead,q.parts.map(p=>p.label),`${q.id}: numeric part labels`);
    for(const part of s.parts){const reason=part.review.trim().replace(/\s+/g,' ');assert.ok(!reasonings.has(reason),`${q.id}: repeated/canned SL per-part review`);reasonings.add(reason);}
    for(const c of r.numericChecks) assertions+=validateAssertion(c,q.id);
    for(const c of s.independentSanityChecks) sanity+=validateAssertion(c,q.id);
    if(q.questionType==='multiple-choice'){meaningful(r.independentPhysicalReasoning,`${q.id}: numeric physical reasoning`);assert.equal(r.allFourOptionsEvaluated,true);checkCorrectText(q,r.uniqueCorrectOptionText,r.correctOption,q.id);assert.equal(s.optionTextReview.independentTextMatch,true);checkCorrectText(q,s.optionTextReview.expectedCorrectOptionText,s.optionTextReview.currentCorrectLabel,q.id);}
  }
  assert.equal(assertions,numeric.independentCalculationChecks);assert.equal(sanity,scope.independentSanityAssertionCount);assert.equal(numeric.mcqOptionsReviewed,200);assert.equal(scope.questions,66);assert.equal(numeric.questionsReviewed,66);
  noFindings(scope.openFindings,'SL scope');noFindings(numeric.unresolvedFindings,'SL numeric');noFindings(native.unresolvedFindings,'SL native');
  sameSet(Object.keys(native.paperHashes),ids,'SL native paper hashes');for(const id of ids) assert.equal(native.paperHashes[id],bindings.get(id).canonicalSha256);
  validateFigures(native.figures,expected,'SL native figures');assert.equal(native.figuresReviewed,expected.filter(q=>q.diagramSvg).length);
  return assertions+sanity+50;
}

function validateAuthor(report,ids,papers,bindings,context) {
  assert.ok(report.status==='passed' || report.status==='passed; independent review required',`${context}: author checks not passed`);bindReports(report,ids,bindings,context);
  const expected=ids.flatMap(id=>papers.get(id).questions),records=report.records ?? report.questions ?? report.questionReviews;
  const map=unique(records,r=>r.question ?? r.questionId ?? r.id,context);sameSet([...map.keys()],expected.map(q=>q.id),`${context} author question evidence`);
  let assertions=0;
  const flat=report.checks ?? [];
  for(const c of flat) assertions+=validateAssertion(c,context);
  for(const q of expected){const r=map.get(q.id);if(has(r,'status')) passed(r,q.id);if(r.questionSha256) assert.equal(r.questionSha256,questionHash(q));
    const cs=r.checks ?? r.checkNames ?? [];assert.ok(Array.isArray(cs),`${q.id}: author check links`);
    for(const c of cs){if(typeof c==='string') assert.ok(flat.some(x=>x.name===c),`${q.id}: missing author calculation ${c}`);else if(has(c,'expected')) assertions+=validateAssertion(c,q.id);else meaningful(c.evidence ?? c.reason,`${q.id}: author physical reasoning`);}
    const parts=r.partReviews ?? r.authorPartReviews ?? (r.parts?.length && r.parts.every(p=>p && typeof p==='object')?r.parts:undefined);
    if(parts){const expectedParts=(r.partReviews || r.authorPartReviews)?q.parts:groups(q);sameSet(parts.map(p=>p.part),expectedParts.map(p=>p.label),`${q.id}: author part labels`);for(const part of parts){const orig=expectedParts.find(p=>p.label===part.part);assert.equal(part.marks,orig.marks);const deriv=part.authorDerivation ?? part.derivation ?? part.reasoning;meaningful(Array.isArray(deriv)?deriv.join(' '):deriv,`${q.id}: author derivation`);if(has(part,'additiveMarkCodeSum')) assert.equal(part.additiveMarkCodeSum,part.marks);if(part.checkNames) for(const name of part.checkNames) assert.ok(flat.some(c=>c.name===name),`${q.id}: missing author part calculation ${name}`);}}
    assert.ok(cs.length || typeof r.analyticalReview==='string' || parts?.length,`${q.id}: empty author evidence`);
  }
  assert.ok(assertions>0,`${context}: no executable numeric author evidence`);if(has(report,'calculationCount')) assert.equal(report.calculationCount,assertions);if(has(report,'authorCalculationCount')) assert.equal(report.authorCalculationCount,assertions);if(typeof report.numericChecks==='number') assert.equal(report.numericChecks,assertions);if(has(report,'allNamedChecksPassed')) assert.equal(report.allNamedChecksPassed,true);return assertions;
}

export function visiblePdfPageCount(raw) {
  const text=raw.toString('latin1');assert.ok(text.startsWith('%PDF-'));assert.ok(!/\/ObjStm\b|\/Encrypt\b/.test(text),'PDF page inspection requires unencrypted visible objects');return [...text.matchAll(/\/Type\s*\/Page\b/g)].length;
}

export function readReviewEvidence({root=ROOT}={}) {
  const spec=json(root,`${DOCS}/specification.json`);assert.equal(spec.syllabus.firstAssessment,2025);assert.equal(spec.assessment.sl.paper2.marks,50);assert.equal(spec.assessment.hl.paper2.minutes,150);assert.equal(spec.assessment.sharedPaper1Clock,true);assert.equal(spec.assessment.calculatorOnEveryPaper,true);assert.equal(spec.assessment.paper3Exists,false);assert.equal(spec.authoringPolicy.sourceQuestionBankReuse,false);
  meaningful(read(root,`${DOCS}/research.md`).toString('utf8'),'Official research',100);meaningful(read(root,`${DOCS}/README.md`).toString('utf8'),'Reproducibility README',100);
  const provenance=json(root,`${DOCS}/source-provenance.json`);passed(provenance,'Source provenance');assert.equal(provenance.summary.pdfs,13);assert.equal(provenance.summary.pages,221);assert.equal(provenance.summary.allOriginalBytesUnchanged,true);const sources=unique(provenance.files,r=>r.filename,'Source files');sameSet([...sources.keys()],['1','2','49','6','9','a','c','f','q','s','v','x','y'].map(s=>`${s}.pdf`),'Supplied sources');
  for(const s of sources.values()){assert.match(s.sha256,/^[a-f0-9]{64}$/);assert.ok(Number.isInteger(s.pageCount)&&s.pageCount>0);assert.ok(Number.isInteger(s.bytes)&&s.bytes>0);}assert.equal([...sources.values()].reduce((n,s)=>n+s.pageCount,0),221);
  const catalog=json(root,`${CONTENT}/catalog.json`);assert.equal(catalog.length,5);sameSet(catalog.map(s=>s.id),['physics-hl-challenge-a','physics-hl-challenge-b','physics-hl-challenge-c','physics-sl-challenge-a','physics-sl-challenge-b'],'Catalogue sets');const metas=catalog.flatMap(s=>{assert.equal(s.status,'published');assert.equal(s.year,2026);assert.equal(s.papers.length,2);for(const p of s.papers){assert.equal(p.mockId,s.id);assert.equal(p.course,s.course);assert.equal(p.set,s.set);}return s.papers;});sameSet(metas.map(p=>p.id),[...EXPECTED.keys()],'Catalogue timed papers');
  sameSet(readdirSync(join(root,CONTENT,'papers')).filter(f=>f.endsWith('.json')),[...EXPECTED.keys()].map(id=>`${id}.json`),'Canonical paper files');
  const papers=new Map(),bindings=new Map(),questions=new Map(),expressions=new Set(),diagramMap=new Map(),stems=new Set();
  const summary={papers:10,sets:5,questions:0,parts:0,markingGroups:0,marks:0,diagrams:0,markdownTables:0,authorChecks:0,independentChecks:0,pdfPages:0,questionPages:0,solutionPages:0};
  for(const meta of metas){const exp=EXPECTED.get(meta.id),file=`${CONTENT}/papers/${meta.id}.json`,raw=read(root,file),p=JSON.parse(raw);assert.equal(p.id,meta.id);for(const key of ['course','set','paper','minutes','marks']) assert.equal(p[key],exp[key],`${p.id}: ${key}`);for(const key of ['id','mockId','course','set','paper','title','minutes','marks','calculator']) assert.equal(p[key],meta[key],`${p.id}: catalogue ${key}`);assert.equal(p.calculator,true);assert.equal(meta.pdfUrl,`/ib-mock-solutions/${p.id}.pdf`);assert.equal(meta.status,'published');assert.equal(meta.year,2026);assert.equal(meta.questionCount,exp.questions);assert.equal(p.questions.length,exp.questions);assert.equal(p.questions.reduce((n,q)=>n+q.marks,0),p.marks);
    const sections=p.paper==='1'?['1A','1B']:['2'];assert.deepEqual(meta.sections,sections);if(p.paper==='2') assert.deepEqual(p.questions.map(q=>q.marks),p.course==='hl'?Array(9).fill(10):[8,8,8,8,9,9]);
    for(const section of sections){const qs=p.questions.filter(q=>q.section===section);const n=section==='1A' ? p.course==='hl'?40:25 : section==='1B'?2:exp.questions;sameSet(qs.map(q=>q.number),Array.from({length:n},(_,i)=>i+1),`${p.id}: ${section} numbers`);if(section==='1A'){const keys=qs.map(q=>q.correctOption);for(let period=1;period<=8;period++) assert.ok(!keys.every((k,i)=>k===keys[i%period]),`${p.id}: repeated ${period}-position MCQ answer-key cycle`);for(const letter of 'ABCD') assert.ok(keys.filter(k=>k===letter).length<=Math.ceil(keys.length*.45),`${p.id}: severe answer-position bias`);}}
    for(const q of p.questions){assert.ok(!questions.has(q.id),`Duplicate question ${q.id}`);assert.ok(sections.includes(q.section));meaningful(q.stem,`${q.id} stem`,15);const norm=q.stem.replace(/\s+/g,' ').trim();assert.ok(!stems.has(norm),'Duplicate new stems');stems.add(norm);assert.equal(q.difficulty,'hard');assert.ok(['core','ahl'].includes(q.level));if(p.course==='sl') assert.equal(q.level,'core');assert.ok(Array.isArray(q.syllabusRefs)&&q.syllabusRefs.length);for(const ref of q.syllabusRefs){assert.ok(ref==='Tools'||has(spec.topicCatalogue,ref),`${q.id}: unknown reference ${ref}`);if(p.course==='sl'&&ref!=='Tools') assert.notEqual(spec.topicCatalogue[ref].level,'hl-only',`${q.id}: AHL-only reference in SL`);}
      assert.equal(q.id,`phy-${p.course}-${p.set.toLowerCase()}-${q.section.toLowerCase()}-${String(q.number).padStart(2,'0')}`,`${q.id}: section identity`);assert.ok(q.sourceAnchors.length);for(const anchor of q.sourceAnchors){assert.ok(sources.has(anchor.document),`${q.id}: unknown source`);assert.ok(Number.isInteger(anchor.page)&&anchor.page>=1&&anchor.page<=sources.get(anchor.document).pageCount);meaningful(anchor.focus,`${q.id} source focus`,10);}meaningful(q.changeNotes,`${q.id} originality rationale`);meaningful(q.cognitiveDemand,`${q.id} thinking demand`,15);
      const gs=groups(q),ms=unique(q.markScheme,g=>g.part || '(unparted)',`${q.id} scheme`);sameSet([...ms.keys()],gs.map(g=>g.label || '(unparted)'),`${q.id} marking groups`);assert.equal(gs.reduce((n,g)=>n+g.marks,0),q.marks);
      if(q.section==='1A'){assert.equal(q.questionType,'multiple-choice');assert.equal(q.marks,1);assert.deepEqual(q.parts,[]);sameSet(q.options.map(o=>o.label),[...'ABCD'],`${q.id} option labels`);assert.equal(new Set(q.options.map(o=>o.text)).size,4);assert.match(q.correctOption,/^[ABCD]$/);}else{assert.equal(q.questionType,q.section==='1B'?'data-based':'structured');assert.ok(q.parts.length);if(q.section==='1B') assert.equal(q.marks,10);for(const g of q.parts) meaningful(g.prompt,`${q.id} part prompt`,4);}
      for(const g of gs){assert.ok(Number.isInteger(g.marks)&&g.marks>0);const steps=ms.get(g.label || '(unparted)').steps;assert.ok(steps.length);assert.equal(steps.reduce((n,s)=>{assert.match(s.code,/^[MAR][1-9]\d*$/);meaningful(s.text,`${q.id} worked point`,3);return n+Number(s.code.slice(1));},0),g.marks,`${q.id} additive marks`);}
      if(q.diagramSvg){assert.match(q.diagramSvg,/^<svg\b/);assert.ok(!/<(?:script|foreignObject|image|defs|style)\b|\bon\w+\s*=|(?:href|url)\s*[:=(]/i.test(q.diagramSvg),'Unsafe scientific SVG');diagramMap.set(q.id,q.diagramSvg);summary.diagrams++;}
      const texts=[q.stem,...q.parts.map(g=>g.prompt),...(q.options||[]).map(o=>o.text),...q.markScheme.flatMap(g=>g.steps.map(s=>s.text))];for(const text of texts){summary.markdownTables+=validateMarkdownTables(text,q.id);for(const m of text.matchAll(/(?<!\\)\$\$([\s\S]*?)(?<!\\)\$\$|(?<!\\)\$([^$\n]+?)(?<!\\)\$/g)) expressions.add((m[1]??m[2]).trim());}
      questions.set(q.id,q);summary.parts+=q.parts.length;summary.markingGroups+=gs.length;
    }
    papers.set(p.id,p);bindings.set(p.id,{id:p.id,questionFile:file,canonicalSha256:sha256(raw),questions:p.questions.length,marks:p.marks,minutes:p.minutes});summary.questions+=p.questions.length;summary.marks+=p.marks;
  }
  assert.equal(summary.questions,219);assert.equal(summary.marks,640);assert.equal(summary.parts,218);assert.equal(summary.markingGroups,388);assert.ok(summary.diagrams>=Math.ceil(summary.questions/2),'At least half the questions require useful reviewed scientific figures');
  const ids=[...EXPECTED.keys()];for(const set of ['a','b','c']){const subset=ids.filter(id=>id.startsWith(`physics-hl-set-${set}-`)),independentReview=`${DOCS}/hl-${set}-independent-review.json`;summary.authorChecks+=validateAuthor(json(root,`${DOCS}/hl-${set}-author-checks.json`),subset,papers,bindings,`HL ${set} author`);summary.independentChecks+=validateHlIndependent(json(root,independentReview),subset,papers,bindings,`HL ${set} independent`);for(const id of subset) Object.assign(bindings.get(id),{authorReview:`${DOCS}/hl-${set}-author-checks.json`,independentReview});}
  const slIds=ids.filter(id=>id.startsWith('physics-sl-'));for(const set of ['a','b']) summary.authorChecks+=validateAuthor(json(root,`${DOCS}/sl-${set}-author-checks.json`),slIds.filter(id=>id.includes(`-set-${set}-`)),papers,bindings,`SL ${set} author`);
  summary.independentChecks+=validateSl(json(root,`${DOCS}/sl-scope-independent-review.json`),json(root,`${DOCS}/sl-numerical-independent-review.json`),json(root,`${DOCS}/sl-native-independent-review.json`),slIds,papers,bindings);
  for(const id of slIds) Object.assign(bindings.get(id),{authorReview:`${DOCS}/sl-${papers.get(id).set.toLowerCase()}-author-checks.json`,independentReview:`${DOCS}/sl-scope-independent-review.json`,independentNumericReview:`${DOCS}/sl-numerical-independent-review.json`});
  const content=json(root,`${DOCS}/content-checks.json`);passed(content,'Content validation');for(const k of ['papers','questions','parts','markingGroups','marks','diagrams','markdownTables']) assert.equal(content[k],summary[k],`Content totals ${k}`);assert.equal(content.exactBankStemMatches,0);assert.equal(content.duplicateNewStems,0);bindReports({papers:content.records},ids,bindings,'Content validation');
  const assets=json(root,`${DOCS}/math-assets-checks.json`);passed(assets,'Scientific render assets');sameSet(Object.keys(assets.papers),ids,'Render source papers');sameSet(Object.keys(assets.diagrams),[...diagramMap.keys()],'Raster diagram coverage');assert.equal(assets.diagramCount,summary.diagrams);assert.equal(assets.mathExpressions,expressions.size);for(const id of ids) assert.equal(assets.papers[id],bindings.get(id).canonicalSha256);for(const [id,svg] of diagramMap){assert.equal(assets.diagrams[id].svgSha256,sha256(svg));assert.match(assets.diagrams[id].pngSha256,/^[a-f0-9]{64}$/);}summary.mathExpressions=expressions.size;
  const pdf=json(root,`${DOCS}/pdf-checks.json`),render=json(root,`${DOCS}/pdf-render-checks.json`),visual=json(root,`${DOCS}/physics-pdf-review.json`);for(const [r,c] of [[pdf,'PDF build'],[render,'PDF render'],[visual,'PDF visual review']]) passed(r,c);const pm=unique(pdf.papers,r=>r.id,'PDF records'),rm=unique(render.records,r=>r.id,'Render records'),vm=unique(visual.papers,r=>r.id,'PDF visual records');for(const [m,c] of [[pm,'PDF builds'],[rm,'PDF renders'],[vm,'PDF visual reviews']]) sameSet([...m.keys()],ids,c);
  for(const id of ids){const r=pm.get(id),v=vm.get(id),ren=rm.get(id),file=`public/ib-mock-solutions/${id}.pdf`,raw=read(root,file),hash=sha256(raw),b=bindings.get(id),p=papers.get(id);passed(r,id);passed(v,id);assert.equal(r.sha256,hash);assert.equal(r.bytes,raw.length);assert.equal(v.sha256,hash,`${id}: changed after visual inspection`);assert.equal(ren.sha256,hash);assert.equal(r.pages,visiblePdfPageCount(raw));assert.equal(v.pages,r.pages);assert.equal(ren.pagesRendered,r.pages);assert.equal(v.allPagesInspected,true);noFindings(v.findings,id);noFindings(ren.outOfPageText,id);assert.equal(r.canonicalQuestionSha256,b.canonicalSha256);assert.equal(v.canonicalQuestionSha256,b.canonicalSha256);assert.equal(r.sourceAndDiagramAssetHashesVerified,true);assert.equal(r.brandingTextCheck,true);assert.equal(r.solutionsStartPage,r.questionPages+1);assert.equal(r.pages,r.questionPages+r.solutionPages);assert.ok(r.questionPages>=2&&r.solutionPages>=2);assert.equal(r.bookmarks,2*p.questions.length+2);sameSet(Object.keys(r.questionStartPages),p.questions.map(q=>q.id),`${id} question bookmarks`);sameSet(Object.keys(r.solutionStartPages),p.questions.map(q=>q.id),`${id} solution bookmarks`);assert.ok(Object.values(r.questionStartPages).every(n=>Number.isInteger(n)&&n>=2&&n<=r.questionPages));assert.ok(Object.values(r.solutionStartPages).every(n=>Number.isInteger(n)&&n>r.solutionsStartPage&&n<=r.pages));Object.assign(b,{pdfFile:file,pdfSha256:hash,pdfPages:r.pages,questionPages:r.questionPages,solutionsStartPage:r.solutionsStartPage});summary.pdfPages+=r.pages;summary.questionPages+=r.questionPages;summary.solutionPages+=r.solutionPages;}
  for(const group of ['hl-a','hl-b','hl-c','sl']){const file=`${DOCS}/${group}-pdf-review.json`,r=json(root,file);passed(r,file);if(has(r,'findings')) noFindings(r.findings,file);const gs=unique(r.papers,p=>p.id,file);const expected=ids.filter(id=>group==='sl'?id.startsWith('physics-sl-'):id.startsWith(`physics-hl-set-${group.slice(-1)}-`));sameSet([...gs.keys()],expected,`${file} exact paper coverage`);for(const [id,p] of gs){passed(p,id);assert.equal(p.allPagesInspected,true);noFindings(p.findings,id);const consolidated=vm.get(id);for(const k of ['sha256','pages','canonicalQuestionSha256']) assert.equal(p[k],consolidated[k],`${id}: aggregate visual ledger differs from group inspection`);if(has(p,'inspectedPages')) sameSet(p.inspectedPages,Array.from({length:p.pages},(_,i)=>i+1),`${id} every inspected page`);}}
  for(const [id,record] of pm) assert.equal(record.scientificAssetReportSha256,sha256(read(root,`${DOCS}/math-assets-checks.json`)),`${id}: PDF build is not bound to the exact scientific raster evidence`);
  assert.equal(render.papers,10);assert.equal(render.pages,summary.pdfPages);
  const db=json(root,`${DOCS}/database-checks.json`);passed(db,'Database verification');for(const k of ['schemaApplied','rowLevelSecurityEnabled','columnRestrictedInsertAndUpdate','noAnonymousAccess']) assert.equal(db[k],true,`Database ${k}`);assert.equal(db.ownerPolicies,3);assert.equal(db.remainingQaRows,0);assert.equal(db.advisors.physicsChallengeRelatedFindings,0);assert.ok(db.verification.checks.length>=15);db.verification.checks.forEach(c=>meaningful(c,'Database actual-role check'));assert.equal(sha256(read(root,db.migration.file)),db.migration.sha256);read(root,db.verification.script);
  const portal=json(root,`${DOCS}/portal-checks.json`);assert.equal(portal.status,'passed');assert.equal(portal.sets,5);assert.equal(portal.papers,10);assert.equal(portal.blueprintQuestions,219);assert.equal(portal.blueprintMarks,640);for(const k of ['isolatedApiFixtures','actualReactBrowser','desktopMobileVisualReview','typeScript']) assert.equal(portal[k],'passed',`Portal ${k}`);assert.equal(portal.liveEmailsSent,0);
  return {summary,papers:[...bindings.values()].sort((a,b)=>a.id.localeCompare(b.id))};
}

function filesBelow(root,folder,accept){return readdirSync(join(root,folder),{withFileTypes:true}).flatMap(e=>{const f=`${folder}/${e.name}`;return e.isDirectory()?filesBelow(root,f,accept):e.isFile()&&accept(f)?[f]:[];});}
export function protectedFilePaths(root=ROOT) {
  const scripts=filesBelow(root,'scripts/ib-physics-mocks-2026',f=>/\.(?:py|cjs|mjs|sql)$/.test(f));
  for(const name of ['common.py','author_hl_a.py','author_hl_b.py','author_hlc.py','author_sl.py','independent_hl_b.py','independent_hl_c.py','review_sl_scope.py','build_pdfs.py','render_pdf_math.cjs','render_pdf_review.py','verify_database.sql']) assert.ok(scripts.includes(`scripts/ib-physics-mocks-2026/${name}`),`Missing scientific/release script ${name}`);
  const db=json(root,`${DOCS}/database-checks.json`);
  return sorted([...new Set([`${CONTENT}/catalog.json`,...[...EXPECTED.keys()].map(id=>`${CONTENT}/papers/${id}.json`),...[...EXPECTED.keys()].map(id=>`public/ib-mock-solutions/${id}.pdf`),...filesBelow(root,DOCS,f=>/\.(?:json|md|png)$/.test(f)),...scripts,db.migration.file,'scripts/finalize-ib-physics-mock-reviews.mjs','scripts/verify-ib-physics-mock-reviews.mjs','scripts/verify-ib-physics-mocks.mjs'])]);
}
/** Read-only; the finalizer supplies an in-memory candidate before atomic write. */
export function verifyReviewManifest(root=ROOT,candidate=undefined){const manifest=candidate??json(root,MANIFEST);assert.equal(manifest.schemaVersion,1);passed(manifest,'Manifest');assert.equal(manifest.hashAlgorithm,'sha256');const evidence=readReviewEvidence({root});assert.deepEqual(manifest.summary,evidence.summary);assert.deepEqual(manifest.papers,evidence.papers);sameSet(manifest.files.map(r=>r.file),protectedFilePaths(root),'Protected release files');for(const r of manifest.files){const raw=read(root,r.file);assert.equal(r.bytes,raw.length,`${r.file}: changed size after review`);assert.equal(r.sha256,sha256(raw),`${r.file}: changed after review`);}return evidence;}
if(process.argv[1]&&pathToFileURL(resolve(process.argv[1])).href===import.meta.url){try{assert.equal(process.argv.length,2,'Read-only verification accepts no bypass arguments');const {summary}=verifyReviewManifest();console.log(`IB Physics review guard passed: ${summary.papers} papers, ${summary.questions} questions, ${summary.markingGroups} covered marking groups, ${summary.pdfPages} PDF pages.`);}catch(e){console.error(`IB Physics review guard failed: ${e.message}`);process.exitCode=1;}}
