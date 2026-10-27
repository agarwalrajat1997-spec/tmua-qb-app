"use client";

import {
  useEffect,
  useId,
  useState,
} from "react";

import ExamCountdown from "@/app/_components/ExamCountdown";
import type { EsatModulePrediction, EsatModule } from "@/lib/esat-predictions";
import moduleStyles from "./EsatPredictionStrip.module.css";
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

type ModuleOverview = {
  ok: boolean;
  pathway: { status: "inferred" | "building"; modules: EsatModule[] };
  predictions: Omit<EsatModulePrediction, "guaranteeEligible" | "inputHash">[];
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
  const [modules, setModules] = useState<ModuleOverview | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    let pending = false;
    async function load() {
      if (pending || document.visibilityState === "hidden") return;
      pending = true;
      await Promise.allSettled([
        (async () => {
          const response = await fetch("/api/esat/overview", { cache: "no-store", credentials: "same-origin", signal: controller.signal });
          if (!response.ok) return;
          const body = await response.json() as OverviewResponse;
          if (!controller.signal.aborted && body.ok) setOverview(body);
        })(),
        (async () => {
          try {
            const response = await fetch("/api/esat/module-predictions", { cache: "no-store", credentials: "same-origin", signal: controller.signal });
            if (!response.ok) return;
            const body = await response.json() as ModuleOverview;
            if (!controller.signal.aborted && body.ok) setModules(body);
          } finally {
            if (!controller.signal.aborted) setLoaded(true);
          }
        })(),
      ]);
      pending = false;
    }
    void load();
    const interval = window.setInterval(() => void load(), 60000);
    const refresh = () => void load();
    window.addEventListener("focus", refresh);
    document.addEventListener("visibilitychange", refresh);
    return () => {
      controller.abort();
      window.clearInterval(interval);
      window.removeEventListener("focus", refresh);
      document.removeEventListener("visibilitychange", refresh);
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

  const hasEvidence = modules?.predictions.some(item => item.independentTestCount > 0 || item.qbUniqueQuestions >= 30);

  return (
    <section className={styles.strip} aria-label="ESAT preparation overview" data-preparation-rank-model={PREPARATION_RANK_MODEL_NAME}>
      <div className={`${styles.copy} ${moduleStyles.predictions}`}>
        <span className={moduleStyles.heading}>
          <span className={styles.label}>Your predicted ESAT scores</span>
          <InfoTooltip label="Predicted ESAT module scores">
            Each recognised ESAT paper is re-scored module by module using its audited difficulty.
            Each subject uses only its own tests and Question Bank evidence to calculate its score, confidence and likely range.
            Repeated papers and retakes count once; verified Question Bank evidence begins after 30 unique first-exposure questions per module.
            Tests taken with 25% extra time use the existing standard-time adjustment.
            Official ESAT results are reported separately for each module. Predictions below 3.5 remain in the building state.
            <span className={moduleStyles.infoDetail}>
              {modules?.pathway.status === "inferred"
                ? `Your practice currently indicates: ${modules.pathway.modules.join(" + ")}. This updates as your practice changes.`
                : "Your pathway is identified automatically from the subjects you practise. While the evidence is incomplete or mixed, we show the modules with enough evidence without assuming your final pathway."}
            </span>
            {modules?.predictions.map(item => (
              <span className={moduleStyles.infoDetail} key={item.module}>
                <strong>{item.module}:</strong>{" "}
                {item.score === null ? "Still building." : `${item.score.toFixed(1)} · ${item.confidence ? item.confidence[0].toUpperCase() + item.confidence.slice(1) : "Building"} confidence.`}
                {item.lowerBound !== null && item.upperBound !== null ? ` Likely range ${item.lowerBound.toFixed(1)}–${item.upperBound.toFixed(1)}.` : ""}
                {` ${item.independentTestCount} independent test${item.independentTestCount === 1 ? "" : "s"}; ${item.qbUniqueQuestions} eligible unique Question Bank questions.`}
              </span>
            ))}
          </InfoTooltip>
        </span>
        {!loaded && !modules ? <strong className={styles.building}>Calculating…</strong>
          : !modules ? <strong className={moduleStyles.unavailable}>Temporarily unavailable.</strong>
          : !hasEvidence ? <strong className={styles.building}>are still building.</strong>
          : <span className={moduleStyles.scores}>
              {modules.predictions.map(item => (
                <span className={moduleStyles.module} key={item.module}>
                  <span className={moduleStyles.moduleName}>{item.module.replace("Mathematics", "Maths")}</span>
                  <strong className={item.score === null ? moduleStyles.building : styles.score}>
                    {item.score === null ? "Still building" : item.score.toFixed(1)}
                  </strong>
                </span>
              ))}
            </span>}
      </div>
      <div className={styles.meta}>
        {preparationMeta}
        <span className={styles.countdownPill}>
          <ExamCountdown exam="ESAT" />
          <InfoTooltip label="ESAT countdown">
            Live countdown to {overview?.countdown?.examDateLabel ?? "4 January 2027"} at midnight (00:00 UK time).
            Days, hours, minutes and seconds update automatically every second.
          </InfoTooltip>
        </span>
      </div>
    </section>
  );
}
