"""Deterministic, independent Theme C authoring. Standard library only; no source exam items."""
import json
import math
import re
from collections import Counter
from html import escape
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'content/ib/physics-hl/wave-behaviour.json'
REPORT=ROOT/'docs/ib-physics-reviews/wave-behaviour.txt'
Q=[]
FAMILIES=[]
C=3.00e8

def f(x,sig=3):return format(x,f'.{sig}g')
def p(prompt,*steps):return prompt,list(steps)
def step(text,code='A1'):return code,text
def format_literal_subscripts(value):
    """Format only literal underscore identifiers outside existing dollar math."""
    greek={'Δ':r'\Delta ','θ':r'\theta ','λ':r'\lambda ','ρ':r'\rho ','η':r'\eta ','ε':r'\varepsilon ','Ω':r'\Omega '}
    identifier=re.compile(r'([A-Za-z0-9ΔθλρηεΩ]+)_([A-Za-z0-9]+(?:[-,][A-Za-z0-9]+)?)')
    def replacement(match):
        base=''.join(greek.get(char,char) for char in match[1]).rstrip()
        suffix=match[2]
        sub=suffix if suffix.isdigit() else (r'\text{'+suffix+'}' if '-' in suffix else r'\mathrm{'+suffix+'}')
        return '$'+base+'_{'+sub+'}$'
    return ''.join(piece if piece.startswith('$') else identifier.sub(replacement,piece)
                   for piece in re.split(r'(\$\$[\s\S]*?\$\$|\$(?:\\.|[^$\n])+\$)',value))

def numeric(good,bad,unit=''):
    vals=[good]+list(bad);assert len(vals)==4 and all(math.isfinite(x)for x in vals)
    labels=[f(x)+(' '+unit if unit else '')for x in vals];assert len(set(labels))==4,labels
    return labels
def text(x,y,s,size=17,color='#172b4d',anchor='middle'):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Arial, sans-serif" font-size="{size}" fill="{color}">{escape(str(s))}</text>'
def line(x1,y1,x2,y2,color='#172b4d',width=2):return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>'
def arrow(x1,y1,x2,y2,label='',color='#1b6ca8'):
    a=math.atan2(y2-y1,x2-x1);u=(x2-10*math.cos(a-.45),y2-10*math.sin(a-.45));v=(x2-10*math.cos(a+.45),y2-10*math.sin(a+.45))
    s=line(x1,y1,x2,y2,color,3)+f'<polyline points="{u[0]},{u[1]} {x2},{y2} {v[0]},{v[1]}" fill="none" stroke="{color}" stroke-width="3"/>'
    return s+(text((x1+x2)/2,(y1+y2)/2-12,label,15,color)if label else '')
def svg(body,caption='',w=640,h=340):return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img"><title>{escape(caption)}</title><rect width="{w}" height="{h}" fill="white"/>{body}</svg>'
def axis_limits(values):
    lo=min(0,min(values));hi=max(0,max(values));span=hi-lo or 1
    unit=10**math.floor(math.log10(span/4))
    increment=next(x for x in (1,2,2.5,5,10) if x*unit>=span/4-1e-12*span)*unit
    lower=math.floor(lo/increment+1e-10)*increment
    upper=math.ceil(hi/increment-1e-10)*increment
    if lower==upper:upper=lower+increment
    ticks=[lower+j*increment for j in range(round((upper-lower)/increment)+1)]
    return lower,upper,ticks

def plot(xs,ys,xlab,ylab,caption='',labels=False,extra=None):
    assert len(xs)==len(ys) and len(xs)>1
    xmin,xmax,xticks=axis_limits(xs)
    ymin,ymax,yticks=axis_limits(ys)
    xy=lambda x,y:(90+(x-xmin)/(xmax-xmin)*480,275-(y-ymin)/(ymax-ymin)*215)
    xzero,yzero=xy(0,0);b=arrow(90,275,590,275)+arrow(90,275,90,38)
    if ymin<0<ymax:b+=line(90,yzero,570,yzero,'#b6c1cf',1)
    if xmin<0<xmax:b+=line(xzero,60,xzero,275,'#b6c1cf',1)
    b+=text(330,325,xlab,16)+text(90,25,ylab,16,anchor='start')
    for x in xticks:
        px,_=xy(x,0);b+=line(px,275,px,280)+text(px,299,f(x),11)
    for y in yticks:
        _,py=xy(0,y);b+=line(85,py,90,py)+text(75,py+4,f(y),11,anchor='end')
    for x,y in zip(xs,ys):
        px,py=xy(x,y)
        if len(xs)<=12:b+=f'<circle cx="{px}" cy="{py}" r="3.5" fill="#1b6ca8"/>'
        if labels:b+=text(px,py-12,f'({f(x)}, {f(y)})',12)
    b+='<polyline points="'+' '.join(f'{xy(x,y)[0]},{xy(x,y)[1]}'for x,y in zip(xs,ys))+'" fill="none" stroke="#1b6ca8" stroke-width="2"/>'
    if extra:
        ex,ey=extra;b+='<polyline points="'+' '.join(f'{xy(x,y)[0]},{xy(x,y)[1]}'for x,y in zip(ex,ey))+'" fill="none" stroke="#c15f20" stroke-width="2" stroke-dasharray="6 4"/>'
        for x,y in zip(ex,ey):
            px,py=xy(x,y);b+=f'<circle cx="{px}" cy="{py}" r="3" fill="#c15f20"/>'
        b+=line(415,30,440,30,'#1b6ca8',2)+text(451,35,'X',13)
        b+='<line x1="495" y1="30" x2="525" y2="30" stroke="#c15f20" stroke-width="2" stroke-dasharray="6 4"/>'+text(539,35,'Y',13)
    return svg(b,caption)
def wave(A,lam,phase=0,direction='right',annotate=False):
    xmap=lambda x:75+x/(2*lam)*500
    ymap=lambda y:170-y/A*85
    b=line(75,170,575,170,'#b6c1cf',1)+arrow(75,285,595,285)+arrow(75,285,75,50)+text(350,332,'Position / m')+text(80,28,'Displacement / m',16,anchor='start')
    pts=[(2*lam*j/160,A*math.sin(2*math.pi*(2*lam*j/160)/lam+phase))for j in range(161)]
    b+='<polyline points="'+' '.join(f'{xmap(x)},{ymap(y)}'for x,y in pts)+'" fill="none" stroke="#1b6ca8" stroke-width="3"/>'
    for j in range(5):b+=line(xmap(j*lam/2),285,xmap(j*lam/2),290)+text(xmap(j*lam/2),308,f(j*lam/2),13)
    for value in [-A,0,A]:b+=line(70,ymap(value),75,ymap(value))+text(62,ymap(value)+5,f(value),13,anchor='end')
    b+=arrow(440 if direction=='right'else 565,55,565 if direction=='right'else 440,55,'wave travel')
    xp=lam/8;yp=A*math.sin(math.pi/4+phase);slope=math.cos(math.pi/4+phase);sign=-1 if direction=='right'else 1;down=(sign*slope)<0
    px=xmap(xp);py=ymap(yp);b+=f'<circle cx="{px}" cy="{py}" r="5" fill="#b65124"/>'+text(px-16,py-12,'P',13,'#b65124')
    if annotate:b+=arrow(px,py,px,py+(45 if down else -45),'','#b65124')+text(200,55,'particle motion',13,'#b65124')
    return svg(b,'Sinusoidal travelling-wave snapshot; axes show physical values')
def standing(L,harmonic,boundary='fixed-fixed',worked=False,end_labels=None):
    b=line(80,170,570,170,'#909aaa',1)+text(325,318,f'Length = {f(L)} m; displacement pattern',16)
    if boundary=='fixed-fixed':fn=lambda u:math.sin(harmonic*math.pi*u);ends=('fixed','fixed')
    elif boundary=='free-free':fn=lambda u:math.cos(harmonic*math.pi*u);ends=('free','free')
    else:fn=lambda u:math.sin(harmonic*math.pi*u/2);ends=('fixed','free')
    for sign,color in [(1,'#1b6ca8'),(-1,'#94b4c9')]:
        b+='<polyline points="'+' '.join(f'{80+490*j/180},{170-sign*70*fn(j/180)}'for j in range(181))+'" fill="none" stroke="'+color+'" stroke-width="2"/>'
    if end_labels:ends=end_labels
    for x,name in [(80,ends[0]),(570,ends[1])]:b+=line(x,65,x,275)+text(x,45,name,14)
    b+=text(325,25,f'Harmonic {harmonic}',18)
    if worked:
        for j in range(181):
            if abs(fn(j/180))<1e-9:b+=f'<circle cx="{80+490*j/180}" cy="170" r="4" fill="#b65124"/>'
        b+=text(325,292,'Marked points are displacement nodes',13,'#b65124')
    return svg(b,'Standing-wave displacement at two opposite phases')
def rays(n1,n2,theta1,theta2=None,worked=False):
    b='<rect x="25" y="170" width="590" height="130" fill="#e5f2fa"/>'+line(25,170,615,170)
    b+='<line x1="320" y1="40" x2="320" y2="300" stroke="#8491a3" stroke-width="2" stroke-dasharray="5 5"/>'
    b+=arrow(320-100*math.sin(math.radians(theta1)),170-100*math.cos(math.radians(theta1)),320,170)
    b+=text(80,90,f'n₁ = {f(n1)}',16)+text(80,235,f'n₂ = {f(n2)}',16)+text(360,60,'normal',13)
    b+=text(270,150,f'θ₁ = {f(theta1)}°',14)
    if theta2 is not None:
        b+=arrow(320,170,320+100*math.sin(math.radians(theta2)),170+100*math.cos(math.radians(theta2)))
        b+=text(395,240,(f'θ₂ = {f(theta2)}°'if worked else 'θ₂'),14)
    b+=text(320,325,'Schematic; angles are measured from the normal',13)
    return svg(b,'Refraction at a plane boundary')
def slits(d,D,caption='Two-slit geometry'):
    b=line(180,35,180,125)+line(180,140,180,200)+line(180,215,180,295)+line(555,35,555,295)
    b+=line(180,132,555,170,'#1b6ca8',1)+line(180,207,555,170,'#1b6ca8',1)
    b+=text(120,170,f'd = {d}',15)+text(555,25,'screen',15)+arrow(190,285,545,285,f'D = {D}')
    b+=text(325,325,'Schematic; slit spacing and screen distance not to scale',13)
    return svg(b,caption)
def fronts(approach=True):
    b=''
    for t in [1,2,3]:b+=f'<circle cx="{360-16*t}" cy="170" r="{45*t}" fill="none" stroke="#709db9" stroke-width="2"/>'
    b+='<circle cx="360" cy="170" r="7" fill="#1b6ca8"/>'+line(370,165,480,100,'#8491a3',1)+text(515,90,'source now',14)+arrow(485,45,560,45,'motion')
    ox=565 if approach else 90;b+=f'<circle cx="{ox}" cy="170" r="6" fill="#b65124"/>'+text(ox,200,'observer',14)
    b+=text(320,325,'Successive wavefronts in a stationary medium; schematic',13)
    return svg(b,'Moving source wavefronts')
def add(family,sub,variant,kind,title,stem,*,opts=None,reasoning='',parts=None,level='core',diagram=None,worked=None,summary='',difficulty=None):
    n=len(Q)+1
    stem=re.sub(r'[-+]?\d+\.\d{10,}',lambda match:f(float(match.group()),10),stem)
    if difficulty is None:
        if kind=='multiple-choice':difficulty='easy' if family in {1,2,7,8,14,19,25,26} or (family==13 and variant==2) else 'medium'
        else:difficulty='hard' if family in {3,5,16,17,21,22,28,29} else 'medium'
    q={'id':f'ib-phy-c-{n:03}','subject':'physics-hl','topicId':'wave-behaviour','collectionId':'physics-wave-behaviour','number':n,'title':title,'subtopic':['Simple harmonic motion','Wave model','Wave phenomena','Standing waves and resonance','Doppler effect'][sub-1],'syllabusCode':f'C.{sub}','level':level,'questionType':kind,'difficulty':difficulty,'calculator':True,'stem':stem,'source':{'document':'Independent syllabus-authored practice','question':n},'verification':{'method':'Deterministic calculation, wave-boundary and dimensional checks in the independent authoring script','notes':f'Editorial family C{family:02}; variant {variant+1}/4. Original setting, numbers, data and artwork; analytical solution and marking arithmetic checked by author. Independent editorial review is separate.'},'status':'published'}
    if kind=='multiple-choice':
        assert opts and len(opts)==4 and len(set(opts))==4
        shift=(n-1)%4;ordered=opts[-shift:]+opts[:-shift]if shift else opts[:];letter='ABCD'[shift]
        q.update(marks=1,parts=[],options=[{'label':lab,'text':t}for lab,t in zip('ABCD',ordered)],correctOption=letter,markScheme=[{'part':'','steps':[{'code':'A1','text':letter+'. '+reasoning}]}])
    else:
        assert parts;q['parts']=[];q['markScheme']=[]
        for j,(prompt,steps)in enumerate(parts):
            lab='abcdefghijklmnopqrstuvwxyz'[j];marks=sum(int(c[1:])for c,t in steps)
            q['parts'].append({'label':lab,'prompt':prompt,'marks':marks});q['markScheme'].append({'part':lab,'steps':[{'code':c,'text':t}for c,t in steps]})
        q['marks']=sum(z['marks']for z in q['parts'])
    if diagram:q['diagramSvg']=diagram
    if worked:q['markSchemeDiagramSvg']=worked
    if summary:q['answerSummary']=summary
    q['stem']=format_literal_subscripts(q['stem'])
    for part in q['parts']:part['prompt']=format_literal_subscripts(part['prompt'])
    for option in q.get('options',[]):option['text']=format_literal_subscripts(option['text'])
    for group in q['markScheme']:
        for point in group['steps']:point['text']=format_literal_subscripts(point['text'])
    Q.append(q);FAMILIES.append(family)

# C.1: SHM condition, period, phase, energy and measured restoring acceleration.
shmconcept=[
('Recognising a restoring acceleration','Which acceleration-displacement relationship describes simple harmonic motion about x = 0, where k is a positive constant?', ['a = −kx.','a = kx.','a = −k/x.','a = −kx² for all x.'],'Acceleration must be proportional to displacement and directed toward equilibrium. The negative proportionality satisfies both conditions.'),
('At maximum displacement','A particle undergoes undamped SHM. At its maximum positive displacement, which pair describes its velocity and acceleration?', ['Velocity is zero; acceleration is directed toward equilibrium.','Velocity is maximum; acceleration is zero.','Velocity and acceleration are both zero.','Velocity is zero; acceleration is directed away from equilibrium.'],'At a turning point the instantaneous velocity is zero, while the restoring acceleration has maximum magnitude toward equilibrium.'),
('At the equilibrium point','An undamped SHM particle crosses equilibrium. Which statement is correct?', ['Speed is maximum and acceleration is zero.','Speed and acceleration are both maximum.','Speed is zero and acceleration is maximum.','Its total mechanical energy is zero.'],'At equilibrium displacement and restoring acceleration are zero. The energy is momentarily entirely kinetic relative to the equilibrium potential-energy zero.'),
('Changing amplitude','A small-angle pendulum oscillates with period T. Its amplitude is reduced while remaining within the small-angle model. What happens to its period?', ['It remains T in this model.','It halves with the amplitude.','It doubles with the amplitude.','It becomes zero.'],'The small-angle period 2π√(L/g) is independent of amplitude. This independence is a property of the approximation, not a statement about arbitrarily large swings.')]
for v,(t,s,o,r)in enumerate(shmconcept):add(1,1,v,'multiple-choice',t,s,opts=o,reasoning=r)

for v in range(4):
    if v==0:s='A mass-spring oscillator has its mass multiplied by four while its spring constant is unchanged. What is the ratio of its new period to its old period?';g=2;bad=[4,.5,16];why='T = 2π√(m/k), so multiplying mass by four multiplies period by two.'
    elif v==1:s='A mass-spring oscillator has its spring constant multiplied by nine while mass stays fixed. What is its new period divided by its old period?';g=1/3;bad=[3,1/9,9];why='T is inversely proportional to √k, so the period ratio is 1/√9 = 1/3.'
    elif v==2:s='A small-angle pendulum is moved to a location with one quarter of the original gravitational field strength. Its length stays fixed. What is its new period divided by its old period?';g=2;bad=[.5,4,.25];why='T = 2π√(L/g); replacing g by g/4 doubles T.'
    else:s='A small-angle pendulum is to have three times its original period at the same location. By what factor must its length be multiplied?';g=9;bad=[3,math.sqrt(3),1/9];why='T is proportional to √L. A period factor of three requires a length factor of nine.'
    add(2,1,v,'multiple-choice','Period scaling without substitution',s,opts=numeric(g,bad),reasoning=why)

for v in range(4):
    A=.04+.01*v;T=.8+.2*v;omega=2*math.pi/T;phi=[math.pi/2,3*math.pi/2,0,math.pi][v];condition=['at its maximum positive displacement','at its maximum negative displacement','crossing equilibrium in the positive direction','crossing equilibrium in the negative direction'][v];fraction=[.1,.15,.2,.3][v];t=fraction*T;x=A*math.sin(omega*t+phi);vel=omega*A*math.cos(omega*t+phi);acc=-omega**2*x
    assert math.isclose(vel**2+omega**2*x*x,omega**2*A*A,rel_tol=1e-12)
    add(3,1,v,'structured','Initial conditions fix the phase',f'An oscillator has amplitude {f(A)} m and period {f(T)} s. At t = 0 it is {condition}. Describe its motion using x = A sin(ωt + φ), taking φ in the interval 0 ≤ φ < 2π.',parts=[p('Determine ω and a suitable phase constant φ.',step(f'ω = 2π/T = {f(omega)} rad s⁻¹.'),step(f'φ = {f(phi)} rad'+(' (zero).'if phi==0 else '.'))),p(f'Calculate the displacement and velocity at t = {f(t)} s.',step('Use x = A sin(ωt + φ) and v = ωA cos(ωt + φ), with the same phase.','M1'),step(f'x = {f(x)} m; v = {f(vel)} m s⁻¹. The velocity sign specifies its direction.')),p('Determine the acceleration at that instant.',step(f'a = −ω²x = {f(acc)} m s⁻².'))],level='ahl',diagram=plot([j*T/128 for j in range(129)],[A*math.sin(2*math.pi*j/128+phi)for j in range(129)],'Time / s','Displacement / m','SHM initial condition and one full period',False),summary=f'φ = {f(phi)} rad; x = {f(x)} m; v = {f(vel)} m s⁻¹')

for v in range(4):
    if v<2:
        m=.2+.1*v;k=32+16*v;T=2*math.pi*math.sqrt(m/k);newmass=m*.5
        add(4,1,v,'structured','Inferring a spring constant',f'A {f(m)} kg mass oscillates on a horizontal spring with measured period {f(T,6)} s. Friction is negligible and the spring obeys Hooke’s law.',parts=[p('Determine the spring constant.',step('Rearrange T = 2π√(m/k) to k = 4π²m/T².','M1'),step(f'k = {f(k)} N m⁻¹.')),p(f'The mass is replaced by {f(newmass)} kg. Predict the new period.',step(f'T_new = T√(m_new/m) = {f(T/math.sqrt(2))} s.')),p('Explain why the restoring force produces SHM.',step('Hooke’s law gives F = −kx, so a = −(k/m)x: acceleration is proportional to displacement and opposite to it.','R1'))],summary=f'k = {f(k)} N m⁻¹')
    else:
        L=.75+.25*(v-2);g=[0,0,9.6,9.9][v];T=2*math.pi*math.sqrt(L/g);angle=[0,0,4,6][v]
        add(4,1,v,'structured','A pendulum measures local gravity',f'A pendulum of length {L} m oscillates with small angular amplitude {angle}° and period {f(T,6)} s. The bob can be modelled as a point mass, and air resistance is negligible.',parts=[p('Determine the local gravitational field strength.',step('Rearrange T = 2π√(L/g) to g = 4π²L/T².','M1'),step(f'g = {f(g)} m s⁻².')),p('Explain why the small angular amplitude matters for this model.',step('For small angles, sin θ ≈ θ in radians.','R1'),step('The restoring force is then proportional to displacement, allowing the SHM period relation.','R1')),p('Predict the period if the length is made four times as large.',step(f'T_new = 2T = {f(2*T)} s.'))],summary=f'g = {f(g)} m s⁻²')

for v in range(4):
    mass=.1+.05*v;A=.06+.02*v;freq=2+.5*v;omega=2*math.pi*freq;q=[.25,.5,-.6,.8][v];x=q*A;Et=.5*mass*omega**2*A*A;Ep=.5*mass*omega**2*x*x;Ek=Et-Ep;speed=math.sqrt(2*Ek/mass)
    assert math.isclose(Ep/Et,q*q)
    add(5,1,v,'structured','Partitioning oscillator energy',f'A {f(mass)} kg oscillator undergoes SHM of amplitude {f(A)} m and frequency {f(freq)} Hz. Potential energy is zero at equilibrium. Consider the instant when displacement x = {f(x)} m.',parts=[p('Calculate the total mechanical energy.',step('Use ω = 2πf and E_total = ½mω²A².','M1'),step(f'E_total = {f(Et)} J.')),p('Calculate the potential energy, kinetic energy and speed at the stated displacement.',step(f'E_p = ½mω²x² = {f(Ep)} J; E_k = E_total − E_p = {f(Ek)} J.'),step(f'Speed = sqrt(2E_k/m) = {f(speed)} m s⁻¹.')),p('Explain why the velocity is not uniquely determined by the displacement alone.',step('The oscillator passes the same non-turning-point displacement moving in two opposite directions, so the same speed can have either velocity sign.','R1'))],level='ahl',diagram=plot([-1+j/40 for j in range(81)],[(-1+j/40)**2 for j in range(81)],'Displacement / amplitude','Potential energy / total energy','Normalized potential-energy shape; absolute energy is not given',False),worked=plot([-A+2*A*j/80 for j in range(81)],[Et*(1-(-1+2*j/80)**2) for j in range(81)],'Displacement / m','Kinetic energy / J','Complementary kinetic-energy curve',False),summary=f'E_total = {f(Et)} J; speed = {f(speed)} m s⁻¹')

for v in range(4):
    K=36+13*v;xs=[-.04,-.02,0,.02,.04];aa=[-K*x for x in xs];T=2*math.pi/math.sqrt(K);unc=.08+.02*v
    table='\n\n| Displacement / m | Acceleration / m s⁻² |\n|---:|---:|\n'+'\n'.join(f'| {x:+.2f} | {a:+.2f} |'for x,a in zip(xs,aa))
    add(6,1,v,'data-based','Testing the SHM condition with sensors',f'The following simulated measurements describe an oscillator. Displacement uncertainty is negligible compared with acceleration uncertainty ±{f(unc)} m s⁻².'+table,parts=[p('Use the relationship between acceleration and displacement to assess whether the data support SHM.',step('The measurements lie on a straight line through the origin with negative gradient.','R1'),step('Thus acceleration is proportional to displacement and directed toward equilibrium, consistent with SHM.','R1')),p('Determine the angular frequency and period.',step(f'The gradient is −{K} s⁻², so ω² = {K} and ω = {f(math.sqrt(K))} rad s⁻¹.','M1'),step(f'T = 2π/ω = {f(T)} s.')),p('A sensor later adds the same positive offset to every acceleration reading. Describe its effect on the gradient and the inference of equilibrium position.',step('The gradient is unchanged, so the period inferred from the slope is unchanged.','R1'),step('The zero-acceleration intercept shifts; without correcting the offset, the inferred equilibrium displacement is biased.','R1'))],diagram=plot(xs,aa,'Displacement / m','Acceleration / m s⁻²','Simulated restoring-acceleration measurements'),worked=plot(xs,aa,'Displacement / m','Acceleration / m s⁻²','Negative slope equals minus angular frequency squared'),summary=f'ω = {f(math.sqrt(K))} rad s⁻¹; T = {f(T)} s')

# C.2: distinguish medium motion, temporal/spatial periods and propagation.
waveconcept=[
('A transverse disturbance','A wave travels east along a string while each small string element moves north and south. What type of wave is this?', ['Transverse.','Longitudinal.','A stationary electric current.','A flow carrying the entire string east.'],'Particle displacement is perpendicular to the propagation direction, which defines a transverse wave.'),
('A longitudinal disturbance','A sound wave travels through air along a straight tube. Which description of nearby air-particle motion is appropriate?', ['Particles oscillate parallel to the wave’s travel direction.','All particles travel with the pulse from one end to the other.','Particles oscillate only perpendicular to the tube.','Particles remain fixed because only pressure changes.'],'In a longitudinal sound wave the particles oscillate back and forth along the propagation direction, creating compressions and rarefactions.'),
('A wave in a vacuum','Which disturbance can propagate through a vacuum?', ['Visible electromagnetic radiation.','A sound pulse in air.','A wave on a stretched string.','A surface water wave.'],'Electromagnetic waves do not require a material medium, whereas the other listed waves rely on mechanical interactions in matter.'),
('Energy without bulk transport','A floating marker bobs as a small surface wave passes, then remains near its initial horizontal position. Which interpretation is appropriate?', ['The wave transfers energy while the marker mainly oscillates locally.','No energy is transferred because the marker does not move with the wave.','The entire water surface travels at the wave speed.','The marker must be at a node of a standing wave.'],'Travelling waves can transfer energy through successive local oscillations with no net bulk displacement in the ideal wave model.')]
for v,(t,s,o,r)in enumerate(waveconcept):add(7,2,v,'multiple-choice',t,s,opts=o,reasoning=r)

for v in range(4):
    lam=[.8,1.2,.006,500e-9][v];freq=[5,12,4000,6e14][v];speed=lam*freq
    if v==0:s=f'A travelling wave has wavelength {lam} m and frequency {freq} Hz. What is its speed?';g=speed;bad=[lam/freq,freq/lam,2*speed];u='m s⁻¹'
    elif v==1:s=f'A wave travels at {f(speed)} m s⁻¹ and has frequency {freq} Hz. What is its wavelength?';g=lam;bad=[speed*freq,lam/2,1/lam];u='m'
    elif v==2:s=f'A wave travels at {f(speed)} m s⁻¹ and has wavelength {f(lam)} m. What is its period?';g=1/freq;bad=[freq,lam/speed*2,1/(2*freq)];u='s'
    else:s=f'An electromagnetic wave in vacuum has wavelength {f(lam)} m. Taking c = 3.00 × 10⁸ m s⁻¹, what is its frequency?';g=freq;bad=[3e8*lam,freq/1000,freq*2];u='Hz'
    add(8,2,v,'multiple-choice','Connecting wave speed and periods',s,opts=numeric(g,bad,u),reasoning=f'Use v = fλ and T = 1/f. The requested quantity is {f(g)} {u}. A spatial repeat distance and a temporal repeat time are different quantities.')

for v in range(4):
    if v==0:s='A wave crosses into a medium in which its speed is 0.75 of its original value. The source is unchanged. What happens to frequency and wavelength?';o=['Frequency stays fixed; wavelength becomes 0.75 of its original value.','Frequency becomes 0.75; wavelength stays fixed.','Both frequency and wavelength become 0.75.','Frequency stays fixed; wavelength becomes 4/3 of its original value.'];r='The source sets frequency across a stationary boundary. From λ = v/f, wavelength scales with speed.'
    elif v==1:s='A source doubles its frequency while generating waves in an ideal nondispersive medium of unchanged wave speed. How does wavelength change?';o=['It halves.','It doubles.','It stays fixed.','It increases by a factor of four.'];r='At fixed propagation speed, wavelength v/f is inversely proportional to frequency.'
    elif v==2:s='A travelling wave is described by both a displacement-position snapshot and a displacement-time graph at one position. Which pairing is correct?';o=['Snapshot repeat distance gives wavelength; time-graph repeat interval gives period.','Snapshot repeat distance gives period; time-graph repeat interval gives wavelength.','Both graphs directly give speed from their vertical-axis amplitude.','Both horizontal axes must have the same unit.'];r='The horizontal axis determines whether a repeat measures distance or time. The speed is then wavelength divided by period.'
    else:s='Two waves travel in the same nondispersive medium. Wave X has three times the wavelength of wave Y. Which frequency ratio is correct?';o=['f_X/f_Y = 1/3.','f_X/f_Y = 3.','f_X/f_Y = 9.','f_X/f_Y = 1.'];r='For the common wave speed, f = v/λ. Tripling wavelength reduces frequency to one third.'
    add(9,2,v,'multiple-choice','What changes at a stationary boundary?',s,opts=o,reasoning=r)

for v in range(4):
    A=.02+.01*v;lam=.4+.2*v;freq=3+v;speed=lam*freq;direction='right'if v%2==0 else'left';xp=lam/8;yp=A/math.sqrt(2);motion='downward'if direction=='right'else'upward'
    add(10,2,v,'structured','Reading a travelling-wave snapshot',f'A sinusoidal wave travels to the {direction} along a string. Its frequency is {freq} Hz. The snapshot at t = 0 is shown. The displacement is zero at x = 0 and initially increases with x. Consider the particle at x = {f(xp)} m.',parts=[p('State the amplitude and wavelength, and calculate the wave speed.',step(f'Amplitude = {f(A)} m; wavelength = {f(lam)} m.'),step(f'Wave speed = fλ = {f(speed)} m s⁻¹.')),p('Determine whether the indicated particle is moving upward or downward at this instant. Explain using the travelling shape.',step(f'The particle is moving {motion}.','A1'),step('For rightward travel the shape just to the left arrives next, so a positive spatial slope means displacement decreases.'if direction=='right'else'For leftward travel the shape just to the right arrives next, so a positive spatial slope means displacement increases.','R1')),p('Calculate the time for the wave pattern to travel one quarter of a wavelength.',step(f't = (λ/4)/v = 1/(4f) = {f(1/(4*freq))} s.'))],diagram=wave(A,lam,direction=direction),worked=wave(A,lam,direction=direction,annotate=True),summary=f'v = {f(speed)} m s⁻¹; particle moves {motion}')

for v in range(4):
    freq=8+4*v;speed1=2+.5*v;speed2=1.2+.4*v;duration=.5+.25*v;lam1=speed1/freq;lam2=speed2/freq;count=freq*duration;L1=speed1*duration;L2=speed2*duration
    add(11,2,v,'structured','A finite wave train enters another medium',f'A source produces a sinusoidal wave for {f(duration)} s at frequency {freq} Hz. The wave speed is {f(speed1)} m s⁻¹ in region 1 and {f(speed2)} m s⁻¹ in region 2. The boundary is stationary and there is no change of source frequency.',parts=[p('Determine the number of oscillations emitted and the spatial length of the complete wave train in region 1.',step(f'N = fΔt = {f(count)} oscillations.'),step(f'L_train,1 = v₁Δt = {f(L1)} m.')),p('Calculate the wavelength in each region.',step(f'λ₁ = v₁/f = {f(lam1)} m; λ₂ = v₂/f = {f(lam2)} m.')),p('Once the entire train is inside region 2, determine its length and explain whether its number of oscillations has changed.',step(f'L_train,2 = Nλ₂ = {f(L2)} m.','M1'),step('The number of emitted oscillations is unchanged; the same cycles occupy a different spatial length because propagation speed changes.','R1'))],summary=f'{f(count)} cycles; wavelengths {f(lam1)} m and {f(lam2)} m')

for v in range(4):
    vel=.8+.4*v;ts=[0,.05,.10,.15,.20];xs=[.10+vel*t for t in ts];roundxs=[round(x,3)for x in xs];delta=.002+.001*v;best=(roundxs[-1]-roundxs[0])/.2;unc=2*delta/.2;lam=.12+.04*v;freq=best/lam
    table='\n\n| Time / s | Crest position / m |\n|---:|---:|\n'+'\n'.join(f'| {t:.2f} | {x:.3f} |'for t,x in zip(ts,roundxs))
    add(12,2,v,'data-based','Tracking the same wave crest',f'A video follows the same crest of a travelling wave. Simulated positions are listed below; the uncertainty of every position is ±{f(delta)} m and timing uncertainty is negligible. The wavelength is measured independently as {f(lam)} m.'+table,parts=[p('Determine the wave speed from the displacement of the tracked crest over the full interval.',step('Use the slope of crest position against time.','M1'),step(f'v = ({f(roundxs[-1])} − {f(roundxs[0])})/0.20 = {f(best)} m s⁻¹.')),p('Estimate the maximum absolute uncertainty in this endpoint speed.',step(f'Uncertainty in the position difference is 2Δx = {f(2*delta)} m.','M1'),step(f'Δv = 2Δx/Δt = {f(unc)} m s⁻¹.')),p('Calculate the wave frequency and explain why the graph does not describe the trajectory of one medium particle.',step(f'f = v/λ = {f(freq)} Hz.'),step('The camera follows a propagating phase feature. Individual medium particles oscillate locally instead of travelling along with that crest.','R1'))],diagram=plot(ts,roundxs,'Time / s','Crest position / m','Simulated motion of one identifiable crest'),worked=plot(ts,roundxs,'Time / s','Crest position / m','Gradient represents propagation speed'),summary=f'v = {f(best)} ± {f(unc)} m s⁻¹; f = {f(freq)} Hz')

# C.3: refraction, superposition, two slits, gratings and diffraction envelopes.
for v in range(4):
    if v==0:
        n1=1;n2=1.50;theta=38;out=math.degrees(math.asin(n1*math.sin(math.radians(theta))/n2));s=f'A ray enters glass of refractive index {n2} from air at {theta}° to the normal. What is its refracted angle?';o=numeric(out,[theta,90-out,math.degrees(math.asin(math.sin(math.radians(theta))*n2))],'°');r=f'Snell’s law gives sin θ₂ = sin {theta}°/{n2}, so θ₂ = {f(out)}°. The ray bends toward the normal.'
    elif v==1:
        n1=1.33;n2=1;out=math.degrees(math.asin(1/n1));s='Light travels from water of refractive index 1.33 toward air. What is the critical angle measured inside the water?';o=numeric(out,[90-out,1/n1,math.degrees(math.atan(1/n1))],'°');r=f'At critical incidence the transmitted ray is at 90° to the normal. Thus sin θ_c = 1/1.33 and θ_c = {f(out)}°.'
    elif v==2:
        s='Which set of conditions allows total internal reflection at a transparent boundary?';o=['The incident medium has higher refractive index and incidence exceeds the critical angle.','The incident medium has lower refractive index and incidence exceeds 45°.','The light is normally incident from any medium.','The incidence angle equals zero and both media have the same index.'];r='Total internal reflection requires travel toward a lower-index medium and incidence greater than the relevant critical angle.'
    else:
        theta=50;out=30;n=math.sin(math.radians(theta))/math.sin(math.radians(out));s='A ray entering a transparent material from air has incidence 50.0° and refraction 30.0°, both measured from the normal. What is the material’s refractive index?';o=numeric(n,[1/n,50/30,30/50]);r=f'With air index 1, n = sin 50.0°/sin 30.0° = {f(n)}. Ratios of angles themselves are not Snell’s law.'
    add(13,3,v,'multiple-choice','Refraction and critical conditions',s,opts=o,reasoning=r)

supercases=[
('A half-integer path difference','Two coherent sources oscillate in phase. At point P their path difference is 2.5 wavelengths and their amplitudes are equal. What is observed at P?', ['Complete destructive interference.','Maximum constructive interference.','A permanent doubling of the wave frequency.','No superposition because the sources are separate.'],'A half-integer number of wavelengths gives a phase difference of an odd multiple of π. Equal-amplitude displacements cancel.'),
('An integer path difference','Two coherent sources oscillate in phase and have equal amplitude A at P. Their path difference is three wavelengths. What is the resultant amplitude at P?', ['2A.','A.','0.','A/2.'],'An integer path difference gives in-phase arrival. The displacements add, so the resultant amplitude is 2A.'),
('Two overlapping pulses','At one point, two small transverse pulses would separately produce displacements +0.035 m and −0.020 m. What displacement does linear superposition predict?', ['+0.015 m.','+0.055 m.','−0.055 m.','−0.015 m.'],'Add signed displacements: +0.035 − 0.020 = +0.015 m. The signs describe opposite directions.'),
('Conditions for a stable pattern','Which property of two sources is essential for a stable interference pattern?', ['A constant phase difference and the same frequency.','Exactly equal source powers in every circumstance.','Different frequencies that continually drift.','Both sources moving at the wave speed.'],'Coherence requires a stable phase relation. Equal amplitude improves contrast but is not the defining requirement for a stable pattern.')]
for v,(t,s,o,r)in enumerate(supercases):add(14,3,v,'multiple-choice',t,s,opts=o,reasoning=r)

for v in range(4):
    wavelength=(450+50*v)*1e-9;D=1.5+.4*v;d=(.2+.05*v)*1e-3;spacing=wavelength*D/d;order=2+v;newindex=1.2+.1*v;newspacing=spacing/newindex
    add(15,3,v,'structured','Designing a two-slit measurement',f'Normally incident monochromatic light of vacuum wavelength {f(wavelength*1e9)} nm passes through two narrow slits separated by {f(d*1000)} mm. A screen is {f(D)} m away in air. Use the small-angle approximation, with air refractive index 1.',parts=[p('Calculate the separation of adjacent bright fringes.',step('Use s = λD/d, converting wavelength and slit separation to metres.','M1'),step(f's = {f(spacing)} m = {f(spacing*1000)} mm.')),p(f'Determine the distance from the central bright fringe to the order-{order} bright fringe on one side.',step(f'y_{order} = {order}s = {f(order*spacing*1000)} mm.')),p(f'The whole space between slits and screen is filled with a transparent medium of refractive index {f(newindex)}. Predict the new fringe spacing and explain which wave quantity stays unchanged.',step(f'λ_medium = λ_vacuum/n, so s_new = s/n = {f(newspacing*1000)} mm.','M1'),step('The frequency stays fixed because it is set by the source; speed and wavelength both decrease in the medium.','R1'))],diagram=slits(f'{f(d*1000)} mm',f'{f(D)} m'),summary=f's = {f(spacing*1000)} mm; filled-medium s = {f(newspacing*1000)} mm')

for v in range(4):
    lines=[300,380,460,540][v];d=1/(lines*1000);lam=(450+50*v)*1e-9;order=2;angle=math.degrees(math.asin(order*lam/d));maxorder=math.floor(d/lam);count=2*maxorder+1
    assert order<=maxorder and maxorder*lam/d<=1<(maxorder+1)*lam/d
    add(16,3,v,'structured','Resolving diffraction-grating orders',f'A grating has {lines} equally spaced lines per millimetre. Monochromatic light of wavelength {f(lam*1e9)} nm falls normally on it. Assume all allowed orders can be detected.',parts=[p('Determine the separation of adjacent grating lines.',step(f'd = 1/({lines} × 1000) = {f(d)} m.')),p('Calculate the angle of the second-order maximum from the forward normal.',step('Use nλ = d sin θ with n = 2.','M1'),step(f'θ₂ = {f(angle)}°.')),p('Determine the largest allowed order and the total number of maxima on both sides, including the central maximum.',step(f'Allowed orders satisfy nλ/d ≤ 1, so n_max = floor(d/λ) = {maxorder}.'),step(f'Total = 2n_max + 1 = {count}.')),p('If white light is used, explain why the noncentral maxima separate colours.',step('At a fixed nonzero order, sin θ is proportional to wavelength, so longer wavelengths appear at larger angles.','R1'))],level='ahl',diagram=slits('?','far-field screen','Neighbouring grating openings; separation to be determined'),summary=f'd = {f(d)} m; θ₂ = {f(angle)}°; {count} maxima')

for v in range(4):
    lam=(480+40*v)*1e-9;b=(.12+.03*v)*1e-3;D=1.8+.3*v;ratio=3+v;d=ratio*b;theta=lam/b;width=2*D*theta;fringe=lam*D/d;count=2*ratio-1
    angles=[theta*(-2+4*j/240)for j in range(241)]
    def intens(a):
        z=math.pi*b*a/lam;env=1 if abs(z)<1e-12 else(math.sin(z)/z)**2
        return env*math.cos(math.pi*d*a/lam)**2
    ii=[intens(a)for a in angles]
    add(17,3,v,'structured','Interference inside a diffraction envelope',f'Two identical rectangular slits each have width {f(b*1000)} mm and centre separation {f(d*1000)} mm. They are illuminated normally by monochromatic light of wavelength {f(lam*1e9)} nm. A screen is {f(D)} m away. Use small angles and the first single-slit minimum θ = λ/b.',parts=[p('Determine the angular position of the first envelope minimum and the full width of the central envelope on the screen.',step(f'θ_min = λ/b = {f(theta)} rad.','M1'),step(f'Central width = 2Dθ_min = {f(width*1000)} mm.')),p('Calculate the separation of adjacent two-slit interference maxima.',step(f's = λD/d = {f(fringe*1000)} mm.')),p('Determine which nonzero interference order first coincides with an envelope minimum, and count the bright interference maxima strictly inside the central envelope.',step(f'At coincidence mλ/d = λ/b, so m = d/b = {ratio}.','M1'),step(f'The allowed interior orders are −{ratio-1} through +{ratio-1}, giving {count} bright maxima. The ±{ratio} maxima are suppressed at the minima.'))],level='ahl',diagram=slits(f'{f(d*1000)} mm',f'{f(D)} m','Given two-slit geometry; each individual width is supplied in the question'),worked=plot(angles,ii,'Angle from central direction / rad','Relative intensity','Computed two-slit intensity under a single-slit envelope',False),summary=f'Central width {f(width*1000)} mm; first missing order {ratio}; {count} interior maxima')

for v in range(4):
    n=1.3+.1*v;refr=[math.degrees(math.asin(.1*j))for j in range(1,6)];inc=[math.degrees(math.asin(n*.1*j))for j in range(1,6)];rounded_in=[round(x,1)for x in inc];rounded_out=[round(x,1)for x in refr];xx=[math.sin(math.radians(x))for x in rounded_out];yy=[math.sin(math.radians(x))for x in rounded_in];gradient=(yy[-1]-yy[0])/(xx[-1]-xx[0]);critical=math.degrees(math.asin(1/gradient))
    table='\n\n| Incidence in air / ° | Refraction in material / ° |\n|---:|---:|\n'+'\n'.join(f'| {a:.1f} | {bval:.1f} |'for a,bval in zip(rounded_in,rounded_out))
    add(18,3,v,'data-based','Measuring refractive index by linearization',f'The following simulated angle readings describe light passing from air into a transparent block. Both angles are measured from the normal. The air index is 1.00.'+table,parts=[p('State the pair of quantities that should be plotted to obtain a straight line whose gradient is the block’s refractive index.',step('Plot sin(incidence) vertically against sin(refraction) horizontally, since sin i = n sin r.','R1')),p('Use the first and last readings in the linearized variables to estimate n.',step('Calculate both sine differences, then gradient = Δ(sin i)/Δ(sin r).','M1'),step(f'n ≈ {f(gradient)}; accept sensible fit estimates consistent with the rounded table.')),p('Use this estimate to determine the critical angle for travel from the block into air.',step(f'sin θ_c = 1/n, giving θ_c ≈ {f(critical)}°.')),p('Explain why plotting incidence angle directly against refraction angle is not an exact linearization.',step('Snell’s law relates the sines of the angles, not the angles themselves. A ratio-of-angles approximation is only justified at small angles.','R1'))],diagram=plot(rounded_out,rounded_in,'Refraction angle / degrees','Incidence angle / degrees','Raw simulated refraction-angle data'),worked=rays(1,gradient,rounded_in[2],rounded_out[2],True),summary=f'n ≈ {f(gradient)}; critical angle ≈ {f(critical)}°')

# C.4: all patterns refer to displacement nodes and antinodes, not pressure.
standconcept=[
('What happens at a node?','In an ideal standing wave on a string, what is the oscillation amplitude at a displacement node?', ['Zero.','Equal to the largest antinode amplitude.','Twice the amplitude at an antinode.','Dependent only on the speed of the observer.'],'At a displacement node the two counter-propagating equal waves cancel at every instant.'),
('Phase within one loop','Two non-node particles lie between the same two adjacent nodes of a standing wave. What is their phase difference?', ['0 rad.','π/2 rad.','π rad.','It increases steadily with their separation as for a travelling wave.'],'All non-node particles in one loop move in phase, although their amplitudes depend on position.'),
('Phase across a node','Two non-node particles are in adjacent loops of a standing wave. What is their phase difference?', ['π rad.','0 rad.','π/4 rad.','It cannot be fixed in a standing wave.'],'Adjacent loops have opposite displacement and velocity signs at corresponding times, giving a phase difference of π.'),
('An open and a closed end','An ideal air column is closed at one end and open at the other. Which sequence lists its first three allowed harmonic numbers?', ['1, 3, 5.','1, 2, 3.','2, 4, 6.','0, 1, 2.'],'The closed end is a displacement node and the open end an antinode, admitting odd numbers of quarter-wavelengths.')]
for v,(t,s,o,r)in enumerate(standconcept):add(19,4,v,'multiple-choice',t,s,opts=o,reasoning=r)

dampconcept=[
('Critical damping','A displaced mechanism is released from rest and must return to equilibrium as quickly as possible without oscillating. Which ideal damping regime is appropriate?', ['Critical damping.','Zero damping.','Very heavy damping in all cases.','Negative damping.'],'Critical damping is the boundary between oscillatory and nonoscillatory response and gives the fastest return without overshoot in the stated oscillator model.'),
('Heavy damping','A heavily damped oscillator is displaced and released without an initial velocity. Which behaviour is expected?', ['A slow return toward equilibrium without repeated crossings.','An oscillation of constant amplitude forever.','A steadily growing oscillation without energy input.','Instantaneous return with infinite speed.'],'Strong damping suppresses oscillations but can make the return slower than in the critical case.'),
('Increasing damping near resonance','For an otherwise unchanged driven oscillator, stronger damping usually has which effect on its resonance response?', ['A lower, broader amplitude peak.','An infinitely high, narrower peak.','A zero response at every driving frequency.','A larger amplitude at all frequencies without additional energy input.'],'More energy is dissipated each cycle. The resonance peak is reduced and broadened; its position can also shift.'),
('Forced oscillation frequency','A damped system is driven steadily at frequency 7 Hz. After transients have died away, at what frequency does its driven oscillation occur?', ['7 Hz.','Always its undamped natural frequency, whatever the drive.','14 Hz in every case.','Zero frequency because damping is present.'],'The sustained forced motion follows the driving frequency. Amplitude depends on how this compares with the system’s natural frequency and damping.')]
for v,(t,s,o,r)in enumerate(dampconcept):add(20,4,v,'multiple-choice',t,s,opts=o,reasoning=r)

for v in range(4):
    L=.8+.2*v;speed=24+6*v;harm=[2,3,3,5][v];boundary=['fixed-fixed','free-free','mixed','mixed'][v];mixed=boundary=='mixed';lam=(4 if mixed else 2)*L/harm;freq=speed/lam;first=speed/((4 if mixed else 2)*L);x1=L/8;x2=7*L/8
    shape=(lambda u:math.sin(harm*math.pi*u/2))if mixed else((lambda u:math.cos(harm*math.pi*u))if boundary=='free-free'else(lambda u:math.sin(harm*math.pi*u)))
    phase=0 if shape(1/8)*shape(7/8)>0 else math.pi
    bdesc={'fixed-fixed':'fixed at both ends','free-free':'free at both ends in an ideal transverse model','mixed':'fixed at the left end and free at the right end'}[boundary]
    add(21,4,v,'structured','Boundary conditions select string modes',f'A string of length {f(L)} m is {bdesc}. The transverse wave speed is {speed} m s⁻¹. It oscillates in harmonic {harm}, whose displacement pattern is shown.',parts=[p('Determine the wavelength and frequency of this mode.',step(f'The boundary conditions give λ = {4 if mixed else 2}L/{harm} = {f(lam)} m.','M1'),step(f'f = v/λ = {f(freq)} Hz.')),p('Determine the frequency of the first harmonic.',step(f'f₁ = v/({4 if mixed else 2}L) = {f(first)} Hz.')),p(f'Determine the phase difference between particles at x = {f(x1)} m and x = {f(x2)} m, measured from the left end.',step(f'The particles are in {"same-phase"if phase==0 else"opposite-phase"} regions of the standing pattern.','R1'),step(f'Phase difference = {"0"if phase==0 else"π"} rad. Neither selected point is a node.'))],diagram=standing(L,harm,boundary),worked=standing(L,harm,boundary,True),summary=f'λ = {f(lam)} m; f = {f(freq)} Hz; f₁ = {f(first)} Hz')

for v in range(4):
    L=[.5,.6,.75,.8][v];speed=340;harm=[1,3,2,3][v];kind=['closed-open','closed-open','open-open','closed-closed'][v];mixed=v<2;factor=4 if mixed else 2;freq=harm*speed/(factor*L);nextn=harm+(2 if mixed else 1);nextfreq=nextn*speed/(factor*L);boundary='mixed'if mixed else('free-free'if v==2 else'fixed-fixed')
    add(22,4,v,'structured','Displacement modes in an air column',f'An ideal {kind.replace("-","–")} air column has length {L} m. The speed of sound is 340 m s⁻¹. Ignore end corrections. The displacement pattern shown is harmonic {harm}.',parts=[p('State the displacement boundary condition at each end.',step('A closed end is a displacement node and an open end is a displacement antinode. Apply this to the two ends shown.','R1')),p('Calculate the mode’s wavelength and frequency.',step(f'λ = {factor}L/{harm} = {f(factor*L/harm)} m.','M1'),step(f'f = {f(freq)} Hz.')),p('Determine the frequency of the next higher allowed mode and explain the step in harmonic number.',step(f'The next allowed harmonic is {nextn}, with frequency {f(nextfreq)} Hz.'),step('One closed and one open end admit only odd harmonics, so the harmonic number increases by two.'if mixed else'Two matching displacement boundary conditions admit each positive integer harmonic, so the harmonic number increases by one.','R1'))],diagram=standing(L,harm,boundary,end_labels=tuple(kind.split('-'))),worked=standing(L,harm,boundary,True,end_labels=tuple(kind.split('-'))),summary=f'f = {f(freq)} Hz; next mode {f(nextfreq)} Hz')

for v in range(4):
    centre=4+v;xs=[centre-2,centre-1,centre,centre+1,centre+2]
    weak_damping=.08;strong_damping=math.sqrt((1-((centre-1)/centre)**2)/2)
    amplitude=lambda frequency,damping:.8/math.sqrt((1-(frequency/centre)**2)**2+(2*damping*frequency/centre)**2)
    weak=[amplitude(x,weak_damping) for x in xs];strong=[amplitude(x,strong_damping) for x in xs]
    assert all(a>b for a,b in zip(weak,strong))
    assert xs[weak.index(max(weak))]==centre and xs[strong.index(max(strong))]==centre-1
    add(23,4,v,'structured','Interpreting two resonance responses',f'The response graph shows constructed samples of the steady amplitude of the same oscillator under the same driving-force amplitude, for two damping settings. The solid curve is X and the dashed curve is Y. The sampled frequency range is {centre-2}–{centre+2} Hz. Read approximate peak frequencies from the plotted points; amplitude is in cm. Connecting segments guide the eye between samples.',parts=[p('Identify which curve has stronger damping and justify the choice with two features.',step('Curve Y has stronger damping.','A1'),step('Its maximum amplitude is smaller and its response peak is broader. Both features support greater energy dissipation.','R1')),p('Estimate the peak-response frequency for each setting.',step(f'X peaks near {centre} Hz and Y near {centre-1} Hz.')),p(f'The drive is set to {centre+2} Hz. State the steady oscillation frequency and explain why it need not equal the frequency of maximum response.',step(f'The steady forced motion occurs at {centre+2} Hz.'),step('The driver sets the frequency; the resonance condition affects the amplitude of that forced motion rather than replacing its frequency.','R1')),p('Suggest a use of added damping where excessive resonance would be harmful.',step('Accept a specific application such as damping structural vibration, a machine mount or a vehicle suspension, with the purpose of limiting resonant amplitude.','R1'))],diagram=plot(xs,weak,'Driving frequency / Hz','Amplitude / cm','Solid X and dashed Y resonance responses',False,(xs,strong)),summary=f'Stronger damping: Y; peaks near {centre} Hz and {centre-1} Hz')

for v in range(4):
    speed=[40,60,320,340][v];factor=2 if v<2 else 4;Ls=[.20,.30,.40,.50,.60];freqs=[round(speed/(factor*L),2)for L in Ls];inv=[1/L for L in reversed(Ls)];ff=list(reversed(freqs));gradient=(ff[-1]-ff[0])/(inv[-1]-inv[0]);speed_est=factor*gradient;description='a stretched string fixed at both ends'if v<2 else'an ideal pipe closed at one end and open at the other'
    table='\n\n| Resonating length / m | First-harmonic frequency / Hz |\n|---:|---:|\n'+'\n'.join(f'| {L:.2f} | {fq:.2f} |'for L,fq in zip(Ls,freqs))
    add(24,4,v,'data-based','Inferring wave speed from resonance',f'Simulated first-harmonic measurements are made using {description}. The wave speed is held constant as the resonating length changes. Any pipe end correction is neglected.'+table,parts=[p('Choose a graph that linearizes frequency against length and state the expected gradient.',step(f'Plot f against 1/L; because f₁ = v/({factor}L), the gradient is v/{factor}.','R1')),p('Use the endpoint values of this linearized graph to estimate the wave speed.',step(f'Gradient ≈ {f(gradient)} Hz m = {f(gradient)} m s⁻¹.','M1'),step(f'v = {factor} × gradient ≈ {f(speed_est)} m s⁻¹.')),p('Predict the first-harmonic frequency for a length of 0.45 m.',step(f'f₁ = v/({factor} × 0.45) ≈ {f(speed_est/(factor*.45))} Hz.')),p('Describe one check that the observed resonance is the first harmonic rather than a higher allowed mode.',step('Observe the displacement pattern or find the lowest resonant frequency at fixed length; it must have the minimum number of nodes compatible with the boundary conditions.','R1'))],diagram=plot(Ls,freqs,'Resonating length / m','First-harmonic frequency / Hz','Raw simulated resonance measurements'),worked=standing(.45,1,'fixed-fixed'if factor==2 else'mixed',True,end_labels=('fixed','fixed')if factor==2 else('closed','open')),summary=f'Wave speed ≈ {f(speed_est)} m s⁻¹')

# C.5: nonrelativistic light shifts and one moving sound participant at a time.
dopplerconcept=[
('A redshifted spectral line','A known stellar emission line is observed at a slightly longer wavelength than its laboratory value. What does this indicate about the star’s radial motion?', ['It is receding from the observer.','It is approaching the observer.','It is necessarily moving only perpendicular to the line of sight.','Its light travels faster than c.'],'For a small Doppler shift, a longer observed wavelength corresponds to recession. The light speed remains c in vacuum.'),
('A source approaching an observer','A sound source approaches a stationary observer through still air. Which description applies to wavefronts ahead of the source?', ['They are closer together and the observed frequency is higher.','They are farther apart and the observed frequency is higher.','They are closer together and the sound speed in air increases.','Their separation is unchanged and the observed frequency is lower.'],'The advancing source emits successive wavefronts from positions closer to the observer, decreasing their spacing. The propagation speed in the medium is unchanged.'),
('Several shifted spectral lines','Three identifiable lines from the same receding object have the same small value of (observed wavelength − rest wavelength)/rest wavelength. Why is this useful?', ['The common fractional shift is consistent with one radial speed.','All three rest wavelengths must be equal.','All three photons must have the same energy.','The object must have zero radial motion.'],'At speed much smaller than c, Δλ/λ_rest ≈ v_radial/c. A common fractional shift therefore corresponds to a common radial velocity.'),
('A moving observer in sound','An observer moves toward a stationary sound source through still air. What changes in the medium itself?', ['Wavefront spacing is unchanged, although the observer encounters fronts more often.','The stationary source emits more cycles per second.','The wavelength everywhere in the air doubles.','The sound speed becomes the sum of source and observer speeds everywhere.'],'Observer motion changes the rate of meeting existing wavefronts. It does not change their spacing in the stationary medium or the source emission rate.')]
for v,(t,s,o,r)in enumerate(dopplerconcept):add(25,5,v,'multiple-choice',t,s,opts=o,reasoning=r)

for v in range(4):
    rest=[500,620,410,700][v];shift=[1.5,-1.24,.82,-2.1][v];obs=rest+shift;speed=C*shift/rest
    add(26,5,v,'multiple-choice','A signed radial velocity from light',f'A laboratory spectral line has wavelength {rest} nm. The same line from an object is measured at {f(obs,6)} nm. Take positive radial velocity to mean recession. For speeds much smaller than c, use Δλ/λ_rest ≈ v/c with c = 3.00 × 10⁸ m s⁻¹. What radial velocity is inferred?',opts=numeric(speed,[-speed,speed*10,speed/1000],'m s⁻¹'),reasoning=f'v = c(λ_observed − λ_rest)/λ_rest = {f(speed)} m s⁻¹. The {"positive"if speed>0 else"negative"} sign means {"recession"if speed>0 else"approach"}.')

for v in range(4):
    freq=[400,600,800,1000][v];u=[20,25,30,35][v];sound=340;source=v<2;approach=v%2==0
    if source:obs=freq*sound/(sound+(-u if approach else u));wrong=freq*(sound+(u if approach else-u))/sound
    else:obs=freq*(sound+(u if approach else-u))/sound;wrong=freq*sound/(sound+(-u if approach else u))
    phrase=('source moves toward'if approach else'source moves away from')+' a stationary observer'if source else('observer moves toward'if approach else'observer moves away from')+' a stationary source'
    add(27,5,v,'multiple-choice','Selecting the acoustic Doppler relation',f'A sound source emits at {freq} Hz in still air where sound speed is 340 m s⁻¹. The {phrase} at {u} m s⁻¹. What frequency is detected?',opts=numeric(obs,[wrong,freq,2*freq-obs],'Hz'),reasoning=(f'For a moving source use f′ = fv/(v {"−"if approach else"+"} u_s), giving {f(obs)} Hz.'if source else f'For a moving observer use f′ = f(v {"+"if approach else"−"} u_o)/v, giving {f(obs)} Hz.'),level='ahl')

for v in range(4):
    freq=[500,700,900,1100][v];sound=330+10*v;u=12+6*v;approach=v%2==0;obs=freq*sound/(sound+(-u if approach else u));spacing=(sound+(-u if approach else u))/freq;direction='toward'if approach else'away from'
    add(28,5,v,'structured','Inferring the speed of a moving sound source',f'A source emits {freq} Hz sound while moving directly {direction} a stationary detector through still air. Sound speed is {sound} m s⁻¹. The detector measures {f(obs,6)} Hz.',parts=[p('Determine the speed of the source.',step(f'Use f′ = fv/(v {"−"if approach else"+"} u_s) and rearrange.','M1'),step(f'u_s = {f(u)} m s⁻¹. Allow rounding consistent with the stated frequency.')),p('Calculate the spacing of successive wavefronts on the detector’s side of the source.',step(f'λ_detected-side = (v {"−"if approach else"+"} u_s)/f = {f(spacing)} m.')),p('Explain why the sound speed itself is not changed by source motion.',step('In this model the propagation speed is determined by the properties of the air. Source motion changes the positions of emission and hence wavefront spacing, not the speed of an emitted front through the air.','R1')),p('If the source stops but continues emitting at the same frequency, state the frequency eventually measured after the old wavefronts have passed.',step(f'The detector eventually measures the emission frequency, {freq} Hz.'))],level='ahl',diagram=fronts(approach),summary=f'Source speed {f(u)} m s⁻¹; wavefront spacing {f(spacing)} m')

for v in range(4):
    freq=[400,500,650,800][v];sound=340;u=[15,22,28,36][v];approach=v%2==0;obs=freq*(sound+(u if approach else-u))/sound;lam=sound/freq;sourceobs=freq*sound/(sound+(-u if approach else u));direction='toward'if approach else'away from'
    add(29,5,v,'structured','A receiver meets stationary wavefronts',f'A stationary source emits sound at {freq} Hz in still air at sound speed 340 m s⁻¹. A receiver moving directly {direction} the source measures frequency {f(obs,6)} Hz.',parts=[p('Determine the receiver’s speed.',step(f'Use f′ = f(v {"+"if approach else"−"} u_o)/v.','M1'),step(f'u_o = {u} m s⁻¹, to the precision of the supplied frequency.')),p('Determine the wavelength in the air.',step(f'The source is stationary, so λ = v/f = {f(lam)} m.')),p(f'In a separate experiment, the receiver stays still while the source moves {direction} it at the speed found in part (a). Calculate the detected frequency.',step(f'Apply the moving-source relation: f′ = fv/(v {"−"if approach else"+"} u_s).','M1'),step(f'f′ = {f(sourceobs)} Hz.')),p('Explain why these two experiments need not give exactly the same frequency shift.',step('For sound, source and observer speeds relative to the medium enter differently: source motion changes wavefront spacing, while observer motion changes the encounter rate with unchanged spacing.','R1'))],level='ahl',summary=f'Receiver speed {u} m s⁻¹; air wavelength {f(lam)} m')

for v in range(4):
    z=[.001,.002,-.0015,-.0025][v];rests=[400,500,650];observed=[round(x*(1+z),3)for x in rests];ratios=[(o-r)/r for o,r in zip(observed,rests)];mean=sum(ratios)/3;velocity=C*mean;newrest=580;newobs=newrest*(1+mean);kind='data-based'if v<2 else'structured'
    table='\n\n| Laboratory wavelength / nm | Observed wavelength / nm |\n|---:|---:|\n'+'\n'.join(f'| {r} | {o:.3f} |'for r,o in zip(rests,observed))
    add(30,5,v,kind,'Checking a common spectral-line shift',f'Three identified emission lines from one source are measured in a calibrated spectrum as follows. All listed values are simulated. Adopt positive radial velocity for recession and c = 3.00 × 10⁸ m s⁻¹. Use the low-speed Doppler approximation.'+table,parts=[p('Calculate the fractional wavelength shift for each line and assess whether one radial velocity can explain them.',step('For each line calculate z = (λ_observed − λ_rest)/λ_rest.','M1'),step(f'All three give z = {f(mean)}, consistent with a common radial velocity.')),p('Determine the radial velocity, including its direction.',step(f'v_radial ≈ cz = {f(velocity)} m s⁻¹, indicating {"recession"if velocity>0 else"approach"}.')),p('Predict the observed wavelength of an additional line whose laboratory wavelength is 580 nm.',step(f'λ_observed = λ_rest(1 + z) = {f(newobs,6)} nm.')),p('Explain why the approximation used is appropriate for these data.',step(f'|v|/c ≈ |z| = {f(abs(mean))}, which is much less than one, so relativistic corrections are small.','R1'))],summary=f'z = {f(mean)}; radial velocity {f(velocity)} m s⁻¹')

def validate(final=True):
    if final:
        assert len(Q)==120
        assert Counter(FAMILIES)=={i:4 for i in range(1,31)}
        assert Counter(q['questionType']for q in Q)=={'multiple-choice':48,'structured':54,'data-based':18}
        assert Counter(q['syllabusCode']for q in Q)=={f'C.{i}':24 for i in range(1,6)}
    assert len({q['stem']for q in Q})==len(Q)
    for n,q in enumerate(Q,1):
        assert q['number']==n and q['id']==f'ib-phy-c-{n:03}'
        assert q['marks']==sum(int(s['code'][1:])for g in q['markScheme']for s in g['steps'])
        if q['parts']:
            assert q['marks']==sum(z['marks']for z in q['parts'])
            for part,group in zip(q['parts'],q['markScheme']):assert part['marks']==sum(int(z['code'][1:])for z in group['steps'])
        for key in ['diagramSvg','markSchemeDiagramSvg']:
            if key in q:
                s=q[key];assert s.startswith('<svg ')and'viewBox='in s and s.endswith('</svg>')
                assert not re.search(r'<(?:script|image|style|foreignObject)|\bon\w+\s*=|(?:href|src)\s*=|url\s*\(',s,re.I)
    if final:assert sum('diagramSvg'in q for q in Q)>=20 and sum('markSchemeDiagramSvg'in q for q in Q)>=10

if __name__=='__main__':
    validate(final=len(Q)==120);OUT.parent.mkdir(parents=True,exist_ok=True);REPORT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(Q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    REPORT.write_text('\n'.join(['Theme C independent authoring report',f'{len(Q)} original question sets; {len(set(FAMILIES))} families.','Types: '+str(dict(Counter(q['questionType']for q in Q))),'Difficulty: '+str(dict(Counter(q['difficulty']for q in Q))),f"Question SVGs: {sum('diagramSvg'in q for q in Q)}; worked SVGs: {sum('markSchemeDiagramSvg'in q for q in Q)}.",'Assertions check numerical identities, all mark sums, unique stems/options, metadata, coverage, and safe vector artwork.','Synthetic data are labelled; answers use declared constants and displayed rounding.','Scope reference only: https://xmltwo.ibo.org/publications/EAD/2026_EN/GR4/GR4-Physics_EN.pdf (corrected November 2024). No copyrighted question adaptation.','Independent physics/editorial cross-review completed; see wave-behaviour-cross-review.txt. Complete rendered diagram review is recorded in diagram-visual-bc.txt; live application integration review is separate.'])+'\n',encoding='utf-8')
    print(json.dumps({'count':len(Q),'families':len(set(FAMILIES)),'types':dict(Counter(q['questionType']for q in Q)),'questionDiagrams':sum('diagramSvg'in q for q in Q),'workedDiagrams':sum('markSchemeDiagramSvg'in q for q in Q)},indent=2))
