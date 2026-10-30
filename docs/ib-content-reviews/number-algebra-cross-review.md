# Independent Number & Algebra cross-review

Read-only mathematical review by the Functions author. No Number & Algebra source or data files were edited in this review.

## Coverage

Read every question and every solution step in Q150–229 (80 questions), including the induction proofs, complex roots and arguments, parameterised linear systems, counting, negative-binomial reasoning, and financial recurrences.

Also reviewed these earlier items: Q1, 4, 16, 31, 34–36, 39–40, 42, 44, 49, 53, 55, 58, 65–66, 68–69, 71, 84–86, 90–91, 94–95, 98–99, 102, 105, 107–111, 113–116, 118, 125, 128, 132, 134, 137–139, 141–142, 145–149. These focused on financial timing, sequence bounds, complex-number geometry and proofs.

## Findings sent to the parent

| ID | Finding | Required correction |
|---|---|---|
| ib-aa-na-071(b) | The multiplier is quarterly and the threshold is 86 compounding periods, but the solution calls them months. | Say **86 quarters = 258 months = 21.5 years**, during **2045**. The reported calendar year itself is correct. |
| ib-aa-na-090(b) | A result requested to three significant figures is shown as 0.62. | Use **0.620 rad**; the unrounded value is approximately 0.620249. |
| ib-aa-na-132(c) | A result explicitly requested to three significant figures is shown as 3. | Use **p = e^1.1 ≈ 3.00**. |
| ib-aa-na-141(d) | The displayed G48 and G49 are rounded to 256 but written as exact equalities. | Use **≈256**, or retain enough digits to show both are below 256. The final answer n=48 is correct. |
| ib-aa-na-221(e) | The sketch scheme uses an undefined generic λ and says to choose the relevant case. | State the actual behaviour: **f(x)→0 from below as x→−∞; f(x)→+∞ as x→+∞**. |
| ib-aa-na-221 | The exponent e^{1/2x} is visually ambiguous. | Consistently use **e^{x/2}** in the stem and solution. |
| ib-aa-na-225(e) | Same undefined generic λ wording as Q221. | State **f(x)→−∞ as x→−∞; f(x)→0 from above as x→+∞**. |
| ib-aa-na-213(c), step 3 | A transient source snapshot appeared to contain an escaped-tab problem in theta. | **Already correct in the subsequent read:** `Factor out $2\sin3\theta$.` No further change needed if that version is retained. |

No other substantive mathematical errors were found within the reviewed scope. Formatting errors in early money expressions were already reported by the parent’s application validator and were not treated as mathematical findings here.

## Independent computation

Used separate SymPy/scipy calculations, rather than relying on the author’s result strings:

- Symbolic polynomial/identity checks passed for Q154, 159, 160, 165, 172, 186, 198 and 201.
- Exact combinatorial count in Q206 independently reproduced: 5,356,108,800.
- Q151: 7-year balance 26,184.224900; first target year 11; minimum unrounded nominal rate 5.7674570165%; geometric initial deposit 24,000.3662165.
- Q156: n−1 must exceed 16.00784556, giving least n=18.
- Q161: original investment 31,504.9741268; minimum initial amount before upward integer rounding 31,423.6093645; six contributions total 16,537.50.
- Q163: model populations 9,646.1955584 and 10,952.9914814, confirming nearest-tree answers.
- Q209: independently solved the **discounted present value** equation, obtaining nominal rate 6.0180389582%, monthly multiplier 1.0050150324652, balance after payment 90 of 111,151.0654116, and alternative payment p=2,805.9919717. This differs computationally from the author’s accumulated-value derivation and confirms it.
- Q211 and Q228: independently expanded the products to degree two; both coefficient equations are correct.
- Q222: exact transformed-quadrilateral area confirmed as 16,128/4,225.
- Q226: the two-game probability confirmed as 14,400/531,441; the binomial identity follows by the stated partition.
- Q216: loan value 180,014.3657281 and quarterly deposit 4,801.1425816 confirm the cent-rounded answers.
- Q227: independently computed tail probabilities at N=14 and N=15 as 0.4786600396 and 0.5387131236, confirming least N=15 and the mode reasoning.
- Q221/Q225: symbolic differentiation confirms their stationary and inflection inputs, and symbolic limits confirm the concrete end behaviour specified above.

This review checks mathematical correctness within its stated coverage; it does not claim external IB examiner approval or full visual QA of the application.
