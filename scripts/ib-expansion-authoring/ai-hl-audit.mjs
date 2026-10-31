import {readFileSync,writeFileSync,readdirSync,mkdirSync,unlinkSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import katex from 'katex';
import {unified} from 'unified';
import remarkParse from 'remark-parse';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import sharp from 'sharp';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../..');
const bank=resolve(root,'content/ib/math-ai-hl');
const out=resolve(root,'docs/ib-expansion-reviews');
const figures=resolve(out,'ai-hl-figures');
mkdirSync(figures,{recursive:true});
const hash=x=>createHash('sha256').update(x).digest('hex');
const parser=unified().use(remarkParse).use(remarkGfm).use(remarkMath);
const ledger=JSON.parse(readFileSync(resolve(out,'ai-hl-author-ledger.json'),'utf8'));
const errors=[],assets=new Map(),seen=new Set(),all=[],files=[];
let formulae=0;
function inspect(text,id){
 if(/[\u0000-\u0009\u000b-\u001f]/.test(text)) errors.push(id+': control character');
 if(/np\.(?:int|float)|NaN|Infinity|TODO|TBD/.test(text))errors.push(id+': non-public calculation text');
 function visit(n){
  if(n.type==='inlineMath'||n.type==='math'){
   formulae++;
   try{katex.renderToString(n.value,{throwOnError:true,strict:'ignore',trust:false});}catch(e){errors.push(id+': '+e.message);}
  }
  if(n.type==='text'&&n.value.includes('$')&&n.position){
   const raw=text.slice(n.position.start.offset,n.position.end.offset);
   if(/(?<!\\)\$/.test(raw))errors.push(id+': unparsed math delimiter');
  }
  n.children?.forEach(visit);
 }
 visit(parser.parse(text));
}
for(const f of readdirSync(bank).filter(x=>x.endsWith('.json')).sort()){
 const bytes=readFileSync(resolve(bank,f)),qs=JSON.parse(bytes);files.push({path:'content/ib/math-ai-hl/'+f,count:qs.length,sha256:hash(bytes)});
 assert([80,100].includes(qs.length));
 qs.forEach((q,i)=>{
  try{
   assert.equal(q.number,i+1);assert.equal(q.source.question,q.number);assert.equal(q.calculator,true);assert.equal(q.subject,'math-ai-hl');assert.equal(q.status,'published');assert.equal(q.source.document,'Independent syllabus-authored practice');
   const prefix={ 'number-algebra':'na',functions:'fn','geometry-trigonometry':'gt','statistics-probability':'sp',calculus:'ca'}[q.topicId];
   assert.equal(q.id,`ib-aihl-${prefix}-${String(q.number).padStart(3,'0')}`);assert.equal(q.collectionId,'ai-hl-'+q.topicId);assert(!seen.has(q.id));seen.add(q.id);
   assert(q.marks>=1&&q.marks<=60);assert(!q.options&&!q.correctOption);
   assert.equal(q.parts.reduce((s,p)=>s+p.marks,0),q.marks);assert.equal(q.parts.length,q.markScheme.length);
   for(const p of q.parts){const g=q.markScheme.find(x=>x.part===p.label);assert(g);assert.equal(g.steps.reduce((s,x)=>s+(x.code==='AG'?0:Number(x.code.slice(1))),0),p.marks);assert.equal(new Set(g.steps.map(x=>x.text)).size,g.steps.length);g.steps.forEach(s=>assert(/^[MAR]1$/.test(s.code)));}
   const l=ledger.find(x=>x.id===q.id);assert(l);assert.equal(l.syllabusCode,q.syllabusCode);assert.equal(l.level,q.level);assert.equal(l.marks,q.marks);
  }catch(e){errors.push(q.id+': '+e.message);}
  [q.title,q.stem,...q.parts.map(p=>p.prompt),...q.markScheme.flatMap(g=>g.steps.map(s=>s.text))].forEach(t=>inspect(t,q.id));
  for(const role of ['diagramSvg','markSchemeDiagramSvg'])if(q[role]){
   const s=q[role];
   if(!/^<svg\b/.test(s)||!s.includes('viewBox=')||!/<\/svg>$/.test(s)||/<(?:script|foreignObject|iframe|object|embed|image|style|animate|set|use)\b|\bon\w+\s*=|(?:href|src)\s*=|url\s*\(/i.test(s))errors.push(q.id+': unsafe SVG');
   const sha=hash(s);if(!assets.has(sha))assets.set(sha,{sha256:sha,svg:s,uses:[]});assets.get(sha).uses.push({id:q.id,role});
  }
  all.push(q);
 });
}
const fam=new Map();for(const r of ledger){fam.set(r.family,(fam.get(r.family)||0)+1);assert.equal(r.variant,(Number(r.id.slice(-3))-1)%4+1);}
for(const [f,n]of fam)assert.equal(n,4,f);
if(errors.length){console.error(JSON.stringify({errors},null,2));process.exit(1);}
const objects=[...assets.values()];
const expectedFiles=new Set(objects.flatMap(x=>[x.sha256+'.svg',x.sha256+'.png']));
for(let n=1;n<=Math.ceil(objects.length/12);n++)expectedFiles.add(`sheet-${String(n).padStart(2,'0')}.png`);
for(const file of readdirSync(figures))if(/^(?:[a-f0-9]{64}\.(?:svg|png)|sheet-\d+\.png)$/.test(file)&&!expectedFiles.has(file))unlinkSync(resolve(figures,file));
for(const item of objects){
 writeFileSync(resolve(figures,item.sha256+'.svg'),item.svg);
 await sharp(Buffer.from(item.svg),{density:144}).resize(1200,760,{fit:'contain',background:'#fff'}).png().toFile(resolve(figures,item.sha256+'.png'));
}
for(let start=0;start<objects.length;start+=12){
 const chunk=objects.slice(start,start+12),layers=[];
 for(let i=0;i<chunk.length;i++){
  const item=chunk[i],left=(i%3)*620,top=Math.floor(i/3)*440;
  const png=await sharp(resolve(figures,item.sha256+'.png')).resize(600,380).png().toBuffer();
  const label=Buffer.from(`<svg width="610" height="45"><rect width="610" height="45" fill="#eef2f5"/><text x="10" y="28" font-size="17" font-family="Arial">${item.uses[0].id} / ${item.uses[0].role} / ${item.sha256.slice(0,8)}</text></svg>`);
  layers.push({input:label,left:left+5,top:top+5},{input:png,left:left+10,top:top+50});
 }
 await sharp({create:{width:1860,height:Math.ceil(chunk.length/3)*440,channels:3,background:'#d6dce0'}}).composite(layers).png().toFile(resolve(figures,`sheet-${String(start/12+1).padStart(2,'0')}.png`));
}
const report={course:'Mathematics: applications and interpretation HL',guideFirstAssessment:2021,guideFinalAssessment:2028,records:all.length,topics:files,families:fam.size,maxVariants:Math.max(...fam.values()),calculatorRequired:true,investigations:all.filter(q=>q.marks>=12).length,formulaeValidated:formulae,diagramUses:objects.reduce((n,x)=>n+x.uses.length,0),uniqueDiagramsRendered:objects.length,proofSheets:Math.ceil(objects.length/12),errors:[],ledgerSha256:hash(readFileSync(resolve(out,'ai-hl-author-ledger.json'))),figures:objects.map(({svg,...rest})=>rest)};
writeFileSync(resolve(out,'ai-hl-author-audit.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({...report,figures:undefined,topics:files.map(f=>({count:f.count,path:f.path}))}));
