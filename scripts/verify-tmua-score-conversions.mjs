import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";

const sharedPath = path.join(
  "public",
  "shared",
  "tmua-score-conversions.js"
);

const source = fs.readFileSync(sharedPath, "utf8");
const context = { console };
vm.createContext(context);
vm.runInContext(source, context, {
  filename: sharedPath
});

const api = context.TS_TMUA_SCORE_CONVERSIONS;
if (!api) {
  throw new Error("Shared TMUA conversion API was not exported.");
}

const profiles = [
  ["full-official-2016.html", "official-2016"],
  ["full-official-2017.html", "official-2017"],
  ["full-official-2018.html", "official-2018"],
  ["full-official-2019.html", "official-2019"],
  ["full-official-2020.html", "official-2020"],
  ["full-official-2021.html", "official-2021"],
  ["full-official-2022.html", "official-2022"],
  ["full-official-2023.html", "official-2023"],
  ["full-specimen.html", "specimen-estimate"],
  ["full-mock-01-all-topics.html", "mock1"],
  ["full-mock-02-all-topics.html", "mock2"],
  ["tmua-2024-2025-challenging-mock/index.html", "informed2024-2025"]
];

const testsRoot = path.join(
  "public",
  "practice-tests",
  "tests"
);

const scriptUrl =
  "/shared/tmua-score-conversions.js?v=20260806-1";

for (const [relative, profile] of profiles) {
  const file = path.join(testsRoot, ...relative.split("/"));
  const html = fs.readFileSync(file, "utf8");

  const markerCount =
    html.split("TS_TMUA_SCORE_CONVERSION_V1_START").length - 1;

  if (markerCount !== 1) {
    throw new Error(`Expected one score marker: ${relative}`);
  }

  if (!html.includes(`window.TS_TMUA_SCORE_PROFILE="${profile}"`)) {
    throw new Error(`Wrong score profile in: ${relative}`);
  }

  if (!html.includes(scriptUrl)) {
    throw new Error(`Shared score script missing from: ${relative}`);
  }

  if (!html.includes("/api/practice-tests/submit")) {
    throw new Error(`Submit API missing from: ${relative}`);
  }
}

for (const profile of profiles.map((entry) => entry[1])) {
  let previous = 0;

  for (let raw = 0; raw <= 40; raw += 1) {
    const score = api.convert(profile, raw);

    if (!Number.isFinite(score) || score < 1.0 || score > 9.0) {
      throw new Error(`${profile} has invalid score at ${raw}: ${score}`);
    }

    if (score < previous) {
      throw new Error(`${profile} is not monotonic at raw ${raw}.`);
    }

    if (Math.round(score * 10) !== score * 10) {
      throw new Error(`${profile} is not rounded to one decimal at ${raw}.`);
    }

    previous = score;
  }
}

const exactChecks = [
  ["official-2016", 28, 9.0],
  ["official-2017", 10, 2.2],
  ["official-2018", 10, 2.3],
  ["official-2019", 34, 7.9],
  ["official-2020", 20, 5.3],
  ["official-2021", 21, 5.6],
  ["official-2022", 22, 6.5],
  ["official-2023", 26, 7.0],
  ["specimen-estimate", 24, 6.5],
  ["mock1", 26, 7.0],
  ["mock2", 30, 7.0],
  ["informed2024-2025", 23, 7.0],
  ["informed2024-2025", 32, 8.5]
];

for (const [profile, raw, expected] of exactChecks) {
  const actual = api.convert(profile, raw);
  if (actual !== expected) {
    throw new Error(
      `${profile} raw ${raw}: expected ${expected}, received ${actual}`
    );
  }
}

const thresholdChecks = {
  "official-2016": [19,21,22,24,25,28],
  "official-2017": [23,24,26,28,29,32],
  "official-2018": [23,24,26,28,29,32],
  "official-2019": [23,24,28,32,35,38],
  "official-2020": [23,24,28,32,35,38],
  "official-2021": [23,24,28,32,35,38],
  "official-2022": [21,22,27,31,34,38],
  "official-2023": [19,21,26,31,34,38],
  "specimen-estimate": [23,24,26,28,29,32]
};

const targetScores = [6.0,6.5,7.0,7.5,8.0,9.0];

for (const [profile, expectedThresholds] of Object.entries(thresholdChecks)) {
  const actualThresholds = targetScores.map((target) => {
    for (let raw = 0; raw <= 40; raw += 1) {
      if (api.convert(profile, raw) >= target) return raw;
    }
    return null;
  });

  if (JSON.stringify(actualThresholds) !== JSON.stringify(expectedThresholds)) {
    throw new Error(
      `${profile} thresholds are wrong: ${JSON.stringify(actualThresholds)}`
    );
  }
}

const challenge = fs.readFileSync(
  path.join(
    testsRoot,
    "tmua-2024-2025-challenging-mock",
    "index.html"
  ),
  "utf8"
);

const revisedPdf =
  "https://apps.thrivingscholars.com/tmua-solutions/" +
  "tmua-2024-2025-challenging-full-test-revised-solutions.pdf";

if (!challenge.includes(revisedPdf)) {
  throw new Error("The revised challenge PDF URL was lost.");
}

console.log(
  "TMUA score-conversion verification passed: 8 official tables, " +
  "specimen estimate, 3 mock curves, combined scoring and submission " +
  "payload correction are protected."
);