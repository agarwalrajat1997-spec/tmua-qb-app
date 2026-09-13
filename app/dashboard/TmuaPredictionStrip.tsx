"use client";

// Emergency load-shedding hotfix, 13 Sep 2026.
// The TMUA predictor/rank strip is supplementary UI. Its overview endpoint
// performs expensive cohort-wide reads and persistence on each dashboard load.
// Temporarily render nothing so normal TMUA access (question bank, practice
// tests and classes) stays available while the overview endpoint is optimised.
export default function TmuaPredictionStrip() {
  return null;
}
