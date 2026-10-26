"use client";

import { useCallback, useEffect, useState } from "react";
import { ESAT_MODULES, type EsatModule, type EsatModulePrediction } from "@/lib/esat-predictions";
import styles from "./EsatModulePredictions.module.css";

type Overview = {
  ok: boolean; error?: string; locked: boolean; predictionSavedAt: string | null; lockedAt: string | null;
  plan: { exam_date: string; modules: EsatModule[]; lock_at: string } | null;
  predictions: EsatModulePrediction[];
  results: { actual_scores: Record<string, number>; assessment: { missedCount: number; meetsScoreCondition: boolean } } | null;
};
const dateText = (date: string) => new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/London", dateStyle: "long" }).format(new Date(date.length === 10 ? `${date}T12:00:00Z` : date));
const timeText = (date: string) => new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/London", dateStyle: "medium", timeStyle: "short" }).format(new Date(date));

export default function EsatModulePredictions() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [error, setError] = useState("");
  const [editing, setEditing] = useState(false);
  const [modules, setModules] = useState<EsatModule[]>(["Mathematics 1"]);
  const [examDate, setExamDate] = useState("");
  const [saving, setSaving] = useState(false);
  const [actualScores, setActualScores] = useState<Record<string, string>>({});
  const load = useCallback(async (signal?: AbortSignal) => {
    try {
      const response = await fetch("/api/esat/module-predictions", { cache: "no-store", credentials: "same-origin", signal });
      const body: Overview = await response.json();
      if (!response.ok || !body.ok) throw new Error(body.error ?? "Unable to load your predictions.");
      if (signal?.aborted) return;
      setOverview(body); setError("");
    } catch (caught) {
      if (!signal?.aborted) setError((caught as Error).message);
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    void load(controller.signal);
    const refresh = () => { if (document.visibilityState === "visible") void load(controller.signal); };
    const timer = window.setInterval(refresh, 60000);
    window.addEventListener("focus", refresh);
    document.addEventListener("visibilitychange", refresh);
    return () => { controller.abort(); window.clearInterval(timer); window.removeEventListener("focus", refresh); document.removeEventListener("visibilitychange", refresh); };
  }, [load]);

  function editPlan() {
    setModules(overview?.plan?.modules ?? ["Mathematics 1"]);
    setExamDate(overview?.plan?.exam_date ?? "");
    setEditing(true);
  }

  async function savePlan(event: React.FormEvent) {
    event.preventDefault(); setSaving(true); setError("");
    try {
      const response = await fetch("/api/esat/module-predictions", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ modules, examDate }) });
      const body: Overview = await response.json();
      if (!response.ok || !body.ok) throw new Error(body.error ?? "Unable to save your exam details.");
      setOverview(body); setEditing(false); setActualScores({});
    } catch (caught) { setError((caught as Error).message); }
    finally { setSaving(false); }
  }

  async function saveResults(event: React.FormEvent) {
    event.preventDefault(); setSaving(true); setError("");
    try {
      const scores = Object.fromEntries((overview?.plan?.modules ?? []).map(module => [module, Number(actualScores[module] ?? overview?.results?.actual_scores[module] ?? "")]));
      const response = await fetch("/api/esat/module-predictions", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ actualScores: scores }) });
      const body: Overview = await response.json();
      if (!response.ok || !body.ok) throw new Error(body.error ?? "Unable to save your results.");
      setOverview(body);
    } catch (caught) { setError((caught as Error).message); }
    finally { setSaving(false); }
  }

  const today = new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/London" }).format(new Date());
  const pastExam = Boolean(overview?.plan && today > overview.plan.exam_date);
  const showForm = Boolean(overview && (!overview.plan || editing));
  const eligibleCount = overview?.predictions.filter(prediction => prediction.guaranteeEligible).length ?? 0;

  return (
    <section className={styles.panel} aria-labelledby="esat-module-predictions-title">
      <div className={styles.heading}>
        <div>
          <p className={styles.eyebrow}>Your ESAT preparation</p>
          <h2 id="esat-module-predictions-title">Predicted scores by module</h2>
          <p>Separate predictions and confidence levels for the three modules you are taking.</p>
        </div>
        {overview?.plan && !editing && (!overview.locked || pastExam) && <button className={styles.secondary} onClick={editPlan}>{pastExam ? "Set up next sitting" : "Edit exam details"}</button>}
      </div>

      {error && <div className={styles.error} role="alert">{error} <button onClick={() => void load()}>Retry</button></div>}
      {!overview && !error && <p role="status">Loading your module predictions…</p>}

      {showForm && <form className={styles.setup} onSubmit={savePlan}>
        <fieldset disabled={saving}>
          <legend>Choose your three exam modules</legend>
          <p>Mathematics 1 is included. Select the other two modules on your exam booking.</p>
          <div className={styles.choices}>{ESAT_MODULES.map(module => <label key={module}>
            <input type="checkbox" checked={modules.includes(module)} disabled={module === "Mathematics 1" || (!modules.includes(module) && modules.length === 3)} onChange={event => setModules(current => event.target.checked ? [...current, module] : current.filter(value => value !== module))} />
            {module}
          </label>)}</div>
          <label className={styles.dateLabel}>Your booked exam date
            <input type="date" required value={examDate} onChange={event => setExamDate(event.target.value)} />
          </label>
          <p>Save these details before the lock date. Your latest saved module predictions lock at 00:00 UK time, two calendar days before your exam.</p>
          <div className={styles.actions}>
            <button className={styles.primary} type="submit" disabled={modules.length !== 3}>{saving ? "Saving…" : "Save and show my predictions"}</button>
            {overview?.plan && <button className={styles.secondary} type="button" onClick={() => setEditing(false)}>Cancel</button>}
          </div>
        </fieldset>
      </form>}

      {overview?.plan && <>
        <div className={styles.lockStatus}>
          <strong>{overview.locked ? "Predictions locked" : "Predictions updating"}</strong>
          <span>Exam: {dateText(overview.plan.exam_date)}</span>
          <span>{overview.locked ? "Locked for" : "Locks"} {dateText(overview.plan.lock_at)} at 00:00 UK time</span>
        </div>
        <div className={styles.cards}>{overview.predictions.map(prediction => <article className={styles.card} key={prediction.module}>
          <h3>{prediction.module}</h3>
          {prediction.score === null ? <>
            <p className={styles.building}>Still building</p>
            <p>Complete a recognised test in this module or build eligible question-bank evidence to see your prediction.</p>
          </> : <>
            <div className={styles.score}>{prediction.score.toFixed(1)}<span> / 9</span></div>
            <p className={styles.confidence} data-confidence={prediction.confidence}>{prediction.confidence ? prediction.confidence[0].toUpperCase() + prediction.confidence.slice(1) : "Building"} confidence</p>
            {prediction.lowerBound !== null && prediction.upperBound !== null && <p>Likely range {prediction.lowerBound.toFixed(1)}–{prediction.upperBound.toFixed(1)}</p>}
          </>}
          <p className={styles.evidence}>{prediction.independentTestCount} independent module {prediction.independentTestCount === 1 ? "paper" : "papers"} · {prediction.qbUniqueQuestions} eligible questions</p>
          <p className={styles.eligibility}>{prediction.guaranteeEligible ? "Meets the confidence requirement" : "Not eligible for the guarantee at this confidence"}</p>
        </article>)}</div>
        {overview.predictionSavedAt && <p className={styles.updated}>Prediction evidence saved {timeText(overview.predictionSavedAt)} UK time.</p>}
        <div className={styles.guarantee}>
          <h3>Your ESAT score guarantee</h3>
          <p>A full refund to your original payment method if your official results fall <strong>more than 0.5 points below your locked predictions in at least two of your three modules</strong>, subject to verification and the guarantee terms.</p>
          <p>Only modules with Medium or High confidence at the lock date count. Low confidence and “Still building” modules do not count. A shortfall of exactly 0.5 points does not qualify.</p>
          <p><strong>{eligibleCount} of 3 modules {overview.locked ? "met" : "currently meet"} the confidence requirement.</strong> {eligibleCount < 2 && !overview.locked ? "Build more evidence before the lock date." : ""}</p>
          <p>After locking, your saved predictions and confidence levels stay fixed. You can continue practising.</p>
        </div>
        {overview.locked && today >= overview.plan.exam_date && <details className={styles.method}>
          <summary>Record your official results</summary>
          <p>Enter the results for this exam sitting and these same three modules. The score check is provisional until your official results and booking are verified.</p>
          <form onSubmit={saveResults}>
            <div className={styles.resultInputs}>{overview.plan.modules.map(module => <label key={module}>{module}
              <input type="number" min="1" max="9" step="0.1" required value={actualScores[module] ?? overview.results?.actual_scores[module] ?? ""} onChange={event => setActualScores(current => ({ ...current, [module]: event.target.value }))} />
            </label>)}</div>
            <button type="submit" className={styles.primary} disabled={saving}>{saving ? "Saving…" : "Save results and check scores"}</button>
          </form>
          {overview.results && <p role="status">{overview.results.assessment.meetsScoreCondition
            ? "Your entered results meet the score condition. Contact Thriving Scholars with your official result report to request verification and your refund."
            : `Your entered results show ${overview.results.assessment.missedCount} qualifying module shortfall(s). At least two are required.`}</p>}
        </details>}
      </>}
      <details className={styles.method}>
        <summary>How your module predictions work</summary>
        <p>Each recognised ESAT paper is scored module by module using that paper’s difficulty conversion. Each subject uses only its own test and Question Bank evidence to calculate its prediction, confidence and likely range. Shared papers and retakes count as one evidence family.</p>
        <p>Question Bank evidence starts contributing after 30 eligible unique questions in that module. Recognised test evidence can produce a prediction independently. Predictions below 3.5 remain “Still building”. Confidence reflects evidence depth, coverage and consistency.</p>
        <p>These are Thriving Scholars preparation estimates. Official ESAT results are reported separately for each module.</p>
      </details>
    </section>
  );
}
