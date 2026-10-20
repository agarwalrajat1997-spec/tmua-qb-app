import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const read = file => readFileSync(resolve(root, file), 'utf8').replace(/\r\n/g, '\n');
const cssAddition = '<!-- Website embedding only; original test and report code below is unchanged. -->\n'
  + '<link rel="stylesheet" href="/mini-test-embed.css">\n';
const jsAddition = '<script defer src="/mini-test-embed.js"></script>\n';
// Normalised hashes of the user-supplied originals. Removing only the two
// additive embed hooks must recover the entire original file byte for byte.
const originalHashes = {
  tmua: '1751af36b7c73419927ad06a8aca65acc964967b5ae2d389f358aa66ca19d6e1',
  esat: '33927d51717ec32ca4e02f5938856f32c5e78bf19c842a69ab4506995cfdb6c9',
};
for (const exam of ['tmua', 'esat']) {
  const html = read(`public/${exam}-mini-test/index.html`);
  assert.equal(html.split(cssAddition).length, 2);
  assert.equal(html.split(jsAddition).length, 2);
  const restored = html.replace(cssAddition, '').replace(jsAddition, '');
  assert.equal(createHash('sha256').update(restored).digest('hex'), originalHashes[exam],
    `${exam}: original questions, solutions, timing, scoring, styling and email code remain unchanged`);
  const script = restored.match(/<script>\n([\s\S]*?)<\/script>/)?.[1];
  assert.ok(script);
  new vm.Script(script);
  const bank = JSON.parse(script.match(/const BANK=(\[[\s\S]*?\]);\nconst MODULES/)?.[1]);
  assert.equal(bank.length, exam === 'tmua' ? 10 : 20);
  assert.equal(new Set(bank.map(question => question.id)).size, bank.length);
  for (const question of bank) {
    assert.ok(question.html.trim() && question.solution.trim());
    assert.ok(question.options.some(option => option.letter === question.answer));
  }
  for (const field of ['paper1:', 'paper2:', 'paper3:', 'report_text:', 'to_email:',
    'attempt_id:', 'solution_link:', 'tmua_paper1_score:', 'math1_score:']) {
    assert.ok(script.includes(field), `${exam}: email report retains ${field}`);
  }
  assert.match(script, /if\(DEMO\|\|SETTINGS\.disableEmail\)\{emailStatus\(\);return\}/);
}

const bridge = read('public/mini-test-embed.js');
const css = read('public/mini-test-embed.css');
new vm.Script(bridge);
assert.match(css, /html\.ts-mini-embedded:not\(\.ts-mini-fullscreen\)/);
assert.match(css, /position:\s*relative/);
assert.match(css, /overflow:\s*visible\s*!important/);
assert.doesNotMatch(css, /display:\s*none/);
assert.doesNotMatch(bridge, /\b(?:fetch|XMLHttpRequest|emailjs|sessionStorage|localStorage)\b/);
assert.doesNotMatch(bridge, /postMessage\([\s\S]{0,160},\s*['"]\*['"]/);

function fixture({
  child = 'https://apps.thrivingscholars.com',
  parent = 'https://www.thrivingscholars.com',
  declaredParent = parent,
  embed = '1',
  referrer = `${parent}/tmua`,
  standalone = false,
} = {}) {
  const classes = new Set();
  const events = new Map();
  const documentEvents = new Map();
  const frames = [];
  const messages = [];
  const observers = [];
  const phases = ['landing', 'exam', 'transition', 'results'];
  const elements = Object.fromEntries(['brandbar', ...phases].map(id => [id, {
    hidden: id !== 'landing' && id !== 'brandbar',
    bottom: id === 'brandbar' ? 72 : 698,
    margin: 0,
    getBoundingClientRect() { return { bottom: this.bottom }; },
  }]));
  const classList = {
    add(name) { classes.add(name); },
    toggle(name, enabled) { if (enabled) classes.add(name); else classes.delete(name); },
  };
  const parentWindow = {
    postMessage(data, target) { messages.push({ data: JSON.parse(JSON.stringify(data)), target }); },
  };
  const url = new URL(`${child}/tmua-mini-test/index.html`);
  url.searchParams.set('embed', embed);
  if (declaredParent !== null) url.searchParams.set('parentOrigin', declaredParent);
  const window = {
    location: url,
    parent: parentWindow,
    scrollY: 0,
    innerHeight: 850,
    requestAnimationFrame(callback) { frames.push(callback); },
    getComputedStyle(element) { return { marginBottom: `${element.margin}px` }; },
    addEventListener(name, callback) { events.set(name, callback); },
  };
  if (standalone) window.parent = window;
  const document = {
    referrer,
    readyState: 'complete',
    body: {},
    documentElement: { classList },
    fonts: { ready: Promise.resolve() },
    getElementById(id) { return elements[id] ?? null; },
    addEventListener(name, callback) { documentEvents.set(name, callback); },
  };
  class Observer {
    constructor(callback) { this.callback = callback; this.elements = []; observers.push(this); }
    observe(element) { this.elements.push(element); }
  }
  vm.runInNewContext(bridge, {
    window, document, URL, URLSearchParams, Set,
    ResizeObserver: Observer, MutationObserver: Observer,
  });
  function flush() {
    let cycles = 0;
    while (frames.length) {
      assert.ok(cycles++ < 20, 'sizing must not loop');
      frames.shift()();
    }
  }
  flush();
  return {
    classes, messages, elements, observers, events, documentEvents, window, flush,
    phase(value) {
      for (const phase of phases) elements[phase].hidden = phase !== value;
      for (const observer of observers) observer.callback([]);
      flush();
    },
    fullscreen(value, overrides = {}) {
      events.get('message')?.({
        source: parentWindow, origin: parent,
        data: { type: 'ts-mini-test-fullscreen', fullscreen: value },
        ...overrides,
      });
      flush();
    },
  };
}

for (const origin of [
  'https://www.thrivingscholars.com',
  'https://thrivingscholars.com',
  'https://thriving-scholars-migration.raj1291241.chatgpt.site',
]) {
  const page = fixture({ parent: origin });
  assert.ok(page.classes.has('ts-mini-embedded'));
  assert.deepEqual(page.messages[0], {
    data: { type: 'ts-mini-test-size', height: 700, phase: 'landing' }, target: origin,
  });
}
for (const config of [
  { parent: 'https://evil.example' },
  { parent: 'https://www.thrivingscholars.com.evil.example' },
  { parent: 'http://www.thrivingscholars.com' },
  { declaredParent: 'https://www.thrivingscholars.com/tmua' },
  { declaredParent: 'https://user@www.thrivingscholars.com' },
  { declaredParent: 'https://www.thrivingscholars.com#fragment' },
  { declaredParent: null },
  { declaredParent: 'null' },
  { referrer: 'https://evil.example/' },
  { parent: 'http://localhost:5173' },
  { parent: 'http://127.0.0.1:5173' },
  { embed: '0' },
  { standalone: true },
]) {
  const page = fixture(config);
  assert.ok(!page.classes.has('ts-mini-embedded'), JSON.stringify(config));
  assert.equal(page.messages.length, 0);
}
for (const host of ['localhost', '127.0.0.1', '[::1]']) {
  assert.ok(fixture({
    child: `http://${host}:3000`, parent: `http://${host}:5173`,
  }).classes.has('ts-mini-embedded'), `${host}: local-only development accepted`);
}
assert.ok(fixture({ referrer: '' }).classes.has('ts-mini-embedded'),
  'no-referrer works with exact allowlisted targetOrigin');

const page = fixture();
page.elements.exam.bottom = 998;
page.phase('exam');
assert.equal(page.messages.at(-1).data.height, 1000);
assert.equal(page.messages.at(-1).data.phase, 'exam');
page.elements.results.bottom = 9998;
page.phase('results');
assert.equal(page.messages.at(-1).data.height, 10000);
page.phase('landing');
assert.equal(page.messages.at(-1).data.height, 700, 'results can shrink back to the entry screen');
const stableCount = page.messages.length;
page.window.innerHeight = 10000;
page.events.get('resize')();
page.flush();
assert.equal(page.messages.length, stableCount, 'parent iframe height does not cause a sizing feedback loop');
page.elements.landing.bottom += 1;
page.events.get('resize')();
page.flush();
assert.equal(page.messages.length, stableCount, 'one-pixel jitter is ignored');
page.elements.landing.bottom = 100000;
page.events.get('resize')();
page.flush();
assert.equal(page.messages.at(-1).data.height, 30000);
page.elements.landing.bottom = -1000;
page.events.get('resize')();
page.flush();
assert.equal(page.messages.at(-1).data.height, 320);

page.fullscreen(true, { origin: 'https://evil.example' });
assert.ok(!page.classes.has('ts-mini-fullscreen'));
page.fullscreen(true, { source: {} });
assert.ok(!page.classes.has('ts-mini-fullscreen'));
page.fullscreen('true');
assert.ok(!page.classes.has('ts-mini-fullscreen'));
page.window.innerHeight = 850;
page.fullscreen(true);
assert.ok(page.classes.has('ts-mini-fullscreen'));
assert.equal(page.messages.at(-1).data.height, 850);
page.fullscreen(false);
assert.ok(!page.classes.has('ts-mini-fullscreen'));
assert.equal(page.messages.at(-1).data.height, 320);
for (const message of page.messages) {
  assert.deepEqual(Object.keys(message.data).sort(), ['height', 'phase', 'type']);
  assert.equal(message.target, 'https://www.thrivingscholars.com');
}
await Promise.resolve();
page.flush();
assert.ok(page.observers.some(observer => observer.elements.length === 5));
assert.ok(page.events.has('load') && page.events.has('resize') && page.events.has('pageshow'));
assert.ok(page.documentEvents.has('toggle'));
console.log('PASS: TMUA/ESAT mini tests preserve the supplied content and email code; secure, fluid embed sizing and fullscreen messages pass.');
