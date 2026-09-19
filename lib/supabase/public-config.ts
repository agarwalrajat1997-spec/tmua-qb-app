// Public application identifiers, verified against this project's Supabase API.
// Publishable keys are intentionally public and do not bypass RLS.
export const PORTAL_SUPABASE_URL = "https://pnkzxzigpkvhlmhsmzdd.supabase.co";
export const PORTAL_SUPABASE_PUBLISHABLE_KEY = "sb_publishable_bferrEWIyBKOcNvfOByGow_70SSxWRN";

export function normalizeSupabaseEnv(value: string | undefined): string {
  // PowerShell/CLI env uploads can accidentally append literal \\r\\n as well
  // as real newlines. Remove boundary whitespace only; reject interior junk.
  return (value ?? "").replace(/^(?:\s|\\r|\\n)+|(?:\s|\\r|\\n)+$/g, "");
}

function isPublicKey(key: string, projectRef: string): boolean {
  if (/^sb_publishable_[A-Za-z0-9_-]+$/.test(key)) return true;
  if (!/^eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$/.test(key)) {
    return false;
  }

  try {
    const payload = JSON.parse(Buffer.from(key.split(".")[1], "base64url").toString());
    return payload.role === "anon" && payload.ref === projectRef;
  } catch {
    return false;
  }
}

export function resolvePublicSupabaseConfig(env: Record<string, string | undefined>) {
  const url = normalizeSupabaseEnv(env.NEXT_PUBLIC_SUPABASE_URL) || PORTAL_SUPABASE_URL;
  const parsed = new URL(url);
  if (parsed.protocol !== "https:" || parsed.username || parsed.password ||
      parsed.search || parsed.hash || (parsed.pathname !== "/" && parsed.pathname !== "") ||
      /\s|\\/.test(url)) {
    throw new Error("NEXT_PUBLIC_SUPABASE_URL must be a clean HTTPS origin.");
  }

  const origin = parsed.origin;
  const projectRef = parsed.hostname.split(".")[0];
  const rejectedVariables: string[] = [];
  let selectedKey: string | undefined;
  for (const name of ["NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY", "NEXT_PUBLIC_SUPABASE_ANON_KEY"]) {
    const key = normalizeSupabaseEnv(env[name]);
    if (!key) continue;
    if (!isPublicKey(key, projectRef)) {
      rejectedVariables.push(name);
    } else if (!selectedKey) {
      selectedKey = key;
    }
  }

  // Only this known project may use the verified public fallback. Never send
  // a project's key to a different host or fall back to a service-role key.
  if (!selectedKey && origin === PORTAL_SUPABASE_URL) {
    selectedKey = PORTAL_SUPABASE_PUBLISHABLE_KEY;
  }
  if (!selectedKey) throw new Error("A valid public Supabase key is required.");

  return { url: origin, key: selectedKey, rejectedVariables };
}
