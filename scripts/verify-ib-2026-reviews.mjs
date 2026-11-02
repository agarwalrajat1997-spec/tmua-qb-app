import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const hash=bytes=>createHash('sha256').update(bytes.toString('utf8').replace(/\r\n/g,'\n')).digest('hex');
const m=JSON.parse(readFileSync('content/ib/math-2026-review-manifest.json','utf8'));
assert.equal(m.schemaVersion,1);assert.equal(m.status,'passed');assert.equal(m.questions,400);assert.equal(m.courses.length,4);
for(const f of m.files)assert.equal(hash(readFileSync(f.file)),f.sha256,f.file+': changed since release review');
for(const c of m.courses){
 const q=JSON.parse(readFileSync(c.questionFile,'utf8')),r=JSON.parse(readFileSync(c.reviewFile,'utf8'));
 assert.equal(q.length,100);assert.equal(r.questions,100);assert.equal(r.status,'passed');
 assert.equal(hash(readFileSync(c.questionFile)),c.sha256);assert.equal(r.sha256,c.sha256);
 assert.deepEqual(r.records.map(x=>x.id).sort(),q.map(x=>x.id).sort());
 assert.ok(r.records.every(x=>x.status==='passed'));
}
console.log('400 Maths additions match four independent content reviews and frozen release hashes.');
