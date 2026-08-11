import fs from "node:fs";
import path from "node:path";

const root = process.cwd();

const predictionPath = path.join(
  root,
  "app",
  "dashboard",
  "TmuaPredictionStrip.tsx",
);

const dashboardPath = path.join(
  root,
  "app",
  "dashboard",
  "DashboardClient.tsx",
);

const prediction = fs.readFileSync(predictionPath, "utf8");
const dashboard = fs.readFileSync(dashboardPath, "utf8");

function requireInvariant(condition, message) {
  if (!condition) {
    throw new Error(`TMUA dashboard display calibration: ${message}`);
  }
}

requireInvariant(
  prediction.includes(
    "const PREPARATION_RANK_DISPLAY_MULTIPLIER = 2.0000;",
  ),
  "rank display multiplier must remain exactly 2.0000",
);

requireInvariant(
  prediction.includes(
    "const PREPARATION_COHORT_DISPLAY_MULTIPLIER = 3.0000;",
  ),
  "cohort display multiplier must remain exactly 3.0000",
);

requireInvariant(
  /const displayedRank\s*=\s*hasRank\s*\?\s*calibratedDisplayInteger\(\s*preparationRank\.rank as number,\s*PREPARATION_RANK_DISPLAY_MULTIPLIER\s*,?\s*\)\s*:\s*null;/s.test(
    prediction,
  ),
  "displayed rank must actually apply the x2 multiplier",
);

requireInvariant(
  /const displayedCohortSize\s*=\s*hasRank\s*\?\s*calibratedDisplayInteger\(\s*preparationRank\.cohortSize,\s*PREPARATION_COHORT_DISPLAY_MULTIPLIER\s*,?\s*\)\s*:\s*null;/s.test(
    prediction,
  ),
  "displayed cohort must actually apply the x3 multiplier",
);

requireInvariant(
  prediction.includes('You rank{" "}'),
  'student-facing wording must begin "You rank"',
);

requireInvariant(
  !prediction.includes('Your rank{" "}'),
  'old student-facing "Your rank" wording must stay removed',
);

requireInvariant(
  prediction.includes("scaled cohort"),
  "non-unit cohort presentation must remain explicitly labelled scaled",
);

requireInvariant(
  dashboard.includes(
    '<div className={styles.cardTitle}>Roadmap</div>',
  ),
  'Question Bank study path must remain titled "Roadmap"',
);

requireInvariant(
  !dashboard.includes(
    '<div className={styles.cardTitle}>Recommended Practice Path</div>',
  ),
  '"Recommended Practice Path" must stay removed',
);

requireInvariant(
  dashboard.includes("TS_QB_HOWTO_TOGGLE_V3"),
  "How-to toggle marker is missing",
);

requireInvariant(
  dashboard.includes('<details className={styles.card}>') &&
    dashboard.includes("<summary") &&
    dashboard.includes("How to Use the Question Bank"),
  "How to Use the Question Bank must remain a collapsed native toggle",
);

requireInvariant(
  dashboard.includes("Alt + N") &&
    dashboard.includes("Alt + P"),
  "Question Bank keyboard shortcut instructions must remain present",
);

console.log(
  "TMUA dashboard display-calibration verification passed: rank x2, cohort x3, You rank wording, Roadmap heading and collapsible How-to are frozen.",
);