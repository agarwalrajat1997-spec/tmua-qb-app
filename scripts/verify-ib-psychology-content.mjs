import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {unified} from 'unified';
import remarkParse from 'remark-parse';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import katex from 'katex';
import {ibHarness} from './ib-component-harness.mjs';
import {readQuestions,sha,ORIGIN,PREFIX,MANIFEST} from './psychology-media.mjs';

const partial=process.argv.includes('--partial'),requireCdn=process.argv.includes('--require-cdn'),liveCdn=process.argv.includes('--live-cdn');
const h=ibHarness(),catalog=h.load('lib/ib/catalog.ts'),{PSYCHOLOGY_TOPICS,PSYCHOLOGY_SECTIONS}=h.load('lib/ib/psychology-catalog.ts');
const questions=readQuestions({partial}).map(({q})=>q),manifest=JSON.parse(readFileSync(MANIFEST,'utf8'));
assert.equal(manifest.schemaVersion,1);assert.equal(manifest.origin,ORIGIN);
const parser=unified().use(remarkParse).use(remarkMath).use(remarkGfm),fingerprints=new Map(),assets=new Set(),counts={};
let formulas=0,figures=0;
function checkMarkdown(text,label){
  assert.doesNotMatch(text,/[\u0000-\u0009\u000b-\u001f]/,label+': control character');
  assert.doesNotMatch(text,/\b(?:TODO|TBD|INSERT SOLUTION|placeholder solution)\b/i,label+': unfinished text');
  const visit=node=>{if(node.type==='math'||node.type==='inlineMath'){katex.renderToString(node.value,{throwOnError:true,strict:'ignore',trust:false});formulas++;}if(node.children)node.children.forEach(visit);};visit(parser.parse(text));
}
for(const q of questions){
  const fingerprint=q.stem.toLowerCase().replace(/\s+/g,' ').trim();
  assert.ok(!fingerprints.has(fingerprint),`${q.id}: duplicate prompt ${fingerprints.get(fingerprint)}`);fingerprints.set(fingerprint,q.id);
  checkMarkdown(q.stem,q.id+' stem');
  for(const group of q.markScheme){
    for(const step of group.steps)checkMarkdown(step.text,q.id+' worked answer');
    for(const band of group.rubric.bands)checkMarkdown(band.descriptor,q.id+' band');
  }
  const prompt=h.model.questionPrompt(q);
  for(const key of ['markScheme','markSchemeDiagramSvg','markSchemeDiagramUrl','markSchemeDiagramCaption','answerSummary','source','verification','correctOption'])assert.ok(!(key in prompt),q.id+': private '+key);
  for(const [svgField,urlField]of[['diagramSvg','diagramUrl'],['markSchemeDiagramSvg','markSchemeDiagramUrl']]){
    const svg=q[svgField];if(!svg){assert.ok(!q[urlField],q.id+': no raster/remote-only image in this release');continue;}
    assert.ok(h.model.safeDiagram(svg),q.id+': unsafe SVG');const hash=sha(svg);assets.add(hash);figures++;
    if(requireCdn||q[urlField]){const entry=manifest.assets[hash];assert.ok(entry,q.id+': no verified CDN asset');assert.equal(entry.key,PREFIX+hash+'.svg');assert.equal(entry.bytes,Buffer.byteLength(svg));assert.equal(entry.contentType,'image/svg+xml');assert.equal(q[urlField],ORIGIN+'/'+entry.key,q.id+': mismatched CDN URL');}
  }
  counts[q.topicId]=(counts[q.topicId]??0)+1;
}
if(!partial){
  assert.equal(questions.length,240);assert.equal(questions.filter(q=>q.level==='sl').length,180);assert.equal(questions.filter(q=>q.level==='ahl').length,60);
  for(const topic of PSYCHOLOGY_TOPICS){
    const qs=questions.filter(q=>q.topicId===topic.id);assert.equal(qs.length,topic.questions,topic.id);
    assert.deepEqual(qs.map(q=>q.number),Array.from({length:topic.questions},(_,i)=>i+1),topic.id+': sequential local numbering');
    for(const area of topic.subtopics)assert.ok(qs.some(q=>q.syllabusCode===area.code),area.code+': content coverage');
    for(const difficulty of ['medium','hard'])assert.ok(qs.some(q=>q.difficulty===difficulty),topic.id+': both difficulties');
  }
  for(const section of Object.keys(PSYCHOLOGY_SECTIONS))assert.ok(questions.some(q=>q.examSection===section),section+': style coverage');
  assert.equal(questions.filter(q=>h.model.questionAvailableForCourse(q,'sl')).length,180);
  assert.equal(questions.filter(q=>h.model.questionAvailableForCourse(q,'hl')).length,240);
}
if(liveCdn)for(const hash of assets){
  const entry=manifest.assets[hash];assert.ok(entry,'Live verification requires a manifest entry');
  const response=await fetch(ORIGIN+'/'+entry.key,{signal:AbortSignal.timeout(25000)});assert.equal(response.status,200);assert.match(response.headers.get('content-type')??'',/^image\/svg\+xml\b/);
  const bytes=Buffer.from(await response.arrayBuffer());assert.equal(sha(bytes),hash);assert.equal(bytes.length,entry.bytes);
}
assert.equal(catalog.IB_COURSES.psychology.firstAssessment,2027);
console.log(JSON.stringify({status:'passed',partial,questions:questions.length,shared:questions.filter(q=>q.level==='sl').length,additionalHl:questions.filter(q=>q.level==='ahl').length,figures,uniqueAssets:assets.size,formulas,collections:counts,cdn:liveCdn?'live-byte-verified':requireCdn?'manifest-and-exact-URL-verified':'not required',scope:'Schema/identity, cohort, section/marks, holistic allocations, exact duplicates, renderable Markdown/math, image safety, SL boundaries and prompt privacy. Scientific correctness is covered by separate independent reviews.'}));
