"use client";

import {
  useEffect,
  useId,
  useState,
} from "react";

import EsatModulePredictions from "./EsatModulePredictions";
import styles from "../dashboard/TmuaPredictionStrip.module.css";

const PREPARATION_RANK_MODEL_NAME = "ESAT Preparation Rank";

// Display calibration mirrors the existing TMUA preparation strip.
// A rank is displayed only when the server supplies an available cohort rank.
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
  status?: "temporarily_unavailable";
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
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, []);

  const preparationRank = overview?.preparationRank ?? null;

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

  const preparationMeta = rankText
    ? (
        <span>
          You rank{" "}
          <strong>{rankText}</strong>

          <InfoTooltip label="Ranking">
            Your rank is based on the rolling 30-day active ESAT cohort and combines your predicted practice score, breadth-depth of questions attempted, and consistency.
          </InfoTooltip>
        </span>
      )
    : preparationRank?.status === "temporarily_unavailable"
    ? <span>Ranking is temporarily unavailable.</span>
    : (
        <span>
          Ranking unlocks with recognised test or Question Bank evidence.

          <InfoTooltip label="Ranking">
            Your rank is based on the rolling 30-day active ESAT cohort and combines your predicted practice score, breadth-depth of questions attempted, and consistency.
          </InfoTooltip>
        </span>
      );

  return (
    <>
      <EsatModulePredictions />
      {overview && <section className={styles.strip} aria-label="ESAT preparation rank" data-preparation-rank-model={PREPARATION_RANK_MODEL_NAME}>
        <div className={styles.meta}>{preparationMeta}</div>
      </section>}
    </>
  );
}
