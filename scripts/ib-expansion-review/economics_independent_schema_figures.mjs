import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import sharp from 'sharp';
import {ibQuestionSchema,questionPrompt,safeDiagram} from '../../lib/ib/question.ts';
import {unified} from 'unified';
import remarkParse from 'remark-parse';
import remarkGfm from 'remark-gfm';
const root=process.cwd(),out=path.join(root,'docs/ib-expansion-reviews/economics-independent-figures');fs.mkdirSync(out,{recursive:true});
const qs=fs.readdirSync(path.join(root,'content/ib/economics')).filter(x=>x.endsWith('.json')).flatMap(file=>JSON.parse(fs.readFileSync(path.join(root,'content/ib/economics',file),'utf8')));
const parser=unified().use(remarkParse).use(remarkGfm),designs=[],seen=new Map(),records=[];let tables=0,bands=0;
for(const q of qs){
 const r=ibQuestionSchema.safeParse(q);assert.ok(r.success,q.id+': '+r.error?.message);
 const prompt=questionPrompt(r.data);for(const f of ['markScheme','markSchemeDiagramSvg','markSchemeDiagramUrl','source','verification'])assert.ok(!(f in prompt),q.id+' leaked '+f);
 assert.ok(!q.diagramSvg,q.id+' public worked diagram');
 const strings=[q.stem,...q.parts.map(x=>x.prompt),...q.markScheme.flatMap(g=>g.steps.map(x=>x.text))];
 for(const s of strings){assert.ok(!/[\u0000-\u0008\u000b-\u001f]|\\n/.test(s),q.id+' malformed text');const walk=n=>{if(n.type==='table')tables++;n.children?.forEach(walk)};walk(parser.parse(s));}
 for(const [i,g] of q.markScheme.entries()){
   if(g.rubric){bands++;assert.ok(g.steps.every(s=>s.code==='IND'));assert.ok(g.rubric.bands.every(b=>b.descriptor.includes('Focus: '+q.parts[i].prompt)),q.id+' generic rubric focus');}
   assert.equal(new Set(g.steps.map(s=>s.text)).size,g.steps.length,q.id+' duplicate criterion');
 }
 const rec={id:q.id,schema:'passed',promptPrivacy:'passed',markingStructure:'passed',diagram:null};
 if(q.markSchemeDiagramSvg){
   const svg=q.markSchemeDiagramSvg;assert.ok(safeDiagram(svg));
   const shape=svg.replace(/<text x="24" y="25"[^>]*>[^<]*<\/text>/,'').replace(/aria-label="[^"]*"/,'');
   let index=seen.get(shape);
   if(index===undefined){index=designs.length;seen.set(shape,index);designs.push({index,id:q.id,file:q.id+'.png',labels:[...svg.matchAll(/<text[^>]*>(.*?)<\/text>/g)].map(m=>m[1])});}
   const png=await sharp(Buffer.from(svg)).resize(800).png().toBuffer();fs.writeFileSync(path.join(out,q.id+'.png'),png);
   rec.diagram={status:'rendered',design:index,sha256:crypto.createHash('sha256').update(svg).digest('hex')};
 }
 records.push(rec);
}
const sheets=[];
for(let start=0;start<designs.length;start+=8){
 const subset=designs.slice(start,start+8),images=[];
 for(let i=0;i<subset.length;i++){
  const d=subset[i],x=i%2*650,y=Math.floor(i/2)*445;
  const png=await sharp(path.join(out,d.file)).resize(640).png().toBuffer();images.push({input:png,left:x,top:y+25});
  const text=Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="640" height="25"><text x="5" y="18" font-size="15">${d.id}; design ${d.index}</text></svg>`);images.push({input:text,left:x,top:y});
 }
 const file='contact-'+(Math.floor(start/8)+1)+'.png';await sharp({create:{width:1300,height:Math.ceil(subset.length/2)*445,channels:3,background:'#ffffff'}}).composite(images).png().toFile(path.join(out,file));sheets.push(file);
}
const report={status:'passed',records:qs.length,levelledGroups:bands,tables,renderedSvgCount:records.filter(r=>r.diagram).length,distinctRenderedDesigns:designs.length,contactSheets:sheets,designs,perRecord:records};
fs.writeFileSync(path.join(root,'docs/ib-expansion-reviews/economics-independent-schema-figures.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({status:report.status,records:qs.length,levelledGroups:bands,tables,renderedSvgCount:report.renderedSvgCount,distinctRenderedDesigns:designs.length}));
