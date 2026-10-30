# Statistics & Probability content review

149 authored variants map one-to-one to source questions 1–149. All retain their source difficulty and total mark allocation. All have complete question text, calculator classification, worked marking steps and published status. No unresolved drafts or missing source questions remain.

## Checks completed

- Ran `python -W error ib-authored/statistics-probability-build.py`. All 149 source mappings, total marks, per-part marks and mark-code sums passed. The builder writes JSON through atomic replacement.
- Ran the parent `scripts/verify-ib-content.mjs` against the authored-content directory. Zero `ib-aa-sp` findings: Markdown/math parsing, control characters and SVG safety checks passed. Errors belonging to other collections were excluded from this topic's result.
- Normal/binomial probabilities, inverse-normal quantiles, numerical roots, least-squares regressions and Pearson correlations are calculated directly with SciPy/NumPy in the builder, using unrounded values for subsequent calculations.
- SymPy assertions independently verify normalization and exact moments for Q94, Q125, Q130, Q133, Q138, Q143 and Q145. Quadrature checks the unknown endpoint density in Q127. Exact algebra checks Q138's admissible quadratic root.
- Enumerated all six-card permutations for Q144 (265 derangements); all three-draw outcomes for Q146/Q147; the discrete first-winning-card distributions; the negative-binomial mass function and both modes in Q149; and the consecutive binomial probabilities at its integer threshold.
- Checked the explicit discrete probability vectors for normalization/nonnegativity. Conditional probability denominators and parameters in the numerical models are valid.
- Final calculator outputs default to three significant figures. Specified four-/two-significant-figure, one-/two-decimal-place, monetary and nearest-integer answers retain their stated precision; exact fractions remain exact. Guard digits remain in intermediate normal standardizations and strict integer thresholds.
- Parent independently checked the actual rendered first eight questions, and separately checked hard-question algebra in Q129, Q138, Q142 and Q149.

## Corrections and authoring decisions

- Figure/table-dependent source questions use newly authored tables or safe geometric SVGs. The supplied source PDF is not embedded and no source branding is reproduced.
- Q3's learner count is read from its stem-and-leaf plot; its lower-quartile follow-up is distinct from the median calculation. Q7/Q20 now ask symmetry-based probabilities instead of restating given values. Q55's median is read from its boxplot. Q70's boxplot follow-up assesses percentile interpretation rather than awarding the same median twice.
- Q61 uses mathematically admissible regression slopes (product 0.6) and an intersection compatible with its quartiles. The source's regression-slope product exceeded 1.
- Q85 asks for the smallest sample achieving an expected count *at least* the target, so an integer solution is well-defined.
- Sampling-with-replacement or independent population sampling is stated wherever a binomial model is used. Q128's long-lasting bulbs are independently selected; Q134 correctly conditions on fruits that passed the sorting check.
- Q118 explicitly states independence between different customers, without claiming that the two product preferences are independent.
- Calculator labels reflect the authored technique: elementary exact probability/algebra is generally no-calculator; inverse-normal, large binomial sums and fitted regressions permit technology.

These are authored practice variants with mathematically checked, IB-style marking conventions; no external examiner review is claimed.
