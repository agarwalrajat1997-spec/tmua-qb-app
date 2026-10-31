import type { Feedback } from "../types";

export type ReviewStatus = {
  status: "pending" | "complete" | "failed" | "missing";
  feedback?: Feedback;
  error?: string;
  code?: string;
  retryable?: boolean;
};

// Only a response from the review endpoint, bound to this exact submission,
// can establish that a newly allocated request ID was never accepted.
export class ReviewNotAcceptedError extends Error {
  readonly name = "ReviewNotAcceptedError";
  constructor(
    public readonly requestId: string,
    message: string,
  ) {
    super(message);
  }
}

export function reviewRequestError(
  status: number,
  payload: unknown,
  submitted: unknown,
): Error {
  const data = payload as Record<string, unknown> | null;
  const request = submitted as Record<string, unknown> | null;
  const message =
    typeof data?.error === "string"
      ? data.error
      : "The tutor could not finish this review.";
  if (
    [409, 429, 503].includes(status) &&
    data?.accepted === false &&
    data.code === "review_not_accepted" &&
    typeof request?.requestId === "string" &&
    request.requestId.length > 0 &&
    data.requestId === request.requestId
  )
    return new ReviewNotAcceptedError(request.requestId, message);
  return new Error(message);
}
