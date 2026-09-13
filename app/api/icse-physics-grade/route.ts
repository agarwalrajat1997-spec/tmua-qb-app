import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";

type GradeSpec = {
  question: string;
  rubric: string;
  marks: number;
};

const GRADE_SPECS: Record<number, GradeSpec> = {
  1: {
    marks: 2,
    question:
      "Rewrite the incomplete definition of displacement as a complete physics definition, then state two physically meaningful differences between distance and displacement.",
    rubric:
      "2 marks: complete definition includes change in position or straight-line separation and direction/vector character, plus two valid differences such as path dependence, scalar versus vector, or distance being at least the magnitude of displacement. 1 mark: mostly correct but incomplete. 0: major misconception.",
  },
  2: {
    marks: 2,
    question:
      "Explain why a passenger seated in a uniformly moving train can correctly say she is at rest while an observer on the platform correctly says she is moving. Explicitly use a reference object or frame.",
    rubric:
      "2 marks: states motion/rest is relative and correctly identifies rest relative to train and motion relative to platform/ground. 1 mark: idea present but reference frame not clearly applied. 0: claims one observer must be wrong.",
  },
  3: {
    marks: 2,
    question:
      "Judge the claim 'If speed remains constant, velocity must remain constant', correct it, and give one valid physical example.",
    rubric:
      "2 marks: rejects claim, explains velocity also depends on direction, and gives a valid example such as uniform circular motion or turning at constant speed. 1 mark: concept right but example/explanation incomplete. 0: accepts claim.",
  },
  4: {
    marks: 2,
    question:
      "Using the area under a velocity-time graph for uniform acceleration from u to v in time t, explain why s=(u+v)t/2 and hence obtain s=ut+1/2 at^2.",
    rubric:
      "2 marks: identifies the area as trapezium or rectangle plus triangle, obtains s=(u+v)t/2 or s=ut+1/2(v-u)t, then uses v-u=at to obtain s=ut+1/2at^2. 1 mark: correct idea but one algebraic bridge missing. 0: only quotes the final formula.",
  },
  19: {
    marks: 2,
    question:
      "Correct the claim that the same signed area calculation under a velocity-time graph gives both distance and displacement. Explain how areas are used for displacement and total distance.",
    rubric:
      "2 marks: displacement is the algebraic/signed area while distance is the sum of magnitudes/unsigned areas. 1 mark: recognizes the distinction but explanation is incomplete. 0: treats both identically.",
  },
};

function sameOriginBrowserRequest(req: NextRequest) {
  const site = req.headers.get("sec-fetch-site");
  return !site || site === "same-origin" || site === "none";
}

export async function POST(req: NextRequest) {
  if (!sameOriginBrowserRequest(req)) {
    return NextResponse.json({ error: "Cross-site request rejected." }, { status: 403 });
  }

  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    return NextResponse.json(
      { error: "AI grader is not configured on the server." },
      { status: 503 }
    );
  }

  let body: any;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON." }, { status: 400 });
  }

  const questionId = Number(body?.questionId);
  const spec = GRADE_SPECS[questionId];
  const response = String(body?.response ?? "").trim();

  if (!spec) {
    return NextResponse.json({ error: "Unsupported question." }, { status: 400 });
  }
  if (!response) {
    return NextResponse.json({ score: 0, feedback: "No response submitted." });
  }
  if (response.length > 3000) {
    return NextResponse.json({ error: "Response is too long." }, { status: 400 });
  }

  const model = process.env.OPENAI_GRADING_MODEL || "gpt-5-mini";

  const upstream = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model,
      temperature: 0,
      messages: [
        {
          role: "system",
          content:
            "You are a strict ICSE Grade 9 Physics examiner. Grade only against the supplied rubric. Reward scientifically equivalent wording. Do not award marks for vague keyword lists that do not communicate the physics.",
        },
        {
          role: "user",
          content:
            `Question:\n${spec.question}\n\nRubric:\n${spec.rubric}\n\nStudent response:\n${response}`,
        },
      ],
      response_format: {
        type: "json_schema",
        json_schema: {
          name: "physics_grade",
          strict: true,
          schema: {
            type: "object",
            properties: {
              score: { type: "number", minimum: 0, maximum: spec.marks },
              feedback: { type: "string" },
            },
            required: ["score", "feedback"],
            additionalProperties: false,
          },
        },
      },
    }),
  });

  const data = await upstream.json().catch(() => ({}));

  if (!upstream.ok) {
    console.error("OpenAI grading error", upstream.status, data);
    return NextResponse.json({ error: "AI grader unavailable." }, { status: 502 });
  }

  let parsed: any = {};
  try {
    parsed = JSON.parse(data?.choices?.[0]?.message?.content || "{}");
  } catch {
    return NextResponse.json({ error: "Invalid grader response." }, { status: 502 });
  }

  let score = Number(parsed?.score);
  if (!Number.isFinite(score)) score = 0;
  score = Math.max(0, Math.min(spec.marks, score));

  return NextResponse.json({
    score,
    feedback: String(parsed?.feedback || "Graded against the ICSE rubric."),
  });
}
