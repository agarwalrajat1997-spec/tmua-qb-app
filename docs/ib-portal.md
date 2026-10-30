# IB portal and Maths AA HL question bank

Entry point: `https://apps.thrivingscholars.com/ib`.
Dedicated sign-in: `/ib-login`.

The portal shares the existing TMUA/ESAT Next.js application and Supabase Auth
project. No new project, email provider, entitlement, checkout, or database table
is required for the question bank. Existing programme gates are unchanged.

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
- https://xmltwo.ibo.org/publications/EAD/2026_EN/GR4/GR4-Physics_EN.pdf

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

## Question bank

The six supplied Maths reference collections map to 962 separately authored
variants. Each stable ID retains the reference question number. Original PDF
files and extracted original text are not deployed. The authored questions,
worked solutions and private authoring notes live outside `public` in
`content/ib/math-aa-hl/` and are imported only by server code.

| Collection | Questions |
| --- | ---: |
| Number & algebra | 229 |
| Functions | 129 |
| Geometry & trigonometry | 182 |
| Statistics & probability | 149 |
| Calculus I | 126 |
| Calculus II | 147 |

- `/ib/question-bank/[collection]`: eight questions per page; keyword, subtopic,
  difficulty and calculator filters, with shareable query parameters.
- `/ib/questions/[id]`: the question by itself.
- `/ib/mark-scheme/[id]`: the question alongside its worked scheme, opened in a
  separate tab from each question. On small screens the sections stack. Print
  styles omit navigation and controls.
- Every question shows difficulty, calculator status and total marks. Each
  scheme allocates method, accuracy and reasoning marks by part.
- There are no video solutions, AI-feedback actions or fabricated progress.

`lib/ib/question.ts` validates records, allocations and self-contained diagrams.
Markdown/LaTeX is rendered on the server through React Markdown and KaTeX;
untrusted HTML and trusted KaTeX commands are disabled. Question rendering uses
an explicit projection which excludes answers, schemes and private review notes.
Every content route verifies the Supabase user independently of the proxy.
Nested question, filter and mark-scheme destinations survive magic-link login.

When a source print omitted a figure, table or subpart, a self-contained variant
was reconstructed for the identifiable mathematical task. These are not claimed
to recover an unreadable original exactly. Per-question verification notes and
the authoring review reports record significant changes. Difficulty labels are
practice-bank estimates, not official IB classifications. The content is
independent IB-style practice, not an official IB or Revision Village product.

## Future content

Physics HL now has 640 original questions across all five themes and 24 subtopics;
see [Physics bank documentation](ib-physics-question-bank.md) for content, diagrams,
Cloudflare delivery and review records. Mock-test views retain honest empty states. The versioned mock
manifest is `content/ib/catalog.json`; no upload/admin page is exposed. There is
no attempt-history or scoring database in this release. Keep stable question IDs
if these features are added. Add a separately approved IB entitlement if
this will become paid content; do not grant it using unrelated TMUA/ESAT products.
If storing content, attempts or uploads in Supabase, add and verify RLS and private
storage policies before writing student data.

## Validation

Run `npm run build` (includes the content and existing portal regression checks).
`npm run verify:ib-question-bank` checks all 962 records, contiguous source
mapping, exact duplicates, part/total marks, every LaTeX expression and SVG
safety, then renders the actual components and routes with isolated synthetic
fixtures. Route checks cover filters, empty states, unknown/draft IDs, server
authorization, private-answer separation and separate-tab links.

`npm run verify:login-routing` and `node scripts/verify-auth-callback-flows.mjs`
cover nested IB destinations and expired-link retries with synthetic tokens.
No automated check sends email or writes student data. Content authors use
algebraic, symbolic and numerical checks, followed by independent sample reviews;
the schema/parser checks alone do not establish mathematical correctness.

For a local visual review without real auth, `scripts/render-ib-review.mjs`
renders the actual components into an isolated static review directory. It is
development tooling, is not imported by the application and creates no deployed
authentication bypass. The production routes always retain authentication.
