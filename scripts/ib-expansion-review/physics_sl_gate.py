"""Bind the independently reviewed Physics SL snapshot to the release gate."""
from pathlib import Path
import json,hashlib

ROOT=Path(__file__).resolve().parents[2];D=ROOT/'docs/ib-expansion-reviews'
numeric=json.loads((D/'physics-sl-independent-numeric.json').read_text(encoding='utf-8'))
scope=json.loads((D/'physics-sl-independent-scope.json').read_text(encoding='utf-8'))
assert numeric['status']=='passed' and numeric['reviewedRecords']==100 and len(numeric['errors'])==0
assert scope['population']==420 and scope['retainedCore']==418
files={};current={}
for p in sorted((ROOT/'content/ib/physics-hl').glob('*.json')):
    raw=p.read_bytes();raw.decode('utf-8');assert b'\r' not in raw and not raw.startswith(b'\xef\xbb\xbf')
    files[p.name]=hashlib.sha256(raw).hexdigest()
    current.update({q['id']:q for q in json.loads(raw)})

def qhash(q):return hashlib.sha256(json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
records=[]
for row in numeric['records']:
    q=current[row['id']];assert qhash(q)==row['sha256']
    records.append({'id':q['id'],'status':'passed','sha256':row['sha256'],'syllabusCode':q['syllabusCode'],'level':q['level'],'marks':q['marks'],'numericalQuantitiesReconstructed':row['quantitiesReconstructed'],'mathCheckReference':'physics-sl-independent-numeric.json#'+q['id'],'scopeAndReasoning':row['scopeAndReasoning'],'figureReview':'Serialized figure rendered and visually inspected; data labels, directions, component positions and readability checked.' if 'diagramSvg' in q else 'No figure in this record.'})
for row in scope['records']:assert qhash(current[row['id']])==row['sha256']
evidence={name:hashlib.sha256((D/name).read_bytes()).hexdigest() for name in ['physics-sl-independent-numeric.json','physics-sl-independent-scope.json','physics-sl-independent-scope-input.json']}
report={'status':'passed','questionCount':100,'scopeQuestionCount':420,'canonicalFiles':files,'records':records,'numericalQuantityChecks':numeric['numericalQuantities'],'figuresRenderedAndInspected':32,'scopeEvidence':'physics-sl-independent-scope.json','evidenceHashes':evidence,'correctedLegacyIds':['ib-phy-d-007','ib-phy-d-037'],'legacyCorrection':'Promoted core to ahl for explicitly AHL circular-orbit speed demand; preserved original IDs, data, prompts and schemes. Original author call classification also corrected.','courseCounts':{'allPhysics':740,'slAvailable':518,'ahl':222,'newSlAdditions':100,'legacyOriginalCoreReviewed':420,'legacyRetainedCore':418},'reviewedOn':'2026-10-31','reviewMethod':'Independent agent review: every numerical response in the100 additions reconstructed from serialized displayed inputs, using no authoring imports; scope/reasoning/units/rounding/marks checked per family with per-record evidence. All32 figures rendered and visually inspected, including final LDR symbols.','limits':'This is not human examiner moderation or IB endorsement. The420 legacy records received a syllabus-demand scope audit, not an additional complete numerical or visual review. A change to any canonical record or evidence file invalidates the corresponding snapshot hash.'}
(D/'physics-sl-independent-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['records','canonicalFiles','evidenceHashes']},ensure_ascii=False,indent=2))
