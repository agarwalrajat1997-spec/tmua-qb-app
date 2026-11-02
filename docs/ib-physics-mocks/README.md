# Physics SL and HL mock series

Six full mocks (three per level) are compiled from 282 distinct, already published,
independently authored Physics questions. They include 132 question diagrams.
Questions may be familiar from the topic bank; the catalogue says so. No past-paper
pages, screenshots or renumbered copyrighted questions are included.

## Assessment blueprint

The official [Physics guide, first assessment 2025](https://www.ibo.org/globalassets/new-structure/university-admission/pdfs/subject-guides/physics-guide.pdf),
printed pages 62–65, specifies:

| Level | Paper 1A | Paper 1B | Shared Paper 1 time | Paper 2 | Paper 2 time |
| --- | --- | --- | --- | --- | --- |
| SL | 25 MCQs / 25 marks | Data-based / 20 marks | 90 minutes | 55 marks | 90 minutes |
| HL | 40 MCQs / 40 marks | Data-based / 20 marks | 120 minutes | 90 marks | 150 minutes |

Each Paper 1A covers all 19 SL or 24 HL syllabus subtopics. Each Paper 2 includes
all five themes; HL papers contain additional HL questions. Paper 1A and 1B use
one uninterrupted deadline. Paper 2 is a separate sitting. No official grade or
IA-inclusive score is inferred.

## Recent paper availability checked on 2 November 2026

- [2025 archive](https://ibdocs.re/past-papers/2025): the May and November
  examination folders both list Physics SL/HL Paper 1A, 1B and 2, with mark schemes.
- [2026 archive](https://ibdocs.re/past-papers/2026): the visible “More Papers M26”
  folder lists HL Paper 1A, 1B and 2 for TZB and TZC. No SL Physics files or Physics
  mark schemes were listed in that folder. This is a partial archive, not evidence
  that 2026 SL papers do not exist.

The directory listings were used to establish availability. The mock content is
compiled from the portal's original bank against the official syllabus blueprint;
it is not a reproduction or a claimed analysis of the 2025/2026 paper contents.

## Student flow

`/ib?subject=physics-hl&view=mocks&course=sl` or `course=hl` → choose paper → timed
runner → immutable submitted answers → worked solutions and self-marking → saved
report → existing EmailJS student report template.

- Draft responses and flags are saved per account and paper in this browser.
  Refresh does not reset the deadline. An expired paper locks and submits.
- A failed submission retains the locked draft and offers a retry. The UUID makes
  retries idempotent. Solutions are returned only after the server saves the attempt.
- The new `ib_physics_mock_attempts` table is isolated from TMUA tables/predictors.
  Authenticated users can only read/insert their own rows and update their own
  self-marking fields. Submitted answers cannot be updated by the authenticated role.
- MCQs are scored from server-side canonical answers. Written marks must be whole
  numbers within every part's maximum. Reports explicitly identify them as
  self-assessed, not examiner or automatic marks.
- The same EmailJS public key, service `service_5l4w8x2` and template
  `template_j1jrs4o` are used. The report retains `name`, `test_title`, `to_email`,
  `session`, `score`, `timestamp`, `paper1`, `paper2` and `solution_link` fields.
  Only the signed-in student's email is used by this flow. Sending failures are
  visible and retryable; a successful SDK response means accepted for delivery.
- The report includes question-level results, topic totals, elapsed time and a
  link back to the private saved attempt. Mark schemes include original solution
  diagrams. Printing is available after marking.

## Verification

- `npm run verify:ib-physics-mocks`: catalogue, exact totals, SL/HL separation,
  numbering, uniqueness, automatic scoring, self-mark bounds, actual API handlers,
  authentication, owner filters, failed writes, immutable retries, report payload.
- `npm run verify:ib-physics-mocks-browser`: real React runner with an isolated API
  and intercepted EmailJS. Desktop/mobile, input, flags, refresh, failed submission,
  marking, mail failure/retry, no automatic resend after refresh and timer expiry.
  Screenshots in `screenshots/`. No live student emails are sent by these tests.
- Existing Physics content and IB portal checks pass. Existing TMUA overview and
  refresh checks pass. The full Next production build passes.
- Live database RLS assertions passed in a rolled-back transaction using synthetic
  users: own read/mark allowed, cross-account read/insert denied, answer update
  denied. All test users and rows were rolled back.

The unrelated existing TMUA overview `GET(request?: Request)` signature prevented
Next's generated route type check. Its parameter is now required, as Next expects;
the existing runtime logic is unchanged.

## Download preservation

The earlier Windows download script stores completed files immediately under
Desktop/IB_Past_Papers and uses `.part` for an in-progress file. Ctrl+C stops that
Windows process without deleting completed downloads. No Windows Desktop files
were accessible or verified from this workspace; no bulk downloader ran here.

## Rebuilding the selection

`python scripts/build-ib-physics-mocks.py` deterministically recreates the catalogue.
It reserves MCQs for later mocks and solves exact written-paper mark allocations.
Do not regenerate a released catalogue without a content-version/history migration:
saved attempts refer to the published IDs and canonical question content.
