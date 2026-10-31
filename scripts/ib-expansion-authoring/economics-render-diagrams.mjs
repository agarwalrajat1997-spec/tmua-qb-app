import fs from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';
const root=path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/(\w:)/,'$1')),'../..');
const dest=path.join(root,'docs/ib-expansion-reviews/economics-figures');
await fs.mkdir(dest,{recursive:true});
const seen=new Set();const files=[];
for(const name of await fs.readdir(path.join(root,'content/ib/economics'))){
  for(const q of JSON.parse(await fs.readFile(path.join(root,'content/ib/economics',name),'utf8'))){
    if(!q.markSchemeDiagramSvg)continue;
    const shape=q.markSchemeDiagramSvg.replace(/<text x="24" y="25"[^>]*>[^<]*<\/text>/,'').replace(/aria-label="[^"]*"/,'');
    if(seen.has(shape))continue;seen.add(shape);
    const target=path.join(dest,q.id+'.png');
    await sharp(Buffer.from(q.markSchemeDiagramSvg)).resize(800).png().toFile(target);files.push(target);
  }
}
console.log(JSON.stringify({rendered:files.length,destination:dest}));
