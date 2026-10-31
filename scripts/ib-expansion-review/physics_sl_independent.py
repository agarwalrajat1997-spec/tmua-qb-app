"""Independent reconstruction from serialized displayed Physics SL inputs.

Does not import or execute any authoring program. Every numerical answer in all
100 additions is reconstructed from its published stem/table/SVG and compared
with the private scheme at its requested significant-figure precision.
"""
from pathlib import Path
import json,re,math,hashlib,xml.etree.ElementTree as ET
from decimal import Decimal,ROUND_HALF_UP
from collections import Counter

ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'docs/ib-expansion-reviews'
BASE={'space-time-motion':200,'particulate-matter':120,'wave-behaviour':120,'fields':100,'nuclear-quantum':100}
records=[];errors=[];checks=[]

def number(s):
    s=s.strip().replace('−','-')
    if '=' in s:s=s.rsplit('=',1)[-1].strip()
    match=re.match(r'([+-]?\d+(?:\.\d*)?(?:e[+-]?\d+)?)(?:\\times\s*10\^\{?([+-]?\d+)\}?)?',s,re.I)
    if not match:return None
    return float(match.group(1))*(10**int(match.group(2)) if match.group(2) else 1)

def maths(s):
    return [x for b in re.findall(r'\$([^$]*)\$',s) if (x:=number(b)) is not None]

def tbl(s):
    out=[]
    for line in s.splitlines():
        if line.startswith('|') and not re.match(r'^\|\s*-',line):
            cells=[v.strip() for v in line.strip('|').split('|')]
            if all(re.fullmatch(r'[+-]?\d+(?:\.\d*)?',v) for v in cells):out.append(list(map(float,cells)))
    return out

def svgtexts(q):
    svg=q.get('diagramSvg')
    assert svg is not None,q['id']+': missing source diagram'
    return [(float(e.attrib.get('x',0)),float(e.attrib.get('y',0)),''.join(e.itertext())) for e in ET.fromstring(svg).iter() if e.tag.endswith('text')]

def chk(q,label,value,what,sf=3):
    group=next(g for g in q['markScheme'] if g['part']==label)
    candidates=[x for step in group['steps'] if step['code'].startswith('A') for x in maths(step['text'])]
    if not candidates:
        candidates=[float(x) for step in group['steps'] if step['code'].startswith('A') for x in re.findall(r'\b\d+(?:\.\d+)?\b',step['text'])]
    if value==0:target=0.;tol=1e-12
    else:
        places=math.floor(math.log10(abs(value)))-sf+1
        # Arithmetic reconstructed with binary floats can land a few ulps below
        # an exact displayed-decimal tie (13.05 or0.05145). Stabilize well beyond
        # all requested answer precision before applying decimal half-up.
        target=float(Decimal(f'{value:.14g}').quantize(Decimal(1).scaleb(places),rounding=ROUND_HALF_UP))
        tol=max(1e-12,abs(target)*1e-10)
    passed=any(abs(x-target)<=tol for x in candidates)
    row={'id':q['id'],'part':label,'quantity':what,'unroundedFromDisplayedInputs':value,'requestedSignificantFigures':sf,'expectedRoundedValue':target,'schemeValues':candidates,'passed':passed}
    checks.append(row)
    if not passed:errors.append(row)

for topic,baseline in BASE.items():
    data=json.loads((ROOT/'content/ib/physics-hl'/f'{topic}.json').read_text(encoding='utf-8'))
    for q in data:
        if q['number']<=baseline:continue
        family=(q['number']-baseline-1)//4;vals=maths(q['stem']);rows=tbl(q['stem']);notes=[]
        if topic=='space-time-motion':
            if family==0:
                m=vals[0];s0,v20=rows[0];s1,v21=rows[-1];slope=(v21-v20)/(s1-s0);a=slope/2
                for lab,value,name in [('a',slope,'gradient in m/s²'),('b',a,'acceleration in m/s²'),('c',m*a,'resultant force in N'),('d',math.sqrt(2*s1/a),'elapsed time in s')]:chk(q,lab,value,name)
                notes=['Constant acceleration is recovered from the displayed v²–s table. Pulling and resultant forces are correctly distinguished.']
            elif family==1:
                m1,u1,m2,u2=vals;v=(m1*u1+m2*u2)/(m1+m2);initial=(m1*u1*u1+m2*u2*u2)/2;final=(m1+m2)*v*v/2;dv=maths(q['parts'][3]['prompt'])[0]
                chk(q,'a',v,'signed common velocity');chk(q,'b',initial,'initial kinetic energy');chk(q,'b',final,'final kinetic energy');chk(q,'b',initial-final,'energy dissipated');chk(q,'d',(m1+m2)*dv,'external impulse')
                notes=['One-dimensional signed momentum; positive velocity and impulse directions checked. Internal conversion of kinetic energy is consistent with negligible external impulse.']
            elif family==2:
                m,height,t,ein,g=vals;useful=m*g*height
                chk(q,'a',useful,'gravitational energy increase');chk(q,'b',useful/ein,'efficiency fraction');chk(q,'c',ein/t,'input power')
                notes=['At unchanged efficiency, halving time doubles input power; no kinetic-energy change at constant speed.']
            elif family==3:
                u,h,g=vals;blocks=re.findall(r'\$([^$]*)\$',q['stem']);du=float(re.search(r'\\pm([\d.]+)',blocks[0]).group(1));dh=float(re.search(r'\\pm([\d.]+)',blocks[1]).group(1));t=math.sqrt(2*h/g);x=u*t
                chk(q,'a',t,'flight time');chk(q,'b',x,'horizontal distance');chk(q,'c',math.sqrt(u*u+2*g*h),'impact speed');chk(q,'d',x*(du/u+dh/(2*h)),'maximum absolute distance uncertainty',2)
                notes=['Independent horizontal/vertical components; maximum rather than root-sum-square uncertainty; drag reduces horizontal speed.']
            else:
                m,u=vals;imp=sum((rows[j][1]+rows[j+1][1])*(rows[j+1][0]-rows[j][0])/2 for j in range(len(rows)-1));peak=max(r[1] for r in rows)
                chk(q,'a',imp,'trapezoidal impulse');chk(q,'b',u+imp/m,'final signed velocity');chk(q,'c',peak/2,'new peak force')
                notes=['Exact area of the displayed piecewise linear pulse; same shape and impulse with twice duration requires half peak force.']
        elif topic=='particulate-matter':
            if family==0:
                power,m,loss,dt,t,plateau=vals;net=power-loss
                chk(q,'a',net,'net heating power');chk(q,'b',net*t/(m*dt),'specific heat capacity');chk(q,'c',net*plateau/m,'latent heat per mass')
                notes=['The rounded displayed heating time is used directly. Phase-change energy raises intermolecular potential energy; ignoring losses overestimates c.']
            elif family==1:
                radius,S,alpha,emiss,sigma=vals;alpha2=maths(q['parts'][3]['prompt'])[0];absorbed=(1-alpha)*S*math.pi*radius**2;T=((1-alpha)*S/(4*emiss*sigma))**.25
                chk(q,'b',absorbed,'absorbed stellar power');chk(q,'c',T,'equilibrium temperature');chk(q,'d',((1-alpha2)*S/(4*emiss*sigma))**.25,'temperature after albedo increase')
                notes=['Projected disc and spherical emission areas checked separately; kelvin and emissivity in the radiation balance; atmosphere limitation appropriate.']
            elif family==2:
                T,R,M=vals;V,p=rows[0];amount=(p*1000)*(V*.001)/(R*T)
                chk(q,'a',amount,'gas amount in mol');chk(q,'c',math.sqrt(3*R*T/M),'rms molecular speed');chk(q,'d',1.5*p*V,'internal energy in J')
                assert max(p*V for V,p in rows)-min(p*V for V,p in rows)<1e-4
                notes=['kPa×litre converts to J; rms not mean speed; monatomic sample expressly stated; displayed pV values constant within rounding.']
            elif family==3:
                I0,V0=rows[0];I1,V1=rows[-1];r=(V0-V1)/(I1-I0);emf=V0+r*I0;I=maths(q['parts'][1]['prompt'])[0];V=emf-r*I
                chk(q,'a',r,'internal resistance');chk(q,'a',emf,'emf intercept');chk(q,'b',V/I,'load resistance');chk(q,'c',I*V,'useful load power');chk(q,'c',I*I*r,'internal heating power')
                notes=['Negative gradient and zero-current intercept checked; terminal voltage rather than emf used for external load; load+internal power equals emf×I.']
            else:
                V,rf,dark,bright,threshold=vals
                chk(q,'a',V*dark/(rf+dark),'dark output voltage');chk(q,'b',V*bright/(rf+bright),'bright output voltage');chk(q,'c',threshold*rf/(V-threshold),'threshold LDR resistance')
                notes=['Ideal high-resistance voltmeter and loading explanation checked; controller activation inequality consistent with both outputs; diagram node and polarity reviewed separately.']
        elif topic=='wave-behaviour':
            if family==0:
                amp=vals[0];x0,a0=rows[0];x1,a1=rows[-1];omega2=-(a1-a0)/(x1-x0);omega=math.sqrt(omega2)
                chk(q,'b',omega,'angular frequency');chk(q,'b',2*math.pi/omega,'oscillation period');chk(q,'c',omega2*amp,'maximum acceleration')
                notes=['a proportional to −x, angular frequency and period are shared C.1; no phase-time or quantitative oscillation-energy demand.']
            elif family==1:
                texts=svgtexts(q);tick1=[float(t) for x,y,t in texts if abs(y-183)<1e-6];tick2=[float(t) for x,y,t in texts if abs(y-388)<1e-6];amplitudes=[float(t) for x,y,t in texts if abs(x-60)<1e-6 and abs(y-65)<1e-6];lam=(max(tick1)-min(tick1))/2;T=(max(tick2)-min(tick2))/2;amp=amplitudes[0]
                chk(q,'a',amp,'amplitude in mm read from SVG');chk(q,'a',lam,'wavelength from two full spatial cycles');chk(q,'b',T,'period from two full time cycles');chk(q,'b',1/T,'frequency');chk(q,'c',lam/T,'wave speed')
                notes=['Both input axes reconstructed from serialized SVG text, with two complete cycles on each trace; particles oscillate rather than moving with the wave pattern.']
            elif family==2:
                d,D,totalmm=vals;uncmm=float(re.search(r'\\pm([\d.]+)',q['stem']).group(1));spacing=totalmm*.001/5;lam=spacing*d/D
                chk(q,'a',spacing,'adjacent-fringe spacing');chk(q,'b',lam,'wavelength');chk(q,'c',uncmm*.001*d/(5*D),'wavelength absolute uncertainty',2)
                notes=['Five intervals, millimetre conversion and common fractional uncertainty verified from displayed distance; coherent-source and doubled-screen-distance explanations correct.']
            elif family==3:
                length,c=vals
                chk(q,'b',4*length,'first-harmonic wavelength');chk(q,'b',c/(4*length),'first-harmonic frequency');chk(q,'c',3*c/(4*length),'next permitted mode frequency')
                notes=['Closed displacement node/open displacement antinode; odd harmonics and resonance explanation correct. First-harmonic terminology fixed during review.']
            else:
                rest,observed,c=vals;shift=observed-rest
                chk(q,'b',shift,'wavelength shift in nm');chk(q,'b',c*shift/rest,'radial recession speed');chk(q,'c',c/(observed*1e-9),'observed frequency')
                notes=['Redshift recession sign; only line-of-sight velocity measured; v/c below0.007 supports the expressly stated low-speed approximation.']
        elif topic=='fields':
            if family==0:
                mass,R,h,satmass,Tref,twor,G=vals;r=R+h;g=G*mass/r**2;T=Tref/math.sqrt(twor**3);ratio=maths(q['parts'][3]['prompt'])[0]
                chk(q,'a',g,'field at R+h');chk(q,'b',satmass*g,'gravitational force');chk(q,'c',T,'period from measured reference and Kepler');chk(q,'d',T*ratio**1.5,'second period from Kepler')
                notes=['Rewritten shared-content version checked from measured reference period; no orbital-speed formula, potential or orbital-energy calculation required. Inward acceleration and force direction correct.']
            elif family==1:
                distance,qa,qb,k,qe=vals;x=distance/(1+math.sqrt(qb/qa));E=k*(qa-qb)/(distance/2)**2
                chk(q,'b',x,'interior zero-field distance from A');chk(q,'c',E,'signed midpoint field');chk(q,'d',qe*E,'signed electron force')
                notes=['Opposing fields between like charges; unique interior root; midpoint E toward A and electron force toward B; field-zero force is zero.']
            elif family==2:
                I,L,B=vals;angle=maths(q['parts'][1]['prompt'])[0]
                chk(q,'a',B*I*L,'perpendicular-wire magnetic force');chk(q,'b',B*I*L*math.sin(math.radians(angle)),'inclined-wire force')
                notes=['Conventional current right crossed with B into page gives upward force; reversed current reverses it. Retagged D.3 during review.']
            elif family==3:
                u,E,L,qcharge,m=vals;a=qcharge*E/m;t=L/u;y=a*t*t/2;angle=math.degrees(math.atan(a*t/u))
                chk(q,'a',a,'vertical acceleration');chk(q,'b',t,'field transit time');chk(q,'c',y,'exit vertical displacement');chk(q,'d',angle,'exit velocity angle')
                notes=['No horizontal force; positive charge accelerates upward; electric force does positive work on developing displacement.']
            else:
                B,r,t=vals;speed=math.pi*r/t
                chk(q,'a',speed,'semicircle speed');chk(q,'b',speed/(B*r),'charge-to-mass ratio');chk(q,'d',2*r,'radius at doubled speed')
                notes=['Half-circumference divided by measured time; magnetic work zero; doubling speed doubles r and leaves semicircle time unchanged.']
        else:
            if family==0:
                ev,h,c=vals;levels=sorted(float(re.search(r'(-?[\d.]+) eV',text).group(1)) for x,y,text in svgtexts(q) if ' eV' in text);gaps=[levels[1]-levels[0],levels[2]-levels[1],levels[2]-levels[0]];energy=(levels[2]-levels[1])*ev
                chk(q,'a',energy,'3-to-2 photon energy');chk(q,'b',energy/h,'photon frequency');chk(q,'b',h*c/energy,'photon wavelength')
                for gap in gaps:chk(q,'c',gap,'distinct downward energy gap in eV')
                chk(q,'d',h*c/(min(gaps)*ev),'longest wavelength')
                notes=['Bound-level energies read from serialized SVG, not a Bohr formula; all three gaps distinct; minimum gap is2→1 for every variant.']
            elif family==1:
                bg=vals[0];net0=rows[0][1]-bg;half=rows[1][0]-rows[0][0];future=maths(q['parts'][2]['prompt'])[0]
                chk(q,'a',net0,'initial source-only counts');chk(q,'b',half,'half-life from successive background-corrected halvings');chk(q,'c',net0/(2**(future/half))+bg,'future total count')
                assert all(abs((rows[j][1]-bg)/(rows[j+1][1]-bg)-2)<1e-10 for j in range(len(rows)-1))
                notes=['Only integer numbers of half-lives are used; background restored after decay; randomness and unchanged isotope half-life explanations correct.']
            elif family==2:
                Pel,eta,MeV,massN,ev,c=vals;thermal=Pel/eta;efission=MeV*1e6*ev;rate=thermal/efission
                chk(q,'a',thermal,'thermal power');chk(q,'b',rate,'fission rate');chk(q,'c',efission/c**2,'mass defect per fission');chk(q,'d',rate*86400*massN,'fuel nuclei mass per day')
                notes=['Recoverable thermal energy and electrical efficiency distinct; per-nucleus mass is not confused with mass defect; controlled-chain criterion correct.']
            elif family==3:
                peak,flux,d,b,sigma=vals;T=b/peak;lum=4*math.pi*d*d*flux;radius=math.sqrt(lum/(4*math.pi*sigma*T**4))
                chk(q,'a',T,'Wien temperature from displayed peak');chk(q,'b',lum,'luminosity');chk(q,'c',radius,'stellar radius from displayed temperature');chk(q,'d',16,'luminosity ratio for twice temperature')
                notes=['Nine-digit input peak used directly; bolometric inverse-square flux, black-body emissivity and kelvin checked; thermal/radiation pressure wording uses corrected guide.']
            else:
                bg=vals[0];tablelines=[line for line in q['stem'].splitlines() if line.startswith('|')];data={line.strip('|').split('|')[0].strip():float(line.strip('|').split('|')[1]) for line in tablelines if line.startswith('| No absorber') or line.startswith('| Thin paper') or line.startswith('| Several millimetres') or line.startswith('| Aluminium plus')};none=data['No absorber'];paper=data['Thin paper'];al=data['Several millimetres of aluminium'];lead=data['Aluminium plus thick lead'];alpha=none-paper;beta=paper-al;gamma=al-bg
                for value,name in [(alpha,'alpha contribution'),(beta,'beta contribution'),(gamma,'gamma contribution')]:chk(q,'a',value,name)
                chk(q,'b',(lead-bg)/gamma,'lead transmission fraction')
                notes=['Successive count differences and background-corrected gamma ratio; detected contributions not falsely equated with source decay branching; ionization/penetration and averaging limitations correct.']
        marks_ok=sum(p['marks'] for p in q['parts'])==q['marks']==sum(int(s['code'][1:]) for g in q['markScheme'] for s in g['steps'])
        if not marks_ok:errors.append({'id':q['id'],'issue':'mark total mismatch'})
        records.append({'id':q['id'],'topic':topic,'family':family+1,'level':q['level'],'syllabusCode':q['syllabusCode'],'marksReviewed':q['marks'],'scopeAndReasoning':notes,'quantitiesReconstructed':len([x for x in checks if x['id']==q['id']]),'sha256':hashlib.sha256(json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()})

report={'status':'passed' if not errors else 'findings','reviewedRecords':len(records),'numericalQuantities':len(checks),'topicCounts':dict(Counter(r['topic'] for r in records)),'errors':errors,'records':records,'checks':checks,'method':'Independent reconstruction solely from serialized displayed stems, tables and SVG text. No authoring imports. Every numerical response compared at requested significant figures; qualitative reasoning, dimensions, signs and scope reviewed by family with per-record hashes.'}
(DEST/'physics-sl-independent-numeric.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['records','checks']},ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
