# Functions content review

Completed 129 individually authored, one-to-one Functions variants, numbered 1–129. All are published in the content file; no unresolved drafts. Each preserves its source question number, difficulty, calculator label and total marks. There are 16 question diagrams and 29 solution diagrams, all freshly generated SVGs.

## Validation performed

- Recalculated the displayed answers, domains, branches, transformations and intersection counts while authoring every solution.
- Executed 42 symbolic/numerical assertions spanning 34 questions using SymPy and scipy. These include polynomial expansions, rational inverse composition, quartic stationary points, numerical equation roots, and an independent normal-tail/erfc check of Question 129.
- Confirmed 129 unique IDs and complete source-number coverage. Difficulty, calculator permission and maximum mark totals match all 129 source entries.
- The application’s real Markdown/remark-math/KaTeX content validator reports no errors for any Functions ID. It also validates per-part and total mark sums and SVG safety. Other collections’ unrelated errors in its aggregate run do not affect this collection.
- Parsed all 45 SVG documents as XML. Mathematical plot paths come directly from the stated functions; qualitative Question 122 uses a labelled monotonic sketch. Standalone raster inspection was unavailable because the local SVG rasterizer dependencies were absent; the parent’s application render review remains the visual integration check.
- Five-significant-figure output for Question 34 retains trailing zeros (0.84800). Rounded numerical coordinates and boundaries use appropriate precision, with guard digits retained in computations.

## Source reconstruction and normalization

| Question | Treatment |
|---|---|
| 30 | Printed reference omitted the rational graph and final instruction. Reconstructed a labelled asymptote/intercept graph for its three-parameter rational-function skill, retaining 4 marks. |
| 39 | Printed reference omitted the quadratic graph/task parts. Reconstructed a coefficient/vertex question from the stated quadratic form, retaining 6 marks. |
| 70 | Printed reference lost parts after the stadium-track introduction. Reconstructed a perimeter, physical-domain and inverse-model sequence, retaining 7 marks. |
| 93 | Source header states 17 marks while visible parts sum to 16. The variant sketch has 6 marks, so the complete scheme totals the stated 17. |
| 107 | Printed reference omitted the cubic graph and final tasks. Reconstructed labelled roots and a y-intercept to determine four coefficients, retaining 7 marks. |
| 127 | Specified that the positive inverse-domain interval must contain x = 0.5, removing an ambiguity between separate monotonic branches. |

The reconstruction notes also remain attached to the relevant questions’ verification metadata. This is a mathematical authoring and code-validation review, not a claim of external IB examiner approval. The source diagrams and source worked solutions are not copied into the app assets.

## Files

- `functions.json`: final application data.
- `functions-build.py`: reproducible builder and mathematical assertions; writes checkpoints atomically.
- `functions-review.md`: this review.
