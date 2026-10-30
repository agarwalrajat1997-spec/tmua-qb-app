/** Static author checks only: no browser automation or external mutations. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import sharp from 'sharp';
import katex from 'katex';
import {unified} from 'unified';
import remarkParse from 'remark-parse';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';

const root=process.cwd();
const jsonPath='content/ib/biology/interaction-interdependence.json';
const qs=JSON.parse(fs.readFileSync(jsonPath,'utf8'));
const author=JSON.parse(fs.readFileSync('docs/ib-biology-reviews/theme-c-author.json','utf8'));
const out=path.join(root,'work/biology-theme-c/rendered');
fs.mkdirSync(out,{recursive:true});
const parse=unified().use(remarkParse).use(remarkGfm).use(remarkMath);
const errors=[];const diagrams=[];let maths=0;
const check=(test,msg)=>{if(!test)errors.push(msg);};
const walk=(node,label)=>{
 if(node.type==='math'||node.type==='inlineMath'){
  try{katex.renderToString(node.value,{throwOnError:true,trust:false,strict:'ignore'});maths++;}catch(e){errors.push(label+': '+e.message);}
 }
 for(const child of node.children??[])walk(child,label);
};
const lastSl={'C1.1':10,'C1.2':6,'C1.3':8,'C2.1':0,'C2.2':7,'C3.1':16,'C3.2':18,'C4.1':18,'C4.2':22};
const lastAll={'C1.1':17,'C1.2':17,'C1.3':19,'C2.1':14,'C2.2':16,'C3.1':23,'C3.2':18,'C4.1':18,'C4.2':22};
const coverage={};const statements=new Set();
for(const [i,q] of qs.entries()){
 check(q.id===`ib-bio-c-${String(i+1).padStart(3,'0')}`,q.id+': sequence');
 check(q.number===i+1&&q.source.question===i+1,q.id+': numbering');
 check(q.subject==='biology'&&q.topicId==='interaction-interdependence'&&q.collectionId==='biology-interaction-interdependence',q.id+': identity');
 check(q.calculator===true,q.id+': calculator');
 check(q.marks===q.markScheme.flatMap(g=>g.steps).reduce((n,s)=>n+Number(s.code.slice(1)),0),q.id+': scheme total');
 if(q.questionType==='multiple-choice'){
  check(q.parts.length===0&&q.marks===1&&q.options.length===4,q.id+': MCQ format');
  check(new Set(q.options.map(o=>o.text)).size===4,q.id+': distinct options');
  check(q.options.map(o=>o.label).join('')==='ABCD'&&'ABCD'.includes(q.correctOption),q.id+': MCQ labels');
  check(q.markScheme[0].steps[0].text.startsWith(q.correctOption+'. '),q.id+': key and explanation');
 }else{
  check(q.marks===q.parts.reduce((n,p)=>n+p.marks,0),q.id+': part total');
  for(const p of q.parts){const g=q.markScheme.find(g=>g.part===p.label);check(g?.steps.length===p.marks,q.id+': part '+p.label);}
 }
 const ledger=author.ledger[i];
 check(ledger.id===q.id,q.id+': ledger alignment');
 check(q.level===(ledger.statements.some(s=>Number(s.split('.')[2])>lastSl[q.syllabusCode])?'ahl':'sl'),q.id+': level boundary');
 ledger.statements.forEach(s=>statements.add(s));
 coverage[q.syllabusCode]=(coverage[q.syllabusCode]??0)+1;
 const strings=[q.stem,...q.parts.map(p=>p.prompt),...(q.options??[]).map(o=>o.text),...q.markScheme.flatMap(g=>g.steps.map(s=>s.text))];
 strings.forEach((s,j)=>walk(parse.parse(s),q.id+'/'+j));
 for(const field of ['diagramSvg','markSchemeDiagramSvg'])if(q[field]){
  const name=q.id+'-'+(field==='diagramSvg'?'question':'solution');
  const file=path.join(out,name+'.png');
  await sharp(Buffer.from(q[field])).resize({width:1140}).png().toFile(file);
  diagrams.push({id:q.id,field,name,file,sha256:crypto.createHash('sha256').update(q[field]).digest('hex')});
 }
}
check(qs.length===144,'144 records');
for(const [code,last] of Object.entries(lastAll)){
 check(coverage[code]===16,code+': sixteen records');
 for(let n=1;n<=last;n++)check(statements.has(code+'.'+n),code+'.'+n+': statement coverage');
}
for(let offset=0;offset<diagrams.length;offset+=9){
 const batch=diagrams.slice(offset,offset+9);const layers=[];
 for(const [j,d] of batch.entries()){
  const x=j%3*600,y=Math.floor(j/3)*365;
  layers.push({input:Buffer.from(`<svg width="600" height="34"><rect width="600" height="34" fill="#e4edf3"/><text x="12" y="24" font-family="Arial" font-size="17">${d.name}</text></svg>`),left:x,top:y});
  layers.push({input:await sharp(d.file).resize(580,320,{fit:'inside'}).png().toBuffer(),left:x+10,top:y+40});
 }
 await sharp({create:{width:1800,height:Math.ceil(batch.length/3)*365,channels:4,background:'white'}}).composite(layers).png().toFile(path.join(out,`sheet-${offset/9+1}.png`));
}
const report={questions:qs.length,mathFragments:maths,coverage,guideStatementsCovered:statements.size,figures:diagrams.length,errors,figuresAwaitingVisualAuthorInspection:diagrams,questionJsonSha256:crypto.createHash('sha256').update(fs.readFileSync(jsonPath)).digest('hex')};
fs.writeFileSync('docs/ib-biology-reviews/theme-c-static-check.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({questions:qs.length,coverage,guideStatementsCovered:statements.size,figures:diagrams.length,maths,errors},null,2));
if(errors.length)process.exitCode=1;
