import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

// Exercise both shipped controllers, not a second implementation of their sort.
// All metadata, storage, question requests and randomness are isolated fixtures.
const plain = value => JSON.parse(JSON.stringify(value));
const flush = async () => { for (let i = 0; i < 50; i++) await Promise.resolve(); };
const defaultFilters = extra => ({ status: 'all', papers: [], topics: [], difficulties: [], sort: 'random', ...extra });

function harness(product, initialFilters = defaultFilters()) {
  const html = readFileSync(`public/${product}/index.html`, 'utf8');
  assert.match(html, /<option\s+value="random">[^<]*Random[^<]*<\/option>/i, `${product}: visible Random option`);
  const scripts = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g)].map(match => match[1]);
  const source = scripts.find(script => script.includes('let allMeta = []'));
  assert.ok(source, `${product}: live controller exists`);
  const esat = product.startsWith('esat');
  const key = row => esat ? row.qid : String(row.display_order);
  const storageKey = esat ? 'ts_esat_supabase_exact_ui_v1' : 'ts_tmua_supabase_exact_ui_v4';
  const rows = Array.from({ length: 12 }, (_, i) => ({
    id: `db-${i + 1}`, qid: `${esat ? 'ESAT' : 'TMUA'}-fixture-${i + 1}`,
    display_order: 101 + i * 13,
    paper: esat ? ['ESAT Mathematics 1', 'ESAT Mathematics 2', 'ESAT Physics'][i % 3] : `Paper ${i % 2 + 1}`,
    topic: esat && i % 3 === 2 ? 'P1. Electricity' : i < 6 ? '1_Algebra & Functions' : '4_Graphs',
    difficulty: i % 5 + 1,
  }));
  const answers = {};
  rows.forEach((row, i) => {
    if (i % 4 === 0) return;
    answers[key(row)] = {
      selected: 'A', checked: i % 4 > 1, isCorrect: i % 4 === 2,
      flagged: i % 3 === 1, answer: 'A', solution_html: '<p>Fixture solution</p>', time_spent: 10 + i,
    };
  });
  const storage = new Map([[storageKey, JSON.stringify({ answers, filters: initialFilters })]]);
  const errors = [], requests = [], listeners = new Map();
  let randomValue = 0.37;
  const math = Object.create(Math);
  math.random = () => randomValue;
  function node() {
    return { value: '', textContent: '', innerHTML: '', style: {}, dataset: {},
      classList: { add() {}, remove() {} }, setAttribute() {}, addEventListener() {},
      querySelector() { return null; }, querySelectorAll() { return []; } };
  }
  const nodes = new Map(['fSort', 'fStatus', 'qTitle', 'qPrompt', 'posCounter', 'posTotal', 'qCard', 'emptyState'].map(id => [id, node()]));
  let selected = { topic: [], difficulty: [], paper: [] };
  const response = value => ({ ok: true, status: 200, json: async () => plain(value), text: async () => JSON.stringify(value) });
  const addEventListener = (name, fn) => { const list = listeners.get(name) || []; list.push(fn); listeners.set(name, list); };
  const ctx = vm.createContext({
    console: { log() {}, warn: error => errors.push(error), error: error => errors.push(error) },
    Math: math, setTimeout: () => 1, clearTimeout() {}, setInterval: () => 1, clearInterval() {},
    addEventListener, dispatchEvent: event => { for (const fn of listeners.get(event.type) || []) fn(event); },
    Event: class { constructor(type) { this.type = type; } },
    CustomEvent: class { constructor(type, options) { this.type = type; this.detail = options.detail; } },
    localStorage: { getItem: k => storage.get(k) || null, setItem: (k, value) => storage.set(k, String(value)) },
    document: { body: node(), addEventListener() {}, getElementById: id => nodes.get(id) || null,
      querySelectorAll: selector => (selected[selector.match(/data-filter-kind="([^"]+)"/)?.[1]] || []).map(value => ({ value })) },
    fetch: async (url, init) => {
      requests.push(String(url));
      if (String(url).includes('public_question')) {
        const request = JSON.parse(init.body);
        const row = rows.find(item => esat ? item.id === request.id : item.display_order === request.p_display_order);
        assert.ok(row, `${product}: canonical identity requested after random navigation`);
        return response({ ...row, options: [], prompt_html: `<p>Question ${row.qid}</p>`, answer: 'A' });
      }
      throw new Error(`Unexpected network request in random-order test: ${url}`);
    },
    alert() {}, confirm: () => false,
  });
  ctx.window = ctx;
  vm.runInContext(source.replace(/\}\)\(\);\s*$/, `
    window.randomPoolTest = {
      loadState, applyFilters, buildFilters, render, normalizeState,
      initialize: rows => { allMeta = rows; tsApplyFinalChapterOrder(); loadState(); applyFilters(); buildFilters(); },
      replaceFilters: filters => { state = normalizeState({ filters }, state); applyFilters(); buildFilters(); },
      visible: () => visibleList.map(questionKey),
      visibleMeta: () => visibleList,
      metadata: () => allMeta,
      current: () => questionKey(currentMeta()),
      state: () => state,
      topicKey: meta => ${esat ? 'tsTopicKey(meta.paper, meta.topic)' : 'tsCanonicalTopic(meta.topic)'}
    };
  })();`), ctx);
  ctx.randomPoolTest.initialize(plain(rows));
  return { ctx, rows, key, answers, nodes, errors, requests, storage, storageKey,
    random: value => { randomValue = value; },
    ui: filters => {
      selected = { topic: filters.topics || [], difficulty: filters.difficulties || [], paper: filters.papers || [] };
      nodes.get('fSort').value = filters.sort || 'topic';
      nodes.get('fStatus').value = filters.status || 'all';
    },
    restore: state => ctx.dispatchEvent({ type: 'ts-qb-state-restored', detail: { product, state } }),
  };
}

for (const product of ['tmua-question-bank', 'esat-question-bank']) {
  const h = harness(product);
  const test = h.ctx.randomPoolTest;
  const initialMetadata = plain(test.metadata());
  const initialAnswers = plain(test.state().answers);
  const canonical = initialMetadata.map(h.key);
  const randomOrder = plain(test.visible());
  assert.deepEqual([...randomOrder].sort(), [...canonical].sort(), `${product}: every eligible question appears exactly once`);
  assert.equal(new Set(randomOrder).size, randomOrder.length);
  assert.notDeepEqual(randomOrder, canonical, `${product}: deterministic fixture actually shuffles`);
  assert.equal(test.state().filters.sort, 'random');
  assert.equal(h.nodes.get('fSort').value, 'random', `${product}: restored preference is visible`);

  // No source mutation, renumbering, answer mutation, or shuffle while opening UI.
  h.ctx.UI.openFilters();
  assert.deepEqual(plain(test.visible()), randomOrder);
  assert.deepEqual(plain(test.metadata()), initialMetadata);
  assert.deepEqual(plain(test.state().answers), initialAnswers);
  test.applyFilters();
  assert.deepEqual(plain(test.visible()), randomOrder, `${product}: passive rebuild preserves the shuffled pool`);

  const visited = [];
  await test.render();
  for (let i = 0; i < randomOrder.length; i++) {
    visited.push(test.current());
    h.ctx.NAV.next();
    await flush();
  }
  assert.deepEqual(visited, randomOrder, `${product}: Next visits each item in the random pool`);
  assert.equal(test.current(), randomOrder.at(-1), `${product}: end remains bounded`);
  h.ctx.NAV.prev(); await flush();
  assert.equal(test.current(), randomOrder.at(-2), `${product}: Previous returns to the prior random item`);
  const jump = initialMetadata.find(row => h.key(row) === randomOrder[3]);
  await h.ctx.NAV.jumpToQid(jump.qid);
  assert.equal(test.current(), h.key(jump), `${product}: Navigator still uses stable question identity`);
  assert.equal(h.nodes.get('qTitle').textContent, `Question ${jump.global_number}`, `${product}: label remains canonical, not pool position`);
  assert.deepEqual(plain(test.metadata()), initialMetadata);
  assert.deepEqual(plain(test.state().answers), initialAnswers);

  h.restore({ filters: {}, answers: plain(initialAnswers) });
  await flush();
  assert.deepEqual(plain(test.visible()), randomOrder, `${product}: cloud restore does not reshuffle`);
  assert.equal(test.current(), h.key(jump), `${product}: cloud restore preserves active identity`);

  const predicates = {
    all: () => true,
    unseen: a => !a.selected,
    attempted: a => !!a.selected,
    correct: a => !!(a.checked && a.isCorrect),
    incorrect: a => !!(a.checked && !a.isCorrect),
    flagged: a => !!a.flagged,
  };
  const cases = Object.keys(predicates).map(status => defaultFilters({ status }));
  cases.push(defaultFilters({ papers: [initialMetadata[0].paper] }));
  cases.push(defaultFilters({ difficulties: ['4', '5'] }));
  const focus = initialMetadata.find(row => initialAnswers[h.key(row)]?.flagged);
  cases.push(defaultFilters({ topics: [test.topicKey(focus)] }));
  cases.push(defaultFilters({ papers: [focus.paper], topics: [test.topicKey(focus)], difficulties: [String(focus.difficulty)], status: 'flagged' }));
  for (const filters of cases) {
    test.replaceFilters(filters);
    const expected = initialMetadata.filter(row =>
      (!filters.papers.length || filters.papers.includes(row.paper)) &&
      (!filters.topics.length || filters.topics.includes(test.topicKey(row))) &&
      (!filters.difficulties.length || filters.difficulties.includes(String(row.difficulty))) &&
      predicates[filters.status](initialAnswers[h.key(row)] || {})
    ).map(h.key);
    assert.deepEqual([...plain(test.visible())].sort(), [...expected].sort(), `${product}: random respects ${JSON.stringify(filters)}`);
    assert.equal(new Set(plain(test.visible())).size, expected.length);
  }
  if (product.startsWith('esat')) {
    const sameTopic = initialMetadata.filter(row => row.topic === '1_Algebra & Functions');
    const m1 = sameTopic.find(row => row.paper === 'ESAT Mathematics 1');
    const m2 = sameTopic.find(row => row.paper === 'ESAT Mathematics 2');
    assert.notEqual(test.topicKey(m1), test.topicKey(m2), 'ESAT Maths 1 and 2 topic keys stay distinct');
    test.replaceFilters(defaultFilters({ topics: [test.topicKey(m1)] }));
    assert.ok(test.visibleMeta().every(row => row.paper === 'ESAT Mathematics 1'), 'ESAT topic filter never leaks matching name from Maths 2');
  }

  test.replaceFilters(defaultFilters({ papers: ['no-such-paper'] }));
  assert.deepEqual(plain(test.visible()), [], `${product}: empty pool is safe`);
  h.ctx.NAV.next(); h.ctx.NAV.prev(); await flush();
  assert.equal(test.current(), '');
  test.replaceFilters(defaultFilters({ papers: [focus.paper], topics: [test.topicKey(focus)], difficulties: [String(focus.difficulty)], status: 'flagged' }));
  assert.equal(test.visible().length, 1, `${product}: singleton pool stays usable`);
  const single = test.current();
  h.ctx.NAV.next(); h.ctx.NAV.prev(); await flush();
  assert.equal(test.current(), single);

  // Applying Random explicitly creates a new traversal; passive restoration did not.
  h.ui(defaultFilters()); h.random(0); h.ctx.STATE.applyFilters(); await flush();
  const firstApply = plain(test.visible());
  h.random(0.999999); h.ctx.STATE.applyFilters(); await flush();
  const secondApply = plain(test.visible());
  assert.notDeepEqual(secondApply, firstApply, `${product}: Apply Random reshuffles rather than reusing stale order`);
  assert.deepEqual([...secondApply].sort(), [...canonical].sort());
  assert.equal(JSON.parse(h.storage.get(h.storageKey)).filters.sort, 'random', `${product}: preference is persisted with normal filters`);
  assert.deepEqual(plain(test.state().answers), initialAnswers);
  assert.deepEqual(plain(test.metadata()), initialMetadata);

  // Existing non-random ordering must not be expanded or changed in this feature.
  for (const sort of ['topic', 'difficulty']) {
    test.replaceFilters(defaultFilters({ sort }));
    assert.deepEqual(plain(test.visible()), canonical, `${product}: legacy ${sort} order is preserved`);
  }
  h.ctx.STATE.clearFilters(); await flush();
  assert.equal(test.state().filters.sort, 'topic');
  assert.equal(h.nodes.get('fSort').value, 'topic', `${product}: Clear All resets visible sort too`);
  assert.deepEqual(plain(test.visible()), canonical);
  assert.deepEqual(plain(test.state().answers), initialAnswers);
  assert.deepEqual(h.errors, [], `${product}: no runtime errors`);
  assert.ok(h.requests.every(url => url.includes('public_question')), `${product}: ordering never submits progress, scores, or answers`);

  const malformed = harness(product, defaultFilters({ sort: 'injected-or-unknown-mode' }));
  assert.equal(malformed.ctx.randomPoolTest.state().filters.sort, 'topic', `${product}: invalid saved sort safely defaults`);
  assert.equal(malformed.nodes.get('fSort').value, 'topic');
  const legacy = harness(product, { status: 'all', papers: [], topics: [], difficulties: [] });
  assert.equal(legacy.ctx.randomPoolTest.state().filters.sort, 'topic', `${product}: legacy state gains safe default`);
}

console.log('PASS: TMUA/ESAT Random pools retain all active filters, stable identities, navigation/history, progress and numbering; passive sync preserves order while Apply reshuffles, with safe reset and saved preferences.');
