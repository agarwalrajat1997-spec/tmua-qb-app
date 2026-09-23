# ESAT Mock Test 5 corrected edition

The Test 5 solution booklet and the active Engineering Test 5 template now use the same 81 questions, five options per question, diagrams and answer letters. The active test ID is `esat-mock-05`; its existing source directory is `esat-mock-13`.

The latest-named Downloads booklet was a byte-identical duplicate of the older `WITH_IMAGES` version. It lacked later live corrections to Physics 3, 7 and 12 and Mathematics 2 question 4. This release preserves those live corrections and updates the corresponding worked solutions.

## Corrections

- Mathematics 1 Q3: change the supplied sum to 37/6 and correct the factorisation, preserving the intended answer 31/2.
- Mathematics 1 Q5: correct diagram dimension lines and the position of R.
- Mathematics 1 Q15/Q17: remove the contradictory immediate return and specify positive w.
- Mathematics 1 Q21: double all four labelled side lengths so the given 12 cm² small triangle is possible, preserving the area ratio and answer 135 cm².
- Mathematics 1 Q24: repair option E's inequality markup.
- Physics Q1/Q2/Q4/Q5/Q7/Q8: clarify required assumptions, provide relationships and correct raw formula labels in the conduction diagram.
- Physics Q10: explicitly provide 3.3 A total and 1.8 A through R, and label both ammeters.
- Physics Q12: match the existing trolley, graph units and 1.05 × 10³ W answer.
- Physics Q14/Q16: clarify heat-loss and constant-resistance assumptions.
- Physics Q18: consistently ask for voltage, resistance and power in every option.
- Physics Q21: embed a clear diagram showing the two wavelengths between P and Q.
- Physics Q24: ask for the larger magnitude of average emf over the two journeys; provide the flux-linkage relation and remove the misleading velocity graph.
- Physics Q27: distinguish the smooth first experiment from the rough patch in the second, and define the height reference.
- Mathematics 2 Q4: match the current live diagram, question and C = 88° answer.
- Mathematics 2 Q14/Q20/Q27: strengthen the non-calculator comparison and correct explanatory wording.
- Mathematics 2 Q22: replace the equivalent correct distractor A with 6a/√13, leaving B uniquely correct.
- Mathematics 2 Q25: specify 0 < x < 16.

## Release and checks

- The dashboard and the test's results/email PDF variable point to `/esat-practice-tests/solutions/esat-mock-05-solutions.pdf?v=20260924`.
- Editable, self-contained booklet source is saved alongside this note in `esat-mock-05-solution-book.html`.
- All existing live answer letters are retained, including Mathematics 2 Q4's C. No scoring registry, prediction calibration or saved attempts were changed.
- PDF: 83 A4 pages (cover, answer keys, 81 complete question/solution pages), 405 options, 997 rendered formula elements, no missing/external images, raw formula delimiters or clipped content. All page layouts reviewed, with detailed checks of repaired diagrams and longest pages.
- PDF SHA-256: `305a1bcba11a8202eeacb40279e5daccabe1934a41eff34b4fbc20f7fad62027`.
- All source questions/options match the booklet; all three answer-key representations agree. Numerical checks cover the corrected equation, triangle, circuit, momentum graph, circle geometry, induction, unique perpendicular-distance option and spring energy.
- Full `prebuild`, production build, `postbuild` and `git diff --check` passed locally. Network/database/email writes were not used by verification.
