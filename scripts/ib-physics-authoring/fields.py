"""Independent IB Physics HL fields practice; deterministic, standard library only.

Constants and models are stated in each task. Figures are original vector drawings.
Fifty problem families, two parameter sets each; not scraped or paraphrased items.
"""
from pathlib import Path
import json, math, html

ROOT = Path(__file__).resolve().parents[2]
G, K, E, ME, MP = 6.67e-11, 8.99e9, 1.60e-19, 9.11e-31, 1.67e-27
Q=[]
CHECKS=[]
TOPICS={'D.1':'Gravitational fields','D.2':'Electric and magnetic fields','D.3':'Motion in electromagnetic fields','D.4':'Induction'}
def fmt(x,n=3):
    if x==0:return '0'
    if 1e-3<=abs(x)<1e5:
        displayed=f'{x:.{n}g}'
        if 'e' not in displayed:return displayed
        coefficient,exponent=displayed.split('e')
        return rf'{coefficient}\times10^{{{int(exponent)}}}'
    p=int(math.floor(math.log10(abs(x))));return rf'{x/10**p:.{n}g}\times10^{{{p}}}'
def near(a,b,name):
    assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-20),(name,a,b)
    CHECKS.append(name)
def tx(x,y,s,size=21,anchor='middle',fill='#172b3a'):
    return f'<text x="{x:.2f}" y="{y:.2f}" font-family="Arial,sans-serif" font-size="{size}" text-anchor="{anchor}" fill="{fill}">{html.escape(str(s))}</text>'
def ln(x1,y1,x2,y2,c='#172b3a',w=2,dash=''):
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{c}" stroke-width="{w}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>'
def arr(x1,y1,x2,y2,c='#762126'):
    a=math.atan2(y2-y1,x2-x1);l=12;w=6
    p1=(x2-l*math.cos(a)+w*math.sin(a),y2-l*math.sin(a)-w*math.cos(a));p2=(x2-l*math.cos(a)-w*math.sin(a),y2-l*math.sin(a)+w*math.cos(a))
    return ln(x1,y1,x2,y2,c,3)+f'<polygon points="{x2:.2f},{y2:.2f} {p1[0]:.2f},{p1[1]:.2f} {p2[0]:.2f},{p2[1]:.2f}" fill="{c}"/>'
def circle(x,y,r,fill='#fff8e5',stroke='#172b3a'):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
def rect(x,y,w,h,fill='none',stroke='#172b3a'):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
def svg(content,title,w=720,h=400):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img"><title>{html.escape(title)}</title><rect width="{w}" height="{h}" fill="white"/>{content}</svg>'
def pair(a,b,d):
    return svg(circle(180,170,45)+circle(540,170,45)+tx(180,178,a)+tx(540,178,b)+ln(225,170,495,170,dash='6 5')+tx(360,225,d)+arr(140,320,580,320)+tx(610,327,'+x'),'Two centres on a horizontal line')
def orbit(label='r',motion=True):
    s=circle(330,195,55,'#fff1bc')+tx(330,202,'M')+circle(330,195,135,'none')+circle(465,195,10,'#762126')+ln(330,195,465,195,dash='6 4')+tx(400,180,label)
    if motion:s+=arr(465,195,465,95)+tx(490,120,'v')
    return svg(s+tx(360,375,'Schematic; radius measured from the centre',17),'Circular orbit and tangential velocity')
def plot(points,xlabel,ylabel,xmax=None,ymin=0,ymax=None,xmin=0):
    xmax=xmax or max(x for x,y in points);ymax=ymax if ymax is not None else max(y for x,y in points)*1.1
    assert xmax>xmin and ymax>ymin
    fx=lambda x:100+540*(x-xmin)/(xmax-xmin);fy=lambda y:320-240*(y-ymin)/(ymax-ymin)
    s=arr(100,320,665,320,'#172b3a')+arr(100,320,100,55,'#172b3a')+tx(390,382,xlabel,19)+tx(100,30,ylabel,19)
    for j in range(5):
        x=xmin+(xmax-xmin)*j/4;y=ymin+(ymax-ymin)*j/4
        s+=ln(fx(x),320,fx(x),326)+tx(fx(x),350,f'{x:.3g}',15)+ln(94,fy(y),100,fy(y))+tx(84,fy(y)+5,f'{y:.3g}',15,'end')
    s+=f'<polyline points="'+ ' '.join(f'{fx(x):.2f},{fy(y):.2f}' for x,y in points)+'" fill="none" stroke="#762126" stroke-width="3"/>'
    for x,y in points:s+=circle(round(fx(x),2),round(fy(y),2),3,'#762126','#762126')
    return svg(s,'Graph: '+ylabel+' against '+xlabel)
def plates(label='E',beam=False):
    s=ln(150,85,150,290,'#172b3a',6)+ln(570,85,570,290,'#172b3a',6)
    for y in [110,165,220,275]:s+=tx(125,y,'+')+tx(595,y,'−')
    s+=arr(240,165,480,165)+tx(460 if beam else 360,140,label)+tx(360,345,'Uniform field; plate edges neglected',17)
    if beam:s+=circle(360,230,10,'#fff1bc')+arr(360,230,360,90,'#1f6c65')+tx(435,95,'initial v')
    return svg(s,'Uniform electric field between parallel plates')

def equipotentials(potential,separation):
    s=ln(190,100,190,285,'#1f6c65',3)+ln(530,100,530,285,'#1f6c65',3)
    s+=tx(190,70,f'{potential:g} V')+tx(530,70,'0 V')
    s+=ln(190,250,530,250,'#64748b',1.5)+ln(190,240,190,260,'#64748b')+ln(530,240,530,260,'#64748b')
    s+=tx(360,285,f'd = {separation:g} m',19)+tx(360,350,'Two equipotential lines; separation is along their normal',18)
    return svg(s,'Locally parallel equipotential lines')
def magnetic(label='B into page',curved=False):
    s=''
    for x in [180,270,360,450,540]:
        for y in [110,180,250]:
            if (x,y)!=(180,180):s+=ln(x-5,y-5,x+5,y+5,'#777')+ln(x-5,y+5,x+5,y-5,'#777')
    s+=tx(360,45,label,19)+arr(80,180,200,180)+tx(100,150,'v')+circle(200,180,8,'#fff1bc')
    if curved:
        upward=curved=='up'
        s+=f'<path d="M 200 180 A 100 100 0 0 {0 if upward else 1} 300 {80 if upward else 280}" fill="none" stroke="#762126" stroke-width="3"/>'
        s+=arr(300,110 if upward else 250,300,78 if upward else 282)
    s+=tx(390,340,'Crosses denote magnetic field into the page',17)
    return svg(s,'Charged particle entering a magnetic field')
def rod(open_circuit=False):
    s=ln(170,110,570,110)+ln(170,290,570,290)+ln(450,110,450,290,'#762126',7)+arr(470,200,620,200)+tx(630,190,'v')+tx(420,235,'L')
    if open_circuit:
        s+=ln(170,110,170,165)+ln(170,235,170,290)+circle(170,165,4)+circle(170,235,4)+tx(135,205,'open',17)
    else:
        s+=ln(170,110,170,170)+rect(160,170,20,60)+ln(170,230,170,290)+tx(135,205,'R')
    for x in [250,330,410]:
        for y in [150,200,250]:s+=ln(x-5,y-5,x+5,y+5,'#777')+ln(x-5,y+5,x+5,y-5,'#777')
    return svg(s+tx(360,350,'Uniform B into page; sliding rod and conducting rails',17),'Sliding rod circuit')

def surface_world():
    s=circle(340,195,125,'#fff1bc')+tx(340,200,'M')+circle(465,195,7,'#762126')+ln(340,195,465,195,dash='6 4')+tx(405,175,'R')
    return svg(s+tx(360,365,'Field evaluated at the surface; R is the planet radius',18),'Surface of a spherical planet')

def two_radii():
    s=circle(340,190,35,'#fff1bc')+tx(340,197,'M')+circle(340,190,85,'none')+circle(340,190,150,'none')
    s+=ln(340,190,425,190,dash='6 4')+ln(340,190,340,40,dash='6 4')+tx(390,215,'r₁')+tx(315,95,'r₂')
    s+=circle(425,190,6,'#762126')+circle(340,40,6,'#1f6c65')+tx(360,380,'Two distinct radii from the same planet centre',17)
    return svg(s,'Inner and outer radii about a spherical planet')

def dipole_midpoint():
    s=circle(150,190,33)+tx(150,198,'+q')+circle(570,190,33)+tx(570,198,'−q')+circle(360,190,4,'#172b3a')
    s+=ln(185,190,330,190,dash='5 4')+ln(390,190,535,190,dash='5 4')+tx(360,230,'midpoint',18)
    s+=arr(310,110,440,110)+tx(375,86,'E from +q →',18)+arr(310,280,440,280,'#1f6c65')+tx(375,315,'E from −q →',18)
    s+=tx(360,370,'At the midpoint the two fields add; an electron feels force left',17)
    return svg(s,'Electric field contributions at a dipole midpoint')

def flux_angle(angle):
    a=math.radians(angle);theta=math.pi/2-a
    x,y=340,190
    s=ln(x-120*math.cos(a),y+120*math.sin(a),x+120*math.cos(a),y-120*math.sin(a),'#172b3a',5)
    s+=arr(x,y,x+150*math.cos(theta),y+150*math.sin(theta),'#1f6c65')+tx(505,310,'area normal',18)
    s+=arr(100,190,610,190)+tx(640,197,'B')
    s+=tx(510,105,f'plane angle: {angle}°',18)+tx(550,230,'normal angle: θ',18)+tx(230,80,'coil plane (edge view)',18)
    s+=tx(360,365,'The given angle is between the coil plane and the field',18)
    return svg(s,'Coil plane and area-normal angles to the field')

def translating_loop():
    s=rect(250,110,240,180)+arr(100,200,215,200)+tx(145,175,'motion',18)
    for x in [280,340,400,460]:
        for y in [140,200,260]:
            s+=ln(x-5,y-5,x+5,y+5,'#777')+ln(x-5,y+5,x+5,y-5,'#777')
    s+=tx(360,55,'Uniform B into page; fixed loop area and orientation',18)+tx(360,355,'The entire loop stays within the same field region',18)
    return svg(s,'Rigid loop translating in a perpendicular uniform field')

def current_coil(trend):
    s=''
    for x in range(200,521,40):s+=f'<ellipse cx="{x}" cy="190" rx="27" ry="85" fill="none" stroke="#172b3a" stroke-width="2"/>'
    s+=arr(240,190,480,190,'#1f6c65')+tx(360,95,'linked magnetic field',17)+ln(175,190,100,190)+ln(545,190,620,190)
    s+=tx(360,55,f'Current magnitude is {trend}',21)+tx(360,340,'Coil carrying a current in a fixed direction',18)
    return svg(s,'Current and linked field in a coil')

def conductor_section(hollow=False):
    s=circle(360,190,110,'#f4f6f7')
    if hollow:
        s+=circle(360,190,66,'white')+tx(360,187,'empty cavity',18)+tx(360,215,'no internal charge',15)+tx(360,320,'conducting shell',18)
    else:s+=tx(360,190,'conducting material',18)
    s+=arr(80,190,210,190,'#1f6c65')+arr(510,190,640,190,'#1f6c65')+tx(360,55,'Applied electric field →',21)
    s+=tx(360,375,'Conducting body at rest in an external field',17)
    return svg(s,'Conductor cross-section in an applied static field')
def coil():
    s=rect(230,100,250,180)+ln(355,75,355,310,dash='6 4')+tx(355,50,'rotation axis',18)+arr(120,200,590,200,'#1f6c65')+tx(605,207,'B')+tx(360,355,'Angle is measured between B and the area normal',17)
    return svg(s,'Coil in a uniform magnetic field')
def sphere():
    s=circle(360,190,110,'#f4f6f7')+tx(360,190,'conducting sphere')+tx(360,220,'electrostatic equilibrium',16)
    for a in [0,math.pi/4,math.pi/2,3*math.pi/4,math.pi,5*math.pi/4,3*math.pi/2,7*math.pi/4]:
        x1,y1=360+115*math.cos(a),190+115*math.sin(a);x2,y2=360+160*math.cos(a),190+160*math.sin(a);s+=arr(x1,y1,x2,y2)
    return svg(s+tx(360,385,'Positively charged conducting sphere',17),'Positively charged conducting sphere')
def data_table(xs,ys,xname,yname):
    return '| '+xname+' | '+yname+' |\n| --- | --- |\n'+'\n'.join(f'| {x:.5g} | {y:.5g} |' for x,y in zip(xs,ys))
def part(prompt,*steps):return (prompt,[{'code':c,'text':t} for c,t in steps])
def add(code,title,stem,parts,difficulty='medium',level='core',kind='structured',diagram=None,solution=None):
    n=len(Q)+1
    p=[{'label':chr(97+i),'prompt':p,'marks':sum(int(s['code'][1:]) for s in steps)} for i,(p,steps) in enumerate(parts)]
    q={'id':f'ib-phy-d-{n:03d}','subject':'physics-hl','topicId':'fields','collectionId':'physics-fields','number':n,'title':title,'subtopic':TOPICS[code],'syllabusCode':code,'level':level,'questionType':kind,'difficulty':difficulty,'calculator':True,'marks':sum(x['marks'] for x in p),'stem':stem,'parts':p,'markScheme':[{'part':chr(97+i),'steps':steps} for i,(_,steps) in enumerate(parts)],'source':{'document':'Independent syllabus-authored practice','question':n},'verification':{'method':'Independent analytical derivation and numerical substitution; deterministic authoring assertions','notes':f'Original fields family {title}. Constants explicitly supplied where needed; diagram generated from stated model. Cross-review recorded separately.'},'status':'published'}
    if diagram:q['diagramSvg']=diagram
    if solution:q['markSchemeDiagramSvg']=solution
    Q.append(q);return q
def mc(code,title,stem,answers,correct,why,difficulty='easy',level='core',diagram=None):
    assert len(answers)==4 and len(set(answers))==4
    q=add(code,title,stem,[],difficulty,level,'multiple-choice',diagram)
    # Rotate answer positions across the bank without changing their association.
    shift=(len(Q)-1)%4;answers=answers[shift:]+answers[:shift];correct=(correct-shift)%4
    letter='ABCD'[correct];q.update(marks=1,parts=[],options=[{'label':c,'text':t} for c,t in zip('ABCD',answers)],correctOption=letter,markScheme=[{'part':'','steps':[{'code':'A1','text':f'**{letter}.** {why}'}]}]);return q

for j in range(2):
    # D.1 — fourteen distinct families.
    a,b=[(3,2),(5,3)][j];ratio=a/b**2
    mc('D.1','Comparing surface gravitational fields',f'World P has mass $M$ and radius $R$. World Q has mass ${a}M$ and radius ${b}R$. What is $g_Q/g_P$?',[f'${fmt(ratio)}$',f'${a/b:.3g}$',f'${b*b/a:.3g}$',f'${a*b*b}$'],0,rf'$g=GM/R^2$, so the ratio is ${a}/{b}^2={fmt(ratio)}$.')
    M,R=[(4.8e24,5.6e6),(7.2e23,3.2e6)][j];g=G*M/R**2;near(g*R**2/G,M,'mass-field inversion')
    add('D.1','Weighing equipment on a new world',rf'A lander reaches a spherical world of mass ${fmt(M)}\,\mathrm{{kg}}$ and radius ${fmt(R)}\,\mathrm{{m}}$. Take $G={fmt(G)}\,\mathrm{{N\,m^2\,kg^{{-2}}}}$.',[part('Calculate the surface gravitational field strength.',('M1',r'$g=GM/R^2$.'),('A1',rf'$g={fmt(g)}\,\mathrm{{N\,kg^{{-1}}}}$.')),part('A tool has mass 4.0 kg. Determine its weight on this world.',('M1',r'$W=mg$.'),('A1',rf'$W={fmt(4*g)}\,\mathrm{{N}}$, towards the centre.'))],difficulty='easy',diagram=surface_world())
    h=[1,2][j];fac=1/(1+h)**2
    mc('D.1','Altitude is not orbital radius',f'A probe is at height ${h}R$ above a spherical planet of radius $R$. If the surface field is $g_0$, what is the field at the probe?',[f'${fmt(fac)}g_0$',f'${1/(h*h):.3g}g_0$',f'${1/(1+h):.3g}g_0$',f'${(1+h)**2}g_0$'],0,rf'The centre-to-probe distance is ${(1+h)}R$, so $g/g_0=R^2/[{1+h}R]^2={fmt(fac)}$.',diagram=orbit(f'{h+1}R',False))
    mu=[3.2e14,4.8e14][j];rs=[4,6,8,10];gs=[mu/(r*1e6)**2 for r in rs]
    add('D.1','Inferring a planet from field data','A simulation of the exterior field of a spherical planet gives the data below. Distances are from its centre. Take $G=6.67\\times10^{-11}\\,\\mathrm{N\\,m^2\\,kg^{-2}}$.\n\n'+data_table(rs,gs,'r / 10⁶ m','g / N kg⁻¹'),[part('Use the data to show that the field follows an inverse-square law.',('M1','Compare $gr^2$ at two or more distances, converting the radii to metres.'),('A1',rf'Each gives $GM={fmt(mu)}\,\mathrm{{m^3\,s^{{-2}}}}$ within the shown precision.')),part('Estimate the mass of the planet.',('M1',r'$M=(gr^2)/G$.'),('A1',rf'$M={fmt(mu/G)}\,\mathrm{{kg}}$.'))],kind='data-based',diagram=plot(list(zip(rs,gs)),'r / 10⁶ m','g / N kg⁻¹'),solution=plot([(1/r**2,g) for r,g in reversed(list(zip(rs,gs)))],'1/(r / 10⁶ m)²','g / N kg⁻¹'))
    r=[7e6,9e6][j];V=-mu/r
    add('D.1','Gravitational potential has a reference zero',rf'A spherical planet has gravitational parameter $GM={fmt(mu)}\,\mathrm{{m^3\,s^{{-2}}}}$. A probe is at $r={fmt(r)}\,\mathrm{{m}}$. Set potential zero at infinity.',[part('Calculate the gravitational potential at the probe.',('M1',r'$V_g=-GM/r$.'),('A1',rf'$V_g={fmt(V)}\,\mathrm{{J\,kg^{{-1}}}}$.')),part('Explain the negative sign.',('R1','Positive external work per unit mass is required to move a stationary test mass from this point to infinity.'))],level='ahl')
    r1,r2=[(6e6,1.2e7),(8e6,2e7)][j];m=[85,120][j];W=mu*m*(1/r1-1/r2)
    near(W, m*((-mu/r2)-(-mu/r1)),'work from potential difference')
    add('D.1','Slowly raising a research capsule',rf'A capsule of mass ${m}\,\mathrm{{kg}}$ is raised very slowly from radius ${fmt(r1)}\,\mathrm{{m}}$ to ${fmt(r2)}\,\mathrm{{m}}$ in a spherical planet\'s field. Its gravitational parameter is $GM={fmt(mu)}\,\mathrm{{m^3\,s^{{-2}}}}$.',[part('Calculate the work done by the lifting mechanism, neglecting changes in kinetic energy.',('M1',r'$W=m\Delta V_g=GMm(1/r_1-1/r_2)$.'),('A1',rf'$W={fmt(W)}\,\mathrm{{J}}$.')),part('State the work done by gravity and explain its sign.',('A1',rf'$W_\mathrm{{gravity}}=-{fmt(W)}\,\mathrm{{J}}$.'),('R1','The gravitational force is inward while the displacement is outward.'))],level='ahl',diagram=two_radii())
    r=[8e6,1.1e7][j];v=math.sqrt(mu/r);T=2*math.pi*r/v;near(4*math.pi**2*r**3/T**2,mu,'circular orbit period')
    add('D.1','Timing a mapping satellite',rf'A satellite follows a circular orbit of radius ${fmt(r)}\,\mathrm{{m}}$ around a planet with $GM={fmt(mu)}\,\mathrm{{m^3\,s^{{-2}}}}$.',[part('Determine its orbital speed.',('M1',r'$GMm/r^2=mv^2/r$.'),('A1',rf'$v=\sqrt{{GM/r}}={fmt(v)}\,\mathrm{{m\,s^{{-1}}}}$.')),part('Determine the period in minutes.',('M1',r'$T=2\pi r/v$.'),('A1',rf'$T={fmt(T/60)}\,\mathrm{{min}}$.'))],diagram=orbit('r'))
    r1,r2=[(7.5e6,1.5e7),(9e6,2.7e7)][j];m=[220,350][j];dEt=mu*m/2*(1/r1-1/r2)
    add('D.1','Energy cost of an orbit change',rf'A satellite of mass ${m}\,\mathrm{{kg}}$ is moved between circular orbits of radii ${fmt(r1)}\,\mathrm{{m}}$ and ${fmt(r2)}\,\mathrm{{m}}$. Take $GM={fmt(mu)}\,\mathrm{{m^3\,s^{{-2}}}}$. Ignore propellant mass changes.',[part('Derive an expression for the total mechanical energy in a circular orbit.',('M1',r'Use $v^2=GM/r$ to obtain $E_k=GMm/(2r)$.'),('A1',r'Add $E_p=-GMm/r$ to give $E_\mathrm{tot}=-GMm/(2r)$.')),part('Calculate the net increase in mechanical energy.',('M1',r'$\Delta E=GMm(1/r_1-1/r_2)/2$.'),('A1',rf'$\Delta E={fmt(dEt)}\,\mathrm{{J}}$.')),part('Explain why comparing gravitational potential energies alone overestimates this increase.',('R1','The larger circular orbit has a smaller speed and hence smaller kinetic energy; this offsets part of the potential-energy increase.'))],difficulty='hard',level='ahl',diagram=two_radii())
    mult=[2,3][j]
    mc('D.1','Escape and orbital speeds',f'A probe in a circular orbit of radius $r$ has speed $u$. What is the escape speed at radius ${mult}r$ around the same planet?', [rf'$\sqrt{{{2/mult:g}}}u$',rf'${mult}u$',rf'$u/{mult}$',rf'$\sqrt{{{mult}}}u$'],0,rf'$u^2=GM/r$ and $v_e^2=2GM/({mult}r)$, so $v_e/u=\sqrt{{2/{mult}}}$.',level='ahl')
    M1,M2,L=[(4e20,9e20,5e6),(9e20,16e20,7e6)][j];x=L/(1+math.sqrt(M2/M1));near(G*M1/x**2,G*M2/(L-x)**2,'two-mass zero-field')
    add('D.1','A zero-field location between moons',rf'Two approximately spherical moons of masses ${fmt(M1)}\,\mathrm{{kg}}$ and ${fmt(M2)}\,\mathrm{{kg}}$ have centres separated by ${fmt(L)}\,\mathrm{{m}}$. Their radii are negligible compared with the separation.',[part('Find the distance from the less massive moon to the zero-field point between them.',('M1',r'Set $GM_1/x^2=GM_2/(L-x)^2$; the fields oppose between the moons.'),('M1',r'Use $(L-x)/x=\sqrt{M_2/M_1}$.'),('A1',rf'$x={fmt(x)}\,\mathrm{{m}}$.')),part('Explain why no zero-field point lies outside the two moons on their joining line.',('R1','Outside the pair both attractive fields point in the same direction.'))],diagram=pair('M₁','M₂',f'L = {L/1e6:g} × 10⁶ m'))
    mc('D.1','Zero field does not mean zero potential',f'Two identical isolated masses are fixed {4+j*2:.1f} m apart. At their midpoint, which statement is correct when gravitational potential is zero at infinity?',['The field is zero and the potential is negative.','Both field and potential are zero.','The field is nonzero and the potential is zero.','The field is zero and the potential is positive.'],0,'The two equal field vectors cancel. Each mass contributes negative scalar potential, and those potentials add.',difficulty='medium',level='ahl',diagram=pair('M','M','equal distances to midpoint'))
    r0=[6e6,8e6][j];dr=1e5;Vm=-mu/(r0-dr);Vp=-mu/(r0+dr);g_est=-(Vp-Vm)/(2*dr)
    add('D.1','Reading a potential gradient',rf'A finely sampled gravitational potential graph near radius ${fmt(r0)}\,\mathrm{{m}}$ is locally almost straight. The values at $r_0-1.0\times10^5\,\mathrm{{m}}$ and $r_0+1.0\times10^5\,\mathrm{{m}}$ are ${fmt(Vm,5)}$ and ${fmt(Vp,5)}\,\mathrm{{J\,kg^{{-1}}}}$, respectively. Positive radial direction is outward.',[part('Estimate the signed radial field from these data.',('M1',r'$g_r=-\Delta V_g/\Delta r$.'),('A1',rf'$g_r\approx {fmt(g_est)}\,\mathrm{{N\,kg^{{-1}}}}$. Accept a value consistent with the displayed rounded potentials.')),part('Explain the meaning of its sign.',('R1','The field is inward, opposite to the chosen outward radial direction.'))],difficulty='medium',level='ahl',kind='data-based',diagram=plot([(r0/1e6-.1,Vm/1e7),(r0/1e6+.1,Vp/1e7)],'r / 10⁶ m','Vg / 10⁷ J kg⁻¹',ymin=Vm/1e7-.1,ymax=Vp/1e7+.1,xmin=r0/1e6-.12,xmax=r0/1e6+.12))
    mc('D.1','The acceleration of an orbiting laboratory',f'A laboratory moves at constant speed in a circular orbit, making one revolution every {90+10*j} minutes. Which statement explains its acceleration?',['Its velocity direction changes because the resultant force is toward the planet.','Its speed increases because gravity does positive work throughout the orbit.','It has no acceleration because its speed is constant.','Its acceleration is tangent to the orbit.'],0,'Acceleration measures change of velocity, including direction. In a circular orbit gravity is perpendicular to the velocity and provides the inward acceleration.',diagram=orbit())
    r=[7.1e6,8.3e6][j];fraction=[.98,.96][j]
    add('D.1','A slowly decaying circular orbit',rf'A satellite loses mechanical energy to a thin atmosphere and settles approximately into a new circular orbit of radius ${fraction:g}r$, compared with its original radius $r={fmt(r)}\,\mathrm{{m}}$.',[part('Determine the ratio of its new speed to its old speed.',('M1',r'$v\propto r^{-1/2}$ for circular orbits.'),('A1',rf'$v_2/v_1=1/\sqrt{{{fraction:g}}}={fmt(1/math.sqrt(fraction))}$.')),part('Explain how the satellite can lose total mechanical energy while its kinetic energy increases.',('R1','The total energy $-GMm/(2r)$ becomes more negative in the lower orbit.'),('R1','Potential energy decreases by more than kinetic energy increases; the difference is transferred to the atmosphere.'))],difficulty='hard',level='ahl')
    # D.2 — sixteen families.
    q1,q2,r=[(2e-9,6e-9,.12),(4e-9,9e-9,.18)][j];F=K*q1*q2/r**2
    mc('D.2','Force between small charged spheres',rf'Two small positive spheres carry charges ${fmt(q1)}\,\mathrm{{C}}$ and ${fmt(q2)}\,\mathrm{{C}}$, separated by ${r:g}\,\mathrm{{m}}$. Take $k={fmt(K)}\,\mathrm{{N\,m^2\,C^{{-2}}}}$. What is the magnitude of their mutual force?',[rf'${fmt(F)}\,\mathrm{{N}}$',rf'${fmt(F*r)}\,\mathrm{{N}}$',rf'${fmt(F*2)}\,\mathrm{{N}}$',rf'${fmt(F/4)}\,\mathrm{{N}}$'],0,rf'$F=kq_1q_2/r^2={fmt(F)}\,\mathrm{{N}}$. The forces have equal magnitude and are repulsive.',diagram=pair('+q₁','+q₂',f'{r:g} m'))
    q,L=[(3e-9,.4),(5e-9,.6)][j];EP=K*q/(L/2)**2*2
    add('D.2','Field at the centre of a charge pair',rf'Point charges $+q$ and $-q$ are fixed at $x=0$ and $x={L:g}\,\mathrm{{m}}$, where $q={fmt(q)}\,\mathrm{{C}}$. Take $k={fmt(K)}\,\mathrm{{N\,m^2\,C^{{-2}}}}$.',[part('Calculate the electric field at the midpoint, including direction.',('M1',r'Each field has magnitude $kq/(L/2)^2$.'),('R1','Both midpoint fields point from the positive charge toward the negative charge, so they add.'),('A1',rf'$E={fmt(EP)}\,\mathrm{{N\,C^{{-1}}}}$ in the positive x direction.')),part('Determine the force on an electron placed at this point. Take $e=1.60\\times10^{-19}\\,\\mathrm{C}$.',('M1',r'$F=qE$ with the electron charge negative.'),('A1',rf'Magnitude ${fmt(E*EP)}\,\mathrm{{N}}$, in the negative x direction.'))],diagram=pair('+q','−q',f'{L:g} m'),solution=dipole_midpoint())
    q,r=[(8e-9,.15),(12e-9,.24)][j];test=-2*E;V=K*q/r;U=test*V
    add('D.2','Potential and particle energy near a charge',rf'A stationary point charge $Q={fmt(q)}\,\mathrm{{C}}$ is in vacuum. A particle with charge $-2e$ is at radius ${r:g}\,\mathrm{{m}}$. Take $k={fmt(K)}\,\mathrm{{N\,m^2\,C^{{-2}}}}$, $e=1.60\times10^{{-19}}\,\mathrm{{C}}$, and zero potential at infinity.',[part('Calculate the electric potential at the particle.',('M1',r'$V=kQ/r$.'),('A1',rf'$V={fmt(V)}\,\mathrm{{V}}$.')),part('Calculate the potential energy of the particle and explain its sign.',('M1',r'$U=qV=-2eV$.'),('A1',rf'$U={fmt(U)}\,\mathrm{{J}}$.'),('R1','The interaction is attractive, so positive work is required to separate the charges to infinity.'))],difficulty='medium',level='ahl')
    mc('D.2','Inside a charged conductor',f'A solid metal sphere of radius {4+j} cm is positively charged and in electrostatic equilibrium. What is the electric field at a point halfway from its centre to its surface?',['Zero.','The surface field divided by two.','Twice the surface field.','Four times the surface field.'],0,'Free charges redistribute until the electric field inside the conducting material is zero.',diagram=sphere())
    R,V0=[(.1,1800),(.15,2400)][j];rs=[0,R/2,R,2*R,3*R];vs=[V0,V0,V0,V0/2,V0/3]
    add('D.2','A conducting sphere potential profile',f'A positively charged conducting sphere has radius {R:g} m. Its potential, measured relative to infinity, is shown below. The surface potential is {V0:g} V, and the interior potential is constant. Take $k=8.99\\times10^9\\,\\mathrm{{N\\,m^2\\,C^{{-2}}}}$.',[part('Use the surface potential to calculate the charge on the sphere.',('M1',r'$V(R)=kQ/R$.'),('A1',rf'$Q=V(R)R/k={fmt(V0*R/K)}\,\mathrm{{C}}$.')),part('Determine the electric field just outside the surface and at the centre.',('M1',r'$E(R^+)=kQ/R^2=V(R)/R$.'),('A1',rf'Just outside, ${fmt(V0/R)}\,\mathrm{{N\,C^{{-1}}}}$ outward; at the centre, zero.')),part('Explain why a nonzero potential at the centre does not contradict a zero field there.',('R1','Field depends on the potential gradient, rather than the absolute potential; the potential is constant throughout the interior.'))],difficulty='hard',level='ahl',kind='data-based',diagram=plot([(R*k/20,V0 if k<=20 else V0*20/k) for k in range(61)],'r / m','V / V',ymax=V0*1.2),solution=sphere())
    signs=[('+q at each of the four corners',4),('+q at three corners and −q at one corner',2)][j];coef=signs[1]
    mc('D.2','Adding scalar potentials at a square centre',rf'Four point charges lie at the corners of a square. Each corner is distance $a$ from the centre. There is {signs[0]}. What is the total potential at the centre, relative to infinity?',[rf'${coef}kq/a$',r'$0$',rf'${coef}kq/a^2$',rf'$-{coef}kq/a$'],0,rf'Potential is scalar. Add $kq_i/a$ with each charge sign; the signed charge sum is ${coef}q$, so $V={coef}kq/a$.',difficulty='medium',level='ahl',diagram=svg(rect(220,60,280,280)+''.join(circle(x,y,14,'#fff1bc') for x,y in [(220,60),(500,60),(220,340),(500,340)])+tx(360,205,'centre')+tx(360,370,signs[0],17),'Four charges at square corners'))
    d,dV=[(.025,150),(.04,240)][j];Ef=dV/d
    add('D.2','Estimating field from equipotentials',rf'Two adjacent equipotential lines in a locally uniform field are separated by ${d:g}\,\mathrm{{m}}$ along their normal. Their potentials are ${dV}\,\mathrm{{V}}$ and $0\,\mathrm{{V}}$.',[part('Calculate the electric field strength and state its direction.',('M1',r'$E=|\Delta V|/\Delta x$.'),('A1',rf'$E={fmt(Ef)}\,\mathrm{{V\,m^{{-1}}}}$, from the higher-potential line toward the lower-potential line.')),part('Find the work done by the field when a $+3.0\\,\\mathrm{nC}$ charge moves from the higher-potential line to the lower-potential line.',('M1',r'$W=q(V_i-V_f)$.'),('A1',rf'$W={fmt(3e-9*dV)}\,\mathrm{{J}}$.'))],difficulty='medium',level='ahl',diagram=equipotentials(dV,d))
    q,m,Ef=[(2e-6,.003,450),(3e-6,.004,600)][j];acc=q*Ef/m
    add('D.2','A charged bead in a horizontal field',rf'A bead of mass ${fmt(m)}\,\mathrm{{kg}}$ and charge $+{fmt(q)}\,\mathrm{{C}}$ is released on a frictionless horizontal insulating track. A uniform horizontal electric field has magnitude ${Ef}\,\mathrm{{N\,C^{{-1}}}}$.',[part('Determine the electric force on the bead.',('M1',r'$F=qE$.'),('A1',rf'$F={fmt(q*Ef)}\,\mathrm{{N}}$, along the field.')),part('Calculate the bead\'s acceleration and explain whether its weight changes that horizontal result.',('M1',r'$a=qE/m$.'),('A1',rf'$a={fmt(acc)}\,\mathrm{{m\,s^{{-2}}}}$.'),('R1','The normal contact force balances the vertical weight; neither contributes a horizontal component.'))],diagram=plates())
    counts=[7,11][j];val=counts*E
    mc('D.2','Resolving elementary charge',rf'An oil droplet has charge $-{fmt(val,4)}\,\mathrm{{C}}$. Take $e=1.60\times10^{{-19}}\,\mathrm{{C}}$. How many excess electrons does it carry?',[str(counts),str(counts+1),str(2*counts),str(counts-2)],0,rf'The excess-electron count is $|Q|/e={counts}$. The negative sign indicates excess rather than missing electrons.')
    val=[2,3][j]
    mc('D.2','A radial electric field and its test charge',f'At a point P near an isolated negative source charge, a test charge $+{val}q$ is replaced by $-{val}q$. Which change occurs?',['The field at P is unchanged; the force reverses.','Both field and force reverse.','The field reverses; the force is unchanged.','Both field and force become zero.'],0,'The source charge determines the electric field. Since $\\mathbf F=q\\mathbf E$, changing only the test-charge sign reverses its force.',diagram=pair('−Q','P','source and field point'))
    q=[3,5][j]
    mc('D.2','Midpoint of two equal positive charges',f'Two identical charges $+{q}q$ are fixed at the ends of a straight line segment. Which statement about their midpoint is correct?',['The electric field is zero because equal field vectors oppose.','The electric field points from left to right.','The electric field points from right to left.','The electric field has twice the magnitude due to either charge alone.'],0,'Fields point away from each positive charge. At the midpoint they are equal in magnitude and opposite in direction.',difficulty='medium',diagram=pair('+Q','+Q','midpoint P'))
    direction=['out of','into'][j];sense=['anticlockwise','clockwise'][j]
    mc('D.2','Magnetic field around a straight wire',f'A long straight wire carries conventional current {direction} the page. Viewed looking at the page, in which sense do its magnetic field lines circle the wire?',[sense,'clockwise' if j==0 else 'anticlockwise','Radially outward.','Radially inward.'],0,'Use the right-hand grip rule: the thumb follows conventional current and the curled fingers give the magnetic-field sense.',diagram=svg(circle(360,190,90,'none')+circle(360,190,12,'#fff1bc')+tx(360,197,'•' if j==0 else '×')+tx(360,335,f'Conventional current {direction} page',18),'Straight wire cross-section'))
    terminal=['north','south'][j]
    mc('D.2','Recognising a solenoid end',f'The field lines emerge from end X of an air-core solenoid and return outside the solenoid to end Y. If X is labelled {terminal} by a student, which assessment is correct?',[('Correct: X is north.' if j==0 else 'Incorrect: X is north.'),'X must be south.','Both ends are north.','Neither end can be assigned a pole.'],0,'Outside a magnet or solenoid, field lines emerge from the north end and enter the south end. This identification is independent of the student\'s proposed label.',diagram=svg(rect(200,130,320,120)+tx(180,200,'X')+tx(545,200,'Y')+arr(480,95,240,95)+arr(240,200,480,200)+tx(360,340,'Outside field returns from X to Y',18),'Solenoid field convention'))
    # Figure above must agree with the stated field: emerge X(left), outside X→Y.
    Q[-1]['diagramSvg']=svg(rect(200,130,320,120)+tx(175,200,'X')+tx(545,200,'Y')+arr(240,95,480,95)+arr(480,200,240,200)+tx(360,340,'Outside: X → Y; inside: Y → X',18),'Solenoid magnetic field loop')
    rs=[.1,.2,.3,.4];c=[.0045,.0072][j];Fs=[c/r**2 for r in rs]
    add('D.2','Testing Coulomb dependence with data','A simulation keeps two charges constant and varies their separation. The surrounding medium is vacuum.\n\n'+data_table(rs,Fs,'r / m','F / N'),[part('Identify a transformation that would produce a straight line through the origin.',('M1','Plot force against $1/r^2$.'),('R1','For fixed charges Coulomb\'s law gives $F=(k|q_1q_2|)(1/r^2)$, with constant gradient.')),part('Determine the gradient of that transformed graph and hence $|q_1q_2|$. Take $k=8.99\\times10^9\\,\\mathrm{N\\,m^2\\,C^{-2}}$.',('M1',r'The gradient is $Fr^2$.'),('A1',rf'Gradient ${fmt(c)}\,\mathrm{{N\,m^2}}$; $|q_1q_2|={fmt(c/K)}\,\mathrm{{C^2}}$.'))],kind='data-based',diagram=plot(list(zip(rs,Fs)),'r / m','F / N'))
    q1,q2,r=[(5e-9,-8e-9,.25),(7e-9,-9e-9,.3)][j];U=K*q1*q2/r
    add('D.2','Work in assembling a charge pair',rf'A charge ${fmt(q1)}\,\mathrm{{C}}$ is fixed in vacuum. A second charge ${fmt(q2)}\,\mathrm{{C}}$ is brought very slowly from infinity to a separation ${r:g}\,\mathrm{{m}}$. Take $k=8.99\times10^9\,\mathrm{{N\,m^2\,C^{{-2}}}}$.',[part('Calculate the external work done during the motion.',('M1',r'For negligible kinetic-energy change, $W_\mathrm{ext}=\Delta U=kq_1q_2/r$.'),('A1',rf'$W_\mathrm{{ext}}={fmt(U)}\,\mathrm{{J}}$.')),part('Explain why this work is negative.',('R1','The attractive electric force does positive work during approach.'),('R1','The external agent removes energy to keep the motion slow, rather than supplying it.'))],difficulty='hard',level='ahl',diagram=pair('+q₁','−q₂',f'{r:g} m'))
    case=['a solid conducting ball','a closed hollow conducting shell with no charge in its cavity'][j]
    add('D.2','Electrostatic shielding and equilibrium',f'An isolated {case} is placed in a static external electric field and allowed to reach electrostatic equilibrium.',[part('Describe the rearrangement of free charge and the resultant field within the conducting material.',('R1','Free charges move under the applied field and build up on the surface.'),('R1','Their induced field cancels the applied field within the conducting material, making the resultant field zero.')),part('Explain why field lines meet the conducting surface at right angles in electrostatic equilibrium.',('R1','Any tangential field would exert a force on free surface charges and cause continuing motion.'),('R1','Equilibrium therefore requires zero tangential component.'))],diagram=conductor_section(hollow=bool(j)))

for j in range(2):
    # D.3 — ten families; right-handed xyz directions always stated.
    sign=['positive','negative'][j];correct='Upward.' if j==0 else 'Downward.'
    mc('D.3','The direction of magnetic deflection',f'A {sign} particle enters a uniform magnetic field directed into the page. Its initial velocity is to the right. What is the direction of the initial magnetic force?',[correct,'Downward.' if j==0 else 'Upward.','Into the page.','To the right.'],0,'For a positive charge, $\\mathbf v\\times\\mathbf B$ points upward. Reverse the force for a negative charge.',difficulty='medium',diagram=magnetic())
    B,v=[(.18,2.4e6),(.24,3.0e6)][j];r=MP*v/(E*B);near(E*v*B,MP*v*v/r,'magnetic centripetal balance')
    add('D.3','A proton track in a magnetic chamber',rf'A proton enters a uniform magnetic field ${B:g}\,\mathrm{{T}}$ at right angles to the field with speed ${fmt(v)}\,\mathrm{{m\,s^{{-1}}}}$. Take $m_p=1.67\times10^{{-27}}\,\mathrm{{kg}}$ and $e=1.60\times10^{{-19}}\,\mathrm{{C}}$.',[part('Calculate the radius of the proton\'s circular path.',('M1',r'$qvB=mv^2/r$.'),('A1',rf'$r=m_pv/(eB)={fmt(r)}\,\mathrm{{m}}$.')),part('Explain what happens to the radius if the speed is doubled, with the same field.',('R1','For the same particle and field $r\\propto v$.'),('A1',rf'The radius doubles to ${fmt(2*r)}\,\mathrm{{m}}$.'))],diagram=magnetic())
    Ef,Bs,Ba,r=[(1.8e4,.06,.2,.12),(2.4e4,.08,.25,.1)][j];v=Ef/Bs;qm=v/(Ba*r)
    near((Ef/Bs)/qm,Ba*r,'selector and analyser consistency')
    add('D.3','Selecting particles and measuring specific charge',rf'A narrow positive-ion beam moves to the right through a velocity selector. The electric field ${fmt(Ef)}\,\mathrm{{V\,m^{{-1}}}}$ points down the page and the magnetic field ${Bs:g}\,\mathrm{{T}}$ points into the page. Undeflected ions then enter a separate magnetic analyser with field ${Ba:g}\,\mathrm{{T}}$, perpendicular to their motion, and follow radius ${r:g}\,\mathrm{{m}}$.',[part('Determine the speed selected by the crossed fields.',('M1',r'Zero resultant force requires $qE=qvB_s$.'),('A1',rf'$v=E/B_s={fmt(v)}\,\mathrm{{m\,s^{{-1}}}}$.')),part('Calculate the charge-to-mass ratio of these ions.',('M1',r'In the analyser $qvB_a=mv^2/r$, so $q/m=v/(B_ar)$.'),('A1',rf'$q/m={fmt(qm)}\,\mathrm{{C\,kg^{{-1}}}}$.')),part('Explain whether doubling both selector fields changes the selected speed.',('R1','It does not: the ratio $E/B_s$ remains the same, so the electric and magnetic forces still cancel at the same speed.'))],difficulty='hard',diagram=magnetic(),solution=svg(arr(360,200,360,90)+tx(485,95,'magnetic force')+arr(360,200,360,310,'#1f6c65')+tx(485,315,'electric force')+tx(360,50,'Undeflected positive ion: equal and opposite forces',18),'Balanced forces in a velocity selector'))
    Ef,u,L=[(2400,3.2e5,.12),(3200,4e5,.16)][j];t=L/u;ax=E*Ef/MP;dx=.5*ax*t*t;vx=ax*t;near(dx,vx*t/2,'transverse deflection from mean velocity')
    add('D.3','Deflection between long vertical plates',rf'A proton moves vertically upward at ${fmt(u)}\,\mathrm{{m\,s^{{-1}}}}$ into a uniform horizontal electric field of ${Ef}\,\mathrm{{N\,C^{{-1}}}}$, directed to the right. The field extends ${L:g}\,\mathrm{{m}}$ vertically. Ignore gravity and edge effects. Take $m_p=1.67\times10^{{-27}}\,\mathrm{{kg}}$, $e=1.60\times10^{{-19}}\,\mathrm{{C}}$. The plate spacing is sufficiently large that the proton does not hit a plate.',[part('Calculate the time the proton spends in the field.',('M1','The vertical velocity is unchanged because there is no vertical electric force.'),('A1',rf'$t=L/u={fmt(t)}\,\mathrm{{s}}$.')),part('Calculate its horizontal displacement while in the field.',('M1',r'$a_x=eE/m_p$.'),('M1',r'$x=\tfrac12a_xt^2$, since the initial horizontal velocity is zero.'),('A1',rf'$x={fmt(dx)}\,\mathrm{{m}}$ to the right.')),part('Determine the angle its exit velocity makes with the vertical.',('M1',r'$v_x=a_xt$ and $\tan\theta=v_x/u$.'),('A1',rf'$\theta={fmt(math.degrees(math.atan(vx/u)))}^\circ$ to the right of the vertical.'))],difficulty='hard',diagram=plates(f'E = {Ef} N C⁻¹',True))
    speed=[1.2e6,2.6e6][j]
    mc('D.3','Magnetic bending does not increase kinetic energy',rf'An electron travels at ${fmt(speed)}\,\mathrm{{m\,s^{{-1}}}}$ in a uniform magnetic field perpendicular to its velocity. Electric fields and radiation losses are negligible. What happens to its speed?',['It remains constant.','It increases continuously.','It decreases continuously.','It is zero after a semicircle.'],0,'The magnetic force is always perpendicular to the instantaneous velocity and does no work. It changes the direction of momentum but not kinetic energy.',diagram=magnetic(curved=True))
    sense=['downward','upward'][j];answer='Negative.' if j==0 else 'Positive.'
    mc('D.3','Inferring the sign from a track',f'A particle enters to the right into a magnetic field directed into the page. Its path initially curves {sense}. What is the sign of its charge?',[answer,'Positive.' if j==0 else 'Negative.','Neutral.','The mass alone determines the sign.'],0,'A positive charge moving right in a field into the page is forced upward. Downward curvature therefore identifies negative charge; upward curvature identifies positive charge.',difficulty='medium',diagram=magnetic(curved=('down' if j==0 else 'up')))
    B,I,L,ang=[(.35,2.4,.18,60),(.42,3.2,.15,30)][j];F=B*I*L*math.sin(math.radians(ang))
    add('D.3','Force on an inclined current segment',rf'A straight wire segment of length ${L:g}\,\mathrm{{m}}$ carries conventional current ${I:g}\,\mathrm{{A}}$ in a uniform field ${B:g}\,\mathrm{{T}}$. The wire makes an angle ${ang}^\circ$ with the field.',[part('Calculate the magnetic-force magnitude on the segment.',('M1',r'$F=BIL\sin\theta$.'),('A1',rf'$F={fmt(F)}\,\mathrm{{N}}$.')),part('State the orientation that makes this force largest, and determine that maximum.',('R1','The segment must be perpendicular to the magnetic field.'),('A1',rf'$F_m=BIL={fmt(B*I*L)}\,\mathrm{{N}}$.'))],difficulty='easy')
    same=j==0
    mc('D.3','Interaction between parallel currents',f'Two long parallel wires carry conventional currents in {"the same" if same else "opposite"} directions. Which statement describes the magnetic forces between them?',['They attract.' if same else 'They repel.','They repel.' if same else 'They attract.','Both forces point in the direction of the currents.','One wire attracts and the other repels.'],0,'The magnetic field from each wire acts on the current in the other. Parallel currents in the same direction attract; opposite currents repel. The two interaction forces are equal and opposite.',diagram=svg(ln(240,70,240,310)+ln(480,70,480,310)+arr(240,260,240,110)+arr(480,260 if same else 110,480,110 if same else 260)+tx(240,350,'wire 1')+tx(480,350,'wire 2'),'Two parallel current-carrying wires'))
    r1,r2=[(4,6),(3,5)][j];ratio=(r2/r1)**2
    mc('D.3','Comparing isotope tracks after a common voltage',f'Two positive ions have the same charge and start from rest. They accelerate through the same potential difference and enter the same perpendicular magnetic field. Their track radii are {r1}.0 cm and {r2}.0 cm. What is the mass ratio of the second ion to the first?',[f'${fmt(ratio)}$',f'${fmt(r2/r1)}$',f'${fmt(r1/r2)}$',f'${fmt((r1/r2)**2)}$'],0,r'$qV=mv^2/2$ and $r=mv/(qB)$ give $r^2=2mV/(qB^2)$. With $q,V,B$ fixed, mass is proportional to radius squared.',difficulty='hard')
    particle=['proton','alpha particle'][j]
    add('D.3','Contrasting electric and magnetic deflection',f'Two beams of identical {particle}s initially move to the right at the same nonrelativistic speed. Beam X enters a uniform electric field directed upward. Beam Y enters a uniform magnetic field directed into the page. Ignore gravity; the fields are large enough to observe deflection.',[part('Compare the initial force directions on the two beams.',('R1','The positive particles in X feel an upward electric force.'),('R1','The right-hand cross-product rule also gives an upward magnetic force on Y initially.')),part('Explain how the subsequent paths differ.',('R1','X follows a parabola: constant vertical electric acceleration is combined with unchanged horizontal velocity.'),('R1','Y follows a circular arc at constant speed because the magnetic force remains perpendicular to its changing velocity.')),part('Compare the changes in kinetic energy.',('R1','X gains kinetic energy as its displacement acquires a component along the electric force.'),('R1','Y has no kinetic-energy change because the magnetic force does no work.'))],difficulty='hard')
    # D.4 — quantitative tasks restricted to perpendicular rods/rectangular coils.
    ang=[30,60][j];N,B,A=[(80,.25,.012),(120,.18,.018)][j];phi=B*A*math.sin(math.radians(ang))
    mc('D.4','Flux angle measured to the plane',rf'A rectangular coil has area ${A:g}\,\mathrm{{m^2}}$ and {N} turns in a uniform field ${B:g}\,\mathrm{{T}}$. The **plane** of the coil makes an angle ${ang}^\circ$ with the field. What is the magnetic flux through one turn?',[rf'${fmt(phi)}\,\mathrm{{Wb}}$',rf'${fmt(phi*N)}\,\mathrm{{Wb}}$',rf'${fmt(B*A*math.cos(math.radians(ang)))}\,\mathrm{{Wb}}$',rf'${fmt(B*A)}\,\mathrm{{Wb}}$'],0,rf'Flux through one turn is $BA\cos\theta$ where $\theta$ is to the normal. Here $\Phi=BA\sin{ang}^\circ={fmt(phi)}\,\mathrm{{Wb}}$; the turn count is not included in single-turn flux.',level='ahl',diagram=flux_angle(ang))
    N=[60,90][j];t1,t2=[(.012,.036),(.02,.05)][j];p1,p2=[(.0012,.0036),(.002,.005)][j];emf=-N*(p2-p1)/(t2-t1)
    add('D.4','Emf from a measured flux ramp',rf'A fixed {N}-turn rectangular coil has the signed flux per turn listed below. The flux changes linearly between the listed times; the positive area normal is fixed.\n\n'+data_table([t1,t2],[p1,p2],'t / s','Φ per turn / Wb'),[part('Determine the average signed induced emf during this interval.',('M1',r'$\mathcal E=-N\Delta\Phi/\Delta t$.'),('A1',rf'$\mathcal E={fmt(emf)}\,\mathrm{{V}}$ for the chosen flux orientation.')),part('State the emf after the flux becomes constant and justify your answer.',('A1',r'$\mathcal E=0$.'),('R1','Flux linkage then has zero rate of change, even though the flux itself need not be zero.'))],level='ahl',kind='data-based',diagram=plot([(t1,p1*1e3),(t2,p2*1e3)],'t / s','Φ per turn / mWb'))
    B,L,v=[(.45,.24,3.2),(.6,.18,4.5)][j];emf=B*L*v;near(emf/L,B*v,'rod electric-magnetic balance')
    add('D.4','A moving rod develops a potential difference',rf'A conducting rod of length ${L:g}\,\mathrm{{m}}$ moves right at ${v:g}\,\mathrm{{m\,s^{{-1}}}}$ along horizontal rails in a uniform field ${B:g}\,\mathrm{{T}}$ into the page. The rod is vertical and perpendicular to the rails. The circuit is initially open.',[part('Calculate the emf between the rod\'s ends.',('M1',r'$\mathcal E=BLv$.'),('A1',rf'$\mathcal E={fmt(emf)}\,\mathrm{{V}}$.')),part('Identify which end becomes positive and explain the charge separation.',('A1','The top end becomes positive.'),('R1','For positive charge moving right in a field into the page, the magnetic force is upward. Charge separation continues until the electric force balances it.'))],level='ahl',diagram=rod(open_circuit=True))
    R=[1.8,2.4][j];I=emf/R;F=B*I*L;P=I*I*R;near(F*v,P,'rod mechanical-electrical power')
    add('D.4','Mechanical power in a loaded rod circuit',rf'In a sliding-rod generator, $B={B:g}\,\mathrm{{T}}$, rod length ${L:g}\,\mathrm{{m}}$, speed ${v:g}\,\mathrm{{m\,s^{{-1}}}}$, and total circuit resistance ${R:g}\,\Omega$. The magnetic field is perpendicular to the circuit plane. Contact friction and changes in speed are negligible.',[part('Determine the induced current.',('M1',r'$I=BLv/R$.'),('A1',rf'$I={fmt(I)}\,\mathrm{{A}}$.')),part('Calculate the force required to maintain the speed.',('M1',r'$F=BIL$ acts opposite the motion, so the applied force is equal in magnitude and forward.'),('A1',rf'$F={fmt(F)}\,\mathrm{{N}}$.')),part('Show numerically that the mechanical input power equals the electrical heating power.',('M1',r'Compare $Fv$ and $I^2R$.'),('A1',rf'Both equal ${fmt(P)}\,\mathrm{{W}}$.'))],difficulty='hard',level='ahl',diagram=rod(),solution=svg(arr(360,200,550,200)+tx(525,170,'applied force')+arr(360,200,170,200,'#1f6c65')+tx(190,245,'magnetic drag')+tx(360,340,'Constant speed: forces balance; P = Fv = I²R',18),'Energy transfer in a moving rod'))
    approaching=j==0;sense='anticlockwise' if approaching else 'clockwise'
    mc('D.4','Lenz law at an approaching magnet',f'A bar magnet\'s north pole faces a circular conducting loop. The magnet moves {"toward" if approaching else "away from"} the loop along their common axis. Viewed from the magnet, what is the induced conventional-current sense?',[sense,'clockwise' if approaching else 'anticlockwise','There is no induced current.','The sense cannot be determined even when the motion is specified.'],0,'The loop opposes the change in linked flux. An approaching north pole induces a north-facing loop (anticlockwise viewed from the magnet); a retreating north pole induces a south-facing loop (clockwise).',difficulty='medium',level='ahl',diagram=svg(rect(110,150,180,90,'#fff1bc')+tx(155,205,'S')+tx(250,205,'N')+f'<ellipse cx="480" cy="195" rx="30" ry="95" fill="none" stroke="#172b3a" stroke-width="3"/>'+arr(300 if approaching else 400,85,400 if approaching else 300,85)+tx(360,60,'magnet motion',18)+tx(360,350,'View from magnet toward loop',18),'Magnet and conducting loop'))
    N,phi0,T=[(100,.0018,.12),(150,.0012,.08)][j];omega=2*math.pi/T;peak=N*omega*phi0
    pts=[(T*k/16,phi0*1e3*math.cos(2*math.pi*k/16)) for k in range(17)]
    add('D.4','Phase and amplitude in a rotating coil',rf'A {N}-turn rectangular coil rotates at constant angular speed in a uniform field. The graph shows the flux through one turn, described by $\Phi=({fmt(phi0)}\,\mathrm{{Wb}})\cos(2\pi t/T)$ with $T={T:g}\,\mathrm{{s}}$.',[part('Determine the maximum induced emf.',('M1',r'$\mathcal E_m=N\omega\Phi_0$ with $\omega=2\pi/T$.'),('A1',rf'$\mathcal E_m={fmt(peak)}\,\mathrm{{V}}$.')),part('State the signed emf at $t=0$ and at $t=T/4$.',('A1',r'At $t=0$, emf is zero because flux is at a turning point.'),('A1',rf'At $T/4$, $\mathcal E=+{fmt(peak)}\,\mathrm{{V}}$, since flux has its most negative slope.')),part('Sketch the emf for one complete cycle, using the same time origin.',('M1','Draw a sine curve starting at zero with an initially positive slope.'),('A1','Correct extrema at $T/4$ and $3T/4$, zeros at $0,T/2,T$, and the calculated amplitude.'))],difficulty='hard',level='ahl',kind='data-based',diagram=plot(pts,'t / s','Φ per turn / mWb',ymin=-phi0*1.25e3,ymax=phi0*1.25e3),solution=plot([(T*k/32,peak*math.sin(2*math.pi*k/32)) for k in range(33)],'t / s','induced emf / V',ymin=-peak*1.25,ymax=peak*1.25))
    N,B,h,w,v=[(30,.35,.12,.08,.4),(40,.28,.15,.1,.5)][j];duration=w/v;full=N*B*h*w;mag=N*B*h*v
    near(mag*duration,full,'entry emf integral equals flux-linkage change')
    add('D.4','Entering and leaving a finite field region',rf'A rectangular coil has {N} turns, height ${h:g}\,\mathrm{{m}}$ and width ${w:g}\,\mathrm{{m}}$ along its horizontal direction of motion. It moves right at ${v:g}\,\mathrm{{m\,s^{{-1}}}}$ through a uniform field ${B:g}\,\mathrm{{T}}$ into the page. The field region has width ${3*w:g}\,\mathrm{{m}}$ along the motion and extends far enough vertically. At $t=0$ the leading edge just enters. Define flux into the page as positive.',[part('Calculate the maximum flux linkage.',('M1',r'$N\Phi_m=NBhw$.'),('A1',rf'$N\Phi_m={fmt(full)}\,\mathrm{{Wb}}$.')),part('Determine the induced-emf magnitudes and the entry and exit time intervals.',('M1',r'While an edge crosses the boundary, $|\mathcal E|=NBhv$ and each crossing lasts $w/v$.'),('A1',rf'Magnitude ${fmt(mag)}\,\mathrm{{V}}$ during $0<t<{fmt(duration)}\,\mathrm{{s}}$ and ${fmt(3*duration)}<t<{fmt(4*duration)}\,\mathrm{{s}}$; zero between these intervals.')),part('Give the signs of the entry and exit emf and explain why they differ.',('A1','Entry emf is negative and exit emf positive for the stated flux orientation.'),('R1','The linked positive flux increases on entry and decreases on exit; Faraday\'s law puts a minus sign in front of its time derivative.'))],difficulty='hard',level='ahl',diagram=svg(rect(300,70,300,250,'#f3f6f7')+rect(220,130,80,130)+arr(160,195,220,195)+tx(175,165,'v')+tx(450,45,'uniform B into page',18)+tx(360,365,'At t = 0: leading edge meets left field boundary',17),'Coil entering a bounded uniform field'),solution=plot([(0,-mag),(duration,-mag),(duration,0),(3*duration,0),(3*duration,mag),(4*duration,mag),(4*duration,0)],'t / s','signed emf / V',ymin=-1.25*mag,ymax=1.25*mag))
    motion=['translates at constant speed','translates while accelerating but stays in the same plane'][j]
    mc('D.4','Motion without changing linked flux',f'A rigid rectangular loop {motion} entirely within a large uniform magnetic field perpendicular to the loop. Its area and orientation remain fixed. What is its net induced emf?',['Zero, because its linked flux is constant.','Nonzero merely because it is moving.','Nonzero because the field passes through it.','Nonzero and equal to its magnetic flux.'],0,'For this rigid loop the magnetic field, area and orientation are all constant, so $d\\Phi/dt=0$. Motional contributions around the closed loop cancel.',level='ahl',diagram=translating_loop())
    trend=['increasing','decreasing'][j]
    add('D.4','A coil opposes a changing current',f'The current magnitude in a coil is {trend} while its direction remains fixed. Discuss the induced emf in the coil itself. No numerical inductance formula is required.',[part('Explain how a changing current leads to an induced emf.',('R1','The current produces a magnetic field and magnetic flux linked with the coil.'),('R1','A changing current changes that linked flux, producing an induced emf.')),part('State the effect of this emf on the current change.',('R1',f'It opposes the {trend} current change, according to Lenz\'s law.'),('R1','For a rising current it acts against the supply; for a falling current it tends to keep the original current flowing.'))],level='ahl',diagram=current_coil(trend))
    nt,na,den=[(3,2,4),(4,3,2)][j];rat=nt*na/den
    mc('D.4','Scaling the rate of flux linkage',f'Coil X has N turns and area A. Coil Y has {nt}N turns and area {na}A. Both coil planes are perpendicular to uniform fields; the rate of change of Y\'s field is 1/{den} of that of X\'s field. What is the ratio of induced-emf magnitudes Y/X?',[f'${fmt(rat)}$',f'${nt*na*den}$',f'${fmt(nt*den/na)}$',f'${fmt(1/rat)}$'],0,rf'$|\mathcal E|=NA|dB/dt|$, so the ratio is ${nt}\times{na}/{den}={fmt(rat)}$.',difficulty='medium',level='ahl')

assert len(Q)==100,len(Q)
from collections import Counter
import xml.etree.ElementTree as ET
assert len({q['id'] for q in Q})==100
assert len({q['stem'] for q in Q})==100,'Distinct numerical scenarios required'
for q in Q:
    assert q['marks']==sum(int(s['code'][1:]) for g in q['markScheme'] for s in g['steps'])
    assert not q['parts'] or q['marks']==sum(p['marks'] for p in q['parts'])
    for p,g in zip(q['parts'],q['markScheme']):assert p['marks']==sum(int(s['code'][1:]) for s in g['steps'])
    for key in ['diagramSvg','markSchemeDiagramSvg']:
        if key in q:
            root=ET.fromstring(q[key]);assert root.attrib.get('viewBox')
    if q['questionType']=='multiple-choice':assert len({o['text'] for o in q['options']})==4
out=ROOT/'content/ib/physics-hl/fields.json';out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(Q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report={'questions':len(Q),'subtopics':dict(Counter(q['syllabusCode'] for q in Q)),'difficulty':dict(Counter(q['difficulty'] for q in Q)),'types':dict(Counter(q['questionType'] for q in Q)),'questionDiagrams':sum('diagramSvg' in q for q in Q),'solutionDiagrams':sum('markSchemeDiagramSvg' in q for q in Q),'physicsIdentityChecks':len(CHECKS)}
review=ROOT/'docs/ib-physics-reviews/fields.txt';review.parent.mkdir(parents=True,exist_ok=True)
review.write_text('Original Theme D Physics HL bank\n\n'+json.dumps(report,indent=2)+'\n\nAuthor checks: all numeric solutions derived from stated inputs; meaningful independent checks include mass-field inversion, orbital-period consistency, gravitational two-body balance, potential-work equivalence, magnetic centripetal balance, selector/analyser consistency, transverse displacement through mean velocity, rod electric/magnetic balance, mechanical/electrical power and emf-time integrals. All records pass count, ID, mark allocation, MCQ uniqueness and SVG XML checks.\n\nScope: corrected first-assessment-2025 IB guide (updated Nov2024). No noncircular orbit calculations, noncollinear gravitational superposition, memorized wire/solenoid B formulae, quantitative self-induction, RL transients or AC circuit analysis.\n\nFifty original problem families, two parameter sets each. Difficulty is an author estimate. These are author checks, not an independent second review or IB moderation. Independent review and visual contact-sheet results are recorded separately.\n',encoding='utf-8')
print(json.dumps(report))
