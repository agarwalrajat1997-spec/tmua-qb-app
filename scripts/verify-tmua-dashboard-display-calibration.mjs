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
  if (!value) {
    throw new Error(`TMUA dashboard display verification: ${message}`);
  }
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
  "ranking blocks are missing or out of order",
);

const rankBlock = prediction.slice(rankStart, cohortStart);
const cohortBlock = prediction.slice(cohortStart, rankTextStart);
const rankTextBlock = prediction.slice(rankTextStart, countdownStart);

check(
  prediction.includes("const PREPARATION_RANK_DISPLAY_MULTIPLIER = 2.0000;"),
  "rank display multiplier must stay 2.0000",
);

check(
  prediction.includes("const PREPARATION_COHORT_DISPLAY_MULTIPLIER = 3.0000;"),
  "cohort display multiplier must stay 3.0000",
);

check(
  rankBlock.includes("calibratedDisplayInteger(") &&
    rankBlock.includes("PREPARATION_RANK_DISPLAY_MULTIPLIER"),
  "displayed rank must actually apply x2",
);

check(
  cohortBlock.includes("calibratedDisplayInteger(") &&
    cohortBlock.includes("PREPARATION_COHORT_DISPLAY_MULTIPLIER"),
  "displayed cohort must actually apply x3",
);

check(
  rankTextBlock.includes("${displayedRank}") &&
    rankTextBlock.includes("${displayedCohortSize}") &&
    rankTextBlock.includes("active users."),
  "rank display must use the final active-users copy",
);

check(
  prediction.includes('You rank{" "}'),
  'visible wording must begin "You rank"',
);

check(
  !prediction.includes('Your rank{" "}'),
  'old visible "Your rank" wording must stay removed',
);

const tooltipSentence =
  "Your rank among the active students on the portal. Rank combines your predicted score, breadth-depth of questions attempted, and consistency.";

check(
  prediction.split(tooltipSentence).length - 1 === 2,
  "both Ranking tooltip states must use the final tooltip copy",
);

check(
  !prediction.includes("scaled cohort") &&
    !prediction.includes("benchmark users") &&
    !prediction.includes("active-user index") &&
    !prediction.includes("fixed presentation calibration:"),
  "stale scaled/benchmark wording must stay removed",
);

check(
  dashboard.includes(
    '<div className={styles.cardTitle}>Roadmap</div>',
  ),
  'Question Bank heading must remain "Roadmap"',
);

check(
  dashboard.includes("TS_QB_HOWTO_TOGGLE_V3") &&
    dashboard.includes('<details className={styles.card}>') &&
    dashboard.includes("<summary"),
  "How to Use the Question Bank must remain collapsible",
);

check(
  dashboard.includes("Alt + N") && dashboard.includes("Alt + P"),
  "Question Bank keyboard shortcuts must remain present",
);

console.log("TMUA dashboard display verifier passed.");
