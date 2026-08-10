"use client";

import {
  useEffect,
  useState,
} from "react";

import styles from "./TmuaPredictionStrip.module.css";

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
      ? `#${displayedRank} of ${displayedCohortSize} active users`
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
        } to TMUA`
      : null;

  const preparationMeta =
    rankText
      ? (
          <span>
            Preparation Rank{" "}
            <strong>
              {rankText}
            </strong>
          </span>
        )
      : (
          <span>
            Preparation Rank unlocks with recognised test or Question Bank evidence.
          </span>
        );

  const countdownMeta =
    countdown &&
    countdownText
      ? (
          <span>
            {countdownText}
            {" \u00b7 "}
            {countdown.examDateLabel}
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