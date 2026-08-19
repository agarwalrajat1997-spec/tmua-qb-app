import { NextResponse } from "next/server";
import { getCanonicalEsatTest } from "@/lib/server/esat-canonical-tests";
import { estimateEsatTestScores } from "@/lib/server/esat-score-estimates";
import { getCanonicalTmuaTest } from "@/lib/server/tmua-canonical-tests";
import { createSupabaseServerClient } from "@/lib/supabase/server";

export const runtime = "nodejs";

const FINGERPRINT =
  "SUBMIT_ROUTE_V4_TMUA_AUTHORITATIVE_20260807";

const SERVER_AUTHORITY =
  "TMUA_SERVER_CANONICAL_AUTHORITY_V1_20260809";

const ESAT_SERVER_AUTHORITY =
  "ESAT_SERVER_CANONICAL_AUTHORITY_V1_20260819";

type CatalogRow = {
  test_id: string;
  title: string;
  paper: "full" | "1" | "2";
  expected_questions: number;
  score_conversion_profile: string | null;
};

type FinalAttemptRow = {
  id: string;
  submitted_at: string;
  test_id: string;
  score: number;
  tmua_score9: number | null;
  attempt_number: number | null;
  paper_1_score: number | null;
  paper_2_score: number | null;
  is_full_timed_attempt: boolean | null;
  score_conversion_profile: string | null;
  predictor_metadata: Record<string, unknown> | null;
};

type PredictorEvaluationRow = {
  attempt_id: string;
  predictor_eligible: boolean;
  combined_score_eligible: boolean;
  effective_weight: number;
  paper_1_raw_score: number;
  paper_2_raw_score: number;
  authoritative_tmua_score9: number | null;
  score_conversion_profile: string | null;
  score_conversion_version: string | null;
  score_status: string | null;
  exclusion_reason: string | null;
};

function badRequest(message: string) {
  return NextResponse.json(
    {
      error: message,
      fingerprint: FINGERPRINT,
    },
    {
      status: 400,
    },
  );
}

function internalError(message: string) {
  return NextResponse.json(
    {
      error: message,
      fingerprint: FINGERPRINT,
    },
    {
      status: 500,
    },
  );
}

function finiteInteger(
  value: unknown,
  fallback = 0,
): number {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return fallback;
  }

  return Math.max(0, Math.round(number));
}

function normaliseAnswer(
  value: unknown,
): string | null {
  if (value == null) {
    return null;
  }

  const answer = String(value)
    .trim()
    .toUpperCase();

  return answer || null;
}

function normaliseAnswerArray(
  value: unknown,
  expectedLength?: number,
): Array<string | null> {
  const source = Array.isArray(value)
    ? value
    : [];

  const targetLength =
    expectedLength == null
      ? source.length
      : expectedLength;

  return Array.from(
    { length: targetLength },
    (_, index) =>
      normaliseAnswer(source[index]),
  );
}

function normaliseTimeArray(
  value: unknown,
  expectedLength?: number,
): number[] {
  const source = Array.isArray(value)
    ? value
    : [];

  const targetLength =
    expectedLength == null
      ? source.length
      : expectedLength;

  return Array.from(
    { length: targetLength },
    (_, index) => {
      const seconds = Number(source[index]);

      return Number.isFinite(seconds)
        ? Math.max(0, seconds)
        : 0;
    },
  );
}

function normaliseFlagArray(
  value: unknown,
  expectedLength?: number,
): boolean[] {
  const source = Array.isArray(value)
    ? value
    : [];

  const targetLength =
    expectedLength == null
      ? source.length
      : expectedLength;

  return Array.from(
    { length: targetLength },
    (_, index) =>
      source[index] === true,
  );
}

function correctCount(
  answers: Array<string | null>,
  correctAnswers: Array<string | null>,
  offset: number,
  limit: number,
): number {
  let correct = 0;

  const end = Math.min(
    answers.length,
    correctAnswers.length,
    offset + limit,
  );

  for (
    let index = offset;
    index < end;
    index += 1
  ) {
    const answer = answers[index];
    const expected = correctAnswers[index];

    if (
      answer != null &&
      expected != null &&
      answer === expected
    ) {
      correct += 1;
    }
  }

  return correct;
}

function incorrectQuestionNumbers(
  answers: Array<string | null>,
  correctAnswers: Array<string | null>,
  totalQuestions: number,
): number[] {
  const incorrect: number[] = [];

  for (
    let index = 0;
    index < totalQuestions;
    index += 1
  ) {
    if (
      answers[index] == null ||
      correctAnswers[index] == null ||
      answers[index] !== correctAnswers[index]
    ) {
      incorrect.push(index + 1);
    }
  }

  return incorrect;
}

function exactAnswerArraysMatch(
  submitted: Array<string | null>,
  canonical: readonly string[],
): boolean {
  if (submitted.length !== canonical.length) {
    return false;
  }

  return canonical.every(
    (expected, index) =>
      submitted[index] === expected,
  );
}

function safeIsoDate(
  value: unknown,
): string | null {
  if (value == null || value === "") {
    return null;
  }

  const date = new Date(String(value));

  if (Number.isNaN(date.valueOf())) {
    return null;
  }

  return date.toISOString();
}

export async function POST(req: Request) {
  const supabase =
    await createSupabaseServerClient();

  const {
    data: { user },
    error: userError,
  } = await supabase.auth.getUser();

  if (userError || !user) {
    return NextResponse.json(
      {
        error: "Unauthorized",
        fingerprint: FINGERPRINT,
      },
      {
        status: 401,
      },
    );
  }

  // This long-lived compatibility endpoint accepts several generations
  // of standalone test payloads before normalising them below.
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let body: any;

  try {
    body = await req.json();
  } catch {
    return badRequest("Invalid JSON");
  }

  const testId =
    String(body?.test_id || "").trim();

  if (!testId) {
    return badRequest("test_id is required");
  }

  const {
    data: catalogData,
    error: catalogError,
  } = await supabase
    .from("tmua_test_catalog")
    .select(
      "test_id,title,paper,expected_questions,score_conversion_profile",
    )
    .eq("test_id", testId)
    .maybeSingle();

  if (catalogError) {
    return internalError(
      `TMUA catalogue lookup failed: ${
        catalogError.message
      }`,
    );
  }

  const catalog =
    catalogData as CatalogRow | null;

  const canonicalTmuaTest =
    getCanonicalTmuaTest(testId);

  const recognisedTmuaTest =
    canonicalTmuaTest != null;

  const canonicalEsatTest =
    getCanonicalEsatTest(testId);

  const recognisedEsatTest =
    canonicalEsatTest != null;

  if (canonicalTmuaTest && !catalog) {
    return internalError(
      "Protected TMUA test is missing from the catalogue.",
    );
  }

  if (catalog && !canonicalTmuaTest) {
    return internalError(
      "TMUA catalogue entry has no canonical server answer key.",
    );
  }

  const submittedAnswers =
    normaliseAnswerArray(body?.answers);

  const submittedCorrectAnswersRaw =
    body?.correct_answers;

  const submittedCorrectAnswers =
    normaliseAnswerArray(
      submittedCorrectAnswersRaw,
    );

  const clientCorrectAnswersSupplied =
    Array.isArray(
      submittedCorrectAnswersRaw,
    );

  let answers = submittedAnswers;
  let correctAnswers =
    submittedCorrectAnswers;

  let timeSpent =
    normaliseTimeArray(body?.time_spent);

  let flags =
    normaliseFlagArray(body?.flags);

  let totalQuestions =
    finiteInteger(
      body?.total_questions,
      Math.max(
        answers.length,
        correctAnswers.length,
      ),
    );

  let paper =
    body?.paper == null
      ? null
      : String(body.paper);

  let testTitle =
    body?.test_title == null
      ? null
      : String(body.test_title);

  const submittedScore =
    body?.score;


  const clientScoreSupplied =
    submittedScore != null &&
    submittedScore !== "";


  let rawScore =
    finiteInteger(submittedScore);

  let paper1Score: number | null =
    null;

  let paper2Score: number | null =
    null;

  let incorrect =
    Array.isArray(body?.incorrect)
      ? body.incorrect
      : [];

  let scoreConversionProfile:
    string | null = null;

  let clientCorrectAnswersMatchCanonical:
    boolean | null = null;

  let clientScoreMatchesAuthoritative:
    boolean | null = null;

  let esatScoreEstimate:
    ReturnType<typeof estimateEsatTestScores> | null = null;

  if (catalog && canonicalTmuaTest) {
    const canonicalPaper =
      canonicalTmuaTest.structure === "full"
        ? "full"
        : canonicalTmuaTest.structure === "paper1"
          ? "1"
          : "2";

    const catalogExpectedQuestions =
      finiteInteger(
        catalog.expected_questions,
      );

    if (
      catalogExpectedQuestions !==
        canonicalTmuaTest.expectedQuestions ||
      catalog.paper !== canonicalPaper
    ) {
      return internalError(
        "TMUA catalogue and canonical registry disagree.",
      );
    }

    if (
      !Array.isArray(body?.answers) ||
      body.answers.length !==
        canonicalTmuaTest.expectedQuestions
    ) {
      return badRequest(
        `answers must contain exactly ${
          canonicalTmuaTest.expectedQuestions
        } entries for this TMUA test.`,
      );
    }

    totalQuestions =
      canonicalTmuaTest.expectedQuestions;

    paper = canonicalPaper;
    testTitle = catalog.title;

    scoreConversionProfile =
      catalog.score_conversion_profile;

    answers =
      normaliseAnswerArray(
        body.answers,
        totalQuestions,
      );

    // SECURITY: recognised TMUA tests are scored only
    // against the server-owned canonical answer key.
    correctAnswers =
      normaliseAnswerArray(
        canonicalTmuaTest.answers,
        totalQuestions,
      );

    timeSpent =
      normaliseTimeArray(
        body?.time_spent,
        totalQuestions,
      );

    flags =
      normaliseFlagArray(
        body?.flags,
        totalQuestions,
      );

    clientCorrectAnswersMatchCanonical =
      clientCorrectAnswersSupplied
        ? submittedCorrectAnswers.length ===
            totalQuestions &&
          exactAnswerArraysMatch(
            submittedCorrectAnswers,
            canonicalTmuaTest.answers,
          )
        : null;

    rawScore =
      correctCount(
        answers,
        correctAnswers,
        0,
        totalQuestions,
      );

    clientScoreMatchesAuthoritative =
      clientScoreSupplied
        ? finiteInteger(
            submittedScore,
            -1,
          ) === rawScore
        : null;

    if (paper === "full") {
      paper1Score =
        correctCount(
          answers,
          correctAnswers,
          0,
          20,
        );

      paper2Score =
        correctCount(
          answers,
          correctAnswers,
          20,
          20,
        );
    } else if (paper === "1") {
      paper1Score = rawScore;
    } else if (paper === "2") {
      paper2Score = rawScore;
    }

    incorrect =
      incorrectQuestionNumbers(
        answers,
        correctAnswers,
        totalQuestions,
      );
  }
  else if (canonicalEsatTest) {
    if (
      !Array.isArray(body?.answers) ||
      body.answers.length !==
        canonicalEsatTest.expectedQuestions
    ) {
      return badRequest(
        `answers must contain exactly ${
          canonicalEsatTest.expectedQuestions
        } entries for this ESAT test.`,
      );
    }

    totalQuestions =
      canonicalEsatTest.expectedQuestions;

    paper = "full";

    answers = normaliseAnswerArray(
      body.answers,
      totalQuestions,
    );

    // SECURITY: recognised ESAT papers are scored only against
    // the committed server-owned canonical answer key.
    correctAnswers = normaliseAnswerArray(
      canonicalEsatTest.answers,
      totalQuestions,
    );

    timeSpent = normaliseTimeArray(
      body?.time_spent,
      totalQuestions,
    );

    flags = normaliseFlagArray(
      body?.flags,
      totalQuestions,
    );

    clientCorrectAnswersMatchCanonical =
      clientCorrectAnswersSupplied
        ? submittedCorrectAnswers.length === totalQuestions &&
          exactAnswerArraysMatch(
            submittedCorrectAnswers,
            canonicalEsatTest.answers,
          )
        : null;

    const sectionScores =
      canonicalEsatTest.sectionRanges.map(
        ([start, end]) =>
          correctCount(
            answers,
            correctAnswers,
            start,
            end - start,
          ),
      );

    rawScore = sectionScores.reduce(
      (sum, value) => sum + value,
      0,
    );

    paper1Score = sectionScores[0];
    paper2Score = sectionScores[1];

    esatScoreEstimate = estimateEsatTestScores(
      testId,
      sectionScores,
    );

    clientScoreMatchesAuthoritative =
      clientScoreSupplied
        ? finiteInteger(submittedScore, -1) === rawScore
        : null;

    incorrect = incorrectQuestionNumbers(
      answers,
      correctAnswers,
      totalQuestions,
    );
  }

  const submittedAt =
    new Date().toISOString();

  const payload = {
    user_id: user.id,
    email: user.email ?? null,

    test_id: testId,
    test_title: testTitle,
    paper,
    total_questions: totalQuestions,

    // For recognised TMUA and ESAT tests, this is recomputed by
    // the server from submitted responses rather than trusting
    // body.score.
    score: rawScore,

    // The database validity/finalisation triggers decide
    // whether an overall /9 score is allowed.
    tmua_score9: null,

    answers,
    correct_answers: correctAnswers,
    time_spent: timeSpent,
    flags,
    incorrect,

    attempt_number: null,
    started_at:
      safeIsoDate(body?.started_at),

    paper_1_score: paper1Score,
    paper_2_score: paper2Score,

    is_full_timed_attempt: false,

    score_conversion_profile:
      scoreConversionProfile,

    predictor_metadata: {
      recognised_tmua_test:
        recognisedTmuaTest,

      recognised_esat_test:
        recognisedEsatTest,

      submission_route:
        FINGERPRINT,

      raw_score_recomputed_server_side:
        recognisedTmuaTest ||
        recognisedEsatTest,

      raw_mark_authority:
        recognisedTmuaTest
          ? "server_canonical_key_v1"
          : recognisedEsatTest
            ? "server_esat_canonical_key_v1"
          : "generic_submission",

      server_authority:
        recognisedTmuaTest
          ? SERVER_AUTHORITY
          : recognisedEsatTest
            ? ESAT_SERVER_AUTHORITY
          : null,

      canonical_key_version:
        recognisedTmuaTest
          ? canonicalTmuaTest?.keyVersion ?? null
          : recognisedEsatTest
            ? canonicalEsatTest?.keyVersion ?? null
          : null,

      canonical_key_sha256:
        recognisedTmuaTest
          ? canonicalTmuaTest?.canonicalSha256 ?? null
          : recognisedEsatTest
            ? canonicalEsatTest?.canonicalSha256 ?? null
          : null,

      client_correct_answers_supplied:
        recognisedTmuaTest || recognisedEsatTest
          ? clientCorrectAnswersSupplied
          : null,

      client_correct_answers_match_canonical:
        recognisedTmuaTest || recognisedEsatTest
          ? clientCorrectAnswersMatchCanonical
          : null,

      client_score_supplied:
        recognisedTmuaTest || recognisedEsatTest
          ? clientScoreSupplied
          : null,

      client_score_matches_authoritative:
        recognisedTmuaTest || recognisedEsatTest
          ? clientScoreMatchesAuthoritative
          : null,

      esat_score_estimate_version:
        esatScoreEstimate?.version ?? null,

      esat_modules:
        esatScoreEstimate?.modules ?? null,

      esat_predicted_combined_practice_score:
        esatScoreEstimate?.predictedCombinedPracticeScore ?? null,

      esat_combined_score_official:
        esatScoreEstimate?.combinedScoreOfficial ?? null,



      submitted_total_questions:
        finiteInteger(
          body?.total_questions,
        ),
    },

    session_label:
      body?.session_label ?? null,

    student_name:
      body?.student_name ?? null,

    submitted_at: submittedAt,
  };

  const {
    data: inserted,
    error: insertError,
  } = await supabase
    .from("practice_test_attempts")
    .insert(payload)
    .select("id")
    .single();

  if (insertError || !inserted) {
    return internalError(
      insertError?.message ||
      "Practice-test insertion failed.",
    );
  }

  // AFTER triggers run synchronously with the insert. Fetch the
  // final row separately because INSERT ... RETURNING does not
  // necessarily reflect changes made by a second UPDATE inside
  // an AFTER trigger.
  const {
    data: finalAttemptData,
    error: finalAttemptError,
  } = await supabase
    .from("practice_test_attempts")
    .select(
      "id,submitted_at,test_id,score,tmua_score9,attempt_number,paper_1_score,paper_2_score,is_full_timed_attempt,score_conversion_profile,predictor_metadata",
    )
    .eq("id", inserted.id)
    .single();

  if (finalAttemptError) {
    return internalError(
      finalAttemptError.message,
    );
  }

  const finalAttempt =
    finalAttemptData as FinalAttemptRow | null;

  const {
    data: evaluationData,
    error: evaluationError,
  } = await supabase
    .from("tmua_test_attempt_evaluations")
    .select(
      "attempt_id,predictor_eligible,combined_score_eligible,effective_weight,paper_1_raw_score,paper_2_raw_score,authoritative_tmua_score9,score_conversion_profile,score_conversion_version,score_status,exclusion_reason",
    )
    .eq("attempt_id", inserted.id)
    .maybeSingle();

  if (evaluationError) {
    return internalError(
      evaluationError.message,
    );
  }

  const evaluation =
    evaluationData as PredictorEvaluationRow | null;

  let attemptNumber =
    finalAttempt?.attempt_number ?? null;

  // Non-TMUA tests, including recognised ESAT papers, intentionally
  // have no TMUA evaluation row. Preserve the generic attempt-number
  // behaviour for those submissions.
  if (attemptNumber == null) {
    const {
      count,
      error: countError,
    } = await supabase
      .from("practice_test_attempts")
      .select(
        "id",
        {
          count: "exact",
          head: true,
        },
      )
      .eq("user_id", user.id)
      .eq("test_id", testId);

    if (!countError) {
      attemptNumber = count ?? null;
    }
  }

  return NextResponse.json({
    ok: true,
    fingerprint: FINGERPRINT,
    attempt: finalAttempt,
    attempt_no: attemptNumber,
    predictor_evaluation:
      evaluation ?? null,
  });
}
