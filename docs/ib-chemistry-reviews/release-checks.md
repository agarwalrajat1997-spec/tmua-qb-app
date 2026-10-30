# Chemistry release checks — 30 October 2026

The release adds 600 original Chemistry questions: 407 shared SL and 193 additional
HL. Six themes and all 22 subtopics are populated. The SL view contains all 21
shared subtopics; R1.4 is HL only. Maths 962 and Physics 640 data records are
unchanged. No new database, payment flow or student-data write is introduced.

## Independent scientific review

| Reviewed bank | Records | Numerical recalculations | Explicit atom/charge checks |
| --- | ---: | ---: | ---: |
| Structure 1–3 | 288 | 125 | Additional inventories and chemical checks in the ledger |
| Reactivity 1 | 96 | 186 | 24 |
| Reactivity 2 | 96 | 136 | 32 |
| Reactivity 3 | 120 | 39 | 39 |

All 600 individual records have coverage entries and hashes. Reproducible
independent scripts passed from their committed locations after the last author
corrections. The 486 numerical comparisons use displayed inputs. Corrections
include input precision, rounding ties, neutralization stoichiometry, scope
wording and explicit working for requested empirical formulas. Breadth additions
and mechanism/structure drawings were independently rechecked.

All 110 SVG uses were inspected: 72 Structure, 24 R1/R2 and 14 R3. These resolve to
99 unique diagrams. Visual checks include atom/bond/lone-pair inventories,
stereochemical wedges, electron-flow arrows, spectra, polymer repeat units,
thermodynamic cycles and readable scales. Final public Cloudflare responses match
the reviewed content hashes and SVG MIME type. A correction gets a new immutable
address; the uploaded manifest cannot silently select a cached earlier image.

## Application and build evidence

- Complete content/CDN gate passed: 600 records, 1,981 marks, 2,187 parsed
  mathematical expressions, all course/subtopic coverage, reconciled marks,
  private-answer projection and all diagram hashes.
- Actual component/route fixtures passed for six Chemistry themes, course-specific
  counts, shared IDs, authenticated HL-only denial in SL mode, filter/pagination
  and login return-link preservation, separate-tab schemes and image fallback.
- Existing Maths/Physics and TMUA/ESAT/SAT/AMC regression suite passed.
- Final production compilation and TypeScript passed with the final CDN manifest.
- Public Supabase configuration checks and the scan of 32 generated browser files
  passed, with no server keys exposed.
- Local actual-component review through the approved browser controls showed a
  readable SL overview, HL mechanism scheme and SL bank at desktop/mobile widths,
  no horizontal overflow and no mathematical parse errors.

The synthetic review helper adds no deployed route or authentication bypass.
Tests do not send email or modify student records. Live browser course switching,
question/scheme navigation and CDN verification are the postdeployment gate and
are recorded in the user-facing release handoff.

Difficulty levels are reasoned practice estimates. These independently authored
schemes are not official IB moderation; passing checks is evidence of the stated
review coverage, not a guarantee that no error could remain.
