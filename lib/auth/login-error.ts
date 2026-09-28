export function loginErrorMessage(error: unknown): string {
  const message = error instanceof Error ? error.message : "";
  if (/failed to fetch|fetch failed|load failed|network.*(?:error|request)|timed?\s*out|timeout/i.test(message)) {
    return "We could not reach the sign-in service. Please try again shortly. If this continues, message us on WhatsApp +44 7459 070019.";
  }
  if (/rate.?limit|too many requests|security purposes/i.test(message)) {
    return "Please wait a minute before requesting another link, and check your inbox and spam folder for the newest email.";
  }
  return message || "Could not send the login link. Please try again or contact support.";
}
