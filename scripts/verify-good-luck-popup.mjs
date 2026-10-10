import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';

let now = Date.parse('2026-10-10T12:00:00+05:30');
class Clock extends Date { static now() { return now; } }
function load(file, imports = {}) {
  const source = ts.transpileModule(readFileSync(file, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText;
  const context = vm.createContext({
    exports: {}, require: name => { assert.ok(name in imports, name); return imports[name]; },
    Date: Clock, URL, Request, Response, console: { error() {} },
  });
  vm.runInContext(source, context);
  return context.exports;
}
const campaign = load('lib/good-luck-popup.ts');

const receipts = new Set();
let user = { id: 'student-a' }, authError = null, databaseError = null, writes = 0;
const db = {
  auth: { getUser: async () => ({ data: { user }, error: authError }) },
  from(table) {
    assert.equal(table, 'student_popup_receipts');
    return {
      select(column) {
        assert.equal(column, 'campaign_key');
        const filters = {};
        const query = {
          eq(key, value) { filters[key] = value; return query; },
          async maybeSingle() {
            assert.equal(filters.user_id, user.id);
            assert.equal(filters.campaign_key, campaign.GOOD_LUCK_CAMPAIGN_KEY);
            return {
              data: receipts.has(`${filters.user_id}:${filters.campaign_key}`) ? { campaign_key: filters.campaign_key } : null,
              error: databaseError,
            };
          },
        };
        return query;
      },
      async upsert(row, options) {
        writes++;
        assert.equal(row.user_id, user.id);
        assert.equal(row.campaign_key, campaign.GOOD_LUCK_CAMPAIGN_KEY);
        assert.equal(options.onConflict, 'user_id,campaign_key');
        assert.equal(options.ignoreDuplicates, true);
        if (databaseError) return { error: databaseError };
        receipts.add(`${row.user_id}:${row.campaign_key}`);
        return { error: null };
      },
    };
  },
};
const route = load('app/api/student/good-luck-popup/route.ts', {
  'next/server': { NextResponse: { json: (data, options) => Response.json(data, options) } },
  '@/lib/supabase/server': { createSupabaseServerClient: async () => db },
  '@/lib/good-luck-popup': campaign,
  '@/lib/auth/service-recovery': { isMissingSession: error => error?.name === 'AuthSessionMissingError' },
});
const request = (origin = 'https://portal.test', body = { action: 'dismiss', user_id: 'spoofed-id' }) => new Request('https://portal.test/api/student/good-luck-popup', {
  method: 'POST', headers: { origin }, body: body === undefined ? undefined : JSON.stringify(body),
});
assert.equal((await route.POST(request('https://other.test'))).status, 403);
assert.equal((await route.POST(request('file://portal.test'))).status, 403);
assert.equal((await route.POST(request('null'))).status, 403);
assert.equal((await route.POST(request('', {}))).status, 403);
const legacy = new Request('https://portal.test/api/student/good-luck-popup', {
  method: 'POST', headers: { origin: 'https://portal.test' },
});
assert.equal((await route.POST(legacy)).status, 400, 'Legacy display requests must never dismiss');
assert.equal((await route.POST(request('https://portal.test', { action: 'show' }))).status, 400);
assert.equal(writes, 0);
user = null;
for (const call of [() => route.GET(), () => route.POST(request())]) {
  assert.equal((await call()).status, 401);
  authError = { name: 'AuthSessionMissingError' };
  assert.equal((await call()).status, 401);
  authError = { name: 'AuthRetryableFetchError' };
  assert.equal((await call()).status, 503);
  authError = null;
}
user = { id: 'student-a' };
databaseError = { code: '57014' };
assert.equal((await route.GET()).status, 503);
const failed = await route.POST(request());
assert.equal(failed.status, 503);
assert.equal((await failed.json()).dismissed, false);
databaseError = null;
assert.equal(receipts.size, 0);
const writesBeforeRead = writes;
for (const date of ['2026-10-10', '2026-10-11', '2026-10-18', '2027-05-01']) {
  now = Date.parse(`${date}T12:00:00+05:30`);
  for (let refresh = 0; refresh < 3; refresh++) {
    const status = await route.GET();
    assert.equal(status.headers.get('cache-control'), 'private, no-store');
    assert.deepEqual(await status.json(), { show: true, dismissed: false });
  }
}
assert.equal(writes, writesBeforeRead, 'Viewing, refreshing and future days never persist a dismissal');
const proxied = new Request('http://localhost:3000/api/student/good-luck-popup', {
  method: 'POST', headers: { origin: 'https://portal.test', host: 'portal.test' },
  body: JSON.stringify({ action: 'dismiss' }),
});
assert.deepEqual(await (await route.POST(proxied)).json(), { show: false, dismissed: true });
const concurrent = await Promise.all([route.POST(request()), route.POST(request())]);
for (const response of concurrent) {
  assert.deepEqual(await response.json(), { show: false, dismissed: true });
}
assert.equal(receipts.size, 1, 'Dismissal is idempotent and uses the signed-in identity');
for (let device = 0; device < 3; device++) {
  assert.deepEqual(await (await route.GET()).json(), { show: false, dismissed: true });
}
user = { id: 'student-b' };
assert.deepEqual(await (await route.GET()).json(), { show: true, dismissed: false });
console.log('PASS: no date limit, read-only eligibility, persistent explicit dismissal, legacy client guard, account isolation, auth/CSRF, retryable errors and no-store responses.');
