import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const root = process.cwd();
const source = fs.readFileSync(path.join(root, 'public/shared/esat-october-2026-portal.js'), 'utf8');
const pathways = ['engineering', 'physics-chemistry', 'physics-biology', 'maths-2-chemistry', 'maths-2-biology', 'chemistry-biology'];
const runtimeSource = fs.readFileSync(path.join(root, 'public/shared/esat-october-2026-runtime.js'), 'utf8');
const scoringContext = {module: {exports: {}}};
vm.runInNewContext(runtimeSource, scoringContext);
const {scoreFor} = scoringContext.module.exports;
const expectedBoundaries = {
  maths1: [13,14,17,20,23,26], maths2: [11,12,15,18,22,25],
  physics: [15,16,19,22,24,27], chemistry: [16,17,20,23,25,27], biology: [18,19,22,24,26,27]
};
for (const [moduleId, rawMarks] of Object.entries(expectedBoundaries)) {
  rawMarks.forEach((raw, i) => assert.equal(scoreFor(moduleId, raw), [4.5,5,6,7,8,9][i], moduleId + ': exact supplied boundary ' + raw));
  assert.equal(scoreFor(moduleId, 27), 9);
}
const reportFunctions = runtimeSource.slice(runtimeSource.indexOf('  function reportHTML('), runtimeSource.indexOf('  function download('));
const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function reportFormats(report, data) {
  const context = {CFG:data.config, DATA:data, esc:escapeHtml, secondsText:value=>String(value), report:()=>report};
  vm.runInNewContext(reportFunctions, context);
  return {html:context.reportHTML(report), csv:context.csv(report)};
}
let largestEmailPacket=0;
const predictionNote='Completed attempts saved to the portal contribute to your dashboard prediction using the three module estimates.';
const runtimeNoteExpression=runtimeSource.match(/scoreNote:(.*?),modules:DATA\.modules/)[1];
const runtimeNote=incomplete=>vm.runInNewContext('('+runtimeNoteExpression+')',{state:{incomplete}});

const fixtures = pathways.map(slug => {
  const html = fs.readFileSync(path.join(root, 'public/esat-practice-tests/tests', 'esat-october-2026-' + slug, 'index.html'), 'utf8');
  const match = html.match(/<script id="test-data" type="application\/json">([\s\S]*?)<\/script>/);
  assert.ok(match, slug + ': embedded test data exists');
  return {slug, data: JSON.parse(match[1])};
});

function reportFor({slug, data}) {
  const modules = data.modules.map(m => {
    const questions = m.questions.map((q, i) => {
      const selected = i % 3 === 2 ? null : i % 3 === 0 ? q.correctAnswer : q.options.find(o => o.label !== q.correctAnswer).label;
      const correctOption = q.options.find(o => o.label === q.correctAnswer);
      const selectedOption = q.options.find(o => o.label === selected);
      return {
        number: q.number,
        selectedAnswer: selected,
        selectedAnswerText: selectedOption?.text || 'Unanswered',
        correctAnswer: q.correctAnswer,
        correctAnswerText: correctOption.text,
        correct: selected === q.correctAnswer,
        timeSpentSeconds: 59 + i,
        lastAnswerChangeAt: selected ? '2026-09-20T08:01:00.000Z' : null,
        flagged: i % 5 === 0
      };
    });
    return {
      id: m.id, name: m.name, questions, questionCount: 27,
      rawScore: questions.filter(q => q.correct).length,
      provisionalScore: 4.5,
      startedAt: '2026-09-20T08:00:00.000Z', submittedAt: '2026-09-20T08:40:00.000Z',
      elapsedSeconds: 2400, reviewSeconds: 15, awaySeconds: 30
    };
  });
  return {
    testId: 'esat-october-2026-' + slug,
    testTitle: 'ESAT Practice Test 2026', pathway: data.pathway,
    attemptId: 'mock-attempt-' + slug,
    student: {name: 'Mock student', email: 'student@example.test', session: 'October 2026'},
    startedAt: '2026-09-20T08:00:00.000Z', submittedAt: '2026-09-20T10:00:00.000Z',
    totalScore: modules.reduce((sum, m) => sum + m.rawScore, 0), totalQuestions: 81, modules,
    scoreNote: 'These practice estimates have not been calibrated against live ESAT results. Each module is converted separately.'
  };
}

function harness(queue = [], storage = new Map()) {
  const calls = [];
  const listeners = new Map();
  const element = tag => ({tag, dataset: {}, children: [], attributes: {}, textContent: '',
    setAttribute(name, value) { this.attributes[name] = value; },
    replaceChildren(...children) { this.children = children; }
  });
  const status = element('div');
  const context = {
    URL, AbortController, Date, Map, Promise, console, setTimeout, clearTimeout,
    localStorage: {getItem: key => storage.get(key) ?? null, setItem: (key, value) => storage.set(key, value)},
    document: {
      getElementById: id => id === 'portal-attempt-status' ? status : null,
      createElement: element,
      addEventListener: (name, listener) => listeners.set(name, listener)
    },
    fetch: async (url, options) => {
      calls.push({url, options, payload: options.body ? JSON.parse(options.body) : undefined});
      assert.ok(queue.length, 'unexpected API call: ' + url);
      const next = queue.shift();
      if (next instanceof Error) throw next;
      return typeof next === 'function' ? next(url, options) : next;
    }
  };
  context.window = {location: {origin: 'https://apps.thrivingscholars.com'}};
  vm.runInNewContext(source, context, {filename: 'esat-october-2026-portal.js'});
  return {
    api: context.window.TS_ESAT_PORTAL, calls, storage, status, queue,
    text: () => status.children.map(child => child.textContent).join(' '),
    retry() {
      const button = status.children.find(child => child.dataset.tsEsatSaveRetry);
      assert.ok(button, 'a retry button is visible');
      listeners.get('click')({target: {closest: () => button}, preventDefault() {}});
    }
  };
}

const response = (body, status = 200) => ({ok: status >= 200 && status < 300, status, json: async () => body});
const saved = id => response({ok: true, attempt: {id}});
const canonical = value => JSON.parse(JSON.stringify(value));
const firstReport = reportFor(fixtures[0]);

// Verify the real six pathway question sets against the production template's
// two-block contract; no EmailJS requests or inbox messages are made.
for (const fixture of fixtures) {
  const h = harness();
  const r = reportFor(fixture);
  const params = h.api.emailParams(r, fixture.data.config);
  const visible = params.paper1 + '\n\n' + params.paper2;
  assert.equal((visible.match(/^Q\./gm) || []).length, 81, fixture.slug + ': exactly 81 visible email rows');
  assert.equal((params.paper1.match(/^Q\./gm) || []).length, 27);
  assert.equal((params.paper2.match(/^Q\./gm) || []).length, 54);
  assert.ok(params.paper2.includes(params.paper3));
  const summary = params.paper1.split('\n\nQUESTION-BY-QUESTION REVIEW\n')[0];
  assert.ok(summary.startsWith('MODULE SCORE SUMMARY\n'));
  assert.equal((summary.match(/Provisional TS practice score:/g) || []).length, 3);
  assert.ok(summary.includes('There is no overall ESAT scaled score.'));
  assert.ok(summary.includes(r.scoreNote));
  assert.ok(summary.includes(predictionNote));
  const completedNote=runtimeNote(false);
  assert.ok(completedNote.includes(predictionNote));
  assert.ok(reportFormats({...r,scoreNote:completedNote},fixture.data).html.includes(predictionNote));
  for (const m of r.modules) assert.ok(summary.includes(`${m.name}: ${m.rawScore} / 27 | Provisional TS practice score: ${m.provisionalScore.toFixed(1)} / 9.0`));
  const formats=reportFormats(r, fixture.data);
  assert.equal((formats.html.match(/Provisional TS practice score: <strong>4\.5 \/ 9\.0<\/strong>/g)||[]).length,3);
  assert.equal((formats.html.match(/<tr><td style=/g)||[]).length,81);
  assert.ok(formats.csv.includes('"Module raw mark (out of 27)","Provisional TS practice score (out of 9)"'));
  assert.equal(formats.csv.split('\r\n').slice(1).filter(line=>line.endsWith(',"9","4.5"')).length,81);
  const longestAnswers=canonical(r);
  longestAnswers.student.name='N'.repeat(120);longestAnswers.student.email='x'.repeat(241)+'@example.test';
  longestAnswers.modules.forEach((m,mi)=>m.questions.forEach((q,qi)=>{
    const option=fixture.data.modules[mi].questions[qi].options.reduce((a,b)=>Buffer.byteLength(a.text||'')>Buffer.byteLength(b.text||'')?a:b);
    q.selectedAnswer=option.label;q.selectedAnswerText=option.text||'';q.lastAnswerChangeAt='2026-09-20T08:01:00.000Z';
  }));
  const packetBytes=Buffer.byteLength(JSON.stringify(h.api.emailParams(longestAnswers,fixture.data.config)),'utf8');
  largestEmailPacket=Math.max(largestEmailPacket,packetBytes);
  assert.ok(packetBytes<48000,fixture.slug+': longest-answer packet remains below EmailJS guard');

  assert.equal(params.solution_link, fixture.data.config.solutionPdfUrl);
  assert.equal(params.score, `${r.totalScore} / 81`);
  assert.equal(params.to_email, r.student.email);
  assert.equal(params.session, r.student.session);
  assert.ok(!Object.hasOwn(params, 'report_html'), 'do not duplicate the large HTML report in the live template payload');
  assert.ok(Buffer.byteLength(JSON.stringify(params), 'utf8') < 48000);
  assert.ok(visible.includes(r.scoreNote));
  for (const [i, m] of r.modules.entries()) {
    assert.equal(params[`section${i + 1}_name`], m.name);
    assert.equal(params[`section${i + 1}_score`], `${m.rawScore} / 27`);
    const block = i === 0 ? params.paper1 : i === 2 ? params.paper3 : params.paper2;
    assert.ok(block.includes(m.name + ' Score:'));
    for (const q of m.questions) {
      const line = block.split('\n').find(row => row.startsWith(`Q.${q.number} |`));
      assert.ok(line.includes(`Correct: ${q.correctAnswer} — ${q.correctAnswerText}`));
      assert.ok(line.includes(`Yours: ${q.selectedAnswer ? q.selectedAnswer + ' — ' + q.selectedAnswerText : 'Unanswered'}`));
      assert.ok(line.includes('Time: '));
      assert.ok(line.includes('Last answer change: ' + (q.lastAnswerChangeAt || '—')));
    }
  }
  const nullScores = canonical(r);
  nullScores.modules[0].provisionalScore = null;
  assert.ok(h.api.emailParams(nullScores, fixture.data.config).paper1.includes('unavailable'));
  const incomplete = h.api.emailParams({...r, incomplete: true}, fixture.data.config);
  assert.ok(!/Provisional TS practice score: \d/.test(incomplete.paper1 + incomplete.paper2));
  assert.ok(!/\d+\.\d+ \/ 9\.0/.test(incomplete.paper1 + incomplete.paper2));
  assert.ok(incomplete.paper1.includes('Incomplete attempts do not contribute to your dashboard prediction.'));
  assert.ok(!incomplete.paper1.includes(predictionNote));
  const incompleteNote=runtimeNote(true);
  assert.ok(incompleteNote.includes('Incomplete attempts do not contribute'));
  assert.ok(!incompleteNote.includes(predictionNote));
  assert.ok(reportFormats({...r,incomplete:true,scoreNote:incompleteNote},fixture.data).html.includes('Incomplete attempts do not contribute'));
  const incompleteFormats=reportFormats({...r,incomplete:true},fixture.data);
  assert.ok(!incompleteFormats.html.includes('4.5 / 9.0'));
  assert.equal(incompleteFormats.csv.split('\r\n').slice(1).filter(line=>line.endsWith(',"9",""')).length,81);

  assert.equal(h.calls.length, 0);
}

// Repeated renders while the first request is in flight must share one request.
let releaseFirst;
const first = harness([() => new Promise(resolve => { releaseFirst = () => resolve(saved('server-1')); })]);
const a = first.api.onComplete(firstReport);
const b = first.api.onComplete(firstReport);
await Promise.resolve();
assert.equal(first.calls.length, 1);
assert.ok(first.text().includes('Saving'));
releaseFirst();
await Promise.all([a, b]);
assert.ok(first.text().includes('saved in your ESAT portal'));
assert.ok(first.text().includes('and contributes to your dashboard prediction using the three module estimates.'));
const sentPayload = first.calls[0].payload;
assert.equal(first.calls[0].url, '/api/practice-tests/submit');
assert.equal(first.calls[0].options.credentials, 'include');
assert.equal(sentPayload.test_id, firstReport.testId);
assert.equal(sentPayload.session_label, firstReport.attemptId);
assert.equal(sentPayload.student_name, firstReport.student.name);
assert.equal(sentPayload.started_at, firstReport.startedAt);
assert.equal(sentPayload.total_questions, 81);
assert.equal(sentPayload.score, 27);
for (const field of ['answers', 'correct_answers', 'time_spent', 'flags']) assert.equal(sentPayload[field].length, 81);
assert.equal(sentPayload.answers[2], '');
assert.equal(sentPayload.time_spent[27], 59);
assert.equal(sentPayload.flags[27], true);
assert.ok(sentPayload.incorrect.includes(2) && sentPayload.incorrect.includes(3) && sentPayload.incorrect.includes(81));
assert.ok(!sentPayload.incorrect.includes(1) && !sentPayload.incorrect.includes(28));
await first.api.onComplete(firstReport);
assert.equal(first.calls.length, 1);
// A record saved before this messaging update must also show current contribution status.
for(const [key,value] of first.storage){const record=JSON.parse(value);record.message='Your result is saved in your ESAT portal attempt history.';first.storage.set(key,JSON.stringify(record));}
const reloaded = harness([], first.storage);
await reloaded.api.onComplete(firstReport);
assert.equal(reloaded.calls.length, 0, 'a confirmed save survives reloading');
assert.ok(reloaded.text().includes('saved'));
assert.ok(reloaded.text().includes('and contributes to your dashboard prediction using the three module estimates.'));

// A network failure may happen after a committed insert. Manual retry must
// discover that row and must not repeat POST, including after a page reload.
const ambiguous = harness([new Error('Failed to fetch')]);
await ambiguous.api.onComplete(firstReport);
await ambiguous.api.onComplete(firstReport);
assert.equal(ambiguous.calls.length, 1, 'failed saves are not retried automatically');
const matchingRow = {...sentPayload, id: 'already-saved', submitted_at: firstReport.submittedAt};
matchingRow.answers = matchingRow.answers.map(value => value || null);
const reconciliation = harness([response({ok: true, attempts: [matchingRow]})], ambiguous.storage);
await reconciliation.api.onComplete(firstReport);
assert.equal(reconciliation.calls.length, 0);
reconciliation.retry();
await reconciliation.api.onComplete(firstReport);
assert.equal(reconciliation.calls.length, 1);
assert.ok(reconciliation.calls[0].url.startsWith('/api/practice-tests/attempts?test_id='));
assert.equal(reconciliation.calls[0].options.credentials, 'include');
assert.ok(reconciliation.text().includes('saved'));

// An older identical score/answer set is a different attempt, so a confirmed
// empty relevant history allows one new POST; two retry clicks still send once.
const oldRow = {...matchingRow, submitted_at: '2026-09-19T10:00:00.000Z'};
const retryNew = harness([new Error('Failed to fetch'), response({ok: true, attempts: [oldRow]}), saved('server-2')]);
await retryNew.api.onComplete(firstReport);
retryNew.retry();
await retryNew.api.onComplete(firstReport);
assert.deepEqual(retryNew.calls.map(call => call.options.method), ['POST', 'GET', 'POST']);
assert.ok(retryNew.text().includes('saved'));

// History failures and a saturated historical window must never blindly resend.
for (const history of [
  response({error: 'No session'}, 401),
  response({ok: true}),
  response({ok: true, attempts: Array.from({length: 50}, () => oldRow)})
]) {
  const h = harness([new Error('Failed to fetch'), history]);
  await h.api.onComplete(firstReport);
  h.retry();
  await h.api.onComplete(firstReport);
  assert.equal(h.calls.length, 2);
  assert.equal(h.calls.filter(call => call.options.method === 'POST').length, 1);
  assert.ok(h.text().includes('Retry saving'));
}

// Server errors after insertion and unreadable successes remain retryable;
// the browser must not claim a confirmed save without a returned attempt id.
for (const failure of [response({error: 'Server failed'}, 500), response({ok: true}), response({ok: false})]) {
  const h = harness([failure]);
  await h.api.onComplete(firstReport);
  assert.ok(h.text().includes('Retry saving'));
  assert.ok(!h.text().includes('saved in your ESAT portal attempt history'));
  assert.ok(!h.text().includes('and contributes to your dashboard prediction'));
}

// If a page reload interrupted an in-flight POST, demand reconciliation instead
// of starting another automatic write. Invalid reports must not be transmitted.
const interruptedStorage = new Map([[
  'ts-esat-october-2026:portal-save:' + firstReport.testId + ':' + firstReport.attemptId,
  JSON.stringify({status: 'sending', updatedAt: 1})
]]);
const interrupted = harness([], interruptedStorage);
await interrupted.api.onComplete(firstReport);
assert.equal(interrupted.calls.length, 0);
assert.ok(interrupted.text().includes('interrupted'));
const invalid = harness();
await invalid.api.onComplete({...firstReport, testId: 'unrecognised-test'});
assert.equal(invalid.calls.length, 0);
assert.ok(invalid.text().includes('could not be validated'));

// Early abandonment remains a local report: it must never create a portal
// attempt that could be mistaken for a fully timed test or enter predictions.
const incompleteSave = harness();
const incompleteReport = {...firstReport, incomplete: true};
await incompleteSave.api.onComplete(incompleteReport);
await incompleteSave.api.onComplete(incompleteReport);
assert.equal(incompleteSave.calls.length, 0);
assert.ok(incompleteSave.text().includes('will not be added to portal attempt history or contribute to your dashboard prediction'));
assert.ok(!incompleteSave.status.children.some(child => child.dataset.tsEsatSaveRetry));
assert.equal(incompleteSave.storage.size, 0, 'local report persistence belongs to the runtime; do not mark an incomplete attempt as sent');

console.log('October 2026 portal verification passed: all six 81-row email payloads; raw marks, answers and times; authenticated persistence; render/reload deduplication; ambiguous-save reconciliation; safe manual retries; incomplete-score handling. All API responses were mocked; no emails or database writes were sent.');

console.log('Exact per-module scoring anchors and three-module out-of-9 summaries verified; largest longest-answer email packet: '+largestEmailPacket+' bytes (limit 48000).');
