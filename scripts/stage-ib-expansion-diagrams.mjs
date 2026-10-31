import {readFileSync,readdirSync,mkdirSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
import {safeDiagram} from '../lib/ib/question.ts';
const output=resolve(process.argv[2]??'../expansion-artifacts');mkdirSync(resolve(output,'assets'),{recursive:true});
const oldAssets=new Set(['maths','physics','chemistry','biology'].flatMap(n=>Object.keys(JSON.parse(readFileSync(`content/ib/${n}-diagram-manifest.json`,'utf8')).assets)));
const objects=new Map();let reusedReferences=0;
for(const course of ['math-ai-hl','economics','business-management','physics-hl'])for(const file of readdirSync(`content/ib/${course}`).filter(f=>f.endsWith('.json'))){
 for(const q of JSON.parse(readFileSync(`content/ib/${course}/${file}`,'utf8')))for(const [field,role] of [['diagramSvg','question'],['markSchemeDiagramSvg','scheme']]){
  const source=q[field];if(!source)continue;if(!safeDiagram(source))throw new Error(q.id+': unsafe SVG');
  const sha256=createHash('sha256').update(source).digest('hex');if(oldAssets.has(sha256)){reusedReferences++;continue;}
  if(!objects.has(sha256))objects.set(sha256,{sha256,key:`ib/expansion/2026-10-31/${sha256}.svg`,bytes:Buffer.byteLength(source),uses:[]});
  objects.get(sha256).uses.push({id:q.id,role,title:q.title});writeFileSync(resolve(output,'assets',sha256+'.svg'),source);
 }
}
const manifest={schemaVersion:1,origin:'https://media.thrivingscholars.com',bucket:'thriving-scholars-media',objects:[...objects.values()].sort((a,b)=>a.sha256.localeCompare(b.sha256))};
writeFileSync(resolve(output,'staged-manifest.json'),JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify({output,uniqueDiagrams:objects.size,references:manifest.objects.reduce((s,o)=>s+o.uses.length,0),reusedReferences}));
