import fs from "node:fs";
import crypto from "node:crypto";
import vm from "node:vm";

const KEY_VERSION =
  "tmua-canonical-keys-20260809-v1";

const registryPath =
  "lib/server/tmua-canonical-tests.ts";

const cataloguePath =
  "supabase/migrations/20260807054500_tmua_test_catalog_and_validity.sql";

const expectedSources = {
  "full-mock-01-all-topics":
    "public/practice-tests/tests/full-mock-01-all-topics.html",

  "full-mock-02-all-topics":
    "public/practice-tests/tests/full-mock-02-all-topics.html",

  "full-official-2016":
    "public/practice-tests/tests/full-official-2016.html",

  "full-official-2017":
    "public/practice-tests/tests/full-official-2017.html",

  "full-official-2018":
    "public/practice-tests/tests/full-official-2018.html",

  "full-official-2019":
    "public/practice-tests/tests/full-official-2019.html",

  "full-official-2020":
    "public/practice-tests/tests/full-official-2020.html",

  "full-official-2021":
    "public/practice-tests/tests/full-official-2021.html",

  "full-official-2022":
    "public/practice-tests/tests/full-official-2022.html",

  "full-official-2023":
    "public/practice-tests/tests/full-official-2023.html",

  "full-specimen":
    "public/practice-tests/tests/full-specimen.html",

  "p1-mock-01-algebra-sequences-functions-geometry":
    "public/practice-tests/tests/p1-mock-01-algebra-sequences-functions-geometry.html",

  "p1-mock-02-graphs-trig-logs":
    "public/practice-tests/tests/p1-mock-02-graphs-trig-logs.html",

  "p1-mock-03-calculus":
    "public/practice-tests/tests/p1-mock-03-calculus.html",

  "p2-mock-04-logic-proofs":
    "public/practice-tests/tests/p2-mock-04-logic-proofs.html",

  "p1-mock-05-all-topics":
    "public/practice-tests/tests/p1-mock-05-all-topics.html",

  "p2-mock-06-all-topics":
    "public/practice-tests/tests/p2-mock-06-all-topics.html",

  "tmua-2024-2025-challenging-mock":
    "public/practice-tests/tests/tmua-2024-2025-challenging-mock/index.html",
};

function normalizeText(path) {
  return fs
    .readFileSync(
      path,
      "utf8"
    )
    .replace(/\r\n/g, "\n");
}

function sha(value) {
  return crypto
    .createHash("sha256")
    .update(value, "utf8")
    .digest("hex");
}

function balancedArray(
  source,
  start
) {
  if (source[start] !== "[") {
    throw new Error(
      "Array extraction did not start at ["
    );
  }

  let depth = 0;
  let quote = null;
  let escaped = false;
  let lineComment = false;
  let blockComment = false;

  for (
    let i = start;
    i < source.length;
    i++
  ) {
    const ch =
      source[i];

    const next =
      source[i + 1];

    if (lineComment) {
      if (ch === "\n") {
        lineComment = false;
      }
      continue;
    }

    if (blockComment) {
      if (
        ch === "*" &&
        next === "/"
      ) {
        blockComment = false;
        i++;
      }
      continue;
    }

    if (quote) {
      if (escaped) {
        escaped = false;
        continue;
      }

      if (ch === "\\") {
        escaped = true;
        continue;
      }

      if (ch === quote) {
        quote = null;
      }

      continue;
    }

    if (
      ch === "/" &&
      next === "/"
    ) {
      lineComment = true;
      i++;
      continue;
    }

    if (
      ch === "/" &&
      next === "*"
    ) {
      blockComment = true;
      i++;
      continue;
    }

    if (
      ch === "'" ||
      ch === '"' ||
      ch === "`"
    ) {
      quote = ch;
      continue;
    }

    if (ch === "[") {
      depth++;
    }
    else if (ch === "]") {
      depth--;

      if (depth === 0) {
        return source.slice(
          start,
          i + 1
        );
      }
    }
  }

  throw new Error(
    "Unterminated array"
  );
}

function escapeRegex(value) {
  return value.replace(
    /[.*+?^${}()|[\]\\]/g,
    "\\$&"
  );
}

function findArray(
  source,
  names
) {
  for (const name of names) {

    const pattern =
      new RegExp(
        "\\b(?:const|let|var)\\s+" +
        escapeRegex(name) +
        "\\s*=\\s*" +
        "(?:Object\\.freeze\\s*\\(\\s*)?" +
        "\\[",
        "g"
      );

    const matches =
      [...source.matchAll(pattern)];

    if (!matches.length) {
      continue;
    }

    if (matches.length !== 1) {
      throw new Error(
        name +
        ": found " +
        matches.length +
        " candidate arrays"
      );
    }

    const opening =
      source.indexOf(
        "[",
        matches[0].index
      );

    return {
      name,
      literal:
        balancedArray(
          source,
          opening
        )
    };
  }

  return null;
}

function evaluateArray(
  literal,
  label
) {
  const value =
    vm.runInNewContext(
      "(" + literal + ")",
      Object.create(null),
      {
        timeout: 1000,
        filename: label
      }
    );

  if (!Array.isArray(value)) {
    throw new Error(
      label + ": expected array"
    );
  }

  return Array.from(value);
}

function answersFromQuestions(
  literal,
  label
) {
  try {
    const questions =
      evaluateArray(
        literal,
        label
      );

    const answers =
      questions.map(
        question =>
          question &&
          typeof question === "object"
            ? question.answer
            : null
      );

    if (
      answers.length &&
      answers.every(
        answer => answer != null
      )
    ) {
      return answers;
    }
  }
  catch (_) {
    // Safe lexical fallback.
  }

  const answers = [];

  const pattern =
    /(?:\banswer\b|["']answer["'])\s*:\s*["']([A-H])["']/gi;

  let match;

  while (
    (match = pattern.exec(literal)) !== null
  ) {
    answers.push(
      match[1].toUpperCase()
    );
  }

  return answers;
}

function extractActiveKey(
  source,
  testId
) {
  const direct =
    findArray(
      source,
      [
        "correctAnswers",
        "CORRECT_ANSWERS",
        "answerKey",
        "ANSWER_KEY",
        "answer_key"
      ]
    );

  if (direct) {
    return evaluateArray(
      direct.literal,
      testId
    );
  }

  const questions =
    findArray(
      source,
      [
        "QUESTIONS",
        "questions",
        "TEST_QUESTIONS",
        "testQuestions"
      ]
    );

  if (!questions) {
    throw new Error(
      testId +
      ": no canonical answer source found"
    );
  }

  return answersFromQuestions(
    questions.literal,
    testId
  );
}

/*
 * Parse the committed registry without executing TypeScript.
 */
const registrySource =
  normalizeText(
    registryPath
  );

const startMarker =
  "/* TMUA_CANONICAL_JSON_START */";

const endMarker =
  "/* TMUA_CANONICAL_JSON_END */";

const start =
  registrySource.indexOf(
    startMarker
  );

const end =
  registrySource.indexOf(
    endMarker
  );

if (
  start < 0 ||
  end <= start
) {
  throw new Error(
    "Canonical registry markers are missing"
  );
}

let block =
  registrySource
    .slice(
      start + startMarker.length,
      end
    )
    .trim();

const assignment =
  "export const TMUA_CANONICAL_TESTS =";

if (
  !block.startsWith(
    assignment
  )
) {
  throw new Error(
    "Canonical registry assignment is malformed"
  );
}

block =
  block
    .slice(
      assignment.length
    )
    .trim();

const suffix =
  "as const;";

if (
  !block.endsWith(
    suffix
  )
) {
  throw new Error(
    "Canonical registry suffix is malformed"
  );
}

const jsonText =
  block
    .slice(
      0,
      -suffix.length
    )
    .trim();

const registry =
  JSON.parse(
    jsonText
  );

const expectedIds =
  Object
    .keys(expectedSources)
    .sort();

const registryIds =
  Object
    .keys(registry)
    .sort();

if (
  JSON.stringify(expectedIds) !==
  JSON.stringify(registryIds)
) {
  throw new Error(
    "Registry does not contain exactly 18 expected tests"
  );
}

/*
 * Phase 2A catalogue must expose exactly the same 18 IDs.
 */
const catalogue =
  normalizeText(
    cataloguePath
  );

const recognisedCatalogueIds =
  [
    ...catalogue.matchAll(
      /'((?:full-|p1-|p2-|tmua-)[^']+)'/g
    )
  ]
    .map(
      match => match[1]
    )
    .filter(
      id =>
        Object.prototype.hasOwnProperty.call(
          expectedSources,
          id
        )
    );

const catalogueIds =
  [
    ...new Set(
      recognisedCatalogueIds
    )
  ].sort();

if (
  JSON.stringify(catalogueIds) !==
  JSON.stringify(expectedIds)
) {
  throw new Error(
    "Phase 2A catalogue and canonical registry differ"
  );
}

let full = 0;
let paper1 = 0;
let paper2 = 0;

for (const testId of expectedIds) {

  const item =
    registry[testId];

  const sourceFile =
    expectedSources[testId];

  if (
    item.sourceFile !==
    sourceFile
  ) {
    throw new Error(
      testId +
      ": unexpected active source file"
    );
  }

  if (
    sourceFile.includes(
      "_backup"
    )
  ) {
    throw new Error(
      testId +
      ": backup source forbidden"
    );
  }

  if (
    item.keyVersion !==
    KEY_VERSION
  ) {
    throw new Error(
      testId +
      ": key version mismatch"
    );
  }

  const activeSource =
    normalizeText(
      sourceFile
    );

  const activeAnswers =
    extractActiveKey(
      activeSource,
      testId
    ).map(
      value =>
        String(value)
          .trim()
          .toUpperCase()
    );

  if (
    activeAnswers.length !==
    item.expectedQuestions
  ) {
    throw new Error(
      testId +
      ": active answer count changed"
    );
  }

  if (
    item.answers.length !==
    item.expectedQuestions
  ) {
    throw new Error(
      testId +
      ": server answer count invalid"
    );
  }

  for (
    let index = 0;
    index < activeAnswers.length;
    index++
  ) {

    if (
      activeAnswers[index] !==
      item.answers[index]
    ) {
      throw new Error(
        testId +
        ": key drift at Q" +
        (index + 1)
      );
    }
  }

  const activeHash =
    sha(
      activeAnswers.join("")
    );

  if (
    activeHash !==
    item.canonicalSha256
  ) {
    throw new Error(
      testId +
      ": SHA-256 mismatch"
    );
  }

  if (item.structure === "full") {

    full++;

    if (
      item.expectedQuestions !== 40 ||
      JSON.stringify(item.paper1Range) !==
        JSON.stringify([0,20]) ||
      JSON.stringify(item.paper2Range) !==
        JSON.stringify([20,40])
    ) {
      throw new Error(
        testId +
        ": invalid full-test structure"
      );
    }
  }
  else if (
    item.structure === "paper1"
  ) {

    paper1++;

    if (
      item.expectedQuestions !== 20 ||
      JSON.stringify(item.paper1Range) !==
        JSON.stringify([0,20]) ||
      item.paper2Range !== null
    ) {
      throw new Error(
        testId +
        ": invalid Paper 1 structure"
      );
    }
  }
  else if (
    item.structure === "paper2"
  ) {

    paper2++;

    if (
      item.expectedQuestions !== 20 ||
      item.paper1Range !== null ||
      JSON.stringify(item.paper2Range) !==
        JSON.stringify([0,20])
    ) {
      throw new Error(
        testId +
        ": invalid Paper 2 structure"
      );
    }
  }
  else {
    throw new Error(
      testId +
      ": invalid structure"
    );
  }
}

if (
  full !== 12 ||
  paper1 !== 4 ||
  paper2 !== 2
) {
  throw new Error(
    "Canonical structure counts are incorrect"
  );
}

console.log(
  "TMUA canonical-key verification passed: " +
  "18 server-owned keys exactly match the active test pages; " +
  "12 full tests preserve the 20+20 split; " +
  "4 Paper 1 and 2 Paper 2 tests contain exactly 20 answers; " +
  "the Phase 2A catalogue matches; backup sources are excluded."
);
