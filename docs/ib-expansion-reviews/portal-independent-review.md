# Portal expansion independent code review

Status: passed. No actionable findings in the reviewed application changes. No application or frozen question-content changes were made by this review.

Reviewed on 31 October 2026: the current expansion diff in `app/ib-login/IBLoginClient.tsx`, `app/ib/IBPortalClient.tsx`, the question-bank/question/mark-scheme routes, course switches, question bodies, exam instructions, rubric rendering and related styles; and `lib/ib/{catalog,humanities-catalog,content,question,diagram-assets}.ts`. Existing authentication, login-destination, server-component harness and regression scripts were read where they determine the new behaviour.

## Findings

No P0–P3 findings remain. The review checked these concrete paths and boundaries:

- All nine subject/course IDs resolve, with four mathematics choices and six subject-navigation entries. AI HL topic links select its own collections. Physics retains its established subject/collection IDs and default HL links; explicit SL queries are retained.
- Question, bank and mark-scheme routes verify the signed-in user before retrieving/displaying questions. Content and asset lookup remain server-only, and student routes are dynamic. Login return destinations stay within the allowlist. The new subject/course links encode a complete `next` destination; an error/retry query leaves that destination intact unless the user explicitly changes subject or course.
- Course availability is applied in both list and single-record lookups. Physics SL requires `core`; Economics, Business, Chemistry and Biology SL require `sl`. AHL question and mark-scheme deep links return not-found under an explicit SL view. Summary counts use the same availability function.
- Bank filters use validated values, retain course/filter state during pagination, and reset pagination on form submission. Paper 3/AHL filters cannot make AHL content appear in an SL bank. Course-switch links clear incompatible level/syllabus values; an incompatible Paper 3 style is discarded by the SL route. Search uses learner-visible question data rather than solutions.
- `questionPrompt` uses an explicit runtime allowlist. Private marking steps, rubrics, solution diagrams, correct options, answer summaries, source and verification metadata are omitted. Server-only imports prevent question banks and the full diagram manifest from entering the client catalogue module.
- Levelled marking schemes use rubric maxima rather than adding indicative steps. Validation checks each part allocation, complete nonoverlapping bands from zero to the maximum, mutually exclusive band/criterion formats, unique criterion IDs and the sum of criterion maxima. `IND` steps have no displayed additive mark code. The Business 17-mark criteria render separately and the guidance explains best fit rather than an answer checklist.
- New diagrams use the same hash/byte/prefix validation and trusted HTTPS origin checks as existing diagrams. Images remain isolated from the page DOM, with a validated embedded fallback. Public question diagrams and private solution diagrams are selected through separate fields.

## Verification

Independently reran both focused checks successfully:

- `node scripts/verify-ib-expansion-portal.mjs`: isolated server-component rendering for course navigation, filtered counts, SL/AHL list and detail boundaries, protected deep links, private solution canaries, paper filters, rubric allocation rejection, and separate written mark-scheme tabs.
- `node --experimental-strip-types scripts/verify-login-routing.mjs`: accepted new deep links and rejected external, traversal and disallowed destinations.

No extra regression test was needed because no defect was found or code changed. The integrating agent's existing type-check, 70-page render and mobile checks were treated as supporting evidence, not repeated independent live-browser verification.

## Limits

This was source review plus local fixture rendering, not a live OTP/email/session exercise, penetration test, production-cache audit or CDN deployment check. The shared live browser was not used. The review does not certify the independently reviewed question content or external publishing state; those have separate author/reviewer and release reports.
