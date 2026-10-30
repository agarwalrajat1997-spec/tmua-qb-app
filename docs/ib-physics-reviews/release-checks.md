# Physics HL release checks — 30 October 2026

This release adds 640 independently authored Physics HL practice questions to the
existing authenticated IB portal. It covers all five themes and all 24 subtopics
of the course first assessed in 2025, using the corrected November 2024 guide.
The 962 Maths AA HL question records and their stable IDs are unchanged.

## Content and review coverage

| Theme | Questions | Independent numerical/concept comparisons |
| --- | ---: | ---: |
| A: Space, time and motion | 200 | 133 |
| B: The particulate nature of matter | 120 | 256 |
| C: Wave behaviour | 120 | 344 |
| D: Fields | 100 | 104 |
| E: Nuclear and quantum physics | 100 | 177 |

The five independent review scripts are retained in
`scripts/ib-physics-review/`; their reports identify reviewed question IDs and
physical assumptions. These checks complement the author calculations and
whole-record reading. They are not official examiner moderation.

There are 260 multiple-choice, 287 structured and 93 data-based questions,
worth 2,163 marks altogether. Difficulty labels comprise 187 easy, 301 medium
and 152 hard questions. They are reviewer estimates. All questions permit a
calculator, consistent with the current Physics assessment structure.

Rendered visual review covers every diagram reference. The three visual reports
record original sheets, observed issues, correction passes and final hashes.
Corrections include axis ticks, label collisions, force/vector proportions and
removal of question figures that supplied an answer requested in the text.
The final set contains 339 unique safe SVGs used in 264 question placements and
131 solution placements.

## Portal behaviour

- All five theme pages and 24 syllabus destinations have published content.
- Difficulty bars have both colour and accessible text labels.
- Syllabus, question type, Core/Additional HL, keyword and difficulty filters are
  shareable and survive sign-in; pagination preserves active filters.
- Written mark schemes open in a separate tab. Multiple-choice schemes award
  exactly one mark; structured parts have reconciled marking-point totals.
- Questions exclude the private answer, solution figures and review metadata.
- Each question and scheme route checks the user before rendering content.
- No video solution, AI-feedback action or new student-data write was added.

## Verification record

The full production build and existing Maths/TMUA/ESAT/SAT/AMC regression suite
passed before the final diagram-only review corrections. The portal component
checks passed after those corrections, including denied access, unknown/draft
IDs, mark-scheme links, all theme/subtopic destinations, filters, safe image
origins and image fallback. Desktop and 375-pixel mobile component views were
inspected without horizontal overflow or broken images.

Cloudflare objects are immutable content hashes under the existing owned
`media.thrivingscholars.com` domain. The upload workflow verifies the public
response's SHA-256 and SVG content type before adding its manifest entry. A
strict prebuild gate requires verified coverage for every current diagram, so
an obsolete manifest cannot silently ship after a correction.

After the final corrections, all five independent checkers passed again (1,014
comparisons). The final content gate passed for all 640 questions, 2,163 marks,
3,053 mathematical expressions and 395 diagram placements, with verified CDN
coverage required. All 339 current public images passed hash and content-type
verification. Final production compilation, TypeScript, public authentication
configuration checks and the scan of 32 generated browser files passed; no
Supabase server keys were exposed.

Live browser verification is the postdeployment gate, recorded in the release
handoff. No automated check sends email or modifies student records.
