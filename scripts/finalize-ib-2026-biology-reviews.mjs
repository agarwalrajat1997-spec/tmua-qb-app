import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,readdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const batches={'unity-diversity':50,'form-function':50,'interaction-interdependence':50,'continuity-change':50};
const reviewed=[];
// Verify all reviews BEFORE normalizing or updating any file.
for(const [name,n]of Object.entries(batches)){
 const questionFile=`content/ib/biology-2026-expansion/${name}.json`,reviewFile=`docs/ib-2026-biology/${name}-independent-review.json`;
 const raw=readFileSync(questionFile),qs=JSON.parse(raw),r=JSON.parse(readFileSync(reviewFile,'utf8'));
 assert.equal(qs.length,n);assert.equal(r.questions,n);assert.equal(r.status,'passed');assert.equal(r.sha256,hash(raw),name+' independent review does not match final bytes');
 assert.deepEqual(r.records.map(x=>x.id).sort(),qs.map(q=>q.id).sort());assert.ok(r.records.every(x=>x.status==='passed'));
 reviewed.push({name,questions:n,questionFile,reviewFile,raw,r});
}
for(const b of reviewed){
 const normalized=b.raw.toString('utf8').replace(/\r\n/g,'\n');writeFileSync(b.questionFile,normalized);
 b.r.reviewedRawSha256??=b.r.sha256;b.r.sha256=hash(Buffer.from(normalized));b.r.normalization='UTF-8 LF; content reviewed before line-ending normalization.';
 writeFileSync(b.reviewFile,JSON.stringify(b.r,null,2)+'\n');
}
const owned=[];
for(const dir of ['scripts/ib-2026-biology','docs/ib-2026-biology'])for(const file of readdirSync(dir).filter(f=>/\.(?:py|json|txt)$/.test(f))){const path=dir+'/'+file;writeFileSync(path,readFileSync(path,'utf8').replace(/\r\n/g,'\n'));owned.push(path);}
for(const b of reviewed)owned.push(b.questionFile);
const manifest={schemaVersion:1,status:'passed',date:'2026-11-03',questions:200,batches:reviewed.map(b=>({name:b.name,questions:b.questions,questionFile:b.questionFile,reviewFile:b.reviewFile,sha256:b.r.sha256})),files:[...new Set(owned)].sort().map(file=>({file,sha256:hash(readFileSync(file))})),provenance:'Independent syllabus-authored practice using official IB guide/specimen for scope and style. Separate AI authoring and review, with computational/biological and visual checks; not official past-paper material and not human examiner moderation.'};
writeFileSync('content/ib/biology-2026-review-manifest.json',JSON.stringify(manifest,null,2)+'\n');
console.log('Finalized 200 Biology questions against four independent reviews.');
