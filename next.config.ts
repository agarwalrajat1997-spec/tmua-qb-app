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
      // Keep bookmarked tests and solution books on the current student edition.
      { source: "/tmua-question-bank/index_diff45_only.html", destination: "/tmua-question-bank", permanent: false },
      { source: "/tmua-question-bank/index.html.backup_safe_mojibake_fix_20260629_192547", destination: "/tmua-question-bank", permanent: false },
      { source: "/practice-tests/tests/_backup_ts_score_note_20260306_132812/:file", destination: "/practice-tests/tests/:file", permanent: false },
      { source: "/practice-tests/tests/:file.pre_restore_20260306_155223", destination: "/practice-tests/tests/:file", permanent: false },
      { source: "/practice-tests/solutions/tmua-2026-predictive-paper-solutions.pdf", destination: "/practice-tests/solutions/2026-11-r1/predictive-paper-worked.pdf", permanent: false },
      { source: "/practice-tests/solutions/topic-test-1/solution.pdf", destination: "/practice-tests/solutions/2026-11-r1/topic-test-1-worked.pdf", permanent: false },
      { source: "/tmua-solutions/topic-test-1-solutions.pdf", destination: "/practice-tests/solutions/2026-11-r1/topic-test-1-worked.pdf", permanent: false },
      { source: "/practice-tests/solutions/topic-test-2/solution.pdf", destination: "/tmua-solutions/topic-test-2-solutions.pdf", permanent: false },
      { source: "/practice-tests/solutions/topic-test-3/solution.pdf", destination: "/practice-tests/solutions/2026-11-r1/topic-test-3-worked.pdf", permanent: false },
      { source: "/tmua-solutions/topic-test-3-solutions.pdf", destination: "/practice-tests/solutions/2026-11-r1/topic-test-3-worked.pdf", permanent: false },
      { source: "/practice-tests/solutions/topic-test-4/solution.pdf", destination: "/tmua-solutions/topic-test-4-solutions.pdf", permanent: false },
      { source: "/practice-tests/solutions/topic-test-5/solution.pdf", destination: "/practice-tests/solutions/2026-11-r1/topic-test-5-worked.pdf", permanent: false },
      { source: "/tmua-solutions/topic-test-5-solutions.pdf", destination: "/practice-tests/solutions/2026-11-r1/topic-test-5-worked.pdf", permanent: false },
      { source: "/tmua-solutions/tmua-2024-2025-challenging-mock-solutions.pdf", destination: "/practice-tests/solutions/2026-11-r1/challenging-mock-worked.pdf", permanent: false },
      { source: "/tmua-solutions/tmua-2024-2025-challenging-full-test-revised-solutions.pdf", destination: "/practice-tests/solutions/2026-11-r1/challenging-mock-worked.pdf", permanent: false },
      { source: "/tmua-tests/topic-test-1", destination: "/practice-tests/tests/p1-mock-01-algebra-sequences-functions-geometry.html", permanent: false },
      { source: "/tmua-tests/topic-test-1/index.html", destination: "/practice-tests/tests/p1-mock-01-algebra-sequences-functions-geometry.html", permanent: false },
      { source: "/tmua-tests/paper1-mock-45", destination: "/dashboard", permanent: false },
      { source: "/tmua-tests/paper1-mock-45/index.html", destination: "/dashboard", permanent: false },
      { source: "/tmua-tests/paper1-mock-75", destination: "/dashboard", permanent: false },
      { source: "/tmua-tests/paper1-mock-75/index.html", destination: "/dashboard", permanent: false },
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
