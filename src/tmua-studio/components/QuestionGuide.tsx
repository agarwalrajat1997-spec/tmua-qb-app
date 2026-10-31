import { useEffect, useState } from "react";
import { MathText } from "./MathHtml";
import { UsefulMethods } from "./UsefulMethods";
import { loadGuide, recordGuideEvent, skillName, type Guide } from "../lib/audited-content";
import { studentMethods, studentText, studentErrorMessage } from "../lib/student-content";
import type { Progress, Question } from "../types";

export function QuestionGuide({ question, submitted, selected }: {
  question: Question;
  submitted: boolean;
  selected?: string;
  questions: Question[];
  progress: Record<string, Progress>;
  onNext: (q: Question) => void;
}) {
  const [guide, setGuide] = useState<Guide>();
  const [error, setError] = useState("");
  const [hintCount, setHintCount] = useState(0);
  const [checkId, setCheckId] = useState("");
  const [response, setResponse] = useState("");
  const [compared, setCompared] = useState(false);
  useEffect(() => {
    let active = true;
    void loadGuide(question).then((value) => { if (active) setGuide(value); })
      .catch((reason) => { if (active) setError(studentErrorMessage(reason)); });
    return () => { active = false; };
  }, [question]);
  const log = (type: string, detail: Record<string, unknown> = {}) => {
    if (!recordGuideEvent(question, type, detail))
      setError("Your practice notes could not be saved on this device.");
  };
  if (!guide) return <div className="audited-guide" role="status">{error || "Loading hints…"}</div>;
  const core = guide.enrichment;
  const methods = studentMethods(core.shortcut_assessments);
  const option = core.option_analysis.find((entry) => entry.option_label === selected);
  const checks = option && !option.is_correct && option.possible_error_ids.length
    ? core.error_hypotheses.filter((entry) => option.possible_error_ids.includes(entry.error_id))
    : core.error_hypotheses;
  const check = checks.find((entry) => entry.error_id === checkId);
  return <section className="audited-guide" aria-label="Hints and learning support">
    <div className="guide-heading"><strong>A little help</strong></div>
    {error && <p role="alert">{studentErrorMessage(error)}</p>}
    {core.hints.slice(0, hintCount).map((hint, index) => <div className="guide-hint" key={hint.hint_id}>
      <strong>Hint {index + 1}</strong><MathText text={studentText(hint.text)} inline={false} />
    </div>)}
    {hintCount < core.hints.length && <button className="secondary" onClick={() => {
      log("hint_opened", { hintId: core.hints[hintCount].hint_id }); setHintCount(hintCount + 1);
    }}>Show {hintCount ? "next" : "first"} hint</button>}
    {core.skills.length > 0 && <details>
      <summary>What this question practises</summary>
      {core.skills.map((skill) => <div className="guide-item" key={skill.skill_id}>
        <strong>{studentText(skillName(guide, skill.skill_id))}</strong>
        <MathText text={studentText(skill.learning_objective)} inline={false} />
        {submitted && <MathText text={studentText(skill.evidence_in_solution)} inline={false} />}
      </div>)}
    </details>}
    {core.accessibility.diagram_description && <details>
      <summary>Diagram description</summary>
      <MathText text={studentText(core.accessibility.diagram_description)} inline={false} />
    </details>}
    {submitted && <>
      <details>
        <summary>Work through the method</summary>
        <MathText text={studentText(core.ordinary_method)} inline={false} />
        {core.solution_steps.map((step) => <div className="guide-item" key={step.step_id}>
          <MathText text={studentText(step.explanation)} inline={false} />
          {step.check && <small><MathText text={studentText(step.check)} /></small>}
        </div>)}
        {core.domain_case_checks.length > 0 && <details>
          <summary>Things to check</summary>
          {core.domain_case_checks.map((text, index) => <MathText key={index} text={studentText(text)} inline={false} />)}
        </details>}
      </details>
      {methods.length > 0 && <details>
        <summary>Other useful approaches</summary><UsefulMethods methods={methods} />
      </details>}
      {option && <details>
        <summary>Understand answer {selected}</summary>
        <MathText text={studentText(option.why)} inline={false} />
      </details>}
      {checks.length > 0 && <details>
        <summary>Check a tricky step</summary>
        <p className="guide-muted">Choose a short check and compare it with your own working.</p>
        <label className="guide-label">Choose a check
          <select value={checkId} onChange={(event) => {
            setCheckId(event.target.value); setResponse(""); setCompared(false);
          }}>
            <option value="">Choose a check…</option>
            {checks.map((entry, index) => <option key={entry.error_id} value={entry.error_id}>Check {index + 1}</option>)}
          </select>
        </label>
        {check && <div className="guide-diagnostic">
          <MathText text={studentText(check.diagnostic_probe)} inline={false} />
          <label className="guide-label">Your reasoning<textarea value={response} rows={3} maxLength={2000}
            onChange={(event) => { setResponse(event.target.value); setCompared(false); }} /></label>
          <button className="secondary" disabled={!response.trim()} onClick={() => {
            log("diagnostic_probe_answered", { errorId: check.error_id, response }); setCompared(true);
          }}>Compare your reasoning</button>
          {compared && <div className="guide-hint">
            <MathText text={studentText(check.expected_probe_answer)} inline={false} />
            <MathText text={studentText(check.remediation)} inline={false} />
          </div>}
        </div>}
      </details>}
    </>}
  </section>;
}
