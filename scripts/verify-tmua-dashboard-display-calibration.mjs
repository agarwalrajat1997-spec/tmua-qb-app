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
const bank = fs.readFileSync(
  path.join(root, "app", "tmua-question-bank", "QuestionBank.tsx"),
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
const preparationMetaStart = prediction.indexOf("const preparationMeta =");

check(
  rankStart >= 0 &&
    cohortStart > rankStart &&
    rankTextStart > cohortStart &&
    preparationMetaStart > rankTextStart,
  "ranking blocks are missing or out of order",
);

const rankBlock = prediction.slice(rankStart, cohortStart);
const cohortBlock = prediction.slice(cohortStart, rankTextStart);
const rankTextBlock = prediction.slice(rankTextStart, preparationMetaStart);

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

// The October bank release replaces the old entry-card roadmap/how-to with the
// actual topic browser. Score/rank checks above remain unchanged.
check(
  /active\s*===\s*["']bank["']\s*\?\s*\(\s*<QuestionBank\s+embedded\s*\/>\s*\)/.test(dashboard)
    && bank.includes('<h1>QUESTION BANK</h1>') && bank.includes('className="topic-overview-grid"'),
  "The dashboard must embed the live question bank with its topic overview",
);

check(
  bank.includes('aria-label="Filter questions"') && bank.includes('htmlFor="bank-topic"')
    && bank.includes('htmlFor="bank-level"') && bank.includes('aria-label="Question pages"')
    && bank.includes('>All topics</button>'),
  "The topic browser must retain labelled topic/difficulty filters, back navigation and pagination",
);

const solutionDialogOpen = bank.match(/<dialog\s+ref=\{solutionDialog\}([\s\S]*?)<header/)?.[1] ?? "";
const studioDialogOpen = bank.match(/<dialog\s+ref=\{studioDialog\}([\s\S]*?)<header/)?.[1] ?? "";
check(
  solutionDialogOpen.includes('aria-labelledby="bank-solution-title"')
    && studioDialogOpen.includes('aria-labelledby="bank-studio-title"')
    && bank.includes('solutionDialog.current?.showModal()')
    && bank.includes('studioDialog.current?.showModal()')
    && bank.includes('aria-label="Close solution"') && bank.includes('aria-label="Close Study Studio"')
    && !solutionDialogOpen.includes('onCancel=') && !studioDialogOpen.includes('onCancel='),
  "Solution and Studio must use labelled native dialogs with explicit close controls and default Escape dismissal",
);

console.log("TMUA dashboard display verifier passed.");
