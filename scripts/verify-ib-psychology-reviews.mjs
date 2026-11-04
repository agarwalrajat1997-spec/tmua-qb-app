import assert from 'node:assert/strict';
import {lstatSync,readFileSync,readdirSync} from 'node:fs';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {ibHarness} from './ib-component-harness.mjs';
import {sha,questionHash,ORIGIN,PREFIX} from './psychology-media.mjs';

export const ROOT=resolve(dirname(fileURLToPath(import.meta.url)),'..');
export const DOCS='docs/ib-psychology-reviews';
export const MANIFEST='content/ib/psychology-review-manifest.json';
export const MUTATION_CODE_FILES=['scripts/verify-ib-psychology-reviews.mjs','scripts/finalize-ib-psychology-reviews.mjs','scripts/verify-ib-psychology-review-mutations.mjs','scripts/ib-component-harness.mjs','scripts/psychology-media.mjs'];
export const EXPECTED_MUTATION_CASES=[
  "Missing independently reviewed question",
  "Duplicate independent question",
  "Stale canonical question hash",
  "Author approving own question",
  "Full prompt and scheme were not read",
  "Canned independent reasoning",
  "Copied independent reasoning",
  "Unresolved independent finding",
  "Incorrect assessment scope",
  "Incorrect section allocation",
  "Contradictory independent calculation",
  "Unbounded numeric tolerance",
  "Non-finite calculation represented as null",
  "Quantitative P3 item lacks recomputation",
  "Missing native diagram inspection",
  "Mobile figure is not legible",
  "Changed inspected native PNG",
  "Changed inspected mobile PNG",
  "Unverified CDN object",
  "Contradictory actual public-byte proof",
  "Current stem changed after review",
  "Wrong course cohort",
  "Holistic bands have a score gap",
  "Contiguous rubric uses incorrect band boundaries",
  "Shared item relabelled HL",
  "Protected author source bytes changed",
  "Finalizer refuses silent rebaseline",
  "Incomplete evidence cannot create a frozen manifest",
  "Canned mutation counters are not sufficient proof",
  "Stale guard code hashes invalidate mutation proof",
  "Read-only verification preserves every protected byte"
];
const BAND_RANGES={3:[[0,0],[1,1],[2,2],[3,3]],4:[[0,0],[1,2],[3,4]],6:[[0,0],[1,2],[3,4],[5,6]],15:[[0,0],[1,3],[4,6],[7,9],[10,12],[13,15]]};
const TOPICS=[['biological-approach','bio',40],['cognitive-approach','cog',40],['sociocultural-approach','soc',40],['research-methodology','res',60],['culture','cul',20],['motivation','mot',20],['technology','tec',20]];
const idsFor=tokens=>TOPICS.filter(([,token])=>tokens.includes(token)).flatMap(([,token,n])=>Array.from({length:n},(_,i)=>`ib-psy-${token}-${String(i+1).padStart(3,'0')}`));
const AUTHORS=[['approaches-author.json',['bio','cog']],['social-extensions-author.json',['soc','cul','mot']],['methods-author.json',['res']],['technology-author.json',['tec']]];
const INDEPENDENT=[['approaches-independent.json',['bio','cog'],'mock_pdf_inventory'],['social-extensions-independent.json',['soc','cul','mot'],'root'],['methods-technology-independent.json',['res','tec'],'mock_exam_spec']];
const plainPath=p=>{assert.ok(typeof p==='string'&&/^[A-Za-z0-9_.\/-]+$/.test(p)&&!p.startsWith('/')&&!p.split('/').includes('..')&&!p.includes('//'),`Unsafe evidence path ${p}`);return p;};
const read=(root,p)=>{plainPath(p);const file=join(root,p);assert.ok(lstatSync(file).isFile(),`${p}: regular file required`);return readFileSync(file);};
const json=(root,p)=>JSON.parse(read(root,p).toString('utf8'));
const noFindings=(value,label)=>assert.deepEqual(value,[],`${label}: unresolved findings`);
const identity=value=>{assert.equal(typeof value,'string');return value.replace(/^\/root\//,'').replace(/^\/root$/,'root');};
const meaningful=(value,label,min=30)=>{assert.ok(typeof value==='string'&&value.trim().length>=min,`${label}: specific substantive evidence required`);assert.ok(!/^(?:pass(?:ed)?|reviewed|checked|verified|all good|no issues)[.\s!]*$/i.test(value),`${label}: canned evidence`);};
function exactIds(records,expected,label){assert.ok(Array.isArray(records),`${label}: record array required`);const ids=records.map(r=>r.questionId);assert.equal(new Set(ids).size,ids.length,`${label}: duplicate records`);assert.deepEqual([...ids].sort(),[...expected].sort(),`${label}: missing/unexpected question records`);return new Map(records.map(r=>[r.questionId,r]));}
function authorOf(id){if(/^ib-psy-(bio|cog)-/.test(id))return 'mock_exam_spec';if(/^ib-psy-(soc|cul|mot)-/.test(id))return 'mock_pdf_inventory';if(/^ib-psy-res-0(?:49|5\d|60)$/.test(id))return 'mock_portal_audit';return 'root';}

export function validateNumericAssertion(check,label,{requireReason=true}={}){
  meaningful(check.name,`${label} name`,3);if(requireReason)meaningful(check.reason,`${label} reason`,12);
  for(const key of ['actual','expected','tolerance'])assert.ok(typeof check[key]==='number'&&Number.isFinite(check[key]),`${label}: finite numeric ${key} required`);
  assert.ok(check.tolerance>=0&&check.tolerance<=Math.max(1e-7,Math.abs(check.expected)*.005),`${label}: tolerance can conceal an error`);
  assert.ok(Math.abs(check.actual-check.expected)<=check.tolerance,`${label}: contradictory calculation`);
  if(Object.hasOwn(check,'passed'))assert.equal(check.passed,true);
  if(Object.hasOwn(check,'status'))assert.equal(check.status,'passed');
}
function numericChecks(record,q,label,options){
  assert.ok(Array.isArray(record.numericChecks),`${label}: numeric-check array required`);
  assert.equal(new Set(record.numericChecks.map(c=>c.name)).size,record.numericChecks.length,`${label}: duplicate calculation names`);
  record.numericChecks.forEach((c,i)=>validateNumericAssertion(c,`${label} calculation ${i+1}`,options));
  if(['p3-graph','p3-data'].includes(q.examSection))assert.ok(record.numericChecks.length,`${label}: quantitative item requires a recomputation`);
}
function fileBindings(report,expectedFiles,bindings,label){
  const rows=report.files??report.collections;assert.ok(Array.isArray(rows),`${label}: file bindings required`);
  assert.deepEqual(rows.map(r=>r.file).sort(),[...expectedFiles].sort(),`${label}: file coverage differs`);
  for(const row of rows){assert.equal(row.sha256,bindings.get(row.file).sha256,`${label}: stale canonical file hash`);if(row.questions!==undefined)assert.equal(row.questions,bindings.get(row.file).questions);}
}
function png(root,path,hash,width,label){
  assert.ok(path.startsWith(`${DOCS}/figures/`),`${label}: portable figure evidence path required`);
  const bytes=read(root,path);assert.equal(sha(bytes),hash,`${label}: inspected PNG changed`);
  assert.equal(bytes.subarray(0,8).toString('hex'),'89504e470d0a1a0a',`${label}: PNG required`);assert.equal(bytes.readUInt32BE(16),width,`${label}: wrong inspected image width`);
}

/** Read-only evidence validation. No badges, hashes or review records are created. */
export function readReviewEvidence({root=ROOT}={}){
  const h=ibHarness(),model=h.model,catalog=h.load('lib/ib/catalog.ts'),psych=h.load('lib/ib/psychology-catalog.ts');
  const questions=new Map(),bindings=new Map(),sections=new Map(),stemHashes=new Set();
  for(const [topic,token,count]of TOPICS){
    const file=`content/ib/psychology/${topic}.json`,raw=read(root,file),qs=JSON.parse(raw);
    assert.ok(Array.isArray(qs));assert.equal(qs.length,count,file);
    assert.deepEqual(qs.map(q=>q.number),Array.from({length:count},(_,i)=>i+1),`${file}: local numbering`);
    for(const q of qs){
      model.ibQuestionSchema.parse(q);assert.equal(q.status,'published');assert.equal(q.topicId,topic);assert.equal(q.id,`ib-psy-${token}-${String(q.number).padStart(3,'0')}`);
      assert.deepEqual(q.markScheme[0].rubric.bands.map(b=>[b.min,b.max]),BAND_RANGES[q.marks],`${q.id}: actual assessment band boundaries required`);
      assert.ok(!questions.has(q.id));questions.set(q.id,q);sections.set(q.examSection,(sections.get(q.examSection)??0)+1);
      const stem=sha(q.stem.toLowerCase().replace(/\s+/g,' ').trim());assert.ok(!stemHashes.has(stem),`${q.id}: duplicate stem`);stemHashes.add(stem);
      assert.ok(!q.markSchemeDiagramSvg&&!q.markSchemeDiagramUrl,'This release reviews stimulus figures through figureReview, not unreviewed separate solution figures');
      for(const privateKey of ['source','verification','markScheme','answerSummary','markSchemeDiagramSvg','markSchemeDiagramUrl'])assert.ok(!(privateKey in model.questionPrompt(q)),`${q.id}: prompt leaks ${privateKey}`);
    }
    bindings.set(file,{file,sha256:sha(raw),questions:qs.length});
  }
  assert.equal(questions.size,240);assert.equal([...questions.values()].filter(q=>q.level==='sl').length,180);assert.equal([...questions.values()].filter(q=>q.level==='ahl').length,60);
  assert.deepEqual([...sections.keys()].sort(),Object.keys(psych.PSYCHOLOGY_SECTIONS).sort(),'All twelve assessment styles required');
  assert.equal(catalog.ibTopicsForCourse('psychology','sl').length,4);assert.equal(catalog.ibTopicsForCourse('psychology','hl').length,7);
  const figures=[...questions.values()].filter(q=>q.diagramSvg);assert.ok(figures.length>=120,'The image-led release needs useful figures in at least half the questions');
  const media=json(root,'content/ib/psychology-diagram-manifest.json');assert.equal(media.schemaVersion,1);assert.equal(media.origin,ORIGIN);
  const figureHashes=new Set(figures.map(q=>sha(q.diagramSvg)));assert.deepEqual(Object.keys(media.assets).sort(),[...figureHashes].sort(),'CDN manifest must match current stimulus SVGs exactly');
  for(const q of figures){const hash=sha(q.diagramSvg),entry=media.assets[hash];assert.equal(entry.key,PREFIX+hash+'.svg');assert.equal(entry.bytes,Buffer.byteLength(q.diagramSvg));assert.equal(entry.contentType,'image/svg+xml');assert.equal(q.diagramUrl,ORIGIN+'/'+entry.key,`${q.id}: verified diagram URL required`);}
  const cdn=json(root,`${DOCS}/cdn-checks.json`);assert.equal(cdn.status,'passed');assert.equal(cdn.origin,ORIGIN);assert.equal(cdn.objects,figureHashes.size);assert.deepEqual(cdn.records.map(r=>r.sha256).sort(),[...figureHashes].sort(),'Actual CDN proof must cover every distinct figure exactly once');
  for(const r of cdn.records){assert.equal(r.status,200);assert.equal(r.publicSha256,r.sha256);assert.equal(r.contentType,'image/svg+xml');assert.equal(r.bytes,media.assets[r.sha256].bytes);assert.equal(r.url,ORIGIN+'/'+PREFIX+r.sha256+'.svg');}
  const native=json(root,`${DOCS}/native-diagram-index.json`);assert.equal(native.schemaVersion,1);assert.equal(native.figures,figures.length);assert.equal(native.uniqueAssets,figureHashes.size);
  const nativeMap=exactIds(native.records,figures.map(q=>q.id),'native figure index');
  for(const q of figures){const r=nativeMap.get(q.id);assert.equal(r.role,'question');assert.equal(r.questionSha256,questionHash(q),`${q.id}: native index predates canonical content`);assert.equal(r.svgSha256,sha(q.diagramSvg));png(root,r.nativePngPath,r.nativePngSha256,1200,q.id);png(root,r.mobilePngPath,r.mobilePngSha256,360,q.id);}
  let authorChecks=0,independentChecks=0;
  for(const [file,tokens]of AUTHORS){
    const report=json(root,`${DOCS}/${file}`),ids=idsFor(tokens);assert.match(report.status,/^author-checks-passed/);noFindings(report.openFindings,file);
    assert.equal(report.questions??report.questionCount,ids.length);fileBindings(report,TOPICS.filter(([,token])=>tokens.includes(token)).map(([topic])=>`content/ib/psychology/${topic}.json`),bindings,file);
    const records=exactIds(report.records,ids,file);
    for(const [id,r]of records){const q=questions.get(id);assert.equal(r.questionSha256,questionHash(q),`${id}: author evidence predates canonical content`);meaningful(r.reasoning,id+' author reasoning',80);noFindings(r.openFindings,id);numericChecks(r,q,id+' author',{requireReason:false});authorChecks+=r.numericChecks.length;if(q.diagramSvg){assert.equal(r.figureEvidence?.svgSha256,sha(q.diagramSvg));assert.ok(JSON.stringify(r.figureEvidence?.scientificChecks??'').length>=60,'Author figure data/geometry checks required');}}
  }
  const uniqueReasoning=new Set();
  for(const [file,tokens,reviewer]of INDEPENDENT){
    const report=json(root,`${DOCS}/${file}`),ids=idsFor(tokens);assert.equal(report.status,'passed');assert.equal(identity(report.reviewer),reviewer,`${file}: assigned independent reviewer required`);assert.equal(report.questions,ids.length);noFindings(report.openFindings,file);
    fileBindings(report,TOPICS.filter(([,token])=>tokens.includes(token)).map(([topic])=>`content/ib/psychology/${topic}.json`),bindings,file);
    const records=exactIds(report.records,ids,file);
    for(const [id,r]of records){
      const q=questions.get(id);assert.equal(r.status,'passed');assert.equal(identity(r.reviewer),reviewer);assert.notEqual(reviewer,authorOf(id),`${id}: author cannot independently approve own work`);
      assert.equal(r.questionSha256,questionHash(q),`${id}: independent review predates canonical content`);assert.equal(r.fullQuestionAndSchemeRead,true,`${id}: full reading missing`);meaningful(r.reasoning,id+' independent reasoning',100);
      const normalized=r.reasoning.trim().toLowerCase().replace(/\s+/g,' ');assert.ok(!uniqueReasoning.has(normalized),`${id}: duplicated independent reasoning`);uniqueReasoning.add(normalized);
      assert.equal(r.assessment?.examSection,q.examSection);assert.equal(r.assessment?.marks,q.marks);assert.equal(r.assessment?.scopeChecked,true);noFindings(r.openFindings,id);
      numericChecks(r,q,id+' independent');independentChecks+=r.numericChecks.length;
      assert.ok(Array.isArray(r.sourceChecks),`${id}: source-check array required`);for(const source of r.sourceChecks){assert.match(source.url,/^https:\/\//);meaningful(source.note,id+' source check',25);}
      if(q.diagramSvg){
        const f=r.figureReview,n=nativeMap.get(id);assert.ok(f,`${id}: actual native/mobile inspection missing`);assert.equal(f.svgSha256,sha(q.diagramSvg));assert.equal(f.nativePngSha256,n.nativePngSha256);assert.equal(f.mobilePngSha256,n.mobilePngSha256);assert.equal(f.scientificGeometryChecked,true);assert.equal(f.legible,true);meaningful(f.reasoning,id+' figure reasoning',50);
        if(f.nativePngPath!==undefined)assert.equal(f.nativePngPath,n.nativePngPath);if(f.mobilePngPath!==undefined)assert.equal(f.mobilePngPath,n.mobilePngPath);
      }else assert.ok(r.figureReview===undefined||r.figureReview===null,`${id}: unexpected figure review`);
    }
  }
  return {summary:{firstAssessment:2027,questions:240,sharedQuestions:180,additionalHlQuestions:60,collections:7,figures:figures.length,uniqueAssets:figureHashes.size,authorNumericChecks:authorChecks,independentNumericChecks:independentChecks},canonicalFiles:[...bindings.values()]};
}

function walk(root,relative){const entries=[];for(const name of readdirSync(join(root,relative)).sort()){const file=relative+'/'+name,stat=lstatSync(join(root,file));assert.ok(!stat.isSymbolicLink(),`${file}: symlink not allowed`);if(stat.isDirectory())entries.push(...walk(root,file));else if(stat.isFile())entries.push(file);}return entries;}
export function protectedFilePaths(root=ROOT){
  const files=[...TOPICS.map(([topic])=>`content/ib/psychology/${topic}.json`),'content/ib/psychology-diagram-manifest.json','lib/ib/psychology-catalog.ts',...walk(root,DOCS),...walk(root,'scripts/ib-psychology-authoring').filter(p=>p.endsWith('.py')),
    'scripts/ib-component-harness.mjs',...readdirSync(join(root,'scripts')).filter(name=>/^(?:(?:verify|finalize|stage|render|upload|attach)-ib-psychology[^/]*|psychology-media)\.mjs$/.test(name)).map(name=>'scripts/'+name)];
  return [...new Set(files)].sort();
}
export function mutationCodeBindings(root=ROOT){return MUTATION_CODE_FILES.map(file=>({file,sha256:sha(read(root,file))}));}
export function validateMutationProof(root,report){
  assert.equal(report.status,'passed');assert.equal(report.unitCases,8);assert.equal(report.mutationCases,EXPECTED_MUTATION_CASES.length);
  assert.deepEqual(report.cases,EXPECTED_MUTATION_CASES,'Every named mutation test must be recorded');
  assert.ok(Number.isSafeInteger(report.semanticMutationCases)&&report.semanticMutationCases>=24,'Semantic mutations must exercise evidence checks, not only frozen-byte drift');
  assert.deepEqual(report.codeBindings,mutationCodeBindings(root),'Mutation proof predates current guard/finalizer/tester/harness code');
}
export function verifyReviewManifest(root=ROOT,provided){
  const manifest=provided??json(root,MANIFEST);assert.equal(manifest.schemaVersion,1);assert.equal(manifest.status,'passed');assert.equal(manifest.hashAlgorithm,'sha256');
  validateMutationProof(root,json(root,`${DOCS}/review-guard-mutation-checks.json`));
  const evidence=readReviewEvidence({root});assert.deepEqual(manifest.summary,evidence.summary);assert.deepEqual(manifest.canonicalFiles,evidence.canonicalFiles);
  const paths=protectedFilePaths(root);assert.deepEqual(manifest.files.map(r=>r.file),paths,'Frozen file inventory differs');assert.equal(new Set(manifest.files.map(r=>r.file)).size,paths.length);
  for(const entry of manifest.files){const bytes=read(root,entry.file);assert.equal(entry.bytes,bytes.length);assert.equal(entry.sha256,sha(bytes),`${entry.file}: bytes changed after final review`);}
  return evidence;
}
if(process.argv[1]&&pathToFileURL(resolve(process.argv[1])).href===import.meta.url){try{assert.equal(process.argv.length,2,'Verification accepts no bypass flags');const e=verifyReviewManifest();console.log(`IB Psychology review guard passed: ${e.summary.questions} questions, ${e.summary.figures} native/mobile reviewed figures, first assessment2027; all frozen bytes match.`);}catch(error){console.error(`IB Psychology review guard failed: ${error.message}`);process.exitCode=1;}}
