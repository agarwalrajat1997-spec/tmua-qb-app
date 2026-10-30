import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
import sharp from 'sharp';
import {safeDiagram} from '../../lib/ib/question.ts';
const qs=JSON.parse(readFileSync('content/ib/biology/continuity-change.json','utf8'));
const dir=resolve('../biology-artifacts/theme-d-independent');mkdirSync(dir,{recursive:true});
const entries=[];
for(const q of qs)for(const field of ['diagramSvg','markSchemeDiagramSvg'])if(q[field]){
 if(!safeDiagram(q[field]))throw Error('Unsafe '+q.id);
 const sha256=createHash('sha256').update(q[field]).digest('hex');
 const file=q.id+'-'+field+'.png';
 await sharp(Buffer.from(q[field])).png().toFile(resolve(dir,file));
 entries.push({id:q.id,field,sha256,file,title:q.title});
}
for(let start=0;start<entries.length;start+=8){
 const items=entries.slice(start,start+8),composite=[];
 for(let i=0;i<items.length;i++){
  const item=items[i],x=(i%2)*820,y=Math.floor(i/2)*470;
  const label=Buffer.from('<svg width="820" height="35"><rect width="100%" height="100%" fill="#edf3f7"/><text x="12" y="24" font-family="Arial" font-size="17">'+item.id+': '+item.title+'</text></svg>');
  const pic=await sharp(resolve(dir,item.file)).resize({width:800,height:420,fit:'contain',background:'white'}).png().toBuffer();
  composite.push({input:label,left:x,top:y},{input:pic,left:x+10,top:y+40});
 }
 const file='sheet-'+String(start/8+1).padStart(2,'0')+'.png';
 await sharp({create:{width:1640,height:Math.ceil(items.length/2)*470,channels:3,background:'#ddd'}}).composite(composite).png().toFile(resolve(dir,file));
}
writeFileSync(resolve(dir,'index.json'),JSON.stringify(entries,null,2)+'\n');
console.log(JSON.stringify({figures:entries.length,directory:dir}));
