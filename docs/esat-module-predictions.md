# ESAT module predictions

The dashboard retains the original compact cream/maroon prediction strip, preparation rank and January countdown. The sole prediction change is separate subject scores. The information icon explains each subject's confidence, range and evidence.

## Automatic pathway inference

No module selection or booked exam date is required. The authenticated GET endpoint `/api/esat/module-predictions` reads the current student's recognised test attempts and eligible Question Bank events. It calculates all five subjects separately before deciding which to show.

Mathematics 1 is always included. An optional module needs at least one recognised independent test section or 30 eligible unique Question Bank questions to indicate a pathway. Entirely blank sections do not count. With two evidenced optional subjects, the pathway is inferred. When more than two optional subjects have evidence, the strongest two are selected only if the second has over 25% more evidence strength than the third. Strength is `2 × independent tests + min(unique QB questions / 30, 3)`. Otherwise the pathway remains uncertain and evidenced modules are shown without claiming a final pathway. Retakes and recombined shared papers do not inflate independent test counts.

The inference indicates current practice, not a confirmed exam booking. It can update as the student's practice changes. Scores remain subject-specific; evidence from one subject never contributes to another.

## Scoring and confidence

Existing evidence weighting, first-exposure QB eligibility, the 30-question subject threshold, repeated-paper treatment, confidence rules and standard-time adjustment for 25% extra time remain. Scores below 3.5 show “Still building”. Medium/High confidence is not redefined by this UI change.

## No portal guarantee workflow

Predictions are live and read-only. No exam plan, prediction-lock or result-submission tables are read or written. PUT/POST are not exposed. The previously introduced lock cron is disabled; existing records are retained. Guarantee assessment and any two-day snapshot are handled manually outside this portal. Historical migrations and policy helpers remain for audit history, not as active portal behavior.

## Verification

`npm run verify:esat-module-predictions` covers subject isolation, independent evidence, QB thresholds, all six pathways, incomplete/mixed evidence, blank sections, read-only API authorization and failure handling. The build also runs existing rank, countdown, ESAT and TMUA regressions.
