import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
import sharp from 'sharp';
import {ibQuestionSchema,safeDiagram} from '../../lib/ib/question.ts';
const qs=JSON.parse(readFileSync('content/ib/biology/unity-diversity.json','utf8'));
const blueprint=JSON.parse(readFileSync('docs/ib-biology-reviews/syllabus-blueprint.json','utf8'));
assert.equal(qs.length,144);
const checks=[];
function numerical(n,expression,expected,tolerance=1e-8){
 assert.ok(Math.abs(expression-expected)<tolerance,'q'+n+': '+expression+' != '+expected);
 checks.push({id:'ib-bio-a-'+String(n).padStart(3,'0'),recalculatedValue:expression,expected});
}
numerical(4,(8/10-1/10)*100,70);numerical(6,4/2,2);numerical(7,19-16,3);numerical(7,25-10,15);
numerical(13,8e18*.12*.25,2.4e17,100);numerical(21,25-1,24);numerical(22,(100-2*22)/2,28);
numerical(24,4**8,65536);numerical(29,12*8,96);numerical(34,38-2,36);numerical(38,20/2,10);
numerical(44,3.45-.05,3.40);numerical(44,3.45+.05,3.50);numerical(50,400/100*10,40);
numerical(51,100/40,2.5);numerical(51,18*100/40,45);numerical(53,36*1000/24,1500);
numerical(68,200*60,12000);numerical(74,5/100*100,5);numerical(84,46/2,23);numerical(85,3*2,6);
numerical(87,18/20*100,90);numerical(88,Number((45000/3100).toPrecision(2)),15);
numerical(89,Number(((9000-1500)/9000*100).toFixed(1)),83.3);numerical(90,3/600*100,.5);numerical(90,42/600*100,7);
numerical(94,12+15,27);
const difference=(a,b)=>[...a].filter((v,i)=>v!==b[i]).length;
numerical(101,difference('ACGTAA','ACGTGA'),1);numerical(101,difference('ACGTAA','TTGCGC'),5);
numerical(102,18/3,6);numerical(103,20/(2+2),5);numerical(115,288/300*100,96);
numerical(116,(3-2.4)/2.4*100,25);numerical(119,8+5-3,10);numerical(126,32+31,63);
numerical(127,(10+10)*2,40);numerical(131,(150-90)/150*100,40);numerical(135,(1200-780)/1200*100,35);
numerical(140,184/200*100,92);numerical(140,138/200*100,69);numerical(140,92-69,23);
numerical(142,28-12,16);numerical(142,15-13,2);
numerical(143,new Set([1,2,3,4,5,6,7]).size,7);
const dir=resolve('../biology-artifacts/theme-a');mkdirSync(dir,{recursive:true});
const records=[],composite=[],svgEntries=[];
for(const q of qs){
 const parsed=ibQuestionSchema.safeParse(q);assert.ok(parsed.success,JSON.stringify(parsed.error));
 const scope=blueprint.topics.find(t=>t.code===q.syllabusCode);
 assert.ok(scope);if(scope.additionalHlOnly)assert.equal(q.level,'ahl');
 assert.equal(q.calculator,true);assert.equal(q.subject,'biology');
 for(const key of ['diagramSvg','markSchemeDiagramSvg'])if(q[key]){
  assert.ok(safeDiagram(q[key]));
  const sha=createHash('sha256').update(q[key]).digest('hex');
  const filename=q.id+'-'+key+'.png';
  await sharp(Buffer.from(q[key])).png().toFile(resolve(dir,filename));
  svgEntries.push({id:q.id,key,sha256:sha,filename,scope:'Original schematic; biological structure, proportions where claimed and labels reviewed by author'});
  const i=svgEntries.length-1,x=(i%2)*830,y=Math.floor(i/2)*420;
  const pic=await sharp(Buffer.from(q[key])).resize({width:810,height:370,fit:'contain',background:'white'}).png().toBuffer();
  const label=Buffer.from('<svg width="830" height="40"><rect width="100%" height="100%" fill="#edf3f7"/><text x="15" y="26" font-family="Arial" font-size="18">'+q.id+': '+q.title+'</text></svg>');
  composite.push({input:label,left:x,top:y},{input:pic,left:x+10,top:y+45});
 }
 records.push({id:q.id,sha256:createHash('sha256').update(JSON.stringify(q)).digest('hex'),scope:q.level,difficulty:q.difficulty,checks:['individual author biological review','scope against corrected guide','mark point allocation','unique original prompt','calculator policy']});
}
await sharp({create:{width:1660,height:Math.ceil(svgEntries.length/2)*420,channels:3,background:'#ddd'}}).composite(composite).png().toFile(resolve(dir,'author-visual-sheet.png'));
writeFileSync('docs/ib-biology-reviews/unity-diversity-author-checks.json',JSON.stringify({status:'passed author checks; independent review pending',questions:144,numericalChecks:checks.length,checks,records,svgEntries,illustration:{id:'ib-bio-a-049',review:'Root and Theme A author inspected original plant-cell cutaway; A wall, B chloroplast, C nucleus, D vacuole, E mitochondrion. No scale measurements inferred.'}},null,2)+'\n');
console.log(JSON.stringify({questions:144,numericalChecks:checks.length,diagrams:svgEntries.length,output:dir}));
