# Physics challenge mocks - 2026

This release replaces the normal offer of bank-compiled Physics mocks with five source-guided challenge sets: three HL sets and two SL sets. Each set has two separate timed sittings, giving six HL and four SL practice papers. Paper 1A and Paper 1B share one uninterrupted clock.

| Course | Paper | Time | Marks | Structure |
|---|---|---:|---:|---|
| HL | 1A + 1B | 120 minutes | 60 | 40 multiple-choice questions and two 10-mark investigations |
| HL | 2 | 150 minutes | 90 | Nine compulsory 10-mark structured questions |
| SL | 1A + 1B | 90 minutes | 45 | 25 multiple-choice questions and two 10-mark investigations |
| SL | 2 | 90 minutes | 50 | Six compulsory questions worth 8, 8, 8, 8, 9 and 9 marks |

All papers permit a calculator and a clean current Physics data booklet. The controlling current IB guide, its statement-level SL/HL boundaries and the corrected 50-mark SL Paper 2 total are recorded in `specification.json` and `research.md`.

The ten papers contain 219 questions, 218 written parts, 170 multiple-choice marking groups, 640 marks and 163 original scientific SVG diagrams. They are intended as demanding practice within the current specification. Difficulty has not been calibrated with a student cohort, and the review does not constitute independent human IB examiner moderation.

## Source and content boundary

Thirteen user-supplied 2025/2026-style PDF extracts, totalling 221 pages, guided selection of concepts, experimental structures and figures. The source inspection identified duplicated experiments, overlapping HL/SL questions and incomplete opening questions. The new questions use rewritten wording, changed data or scientific inferences, freshly calculated solutions and precise new diagrams. Internal page anchors and change notes preserve their lineage. These are source-guided adaptations and independently developed extensions, rather than a claim that the underlying physics question families have no antecedents.

No question is loaded from the portal Physics question bank in the new flow. The exact canonical stems also have zero exact matches to the old bank or to another new question. The supplied PDFs and raw OCR/text extractions remain outside the release; `source-provenance.json` records their fingerprints, page counts and selection anchors.

Each canonical paper JSON in `content/ib/physics-mocks-2026/papers` is the source for the authenticated website and its printable book. Prompt and review allowlists keep correct options, marking points and private author/source evidence out of the pre-submission question payload. Native diagram reviews, independent per-part scientific reviews and numerical checks are recorded separately from initial author evidence.

## Student flow

The course catalogue offers three HL sets and two SL sets. Each paper provides a timer, question navigation, flags and account-specific device drafts. A successful immutable server submission unlocks the worked solutions and the combined PDF, whose question paper precedes the worked solution book. Multiple-choice marks are automatic; written marks are bounded whole-number self-assessments. No official IB grade or internal-assessment prediction is calculated.

The existing EmailJS service sends a completion report after submission and a scored follow-up after written marks are saved. Both use the authenticated recipient, persisted student name and the same canonical combined-PDF URL as the portal. Delivery acceptance is distinct from independently observing an inbox receipt.

New attempts use `ib_physics_challenge_attempts`, with owner-row policies, restricted insert/update columns and immutable response/initial-mark triggers. The earlier Physics table is retained. An owner can reopen an existing legacy saved attempt through a read-only archive; the retired bank series does not offer new starts or submissions. Earlier SL Paper 2 history retains its original 55-mark interpretation, while the new series uses the corrected 50-mark format.

## Reproduction and verification

Author and independent calculation scripts are under `scripts/ib-physics-mocks-2026`. Original source files are required for authoring; normal builds use the reviewed canonical content and supplied evidence, and do not regenerate or approve questions automatically. The author scripts are not substitutes for independent review.

The PDF tools render mathematical expressions and scientific SVGs, verify source/SVG/raster hashes, assemble branded question-first books, and render every final page for inspection. The scientific asset report is bound into each build record; final PDF, content and visual-review hashes must agree. Native PNG inspection hashes refer to the actual inspected preview images and may differ from the higher-resolution PDF raster hashes.

`audit_content.mjs` checks the standalone schema, all mathematical expressions, actual Markdown table parsing, unique identities/stems, current mark totals and answer-key patterns. `verify-ib-physics-mocks.mjs` exercises the actual API/model/page boundaries with isolated fixtures, including access denial, owner isolation, immutable retries, scoring and report payloads. The browser acceptance script exercises the actual React flow without sending live mail. `verify_database.sql` records rolled-back checks using real authenticated/anonymous database roles; it leaves no test rows.

The explicit review finalizer may run only after every scientific and final-page review has passed. The resulting frozen manifest is verified read-only by normal builds. A later change must fail against the existing freeze; it requires a deliberately managed new review, rather than silently refreshing hashes. See `review-guard.md` for that contract. Existing Maths AA/AI and question-bank verification remains part of the production build.

Live deployment, canonical PDF byte checks, real account submission/history, responsive layout and EmailJS acceptance are recorded separately in the user-facing release checks after publishing. No unrelated student attempt is altered during that verification.
