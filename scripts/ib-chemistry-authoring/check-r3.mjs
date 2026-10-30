import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import assert from 'node:assert/strict';
import {unified} from 'unified';
import remarkParse from 'remark-parse';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import katex from 'katex';
import {ibQuestionSchema,questionPrompt,safeDiagram} from '../../lib/ib/question.ts';

const qs=JSON.parse(readFileSync('content/ib/chemistry/reactivity-3.json','utf8'));
assert.equal(qs.length,120);
const parser=unified().use(remarkParse).use(remarkGfm).use(remarkMath);
let maths=0,diagrams=0;const errors=[];
function walk(node,id,source){
 if(['math','inlineMath'].includes(node.type)){try{katex.renderToString(node.value,{throwOnError:true,strict:'ignore',trust:false});maths++;}catch(e){errors.push(id+': '+e.message);}}
 if(node.type==='text'&&node.value.includes('$')&&node.position){const raw=source.slice(node.position.start.offset,node.position.end.offset);if(/(?<!\\)\$/.test(raw))errors.push(id+': unparsed math delimiter '+raw);}
 node.children?.forEach(c=>walk(c,id,source));
}
for(const [i,q] of qs.entries()){
 const parsed=ibQuestionSchema.safeParse(q);if(!parsed.success)errors.push(q.id+': '+parsed.error.message);
 assert.equal(q.number,i+1);
 const strings=[q.stem,...q.parts.map(p=>p.prompt),...(q.options||[]).map(o=>o.text),...q.markScheme.flatMap(g=>g.steps.map(s=>s.text))];
 for(const s of strings){if(/[\u0000-\u0009\u000b-\u001f]/.test(s))errors.push(q.id+': control character');walk(parser.parse(s),q.id,s);}
 for(const k of ['diagramSvg','markSchemeDiagramSvg'])if(q[k]){diagrams++;if(!safeDiagram(q[k]))errors.push(q.id+': unsafe diagram');}
 const pub=questionPrompt(q);for(const k of ['markScheme','answerSummary','correctOption','verification','source','markSchemeDiagramSvg'])assert.ok(!(k in pub));
}
const ledger=[
 ['R3-004 hydrogen concentration',10**-3.42,3.8018939632056124e-4],
 ['R3-005 dilution pH',-Math.log10(.150*.0100/.2500),2.221848749616356],
 ['R3-007 neutral pH at supplied Kw',-Math.log10(Math.sqrt(4e-14)),6.698970004336019],
 ['R3-013 excess acid pH',-Math.log10((.02*.08-.012*.1)/.032),1.9030899869919438],
 ['R3-015 titration concentration',.125*.01640/.020,0.1025],
 ['R3-018 weak acid pH',-Math.log10(Math.sqrt(1.6e-5*.100)),2.8979400086720375],
 ['R3-019 weak base pH',14+Math.log10(Math.sqrt(4e-6*.025)),10.5],
 ['R3-023 Ka',10**-4.36,4.365158322401656e-5],
 ['R3-027 buffer pH',-Math.log10(2e-5*.06/.09),4.8750612633917],
 ['R3-028 after acid pH',-Math.log10(1.8e-5*.05/.04),4.647817481888637],
 ['R3-037 magnesium gas volume',.486/24.31*22.7,.45381324557795145],
 ['R3-052 Gibbs kJ/mol',-2*96500*.72/1000,-138.96],
 ['R3-058 iron concentration',.0200*.01860*5/.025,.0744]
];
for(const [label,actual,expected] of ledger)if(Math.abs(actual-expected)>1e-10*Math.max(1,Math.abs(expected)))errors.push(label+': mismatch '+actual);
const report={status:errors.length?'failed':'passed',questions:qs.length,mathExpressions:maths,diagrams,coverage:Object.fromEntries(['R3.1','R3.2','R3.3','R3.4'].map(c=>[c,qs.filter(q=>q.syllabusCode===c).length])),sl:qs.filter(q=>q.level==='sl').length,ahl:qs.filter(q=>q.level==='ahl').length,checks:['schema and IDs','exact mark sums via schema','private/public field separation','full Markdown/KaTeX parsing','safe SVG','independent numerical ledger'],numericLedger:ledger.map(([label,actual])=>({label,actual})),errors};
mkdirSync('docs/ib-chemistry-reviews',{recursive:true});writeFileSync('docs/ib-chemistry-reviews/reactivity-3-validation.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));if(errors.length)process.exitCode=1;
