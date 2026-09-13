# ESAT evidence-calibrated score estimate v2

Version: `ESAT_EVIDENCE_CALIBRATED_V2_20260818`

## Purpose

This model gives the best reproducible practice estimate available before
the portal has a trustworthy cohort of timed candidate responses. It does
not claim to reproduce UAT-UK's confidential operational equating.

The API returns three module estimates on the official 1.0-9.0 reporting
scale. It also returns a `predictedCombinedPracticeScore`, calculated as the
mean of the three module estimates. The combined value is a Thriving
Scholars practice summary; official ESAT results report modules separately.

## Evidence hierarchy

1. [Official UAT-UK test-results guidance](https://esat-tmua.ac.uk/test-results/)
   establishes that ESAT forms are equated with Rasch item-response methods,
   that module scaling is separate, that the typical score is 4.5 and that
   about 10% of candidates score above 7.0.
2. [Official UAT-UK ESAT preparation guidance](https://esat-tmua.ac.uk/esat-preparation-materials/)
   states that legacy ENGAA and NSAA questions are representative preparation
   for the current ESAT specification.
3. Legacy Cambridge subject-module conversion shapes supply separate priors
   for Mathematics 1, Physics, Chemistry and Biology. They are resampled from
   20 questions to 27; they are not presented as current official ESAT tables.
4. Mathematics 2 uses the median shape of the portal's official 2016-2023
   TMUA conversion profiles as a mathematical-reasoning prior. This follows
   the portal's existing rule of using real historical curves rather than a
   percentage-to-nine formula.
5. The source-paper audit supplies form difficulty. The reusable forms are:
   Engineering Mocks 1, 3 and 5 for Easy, Standard and Challenge
   Mathematics/Physics; and the corresponding Easy, Standard and Challenge
   Chemistry/Biology solution-book sources. Engineering Mocks 2 and 4 retain
   their own Standard and Hard calibrations.

## Calibration anchors

Each source module has an explicit expected raw mark at the official 4.5
centre and 7.0 top-decile anchors. These control points warp the appropriate
subject prior and materialise an immutable 28-entry lookup table (raw 0-27).

| Source form | Mathematics 1 | Physics | Mathematics 2 | Chemistry | Biology |
| --- | ---: | ---: | ---: | ---: | ---: |
| Easy | 18.1 / 23.6 | 16.3 / 21.1 | 14.5 / 19.6 | 21.1 / 25.0 | 18.9 / 23.8 |
| Standard | 15.1 / 21.6 | 13.3 / 19.1 | 11.5 / 17.6 | 18.1 / 23.0 | 15.9 / 21.8 |
| Challenge | 12.1 / 19.6 | 10.3 / 17.1 | 8.5 / 15.6 | 15.1 / 21.0 | 12.9 / 19.8 |

Each cell is `raw at 4.5 / raw at 7.0`. Engineering Mock 4 uses intermediate
Hard anchors between the Standard and Challenge rows.

The source classifications are form-level judgements, based on the complete
question and worked-solution sets: Easy emphasises direct setup and shorter
solution chains; Standard combines routine and multi-step ESAT-style work;
Challenge has denser interpretation, quantitative reasoning and longer
chains. Reused modules share the same calibration ID across pathways, so the
same paper cannot receive a different score merely because it appears in a
different pathway.

## Invariants

- Every source-module table contains 28 scores, is monotonic, begins at 1.0
  and ends at 9.0.
- The raw mark nearest each form's central anchor maps to approximately 4.5;
  the mark nearest the top-decile anchor maps to approximately 7.0.
- At the same raw mark, a harder form cannot receive a lower estimate than an
  easier form containing the corresponding source module.
- Mathematics, Physics, Chemistry and Biology do not share a generic
  percentage curve.
- All 20 portal tests resolve exactly three calibration IDs matching their
  three module names.

## Validation and future calibration

The verifier checks 20 test profiles, 21 reusable source-module calibrations
and all 588 raw-score table entries. It also checks cross-tier ordering,
module/calibration integrity, endpoints, anchors and invalid inputs.

Once enough timed attempts exist, the replacement process is:

1. score answers server-side against an immutable answer-key registry;
2. exclude previews, duplicates, interrupted attempts and suspicious timing;
3. fit item difficulties by module and inspect item fit/differential behaviour;
4. equate shared source forms and validate predicted versus observed score
   distributions out of sample;
5. publish a new version while retaining v2 for historical attempts.

Until that cohort exists, v2 should be described as an
**evidence-calibrated practice estimate**, never as an official ESAT result
or a candidate-fitted Rasch calibration.
