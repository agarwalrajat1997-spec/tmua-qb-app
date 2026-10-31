import { useEffect, useState } from "react";
import { MathText } from "./MathHtml";
import {
  loadGuide,
  recordGuideEvent,
  skillName,
  type Guide,
  type Route,
} from "../lib/audited-content";
import type { Progress, Question } from "../types";
import taxonomy from "../data/shortcut-taxonomy.json";
import { isEligibleTmua } from "../lib/question-eligibility";
import { fetchStudioQuestion, studioUrl } from "../lib/api";

const classification: Record<string, string> = {
  material_shortcut: "Genuine shortcut",
  useful_ordinary_method: "Useful ordinary method",
  not_applicable: "Does not help here",
  unsafe_here: "Unsafe here",
  insufficient_information: "Not established",
};
export function QuestionGuide({
  question,
  submitted,
  selected,
  questions,
  progress,
  onNext,
}: {
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
  const [diagnosticId, setDiagnosticId] = useState("");
  const [response, setResponse] = useState("");
  const [compared, setCompared] = useState(false);
  const [confirmed, setConfirmed] = useState(false);
  const [prerequisites, setPrerequisites] = useState(false);
  const [routeNotice, setRouteNotice] = useState("");
  useEffect(() => {
    let active = true;
    void loadGuide(question)
      .then((g) => {
        if (active) setGuide(g);
      })
      .catch((e) => {
        if (active) setError(e.message);
      });
    return () => {
      active = false;
    };
  }, [question]);
  const log = (type: string, detail: Record<string, unknown> = {}) => {
    if (!recordGuideEvent(question, type, detail))
      setError("Your practice notes could not be saved on this device.");
  };
  if (!guide)
    return (
      <div className="audited-guide" role="status">
        {error || "Loading hints and skills…"}
      </div>
    );
  const core = guide.enrichment;
  const diagnosis = core.error_hypotheses.find(
    (e) => e.error_id === diagnosticId,
  );
  const option = core.option_analysis.find((o) => o.option_label === selected);
  const hypotheses =
    option && !option.is_correct && option.possible_error_ids.length
      ? core.error_hypotheses.filter((e) =>
          option.possible_error_ids.includes(e.error_id),
        )
      : core.error_hypotheses;
  const label = (id: string) => skillName(guide, id);
  function targetFor(route: Route) {
    return questions.find(
      (q) =>
        q.qid === route.target_qid &&
        q.source_sha256 === route.target_source_sha256 &&
        q.content_version === route.target_content_version,
    );
  }
  function selectDiagnostic(id: string) {
    setDiagnosticId(id);
    setResponse("");
    setCompared(false);
    setConfirmed(false);
    setPrerequisites(false);
    setRouteNotice("");
  }
  async function openRoute(route: Route) {
    if (!isEligibleTmua(route.target_qid)) {
      setRouteNotice(
        "This question has been removed from the active TMUA bank. Choose another practice question.",
      );
      return;
    }
    const seen = Object.entries(progress).some(
      ([key, value]) =>
        key.startsWith(`tmua:${route.target_qid}`) &&
        (value.submitted || value.reviewedAt || value.solutionViewed),
    );
    if (seen) {
      setRouteNotice(
        "You have already tried this question. Use the question bank to choose fresh practice.",
      );
      return;
    }
    setRouteNotice("Opening the reviewed follow-up…");
    try {
      let target = targetFor(route);
      if (!target) {
        const { question: record } = await fetchStudioQuestion(
          route.target_qid, route.target_content_version,
        );
        if (
          record.qid !== route.target_qid ||
          record.source_sha256 !== route.target_source_sha256 ||
          record.content_version !== route.target_content_version ||
          !record.answer_verified
        )
          throw Error(
            "The reviewed follow-up version does not match. Please refresh the app.",
          );
        target = record;
      }
      log("followup_opened", {
        routeId: route.route_id,
        targetQid: target.qid,
        targetVersion: target.content_version,
        evidence: "learner_self_report",
        diagnosticId,
        prerequisiteAndExposureCheck: true,
      });
      onNext(target);
    } catch (e) {
      setRouteNotice((e as Error).message);
    }
  }
  const relevantRoutes = guide.routes.filter(
    (r) =>
      isEligibleTmua(r.target_qid) &&
      diagnosis &&
      r.error_ids.includes(diagnosis.error_id),
  );
  return (
    <section className="audited-guide" aria-label="Audited question guide">
      <div className="guide-heading">
        <strong>Hints & skills</strong>
        <span>Audited collection</span>
      </div>
      {error && <p role="alert">{error}</p>}
      <p className="guide-muted">
        A little help when you need it. Your working can be as concise as you
        like.
      </p>
      {core.hints.slice(0, hintCount).map((hint, i) => (
        <div className="guide-hint" key={hint.hint_id}>
          <strong>Hint {i + 1}</strong>
          <MathText text={hint.text} inline={false} />
        </div>
      ))}
      {hintCount < core.hints.length && (
        <button
          className="secondary"
          onClick={() => {
            log("hint_opened", { hintId: core.hints[hintCount].hint_id });
            setHintCount(hintCount + 1);
          }}
        >
          Show {hintCount ? "next" : "first"} hint
        </button>
      )}
      <details>
        <summary>Skills in this question · {core.skills.length}</summary>
        {core.skills.map((skill) => (
          <div className="guide-item" key={skill.skill_id}>
            <strong>{label(skill.skill_id)}</strong>
            <small>{skill.role}</small>
            <MathText text={skill.learning_objective} inline={false} />
            {submitted && (
              <MathText text={skill.evidence_in_solution} inline={false} />
            )}
          </div>
        ))}
      </details>
      {core.accessibility.diagram_description && (
        <details>
          <summary>Diagram description</summary>
          <MathText
            text={core.accessibility.diagram_description}
            inline={false}
          />
        </details>
      )}
      {submitted && (
        <>
          {guide.route_candidates && guide.route_candidates.length > 0 && (
            <p className="guide-muted">
              Follow-up candidates are saved in this audit. They need the
              recorded review checks before they can be recommended.
            </p>
          )}
          <a
            href={
              studioUrl("guide", { qid: question.qid, contentVersion: question.content_version })
            }
            download
          >
            Download the saved audit details
          </a>
          <details>
            <summary>Method, checks & useful alternatives</summary>
            <MathText text={core.ordinary_method} inline={false} />
            {core.solution_steps.map((step) => (
              <div className="guide-item" key={step.step_id}>
                <MathText text={step.explanation} inline={false} />
                <small>
                  <MathText text={step.check} />
                </small>
              </div>
            ))}
            <h4>Domain & case checks</h4>
            {core.domain_case_checks.map((check, i) => (
              <MathText key={i} text={check} inline={false} />
            ))}
            {core.useful_alternatives.map((a, i) => (
              <div className="guide-item" key={i}>
                <strong>{a.method}</strong>
                <MathText text={a.concise_justification} inline={false} />
                <MathText text={a.when_useful} inline={false} />
              </div>
            ))}
          </details>
          <details>
            <summary>The 10 shortcut checks</summary>
            <p className="guide-muted">
              Only a material saving over the best ordinary method earns a
              shortcut label.
            </p>
            {core.shortcut_assessments.map((a, i) => (
              <details className="guide-trick" key={a.shortcut_id}>
                <summary>
                  {taxonomy.find((t) => t.id === a.shortcut_id)?.name ??
                    a.shortcut_id}{" "}
                  · {classification[a.classification] ?? a.classification}
                </summary>
                <MathText text={a.method_here} inline={false} />
                <MathText text={a.saving_judgment} inline={false} />
                <p>
                  <strong>Baseline:</strong>{" "}
                  <MathText text={a.best_ordinary_baseline} />
                </p>
                <p>
                  <strong>Work avoided:</strong>{" "}
                  <MathText text={a.work_avoided} />
                </p>
                <MathText
                  text={
                    Array.isArray(a.conditions_checked)
                      ? a.conditions_checked.join("\n")
                      : String(a.conditions_checked)
                  }
                  inline={false}
                />
              </details>
            ))}
          </details>
          {option && (
            <details>
              <summary>Understand option {selected}</summary>
              <MathText text={option.why} inline={false} />
              <MathText text={option.diagnosis_limit} inline={false} />
            </details>
          )}
          <details>
            <summary>Find the step to practise next</summary>
            <p>
              A chosen option alone does not tell us why an error happened.
              Compare your working with a check below.
            </p>
            <label className="guide-label">
              Which step would you like to check?
              <select
                value={diagnosticId}
                onChange={(e) => selectDiagnostic(e.target.value)}
              >
                <option value="">Choose a check…</option>
                {hypotheses.map((h) => (
                  <option key={h.error_id} value={h.error_id}>
                    {h.description}
                  </option>
                ))}
              </select>
            </label>
            {diagnosis && (
              <div className="guide-diagnostic">
                <MathText text={diagnosis.diagnostic_probe} inline={false} />
                <label className="guide-label">
                  Your reasoning
                  <textarea
                    value={response}
                    onChange={(e) => {
                      setResponse(e.target.value);
                      setCompared(false);
                      setConfirmed(false);
                    }}
                    rows={3}
                    maxLength={2000}
                  />
                </label>
                <button
                  className="secondary"
                  disabled={!response.trim()}
                  onClick={() => {
                    log("diagnostic_probe_answered", {
                      errorId: diagnosis.error_id,
                      response,
                    });
                    setCompared(true);
                  }}
                >
                  Compare with the check
                </button>
                {compared && (
                  <>
                    <div className="guide-hint">
                      <MathText
                        text={diagnosis.expected_probe_answer}
                        inline={false}
                      />
                      <MathText
                        text={diagnosis.confirmation_rule}
                        inline={false}
                      />
                      <MathText text={diagnosis.remediation} inline={false} />
                    </div>
                    <label className="guide-checkbox">
                      <input
                        type="checkbox"
                        checked={confirmed}
                        onChange={(e) => {
                          setConfirmed(e.target.checked);
                          log("diagnostic_self_report", {
                            errorId: diagnosis.error_id,
                            confirmed: e.target.checked,
                            response,
                          });
                        }}
                      />
                      This matches the mistake in my working.
                    </label>
                    <p className="guide-muted">
                      This is your own check, not an automatic skill diagnosis.
                    </p>
                    {confirmed && (
                      <>
                        <label className="guide-checkbox">
                          <input
                            type="checkbox"
                            checked={prerequisites}
                            onChange={(e) => setPrerequisites(e.target.checked)}
                          />
                          I meet the conditions below and have not recently
                          practised this question or seen its solution.
                        </label>
                        {relevantRoutes.map((route) => (
                          <div className="guide-item" key={route.route_id}>
                            <MathText
                              text={route.why_content_matches}
                              inline={false}
                            />
                            <p className="guide-muted">
                              {route.target_qid} · {route.relationship}
                            </p>
                            <MathText
                              text={route.selection_condition}
                              inline={false}
                            />
                            <MathText
                              text={route.diagnostic_gate.evidence_needed}
                              inline={false}
                            />
                            <MathText
                              text={route.diagnostic_gate.confirmation_rule}
                              inline={false}
                            />
                            <button
                              className="secondary"
                              disabled={!prerequisites}
                              onClick={() => void openRoute(route)}
                            >
                              Practise this skill
                            </button>
                          </div>
                        ))}
                        {!relevantRoutes.length && (
                          <p>
                            No verified follow-up is available for this check
                            yet. Rework the step above, then choose fresh
                            practice in the question bank.
                          </p>
                        )}
                      </>
                    )}
                  </>
                )}
              </div>
            )}
            {routeNotice && <p role="status">{routeNotice}</p>}
          </details>
        </>
      )}
      <small className="guide-muted">
        Hints and self-check notes are saved on this device.
      </small>
    </section>
  );
}
