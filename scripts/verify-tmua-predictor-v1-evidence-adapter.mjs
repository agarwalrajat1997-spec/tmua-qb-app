import fs from "node:fs";
import path from "node:path";

import {
  buildTmuaPredictorInputsByUser,
} from "../lib/server/tmua-predictor-v1-evidence-adapter.ts";

import {
  calculateTmuaPredictorV1,
} from "../lib/server/tmua-predictor-v1-engine.ts";

const root =
  process.cwd();

const adapterPath =
  path.join(
    root,
    "lib",
    "server",
    "tmua-predictor-v1-evidence-adapter.ts",
  );

const source =
  fs.readFileSync(
    adapterPath,
    "utf8",
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

function profiles() {
  return Array.from(
    {
      length: 12,
    },
    (
      _,
      index,
    ) => ({
      profile:
        `profile-${index + 1}`,

      score_values:
        Array.from(
          {
            length: 41,
          },
          (
            _unused,
            raw,
          ) =>
            1 +
            8 *
              (
                raw /
                40
              ),
        ),
    }),
  );
}

assert(
  !source.includes(
    "@supabase",
  ),
  "Evidence adapter itself must remain database-client independent",
);

assert(
  !source.includes(
    "fetch(",
  ),
  "Evidence adapter must not make network requests",
);

assert(
  !source.includes(
    "process.env",
  ),
  "Evidence adapter must not depend on environment variables",
);

assert(
  !source.includes(
    "tmua_prediction_snapshots",
  ),
  "Evidence adapter must not write snapshot storage",
);

const payload = {
  conversionProfiles:
    profiles(),

  activeTopics: [
    "Geometry",
    "Algebra",
    "Geometry",
  ],

  testAttempts: [
    {
      user_id:
        "user-a",

      test_id:
        "p1-live-shape",

      attempt_id:
        "attempt-a",

      attempt_number:
        "1",

      evaluated_at:
        "2026-08-08T01:34:50.50606+00:00",

      predictor_eligible:
        true,

      topic_breadth:
        "broad",

      combined_score_eligible:
        false,

      authoritative_tmua_score9:
        null,

      effective_weight:
        "0.7200",

      paper_1_raw_score:
        13,

      paper_1_effective_weight:
        "0.7200",

      /*
       * Exact important production representation:
       * unused P2 is zero, not NULL.
       */
      paper_2_raw_score:
        0,

      paper_2_effective_weight:
        "0.0000",
    },

    {
      user_id:
        "user-b",

      test_id:
        "full-official-2023",

      attempt_id:
        "attempt-b",

      attempt_number:
        1,

      evaluated_at:
        "2026-08-09T10:00:00.000Z",

      predictor_eligible:
        true,

      topic_breadth:
        "full_syllabus",

      combined_score_eligible:
        true,

      authoritative_tmua_score9:
        "7.20",

      effective_weight:
        "1.0000",

      paper_1_raw_score:
        14,

      paper_1_effective_weight:
        "1.0000",

      paper_2_raw_score:
        15,

      paper_2_effective_weight:
        "1.0000",
    },
  ],

  qbEvents: [
    {
      user_id:
        "user-a",

      id:
        "event-a",

      source:
        "qb-progress-trigger-v2",

      history_quality:
        "observed",

      predictor_eligible:
        true,

      canonical_qid:
        "Q-A",

      canonical_active:
        true,

      selected_answer:
        "B",

      canonical_answer:
        "A",

      canonical_topic:
        "Algebra",

      attempted_at:
        "2026-08-09T12:00:00.000Z",

      claimed_is_correct:
        true,

      client_topic_id:
        "FORGED",
    },
  ],
};

const users =
  buildTmuaPredictorInputsByUser(
    payload,
  );

equal(
  users.length,
  2,
  "Adapter groups exactly two users",
);

equal(
  users[0].userId,
  "user-a",
  "User grouping is deterministic",
);

equal(
  users[0].input
    .conversionProfiles.length,
  12,
  "All twelve conversion profiles are shared into each input",
);

equal(
  users[0].input
    .activeTopics.length,
  2,
  "Active topics are de-duplicated",
);

const userA =
  calculateTmuaPredictorV1(
    users[0].input,
  );

close(
  userA.testWeight,
  0.72,
  "Live P1 row keeps only its explicit P1 weight",
);

close(
  userA.testSignalScore9,
  6.2,
  "Live P1 row ignores zero-weight unused P2",
);

equal(
  userA.diagnostics
    .trustedQbEventCount,
  1,
  "Canonical trigger-v2 event reaches engine",
);

equal(
  users[0].input
    .qbEvents[0]
    .claimedIsCorrect,
  true,
  "Audit correctness field may be carried but not trusted",
);

equal(
  users[0].input
    .qbEvents[0]
    .clientTopicId,
  "FORGED",
  "Client topic may be carried but not trusted",
);

const userB =
  calculateTmuaPredictorV1(
    users[1].input,
  );

close(
  userB.predictedTmuaScore9,
  7.2,
  "Authoritative full /9 passes unchanged through adapter",
);

equal(
  userB.independentTestCount,
  1,
  "Full test remains one independent family",
);

console.log(
  "TMUA Predictor V1 evidence-adapter verification passed:",
);

console.log(
  `${assertions} invariants verified; ` +
  "live numeric/string fields normalize deterministically; " +
  "zero-weight unused paper components remain excluded; " +
  "authoritative full scores pass unchanged; " +
  "canonical QB evidence is mapped without trusting client correctness/topic fields; " +
  "adapter has no database, network or snapshot-write dependency.",
);