import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
import sharp from 'sharp';
import katex from 'katex';
import {unified} from 'unified';
import remarkParse from 'remark-parse';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import {ibQuestionSchema,safeDiagram} from '../../lib/ib/question.ts';

const qs=JSON.parse(readFileSync('content/ib/biology/form-function.json','utf8'));
assert.equal(qs.length,160);
const numerical=[];
function calc(n,description,value,expected,answerFragment,tol=1e-9){
 assert.ok(Math.abs(value-expected)<=tol,description);
 assert.ok(JSON.stringify(qs[n-1].markScheme).includes(answerFragment),`q${n}: ${answerFragment}`);
 numerical.push({id:qs[n-1].id,description,recalculated:value,expected,answerFragment});
}
calc(13,'Lipid fuel mass: 760/38.0',760/38,20,'20.0');
calc(13,'Carbohydrate fuel mass rounded to three significant figures',Number((760/17).toPrecision(3)),44.7,'44.7');
calc(14,'Links and water molecules for four open chains of 25 residues',4*(25-1),96,'96');
calc(16,'Difference in unsaturated-residue percentage',72-49,23,'23 percentage');
calc(21,'Four independently chosen positions with three choices each',3**4,81,'81');
calc(24,'Amino acid P from one serving of each food',1.6+.4,2,'2.0');
calc(24,'Amino acid Q from one serving of each food',.3+1.3,1.6,'1.6');
calc(32,'Unfolding-midpoint reduction',68-49,19,'19');
calc(40,'Percentage mass gain',Number(((2.64-2.4)/2.4*100).toFixed(8)),10,'10.0');
calc(46,'Sodium exported in 120 pump cycles',120*3,360,'360');
calc(46,'Potassium imported in 120 pump cycles',120*2,240,'240');
calc(46,'Net outward elementary charges',120*(3-2),120,'120');
calc(71,'Small-cube surface area / volume',6*10**2/10**3,.6,'0.600');
calc(71,'Large-cube surface area / volume',6*20**2/20**3,.3,'0.300');
calc(72,'Convert mm to micrometres before taking linear ratio',1.2*1000/8,150,'150');
calc(80,'Added cylindrical lateral area plus starting area, three significant figures',Number((40+300*2*Math.PI*.05*1).toPrecision(3)),134,'134');
calc(80,'Area multiplication factor, three significant figures',Number(((40+300*2*Math.PI*.05*1)/40).toPrecision(3)),3.36,'3.36');
calc(88,'Vital capacity excludes residual volume',.5+2.4+1.2,4.1,'4.10');
calc(88,'Minute ventilation',.5*15,7.5,'7.5');
calc(90,'Mean stomatal count',(44+48+42+46)/4,45,'45');
calc(90,'Stomatal density',((44+48+42+46)/4)/.2,225,'225');
calc(91,'Potometer displaced-volume rate, two significant figures',Number((Math.PI*.35**2*12/10).toPrecision(2)),.46,'0.46');
calc(92,'Inverse-thickness diffusion factor',.5/.8,.625,'0.625');
calc(94,'Bohr saturation difference at 4 kPa',65-45,20,'20 percentage');
calc(95,'Foetal versus adult saturation difference',85-60,25,'25 percentage');
calc(96,'Resting oxygen extraction per 100 cm3 blood',20*(.97-.75),4.4,'4.40');
calc(96,'Active oxygen extraction per 100 cm3 blood',20*(.97-.35),12.4,'12.4');
calc(103,'Ratio of observed event proportions',12/5,2.4,'2.4');
calc(118,'Sarcomere percentage shortening',(3-2.4)/3*100,20,'20%');
calc(122,'Unrounded static muscle force then two-significant-figure answer',18*.28/.035,144,'1.4');
calc(124,'Mean range rounded to nearest whole degree',Math.round((110+107+112)/3),110,'110');
calc(128,'Force per recruited motor unit',18/6,3,'3 N');
calc(128,'Force for three recruited units',3*3,9,'9 N');
calc(136,'Percentage reduction in skeletal mass gain',(1.8-1.17)/1.8*100,35,'35.0');
calc(141,'Mass-gain difference at pH 6 and pH 8',90-10,80,'80 mg');
calc(143,'Both-resource gain minus water-only gain',8-5,3,'3.0 g');

const parser=unified().use(remarkParse).use(remarkMath).use(remarkGfm);
let mathCount=0;
function markdown(value){
 if(typeof value==='string'){
  const visit=n=>{if(n.type==='math'||n.type==='inlineMath'){katex.renderToString(n.value,{throwOnError:true,strict:'error'});mathCount++;}for(const c of n.children||[])visit(c);};visit(parser.parse(value));
 }else if(Array.isArray(value))value.forEach(markdown);
 else if(value&&typeof value==='object')for(const [k,v] of Object.entries(value))if(!k.endsWith('Svg'))markdown(v);
}
const dir=resolve('../biology-artifacts/theme-b');mkdirSync(dir,{recursive:true});
const pictures=[],records=[];
for(const q of qs){
 const parsed=ibQuestionSchema.safeParse(q);assert.ok(parsed.success,JSON.stringify(parsed.error));
 assert.equal(q.calculator,true);assert.equal(q.subject,'biology');
 assert.equal(q.markScheme.flatMap(p=>p.steps).length,q.marks);
 if(q.questionType==='multiple-choice'){
  assert.equal(q.marks,1);assert.equal(q.parts.length,0);assert.equal(new Set(q.options.map(o=>o.text)).size,4);
  assert.equal(q.options.filter(o=>o.label===q.correctOption).length,1);
 }else assert.equal(q.parts.reduce((n,p)=>n+p.marks,0),q.marks);
 if(q.questionType==='data-based')assert.match(q.stem,/construct|model/i);
 markdown(q);
 for(const key of ['diagramSvg','markSchemeDiagramSvg'])if(q[key]){
  assert.ok(safeDiagram(q[key]));const filename=q.id+'-'+key+'.png';
  await sharp(Buffer.from(q[key])).png().toFile(resolve(dir,filename));
  pictures.push({id:q.id,key,filename,title:q.title,sha256:createHash('sha256').update(q[key]).digest('hex')});
 }
 records.push({id:q.id,level:q.level,difficulty:q.difficulty,sha256:createHash('sha256').update(JSON.stringify(q)).digest('hex')});
}
for(let offset=0;offset<pictures.length;offset+=6){
 const entries=pictures.slice(offset,offset+6),composite=[];
 for(const [i,p] of entries.entries()){
  const x=(i%2)*760,y=Math.floor(i/2)*410;
  const pic=await sharp(resolve(dir,p.filename)).resize({width:740,height:355,fit:'contain',background:'white'}).png().toBuffer();
  const safe=p.title.replaceAll('&','&amp;').replaceAll('<','&lt;');
  const label=Buffer.from(`<svg width="760" height="45"><rect width="100%" height="100%" fill="#edf3f7"/><text x="12" y="28" font-family="Arial" font-size="17">${p.id}: ${safe}</text></svg>`);
  composite.push({input:label,left:x,top:y},{input:pic,left:x+10,top:y+48});
 }
 await sharp({create:{width:1520,height:Math.ceil(entries.length/2)*410,channels:3,background:'#ddd'}}).composite(composite).png().toFile(resolve(dir,`author-sheet-${offset/6+1}.png`));
}
const report={status:'Automated author checks passed; visual inspection and independent review recorded separately.',questions:160,mathExpressions:mathCount,numericalChecks:numerical.length,numerical,records,svgEntries:pictures};
writeFileSync('docs/ib-biology-reviews/form-function-author-checks.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({questions:160,mathExpressions:mathCount,numericalChecks:numerical.length,diagrams:pictures.length,directory:dir}));
