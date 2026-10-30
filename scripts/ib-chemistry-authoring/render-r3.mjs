import sharp from 'sharp';
import {readFileSync,mkdirSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
const qs=JSON.parse(readFileSync('content/ib/chemistry/reactivity-3.json','utf8'));
const dest=resolve('../chemistry-research/r3-diagrams');mkdirSync(dest,{recursive:true});
const composite=[],index=[];let i=0;
for(const q of qs)for(const key of ['diagramSvg','markSchemeDiagramSvg'])if(q[key]){
 const x=i%3*800,y=Math.floor(i/3)*440;
 const png=await sharp(Buffer.from(q[key])).resize({width:780,height:390,fit:'contain',background:'white'}).png().toBuffer();
 const caption=Buffer.from(`<svg width="800" height="40"><rect width="800" height="40" fill="#fff3ce"/><text x="12" y="26" font-family="Arial" font-size="17">${q.id}: ${key}</text></svg>`);
 composite.push({input:caption,left:x,top:y},{input:png,left:x+10,top:y+45});
 index.push({id:q.id,role:key});i++;
}
await sharp({create:{width:2400,height:Math.ceil(i/3)*440,channels:3,background:'#e6e6e6'}}).composite(composite).png().toFile(resolve(dest,'contact-sheet.png'));
writeFileSync(resolve(dest,'index.json'),JSON.stringify(index,null,2)+'\n');
console.log(resolve(dest,'contact-sheet.png'));
