import assert from "node:assert/strict";
import {
  normalizeSupabaseEnv,
  resolvePublicSupabaseConfig,
  PORTAL_SUPABASE_URL,
  PORTAL_SUPABASE_PUBLISHABLE_KEY,
} from "../lib/supabase/public-config.ts";
import { loginErrorMessage } from "../lib/auth/login-error.ts";

const fakeJwt = (role, ref = "pnkzxzigpkvhlmhsmzdd") => [
  Buffer.from(JSON.stringify({ alg: "HS256", typ: "JWT" })).toString("base64url"),
  Buffer.from(JSON.stringify({ role, ref })).toString("base64url"),
  "not-a-real-signature",
].join(".");

for (const suffix of ["\r\n", "\\r\\n", " \\r\\n\n ", ""]) {
  const result = resolvePublicSupabaseConfig({
    NEXT_PUBLIC_SUPABASE_URL: PORTAL_SUPABASE_URL + suffix,
    NEXT_PUBLIC_SUPABASE_ANON_KEY: fakeJwt("service_role") + suffix,
  });
  assert.equal(result.url, PORTAL_SUPABASE_URL);
  assert.equal(result.key, PORTAL_SUPABASE_PUBLISHABLE_KEY);
  assert.deepEqual(result.rejectedVariables, ["NEXT_PUBLIC_SUPABASE_ANON_KEY"]);
  assert.equal(new URL("/auth/v1/otp", result.url).pathname, "/auth/v1/otp");
}

assert.equal(normalizeSupabaseEnv("  value\\r\\n\n"), "value");
assert.equal(resolvePublicSupabaseConfig({ NEXT_PUBLIC_SUPABASE_ANON_KEY: fakeJwt("anon") }).key, fakeJwt("anon"));
for (const badKey of ["sb_secret_test-only", fakeJwt("authenticated"), fakeJwt("anon", "wrong-project"), "invalid"]) {
  const result = resolvePublicSupabaseConfig({ NEXT_PUBLIC_SUPABASE_ANON_KEY: badKey });
  assert.equal(result.key, PORTAL_SUPABASE_PUBLISHABLE_KEY);
  assert.equal(result.rejectedVariables.length, 1);
}
assert.equal(resolvePublicSupabaseConfig({
  NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: PORTAL_SUPABASE_PUBLISHABLE_KEY,
  NEXT_PUBLIC_SUPABASE_ANON_KEY: fakeJwt("service_role"),
}).key, PORTAL_SUPABASE_PUBLISHABLE_KEY);

for (const badUrl of ["http://example.com", "https://user:pass@example.com", PORTAL_SUPABASE_URL + "/wrong", PORTAL_SUPABASE_URL + "?key=x", PORTAL_SUPABASE_URL + "\\r\\n/other"]) {
  assert.throws(() => resolvePublicSupabaseConfig({ NEXT_PUBLIC_SUPABASE_URL: badUrl }));
}
assert.throws(() => resolvePublicSupabaseConfig({ NEXT_PUBLIC_SUPABASE_URL: "https://different.supabase.co" }), /public Supabase key/);
for (const message of ["Failed to fetch", "Load failed", "fetch failed", "Connection timeout"]) {
  assert.match(loginErrorMessage(new Error(message)), /could not reach the sign-in service/);
}
assert.match(loginErrorMessage(new Error("For security purposes, try again in 60 seconds")), /wait a minute/);
assert.equal(loginErrorMessage(new Error("Invalid email address")), "Invalid email address");
console.log("Supabase public config and login error regression checks passed.");
