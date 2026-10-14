import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { chromium } from 'playwright';

// Read-only production smoke check. Fresh anonymous contexts never submit tests,
// emails or account receipts; dismissal below is stored in that browser only.
const base = process.env.REMINDER_BASE_URL || 'http://localhost:5182';
const browser = await chromium.launch({ channel: 'chrome', headless: true });
try {
  const context = await browser.newContext();
  const api = await context.request.get(`${base}/api/student/esat-final-reminder`);
  const state = await api.json();
  assert.equal(api.status(), state.active ? 401 : 200);
  assert.match(api.headers()['cache-control'], /no-store/);
  const path = '/esat-resources/esat-2026-extra-practice-pack.pdf';
  const pdf = await context.request.get(base + path);
  assert.equal(pdf.status(), 200);
  assert.match(pdf.headers()['content-type'], /application\/pdf/);
  const hash = data => createHash('sha256').update(data).digest('hex');
  assert.equal(hash(await pdf.body()), hash(readFileSync(`public${path}`)));
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(`${base}/esat`, { waitUntil: 'networkidle' });
  assert.match(page.url(), /\/login\?next=%2Fesat/i);
  const dialog = page.locator('dialog.ts-final-reminder[open]');
  if (state.active) {
    await dialog.waitFor({ timeout: 20000 });
    assert.match(await dialog.innerText(), /Your final ESAT warm-up/);
    assert.equal(await dialog.locator('.ts-final-pdf').getAttribute('href'), path);
    assert.equal(await dialog.locator('.ts-final-pdf').getAttribute('target'), '_blank');
    await dialog.locator('.ts-final-close').click();
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForTimeout(1600);
    assert.equal(await dialog.count(), 0);
  } else {
    await page.waitForTimeout(1600);
    assert.equal(await dialog.count(), 0);
  }
  assert.deepEqual(errors, []);
  await context.close();
  console.log(`PASS ${base}: actual login route, loader, public PDF hash/content type, no-store API, anonymous dismissal and no browser errors. Campaign active=${state.active}.`);
} finally {
  await browser.close();
}
