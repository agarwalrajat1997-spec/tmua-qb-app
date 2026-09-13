import fs from "node:fs";
import crypto from "node:crypto";

import {
  buildTmuaPredictorInputsByUser,
} from "../lib/server/tmua-predictor-v1-evidence-adapter.ts";

import {
  calculateTmuaPredictorV1,
} from "../lib/server/tmua-predictor-v1-engine.ts";

const payloadPath =
  process.argv[2];

if (!payloadPath) {
  throw new Error(
    "Usage: node run-tmua-predictor-v1-shadow.mjs <payload.json>",
  );
}

const payload =
  JSON.parse(
    fs.readFileSync(
      payloadPath,
      "utf8",
    ),
  );

function hash(
  value,
) {
  return crypto
    .createHash(
      "sha256",
    )
    .update(
      value,
      "utf8",
    )
    .digest(
      "hex",
    );
}

function round(
  value,
  decimals = 2,
) {
  const factor =
    10 ** decimals;

  return Math.round(
    value *
      factor,
  ) / factor;
}

function median(
  values,
) {
  if (values.length === 0) {
    return null;
  }

  const sorted =
    [...values].sort(
      (a, b) =>
        a - b,
    );

  const middle =
    Math.floor(
      sorted.length /
        2,
    );

  if (
    sorted.length % 2 === 1
  ) {
    return sorted[
      middle
    ];
  }

  return (
    sorted[
      middle - 1
    ] +
    sorted[
      middle
    ]
  ) / 2;
}

function mean(
  values,
) {
  if (values.length === 0) {
    return null;
  }

  return (
    values.reduce(
      (sum, value) =>
        sum + value,
      0,
    ) /
    values.length
  );
}

const users =
  buildTmuaPredictorInputsByUser(
    payload,
  );

const aliasRecords =
  users
    .map(
      (user) => ({
        ...user,
        anonymousKey:
          hash(
            user.userId,
          ),
      }),
    )
    .sort(
      (a, b) =>
        a.anonymousKey.localeCompare(
          b.anonymousKey,
        ),
    );

const results =
  aliasRecords.map(
    (
      user,
      index,
    ) => {
      const result =
        calculateTmuaPredictorV1(
          user.input,
        );

      const evidenceMode =
        result.testWeight > 0 &&
        result.qbWeight > 0
          ? "blended"
          : result.testWeight > 0
            ? "test_only"
            : result.qbWeight > 0
              ? "qb_only"
              : "insufficient";

      return {
        student:
          `student-${String(
            index + 1,
          ).padStart(
            3,
            "0",
          )}`,

        status:
          result.predictionStatus,

        mode:
          evidenceMode,

        predicted:
          result.predictedTmuaScore9,

        lower:
          result.lowerBound,

        upper:
          result.upperBound,

        confidence:
          result.confidence,

        tests:
          result.testEvidenceCount,

        independentTests:
          result.independentTestCount,

        combinedFull:
          result.combinedFullCount,

        testWeight:
          result.testWeight,

        qbUnique:
          result.qbUniqueQuestions,

        qbWeight:
          result.qbWeight,

        qbCoverage:
          result.qbTopicCoverage,

        testSd:
          result.diagnostics
            .testSignalStandardDeviation,

        trustedQbEvents:
          result.diagnostics
            .trustedQbEventCount,
      };
    },
  );

for (
  const result of results
) {
  if (
    result.predicted !== null &&
    (
      result.predicted < 1 ||
      result.predicted > 9
    )
  ) {
    throw new Error(
      "Shadow result escaped TMUA 1-9 range",
    );
  }
}

const predictions =
  results
    .map(
      (result) =>
        result.predicted,
    )
    .filter(
      (value) =>
        typeof value ===
        "number",
    );

const rangeWidths =
  results
    .filter(
      (result) =>
        result.lower !== null &&
        result.upper !== null,
    )
    .map(
      (result) =>
        result.upper -
        result.lower,
    );

function countWhere(
  predicate,
) {
  return results.filter(
    predicate,
  ).length;
}

const summary = {
  usersWithCapturedEvidence:
    results.length,

  predicted:
    countWhere(
      (row) =>
        row.status ===
        "predicted",
    ),

  insufficient:
    countWhere(
      (row) =>
        row.status ===
        "insufficient_evidence",
    ),

  modes: {
    testOnly:
      countWhere(
        (row) =>
          row.mode ===
          "test_only",
      ),

    qbOnly:
      countWhere(
        (row) =>
          row.mode ===
          "qb_only",
      ),

    blended:
      countWhere(
        (row) =>
          row.mode ===
          "blended",
      ),

    insufficient:
      countWhere(
        (row) =>
          row.mode ===
          "insufficient",
      ),
  },

  confidence: {
    low:
      countWhere(
        (row) =>
          row.confidence ===
          "low",
      ),

    medium:
      countWhere(
        (row) =>
          row.confidence ===
          "medium",
      ),

    high:
      countWhere(
        (row) =>
          row.confidence ===
          "high",
      ),
  },

  prediction: {
    minimum:
      predictions.length
        ? Math.min(
            ...predictions,
          )
        : null,

    median:
      median(
        predictions,
      ),

    mean:
      mean(
        predictions,
      ),

    maximum:
      predictions.length
        ? Math.max(
            ...predictions,
          )
        : null,
  },

  likelyRangeWidth: {
    minimum:
      rangeWidths.length
        ? Math.min(
            ...rangeWidths,
          )
        : null,

    median:
      median(
        rangeWidths,
      ),

    mean:
      mean(
        rangeWidths,
      ),

    maximum:
      rangeWidths.length
        ? Math.max(
            ...rangeWidths,
          )
        : null,
  },

  evidence: {
    maximumIndependentTests:
      results.length
        ? Math.max(
            ...results.map(
              (row) =>
                row.independentTests,
            ),
          )
        : 0,

    maximumQbUnique:
      results.length
        ? Math.max(
            ...results.map(
              (row) =>
                row.qbUnique,
            ),
          )
        : 0,

    usersWithCombinedFull:
      countWhere(
        (row) =>
          row.combinedFull >
          0,
      ),

    usersWithHighDispersion:
      countWhere(
        (row) =>
          row.testSd >
          1,
      ),
  },
};

function cleanNumbers(
  value,
) {
  if (Array.isArray(value)) {
    return value.map(
      cleanNumbers,
    );
  }

  if (
    value &&
    typeof value ===
      "object"
  ) {
    return Object.fromEntries(
      Object.entries(value)
        .map(
          ([key, nested]) => [
            key,
            cleanNumbers(
              nested,
            ),
          ],
        ),
    );
  }

  if (
    typeof value ===
      "number"
  ) {
    return round(
      value,
      4,
    );
  }

  return value;
}

console.log(
  "",
);

console.log(
  "TMUA PREDICTOR V1 SHADOW SUMMARY",
);

console.log(
  JSON.stringify(
    cleanNumbers(
      summary,
    ),
    null,
    2,
  ),
);

console.log(
  "",
);

console.log(
  "ANONYMISED STUDENT RESULTS",
);

for (
  const row of results
) {
  console.log(
    JSON.stringify(
      cleanNumbers(
        row,
      ),
    ),
  );
}

console.log(
  "",
);

console.log(
  "SHADOW RUN COMPLETE: READ-ONLY CALCULATION; ZERO SNAPSHOT WRITES.",
);