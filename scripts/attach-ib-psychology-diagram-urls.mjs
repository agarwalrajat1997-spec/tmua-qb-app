import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {ORIGIN,PREFIX,MANIFEST,readQuestions,sha} from './psychology-media.mjs';
const manifest=JSON.parse(readFileSync(MANIFEST,'utf8'));assert.equal(manifest.origin,ORIGIN);
const files=new Map();let attached=0;
for(const {q,file} of readQuestions({partial:process.argv.includes('--partial')})){
  for(const [svgField,urlField] of [['diagramSvg','diagramUrl'],['markSchemeDiagramSvg','markSchemeDiagramUrl']]){
    const svg=q[svgField];if(!svg)continue;
    const hash=sha(svg),entry=manifest.assets[hash];assert.ok(entry,`${q.id}: SVG is not publicly verified`);
    assert.equal(entry.key,PREFIX+hash+'.svg');assert.equal(entry.bytes,Buffer.byteLength(svg));
    assert.equal(entry.contentType,'image/svg+xml');
    const url=ORIGIN+'/'+entry.key;assert.ok(!q[urlField]||q[urlField]===url,`${q.id}: existing URL disagrees with its SVG`);
    if(q[urlField]!==url){q[urlField]=url;attached++;}
  }
  if(!files.has(file))files.set(file,[]);files.get(file).push(q);
}
if(attached&&!process.argv.includes('--check'))for(const [file,questions]of files)writeFileSync(file,JSON.stringify(questions,null,2)+'\n');
if(process.argv.includes('--check'))assert.equal(attached,0,'Verified diagram URLs still need attachment');
console.log(JSON.stringify({status:process.argv.includes('--check')?'checked':'attached',addedUrls:attached,files:files.size,next:attached?'Authors must rerun their substantive checks and evidence before independent review':'No canonical changes'}));
