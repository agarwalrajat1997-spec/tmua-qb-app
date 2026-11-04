import assert from 'node:assert/strict';
import {mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import sharp from 'sharp';
import {readStage,readQuestions,questionHash,sha} from './psychology-media.mjs';
const directory=resolve(process.argv.slice(2).find(a=>!a.startsWith('--'))||'../psychology-bank-2026/media'),stage=readStage(directory);
const current=new Map(readQuestions({partial:process.argv.includes('--partial')}).map(({q})=>[q.id,q]));
const native=resolve(directory,'native'),mobile=resolve(directory,'mobile'),sheets=resolve(directory,'sheets');
const publishEvidence=process.argv.includes('--evidence'),evidenceDirectory='docs/ib-psychology-reviews/figures';
if(publishEvidence){assert.equal(stage.questions,240,'Final native evidence requires the full bank');assert.equal(current.size,240);mkdirSync(evidenceDirectory,{recursive:true});}
for(const p of [native,mobile,sheets])mkdirSync(p,{recursive:true});
const records=[];
for(const item of stage.objects){
  const bytes=readFileSync(resolve(directory,'assets',item.sha256+'.svg'));assert.equal(sha(bytes),item.sha256);
  const png=await sharp(bytes,{density:144}).flatten({background:'white'}).resize({width:1200}).png().toBuffer();
  const small=await sharp(png).resize({width:360}).png().toBuffer();
  if(publishEvidence){writeFileSync(resolve(evidenceDirectory,item.sha256+'-native.png'),png);writeFileSync(resolve(evidenceDirectory,item.sha256+'-mobile.png'),small);}
  for(const use of item.uses){
    const q=current.get(use.questionId);assert.ok(q);assert.equal(use.questionSha256,questionHash(q),'Canonical changed after staging; stage again');
    const name=`${use.questionId}-${use.role}.png`,nativePath=resolve(native,name),mobilePath=resolve(mobile,name);
    writeFileSync(nativePath,png);writeFileSync(mobilePath,small);
    records.push({...use,svgSha256:item.sha256,nativePngSha256:sha(png),nativePngPath:publishEvidence?`${evidenceDirectory}/${item.sha256}-native.png`:nativePath,mobilePngSha256:sha(small),mobilePngPath:publishEvidence?`${evidenceDirectory}/${item.sha256}-mobile.png`:mobilePath});
  }
}
records.sort((a,b)=>a.questionId.localeCompare(b.questionId)||a.role.localeCompare(b.role));
const escape=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
for(let start=0;start<records.length;start+=12){
  const subset=records.slice(start,start+12),inputs=[];
  for(let i=0;i<subset.length;i++){
    const record=subset[i],x=i%3*700,y=Math.floor(i/3)*450;
    const thumb=await sharp(record.nativePngPath).resize({width:670,height:390,fit:'contain',background:'white'}).png().toBuffer();
    const label=Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="700" height="45"><rect width="700" height="45" fill="#fff3ce"/><text x="12" y="18" font-family="Arial" font-size="13">${escape(record.questionId+' · '+record.role)}</text><text x="12" y="36" font-family="Arial" font-size="11">${escape(record.title.slice(0,90))}</text></svg>`);
    inputs.push({input:label,left:x,top:y},{input:thumb,left:x+15,top:y+50});
  }
  await sharp({create:{width:2100,height:1800,channels:3,background:'#eee'}}).composite(inputs).png().toFile(resolve(sheets,`sheet-${String(start/12+1).padStart(2,'0')}.png`));
}
const evidence={schemaVersion:1,status:'rendered; visual review required',figures:records.length,uniqueAssets:stage.objects.length,records};
writeFileSync(resolve(directory,'native-diagram-index.json'),JSON.stringify(evidence,null,2)+'\n');
if(publishEvidence)writeFileSync('docs/ib-psychology-reviews/native-diagram-index.json',JSON.stringify(evidence,null,2)+'\n');
console.log(JSON.stringify({status:'rendered',figures:records.length,native,mobile,sheets,visualReview:'required; no automatic pass assigned'}));
