import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,readdirSync} from 'node:fs';
import {resolve,relative,dirname} from 'node:path';
import {createHash} from 'node:crypto';

const rawHash=bytes=>createHash('sha256').update(bytes).digest('hex');
const hash=bytes=>rawHash(Buffer.from(bytes.toString('utf8').replace(/\r\n/g,'\n')));
const root=process.cwd(),workspace=dirname(root);
function portable(value){
 if(typeof value==='string')return value.startsWith(workspace+'\\')||value.startsWith(workspace+'/')?relative(root,value).replaceAll('\\','/'):value;
 if(Array.isArray(value))return value.map(portable);
 if(value&&typeof value==='object')return Object.fromEntries(Object.entries(value).map(([key,v])=>[key,portable(v)]));
 return value;
}
// Render artifact locations are local evidence, not user-specific repository metadata.
for(const name of readdirSync('docs/ib-biology-reviews').filter(n=>n.endsWith('.json'))){
 const path=resolve('docs/ib-biology-reviews',name);
 const original=readFileSync(path,'utf8'),updated=JSON.stringify(portable(JSON.parse(original)),null,2)+'\n';
 if(updated!==original)writeFileSync(path,updated);
}
const files=['unity-diversity','form-function','interaction-interdependence','continuity-change'];
const themes=files.map((name,i)=>{
 const file=name+'.json',bytes=readFileSync('content/ib/biology/'+file),sha256=hash(bytes);
 const review=`docs/ib-biology-reviews/theme-${'abcd'[i]}-independent-review.json`;
 let reportBytes=readFileSync(review);const report=JSON.parse(reportBytes);
 assert.equal(report.status,'passed',review);
 assert.ok(reportBytes.toString('utf8').includes(rawHash(bytes))||report.canonicalQuestionJsonSha256===sha256,review+': current file not independently signed off');
 report.canonicalQuestionJsonSha256=sha256;
 report.hashNormalization='LF line endings; original reviewed file hash retained above.';
 writeFileSync(review,JSON.stringify(report,null,2)+'\n');reportBytes=readFileSync(review);
 return {file,questions:JSON.parse(bytes).length,sha256,reviewedFileSha256:rawHash(bytes),review,reviewSha256:hash(reportBytes)};
});
const supplement='docs/ib-biology-reviews/theme-d-additions-independent-review.json';
let supplementalBytes=readFileSync(supplement);const supplementalReport=JSON.parse(supplementalBytes);
assert.equal(supplementalReport.status,'passed');
assert.ok(supplementalBytes.toString('utf8').includes(themes[3].reviewedFileSha256)||supplementalReport.canonicalQuestionJsonSha256===themes[3].sha256);
supplementalReport.canonicalQuestionJsonSha256=themes[3].sha256;
supplementalReport.hashNormalization='LF line endings; original reviewed file hash retained above.';
writeFileSync(supplement,JSON.stringify(supplementalReport,null,2)+'\n');supplementalBytes=readFileSync(supplement);
const media=readFileSync('content/ib/biology-diagram-manifest.json');
const manifest={schemaVersion:1,hashNormalization:'UTF-8 JSON with LF line endings',reviewedOn:'2026-10-30',questions:themes.reduce((n,t)=>n+t.questions,0),themes,
 visualAssets:Object.keys(JSON.parse(media).assets).length,mediaManifestSha256:hash(media),
 supplementalReview:{file:supplement,sha256:hash(supplementalBytes)},
 syllabus:'Biology first assessment2025; official guide corrected March2024 and linked by2027 examiner instructions',
 sources:[
  {url:'https://xmltwo.ibo.org/publications/EAD/2026_EN/GR4/GR4-Biology_EN.pdf',purpose:'Scope, course boundaries, command terms and assessment structure'},
  {url:'https://ibo.org/globalassets/new-structure/university-admission/pdfs/subject-guides-documents/sl-sample-exam-paper-1b--biology.pdf',purpose:'Exam-format and question-style calibration; no paper text or images reproduced'}
 ],
 referenceBankAccess:'Both supplied Biology reference links returned Cloudflare1033. No source-bank questions or images were copied.',
 originality:'Independent question wording, constructed practice datasets, self-drawn vector figures and two original AI-assisted schematics. Reported empirical results are explicitly cited.',
 reviewLimit:'Agent authoring and independent agent reviews; no claim of IB endorsement or external human examiner approval.'};
assert.equal(manifest.questions,640);
writeFileSync('content/ib/biology-review-manifest.json',JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify({status:'review-bound',questions:manifest.questions,visualAssets:manifest.visualAssets}));
