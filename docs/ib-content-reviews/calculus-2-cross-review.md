# Independent Calculus II mathematical cross-review

Reviewed the final 147-question Calculus II collection read-only. Manually reviewed all question statements, domains and marking steps for Q100–147, plus representative earlier integrals, motion models, substitutions and graphs. No content files were modified by this reviewer. Findings were sent to the root agent and the latest JSON was subsequently inspected to confirm the corrections listed below.

## Corrected findings

| Question | Finding and evidence | Confirmed correction |
| --- | --- | --- |
| 16 | The nonlinear curve has local maxima at x≈−0.02309127 and x≈1.13155184, with a local minimum at zero. The original request for “the local maximum” was ambiguous. | Prompt now specifies B with x>0; updated diagram labels A/B. |
| 50,90,102,105 | Python `\ne` had become a literal newline followed by “e” inside mathematics. This changed the mathematical condition while passing the ordinary parser check. | Latest JSON contains actual LaTeX `\ne` in all four stems. |
| 58(c) | Rounded Euler estimate2.75 versus exact2.82529034 gives2.664871…% error, not a three-significant-figure2.7%. | Final answer2.66%. |
| 66(c) | A numerical endpoint artefact added a zero-length `(3.14,3.14)` “moving away” interval. On the last interval before π, displacement is negative and velocity positive. | Removed; correct intervals begin0,π/2,2 and end approximately0.863,1.86,2.61. |
| 119(e) | Discriminant analysis only needs at least one nonnegative input root; for example V=1 also has a negative quadratic root. | Scheme now explicitly says “at least one root d is non-negative” on the attainable ranges. |
| 138 | If N₀>L/2, a forward-time logistic trajectory cannot subsequently attain its globally maximal growth rate at N=L/2. | Initial restriction strengthened to0<N₀<L/2. |

## Independent numerical checks

SciPy/root finding/quadrature and direct recurrence calculations gave:

- Q14: first root1.303237249, stationary abscissae0.598093262 and1.598093262, signed integral1.814367301.
- Q16: total absolute area2.522656163; the two stationary maxima above were found from a dense sign-bracket search.
- Q31: nonconstant integral from3 to5 equals15.787070886, validating the recovered C=2.
- Q43: nonzero meeting time14.996741865, consistent with15.0 to3sf.
- Euler final approximations: Q1010.964285714; Q117−0.669851452; Q1196.982716189; Q12110.9 before requested2sf rounding; Q1271.572161800. All intermediate displayed sequences agree.
- Q112: emptying time14.161608709s and half-volume depth-decrease magnitude0.150692749cm/s.
- Q135: stationary x2.975086322, y−0.583011101; normal condition x2.019254258, y−1.092467554; volume3.234031699.
- Q146: first-model P(30)=9463.246763 and P(50)=14916.233816. Refined model P₂(13)=5714.489963, P₂(14)=6201.140257; the first qualifying integer week is14.
- Q147: M(18)=322.499009, M(40)=635.928135, M₂(40)=770.737766. First qualifying integer hour16, with M₂(15)=341.108788 and M₂(16)=375.658028.

## Independent symbolic checks

SymPy assertions passed for the exact ODE solutions in Q100, Q119 and Q133; Q106/Q122 Maclaurin coefficients through degree5; Q110's radical primitive; Q131's inverse-cosine differential identity; Q137's density normalization and11/16 probability; Q142's general-solution particular term; and Q145's fourth logarithmic moment `(11e³−8)/81`.

Manual checks additionally covered the substitution bounds/signs, maximal solution intervals, all hard-question derivative/reduction recurrences, density normalizations, omitted constant-ratio ODE solutions, symmetry arguments, geometric regions and mark-step conclusions.

## Diagram inspection

Rendered the actual authored SVGs for Q1,4,14,16,81 with Inkscape and inspected a contact sheet. The polynomial roots/vertex/shaded area, trapezoidal velocity graph, nonlinear signs/extrema, labelled A/B and cubic derivative lobes agree with their stated formulas and tested regions.

No unresolved mathematical blocker remains among the reviewed questions. This was an independent mathematical content review, not external examiner certification or exhaustive verification of every early question.
