import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { performance } from 'node:perf_hooks';
import { ibHarness } from './ib-component-harness.mjs';

// Exercise the real async content loader, not the route-level content double.
const imports=[];
const h=ibHarness({onModule:name=>imports.push(name)});
const started=performance.now();
const content=h.load('lib/ib/content.ts');
const moduleMs=performance.now()-started;
const bankImports=()=>imports.filter(name=>/^@\/content\/ib\/[^/]+\/[^/]+\.json$/.test(name));
assert.equal(bankImports().length,0,'importing navigation does not load any question banks');
const summary=content.getIbSummary('hl');
assert.equal(summary['physics-hl'].questions,740);
assert.equal(content.getIbSummary('sl')['physics-hl'].questions,518);
assert.equal(content.getIbSummary('hl'),summary,'summary reuses immutable build metadata');
assert.equal(bankImports().length,0,'overview requires zero question banks');

const startBank=performance.now();
const [hl,sl,question]=await Promise.all([
  content.getIbQuestions('physics-space-time-motion','hl'),
  content.getIbQuestions('physics-space-time-motion','sl'),
  content.getIbQuestion('ib-phy-a-001','hl'),
]);
const firstBankMs=performance.now()-startBank;
assert.equal(bankImports().length,1,'parallel list/detail/course requests share one bank load');
assert.equal(question,hl.find(q=>q.id==='ib-phy-a-001'));
assert.ok(sl.every(q=>q.level==='core'));
assert.equal(await content.getIbQuestions('physics-space-time-motion'),hl,'warm banks reuse validated content');
const ahl=hl.find(q=>q.level==='ahl');
assert.equal(await content.getIbQuestion(ahl.id,'sl'),undefined,'SL cannot access AHL detail');
for(const invalid of ['missing','__proto__','constructor']){
 assert.equal((await content.getIbQuestions(invalid)).length,0);
 assert.equal(await content.getIbQuestion(invalid),undefined);
}
assert.equal(bankImports().length,1,'unknown IDs cannot trigger arbitrary bank imports');

let timer=performance.now();
for(let i=0;i<100;i++)content.getIbSummary(i%2?'sl':'hl');
const summaryAverageMs=(performance.now()-timer)/100;
timer=performance.now();
for(let i=0;i<1000;i++)await content.getIbQuestions('physics-space-time-motion','sl');
const collectionLookupAverageMs=(performance.now()-timer)/1000;

let total=0;
for(const collection of h.model.IB_COLLECTIONS){
 const file=`content/ib/${collection.subject}/${collection.subject==='math-aa-hl'?collection.id:collection.topicId}.json`;
 const enrichment=[...['aa-sl','aa-hl','ai-sl','ai-hl'].flatMap(course=>JSON.parse(readFileSync('content/ib/math-2026-expansion/'+course+'.json','utf8'))),...['structure','periodicity','reactivity','mechanisms'].flatMap(batch=>JSON.parse(readFileSync('content/ib/chemistry-2026-expansion/'+batch+'.json','utf8'))),...['unity-diversity','form-function','interaction-interdependence','continuity-change'].flatMap(batch=>JSON.parse(readFileSync('content/ib/biology-2026-expansion/'+batch+'.json','utf8')))].filter(q=>q.collectionId===collection.id);
 const expected=[...JSON.parse(readFileSync(file,'utf8')),...enrichment].filter(q=>q.status==='published');
 const actual=await content.getIbQuestions(collection.id,'hl');
 assert.deepEqual(Array.from(actual,q=>q.id),expected.map(q=>q.id),'question order preserved');
 assert.deepEqual(Array.from(await content.getIbQuestions(collection.id,'sl'),q=>q.id),expected.filter(q=>h.model.questionAvailableForCourse(q,'sl')).map(q=>q.id));
 for(const q of actual)assert.equal(await content.getIbQuestion(q.id),q,'generated ID index resolves every published question');
 total+=actual.length;
}
assert.equal(bankImports().length,45,'each bank loaded only once');
assert.equal(total,5922);

// A failed load must not poison the cache for the lifetime of the server.
let attempts=0;
const loaders={IB_BANK_LOADERS:{'physics-space-time-motion':async()=>{if(++attempts===1)throw Error('temporary fixture failure');return {default:hl};}}};
// Override only the asynchronous source; validation and retry logic remain real.
const resilient=ibHarness({moduleMocks:{'./bank-loaders':loaders}}).load('lib/ib/content.ts');
await assert.rejects(()=>resilient.getIbQuestions('physics-space-time-motion'),/temporary fixture failure/);
assert.equal((await resilient.getIbQuestions('physics-space-time-motion')).length,hl.length);
assert.equal(attempts,2);
console.log(JSON.stringify({status:'passed',method:'Isolated local module loader; no live auth or network latency',moduleMs,firstBankMs,summaryAverageMs,collectionLookupAverageMs,overviewBanks:0,firstCollectionBanks:1,totalQuestions:total,physicsOverviewPayloadBytes:Buffer.byteLength(JSON.stringify(summary['physics-hl'])),allCoursesPayloadBytes:Buffer.byteLength(JSON.stringify(summary))}));
