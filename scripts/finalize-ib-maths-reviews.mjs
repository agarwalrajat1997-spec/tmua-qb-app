import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,readdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';

const hash=data=>createHash('sha256').update(data.toString('utf8').replace(/\r\n/g,'\n')).digest('hex');
const rawHash=data=>createHash('sha256').update(data).digest('hex');
const definitions=[['math-aa-sl','aa-sl-independent-review.json',400],['math-ai-sl','ai-sl-independent-review.json',400],['math-aa-hl','aa-hl-additions-independent-review.json',120]];
const courses=[];
const baseline='83cb12758b3ceb67ffb7ac814082a86d7e110f82';
const originalCounts={'number-algebra':229,functions:129,'geometry-trigonometry':182,'statistics-probability':149,'calculus-1':126,'calculus-2':147};
const legacyMappings=[];
for(const [course,name,reviewedQuestions] of definitions){
 const reviewPath='docs/ib-maths-reviews/'+name;
 const report=JSON.parse(readFileSync(reviewPath,'utf8'));
 assert.equal(report.status,'passed');assert.equal(report.questionCount,reviewedQuestions);
 const reviewedFiles=report.files??report.hashes;
 const canonicalFiles={};
 const files=readdirSync('content/ib/'+course).filter(file=>file.endsWith('.json')).sort().map(file=>{
  const path=`content/ib/${course}/${file}`,bytes=readFileSync(path),sha256=hash(bytes),questions=JSON.parse(bytes);
  assert.ok(reviewedFiles[file]===rawHash(bytes)||reviewedFiles[file]===sha256||report.canonicalFiles?.[file]===sha256,`${course}/${file}: not the independently reviewed content`);
  canonicalFiles[file]=sha256;
  if(course==='math-aa-hl'){
   const prior=JSON.parse(execFileSync('git',['show',`${baseline}:${path}`],{encoding:'utf8',maxBuffer:10*1024*1024}));
   assert.equal(prior.length,originalCounts[file.replace('.json','')]);
   for(const q of prior){
    const current=questions.find(item=>item.id===q.id);
    assert.ok(current);assert.deepEqual({id:current.id,number:current.number,source:current.source},{id:q.id,number:q.number,source:q.source});
    legacyMappings.push({id:q.id,number:q.number,source:q.source});
   }
  }
  return {file,questions:questions.length,sha256};
 });
 report.canonicalFiles=canonicalFiles;report.hashNormalization='SHA256 of UTF-8 JSON with LF line endings; original reviewer hashes retained.';
 writeFileSync(reviewPath,JSON.stringify(report,null,2)+'\n');
 courses.push({course,questions:files.reduce((sum,f)=>sum+f.questions,0),independentlyReviewedQuestions:reviewedQuestions,review:reviewPath,files});
}
const mediaPath='content/ib/maths-diagram-manifest.json',mediaBytes=readFileSync(mediaPath),media=JSON.parse(mediaBytes);
assert.equal(media.origin,'https://media.thrivingscholars.com');assert.ok(Object.keys(media.assets).length>300);
const evidenceFiles=readdirSync('docs/ib-maths-reviews').filter(file=>file.endsWith('.json')).sort().map(file=>({file:'docs/ib-maths-reviews/'+file,sha256:hash(readFileSync('docs/ib-maths-reviews/'+file))}));
const manifest={schemaVersion:1,reviewedOn:'2026-10-31',hashNormalization:'UTF-8 JSON with LF line endings',questions:courses.reduce((sum,c)=>sum+c.questions,0),courses,
 retainedLegacyQuestions:962,legacyBaselineCommit:baseline,legacySourceMappingsSha256:rawHash(JSON.stringify(legacyMappings.sort((a,b)=>a.id.localeCompare(b.id)))),
 evidenceFiles,visualAssets:Object.keys(media.assets).length,mediaManifestSha256:hash(mediaBytes),
 syllabus:'Current Mathematics AA/AI courses first assessed in2021, with final assessment November2028; excludes the first-assessment2029 revision.',
 sources:[
  {url:'https://www.ibo.org/globalassets/new-structure/university-admission/pdfs/dp-mathematics-analysis-and-approaches-guide-en.pdf',purpose:'AA syllabus, SL/AHL boundaries, command terms and assessment conventions'},
  {url:'https://ibo.org/globalassets/new-structure/university-admission/pdfs/dp-mathematics-applications-and-interpretation-guide-en.pdf',purpose:'AI SL scope, calculator requirements and contextual assessment'},
  {url:'https://www.ibo.org/programmes/diploma-programme/assessment-and-exams/sample-exam-papers/',purpose:'Official specimen question and marking-style calibration; no paper text or images reproduced'},
  {url:'https://village.pirateib.su/#app/ib-math',purpose:'Supplied reference course/topic navigation; AA SL functions and AI SL statistics samples inspected for style and difficulty. Some individual reference destinations returned the landing page.'}
 ],
 originality:'920 additions independently authored across260 question families, with varied values and contexts. Mathematical diagrams are precise Python-authored SVGs. Existing AA HL reference mappings remain stable; two repeated exercises now have distinct values and recalculated solutions.',
 reviewLimit:'Agent authoring and separate agent mathematical reviews. All800 new SL records and120 HL additions independently reviewed, plus two revised legacy variants. Existing962 HL records received retained author-check replays,24 fresh high-risk reviews and11 targeted corrections; this is not a new independent proof of every legacy solution, human examiner approval or IB endorsement.',
 visualReview:'All72 AA SL and136 AI SL figures were rendered and independently inspected. Existing and added HL figures were rendered, with corrected labels/geometry and targeted final inspection. Cloudflare public response bytes verified against authored hashes.'};
assert.equal(manifest.questions,1882);assert.equal(legacyMappings.length,962);
writeFileSync('content/ib/maths-review-manifest.json',JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify({status:'review-bound',questions:manifest.questions,visualAssets:manifest.visualAssets,retainedLegacyQuestions:962}));
