import { createHash } from "node:crypto";

export const TMUA_PREDICTOR_V1_MODEL_VERSION =
  "tmua-predictor-v1.0.0";

const SCORE_MINIMUM = 1;
const SCORE_MAXIMUM = 9;

const PAPER_PROFILE_COUNT = 12;
const PAPER_PROFILE_CARDINALITY = 41;

const FAMILY_WEIGHT_MAXIMUM = 1.5;

const FIRST_RETAKE_COEFFICIENT = 0.75;
const LATEST_RETAKE_COEFFICIENT = 0.25;

const QB_MINIMUM_UNIQUE = 30;
const QB_FULL_WEIGHT_UNIQUE = 500;

const QB_WEIGHT_MAXIMUM = 1.5;
const QB_TEST_WEIGHT_CAP_RATIO = 0.6;
const QB_TOPIC_COVERAGE_FLOOR = 0.25;

const QB_OVERALL_ACCURACY_WEIGHT = 0.7;
const QB_LOWER_QUARTILE_WEIGHT = 0.3;

const QB_SCORE_INTERCEPT = 4.5;
const QB_ACCURACY_CENTER_PERCENT = 55;
const QB_ACCURACY_SLOPE = 0.075;
const QB_RECOVERY_CENTER = 0.5;
const QB_RECOVERY_COEFFICIENT = 0.3;
const QB_SCORE_MINIMUM = 2.5;
const QB_SCORE_MAXIMUM = 8.5;

const RECOVERY_MINIMUM_HOURS = 24;

const CONFIDENCE_HIGH_MINIMUM_FAMILIES = 3;
const CONFIDENCE_HIGH_MINIMUM_BROAD = 1;
const CONFIDENCE_HIGH_MINIMUM_TEST_WEIGHT = 1.5;

const DISPERSION_DOWNGRADE_THRESHOLD = 1.0;
const DISPERSION_FORCE_LOW_THRESHOLD = 1.5;

export type TmuaConversionProfile = {
  profileId: string;
  scores: number[];
};

export type TmuaPredictorTestAttempt = {
  testId: string;
  attemptId: string;
  attemptNumber: number | null;
  evaluatedAt: string;

  predictorEligible: boolean;

  topicBreadth:
    | "full_syllabus"
    | "broad"
    | "narrow"
    | string;

  combinedScoreEligible: boolean;
  authoritativeTmuaScore9: number | null;

  effectiveWeight: number | null;

  paper1RawScore: number | null;
  paper1EffectiveWeight: number | null;

  paper2RawScore: number | null;
  paper2EffectiveWeight: number | null;
};

export type TmuaPredictorQbEvent = {
  id: string;

  source: string;
  historyQuality: string;

  predictorEligible: boolean;

  canonicalQid: string | null;
  canonicalActive: boolean;

  selectedAnswer: string | null;
  canonicalAnswer: string | null;

  canonicalTopic: string | null;

  attemptedAt: string;

  /*
   * Deliberately ignored audit/client fields.
   * Fixtures exercise these to prove they have no authority.
   */
  claimedIsCorrect?: boolean | null;
  clientTopicId?: string | null;
};

export type TmuaPredictorInput = {
  testAttempts: TmuaPredictorTestAttempt[];
  qbEvents: TmuaPredictorQbEvent[];

  conversionProfiles: TmuaConversionProfile[];

  activeTopics: string[];
};

export type TmuaPredictionStatus =
  | "predicted"
  | "insufficient_evidence";

export type TmuaPredictionConfidence =
  | "low"
  | "medium"
  | "high";

type NormalizedTestAttempt = {
  testId: string;
  attemptId: string;
  attemptNumber: number | null;
  evaluatedAt: string;

  signal: number;
  weight: number;

  broadOrFull: boolean;
  combinedFull: boolean;
};

type TestFamily = {
  testId: string;
  signal: number;
  weight: number;

  broadOrFull: boolean;
  combinedFull: boolean;

  eligibleAttemptCount: number;
};

type TrustedQbEvent = {
  id: string;
  canonicalQid: string;

  predictorEligible: boolean;

  selectedAnswer: string | null;
  canonicalAnswer: string | null;
  canonicalTopic: string | null;

  attemptedAt: string;
};

export type TmuaPredictorResult = {
  modelVersion: string;

  predictionStatus: TmuaPredictionStatus;

  predictedTmuaScore9: number | null;
  lowerBound: number | null;
  upperBound: number | null;

  confidence: TmuaPredictionConfidence | null;

  testSignalScore9: number | null;
  testWeight: number;
  testEvidenceCount: number;
  independentTestCount: number;
  combinedFullCount: number;

  qbSignalScore9: number | null;
  qbWeight: number;
  qbUniqueQuestions: number;
  qbTopicCoverage: number;

  conversionSetHash: string;
  activeTopicSetHash: string;
  inputHash: string;

  diagnostics: {
    broadTestFamilyCount: number;
    testSignalStandardDeviation: number;

    qbOverallAccuracy: number | null;
    qbLowerQuartileTopicAccuracy: number | null;
    qbBalancedAccuracy: number | null;
    qbRecoveryFraction: number | null;
    qbRecoveryOpportunityCount: number;

    trustedQbEventCount: number;
    eligibleFirstExposureCount: number;

    testFamilies: Array<{
      testId: string;
      signal: number;
      weight: number;
      broadOrFull: boolean;
      combinedFull: boolean;
      eligibleAttemptCount: number;
    }>;
  };
};

function assertFiniteNumber(
  value: number,
  label: string,
): void {
  if (!Number.isFinite(value)) {
    throw new Error(
      `${label} must be finite`,
    );
  }
}

function clamp(
  value: number,
  minimum: number,
  maximum: number,
): number {
  return Math.max(
    minimum,
    Math.min(
      maximum,
      value,
    ),
  );
}

function round(
  value: number,
  decimals: number,
): number {
  const factor =
    10 ** decimals;

  return (
    Math.round(
      (value + Number.EPSILON) *
        factor,
    ) /
    factor
  );
}

function normalizeText(
  value: string | null,
): string {
  return (
    value ??
    ""
  )
    .trim();
}

function normalizeAnswer(
  value: string | null,
): string {
  return normalizeText(
    value,
  ).toUpperCase();
}

function canonicalJson(
  value: unknown,
): string {
  if (
    value === null ||
    typeof value !== "object"
  ) {
    const encoded =
      JSON.stringify(
        value,
      );

    if (
      encoded === undefined
    ) {
      throw new Error(
        "Unsupported undefined value in canonical JSON",
      );
    }

    return encoded;
  }

  if (Array.isArray(value)) {
    return (
      "[" +
      value
        .map(
          canonicalJson,
        )
        .join(",") +
      "]"
    );
  }

  const object =
    value as Record<
      string,
      unknown
    >;

  return (
    "{" +
    Object.keys(object)
      .sort()
      .map(
        (key) =>
          JSON.stringify(key) +
          ":" +
          canonicalJson(
            object[key],
          ),
      )
      .join(",") +
    "}"
  );
}

function sha256(
  value: unknown,
): string {
  return createHash(
    "sha256",
  )
    .update(
      canonicalJson(value),
      "utf8",
    )
    .digest(
      "hex",
    );
}

function parseTimestamp(
  value: string,
  label: string,
): number {
  const timestamp =
    Date.parse(value);

  if (!Number.isFinite(timestamp)) {
    throw new Error(
      `${label} is not a valid timestamp`,
    );
  }

  return timestamp;
}

function median(
  values: number[],
): number {
  if (values.length === 0) {
    throw new Error(
      "Cannot calculate median of empty input",
    );
  }

  const sorted =
    [...values].sort(
      (a, b) =>
        a - b,
    );

  const middle =
    Math.floor(
      sorted.length / 2,
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

function weightedMean(
  pairs: Array<{
    value: number;
    weight: number;
  }>,
): number {
  const usable =
    pairs.filter(
      ({ value, weight }) =>
        Number.isFinite(value) &&
        Number.isFinite(weight) &&
        weight > 0,
    );

  if (usable.length === 0) {
    throw new Error(
      "Weighted mean has no positive-weight observations",
    );
  }

  const totalWeight =
    usable.reduce(
      (sum, item) =>
        sum + item.weight,
      0,
    );

  return (
    usable.reduce(
      (sum, item) =>
        sum +
        item.value *
          item.weight,
      0,
    ) /
    totalWeight
  );
}

function weightedPopulationSd(
  pairs: Array<{
    value: number;
    weight: number;
  }>,
): number {
  const usable =
    pairs.filter(
      ({ value, weight }) =>
        Number.isFinite(value) &&
        Number.isFinite(weight) &&
        weight > 0,
    );

  if (usable.length <= 1) {
    return 0;
  }

  const mean =
    weightedMean(
      usable,
    );

  const totalWeight =
    usable.reduce(
      (sum, item) =>
        sum +
        item.weight,
      0,
    );

  const variance =
    usable.reduce(
      (sum, item) =>
        sum +
        item.weight *
          (
            item.value -
            mean
          ) ** 2,
      0,
    ) /
    totalWeight;

  return Math.sqrt(
    variance,
  );
}

function validateConversionProfiles(
  profiles: TmuaConversionProfile[],
): TmuaConversionProfile[] {
  if (
    profiles.length !==
    PAPER_PROFILE_COUNT
  ) {
    throw new Error(
      `Predictor V1 requires exactly ${PAPER_PROFILE_COUNT} conversion profiles; received ${profiles.length}`,
    );
  }

  const sorted =
    [...profiles].sort(
      (a, b) =>
        a.profileId.localeCompare(
          b.profileId,
        ),
    );

  const seen =
    new Set<string>();

  for (
    const profile of sorted
  ) {
    const profileId =
      normalizeText(
        profile.profileId,
      );

    if (!profileId) {
      throw new Error(
        "Conversion profile id cannot be empty",
      );
    }

    if (
      seen.has(profileId)
    ) {
      throw new Error(
        `Duplicate conversion profile ${profileId}`,
      );
    }

    seen.add(
      profileId,
    );

    if (
      profile.scores.length !==
      PAPER_PROFILE_CARDINALITY
    ) {
      throw new Error(
        `Conversion profile ${profileId} must contain ${PAPER_PROFILE_CARDINALITY} scores`,
      );
    }

    for (
      let raw = 0;
      raw <
        profile.scores.length;
      raw += 1
    ) {
      const score =
        profile.scores[
          raw
        ];

      assertFiniteNumber(
        score,
        `${profileId}[${raw}]`,
      );

      if (
        score <
          SCORE_MINIMUM ||
        score >
          SCORE_MAXIMUM
      ) {
        throw new Error(
          `Conversion profile ${profileId} raw ${raw} is outside 1-9`,
        );
      }
    }
  }

  return sorted;
}

export function hashTmuaConversionProfiles(
  profiles: TmuaConversionProfile[],
): string {
  const validated =
    validateConversionProfiles(
      profiles,
    );

  return sha256(
    validated.map(
      (profile) => ({
        profileId:
          normalizeText(
            profile.profileId,
          ),
        scores:
          profile.scores,
      }),
    ),
  );
}

function canonicalActiveTopics(
  topics: string[],
): string[] {
  return [
    ...new Set(
      topics
        .map(
          (topic) =>
            normalizeText(
              topic,
            ),
        )
        .filter(Boolean),
    ),
  ].sort(
    (a, b) =>
      a.localeCompare(b),
  );
}

export function hashTmuaActiveTopics(
  topics: string[],
): string {
  return sha256(
    canonicalActiveTopics(
      topics,
    ),
  );
}

export function normalizeTmuaPaperRaw20(
  rawScore20: number,
  profiles: TmuaConversionProfile[],
): number {
  assertFiniteNumber(
    rawScore20,
    "rawScore20",
  );

  if (
    !Number.isInteger(
      rawScore20,
    ) ||
    rawScore20 < 0 ||
    rawScore20 > 20
  ) {
    throw new Error(
      "Paper raw score must be an integer from 0 to 20",
    );
  }

  const validated =
    validateConversionProfiles(
      profiles,
    );

  const raw40 =
    rawScore20 * 2;

  const scores =
    validated.map(
      (profile) =>
        profile.scores[
          raw40
        ],
    );

  return median(
    scores,
  );
}

function positiveWeight(
  preferred: number | null,
  fallback: number | null,
): number | null {
  /*
   * A present zero is authoritative: that component contributed
   * no usable evidence. Fallback is permitted only when the
   * component-specific field is genuinely absent/null.
   *
   * This matches the live evaluation schema, where an unused
   * paper is represented as raw_score = 0 and effective_weight = 0.
   */
  if (
    preferred !== null
  ) {
    return (
      Number.isFinite(
        preferred,
      ) &&
      preferred > 0
    )
      ? preferred
      : null;
  }

  if (
    fallback !== null &&
    Number.isFinite(
      fallback,
    ) &&
    fallback > 0
  ) {
    return fallback;
  }

  return null;
}

function isBroadOrFull(
  topicBreadth: string,
): boolean {
  return (
    topicBreadth ===
      "full_syllabus" ||
    topicBreadth ===
      "broad"
  );
}

function normalizeTestAttempt(
  attempt: TmuaPredictorTestAttempt,
  profiles: TmuaConversionProfile[],
): NormalizedTestAttempt | null {
  if (
    !attempt.predictorEligible
  ) {
    return null;
  }

  const testId =
    normalizeText(
      attempt.testId,
    );

  const attemptId =
    normalizeText(
      attempt.attemptId,
    );

  if (
    !testId ||
    !attemptId
  ) {
    return null;
  }

  parseTimestamp(
    attempt.evaluatedAt,
    `test ${attemptId} evaluatedAt`,
  );

  const broadOrFull =
    isBroadOrFull(
      attempt.topicBreadth,
    );

  if (
    attempt.combinedScoreEligible &&
    attempt.authoritativeTmuaScore9 !== null
  ) {
    const score =
      attempt.authoritativeTmuaScore9;

    const weight =
      positiveWeight(
        attempt.effectiveWeight,
        null,
      );

    if (
      Number.isFinite(score) &&
      score >= SCORE_MINIMUM &&
      score <= SCORE_MAXIMUM &&
      weight !== null
    ) {
      return {
        testId,
        attemptId,
        attemptNumber:
          attempt.attemptNumber,
        evaluatedAt:
          attempt.evaluatedAt,

        signal:
          score,

        weight,

        broadOrFull,
        combinedFull: true,
      };
    }

    return null;
  }

  const components: Array<{
    value: number;
    weight: number;
  }> = [];

  if (
    attempt.paper1RawScore !== null
  ) {
    const weight =
      positiveWeight(
        attempt.paper1EffectiveWeight,
        attempt.effectiveWeight,
      );

    if (weight !== null) {
      components.push({
        value:
          normalizeTmuaPaperRaw20(
            attempt.paper1RawScore,
            profiles,
          ),
        weight,
      });
    }
  }

  if (
    attempt.paper2RawScore !== null
  ) {
    const weight =
      positiveWeight(
        attempt.paper2EffectiveWeight,
        attempt.effectiveWeight,
      );

    if (weight !== null) {
      components.push({
        value:
          normalizeTmuaPaperRaw20(
            attempt.paper2RawScore,
            profiles,
          ),
        weight,
      });
    }
  }

  if (
    components.length === 0
  ) {
    return null;
  }

  const signal =
    weightedMean(
      components,
    );

  const weight =
    components.reduce(
      (sum, item) =>
        sum +
        item.weight,
      0,
    );

  return {
    testId,
    attemptId,
    attemptNumber:
      attempt.attemptNumber,
    evaluatedAt:
      attempt.evaluatedAt,

    signal,
    weight,

    broadOrFull,
    combinedFull: false,
  };
}

function compareTestAttempts(
  a: NormalizedTestAttempt,
  b: NormalizedTestAttempt,
): number {
  const aAttempt =
    a.attemptNumber ??
    Number.MAX_SAFE_INTEGER;

  const bAttempt =
    b.attemptNumber ??
    Number.MAX_SAFE_INTEGER;

  if (
    aAttempt !==
    bAttempt
  ) {
    return (
      aAttempt -
      bAttempt
    );
  }

  const timeDifference =
    parseTimestamp(
      a.evaluatedAt,
      "evaluatedAt",
    ) -
    parseTimestamp(
      b.evaluatedAt,
      "evaluatedAt",
    );

  if (
    timeDifference !== 0
  ) {
    return timeDifference;
  }

  return a.attemptId.localeCompare(
    b.attemptId,
  );
}

function collapseTestFamily(
  attempts: NormalizedTestAttempt[],
): TestFamily {
  if (
    attempts.length === 0
  ) {
    throw new Error(
      "Cannot collapse empty test family",
    );
  }

  const sorted =
    [...attempts].sort(
      compareTestAttempts,
    );

  const broadOrFull =
    sorted.some(
      (attempt) =>
        attempt.broadOrFull,
    );

  const combinedFull =
    sorted.some(
      (attempt) =>
        attempt.combinedFull,
    );

  if (
    sorted.length === 1
  ) {
    return {
      testId:
        sorted[0].testId,

      signal:
        sorted[0].signal,

      weight:
        Math.min(
          FAMILY_WEIGHT_MAXIMUM,
          sorted[0].weight,
        ),

      broadOrFull,
      combinedFull,

      eligibleAttemptCount: 1,
    };
  }

  const first =
    sorted[0];

  const latest =
    sorted[
      sorted.length - 1
    ];

  const firstMass =
    FIRST_RETAKE_COEFFICIENT *
    first.weight;

  const latestMass =
    LATEST_RETAKE_COEFFICIENT *
    latest.weight;

  const totalMass =
    firstMass +
    latestMass;

  const signal =
    (
      first.signal *
        firstMass +
      latest.signal *
        latestMass
    ) /
    totalMass;

  return {
    testId:
      first.testId,

    signal,

    weight:
      Math.min(
        FAMILY_WEIGHT_MAXIMUM,
        totalMass,
      ),

    broadOrFull,
    combinedFull,

    eligibleAttemptCount:
      sorted.length,
  };
}

function buildTestFamilies(
  attempts: TmuaPredictorTestAttempt[],
  profiles: TmuaConversionProfile[],
): {
  normalizedAttemptCount: number;
  families: TestFamily[];
} {
  const normalized =
    attempts
      .map(
        (attempt) =>
          normalizeTestAttempt(
            attempt,
            profiles,
          ),
      )
      .filter(
        (
          attempt,
        ): attempt is NormalizedTestAttempt =>
          attempt !== null,
      );

  const groups =
    new Map<
      string,
      NormalizedTestAttempt[]
    >();

  for (
    const attempt of normalized
  ) {
    const existing =
      groups.get(
        attempt.testId,
      ) ??
      [];

    existing.push(
      attempt,
    );

    groups.set(
      attempt.testId,
      existing,
    );
  }

  const families =
    [...groups.entries()]
      .sort(
        ([a], [b]) =>
          a.localeCompare(b),
      )
      .map(
        (
          [, familyAttempts],
        ) =>
          collapseTestFamily(
            familyAttempts,
          ),
      );

  return {
    normalizedAttemptCount:
      normalized.length,
    families,
  };
}

function trustedQbEvents(
  events: TmuaPredictorQbEvent[],
): TrustedQbEvent[] {
  return events
    .filter(
      (event) =>
        event.source ===
          "qb-progress-trigger-v2" &&
        event.historyQuality ===
          "observed" &&
        event.canonicalActive ===
          true &&
        Boolean(
          normalizeText(
            event.canonicalQid,
          ),
        ),
    )
    .map(
      (event) => {
        parseTimestamp(
          event.attemptedAt,
          `QB event ${event.id} attemptedAt`,
        );

        return {
          id:
            normalizeText(
              event.id,
            ),

          canonicalQid:
            normalizeText(
              event.canonicalQid,
            ),

          predictorEligible:
            event.predictorEligible,

          selectedAnswer:
            event.selectedAnswer,

          canonicalAnswer:
            event.canonicalAnswer,

          canonicalTopic:
            event.canonicalTopic,

          attemptedAt:
            event.attemptedAt,
        };
      })
    .filter(
      (event) =>
        Boolean(event.id),
    );
}

function compareQbEvents(
  a: TrustedQbEvent,
  b: TrustedQbEvent,
): number {
  const timeDifference =
    parseTimestamp(
      a.attemptedAt,
      "QB attemptedAt",
    ) -
    parseTimestamp(
      b.attemptedAt,
      "QB attemptedAt",
    );

  if (
    timeDifference !== 0
  ) {
    return timeDifference;
  }

  return a.id.localeCompare(
    b.id,
  );
}

function isScoreableQbEvent(
  event: TrustedQbEvent,
): boolean {
  return (
    normalizeAnswer(
      event.selectedAnswer,
    ) !== "" &&
    normalizeAnswer(
      event.canonicalAnswer,
    ) !== ""
  );
}

function isCanonicalCorrect(
  event: TrustedQbEvent,
): boolean {
  if (
    !isScoreableQbEvent(
      event,
    )
  ) {
    return false;
  }

  return (
    normalizeAnswer(
      event.selectedAnswer,
    ) ===
    normalizeAnswer(
      event.canonicalAnswer,
    )
  );
}

function buildQbSignal(
  events: TmuaPredictorQbEvent[],
  activeTopics: string[],
): {
  trustedEventCount: number;

  eligibleFirstExposureCount: number;

  uniqueQuestions: number;
  topicCoverage: number;

  overallAccuracy: number | null;
  lowerQuartileTopicAccuracy: number | null;
  balancedAccuracy: number | null;

  recoveryFraction: number | null;
  recoveryOpportunityCount: number;

  signal: number | null;
  rawWeight: number;
} {
  const trusted =
    trustedQbEvents(
      events,
    );

  const grouped =
    new Map<
      string,
      TrustedQbEvent[]
    >();

  for (
    const event of trusted
  ) {
    const existing =
      grouped.get(
        event.canonicalQid,
      ) ??
      [];

    existing.push(
      event,
    );

    grouped.set(
      event.canonicalQid,
      existing,
    );
  }

  const firstExposures: TrustedQbEvent[] =
    [];

  for (
    const [, questionEvents] of grouped
  ) {
    const sorted =
      [...questionEvents].sort(
        compareQbEvents,
      );

    /*
     * Important:
     * exposure #1 is selected before checking predictorEligible.
     */
    firstExposures.push(
      sorted[0],
    );
  }

  const eligibleFirst =
    firstExposures.filter(
      (event) =>
        event.predictorEligible &&
        isScoreableQbEvent(
          event,
        ),
    );

  const uniqueQuestions =
    eligibleFirst.length;

  if (
    uniqueQuestions === 0
  ) {
    return {
      trustedEventCount:
        trusted.length,

      eligibleFirstExposureCount: 0,

      uniqueQuestions: 0,
      topicCoverage: 0,

      overallAccuracy: null,
      lowerQuartileTopicAccuracy: null,
      balancedAccuracy: null,

      recoveryFraction: null,
      recoveryOpportunityCount: 0,

      signal: null,
      rawWeight: 0,
    };
  }

  const correctCount =
    eligibleFirst.filter(
      isCanonicalCorrect,
    ).length;

  const overallAccuracy =
    correctCount /
    uniqueQuestions;

  const topicGroups =
    new Map<
      string,
      {
        attempts: number;
        correct: number;
      }
    >();

  for (
    const event of eligibleFirst
  ) {
    const topic =
      normalizeText(
        event.canonicalTopic,
      );

    if (!topic) {
      continue;
    }

    const current =
      topicGroups.get(
        topic,
      ) ?? {
        attempts: 0,
        correct: 0,
      };

    current.attempts += 1;

    if (
      isCanonicalCorrect(
        event,
      )
    ) {
      current.correct += 1;
    }

    topicGroups.set(
      topic,
      current,
    );
  }

  const qualifyingTopics =
    [...topicGroups.entries()]
      .filter(
        (
          [, stats],
        ) =>
          stats.attempts >= 3,
      );

  const smoothedTopicAccuracies =
    qualifyingTopics
      .map(
        (
          [, stats],
        ) =>
          (
            stats.correct +
            1
          ) /
          (
            stats.attempts +
            2
          ),
      )
      .sort(
        (a, b) =>
          a - b,
      );

  let lowerQuartileTopicAccuracy =
    overallAccuracy;

  if (
    smoothedTopicAccuracies.length >
    0
  ) {
    const quartileCount =
      Math.ceil(
        smoothedTopicAccuracies.length /
          4,
      );

    lowerQuartileTopicAccuracy =
      smoothedTopicAccuracies
        .slice(
          0,
          quartileCount,
        )
        .reduce(
          (sum, value) =>
            sum + value,
          0,
        ) /
      quartileCount;
  }

  const balancedAccuracy =
    QB_OVERALL_ACCURACY_WEIGHT *
      overallAccuracy +
    QB_LOWER_QUARTILE_WEIGHT *
      lowerQuartileTopicAccuracy;

  const canonicalTopics =
    canonicalActiveTopics(
      activeTopics,
    );

  const activeTopicSet =
    new Set(
      canonicalTopics,
    );

  const representedTopics =
    qualifyingTopics.filter(
      ([topic]) =>
        activeTopicSet.has(
          topic,
        ),
    ).length;

  const topicCoverage =
    canonicalTopics.length === 0
      ? 0
      : representedTopics /
        canonicalTopics.length;

  const wrongFirstExposures =
    eligibleFirst.filter(
      (event) =>
        !isCanonicalCorrect(
          event,
        ),
    );

  let recovered =
    0;

  for (
    const first of wrongFirstExposures
  ) {
    const firstTimestamp =
      parseTimestamp(
        first.attemptedAt,
        "QB first attemptedAt",
      );

    const recoveryAfter =
      firstTimestamp +
      RECOVERY_MINIMUM_HOURS *
        60 *
        60 *
        1000;

    const laterEvents =
      (
        grouped.get(
          first.canonicalQid,
        ) ??
        []
      )
        .filter(
          (event) =>
            event !== first,
        )
        .sort(
          compareQbEvents,
        );

    const hasRecovery =
      laterEvents.some(
        (event) =>
          event.predictorEligible &&
          isScoreableQbEvent(
            event,
          ) &&
          parseTimestamp(
            event.attemptedAt,
            "QB recovery attemptedAt",
          ) >=
            recoveryAfter &&
          isCanonicalCorrect(
            event,
          ),
      );

    if (hasRecovery) {
      recovered += 1;
    }
  }

  const recoveryOpportunityCount =
    wrongFirstExposures.length;

  const recoveryFraction =
    recoveryOpportunityCount === 0
      ? QB_RECOVERY_CENTER
      : recovered /
        recoveryOpportunityCount;

  if (
    uniqueQuestions <
    QB_MINIMUM_UNIQUE
  ) {
    return {
      trustedEventCount:
        trusted.length,

      eligibleFirstExposureCount:
        eligibleFirst.length,

      uniqueQuestions,
      topicCoverage,

      overallAccuracy,
      lowerQuartileTopicAccuracy,
      balancedAccuracy,

      recoveryFraction,
      recoveryOpportunityCount,

      signal: null,
      rawWeight: 0,
    };
  }

  const signal =
    clamp(
      QB_SCORE_INTERCEPT +
        QB_ACCURACY_SLOPE *
          (
            100 *
              balancedAccuracy -
            QB_ACCURACY_CENTER_PERCENT
          ) +
        QB_RECOVERY_COEFFICIENT *
          (
            recoveryFraction -
            QB_RECOVERY_CENTER
          ),
      QB_SCORE_MINIMUM,
      QB_SCORE_MAXIMUM,
    );

  const topicCoverageFactor =
    Math.max(
      QB_TOPIC_COVERAGE_FLOOR,
      topicCoverage,
    );

  const rawWeight =
    QB_WEIGHT_MAXIMUM *
    Math.min(
      1,
      uniqueQuestions /
        QB_FULL_WEIGHT_UNIQUE,
    ) *
    topicCoverageFactor;

  return {
    trustedEventCount:
      trusted.length,

    eligibleFirstExposureCount:
      eligibleFirst.length,

    uniqueQuestions,
    topicCoverage,

    overallAccuracy,
    lowerQuartileTopicAccuracy,
    balancedAccuracy,

    recoveryFraction,
    recoveryOpportunityCount,

    signal,
    rawWeight,
  };
}

function confidenceLevel(
  input: {
    testFamilyCount: number;
    broadFamilyCount: number;
    combinedFullCount: number;

    testWeight: number;
    testSd: number;

    qbUniqueQuestions: number;
    qbTopicCoverage: number;

    qbOnly: boolean;
  },
): TmuaPredictionConfidence {
  if (
    input.qbOnly
  ) {
    return "low";
  }

  let confidence:
    TmuaPredictionConfidence =
      "low";

  if (
    input.testFamilyCount >=
      CONFIDENCE_HIGH_MINIMUM_FAMILIES &&
    input.broadFamilyCount >=
      CONFIDENCE_HIGH_MINIMUM_BROAD &&
    input.testWeight >=
      CONFIDENCE_HIGH_MINIMUM_TEST_WEIGHT
  ) {
    confidence =
      "high";
  }
  else {
    const mediumByTests =
      (
        input.testFamilyCount >= 2 &&
        input.broadFamilyCount >= 1
      ) ||
      (
        input.testFamilyCount >= 2 &&
        input.testWeight >= 1
      );

    const mediumByCombinedAndQb =
      input.combinedFullCount >= 1 &&
      input.qbUniqueQuestions >= 100 &&
      input.qbTopicCoverage >= 0.5;

    if (
      mediumByTests ||
      mediumByCombinedAndQb
    ) {
      confidence =
        "medium";
    }
  }

  if (
    input.testSd >
    DISPERSION_FORCE_LOW_THRESHOLD
  ) {
    return "low";
  }

  if (
    input.testSd >
    DISPERSION_DOWNGRADE_THRESHOLD
  ) {
    if (
      confidence === "high"
    ) {
      return "medium";
    }

    if (
      confidence === "medium"
    ) {
      return "low";
    }
  }

  return confidence;
}

function likelyHalfWidth(
  confidence:
    TmuaPredictionConfidence,

  hasTestEvidence: boolean,
  broadFamilyCount: number,
  qbOnly: boolean,
  testSd: number,
): number {
  const base =
    confidence === "high"
      ? 0.5
      : confidence === "medium"
        ? 0.8
        : 1.2;

  let width =
    base;

  if (
    hasTestEvidence &&
    broadFamilyCount === 0
  ) {
    width += 0.2;
  }

  if (
    qbOnly
  ) {
    width += 0.2;
  }

  if (
    Number.isFinite(
      testSd,
    )
  ) {
    width =
      Math.max(
        width,
        0.75 *
          testSd,
      );
  }

  return clamp(
    width,
    0.5,
    1.8,
  );
}

function canonicalTrustedQbHashInput(
  events: TmuaPredictorQbEvent[],
): Array<Record<string, unknown>> {
  return trustedQbEvents(
    events,
  )
    .map(
      (event) => ({
        id:
          event.id,

        canonicalQid:
          event.canonicalQid,

        predictorEligible:
          event.predictorEligible,

        selectedAnswer:
          normalizeAnswer(
            event.selectedAnswer,
          ),

        canonicalAnswer:
          normalizeAnswer(
            event.canonicalAnswer,
          ),

        canonicalTopic:
          normalizeText(
            event.canonicalTopic,
          ),

        attemptedAt:
          event.attemptedAt,
      }),
    )
    .sort(
      (a, b) => {
        const qid =
          String(
            a.canonicalQid,
          ).localeCompare(
            String(
              b.canonicalQid,
            ),
          );

        if (qid !== 0) {
          return qid;
        }

        const time =
          String(
            a.attemptedAt,
          ).localeCompare(
            String(
              b.attemptedAt,
            ),
          );

        if (time !== 0) {
          return time;
        }

        return String(
          a.id,
        ).localeCompare(
          String(
            b.id,
          ),
        );
      },
    );
}

function canonicalTestHashInput(
  attempts: TmuaPredictorTestAttempt[],
): Array<Record<string, unknown>> {
  return attempts
    .filter(
      (attempt) =>
        attempt.predictorEligible,
    )
    .map(
      (attempt) => ({
        testId:
          normalizeText(
            attempt.testId,
          ),

        attemptId:
          normalizeText(
            attempt.attemptId,
          ),

        attemptNumber:
          attempt.attemptNumber,

        evaluatedAt:
          attempt.evaluatedAt,

        topicBreadth:
          attempt.topicBreadth,

        combinedScoreEligible:
          attempt.combinedScoreEligible,

        authoritativeTmuaScore9:
          attempt.authoritativeTmuaScore9,

        effectiveWeight:
          attempt.effectiveWeight,

        paper1RawScore:
          attempt.paper1RawScore,

        paper1EffectiveWeight:
          attempt.paper1EffectiveWeight,

        paper2RawScore:
          attempt.paper2RawScore,

        paper2EffectiveWeight:
          attempt.paper2EffectiveWeight,
      }),
    )
    .sort(
      (a, b) => {
        const test =
          String(
            a.testId,
          ).localeCompare(
            String(
              b.testId,
            ),
          );

        if (test !== 0) {
          return test;
        }

        const numberA =
          typeof a.attemptNumber ===
          "number"
            ? a.attemptNumber
            : Number.MAX_SAFE_INTEGER;

        const numberB =
          typeof b.attemptNumber ===
          "number"
            ? b.attemptNumber
            : Number.MAX_SAFE_INTEGER;

        if (
          numberA !==
          numberB
        ) {
          return (
            numberA -
            numberB
          );
        }

        const time =
          String(
            a.evaluatedAt,
          ).localeCompare(
            String(
              b.evaluatedAt,
            ),
          );

        if (time !== 0) {
          return time;
        }

        return String(
          a.attemptId,
        ).localeCompare(
          String(
            b.attemptId,
          ),
        );
      },
    );
}

export function calculateTmuaPredictorV1(
  input: TmuaPredictorInput,
): TmuaPredictorResult {
  const validatedProfiles =
    validateConversionProfiles(
      input.conversionProfiles,
    );

  const conversionSetHash =
    hashTmuaConversionProfiles(
      validatedProfiles,
    );

  const activeTopicSetHash =
    hashTmuaActiveTopics(
      input.activeTopics,
    );

  const test =
    buildTestFamilies(
      input.testAttempts,
      validatedProfiles,
    );

  const families =
    test.families;

  const testWeight =
    families.reduce(
      (sum, family) =>
        sum +
        family.weight,
      0,
    );

  const testSignal =
    families.length === 0
      ? null
      : weightedMean(
          families.map(
            (family) => ({
              value:
                family.signal,

              weight:
                family.weight,
            }),
          ),
        );

  const testSd =
    families.length <= 1
      ? 0
      : weightedPopulationSd(
          families.map(
            (family) => ({
              value:
                family.signal,

              weight:
                family.weight,
            }),
          ),
        );

  const broadFamilyCount =
    families.filter(
      (family) =>
        family.broadOrFull,
    ).length;

  const combinedFullCount =
    families.filter(
      (family) =>
        family.combinedFull,
    ).length;

  const qb =
    buildQbSignal(
      input.qbEvents,
      input.activeTopics,
    );

  const qbWeight =
    qb.signal === null
      ? 0
      : testWeight > 0
        ? Math.min(
            qb.rawWeight,
            QB_TEST_WEIGHT_CAP_RATIO *
              testWeight,
          )
        : qb.rawWeight;

  let predictionStatus:
    TmuaPredictionStatus =
      "insufficient_evidence";

  let predicted:
    number | null =
      null;

  if (
    testSignal !== null &&
    testWeight > 0 &&
    qb.signal !== null &&
    qbWeight > 0
  ) {
    predictionStatus =
      "predicted";

    predicted =
      (
        testSignal *
          testWeight +
        qb.signal *
          qbWeight
      ) /
      (
        testWeight +
        qbWeight
      );
  }
  else if (
    testSignal !== null &&
    testWeight > 0
  ) {
    predictionStatus =
      "predicted";

    predicted =
      testSignal;
  }
  else if (
    qb.signal !== null &&
    qbWeight > 0
  ) {
    predictionStatus =
      "predicted";

    predicted =
      qb.signal;
  }

  const qbOnly =
    testSignal === null &&
    qb.signal !== null;

  let confidence:
    TmuaPredictionConfidence | null =
      null;

  let lowerBound:
    number | null =
      null;

  let upperBound:
    number | null =
      null;

  if (
    predictionStatus ===
      "predicted" &&
    predicted !== null
  ) {
    predicted =
      clamp(
        predicted,
        SCORE_MINIMUM,
        SCORE_MAXIMUM,
      );

    confidence =
      confidenceLevel({
        testFamilyCount:
          families.length,

        broadFamilyCount,

        combinedFullCount,

        testWeight,
        testSd,

        qbUniqueQuestions:
          qb.uniqueQuestions,

        qbTopicCoverage:
          qb.topicCoverage,

        qbOnly,
      });

    const halfWidth =
      likelyHalfWidth(
        confidence,
        testWeight > 0,
        broadFamilyCount,
        qbOnly,
        testSd,
      );

    lowerBound =
      clamp(
        predicted -
          halfWidth,
        SCORE_MINIMUM,
        SCORE_MAXIMUM,
      );

    upperBound =
      clamp(
        predicted +
          halfWidth,
        SCORE_MINIMUM,
        SCORE_MAXIMUM,
      );
  }

  const inputHash =
    sha256({
      modelVersion:
        TMUA_PREDICTOR_V1_MODEL_VERSION,

      sortedTrustedQbEvidence:
        canonicalTrustedQbHashInput(
          input.qbEvents,
        ),

      sortedTestEvidence:
        canonicalTestHashInput(
          input.testAttempts,
        ),

      conversionSetHash,
      activeTopicSetHash,
    });

  return {
    modelVersion:
      TMUA_PREDICTOR_V1_MODEL_VERSION,

    predictionStatus,

    predictedTmuaScore9:
      predicted === null
        ? null
        : round(
            predicted,
            2,
          ),

    lowerBound:
      lowerBound === null
        ? null
        : round(
            lowerBound,
            2,
          ),

    upperBound:
      upperBound === null
        ? null
        : round(
            upperBound,
            2,
          ),

    confidence,

    testSignalScore9:
      testSignal === null
        ? null
        : round(
            testSignal,
            2,
          ),

    testWeight:
      round(
        testWeight,
        4,
      ),

    testEvidenceCount:
      test.normalizedAttemptCount,

    independentTestCount:
      families.length,

    combinedFullCount,

    qbSignalScore9:
      qb.signal === null
        ? null
        : round(
            qb.signal,
            2,
          ),

    qbWeight:
      round(
        qbWeight,
        4,
      ),

    qbUniqueQuestions:
      qb.uniqueQuestions,

    qbTopicCoverage:
      round(
        qb.topicCoverage,
        4,
      ),

    conversionSetHash,
    activeTopicSetHash,
    inputHash,

    diagnostics: {
      broadTestFamilyCount:
        broadFamilyCount,

      testSignalStandardDeviation:
        round(
          testSd,
          4,
        ),

      qbOverallAccuracy:
        qb.overallAccuracy === null
          ? null
          : round(
              qb.overallAccuracy,
              4,
            ),

      qbLowerQuartileTopicAccuracy:
        qb.lowerQuartileTopicAccuracy ===
        null
          ? null
          : round(
              qb.lowerQuartileTopicAccuracy,
              4,
            ),

      qbBalancedAccuracy:
        qb.balancedAccuracy === null
          ? null
          : round(
              qb.balancedAccuracy,
              4,
            ),

      qbRecoveryFraction:
        qb.recoveryFraction === null
          ? null
          : round(
              qb.recoveryFraction,
              4,
            ),

      qbRecoveryOpportunityCount:
        qb.recoveryOpportunityCount,

      trustedQbEventCount:
        qb.trustedEventCount,

      eligibleFirstExposureCount:
        qb.eligibleFirstExposureCount,

      testFamilies:
        families.map(
          (family) => ({
            testId:
              family.testId,

            signal:
              round(
                family.signal,
                4,
              ),

            weight:
              round(
                family.weight,
                4,
              ),

            broadOrFull:
              family.broadOrFull,

            combinedFull:
              family.combinedFull,

            eligibleAttemptCount:
              family.eligibleAttemptCount,
          }),
        ),
    },
  };
}