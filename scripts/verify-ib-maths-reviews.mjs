import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
export const ROOT=resolve(dirname(fileURLToPath(import.meta.url)),'..');
export const hash=data=>createHash('sha256').update(data.toString('utf8').replace(/\r\n/g,'\n')).digest('hex');
export const questionHash=q=>createHash('sha256').update(JSON.stringify(q)).digest('hex');
const sha=value=>assert.match(value,/^[a-f0-9]{64}$/,'A pinned SHA256 is required');
const substantive=(value,label,min=40)=>assert.ok(typeof value==='string'&&value.trim().length>=min,`${label}: substantive evidence required`);

/** Reverse only listed marking-text leaves, then recover the frozen canonical file. */
export function validateReviewedCorrection({course,file,baselineSha256,currentBytes,reviewBytes,evidenceSha256}){
 sha(evidenceSha256);assert.equal(hash(reviewBytes),evidenceSha256,'Correction review is not pinned to its evidence bytes');
 const report=JSON.parse(reviewBytes),questions=JSON.parse(currentBytes);
 assert.equal(report.status,'passed');assert.equal(report.author,'root');assert.equal(report.reviewer,'mock_pdf_inventory');assert.notEqual(report.author,report.reviewer);
 assert.equal(report.course,course);assert.equal(report.file,file);
 if(report.contentPath!==undefined)assert.equal(report.contentPath,`content/ib/${course}/${file}`);
 for(const key of ['baselineSha256','currentSha256','originalQuestionSha256','updatedQuestionSha256'])sha(report[key]);
 assert.equal(report.baselineSha256,baselineSha256,'Correction must retain the original frozen file hash');
 assert.equal(report.currentSha256,hash(currentBytes),'Correction is bound to different current bytes');
 assert.notEqual(report.currentSha256,report.baselineSha256,'A correction must change reviewed text');
 assert.ok(Array.isArray(questions));assert.equal(typeof report.questionId,'string');
 const matches=questions.filter(q=>q.id===report.questionId);assert.equal(matches.length,1,'Correction needs exactly one existing question');
 assert.equal(questionHash(matches[0]),report.updatedQuestionSha256,'Updated question hash differs');
 assert.ok(Array.isArray(report.changes)&&report.changes.length>0&&report.changes.length<=20,'Explicit bounded text changes required');
 const restored=JSON.parse(JSON.stringify(questions)),original=restored.find(q=>q.id===report.questionId),leaves=new Set();
 for(const change of report.changes){
  assert.deepEqual(Object.keys(change).sort(),['after','before','group','step'],'Only marking-step text replacements are permitted');
  assert.ok(Number.isSafeInteger(change.group)&&change.group>=0&&Number.isSafeInteger(change.step)&&change.step>=0,'Invalid correction coordinates');
  const key=`${change.group}:${change.step}`;assert.ok(!leaves.has(key),'Duplicate correction text leaf');leaves.add(key);
  assert.equal(typeof change.before,'string');assert.equal(typeof change.after,'string');assert.notEqual(change.before,change.after,'No-op correction');
  const target=original.markScheme?.[change.group]?.steps?.[change.step];assert.ok(target,'Correction step does not exist');
  assert.equal(target.text,change.after,'Listed replacement does not match the current text');target.text=change.before;
 }
 assert.equal(questionHash(original),report.originalQuestionSha256,'Original question is not restored by only the listed text changes');
 assert.equal(hash(JSON.stringify(restored,null,2)+'\n'),baselineSha256,'Unreviewed changes remain outside the listed correction');
 substantive(report.reasoning,'Correction reasoning',80);assert.deepEqual(report.openFindings,[],'Correction has unresolved findings');
 assert.ok(Array.isArray(report.numericChecks)&&report.numericChecks.length,'Independent numeric evidence required');
 const names=new Set();
 for(const check of report.numericChecks){
  substantive(check.name,'Numeric check name',4);substantive(check.reason,'Numeric check reason',12);assert.ok(!names.has(check.name),'Duplicate numeric check');names.add(check.name);
  for(const key of ['actual','expected','tolerance'])assert.ok(typeof check[key]==='number'&&Number.isFinite(check[key]),`Finite numeric ${key} required`);
  assert.ok(check.tolerance>=0&&check.tolerance<=Math.max(1e-10,Math.abs(check.expected)*1e-8),'Numeric tolerance could conceal a correction error');
  assert.ok(Math.abs(check.actual-check.expected)<=check.tolerance,'Correction numeric evidence is contradictory');
  if(Object.hasOwn(check,'passed'))assert.equal(check.passed,true);if(Object.hasOwn(check,'status'))assert.equal(check.status,'passed');
 }
 return questions;
}

export function verifyMathsReviews(root=ROOT){
const read=file=>readFileSync(join(root,file));
const manifest=JSON.parse(read('content/ib/maths-review-manifest.json'));
const expected={'math-aa-sl':400,'math-ai-sl':400,'math-aa-hl':1082};
const legacyCounts={'number-algebra':229,functions:129,'geometry-trigonometry':182,'statistics-probability':149,'calculus-1':126,'calculus-2':147};
assert.equal(manifest.schemaVersion,1);assert.equal(manifest.questions,1882);
const evidence=new Map();
for(const entry of manifest.evidenceFiles){assert.ok(!evidence.has(entry.file),'Duplicate review evidence path');const bytes=read(entry.file);assert.equal(hash(bytes),entry.sha256,entry.file+': review evidence changed');evidence.set(entry.file,{bytes,sha256:entry.sha256});}
const corrections=manifest.corrections??[];assert.ok(Array.isArray(corrections));
const byFile=new Map(),reports=new Set();
for(const entry of corrections){
 assert.deepEqual(Object.keys(entry).sort(),['course','file','review'],'Correction entry has unexpected fields');
 assert.ok(Object.hasOwn(expected,entry.course));assert.match(entry.file,/^[a-z0-9-]+\.json$/);
 assert.match(entry.review,/^docs\/ib-maths-reviews\/[a-z0-9-]+\.json$/,'Correction review path must stay within reviewed Maths evidence');
 const key=`${entry.course}/${entry.file}`;assert.ok(!byFile.has(key)&&!reports.has(entry.review),'Duplicate correction target or review');
 assert.ok(evidence.has(entry.review),'Correction review must be pinned in evidenceFiles');byFile.set(key,entry);reports.add(entry.review);
}
const mappings=[],used=new Set();
for(const entry of manifest.courses){
 assert.equal(entry.questions,expected[entry.course]);
 const review=JSON.parse(read(entry.review));
 assert.equal(review.status,'passed');assert.equal(review.questionCount,entry.independentlyReviewedQuestions);
 let count=0;
 for(const file of entry.files){
  const key=`${entry.course}/${file.file}`,bytes=read(`content/ib/${key}`),correction=byFile.get(key);
  let questions;
  if(correction){const pinned=evidence.get(correction.review);questions=validateReviewedCorrection({course:entry.course,file:file.file,baselineSha256:file.sha256,currentBytes:bytes,reviewBytes:pinned.bytes,evidenceSha256:pinned.sha256});used.add(key);}
  else {assert.equal(hash(bytes),file.sha256,`${key}: content changed since review`);questions=JSON.parse(bytes);}
  assert.equal(review.canonicalFiles[file.file],file.sha256,'Review is bound to different content');
  assert.equal(questions.length,file.questions);count+=questions.length;
  if(entry.course==='math-aa-hl')for(const q of questions.filter(q=>q.number<=legacyCounts[file.file.replace('.json','')]))mappings.push({id:q.id,number:q.number,source:q.source});
 }
 assert.equal(count,entry.questions);
}
assert.equal(mappings.length,962);
assert.equal(used.size,corrections.length,'A correction does not target an existing reviewed file');
assert.equal(createHash('sha256').update(JSON.stringify(mappings.sort((a,b)=>a.id.localeCompare(b.id)))).digest('hex'),manifest.legacySourceMappingsSha256,'Existing HL source mappings changed');
const media=read('content/ib/maths-diagram-manifest.json');
assert.equal(hash(media),manifest.mediaManifestSha256,'Maths images changed since visual review');
assert.equal(Object.keys(JSON.parse(media).assets).length,manifest.visualAssets);
return {questions:1882,corrections:corrections.length,visualAssets:manifest.visualAssets};
}
if(process.argv[1]&&pathToFileURL(resolve(process.argv[1])).href===import.meta.url){try{assert.equal(process.argv.length,2,'Review verification accepts no bypass arguments');const r=verifyMathsReviews();console.log(`IB Maths reviews passed:1882 questions,920 independently reviewed additions,962 retained source mappings,${r.visualAssets} verified figures and${r.corrections} narrowly reviewed correction(s); original review hashes retained.`);}catch(error){console.error(`IB Maths reviews failed:${error.message}`);process.exitCode=1;}}
