import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';

let now = Date.parse('2026-10-14T12:00:00+05:30');
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
const campaign = load('lib/esat-final-reminder.ts');
const recovery = load('lib/auth/service-recovery.ts');
const start = Date.parse(campaign.ESAT_FINAL_REMINDER_START);
const end = Date.parse(campaign.ESAT_FINAL_REMINDER_END);
assert.equal(campaign.ESAT_FINAL_REMINDER_CAMPAIGN_KEY, 'esat-final-warmup-2026-10-14');
assert.equal(start, Date.parse('2026-10-14T00:00:00+05:30'));
assert.equal(end, Date.parse('2026-10-17T00:00:00+05:30'));
for (const [time, active] of [[start - 1, false], [start, true], [end - 1, true], [end, false], [end + 1, false], [NaN, false]]) {
  assert.equal(campaign.isEsatFinalReminderActive(time), active);
}

const oldReceipt = 'student-a:pre-exam-good-luck-2026-10-10';
const tmuaReceipt = 'student-a:tmua-final-warmup-2026-10-13';
const receipts = new Set([oldReceipt, tmuaReceipt]);
let user = { id: 'student-a' }, authError = null, databaseError = null;
let writes = 0, reads = 0, clients = 0, authCalls = 0;
let afterAuth = null, afterRead = null, throwClient = false;
const db = {
  auth: { getUser: async () => {
    authCalls++;
    afterAuth?.();
    return { data: { user }, error: authError };
  } },
  from(table) {
    assert.equal(table, 'student_popup_receipts');
    return {
      select(column) {
        assert.equal(column, 'campaign_key');
        const filters = {};
        const query = {
          eq(key, value) { filters[key] = value; return query; },
          async maybeSingle() {
            reads++;
            assert.equal(filters.user_id, user.id);
            assert.equal(filters.campaign_key, campaign.ESAT_FINAL_REMINDER_CAMPAIGN_KEY);
            afterRead?.();
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
        assert.equal(row.campaign_key, campaign.ESAT_FINAL_REMINDER_CAMPAIGN_KEY);
        assert.equal(options.onConflict, 'user_id,campaign_key');
        assert.equal(options.ignoreDuplicates, true);
        if (databaseError) return { error: databaseError };
        receipts.add(`${row.user_id}:${row.campaign_key}`);
        return { error: null };
      },
    };
  },
};
const route = load('app/api/student/esat-final-reminder/route.ts', {
  'next/server': { NextResponse: { json: (data, options) => Response.json(data, options) } },
  '@/lib/supabase/server': { createSupabaseServerClient: async () => {
    clients++;
    if (throwClient) throw new Error('Service unavailable');
    return db;
  } },
  '@/lib/esat-final-reminder': campaign,
  '@/lib/auth/service-recovery': recovery,
});
const request = (origin = 'https://portal.test', body = { action: 'dismiss', user_id: 'spoofed-id' }) => new Request('https://portal.test/api/student/esat-final-reminder', {
  method: 'POST', headers: origin === null ? {} : { origin }, body: JSON.stringify(body),
});
async function body(response, status = 200) {
  assert.equal(response.status, status);
  assert.equal(response.headers.get('cache-control'), 'private, no-store');
  return response.json();
}
const eligible = { show: true, dismissed: false, active: true, authenticated: true };
const dismissed = { show: false, dismissed: true, active: true, authenticated: true };

for (const time of [start - 1, end, end + 24 * 60 * 60 * 1000]) {
  now = time;
  const callsBefore = [clients, authCalls, reads, writes];
  assert.deepEqual(await body(await route.GET()), { show: false, dismissed: false, active: false, authenticated: false });
  assert.deepEqual(await body(await route.POST(request())), { show: false, dismissed: false, active: false, authenticated: false });
  assert.deepEqual([clients, authCalls, reads, writes], callsBefore, 'Inactive campaign never contacts auth or storage');
}
now = start;
for (const origin of ['https://other.test', 'file://portal.test', 'null', '', null, 'https://portal.test/path', 'https://portal.test:444', 'https://portal.test.evil.test']) {
  assert.equal((await route.POST(request(origin))).status, 403);
}
assert.equal((await route.POST(request('https://portal.test', { action: 'show' }))).status, 400);
assert.equal((await route.POST(request('https://portal.test', null))).status, 400);
assert.equal((await route.POST(new Request('https://portal.test/api/student/esat-final-reminder', {
  method: 'POST', headers: { origin: 'https://portal.test' }, body: 'not-json',
}))).status, 400);
assert.equal(writes, 0);

user = null;
for (const call of [() => route.GET(), () => route.POST(request())]) {
  for (const missing of [null, { name: 'AuthSessionMissingError' }, { code: 'session_not_found' }]) {
    authError = missing;
    assert.deepEqual(await body(await call(), 401), { show: false, dismissed: false, active: true, authenticated: false });
  }
  authError = { name: 'AuthRetryableFetchError' };
  assert.deepEqual(await body(await call(), 503), { show: false, dismissed: false, active: true, authenticated: false });
  authError = null;
  throwClient = true;
  assert.equal((await call()).status, 503);
  throwClient = false;
}
assert.equal(reads, 0);
assert.equal(writes, 0);
user = { id: 'student-a' };
for (const date of ['2026-10-14', '2026-10-15', '2026-10-16']) {
  now = Date.parse(`${date}T12:00:00+05:30`);
  for (let refresh = 0; refresh < 3; refresh++) assert.deepEqual(await body(await route.GET()), eligible);
}
assert.equal(writes, 0, 'Showing, refreshing and subsequent days do not save a receipt');
assert.equal(receipts.size, 2, 'Old good-luck and TMUA receipts do not suppress the ESAT message');

databaseError = { code: '57014' };
assert.deepEqual(await body(await route.GET(), 503), { ...eligible, show: false });
assert.deepEqual(await body(await route.POST(request()), 503), { ...eligible, show: false });
databaseError = null;
assert.equal(receipts.size, 2, 'Failed save never claims dismissal');

// Expiry while awaiting auth/read must not reopen or newly dismiss the reminder.
afterAuth = () => { now = end; };
const writesBeforeExpiry = writes;
assert.deepEqual(await body(await route.POST(request())), { show: false, dismissed: false, active: false, authenticated: true });
assert.equal(writes, writesBeforeExpiry);
afterAuth = null;
now = end - 1;
afterRead = () => { now = end; };
assert.deepEqual(await body(await route.GET()), { show: false, dismissed: false, active: false, authenticated: true });
afterRead = null;
now = end - 1;

const proxied = new Request('http://localhost:3000/api/student/esat-final-reminder', {
  method: 'POST', headers: { origin: 'https://portal.test', host: 'PORTAL.TEST' },
  body: JSON.stringify({ action: 'dismiss', user_id: 'spoofed-id' }),
});
assert.deepEqual(await body(await route.POST(proxied)), dismissed);
const concurrent = await Promise.all([route.POST(request()), route.POST(request())]);
for (const response of concurrent) assert.deepEqual(await body(response), dismissed);
assert.equal(receipts.size, 3, 'Concurrent dismissal adds one ESAT receipt and preserves both earlier campaigns');
assert.ok(receipts.has(oldReceipt));
assert.ok(receipts.has(tmuaReceipt));
assert.ok(receipts.has(`student-a:${campaign.ESAT_FINAL_REMINDER_CAMPAIGN_KEY}`));
for (let device = 0; device < 3; device++) assert.deepEqual(await body(await route.GET()), dismissed);
user = { id: 'student-b' };
assert.deepEqual(await body(await route.GET()), eligible, 'Another student retains their own eligibility');

// The ESAT campaign is independent of the existing TMUA window and receipts.
const tmuaCampaign = load('lib/tmua-final-reminder.ts');
assert.notEqual(campaign.ESAT_FINAL_REMINDER_CAMPAIGN_KEY, tmuaCampaign.TMUA_FINAL_REMINDER_CAMPAIGN_KEY);
assert.equal(campaign.ESAT_FINAL_REMINDER_END, tmuaCampaign.TMUA_FINAL_REMINDER_END);
assert.equal(campaign.isEsatFinalReminderActive(Date.parse('2026-10-13T12:00:00+05:30')), false);
assert.equal(tmuaCampaign.isTmuaFinalReminderActive(Date.parse('2026-10-13T12:00:00+05:30')), true);
assert.equal(route.runtime, 'nodejs');
assert.equal(route.dynamic, 'force-dynamic');

// The only schema change is an atomic expansion of the existing campaign
// allowlist. Find by suffix so a production-assigned timestamp can be kept.
const migrationFiles = readdirSync('supabase/migrations').filter(file => file.endsWith('_allow_esat_final_reminder_receipts.sql'));
assert.equal(migrationFiles.length, 1);
const migration = readFileSync(`supabase/migrations/${migrationFiles[0]}`, 'utf8').replace(/--[^\n]*/g, '');
assert.match(migration, /alter table public\.student_popup_receipts\s+drop constraint student_popup_receipts_campaign_key_check,\s+add constraint student_popup_receipts_campaign_key_check\s+check \(campaign_key in/);
assert.deepEqual([...migration.matchAll(/'([^']+)'/g)].map(match => match[1]), [
  'pre-exam-good-luck-2026-10-10',
  tmuaCampaign.TMUA_FINAL_REMINDER_CAMPAIGN_KEY,
  campaign.ESAT_FINAL_REMINDER_CAMPAIGN_KEY,
]);
assert.doesNotMatch(migration, /\b(delete|truncate|update|insert|grant|revoke|policy|disable|cascade)\b/i);
assert.equal((migration.match(/;/g) || []).length, 1, 'Constraint replacement is one atomic statement');
console.log('PASS: ESAT reminder date boundaries, server expiry, read-only eligibility, explicit account-scoped dismissal, TMUA and old receipt isolation, auth, CSRF, retryable failures, idempotency and narrow migration.');
