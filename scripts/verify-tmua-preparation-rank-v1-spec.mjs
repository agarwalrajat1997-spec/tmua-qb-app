import fs from "node:fs";
import path from "node:path";

const root = process.cwd();

const specPath =
  path.join(
    root,
    "lib",
    "server",
    "tmua-preparation-rank-v1-spec.json",
  );

const packagePath =
  path.join(
    root,
    "package.json",
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
    `${message}; expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`,
  );
}

function approx(actual, expected, message, tolerance = 1e-9) {
  assert(
    Number.isFinite(actual) &&
      Math.abs(actual - expected) <= tolerance,
    `${message}; expected approximately ${expected}, got ${actual}`,
  );
}

function clamp(value, minimum = 0, maximum = 1) {
  return Math.min(
    maximum,
    Math.max(
      minimum,
      value,
    ),
  );
}

assert(
  fs.existsSync(specPath),
  "Preparation Rank V1 specification file must exist",
);

const spec =
  JSON.parse(
    fs.readFileSync(
      specPath,
      "utf8",
    ),
  );

equal(
  spec.model,
  "TMUA Preparation Rank V1",
  "model name is locked",
);

equal(
  spec.model_version,
  "tmua-preparation-rank-v1-20260810",
  "model version is locked",
);

equal(
  spec.status,
  "locked",
  "model status is locked",
);

equal(
  spec.separation.predictor_is_separate,
  true,
  "Predictor must remain separate",
);

equal(
  spec.separation.preparation_rank_is_not_tmua_score,
  true,
  "Preparation Rank cannot be presented as TMUA score",
);

equal(
  spec.separation.preparation_rank_is_not_candidate_percentile,
  true,
  "Preparation Rank cannot be candidate percentile",
);

equal(
  spec.separation.preparation_rank_must_not_be_called_tmua_rank,
  true,
  "Preparation Rank cannot be called TMUA rank",
);

equal(
  spec.separation.predictor_v1_must_not_be_modified_by_rank_model,
  true,
  "Preparation Rank cannot modify Predictor V1",
);

const weights =
  spec.score.weights;

equal(
  weights.predicted_tmua_performance,
  0.70,
  "Predictor weight",
);

equal(
  weights.syllabus_breadth,
  0.10,
  "breadth weight",
);

equal(
  weights.evidence_depth,
  0.08,
  "evidence-depth weight",
);

equal(
  weights.recent_activity,
  0.06,
  "activity weight",
);

equal(
  weights.consistency,
  0.03,
  "consistency weight",
);

equal(
  weights.recovery,
  0.03,
  "recovery weight",
);

approx(
  Object.values(weights)
    .reduce(
      (sum, value) => sum + value,
      0,
    ),
  1,
  "weights must sum to exactly 100%",
);

equal(
  spec.score.scale_min,
  0,
  "score minimum",
);

equal(
  spec.score.scale_max,
  100,
  "score maximum",
);

equal(
  spec.score.rank_uses_unrounded_score,
  true,
  "ranking must use unrounded score",
);

equal(
  spec.score.performance.formula,
  "clamp((predicted_tmua_score9 - 1) / 8, 0, 1)",
  "performance formula",
);

equal(
  spec.score.performance.missing_prediction_value,
  0,
  "missing Predictor contributes zero performance",
);

equal(
  spec.score.performance.fake_baseline_forbidden,
  true,
  "fake Predictor baseline is forbidden",
);

equal(
  spec.score.breadth.test_formula,
  "min(1, broad_or_full_independent_test_families / 2)",
  "test breadth formula",
);

equal(
  spec.score.breadth.qb_formula,
  "clamp(trusted_canonical_topic_coverage, 0, 1)",
  "QB breadth formula",
);

equal(
  spec.score.breadth.combined_formula,
  "1 - (1 - test_breadth) * (1 - qb_breadth)",
  "combined breadth formula",
);

equal(
  spec.score.breadth.test_families_must_be_predictor_eligible,
  true,
  "breadth test families must be predictor eligible",
);

equal(
  spec.score.breadth.qb_topics_are_server_canonical,
  true,
  "QB breadth must use canonical server topics",
);

equal(
  spec.score.breadth.qb_topic_denominator_matches_predictor_active_topic_definition,
  true,
  "QB topic denominator must match Predictor V1",
);

equal(
  spec.score.evidence_depth.test_formula,
  "min(1, predictor_test_family_weight / 2)",
  "test depth formula",
);

equal(
  spec.score.evidence_depth.qb_formula,
  "min(1, trusted_unique_first_exposures / 150)",
  "QB depth formula",
);

equal(
  spec.score.evidence_depth.combined_formula,
  "1 - (1 - test_depth) * (1 - qb_depth)",
  "combined depth formula",
);

equal(
  spec.score.evidence_depth.retakes_do_not_create_independent_depth,
  true,
  "retakes cannot manufacture evidence depth",
);

equal(
  spec.score.recent_activity.window_days,
  30,
  "activity window",
);

equal(
  spec.score.recent_activity.qb_formula,
  "min(1, distinct_canonical_qb_interactions_30d / 60)",
  "QB activity formula",
);

equal(
  spec.score.recent_activity.test_formula,
  "min(1, independent_recognised_test_families_30d / 2)",
  "test activity formula",
);

equal(
  spec.score.recent_activity.combined_formula,
  "0.70 * qb_activity + 0.30 * test_activity",
  "combined activity formula",
);

equal(
  spec.score.recent_activity.activity_is_separate_from_predictor_eligibility,
  true,
  "activity and Predictor eligibility are separate",
);

equal(
  spec.score.recent_activity.predictor_ineligible_activity_may_count_as_activity,
  true,
  "ineligible attempts may still count as activity",
);

equal(
  spec.score.recent_activity.activity_alone_cannot_create_a_preparation_score,
  true,
  "activity alone cannot create a score",
);

equal(
  spec.score.consistency.two_or_more_family_formula,
  "max(0, 1 - weighted_population_test_family_sd / 1.5)",
  "consistency formula",
);

equal(
  spec.score.consistency.fewer_than_two_with_genuine_evidence,
  0.5,
  "low-family neutral consistency",
);

equal(
  spec.score.consistency.no_genuine_evidence,
  0,
  "zero-evidence consistency",
);

equal(
  spec.score.consistency.sd_uses_predictor_v1_family_signals,
  true,
  "consistency uses Predictor family signals",
);

equal(
  spec.score.recovery.uses_predictor_v1_trusted_recovery_definition,
  true,
  "recovery definition must match Predictor V1",
);

equal(
  spec.score.recovery.genuine_qb_evidence_required,
  true,
  "recovery requires genuine QB evidence",
);

equal(
  spec.score.recovery.no_wrong_first_opportunity_value,
  0.5,
  "neutral recovery",
);

equal(
  spec.score.recovery.no_genuine_qb_evidence_value,
  0,
  "test-only recovery",
);

equal(
  spec.score.recovery.minimum_recovery_delay_hours,
  24,
  "recovery delay",
);

equal(
  spec.score.genuine_preparation_evidence.zero_evidence_internal_score,
  0,
  "internal zero-evidence score",
);

equal(
  spec.score.genuine_preparation_evidence.public_score_without_genuine_evidence,
  null,
  "public zero-evidence score must be absent",
);

equal(
  spec.score.genuine_preparation_evidence.public_rank_without_genuine_evidence,
  null,
  "public zero-evidence rank must be absent",
);

function performance(predictedTmuaScore9) {
  if (
    predictedTmuaScore9 == null
  ) {
    return 0;
  }

  return clamp(
    (predictedTmuaScore9 - 1) / 8,
  );
}

function breadth({
  broadOrFullFamilies,
  qbTopicCoverage,
}) {
  const test =
    Math.min(
      1,
      Math.max(
        0,
        broadOrFullFamilies,
      ) / 2,
    );

  const qb =
    clamp(
      qbTopicCoverage,
    );

  return (
    1 -
    (1 - test) *
      (1 - qb)
  );
}

function depth({
  testWeight,
  trustedUnique,
}) {
  const test =
    Math.min(
      1,
      Math.max(
        0,
        testWeight,
      ) / 2,
    );

  const qb =
    Math.min(
      1,
      Math.max(
        0,
        trustedUnique,
      ) / 150,
    );

  return (
    1 -
    (1 - test) *
      (1 - qb)
  );
}

function activity({
  qbUnique30d,
  testFamilies30d,
}) {
  const qb =
    Math.min(
      1,
      Math.max(
        0,
        qbUnique30d,
      ) / 60,
    );

  const tests =
    Math.min(
      1,
      Math.max(
        0,
        testFamilies30d,
      ) / 2,
    );

  return (
    0.70 * qb +
    0.30 * tests
  );
}

function consistency({
  genuineEvidence,
  familyCount,
  familySd,
}) {
  if (!genuineEvidence) {
    return 0;
  }

  if (familyCount < 2) {
    return 0.5;
  }

  assert(
    Number.isFinite(familySd),
    "two or more family signals require finite SD",
  );

  return Math.max(
    0,
    1 - familySd / 1.5,
  );
}

function recovery({
  hasGenuineQbEvidence,
  recoveryValue,
}) {
  if (!hasGenuineQbEvidence) {
    return 0;
  }

  if (recoveryValue == null) {
    return 0.5;
  }

  return clamp(
    recoveryValue,
  );
}

function preparation(input) {
  const genuineEvidence =
    Boolean(
      input.hasGenuineTestEvidence ||
      input.hasGenuineQbEvidence
    );

  if (!genuineEvidence) {
    return {
      publicScore: null,
      internalScore: 0,
      rankEligible: false,
    };
  }

  const P =
    performance(
      input.predictedTmuaScore9,
    );

  const B =
    breadth({
      broadOrFullFamilies:
        input.broadOrFullFamilies,
      qbTopicCoverage:
        input.qbTopicCoverage,
    });

  const D =
    depth({
      testWeight:
        input.testWeight,
      trustedUnique:
        input.trustedUnique,
    });

  const A =
    activity({
      qbUnique30d:
        input.qbUnique30d,
      testFamilies30d:
        input.testFamilies30d,
    });

  const C =
    consistency({
      genuineEvidence,
      familyCount:
        input.familyCount,
      familySd:
        input.familySd,
    });

  const R =
    recovery({
      hasGenuineQbEvidence:
        input.hasGenuineQbEvidence,
      recoveryValue:
        input.recoveryValue,
    });

  const score =
    100 * (
      0.70 * P +
      0.10 * B +
      0.08 * D +
      0.06 * A +
      0.03 * C +
      0.03 * R
    );

  return {
    publicScore: score,
    internalScore: score,
    rankEligible: true,
    components: {
      P,
      B,
      D,
      A,
      C,
      R,
    },
  };
}

approx(
  performance(1),
  0,
  "TMUA 1.0 normalises to zero",
);

approx(
  performance(5),
  0.5,
  "TMUA 5.0 normalises to one-half",
);

approx(
  performance(9),
  1,
  "TMUA 9.0 normalises to one",
);

approx(
  performance(null),
  0,
  "missing Predictor score contributes zero",
);

approx(
  performance(-5),
  0,
  "performance clamps below scale",
);

approx(
  performance(12),
  1,
  "performance clamps above scale",
);

approx(
  breadth({
    broadOrFullFamilies: 0,
    qbTopicCoverage: 0,
  }),
  0,
  "zero breadth",
);

approx(
  breadth({
    broadOrFullFamilies: 1,
    qbTopicCoverage: 0,
  }),
  0.5,
  "one broad family gives half test breadth",
);

approx(
  breadth({
    broadOrFullFamilies: 2,
    qbTopicCoverage: 0,
  }),
  1,
  "two broad families saturate test breadth",
);

approx(
  breadth({
    broadOrFullFamilies: 1,
    qbTopicCoverage: 0.5,
  }),
  0.75,
  "breadth combines complementary sources",
);

approx(
  depth({
    testWeight: 1,
    trustedUnique: 75,
  }),
  0.75,
  "depth combines half test and half QB evidence",
);

approx(
  depth({
    testWeight: 2,
    trustedUnique: 0,
  }),
  1,
  "test depth saturates at weight two",
);

approx(
  depth({
    testWeight: 0,
    trustedUnique: 150,
  }),
  1,
  "QB depth saturates at 150 unique questions",
);

approx(
  activity({
    qbUnique30d: 30,
    testFamilies30d: 1,
  }),
  0.5,
  "half QB and half test activity gives one-half activity",
);

approx(
  activity({
    qbUnique30d: 600,
    testFamilies30d: 20,
  }),
  1,
  "activity clamps at one",
);

approx(
  consistency({
    genuineEvidence: true,
    familyCount: 1,
    familySd: null,
  }),
  0.5,
  "single-family consistency is neutral",
);

approx(
  consistency({
    genuineEvidence: true,
    familyCount: 2,
    familySd: 0,
  }),
  1,
  "zero dispersion gives maximum consistency",
);

approx(
  consistency({
    genuineEvidence: true,
    familyCount: 2,
    familySd: 0.75,
  }),
  0.5,
  "SD 0.75 gives one-half consistency",
);

approx(
  consistency({
    genuineEvidence: true,
    familyCount: 2,
    familySd: 3,
  }),
  0,
  "large dispersion floors consistency at zero",
);

approx(
  consistency({
    genuineEvidence: false,
    familyCount: 0,
    familySd: null,
  }),
  0,
  "login-only activity earns no consistency",
);

approx(
  recovery({
    hasGenuineQbEvidence: false,
    recoveryValue: null,
  }),
  0,
  "test-only evidence earns no recovery component",
);

approx(
  recovery({
    hasGenuineQbEvidence: true,
    recoveryValue: null,
  }),
  0.5,
  "QB evidence with no wrong-first opportunity is neutral",
);

approx(
  recovery({
    hasGenuineQbEvidence: true,
    recoveryValue: 0.8,
  }),
  0.8,
  "trusted recovery passes through",
);

const balancedFixture =
  preparation({
    predictedTmuaScore9: 5,
    broadOrFullFamilies: 1,
    qbTopicCoverage: 0.5,
    testWeight: 1,
    trustedUnique: 75,
    qbUnique30d: 30,
    testFamilies30d: 1,
    familyCount: 1,
    familySd: null,
    hasGenuineTestEvidence: true,
    hasGenuineQbEvidence: true,
    recoveryValue: 0.8,
  });

approx(
  balancedFixture.publicScore,
  55.4,
  "balanced fixture score",
);

equal(
  balancedFixture.rankEligible,
  true,
  "genuine evidence is rank eligible",
);

const qbBelowPredictorThreshold =
  preparation({
    predictedTmuaScore9: null,
    broadOrFullFamilies: 0,
    qbTopicCoverage: 0.25,
    testWeight: 0,
    trustedUnique: 20,
    qbUnique30d: 20,
    testFamilies30d: 0,
    familyCount: 0,
    familySd: null,
    hasGenuineTestEvidence: false,
    hasGenuineQbEvidence: true,
    recoveryValue: null,
  });

assert(
  qbBelowPredictorThreshold.publicScore > 0,
  "genuine QB evidence may create Preparation Score before Predictor activation",
);

assert(
  qbBelowPredictorThreshold.publicScore < 20,
  "small QB-only evidence cannot create a large Preparation Score fixture",
);

const loginOnlyFixture =
  preparation({
    predictedTmuaScore9: null,
    broadOrFullFamilies: 0,
    qbTopicCoverage: 0,
    testWeight: 0,
    trustedUnique: 0,
    qbUnique30d: 60,
    testFamilies30d: 0,
    familyCount: 0,
    familySd: null,
    hasGenuineTestEvidence: false,
    hasGenuineQbEvidence: false,
    recoveryValue: null,
  });

equal(
  loginOnlyFixture.publicScore,
  null,
  "activity without genuine evidence has no public Preparation Score",
);

equal(
  loginOnlyFixture.internalScore,
  0,
  "activity without evidence has internal zero",
);

equal(
  loginOnlyFixture.rankEligible,
  false,
  "activity without evidence cannot receive rank",
);

function activeCohortMember({
  entitled,
  signedIn30d,
  recognisedTestActivity30d,
  qbInteraction30d,
  explicitlyExcluded,
}) {
  if (!entitled) {
    return false;
  }

  if (explicitlyExcluded) {
    return false;
  }

  return Boolean(
    signedIn30d ||
    recognisedTestActivity30d ||
    qbInteraction30d
  );
}

equal(
  activeCohortMember({
    entitled: true,
    signedIn30d: true,
    recognisedTestActivity30d: false,
    qbInteraction30d: false,
    explicitlyExcluded: false,
  }),
  true,
  "signed-in entitled student belongs to active cohort",
);

equal(
  activeCohortMember({
    entitled: true,
    signedIn30d: false,
    recognisedTestActivity30d: false,
    qbInteraction30d: true,
    explicitlyExcluded: false,
  }),
  true,
  "QB interaction can establish active cohort membership",
);

equal(
  activeCohortMember({
    entitled: false,
    signedIn30d: true,
    recognisedTestActivity30d: true,
    qbInteraction30d: true,
    explicitlyExcluded: false,
  }),
  false,
  "TMUA entitlement is mandatory",
);

equal(
  activeCohortMember({
    entitled: true,
    signedIn30d: true,
    recognisedTestActivity30d: true,
    qbInteraction30d: true,
    explicitlyExcluded: true,
  }),
  false,
  "explicit staff/internal exclusion wins",
);

equal(
  spec.cohort.window_days,
  30,
  "cohort window",
);

equal(
  spec.cohort.tmua_entitlement_required,
  true,
  "cohort requires TMUA entitlement",
);

equal(
  spec.cohort.activity_does_not_require_predictor_eligibility,
  true,
  "cohort activity is separate from Predictor eligibility",
);

equal(
  spec.cohort.under_10_second_qb_interaction_can_count_as_active,
  true,
  "fast QB interaction may count as active",
);

equal(
  spec.cohort.under_10_second_qb_interaction_cannot_become_predictor_evidence,
  true,
  "fast QB interaction cannot become Predictor evidence",
);

equal(
  spec.cohort.explicit_staff_internal_exclusion_required,
  true,
  "staff/internal exclusion must be explicit",
);

equal(
  spec.cohort.email_heuristic_exclusion_forbidden,
  true,
  "email heuristics are forbidden",
);

equal(
  spec.cohort.entitlement_and_staff_sources_resolved_in_phase_3c1,
  true,
  "3C1 must resolve entitlement and staff sources",
);

equal(
  spec.ranking.active_login_only_user_counts_in_cohort_denominator,
  true,
  "login-only active users stay in cohort denominator",
);

equal(
  spec.ranking.active_login_only_user_receives_rank,
  false,
  "login-only users receive no Preparation Rank",
);

equal(
  spec.ranking.tie_method,
  "competition",
  "tie ranking method",
);

equal(
  JSON.stringify(
    spec.ranking.tie_example,
  ),
  JSON.stringify(
    [1, 2, 2, 4],
  ),
  "tie example",
);

equal(
  spec.ranking.display_rounding_must_not_affect_rank,
  true,
  "display rounding cannot affect rank",
);

function competitionRanks(scores) {
  const ordered =
    [...scores]
      .sort(
        (a, b) =>
          b.score - a.score,
      );

  let previousScore = null;
  let previousRank = 0;

  return ordered.map(
    (entry, index) => {
      const rank =
        previousScore !== null &&
        Object.is(
          entry.score,
          previousScore,
        )
          ? previousRank
          : index + 1;

      previousScore =
        entry.score;

      previousRank =
        rank;

      return {
        id: entry.id,
        score: entry.score,
        rank,
      };
    },
  );
}

const ranks =
  competitionRanks([
    {
      id: "a",
      score: 80.0001,
    },
    {
      id: "b",
      score: 80,
    },
    {
      id: "c",
      score: 80,
    },
    {
      id: "d",
      score: 79.9999,
    },
  ]);

equal(
  ranks[0].rank,
  1,
  "highest score rank",
);

equal(
  ranks[1].rank,
  2,
  "first tied score rank",
);

equal(
  ranks[2].rank,
  2,
  "second tied score rank",
);

equal(
  ranks[3].rank,
  4,
  "competition ranking skips rank three",
);

assert(
  ranks[0].rank !==
    ranks[1].rank,
  "scores that merely round to the same display value must not tie",
);

equal(
  spec.privacy.other_student_uuid_exposure_forbidden,
  true,
  "other student UUIDs are private",
);

equal(
  spec.privacy.other_student_score_exposure_forbidden,
  true,
  "other student scores are private",
);

equal(
  spec.privacy.named_leaderboard_requires_explicit_opt_in,
  true,
  "named leaderboard requires opt-in",
);

equal(
  spec.privacy.public_population_percentile_claims_forbidden,
  true,
  "public candidate percentile claims are forbidden",
);

equal(
  spec.integrity.actual_score_field,
  "actualPreparationScore",
  "actual score field",
);

equal(
  spec.integrity.actual_rank_field,
  "actualPreparationRank",
  "actual rank field",
);

equal(
  spec.integrity.actual_cohort_field,
  "actualActiveCohortSize",
  "actual cohort field",
);

equal(
  spec.integrity.display_multiplier_default,
  1,
  "display multiplier defaults to one",
);

equal(
  spec.integrity.non_unit_display_scaling_must_be_explicitly_labelled_scaled_or_indexed,
  true,
  "scaled/indexed displays must be labelled",
);

equal(
  spec.integrity.scaled_values_must_not_replace_actual_values,
  true,
  "scaled values cannot overwrite actual values",
);

equal(
  spec.integrity.fake_rank_forbidden,
  true,
  "fake ranks are forbidden",
);

equal(
  spec.integrity.fake_cohort_size_forbidden,
  true,
  "fake cohort sizes are forbidden",
);

equal(
  spec.integrity.fake_preparation_score_forbidden,
  true,
  "fake Preparation Scores are forbidden",
);

equal(
  spec.future_persistence.append_only,
  true,
  "future persistence is append-only",
);

equal(
  spec.future_persistence.versioned_model_required,
  true,
  "future snapshots require model version",
);

equal(
  spec.future_persistence.no_schema_created_in_phase_3c0,
  true,
  "3C0 creates no schema",
);

equal(
  spec.phase_3c0.specification_only,
  true,
  "3C0 is specification-only",
);

equal(
  spec.phase_3c0.database_changes,
  false,
  "3C0 has no database changes",
);

equal(
  spec.phase_3c0.runtime_changes,
  false,
  "3C0 has no runtime changes",
);

equal(
  spec.phase_3c0.dashboard_changes,
  false,
  "3C0 has no dashboard changes",
);

equal(
  spec.phase_3c0.production_deployment,
  false,
  "3C0 has no production deployment",
);

const packageJson =
  JSON.parse(
    fs.readFileSync(
      packagePath,
      "utf8",
    ),
  );

equal(
  packageJson.scripts[
    "verify:tmua-preparation-rank-v1-spec"
  ],
  "node scripts/verify-tmua-preparation-rank-v1-spec.mjs",
  "package verifier command",
);

const prebuildToken =
  "npm run verify:tmua-preparation-rank-v1-spec";

equal(
  packageJson.scripts.prebuild
    .split(prebuildToken)
    .length - 1,
  1,
  "prebuild must contain Preparation Rank verifier exactly once",
);

console.log(
  "TMUA Preparation Rank V1 specification verification passed:",
);

console.log(
  `${assertions} invariants/fixtures verified; ` +
  "Preparation Rank remains separate from Predictor V1; " +
  "the score weights are locked at 70/10/8/6/3/3; " +
  "breadth, depth, activity, consistency and recovery are deterministic; " +
  "login-only users can count in the active denominator but cannot receive a rank; " +
  "competition ties use unrounded scores; " +
  "privacy forbids exposing other students' UUIDs/scores; " +
  "actual cohort/rank values cannot be silently scaled or fabricated; " +
  "Phase 3C0 remains specification-only.",
);
