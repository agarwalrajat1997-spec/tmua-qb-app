import { NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";
import { supabaseServer } from "@/utils/supabase/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type IncomingEvent = {
  question_id?: unknown;
  topic_id?: unknown;
  selected_answer?: unknown;
  is_correct?: unknown;
  attempted_at?: unknown;
  client_event_id?: unknown;
  metadata?: unknown;
};

function text(value: unknown, maxLength = 500): string | null {
  if (value == null) return null;
  const clean = String(value).trim();
  return clean ? clean.slice(0, maxLength) : null;
}

function boolean(value: unknown): boolean | null {
  return typeof value === "boolean" ? value : null;
}

function timestamp(value: unknown): string {
  const parsed = new Date(String(value || ""));
  return Number.isFinite(parsed.getTime())
    ? parsed.toISOString()
    : new Date().toISOString();
}

function serviceClient() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key =
    process.env.SUPABASE_SERVICE_ROLE_KEY ||
    process.env.SUPABASE_SERVICE_KEY;

  if (!url || !key) {
    throw new Error("Supabase service credentials are missing.");
  }

  return createClient(url, key, {
    auth: {
      persistSession: false,
      autoRefreshToken: false,
    },
  });
}

export async function POST(request: Request) {
  try {
    const authClient = await supabaseServer();
    const {
      data: { user },
      error: authError,
    } = await authClient.auth.getUser();

    if (authError || !user) {
      return NextResponse.json(
        { error: "Authentication required." },
        { status: 401 },
      );
    }

    const body = await request.json();
    const incoming: IncomingEvent[] = Array.isArray(body?.events)
      ? body.events
      : [body];

    const rows = incoming
      .slice(0, 100)
      .map((event) => {
        const questionId = text(event.question_id, 160);
        const isCorrect = boolean(event.is_correct);

        if (!questionId || isCorrect == null) {
          return null;
        }

        const attemptedAt = timestamp(event.attempted_at);
        const selectedAnswer = text(event.selected_answer, 80);
        const suppliedEventId = text(event.client_event_id, 500);
        const clientEventId =
          suppliedEventId ||
          [
            user.id,
            questionId,
            selectedAnswer || "",
            String(isCorrect),
            attemptedAt,
          ].join("|");

        return {
          user_id: user.id,
          email: user.email?.toLowerCase() || null,
          product: "tmua-question-bank",
          question_id: questionId,
          topic_id: text(event.topic_id, 160),
          selected_answer: selectedAnswer,
          is_correct: isCorrect,
          attempted_at: attemptedAt,
          source: "tmua-question-bank",
          client_event_id: clientEventId,
          history_quality: "observed",
          metadata:
            event.metadata &&
            typeof event.metadata === "object" &&
            !Array.isArray(event.metadata)
              ? event.metadata
              : {},
        };
      })
      .filter(
        (
          row,
        ): row is NonNullable<typeof row> => row !== null,
      );

    if (!rows.length) {
      return NextResponse.json(
        { error: "No valid answer events were supplied." },
        { status: 400 },
      );
    }

    const admin = serviceClient();
    const { error } = await admin
      .from("tmua_qb_attempt_events")
      .upsert(rows, {
        onConflict: "client_event_id",
        ignoreDuplicates: true,
      });

    if (error) {
      console.error("TMUA QB event insert failed:", error);
      return NextResponse.json(
        { error: "Could not record question-bank evidence." },
        { status: 500 },
      );
    }

    return NextResponse.json({
      ok: true,
      accepted: rows.length,
    });
  } catch (error) {
    console.error("TMUA QB attempt-event route failed:", error);
    return NextResponse.json(
      {
        error: "Unexpected attempt-event error.",
        message:
          error instanceof Error ? error.message : String(error),
      },
      { status: 500 },
    );
  }
}