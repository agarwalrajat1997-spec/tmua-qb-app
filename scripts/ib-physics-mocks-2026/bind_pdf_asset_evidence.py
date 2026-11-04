"""Revalidate the complete scientific asset chain and bind portable PDF evidence.

No PDF bytes are changed. This supports build ledgers made before the portable
asset-report digest field was introduced, without inventing a new visual review.
"""
from pathlib import Path
import os,json,hashlib
ROOT=Path(__file__).resolve().parents[2];WORK=Path(os.environ.get('IB_PHYSICS_MOCK_WORK',ROOT.parent/'physics-mocks-2026'));DOC=ROOT/'docs/ib-physics-mocks-2026'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
assets=WORK/'pdf-assets';manifest=json.loads((assets/'manifest.json').read_text(encoding='utf8'));report_path=DOC/'math-assets-checks.json';scientific=json.loads(report_path.read_bytes());report_sha=sha(report_path.read_bytes())
assert scientific['status']=='passed' and scientific['papers']==manifest['sourcePapers'] and scientific['diagrams']==manifest['diagramChecks']
ledger_path=DOC/'pdf-checks.json';ledger=json.loads(ledger_path.read_bytes());figures=0
for row in ledger['papers']:
    raw=(ROOT/'content/ib/physics-mocks-2026/papers'/(row['id']+'.json')).read_bytes();paper=json.loads(raw)
    assert sha(raw)==row['canonicalQuestionSha256']==manifest['sourcePapers'][row['id']]
    pdf=(ROOT/'public/ib-mock-solutions'/(row['id']+'.pdf')).read_bytes();assert sha(pdf)==row['sha256'] and len(pdf)==row['bytes']
    for question in paper['questions']:
        if not question.get('diagramSvg'):continue
        evidence=manifest['diagramChecks'][question['id']]
        assert evidence['svgSha256']==sha(question['diagramSvg'].encode('utf8'))
        assert evidence['pngSha256']==sha((assets/manifest['diagrams'][question['id']]).read_bytes())
        figures+=1
    row['scientificAssetReportSha256']=report_sha
    row['portableEvidenceValidation']='Canonical content, scientific report/scratch manifest, actual SVG and PNG bytes, and unchanged final PDF SHA-256 all revalidated.'
assert len(ledger['papers'])==10 and figures==scientific['diagramCount']
ledger_path.write_text(json.dumps(ledger,indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps({'status':'passed','unchangedPdfs':len(ledger['papers']),'revalidatedDiagrams':figures,'scientificAssetReportSha256':report_sha}))
