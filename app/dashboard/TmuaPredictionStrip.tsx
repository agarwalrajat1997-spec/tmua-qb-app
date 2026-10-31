"use client";

import {
  useEffect,
  useId,
  useState,
} from "react";

import ExamCountdown from "@/app/_components/ExamCountdown";
import styles from "./TmuaPredictionStrip.module.css";

// Internal model identity. Visible student-facing label begins "You rank".
const PREPARATION_RANK_MODEL_NAME = "Preparation Rank";

// Display-only calibration for sample-bias adjustment.
// Authoritative rank/cohort calculations remain unchanged.
const PREPARATION_RANK_DISPLAY_MULTIPLIER = 2.0000;
const PREPARATION_COHORT_DISPLAY_MULTIPLIER = 3.0000;

function calibratedDisplayInteger(
  value: number,
  multiplier: number,
): number {
  return Math.max(
    1,
    Math.round(value * multiplier),
  );
}

type PredictorOverview = {
  modelVersion: string;

  status:
    | "predicted"
    | "insufficient_evidence";

  score:
    | number
    | null;

  lowerBound:
    | number
    | null;

  upperBound:
    | number
    | null;

  confidence:
    | "low"
    | "medium"
    | "high"
    | null;

  testEvidenceCount:
    number;

  independentTestCount:
    number;

  qbUniqueQuestions:
    number;

  qbTopicCoverage:
    number;

  calculatedAt:
    string;
};

type PreparationRankOverview = {
  modelVersion:
    string;

  hasGenuinePreparationEvidence:
    boolean;

  score:
    | number
    | null;

  rank:
    | number
    | null;

  cohortSize:
    number;

  components:
    | {
        performance:
          number;

        breadth:
          number;

        evidenceDepth:
          number;

        recentActivity:
          number;

        consistency:
          number;

        recovery:
          number;
      }
    | null;

  calculatedAt:
    string;
};

type CountdownOverview = {
  daysToTmua:
    number;

  examDate:
    string;

  examDateLabel:
    string;
};

type OverviewResponse = {
  viewerId?: string;
  ok:
    boolean;

  predictor?:
    PredictorOverview;

  preparationRank?:
    PreparationRankOverview;

  countdown?:
    CountdownOverview;

  error?:
    string;
};

function scoreText(
  value: number,
): string {
  return value
    .toFixed(1);
}

function confidenceText(
  value:
    PredictorOverview["confidence"],
): string {
  if (!value) {
    return "";
  }

  return (
    value.charAt(0)
      .toUpperCase() +
    value.slice(1)
  );
}

type InfoTooltipProps = {
  label: string;
  children: React.ReactNode;
};

function InfoTooltip({
  label,
  children,
}: InfoTooltipProps) {
  const tooltipId = useId();

  return (
    <span className={styles.infoWrap}>
      <button
        type="button"
        className={styles.infoButton}
        aria-label={`About ${label}`}
        aria-describedby={tooltipId}
      >
        i
      </button>

      <span
        id={tooltipId}
        role="tooltip"
        className={styles.tooltip}
      >
        <strong className={styles.tooltipTitle}>
          {label}
        </strong>

        <span className={styles.tooltipText}>
          {children}
        </span>
      </span>
    </span>
  );
}
type OverviewRefreshDependencies = {
  fetcher: typeof fetch;
  schedule: (callback: () => void, delay: number) => number;
  cancel: (timer: number) => void;
  now: () => number;
  onOverview: (overview: OverviewResponse | null) => void;
  onSettled: () => void;
};

// One controller owns the current viewer and request generation. A saved answer
// invalidates an older read, even when that read cannot be cancelled in time.
export function createTmuaOverviewRefresh(deps: OverviewRefreshDependencies) {
  let disposed = false, blocked = false, started = false;
  let viewerId: string | null = null;
  let revision = 0, pending = false, dueAt = 0;
  let timer: number | null = null;
  let active: AbortController | null = null;
  let cancelActive: (() => void) | null = null;
  let lastFocusRefresh = Number.NEGATIVE_INFINITY;
  let unverifiedSaveSequence = 0;
  const seen = new Set<string>();
  const unverifiedSaves = new Map<string, number>();

  function remember(set: Set<string>, value: string) {
    set.add(value);
    if (set.size > 128) set.delete(set.values().next().value as string);
  }
  function clearTimer() {
    if (timer !== null) deps.cancel(timer);
    timer = null;
  }
  function queue(delay = 500) {
    if (disposed || blocked) return;
    pending = true;
    dueAt = deps.now() + delay;
    clearTimer();
    timer = deps.schedule(() => { timer = null; void run(); }, delay);
  }
  function accountChanged() {
    blocked = true;
    pending = false;
    clearTimer();
    unverifiedSaves.clear();
    deps.onOverview(null);
  }
  async function run() {
    if (disposed || blocked || active || !pending) return;
    pending = false;
    const requestRevision = revision;
    const expectedViewer = viewerId;
    const unverifiedAtStart = new Map(unverifiedSaves);
    const request = new AbortController();
    active = request;
    let deadline: number | null = null;
    let rejectDeadline: (error: Error) => void = () => {};
    const deadlineFailure = new Promise<never>((_resolve, reject) => {
      rejectDeadline = reject;
      deadline = deps.schedule(() => {
        deadline = null;
        request.abort();
        reject(new Error("Overview request timed out"));
      }, 30_000);
    });
    cancelActive = () => {
      if (deadline !== null) deps.cancel(deadline);
      deadline = null;
      request.abort();
      rejectDeadline(new Error("Overview request cancelled"));
    };
    try {
      const query = expectedViewer ? `?expectedUserId=${encodeURIComponent(expectedViewer)}` : "";
      const endpoint = "/api/tmua/overview";
      const read = (async () => {
        const response = await deps.fetcher(endpoint + query, {
          method: "GET", cache: "no-store", credentials: "same-origin", signal: request.signal,
        });
        return { response, body: response.ok ? await response.json() as OverviewResponse : null };
      })();
      // Bound both response headers and body decoding, even if fetch ignores abort.
      const { response, body } = await Promise.race([read, deadlineFailure]);
      if (disposed) return;
      if ([401, 403, 409].includes(response.status)) { accountChanged(); return; }
      if (!response.ok) return;
      if (disposed || blocked) return;
      if (!body?.ok || !body.predictor || typeof body.viewerId !== "string" || !body.viewerId) return;
      if (expectedViewer && body.viewerId !== expectedViewer) { accountChanged(); return; }
      viewerId = body.viewerId;
      const savedDuringVerification = (unverifiedSaves.get(viewerId) ?? 0) > (unverifiedAtStart.get(viewerId) ?? 0);
      // A first verified response can dismiss a queued notification for a
      // different viewer, while preserving focus refreshes or matching saves.
      if (!expectedViewer && !savedDuringVerification && unverifiedSaves.size > 0 && requestRevision === revision) {
        pending = false;
        clearTimer();
      }
      unverifiedSaves.clear();
      if (savedDuringVerification) { revision += 1; queue(); }
      if (requestRevision === revision) deps.onOverview(body);
    } catch {
      // Keep the last verified overview during a temporary network failure.
      // No timer retries or polling: the next saved answer/focus can retry.
    } finally {
      if (deadline !== null) deps.cancel(deadline);
      if (active === request) { active = null; cancelActive = null; }
      if (!disposed) {
        deps.onSettled();
        if (pending && !blocked) queue(Math.max(0, dueAt - deps.now()));
      }
    }
  }
  return {
    start() {
      if (started || disposed || blocked) return;
      started = true;
      lastFocusRefresh = deps.now();
      pending = true;
      void run();
    },
    saved(detail: unknown) {
      if (disposed || blocked || !detail || typeof detail !== "object") return;
      const event = detail as { viewerId?: unknown; submissionId?: unknown };
      if (typeof event.viewerId !== "string" || !event.viewerId || event.viewerId.length > 128 ||
          typeof event.submissionId !== "string" || !event.submissionId || event.submissionId.length > 256) return;
      if (viewerId && event.viewerId !== viewerId) return;
      const identity = `${event.viewerId}:${event.submissionId}`;
      if (seen.has(identity)) return;
      remember(seen, identity);
      if (!viewerId) {
        unverifiedSaves.set(event.viewerId, ++unverifiedSaveSequence);
        if (unverifiedSaves.size > 128) unverifiedSaves.delete(unverifiedSaves.keys().next().value as string);
        queue();
        return;
      }
      revision += 1;
      queue();
    },
    refresh() {
      if (disposed || blocked || deps.now() - lastFocusRefresh < 15_000) return;
      lastFocusRefresh = deps.now();
      revision += 1;
      queue();
    },
    dispose() {
      disposed = true;
      pending = false;
      clearTimer();
      cancelActive?.();
      unverifiedSaves.clear();
    },
  };
}

export default function TmuaPredictionStrip() {
  const [
    overview,
    setOverview,
  ] =
    useState<
      OverviewResponse |
      null
    >(null);

  const [
    loaded,
    setLoaded,
  ] =
    useState(false);

  useEffect(
    () => {
      const controller = createTmuaOverviewRefresh({
        fetcher: fetch,
        schedule: (callback, delay) => window.setTimeout(callback, delay),
        cancel: timer => window.clearTimeout(timer),
        now: Date.now,
        onOverview: setOverview,
        onSettled: () => setLoaded(true),
      });
      const saved = (event: Event) => controller.saved((event as CustomEvent).detail);
      const refresh = () => { if (!document.hidden) controller.refresh(); };
      window.addEventListener("ts-tmua-attempt-saved", saved);
      window.addEventListener("focus", refresh);
      document.addEventListener("visibilitychange", refresh);
      controller.start();

      return () => {
        controller.dispose();
        window.removeEventListener("ts-tmua-attempt-saved", saved);
        window.removeEventListener("focus", refresh);
        document.removeEventListener("visibilitychange", refresh);
      };
    },
    [],
  );

  if (
    !loaded ||
    !overview?.predictor
  ) {
    return null;
  }

  const predictor =
    overview.predictor;

  const preparationRank =
    overview.preparationRank ??
    null;

  const countdown =
    overview.countdown ??
    null;

  const hasRank =
    preparationRank?.rank !==
      null &&
    preparationRank?.rank !==
      undefined &&
    preparationRank.cohortSize >
      0;

  const displayedRank =
    hasRank
      ? calibratedDisplayInteger(
          preparationRank.rank as number,
          PREPARATION_RANK_DISPLAY_MULTIPLIER,
        )
      : null;

  const displayedCohortSize =
    hasRank
      ? calibratedDisplayInteger(
          preparationRank.cohortSize,
          PREPARATION_COHORT_DISPLAY_MULTIPLIER,
        )
      : null;
  const rankText =
    displayedRank !== null &&
    displayedCohortSize !== null
      ? `#${displayedRank} out of ${displayedCohortSize} active users.`
      : null;
  const preparationMeta =
    rankText
      ? (
          <span>
            You rank{" "}
            <strong>
              {rankText}
            </strong>

            <InfoTooltip label="Ranking">
              Your rank among the active students on the portal. Rank combines your predicted score, breadth-depth of questions attempted, and consistency.
            </InfoTooltip>
          </span>
        )
      : (
          <span>
            Ranking unlocks with recognised test or Question Bank evidence.

            <InfoTooltip label="Ranking">
              Your rank among the active students on the portal. Rank combines your predicted score, breadth-depth of questions attempted, and consistency.
            </InfoTooltip>
          </span>
        );

  const countdownMeta = countdown ? (
    <span className={styles.countdownPill}>
      <ExamCountdown exam="TMUA" />
      <InfoTooltip label="TMUA countdown">
        Live countdown to {countdown.examDateLabel} at midnight (00:00 UK time).
        Days, hours, minutes and seconds update automatically every second.
      </InfoTooltip>
    </span>
  ) : null;

  if (
    predictor.status ===
      "insufficient_evidence" ||
    predictor.score ===
      null ||
    predictor.score <
      3.5
  ) {
    return (
      <section
        className={
          styles.strip
        }
        aria-label="TMUA preparation overview"
        data-preparation-rank-model={PREPARATION_RANK_MODEL_NAME}
      >
        <div
          className={
            styles.copy
          }
        >
          <span
            className={
              styles.label
            }
          >
            Your predicted TMUA score
          </span>

          <InfoTooltip label="Predicted TMUA score">
            Eligible practice-test evidence is the main signal. Retakes are collapsed within a test family. Verified Question Bank evidence starts contributing after 30 unique first-exposure questions and is capped so that it cannot overpower test evidence. Until enough eligible evidence exists, no synthetic score is shown.
          </InfoTooltip>

          <strong
            className={
              styles.building
            }
          >
            is still building.
          </strong>
        </div>

        <div
          className={
            styles.meta
          }
        >
          {preparationMeta}
          {countdownMeta}
        </div>
      </section>
    );
  }

  const hasRange =
    predictor.lowerBound !==
      null &&
    predictor.upperBound !==
      null;

  return (
    <section
      className={
        styles.strip
      }
      aria-label="TMUA preparation overview"
        data-preparation-rank-model={PREPARATION_RANK_MODEL_NAME}
    >
      <div
        className={
          styles.copy
        }
      >
        <span
          className={
            styles.label
          }
        >
          Your predicted TMUA score is
        </span>

        <InfoTooltip label="Predicted TMUA score">
          Eligible practice-test evidence is the main signal. Retakes are collapsed within a test family. Verified Question Bank evidence starts contributing after 30 unique first-exposure questions and is capped so that it cannot overpower test evidence. Confidence reflects the amount and spread of independent evidence.
        </InfoTooltip>

        <strong
          className={
            styles.score
          }
        >
          {scoreText(
            predictor.score,
          )}
        </strong>
      </div>

      <div
        className={
          styles.meta
        }
      >
        {hasRange ? (
          <span>
            Likely range{" "}
            {scoreText(
              predictor.lowerBound as number,
            )}
            {"\u2013"}
            {scoreText(
              predictor.upperBound as number,
            )}
          </span>
        ) : null}

        {predictor.confidence ? (
          <span>
            {confidenceText(
              predictor.confidence,
            )}{" "}
            confidence
          </span>
        ) : null}

        {preparationMeta}
        {countdownMeta}
      </div>
    </section>
  );
}
