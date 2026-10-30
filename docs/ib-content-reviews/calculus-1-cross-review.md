# Calculus 1 independent cross-review

Reviewed by the Geometry & Trigonometry content agent. The reviewer did not edit Calculus 1 content.

## Coverage

- Remaining hard questions reviewed: Q101, Q102, Q104, Q105, Q107, Q108, Q109, Q111, Q112, Q113, Q115, Q116, Q117, Q119, Q120, Q121, Q123, Q124, Q125.
- Additional medium questions reviewed: Q44, Q52, Q64, Q65, Q70, Q73, Q78, Q80, Q84, Q90, Q94, Q97, Q98, Q99.
- SVGs independently rendered and visually inspected: Q16 question and scheme; Q53 question; Q63 scheme; Q70 question; Q77 question; Q82 scheme; Q116 scheme; Q120 question; Q121 scheme; Q123 scheme. Eleven diagrams total.

## Findings

No substantive mathematical errors found in the 33 reviewed questions. Checked derivatives, domain restrictions, inverse branches, implicit tangent conditions, nonzero denominators, sign changes, optimization endpoints, units and related-rate conversions.

Specific domain checks include the excluded upper endpoint 5 in Q104's inverse domain, the positive/nonzero derivative denominator in Q111, the logarithm domain and inequality intervals in Q112, and the absolute value needed in Q125's derivative at nonzero x. Q125 correctly excludes x=0 from its derivative formula while retaining it in the function/restricted-inverse range analysis.

The half-segment tank geometry and filling limits in Q120 are consistent with the illustrated vertical partition and maximum angle. The inverse and concavity arguments in Q121, Q124 and Q125 are sound. Q94 correctly excludes the canceled root x=3 and addresses the parameter case a=3 separately.

## Independent computations

Python/SymPy/SciPy recomputation used separate expressions for the following checks:

| Question | Independent result | Agreement |
|---|---|---|
| Q73 | c = -1.273437562464384; 1% threshold t = 11.616329784615482 min | Matches -1.27 and 11.6 min |
| Q90 | h = 1536^(1/10) = 2.0827594879848212 | Matches 2.08 |
| Q104 | Derivative of ln(3 - sqrt(x+4)) algebraically agrees with the inverse-derivative expression | Exact symbolic difference zero |
| Q116 | a(s)=1 roots: 1.6848152406167574 and 2.8587100901267672 m | Matches 1.68 and 2.86 |
| Q119 | Second normal/curve intersection: (4.324534079799462, -2.4958142331132307) | Matches (4.32, -2.50) |
| Q120 | Right volume rounds to 2764 litres; fill time 12.32950072150989 min | Matches 2764 litres and 12 min |
| Q123 | Inflexion abscissae 0.20450809107140286 and 1.1950096911682448 | Matches 0.205 and 1.20 |

Other reviewed exact expressions were independently recomputed manually, including the chain/product rules, vector-independent implicit derivations, inverse formulas and sign charts.

## Visual finding sent to parent

Q53's rightmost label G(t=4.5) extends beyond the SVG viewBox and is clipped. The graph itself and its zero are correct. Shift this label left or use text-anchor=end. Parent confirmed it will apply this rendering correction to the builder and JSON. No other material visual issues were found in the selected diagrams.
