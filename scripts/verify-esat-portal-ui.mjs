import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import ts from 'typescript';

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

const strip = readTsx('app/esat/EsatModulePredictions.tsx');
const visibleText = collect(strip, node => ts.isJsxText(node)).map(node => node.text).join(' ');
assert.doesNotMatch(visibleText, /\bTMUA\b/i,
  'ESAT predictor explanation must not refer students to a different exam predictor');
for (const phrase of ['recognised ESAT paper', 'module by module', 'retakes', 'Question Bank evidence',
  'confidence and likely range', 'Official ESAT results are reported separately for each module']) {
  assert.ok(visibleText.includes(phrase), `ESAT explanation preserves: ${phrase}`);
}
console.log('PASS: ESAT Logout matches TMUA styling, keeps its logout route, and its predictor explanation is ESAT-specific.');
