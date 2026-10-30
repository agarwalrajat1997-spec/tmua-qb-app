import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const hash=data=>createHash('sha256').update(data.toString('utf8').replace(/\r\n/g,'\n')).digest('hex');
const manifest=JSON.parse(readFileSync('content/ib/maths-review-manifest.json','utf8'));
const expected={'math-aa-sl':400,'math-ai-sl':400,'math-aa-hl':1082};
const legacyCounts={'number-algebra':229,functions:129,'geometry-trigonometry':182,'statistics-probability':149,'calculus-1':126,'calculus-2':147};
assert.equal(manifest.schemaVersion,1);assert.equal(manifest.questions,1882);
const mappings=[];
for(const entry of manifest.courses){
 assert.equal(entry.questions,expected[entry.course]);
 const review=JSON.parse(readFileSync(entry.review,'utf8'));
 assert.equal(review.status,'passed');assert.equal(review.questionCount,entry.independentlyReviewedQuestions);
 let count=0;
 for(const file of entry.files){
  const bytes=readFileSync(`content/ib/${entry.course}/${file.file}`),questions=JSON.parse(bytes);
  assert.equal(hash(bytes),file.sha256,`${entry.course}/${file.file}: content changed since review`);
  assert.equal(review.canonicalFiles[file.file],file.sha256,'Review is bound to different content');
  assert.equal(questions.length,file.questions);count+=questions.length;
  if(entry.course==='math-aa-hl')for(const q of questions.filter(q=>q.number<=legacyCounts[file.file.replace('.json','')]))mappings.push({id:q.id,number:q.number,source:q.source});
 }
 assert.equal(count,entry.questions);
}
assert.equal(mappings.length,962);
assert.equal(createHash('sha256').update(JSON.stringify(mappings.sort((a,b)=>a.id.localeCompare(b.id)))).digest('hex'),manifest.legacySourceMappingsSha256,'Existing HL source mappings changed');
for(const evidence of manifest.evidenceFiles)assert.equal(hash(readFileSync(evidence.file)),evidence.sha256,evidence.file+': review evidence changed');
const media=readFileSync('content/ib/maths-diagram-manifest.json');
assert.equal(hash(media),manifest.mediaManifestSha256,'Maths images changed since visual review');
assert.equal(Object.keys(JSON.parse(media).assets).length,manifest.visualAssets);
console.log(`IB Maths reviews passed:1882 questions,920 independently reviewed additions,962 retained source mappings and${manifest.visualAssets} verified figures match their release hashes.`);
