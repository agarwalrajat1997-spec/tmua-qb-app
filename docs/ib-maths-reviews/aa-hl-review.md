# Mathematics AA HL enhancement and review

This collection targets the first-assessment-2021 course used through the 2028 examinations. It excludes the first-assessment-2029 revision. The official guide and specimen links, assessment structure, SL/AHL code ranges and key exclusions are recorded in `syllabus-blueprint.json`.

## Delivered content

| Collection | Retained reference mappings | Original additions | Final count |
|---|---:|---:|---:|
| Number and algebra | 229 | 20 | 249 |
| Functions | 129 | 20 | 149 |
| Geometry and trigonometry | 182 | 20 | 202 |
| Statistics and probability | 149 | 20 | 169 |
| Calculus I | 126 | 20 | 146 |
| Calculus II | 147 | 20 | 167 |
| Total | 962 | 120 | 1082 |

Every existing ID, collection number and legacy source mapping is retained. Additions use the source label **Independent syllabus-authored practice**. Their 60 families have two parameter variants each. There are analytic Paper 1 demands, technology-supported Paper 2 demands and 24 compact problem-solving investigations in the style of Paper 3. These are individual practice questions, not complete timed examination papers. Each new marking step is a separate M1, A1 or R1 award. A given target result earns no accuracy mark merely for being copied.

All records now have a primary official syllabus code, an SL/AHL content level and an assessment style. Level describes the content demand within the HL course. It does not label the entire HL course as SL. Some questions integrate several topics; the single primary code does not enumerate every prerequisite.

## Mathematical and marking corrections

The deterministic correction builder records eleven specific legacy corrections in `aa-hl-corrections.json`:

- **NA133:** replaced indistinguishable-object permutations, which the guide excludes, with all-distinct volunteers assigned to labelled booths. The positional restrictions remain meaningful; counts are 12×10! and 8×10!.
- **C1-074:** replaced an examination-excluded continuity/differentiability test with the equivalent point and tangent conditions for the same quadratic coefficients.
- **C1-093:** removed repeated derivative awards and double credit for equivalent tangent equations. The question now has 12 distinct marks, split 3+3+6.
- **GT158 and GT168:** removed duplicate accuracy awards for equivalent expressions of the same distance.
- **C2-143:** condensed the induction and series allocation from 21 to 14 marks, split 3+6+5, without awarding repeated derivative data again.
- **C2-129:** explicitly defined a finite integral followed by a limit, so the task uses examined integration-by-parts and limit techniques without relying on unfamiliar improper-integral notation.
- **SP148 and SP149:** changed numerical variants to remove mathematical duplication with FN129 and NA227. SP148 now uses root product 9 and the threshold 13/4. SP149 uses success probability 1/3, coefficient denominator 486, modes 9 and 10, and least threshold sample size 11.
- **C1-022 and C1-120:** moved clipped graph labels and rebuilt the circular-tank cross-section from Python trigonometric coordinates. The tank top is the chord at maximum angle 3π/4; sample water edges represent β=2π/3 and α=π/3. The volume and related-rate calculations agree with that geometry.

All 120 additions were checked against their displayed parameter values. The author's numerical and symbolic checks are in the six `aa-hl-<collection>.py` builders, with individual evidence in the six additions ledgers. Root review identified and resolved exact-versus-decimal partial-fraction answers, undefined parameter names, inverse-branch wording, principal-argument wrapping and three-significant-figure formatting. Derivative notation and formula prompts were also normalized.

## Verification evidence and its limits

`aa-hl-replay-legacy.py` re-executed all six original author builders in memory with their output writers disabled. It reconstructed all 962 legacy questions and passed 7,175 assertions. That figure includes mark totals and text checks as well as mathematical assertions; it must not be presented as 7,175 independent mathematical proofs. The six replay reports separate the original source lines and explicitly identified per-question check numbers.

`aa-hl-high-risk-legacy-check.py` adds fresh calculations for 24 specifically inspected legacy questions, four in each collection. It independently checks cash-flow timing, exceptional plane systems, inverse branches, quartic extrema, vector projections, probability densities, conditional root thresholds, waiting-time modes, implicit-curve branches, ODE initial conditions and non-monotonic population thresholds. Its report gives the actual reasoning and computation for each named record. Earlier collection cross-reviews remain in `docs/ib-content-reviews/` and are additional evidence, with their original stated sampling coverage.

The complete runtime content validator passed on the frozen 1082-question set: every part total, 15,121 rendered formulae, 132 safe SVGs, numbering, official-code ranges, published schema, duplicate prompt checks and private-solution separation. These structural and rendering checks do not establish the correctness of every displayed proof or the pedagogical merit of every legacy mark allocation.

The present work is therefore **not a claim that all 962 legacy solutions received a new independent step-by-step semantic re-review**. It combines retained author assertions, the previous cross-reviews, fresh high-risk checks and the explicit corrections above. There is no external IB examiner certification. This distinction is preserved in the per-record ledger.

## Reproduction and frozen records

Use Python with SymPy, SciPy and NumPy available. The temporary dependency directories in this working copy are not runtime application dependencies.

1. Run the original six builders in `scripts/ib-authoring/` only when intentionally reconstructing the legacy baseline.
2. Run the six collection-specific `scripts/ib-maths-authoring/aa-hl-*.py` addition builders. Each replaces only its own twenty-item suffix and retains the current legacy prefix.
3. Run `aa-hl-finalize.py` to reapply the legacy corrections and metadata. It is idempotent.
4. Run `aa-hl-high-risk-legacy-check.py`, the independent additions checker, and the root maths content validator.

`aa-hl-hashes.json` binds the six frozen content files using UTF-8 with line endings normalized to LF, so Windows checkout conversion does not change the binding. `aa-hl-record-review-ledger.json` contains one record hash per question. SVGs contain explicit calculated paths and labels; no style blocks, use/image elements, external references or URL-based assets are embedded in the authored SVG source.
