import fs from "node:fs";

import {
  calculateTmuaPredictorV1,
} from "../lib/server/tmua-predictor-v1-engine.ts";

import {
  buildTmuaPredictionSnapshotInsert,
} from "../lib/server/tmua-predictor-v1-snapshot.ts";

const source =
  fs.readFileSync(
    "lib/server/tmua-predictor-v1-snapshot.ts",
    "utf8",
  );

let assertions =
  0;

function assert(
  condition,
  message,
) {
  assertions += 1;

  if (!condition) {
    throw new Error(
      message,
    );
  }
}

function equal(
  actual,
  expected,
  message,
) {
  assert(
    Object.is(
      actual,
      expected,
    ),
    `${message}: expected ${expected}; received ${actual}`,
  );
}

function profiles() {
  return Array.from(
    {
      length: 12,
    },
    (
      _,
      index,
    ) => ({
      profileId:
        `profile-${index + 1}`,

      scores:
        Array.from(
          {
            length: 41,
          },
          (
            _unused,
            raw,
          ) =>
            1 +
            8 *
              (
                raw /
                40
              ),
        ),
    }),
  );
}

assert(
  !source.includes(
    "@supabase",
  ),
  "Snapshot mapper remains database-client independent",
);

assert(
  !source.includes(
    "fetch(",
  ),
  "Snapshot mapper must not make network requests",
);

assert(
  !source.includes(
    "process.env",
  ),
  "Snapshot mapper must not depend on environment",
);

const predictedResult =
  calculateTmuaPredictorV1({
    conversionProfiles:
      profiles(),

    activeTopics: [
      "Algebra",
    ],

    qbEvents: [],

    testAttempts: [
      {
        testId:
          "full-test",

        attemptId:
          "attempt-1",

        attemptNumber:
          1,

        evaluatedAt:
          "2026-08-10T00:00:00.000Z",

        predictorEligible:
          true,

        topicBreadth:
          "full_syllabus",

        combinedScoreEligible:
          true,

        authoritativeTmuaScore9:
          7.2,

        effectiveWeight:
          1,

        paper1RawScore:
          15,

        paper1EffectiveWeight:
          1,

        paper2RawScore:
          14,

        paper2EffectiveWeight:
          1,
      },
    ],
  });

const predicted =
  buildTmuaPredictionSnapshotInsert(
    "user-a",
    predictedResult,
    "2026-08-10T01:02:03Z",
  );

equal(
  predicted.userId,
  "user-a",
  "User identity is preserved separately",
);

equal(
  predicted.predictionStatus,
  "predicted",
  "Predicted status maps exactly",
);

equal(
  predicted.predictedTmuaScore9,
  7.2,
  "Predicted score maps exactly",
);

equal(
  predicted.testSignalScore9,
  7.2,
  "Test signal maps exactly",
);

equal(
  predicted.testWeight,
  1,
  "Test weight maps exactly",
);

equal(
  predicted.qbWeight,
  0,
  "Unused QB weight remains zero",
);

equal(
  predicted.inputHash,
  predictedResult.inputHash,
  "Input hash maps exactly",
);

equal(
  predicted.conversionSetHash,
  predictedResult.conversionSetHash,
  "Conversion provenance maps exactly",
);

equal(
  predicted.activeTopicSetHash,
  predictedResult.activeTopicSetHash,
  "Topic provenance maps exactly",
);

equal(
  predicted.calculatedAt,
  "2026-08-10T01:02:03.000Z",
  "Timestamp canonicalizes deterministically",
);

equal(
  predicted.evidenceDetails.input_hash,
  predicted.inputHash,
  "Diagnostic provenance includes the same input hash",
);

const insufficientResult =
  calculateTmuaPredictorV1({
    conversionProfiles:
      profiles(),

    activeTopics: [
      "Algebra",
    ],

    testAttempts: [],

    qbEvents: [],
  });

const insufficient =
  buildTmuaPredictionSnapshotInsert(
    "user-b",
    insufficientResult,
    "2026-08-10T01:02:03Z",
  );

equal(
  insufficient.predictionStatus,
  "insufficient_evidence",
  "Insufficient state maps exactly",
);

equal(
  insufficient.predictedTmuaScore9,
  null,
  "Insufficient state has no synthetic prediction",
);

equal(
  insufficient.lowerBound,
  null,
  "Insufficient state has no lower bound",
);

equal(
  insufficient.upperBound,
  null,
  "Insufficient state has no upper bound",
);

equal(
  insufficient.confidence,
  null,
  "Insufficient state has no confidence label",
);

equal(
  insufficient.testWeight,
  0,
  "Insufficient state has zero test weight",
);

equal(
  insufficient.qbWeight,
  0,
  "Insufficient state has zero QB weight",
);

assert(
  JSON.parse(
    JSON.stringify(
      predicted.evidenceDetails,
    ),
  ) !== null,
  "Evidence details are JSON serializable",
);

console.log(
  "TMUA Predictor V1 snapshot-mapper verification passed:",
);

console.log(
  `${assertions} invariants verified; ` +
  "predicted and insufficient states map exactly; " +
  "no baseline score is invented; " +
  "typed score/weight/count provenance is preserved; " +
  "diagnostic evidence remains JSON serializable; " +
  "the mapper has no database/network dependency.",
);