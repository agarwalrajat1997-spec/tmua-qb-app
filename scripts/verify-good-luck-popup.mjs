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
assert.equal(campaign.isGoodLuckCampaignActive(campaign.GOOD_LUCK_START - 1), false);
assert.equal(campaign.isGoodLuckCampaignActive(campaign.GOOD_LUCK_START), true);
assert.equal(campaign.isGoodLuckCampaignActive(campaign.GOOD_LUCK_END - 1), true);
assert.equal(campaign.isGoodLuckCampaignActive(campaign.GOOD_LUCK_END), false);

const receipts = new Set();
let user = { id: 'student-a' }, authError = null, databaseError = null, writes = 0;
const db = {
  auth: { getUser: async () => ({ data: { user }, error: authError }) },
  from(table) {
    assert.equal(table, 'student_popup_receipts');
    return { upsert(row, options) {
      writes++;
      assert.equal(row.user_id, user.id);
      assert.equal(row.campaign_key, campaign.GOOD_LUCK_CAMPAIGN_KEY);
      assert.equal(options.onConflict, 'user_id,campaign_key');
      assert.equal(options.ignoreDuplicates, true);
      return { select: async () => {
        if (databaseError) return { data: null, error: databaseError };
        const key = `${row.user_id}:${row.campaign_key}`;
        if (receipts.has(key)) return { data: [], error: null };
        receipts.add(key);
        return { data: [{ campaign_key: row.campaign_key }], error: null };
      } };
    } };
  },
};
const route = load('app/api/student/good-luck-popup/route.ts', {
  'next/server': { NextResponse: { json: (data, options) => Response.json(data, options) } },
  '@/lib/supabase/server': { createSupabaseServerClient: async () => db },
  '@/lib/good-luck-popup': campaign,
  '@/lib/auth/service-recovery': { isMissingSession: error => error?.name === 'AuthSessionMissingError' },
});
const request = (origin = 'https://portal.test') => new Request('https://portal.test/api/student/good-luck-popup', {
  method: 'POST', headers: { origin }, body: JSON.stringify({ user_id: 'spoofed-id' }),
});
assert.equal((await route.POST(request('https://other.test'))).status, 403);
assert.equal(writes, 0);
now = campaign.GOOD_LUCK_START - 1;
assert.deepEqual(await (await route.POST(request())).json(), { show: false });
const proxied = new Request('http://localhost:3000/api/student/good-luck-popup', {
  method: 'POST', headers: { origin: 'https://portal.test', host: 'portal.test' },
});
assert.equal((await route.POST(proxied)).status, 200, 'Incoming Host must work behind Next/Vercel proxy');
assert.equal((await route.POST(request('file://portal.test'))).status, 403);
assert.equal(writes, 0);
now = campaign.GOOD_LUCK_START;
user = null;
assert.equal((await route.POST(request())).status, 401);
authError = { name: 'AuthSessionMissingError' };
assert.equal((await route.POST(request())).status, 401);
authError = { name: 'AuthRetryableFetchError' };
assert.equal((await route.POST(request())).status, 503);
authError = null; user = { id: 'student-a' };
databaseError = { code: '57014' };
assert.equal((await route.POST(request())).status, 503);
databaseError = null;
const concurrent = await Promise.all([route.POST(request()), route.POST(request())]);
const shown = await Promise.all(concurrent.map(async response => (await response.json()).show));
assert.equal(shown.filter(Boolean).length, 1);
for (let device = 0; device < 3; device++) {
  const response = await route.POST(request());
  assert.equal(response.headers.get('cache-control'), 'private, no-store');
  assert.deepEqual(await response.json(), { show: false });
}
user = { id: 'student-b' };
assert.deepEqual(await (await route.POST(request())).json(), { show: true });
now = campaign.GOOD_LUCK_END;
user = { id: 'student-c' };
assert.deepEqual(await (await route.POST(request())).json(), { show: false });
console.log('PASS: Saturday boundaries, auth/CSRF guards, fail-closed persistence, one receipt per student across requests/devices, and no-store responses.');
