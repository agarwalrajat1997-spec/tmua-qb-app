# IB Maths AA HL release checks

Scope: 962 source-mapped questions across six collections, with written marking schemes, difficulty and calculator labels. Physics and mocks remain empty. No emails or student-data writes were performed during verification.

## Content checks

- All 962 records are published, with contiguous reference numbers and no exact duplicate prompts.
- Every part and question total equals its marking allocations.
- The real Markdown/KaTeX parser renders all 13,868 mathematical expressions; 122 embedded SVGs pass the non-interactive asset validator.
- Control characters and unexpected newlines inside inline mathematics are rejected, including accidental Python string escapes.
- The author reviews describe their mathematical checks. Independent cross-review reports record actual sampled coverage and corrections; they do not claim external IB examiner certification.
- Final root checks also covered the supplied screenshot examples (Number & Algebra 2 and 5), sampled hard questions across all collections, exact boundary sums in NA56, C1 Q31’s nonzero increment notation and C1 Q53’s formerly clipped endpoint label.

## Application checks

- Actual server components render with synthetic fixtures; no answers or private source/review metadata reach question HTML.
- All question and scheme routes require a verified user. Draft and unknown IDs are withheld. Filters, pagination bounds and empty results are checked.
- Scheme links use a separate tab with noopener/noreferrer. No video or AI-feedback actions are present.
- Existing magic-link callbacks preserve nested IB routes and filters, including expired-link retries. These are synthetic provider tests, not an email-delivery test.
- Desktop and 390px mobile visual reviews use the actual React components and CSS in a separate static harness. The harness is never deployed or imported by the app, and supplies no authentication bypass.
- The full npm build and the existing TMUA/ESAT regression suite passed. The final diagram-label adjustment was followed by a fresh IB validation, production compilation and browser-key exposure check.

Source reconstruction notes are recorded in the six author reports. Original PDFs and extracted source question text are not included in the repository. The offline builders use only non-text reference metadata plus the newly authored content.
