import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {readQuestions,sha,ORIGIN,PREFIX,MANIFEST} from './psychology-media.mjs';
const record=process.argv.includes('--record');
assert.ok(process.argv.slice(2).every(a=>a==='--record'),'Unknown CDN verifier argument');
assert.ok(!record||!existsSync('content/ib/psychology-review-manifest.json'),'A frozen release cannot rewrite its CDN evidence');
const source=new Map(readQuestions().flatMap(({q})=>q.diagramSvg?[[sha(q.diagramSvg),q.diagramSvg]]:[]));
const manifest=JSON.parse(readFileSync(MANIFEST,'utf8'));assert.equal(manifest.origin,ORIGIN);
assert.deepEqual(Object.keys(manifest.assets).sort(),[...source.keys()].sort());
const records=[],entries=Object.entries(manifest.assets);
for(let start=0;start<entries.length;start+=4){
  const batch=await Promise.all(entries.slice(start,start+4).map(async([hash,asset])=>{
    assert.equal(asset.key,PREFIX+hash+'.svg');assert.equal(asset.bytes,Buffer.byteLength(source.get(hash)));assert.equal(asset.contentType,'image/svg+xml');
    const url=ORIGIN+'/'+asset.key,response=await fetch(url,{signal:AbortSignal.timeout(25000)});
    assert.equal(response.status,200);assert.match(response.headers.get('content-type')??'',/^image\/svg\+xml\b/);
    const bytes=Buffer.from(await response.arrayBuffer());assert.equal(sha(bytes),hash);assert.equal(bytes.length,asset.bytes);
    return {sha256:hash,url,status:200,contentType:'image/svg+xml',bytes:bytes.length,publicSha256:sha(bytes)};
  }));records.push(...batch);
}
const report={status:'passed',origin:ORIGIN,objects:records.length,records:records.sort((a,b)=>a.sha256.localeCompare(b.sha256)),method:'Actual HTTPS200, SVG content type and complete public response bytes matched each original content-hashed SVG.'};
if(record)writeFileSync('docs/ib-psychology-reviews/cdn-checks.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({status:'passed',objects:records.length,recorded:record}));
