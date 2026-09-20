/** October 2026 source keys and the owner's provisional, uncalibrated anchors.
 * These papers are deliberately separate from the legacy calibrated predictor.
 */
import type { EsatModuleName } from "./esat-score-estimates";

export const ESAT_OCTOBER_2026_KEY_VERSION = "esat-october-2026-keys-20260920-v1";
export const ESAT_OCTOBER_2026_SCORE_VERSION = "TS_ESAT_OCTOBER_2026_PROVISIONAL_V1";

type OctoberSeed = {
  sourceDirectory: string;
  modules: readonly [EsatModuleName, EsatModuleName, EsatModuleName];
  answerKey: string;
  canonicalSha256: string;
  keyVersion: string;
};

export const ESAT_OCTOBER_2026_SEEDS: Readonly<Record<string, OctoberSeed>> = Object.freeze({
  "esat-october-2026-engineering": { sourceDirectory: "esat-october-2026-engineering", modules: ["Mathematics 1", "Mathematics 2", "Physics"], answerKey: "BDAEBCDAABCDBCEADCBECCDDECADEABADACCBBDEECDECCBBEAABBDBEDCDABDAEEBEBCDCCACEAABCBB", canonicalSha256: "85e9e69fc647ee6a6d4ef39b6ef9e1d4817727eda8a112fc9bc54e1d98c11d32", keyVersion: ESAT_OCTOBER_2026_KEY_VERSION },
  "esat-october-2026-physics-chemistry": { sourceDirectory: "esat-october-2026-physics-chemistry", modules: ["Mathematics 1", "Physics", "Chemistry"], answerKey: "BDAEBCDAABCDBCEADCBECCDDECABEDCDABDAEEBEBCDCCACEAABCBBBDACEBDCEDCBEAECBDECADBCDEB", canonicalSha256: "df1ab7e271ca9dfc9c8d6d1ca8d8ae8bbccd3814aea96ccfdb81f295768607f2", keyVersion: ESAT_OCTOBER_2026_KEY_VERSION },
  "esat-october-2026-physics-biology": { sourceDirectory: "esat-october-2026-physics-biology", modules: ["Mathematics 1", "Physics", "Biology"], answerKey: "BDAEBCDAABCDBCEADCBECCDDECABEDCDABDAEEBEBCDCCACEAABCBBCEEBDABDEACDBHCEDAEDBAFBCEA", canonicalSha256: "ea4dc164adda21ea9238f3996ab7ec166940fda24ff99aa6502fbb2724488c8c", keyVersion: ESAT_OCTOBER_2026_KEY_VERSION },
  "esat-october-2026-maths-2-chemistry": { sourceDirectory: "esat-october-2026-maths-2-chemistry", modules: ["Mathematics 1", "Mathematics 2", "Chemistry"], answerKey: "BDAEBCDAABCDBCEADCBECCDDECADEABADACCBBDEECDECCBBEAABBDBDACEBDCEDCBEAECBDECADBCDEB", canonicalSha256: "91f7f325b9f0f5420ebbb610da3a5fd69d2b6c3dd588fab3b527c46190344755", keyVersion: ESAT_OCTOBER_2026_KEY_VERSION },
  "esat-october-2026-maths-2-biology": { sourceDirectory: "esat-october-2026-maths-2-biology", modules: ["Mathematics 1", "Mathematics 2", "Biology"], answerKey: "BDAEBCDAABCDBCEADCBECCDDECADEABADACCBBDEECDECCBBEAABBDCEEBDABDEACDBHCEDAEDBAFBCEA", canonicalSha256: "e57cb3e090500af07842ecdbf3f52e2763a24b7f1adbaca2691669a2dc7c0a4f", keyVersion: ESAT_OCTOBER_2026_KEY_VERSION },
  "esat-october-2026-chemistry-biology": { sourceDirectory: "esat-october-2026-chemistry-biology", modules: ["Mathematics 1", "Chemistry", "Biology"], answerKey: "BDAEBCDAABCDBCEADCBECCDDECABDACEBDCEDCBEAECBDECADBCDEBCEEBDABDEACDBHCEDAEDBAFBCEA", canonicalSha256: "e9ab52400f50bdbdfa5c2565536aa027556ae78bca9bfe7215df1d06965f2c8e", keyVersion: ESAT_OCTOBER_2026_KEY_VERSION },
});

const ANCHORS: Readonly<Record<EsatModuleName, readonly (readonly [number, number])[]>> = {
  "Mathematics 1": [[0,1],[13,4.5],[14,5],[17,6],[20,7],[23,8],[26,9],[27,9]],
  "Mathematics 2": [[0,1],[11,4.5],[12,5],[15,6],[18,7],[22,8],[25,9],[27,9]],
  Physics: [[0,1],[15,4.5],[16,5],[19,6],[22,7],[24,8],[27,9]],
  Chemistry: [[0,1],[16,4.5],[17,5],[20,6],[23,7],[25,8],[27,9]],
  Biology: [[0,1],[18,4.5],[19,5],[22,6],[24,7],[26,8],[27,9]],
};

function provisionalScore(module: EsatModuleName, raw: number) {
  const anchors = ANCHORS[module];
  for (let i = 1; i < anchors.length; i += 1) {
    if (raw <= anchors[i][0]) {
      const [x0, y0] = anchors[i - 1];
      const [x1, y1] = anchors[i];
      return Math.round((y0 + (raw - x0) * (y1 - y0) / (x1 - x0)) * 10) / 10;
    }
  }
  return 9;
}

export function estimateOctober2026EsatScores(testId: string, rawScores: readonly unknown[]) {
  const profile = ESAT_OCTOBER_2026_SEEDS[testId];
  if (!profile) return null;
  if (!Array.isArray(rawScores) || rawScores.length !== 3) {
    throw new Error("rawScores must contain exactly three module marks.");
  }
  const modules = profile.modules.map((module, index) => {
    const raw = Number(rawScores[index]);
    if (!Number.isInteger(raw) || raw < 0 || raw > 27) {
      throw new Error(`Invalid raw score for ${module}; expected an integer from 0 to 27.`);
    }
    return { module, raw, total: 27 as const, estimatedScore: provisionalScore(module, raw), calibrationId: null };
  });
  return {
    version: ESAT_OCTOBER_2026_SCORE_VERSION,
    status: "provisional_uncalibrated" as const,
    method: "owner_module_anchors_linear_interpolation_v1" as const,
    scoreLabel: "Provisional TS practice score",
    testId,
    rawTotal: modules.reduce((sum, item) => sum + item.raw, 0),
    rawTotalPossible: 81 as const,
    modules,
    predictorEligible: false as const,
    predictedCombinedPracticeScore: null,
    averageModuleEstimate: null,
    combinedScoreOfficial: false as const,
    note: "These practice estimates have not been calibrated against live ESAT results. Each module is converted separately. Interpolation, including below 4.5, is a display convention; there is no overall ESAT scaled score.",
  };
}
