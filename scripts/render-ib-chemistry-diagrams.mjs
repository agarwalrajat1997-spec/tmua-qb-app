import sharp from 'sharp';
import {readFileSync,mkdirSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
const root=resolve(process.argv[2]||'../chemistry-artifacts');
const manifest=JSON.parse(readFileSync(resolve(root,'staged-manifest.json'),'utf8'));
const dir=resolve(root,'sheets');mkdirSync(dir,{recursive:true});
const objects=[...manifest.objects].sort((a,b)=>a.uses[0].id.localeCompare(b.uses[0].id)||a.uses[0].role.localeCompare(b.uses[0].role));
const columns=3,rows=4,w=720,h=440;
const escape=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const index=[];
for(let start=0;start<objects.length;start+=columns*rows){
 const subset=objects.slice(start,start+columns*rows),composite=[];
 for(let i=0;i<subset.length;i++){
  const item=subset[i],u=item.uses[0],x=(i%columns)*w,y=Math.floor(i/columns)*h;
  const source=readFileSync(resolve(root,'assets',item.sha256+'.svg'));
  const png=await sharp(source).resize({width:w-30,height:h-75,fit:'contain',background:'white'}).png().toBuffer();
  const caption=`${u.id} ${u.role}: ${u.title}`.slice(0,87);
  const label=Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="50"><rect width="100%" height="100%" fill="#fff3ce"/><text x="12" y="23" font-family="Arial" font-size="14">${escape(caption)}</text><text x="12" y="43" font-family="Arial" font-size="12">${item.sha256.slice(0,20)} · ${item.uses.length} use(s)</text></svg>`);
  composite.push({input:label,left:x,top:y},{input:png,left:x+15,top:y+55});
 }
 const filename='sheet-'+String(start/(columns*rows)+1).padStart(2,'0')+'.png';
 await sharp({create:{width:columns*w,height:rows*h,channels:3,background:'#e6e6e6'}}).composite(composite).png().toFile(resolve(dir,filename));
 index.push({sheet:filename,diagrams:subset.map(o=>({sha256:o.sha256,uses:o.uses}))});
}
writeFileSync(resolve(dir,'index.json'),JSON.stringify(index,null,2)+'\n');
console.log(JSON.stringify({diagrams:objects.length,sheets:index.length,directory:dir}));
