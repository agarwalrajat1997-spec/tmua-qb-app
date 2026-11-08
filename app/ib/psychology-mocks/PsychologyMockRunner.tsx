"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import Script from "next/script";
import IbBrand from "../IbBrand";
import MathContent from "../components/MathContent";
import DiagramImage from "../components/DiagramImage";
import { selectedQuestions, sectionTitle, answerKey, psychologyPdfUrl, reportPayload, secondsRemaining, restorePsychologyDraft, type PsychologyMockDraft, type PsychologyMockPrompt, type PsychologyPromptQuestion, type PsychologySolution, type MockReview } from "@/lib/ib/psychology-mock-model";
import styles from "../mocks/physics-challenge.module.css";

type Draft = PsychologyMockDraft;
type MailState = "idle" | "sending" | "sent" | "failed" | "unknown";
type MailKind = "completion" | "scored";
type EmailJs = { init: (key: string) => void; send: (service: string, template: string, payload: Record<string, string>) => Promise<unknown> };
type Props = { paper: PsychologyMockPrompt; email: string; accountId: string; initialAttempt?: string };
const emptyDraft = (): Draft => ({ version: 2, attemptId: "", name: "", startedAt: 0, deadline: 0, elapsed: 0, stage: "instructions", index: 0, answers: {}, flags: {}, marks: {} });
const clock = (seconds: number) => `${String(Math.floor(seconds / 3600)).padStart(2, "0")}:${String(Math.floor(seconds / 60) % 60).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;
function ResearchChart({src,caption}:{src:string;caption:string}){
  return <><img src={src} alt={caption} width={650} height={300} style={{maxWidth:"100%",height:"auto"}}/><details style={{textAlign:"left"}}><summary>Read chart values</summary><p>{caption}</p></details></>;
}
function MockQuestion({ question }: { question: PsychologyPromptQuestion | PsychologySolution }) {
  return <div className={styles.questionBody}><div className={styles.questionHeading}><h2>Question {question.number}{" · "+question.title}</h2><strong>[Maximum mark: {question.marks}]</strong></div>{question.stem ? <MathContent>{question.stem}</MathContent> : null}{question.stimulusUrl ? <figure className={styles.diagram}><ResearchChart src={question.stimulusUrl} caption={question.stimulusCaption || question.title}/></figure> : null}{question.parts.map(part => <div key={part.label}><MathContent>{part.prompt}</MathContent></div>)}</div>;
}
async function emailJsReady(): Promise<EmailJs> {
  const start = Date.now();
  while (Date.now() - start < 4000) {
    const sdk = (window as Window & { emailjs?: EmailJs }).emailjs;
    if (sdk?.send) return sdk;
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  throw new Error("The email service has not loaded. Check your connection, then retry.");
}
async function attemptResponse(response: Response, fallback: string) {
  let data;
  try { data = await response.json(); } catch { throw new Error(fallback); }
  if (!data || typeof data !== "object") throw new Error(fallback);
  if (!response.ok) throw new Error(typeof data.error === "string" ? data.error : fallback);
  if (!data.review || !Array.isArray(data.review.solutions)) throw new Error(fallback);
  return data as { review: MockReview; paper: string };
}
export default function PsychologyMockRunner({ paper, email, accountId, initialAttempt }: Props) {
  const [draft, setDraft] = useState<Draft>(emptyDraft), [ready, setReady] = useState(false), [remaining, setRemaining] = useState(paper.minutes * 60);
  const [review, setReview] = useState<MockReview | null>(null), [busy, setBusy] = useState(false), [error, setError] = useState("");
  const [warning, setWarning] = useState(""), [confirm, setConfirm] = useState(false), [pdfOpen, setPdfOpen] = useState(false);
  const [mail, setMail] = useState<Record<MailKind, MailState>>({ completion: "idle", scored: "idle" });
  const [mailError, setMailError] = useState("");
  const draftRef = useRef(draft); draftRef.current = draft;
  const submitting = useRef(false), mailBusy = useRef(new Set<string>());
  const storageKey = `ts:ib-psychology:v2:${accountId}:${paper.id}`, api = `/api/ib/psychology-mocks/${paper.mockId}`;
  const home = `/ib?subject=psychology&course=${paper.course}&view=mocks`;
  const pdfUrl = psychologyPdfUrl(paper);
  const mailKey = useCallback((attempt: string, kind: MailKind) => `ts:ib-psychology-mail:v2:${accountId}:${attempt}:${kind}`, [accountId]);
  const setMailStatus = useCallback((attempt: string, kind: MailKind, state: MailState) => {
    setMail(old => ({ ...old, [kind]: state }));
    try { localStorage.setItem(mailKey(attempt, kind), state); } catch { setWarning("This browser cannot retain the email status. Check your inbox before retrying a report."); }
  }, [mailKey]);
  const deliverEmail = useCallback(async (result: MockReview, kind: MailKind, manual = false) => {
    const key = mailKey(result.id, kind);
    if (mailBusy.current.has(key) || (kind === "scored" && result.score.total === null)) return;
    let stored: string | null = null;
    try { stored = localStorage.getItem(key); } catch {}
    if (stored === "sent") { setMail(old => ({ ...old, [kind]: "sent" })); return; }
    if (!manual && (stored === "sending" || stored === "unknown" || stored === "failed")) { setMail(old => ({ ...old, [kind]: stored === "sending" ? "unknown" : stored as MailState })); return; }
    mailBusy.current.add(key); setMailStatus(result.id, kind, "sending"); setMailError("");
    try {
      const sdk = await emailJsReady();
      sdk.init("9jjn3yBHl6S88hITy");
      await sdk.send("service_5l4w8x2", "template_j1jrs4o", reportPayload(paper, kind === "completion" && result.selfMarks ? { ...result, score: { ...result.score, total: null, written: null, rows: result.score.rows.map(r => r.marking === "self-assessed" ? {...r,score:null} : r), topics: result.score.topics.map(t => ({...t,score:null})) } } : result, email, window.location.origin));
      setMailStatus(result.id, kind, "sent");
    } catch (e) { setMailStatus(result.id, kind, "failed"); setMailError(e instanceof Error ? e.message : "The service did not confirm sending. Your saved report and solution book remain available."); }
    finally { mailBusy.current.delete(key); }
  }, [email, mailKey, paper, setMailStatus]);
  const loadAttempt = useCallback(async (attempt: string) => {
    setBusy(true); setError("");
    try {
      const response = await fetch(`${api}?attempt=${encodeURIComponent(attempt)}&paper=${paper.paper}`, { cache: "no-store" });
      const data = await attemptResponse(response, "We could not load your saved attempt. Please retry.");
      if (data.paper !== paper.paper) throw new Error("This saved attempt belongs to the other paper.");
      const result = data.review as MockReview; setReview(result);
      let partial: Draft | null = null;
      try { const raw = localStorage.getItem(storageKey); if (raw) { const saved = restorePsychologyDraft(raw, paper); if (saved?.attemptId === result.id) partial = saved; } } catch {}
      setDraft(d => ({ ...d, attemptId: result.id, name: result.name, elapsed: result.elapsed, stage: "review", answers: result.answers, marks: result.selfMarks ?? partial?.marks ?? d.marks }));
      for (const kind of ["completion", "scored"] as const) try { const state = localStorage.getItem(mailKey(attempt, kind)); setMail(old => ({ ...old, [kind]: state === "sending" ? "unknown" : ["sent", "failed", "unknown"].includes(state ?? "") ? state as MailState : "idle" })); } catch {}
    } catch (e) { setError(e instanceof Error ? e.message : "Could not load your report."); } finally { setBusy(false); }
  }, [api, mailKey, paper, storageKey]);
  useEffect(() => {
    let saved: Draft | null = null;
    if (!initialAttempt) try { const raw = localStorage.getItem(storageKey); if (raw) saved = restorePsychologyDraft(raw, paper); } catch { setWarning("Device saving is unavailable. Keep this tab open until submission."); }
    if (saved) setDraft(saved); setReady(true);
    const attempt = initialAttempt || (saved?.stage === "review" ? saved.attemptId : undefined);
    if (attempt) void loadAttempt(attempt);
  }, [initialAttempt, loadAttempt, paper, storageKey]);
  useEffect(() => {
    if (!ready || initialAttempt) return;
    try { localStorage.setItem(storageKey, JSON.stringify(draft)); } catch { setWarning("This browser cannot save your draft. Keep this tab open until your attempt is submitted."); }
  }, [draft, initialAttempt, ready, storageKey]);
  useEffect(() => {
    if (!ready || draft.stage !== "running") return;
    const tick = () => {
      const seconds = secondsRemaining(draftRef.current.deadline, Date.now(), paper.minutes * 60); setRemaining(seconds);
      if (!seconds) setDraft(d => d.stage === "running" ? { ...d, stage: "pending", elapsed: paper.minutes * 60 } : d);
    };
    tick(); const timer = setInterval(tick, 500);
    const warn = (event: BeforeUnloadEvent) => { event.preventDefault(); event.returnValue = ""; };
    window.addEventListener("beforeunload", warn);
    return () => { clearInterval(timer); window.removeEventListener("beforeunload", warn); };
  }, [draft.stage, paper.minutes, ready]);
  const submit = useCallback(async () => {
    const d = draftRef.current;
    if (d.stage !== "pending" || submitting.current) return;
    submitting.current = true; setBusy(true); setError("");
    try {
      const response = await fetch(api, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action: "submit", paper: paper.paper, attemptId: d.attemptId, answers: d.answers, elapsed: d.elapsed, name: d.name }) });
      const data = await attemptResponse(response, "The server could not confirm your submission. Your responses remain on this device; please retry.");
      const result = data.review as MockReview; setReview(result); setDraft(current => ({ ...current, stage: "review", name: result.name, elapsed: result.elapsed, answers: result.answers, marks: result.selfMarks ?? current.marks }));
      window.history.replaceState(null, "", `?course=${paper.course}&attempt=${result.id}`);
      void deliverEmail(result, "completion");
    } catch (e) { setError(e instanceof Error ? e.message : "Submission failed. Your responses remain on this device."); } finally { submitting.current = false; setBusy(false); }
  }, [api, deliverEmail, paper.paper]);
  useEffect(() => { if (ready && draft.stage === "pending") void submit(); }, [draft.stage, ready, submit]);
  function start() { const now = Date.now(); setDraft(d => ({ ...d, attemptId: crypto.randomUUID(), startedAt: now, deadline: now + paper.minutes * 60000, stage: "running" })); window.scrollTo({ top: 0 }); }
  function finish() { setConfirm(false); setDraft(d => ({ ...d, stage: "pending", elapsed: Math.min(paper.minutes * 60, Math.max(0, Math.round((Date.now() - d.startedAt) / 1000))) })); }
  function write(key: string, value: string) { setDraft(d => d.stage === "running" && Date.now() < d.deadline ? { ...d, answers: { ...d.answers, [key]: value } } : d); }
  function jump(index: number) { setDraft(d => ({ ...d, index })); setConfirm(false); window.scrollTo({ top: 0, behavior: "smooth" }); }
  async function saveMarks() {
    if (!review || busy) return; setBusy(true); setError("");
    try {
      const response = await fetch(api, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action: "mark", paper: paper.paper, attemptId: review.id, selfMarks: draft.marks }) });
      const data = await attemptResponse(response, "The server could not confirm saving your marks. Please retry.");
      setReview(data.review); setDraft(d => ({ ...d, marks: data.review.selfMarks ?? d.marks })); void deliverEmail(data.review, "scored");
    } catch (e) { setError(e instanceof Error ? e.message : "Marks could not be saved. Please retry."); } finally { setBusy(false); }
  }
  function startAgain() { try { localStorage.removeItem(storageKey); } catch {} window.location.assign(`/ib/psychology-mocks/${paper.mockId}/${paper.paper}`); }
  const answered = (q: PsychologyPromptQuestion) => q.parts.every(p => !!draft.answers[answerKey(q.id, p.label)]?.trim());
  const activeQuestions = selectedQuestions(paper.questions, review?.answers.__choice ?? draft.answers.__choice);
  const extended = paper.questions.filter(q => q.optional);
  const chosen = activeQuestions.filter(q => q.optional);
  const item = activeQuestions[draft.index] ?? activeQuestions[0];
  const answerCount = activeQuestions.filter(answered).length;
  const resources = paper.resources.length ? <details className={styles.instructions}><summary>Paper 3 resource booklet · Sources 2–5</summary>{paper.resources.map(r=><section key={r.number}><h3>Source {r.number} · {r.title}</h3><MathContent>{r.text}</MathContent>{r.figureUrl ? <figure className={styles.diagram}><ResearchChart src={r.figureUrl} caption={r.caption || r.title}/></figure> : null}</section>)}<a href={paper.questionBooklets[1].url} target="_blank" rel="noopener noreferrer">Print the resource booklet (PDF) ↗</a></details> : null;
  const choices = extended.length ? <details className={styles.instructions} open={draft.stage === "instructions" || undefined}>
    <summary>Section C · Choose one of {extended.length} essays</summary>
    <p>Read the options below. You can change your choice while the timer is running. Answer Questions 1–4 as well. Only your chosen essay counts toward the total.</p>
    {extended.map(q => <details key={q.id}><summary>Question {q.number} · {q.title}</summary>
      <MathContent>{q.stem}</MathContent>{q.stimulusUrl ? <DiagramImage src={q.stimulusUrl} caption={q.stimulusCaption || q.title}/> : null}<ol>{q.parts.map(p =>
        <li key={p.label}>{p.prompt} [{p.marks}]</li>)}</ol></details>)}
    {chosen.map((q, slot) => <label className={styles.field} key={slot}>Selected essay
      <select value={q.id} onChange={event => {
        const ids = chosen.map(x => x.id);
        ids[slot] = event.target.value;
        setDraft(d => d.stage === "running" && Date.now() >= d.deadline ? d : ({...d, index:0, answers: {...d.answers, __choice: ids.join(",")}}));
      }}>{extended.map(option => <option value={option.id} key={option.id}
        disabled={chosen.some((other, i) => i !== slot && other.id === option.id)}>
        Question {option.number} · {option.title}</option>)}</select></label>)}
  </details> : null;
  const unmarked = activeQuestions.flatMap(q => q.parts.map(p => answerKey(q.id, p.label))).filter(key => draft.marks[key] === undefined).length;
  return <div className={styles.app}>
    <Script src="https://cdn.jsdelivr.net/npm/emailjs-com@3/dist/email.min.js" strategy="afterInteractive" />
    <header className={styles.header}><Link href={home} aria-label="IB Psychology mock tests"><IbBrand /></Link><span className={styles.account}>{email}</span><Link href={home}>All mocks ↗</Link></header>
    <main className={styles.main}>
      <div className={styles.heading}><span className={styles.tag}>PSYCHOLOGY · {paper.course.toUpperCase()}</span><h1>Mock Set {paper.set}<span>Paper {paper.paper}</span></h1><p>{paper.minutes} minutes · {paper.marks} marks · First assessment 2027</p></div>
      {warning ? <p className={styles.notice} role="status">{warning}</p> : null}
      {error ? <div className={styles.error} role="alert">{error}{(initialAttempt || draft.stage === "review") && !review ? <button onClick={() => loadAttempt(initialAttempt || draft.attemptId)} disabled={busy}>Retry loading</button> : null}</div> : null}
      {!ready ? <p>Loading your saved work…</p> : null}
      {ready && draft.stage === "instructions" && !initialAttempt ? <section className={styles.instructions}><h2>Before you begin</h2><ul><li>{paper.paper === "1" ? "Answer Questions 1–4, then either Question 5 or Question 6. Apply psychological knowledge to the scenarios and develop a reasoned conceptual argument in your essay." : paper.paper === "2" ? "Answer all five questions. In Section A use the class practical specified in your question paper. In Section B evaluate the unseen study." : "Answer all four questions. Source 1 appears with Question 1. Use Sources 2–5 in the resource booklet as directed."}</li><li>You may work on paper. Enter your answer or a brief working summary beside each part and retain your written work for marking.</li><li>Your timer continues if you leave or refresh. Drafts are saved on this device; successful submissions are saved to your account.</li><li>After submission, your completion report and the worked mark scheme link are emailed to {email}. Marking is initially pending. You can then self-assess each part and send the scored report.</li></ul>{resources}{choices}<p>Print the question booklets: {paper.questionBooklets.map(b => <a key={b.url} style={{marginRight:16}} href={b.url} target="_blank" rel="noopener noreferrer">{b.label} (PDF) ↗</a>)}</p><label className={styles.field}>Your name for the report<input value={draft.name} onChange={e => setDraft(d => ({ ...d, name: e.target.value }))} maxLength={100} autoComplete="name" /></label><p className={styles.note}>This is an independent practice mock. Written marks are self-assessed, and no official IB grade is calculated.</p><button className={styles.primary} onClick={start}>Start timed paper →</button></section> : null}
      {ready && draft.stage === "running" ? <>
        {resources}{choices}<div className={styles.toolbar}><strong>{sectionTitle(item)} · Question {item.number}</strong><span role="timer" aria-label="Time remaining" className={remaining < 300 ? styles.urgent : styles.timer}>{clock(remaining)}</span><button className={styles.secondary} onClick={() => setDraft(d => ({ ...d, flags: { ...d.flags, [item.id]: !d.flags[item.id] } }))} aria-pressed={!!draft.flags[item.id]}>{draft.flags[item.id] ? "⚑ Flagged" : "Flag question"}</button><button className={styles.primary} onClick={() => setConfirm(true)}>Submit paper</button></div>
        {confirm ? <section className={styles.confirm} role="alertdialog" aria-labelledby="psychology-submit-title"><h2 id="psychology-submit-title">Submit this paper?</h2><p>{activeQuestions.length - answerCount} question{activeQuestions.length - answerCount === 1 ? "" : "s"} without a complete typed response. Keep your written working for marking. Submitted responses cannot be changed.</p><button className={styles.primary} onClick={finish}>Submit and review</button><button className={styles.secondary} onClick={() => setConfirm(false)}>Keep working</button></section> : null}
        <div className={styles.examGrid}><aside className={styles.navigator} aria-label="Question navigator">{[...new Set(activeQuestions.map(q => q.section))].map(section => <div key={section}><h2>{section ? `Paper ${section}` : `Paper ${paper.paper}`}</h2><div className={styles.numbers}>{activeQuestions.map((q, index) => q.section === section ? <button key={q.id} onClick={() => jump(index)} aria-label={`Paper ${q.section} question ${q.number}${answered(q) ? ", answered" : ""}${draft.flags[q.id] ? ", flagged" : ""}`} aria-current={index === draft.index ? "step" : undefined} className={`${answered(q) ? styles.answered : ""} ${index === draft.index ? styles.current : ""}`}>{q.number}{draft.flags[q.id] ? " ⚑" : ""}</button> : null)}</div></div>)}<p>Filled = response entered<br />⚑ = review later</p></aside><section className={styles.question} aria-label={`Question ${item.number}`}><MockQuestion question={item} /><div className={styles.responses}>{item.parts.map(part => <label key={part.label} className={styles.field}>Your response · {part.marks} marks<textarea rows={4} maxLength={12000} value={draft.answers[answerKey(item.id, part.label)] ?? ""} onChange={e => write(answerKey(item.id, part.label), e.target.value)} placeholder="Enter your answer or summarise working completed on paper." /></label>)}</div><div className={styles.questionFooter}><button className={styles.secondary} disabled={draft.index === 0} onClick={() => jump(draft.index - 1)}>← Previous</button><span>{draft.index + 1} of {activeQuestions.length}</span>{draft.index < activeQuestions.length - 1 ? <button className={styles.primary} onClick={() => jump(draft.index + 1)}>Next →</button> : <button className={styles.primary} onClick={() => setConfirm(true)}>Review and submit</button>}</div></section></div>
      </> : null}
      {draft.stage === "pending" ? <section className={styles.instructions}><h2>{busy ? "Saving your responses…" : "Responses locked for submission"}</h2><p>Your responses remain on this device. The solution book appears after the server confirms the saved attempt.</p>{!busy ? <button className={styles.primary} onClick={submit}>Retry submission</button> : null}</section> : null}
      {review ? <>{resources}
        <section className={styles.result}><span className={styles.tag}>{review.selfMarks ? "REPORT SAVED · SELF-ASSESSED" : "ATTEMPT SAVED · MARKING PENDING"}</span><h2>{review.score.total === null ? "Your paper is submitted" : `${review.score.total} / ${review.score.maximum}`}</h2><p>Time used: {clock(review.elapsed)}.  {review.selfMarks ? "Your written marks are self-assessed." : "Use the worked solution book below, then enter a mark for every part."} No official IB grade is calculated.</p><div className={styles.reportActions}>{(["completion", ...(review.selfMarks ? ["scored"] as const : [])] as MailKind[]).map(kind => <button key={kind} className={styles.secondary} disabled={mail[kind] === "sending" || mail[kind] === "sent"} onClick={() => deliverEmail(review, kind, true)}>{mail[kind] === "sent" ? `${kind === "completion" ? "Completion" : "Scored"} email accepted ✓` : mail[kind] === "sending" ? "Sending report…" : `${mail[kind] === "failed" || mail[kind] === "unknown" ? "Retry" : "Email"} ${kind} report`}</button>)}<button className={styles.secondary} onClick={() => window.print()}>Print report</button><p role="status">{mailError || (mail.completion === "sent" ? `Completion report accepted for delivery to ${email}.` : mail.completion === "unknown" ? "The previous email request was not confirmed. Check your inbox before retrying." : "")}</p></div></section>
        <section className={styles.pdfSection}><h2>Worked mark scheme</h2><p>Use the worked responses and question-specific markbands to assess your answers.</p><a className={styles.primary} href={pdfUrl} target="_blank" rel="noopener noreferrer">Open the solutions PDF ↗</a><details onToggle={event => { if (event.currentTarget.open) setPdfOpen(true); }}><summary>Read the PDF here</summary>{pdfOpen ? <iframe src={`${pdfUrl}#toolbar=0&navpanes=0&view=FitH`} title={`${paper.title} worked mark scheme`} className={styles.pdfFrame} referrerPolicy="no-referrer" /> : null}<p className={styles.note}>If the PDF does not appear, use the link above.</p></details></section>
        {review.selfMarks ? <section className={styles.breakdown}><h2>Question breakdown</h2><table><thead><tr><th>Question</th><th>Marks (self-assessed)</th></tr></thead><tbody>{review.score.rows.map(q => <tr key={q.id}><td>{q.label}</td><td>{q.score} / {q.max}</td></tr>)}</tbody></table></section> : null}
        <section className={styles.solutions}><h2>Worked solutions and self-assessment</h2><p>For longer responses choose the best-fit markband using your whole answer. Award credit for other well-supported arguments. For class-practical questions, mark the research you actually conducted. Enter a whole-number mark for each response; award zero if nothing is creditworthy.</p>{review.solutions.map(q => <details key={q.id} className={styles.solution}><summary>Paper {q.section} · Question {q.number} · {q.marks} marks</summary><div className={styles.solutionBody}><MockQuestion question={q} />{q.markScheme.map(group => <section key={group.part || "whole"}><h3>Worked response</h3><p className={styles.writtenAnswer}><strong>Your response:</strong> {review.answers[answerKey(q.id, group.part)] || "No typed response. Check your retained written work."}</p><ol className={styles.markSteps}>{group.steps.map((step, index) => <li key={index}><strong>{step.code}</strong><MathContent>{step.text}</MathContent></li>)}</ol>{<label className={styles.markInput}>Your mark for Question {q.number}<select disabled={!!review.selfMarks} value={draft.marks[answerKey(q.id, group.part)] ?? ""} onChange={event => { const value = event.target.value; setDraft(d => { const marks = { ...d.marks }; if (value === "") delete marks[answerKey(q.id, group.part)]; else marks[answerKey(q.id, group.part)] = Number(value); return { ...d, marks }; }); }}><option value="">Choose a mark</option>{Array.from({ length: (q.parts.find(part => part.label === group.part)?.marks ?? 0) + 1 }, (_, mark) => <option key={mark} value={mark}>{mark}</option>)}</select></label>}</section>)}</div></details>)}</section>
        {!review.selfMarks ? <div className={styles.markFooter}><p>{unmarked} part{unmarked === 1 ? "" : "s"} left to mark. Save the marks to receive the self-assessed score report.</p><button className={styles.primary} onClick={saveMarks} disabled={busy || unmarked > 0}>{busy ? "Saving…" : "Save marks and email scored report"}</button></div> : null}
        <Link className={styles.back} href={home}>← Back to Psychology mocks</Link>{review.selfMarks ? <button className={styles.secondary} onClick={startAgain}>Start a new attempt</button> : null}
      </> : null}
    </main>
  </div>;
}
