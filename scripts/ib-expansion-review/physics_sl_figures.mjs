import fs from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';
const root=path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/(\w:)/,'$1')),'../..');
const dest=path.join(root,'docs/ib-expansion-reviews/physics-sl-independent-figures');
const base={'space-time-motion':200,'particulate-matter':120,'wave-behaviour':120,fields:100,'nuclear-quantum':100};
await fs.mkdir(dest,{recursive:true});
const report=[];
for(const [topic,n] of Object.entries(base)){
 const qs=JSON.parse(await fs.readFile(path.join(root,'content/ib/physics-hl',topic+'.json'),'utf8')).filter(q=>q.number>n&&q.diagramSvg);
 for(const q of qs){
  const png=path.join(dest,q.id+'.png');await sharp(Buffer.from(q.diagramSvg)).resize({width:640}).png().toFile(png);
  report.push({id:q.id,topic,input:'serialized diagramSvg',rendered:png});
 }
}
await fs.writeFile(path.join(dest,'render-ledger.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({rendered:report.length,dest}));
