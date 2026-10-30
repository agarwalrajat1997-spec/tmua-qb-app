"""Reproduce the original 160-question Biology Theme B collection."""
import hashlib
import random
from form_function_common import *
from form_function_b1 import add_b11,add_b12
from form_function_b2 import add_b21,add_b22,add_b23
from form_function_b3 import add_b31,add_b32,add_b33
from form_function_b4 import add_b41,add_b42

b=Bank()
for add in (add_b11,add_b12,add_b21,add_b22,add_b23,add_b31,add_b32,add_b33,add_b41,add_b42):add(b)

# Explicit syllabus breadth at the appropriate course level.
b.extend(7,P('Relate these surface carbohydrate differences to ABO blood groups.',A('A and B blood-group antigens differ in their exposed carbohydrate structures on red blood cell surface glycoproteins and glycolipids.')))
b.extend(37,P('On a copy of this membrane scheme, add a glycoprotein and a cholesterol molecule in biologically appropriate positions.',A('A carbohydrate chain is attached to a membrane protein on the extracellular face.'),A('Cholesterol is positioned among the phospholipid tails within the bilayer, with its small polar region near the heads.')))
b.questions[36]['markSchemeDiagramSvg']=worked_membrane_svg()
b.extend(40,P('State the function of aquaporins and whether they directly use ATP for water passage.',A('Aquaporins provide membrane channels that allow water to pass rapidly; movement through an open aquaporin is passive and does not directly consume ATP.')))
b.extend(110,P('Explain the function of the septum separating the left and right sides of the heart.',R('It prevents mixing between the two sides, helping maintain distinct pulmonary and systemic blood circuits.')))
b.extend(110,P('State the position and role of the sinoatrial node.',A('The sinoatrial node is in the wall of the right atrium.'),A('It acts as the normal pacemaker, initiating electrical excitation that coordinates the heartbeat.')))
b.extend(111,P('Outline the order of atrial and ventricular contraction after excitation begins at the sinoatrial node.',A('Excitation spreads through the atria so they contract before the ventricles.'),A('A delay at the atrioventricular node allows ventricular filling before excitation leads to ventricular contraction and, once pressure is sufficient, ejection.')))
b.extend(127,P('Explain how the position and closure of the nostril or blowhole can assist life in water.',A('An opening high on the head permits breathing at the surface with little of the body exposed.'),A('Closure during a dive limits water entry into the airways.')))
b.extend(151,P('Distinguish an obligate aerobe from a facultative anaerobe.',A('An obligate aerobe requires oxygen for growth under the relevant conditions.'),A('A facultative anaerobe can obtain energy and grow with or without oxygen, using alternative pathways when oxygen is absent.')))

# Asset is recorded by content hash in the shared, reviewed provenance registry.
registry=json.loads((ROOT/'content/ib/biology-image-sources.json').read_text(encoding='utf8'))
asset=next(a for a in registry['assets'] if any(u['id']=='ib-bio-b-085' for u in a['uses']))
b.questions[84]['diagramUrl']=asset['url'];b.questions[84]['diagramCaption']=asset['caption']
for q in b.questions:
    if 'diagramSvg' in q:q['diagramCaption']='Original schematic illustration.'
    if 'markSchemeDiagramSvg' in q:q['markSchemeDiagramCaption']='Original worked schematic illustration.'
b.questions[140]['diagramCaption']='Original graph of the constructed data supplied in the question.'

# Difficulty reflects the inference/design required, independently of SL/AHL scope.
hard={15,16,31,32,39,47,51,63,80,94,96,103,111,122,136,141,142,143,144,154,158,159,160}
for q in b.questions:
    if q['number'] in hard:q['difficulty']='hard'
    if q['number'] in {50,67,116,132}:q['difficulty']='medium'

# Replace conspicuously impossible distractors with plausible conceptual errors.
replacements={
1:['It can form four covalent bonds but cannot bond to another carbon atom.','It forms only straight unbranched chains with other carbon atoms.','Its bonds to other carbon atoms must all be double bonds.'],
2:['A glycosidic bond forms and a water molecule is consumed.','A peptide bond forms and a water molecule is released.','A glycosidic bond is broken and a water molecule is consumed.'],
3:['It is large and insoluble in water.','It is small and largely insoluble in water.','It is a branched polymer with a low osmotic effect.'],
17:['The amino group shared by the general amino-acid structure.','The carboxyl group shared by the general amino-acid structure.','The hydrogen atom bonded to the central carbon.'],
33:['A sodium ion moving directly through the lipid interior.','A glucose molecule moving directly through the lipid interior.','An amino acid in its charged form moving directly through the lipid interior.'],
35:['A peripheral protein always spans the entire bilayer.','A peripheral protein forms the hydrophobic core of every phospholipid.','A peripheral protein must be covalently attached to a carbohydrate chain.'],
81:['The rate of diffusion increases indefinitely with the total body volume.','All cells in a large animal are the same short distance from its outer surface.','A large animal has a higher external surface-area-to-volume ratio than a geometrically similar smaller animal.'],
82:['A large, thick surface with maintained gradients.','A thin surface with the same gas concentration on both sides.','A small, dry surface with a long diffusion path.'],
83:['The diaphragm relaxes, thoracic volume decreases and air enters.','The diaphragm contracts, thoracic volume decreases and air enters.','The diaphragm contracts, lung pressure rises above atmospheric pressure and air enters.'],
97:['A thick layer of smooth muscle around the endothelium.','A thick multilayered elastic wall.','A very large distance between blood and surrounding tissue fluid.'],
98:['A thin wall with little supporting tissue and no elastic recoil.','A lumen containing paired valves at regular intervals in all systemic arteries.','A wall designed mainly for exchange directly across a single endothelial layer.'],
}
for number,wrongs in replacements.items():
    q=b.questions[number-1];correct=next(o['text'] for o in q['options'] if o['label']==q['correctOption'])
    q['options']=[{'label':k,'text':v} for k,v in zip('ABCD',[correct]+wrongs)];q['correctOption']='A'

# A balanced shuffled answer pool is reproducible without a visible cyclic pattern.
mcqs=[q for q in b.questions if q['questionType']=='multiple-choice']
pool=list(('ABCD'*((len(mcqs)+3)//4))[:len(mcqs)])
rng=random.Random('biology-form-function-original-2026');rng.shuffle(pool)
for q,key in zip(mcqs,pool):
    correct=next(o['text'] for o in q['options'] if o['label']==q['correctOption'])
    wrongs=[o['text'] for o in q['options'] if o['label']!=q['correctOption']];rng.shuffle(wrongs)
    values=iter(wrongs);q['options']=[{'label':k,'text':correct if k==key else next(values)} for k in 'ABCD']
    q['correctOption']=key
    q['markScheme'][0]['steps'][0]['text']=key+'. '+q['markScheme'][0]['steps'][0]['text'].split('. ',1)[1]

b.save()

# Factual scope map points to each original competency family, not copied guide text.
blueprint=json.loads((ROOT/'docs/ib-biology-reviews/syllabus-blueprint.json').read_text(encoding='utf8'))
scope=[]
for t in blueprint['topics']:
    if not t['code'].startswith('B'):continue
    qs=[q for q in b.questions if q['syllabusCode']==t['code']]
    scope.append({'code':t['code'],'sharedStatementRange':t['slStatements'],'additionalHlStatementRange':t['additionalHlStatements'],'sharedConcepts':t['sharedConcepts'],'additionalHlConcepts':t['additionalHlConcepts'],'guidePrintedPages':t['guidePrintedPages'],'questionMap':[{'id':q['id'],'level':q['level'],'competency':q['title']} for q in qs]})
report_path=ROOT/'docs/ib-biology-reviews/form-function-author.json'
report=json.loads(report_path.read_text(encoding='utf8'))
report.update(statementMap=scope,primarySources=blueprint['primarySources'],mcqKeys=dict(Counter(q['correctOption'] for q in mcqs)),difficulty=dict(Counter(q['difficulty'] for q in b.questions)),illustrativeAsset={'id':'ib-bio-b-085','sha256':asset['sha256'],'caption':asset['caption']},namedExampleSources=[{'url':'https://www.nps.gov/tont/learn/nature/saguaro.htm','supports':'Saguaro shallow radial roots and expandable water-storage pleats; independently worded q139.'},{'url':'https://www.nparks.gov.sg/florafaunaweb/flora/2/7/2797','supports':'Ceiba pentandra tall growth and buttresses; independently worded q140.'}],records=[{'id':q['id'],'sha256':hashlib.sha256(json.dumps(q,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()} for q in b.questions])
report['namedExampleSources'].append({'url':'https://plants.usda.gov/DocumentLibrary/factsheet/pdf/fs_avge.pdf','supports':'Black mangrove Avicennia germinans leaf salt glands and pneumatophores; independently worded q134.'})
independent_path=ROOT/'docs/ib-biology-reviews/theme-b-independent-review.json'
if independent_path.exists():
    signed=json.loads(independent_path.read_text(encoding='utf8'))
    current_hash=hashlib.sha256((ROOT/'content/ib/biology/form-function.json').read_bytes()).hexdigest()
    if signed.get('status')=='passed' and signed.get('questionJsonSha256')==current_hash:
        report['reviewStatus']='Author and independent review passed for all 160 records; see docs/ib-biology-reviews/theme-b-independent-review.json.'
report['numericalCheckReport']='docs/ib-biology-reviews/form-function-author-checks.json'
report['independentReviewReport']='docs/ib-biology-reviews/theme-b-independent-review.json'
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Added scope ledger, shuffled MCQ distribution, explicit course-independent difficulty and external illustration provenance.')
