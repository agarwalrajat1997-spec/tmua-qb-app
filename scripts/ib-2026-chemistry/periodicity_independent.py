"""Independent chemical/numerical reproducer for all thirty S3 additions.

Run from any directory with RDKit available (ordinary installation or PYTHONPATH):
    python scripts/ib-2026-chemistry/periodicity_independent.py
Add --write-review only after a fresh human/agent read-through to bind the review.
The normal command is read-only. It does not rerun the authoring script.
"""
import json,math,re,sys,hashlib
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit.Chem.EnumerateStereoisomers import EnumerateStereoisomers,StereoEnumerationOptions
ROOT=Path(__file__).resolve().parents[2]
BATCH=ROOT/'content/ib/chemistry-2026-expansion/periodicity.json'
REVIEW=ROOT/'docs/ib-2026-chemistry/periodicity-independent-review.json'
questions=json.loads(BATCH.read_text(encoding='utf8'));byid={q['id']:q for q in questions};records=[]
assert len(questions)==30 and len(byid)==30
assert sum(q['level']=='sl' for q in questions)==12
assert sum(q['level']=='ahl' for q in questions)==18
def C(label,actual,expected,tolerance=1e-9):
 if isinstance(actual,(str,list,tuple,dict)):
  assert actual==expected,(label,actual,expected)
 else:assert abs(actual-expected)<=tolerance*max(1,abs(expected)),(label,actual,expected)
 return {'type':'independent calculation','check':label,'actual':actual,'expected':expected,'tolerance':tolerance}
def F(smiles,expected):
 mol=Chem.MolFromSmiles(smiles);assert mol is not None,smiles;Chem.SanitizeMol(mol)
 formula=rdMolDescriptors.CalcMolFormula(mol);assert formula==expected,(smiles,formula,expected)
 return {'type':'independent molecular structure','smiles':smiles,'formula':formula,'valenceSanitization':'passed','formalCharge':Chem.GetFormalCharge(mol)}
def electron(z,charge):return z-charge
def parse_formula(formula):
 f=formula.split('^')[0];tokens=re.findall(r'[A-Z][a-z]?|\d+|[()]',f);stack=[{}];i=0
 while i<len(tokens):
  tok=tokens[i];i+=1
  if tok=='(':stack.append({});continue
  if tok==')':
   group=stack.pop();n=int(tokens[i]) if i<len(tokens) and tokens[i].isdigit() else 1
   if i<len(tokens) and tokens[i].isdigit():i+=1
   for a,c in group.items():stack[-1][a]=stack[-1].get(a,0)+c*n
  else:
   n=int(tokens[i]) if i<len(tokens) and tokens[i].isdigit() else 1
   if i<len(tokens) and tokens[i].isdigit():i+=1
   stack[-1][tok]=stack[-1].get(tok,0)+n
 assert len(stack)==1
 return stack[0]
def species_charge(f):
 if '^' not in f:return 0
 p=f.split('^')[1];return(-1 if p.endswith('-') else 1)*int(p[:-1] or 1)
def B(left,right):
 def total(side):
  a={};charge=0
  for formula,n in side.items():
   charge+=species_charge(formula)*n
   for e,c in parse_formula(formula).items():a[e]=a.get(e,0)+n*c
  return a,charge
 a,charge=total(left);assert(a,charge)==total(right),(left,right,total(left),total(right))
 return {'type':'independent atom-charge conservation','left':left,'right':right,'atoms':a,'charge':charge}
def R(number,note,*checks):
 q=byid[f'ib-chem-s3-{number}']
 assert q['marks']==sum(p['marks'] for p in q['parts'])==sum(sum(int(s['code'][1:]) for s in g['steps']) for g in q['markScheme'])
 assert q['number']==q['source']['question']==number
 assert all(p['marks']==sum(int(s['code'][1:]) for s in next(g for g in q['markScheme'] if g['part']==p['label'])['steps']) for p in q['parts'])
 records.append({'id':q['id'],'status':'passed','contentSha256':hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest(),'chemicalScopeAndReasoning':note,'independentChecks':checks,'marking':'Question-specific allocations and per-part totals checked; correct alternatives/consistent ECF remain appropriate. These are instructional analytic schemes, not official IB marking.','visualReview':'Inspected in three S3 full-bank contact sheets: connectivity/charge, spectral axes, whole-multiplet areas, stereochemical wedges, dipole-displacement directions and supplied-data labels agree with the question.'})

R(701,'An isoelectronic comparison retains occupied shells; neutral Na is a different-shell comparison. Ionic mobility explains solid/molten contrast.',C('ion electron counts',[electron(z,ch) for z,ch in [(8,-2),(9,-1),(11,1),(12,2),(13,3)]],[10]*5),C('alumina charge',2*3+3*(-2),0))
assert 'intermediate carrier' not in ' '.join(s['text'] for g in byid['ib-chem-s3-702']['markScheme'] for s in g['steps'])
R(702,'Cl2>Br2>I2 oxidising order follows the two displacement observations. Br- is consumed then regenerated, so the final text correctly calls it a regenerated carrier rather than a produced-then-consumed intermediate.',B({'Cl2':1,'Br^-':2},{'Cl^-':2,'Br2':1}),B({'Br2':1,'I^-':2},{'Br^-':2,'I2':1}),B({'Cl2':1,'I^-':2},{'Cl^-':2,'I2':1}),C('two-stage halogen amount',.0100*1*1,.0100))
x=(5.0834-40.30*.1100)/(61.98-40.30);y=.1100-x
R(703,'Both basic oxides consume two acid equivalents, so mass supplies the independent composition constraint. The calculated positive composition reproduces both observations.',B({'Na2O':1,'HCl':2},{'NaCl':2,'H2O':1}),B({'MgO':1,'HCl':2},{'MgCl2':1,'H2O':1}),C('Na2O amount',x,.03),C('MgO amount',y,.08),C('Na2O percentage',100*x*61.98/5.0834,36.57788094582368,1e-6))
R(704,'The continuous Si-O network is a supplied counterexample to defining acidity by water reaction; oxide/base reaction balances, and molten ionic versus molecular liquid charge carriers differ.',B({'SiO2':1,'NaOH':2},{'Na2SiO3':1,'H2O':1}),C('silicon valence coordination in stated network',4,4),F('O=S=O','O2S'))
np=.1135/22.70*2;no=(2.0194-np*77.98)/61.98
R(705,'Peroxide oxygen starts at-1 and partitions into reduced hydroxide oxygen and oxidised O2. Dry gas and water-loss assumptions are explicit.',B({'Na2O2':2,'H2O':2},{'NaOH':4,'O2':1}),C('peroxide amount',np,.01),C('oxide amount',no,.02),C('peroxide mass percentage',np*77.98/2.0194*100,38.61543032583936,1e-6),C('NaOH total',2*(np+no),.06))
alcs=['CCCCO','CCC(O)C','CC(C)CO','CC(C)(C)O']
def alcohol_class(smiles):
 m=Chem.MolFromSmiles(smiles);o=next(a for a in m.GetAtoms() if a.GetSymbol()=='O' and a.GetTotalNumHs()==1);c=o.GetNeighbors()[0]
 return sum(a.GetSymbol()=='C' for a in c.GetNeighbors())
R(706,'Four alcohol connectivities/classes are correct; tertiary retains an OH donor. Added mixture part has two valid class-pair possibilities and cannot identify which of the two primary connectivities is present.',*(F(m,'C4H10O') for m in alcs),C('OH-bearing carbon neighbour counts',[alcohol_class(m) for m in alcs],[1,2,1,3]),C('primary+secondary moles',.005+.015,.020),C('primary+secondary oxygen equivalents',2*.005+.015,.025),C('primary+tertiary moles',.0125+.0075,.020),C('primary+tertiary oxygen equivalents',2*.0125,.025),C('two-primary mismatch',2*.02,.04))
R(707,'Hex-1-ene and cyclohexane share C6H12 but differ in connectivity and functional class. Bromine adds across the terminal double bond without changing carbon count.',F('C=CCCCC','C6H12'),F('C1CCCCC1','C6H12'),F('BrCC(Br)CCCC','C6H12Br2'),C('combustion carbon count',.06/.01,6),C('combustion H count',2*.06/.01,12))
R(708,'Propanoic acid and ethyl methanoate are same-formula acid/ester isomers; selective CO2 determines the acid fraction. Hydrolysis products individually have different formulas and are not isomers of the original acid.',F('CCC(=O)O','C3H6O2'),F('CCOC=O','C3H6O2'),F('O=CO','CH2O2'),F('CCO','C2H6O'),C('acid mole fraction',(.1362/22.70)/(.7400/74),.6),B({'C3H6O2':1,'H2O':1},{'CH2O2':1,'C2H6O':1}))
R(709,'The pictured chain has six carbons and lower alkene locant2, then bromo locant4. A drawing reversal preserves connectivity; moving Br creates a positional isomer.',F('CC=CC(Br)CC','C6H11Br'),F('BrCC=CCCC','C6H11Br'),C('hydrogen count from monobromo monoalkene',2*6-1,11))
R(710,'Alcohol/ether donor versus acceptor distinction is correct. Ethane-1,2-diol has more OH groups and more electrons, so bulk boiling cannot isolate individual hydrogen-bond strength.',F('CCO','C2H6O'),F('COC','C2H6O'),F('OCCO','C2H6O2'),C('ethanol/ether molar mass equality',2*12+6+16,46),C('diol oxygen count',len([a for a in Chem.MolFromSmiles('OCCO').GetAtoms() if a.GetSymbol()=='O']),2))
amines=['CCCN','CCNC','CN(C)C']
def n_counts(smiles):
 m=Chem.MolFromSmiles(smiles);a=next(a for a in m.GetAtoms() if a.GetSymbol()=='N');return(sum(n.GetSymbol()=='C' for n in a.GetNeighbors()),a.GetTotalNumHs())
R(711,'Primary/secondary/tertiary classify carbon groups on nitrogen, not pre-existing N-H bonds. Each nitrogen accepts one proton at its lone pair.',*(F(m,'C3H9N') for m in amines),C('carbon-neighbour and N-H counts',[n_counts(m) for m in amines],[(1,2),(2,1),(3,0)]),C('HCl needed',.2955/59.10,.005))
R(712,'Pentanol and tertiary 2-methylbutan-2-ol classes agree with the drawings. Identical formula means combustion ratios cannot measure composition; the supplied selective covalent reaction can.',F('CCCCCO','C5H12O'),F('CCC(C)(C)O','C5H12O'),C('classes',[alcohol_class('CCCCCO'),alcohol_class('CCC(C)(C)O')],[1,3]),C('A mass',.006*88.15,.5289),C('B mass',.004*88.15,.3526))
R(713,'The two ionisation reversals are specific sublevel and electron-pairing effects; the next-ionisation species differs. Na+ removes a core n2 electron and has the greatest second IE in this period.',C('Mg-to-Al step',578-738,-160),C('P-to-S step',1000-1012,-12),C('Na+ total electrons',11-1,10),C('period3 valence/core distinction',3-2,1))
R(714,'Fe loses4s before3d, giving d6/d5; supplied redox steps regenerate iron and sum to the peroxodisulfate/iodide reaction. No detailed catalytic mechanism is required from memory.',B({'Fe^3+':2,'I^-':2},{'Fe^2+':2,'I2':1}),B({'Fe^2+':2,'S2O8^2-':1},{'Fe^3+':2,'SO4^2-':2}),B({'S2O8^2-':1,'I^-':2},{'SO4^2-':2,'I2':1}),C('Fe2+ d count',26-18-2,6),C('Fe3+ d count',26-18-3,5))
h=6.63e-34;c=3e8;NA=6.02e23
R(715,'Cu2+ remains d9. Shorter450nm absorption implies larger splitting. Complementary colours are explicitly simplified in the question; full real spectra are not overclaimed.',C('Cu2+ d count',29-18-2,9),C('650nm photon molar kJ',h*c*NA/(650e-9)/1000,184.21199999999996),C('450nm photon molar kJ',h*c*NA/(450e-9)/1000,266.084),C('energy ratio',(h*c/(450e-9))/(h*c/(650e-9)),650/450))
det=.2*.1-.6*.8;a=(.340*.1-.6*.440)/det;b=(.2*.440-.340*.8)/det
R(716,'Neutral ligands leave oxidation states+2; d9 Cu and d8 Ni are correct. Two independent absorbances determine two positive concentrations under the explicitly supplied linear calibration rule.',C('A concentration mmol dm-3',a,.5),C('B concentration mmol dm-3',b,.4),C('450nm closure',.2*a+.6*b,.340),C('650nm closure',.8*a+.1*b,.440),C('Ni2+ d count',28-18-2,8))
R(717,'Four ammine ligands consume four protons and four additional water ligands. Atom/charge balance and unchanged CuII/d9 distinguish ligand exchange from redox.',B({'Cu(NH3)4(H2O)2^2+':1,'H^+':4,'H2O':4},{'Cu(H2O)6^2+':1,'NH4^+':4}),C('minimum H+',4*.00250,.0100),C('copper d count before/after',29-18-2,9))
R(718,'MnVII is d0, so supplied ligand-to-metal charge transfer is needed for this counterexample to a d-d-only rule. Manganese still qualifies by ions such as MnII/d5; low blue/red absorption matches purple transmission.',C('Mn oxidation state',-1-4*(-2),7),C('MnVII d electrons',25-18-7,0),C('MnII d electrons',25-18-2,5),C('outer spectral regions less absorbed',.1<.9 and .1<.7,True))
amount=(.26845-.01802)/250.43
R(719,'Dry mass establishes formula-unit amount, water loss determines one lattice water, immediate chloride shows two counterions and total chloride shows one coordinated ligand. CoIII/d6 and coordination6 agree.',C('formula-unit amount',amount,.001),C('water count',(.01802/18.02)/amount,1),C('free Cl per formula',(.28664/143.32)/amount,2),C('total Cl per formula',(.42996/143.32)/amount,3),C('CoIII d count',27-18-3,6),C('coordination number',5+1,6))
R(720,'Ester identity is supported by every NMR integral/splitting and absent acid OH. Acylium43 plus ethoxy radical45 conserves atoms, mass and charge.',F('CC(=O)OCC','C4H8O2'),B({'C4H8O2^+':1},{'C2H3O^+':1,'C2H5O':1}),C('molecular mass',4*12+8+2*16,88),C('fragment sum',43+45,88),C('NMR total H',3+2+3,8))
R(721,'Propanone has two symmetry-equivalent methyl groups and no adjacent carbonyl H; propanal would have an aldehyde proton and multiple environments. Fragment43 alone uses mass balance, not unprovided mechanistic detail.',F('CC(=O)C','C3H6O'),F('CCC=O','C3H6O'),B({'C3H6O^+':1},{'C2H3O^+':1,'CH3':1}),C('fragment sum',43+15,58),C('equivalent methyl H',2*3,6))
R(722,'Diethyl ether has two environments with6:4 total areas, not a line-height count. Other candidate ethers have inequivalent group sets; butanol is an isomer and has an OH IR band.',F('CCOCC','C4H10O'),F('COCCC','C4H10O'),F('COC(C)C','C4H10O'),F('CCCCO','C4H10O'),C('integrated H',6+4,10))
R(723,'Chlorine binomial isotope selection gives9:6:1; the3H doublet/1H quartet picks1,1-dichloroethane. Both connectivities share the same isotope cluster.',F('CC(Cl)Cl','C2H4Cl2'),F('ClCCCl','C2H4Cl2'),C('two-35Cl probability',.75**2,9/16),C('mixed isotope probability',2*.75*.25,6/16),C('at least one37Cl',1-.75**2,7/16),C('light molecular mass',2*12+4+2*35,98))
R(724,'The two ethyl groups are inequivalent: one is next to C=O, one next to O. Both CH2 signals are quartets; the alternatives require absent singlets. Acylium57/ethoxy45 conservation is exact.',F('CCC(=O)OCC','C5H10O2'),B({'C5H10O2^+':1},{'C3H5O^+':1,'C2H5O':1}),C('fragment mass sum',57+45,102),C('total NMR H',3+3+2+2,10))
ma=Chem.MolFromSmiles('C[C@H](O)CC');mb=Chem.MolFromSmiles('C[C@@H](O)CC')
R(725,'Wedge/dash drawings encode opposite arrangements at one stereogenic carbon. Optical rotation, not ordinary achiral IR or boiling point, measures the non-racemic composition under the supplied linear rule.',F('C[C@H](O)CC','C4H10O'),F('C[C@@H](O)CC','C4H10O'),C('one stereogenic centre',len(Chem.FindMolChiralCenters(ma,includeUnassigned=True)),1),C('opposite canonical stereostructures differ',Chem.MolToSmiles(ma,True)!=Chem.MolToSmiles(mb,True),True),C('A fraction',(3+12)/24,.625),C('rotation closure',.625*12+.375*(-12),3))
R(726,'But-2-ene has H/methyl differences at each double-bond carbon and permits cis/trans; terminal but-1-ene does not. A pi bond constrains rotation, while positional change alters connectivity.',F('C/C=C/C','C4H8'),F('C/C=C\\C','C4H8'),F('C=CCC','C4H8'),C('same nominal molecular mass',4*12+8,56))
opts=StereoEnumerationOptions(onlyUnassigned=True,maxIsomers=16)
def stereo_count(smiles):return len(tuple(EnumerateStereoisomers(Chem.MolFromSmiles(smiles),options=opts)))
R(727,'Distinct connectivity stereocounts are2,2,1: A has chirality but terminal double bond, B has one geometric pair, C has neither. Bromine isotope appearance cannot settle connectivity.',F('C=CC(Br)C','C4H7Br'),F('CC=CCBr','C4H7Br'),F('C=C(Br)CC','C4H7Br'),C('stereoisomer counts',[stereo_count(m) for m in ['C=CC(Br)C','CC=CCBr','C=C(Br)CC']],[2,2,1]),C('total count',2+2+1,5))
R(728,'The supplied dipole-change criterion, not a permanent dipole, governs IR activity. Arrow directions depict symmetric/asymmetric/bending displacements consistently; the conversion from cm-1 to micrometres uses10000.',C('2349cm-1 wavelength micrometre',10000/2349,4.257130693912303,1e-7),C('667cm-1 wavelength micrometre',10000/667,14.992503748125937),C('interval inclusion',5<=10000/667<=30,True))
R(729,'Two independent whole-area comparisons both give ethanol:ethanal3:2. Aldehyde quartet and methyl doublet follow neighbouring-H counts. IR depths lack a common calibration for mixture quantification.',F('CCO','C2H6O'),F('CC=O','C2H4O'),C('methyl ratio',(9/3)/(6/3),1.5),C('CH2/CHO ratio',(6/2)/(2/1),1.5),C('mixture amount',.006+.004,.010),C('sample mass',.006*46.07+.004*44.05,.45262))
R(730,'Two equivalent methyl groups plus methine and exchangeable OH account for all8H in propan-2-ol. CH splitting is explicitly unresolved, so no out-of-scope higher multiplet interpretation is required;43+17 fragmentation is not unique to an isomer.',F('CC(O)C','C3H8O'),F('CCCO','C3H8O'),B({'C3H8O^+':1},{'C3H7^+':1,'OH':1}),C('H reconciliation',6+1+1,8),C('fragment mass balance',43+17,60))

assert len(records)==30 and {r['id'] for r in records}==set(byid)
rawsha=hashlib.sha256(BATCH.read_bytes()).hexdigest()
report={'status':'passed','questions':30,'sha256':rawsha,'reviewer':'Independent Reactivity author agent; not the S3 question author','reviewDate':'2026-11-03','records':records,'checks':sum(len(r['independentChecks']) for r in records),'officialGuide':'https://www.ibo.org/globalassets/new-structure/university-admission/pdfs/subject-guides/chemistry-guide.pdf','scope':'Current Chemistry first assessment2025;12SL/18AHL. Supplied unfamiliar calibration/charge-transfer/oxidation-test rules are explicit; no unsupplied septet,R/S or E/Z requirement.','visualEvidence':'All30 SVGs inspected in s3-contact-1.png through s3-contact-3.png. NMR whole-multiplet areas, isotope clusters, molecule connectivity and chirality agree with the supplied evidence.','limitation':'Independent AI chemistry/math/visual audit, not human examiner moderation. Re-running reproduces calculations and structural checks, not a new visual or prose review.'}
if '--write-review' in sys.argv:
 REVIEW.parent.mkdir(parents=True,exist_ok=True);REVIEW.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
elif REVIEW.exists():
 saved=json.loads(REVIEW.read_text(encoding='utf8'));assert saved['sha256']==rawsha,'Question bytes changed since the saved independent review; fresh review is required.'
print(json.dumps({'status':'passed','questions':30,'independentChecks':report['checks'],'sha256':rawsha,'reviewWritten':'--write-review' in sys.argv}))
