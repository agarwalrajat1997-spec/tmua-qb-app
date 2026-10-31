import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

const source = pathToFileURL(resolve('lib/tmua-bank-client.ts')).href;
let instance = 0;
const fresh = () => import(`${source}?test=${++instance}`);
const json = (value, status = 200) => new Response(JSON.stringify(value), { status, headers: { 'Content-Type': 'application/json' } });
const storage = new Map();
globalThis.localStorage = {
  get length() { return storage.size; }, key: i => [...storage.keys()][i] ?? null,
  getItem: key => storage.get(key) ?? null, setItem: (key, value) => storage.set(key, String(value)),
  removeItem: key => storage.delete(key),
};
const q = (qid, display_order, difficulty, topic = '1_Algebra') => ({ qid, display_order, difficulty, topic,
  subtopic: 'Equations', paper: '1', content_version: 'v1' });
const questions = [q('TMUA-P1-HARD', 397, 5), q('TMUA-P1-EASY', 1824, 1), q('TMUA-TS-A-P1-Q6', 2074, 2)];
questions[2].audit_qid = 'TMUA-JZ-A-P1-Q6';
const emptyNetwork = async (_url, init) => init?.body
  ? json({ ok: true, saved: { user_id: 'A' } })
  : json({ ok: true, user_id: 'A', progress: {}, data: { parsed: { answers: {} } } });
const pendingKeys = () => [...storage.keys()].filter(key => key.includes(':pending:'));

// Difficulty is a presentation sort; original objects and stable IDs are intact.
let api = await fresh();
const extended = [...questions, q('TMUA-P1-T10', 3, 1, '10_Miscellaneous'), q('TMUA-P1-T2', 8, 5, '2_Sequences')];
const original = JSON.stringify(extended);
assert.deepEqual(api.sortQuestions(extended).map(x => x.display_order), [1824, 2074, 397, 8, 3]);
assert.equal(JSON.stringify(extended), original);
assert.equal(api.sortQuestions(questions)[0], questions[1]);

// Earlier numeric progress saved under a UI position must not become a false
// completion. Explicit stable rows and original canonical/audit aliases do merge.
const merged = api.mergeProgressSources(questions, {
  397: { status: 'correct', selected_answer: 'H', updated_at: '2026-10-31T12:00:00Z' },
  1824: { status: 'wrong', selected_answer: 'C', flagged: true,
    submission_id: 'tmua-stable-v1|1824|answer', updated_at: '2026-10-31T12:00:00Z' },
  'TMUA-JZ-A-P1-Q6': { status: 'correct', selected_answer: 'B', updated_at: '2026-10-31T11:00:00Z' },
}, { parsed: { answers: {
  'SB-1824': { selected: 'B', checked: true, isCorrect: true, flagged: false, updated_at: '2026-10-30T12:00:00Z' },
  'TMUA-TS-A-P1-Q6': { selected: 'D', checked: true, isCorrect: false, updated_at: '2026-10-31T13:00:00Z' },
} } });
assert.equal(merged['TMUA-P1-HARD'], undefined);
assert.equal(merged['TMUA-P1-EASY'].selected_answer, 'C');
assert.equal(merged['TMUA-P1-EASY'].status, 'wrong');
assert.equal(merged['TMUA-P1-EASY'].flagged, true);
assert.equal(merged['TMUA-TS-A-P1-Q6'].selected_answer, 'D');
const removedBookmark = api.mergeProgressSources(questions, {
  1824: { flagged: true, status: 'correct', selected_answer: 'A', submission_id: 'tmua-stable-v1|1824|old', updated_at: '2026-10-31T13:00:00Z' },
}, { parsed: { answers: { '1824': { flagged: false, selected: 'A', checked: true, isCorrect: true },
  'TMUA-TS-A-P1-Q6': { selected: 'NEW', flagged: false }, 'TMUA-JZ-A-P1-Q6': { selected: 'OLD', flagged: true } } } });
assert.equal(removedBookmark['TMUA-P1-EASY'].flagged, false);
assert.equal(removedBookmark['TMUA-TS-A-P1-Q6'].selected_answer, 'NEW');

// Writes use 1824 rather than the first card's position or qid; the compact delta
// updates one answer and retains unrelated older fields without solution blobs.
const writes = [];
globalThis.fetch = async (url, init) => {
  if (init?.body) { writes.push({ url, body: JSON.parse(init.body) }); return json({ ok: true, saved: { user_id: 'A' } }); }
  return json({ ok: true, user_id: 'A', progress: {}, data: { parsed: { answers: {
    '1824': { selected: 'B', checked: true, isCorrect: true, customNote: 'retain this', solution_html: 'large old solution' },
    '397': { selected: 'A', checked: true, isCorrect: true },
  } } } });
};
await api.loadProgress('A', questions);
const saved = await api.saveQuestionProgress('A', questions[1], { flagged: true });
assert.equal(saved.syncState, 'synced');
assert.equal(writes.length, 2);
assert.equal(writes[0].body.expected_user_id, 'A');
assert.equal(writes[0].body.identity_version, 'tmua-display-order-v1');
assert.equal(writes[0].body.updates[0].question_id, '1824');
assert.equal(writes[0].body.updates[0].selected_answer, 'B');
assert.deepEqual(Object.keys(writes[1].body.patch.answers), ['1824']);
assert.equal(writes[1].body.patch.answers['1824'].customNote, 'retain this');
assert.equal(writes[1].body.patch.answers['1824'].solution_html, undefined);
assert.equal(pendingKeys().length, 0);

// A failed compact mirror does not resend the already acknowledged submission.
storage.clear(); api = await fresh(); let canonicalSaves = 0, mirrorDown = true;
globalThis.fetch = async (url, init) => {
  if (!init?.body) return emptyNetwork(url, init);
  if (url.endsWith('/progress/save')) { canonicalSaves++; return json({ ok: true }); }
  return mirrorDown ? json({ error: 'temporarily unavailable' }, 503) : json({ ok: true, saved: { user_id: 'A' } });
};
await api.loadProgress('A', questions);
assert.equal((await api.saveQuestionProgress('A', questions[1], { status: 'correct', selected_answer: 'E',
  answer_elapsed_seconds: 37, answer_submitted_at: '2026-10-31T13:00:00Z', submission_id: 'tmua-stable-v1|1824|unique' })).syncState, 'offline');
assert.equal(canonicalSaves, 1); assert.equal(pendingKeys().length, 1);
mirrorDown = false;
api = await fresh();
const recovered = await api.loadProgress('A', questions);
assert.equal(recovered.progress['TMUA-P1-EASY'].selected_answer, 'E');
assert.equal(recovered.progress['TMUA-P1-EASY'].answer_elapsed_seconds, 37);
assert.equal(canonicalSaves, 1); assert.equal(pendingKeys().length, 0);

// Edits made while a save is in flight remain separately journaled and delivered.
storage.clear(); api = await fresh(); let release;
const slow = new Promise(resolve => { release = resolve; }); const deliveries = [];
globalThis.fetch = async (url, init) => {
  if (!init?.body) return emptyNetwork(url, init);
  const body = JSON.parse(init.body);
  if (url.endsWith('/progress/save')) {
    deliveries.push(body.updates[0]); if (deliveries.length === 1) await slow;
  }
  return json({ ok: true, saved: { user_id: 'A' } });
};
await api.loadProgress('A', questions);
const one = api.saveQuestionProgress('A', questions[1], { status: 'wrong', selected_answer: 'A', submission_id: 'tmua-stable-v1|1824|first' });
await new Promise(resolve => setTimeout(resolve, 0));
const two = api.saveQuestionProgress('A', questions[1], { status: 'correct', selected_answer: 'B', submission_id: 'tmua-stable-v1|1824|second' });
assert.equal(pendingKeys().length, 2);
release(); await Promise.all([one, two]);
assert.deepEqual(deliveries.map(x => x.selected_answer), ['A', 'B']); assert.equal(pendingKeys().length, 0);

// Another signed-in account can never receive or replay the first account's work.
storage.clear(); api = await fresh(); globalThis.fetch = async () => json({ error: 'down' }, 503);
await api.saveQuestionProgress('A', questions[1], { selected_answer: 'SECRET-A', status: 'wrong' });
const aJournals = pendingKeys().length;
globalThis.fetch = async (_url, init) => { assert.equal(init?.body, undefined); return json({ ok: true, user_id: 'B', progress: {}, data: { parsed: { answers: {} } } }); };
const other = await api.loadProgress('B', questions);
assert.equal(other.progress['TMUA-P1-EASY'], undefined); assert.equal(pendingKeys().length, aJournals);
await assert.rejects(api.loadProgress('A', questions), error => error.code === 'ACCOUNT_CHANGED');
let badPosts = 0; globalThis.fetch = async () => { badPosts++; return json({ ok: true }); };
await assert.rejects(api.saveQuestionProgress('A', questions[1], { flagged: true }), error => error.code === 'ACCOUNT_CHANGED');
assert.equal(badPosts, 0);

// A 409 received mid-save retains the journal and pauses further submissions.
api = await fresh(); globalThis.fetch = async () => json({ ok: false, code: 'ACCOUNT_CHANGED' }, 409);
await assert.rejects(api.saveQuestionProgress('C', questions[0], { selected_answer: 'A' }), error => error.code === 'ACCOUNT_CHANGED');
assert.ok(pendingKeys().some(key => key.includes(':C:')));

// Only an owner-labelled legacy journal migrates; unowned local history remains
// untouched and can never be assigned to a new student.
storage.clear(); api = await fresh(); const oldKey = 'ts_tmua_supabase_exact_ui_v4';
const unowned = JSON.stringify({ answers: { '397': { selected: 'DO-NOT-IMPORT', checked: true } } });
storage.set(oldKey, unowned);
storage.set(oldKey + '__account_v3:A:pending:old-tab', JSON.stringify({ at: Date.now(), patch: { answers: { 'SB-1824': { selected: 'F', checked: true, isCorrect: true } } } }));
const imported = [];
globalThis.fetch = async (url, init) => { if (init?.body) imported.push(JSON.parse(init.body)); return emptyNetwork(url, init); };
const legacy = await api.loadProgress('A', questions);
assert.equal(legacy.progress['TMUA-P1-EASY'].selected_answer, 'F');
assert.equal(legacy.progress['TMUA-P1-HARD'], undefined);
assert.equal(storage.get(oldKey), unowned);
assert.equal(imported[0].updates[0].question_id, '1824');
assert.equal(imported.length, 2); await api.loadProgress('A', questions); assert.equal(imported.length, 2);

// A blocked/full browser store does not break online saving and is never
// described as a durable on-device copy.
storage.clear(); api = await fresh();
const originalSet = globalThis.localStorage.setItem;
globalThis.localStorage.setItem = () => { throw new Error('QuotaExceededError'); };
globalThis.fetch = emptyNetwork;
const noStorage = await api.saveQuestionProgress('A', questions[1], { flagged: false });
assert.equal(noStorage.syncState, 'synced'); assert.match(noStorage.warnings.join(' '), /cannot keep a durable offline copy/);
globalThis.localStorage.setItem = originalSet;

console.log('PASS: TMUA difficulty ordering, stable aliases, ambiguous legacy isolation, preserved history, per-account outbox, offline reload, partial acknowledgements, in-flight edits and account changes.');
