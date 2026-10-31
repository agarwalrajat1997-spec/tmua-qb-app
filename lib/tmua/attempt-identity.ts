/** Optional browser correlation ID; never an account ID or scoring authority. */
export function readPredictiveAttemptId(value: unknown): string | null {
  if (value === undefined || value === null) return null;
  if (typeof value !== "string" || value.length > 80 ||
    !/^(?:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|attempt-\d{10,16}-[0-9a-f]{1,32})$/i.test(value)) {
    throw new Error("Invalid predictive attempt identifier.");
  }
  return value;
}
