import { safeLoginDestination } from "@/lib/auth/login-destination";
import { supabaseBrowser } from "@/utils/supabase/browser";

function retryDestination(next: string) {
  const path = new URL(next, "https://apps.thrivingscholars.com").pathname;
  const login = path === "/amc" || path.startsWith("/amc/") || path.startsWith("/amc-")
    ? "/amc-login"
    : path === "/sat" || path.startsWith("/sat/") || path.startsWith("/sat-") ? "/sat-login" : "/login";
  return `${login}?e=invalid_or_consumed_link&next=${encodeURIComponent(next)}`;
}

/** Only the browser can read implicit-flow fragments. Never forward them to a
 * server URL, logs, analytics, custom storage, or the rendered component. */
export async function completeImplicitLogin(): Promise<string> {
  const next = safeLoginDestination(new URLSearchParams(window.location.search).get("next"));
  const retry = retryDestination(next);
  const fragment = window.location.hash;

  try {
    // Clear the ENTIRE fragment (including unknown/provider parameters) before
    // constructing the Supabase client, awaiting work, or making any request.
    window.history.replaceState(null, "", `/auth/complete?next=${encodeURIComponent(next)}`);
  } catch {
    // If history is unavailable, do not initialise auth while tokens remain.
    return retry;
  }

  const params = new URLSearchParams(fragment.replace(/^#/, ""));
  const accessToken = params.get("access_token");
  const refreshToken = params.get("refresh_token");
  if (params.has("error") || params.has("error_code") || !accessToken || !refreshToken ||
    params.getAll("access_token").length !== 1 || params.getAll("refresh_token").length !== 1 ||
    params.get("token_type")?.toLowerCase() !== "bearer") return retry;

  let client: ReturnType<typeof supabaseBrowser> | undefined;
  let sessionEstablished = false;
  try {
    client = supabaseBrowser();
    const { data, error } = await client.auth.setSession({
      access_token: accessToken,
      refresh_token: refreshToken,
    });
    if (error || !data.session) return retry;
    sessionEstablished = true;
    // Cookie presence or a locally decoded JWT is not verification. Confirm
    // with Auth; the destination still performs its normal product/expiry gate.
    const verified = await client.auth.getUser();
    if (verified.error || !verified.data.user) throw new Error("Unverified session");
    return next;
  } catch {
    if (client && sessionEstablished) {
      try { await client.auth.signOut({ scope: "local" }); } catch { /* Never expose provider errors or tokens. */ }
    }
    return retry;
  }
}
