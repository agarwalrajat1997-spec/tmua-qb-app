# Chemistry SL and HL practice bank

The authenticated IB portal now has one canonical Chemistry bank with two course
views. SL shows 407 shared syllabus questions. HL shows those same records plus
193 additional HL questions, for 600 in total. Shared questions retain the same
IDs, diagrams and mark schemes when students change course.

- SL: `/ib?subject=chemistry&view=questions&course=sl`
- HL: `/ib?subject=chemistry&view=questions&course=hl`

| Collection | Shared SL | Additional HL | HL view |
| --- | ---: | ---: | ---: |
| Structure 1: Models of the particulate nature of matter | 104 | 16 | 120 |
| Structure 2: Models of bonding and structure | 68 | 28 | 96 |
| Structure 3: Classification of matter | 36 | 36 | 72 |
| Reactivity 1: What drives chemical reactions? | 60 | 36 | 96 |
| Reactivity 2: How much, how fast and how far? | 64 | 32 | 96 |
| Reactivity 3: What are the mechanisms of chemical change? | 75 | 45 | 120 |

All 22 numbered subtopics have content. All 21 shared SL subtopics have shared
questions; R1.4 is entirely HL. Difficulty and qualification are separate: a hard
SL question remains SL content. The boundary follows the corrected guide for
first assessment 2025, updated March 2024 and verified through official examiner
instructions. The detailed mapping and exclusions are in
`ib-chemistry-reviews/syllabus-blueprint.json`.

## Student experience

A prominent SL/HL selector appears on the overview, collection, question, scheme
and Chemistry sign-in views. Course selection survives navigation, filters,
pagination and sign-in return links. An HL-only question or scheme is unavailable
in SL mode, after the normal authentication check. Switching an HL-only detail
page to SL leads to its corresponding SL collection.

Questions have accessible coloured difficulty bars, SL-content/Additional-HL
tags, question type, calculator label and mark total. Calculators are permitted
throughout the current Chemistry assessment structure. Written mark schemes open
in separate tabs; no video or AI-feedback action is included. Multiple-choice
questions award one mark with an explanatory scheme. Structured and data-based
parts have individual mark allocations and worked reasoning. These are original
IB-style practice schemes, not official IB examiner moderation.

There are 154 multiple-choice, 329 structured and 117 data-based questions, worth
1,981 marks. Difficulty estimates comprise 104 easy, 315 medium and 181 hard
questions. Constructed or simulated datasets are identified as such. Needed
constants and chemical data are supplied within questions. No third-party exam
paper or question-bank illustration is bundled.

## Diagrams and verification

There are 99 distinct original SVGs in 75 question placements and 35 solution
placements. All 110 diagram uses received visual review. Chemistry-specific
review includes atom and charge conservation, bonds and lone pairs, curly-arrow
origins and destinations, stereochemistry, polymer repeat units and spectra.
Content hashes connect reviewed SVGs to verified Cloudflare responses at the
existing `https://media.thrivingscholars.com` domain. A corrected figure receives
a new immutable address under `ib/chemistry/2026-10-30/`. The safe inline SVG is
retained as an image fallback; solution figures are excluded from question views.

`npm run verify:ib-chemistry-question-bank` checks the schema, all course/subtopic
coverage, mark totals, distinct question inputs (including diagrams), unique MCQ
options, answer isolation, safe SVGs and all 2,187 mathematical expressions.
Its `--require-cdn` gate prevents a build with a missing or stale image manifest.
`node scripts/verify-ib-portal.mjs` includes course-aware route/component checks
with isolated fixtures and existing Maths/Physics regressions.

All 600 records were independently reviewed. The reproducible review scripts in
`scripts/ib-chemistry-review/` log 486 independent numerical comparisons, at least
95 explicitly counted equation-balance checks, additional Structure formula and
bond inventories, full-record hashes and complete diagram coverage. Reports in
`ib-chemistry-reviews/` distinguish author checks, independent scientific review
and rendered visual inspection. Numerical checks use the displayed data, including
the corrections to prematurely rounded supplied values and exact rounding ties.

The static review helper creates local HTML from actual components with synthetic
users; it launches no browser, adds no deployed route and grants no auth bypass.
Browser review is performed separately. No automated test sends email or modifies
student records. Existing Maths (962) and Physics (640) content records are intact.

## Maintenance

Deterministic stdlib Python builders are in `scripts/ib-chemistry-authoring/`.
After regeneration, rerun the affected independent reviews and the content gate.
Stage diagrams with `scripts/stage-ib-chemistry-diagrams.mjs`, render contact sheets
with `scripts/render-ib-chemistry-diagrams.mjs`, and upload through
`scripts/upload-ib-chemistry-diagrams.mjs` using the existing Wrangler connection.
The uploader checks the public response hash and SVG content type, resumes
verified hashes, and writes no credentials to the repository.

Primary guide: https://xmltwo.ibo.org/publications/EAD/2026_EN/GR4/GR4-Chemistry_EN.pdf

Official overview: https://www.ibo.org/programmes/diploma-programme/curriculum/sciences/chemistry/
