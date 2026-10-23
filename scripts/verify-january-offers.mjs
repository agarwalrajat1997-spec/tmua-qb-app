import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';
import React from 'react';
import * as jsxRuntime from 'react/jsx-runtime';
import { renderToStaticMarkup } from 'react-dom/server';

const css = new Proxy({}, { get: (_, key) => key === '__esModule' ? false : String(key) });
function load(file, imports = {}, extras = {}) {
  const code = ts.transpileModule(readFileSync(file, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022,
      jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true },
  }).outputText;
  const context = vm.createContext({ exports: {}, require(name) {
    assert.ok(name in imports, `Unexpected dependency: ${name}`);
    return imports[name];
  }, ...extras });
  vm.runInContext(code, context);
  return context.exports;
}

const offer = load('lib/january-offer.ts');
assert.equal(offer.JANUARY_OFFER_PRICE, 119);
assert.equal(offer.JANUARY_USUAL_PRICE, 149);
assert.equal(offer.JANUARY_USUAL_PRICE - offer.JANUARY_OFFER_PRICE, 30);
assert.equal(offer.JANUARY_OFFER_LIMIT, 50);
assert.equal(offer.JANUARY_OFFER_SITTING, 'January 2027');
assert.notEqual(offer.JANUARY_TMUA_CHECKOUT, offer.JANUARY_ESAT_CHECKOUT);
for (const programme of ['tmua', 'esat']) {
  const url = new URL(offer.januaryCheckout(programme));
  assert.equal(url.protocol, 'https:');
  assert.equal(url.hostname, 'buy.stripe.com');
}

const Banner = load('app/components/JanuaryAccessOffer.tsx', {
  'react/jsx-runtime': jsxRuntime,
  '@/lib/january-offer': offer,
  './JanuaryAccessOffer.module.css': css,
}).default;

for (const programme of ['tmua', 'esat']) {
  const html = renderToStaticMarkup(React.createElement(Banner, { programme, existingStudent: true }));
  assert.ok(html.includes(`Full ${programme.toUpperCase()} access`));
  assert.match(html, /£119/);
  assert.match(html, /<s>£149<\/s>/);
  assert.match(html, /January 2027/);
  assert.match(html, /First 50 purchases across TMUA and ESAT combined/);
  assert.match(html, /Question Bank \+ Practice Test Series/);
  assert.match(html, /Your existing access is unchanged/);
  assert.ok(html.includes(offer.januaryCheckout(programme).replaceAll('&', '&amp;')));
  assert.doesNotMatch(html, /classes|mandatory|upgrade now|alertdialog/i);
}

function renderLogin(next, selected = { tests: true, bank: true }) {
  let stateIndex = 0;
  const opened = [];
  const states = ['', false, null, null, selected.tests, selected.bank];
  const fakeReact = { ...React, useEffect() {}, useMemo: fn => fn(),
    useState(initial) { const value = stateIndex < states.length ? states[stateIndex] : initial;
      stateIndex++; return [value, () => {}]; } };
  const Login = load('app/login/LoginClient.tsx', {
    react: { __esModule: true, default: fakeReact, ...fakeReact },
    'react/jsx-runtime': jsxRuntime,
    'next/navigation': { useRouter: () => ({ replace() {} }), useSearchParams: () => ({ get: key => key === 'next' ? next : null }) },
    '@/utils/supabase/browser': { supabaseBrowser: () => ({ auth: {} }) },
    '@/lib/auth/login-destination': { safeLoginDestination: value => value || '/dashboard' },
    '@/lib/auth/login-error': { loginErrorMessage: () => 'Error' },
    '@/lib/january-offer': offer,
    '../components/JanuaryAccessOffer': { __esModule: true, default: Banner },
    './login.module.css': css,
  }, { window: { open: (...args) => opened.push(args) } }).default;
  const tree = Login({ uiMark: 'offer-test' });
  function visit(node, callback) {
    if (!node || typeof node !== 'object') return;
    if (Array.isArray(node)) { node.forEach(child => visit(child, callback)); return; }
    callback(node);
    visit(node.props?.children, callback);
  }
  let checkout;
  visit(tree, node => {
    if (node.type === 'button' && node.props.className?.includes('enrollBtn')) checkout = node;
  });
  assert.ok(checkout, 'Login retains its checkout button');
  if (!checkout.props.disabled) checkout.props.onClick();
  return { html: renderToStaticMarkup(tree), opened, checkout };
}

for (const next of ['/esat', '/esat-question-bank', '/esat-practice-tests/tests/esat-mock-01/index.html']) {
  const { html, opened } = renderLogin(next);
  assert.match(html, /Complete ESAT Access/);
  assert.match(html, /Get Complete Access for £119/);
  assert.match(html, /<s>£149<\/s>/);
  assert.match(html, /First 50 purchases across TMUA and ESAT combined/);
  assert.equal(opened[0][0], offer.JANUARY_ESAT_CHECKOUT, 'Preserve entire ESAT URL, including any promotion query');
}
const tmua = renderLogin('/dashboard?view=tmua');
assert.match(tmua.html, /£119/);
assert.match(tmua.html, /<s>£149<\/s> standard bundle/);
assert.match(tmua.html, /Save £30 on full access/);
assert.doesNotMatch(tmua.html, /Save £59/);
assert.equal(tmua.opened[0][0], offer.JANUARY_TMUA_CHECKOUT, 'Preserve entire TMUA URL, including any promotion query');
for (const [selected, link] of [
  [{ tests: true, bank: false }, 'https://buy.stripe.com/cNi7sN4I84d06cjbA60oM00'],
  [{ tests: false, bank: true }, 'https://buy.stripe.com/7sYfZj7UkcJwcAH7jQ0oM01'],
]) {
  const result = renderLogin('/dashboard', selected);
  assert.match(result.html, /class="price">£89/);
  assert.equal(result.opened[0][0], link, 'Standalone checkout remains unchanged');
}
const empty = renderLogin('/dashboard', { tests: false, bank: false });
assert.equal(empty.checkout.props.disabled, true);
assert.equal(empty.opened.length, 0);

for (const [file, programme] of [
  ['app/dashboard/DashboardClient.tsx', 'tmua'],
  ['app/esat/ESATDashboardClient.tsx', 'esat'],
]) {
  const source = readFileSync(file, 'utf8');
  assert.equal((source.match(/<JanuaryAccessOffer /g) || []).length, 1);
  assert.ok(source.includes(`<JanuaryAccessOffer programme="${programme}" existingStudent />`));
}
assert.doesNotMatch(readFileSync('app/layout.tsx', 'utf8'), /JanuaryAccessOffer/,
  'Offer is not globally injected into active tests, SAT or AMC');
console.log('PASS: January offers show £119 / £149, combined 50-purchase terms, isolated exam checkout routes, unchanged £89 standalone products and non-disruptive dashboard banners.');
