import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source = fs.readFileSync(new URL('../public/shared/practice-test-options.js', import.meta.url), 'utf8');
const context = vm.createContext({ console, Math, Set });
vm.runInContext(source, context);
const api = context.TS_TEST_OPTIONS;
const plain = value => JSON.parse(JSON.stringify(value));

// Minimal DOM adapter exercises actual radio change/lock/remount behaviour without network or student data.
function hostFixture() {
  const note = { textContent: '' }, lockedNote = { textContent: '' };
  const listeners = [];
  const doc = { getElementById: () => null, createElement: () => ({}), head: { appendChild() {} } };
  let inputs = [], markup = '';
  return {
    ownerDocument: doc, classList: { add() {} },
    set innerHTML(html) {
      markup = html;
      inputs = [...html.matchAll(/data-ts-choice="([^"]+)" value="([^"]+)"/g)].map(([, key, value]) => ({
        key, value, checked: false, disabled: false,
        getAttribute: () => key, matches: () => true,
      }));
    },
    get innerHTML() { return markup; },
    querySelectorAll: () => inputs,
    querySelector(selector) {
      if (selector === '.ts-test-settings-grid') return markup ? {} : null;
      return selector === '.ts-test-score-note' ? note : lockedNote;
    },
    addEventListener: (_, fn) => listeners.push(fn),
    choose(key, value) {
      const input = inputs.find(i => i.key === key && i.value === String(value));
      assert.ok(input, `choice ${key}=${value} exists`);
      listeners.forEach(fn => fn({ target: input }));
    },
    get inputs() { return inputs; }, get note() { return note.textContent; },
  };
}

for (const [programme, sizes, base] of [['TMUA', [20, 20], 4500], ['TMUA', [20], 4500], ['ESAT', [27, 27, 27], 2400]]) {
  const total = sizes.reduce((a, b) => a + b, 0);
  for (const multiplier of [1, 1.25, 1.5]) {
    for (const order of ['sequential', 'randomised']) {
      const settings = api.create({ testId: 'fixture', programme, sectionSizes: sizes, baseSeconds: base });
      const host = hostFixture(); settings.mount(host);
      host.choose('order', order); host.choose('time_multiplier', multiplier);
      assert.equal(settings.durationSeconds(), base * multiplier);
      if (multiplier !== 1) {
        assert.match(host.note, /actual raw mark stays unchanged/);
        assert.match(host.note, /provisional, unvalidated/);
        assert.match(host.note, /not an official/);
        assert.match(host.note, /standard-time equivalent/);
      }
      const first = plain(settings.start());
      assert.equal(first.order, order);
      assert.equal(first.time_multiplier, multiplier);
      assert.equal(new Set(first.question_order).size, total);
      assert.ok(host.inputs.every(input => input.disabled), 'all choices locked after start');
      assert.deepEqual(plain(settings.start()), first, 'starting twice never reshuffles');
      let offset = 0;
      sizes.forEach((size, section) => {
        for (let position = 0; position < size; position++) {
          const original = settings.questionAt(section, position);
          assert.ok(original >= offset && original < offset + size, 'never crosses a section');
          assert.equal(settings.positionOf(original), position);
          if (order === 'sequential') assert.equal(original, offset + position);
        }
        offset += size;
      });
      const restored = api.create({ programme, sectionSizes: sizes, baseSeconds: base });
      restored.restore(first);
      assert.deepEqual(plain(restored.metadata()), first, 'reload keeps exact mapping and time');
      const remount = hostFixture(); settings.mount(remount);
      assert.equal(remount.inputs.find(i => i.key === 'time_multiplier' && i.checked).value, String(multiplier));
      remount.choose('time_multiplier', multiplier === 1 ? 1.5 : 1);
      assert.deepEqual(plain(settings.metadata()), first, 'locked events cannot change settings');
      const returned = settings.metadata(); returned.question_order.reverse(); returned.section_sizes[0] = 999;
      assert.deepEqual(plain(settings.metadata()), first, 'public metadata cannot mutate internal state');
      const answers = Array.from({ length: total }, (_, i) => 'ABCDE'[i % 5]);
      const submitted = Array(total).fill(null);
      settings.sequence().forEach(original => { submitted[original] = answers[original]; });
      assert.deepEqual(submitted, answers, 'canonical answer mapping is unchanged');
    }
  }
  const legacy = api.create({ programme, sectionSizes: sizes, baseSeconds: base });
  legacy.restore(null);
  assert.equal(legacy.durationSeconds(), base);
  assert.deepEqual(plain(legacy.sequence()), Array.from({ length: total }, (_, i) => i));
}

const test = api.create({ programme: 'TMUA', sectionSizes: [20, 20], baseSeconds: 4500 });
const valid = plain(test.start());
const badCopies = [
  false, 0, '', [], 'invalid',
  { ...valid, version: 2 }, { ...valid, time_multiplier: 2 }, { ...valid, base_seconds_per_section: 3600 },
  { ...valid, section_sizes: [40] }, { ...valid, question_order: Array(40).fill(0) },
  { ...valid, question_order: valid.question_order.map(i => i === 0 ? 20 : i === 20 ? 0 : i), order: 'randomised' },
  { ...valid, question_order: valid.question_order.map(i => i === 0 ? 1 : i === 1 ? 0 : i) },
];
for (const invalid of badCopies) {
  assert.throws(() => test.restore(invalid));
  assert.deepEqual(plain(test.metadata()), valid, 'invalid restore is atomic');
}
assert.throws(() => test.questionAt(2, 0));
assert.throws(() => test.questionAt(0, 20));
assert.throws(() => test.positionOf(-1));
assert.equal(api.deduction(40, 1.25), 3);
assert.equal(api.deduction(40, 1.5), 5);
assert.equal(api.deduction(20, 1.25), 2);
assert.equal(api.deduction(20, 1.5), 3);
assert.equal(api.deduction(27, 1.25), 2);
assert.equal(api.deduction(27, 1.5), 3);
assert.equal(api.adjustedRaw(1, 40, 1.5), 0);
assert.equal(api.adjustedRaw(30, 40, 1.25), 27);
assert.equal(api.adjustedRaw(30, 40, 1.5), 25);
assert.equal(api.adjustedRaw(30, 40, 1), 30);
console.log('PASS shared practice settings: 18 order/time/format combinations, canonical mappings, locked controls, resume, tamper rejection and provisional policy.');
