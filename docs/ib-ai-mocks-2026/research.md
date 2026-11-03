# AI HL mock specification for the 2026 syllabus

The controlling document is the [official current AI guide](https://xmltwo.ibo.org/publications/EAD/2026_EN/GR5/GR5-Maths_AI_EN.pdf), published February 2019 and updated August 2025. The [2026 examiner instructions](https://ibpublishing.ibo.org/exinst/apps/exinst/index.html?chapter=2&doc=EX_instructions_2026_e&part=12) explicitly link that version. The guide has 103 PDF pages; add six to its printed page number to locate a one-based PDF page.

| Paper | Time | Marks | Form |
|---|---:|---:|---|
| AI HL 1 | 120 minutes | 110 | Compulsory short responses |
| AI HL 2 | 120 minutes | 110 | Compulsory extended responses |
| AI HL 3 | 75 minutes | 55 | Two compulsory investigations |

Every paper requires a GDC and a clean AI formula booklet. There is no AA Section A/B split. The guide does not mandate a Paper 1 or 2 question count: sixteen short questions and six extended questions are defensible collection choices. The two Paper 3 questions can carry 27 and 28 marks. These requirements appear on guide printed pages 75 and 78–80.

The [public official specimen pack](https://www.ibo.org/globalassets/new-structure/university-admission/pdfs/dp-mathematics-applications-and-interpretation-specimen-papers-en.pdf) illustrates eighteen short Paper 1 questions, seven extended Paper 2 questions, and two connected Paper 3 themes. It supports mathematical working for GDC results and explicit interpretation marks. Its 2018 Paper 3 cover still says one hour; the updated current guide controls the duration.

The [IB mathematics curriculum page](https://www.ibo.org/programmes/diploma-programme/curriculum/mathematics/) identifies November 2028 as the final assessment of the present courses. The [AI redevelopment page](https://ibo.org/university-admission/latest-curriculum-updates/dp-mathematics-applications-and-interpretation-updates/) describes the first-assessment-2029 reductions. Do not import those reductions into these mocks: complex numbers, cross products, Poisson models and the existing inference topics remain relevant now. The future 100/100/50 totals and one-hour Paper 3 are not the current specification.

## AI character and boundaries

AI reasoning should centre on choosing models, translating contexts, using technology meaningfully, assessing assumptions, and interpreting results. It should not become a copy of AA papers with calculator permission added. Valid HL additions include matrices/eigenvalues, phasors, nonlinear regression, graph algorithms, inferential statistics, regular Markov chains and coupled differential systems. AHL and SL reference numbers in `specification.json` use the official guide, not a third-party worksheet sequence.

The machine-readable file records the precise restrictions. Especially useful checks before authoring are:

- Complex roots-of-unity tasks are excluded by AHL 1.13; integer powers and phasors are included. Matrix algebra is AHL 1.14, and eigenvalue calculations are limited to 2×2 in AHL 1.15. Exact diagonalization uses distinct real eigenvalues.
- AI vector lines and products are AHL 3.11–3.13; plane-equation methods are not assumed content. Cross-product areas and relative-motion closest approaches are suitable alternatives.
- Voronoi work is SL 3.6. Give site coordinates and a suitable diagram; a waste-location optimum must actually occur at a three-edge vertex in the designed problem.
- Network algorithms are AHL 3.14–3.16. Chinese postman uses undirected graphs with at most four odd vertices. TSP bounds use nearest neighbour and deleted vertex, with least-distance completion where needed.
- Statistical models must state independence, normality/rate assumptions and the parameter being tested. Use known/unknown population sigma correctly. Pooled two-sample t is SL 4.11; single-sample/paired t is AHL 4.18. Chi-square fitted-parameter degrees of freedom are AHL 4.12. Binomial and Poisson tests are one-tailed; critical regions keep the Type I probability strictly below the specified level.
- AHL 4.19 is regular Markov chains, with column states and probabilities running from column j to row i. Absorbing-chain theory is not assumed.
- Euler coupled models are AHL 5.16. Phase portraits in AHL 5.17 have distinct nonzero eigenvalues; complex cases are qualitative and exact solutions require distinct real eigenvalues. Given second-order equations are AHL 5.18. Do not assume Jacobians, Runge–Kutta, integration by parts, Maclaurin series or l'Hopital.

## Named style sources and originality

The public [Christos AI exercise index](https://www.christosnikolaidis.com/en/mai-exercise/) separates shared SL/HL content and HL additions, and emphasizes questions with working space and solutions. Its numbering explicitly follows the author's own notes; it is not the official numbering. The public [AI HL tests index](https://www.christosnikolaidis.com/en/mai-hl-test/) illustrates cumulative topic combinations. The [AI Paper 3 index](https://www.christosnikolaidis.com/en/mai-hl-test2/) groups investigations around inference, differential models, distributions and matrices; several entries are explicitly official specimens. These are structural references, not question text to reproduce.

The public [Revision Village AI HL overview](https://www.revisionvillage.com/ib-math/applications-and-interpretation-hl/questionbank/) and [mock overview](https://www.revisionvillage.com/ib-mock-exams/) were inspected for short contextual prompts, difficulty progression and part marking. Paid content was not accessed or bypassed. Any stale secondary timing gives way to the official current guide.

All authored material will therefore use independent contexts, data, diagram geometry, questions and solutions. It is original IB-style practice, not an official past paper or a reconstruction of any named provider's question.

## Production verification

For each part, solve afresh from the stated givens, record executable numerical checks where appropriate, and separately verify domains, alternatives, end cases, rounding, significance decisions and interpretation. Proof/generalization marks require written mathematical justification; numerical spot checks alone do not establish a proof. Part marks, question marks and paper totals must reconcile. Scientific SVGs need correctly scaled data, named axes/units and legible labels. Final PDFs must be visually checked for tall mathematical expressions, especially multiline stems containing integrals or large fractions.
