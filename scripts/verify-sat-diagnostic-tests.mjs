import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

for (const testNumber of [1, 2, 3]) {
  const html = await readFile(
    new URL(`../public/sat-test-${testNumber}/index.html`, import.meta.url),
    "utf8",
  );
  const route = await readFile(
    new URL(`../app/sat-test-${testNumber}/route.ts`, import.meta.url),
    "utf8",
  );

  assert.match(html, new RegExp(`Digital SAT Math Test ${testNumber}`));
  assert.match(html, /Module 1:<\/strong> Math, 22 questions, 35 minutes/);
  assert.match(html, /Module 2:<\/strong> Math, 22 questions, 35 minutes/);
  assert.match(html, /predicted Math score out of 800/);
  assert.match(html, /www\.desmos\.com\/api/);
  assert.match(html, /emailjs\.send\(/);
  assert.match(route, new RegExp(`/sat-test-${testNumber}/index\\.html`));
}

console.log("SAT diagnostic tests 1–3 are restored and routable.");
