# Physics HL question bank

The Physics section of the existing authenticated IB portal contains 640 original
practice questions covering all 24 subtopics of the first-assessment-2025 course.
The corrected guide updated in November 2024 is the syllabus boundary. Questions
and self-drawn figures were independently authored from physical concepts; they
are not renamed or number-swapped copies of a commercial question bank.

| Theme | Collection route suffix | Questions |
| --- | --- | ---: |
| A: Space, time and motion | physics-space-time-motion | 200 |
| B: The particulate nature of matter | physics-particulate-matter | 120 |
| C: Wave behaviour | physics-wave-behaviour | 120 |
| D: Fields | physics-fields | 100 |
| E: Nuclear and quantum physics | physics-nuclear-quantum | 100 |

Entry: `/ib?subject=physics-hl&view=questions`. Collections use
`/ib/question-bank/[collection]`; individual questions use `/ib/questions/ib-phy-…`.
Each question's written mark scheme opens in a separate tab at
`/ib/mark-scheme/[id]`. There are no video or AI-feedback actions. Physics mock
tests retain their empty state; this release is a practice question bank.

## Content and marking

There are 260 multiple-choice, 287 structured and 93 data-based questions.
Multiple-choice questions award exactly one mark and include explanatory physics
in their written scheme. Structured/data parts allocate distinct method,
accuracy and reasoning points. Alternatives and error carried forward are
described where appropriate; there is no blanket significant-figure or unit
penalty. Difficulty labels are reasoned practice estimates, not official IB
classifications or empirical grade boundaries. Coloured bars are accompanied by
text labels. All current Physics question styles allow a calculator.

Core and additional-HL tags, syllabus code, question type, difficulty, keyword,
pagination and subtopic filters have shareable destinations and survive login.
All 24 official subtopic codes have content. The shared Maths bank retains its
962 records and stable routes.

`scripts/ib-physics-authoring/` contains deterministic standard-library Python
builders. Regeneration must be followed by content validation and image staging;
never deploy a regenerated bank with an out-of-date image manifest. The original
and independent review records are in `docs/ib-physics-reviews/`. Constructed
datasets are explicitly described as constructed or simulated. No copyrighted
exam PDF or reference-bank graphics are bundled.

## Diagrams and Cloudflare

The owned `thriving-scholars-media` R2 bucket serves diagrams at the existing
`https://media.thrivingscholars.com` domain. Each SVG has a full SHA-256 object key
under `ib/physics-hl/2026-10-30/`. A correction produces a new immutable image
address, avoiding stale cached figures. Only verified object hashes enter
`content/ib/physics-diagram-manifest.json`.

The server resolves each safe SVG to its verified CDN address. A client image
retains the embedded SVG as a fallback if the CDN fails. Only the owned HTTPS
origin is trusted by default; `IB_DIAGRAM_CDN_ORIGIN` may explicitly override it.
No auth credential is sent to the image host. Solution images and their addresses
are excluded from question projections. All question and mark-scheme routes
retain independently verified Supabase authentication.

To update diagrams, stage them with
`node --experimental-strip-types scripts/stage-ib-physics-diagrams.mjs`, then use
`scripts/upload-ib-physics-diagrams.mjs` with the staged directory and installed
Wrangler entry path. The uploader uses an existing Wrangler session, writes no
credentials, resumes verified content hashes, and checks every public response's
SHA-256 and SVG content type before writing the application manifest. Preserve
the current bucket/domain; this workflow does not enable a new public bucket.

## Verification

`npm run verify:ib-physics-question-bank` requires verified CDN coverage and checks
all 640 records, source-free numbering, scope codes, mark sums, unique prompts and
options, private-answer projection, full Markdown/KaTeX parsing and safe SVGs. The
command includes `--require-cdn` so a stale or missing image manifest blocks a build.
`node scripts/verify-ib-portal.mjs` exercises actual route/components with
synthetic users, including denied access, private answers, draft/unknown IDs,
separate tabs, filters, pagination and CDN fallback. `npm run build` includes the
Physics validation and pre-existing Maths/TMUA/ESAT/SAT/AMC regressions.

`scripts/render-ib-physics-review.mjs` renders actual components in a separate
local static review directory. It supplies synthetic fixtures only, is never
imported by the app, and introduces no deployed authentication bypass.
`scripts/render-ib-physics-diagrams.mjs` creates contact sheets for pixel review.
The review reports distinguish source/numerical review from rendered visual QA.

Independent agent review covered all 640 records. This does not constitute IB
approval, official examiner moderation, or a guarantee that no error can remain.
No automated check sends an email or writes student data. The existing signed-in
session is used for production UI checks; email delivery is not tested here.

## Primary syllabus sources

- Corrected guide linked by the official 2026 examiner instructions:
  https://xmltwo.ibo.org/publications/EAD/2026_EN/GR4/GR4-Physics_EN.pdf
- IB physics overview:
  https://www.ibo.org/programmes/diploma-programme/curriculum/sciences/physics/
- Detailed boundary/reference findings: `ib-physics-reviews/syllabus-blueprint.json`.

No unverified third-party data booklet is distributed. Students may use a clean,
current data booklet as permitted by the course.
