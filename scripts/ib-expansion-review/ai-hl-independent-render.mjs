// Independently rasterize the actual final learner/markscheme SVG strings.
import { readFileSync, writeFileSync, mkdirSync, readdirSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import sharp from 'sharp';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../..');
const dest=resolve(root,'work/ai-hl-independent/figures');
mkdirSync(dest,{recursive:true});
const digest=x=>createHash('sha256').update(x).digest('hex');
const figures=new Map();
for(const f of readdirSync(resolve(root,'content/ib/math-ai-hl')).filter(x=>x.endsWith('.json')).sort()){
 for(const q of JSON.parse(readFileSync(resolve(root,'content/ib/math-ai-hl',f),'utf8'))){
  for(const role of ['diagramSvg','markSchemeDiagramSvg'])if(q[role]){
   const sha=digest(q[role]);
   if(!figures.has(sha))figures.set(sha,{sha256:sha,svg:q[role],uses:[]});
   figures.get(sha).uses.push({id:q.id,role});
  }
 }
}
const items=[...figures.values()];
for(const f of items){
 await sharp(Buffer.from(f.svg),{density:144}).resize(1200,760,{fit:'contain',background:'white'}).png().toFile(resolve(dest,f.sha256+'.png'));
}
const pages=[];
for(let start=0;start<items.length;start+=12){
 const chunk=items.slice(start,start+12),layers=[];
 for(let k=0;k<chunk.length;k++){
  const f=chunk[k],left=k%3*620,top=Math.floor(k/3)*440;
  const label=Buffer.from(`<svg width="610" height="44"><rect width="610" height="44" fill="#edf1f4"/><text x="8" y="27" font-size="16" font-family="Arial">${f.uses[0].id} / ${f.uses[0].role} / ${f.sha256.slice(0,8)}</text></svg>`);
  layers.push({input:label,left:left+5,top:top+4},{input:await sharp(resolve(dest,f.sha256+'.png')).resize(600,380).toBuffer(),left:left+10,top:top+50});
 }
 const file=`sheet-${String(start/12+1).padStart(2,'0')}.png`;
 await sharp({create:{width:1860,height:Math.ceil(chunk.length/3)*440,channels:3,background:'#d2d9de'}}).composite(layers).png().toFile(resolve(dest,file));
 pages.push({path:'work/ai-hl-independent/figures/'+file,sha256:digest(readFileSync(resolve(dest,file)))});
}
const index={uniqueDiagrams:items.length,diagramUses:items.reduce((n,f)=>n+f.uses.length,0),sheets:pages,figures:items.map(({svg,...f})=>({...f,pngSha256:digest(readFileSync(resolve(dest,f.sha256+'.png')))}))};
writeFileSync(resolve(dest,'index.json'),JSON.stringify(index,null,2)+'\n');
console.log(JSON.stringify({uniqueDiagrams:index.uniqueDiagrams,diagramUses:index.diagramUses,sheets:pages}));
