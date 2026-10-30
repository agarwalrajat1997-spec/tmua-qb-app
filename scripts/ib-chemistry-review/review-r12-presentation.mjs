import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
import {unified} from 'unified';
import remarkParse from 'remark-parse';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import katex from 'katex';
import sharp from 'sharp';
import {ibQuestionSchema,questionPrompt,safeDiagram} from '../../lib/ib/question.ts';

const parser=unified().use(remarkParse).use(remarkGfm).use(remarkMath);
const results=[];
for(const bank of ['reactivity-1','reactivity-2']){
 const qs=JSON.parse(readFileSync(`content/ib/chemistry/${bank}.json`,'utf8'));
 if(!qs.length){results.push({bank,status:'awaiting-content'});continue;}
 const errors=[],entries=[],pictures=[];let maths=0;
 function walk(node,id,source){
  if(['math','inlineMath'].includes(node.type)){
   try{katex.renderToString(node.value,{throwOnError:true,strict:'ignore',trust:false});maths++;}
   catch(e){errors.push(id+': '+e.message);}
  }
  if(node.type==='text'&&node.position){
   const raw=source.slice(node.position.start.offset,node.position.end.offset);
   if(/(?<!\\)\$/.test(raw)) errors.push(id+': unparsed dollar delimiter '+raw);
   if(/\\(?:mathrm|Delta|frac|times|exp|ln|sum|rightarrow|to|circ|pm|alpha|beta)\b/.test(raw)) errors.push(id+': raw LaTeX outside math '+raw);
   if(/(?:kJ|mol|dm|cm|K|s)\s*\^\{?-?\d/.test(raw)) errors.push(id+': raw unit exponent '+raw);
  }
  node.children?.forEach(c=>walk(c,id,source));
 }
 for(const q of qs){
  const e0=errors.length,m0=maths;
  const parsed=ibQuestionSchema.safeParse(q);if(!parsed.success)errors.push(q.id+': '+parsed.error.message);
  const strings=[q.stem,...q.parts.map(p=>p.prompt),...(q.options||[]).map(o=>o.text),...q.markScheme.flatMap(g=>g.steps.map(s=>s.text))];
  for(const s of strings){
   if(/[\u0000-\u0009\u000b-\u001f\ufffd]/.test(s))errors.push(q.id+': invalid/control character');
   walk(parser.parse(s),q.id,s);
  }
  const pub=questionPrompt(q);
  for(const key of ['markScheme','correctOption','answerSummary','source','verification','markSchemeDiagramSvg'])if(key in pub)errors.push(q.id+': private field exposed '+key);
  for(const key of ['diagramSvg','markSchemeDiagramSvg'])if(q[key]){
   if(!safeDiagram(q[key]))errors.push(q.id+': unsafe SVG');
   pictures.push({id:q.id,key,svg:q[key]});
  }
  entries.push({id:q.id,mathExpressions:maths-m0,status:errors.length===e0?'passed':'failed'});
 }
 const dest=resolve(`../chemistry-research/${bank}-diagrams`);mkdirSync(dest,{recursive:true});
 for(let offset=0;offset<pictures.length;offset+=9){
  const group=pictures.slice(offset,offset+9),composite=[];
  for(const [i,pic] of group.entries()){
   const x=i%3*800,y=Math.floor(i/3)*440;
   const png=await sharp(Buffer.from(pic.svg)).resize({width:780,height:390,fit:'contain',background:'white'}).png().toBuffer();
   const caption=Buffer.from(`<svg width="800" height="40"><rect width="800" height="40" fill="#fff3ce"/><text x="12" y="26" font-family="Arial" font-size="17">${pic.id}: ${pic.key}</text></svg>`);
   composite.push({input:caption,left:x,top:y},{input:png,left:x+10,top:y+45});
  }
  await sharp({create:{width:2400,height:Math.ceil(group.length/3)*440,channels:3,background:'#eee'}}).composite(composite).png().toFile(resolve(dest,`sheet-${1+offset/9}.png`));
 }
 writeFileSync(resolve(dest,'index.json'),JSON.stringify(pictures.map(({id,key})=>({id,key})),null,2)+'\n');
 const report={bank,status:errors.length?'failed':'passed',questions:qs.length,mathExpressions:maths,diagrams:pictures.length,entries,errors};
 writeFileSync(`docs/ib-chemistry-reviews/${bank}-presentation-audit.json`,JSON.stringify(report,null,2)+'\n');
 results.push({...report,entries:undefined});
}
console.log(JSON.stringify(results));
if(results.some(r=>r.status==='failed'))process.exitCode=1;
