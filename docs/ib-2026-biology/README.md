# Biology expansion, November 2026

200 original hard, multi-part Biology practice questions with worked marking points and 200 self-contained scientific SVG figures. Each theme adds 50 questions, numbered 701–750, while preserving the existing 640-question Biology bank.

| Theme | Questions | Shared SL/HL | Additional HL | SVGs |
| --- | ---: | ---: | ---: | ---: |
| A: Unity and diversity | 50 | 20 | 30 | 50 |
| B: Form and function | 50 | 20 | 30 | 50 |
| C: Interaction and interdependence | 50 | 20 | 30 | 50 |
| D: Continuity and change | 50 | 20 | 30 | 50 |
| Total | 200 | 80 | 120 | 200 |

The SL selection contains the 80 shared questions. HL includes those same records plus 120 questions requiring additional-HL understanding. Difficulty does not determine course eligibility; statement-level syllabus scope does. These are 200 canonical questions, without duplicate SL/HL copies.

## Provenance

Scope follows the [official Biology guide, first assessment 2025, updated March 2024](https://xmltwo.ibo.org/publications/EAD/2026_EN/GR4/GR4-Biology_EN.pdf), linked by the [IB examiner instructions](https://ibpublishing.ibo.org/exinst/apps/exinst/index.html?chapter=1&doc=EX_instructions_2027_e&part=11). The [official SL/HL specimen papers](https://www.ibo.org/globalassets/new-structure/programmes/dp/pdfs/biology-hl-sl-specimen-papers-1a-2b-2-en.pdf) inform command terms, structured reasoning and data interpretation.

All wording, numerical datasets, models, drawings and solutions are independently authored practice. Constructed evidence is labelled; figures are schematics or data visualizations and are not presented as real micrographs or published experiments. Named course organisms provide context without attributing invented measurements to genuine studies. The source label is `Independent syllabus-authored practice`. M/A/R are portal instructional labels, not official IB science mark codes.

## Review and release checks

Authors performed 550 executable checks across the four batches. Separate reviewers performed 632 additional executable evidence checks (162/147/158/165 across themes A/B/C/D). A different AI reviewer reads every question and full scheme, independently reconstructs calculations, checks biological assumptions and statement-level scope, examines distinct mark awards, and inspects the scientific figures. Per-question evidence and raw JSON SHA-256 bindings are stored in the author and independent review files. Four complete, passed independent reviews are required for finalization. These computational checks and separate AI reviews are not human IB examiner moderation; difficulty has not been calibrated against student performance.

Scoped checks from the repository root:

```text
npm run verify:ib-2026-biology
npm run verify:ib-content-index
npm run verify:ib-content-loading
node scripts/verify-ib-2026-biology-portal.mjs
node scripts/render-ib-2026-biology.mjs
```

The Biology prebuild gate validates schema, marks, syllabus titles, course counts, safe SVGs, private-answer exclusions and frozen reviews. The separate loading/route checks exercise all 200 identifiers, question and worked-solution views, all 120 AHL exclusions for SL, automatic filters, authentication and answer canaries. They use isolated server-component/authentication harnesses, not a live production browser or network-performance measurement. Rendering generates local review pages and contact sheets.

Navigation remains metadata-only. Each Biology topic loads its original bank and only that theme's 50 additions; concurrent requests share the existing validated promise cache. Integration checks preserve all 640 original records.

Author and independent Python tools use repository-relative paths and the standard library; Node tools use the repository's installed dependencies. Some Python tools regenerate content or review reports, so they are maintenance actions rather than substitutes for reviewing changed bytes. After changes, finish independent review, regenerate the index/derived chunks and content/portal reports, then finalize review hashes. Subsequent changes require the relevant checks and review again. This document records repository preparation and verification, not deployment success.
