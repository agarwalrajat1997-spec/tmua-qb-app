'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { ArrowLeft, ArrowRight, BookOpen, Bookmark, ChevronLeft, Lightbulb, Sparkles, X } from 'lucide-react';
import { MathHtml, MathText } from '@/src/tmua-studio/components/MathHtml';
import { skillName, type Guide } from '@/src/tmua-studio/lib/audited-content';
import { studentMethods } from '@/src/tmua-studio/lib/student-content';
import type { Question, StoredSolution } from '@/src/tmua-studio/types';
import { loadProgress, saveQuestionProgress, sortQuestions, type BankQuestion, type QuestionProgress } from '@/lib/tmua-bank-client';
import { supabaseBrowser } from '@/utils/supabase/browser';
import PastPaperPracticeLink from '../components/PastPaperPracticeLink';
import './bank.css';

type Detail = { question: Question; guide: Guide; viewerId: string };
const PAGE_SIZE = 15;
const cleanTopic = (s: string | null | undefined) => String(s || 'General practice').replace(/^\s*\d+[._\-):\s]+/, '').replaceAll('_',' ').replaceAll('&amp;','&').replaceAll('â€”','—').replaceAll('â€“','–');
async function studio<T>(action: string, q?: BankQuestion, viewerId?: string): Promise<T> {
  const params = new URLSearchParams({ action });
  if (viewerId) params.set('expectedUserId',viewerId);
  if (q) { params.set('qid', q.qid); params.set('contentVersion', q.content_version); }
  const res = await fetch(`/api/tmua/studio?${params}`, { cache: 'no-store' });
  const result = await res.json();
  if (!res.ok) throw Error(result.error || 'This question could not be loaded. Please retry.');
  return result as T;
}

function Level({ value }: { value: number }) {
  return <span className={`difficulty ${value <= 2 ? 'easy' : value === 3 ? 'medium' : 'hard'}`}><span className="difficulty-bars" aria-hidden="true">{[1,2,3,4,5].map(n => <i key={n} className={n <= value ? 'on' : ''} style={{height: 3+n*2}} />)}</span>Level {value}</span>;
}
function stateLabel(p?: QuestionProgress) {
  if (p?.status === 'correct') return 'Correct';
  if (p?.status === 'wrong' || p?.status === 'incorrect') return 'Needs review';
  if (hasAttempt(p)) return 'Attempted';
  return 'Not attempted';
}
function hasAttempt(p?: QuestionProgress) {
  return !!p?.selected_answer || ['correct','wrong','incorrect','answered','attempted'].includes(p?.status || '');
}

function BankLoading() {
  return <section className="bank-loading" role="status" aria-live="polite">
    <video className="bank-loading-mascot" autoPlay loop muted playsInline aria-hidden="true" poster="/tmua-studio/brand/thinking.png"><source src="/tmua-studio/brand/thinking.webm" type="video/webm"/><source src="/tmua-studio/brand/thinking.mp4" type="video/mp4"/></video>
    <span className="bank-loading-spinner" aria-hidden="true"/>
    <h1>Getting your question bank ready</h1>
    <p>Loading your questions and saved progress…</p>
  </section>;
}

function QuestionCard({ q, index, viewerId, state, onSave, onSolution, onStudio, getDetail }: {
  q: BankQuestion; index: number; viewerId: string; state?: QuestionProgress;
  onSave: (q: BankQuestion, patch: Partial<QuestionProgress>) => void;
  onSolution: (q: BankQuestion) => void; onStudio: (q: BankQuestion) => void;
  getDetail: (q: BankQuestion) => Promise<Detail>;
}) {
  const [detail, setDetail] = useState<Detail>();
  const [error, setError] = useState('');
  const [selection, setSelection] = useState('');
  const [checked, setChecked] = useState<{ correct: boolean; answer: string }>();
  const [busy, setBusy] = useState(false);
  const [hints, setHints] = useState(0);
  const elapsed = useRef(0);
  const activeSince = useRef<number | null>(null);
  const container = useRef<HTMLElement>(null);
  const load = useCallback(() => { setError(''); void getDetail(q).then(setDetail).catch(e => setError(e.message)); }, [getDetail,q]);
  useEffect(() => {
    const node = container.current; if (!node) return;
    const observer = new IntersectionObserver(entries => {
      if (entries.some(x => x.isIntersecting)) { load(); observer.disconnect(); }
    }, { rootMargin: '500px' });
    observer.observe(node); return () => observer.disconnect();
  }, [load]);
  useEffect(() => {
    const update = () => {
      const now = Date.now();
      if (activeSince.current !== null) elapsed.current += now - activeSince.current;
      activeSince.current = !document.hidden && document.hasFocus() && container.current?.classList.contains('is-in-focus') && !document.querySelector('.tmua-bank-root dialog[open]') ? now : null;
    };
    window.addEventListener('ts-bank-focus', update);
    window.addEventListener('focus', update);
    window.addEventListener('blur', update);
    document.addEventListener('visibilitychange', update);
    return () => {window.removeEventListener('ts-bank-focus', update);window.removeEventListener('focus', update);window.removeEventListener('blur', update);document.removeEventListener('visibilitychange', update);};
  }, []);
  async function check() {
    if (!selection || busy) return;
    const answerSeconds = Math.max(0, Math.round((elapsed.current + (activeSince.current === null ? 0 : Date.now()-activeSince.current))/1000));
    setBusy(true); setError('');
    try {
      const res = await fetch('/api/tmua/studio?action=answers', {method:'POST', headers:{'Content-Type':'application/json','X-TS-Studio':'1'}, body:JSON.stringify({expectedUserId:viewerId,exam:'tmua', qid:q.qid, answer:selection, contentVersion:q.content_version})});
      const result = await res.json();
      if (!res.ok) throw Error(result.error || 'Answer check unavailable. Your selection is kept.');
      setChecked(result);
      onSave(q, { selected_answer:selection, status:result.correct ? 'correct' : 'wrong', submission_id:`tmua-stable-v1|${q.display_order}|${crypto.randomUUID()}`, answer_elapsed_seconds:answerSeconds, answer_submitted_at:new Date().toISOString() });
    } catch(e) { setError(e instanceof Error ? e.message : 'Please try again.'); }
    finally { setBusy(false); }
  }
  const longOptions = detail?.question.options.some(o => o.html.replace(/<[^>]*>/g,'').length > 70);
  return <article ref={container} className="question-card" id={`question-${q.qid}`} data-question={q.qid} aria-labelledby={`title-${q.qid}`} tabIndex={-1}>
    <div className="question-layout"><div className="question-content">
      <div className="question-top"><div><h2 className="question-number" id={`title-${q.qid}`}>Question {index}</h2><div className="question-ref">{cleanTopic(q.subtopic)}</div></div><Level value={q.difficulty}/></div>
      {detail ? <><MathHtml html={detail.question.prompt_html} className="question-stem"/>
        <div className={`options-grid ${longOptions ? 'long-options' : ''}`} role="group" aria-label={`Answer options for question ${index}`}>
          {detail.question.options.map(o => <button key={o.label} className={`answer-option ${selection===o.label?'selected':''} ${checked && o.label===checked.answer?'correct':''} ${checked && selection===o.label && !checked.correct?'incorrect':''}`} aria-pressed={selection===o.label} disabled={!!checked || busy} onClick={() => setSelection(o.label)}><span className="answer-letter">{o.label}</span><MathHtml html={o.html} className="option-value" inline/></button>)}
        </div>
        {hints>0 && <div className="hint-box"><div className="hint-label"><Lightbulb className="icon small"/>Hint · {hints} / {detail.guide.enrichment.hints.length}</div>{detail.guide.enrichment.hints.slice(0,hints).map(h => <MathText key={h.hint_id} text={h.text} inline={false}/>)}{hints<detail.guide.enrichment.hints.length && <button className="text-link" onClick={() => setHints(n=>n+1)}>A little more help <ArrowRight className="icon small"/></button>}</div>}
        <div className="check-row"><button className="btn primary" disabled={!selection || busy} onClick={() => { if(checked){setChecked(undefined);setSelection('');elapsed.current=0;if(activeSince.current!==null)activeSince.current=Date.now();} else void check(); }}>{busy?'Checking…':checked?'Try again':'Check answer'}</button><p className="check-message" role="status">{checked ? checked.correct ? 'Correct — well done.' : 'That answer needs another look. Try a hint or open the solution.' : state?.selected_answer ? `Previous attempt: ${state.selected_answer} · ${stateLabel(state)}` : ''}</p></div>
      </> : <div className="question-loading" role="status">{error ? <><p>{error}</p><button className="btn" onClick={load}>Retry</button></> : 'Loading question…'}</div>}
      {detail && error && <p className="bank-error" role="alert">{error}</p>}
    </div><aside className="question-tools" aria-label={`Tools for question ${index}`}>
      <div className="tools-top"><span className={`pill ${state?.status==='correct'?'green':state?.status==='wrong'?'warning':'grey'}`}>{stateLabel(state)}</span><button className={`icon-btn ${state?.flagged?'saved':''}`} aria-label={state?.flagged?'Unsave question':'Save question'} aria-pressed={!!state?.flagged} onClick={() => onSave(q,{flagged:!state?.flagged})}><Bookmark className="icon small"/></button></div>
      <button className="tool-button solution-button" onClick={() => onSolution(q)}><BookOpen className="icon"/>Solution</button>
      <button className="tool-button ai-button" onClick={() => onStudio(q)}><Sparkles className="icon"/>AI feedback</button>
      <button className="tool-button hint-button" disabled={!detail} aria-expanded={hints>0} onClick={() => setHints(n=>n?0:1)}><Lightbulb className="icon"/>Hint</button>
    </aside></div>
  </article>;
}

function Solution({ q, detail, result }: {q:BankQuestion; detail:Detail; result:StoredSolution}) {
  const [collapsed,setCollapsed] = useState(false);
  const g = detail.guide;
  const useful = studentMethods(g.enrichment.shortcut_assessments);
  return <div className={`solution-interior ${collapsed?'is-question-collapsed':''}`}>
    <div className="solution-workspace">
      <section className="solution-question-pane" aria-label="Question" hidden={collapsed} tabIndex={0}><header className="solution-question-heading"><h3>Question</h3><Level value={q.difficulty}/></header><MathHtml html={detail.question.prompt_html} className="solution-question-stem"/>
        <div className="solution-question-options">{detail.question.options.map(o=><div key={o.label} className={`solution-question-option ${o.label===result.answer?'is-correct':''}`}><span className="option-letter">{o.label}</span><MathHtml html={o.html} inline className="option-value"/></div>)}</div>
      </section>
      <div className="solution-divider"><button id="solutionCollapseButton" aria-expanded={!collapsed} aria-label={collapsed?'Expand question pane':'Collapse question pane'} onClick={()=>setCollapsed(!collapsed)}><ChevronLeft className="icon"/></button></div>
      <section className="solution-answer-pane" aria-label="Worked solution" tabIndex={0}><div id="solutionAnswerContent"><div className="solution-header"><h3>Worked solution</h3><span className="pill green">Answer {result.answer}</span></div>
        <MathHtml html={result.solutionHtml} className="solution-answer"/>
        {g.enrichment.solution_steps.length>0 && <details className="audit-details"><summary>Step-by-step reasoning</summary><ol className="solution-steps">{g.enrichment.solution_steps.map(s=><li key={s.step_id}><div><MathText text={s.explanation} inline={false}/>{s.check && <p className="step-check"><MathText text={s.check}/></p>}</div></li>)}</ol></details>}
        {useful.map(s=><div className="shortcut-box" key={s.id}><p className="eyebrow">{s.label}</p><h4>{s.title}</h4><MathText text={s.explanation} inline={false}/>{s.conditions.length>0 && <div className="shortcut-condition"><b>When it works</b>{s.conditions.map((c,i)=><MathText key={i} text={c} inline={false}/>)}</div>}{s.limitations.length>0 && <div className="shortcut-condition"><b>Take care</b>{s.limitations.map((c,i)=><MathText key={i} text={c} inline={false}/>)}</div>}</div>)}
        {g.enrichment.error_hypotheses.length>0 && <div className="trap-box"><b>Common mistakes to watch for</b>{g.enrichment.error_hypotheses.map(e=><MathText key={e.error_id} text={e.description} inline={false}/>)}</div>}
        <div className="solution-footer"><div className="skill-tags" aria-label="Skills practised">{g.enrichment.skills.map(s=><span key={s.skill_id}>{skillName(g,s.skill_id)}</span>)}</div></div>
      </div></section>
    </div>
  </div>;
}

export default function QuestionBank({embedded=false}:{embedded?:boolean}) {
  const [questions,setQuestions] = useState<BankQuestion[]>([]);
  const [viewer,setViewer] = useState('');
  const [error,setError] = useState('');
  const [loading,setLoading] = useState(true);
  const [retry,setRetry] = useState(0);
  const [progress,setProgress] = useState<Record<string,QuestionProgress>>({});
  const currentProgress = useRef(progress);
  const [sync,setSync] = useState('');
  const [topic,setTopic] = useState('');
  const [subtopic,setSubtopic] = useState('all');
  const [difficulty,setDifficulty] = useState('all');
  const [status,setStatus] = useState('all');
  const [search,setSearch] = useState('');
  const [page,setPage] = useState(0);
  const [solution,setSolution] = useState<{q:BankQuestion;detail:Detail;result:StoredSolution}>();
  const [solutionError,setSolutionError] = useState('');
  const [solutionQ,setSolutionQ] = useState<BankQuestion>();
  const solutionDialog = useRef<HTMLDialogElement>(null);
  const [studioQ,setStudioQ] = useState<BankQuestion>();
  const initialStudioQ = useRef<string>('');
  const studioOpenId = useRef('');
  const studioDialog = useRef<HTMLDialogElement>(null);
  const frame = useRef<HTMLIFrameElement>(null);
  const solutionGeneration = useRef(0);
  const viewerRef = useRef('');
  const studioSubmissions = useRef(new Set<string>());
  const cache = useRef(new Map<string,Promise<Detail>>());
  const getDetail = useCallback((q:BankQuestion) => {
    const key = `${viewerRef.current}:${q.qid}@${q.content_version}`;
    let value = cache.current.get(key);
    if (!value) { value = studio<Detail>('question',q,viewerRef.current).catch(e=>{cache.current.delete(key);throw e;});cache.current.set(key,value); }
    return value;
  },[]);
  useEffect(()=>{
    let active=true;
    setLoading(true);setError('');
    void studio<{viewerId:string;questions:BankQuestion[]}>('catalogue').then(async data=>{
      if(!active)return;
      const sorted=sortQuestions(data.questions.map(q=>({...q,subtopic:q.subtopic||'General practice'})));
      viewerRef.current=data.viewerId;setViewer(data.viewerId);setQuestions(sorted);
      const restored=await loadProgress(data.viewerId,sorted);
      if(!active)return;
      setProgress(restored.progress);currentProgress.current=restored.progress;
      setSync(restored.warnings.join(' ') || (restored.syncState==='offline'?'Saved work is on this device; account sync is pending.':''));
    }).catch(e=>active&&setError(e.message)).finally(()=>active&&setLoading(false));
    return()=>{active=false;};
  },[retry]);
  useEffect(()=>{setPage(0);},[topic,subtopic,difficulty,status,search]);
  useEffect(()=>{
    function receive(event:MessageEvent){
      if(event.origin!==location.origin || event.source!==frame.current?.contentWindow)return;
      if(event.data?.type==='ts-studio-answer') {
        const data=event.data;
        const q=questions.find(q=>q.qid===data.qid && q.content_version===data.contentVersion);
        if(q && typeof data.selected==='string' && typeof data.correct==='boolean' && typeof data.submissionId==='string' && !studioSubmissions.current.has(data.submissionId)) {
          studioSubmissions.current.add(data.submissionId);
          save(q,{selected_answer:data.selected,status:data.correct?'correct':'wrong',submission_id:`tmua-stable-v1|${q.display_order}|${data.submissionId}`,answer_elapsed_seconds:typeof data.answerElapsedSeconds==='number'?data.answerElapsedSeconds:null,answer_submitted_at:new Date().toISOString()});
        }
      }
      if(event.data?.type==='ts-studio-question') {const q=questions.find(q=>q.qid===event.data.qid);if(q)setStudioQ(q);}
      if(event.data?.type==='ts-studio-close') studioDialog.current?.close();
      if(event.data?.type==='ts-studio-ready' && studioQ) frame.current?.contentWindow?.postMessage({type:'ts-studio-open',qid:studioQ.qid,openId:studioOpenId.current},location.origin);
    }
    window.addEventListener('message',receive);return()=>window.removeEventListener('message',receive);
  },[studioQ,viewer,questions,loading]);
  useEffect(()=>{
    const update=()=>{
      const cards=[...document.querySelectorAll<HTMLElement>('.tmua-bank-root .question-card')];
      let current:HTMLElement|undefined;let most=0;
      const top=document.querySelector('.tmua-bank-root .filter-panel')?.getBoundingClientRect().bottom ?? 64;
      for(const card of cards){const r=card.getBoundingClientRect();const shown=Math.max(0,Math.min(innerHeight,r.bottom)-Math.max(top,r.top));if(shown>most){most=shown;current=card;}}
      cards.forEach(c=>c.classList.toggle('is-in-focus',c===current));
      window.dispatchEvent(new Event('ts-bank-focus'));
    };
    let raf=0;const request=()=>{cancelAnimationFrame(raf);raf=requestAnimationFrame(update);};
    const observer=new ResizeObserver(request);document.querySelectorAll('.tmua-bank-root .question-card').forEach(c=>observer.observe(c));
    window.addEventListener('scroll',request,true);window.addEventListener('resize',request);request();
    return()=>{observer.disconnect();cancelAnimationFrame(raf);window.removeEventListener('scroll',request,true);window.removeEventListener('resize',request);};
  },[questions,topic,subtopic,difficulty,status,search,page]);
  const topics=useMemo(()=>[...new Set(questions.map(q=>q.topic))],[questions]);
  const filtered=useMemo(()=>questions.filter(q=>{
    const p=progress[q.qid];
    return (!topic||topic==='all'||q.topic===topic) && (subtopic==='all'||q.subtopic===subtopic) && (difficulty==='all'||q.difficulty===Number(difficulty)) && (status==='all'||status==='saved'&&p?.flagged||status==='correct'&&p?.status==='correct'||status==='review'&&['wrong','incorrect'].includes(p?.status||'')||status==='attempted'&&hasAttempt(p)||status==='unattempted'&&!hasAttempt(p)) && (!search||`${q.qid} ${q.topic} ${q.subtopic} ${q.skill_search||''}`.toLowerCase().includes(search.toLowerCase()));
  }),[questions,topic,subtopic,difficulty,status,search,progress]);
  useEffect(()=>{setPage(p=>Math.min(p,Math.max(0,Math.ceil(filtered.length/PAGE_SIZE)-1)));},[filtered.length]);
  const visible=filtered.slice(page*PAGE_SIZE,(page+1)*PAGE_SIZE);
  const saved=questions.filter(q=>progress[q.qid]?.flagged).length;
  function openTopic(name:string){setTopic(name);setSubtopic('all');setDifficulty('all');setStatus('all');setSearch('');setPage(0);}
  function save(q:BankQuestion,patch:Partial<QuestionProgress>){
    if (loading || !viewer) return;
    const updated={...currentProgress.current[q.qid],...patch};
    currentProgress.current={...currentProgress.current,[q.qid]:updated};setProgress(currentProgress.current);setSync('Saving…');
    void saveQuestionProgress(viewer,q,updated).then(r=>setSync(r.warnings.join(' ') || (r.syncState==='synced'?'Progress saved.':'Saved on this device · sync pending.'))).catch(e=>setSync(e.message));
  }
  async function showSolution(q:BankQuestion){
    const generation=++solutionGeneration.current;
    setSolution(undefined);setSolutionError('');setSolutionQ(q);if(!solutionDialog.current?.open)solutionDialog.current?.showModal();window.dispatchEvent(new Event('ts-bank-focus'));
    try{const [detail,result]=await Promise.all([getDetail(q),studio<StoredSolution>('solution',q,viewer)]);if(generation===solutionGeneration.current)setSolution({q,detail,result});}catch(e){if(generation===solutionGeneration.current)setSolutionError(e instanceof Error?e.message:'Solution unavailable.');}
  }
  function showStudio(q:BankQuestion){
    studioOpenId.current=crypto.randomUUID();
    if(!initialStudioQ.current)initialStudioQ.current=q.qid;
    setStudioQ(q);if(!studioDialog.current?.open)studioDialog.current?.showModal();window.dispatchEvent(new Event('ts-bank-focus'));
    frame.current?.contentWindow?.postMessage({type:'ts-studio-open',qid:q.qid,openId:studioOpenId.current},location.origin);
  }
  async function logout(){await supabaseBrowser().auth.signOut();location.assign('/login');}
  return <div className={`ts-qb-preview tmua-bank-root ${embedded?'bank-embedded':''}`}>
    {!embedded && <><a className="skip" href="#tmua-bank-main">Skip to question bank</a><header className="portal-header"><a className="portal-brand" href="/dashboard">Thriving Scholars</a><span className="portal-subtitle">TMUA STUDENT PORTAL</span><div className="portal-account"><button className="logout-btn" onClick={()=>void logout()}>Logout</button></div></header>
      <aside className="portal-sidebar" aria-label="Portal navigation"><div className="workspace-label">YOUR TMUA<br/>WORKSPACE</div><nav className="workspace-nav"><button className="workspace-link active" aria-current="page" aria-label="Question Bank" onClick={()=>openTopic('')}><span className="nav-number">1</span><span className="nav-text">Question Bank</span></button><a className="workspace-link" href="/dashboard?section=practice" aria-label="Practice Tests"><span className="nav-number">2</span><span className="nav-text">Practice Tests</span></a><a className="workspace-link" href="/dashboard?section=classes" aria-label="Classes"><span className="nav-number">3</span><span className="nav-text">Classes</span></a></nav><div className="sidebar-secondary"><a className="resource-link" href="/dashboard?section=resources" aria-label="Resources"><BookOpen className="icon"/><span className="nav-text">Resources</span></a></div><div className="sidebar-foot"><strong>Support</strong><a href="mailto:outreach@thrivingscholars.com">outreach@<wbr/>thrivingscholars.com</a><a href="https://wa.me/447459070019">WhatsApp: +44 7459 070019</a></div></aside></>}
    <main className="ts-questionbank" id="tmua-bank-main" aria-busy={loading}>
      {loading && <BankLoading/>}
      {!loading && sync && <p className="bank-sync" role="status">{sync}</p>}
      {error && <div className="bank-error" role="alert"><p>{error}</p><button className="btn" onClick={()=>setRetry(n=>n+1)}>Retry loading</button><a className="btn" href="/login?next=%2Ftmua-question-bank">Sign in</a></div>}
      {!loading && !error && (!topic ? <section id="overview" className="qb-view"><div className="page-heading"><div><h1>QUESTION BANK</h1><p>Choose a topic. Questions progress from Level 1 to Level 5.</p></div><button className="btn" onClick={()=>{openTopic('all');setStatus('saved');}}><Bookmark className="icon small"/>Saved {saved}</button></div><div className="topic-overview-grid">{topics.map((t,i)=>{
        const set=questions.filter(q=>q.topic===t), done=set.filter(q=>hasAttempt(progress[q.qid])).length;
        const subjects=[...new Set(set.map(q=>q.subtopic))].slice(0,3).map(cleanTopic).join(' · ');
        return <article className="topic-tile" key={t}><div className="topic-tile-head"><span className="topic-index">{String(i+1).padStart(2,'0')}</span><span className="topic-count">{set.length} questions</span></div><h2><button className="topic-open" onClick={()=>openTopic(t)}>{cleanTopic(t)}</button></h2><p className="topic-description">{subjects}</p><div className="topic-progress-meta"><span>{done} / {set.length} practised</span></div><div className="progress-track" role="progressbar" aria-label={`${cleanTopic(t)} questions practised`} aria-valuemin={0} aria-valuemax={set.length} aria-valuenow={done}><span style={{width:`${done/set.length*100}%`}}/></div><div className="topic-tile-foot"><button className="topic-open" onClick={()=>openTopic(t)}>Open topic <ArrowRight className="icon small"/></button></div></article>;
      })}</div></section> : <section className="qb-view"><div className="practice-topline"><button className="text-link" onClick={()=>openTopic('')}><ArrowLeft className="icon small"/>All topics</button><span className="view-label">QUESTION BANK</span></div><div className="page-heading"><div><h1>{topic==='all'?'All topics':cleanTopic(topic)}</h1><p>Start with the foundations and work towards harder questions.</p></div><button className="btn" onClick={()=>setStatus(status==='saved'?'all':'saved')} aria-pressed={status==='saved'}><Bookmark className="icon small"/>Saved {saved}</button></div>
        <div className="filter-panel" aria-label="Filter questions"><div className="field"><label htmlFor="bank-topic">Topic</label><select id="bank-topic" value={topic} onChange={e=>openTopic(e.target.value)}><option value="all">All topics</option>{topics.map(t=><option key={t} value={t}>{cleanTopic(t)}</option>)}</select></div><div className="field"><label htmlFor="bank-subtopic">Subtopic</label><select id="bank-subtopic" value={subtopic} onChange={e=>setSubtopic(e.target.value)}><option value="all">All subtopics</option>{[...new Set(questions.filter(q=>topic==='all'||q.topic===topic).map(q=>q.subtopic))].map(s=><option key={s} value={s}>{cleanTopic(s)}</option>)}</select></div><div className="field"><label htmlFor="bank-level">Difficulty</label><select id="bank-level" value={difficulty} onChange={e=>setDifficulty(e.target.value)}><option value="all">All levels</option>{[1,2,3,4,5].map(l=><option key={l} value={l}>Level {l}</option>)}</select></div><div className="field"><label htmlFor="bank-progress">Progress</label><select id="bank-progress" value={status} onChange={e=>setStatus(e.target.value)}><option value="all">All questions</option><option value="unattempted">Not attempted</option><option value="attempted">Attempted</option><option value="review">Needs review</option><option value="correct">Correct</option><option value="saved">Saved</option></select></div><div className="field"><label htmlFor="bank-search">Search</label><input id="bank-search" type="search" placeholder="Search topics or skills…" value={search} onChange={e=>setSearch(e.target.value)}/></div></div>
        <div className="results-bar"><span>{filtered.length ? `${page*PAGE_SIZE+1}–${Math.min((page+1)*PAGE_SIZE,filtered.length)} of ${filtered.length}`:'No matching questions'} · Easiest to hardest</span><button className="text-link" onClick={()=>openTopic(topic)}>Clear filters</button></div>
        {visible.map((q,i)=><QuestionCard key={q.qid} q={q} viewerId={viewer} index={page*PAGE_SIZE+i+1} state={progress[q.qid]} onSave={save} onSolution={q=>void showSolution(q)} onStudio={showStudio} getDetail={getDetail}/>)}
        {filtered.length>PAGE_SIZE && <nav className="bank-pagination" aria-label="Question pages"><button className="btn" disabled={page===0} onClick={()=>{setPage(n=>n-1);document.getElementById('tmua-bank-main')?.scrollIntoView();}}><ArrowLeft className="icon small"/>Previous</button><span>Page {page+1} of {Math.ceil(filtered.length/PAGE_SIZE)}</span><button className="btn" disabled={(page+1)*PAGE_SIZE>=filtered.length} onClick={()=>{setPage(n=>n+1);document.getElementById('tmua-bank-main')?.scrollIntoView();}}>Next<ArrowRight className="icon small"/></button></nav>}
      </section>)}
      {!loading && <footer className="bank-past-paper-link"><PastPaperPracticeLink /></footer>}
    </main>
    <dialog ref={solutionDialog} onClose={()=>window.dispatchEvent(new Event('ts-bank-focus'))} className="qb-modal solution-modal" aria-labelledby="bank-solution-title"><header className="solution-modal-header"><div><h2 id="bank-solution-title">Worked solution</h2><p>{cleanTopic(solutionQ?.subtopic)}</p></div><button className="icon-btn" aria-label="Close solution" onClick={()=>solutionDialog.current?.close()}><X className="icon"/></button></header>{solution ? <Solution {...solution}/> : <div className="bank-modal-loading" role="status">{solutionError || 'Loading the solution…'}{solutionError && solutionQ && <button className="btn" onClick={()=>void showSolution(solutionQ)}>Retry</button>}</div>}</dialog>
    <dialog ref={studioDialog} onClose={()=>window.dispatchEvent(new Event('ts-bank-focus'))} className="qb-modal studio-modal" aria-labelledby="bank-studio-title"><header className="solution-modal-header"><div><h2 id="bank-studio-title">Study Studio</h2><p>Write, type or upload your working.</p></div><button className="icon-btn" aria-label="Close Study Studio" onClick={()=>studioDialog.current?.close()}><X className="icon"/></button></header>{studioQ && <iframe ref={frame} src={`/tmua-question-bank/studio?qid=${encodeURIComponent(initialStudioQ.current)}`} title="Study Studio writing and feedback"/>}</dialog>
  </div>;
}
