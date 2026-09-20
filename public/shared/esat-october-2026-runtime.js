(function () {
  'use strict';
  const ANCHORS = {
    maths1: [[0,1],[13,4.5],[14,5],[17,6],[20,7],[23,8],[26,9],[27,9]],
    maths2: [[0,1],[11,4.5],[12,5],[15,6],[18,7],[22,8],[25,9],[27,9]],
    physics: [[0,1],[15,4.5],[16,5],[19,6],[22,7],[24,8],[27,9]],
    chemistry: [[0,1],[16,4.5],[17,5],[20,6],[23,7],[25,8],[27,9]],
    biology: [[0,1],[18,4.5],[19,5],[22,6],[24,7],[26,8],[27,9]]
  };
  const esc = value => String(value == null ? '' : value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const iso = value => value == null ? null : new Date(value).toISOString();
  const canonicalId = id => ({mathematics1:'maths1',mathematics2:'maths2',math1:'maths1',math2:'maths2',m1:'maths1',m2:'maths2'}[String(id).toLowerCase().replace(/[^a-z0-9]/g,'')] || String(id).toLowerCase().replace(/[^a-z0-9]/g,''));
  function plainMath(value) {
    let text=String(value).replace(/\\{2,}/g,'\\').replace(/\\(?:dfrac|tfrac)(?![A-Za-z])/g,'\\frac');
    for(let i=0;i<6;i++) {
      const previous=text;
      text=text.replace(/\\(?:text|mathrm|operatorname)\{([^{}]*)\}/g,'$1').replace(/\\sqrt\{([^{}]*)\}/g,'√($1)').replace(/\\frac\s*(?:\{([^{}]*)\}|([A-Za-z0-9]))\s*(?:\{([^{}]*)\}|([A-Za-z0-9]))/g,(_,a,b,c,d)=>'('+(a??b)+')/('+(c??d)+')');
      if(previous===text)break;
    }
    const symbols={times:'×',cdot:'·',div:'÷',leq:'≤',le:'≤',geq:'≥',ge:'≥',neq:'≠',ne:'≠',approx:'≈',infty:'∞',pi:'π',theta:'θ',alpha:'α',beta:'β',gamma:'γ',lambda:'λ',mu:'μ',Delta:'Δ',circ:'°'};
    return text.replace(/\\(times|cdot|div|leq|le|geq|ge|neq|ne|approx|infty|pi|theta|alpha|beta|gamma|lambda|mu|Delta|circ)(?![A-Za-z])/g,(_,key)=>symbols[key]).replace(/\\(?:left|right)\b/g,'').replace(/\\[,;:!]/g,' ').replace(/\\%/g,'%').replace(/\^\{([^{}]*)\}/g,'^($1)').replace(/_\{([^{}]*)\}/g,'_($1)').replace(/\s+/g,' ').trim();
  }
  function scoreFor(id, raw) {
    const points = ANCHORS[canonicalId(id)];
    if (!points) throw new Error('Missing practice conversion for ' + id);
    raw = Math.max(0,Math.min(27,Number(raw)));
    for (let i=1;i<points.length;i++) if (raw <= points[i][0]) {
      const [x0,y0] = points[i-1], [x1,y1] = points[i];
      return Math.round((y0+(raw-x0)*(y1-y0)/(x1-x0))*10)/10;
    }
    return 9;
  }
  function accrueState(s,until) {
    if(s.status!=='running'||!s.clock) return;
    const m=s.modules[s.moduleIndex],end=Math.min(until,m.deadline),elapsed=Math.max(0,end-s.clock.lastAt);
    if(s.clock.attention) {
      if(s.clock.view==='question') m.timesMs[s.clock.questionIndex]+=elapsed;
      else m.reviewMs+=elapsed;
    } else m.awayMs+=elapsed;
    s.clock.lastAt=Math.max(s.clock.lastAt,end);
  }
  function beginModuleState(s,index,now,durationMs,attention) {
    s.moduleIndex=index; s.questionIndex=0; s.view='question';
    const m=s.modules[index];m.startedAt=now;m.deadline=now+durationMs;
    s.clock={lastAt:now,view:s.view,questionIndex:0,attention};
  }
  function finishModuleState(s,at,reason,durationMs,moduleCount) {
    const m=s.modules[s.moduleIndex];m.submittedAt=at;m.submissionReason=reason;
    if(s.moduleIndex<moduleCount-1) beginModuleState(s,s.moduleIndex+1,at,durationMs,false);
    else {s.status='complete';s.submittedAt=at;s.clock=null;s.delivery={status:'not-sent',message:''};}
  }
  function syncState(s,now,{durationMs=2400000,moduleCount=3,resumed=false,visible=true}={}) {
    if(s.status!=='running')return false;
    if(resumed&&s.clock)s.clock.attention=false;
    let advanced=false;
    while(s.status==='running'&&now>=s.modules[s.moduleIndex].deadline) {
      const deadline=s.modules[s.moduleIndex].deadline;
      accrueState(s,deadline);finishModuleState(s,deadline,'time-expired',durationMs,moduleCount);advanced=true;
    }
    if(s.status==='running') {accrueState(s,now);s.clock.attention=visible;}
    return advanced;
  }
  if(typeof document==='undefined') {
    if(typeof module!=='undefined')module.exports={scoreFor,anchors:ANCHORS,canonicalId,plainMath,accrueState,beginModuleState,finishModuleState,syncState};
    return;
  }
  const DATA = JSON.parse(document.getElementById('test-data').textContent);
  const CFG = DATA.config || {};
  const app = document.getElementById('app');
  const DURATION = Number(CFG.durationSeconds) > 0 ? Number(CFG.durationSeconds) * 1000 : 2400000;
  const KEY = 'ts-esat-2026-v3:' + DATA.id;
  const isAttentive=()=>!resumePending&&document.visibilityState!=='hidden'&&(typeof document.hasFocus!=='function'||document.hasFocus());
  const totalQuestions = DATA.modules.reduce((n,m) => n + m.questions.length, 0);
  const fingerprint = JSON.stringify(DATA.modules.map(m => [m.id,m.sourceSha256||'',m.questions.map(q => [q.number,q.correctAnswer,q.options.map(o => o.label)])]));
  let storageFailure = false, notice = '', resultsModule = 0, solutionQuestion = 0, solutionsVisible = false, timerHidden = false, notesVisible = false;
  let state;
  let deliveryInFlight = false;
  let resumePending=false,candidateDraft=null,navOpen=false,prefs={scheme:'standard',large:false,hideTimer:false};
  try { prefs={...prefs,...JSON.parse(localStorage.getItem('ts-esat-display-prefs')||'{}')}; } catch (_) {}
  if(!['standard','cream','blue-tint','high-contrast'].includes(prefs.scheme))prefs.scheme='standard';
  timerHidden=!!prefs.hideTimer;
  function savePrefs(){try{localStorage.setItem('ts-esat-display-prefs',JSON.stringify(prefs));}catch(_){}}

  function fresh() {
    return { version:3,testId:DATA.id,fingerprint,status:'ready',student:{name:'',email:''},attemptId:'',startedAt:null,submittedAt:null,moduleIndex:0,questionIndex:0,view:'question',clock:null,delivery:{status:'not-sent',message:''},modules:DATA.modules.map(m => ({answers:m.questions.map(() => null),flags:m.questions.map(() => false),timesMs:m.questions.map(() => 0),answerUpdatedAt:m.questions.map(() => null),notes:m.questions.map(() => ''),reviewMs:0,awayMs:0,startedAt:null,deadline:null,submittedAt:null,submissionReason:null})) };
  }
  function validSaved(s) {
    if(!s||s.version!==3||s.fingerprint!==fingerprint||!['ready','running','complete'].includes(s.status))return false;
    if(!Number.isInteger(s.moduleIndex)||s.moduleIndex<0||s.moduleIndex>=DATA.modules.length||!Array.isArray(s.modules)||s.modules.length!==DATA.modules.length)return false;
    if(!Number.isInteger(s.questionIndex)||s.questionIndex<0||s.questionIndex>=DATA.modules[s.moduleIndex].questions.length||!['question','review'].includes(s.view)||!s.student||typeof s.student.name!=='string'||typeof s.student.email!=='string'||!s.delivery)return false;
    if(!s.modules.every((m,mi)=>{
      const qs=DATA.modules[mi].questions;
      return ['answers','flags','timesMs','notes'].every(key=>Array.isArray(m[key])&&m[key].length===qs.length)&&m.answers.every((a,i)=>a===null||qs[i].options.some(o=>o.label===a))&&m.flags.every(f=>typeof f==='boolean')&&m.notes.every(n=>typeof n==='string')&&m.timesMs.every(t=>Number.isFinite(t)&&t>=0)&&Number.isFinite(m.reviewMs)&&m.reviewMs>=0&&Number.isFinite(m.awayMs)&&m.awayMs>=0;
    }))return false;
    if(s.status==='running') {
      const m=s.modules[s.moduleIndex],c=s.clock;
      if(!c||!Number.isFinite(c.lastAt)||!Number.isInteger(c.questionIndex)||c.questionIndex<0||c.questionIndex>=m.answers.length||!['question','review'].includes(c.view)||!Number.isFinite(m.startedAt)||!Number.isFinite(m.deadline)||m.deadline<=m.startedAt)return false;
    }
    if(s.status==='complete'&&(!Number.isFinite(s.startedAt)||!Number.isFinite(s.submittedAt)||!s.modules.every(m=>Number.isFinite(m.startedAt)&&Number.isFinite(m.submittedAt))))return false;
    return true;
  }
  try {
    const saved = JSON.parse(localStorage.getItem(KEY) || 'null');
    const valid=validSaved(saved); state = valid ? saved : fresh(); resumePending=valid&&saved.status!=='ready';
  } catch (_) { state = fresh(); storageFailure = true; }
  if (state.delivery.status === 'sending') state.delivery = {status:'failed',message:'The previous email request was interrupted; delivery could not be confirmed. Check your inbox before retrying.'};
  function save() { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (_) { storageFailure = true; } }
  function msText(ms) { const s = Math.max(0,Math.floor(ms/1000)); return String(Math.floor(s/60)).padStart(2,'0') + ':' + String(s%60).padStart(2,'0'); }
  function secondsText(seconds) { return msText(Math.round(seconds)*1000); }
  function accrue(until) {
    accrueState(state,until);
  }
  function resetClock(now, attention = isAttentive()) {
    state.clock = {lastAt:now,view:state.view,questionIndex:state.questionIndex,attention};
  }
  function beginModule(index, now, attention) {
    beginModuleState(state,index,now,DURATION,attention); notesVisible=false;
  }
  function finishModule(at, reason) {
    finishModuleState(state,at,reason,DURATION,DATA.modules.length); notesVisible=false;
  }
  function sync(now = Date.now(), resumed = false) {
    const advanced=syncState(state,now,{durationMs:DURATION,moduleCount:DATA.modules.length,resumed,visible:isAttentive()});
    save();
    if (advanced) {
      document.getElementById('submit-dialog')?.close();
      notice=state.status==='complete' ? 'The final module timer ended. Your test has been submitted.' : 'The previous module timer ended. The next module has started automatically.';
    }
    return advanced;
  }
  function start(name,email,session='Practice sitting') {
    state=fresh(); state.student={name:name.trim(),email:email.trim(),session}; candidateDraft=null; navOpen=false;
    state.attemptId=globalThis.crypto?.randomUUID ? crypto.randomUUID() : DATA.id+'-'+Date.now()+'-'+Math.random().toString(36).slice(2);
    state.status='running'; state.startedAt=Date.now(); beginModule(0,state.startedAt,true); save(); render();
  }
  function moduleRaw(index) { return DATA.modules[index].questions.reduce((n,q,i) => n+(state.modules[index].answers[i]===q.correctAnswer ? 1:0),0); }
  function plain(html) {
    const el=document.createElement('div'); el.innerHTML=html || '';
    el.querySelectorAll('[data-tex]').forEach(n => n.replaceWith(document.createTextNode(n.getAttribute('data-tex'))));
    el.querySelectorAll('img').forEach(n => n.replaceWith(document.createTextNode(n.alt || '[diagram]')));
    el.querySelectorAll('svg').forEach(n => n.replaceWith(document.createTextNode(n.getAttribute('aria-label') || n.querySelector('title')?.textContent || '[diagram]')));
    el.querySelectorAll('br').forEach(n => n.replaceWith(document.createTextNode(' ')));
    return el.textContent.replace(/\s+/g,' ').trim();
  }
  function optionText(q,label) { const option=q.options.find(o=>o.label===label);return label ? plainMath(option?.text || plain(option?.html || '')) : 'Unanswered'; }
  function report() {
    if (state.status !== 'complete') return null;
    return {schemaVersion:1,testId:DATA.id,testTitle:DATA.title || 'ESAT Practice Test 2026',pathway:DATA.pathway,attemptId:state.attemptId,student:{...state.student},startedAt:iso(state.startedAt),submittedAt:iso(state.submittedAt),generatedAt:iso(Date.now()),incomplete:!!state.incomplete,totalScore:DATA.modules.reduce((n,_,i) => n+moduleRaw(i),0),totalQuestions,scoreLabel:'Provisional TS practice score',scoreNote:'These practice estimates have not been calibrated against live ESAT results. Each module is converted separately. Interpolation, including below 4.5, is a display convention; there is no overall ESAT scaled score.'+(state.incomplete?' Incomplete attempts do not contribute to your dashboard prediction.':' Completed attempts saved to the portal contribute to your dashboard prediction using the three module estimates.'),modules:DATA.modules.map((m,mi) => ({id:m.id,name:m.name,rawScore:moduleRaw(mi),questionCount:m.questions.length,provisionalScore:state.incomplete?null:scoreFor(m.id,moduleRaw(mi)),startedAt:iso(state.modules[mi].startedAt),submittedAt:iso(state.modules[mi].submittedAt),submissionReason:state.modules[mi].submissionReason,elapsedSeconds:Math.round((state.modules[mi].submittedAt-state.modules[mi].startedAt)/1000),reviewSeconds:Math.round(state.modules[mi].reviewMs/1000),awaySeconds:Math.round(state.modules[mi].awayMs/1000),questions:m.questions.map((q,i) => ({number:q.number,selectedAnswer:state.modules[mi].answers[i],selectedAnswerText:optionText(q,state.modules[mi].answers[i]),correctAnswer:q.correctAnswer,correctAnswerText:optionText(q,q.correctAnswer),correct:state.modules[mi].answers[i]===q.correctAnswer,timeSpentSeconds:Math.round(state.modules[mi].timesMs[i]/1000),flagged:state.modules[mi].flags[i],lastAnswerChangeAt:iso(state.modules[mi].answerUpdatedAt?.[i])}))}))};
  }
  function reportHTML(r=report()) {
    if (!r) return '';
    const cell='padding:6px;border-bottom:1px solid #ddd;';
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(r.testTitle)+' — score report</title></head><body style="margin:0;background:#edf0f3;font:14px/1.5 Arial,Helvetica,sans-serif;color:#202020"><main style="max-width:900px;margin:20px auto;background:#fff">'+
      '<header style="padding:25px 28px;background:#0f6f9f;color:white"><strong style="font-size:23px">Thriving Scholars</strong><h1 style="margin:10px 0;font-size:24px">'+esc(r.testTitle)+'</h1><div>'+esc(r.pathway)+'</div></header><div style="padding:22px 28px;background:#f5f8fb"><p><strong>'+esc(r.student.name)+'</strong> · '+esc(r.student.email)+'</p><p style="font-size:20px;color:#075d91"><strong>Raw mark: '+r.totalScore+' / '+r.totalQuestions+'</strong></p><p>Started: '+esc(r.startedAt)+'<br>Submitted: '+esc(r.submittedAt)+'<br>Attempt: '+esc(r.attemptId)+'</p><p style="font-size:12px">'+esc(r.scoreNote)+'</p></div>'+
      r.modules.map(m => '<section style="padding:20px 24px"><h2 style="font-size:20px;color:#075d91;margin:0 0 10px">'+esc(m.name)+'</h2><p><strong>'+m.rawScore+'/'+m.questionCount+'</strong> · Provisional TS practice score: <strong>'+(r.incomplete||m.provisionalScore==null?'Unavailable':m.provisionalScore.toFixed(1)+' / 9.0')+'</strong></p><p style="font-size:12px">Started: '+esc(m.startedAt)+' · Submitted: '+esc(m.submittedAt)+'<br>Module time '+secondsText(m.elapsedSeconds)+' · Review '+secondsText(m.reviewSeconds)+' · Away from test '+secondsText(m.awaySeconds)+'</p><table style="width:100%;border-collapse:collapse;font-size:12px"><thead><tr style="background:#eaf3f8">'+['Q','Your answer','Correct answer','Result','Time','Last answer change (UTC)'].map(t => '<th style="'+cell+'">'+t+'</th>').join('')+'</tr></thead><tbody>'+m.questions.map(q => '<tr><td style="'+cell+'">'+q.number+'</td><td style="'+cell+'">'+esc(q.selectedAnswer ? q.selectedAnswer+' — '+q.selectedAnswerText : 'Unanswered')+'</td><td style="'+cell+'">'+esc(q.correctAnswer+' — '+q.correctAnswerText)+'</td><td style="'+cell+'color:'+(q.correct?'#155e3b':'#922c21')+'">'+(q.correct?'Correct':q.selectedAnswer?'Incorrect':'Unanswered')+'</td><td style="'+cell+'white-space:nowrap">'+secondsText(q.timeSpentSeconds)+'</td><td style="'+cell+'">'+esc(q.lastAnswerChangeAt||'—')+'</td></tr>').join('')+'</tbody></table></section>').join('')+
      /* TS_ESAT_PDF_REPORT_LINK_V1 */
      (CFG.solutionPdfUrl ? '<div style="padding:18px 28px;background:#f5f8fb"><a href="'+esc(CFG.solutionPdfUrl)+'" target="_blank" rel="noopener noreferrer" style="display:inline-block;padding:12px 18px;background:#075d91;color:#fff;text-decoration:none;border-radius:8px;font-weight:bold">Open '+esc(DATA.pathway)+' solution book (PDF)</a></div>' : '')+
      '<footer style="padding:22px 28px;border-top:1px solid #e7ddcf;font-size:12px;color:#657080">Question time is active viewing time across all visits. Module review and time away from the test are tracked separately; all continue to count against the module clock. Times are rounded to the nearest second. Generated '+esc(r.generatedAt)+'.</footer></main></body></html>';
  }
  function csv(r=report()) {
    const quote=x => '"'+String(x == null ? '' : x).replace(/"/g,'""')+'"';
    const rows=[['Pathway','Module','Question','Selected letter','Selected answer','Correct letter','Correct answer','Result','Time spent seconds','Flagged','Module started UTC','Module submitted UTC','Last answer change UTC','Module raw mark (out of 27)','Provisional TS practice score (out of 9)']];
    r.modules.forEach(m => m.questions.forEach(q => rows.push([r.pathway,m.name,q.number,q.selectedAnswer || '',q.selectedAnswerText,q.correctAnswer,q.correctAnswerText,q.correct?'Correct':q.selectedAnswer?'Incorrect':'Unanswered',q.timeSpentSeconds,q.flagged?'Yes':'No',m.startedAt,m.submittedAt,q.lastAnswerChangeAt||'',m.rawScore,r.incomplete||m.provisionalScore==null?'':m.provisionalScore.toFixed(1)])));
    return '\uFEFF'+rows.map(row => row.map(quote).join(',')).join('\r\n');
  }
  function download(contents,type,suffix) {
    const blob=new Blob([contents],{type}), url=URL.createObjectURL(blob), a=document.createElement('a');
    a.href=url; a.download=DATA.id+'_'+state.attemptId.slice(0,8)+'_'+suffix; document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url),3000);
  }
  function emailConfigured() { return Boolean(CFG.reportEndpoint || (CFG.emailjs?.serviceId && CFG.emailjs?.templateId && CFG.emailjs?.publicKey && CFG.emailjs?.enabled !== false)); }
  async function sendReport(manual=false) {
    if (state.status !== 'complete' || deliveryInFlight || (state.delivery.status==='sent' && !manual)) return;
    if (!emailConfigured()) { state.delivery={status:'unconfigured',message:'Automatic email delivery is not connected for this copy. Download your complete report below.'}; save(); updateDelivery(); return; }
    if(!state.student.email) {state.delivery={status:'failed',message:'No email address was provided. Download your complete report below.'};save();updateDelivery();return;}
    const r=report(), html=reportHTML(r); deliveryInFlight=true;
    state.delivery={status:'sending',message:'Sending your complete score report…'}; save(); updateDelivery();
    const controller=new AbortController(), timeout=setTimeout(() => controller.abort(),25000);
    try {
      let endpoint=CFG.reportEndpoint, payload;
      if (endpoint) payload={...r,report_html:html,idempotencyKey:r.attemptId};
      else {
        endpoint='https://api.emailjs.com/api/v1.0/email/send';
        payload={service_id:CFG.emailjs.serviceId,template_id:CFG.emailjs.templateId,user_id:CFG.emailjs.publicKey,template_params:window.TS_ESAT_PORTAL ? window.TS_ESAT_PORTAL.emailParams(r,CFG) : {name:r.student.name,to_email:r.student.email,test_title:r.testTitle+' — '+r.pathway,session:r.pathway,pathway:r.pathway,attempt_id:r.attemptId,timestamp:r.submittedAt,score:r.totalScore+'/'+r.totalQuestions,raw_score:r.totalScore,report_html:html,estimate_note:r.scoreNote}};
        if (new Blob([JSON.stringify(payload.template_params)]).size>48000) throw new Error('This detailed report exceeds the email service limit. Download the full report below.');
      }
      const response=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),signal:controller.signal,credentials:'omit'});
      const text=await response.text();
      if (!response.ok) throw new Error('The email service returned '+response.status+'.');
      if(!CFG.reportEndpoint&&(response.status!==200||text.trim()!=='OK'))throw new Error('The email service returned an unexpected response; delivery could not be confirmed.');
      let parsed; try { parsed=JSON.parse(text); } catch (_) {}
      if (parsed && (parsed.success===false || parsed.ok===false || parsed.error)) throw new Error('The email service did not accept the report.');
      if(state.attemptId===r.attemptId)state.delivery={status:'sent',message:'The email service accepted your report for '+r.student.email+'. Check your inbox and spam folder.',sentAt:Date.now()};
    } catch (e) {
      if(state.attemptId===r.attemptId)state.delivery={status:'failed',message:(e.name==='AbortError'?'The email request timed out; delivery could not be confirmed.':e.message==='Failed to fetch'?'Email could not be sent from this browser. Check your connection or use the hosted test.':e.message)+' Your score is saved here. Download the full report or retry.'};
    } finally { clearTimeout(timeout); deliveryInFlight=false; save(); updateDelivery(); }
  }
  function deliveryMarkup() {
    const d=state.delivery;
    const msg=d.message || (emailConfigured()?'Your complete score report can be emailed to '+state.student.email+'.':'Automatic email delivery is not connected for this copy. Download your complete report below.');
    return '<div class="notice '+(d.status==='failed'?'error':'')+'" role="status">'+esc(msg)+'</div>'+(emailConfigured()?'<button class="btn secondary" data-action="email" '+(d.status==='sending'?'disabled':'')+'>'+(d.status==='sent'?'Send report again':d.status==='failed'?'Retry email':'Send report')+'</button>':'');
  }
  function updateDelivery() { const el=document.getElementById('email-status'); if(el) el.innerHTML=deliveryMarkup(); }
  function banner() { return (storageFailure?'<div class="notice error">This browser cannot save progress locally. Keep this tab open until submission; refreshing may lose your answers.</div>':'')+(notice?'<div class="notice" role="status">'+esc(notice)+'</div>':''); }
  function toolbar() {
    const active=state.status==='running'&&!resumePending, m=DATA.modules[state.moduleIndex];
    const count=active?(state.view==='review'?'Review':(state.questionIndex+1)+' of '+m.questions.length):state.status==='complete'?'Test complete':'Three modules';
    return `<header class="exam-header"><div class="brand"><small>Thriving Scholars</small>Engineering and Science Admissions Test (ESAT)</div><div class="header-right">${active?`<span class="time-box" id="timeBox"><span ${timerHidden?'hidden':''} id="clockWrap">Time remaining <span id="timer" role="timer"></span></span><button class="text-button" data-action="timer">${timerHidden?'Show time':'Hide'}</button></span>`:`<span>${state.status==='complete'?'Test complete':'ESAT Practice Test 2026'}</span>`}<span class="header-count">${esc(count)}</span></div></header><div class="sub-header"><span class="sub-label">${active?'Module '+(state.moduleIndex+1)+' · '+esc(m.name):esc(DATA.pathway)}</span><div class="sub-tools"><button class="text-button" data-action="text-size" aria-pressed="${prefs.large}">Text size</button><button class="text-button" data-action="fullscreen">${document.fullscreenElement?'Exit full screen':'Full screen'}</button><select id="scheme-select" class="scheme-select" aria-label="Colour scheme">${[['standard','Colour scheme: standard'],['cream','Cream'],['blue-tint','Pale blue'],['high-contrast','High contrast']].map(([v,t])=>`<option value="${v}" ${prefs.scheme===v?'selected':''}>${t}</option>`).join('')}</select></div></div>`;
  }
  function instructions() {
    if(candidateDraft) return `<div class="screen"><section class="welcome-card"><p class="eyebrow">Before you begin</p><h1>ESAT instructions</h1><p class="subtitle">${esc(candidateDraft.name)} · ${esc(candidateDraft.session)} · 120 minutes in total</p><ol class="instruction-list"><li>There are <strong>three modules</strong>: ${DATA.modules.map(m=>esc(m.name)).join(', ')}. Each has <strong>27 questions</strong> and a separate <strong>40-minute</strong> timer.</li><li>Select <strong>Start ${esc(DATA.modules[0].name)}</strong> to begin. The next module starts immediately when the current module is submitted or its time expires.</li><li>Use <strong>Previous, Next, Navigator</strong> and <strong>Flag for review</strong>. The review table lists answered, unanswered and flagged questions while the timer continues.</li><li>Submitted modules stay locked. Raw marks, correct answers, worked solutions and your solution PDF become available only after final submission.</li><li>The clock continues during a short break, when you switch tabs, and when you close or refresh this page. Unused time does not transfer.</li><li><strong>Keyboard:</strong> Alt+N / Alt+Shift+N = next; Alt+P / Alt+Shift+P = previous; Alt+F / Alt+Shift+F = flag; Alt+V = navigator; Alt+R = review. Escape closes the navigator or returns from review. Answer letters select an option.</li></ol><div class="report">Your results show raw marks and a separate <strong>Provisional TS practice score</strong> for each module. These estimates have not been calibrated against live ESAT results; there is no combined scaled ESAT score.</div><p class="small-note">No calculator, dictionary or formula booklet. Use a separate sheet or erasable board for working. Timer visibility, text size and colour scheme can be changed during the test.</p><div class="button-row"><button class="secondary" data-action="back-welcome">Back</button><button class="primary" data-action="begin">Start ${esc(DATA.modules[0].name)}</button></div></section></div>`;
    return `<div class="screen"><section class="welcome-card"><p class="eyebrow">Thriving Scholars · Digital practice</p><h1>ESAT Practice Test 2026</h1><p class="subtitle">${esc(DATA.pathway)}<br>${DATA.modules.map(m=>esc(m.name)).join(' · ')}</p><div class="welcome-layout"><div><h2>Test format</h2><table class="format-table"><thead><tr><th>Module</th><th>Questions</th><th>Time</th></tr></thead><tbody>${DATA.modules.map((m,i)=>`<tr><td>Module ${i+1}<small>${esc(m.name)}</small></td><td>${m.questions.length}</td><td>40 min</td></tr>`).join('')}</tbody></table><ul class="rules"><li><strong>81 questions · 120 minutes.</strong> Modules run consecutively, with no scheduled break.</li><li>Choose one answer per question. Incorrect and blank answers score zero.</li><li>No calculator, dictionary or formula booklet.</li><li>Revisit questions within the current module. Submitted modules stay locked.</li><li>Unused time does not transfer to the next module.</li></ul></div><form class="candidate-form" id="start-form"><h2>Your details</h2><div class="field"><label for="student-name">Full name</label><input id="student-name" name="studentName" autocomplete="name" maxlength="120" placeholder="Enter your full name" required></div><div class="field"><label for="student-email">Email for your report</label><input id="student-email" name="studentEmail" type="email" autocomplete="email" maxlength="254" placeholder="you@example.com" ${emailConfigured()?'required':''}></div><div class="field"><label for="student-session">ESAT session</label><select id="student-session" name="studentSession"><option>Practice sitting</option><option>October 2026</option><option>January 2027</option></select></div><p class="form-note">${emailConfigured()?'Your score report will be emailed automatically when you finish. Your name, email and results are sent through Thriving Scholars’ email service. Email and the linked PDF need an internet connection.':'Your details appear on your downloadable report.'}</p><button type="submit" class="primary">Read instructions</button></form></div><p class="source-note">Independent practice material by Thriving Scholars; not an official UAT-UK or Pearson test.<br><a href="https://esat-tmua.ac.uk/about-the-tests/esat-test/" target="_blank" rel="noopener">Official ESAT format</a><a href="/esat?view=tests">Return to ESAT practice tests</a></p></section></div>`;
  }
  function moduleTabs() { return ''; }
  function running() {
    if(state.view==='review') return reviewMarkup()+submitDialog();
    const mi=state.moduleIndex,m=DATA.modules[mi],s=state.modules[mi],q=m.questions[state.questionIndex],a=s.answers[state.questionIndex],flag=s.flags[state.questionIndex];
    return `<div class="question-wrap"><div class="question-meta"><div class="section-name">Module ${mi+1} · ${esc(m.name)}</div><button class="flag-button ${flag?'active':''}" data-action="flag" aria-pressed="${flag}"><span class="flag-icon" aria-hidden="true">⚑</span> ${flag?'Flagged for review':'Flag for review'}</button></div><div class="question-topline"><span class="module-chip">M${mi+1}</span><span class="question-number" tabindex="-1" id="question-heading">Question ${q.number}</span></div><div class="stem esat-content">${q.questionHtml}</div><div class="options" role="radiogroup" aria-labelledby="question-heading">${q.options.map(o=>`<button class="option ${a===o.label?'selected':''}" type="button" role="radio" aria-checked="${a===o.label}" data-action="select" data-label="${esc(o.label)}"><span class="radio" aria-hidden="true"></span><strong class="option-letter">${esc(o.label)}</strong><span class="option-content esat-content">${o.html}</span></button>`).join('')}</div><button class="clear-button" data-action="clear" ${!a?'disabled':''}>Clear response</button><button class="clear-button notes-toggle" data-action="notes">${notesVisible?'Hide':'Show'} private notes</button>${notesVisible?`<label class="notes-label">Private working notes<textarea id="question-notes" rows="4" placeholder="These notes are not included in your report.">${esc(s.notes[state.questionIndex])}</textarea></label>`:''}<p class="shortcuts">Alt+N / Alt+Shift+N: next · Alt+P / Alt+Shift+P: previous · Alt+F: flag · Alt+V: navigator · Alt+R: review</p></div>${submitDialog()}`;
  }
  function reviewMarkup() {
    const mi=state.moduleIndex,m=DATA.modules[mi],s=state.modules[mi],answered=s.answers.filter(Boolean).length,flags=s.flags.filter(Boolean).length;
    return `<div class="screen"><section class="welcome-card"><p class="eyebrow">Module ${mi+1} · ${esc(m.name)}</p><h1>Review your answers</h1><p class="subtitle">Your timer is still running. Select a question to revisit it before submitting this module.</p><div class="review-summary"><span>${answered} answered</span><span>${m.questions.length-answered} unanswered</span><span>${flags} flagged</span></div><div class="button-row"><button class="secondary" data-action="review-all">Review all</button><button class="secondary" data-action="review-unanswered" ${answered===m.questions.length?'disabled':''}>Review unanswered</button><button class="secondary" data-action="review-flagged" ${flags===0?'disabled':''}>Review flagged</button></div><div class="table-scroll"><table class="review-table"><thead><tr><th>Question</th><th>Your answer</th><th>Status</th><th>Review flag</th></tr></thead><tbody>${m.questions.map((q,i)=>`<tr><td><button data-action="goto" data-index="${i}">Question ${q.number}</button></td><td>${esc(s.answers[i]||'—')}</td><td>${s.answers[i]?'Answered':'Not answered'}</td><td class="flag-cell">${s.flags[i]?'⚑ Flagged':'—'}</td></tr>`).join('')}</tbody></table></div><div class="warning">${mi<2?'Submitting locks this module and immediately starts the 40-minute '+esc(DATA.modules[mi+1].name)+' timer. There is no break or score display.':'Submitting this module ends the test and opens your results and worked solutions.'}</div><div class="button-row"><button class="primary" data-action="submit-module">${mi<2?'Submit '+esc(m.name)+' & continue':'Submit final module & finish'}</button><button class="clear-button" data-action="abandon">End the whole attempt early</button></div></section></div>`;
  }
  function submitDialog() {
    const m=DATA.modules[state.moduleIndex],s=state.modules[state.moduleIndex],unanswered=s.answers.filter(a => !a).length,flagged=s.flags.filter(Boolean).length,last=state.moduleIndex===DATA.modules.length-1;
    return '<dialog id="submit-dialog" aria-labelledby="submit-title"><h2 id="submit-title">'+(last?'Finish your test?':'Submit '+esc(m.name)+'?')+'</h2><p><strong>'+unanswered+' unanswered</strong> · '+flagged+' flagged for review</p><p>This module will be locked. '+(last?'Your results and worked solutions will become available.':'The '+esc(DATA.modules[state.moduleIndex+1].name)+' timer starts immediately. You cannot come back to this module.')+'</p><div class="dialog-actions"><button class="btn secondary" data-action="cancel-submit">Keep working</button><button class="btn primary" data-action="confirm-submit">'+(last?'Submit test':'Submit & start next module')+'</button></div></dialog><dialog id="abandon-dialog"><h2>End the whole attempt early?</h2><p>All three modules will close. Your report will be marked incomplete and no practice score estimates will be shown.</p><div class="button-row"><button class="secondary" data-action="cancel-abandon">Keep working</button><button class="primary" data-action="confirm-abandon">End incomplete attempt</button></div></dialog>';
  }
  function results() {
    const r=report();
    return `<div class="screen"><section class="finish-card"><p class="eyebrow">Thriving Scholars · Results</p><h1>${r.incomplete?'Attempt ended early':'Test complete'}</h1><p class="subtitle">${esc(r.student.name)} · ${esc(DATA.pathway)}<br><span class="small-note">${esc(r.student.email)} · ${esc(r.submittedAt)}</span></p><div class="score-grid">${r.modules.map(m=>`<div class="score-box">${esc(m.name)}<strong>${m.rawScore} / ${m.questionCount}</strong><small>${m.questions.filter(q=>!q.selectedAnswer).length} unanswered · ${secondsText(m.elapsedSeconds)} used</small>${r.incomplete?'':`<small>Provisional TS practice score</small><strong class="module-estimate">${(m.provisionalScore==null?'Unavailable':m.provisionalScore.toFixed(1))} <span>/ 9.0</span></strong>`}</div>`).join('')}</div><div class="predictor-box"><div class="predictor-top"><div><h2>Total raw mark: ${r.totalScore} / ${totalQuestions}</h2><p>${r.incomplete?'Incomplete attempt — practice estimates are not shown.':'Separate provisional module scores · no overall scaled ESAT score'}</p></div></div><p class="small-note">${esc(r.scoreNote)}</p></div><div class="button-row"><button class="primary" data-action="solutions">Review worked solutions</button></div>${pdfLinks()}<div class="result-tabs" role="group" aria-label="Module analysis">${r.modules.map((m,i)=>`<button class="${i===resultsModule?'active':''}" data-action="result-module" data-index="${i}" aria-pressed="${i===resultsModule}">${esc(m.name)}</button>`).join('')}</div>${resultTable(resultsModule)}<p class="small-note">Question time is active viewing time across all visits. Module review and time away from the test are tracked separately. The countdown never pauses. Answer changes are timestamped when recorded.</p><section id="portal-attempt-status" aria-live="polite"></section><section class="report-actions"><h2>Your report</h2><div id="email-status">${deliveryMarkup()}</div><div class="button-row"><button class="secondary" data-action="download-json">Download report JSON</button><button class="secondary" data-action="download-csv">Download answers CSV</button><button class="secondary" data-action="download-html">Download HTML report</button></div><details class="email-area" id="email-details"><summary>Preview full score report</summary><iframe id="email-preview" class="email-preview" title="Full score report preview" sandbox=""></iframe></details></section><div class="button-row"><button class="secondary" data-action="restart">Start a new attempt</button><a class="secondary link-button" href="/esat?view=tests">Return to ESAT practice tests</a></div></section></div><dialog id="restart-dialog" aria-labelledby="restart-title"><h2 id="restart-title">Start a new attempt?</h2><p>Your current saved answers and report will be replaced. Download the report before continuing.</p><div class="button-row"><button class="secondary" data-action="cancel-restart">Keep these results</button><button class="primary" data-action="confirm-restart">Start again</button></div></dialog>`;
  }
  function resultTable(mi) {
    const m=report().modules[mi];
    return `<h2 class="analysis-heading">${esc(m.name)} · question analysis</h2><div class="table-scroll"><table class="result-table"><thead><tr><th>Question</th><th>Your answer</th><th>Correct answer</th><th>Time</th><th>Flagged</th><th>Status</th></tr></thead><tbody>${m.questions.map((q,i)=>`<tr><td><button data-action="open-solution" data-index="${i}">${q.number}</button></td><td>${esc(q.selectedAnswer?q.selectedAnswer+' — '+q.selectedAnswerText:'Unanswered')}</td><td>${esc(q.correctAnswer+' — '+q.correctAnswerText)}</td><td>${secondsText(q.timeSpentSeconds)}</td><td>${q.flagged?'⚑ Yes':'—'}</td><td class="${q.correct?'status-good':q.selectedAnswer?'status-bad':''}">${q.correct?'Correct':q.selectedAnswer?'Incorrect':'Unanswered'}</td></tr>`).join('')}</tbody></table></div>`;
  }
  function pdfLinks() {
    if(!CFG.solutionPdfUrl || !/^https:\/\//i.test(CFG.solutionPdfUrl))return '';
    return `<details class="pdf-area" id="solution-pdf"><summary>View the complete ${esc(DATA.pathway)} solution book (PDF)</summary><iframe class="pdf-preview" data-pdf-url="${esc(CFG.solutionPdfUrl)}" title="${esc(DATA.pathway)} solution book"></iframe><a class="pdf-open-link" href="${esc(CFG.solutionPdfUrl)}" target="_blank" rel="noopener noreferrer">Open solution book in a new tab</a></details>`;
  }
  function solutionMarkup(mi) {
    const m=DATA.modules[mi],s=state.modules[mi],i=solutionQuestion,q=m.questions[i],answer=s.answers[i];
    return `<div class="question-wrap"><div class="question-meta"><div class="section-name">Worked solutions · ${esc(m.name)}</div><div class="review-paper-pick"><label for="solution-module">Module</label><select id="solution-module">${DATA.modules.map((v,j)=>`<option value="${j}" ${j===mi?'selected':''}>${esc(v.name)}</option>`).join('')}</select><label for="solution-question">Question</label><select id="solution-question">${m.questions.map((v,j)=>`<option value="${j}" ${j===i?'selected':''}>${v.number}</option>`).join('')}</select></div></div><div class="question-topline"><span class="module-chip">M${mi+1}</span><span class="question-number">Question ${q.number}</span><span class="badge">${answer===q.correctAnswer?'Correct':answer?'Incorrect':'Not answered'}</span></div><div class="stem esat-content">${q.questionHtml}</div><div class="options">${q.options.map(o=>`<div class="option ${o.label===q.correctAnswer?'correct':o.label===answer?'wrong':''}"><strong class="option-letter">${esc(o.label)}</strong><span class="option-content esat-content">${o.html}</span>${o.label===q.correctAnswer?'<span class="option-status">Correct answer</span>':o.label===answer?'<span class="option-status">Your answer</span>':''}</div>`).join('')}</div><div class="solution-panel esat-content"><h2>Worked solution</h2>${q.solutionHtml}<div class="metadata">${[q.topic,q.subtopic,q.difficulty?'Difficulty '+q.difficulty+'/5':'',...(q.tags||[])].filter(Boolean).map(t=>`<span>${esc(t)}</span>`).join('')}</div></div></div>`;
  }
  function footer() {
    if(resumePending)return '<footer class="exam-footer"><span class="footer-brand">Thriving Scholars · ESAT Practice Test 2026</span></footer>';
    if(state.status==='running')return `<footer class="exam-footer"><div class="footer-left"><button class="footer-button" data-action="${state.view==='review'?'return-question':'review'}">${state.view==='review'?'← Back to question':'Review module'}</button></div><div class="footer-right">${state.view==='question'?`<button class="footer-button" data-action="prev" ${state.questionIndex===0?'disabled':''}>← Previous</button>`:''}<button class="footer-button" data-action="navigator" aria-expanded="${navOpen}" aria-controls="navigator">Navigator</button>${state.view==='question'?`<button class="footer-button next" data-action="next">${state.questionIndex===26?'Review module':'Next →'}</button>`:''}</div></footer>`;
    if(state.status==='complete'&&solutionsVisible)return `<footer class="exam-footer"><div class="footer-left"><button class="footer-button" data-action="back-results">← Results</button></div><div class="footer-right"><button class="footer-button" data-action="solution-prev" ${resultsModule===0&&solutionQuestion===0?'disabled':''}>← Previous</button><button class="footer-button next" data-action="solution-next" ${resultsModule===2&&solutionQuestion===26?'disabled':''}>Next →</button></div></footer>`;
    return '<footer class="exam-footer"><div class="footer-left"><span class="footer-brand">Thriving Scholars · ESAT Practice Test 2026</span></div></footer>';
  }

  function navigatorMarkup() {
    if(!navOpen||state.status!=='running')return '';
    const m=DATA.modules[state.moduleIndex],s=state.modules[state.moduleIndex];
    return `<section id="navigator" class="navigator open" aria-label="Module navigator"><div class="nav-top"><h3>${esc(m.name)} navigator</h3><button data-action="navigator" aria-label="Close navigator">×</button></div><div class="nav-grid">${m.questions.map((q,i)=>`<button class="nav-number ${s.answers[i]?'answered ':''}${s.flags[i]?'flagged ':''}${i===state.questionIndex?'current':''}" data-action="goto" data-index="${i}" aria-label="Question ${q.number}, ${s.answers[i]?'answered':'unanswered'}${s.flags[i]?', flagged':''}">${q.number}${s.flags[i]?' ⚑':''}</button>`).join('')}</div><div class="nav-note">Green = answered · gold outline / ⚑ = flagged · blue = current.<br>Only the current module can be opened.</div></section>`;
  }
  function resumeMarkup() {
    return `<div class="screen"><section class="welcome-card"><p class="eyebrow">Thriving Scholars · Digital practice</p><h1>ESAT Practice Test 2026</h1><p class="subtitle">${esc(DATA.pathway)}</p><div class="resume-box"><p><strong>${state.status==='running'?'An attempt is in progress.':'A completed attempt is saved.'}</strong> ${state.status==='running'?'Its clock continues while this page is closed or while you are on this screen.':'You can reopen the full report and worked solutions.'}</p><p class="small-note">${esc(state.student.name)} · ${esc(state.student.email)}</p><button class="primary" data-action="resume">${state.status==='running'?'Resume attempt':'Open saved results'}</button><button class="clear-button" data-action="clear-saved">Clear saved attempt</button></div><table class="format-table"><thead><tr><th>Module</th><th>Questions</th><th>Time</th></tr></thead><tbody>${DATA.modules.map(m=>`<tr><td>${esc(m.name)}</td><td>27</td><td>40 min</td></tr>`).join('')}</tbody></table><p class="small-note">Progress is stored in this browser. Submitted modules remain locked.</p></section></div><dialog id="clear-saved-dialog"><h2>Clear saved attempt?</h2><p>The saved answers, report and candidate details for this attempt will be removed from this browser.</p><div class="button-row"><button class="secondary" data-action="cancel-clear-saved">Keep saved attempt</button><button class="primary" data-action="confirm-clear-saved">Clear attempt</button></div></dialog>`;
  }
  function render() {
    document.body.className=(prefs.scheme==='standard'?'':prefs.scheme)+(prefs.large?' large-text':'');
    app.innerHTML='<div class="app-shell">'+toolbar()+'<main class="exam-main" id="main-content">'+banner()+(resumePending?resumeMarkup():state.status==='ready'?instructions():state.status==='running'?running():solutionsVisible?solutionMarkup(resultsModule):results())+'</main>'+footer()+navigatorMarkup()+'</div>';
    updateTimer();
    const pdf=document.getElementById('solution-pdf');if(pdf)pdf.addEventListener('toggle',()=>{if(pdf.open){const f=pdf.querySelector('iframe');if(f&&!f.getAttribute('src'))f.setAttribute('src',f.getAttribute('data-pdf-url')+'#toolbar=0&navpanes=0&view=FitH');}});
    const preview=document.getElementById('email-details');if(preview)preview.addEventListener('toggle',()=>{if(preview.open)document.getElementById('email-preview').srcdoc=reportHTML();});
    if(!resumePending && state.status==='complete' && window.TS_ESAT_PORTAL) window.TS_ESAT_PORTAL.onComplete(report());
    if(!resumePending && state.status==='complete' && state.delivery.status==='not-sent' && CFG.autoEmail !== false && emailConfigured() && state.student.email) sendReport();
  }
  function updateTimer() {
    const timer=document.getElementById('timer'); if(!timer || state.status!=='running') return;
    const remaining=Math.max(0,state.modules[state.moduleIndex].deadline-Date.now());
    timer.textContent=timerHidden?'Timer hidden':msText(Math.ceil(remaining/1000)*1000);
    timer.classList.toggle('urgent',remaining<=300000); document.getElementById('timeBox')?.classList.toggle('urgent',remaining<=300000);
    timer.setAttribute('aria-label',timerHidden?'Timer hidden':msText(Math.ceil(remaining/1000)*1000)+' remaining');
  }
  function moveTo(index,view='question') {
    if(state.status!=='running') return;
    if(sync()) { render(); return; }
    navOpen=false; state.questionIndex=Math.max(0,Math.min(DATA.modules[state.moduleIndex].questions.length-1,index)); state.view=view; resetClock(Date.now()); save(); render();
    document.getElementById('question-heading')?.focus({preventScroll:true});
    window.scrollTo({top:0,behavior:'instant'});
  }
  function choose(label) {
    if(state.status!=='running' || state.view!=='question') return;
    if(sync()) { render(); return; }
    const q=DATA.modules[state.moduleIndex].questions[state.questionIndex];
    if(label !== null && !q.options.some(o => o.label===label)) return;
    const m=state.modules[state.moduleIndex]; if(m.answers[state.questionIndex]!==label){m.answers[state.questionIndex]=label;(m.answerUpdatedAt ||= m.answers.map(()=>null))[state.questionIndex]=Date.now();} save(); render();
  }
  async function fullscreen() {
    try { if(document.fullscreenElement) await document.exitFullscreen(); else await document.documentElement.requestFullscreen(); render(); }
    catch (_) { notice='Fullscreen is unavailable in this browser. You can continue in the current window.'; render(); }
  }
  app.addEventListener('submit',e => {
    if(e.target.id==='start-form') { e.preventDefault(); const fields=new FormData(e.target); candidateDraft={name:String(fields.get('studentName')||'').trim(),email:String(fields.get('studentEmail')||'').trim(),session:String(fields.get('studentSession')||'Practice sitting')}; render(); window.scrollTo({top:0,behavior:'instant'}); }
  });
  app.addEventListener('input',e => {
    if(e.target.id==='question-notes' && state.status==='running') { state.modules[state.moduleIndex].notes[state.questionIndex]=e.target.value; save(); }
  });
  app.addEventListener('change',e=>{if(e.target.id==='scheme-select'){prefs.scheme=e.target.value;savePrefs();render();return;}if(e.target.id==='solution-module'&&state.status==='complete'){resultsModule=Number(e.target.value);solutionQuestion=0;render();return;}if(e.target.id==='solution-question'&&state.status==='complete'){solutionQuestion=Number(e.target.value);render();}});
  app.addEventListener('click',e => {
    const button=e.target.closest('[data-action]'); if(!button || button.disabled) return;
    const action=button.dataset.action;
    if(action==='resume'){resumePending=false;if(state.status==='running')sync();render();return;}
    if(action==='clear-saved'){document.getElementById('clear-saved-dialog').showModal();return;}
    if(action==='cancel-clear-saved'){document.getElementById('clear-saved-dialog').close();return;}
    if(action==='confirm-clear-saved'){resumePending=false;state=fresh();candidateDraft=null;notice='';save();render();return;}
    if(resumePending&&!['fullscreen','text-size'].includes(action))return;
    if(state.status==='running' && sync()) { render(); return; }
    if(action==='fullscreen') { fullscreen(); return; }
    if(action==='timer') { timerHidden=!timerHidden; prefs.hideTimer=timerHidden;savePrefs();render();return; }
    if(action==='text-size'){prefs.large=!prefs.large;savePrefs();render();return;}
    if(action==='back-welcome'){candidateDraft=null;render();return;}
    if(action==='begin'&&state.status==='ready'&&candidateDraft){start(candidateDraft.name,candidateDraft.email,candidateDraft.session);return;}
    if(action==='navigator'&&state.status==='running'){navOpen=!navOpen;render();return;}
    if(action==='review-all'){moveTo(0);return;}
    if(action==='review-unanswered'){moveTo(state.modules[state.moduleIndex].answers.findIndex(a=>!a));return;}
    if(action==='review-flagged'){moveTo(state.modules[state.moduleIndex].flags.findIndex(Boolean));return;}
    if(action==='abandon'){document.getElementById('abandon-dialog').showModal();return;}
    if(action==='cancel-abandon'){document.getElementById('abandon-dialog').close();return;}
    if(action==='confirm-abandon'&&state.status==='running'){const now=Date.now();accrue(now);state.incomplete=true;while(state.status==='running')finishModule(now,'ended-early');navOpen=false;save();render();return;}
    if(action==='select') { choose(button.dataset.label); return; }
    if(action==='clear') { choose(null); return; }
    if(action==='prev') { moveTo(state.questionIndex-1); return; }
    if(action==='next') { const last=state.questionIndex===DATA.modules[state.moduleIndex].questions.length-1; moveTo(last?state.questionIndex:state.questionIndex+1,last?'review':'question'); return; }
    if(action==='review') { moveTo(state.questionIndex,'review'); return; }
    if(action==='return-question') { moveTo(state.questionIndex); return; }
    if(action==='goto') { moveTo(Number(button.dataset.index)); return; }
    if(action==='flag' && state.status==='running') { const m=state.modules[state.moduleIndex]; m.flags[state.questionIndex]=!m.flags[state.questionIndex]; save(); render(); return; }
    if(action==='notes') { notesVisible=!notesVisible; render(); return; }
    if(action==='submit-module') { document.getElementById('submit-dialog').showModal(); return; }
    if(action==='cancel-submit') { document.getElementById('submit-dialog').close(); return; }
    if(action==='confirm-submit' && state.status==='running') { const now=Date.now();navOpen=false; accrue(now); finishModule(now,'submitted'); if(state.status==='running') state.clock.attention=isAttentive(); notice=''; save(); render(); window.scrollTo({top:0,behavior:'instant'}); return; }
    if(state.status!=='complete') return;
    if(action==='back-results'){solutionsVisible=false;render();return;}
    if(action==='open-solution'){solutionsVisible=true;solutionQuestion=Number(button.dataset.index);render();window.scrollTo({top:0,behavior:'instant'});return;}
    if(action==='result-module') { resultsModule=Number(button.dataset.index); solutionQuestion=0; render(); return; }
    if(action==='solution-prev'||action==='solution-next') {const next=Math.max(0,Math.min(totalQuestions-1,resultsModule*27+solutionQuestion+(action==='solution-prev'?-1:1)));resultsModule=Math.floor(next/27);solutionQuestion=next%27;render();window.scrollTo({top:0,behavior:'instant'});return;}
    if(action==='solutions') { solutionsVisible=!solutionsVisible; render(); return; }
    if(action==='download-html') { download(reportHTML(),'text/html;charset=utf-8','score_report.html'); return; }
    if(action==='download-csv') { download(csv(),'text/csv;charset=utf-8','question_report.csv'); return; }
    if(action==='download-json') { download(JSON.stringify(report(),null,2),'application/json','score_report.json'); return; }
    if(action==='email') { sendReport(true); return; }
    if(action==='restart') { document.getElementById('restart-dialog').showModal(); return; }
    if(action==='cancel-restart') { document.getElementById('restart-dialog').close(); return; }
    if(action==='confirm-restart') { state=fresh(); solutionsVisible=false; resultsModule=0; notice=''; save(); render(); window.scrollTo({top:0,behavior:'instant'}); }
  });
  document.addEventListener('keydown',e => {
    if(resumePending)return;
    if(e.repeat || e.ctrlKey || e.metaKey || e.target.closest('input,textarea,select,[contenteditable="true"]') || document.querySelector('dialog[open]')) return;
    if(e.key==='Escape'&&navOpen){e.preventDefault();navOpen=false;render();return;}
    const k=e.key.toLowerCase();
    if(state.status==='complete' && solutionsVisible && e.altKey && (k==='n'||k==='p')) {
      e.preventDefault();const next=Math.max(0,Math.min(totalQuestions-1,resultsModule*27+solutionQuestion+(k==='n'?1:-1)));resultsModule=Math.floor(next/27);solutionQuestion=next%27;render();return;
    }
    if(state.status!=='running')return;
    if(k==='escape'&&state.view==='review'){e.preventDefault();moveTo(state.questionIndex);return;}
    if(e.altKey && ['n','p','f','r','v'].includes(k)) {
      e.preventDefault();
      if(k==='n') { const last=state.questionIndex===DATA.modules[state.moduleIndex].questions.length-1; moveTo(last?state.questionIndex:state.questionIndex+1,last?'review':'question'); }
      if(k==='p') moveTo(state.questionIndex-1);
      if(k==='v'){navOpen=!navOpen;render();}
      if(k==='r') moveTo(state.questionIndex,state.view==='review'?'question':'review');
      if(k==='f' && state.view==='question') { if(sync()) { render(); return; } const m=state.modules[state.moduleIndex]; m.flags[state.questionIndex]=!m.flags[state.questionIndex]; save(); render(); }
    } else if(!e.altKey && !e.shiftKey && /^[a-h]$/.test(k) && state.view==='question') { e.preventDefault(); choose(k.toUpperCase()); }
  });
  document.addEventListener('visibilitychange',() => {
    if(state.status!=='running') return;
    const advanced=sync();
    if(state.clock) state.clock.attention=isAttentive(); save(); if(advanced) render();
  });
  window.addEventListener('blur',()=>{if(state.status==='running'){const advanced=sync();if(state.clock)state.clock.attention=false;save();if(advanced)render();}});
  window.addEventListener('focus',()=>{if(state.status==='running'){const advanced=sync();save();if(advanced)render();}});
  window.addEventListener('pagehide',() => { if(state.status==='running') { accrue(Date.now()); if(state.clock) state.clock.attention=false; save(); } });
  window.addEventListener('pageshow',e => { if(e.persisted && state.status==='running') { sync(Date.now(),true); render(); } });
  window.addEventListener('beforeunload',() => { if(state.status==='running') { accrue(Date.now()); if(state.clock) state.clock.attention=false; save(); } });
  if(state.status==='running') { sync(Date.now(),true); notice=state.status==='running'?'Your saved attempt has resumed. The module clock continued while you were away.':'Your saved test has been submitted because the module timers expired.'; }
  render();
  setInterval(() => { if(state.status==='running') { if(sync()) render(); else updateTimer(); } },500);
  window.ESATRuntime=Object.freeze({getState:() => JSON.parse(JSON.stringify(state)),getReport:report,getReportHTML:reportHTML,scoreFor,storageKey:KEY,anchors:JSON.parse(JSON.stringify(ANCHORS))});
})();
