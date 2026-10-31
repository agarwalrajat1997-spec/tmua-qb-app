import assert from 'node:assert/strict';
import { readFileSync, existsSync, statSync } from 'node:fs';
import { registerHooks } from 'node:module';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import ts from 'typescript';

// A dependency-free Node runner for the copied TypeScript algorithms and transport.
registerHooks({
  resolve(specifier, context, next) {
    if (specifier.startsWith('.') && context.parentURL?.includes('/tmua-studio/')) {
      const candidate = new URL(`${specifier}.ts`, context.parentURL);
      if (existsSync(candidate)) return { url: candidate.href, shortCircuit: true };
    }
    return next(specifier, context);
  },
  load(url, context, next) {
    if (url.includes('/tmua-studio/') && url.endsWith('.ts')) {
      const source = ts.transpileModule(readFileSync(new URL(url), 'utf8'), {
        compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 },
        fileName: fileURLToPath(url),
      }).outputText;
      return { format: 'module', source, shortCircuit: true };
    }
    return next(url, context);
  },
});

const api = await import('./lib/api.ts');
const { consumeStudioOpen } = await import('./lib/embed-session.ts');
let history = { received: false };
let opened = consumeStudioOpen(history, 'q1', 'opening-one', 'tmua:q1@v1');
assert.equal(opened.revisit, false, 'First ready reply must not count as a second visit');
history = opened.history;
opened = consumeStudioOpen(history, 'q1', 'opening-one', 'tmua:q1@v1');
assert.equal(opened.revisit, false, 'Duplicate ready reply must not remount the notebook');
opened = consumeStudioOpen(opened.history, 'q1', 'opening-two', 'tmua:q1@v1');
assert.equal(opened.revisit, true, 'A real reopen of the same question is a new visit');
opened = consumeStudioOpen(opened.history, 'q2', 'opening-three', 'tmua:q1@v1');
assert.equal(opened.revisit, false, 'A different question uses its own normal mount');
const publicRoot = new URL('../../public/tmua-studio/', import.meta.url);
const assetManifest = JSON.parse(readFileSync(new URL('./data/studio-assets.json', import.meta.url), 'utf8'));
for (const asset of assetManifest.assets) {
  const bytes = readFileSync(new URL(asset.path, publicRoot));
  assert.equal(bytes.length, asset.bytes, `Studio asset truncated: ${asset.path}`);
  assert.equal(createHash('sha256').update(bytes).digest('hex'), asset.sha256, `Studio asset changed: ${asset.path}`);
}
const brandSource = readFileSync(new URL('./components/ThinkingBrand.tsx', import.meta.url), 'utf8');
for (const [file, type, magic] of [
  ['thinking.webm', 'video/webm', Buffer.from([0x1a, 0x45, 0xdf, 0xa3])],
  ['thinking.mp4', 'video/mp4', Buffer.from('ftyp')],
]) {
  const bytes = readFileSync(new URL(`brand/${file}`, publicRoot));
  assert.ok(bytes.length > 100_000, 'The real supplied animation must be present');
  assert.ok(bytes.subarray(0, 12).includes(magic), 'Animation container must match its declared type');
  assert.ok(brandSource.includes(`/tmua-studio/brand/${file}`) && brandSource.includes(type));
}
assert.ok(brandSource.includes('muted') && brandSource.includes('loop') && brandSource.includes('playsInline'));
assert.ok(brandSource.includes('prefers-reduced-motion'));
for (const file of ['brand/thinking.png', 'fonts/kalam/kalam-400.ttf', 'fonts/kalam/kalam-700.ttf',
  'vendor/mathjax/tex-svg.js', 'vendor/mathjax/ui/safe.js', 'vendor/mathjax/input/tex/extensions/mathtools.js', 'vendor/mathjax/newcm/svg.js']) {
  assert.ok(statSync(new URL(file, publicRoot)).size > 1000, `Required Studio asset missing: ${file}`);
}
const manifest = JSON.parse(readFileSync(new URL('./data/tmua-eligibility.json', import.meta.url), 'utf8'));
assert.equal(manifest.active_audit_ids.length, 2178);
assert.equal(new Set(manifest.active_audit_ids).size, 2178);
assert.equal(manifest.excluded_ids.length, 22);
const { ReviewNotAcceptedError } = await import('./lib/review-status.ts');
const calls = [];
let response;
const originalFetch = globalThis.fetch;
globalThis.fetch = async (input, init = {}) => { calls.push({ input, init }); return response; };
try {
  api.acceptStudioViewer('student-a');
  assert.throws(() => api.acceptStudioViewer('student-b'), /account changed/);
  response = Response.json({ correct: true });
  assert.equal((await api.checkAnswer('TS-TMUA-1', 'version-a', 'B')).correct, true);
  assert.equal(calls[0].input, '/api/tmua/studio');
  assert.equal(calls[0].init.credentials, 'same-origin');
  assert.equal(calls[0].init.headers['X-TS-Studio'], '1');
  assert.deepEqual(JSON.parse(calls[0].init.body), {
    action: 'answer', qid: 'TS-TMUA-1', contentVersion: 'version-a', answer: 'B', expectedUserId: 'student-a',
  });
  const requestId = '22222222-2222-4222-8222-222222222222';
  for (const status of [409, 429, 503]) {
    response = Response.json({ accepted: false, code: 'review_not_accepted', requestId, error: 'Wait before retrying.' }, { status });
    const before = calls.length;
    await assert.rejects(api.checkWorking({ requestId, qid: 'TS-TMUA-1', contentVersion: 'version-a' }), ReviewNotAcceptedError);
    assert.equal(calls.length, before + 1, 'Preacceptance rejection must not resubmit a paid request');
  }
  response = Response.json({ accepted: false, code: 'review_not_accepted', requestId: 'different-request', error: 'Unavailable' }, { status: 503 });
  await assert.rejects(api.checkWorking({ requestId }), error => !(error instanceof ReviewNotAcceptedError));
  response = Response.json({ error: 'Unavailable' }, { status: 503 });
  await assert.rejects(api.checkWorking({ requestId }), error => !(error instanceof ReviewNotAcceptedError));
  response = Response.json({ status: 'pending' });
  await api.recoverReview(requestId);
  const last = calls.at(-1);
  assert.equal(last.init.method, undefined, 'Recovery must be a read');
  assert.match(last.input, /action=review-status/);
  assert.match(last.input, /expectedUserId=student-a/);
  response = Response.json({ viewerId: 'student-b', question: {} });
  await assert.rejects(api.fetchStudioQuestion('TS-TMUA-1'), /account changed/);
} finally { globalThis.fetch = originalFetch; }

const { createNotebookStore } = await import('./lib/notebook-store.ts');
const { emptyBoard } = await import('./types.ts');
const stored = new Map(), boards = new Map(), reviews = new Map();
let release;
const finished = new Promise(resolve => { release = resolve; });
let assessmentCalls = 0;
const feedback = { revision: 1, summary: 'Valid method.', lines: [], firstErrorLine: null, nextStep: 'Check the domain.' };
const store = createNotebookStore({
  read: async key => stored.get(key), write: async (key, value) => stored.set(key, structuredClone(value)),
  loadBoard: async key => boards.get(key), saveBoard: async (key, value) => boards.set(key, structuredClone(value)),
  loadReview: async key => reviews.get(key), saveReview: async (key, value) => reviews.set(key, structuredClone(value)),
  hash: async () => 'hash-one', assess: async () => { assessmentCalls++; await finished; return feedback; },
  solution: async () => ({ qid: 'q1', answer: 'B', solutionHtml: '<p>Reviewed solution</p>', shortcuts: [] }),
});
const scopeA = 'user:student-a:practice:tmua:q1@version-a';
const scopeB = 'user:student-b:practice:tmua:q1@version-a';
const context = { exam: 'tmua', qid: 'q1', contentVersion: 'version-a' };
await store.open(scopeA, 'entry-a', context);
await store.open(scopeA, 'entry-a', context);
assert.equal(store.get(scopeA).visits, 1, 'StrictMode entry does not create duplicate visits');
await assert.rejects(store.fresh(scopeA), /revisit/);
await store.open(scopeB, 'entry-b', context);
const pad = store.get(scopeA).pads[0];
const snapshot = { board: { ...emptyBoard(), note: 'Original student working', revision: 1 }, image: '', hash: 'hash-one',
  capture: { x: 0, y: 0, w: 1200, h: 900 }, regions: [], groups: [], structure: { steps: [] } };
const submission = store.submit(scopeA, pad.id, async () => structuredClone(snapshot), context);
for (let i = 0; i < 100 && assessmentCalls === 0; i++) await new Promise(resolve => setImmediate(resolve));
assert.equal(assessmentCalls, 1);
await store.submit(scopeA, pad.id, async () => { throw Error('Duplicate capture'); }, context);
assert.equal(assessmentCalls, 1, 'Second click cannot create a duplicate accepted review');
assert.equal(store.get(scopeB).pads[0].status, 'draft', 'Another student keeps a separate notebook');
release();
await submission;
assert.equal(store.get(scopeA).pads[0].status, 'complete');
assert.equal(store.get(scopeA).pads[0].feedback.source.hash, 'hash-one');
assert.equal(store.get(scopeB).pads[0].feedback, undefined);
await store.open(scopeA, 'entry-a-revisit', context);
await store.fresh(scopeA);
assert.equal(store.get(scopeA).pads.length, 2);
assert.equal(store.get(scopeA).pads[0].status, 'complete', 'Fresh pad preserves the submitted original');

const { eraseInk, strokeGeometry } = await import('./lib/ink-geometry.ts');
const stroke = { id: 'line', points: [[20,100,.5],[300,100,.5]], size: 6, color: '#172033', tool: 'pen', renderVersion: 2 };
const original = structuredClone(stroke);
const erased = eraseInk([stroke], [160,90,.5], [160,110,.5], 4);
assert.deepEqual(stroke, original, 'Erasing does not modify the saved original stroke');
assert.ok(strokeGeometry(erased[0]).length >= 2, 'Precise erasing retains both sides of a line');

console.log(`Studio verification passed: ${assetManifest.assets.length} complete assets, real animation containers/types, eligible-bank manifest, iframe handshake, cookie transport, identity binding, review recovery, duplicate prevention, notebook separation, saved pads, precise erasing. No live API calls.`);
