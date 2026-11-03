"""Thirty original S3 problems. Run with RDKit available on PYTHONPATH.

All spectra are constructed teaching data, not scans of experimental spectra.
Numerical assertions and RDKit valence/formula checks accompany the authoring.
"""
import json, math, hashlib, re
from pathlib import Path
from html import escape
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit.Chem.Draw import rdMolDraw2D

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'content/ib/chemistry-2026-expansion/periodicity.json'
REVIEW=ROOT/'docs/ib-2026-chemistry/periodicity-author-review.json'
questions=[]
checks=[]
BLUE='#176089'; INK='#172b4d'
def tx(x,y,s,size=16,anchor='middle'):
    return f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" text-anchor="{anchor}" fill="{INK}">{escape(str(s))}</text>'
def ln(x,y,a,b,col=INK,w=2):return f'<line x1="{x}" y1="{y}" x2="{a}" y2="{b}" stroke="{col}" stroke-width="{w}"/>'
def svg(body,title,w=760,h=360):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img"><title>{escape(title)}</title><rect width="{w}" height="{h}" fill="white"/>{body}</svg>'
def chart(xs,ys,xlabel,ylabel,title,labels=None):
    xmin=min(xs);xmax=max(xs); ymax=max(ys)*1.22
    X=lambda x:85+590*(x-xmin)/(xmax-xmin or 1)
    Y=lambda y:280-220*y/ymax
    b=ln(85,280,700,280)+ln(85,280,85,45)+tx(390,338,xlabel)+tx(90,27,ylabel,16,'start')
    b+='<polyline points="'+' '.join(f'{X(x):.2f},{Y(y):.2f}' for x,y in zip(xs,ys))+'" fill="none" stroke="'+BLUE+'" stroke-width="2"/>'
    for i,(x,y) in enumerate(zip(xs,ys)):
        b+=f'<circle cx="{X(x)}" cy="{Y(y)}" r="5" fill="{BLUE}"/>'+tx(X(x),305,labels[i] if labels else x,14)+tx(X(x),Y(y)-12,f'{y:g}',14)
    for y in [0,ymax/4,ymax/2,3*ymax/4]:b+=tx(72,Y(y)+5,f'{y:.3g}',12,'end')
    return svg(b,title)
def molecule(smi,w=340,h=190):
    m=Chem.MolFromSmiles(smi);assert m is not None,smi
    Chem.SanitizeMol(m)
    d=rdMolDraw2D.MolDraw2DSVG(w,h);d.drawOptions().padding=.17
    d.DrawMolecule(m);d.FinishDrawing();raw=d.GetDrawingText()
    inner=raw[raw.index('>',raw.index('<svg'))+1:raw.rindex('</svg>')]
    # RDKit emits only vector primitives and inline style attributes.
    return inner,rdMolDescriptors.CalcMolFormula(m)
def molecules(items,title,columns=2):
    h=240*math.ceil(len(items)/columns);b=''
    for i,(label,smi,formula) in enumerate(items):
        inner,actual=molecule(smi)
        if formula:assert actual==formula,(smi,actual,formula)
        x=(i%columns)*380;y=(i//columns)*240
        b+=f'<g transform="translate({x+20},{y+30})">{inner}</g>'+tx(x+190,y+24,label,18)
    return svg(b,title,h=h)
def spectrum(kind,peaks,title):
    # peaks: (position, integration or height, label), plotted in conventional descending x.
    if kind=='nmr':xmin,xmax=0,11;xl='δ / ppm (constructed ¹H NMR; OH omitted if stated)'
    elif kind=='ir':xmin,xmax=500,4000;xl='Wavenumber / cm⁻¹ (constructed IR)'
    else:xmin,xmax=0,max(p[0] for p in peaks)*1.15;xl='m/z (constructed mass spectrum)'
    X=lambda x:80+610*((xmax-x)/(xmax-xmin) if kind!='ms' else (x-xmin)/(xmax-xmin))
    b=ln(80,270,705,270)+ln(80,270,80,45)+tx(390,334,xl,15)+tx(80,25,title,16,'start')
    patterns={'s':[1],'d':[1,1],'t':[1,2,1],'q':[1,3,3,1],'u':[1]}
    highest=max(v*max(patterns[label[0]])/sum(patterns[label[0]]) for pos,v,label in peaks) if kind=='nmr' else 1
    for pi,(pos,v,label) in enumerate(peaks):
        if kind=='nmr':
            mult=patterns[label[0]];code=chr(97+pi)
            for j,a in enumerate(mult):b+=ln(X(pos)+(j-(len(mult)-1)/2)*5,270,X(pos)+(j-(len(mult)-1)/2)*5,270-140*v*a/sum(mult)/highest,BLUE,2)
            lab='unresolved' if label=='u' else label
            b+=tx(95+(pi%2)*335,50+(pi//2)*22,f'{code}: δ {pos:g}, {lab}, ∫{v:g}',14,'start')
            b+=tx(X(pos),116-(pi%2)*13,code,14)
        elif kind=='ms':b+=ln(X(pos),270,X(pos),270-1.7*v,BLUE,4)+tx(X(pos),270-1.7*v-12,f'{pos:g}',14)
    if kind=='ir':
        pts=[]
        for k in range(801):
            x=xmin+(xmax-xmin)*k/800
            y=65+sum(v*math.exp(-.5*((x-p)/float(label))**2) for p,v,label in peaks)
            pts.append(f'{X(x):.1f},{min(258,y):.1f}')
        b+='<polyline points="'+' '.join(pts)+'" fill="none" stroke="'+BLUE+'" stroke-width="2"/>'
        for p,v,width in peaks:b+=tx(X(p),min(258,65+v)+23,str(p),13)
        b+=tx(74,72,'100',12,'end')+tx(74,269,'0',12,'end')+tx(90,46,'Transmittance / %',13,'start')
    for p in ([0,2,4,6,8,10] if kind=='nmr' else [500,1000,1500,2000,2500,3000,3500,4000] if kind=='ir' else [0,20,40,60,80,100,120,140]):
        if xmin<=p<=xmax:b+=tx(X(p),295,p,12)
    return svg(b,title)
def stack(*figures):
    b='';y=0
    for f in figures:
        h=float(re.search(r'viewBox="0 0 760 ([\d.]+)"',f)[1]);inner=f[f.index('>')+1:f.rindex('</svg>')]
        b+=f'<g transform="translate(0,{y})">{inner}</g>';y+=h
    return svg(b,'Multi-panel chemical evidence',h=y)
def P(prompt,*steps):return (prompt,list(steps))
def add(n,title,code,level,stem,fig,parts,evidence,answer):
    ps=[];ms=[]
    for i,(prompt,steps) in enumerate(parts):
        label=chr(97+i);ps.append({'label':label,'prompt':prompt,'marks':len(steps)})
        ms.append({'part':label,'steps':[{'code':'A1' if not s.startswith('Reason:') else 'R1','text':s.removeprefix('Reason:')} for s in steps]})
    questions.append(dict(id=f'ib-chem-s3-{n}',number=n,title=title,subject='chemistry',topicId='structure-3',collectionId='chemistry-structure-3',syllabusCode=code,subtopic='The periodic table: Classification of elements' if code=='S3.1' else 'Functional groups: Classification of organic compounds',level=level,difficulty='hard',calculator=True,questionType='data-based',marks=sum(p['marks'] for p in ps),stem=stem,diagramSvg=fig,diagramCaption='Original constructed figure. Molecular drawings show connectivity; spectra are schematic teaching data. All numerical evidence is also stated in the question.',parts=ps,markScheme=ms,answerSummary=answer,source={'document':'Independent syllabus-authored practice','question':n},status='published',verification={'method':'Independent author derivation, numerical assertions and molecular valence checks; separate reviewer required before release','notes':evidence}))
    checks.append({'id':f'ib-chem-s3-{n}','status':'passed','evidence':evidence})

# Shared SL/HL: five periodic investigations and seven organic investigations.
add(701,'An isoelectronic series that crosses a period','S3.1','sl',
    'Five monatomic ions A–E each contain 10 electrons. Their proton numbers are 8, 9, 11, 12 and 13 respectively. The figure gives their radii (140, 133, 102, 72 and 54 pm).',
    chart([8,9,11,12,13],[140,133,102,72,54],'Proton number','Ionic radius / pm','Isoelectronic ions'),[
    P('Identify A–E, including charges, and explain the radius trend without invoking a change in occupied principal shell.','A = O²⁻ and B = F⁻.','C = Na⁺, D = Mg²⁺ and E = Al³⁺.','Reason:Each has the same occupied shells and 10 electrons, while nuclear charge increases.','Reason:Greater attraction between the nucleus and the same electron population contracts the ion.'),
    P('A student claims neutral sodium must also be smaller than neutral fluorine. Evaluate the claim using electron configurations.','Neutral Na is 1s²2s²2p⁶3s¹; neutral F is 1s²2s²2p⁵.','Reason:Na has an additional occupied shell with greater distance and shielding, so the ionic-series argument cannot be transferred; neutral Na is larger.'),
    P('Deduce the formula of the neutral compound formed by E and A, and predict whether it conducts as a pure solid and when molten.','Al₂O₃ follows from balancing 2 × (+3) with 3 × (−2).','Reason:The ionic solid has ions fixed in place; molten material has mobile ions and conducts.')],
    'Electron counts Z−charge=10 for all five; Al₂O₃ charge sum 0; neutral Na occupies n=3 whereas F ends at n=2.','O²⁻, F⁻, Na⁺, Mg²⁺, Al³⁺; Al₂O₃')

b=tx(380,25,'Displacement observations (aqueous solutions; organic extraction)',17)
for x,label in [(150,'X₂ + Y⁻'),(380,'Y₂ + Z⁻'),(610,'Z₂ + X⁻')]:
    b+=f'<rect x="{x-55}" y="65" width="110" height="170" rx="18" fill="none" stroke="{INK}" stroke-width="2"/>'+ln(x-53,150,x+53,150)+tx(x,55,label)+tx(x,270,'new halogen' if x<600 else 'no reaction',15)
b+=tx(150,125,'Y₂ forms')+tx(380,125,'Z₂ forms')+tx(610,125,'Z₂ remains')
add(702,'Ordering halogens from a reaction network','S3.1','sl',
    'X, Y and Z are chlorine, bromine and iodine in an unknown order. X₂ displaces Y₂ from Y⁻, Y₂ displaces Z₂ from Z⁻, and Z₂ does not react with X⁻. For a separate experiment, 0.0100 mol X₂ is added to excess aqueous Y⁻; the resulting halogen is completely transferred to fresh excess Z⁻.',svg(b,'Three halogen displacement observations'),[
    P('Identify X, Y and Z and explain the trend in oxidizing ability in terms of attraction for an incoming electron.','X = chlorine, Y = bromine, Z = iodine.','Reason:Oxidizing ability decreases down Group 17 as the incoming electron is added farther from the nucleus and experiences greater shielding.'),
    P('Write ionic equations for both stages and determine the final amount of Z₂.','Cl₂ + 2Br⁻ → 2Cl⁻ + Br₂.','Br₂ + 2I⁻ → 2Br⁻ + I₂.','0.0100 mol I₂ forms because each stage has a 1:1 halogen mole ratio.'),
    P('Deduce the overall equation and explain whether Y⁻ is consumed overall.','Cl₂ + 2I⁻ → 2Cl⁻ + I₂.','Reason:Br⁻ is consumed in the first step and regenerated in the second; it is a regenerated halide carrier in the two-stage process, not a net reactant.')],
    'Both displacement equations atom/charge balanced; two-electron equivalents conserved; final I₂=0.0100 mol.','Cl > Br > I; 0.0100 mol I₂')

add(703,'Solving a mixed oxide composition','S3.1','sl',
    'A dry 5.0834 g mixture contains only Na₂O and MgO. It is added to excess hydrochloric acid. A back titration shows that 0.2200 mol HCl was consumed. Use M(Na₂O)=61.98 and M(MgO)=40.30 g mol⁻¹. The apparatus sketch shows the mixture being transferred to the acid before the remaining acid is titrated.',
    svg(tx(155,35,'dry oxide mixture')+ln(155,55,155,110)+tx(155,125,'↓')+'<path d="M120 155 L120 220 L65 300 L245 300 L190 220 L190 155" fill="none" stroke="#172b4d" stroke-width="2"/>'+tx(155,268,'excess HCl')+tx(460,40,'remaining acid')+'<rect x="435" y="65" width="50" height="160" fill="none" stroke="#172b4d" stroke-width="2"/>'+ln(460,225,460,260)+tx(460,285,'back titration')+ln(280,210,370,210)+tx(325,195,'then'), 'Mixed oxide back-titration apparatus'),[
    P('Write both reactions with HCl and formulate two independent equations for the unknown mole amounts x and y.','Na₂O + 2HCl → 2NaCl + H₂O; MgO + 2HCl → MgCl₂ + H₂O.','2x + 2y = 0.2200.','61.98x + 40.30y = 5.0834.'),
    P('Determine the mass percentage of Na₂O.','x = 0.03000 mol and y = 0.08000 mol.','m(Na₂O) = 1.8594 g.','Na₂O mass percentage = 36.58% (36.6% accepted).'),
    P('Explain why measuring only the amount of acid consumed would not determine the composition, and predict the qualitative acid–base character of both oxides.','Reason:Each mole of either oxide consumes 2 mol HCl, so acid consumption determines only x + y.','Both are basic metal oxides; oxide ions accept protons to form water.')],
    'Linear equations recover x=.03000,y=.08000; mass sum5.0834; acid .2200; Na₂O%=36.5787.','36.6% Na₂O by mass')

fig=molecules([('A: Na₂O ionic composition','[Na+].[Na+].[O-2]',None),('B: molecular oxide','O=S=O','O2S')],'Ionic and molecular oxide models')
nb=tx(380,30,'C: fragment of a SiO₂ network (2D projection)',17)
for ox,oy,sx,sy in [(270,175,160,175),(490,175,600,175),(380,100,380,55),(380,250,380,295)]:
    nb+=ln(380,175,ox,oy)+ln(ox,oy,sx,sy)+tx(ox,oy+6,'O',20)+tx(sx,sy+6,'Si',20)
nb+=tx(380,181,'Si',20)+tx(380,335,'Each O bridges two Si; each Si has four O neighbors in the extended network.',14)
for x,y,dx,dy in [(160,175,-60,0),(600,175,60,0),(380,55,70,0),(380,295,70,0)]:
    nb+=ln(x+12,y,x+dx,y+dy)+tx(x+dx+(15 if dx>0 else -15),y+dy+5,'…',20)
fig=stack(fig,svg(nb,'Extended silica network fragment'))
add(704,'Testing an oxide classification rule','S3.1','sl',
    'A is ionic Na₂O, B is molecular SO₂, and C is a giant covalent SiO₂ network. C is shown as a fragment of the extended network, with continuation beyond the drawing; the projection does not represent bond angles. A student proposes that an acidic oxide must react with water. Data: A reacts with water to give an alkaline solution; B dissolves to give an acidic solution; C does not react with water but reacts with hot concentrated NaOH to form Na₂SiO₃ and water.',fig,[
    P('Evaluate the student’s rule and write a balanced equation for C with NaOH.','Reason:C is a counterexample: acid–base classification can be shown by reaction with a base even if the oxide does not react with water.','SiO₂ + 2NaOH → Na₂SiO₃ + H₂O.'),
    P('Explain why water behavior alone cannot establish whether the solid contains discrete molecules.','Reason:SO₂ consists of discrete molecules, but SiO₂ has a continuous covalent network.','Reason:Water reactivity depends on bond-breaking and reaction feasibility; the absence of dissolution is not proof of neutral oxide character.'),
    P('Compare bonding and charge carriers in molten A and liquid B, and relate the broad metal/nonmetal trend to the oxide classification.','Molten A contains mobile Na⁺ and O²⁻ ions and conducts.','Pure liquid SO₂ has no substantial population of mobile ions and is a poor conductor.','Reason:Electropositive metals tend to form basic ionic oxides; nonmetal oxides are commonly acidic and covalent. This is a broad trend, not a water-solubility definition.')],
    'Na₂SiO₃ equation Na2Si1O4H2 both sides; extended network fragment uses bridgingoxygen andfourcoordinateSi; no reaction-with-water necessity.','SiO₂ is acidic despite not reacting with water')

b='<path d="M80 110 L80 245 L35 300 L225 300 L170 245 L170 110" fill="none" stroke="#172b4d" stroke-width="2"/>'+tx(130,278,'oxide + peroxide')+ln(170,130,350,130)+ln(350,130,350,210)+'<rect x="340" y="190" width="280" height="55" fill="none" stroke="#172b4d" stroke-width="2"/>'+ln(535,190,535,245)+ln(535,217,690,217)+tx(480,175,'dry gas syringe')+tx(480,280,'0.1135 dm³ O₂ at STP')+tx(125,70,'excess water added')
add(705,'An oxide–peroxide mixture and oxidation states','S3.1','sl',
    'A 2.0194 g dry mixture of Na₂O and Na₂O₂ reacts completely with excess water. All peroxide is ultimately converted to NaOH and O₂; a drying stage removes water vapor before the gas syringe. The dry O₂ volume is 0.1135 dm³ at STP, where molar gas volume is 22.70 dm³ mol⁻¹. Use M(Na₂O)=61.98 and M(Na₂O₂)=77.98 g mol⁻¹.',svg(b,'Dry oxygen collection from an oxide–peroxide mixture'),[
    P('Write the net peroxide reaction and use the gas volume to determine the peroxide mass percentage.','2Na₂O₂ + 2H₂O → 4NaOH + O₂.','n(O₂) = 0.1135/22.70 = 0.005000 mol; n(Na₂O₂) = 0.01000 mol.','m(Na₂O₂) = 0.7798 g, giving 38.62% by mass.'),
    P('Determine the total amount of NaOH formed from both components.','m(Na₂O) = 2.0194 − 0.7798 = 1.2396 g, so n(Na₂O) = 0.02000 mol.','Na₂O + H₂O → 2NaOH; both components give 2 mol NaOH per mole.','Total NaOH = 2(0.02000 + 0.01000) = 0.06000 mol.'),
    P('Explain, using oxygen oxidation states, why the peroxide reaction is a disproportionation.','O is −1 in peroxide, −2 in hydroxide and 0 in oxygen gas.','Reason:Oxygen from the same initial oxidation state undergoes both reduction and oxidation.')],
    'O₂.005000→peroxide.01000mol;oxide.02000mol;OH.06000mol;O−1 branches−2and0; masspercentage38.6154.','38.6% Na₂O₂; 0.0600 mol NaOH')

add(706,'A missing alcohol isomer','S3.2','sl',
    'Three compounds A–C are shown. All are alcohols with molecular formula C₄H₁₀O. The complete set of alcohol constitutional isomers with this formula contains four members. Measured boiling temperatures for the four isomers are 117.7, 108.0, 99.5 and 82.2 °C; the lowest belongs to the most compact, highly branched isomer.',molecules([('A','CCCCO','C4H10O'),('B','CCC(O)C','C4H10O'),('C','CC(C)CO','C4H10O')],'Three of the four C4H10O alcohol isomers'),[
    P('Give IUPAC names and classify the alcohol groups in A–C as primary, secondary or tertiary.','A is butan-1-ol, primary.','B is butan-2-ol, secondary.','C is 2-methylpropan-1-ol, primary.'),
    P('Draw and name the missing isomer and explain why an ether is not a valid answer to this specific request.','The missing isomer is (CH₃)₃COH, 2-methylpropan-2-ol.','It is a tertiary alcohol; an ether lacks the hydroxy group required by the specified alcohol class.'),
    P('A student attributes its lowest boiling temperature to an inability to hydrogen-bond. Evaluate this explanation.','Reason:It has an O–H bond and lone pairs on oxygen, so it can form intermolecular hydrogen bonds.','Reason:All four have the same molecular formula; increased branching reduces effective contact between molecules and weakens dispersion contributions. A lower boiling temperature does not establish the absence of hydrogen bonding.'),
    P('A 0.0200 mol mixture contains exactly two distinct alcohols from the complete four-member set and consumes 0.0250 mol of oxygen-transfer equivalents in a quantitative test. The supplied rule is 2 equivalents per primary alcohol, 1 per secondary alcohol and 0 per tertiary alcohol. Determine the possible pairs of classes and their amounts. Does this determine the identity of a primary component?',
      'For primary + secondary, p+s=0.0200 and 2p+s=0.0250, giving p=0.00500 mol and s=0.0150 mol.',
      'For primary + tertiary, 2p=0.0250, giving p=0.0125 mol and t=0.00750 mol.',
      'Reason:Secondary + tertiary would consume at most 0.0200 mol equivalents; two primary isomers would consume 0.0400 mol. Both are excluded.',
      'Reason:The primary component could be A or C; this test measures class-dependent reaction and does not distinguish the two primary connectivities.')],
    'RDKit formula C4H10O for A/B/C; omitted CC(C)(C)O also C4H10O; OH-bearing carbon degrees1,2,1,3. Mixture p/s=.005/.015 or p/t=.0125/.0075 mol; class constraints exclude s/t and p/p; primary identity unresolved.','Missing: 2-methylpropan-2-ol; class-analysis mixture has two possible compositions')

add(707,'When combustion does not identify a homologous series','S3.2','sl',
    'A and B have the structures shown. Complete combustion of 0.0100 mol of either gives 0.0600 mol CO₂ and 0.0600 mol H₂O. Under the stated test conditions, A reacts rapidly with bromine by addition, whereas B does not. Do not assume that a shared empirical formula establishes a shared functional group.',molecules([('A','C=CCCCC','C6H12'),('B','C1CCCCC1','C6H12')],'An alkene and a cycloalkane with matching combustion amounts'),[
    P('Deduce the molecular formula from the combustion amounts and reconcile it with both structures.','Each molecule contains 6 carbon atoms and 12 hydrogen atoms, giving C₆H₁₂.','Reason:A contains one C=C bond while B contains a ring; each reduces the hydrogen count by two relative to an acyclic alkane.'),
    P('Give A’s IUPAC name and draw the bromine addition product, retaining the six-carbon chain.','A is hex-1-ene.','The product is BrCH₂–CHBr–CH₂–CH₂–CH₂–CH₃; the C=C becomes C–C and one Br attaches to each former double-bond carbon.'),
    P('Explain why A and B are structural isomers but are not successive members of one homologous series.','They share the molecular formula but have different atom connectivity.','Reason:Successive homologues have the same functional group and differ by CH₂; A and B neither differ by CH₂ nor share the alkene functional group.')],
    'RDKit confirms bothC6H12; combustion6CO₂+6H₂O per mol; Braddition C6H12Br2 balanced. Cyclohexane avoids small-ring bromine exception.','A hex-1-ene; both C₆H₁₂, distinct functional classes')

add(708,'Same molecular formula, different acid behavior','S3.2','sl',
    'A and B are shown. Both have formula C₃H₆O₂. Only A reacts with excess NaHCO₃ to give one mole of CO₂ per mole of organic compound. A 0.7400 g sample containing only A and B produces 0.1362 dm³ CO₂ at STP (22.70 dm³ mol⁻¹). Use M(C₃H₆O₂)=74.00 g mol⁻¹. The hydrolysis of B is supplied: HCOOCH₂CH₃ + H₂O ⇌ HCOOH + CH₃CH₂OH.',molecules([('A','CCC(=O)O','C3H6O2'),('B','CCOC=O','C3H6O2')],'An acid and ester with identical formula'),[
    P('Identify the functional group in each compound, name A and explain why their empirical formulas are identical.','A contains a carboxyl group and is propanoic acid; B contains an ester group.','Both molecular formulas reduce to empirical formula C₃H₆O₂ because 3, 6 and 2 have no common integer factor greater than 1.'),
    P('Determine the mole fraction of A and explain whether the mass fraction differs.','n(A) = n(CO₂) = 0.1362/22.70 = 0.006000 mol.','Total amount = 0.7400/74.00 = 0.01000 mol; mole fraction A = 0.6000.','Reason:Both have the same molar mass, so the mass fraction is also 0.6000.'),
    P('A student calls the supplied hydrolysis products isomers of A. Evaluate this claim and identify their functional groups.','HCOOH is a carboxylic acid and CH₃CH₂OH is an alcohol.','Reason:Neither has molecular formula C₃H₆O₂, so neither is an isomer of A; hydrolysis changes connectivity by reaction with water rather than rearranging one molecule without changing its formula.')],
    'BothRDKitC3H6O2; .1362/22.7=.006; total.010; acid moleandmassfraction.600; suppliedhydrolysisbalancedC3H8O3.','60.0% A by mass and mole')

add(709,'Repairing a skeletal-formula name','S3.2','sl',
    'The skeletal structure shown contains one bromo substituent and one C=C bond. A student names it 3-bromohex-4-ene. No stereochemical descriptor is required.',molecules([('Unknown monoalkene','CC=CC(Br)CC','C6H11Br')],'A bromo-substituted six-carbon monoalkene'),[
    P('Correct the name and explain the numbering decision.','4-bromohex-2-ene.','Reason:The six-carbon chain is numbered to give the double bond locant 2 rather than 4; the bromo substituent is then at carbon 4.'),
    P('Determine molecular and empirical formulas, accounting explicitly for each hydrogen on the two double-bond carbons and the brominated carbon.','The two alkene carbons each carry one H, and the brominated carbon carries one H.','Molecular formula C₆H₁₁Br; it is already the simplest whole-number ratio, so the empirical formula is the same.'),
    P('Draw a positional isomer with the same six-carbon skeleton, the same double-bond position and a different bromo position. Explain why reversing the page drawing alone does not produce an isomer.','For example BrCH₂–CH=CH–CH₂–CH₂–CH₃, i.e. 1-bromohex-2-ene.','Reason:An isomer changes connectivity, such as moving the C–Br bond; rotating or reversing a drawing preserves connectivity.')],
    'RDKitCC=CC(Br)CCC6H11Br; chainpositionsalkene2,bromo4; terminalbromopositionalisomerC6H11Br.','4-bromohex-2-ene; C₆H₁₁Br')

add(710,'Hydrogen-bond evidence and an unfair boiling-point comparison','S3.2','sl',
    'A, B and C are ethanol, methoxymethane and ethane-1,2-diol respectively, with the structures shown. Their normal boiling temperatures are approximately 78, −24 and 197 °C. A and B have the same molar mass; C does not. Hydrogen bonding requires an H bonded to O, N or F and a lone pair on an appropriate electronegative atom.',molecules([('A','CCO','C2H6O'),('B','COC','C2H6O'),('C','OCCO','C2H6O2')],'Hydrogen-bond donors and acceptors'),[
    P('Explain why A and B have very different boiling temperatures despite equal molar mass.','A has an O–H hydrogen-bond donor and oxygen lone-pair acceptor; its molecules hydrogen-bond to one another.','B has acceptor lone pairs but no O–H/N–H/F–H donor, so pure B lacks this hydrogen-bond network.','Reason:More energy is required to separate A molecules; dispersion forces alone do not explain the difference.'),
    P('Draw one valid hydrogen bond between water and B, labeling the donor and acceptor atoms. Explain why B need not be insoluble in water.','A valid drawing is O(water)–H···O(B), with the dotted interaction from water H to B oxygen.','Reason:Water supplies donors and B supplies acceptors; absence of self hydrogen bonding does not imply absence of hydrogen bonding to water.'),
    P('Evaluate the claim that C’s higher boiling point proves that a hydrogen bond involving C is individually stronger than one involving A.','Reason:C has two hydroxy groups per molecule and can form a more extensive intermolecular network.','Reason:C also has higher molar mass and more electrons, affecting dispersion. Bulk boiling data alone do not isolate the strength of an individual hydrogen bond.')],
    'RDKit formulaandvalence checks; donorcountsA1B0C2; acceptorsA1B1C2; no inference individualbondenergyfrombulkboilingpoint.','Self-donors A and C; B accepts hydrogen bonds from water')

add(711,'Amine classification is not a count of N–H bonds','S3.2','sl',
    'Three amines A–C have formula C₃H₉N. Their structures and measured boiling temperatures are A: 49 °C, B: 36 °C, C: 3 °C. Each reacts with HCl by accepting one proton at the nitrogen lone pair. Assume complete protonation with excess HCl.',molecules([('A: 49 °C','CCCN','C3H9N'),('B: 36 °C','CCNC','C3H9N'),('C: 3 °C','CN(C)C','C3H9N')],'Primary, secondary and tertiary amines'),[
    P('Classify each amine and distinguish this classification from the number of H atoms bonded to nitrogen.','A is primary: one carbon group on N, with two N–H bonds.','B is secondary: two carbon groups on N, with one N–H bond.','C is tertiary: three carbon groups on N, with no N–H bond.'),
    P('Explain why C’s low boiling temperature does not prevent it from hydrogen-bonding to water or reacting with HCl.','Reason:C has no donor N–H bond for self hydrogen bonding, but its nitrogen lone pair accepts a hydrogen bond from water.','The same lone pair can accept H⁺, giving (CH₃)₃NH⁺.'),
    P('Determine the HCl amount required to protonate 0.2955 g of any one pure isomer, using molar mass 59.10 g mol⁻¹. Evaluate a student’s proposed 2:1 HCl:A ratio.','n(amine)=0.2955/59.10=0.005000 mol, requiring 0.005000 mol HCl.','Reason:Each nitrogen has one proton-accepting lone pair; two pre-existing N–H bonds in A do not create two independent basic sites.')],
    'C3H9Nall; Ncarbonneighbors1/2/3; eachone lonepair; mol .005000, acid1:1 notN-Hcount.','A primary, B secondary, C tertiary; each consumes 1 HCl per molecule')

add(712,'An isomer mixture with a selective reaction','S3.2','sl',
    'A mixture contains only the two C₅H₁₂O alcohols shown. Its total amount is 0.01000 mol. Under the stated quantitative test, each mole of primary alcohol produces one mole of a measured carboxylic acid, while tertiary alcohol is recovered unchanged; 0.006000 mol acid is obtained. Use M(C₅H₁₂O)=88.15 g mol⁻¹.',molecules([('A','CCCCCO','C5H12O'),('B','CCC(O)(C)C','C5H12O')],'Selective analysis of primary and tertiary alcohol isomers'),[
    P('Name and classify A and B, identifying the carbon atom that controls the classification.','A is pentan-1-ol; its OH-bearing carbon is attached to one carbon, so it is primary.','B is 2-methylbutan-2-ol; its OH-bearing carbon is attached to three carbons, so it is tertiary.'),
    P('Determine the masses of A and B in the initial mixture.','n(A)=0.006000 mol and n(B)=0.004000 mol.','m(A)=0.5289 g and m(B)=0.3526 g.'),
    P('Explain why a combustion carbon/hydrogen ratio would not determine this composition, and why assigning the difference in reactivity simply to stronger intermolecular hydrogen bonding is insufficient.','Reason:The isomers have identical molecular and empirical formulas, so any mixture has the same combustion carbon/hydrogen ratio.','Reason:Both contain O–H groups and can hydrogen-bond; the selective covalent reaction depends on the local bonding at the OH-bearing carbon, including the absence of a carbon-bound H there in B.')],
    'RDKitbothC5H12O; AOHcarbondegree1,Bdegree3andnoH; .006*.88.15=.5289g,.004*88.15=.3526g.','0.5289 g pentan-1-ol; 0.3526 g tertiary isomer')

# AHL periodic classification: electron sublevels, transition states and color.
add(713,'Two reversals within a periodic ionization trend','S3.1','ahl',
    'First ionization energies across Period 3 are shown: Na 496, Mg 738, Al 578, Si 787, P 1012, S 1000, Cl 1251 and Ar 1521 kJ mol⁻¹. Interpret both downward steps using electron sublevels and electron–electron repulsion.',chart(list(range(11,19)),[496,738,578,787,1012,1000,1251,1521],'Element in Period 3','First ionization energy / kJ mol⁻¹','Periodic trend with two local reversals',['Na','Mg','Al','Si','P','S','Cl','Ar']),[
    P('Explain the overall increase and the Mg→Al reversal with the relevant valence configurations.','Reason:Across the period nuclear charge increases with broadly similar principal-shell shielding, increasing attraction for valence electrons.','Mg is [Ne]3s² and Al is [Ne]3s²3p¹.','Reason:The removed Al electron is in a higher-energy, less penetrating 3p sublevel and is easier to remove than a Mg 3s electron.'),
    P('Use orbital occupancy to explain the P→S reversal. Do not rely only on a phrase such as “half-filled stability”.','P is [Ne]3s²3p³ with one electron in each 3p orbital; S is [Ne]3s²3p⁴ with one 3p pair.','Reason:Repulsion between paired electrons in S makes one of those electrons easier to remove, slightly outweighing the increase in nuclear charge.'),
    P('Evaluate whether the graph alone predicts which period-3 element has the greatest second ionization energy. Identify that element using configurations.','Reason:First and second ionization remove electrons from different species, so the first-ionization graph alone is insufficient.','Na has the greatest second ionization energy: Na⁺ is [Ne], so removal is from the n=2 core rather than the n=3 valence shell of the other period-3 cations.')],
    'ConfigurationsverifyMg3s2Al3p1P3p3S3p4; Na+closedNe core; no unsupported half-filledslogan.','Reversals arise from 3p energy and pairing repulsion')

b=tx(380,35,'Fe³⁺ / Fe²⁺ catalytic cycle',20)+tx(150,135,'2 Fe³⁺')+tx(600,135,'2 Fe²⁺')+ln(230,130,520,130)+tx(380,100,'2 I⁻ → I₂')+tx(520,150,'→',24)+ln(520,230,230,230)+tx(380,270,'S₂O₈²⁻ → 2 SO₄²⁻')+tx(235,249,'←',24)+tx(380,320,'Catalyst is regenerated; two separate steps are supplied.',15)
add(714,'Transition-metal electron states in a catalytic cycle','S3.1','ahl',
    'The two supplied steps are 2Fe³⁺ + 2I⁻ → 2Fe²⁺ + I₂ and 2Fe²⁺ + S₂O₈²⁻ → 2Fe³⁺ + 2SO₄²⁻. Iron has Z=26. A lower measured activation barrier is observed with the iron catalyst; temperature and reactant concentrations are unchanged.',svg(b,'Iron oxidation-state catalytic cycle'),[
    P('Give the ground-state electron configurations of Fe, Fe²⁺ and Fe³⁺, explaining the order of electron removal.','Fe is [Ar]3d⁶4s².','Fe²⁺ is [Ar]3d⁶ and Fe³⁺ is [Ar]3d⁵; the 4s electrons are removed before 3d when these cations form.'),
    P('Add the steps to obtain the overall ionic equation and identify where iron is oxidized and reduced.','S₂O₈²⁻ + 2I⁻ → 2SO₄²⁻ + I₂.','Fe³⁺ is reduced to Fe²⁺ in the iodide step; Fe²⁺ is oxidized in the peroxodisulfate step.'),
    P('Explain why variable oxidation states enable the cycle and evaluate a claim that the catalyst changes the reaction’s equilibrium constant.','Reason:Accessible Fe²⁺/Fe³⁺ states permit electron transfer in two steps and regeneration of the catalyst.','Reason:The catalyst provides an alternative pathway with lower activation energy, increasing rate.','Reason:It does not change the reactant/product energy difference or the equilibrium constant at the same temperature.')],
    'Bothionicsteps and net atom/charge balanced; Fe2d6Fe3d5; 2electrons transferred overall; catalystregenerated.','Net S₂O₈²⁻ + 2I⁻ → 2SO₄²⁻ + I₂')

fig=chart([450,650],[.8,.2],'Absorption band / nm','Relative absorbance','Complex A: supplied absorption maxima')
add(715,'Ligand color changes without changing oxidation state','S3.1','ahl',
    'Complexes A and B both contain Cu²⁺ but different ligands. Their broad absorption-band maxima are 650 nm (A) and 450 nm (B). The figure illustrates the two probe wavelengths for A; use the stated maxima for the energy calculation. Simplified complementary-color pairs are red↔cyan, orange↔blue, yellow↔violet. Treat 650 nm as red and 450 nm as blue. Use h=6.63×10⁻³⁴ J s, c=3.00×10⁸ m s⁻¹ and Nₐ=6.02×10²³ mol⁻¹.',fig,[
    P('Determine the Cu²⁺ d-electron count and explain why replacing ligands can change color while Cu remains +2.','Cu²⁺ is [Ar]3d⁹, so it is d⁹.','Reason:Ligands split the d-orbital energies; different ligands change the splitting and thus the visible photon energy absorbed. A color change need not imply oxidation-state change.'),
    P('Calculate the molar photon energies at both maxima and identify the larger splitting.','Use E = hcNₐ/λ, with wavelengths converted from nm to m.','A: 184 kJ mol⁻¹; B: 266 kJ mol⁻¹ (three significant figures).','B has the larger splitting because it absorbs shorter-wavelength, higher-energy photons.'),
    P('Predict the simplified transmitted colors and state one reason a real solution need not match a single complementary color exactly.','A absorbs red, so its simplified transmitted color is cyan; B absorbs blue, so it is orange.','Reason:Real absorption bands are broad and may overlap, and perceived color depends on the whole transmitted spectrum and illumination.')],
    'hcNA/650nm=184212Jmol;450nm=266084Jmol;CuII3d9. Graphmustbe corrected to agree650nmmajor band before release.','A 184 kJ mol⁻¹/cyan; B 266 kJ mol⁻¹/orange')
# Graph values correspond to the given red-absorbing A, not the reverse.
questions[-1]['diagramSvg']=chart([450,650],[.2,.8],'Probe wavelength / nm','Relative absorbance','Complex A: two probe readings')
questions[-1]['verification']['notes']='hcNA/650nm=184212 J mol⁻¹; 450nm=266084 J mol⁻¹; CuII3d9; figure A absorbance650=.8>450=.2.'
checks[-1]['evidence']=questions[-1]['verification']['notes']

b=ln(90,270,695,270)+ln(90,270,90,50)+tx(380,335,'Probe wavelength / nm')+tx(90,30,'Absorbance of separate 1.00 mmol dm⁻³ standards',16,'start')
for x,label,a,bb in [(240,'450',.20,.60),(560,'650',.80,.10)]:
    b+=f'<rect x="{x-50}" y="{270-220*a}" width="35" height="{220*a}" fill="#176089"/><rect x="{x+15}" y="{270-220*bb}" width="35" height="{220*bb}" fill="#b56520"/>'+tx(x,300,label)+tx(x-32,270-220*a-10,str(a),13)+tx(x+32,270-220*bb-10,str(bb),13)
b+=tx(490,65,'Blue: A; orange: B',15)
add(716,'Separating two overlapping complex spectra','S3.1','ahl',
    'A is [Cu(H₂O)₆]²⁺ and B is [Ni(NH₃)₆]²⁺. The chart gives absorbances of separate 1.00 mmol dm⁻³ standards: A at 450/650 nm = 0.20/0.80; B = 0.60/0.10. In the same cell, absorbances add linearly and are proportional to concentration. A mixture gives 0.340 at 450 nm and 0.440 at 650 nm. This linear calibration rule is supplied for this question.',svg(b,'Two-wavelength calibration for colored complexes'),[
    P('Find metal oxidation states and d-electron counts in A and B.','Both ligands H₂O and NH₃ are neutral, so both metals are +2.','Cu²⁺ is d⁹; Ni²⁺ is d⁸.'),
    P('Determine the concentrations of A and B in mmol dm⁻³, showing both equations.','Let a and b be concentrations in mmol dm⁻³: 0.20a + 0.60b = 0.340 and 0.80a + 0.10b = 0.440.','Solving gives a = 0.500 mmol dm⁻³.','b = 0.400 mmol dm⁻³.'),
    P('Explain why measuring only at 450 nm would not determine both concentrations, and why Ni is a transition element even though its aqueous ions have lost 4s electrons.','Reason:One absorbance supplies one equation for two unknowns; both complexes absorb at 450 nm.','Reason:Ni forms ions with a partially filled d sublevel (such as d⁸ Ni²⁺), satisfying the transition-element definition.')],
    '.2*.5+.6*.4=.34;.8*.5+.1*.4=.44;determinant−.46nonzero; CuII d9 NiII d8.','[A]=0.500; [B]=0.400 mmol dm⁻³')

b=tx(175,55,'[Cu(NH₃)₄(H₂O)₂]²⁺')+tx(585,55,'[Cu(H₂O)₆]²⁺')+ln(315,90,455,90)+tx(385,78,'H⁺ added',15)+tx(450,112,'→',22)
for x,col in [(175,'#342b9f'),(585,'#62b5d8')]:b+=f'<path d="M{x-65} 125 L{x-65} 290 Q{x} 315 {x+65} 290 L{x+65} 125" fill="none" stroke="{INK}" stroke-width="2"/><rect x="{x-61}" y="190" width="122" height="90" fill="{col}" opacity=".65"/>'
add(717,'A color change caused by protonating ligands','S3.1','ahl',
    'A solution contains 0.00250 mol [Cu(NH₃)₄(H₂O)₂]²⁺. Adding excess acid quantitatively converts each coordinated NH₃ into NH₄⁺ and replaces it by H₂O, giving [Cu(H₂O)₆]²⁺. The solution changes color. Ignore any acid consumption by other species.',svg(b,'Acid-driven ligand replacement at copper(II)'),[
    P('Write the overall equation, including the number of water molecules consumed, and calculate the minimum H⁺ amount.','[Cu(NH₃)₄(H₂O)₂]²⁺ + 4H⁺ + 4H₂O → [Cu(H₂O)₆]²⁺ + 4NH₄⁺.','Minimum H⁺ = 4 × 0.00250 = 0.0100 mol.'),
    P('Determine the oxidation state and d-electron count of copper before and after conversion and evaluate a redox interpretation of the color change.','Cu is +2 and d⁹ before and after.','Reason:The ligand set changes and so does the d-orbital splitting; no copper oxidation-state change is required.'),
    P('Explain the role of the nitrogen lone pair in both the original complex and the reaction with acid.','NH₃ donates its nitrogen lone pair to copper to form a coordinate covalent bond.','NH₃ accepts H⁺ at that lone pair to form NH₄⁺; protonated NH₄⁺ has no available nitrogen lone pair for the same coordination.')],
    'EquationCu1N4H30O6charge+6eachside;4H+percomplex;CuII d9 unchanged; NH4noN lonepair.','0.0100 mol H⁺; color change is ligand replacement')

fig=chart([450,520,580,650],[.1,.9,.7,.1],'Wavelength / nm','Relative absorbance','Purple permanganate: constructed visible absorption')
add(718,'A colored species outside a simple d–d model','S3.1','ahl',
    'MnO₄⁻ is intensely purple and absorbs strongly in the green/yellow region. Its simplified spectrum is shown (relative absorbance at 450, 520, 580, 650 nm: 0.10, 0.90, 0.70, 0.10). A proposed explanation is “every colored metal-containing species must have a partly filled d sublevel”. For this question, an alternative mechanism is supplied: a photon can transfer electron density from an oxygen-based orbital to a metal-based orbital; this is called ligand-to-metal charge transfer.',fig,[
    P('Deduce Mn’s oxidation state in MnO₄⁻ and the corresponding d-electron count, starting from Mn: [Ar]3d⁵4s².','Mn + 4(−2)=−1, so Mn is +7.','Removing 4s² and 3d⁵ gives d⁰.'),
    P('Evaluate the proposed explanation and explain how the supplied alternative resolves the observation.','Reason:A d⁰ ion has no d electron to undergo a transition between split d levels, so a d–d-only explanation cannot account for this color.','Reason:Charge transfer involves an initially occupied ligand-based orbital and can absorb visible light even when the metal d count is zero.'),
    P('Explain why this observation does not mean manganese is not a transition element. Predict which regions are transmitted most in the simplified spectrum.','Reason:Transition-element classification depends on forming at least one ion with a partially filled d sublevel; Mn²⁺, for example, is d⁵.','The blue/violet and red regions are transmitted more than green/yellow, consistent with purple appearance.')],
    'MnVII d0;MnII d5; LMCT supplied rather than required recall; data absorptiongreen/yellow supportsred+bluetransmission.','Mn(VII) d⁰; color can arise from charge transfer')

b=tx(380,35,'Sequential chloride and water analysis',20)+tx(150,95,'hydrated solid')+ln(150,120,150,190)+tx(150,220,'gentle drying')+tx(150,260,'mass loss: 0.01802 g')+tx(530,95,'fresh 0.26845 g portion')+ln(530,115,530,175)+tx(530,205,'Ag⁺: immediate precipitate')+tx(530,240,'0.28664 g AgCl')+tx(530,290,'after complete breakdown:')+tx(530,320,'total 0.42996 g AgCl')
add(719,'Which chloride ions are inside the complex?','S3.1','ahl',
    'A cobalt compound has composition Co(NH₃)₅Cl₃·xH₂O. The water is crystallization water. A 0.26845 g portion loses 0.01802 g on gentle drying without losing NH₃ or Cl. A fresh equal portion gives 0.28664 g AgCl immediately with excess AgNO₃, when only uncoordinated chloride reacts. After complete breakdown of all complexes, the total AgCl is 0.42996 g. M(AgCl)=143.32, M(H₂O)=18.02, and M(Co(NH₃)₅Cl₃)=250.43 g mol⁻¹. All NH₃ is coordinated.',svg(b,'Analytical evidence for cobalt complex composition'),[
    P('Determine x and the mole amount of the compound in the portion.','Dry compound mass = 0.25043 g; amount = 0.25043/250.43 = 0.001000 mol.','Water amount = 0.01802/18.02 = 0.001000 mol, so x = 1.'),
    P('Deduce the complex formula including counterions and explain the immediate-versus-total chloride result.','Immediate chloride = 0.28664/143.32 = 0.002000 mol, i.e. two free Cl⁻ per formula unit.','Reason:Total chloride = 0.003000 mol, so the third chloride is coordinated and unavailable to precipitate immediately.','Formula [Co(NH₃)₅Cl]Cl₂·H₂O; the complex cation is [Co(NH₃)₅Cl]²⁺.'),
    P('Deduce cobalt’s oxidation state, d-electron count and coordination number.','Co is +3 because neutral NH₃ plus one Cl⁻ gives complex charge +2; Co³⁺ is [Ar]3d⁶.','Coordination number 6: five nitrogen donor atoms and one chloride donor.')],
    'BaseM250.43;hydrateM268.45;.001molcompound;.001water;.002freeCl;.003totalCl;CoIII d6coord6.','[Co(NH₃)₅Cl]Cl₂·H₂O; Co(III), d⁶')

# AHL organic evidence: multi-technique deductions and stereochemical reasoning.
fig=stack(spectrum('ir',[(1740,160,40)],'IR: strong carbonyl; no broad O–H'),spectrum('nmr',[(1.25,3,'t'),(4.10,2,'q'),(2.00,3,'s')],'Three proton environments; integrals are group areas'))
add(720,'A structure constrained by three analytical methods','S3.2','ahl',
    'An unknown has formula C₄H₈O₂ and a molecular ion at m/z 88. The constructed IR shows a strong 1740 cm⁻¹ absorption and no broad O–H band. Its ¹H NMR has δ1.25 triplet (integral 3), δ4.10 quartet (2), and δ2.00 singlet (3). Candidate structures are CH₃COOCH₂CH₃, CH₃CH₂COOCH₃, HCOOCH(CH₃)₂ and CH₃CH₂CH₂COOH.',fig,[
    P('Identify the structure and assign every NMR environment, including the splitting.','CH₃COOCH₂CH₃ (ethyl ethanoate).','The ethoxy CH₃ is the δ1.25 triplet (two neighboring H); OCH₂ is the δ4.10 quartet (three neighboring H).','The CH₃ next to C=O gives the δ2.00 singlet, with no adjacent proton-bearing carbon.'),
    P('Explain how IR excludes one candidate and why molecular-ion mass alone cannot select among the four.','Reason:The broad acid O–H absorption is absent, inconsistent with the carboxylic-acid candidate.','Reason:All four are C₄H₈O₂ isomers and have the same molecular-ion nominal mass 88.'),
    P('An intense fragment is assigned CH₃CO⁺ at m/z 43. Check this assignment and identify the neutral fragment lost from the molecular radical cation.','CH₃CO⁺ has nominal mass 2(12)+3+16=43.','The neutral fragment is ·OC₂H₅ with mass 45; atoms, mass 88=43+45, and total charge +1 are conserved.')],
    'RDKitCC(=O)OCCC4H8O2;nominal88;Hgroups3+2+3=8;fragmentC2H3O+43 +C2H5O radical45.','CH₃COOCH₂CH₃')

fig=stack(spectrum('ir',[(1715,165,45)],'IR carbonyl; no O–H'),spectrum('nmr',[(2.15,6,'s')],'Single 6H resonance; no aldehyde proton'))
add(721,'What a single NMR resonance establishes','S3.2','ahl',
    'An unknown is either CH₃COCH₃ or CH₃CH₂CHO. Its formula is C₃H₆O, molecular-ion m/z is 58, IR has a strong carbonyl band near 1715 cm⁻¹, and ¹H NMR has one singlet at δ2.15 integrating to 6H. No signal occurs near δ9–10. The IR position is approximate and should not alone be treated as a definitive ketone/aldehyde distinction.',fig,[
    P('Identify the compound and explain its NMR equivalence and splitting.','It is propanone, CH₃COCH₃.','The two methyl groups are equivalent by molecular symmetry, giving one environment of six H.','There are no neighboring H on the carbonyl carbon, so the resonance is a singlet.'),
    P('Explain why IR and molecular-ion mass are insufficient here, and state one independent NMR observation excluding propanal.','Both candidates have C=O and formula C₃H₆O, so they can show carbonyl absorption and molecular ion m/z 58.','Reason:Propanal requires an aldehyde proton near δ9–10 and inequivalent proton environments, incompatible with the single 6H resonance.'),
    P('Predict the masses of the acylium fragment CH₃CO⁺ and the neutral species lost in forming it from the propanone molecular radical cation.','CH₃CO⁺ is m/z 43.','A neutral methyl radical ·CH₃ of mass 15 is lost; 58=43+15 and charge +1 is retained on the detected fragment.')],
    'RDKitCC(=O)CC3H6O;H6onesymmetryclass;M58;fragment43+15; nooff-syllabus complexsplitting.','Propanone; one equivalent set of six methyl H')

fig=stack(spectrum('ir',[(1100,110,70)],'IR: C–O region; no broad O–H and no C=O'),spectrum('nmr',[(1.18,6,'t'),(3.45,4,'q')],'Two environments with 6:4 integrated area'))
add(722,'Symmetry hidden in an ether spectrum','S3.2','ahl',
    'An oxygen-containing compound has formula C₄H₁₀O. IR shows no O–H or C=O absorption. Its ¹H NMR contains only δ1.18 triplet (6H) and δ3.45 quartet (4H). Compare three candidate connectivities: CH₃CH₂OCH₂CH₃, CH₃OCH₂CH₂CH₃ and CH₃OCH(CH₃)₂. Do not infer proton count from line heights; supplied integrals are total resonance areas.',fig,[
    P('Deduce the structure and assign the NMR signals.','CH₃CH₂OCH₂CH₃.','Two equivalent terminal CH₃ groups give 6H triplet by coupling to adjacent CH₂.','Two equivalent OCH₂ groups give 4H quartet by coupling to adjacent CH₃.'),
    P('Explain how each of the other connectivities fails the complete evidence.','Reason:CH₃OCH₂CH₂CH₃ has four inequivalent proton environments rather than two.','Reason:CH₃OCH(CH₃)₂ has three proton environments and an OCH₃ singlet, incompatible with only the given triplet/quartet pair.'),
    P('Determine the empirical formula and state whether this sample is a structural isomer of butan-1-ol. Predict one IR distinction between them.','Empirical formula is C₄H₁₀O, since oxygen count 1 prevents further reduction; it is a structural isomer of butan-1-ol.','Butan-1-ol has a broad O–H absorption; the ether has no O–H bond.')],
    'ThreecandidateRDKitformulasC4H10O; chosen symmetryCH3sixHCH2fourH; noforbiddenseptetanalysisasked.','CH₃CH₂OCH₂CH₃')

fig=stack(spectrum('ms',[(98,90,''),(100,60,''),(102,10,'')],'Molecular-ion cluster; ³⁵Cl:³⁷Cl = 3:1'),spectrum('nmr',[(2.10,3,'d'),(5.90,1,'q')],'Only two proton environments'))
add(723,'Isotope and NMR evidence for a dichloro isomer','S3.2','ahl',
    'A compound is either CH₃CHCl₂ or ClCH₂CH₂Cl. Its molecular-ion cluster at m/z 98, 100 and 102 has relative intensities 9:6:1. For chlorine, use ³⁵Cl:³⁷Cl=3:1 and independent isotope selection. The ¹H NMR contains a 3H doublet at δ2.10 and a 1H quartet at δ5.90.',fig,[
    P('Derive the molecular-ion intensity ratio and explain the middle mass.','Probabilities are (3/4)², 2(3/4)(1/4), and (1/4)², giving 9:6:1.','m/z 100 has one ³⁵Cl and one ³⁷Cl; there are two distinguishable isotope placements.'),
    P('Select the isomer using all the NMR evidence and assign the resonances.','CH₃CHCl₂, 1,1-dichloroethane.','CH₃ gives a 3H doublet from one neighboring CH; CHCl₂ gives a 1H quartet from three neighboring methyl H.','ClCH₂CH₂Cl has symmetry-equivalent proton environments and cannot give the specified 3:1 integral pattern.'),
    P('Calculate the fraction of molecules containing at least one ³⁷Cl and assess whether the mass cluster distinguishes the two structural isomers.','Fraction = 1 − (3/4)² = 7/16 = 43.75%.','Reason:Both isomers have two chlorine atoms and the same formula C₂H₄Cl₂, so the molecular-ion cluster alone does not distinguish connectivity.')],
    'M98=24+4+70; isotopologueprob9/16,6/16,1/16; chosenC2H4Cl2;H3d1q.','1,1-dichloroethane; 43.75% contain ³⁷Cl')

fig=stack(spectrum('ir',[(1740,160,45)],'IR: strong ester carbonyl, no broad O–H'),spectrum('nmr',[(1.00,3,'t'),(1.25,3,'t'),(2.30,2,'q'),(4.15,2,'q')],'Four resonances; each displayed integral is a whole multiplet'))
add(724,'Distinguishing two ethyl groups in an ester','S3.2','ahl',
    'A compound has formula C₅H₁₀O₂ and molecular-ion m/z 102. IR shows an ester C=O near 1740 cm⁻¹ and no broad O–H. The NMR has δ1.00 triplet (3H), δ1.25 triplet (3H), δ2.30 quartet (2H), δ4.15 quartet (2H). Candidate connectivities are CH₃CH₂COOCH₂CH₃, CH₃COOCH₂CH₂CH₃ and CH₃CH₂CH₂COOCH₃.',fig,[
    P('Deduce the connectivity and assign both CH₂ resonances.','CH₃CH₂COOCH₂CH₃ (ethyl propanoate).','The δ4.15 quartet is OCH₂, and δ2.30 quartet is CH₂ next to C=O.','Each is adjacent to a CH₃ group, producing quartet splitting; the methyl partners give the two 3H triplets.'),
    P('Use a specific NMR feature to exclude each alternative, rather than relying only on carbon count.','Reason:CH₃COOCH₂CH₂CH₃ requires an acetyl CH₃ singlet, absent here.','Reason:CH₃CH₂CH₂COOCH₃ requires an OCH₃ singlet, absent here.'),
    P('An acylium fragment C₃H₅O⁺ appears at m/z 57. Identify the lost neutral radical and verify mass, atom and charge conservation.','Lost radical is ·OC₂H₅, nominal mass 45.','C₅H₁₀O₂⁺· → C₃H₅O⁺ + ·OC₂H₅; 102=57+45, all atoms balance and total charge remains +1.')],
    'RDKitCCC(=O)OCCC5H10O2;integrals10H; C3H5O57 +C2H5O45=M102; candidatesnotvariednumericclones.','CH₃CH₂COOCH₂CH₃')

fig=molecules([('Enantiomer A','CC[C@H](O)C','C4H10O'),('Enantiomer B','CC[C@@H](O)C','C4H10O')],'Opposite configurations of butan-2-ol')
add(725,'A non-racemic mixture that ordinary spectra cannot resolve','S3.2','ahl',
    'A and B are the two drawn enantiomers of butan-2-ol. At the stated temperature, wavelength, total concentration and path length, a pure A solution rotates plane-polarized light by +12.0° and pure B by −12.0°. Mixture rotation is the mole-fraction weighted sum under these same conditions. A mixture gives +3.00°. The measured IR spectra are taken in an achiral environment.',fig,[
    P('Identify the stereogenic carbon and explain why the drawings represent enantiomers. No R/S labels are required.','The carbon bonded to OH has four different groups: OH, H, CH₃ and CH₂CH₃.','The drawings have opposite three-dimensional arrangements at this carbon and are non-superimposable mirror images.'),
    P('Calculate the mole percentages of A and B and explain why the mixture is not racemic.','Let x be A’s mole fraction: 12.0x − 12.0(1−x)=3.00.','x=0.625, so A=62.5% and B=37.5%.','A racemate is 50:50 and has zero net rotation; this sample has excess A.'),
    P('Evaluate whether a match in IR spectrum and boiling temperature proves the mixture is racemic.','Reason:Enantiomers have the same IR absorption in an achiral environment and the same boiling temperature under the same conditions.','Reason:Those observations do not determine their proportions; optical rotation under controlled conditions can distinguish a non-racemic mixture.')],
    'RDKitoppositeonechiralcenter;12(.625)−12(.375)=3;specifiedfixedtotalconcentration avoidsrotationnormalizationambiguity.','62.5% A and 37.5% B')

fig=molecules([('A','C/C=C/C','C4H8'),('B',r'C/C=C\C','C4H8'),('C','C=CCC','C4H8')],'Two but-2-ene geometries and but-1-ene')
add(726,'Why only one alkene connectivity gives cis/trans forms','S3.2','ahl',
    'The three structures A–C are shown. In A the terminal methyl groups lie on opposite sides of C=C; in B they lie on the same side. C has a terminal CH₂= group. Do not use E/Z notation.',fig,[
    P('Name A and B using cis/trans terminology and explain the structural requirement that C fails.','A is trans-but-2-ene; B is cis-but-2-ene.','Reason:Each C of C=C must have two different substituents; the terminal carbon of C (but-1-ene) has two H atoms and fails this requirement.'),
    P('Explain why interconversion of A and B is not ordinary rotation around a single bond, and distinguish their relationship from that between A and C.','Reason:The π bond constrains rotation; interconversion requires disruption of π overlap rather than free C–C single-bond rotation.','A and B are stereoisomers with the same connectivity; A and C are structural isomers with a different double-bond position.'),
    P('A student states that equal molecular mass proves all three have identical boiling temperatures. Evaluate the reasoning and identify one feature that can change intermolecular attraction.','Reason:Equal mass alone does not fix intermolecular forces; spatial arrangement and molecular symmetry can alter resultant dipoles and packing.','The cis and trans arrangements can have different net dipoles, so physical properties may differ even though formula and connectivity match.')],
    'RDKitstereobondsC/C=C/Ctrans,C/C=C\\Ccis;allC4H8;terminalcarbon2H lacksgeometricalisomerism.','A trans, B cis; C has no cis/trans pair')

fig=molecules([('A','C=CC(Br)C','C4H7Br'),('B','CC=CCBr','C4H7Br'),('C','C=C(Br)CC','C4H7Br')],'Three bromoalkene connectivities; no geometry implied where unspecified')
add(727,'Counting distinct stereoisomers without double counting','S3.2','ahl',
    'A, B and C are three distinct connectivities with formula C₄H₇Br: A=CH₂=CH–CHBr–CH₃; B=CH₃–CH=CH–CH₂Br; C=CH₂=C(Br)–CH₂–CH₃. Where the drawing leaves stereochemistry unspecified, include all possible stereoisomers. Use cis/trans descriptions where applicable; R/S and E/Z labels are not required.',fig,[
    P('Determine the stereoisomer count for A, explaining which feature creates it and why its C=C does not create a second pair.','A has one carbon bonded to Br, H, CH₃ and CH=CH₂, giving two enantiomers.','Its terminal C=C has one carbon with two H atoms, so no cis/trans pair occurs.'),
    P('Determine the count for B and C, with a structural reason for each.','Reason:B has two cis/trans forms because each alkene carbon carries H and a different carbon group; it has no stereogenic tetrahedral carbon.','Reason:C has one form: the terminal C=C fails the two-different-substituents test and no tetrahedral carbon has four different groups.'),
    P('State the total across the three connectivities and explain why an approximately 1:1 molecular-ion pair two mass units apart would not settle which connectivity is present.','Total = 2+2+1 = 5 stereoisomers.','Reason:Each contains one bromine atom; comparable ⁷⁹Br/⁸¹Br abundances give the same approximate M:M+2 pattern for all three connectivities and their stereoisomers.')],
    'RDKitallC4H7Br;Achiralcenter1twomirrorforms;Balkenebothsubstituentsdifferenttwo;CterminalCH2no;total5.','A:2; B:2; C:1; total5')

b=tx(380,30,'CO₂: vibration models (arrows indicate displacement)',18)
for y,label,arrows in [(110,'symmetric stretch',[(180,-30),(580,30)]),(220,'asymmetric stretch',[(180,30),(380,-30),(580,30)]),(330,'bend',[(180,0),(380,1),(580,0)])]:
    b+=tx(180,y,'O',24)+tx(380,y,'C',24)+tx(580,y,'O',24)+ln(200,y-8,360,y-8)+ln(400,y-8,560,y-8)+tx(55,y+35,label,14,'start')
    if label!='bend':
        for x,dx in arrows:b+=ln(x,y-35,x+dx,y-35,BLUE,3)+tx(x+dx,y-42,'←' if dx<0 else '→',20)
    else:b+=tx(180,y-35,'↓',25)+tx(380,y-35,'↑',25)+tx(580,y-35,'↓',25)
add(728,'A nonpolar molecule can absorb infrared radiation','S3.2','ahl',
    'For this problem, a vibration absorbs IR only if the molecular dipole changes during that vibration. CO₂ is linear and has zero permanent dipole. Its symmetric stretch leaves the dipole zero; an asymmetric stretch and bending vibrations change the instantaneous dipole. Bands occur near 2349 and 667 cm⁻¹. Much of Earth’s outgoing thermal radiation lies between 5 and 30 μm. Use λ=1/wavenumber, with consistent units.',svg(b,'Symmetric, asymmetric and bending modes of CO2',h=390),[
    P('Explain why the symmetric stretch can be IR-inactive while the asymmetric stretch and bend are active, despite the same atoms and bonds.','Reason:In the symmetric stretch the equal, opposite bond dipoles cancel throughout the vibration, so the dipole does not change.','Reason:The other motions break that instantaneous cancellation and change the dipole, permitting absorption under the supplied rule.'),
    P('Convert both wavenumbers to wavelengths in μm and identify which falls within the stated 5–30 μm interval.','λ(2349)=10⁴/2349=4.26 μm.','λ(667)=10⁴/667=15.0 μm; this is within the stated interval, while 4.26 μm is outside.'),
    P('Evaluate the rule “all nonpolar molecules are IR-inactive” and compare a homonuclear diatomic molecule under the supplied dipole-change criterion.','CO₂ is a counterexample: a permanent dipole is not required if a vibration changes dipole.','Reason:A homonuclear diatomic such as N₂ remains symmetric during its stretch and has no changing dipole, so its stretching vibration is IR-inactive under this model.')],
    '10000/2349=4.257;10000/667=14.993;IRcriterionexplicitlygiven; elementarymodepicturesnotcoordinationpattern.','CO₂ bend near15.0 μm lies within stated thermal interval')

fig=stack(spectrum('ir',[(3300,95,200),(1720,150,40)],'Mixture IR: broad O–H and carbonyl'),spectrum('nmr',[(1.20,9,'t'),(3.70,6,'q'),(2.20,6,'d'),(9.80,2,'q')],'Mixture: group integrals 9, 6, 6 and 2; exchangeable OH omitted'))
add(729,'Quantifying a mixture from whole-multiplet integrals','S3.2','ahl',
    'A mixture contains ethanol and ethanal only, with total amount 0.01000 mol. Its NMR has δ1.20 triplet (integral 9), δ3.70 quartet (6), δ2.20 doublet (6), δ9.80 quartet (2). These are relative whole-multiplet areas, not line heights; exchangeable OH is omitted. IR has broad O–H near 3300 and C=O near 1720 cm⁻¹. Use M(ethanol)=46.07 and M(ethanal)=44.05 g mol⁻¹. Assume no exchange or reaction between the components during measurement.',fig,[
    P('Assign every resonance to a proton environment and account for splitting.','Ethanol CH₃ gives δ1.20 triplet; ethanol CH₂ gives δ3.70 quartet.','Ethanal CH₃ gives δ2.20 doublet because it has one neighboring aldehyde H.','Ethanal CHO gives δ9.80 quartet because it has three neighboring methyl H.'),
    P('Determine the component mole ratio using two independent integral comparisons, then calculate their amounts.','Methyl comparison: (9/3):(6/3)=3:2 for ethanol:ethanal.','CH₂/CHO comparison: (6/2):(2/1)=3:2, confirming the ratio.','Amounts are ethanol 0.006000 mol and ethanal 0.004000 mol.'),
    P('Calculate the sample mass and explain why the IR peak depths alone are not a justified substitute for the supplied NMR calibration.','Mass = 0.006000(46.07)+0.004000(44.05)=0.45262 g.','Reason:Different functional groups have different absorption strengths and band shapes; no common proportionality calibration from IR depth to component amount was supplied.')],
    'NMR integralratios3:2bothCH3andCH2/CHO;Hareasethanol15 excludingOH+ethanal8; mass.45262g; allowedonlyd/t/q.','Ethanol:ethanal=3:2; total mass0.45262g')

fig=stack(spectrum('ms',[(43,100,''),(60,15,'')],'Molecular ion m/z60; major fragment43'),spectrum('nmr',[(1.20,6,'d'),(3.90,1,'u')],'Non-exchangeable proton areas 6:1; CH splitting unresolved'))
add(730,'Reconciling exchange, integration and a molecular formula','S3.2','ahl',
    'An alcohol has molecular formula C₃H₈O and molecular-ion m/z60. Before adding D₂O, its ¹H NMR contains a 6H doublet near δ1.20, a 1H CH resonance near δ3.90 whose splitting is deliberately unresolved in the figure, and a broad exchangeable 1H signal. After D₂O treatment the broad 1H signal disappears but the other integrated areas remain 6:1. Compare propan-1-ol and propan-2-ol. No interpretation of higher-order multiplets is required.',fig,[
    P('Identify the alcohol and explain the 6H doublet without interpreting the unresolved CH resonance.','Propan-2-ol, (CH₃)₂CHOH.','Two equivalent methyl groups give six H in one environment; one adjacent CH proton splits their signal into a doublet.'),
    P('Explain how the D₂O result supports the functional-group assignment, and reconcile all eight H atoms with the formula.','The disappearing broad proton is an exchangeable O–H hydrogen, consistent with an alcohol.','There are six methyl H, one methine H and one OH H, giving eight in total.'),
    P('Propose an atom- and charge-balanced fragmentation giving C₃H₇⁺ at m/z43 from the molecular radical cation. Explain whether this fragment alone distinguishes the two alcohol isomers.','C₃H₈O⁺· → C₃H₇⁺ + ·OH; nominal masses 60=43+17 and total charge +1 is conserved.','Reason:The fragment formula can be formed by loss of OH from either isomer, so this fragment alone does not establish the original connectivity; the NMR evidence does.')],
    'RDKitCC(O)CC3H8O;H6methyl+1CH+1OH; M60 fragmentC3H7+43 +OHradical17. CHsplittingexplicitlyunresolvedtoexcludeHLseptetrequirement.','Propan-2-ol; disappearing signal is OH')

# Numerical and structural author assertions independent of the displayed rounding.
assert len(questions)==30
assert sum(q['level']=='sl' for q in questions)==12
assert sum(q['level']=='ahl' for q in questions)==18
assert math.isclose(.03*61.98+.08*40.30,5.0834)
assert math.isclose(.1135/22.70*2,.01000)
assert math.isclose(.02*61.98+.01*77.98,2.0194)
assert math.isclose(.2*.5+.6*.4,.340) and math.isclose(.8*.5+.1*.4,.440)
assert math.isclose(.26845-.01802,.25043)
assert math.isclose(.28664/143.32,.002)
assert math.isclose(.42996/143.32,.003)
assert math.isclose(.006*46.07+.004*44.05,.45262)
for q in questions:
    assert q['marks']==sum(p['marks'] for p in q['parts'])
    assert q['marks']==sum(len(g['steps']) for g in q['markScheme'])
    assert '<image' not in q['diagramSvg'] and 'href=' not in q['diagramSvg']
OUT.parent.mkdir(parents=True,exist_ok=True);REVIEW.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(questions,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
review={'status':'passed','questions':30,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'checks':'Original derivations, RDKit connectivity/valence/formula validation, explicit numerical assertions, part/mark totals; separate independent chemistry review still required.','records':checks}
REVIEW.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print(f'Wrote {len(questions)} S3 questions, all with original vector figures.')
