import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import ts from 'typescript';
import vm from 'node:vm';
import * as React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import * as jsxRuntime from 'react/jsx-runtime';
import * as esatPolicy from '../lib/esat-predictions.ts';

function readTsx(path) {
  const source = readFileSync(path, 'utf8');
  return ts.createSourceFile(path, source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
}

function collect(root, predicate) {
  const matches = [];
  function visit(node) {
    if (predicate(node)) matches.push(node);
    ts.forEachChild(node, visit);
  }
  visit(root);
  return matches;
}

function logoutButton(file) {
  const matches = collect(file, node => ts.isJsxElement(node)
    && node.openingElement.tagName.getText(file) === 'button'
    && node.children.some(child => ts.isJsxText(child) && child.text.trim() === 'Logout'));
  assert.equal(matches.length, 1, `${file.fileName} has one Logout button`);
  return matches[0].openingElement;
}

function attribute(element, name, file) {
  const attr = element.attributes.properties.find(property => ts.isJsxAttribute(property)
    && property.name.getText(file) === name);
  return attr?.initializer?.getText(file);
}

const tmua = readTsx('app/dashboard/DashboardClient.tsx');
const esat = readTsx('app/esat/ESATDashboardClient.tsx');
const tmuaLogout = logoutButton(tmua);
const esatLogout = logoutButton(esat);
assert.equal(attribute(esatLogout, 'className', esat), attribute(tmuaLogout, 'className', tmua),
  'ESAT Logout uses exactly the same shared button styles as TMUA');
assert.equal(attribute(esatLogout, 'type', esat), '"button"');
assert.match(attribute(esatLogout, 'onClick', esat), /window\.location\.href\s*=\s*"\/api\/logout"/,
  'ESAT retains its existing server logout endpoint');
assert.match(esat.text, /import styles from "\.\.\/dashboard\/dashboard\.module\.css"/);
assert.match(tmua.text, /import styles from "\.\/dashboard\.module\.css"/);

const strip = readTsx('app/esat/EsatPredictionStrip.tsx');
const visibleText = collect(strip, node => ts.isJsxText(node)).map(node => node.text).join(' ');
assert.doesNotMatch(visibleText, /\bTMUA\b/i,
  'ESAT predictor explanation must not refer students to a different exam predictor');
for (const phrase of ['recognised ESAT paper', 'module by module', 'retakes', 'Question Bank evidence',
  'confidence and likely range', 'Official ESAT results are reported separately for each module']) {
  assert.ok(visibleText.includes(phrase), `ESAT explanation preserves: ${phrase}`);
}
console.log('PASS: ESAT Logout matches TMUA styling, keeps its logout route, and its predictor explanation is ESAT-specific.');

assert.match(strip.text, /<ExamCountdown exam="ESAT"/);
assert.match(strip.text, /styles\.strip/);
assert.match(strip.text, /preparationMeta/);
assert.doesNotMatch(strip.text, /<form|type="date"|actualScores|lock_at/);

// Render the actual strip against ready and partial responses, including older
// API responses, so neither the strip nor its info tooltip leaks partial scores.
function renderStrip(predictions, status="inferred") {
  let index=0;
  const states=[{ok:true,preparationRank:{rank:4,cohortSize:40}}, {ok:true,pathway:{status,modules:predictions.map(p=>p.module)},predictions},true];
  const exports={};
  const css=new Proxy({}, {get:(_,key)=>String(key)});
  const compiled=ts.transpileModule(strip.text,{compilerOptions:{jsx:ts.JsxEmit.ReactJSX,module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
  vm.runInNewContext(compiled,{exports,require:name=>{
    if(name==="react")return{...React,useEffect:()=>{},useState:()=>[states[index++],()=>{}]};
    if(name==="react/jsx-runtime")return jsxRuntime;
    if(name==="@/lib/esat-predictions")return esatPolicy;
    if(name==="@/app/_components/ExamCountdown")return{default:()=>React.createElement("span",{role:"timer"},"68 days")};
    if(name.endsWith(".css"))return{default:css};
    throw new Error(name);
  }});
  return renderToStaticMarkup(React.createElement(exports.default));
}
const scores=["Mathematics 1","Mathematics 2","Biology"].map(module=>({module,score:6.5,confidence:"low",lowerBound:5,upperBound:8,independentTestCount:0,qbUniqueQuestions:20,qbTopicCoverage:1}));
for(const [items,status] of [[[],"building"],[scores.slice(0,2),"building"],[scores.map((p,i)=>i===2?{...p,score:null,confidence:null}:p),"inferred"],[scores,"building"]]){
  const html=renderStrip(items,status);
  assert.match(html,/>Still building\.</);
  assert.doesNotMatch(html,/Maths [12]|Biology|6\.5|class="moduleName"/);
  assert.match(html,/You rank/);
  assert.match(html,/68 days/);
}
const readyHtml=renderStrip(scores);
assert.match(readyHtml,/Maths 1/); assert.match(readyHtml,/Maths 2/); assert.match(readyHtml,/Biology/);
assert.match(readyHtml,/Low confidence/);
assert.doesNotMatch(readyHtml,/>Still building\.</);
console.log("PASS: one building state until all three scores are ready; module names, scores and confidence appear together; rank/countdown remain visible.");
