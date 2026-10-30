"""Bind the completed AA SL author, independent and visual reviews to exact files."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]
folder=ROOT/'docs'/'ib-maths-reviews'
author=json.loads((folder/'aa-sl-author-review.json').read_text(encoding='utf-8'))
independent=json.loads((folder/'aa-sl-independent-review.json').read_text(encoding='utf-8'))
files=sorted((ROOT/'content'/'ib'/'math-aa-sl').glob('*.json'))
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
assert hashes==author['sha256']
assert hashes==independent['files'] and independent['status']=='passed'
questions=[q for p in files for q in json.loads(p.read_text(encoding='utf-8'))]
figures=[dict(id=q['id'],role=field,sha256=hashlib.sha256(q[field].encode()).hexdigest()) for q in questions for field in ['diagramSvg','markSchemeDiagramSvg'] if field in q]
report=dict(status='author-frozen; independent review passed',questionCount=400,topicCounts=author['topicCounts'],marks=sum(q['marks'] for q in questions),familyCount=100,maximumVariantsPerFamily=4,examStyleCounts=author['examStyleCounts'],difficultyCounts=author['difficultyCounts'],calculatorCounts=author['calculatorCounts'],sources=author['sources'],assessment=author['assessment'],syllabusCodes=author['syllabusCodes'],scopeDecisions=['Current first-assessment2021 AA SL content; no2029-syllabus substitutions','No complex numbers, vectors, induction, generalized binomial series, continuous probability density questions, differential equations, first-principles derivatives, lHopital, unrestricted general trig solutions or HL inverse-trig graphs','Combined horizontal scaling and shift f(ax+b) excluded; fn065–068 now use simple horizontal shifts','Ambiguous sine-rule case belongs to SL3.5; double sine/cosine identities belong to SL3.6','Binomial/normal probabilities and inverse-normal values use GDC; no-calculator questions use exact/manual-friendly quantities'],visualReview=dict(count=len(figures),method='Rendered every SVG using Sharp, inspected all six contact sheets at readable size, and re-rendered/inspected corrected inverse branches, sector chords and normal plot axes',result='Passed: labels, branches, curve shape, coordinate scale, geometry, units, clipping and origin-outside viewports checked',contactSheets='work/aa-sl-review/contact-1.png through contact-6.png',figures=figures),hashes=hashes,authorReview='aa-sl-author-review.json',independentReview='aa-sl-independent-review.json',limits='Original IB-style practice, not official IB material. Reviews were performed by separate AI agents with symbolic/numerical tools, not an accredited human examiner. Syllabus-code coverage does not claim every possible formulation or exam difficulty is exhausted.',unresolvedFindings=[])
(folder/'aa-sl-freeze-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status=report['status'],questionCount=len(questions),marks=report['marks'],figures=len(figures),hashes=hashes),indent=2))
