import type { NextConfig } from "next";

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { join } from "node:path";

import { resolvePublicSupabaseConfig } from "./lib/supabase/public-config";
import { PAST_PAPER_PRACTICE_URL } from "./lib/past-paper-practice";

// The popup artwork is deliberately bundled as text chunks so it cannot be
// replaced by a corrupt static-file/CDN response. Reconstruct and verify the
// exact WebP bytes whenever Next loads this config for a build.
const notepadImageBase64 = Array.from(
  { length: 9 },
  (_, index) => {
    const source = readFileSync(
      join(
        process.cwd(),
        "lib",
        "erasable-notepad-image",
        `chunk-${String(index + 1).padStart(2, "0")}.ts`,
      ),
      "utf8",
    );

    const match = source.match(
      /^export default "([A-Za-z0-9+/=]+)";\s*$/,
    );

    if (!match) {
      throw new Error(
        `Invalid erasable-notepad image chunk ${index + 1}.`,
      );
    }

    return match[1];
  },
).join("");

const notepadImageBytes = Buffer.from(
  notepadImageBase64,
  "base64",
);
const notepadImageGitHash = createHash("sha1")
  .update(
    Buffer.concat([
      Buffer.from(`blob ${notepadImageBytes.length}\0`),
      notepadImageBytes,
    ]),
  )
  .digest("hex");

if (
  notepadImageBase64.length !== 21088 ||
  notepadImageBytes.length !== 15814 ||
  notepadImageBytes.subarray(0, 4).toString("ascii") !== "RIFF" ||
  notepadImageBytes.subarray(8, 12).toString("ascii") !== "WEBP" ||
  notepadImageGitHash !== "b4ab0d3c619b2d359574cc8ae3af6a59f713013b"
) {
  throw new Error(
    "Bundled erasable-notepad artwork failed byte-integrity verification.",
  );
}

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
