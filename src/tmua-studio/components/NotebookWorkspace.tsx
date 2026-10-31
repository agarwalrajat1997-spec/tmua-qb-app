import {
  useCallback,
  useEffect,
  useRef,
  useState,
  useSyncExternalStore,
} from "react";
import {
  FileText,
  Plus,
  LockKeyhole,
  Sparkles,
  ShieldCheck,
} from "lucide-react";
import {
  cleanTopic,
  type Question,
  type Progress,
  type Feedback,
} from "../types";
import { notebooks } from "../lib/notebooks";
import { InkBoard, type BoardHandle } from "./InkBoard";
import { MathHtml, MathText } from "./MathHtml";
import { scheduleFeedbackWarmup } from "../lib/warm-feedback";
import { ThinkingBrand } from "./ThinkingBrand";
import { UsefulMethods } from "./UsefulMethods";
import { loadGuide } from "../lib/audited-content";
import { studentMethods, studentErrorMessage, type StudentMethod } from "../lib/student-content";
import { recommendNext } from "../lib/next-question";
import {
  subscribeSync,
  syncState,
  syncLabel,
  flushCloud,
  resolveCloudConflict,
} from "../lib/cloud-storage";

const noRevision = () => {};
export function NotebookWorkspace({
  scope,
  question,
  isMock,
  readOnly,
  online,
  aiReady,
  onConnect,
  onStatus,
  onReviewComplete,
  questions = [],
  progress = {},
  onNextQuestion,
}: {
  scope: string;
  question: Question;
  isMock: boolean;
  readOnly: boolean;
  online: boolean;
  aiReady: boolean;
  onConnect: () => void;
  onStatus: (text: string) => void;
  onReviewComplete: (feedback?: Feedback) => void;
  questions?: Question[];
  progress?: Record<string, Progress>;
  onNextQuestion?: (question: Question) => void;
}) {
  const entry = useRef(crypto.randomUUID()),
    board = useRef<BoardHandle>(null);
  const [error, setError] = useState("");
  const [methods, setMethods] = useState<StudentMethod[]>([]);
  const [reviewAction, setReviewAction] = useState<"check" | "retry" | null>(
    null,
  );
  const subscribe = useCallback(
    (fn: () => void) => notebooks.subscribe(scope, fn),
    [scope],
  );
  const read = useCallback(() => notebooks.get(scope), [scope]);
  const notebook = useSyncExternalStore(subscribe, read, () => undefined);
  useEffect(() => (isMock ? undefined : scheduleFeedbackWarmup()), [isMock]);
  useEffect(() => {
    let active = true;
    setMethods([]);
    if (question.audited) void loadGuide(question).then((guide) => {
      if (active) setMethods(studentMethods(guide.enrichment.shortcut_assessments));
    }).catch(() => {});
    return () => { active = false; };
  }, [question]);
  useEffect(() => {
    void notebooks
      .open(scope, entry.current, {
        exam: question.exam,
        qid: question.qid,
        contentVersion: question.content_version,
      })
      .catch((e) => setError(e.message));
  }, [scope, question.exam, question.qid, question.content_version]);
  const run = (task: Promise<unknown>, padId?: string) =>
    void task.catch((e) => {
      const message = (e as Error).message;
      // Review failures already persisted on their pad have one display owner.
      const saved = notebooks.get(scope)?.pads.find((p) => p.id === padId);
      if (!padId || saved?.error !== message) setError(message);
    });
  const pad =
    notebook?.pads.find((p) => p.id === notebook.active) ??
    notebook?.pads.at(-1);
  const solutionActive =
    !isMock && notebook?.active === "solution" && notebook.solutionUnlocked;
  useEffect(() => setError(""), [scope, notebook?.active]);
  const retryConfirmed =
    pad?.recovery?.requestId === pad?.requestId &&
    pad?.recovery?.status === "failed" &&
    pad.recovery.retryable === true;
  const pending =
    pad && ["preparing", "queued", "reviewing"].includes(pad.status);
  const locked = readOnly || (!!pad && pad.status !== "draft");
  const boardKey = `board:${pad?.storageKey ?? scope}`;
  const notebookKey = `notebook:${scope}`;
  const cloudState = useSyncExternalStore(
    subscribeSync,
    () => {
      const states = [syncState(boardKey), syncState(notebookKey)];
      return states.includes("conflict")
        ? "conflict"
        : states.includes("offline")
          ? "offline"
          : states.includes("saving")
            ? "saving"
            : states.every((s) => s === "synced")
              ? "synced"
              : "device";
    },
    () => "device" as const,
  );
  const next =
    pad?.status === "complete" && !isMock
      ? recommendNext(question, questions, progress, pad.feedback)
      : null;
  useEffect(() => {
    if (
      pad?.status === "queued" ||
      pad?.status === "reviewing" ||
      pad?.status === "complete"
    ) {
      void flushCloud(boardKey);
      void flushCloud(`notebook:${scope}`);
    }
  }, [pad?.status, boardKey, scope]);
  function submit() {
    if (isMock || !pad || pad.status !== "draft") return;
    if (!aiReady) {
      onConnect();
      return;
    }
    const handle = board.current;
    if (!handle?.hasWork()) {
      setError("Write your working or add a photo first.");
      return;
    }
    setError("");
    run(
      notebooks
        .submit(
          scope,
          pad.id,
          () => handle.freeze(),
          {
            exam: question.exam,
            qid: question.qid,
            contentVersion: question.content_version,
          },
          () => handle.releaseUnsubmitted(),
        )
        .finally(() =>
          onReviewComplete(
            notebooks.get(scope)?.pads.find((p) => p.id === pad.id)?.feedback,
          ),
        ),
      pad.id,
    );
  }
  function retryReview() {
    if (isMock || readOnly || !online || !pad || reviewAction) return;
    if (!aiReady) {
      onConnect();
      return;
    }
    const handle = board.current;
    if (!handle) return;
    setError("");
    setReviewAction("retry");
    run(
      notebooks
        .retry(scope, pad.id, () => handle.snapshot(), {
          exam: question.exam,
          qid: question.qid,
          contentVersion: question.content_version,
        })
        .then(() => {
          const saved = notebooks.get(scope)?.pads.find((p) => p.id === pad.id);
          if (saved?.status === "complete") onReviewComplete(saved.feedback);
        })
        .finally(() => setReviewAction(null)),
      pad.id,
    );
  }
  function checkSavedReview() {
    if (!pad || reviewAction || !online) return;
    setError("");
    setReviewAction("check");
    run(
      notebooks
        .recover(scope, pad.id)
        .then(() => {
          const saved = notebooks.get(scope)?.pads.find((p) => p.id === pad.id);
          if (saved?.status === "complete") onReviewComplete(saved.feedback);
        })
        .finally(() => setReviewAction(null)),
      pad.id,
    );
  }
  if (!notebook || !pad)
    return (
      <div className="notebook-loading" role="status">
        {error || "Opening your saved pad…"}
      </div>
    );
  return (
    <div className="notebook-workspace">
      <div
        className="notebook-tabs"
        role="tablist"
        aria-label="Saved working pads"
      >
        {!isMock && (
          <ThinkingBrand
            active={notebook.pads.some((p) =>
              ["preparing", "queued", "reviewing"].includes(p.status),
            )}
          />
        )}
        {notebook.pads.map((p, i) => (
          <button
            key={p.id}
            role="tab"
            aria-selected={!solutionActive && pad.id === p.id}
            aria-label={`Pad ${i + 1}${p.status === "draft" ? "" : `, ${{
              preparing: "preparing", queued: "waiting", reviewing: "reviewing",
              complete: "feedback ready", failed: "needs attention",
            }[p.status]}`}`}
            className={!solutionActive && pad.id === p.id ? "selected" : ""}
            onClick={() => run(notebooks.select(scope, p.id))}
          >
            {i + 1}
            {p.status !== "draft" && (
              <span aria-hidden="true" className={`pad-dot ${p.status}`} />
            )}
          </button>
        ))}
        {!isMock && notebook.solutionUnlocked && (
          <button
            role="tab"
            aria-selected={!!solutionActive}
            className={
              solutionActive ? "selected solution-tab" : "solution-tab"
            }
            onClick={() => run(notebooks.select(scope, "solution"))}
          >
            <FileText size={15} />
            Solution
          </button>
        )}
        {!isMock && !readOnly && notebook.visits > 1 && (
          <button
            className="fresh-pad"
            aria-label="Start a fresh attempt pad"
            onClick={() => run(notebooks.fresh(scope))}
          >
            <Plus size={15} />
            Fresh pad
          </button>
        )}
      </div>
      {error && (
        <div className="inline-error" role="alert">
          {studentErrorMessage(error)}
        </div>
      )}
      {solutionActive ? (
        <section
          className="solution-pad"
          role="tabpanel"
          aria-label="Worked solution"
        >
          <div className="solution-paper">
            <span className="solution-eyebrow">
              THRIVING SCHOLARS · WORKED SOLUTION
            </span>
            <h2>Understand the complete method.</h2>
            {notebook.solution ? (
              <>
                <p className="solution-answer">
                  Answer <MathText text={notebook.solution.answer} />
                </p>
                <MathHtml html={notebook.solution.solutionHtml} />
                <UsefulMethods methods={methods} />
                <p className="solution-provenance">
                  From the question bank. Return to a numbered pad for feedback
                  on your own working.
                </p>
              </>
            ) : notebook.solutionError ? (
              <>
                <p role="alert">{studentErrorMessage(notebook.solutionError)}</p>
                <button
                  className="secondary"
                  onClick={() =>
                    run(
                      notebooks.loadSolution(
                        scope,
                        question.exam,
                        question.qid,
                        question.content_version,
                      ),
                    )
                  }
                >
                  Load solution
                </button>
              </>
            ) : (
              <p role="status">Loading the solution…</p>
            )}
          </div>
        </section>
      ) : (
        <InkBoard
          key={pad.id}
          storageKey={pad.storageKey}
          ref={board}
          readOnly={locked}
          feedback={isMock ? null : (pad.feedback ?? null)}
          checking={!!pending}
          reviewStage={
            pad.status === "preparing" ||
            pad.status === "queued" ||
            pad.status === "reviewing"
              ? pad.status
              : undefined
          }
          reviewError={pad.error}
          onRevision={noRevision}
          onStatus={onStatus}
          allowReview={!isMock}
          animateFeedback={pad.status === "complete"}
          onClarify={async (regionIds, text) => {
            if (!board.current)
              throw Error("Reopen this pad before clarifying.");
            await notebooks.clarify(
              scope,
              pad.id,
              regionIds,
              text,
              () => board.current!.snapshot(),
              {
                exam: question.exam,
                qid: question.qid,
                contentVersion: question.content_version,
              },
            );
            onReviewComplete(
              notebooks.get(scope)?.pads.find((p) => p.id === pad.id)?.feedback,
            );
          }}
        />
      )}
      <div className="writing-footer">
        <span>
          <ShieldCheck size={15} />
          {isMock
            ? "Independent working · AI is off during tests"
            : notebook.pads.some((p) =>
                  ["preparing", "queued", "reviewing"].includes(p.status),
                )
              ? "Review continues while you use other pads or questions."
              : locked
                ? "Submitted working is saved and read-only."
                : syncLabel(cloudState)}
        </span>
        {!solutionActive && (
          <button
            className="primary check-working"
            disabled={isMock || locked || !online}
            onClick={submit}
          >
            {locked ? <LockKeyhole size={15} /> : <Sparkles size={17} />}{" "}
            {pending
              ? pad.status === "queued"
                ? "Waiting…"
                : "Reviewing…"
              : locked
                ? "Submitted"
                : "Submit working"}
          </button>
        )}
        {solutionActive && (
          <button
            className="secondary"
            onClick={() => run(notebooks.select(scope, pad.id))}
          >
            {pending
              ? "Review in progress…"
              : pad.status === "complete"
                ? "View feedback"
                : "Back to working"}
          </button>
        )}
      </div>
      {!isMock && pad.status === "failed" && pad.requestId && (
        <div className="cloud-detail">
          <button
            className="text-button"
            disabled={!online || !!reviewAction}
            onClick={checkSavedReview}
          >
            {reviewAction === "check"
              ? "Checking saved review…"
              : "Check saved review"}
          </button>
          {!readOnly && !solutionActive && pad.source && retryConfirmed && (
            <>
              <button
                className="text-button"
                disabled={!online || !!reviewAction}
                onClick={retryReview}
              >
                {reviewAction === "retry"
                  ? "Checking before retry…"
                  : "Retry review"}
              </button>
              <small>
                Try again when you’re ready. Your saved working stays unchanged.
              </small>
            </>
          )}
          {!retryConfirmed && (
            <small>
              Check whether your feedback is ready before starting another review.
            </small>
          )}
        </div>
      )}
      {pad.recovery &&
        pad.recovery.requestId === pad.requestId &&
        pad.recovery.previousReview && (
          <div className="cloud-detail" role="status">
            {pad.recovery.previousReview.summary
              ? `An earlier saved review said: ${pad.recovery.previousReview.summary}`
              : pad.recovery.previousReview.error
                ? studentErrorMessage(pad.recovery.previousReview.error)
                : "The earlier review has no saved feedback yet."}{" "}
            Check your latest review for the most recent feedback.
          </div>
        )}
      <div className="cloud-detail" role="status">
        {locked ? syncLabel(cloudState) : ""}
        {cloudState === "conflict" && (
          <>
            {" "}
            ·{" "}
            <button
              onClick={() =>
                run(
                  Promise.all(
                    [boardKey, notebookKey]
                      .filter((k) => syncState(k) === "conflict")
                      .map((k) => resolveCloudConflict(k, "device")),
                  ).then(() => {}),
                )
              }
            >
              Save this copy to my account
            </button>
          </>
        )}
      </div>
      {next && onNextQuestion && (
        <div className="next-practice">
          <span>
            {next.reason}
            <small>{cleanTopic(next.question.topic)}</small>
          </span>
          <button
            className="secondary"
            onClick={() => onNextQuestion(next.question)}
          >
            Next question
          </button>
        </div>
      )}
    </div>
  );
}
