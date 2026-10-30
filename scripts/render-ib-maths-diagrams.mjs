// Deterministic raster proofs of authored vector figures; no browser automation.
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
import sharp from 'sharp';
const dir=resolve(process.argv[2]??'../maths-artifacts');
const manifest=JSON.parse(readFileSync(resolve(dir,'staged-manifest.json'),'utf8'));
mkdirSync(resolve(dir,'proofs'),{recursive:true});
const escape=text=>text.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
for(let start=0;start<manifest.objects.length;start+=24){
 const entries=manifest.objects.slice(start,start+24),layers=[];
 for(let i=0;i<entries.length;i++){
  const item=entries[i],left=(i%3)*520,top=Math.floor(i/3)*370;
  const image=await sharp(readFileSync(resolve(dir,'assets',item.sha256+'.svg')),{density:110}).resize(500,310,{fit:'contain',background:'#ffffff'}).png().toBuffer();
  const label=`${item.uses[0].id} · ${item.uses[0].role} · ${item.sha256.slice(0,9)}`;
  const title=Buffer.from(`<svg width="510" height="40"><rect width="510" height="40" fill="#f4f0e8"/><text x="8" y="25" font-family="Arial" font-size="15">${escape(label)}</text></svg>`);
  layers.push({input:image,left:left+10,top:top+45},{input:title,left:left+5,top:top+5});
 }
 await sharp({create:{width:1560,height:Math.ceil(entries.length/3)*370,channels:3,background:'#d8d8d8'}}).composite(layers).png().toFile(resolve(dir,'proofs',`sheet-${String(start/24+1).padStart(2,'0')}.png`));
}
writeFileSync(resolve(dir,'proofs','index.json'),JSON.stringify(manifest.objects.map((item,index)=>({sheet:Math.floor(index/24)+1,position:index%24+1,...item})),null,2)+'\n');
console.log(JSON.stringify({diagrams:manifest.objects.length,proofSheets:Math.ceil(manifest.objects.length/24)}));
