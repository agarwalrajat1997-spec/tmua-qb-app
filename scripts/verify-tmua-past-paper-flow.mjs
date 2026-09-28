import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const engine = fs.readFileSync('public/shared/tmua-past-paper-options.js', 'utf8');
const ids = Array.from({ length: 8 }, (_, i) => `full-official-${2016 + i}`).concat('full-specimen');
const durations = { '1': 4500, '1.25': 5625, '1.5': 6750 };
const clean = value => JSON.parse(JSON.stringify(value));

// Small DOM contract facade: real labels/inputs keep identity, listeners and ordering.
// This test executes the actual inline exam controller and actual submit serializer.
class Element {
  constructor(tag = 'div') {
    this.tagName = tag.toUpperCase(); this.children = []; this.parentElement = null;
    this.className = ''; this._text = ''; this._html = ''; this.style = {}; this.dataset = {};
    this.listeners = new Map(); this.value = ''; this.disabled = false; this.checked = false;
    this.classList = {
      add: name => { this.className = [...new Set(this.className.split(' ').concat(name))].join(' ').trim(); },
      remove: name => { this.className = this.className.split(' ').filter(x => x !== name).join(' '); },
      contains: name => this.className.split(' ').includes(name),
    };
  }
  appendChild(node) {
    if (node.parentElement) node.parentElement.children = node.parentElement.children.filter(child => child !== node);
    node.parentElement = this; this.children.push(node); return node;
  }
  insertAdjacentElement(where, node) {
    assert.equal(where, 'afterend'); node.parentElement = this.parentElement;
    this.parentElement.children.splice(this.parentElement.children.indexOf(this) + 1, 0, node);
  }
  addEventListener(name, fn) { if (!this.listeners.has(name)) this.listeners.set(name, []); this.listeners.get(name).push(fn); }
  dispatch(name) { for (const fn of this.listeners.get(name) || []) fn({ target: this }); }
  get textContent() { return this._text + this.children.map(child => child.textContent).join(''); }
  set textContent(value) { this._text = String(value); this.children = []; }
  get innerHTML() { return this._html; }
  set innerHTML(html) {
    this._html = String(html); this.children = []; this._text = '';
    const heading = this._html.match(/<div class="question-number">([\s\S]*?)<\/div>/);
    if (heading) { const node = new Element(); node.className = 'question-number'; node.textContent = heading[1]; this.appendChild(node); }
    for (const _ of this._html.matchAll(/class="options"/g)) {
      const group = new Element(); group.className = 'options'; this.appendChild(group);
      for (const match of this._html.matchAll(/<label class="option">([\s\S]*?)<\/label>/g)) {
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
    const matches = node => {
      if (selector === 'input[type="radio"]') return node.tagName === 'INPUT' && node.type === 'radio';
      const name = selector.match(/^input\[name=['"]([^'"]+)['"]\]$/);
      if (name) return node.tagName === 'INPUT' && node.name === name[1];
      if (selector === 'label.option') return node.tagName === 'LABEL' && node.classList.contains('option');
      if (selector.startsWith('.')) return node.classList.contains(selector.slice(1));
      if (selector.startsWith('#')) return node.id === selector.slice(1);
      return false;
    };
    const found = []; const visit = node => node.children.forEach(child => { if (matches(child)) found.push(child); visit(child); });
    visit(this); return found;
  }
  querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
}

function environment(testId, order, multiplier) {
  const html = fs.readFileSync(`public/practice-tests/tests/${testId}.html`, 'utf8');
  const scripts = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g)].map(match => match[1]);
  const controller = scripts.find(script => /const correctAnswers\s*=/.test(script) && /const questions\s*=/.test(script));
  const serializer = scripts.find(script => script.includes('window.TS_SAVE_ATTEMPT = async function'));
  assert.ok(controller && serializer, `${testId}: actual controller and serializer present`);
  assert.ok(html.includes('/shared/tmua-past-paper-options.js') && html.includes('/shared/tmua-past-paper-options.css'));
  const elements = new Map();
  for (const match of html.matchAll(/\bid="([^"]+)"/g)) if (!elements.has(match[1])) { const node = new Element(); node.id = match[1]; elements.set(match[1], node); }
  const body = new Element('body'), footer = new Element(); footer.className = 'footer';
  elements.get('student-name').value = 'Regression Student'; elements.get('student-email').value = 'regression@example.invalid';
  elements.get('test-date').value = 'October 2026'; elements.get('test-title').textContent = `Regression ${testId}`;
  const controls = [{ disabled: false }, { disabled: false }];
  const document = {
    readyState: 'loading', body, addEventListener() {}, createElement: tag => new Element(tag),
    getElementById(id) {
      for (const root of elements.values()) { const nested = root.querySelector('#' + id); if (nested) return nested; }
      if (id === 'solution-frame' && !elements.has(id)) elements.set(id, new Element('iframe'));
      return elements.get(id) || null;
    },
    querySelector(selector) {
      if (selector === '.footer') return footer;
      if (selector.includes('ts-past-order')) return { value: order };
      if (selector.includes('ts-past-time')) return { value: multiplier };
      return this.querySelectorAll(selector)[0] || null;
    },
    querySelectorAll(selector) {
      if (selector.includes('ts-past-paper-settings')) return controls;
      return [...elements.values()].flatMap(node => node.querySelectorAll(selector));
    },
  };
  let clock = Date.parse('2026-09-20T12:00:00Z'), seed = 912783, timerId = 0;
  const intervals = new Map(), requests = [], emails = [], alerts = [];
  const maths = Object.create(Math); maths.random = () => { seed = (1664525 * seed + 1013904223) >>> 0; return seed / 4294967296; };
  class Clock extends Date { constructor(...args) { super(...(args.length ? args : [clock])); } static now() { return clock; } }
  const context = vm.createContext({
    document, Date: Clock, Math: maths, console: { log() {}, error() {}, warn() {} },
    setInterval: (fn, ms) => { assert.equal(ms, 1000); intervals.set(++timerId, fn); return timerId; },
    clearInterval: id => intervals.delete(id), setTimeout: fn => { fn(); return 0; }, clearTimeout() {},
    confirm: () => true, alert: message => alerts.push(message),
    MathJax: { typesetPromise: async () => {} },
    emailjs: { send: (_service, _template, payload) => { emails.push(clean(payload)); return Promise.resolve(); } },
    fetch: async (url, init) => { requests.push({ url, payload: JSON.parse(init.body) }); return { ok: true, status: 200, json: async () => ({ ok: true }) }; },
  });
  context.window = context; context.addEventListener = () => {};
  vm.runInContext(engine, context, { filename: 'tmua-past-paper-options.js' });
  vm.runInContext(controller, context, { filename: `${testId}:controller` });
  vm.runInContext(serializer, context, { filename: `${testId}:serializer` });
  const read = expression => vm.runInContext(expression, context);
  context.onload?.();
  return { context, read, document, elements, intervals, requests, emails, alerts, controls,
    advance: seconds => { clock += seconds * 1000; },
    tick: async seconds => { clock += seconds * 1000; await context.updateTimer(); },
  };
}

let completed = 0;
for (const testId of ids) for (const order of ['sequential', 'randomised']) for (const multiplier of ['1', '1.25', '1.5']) {
  for (const mode of ['correct', 'mixed', 'blank']) {
    const h = environment(testId, order, multiplier), label = `${testId}/${order}/${multiplier}/${mode}`;
    h.advance(123); h.context.startExam();
    assert.equal(h.read('examStage'), 'paper', label);
    assert.equal(h.read('minutes * 60 + seconds'), durations[multiplier], label);
    assert.equal(h.intervals.size, 1, 'exactly one paper timer');
    const metadata = clean(h.context.TS_TMUA_PAST_PAPER.metadata());
    const keys = clean(h.read('correctAnswers'));
    const expected = Array(40).fill(null), expectedFlags = Array(40).fill(false);
    const initialDeadline = h.read('paperDeadline'); h.advance(3); h.context.startExam();
    assert.equal(h.read('paperDeadline'), initialDeadline, 'double Start must not reset timing or order');
    assert.equal(h.read('timeSpent.reduce((a,b)=>a+b,0)'), 0, 'instruction time is excluded');
    for (const paper of [1, 2]) {
      if (paper === 2) {
        h.context.confirmSubmit();
        assert.equal(h.read('examStage'), 'break', label);
        assert.equal(h.read('breakMinutes * 60 + breakSeconds'), 300, 'break remains five minutes');
        const totalBefore = h.read('timeSpent.reduce((a,b)=>a+b,0)');
        h.advance(71); h.context.skipBreak();
        assert.equal(h.read('timeSpent.reduce((a,b)=>a+b,0)'), totalBefore, 'break time excluded');
        assert.equal(h.read('minutes * 60 + seconds'), durations[multiplier], 'same allowance on Paper 2');
        const deadline = h.read('paperDeadline'); h.context.skipBreak();
        assert.equal(h.read('paperDeadline'), deadline, 'double Skip must not restart Paper 2');
      }
      h.context.openNavigator();
      const buttons = h.elements.get('navigator-grid').children;
      assert.equal(buttons.length, 20, label);
      assert.deepEqual(buttons.map(button => Number(button.dataset.index)), metadata.question_order.slice((paper - 1) * 20, paper * 20));
      const first = h.read('current'); h.context.prevQuestion(); assert.equal(h.read('current'), first, 'cannot cross paper boundary backwards');
      h.context.jumpTo(paper === 1 ? 20 : 0); assert.equal(h.read('current'), first, 'navigator cannot cross paper boundary');
      for (let position = 0; position < 20; position++) {
        const canonical = metadata.question_order[(paper - 1) * 20 + position];
        assert.equal(h.read('current'), canonical, label);
        const container = h.elements.get('question-container');
        const inputs = container.querySelectorAll('input[type="radio"]');
        assert.deepEqual(inputs.map(input => input.value), metadata.option_order[canonical]);
        assert.ok(inputs.every(input => input.name === `q${canonical + 1}`));
        assert.equal(h.elements.get('counter').textContent, `Q${position + 1} of 20 (Paper ${paper})`);
        const shouldAnswer = mode === 'correct' || (mode === 'mixed' && canonical % 3 !== 2);
        if (shouldAnswer) {
          const value = mode === 'mixed' && canonical % 3 === 1 ? inputs.find(input => input.value !== keys[canonical]).value : keys[canonical];
          const input = inputs.find(input => input.value === value); input.checked = true; input.dispatch('change'); expected[canonical] = value;
          assert.equal(h.read(`userAnswers[${canonical}]`), value, 'displayed option submits canonical value');
        }
        if (canonical % 7 === 0) {
          h.context.toggleFlag(); expectedFlags[canonical] = true;
          const button = h.document.getElementById(`nav-btn-${canonical}`);
          assert.equal(button.textContent, `⚑ ${position + 1}`, 'flag keeps display position');
          h.context.toggleFlag(); h.context.toggleFlag();
          assert.equal(button.textContent, `⚑ ${position + 1}`, 'repeated flag changes never produce NaN');
        }
        h.advance(2);
        if (position < 19) {
          h.context.nextQuestion();
          if (position === 0) {
            h.context.prevQuestion(); assert.equal(h.read('current'), canonical);
            const restoredInput = h.elements.get('question-container').querySelectorAll('input[type="radio"]').find(input => input.checked);
            assert.equal(restoredInput?.value ?? null, expected[canonical], 'navigation restores selection');
            h.context.nextQuestion();
          }
        } else {
          h.context.nextQuestion(); assert.equal(h.read('current'), canonical, 'last displayed question stays within current paper');
        }
      }
    }
    await h.context.confirmSubmit(); await h.context.confirmSubmit(); await h.context.submitExam();
    assert.equal(h.requests.length, 1, 'submit is saved exactly once'); assert.equal(h.emails.length, 1, 'one results email');
    assert.equal(h.requests[0].url, '/api/practice-tests/submit');
    const payload = h.requests[0].payload;
    assert.equal(payload.test_id, testId); assert.equal(payload.total_questions, 40);
    assert.deepEqual(payload.answers, expected, label); assert.deepEqual(payload.correct_answers, keys);
    assert.deepEqual(payload.flags, expectedFlags); assert.deepEqual(payload.attempt_settings, metadata);
    assert.equal(payload.score, expected.filter((value, i) => value === keys[i]).length, label);
    assert.deepEqual(payload.incorrect, expected.flatMap((value, i) => value === keys[i] ? [] : [i + 1]));
    assert.equal(payload.time_spent.reduce((a, b) => a + b, 0), 83, '83 seconds working; no instruction/break/final double counting');
    const report = h.elements.get('question-container').innerHTML;
    for (let i = 0; i < 40; i++) {
      assert.ok(report.includes(h.context.TS_TMUA_PAST_PAPER.formatQuestion(i)), label);
      assert.ok(report.includes(h.context.TS_TMUA_PAST_PAPER.formatAnswer(i, keys[i])), label);
      const analysis = h.emails[0][i < 20 ? 'paper1' : 'paper2'];
      assert.ok(analysis.includes(h.context.TS_TMUA_PAST_PAPER.formatQuestion(i)));
      assert.ok(analysis.includes(`Correct: ${h.context.TS_TMUA_PAST_PAPER.formatAnswer(i, keys[i])}`));
    }
    assert.equal(h.read('examStage'), 'complete'); assert.equal(h.intervals.size, 0);
    completed++;
  }
  // Timer expiry uses elapsed wall clock, including background tabs; never extends the allowance.
  const t = environment(testId, order, multiplier); t.advance(95); t.context.startExam();
  const first = t.read('current');
  await t.tick(durations[multiplier] - 1);
  assert.equal(t.read('examStage'), 'paper'); assert.equal(t.elements.get('time').textContent, '00:01');
  await t.tick(1); assert.equal(t.read('examStage'), 'break');
  assert.equal(t.read(`timeSpent[${first}]`), durations[multiplier]);
  for (let second = 0; second < 299; second++) { t.advance(1); t.context.updateBreakTimer(); }
  assert.equal(t.read('examStage'), 'break');
  t.advance(1); t.context.updateBreakTimer(); assert.equal(t.read('examStage'), 'paper', 'automatic break ends at exactly300 seconds');
  assert.equal(t.read('paper'), 2); assert.equal(t.read('minutes * 60 + seconds'), durations[multiplier]);
  const second = t.read('current');
  await t.tick(durations[multiplier] + 40);
  assert.equal(t.read('examStage'), 'complete'); assert.equal(t.requests.length, 1);
  assert.equal(t.requests[0].payload.time_spent[second], durations[multiplier], 'background time capped at paper deadline');
  assert.equal(t.requests[0].payload.time_spent.reduce((a, b) => a + b, 0), durations[multiplier] * 2);
}
console.log(`TMUA past-paper flow verified: ${completed} complete submissions across9 actual templates, both orders,3 time allowances, canonical scoring/reports, navigation/flags and exact timers.`);
