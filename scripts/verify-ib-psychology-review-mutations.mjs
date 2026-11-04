import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,existsSync,unlinkSync} from 'node:fs';
import {join,dirname,resolve} from 'node:path';
import {sha} from './psychology-media.mjs';
import {ROOT,DOCS,MANIFEST,validateNumericAssertion,readReviewEvidence,protectedFilePaths,verifyReviewManifest,EXPECTED_MUTATION_CASES,validateMutationProof,mutationCodeBindings} from './verify-ib-psychology-reviews.mjs';
import {finalizeReviewManifest} from './finalize-ib-psychology-reviews.mjs';

const unitOnly=process.argv.includes('--unit-only');assert.ok(process.argv.slice(2).every(a=>a==='--unit-only'));
const executedCodeBindings=mutationCodeBindings(ROOT);
const good={name:'Recomputed mean difference',actual:3,expected:3,tolerance:1e-9,reason:'Independent subtraction of the supplied group means.'};
validateNumericAssertion(good,'fixture');let unitCases=0;
for(const edit of [c=>c.actual=4,c=>c.actual=Infinity,c=>c.expected=NaN,c=>c.tolerance=-1,c=>c.tolerance=100,c=>c.actual=true,c=>c.reason='',c=>c.passed=false]){const c=structuredClone(good);edit(c);assert.throws(()=>validateNumericAssertion(c,'bad fixture'));unitCases++;}
if(unitOnly){console.log(JSON.stringify({status:'passed',unitCases,scope:'Finite values, recomputed equality, bounded tolerances, substantive reasons and failed-assertion rejection; full evidence mutation tests remain pending.'}));process.exit(0);}

// Only scientifically complete real evidence is copied. All mutations and any
// temporary manifest writes are confined to this disposable workspace fixture.
const evidence=readReviewEvidence({root:ROOT}),sourcePaths=protectedFilePaths(ROOT),originals=new Map(sourcePaths.map(p=>[p,readFileSync(join(ROOT,p))]));
const parent=resolve(ROOT,'../psychology-bank-2026/review-guard-fixtures');mkdirSync(parent,{recursive:true});const copy=mkdtempSync(join(parent,'isolated-'));
for(const [p,b]of originals){mkdirSync(dirname(join(copy,p)),{recursive:true});writeFileSync(join(copy,p),b);}
// A format-valid positive control breaks the proof bootstrap cycle only in the
// disposable copy. It is explicitly synthetic and is never a live execution claim.
const reportPath=`${DOCS}/review-guard-mutation-checks.json`;
const synthetic={status:'passed',unitCases:8,mutationCases:EXPECTED_MUTATION_CASES.length,cases:EXPECTED_MUTATION_CASES,semanticMutationCases:27,codeBindings:mutationCodeBindings(copy),scope:'Synthetic mutation-proof positive control confined to an isolated fixture; not a real test-execution claim.'};
const syntheticBytes=Buffer.from(JSON.stringify(synthetic,null,2)+'\n');writeFileSync(join(copy,reportPath),syntheticBytes);
const fixtureOriginals=new Map(originals);fixtureOriginals.set(reportPath,syntheticBytes);const paths=[...fixtureOriginals.keys()].sort();
const proof={schemaVersion:1,status:'passed',hashAlgorithm:'sha256',scope:'Validated real science evidence with a synthetic mutation-proof positive control in an isolated negative-test copy',...evidence,files:paths.map(p=>({file:p,bytes:fixtureOriginals.get(p).length,sha256:sha(fixtureOriginals.get(p))}))};
const frozen=Buffer.from(JSON.stringify(proof,null,2)+'\n');mkdirSync(dirname(join(copy,MANIFEST)),{recursive:true});writeFileSync(join(copy,MANIFEST),frozen);
verifyReviewManifest(copy);
const cases=[],semanticCases=[];
function restore(){for(const [p,b]of fixtureOriginals)writeFileSync(join(copy,p),b);writeFileSync(join(copy,MANIFEST),frozen);}
function changeJson(p,edit){const d=JSON.parse(readFileSync(join(copy,p),'utf8'));edit(d);writeFileSync(join(copy,p),JSON.stringify(d,null,2)+'\n');}
function reject(name,edit,{finalizer=false,semantic=true}={}){restore();edit();if(semantic){assert.throws(()=>readReviewEvidence({root:copy}),undefined,name+' must fail its evidence checks, independently of frozen bytes');semanticCases.push(name);}assert.throws(()=>finalizer?finalizeReviewManifest(copy):verifyReviewManifest(copy),undefined,name);assert.deepEqual(readFileSync(join(copy,MANIFEST)),frozen,'A failed check must not rebaseline the fixture');cases.push(name);}
const independent=`${DOCS}/approaches-independent.json`,quantitative=`${DOCS}/methods-technology-independent.json`;
reject('Missing independently reviewed question',()=>changeJson(independent,d=>d.records.pop()));
reject('Duplicate independent question',()=>changeJson(independent,d=>d.records[1]=d.records[0]));
reject('Stale canonical question hash',()=>changeJson(independent,d=>d.records[0].questionSha256='0'.repeat(64)));
reject('Author approving own question',()=>changeJson(independent,d=>{d.reviewer='mock_exam_spec';d.records[0].reviewer='mock_exam_spec';}));
reject('Full prompt and scheme were not read',()=>changeJson(independent,d=>d.records[0].fullQuestionAndSchemeRead=false));
reject('Canned independent reasoning',()=>changeJson(independent,d=>d.records[0].reasoning='Checked and passed.'));
reject('Copied independent reasoning',()=>changeJson(independent,d=>d.records[1].reasoning=d.records[0].reasoning));
reject('Unresolved independent finding',()=>changeJson(independent,d=>d.records[0].openFindings=['Unresolved question']));
reject('Incorrect assessment scope',()=>changeJson(independent,d=>d.records[0].assessment.scopeChecked=false));
reject('Incorrect section allocation',()=>changeJson(independent,d=>d.records[0].assessment.marks++));
reject('Contradictory independent calculation',()=>changeJson(quantitative,d=>{const c=d.records.find(r=>r.numericChecks.length).numericChecks[0];c.actual=c.expected+Math.max(1,Math.abs(c.expected));}));
reject('Unbounded numeric tolerance',()=>changeJson(quantitative,d=>{d.records.find(r=>r.numericChecks.length).numericChecks[0].tolerance=1e99;}));
reject('Non-finite calculation represented as null',()=>changeJson(quantitative,d=>d.records.find(r=>r.numericChecks.length).numericChecks[0].actual=null));
reject('Quantitative P3 item lacks recomputation',()=>changeJson(quantitative,d=>{d.records.find(r=>['p3-graph','p3-data'].includes(r.assessment.examSection)).numericChecks=[];}));
reject('Missing native diagram inspection',()=>changeJson(independent,d=>delete d.records.find(r=>r.figureReview).figureReview));
reject('Mobile figure is not legible',()=>changeJson(independent,d=>d.records.find(r=>r.figureReview).figureReview.legible=false));
const native=JSON.parse(readFileSync(join(copy,DOCS,'native-diagram-index.json'),'utf8')).records[0];
reject('Changed inspected native PNG',()=>writeFileSync(join(copy,native.nativePngPath),Buffer.from('changed native PNG')));
reject('Changed inspected mobile PNG',()=>writeFileSync(join(copy,native.mobilePngPath),Buffer.from('changed mobile PNG')));
reject('Unverified CDN object',()=>changeJson('content/ib/psychology-diagram-manifest.json',d=>delete d.assets[Object.keys(d.assets)[0]]));
reject('Contradictory actual public-byte proof',()=>changeJson(`${DOCS}/cdn-checks.json`,d=>d.records[0].publicSha256='0'.repeat(64)));
reject('Current stem changed after review',()=>changeJson('content/ib/psychology/biological-approach.json',d=>d[0].stem+=' Altered after review.'));
reject('Wrong course cohort',()=>changeJson('content/ib/psychology/biological-approach.json',d=>d[0].firstAssessment=2026));
reject('Holistic bands have a score gap',()=>changeJson('content/ib/psychology/biological-approach.json',d=>d[0].markScheme[0].rubric.bands[0].min=1));
reject('Contiguous rubric uses incorrect band boundaries',()=>changeJson('content/ib/psychology/biological-approach.json',d=>d[0].markScheme[0].rubric.bands=[{min:0,max:0,descriptor:'No answer'},{min:1,max:4,descriptor:'Incorrect contiguous score range'}]));
reject('Shared item relabelled HL',()=>changeJson('content/ib/psychology/biological-approach.json',d=>d[0].level='ahl'));
reject('Protected author source bytes changed',()=>writeFileSync(join(copy,'scripts/ib-psychology-authoring/methods_evaluation.py'),Buffer.from('changed author source')),{semantic:false});
reject('Finalizer refuses silent rebaseline',()=>changeJson('content/ib/psychology/biological-approach.json',d=>d[0].title+=' changed'),{finalizer:true});
restore();unlinkSync(join(copy,MANIFEST));changeJson(independent,d=>d.status='pending');assert.throws(()=>readReviewEvidence({root:copy}));assert.throws(()=>finalizeReviewManifest(copy));assert.equal(existsSync(join(copy,MANIFEST)),false);cases.push('Incomplete evidence cannot create a frozen manifest');semanticCases.push('Incomplete evidence cannot create a frozen manifest');restore();
restore();unlinkSync(join(copy,MANIFEST));writeFileSync(join(copy,reportPath),JSON.stringify({status:'passed',unitCases:8,mutationCases:25}));assert.throws(()=>finalizeReviewManifest(copy));assert.equal(existsSync(join(copy,MANIFEST)),false);cases.push('Canned mutation counters are not sufficient proof');restore();
const stale=structuredClone(synthetic);stale.codeBindings[0].sha256='0'.repeat(64);unlinkSync(join(copy,MANIFEST));writeFileSync(join(copy,reportPath),JSON.stringify(stale));assert.throws(()=>finalizeReviewManifest(copy));assert.equal(existsSync(join(copy,MANIFEST)),false);cases.push('Stale guard code hashes invalidate mutation proof');restore();

// Ordinary verification must be read-only, including all protected evidence bytes.
const before=new Map(paths.map(p=>[p,sha(readFileSync(join(copy,p)))]));verifyReviewManifest(copy);
for(const [p,hash]of before)assert.equal(sha(readFileSync(join(copy,p))),hash,'Verification wrote to '+p);cases.push('Read-only verification preserves every protected byte');
assert.deepEqual(cases,EXPECTED_MUTATION_CASES);
assert.deepEqual(mutationCodeBindings(ROOT),executedCodeBindings,'Critical checking code changed during the test run');
const report={status:'passed',unitCases,mutationCases:cases.length,cases,semanticMutationCases:semanticCases.length,codeBindings:executedCodeBindings,scope:'Real complete science evidence copied into an isolated local fixture, with an explicitly synthetic mutation-proof positive control confined to that copy. Semantic cases rejected by readReviewEvidence before the frozen-byte check; protected-source bytes classified as hash-only. This real execution proof is written only after every test passes. No production, canonical source, review or media bytes were mutated. No live emails or database writes.'};
validateMutationProof(ROOT,report);
const target=join(ROOT,DOCS,'review-guard-mutation-checks.json'),bytes=JSON.stringify(report,null,2)+'\n';
if(existsSync(join(ROOT,MANIFEST)))assert.equal(readFileSync(target,'utf8'),bytes,'Frozen mutation evidence must remain unchanged');else writeFileSync(target,bytes);
console.log(JSON.stringify({status:'passed',unitCases,mutationCases:cases.length,isolatedCopy:copy}));
