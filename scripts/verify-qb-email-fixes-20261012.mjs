import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';

const fixes = JSON.parse(fs.readFileSync('scripts/data/qb-email-fixes-20261012.json', 'utf8'));
const fixtures = JSON.parse(fs.readFileSync('scripts/data/esat-option-heading-fixtures.json', 'utf8'));
const source = fs.readFileSync('app/api/esat/qb/_server.ts', 'utf8');
const ctx = vm.createContext({ exports: {} });
vm.runInContext(ts.transpileModule(source.slice(source.indexOf('export function normaliseQuestion')), {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
}).outputText, ctx);
const html = fs.readFileSync('public/esat-question-bank/index.html', 'utf8');
assert.ok(fs.readFileSync('app/api/esat/qb/question/route.ts', 'utf8').includes('"source_json"'));
const renderCode = html.slice(html.indexOf('  function renderOptions(meta, q)'), html.indexOf('  function renderFeedback(meta)'));
let box = { innerHTML: '' };
const escapeHtml = value => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[c]));
const render = vm.createContext({
  el: () => box, questionKey: () => 'stable-qid', answerFor: () => ({}), escapeHtml,
  tsPrepareOptionHtml: value => value,
});
vm.runInContext(renderCode, render);
for (const fixture of fixtures) {
  const q = ctx.exports.normaliseQuestion(fixture);
  assert.equal(q.source_json, undefined);
  assert.deepEqual(q.options, fixture.options, 'Live options must not be replaced by import snapshots');
  assert.equal(q.option_table_headers.length, fixture.source_json.option_table.headers.length);
  render.renderOptions({}, q);
  for (const header of q.option_table_headers) {
    assert.ok(box.innerHTML.includes(escapeHtml(header.label)));
    if (header.unit) assert.ok(box.innerHTML.includes('(' + escapeHtml(header.unit) + ')'));
  }
  assert.equal((box.innerHTML.match(/type="radio"/g) || []).length, fixture.options.length);
}
render.renderOptions({}, ctx.exports.normaliseQuestion({ qid: 'plain', options: [] }));
assert.equal(box.innerHTML, '', 'Headings must clear when navigating to a plain question');
render.renderOptions({}, ctx.exports.normaliseQuestion({ options: [], source_json: { option_table: { headers: [{ label: '<img src=x onerror=alert(1)>', unit: '<script>' }] } } }));
assert.ok(!box.innerHTML.includes('<img') && !box.innerHTML.includes('<script>'), 'Escape imported heading text');

for (const exam of ['tmua', 'esat']) {
  const page = fs.readFileSync(`public/${exam}-question-bank/index.html`, 'utf8');
  const block = page.split('<!-- TS_BUG_REPORT_STANDALONE_JS_V1 -->')[1].split('</script>')[0].replace(/^[\s\S]*?<script>/, '');
  const nodes = new Map();
  const el = id => { if (!nodes.has(id)) nodes.set(id, { innerText: '', textContent: '', value: '', style: {}, dataset: {}, focus() {} }); return nodes.get(id); };
  const identity = { qid: `${exam}-immutable-qid`, id: 'stable-uuid', number: 1712, display_order: 1533, paper: 'Biology', topic: 'Membranes', subtopic: 'Transport' };
  el('qCard').dataset.reportContext = JSON.stringify(identity);
  el('qTitle').innerText = 'Question 1712'; el('posCounter').innerText = '9'; el('posTotal').innerText = '11';
  el('qPrompt').innerText = 'The original question'; el('metaStatus').innerText = 'Checked - Incorrect';
  const sent = [];
  const window = { location: { href: `https://portal.test/${exam}-question-bank/index.html` } };
  const emailjs = { init() {}, async send(service, template, payload) { sent.push(payload); } };
  window.emailjs = emailjs;
  const env = vm.createContext({ window, emailjs, document: { getElementById: el, querySelector: () => ({ value: 'D' }) }, setTimeout() {}, alert() {}, console });
  vm.runInContext(block, env);
  env.BUG_REPORT = window.BUG_REPORT;
  window.BUG_REPORT.open();
  // Simulate navigation while the report is open; the email must still describe
  // the originally rendered question, regardless of changing filter positions.
  el('qCard').dataset.reportContext = JSON.stringify({ qid: 'different-question', number: 1 });
  el('qPrompt').innerText = 'A different question';
  el('bugComment').value = 'The units are missing';
  await window.BUG_REPORT.submit();
  assert.equal(sent.length, 1);
  assert.equal(sent[0].qid, identity.qid);
  assert.equal(sent[0].display_order, '1533');
  assert.equal(sent[0].question_number, '1712');
  assert.equal(sent[0].subtopic, 'Transport');
  assert.equal(sent[0].filtered_position, '9 of 11');
  assert.equal(sent[0].prompt_preview, 'The original question');
  assert.equal(sent[0].comment, 'The units are missing');
  assert.ok(page.includes('card.dataset.reportContext = JSON.stringify'));
}
assert.equal(fixes.length, 7);
for (const suffix of ['0804-28048806', '0805-7CA782B5']) {
  const copies = fixes.filter(f => f.qid.endsWith(suffix));
  assert.equal(copies.length, 2);
  assert.deepEqual(copies[0].patch, copies[1].patch, 'Matching maths corrections across apps');
}
const bio = fixes.find(f => f.qid === 'ESAT-BIO-0115');
assert.ok(bio.patch.options.every(o => o.html.includes(' nm;')));
assert.equal(bio.expected.answer, 'H');
assert.equal(fixes.find(f => f.qid === 'ESAT-P1-0685-0490625F').patch.paper, 'ESAT Mathematics 2');
console.log('PASS: all 45 option-table heading fixtures, escaping/plain-question navigation, immutable report identities and open-time snapshots in both apps, and seven consistent content corrections. No email sent.');
