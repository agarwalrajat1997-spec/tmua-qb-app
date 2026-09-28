import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const root = process.cwd();
const engine = fs.readFileSync(path.join(root, 'public/shared/tmua-past-paper-options.js'), 'utf8');
const ids = Array.from({ length: 8 }, (_, i) => `full-official-${2016 + i}`).concat('full-specimen');
const clean = value => JSON.parse(JSON.stringify(value));

// DOM contract harness: exercise the real engine with all 360 actual question templates.
// Integration coverage additionally runs the real inline exam controllers and submit helpers.
class Element {
  constructor(tagName = 'div') {
    this.tagName = tagName.toUpperCase(); this.children = []; this.parentElement = null;
    this.className = ''; this._text = ''; this._html = '';
  }
  appendChild(node) {
    if (node.parentElement) node.parentElement.children = node.parentElement.children.filter(child => child !== node);
    node.parentElement = this; this.children.push(node); return node;
  }
  insertAdjacentElement(where, node) {
    assert.equal(where, 'afterend');
    const siblings = this.parentElement.children;
    node.parentElement = this.parentElement;
    siblings.splice(siblings.indexOf(this) + 1, 0, node);
  }
  get textContent() { return this._text + this.children.map(child => child.textContent).join(''); }
  set textContent(value) { this._text = value; this.children = []; }
  get innerHTML() { return this._html; }
  set innerHTML(html) {
    this._html = html; this.children = [];
    const heading = html.match(/<div class="question-number">([\s\S]*?)<\/div>/);
    if (heading) { const node = new Element(); node.className = 'question-number'; node.textContent = heading[1]; this.appendChild(node); }
    const groups = [...html.matchAll(/class="options"/g)];
    for (const _ of groups) {
      const group = new Element(); group.className = 'options'; this.appendChild(group);
      for (const match of html.matchAll(/<label class="option">([\s\S]*?)<\/label>/g)) {
        const label = new Element('label'); label.className = 'option'; label.originalHTML = match[0];
        for (const inputMatch of match[1].matchAll(/<input\b([^>]*)>/g)) {
          const input = new Element('input');
          for (const attr of inputMatch[1].matchAll(/(type|name|value)="([^"]*)"/g)) input[attr[1]] = attr[2];
          label.appendChild(input);
        }
        group.appendChild(label);
      }
    }
  }
  querySelectorAll(selector) {
    const result = [];
    const matches = node => selector === 'input[type="radio"]' ? node.tagName === 'INPUT' && node.type === 'radio'
      : selector === 'label.option' ? node.tagName === 'LABEL' && node.className === 'option'
      : selector.startsWith('.') ? node.className === selector.slice(1) : false;
    const visit = node => node.children.forEach(child => { if (matches(child)) result.push(child); visit(child); });
    visit(this); return result;
  }
  querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
}

function environment(order = 'sequential', multiplier = '1') {
  const selected = { order, multiplier };
  const controls = [{ disabled: false }, { disabled: false }];
  let seed = 982453653;
  const seededMath = Object.create(Math);
  seededMath.random = () => { seed = (1664525 * seed + 1013904223) >>> 0; return seed / 4294967296; };
  const document = {
    readyState: 'loading', addEventListener() {},
    getElementById() { return null; }, createElement: name => new Element(name),
    querySelector(selector) { return { value: selector.includes('ts-past-order') ? selected.order : selected.multiplier }; },
    querySelectorAll(selector) { return selector.includes('ts-past-paper-settings') ? controls : []; }
  };
  const context = vm.createContext({ document, window: {}, Math: seededMath });
  vm.runInContext(engine, context);
  return { api: context.window.TS_TMUA_PAST_PAPER, document, selected, controls };
}

let diagramOptions = 0;
let checkedOptions = 0;
for (const testId of ids) {
  const html = fs.readFileSync(path.join(root, `public/practice-tests/tests/${testId}.html`), 'utf8');
  const literal = html.match(/const questions\s*=\s*(\[[\s\S]*?\n\s*\]);/);
  assert.ok(literal, `${testId}: questions present`);
  const questions = vm.runInNewContext(literal[1]);
  const original = JSON.stringify(questions);
  assert.equal(questions.length, 40);

  for (const multiplier of ['1', '1.25', '1.5']) {
    const { api } = environment('sequential', multiplier);
    const config = clean(api.prepare(questions, { testId }));
    assert.equal(config.seconds_per_paper, ({ '1': 4500, '1.25': 5625, '1.5': 6750 })[multiplier]);
    assert.equal(api.durationSeconds(), config.seconds_per_paper);
    assert.deepEqual(config.question_order, Array.from({ length: 40 }, (_, i) => i));
    assert.equal(api.questionAt(2, 0), 20);
    assert.equal(api.formatQuestion(23), 'Q4');
    assert.equal(api.formatAnswer(23, 'B'), 'B');
  }

  const { api, document, selected, controls } = environment('randomised', '1.25');
  const config = clean(api.prepare(questions, { testId }));
  assert.ok(controls.every(input => input.disabled));
  assert.deepEqual(config.question_order.slice(0, 20).toSorted((a, b) => a - b), Array.from({ length: 20 }, (_, i) => i));
  assert.deepEqual(config.question_order.slice(20).toSorted((a, b) => a - b), Array.from({ length: 20 }, (_, i) => i + 20));
  assert.notDeepEqual(config.question_order, Array.from({ length: 40 }, (_, i) => i));
  if (testId === 'full-official-2022') assert.equal(config.option_order[23].at(-1), 'E');

  questions.forEach((question, originalIndex) => {
    const container = document.createElement('div'); container.innerHTML = question;
    const inputs = container.querySelectorAll('input[type="radio"]');
    const originalLabels = container.querySelectorAll('label.option');
    const originalByValue = new Map(originalLabels.map(label => [label.querySelector('input[type="radio"]').value, label]));
    inputs.forEach(input => { input.listener = () => input.value; input.checked = input.value === 'B'; });
    api.decorateQuestion(container, originalIndex);
    const labels = container.querySelectorAll('label.option');
    const order = labels.map(label => label.querySelector('input[type="radio"]').value);
    assert.deepEqual(order, config.option_order[originalIndex]);
    assert.equal(api.questionAt(originalIndex < 20 ? 1 : 2, api.positionOf(originalIndex)), originalIndex);
    assert.equal(container.querySelector('.question-number')._text, `Question ${api.positionOf(originalIndex) + 1}`);
    assert.match(api.formatQuestion(originalIndex), new RegExp(`^Original Q${originalIndex % 20 + 1} \\(shown as Q\\d+\\)$`));
    labels.forEach((label, displayIndex) => {
      const input = label.querySelector('input[type="radio"]');
      assert.equal(label, originalByValue.get(input.value), 'the entire original label must move, including images');
      assert.equal(input.name, `q${originalIndex + 1}`);
      assert.equal(input.listener(), input.value, 'listeners survive moving DOM nodes');
      assert.equal(input.checked, input.value === 'B');
      assert.equal(label.querySelector('.ts-past-choice-letter').textContent, 'ABCDEFGH'[displayIndex]);
      assert.equal(api.formatAnswer(originalIndex, input.value), `${input.value} (shown as ${'ABCDEFGH'[displayIndex]})`);
      if (label.originalHTML.includes('<img')) diagramOptions++;
      checkedOptions++;
    });
    api.decorateQuestion(container, originalIndex);
    assert.equal(container.querySelectorAll('.ts-past-choice-letter').length, inputs.length, 'repeat decoration must not duplicate badges');
  });
  assert.equal(JSON.stringify(questions), original, 'canonical question templates must not change');
  selected.order = 'sequential'; selected.multiplier = '1.5';
  assert.deepEqual(clean(api.prepare(questions, { testId })), config, 'repeat starts keep the same permutation and timing');
  const detachedCopy = api.metadata(); detachedCopy.question_order.reverse(); detachedCopy.option_order[0].reverse();
  assert.deepEqual(clean(api.metadata()), config, 'callers cannot mutate the active permutation');
  assert.equal(api.formatAnswer(0, null), null);
  assert.equal(api.formatAnswer(0, '–'), '–');
}

const sampleHtml = fs.readFileSync(path.join(root, 'public/practice-tests/tests/full-official-2022.html'), 'utf8');
const sample = vm.runInNewContext(sampleHtml.match(/const questions\s*=\s*(\[[\s\S]*?\n\s*\]);/)[1]);
for (const mutate of [
  questions => questions.pop(),
  questions => { questions[39] = questions[39].replace('name="q40"', 'name="q1"'); },
  questions => { questions[39] = questions[39].replace('value="A"', 'value="B"'); },
  questions => { questions[39] = questions[39].replace('class="question-number"', 'class="missing"'); },
]) {
  const { api, controls } = environment('randomised', '1');
  const broken = sample.slice(); mutate(broken);
  assert.throws(() => api.prepare(broken, { testId: 'full-official-2022' }));
  assert.throws(() => api.metadata(), 'failed validation must not commit partial preparation');
  assert.ok(controls.every(input => !input.disabled), 'failed validation must not lock the settings');
  assert.equal(api.prepare(sample, { testId: 'full-official-2022' }).question_order.length, 40);
}
assert.throws(() => environment().api.prepare(sample, { testId: 'tmua-2026-predictive-paper' }));
assert.throws(() => environment('randomised', '2').api.prepare(sample, { testId: 'full-official-2022' }));
assert.throws(() => environment('invalid', '1').api.prepare(sample, { testId: 'full-official-2022' }));
assert.ok(diagramOptions > 0, 'image choices are covered');
console.log(`TMUA past-paper options engine verified: 9 papers, 360 questions, ${checkedOptions} options (${diagramOptions} image options), 3 timing allowances, canonical mappings and atomic validation.`);
