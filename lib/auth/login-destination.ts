export const LOGIN_DESTINATION_COOKIE = "ts_login_destination";
export const LOGIN_DESTINATION_MAX_AGE_SECONDS = 15 * 60;

const DEFAULT_DESTINATION = "/dashboard";

const ALLOWED_DESTINATION_PREFIXES = [
  "/dashboard",
  "/amc",
  "/sat",
  "/tmua-question-bank",
  "/practice-tests",
  "/amc-question-bank",
  "/amc-8-question-bank",
  "/amc-10-question-bank",
  "/amc-12-question-bank",
  "/sat-question-bank",
  "/sat-practice-tests",
  "/classes",
  "/tmua-classes",
  "/group-sessions",
  "/esat",
  "/esat-question-bank",
  "/esat-practice-tests",
] as const;

export function safeLoginDestination(value: unknown): string {
  if (typeof value !== "string") return DEFAULT_DESTINATION;

  const destination = value.trim();

  if (
    !destination.startsWith("/") ||
    destination.startsWith("//") ||
    destination.includes("\\") ||
    destination.includes("\u0000")
  ) {
    return DEFAULT_DESTINATION;
  }

  let parsed: URL;

  try {
    parsed = new URL(destination, "https://apps.thrivingscholars.com");
  } catch {
    return DEFAULT_DESTINATION;
  }

  const allowed = ALLOWED_DESTINATION_PREFIXES.some(
    (prefix) =>
      parsed.pathname === prefix || parsed.pathname.startsWith(`${prefix}/`),
  );

  if (!allowed) return DEFAULT_DESTINATION;

  return `${parsed.pathname}${parsed.search}`;
}

export function decodeLoginDestination(value: string | undefined): string | null {
  if (!value) return null;

  try {
    return safeLoginDestination(decodeURIComponent(value));
  } catch {
    return null;
  }
}
