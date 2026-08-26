export const ESAT_SCORE_ESTIMATE_VERSION =
  "ESAT_EVIDENCE_CALIBRATED_V2_20260818";

export type EsatDifficulty =
  | "easy"
  | "standard"
  | "hard";

export type EsatModuleName =
  | "Mathematics 1"
  | "Mathematics 2"
  | "Physics"
  | "Chemistry"
  | "Biology";

type PaperCalibrationSeed = {
  module: EsatModuleName;
  sourceForm: string;
  medianRawAnchor: number;
  topDecileRawAnchor: number;
  auditBand: EsatDifficulty;
};

export type EsatPaperCalibration =
  PaperCalibrationSeed & {
    conversionTable: readonly number[];
  };

export type EsatTestProfile = {
  title: string;
  difficulty: EsatDifficulty;
  modules: readonly [
    EsatModuleName,
    EsatModuleName,
    EsatModuleName,
  ];
  calibrationIds: readonly [string, string, string];
};

export type EsatModuleEstimate = {
  module: EsatModuleName;
  raw: number;
  total: 27;
  estimatedScore: number;
  calibrationId: string;
};

type HistoricalReference = {
  rawTotal: number;
  scores: readonly number[];
  medianRawAnchor: number;
  topDecileRawAnchor: number;
};

// These reference shapes preserve the subject-specific behaviour of
// legacy Cambridge science-admissions conversions. Mathematics 2 uses
// the median of the portal's official 2016-2023 TMUA conversions as a
// mathematical-reasoning prior. They are priors, not claimed official
// ESAT raw-score conversions.
const HISTORICAL_REFERENCE_CURVES: Readonly<
  Record<EsatModuleName, HistoricalReference>
> = Object.freeze({
  "Mathematics 1": {
    rawTotal: 20,
    scores: [
      1, 1, 1, 1, 1, 1.6, 2.2, 2.6, 3.1, 3.6, 4,
      4.4, 4.9, 5.4, 5.9, 6.4, 7, 7.7, 8.6, 9, 9,
    ],
    medianRawAnchor: 15.1,
    topDecileRawAnchor: 21.6,
  },
  "Mathematics 2": {
    rawTotal: 40,
    scores: [
      1, 1, 1, 1, 1, 1, 1, 1.1, 1.5, 1.9, 2.3,
      2.6, 3, 3.3, 3.6, 3.9, 4.2, 4.5, 4.8, 5.1,
      5.4, 5.7, 5.9, 6.2, 6.5, 6.8, 7, 7.1, 7.2,
      7.3, 7.4, 7.6, 7.7, 7.8, 8, 8.1, 8.4, 8.6,
      9, 9, 9,
    ],
    medianRawAnchor: 11.5,
    topDecileRawAnchor: 17.6,
  },
  Physics: {
    rawTotal: 20,
    scores: [
      1, 1, 1, 1, 1, 1.5, 2.2, 2.8, 3.4, 4, 4.6,
      5.1, 5.7, 6.3, 6.9, 7.6, 8.3, 9, 9, 9, 9,
    ],
    medianRawAnchor: 13.3,
    topDecileRawAnchor: 19.1,
  },
  Chemistry: {
    rawTotal: 20,
    scores: [
      1, 1, 1, 1, 1, 1, 1, 1, 1.6, 2.1, 2.6,
      3.2, 3.7, 4.3, 4.8, 5.5, 6.2, 7, 8.1, 9, 9,
    ],
    medianRawAnchor: 18.1,
    topDecileRawAnchor: 23,
  },
  Biology: {
    rawTotal: 20,
    scores: [
      1, 1, 1, 1, 1, 1, 1.5, 2, 2.6, 3.1, 3.6,
      4.1, 4.6, 5.1, 5.6, 6.2, 6.9, 7.7, 8.8, 9, 9,
    ],
    medianRawAnchor: 15.9,
    topDecileRawAnchor: 21.8,
  },
});

const PAPER_CALIBRATION_SEEDS: Readonly<
  Record<string, PaperCalibrationSeed>
> = Object.freeze({
  "engineering-01-m1": {
    module: "Mathematics 1",
    sourceForm: "Engineering Mock 1 / Easy source",
    medianRawAnchor: 18.1,
    topDecileRawAnchor: 23.6,
    auditBand: "easy",
  },
  "engineering-01-physics": {
    module: "Physics",
    sourceForm: "Engineering Mock 1 / Easy source",
    medianRawAnchor: 16.3,
    topDecileRawAnchor: 21.1,
    auditBand: "easy",
  },
  "engineering-01-m2": {
    module: "Mathematics 2",
    sourceForm: "Engineering Mock 1 / Easy source",
    medianRawAnchor: 14.5,
    topDecileRawAnchor: 19.6,
    auditBand: "easy",
  },
  "engineering-02-m1": {
    module: "Mathematics 1",
    sourceForm: "Engineering Mock 2 / Standard source",
    medianRawAnchor: 15.1,
    topDecileRawAnchor: 21.6,
    auditBand: "standard",
  },
  "engineering-02-physics": {
    module: "Physics",
    sourceForm: "Engineering Mock 2 / Standard source",
    medianRawAnchor: 13.3,
    topDecileRawAnchor: 19.1,
    auditBand: "standard",
  },
  "engineering-02-m2": {
    module: "Mathematics 2",
    sourceForm: "Engineering Mock 2 / Standard source",
    medianRawAnchor: 11.5,
    topDecileRawAnchor: 17.6,
    auditBand: "standard",
  },
  "engineering-03-m1": {
    module: "Mathematics 1",
    sourceForm: "Engineering Mock 3 / Standard source",
    medianRawAnchor: 15.1,
    topDecileRawAnchor: 21.6,
    auditBand: "standard",
  },
  "engineering-03-physics": {
    module: "Physics",
    sourceForm: "Engineering Mock 3 / Standard source",
    medianRawAnchor: 13.3,
    topDecileRawAnchor: 19.1,
    auditBand: "standard",
  },
  "engineering-03-m2": {
    module: "Mathematics 2",
    sourceForm: "Engineering Mock 3 / Standard source",
    medianRawAnchor: 11.5,
    topDecileRawAnchor: 17.6,
    auditBand: "standard",
  },
  "engineering-04-m1": {
    module: "Mathematics 1",
    sourceForm: "Engineering Mock 4 / Hard source",
    medianRawAnchor: 13.1,
    topDecileRawAnchor: 20.2,
    auditBand: "hard",
  },
  "engineering-04-physics": {
    module: "Physics",
    sourceForm: "Engineering Mock 4 / Hard source",
    medianRawAnchor: 11.3,
    topDecileRawAnchor: 17.7,
    auditBand: "hard",
  },
  "engineering-04-m2": {
    module: "Mathematics 2",
    sourceForm: "Engineering Mock 4 / Hard source",
    medianRawAnchor: 9.5,
    topDecileRawAnchor: 16.2,
    auditBand: "hard",
  },
  "engineering-05-m1": {
    module: "Mathematics 1",
    sourceForm: "Engineering Mock 5 / Challenge source",
    medianRawAnchor: 12.1,
    topDecileRawAnchor: 19.6,
    auditBand: "hard",
  },
  "engineering-05-physics": {
    module: "Physics",
    sourceForm: "Engineering Mock 5 / Challenge source",
    medianRawAnchor: 10.3,
    topDecileRawAnchor: 17.1,
    auditBand: "hard",
  },
  "engineering-05-m2": {
    module: "Mathematics 2",
    sourceForm: "Engineering Mock 5 / Challenge source",
    medianRawAnchor: 8.5,
    topDecileRawAnchor: 15.6,
    auditBand: "hard",
  },
  "chemistry-easy": {
    module: "Chemistry",
    sourceForm: "Chemistry Easy Practice Set 2",
    medianRawAnchor: 21.1,
    topDecileRawAnchor: 25,
    auditBand: "easy",
  },
  "chemistry-standard": {
    module: "Chemistry",
    sourceForm: "Chemistry Standard Solution Book",
    medianRawAnchor: 18.1,
    topDecileRawAnchor: 23,
    auditBand: "standard",
  },
  "chemistry-hard": {
    module: "Chemistry",
    sourceForm: "Chemistry Very Hard Challenge",
    medianRawAnchor: 15.1,
    topDecileRawAnchor: 21,
    auditBand: "hard",
  },
  "biology-easy": {
    module: "Biology",
    sourceForm: "Biology Easy Practice Set 2",
    medianRawAnchor: 18.9,
    topDecileRawAnchor: 23.8,
    auditBand: "easy",
  },
  "biology-standard": {
    module: "Biology",
    sourceForm: "Biology Standard Set 1",
    medianRawAnchor: 15.9,
    topDecileRawAnchor: 21.8,
    auditBand: "standard",
  },
  "biology-hard": {
    module: "Biology",
    sourceForm: "Biology Final Challenge",
    medianRawAnchor: 12.9,
    topDecileRawAnchor: 19.8,
    auditBand: "hard",
  },
});

function clamp(
  value: number,
  minimum: number,
  maximum: number,
) {
  return Math.min(maximum, Math.max(minimum, value));
}

function roundOneDecimal(value: number) {
  return Math.round(value * 10) / 10;
}

function interpolate(
  start: number,
  end: number,
  proportion: number,
) {
  return start + (end - start) * proportion;
}

function piecewiseMap(
  value: number,
  sourcePoints: readonly number[],
  targetPoints: readonly number[],
) {
  for (let index = 1; index < sourcePoints.length; index += 1) {
    if (value <= sourcePoints[index]) {
      const sourceStart = sourcePoints[index - 1];
      const sourceEnd = sourcePoints[index];
      const proportion =
        sourceEnd === sourceStart
          ? 0
          : (value - sourceStart) /
            (sourceEnd - sourceStart);

      return interpolate(
        targetPoints[index - 1],
        targetPoints[index],
        proportion,
      );
    }
  }

  return targetPoints[targetPoints.length - 1];
}

function scoreReferenceCurve(
  reference: HistoricalReference,
  equivalentRawOutOf27: number,
) {
  const rawOnReferenceScale =
    (clamp(equivalentRawOutOf27, 0, 27) / 27) *
    reference.rawTotal;
  const lower = Math.floor(rawOnReferenceScale);
  const upper = Math.ceil(rawOnReferenceScale);

  if (lower === upper) {
    return reference.scores[lower];
  }

  return interpolate(
    reference.scores[lower],
    reference.scores[upper],
    rawOnReferenceScale - lower,
  );
}

function buildConversionTable(seed: PaperCalibrationSeed) {
  const reference =
    HISTORICAL_REFERENCE_CURVES[seed.module];
  const sourcePoints = [
    0,
    seed.medianRawAnchor,
    seed.topDecileRawAnchor,
    27,
  ];
  const targetPoints = [
    0,
    reference.medianRawAnchor,
    reference.topDecileRawAnchor,
    27,
  ];
  const values = Array.from({ length: 28 }, (_, raw) => {
    if (raw === 0) return 1;
    if (raw === 27) return 9;

    const equivalentRaw = piecewiseMap(
      raw,
      sourcePoints,
      targetPoints,
    );

    return roundOneDecimal(
      clamp(
        scoreReferenceCurve(reference, equivalentRaw),
        1,
        9,
      ),
    );
  });

  for (let index = 1; index < values.length; index += 1) {
    values[index] = Math.max(values[index], values[index - 1]);
  }

  return Object.freeze(values);
}

const PAPER_CALIBRATIONS: Readonly<
  Record<string, EsatPaperCalibration>
> = Object.freeze(
  Object.fromEntries(
    Object.entries(PAPER_CALIBRATION_SEEDS).map(
      ([calibrationId, seed]) => [
        calibrationId,
        Object.freeze({
          ...seed,
          conversionTable: buildConversionTable(seed),
        }),
      ],
    ),
  ),
);

const ENGINEERING_MODULES = [
  "Mathematics 1",
  "Physics",
  "Mathematics 2",
] as const;

const TEST_PROFILES: Readonly<
  Record<string, EsatTestProfile>
> = Object.freeze({
  "esat-mock-01": {
    title: "ESAT Engineering Full Mock Test 1",
    difficulty: "easy",
    modules: ENGINEERING_MODULES,
    calibrationIds: [
      "engineering-01-m1",
      "engineering-01-physics",
      "engineering-01-m2",
    ],
  },
  "esat-mock-02": {
    title: "ESAT Engineering Full Mock Test 2",
    difficulty: "standard",
    modules: ENGINEERING_MODULES,
    calibrationIds: [
      "engineering-02-m1",
      "engineering-02-physics",
      "engineering-02-m2",
    ],
  },
  "esat-mock-03": {
    title: "ESAT Engineering Full Mock Test 3",
    difficulty: "standard",
    modules: ENGINEERING_MODULES,
    calibrationIds: [
      "engineering-03-m1",
      "engineering-03-physics",
      "engineering-03-m2",
    ],
  },
  "esat-mock-04": {
    title: "ESAT Engineering Full Mock Test 4",
    difficulty: "hard",
    modules: ENGINEERING_MODULES,
    calibrationIds: [
      "engineering-04-m1",
      "engineering-04-physics",
      "engineering-04-m2",
    ],
  },
  // The fifth live Engineering page is hosted in the esat-mock-13
  // folder but deliberately retains its historic attempt ID.
  "esat-mock-05": {
    title: "ESAT Engineering Full Mock Test 5",
    difficulty: "hard",
    modules: ENGINEERING_MODULES,
    calibrationIds: [
      "engineering-05-m1",
      "engineering-05-physics",
      "engineering-05-m2",
    ],
  },
  "esat-physics-chemistry-level-0": {
    title: "Physics + Chemistry â€” Level 0 Easy",
    difficulty: "easy",
    modules: ["Mathematics 1", "Physics", "Chemistry"],
    calibrationIds: [
      "engineering-01-m1",
      "engineering-01-physics",
      "chemistry-easy",
    ],
  },
  "esat-physics-chemistry-level-1": {
    title: "Physics + Chemistry â€” Level 1 Standard",
    difficulty: "standard",
    modules: ["Mathematics 1", "Physics", "Chemistry"],
    calibrationIds: [
      "engineering-03-m1",
      "engineering-03-physics",
      "chemistry-standard",
    ],
  },
  "esat-physics-chemistry-level-2": {
    title: "Physics + Chemistry â€” Level 2 Harder than ESAT",
    difficulty: "hard",
    modules: ["Mathematics 1", "Physics", "Chemistry"],
    calibrationIds: [
      "engineering-05-m1",
      "engineering-05-physics",
      "chemistry-hard",
    ],
  },
  "esat-physics-biology-level-0": {
    title: "Physics + Biology â€” Level 0 Easy",
    difficulty: "easy",
    modules: ["Mathematics 1", "Physics", "Biology"],
    calibrationIds: [
      "engineering-01-m1",
      "engineering-01-physics",
      "biology-easy",
    ],
  },
  "esat-physics-biology-level-1": {
    title: "Physics + Biology â€” Level 1 Standard",
    difficulty: "standard",
    modules: ["Mathematics 1", "Physics", "Biology"],
    calibrationIds: [
      "engineering-03-m1",
      "engineering-03-physics",
      "biology-standard",
    ],
  },
  "esat-physics-biology-level-2": {
    title: "Physics + Biology â€” Level 2 Harder than ESAT",
    difficulty: "hard",
    modules: ["Mathematics 1", "Physics", "Biology"],
    calibrationIds: [
      "engineering-05-m1",
      "engineering-05-physics",
      "biology-hard",
    ],
  },
  "esat-maths2-chemistry-level-0": {
    title: "Maths 2 + Chemistry â€” Level 0 Easy",
    difficulty: "easy",
    modules: ["Mathematics 1", "Mathematics 2", "Chemistry"],
    calibrationIds: [
      "engineering-01-m1",
      "engineering-01-m2",
      "chemistry-easy",
    ],
  },
  "esat-maths2-chemistry-level-1": {
    title: "Maths 2 + Chemistry â€” Level 1 Standard",
    difficulty: "standard",
    modules: ["Mathematics 1", "Mathematics 2", "Chemistry"],
    calibrationIds: [
      "engineering-03-m1",
      "engineering-03-m2",
      "chemistry-standard",
    ],
  },
  "esat-maths2-chemistry-level-2": {
    title: "Maths 2 + Chemistry â€” Level 2 Harder than ESAT",
    difficulty: "hard",
    modules: ["Mathematics 1", "Mathematics 2", "Chemistry"],
    calibrationIds: [
      "engineering-05-m1",
      "engineering-05-m2",
      "chemistry-hard",
    ],
  },
  "esat-maths2-biology-level-0": {
    title: "Maths 2 + Biology â€” Level 0 Easy",
    difficulty: "easy",
    modules: ["Mathematics 1", "Mathematics 2", "Biology"],
    calibrationIds: [
      "engineering-01-m1",
      "engineering-01-m2",
      "biology-easy",
    ],
  },
  "esat-maths2-biology-level-1": {
    title: "Maths 2 + Biology â€” Level 1 Standard",
    difficulty: "standard",
    modules: ["Mathematics 1", "Mathematics 2", "Biology"],
    calibrationIds: [
      "engineering-03-m1",
      "engineering-03-m2",
      "biology-standard",
    ],
  },
  "esat-maths2-biology-level-2": {
    title: "Maths 2 + Biology â€” Level 2 Harder than ESAT",
    difficulty: "hard",
    modules: ["Mathematics 1", "Mathematics 2", "Biology"],
    calibrationIds: [
      "engineering-05-m1",
      "engineering-05-m2",
      "biology-hard",
    ],
  },
  "esat-chemistry-biology-level-0": {
    title: "Chemistry + Biology â€” Level 0 Easy",
    difficulty: "easy",
    modules: ["Mathematics 1", "Chemistry", "Biology"],
    calibrationIds: [
      "engineering-01-m1",
      "chemistry-easy",
      "biology-easy",
    ],
  },
  "esat-chemistry-biology-level-1": {
    title: "Chemistry + Biology â€” Level 1 Standard",
    difficulty: "standard",
    modules: ["Mathematics 1", "Chemistry", "Biology"],
    calibrationIds: [
      "engineering-03-m1",
      "chemistry-standard",
      "biology-standard",
    ],
  },
  "esat-chemistry-biology-level-2": {
    title: "Chemistry + Biology â€” Level 2 Harder than ESAT",
    difficulty: "hard",
    modules: ["Mathematics 1", "Chemistry", "Biology"],
    calibrationIds: [
      "engineering-05-m1",
      "chemistry-hard",
      "biology-hard",
    ],
  },
  "esat-recall-2024-25-engineering": {
    title: "ESAT 2024â€“25 Recall Mock â€” Engineering",
    difficulty: "hard",
    modules: ["Mathematics 1", "Mathematics 2", "Physics"],
    calibrationIds: ["engineering-05-m1", "engineering-05-m2", "engineering-05-physics"],
  },
  "esat-recall-2024-25-physics-chemistry": {
    title: "ESAT 2024â€“25 Recall Mock â€” Physics + Chemistry",
    difficulty: "hard",
    modules: ["Mathematics 1", "Physics", "Chemistry"],
    calibrationIds: ["engineering-05-m1", "engineering-05-physics", "chemistry-hard"],
  },
  "esat-recall-2024-25-physics-biology": {
    title: "ESAT 2024â€“25 Recall Mock â€” Physics + Biology",
    difficulty: "hard",
    modules: ["Mathematics 1", "Physics", "Biology"],
    calibrationIds: ["engineering-05-m1", "engineering-05-physics", "biology-hard"],
  },
  "esat-recall-2024-25-maths2-chemistry": {
    title: "ESAT 2024â€“25 Recall Mock â€” Maths 2 + Chemistry",
    difficulty: "hard",
    modules: ["Mathematics 1", "Mathematics 2", "Chemistry"],
    calibrationIds: ["engineering-05-m1", "engineering-05-m2", "chemistry-hard"],
  },
  "esat-recall-2024-25-maths2-biology": {
    title: "ESAT 2024â€“25 Recall Mock â€” Maths 2 + Biology",
    difficulty: "hard",
    modules: ["Mathematics 1", "Mathematics 2", "Biology"],
    calibrationIds: ["engineering-05-m1", "engineering-05-m2", "biology-hard"],
  },
  "esat-recall-2024-25-chemistry-biology": {
    title: "ESAT 2024â€“25 Recall Mock â€” Chemistry + Biology",
    difficulty: "hard",
    modules: ["Mathematics 1", "Chemistry", "Biology"],
    calibrationIds: ["engineering-05-m1", "chemistry-hard", "biology-hard"],
  },
});

export function getEsatTestProfile(testId: string) {
  return TEST_PROFILES[testId] ?? null;
}

export function estimateEsatTestScores(
  testId: string,
  rawScores: readonly unknown[],
) {
  const profile = getEsatTestProfile(testId);

  if (!profile) {
    throw new Error("Unknown ESAT test profile.");
  }

  if (!Array.isArray(rawScores) || rawScores.length !== 3) {
    throw new Error("rawScores must contain exactly three module marks.");
  }

  const modules: EsatModuleEstimate[] =
    profile.modules.map((module, index) => {
      const submittedRaw = Number(rawScores[index]);

      if (
        !Number.isFinite(submittedRaw) ||
        submittedRaw < 0 ||
        submittedRaw > 27
      ) {
        throw new Error(
          `Invalid raw score for ${module}; expected 0 to 27.`,
        );
      }

      const raw = Math.round(submittedRaw);
      const calibrationId = profile.calibrationIds[index];
      const calibration = PAPER_CALIBRATIONS[calibrationId];

      if (!calibration || calibration.module !== module) {
        throw new Error(
          `Invalid calibration mapping for ${testId}: ${module}.`,
        );
      }

      return {
        module,
        raw,
        total: 27 as const,
        estimatedScore: calibration.conversionTable[raw],
        calibrationId,
      };
    });

  const rawTotal = modules.reduce(
    (sum, item) => sum + item.raw,
    0,
  );
  const predictedCombinedPracticeScore = roundOneDecimal(
    modules.reduce(
      (sum, item) => sum + item.estimatedScore,
      0,
    ) / modules.length,
  );

  return {
    version: ESAT_SCORE_ESTIMATE_VERSION,
    status: "evidence_calibrated" as const,
    method:
      "module_prior_with_source_form_equating_v2" as const,
    testId,
    testTitle: profile.title,
    difficulty: profile.difficulty,
    rawTotal,
    rawTotalPossible: 81 as const,
    modules,
    predictedCombinedPracticeScore,
    // Retained for the existing shared renderer/API consumers.
    averageModuleEstimate: predictedCombinedPracticeScore,
    combinedScoreOfficial: false as const,
    note:
      "Best evidence-calibrated practice estimate for this paper. " +
      "It combines subject-specific historical conversion shapes, official ESAT distribution anchors, " +
      "and the audited difficulty of each source form. Official ESAT reports modules separately and " +
      "equates live forms using candidate-response data, so this combined practice score is not an official UAT-UK result.",
  };
}

export const ESAT_PAPER_CALIBRATIONS = PAPER_CALIBRATIONS;
export const ESAT_TEST_PROFILES = TEST_PROFILES;
