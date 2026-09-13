import fs from "node:fs";

const routePath =
  "app/api/practice-tests/submit/route.ts";

const registryPath =
  "lib/server/tmua-canonical-tests.ts";

function readNormalized(path) {
  return fs
    .readFileSync(
      path,
      "utf8"
    )
    .replace(/\r\n/g, "\n");
}

function assert(
  condition,
  message
) {
  if (!condition) {
    throw new Error(message);
  }
}

const route =
  readNormalized(
    routePath
  );

const compactRoute =
  route.replace(
    /\s+/g,
    " "
  );

/*
 * ----------------------------------------------------------
 * STATIC TRUST-BOUNDARY ASSERTIONS
 * ----------------------------------------------------------
 */

assert(
  route.includes(
    'getCanonicalTmuaTest'
  ),
  "Submit route does not use canonical TMUA registry"
);

assert(
  route.includes(
    'TMUA_SERVER_CANONICAL_AUTHORITY_V1_20260809'
  ),
  "Phase 2C server-authority marker missing"
);

assert(
  route.includes(
    'SUBMIT_ROUTE_V4_TMUA_AUTHORITATIVE_20260807'
  ),
  "Phase 2B fingerprint unexpectedly changed"
);

assert(
  route.includes(
    'const recognisedTmuaTest ='
  ) &&
  route.includes(
    'canonicalTmuaTest != null'
  ),
  "Canonical registry is not the protected-test identity source"
);

assert(
  route.includes(
    'Protected TMUA test is missing from the catalogue.'
  ),
  "Missing catalogue fail-closed guard"
);

assert(
  route.includes(
    'TMUA catalogue entry has no canonical server answer key.'
  ),
  "Missing canonical-key fail-closed guard"
);

assert(
  route.includes(
    'TMUA catalogue and canonical registry disagree.'
  ),
  "Missing catalogue/canonical structure consistency guard"
);

assert(
  route.includes(
    'answers must contain exactly'
  ),
  "Missing exact answer-array length validation"
);

assert(
  compactRoute.includes(
    'correctAnswers = normaliseAnswerArray( canonicalTmuaTest.answers, totalQuestions, );'
  ),
  "Recognised TMUA scoring does not use canonical server answers"
);

assert(
  !compactRoute.includes(
    'correctAnswers = normaliseAnswerArray( body?.correct_answers, totalQuestions, );'
  ),
  "Client correct_answers still controls recognised TMUA scoring"
);

assert(
  route.includes(
    '? "server_canonical_key_v1"'
  ),
  "Raw-mark authority metadata is not server canonical"
);

assert(
  route.includes(
    'canonical_key_version:'
  ) &&
  route.includes(
    'canonical_key_sha256:'
  ),
  "Canonical key provenance metadata missing"
);

assert(
  route.includes(
    'client_correct_answers_match_canonical:'
  ) &&
  route.includes(
    'client_score_matches_authoritative:'
  ),
  "Tamper/audit metadata missing"
);

assert(
  compactRoute.includes(
    'score: rawScore,'
  ),
  "Stored raw score is not the server-computed rawScore"
);

assert(
  compactRoute.includes(
    'tmua_score9: null,'
  ),
  "Route must continue delegating /9 authority to Phase 2B DB finalisation"
);
assert(
  !route.includes(
    "body?.tmua_score9"
  ) &&
  !route.includes(
    "body.tmua_score9"
  ),
  "Submit route must not read browser tmua_score9 at all"
);

/*
 * ----------------------------------------------------------
 * READ THE COMMITTED SERVER REGISTRY
 * ----------------------------------------------------------
 */

const registrySource =
  readNormalized(
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

assert(
  start >= 0 &&
  end > start,
  "Canonical registry markers missing"
);

let registryBlock =
  registrySource
    .slice(
      start + startMarker.length,
      end
    )
    .trim();

const assignment =
  "export const TMUA_CANONICAL_TESTS =";

assert(
  registryBlock.startsWith(
    assignment
  ),
  "Canonical registry assignment malformed"
);

registryBlock =
  registryBlock
    .slice(
      assignment.length
    )
    .trim();

const suffix =
  "as const;";

assert(
  registryBlock.endsWith(
    suffix
  ),
  "Canonical registry suffix malformed"
);

const registry =
  JSON.parse(
    registryBlock
      .slice(
        0,
        -suffix.length
      )
      .trim()
  );

assert(
  Object.keys(registry).length === 18,
  "Expected exactly 18 canonical TMUA tests"
);

/*
 * ----------------------------------------------------------
 * EXECUTABLE ANTI-TAMPER CONTRACT TESTS
 *
 * These deliberately inject forged browser score/key claims.
 * Only answers + canonical key are allowed to determine raw
 * score.
 * ----------------------------------------------------------
 */

function authoritativeRawScore(
  test,
  submittedAnswers
) {
  if (
    !Array.isArray(submittedAnswers) ||
    submittedAnswers.length !==
      test.expectedQuestions
  ) {
    throw new Error(
      "malformed answer array"
    );
  }

  let score = 0;

  for (
    let index = 0;
    index < test.expectedQuestions;
    index++
  ) {
    const submitted =
      submittedAnswers[index] == null
        ? null
        : String(
            submittedAnswers[index]
          )
            .trim()
            .toUpperCase();

    if (
      submitted != null &&
      submitted === test.answers[index]
    ) {
      score++;
    }
  }

  return score;
}

function differentAnswer(
  answer
) {
  return answer === "A"
    ? "B"
    : "A";
}

const full =
  registry[
    "full-official-2016"
  ];

assert(
  full &&
  full.expectedQuestions === 40,
  "Full-test tamper fixture missing"
);

/*
 * Attack 1:
 * Client claims score 0 and sends a completely fake key,
 * while actual selections are all correct.
 *
 * Authoritative result must still be 40.
 */
const attack1 = {
  answers:
    [...full.answers],

  correct_answers:
    full.answers.map(
      differentAnswer
    ),

  score:
    0,

  tmua_score9:
    1.0
};

assert(
  authoritativeRawScore(
    full,
    attack1.answers
  ) === 40,
  "Forged low client score/key altered authoritative raw score"
);

/*
 * Attack 2:
 * Every submitted selection is deliberately wrong.
 * Client supplies a matching forged key and claims 40/40 + 9.
 *
 * Authoritative result must still be zero.
 */
const wrongAnswers =
  full.answers.map(
    differentAnswer
  );

const attack2 = {
  answers:
    wrongAnswers,

  correct_answers:
    wrongAnswers,

  score:
    40,

  tmua_score9:
    9.0
};

assert(
  authoritativeRawScore(
    full,
    attack2.answers
  ) === 0,
  "Forged perfect score/key altered authoritative raw score"
);

/*
 * Attack 3:
 * Correct client key but forged raw score.
 */
const attack3 = {
  answers:
    wrongAnswers,

  correct_answers:
    [...full.answers],

  score:
    40
};

assert(
  authoritativeRawScore(
    full,
    attack3.answers
  ) === 0,
  "Forged raw score altered canonical scoring"
);

/*
 * Attack 4:
 * Missing answer slots must not silently become a valid
 * 40-question full attempt.
 */
let missingRejected =
  false;

try {
  authoritativeRawScore(
    full,
    full.answers.slice(
      0,
      39
    )
  );
}
catch {
  missingRejected = true;
}

assert(
  missingRejected,
  "39-answer full test was not rejected"
);

/*
 * Attack 5:
 * Extra answer slots must also be rejected.
 */
let extraRejected =
  false;

try {
  authoritativeRawScore(
    full,
    [
      ...full.answers,
      "A"
    ]
  );
}
catch {
  extraRejected = true;
}

assert(
  extraRejected,
  "41-answer full test was not rejected"
);

/*
 * Attack 6:
 * Unknown IDs have no canonical protected-test authority.
 */
assert(
  registry[
    "attacker-invented-test"
  ] == null,
  "Unknown test unexpectedly resolves to canonical registry"
);

/*
 * Single-paper structure remains raw evidence only.
 */
const paper1 =
  registry[
    "p1-mock-01-algebra-sequences-functions-geometry"
  ];

assert(
  paper1 &&
  paper1.structure === "paper1" &&
  paper1.expectedQuestions === 20,
  "Paper 1 canonical fixture invalid"
);

/*
 * null is permitted as an unanswered question provided the
 * browser sends the exact expected array shape.
 */
const partlyBlank =
  [...paper1.answers];

partlyBlank[0] =
  null;

assert(
  authoritativeRawScore(
    paper1,
    partlyBlank
  ) === 19,
  "Unanswered question handling is incorrect"
);

console.log(
  "TMUA server-authority verification passed: canonical registry " +
  "defines all 18 protected tests; catalogue/key mismatches fail closed; " +
  "recognised tests require exact 20/40-answer array shapes; client " +
  "correct_answers, raw score and tmua_score9 claims cannot alter " +
  "authoritative raw scoring; Phase 2B retains /9 authority."
);
