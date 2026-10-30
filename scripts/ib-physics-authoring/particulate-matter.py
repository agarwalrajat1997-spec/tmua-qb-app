"""Rebuild 120 independently authored Theme B questions using only Python's standard library.

Run from any directory. All numerical answers are computed from the declared models.
Four variants at most per editorial family; variations change a physical condition or unknown.
"""
import json
import math
import re
from collections import Counter
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'content/ib/physics-hl/particulate-matter.json'
REPORT = ROOT / 'docs/ib-physics-reviews/particulate-matter.txt'
Q = []
FAMILIES = []
SIGMA = 5.67e-8
KB = 1.38e-23
NA = 6.02e23
R = 8.31

def f(x, sig=3):
    return format(x, f'.{sig}g')

def p(prompt, *steps):
    return (prompt, list(steps))

def step(text, code='A1'):
    return (code, text)

def format_literal_subscripts(value):
    """Format only literal underscore identifiers outside existing dollar math."""
    # These supplied fractional powers use explicit math rather than caret prose.
    for plain, maths in {
        '2^(1/4)': r'$2^{1/4}$',
        '(0.5)^(1/4)': r'$(0.5)^{1/4}$',
        '(0.80/0.50)^(1/4)': r'$(0.80/0.50)^{1/4}$',
        'flux^(1/4)': r'$\text{flux}^{1/4}$',
        'distance^(−1/2)': r'$\text{distance}^{−1/2}$',
        'T = (F_surface/σ)^(1/4)': r'$T = (F_{\mathrm{surface}}/\sigma)^{1/4}$',
        'T = [(1 − a)S/(4eσ)]^(1/4)': r'$T = [(1 − a)S/(4eσ)]^{1/4}$',
        'T_eff = (F_out/σ)^(1/4)': r'$T_{\mathrm{eff}} = (F_{\mathrm{out}}/\sigma)^{1/4}$',
        'PV^(5/3)': r'$PV^{5/3}$',
        'TV^(2/3)': r'$TV^{2/3}$',
    }.items():
        value=value.replace(plain, maths)
    value=re.sub(r'T_f = ([0-9.]+)\(V_i/V_f\)\^\(2/3\)',
                 lambda m:r'$T_{\mathrm{f}} = '+m[1]+r'(V_{\mathrm{i}}/V_{\mathrm{f}})^{2/3}$',value)
    greek={'Δ':r'\Delta ','θ':r'\theta ','λ':r'\lambda ','ρ':r'\rho ','η':r'\eta ','ε':r'\varepsilon ','Ω':r'\Omega '}
    identifier=re.compile(r'([A-Za-z0-9ΔθλρηεΩ]+)_([A-Za-z0-9]+(?:[-,][A-Za-z0-9]+)?)')
    def replacement(match):
        base=''.join(greek.get(char,char) for char in match[1]).rstrip()
        suffix=match[2]
        sub=suffix if suffix.isdigit() else (r'\text{'+suffix+'}' if '-' in suffix else r'\mathrm{'+suffix+'}')
        return '$'+base+'_{'+sub+'}$'
    return ''.join(piece if piece.startswith('$') else identifier.sub(replacement,piece)
                   for piece in re.split(r'(\$\$[\s\S]*?\$\$|\$(?:\\.|[^$\n])+\$)',value))

def numeric(correct, distractors, unit=''):
    vals = [correct] + list(distractors)
    assert len(vals) == 4 and all(math.isfinite(x) for x in vals)
    labels = [(f(x) + (' ' + unit if unit else '')) for x in vals]
    assert len(set(labels)) == 4, labels
    return labels

def svg(body, caption='', w=640, h=340):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img"><title>{escape(caption)}</title><rect width="{w}" height="{h}" fill="#ffffff"/>{body}</svg>'

def text(x, y, label, size=17, color='#172b4d', anchor='middle'):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Arial, sans-serif" font-size="{size}" fill="{color}">{escape(str(label))}</text>'

def line(x1,y1,x2,y2,color='#172b4d',width=2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>'

def arrow(x1,y1,x2,y2,label='',color='#1b6ca8'):
    a=math.atan2(y2-y1,x2-x1)
    p1=(x2-10*math.cos(a-.45),y2-10*math.sin(a-.45))
    p2=(x2-10*math.cos(a+.45),y2-10*math.sin(a+.45))
    s=line(x1,y1,x2,y2,color,3)+f'<polyline points="{p1[0]},{p1[1]} {x2},{y2} {p2[0]},{p2[1]}" fill="none" stroke="{color}" stroke-width="3"/>'
    return s+(text((x1+x2)/2+8,(y1+y2)/2-10,label,15,color) if label else '')

def axis_limits(values):
    lo=min(0,min(values));hi=max(0,max(values));span=hi-lo or 1
    unit=10**math.floor(math.log10(span/4))
    increment=next(x for x in (1,2,2.5,5,10) if x*unit>=span/4-1e-12*span)*unit
    lower=math.floor(lo/increment+1e-10)*increment
    upper=math.ceil(hi/increment-1e-10)*increment
    if lower==upper:upper=lower+increment
    ticks=[lower+j*increment for j in range(round((upper-lower)/increment)+1)]
    return lower,upper,ticks

def plot(xs,ys,xlab,ylab, caption='', extra=None, labels=False):
    assert len(xs)==len(ys) and len(xs)>=2
    xs,ys=zip(*dict.fromkeys(zip(xs,ys)))
    xmin,xmax,xticks=axis_limits(xs)
    ymin,ymax,yticks=axis_limits(ys)
    def xy(x,y):return (85+(x-xmin)/(xmax-xmin)*490,275-(y-ymin)/(ymax-ymin)*215)
    body=arrow(85,275,595,275)+arrow(85,275,85,40)
    if ymin<0<ymax:body+=line(85,xy(0,0)[1],575,xy(0,0)[1],'#b6c1cf',1)
    if xmin<0<xmax:body+=line(xy(0,0)[0],60,xy(0,0)[0],275,'#b6c1cf',1)
    body+=text(340,326,xlab)+text(88,25,ylab,16,anchor='start')
    for x in xticks:
        px,_=xy(x,0)
        body+=line(px,275,px,280)+text(px,299,f(x),11)
    for y in yticks:
        _,py=xy(0,y)
        body+=line(80,py,85,py)+text(75,py+4,f(y),11,anchor='end')
    for x,y in zip(xs,ys):
        px,py=xy(x,y)
        if len(xs)<=12:body+=f'<circle cx="{px}" cy="{py}" r="4" fill="#1b6ca8"/>'
        if labels:body+=text(px,py-10,f'({f(x)}, {f(y)})',13)
    body+=f'<polyline points="'+ ' '.join(f'{xy(x,y)[0]},{xy(x,y)[1]}' for x,y in zip(xs,ys))+'" fill="none" stroke="#1b6ca8" stroke-width="2"/>'
    if extra:
        ex,ey=extra
        body+=f'<polyline points="'+ ' '.join(f'{xy(x,y)[0]},{xy(x,y)[1]}' for x,y in zip(ex,ey))+'" fill="none" stroke="#c25720" stroke-width="2" stroke-dasharray="6 4"/>'
    return svg(body,caption)

def budget(solar, reflected, downward, upward, solved=False):
    b='<rect x="70" y="330" width="600" height="18" fill="#e4bc7c"/><rect x="70" y="130" width="600" height="42" rx="10" fill="#dbeef9"/>'
    b+=text(370,376,'Surface')+text(370,155,'Atmospheric layer')
    b+=arrow(125,35,125,320)+arrow(250,320,250,35,color='#b15e2b')
    b+=arrow(405,182,405,320)+arrow(560,320,560,182,color='#b15e2b')
    b+=arrow(560,120,560,35,color='#b15e2b')
    b+=text(175,82,str(solar),18)+text(175,103,'solar in',14)
    b+=text(295,82,str(reflected),18)+text(295,103,'reflected',14)
    b+=text(340,237,str(downward),18)+text(340,260,'IR down',14)
    b+=text(620,237,str(upward),18)+text(620,260,'surface IR',14)
    b+=text(630,65,str(downward),18)+text(630,88,'IR to space',14)
    b+=text(370,408,'IR = infrared; mean fluxes / W m⁻²; schematic',14)
    return svg(b,'One-layer model including infrared emission to space',740,430)

def heating_stages(initial,final):
    low=min(initial,0)-5;high=max(final,0)+5
    Y=lambda temperature:265-(temperature-low)/(high-low)*205
    points=[(85,Y(initial)),(205,Y(0)),(445,Y(0)),(565,Y(final))]
    b=arrow(75,Y(0),605,Y(0))+arrow(85,275,85,35)
    b+=text(340,325,'Heating time (schematic; no numerical time scale)',14)+text(90,25,'Temperature / °C',16,anchor='start')
    b+='<polyline points="'+' '.join(f'{x},{y}' for x,y in points)+'" fill="none" stroke="#1b6ca8" stroke-width="3"/>'
    for value in sorted(set([initial,0,final])):b+=text(65,Y(value)+5,f(value),13,anchor='end')
    b+=text(325,Y(0)-15,'melting',15)+text(555,Y(final)-15,'water',13)
    return svg(b,'Schematic heating stages; numerical time is deliberately not supplied')

def slab(T1,T2,k,d,A):
    b='<rect x="220" y="75" width="200" height="170" fill="#deebf5" stroke="#172b4d" stroke-width="2"/>'
    b+=text(160,155,f'{T1} °C')+text(480,155,f'{T2} °C')+arrow(225,270,415,270,f'd = {d} m')
    b+=arrow(245,155,395,155,'heat')+text(320,50,f'k = {k} W m⁻¹ K⁻¹; A = {A} m²',15)
    return svg(b,'Steady thermal conduction across a slab')

def circuit(rtop,rbottom,supply, answer=False, internal=None):
    b=line(150,70,470,70)+line(470,70,470,105)+line(470,145,470,185)+line(470,225,470,280)+line(470,280,150,280)
    b+=line(150,70,150,160)+line(150,180,150,280)
    b+=line(128,160,172,160,width=3)+line(138,180,162,180,width=3)
    b+='<rect x="452" y="105" width="36" height="40" fill="white" stroke="#172b4d" stroke-width="2"/><rect x="452" y="185" width="36" height="40" fill="white" stroke="#172b4d" stroke-width="2"/>'
    b+=text(505,130,rtop,15,anchor='start')+text(505,210,rbottom,15,anchor='start')+text(94,175,supply,15)
    b+=line(470,165,560,165)+f'<circle cx="470" cy="165" r="4" fill="#172b4d"/>'+text(575,160,'Vout',14)
    b+=line(470,280,560,280)+text(575,280,'0 V',14)
    if answer:b+=arrow(300,50,400,50,'I')
    return svg(b,'Two-resistor potential divider; output relative to lower node')

def pv_cycle(points, labels, direction=True):
    vs=[a for a,b in points];ps=[b for a,b in points]
    vmax=max(vs)*1.25;pmax=max(ps)*1.25
    xy=lambda v,p:(85+v/vmax*490,275-p/pmax*220)
    b=arrow(85,275,590,275)+arrow(85,275,85,35)+text(335,325,'Volume / 10⁻³ m³')+text(90,23,'Pressure / kPa',16,anchor='start')
    for j,(v,pres) in enumerate(points):
        x,y=xy(v,pres);v2,p2=points[(j+1)%len(points)];xx,yy=xy(v2,p2)
        label_y=y-15 if pres==max(ps) else y+25
        b+=line(x,y,xx,yy,'#1b6ca8',2)+text(x,label_y,f'{labels[j]} ({v}, {pres})',14)
        if direction:b+=arrow(x+(xx-x)*.35,y+(yy-y)*.35,x+(xx-x)*.65,y+(yy-y)*.65)
    return svg(b,'Closed gas cycle with traversal direction')

def add(family, sub, variant, kind, title, stem, *, opts=None, reasoning='', parts=None, level='core', diagram=None, worked=None, summary='', difficulty=None):
    n=len(Q)+1
    stem=re.sub(r'[-+]?\d+\.\d{10,}',lambda match:f(float(match.group()),10),stem)
    if difficulty is None:
        if kind=='multiple-choice':
            difficulty='easy' if family in {1,2,7,8,13,14,19} or (family==25 and variant==2) or (family==26 and variant<3) else 'medium'
        else:
            difficulty='hard' if family in {10,11,17,22,23,24,30} else 'medium'
    q={'id':f'ib-phy-b-{n:03}','subject':'physics-hl','topicId':'particulate-matter','collectionId':'physics-particulate-matter','number':n,'title':title,'subtopic':['Thermal energy transfers','Greenhouse effect','Gas laws','Thermodynamics','Current and circuits'][sub-1],'syllabusCode':f'B.{sub}','level':level,'questionType':kind,'difficulty':difficulty,'calculator':True,'stem':stem,'source':{'document':'Independent syllabus-authored practice','question':n},'verification':{'method':'Deterministic calculation and model/units checks in the independent authoring script','notes':f'Editorial family B{family:02}; physical variant {variant+1}/4. Original stem, values and diagrams. Author checked signs, units, givens and mark totals; independent editorial review is separate.'},'status':'published'}
    if kind=='multiple-choice':
        assert opts and len(opts)==4 and len(set(opts))==4
        shift=(n-1)%4; ordered=opts[-shift:]+opts[:-shift] if shift else opts[:]
        correct='ABCD'[shift]
        q.update(marks=1,parts=[],options=[{'label':lab,'text':t} for lab,t in zip('ABCD',ordered)],correctOption=correct,markScheme=[{'part':'','steps':[{'code':'A1','text':f'{correct}. {reasoning}'}]}])
    else:
        assert parts
        q['parts']=[];q['markScheme']=[]
        for j,(prompt,steps) in enumerate(parts):
            lab='abcdefghijklmnopqrstuvwxyz'[j]; marks=sum(int(c[1:]) for c,t in steps)
            q['parts'].append({'label':lab,'prompt':prompt,'marks':marks})
            q['markScheme'].append({'part':lab,'steps':[{'code':c,'text':t} for c,t in steps]})
        q['marks']=sum(x['marks'] for x in q['parts'])
    if diagram:q['diagramSvg']=diagram
    if worked:q['markSchemeDiagramSvg']=worked
    if summary:q['answerSummary']=summary
    q['stem']=format_literal_subscripts(q['stem'])
    for part in q['parts']:part['prompt']=format_literal_subscripts(part['prompt'])
    for option in q.get('options',[]):option['text']=format_literal_subscripts(option['text'])
    for group in q['markScheme']:
        for point in group['steps']:point['text']=format_literal_subscripts(point['text'])
    Q.append(q);FAMILIES.append(family)

# B.1 -- six distinct skill families.
concepts=[
('Melting at constant temperature','A pure crystalline solid melts at its melting point while receiving energy. Which microscopic change explains the energy transfer?', ['The average intermolecular potential energy increases.','The mean random kinetic energy steadily increases.','The molecules stop moving.','The mass of each molecule increases.'],'The constant temperature indicates no rise in mean random kinetic energy. Energy changes intermolecular configuration and hence potential energy.'),
('Thermal contact','A small hot metal block touches a larger cool block in an insulated box. Which statement about the initial net energy transfer is correct?', ['Energy transfers from the hotter block to the cooler block.','Energy transfers from the block with greater mass.','Energy transfers toward the block with greater total internal energy.','No energy transfers until their temperatures are equal.'],'The temperature difference determines the direction of net thermal energy transfer, not mass or total internal energy.'),
('Internal energy of a liquid','Which description accounts for the internal energy of a stationary sample of liquid?', ['The sum of random molecular kinetic energy and intermolecular potential energy.','Only the kinetic energy of the sample as a whole.','Only intermolecular potential energy.','The energy needed to lift the sample through one metre.'],'Internal energy concerns microscopic random kinetic and interaction energies. A stationary sample still has molecular motion.'),
('Convection in a sealed cavity','The lower surface of an air-filled cavity is heated. Which sequence best explains a possible convection current?', ['The heated air expands, its density falls, and buoyancy makes it rise.','The heated air contracts, its density rises, and it rises.','The molecules become heavier and pull cooler air upward.','Infrared photons carry the entire air mass upward.'],'Heating allows local expansion. Lower-density air experiences a net upward buoyancy force, while cooler air moves in to replace it.')]
for v,(title,stem,opts,why) in enumerate(concepts):add(1,1,v,'multiple-choice',title,stem,opts=opts,reasoning=why)

for v in range(4):
    m=.4+.1*v;c=700+100*v;dt=15+5*v;heat=m*c*dt
    if v==0:stem=f'A {m} kg solid with specific heat capacity {c} J kg⁻¹ K⁻¹ warms by {dt} K without changing phase. How much energy does it absorb?';good=heat;bad=[heat/m,heat/1000,heat*2];unit='J'
    elif v==1:stem=f'A {m} kg sample absorbs {f(heat)} J and warms by {dt} K. What is its specific heat capacity?';good=c;bad=[c*m,c/dt,c*2];unit='J kg⁻¹ K⁻¹'
    elif v==2:stem=f'A solid absorbs {f(heat)} J. Its specific heat capacity is {c} J kg⁻¹ K⁻¹ and its temperature rise is {dt} K. What is its mass?';good=m;bad=[m*1000,m*dt,m/2];unit='kg'
    else:stem=f'A {m} kg solid with specific heat capacity {c} J kg⁻¹ K⁻¹ loses {f(heat)} J. What is the magnitude of its temperature decrease?';good=dt;bad=[dt/2,dt*m,dt*1000];unit='K'
    add(2,1,v,'multiple-choice','Using heat capacity',stem,opts=numeric(good,bad,unit),reasoning=f'Use Q = mcΔT with the magnitude of the transferred energy. Rearranging for the requested quantity gives {f(good)} {unit}.')

for v in range(4):
    m=[.12,.18,.25,.3][v];t0=[-15,0,-8,0][v];tf=[12,25,0,40][v];ci=2100;cw=4200;lf=3.34e5
    q1=m*ci*(-t0);q2=m*lf;q3=m*cw*tf;total=q1+q2+q3;power=150+50*v;time=total/power
    assert math.isclose(total,m*(ci*(-t0)+lf+cw*tf))
    add(3,1,v,'structured','Heating through a phase change',f'A {m} kg sample of ice initially at {t0} °C is converted completely to water at {tf} °C by a heater delivering {power} W to the sample. Take c_ice = 2100 J kg⁻¹ K⁻¹, c_water = 4200 J kg⁻¹ K⁻¹ and L_f = 3.34 × 10⁵ J kg⁻¹. No energy escapes.',parts=[p('Calculate the total energy supplied.',step(f'Separate warming the ice, melting and warming the water: Q = mc_ice(0 − T_i) + mL_f + mc_water T_f.','M1'),step(f'The contributions are {f(q1)} J, {f(q2)} J and {f(q3)} J, giving Q = {f(total)} J.')),p('Calculate the minimum heating time and explain why temperature stays constant while the ice melts.',step(f't = Q/P = {f(total)}/{power} = {f(time)} s.'),step('During melting the supplied energy increases intermolecular potential energy instead of increasing mean random kinetic energy.','R1'))],diagram=heating_stages(t0,tf),worked=plot([0,q1,q1+q2,total],[t0,0,0,tf],'Energy supplied / J','Temperature / °C','Energy allocation through the phase change'),summary=f'{f(total)} J; {f(time)} s')

for v in range(4):
    hot=60+10*v;cold=10+5*v;k=.2+.1*v;area=.6+.2*v;d=.025+.005*v;rate=k*area*(hot-cold)/d;hours=2+v;energy=rate*hours*3600
    add(4,1,v,'structured','A conduction design constraint',f'A uniform insulating panel has conductivity {f(k)} W m⁻¹ K⁻¹, area {f(area)} m² and thickness {f(d)} m. Its faces remain at {hot} °C and {cold} °C. Edge losses are negligible.',parts=[p('Calculate the steady energy-transfer rate through the panel.',step('Use the magnitude P = kA(T_hot − T_cold)/d.','M1'),step(f'P = {f(rate)} W, from the hotter face to the cooler face.')),p(f'The design is changed to reduce this rate by a factor of {v+2} without changing material, area or face temperatures. Determine the new thickness.',step(f'At fixed k, A and temperature difference, P is inversely proportional to d.','R1'),step(f'd_new = {v+2}d = {f((v+2)*d)} m.')),p(f'Calculate the energy transferred through the original panel in {hours} h.',step(f'E = Pt = {f(rate)} × {hours*3600} = {f(energy)} J.'))],diagram=slab(hot,cold,f(k),f(d),f(area)),worked=plot([d*(1+(v+1)*j/40) for j in range(41)],[rate/(1+(v+1)*j/40) for j in range(41)],'Thickness / m','Transfer rate / W','Inverse conduction-rate relationship',labels=False),summary=f'{f(rate)} W; new thickness {f((v+2)*d)} m')

for v in range(4):
    temp=[3200,4500,6100,8000][v];radius=[1.1e8,2.2e8,3.5e8,4.0e8][v];lum=4*math.pi*radius**2*SIGMA*temp**4;dist=(2+v)*1e17;bright=lum/(4*math.pi*dist**2);peak=2.90e-3/temp
    add(5,1,v,'structured','Radiation from a distant sphere',f'A spherical source behaves as a blackbody with radius {f(radius)} m and surface temperature {temp} K. An observer is {f(dist)} m from its centre. Use σ = 5.67 × 10⁻⁸ W m⁻² K⁻⁴ and Wien constant 2.90 × 10⁻³ m K. Absorption between source and observer is negligible.',parts=[p('Calculate the total radiated power.',step('Use the entire spherical area: L = 4πr²σT⁴.','M1'),step(f'L = {f(lum)} W.')),p('Calculate the received power per unit area and the peak wavelength of the emitted spectrum.',step(f'b = L/(4πd²) = {f(bright)} W m⁻².'),step(f'λ_max = 2.90 × 10⁻³/T = {f(peak)} m.')),p('The distance doubles. State and explain the change in received power per unit area.',step('It becomes one quarter as large because the same luminosity spreads over four times the area.','R1'))],summary=f'L = {f(lum)} W; b = {f(bright)} W m⁻²; peak = {f(peak)} m')

for v in range(4):
    mass=.25+.05*v;power=30+10*v;c=600+200*v;loss=5+v;slope=(power-loss)/(mass*c);ts=[0,30,60,90,120];temps=[20+slope*t for t in ts];rounded=[round(x,2) for x in temps];measured=(rounded[-1]-rounded[0])/120;c_est=(power-loss)/(mass*measured)
    table='\n\n| Time / s | Temperature / °C |\n|---:|---:|\n'+'\n'.join(f'| {t} | {T:.2f} |' for t,T in zip(ts,rounded))
    add(6,1,v,'data-based','Calorimeter data and heat leakage',f'The following simulated data describe a {f(mass)} kg block heated at constant electrical power {power} W. A separate calibration estimates a constant {loss} W transfer to the surroundings over this interval. Each temperature reading has uncertainty ±0.10 °C.'+table,parts=[p('Use the full time interval to estimate the rate of temperature rise.',step('Use the difference of endpoint temperatures divided by the 120 s interval.','M1'),step(f'Gradient = {f(measured)} K s⁻¹; accept a fit consistent with the displayed readings.')),p('Determine the specific heat capacity of the block, allowing for the heat leakage.',step('Net power storing thermal energy is P_net = P_electrical − P_loss = mc(dT/dt).','M1'),step(f'c = ({power} − {loss})/({f(mass)} × {f(measured,5)}) = {f(c_est)} J kg⁻¹ K⁻¹.')),p('A student neglects the heat leakage. State the direction of the resulting error in c and explain it.',step('The calculated c is too large: the student attributes all electrical power to raising the block temperature.','R1')),p('Suggest a specific improvement that reduces this bias.',step('Add effective thermal insulation around the block, or measure the heat leakage under the same temperature conditions and subtract it.','R1'))],diagram=plot(ts,rounded,'Time / s','Temperature / °C','Simulated calorimeter measurements'),worked=plot(ts,rounded,'Time / s','Temperature / °C','Use the full interval when estimating the slope'),summary=f'c ≈ {f(c_est)} J kg⁻¹ K⁻¹')

# B.2 -- radiation budgets, molecular mechanisms and model limitations.
green=[
('Molecular infrared absorption','Why can a greenhouse gas absorb selected infrared frequencies?', ['Its molecular energy-level differences match the photon energies.','It absorbs every wavelength equally because it is a gas.','Its molecules must first become electrically charged.','Infrared photons have no energy.'],'Absorption is associated with allowed molecular energy changes; photon energy must match an available transition.'),
('Re-emission directions','In a simple greenhouse model, an atmospheric layer absorbs infrared radiation from the surface. Which statement about subsequent emission is appropriate?', ['It emits infrared in both upward and downward directions.','It emits only toward space.','It reflects every photon directly back without an energy interaction.','It permanently stores all absorbed radiation.'],'Thermal emission occurs in all directions, so some emitted radiation returns toward the surface.'),
('Natural and enhanced effects','Which change most directly describes an enhanced greenhouse effect?', ['An increase in infrared absorption and emission by greenhouse gases following increased gas concentration.','The complete removal of sunlight by the atmosphere.','A decrease of all molecular energy levels to zero.','A greenhouse effect that exists only where glass buildings are present.'],'More greenhouse gas can alter infrared transfer and the radiative balance. The mechanism already exists naturally.'),
('A temperature response','A planet initially has balanced incoming and outgoing energy. Outgoing power is then temporarily reduced at unchanged surface temperature. What happens initially?', ['Its stored energy increases and its temperature tends to rise.','Its stored energy decreases and its temperature falls.','Its temperature must remain fixed because the original state was balanced.','Its mass doubles immediately.'],'Incoming power exceeds outgoing power, giving a positive net energy gain. Warming tends to increase thermal emission.')]
for v,(t,s,o,r) in enumerate(green):add(7,2,v,'multiple-choice',t,s,opts=o,reasoning=r)

for v in range(4):
    incident=[300,400,500,600][v];a=[.2,.3,.4,.25][v];scattered=incident*a
    if v<2:
        stem=f'A surface receives {incident} W of radiation and scatters {f(scattered)} W. What is its albedo?';good=a;bad=[1-a,1/a,a*100];unit='';why=f'Albedo = scattered power / incident power = {f(scattered)}/{incident} = {f(a)}.'
    else:
        T=[0,0,350,420][v];e=[0,0,.65,.8][v];flux=e*SIGMA*T**4
        stem=f'A surface at {T} K emits {f(flux,5)} W m⁻². Using σ = 5.67 × 10⁻⁸ W m⁻² K⁻⁴, what is its emissivity?';good=e;bad=[1/e,e/4,e**4];unit='';why=f'Emissivity = emitted flux/(σT⁴) = {f(e)}. It compares the surface with a blackbody at the same temperature.'
    add(8,2,v,'multiple-choice','Radiative surface properties',stem,opts=numeric(good,bad,unit),reasoning=why)

for v in range(4):
    if v==0:stem='A simple airless-planet model has equilibrium temperature T. The solar constant doubles while albedo and emissivity stay fixed. What is the new temperature divided by T?';g=2**.25;bad=[2,2**.5,.5];why='Balance gives T⁴ proportional to the solar constant. The ratio is 2^(1/4).'
    elif v==1:stem='In an airless-planet model, albedo rises from 0.20 to 0.60. Incoming solar constant and emissivity stay fixed. What is new equilibrium temperature / old equilibrium temperature?';g=(.4/.8)**.25;bad=[.5,2**.25,.75];why='Absorbed power is proportional to 1 − albedo. Its ratio is 0.40/0.80, so the temperature ratio is (0.5)^(1/4).'
    elif v==2:stem='In an airless-planet model, emissivity changes from 0.80 to 0.50. Absorbed solar power stays fixed. What is new equilibrium temperature / old equilibrium temperature?';g=(.8/.5)**.25;bad=[.5/.8,.8/.5,(.5/.8)**.25];why='At the same absorbed power, emissivity × T⁴ is fixed. The temperature ratio is (0.80/0.50)^(1/4).'
    else:stem='Two airless planets have identical albedo and emissivity and orbit the same star. Planet Y is three times as far from the star as planet X. What is T_Y/T_X at radiative equilibrium?';g=1/math.sqrt(3);bad=[1/3,1/9,math.sqrt(3)];why='Solar flux decreases as distance squared and T is proportional to flux^(1/4); therefore T is proportional to distance^(−1/2).'
    add(9,2,v,'multiple-choice','Equilibrium-temperature scaling',stem,opts=numeric(g,bad),reasoning=why)

for v in range(4):
    S=1200+160*v;a=.2+.05*v;incoming=S/4;absorbed=incoming*(1-a);down=absorbed;surface=absorbed+down;T=(surface/SIGMA)**.25
    add(10,2,v,'structured','A one-layer atmosphere',f'A spherical planet receives a solar constant of {S} W m⁻² and has albedo {f(a)}. In a simplified steady model, the atmosphere transmits all unreflected solar radiation, absorbs all upward surface infrared radiation, and emits the same infrared flux upward and downward. The surface and atmospheric layer emit as blackbodies. Use σ = 5.67 × 10⁻⁸ W m⁻² K⁻⁴.',parts=[p('Calculate the mean absorbed solar flux over the whole planet.',step('Average the intercepted sunlight over the full sphere: F_abs = (1 − a)S/4.','M1'),step(f'F_abs = {f(absorbed)} W m⁻².')),p('Determine the upward surface infrared flux by balancing the whole planet and then the surface.',step(f'Top-of-atmosphere balance requires upward atmospheric emission {f(absorbed)} W m⁻², so downward emission is the same.','R1'),step(f'Surface balance gives F_surface = F_abs + F_down = {f(surface)} W m⁻².')),p('Calculate the surface temperature and identify one limitation of the model.',step(f'T = (F_surface/σ)^(1/4) = {f(T)} K.'),step('A valid limitation is the assumption of complete infrared absorption, no atmospheric solar absorption, a single uniform temperature/layer, or omission of nonradiative heat transfer.','R1'))],diagram=budget('S/4','aS/4','?','?'),worked=budget(f(incoming),f(incoming*a),f(down),f(surface)),summary=f'{f(absorbed)} W m⁻² absorbed; {f(T)} K')

for v in range(4):
    S=1000+200*v;a=.15+.05*v;e=.9-.05*v;T=((1-a)*S/(4*e*SIGMA))**.25;delta=.04+.01*v;a2=a+delta;T2=((1-a2)*S/(4*e*SIGMA))**.25
    add(11,2,v,'structured','Albedo change in a radiative model',f'An airless spherical body has solar constant {S} W m⁻², albedo {f(a)} and emissivity {f(e)}. Use σ = 5.67 × 10⁻⁸ W m⁻² K⁻⁴. Assume its surface has one uniform temperature.',parts=[p('Derive an expression for its equilibrium temperature.',step('Set absorbed power (1 − a)Sπr² equal to emitted power eσT⁴(4πr²).','M1'),step('Cancel πr² and rearrange: T = [(1 − a)S/(4eσ)]^(1/4).')),p(f'Calculate the original temperature and the new temperature if albedo rises to {f(a2)} with everything else fixed.',step(f'T_original = {f(T)} K; T_new = {f(T2)} K.')),p('Explain why using a single global temperature can be a limitation even if total incoming power is known.',step('Real surfaces can have day/night and latitude temperature differences.','R1'),step('Emission depends on the fourth power of local temperature, so emission computed at an average temperature need not equal the actual average emission.','R1'))],summary=f'{f(T)} K → {f(T2)} K')

for v in range(4):
    S=1200+80*v;a=.22+.04*v;inc=S/4;ref=inc*a;em=inc-ref;unc=3+v;T=(em/SIGMA)**.25
    add(12,2,v,'data-based','Auditing a satellite radiation budget',f'A simulated satellite dataset gives global mean fluxes for a planet: incoming solar {f(inc)} ± {unc} W m⁻², reflected solar {f(ref)} ± {unc} W m⁻², and outgoing thermal {f(em)} ± {unc} W m⁻². Each quoted uncertainty is an absolute maximum uncertainty. Treat the mean budget as steady.',parts=[p('Calculate the planetary albedo.',step(f'a = reflected/incoming = {f(ref)}/{f(inc)} = {f(a)}.')),p('Calculate the net retained flux and its maximum absolute uncertainty.',step(f'F_net = incoming − reflected − outgoing = {f(inc-ref-em)} W m⁻².','M1'),step(f'For this sum/difference, add absolute uncertainties: ΔF_net = {3*unc} W m⁻².')),p('Determine the effective blackbody temperature corresponding to the outgoing thermal flux, using σ = 5.67 × 10⁻⁸ W m⁻² K⁻⁴.',step(f'T_eff = (F_out/σ)^(1/4) = {f(T)} K.')),p(f'A proposed model predicts a retained flux of {2*unc} W m⁻². Is it distinguishable from zero using these quoted uncertainty bounds?',step(f'No. {2*unc} W m⁻² lies inside the measurement interval ±{3*unc} W m⁻², so these measurements do not resolve the proposed imbalance.','R1'))],diagram=budget(f(inc),f(ref),'atmosphere',f(em)),summary=f'Albedo {f(a)}; net 0 ± {3*unc} W m⁻²')

# B.3 -- gas states and microscopic models.
gasconcept=[
('Pressure and collisions','In a rigid sealed container, an ideal gas is warmed. What most directly explains the rise in pressure?', ['Particles transfer more momentum to the walls per unit time.','Every particle becomes more massive.','The container must contain more particles.','The particles stop colliding with one another.'],'Higher temperature increases typical molecular speeds and the momentum-transfer rate to each wall.'),
('Ideal-gas validity','Under which conditions is an ideal-gas model generally more reliable for a real gas?', ['Low density and temperature well above condensation.','High density close to condensation.','All particles held at fixed lattice positions.','Any pressure if the temperature is exactly 0 K.'],'Large separations reduce the importance of molecular volume and intermolecular forces; temperatures above condensation help maintain a dilute gas.'),
('Equal-temperature gases','Samples of helium and neon are at the same kelvin temperature. In the ideal monatomic model, which molecular quantity has the same mean value?', ['Translational kinetic energy.','Speed.','Momentum magnitude.','Mass.'],'Mean translational kinetic energy is 3k_B T/2. Different particle masses imply different typical speeds at the same temperature.'),
('Compression at fixed temperature','A fixed amount of ideal gas is compressed isothermally to half its volume. Which pair correctly describes pressure and mean translational kinetic energy?', ['Pressure doubles; mean kinetic energy is unchanged.','Pressure halves; mean kinetic energy doubles.','Pressure doubles; mean kinetic energy doubles.','Pressure is unchanged; mean kinetic energy halves.'],'PV is constant for fixed amount and temperature, so pressure doubles. Mean molecular kinetic energy depends only on temperature.')]
for v,(t,s,o,r) in enumerate(gasconcept):add(13,3,v,'multiple-choice',t,s,opts=o,reasoning=r)

for v in range(4):
    n=.2+.1*v;temp=280+20*v;vol=.004+.001*v;pressure=n*R*temp/vol
    if v==0:s=f'A sample of {n} mol ideal gas occupies {vol} m³ at {temp} K. With R = 8.31 J mol⁻¹ K⁻¹, what is its pressure?';g=pressure;bad=[g/1000,g*vol,g*2];unit='Pa'
    elif v==1:s=f'An ideal gas at {temp} K occupies {vol} m³ and has pressure {f(pressure,6)} Pa. With R = 8.31 J mol⁻¹ K⁻¹, how many moles are present?';g=n;bad=[n*1000,n*temp,n/2];unit='mol'
    elif v==2:s=f'A {n} mol sample of ideal gas has pressure {f(pressure,6)} Pa and volume {vol} m³. With R = 8.31 J mol⁻¹ K⁻¹, what is its temperature?';g=temp;bad=[temp-273,temp/2,temp*2];unit='K'
    else:s=f'A {n} mol ideal gas at {temp} K has pressure {f(pressure,6)} Pa. With R = 8.31 J mol⁻¹ K⁻¹, what volume does it occupy?';g=vol;bad=[vol*1000,vol/2,vol*temp];unit='m³'
    add(14,3,v,'multiple-choice','Solving an ideal-gas state',s,opts=numeric(g,bad,unit),reasoning=f'Use PV = nRT with SI pressure and volume and kelvin temperature. Rearranging for the requested quantity gives {f(g)} {unit}.')

for v in range(4):
    if v==0:s='An ideal gas is heated from 250 K to 1000 K. What is the ratio of final to initial rms molecular speed?';g=2;bad=[4,.5,16];why='The rms speed is proportional to the square root of kelvin temperature for fixed molecular mass: sqrt(1000/250) = 2.';unit=''
    elif v==1:s='At the same temperature, gas X has particles with four times the mass of particles of gas Y. What is v_rms,X / v_rms,Y?';g=.5;bad=[4,2,.25];why='Equal temperature means equal mean translational kinetic energy. Thus rms speed is inversely proportional to the square root of particle mass.';unit=''
    elif v==2:temp=420;s=f'What is the mean translational kinetic energy of an ideal-gas particle at {temp} K? Use k_B = 1.38 × 10⁻²³ J K⁻¹.';g=1.5*KB*temp;bad=[KB*temp,.5*KB*temp,3*KB*temp];why=f'Mean translational kinetic energy = 3k_B T/2 = {f(g)} J.';unit='J'
    else:rho=1.8;speed=450;s=f'An ideal gas has density {rho} kg m⁻³ and rms molecular speed {speed} m s⁻¹. What pressure does the kinetic model predict?';g=rho*speed**2/3;bad=[rho*speed**2,rho*speed/3,g/1000];why=f'P = ρv_rms²/3 = {f(g)} Pa. The mean-square speed, not the square of the mean speed, enters this relation.';unit='Pa'
    add(15,3,v,'multiple-choice','Molecular speed and energy',s,opts=numeric(g,bad,unit),reasoning=why)

for v in range(4):
    p0=1.2e5;v0=.006;t0=300;n=p0*v0/(R*t0)
    if v==0:
        t1=420;p1=p0*t1/t0;v1=v0;condition='heated at fixed volume to 420 K';unknown='final pressure';value=p1;unit='Pa';relation='P/T is constant because n and V are fixed.'
    elif v==1:
        t1=450;p1=p0;v1=v0*t1/t0;condition='heated at constant pressure to 450 K';unknown='final volume';value=v1;unit='m³';relation='V/T is constant because n and P are fixed.'
    elif v==2:
        t1=t0;v1=v0/3;p1=p0*3;condition='compressed isothermally to one third of its initial volume';unknown='final pressure';value=p1;unit='Pa';relation='PV is constant because n and T are fixed.'
    else:
        p1=.8e5;t1=320;v1=v0;n1=p1*v1/(R*t1);condition='left in the same rigid container; the pressure later becomes 8.00 × 10⁴ Pa and temperature becomes 320 K';unknown='fraction of the original gas particles remaining';value=n1/n;unit='';relation='At fixed volume N is proportional to P/T, so N1/N0 = (P1/P0)(T0/T1).'
    add(16,3,v,'structured','A controlled gas-state change',f'An ideal gas initially has pressure 1.20 × 10⁵ Pa, volume 0.00600 m³ and temperature 300 K. It is {condition}. Use R = 8.31 J mol⁻¹ K⁻¹.',parts=[p('Calculate the initial amount of gas.',step('n = PV/(RT).','M1'),step(f'n = {f(n)} mol.')),p(f'Determine the {unknown}.',step(relation,'M1'),step(f'The result is {f(value)} {unit}.')),p('State one assumption needed when applying the ideal-gas equation to these states.',step('Accept negligible intermolecular potential-energy effects/forces except during collisions, negligible molecular volume, or a dilute gas sufficiently far from condensation.','R1'))],summary=f'{unknown}: {f(value)} {unit}')

for v in range(4):
    mass_particle=[6.64e-27,3.32e-26,6.63e-26,1.39e-25][v];T=300+80*v;vol=.003+.001*v;N=(2+v)*1e22;rho=N*mass_particle/vol;vrms=math.sqrt(3*KB*T/mass_particle);pressure=N*KB*T/vol;U=1.5*N*KB*T
    assert math.isclose(pressure,rho*vrms**2/3,rel_tol=1e-12)
    add(17,3,v,'structured','Connecting microscopic and bulk quantities',f'A monatomic ideal gas contains {f(N)} particles in {f(vol)} m³ at {T} K. Each particle has mass {f(mass_particle)} kg. Use k_B = 1.38 × 10⁻²³ J K⁻¹.',parts=[p('Determine the rms molecular speed.',step('Equate ½m v_rms² to 3k_B T/2, giving v_rms = sqrt(3k_B T/m).','M1'),step(f'v_rms = {f(vrms)} m s⁻¹.')),p('Calculate the density and hence the pressure using the kinetic model.',step(f'ρ = Nm/V = {f(rho)} kg m⁻³.'),step(f'P = ρv_rms²/3 = {f(pressure)} Pa.')),p('Determine the total internal energy and explain why the container can be stationary while this energy is nonzero.',step(f'U = 3Nk_B T/2 = {f(U)} J.'),step('The energy belongs to random particle motion; zero centre-of-mass velocity does not mean zero molecular velocities.','R1'))],summary=f'v_rms = {f(vrms)} m s⁻¹; P = {f(pressure)} Pa; U = {f(U)} J')

for v in range(4):
    n=.025+.005*v;T=300+20*v;coeff=n*R*T;vols=[20,25,30,40,50];pressures=[round(coeff/(x*1e-6)/1000,2) for x in vols];prod=[P*V for P,V in zip(pressures,vols)];mean=sum(prod)/len(prod);n_est=mean*.001/(R*T)
    table='\n\n| Volume / cm³ | Absolute pressure / kPa |\n|---:|---:|\n'+'\n'.join(f'| {V} | {P:.2f} |' for V,P in zip(vols,pressures))
    add(18,3,v,'data-based','Testing an isothermal gas model',f'A simulated compression experiment holds a fixed gas sample at {T} K. The readings below use absolute pressure. Use R = 8.31 J mol⁻¹ K⁻¹.'+table,parts=[p('Calculate PV for the smallest and largest volumes and assess the isothermal ideal-gas prediction.',step(f'The endpoint products are {f(prod[0],5)} and {f(prod[-1],5)} kPa cm³.'),step('They agree to the displayed precision, consistent with constant PV for fixed amount and temperature. This supports the model but does not prove it.','R1')),p('Use the mean PV product to estimate the amount of gas.',step('Convert 1 kPa cm³ = 10⁻³ J, then use n = mean(PV)/(RT).','M1'),step(f'n = {f(n_est)} mol.')),p('State what should be plotted to obtain a straight line through the origin and identify its gradient.',step('Plot absolute pressure P against 1/V; the gradient is nRT when SI units are used.','R1')),p('Explain why compressing quickly could invalidate this test.',step('Rapid compression can raise the gas temperature before it exchanges heat with the surroundings, so the fixed-temperature assumption fails.','R1'))],diagram=plot(vols,pressures,'Volume / cm³','Pressure / kPa','Raw simulated pressure-volume data'),worked=plot([1/(x*1e-6) for x in reversed(vols)],list(reversed(pressures)),'1/Volume / m⁻³','Pressure / kPa','Linearized simulated gas data'),summary=f'n ≈ {f(n_est)} mol')

# B.4 -- every item in this subsection is AHL.
for v in range(4):
    cases=[(500,180),(240,-160),(-130,70),(-300,-450)];heat,work=cases[v];du=heat-work
    s=f'A closed system has net heat transfer Q = {heat:+d} J and net work W = {work:+d} J. Q is positive into the system; W is positive when done by the system. What is its change in internal energy?'
    add(19,4,v,'multiple-choice','First-law signs',s,opts=numeric(du,[heat+work,-du,du/2],'J'),reasoning=f'With Q = ΔU + W, ΔU = Q − W = {heat} − ({work}) = {du:+d} J.',level='ahl')

entropy_cases=[
('Entropy in an isolated system','Which process can occur in an isolated system according to the second law?', ['A spontaneous process with a positive total entropy change.','A spontaneous process with a negative total entropy change.','A refrigerator lowering total entropy without any other change.','Heat flowing spontaneously from cold to hot with no compensating effect.'],'An irreversible spontaneous process increases the entropy of an isolated system; the reversible limit has zero change.'),
('Local entropy decrease','A refrigerator lowers the entropy of its contents. Which condition is required for consistency with the second law?', ['The entropy increase of the surroundings is at least as large.','The surroundings must also lose entropy.','The work input must be zero.','The contents must be an isolated system.'],'The contents are not isolated. Their entropy reduction is compensated by heat rejection and work-related dissipation in the surroundings.'),
('Reversible cycle','An ideal reversible engine completes one cycle. What is the change in the entropy of its working gas?', ['Zero.','Positive because it did useful work.','Negative because it rejected heat.','Equal to its net work divided by its maximum temperature.'],'Entropy is a state function. At the end of a complete cycle the gas returns to its initial state, so its entropy change is zero.'),
('Unequal-temperature reservoirs','A small energy Q flows from a reservoir at T_h to one at T_c, where T_h > T_c. Which expression gives the total entropy change?', ['Q/T_c − Q/T_h.','Q/T_h − Q/T_c.','Q(T_h − T_c).','Zero for every pair of temperatures.'],'The cold reservoir gains Q/T_c and the hot reservoir loses Q/T_h. The total is positive because T_c is smaller.')]
for v,(t,s,o,r) in enumerate(entropy_cases):add(20,4,v,'multiple-choice',t,s,opts=o,reasoning=r,level='ahl')

for v in range(4):
    loP=80+20*v;hiP=200+30*v;loV=1+v;hiV=loV+3+v;clockwise=(v%2==0)
    points=[(loV,loP),(loV,hiP),(hiV,hiP),(hiV,loP)]
    if not clockwise:points=list(reversed(points))
    work=(hiP-loP)*(hiV-loV)*(1 if clockwise else -1)
    add(21,4,v,'structured','A directional gas cycle',f'A fixed amount of gas follows the rectangular cycle shown, returning to its initial state. The arrows give the direction. The pressure limits are {loP} kPa and {hiP} kPa; the volume limits are {loV} × 10⁻³ m³ and {hiV} × 10⁻³ m³. Use the convention that work done by the gas is positive.',parts=[p('Calculate the net work done by the gas in one cycle.',step('The magnitude is the enclosed area: (P_high − P_low)(V_high − V_low).','M1'),step(f'The cycle is {"clockwise" if clockwise else "anticlockwise"}, so W = {work:+d} J. The kPa × 10⁻³ m³ factors give joules.')),p('Determine the net heat transferred into the gas per cycle.',step('The gas returns to the same state, so ΔU_cycle = 0.','R1'),step(f'Q_net = ΔU + W = {work:+d} J.')),p('Explain whether the cycle produces net mechanical work or requires net mechanical input.',step('It produces net mechanical work because W is positive.' if clockwise else 'It requires net mechanical input because W is negative.','R1'))],level='ahl',diagram=pv_cycle(points,'ABCD'),worked=pv_cycle(points,'ABCD'),summary=f'W_net = Q_net = {work:+d} J')

for v in range(4):
    n=.2+.1*v;T0=420+60*v;V0=.005;ratio=[2,3,.5,.4][v];V1=V0*ratio;P0=n*R*T0/V0;P1=P0*ratio**(-5/3);T1=T0*ratio**(-2/3);du=1.5*n*R*(T1-T0);work=-du
    assert math.isclose(P0*V0**(5/3),P1*V1**(5/3),rel_tol=1e-12)
    add(22,4,v,'structured','A monatomic adiabatic change',f'A fixed {f(n)} mol sample of monatomic ideal gas initially has temperature {T0} K and volume 0.00500 m³. It changes adiabatically to volume {f(V1)} m³. Take R = 8.31 J mol⁻¹ K⁻¹ and PV^(5/3) = constant.',parts=[p('Determine the final temperature.',step('Combine PV^(5/3) = constant with PV = nRT to obtain TV^(2/3) = constant.','M1'),step(f'T_f = {T0}(V_i/V_f)^(2/3) = {f(T1)} K.')),p('Calculate the change in internal energy and work done by the gas.',step(f'ΔU = 3nR(T_f − T_i)/2 = {f(du)} J.'),step(f'Q = 0, so W = −ΔU = {f(work)} J.')),p('Explain the sign of the temperature change using energy transfer.',step('During expansion the gas does work with no heat input, reducing its internal energy and temperature.' if ratio>1 else 'During compression work is done on the gas with no heat leaving, increasing its internal energy and temperature.','R1'))],level='ahl',summary=f'T_f = {f(T1)} K; W = {f(work)} J')

for v in range(4):
    Th=[600,750,900,1000][v];Tc=[300,330,360,400][v];inputP=(4+v)*1e4;eta=.24+.03*v;output=inputP*eta;limit=1-Tc/Th;waste=inputP-output;dS=waste/Tc-inputP/Th
    assert eta<limit and dS>0
    add(23,4,v,'structured','Testing an engine claim',f'A steady heat engine absorbs {f(inputP)} W from a reservoir at {Th} K and produces useful mechanical power {f(output)} W. It rejects its remaining heat to a reservoir at {Tc} K.',parts=[p('Calculate its actual efficiency and the Carnot efficiency for these reservoirs.',step(f'η_actual = P_useful/P_in = {f(eta)} ({f(100*eta)}%).'),step(f'η_Carnot = 1 − T_c/T_h = {f(limit)} ({f(100*limit)}%).')),p('Calculate the heat-rejection rate.',step(f'P_rejected = P_in − P_useful = {f(waste)} W.')),p('Calculate the total entropy increase of the reservoirs each second and use it to assess whether the stated engine violates the second law.',step(f'Entropy rate = P_rejected/T_c − P_in/T_h = {f(dS)} J K⁻¹ s⁻¹.','M1'),step('The total entropy rate is positive and the efficiency is below the reversible limit, so these figures do not violate the second law.','R1'))],level='ahl',summary=f'η = {f(100*eta)}%; heat rejection {f(waste)} W')

for v in range(4):
    energies=[120,180,240,300];heat=energies[v];Th=400+40*v;Tc=280+20*v;dSh=-heat/Th;dSc=heat/Tc;total=dSh+dSc;omegai=[4,6,8,10][v];omegaf=omegai*(v+2);micro=KB*math.log(omegaf/omegai)
    add(24,4,v,'data-based','Two descriptions of entropy',f'Two ideal thermal reservoirs exchange {heat} J. Their fixed temperatures are {Th} K and {Tc} K. Separately, a simple model has {omegai} accessible equally probable microstates before a constraint is removed and {omegaf} afterward. Use k_B = 1.38 × 10⁻²³ J K⁻¹.',parts=[p('For heat flowing from the hotter reservoir to the colder one, calculate the entropy change of each reservoir and the combined change.',step(f'ΔS_hot = −Q/T_h = {f(dSh)} J K⁻¹; ΔS_cold = Q/T_c = {f(dSc)} J K⁻¹.','M1'),step(f'ΔS_total = {f(total)} J K⁻¹.')),p('Explain why reversing this transfer without another change is not spontaneous.',step('Reversal would make the combined entropy change negative, contradicting the second law for the isolated pair.','R1')),p('Calculate the entropy change of the microstate model.',step('ΔS = k_B ln Ω_f − k_B ln Ω_i = k_B ln(Ω_f/Ω_i).','M1'),step(f'ΔS = {f(micro)} J K⁻¹.')),p('Explain why a macrostate with more equally probable microstates is more likely.',step('There are more distinct microscopic arrangements corresponding to that macrostate, so its total probability is larger.','R1'))],level='ahl',summary=f'Reservoir total {f(total)} J K⁻¹; microstate change {f(micro)} J K⁻¹')

# B.5 -- networks, sources, sensing and measurement.
for v in range(4):
    rr=[6,8,12,18][v]
    if v==0:s=f'Two resistors of {rr} Ω each are in series. This pair is connected in parallel with one {rr} Ω resistor. What is the equivalent resistance?';g=2*rr/3;bad=[3*rr,rr/3,1.5*rr];why='The series branch is 2R. Its parallel combination with R gives (2R × R)/(2R + R) = 2R/3.'
    elif v==1:s=f'Two {rr} Ω resistors are in parallel. A third {rr} Ω resistor is in series with that combination. What is the equivalent resistance?';g=1.5*rr;bad=[rr/3,3*rr,2*rr/3];why='The parallel pair gives R/2; adding the series resistor gives 3R/2.'
    elif v==2:s=f'Three identical {rr} Ω resistors are connected in parallel. What is their equivalent resistance?';g=rr/3;bad=[3*rr,rr/2,rr];why='Conductances add: 1/R_eq = 3/R, so R_eq = R/3.'
    else:s=f'A network has two parallel branches. One branch contains a {rr} Ω resistor; the other contains two {rr} Ω resistors in series. A further {rr} Ω resistor is in series with the whole network. What is the equivalent resistance?';g=5*rr/3;bad=[4*rr,rr/4,2*rr/3];why='The parallel block is 2R/3 and the external series resistor adds R, giving 5R/3.'
    add(25,5,v,'multiple-choice','Identifying series and parallel structure',s,opts=numeric(g,bad,'Ω'),reasoning=why)

circuitconcept=[
('A hot filament','A filament lamp becomes hotter as its potential difference increases. Its current rises less than proportionally to potential difference. What happens to its resistance?', ['It increases.','It decreases.','It remains constant.','It becomes zero.'],'R = V/I. If V increases by a larger factor than I, this ratio increases; increased temperature increases the filament resistivity.'),
('A negative-temperature-coefficient sensor','An NTC thermistor is warmed. Which change is expected?', ['Its resistance decreases.','Its resistance necessarily doubles.','It becomes an ideal voltage source.','Its resistance cannot depend on temperature.'],'NTC means negative temperature coefficient: increasing temperature decreases resistance over its operating range.'),
('An illuminated sensor','The illumination on an LDR increases while its potential difference stays fixed. What is normally expected?', ['Resistance falls and current increases.','Resistance rises and current increases.','Resistance falls and current decreases.','Both resistance and current remain fixed.'],'Greater illumination lowers LDR resistance; at fixed voltage I = V/R therefore increases.'),
('Finite voltmeter resistance','A voltmeter with finite resistance is connected across one resistor in a two-resistor divider supplied by an ideal cell. Compared with an ideal voltmeter, what does it do to the measured resistor combination?', ['It provides a parallel path and lowers that branch resistance.','It adds its resistance in series with the cell.','It guarantees zero current through the divider.','It increases that branch resistance to infinity.'],'The finite meter is in parallel with the resistor, so their combined resistance is smaller. This loading can alter the measured potential difference.')]
for v,(t,s,o,r) in enumerate(circuitconcept):add(26,5,v,'multiple-choice',t,s,opts=o,reasoning=r)

for v in range(4):
    emf=6+2*v;r=.4+.2*v;load=3+v;current=emf/(load+r);terminal=current*load;internal=current**2*r;eff=load/(load+r)
    add(27,5,v,'structured','A source under load',f'A cell has emf {emf} V and constant internal resistance {f(r)} Ω. It supplies a single external resistor of {load} Ω. Connecting wires have negligible resistance.',parts=[p('Calculate the circuit current and the terminal potential difference.',step('I = ε/(R + r).','M1'),step(f'I = {f(current)} A; terminal V = IR = {f(terminal)} V.')),p('Calculate the power transferred inside the cell and the fraction of its electrical power delivered to the external resistor.',step(f'P_internal = I²r = {f(internal)} W.'),step(f'Fraction = I²R/(εI) = R/(R+r) = {f(eff)}.')),p('Explain why terminal voltage rises when the external resistance is increased.',step('Larger external resistance reduces the current, so the internal drop Ir decreases and V = ε − Ir rises.','R1'))],summary=f'I = {f(current)} A; terminal V = {f(terminal)} V')

for v in range(4):
    supply=6+2*v;fixed=2000+1000*v;sensor=6000-1000*v;below=v%2==0;top=fixed if below else sensor;bottom=sensor if below else fixed;out=supply*bottom/(top+bottom);sensor2=sensor/2;out2=supply*(sensor2 if below else fixed)/(fixed+sensor2)
    add(28,5,v,'structured','A sensor-divider threshold',f'An ideal {supply} V supply feeds a series combination of a {fixed} Ω fixed resistor and an LDR. The LDR initially has resistance {sensor} Ω. The output is measured from the midpoint to the lower node by an ideal voltmeter. The diagram shows which resistor is above the midpoint.',parts=[p('Calculate the initial output potential difference.',step('For the lower resistor, V_out = εR_lower/(R_upper + R_lower).','M1'),step(f'V_out = {f(out)} V.')),p('Brighter light halves the LDR resistance. Calculate the new output potential difference.',step(f'Use R_LDR,new = {f(sensor2)} Ω in the divider expression.','M1'),step(f'V_out,new = {f(out2)} V.')),p('Explain the direction of the output change in terms of the resistance ratio.',step('The LDR is below the midpoint. Reducing its resistance reduces its fraction of total resistance, so output falls.' if below else 'The fixed resistor is below the midpoint. Reducing the upper LDR resistance increases the lower resistor’s fraction of total resistance, so output rises.','R1'))],diagram=circuit(f'{top} Ω'+(' LDR' if not below else ''),f'{bottom} Ω'+(' LDR' if below else ''),f'{supply} V'),worked=circuit(f'{top} Ω',f'{bottom} Ω',f'{supply} V',True),summary=f'{f(out)} V → {f(out2)} V')

for v in range(4):
    length=1.5+.5*v;diam=(.3+.1*v)*1e-3;rho=1.1e-6;area=math.pi*(diam/2)**2;res=rho*length/area;voltage=3+v;cur=voltage/res;seconds=60+30*v;charge=cur*seconds;energy=voltage*charge
    add(29,5,v,'structured','A resistive heating wire',f'A uniform wire has length {f(length)} m, diameter {f(diam*1000)} mm and resistivity 1.10 × 10⁻⁶ Ω m. Its temperature is maintained constant so its resistivity does not change. An ideal {voltage} V supply is connected across it for {seconds} s.',parts=[p('Calculate the wire resistance.',step('Use cross-sectional area A = π(d/2)² and R = ρL/A; convert diameter to metres.','M1'),step(f'A = {f(area)} m² and R = {f(res)} Ω.')),p('Calculate the total charge passing a cross-section and the electrical energy transferred.',step(f'I = V/R = {f(cur)} A; q = It = {f(charge)} C.'),step(f'E = Vq = {f(energy)} J.')),p('The same material and length are used with twice the diameter. State the factor change in power for the same ideal voltage supply.',step('Area increases by four and resistance falls to one quarter. Since P = V²/R at fixed voltage, power increases by a factor of four.','R1'))],summary=f'R = {f(res)} Ω; charge {f(charge)} C; energy {f(energy)} J')

for v in range(4):
    slope=3+v;offset=.2+.1*v;Ls=[.2,.4,.6,.8,1.0];Rs=[slope*x+offset for x in Ls];d=.4e-3+.05e-3*v;area=math.pi*d*d/4;rho=slope*area;uncd=.01e-3;frac=2*uncd/d
    kind='data-based' if v<2 else 'structured'
    table='\n\n| Wire length / m | Measured resistance / Ω |\n|---:|---:|\n'+'\n'.join(f'| {L:.2f} | {rval:.2f} |' for L,rval in zip(Ls,Rs))
    add(30,5,v,kind,'Separating wire and contact resistance',f'A simulated investigation uses uniform wire of measured diameter {f(d*1000)} ± 0.010 mm. The measured resistance includes the wire and an approximately constant contact resistance. The model is R_measured = (ρ/A)L + R_contact.'+table,parts=[p('Determine the gradient and intercept of resistance against length, with units.',step(f'Gradient = ΔR/ΔL = {f(slope)} Ω m⁻¹.'),step(f'Intercept = {f(offset)} Ω, interpreted as contact resistance.')),p('Calculate the wire resistivity.',step('ρ = gradient × A, with A = πd²/4.','M1'),step(f'ρ = {f(rho)} Ω m.')),p('Ignoring uncertainty in the gradient, estimate the percentage uncertainty in the resistivity due to the diameter measurement.',step(f'Because ρ is proportional to d², percentage uncertainty = 2Δd/d × 100 = {f(frac*100)}%.')),p('Explain why calculating R_measured A/L separately for each length produces a length-dependent apparent resistivity.',step('The contact resistance contributes an extra term R_contact A/L. Its effect is larger at short lengths, so that calculation cannot isolate the material resistivity.','R1'))],diagram=plot(Ls,Rs,'Wire length / m','Measured resistance / Ω','Simulated wire resistance measurements'),worked=plot([0,1],[offset,slope+offset],'Wire length / m','Measured resistance / Ω','Extrapolated intercept represents contact resistance'),summary=f'ρ = {f(rho)} Ω m; diameter contribution {f(frac*100)}%')

def validate():
    # A global satellite budget is not the same diagram as a one-layer surface budget.
    for q,family in zip(Q,FAMILIES):
        if family==12:q.pop('diagramSvg',None)
    assert len(Q)==120
    assert Counter(FAMILIES)=={i:4 for i in range(1,31)}
    assert Counter(x['questionType'] for x in Q)=={'multiple-choice':48,'structured':54,'data-based':18}
    assert Counter(x['syllabusCode'] for x in Q)=={f'B.{i}':24 for i in range(1,6)}
    assert len({q['stem'] for q in Q})==120
    for n,q in enumerate(Q,1):
        assert q['number']==n and q['id']==f'ib-phy-b-{n:03}'
        assert q['marks']==sum(int(s['code'][1:]) for g in q['markScheme'] for s in g['steps'])
        if q['parts']:
            assert q['marks']==sum(x['marks'] for x in q['parts'])
            for part,scheme in zip(q['parts'],q['markScheme']):assert part['marks']==sum(int(s['code'][1:]) for s in scheme['steps'])
        if q['syllabusCode']=='B.4':assert q['level']=='ahl'
        else:assert q['level']=='core'
        for key in ['diagramSvg','markSchemeDiagramSvg']:
            if key in q:
                s=q[key];assert s.startswith('<svg ') and 'viewBox=' in s and s.endswith('</svg>')
                assert not re.search(r'<(?:script|image|style|foreignObject)|\bon\w+\s*=|(?:href|src)\s*=|url\s*\(',s,re.I)
        assert q['stem'].count('$')%2==0
    assert sum('diagramSvg'in q for q in Q)>=20 and sum('markSchemeDiagramSvg'in q for q in Q)>=10

if __name__=='__main__':
    validate();OUT.parent.mkdir(parents=True,exist_ok=True);REPORT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(Q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report=['Theme B independent authoring report','120 question sets; 30 editorial families with four physical variants each.','Coverage: 24 questions per B.1–B.5. B.4 exclusively AHL.','Types: '+str(dict(Counter(q['questionType']for q in Q))),'Difficulty: '+str(dict(Counter(q['difficulty']for q in Q))),f"Question diagrams: {sum('diagramSvg'in q for q in Q)}; worked diagrams: {sum('markSchemeDiagramSvg'in q for q in Q)}.",'Numerical checks: heat-energy accounting; molecular pressure identity; adiabatic invariant; engine efficiency/entropy consistency; all values recomputed from declared constants.','Structural checks: IDs, numbering, stems, type distribution, syllabus coverage, uniqueness of displayed MCQ choices, per-part and total mark sums, SVG safety.','Data are explicitly simulated. Data-table rounding is used when deriving expected numerical results.','Source used for scope only: corrected Physics guide (November 2024), https://xmltwo.ibo.org/publications/EAD/2026_EN/GR4/GR4-Physics_EN.pdf . No source question wording, numbers or artwork adapted.','Independent physics/editorial cross-review completed; see particulate-matter-cross-review.txt. Complete rendered diagram review is recorded in diagram-visual-bc.txt; live application integration review is separate.']
    REPORT.write_text('\n'.join(report)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(OUT),'count':len(Q),'types':dict(Counter(q['questionType']for q in Q)),'diagrams':sum('diagramSvg'in q for q in Q),'workedDiagrams':sum('markSchemeDiagramSvg'in q for q in Q)},indent=2))
