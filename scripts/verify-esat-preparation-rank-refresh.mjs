import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import * as crypto from 'node:crypto';
import ts from 'typescript';
import * as canonical from '../lib/server/esat-canonical-tests.ts';
import * as october from '../lib/server/esat-october-2026-tests.ts';
import * as evidence from '../lib/server/esat-predictor-evidence.ts';
import * as predictor from '../lib/server/esat-predictor-v1-engine.ts';
import * as preparation from '../lib/server/tmua-preparation-rank-v1-engine.ts';
import { createStandardTimeEstimate } from '../lib/server/practice-standard-time.ts';

const source = readFileSync('lib/server/esat-preparation-rank-refresh.ts', 'utf8');
const NOW = Date.parse('2026-10-20T12:00:00Z');
const DAY = 86_400_000;
const iso = days => new Date(NOW - days * DAY).toISOString();
const MODULES = { 'node:crypto': crypto, './esat-canonical-tests.ts': canonical,
  './esat-october-2026-tests.ts': october, './esat-predictor-evidence.ts': evidence,
  './esat-predictor-v1-engine.ts': predictor, './tmua-preparation-rank-v1-engine.ts': preparation };
function loadWorker(pageSize = 1000, maxRows = 100_000) {
  const compiled = ts.transpileModule(source.replace('const PAGE_SIZE = 1000;', `const PAGE_SIZE = ${pageSize};`)
    .replace('const MAX_ROWS = 100_000;', `const MAX_ROWS = ${maxRows};`), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText;
  class Clock extends Date {
    constructor(...args) { super(...(args.length ? args : [NOW])); }
    static now() { return NOW; }
  }
  const context = vm.createContext({ Date: Clock, exports: {}, require: name => {
    assert.ok(MODULES[name], `Unexpected runtime import: ${name}`);
    return MODULES[name];
  } });
  vm.runInContext(compiled, context);
  return context.exports.refreshEsatPreparationRank;
}

const users = [
  ['test-active', 100], ['qb-active', 100], ['login-only', 2], ['old-test-login', 1],
  ['inactive', 31], ['expired', 1], ['unapproved', 1], ['tmua-only', 1],
  ['at-boundary', 30], ['future-login', -1], ['unknown-qb', 100],
].map(([id, days]) => ({ id, email: `${id}@example.com`, last_sign_in_at: iso(days) }));
const questions = Array.from({ length: 32 }, (_, i) => ({
  qid: `ESAT-${i}`, topic: ['Algebra', 'Geometry', 'Physics', 'Chemistry'][i % 4], answer: 'A', is_active: true,
}));
function attempt(user, id, raw, days, number = 1, extraTime = false) {
  const test = canonical.getCanonicalEsatTest(id);
  const answers = test.answers.map((answer, i) => i % 27 < raw ? answer : null);
  const settings = { version: 1, order: 'sequential', time_multiplier: 1.25,
    question_order: Array.from({ length: 81 }, (_, i) => i), section_sizes: [27, 27, 27], base_seconds_per_section: 2400 };
  return { id: `${user}-${id}-${number}`, user_id: user, test_id: id, answers,
    attempt_number: number, submitted_at: iso(days),
    predictor_metadata: extraTime ? { practice_settings: settings,
      standard_time_estimate: createStandardTimeEstimate(id, answers, settings) } : null };
}
function fixture() {
  const tests = [
    attempt('test-active', 'esat-mock-01', 16, 7),
    attempt('test-active', 'esat-mock-01', 23, 2, 2),
    attempt('test-active', 'esat-october-2026-engineering', 20, 4, 1, true),
    attempt('test-active', 'esat-october-2026-physics-chemistry', 22, 1),
    attempt('old-test-login', 'esat-mock-01', 17, 50),
    attempt('inactive', 'esat-mock-01', 27, 31),
    attempt('at-boundary', 'esat-mock-01', 27, 30),
  ];
  return {
    practice_test_attempts: tests,
    esat_qb_questions: questions,
    tmua_qb_attempt_events: [...questions.map((q, i) => ({ id: `event-${i}`, user_id: 'qb-active',
      product: 'esat-question-bank', question_id: `legacy-${i}`, metadata: { canonical_qid: q.qid },
      source: 'qb-progress-trigger-v2', history_quality: 'observed', predictor_eligible: true,
      selected_answer: i < 25 ? 'A' : 'B', attempted_at: iso(3),
    })), { id: 'unknown-event', user_id: 'unknown-qb', product: 'esat-question-bank', question_id: 'unknown',
      metadata: {}, source: 'qb-progress-trigger-v2', history_quality: 'observed', predictor_eligible: true,
      selected_answer: 'A', attempted_at: iso(1) }],
    student_access: users.map((user, i) => ({ id: `access-${i}`, email: user.email.toUpperCase(),
      product: user.id === 'tmua-only' ? 'tmua-question-bank' : i % 2 ? 'esat-classes' : 'esat-question-bank',
      approved: user.id !== 'unapproved', expires_at: user.id === 'expired' ? iso(0) : null })),
    tmua_preparation_rank_runs: [], tmua_preparation_rank_snapshots: [],
  };
}
function harness(options = {}) {
  const tables = fixture(), queries = [], writes = [];
  const authUsers = options.authUsers ?? structuredClone(users);
  let authCalls = 0;
  const admin = {
    auth: { admin: { listUsers: async ({ page, perPage }) => {
      authCalls += 1;
      const data = authUsers.slice((page - 1) * perPage, page * perPage);
      if (options.duplicateAuth && page === 2) data[0] = authUsers[0];
      return { data: { users: data, total: authUsers.length }, error: null };
    } } },
    from(table) {
      const ops = [];
      const builder = {};
      for (const name of ['select', 'eq', 'in', 'order', 'range', 'retry', 'insert']) {
        builder[name] = (...args) => { ops.push([name, ...args]); return builder; };
      }
      builder.then = (resolve, reject) => Promise.resolve().then(() => {
        queries.push({ table, ops });
        assert.ok(ops.some(([name, value]) => name === 'retry' && value === false));
        if (table === options.failTable) return { data: null, error: { code: options.failCode ?? '57014', message: 'fixture failure' } };
        if (options.missingCanonical && table === 'esat_qb_questions') return { data: null, error: { code: '42P01' } };
        const insert = ops.find(([name]) => name === 'insert');
        if (insert) {
          const rows = Array.isArray(insert[1]) ? insert[1] : [insert[1]];
          tables[table].push(...structuredClone(rows));
          writes.push({ table, rows: structuredClone(rows) });
          return { data: null, error: null };
        }
        const actualTable = table === 'esat_questions' ? 'esat_qb_questions' : table;
        assert.ok(tables[actualTable], `Unexpected table: ${table}`);
        let rows = [...tables[actualTable]];
        for (const [name, key, value] of ops) {
          if (name === 'eq') rows = rows.filter(row => row[key] === value);
          if (name === 'in') rows = rows.filter(row => value.includes(row[key]));
        }
        if (ops.some(([name, , value]) => name === 'select' && value?.head)) {
          return { data: null, count: options.wrongCount ? rows.length + 1 : rows.length, error: null };
        }
        const orders = ops.filter(([name]) => name === 'order');
        assert.ok(orders.some(([, key]) => key === 'id' || key === 'qid'), 'Stable pagination tie-breaker');
        rows.sort((a, b) => {
          for (const [, key] of orders) { const result = String(a[key]).localeCompare(String(b[key])); if (result) return result; }
          return 0;
        });
        const range = ops.find(([name]) => name === 'range');
        if (range) rows = rows.slice(range[1], range[2] + 1);
        return { data: structuredClone(rows), error: null };
      }).then(resolve, reject);
      return builder;
    },
  };
  return { admin, tables, queries, writes, authCalls: () => authCalls };
}

const run = loadWorker(2);
const h = harness();
const result = await run(h.admin);
assert.equal(result.cohortSize, 4);
assert.equal(result.calculatedAt, new Date(NOW).toISOString());
assert.equal(h.tables.tmua_preparation_rank_runs.length, 1);
const snapshots = h.tables.tmua_preparation_rank_snapshots;
assert.deepEqual(snapshots.map(row => row.user_id).sort(), ['login-only', 'old-test-login', 'qb-active', 'test-active']);
assert.ok(h.authCalls() > 1, 'Exercises multi-page auth users');
assert.ok(h.writes.filter(row => row.table.endsWith('_snapshots')).length > 1, 'Exercises chunked persistence');
const login = snapshots.find(row => row.user_id === 'login-only');
assert.equal(login.genuine_preparation_evidence, false);
assert.equal(login.actual_preparation_rank, null);
assert.equal(login.actual_active_cohort_size, 4, 'Login-only members remain in the denominator');

// Recreate the existing request-side input, using the existing audited engines.
// This proves the refresh does not change canonical scoring, retakes, pathway
// families, extra-time handling, preparation weights or rank ordering.
const expected = snapshots.map(row => {
  const tests = h.tables.practice_test_attempts.filter(test => test.user_id === row.user_id);
  const testEvidence = evidence.buildEsatTestEvidence(tests);
  const qb = h.tables.tmua_qb_attempt_events.filter(event => event.user_id === row.user_id);
  const events = qb.map(event => {
    const q = questions.find(question => question.qid === event.metadata.canonical_qid);
    return { id: event.id, source: event.source, historyQuality: event.history_quality,
      predictorEligible: event.predictor_eligible, canonicalQid: q?.qid ?? event.question_id,
      canonicalActive: !!q?.is_active, selectedAnswer: event.selected_answer, canonicalAnswer: q?.answer ?? null,
      canonicalTopic: q?.topic ?? null, attemptedAt: event.attempted_at };
  });
  const prediction = predictor.calculateEsatPredictorV1({ testAttempts: testEvidence, qbEvents: events,
    activeTopics: [...new Set(questions.map(q => q.topic))].sort() });
  const families = [...new Set(testEvidence.map(test => test.testId))].map(id => {
    const attempts = testEvidence.filter(test => test.testId === id).sort((a, b) => Date.parse(a.evaluatedAt) - Date.parse(b.evaluatedAt));
    return { score9: attempts.length === 1 ? attempts[0].predictedCombinedPracticeScore :
      .75 * attempts[0].predictedCombinedPracticeScore + .25 * attempts.at(-1).predictedCombinedPracticeScore, weight: 1.5 };
  });
  const recentTests = new Set(tests.filter(test => Date.parse(test.submitted_at) > NOW - 30 * DAY)
    .map(test => october.getEsatPredictorFamilyId(test.test_id))).size;
  const score = preparation.calculatePreparationScore({ predictedTmuaScore9: prediction.predictedEsatPracticeScore,
    broadOrFullIndependentTestFamilies: prediction.independentTestCount, predictorTestWeight: prediction.testWeight,
    trustedUniqueFirstExposures: prediction.qbUniqueQuestions, trustedCanonicalTopicCoverage: prediction.qbTopicCoverage,
    distinctCanonicalQbInteractions30d: qb.length, independentRecognisedTestFamilies30d: recentTests,
    testFamilySignals: families, hasGenuineTestEvidence: testEvidence.length > 0,
    hasGenuineQbEvidence: prediction.qbUniqueQuestions > 0, recovery: null });
  assert.equal(row.actual_preparation_score, score.actualPreparationScore);
  assert.equal(row.predicted_tmua_score9, prediction.predictedEsatPracticeScore);
  assert.equal(row.predictor_input_hash, prediction.inputHash);
  assert.equal(row.independent_recognised_test_families_30d, recentTests);
  return { userId: row.user_id, active: true, score };
});
for (const ranked of preparation.rankPreparationCohort(expected)) {
  assert.equal(snapshots.find(row => row.user_id === ranked.userId).actual_preparation_rank, ranked.actualPreparationRank);
}
assert.equal(snapshots.find(row => row.user_id === 'test-active').independent_recognised_test_families_30d, 2,
  'Two October pathways count as one shared family');
assert.ok(h.queries.some(query => query.table === 'practice_test_attempts'
  && query.ops.some(([name, select]) => name === 'select' && select.includes('predictor_metadata'))));
const second = await run(h.admin);
assert.notEqual(second.runId, result.runId);
assert.notEqual(h.tables.tmua_preparation_rank_runs[0].input_hash, h.tables.tmua_preparation_rank_runs[1].input_hash,
  'A refresh always writes a fresh complete run, even at the same test clock time');

const alias = harness({ missingCanonical: true });
assert.equal((await run(alias.admin)).cohortSize, 4);
assert.ok(alias.queries.some(query => query.table === 'esat_questions'));
const outage = harness({ failTable: 'esat_qb_questions' });
await assert.rejects(() => run(outage.admin));
assert.ok(!outage.queries.some(query => query.table === 'esat_questions'), 'Outages must not scan historical aliases');
assert.equal(outage.writes.length, 0);
await assert.rejects(() => run(harness({ wrongCount: true }).admin), /completeness check failed/);
await assert.rejects(() => run(harness({ failTable: 'tmua_preparation_rank_snapshots' }).admin), /snapshot insert failed/);
await assert.rejects(() => run(harness({ duplicateAuth: true }).admin), /duplicate identity/);
await assert.rejects(() => loadWorker(2, 4)(harness().admin), /safety limit/);

const empty = harness({ authUsers: [] });
assert.equal((await run(empty.admin)).cohortSize, 0);
assert.equal(empty.tables.tmua_preparation_rank_snapshots.length, 0);
assert.ok(!source.includes('tmua_preparation_rank_exclusions'), 'ESAT has no TMUA-specific exclusion policy');
console.log('PASS: ESAT background ranking preserves scoring/cohort rules, handles complete paginated reads, and publishes only verified complete snapshots.');
