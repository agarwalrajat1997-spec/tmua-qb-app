import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';
import { createClient as createActualClient } from '@supabase/supabase-js';
import { NextRequest, NextResponse } from 'next/server.js';

function moduleAt(file, imports = {}, overrides = {}) {
  const code = ts.transpileModule(readFileSync(file, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.React }
  }).outputText;
  const context = vm.createContext({ exports: {}, require(name) {
    if (!(name in imports)) throw new Error(`Unexpected import ${name}`);
    return imports[name];
  }, console: { error() {} }, process: { env: {
    NEXT_PUBLIC_SUPABASE_URL: 'https://project.test', NEXT_PUBLIC_SUPABASE_ANON_KEY: 'public-test',
    SUPABASE_SERVICE_ROLE_KEY: 'server-test', NODE_ENV: 'production'
  } }, Response, Request, URL, URLSearchParams, Date, JSON, AbortSignal, DOMException, fetch, setTimeout, clearTimeout, ...overrides });
  vm.runInContext(code, context);
  return context.exports;
}
const next = { NextResponse: { json: (body, opts) => Response.json(body, opts) } };
const recovery = moduleAt('lib/auth/service-recovery.ts');
const compact = moduleAt('lib/qb/compact-progress.ts');
const pastPaperSettings = moduleAt('lib/tmua/past-paper-settings.ts');
const user = { id: 'owner-one', email: 'owner@example.test' };
let authError = null, authThrows = false, tableError = null, eventFailOnce = false;
let writeCount = 0, rpcCount = 0, canonicalLookups = 0;
const eventIds = new Set(), storedRows = new Map(), options = [], pagesRead = [];
let retryDisabled = 0;
const history = Array.from({ length: 1205 }, (_, i) => ({
  question_id: String(i + 1).padStart(5, '0'), status: 'correct', selected_answer: 'A',
  flagged: i === 1204, time_spent: 31, submission_id: `submission-${i}`
}));
function tableQuery(table) {
  let range, selection = '', qids = [];
  const q = {
    retry(value) { assert.equal(value, false); retryDisabled++; return q; },
    select(columns) { selection = columns; return q; }, eq() { return q; }, ilike() { return q; },
    or() { return q; }, order() { return q; }, limit() { return q; }, maybeSingle() { return q; },
    in(_field, values) { qids = values; return q; },
    range(from, to) { range = [from, to]; return q; },
    async upsert(rows) {
      writeCount++;
      if (table === 'tmua_qb_attempt_events') {
        if (eventFailOnce) { eventFailOnce = false; return { error: { message: 'offline' } }; }
        for (const row of rows) eventIds.add(row.client_event_id);
      } else {
        for (const row of rows) storedRows.set(row.question_id, row);
      }
      return { error: null };
    },
    then(resolve, reject) {
      try {
        if (table.startsWith('esat_')) {
          canonicalLookups++;
          return Promise.resolve({ data: tableError ? null : qids.map(qid => ({ qid, topic: 'Physics',
            difficulty: 3, answer: 'A', is_active: true })), error: tableError }).then(resolve, reject);
        }
        if (table === 'qb_progress') {
          pagesRead.push(range);
          assert.ok(range, 'Progress history must use explicit pagination');
          return Promise.resolve({ data: history.slice(range[0], range[1] + 1), error: tableError }).then(resolve, reject);
        }
        if (table === 'student_access') return Promise.resolve({ data: [{ approved: true }], error: tableError }).then(resolve, reject);
        if (table === 'user_progress') return Promise.resolve({ data: { data: { parsed: { answers: {} } } }, error: null }).then(resolve, reject);
        throw new Error(`Unexpected read: ${table} ${selection}`);
      } catch (e) { return Promise.reject(e).then(resolve, reject); }
    }
  };
  return q;
}
const db = { auth: { async getUser() {
  if (authThrows) throw new Error('Connection lost');
  return { data: { user: authError?.name === 'AuthSessionMissingError' ? null : user }, error: authError };
} }, from: tableQuery, async rpc() { rpcCount++; return { data: '2026-09-20T00:00:00Z', error: null }; } };
const createClient = (_url, _key, opts) => { options.push(opts); return db; };
const common = { 'next/server': next, '@supabase/ssr': { createServerClient: createClient },
  'next/headers': { cookies: async () => ({ get() {}, set() {}, getAll() { return []; } }) },
  '@/lib/auth/service-recovery': recovery };
const save = moduleAt('app/api/qb/progress/save/route.ts', { ...common,
  '@/app/api/esat/qb/_server': { ESAT_TABLE_CANDIDATES: ['esat_qb_questions', 'esat_questions'], adminClient: () => db }
});
const load = moduleAt('app/api/qb/progress/load/route.ts', common);
const appState = moduleAt('app/api/qb/user-progress/route.ts', {
  '@/utils/supabase/server': { supabaseServer: async () => db },
  '@/lib/auth/service-recovery': recovery, '@/lib/qb/compact-progress': compact
});
const post = (route, body) => route.POST(new Request('https://portal.test/api/progress', {
  method: 'POST', body: JSON.stringify(body)
}));
const tmuaBody = { product: 'tmua-question-bank', identity_version: 'tmua-display-order-v1',
  expected_user_id: user.id, updates: [{ question_id: '1205', status: 'correct', selected_answer: 'H',
    flagged: true, answer_elapsed_seconds: 45, submission_id: 'immutable-submission' }] };
const stateBody = { product: 'tmua-question-bank', version: 2, expected_user_id: user.id,
  patch: { answers: { '1205': { selected: 'H', checked: true, solution_html: 'catalogue content' } } } };
for (const expected of ['another-owner', null, '']) {
  const before = writeCount + rpcCount;
  for (const [route, body] of [[save, tmuaBody], [appState, stateBody]]) {
    const response = await post(route, { ...body, expected_user_id: expected });
    assert.equal(response.status, 409); assert.equal((await response.json()).code, 'ACCOUNT_CHANGED');
  }
  assert.equal(writeCount + rpcCount, before, 'Account mismatch must make no writes');
}
assert.equal((await post(save, tmuaBody)).status, 200);
assert.equal(storedRows.get('1205').submission_id, 'immutable-submission');
assert.equal(storedRows.get('1205').selected_answer, 'H');
assert.equal(storedRows.get('1205').answer_elapsed_seconds, 45);
assert.equal((await post(appState, stateBody)).status, 200);
// Older open tabs remain compatible, while newer writes are bound to an owner.
const legacy = { ...tmuaBody }; delete legacy.expected_user_id;
assert.equal((await post(save, legacy)).status, 200);
const legacyState = { ...stateBody }; delete legacyState.expected_user_id;
assert.equal((await post(appState, legacyState)).status, 200);

const loaded = await load.GET(new Request('https://portal.test/api/qb/progress/load?product=tmua-question-bank'));
assert.equal(loaded.status, 200); assert.equal(loaded.headers.get('Cache-Control'), 'no-store');
const payload = await loaded.json();
assert.equal(payload.user_id, user.id); assert.equal(Object.keys(payload.progress).length, 1205);
assert.equal(payload.progress['01205'].flagged, true); assert.deepEqual(pagesRead, [[0, 999], [1000, 1999]]);

const esatBody = { product: 'esat-question-bank', identity_version: 'esat-qid-v1',
  expected_user_id: user.id, updates: [{ question_id: 'ESAT-PHY-0026', status: 'correct',
    selected_answer: 'A', answer_elapsed_seconds: 45, submission_id: 'unique-esat-submission' }] };
eventFailOnce = true;
assert.equal((await post(save, esatBody)).status, 503, 'A partial save must signal retry');
assert.equal((await post(save, esatBody)).status, 200);
assert.equal((await post(save, esatBody)).status, 200);
assert.equal(eventIds.size, 1, 'Retry preserves the same immutable predictor event identity');
assert.equal(storedRows.get('ESAT-PHY-0026').submission_id, 'unique-esat-submission');

canonicalLookups = 0; tableError = { code: '57014', message: 'Connection timeout' };
const unavailable = await post(save, esatBody);
assert.equal(unavailable.status, 503); assert.equal(unavailable.headers.get('Retry-After'), '30');
assert.equal(canonicalLookups, 1, 'An outage must not fan out across compatibility table names');
tableError = null;
for (const failure of ['returned', 'thrown']) {
  authError = failure === 'returned' ? { name: 'AuthRetryableFetchError' } : null;
  authThrows = failure === 'thrown';
  for (const [route, body] of [[save, tmuaBody], [appState, stateBody]]) {
    const response = await post(route, body); assert.equal(response.status, 503);
    assert.equal(response.headers.get('Retry-After'), '30');
    assert.equal((await response.json()).stack, undefined);
  }
  assert.equal((await load.GET(new Request('https://portal.test/api/qb/progress/load'))).status, 503);
}
authThrows = false; authError = { name: 'AuthSessionMissingError' };
assert.equal((await post(save, tmuaBody)).status, 401);
authError = null;

// Client constructors should not perform hidden retries behind the controlled outbox.
const serverClient = moduleAt('lib/supabase/server.ts', common);
await serverClient.createSupabaseServerClient();
const browserClient = moduleAt('utils/supabase/browser.ts', {
  '@supabase/ssr': { createBrowserClient: createClient }, '@/lib/auth/service-recovery': recovery
});
browserClient.supabaseBrowser();
for (const helperFile of ['app/api/esat/qb/_server.ts', 'app/api/tmua/qb/_server.ts']) {
  const helper = moduleAt(helperFile, { ...common,
    '@supabase/supabase-js': { createClient }, '@/utils/supabase/server': { supabaseServer: async () => db }
  });
  helper.adminClient();
  authError = { name: 'AuthRetryableFetchError' };
  const result = await (helper.requireESATAccess || helper.requireTmuaAccess)();
  assert.equal(result.response.status, 503, `${helperFile}: transient auth is not an access denial`);
  authError = { name: 'AuthSessionMissingError' };
  assert.equal((await (helper.requireESATAccess || helper.requireTmuaAccess)()).response.status, 401);
  authError = null;
}
// Refresh cookies must survive a later access-service outage and a redirect.
let refreshedCookies;
const cookieProxy = moduleAt('proxy.ts', {
  'next/server': { NextResponse }, '@/lib/auth/service-recovery': recovery,
  '@supabase/ssr': { createServerClient: (_url, _key, opts) => {
    refreshedCookies = opts.cookies;
    return { ...db, auth: { async getUser() {
      refreshedCookies.setAll([{ name: 'sb-session', value: 'refreshed-token',
        options: { path: '/', httpOnly: true, secure: true, sameSite: 'lax' } }]);
      return { data: { user }, error: null };
    } } };
  } }
});
tableError = { message: 'Entitlements unavailable' };
const accessFailure = await cookieProxy.proxy(new NextRequest('https://portal.test/esat-question-bank/index.html'));
assert.equal(accessFailure.status, 503);
assert.equal(accessFailure.cookies.get('sb-session').value, 'refreshed-token');
assert.equal(accessFailure.cookies.get('sb-session').httpOnly, true);
tableError = null;
assert.ok(options.length > 3);
for (const opts of options) {
  assert.equal(opts.global.fetch, recovery.serviceFetch);
}
assert.ok(retryDisabled > 5);
// Exercise the actual installed SDK (rather than assuming documentation options
// are available) and the production fetch wrapper against controlled failures.
let networkCalls = 0;
const failingFetch = moduleAt('lib/auth/service-recovery.ts', {}, {
  fetch: async () => { networkCalls++; return new Response('unavailable', { status: 503 }); }
});
const actual = createActualClient('https://project.test', 'public-key', {
  auth: { persistSession: false, autoRefreshToken: false }, global: { fetch: failingFetch.serviceFetch }
});
const failedRead = await actual.from('qb_progress').select('question_id').retry(false);
assert.equal(failedRead.status, 503); assert.equal(networkCalls, 1);
networkCalls = 0;
const timedFetch = moduleAt('lib/auth/service-recovery.ts', {}, {
  AbortSignal: { timeout: () => AbortSignal.timeout(5), any: signals => AbortSignal.any(signals) },
  fetch: (_input, init) => {
    networkCalls++;
    return new Promise((_resolve, reject) => {
      if (init.signal.aborted) reject(init.signal.reason);
      else init.signal.addEventListener('abort', () => reject(init.signal.reason), { once: true });
    });
  }
});
const timeoutClient = createActualClient('https://project.test', 'public-key', {
  auth: { persistSession: false, autoRefreshToken: false }, global: { fetch: timedFetch.serviceFetch }
});
let watchdog;
const timedRead = await Promise.race([
  timeoutClient.from('qb_progress').select('question_id'),
  new Promise((_resolve, reject) => { watchdog = setTimeout(() => reject(Error('Abort was retried or did not finish')), 500); })
]);
clearTimeout(watchdog);
assert.equal(timedRead.status, 0); assert.equal(networkCalls, 1);
assert.match(timedRead.error.message, /AbortError/);
// The actual catalogue handlers distinguish a missing question from an outage,
// and try legacy table names only when the canonical table does not exist.
let questionCalls = 0, questionError = null, missingQuestion = false, legacyTable = false;
const questionRow = { qid: 'ESAT-PHY-0026', id: '00000000-0000-4000-8000-000000000026',
  answer: 'A', solution_html: '<p>Exact worked solution</p>', options: ['A', 'B'], is_active: true };
const questionDb = { from(table) {
  let isList = false;
  const q = { select: () => q, eq: () => q, order: () => q, maybeSingle: () => q,
    range: () => { isList = true; return q; }, retry(value) { assert.equal(value, false); return q; },
    then(resolve, reject) {
      questionCalls++;
      const error = legacyTable && table === 'esat_qb_questions'
        ? { code: 'PGRST205', message: 'Table missing' } : questionError;
      return Promise.resolve({ error, data: error ? null : isList ? [questionRow] : missingQuestion ? null : questionRow }).then(resolve, reject);
    }
  }; return q;
} };
const questionHelpers = { ESAT_TABLE_CANDIDATES: ['esat_qb_questions', 'esat_questions'],
  adminClient: () => questionDb, normaliseQuestion: row => row,
  requireESATAccess: async () => ({ ok: true }), requireTmuaAccess: async () => ({ ok: true }),
  json: (body, status = 200) => Response.json(body, { status, headers: status === 503 ? { 'Retry-After': '30' } : {} }) };
for (const exam of ['tmua', 'esat']) {
  const question = moduleAt(`app/api/${exam}/qb/question/route.ts`, { '../_server': questionHelpers });
  const list = moduleAt(`app/api/${exam}/qb/list/route.ts`, { '../_server': questionHelpers });
  questionError = { code: '57014', message: 'Database timeout' }; questionCalls = 0;
  assert.equal((await question.GET(new Request('https://portal.test/q?qid=ESAT-PHY-0026'))).status, 503);
  assert.equal(questionCalls, 1);
  questionCalls = 0; assert.equal((await list.GET()).status, 503); assert.equal(questionCalls, 1);
  questionError = null; missingQuestion = true; questionCalls = 0;
  assert.equal((await question.GET(new Request('https://portal.test/q?qid=ESAT-PHY-0026'))).status, 404);
  assert.equal(questionCalls, 1);
  missingQuestion = false;
  assert.equal((await question.GET(new Request('https://portal.test/q?qid=ESAT-PHY-0026'))).status, 200);
  if (exam === 'esat') {
    legacyTable = true; questionCalls = 0;
    assert.equal((await question.GET(new Request('https://portal.test/q?qid=ESAT-PHY-0026'))).status, 200);
    assert.equal(questionCalls, 2); legacyTable = false;
  }
}
const checker = moduleAt('app/api/tmua/qb/check/route.ts', { '../_server': questionHelpers });
questionError = { code: '57014', message: 'Database timeout' };
assert.equal((await post(checker, { qid: questionRow.qid, selected: 'A' })).status, 503);
questionError = null;
const checked = await (await post(checker, { qid: questionRow.qid, selected: 'A' })).json();
assert.equal(checked.isCorrect, true); assert.equal(checked.answer, 'A');
assert.equal(checked.solution_html, questionRow.solution_html);
assert.equal((await (await post(checker, { qid: questionRow.qid, selected: 'B' })).json()).isCorrect, false);

// Execute the real nested TMUA dashboard effect and render branches. An access
// query failure must render the retry control, never the empty-products screen.
async function dashboardScenario(failure, accessRows = []) {
  let stateIndex = 0, effectIndex = 0;
  const states = [], effects = [], redirects = [];
  let nextFailure = failure;
  const react = {
    createElement: (type, props, ...children) => ({ type, props: { ...props, children } }),
    useState(initial) {
      const index = stateIndex++;
      if (!(index in states)) states[index] = typeof initial === 'function' ? initial() : initial;
      return [states[index], value => { states[index] = typeof value === 'function' ? value(states[index]) : value; }];
    },
    useMemo: factory => factory(), useEffect: effect => { effects[effectIndex++] = effect; }
  };
  function RetryComponent() {}
  const dashboardDb = { auth: { getSession: async () => {
    if (nextFailure === 'session-throws') throw new Error('Network unavailable');
    return { data: { session: { user } }, error: nextFailure === 'session-error' ? { name: 'AuthRetryableFetchError' } : null };
  } }, from() {
    const q = { select: () => q, ilike: () => q, eq: () => q, or: () => q,
      retry: async value => { assert.equal(value, false); return { data: accessRows, error: nextFailure === 'access-error' ? { message: 'Database offline' } : null }; } };
    return q;
  } };
  const component = moduleAt('app/dashboard/DashboardClient.tsx', {
    react: { __esModule: true, default: react, ...react },
    'next/navigation': { useRouter: () => ({ replace: value => redirects.push(value) }) },
    '@/utils/supabase/browser': { supabaseBrowser: () => dashboardDb },
    './dashboard.module.css': { default: {} }, './TmuaPredictionStrip': { default() {} },
    '../components/ServiceRetry': { default: RetryComponent }, '@/lib/auth/service-recovery': recovery,
    '@/lib/tmua/past-paper-settings': pastPaperSettings
  }, { window: { location: { href: 'https://portal.test/dashboard' }, history: { replaceState() {} } } });
  function render() { stateIndex = 0; effectIndex = 0; return component.default({ uiMark: 'test' }); }
  render(); effects[0]();
  for (let i = 0; i < 20; i++) await Promise.resolve();
  let view = render();
  if (failure) {
    assert.equal(view.type, RetryComponent, `${failure}: must show the temporary-service retry control`);
    assert.equal(redirects.length, 0, 'Transient failure must retain the signed-in session');
    nextFailure = null; view.props.onRetry(); render(); effects[0]();
    for (let i = 0; i < 20; i++) await Promise.resolve();
    view = render();
    assert.notEqual(view.type, RetryComponent, 'Retry recovers when access service is available');
  }
  return JSON.stringify(view);
}
for (const failure of ['session-throws', 'session-error', 'access-error']) await dashboardScenario(failure);
assert.match(await dashboardScenario(null), /No products enabled/, 'A successful empty entitlement response remains a genuine no-access state');
assert.doesNotMatch(await dashboardScenario(null, [{ product: 'tmua-question-bank' }]), /No products enabled/);
console.log('PASS: Owner-bound writes reject account changes without mutation; >1,000 progress rows retained; partial-save retry preserves event identity; transient outages return503 without table-fallback fanout; critical reads disable SDK retries and timeouts abort without retry.');
