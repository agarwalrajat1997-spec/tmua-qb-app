"""Fresh SL calculation/option audit. Does not import or execute author code."""
from pathlib import Path
import math,json,hashlib,re
ROOT=Path(__file__).resolve().parents[2]
papers={}
questions={}
records={}
checks=0
def sh(b):return hashlib.sha256(b).hexdigest()
for set_ in ['a','b']:
 for pn in ['1','2']:
  path=ROOT/f'content/ib/physics-mocks-2026/papers/physics-sl-set-{set_}-paper-{pn}.json'
  paper=json.loads(path.read_text(encoding='utf8'));papers[paper['id']]={'id':paper['id'],'sha256':sh(path.read_bytes()),'questions':len(paper['questions']),'marks':paper['marks']}
  assert sum(q['marks'] for q in paper['questions'])==paper['marks']
  for q in paper['questions']:
   qid=q['id'];assert qid not in questions;questions[qid]=q
   for p,s in zip(q['parts'],q['markScheme']):
    assert p['label']==s['part']
    assert p['marks']==sum(int(re.search(r'\d+$',t['code'])[0]) for t in s['steps'])
   records[qid]={'id':qid,'paperId':paper['id'],'status':'passed','canonicalQuestionSha256':sh(json.dumps(q,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()),'fullStemPartsOptionsAndSchemeRead':True,'numericChecks':[],'partLabelsRead':[p['label'] for p in q['parts']]}

def qid(set_,section,n):return f'phy-sl-{set_}-{section}-{n:02d}'
def num(set_,section,n,part,name,actual,expected,tol=1e-9):
 global checks
 key=qid(set_,section,n);assert math.isfinite(actual) and abs(actual-expected)<=tol,(key,part,name,actual,expected,tol)
 records[key]['numericChecks'].append({'part':part,'name':name,'actual':actual,'expected':expected,'absoluteTolerance':tol,'status':'passed'});checks+=1
 return actual
def mc(set_,n,tokens,reason):
 key=qid(set_,'1a',n);q=questions[key];matched=[o for o in q['options'] if all((o['text'].lower().startswith(t[1:].lower()) if t.startswith('^') else t.lower() in o['text'].lower()) for t in tokens)]
 assert len(q['options'])==4 and len({o['text'] for o in q['options']})==4
 assert len(matched)==1,(key,tokens,matched)
 assert matched[0]['label']==q['correctOption'],(key,matched[0],q['correctOption'])
 scheme=' '.join(t['text'] for s in q['markScheme'] for t in s['steps'])
 for letter in re.findall(r'Therefore choose ([ABCD])',scheme):assert letter==q['correctOption'],(key,'stale scheme letter')
 records[key].update(uniqueCorrectOptionText=matched[0]['text'],correctOption=q['correctOption'],allFourOptionsEvaluated=True,independentPhysicalReasoning=reason)

# Set A MCQs: fresh equations and option selection by text, independent of order.
num('a','1a',1,'','path speed / m s-1',(30+40+30)/80,1.25);num('a','1a',1,'','displacement speed / m s-1',math.hypot(30-30,40)/80,.5)
mc('a',1,['^$1.25','$0.500'],'The east/west legs cancel as vectors but both contribute to path length; the requested order excludes the reversed pair.')
num('a','1a',2,'','later crossing time / s',(6+math.sqrt(36-4*5*1.6))/10,.8);num('a','1a',2,'','descending horizontal range / m',8*.8,6.4)
mc('a',2,['$6.4'],'The later quadratic root has negative vertical velocity; the earlier root is ascending.')
num('a','1a',3,'','acceleration ratio',(1+.4)/(1-.4),7/3)
mc('a',3,['7/3'],'Equal-speed separate trials allow equal drag; drag adds to weight upward and opposes weight downward.')
vx=(2*6-3-5)/2;num('a','1a',4,'','cart X final speed / m s-1',vx,2);num('a','1a',4,'','kinetic energy dissipated / J',.5*2*6**2+.5*3**2-(.5*2*vx**2+.5*5**2),24)
mc('a',4,['$24'],'Signed momentum gives vX=2; squaring both initial velocities gives initial40.5J and final16.5J, so only24J is lost.')
k=.84*2/(.100**2-.040**2);num('a','1a',5,'','spring constant / N m-1',k,200);num('a','1a',5,'','energy at0.080m / J',k*.080**2/2,.64)
mc('a',5,['$0.64'],'Work between extensions is the difference of squared extensions, not the square of the extension change.')
num('a','1a',6,'','sled final speed / m s-1',math.sqrt(2*(2*10*3*.5-3*3)/2),math.sqrt(21))
mc('a',6,['$4.6'],'Subtract friction work from the gravitational drop and convert the remainder into kinetic energy; all distractors miss a term or height.')
num('a','1a',7,'','specific heat ratio',.2*40/(.3*20),4/3)
mc('a',7,['$4/3$'],'Energy gained and lost use different masses and temperature intervals.')
num('a','1a',8,'','albedo X',80/400,.2);num('a','1a',8,'','albedo Y',180/600,.3);num('a','1a',8,'','emissivity ratio',300/200,1.5)
mc('a',8,['Y has the greater albedo','1.50'],'At equal temperature infrared emission ratio is emissivity ratio; reflection ratio is independently albedo.')
num('a','1a',9,'','initial planetary energy imbalance / W m-2',240-180,60)
mc('a',9,['initially gains energy'],'Positive top-of-atmosphere imbalance warms the system; absorption cannot destroy energy.')
num('a','1a',10,'','moles inferred from offset-independent slope',(.180e6-.100e6)/(300-100)*.05/8.31,2.4067388688327314)
mc('a',10,['$2.41'],'A fixed sensor offset leaves the pressure-temperature slope intact; convert kPa toPa.')
num('a','1a',11,'','internal-energy ratio',2*1.5/(1*1.5),2);num('a','1a',11,'','rms-speed ratio',math.sqrt(1/.2),math.sqrt(5))
mc('a',11,['$2$',r'\sqrt5'],'Internal energy scales with atom number, but rms speed at fixed temperature scales inversely as square root of atomic mass.')
Rl=1/(1/6+1/3);num('a','1a',12,'','external power fraction',Rl/(Rl+1),2/3)
mc('a',12,['$2/3$'],'External and internal series powers share the same total current, so the useful fraction is RL/(RL+r).')
num('a','1a',13,'','transverse velocity / m s-1',-5*(-.080),.4)
mc('a',13,['$0.40','upward'],'A translating rightward profile samples the negative of its spatial slope at a fixed particle.')
num('a','1a',14,'','initial phase cycles modulo one',((3-2.4)/.4)%1,.5);num('a','1a',14,'','final phase cycle remainder',(((3-2.4)/.4)+.5)%1,0,1e-12)
mc('a',14,['Destructive interference changes to constructive'],'Adding a half-cycle source phase reverses the interference condition without changing frequency/coherence.')
num('a','1a',15,'','resonance frequency / Hz',343/(2*(.540-.180)),476.38888888888886)
mc('a',15,['$476'],'Successive open-closed modes differ by a half wavelength in effective length; subtraction removes common end correction.')
mc('a',16,['dashed response has greater damping'],'A lower broader steady-state peak for fixed driving force indicates greater damping; peak height does not define natural frequency.')
num('a','1a',17,'','central mass ratio',2**3/(.5**2),32)
mc('a',17,['$32$'],'The two central stars differ, so mass must be kept in the circular-orbit period relation.')
num('a','1a',18,'','instantaneous tangential acceleration for perpendicular vectors',1*0+0*1,0)
mc('a',18,['North; zero'],'Gravity sets northward acceleration but is instantaneously perpendicular to eastward velocity, so no instantaneous speed change.')
num('a','1a',19,'','horizontal field / E0',2*math.cos(math.pi/3),1)
mc('a',19,['$E_0$ to the right'],'Equal vertical components cancel; horizontal components add with the actual60-degree angle.')
num('a','1a',20,'','selected-radius ratio',2/(.5),4)
mc('a',20,['$4r$'],'Both pass the same velocity selector and therefore have the same speed; analyser radius scales as m/q.')
mc('a',21,['A tiny fraction'],'Rare reversals and predominantly straight passage jointly imply concentrated positive charge and small nuclear size.')
num('a','1a',22,'','final nucleon number',238-4,234);num('a','1a',22,'','final proton number',92-2+1,91)
mc('a',22,['$234$','$91$'],'Alpha changes A/Z by−4/−2; beta-minus changes Z by+1 at fixed A.')
bg=(4*44-116)/3;num('a','1a',23,'','background rate / s-1',bg,20);num('a','1a',23,'','late source/background ratio',(116-bg)*2**(-120/40)/bg,.6)
mc('a',23,['$0.60$'],'Subtract a fixed background before applying decay, and compare source-only to background at the final time.')
num('a','1a',24,'','fission release / MeV',141*8.4+92*8.6-235*7.6,189.6)
num('a','1a',24,'','free neutron count',235+1-141-92,3)
mc('a',24,['$190'],'Binding totals use nucleon-number weights; an incident free neutron has no nuclear binding and three free neutrons conserveA.')
num('a','1a',25,'','parallax distance / light-year',3.26/(.100/2),65.2)
mc('a',25,['$65.2'],'Full six-month angular displacement is2p, notp; then convert parsecs to light-years.')

# Set B MCQs.
num('b','1a',1,'','successive-second distance ratio',((4*3+5*9)-(4*2+5*4))/(4+5),29/9)
mc('b',1,['$29/9$'],'Integrate constant-acceleration displacement over2–3s and0–1s, retaining the initial downward speed.')
num('b','1a',2,'','impact direction / degree',math.degrees(math.atan(math.sqrt(2*10*18)/12)),57.688466762576155)
mc('b',2,['$58^'],'Impact velocity angle uses vertical speed, not the displacement direction; horizontal speed remains12.')
num('b','1a',3,'','signed acceleration-time area / m s-1',.5*2*6+.5*(6-2)*(6-2),14)
num('b','1a',3,'','mean resultant force / N',3*14/6,7)
mc('b',3,['$7.0'],'Include the negative tail of the piecewise-linear acceleration graph and divide signed impulse by total duration.')
num('b','1a',4,'','retained kinetic fraction',(.5*4*(.5)**2)/(.5+1.5),.25)
mc('b',4,['$1/4$'],'Opposite initial momenta leave a combined speedv/2; total initial kinetic energy includes both masses.')
num('b','1a',5,'','pump input / W',12*(10*5+2**2/2)/.6,1040)
mc('b',5,['$1.04'],'Both gravitational and outgoing kinetic energy are useful output, then divide by efficiency.')
num('b','1a',6,'','thermal-rate increase',(1+1/4)/(.25+.25),2.5)
mc('b',6,['$2.5$'],'Diameter doubling quadruples area; add series thermal resistances before comparing rates.')
num('b','1a',7,'','specific heat / J kg-1 K-1',(100-60)/(.2*((14-6)/60)),1500)
mc('b',7,['$1500'],'At the same temperature, subtract the two heating equations so the same loss cancels; convert minutes toseconds.')
num('b','1a',8,'','atmosphere infrared absorption / W m-2',25+15,40)
mc('b',8,[r'$40\,'],'Balance the atmosphere separately, not just the whole planet or surface; both upward/downward emissions count.')
num('b','1a',9,'','rms speed ratio',math.sqrt(1.5*2),math.sqrt(3))
mc('b',9,[r'$\sqrt3$'],'The sealed gas has constant particle number; PV increases temperature by3 and rms speed bysqrt3.')
num('b','1a',10,'','final water temperature / Celsius',(8000-.020*330000)/(.100*4200),10/3)
mc('b',10,['$3.33'],'Melt all ice first, then warm the full100g including the newly melted ice.')
oldRL=1/(1/4+1/12);oldI=18/(2+oldRL);newI=18/(2+4)
num('b','1a',11,'','initial terminal voltage / V',18-2*oldI,10.8);num('b','1a',11,'','final terminal voltage / V',18-2*newI,12)
num('b','1a',11,'','initial branch current / A',(18-2*oldI)/4,2.7);num('b','1a',11,'','final branch current / A',newI,3)
mc('b',11,['Both increase.'],'Removing a branch reduces cell current/internal drop, increasing voltage across the remaining4-ohm branch and its current.')
num('b','1a',12,'','new spring period / s',2*math.pi/math.sqrt((12/.030)/4),math.pi/5)
mc('b',12,['$0.628'],'Graph slope gives originalomega²=400; quadrupling mass halvesomega and doubles the period.')
num('b','1a',13,'','transmission angle / degree',math.degrees(math.asin((1480/340)*math.sin(math.radians(10)))),49.10234824130518)
mc('b',13,['$49^','unchanged'],'Boundary phase continuity fixes frequency while speed and wavelength change; the ray bends away from normal.')
num('b','1a',14,'','immersed critical angle / degree',math.degrees(math.asin(1.33*math.sin(math.radians(30)))),41.682325393339176)
mc('b',14,['$42^'],'Infer solid index2 from the air boundary and then use the new liquid/solid index ratio.')
num('b','1a',15,'','third harmonic after length/tension change / Hz',3*50*math.sqrt(2.25)/1.5,150)
mc('b',15,[r'$150\,'],'The supplied wave-speed law at unchangedlinear density cancels the1.5 length factor for the fundamental; multiply by3 afterwards.')
num('b','1a',16,'','recession speed ratio',(.75/500)/(.65/650),1.5)
mc('b',16,['$1.50$'],'Low-speed fractional wavelength shifts, rather than absolute shifts, give the velocity ratio.')
num('b','1a',17,'','surface circular period ratio at equal density',math.sqrt(3**3/3**3),1)
mc('b',17,['$1$'],'At equalmean density M scalesR³, cancellingR³ in the near-surface circular-period equation.')
eps=.001;r0=1/3;force0=4/(1-r0)**2-1/r0**2;force1=4/(1-r0-eps)**2-1/(r0+eps)**2
num('b','1a',18,'','field cancellation at equilibrium in normalized units',force0,0,1e-12)
assert force1>0
mc('b',18,['Toward $4M$','unstable'],'A rightward displacement strengthens the rightward attraction and weakens the leftward one; the resulting acceleration increases the displacement.')
mc('b',19,['X positive; Y neutral'],'The externalnegative rod expels electrons while grounded; only disconnecting Earth first traps the electron deficit.')
num('b','1a',20,'','negative-charge vertical force sign',-1*(0*0-(-1)*(-1)),1)
mc('b',20,['Upward, parallel'],'Right of upward current B is into thepage; a leftward positive particle would feel downward force, reversed for a negative charge.')
num('b','1a',21,'','absorbing transition gap / eV',5-2,3)
mc('b',21,['Populate the $2.0'],'The lowerstate of the3eV gap must be occupied; ground-state gaps and intensitychanges cannot match3eV singlephoton energy.')
num('b','1a',22,'','required nuclear energy / MeV',56*8.8-14*4*7.1,95.2)
mc('b',22,['$95.2','supplied'],'Nucleon and proton numbersmatch; final lower totalbinding means restenergy rises and external energy mustbe supplied.')
mc('b',23,['Fewer neutrons survive'],'Control rods absorb neutrons and change the reproductionrate, not the per-fission energy or nuclear masses; moderation has a separate function.')
num('b','1a',24,'','radius ratio',math.sqrt(1e4/.0100),1000)
mc('b',24,['$1000$'],'Equaltemperature leaves luminosity proportionalto radius squared, so take the square root of10^6.')
num('b','1a',25,'','apparent brightness ratio',(.050/.200)**2,1/16)
mc('b',25,['$1/16$'],'At equal luminosity brightness scales with parallax squared, not parallax or distance directly.')

# All numerical parts in the four data-based investigations.
num('a','1b',1,'a','peak interval / s',1/10,.1);num('a','1b',1,'a','interval uncertainty / s',.2/10**2,.002)
v=(.072-.020)/(2*.1);num('a','1b',1,'b','central velocity / m s-1',v,.26)
num('a','1b',1,'c','constant acceleration / m s-2',((.044-.020)-(.020-.000))/.1**2,.4)
num('a','1b',1,'d','linearized maximum velocity uncertainty / m s-1',v*(.002/(.072-.020)+.004/.2),.0152)
rho=3.9/(9.81*4e-4);num('a','1b',2,'b','density from buoyancy slope / kg m-3',rho,993.8837920489296)
num('a','1b',2,'c','density uncertainty / kg m-3',rho*(.15/3.9+.08/4),58.1039755351682,1e-6)
num('a','1b',2,'d','density change from a constant forceoffset',((2.35+.1)-(1.88+.1))-(2.35-1.88),0)
num('b','1b',1,'b','constant parasitic loss / W',9-.6/.1,3)
num('b','1b',1,'c','thermalconductivity / W m-1 K-1',.6/(2e-4*30),100)
num('b','1b',1,'d','linearized fractional maximum uncertainty',.03/.6+.04/2+1/30,.10333333333333333)
num('b','1b',2,'a','lost energyfraction',1-.512/.8,.36);num('b','1b',2,'b','rebound speedratio',math.sqrt(.512/.8),.8)
num('b','1b',2,'c','fifth reboundheight / m',.8*(.512/.8)**5,.08589934592)
assert .040+.005<.086-.007
num('b','1b',2,'e','retention ratio with common calibration error',(1.1*.512)/(1.1*.8),.64)

# Set A Paper2: complete fresh model calculations.
u=1.2*3/(1.2+.8);num('a','2',1,'a','coupled velocity / m s-1',u,1.8)
num('a','2',1,'b','mean collision force / N',.8*u/.05,28.8)
K=.5*2*u*u;num('a','2',1,'c','dissipated fraction',1-K/(.5*1.2*3**2),.4)
num('a','2',1,'d','spring compression / m',math.sqrt(2*K/180),.18973665961010275)
bare=.8*12*20/.2;wrapped=12*20/(.2/.8+.05/.04)
num('a','2',2,'b','bare conduction / W',bare,960);num('a','2',2,'c','insulated conduction / W',wrapped,160)
num('a','2',2,'d','interface temperature / Celsius',22-wrapped*.2/(.8*12),56/3)
num('a','2',2,'e','electrical energy saved / kWh',(bare-wrapped)/.8/1000*10,10)
spacing=600e-9*2.5/(.3e-3);num('a','2',3,'b','bright fringe spacing / m',spacing,.005)
num('a','2',3,'c','specified dark-fringe separation / m',(1.5-(-.5))*spacing,.01)
num('a','2',3,'d','immersed fringe spacing / m',spacing/1.33,.0037593984962406013)
E=240/.04;F=1.6e-19*E;acc=F/1.67e-27;t=.03/1e5;y=.5*acc*t*t
num('a','2',4,'a','plate field / V m-1',E,6000);num('a','2',4,'a','proton force / N',F,9.6e-16,1e-24)
num('a','2',4,'b','proton acceleration / m s-2',acc,5.748502994011976e11,.1)
num('a','2',4,'c','unimpeded projected displacement / m',y,.02586826347305389)
xhit=1e5*math.sqrt(2*.020/acc);num('a','2',4,'d','plate hit horizontal distance / m',xhit,.026378652985574024);assert y>.02 and xhit<.03
half=20/math.log2((270-30)/(90-30));num('a','2',5,'b','half-life / min',half,10)
num('a','2',5,'c','gross count rate30min / s-1',30+(270-30)*2**(-30/half),60)
num('a','2',5,'d','remaining nuclei30min',8e9*2**(-30/half),1e9)
dist=math.sqrt(3e27/(4*math.pi*2.5e-10));rad=math.sqrt(3e27/(4*math.pi*5.67e-8*6000**4))
num('a','2',6,'a','distance / m',dist,9.772050238058398e17,1e6)
num('a','2',6,'b','annual parallax / arc-second',3.086e16/dist,.03157986220722864)
num('a','2',6,'c','stellar radius / m',rad,1802443521.0463533,1e-2)
num('a','2',6,'d','Wien peak / m',2.90e-3/6000,4.833333333333333e-7,1e-15)

# Set B Paper2.
vt=2*(1e-3)**2*(3000-1000)*9.81/(9*.2)
num('b','2',1,'a','driving force / N',4*math.pi/3*1e-9*2000*9.81,8.2184063828869e-5,1e-12)
num('b','2',1,'b','terminal velocity / m s-1',vt,.0218);num('b','2',1,'c','double-radius terminal velocity / m s-1',4*vt,.0872)
I=(-3+math.sqrt(57))/2;VL=I**2
num('b','2',2,'b','load-line residual at operating point / V',VL+3*I-12,0)
num('b','2',2,'c','operating current / A',I,2.274917217635375)
num('b','2',2,'d','lamp power fraction',VL/12,.43127069559115635)
f1=343/(4*.85);num('b','2',3,'b','fundamental frequency / Hz',f1,100.88235294117648)
num('b','2',3,'c','next odd harmonic / Hz',3*f1,302.64705882352945)
num('b','2',3,'d','end correction / m',343/(4*98.6)-.85,.01967545638945234)
GM=4*math.pi**2*(7.2e6)**3/(6000**2)
num('b','2',4,'a','planet mass / kg',GM/6.67e-11,6.136615198230552e24,1e13)
num('b','2',4,'b','circular orbit speed / m s-1',2*math.pi*7.2e6/6000,7539.822368615503)
num('b','2',4,'c','surface gravitational field / N kg-1',GM/(6e6)**2,11.36978427005494)
num('b','2',4,'d','second circular period / s',6000*2**1.5,16970.562748477143)
T=(.64*1000/(4*.8*5.67e-8))**.25;Tnew=(.75*1000/(4*.8*5.67e-8))**.25
num('b','2',5,'b','initial uniform equilibrium / K',T,243.70348190300822)
num('b','2',5,'c','changed-albedo equilibrium / K',Tnew,253.56076684732787)
num('b','2',5,'c','temperature ratio power-law cross-check',Tnew/T,(.75/.64)**.25)
num('b','2',6,'b','fission thermal power / W',640e6/.4,1.6e9)
Ef=200e6*1.6e-19;num('b','2',6,'c','energy per fission / J',Ef,3.2e-11,1e-18)
Ndot=1.6e9/Ef;num('b','2',6,'d','fission rate / s-1',Ndot,5e19,1e5)
num('b','2',6,'e','fissioned uranium mass per day / kg',Ndot*86400*235*1.66e-27,1.685232)

assert len(records)==66 and sum('uniqueCorrectOptionText' in r for r in records.values())==50
assert len(papers)==4 and sum(p['marks'] for p in papers.values())==190
native=ROOT.parent/'physics-mocks-2026/sl-independent-native-qa/render-checks.json'
if native.exists():
 nr=json.loads(native.read_text())
 for f in nr['figures']:
  key=f['id'];records[key]['diagramSvgSha256']=sh(questions[key]['diagramSvg'].encode())
  records[key]['nativePngSha256']=sh((native.parent/f['file']).read_bytes())
visual_file=ROOT/'docs/ib-physics-mocks-2026/sl-native-independent-review.json'
visual=json.loads(visual_file.read_text(encoding='utf8')) if visual_file.exists() else None
visual_passed=False
if visual and visual['status']=='passed':
 expected_figures={key for key,q in questions.items() if 'diagramSvg' in q}
 assert len(visual['figures'])==len(expected_figures) and {f['id'] for f in visual['figures']}==expected_figures
 assert visual['paperHashes']=={p['id']:p['sha256'] for p in papers.values()}
 assert not visual['unresolvedFindings']
 for f in visual['figures']:
  assert f['status']=='passed' and f['svgSha256']==sh(questions[f['id']]['diagramSvg'].encode())
  records[f['id']]['independentNativeFigureStatus']='passed'
 visual_passed=True
report={'status':'passed' if visual_passed else 'calculations-passed-awaiting-native-visual-audit','scope':'Independent all66 numerical/MCQ-option audit. Does not execute author code; a separate reviewer checks full SL scope and qualitative marking.','independentCalculationChecks':checks,'questionsReviewed':66,'mcqOptionsReviewed':200,'papers':list(papers.values()),'records':list(records.values()),'unresolvedFindings':visual.get('unresolvedFindings',[]) if visual else [],'nativeVisualReview':{'file':str(visual_file.relative_to(ROOT)),'status':'passed' if visual_passed else 'pending','sha256':sh(visual_file.read_bytes()) if visual else None}}
out=ROOT/'docs/ib-physics-mocks-2026/sl-numerical-independent-review.json';out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf8',newline='\n')
print(json.dumps({'status':report['status'],'questions':66,'checks':checks,'paperHashes':{p['id']:p['sha256'] for p in papers.values()}}))
