import type { NextConfig } from "next";

import { resolvePublicSupabaseConfig } from "./lib/supabase/public-config";
import { PAST_PAPER_PRACTICE_URL } from "./lib/past-paper-practice";

const publicSupabase = resolvePublicSupabaseConfig(process.env);
if (publicSupabase.rejectedVariables.length) {
  console.warn(
    `[supabase-config] Ignoring invalid or privileged public key settings: ${publicSupabase.rejectedVariables.join(", ")}. Using a validated public key.`,
  );
}

const nextConfig: NextConfig = {
  outputFileTracingIncludes: { "/api/tmua/studio": ["./content/tmua-studio/**/*"] },
  async headers() {
    return [{
      source: "/auth/:path*",
      headers: [
        { key: "Referrer-Policy", value: "no-referrer" },
        { key: "Cache-Control", value: "private, no-store" },
        { key: "X-Robots-Tag", value: "noindex, nofollow" },
      ],
    }];
  },
  // Next redirects run before authentication, so retired free-resource links
  // also work for signed-out visitors. All other AMC routes stay protected.
  async redirects() {
    return [
      { source: "/tmua-question-bank/index.html", destination: "/tmua-question-bank", permanent: false },
      { source: "/question-bank-tmua", destination: "/tmua-question-bank", permanent: false },
      { source: "/question-bank-tmua/index.html", destination: "/tmua-question-bank", permanent: false },
      {
        source: "/amc",
        has: [{ type: "query", key: "section", value: "past-papers" }],
        destination: PAST_PAPER_PRACTICE_URL,
        permanent: true,
      },
      {
        source: "/amc-past-paper-practice",
        destination: PAST_PAPER_PRACTICE_URL,
        permanent: true,
      },
      {
        source: "/amc-past-paper-practice/index.html",
        destination: PAST_PAPER_PRACTICE_URL,
        permanent: true,
      },
    ];
  },
  // Next replaces these references in BOTH client and server bundles. Never
  // allow an accidentally uploaded service-role key into browser JavaScript.
  env: {
    NEXT_PUBLIC_SUPABASE_URL: publicSupabase.url,
    NEXT_PUBLIC_SUPABASE_ANON_KEY: publicSupabase.key,
    NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: publicSupabase.key,
  },
};

export default nextConfig;
