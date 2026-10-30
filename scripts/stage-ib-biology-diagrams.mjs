import {readFileSync,readdirSync,mkdirSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
import {safeDiagram} from '../lib/ib/question.ts';
const directory=resolve('content/ib/biology');
const output=resolve(process.argv[2]||'../biology-artifacts');
const themes=process.argv[3]||'a,b,c,d';
mkdirSync(resolve(output,'assets'),{recursive:true});
const objects=new Map();
for(const file of readdirSync(directory).filter(n=>n.endsWith('.json'))){
 const bank=JSON.parse(readFileSync(resolve(directory,file),'utf8'));
 if(!Array.isArray(bank))continue;
 for(const q of bank)for(const [field,role] of [['diagramSvg','question'],['markSchemeDiagramSvg','scheme']]){
  if(!themes.split(',').includes(q.id.split('-')[2]))continue;
  const source=q[field];if(!source)continue;if(!safeDiagram(source))throw new Error(q.id+': unsafe '+field);
  const sha256=createHash('sha256').update(source).digest('hex');
  if(!objects.has(sha256))objects.set(sha256,{sha256,key:`ib/biology/2026-10-30/${sha256}.svg`,bytes:Buffer.byteLength(source),extension:"svg",contentType:"image/svg+xml",uses:[]});
  objects.get(sha256).uses.push({id:q.id,role,title:q.title});
  writeFileSync(resolve(output,'assets',sha256+'.svg'),source);
 }
}
const raster=JSON.parse(readFileSync(resolve('content/ib/biology-image-sources.json'),'utf8'));
for(const asset of raster.assets){
 const source=readFileSync(resolve('public'+asset.publicPath));
 const sha256=createHash('sha256').update(source).digest('hex');
 if(sha256!==asset.sha256||!source.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10])))throw new Error('Invalid original raster');
 objects.set(sha256,{sha256,key:`ib/biology/2026-10-30/${sha256}.png`,bytes:source.length,extension:'png',contentType:'image/png',publicPath:asset.publicPath,uses:asset.uses});
 writeFileSync(resolve(output,'assets',sha256+'.png'),source);
}
const manifest={schemaVersion:1,origin:'https://media.thrivingscholars.com',bucket:'thriving-scholars-media',objects:[...objects.values()].sort((a,b)=>a.sha256.localeCompare(b.sha256))};
writeFileSync(resolve(output,'staged-manifest.json'),JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify({output,uniqueDiagrams:manifest.objects.length,references:manifest.objects.reduce((s,o)=>s+o.uses.length,0),bytes:manifest.objects.reduce((s,o)=>s+o.bytes,0)}));
