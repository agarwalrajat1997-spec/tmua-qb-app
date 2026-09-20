(() => {
  'use strict';
  if (window.TS_ESAT_PORTAL) return;

  const SAVED_MESSAGE = 'Your result is saved in your ESAT portal attempt history and contributes to your dashboard prediction using the three module estimates.';
  const PREDICTION_NOTE = 'Completed attempts saved to the portal contribute to your dashboard prediction using the three module estimates.';
  const INCOMPLETE_NOTE = 'Incomplete attempts do not contribute to your dashboard prediction.';
  const entries = new Map();
  let activeKey = '';
  const secondsText = value => {
    const seconds = Math.max(0, Math.round(Number(value) || 0));
    return String(Math.floor(seconds / 60)).padStart(2, '0') + ':' + String(seconds % 60).padStart(2, '0');
  };
  const answer = value => String(value || '').trim().toUpperCase();
  const saveKey = r => 'ts-esat-october-2026:portal-save:' + r.testId + ':' + r.attemptId;

  function emailParams(r, cfg) {
    const analyses = r.modules.map(m => {
      const estimate = !r.incomplete && m.provisionalScore != null && Number.isFinite(Number(m.provisionalScore))
        ? 'Provisional TS practice score: ' + Number(m.provisionalScore).toFixed(1) + ' / 9.0'
        : 'Provisional TS practice score: unavailable for this incomplete attempt.';
      return [
        `${m.name} Score: ${m.rawScore} / ${m.questionCount}`,
        estimate,
        `Started: ${m.startedAt || 'Not started'}`,
        `Submitted: ${m.submittedAt || 'Not submitted'}`,
        `Module time: ${secondsText(m.elapsedSeconds)} | Review: ${secondsText(m.reviewSeconds)} | Away: ${secondsText(m.awaySeconds)}`,
        '',
        ...m.questions.map(q =>
          `Q.${q.number} | Correct: ${q.correctAnswer} — ${q.correctAnswerText}` +
          ` | Yours: ${q.selectedAnswer ? q.selectedAnswer + ' — ' + q.selectedAnswerText : 'Unanswered'}` +
          ` | Result: ${q.correct ? 'Correct' : q.selectedAnswer ? 'Incorrect' : 'Unanswered'}` +
          ` | Time: ${secondsText(q.timeSpentSeconds)}` +
          ` | Last answer change: ${q.lastAnswerChangeAt || '—'}` + (q.flagged ? ' | Flagged' : '')
        )
      ].join('\n');
    });
    let solutionLink = '';
    if (cfg.solutionPdfUrl) {
      const url = new URL(cfg.solutionPdfUrl, window.location.origin);
      if (url.protocol === 'https:' || url.protocol === 'http:') solutionLink = url.href;
    }
    const baseNote = r.scoreNote || 'These practice estimates have not been calibrated against live ESAT results. Each module is converted separately; there is no overall ESAT scaled score.';
    const predictionNote = r.incomplete ? INCOMPLETE_NOTE : PREDICTION_NOTE;
    const note = baseNote.includes(predictionNote) ? baseNote : baseNote + ' ' + predictionNote;
    const moduleSummary = [
      'MODULE SCORE SUMMARY',
      ...r.modules.map(m => `${m.name}: ${m.rawScore} / ${m.questionCount} | Provisional TS practice score: ` +
        (!r.incomplete && m.provisionalScore != null && Number.isFinite(Number(m.provisionalScore))
          ? Number(m.provisionalScore).toFixed(1) + ' / 9.0'
          : 'unavailable for this incomplete attempt.')),
      note,
      /no overall ESAT scaled score/i.test(note) ? '' : 'There is no overall ESAT scaled score.'
    ].filter(Boolean).join('\n');
    const params = {
      name: r.student.name,
      to_email: r.student.email,
      test_title: r.testTitle + ' — ' + r.pathway,
      session: r.student.session || r.pathway,
      pathway: r.pathway,
      attempt_id: r.attemptId,
      timestamp: r.submittedAt,
      score: `${r.totalScore} / ${r.totalQuestions}`,
      raw_score: r.totalScore,
      solution_link: solutionLink,
      // The existing production template displays two analysis blocks.
      // Put modules 2 AND 3 in paper2; paper3 is retained for compatibility.
      paper1: `${moduleSummary}\n\nQUESTION-BY-QUESTION REVIEW\n${analyses[0]}`,
      paper2: `${analyses[1]}\n\n${analyses[2]}\n\n${note}\nQuestion times are active viewing time across all visits, rounded to the nearest second. Review and away time are tracked separately and count against the module clock.`,
      paper3: analyses[2],
      estimate_note: note
    };
    const legacyKeys = {maths1: 'mathematics_1', maths2: 'mathematics_2', physics: 'physics', chemistry: 'chemistry', biology: 'biology'};
    r.modules.forEach((m, i) => {
      params[`section${i + 1}_name`] = m.name;
      params[`section${i + 1}_score`] = `${m.rawScore} / ${m.questionCount}`;
      if (legacyKeys[m.id]) params[`${legacyKeys[m.id]}_score`] = `${m.rawScore} / ${m.questionCount}`;
    });
    return params;
  }

  function submission(r) {
    if (!r || !r.attemptId || !/^esat-october-2026-(engineering|physics-chemistry|physics-biology|maths-2-chemistry|maths-2-biology|chemistry-biology)$/.test(r.testId) ||
        !Array.isArray(r.modules) || r.modules.length !== 3 || r.modules.some(m => !Array.isArray(m.questions) || m.questions.length !== 27) ||
        !Number.isFinite(Date.parse(r.startedAt)) || !Number.isInteger(r.totalScore) || r.totalScore < 0 || r.totalScore > 81) {
      throw new Error('The completed report could not be validated. Download your report before leaving this page.');
    }
    const questions = r.modules.flatMap(m => m.questions);
    return {
      test_id: r.testId,
      test_title: r.testTitle + ' — ' + r.pathway,
      paper: 'full',
      total_questions: 81,
      score: r.totalScore,
      answers: questions.map(q => answer(q.selectedAnswer)),
      correct_answers: questions.map(q => answer(q.correctAnswer)),
      time_spent: questions.map(q => Math.max(0, Number(q.timeSpentSeconds) || 0)),
      flags: questions.map(q => q.flagged === true),
      incorrect: questions.flatMap((q, i) => answer(q.selectedAnswer) && answer(q.selectedAnswer) === answer(q.correctAnswer) ? [] : [i + 1]),
      started_at: r.startedAt,
      student_name: r.student.name,
      session_label: r.attemptId
    };
  }

  function readRecord(key) {
    try {
      const value = JSON.parse(localStorage.getItem(key) || 'null');
      if (!value || !['sent', 'sending', 'failed'].includes(value.status)) return null;
      if (value.status === 'sent') value.message = SAVED_MESSAGE;
      return value;
    } catch (_) { return null; }
  }

  function render(entry) {
    if (activeKey !== entry.key) return;
    const node = document.getElementById('portal-attempt-status');
    if (!node) return;
    node.setAttribute('role', 'status');
    node.setAttribute('aria-live', 'polite');
    const message = document.createElement('p');
    message.textContent = entry.record.message;
    const children = [message];
    if (entry.record.status === 'failed') {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'btn secondary';
      button.textContent = 'Retry saving to portal';
      button.dataset.tsEsatSaveRetry = entry.key;
      children.push(button);
    }
    const link = document.createElement('a');
    link.href = '/esat?view=tests';
    link.className = 'btn secondary';
    link.textContent = 'Return to practice tests';
    children.push(link);
    node.replaceChildren(...children);
  }

  function remember(entry, record) {
    entry.record = {...record, updatedAt: Date.now()};
    try { localStorage.setItem(entry.key, JSON.stringify(entry.record)); } catch (_) {}
    render(entry);
  }

  async function request(url, options) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 25000);
    try {
      const response = await fetch(url, {...options, credentials: 'include', cache: 'no-store', signal: controller.signal});
      if (response.status === 401 || response.status === 403) throw new Error('Sign in to the ESAT portal, then retry saving. Your answers remain saved in this browser.');
      if (!response.ok) throw new Error('The portal did not confirm saving (HTTP ' + response.status + '). Retry checks your attempt history before sending again.');
      let body;
      try { body = await response.json(); } catch (_) { throw new Error('The portal returned an unreadable response. Retry checks your attempt history before sending again.'); }
      if (!body || body.ok !== true || body.error) throw new Error('The portal did not confirm saving. Retry checks your attempt history before sending again.');
      return body;
    } finally { clearTimeout(timer); }
  }

  function sameArray(a, b, normalise) {
    return Array.isArray(a) && a.length === b.length && a.every((value, i) => normalise(value) === normalise(b[i]));
  }

  async function findSaved(entry, payload) {
    const body = await request('/api/practice-tests/attempts?test_id=' + encodeURIComponent(payload.test_id), {method: 'GET'});
    if (!Array.isArray(body.attempts)) throw new Error('Attempt history could not be checked. Nothing has been sent again; please retry later.');
    const matching = body.attempts.find(row => row && row.id && row.test_id === payload.test_id &&
      Number(row.total_questions) === 81 && Number(row.score) === payload.score &&
      Date.parse(row.submitted_at) >= Date.parse(entry.report.startedAt) &&
      sameArray(row.answers, payload.answers, answer) &&
      sameArray(row.correct_answers, payload.correct_answers, answer) &&
      sameArray(row.time_spent, payload.time_spent, value => Number(value) || 0) &&
      sameArray(row.flags, payload.flags, value => value === true));
    if (matching) return matching;
    // This existing endpoint exposes the oldest 50 attempts. If that window is
    // full, an ambiguous prior write may be outside it; do not create a duplicate.
    if (body.attempts.length >= 50) throw new Error('Your attempt history is too long to confirm this save safely. Download your report and contact Thriving Scholars before retrying.');
    return null;
  }

  function save(entry, reconcile) {
    if (entry.pending) return entry.pending;
    remember(entry, {status: 'sending', message: reconcile ? 'Checking your portal attempt history…' : 'Saving your result to the ESAT portal…'});
    entry.pending = Promise.resolve().then(async () => {
      try {
        const payload = submission(entry.report);
        let existing;
        if (reconcile) existing = await findSaved(entry, payload);
        if (existing) {
          remember(entry, {status: 'sent', serverAttemptId: existing.id, message: SAVED_MESSAGE});
          return entry.record;
        }
        remember(entry, {status: 'sending', message: 'Saving your result to the ESAT portal…'});
        const body = await request('/api/practice-tests/submit', {
          method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)
        });
        if (!body.attempt || !body.attempt.id) throw new Error('The portal did not return a saved attempt. Retry checks your attempt history before sending again.');
        remember(entry, {status: 'sent', serverAttemptId: body.attempt.id, message: SAVED_MESSAGE});
      } catch (error) {
        const message = error && error.name === 'AbortError'
          ? 'Saving timed out; the portal may still have received your result. Retry checks your attempt history before sending again.'
          : error && error.message && error.message !== 'Failed to fetch'
            ? error.message
            : 'The portal could not confirm saving. Your answers remain here. Retry checks your attempt history before sending again.';
        remember(entry, {status: 'failed', message});
      } finally { entry.pending = null; }
      return entry.record;
    });
    return entry.pending;
  }

  function onComplete(r) {
    if (!r || !r.attemptId || !r.testId) return Promise.resolve(null);
    const key = saveKey(r);
    activeKey = key;
    if (r.incomplete) {
      const entry = {
        key,
        report: r,
        pending: null,
        record: {status: 'incomplete', message: 'Incomplete attempt kept in this browser. Download your report; it will not be added to portal attempt history or contribute to your dashboard prediction.'}
      };
      entries.set(key, entry);
      render(entry);
      return Promise.resolve(entry.record);
    }
    let entry = entries.get(key);
    if (!entry) {
      const saved = readRecord(key);
      entry = {key, report: r, pending: null, record: saved || {status: 'new', message: ''}};
      entries.set(key, entry);
      if (saved && saved.status === 'sending') {
        remember(entry, {status: 'failed', message: 'A previous save was interrupted. Retry checks your portal attempt history before sending again.'});
      }
    }
    entry.report = r;
    if (entry.record.status === 'new') return save(entry, false);
    render(entry);
    return entry.pending || Promise.resolve(entry.record);
  }

  document.addEventListener('click', event => {
    const button = event.target && event.target.closest && event.target.closest('[data-ts-esat-save-retry]');
    if (!button) return;
    const entry = entries.get(button.dataset.tsEsatSaveRetry);
    if (!entry || entry.pending || entry.record.status !== 'failed') return;
    event.preventDefault();
    void save(entry, true);
  });

  window.TS_ESAT_PORTAL = {emailParams, onComplete};
})();
