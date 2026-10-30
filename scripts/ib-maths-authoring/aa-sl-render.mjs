import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
const require=createRequire(import.meta.url);
const sharp=require('sharp');
const root=process.cwd(),bank=process.argv[2]||'math-aa-sl',out=path.join(root,'work',process.argv[3]||'aa-sl-review');
await fs.mkdir(out,{recursive:true});
const figs=[];
for(const name of (await fs.readdir(path.join(root,'content/ib',bank))).sort()){
 const qs=JSON.parse(await fs.readFile(path.join(root,'content/ib',bank,name),'utf8'));
 for(const q of qs)for(const field of ['diagramSvg','markSchemeDiagramSvg'])if(q[field]){
  const id=q.id+(field==='diagramSvg'?'-question':'-solution');
  const png=await sharp(Buffer.from(q[field])).resize(620,360,{fit:'contain',background:'white'}).png().toBuffer();
  await fs.writeFile(path.join(out,id+'.png'),png);
  const label='<svg xmlns="http://www.w3.org/2000/svg" width="620" height="30"><text x="12" y="21" font-size="17" font-family="Arial">'+id+'</text></svg>';
  figs.push({id,png,banner:Buffer.from(label)});
 }
}
for(let offset=0;offset<figs.length;offset+=12){
 const batch=figs.slice(offset,offset+12),layers=[];
 for(let j=0;j<batch.length;j++){const left=(j%3)*620,top=Math.floor(j/3)*390;layers.push({input:batch[j].banner,left,top},{input:batch[j].png,left,top:top+30});}
 await sharp({create:{width:1860,height:Math.ceil(batch.length/3)*390,channels:3,background:'white'}}).composite(layers).png().toFile(path.join(out,'contact-'+(offset/12+1)+'.png'));
}
console.log(JSON.stringify({figures:figs.length,out}));
