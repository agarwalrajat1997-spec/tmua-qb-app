"use client";

import { useEffect, useId, useState } from "react";

import styles from "../dashboard/TmuaPredictionStrip.module.css";

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

type OverviewResponse = {
  ok: boolean;
  predictor?: PredictorOverview;
};

function scoreText(value: number): string {
  return value.toFixed(1);
}

function titleCase(value: string): string {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function InfoTooltip({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
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

      <span id={tooltipId} role="tooltip" className={styles.tooltip}>
        <strong className={styles.tooltipTitle}>{label}</strong>
        <span className={styles.tooltipText}>{children}</span>
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
        // This supplementary summary must never block the ESAT workspace.
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
  const testText = `${predictor.independentTestCount} independent full ${
    predictor.independentTestCount === 1 ? "paper" : "papers"
  }`;
  const qbText = predictor.qbUniqueQuestions >= 30
    ? `${predictor.qbUniqueQuestions} verified Question Bank first attempts`
    : "Question Bank evidence unlocks at 30 verified first attempts";

  if (
    predictor.status === "insufficient_evidence" ||
    predictor.score === null
  ) {
    return (
      <section className={styles.strip} aria-label="ESAT preparation overview">
        <div className={styles.copy}>
          <span className={styles.label}>Your predicted ESAT practice score</span>
          <InfoTooltip label="Predicted ESAT practice score">
            Recognised full-paper evidence is the main signal. Retakes are
            collapsed within each paper family. Verified Question Bank evidence
            begins after 30 unique first-exposure questions and cannot overpower
            test evidence. Official ESAT results are reported by module, so this
            combined 1-9 number is a Thriving Scholars practice estimate.
          </InfoTooltip>
          <strong className={styles.building}>is still building.</strong>
        </div>

        <div className={styles.meta}>
          <span>{testText}</span>
          <span>{qbText}</span>
        </div>
      </section>
    );
  }

  const hasRange =
    predictor.lowerBound !== null && predictor.upperBound !== null;

  return (
    <section className={styles.strip} aria-label="ESAT preparation overview">
      <div className={styles.copy}>
        <span className={styles.label}>
          Your predicted ESAT practice score is
        </span>
        <InfoTooltip label="Predicted ESAT practice score">
          Each recognised paper is re-scored on the server, converted module by
          module using that paper&apos;s audited difficulty, and then combined with
          the same retake, evidence-weight, confidence and likely-range rules as
          the TMUA predictor. Official ESAT reports modules separately; this is
          not an official UAT-UK combined score.
        </InfoTooltip>
        <strong className={styles.score}>{scoreText(predictor.score)}</strong>
      </div>

      <div className={styles.meta}>
        {hasRange ? (
          <span>
            Likely range {scoreText(predictor.lowerBound as number)}
            {"\u2013"}
            {scoreText(predictor.upperBound as number)}
          </span>
        ) : null}

        {predictor.confidence ? (
          <span>{titleCase(predictor.confidence)} confidence</span>
        ) : null}

        <span>{testText}</span>
        <span>{qbText}</span>
      </div>
    </section>
  );
}
