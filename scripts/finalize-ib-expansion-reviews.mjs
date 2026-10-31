import assert from 'node:assert/strict';
import {readFileSync,readdirSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const hash=value=>createHash('sha256').update(value.toString('utf8').replace(/\r\n/g,'\n')).digest('hex');
const specifications=[['math-ai-hl',500,'ai-hl-independent-review.json',500],['economics',360,'economics-independent-review.json',360],['business-management',400,'business-independent-review.json',400],['physics-hl',740,'physics-sl-independent-review.json',100]];
const courses=[];
for(const [subject,total,reviewName,reviewCount] of specifications){
 const reviewPath='docs/ib-expansion-reviews/'+reviewName,review=JSON.parse(readFileSync(reviewPath,'utf8'));
 assert.equal(review.status,'passed',reviewPath);assert.equal(review.questionCount,reviewCount,reviewPath);
 assert.equal(review.records.length,reviewCount);for(const record of review.records)assert.equal(record.status,'passed',record.id);assert.equal(new Set(review.records.map(r=>r.id)).size,reviewCount);
 const files=[];let count=0;
 for(const file of readdirSync(`content/ib/${subject}`).filter(f=>f.endsWith('.json')).sort()){
  const path=`content/ib/${subject}/${file}`,data=readFileSync(path),questions=JSON.parse(data),sha256=hash(data);
  assert.equal(review.canonicalFiles[file],sha256,`${path}: changed after independent review`);
  files.push({file,questions:questions.length,sha256});count+=questions.length;
 }
 assert.equal(count,total,subject);
 courses.push({subject,questions:total,independentlyReviewedQuestions:reviewCount,review:reviewPath,files});
}
const evidencePaths=new Set(readdirSync('docs/ib-expansion-reviews').filter(f=>/\.(json|md)$/.test(f)).map(file=>'docs/ib-expansion-reviews/'+file));
// Include the transitive review records, including figure-render ledgers.
for(const file of evidencePaths){
 if(!file.endsWith('.json'))continue;
 const document=JSON.parse(readFileSync(file,'utf8'));
 for(const [reference,wanted] of Object.entries(document.evidenceHashes??{})){
  assert.ok(!reference.includes('..')&&!reference.startsWith('/')&&!reference.includes('\\'),'Unsafe evidence reference');
  const path='docs/ib-expansion-reviews/'+reference;
  assert.equal(hash(readFileSync(path)),wanted,path+': evidence reference does not match');evidencePaths.add(path);
 }
}
const evidenceFiles=[...evidencePaths].sort().map(file=>({file,sha256:hash(readFileSync(file))}));
const media=readFileSync('content/ib/expansion-diagram-manifest.json'),assets=JSON.parse(media).assets;
assert.ok(Object.keys(assets).length>0,'Cloudflare diagrams have not been verified');
const manifest={schemaVersion:1,date:'2026-10-31',baselineCommit:'f15087a7b38d15b9ba0d41dc725bc393ca32e682',newQuestions:1360,questionsInChangedBanks:2000,legacyPhysicsScopeReviews:420,courses,evidenceFiles,mediaManifestSha256:hash(media),visualAssets:Object.keys(assets).length,limitations:'Independent agent reviews and deterministic mathematical/content checks; not an IB-endorsed bank or a human examiner certification. Legacy Physics review covers SL scope; new Physics solutions independently recomputed. Existing prior Maths review remains separately bound.'};
writeFileSync('content/ib/expansion-review-manifest.json',JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify({status:'frozen',newQuestions:1360,changedBankQuestions:2000,evidenceFiles:evidenceFiles.length,visualAssets:manifest.visualAssets}));
