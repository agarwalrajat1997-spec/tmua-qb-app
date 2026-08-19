"use client";

import {
  useEffect,
  useId,
  useState,
} from "react";

import styles from "../dashboard/TmuaPredictionStrip.module.css";

const PREPARATION_RANK_MODEL_NAME = "ESAT Preparation Rank";

// Display calibration mirrors the existing TMUA preparation strip.
// The server continues to return the genuine rolling 30-day portal cohort.
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
  status: "predicted" | "insufficient_evidence";
  score: number | null;
  lowerBound: number | null;
  upperBound: number | null;
  confidence: "low" | "medium" | "high" | null;
  testEvidenceCount: number;
  independentTestCount: number;
  qbUniqueQuestions: number;
  qbTopicCoverage: number;
  calculatedAt: string;
  combinedScoreOfficial: false;
};

type PreparationRankOverview = {
  modelVersion: string;
  hasGenuinePreparationEvidence: boolean;
  score: number | null;
  rank: number | null;
  cohortSize: number;
  components: {
    performance: number;
    breadth: number;
    evidenceDepth: number;
    recentActivity: number;
    consistency: number;
    recovery: number;
  } | null;
  calculatedAt: string;
};

type CountdownOverview = {
  daysToEsat: number;
  examDate: string;
  examDateLabel: string;
};

type OverviewResponse = {
  ok: boolean;
  predictor?: PredictorOverview;
  preparationRank?: PreparationRankOverview;
  countdown?: CountdownOverview;
  error?: string;
};

function scoreText(value: number): string {
  return value.toFixed(1);
}

function confidenceText(
  value: PredictorOverview["confidence"],
): string {
  if (!value) {
    return "";
  }

  return value.charAt(0).toUpperCase() + value.slice(1);
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

export default function EsatPredictionStrip() {
  const [overview, setOverview] = useState<OverviewResponse | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const response = await fetch("/api/esat/overview", {
          method: "GET",
          cache: "no-store",
          credentials: "same-origin",
        });

        if (!response.ok) {
          return;
        }

        const body = (await response.json()) as OverviewResponse;

        if (!cancelled && body.ok && body.predictor) {
          setOverview(body);
        }
      }
      catch {
        // Supplementary dashboard information must never block the workspace.
      }
      finally {
        if (!cancelled) {
          setLoaded(true);
        }
      }
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, []);

  if (!loaded || !overview?.predictor) {
    return null;
  }

  const predictor = overview.predictor;
  const preparationRank = overview.preparationRank ?? null;
  const countdown = overview.countdown ?? null;

  const hasRank =
    preparationRank?.rank !== null &&
    preparationRank?.rank !== undefined &&
    preparationRank.cohortSize > 0;

  const displayedRank = hasRank
    ? calibratedDisplayInteger(
        preparationRank.rank as number,
        PREPARATION_RANK_DISPLAY_MULTIPLIER,
      )
    : null;

  const displayedCohortSize = hasRank
    ? calibratedDisplayInteger(
        preparationRank.cohortSize,
        PREPARATION_COHORT_DISPLAY_MULTIPLIER,
      )
    : null;

  const rankText =
    displayedRank !== null && displayedCohortSize !== null
      ? `#${displayedRank} out of ${displayedCohortSize} active users.`
      : null;

  const countdownText = countdown
    ? `${countdown.daysToEsat} ${
        countdown.daysToEsat === 1 ? "day" : "days"
      } till ESAT`
    : null;

  const preparationMeta = rankText
    ? (
        <span>
          You rank{" "}
          <strong>{rankText}</strong>

          <InfoTooltip label="Ranking">
            Your rank is based on the rolling 30-day active ESAT cohort and combines your predicted practice score, breadth-depth of questions attempted, and consistency. The displayed rank and cohort use the same calibrated presentation as TMUA to account for Thriving Scholars students who also prepare outside the portal.
          </InfoTooltip>
        </span>
      )
    : (
        <span>
          Ranking unlocks with recognised test or Question Bank evidence.

          <InfoTooltip label="Ranking">
            Your rank is based on the rolling 30-day active ESAT cohort and combines your predicted practice score, breadth-depth of questions attempted, and consistency.
          </InfoTooltip>
        </span>
      );

  const countdownMeta = countdown && countdownText
    ? (
        <span>
          {countdownText}

          <InfoTooltip label="ESAT countdown">
            Calendar days remaining until the configured ESAT exam date. The countdown updates automatically each day. Current exam date: {countdown.examDateLabel}.
          </InfoTooltip>
        </span>
      )
    : null;

  if (
    predictor.status === "insufficient_evidence" ||
    predictor.score === null ||
    predictor.score < 3.5
  ) {
    return (
      <section
        className={styles.strip}
        aria-label="ESAT preparation overview"
        data-preparation-rank-model={PREPARATION_RANK_MODEL_NAME}
      >
        <div className={styles.copy}>
          <span className={styles.label}>
            Your predicted ESAT practice score
          </span>

          <InfoTooltip label="Predicted ESAT practice score">
            Recognised full-paper evidence is the main signal. Retakes are collapsed within each paper family. Verified Question Bank evidence begins after 30 unique first-exposure questions and is capped so that it cannot overpower test evidence. Predictions below 3.5 remain in the building state. Official ESAT results are reported by module, so this combined 1-9 number is a Thriving Scholars practice estimate.
          </InfoTooltip>

          <strong className={styles.building}>
            is still building.
          </strong>
        </div>

        <div className={styles.meta}>
          {preparationMeta}
          {countdownMeta}
        </div>
      </section>
    );
  }

  const hasRange =
    predictor.lowerBound !== null &&
    predictor.upperBound !== null;

  return (
    <section
      className={styles.strip}
      aria-label="ESAT preparation overview"
      data-preparation-rank-model={PREPARATION_RANK_MODEL_NAME}
    >
      <div className={styles.copy}>
        <span className={styles.label}>
          Your predicted ESAT practice score is
        </span>

        <InfoTooltip label="Predicted ESAT practice score">
          Each recognised paper is re-scored on the server, converted module by module using that paper&apos;s audited difficulty, and then combined with the same retake, evidence-weight, confidence and likely-range rules as the TMUA predictor. Official ESAT reports modules separately; this is not an official UAT-UK combined score.
        </InfoTooltip>

        <strong className={styles.score}>
          {scoreText(predictor.score)}
        </strong>
      </div>

      <div className={styles.meta}>
        {hasRange ? (
          <span>
            Likely range{" "}
            {scoreText(predictor.lowerBound as number)}
            {"\u2013"}
            {scoreText(predictor.upperBound as number)}
          </span>
        ) : null}

        {predictor.confidence ? (
          <span>
            {confidenceText(predictor.confidence)}{" "}
            confidence
          </span>
        ) : null}

        {preparationMeta}
        {countdownMeta}
      </div>
    </section>
  );
}
