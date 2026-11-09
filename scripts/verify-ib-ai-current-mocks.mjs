import assert from 'node:assert/strict';
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import katex from 'katex';
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import { ibHarness } from './ib-component-harness.mjs';

const infrastructureOnly = process.argv.includes('--infrastructure-only');
assert.ok(process.argv.slice(2).every(v => v === '--infrastructure-only'), 'Unknown verification argument');
const h = ibHarness(), m = h.load('lib/ib/maths-mock-model.ts'), server = h.load('lib/ib/maths-mocks.ts');
const { MATHS_MOCKS, AI_MATHS_MOCKS, ALL_MATHS_MOCKS, getMathsMock, mathsStrand, mathsStrandName, mathsSubject,
  mathsAnswerKey, mathsPdfUrl, mathsReportPayload, cleanMathsAnswers, validateMathsMarks, scoreMathsMock, restoreMathsMockDraft, mathsSecondsRemaining } = m;
const normal = value => JSON.parse(JSON.stringify(value));
const expectedIds = ['a', 'b', 'c', 'd'].flatMap(s => ['1', '2', '3'].map(p => `ai-hl-set-${s}-paper-${p}`));
assert.deepEqual(normal(AI_MATHS_MOCKS.map(p => p.id)), expectedIds);
assert.equal(ALL_MATHS_MOCKS.length, 26); assert.equal(new Set(ALL_MATHS_MOCKS.map(p => p.id)).size, 26);
assert.equal(MATHS_MOCKS.length, 10); assert.equal(MATHS_MOCKS.reduce((s, p) => s + p.questionCount, 0), 90);
assert.equal(AI_MATHS_MOCKS.reduce((s, p) => s + p.questionCount, 0), 96);
assert.equal(AI_MATHS_MOCKS.reduce((s, p) => s + p.marks, 0), 1100);
assert.equal(mathsSubject('hl', 'ai'), 'math-ai-hl'); assert.equal(mathsSubject('hl'), 'math-aa-hl');
assert.equal(mathsStrand(MATHS_MOCKS[0]), 'aa'); assert.equal(mathsStrandName(AI_MATHS_MOCKS[0]), 'Applications and interpretation');
for (const id of ['ai-sl-set-a-paper-3', 'ai-hl-set-e-paper-1']) assert.equal(getMathsMock(id), undefined);

function fixture(meta) {
  const base = Math.floor(meta.marks / meta.questionCount), remainder = meta.marks % meta.questionCount;
  return { ...meta, questions: Array.from({ length: meta.questionCount }, (_, index) => {
    const marks = base + Number(index < remainder);
    return { number: index + 1, section: '', marks, stem: 'Isolated API fixture, not publication content.',
      parts: [{ label: 'a', prompt: 'Give the result.', marks }], syllabusRefs: ['AI HL fixture'], cognitiveDemand: 'Reason and interpret',
      answerSummary: 'PRIVATE_AI_ANSWER_CANARY', markScheme: [{ part: 'a', steps: [{ code: `A${marks}`, text: 'PRIVATE_AI_SCHEME_CANARY' }] }],
      ...(index === 0 ? { diagramSvg: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="M0 0L100 100"/></svg>' } : {}) };
  }) };
}
const fixturePapers = new Map();
for (const meta of AI_MATHS_MOCKS) {
  assert.equal(meta.strand, 'ai'); assert.equal(meta.course, 'hl'); assert.equal(meta.year, meta.paper === '3' && ['C','D'].includes(meta.set) ? 2027 : 2026); assert.equal(meta.status, 'published');
  assert.equal(meta.calculator, true); assert.deepEqual(normal(meta.sections), []);
  assert.equal(meta.minutes, meta.paper === '3' ? 75 : 120); assert.equal(meta.marks, meta.paper === '3' ? 55 : 110);
  assert.equal(meta.questionCount, meta.paper === '1' ? 16 : meta.paper === '2' ? 6 : 2);
  const paper = server.validateMathsMockPaper(fixture(meta), meta); fixturePapers.set(meta.id, paper);
  const prompt = server.mathsMockPrompt(paper, meta);
  assert.equal(prompt.strand, 'ai'); assert.equal(prompt.questions[0].section, '');
  assert.doesNotMatch(JSON.stringify(prompt), /PRIVATE_AI_|markScheme|answerSummary|diagramSvg/);
  assert.match(prompt.questions[0].diagramUrl, /^data:image\/svg\+xml;base64,/);
  for (const patch of [{ strand: 'aa' }, { course: 'sl' }, { calculator: false }]) assert.throws(() => server.validateMathsMockPaper({ ...paper, ...patch }, meta));
  const bad = normal(paper); bad.questions[0].section = 'A'; assert.throws(() => server.validateMathsMockPaper(bad, meta));
  const badMarks = normal(paper); badMarks.questions[0].markScheme[0].steps[0].code = 'M1'; assert.throws(() => server.validateMathsMockPaper(badMarks, meta));
  const unsafe = normal(paper); unsafe.questions[0].diagramSvg = '<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'; assert.throws(() => server.validateMathsMockPaper(unsafe, meta));
  const marks = Object.fromEntries(paper.questions.flatMap(q => q.parts.map(p => [mathsAnswerKey(q.number, p.label), p.marks])));
  assert.equal(scoreMathsMock(paper.questions, validateMathsMarks(paper.questions, marks)).total, meta.marks);
  assert.equal(scoreMathsMock(paper.questions, null).total, null);
  for (const value of [-1, 999, 0.5, '1']) assert.throws(() => validateMathsMarks(paper.questions, { ...marks, '1:a': value }));
  assert.throws(() => cleanMathsAnswers(paper.questions, { '1:a': 'x'.repeat(12001) }));
  const draft = { version: 1, attemptId: '22222222-2222-4222-8222-222222222222', name: 'Student', startedAt: 100000,
    deadline: 100000 + meta.minutes * 60000, elapsed: 0, stage: 'running', index: 0, answers: {}, flags: { 1: true }, marks: {} };
  assert.equal(restoreMathsMockDraft(JSON.stringify(draft), prompt).deadline, draft.deadline);
  assert.equal(mathsSecondsRemaining(draft.deadline, draft.startedAt + 61000, meta.minutes * 60), meta.minutes * 60 - 61);
  assert.equal(restoreMathsMockDraft(JSON.stringify({ ...draft, deadline: draft.deadline + 1 }), prompt), null);
  const review = { id: draft.attemptId, submittedAt: '2026-11-03T00:00:00Z', name: 'Student', elapsed: 61,
    answers: cleanMathsAnswers(paper.questions, {}), selfMarks: null, score: scoreMathsMock(paper.questions, null), solutions: paper.questions };
  const pending = mathsReportPayload(meta, review, 'student@example.invalid', 'https://example.invalid');
  const scored = mathsReportPayload(meta, { ...review, selfMarks: marks, score: scoreMathsMock(paper.questions, marks) }, 'student@example.invalid', 'https://example.invalid');
  assert.match(pending.session, /^IB Mathematics AI HL/); assert.match(pending.score, /pending/i); assert.match(scored.score, /self-assessed/);
  assert.equal(scored.solution_link, pending.solution_link); assert.equal(pending.solution_link, mathsPdfUrl(meta, 'https://example.invalid'));
  assert.match(pending.paper1 + pending.paper2, /Marking is pending/); assert.match(pending.paper1 + pending.paper2, new RegExp(meta.id));
  if (meta.paper === '3') assert.match(pending.paper3, /75 minutes; 55 marks/);
}

// Actual API handlers with isolated account-aware persistence; no network or mail.
const owner = { id: '11111111-1111-4111-8111-111111111111', email: 'student@example.invalid' };
let user = owner, access = 'active', outage = false, loads = 0, queries = 0, writes = 0;
const rows = new Map();
const db = { auth: { getUser: async () => ({ data: { user }, error: null }) }, from(table) {
  queries++; assert.equal(table, 'ib_maths_mock_attempts'); let action = 'select', patch, filters = [];
  const matching = () => [...rows.values()].filter(row => filters.every(([key, value]) => row[key] === value));
  const query = { select() { return query; }, eq(key, value) { filters.push([key, value]); return query; }, is(key, value) { filters.push([key, value]); return query; }, order() { return query; }, limit() { return query; },
    async insert(row) { writes++; if (outage) return { error: { code: '503' } }; if (rows.has(row.id)) return { error: { code: '23505' } }; rows.set(row.id, { ...row, submitted_at: '2026-11-03T00:00:00Z', self_marks: null, marked_at: null }); return { error: null }; },
    update(value) { writes++; action = 'update'; patch = value; return query; },
    async maybeSingle() { return outage ? { data: null, error: { code: '503' } } : { data: matching()[0] ?? null, error: null }; },
    then(resolve, reject) { try { if (outage) return resolve({ error: { code: '503' } }); const found = matching(); if (action === 'update') for (const row of found) Object.assign(row, patch); resolve({ data: found, error: null }); } catch (e) { reject(e); } },
  }; return query;
} };
const mocks = { '@/lib/supabase/server': { createSupabaseServerClient: async () => db }, '@/lib/ib/access': { getIbAccessState: async () => access },
  '@/lib/ib/maths-mocks': { ...server, getMathsMockPaper: async id => { loads++; return fixturePapers.get(id); } } };
const api = ibHarness({ moduleMocks: mocks }).load('app/api/ib/maths-mocks/[id]/route.ts');
const post = (id, value, origin = 'https://example.invalid') => api.POST(new Request(`https://example.invalid/api/ib/maths-mocks/${id}`, { method: 'POST', headers: { origin, 'Content-Type': 'application/json' }, body: JSON.stringify(value) }), { params: Promise.resolve({ id }) });
const get = (id, attempt = '') => api.GET(new Request(`https://example.invalid/api/ib/maths-mocks/${id}${attempt ? '?attempt=' + attempt : ''}`), { params: Promise.resolve({ id }) });
for (const [index, meta] of AI_MATHS_MOCKS.entries()) {
  const paper = fixturePapers.get(meta.id), attemptId = `33333333-3333-4333-8333-${String(index + 1).padStart(12, '0')}`;
  const body = { action: 'submit', attemptId, name: 'Student', answers: { '1:a': 'Original working' }, elapsed: meta.minutes * 60 };
  user = null; const beforeAuth = { loads, queries }; assert.equal((await get(meta.id, attemptId)).status, 401); assert.equal((await post(meta.id, body)).status, 401); assert.equal(loads, beforeAuth.loads); assert.equal(queries, beforeAuth.queries); user = owner;
  assert.equal((await post(meta.id, body, 'https://evil.invalid')).status, 403);
  assert.equal((await post(meta.id, { ...body, elapsed: meta.minutes * 60 + 1 })).status, 400);
  let response = await post(meta.id, body); assert.equal(response.status, 200); let review = (await response.json()).review;
  assert.equal(review.solutions.length, meta.questionCount); assert.equal(review.score.total, null); assert.equal(review.answers['1:a'], 'Original working');
  response = await post(meta.id, { ...body, answers: { '1:a': 'Overwrite' }, name: 'Changed' }); review = (await response.json()).review;
  assert.equal(review.answers['1:a'], 'Original working'); assert.equal(review.name, 'Student');
  assert.equal((await get(AI_MATHS_MOCKS[(index + 1) % AI_MATHS_MOCKS.length].id, attemptId)).status, 404, 'attempts cannot cross paper IDs');
  assert.equal((await get(MATHS_MOCKS[0].id, attemptId)).status, 404, 'AI attempts cannot leak through an AA URL');
  user = { id: '44444444-4444-4444-8444-444444444444', email: 'other@example.invalid' }; assert.equal((await get(meta.id, attemptId)).status, 404); assert.equal((await post(meta.id, body)).status, 404); assert.deepEqual((await (await get(meta.id)).json()).attempts, []); user = owner;
  const marks = Object.fromEntries(paper.questions.flatMap(q => q.parts.map(p => [mathsAnswerKey(q.number, p.label), p.marks])));
  for (const state of ['trial_expired', 'trial_required', 'unavailable']) {
    access = state; const before = { loads, queries, writes }, snapshot = normal([...rows.values()]);
    for (const response of [await get(meta.id), await get(meta.id, attemptId), await post(meta.id, body), await post(meta.id, { ...body, action: 'mark', selfMarks: marks })]) {
      assert.equal(response.status, state === 'unavailable' ? 503 : 403); assert.equal(response.headers.get('Cache-Control'), 'private, no-store');
      const payload = await response.json(); assert.deepEqual(Object.keys(payload).sort(), ['access_url', 'error']); assert.equal(payload.access_url, '/ib-access'); assert.doesNotMatch(JSON.stringify(payload), /PRIVATE_AI_|solutions|answers|selfMarks/);
    }
    assert.deepEqual({ loads, queries, writes }, before, 'inactive access cannot touch private content or attempts'); assert.deepEqual(normal([...rows.values()]), snapshot);
  }
  access = 'active'; assert.equal((await get(meta.id, attemptId)).status, 200);
  assert.equal((await post(meta.id, { ...body, action: 'mark', selfMarks: { ...marks, '1:a': 999 } })).status, 400);
  response = await post(meta.id, { ...body, action: 'mark', selfMarks: marks }); assert.equal((await response.json()).review.score.total, meta.marks);
  response = await post(meta.id, { ...body, action: 'mark', selfMarks: Object.fromEntries(Object.keys(marks).map(k => [k, 0])) }); assert.equal((await response.json()).review.score.total, meta.marks);
  assert.equal((await (await get(meta.id)).json()).attempts.length, 1);
  outage = true; assert.equal((await get(meta.id, attemptId)).status, 503); assert.equal((await post(meta.id, body)).status, 503); outage = false;
}
assert.equal(rows.size, AI_MATHS_MOCKS.length);

// Real shared page guard: inactive users redirect before any private paper load.
for (const state of ['active', 'trial_expired', 'trial_required', 'unavailable']) {
  access = state; const destinations = [], meta = AI_MATHS_MOCKS[0], before = loads;
  const auth = ibHarness({ user: owner, onDestination: url => destinations.push(url), moduleMocks: mocks }).load('lib/ib/auth.ts');
  const page = ibHarness({ moduleMocks: { ...mocks, '@/lib/ib/auth': auth } }).load('app/ib/maths-mocks/[id]/page.tsx').default;
  const render = () => page({ params: Promise.resolve({ id: meta.id }), searchParams: Promise.resolve({}) });
  if (state === 'active') { const tree = await render(); assert.equal(tree.props.paper.strand, 'ai'); assert.equal(tree.props.accountId, owner.id); assert.doesNotMatch(JSON.stringify(tree.props.paper), /PRIVATE_AI_|markScheme|answerSummary/); assert.equal(loads, before + 1); }
  else { await assert.rejects(render, /REDIRECT/); assert.deepEqual(destinations, [`/ib-access?state=${state}`]); assert.equal(loads, before); }
}
access = 'active';
const List = h.load('app/ib/components/MathsMockList.tsx').default;
for (const [strand, course, count] of [['ai', 'hl', 12], ['aa', 'hl', 6], ['aa', 'sl', 4]]) {
  const html = renderToStaticMarkup(React.createElement(List, { strand, course }));
  assert.equal((html.match(/>Start ↗<\/span>/g) ?? []).length, count); assert.doesNotMatch(html, new RegExp(`/ib/maths-mocks/${strand === 'ai' ? 'aa' : 'ai'}-`));
  if (strand === 'ai') { assert.match(html, /every AI paper/); assert.match(html, /Mock Set D/); assert.doesNotMatch(html, /without a calculator|reconstructed/); }
}
const Runner = h.load('app/ib/maths-mocks/MathsMockRunner.tsx').default;
const runnerHtml = renderToStaticMarkup(React.createElement(Runner, { paper: server.mathsMockPrompt(fixturePapers.get(AI_MATHS_MOCKS[0].id), AI_MATHS_MOCKS[0]), email: owner.email, accountId: owner.id }));
assert.match(runnerHtml, /APPLICATIONS AND INTERPRETATION/); assert.match(runnerHtml, /math-ai-hl/); assert.doesNotMatch(runnerHtml, /ANALYSIS AND APPROACHES|math-aa-hl/);
const index = h.load('lib/ib/build-content-index.ts').buildIbContentIndex([]);
assert.equal(index.summaries.hl['math-ai-hl'].mocks, 12); assert.equal(index.summaries.hl['math-aa-hl'].mocks, 6); assert.equal(index.summaries.sl['math-aa-sl'].mocks, 4);
const migrations = readdirSync('supabase/migrations').filter(f => /_ib_ai_hl_mock_attempt_ids\.sql$/.test(f)); assert.equal(migrations.length, 1);
const sql = readFileSync(`supabase/migrations/${migrations[0]}`, 'utf8');
for (const pattern of ["^aa-hl-set-[ab]-paper-[123]$", "^aa-sl-set-[ab]-paper-[12]$", "^ai-hl-set-[a-d]-paper-[12]$", "^ai-hl-set-[ab]-paper-3$"]) assert.ok(sql.includes(pattern));
assert.match(sql, /drop constraint ib_maths_mock_attempts_mock_id_check,[\s\S]+add constraint ib_maths_mock_attempts_mock_id_check check/i);
assert.doesNotMatch(sql.replace(/--[^\n]*/g, ''), /\b(?:grant|revoke|delete|truncate|update|create policy|drop policy|alter column)\b/i);

let questions = 0, marks = 0, diagrams = 0, formulae = 0;
if (!infrastructureOnly) {
  const parser = unified().use(remarkParse).use(remarkMath).use(remarkGfm);
  const markdown = value => { function visit(n) { if (n.type === 'math' || n.type === 'inlineMath') { katex.renderToString(n.value, { throwOnError: true, strict: 'ignore', trust: false }); formulae++; } n.children?.forEach(visit); } visit(parser.parse(value)); };
  for (const meta of AI_MATHS_MOCKS) {
    const file = `content/ib/${meta.paper === "3" && ["C","D"].includes(meta.set) ? "practice-2027/ai" : "ai-mocks-2026/papers"}/${meta.id}.json`; assert.ok(existsSync(file), `Missing paper ${meta.id}`);
    const paper = server.validateMathsMockPaper(JSON.parse(readFileSync(file, 'utf8')), meta); questions += paper.questions.length; marks += paper.marks;
    for (const q of paper.questions) { markdown(q.stem); for (const p of q.parts) markdown(p.prompt); for (const g of q.markScheme) for (const s of g.steps) markdown(s.text); if (q.diagramSvg) diagrams++; }
    const pdf = `public/ib-mock-solutions/${meta.id}.pdf`; assert.ok(existsSync(pdf), `Missing combined PDF ${meta.id}`); assert.equal(readFileSync(pdf).subarray(0, 5).toString(), '%PDF-');
  }
  assert.equal(questions, 96); assert.equal(marks, 1100);
}
console.log(JSON.stringify({ status: 'passed', mode: infrastructureOnly ? 'isolated infrastructure fixtures; publication assets not checked' : 'publication catalogue, content and PDF assets', papers: AI_MATHS_MOCKS.length, questions, marks, diagrams, formulae,
  verified: 'AI/AA catalogue isolation; all-paper GDC; AI no sections; private prompts; deadlines; bounded self-marks; AI and AA attempt isolation; immutable/idempotent submit and marking; owner access; all trial states; actual shared page guard; report/PDF consistency; additive ID migration; no live writes or email' }));
