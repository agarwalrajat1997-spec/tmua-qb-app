import {readFileSync,writeFileSync,readdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const courses=['aa-sl','aa-hl','ai-sl','ai-hl'];
const bindings=[],prepared=[];
for(const course of courses){
 const file='content/ib/math-2026-expansion/'+course+'.json';
 const reviewFile='docs/ib-2026-maths/'+course+'-independent-review.json';
 const raw=readFileSync(file),q=JSON.parse(raw),review=JSON.parse(readFileSync(reviewFile,'utf8'));
 assert.equal(review.status,'passed');assert.equal(review.questions,100);
 assert.equal(review.sha256,hash(raw),course+': content changed since independent review');
 assert.equal(review.records.length,100);
 for(const record of review.records)if(!record.status&&record.verdict==='passed')record.status='passed';
 assert.deepEqual(review.records.map(x=>x.id).sort(),q.map(x=>x.id).sort());
 assert.ok(review.records.every(x=>x.status==='passed'));
 prepared.push({course,file,reviewFile,raw,review});
}
for(const {course,file,reviewFile,raw,review} of prepared){
 const lf=raw.toString('utf8').replace(/\r\n/g,'\n');
 writeFileSync(file,lf);
 review.reviewedRawSha256??=review.sha256;
 review.sha256=hash(Buffer.from(lf));
 review.lineEndingNormalization='LF only; parsed content and per-question review unchanged';
 writeFileSync(reviewFile,JSON.stringify(review,null,2)+'\n');
 bindings.push({course,questions:100,questionFile:file,reviewFile,sha256:review.sha256});
}
const paths=[
 ...bindings.flatMap(x=>[x.questionFile,x.reviewFile]),
 ...readdirSync('scripts/ib-2026-authoring').filter(x=>x.endsWith('.py')||x.endsWith('.txt')).map(x=>'scripts/ib-2026-authoring/'+x),
 ...courses.map(x=>'docs/ib-2026-maths/'+x+'-author-review.json'),
];
// Text is pinned to LF to match Git and avoid platform-dependent release hashes.
for(const p of paths)writeFileSync(p,readFileSync(p,'utf8').replace(/\r\n/g,'\n').replace(/\n+$/,'\n'));
const files=paths.map(file=>({file,sha256:hash(readFileSync(file))}));
writeFileSync('content/ib/math-2026-review-manifest.json',JSON.stringify({schemaVersion:1,status:'passed',date:'2026-11-03',questions:400,courses:bindings,files,provenance:'Independent syllabus-authored practice; not official IB past-paper questions. AI authoring and separate AI review, not human examiner moderation.'},null,2)+'\n');
console.log('Bound 400 reviewed questions, four independent reviews and authoring evidence to final release bytes.');
