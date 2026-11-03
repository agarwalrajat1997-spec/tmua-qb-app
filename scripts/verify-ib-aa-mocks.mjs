import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import katex from 'katex';
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import { ibHarness } from './ib-component-harness.mjs';

const infrastructureOnly = process.argv.includes('--infrastructure-only');
const h = ibHarness(), m = h.load('lib/ib/maths-mock-model.ts'), server = h.load('lib/ib/maths-mocks.ts');
const { MATHS_MOCKS, mathsAnswerKey, cleanMathsAnswers, validateMathsMarks, scoreMathsMock, mathsPdfUrl, mathsReportPayload, mathsSecondsRemaining, restoreMathsMockDraft } = m;
assert.equal(MATHS_MOCKS.length, 10);
assert.equal(new Set(MATHS_MOCKS.map(p => p.id)).size, 10);
assert.equal(MATHS_MOCKS.reduce((n, p) => n + p.questionCount, 0), 90);
assert.equal(MATHS_MOCKS.reduce((n, p) => n + p.marks, 0), 870);
for (const p of MATHS_MOCKS) {
  assert.match(p.id, /^aa-(?:hl|sl)-set-[ab]-paper-[123]$/);
  assert.equal(p.status, 'published'); assert.equal(p.year, 2025);
  assert.equal(p.calculator, p.paper !== '1');
  assert.equal(p.minutes, p.course === 'sl' ? 90 : p.paper === '3' ? 75 : 120);
  assert.equal(p.marks, p.course === 'sl' ? 80 : p.paper === '3' ? 55 : 110);
  assert.equal(mathsPdfUrl(p, 'https://example.invalid'), `https://example.invalid/ib-mock-solutions/${p.id}.pdf`);
  assert.throws(() => mathsPdfUrl({ ...p, pdfUrl: 'https://evil.invalid/other.pdf' }));
}
const normal = value => JSON.parse(JSON.stringify(value));
function fixture(meta) {
  const base = Math.floor(meta.marks / meta.questionCount), remainder = meta.marks % meta.questionCount;
  return { id: meta.id, course: meta.course, set: meta.set, paper: meta.paper, title: meta.title, minutes: meta.minutes, marks: meta.marks, calculator: meta.calculator,
    questions: Array.from({ length: meta.questionCount }, (_, i) => { const marks = base + Number(i < remainder); return {
      number: i + 1, section: meta.paper === '3' ? '' : i < Math.ceil(meta.questionCount / 2) ? 'A' : 'B', marks,
      stem: 'Isolated API fixture. This is not publication content.', parts: [{ label: 'a', prompt: 'Fixture response.', marks }],
      answerSummary: 'PRIVATE_MATHS_ANSWER_CANARY', markScheme: [{ part: 'a', steps: [{ code: `A${marks}`, text: 'PRIVATE_MATHS_SCHEME_CANARY' }] }],
      ...(i === 0 ? { diagramSvg: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="M0 0L100 100"/></svg>' } : {}) }; }) };
}
const fixturePapers = new Map();
let assertions = 0;
for (const meta of MATHS_MOCKS) {
  const p = server.validateMathsMockPaper(fixture(meta), meta); fixturePapers.set(meta.id, p);
  const marks = Object.fromEntries(p.questions.flatMap(q => q.parts.map(part => [mathsAnswerKey(q.number, part.label), part.marks])));
  const full = Object.fromEntries(Object.keys(marks).map(key => [key, 'Retained written working']));
  const clean = cleanMathsAnswers(p.questions, { ...full, unknown: 'drop this' });
  assert.equal('unknown' in clean, false); assert.equal(Object.keys(clean).length, Object.keys(marks).length);
  assert.equal(scoreMathsMock(p.questions, validateMathsMarks(p.questions, marks)).total, meta.marks);
  assert.equal(scoreMathsMock(p.questions, Object.fromEntries(Object.keys(marks).map(key => [key, 0]))).total, 0);
  assert.equal(scoreMathsMock(p.questions, null).total, null);
  for (const bad of [null, [], 'bad']) assert.throws(() => cleanMathsAnswers(p.questions, bad));
  assert.throws(() => cleanMathsAnswers(p.questions, { [Object.keys(marks)[0]]: 'x'.repeat(12001) }));
  for (const bad of [-1, 999, 0.5, '1', null]) assert.throws(() => validateMathsMarks(p.questions, { ...marks, [Object.keys(marks)[0]]: bad }));
  assert.throws(() => validateMathsMarks(p.questions, {}));
  const prompt = server.mathsMockPrompt(p, meta);
  assert.doesNotMatch(JSON.stringify(prompt), /PRIVATE_MATHS_(?:ANSWER|SCHEME)_CANARY|markScheme|answerSummary|diagramSvg/);
  assert.match(prompt.questions[0].diagramUrl, /^data:image\/svg\+xml;base64,/);
  const review = { id: '22222222-2222-4222-8222-222222222222', submittedAt: '2026-11-03T00:00:00Z', name: 'Student', elapsed: 123, answers: clean, selfMarks: null, score: scoreMathsMock(p.questions, null), solutions: p.questions };
  const pending = mathsReportPayload(meta, review, 'student@example.invalid', 'https://example.invalid');
  assert.match(pending.score, /pending/i); assert.doesNotMatch(pending.score, /null|NaN/);
  assert.equal(pending.solution_link, mathsPdfUrl(meta, 'https://example.invalid'));
  assert.match(pending.paper1 + pending.paper2, /Marking is pending/);
  const scored = mathsReportPayload(meta, { ...review, selfMarks: marks, score: scoreMathsMock(p.questions, marks) }, 'student@example.invalid', 'https://example.invalid');
  assert.equal(scored.to_email, 'student@example.invalid'); assert.match(scored.score, /self-assessed/); assert.equal(scored.solution_link, pending.solution_link);
  assert.equal(mathsSecondsRemaining(5000, 1000, 120), 4); assert.equal(mathsSecondsRemaining(5000, 5001, 120), 0); assert.equal(mathsSecondsRemaining(5000000, 0, 120), 120);
  const draft = { version: 1, attemptId: review.id, name: 'Student', startedAt: 100000, deadline: 100000 + meta.minutes * 60000, elapsed: 0, stage: 'running', index: 0, answers: clean, flags: { 1: true }, marks: {} };
  assert.equal(restoreMathsMockDraft(JSON.stringify(draft), prompt).deadline, draft.deadline);
  assert.equal(mathsSecondsRemaining(draft.deadline, draft.startedAt + 25000, meta.minutes * 60), meta.minutes * 60 - 25, 'refresh uses original deadline');
  for (const patch of [{ index: -1 }, { deadline: draft.deadline + 1000 }, { attemptId: 'bad' }, { answers: [] }, { marks: { '1:a': 999 } }, { flags: { '999': true } }]) assert.equal(restoreMathsMockDraft(JSON.stringify({ ...draft, ...patch }), prompt), null);
  const wrong = normal(p); wrong.questions[0].parts[0].marks++; assert.throws(() => server.validateMathsMockPaper(wrong, meta));
  const wrongScheme = normal(p); wrongScheme.questions[0].markScheme[0].steps[0].code = 'M1'; assert.throws(() => server.validateMathsMockPaper(wrongScheme, meta));
  const unsafe = normal(p); unsafe.questions[0].diagramSvg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><script>alert(1)</script></svg>'; assert.throws(() => server.validateMathsMockPaper(unsafe, meta));
  assertions += 40;
}

// Exercise the actual endpoint with an isolated owner-aware adapter. No network or email.
const owner = { id: '11111111-1111-4111-8111-111111111111', email: 'student@example.invalid' };
let user = owner, outage = false, loads = 0, access = 'active', accessChecks = 0, queries = 0, writes = 0;
const rows = new Map();
const db = { auth: { getUser: async () => ({ data: { user }, error: null }) }, from(table) {
  queries++;
  assert.equal(table, 'ib_maths_mock_attempts'); let action = 'select', patch, filters = [];
  const matching = () => [...rows.values()].filter(row => filters.every(([key, value]) => row[key] === value));
  const query = { select() { return query; }, eq(key, value) { filters.push([key, value]); return query; }, is(key, value) { filters.push([key, value]); return query; }, order() { return query; }, limit() { return query; },
    insert: async row => { writes++; if (outage) return { error: { code: '503' } }; if (rows.has(row.id)) return { error: { code: '23505' } }; rows.set(row.id, { ...row, submitted_at: '2026-11-03T00:00:00Z', self_marks: null, marked_at: null }); return { error: null }; },
    update(value) { writes++; action = 'update'; patch = value; return query; },
    async maybeSingle() { return outage ? { data: null, error: { code: '503' } } : { data: matching()[0] ?? null, error: null }; },
    then(resolve, reject) { try { if (outage) return resolve({ error: { code: '503' } }); const found = matching(); if (action === 'update') for (const row of found) Object.assign(row, patch); resolve({ data: found, error: null }); } catch (e) { reject(e); } },
  }; return query;
} };
const mocks = { '@/lib/supabase/server': { createSupabaseServerClient: async () => db }, '@/lib/ib/access': { getIbAccessState: async () => { accessChecks++; return access; } }, '@/lib/ib/maths-mocks': { ...server, getMathsMockPaper: async id => { loads++; return fixturePapers.get(id); } } };
const api = ibHarness({ moduleMocks: mocks }).load('app/api/ib/maths-mocks/[id]/route.ts');
const meta = MATHS_MOCKS[0], paper = fixturePapers.get(meta.id), attempt = '33333333-3333-4333-8333-333333333333';
const body = { action: 'submit', attemptId: attempt, name: 'Student', answers: {}, elapsed: 30 };
const pageHarness = ibHarness({ user: owner, moduleMocks: mocks });
const page = pageHarness.load('app/ib/maths-mocks/[id]/page.tsx').default;
const tree = await page({ params: Promise.resolve({ id: meta.id }), searchParams: Promise.resolve({}) });
assert.doesNotMatch(JSON.stringify(tree.props.paper), /PRIVATE_MATHS_(?:ANSWER|SCHEME)_CANARY|markScheme|answerSummary|diagramSvg/);
assert.equal(tree.props.accountId, owner.id); assert.equal(tree.props.paper.id, meta.id);
const blockedPage = ibHarness({ user: null, moduleMocks: mocks }).load('app/ib/maths-mocks/[id]/page.tsx').default;
const beforePage = loads; await assert.rejects(() => blockedPage({ params: Promise.resolve({ id: meta.id }), searchParams: Promise.resolve({}) }), /AUTH_REQUIRED/); assert.equal(loads, beforePage);
const post = (value, origin = 'https://example.invalid', id = meta.id) => api.POST(new Request(`https://example.invalid/api/ib/maths-mocks/${id}`, { method: 'POST', headers: { origin, 'Content-Type': 'application/json' }, body: JSON.stringify(value) }), { params: Promise.resolve({ id }) });
const get = (id = meta.id, key = attempt) => api.GET(new Request(`https://example.invalid/api/ib/maths-mocks/${id}${key ? '?attempt=' + key : ''}`), { params: Promise.resolve({ id }) });
assert.equal((await post(body, 'https://evil.invalid')).status, 403);
assert.equal((await get('unknown')).status, 404);
user = null; const before = loads, beforeAuthAccess = accessChecks; assert.equal((await post(body)).status, 401); assert.equal((await get()).status, 401); assert.equal(loads, before, 'unauthenticated users never load private schemes'); assert.equal(accessChecks, beforeAuthAccess, 'trial access is checked only after authentication'); user = owner;
for (const patch of [{ elapsed: -1 }, { elapsed: meta.minutes * 60 + 1 }, { elapsed: 1.5 }, { answers: [] }, { name: 'a'.repeat(101) }, { attemptId: 'bad' }]) assert.equal((await post({ ...body, ...patch })).status, 400);
outage = true; assert.equal((await post(body)).status, 503); outage = false;
let response = await post(body); assert.equal(response.status, 200); let result = await response.json(); assert.equal(result.review.score.total, null); assert.equal(result.review.solutions.length, paper.questions.length);
response = await post({ ...body, answers: { '1:a': 'Overwrite' }, name: 'Changed' }); result = await response.json(); assert.equal(result.review.answers['1:a'], ''); assert.equal(result.review.name, 'Student'); assert.equal(rows.size, 1);
user = { id: '44444444-4444-4444-8444-444444444444', email: 'other@example.invalid' }; assert.equal((await get()).status, 404); assert.equal((await post(body)).status, 404); assert.deepEqual((await (await get(meta.id, '')).json()).attempts, []); user = owner;
assert.equal((await get(meta.id, 'bad')).status, 400);
assert.equal((await post({ ...body, action: 'mark', selfMarks: {} })).status, 400);
const marks = Object.fromEntries(paper.questions.flatMap(q => q.parts.map(part => [mathsAnswerKey(q.number, part.label), part.marks])));
// A saved attempt must not bypass trial access. Denied users cannot read history,
// retrieve private solutions, create attempts or change marks, even with valid inputs.
const inactiveAttempt = '55555555-5555-4555-8555-555555555555';
for (const state of ['active', 'trial_expired', 'trial_required', 'unavailable']) {
  access = state;
  const expected = state === 'active' ? 200 : state === 'unavailable' ? 503 : 403;
  if (state === 'active') {
    assert.equal((await get()).status, expected);
    assert.equal((await get(meta.id, '')).status, expected);
    assert.equal((await post(body)).status, expected);
  } else {
    const snapshot = normal([...rows.values()]), beforeGate = { loads, queries, writes, accessChecks };
    const denied = [await get(), await get(meta.id, ''), await post({ ...body, attemptId: inactiveAttempt }), await post({ ...body, action: 'mark', selfMarks: marks })];
    for (const response of denied) {
      assert.equal(response.status, expected, `${state} blocks reads and writes`);
      assert.equal(response.headers.get('Cache-Control'), 'private, no-store');
      const payload = await response.json();
      assert.deepEqual(Object.keys(payload).sort(), ['access_url', 'error']);
      assert.equal(payload.access_url, '/ib-access');
      assert.doesNotMatch(JSON.stringify(payload), /PRIVATE_MATHS_(?:ANSWER|SCHEME)_CANARY|solutions|selfMarks|answers|submittedAt/);
    }
    assert.equal(accessChecks - beforeGate.accessChecks, 4);
    assert.equal(loads, beforeGate.loads, `${state} never loads private paper content`);
    assert.equal(queries, beforeGate.queries, `${state} never queries attempt records`);
    assert.equal(writes, beforeGate.writes, `${state} never invokes a mutation`);
    assert.deepEqual(normal([...rows.values()]), snapshot);
    assert.equal(rows.has(inactiveAttempt), false);
  }
  // Exercise the actual shared page guard, rather than a simulated replacement.
  // The page must redirect before loading any private paper for inactive access.
  const destinations = [];
  const authHarness = ibHarness({ user: owner, onDestination: url => destinations.push(url), moduleMocks: mocks });
  const guardedPage = ibHarness({ moduleMocks: { ...mocks, '@/lib/ib/auth': authHarness.load('lib/ib/auth.ts') } }).load('app/ib/maths-mocks/[id]/page.tsx').default;
  const beforeGuardedPage = loads, beforePageAccess = accessChecks;
  const renderPage = () => guardedPage({ params: Promise.resolve({ id: meta.id }), searchParams: Promise.resolve({}) });
  if (state === 'active') {
    const tree = await renderPage(); assert.equal(tree.props.accountId, owner.id); assert.equal(loads, beforeGuardedPage + 1);
    assert.deepEqual(destinations, []);
  } else {
    await assert.rejects(renderPage, /REDIRECT/);
    assert.deepEqual(destinations, [`/ib-access?state=${state}`]); assert.equal(loads, beforeGuardedPage);
  }
  assert.equal(accessChecks, beforePageAccess + 1, 'page invokes the shared IB access guard');
}
access = 'active';
response = await post({ ...body, action: 'mark', selfMarks: marks }); assert.equal((await response.json()).review.score.total, meta.marks);
response = await post({ ...body, action: 'mark', selfMarks: Object.fromEntries(Object.keys(marks).map(key => [key, 0])) }); assert.equal((await response.json()).review.score.total, meta.marks, 'mark retries retain first saved self-assessment');
assert.equal((await get()).status, 200); assert.equal((await (await get(meta.id, '')).json()).attempts.length, 1);
outage = true; assert.equal((await get()).status, 503); outage = false;

const schemaSql = readFileSync('supabase/migrations/20261103021858_ib_maths_mock_attempts.sql', 'utf8');
assert.match(schemaSql, /enable row level security/i); assert.match(schemaSql, /grant update \(self_marks, marked_at\)/i); assert.doesNotMatch(schemaSql, /grant update on/i); assert.doesNotMatch(schemaSql, /security definer/i); assert.match(schemaSql, /using \(\(select auth.uid\(\)\) = user_id\) with check/i); assert.match(schemaSql, /Submitted mathematics responses are immutable/);
const runner = readFileSync('app/ib/maths-mocks/MathsMockRunner.tsx', 'utf8');
assert.match(runner, /deliverEmail\(result, "completion"\)/); assert.match(runner, /deliverEmail\(data.review, "scored"\)/); assert.match(runner, /localStorage.setItem\(mailKey\(attempt, kind\), state\)/); assert.match(runner, /stored === "sent"/); assert.match(runner, /if \(event.currentTarget.open\) setPdfOpen\(true\)/); assert.match(runner, /href=\{pdfUrl\}/); assert.match(runner, /src=\{`\$\{pdfUrl\}#toolbar=0/);
for (const course of ['hl', 'sl']) {
  const List = h.load('app/ib/components/MathsMockList.tsx').default;
  const html = renderToStaticMarkup(React.createElement(List, { course }));
  assert.equal((html.match(/>Start ↗<\/span>/g) ?? []).length, course === 'hl' ? 6 : 4);
  assert.doesNotMatch(html, new RegExp(`/ib/maths-mocks/aa-${course === 'hl' ? 'sl' : 'hl'}-`));
}

let realQuestions = 0, realMarks = 0, diagrams = 0, formulae = 0;
if (!infrastructureOnly) {
  const parser = unified().use(remarkParse).use(remarkMath).use(remarkGfm);
  function markdown(value) { function visit(n) { if (n.type === 'math' || n.type === 'inlineMath') { katex.renderToString(n.value, { throwOnError: true, strict: 'ignore', trust: false }); formulae++; } n.children?.forEach(visit); } visit(parser.parse(value)); }
  for (const meta of MATHS_MOCKS) {
    const path = `content/ib/aa-mocks-2026/papers/${meta.id}.json`; assert.ok(existsSync(path), `Missing paper ${meta.id}`);
    const p = server.validateMathsMockPaper(JSON.parse(readFileSync(path, 'utf8')), meta); realQuestions += p.questions.length; realMarks += p.marks;
    for (const q of p.questions) { markdown(q.stem); for (const part of q.parts) markdown(part.prompt); for (const g of q.markScheme) for (const s of g.steps) markdown(s.text); if (q.diagramSvg) diagrams++; }
    const pdf = `public/ib-mock-solutions/${meta.id}.pdf`; assert.ok(existsSync(pdf), `Missing combined PDF ${meta.id}`); assert.equal(readFileSync(pdf).subarray(0, 4).toString(), '%PDF');
  }
  assert.equal(realQuestions, 90); assert.equal(realMarks, 870);
}
console.log(JSON.stringify({ status: 'passed', mode: infrastructureOnly ? 'infrastructure fixtures only; publication content not checked' : 'full catalogue, publication content and PDF assets', papers: 10, infrastructureAssertionsAtLeast: assertions, realQuestions, realMarks, diagrams, formulae,
  verified: 'owner-auth APIs; active/expired/required/unavailable access for GET, POST and shared page guard; inactive access prevents private content loads, attempt queries and mutations; wrong-origin rejection; immutable idempotent submit/mark; bounded self-marks; outage recovery; private scheme exclusion; deadline refresh; invalid draft rejection; pending/scored report contracts; canonical PDF link; separate courses; no live mail or database writes' }));
