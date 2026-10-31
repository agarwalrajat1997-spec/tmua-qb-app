# AI HL author freeze

500 original practice questions are complete: 100 in each of the five course topics, with 25 distinct families per topic and four variants per family. All require a calculator. The bank targets the first-assessment-2021 course through its final 2028 assessment, not the revised 2029 course.

The bank includes 440 records with AHL primary scope and 188 investigations carrying 12–14 marks. These investigate modelling assumptions, uncertainty, interpretation, decisions and numerical methods alongside calculations.

The official guide and specimen were read for scope and assessment conventions. All wording, numerical data and figures were independently authored; no published question or markscheme was copied.

## Verification

- Structural, numbering, source, per-part mark-total, one-point criterion, calculator, unique-family and SVG-safety checks passed for all 500 records.
- 3572 formula occurrences rendered through KaTeX without errors.
- A separate numerical audit, which does not import the generator, checked all 500 records through 1420 ledger fields. Lists and vectors were checked componentwise. It uses direct probability sums, independent t/normal probability evaluations, iteration, residual equations, quadrature, normal-equation least squares and matrix exponentials.
- All 52 diagram uses (43 unique SVGs) were rasterized. Four contact sheets were visually inspected. Original diagram coordinates and networks are public; rotated solution coordinates are present only in private markscheme figures.
- Decimal ROUND_HALF_UP preserves three-significant-figure trailing zeros. Calculations retain unrounded working. All bank and author files use UTF-8 with LF endings.
- Scope rationale and unrounded results are recorded for every question in `ai-hl-author-ledger.json`. Exact bank and per-record hashes are in `ai-hl-author-freeze.json`.
- This is author verification. Independent cross-review and app/media/deployment checks are owned by the integrating agent.

## Scope decisions

- No complex-number roots, general proof of vector-product properties, Runge–Kutta methods, logistic differential-equation derivation, or complex-eigenvalue exact ODE solutions are required.
- Diagonalization uses 2 by 2 matrices with distinct real eigenvalues. Complex/imaginary phase portraits are assessed qualitatively.
- Confidence intervals and mean tests use t when population SD is unknown. Pooled two-sample tests state the equal-variance assumption. Matched pairs analyze a single sample of differences.
- Binomial/Poisson tests are one-tailed; their discrete critical regions use actual Type I probability strictly below the nominal level.
- Chi-square goodness-of-fit accounts for the fitted parameter and all expected category counts exceed 5. Nonlinear regression states whether it minimizes residuals in log or original output units.
- Column Markov state conventions and simultaneous old-state Euler updates are explicit.

## Reproduction

Run `ai_hl_build.py` (optionally `--limit 80` for the 400-record checkpoint), `ai_hl_numeric_audit.py`, `ai-hl-audit.mjs`, and finally `ai_hl_signoff.py` from this authoring directory or the repository root. Python uses the existing `work/aa-sl-deps` scientific dependencies; Node uses the repository dependencies.

## Families

### number-algebra

| Questions | Family | Primary scope | Marks |
|---|---|---|---|
| 1–4 | Arithmetic investment investigation | 1.2 | 12 |
| 5–8 | Geometric sequences and threshold | 1.3 | 7 |
| 9–12 | Real investment value | 1.4 | 6 |
| 13–16 | Loan repayment and balance | 1.7 | 8 |
| 17–20 | Bounds and logarithmic scales | 1.6 | 6 |
| 21–24 | Logarithm laws and domain | 1.9 | 6 |
| 25–28 | Rational exponents | 1.10 | 6 |
| 29–32 | Infinite geometric distance | 1.11 | 7 |
| 33–36 | Infinite series investigation | 1.11 | 12 |
| 37–40 | Cartesian complex arithmetic | 1.12 | 6 |
| 41–44 | Quadratic roots and Argand interpretation | 1.12 | 7 |
| 45–48 | Complex phasor addition | 1.13 | 8 |
| 49–52 | Integer powers in polar form | 1.13 | 6 |
| 53–56 | Complex multiplication and geometry | 1.12 | 7 |
| 57–60 | Matrix systems in context | 1.14 | 7 |
| 61–64 | Three-variable matrix model | 1.14 | 6 |
| 65–68 | Matrix encoding and decoding | 1.14 | 6 |
| 69–72 | Inverse matrix and perturbation | 1.14 | 7 |
| 73–76 | Eigenvalues and eigenvectors | 1.15 | 8 |
| 77–80 | Diagonalization investigation | 1.15 | 12 |
| 81–84 | Affine recurrence investigation | 1.11 | 12 |
| 85–88 | Matrix powers and invariant state | 1.15 | 12 |
| 89–92 | Annuity and inflation investigation | 1.7 | 12 |
| 93–96 | Geometric threshold sensitivity | 1.3 | 12 |
| 97–100 | Eigenvalue control investigation | 1.15 | 12 |

### functions

| Questions | Family | Primary scope | Marks |
|---|---|---|---|
| 1–4 | Composite functions in context | 2.7 | 8 |
| 5–8 | Inverse and restricted domain | 2.7 | 6 |
| 9–12 | Exponential inverse | 2.7 | 6 |
| 13–16 | Graph transformations | 2.8 | 7 |
| 17–20 | Composite transformations | 2.8 | 7 |
| 21–24 | Half-life model | 2.9 | 8 |
| 25–28 | Offset exponential modelling | 2.9 | 8 |
| 29–32 | Natural logarithmic model | 2.9 | 7 |
| 33–36 | Sinusoidal parameters | 2.9 | 8 |
| 37–40 | Sinusoidal inequality investigation | 2.9 | 12 |
| 41–44 | Logistic investigation | 2.9 | 12 |
| 45–48 | Logistic calibration | 2.9 | 9 |
| 49–52 | Piecewise continuity | 2.9 | 8 |
| 53–56 | Piecewise inverse in context | 2.9 | 8 |
| 57–60 | Log-log linearization | 2.10 | 7 |
| 61–64 | Semi-log exponential interpretation | 2.10 | 8 |
| 65–68 | Residual-based model investigation | 2.9 | 12 |
| 69–72 | Polynomial modelling | 2.5 | 8 |
| 73–76 | Rational model and domain | 2.9 | 8 |
| 77–80 | Quadratic decision modelling | 2.6 | 8 |
| 81–84 | Power fit investigation | 2.10 | 12 |
| 85–88 | Inverse sensitivity investigation | 2.7 | 12 |
| 89–92 | Exponential versus logistic investigation | 2.9 | 13 |
| 93–96 | Transformation forecast investigation | 2.8 | 12 |
| 97–100 | Piecewise model investigation | 2.9 | 12 |

### geometry-trigonometry

| Questions | Family | Primary scope | Marks |
|---|---|---|---|
| 1–4 | Radians and sector geometry | 3.7 | 7 |
| 5–8 | Unit-circle trigonometric solutions | 3.8 | 7 |
| 9–12 | Triangle modelling | 3.3 | 7 |
| 13–16 | Affine matrix transformations | 3.9 | 8 |
| 17–20 | Composition of transformation matrices | 3.9 | 7 |
| 21–24 | Determinant and area scale | 3.9 | 8 |
| 25–28 | Fractal transformations investigation | 3.9 | 12 |
| 29–32 | Three-dimensional vectors | 3.10 | 7 |
| 33–36 | Vector and parametric line forms | 3.11 | 7 |
| 37–40 | Vector constant-velocity motion | 3.12 | 8 |
| 41–44 | Relative motion investigation | 3.12 | 12 |
| 45–48 | Scalar product | 3.13 | 7 |
| 49–52 | Vector product and area | 3.13 | 8 |
| 53–56 | Intersection of vector lines | 3.11 | 6 |
| 57–60 | Graph degrees and Euler trails | 3.16 | 8 |
| 61–64 | Adjacency matrix walks | 3.15 | 7 |
| 65–68 | Graph transition matrix | 3.15 | 7 |
| 69–72 | Kruskal network investigation | 3.16 | 12 |
| 73–76 | Prim network investigation | 3.16 | 12 |
| 77–80 | Chinese postman with two odd vertices | 3.16 | 12 |
| 81–84 | Postman pairing investigation | 3.16 | 12 |
| 85–88 | Nearest-neighbour TSP investigation | 3.16 | 12 |
| 89–92 | Deleted-vertex TSP investigation | 3.16 | 12 |
| 93–96 | Metric completion routing investigation | 3.16 | 12 |
| 97–100 | Voronoi modelling investigation | 3.6 | 13 |

### statistics-probability

| Questions | Family | Primary scope | Marks |
|---|---|---|---|
| 1–4 | Valid and reliable data collection | 4.12 | 12 |
| 5–8 | Discrete expectation and variance | 4.14 | 6 |
| 9–12 | Binomial model and conditional probability | 4.8 | 7 |
| 13–16 | Normal quantiles | 4.9 | 6 |
| 17–20 | Chi-square independence test | 4.11 | 9 |
| 21–24 | Fitted-parameter goodness of fit | 4.12 | 12 |
| 25–28 | Pooled two-sample t-test | 4.11 | 9 |
| 29–32 | Nonlinear least-squares regression | 4.13 | 9 |
| 33–36 | Nonlinear model comparison investigation | 4.13 | 12 |
| 37–40 | Linear transformation of a random variable | 4.14 | 6 |
| 41–44 | Linear combinations of normal variables | 4.15 | 7 |
| 45–48 | Central limit theorem | 4.15 | 7 |
| 49–52 | t confidence interval | 4.16 | 8 |
| 53–56 | Known-SD confidence interval | 4.16 | 8 |
| 57–60 | Poisson rate model | 4.17 | 7 |
| 61–64 | Sum of Poisson variables | 4.17 | 7 |
| 65–68 | Known-SD mean test | 4.18 | 9 |
| 69–72 | One-sample t-test | 4.18 | 9 |
| 73–76 | Matched-pairs t-test | 4.18 | 10 |
| 77–80 | Exact binomial test investigation | 4.18 | 12 |
| 81–84 | Poisson test investigation | 4.18 | 12 |
| 85–88 | Population correlation test | 4.18 | 10 |
| 89–92 | Normal Type I and II investigation | 4.18 | 12 |
| 93–96 | Two-state Markov investigation | 4.19 | 12 |
| 97–100 | Three-state Markov investigation | 4.19 | 12 |

### calculus

| Questions | Family | Primary scope | Marks |
|---|---|---|---|
| 1–4 | Product rule and tangent | 5.9 | 8 |
| 5–8 | Quotient rule | 5.9 | 7 |
| 9–12 | Chain rule and logarithmic derivative | 5.9 | 7 |
| 13–16 | Related rates for volume and area | 5.9 | 8 |
| 17–20 | Implicit related rates | 5.9 | 8 |
| 21–24 | Exponential optimization investigation | 5.10 | 12 |
| 25–28 | Second derivative and concavity | 5.10 | 8 |
| 29–32 | Integration by substitution | 5.11 | 7 |
| 33–36 | Trigonometric integration | 5.11 | 7 |
| 37–40 | Area with sign changes investigation | 5.12 | 12 |
| 41–44 | Volume of revolution investigation | 5.12 | 12 |
| 45–48 | Kinematics investigation | 5.13 | 12 |
| 49–52 | Kinematic chain rule | 5.13 | 7 |
| 53–56 | Separable growth equation | 5.14 | 8 |
| 57–60 | Separation and model critique investigation | 5.14 | 12 |
| 61–64 | Inflow-outflow differential equation | 5.14 | 12 |
| 65–68 | Slope-field interpretation | 5.15 | 8 |
| 69–72 | Euler method investigation | 5.16 | 12 |
| 73–76 | Euler refinement investigation | 5.16 | 12 |
| 77–80 | Coupled Euler investigation | 5.16 | 12 |
| 81–84 | Distinct-real coupled differential equations | 5.17 | 14 |
| 85–88 | Phase-plane investigation | 5.17 | 12 |
| 89–92 | Complex-eigenvalue phase behaviour | 5.17 | 8 |
| 93–96 | Second-order Euler investigation | 5.18 | 12 |
| 97–100 | Exact second-order investigation | 5.18 | 13 |
