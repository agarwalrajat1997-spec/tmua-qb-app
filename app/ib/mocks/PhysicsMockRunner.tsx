"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import Script from "next/script";
import IbBrand from "../IbBrand";
import MathContent from "../components/MathContent";
import DiagramImage from "../components/DiagramImage";
import { answerKey, physicsPdfUrl, reportPayload, secondsRemaining, restorePhysicsDraft, type PhysicsMockDraft, type PhysicsMockPrompt, type PhysicsPromptQuestion, type PhysicsSolution, type MockReview } from "@/lib/ib/physics-mock-model";
import styles from "./physics-challenge.module.css";

type Draft = PhysicsMockDraft;
type MailState = "idle" | "sending" | "sent" | "failed" | "unknown";
type MailKind = "completion" | "scored";
type EmailJs = { init: (key: string) => void; send: (service: string, template: string, payload: Record<string, string>) => Promise<unknown> };
type Props = { paper: PhysicsMockPrompt; email: string; accountId: string; initialAttempt?: string };
const emptyDraft = (): Draft => ({ version: 2, attemptId: "", name: "", startedAt: 0, deadline: 0, elapsed: 0, stage: "instructions", index: 0, answers: {}, flags: {}, marks: {} });
const clock = (seconds: number) => `${String(Math.floor(seconds / 3600)).padStart(2, "0")}:${String(Math.floor(seconds / 60) % 60).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;
function MockQuestion({ question }: { question: PhysicsPromptQuestion | PhysicsSolution }) {
  const src = question.diagramUrl;
  return <div className={styles.questionBody}><div className={styles.questionHeading}><h2>Question {question.number}</h2><strong>[Maximum mark: {question.marks}]</strong></div>{question.stem ? <MathContent>{question.stem}</MathContent> : null}{src ? <figure className={styles.diagram}><DiagramImage src={src} caption={question.diagramCaption || `Diagram for question ${question.number}`} /></figure> : null}<ol className={styles.parts}>{question.parts.map(part => <li key={part.label}><span>{part.label ? `(${part.label})` : ""}</span><MathContent>{part.prompt}</MathContent><strong>[{part.marks}]</strong></li>)}</ol></div>;
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
export default function PhysicsMockRunner({ paper, email, accountId, initialAttempt }: Props) {
  const [draft, setDraft] = useState<Draft>(emptyDraft), [ready, setReady] = useState(false), [remaining, setRemaining] = useState(paper.minutes * 60);
  const [review, setReview] = useState<MockReview | null>(null), [busy, setBusy] = useState(false), [error, setError] = useState("");
  const [warning, setWarning] = useState(""), [confirm, setConfirm] = useState(false), [pdfOpen, setPdfOpen] = useState(false);
  const [mail, setMail] = useState<Record<MailKind, MailState>>({ completion: "idle", scored: "idle" });
  const [mailError, setMailError] = useState("");
  const draftRef = useRef(draft); draftRef.current = draft;
  const submitting = useRef(false), mailBusy = useRef(new Set<string>());
  const storageKey = `ts:ib-physics:v2:${accountId}:${paper.id}`, api = `/api/ib/mocks/${paper.mockId}`;
  const home = `/ib?subject=physics-hl&course=${paper.course}&view=mocks`;
  const pdfUrl = physicsPdfUrl(paper);
  const mailKey = useCallback((attempt: string, kind: MailKind) => `ts:ib-physics-mail:v2:${accountId}:${attempt}:${kind}`, [accountId]);
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
      await sdk.send("service_5l4w8x2", "template_j1jrs4o", reportPayload(paper, result, email, window.location.origin));
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
      try { const raw = localStorage.getItem(storageKey); if (raw) { const saved = restorePhysicsDraft(raw, paper); if (saved?.attemptId === result.id) partial = saved; } } catch {}
      setDraft(d => ({ ...d, attemptId: result.id, name: result.name, elapsed: result.elapsed, stage: "review", answers: result.answers, marks: result.selfMarks ?? partial?.marks ?? d.marks }));
      for (const kind of ["completion", "scored"] as const) try { const state = localStorage.getItem(mailKey(attempt, kind)); setMail(old => ({ ...old, [kind]: state === "sending" ? "unknown" : ["sent", "failed", "unknown"].includes(state ?? "") ? state as MailState : "idle" })); } catch {}
    } catch (e) { setError(e instanceof Error ? e.message : "Could not load your report."); } finally { setBusy(false); }
  }, [api, mailKey, paper, storageKey]);
  useEffect(() => {
    let saved: Draft | null = null;
    if (!initialAttempt) try { const raw = localStorage.getItem(storageKey); if (raw) saved = restorePhysicsDraft(raw, paper); } catch { setWarning("Device saving is unavailable. Keep this tab open until submission."); }
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
      window.history.replaceState(null, "", `?attempt=${result.id}`);
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
  function startAgain() { try { localStorage.removeItem(storageKey); } catch {} window.location.assign(`/ib/mocks/${paper.mockId}/${paper.paper}`); }
  const answered = (q: PhysicsPromptQuestion) => q.questionType === "multiple-choice" ? !!draft.answers[q.id] : q.parts.every(p => !!draft.answers[answerKey(q.id, p.label)]?.trim());
  const item = paper.questions[draft.index], answerCount = paper.questions.filter(q => answered(q)).length;
  const unmarked = paper.questions.flatMap(q => q.parts.map(p => answerKey(q.id, p.label))).filter(key => draft.marks[key] === undefined).length;
  return <div className={styles.app}>
    <Script src="https://cdn.jsdelivr.net/npm/emailjs-com@3/dist/email.min.js" strategy="afterInteractive" />
    <header className={styles.header}><Link href={home} aria-label="IB Physics mock tests"><IbBrand /></Link><span className={styles.account}>{email}</span><Link href={home}>All mocks ↗</Link></header>
    <main className={styles.main}>
      <div className={styles.heading}><span className={styles.tag}>PHYSICS · {paper.course.toUpperCase()}</span><h1>Mock Set {paper.set}<span>Paper {paper.paper}</span></h1><p>{paper.minutes} minutes · {paper.marks} marks · Calculator permitted</p></div>
      {warning ? <p className={styles.notice} role="status">{warning}</p> : null}
      {error ? <div className={styles.error} role="alert">{error}{(initialAttempt || draft.stage === "review") && !review ? <button onClick={() => loadAttempt(initialAttempt || draft.attemptId)} disabled={busy}>Retry loading</button> : null}</div> : null}
      {!ready ? <p>Loading your saved work…</p> : null}
      {ready && draft.stage === "instructions" && !initialAttempt ? <section className={styles.instructions}><h2>Before you begin</h2><ul><li>Answer all questions. Show your method and working clearly; a correct unsupported answer may not earn every mark.</li><li>{paper.calculator ? "Have a calculator ready. Give answers to an appropriate precision with units unless a question specifies otherwise." : "Do not use a calculator. Give exact answers unless a question specifies an approximation."}</li><li>Use a clean Physics data booklet, paper and a pen. Figures are not necessarily drawn to scale.</li><li>You may work on paper. Enter your answer or a brief working summary beside each part and retain your written work for marking.</li><li>Your timer continues if you leave or refresh. Drafts are saved on this device; successful submissions are saved to your account.</li><li>After submission, your completion report and the combined question-and-solution PDF link are emailed to {email}. Marking is initially pending. You can then self-assess each part and send the scored report.</li></ul><label className={styles.field}>Your name for the report<input value={draft.name} onChange={e => setDraft(d => ({ ...d, name: e.target.value }))} maxLength={100} autoComplete="name" /></label><p className={styles.note}>This is an independent practice mock. Written marks are self-assessed, and no official IB grade is calculated.</p><button className={styles.primary} onClick={start}>Start timed paper →</button></section> : null}
      {ready && draft.stage === "running" ? <>
        <div className={styles.toolbar}><strong>{item.section ? `Paper ${item.section} · ` : ""}Question {item.number}</strong><span role="timer" aria-label="Time remaining" className={remaining < 300 ? styles.urgent : styles.timer}>{clock(remaining)}</span><button className={styles.secondary} onClick={() => setDraft(d => ({ ...d, flags: { ...d.flags, [item.id]: !d.flags[item.id] } }))} aria-pressed={!!draft.flags[item.id]}>{draft.flags[item.id] ? "⚑ Flagged" : "Flag question"}</button><button className={styles.primary} onClick={() => setConfirm(true)}>Submit paper</button></div>
        {confirm ? <section className={styles.confirm} role="alertdialog" aria-labelledby="physics-submit-title"><h2 id="physics-submit-title">Submit this paper?</h2><p>{paper.questions.length - answerCount} question{paper.questions.length - answerCount === 1 ? "" : "s"} without a complete typed response. Keep your written working for marking. Submitted responses cannot be changed.</p><button className={styles.primary} onClick={finish}>Submit and review</button><button className={styles.secondary} onClick={() => setConfirm(false)}>Keep working</button></section> : null}
        <div className={styles.examGrid}><aside className={styles.navigator} aria-label="Question navigator">{[...new Set(paper.questions.map(q => q.section))].map(section => <div key={section}><h2>{section ? `Paper ${section}` : `Paper ${paper.paper}`}</h2><div className={styles.numbers}>{paper.questions.map((q, index) => q.section === section ? <button key={q.id} onClick={() => jump(index)} aria-label={`Paper ${q.section} question ${q.number}${answered(q) ? ", answered" : ""}${draft.flags[q.id] ? ", flagged" : ""}`} aria-current={index === draft.index ? "step" : undefined} className={`${answered(q) ? styles.answered : ""} ${index === draft.index ? styles.current : ""}`}>{q.number}{draft.flags[q.id] ? " ⚑" : ""}</button> : null)}</div></div>)}<p>Filled = response entered<br />⚑ = review later</p></aside><section className={styles.question} aria-label={`Question ${item.number}`}><MockQuestion question={item} /><div className={styles.responses}>{item.questionType === "multiple-choice" ? <fieldset className={styles.mcqChoices}><legend>Choose one answer</legend>{item.options?.map(option => <label key={option.label}><input type="radio" name={item.id} value={option.label} checked={draft.answers[item.id] === option.label} onChange={() => write(item.id, option.label)} /><strong>{option.label}</strong><MathContent>{option.text}</MathContent></label>)}<button className={styles.secondary} onClick={() => write(item.id, "")}>Clear choice</button></fieldset> : null}{item.parts.map(part => <label key={part.label} className={styles.field}>{part.label ? `Part (${part.label})` : "Your response"} · {part.marks} marks<textarea rows={4} maxLength={12000} value={draft.answers[answerKey(item.id, part.label)] ?? ""} onChange={e => write(answerKey(item.id, part.label), e.target.value)} placeholder="Enter your answer or summarise working completed on paper." /></label>)}</div><div className={styles.questionFooter}><button className={styles.secondary} disabled={draft.index === 0} onClick={() => jump(draft.index - 1)}>← Previous</button><span>{draft.index + 1} of {paper.questions.length}</span>{draft.index < paper.questions.length - 1 ? <button className={styles.primary} onClick={() => jump(draft.index + 1)}>Next →</button> : <button className={styles.primary} onClick={() => setConfirm(true)}>Review and submit</button>}</div></section></div>
      </> : null}
      {draft.stage === "pending" ? <section className={styles.instructions}><h2>{busy ? "Saving your responses…" : "Responses locked for submission"}</h2><p>Your responses remain on this device. The solution book appears after the server confirms the saved attempt.</p>{!busy ? <button className={styles.primary} onClick={submit}>Retry submission</button> : null}</section> : null}
      {review ? <>
        <section className={styles.result}><span className={styles.tag}>{review.selfMarks ? "REPORT SAVED · SELF-ASSESSED" : "ATTEMPT SAVED · MARKING PENDING"}</span><h2>{review.score.total === null ? "Your paper is submitted" : `${review.score.total} / ${review.score.maximum}`}</h2><p>Time used: {clock(review.elapsed)}. {review.score.mcqMaximum ? `Multiple choice: ${review.score.mcq} / ${review.score.mcqMaximum} (automatically marked). ` : ""} {review.selfMarks ? "Your written marks are self-assessed." : "Use the worked solution book below, then enter a mark for every part."} No official IB grade is calculated.</p><div className={styles.reportActions}>{(["completion", ...(review.selfMarks ? ["scored"] as const : [])] as MailKind[]).map(kind => <button key={kind} className={styles.secondary} disabled={mail[kind] === "sending" || mail[kind] === "sent"} onClick={() => deliverEmail(review, kind, true)}>{mail[kind] === "sent" ? `${kind === "completion" ? "Completion" : "Scored"} email accepted ✓` : mail[kind] === "sending" ? "Sending report…" : `${mail[kind] === "failed" || mail[kind] === "unknown" ? "Retry" : "Email"} ${kind} report`}</button>)}<button className={styles.secondary} onClick={() => window.print()}>Print report</button><p role="status">{mailError || (mail.completion === "sent" ? `Completion report accepted for delivery to ${email}.` : mail.completion === "unknown" ? "The previous email request was not confirmed. Check your inbox before retrying." : "")}</p></div></section>
        <section className={styles.pdfSection}><h2>Question paper and worked solution book</h2><p>The question paper comes first, followed by the complete worked solutions.</p><a className={styles.primary} href={pdfUrl} target="_blank" rel="noopener noreferrer">Open the combined PDF ↗</a><details onToggle={event => { if (event.currentTarget.open) setPdfOpen(true); }}><summary>Read the PDF here</summary>{pdfOpen ? <iframe src={`${pdfUrl}#toolbar=0&navpanes=0&view=FitH`} title={`${paper.title} question paper and worked solutions`} className={styles.pdfFrame} referrerPolicy="no-referrer" /> : null}<p className={styles.note}>If the PDF does not appear, use the link above.</p></details></section>
        {review.selfMarks ? <section className={styles.breakdown}><h2>Question breakdown</h2><table><thead><tr><th>Question</th><th>Marks (MCQ automatic; written self-assessed)</th></tr></thead><tbody>{review.score.rows.map(q => <tr key={q.id}><td>{q.label}</td><td>{q.score} / {q.max}</td></tr>)}</tbody></table></section> : null}
        <section className={styles.solutions}><h2>Worked solutions and self-assessment</h2><p>Check your retained working and the supplied marking points. Enter whole-number marks up to each part’s maximum. Accept valid alternative methods and apply follow-through only where the marking note allows it.</p>{review.solutions.map(q => <details key={q.id} className={styles.solution}><summary>Paper {q.section} · Question {q.number} · {q.marks} marks</summary><div className={styles.solutionBody}><MockQuestion question={q} />{q.options ? <ul>{q.options.map(option => <li key={option.label}><strong>{option.label}</strong><MathContent>{option.text}</MathContent></li>)}</ul> : null}{q.markScheme.map(group => <section key={group.part || "whole"}><h3>{group.part ? `Part (${group.part})` : "Worked solution"}</h3><p className={styles.writtenAnswer}><strong>Your response:</strong> {review.answers[answerKey(q.id, group.part)] || "No typed response. Check your retained written work."}</p><ol className={styles.markSteps}>{group.steps.map((step, index) => <li key={index}><strong>{step.code}</strong><MathContent>{step.text}</MathContent></li>)}</ol>{q.questionType === "multiple-choice" ? <p><strong>Correct choice: {q.correctOption}.</strong> Automatically marked.</p> : <label className={styles.markInput}>Your mark for Question {q.number}{group.part ? ` (${group.part})` : ""}<select disabled={!!review.selfMarks} value={draft.marks[answerKey(q.id, group.part)] ?? ""} onChange={event => { const value = event.target.value; setDraft(d => { const marks = { ...d.marks }; if (value === "") delete marks[answerKey(q.id, group.part)]; else marks[answerKey(q.id, group.part)] = Number(value); return { ...d, marks }; }); }}><option value="">Choose a mark</option>{Array.from({ length: (q.parts.find(part => part.label === group.part)?.marks ?? 0) + 1 }, (_, mark) => <option key={mark} value={mark}>{mark}</option>)}</select></label>}</section>)}</div></details>)}</section>
        {!review.selfMarks ? <div className={styles.markFooter}><p>{unmarked} part{unmarked === 1 ? "" : "s"} left to mark. Save the marks to receive the self-assessed score report.</p><button className={styles.primary} onClick={saveMarks} disabled={busy || unmarked > 0}>{busy ? "Saving…" : "Save marks and email scored report"}</button></div> : null}
        <Link className={styles.back} href={home}>← Back to Physics mocks</Link>{review.selfMarks ? <button className={styles.secondary} onClick={startAgain}>Start a new attempt</button> : null}
      </> : null}
    </main>
  </div>;
}
