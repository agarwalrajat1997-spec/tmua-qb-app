# Calculus I authoring and verification

Completed all 126 reference numbers, retaining their source difficulty (39 easy, 60 medium, 27 hard) and exact source total marks. The bank has 1202 total marks, 16 calculator-allowed questions and 110 no-calculator questions. There are 10 question diagrams and 8 marking-scheme diagrams. All 126 records are published; there are no unresolved drafts.

Each question is a separately authored variant of its corresponding reference, with changed meaningful numbers or context and recomputed dependent values. The mathematical method, approximate difficulty and principal part sequence are retained. No source branding, raw PDF images, video links or feedback features are included. Written marking schemes use M/A/R allocations whose sums equal the question and individual-part totals.

## Checks performed

- Rebuilt the entire JSON atomically from `calculus-1-build.py`; numbered coverage 1–126, unique stems and exact source total marks are asserted in the build.
- Every record has at least one actual symbolic or numerical check, in addition to reasoning through the scheme during authoring. The final audit checks explicit derivatives, implicit derivatives via −F_x/F_y, limits, prescribed points, parameter substitutions, rates or graph-defining data as appropriate. These checks establish the particular identities described in each record's verification notes; they are not an independent examiner certification of every possible solution method.
- Numeric roots were bracketed on the stated domains, substituted back into their equations, and extrema in the kinematics questions were compared with interval endpoints. Exact forms are preferred. Non-exact answers are displayed to three significant figures unless the problem asks for another accuracy.
- Source diagrams and broken fraction/root extraction were inspected in the original PDF where needed, including Questions 59, 87, 114, 115 and 120. Essential figures have been reconstructed as standalone SVG geometry.
- Ran the parent's `verify-ib-content.mjs` against `ib-authored` after the final rebuild. Calculus I has zero schema, per-part mark, Markdown, KaTeX or SVG-safety errors. Other collections' diagnostics are outside this file's scope. Derivative primes are superscripts throughout, and all Python control-character escapes in the content were removed at the raw-string source.

## Deliberate mathematical clarifications

| Reference | Clarification in variant |
|---|---|
| 54 | Seven source marks retained, with method steps for composition and the normal; no accuracy marks merely repeat the given derivative values. |
| 72 | The maximum-speed acceleration is written as exact zero, removing numerical root-finder noise. |
| 87 | The value at zero is defined by continuous extension and positive ordered parameters are stated, making the maximum-at-the-limit premise well-posed. |
| 91 | A positive periodic model is described as speed; wall-turn counting is explicitly part of the idealized model. The requested derivative is the rate of change of speed. |
| 92 | The circular limiting case is explicitly allowed, so the endpoint optimum is attainable. |
| 94 | The asymptote/root-distance claim excludes the removable-hole case a=3. |
| 107 | The gutter's physical orientation is stated so the designated free surface is horizontal and h is its water depth. |
| 118 | The normal point and actual horizontal-tangent points are independently substituted into the curve; the horizontal-tangent numerator and nonzero denominator are also checked. |
| 120 | The divided circular-segment tank is reconstructed with explicit dimensions, angle definitions and half-segment area, making the geometry unambiguous without the original image. |
| 122 | Marks for identifying a completed-cube form and its coefficients are not duplicated; the inverse-variable interchange earns a separate step. |
| 123 | Both numerical inflexion roots are checked for sign changes, and the exact tangent substitution polynomial is factored. |
| 126 | All three nearest parallel-tangent points are checked against the curve, including exclusion of negative product candidates and derivative-denominator checks in the scheme. |

## Files

- `calculus-1.json`: final content asset, 126 records.
- `calculus-1-build.py`: reproducible authoring data, math checks and atomic checkpoint writer. Its SymPy/NumPy/SciPy dependencies were isolated under `/tmp/ib-c1-deps`, without changing app dependencies.
- `calculus-1-review.md`: this report.
