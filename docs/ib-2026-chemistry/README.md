# Chemistry expansion, November 2026

200 original hard structured/data-based questions, with full worked marking points. The shared SL/HL selection contains 80 questions; an additional 120 require HL content. These are 200 canonical questions, not repeated SL/HL copies.

The six themes receive 35, 35, 30, 30, 35 and 35 questions respectively (S1, S2, S3, R1, R2, R3). The existing 600 Chemistry questions remain frozen. New questions use numbers 701 onward in each theme.

## Sources and provenance

- [Official Chemistry guide, first assessment 2025](https://www.ibo.org/globalassets/new-structure/university-admission/pdfs/subject-guides/chemistry-guide.pdf): syllabus scope, SL/HL distinctions and assessment objectives.
- [Official Chemistry SL/HL specimen papers](https://www.ibo.org/globalassets/new-structure/programmes/dp/pdfs/chemistry-hl-sl-specimen-papers-1a-2b-2-en.pdf): question presentation, command terms, structured reasoning and data interpretation.
- The repository's existing corrected syllabus blueprint was cross-checked against the guide, including the distinction between shared statements and AHL extensions within a subtopic.

All questions, numerical datasets, apparatus sketches, spectra, molecular drawings and solutions in this expansion are newly authored. Spectra are labeled as constructed teaching data. None is represented as an official IB past-paper question. The instructional M/A/R marking labels belong to the portal and are not presented as official IB science mark codes.

## Verification

Each author derives and checks the solutions; a different reviewer then audits the final records. Reviews cover chemical scope, valence/connectivity, atom/charge/electron balance, physical/numerical roots, units, stereochemistry, spectrum assignments, significant figures, alternatives and part/mark totals as relevant. The independent evidence identifies each question and binds the reviewed JSON by SHA-256. Visual inspection covers the question and private solution figures. These are computational checks and separate AI reviews, not human examiner moderation.

`npm run verify:ib-2026-chemistry` checks the production schema, Markdown/formula rendering, exact syllabus titles, 80/120 level split, distinct identifiers/prompts, safe figures, private-answer exclusions and frozen review hashes. The portal integration checker also exercises all 200 detail/solution views, all 120 AHL access exclusions for SL, automatic filters, authentication and six independently lazy-loaded topic chunks.

The navigation index contains metadata only. A topic request loads its existing bank and that topic's 30–35 new questions, with the existing promise cache retained.
