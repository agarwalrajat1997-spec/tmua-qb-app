# Mathematics AA mock release

This release contains ten 2025-series mocks: six AA HL papers and four AA SL papers, with 90 questions, 870 marks and 27 original diagrams. The combined PDFs contain 220 pages: 109 question-paper pages, ten solution covers and 101 retained worked-solution pages. Each PDF puts the question paper before its corrected solution book.

The supplied books contained solutions rather than complete original question stems. The questions are carefully reconstructed practice wording, with missing givens and assumptions made explicit and checked against the supplied answers. They are not claimed to reproduce the exact original wording. Confirmed source errors are corrected in the portal scheme and inline in the final PDF. Internal review records retain the source-page mapping. At the user's request, student PDFs carry Thriving Scholars branding and omit other credits, watermarks and file labels; this does not establish authorship of the supplied solution material.

HL Papers 1 and 2 allow 120 minutes and 110 marks each; HL Paper 3 allows **75 minutes** and 55 marks. SL Papers 1 and 2 allow 90 minutes and 80 marks each. Paper 1 prohibits calculators; the other papers require a graphic display calculator. The 75-minute HL Paper 3 timing follows the corrected [IB AA guide](https://xmltwo.ibo.org/publications/EAD/2026_EN/GR5/GR5-Maths_AA_EN.pdf).

Students submit written answers, then use the solution book to enter bounded marks for each part. The resulting total is labelled **self-assessed**; the portal does not automatically award an IB grade. Submission triggers an EmailJS report with marking pending. Saving the self-assessment triggers the scored report. Both use the same canonical PDF URL shown in the portal: `/ib-mock-solutions/<paper-id>.pdf`. These are public PDF assets, following the TMUA download pattern; attempt and review APIs require the owning signed-in account. Delivery depends on the configured EmailJS service and is verified separately from these content guards.

Verification comprises 392 author calculations and 641 independently recomputed checks, plus complete question, scheme, diagram and PDF layout reviews. It is computational and AI review, not moderation by human IB examiners. The independent reports bind all ten canonical JSON files by raw SHA-256 and cover all 90 unique questions. The three final PDF reviews bind the exact final PDF bytes. Database and portal checks are recorded separately.

## Finalization order

1. Finish the questions, schemes, diagrams, catalogue, portal implementation and database verification. Run the author and independent checkers in `scripts/ib-aa-mocks-2026/`; preserve canonical JSON as UTF-8 with LF line endings.
2. Build and render the combined PDFs, inspect every new question page and corrected solution page, and finish the three PDF review reports. A rebuild requires fresh hash binding and any affected visual rechecks.
3. Finish all release evidence under this directory, including `database-checks.json`. All independent and PDF reviews must pass, with no unresolved findings. The finalizer validates these reports against actual canonical files and PDF bytes before changing the PDF summary labels to `passed`.
4. Freeze the release only after all protected files are final:

   ```sh
   node scripts/finalize-ib-aa-mock-reviews.mjs
   npm run verify:ib-aa-mocks
   ```

`content/ib/aa-mocks-2026/review-manifest.json` records raw hashes for the papers, PDFs, catalogue, JSON evidence, this document and the author, reviewer, PDF-building and verification scripts. The normal `verify:ib-aa-mocks` command runs the existing functional checks followed by the read-only review guard. It never regenerates or approves evidence. Changing a protected file fails the guard until the affected reviews are renewed and the release is deliberately finalized again. Finalization does not replace the portal, database, production-build or live email checks.
