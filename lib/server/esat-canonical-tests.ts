/**
 * Server-authoritative answer keys for every full ESAT practice paper.
 *
 * Never import this registry into a client component. Browser-supplied
 * correct_answers and score values are audit inputs only for recognised
 * papers; the submission route scores against this registry.
 */

import type {
  EsatModuleName,
} from "./esat-score-estimates";

export const ESAT_CANONICAL_KEY_VERSION =
  "esat-canonical-keys-20260819-v1" as const;

type CanonicalSeed = {
  sourceDirectory: string;
  modules: readonly [
    EsatModuleName,
    EsatModuleName,
    EsatModuleName,
  ];
  answerKey: string;
  canonicalSha256: string;
};

export type EsatCanonicalTest = {
  readonly testId: string;
  readonly keyVersion: string;
  readonly sourceFile: string;
  readonly expectedQuestions: 81;
  readonly sectionRanges: readonly [
    readonly [0, 27],
    readonly [27, 54],
    readonly [54, 81],
  ];
  readonly modules: CanonicalSeed["modules"];
  readonly canonicalSha256: string;
  readonly answers: readonly string[];
};

const ENGINEERING_MODULES = [
  "Mathematics 1",
  "Physics",
  "Mathematics 2",
] as const;

const SEEDS: Readonly<Record<string, CanonicalSeed>> = Object.freeze({
  "esat-mock-01": { sourceDirectory: "esat-mock-01", modules: ENGINEERING_MODULES, answerKey: "GCBBEGDCBCADBADCBDCEECEDECCFADEGCDEDDFBCGDEBCGDEGHCDCBAFDADDFBDDBEEBCADACBAACCDCD", canonicalSha256: "3f86a78f78379fee6ed3e4623ca80e88aa5112971afd608355c6894c11009368" },
  "esat-mock-02": { sourceDirectory: "esat-mock-02", modules: ENGINEERING_MODULES, answerKey: "CBCCDBACCDCADCDCCCAEDBADEDCDGFBACGDABHEGADFBDEFEDCCCABCBCAACBDCBBBEBCCBBEEGGDAEDC", canonicalSha256: "20ce00800f966b42edbf11c45f95b434413bb51bdc9f85004cd633792482ac96" },
  "esat-mock-03": { sourceDirectory: "esat-mock-03", modules: ENGINEERING_MODULES, answerKey: "CBECDDEAADDCBABEEEDEDDCDDACDEBAEDFEACDFEHCFAHDADFEBHGCCACCCBDEDFDBADEGDGCCCGEDABA", canonicalSha256: "811507dcb76b8a306817572dc4777eaf019c0864da667e6e4359dbf843698074" },
  "esat-mock-04": { sourceDirectory: "esat-mock-04", modules: ENGINEERING_MODULES, answerKey: "CEBDACEBDABCEDABCEDACEBDACEADECBAEDBCCADBEADCEBADCEBBDDCBAEAEDBCCBEAEBCDABDCBCDEA", canonicalSha256: "0c0f9d95eca282806536545ecfe325d322d577d66735e60748cd45489b08cead" },
  "esat-mock-05": { sourceDirectory: "esat-mock-13", modules: ENGINEERING_MODULES, answerKey: "CBDAECBDAECBDAEBCDAECBDAECBDDCCBDDCDCEDCCDDEDCCBBDDBCCDBECBCBBCBBBCBBCCDDCCBCCBED", canonicalSha256: "a16bfdfd27ae9e2d179458a77f2486898ccd4210285ade3e53462df625b293e2" },

  "esat-physics-chemistry-level-0": { sourceDirectory: "esat-physics-chemistry-level-0", modules: ["Mathematics 1", "Physics", "Chemistry"], answerKey: "GCBBEGDCBCADBADCBDCEECEDECCFADEGCDEDDFBCGDEBCGDEGHCDCBBDCDDDFCBHCADCBAFBCBCDBCCEC", canonicalSha256: "be24a54cd73dbed4cb7351fc6a573f7f2ae3dff20276bf6dc8813efe315c0af2" },
  "esat-physics-chemistry-level-1": { sourceDirectory: "esat-physics-chemistry-level-1", modules: ["Mathematics 1", "Physics", "Chemistry"], answerKey: "CBECDDEAADDCBABEEEDEDDCDDACDEBAEDFEACDFEHCFAHDADFEBHGCCDBCEBECDDEFBECBDCACBCDCAEC", canonicalSha256: "d7a88e86962c84102d9019bada563c0f3df9fa508ccf17b4635f45f4aa53fee4" },
  "esat-physics-chemistry-level-2": { sourceDirectory: "esat-physics-chemistry-level-2", modules: ["Mathematics 1", "Physics", "Chemistry"], answerKey: "CBDAECBDAECBDAEBCDAECBDAECBDDCCBDDCDCEDCCDDEDCCBBDDBCCADFHCGBGEFCBEACDCBEBADFDFEA", canonicalSha256: "ca74e331e8b1c8f4c8c0ba42a2ceb06bcf88b3f596917e1e7c56b6b1f6f1bed6" },

  "esat-physics-biology-level-0": { sourceDirectory: "esat-physics-biology-level-0", modules: ["Mathematics 1", "Physics", "Biology"], answerKey: "GCBBEGDCBCADBADCBDCEECEDECCFADEGCDEDDFBCGDEBCGDEGHCDCBCAHCEECDBBEGCDBBEEEEDABCBHB", canonicalSha256: "036fdb995b1d400fee56e413e25797eabe74f4a944169940dc001730f1ecf41a" },
  "esat-physics-biology-level-1": { sourceDirectory: "esat-physics-biology-level-1", modules: ["Mathematics 1", "Physics", "Biology"], answerKey: "CBECDDEAADDCBABEEEDEDDCDDACDEBAEDFEACDFEHCFAHDADFEBHGCDCCGCFEFCDBEBDCEEHBCEDBBCFE", canonicalSha256: "640c4fef78cba8e6eb730c3108ad5cd104874a2a6ca04d2ed04a597855e21095" },
  "esat-physics-biology-level-2": { sourceDirectory: "esat-physics-biology-level-2", modules: ["Mathematics 1", "Physics", "Biology"], answerKey: "CBDAECBDAECBDAEBCDAECBDAECBDDCCBDDCDCEDCCDDEDCCBBDDBCCCFBCCDCDCBBEFECDBBEEAEDFECH", canonicalSha256: "9c890f1b6ea596c69e955af270123a435b66e36b86f664c0dce459b5999abd2d" },

  "esat-maths2-chemistry-level-0": { sourceDirectory: "esat-maths2-chemistry-level-0", modules: ["Mathematics 1", "Mathematics 2", "Chemistry"], answerKey: "GCBBEGDCBCADBADCBDCEECEDECCAFDADDFBDDBEEBCADACBAACCDCDBDCDDDFCBHCADCBAFBCBCDBCCEC", canonicalSha256: "3805f4a9974c4c8bda198ed756aec0aded94ef9b33ac80c1d6d94364f98c65c1" },
  "esat-maths2-chemistry-level-1": { sourceDirectory: "esat-maths2-chemistry-level-1", modules: ["Mathematics 1", "Mathematics 2", "Chemistry"], answerKey: "CBECDDEAADDCBABEEEDEDDCDDACCACCCBDEDFDBADEGDGCCCGEDABACDBCEBECDDEFBECBDCACBCDCAEC", canonicalSha256: "1ab1605123721a887099265ce3f29d7bb4efbbb3e0a0183e6ec8164d931d2692" },
  "esat-maths2-chemistry-level-2": { sourceDirectory: "esat-maths2-chemistry-level-2", modules: ["Mathematics 1", "Mathematics 2", "Chemistry"], answerKey: "CBDAECBDAECBDAEBCDAECBDAECBDBECBCBBCBBBCBBCCDDCCBCCBEDADFHCGBGEFCBEACDCBEBADFDFEA", canonicalSha256: "8405e6d2ace47606527c76993dc44b735881d79ff4488699fe38ff9623590ec0" },

  "esat-maths2-biology-level-0": { sourceDirectory: "esat-maths2-biology-level-0", modules: ["Mathematics 1", "Mathematics 2", "Biology"], answerKey: "GCBBEGDCBCADBADCBDCEECEDECCAFDADDFBDDBEEBCADACBAACCDCDCAHCEECDBBEGCDBBEEEEDABCBHB", canonicalSha256: "4246661ec11e6f40660302d25aeb9bb436861001d26fb1f34ca706b5dad88be3" },
  "esat-maths2-biology-level-1": { sourceDirectory: "esat-maths2-biology-level-1", modules: ["Mathematics 1", "Mathematics 2", "Biology"], answerKey: "CBECDDEAADDCBABEEEDEDDCDDACCACCCBDEDFDBADEGDGCCCGEDABADCCGCFEFCDBEBDCEEHBCEDBBCFE", canonicalSha256: "b0d3e2508334e54c9bedf5ae8df544ffb5249bce24bcb0ad1e7ddf882278c076" },
  "esat-maths2-biology-level-2": { sourceDirectory: "esat-maths2-biology-level-2", modules: ["Mathematics 1", "Mathematics 2", "Biology"], answerKey: "CBDAECBDAECBDAEBCDAECBDAECBDBECBCBBCBBBCBBCCDDCCBCCBEDCFBCCDCDCBBEFECDBBEEAEDFECH", canonicalSha256: "485eec79a3b3c0644a52a6e2dd31a12e3cb503116b14773fd25e7df06a40919b" },

  "esat-chemistry-biology-level-0": { sourceDirectory: "esat-chemistry-biology-level-0", modules: ["Mathematics 1", "Chemistry", "Biology"], answerKey: "GCBBEGDCBCADBADCBDCEECEDECCBDCDDDFCBHCADCBAFBCBCDBCCECCAHCEECDBBEGCDBBEEEEDABCBHB", canonicalSha256: "f89b83c945775fba092284a13d295db72ff2884f54b57d34ebe66fb8019deb9f" },
  "esat-chemistry-biology-level-1": { sourceDirectory: "esat-chemistry-biology-level-1", modules: ["Mathematics 1", "Chemistry", "Biology"], answerKey: "CBECDDEAADDCBABEEEDEDDCDDACCDBCEBECDDEFBECBDCACBCDCAECDCCGCFEFCDBEBDCEEHBCEDBBCFE", canonicalSha256: "25f542a3d0cae9b53faa7961605b371c8d608401083253158ca326c16bf507c9" },
  "esat-chemistry-biology-level-2": { sourceDirectory: "esat-chemistry-biology-level-2", modules: ["Mathematics 1", "Chemistry", "Biology"], answerKey: "CBDAECBDAECBDAEBCDAECBDAECBADFHCGBGEFCBEACDCBEBADFDFEACFBCCDCDCBBEFECDBBEEAEDFECH", canonicalSha256: "21cdb9359dabe7c374f0ed77d26c05695405b21f4c4956a0ccada2ad3c8c47bd" },
  "esat-recall-2024-25-engineering": { sourceDirectory: "esat-recall-2024-25-engineering", modules: ["Mathematics 1", "Mathematics 2", "Physics"], answerKey: "CADEDBBCAECBEEADABDADCEBDECBDACAEDABBEDCACCADCCDEBEBEBEBACEBCABDCECCACEBBCDECBDAE", canonicalSha256: "9f80461ac16ccd3c8de0b0ef4887934cecaea58d00ed88b31f9a89f6ea4f9ada" },
  "esat-recall-2024-25-physics-chemistry": { sourceDirectory: "esat-recall-2024-25-physics-chemistry", modules: ["Mathematics 1", "Physics", "Chemistry"], answerKey: "CADEDBBCAECBEEADABDADCEBDECEBACEBCABDCECCACEBBCDECBDAECAEBDBADCECAEBDACEBDECADBCA", canonicalSha256: "d59f1b7b9c948b66f9bfc5be77a4d9325af490a0ed8afd9ec68dec67b9a02b3c" },
  "esat-recall-2024-25-physics-biology": { sourceDirectory: "esat-recall-2024-25-physics-biology", modules: ["Mathematics 1", "Physics", "Biology"], answerKey: "CADEDBBCAECBEEADABDADCEBDECEBACEBCABDCECCACEBBCDECBDAEAFBCAEBCCFCDDCDBEDABHAGEBEE", canonicalSha256: "62aa5660b4ff7d5366c2250e1d81ee97eacc9bfada19d463cb342495963c1b81" },
  "esat-recall-2024-25-maths2-chemistry": { sourceDirectory: "esat-recall-2024-25-maths2-chemistry", modules: ["Mathematics 1", "Mathematics 2", "Chemistry"], answerKey: "CADEDBBCAECBEEADABDADCEBDECBDACAEDABBEDCACCADCCDEBEBEBCAEBDBADCECAEBDACEBDECADBCA", canonicalSha256: "f63ecc89d69ef746f2471ce25befe1d405b32a6c4bbe5d4cfe721200762faba4" },
  "esat-recall-2024-25-maths2-biology": { sourceDirectory: "esat-recall-2024-25-maths2-biology", modules: ["Mathematics 1", "Mathematics 2", "Biology"], answerKey: "CADEDBBCAECBEEADABDADCEBDECBDACAEDABBEDCACCADCCDEBEBEBAFBCAEBCCFCDDCDBEDABHAGEBEE", canonicalSha256: "46a1b27d6c4f64c5057b9fe834a19b89defad964145453c6f92baf374daeb816" },
  "esat-recall-2024-25-chemistry-biology": { sourceDirectory: "esat-recall-2024-25-chemistry-biology", modules: ["Mathematics 1", "Chemistry", "Biology"], answerKey: "CADEDBBCAECBEEADABDADCEBDECCAEBDBADCECAEBDACEBDECADBCAAFBCAEBCCFCDDCDBEDABHAGEBEE", canonicalSha256: "3c05386f4b7a723c2f4cf222e1fbd6fdfc7c5c392d6738cdb330f2f98c5e4d1a" },
});

const SECTION_RANGES = [
  [0, 27],
  [27, 54],
  [54, 81],
] as const;

function expandTest(
  testId: string,
  seed: CanonicalSeed,
): EsatCanonicalTest {
  const answers = Object.freeze(seed.answerKey.split(""));

  if (
    answers.length !== 81 ||
    answers.some((answer) => !/^[A-H]$/.test(answer))
  ) {
    throw new Error(`Invalid canonical ESAT answer key for ${testId}.`);
  }

  return Object.freeze({
    testId,
    keyVersion: ESAT_CANONICAL_KEY_VERSION,
    sourceFile:
      `public/esat-practice-tests/tests/${seed.sourceDirectory}/index.html`,
    expectedQuestions: 81,
    sectionRanges: SECTION_RANGES,
    modules: seed.modules,
    canonicalSha256: seed.canonicalSha256,
    answers,
  });
}

export const ESAT_CANONICAL_TESTS: Readonly<
  Record<string, EsatCanonicalTest>
> = Object.freeze(
  Object.fromEntries(
    Object.entries(SEEDS).map(([testId, seed]) => [
      testId,
      expandTest(testId, seed),
    ]),
  ),
);

export function getCanonicalEsatTest(
  testId: string,
): EsatCanonicalTest | null {
  return ESAT_CANONICAL_TESTS[testId] ?? null;
}
