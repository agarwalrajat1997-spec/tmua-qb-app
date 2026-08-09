import fs from "node:fs";
import path from "node:path";

import {
  TMUA_PREDICTOR_V1_MODEL_VERSION,
  calculateTmuaPredictorV1,
  hashTmuaActiveTopics,
  hashTmuaConversionProfiles,
  normalizeTmuaPaperRaw20,
} from "../lib/server/tmua-predictor-v1-engine.ts";

const root =
  process.cwd();

const enginePath =
  path.join(
    root,
    "lib",
    "server",
    "tmua-predictor-v1-engine.ts",
  );

const specPath =
  path.join(
    root,
    "lib",
    "server",
    "tmua-predictor-v1-spec.json",
  );

const engineSource =
  fs.readFileSync(
    enginePath,
    "utf8",
  );

const spec =
  JSON.parse(
    fs
      .readFileSync(
        specPath,
        "utf8",
      )
      .replace(
        /^\uFEFF/,
        "",
      ),
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

function close(
  actual,
  expected,
  message,
  epsilon = 1e-9,
) {
  assert(
    Math.abs(
      actual -
      expected,
    ) <= epsilon,
    `${message}: expected ${expected}; received ${actual}`,
  );
}

function clone(
  value,
) {
  return JSON.parse(
    JSON.stringify(
      value,
    ),
  );
}

function makeProfiles() {
  return Array.from(
    {
      length: 12,
    },
    (
      _,
      profileIndex,
    ) => ({
      profileId:
        `profile-${String(
          profileIndex + 1,
        ).padStart(
          2,
          "0",
        )}`,

      scores:
        Array.from(
          {
            length: 41,
          },
          (
            _score,
            raw,
          ) => {
            const base =
              1 +
              8 *
                (
                  raw /
                  40
                );

            const offset =
              (
                profileIndex -
                5.5
              ) *
              0.01;

            return Math.max(
              1,
              Math.min(
                9,
                base +
                  offset,
              ),
            );
          },
        ),
    }),
  );
}

const profiles =
  makeProfiles();

const activeTopics =
  [
    "Algebra",
    "Sequences",
    "Geometry",
    "Trigonometry",
  ];

function testAttempt(
  overrides = {},
) {
  return {
    testId:
      "official-1",

    attemptId:
      "attempt-1",

    attemptNumber:
      1,

    evaluatedAt:
      "2026-08-01T10:00:00.000Z",

    predictorEligible:
      true,

    topicBreadth:
      "full_syllabus",

    combinedScoreEligible:
      true,

    authoritativeTmuaScore9:
      7,

    effectiveWeight:
      1,

    paper1RawScore:
      null,

    paper1EffectiveWeight:
      null,

    paper2RawScore:
      null,

    paper2EffectiveWeight:
      null,

    ...overrides,
  };
}

function qbEvent(
  index,
  overrides = {},
) {
  const day =
    String(
      1 +
      Math.floor(
        index /
        24,
      ),
    ).padStart(
      2,
      "0",
    );

  const hour =
    String(
      index %
        24,
    ).padStart(
      2,
      "0",
    );

  return {
    id:
      `qb-${index}`,

    source:
      "qb-progress-trigger-v2",

    historyQuality:
      "observed",

    predictorEligible:
      true,

    canonicalQid:
      `Q${index}`,

    canonicalActive:
      true,

    selectedAnswer:
      index % 4 === 0
        ? "B"
        : "A",

    canonicalAnswer:
      "A",

    canonicalTopic:
      activeTopics[
        index %
          activeTopics.length
      ],

    attemptedAt:
      `2026-08-${day}T${hour}:00:00.000Z`,

    claimedIsCorrect:
      null,

    clientTopicId:
      null,

    ...overrides,
  };
}

function makeQbEvents(
  count,
) {
  return Array.from(
    {
      length: count,
    },
    (
      _,
      index,
    ) =>
      qbEvent(
        index + 1,
      ),
  );
}

function run(
  {
    tests = [],
    qb = [],
    curves = profiles,
    topics = activeTopics,
  } = {},
) {
  return calculateTmuaPredictorV1({
    testAttempts:
      tests,

    qbEvents:
      qb,

    conversionProfiles:
      curves,

    activeTopics:
      topics,
  });
}

/*
 * ==========================================================
 * SOURCE PURITY
 * ==========================================================
 */

assert(
  !engineSource.includes(
    "@supabase",
  ),
  "Pure engine must not import Supabase",
);

assert(
  !engineSource.includes(
    ".from(",
  ),
  "Pure engine must not query database tables",
);

assert(
  !engineSource.includes(
    "fetch(",
  ),
  "Pure engine must not make network requests",
);

assert(
  !engineSource.includes(
    "process.env",
  ),
  "Pure engine must not depend on environment variables",
);

assert(
  !engineSource.includes(
    "tmua_prediction_snapshots",
  ),
  "Pure engine must not write or reference snapshot storage",
);

/*
 * ==========================================================
 * LOCKED SPEC IDENTITY
 * ==========================================================
 */

equal(
  TMUA_PREDICTOR_V1_MODEL_VERSION,
  spec.model_version,
  "Engine model version must match locked specification",
);

equal(
  spec.qb_evidence
    .minimum_unique_questions_for_signal,
  30,
  "Locked QB activation threshold",
);

equal(
  spec.test_family_policy
    .multiple_eligible_attempts
    .first_coefficient,
  0.75,
  "Locked first retake coefficient",
);

equal(
  spec.test_family_policy
    .multiple_eligible_attempts
    .latest_coefficient,
  0.25,
  "Locked latest retake coefficient",
);

equal(
  spec.qb_evidence
    .weight
    .when_test_evidence_exists_cap_ratio_to_test_weight,
  0.6,
  "Locked QB-to-test weight cap",
);

equal(
  spec.paper_normalization
    .expected_profile_count,
  12,
  "Locked conversion-profile cardinality",
);

/*
 * ==========================================================
 * CONVERSION PROFILE CONTRACT
 * ==========================================================
 */

close(
  normalizeTmuaPaperRaw20(
    10,
    profiles,
  ),
  5,
  "Raw 10/20 maps to median synthetic 5.0",
);

close(
  normalizeTmuaPaperRaw20(
    20,
    profiles,
  ),
  8.9975,
  "Raw 20/20 respects median of bounded profile set",
);

{
  const eleven =
    profiles.slice(
      0,
      11,
    );

  let threw =
    false;

  try {
    normalizeTmuaPaperRaw20(
      10,
      eleven,
    );
  }
  catch {
    threw =
      true;
  }

  assert(
    threw,
    "Engine must fail closed unless exactly 12 profiles are supplied",
  );
}

{
  const malformed =
    clone(
      profiles,
    );

  malformed[0]
    .scores =
      malformed[0]
        .scores
        .slice(
          0,
          40,
        );

  let threw =
    false;

  try {
    normalizeTmuaPaperRaw20(
      10,
      malformed,
    );
  }
  catch {
    threw =
      true;
  }

  assert(
    threw,
    "Every profile must contain all 41 raw-score points",
  );
}

/*
 * ==========================================================
 * SPARSE EVIDENCE
 * ==========================================================
 */

{
  const result =
    run();

  equal(
    result.predictionStatus,
    "insufficient_evidence",
    "No evidence",
  );

  equal(
    result.predictedTmuaScore9,
    null,
    "No evidence must not produce fake baseline score",
  );

  equal(
    result.confidence,
    null,
    "No evidence must not receive confidence",
  );
}

{
  const result =
    run({
      qb:
        makeQbEvents(
          29,
        ),
    });

  equal(
    result.qbUniqueQuestions,
    29,
    "29 trusted unique first exposures counted",
  );

  equal(
    result.qbSignalScore9,
    null,
    "29 questions cannot activate QB signal",
  );

  equal(
    result.qbWeight,
    0,
    "29 questions have zero QB weight",
  );

  equal(
    result.predictionStatus,
    "insufficient_evidence",
    "29 QB questions alone remain insufficient",
  );
}

{
  const result =
    run({
      qb:
        makeQbEvents(
          30,
        ),
    });

  equal(
    result.qbUniqueQuestions,
    30,
    "30 unique trusted first exposures counted",
  );

  assert(
    result.qbSignalScore9 !==
      null,
    "30 questions activate QB signal",
  );

  assert(
    result.qbWeight > 0,
    "30 questions activate positive QB weight",
  );

  equal(
    result.predictionStatus,
    "predicted",
    "30-question QB-only evidence produces a prediction",
  );

  equal(
    result.confidence,
    "low",
    "QB-only prediction cannot exceed low confidence",
  );
}

/*
 * ==========================================================
 * TEST AUTHORITY
 * ==========================================================
 */

{
  const result =
    run({
      tests: [
        testAttempt({
          authoritativeTmuaScore9:
            7.2,
        }),
      ],
    });

  close(
    result.testSignalScore9,
    7.2,
    "Single authoritative full test signal",
  );

  close(
    result.predictedTmuaScore9,
    7.2,
    "Test-only prediction equals authoritative test signal",
  );

  equal(
    result.confidence,
    "low",
    "Single independent test remains low confidence",
  );

  equal(
    result.independentTestCount,
    1,
    "Single test gives one independent family",
  );
}

{
  const result =
    run({
      tests: [
        testAttempt({
          authoritativeTmuaScore9:
            7,

          paper1RawScore:
            0,

          paper1EffectiveWeight:
            1,

          paper2RawScore:
            0,

          paper2EffectiveWeight:
            1,
        }),
      ],
    });

  close(
    result.testSignalScore9,
    7,
    "Authoritative combined /9 must override paper components",
  );
}

{
  const result =
    run({
      tests: [
        testAttempt({
          combinedScoreEligible:
            false,

          authoritativeTmuaScore9:
            null,

          paper1RawScore:
            10,

          paper1EffectiveWeight:
            1,

          paper2RawScore:
            null,

          paper2EffectiveWeight:
            null,

          effectiveWeight:
            1,
        }),
      ],
    });

  close(
    result.testSignalScore9,
    5,
    "Paper-only evidence uses median twelve-profile normalization",
  );
}

/*
 * ==========================================================
 * RETAKE ANTI-GAMING
 * ==========================================================
 */

{
  const attempts =
    [
      6,
      5,
      9,
      4,
      8,
    ].map(
      (
        score,
        index,
      ) =>
        testAttempt({
          attemptId:
            `retake-${index + 1}`,

          attemptNumber:
            index + 1,

          evaluatedAt:
            `2026-08-0${index + 1}T10:00:00.000Z`,

          authoritativeTmuaScore9:
            score,
        }),
    );

  const result =
    run({
      tests:
        attempts,
    });

  equal(
    result.testEvidenceCount,
    5,
    "All five eligible attempts remain visible in provenance",
  );

  equal(
    result.independentTestCount,
    1,
    "Five attempts of same test remain one independent family",
  );

  close(
    result.testSignalScore9,
    6.5,
    "Only first and latest retake contribute 75/25",
  );

  close(
    result.testWeight,
    1,
    "Repeated unit-weight attempts do not manufacture extra evidence mass",
  );
}

{
  const result =
    run({
      tests: [
        testAttempt({
          attemptId:
            "weighted-first",

          attemptNumber:
            1,

          authoritativeTmuaScore9:
            6,

          effectiveWeight:
            0.5,
        }),

        testAttempt({
          attemptId:
            "weighted-middle",

          attemptNumber:
            2,

          authoritativeTmuaScore9:
            9,

          effectiveWeight:
            1,
        }),

        testAttempt({
          attemptId:
            "weighted-latest",

          attemptNumber:
            3,

          authoritativeTmuaScore9:
            8,

          effectiveWeight:
            1,
        }),
      ],
    });

  close(
    result.testSignalScore9,
    6.8,
    "Retake calculation respects upstream effective weights",
  );

  close(
    result.testWeight,
    0.625,
    "Retake family mass is coefficient-weighted and not farmable",
  );
}

/*
 * ==========================================================
 * CONFIDENCE + DISPERSION
 * ==========================================================
 */

{
  const result =
    run({
      tests: [
        testAttempt({
          testId:
            "test-a",

          attemptId:
            "a",

          authoritativeTmuaScore9:
            6.8,
        }),

        testAttempt({
          testId:
            "test-b",

          attemptId:
            "b",

          authoritativeTmuaScore9:
            7,
        }),

        testAttempt({
          testId:
            "test-c",

          attemptId:
            "c",

          authoritativeTmuaScore9:
            7.2,
        }),
      ],
    });

  equal(
    result.independentTestCount,
    3,
    "Three separate test ids create three independent families",
  );

  equal(
    result.confidence,
    "high",
    "Three consistent broad/full tests can reach high confidence",
  );
}

{
  const result =
    run({
      tests: [
        testAttempt({
          testId:
            "test-a",

          attemptId:
            "a",

          authoritativeTmuaScore9:
            4,
        }),

        testAttempt({
          testId:
            "test-b",

          attemptId:
            "b",

          authoritativeTmuaScore9:
            7,
        }),

        testAttempt({
          testId:
            "test-c",

          attemptId:
            "c",

          authoritativeTmuaScore9:
            9,
        }),
      ],
    });

  equal(
    result.confidence,
    "low",
    "Large disagreement forces confidence to low",
  );

  assert(
    result.diagnostics
      .testSignalStandardDeviation >
      1.5,
    "Inconsistent fixture must exceed force-low dispersion threshold",
  );
}

/*
 * ==========================================================
 * QB SERVER AUTHORITY
 * ==========================================================
 */

{
  const base =
    makeQbEvents(
      40,
    );

  const forged =
    clone(
      base,
    ).map(
      (event) => ({
        ...event,

        claimedIsCorrect:
          !(
            event.selectedAnswer ===
            event.canonicalAnswer
          ),

        clientTopicId:
          "FORGED_TOPIC",
      }));

  const originalResult =
    run({
      qb:
        base,
    });

  const forgedResult =
    run({
      qb:
        forged,
    });

  equal(
    forgedResult.qbSignalScore9,
    originalResult.qbSignalScore9,
    "Client claimed correctness cannot alter QB signal",
  );

  equal(
    forgedResult.qbTopicCoverage,
    originalResult.qbTopicCoverage,
    "Client topic id cannot alter canonical topic coverage",
  );

  equal(
    forgedResult.inputHash,
    originalResult.inputHash,
    "Ignored forged audit/client fields do not alter authoritative input hash",
  );
}

/*
 * ==========================================================
 * FIRST EXPOSURE BEFORE ELIGIBILITY
 * ==========================================================
 */

{
  const events =
    makeQbEvents(
      29,
    );

  events.push(
    qbEvent(
      1000,
      {
        id:
          "blocked-first",

        canonicalQid:
          "BLOCKED-Q",

        predictorEligible:
          false,

        selectedAnswer:
          "A",

        canonicalAnswer:
          "A",

        attemptedAt:
          "2026-08-01T00:00:00.000Z",
      },
    ),
  );

  events.push(
    qbEvent(
      1001,
      {
        id:
          "later-familiar",

        canonicalQid:
          "BLOCKED-Q",

        predictorEligible:
          true,

        selectedAnswer:
          "A",

        canonicalAnswer:
          "A",

        attemptedAt:
          "2026-08-03T00:00:00.000Z",
      },
    ),
  );

  const result =
    run({
      qb:
        events,
    });

  equal(
    result.qbUniqueQuestions,
    29,
    "Ineligible first exposure blocks later attempt from masquerading as first exposure",
  );

  equal(
    result.predictionStatus,
    "insufficient_evidence",
    "Blocked familiar retry cannot create 30th eligible first exposure",
  );
}

/*
 * ==========================================================
 * RECOVERY
 * ==========================================================
 */

{
  const events =
    makeQbEvents(
      30,
    );

  /*
   * Make Q1 the sole initially-wrong question in this fixture.
   * That makes recovery fraction 0 before the valid retry
   * and exactly 1 after the >=24-hour correct retry.
   */
  for (
    const event of events
  ) {
    event.selectedAnswer =
      "A";

    event.canonicalAnswer =
      "A";
  }

  events[0] = {
    ...events[0],

    selectedAnswer:
      "B",

    canonicalAnswer:
      "A",

    attemptedAt:
      "2026-08-01T00:00:00.000Z",
  };

  events.push(
    {
      ...events[0],

      id:
        "too-early-recovery",

      selectedAnswer:
        "A",

      attemptedAt:
        "2026-08-01T12:00:00.000Z",
    },
  );

  const early =
    run({
      qb:
        events,
    });

  events.push(
    {
      ...events[0],

      id:
        "valid-recovery",

      selectedAnswer:
        "A",

      attemptedAt:
        "2026-08-02T00:00:00.000Z",
    },
  );

  const recovered =
    run({
      qb:
        events,
    });

  close(
    early.diagnostics
      .qbRecoveryFraction,
    0,
    "Recovery before 24 hours does not count",
  );

  close(
    recovered.diagnostics
      .qbRecoveryFraction,
    1,
    "Recovery at 24 hours counts",
  );

  assert(
    recovered.qbSignalScore9 >
      early.qbSignalScore9,
    "Valid delayed recovery modestly improves QB signal",
  );
}

/*
 * ==========================================================
 * QB CANNOT OVERPOWER TESTS
 * ==========================================================
 */

{
  const result =
    run({
      tests: [
        testAttempt({
          authoritativeTmuaScore9:
            8,
        }),
      ],

      qb:
        makeQbEvents(
          500,
        ),
    });

  assert(
    result.qbWeight <=
      0.6 *
        result.testWeight +
        1e-9,
    "Final QB weight must never exceed 60% of test weight",
  );

  assert(
    result.predictedTmuaScore9 >=
      1 &&
      result.predictedTmuaScore9 <=
        9,
    "Mixed prediction remains on TMUA 1-9 scale",
  );
}

/*
 * ==========================================================
 * HASH / PROVENANCE DETERMINISM
 * ==========================================================
 */

{
  const originalHash =
    hashTmuaConversionProfiles(
      profiles,
    );

  const reorderedHash =
    hashTmuaConversionProfiles(
      [...profiles].reverse(),
    );

  equal(
    originalHash,
    reorderedHash,
    "Conversion-set hash is profile-order independent",
  );

  const changed =
    clone(
      profiles,
    );

  changed[0]
    .scores[20] +=
      0.01;

  const changedHash =
    hashTmuaConversionProfiles(
      changed,
    );

  assert(
    changedHash !==
      originalHash,
    "Conversion curve change alters conversion-set provenance",
  );
}

{
  const first =
    hashTmuaActiveTopics(
      activeTopics,
    );

  const reordered =
    hashTmuaActiveTopics(
      [
        ...activeTopics,
      ].reverse(),
    );

  equal(
    first,
    reordered,
    "Active-topic-set hash is order independent",
  );
}

{
  const tests = [
    testAttempt({
      testId:
        "hash-a",

      attemptId:
        "hash-attempt-a",
    }),

    testAttempt({
      testId:
        "hash-b",

      attemptId:
        "hash-attempt-b",

      authoritativeTmuaScore9:
        6.5,
    }),
  ];

  const qb =
    makeQbEvents(
      35,
    );

  const first =
    run({
      tests,
      qb,
    });

  const reordered =
    run({
      tests:
        [...tests].reverse(),

      qb:
        [...qb].reverse(),

      curves:
        [...profiles].reverse(),

      topics:
        [...activeTopics].reverse(),
    });

  equal(
    reordered.inputHash,
    first.inputHash,
    "Equivalent evidence produces same input hash regardless of input ordering",
  );

  equal(
    reordered.predictedTmuaScore9,
    first.predictedTmuaScore9,
    "Equivalent reordered evidence produces identical prediction",
  );
}

{
  const first =
    run({
      tests: [
        testAttempt(),
      ],
    });

  const changedProfiles =
    clone(
      profiles,
    );

  changedProfiles[0]
    .scores[20] +=
      0.01;

  const second =
    run({
      tests: [
        testAttempt(),
      ],

      curves:
        changedProfiles,
    });

  assert(
    first.conversionSetHash !==
      second.conversionSetHash,
    "Conversion-set provenance changes when curve changes",
  );

  assert(
    first.inputHash !==
      second.inputHash,
    "Input hash changes when conversion-set provenance changes",
  );
}

/*
 * ==========================================================
 * BOUNDS
 * ==========================================================
 */

for (
  const score of [
    1,
    1.1,
    5,
    8.9,
    9,
  ]
) {
  const result =
    run({
      tests: [
        testAttempt({
          authoritativeTmuaScore9:
            score,
        }),
      ],
    });

  assert(
    result.predictedTmuaScore9 >=
      1 &&
      result.predictedTmuaScore9 <=
        9,
    `Prediction ${score} must remain bounded`,
  );

  assert(
    result.lowerBound >=
      1 &&
      result.lowerBound <=
        result.predictedTmuaScore9,
    `Lower range bound for ${score} must be valid`,
  );

  assert(
    result.upperBound <=
      9 &&
      result.upperBound >=
        result.predictedTmuaScore9,
    `Upper range bound for ${score} must be valid`,
  );
}

/*
 * ==========================================================
 * LEGACY DIRECT QB EVENTS EXCLUDED
 * ==========================================================
 */

{
  const legacy =
    makeQbEvents(
      100,
    ).map(
      (event) => ({
        ...event,

        source:
          "tmua-question-bank",

        claimedIsCorrect:
          true,
      }));

  const result =
    run({
      qb:
        legacy,
    });

  equal(
    result.diagnostics
      .trustedQbEventCount,
    0,
    "Legacy direct QB events have zero Predictor V1 authority",
  );

  equal(
    result.predictionStatus,
    "insufficient_evidence",
    "Legacy direct QB history cannot create a prediction",
  );
}

/*
 * ==========================================================
 * INELIGIBLE TESTS EXCLUDED
 * ==========================================================
 */

{
  const result =
    run({
      tests: [
        testAttempt({
          predictorEligible:
            false,

          authoritativeTmuaScore9:
            9,
        }),
      ],
    });

  equal(
    result.testEvidenceCount,
    0,
    "Upstream-ineligible test is excluded",
  );

  equal(
    result.predictionStatus,
    "insufficient_evidence",
    "Excluded test cannot create predictor evidence",
  );
}

console.log(
  "TMUA Predictor V1 engine verification passed:",
);

console.log(
  `${assertions} invariants/fixtures verified; ` +
  "the engine is pure and database-independent; " +
  "combined full tests retain authoritative /9 scoring; " +
  "paper evidence uses the median of exactly 12 conversion profiles; " +
  "retakes collapse to one 75/25 family; " +
  "legacy/direct and forged QB authority is excluded; " +
  "first exposure is fixed before eligibility filtering; " +
  "recovery requires 24 hours; " +
  "QB activates at 30 unique questions and is capped against test evidence; " +
  "confidence responds to independent evidence and dispersion; " +
  "provenance hashes are deterministic and order-independent.",
);