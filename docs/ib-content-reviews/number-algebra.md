# Number & Algebra authoring review

Completed 229 numbered variants, with one-to-one source mapping to all questions in the supplied Number & Algebra PDF. All are published; no unresolved drafts remain. Original source difficulty, calculator flag and total marks are preserved. Each question has an explicit stem, all subparts, and a written marking scheme using method, accuracy and reasoning marks. Each part's awarded marks sum to its allocation.

## Mathematical verification

The reproducible Python builder uses exact SymPy algebra, ordinary numerical evaluation and SciPy root/distribution calculations. It now passes 73 explicit computational assertions, including exact binomial coefficients; polynomial and partial-fraction identities; complex-number substitutions; derivative identities at multiple orders; geometric/arithmetic sums; the loan equation residual; enumeration of all six-card derangements; enumeration of all permitted letter-position patterns; and the inverse-tangent telescoping sum for n=1…100. The final two assertions check all 229 mappings and every source mark/difficulty/calculator tag. Not every individual reasoning step has an independent machine proof.

The root's independent review checked representative early questions and the entire Q150–229 tail, plus selected complex-number/proof questions. Corrections from that review are incorporated: quarterly periods in Q71; three-significant-figure output in Q90/Q132; approximate signs for rounded Q141 sums; clean LaTeX in Q213; explicit exponential form and end behaviour in Q221/Q225. The root additionally verified Q1/Q20/Q40 and Q76/Q86/Q98. This is authored exam-style content, not an external examiner certification.

## Source reconstruction and domain corrections

- Q22: the reference print omits its subparts. Reconstructed smallest-model and total-height questions from the supplied geometric-scaling setup, with the same six-mark total.
- Q182: the print omits later subparts. Completed the parameter and infinite-solution-family continuation of its dependent-plane problem.
- Tables and geometric constructions are expressed explicitly in the revised stems, so no inaccessible source images are needed. Newly drawn Argand diagrams accompany Q35, Q90 and Q114; Q102 and Q222 have answer diagrams. All diagrams are independent SVG geometry without source branding or external assets.
- Q172 keeps both exponent solutions, including the lower-degree case; cancelling its factor would lose a valid solution.
- Q215 and Q224 explicitly define the argument convention for noninteger complex powers. Otherwise the original-style rational-power task would be branch-dependent.
- Q229 restricts the arctangent subtraction identity to positive arguments and uses nonnegative x in the following identity, ensuring the principal branch is valid.
- Q195's infinite-sum numerator is 192 for the revised initial values; its maximum is 96.

## Presentation and schema checks

The complete app content validator passes with zero issues after regeneration. It checks marking totals, matching subparts, source mappings, math delimiters/KaTeX parsing, control characters and safe SVG syntax. Currency is written as USD, AUD or GBP, or as a math text unit; no broad currency substitution is used. Monetary rounding and calculator-dependent numerical results are stated where needed.

Files: `number-algebra.json` is the importable content; `number-algebra-build.py` regenerates it atomically and reruns the computational assertions. Source documents are unchanged.
