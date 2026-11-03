import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const hash=bytes=>createHash('sha256').update(bytes.toString('utf8').replace(/\r\n/g,'\n')).digest('hex');
const m=JSON.parse(readFileSync('content/ib/chemistry-2026-review-manifest.json','utf8'));
assert.equal(m.schemaVersion,1);assert.equal(m.status,'passed');assert.equal(m.questions,200);assert.equal(m.batches.length,4);
for(const f of m.files)assert.equal(hash(readFileSync(f.file)),f.sha256,f.file+' changed since release review');
for(const b of m.batches){const q=JSON.parse(readFileSync(b.questionFile)),r=JSON.parse(readFileSync(b.reviewFile));assert.equal(q.length,b.questions);assert.equal(r.questions,b.questions);assert.equal(r.status,'passed');assert.equal(hash(readFileSync(b.questionFile)),b.sha256);assert.equal(r.sha256,b.sha256);assert.deepEqual(r.records.map(x=>x.id).sort(),q.map(x=>x.id).sort());assert.ok(r.records.every(x=>x.status==='passed'));}
console.log('200 Chemistry additions match four separate reviews and frozen release hashes.');
