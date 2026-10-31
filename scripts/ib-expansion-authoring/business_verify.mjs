import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import sharp from 'sharp';
import {ibQuestionSchema,questionPrompt,safeDiagram} from '../../lib/ib/question.ts';
import {unified} from 'unified';
import remarkParse from 'remark-parse';
import remarkGfm from 'remark-gfm';
const root=process.cwd(),dir=path.join(root,'content/ib/business-management');
const renderDir=path.join(root,'docs/ib-expansion-reviews/business-figures');
fs.mkdirSync(renderDir,{recursive:true});
const records=fs.readdirSync(dir).filter(n=>n.endsWith('.json')).flatMap(n=>JSON.parse(fs.readFileSync(path.join(dir,n),'utf8')));
const parser=unified().use(remarkParse).use(remarkGfm);
let tables=0;const renders=[],coverage={},ids=new Set(),fingerprints=new Set();
for(const q of records){
  const p=ibQuestionSchema.safeParse(q);assert.ok(p.success,q.id+': '+p.error?.message);
  assert.ok(!ids.has(q.id),'Duplicate ID');ids.add(q.id);
  const fp=crypto.createHash('sha256').update(q.stem+JSON.stringify(q.parts)).digest('hex');assert.ok(!fingerprints.has(fp),'Duplicate stem and parts');fingerprints.add(fp);
  assert.equal(q.calculator,true);assert.equal(q.status,'published');
  const prompt=questionPrompt(p.data);
  for(const key of ['markScheme','verification','source','answerSummary','markSchemeDiagramSvg','markSchemeDiagramUrl'])assert.ok(!(key in prompt),q.id+' leaked '+key);
  const strings=[q.stem,...q.parts.map(x=>x.prompt),...q.markScheme.flatMap(g=>g.steps.map(s=>s.text))];
  for(const s of strings){
    assert.ok(!/[\u0000-\u0008\u000b-\u001f]|\\n\\n|\bTODO\b|\bTBD\b/.test(s),q.id+' malformed text');
    const tree=parser.parse(s);const walk=n=>{if(n.type==='table')tables++;if(n.children)n.children.forEach(walk);};walk(tree);
  }
  for(const g of q.markScheme){assert.equal(new Set(g.steps.map(s=>s.text)).size,g.steps.length,q.id+' duplicated criterion');if(g.rubric)assert.ok(g.steps.every(s=>s.code==='IND'));}
  coverage[q.syllabusCode]??={sl:0,ahl:0};coverage[q.syllabusCode][q.level]++;
  for(const key of ['diagramSvg','markSchemeDiagramSvg'])if(q[key]){
    assert.ok(safeDiagram(q[key]),q.id+' unsafe SVG');
    const buf=await sharp(Buffer.from(q[key])).resize(780).png().toBuffer();
    const meta=await sharp(buf).metadata();assert.ok(meta.width&&meta.height,q.id+' empty rendering');
    const file=q.id+'-'+(key==='diagramSvg'?'question':'solution')+'.png';fs.writeFileSync(path.join(renderDir,file),buf);
    renders.push({id:q.id,kind:key,file,width:meta.width,height:meta.height,sha256:crypto.createHash('sha256').update(q[key]).digest('hex')});
  }
}
assert.equal(records.length,400);
const counts=Object.fromEntries([...new Set(records.map(q=>q.topicId))].map(t=>[t,records.filter(q=>q.topicId===t).length]));Object.values(counts).forEach(n=>assert.equal(n,80));
for(const t of Object.keys(counts))assert.deepEqual(records.filter(q=>q.topicId===t).map(q=>q.number),Array.from({length:80},(_,i)=>i+1));
assert.equal(records.filter(q=>q.level==='sl').length,260);assert.equal(records.filter(q=>q.level==='ahl').length,140);
const sheets=[];
for(let offset=0;offset<renders.length;offset+=12){
  const subset=renders.slice(offset,offset+12),composite=[];
  for(let i=0;i<subset.length;i++){
    const r=subset[i],x=(i%3)*400,y=Math.floor(i/3)*255;
    const thumb=await sharp(path.join(renderDir,r.file)).resize({width:390,height:215,fit:'contain',background:'#ffffff'}).png().toBuffer();
    const label=Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="390" height="25"><text x="5" y="19" font-size="15" font-family="Arial">${r.id} ${r.kind==='diagramSvg'?'question':'solution'}</text></svg>`);
    composite.push({input:thumb,left:x,top:y+28},{input:label,left:x,top:y});
  }
  const file=`business-contact-${Math.floor(offset/12)+1}.png`;
  await sharp({create:{width:1200,height:Math.ceil(subset.length/3)*255,channels:3,background:'#ffffff'}}).composite(composite).png().toFile(path.join(renderDir,file));sheets.push(file);
}
const report={records:records.length,counts,levels:{sl:260,ahl:140},coverage,tables,renderedFigures:renders.length,contactSheets:sheets,renders,schema:'passed',promptPrivacy:'passed',distinctCriteria:'passed',originalPromptFingerprints:400};
fs.writeFileSync(path.join(root,'docs/ib-expansion-reviews/business-render-schema-report.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({records:400,counts,levels:report.levels,tables,renders:renders.length,schema:'passed',promptPrivacy:'passed'},null,2));
