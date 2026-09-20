import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const html = readFileSync('public/esat-question-bank/index.html', 'utf8');
const start = html.indexOf('  async function hydrateCanonicalProgress()');
const end = html.indexOf('\n  function renderDifficultyLabel', start);
assert.ok(start >= 0 && end > start, 'Exercise the actual ESAT hydration function');
const source = html.slice(start, end);
const qid = 'ESAT-PHY-0001';
const local = selected => ({ selected, checked: true, isCorrect: selected === 'B', flagged: true });
const canonical = selected => ({ selected_answer: selected, status: selected === 'B' ? 'correct' : 'wrong', flagged: false });
const copy = value => JSON.parse(JSON.stringify(value));

function scenario(answers = {}, initialCompact = {}, initialUpdates = []) {
  let resolve, reject, saved = null;
  const request = new Promise((a, b) => { resolve = a; reject = b; });
  const pending = { compact: initialCompact, updates: initialUpdates };
  const context = vm.createContext({
    state: { answers: copy(answers) },
    allMeta: [{ qid, display_order: 1, original_index: 1 }],
    questionKey: meta => meta.qid,
    fetch: () => request,
    saveState: () => { saved = copy(context.state.answers); },
    window: {
      TS_QB_TRANSPORT: { pendingUpdates: product => { assert.equal(product, 'esat-question-bank'); return pending.updates; } },
      TS_QB_SYNC: { pendingAnswers: () => pending.compact },
    },
    console: { warn() {} },
  });
  vm.runInContext(source, context);
  const run = context.hydrateCanonicalProgress();
  return {
    context, pending, saved: () => saved,
    complete: async progress => {
      resolve({ ok: true, json: async () => ({ ok: true, progress }) });
      await run;
    },
    fail: async () => { reject(new Error('offline')); await run; },
  };
}

// A compact journal restore arriving during the GET must survive a stale response.
const restored = scenario();
restored.context.state.answers[qid] = local('B');
await restored.complete({ [qid]: canonical('A') });
assert.deepEqual(restored.saved()[qid], local('B'));

// Replay may acknowledge/remove a durable submission while an earlier GET returns.
// Keep the verified pending snapshot captured before that GET, even after removal.
const replay = scenario({ [qid]: local('A') }, {}, [{ question_id: qid, ...canonical('B') }]);
replay.pending.updates = [];
await replay.complete({ [qid]: canonical('A') });
assert.equal(replay.saved()[qid].selected, 'B');
assert.equal(replay.saved()[qid].checked, true);

// Compact-only pending edits also survive startup; unowned legacy data is never read.
const compact = scenario({}, { [qid]: local('B') });
compact.pending.compact = {};
await compact.complete({ [qid]: canonical('A') });
assert.deepEqual(compact.saved()[qid], local('B'));

// Unchanged local cache must not mask a more recent answer from another device.
const remote = scenario({ [qid]: local('A') });
await remote.complete({ [qid]: canonical('B') });
assert.equal(remote.saved()[qid].selected, 'B');
assert.equal(remote.saved()[qid].flagged, false);

// An answer queued by another tab during the GET is also preserved.
const late = scenario();
late.pending.updates = [{ question_id: qid, ...canonical('B') }];
await late.complete({ [qid]: canonical('A') });
assert.equal(late.saved()[qid].selected, 'B');

// Failed reads preserve newly restored/local answers rather than resetting completion.
const offline = scenario({ [qid]: local('A') });
offline.context.state.answers[qid] = local('B');
await offline.fail();
assert.deepEqual(offline.saved()[qid], local('B'));
console.log('PASS: ESAT startup preserves account-bound pending answers and in-flight edits while accepting newer canonical progress.');
