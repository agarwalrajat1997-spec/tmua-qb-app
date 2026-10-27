# ESAT module predictions

The dashboard retains the original compact cream/maroon prediction strip, preparation rank and January countdown. The sole prediction change is separate subject scores. The information icon explains each subject's confidence, range and evidence.

## Automatic pathway inference

No module selection or booked exam date is required. The authenticated GET endpoint `/api/esat/module-predictions` reads the current student's recognised test attempts and eligible Question Bank events. It calculates all five subjects separately before deciding which to show.

Mathematics 1 is always included. An optional module needs at least one recognised independent test section or 20 eligible unique Question Bank questions to indicate a pathway. Entirely blank sections do not count. With two evidenced optional subjects, the pathway is inferred. When more than two optional subjects have evidence, the strongest two are selected only if the second has over 25% more evidence strength than the third. Strength is `2 × independent tests + min(unique QB questions / 20, 3)`. Otherwise the pathway remains uncertain and the strip shows one “Still building” message. Retakes and recombined shared papers do not inflate independent test counts.

The inference indicates current practice, not a confirmed exam booking. It can update as the student's practice changes. Scores remain subject-specific; evidence from one subject never contributes to another.

## Scoring and confidence

ESAT module scores can now use Question Bank evidence after 20 eligible unique first-exposure questions per module. The trusted server override affects module predictions only; the shared engine default stays at 30 for TMUA and the legacy cohort-rank calculation. Question Bank-only predictions always have Low confidence, regardless of volume. Recognised paper evidence is required for Medium/High confidence under the existing rules. Repeated-paper treatment and standard-time adjustment for 25% extra time remain.

All three module scores appear together only after the pathway is inferred and each subject has a numerical prediction of at least 3.5 with a confidence label. Until then, both API and UI withhold the partial score set and the strip shows a single “Still building” message. This includes a missing Mathematics 1 score, fewer than two identified optional modules, mixed/ambiguous pathways, and any subject below 3.5. A qualifying paper can supply evidence independently of the question-bank minimum; 20 questions per subject is the QB-only route, not a new mandatory requirement for test-based predictions.

## No portal guarantee workflow

Predictions are live and read-only. No exam plan, prediction-lock or result-submission tables are read or written. PUT/POST are not exposed. The previously introduced lock cron is disabled; existing records are retained. Guarantee assessment and any two-day snapshot are handled manually outside this portal. Historical migrations and policy helpers remain for audit history, not as active portal behavior.

## Verification

`npm run verify:esat-module-predictions` covers subject isolation, independent evidence, QB thresholds, all six pathways, incomplete/mixed evidence, blank sections, read-only API authorization and failure handling. The build also runs existing rank, countdown, ESAT and TMUA regressions.
