import assert from "node:assert/strict";
import {
  ESAT_PAPER_CALIBRATIONS,
  ESAT_SCORE_ESTIMATE_VERSION,
  ESAT_TEST_PROFILES,
  estimateEsatTestScores,
} from "../lib/server/esat-score-estimates.ts";

assert.equal(
  ESAT_SCORE_ESTIMATE_VERSION,
  "ESAT_EVIDENCE_CALIBRATED_V2_20260818",
);
assert.equal(Object.keys(ESAT_TEST_PROFILES).length, 26);
assert.equal(Object.keys(ESAT_PAPER_CALIBRATIONS).length, 21);

for (
  const [calibrationId, calibration]
  of Object.entries(ESAT_PAPER_CALIBRATIONS)
) {
  const table = calibration.conversionTable;

  assert.equal(
    table.length,
    28,
    `${calibrationId} must cover every raw mark from 0 to 27`,
  );
  assert.equal(table[0], 1, `${calibrationId} 0/27 must map to 1.0`);
  assert.equal(table[27], 9, `${calibrationId} 27/27 must map to 9.0`);

  table.forEach((score, index) => {
    assert.ok(
      score >= 1 && score <= 9,
      `${calibrationId} raw ${index} is outside 1.0-9.0`,
    );
    assert.equal(
      score,
      Math.round(score * 10) / 10,
      `${calibrationId} raw ${index} must use one decimal place`,
    );

    if (index > 0) {
      assert.ok(
        score >= table[index - 1],
        `${calibrationId} conversion must be monotonic`,
      );
    }
  });

  const medianAnchorScore =
    table[Math.round(calibration.medianRawAnchor)];
  const topDecileAnchorScore =
    table[Math.round(calibration.topDecileRawAnchor)];

  assert.ok(
    Math.abs(medianAnchorScore - 4.5) <= 0.35,
    `${calibrationId} median anchor should be close to 4.5`,
  );
  assert.ok(
    Math.abs(topDecileAnchorScore - 7) <= 0.4,
    `${calibrationId} top-decile anchor should be close to 7.0`,
  );
}

for (const [testId, profile] of Object.entries(ESAT_TEST_PROFILES)) {
  const estimate = estimateEsatTestScores(testId, [12, 18, 24]);

  assert.deepEqual(
    estimate.modules.map((item) => item.module),
    [...profile.modules],
  );
  assert.deepEqual(
    estimate.modules.map((item) => item.calibrationId),
    [...profile.calibrationIds],
  );
  assert.equal(estimate.rawTotal, 54);
  assert.equal(estimate.rawTotalPossible, 81);
  assert.equal(estimate.combinedScoreOfficial, false);
  assert.equal(estimate.status, "evidence_calibrated");
  assert.equal(
    estimate.predictedCombinedPracticeScore,
    estimate.averageModuleEstimate,
  );
  assert.match(estimate.note, /not an official UAT-UK result/i);

  const perfect = estimateEsatTestScores(testId, [27, 27, 27]);
  assert.equal(perfect.rawTotal, 81);
  assert.equal(perfect.predictedCombinedPracticeScore, 9);
}

const tierSeries = [
  [
    "esat-physics-chemistry-level-0",
    "esat-physics-chemistry-level-1",
    "esat-physics-chemistry-level-2",
  ],
  [
    "esat-physics-biology-level-0",
    "esat-physics-biology-level-1",
    "esat-physics-biology-level-2",
  ],
  [
    "esat-maths2-chemistry-level-0",
    "esat-maths2-chemistry-level-1",
    "esat-maths2-chemistry-level-2",
  ],
  [
    "esat-maths2-biology-level-0",
    "esat-maths2-biology-level-1",
    "esat-maths2-biology-level-2",
  ],
  [
    "esat-chemistry-biology-level-0",
    "esat-chemistry-biology-level-1",
    "esat-chemistry-biology-level-2",
  ],
];

for (const [easyId, standardId, hardId] of tierSeries) {
  for (const raw of [8, 12, 15, 18, 21, 24]) {
    const easy = estimateEsatTestScores(
      easyId,
      [raw, raw, raw],
    ).predictedCombinedPracticeScore;
    const standard = estimateEsatTestScores(
      standardId,
      [raw, raw, raw],
    ).predictedCombinedPracticeScore;
    const hard = estimateEsatTestScores(
      hardId,
      [raw, raw, raw],
    ).predictedCombinedPracticeScore;

    assert.ok(
      easy <= standard && standard <= hard,
      `${easyId}/${standardId}/${hardId} must reward the same raw mark more on harder forms`,
    );
  }
}

const standardSubjectProfile = estimateEsatTestScores(
  "esat-maths2-chemistry-level-1",
  [15, 15, 15],
).modules.map((item) => item.estimatedScore);

assert.ok(
  new Set(standardSubjectProfile).size > 1,
  "Subject modules must not share one generic percentage curve",
);

assert.throws(
  () => estimateEsatTestScores("unknown", [1, 2, 3]),
  /Unknown ESAT test profile/,
);
assert.throws(
  () => estimateEsatTestScores(
    "esat-physics-chemistry-level-1",
    [1, 2],
  ),
  /exactly three module marks/,
);
assert.throws(
  () => estimateEsatTestScores(
    "esat-physics-chemistry-level-1",
    [1, 2, 28],
  ),
  /expected 0 to 27/,
);

console.log(
  `ESAT score verification passed: ${Object.keys(ESAT_TEST_PROFILES).length} test profiles, ` +
  `${Object.keys(ESAT_PAPER_CALIBRATIONS).length} paper calibrations and 588 raw-score table entries.`,
);
