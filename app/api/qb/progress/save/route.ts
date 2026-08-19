/* eslint-disable @typescript-eslint/no-explicit-any */

import { NextResponse } from "next/server";
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import {
  ESAT_TABLE_CANDIDATES,
  adminClient,
} from "@/app/api/esat/qb/_server";

type QBUpdate =
  | {
      question_id: string;
      status?: string | null;
      selected_answer?: string | null;
      flagged?: boolean | null;
      time_spent?: number | null;
      last_seen_at?: string | null;
      answer_elapsed_seconds?: number | null;
      answer_submitted_at?: string | null;
      submission_id?: string | null;
    }
  | { key: string; value: any }; // compatibility: value should be an object with fields above

async function supabaseServer() {
  const cookieStore = await cookies();
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL!;
  const key =
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!;
  return createServerClient(url, key, {
    cookies: {
      get(name: string) {
        return cookieStore.get(name)?.value;
      },
      set(name: string, value: string, options: any) {
        cookieStore.set({ name, value, ...options });
      },
      remove(name: string, options: any) {
        cookieStore.set({ name, value: "", ...options });
      },
    },
  });
}

function jsonErr(status: number, error: string, extra?: any) {
  return NextResponse.json({ error, ...(extra ? { extra } : {}) }, { status });
}

function toIsoOrNull(x: any): string | null {
  if (!x) return null;
  const s = String(x);
  const d = new Date(s);
  if (Number.isNaN(d.getTime())) return null;
  return d.toISOString();
}

function normaliseAnswer(value: unknown): string {
  return String(value ?? "").trim().toUpperCase();
}

async function captureEsatPredictorEvents(
  user: { id: string; email?: string | null },
  rows: any[],
) {
  const submittedRows = rows.filter(
    (row) =>
      row.product === "esat-question-bank" &&
      typeof row.submission_id === "string" &&
      row.submission_id.trim() !== "" &&
      normaliseAnswer(row.selected_answer) !== "",
  );

  if (submittedRows.length === 0) {
    return;
  }

  const admin = adminClient();
  const qids = [
    ...new Set(
      submittedRows.map((row) => String(row.question_id)),
    ),
  ];

  let canonicalRows: any[] | null = null;

  for (const table of ESAT_TABLE_CANDIDATES) {
    const result = await admin
      .from(table)
      .select("qid,topic,difficulty,answer,is_active")
      .in("qid", qids)
      .eq("is_active", true);

    if (!result.error) {
      canonicalRows = result.data ?? [];
      break;
    }
  }

  if (canonicalRows == null) {
    throw new Error(
      "Unable to load canonical ESAT questions for predictor capture.",
    );
  }

  const canonicalByQid = new Map(
    canonicalRows.map((row) => [String(row.qid), row]),
  );

  const eventRows = submittedRows.flatMap((row) => {
    const question = canonicalByQid.get(String(row.question_id));

    if (!question) {
      return [];
    }

    const selectedAnswer = normaliseAnswer(row.selected_answer);
    const canonicalAnswer = normaliseAnswer(question.answer);

    if (!selectedAnswer || !canonicalAnswer) {
      return [];
    }

    const responseSeconds = Number.isFinite(
      Number(row.answer_elapsed_seconds),
    )
      ? Math.max(0, Math.round(Number(row.answer_elapsed_seconds)))
      : null;

    const predictorEligible =
      responseSeconds !== null && responseSeconds >= 10;

    const isCorrect = selectedAnswer === canonicalAnswer;
    const numericDifficulty = Number(question.difficulty);

    return [{
      user_id: user.id,
      email: user.email?.toLowerCase() ?? null,
      product: "esat-question-bank",
      question_id: String(question.qid),
      topic_id: String(question.topic ?? "") || null,
      selected_answer: selectedAnswer,
      is_correct: isCorrect,
      attempted_at:
        row.answer_submitted_at ?? row.updated_at ?? new Date().toISOString(),
      source: "qb-progress-trigger-v2",
      client_event_id:
        `esat-qb-progress|${user.id}|${row.submission_id}`,
      history_quality: "observed",
      metadata: {
        capture_version: "20260819-1",
        canonical_qid: String(question.qid),
        saved_status: String(row.status ?? ""),
      },
      status: isCorrect ? "correct" : "wrong",
      difficulty: Number.isFinite(numericDifficulty)
        ? numericDifficulty
        : null,
      response_seconds: responseSeconds,
      predictor_eligible: predictorEligible,
      exclusion_reason:
        responseSeconds === null
          ? "missing_response_time"
          : responseSeconds < 10
            ? "under_10_seconds"
            : null,
      submission_id: String(row.submission_id),
    }];
  });

  if (eventRows.length === 0) {
    return;
  }

  const { error } = await admin
    .from("tmua_qb_attempt_events")
    .upsert(eventRows, {
      onConflict: "client_event_id",
      ignoreDuplicates: true,
    });

  if (error) {
    throw new Error(
      `ESAT predictor event capture failed: ${error.message}`,
    );
  }
}

export async function POST(req: Request) {
  try {
    const supabase = await supabaseServer();

    const { data: auth, error: authErr } = await supabase.auth.getUser();
    if (authErr || !auth?.user) return jsonErr(401, "Not authenticated");

    const body = await req.json().catch(() => null);
    const updates = body?.updates as QBUpdate[] | undefined;

    const email = String(auth.user.email || "").toLowerCase();
    const requestedProduct = String(body?.product || "tmua-question-bank");

    const allowedProducts = new Set([
      "tmua-question-bank",
      "esat-question-bank"
    ]);

    const product = allowedProducts.has(requestedProduct)
      ? requestedProduct
      : "tmua-question-bank";

    if (!Array.isArray(updates) || updates.length === 0) {
      return jsonErr(400, "updates is required");
    }

    // Build upsert rows
    const nowIso = new Date().toISOString();
    const rows: any[] = [];

    for (const u of updates) {
      // Compatibility path: { key, value }
      if ((u as any)?.key && typeof (u as any)?.key === "string") {
        const qid = String((u as any).key || "").trim();
        const v = (u as any).value;
        if (!qid) continue;
        if (!v || typeof v !== "object") continue; // can't store a string blob in this schema

        rows.push({
          user_id: auth.user.id,
          email,
          product,
          question_id: qid,
          status: v.status ?? null,
          selected_answer: v.selected_answer ?? v.selectedAnswer ?? null,
          flagged: typeof v.flagged === "boolean" ? v.flagged : null,
          time_spent: Number.isFinite(Number(v.time_spent)) ? Number(v.time_spent) : (Number.isFinite(Number(v.timeSpent)) ? Number(v.timeSpent) : null),
          last_seen_at: toIsoOrNull(v.last_seen_at ?? v.lastSeenAt) ?? null,
          answer_elapsed_seconds: Number.isFinite(Number(v.answer_elapsed_seconds ?? v.answerElapsedSeconds))
            ? Math.max(0, Math.round(Number(v.answer_elapsed_seconds ?? v.answerElapsedSeconds)))
            : null,
          answer_submitted_at: toIsoOrNull(v.answer_submitted_at ?? v.answerSubmittedAt),
          submission_id: String(v.submission_id ?? v.submissionId ?? "").trim() || null,
          updated_at: nowIso,
        });
        continue;
      }

      // Normal path: { question_id, ... }
      const qid = String((u as any).question_id || "").trim();
      if (!qid) continue;

      rows.push({
        user_id: auth.user.id,
          email,
        product,
        question_id: qid,
        status: (u as any).status ?? null,
        selected_answer: (u as any).selected_answer ?? null,
        flagged: typeof (u as any).flagged === "boolean" ? (u as any).flagged : null,
        time_spent: Number.isFinite(Number((u as any).time_spent)) ? Number((u as any).time_spent) : null,
        last_seen_at: toIsoOrNull((u as any).last_seen_at) ?? null,
        answer_elapsed_seconds: Number.isFinite(Number((u as any).answer_elapsed_seconds))
          ? Math.max(0, Math.round(Number((u as any).answer_elapsed_seconds)))
          : null,
        answer_submitted_at: toIsoOrNull((u as any).answer_submitted_at),
        submission_id: String((u as any).submission_id ?? "").trim() || null,
        updated_at: nowIso,
      });
    }

    if (rows.length === 0) {
      return jsonErr(400, "No valid updates (missing question_id or value object)");
    }

    const { error } = await supabase
      .from("qb_progress")
      .upsert(rows, { onConflict: "user_id,product,question_id" });

    if (error) {
      return jsonErr(500, "Supabase upsert failed", { message: error.message });
    }

    if (product === "esat-question-bank") {
      await captureEsatPredictorEvents(auth.user, rows);
    }

    return NextResponse.json({ ok: true, saved: rows.length });
  } catch (e: any) {
    return NextResponse.json(
      { error: "Unhandled error in /api/qb/progress/save", message: String(e?.message || e), stack: String(e?.stack || "") },
      { status: 500 }
    );
  }
}

