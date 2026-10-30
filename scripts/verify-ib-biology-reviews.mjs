import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';

// Publication is tied to the reviewed content and media, rather than a stale sign-off.
// JSON formatting line endings differ between Windows authoring and Linux builds.
// Canonical LF preserves the reviewed JSON content across both environments.
const hash=bytes=>createHash('sha256').update(bytes.toString('utf8').replace(/\r\n/g,'\n')).digest('hex');
const manifest=JSON.parse(readFileSync('content/ib/biology-review-manifest.json','utf8'));
const themes=['unity-diversity','form-function','interaction-interdependence','continuity-change'];
assert.equal(manifest.schemaVersion,1);
assert.deepEqual(manifest.themes.map(t=>t.file),themes.map(t=>t+'.json'));
let total=0;
for(const entry of manifest.themes){
 const bytes=readFileSync('content/ib/biology/'+entry.file);
 const questions=JSON.parse(bytes);
 assert.equal(hash(bytes),entry.sha256,entry.file+': content changed since independent review');
 assert.equal(questions.length,entry.questions);
 const reportBytes=readFileSync(entry.review);
 const report=JSON.parse(reportBytes);
 assert.equal(report.status,'passed',entry.review+': incomplete independent review');
 assert.equal(hash(reportBytes),entry.reviewSha256,entry.review+': review changed since release sign-off');
 assert.ok(reportBytes.toString('utf8').includes(entry.sha256),entry.review+': stale question hash');
 total+=questions.length;
}
assert.equal(total,manifest.questions);
const mediaBytes=readFileSync('content/ib/biology-diagram-manifest.json');
assert.equal(hash(mediaBytes),manifest.mediaManifestSha256,'Media changed since visual review');
assert.equal(Object.keys(JSON.parse(mediaBytes).assets).length,manifest.visualAssets);
const supplement=manifest.supplementalReview;
const supplementalBytes=readFileSync(supplement.file);
assert.equal(hash(supplementalBytes),supplement.sha256);
assert.equal(JSON.parse(supplementalBytes).status,'passed');
assert.ok(supplementalBytes.toString('utf8').includes(manifest.themes[3].sha256),'Final Theme D additions require a current independent review');
console.log(`IB Biology reviews passed: ${total} questions and ${manifest.visualAssets} visual assets match their independent review and release hashes.`);
