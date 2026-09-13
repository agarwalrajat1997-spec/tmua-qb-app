import fs from "node:fs";

import {
  buildTmuaPredictorInputsByUser,
} from "../lib/server/tmua-predictor-v1-evidence-adapter.ts";

import {
  calculateTmuaPredictorV1,
} from "../lib/server/tmua-predictor-v1-engine.ts";

import {
  buildTmuaPredictionSnapshotInsert,
} from "../lib/server/tmua-predictor-v1-snapshot.ts";

const inputPath =
  process.argv[2];

const outputPath =
  process.argv[3];

if (
  !inputPath ||
  !outputPath
) {
  throw new Error(
    "Usage: node build-tmua-predictor-v1-snapshot-csv.mjs <input.json> <output.csv>",
  );
}

const payload =
  JSON.parse(
    fs
      .readFileSync(
        inputPath,
        "utf8",
      )
      .replace(
        /^\uFEFF/,
        "",
      )
      .trim(),
  );

const inputs =
  buildTmuaPredictorInputsByUser(
    payload,
  );

const calculatedAt =
  new Date().toISOString();

const snapshots =
  inputs.map(
    ({ userId, input }) =>
      buildTmuaPredictionSnapshotInsert(
        userId,
        calculateTmuaPredictorV1(
          input,
        ),
        calculatedAt,
      ),
  );

const uniqueKeys =
  new Set();

for (
  const snapshot of snapshots
) {
  const key =
    [
      snapshot.userId,
      snapshot.modelVersion,
      snapshot.inputHash,
    ].join("|");

  if (uniqueKeys.has(key)) {
    throw new Error(
      "Duplicate snapshot deduplication key in batch",
    );
  }

  uniqueKeys.add(
    key,
  );
}

function csv(
  value,
) {
  if (
    value === null ||
    value === undefined
  ) {
    return "";
  }

  const text =
    typeof value === "object"
      ? JSON.stringify(value)
      : String(value);

  return (
    '"' +
    text.replaceAll(
      '"',
      '""',
    ) +
    '"'
  );
}

const headers = [
  "user_id",
  "model_version",
  "input_hash",
  "prediction_status",
  "predicted_tmua_score9",
  "lower_bound",
  "upper_bound",
  "confidence",
  "test_signal_score9",
  "test_weight",
  "test_evidence_count",
  "independent_test_count",
  "combined_full_count",
  "qb_signal_score9",
  "qb_weight",
  "qb_unique_questions",
  "qb_topic_coverage",
  "conversion_set_hash",
  "active_topic_set_hash",
  "evidence_details",
  "calculated_at",
];

const lines = [
  headers.join(","),
];

for (
  const row of snapshots
) {
  lines.push(
    [
      row.userId,
      row.modelVersion,
      row.inputHash,
      row.predictionStatus,
      row.predictedTmuaScore9,
      row.lowerBound,
      row.upperBound,
      row.confidence,
      row.testSignalScore9,
      row.testWeight,
      row.testEvidenceCount,
      row.independentTestCount,
      row.combinedFullCount,
      row.qbSignalScore9,
      row.qbWeight,
      row.qbUniqueQuestions,
      row.qbTopicCoverage,
      row.conversionSetHash,
      row.activeTopicSetHash,
      row.evidenceDetails,
      row.calculatedAt,
    ]
      .map(
        csv,
      )
      .join(","),
  );
}

fs.writeFileSync(
  outputPath,
  lines.join("\n") + "\n",
  "utf8",
);

const predicted =
  snapshots.filter(
    (row) =>
      row.predictionStatus ===
      "predicted",
  ).length;

const insufficient =
  snapshots.length -
  predicted;

console.log(
  "TMUA Predictor V1 snapshot batch built:",
);

console.log(
  `Rows: ${snapshots.length}`,
);

console.log(
  `Predicted: ${predicted}`,
);

console.log(
  `Insufficient evidence: ${insufficient}`,
);

console.log(
  `Calculated at: ${calculatedAt}`,
);

console.log(
  "Duplicate input keys: 0",
);