# IB portal foundation

Entry point: `https://apps.thrivingscholars.com/ib`.
Dedicated sign-in: `/ib-login`.

The portal shares the existing TMUA/ESAT Next.js application and Supabase Auth
project. No new project, email provider, entitlement, checkout, or database table
is required for this empty foundation. Existing programme gates are unchanged.

## Navigation

`/ib?subject=math-aa-hl&view=questions` is the default.
`subject=physics-hl` switches subject; `view=mocks` opens mock tests.
Subject and view survive refresh, deep links, login, and expired-link retries.
Both pages are responsive and intentionally excluded from indexing.

The five Maths topic groups describe the current AA course, whose final assessment
is November 2028. Physics uses the five themes of the course first assessed in
2025. Maths subtopic groupings are navigation categories, not official syllabus
reference numbers. Sources:
- https://www.ibo.org/programmes/diploma-programme/curriculum/mathematics/
- https://www.ibo.org/globalassets/new-structure/university-admission/pdfs/subject-guides/mathematics-analysis-approaches-guide.pdf
- https://www.ibo.org/globalassets/new-structure/university-admission/pdfs/subject-guides/physics-guide.pdf

## Authentication

The existing proxy protects `/ib/:path*`; the server page independently verifies
the user. The public form uses the existing same-origin `/api/auth/login-intent`
cookie and `signInWithOtp` magic-link flow with the existing `/auth/callback` URL.
It does not change the shared email template or redirect allowlist. PKCE,
token-hash and implicit callbacks retain their existing handling. Failed IB
callbacks return to `/ib-login` with the selected subject/view. No separate
numeric OTP form is advertised because the existing template sends a link.

No sign-in emails are sent by automated checks. Test email delivery manually with
a consenting test account and the newest link in the same browser/device.

## Next content phase

- Topic IDs and course metadata: `lib/ib/catalog.ts`.
- Empty, versioned content manifest: `content/ib/catalog.json` (outside `public`).
- Question and mock import types / server-only summaries: `lib/ib/content.ts`.
- Question records reserve written mark schemes; no video fields are needed.
- Counts currently reflect zero published questions and mocks; no sample content
  or fabricated progress is shown. Topic expansion and topic search work now.

Before publishing content, implement schema validation, authenticated question /
mark-scheme delivery and the practice/test player, then load approved material.
Keep stable IDs for attempt history. Add a separately approved IB entitlement if
this will become paid content; do not grant it using unrelated TMUA/ESAT products.
If storing content, attempts or uploads in Supabase, add and verify RLS and private
storage policies before writing student data. No upload/admin page is exposed in
this foundation release.

## Validation

Run `npm run build` (includes the existing portal regression checks),
`npm run verify:login-routing` and `node scripts/verify-auth-callback-flows.mjs`.
Visual checks: desktop/mobile login, both subjects, topic search and expansion,
mock-test empty state, and unauthenticated `/ib` redirect. Auth callback checks
use isolated synthetic clients/tokens; they do not send live emails.
