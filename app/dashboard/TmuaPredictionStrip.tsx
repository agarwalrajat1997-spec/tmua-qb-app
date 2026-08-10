"use client";

import {
  useEffect,
  useState,
} from "react";

import styles from "./TmuaPredictionStrip.module.css";

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

type OverviewResponse = {
  ok: boolean;
  predictor?: PredictorOverview;
  error?: string;
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
    predictor,
    setPredictor,
  ] =
    useState<
      PredictorOverview |
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
            setPredictor(
              body.predictor,
            );
          }
        }
        catch {
          // The predictor is supplementary UI.
          // Existing dashboard functionality must continue
          // even if this request fails.
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
    !predictor
  ) {
    return null;
  }

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
        aria-label="TMUA prediction"
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
            Your TMUA prediction
          </span>

          <strong
            className={
              styles.building
            }
          >
            is still building.
          </strong>
        </div>

        <span
          className={
            styles.detail
          }
        >
          Complete more recognised tests or Question Bank practice.
        </span>
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
      aria-label="TMUA prediction"
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
            –
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
      </div>
    </section>
  );
}