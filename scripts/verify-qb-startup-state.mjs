import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

// Run the actual page controller: the initial compact-sync placeholder used to
// replace default filters with {}, making the first metadata render throw.
const plain = value => JSON.parse(JSON.stringify(value));
const flush = async () => { for (let i = 0; i < 30; i++) await Promise.resolve(); };

function harness(product, saved, holdMetadata = false, holdQuestion = false) {
  const html = readFileSync(`public/${product}/index.html`, 'utf8');
  const source = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g)]
    .map(match => match[1]).find(script => script.includes('let allMeta = []'));
  assert.ok(source, `${product}: main page controller exists`);
  const esat = product === 'esat-question-bank';
  const storageKey = esat ? 'ts_esat_supabase_exact_ui_v1' : 'ts_tmua_supabase_exact_ui_v4';
  const storage = new Map([[storageKey, typeof saved === 'string' ? saved : JSON.stringify(saved)]]);
  const listeners = new Map();
  const errors = [];
  function node() {
    const attributes = new Map();
    const handlers = new Map();
    return {
      textContent: '', innerHTML: '', value: '', hidden: false,
      setAttribute: (name, value) => attributes.set(name, String(value)),
      getAttribute: name => attributes.get(name),
      addEventListener: (name, handler) => handlers.set(name, handler),
      click: () => handlers.get('click')?.(),
    };
  }
  const nodes = new Map(['qTitle', 'qPrompt', 'importText', 'qbStartup', 'qbStartupTitle', 'qbStartupCopy', 'qbStartupRetry']
    .map(id => [id, node()]));
  const body = node();
  body.setAttribute('data-qb-phase', 'loading');
  const rows = [
    { id: 'first', qid: 'ESAT-M1-0001', display_order: 301, paper: esat ? 'ESAT Mathematics 1' : 'Paper 1', topic: '1_Algebra & Functions', difficulty: 3 },
    { id: 'second', qid: 'ESAT-PHY-0001', display_order: 904, paper: esat ? 'ESAT Physics' : 'Paper 2', topic: esat ? 'P1. Electricity' : '4_Graphs', difficulty: 4 },
  ];
  let releaseMetadata;
  const metadataGate = holdMetadata ? new Promise(resolve => { releaseMetadata = resolve; }) : Promise.resolve();
  let releaseQuestion;
  const questionGate = holdQuestion ? new Promise(resolve => { releaseQuestion = resolve; }) : Promise.resolve();
  let metadataFailure = false;
  const response = value => ({ ok: true, status: 200, json: async () => plain(value), text: async () => JSON.stringify(value) });
  const addEventListener = (name, callback) => {
    const handlers = listeners.get(name) || [];
    handlers.push(callback);
    listeners.set(name, handlers);
  };
  const ctx = vm.createContext({
    console: { log() {}, warn() {}, error: error => errors.push(error) },
    setTimeout: () => 1, clearTimeout() {}, setInterval: () => 1, clearInterval() {},
    addEventListener,
    dispatchEvent: event => { for (const handler of listeners.get(event.type) || []) handler(event); },
    Event: class { constructor(type) { this.type = type; } },
    CustomEvent: class { constructor(type, options) { this.type = type; this.detail = options.detail; } },
    localStorage: { getItem: key => storage.get(key) || null, setItem: (key, value) => storage.set(key, String(value)) },
    document: { body, addEventListener() {}, getElementById: id => nodes.get(id) || null, querySelectorAll: () => [] },
    fetch: async (url, init) => {
      if (String(url).includes('list')) {
        await metadataGate;
        if (metadataFailure) throw new Error('Private diagnostic: TypeError at applyFilters line 3352');
        return response(esat ? { ok: true, questions: rows } : rows);
      }
      if (String(url).includes('/progress/load')) return response({ ok: true, progress: {} });
      if (String(url).includes('public_question')) {
        await questionGate;
        const body = JSON.parse(init.body);
        const row = rows.find(item => esat ? item.id === body.id : item.display_order === body.p_display_order);
        assert.ok(row, `${product}: loads the canonical question`);
        return response({ ...row, options: [], prompt_html: '<p>Test question</p>', answer: 'A' });
      }
      throw new Error(`Unexpected request: ${url}`);
    },
    alert() {}, confirm: () => false,
  });
  ctx.window = ctx;
  vm.runInContext(source.replace(/\}\)\(\);\s*$/, `
    window.startupTest = {
      boot, loadState, applyFilters,
      state: () => state,
      visible: () => visibleList.map(questionKey),
      current: () => questionKey(currentMeta())
    };
  })();`), ctx);
  return { ctx, rows, nodes, body, errors, storage, storageKey, releaseMetadata, releaseQuestion,
    failMetadata: value => { metadataFailure = value; },
    restore: state => ctx.dispatchEvent({ type: 'ts-qb-state-restored', detail: { product, state } }) };
}

for (const product of ['tmua-question-bank', 'esat-question-bank']) {
  const firstKey = product.startsWith('tmua') ? '301' : 'ESAT-M1-0001';
  const secondKey = product.startsWith('tmua') ? '904' : 'ESAT-PHY-0001';
  const answer = { selected: 'A', checked: false, flagged: true, time_spent: 41 };
  for (const filters of [{}, { difficulties: ['3'] }, null, { papers: null, topics: {}, difficulties: '3' }]) {
    const h = harness(product, { answers: { [firstKey]: answer }, filters });
    await h.ctx.startupTest.boot();
    assert.deepEqual(h.errors, [], `${product}: startup never exposes an exception for partial filters`);
    assert.equal(h.nodes.get('qTitle').textContent, 'Question 1');
    assert.equal(h.body.getAttribute('data-qb-phase'), 'ready');
    assert.equal(h.nodes.get('qbStartup').getAttribute('aria-busy'), 'false');
    assert.equal(h.nodes.get('qbStartupRetry').hidden, true);
    assert.equal(h.ctx.startupTest.current(), firstKey);
    assert.deepEqual(plain(h.ctx.startupTest.state().answers[firstKey]), answer);
    const normalized = h.ctx.startupTest.state().filters;
    for (const key of ['papers', 'topics', 'difficulties']) assert.ok(Array.isArray(normalized[key]));
    assert.equal(normalized.status, 'all');
    if (filters?.difficulties?.[0] === '3' && Array.isArray(filters.difficulties)) {
      assert.deepEqual(plain(h.ctx.startupTest.visible()), [firstKey], 'A valid saved filter still applies');
    }
  }

  const malformed = harness(product, '{bad json');
  await malformed.ctx.startupTest.boot();
  assert.deepEqual(malformed.errors, []);
  assert.equal(malformed.nodes.get('qTitle').textContent, 'Question 1');

  // Cloud restoration may finish before metadata: retain its selections and
  // progress, then render the chosen subject after the pending list resolves.
  const race = harness(product, { answers: {}, filters: {} }, true);
  const booting = race.ctx.startupTest.boot();
  assert.equal(race.body.getAttribute('data-qb-phase'), 'loading');
  assert.equal(race.nodes.get('qbStartup').getAttribute('aria-busy'), 'true');
  race.restore({ answers: { [secondKey]: answer }, filters: { papers: [race.rows[1].paper] } });
  race.releaseMetadata();
  await booting;
  assert.deepEqual(race.errors, []);
  assert.deepEqual(plain(race.ctx.startupTest.visible()), [secondKey]);
  assert.equal(race.ctx.startupTest.current(), secondKey);
  assert.deepEqual(plain(race.ctx.startupTest.state().answers[secondKey]), answer);
  assert.equal(race.body.getAttribute('data-qb-phase'), 'ready');

  // A partial restored snapshot must not erase another valid filter or the
  // current question. Malformed fields fall back to known good values.
  race.restore({ filters: { status: 'flagged', topics: null } });
  await flush();
  assert.deepEqual(plain(race.ctx.startupTest.visible()), [secondKey]);
  assert.equal(race.ctx.startupTest.current(), secondKey);
  assert.deepEqual(plain(race.ctx.startupTest.state().filters.papers), [race.rows[1].paper]);
  assert.deepEqual(plain(race.ctx.startupTest.state().answers[secondKey]), answer);

  const imported = harness(product, {});
  imported.nodes.get('importText').value = JSON.stringify({ answers: { [firstKey]: answer }, filters: { difficulties: ['3'] } });
  imported.ctx.STATE.importProgress();
  await flush();
  assert.deepEqual(plain(imported.ctx.startupTest.state().answers[firstKey]), answer);
  assert.deepEqual(plain(imported.ctx.startupTest.state().filters.papers), []);
  assert.deepEqual(plain(imported.ctx.startupTest.state().filters.difficulties), ['3']);

  // A completed metadata fetch is insufficient: keep the loading presentation
  // until the actual question has arrived and rendered.
  const delayed = harness(product, { answers: {}, filters: {} }, false, true);
  const loadingQuestion = delayed.ctx.startupTest.boot();
  await flush();
  assert.equal(delayed.body.getAttribute('data-qb-phase'), 'loading');
  assert.equal(delayed.nodes.get('qbStartup').getAttribute('aria-busy'), 'true');
  assert.equal(delayed.nodes.get('qTitle').textContent, '');
  delayed.releaseQuestion();
  await loadingQuestion;
  assert.equal(delayed.body.getAttribute('data-qb-phase'), 'ready');
  assert.equal(delayed.nodes.get('qTitle').textContent, 'Question 1');

  // A genuine service failure remains visible in friendly language; private
  // diagnostics stay in the console. The actual retry button re-runs boot.
  const recovery = harness(product, { answers: { [firstKey]: answer }, filters: {} });
  recovery.failMetadata(true);
  await recovery.ctx.startupTest.boot();
  assert.equal(recovery.body.getAttribute('data-qb-phase'), 'error');
  assert.equal(recovery.nodes.get('qbStartup').getAttribute('role'), 'alert');
  assert.equal(recovery.nodes.get('qbStartup').getAttribute('aria-busy'), 'false');
  assert.equal(recovery.nodes.get('qbStartupRetry').hidden, false);
  assert.match(recovery.nodes.get('qbStartupCopy').textContent, /Please try again/);
  assert.equal(recovery.errors.length, 1, 'Diagnostics are retained for troubleshooting');
  const displayed = [...recovery.nodes.values()].map(item => item.textContent + item.innerHTML).join('\n');
  assert.doesNotMatch(displayed, /Private diagnostic|TypeError|applyFilters|3352|Supabase/);
  recovery.failMetadata(false);
  const retrying = recovery.nodes.get('qbStartupRetry').click();
  assert.equal(recovery.body.getAttribute('data-qb-phase'), 'loading');
  assert.equal(recovery.nodes.get('qbStartupRetry').hidden, true);
  await retrying;
  assert.equal(recovery.body.getAttribute('data-qb-phase'), 'ready');
  assert.equal(recovery.nodes.get('qTitle').textContent, 'Question 1');
  assert.deepEqual(plain(recovery.ctx.startupTest.state().answers[firstKey]), answer);
}

console.log('PASS: TMUA and ESAT startup normalize partial state, preserve progress, stay loading until questions render, and recover through a friendly error and working retry button.');
