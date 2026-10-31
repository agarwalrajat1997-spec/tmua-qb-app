"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ArrowLeft, ArrowRight, Check, ChevronDown, PenLine } from "lucide-react";
import { NotebookWorkspace } from "./components/NotebookWorkspace";
import { QuestionGuide } from "./components/QuestionGuide";
import { MathHtml } from "./components/MathHtml";
import { cacheGuide, recordGuideEvent } from "./lib/audited-content";
import {
  acceptStudioViewer, checkAnswer, fetchStudioQuestion, getStoredSolution,
  studioRead, type StudioQuestion,
} from "./lib/api";
import { resumeCloudSync } from "./lib/cloud-storage";
import { readLocal } from "./lib/storage";
import { consumeStudioOpen, type EmbedOpenHistory } from "./lib/embed-session";
import { studentErrorMessage } from "./lib/student-content";
import { cleanTopic, questionKey, type Progress, type Question, type StoredSolution } from "./types";

function tellParent(message: Record<string, unknown>) {
  if (window.parent !== window) window.parent.postMessage(message, window.location.origin);
}

type Selection = { qid: string; contentVersion?: string };
type CatalogueItem = Omit<Question, "prompt_html" | "options" | "updated_at">;

export default function StudioEmbed() {
  const [selection, setSelection] = useState<Selection>();
  const [loaded, setLoaded] = useState<StudioQuestion>();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [progress, setProgress] = useState<Record<string, Progress>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [online, setOnline] = useState(true);
  const [saveStatus, setSaveStatus] = useState("Your working saves automatically");
  const [busy, setBusy] = useState(false);
  const [solution, setSolution] = useState<StoredSolution>();
  const [showSolution, setShowSolution] = useState(false);
  const [visit, setVisit] = useState(0);
  const owner = useRef<string | undefined>(undefined);
  const questionOpenedAt = useRef(Date.now());
  const activeQuestionKey = useRef("");
  const parentOpenHistory = useRef<EmbedOpenHistory>({ received: false });

  const openQuestion = useCallback((question: Question) => {
    setSelection({ qid: question.qid, contentVersion: question.content_version });
  }, []);
  const updateProgress = useCallback((question: Question, patch: Progress) => {
    const uid = owner.current;
    if (!uid) return;
    setProgress((previous) => {
      const next = { ...previous, [questionKey(question)]: {
        ...previous[questionKey(question)], contentVersion: question.content_version, ...patch,
      } };
      return next;
    });
  }, []);

  useEffect(() => {
    if (!owner.current) return;
    try { localStorage.setItem(`ts-studio-progress-v1:user:${owner.current}`, JSON.stringify(progress)); }
    catch { setNotice("Your browser could not save the answer history. Your writing pads save separately."); }
  }, [progress]);

  useEffect(() => {
    const qid = new URLSearchParams(window.location.search).get("qid");
    if (qid) setSelection({ qid });
    const onMessage = (event: MessageEvent) => {
      if (event.origin !== window.location.origin || event.source !== window.parent ||
          event.data?.type !== "ts-studio-open" || typeof event.data.qid !== "string" ||
          !event.data.qid || event.data.qid.length > 180) return;
      const qid = event.data.qid;
      const opened = consumeStudioOpen(
        parentOpenHistory.current, qid, event.data.openId, activeQuestionKey.current,
      );
      parentOpenHistory.current = opened.history;
      if (opened.revisit) setVisit((value) => value + 1);
      setSelection((previous) => previous?.qid === qid ? previous : { qid });
    };
    const connection = () => setOnline(navigator.onLine);
    const escape = (event: KeyboardEvent) => {
      if (event.key !== "Escape" || event.defaultPrevented || window.parent === window) return;
      // Child confirmation/feedback panels consume Escape before closing Studio.
      if (document.querySelector('dialog[open], [role="dialog"], .feedback-detail')) return;
      event.preventDefault();
      tellParent({ type: "ts-studio-close" });
    };
    connection();
    window.addEventListener("message", onMessage);
    window.addEventListener("online", connection);
    window.addEventListener("offline", connection);
    window.addEventListener("keydown", escape);
    tellParent({ type: "ts-studio-ready" });
    return () => {
      window.removeEventListener("message", onMessage);
      window.removeEventListener("online", connection);
      window.removeEventListener("offline", connection);
      window.removeEventListener("keydown", escape);
    };
  }, []);

  useEffect(() => {
    let active = true;
    void studioRead<{ viewerId: string; questions: CatalogueItem[] }>("catalogue").then((data) => {
      acceptStudioViewer(data.viewerId);
      if (active) setQuestions(data.questions.map((question) => ({
        ...question, prompt_html: "", options: [], updated_at: "",
      })));
    }).catch(() => {
      // The individual question still works if the optional Next catalogue is unavailable.
    });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!selection) return;
    let active = true;
    setLoading(true);
    setError("");
    setNotice("");
    setSolution(undefined);
    setShowSolution(false);
    setBusy(false);
    activeQuestionKey.current = "";
    void fetchStudioQuestion(selection.qid, selection.contentVersion).then((data) => {
      if (!active) return;
      if (data.guide) cacheGuide(data.question, data.guide);
      if (!owner.current) {
        owner.current = data.viewerId;
        setProgress(readLocal(`ts-studio-progress-v1:user:${data.viewerId}`, {}));
        void resumeCloudSync();
      }
      activeQuestionKey.current = questionKey(data.question);
      questionOpenedAt.current = Date.now();
      setLoaded(data);
      tellParent({ type: "ts-studio-question", qid: data.question.qid });
    }).catch((reason: Error) => {
      if (active) { setLoaded(undefined); setError(reason.message); }
    }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [selection]);

  async function submitAnswer() {
    if (!loaded) return;
    const question = loaded.question;
    const selected = progress[questionKey(question)]?.selected;
    const openedAt = questionOpenedAt.current;
    if (!selected || busy) return;
    setBusy(true);
    setNotice("");
    try {
      const result = await checkAnswer(question.qid, question.content_version, selected);
      updateProgress(question, { selected, submitted: true, correct: result.correct, checkedAt: new Date().toISOString() });
      tellParent({
        type: "ts-studio-answer", qid: question.qid, contentVersion: question.content_version,
        selected, correct: result.correct, submissionId: crypto.randomUUID(),
        answerElapsedSeconds: Math.max(0, Math.round((Date.now() - openedAt) / 1000)),
      });
    } catch (reason) {
      if (activeQuestionKey.current === questionKey(question)) setNotice((reason as Error).message);
    } finally {
      if (activeQuestionKey.current === questionKey(question)) setBusy(false);
    }
  }

  async function toggleSolution() {
    if (!loaded) return;
    if (showSolution) { setShowSolution(false); return; }
    const question = loaded.question;
    setNotice("");
    try {
      const result = solution ?? await getStoredSolution("tmua", question.qid, question.content_version);
      if (activeQuestionKey.current !== questionKey(question)) return;
      setSolution(result);
      setShowSolution(true);
      updateProgress(question, { solutionViewed: true });
      recordGuideEvent(question, "solution_opened");
    } catch (reason) {
      if (activeQuestionKey.current === questionKey(question)) setNotice((reason as Error).message);
    }
  }

  const question = loaded?.question;
  const current = question ? progress[questionKey(question)] ?? {} : {};
  const scope = loaded && question ? `user:${loaded.viewerId}:practice:${questionKey(question)}` : "";

  return <main className="studio-embed">
    <header className="studio-embed-header">
      <button className="secondary" onClick={() => {
        if (window.parent !== window) tellParent({ type: "ts-studio-close" });
        else window.location.assign("/tmua-question-bank");
      }}><ArrowLeft size={16} /> Question bank</button>
      <div><strong>Study Studio</strong><span>Write, think, understand.</span></div>
      {!online && <span role="status" className="studio-connection">Offline · writing stays saved on this device</span>}
    </header>
    {notice && <div className="studio-embed-notice" role="status">{studentErrorMessage(notice)}<button aria-label="Dismiss message" onClick={() => setNotice("")}>×</button></div>}
    {loading ? <div className="studio-embed-empty" role="status">Opening your question and saved working…</div> :
      error ? <div className="studio-embed-empty" role="alert"><p>{studentErrorMessage(error)}</p><button className="secondary" onClick={() => setSelection((previous) => previous ? { ...previous } : undefined)}>Try again</button></div> :
      question && loaded ? <div className="workbench">
        <section className="question-panel" aria-label="Question">
          <div className="question-content">
            <div className="question-meta"><span className="tag">TMUA</span><span>Level {question.difficulty} · {question.paper}</span></div>
            <p className="studio-topic">{cleanTopic(question.topic)}</p>
            <h1>Show how you get there.</h1>
            <MathHtml html={question.prompt_html} className="question-prompt" />
            <div className="options" aria-label="Answer choices">
              {question.options.map((option) => <button key={option.label}
                aria-pressed={current.selected === option.label}
                disabled={busy}
                className={`answer-option ${current.selected === option.label ? "chosen" : ""}`}
                onClick={() => updateProgress(question, { selected: option.label, submitted: false, correct: undefined })}>
                <span className="option-letter">{option.label}</span><MathHtml html={option.html} />
                {current.selected === option.label && <Check size={16} />}
              </button>)}
            </div>
            <button className="primary full-width" disabled={!current.selected || busy || !online} onClick={() => void submitAnswer()}>
              {busy ? "Checking…" : "Check answer"}<ArrowRight size={16} />
            </button>
            {current.submitted && <div className={`answer-result ${current.correct ? "good" : "retry"}`} role="status">
              <strong>{current.correct ? "That’s the correct answer." : "Not quite. Give it another go."}</strong>
              <p>{current.correct ? "Can you explain why your method works?" : "Review your working, or open the worked solution."}</p>
              <button className="text-button" onClick={() => void toggleSolution()}>{showSolution ? "Hide solution" : "View worked solution"}<ChevronDown size={14} /></button>
              {showSolution && solution && <MathHtml html={solution.solutionHtml} />}
            </div>}
            <div className="question-tip"><PenLine size={17} /><p>Try the question independently first.<br /><strong>Your working is where the learning happens.</strong></p></div>
            {question.audited && <QuestionGuide key={questionKey(question)} question={question}
              submitted={!!current.submitted} selected={current.selected} questions={[]}
              progress={progress} onNext={openQuestion} />}
          </div>
        </section>
        <section className="writing-panel" aria-label="Your working">
          <div className="writing-heading"><div><span className="small-dot" /><strong>Your working</strong><span className="writing-subtitle">Think it through, one line at a time.</span></div><small>{saveStatus}</small></div>
          <NotebookWorkspace key={`${scope}:visit:${visit}`} scope={scope} question={question} isMock={false} readOnly={false}
            online={online} aiReady={loaded.configured}
            onConnect={() => setNotice("Feedback is temporarily unavailable. Your working is saved. You can keep writing and use the hints and solutions. Please contact your teacher if this continues.")}
            onStatus={setSaveStatus} questions={questions} progress={progress} onNextQuestion={openQuestion}
            onReviewComplete={(feedback) => {
              if (!feedback) return;
              updateProgress(question, { reviewedAt: new Date().toISOString() });
              tellParent({ type: "ts-studio-reviewed", qid: question.qid, contentVersion: question.content_version });
            }} />
        </section>
      </div> : <div className="studio-embed-empty">Choose a question from the question bank to open your writing pad.</div>}
  </main>;
}
