# Psychology question bank — first assessment 2027

This release contains **240 unique original medium/hard questions**: 180 shared questions displayed in both SL and HL, plus 60 additional-HL questions. SL displays 180; HL displays 240. The seven collections are biological approach (40), cognitive approach (40), sociocultural approach (40), research methodology (60), culture (20), motivation (20) and technology (20). **126 question records include illustrations, using 79 distinct SVG assets.** Repeated assets within a related stimulus pack are explicitly recorded.

The scope follows the [official 2027 guide](https://ibo.org/globalassets/new-structure/university-admission/pdfs/subject-guides/psychology-first-assessment-2027-guide-sbs.pdf), [subject brief](https://ibo.org/globalassets/new-structure/programmes/dp/pdfs/dp_psychology_subjectbrief_en.pdf), [2027 examiner instructions](https://ibpublishing.ibo.org/exinst/apps/exinst/index.html?chapter=9&doc=EX_instructions_2027_e&part=10) and [IB curriculum update](https://www.ibo.org/university-admission/latest-curriculum-updates/psychology-updates/). Paper 1 and Paper 2 are each 90 minutes/35 marks; HL Paper 3 is 105 minutes/30 marks. This is a practice bank, with individual items rather than assembled timed sittings. The legacy course ending in 2026 has a different assessment structure.

`specification.json`, `topic-taxonomy.json` and `research.md` retain scope, primary-source URLs and access caveats. The public guide is dated February 2025; the examiner instructions name a later update but their guide link resolves to the legacy document. No inaccessible updated guide or public official specimen pack is claimed as reviewed. BIO/COG/SOC/RES/CUL/MOT/TEC codes are internal navigation codes.

## Question and marking conventions

| Style | Marks | Availability |
|---|---:|---|
| Paper 1A: content and explanatory example | 4 | SL + HL |
| Paper 1B: application to a supplied scenario | 6 | SL + HL |
| Paper 1C: conceptual argument in context | 15 | SL + HL |
| Paper 2A: methodological knowledge | 4 | SL + HL |
| Paper 2A: concept application | 4 | SL + HL |
| Paper 2A: methodological comparison | 6 | SL + HL |
| Paper 2A: research design | 6 | SL + HL |
| Paper 2B: unseen-study evaluation | 15 | SL + HL |
| Paper 3: graphical limitation | 3 | HL |
| Paper 3: findings and conclusion | 6 | HL |
| Paper 3: qualitative research evaluation | 6 | HL |
| Paper 3: three-source claim synthesis | 15 | HL |

Worked answers are indicative arguments, assessed through holistic best-fit bands. `IND` paragraphs are not additive one-mark points, and alternative justified responses can receive full credit. The bands are 0/1/2/3 for three marks; 0/1–2/3–4 for four; 0/1–2/3–4/5–6 for six; and 0/1–3/4–6/7–9/10–12/13–15 for fifteen. Descriptors are original wording. Medium/hard classifications are editorial, without claimed examiner difficulty calibration. `calculator: false` means no calculator is needed for the practice item; it does not assert an official examination prohibition.

## Provenance and review

Questions, scenarios and diagrams are original. Scientific mechanisms were checked against legitimate primary publications, including [Logothetis et al. on the fMRI signal](https://www.nature.com/articles/35084005) and [Tversky and Kahneman on judgement heuristics](https://pubmed.ncbi.nlm.nih.gov/17835457/); question-level author evidence retains the relevant references. No PirateIB questions or leaked Revision Village mirror material were copied.

Constructed studies, numerical results and interview quotations are explicitly labelled simulated. They are not attributed to real participants or published studies. Paper 2A items supply fictional practical records as self-contained methodology practice; an actual examination requires the student's own class-practical experience. Shared-level graphics support concepts or methodology; direct statistical/graphical interpretation is confined to HL. Supplied confidence intervals are checked and interpreted without claiming re-estimation from unavailable raw observations.

Separate AI reviewers read every complete prompt, worked answer and rubric, checked mechanisms, alternative interpretations and assessment scope, and inspected all distinct figures at native and 360-pixel widths. Numerical checks cover supplied contrasts, scales and plotted coordinates where applicable. This is computational and independent AI review, without human IB examiner moderation or IB endorsement. Final per-question coverage is recorded in:

- `approaches-independent.json` — BIO/COG, reviewer `mock_pdf_inventory`.
- `social-extensions-independent.json` — SOC/CUL/MOT, reviewer `root`.
- `methods-technology-independent.json` — RES/TEC, reviewer `mock_exam_spec`.

RES049–060 were authored by `mock_portal_audit`; the methods author ledger records this coauthorship. Author checks remain separate from independent approval. `native-diagram-index.json` binds each illustrated question to SVG and inspected PNG hashes; `cdn-checks.json` records successful public-byte verification for all 79 assets.

## Reproduction and release control

From the repository root, the author entry points are `scripts/ib-psychology-authoring/approaches.py`, `social_extensions.py`, `methods.py` and `technology.py`. `methods.py` incorporates `methods_evaluation.py`; all use `common.py`. Run these only in an authoring/review workspace: they regenerate canonical drafts and author evidence. The verified diagram manifest lets the helper attach the corresponding public URLs.

The separate replay scripts are `independent_approaches.py`, `independent_social_extensions.py` and `independent_methods_technology.py` in the same directory. Reviewer-controlled semantic/image pins must match actually reviewed content. **Never regenerate pins or refresh approval hashes merely to make a changed question pass.** Changed wording, answers, figures or measurements require a fresh substantive review of the change and its consequences.

The media pipeline uses `stage-ib-psychology-diagrams.mjs`, `upload-ib-psychology-diagrams.mjs`, `attach-ib-psychology-diagram-urls.mjs` and `render-ib-psychology-diagrams.mjs --evidence`. Restage after canonical changes; final author and independent reports must bind the URL-enriched questions and final inspected images. `verify-ib-psychology-content.mjs --require-cdn`, `verify-ib-psychology-media.mjs` and `verify-ib-psychology-portal.mjs` check content, media and portal behaviour.

Once all reviews and media evidence pass, run `node scripts/verify-ib-psychology-review-mutations.mjs` in its isolated fixture, then explicitly run `node scripts/finalize-ib-psychology-reviews.mjs`. The proof requires all 31 ordered case identities, eight numerical unit cases and current guard/finalizer/tester/harness/media-helper hashes. Semantic mutations must fail `readReviewEvidence` before the frozen-byte check. The clearly labelled synthetic positive proof bootstraps only the disposable fixture; the real proof is written after actual checks pass. The finalizer verifies an existing manifest instead of silently replacing it. Do not delete a frozen manifest to bypass a failure.

`node scripts/verify-ib-psychology-reviews.mjs` is read-only and verifies the mutation proof and every protected byte against `content/ib/psychology-review-manifest.json`. The ordinary `npm run verify:ib-psychology` includes this guard. A later content change must fail verification until it completes a separate reviewed release process; verification never manufactures a new approval. Keep subsequent live deployment QA notes outside this frozen documentation directory, under `work/psychology-bank-2026/`.
