# Independent Geometry & Trigonometry cross-review

Reviewed all 27 hard items Q156–182 and ten medium samples Q75, Q85, Q95, Q105, Q115, Q125, Q135, Q145, Q150 and Q155: 37 questions in total. Read every stem, part and marking-scheme step for these items and independently recomputed their key algebra and geometry. No substantive final-answer error was found.

Three presentation corrections were sent directly to the author:

- Q158: replace the ambiguous intermediate `99/9 sqrt(5)` with an explicit fraction `99/(9 sqrt(5))`. The final answer, `11 sqrt(5)/5`, was already correct.
- Q171: retain three significant figures in the final angle: `12.0°`, since `arcsin(5/24)=12.0246991806°`.
- Q135(b) and Q172(b): escape the percent symbols inside math (`75\%`, `90\%`) or move them to prose, ensuring KaTeX displays the percentage symbol.

The apparent doubled LaTeX slashes in a tool display were independently identified as a Python repr/JSON escaping layer, not a defect in the stored strings.

## Computational evidence

A separate SymPy/SciPy calculation passed 24 assertions covering GT156 stationary derivative; GT157 reflection coordinates; GT158 perpendicular distance; GT159 inverse/composite answer; GT162 line-plane angle; GT167 simultaneous distance quadratic, minimum and shortest independent connector; GT168 line distance; GT170 closest time; GT171 acute angle; GT172 rope root; GT174 reflected midpoint; GT175 plane angle; GT176 lens radius; GT177 normal; GT178 squared-angle equation; GT179 threshold, inflections and stationary abscissae; GT180/181 right-triangle geometry; GT182 common perpendicular; and GT135 grazed area.

Selected independent results:

| Item | Result |
|---|---|
| GT167 | Actual separation squared at closest time: `326/7`; shortest path connector `(-2,-2,2)` |
| GT171 | `12.024699180565824°` |
| GT172 | Rope length `14.191810050350966 m` |
| GT175 | Acute plane angle `14.506124408714392°`, rounding to `15°` |
| GT176 | Lens coefficient `5.612265758742955`; radius `1.8877561064939279 cm` |
| GT179 | Stationary x-coordinates `-1.4353102164, 0.2188978522, 1.5914123642`; inflections `-3/4,1`; inverse threshold `15/8` |

This cross-review verifies mathematical consistency of the sampled variants. It is not an external examiner certification or a second source-fidelity review of every source page.
