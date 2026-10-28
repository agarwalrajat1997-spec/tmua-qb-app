// Retain saved attempts from the previous catalogue naming scheme.
const legacyPrefix = "TMUA-\u004a\u005a-";

export function canonicalQuestionIdentity(value: string): string {
  return value.split(legacyPrefix).join("TMUA-TS-");
}

export function canonicalQuestionState<T>(value: T): T {
  if (typeof value === "string") return canonicalQuestionIdentity(value) as T;
  if (Array.isArray(value)) return value.map(canonicalQuestionState) as T;
  if (!value || typeof value !== "object") return value;
  const input = value as Record<string, unknown>;
  return Object.fromEntries(Object.entries(input).flatMap(([key, item]) => {
    const canonical = canonicalQuestionIdentity(key);
    // A newer canonical entry wins if an old tab also retained the legacy key.
    if (canonical !== key && Object.hasOwn(input, canonical)) return [];
    return [[canonical, canonicalQuestionState(item)]];
  })) as T;
}
