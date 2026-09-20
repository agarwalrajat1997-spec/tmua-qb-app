// A failed service call is not evidence that a student's account has no access.
export const SERVICE_RETRY_MESSAGE =
  "We’re having trouble checking your access right now. Please try again in a moment.";

export function isMissingSession(error: unknown): boolean {
  const e = error as { name?: string; code?: string } | null;
  return e?.name === "AuthSessionMissingError" || e?.code === "session_not_found";
}

export async function withServiceTimeout<T>(promise: PromiseLike<T>, ms = 15_000): Promise<T> {
  let timer: ReturnType<typeof setTimeout> | undefined;
  try {
    return await Promise.race([
      Promise.resolve(promise),
      new Promise<never>((_, reject) => {
        timer = setTimeout(() => reject(new Error("Service check timed out")), ms);
      }),
    ]);
  } finally {
    clearTimeout(timer);
  }
}

// Abort the network request as well as bounding the UI wait. Preserve caller cancellation.
export const serviceFetch: typeof fetch = async (input, init = {}) => {
  const timeout = AbortSignal.timeout(12_000);
  const source = init.signal || (input instanceof Request ? input.signal : null);
  const signal = source ? AbortSignal.any([source, timeout]) : timeout;
  try {
    return await fetch(input, { ...init, signal });
  } catch (error) {
    // PostgREST does not retry AbortError. AbortSignal.timeout emits TimeoutError,
    // so normalize cancellation to avoid starting another request after timeout.
    if (signal.aborted) throw new DOMException("Service request aborted", "AbortError");
    throw error;
  }
};
