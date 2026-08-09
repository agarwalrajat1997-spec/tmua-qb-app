import fs from "node:fs";
import path from "node:path";

const root = process.cwd();

const specPath =
  path.join(
    root,
    "lib",
    "server",
    "tmua-predictor-v1-spec.json",
  );

const spec =
  JSON.parse(
    fs.readFileSync(
      specPath,
      "utf8",
    ),
  );

let assertions = 0;

function assert(condition, message) {
  assertions += 1;

  if (!condition) {
    throw new Error(message);
  }
}

function equal(actual, expected, message) {
  assert(
    Object.is(actual, expected),
    `${message}: expected ${expected}; received ${actual}`,
  );
}

function close(actual, expected, message, epsilon = 1e-9) {
  assert(
    Math.abs(actual - expected) <= epsilon,
    `${message}: expected ${expected}; received ${actual}`,
  );
}

function clamp(value, minimum, maximum) {
  return Math.max(
    minimum,
    Math.min(
      maximum,
      value,
    ),
  );
}

function qbScore(accuracy, recovery) {
  const f =
    spec.qb_evidence.score_formula;

  return clamp(
    f.intercept +
      f.accuracy_slope_per_percentage_point *
        (
          100 * accuracy -
          f.accuracy_center_percent
        ) +
      f.recovery_coefficient *
        (
          recovery -
          f.recovery_center
        ),
    f.minimum,
    f.maximum,
  );
}

function topicCoverageFactor(coverage) {
  const w =
    spec.qb_evidence.weight;

  return Math.max(
    w.topic_coverage_floor,
    Math.min(
      1,
      coverage,
    ),
  );
}

function rawQbWeight(
  uniqueQuestions,
  topicCoverage,
) {
  const w =
    spec.qb_evidence.weight;

  return (
    w.maximum *
    Math.min(
      1,
      uniqueQuestions /
        w.coverage_question_target,
    ) *
    topicCoverageFactor(
      topicCoverage,
    )
  );
}

function finalQbWeight(
  rawWeight,
  testWeight,
) {
  const ratio =
    spec.qb_evidence.weight
      .when_test_evidence_exists_cap_ratio_to_test_weight;

  if (testWeight <= 0) {
    return rawWeight;
  }

  return Math.min(
    rawWeight,
    ratio * testWeight,
  );
}

function collapseFamily(attempts) {
  assert(
    attempts.length >= 1,
    "Test family requires at least one eligible attempt",
  );

  if (attempts.length === 1) {
    return {
      signal: attempts[0].signal,
      weight: attempts[0].weight,
    };
  }

  const first =
    attempts[0];

  const latest =
    attempts[
      attempts.length - 1
    ];

  const policy =
    spec.test_family_policy
      .multiple_eligible_attempts;

  const firstMass =
    policy.first_coefficient *
    first.weight;

  const latestMass =
    policy.latest_coefficient *
    latest.weight;

  const familyWeight =
    firstMass +
    latestMass;

  return {
    signal:
      (
        firstMass *
          first.signal +
        latestMass *
          latest.signal
      ) /
      familyWeight,

    weight:
      familyWeight,
  };
}

function confidence(input) {
  const policy =
    spec.confidence;

  if (input.qbOnly) {
    return "low";
  }

  let level =
    "low";

  const high =
    policy.high;

  if (
    input.testFamilies >=
      high.minimum_independent_test_families &&
    input.broadFamilies >=
      high.minimum_broad_or_full_families &&
    input.testWeight >=
      high.minimum_test_weight
  ) {
    level =
      "high";
  }
  else {
    const medium =
      policy.medium_any;

    const mediumByTests =
      (
        input.testFamilies >=
          medium[0]
            .minimum_independent_test_families &&
        input.broadFamilies >=
          medium[0]
            .minimum_broad_or_full_families
      ) ||
      (
        input.testFamilies >=
          medium[1]
            .minimum_independent_test_families &&
        input.testWeight >=
          medium[1]
            .minimum_test_weight
      );

    const mediumByCombinedAndQb =
      input.combinedFullFamilies >=
        medium[2]
          .minimum_combined_full_families &&
      input.qbUnique >=
        medium[2]
          .minimum_qb_unique_questions &&
      input.qbCoverage >=
        medium[2]
          .minimum_qb_topic_coverage;

    if (
      mediumByTests ||
      mediumByCombinedAndQb
    ) {
      level =
        "medium";
    }
  }

  const dispersion =
    policy.test_dispersion;

  if (
    input.testSd >
    dispersion.force_low_above
  ) {
    return "low";
  }

  if (
    input.testSd >
    dispersion.downgrade_one_level_above
  ) {
    if (level === "high") {
      return "medium";
    }

    if (level === "medium") {
      return "low";
    }
  }

  return level;
}

function likelyHalfWidth(input) {
  const policy =
    spec.likely_range;

  let width =
    policy.base_half_width[
      input.confidence
    ];

  if (
    input.hasTestEvidence &&
    input.broadFamilies === 0
  ) {
    width +=
      policy
        .test_evidence_without_broad_or_full_penalty;
  }

  if (input.qbOnly) {
    width +=
      policy.qb_only_penalty;
  }

  if (
    Number.isFinite(
      input.testSd,
    )
  ) {
    width =
      Math.max(
        width,
        policy
          .dispersion_half_width_multiplier *
          input.testSd,
      );
  }

  return clamp(
    width,
    policy.minimum_half_width,
    policy.maximum_half_width,
  );
}

/*
 * ==========================================================
 * IDENTITY / SEPARATION
 * ==========================================================
 */

equal(
  spec.schema_version,
  1,
  "Specification schema version",
);

equal(
  spec.model_version,
  "tmua-predictor-v1.0.0",
  "Predictor model version",
);

equal(
  spec.score_scale.minimum,
  1,
  "TMUA score floor",
);

equal(
  spec.score_scale.maximum,
  9,
  "TMUA score ceiling",
);

assert(
  spec.separation
    .observed_score
    .never_replace_with_prediction === true,
  "Observed and predicted TMUA scores must remain separate",
);

assert(
  spec.separation
    .preparation_rank
    .not_part_of_predictor_v1 === true,
  "Preparation rank must remain outside Predictor V1",
);

/*
 * ==========================================================
 * TEST AUTHORITY
 * ==========================================================
 */

equal(
  spec.test_evidence.table,
  "tmua_test_attempt_evaluations",
  "Test evidence table",
);

assert(
  spec.test_evidence
    .require_predictor_eligible === true,
  "Tests must be predictor eligible",
);

assert(
  spec.test_evidence
    .recompute_validity === false,
  "Predictor must not duplicate upstream test validity",
);

assert(
  spec.test_evidence
    .combined_full
    .do_not_double_count_paper_components === true,
  "Combined full attempts must not double count paper components",
);

equal(
  spec.paper_normalization
    .expected_profile_count,
  12,
  "V1 conversion profile count",
);

equal(
  spec.paper_normalization
    .raw20_to_raw40_multiplier,
  2,
  "20-question normalization multiplier",
);

equal(
  spec.paper_normalization
    .profile_aggregation,
  "median",
  "Paper normalization aggregation",
);

assert(
  spec.paper_normalization
    .require_conversion_set_hash_in_provenance === true,
  "Conversion-set provenance hash is mandatory",
);

/*
 * ==========================================================
 * RETAKE POLICY
 * ==========================================================
 */

close(
  spec.test_family_policy
    .multiple_eligible_attempts
    .first_coefficient,
  0.75,
  "First valid exposure coefficient",
);

close(
  spec.test_family_policy
    .multiple_eligible_attempts
    .latest_coefficient,
  0.25,
  "Latest valid retake coefficient",
);

close(
  spec.test_family_policy
    .multiple_eligible_attempts
    .intermediate_coefficient,
  0,
  "Intermediate retake coefficient",
);

assert(
  spec.test_family_policy
    .repeated_attempts_do_not_increase_independent_test_count === true,
  "Retakes cannot manufacture independent evidence",
);

{
  const single =
    collapseFamily([
      {
        signal: 7,
        weight: 1,
      },
    ]);

  close(
    single.signal,
    7,
    "Single-attempt family signal",
  );

  close(
    single.weight,
    1,
    "Single-attempt family weight",
  );
}

{
  const family =
    collapseFamily([
      {
        signal: 6,
        weight: 1,
      },
      {
        signal: 5,
        weight: 1,
      },
      {
        signal: 8,
        weight: 1,
      },
    ]);

  close(
    family.signal,
    6.5,
    "75/25 retake signal",
  );

  close(
    family.weight,
    1,
    "Retake family does not gain evidence mass",
  );
}

{
  const family =
    collapseFamily([
      {
        signal: 6,
        weight: 0.5,
      },
      {
        signal: 7,
        weight: 0.9,
      },
      {
        signal: 8,
        weight: 1,
      },
    ]);

  close(
    family.signal,
    6.8,
    "Validity-weighted retake signal",
  );

  close(
    family.weight,
    0.625,
    "Validity-weighted family mass",
  );
}

/*
 * ==========================================================
 * QB TRUST
 * ==========================================================
 */

equal(
  spec.qb_evidence
    .trusted_event_predicates
    .source,
  "qb-progress-trigger-v2",
  "Trusted QB source",
);

equal(
  spec.qb_evidence
    .trusted_event_predicates
    .history_quality,
  "observed",
  "Trusted QB history quality",
);

assert(
  spec.qb_evidence
    .legacy_direct_source
    .predictor_authority === false,
  "Legacy direct QB events must have no predictor authority",
);

assert(
  spec.qb_evidence
    .legacy_direct_source
    .exclude_even_if_predictor_eligible === true,
  "Legacy direct QB events remain excluded even if their legacy flag is true",
);

equal(
  spec.qb_evidence
    .canonical_question
    .event_metadata_key,
  "canonical_qid",
  "Canonical QB identity key",
);

equal(
  spec.qb_evidence
    .canonical_question
    .table,
  "tmua_qb_questions",
  "Canonical QB table",
);

assert(
  spec.qb_evidence
    .correctness
    .event_is_correct_is_audit_only === true,
  "Event is_correct must not be scoring authority",
);

assert(
  spec.qb_evidence
    .correctness
    .client_topic_id_is_non_authoritative === true,
  "Client topic_id must not be topic authority",
);

assert(
  spec.qb_evidence
    .correctness
    .difficulty_weighting === false,
  "Predictor V1 must not invent item-difficulty weights",
);

assert(
  spec.qb_evidence
    .first_exposure
    .rank_before_predictor_eligibility_filter === true,
  "First exposure must be identified before eligibility filtering",
);

assert(
  spec.qb_evidence
    .first_exposure
    .later_attempt_cannot_replace_excluded_first_exposure === true,
  "Excluded first exposure cannot be replaced by a later familiar attempt",
);

equal(
  spec.qb_evidence
    .minimum_unique_questions_for_signal,
  30,
  "Minimum QB evidence gate",
);

equal(
  spec.qb_evidence
    .topic
    .minimum_first_exposures_to_count_topic,
  3,
  "Minimum topic evidence",
);

/*
 * ==========================================================
 * QB MATHEMATICS
 * ==========================================================
 */

close(
  spec.qb_evidence
    .balanced_accuracy
    .overall_weight +
  spec.qb_evidence
    .balanced_accuracy
    .lower_quartile_topic_weight,
  1,
  "Balanced-accuracy weights",
);

close(
  qbScore(
    0.55,
    0.5,
  ),
  4.5,
  "QB centre-point score",
);

close(
  qbScore(
    0.75,
    0.5,
  ),
  6.0,
  "QB 75% score",
);

close(
  qbScore(
    0.75,
    1.0,
  ),
  6.15,
  "QB recovery contribution",
);

close(
  qbScore(
    0,
    0,
  ),
  2.5,
  "QB lower clamp",
);

close(
  rawQbWeight(
    30,
    1,
  ),
  0.09,
  "QB weight at activation threshold with full topic coverage",
);

close(
  rawQbWeight(
    500,
    1,
  ),
  1.5,
  "Maximum QB weight",
);

close(
  rawQbWeight(
    500,
    0,
  ),
  0.375,
  "QB topic-concentration penalty",
);

close(
  finalQbWeight(
    1.5,
    1,
  ),
  0.6,
  "QB cannot overpower existing test evidence",
);

/*
 * ==========================================================
 * CONFIDENCE
 * ==========================================================
 */

equal(
  confidence({
    testFamilies: 1,
    broadFamilies: 1,
    combinedFullFamilies: 0,
    testWeight: 1,
    qbUnique: 0,
    qbCoverage: 0,
    testSd: 0,
    qbOnly: false,
  }),
  "low",
  "Single test remains low confidence",
);

equal(
  confidence({
    testFamilies: 1,
    broadFamilies: 1,
    combinedFullFamilies: 1,
    testWeight: 1,
    qbUnique: 100,
    qbCoverage: 0.5,
    testSd: 0,
    qbOnly: false,
  }),
  "medium",
  "Combined full plus meaningful QB is medium confidence",
);

equal(
  confidence({
    testFamilies: 3,
    broadFamilies: 1,
    combinedFullFamilies: 1,
    testWeight: 2,
    qbUnique: 0,
    qbCoverage: 0,
    testSd: 0.5,
    qbOnly: false,
  }),
  "high",
  "Three consistent independent tests can reach high confidence",
);

equal(
  confidence({
    testFamilies: 3,
    broadFamilies: 1,
    combinedFullFamilies: 1,
    testWeight: 2,
    qbUnique: 0,
    qbCoverage: 0,
    testSd: 1.2,
    qbOnly: false,
  }),
  "medium",
  "Test disagreement downgrades confidence",
);

equal(
  confidence({
    testFamilies: 0,
    broadFamilies: 0,
    combinedFullFamilies: 0,
    testWeight: 0,
    qbUnique: 500,
    qbCoverage: 1,
    testSd: 0,
    qbOnly: true,
  }),
  "low",
  "QB-only V1 prediction cannot exceed low confidence",
);

/*
 * ==========================================================
 * LIKELY RANGE
 * ==========================================================
 */

close(
  likelyHalfWidth({
    confidence: "low",
    hasTestEvidence: true,
    broadFamilies: 1,
    qbOnly: false,
    testSd: 0,
  }),
  1.2,
  "Low-confidence full/broad range",
);

close(
  likelyHalfWidth({
    confidence: "low",
    hasTestEvidence: true,
    broadFamilies: 0,
    qbOnly: false,
    testSd: 0,
  }),
  1.4,
  "Narrow-test uncertainty penalty",
);

close(
  likelyHalfWidth({
    confidence: "low",
    hasTestEvidence: false,
    broadFamilies: 0,
    qbOnly: true,
    testSd: 0,
  }),
  1.4,
  "QB-only uncertainty penalty",
);

close(
  likelyHalfWidth({
    confidence: "high",
    hasTestEvidence: true,
    broadFamilies: 1,
    qbOnly: false,
    testSd: 0.8,
  }),
  0.6,
  "High-confidence range still reflects dispersion",
);

/*
 * ==========================================================
 * BLENDING / SPARSE EVIDENCE
 * ==========================================================
 */

assert(
  spec.blend
    .no_test_and_insufficient_qb === null,
  "Insufficient evidence must produce no prediction rather than a fake baseline",
);

{
  const testSignal =
    6;

  const testWeight =
    2;

  const qbSignal =
    7;

  const qbWeight =
    finalQbWeight(
      1.5,
      testWeight,
    );

  const blended =
    (
      testSignal *
        testWeight +
      qbSignal *
        qbWeight
    ) /
    (
      testWeight +
      qbWeight
    );

  close(
    qbWeight,
    1.2,
    "QB cap in mixed-evidence fixture",
  );

  close(
    blended,
    6.375,
    "Mixed-evidence weighted prediction",
  );
}

/*
 * ==========================================================
 * SNAPSHOT / PROVENANCE
 * ==========================================================
 */

assert(
  spec.snapshot_policy
    .append_only === true,
  "Prediction snapshots must be append only",
);

assert(
  spec.snapshot_policy
    .deduplicate_identical_inputs === true,
  "Identical prediction inputs must deduplicate",
);

for (
  const required of [
    "model_version",
    "sorted_trusted_qb_evidence",
    "sorted_test_evidence",
    "conversion_set_hash",
    "active_topic_set_hash",
  ]
) {
  assert(
    spec.snapshot_policy
      .input_hash_must_include
      .includes(required),
    `Input hash is missing ${required}`,
  );
}

/*
 * ==========================================================
 * FORBIDDEN V1 BEHAVIOUR
 * ==========================================================
 */

for (
  const forbidden of [
    "client_authoritative_correctness",
    "client_authoritative_topic",
    "legacy_direct_qb_events_as_predictor_evidence",
    "qb_progress_as_historical_performance_evidence",
    "arbitrary_question_difficulty_weighting",
    "population_fitted_machine_learning",
    "retake_count_as_independent_evidence",
    "prediction_labelled_as_observed_score",
    "preparation_rank_inside_prediction_formula",
  ]
) {
  assert(
    spec.forbidden_in_v1
      .includes(forbidden),
    `Missing forbidden-policy invariant: ${forbidden}`,
  );
}

console.log(
  "TMUA Predictor V1 specification verification passed:",
);

console.log(
  `${assertions} invariants/fixtures verified; ` +
  "test validity remains upstream-authoritative; " +
  "retakes collapse to one test family; " +
  "QB requires trigger-v2 canonical evidence and 30 unique first exposures; " +
  "client correctness/topic fields are non-authoritative; " +
  "QB cannot overpower test evidence; " +
  "confidence/ranges are deterministic evidence labels; " +
  "prediction and preparation rank remain separate.",
);
