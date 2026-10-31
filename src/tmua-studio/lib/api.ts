import type { Exam, Feedback, Question, StoredSolution } from "../types";
import type { Guide } from "./audited-content";
import { reviewRequestError, type ReviewStatus } from "./review-status";

export const STUDIO_API = "/api/tmua/studio";
let viewerId: string | undefined;

export function studioViewerId() {
  return viewerId;
}

// The first verified identity owns this iframe's notebook queue for its lifetime.
export function acceptStudioViewer(id: string) {
  if (!id || (viewerId && viewerId !== id))
    throw Error("Your signed-in account changed. Refresh the question bank before continuing.");
  viewerId = id;
}

export function studioUrl(action: string, params: Record<string, string | undefined> = {}) {
  const query = new URLSearchParams({ action });
  for (const [key, value] of Object.entries(params))
    if (value !== undefined) query.set(key, value);
  return `${STUDIO_API}?${query}`;
}

export async function studioRead<T>(action: string, params: Record<string, string | undefined> = {}): Promise<T> {
  const response = await fetch(studioUrl(action, { ...params, expectedUserId: viewerId }), {
    credentials: "same-origin",
    cache: "no-store",
    signal: AbortSignal.timeout(30_000),
  });
  const result = await response.json() as T & { error?: string };
  if (!response.ok) throw Error(result.error ?? "This question could not be loaded. Please try again.");
  return result;
}

export type StudioQuestion = { viewerId: string; question: Question; guide?: Guide; configured: boolean };
export async function fetchStudioQuestion(qid: string, contentVersion?: string) {
  const result = await studioRead<StudioQuestion>("question", { qid, contentVersion });
  acceptStudioViewer(result.viewerId);
  return result;
}

export async function checkAnswer(qid: string, contentVersion: string | undefined, answer: string) {
  if (!viewerId) throw Error("Sign in before checking your answer.");
  const response = await fetch(STUDIO_API, {
    method: "POST",
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", "X-TS-Studio": "1" },
    body: JSON.stringify({ action: "answer", qid, contentVersion, answer, expectedUserId: viewerId }),
    signal: AbortSignal.timeout(30_000),
  });
  const result = await response.json() as { correct: boolean; error?: string };
  if (!response.ok) throw Error(result.error ?? "Your answer could not be checked. Please try again.");
  return result;
}

export async function checkWorking(body: unknown): Promise<Feedback> {
  if (!viewerId) throw Error("Sign in to Study Studio before sending your working.");
  let response: Response;
  try {
    response = await fetch(STUDIO_API, {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json", "X-TS-Studio": "1" },
      body: JSON.stringify({ ...(body as Record<string, unknown>), action: "review", expectedUserId: viewerId }),
      signal: AbortSignal.timeout(240_000),
    });
  } catch {
    throw Error("The review connection was interrupted. It may still be running. Your working is saved; reopen the question to check the existing review.");
  }
  const result = await response.json() as Feedback & { error?: string; status?: string; requestId?: string };
  if (!response.ok) throw reviewRequestError(response.status, result, body);
  if (response.status === 202 && result.requestId) return awaitReview(result.requestId);
  return result;
}

async function awaitReview(id: string): Promise<Feedback> {
  // Read the accepted job; polling never sends another paid assessment.
  for (let i = 0; i < 120; i++) {
    await new Promise((resolve) => setTimeout(resolve, Math.min(5000, 1200 + i * 300)));
    let result: ReviewStatus;
    try { result = await recoverReview(id); } catch { continue; }
    if (result.status === "complete" && result.feedback) return result.feedback;
    if (result.status === "failed" || result.status === "missing")
      throw Error(result.error ?? "The saved review could not finish. Your original working is safe.");
  }
  throw Error("Your review is still processing. Reopen this question to retrieve it; no new request is needed.");
}

export function getStoredSolution(exam: Exam, qid: string, contentVersion?: string): Promise<StoredSolution> {
  return studioRead("solution", { exam, qid, contentVersion });
}

export function recoverReview(id: string): Promise<ReviewStatus> {
  return studioRead("review-status", { id });
}
