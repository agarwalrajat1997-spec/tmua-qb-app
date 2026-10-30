# Geometry & Trigonometry authored content review

## Deliverable

- 182 questions, one-to-one reference mapping Q1–Q182.
- Difficulty retained from source: 70 easy, 85 medium, 27 hard.
- Original source calculator flags retained.
- Each question has a complete written marking scheme and explicit part marks.
- No unresolved drafts: 182 entries are ready for integration. This is authored practice content, not an official IB examiner-approved bank.
- 26 question SVGs and 6 marking-scheme SVGs; no source branding, video links or AI feedback.

## Verification performed

- Rebuilt all entries with `python -W error geometry-trigonometry-build.py`; mathematical parameter and root assertions execute during the build.
- Validated contiguous source IDs, unique source mapping, part/scheme pairing, every per-part award sum and every total mark sum.
- Parsed all 32 SVGs as XML, checked prohibited markup/resource patterns, rendered all with bundled Sharp, and visually inspected three contact sheets.
- Inspected source PDF renders for truncated graph/shape references; reconstructed missing conditions explicitly in affected entries.
- Used SymPy exact vector algebra, cross products, plane equations, projection/reflection, polynomial factoring and roots; used numerical bracketing/optimization for trigonometry, related rates and closest approaches.
- Cross-review from the Number & Algebra author independently checked all hard questions Q156–Q182 and medium Q75,85,95,105,115,125,135,145,150,155. Parent also sampled exact-ratio criteria, closest motion, hard vectors and inverse graphs.
- Corrections from review: distinct quadrant accuracy criteria; time variable and 15:48 conversion in Q134; explicit denominator grouping in Q158; correct +2x quartic in Q179; readable radius label in Q42; USD currency notation; percent escaping; scientific notation as powers of 10; guard digits in numerical intermediates.
- All mathematical display dollar delimiters balanced. Matrix line-break backslashes are intentional; ordinary LaTeX commands use single backslashes in decoded JSON.

## Source reconstruction notes

- Q1: Reference graph/parts partly omitted in PDF; complete new labelled graph retains amplitude, period and midline skills. Exact extrema verified from the new sinusoid.
- Q2: Reference graph/parts partly omitted in PDF; complete new labelled graph retains amplitude, period and midline skills. Exact extrema verified from the new sinusoid.
- Q4: Reference graph/parts partly omitted in PDF; complete new labelled graph retains amplitude, period and midline skills. Exact extrema verified from the new sinusoid.
- Q15: Reference figure/parts clipped. New sector-and-perpendicular description completely specifies the equivalent area task; numeric geometry checked.
- Q25: Reference base diagram partly absent; base dimensions explicitly supplied for an equally demanding right-pyramid calculation.
- Q49: Reference later parts clipped; full new model question retains Ferris-wheel amplitude/period/height skills.
- Q52: Reference figure/parts clipped. New sector-and-perpendicular description completely specifies the equivalent area task; numeric geometry checked.
- Q55: New complete geometric definition reconstructs the clipped reference shaded-region task; area and positive radius numerically checked.
- Q57: Reference graph/parts partly omitted in PDF; complete new labelled graph retains amplitude, period and midline skills. Exact extrema verified from the new sinusoid.
- Q72: Truss direction labels are absent from source extraction; a fully specified equilateral-lattice vector variant preserves the intended scalar-product skill.
- Q75: Source blade diagram reconstructed by a complete disk/annular-sector specification; changed all radii and angle.
- Q95: Reference chord/angle values appear geometrically inconsistent; rebuilt from exact central-angle data on a genuine circle. Coordinates independently verify lengths and areas.
- Q112: Source Q112 supplies an unlabelled triangle/sector/median figure but no recoverable numerical givens or parts; a complete 8-mark version is reconstructed. Distances and sector area checked numerically.
- Q116: Explicit planted-region definition replaces partly unreadable source shading. All geometry and ceiling operation checked using unrounded values.
- Q118: Grazing sectors reconstructed from the visible triangular-fence diagram. Computed alpha and checked via sine rule that BD exceeds 7.5 m, so the assumed wrap path is valid.
- Q125: Source graph reconstructed through explicitly specified consecutive stationary points. Frequencies and inverse interval checked algebraically.
- Q140: Source Q140 has only introductory wheel data; reconstructed complete modelling sequence to its advertised 16 marks. Period, endpoints and threshold times verified numerically.
- Q146: Source Q146 part (b) is clipped from the PDF; reconstructed period/intercept task matching its 5-mark allocation. Solutions checked by direct substitution.
- Q150: Original limit at tangent pole lacked a side; new domain explicitly selects the left-hand limit so the result is well-defined.
- Q154: Source Q154 stops after its line/plane definitions; the missing angle condition was reconstructed as a complete exact-value 5-mark problem.
- Q156: Source Q156 is clipped after trapezium dimensions; restored the angle-maximization task shown by its knife-holder diagram. Critical point and both endpoints checked independently.
- Q165: Source Q165 final part is absent; restored a 3-mark exact root application, retaining scalar-product geometry and changing the side-length ratio.
- Q176: Both circle radii and shared-area target changed. Lens formula, central angles and positive radius checked numerically; SVG reconstructed from the two exact circle radii and centre distance.
- Q179: Quartic roots, critical points, concavity and composition domain checked with SymPy. Restricted inverse endpoints reflected in the SVG. The phrase maximal decreasing interval removes the original ambiguity about choosing an inverse branch.

## Mark allocations

The bank preserves the number and sequence of source questions. The following reconstructed or rebalanced variants use different totals so the awards match the actual written task; totals are not padded to a source maximum when its parts were unavailable.

| Question | Source marks | Authored marks |
|---|---:|---:|
| Q2 | 6 | 7 |
| Q4 | 6 | 7 |
| Q9 | 6 | 8 |
| Q19 | 4 | 5 |
| Q36 | 6 | 7 |
| Q49 | 7 | 8 |
| Q52 | 5 | 6 |
| Q57 | 6 | 9 |
| Q68 | 9 | 10 |
| Q89 | 12 | 11 |
| Q97 | 16 | 13 |
| Q128 | 7 | 6 |

Source extraction omitted the total-mark field for Q125, Q142 and Q157; their part totals are 10, 22 and 16 respectively.

## Limitations

Where the uploaded PDF is physically clipped, exact omitted source text cannot be recovered. These entries use a fully specified, mathematically valid reconstruction of the visible method/diagram, recorded above. Difficulty is inherited rather than empirically calibrated against student performance. No claim is made of official IB endorsement or examiner moderation.
