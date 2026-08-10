import type {
  TmuaConversionProfile,
  TmuaPredictorInput,
  TmuaPredictorQbEvent,
  TmuaPredictorTestAttempt,
} from "./tmua-predictor-v1-engine";

export type TmuaDatabaseConversionProfileRow = {
  profile: string;
  score_values: Array<number | string>;
};

export type TmuaDatabaseTestEvaluationRow = {
  user_id: string;

  test_id: string;
  attempt_id: string;
  attempt_number: number | string | null;
  evaluated_at: string;

  predictor_eligible: boolean;

  topic_breadth: string;

  combined_score_eligible: boolean;
  authoritative_tmua_score9: number | string | null;

  effective_weight: number | string | null;

  paper_1_raw_score: number | string | null;
  paper_1_effective_weight: number | string | null;

  paper_2_raw_score: number | string | null;
  paper_2_effective_weight: number | string | null;
};

export type TmuaDatabaseQbEventRow = {
  user_id: string;

  id: string;

  source: string;
  history_quality: string;

  predictor_eligible: boolean;

  canonical_qid: string | null;
  canonical_active: boolean;

  selected_answer: string | null;
  canonical_answer: string | null;
  canonical_topic: string | null;

  attempted_at: string;

  claimed_is_correct?: boolean | null;
  client_topic_id?: string | null;
};

export type TmuaPredictorDatabasePayload = {
  conversionProfiles:
    TmuaDatabaseConversionProfileRow[];

  activeTopics:
    string[];

  testAttempts:
    TmuaDatabaseTestEvaluationRow[];

  qbEvents:
    TmuaDatabaseQbEventRow[];
};

export type TmuaPredictorUserInput = {
  userId: string;
  input: TmuaPredictorInput;
};

function nonEmptyString(
  value: unknown,
  label: string,
): string {
  if (
    typeof value !== "string" ||
    value.trim() === ""
  ) {
    throw new Error(
      `${label} must be a non-empty string`,
    );
  }

  return value.trim();
}

function nullableString(
  value: unknown,
): string | null {
  if (
    value === null ||
    value === undefined
  ) {
    return null;
  }

  if (
    typeof value !== "string"
  ) {
    throw new Error(
      "Expected nullable string",
    );
  }

  const normalized =
    value.trim();

  return normalized === ""
    ? null
    : normalized;
}

function finiteNumber(
  value: unknown,
  label: string,
): number {
  const number =
    typeof value === "number"
      ? value
      : typeof value === "string" &&
          value.trim() !== ""
        ? Number(value)
        : Number.NaN;

  if (!Number.isFinite(number)) {
    throw new Error(
      `${label} must be finite`,
    );
  }

  return number;
}

function nullableFiniteNumber(
  value: unknown,
  label: string,
): number | null {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return null;
  }

  return finiteNumber(
    value,
    label,
  );
}

function nullableInteger(
  value: unknown,
  label: string,
): number | null {
  const number =
    nullableFiniteNumber(
      value,
      label,
    );

  if (number === null) {
    return null;
  }

  if (!Number.isInteger(number)) {
    throw new Error(
      `${label} must be an integer`,
    );
  }

  return number;
}

function requireBoolean(
  value: unknown,
  label: string,
): boolean {
  if (typeof value !== "boolean") {
    throw new Error(
      `${label} must be boolean`,
    );
  }

  return value;
}

function normalizeActiveTopics(
  topics: string[],
): string[] {
  return [
    ...new Set(
      topics
        .map(
          (topic) =>
            nonEmptyString(
              topic,
              "active topic",
            ),
        ),
    ),
  ].sort(
    (a, b) =>
      a.localeCompare(b),
  );
}

export function adaptTmuaConversionProfiles(
  rows: TmuaDatabaseConversionProfileRow[],
): TmuaConversionProfile[] {
  return rows
    .map(
      (row) => ({
        profileId:
          nonEmptyString(
            row.profile,
            "conversion profile",
          ),

        scores:
          row.score_values.map(
            (
              value,
              index,
            ) =>
              finiteNumber(
                value,
                `${row.profile}[${index}]`,
              ),
          ),
      }),
    )
    .sort(
      (a, b) =>
        a.profileId.localeCompare(
          b.profileId,
        ),
    );
}

export function adaptTmuaTestEvaluation(
  row: TmuaDatabaseTestEvaluationRow,
): TmuaPredictorTestAttempt {
  return {
    testId:
      nonEmptyString(
        row.test_id,
        "test_id",
      ),

    attemptId:
      nonEmptyString(
        row.attempt_id,
        "attempt_id",
      ),

    attemptNumber:
      nullableInteger(
        row.attempt_number,
        "attempt_number",
      ),

    evaluatedAt:
      nonEmptyString(
        row.evaluated_at,
        "evaluated_at",
      ),

    predictorEligible:
      requireBoolean(
        row.predictor_eligible,
        "predictor_eligible",
      ),

    topicBreadth:
      nonEmptyString(
        row.topic_breadth,
        "topic_breadth",
      ),

    combinedScoreEligible:
      requireBoolean(
        row.combined_score_eligible,
        "combined_score_eligible",
      ),

    authoritativeTmuaScore9:
      nullableFiniteNumber(
        row.authoritative_tmua_score9,
        "authoritative_tmua_score9",
      ),

    effectiveWeight:
      nullableFiniteNumber(
        row.effective_weight,
        "effective_weight",
      ),

    paper1RawScore:
      nullableInteger(
        row.paper_1_raw_score,
        "paper_1_raw_score",
      ),

    paper1EffectiveWeight:
      nullableFiniteNumber(
        row.paper_1_effective_weight,
        "paper_1_effective_weight",
      ),

    paper2RawScore:
      nullableInteger(
        row.paper_2_raw_score,
        "paper_2_raw_score",
      ),

    paper2EffectiveWeight:
      nullableFiniteNumber(
        row.paper_2_effective_weight,
        "paper_2_effective_weight",
      ),
  };
}

export function adaptTmuaQbEvent(
  row: TmuaDatabaseQbEventRow,
): TmuaPredictorQbEvent {
  return {
    id:
      nonEmptyString(
        row.id,
        "QB event id",
      ),

    source:
      nonEmptyString(
        row.source,
        "QB source",
      ),

    historyQuality:
      nonEmptyString(
        row.history_quality,
        "QB history_quality",
      ),

    predictorEligible:
      requireBoolean(
        row.predictor_eligible,
        "QB predictor_eligible",
      ),

    canonicalQid:
      nullableString(
        row.canonical_qid,
      ),

    canonicalActive:
      requireBoolean(
        row.canonical_active,
        "canonical_active",
      ),

    selectedAnswer:
      nullableString(
        row.selected_answer,
      ),

    canonicalAnswer:
      nullableString(
        row.canonical_answer,
      ),

    canonicalTopic:
      nullableString(
        row.canonical_topic,
      ),

    attemptedAt:
      nonEmptyString(
        row.attempted_at,
        "QB attempted_at",
      ),

    /*
     * Preserved only so the engine verifier can prove these
     * fields remain non-authoritative.
     */
    claimedIsCorrect:
      row.claimed_is_correct ??
      null,

    clientTopicId:
      nullableString(
        row.client_topic_id,
      ),
  };
}

export function buildTmuaPredictorInputsByUser(
  payload: TmuaPredictorDatabasePayload,
): TmuaPredictorUserInput[] {
  const conversionProfiles =
    adaptTmuaConversionProfiles(
      payload.conversionProfiles,
    );

  const activeTopics =
    normalizeActiveTopics(
      payload.activeTopics,
    );

  const userIds =
    new Set<string>();

  for (
    const row of payload.testAttempts
  ) {
    userIds.add(
      nonEmptyString(
        row.user_id,
        "test user_id",
      ),
    );
  }

  for (
    const row of payload.qbEvents
  ) {
    userIds.add(
      nonEmptyString(
        row.user_id,
        "QB user_id",
      ),
    );
  }

  return [
    ...userIds,
  ]
    .sort(
      (a, b) =>
        a.localeCompare(b),
    )
    .map(
      (userId) => ({
        userId,

        input: {
          conversionProfiles,

          activeTopics,

          testAttempts:
            payload.testAttempts
              .filter(
                (row) =>
                  row.user_id ===
                  userId,
              )
              .map(
                adaptTmuaTestEvaluation,
              ),

          qbEvents:
            payload.qbEvents
              .filter(
                (row) =>
                  row.user_id ===
                  userId,
              )
              .map(
                adaptTmuaQbEvent,
              ),
        },
      }),
    );
}