import fs from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';
import crypto from 'node:crypto';
const root=process.cwd(),dest=path.join(root,'docs/ib-expansion-reviews/business-independent-figures');
await fs.mkdir(dest,{recursive:true});
const records=[];
for(const name of (await fs.readdir('content/ib/business-management')).filter(n=>n.endsWith('.json')).sort()){
 const qs=JSON.parse(await fs.readFile(path.join(root,'content/ib/business-management',name),'utf8'));
 for(const q of qs)for(const key of ['diagramSvg','markSchemeDiagramSvg'])if(q[key]){
  const file=q.id+'-'+key+'.png',buf=await sharp(Buffer.from(q[key])).resize({width:760}).png().toBuffer();
  await fs.writeFile(path.join(dest,file),buf);
  const {height}=await sharp(buf).metadata();
  records.push({id:q.id,key,file,svgSha256:crypto.createHash('sha256').update(q[key]).digest('hex'),height});
 }
}
for(let i=0;i<records.length;i+=8){
 const batch=records.slice(i,i+8),overlays=[];
 for(let j=0;j<batch.length;j++){
  const {file,id,key}=batch[j],left=(j%2)*780,top=Math.floor(j/2)*390;
  const title=Buffer.from(`<svg width="760" height="35"><rect width="760" height="35" fill="#dbeafe"/><text x="8" y="24" font-size="19" font-family="Arial">${id} ${key}</text></svg>`);
  overlays.push({input:title,left,top});
  overlays.push({input:await sharp(path.join(dest,file)).resize({width:760,height:350,fit:'inside'}).png().toBuffer(),left,top:top+35});
 }
 await sharp({create:{width:1560,height:Math.ceil(batch.length/2)*390,channels:3,background:'white'}}).composite(overlays).png().toFile(path.join(dest,`contact-${i/8+1}.png`));
}
await fs.writeFile(path.join(dest,'render-ledger.json'),JSON.stringify({rendered:records.length,records},null,2)+'\n');
console.log(JSON.stringify({rendered:records.length,contacts:Math.ceil(records.length/8),dest}));
