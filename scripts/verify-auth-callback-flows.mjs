import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';

// Synthetic tokens and injected clients ONLY. No real auth requests or sessions.
const env = {
  NEXT_PUBLIC_SUPABASE_URL: 'https://project.invalid',
  NEXT_PUBLIC_SUPABASE_ANON_KEY: 'public-test',
};
function moduleAt(file, imports = {}, extras = {}) {
  const code = ts.transpileModule(readFileSync(file, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX },
  }).outputText;
  const context = vm.createContext({
    exports: {}, require(name) { assert.ok(name in imports, `Unexpected import ${name}`); return imports[name]; },
    URL, URLSearchParams, Response, Request, process: { env },
    console: { error() { throw new Error('Auth data must not be logged'); }, log() { throw new Error('Unexpected log'); } },
    ...extras,
  });
  vm.runInContext(code, context);
  return context.exports;
}
const destinations = moduleAt('lib/auth/login-destination.ts');
let intent = null, modeError = null;
const cookieWrites = [];
const exchanges = [];
const verifications = [];
function redirect(url) {
  const response = new Response(null, { status: 307, headers: { Location: String(url) } });
  response.cookies = {
    set(name, value) { cookieWrites.push(['response', name, value]); },
    delete(name) { cookieWrites.push(['delete', name]); },
  };
  return response;
}
const callback = moduleAt('app/auth/callback/route.ts', {
  'next/server': { NextResponse: { redirect } },
  'next/headers': { cookies: async () => ({
    get(name) { assert.equal(name, destinations.LOGIN_DESTINATION_COOKIE); return intent ? { value: intent } : undefined; },
    getAll() { return []; }, set(name, value) { cookieWrites.push(['store', name, value]); },
  }) },
  '@supabase/ssr': { createServerClient(_url, _key, options) {
    function write() { options.cookies.setAll([{ name: 'session-test', value: 'synthetic-cookie', options: {} }]); }
    return { auth: {
      async exchangeCodeForSession(code) { exchanges.push(code); if (!modeError) write(); return { error: modeError }; },
      async verifyOtp(input) { verifications.push(JSON.parse(JSON.stringify(input))); if (!modeError) write(); return { error: modeError }; },
    } };
  } },
  '@/lib/auth/login-destination': destinations,
});
const runCallback = path => callback.GET(new Request(`https://apps.thrivingscholars.com${path}`));

// Existing PKCE flow remains server-side and retains cookie-write behavior.
intent = encodeURIComponent('/esat?section=question-bank');
let response = await runCallback('/auth/callback?code=synthetic-code');
assert.equal(response.headers.get('location'), 'https://apps.thrivingscholars.com/esat?section=question-bank');
assert.deepEqual(exchanges, ['synthetic-code']);
assert.equal(verifications.length, 0);
assert.ok(cookieWrites.some(([where]) => where === 'response'));
assert.ok(cookieWrites.some(([where]) => where === 'store'));
assert.ok(cookieWrites.some(([where]) => where === 'delete'));
assert.match(response.headers.get('cache-control'), /no-store/);

// Existing cross-device token_hash flow remains server-side.
response = await runCallback('/auth/callback?token_hash=synthetic-hash&type=magiclink&next=%2Fdashboard');
assert.equal(response.headers.get('location'), 'https://apps.thrivingscholars.com/dashboard');
assert.deepEqual(verifications.at(-1), { token_hash: 'synthetic-hash', type: 'magiclink' });
assert.equal(exchanges.length, 1);
modeError = { message: 'synthetic provider error' };
response = await runCallback('/auth/callback?token_hash=synthetic-hash&type=magiclink');
assert.equal(new URL(response.headers.get('location')).pathname, '/login');
assert.equal(new URL(response.headers.get('location')).searchParams.get('e'), 'invalid_or_consumed_link');
assert.doesNotMatch(response.headers.get('location'), /synthetic/);
modeError = null;

// IB returns to its own portal and keeps the selected subject on an expired link.
intent = encodeURIComponent('/ib?subject=physics-hl&view=mocks');
response = await runCallback('/auth/callback?code=synthetic-ib-code');
assert.equal(response.headers.get('location'), 'https://apps.thrivingscholars.com/ib?subject=physics-hl&view=mocks');
modeError = { message: 'synthetic provider error' };
response = await runCallback('/auth/callback?code=expired-ib-code');
assert.equal(new URL(response.headers.get('location')).pathname, '/ib-login');
assert.equal(new URL(response.headers.get('location')).searchParams.get('next'), '/ib?subject=physics-hl&view=mocks');
modeError = null;
intent = null;

// A question/solution tab survives sign-in and an expired-link retry intact.
for (const next of ['/ib/mark-scheme/ib-aa-fn-001', '/ib/question-bank/functions?difficulty=hard&calculator=no&page=2']) {
  intent = encodeURIComponent(next);
  response = await runCallback('/auth/callback?code=synthetic-deep-link');
  assert.equal(response.headers.get('location'), `https://apps.thrivingscholars.com${next}`);
  modeError = { message: 'synthetic expired link' };
  response = await runCallback('/auth/callback?code=expired-deep-link');
  assert.equal(new URL(response.headers.get('location')).pathname, '/ib-login');
  assert.equal(new URL(response.headers.get('location')).searchParams.get('next'), next);
  modeError = null;
}
intent = null;

// The server never receives fragments; no-query requests preserve them through
// a redirect whose Location has no fragment (HTTP fragment inheritance).
const authCalls = exchanges.length + verifications.length;
response = await runCallback('/auth/callback?next=%2Fesat');
const bridge = new URL(response.headers.get('location'));
assert.equal(bridge.pathname, '/auth/complete');
assert.equal(bridge.searchParams.get('next'), '/esat');
assert.equal(bridge.hash, '');
assert.equal(exchanges.length + verifications.length, authCalls);
assert.equal(response.headers.get('referrer-policy'), 'no-referrer');
assert.match(response.headers.get('cache-control'), /no-store/);
response = await runCallback('/auth/callback?next=https%3A%2F%2Fevil.invalid');
assert.equal(new URL(response.headers.get('location')).searchParams.get('next'), '/dashboard');
response = await runCallback('/auth/callback?token_hash=synthetic-hash&type=unsupported&next=%2Fesat');
assert.equal(new URL(response.headers.get('location')).pathname, '/auth/complete');
assert.doesNotMatch(response.headers.get('location'), /synthetic-hash|token_hash/);

let events, browser, setError, setThrows, missingSession, verifyError, missingUser, historyThrows;
const syntheticFragment = '#access_token=synthetic-access&refresh_token=synthetic-refresh&token_type=bearer&provider_token=discard-me';
function reset(search = '?next=%2Fesat', hash = syntheticFragment) {
  events = [];
  setError = null; setThrows = false; missingSession = false; verifyError = null; missingUser = false; historyThrows = false;
  browser = {
    location: { search, hash },
    history: { replaceState(_state, _title, path) {
      events.push(['clear', path]);
      if (historyThrows) throw new Error('history unavailable');
      const url = new URL(path, 'https://apps.thrivingscholars.com');
      browser.location.search = url.search;
      browser.location.hash = url.hash;
    } },
  };
}
function bridgeModule() {
  return moduleAt('lib/auth/implicit-callback.ts', {
    '@/lib/auth/login-destination': destinations,
    '@/utils/supabase/browser': { supabaseBrowser() {
      events.push(['create-client']);
      assert.equal(browser.location.hash, '', 'Clear fragment before any auth initialisation');
      return { auth: {
        async setSession(input) {
          events.push(['set', JSON.parse(JSON.stringify(input))]);
          if (setThrows) throw new Error('Do not log this provider error');
          return { data: { session: missingSession ? null : { access_token: 'synthetic-access' } }, error: setError };
        },
        async getUser() {
          events.push(['verify']);
          return { data: { user: missingUser ? null : { id: 'synthetic-user' } }, error: verifyError };
        },
        async signOut(input) { events.push(['sign-out', JSON.parse(JSON.stringify(input))]); return { error: null }; },
      } };
    } },
  }, { window: browser });
}
reset();
assert.equal(await bridgeModule().completeImplicitLogin(), '/esat');
assert.deepEqual(events.map(event => event[0]), ['clear', 'create-client', 'set', 'verify']);
assert.deepEqual(events[2][1], { access_token: 'synthetic-access', refresh_token: 'synthetic-refresh' });
assert.doesNotMatch(events[0][1], /synthetic|provider_token|discard-me/);

// Disallow external destinations; existing allow-listed internal query routing survives.
for (const next of ['https://evil.invalid', '//evil.invalid', '/auth/complete', '/esat\\..\\evil']) {
  reset(`?next=${encodeURIComponent(next)}`);
  assert.equal(await bridgeModule().completeImplicitLogin(), '/dashboard');
}
reset('?next=%2Fesat%3Fsection%3Dquestion-bank');
assert.equal(await bridgeModule().completeImplicitLogin(), '/esat?section=question-bank');

// Missing/invalid/duplicate/provider-error fragments never initialise an auth client.
for (const hash of ['', '#access_token=synthetic-access', '#refresh_token=synthetic-refresh',
  `${syntheticFragment}&access_token=duplicate`, `${syntheticFragment}&refresh_token=duplicate`,
  `${syntheticFragment}&error=expired&error_description=PRIVATE`,
  '#access_token=a&refresh_token=b&token_type=unsupported']) {
  reset('?next=%2Fesat', hash);
  const destination = await bridgeModule().completeImplicitLogin();
  assert.equal(new URL(destination, 'https://portal.invalid').pathname, '/login');
  assert.equal(new URL(destination, 'https://portal.invalid').searchParams.get('next'), '/esat');
  assert.deepEqual(events.map(event => event[0]), ['clear']);
  assert.doesNotMatch(destination, /PRIVATE|synthetic|access_token|refresh_token/);
}
for (const [next, login] of [['/amc', '/amc-login'], ['/sat', '/sat-login'], ['/ib?subject=physics-hl', '/ib-login'], ['/dashboard', '/login']]) {
  reset(`?next=${encodeURIComponent(next)}`, '');
  assert.equal(new URL(await bridgeModule().completeImplicitLogin(), 'https://portal.invalid').pathname, login);
}
for (const failure of ['error', 'throws', 'missingSession']) {
  reset();
  if (failure === 'error') setError = { message: 'PRIVATE token synthetic-access' };
  if (failure === 'throws') setThrows = true;
  if (failure === 'missingSession') missingSession = true;
  const destination = await bridgeModule().completeImplicitLogin();
  assert.match(destination, /^\/login\?/);
  assert.doesNotMatch(destination, /PRIVATE|synthetic/);
  assert.equal(events.filter(event => event[0] === 'verify').length, 0);
}
for (const failure of ['error', 'missingUser']) {
  reset();
  if (failure === 'error') verifyError = { message: 'PRIVATE' };
  if (failure === 'missingUser') missingUser = true;
  assert.match(await bridgeModule().completeImplicitLogin(), /^\/login\?/);
  assert.deepEqual(events.at(-1), ['sign-out', { scope: 'local' }]);
}
reset();
historyThrows = true;
assert.match(await bridgeModule().completeImplicitLogin(), /^\/login\?/);
assert.deepEqual(events.map(event => event[0]), ['clear']);

const config = moduleAt('next.config.ts', {
  './lib/supabase/public-config': { resolvePublicSupabaseConfig: () => ({ url: 'https://project.invalid', key: 'public-test', rejectedVariables: [] }) },
  './lib/past-paper-practice': { PAST_PAPER_PRACTICE_URL: 'https://www.thrivingscholars.com/post/free-tmua-esat-maths-past-paper-practice' },
}).default;
const authHeaders = (await config.headers()).find(entry => entry.source === '/auth/:path*');
assert.ok(authHeaders.headers.some(header => header.key === 'Referrer-Policy' && header.value === 'no-referrer'));
assert.ok(authHeaders.headers.some(header => header.key === 'Cache-Control' && header.value.includes('no-store')));
assert.ok(authHeaders.headers.some(header => header.key === 'X-Robots-Tag' && header.value.includes('noindex')));
const clientSource = readFileSync('app/auth/complete/CallbackBridge.tsx', 'utf8');
assert.match(clientSource, /useRef\(false\)/);
assert.match(clientSource, /window\.location\.replace\(destination\)/);
for (const file of ['app/auth/complete/CallbackBridge.tsx', 'app/auth/complete/page.tsx', 'lib/auth/implicit-callback.ts']) {
  assert.doesNotMatch(readFileSync(file, 'utf8'), /console\.|localStorage|sessionStorage|sendBeacon|gtag|dataLayer/);
}
console.log('Auth callback flows passed: unchanged PKCE/token_hash; fragment cleanup before SDK; verified implicit session; safe programme redirects; provider failures; no token logging/storage; no-referrer/no-store (isolated synthetic tests only).');
