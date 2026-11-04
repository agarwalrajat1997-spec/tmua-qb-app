import assert from 'node:assert/strict';
import {mkdirSync,mkdtempSync,writeFileSync} from 'node:fs';
import {resolve,join} from 'node:path';
import {sha,questionHash,ORIGIN,BUCKET,PREFIX,validateObject,readStage} from './psychology-media.mjs';
assert.equal(sha('abc'),'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad');
assert.equal(questionHash({z:1,a:[2,{b:'β'}]}),questionHash({a:[2,{b:'β'}],z:1}),'canonical question hashing is independent of key insertion order');
assert.notEqual(questionHash({a:[1,2]}),questionHash({a:[2,1]}),'question/step order remains significant');
const hash='a'.repeat(64),item={sha256:hash,key:PREFIX+hash+'.svg',bytes:100,uses:[{questionId:'ib-psy-bio-001',questionSha256:'b'.repeat(64),role:'question'}]};
validateObject(item);let rejected=0;
function rejectItem(change){const copy=structuredClone(item);change(copy);assert.throws(()=>validateObject(copy));rejected++;}
rejectItem(i=>i.sha256='../outside');
rejectItem(i=>i.key='ib/physics-hl/2026-10-30/'+hash+'.svg');
rejectItem(i=>i.key=PREFIX+'../'+hash+'.svg');
rejectItem(i=>i.bytes=-1);
rejectItem(i=>i.bytes=1.5);
rejectItem(i=>i.uses=[]);
rejectItem(i=>i.uses[0].questionId='../outside');
rejectItem(i=>i.uses[0].role='../../outside');
rejectItem(i=>i.uses[0].questionSha256='old-unbound-source');
const parent=resolve('../psychology-bank-2026/media-fixtures');mkdirSync(parent,{recursive:true});
const dir=mkdtempSync(join(parent,'isolated-'));
const stage={schemaVersion:1,origin:ORIGIN,bucket:BUCKET,questions:1,objects:[item]};
function save(value){writeFileSync(join(dir,'staged-manifest.json'),JSON.stringify(value));}
save(stage);assert.equal(readStage(dir).objects.length,1);
for(const alter of [s=>s.origin='https://external.invalid',s=>s.bucket='other-bucket',s=>s.questions=241,s=>s.objects.push(s.objects[0])]){const changed=structuredClone(stage);alter(changed);save(changed);assert.throws(()=>readStage(dir));rejected++;}
save(stage);
console.log(JSON.stringify({status:'passed',rejectedUnsafeCases:rejected,checks:'Owned origin/bucket/prefix only; immutable content keys; bounded byte counts and question count; safe native filenames/roles; unique staged assets; stable canonical hashing. No uploads or live network requests.'}));
