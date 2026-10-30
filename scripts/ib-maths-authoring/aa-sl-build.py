"""Canonical deterministic authoring entrypoint for the AA SL bank.
Run with the bundled Python; workspace dependency location is in aa_sl_core.py.
"""
from aa_sl_core import *
import aa_sl_na, aa_sl_fn, aa_sl_gt, aa_sl_sp, aa_sl_ca

for topic,module in [('number-algebra',aa_sl_na),('functions',aa_sl_fn),('geometry-trigonometry',aa_sl_gt),('statistics-probability',aa_sl_sp),('calculus',aa_sl_ca)]:
 save(topic,module.build())

folder=ROOT/'docs'/'ib-maths-reviews';folder.mkdir(parents=True,exist_ok=True)
files=sorted((ROOT/'content'/'ib'/'math-aa-sl').glob('*.json'))
records=[q for path in files for q in json.loads(path.read_text(encoding='utf-8'))]
assert len(records)==400 and len(LEDGER)==400
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
report=dict(course='Mathematics: analysis and approaches SL',syllabus='First assessment2021; current through final assessment2028',provenance='Original independently authored practice. No copied examination wording or artwork.',assessment=dict(paper1='No calculator;90 minutes;80 marks;short and extended written response',paper2='GDC required;90 minutes;80 marks;short and extended written response',paper3='Not an AA SL assessment'),sources=[dict(title='Official AA guide, first assessment2021',url='https://www.ibo.org/globalassets/new-structure/university-admission/pdfs/dp-mathematics-analysis-and-approaches-guide-en.pdf'),dict(title='Official AA specimen papers, first examinations2021',url='https://www.ibo.org/globalassets/new-structure/university-admission/pdfs/dp-mathematics-analysis-and-approaches-specimen-papers-en.pdf')],count=len(records),topicCounts=dict(Counter(q['topicId'] for q in records)),difficultyCounts=dict(Counter(q['difficulty'] for q in records)),calculatorCounts=dict(Counter(str(q['calculator']) for q in records)),examStyleCounts=dict(Counter(q['examStyle'] for q in records)),familyCount=len(set(z['family'] for z in LEDGER)),maximumVariantsPerFamily=max(Counter(z['family'] for z in LEDGER).values()),questionDiagrams=sum('diagramSvg'in q for q in records),markSchemeDiagrams=sum('markSchemeDiagramSvg'in q for q in records),syllabusCodes={topic:sorted(set(q['syllabusCode'] for q in records if q['topicId']==topic),key=lambda z:tuple(map(int,z.split('.')))) for topic in Counter(q['topicId'] for q in records)},sha256=hashes,verification='Every record has explicit marking points,scope/calculator review and a traceable family. Generator assertions check symbolic identities, substitution, exact sums, numerical residuals, distribution probabilities, integer boundaries and diagram coordinates. Separate AA SL independent verification report also required before publication.',ledger=sorted(LEDGER,key=lambda z:z['id']))
(folder/'aa-sl-author-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['ledger','sources','assessment','verification']},indent=2))
