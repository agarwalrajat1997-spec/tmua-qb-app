import {mkdirSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {ORIGIN,BUCKET,PREFIX,sha,questionHash,readQuestions} from './psychology-media.mjs';
const directory=resolve(process.argv.slice(2).find(a=>!a.startsWith('--'))||'../psychology-bank-2026/media');
mkdirSync(resolve(directory,'assets'),{recursive:true});
const objects=new Map(),questions=readQuestions({partial:process.argv.includes('--partial')});
for(const {q,file} of questions)for(const [field,role] of [['diagramSvg','question'],['markSchemeDiagramSvg','scheme']]){
  const svg=q[field];if(!svg)continue;
  const hash=sha(svg);
  if(!objects.has(hash))objects.set(hash,{sha256:hash,key:PREFIX+hash+'.svg',bytes:Buffer.byteLength(svg),uses:[]});
  objects.get(hash).uses.push({questionId:q.id,role,title:q.title,file,questionSha256:questionHash(q)});
  writeFileSync(resolve(directory,'assets',hash+'.svg'),svg);
}
const manifest={schemaVersion:1,origin:ORIGIN,bucket:BUCKET,questions:questions.length,objects:[...objects.values()].sort((a,b)=>a.sha256.localeCompare(b.sha256))};
writeFileSync(resolve(directory,'staged-manifest.json'),JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify({status:'staged',questions:questions.length,uniqueAssets:objects.size,diagramReferences:manifest.objects.reduce((n,o)=>n+o.uses.length,0),directory}));
