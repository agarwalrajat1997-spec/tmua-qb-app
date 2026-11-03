"""Independent review calculations, not imported from the author generator.

The reviewer read every stem, question part and worked marking point. This
script records fresh calculations from the supplied data and binds that review
to the exact final JSON. It intentionally does not import reactivity.py.
"""
import math,json,hashlib,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'content/ib/chemistry-2026-expansion/reactivity.json'
questions=json.loads(source.read_text(encoding='utf8'))
by_id={q['id']:q for q in questions};records=[]
def record(theme,num,note,*calculations):
    q=by_id[f'ib-chem-r{theme}-{num}'];values=[]
    for label,value,reference in calculations:
        assert math.isclose(value,reference,rel_tol=3e-5,abs_tol=1e-11),(q['id'],label,value,reference)
        values.append({'quantity':label,'independentlyCalculated':value,'reference':reference})
    assert values
    assert q['marks']==sum(p['marks'] for p in q['parts'])
    assert q['marks']==sum(int(s['code'][1:]) for g in q['markScheme'] for s in g['steps'])
    assert q['level']==('sl' if num<=(712 if theme==1 else 714) else 'ahl')
    assert q['difficulty']=='hard' and q['diagramSvg']
    records.append({'id':q['id'],'status':'passed','chemistryAndScope':note,'calculations':values,'visualReview':'Question figure inspected against supplied quantities, axes, states and worked conclusions. Exact peak/threshold corrections recorded in review findings.','marking':'Part totals and total score reconciled; distinct scientific reasoning and valid alternatives reviewed.'})

record(1,701,'HCl .0600 mol vs NaOH .0400 mol; 1:1 neutralization; cup and solution gain heat while reaction loses it. SL calorimetry.',('reaction heat J',-(100*4.18+45)*6,-2778),('enthalpy kJ/mol',-(100*4.18+45)*6/40,-69.45),('wrong calculation kJ/mol',-100*4.18*6/60,-41.8))
record(1,702,'Linear cooling correction requires reaction completion; intercept is not a direct observed maximum.',('corrected rise K',31.8-(-.1)*2-22,10),('enthalpy kJ/mol',-334.4*10/(1000*.025),-133.76),('underestimate %',.2/10*100,2))
record(1,703,'Reverse dissolution to cancel NaOH(s) and Na+; concentration/phase matching essential to Hess cycle.',('neutralization kJ/mol',-102-(-44),-58),('rise K',.03*102000/250,12.24))
record(1,704,'One double bond and H-H broken; one C-C and two additional C-H formed. Unchanged C-H terms cancel in a complete inventory.',('estimate kJ/mol',614+436-348-2*414,-126),('difference kJ/mol',-126-(-137),11))
record(1,705,'Profile levels are energy not time; catalyst changes the barrier without endpoints. Enthalpic stability distinguished from kinetic accessibility.',('forward enthalpy',-15-20,-35),('reverse enthalpy',20-(-15),35),('2mol heat',2*(-35),-70))
record(1,706,'Both methane routes atom balanced; carbon product fractions weight both oxygen and heat. CO has health/environment implications.',('oxygen mol',.75*2+.25*1.5,1.875),('heat released kJ',.75*890+.25*607,819.25),('shortfall %',(890-819.25)/890*100,7.9494382))
record(1,707,'Complete combustion gives 1 CO2 per methane and 2 per ethanol. Efficiency and fuel mass must precede emissions comparison.',('methane mass g',1000/(.8*50),25),('ethanol mass g',1000/(.9*27),41.1522634),('ethanol CO2 g',1000/(.9*27)/46*88,78.7260691))
record(1,708,'Acidic half-equations conserve atoms and charge; fuel utilization differs from conversion efficiency; no Faraday calculation at SL.',('water mol',1*.8,.8),('O2 mol',.8/2,.4),('useful kJ',1*.8*.6*286,137.28),('overall efficiency %',.8*.6*100,48))
record(1,709,'Supplied alkaline methanol oxidation combines with 1.5O2+3H2O+6e→6OH; net CH3OH+1.5O2→CO2+2H2O. Immediate CO2 assumption stated.',('methanol mol',500/(.45*726),1.5304567),('methanol g',500/(.45*726)*32,48.9746143))
record(1,710,'Reverse MgO/acid reaction; matched aqueous states cancel. Reverse heat must change sign.',('MgO formation kJ/mol',-467-286+146,-607),('heat released kJ',.480/24*607,12.14))
record(1,711,'Calibration includes cup plus contents; proposed solution-alone capacity exceeding calibrated total is an intentional inconsistency to detect.',('calibrated capacity J/K',12*240/8,360),('molar enthalpy kJ/mol',-360*5.5/(.02*1000),-99),('proposed solution capacity J/K',100*4.18,418))
record(1,712,'Gas-phase bond enthalpies need five C-H, one C-C, one C-O, one O-H and three O=O broken. Ethanol starting state kept gaseous.',('broken kJ/mol',5*414+348+358+463+3*498,4733),('formed kJ/mol',4*804+6*463,5994),('liquid water correction kJ/mol',4733-5994-3*44,-1393))
record(1,713,'Formation-data sum and reference-state distinction are AHL. Oxygen elemental reference zero, ethanol compound nonzero.',('liquid combustion kJ/mol',2*-394+3*-286+278,-1368),('gas combustion kJ/mol',2*-394+3*-242+278,-1236),('water-state difference',3*44,132))
record(1,714,'Mg2+ requires both ionizations and two Cl electron affinities; lattice-formation sign distinguished from dissociation.',('gaseous-ion path',148+738+1451+244-2*349,1883),('lattice formation',-642-(148+738+1451+244-2*349),-2525))
record(1,715,'Second oxygen affinity applies to O−, not neutral O. Endothermic isolated affinity can be offset by lattice formation.',('ion path',2*(108+496)+498/2-141+744,2060),('lattice formation',-414-2060,-2474),('affinity replacement error',(-141+744)-2*-141,885))
record(1,716,'MgO Hess cycle recovers O−+e→O2− positive affinity; lattice comparison involves charge, distance and geometry.',('second affinity',-602-148-738-1451-249+141+3791,744))
record(1,717,'Same CO2 endpoint allows Hess subtraction. Partial conversion to CO does not change the total when CO subsequently burns.',('CO formation',-394+283,-111),('initial heat',.6*-111+.4*-394,-224.2),('later heat magnitude',.6*283,169.8))
record(1,718,'Fuel blend uses mole-weighted complete combustion; uncorrected heat loss biases inferred ethane down.',('methane combustion',-394-2*286+74,-892),('ethane combustion',-2*394-3*286+84,-1562),('ethane fraction',(1250-892)/(1562-892),.5343283582),('oxygen mol',2+1.5*(1250-892)/(1562-892),2.801492537))
record(1,719,'Only the reference allotrope receives zero formation enthalpy. Kinetic and pressure effects cannot be inferred from one enthalpy difference.',('diamond combustion',-394-1.9,-395.9),('extra .2mol heat',.2*1.9,.38))
record(1,720,'Supplied gas-ion→aqueous steps plus lattice dissociation, not an unstated hydration convention. Positive enthalpy does not prohibit entropy-driven dissolution.',('solution enthalpy',787-406-364,17),('temperature change',-.05*17000/450,-1.8888889))
record(1,721,'Entropy includes coefficients and unit conversion; standard-state sign boundary is not a universal CO2-pressure or rate prediction.',('entropy J/K/mol',39.8+214-92.9,160.9),('G298 kJ/mol',178-298*.1609,130.0518),('boundary K',178/.1609,1106.277812))
record(1,722,'Vaporization enthalpy competes with entropy. Positive standard Gibbs change does not prohibit evaporation into low-partial-pressure air.',('G298',38.6-298*.1097,5.9094),('boundary K',38.6/.1097,351.868733))
record(1,723,'Reaction as written consumes 2 H2O2. Negative H and positive S give no positive-temperature sign boundary in supplied constant-data model.',('entropy J/K',2*69.9+205-2*109.6,125.6),('G298 kJ',-196-298*.1256,-233.4288))
record(1,724,'G-T slope has entropy units; no inference about activation energy or rate.',('slope kJ/K/mol',(-10-20)/(500-300),-.15),('enthalpy',20+.15*300,65),('boundary K',65/.15,433.3333333),('G450',65-.15*450,-2.5))
record(1,725,'Actual Gibbs relation explicitly supplied, dimensionless Q. Q<K gives forward change despite positive standard term.',('G actual kJ',4.8+.00831*298*math.log(.02),-4.8876595),('K',math.exp(-4.8/(.00831*298)),.14394445))
record(1,726,'Reversal/halving changes G and powers of K; physical equilibrium state is the same.',('reverse-half G',-(-33)/2,16.5),('K first',math.exp(33/(.00831*298)),612867.2554),('K second',math.exp(-16.5/(.00831*298)),.00127736756))
t=40000/(150-8.31*math.log(100))
record(1,727,'Combines G=H−TS with G=−RTlnK; no van’t Hoff relation presumed. J/kJ consistency required.',('temperature K',t,358.003335),('substitution K',math.exp(-(40000-150*t)/(8.31*t)),100))
record(1,728,'Both equations atom balanced; a negative formal sum does not establish actual physical coupling or product selectivity.',('combined Gibbs kJ',28.6-237,-208.4))
record(1,729,'Reservoir entropy relation provided; gas-count argument refers to system only, and surroundings can reverse total sign.',('total entropy298',-198+92200/298,111.395973),('G298 kJ',-92.2+298*.198,-33.196),('G700 kJ',-92.2+700*.198,46.4))
record(1,730,'Lowest of all three G curves defines stability. Solid-gas crossing is metastable because liquid is lower. Fixed interval supplied.',('solid/liquid K',8/.025,320),('liquid/gas K',(44-8)/(.115-.025),400),('solid/gas K',44/.115,382.6086957),('liquid at solid/gas',8-.025*(44/.115),-1.56521739))

record(2,701,'CaCO3+2HCl→CaCl2+H2O+CO2 balanced. Mass plateau alone is not proof of carbonate exhaustion.',('purity %',.880/44*100/2.5*100,80),('acid excess mol',.05-.88/44*2,.01),('gas dm3',.88/44*22.7,.454))
record(2,702,'2Al:3Cu ratio; unrecovered copper is not equivalent to unreacted aluminium under given complete reaction assumption.',('Cu theoretical g',.540/27*1.5*63.5,1.905),('yield %',1.7145/1.905*100,90),('CuII residual M',(.05*.8-.54/27*1.5)/.05,.2))
record(2,703,'Only carbonate loses CO2; original MgO and newly formed MgO both remain. Water would bias inferred carbonate upwards.',('carbonate %',(5-3.68)/44*84/5*100,50.4),('residue mol',3.68/40,.092))
record(2,704,'NaCl limiting; quantitative precipitation distinguished from isolation recovery. Atom economy is equation-based.',('theoretical AgCl g',.03*.1*143.5,.4305),('AgI residual M',(.04*.15-.03*.1)/.07,.0428571429),('atom economy %',143.5/(169.9+58.5)*100,62.8283713))
record(2,705,'Esterification theoretical limiting-feed maximum does not presume complete conversion; water coproduct lowers atom economy.',('ester theory g',.2*88,17.6),('yield %',12.32/17.6*100,70),('atom economy %',88/106*100,83.0188679))
record(2,706,'Gas-volume ratios require common T/P. Recovery yield alone cannot establish conversion or outlet composition.',('NH3 theory dm3',9/3*2,6),('N2 theoretical leftover dm3',4-9/3,1),('collected yield %',4.8/6*100,80))
record(2,707,'Tangent—not origin secant—gives instantaneous rate; factor 2 converts O2 production into peroxide disappearance.',('tangent cm3/s',(40.8-22.4)/(30-10),.92),('oxygen mol/s',.92/1000/24,3.83333333e-5),('peroxide M/s',2*.92/1000/24/.05,.001533333333))
record(2,708,'Equal carbonate mass limits equal final gas; surface area changes rate, not final stoichiometric amount. Average rate ratio is not instantaneous ratio.',('final cm3',.25/100*22.7*1000,56.75),('acid required mol',.25/100*2,.005),('average-rate ratio',40/20,2))
tail=lambda a:math.erfc(math.sqrt(a))+2/math.sqrt(math.pi)*math.sqrt(a)*math.exp(-a)
record(2,709,'Kinetic-energy distributions have equal normalization; common activation threshold E=5 corresponds to reduced thresholds5/4 for the temperatures.',('lower fraction',tail(5),.01856613546),('higher fraction',tail(4),.04601170569),('collision multiplier',1.1*tail(4)/tail(5),2.72608569))
record(2,710,'Exact corrected profile peaks75/50 and endpoints0/30 agree with local barriers. Same endpoints mean no change in enthalpy or equilibrium.',('uncatalyzed reverse barrier',75-30,45),('catalyzed reverse barrier',50-30,20),('enthalpy',30-0,30))
b=(-.05+math.sqrt(.2825))/2;a=(1.4-b)/2
record(2,711,'Before injection N2O4=.4,NO2=.2 give K=.1; after injection conserved NO2 equivalents1.4. Final traces preserve K and 2:1 relaxation.',('initial K',.2**2/.4,.1),('final K',b*b/a,.1),('NO2-equivalent conservation',2*a+b,1.4))
record(2,712,'Exothermic Haber equilibrium yield falls with temperature; initial rate can rise. Compression favors 2 vs4 gas particles without changing K.',('gas particle decrease',1+3-2,2))
record(2,713,'Henry-type proportional relation supplied as data; partial CO2 pressure, not total air pressure. Original slope cannot be assumed at new T.',('dissolved CO2 M',.0300*.000400,.000012))
record(2,714,'At fixed V/T inert gas does not alter reacting concentrations. Catalyst event increases equal forward/reverse rates; reciprocal K is equation convention.',('reverse K',1/.025,40))
record(2,715,'Independent initial comparisons give NO order2,Br2 order1; stoichiometry alone does not prove molecularity3.',('rate constant',2e-4/(.1**2*.1),.2),('predicted M/s',.2*.2**2*.2,.0016))
record(2,716,'NO3 formed then consumed, one NO2 cancels; slow 2NO2 step supports local law, not extrapolation to zero CO.',('k dm3/mol/s',8e-6/.02**2,.02))
record(2,717,'Zero empirical order under irradiation is not zero-particle molecularity. Constant-rate continuation explicitly supplied for timing.',('time initial .0100M s',.01/4e-5,250),('time initial .00500M s',.005/4e-5,125))
record(2,718,'Supplied rational rate model linearized, asymptotes checked with units. No off-syllabus named catalytic law needed.',('k per s',1/5,.2),('b dm3/mol',100/5,20),('rate at.05M',.2*.05/(1+20*.05),.005),('high limit M/s',.2/20,.01))
record(2,719,'Third-order concentration rate falls eightfold on doubling V; amount rate falls fourfold because V doubles.',('original M/s',.5*.1*.2**2,.002),('after dilution M/s',.5*.05*.1**2,.00025),('amount-rate ratio',(.5*.1*.2**2*1)/(.5*.05*.1**2*2),4))
record(2,720,'Fast-equilibrium relation supplied; N2O2 is intermediate not transition state. Slow O2 consumption means NO2 production twice rate.',('effective k',.02*10,.2),('O2 consumption M/s',.02*10*.1**2*.2,.0004),('NO2 production M/s',2*.02*10*.1**2*.2,.0008))
record(2,721,'Local barriers start from preceding minima, not a shared zero. Equal prefactor/concentration assumption explicit; neither kinetics nor abundance inferred from profile alone.',('barrier1',80-0,80),('barrier2',20-(-70),90),('step2 enthalpy',-100-(-70),-30))
ea=8.31*math.log(4)/(1/300-1/330);factor=.001*math.exp(ea/(8.31*300))
record(2,722,'Two-temperature Arrhenius uses kelvin and common A; Ea units converted J→kJ.',('Ea kJ/mol',ea/1000,38.0164323),('A per s',factor,4194.304),('k315 per s',factor*math.exp(-ea/(8.31*315)),.002067116))
record(2,723,'Unit-normalized ln(k/s−1) gives intercept ln(A/s−1), not A itself.',('Ea kJ/mol',6000*8.31/1000,49.86),('A per s',math.exp(20),485165195.4),('k400 per s',math.exp(20-6000/400),148.4131591),('temperature k1 K',6000/20,300))
record(2,724,'Parallel pathway prefactors alter crossing; adding a positive-rate path does not remove original path.',('crossing K',20000/(8.31*math.log(1000)),348.4114095),('ratio300',.001*math.exp(20000/(8.31*300)),3.048681),('ratio500',.001*math.exp(20000/(8.31*500)),.123159))
record(2,725,'Piecewise Arrhenius left side is higher T; different apparent slopes reject single constant pair but not prove unique mechanism.',('low apparent Ea kJ/mol',5000*8.31/1000,41.55),('high apparent Ea kJ/mol',8000*8.31/1000,66.48))
record(2,726,'A/B1:1 isomerization preserves total; adding A raises total without changing K. Graph contains instantaneous A jump then conserved relaxation.',('initial A M',1/(1+9),.1),('immediate Q',.9/(.1+.2),3),('final A M',1.2/10,.12),('final B M',1.2*9/10,1.08))
record(2,727,'1:1:1:1 stoichiometry and equal reactants give positive square-root linear relation; negative branch lies outside physical concentration interval.',('product M',2*.2/3,.1333333333),('reactant M',.2-2*.2/3,.0666666667),('K',(2*.2/3)**2/(.2-2*.2/3)**2,4))
# Bisection is independent of the author's algebraic rationalized quadratic root.
lo=0.;hi=.1
for _ in range(120):
    mid=(lo+hi)/2
    if mid/(1-2*mid)**2>1e-4:hi=mid
    else:lo=mid
exact=(lo+hi)/2
record(2,728,'Dimerization consumes2NO2 perN2O4; expression squares NO2. Independent bisection confirms supplied benchmark and negligible depletion.',('exact x M',exact,.00009996001999),('estimated NO2 depletion %',2*.0001*100,.02),('approx relative error %',(.0001-exact)/exact*100,.0399960016))
record(2,729,'Initial Q>K requires reverse ICE signs; physical positive square-root relation respects material conservation.',('initial Q',1.2**2/.2**2,36),('extent M',(1.2-4*.2)/(2+4),1/15),('final Q',(1.2-2/15)**2/(.2+1/15)**2,16))
record(2,730,'Unequal total concentration powers leave volume factor; halving volume doubles Q for dissociation.',('volume dm3',.04**2/(.08*.02),1),('immediate Q',(.04/.5)**2/(.02/.5),.16))
x=(-3+math.sqrt(13))/20
record(2,731,'Expansion halves concentrations instantly, then dissociation increases CO/Cl2 with same K; exact graph asymptote respects mass and K.',('initial K',.4/.2**2,10),('immediate Q',.2/.1**2,20),('final asymptote Q',(.2-x)/(.1+x)**2,10))
record(2,732,'Dimensionless normalized quotient and actual Gibbs relation explicitly supplied. Standard and actual signs differ because Q>K.',('Q',.3**2/.1**2,9),('standard G kJ',-.00831*400*math.log(4),-4.60804246),('actual G kJ',.00831*400*math.log(9/4),2.69553108))
record(2,733,'Ratios multiply to KAC6, not sum5; all isomers remain present and total conserved.',('KAC',2*3,6),('equilibrium A M',.9/(1+2+6),.1),('equilibrium total',.1+.2+.6,.9))
record(2,734,'Candidate X passes atom balance but not K; Y passes K but not atoms. Both conditions independently necessary.',('K',.2/.4**2,1.25),('immediate Q',.4/.8**2,.625),('X conservation',.6+2*.5,1.6),('X Q',.5/.6**2,1.3888889),('Y conservation',.8+2*.8,2.4),('Y Q',.8/.8**2,1.25))
record(2,735,'Explicit ideal model isolates approximation validity, not real10M activity chemistry. Keep trace-A depletion while B change is negligible; K alone insufficient.',('naive x M',.01*10*.0001,.00001),('refined x M',(.01*10*.0001)/(1+.01*10),.00000909090909),('B depletion %',(.01*10*.0001)/(1+.01*10)/10*100,.0000909090909))

assert len(records)==65 and len(by_id)==65
assert {r['id'] for r in records}==set(by_id)
review={'status':'passed','questions':65,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'reviewer':'Separate reviewer; did not author this batch or import its calculation functions','method':'Line-by-line scientific review of all65 stems, parts and worked allocations; fresh numerical calculations from stated inputs; physical-root, stoichiometric, unit and scope checks; all65 figures inspected.','findingsResolved':['R2-710 original plotted peaks exceeded stated75/50. Author replaced curves with exact stationary-level interpolation.','R2-709 added explicit activation threshold at E=5 to match the supplied tail fractions, with explicit visible stroke.','R1 cycle axes distinguish enthalpy from Gibbs energy; R2-718 now shows the stated inverse-rate linearization; R2-719 compares dimensionless rates relative to their own initial values.','Author corrected merged variable/prose spacing and displayed three-significant-figure final values while retaining explicitly labeled unrounded working.'],'limitations':'Separate AI review and computational checks, not human IB examiner moderation. Constructed models/measurements are identified in the questions.','records':records}
out=ROOT/'docs/ib-2026-chemistry/reactivity-independent-review.json'
if '--write-review' in sys.argv:
    out.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
elif out.exists():
    existing=json.loads(out.read_text(encoding='utf8'))
    assert existing['sha256']==review['sha256'],'Reviewed Chemistry content has changed; a new independent review is required.'
    assert {r['id'] for r in existing['records']}==set(by_id)
print(json.dumps({'status':'passed','questions':65,'independentNumericalChecks':sum(len(r['calculations']) for r in records),'sha256':review['sha256']}))
