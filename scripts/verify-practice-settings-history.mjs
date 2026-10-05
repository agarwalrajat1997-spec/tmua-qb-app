import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const ts = require('typescript'), React = require('react');
const { renderToStaticMarkup } = require('react-dom/server');
function load(file, imports = {}) {
  const output = ts.transpileModule(fs.readFileSync(file, 'utf8'), { compilerOptions: {
    jsx: ts.JsxEmit.ReactJSX, module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020,
  }}).outputText;
  const module = { exports: {} };
  vm.runInNewContext(output, { module, exports: module.exports, require: name => imports[name] || require(name) });
  return module.exports;
}
const settingsModule = load('lib/practice-settings.ts');
const { default: Component } = load('app/components/PracticeAttemptSettings.tsx', { '@/lib/practice-settings': settingsModule });
const settings = { version: 1, order: 'randomised', time_multiplier: 1.25, question_order: Array.from({length:40},(_,i)=>i), section_sizes: [20,20], base_seconds_per_section:4500 };
const estimate = { time_multiplier:1.25, estimated_score:5.5, note:'Provisional, not an official result. Actual raw marks unchanged.', units:[{label:'Full test',actual_raw:30,total_questions:40,adjusted_raw:27}] };
const html = renderToStaticMarkup(React.createElement(Component, {settings,estimate,detailed:true}));
assert.match(html, /Randomised questions/);
assert.match(html, /25% extra time/);
assert.match(html, /93 min 45 sec/);
assert.match(html, /Estimated standard-time equivalent: 5.5\/9/);
assert.match(html, /30\/40 actual → 27\/40 estimated/);
assert.match(html, /actual raw mark unchanged/);
assert.equal(renderToStaticMarkup(React.createElement(Component, {})), '', 'historical rows without settings unchanged');
const standard = renderToStaticMarkup(React.createElement(Component, {settings:{...settings,time_multiplier:1},estimate:{...estimate,time_multiplier:1}}));
assert.doesNotMatch(standard, /standard-time equivalent/);
assert.match(standard, /Standard time/);
for (const file of ['app/dashboard/DashboardClient.tsx','app/esat/ESATDashboardClient.tsx']) {
  const source = fs.readFileSync(file,'utf8');
  assert.match(source, /settings=\{latest\?\.practice_settings\}/, `${file} latest attempt settings visible`);
  assert.match(source, /settings=\{a\.practice_settings\} estimate=\{a\.standard_time_estimate\} detailed/, `${file} history has full explanation`);
}
console.log('PASS practice history: settings, separate adjusted estimate, actual marks and legacy compatibility.');
