import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const hash=value=>createHash('sha256').update(value.toString('utf8').replace(/\r\n/g,'\n')).digest('hex');
const manifest=JSON.parse(readFileSync('content/ib/expansion-review-manifest.json','utf8'));
assert.equal(manifest.schemaVersion,1);assert.equal(manifest.newQuestions,1360);assert.equal(manifest.questionsInChangedBanks,2000);assert.equal(manifest.legacyPhysicsScopeReviews,420);
let bankTotal=0,reviewTotal=0;
for(const entry of manifest.courses){
 const review=JSON.parse(readFileSync(entry.review,'utf8'));assert.equal(review.status,'passed');assert.equal(review.questionCount,entry.independentlyReviewedQuestions);assert.equal(review.records.length,review.questionCount);
 for(const record of review.records)assert.equal(record.status,'passed',record.id);
 const reviewedIds=new Set(review.records.map(r=>r.id));assert.equal(reviewedIds.size,review.questionCount);
 let count=0;
 for(const file of entry.files){
  const path=`content/ib/${entry.subject}/${file.file}`,bytes=readFileSync(path),questions=JSON.parse(bytes);
  assert.equal(hash(bytes),file.sha256,path+': changed after review');assert.equal(review.canonicalFiles[file.file],file.sha256,'Review bound to different content');assert.equal(questions.length,file.questions);
  const base=entry.subject==='physics-hl'?({'space-time-motion.json':200,'particulate-matter.json':120,'wave-behaviour.json':120,'fields.json':100,'nuclear-quantum.json':100}[file.file]):0;
  for(const q of questions.filter(q=>q.number>base))assert.ok(reviewedIds.has(q.id),q.id+': missing independent review');
  count+=questions.length;
 }
 assert.equal(count,entry.questions);bankTotal+=count;reviewTotal+=review.questionCount;
 if(entry.subject==='physics-hl')assert.equal(review.scopeQuestionCount,420);
 for(const [file,wanted] of Object.entries(review.evidenceHashes??{}))assert.equal(hash(readFileSync('docs/ib-expansion-reviews/'+file)),wanted,file+': evidence reference changed');
}
assert.equal(bankTotal,2000);assert.equal(reviewTotal,1360);
for(const evidence of manifest.evidenceFiles)assert.equal(hash(readFileSync(evidence.file)),evidence.sha256,evidence.file+': review evidence changed');
const media=readFileSync('content/ib/expansion-diagram-manifest.json');assert.equal(hash(media),manifest.mediaManifestSha256);assert.equal(Object.keys(JSON.parse(media).assets).length,manifest.visualAssets);
console.log(`IB expansion review passed: 1360 independently reviewed new questions, 420 legacy Physics SL scope reviews, ${manifest.visualAssets} Cloudflare figures; all release content and evidence match reviewed hashes.`);
