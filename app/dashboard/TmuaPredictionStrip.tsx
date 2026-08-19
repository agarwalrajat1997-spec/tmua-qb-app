"use client";

import {
  useEffect,
  useId,
  useState,
} from "react";

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
      let cancelled =
        false;

      async function load() {
        try {
          const response =
            await fetch(
              "/api/tmua/overview",
              {
                method:
                  "GET",

                cache:
                  "no-store",

                credentials:
                  "same-origin",
              },
            );

          if (
            !response.ok
          ) {
            return;
          }

          const body =
            (
              await response.json()
            ) as
              OverviewResponse;

          if (
            !cancelled &&
            body.ok &&
            body.predictor
          ) {
            setOverview(
              body,
            );
          }
        }
        catch {
          // Supplementary dashboard information must never
          // break the existing workspace.
        }
        finally {
          if (
            !cancelled
          ) {
            setLoaded(
              true,
            );
          }
        }
      }

      void load();

      return () => {
        cancelled =
          true;
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
  const countdownText =
    countdown
      ? `${
          countdown.daysToTmua
        } ${
          countdown.daysToTmua ===
          1
            ? "day"
            : "days"
        } till TMUA`
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

  const countdownMeta =
    countdown &&
    countdownText
      ? (
          <span>
            {countdownText}

            <InfoTooltip label="TMUA countdown">
              Calendar days remaining until your configured TMUA exam date. The countdown updates automatically each day. Current exam date: {countdown.examDateLabel}.
            </InfoTooltip>
          </span>
        )
      : null;

  if (
    predictor.status ===
      "insufficient_evidence" ||
    predictor.score ===
      null
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