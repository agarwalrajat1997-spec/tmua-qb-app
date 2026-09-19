import type { NextConfig } from "next";

import { resolvePublicSupabaseConfig } from "./lib/supabase/public-config";

const publicSupabase = resolvePublicSupabaseConfig(process.env);
if (publicSupabase.rejectedVariables.length) {
  console.warn(
    `[supabase-config] Ignoring invalid or privileged public key settings: ${publicSupabase.rejectedVariables.join(", ")}. Using a validated public key.`,
  );
}

const nextConfig: NextConfig = {
  // Next replaces these references in BOTH client and server bundles. Never
  // allow an accidentally uploaded service-role key into browser JavaScript.
  env: {
    NEXT_PUBLIC_SUPABASE_URL: publicSupabase.url,
    NEXT_PUBLIC_SUPABASE_ANON_KEY: publicSupabase.key,
    NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: publicSupabase.key,
  },
};

export default nextConfig;
