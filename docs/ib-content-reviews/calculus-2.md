# Calculus II authoring and verification

Completed 147 individually mapped variants, Q1–147, from the supplied Calculus II PDF. The difficulty distribution remains 41 easy, 58 medium and 48 hard. Every question has a written marking scheme and an assigned calculator flag. No unresolved drafts remain in this collection.

## Actual checks performed

- The deterministic generator reconstructs every item and atomically checkpoints the JSON after each batch. It asserts each part’s M/A/R allocation, total marks, complete numbering and source difficulty.
- 75 explicit symbolic checks pass: antiderivative differentiation, initial-value substitution, residuals of differential equations, Maclaurin coefficients, a parameter-dependent differential equation, an improper integral, inverse-profile volume and a reduction-formula value.
- Numerical work uses SciPy root bracketing and quadrature, retaining guard digits until final answers. Kinematic distances split at velocity sign changes. Numerical areas use signed regions correctly. Euler sequences are calculated step by step; percentage errors use the explicitly requested rounded estimate where applicable.
- The complicated inverse-region Q70 was additionally checked over its two fixed points: approximately 1.9227674893 and 5.7724122178. Its derivative remains positive on that interval (minimum approximately 0.1508413), so the inverse and reflection-area argument are valid.
- The refined growth models in Q146 and Q147 satisfy their stated initial conditions and rate laws. Their whole-week/hour thresholds are checked by direct integer scanning.
- The parent Markdown/KaTeX validator reports no Calculus II errors. Raw string handling and output normalization prevent Python escapes and doubled LaTeX command backslashes. Scientific-notation values use KaTeX notation rather than programming-style `e+03`.
- Supplied diagrams are safe inline SVG. Axis ticks use sensible intervals; Q1 explicitly labels its two roots and vertex and shades region R. Other missing graphical information is reconstructed or fully specified in text. PDFs were inspected visually for formula ambiguities including Q79’s exponential and Q135’s radical.

## Deliberate corrections and clarifications

- Independent peer review clarified Q16’s requested maximum as the one with positive abscissa and added labels A/B to its diagram; it also restricted Q138’s initial population below half capacity so the fastest-growth state is attained in forward time.
- A final escape audit preserves LaTeX commands such as `\ne` while converting only standalone text newline escapes; this fixes the hidden newline issue in Q50, Q90, Q102 and Q105.

- Q31 retains the essential radical derivative and uses a recomputed numerical integral condition.
- Q37 has 12 marks instead of the source’s 15, avoiding redundant credit for elementary parts; its piecewise velocity is continuous and all distance calculations use the stated branches.
- Peer review also removed a zero-length interval created by rounding the endpoint pi in Q66 and corrected Q58’s percentage-error display to three significant figures. Root deduplication now retains full precision and clamps endpoint values.
- Q59 preserves its source total of five marks; the two integrations by parts receive distinct method and intermediate-result credits.
- Q85 calls the cotangent expansion a Laurent expansion rather than a Maclaurin expansion.
- Q101’s source has no extracted overall total; its seven allocated marks match its source parts.
- Q108 and Q112 specify complete finite solids and inverse profiles so no missing diagram is needed to infer a boundary.
- Q119’s excluded range follows the quadratic discriminant together with existence of at least one non-negative input root; it does not claim both roots are non-negative.
- Q124 explicitly excludes the additional stationary equal-gradient point in the part concerning non-stationary equal gradients.
- Q128 retains the square root in the integrating factor.
- Q130 states both horizontal asymptotes and distinguishes a concavity change across a discontinuity from an inflexion point.
- Q134 explicitly extends the algebraic solution across its excluded input before asking about negative-input stationary points.
- Q140 restricts its polynomial-degree claim to positive integer parameters.
- Q147’s refined model includes the integration constant required by the cosine term at time zero; this corrects the reference model’s initial-condition inconsistency.

This is a computationally checked authored bank, not a claim of external examiner review or official IB endorsement. Independent peer review is being coordinated by the parent integrator.
