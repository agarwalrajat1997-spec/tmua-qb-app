# Economics independent review — 31 October 2026

The reviewed snapshot passes the independent review. It contains 360 original practice records in 122 families: introduction 40, microeconomics 120, macroeconomics 100 and global economy 100. The common-content/AHL split remains 256/104. The release gate is `economics-independent-review.json`, which lists all 360 IDs, their canonical record hashes and the exact UTF-8 LF file hashes. These findings apply to that snapshot.

## Sources and assessment

Scope and assessment were checked against the current official [Economics guide, first assessment 2024](https://xmltwo.ibo.org/publications/EAD/2026_EN/GR3/GR3-Econ_EN_24.pdf) and the [2027 Economics examiner instructions](https://ibpublishing.ibo.org/exinst/apps/exinst/index.html?chapter=3&doc=EX_instructions_2027_e&part=10). The review did not copy examination questions, stimuli, diagrams or marking text.

All 54 complete Paper 1 questions have the 10+15 allocation, prohibit calculators and require the candidate's actual studied examples. All 54 complete Paper 2 cases use the shared common-content 4+5+4+4+4+4+15 allocation. All 38 complete Paper 3 cases are AHL, with 20 analytic marks and a 10-mark policy recommendation. The other 214 records are shorter structured practice. Paper 2 and Paper 3 allow calculators. Whole AHL topics and embedded AHL demands were checked against each record's level; a common topic code does not automatically make every calculation within that topic common content.

## Independent coverage

Every family baseline and every subsequent variant's changed stem, prompt, scheme and rubric focus was read. The per-ID report records the family-specific economic mechanism, variant evidence, causal interpretation, scope, numerical coverage and figure reference. Qualitative variants were checked for changed application or judgement rather than merely changed place names. Long-answer guidance was checked for case evidence, causal analysis, balanced qualification and defensible alternative conclusions. Best-fit bands are bound to the actual task and variant, with indicative content carried by zero-value IND entries.

The independent numerical implementation reads the final serialized public stems and tables; it imports neither authoring functions nor the author's expression ledger. It reconstructed all explicit numerical requests: 158 records, 290 parts and 528 result assertions. These include opportunity cost, circular flows, elasticities, market intervention and welfare, discrete monopoly, national accounts, labour and price indices, taxation, multiplier and debt, Lorenz cumulatives, exchange conversion, current accounts, tariff welfare, comparative advantage and development budgets. All assertions pass. Exact fractions or the stated precision are accepted; displayed two-decimal answers use half-up rounding, including −0.625 → −0.63.

All 360 records pass the current question schema and prompt privacy checks. All 80 Markdown tables are well formed. All 148 private solution SVGs were freshly rendered; all 21 distinct content/label designs were visually inspected across three new contact sheets. Their economic movements, intervention wedges, shortage/excess-supply projections, PPC rotation, and Lorenz geometry agree with their explanations. Repeated diagrams were mapped to their corresponding records. Schematic diagrams are not claimed to reproduce every model's numerical coordinates.

## Essential corrections made

The review clarified the precedence of additional evidence: structured initial parts retain the original assumptions, while the final application part uses the additional evidence; Paper 1 part (b) explicitly substitutes a changed case condition. This prevents internally contradictory assumptions from affecting earlier marks.

Other corrections make awarded marks correspond to distinct requested work. Examples include separate Lorenz before/after pairs, explicit 2+2 allocations for mixed calculation/explanation, intermediate data selection rather than formula-only working, and removal of duplicate credit for a signed current-account result and its deficit label. Prompts now request interpretations that their schemes mark. FDI guidance distinguishes domestic output from residents' factor income; overseas tourism is explicitly an export; real-interest questions state when an approximation is intended. Task and variant evidence were added to all best-fit rubric focuses, and rounding was aligned with current examiner guidance. The 35 exact targeted source replacements are recorded in `economics-independent-fixes.json`; the stage, rubric-focus and rounding corrections are also visible in the final authoring sources. Question totals and level counts are unchanged.

## Evidence and limits

- `economics-independent-review.json`: final status, all 360 per-ID findings and canonical hashes.
- `economics-independent-numeric.json`: reconstructed inputs, outputs and requested-part coverage.
- `economics-independent-schema-figures.json`: schema, privacy, table and SVG rendering results.
- `economics-independent-figures/`: 148 fresh PNGs and three reviewed contact sheets.
- `economics-independent-fixes.json`: exact targeted source replacements with reasons.
- `economics-audit.json` and `economics-ledger.json`: regenerated author checks and hashes after corrections.

This is an independent second-agent content review, not a human IB examiner review or an IB endorsement. The practice datasets are fictional. Paper 1 examples remain the student's responsibility. A substantive edit after the listed hashes requires the affected numerical, semantic or diagram review to be repeated and the final hashes rebound.
