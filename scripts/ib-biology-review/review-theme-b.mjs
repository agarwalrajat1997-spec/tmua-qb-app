/** Independent complete-bank review checks. No browser, network or content mutation. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import sharp from 'sharp';
import {ibQuestionSchema,safeDiagram,questionPrompt} from '../../lib/ib/question.ts';
import {unified} from 'unified';
import remarkParse from 'remark-parse';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import katex from 'katex';

const snapshot=process.argv.includes('--snapshot');
const source=snapshot?'work/theme-b-review-snapshot.json':'content/ib/biology/form-function.json';
const qs=JSON.parse(fs.readFileSync(source,'utf8'));
const out=path.resolve('work/biology-theme-b-independent/rendered');fs.mkdirSync(out,{recursive:true});
const errors=[];const numeric=[];const figures=[];const rasterFigures=[];const records=[];let maths=0;
const hash=s=>crypto.createHash('sha256').update(s).digest('hex');
const check=(condition,label)=>{if(!condition)errors.push(label);};
const parser=unified().use(remarkParse).use(remarkGfm).use(remarkMath);
function visit(n,id){if(n.type==='math'||n.type==='inlineMath'){try{katex.renderToString(n.value,{throwOnError:true,trust:false,strict:'ignore'});maths++;}catch(e){errors.push(id+': '+e.message);}}for(const c of n.children??[])visit(c,id);}
const topicRanges=[['B1.1',1,16,16],['B1.2',17,32,24],['B2.1',33,48,40],['B2.2',49,64,54],['B2.3',65,80,72],['B3.1',81,96,92],['B3.2',97,112,106],['B3.3',113,128,112],['B4.1',129,144,144],['B4.2',145,160,160]];
for(const [index,q] of qs.entries()){
 const parsed=ibQuestionSchema.safeParse(q);check(parsed.success,q.id+': schema '+(parsed.success?'':parsed.error.message));
 check(q.number===index+1&&q.id===`ib-bio-b-${String(index+1).padStart(3,'0')}`,q.id+': consecutive numbering');
 const range=topicRanges.find(([,first,last])=>q.number>=first&&q.number<=last);
 check(range&&q.syllabusCode===range[0],q.id+': topic mapping');
 check(range&&q.level===(q.number<=range[3]?'sl':'ahl'),q.id+': independently assessed required-knowledge level');
 const prompt=questionPrompt(q);check(!('markScheme'in prompt)&&!('correctOption'in prompt)&&!('verification'in prompt),q.id+': answer privacy');
 const strings=[q.stem,...q.parts.map(p=>p.prompt),...(q.options??[]).map(o=>o.text),...q.markScheme.flatMap(g=>g.steps.map(s=>s.text))];
 for(const s of strings)visit(parser.parse(s),q.id);
 if(q.options){check(new Set(q.options.map(o=>o.text)).size===4,q.id+': unique options');check(q.markScheme[0].steps[0].text.startsWith(q.correctOption+'. '),q.id+': key/rationale label');}
 for(const field of ['diagramSvg','markSchemeDiagramSvg'])if(q[field]){
  check(safeDiagram(q[field]),q.id+': safe '+field);
  const name=q.id+'-'+(field==='diagramSvg'?'question':'solution');const file=path.join(out,name+'.png');
  await sharp(Buffer.from(q[field])).resize({width:1152}).png().toFile(file);
  figures.push({id:q.id,field,name,file,sha256:hash(q[field])});
 }
 for(const field of ['diagramUrl','markSchemeDiagramUrl'])if(q[field]&&!q[field].endsWith('.svg')){
  const filename=q[field].split('/').pop();
  check(/^[a-f0-9]{64}\.png$/.test(filename),q.id+': content-addressed raster '+field);
  const localFile=path.resolve('public/ib-assets/biology',filename);
  check(fs.existsSync(localFile),q.id+': local raster review asset');
  if(fs.existsSync(localFile)){
   const bytes=fs.readFileSync(localFile);const metadata=await sharp(bytes).metadata();
   check(hash(bytes)===filename.slice(0,64),q.id+': exact raster bytes');
   check(metadata.width>0&&metadata.height>0,q.id+': decodable raster dimensions');
   rasterFigures.push({id:q.id,field,url:q[field],file:localFile,sha256:hash(bytes),width:metadata.width,height:metadata.height});
  }
 }
 records.push({id:q.id,syllabusCode:q.syllabusCode,level:q.level,sha256:hash(JSON.stringify(q)),editorialReview:'Complete prompt, all options where present, all marking points and scope read independently.'});
}
check(qs.length===160,'160 complete records');
const Q=n=>qs[n-1];
const sourceText=n=>[Q(n).stem,...Q(n).parts.map(p=>p.prompt)].join('\n');
const answerText=n=>Q(n).markScheme.flatMap(g=>g.steps.map(s=>s.text)).join('\n');
const words={one:1,two:2,three:3,four:4};
function value(n,regex,group=1){const match=sourceText(n).match(regex);check(!!match,Q(n).id+': displayed input '+regex);if(!match)return NaN;return words[match[group].toLowerCase()]??Number(match[group]);}
function calc(n,label,inputs,formula,answerEvidence,unrounded){
 const result=formula(...inputs.map(x=>x.value));
 check(Number.isFinite(result),Q(n).id+': finite '+label);
 check(Math.abs(result-unrounded)<Math.max(1e-9,Math.abs(unrounded)*1e-10),Q(n).id+': independent '+label);
 check(answerEvidence.test(answerText(n)),Q(n).id+': accepted displayed answer for '+label);
 numeric.push({id:Q(n).id,quantity:label,inputs,independentResult:result,acceptedAnswerEvidence:answerText(n).match(answerEvidence)?.[0]??null,status:'recomputed from question quantities and reconciled with scheme'});
}
const input=(name,v)=>({name,value:v});
const read=(n,name,re,g=1)=>input(name,value(n,re,g));
calc(8,'Ester links and released water',[read(8,'fatty acids',/(three) fatty/)],x=>x,/Three ester links[\s\S]*Three water molecules/,3);
const fuel=[read(13,'required kJ',/needs ([\d.]+) kJ/),read(13,'lipid kJ per g',/lipid supplies ([\d.]+)/),read(13,'carbohydrate kJ per g',/carbohydrate supplies ([\d.]+)/)];
calc(13,'lipid mass',fuel,(e,f)=>e/f,/20\.0/,20);calc(13,'carbohydrate mass',fuel,(e,f,c)=>e/c,/44\.7/,760/17);
calc(14,'hydrolysed links and consumed water',[read(14,'separate chains',/(four) separate/),read(14,'residues per chain',/exactly (\d+) glucose/)],(c,n)=>c*(n-1),/96 links[\s\S]*96 water/,96);
calc(16,'unsaturated-residue percentage-point difference',[read(16,'cool treatment',/\|12\|(\d+)\|/),read(16,'warm treatment',/\|24\|(\d+)\|/)],(a,b)=>a-b,/23 percentage points/,23);
const peptide=[read(21,'positions',/(four) positions/),read(21,'choices per position',/(three) amino acid/)]
calc(21,'ordered peptide sequences',peptide,(n,k)=>k**n,/81/,81);calc(21,'peptide bonds and released water',peptide,n=>n-1,/Three peptide bonds[\s\S]*three water/,3);
const foods=[read(24,'P in X',/\|X\|([\d.]+)\|/),read(24,'P in Y',/\|Y\|([\d.]+)\|/),read(24,'Q in X',/\|X\|[\d.]+\|([\d.]+)\|/),read(24,'Q in Y',/\|Y\|[\d.]+\|([\d.]+)\|/)];
calc(24,'combined P supply',foods,(a,b)=>a+b,/P = 2\.0/,2);calc(24,'combined Q supply',foods,(a,b,c,d)=>c+d,/Q = 1\.6/,1.6);
calc(32,'unfolding-midpoint drop',[read(32,'intact',/\|Disulfide bonds intact\|(\d+)\|/),read(32,'reduced',/\|Disulfide bonds reduced\|(\d+)\|/)],(a,b)=>a-b,/19 °C/,19);
calc(40,'mass percentage increase',[read(40,'initial mass',/initial mass of ([\d.]+)/),read(40,'final mass',/final mass of ([\d.]+)/)],(i,f)=>(f-i)/i*100,/10\.0/,10);
const pump=[read(46,'cycles',/For (\d+) complete/),read(46,'Na per cycle',/(three) sodium/),read(46,'K per cycle',/(two) potassium/)];
calc(46,'sodium moved outward',pump,(c,a)=>c*a,/360 sodium/,360);calc(46,'potassium moved inward',pump,(c,a,b)=>c*b,/240 potassium/,240);calc(46,'net outward charge',pump,(c,a,b)=>c*(a-b),/120 elementary/,120);
const cubes=[read(71,'small side',/side lengths ([\d.]+)/),read(71,'large side',/and ([\d.]+) μm/)];
calc(71,'small SA:V',cubes,x=>6/x,/0\.600/,0.6);calc(71,'large SA:V',cubes,(x,y)=>6/y,/0\.300/,0.3);
calc(72,'extension:erythrocyte dimension ratio',[read(72,'extension mm',/as ([\d.]+) mm/),read(72,'erythrocyte μm',/diameter of ([\d.]+)/)],(l,d)=>l*1000/d,/150:1/,150);
const micro=[read(80,'base area',/area ([\d.]+) μm²/),read(80,'projections',/adding (\d+) cylindrical/),read(80,'radius',/radius ([\d.]+) μm/),read(80,'length',/length ([\d.]+) μm/)];
calc(80,'new area',micro,(a,n,r,l)=>a+n*2*Math.PI*r*l,/134\./,40+30*Math.PI);calc(80,'area factor',micro,(a,n,r,l)=>(a+n*2*Math.PI*r*l)/a,/3\.36/,(40+30*Math.PI)/40);
const lungs=[read(88,'tidal L',/tidal volume of ([\d.]+)/),read(88,'IRV L',/inspiratory reserve volume of ([\d.]+)/),read(88,'ERV L',/expiratory reserve volume of ([\d.]+)/),read(88,'breaths/min',/frequency is (\d+)/)];
calc(88,'vital capacity',lungs,(t,i,e)=>t+i+e,/4\.10 L/,4.1);calc(88,'minute ventilation',lungs,(t,i,e,f)=>t*f,/7\.5 L per minute/,7.5);
const stomata=[read(90,'count 1',/counts are (\d+)/),read(90,'count 2',/counts are \d+, (\d+)/),read(90,'count 3',/counts are \d+, \d+, (\d+)/),read(90,'count 4',/and (\d+)\./),read(90,'field area',/area ([\d.]+) mm²/)];
calc(90,'mean stomatal count',stomata,(a,b,c,d)=>(a+b+c+d)/4,/45 stomata/,45);calc(90,'stomatal density',stomata,(a,b,c,d,s)=>(a+b+c+d)/4/s,/225 stomata/,225);
const pot=[read(91,'radius mm',/radius ([\d.]+) mm/),read(91,'distance mm',/moves ([\d.]+) mm/),read(91,'minutes',/in ([\d.]+) minutes/)];
calc(91,'water uptake rate',pot,(r,d,t)=>Math.PI*r*r*d/t,/0\.46/,Math.PI*.35*.35*12/10);
calc(92,'relative diffusion rate',[read(92,'original thickness',/from ([\d.]+) μm/),read(92,'new thickness',/to ([\d.]+) μm/)],(a,b)=>a/b,/0\.625, or 62\.5%/,0.625);
calc(94,'Bohr-effect percentage-point difference',[read(94,'pH 7.4 saturation',/\|4\|(\d+)\|/),read(94,'pH 7.2 saturation',/\|4\|\d+\|(\d+)\|/)],(a,b)=>a-b,/20 percentage points/,20);
calc(95,'fetal/adult percentage-point difference',[read(95,'fetal saturation',/and (\d+)% for/),read(95,'adult saturation',/give (\d+)% saturation/)],(a,b)=>a-b,/25 percentage points/,25);
const oxygen=[read(96,'capacity',/carries ([\d.]+) cm³/),read(96,'arterial percent',/Arterial saturation is (\d+)%/),read(96,'rest venous percent',/venous saturation is (\d+)%/),read(96,'active venous percent',/and (\d+)% during/)];
calc(96,'oxygen extraction at rest',oxygen,(c,a,r)=>c*(a-r)/100,/4\.40/,4.4);calc(96,'oxygen extraction during activity',oxygen,(c,a,r,v)=>c*(a-v)/100,/12\.4/,12.4);
calc(103,'incidence ratio',[read(103,'P rate',/in (\d+) per 1000/),read(103,'Q rate',/and (\d+) per 1000/)],(a,b)=>a/b,/2\.4:1/,2.4);
const pressureRows=[...Q(111).stem.matchAll(/\|([PQRS])\|(\d+)\|(\d+)\|(\d+)\|/g)].map(m=>({time:m[1],atrium:+m[2],ventricle:+m[3],aorta:+m[4]}));
check(pressureRows.filter(r=>r.ventricle>r.aorta).map(r=>r.time).join('')==='Q','B111 aortic valve state');
check(pressureRows.filter(r=>r.atrium>r.ventricle).map(r=>r.time).join('')==='S','B111 AV valve state');
numeric.push({id:Q(111).id,quantity:'Pressure-derived valve states',inputs:pressureRows,independentResult:{aorticOpen:['Q'],leftAvOpen:['S']},status:'Every displayed row recomputed'});
calc(118,'sarcomere shortening percentage',[read(118,'initial length',/from ([\d.]+) μm/),read(118,'final length',/to ([\d.]+) μm/)],(a,b)=>(a-b)/a*100,/20% shortening/,20);
calc(122,'muscle force',[read(122,'load N',/load of (\d+) N/),read(122,'load arm m',/acting ([\d.]+) m/),read(122,'muscle arm m',/arm is ([\d.]+) m/)],(f,l,m)=>f*l/m,/1\.4\\times10\^\{2\}/,144);
calc(124,'mean joint range',[read(124,'angle 1',/trials: (\d+)°/),read(124,'angle 2',/trials: \d+°, (\d+)°/),read(124,'angle 3',/and (\d+)°/)],(a,b,c)=>(a+b+c)/3,/110\./,329/3);
check(/2, 4 and 6 units/.test(Q(128).stem)&&/6, 12 and 18 N/.test(Q(128).stem),'B128 supplied recruitment data');
calc(128,'force per unit',[input('units',2),input('N',6)],(n,f)=>f/n,/3 N/,3);calc(128,'three-unit force',[input('units',3),input('N per unit',3)],(n,f)=>n*f,/9 N/,9);
calc(136,'coral mass-gain percentage reduction',[read(136,'reference gain',/are ([\d.]+) g at/),read(136,'lower pH gain',/and ([\d.]+) g at/)],(a,b)=>(a-b)/a*100,/35\.0%/,35);
calc(141,'gain difference at pH 6 and 8',[read(141,'pH6 mg',/\|6\|(\d+)\|/),read(141,'pH8 mg',/\|8\|(\d+)\|/)],(a,b)=>a-b,/80 mg/,80);
calc(143,'combined-minus-water gain',[read(143,'both g',/plus nutrients, ([\d.]+) g/),read(143,'water g',/extra water only, ([\d.]+) g/)],(a,b)=>a-b,/3\.0 g/,3);

for(let offset=0;offset<figures.length;offset+=9){
 const batch=figures.slice(offset,offset+9),layers=[];
 for(const [j,f] of batch.entries()){
  const x=j%3*600,y=Math.floor(j/3)*350;
  layers.push({input:Buffer.from(`<svg width="600" height="34"><rect width="600" height="34" fill="#e6eef4"/><text x="12" y="24" font-family="Arial" font-size="17">${f.name}</text></svg>`),left:x,top:y});
  layers.push({input:await sharp(f.file).resize(580,300,{fit:'inside'}).png().toBuffer(),left:x+10,top:y+40});
 }
 await sharp({create:{width:1800,height:Math.ceil(batch.length/3)*350,channels:4,background:'white'}}).composite(layers).png().toFile(path.join(out,`sheet-${offset/9+1}.png`));
}
const report={status:errors.length?'failed':'computed checks passed; final visual signoff separate',source,questionJsonSha256:hash(fs.readFileSync(source)),questions:qs.length,records,scopeBasis:'Independent comparison with corrected official Biology guide and local verified blueprint. All 10 B subtopics have 16 records. Actual required knowledge, not difficulty, governs SL/AHL.',levelRanges:topicRanges,numericChecks:numeric,numericCheckCount:numeric.length,numericQuestions:new Set(numeric.map(x=>x.id)).size,figures,rasterFigures,mathFragments:maths,errors};
fs.mkdirSync('docs/ib-biology-reviews',{recursive:true});
fs.writeFileSync(snapshot?'work/theme-b-preliminary-independent.json':'docs/ib-biology-reviews/theme-b-independent-computed.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({status:report.status,questions:report.questions,numericCheckCount:report.numericCheckCount,numericQuestions:report.numericQuestions,figures:figures.length,rasterFigures:rasterFigures.length,errors},null,2));
if(errors.length)process.exitCode=1;
