# Independent Functions content review

The Calculus I author independently reviewed all Functions Questions 101–129, plus 43 earlier sampled questions listed below. No substantive mathematical errors were found. This review concerns the mathematical content assets; it is not external examiner certification or a complete independent verification of every Functions question.

## Reviewed question IDs

Full hard-question review: **ib-aa-fn-101 through ib-aa-fn-129**, inclusive (29 questions).

Earlier samples: **ib-aa-fn-001, ib-aa-fn-002, ib-aa-fn-006, ib-aa-fn-007, ib-aa-fn-018, ib-aa-fn-020, ib-aa-fn-021, ib-aa-fn-022, ib-aa-fn-025, ib-aa-fn-030, ib-aa-fn-032, ib-aa-fn-036, ib-aa-fn-037, ib-aa-fn-041, ib-aa-fn-043, ib-aa-fn-048, ib-aa-fn-049, ib-aa-fn-050, ib-aa-fn-051, ib-aa-fn-052, ib-aa-fn-056, ib-aa-fn-058, ib-aa-fn-059, ib-aa-fn-061, ib-aa-fn-064, ib-aa-fn-065, ib-aa-fn-067, ib-aa-fn-070, ib-aa-fn-071, ib-aa-fn-075, ib-aa-fn-077, ib-aa-fn-079, ib-aa-fn-080, ib-aa-fn-082, ib-aa-fn-083, ib-aa-fn-084, ib-aa-fn-085, ib-aa-fn-086, ib-aa-fn-089, ib-aa-fn-093, ib-aa-fn-097, ib-aa-fn-098, ib-aa-fn-100** (43 questions).

Total distinct reviewed questions: **72**. An earlier progress message called the earlier sample count 44; enumerating the actual reviewed IDs gives 43. No additional question is claimed to compensate for that counting error.

The earlier samples emphasized graph transformations, inverse domains/ranges, restricted-domain endpoints, rational asymptotes, removable-factor exclusions, physical domains and numerical inequalities. Graph-defining formulas and labelled coordinates were also inspected in `functions-build.py` for Questions 1, 6, 7, 25, 30, 37, 80, 100, 107, 113 and 122. This was a code/geometry consistency review, not a separate browser screenshot review.

## Independent symbolic coverage

A separate SymPy calculation, without changing the Functions content, passed **20 identity assertions** covering 19 distinct question numbers:

| Question | Independently checked identity or condition |
|---|---|
| 101 | Cubic expansion from roots 2, 5/2, 3. |
| 102 | Quintic expansion of (x+2)^3(x²−3x+5). |
| 103 | Conjugate-pair product (25+4)(4+9)=377. |
| 105 | Arithmetic-series sum at n=20 equals 1170. |
| 106 | The next proposed input 7π/6 gives composite output 6. |
| 107 | Cubic coefficients from roots −2, 1, 3 and leading coefficient 2. |
| 108 | The derived parameters m=n=6/5 satisfy the supplied quadratic value. |
| 110 | The proposed tangent gives a perfect-square intersection equation. |
| 111 | The quartic factorization is exact. |
| 117 | The quartic factorization is exact. |
| 119 | p(−1)=−36, giving the transformed polynomial's constant and root product. |
| 120 | f−f⁻¹ gives 7(x²−3x−2) after legitimate cross-multiplication. |
| 121 | The discriminant is 60k(2k−1). |
| 123 | The completed-square form 8(x−5/8)²−1/8 is exact. |
| 124 | 3(x+3)(x²+4) reproduces the coefficient assignment. |
| 125 | The rational denominator is (x+2)²−16. |
| 126 | The arithmetic-progression roots 4, 4±4i give x³−12x²+64x−128. |
| 127 | Both the quartic factorization and f(1/2)=5/4 were checked (two assertions). |
| 128 | The completed-cube form (x+3)³/3−2 is exact. |

## Independent numerical coverage

Stationary points were recomputed from the differentiated polynomials, with ordinates evaluated independently:

| Question | Computed stationary coordinates |
|---|---|
| 111 | (−1.574213799, −2.878898021), (0.070464553, 6.035382560), (2.253749246, −12.949453289) |
| 117 | (−2.192582404, −25), (0.5, 27.5625), (3.192582404, −25) |
| 127 | (−1.137257817, −1.109116566), (0.162914020, 1.581833561), (1.349343796, −0.526183792) |

Additional independent computations:

- Q83: a numerical scan and bracketing over 0.0001 ≤ x ≤ 50 found the positive crossing at **4.5636680225**, consistent with 4.56 in the scheme. Odd symmetry and sign checks support the stated negative interval. This finite scan is not presented as a formal global root-count proof.
- Q89: the inequality boundary is **0.7110942010**, consistent with 0.711.
- Q127: the inverse-composition inequality boundary is **0.6494759461**, consistent with 0.649; the upper endpoint remains included.
- Q129: the conditional normal probability is **0.2729507389**, consistent with 0.273.

The numeric outputs agree with the written marking schemes at their stated precision.

## Reasoning review

The non-symbolic review checked the stated algebra and logical restrictions in all 72 reviewed records. In particular:

- Q111 and Q127 use the maximal monotone interval containing the required input; inverse endpoints and inequality direction are consistent with that restriction.
- Q116 stops each sine restriction at its first turning point, including that endpoint.
- Q122 correctly counts two solutions at height zero, four below the central peak, three at the central peak, and two between that peak and the unattained asymptote; the answer is {0} ∪ (b²,25).
- Q125 chooses the inverse square-root branch compatible with x>2 and rejects the other composition solution.
- Q126 explicitly permits complex roots, making both the arithmetic- and geometric-progression arguments valid.
- Q129 accounts for the distinct-real-root conditioning and proves the smaller-root absolute-value threshold before taking the probability ratio.

## Follow-ups

No mathematical correction was required by this review. Two presentational/model-clarity notes were sent to the parent:

1. Bare derivative primes in several Functions records were typography, not mathematical errors. The Functions author has since normalized these in both emitter and JSON.
2. Q71's choice of an 8 m frame assumes the selected entire frame is used without cutting. The Functions author is clarifying this intended physical constraint.

The checks above were already completed before this report was saved; they were not repeated for the report.
