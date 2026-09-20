type JsonObject = Record<string, unknown>;

export function isObject(value: unknown): value is JsonObject {
  return !!value && typeof value === "object" && !Array.isArray(value);
}

// Answers, flags, timers, filters and their original question keys are retained.
// Worked solutions belong to the question catalogue, not each student's history.
export function compactProgressState(value: unknown): JsonObject {
  if (!isObject(value)) throw new Error("Invalid progress state");
  const state = { ...value };
  if (state.answers !== undefined) {
    if (!isObject(state.answers)) throw new Error("Invalid answers map");
    state.answers = Object.fromEntries(Object.entries(state.answers).map(([key, answer]) => {
      if (["__proto__", "constructor", "prototype"].includes(key) || !isObject(answer)) {
        throw new Error("Invalid answer entry");
      }
      const compact = { ...answer };
      delete compact.solution_html;
      return [key, compact];
    }));
  }
  return state;
}

export function progressStateFromEnvelope(value: unknown): JsonObject {
  if (!isObject(value)) throw new Error("Invalid progress envelope");
  const state = isObject(value.parsed) ? value.parsed
    : typeof value.raw === "string" ? JSON.parse(value.raw) : {};
  return compactProgressState(state);
}
