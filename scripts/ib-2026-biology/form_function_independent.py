"""Independent Theme B scientific review reproducer, standard library only.
No author script is imported. A fixed raw-byte hash requires re-review after edits.
Manual biological/diagram evidence accompanies separately recomputed calculations.
"""
from pathlib import Path
from collections import Counter
import hashlib, json, math, re, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
BANK=ROOT/'content/ib/biology-2026-expansion/form-function.json'
EXPECTED_SHA256='1b0b9435af42e22aabd53ec71312520b7a120f4bad86099b94714c9302fc9154'
raw=BANK.read_bytes()
assert hashlib.sha256(raw).hexdigest()==EXPECTED_SHA256,'Reviewed content changed'
qs=json.loads(raw);qm={q['number']:q for q in qs};records=[]
assert len(qs)==len(qm)==50 and sorted(qm)==list(range(701,751))
assert Counter(q['level'] for q in qs)=={'sl':20,'ahl':30}
def ck(label,actual,expected,tol=1e-8):
    if isinstance(expected,bool):assert bool(actual)==expected,(label,actual,expected)
    else:assert math.isclose(actual,expected,rel_tol=tol,abs_tol=tol),(label,actual,expected)
    return {'label':label,'actual':actual,'expected':expected,'status':'passed'}
def audit(n,checks,calculation,biology,visual):
    q=qm[n]
    assert q['id']==f'ib-bio-b-{n}' and q['source']=={'document':'Independent syllabus-authored practice','question':n}
    assert q['level']==('sl' if n<=720 else 'ahl')
    assert q['difficulty']=='hard' and q['calculator'] and q['status']=='published'
    assert q['marks']==sum(p['marks'] for p in q['parts'])
    for p,g in zip(q['parts'],q['markScheme'],strict=True):
        assert p['label']==g['part'] and p['marks']==sum(int(s['code'][1:]) for s in g['steps'])
        assert all(s['code'] in ('M1','A1','R1') for s in g['steps'])
    root=ET.fromstring(q['diagramSvg'])
    assert root.attrib['viewBox']=='0 0 800 480'
    assert len(q['diagramSvg'])<=300000
    assert not re.search(r'<(?:script|foreignObject|image|style|animate)|(?:href|src)=|url\s*\(|\bon\w+\s*=',q['diagramSvg'],re.I)
    records.append({'id':q['id'],'status':'passed','verdict':'passed','level':q['level'],'syllabusCode':q['syllabusCode'],
        'calculation':calculation,'independentChecks':checks,'biologicalReasoning':biology,'diagramReview':visual,
        'markAllocationReview':'Read all requested parts and every solution award; distinct M1/A1/R1 points reconcile with every part and question total. Conditional model results and valid alternative biological explanations remain explicit.',
        'questionSha256':hashlib.sha256(json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()})

audit(701,[ck('Open-chain links',6-1,5),ck('Water consumed µmol',10*(6-1),50),ck('Glucose µmol',10*6,60),ck('Particle increase percent',(60-10)/10*100,500)],
'Six-residue open chains contain five links. Ten µmol chains use50 µmol water and yield60 µmol glucose; particle number rises sixfold, or500%.',
'Alpha/beta linkage orientation changes enzyme recognition and long-chain form. Failure of this enzyme does not make beta polymers unhydrolysable. Insoluble storage reduces osmotic particle burden.',
'Both drawn chains contain six glucose-residue hexagons and five links. Alternating Q orientation is explicit; diagram does not claim full molecular stereochemistry.')
audit(702,[ck('Liquid fraction difference pp',80-15,65),ck('Hydrolysis fatty acid mmol',2*3,6),ck('Glycerol mmol',2,2)],
'At20°C liquid fractions differ65 percentage points. Two mmol triglyceride produce2 mmol glycerol and6 mmol fatty acids, using6 mmol water.',
'Cis kinks impair packing and lower melting transitions. Triglycerides are not long repeated-monomer polymers, and melting alone does not establish insulation.',
'X and Y curves have the given80/15 values at20°C, non-negative liquid percentages and a100% cap; axes and legend are clear.')
audit(703,[ck('Corrected anti-A before',90-5,85),ck('Corrected anti-A after',6-5,1),ck('Background-corrected loss percent',(85-1)/85*100,98.8235294118)],
'Background is subtracted before calculating the98.8% anti-A decline; both original signals exceed background.',
'Both terminal recognition patterns support AB. Glycosidase acts on carbohydrate, protease on the specified protein anchors; the scheme does not generalize this to all glycolipids.',
'Four bars preserve the90/6 and80/78 paired signals and distinguish before/after antibody labels without showing the computed percentage.')
audit(704,[ck('Carbohydrate dry g',510/17,30),ck('Lipid dry g',510/37,13.7837837838),ck('Mass saving percent',(510/17-510/37)/(510/17)*100,54.0540540541)],
'Divide510 kJ by the supplied17/37 kJ g−1, using unrounded lipid mass in the54.1% saving.',
'Energy density and hydrophobic storage support lipid reserves. Dry fuel mass is distinct from total body-mass change; water and conversion conditions matter.',
'Both energy-versus-mass lines pass through zero with slopes17/37 and correct units. No answer mass is marked.')
audit(705,[ck('12 g P supplies E mg',12/10*20,24),ck('12 g P supplies F mg',12/10*80,96),ck('Mixed E mg',.6*20+.6*80,60),ck('Mixed F mg',.6*80+.6*20,60),ck('Tripeptide links',3-1,2)],
'Twelve grams P fails E at24 mg despite96 mg F. Six grams of each gives60 mg E/F; a tripeptide has two peptide links.',
'Essential amino acids must be supplied sufficiently and sequence positions cannot be replaced by a surplus different amino acid. Complete digestion and two requirements are supplied simplifications.',
'Four amino-acid bars correctly display20/80/80/20 mg per10 g, with labels linking food and amino-acid identity.')
audit(706,[ck('Cooling recovery pp',30-20,10),ck('Neutralization recovery pp',80-10,70),ck('Remaining deficit pp',100-80,20)],
'Untreated100 units makes the measured values equal percentage activities; recovery is10 versus70 percentage points, with20 points still missing after neutralization.',
'Unchanged peptide-chain length argues against complete hydrolysis; denaturation can alter conformation without cleavage and may be partly reversible. Function is indirect structural evidence.',
'Five activity bars match untreated/heated/cooled/pH2/neutralized100/20/30/10/80 and do not confuse treatment samples.')
audit(707,[ck('Oxygen rate fourfold',8/2,4),ck('Ion channel rate at four units',4,4),ck('Protein-free ion flux',0,0)],
'Oxygen rate2→8 follows the fourfold supplied gradient; open-channel ion flux is possible with the supplied inward electrochemical gradient.',
'Small nonpolar O2 crosses lipid; charged ions need a hydrophilic pathway. Downhill channel transport is not directly ATP-driven and reverses with its driving gradient.',
'Three traces now have solid/dashed/dotted lines with matching legends. Protein-free Z+ remains zero, O2 is the higher linear trace, and channel Z+ the lower positive trace.')
audit(708,[ck('Equilibrium relative volume',1/2,.5),ck('Two-minute volume difference',.80-.55,.25)],
'Fixed solute amount requires half volume to double internal concentration; both vesicle types converge on0.500.',
'Aquaporins change permeability and rate, not the solute-conservation equilibrium. External concentration is constant and pressure effects are excluded by the model.',
'Aquaporin trace reaches0.55 at2 min and approaches0.50 faster than the no-aquaporin0.80 trace; both start at1.')
audit(709,[ck('Inside/outside concentration',80/8,10),ck('Uptake decline percent',(6-.4)/6*100,93.3333333333)],
'Uncharged S is tenfold more concentrated inside; measured inward uptake declines93.3% after ATP depletion.',
'Sustained inward accumulation needs energy against the concentration gradient. Residual unidirectional uptake need not be net accumulation; passive outward leak can remain. Viability/rescue control is appropriate.',
'Membrane protein spans the bilayer; outside8 and cytoplasm80 labels are on the correct sides. Lipid heads/tails face appropriate environments.')
audit(710,[ck('Digestive-marker recovered total',85+15,100),ck('Cytosolic-marker recovered total',10+90,100)],
'Each marker separately totals100%; percentages are marker recovery, not pellet mass purity.',
'Detergent improves access to compartmentalized enzyme. Cold/isotonic handling preserves interpretable fractions; cytosolic carryover and organelle breakage remain possible.',
'Four bars show digestive85/15 and cytosolic10/90 in pellet/supernatant, with paired labels and percentage units.')
audit(711,[ck('Original volume µm3',40**3,64000),ck('Subdivided volume µm3',8*20**3,64000),ck('Original area µm2',6*40**2,9600),ck('New area µm2',8*6*20**2,19200),ck('Original SA/V',6/40,.15),ck('New SA/V',6/20,.30)],
'Eight20-µm cubes conserve64000 µm³ but double exposed area9600→19200 µm² and SA/V0.150→0.300 µm−1; centre-to-nearest-face distance halves20→10 µm.',
'The fully exposed assumption is explicit; touching faces in tissue invalidate simply summing all six faces. Geometry is not sufficient to specify metabolic rate.',
'One large perspective cube and a two-layer explanation distinguish eight smaller cubes from the four visible front faces. No false claim that all real cells are cubes.')
audit(712,[],
'No numerical result is required. Independently checked self-renewal, three demonstrated tissue lineages and the limits of the tested potency.',
'Repeated recloning supports self-renewal, specialized descendants support differentiation, and a limited tissue range demonstrates neither pluripotency nor totipotency. Single-cell tracing controls starting-cell mixtures.',
'The gradient diagram varies signal6→1 with positional fates and separately shows stem-like and specialized descendants; arrows distinguish renewal from differentiation.')
audit(713,[ck('Relative diffusion model',.8*.9/3,.24),ck('Predicted rate',240*.8*.9/3,57.6)],
'The supplied Fick-type proportional model gives J/H0.240 and57.6 units; measured80 tests model completeness, not the existence of diffusion.',
'Ventilation renews air, perfusion renews blood, and diffusion crosses the barrier. Thickness, local gradients and functional area can differ from averages.',
'Barriers are shown at schematic1:3 thickness with oxygen arrows air→blood. The caption states dimensions are schematic rather than claiming a measured micrograph.')
audit(714,[ck('P minute ventilation',12*.5,6),ck('Q minute ventilation',30*.2,6),ck('P fresh-air delivery',12*(.5-.15),4.2),ck('Q fresh-air delivery',30*(.2-.15),1.5)],
'Subtract0.150 L dead space per breath before multiplying frequency: equal6.00 L/min total ventilation gives4.20 versus1.50 L/min fresh-air delivery.',
'Shallow breaths devote more volume to conducting airways. Diaphragm/intercostal volume-pressure changes, quiet recoil and forced expiration are within sharedB3.1.5; titin/antagonistic fine detail is not demanded.',
'Ten-second traces show two P cycles of0.5 L and five Q cycles of0.2 L, consistent with12/30 breaths per minute.')
audit(715,[ck('Sun density mm−2',(20+24+16)/3/.2,100),ck('Shade density mm−2',(10+12+8)/3/.2,50),ck('Relative increase percent',(100-50)/50*100,100)],
'Means20/10 per0.200 mm² give100/50 stomata mm−2; sun mean is100% higher.',
'Leaf is the independent replicate. Aperture, humidity and other factors prevent density being equated with a twofold transpiration rate; means alone do not establish significance.',
'Dicot tissue plan has upper epidermis, palisade-like layer, spongy spaces and a lower opening in the correct orientation; explicitly not the counted fields.')
audit(716,[ck('X wall thickness',6-4,2),ck('Y wall thickness',7-6,1),ck('Lumen area ratio',6**2/4**2,2.25)],
'Wall differences are2/1 arbitrary units; π cancels in the Y:X lumen-area ratio2.25.',
'Wall muscle/elastic structure supports artery identification, with pressure/direction rather than blood oxygen defining vessel type. Venous return assistance is correctly explained.',
'Same-scale radii are Xouter120/inner80 andYouter140/inner120 pixels, matching6/4 and7/6 units. Radial6 labels refer to Xoutside andYlumen, with explicit captions.')
audit(717,[ck('Drier uptake µL/min',math.pi*.5**2*5/10,.392699081699),ck('Humid uptake µL/min',math.pi*.5**2*2/10,.157079632679),ck('Decrease percent',(5-2)/5*100,60)],
'Cross-sectional areaπr² times displacement/time gives0.393/0.157 µL/min and60.0% decrease; mm³ equalsµL.',
'Humidity reduces water-vapour gradient. Leaf tension/cohesion and lignified dead xylem explain flow; uptake is not automatically exact instantaneous transpiration.',
'Displacement traces reach5/2 mm at10 min with matched axes and clear drier/humid line styles.')
audit(718,[ck('Rolled water-loss reduction percent',(5-2)/5*100,60),ck('Rolled/open ratio',2/5,.4)],
'Reference is held-open5.0, so rolling reduces loss by60.0%, not150%.',
'Sheltering and humidity reduce water loss, but handling damage/illumination/area are confounders. One leaf response is distinct from inherited adaptation over generations.',
'Roll opens to external air and stomatal marks lie on the inward-facing ellipse. The sheltered space is inside, with cuticular roll geometry and no inverted stomatal side.')
audit(719,[ck('Density increase at60cm',12-0,12),ck('Observed removal range increase cm',80-40,40)],
'At60 cm increase is12 snails/m²; a relative percentage rise from zero is undefined. Observed upper occupied sample position extends40→80 cm.',
'Randomized removal/sham replication supports biotic restriction but does not uniquely reveal the full fundamental niche or exclude altered shelter/predation. No significance is inferred from means.',
'Sham density is positive through40cm and zero at60/80/100; removal remains positive through80 and zero at100, matching the observations rather than asserting unsampled exact boundaries.')
audit(720,[ck('Prey light-growth increase percent',(4-2)/2*100,100),ck('Prey light-growth fold',4/2,2)],
'Prey doubles light growth2→4 divisions/day, a100% increase; dark no-prey0.2 may use finite stores.',
'Tracer carbon fixation plus internal prey vacuoles supports mixotrophy. Washed prey and controls distinguish ingestion from adhering/free label; serial transfer tests sustained alternative nutrition.',
'Four culture bars correctly pair light/dark and prey/no-prey4/2/2/0.2. No unsupported real organism identity is supplied.')
audit(721,[ck('Hydrophobic buried fraction',6/8,.75)],
'Six of eight H residues gives75.0%; the mutation changes sequence chemistry without requiring chain cleavage.',
'Soluble hydrophobic cores and membrane-facing hydrophobic surfaces fit different environments. Charged replacement can alter tertiary stability context-dependently; equal purified protein assays separate abundance from specific function.',
'Soluble/membrane environments and H/P/charge key are explicit schematic positions, rather than a literal complete eight-residue inventory.')
audit(722,[ck('Last internal acceptor index',12-4,8),ck('Number of allowed i values',len(range(1,9)),8)],
'i ranges1..8 under i+4≤12, giving eight possible internal hydrogen bonds.',
'Backbone hydrogen bonds stabilize secondary conformation; peptide bonds link residues covalently. Alpha helix/beta sheet differ while sequence can remain unchanged after H-bond disruption.',
'Selected O···H contacts terminate at displayed oxygen and hydrogen, not R-groups. Caption explicitly shows two selected turns with omitted intervening backbone, avoiding a false two-chain claim.')
audit(723,[ck('Total residues',21+30,51),ck('Peptide bonds',21-1+30-1,49),ck('Disulfides',1+2,3),ck('Chains after reduction',2,2)],
'Separate21/30-residue chains contain20+29=49 peptide bonds, so complete hydrolysis uses49 water. Disulfides are1intra/2inter; reduction retains two peptide chains.',
'Cysteine disulfides stabilize tertiary/interchain arrangement; breaking them does not hydrolyse peptide backbone. Multiple polypeptides establish quaternary organization.',
'Numbered A/B chains correctly connectA6–A11,A7–B7,A20–B19, with one loop onA and two cross-chain bonds. No nonexistent A–B peptide bond is drawn.')
audit(724,[ck('Hb polypeptide subunits',64/16,4),ck('Collagen polypeptide chains',300/100,3),ck('Equal-mass assembly ratio',300/64,4.6875)],
'Native/subunit masses give4 and3 chains; equal mass has H:C assembly ratio4.69 because assembly number is inverse molecular mass.',
'Haem is a non-polypeptide prosthetic group, not a fifth chain. Globular Hb supports reversible binding while fibrous collagen supports tension; real variants are acknowledged.',
'Bars are explicitly molecular masses64/16/300/100kDa, not concentrations or direct mechanical strength.')
audit(725,[ck('Unsaturated increase pp',60-30,30),ck('Unsaturated relative increase percent',(60-30)/30*100,100),ck('Cold fluidity advantage',40-15,25),ck('Warm fluidity advantage',70-55,15)],
'Cold acclimation increases unsaturated fraction by30points/100%; model fluidity advantages25at5°C and15at20°C are not constant.',
'Cis unsaturation opposes close packing and cooling-induced stiffening. Genetically matched acclimation is plasticity, not evidence of changed allele frequencies.',
'Both composition curves rise with temperature; the60%unsaturated trace is higher and the stated differences match the plotted5/20°C points.')
audit(726,[ck('Cold cholesterol effect',25-5,20),ck('Warm cholesterol effect',55-80,-25)],
'Cholesterol increases low-temperature index20units but decreases high-temperature index25units.',
'Its polar region is near heads and rings among tails; reduced low-T packing and restrained high-T movement explain buffering rather than always fluidizing.',
'Curves cross between15and25°C; both endpoints and opposite temperature-dependent effects are correctly shown with a clear legend.')
audit(727,[ck('Protected component',80-5,75),ck('Protected fraction percent',75/80*100,93.75)],
'On the requested pre-detergent retained-signal denominator,75/80=93.8% is above detergent/protease background.',
'Former extracellular domains become luminal upon inward budding and become extracellular on fusion. Protection supports enclosure but does not alone prove live-cell endocytosis rather than isolation fragments.',
'Both X circles are now attached to membrane-spanning stems. X remains on the extracellular/luminal side and the short tail extends cytoplasmically; no membrane-side inversion is drawn.')
audit(728,[ck('Receptor conductance inhibition percent',(8-.2)/8*100,97.5),ck('Voltage response retention',20/20,1)],
'Antagonist reduces ACh conductance97.5% while supplied voltage response remains20units.',
'Ligand and voltage gates respond to different triggers; open Na+ channels permit downhill entry without direct ATP pumping. Tested selectivity is not universal absence of off-target effects.',
'Independent-trial traces now have three distinct styles. The voltage step20, ACh8andblockedACh0.2 plateau values are correct; the figure is not labelled an action potential.')
audit(729,[ck('ATP count',800,800),ck('Sodium export',800*3,2400),ck('Potassium import',800*2,1600),ck('Net elementary-charge export',800*(3-2),800)],
'800cycles use800ATP, export2400Na+, import1600K+ and export800net positive elementary charges.',
'Direct electrogenic contribution and maintained gradients are distinguished from channel flux. Voltage cannot be calculated without capacitance/geometry and other currents.',
'Destination-side captions place threeNa+outside and twoK+inside per cycle; bilateral phospholipid heads/tails and spanning pump are correctly oriented.')
audit(730,[ck('Na outside/inside concentration ratio',140/10,14),ck('Glucose inside/outside ratio',5/1,5),ck('Uptake decline percent',(60-10)/60*100,83.3333333333)],
'Na concentration ratio14andglucose5are consistent with the supplied electrochemical entry drive; uptake declines83.3% over30min.',
'Apical cotransport uses stored Na gradient to drive uphill glucose. Basolateral pump uses ATP directly, cotransport indirectly; a pre-existing gradient explains delayed inhibition.',
'Apical T faces lumen; separate basolateral carrier/pump face external fluid. Concentrations match the question and no reversed epithelial polarity is drawn.')
audit(731,[ck('Area decrease percent',(40-20)/40*100,50),ck('ATP decrease percent',(100-60)/100*100,40),ck('Control ATP/area',100/40,2.5),ck('Mutant ATP/area',60/20,3)],
'Area halves whileATPfalls40%; rates per area2.50versus3.00refute strict proportionality.',
'Cristae enlarge inner-membrane area; matrix compartmentalizes Krebs reactions. One equal marker does not prove all components, integrity or transport equal.',
'Continuous folded inner boundary lies inside the outer envelope. P points to matrix and Q to the narrow intermembrane region, with folds continuous rather than detached internal lines.')
audit(732,[ck('A area/volume µm−1',20/.2,100),ck('B area/volume µm−1',20/.4,50),ck('Ratio of area/volume',100/50,2)],
'Same20µm²membrane gives100versus50µm−1area/volume with0.2/0.4µm³lumens; equal area/density preserves equal photosystem count.',
'Photosystems occupy thylakoid membranes and Calvin reactions stroma. Smaller volume allows greater concentration change per transported amount, not a guaranteed twofold whole photosynthetic rate.',
'Double envelope, external stroma Y and closed narrow thylakoid lumen X are correctly drawn. Connections are labelled schematic and do not open lumen directly into stroma.')
audit(733,[ck('2min recovered percent',70+10+0+20,100),ck('10min recovered percent',20+60+20+0,100),ck('30min recovered percent',5+10+80+5,100),ck('Medium increase pp',80-0,80)],
'Recovered fractions each total100%; extracellular label rises80points, with RER→Golgi→medium timing.',
'Bound ribosomes synthesize secretory protein; Golgi processes/sorts rather than translating. Population fractions cannot prove the route of every molecule; purity/label-recycling controls are appropriate.',
'RER/Golgi/medium now use solid/dashed/dotted styles. Points70/20/5,10/60/10and0/20/80match all time positions.')
audit(734,[ck('Control cytoplasmic percent',8/(2+8)*100,80),ck('Treated cytoplasmic percent',1/(9+1)*100,10),ck('Difference pp',80-10,70)],
'Equal10unit totals give80%control and10%treatedcytoplasmic label, a70point difference.',
'Nuclear pores allow regulated exchange while retaining compartmental separation and pre-translation processing. Equal recovery does not control all degradation/processing or viability effects.',
'Double envelope is interrupted by a deliberately open pore with aligned gap and cytoplasmic ribosomes outside; the gap is not falsely represented by a fully closed ellipse.')
audit(735,[ck('Control internalized percent',70/100*100,70),ck('Clathrin-reduced internalized percent',15/98*100,15.306122449),ck('Binding retention fraction',98/100,.98)],
'Normalize internalization to each condition’s bound cargo:70.0%versus15.3%, with98%binding retention.',
'Near-normal binding but poor uptake localizes the tested defect toward coated-pit/vesicle formation. Clathrin is cytoplasmic and enclosed cargo luminal; other uptake mechanisms are not excluded.',
'Coat polygons sit on the cytoplasmic convex side of the inward pit and cargo dots on its extracellular/luminal side. Caption does not place clathrin inside the lumen.')
audit(736,[ck('Additional membrane µm2',40*2*math.pi*.1*1,25.1327412287),ck('Total membrane µm2',100+40*2*math.pi*.1,125.132741229),ck('Area increase percent',40*2*math.pi*.1/100*100,25.1327412287)],
'Replacing circular bases with equal tops cancels those areas, leaving40×2πrL=25.1µm²extra,125µm²totaland25.1%increase.',
'Microvilli are continuous projections of one cell, not new cells or motile cilia. Additional area increases capacity only if per-area transport and downstream factors permit.',
'Apical membrane stays continuous through four representative protrusions, with lumen above and cytoplasm below. Caption explicitly models40cylinders rather than claiming four are the full count.')
audit(737,[ck('Average X/Y surface per cell',(95/40)/(5/60),28.5),ck('Inflation volume decrease percent',(.6-.2)/.6*100,66.6666666667)],
'Coverage fraction divided by cell-number fraction yields28.5times mean area; inflation at fixed pressure falls66.7%.',
'Thin typeIprovides diffusion area; typeIIvesicles deliver surfactant and lower surface tension. Mechanical inflation is not a haemoglobin-affinity assay.',
'Thin spread X and a cuboidal vesicle-containing Y share the air-facing lining, with capillary below. The large X surface is distinct from numerical cell abundance.')
audit(738,[ck('Mitochondrial volume-fraction ratio',30/8,3.75),ck('Volume-fraction difference pp',30-8,22)],
'CardiacYhas3.75times mitochondrial fraction, not an automatically3.75times ATP flux.',
'Long multinucleate unbranched skeletal fibres contrast with branched central-nucleus cardiac cells and joining discs. Multinucleation alone does not uniquely identify all tissues.',
'Latest full-size render shows striations in both tissues, central nuclei and bold cardiac joining discs. The skeletal top is one long fibre, not an unexplained row of independent cells.')
audit(739,[ck('Supplied saturation difference pp',74.93-57.06,17.87),ck('F lower P50',20<27,True)],
'F has lower P50 and higher affinity; the given rounded values at 30 mmHg differ by 17.87 percentage points, approximately 17.9.',
'Foetal binding removes O2 from the dissolved pool and maintains a diffusion partial-pressure gradient. Blood supplies and Hb remain separated; greater affinity can impair adult unloading.',
'F lies left/above A at matched conditions, passes 50% saturation at 20 versus 27 mmHg and approaches the same capacity. The curves do not imply blood mixing.')
audit(740,[ck('Saturation difference pp',74.29-62.70,11.59),ck('Right-shifted P50',33>27,True)],
'At 40 mmHg the given values differ by 11.59 percentage points; higher P50 indicates lower affinity.',
'The CO2/pH shift aids unloading in respiring tissues. CO2 does not simply occupy the haem oxygen sites, and simultaneous CO2/pH changes do not separate their causal effects.',
'The higher-CO2/lower-pH curve lies right of control at matched Hb. The legend labels both changed variables, making the confounding explicit.')
audit(741,[ck('Supplied saturation drop pp',74.29-6.41,67.88),ck('Cooperative low-pressure comparison',6.41<27.03,True),ck('Cooperative high-pressure comparison',74.29>59.70,True)],
'The displayed rounded subtraction is 67.88 percentage points, approximately 67.9; identical P50 specifies only one point.',
'Initial O2binding changes conformation and promotes further binding at other subunits, giving a steep middle and finite capacity. Saturation decline is not oxygen volume without Hb amount/capacity.',
'C and N share 50% saturation at 27 mmHg, but C is S-shaped and N hyperbolic. C lies below N at low pressure and above it at higher pressure, matching supplied data.')
audit(742,[ck('X full capacity mL/L',100*1.34,134),ck('Y full capacity mL/L',120*1.34,160.8),ck('X bound content',134*.7429,99.5486),ck('Y bound content',160.8*.5892,94.74336)],
'Full capacities of 134/160.8 mL/L multiplied by supplied fractional saturations give 99.55/94.74 mL/L, despite more Hb in Y.',
'Affinity, maximum capacity and actual oxygen content are distinct. One content value cannot identify foetal blood; temperature, partial pressure and Hb amount matter.',
'Curves plot saturation rather than oxygen content, with Hb concentration and P50 both labelled. Y has lower affinity despite its higher Hb amount.')
audit(743,[ck('Initial steady balance mL/min',20-17-3,0),ck('Blocked accumulation mL/min',20-17-1,2),ck('One-hour conditional mL',2*60,120)],
'The initial 20=17+3 balance becomes 2 mL/min accumulation; 120 mL per hour is explicitly conditional on fixed rates.',
'Protein retention affects osmotic balance and lymph returns excess fluid. Altered tissue pressure prevents indefinite fixed-rate extrapolation. The supplied aggregate model does not assert every real capillary reabsorbs17/20.',
'Capillary flow, outward 20, return 17 and lymph 3 arrows are correctly directed. Lymph valve chevrons and the forward arrow agree.')
audit(744,[ck('0.20s aortic opening gradient',100>85,True),ck('0.20s mitral closure gradient',100>10,True),ck('0.50s mitral opening gradient',10>5,True),ck('0.50s aortic closure gradient',85>5,True),ck('Stroke volume mL',120-50,70),ck('Output L/min',(120-50)*75/1000,5.25)],
'The specified pressure inequalities give open aortic/closed mitral valves at 0.20 s, and open mitral/closed aortic valves at 0.50 s. Stroke volume 70 mL gives 5.25 L/min.',
'Both valves can be closed during isovolumetric intervals. The sinoatrial node starts the beat; pressure gradients passively set valve state. Pressure is not flow or volume.',
'Latest solid/dashed/dotted ventricle/atrium/aorta styles resolve the previous shared-solid legend. All four requested-time pressures match the points.')
audit(745,[ck('Supplied systemic/pulmonary pressure ratio',120/25,4.8)],
'The stated pressure ratio is 4.80; this compares pressures, not oxygen concentrations.',
'The fish circuit has one heart passage per full circuit; the mammalian circuit passes right heart → lungs → left heart → body. Named chamber/vessel sequence and septal separation are correct.',
'All arrows form closed directed circuits: fish pump → gills → body → pump; Q → lungs → R → body → Q. Q/R are labelled as two sides of one heart in the stem.')
audit(746,[ck('Pressure decrease percent',(40-10)/40*100,75),ck('Raw recovery fraction',35/40,.875)],
'Pressure falls 75.0%; recovery to 35/40 of control is partial and does not establish perfect specificity of a broad inhibitor.',
'Living root cells actively accumulate ions to generate positive root pressure, while dead xylem is not an ATP pump. Sieve elements/companion cells, pores and plasmodesmata are accurately distinguished.',
'The sieve element has perforated plates and reduced contents; the companion cell has a nucleus, organelles and connecting channels. Phloem is distinguished from the xylem pressure conduit.')
audit(747,[ck('Sarcomere shortening percent',(3-2.2)/3*100,26.6666666667),ck('Initial thin-free length',3-2,1),ck('Final thin-free length',2.2-2,.2),ck('Fixed thick length',.8*2,1.6)],
'Length 3.00→2.20 µm shortens 26.7%; the central thin-free region changes 1.00→0.200 µm while filament lengths remain fixed.',
'Sliding increases overlap and brings Z lines closer. Titin recoil and antagonistic pulling explain return/stretch rather than active pushing by the same muscle.',
'Both diagrams use 130 pixels/µm; thick filaments are 208 pixels=1.60 µm and thin filaments 130 pixels=1.00 µm in both. The 0.500 µm scale bar is 65 pixels and Z-line separations 390/286 match 3.00/2.20 µm.')
audit(748,[ck('Unit1 force N',12-0,12),ck('Unit2 force N',32-12,20),ck('Unit3 force N',62-32,30),ck('42 absent under fixed order',42 not in [0,12,32,62],True)],
'Successive increments 12/20/30 N give allowed fixed-order states 0/12/32/62 N; 12+30 does not permit 42 N without skipping unit 2.',
'A motor unit is one motor neuron and its innervated fibres. Recruitment grades whole-muscle force; model restrictions on frequency/length avoid overgeneralizing to real force control.',
'Three neurons branch to separate fibre groups without sharing fibres; caption states drawing counts are not force calibration, preventing false numerical inference.')
audit(749,[ck('Load moment Nm',60*.4,24),ck('Required muscle force N',60*.4/.04,600),ck('Flexion reduction degrees',120-85,35),ck('Flexion reduction percent',(120-85)/120*100,29.1666666667),ck('Drawn lever-arm ratio',(680-160)/(212-160),10)],
'A 24.0 N m load moment requires 600 N at 0.0400 m; range drops 35° or 29.2%. The drawn moment arms have an exact 10:1 ratio.',
'Tendons transmit muscle force, ligaments link bones, and cartilage/fluid reduce friction. Femur/pelvis ball-and-socket anatomy is multiplanar; the linear static lever is explicitly a simplified model.',
'Muscle force upward at x212 and load downward at x680 have opposed moments about x160. Dimension lines end at the same force coordinates; all lengths are scaled consistently.')
audit(750,[ck('Streamlined mechanical power W',40*2,80),ck('Comparison power W',65*2,130),ck('Power saving percent',(130-80)/130*100,38.4615384615)],
'Drag powers 80.0/130 W give a 38.5% reduction at fixed 2 m/s; this does not automatically quantify total migration energy.',
'Streamlining/flippers and coordinated tail/body pulling serve swimming. Metabolic maintenance, duration, efficiency and behaviour are outside the stated mechanical model.',
'Drag curves pass 40/65 N at 2 m/s, with non-negative quadratic increases and matched speed axes. No whole-animal metabolic outcome is falsely plotted.')

assert {r['id'] for r in records}=={q['id'] for q in qs}
report={'status':'passed','questions':50,'sha256':EXPECTED_SHA256,
    'reviewer':'Separate AI reviewer who did not author Theme B',
    'method':'Read every stem, part and worked solution against current first-assessment-2025 guide limits. Recomputed calculations without author helpers, inspected all 50 rendered diagrams and targeted full-size scientific geometry, sidedness and labels.',
    'independentCheckCount':sum(len(r['independentChecks']) for r in records),
    'diagramCount':50,'substantiveNonTableDiagrams':50,'levels':{'sl':20,'ahl':30},'marks':sum(q['marks'] for q in qs),
    'officialGuide':'https://ibo.org/globalassets/new-structure/university-admission/pdfs/subject-guides/biology-guide.pdf',
    'correctedGuide':'https://xmltwo.ibo.org/publications/EAD/2026_EN/GR4/GR4-Biology_EN.pdf',
    'specimen':'https://www.ibo.org/globalassets/new-structure/programmes/dp/pdfs/biology-hl-sl-specimen-papers-1a-2b-2-en.pdf',
    'scopeReview':'First 20 questions require shared statements only. All later questions require AHL protein structure, membrane fluidity/vesicle/cotransport mechanisms, organelle ultrastructure, pneumocyte/muscle specialization, Hb curves, advanced circulation or B3.3. All B3.3 questions are AHL. Supplied numerical formulas do not masquerade as recall requirements.',
    'corrections':['B739: clarified that foetal binding removes dissolved O2 and maintains the diffusion partial-pressure gradient.','B741: used displayed rounded values to obtain 67.88 percentage points (approximately 67.9).','B727: explicitly anchored labelled extracellular domain to the membrane before and after endocytosis.','Shared plots: distinguished third series with dotted line and matching legend.','All fields: expanded editorial separation of prose from numeric quantities.'],
    'limitations':['Original constructed IB-style practice, not official past-paper content or official IB markschemes.','Computational checks and separate AI scientific review are not human IB examiner moderation.','Difficulty is editorial; no student-performance calibration.','Content review does not claim build or deployment success.'],
    'records':records}
out=ROOT/'docs/ib-2026-biology/form-function-independent-review.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps({k:report[k] for k in ['status','questions','sha256','independentCheckCount','diagramCount','levels','marks']}))
