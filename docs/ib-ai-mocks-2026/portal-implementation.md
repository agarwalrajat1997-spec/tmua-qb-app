# Mathematics AI HL mock portal

The ten original AI HL papers use the existing Mathematics mock runner and API. AA URLs, canonical content, PDFs, scientific reviews and frozen review manifest remain unchanged.

| Set | Paper 1 | Paper 2 | Paper 3 |
| --- | --- | --- | --- |
| A | 16 questions, 120 minutes, 110 marks | 6 questions, 120 minutes, 110 marks | 2 questions, 75 minutes, 55 marks |
| B | 16 questions, 120 minutes, 110 marks | 6 questions, 120 minutes, 110 marks | 2 questions, 75 minutes, 55 marks |
| C | 16 questions, 120 minutes, 110 marks | 6 questions, 120 minutes, 110 marks | — |
| D | 16 questions, 120 minutes, 110 marks | 6 questions, 120 minutes, 110 marks | — |

Every AI paper requires a graphic display calculator. AI questions have no Section A/B grouping. The catalogue totals 92 questions and 990 marks. The AI HL subject's Mock tests tab contains these ten papers; AA listings remain isolated.

## Content contract

Metadata lives in `content/ib/ai-mocks-2026/catalog.json`. Full papers live in `content/ib/ai-mocks-2026/papers/<id>.json`. IDs are `ai-hl-set-[a-d]-paper-[12]` plus `ai-hl-set-[ab]-paper-3`. The root fields are:

```json
{
  "id": "ai-hl-set-a-paper-1",
  "strand": "ai",
  "course": "hl",
  "set": "A",
  "paper": "1",
  "title": "Mathematics AI HL · Set A · Paper 1",
  "minutes": 120,
  "marks": 110,
  "calculator": true,
  "questions": []
}
```

The empty `questions` array above illustrates the root shape only; publication validation requires the catalogue's exact count. Each question has `number`, `section: ""`, `marks`, `stem`, `parts`, optional `diagramSvg` and `answerSummary`, and a `markScheme` with one marking group per part. Optional `syllabusRefs: string[]` and `cognitiveDemand: string` record the internal syllabus and reasoning audit. They are not displayed in the question runner. No fictional source-page field is needed for original questions.

Part labels are unique strings, including an empty label for an unparted question. Part marks sum to question marks; question marks sum to the paper maximum. Each marking step has an additive `M`, `A` or `R` code followed by a positive integer, and its group's mark weights sum exactly to its part maximum. Diagrams must pass the existing SVG safety check. The public paper prompt excludes answer summaries, marking schemes and raw SVG; a diagram is sent as a safe image data URL.

## Attempts, access and reports

The routes remain `/ib/maths-mocks/<id>` and `/api/ib/maths-mocks/<id>`. The page uses `requireIbUser`; both API methods authenticate and then check `getIbAccessState`. Expired or required access returns 403, and unavailable access checking returns 503. No inactive request can load a private paper or query an attempt.

Drafts use the existing account-and-paper storage key. A saved deadline continues across refreshes, responses lock at the deadline, and submission UUIDs make retries return the first immutable saved attempt. Database reads and updates filter on both owner and mock ID. Self-assessment is bounded by every part's maximum and can be saved once. These written marks are self-assessed, not automatic mathematical grading or an official IB grade prediction.

After a confirmed submission, the runner sends the existing EmailJS completion report with pending marks. Saving self-assessed marks sends the scored report. Completion and scored mail states remain separate and persist on the device for retry handling. Email-service acceptance is not proof of inbox delivery. Both reports and the submitted UI use the same combined public PDF at `/ib-mock-solutions/<id>.pdf`, containing the question paper first and worked solutions afterwards. No live emails are sent by the isolated verification suite.

## Database migration

The additive `ib_ai_hl_mock_attempt_ids` migration expands only `ib_maths_mock_attempts_mock_id_check`. All AA IDs remain allowed, and AI C/D Paper 3 and AI SL IDs remain disallowed. The existing elapsed-time constraint already limits HL Papers 1/2 to 7,200 seconds and Paper 3 to 4,500 seconds. No row, owner policy, privilege, index or immutability trigger is changed.

The reviewed migration was applied to the portal project as version `20261103035050`. The actual allowed IDs, elapsed bounds, ownership policies and immutable submissions were verified in a rolled-back transaction; no QA rows remain. See `database-checks.json` and the portable transaction in `scripts/ib-ai-mocks-2026/verify_database.sql` for the evidence. Fresh environments must apply this migration through their migration workflow before using AI attempts; a local migration file alone does not establish that it has been applied there.

## Verification

Run `node scripts/verify-ib-ai-mocks.mjs --infrastructure-only` while content is being authored. This exercises actual API handlers and the shared page guard with isolated persistence, including all ten IDs, every access state, owner isolation, AI/AA isolation, immutable retry behavior, calculator rules, timing, UI labels and report/PDF links. It performs no network, database or email writes.

Before release run `node scripts/verify-ib-ai-mocks.mjs` against all ten actual question JSONs and combined PDF assets. It also parses every mathematical expression in stems, parts and marking points with KaTeX. The full gate fails while any required publication asset is missing. Run the existing AA verification and its read-only frozen review guard to establish that AA publication assets were preserved. Independent mathematical and PDF visual review remain additional release requirements; this infrastructure check does not replace them.
