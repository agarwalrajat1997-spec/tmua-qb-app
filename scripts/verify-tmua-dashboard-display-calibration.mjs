import fs from "node:fs";
import path from "node:path";

const root = process.cwd();

const prediction = fs.readFileSync(
  path.join(root, "app", "dashboard", "TmuaPredictionStrip.tsx"),
  "utf8",
);

const dashboard = fs.readFileSync(
  path.join(root, "app", "dashboard", "DashboardClient.tsx"),
  "utf8",
);

function check(value, message) {
  if (!value) throw new Error(message);
}

const rankStart = prediction.indexOf("const displayedRank =");
const cohortStart = prediction.indexOf("const displayedCohortSize =");
const rankTextStart = prediction.indexOf("const rankText =");
const countdownStart = prediction.indexOf("const countdownText =");

check(
  rankStart >= 0 &&
  cohortStart > rankStart &&
  rankTextStart > cohortStart &&
  countdownStart > rankTextStart,
  "ranking blocks missing",
);

const rankBlock = prediction.slice(rankStart, cohortStart);
const cohortBlock = prediction.slice(cohortStart, rankTextStart);
const rankTextBlock = prediction.slice(rankTextStart, countdownStart);

check(
  prediction.includes(
    "const PREPARATION_RANK_DISPLAY_MULTIPLIER = 2.0000;"
  ),
  "rank multiplier changed",
);

check(
  prediction.includes(
    "const PREPARATION_COHORT_DISPLAY_MULTIPLIER = 3.0000;"
  ),
  "cohort multiplier changed",
);

check(
  rankBlock.includes("calibratedDisplayInteger(") &&
  rankBlock.includes("PREPARATION_RANK_DISPLAY_MULTIPLIER"),
  "rank x2 is not actually applied",
);

check(
  cohortBlock.includes("calibratedDisplayInteger(") &&
  cohortBlock.includes("PREPARATION_COHORT_DISPLAY_MULTIPLIER"),
  "cohort x3 is not actually applied",
);

check(
  rankTextBlock.includes("${displayedRank}") &&
  rankTextBlock.includes("${displayedCohortSize}") &&
  rankTextBlock.includes("active-user index"),
  "rank display copy changed",
);

check(
  prediction.includes('You rank{" "}'),
  '"You rank" wording changed',
);

check(
  (
    prediction.split(
      "Your indexed rank among active students on the portal."
    ).length - 1
  ) === 2,
  "ranking tooltip changed",
);

check(
  dashboard.includes(
    '<div className={styles.cardTitle}>Roadmap</div>'
  ),
  "Roadmap changed",
);

check(
  dashboard.includes("TS_QB_HOWTO_TOGGLE_V3") &&
  dashboard.includes('<details className={styles.card}>') &&
  dashboard.includes("<summary"),
  "Question Bank How-to toggle changed",
);

check(
  dashboard.includes("Alt + N") &&
  dashboard.includes("Alt + P"),
  "Question Bank shortcuts changed",
);

console.log("TMUA dashboard display verifier passed.");