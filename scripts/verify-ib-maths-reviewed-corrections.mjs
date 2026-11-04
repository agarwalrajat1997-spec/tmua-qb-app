import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import katex from 'katex';
import {hash,questionHash,validateReviewedCorrection,verifyMathsReviews} from './verify-ib-maths-reviews.mjs';

const manifest=JSON.parse(readFileSync('content/ib/maths-review-manifest.json','utf8'));
const correction=manifest.corrections.find(e=>e.course==='math-aa-hl'&&e.file==='calculus-2.json');assert.ok(correction);
const frozen=manifest.courses.find(e=>e.course===correction.course).files.find(e=>e.file===correction.file);
const path=`content/ib/${correction.course}/${correction.file}`,currentBytes=readFileSync(path),reviewBytes=readFileSync(correction.review);
const report=JSON.parse(reviewBytes),questions=JSON.parse(currentBytes),index=questions.findIndex(q=>q.id===report.questionId);assert.equal(report.questionId,'ib-aa-c2-056');
const pin=manifest.evidenceFiles.find(e=>e.file===correction.review);assert.ok(pin);
const base={course:correction.course,file:correction.file,baselineSha256:frozen.sha256,currentBytes,reviewBytes,evidenceSha256:pin.sha256};
validateReviewedCorrection(base);assert.equal(verifyMathsReviews().corrections,1);
const rejected=[];
function reject(name,change,{bank=false,repin=true}={}){
  const qs=structuredClone(questions),r=structuredClone(report),args={...base};change(qs,r,args);
  if(bank){args.currentBytes=Buffer.from(JSON.stringify(qs,null,2)+'\n');r.currentSha256=hash(args.currentBytes);r.updatedQuestionSha256=questionHash(qs[index]);}
  args.reviewBytes=Buffer.from(JSON.stringify(r,null,2)+'\n');if(repin)args.evidenceSha256=hash(args.reviewBytes);
  assert.throws(()=>validateReviewedCorrection(args),undefined,name);rejected.push(name);
}
reject('Another question changed',qs=>qs[0].stem+=' Unreviewed addition.',{bank:true});
reject('Corrected question stem changed',qs=>qs[index].stem+=' Unreviewed addition.',{bank:true});
reject('Extra marking step changed',qs=>qs[index].markScheme[0].steps[0].text+=' Unreviewed addition.',{bank:true});
reject('Marks changed',qs=>qs[index].parts[0].marks++,{bank:true});
reject('Question identity changed',qs=>qs[index].number++,{bank:true});
reject('Wrong frozen baseline',(_q,r)=>r.baselineSha256='0'.repeat(64));
reject('Wrong current hash',(_q,r)=>r.currentSha256='0'.repeat(64));
reject('Wrong original question hash',(_q,r)=>r.originalQuestionSha256='0'.repeat(64));
reject('Wrong updated question hash',(_q,r)=>r.updatedQuestionSha256='0'.repeat(64));
reject('Wrong before text',(_q,r)=>r.changes[0].before+=' ');
reject('Wrong after text',(_q,r)=>r.changes[0].after+=' ');
reject('Extra unreviewed change property',(_q,r)=>r.changes[0].field='stem');
reject('Duplicate text coordinate',(_q,r)=>r.changes.push({...r.changes[0]}));
reject('Out-of-range text coordinate',(_q,r)=>r.changes[0].step=999);
reject('No changes declared',(_q,r)=>r.changes=[]);
reject('Self review',(_q,r)=>r.reviewer=r.author);
reject('Review not passed',(_q,r)=>r.status='pending');
reject('Unresolved finding',(_q,r)=>r.openFindings=['Still unresolved']);
reject('No substantive review',(_q,r)=>r.reasoning='Passed');
reject('Missing numeric evidence',(_q,r)=>r.numericChecks=[]);
reject('Nonfinite numeric evidence',(_q,r)=>r.numericChecks[0].actual=Infinity);
reject('Contradictory numeric evidence',(_q,r)=>r.numericChecks[0].actual+=1);
reject('Unbounded tolerance',(_q,r)=>r.numericChecks[0].tolerance=1e99);
reject('Wrong course',(_q,r)=>r.course='math-ai-sl');
reject('Changed report without an updated evidence pin',(_q,r)=>r.reasoning+=' Altered.',{repin:false});
reject('Missing evidence pin',(_q,_r,args)=>args.evidenceSha256=undefined,{repin:false});

// Fresh numerical calculations use both geometries, not the displayed answer.
function simpson(f,a,b,n=16384){const h=(b-a)/n;let sum=f(a)+f(b);for(let i=1;i<n;i++)sum+=(i%2?4:2)*f(a+i*h);return sum*h/3;}
const expected=Math.PI*(4*Math.log(8)-161/32);
const disc=simpson(y=>Math.PI*(Math.exp(y)/4-2)**2,0,Math.log(8));
const shell=simpson(x=>2*Math.PI*(-x)*Math.log(4*x+8),-7/4,0);
assert.ok(expected>0&&Math.abs(disc-expected)<1e-11&&Math.abs(shell-expected)<1e-11);
assert.equal(BigInt(report.changes[0].before.match(/\d{40,}/)[0]),2n**384n,'Original giant log is exactly log(2^384)');
const final=questions[index].markScheme[1].steps[3].text;
assert.doesNotMatch(final,/\d{10,}/);const math=final.match(/^\$(.*)\$\.$/s);assert.ok(math);katex.renderToString(math[1],{throwOnError:true,strict:'ignore'});
assert.deepEqual(readFileSync(path),currentBytes,'Tests must not write bank bytes');assert.deepEqual(readFileSync(correction.review),reviewBytes,'Tests must not write review bytes');
console.log(JSON.stringify({status:'passed',rejectedCases:rejected.length,checks:rejected,discVolume:disc,shellVolume:shell,expectedVolume:expected,maths:'Exact2^384 identity; independent disc/shell quadrature; compact final expression renders with KaTeX',writes:0}));
