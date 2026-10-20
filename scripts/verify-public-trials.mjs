import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';

// Real route code, isolated doubles only: this script cannot grant live access
// or send mail. Unexpected imports/network/database tables fail immediately.
const BASE_TIME = Date.parse('2026-10-20T12:00:00Z');
let now = BASE_TIME;
class Clock extends Date {
  constructor(...args) { super(...(args.length ? args : [now])); }
  static now() { return now; }
}
const env = {
  NODE_ENV: 'production', NEXT_PUBLIC_SUPABASE_URL: 'https://project.invalid',
  NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: 'public-test', SUPABASE_SERVICE_ROLE_KEY: 'service-test',
};
function moduleAt(file, imports = {}, extras = {}) {
  const code = ts.transpileModule(readFileSync(file, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText;
  const ctx = vm.createContext({
    exports: {}, require(name) { assert.ok(name in imports, `Unexpected import: ${name}`); return imports[name]; },
    process: { env }, console: { error() {} }, Request, Response, URL, TextDecoder, Uint8Array,
    RangeError, Date: Clock, AbortController, setTimeout, clearTimeout, ...extras,
  });
  vm.runInContext(code, ctx);
  return ctx.exports;
}
const plain = value => JSON.parse(JSON.stringify(value));
const trialRows = new Map();
const rpcCalls = [];
const queryCalls = [];
const loginMails = [];
const welcomeMails = [];
let grantFailure, claimFailure, otpFailure, welcomeOk = true, markerFailure, uniqueFailure;
const tableKey = (program, email) => `${program}:${email}`;
function query(table) {
  assert.match(table, /^(tmua|esat)_free_trials$/);
  const program = table.split('_')[0];
  const conditions = [];
  let patch;
  const q = {
    update(value) { patch = value; assert.deepEqual(Object.keys(value), ['updated_at']); return q; },
    eq(key, value) { conditions.push(['eq', key, value]); return q; },
    gt(key, value) { conditions.push(['gt', key, value]); return q; },
    lt(key, value) { conditions.push(['lt', key, value]); return q; },
    select(columns) { assert.equal(columns, 'id'); return q; },
    retry(value) { assert.equal(value, false); return q; },
    then(resolve, reject) {
      try {
        queryCalls.push({ table, patch: plain(patch), conditions: plain(conditions) });
        if (claimFailure) return Promise.resolve({ data: null, error: claimFailure }).then(resolve, reject);
        const matches = [...trialRows.values()].filter(row => row.program === program &&
          conditions.every(([op, key, value]) => op === 'eq' ? row[key] === value :
            op === 'lt' ? row[key] < value : row[key] > value));
        for (const row of matches) Object.assign(row, patch);
        return Promise.resolve({ data: matches.map(row => ({ id: row.id })), error: null }).then(resolve, reject);
      } catch (error) { return Promise.reject(error).then(resolve, reject); }
    },
  };
  return q;
}
const db = {
  from: query,
  rpc(name, args) {
    return { retry(value) {
      assert.equal(value, false);
      rpcCalls.push({ name, args: plain(args) });
      if (name.startsWith('mark_')) return Promise.resolve({ data: null, error: markerFailure });
      assert.match(name, /^grant_(tmua|esat)_free_trial$/);
      assert.deepEqual(Object.keys(args).sort(), ['p_email', 'p_student_name']);
      if (uniqueFailure) { uniqueFailure = false; return Promise.resolve({ error: { code: '23505' } }); }
      if (grantFailure) return Promise.resolve({ error: grantFailure });
      const program = name.split('_')[1];
      const key = tableKey(program, args.p_email);
      let row = trialRows.get(key);
      let status = 'trial_already_active';
      if (!row) {
        status = 'trial_started';
        row = { id: key, program, email: args.p_email, status: 'active',
          started_at: new Clock().toISOString(), updated_at: new Clock().toISOString(),
          expires_at: new Clock(now + 48 * 3_600_000).toISOString() };
        trialRows.set(key, row);
      } else if (Date.parse(row.expires_at) <= now) status = 'trial_already_used';
      return Promise.resolve({ data: [{ out_status: status,
        out_started_at: row.started_at, out_expires_at: row.expires_at }], error: null });
    } };
  },
};
const shared = moduleAt('app/api/public/_trial.ts', {
  '@supabase/supabase-js': { createClient(_url, key) {
    return key === 'service-test' ? db : { auth: { async signInWithOtp(input) {
      loginMails.push(plain(input));
      if (otpFailure === 'throw') throw new Error('Provider timeout');
      return { error: otpFailure };
    } } };
  } },
  '@/lib/auth/service-recovery': { serviceFetch() { throw new Error('Unexpected network'); } },
  '@/lib/server/trial-welcome-email': { async sendTrialWelcomeEmail(input) {
    welcomeMails.push(plain(input)); return { ok: welcomeOk };
  } },
});
const routes = Object.fromEntries(['tmua', 'esat'].map(program => [program,
  moduleAt(`app/api/public/${program}-free-trial/route.ts`, { '../_trial': shared })]));
function request(body, overrides = {}) {
  return new Request('https://portal.invalid/api/public/free-trial', {
    method: 'POST', headers: { Origin: 'https://www.thrivingscholars.com', 'Content-Type': 'application/json' },
    body: JSON.stringify(body), ...overrides,
  });
}
const post = (program, email, rest = {}) => routes[program].POST(request({
  email, student_name: 'Example Student', program, ...rest,
}));

for (const program of ['tmua', 'esat']) {
  const email = `${program}_student@example.com`;
  const first = await post(program, ` ${email.toUpperCase()} `);
  assert.equal(first.status, 200);
  assert.equal(first.headers.get('access-control-allow-origin'), 'https://www.thrivingscholars.com');
  assert.match(first.headers.get('cache-control'), /no-store/);
  const data = await first.json();
  assert.equal(data.status, 'trial_started');
  assert.equal(data.login_email_sent, true);
  assert.equal(data.welcome_email_sent, true);
  assert.equal(Date.parse(data.expires_at) - now, 48 * 3_600_000);
  assert.equal(data.dashboard_url, `https://apps.thrivingscholars.com/${program === 'tmua' ? 'dashboard' : 'esat'}`);
  assert.equal(loginMails.at(-1).email, email);
  assert.equal(loginMails.at(-1).options.shouldCreateUser, true);
  assert.ok(loginMails.at(-1).options.emailRedirectTo.endsWith(program === 'tmua' ? 'next=%2Fdashboard' : 'next=%2Fesat'));
  assert.equal(welcomeMails.at(-1).program, program);
  assert.equal(welcomeMails.at(-1).expiresAt, data.expires_at);

  const sent = loginMails.length;
  const repeat = await (await post(program, email)).json();
  assert.equal(repeat.status, 'trial_already_active');
  assert.equal(repeat.expires_at, data.expires_at);
  assert.equal(repeat.email_resend_limited, true);
  assert.equal(repeat.login_email_sent, false);
  assert.equal(repeat.welcome_email_sent, false);
  assert.equal(repeat.retry_after_seconds, 300);
  assert.equal(loginMails.length, sent);
  assert.match(repeat.message, /not sent another email/);

  now += 301_000;
  const attempts = await Promise.all(Array.from({ length: 8 }, () => post(program, email)));
  const results = await Promise.all(attempts.map(response => response.json()));
  assert.equal(results.filter(result => result.login_email_sent).length, 1, 'Only one concurrent resend wins');
  assert.equal(loginMails.length, sent + 1);
  assert.ok(results.every(result => result.expires_at === data.expires_at));
  assert.ok(queryCalls.filter(call => call.table === `${program}_free_trials`)
    .every(call => call.conditions.some(([op, field]) => op === 'gt' && field === 'expires_at')));
}

const beforeInvalid = rpcCalls.length;
for (const [body, status] of [[null, 400], [[], 400], ['not an object', 400],
  [{ email: 'wrong' }, 400], [{ email: 'ok@example.com', program: 'esat' }, 400],
  [{ email: 'ok@example.com', student_name: 'x'.repeat(121) }, 400],
  [{ email: 'ok@example.com', student_name: 'bad\nname' }, 400]]) {
  assert.equal((await routes.tmua.POST(request(body))).status, status);
}
assert.equal((await routes.tmua.POST(request({ email: 'ok@example.com' }, { headers: {
  Origin: 'https://evil.invalid', 'Content-Type': 'application/json',
} }))).status, 403);
assert.equal((await routes.tmua.POST(request({ email: 'ok@example.com' }, { headers: {
  Origin: 'https://www.thrivingscholars.com', 'Content-Type': 'text/plain',
} }))).status, 415);
assert.equal((await routes.tmua.POST(request({}, { body: '{"email":' }))).status, 400);
assert.equal((await routes.tmua.POST(request({ email: 'ok@example.com', extra: 'x'.repeat(5_000) }))).status, 413);
assert.equal(rpcCalls.length, beforeInvalid);
const preflight = await routes.tmua.OPTIONS(new Request('https://portal.invalid', {
  method: 'OPTIONS', headers: { Origin: 'https://thrivingscholars.com' },
}));
assert.equal(preflight.status, 204);
assert.equal(preflight.headers.get('access-control-allow-origin'), 'https://thrivingscholars.com');
assert.equal((await routes.tmua.OPTIONS(new Request('https://portal.invalid'))).status, 403);

now = BASE_TIME + 49 * 3_600_000;
const expiredMailCount = loginMails.length;
const expired = await post('tmua', 'tmua_student@example.com');
assert.equal(expired.status, 409);
assert.equal((await expired.json()).status, 'trial_already_used');
assert.equal(loginMails.length, expiredMailCount);
grantFailure = { code: 'database_down' };
assert.equal((await post('esat', 'failure@example.com')).status, 500);
grantFailure = undefined;
claimFailure = { code: 'database_down' };
const noClaim = await (await post('esat', 'claim@example.com')).json();
assert.equal(noClaim.ok, true);
assert.equal(noClaim.login_email_sent, false);
assert.equal(loginMails.length, expiredMailCount);
claimFailure = undefined;
otpFailure = 'throw';
const otpFailed = await (await post('esat', 'otp@example.com')).json();
assert.equal(otpFailed.ok, true);
assert.equal(otpFailed.login_email_sent, false);
assert.equal(otpFailed.welcome_email_sent, true);
assert.match(otpFailed.message, /request a sign-in link/);
otpFailure = undefined;
welcomeOk = false;
markerFailure = { code: 'marker_down' };
const welcomeFailed = await (await post('tmua', 'welcome@example.com')).json();
assert.equal(welcomeFailed.login_email_sent, true);
assert.equal(welcomeFailed.welcome_email_sent, false);
assert.match(welcomeFailed.message, /secure sign-in link/);
welcomeOk = true;
markerFailure = undefined;
uniqueFailure = true;
assert.equal((await post('tmua', 'race@example.com')).status, 200);

let payload, emailResponse = { ok: true };
const welcome = moduleAt('lib/server/trial-welcome-email.ts', {}, {
  fetch: async (url, options) => {
    assert.equal(url, 'https://api.emailjs.com/api/v1.0/email/send');
    payload = JSON.parse(options.body);
    return emailResponse;
  },
});
for (const program of ['tmua', 'esat']) {
  const input = { program, studentName: 'Example', studentEmail: 'test@example.com',
    expiresAt: '2026-10-22T12:00:00Z' };
  assert.equal((await welcome.sendTrialWelcomeEmail(input)).ok, true);
  assert.equal(payload.template_id, 'template_whjida8');
  assert.equal(payload.service_id, 'service_5l4w8x2');
  assert.equal(payload.template_params.exam_name, program.toUpperCase());
  assert.equal(payload.template_params.access_duration, '2 days');
  assert.equal(payload.template_params.login_url, `https://apps.thrivingscholars.com/${program === 'tmua' ? 'dashboard' : 'esat'}`);
  assert.match(payload.template_params.expires_at, /22 Oct 2026/);
  assert.equal(payload.accessToken, undefined);
}
emailResponse = { ok: false, status: 400 };
assert.equal((await welcome.sendTrialWelcomeEmail({ program: 'esat', studentName: '', studentEmail: 'test@example.com', expiresAt: null })).ok, false);

// Execute the actual access helper and classes route. No class links may be read
// until auth and the correct, approved, unexpired product have been checked.
let user = null, accessRows = [], accessError = null, selectedProduct, expiryFilter, emailFilter, classReads = 0;
const accessDb = {
  auth: { getUser: async () => ({ data: { user }, error: null }) },
  from(table) {
    assert.equal(table, 'student_access');
    const q = { select() { return q; }, ilike(_field, value) { emailFilter = value; return q; },
      eq(field, value) { if (field === 'product') selectedProduct = value;
        if (field === 'approved') assert.equal(value, true); return q; },
      or(value) { expiryFilter = value; return q; }, limit(value) { assert.equal(value, 1); return q; },
      retry: async () => ({ data: accessRows, error: accessError }) };
    return q;
  },
};
const recovery = { withServiceTimeout: promise => promise, serviceFetch() {},
  isMissingSession: () => false };
const access = moduleAt('app/api/esat/qb/_server.ts', {
  '@supabase/supabase-js': { createClient() { throw new Error('Unexpected admin access'); } },
  '@/utils/supabase/server': { supabaseServer: async () => accessDb },
  '@/lib/auth/service-recovery': recovery,
});
const classes = moduleAt('app/api/esat/classes/route.ts', {
  'next/server': { NextResponse: { json: Response.json } },
  '@supabase/supabase-js': { createClient: () => ({ from(table) {
    classReads++; assert.equal(table, 'esat_class_sessions');
    const q = { select() { return q; }, eq() { return q; }, order() { return q; },
      retry: async () => ({ data: [], error: null }) }; return q;
  } }) },
  '@/app/api/esat/qb/_server': access, '@/lib/auth/service-recovery': recovery,
});
assert.equal((await classes.GET()).status, 401);
assert.equal(classReads, 0);
user = { id: 'student', email: 'student_one@example.com' };
assert.equal((await classes.GET()).status, 403);
assert.equal(classReads, 0);
assert.equal(selectedProduct, 'esat-classes');
assert.equal(emailFilter, 'student\\_one@example.com');
assert.match(expiryFilter, /^expires_at\.is\.null,expires_at\.gt\./);
accessError = { message: 'database unavailable' };
assert.equal((await classes.GET()).status, 503);
assert.equal(classReads, 0);
accessError = null;
accessRows = [{ approved: true }];
const approved = await classes.GET();
assert.equal(approved.status, 200);
assert.equal(classReads, 1);
assert.equal(approved.headers.get('cache-control'), 'no-store');
assert.equal((await access.requireESATAccess()).ok, true);
assert.equal(selectedProduct, 'esat-question-bank');
const proxy = readFileSync('proxy.ts', 'utf8');
assert.match(proxy, /prefix: "\/esat-classes", product: "esat-classes"/);
assert.match(proxy, /"\/esat-classes\/:path\*"/);
assert.doesNotMatch(readFileSync('app/api/public/_trial.ts', 'utf8'), /\.from\(["']student_access/);

// Request-time expiry checks protect open TMUA tabs after the 48-hour page
// gate has already passed. Run the real helper and submission route, with no
// network, database writes, score changes or live authentication.
let tmuaAccess = { approved: true, expires_at: null }, tmuaAccessError = null;
let tmuaAuthError = null, tmuaEmail = 'student_one@example.com';
const accessSelections = [], accessFilters = [], submitTables = [];
const tmuaDb = {
  auth: { getUser: async () => ({
    data: { user: tmuaEmail ? { id: 'student', email: tmuaEmail } : null }, error: tmuaAuthError,
  }) },
  from(table) {
    submitTables.push(table);
    assert.ok(['student_access', 'tmua_test_catalog'].includes(table), 'Denied requests must not write attempts');
    const q = {
      select(value) { if (table === 'student_access') accessSelections.push(value); return q; },
      eq(field, value) { if (table === 'student_access') accessFilters.push([field, value]); return q; },
      ilike(field, value) { accessFilters.push([field, value]); return q; },
      or(value) { accessFilters.push(['expiry', value]); return q; },
      limit(value) { assert.equal(value, 1); return q; }, maybeSingle() { return q; },
      retry(value) { assert.equal(value, false); return q; },
      then(resolve, reject) {
        const result = table === 'tmua_test_catalog'
          ? { data: { test_id: 'known-tmua', title: 'Mock', paper: 'full', expected_questions: 40 }, error: null }
          : { data: tmuaAccess, error: tmuaAccessError };
        return Promise.resolve(result).then(resolve, reject);
      },
    };
    return q;
  },
};
const tmuaHelper = moduleAt('app/api/tmua/qb/_server.ts', {
  'next/server': { NextResponse: { json: Response.json } },
  'next/headers': { cookies: async () => ({ getAll: () => [] }) },
  '@supabase/supabase-js': { createClient: () => tmuaDb },
  '@supabase/ssr': { createServerClient: () => tmuaDb },
  '@/lib/auth/service-recovery': recovery,
});
let reachedScoringValidation = 0, submissionExam = 'tmua';
const submission = moduleAt('app/api/practice-tests/submit/route.ts', {
  'next/server': { NextResponse: { json: Response.json } },
  '@/lib/server/esat-canonical-tests': { getCanonicalEsatTest: () =>
    submissionExam === 'esat' ? { expectedQuestions: 81 } : null },
  '@/lib/server/esat-score-estimates': {}, '@/lib/server/esat-october-2026-tests': {},
  '@/lib/server/tmua-canonical-tests': { getCanonicalTmuaTest: () =>
    submissionExam === 'tmua' ? { expectedQuestions: 40 } : null },
  '@/lib/server/tmua-predictive-2026': { TMUA_PREDICTIVE_2026_ID: 'predictive-tmua' },
  '@/lib/supabase/server': { createSupabaseServerClient: async () => tmuaDb },
  '@/lib/tmua/past-paper-settings': { validateTmuaPastPaperSettings() {} },
  '@/lib/server/practice-standard-time': { resolvePracticeSettings() {
    reachedScoringValidation++;
    throw new Error('Isolated test stops before scoring and persistence');
  } },
});
const submit = () => submission.POST(new Request('https://portal.invalid/api/practice-tests/submit', {
  method: 'POST', body: JSON.stringify({ test_id: 'known-tmua' }),
}));
for (const [row, allowed] of [
  [{ approved: true, expires_at: new Clock(now - 1).toISOString() }, false],
  [{ approved: true, expires_at: new Clock().toISOString() }, false],
  [{ approved: true, expires_at: 'invalid' }, false],
  [{ approved: true }, false], [null, false],
  [{ approved: false, expires_at: null }, false],
  [{ approved: true, expires_at: null }, true],
  [{ approved: true, expires_at: new Clock(now + 60_000).toISOString() }, true],
  [{ approved: true, expires_at: new Clock(now + 90 * 86_400_000).toISOString() }, true],
]) {
  tmuaAccess = row;
  const accessResult = await tmuaHelper.requireTmuaAccess();
  assert.equal(accessResult.ok, allowed);
  if (!allowed) assert.equal(accessResult.response.status, 403);
  const before = reachedScoringValidation;
  const submitResult = await submit();
  assert.equal(submitResult.status, allowed ? 400 : 403);
  assert.equal(reachedScoringValidation - before, allowed ? 1 : 0,
    'Expired/unapproved access must stop before scoring and database writes');
}
tmuaAccessError = { message: 'Database unavailable' };
assert.equal((await tmuaHelper.requireTmuaAccess()).response.status, 503);
assert.equal((await submit()).status, 503);
tmuaAccessError = null;
// This is a shared endpoint. An ESAT entry in the shared catalogue must not
// acquire a TMUA entitlement requirement, nor should generic legacy tests.
tmuaAccess = null;
for (const exam of ['esat', 'legacy']) {
  submissionExam = exam;
  const before = accessSelections.length;
  const beforeValidation = reachedScoringValidation;
  assert.equal((await submit()).status, 400);
  assert.equal(accessSelections.length, before);
  assert.equal(reachedScoringValidation, beforeValidation + 1);
}
submissionExam = 'tmua';
tmuaEmail = null;
assert.equal((await tmuaHelper.requireTmuaAccess()).response.status, 401);
assert.equal((await submit()).status, 401);
assert.ok(accessSelections.every(value => value === 'approved,expires_at'));
assert.ok(accessFilters.some(([field, value]) => field === 'product' && value === 'practice-tests'));
assert.ok(accessFilters.some(([field, value]) => field === 'product' && value === 'tmua-question-bank'));
assert.ok(accessFilters.some(([field, value]) => field === 'email' && value === 'student\\_one@example.com'));
assert.ok(accessFilters.some(([field, value]) => field === 'expiry' && value.startsWith('expires_at.is.null,expires_at.gt.')));
for (const exam of ['tmua', 'esat']) {
  const miniTest = readFileSync(`public/${exam}-mini-test/index.html`, 'utf8');
  assert.doesNotMatch(miniTest, /\/api\/practice-tests\/submit/);
  assert.match(miniTest, /emailjs/i, 'Public mini-tests retain their independent anonymous email flow');
}
// Guard coverage must include every current portal test, not only full mocks:
// six topic/paper tests, nine official/specimen papers, and four full mocks.
const predictiveRegistry = moduleAt('lib/server/tmua-predictive-2026.ts');
const canonicalRegistry = moduleAt('lib/server/tmua-canonical-tests.ts', {
  './tmua-predictive-2026.ts': predictiveRegistry,
});
const dashboardIds = [...readFileSync('app/dashboard/DashboardClient.tsx', 'utf8')
  .matchAll(/test_id:\s*"([^"]+)"/g)].map(match => match[1]);
assert.equal(new Set(dashboardIds).size, 19);
for (const id of dashboardIds) {
  assert.ok(canonicalRegistry.getCanonicalTmuaTest(id), `${id}: must be covered by request-time TMUA access gate`);
}
console.log('Public TMUA/ESAT trials passed: validation, exact RPC contract, 48h/repeats, atomic cooldown, delivery failures, and ESAT class expiry protection (all isolated mocks).');
console.log('TMUA request-time trial expiry passed: QB and new mock submissions reject expired/equal/invalid expiry; permanent and longer paid access preserved; outages fail closed before scoring.');
