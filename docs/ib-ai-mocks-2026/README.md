# Mathematics AI HL challenge mocks

Ten original Thriving Scholars timed papers are available at
`/ib?subject=math-ai-hl&view=mocks`. These extend the existing AA attempt flow.
They are intended to stretch students beyond typical exam difficulty while
remaining within the current AI HL specification. Difficulty has not been
empirically calibrated against an examination cohort.

| Set | Papers | Minutes | Marks | Questions |
| --- | --- | --- | --- | --- |
| A | 1, 2, 3 | 120, 120, 75 | 110, 110, 55 | 16, 6, 2 |
| B | 1, 2, 3 | 120, 120, 75 | 110, 110, 55 | 16, 6, 2 |
| C | 1, 2 | 120, 120 | 110, 110 | 16, 6 |
| D | 1, 2 | 120, 120 | 110, 110 | 16, 6 |

The collection contains 92 distinct questions, 990 marks and 41 original
scientific SVG figures. All papers require a graphic display calculator. AI
papers have compulsory questions without an AA-style Section A/B division.
Every public combined PDF contains the question paper followed by its complete
worked solution book, with part-specific method, accuracy and reasoning marks.

## Specification and reference use

The controlling source is the [current official AI guide](https://xmltwo.ibo.org/publications/EAD/2026_EN/GR5/GR5-Maths_AI_EN.pdf),
updated August 2025 and linked from the 2026 examiner instructions. The
[official specimen and markscheme pack](https://www.ibo.org/globalassets/new-structure/university-admission/pdfs/dp-mathematics-applications-and-interpretation-specimen-papers-en.pdf)
informs response style, part marks and sustained investigation. Its original
one-hour Paper 3 cover is superseded by the current guide's 75-minute format.
The future first-assessment-2029 reductions do not apply to this collection.

`specification.json` and `research.md` record the source access and exact
syllabus boundaries. Public Christos Nikolaidis and Revision Village examples,
and local reference PDFs, informed assessment conventions. The questions,
data, wording, investigations and diagrams in this collection were authored
afresh; no provider question was copied or turned into a numerical variant.
Reference-provider credits are not printed in the student PDFs.

## Mathematical and visual review

Separate reviewers re-solved every question and reviewed every part against the
full stem, marking points, units, domain, model assumptions and syllabus. Fresh
independent checks cover numerical answers, exact small matrices, network
optimisation, discrete test tails, confidence intervals, global extrema,
regression fits, differential models and qualitative reasoning. The reports
bind the precise canonical paper hashes; computational evidence is distinct
from author derivations and from independent review.

All figures are regenerated from the frozen canonical SVGs. The asset ledger
binds paper, SVG and raster hashes, which the PDF builder checks before
embedding them. Math expressions are typeset through MathJax; the portal
verifier separately parses Markdown and checks all formulae with KaTeX. Final
PDF pages are rendered for inspection, with hash-bound visual review reports.
This is AI-assisted authoring, separate AI review and computation, not human
IB examiner moderation.

The immutable release manifest and read-only review guard protect the reviewed
questions, graphics, PDFs and evidence against accidental changes. Existing AA
content and its frozen review manifest are preserved.

## Attempt and report behaviour

The shared runner supports a persistent deadline, device drafts, navigation,
flags and owner-scoped saved attempt history. Responses become immutable after
submission. Completion reports initially say marking is pending. The student
then self-assesses each written part against the marking points and saves a
bounded whole-number mark. A scored follow-up report identifies the score as
self-assessed; no official IB grade is calculated.

The existing EmailJS integration uses only the authenticated account's email
address. The submitted portal view, optional PDF iframe and completion/scored
emails use one canonical PDF URL helper. Service acceptance is reported
accurately; it does not prove recipient inbox delivery. The direct PDF link is
available when a browser cannot display the native PDF iframe.

The database migration only extends the allowed mock identifiers. It preserves
all AA records, ownership policies, field privileges, immutability and current
IB trial/access rules. `database-checks.json` records real rolled-back owner,
other-user, anonymous, identifier and duration tests.

## Rebuilding

Authoring scripts live in `scripts/ib-ai-mocks-2026`. They deliberately rewrite
author evidence and should not be run as routine production checks. Any
canonical change requires renewed independent review, figure generation, PDF
rendering and visual review before finalizing a new manifest.

PDF generation uses task-local Python dependencies (PyMuPDF 1.26.5,
ReportLab 5.1.0) and MathJax 3.2.2. Author calculations use NumPy 2.3.5
and SciPy 1.16.2, alongside the exact/symbolic tools specified in their scripts. Set
`IB_AI_MOCK_WORK`, `IB_AI_PDF_DEPS` and `IB_AI_MATHJAX_MODULES` to those local
dependency locations; production dependencies are unchanged. Run
`render_pdf_math.cjs`, `build_pdfs.py` and `render_pdf_review.py` in that order.
The PDF builder verifies the complete source/asset hash chain and produces
deterministic branded files.

Routine release checks use `verify-ib-ai-mocks.mjs` and
`verify-ib-ai-mock-reviews.mjs`, followed by the full production build and live
portal/API/PDF/report verification. Never finalize a review manifest merely to
silence a changed-content failure.
