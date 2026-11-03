"""Thirty-five original hard R3 questions, first-assessment-2025 Chemistry.
Run from any directory. Standard-library-only; writes only this batch and its
author evidence, never an existing bank. All output uses UTF-8/LF.
"""
from pathlib import Path
import math,json,html,re,hashlib,collections,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
QUESTIONS=[];REVIEWS=[]
TITLES={'R3.1':'Proton transfer reactions','R3.2':'Electron transfer reactions','R3.3':'Electron sharing reactions','R3.4':'Electron-pair sharing reactions'}
KW=1e-14
def esc(x):return html.escape(str(x))
def text(x,y,t,size=16,anchor='middle'):
 return f'<text x="{x:g}" y="{y:g}" text-anchor="{anchor}" font-family="Arial,sans-serif" font-size="{size}" fill="#111" stroke="none">{esc(t)}</text>'
def line(x1,y1,x2,y2,dash=False):
 return f'<path d="M{x1:g} {y1:g}L{x2:g} {y2:g}" fill="none" stroke="#111" stroke-width="2"'+(' stroke-dasharray="5 4"' if dash else '')+'/>'
def dot(x,y):return f'<circle cx="{x:g}" cy="{y:g}" r="2.5" fill="#111"/>'
def pair(x,y,horizontal=True):return dot(x-4 if horizontal else x,y if horizontal else y-4)+dot(x+4 if horizontal else x,y if horizontal else y+4)
def svg(body,title):
 return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 420" role="img" aria-label="'+esc(title)+'"><rect width="640" height="420" fill="white"/>'+text(320,26,title,18)+body+'</svg>'
def curly(start,c1,c2,end,fish=False):
 x,y=end;dx=x-c2[0];dy=y-c2[1];norm=math.hypot(dx,dy);ux=dx/norm;uy=dy/norm
 b=f'<path d="M{start[0]:g} {start[1]:g}C{c1[0]:g} {c1[1]:g} {c2[0]:g} {c2[1]:g} {x:g} {y:g}" fill="none" stroke="#111" stroke-width="2"/>'
 if fish:return b+line(x,y,x-10*ux+5*uy,y-10*uy-5*ux)
 return b+f'<path d="M{x:g} {y:g}L{x-10*ux+5*uy:g} {y-10*uy-5*ux:g}L{x-10*ux-5*uy:g} {y-10*uy+5*ux:g}Z" fill="#111"/>'
def arrow(a,b):return curly(a,(a[0]+(b[0]-a[0])/3,a[1]),(a[0]+2*(b[0]-a[0])/3,b[1]),b)
def chart(title,points,xlabel,ylabel,xrange=None,yrange=None,extra=()):
 xr=xrange or (min(x for x,y in points),max(x for x,y in points));yr=yrange or (0,max(y for x,y in points)*1.12)
 X=lambda x:100+470*(x-xr[0])/(xr[1]-xr[0]);Y=lambda y:340-260*(y-yr[0])/(yr[1]-yr[0])
 b=line(100,70,100,340)+line(100,340,580,340)+text(340,397,xlabel,15)
 b+='<text x="22" y="205" transform="rotate(-90 22 205)" text-anchor="middle" font-family="Arial,sans-serif" font-size="15">'+esc(ylabel)+'</text>'
 for i in range(6):
  x=xr[0]+i*(xr[1]-xr[0])/5;y=yr[0]+i*(yr[1]-yr[0])/5
  b+=line(X(x),340,X(x),345)+text(X(x),365,f'{x:.3g}',13)+line(95,Y(y),100,Y(y))+text(90,Y(y)+5,f'{y:.3g}',13,'end')
 if yr[0]<0<yr[1]:b+=line(100,Y(0),570,Y(0),True)
 def path(pts,dash=False):
  return '<polyline points="'+' '.join(f'{X(x):.2f},{Y(y):.2f}' for x,y in pts)+'" fill="none" stroke="#111" stroke-width="2"'+(' stroke-dasharray="6 4"' if dash else '')+'/>'
 b+=path(points)
 for label,pts in extra:b+=path(pts,True)+text(X(pts[-1][0])-8,Y(pts[-1][1])-12,label,13,'end')
 return svg(b,title)
def curve(title,fn,xr,xlabel,ylabel,yr=None,extra=()):
 return chart(title,[(xr[0]+(xr[1]-xr[0])*i/240,fn(xr[0]+(xr[1]-xr[0])*i/240)) for i in range(241)],xlabel,ylabel,xr,yr,extra)
def titration_pH(v,ca=.1,va=25,cb=.1,ka=None):
 # mL units cancel in concentrations. Full numerical charge balance is used for
 # a physically valid drawing; students use the stated permitted approximations.
 acid=ca*va/(va+v);sodium=cb*v/(va+v)
 if ka is None:
  excess=acid-sodium
  if abs(excess)<1e-12:return 7.
  return -math.log10(excess) if excess>0 else -math.log10(KW/(-excess))
 lo,hi=0.,14.
 for _ in range(100):
  p=(lo+hi)/2;h=10**(-p);f=h+sodium-KW/h-acid*ka/(ka+h)
  if f>0:lo=p
  else:hi=p
 return (lo+hi)/2
def titration(title,ca=.1,va=25,cb=.1,ka=None,base=False,vmax=40):
 fn=lambda v:14-titration_pH(v,ca,va,cb,ka) if base else titration_pH(v,ca,va,cb,ka)
 return curve(title,fn,(0,vmax),'Added titrant / cm3','pH',(0,14))
def cell(title,left='Zn(s)',right='Cu(s)',solutions=('Zn2+(aq)','Cu2+(aq)'),electrolytic=False):
 b=''
 if electrolytic:
  b+='<path d="M100 160V340H540V160" fill="none" stroke="#111" stroke-width="2"/><path d="M100 240H540V340H100Z" fill="#f3f3f3" stroke="none"/>'
  b+=line(180,180,180,310)+line(460,180,460,310)+line(180,180,180,85)+line(460,180,460,85)+line(180,85,280,85)+line(360,85,460,85)
  b+='<circle cx="320" cy="85" r="40" fill="white" stroke="#111" stroke-width="2"/>'
  b+=text(320,90,'DC',16)+text(270,72,'+',21)+text(370,72,'−',21)
  b+=text(180,360,left,15)+text(460,360,right,15)+text(320,280,solutions[0],16)
 else:
  for x in [75,355]:
   b+=f'<path d="M{x} 170V335H{x+210}V170" fill="none" stroke="#111" stroke-width="2"/><path d="M{x} 245H{x+210}V335H{x}Z" fill="#f3f3f3" stroke="none"/>'
  b+=line(150,175,150,300)+line(490,175,490,300)+line(150,175,150,80)+line(490,175,490,80)+line(150,80,285,80)+line(355,80,490,80)
  b+='<circle cx="320" cy="80" r="35" fill="white" stroke="#111" stroke-width="2"/>'
  b+=text(320,85,'V',18)
  b+='<path d="M250 280V185Q250 145 290 145H350Q390 145 390 185V280M265 280V185Q265 160 290 160H350Q375 160 375 185V280" fill="none" stroke="#111" stroke-width="2"/>'
  b+=text(320,132,'KNO3 salt bridge',13)+text(150,363,left,15)+text(490,363,right,15)+text(178,282,solutions[0],15)+text(460,282,solutions[1],15)
 b+=text(320,399,'Electrode materials and solutions are specified in the question.',13)
 return svg(b,title)
def chain(title,groups,double=(),notes=()):
 start=320-50*(len(groups)-1);b=''
 for i,g in enumerate(groups):
  x=start+100*i;b+=text(x,210,g,22)
  if i<len(groups)-1:
   b+=line(x+28,203,x+72,203)
   if i in double:b+=line(x+28,211,x+72,211)
 for i,n in enumerate(notes):b+=text(320,285+24*i,n,16)
 return svg(b,title)
def flask(title,labels=('acid sample','standard alkali')):
 b='<path d="M310 255H330V300L390 365Q320 390 250 365L310 300Z" fill="none" stroke="#111" stroke-width="2"/>'
 b+='<path d="M280 330H360L380 363Q320 382 260 363Z" fill="#eee" stroke="#111" stroke-width="1"/>'
 b+='<path d="M310 60H330V210L323 224V240M310 60V210L317 224V240" fill="none" stroke="#111" stroke-width="2"/>'+line(303,204,338,204)
 for i in range(7):b+=line(310,82+17*i,321,82+17*i)
 b+=text(320,410,labels[0],15)+text(320,48,labels[1],15)+text(386,208,'tap',14)
 return svg(b,title)
def radical(title='Homolytic bond fission'):
 b=text(255,205,'Cl',26)+text(385,205,'Cl',26)+line(278,196,362,196)
 for x in [255,385]:b+=pair(x,166)+pair(x,228)+pair(x-30 if x==255 else x+30,195,False)
 b+=curly((318,196),(310,130),(280,135),(272,183),True)+curly((322,196),(330,130),(360,135),(368,183),True)
 b+=text(320,100,'UV',18)+text(320,320,'The two curved arrows each have one barb.',16)
 return svg(b,title)
def nucleophile(title='Reactants for nucleophilic substitution',arrows=False,tertiary=False):
 # Explicit O-H bond and three oxygen lone pairs; primary carbon has four bonds.
 b=text(100,220,'O',24)+text(100,282,'H',22)+line(100,231,100,260)+text(126,202,'−',21)
 b+=pair(77,217,False)+pair(100,188)+pair(124,220,False)
 b+=text(335,220,'C',24)+text(470,220,'Br',24)+line(349,212,445,212)
 b+=text(335,125,'CH3' if tertiary else 'H',22)+line(335,140,335,193)
 b+=text(335,310,'CH3' if tertiary else 'H',22)+line(335,231,335,284)
 b+=text(220,220,'CH3',22)+line(248,212,320,212)
 b+=text(345,178,'δ+',16)+text(480,178,'δ−',16)
 if arrows:
  b+=curly((124,220),(155,150),(260,150),(320,204))+curly((400,212),(410,260),(455,270),(468,233))
 return svg(b,title)
def tertiary_cation(title='A candidate carbocation intermediate'):
 b=text(320,211,'C',25)+text(345,190,'+',22)
 for x,y,lab in [(210,210,'CH3'),(375,115,'CH3'),(375,305,'CH3')]:
  b+=line(320+(x-320)*.18,204+(y-204)*.18,x+(320-x)*.24,y+(204-y)*.24)+text(x,y+7,lab,23)
 return svg(b,title)
def lewis_adduct():
 b=text(210,210,'B',25)+text(90,210,'F',25)+line(110,202,193,202)+text(260,115,'F',25)+line(218,185,248,133)+text(260,305,'F',25)+line(218,220,248,280)
 b+=text(470,210,'N',25)+pair(430,202,False)+text(470,115,'H',22)+line(470,133,470,185)+text(545,250,'H',22)+line(486,215,528,240)+text(470,305,'H',22)+line(470,226,470,282)
 for x,y in [(60,210),(90,180),(90,240),(260,85),(287,115),(240,95),(260,337),(287,305),(240,325)]:
  b+=pair(x,y,horizontal=(x in [90,260]))
 b+=text(320,360,'Separate BF3 and NH3 molecules; all shown dots are valence electrons.',14)
 return svg(b,'Lewis acid/base reactants')
def composition(formula):
 if formula=='e':return {}
 tokens=re.findall(r'[A-Z][a-z]?|\d+|\(|\)',formula);stack=[collections.Counter()];i=0
 while i<len(tokens):
  t=tokens[i]
  if t=='(':stack.append(collections.Counter());i+=1
  elif t==')':
   group=stack.pop();i+=1;mult=int(tokens[i]) if i<len(tokens) and tokens[i].isdigit() else 1
   if i<len(tokens) and tokens[i].isdigit():i+=1
   for k,v in group.items():stack[-1][k]+=v*mult
  else:
   assert re.match(r'[A-Z]',t);i+=1;mult=int(tokens[i]) if i<len(tokens) and tokens[i].isdigit() else 1
   if i<len(tokens) and tokens[i].isdigit():i+=1
   stack[-1][t]+=mult
 assert len(stack)==1
 return dict(stack[0])
def num(label,actual,expected):
 assert math.isclose(actual,expected,rel_tol=1e-6,abs_tol=1e-12 if expected==0 else abs(expected)*1e-8),(label,actual,expected)
 return dict(label=label,actual=actual,expected=expected,status='passed')
def truth(label,value):
 assert value,label
 return dict(label=label,actual=True,expected=True,status='passed')
def balance(label,lhs,rhs):
 def total(side):
  a=collections.Counter();charge=0
  for coefficient,formula,z in side:
   for k,v in composition(formula).items():a[k]+=coefficient*v
   charge+=coefficient*z
  return dict(a),charge
 l,r=total(lhs),total(rhs);assert l==r,(label,l,r)
 return dict(label=label,atoms=l[0],netCharge=l[1],status='passed')
def P(prompt,*steps):return prompt,steps
def M(x):return 'M1',x
def A(x):return 'A1',x
def R(x):return 'R1',x
def add(n,title,code,stem,parts,diagram,checks,scheme_diagram=None):
 suffix='\n\nGive non-exact numerical answers to three significant figures; report pH values to three decimal places unless stated otherwise.'
 if code=='R3.1':suffix+='\n\nUnless specified otherwise, use 298 K, $K_w=1.00\\times10^{-14}$ and ideal dilute-solution assumptions.'
 q=dict(id=f'ib-chem-r3-{n}',number=n,subject='chemistry',topicId='reactivity-3',collectionId='chemistry-reactivity-3',subtopic=TITLES[code],syllabusCode=code,level='sl' if n<=714 else 'ahl',title=title,difficulty='hard',calculator=True,questionType='data-based' if code in ['R3.1','R3.2'] else 'structured',stem=stem+suffix,parts=[],markScheme=[],source=dict(document='Independent syllabus-authored practice',question=n),status='published',verification=dict(method='Original author chemical review plus executable atom/charge/electron and numerical checks',notes='Current first-assessment-2025 specification; instructional M/A/R allocation, not an official IB markscheme. Independent review required before release.'))
 for i,(prompt,steps) in enumerate(parts):
  lab=chr(97+i);marks=sum(int(c[1:]) for c,t in steps)
  q['parts'].append(dict(label=lab,prompt=prompt,marks=marks));q['markScheme'].append(dict(part=lab,steps=[dict(code=c,text=t) for c,t in steps]))
 q['marks']=sum(p['marks'] for p in q['parts'])
 assert 8<=q['marks']<=14,(n,q['marks'])
 q['diagramSvg']=diagram;q['diagramCaption']='Original chemical diagram. Use the stated quantities; apparatus and structural layouts are schematic.'
 if scheme_diagram:q['markSchemeDiagramSvg']=scheme_diagram;q['markSchemeDiagramCaption']='Electron flow and structures for the worked explanation.'
 q['answerSummary']=' '.join(t for prompt,steps in parts for c,t in steps if c=='A1')
 for d in [diagram,scheme_diagram]:
  if d:ET.fromstring(d);assert len(d)<300000 and not re.search(r'<(?:script|foreignObject|image|style|animate)|(?:href|src)=|url\s*\(',d,re.I)
 QUESTIONS.append(q);REVIEWS.append(dict(id=q['id'],scope=q['level'],code=code,checks=checks,authorStatus='passed',diagramReview='Atom valences, bond orders, formal/ionic charges, electron-pair versus single-electron arrowheads, graph axes and physical apparatus connections checked against the individual problem.'))

# SHARED SL/HL: 701--714.
ph1=-math.log10(.0006/.050);ph2=-math.log10(.0006/.250)
add(701,'A strongly acidic spill after incomplete neutralization','R3.1',
r'A spill contains $20.0\ \mathrm{cm^3}$ of $0.150\ \mathrm{mol\,dm^{-3}}$ HCl. It is mixed with $30.0\ \mathrm{cm^3}$ of $0.0800\ \mathrm{mol\,dm^{-3}}$ NaOH. Both are fully dissociated. The diagram represents the acid-to-alkali mole ratio; each filled circle represents the same amount of the specified ion. Volumes are additive.',
[P('Write the net ionic neutralization equation and determine the amount of excess reactant.',A(r'$\mathrm{H^+(aq)+OH^-(aq)\rightarrow H_2O(l)}$.'),M(r'$n(H^+)=0.00300$ mol; $n(OH^-)=0.00240$ mol.'),A(r'$0.000600$ mol of acid remains.')),
 P('Find the pH after mixing. Explain why averaging the original pH values is chemically invalid.',M(r'$[H^+]=0.000600/0.0500=0.0120\ \mathrm{mol\,dm^{-3}}$.'),A(f'pH $={ph1:.3f}$.'),R('Neutralization consumes ions; pH is logarithmic and is not an additive conserved quantity.')),
 P('The mixture is diluted to a total volume of 250 cubic centimetres. Find the new pH and explain which quantity is unchanged.',M(r'$[H^+]=0.000600/0.250=0.00240$.'),A(f'pH $={ph2:.3f}$.'),R('The excess amount of acid remains 0.000600 mol; dilution changes its concentration.'))],
svg(''.join(dot(130+48*i,150) for i in range(5))+''.join(dot(130+48*i,260) for i in range(4))+text(85,155,'H+',17)+text(80,265,'OH−',17)+text(320,350,'Before mixing: equal ion amounts per dot; spectator ions omitted.',15),'Reactive-ion inventory before mixing'),
[balance('Net neutralization',[(1,'H',1),(1,'OH',-1)],[(1,'H2O',0)]),num('Excess acid mol',.020*.150-.030*.080,.0006),num('Fivefold dilution pH change',ph2-ph1,math.log10(5))])

ca=.100*.0184/.025;oh=.100*.0002/.0436;phpast=-math.log10(KW/oh)
add(702,'Locating equivalence without confusing an end point','R3.1',
r'A $25.0\ \mathrm{cm^3}$ sample of a fully dissociated monoprotic acid is titrated with $0.100\ \mathrm{mol\,dm^{-3}}$ NaOH. The pH curve has its steepest region centred at $18.40\ \mathrm{cm^3}$. A student records an indicator end point at $18.60\ \mathrm{cm^3}$.',
[P('Determine the acid concentration from the equivalence volume and explain why equivalence is a stoichiometric condition.',M(r'$n(HA)=0.100(0.01840)=0.001840$ mol.'),A(r'$c(HA)=0.0736\ \mathrm{mol\,dm^{-3}}$.'),R('For a monoprotic acid, equivalence occurs when equal amounts of acid and hydroxide have reacted, irrespective of an indicator observation.')),
 P('Determine the pH at equivalence and at the student’s end point. Use Kw directly if hydroxide remains.',A('Equivalence pH is 7.000 at 298 K for this strong-acid/strong-base reaction.'),M(r'Excess $OH^-$ at 18.60 cm3 is $0.100(0.00020)=2.00\times10^{-5}$ mol in 0.04360 dm3; use $[H^+]=K_w/[OH^-]$.'),A(f'End-point pH $={phpast:.3f}$.')),
 P('Calculate the percentage bias in concentration if 18.60 cubic centimetres is used, and propose an improved data-collection strategy.',M(r'Biased concentration $=0.100(0.01860)/0.0250=0.0744$.'),A(r'Bias $=100(0.0744-0.0736)/0.0736=1.09\%$ high.'),R('Use smaller titrant increments around the steep region and locate its centre; retain several measurements on both sides.'))],
titration('Strong-acid titration data shape',ca=ca,vmax=26),
[balance('Neutralization',[(1,'H',1),(1,'OH',-1)],[(1,'H2O',0)]),num('Acid concentration',ca,.0736),num('End-point hydroxide concentration',oh,1/2180),truth('Overrun is basic',phpast>7)])

add(703,'One ion can either donate or accept a proton','R3.1',
r'The hydrogen carbonate ion is shown with its oxygen-bound proton. In separate experiments it is placed in strongly acidic solution and strongly basic solution. A third hydrogen carbonate solution has measured pH 8.20. Do not assume a hydrolysis constant or calculate an equilibrium composition.',
[P('Write one equation in which hydrogen carbonate accepts a proton from H3O+ and another in which it donates a proton to OH−.',A(r'$\mathrm{HCO_3^-+H_3O^+\rightarrow H_2CO_3+H_2O}$.'),A(r'$\mathrm{HCO_3^-+OH^-\rightarrow CO_3^{2-}+H_2O}$.'),R('Both equations conserve atoms and charge; hydrogen carbonate acts as a base in the first and as an acid in the second.')),
 P('Identify the conjugate acid and conjugate base of HCO3−. Explain why carbonate cannot act as a Brønsted–Lowry acid by proton donation.',A(r'Conjugate acid $\mathrm{H_2CO_3}$; conjugate base $\mathrm{CO_3^{2-}}$.'),R('Conjugate partners differ by exactly one proton and one charge unit.'),R('Carbonate has no proton to donate, although it can accept one.')),
 P('Find [H+] and [OH−] in the measured solution and classify it using the ion concentrations.',M(r'$[H^+]=10^{-8.20}$; $[OH^-]=K_w/[H^+]$.'),A(r'$[H^+]=6.31\times10^{-9}$ and $[OH^-]=1.58\times10^{-6}\ \mathrm{mol\,dm^{-3}}$.'),R('It is basic because hydroxide concentration exceeds hydrogen-ion concentration.'))],
svg(text(320,205,'C',24)+text(210,205,'O',24)+line(231,194,298,194)+line(231,205,298,205)+text(410,130,'O',24)+line(333,184,390,139)+text(485,130,'H',22)+line(426,122,468,122)+text(410,285,'O',24)+line(333,213,390,267)+text(437,264,'−',20)+pair(410,97)+pair(410,157)+pair(410,317)+pair(440,286,False)+pair(384,285,False)+pair(210,167)+pair(210,239),'Hydrogen carbonate structural representation'),
[balance('Proton acceptance',[(1,'HCO3',-1),(1,'H3O',1)],[(1,'H2CO3',0),(1,'H2O',0)]),balance('Proton donation',[(1,'HCO3',-1),(1,'OH',-1)],[(1,'CO3',-2),(1,'H2O',0)]),num('Ion product',10**-8.2*(KW/10**-8.2),KW)])

add(704,'An acid can be concentrated yet weak','R3.1',
r'Acid X is monoprotic, concentration $0.0200\ \mathrm{mol\,dm^{-3}}$, pH 1.70. Acid Y is monoprotic, concentration $0.200\ \mathrm{mol\,dm^{-3}}$, pH 2.70. Their measured conductivities under identical conditions are 8.1 and 0.85 mS cm−1 respectively. The graph shows a tenfold dilution of X. No dissociation constant is required.',
[P('Calculate [H+] for each acid and the approximate fraction of Y molecules that have dissociated. Neglect water autoionization.',M(r'$[H^+]_X=10^{-1.70}$ and $[H^+]_Y=10^{-2.70}$.'),A(r'$0.0200$ and $0.00200\ \mathrm{mol\,dm^{-3}}$, respectively.'),A(r'Fraction for Y $=10^{-2.70}/0.200=0.00998$, approximately $1.00\%$.')),
 P('Explain the distinction between acid strength and concentration, using both experiments as evidence.',R('Concentration counts total acid amount per volume; strength describes the extent of ionization.'),R('X is essentially completely ionized while only about 1% of Y is ionized despite Y’s tenfold larger total concentration.'),R('The lower measured conductivity of Y is consistent with fewer mobile ions, although mobilities also affect a conductivity comparison.')),
 P('Predict the pH of X after the illustrated dilution. Explain why a one-unit rise cannot automatically be assigned to Y after the same dilution.',M('For fully ionized X, a tenfold dilution divides [H+] by ten.'),A('X changes from pH 1.70 to 2.700.'),R('A weak acid’s ionization equilibrium shifts on dilution, so its fraction dissociated increases and [H+] does not generally fall tenfold.'))],
curve('Measured dilution trend for X',lambda logfactor:1.70+logfactor,(0,1),'log10(dilution factor)','pH',(1.5,3)),
[num('Fraction Y dissociated',10**-2.7/.2,.009976311574844394),num('Strong acid H+ fraction',10**-1.7/.02,.99763115748444),truth('Weaker sample is more concentrated',.2>.02 and 10**-2.7<10**-1.7)])

purity=.5*(.0250-.0200*.500)*100.09*100
add(705,'A carbonate impurity measured by back titration','R3.1',
r'A $1.000$ g antacid sample contains CaCO3 and an inert, acid-insoluble filler. It is treated with $25.00\ \mathrm{cm^3}$ of $1.000\ \mathrm{mol\,dm^{-3}}$ HCl. After reaction and removal of dissolved CO2, excess acid requires $20.00\ \mathrm{cm^3}$ of $0.5000\ \mathrm{mol\,dm^{-3}}$ NaOH. Use $M_r(\mathrm{CaCO_3})=100.09$. Gas molar volume under collection conditions is $24.8\ \mathrm{dm^3\,mol^{-1}}$.',
[P('Write a balanced molecular equation for the reaction with HCl and calculate the amount of acid that reacted with the sample.',A(r'$\mathrm{CaCO_3(s)+2HCl(aq)\rightarrow CaCl_2(aq)+CO_2(g)+H_2O(l)}$.'),M(r'Initial acid $=0.02500$ mol; excess acid $=0.02000(0.5000)=0.01000$ mol.'),A('Acid consumed $=0.01500$ mol.')),
 P('Determine the mass percentage of calcium carbonate.',M(r'$n(CaCO_3)=0.01500/2=0.007500$ mol.'),A(r'Mass $=0.750675$ g; percentage $=75.1\%$.'),R('The 2:1 acid-to-carbonate ratio must be used; treating it as 1:1 would give an impossible mass greater than the sample mass.')),
 P('Predict the dry CO2 volume from the sample. The collected volume was only 168 cubic centimetres. Explain a possible low gas result that does not invalidate the titration.',M(r'$V=0.007500(24.8)=0.186$ dm3.'),A('Predicted volume 186 cubic centimetres.'),R('Some carbon dioxide may dissolve in the collection liquid or escape through a leak; the acid consumption can still be measured correctly after carbon dioxide is removed.'))],
flask('Back-titration apparatus',('treated antacid + excess HCl','0.5000 M NaOH')),
[balance('Carbonate neutralization',[(1,'CaCO3',0),(2,'HCl',0)],[(1,'CaCl2',0),(1,'CO2',0),(1,'H2O',0)]),num('Purity percentage',purity,75.0675),num('CO2 volume cm3',.0075*24.8*1000,186)])

add(706,'Building a cell from displacement evidence','R3.2',
r'Experiments show that Mg displaces Zn from Zn2+(aq), Zn displaces Cu from Cu2+(aq), and Cu does not displace Zn from Zn2+(aq). A cell is constructed from Mg/Mg2+ and Cu2+/Cu half-cells as shown. No electrode-potential values are supplied or needed. Use $M(\mathrm{Mg})=24.31$ and $M(\mathrm{Cu})=63.55\ \mathrm{g\,mol^{-1}}$.',
[P('Use the evidence to identify the anode and cathode, state their signs during discharge, and write their half-equations.',R('Mg is more easily oxidized than Zn, which is more easily oxidized than Cu; Mg is the negative anode and Cu the positive cathode.'),A(r'Anode: $\mathrm{Mg(s)\rightarrow Mg^{2+}(aq)+2e^-}$.'),A(r'Cathode: $\mathrm{Cu^{2+}(aq)+2e^-\rightarrow Cu(s)}$.')),
 P('Explain the directions of electron movement in the wire and ion movement in the salt bridge.',R('Electrons flow from the magnesium electrode to the copper electrode through the external wire.'),R('Nitrate ions move toward the magnesium half-cell to balance accumulating magnesium ions.'),R('Potassium ions move toward the copper half-cell to replace positive charge lost as copper ions are reduced.')),
 P('The magnesium electrode loses 0.4862 g. Assuming only the stated reactions, find the copper mass gained and explain why electrons do not carry current through the salt bridge.',M(r'$n(Mg)=0.4862/24.31=0.02000$ mol; the Cu:Mg molar ratio is 1:1.'),A('Copper gained $=0.02000(63.55)=1.27$ g, using an unrounded mass of 1.271 g.'),R('The bridge conducts by movement of ions; free electrons are carried by the metal circuit, not by the aqueous bridge.'))],
cell('Cell designed from displacement evidence',left='Mg(s)',right='Cu(s)',solutions=('Mg2+(aq)','Cu2+(aq)')),
[balance('Magnesium oxidation',[(1,'Mg',0)],[(1,'Mg',2),(2,'e',-1)]),balance('Copper reduction',[(1,'Cu',2),(2,'e',-1)],[(1,'Cu',0)]),num('Copper mass',.4862/24.31*63.55,1.271)])

storage=cell('Laboratory model of a rechargeable lead–acid cell',left='Pb(s)',right='PbO2(s)',solutions=('H+(aq), SO4 2−(aq)',''),electrolytic=True).replace('>DC<','>load<').replace(text(270,72,'+',21),'').replace(text(370,72,'−',21),'')
add(707,'Reversing a rechargeable cell without changing the chemistry','R3.2',
r'During discharge, the cell follows these half-equations: $\mathrm{Pb(s)+SO_4^{2-}(aq)\rightarrow PbSO_4(s)+2e^-}$ and $\mathrm{PbO_2(s)+SO_4^{2-}(aq)+4H^+(aq)+2e^-\rightarrow PbSO_4(s)+2H_2O(l)}$. Both electrode materials contact the same well-mixed electrolyte. Treat its volume as constant.',
[P('Combine the half-equations and identify which original electrode is oxidized during discharge.',M('Add the half-equations and cancel the two electrons.'),A(r'$\mathrm{Pb+PbO_2+2SO_4^{2-}+4H^+\rightarrow 2PbSO_4+2H_2O}$, with states as given.'),R('The lead metal electrode is oxidized: Pb goes from oxidation state 0 to +2.')),
 P('Write the half-equation that occurs at the lead-metal plate during charging and identify its role then.',M('Charging reverses the discharge conversion at this plate.'),A(r'$\mathrm{PbSO_4(s)+2e^-\rightarrow Pb(s)+SO_4^{2-}(aq)}$.'),R('The plate is the cathode during charging because reduction occurs there; an external electrical supply is required.')),
 P('Discharge converts 0.0100 mol of PbO2. Initially the electrolyte contains 0.0500 mol of sulfuric acid, expressed as its formal amount. Find the remaining formal amount and explain the trend in acid concentration.',M('Each mole of PbO2 consumes 4 mol H+ and 2 mol sulfate, equivalent to 2 mol H2SO4.'),A('Formal acid remaining $=0.0500-2(0.0100)=0.0300$ mol.'),R('Acid is consumed on discharge, so its formal concentration falls at constant volume; this statement does not assume that both acid protons are fully dissociated.'))],
storage,
[balance('Lead discharge oxidation',[(1,'Pb',0),(1,'SO4',-2)],[(1,'PbSO4',0),(2,'e',-1)]),balance('Lead-dioxide reduction',[(1,'PbO2',0),(1,'SO4',-2),(4,'H',1),(2,'e',-1)],[(1,'PbSO4',0),(2,'H2O',0)]),num('Formal acid remaining',.05-2*.01,.03)])

add(708,'Why melting changes the products of an ionic conductor','R3.2',
r'Pure MgCl2 is electrolysed using inert electrodes at 720 degrees Celsius, where both the electrolyte and magnesium product are liquid. There is no water. The same apparatus is first tested with solid MgCl2 and then with the melt. No current-time calculation is required.',
[P('Explain the difference in conduction before and after melting, and identify the charge carriers in the melt and the leads.',R('In the solid the ions are held in fixed lattice positions and cannot migrate through the sample.'),R('The melt contains mobile Mg2+ and Cl− ions, which carry current through the electrolyte.'),R('Electrons carry current through the external metallic leads.')),
 P('Write both electrode half-equations, with states, and identify the electrode signs.',A(r'Negative cathode: $\mathrm{Mg^{2+}(l)+2e^-\rightarrow Mg(l)}$.'),A(r'Positive anode: $\mathrm{2Cl^-(l)\rightarrow Cl_2(g)+2e^-}$.'),R('Reduction occurs at the cathode and oxidation at the anode; the power supply drives the non-spontaneous overall change.')),
 P('A run decomposes 0.200 mol of MgCl2 completely. Determine both product amounts and explain why neither hydrogen nor oxygen is expected.',M('Combine the half-equations to obtain one mole of each product per mole of MgCl2.'),A('0.200 mol Mg and 0.200 mol Cl2.'),R('There is no water or other hydrogen/oxygen-containing reactant in the specified melt.'))],
cell('Electrolysis of a water-free magnesium chloride melt','inert electrode X','inert electrode Y',('molten MgCl2 at 720 C',''),True),
[balance('Molten magnesium reduction',[(1,'Mg',2),(2,'e',-1)],[(1,'Mg',0)]),balance('Chloride oxidation',[(2,'Cl',-1)],[(1,'Cl2',0),(2,'e',-1)]),num('Molar product ratio',.2/.2,1)])

def oxidation_apparatus():
 b=''
 # Left: reflux condenser, open at top and water jacket; flask heated below.
 b+='<path d="M145 110V220Q90 245 110 295Q165 330 220 295Q240 245 185 220V110M130 110V210H145M185 210H200V110M130 110H145M185 110H200" fill="none" stroke="#111" stroke-width="2"/>'
 b+=line(130,192,108,192)+line(200,125,222,125)+text(82,195,'water in',12)+text(237,129,'out',12)+text(165,80,'open',13)+text(165,365,'X',19)
 # Right: distillation head feeds a downward water-jacketed condenser and receiver.
 b+='<path d="M380 160V230Q340 250 355 295Q390 325 425 295Q440 250 400 230V160H380M390 160V125L535 210M385 137L530 222M395 110L540 196" fill="none" stroke="#111" stroke-width="2"/>'
 b+=line(522,215,538,202)+line(410,120,423,108)+text(555,228,'water in',12)+text(434,101,'out',12)
 b+='<path d="M535 220V265L558 300Q575 305 592 300L615 265V245" fill="none" stroke="#111" stroke-width="2"/>'
 b+='<path d="M520 255V330H628V255M520 275H628" fill="none" stroke="#111" stroke-width="2"/>'
 b+='<path d="M525 303l9-8 8 9-8 9Z M601 310l10-7 8 9-9 8Z" fill="none" stroke="#111" stroke-width="1.5"/>'
 b+=text(575,351,'ice bath',14)
 b+=text(390,365,'Y',19)+text(165,395,'Heat',14)+text(390,395,'Heat',14)
 return svg(b,'Two oxidation apparatus arrangements')
add(709,'Choosing an apparatus to stop oxidation at the right stage','R3.2',
r'A primary alcohol, ethanol, can be oxidized first to an aldehyde and then to a carboxylic acid. The two apparatus arrangements are shown. Oxidation conditions and a suitable oxidizing agent are provided; the reagent’s identity need not be recalled. The aldehyde is more volatile than the alcohol and aqueous reaction mixture. The receiver in Y is cooled in an ice bath because ethanal boils near 20°C.',
[P('Write equations using [O] for the two successive oxidation steps and name the products.',A(r'$\mathrm{CH_3CH_2OH+[O]\rightarrow CH_3CHO+H_2O}$; ethanal.'),A(r'$\mathrm{CH_3CHO+[O]\rightarrow CH_3COOH}$; ethanoic acid.'),R('The carbon bearing the hydroxy group is oxidized first to an aldehyde carbonyl and then to a carboxyl group.')),
 P('Choose the arrangement most suitable for collecting ethanal and the one for maximizing ethanoic acid. Explain the difference.',A('Y is distillation for ethanal; X is reflux for ethanoic acid.'),R('Distillation removes the more volatile aldehyde from contact with the oxidant as it forms.'),R('Reflux returns condensed volatile material to the flask, allowing prolonged heating and further oxidation without losing reactants.')),
 P('An oxidized 0.0800 mol sample gives 0.0500 mol aldehyde and 0.0200 mol acid, with the remainder unreacted. Find the amount of [O] consumed and explain why replacing ethanol by a tertiary alcohol would change the outcome.',M('Aldehyde formation uses one [O] per alcohol; acid formation uses two in total.'),A(r'$n([O])=0.0500+2(0.0200)=0.0900$ mol.'),R('A tertiary alcohol lacks a hydrogen on the carbon bearing the hydroxy group and is not oxidized under these same conditions without carbon–carbon bond cleavage.'))],
oxidation_apparatus(),
[balance('Ethanol to aldehyde',[(1,'C2H6O',0),(1,'O',0)],[(1,'C2H4O',0),(1,'H2O',0)]),balance('Aldehyde to acid',[(1,'C2H4O',0),(1,'O',0)],[(1,'C2H4O2',0)]),num('Oxidant equivalents',.05+2*.02,.09)])

add(710,'The acidity controls a redox titration’s stoichiometry','R3.2',
r'A $25.00\ \mathrm{cm^3}$ Fe2+(aq) sample consumes $18.00\ \mathrm{cm^3}$ of $0.02000\ \mathrm{mol\,dm^{-3}}$ MnO4− in strongly acidic solution. The intended manganese half-equation is $\mathrm{MnO_4^-+8H^++5e^-\rightarrow Mn^{2+}+4H_2O}$. If insufficient acid is present, a brown MnO2 solid may instead form by $\mathrm{MnO_4^-+4H^++3e^-\rightarrow MnO_2+2H_2O}$. These are the only manganese pathways to consider.',
[P('Write the iron half-equation and the overall ionic equation for the intended titration.',A(r'$\mathrm{Fe^{2+}\rightarrow Fe^{3+}+e^-}$.'),M('Multiply the iron half-equation by five and cancel electrons.'),A(r'$\mathrm{MnO_4^-+8H^++5Fe^{2+}\rightarrow Mn^{2+}+4H_2O+5Fe^{3+}}$.')),
 P('Find the concentration of Fe2+ in the sample using the intended reaction.',M(r'$n(MnO_4^-)=0.02000(0.01800)=3.600\times10^{-4}$ mol.'),A(r'$n(Fe^{2+})=1.800\times10^{-3}$ mol.'),A(r'$c(Fe^{2+})=0.0720\ \mathrm{mol\,dm^{-3}}$.')),
 P('Explain the significance of a brown solid and the direction of bias if the entire titrant is incorrectly treated as reacting by the five-electron pathway.',R('Brown MnO2 indicates that at least some permanganate has followed the three-electron pathway.'),R('Each such mole of permanganate oxidizes only three moles of Fe2+, rather than five.'),R('Using five for all titrant moles therefore overestimates the amount and concentration of iron.'))],
flask('Acidic redox titration',('Fe2+ sample + sufficient acid','standard MnO4−')),
[balance('Intended redox equation',[(1,'MnO4',-1),(8,'H',1),(5,'Fe',2)],[(1,'Mn',2),(4,'H2O',0),(5,'Fe',3)]),balance('Brown manganese pathway',[(1,'MnO4',-1),(4,'H',1),(3,'e',-1)],[(1,'MnO2',0),(2,'H2O',0)]),num('Iron concentration',.020*.018*5/.025,.072)])

add(711,'A chain reaction makes more product than one initiation event','R3.3',
r'Ethane and chlorine are exposed to ultraviolet light. The diagram shows electron movement during the initiation stage. Restrict the product mechanism to the first substitution of ethane. Radical dots must be shown where appropriate.',
[P('Identify the type of bond fission and write the initiation equation. Explain the meaning of each arrowhead.',R('The Cl–Cl bond undergoes homolytic fission.'),A(r'$\mathrm{Cl_2\xrightarrow{UV}2Cl{\cdot}}$.'),R('Each fish-hook arrow represents one electron from the bonding pair moving to one chlorine atom.')),
 P('Write the two propagation equations and explain why the process is a chain.',A(r'$\mathrm{Cl{\cdot}+CH_3CH_3\rightarrow HCl+CH_3CH_2{\cdot}}$.'),A(r'$\mathrm{CH_3CH_2{\cdot}+Cl_2\rightarrow CH_3CH_2Cl+Cl{\cdot}}$.'),R('A chlorine radical is regenerated after each two-step cycle and can initiate another cycle without another Cl2 photolysis event.')),
 P('Give a termination equation that makes a four-carbon product and explain why it terminates a chain rather than propagating it.',A(r'$\mathrm{2CH_3CH_2{\cdot}\rightarrow CH_3CH_2CH_2CH_3}$.'),R('Two unpaired electrons pair to form the new carbon–carbon bond.'),R('No radical product remains, so these two chains can no longer propagate.'))],
radical('Initiation electron flow in ethane chlorination'),
[balance('Ethane hydrogen abstraction',[(1,'Cl',0),(1,'C2H6',0)],[(1,'HCl',0),(1,'C2H5',0)]),balance('Propagation regeneration',[(1,'C2H5',0),(1,'Cl2',0)],[(1,'C2H5Cl',0),(1,'Cl',0)]),balance('Radical coupling termination',[(2,'C2H5',0)],[(1,'C4H10',0)]),num('Radical count propagation input/output',1,1)])

chrom=lambda x:sum(a*math.exp(-((x-c)/.24)**2) for c,a in [(2,20),(5,50),(8,25),(11,5)])
add(712,'A chromatogram reveals repeated substitution','R3.3',
r'A closed reaction initially contains 0.100 mol methane and sufficient chlorine. After partial UV chlorination, carbon-containing products are separated. Corrected peak areas are proportional to moles, with all carbon remaining in the four indicated one-carbon species: CH4 20.0%, CH3Cl 50.0%, CH2Cl2 25.0%, CHCl3 5.0%. Neglect radical-coupling products and any CCl4.',
[P('Find the amount of each carbon-containing species and the amount of chlorine consumed.',M('Multiply each corrected fraction by the original 0.100 mol of carbon.'),A('Amounts: 0.0200, 0.0500, 0.0250 and 0.00500 mol, respectively.'),A(r'$n(Cl_2)=0.0500+2(0.0250)+3(0.00500)=0.115$ mol.')),
 P('Write an overall equation forming CH2Cl2 from methane, and find the total amount of HCl produced across the mixture.',A(r'$\mathrm{CH_4+2Cl_2\rightarrow CH_2Cl_2+2HCl}$.'),M('Each substitution consumes one Cl2 and replaces one C–H bond with C–Cl, producing one HCl.'),A('Total HCl is 0.115 mol.')),
 P('Explain why chloromethane is not the only product and why methane can be stable in the dark despite favourable overall reaction energy.',R('Chloromethane still contains C–H bonds and can undergo further radical substitution.'),R('UV light supplies energy for initiation; favourable overall energy does not remove an activation barrier.'),R('Strong C–H/C–C bonds and the essentially non-polar nature of alkanes make uncatalysed dark reactions kinetically slow.'))],
curve('Separated carbon-species peaks (equal width)',chrom,(0,13),'Retention coordinate / arbitrary units','Corrected detector response',(0,60)),
[balance('Two substitutions',[(1,'CH4',0),(2,'Cl2',0)],[(1,'CH2Cl2',0),(2,'HCl',0)]),num('Carbon amount conserved',.020+.050+.025+.005,.100),num('Cl2 and HCl amount',.05+2*.025+3*.005,.115)])

add(713,'Following electron pairs without inventing a free electron','R3.4',
r'Aqueous hydroxide reacts with bromoethane to form ethanol. The reactant diagram shows lone pairs on oxygen and the polarized C–Br bond. Describe electron-pair movement only; a named kinetic mechanism or rate equation is not required.',
[P('Identify the nucleophile and the electrophilic atom, explaining their roles in terms of electron pairs.',A(r'$\mathrm{OH^-}$ is the nucleophile and the carbon bonded to Br is the electrophilic atom.'),R('Oxygen has an available lone pair that can be donated to form a new bond.'),R('The C–Br bond is polarized toward bromine, leaving the carbon electron-deficient.')),
 P('Write the net ionic substitution equation and describe the origins and destinations of the two curly arrows.',A(r'$\mathrm{CH_3CH_2Br+OH^-\rightarrow CH_3CH_2OH+Br^-}$.'),R('One arrow starts at an oxygen lone pair and ends at the carbon bonded to bromine.'),R('The other starts in the C–Br bonding pair and ends at bromine, which receives both electrons.')),
 P('Explain why the leaving species is bromide rather than a bromine radical, and distinguish substitution from addition in this example.',R('Heterolytic fission transfers the complete bonding pair to Br, forming Br− rather than Br·.'),R('One group replaces another at carbon; the carbon skeleton and carbon–carbon bond order are retained.'),R('Both charge and atoms are conserved: total charge is −1 on each side and no isolated free electron appears in the equation.'))],
nucleophile('Bromoethane and hydroxide reactants'),
[balance('Hydroxide substitution',[(1,'C2H5Br',0),(1,'OH',-1)],[(1,'C2H6O',0),(1,'Br',-1)]),num('Attacked carbon bond-order sum',1+1+1+1,4),num('Hydroxide valence electrons',6+1+1,8)],
nucleophile('Electron-pair movements in the substitution',True))

add(714,'Separating alkene addition from alkane substitution','R3.4',
r'A 0.300 mol mixture contains only ethene and ethane. In an inert non-aqueous solvent in the dark it reacts with 0.180 mol Br2, which is just enough to remove all the ethene; ethane does not react under these conditions. In a subsequent UV experiment, each remaining ethane molecule undergoes exactly one substitution. The two starting molecules are shown.',
[P('Write the dark-reaction equation, name its reaction type, and explain why ethene reacts.',A(r'$\mathrm{CH_2{=}CH_2+Br_2\rightarrow CH_2BrCH_2Br}$.'),A('Electrophilic addition; the product is 1,2-dibromoethane.'),R('The carbon–carbon double bond has high electron density and can donate an electron pair to an electrophile.')),
 P('Determine the initial mole fractions of ethene and ethane.',M('The dark reaction consumes one Br2 per ethene, so ethene amount is 0.180 mol.'),A('Ethane amount is $0.300-0.180=0.120$ mol.'),A('Mole fractions: ethene 0.600 and ethane 0.400.')),
 P('Write the UV substitution equation for ethane and compare the amounts of HBr formed in the two experiments.',A(r'$\mathrm{C_2H_6+Br_2\xrightarrow{UV}C_2H_5Br+HBr}$.'),A('The dark ethene addition gives no HBr; single substitution of the remaining ethane gives 0.120 mol HBr.'),R('Addition incorporates both bromine atoms into the organic product; substitution replaces H by Br and releases HBr.'))],
svg(text(170,145,'H2C',24)+text(360,145,'CH2',24)+line(205,132,320,132)+line(205,144,320,144)+text(500,145,'Ethene',19)+text(170,285,'H3C',24)+text(360,285,'CH3',24)+line(205,275,320,275)+text(500,285,'Ethane',19),'Two hydrocarbons under different bromination conditions'),
[balance('Ethene bromine addition',[(1,'C2H4',0),(1,'Br2',0)],[(1,'C2H4Br2',0)]),balance('Ethane bromine substitution',[(1,'C2H6',0),(1,'Br2',0)],[(1,'C2H5Br',0),(1,'HBr',0)]),num('Ethene mole fraction',.180/.300,.6),num('Ethane mole fraction',.120/.300,.4)])

# ADDITIONAL HL: equilibrium calculations and detailed electron-pair mechanisms.
ka=1.80e-5;c=.0400;h=math.sqrt(ka*c)
add(715,'A weak-acid approximation has a limited range','R3.1',
r'A monoprotic acid HA has $K_a=1.80\times10^{-5}$. For a $0.0400\ \mathrm{mol\,dm^{-3}}$ solution, a student assumes $[HA]_{\rm eq}\approx c$ and obtains $[H^+]\approx\sqrt{K_ac}$. The graph shows this approximate prediction over a range where the approximation is useful. Water autoionization is negligible in the cases considered.',
[P('Write the ionization equation and Ka expression, then find the predicted pH of the 0.0400 mol dm−3 solution.',A(r'$\mathrm{HA+H_2O\rightleftharpoons H_3O^++A^-}$; $K_a=[H^+][A^-]/[HA]$.'),M(r'$[H^+]\approx\sqrt{(1.80\times10^{-5})(0.0400)}$.'),A(f'$[H^+]={h:.3g}$; pH $={-math.log10(h):.3f}$.')),
 P('Test the approximation using the percentage dissociation. Then repeat this check at 0.000400 mol dm−3, without solving a quadratic.',M('Use estimated fraction dissociated $[H^+]/c$ in each case.'),A('At 0.0400 M the fraction is 2.12%; at 0.000400 M it is 21.2%.'),R('The first small depletion is reasonable under a 5% criterion; the second is too large to regard [HA] as unchanged.')),
 P('Explain the gradient of the plotted relationship and why extending its straight line indefinitely would be physically unsound.',M(r'$pH\approx\frac12(pK_a-\log_{10}c)$.'),A('Gradient is −0.5 for pH versus log10(c).'),R('At sufficiently low concentration the assumed small dissociation fails, and eventually water autoionization also matters; the same straight-line approximation cannot be extrapolated without limit.'))],
curve('Approximate weak-acid pH versus log concentration',lambda x:.5*(-math.log10(ka)-x),(-1.4,-.4),'log10(c / mol dm−3)','Predicted pH',(1.9,3.4)),
[balance('Acid ionization',[(1,'CH3COOH',0),(1,'H2O',0)],[(1,'H3O',1),(1,'CH3COO',-1)]),num('Initial dissociation fraction',h/c,math.sqrt(ka/c)),num('100fold dilution fraction ratio',math.sqrt(ka/.0004)/(math.sqrt(ka/.04)),10),truth('Dilute approximation fails5percent',math.sqrt(ka*.0004)/.0004>.05)])

kb=1.80e-5;ka_nh4=KW/kb;oh=math.sqrt(kb*.0800);hh=math.sqrt(ka_nh4*.0800)
add(716,'A weak base and its conjugate-acid salt','R3.1',
r'Ammonia has $K_b=1.80\times10^{-5}$. Compare separate $0.0800\ \mathrm{mol\,dm^{-3}}$ solutions of NH3 and NH4Cl. Chloride has negligible acid–base activity. Use small-ionization approximations and verify them.',
[P('Calculate Ka for NH4+ and write the ammonium hydrolysis equation.',M(r'$K_a(NH_4^+)=K_w/K_b(NH_3)$.'),A(r'$K_a=5.56\times10^{-10}$.'),A(r'$\mathrm{NH_4^++H_2O\rightleftharpoons NH_3+H_3O^+}$.')),
 P('Calculate the pH of each solution and check the approximate fractional ionization in each.',M(r'For ammonia, $[OH^-]\approx\sqrt{K_bc}$, then $pOH=-\log[OH^-]$ and $pH=14-pOH$.'),A(f'Ammonia pH $={14+math.log10(oh):.3f}$; fractional ionization $=1.50\\%$.'),M(r'For ammonium, $[H^+]\approx\sqrt{K_ac}$.'),A(f'NH4Cl pH $={-math.log10(hh):.3f}$; fractional ionization $=0.00833\\%$, so both are small.')),
 P('Explain why dissolving NH4Cl can lower pH although no HCl molecule is released.',R('NH4+ donates a proton to water in an equilibrium reaction.'),R('The chloride ion is a spectator; acidity arises from the conjugate acid of the weak base.'),R('A salt dissociates into its ions; producing free HCl molecules is neither necessary nor the stated aqueous process.'))],
curve('Conjugate-pair solution comparison',lambda c:14+math.log10(math.sqrt(kb*c)),(.01,.08),'Formal concentration / mol dm−3','pH',(4,12),extra=[('NH4Cl',[(c,-math.log10(math.sqrt(ka_nh4*c))) for c in [.01,.02,.04,.06,.08]])]),
[balance('Ammonium hydrolysis',[(1,'NH4',1),(1,'H2O',0)],[(1,'NH3',0),(1,'H3O',1)]),balance('Ammonia ionization',[(1,'NH3',0),(1,'H2O',0)],[(1,'NH4',1),(1,'OH',-1)]),num('Conjugate product',kb*ka_nh4,KW),num('Base dissociation percentage',100*oh/.08,1.5)])

def carboxyl(x,y,proton=True):
 b=text(x,y,'C',17)+text(x-48,y,'CH3',16)+line(x-27,y-7,x-12,y-7)
 b+=text(x,y-45,'O',18)+line(x-4,y-30,x-4,y-18)+line(x+4,y-30,x+4,y-18)
 b+=text(x+45,y,'O',18)+line(x+12,y-7,x+31,y-7)+pair(x+45,y-27)+pair(x+45,y+20)
 if proton:b+=text(x+87,y,'H',17)+line(x+58,y-7,x+75,y-7)
 else:b+=text(x+66,y-12,'−',17)+pair(x+68,y+7,False)
 return b
bufferfig=svg(carboxyl(145,150)+carboxyl(395,150)+carboxyl(95,285,False)+carboxyl(295,285,False)+carboxyl(495,285,False)+text(320,375,'Representative inventory: two HA units for three A− units.',15),'Acid/conjugate-base inventory')
add(717,'Adjusting a buffer by consuming conjugate base','R3.1',
r'A buffer is made with 0.0100 mol ethanoic acid HA and 0.0150 mol sodium ethanoate A− in a total volume of 250 cubic centimetres. The acid has pKa 4.76. An added small amount of strong acid reacts essentially completely with A−. Use the acid equilibrium expression; no quadratic solution is required.',
[P('Derive the concentration-ratio form for pH and find the initial buffer pH.',M(r'From $K_a=[H^+][A^-]/[HA]$, rearrange to $[H^+]=K_a[HA]/[A^-]$.'),A(r'$pH=pK_a+\log_{10}([A^-]/[HA])$.'),A(r'Initial pH $=4.76+\log_{10}(1.50)=4.936$.')),
 P('Find the volume of 1.00 mol dm−3 HCl needed to change the pH to 4.76, assuming volumes are additive.',M('Target pH = pKa requires equal acid and conjugate-base amounts; after x mol HCl these are $0.0100+x$ and $0.0150-x$.'),A('$x=0.00250$ mol, requiring 2.50 cubic centimetres HCl.'),R('The common final volume cancels from the concentration ratio; it must not be applied to only one component.')),
 P('Write the buffer’s reaction with added HCl and explain why a comparable amount of pure strong acid would not itself make an acidic buffer.',A(r'$\mathrm{CH_3COO^-+H^+\rightarrow CH_3COOH}$.'),R('The buffer contains appreciable amounts of a weak acid and its conjugate base, allowing added acid or base to be consumed.'),R('A strong acid is essentially fully dissociated and does not provide a comparable reservoir of a weak acid/conjugate-base pair.'))],
bufferfig,
[balance('Acetate neutralizes acid',[(1,'CH3COO',-1),(1,'H',1)],[(1,'CH3COOH',0)]),num('Target equal amounts',.010+.0025,.015-.0025),num('Target HCl cm3',.0025/1*1000,2.5)])

add(718,'Equal initial pH does not mean equal buffer capacity','R3.1',
r'Buffer P contains 0.0200 mol HA and 0.0100 mol A− in 200 cubic centimetres; pKa(HA) = 4.00. Buffer Q is prepared by diluting an identical complete portion to 2.00 dm3. Separate 20.0 cubic centimetre aliquots of P and Q each receive 1.00 cubic centimetre of 1.50 mol dm−3 NaOH. Assume quantitative neutralization before any weak equilibrium calculation.',
[P('Calculate the common initial pH and explain why the dilution scarcely changes it.',M(r'$pH=4.00+\log_{10}(0.0100/0.0200)$.'),A('Both initial pH values are approximately 3.699.'),R('Dilution changes both component concentrations by the same factor, so their ratio is unchanged, provided the buffer approximation remains valid.')),
 P('Determine the final pH after adding NaOH to the P aliquot.',M('The aliquot initially has 0.00200 mol HA and 0.00100 mol A−; hydroxide added is 0.00150 mol.'),A('After reaction, HA = 0.000500 mol and A− = 0.00250 mol.'),A(r'$pH=4.00+\log_{10}(5)=4.699$.')),
 P('Determine the final pH for the Q aliquot and explain the difference from P.',M('Q’s aliquot initially has only 0.000200 mol HA; 0.00130 mol OH− therefore remains in 0.0210 dm3.'),M(r'$[OH^-]=0.00130/0.0210=0.0619$; use $pH=14+\log[OH^-]$.'),A(f'pH $={14+math.log10(.0013/.021):.3f}$, strongly basic.'),R('Equal initial ratios give equal starting pH, but Q has much less neutralizing acid per aliquot, so the same added hydroxide exhausts its buffer component.'))],
curve('Initial buffer pH under dilution',lambda x:4+math.log10(.5),(1,10),'Dilution factor','Initial pH',(3,5)),
[balance('Buffer consumes hydroxide',[(1,'CH3COOH',0),(1,'OH',-1)],[(1,'CH3COO',-1),(1,'H2O',0)]),num('P postaddition ratio',(.001+.0015)/(.002-.0015),5),num('Q excessOH',.0015-.0002,.0013),truth('Q buffer component exhausted',.0015>.0002)])

ka=10**-4.80;ceq=.00250/.0500;pheq=14+math.log10(math.sqrt(KW/ka*ceq))
add(719,'Reading a weak-acid titration before choosing an indicator','R3.1',
r'A $25.0\ \mathrm{cm^3}$ monoprotic weak-acid sample is titrated with $0.100\ \mathrm{mol\,dm^{-3}}$ NaOH. Equivalence occurs at $25.0\ \mathrm{cm^3}$ and the pH at half-equivalence is 4.80. Candidate indicators change colour over pH 3.1–4.4 and 8.2–10.0. Use small-ionization approximations where needed.',
[P('Find the acid concentration and Ka, explaining the half-equivalence result.',M('At equivalence, acid amount is $0.100(0.0250)=0.00250$ mol.'),A(r'Acid concentration $=0.100\ \mathrm{mol\,dm^{-3}}$; $K_a=10^{-4.80}=1.58\times10^{-5}$.'),R('At half-equivalence the amounts of HA and A− are equal, so the equilibrium expression gives [H+] = Ka and pH = pKa.')),
 P('Calculate the approximate equivalence-point pH and show the ion hydrolysis responsible.',A(r'$\mathrm{A^-+H_2O\rightleftharpoons HA+OH^-}$.'),M(r'$[A^-]=0.00250/0.0500=0.0500$; $K_b=K_w/K_a$ and $[OH^-]\approx\sqrt{K_b[A^-]}$.'),A(f'Equivalence pH $={pheq:.3f}$.')),
 P('Choose the more suitable indicator and explain what happens to equivalence volume if 25.0 cubic centimetres of water is added to the original acid sample before titration.',A('Use the indicator with range 8.2–10.0, matching the steep basic equivalence region.'),R('Water does not change the amount of acid, so equivalence still requires 25.0 cubic centimetres of NaOH.'),R('The pH curve changes with dilution, but the stoichiometric amount required for equivalence does not.'))],
titration('Weak-acid / strong-base titration',ka=ka,vmax=40),
[balance('Conjugate-base hydrolysis',[(1,'CH3COO',-1),(1,'H2O',0)],[(1,'CH3COOH',0),(1,'OH',-1)]),num('Equivalence salt concentration',.1*.025/.050,.05),num('Hydrolysis fraction',math.sqrt(KW/ka*.05)/.05,.000112334976114278)] )

kb=10**-4.30;acidka=KW/kb;ceq=.0800*.0200/.0360;h=math.sqrt(acidka*ceq)
add(720,'A weak-base titration with an acidic equivalence point','R3.1',
r'A 20.0 cubic centimetre sample of a monofunctional weak base B, concentration 0.0800 mol dm−3, is titrated with 0.100 mol dm−3 HCl. The base has pKb 4.30. Treat B/BH+ as the only weak conjugate system.',
[P('Find the equivalence volume and the pH at half-equivalence.',M('Base amount $=0.0800(0.0200)=0.00160$ mol, giving 16.0 cubic centimetres acid at equivalence.'),R('At half-equivalence, [B] = [BH+], so pOH = pKb = 4.30.'),A('Half-equivalence is at 8.00 cubic centimetres and pH = 9.700.')),
 P('Calculate the approximate equivalence-point pH.',M(r'$K_a(BH^+)=K_w/K_b=2.00\times10^{-10}$; $[BH^+]=0.00160/0.0360=0.0444$.'),M(r'$[H^+]\approx\sqrt{K_a[BH^+]}$.'),A(f'Equivalence pH $={-math.log10(h):.3f}$.')),
 P('Explain why the equivalence solution is acidic. Choose between indicators with ranges 4.4–6.2 and 8.2–10.0, and distinguish an indicator end point from equivalence.',A(r'$\mathrm{BH^++H_2O\rightleftharpoons B+H_3O^+}$ makes the solution acidic.'),A('The 4.4–6.2 indicator is more suitable.'),R('Equivalence is the stoichiometric acid/base balance; the observed colour end point occurs over an indicator equilibrium range and need not coincide exactly.'))],
titration('Weak-base / strong-acid titration',ca=.0800,va=20,cb=.100,ka=kb,base=True,vmax=28),
[balance('Protonation model using ammonia',[(1,'NH3',0),(1,'H',1)],[(1,'NH4',1)]),num('Equivalence cm3',.08*.020/.1*1000,16),num('Conjugate product',kb*acidka,KW),truth('Equivalence acidic',-math.log10(h)<7)])

add(721,'Measuring an indicator equilibrium by absorbance','R3.1',
r'An indicator obeys $\mathrm{HInd(aq)\rightleftharpoons H^+(aq)+Ind^-(aq)}$ with pKa 5.50. At a chosen wavelength, only HInd absorbs appreciably and absorbance is proportional to its concentration. At the same total indicator concentration and path length, completely protonated indicator has absorbance 0.500; an unknown buffered sample has absorbance 0.100. The spectra illustrate the two forms; no particular molecular structure is assumed.',
[P('Write the indicator Ka expression and find the fractions of indicator present as HInd and Ind−.',A(r'$K_a=[H^+][Ind^-]/[HInd]$.'),M('The protonated fraction is $0.100/0.500=0.200$.'),A('Fractions are 0.200 HInd and 0.800 Ind−.')),
 P('Calculate the sample pH and explain which component is favoured as pH increases.',M(r'$[Ind^-]/[HInd]=4$; $pH=pK_a+\log_{10}4$.'),A('pH = 6.102.'),R('Higher pH means lower [H+], shifting the indicator equilibrium toward Ind−.')),
 P('Show why the colour transition is spread over a pH interval rather than occurring at one exact pH. Find the pH values for concentration ratios 0.10 and 10.0.',M('Use pH = pKa + log(conjugate ratio).'),A('The ratios 0.10 and 10.0 give pH 4.500 and 6.500, respectively.'),R('Both coloured forms coexist through the equilibrium range; the eye detects a change in their relative contributions, not an instantaneous conversion at equivalence.'))],
curve('Illustrative indicator absorption spectra',lambda w:.5*math.exp(-((w-520)/22)**2),(350,650),'Wavelength / nm','Absorbance',(0,.55),extra=[('',[(w,.35*math.exp(-((w-430)/15)**2)) for w in range(350,651,2)])]).replace('</svg>',text(225,160,'Ind−',15)+text(366,92,'HInd',15)+'</svg>'),
[num('Indicator fractions sum',.1/.5+(1-.1/.5),1),num('Sample pH',5.5+math.log10(.8/.2),6.1020599913279625),num('Transition interval width',(5.5+math.log10(10))-(5.5+math.log10(.1)),2)])

add(722,'Electron-pair donation without a proton transfer','R3.4',
r'BF3 reacts with NH3 to form a 1:1 adduct. The diagram shows their Lewis formulas. In a separate ligand-exchange system, a Co(III) complex contains four neutral NH3 ligands and two Cl− ligands. A chloride ligand is replaced by a fifth ammonia ligand; the coordination number remains six.',
[P('Identify the Lewis acid and Lewis base in the BF3/NH3 reaction, and describe the origin and destination of the donated electron pair.',A('BF3 is the Lewis acid; NH3 is the Lewis base.'),R('The lone pair on nitrogen is donated toward boron to form the N–B bond.'),R('Boron begins with six electrons around it and can accept a pair; no proton transfer is necessary.')),
 P('Describe or draw the adduct’s N–B bond and determine the formal charges on N and B in its Lewis representation.',A(r'Adduct $\mathrm{H_3N\rightarrow BF_3}$ has four bonds around both N and B.'),A('Nitrogen has formal charge +1; boron −1; the whole adduct is neutral.'),R('After formation the coordinate bond is an ordinary shared-pair covalent bond; its donated origin does not make its electrons permanently distinguishable.')),
 P('Determine the charges of the original cobalt complex and the complex after ligand exchange. Write the balanced ligand-exchange equation.',M('For Co(III), four NH3 and two Cl− give $+3+0-2=+1$; five NH3 and one Cl− give +2.'),A(r'$\mathrm{[Co(NH_3)_4Cl_2]^++NH_3\rightleftharpoons[Co(NH_3)_5Cl]^{2+}+Cl^-}$.'),R('One anionic ligand leaves as Cl−, balancing the increased complex charge while six donor ligands remain coordinated.'))],
lewis_adduct(),
[balance('Lewis adduct atom/charge balance',[(1,'BF3',0),(1,'NH3',0)],[(1,'BF3NH3',0)]),balance('Ligand exchange',[(1,'Co(NH3)4Cl2',1),(1,'NH3',0)],[(1,'Co(NH3)5Cl',2),(1,'Cl',-1)]),num('Adduct total formal charge',1-1,0)])

she=cell('Measuring a metal half-cell against hydrogen','Pt(s), H2(g)','Cu(s)',('H+(aq)','Cu2+(aq)'))
she=she.replace('</svg>','<path d="M85 115V205H125V280" fill="none" stroke="#111" stroke-width="2"/>'+text(68,105,'H2 in',13)+''.join(f'<circle cx="{130+8*(i%2)}" cy="{300-15*i}" r="3" fill="white" stroke="#111"/>' for i in range(4))+'</svg>')
add(723,'The voltmeter sign depends on the leads, not the chemistry','R3.2',
r'The left half-cell is the standard hydrogen electrode, using platinum, H2 at 100 kPa and $[H^+]=1.00\ \mathrm{mol\,dm^{-3}}$. The right half-cell is Cu2+/Cu at $[Cu^{2+}]=1.00\ \mathrm{mol\,dm^{-3}}$. Both are at 298 K. With the red voltmeter lead on Cu and the black lead on Pt, the reading is +0.340 V. The standard hydrogen reduction potential is defined as 0.000 V.',
[P('Deduce the standard reduction potential of Cu2+/Cu and identify the spontaneous electrode reactions.',M('A positive reading with the red lead on Cu identifies Cu as the higher-potential electrode in this discharge cell.'),A(r'$E^\circ(Cu^{2+}/Cu)=+0.340$ V; $\mathrm{Cu^{2+}+2e^-\rightarrow Cu}$ at the cathode.'),A(r'At Pt, $\mathrm{H_2\rightarrow2H^++2e^-}$; Pt is an inert electron conductor.')),
 P('State the electron direction and explain what changes if only the voltmeter leads are exchanged.',A('Electrons in the external circuit move from the hydrogen electrode toward copper.'),A('The voltmeter reading changes to −0.340 V.'),R('Exchanging measuring leads reverses the displayed potential difference, but does not reverse the spontaneous chemical reaction or reassign the physical anode/cathode.')),
 P('Explain why each of the three specified standard-state conditions matters and why the salt bridge cannot be replaced by a dry insulating tube.',R('Electrode potentials depend on aqueous composition, gas pressure and temperature; the standard comparison fixes these conditions.'),R('A conducting salt bridge permits ion migration to maintain bulk electrical neutrality as redox occurs.'),R('A dry insulating tube provides no ionic path, so charge separation would halt sustained current.'))],
she,
[balance('Hydrogen oxidation',[(1,'H2',0)],[(2,'H',1),(2,'e',-1)]),balance('Copper reduction',[(1,'Cu',2),(2,'e',-1)],[(1,'Cu',0)]),num('Cell potential',.340-0,.340)])

add(724,'Scaling a redox equation does not scale its voltage','R3.2',
r'Use these standard reduction potentials: $\mathrm{Sn^{4+}(aq)+2e^-\rightleftharpoons Sn^{2+}(aq)}$, +0.150 V; $\mathrm{I_2(s)+2e^-\rightleftharpoons2I^-(aq)}$, +0.540 V. In the model cell, solid iodine is in contact with the iodide solution and inert electrodes provide electrical contact. Take $F=96500\ \mathrm{C\,mol^{-1}}$.',
[P('Write the spontaneous overall reaction and identify the oxidizing and reducing agents.',M('The more positive reduction potential selects iodine reduction; reverse the tin half-equation.'),A(r'$\mathrm{Sn^{2+}+I_2\rightarrow Sn^{4+}+2I^-}$.'),A('I2 is the oxidizing agent; Sn2+ is the reducing agent.')),
 P('Calculate the standard cell potential and the standard Gibbs energy change per mole of the equation as written.',M(r'$E^\circ_{\rm cell}=0.540-0.150$; two moles of electrons are transferred.'),A(r'$E^\circ_{\rm cell}=+0.390$ V.'),A(r'$\Delta G^\circ=-2(96500)(0.390)=-75.3\ \mathrm{kJ\,mol^{-1}}$.')),
 P('A student doubles every coefficient and reports a cell potential of 0.780 V. Correct this claim, give the corresponding Gibbs energy change, and distinguish spontaneity from reaction speed.',R('Cell potential is an intensive quantity, so it remains +0.390 V.'),A('The doubled reaction transfers 4 mol electrons and has Gibbs energy change −151 kJ per mole of the doubled equation, using an unrounded value of −150.54 kJ.'),R('A negative standard Gibbs energy change establishes thermodynamic favourability under standard conditions, not a fast rate; an activation barrier can still slow the reaction.'))],
cell('Tin / iodine redox cell','Pt(s)','Pt(s), I2(s)',('Sn4+(aq), Sn2+(aq)','I−(aq)')),
[balance('Tin/iodine reaction',[(1,'Sn',2),(1,'I2',0)],[(1,'Sn',4),(2,'I',-1)]),num('Cell potential',.540-.150,.390),num('Gibbs energy kJ',-2*96500*.390/1000,-75.27),num('Doubled reaction Gibbs',-4*96500*.390/1000,-150.54)])

add(725,'The same ion can be oxidized and reduced','R3.2',
r'The standard reduction potentials are $\mathrm{Cu^++e^-\rightleftharpoons Cu(s)}$, +0.520 V, and $\mathrm{Cu^{2+}+e^-\rightleftharpoons Cu^+}$, +0.150 V. Consider only these couples under standard conditions. Use $F=96500\ \mathrm{C\,mol^{-1}}$.',
[P('Construct the disproportionation reaction of Cu+ and explain its classification.',A(r'$\mathrm{2Cu^+\rightarrow Cu^{2+}+Cu(s)}$.'),R('One Cu+ loses an electron to become Cu2+ while another gains an electron to become Cu metal.'),R('The same reactant species is therefore both oxidized and reduced.')),
 P('Calculate its standard cell potential and Gibbs energy change, showing the number of electrons transferred per equation.',M(r'Cathodic Cu+/Cu is +0.520 V; the reversed Cu2+/Cu+ step supplies oxidation, so $E^\circ=0.520-0.150$.'),A('Cell potential is +0.370 V; one mole of electrons is transferred per 2 mol of Cu+ consumed.'),A(r'$\Delta G^\circ=-1(96500)(0.370)=-35.7\ \mathrm{kJ\,mol^{-1}}$.')),
 P('If 0.0400 mol of Cu+ disproportionates completely, find both product amounts. Explain why using n = 2 in the Gibbs equation would double-count the electron transfer.',M('The stoichiometric coefficients give one mole of each product from two moles of Cu+.'),A('0.0200 mol Cu2+ and 0.0200 mol Cu(s).'),R('The electron lost by one Cu+ is the same electron gained by the other; it is counted once as transferred, rather than once at each electrode.'))],
cell('Two roles for copper(I)','Cu(s)','Pt(s)',('Cu+(aq)','Cu+(aq), Cu2+(aq)')),
[balance('Disproportionation',[(2,'Cu',1)],[(1,'Cu',2),(1,'Cu',0)]),num('Transferred electron stoichiometry',1,1),num('Disproportionation potential',.520-.150,.370),num('Gibbs energy kJ',-96500*.370/1000,-35.705)])

add(726,'An electrode can replenish the electrolyte or consume water','R3.2',
r'An aqueous copper(II) sulfate electrolyte is electrolysed with either two inert electrodes or a copper anode and an inert cathode. Copper deposits at the cathode in both runs. The inert anode releases oxygen; the copper anode instead dissolves, with no gas. Treat electrolyte volume as constant and assume only the observed electrode processes. Each run deposits 0.0200 mol Cu from an initial 0.100 mol Cu2+ in 0.100 dm3.',
[P('Write the cathode half-equation and the two possible anode half-equations, with states.',A(r'Cathode: $\mathrm{Cu^{2+}(aq)+2e^-\rightarrow Cu(s)}$.'),A(r'Inert anode: $\mathrm{2H_2O(l)\rightarrow O_2(g)+4H^+(aq)+4e^-}$.'),A(r'Copper anode: $\mathrm{Cu(s)\rightarrow Cu^{2+}(aq)+2e^-}$.')),
 P('For the inert-anode run, find the final Cu2+ concentration, oxygen amount and amount of H+ generated.',M('Two moles of deposited copper require four moles of electrons, corresponding to one mole O2 and four moles H+.'),A('Final Cu2+ is 0.0800 mol in 0.100 dm3, giving 0.800 mol dm−3.'),A('O2 produced = 0.0100 mol; H+ generated = 0.0400 mol.')),
 P('Explain the different copper-ion trend for the copper-anode run, and compare the anode and cathode copper mass changes.',R('Anode dissolution produces the same amount of Cu2+ that the cathode consumes, so its total amount and concentration remain approximately unchanged.'),R('The anode loses the same copper mass that the cathode gains, assuming only these copper processes.'),R('The electrode material changes the available oxidation reaction; calling every anode inert would miss this material balance.'))],
cell('Aqueous copper sulfate electrolysis','anode material varied','inert cathode',('Cu2+(aq), SO4 2−(aq)',''),True),
[balance('Inert-anode net reaction',[(2,'Cu',2),(2,'H2O',0)],[(2,'Cu',0),(1,'O2',0),(4,'H',1)]),balance('Copper transfer',[(1,'Cu',0),(1,'Cu',2)],[(1,'Cu',2),(1,'Cu',0)]),num('Final copper concentration',(.100-.0200)/.100,.8),num('Oxygen mol',.0200/2,.0100)])

add(727,'A plating mass deficit reveals a competing reduction','R3.2',
r'A nickel anode supplies Ni2+ to an electroplating bath while a conducting object is coated at the other electrode. The anode loses 0.900 g Ni; the object gains only 0.810 g Ni. Assume all anode loss forms Ni2+, all object mass gain is Ni, and the remaining electron transfer produces H2 by $\mathrm{2H^++2e^-\rightarrow H_2}$. Use $M(Ni)=58.69\ \mathrm{g\,mol^{-1}}$. No current-time calculation is needed.',
[P('Identify the electrode connection needed for the object and write both nickel half-equations.',A('The object must be the negative cathode; nickel reduction deposits the coating there.'),A(r'$\mathrm{Ni^{2+}(aq)+2e^-\rightarrow Ni(s)}$ at the object.'),A(r'$\mathrm{Ni(s)\rightarrow Ni^{2+}(aq)+2e^-}$ at the positive nickel anode.')),
 P('Calculate the fraction of the supplied electron transfer that deposits nickel and the net increase in Ni2+ amount in the bath.',M('Both nickel processes transfer 2 mol electrons per mole Ni, so their electron-transfer ratio equals the nickel mass ratio.'),A('Depositing fraction $=0.810/0.900=0.900$, or 90.0%.'),A(r'Ni2+ increase $=(0.900-0.810)/58.69=1.53\times10^{-3}$ mol.')),
 P('Find the amount of hydrogen evolved and explain why anode mass loss alone cannot be used as the coating mass.',M('The difference in nickel-equivalent moles corresponds to 2 electron moles per mole; producing one H2 also requires 2 electron moles.'),A(r'$n(H_2)=0.0900/58.69=1.53\times10^{-3}$ mol.'),R('A competing reduction diverts electrons away from metal deposition, leaving some newly formed Ni2+ in solution.'))],
cell('Nickel electroplating circuit','nickel anode','conducting object',('Ni2+(aq), H+(aq)',''),True),
[balance('Nickel oxidation',[(1,'Ni',0)],[(1,'Ni',2),(2,'e',-1)]),balance('Hydrogen side reduction',[(2,'H',1),(2,'e',-1)],[(1,'H2',0)]),num('Electron deposition fraction',.810/.900,.9),num('Net nickel increase mol',.09/58.69,.0015334810018742546)])

brine=cell('Separated compartments in brine electrolysis','inert electrode X','inert electrode Y',('Na+(aq), Cl−(aq), water',''),True).replace('</svg>',line(320,190,320,338,True)+text(320,180,'membrane',14)+'</svg>')
add(728,'Gas ratios distinguish brine and water electrolysis','R3.2',
r'Concentrated aqueous NaCl is electrolysed in separated compartments with inert electrodes. Under the stated operating conditions the observed anode product is Cl2 and the cathode product is H2; a membrane prevents chlorine contacting the cathodic alkaline solution. In a separate dilute solution under conditions favouring water oxidation, the observed gases are O2 and H2. Product identities are supplied, so no overpotential or Nernst calculation is required.',
[P('Write the half-equations for the concentrated-brine run and identify the origin of hydrogen.',A(r'Anode: $\mathrm{2Cl^-(aq)\rightarrow Cl_2(g)+2e^-}$.'),A(r'Cathode: $\mathrm{2H_2O(l)+2e^-\rightarrow H_2(g)+2OH^-(aq)}$.'),R('Hydrogen comes from water reduction; sodium ions remain aqueous rather than being deposited as sodium metal.')),
 P('The brine run produces 0.0120 mol Cl2. Find the hydrogen amount and the pH if the generated hydroxide is retained in a final cathode-solution volume of 0.200 dm3.',M('Equal two-electron gas steps give 0.0120 mol H2 and 0.0240 mol OH−.'),M(r'$[OH^-]=0.0240/0.200=0.120$; $pH=14+\log_{10}(0.120)$.'),A('pH = 13.079.')),
 P('For the dilute water-oxidation run, write an anode equation and deduce the H2:O2 gas-volume ratio at equal temperature and pressure. Explain why the two experiments have different gas ratios.',A(r'$\mathrm{2H_2O\rightarrow O_2+4H^++4e^-}$ at the anode.'),A('H2:O2 is 2:1, whereas H2:Cl2 in the concentrated-brine run is 1:1.'),R('One O2 releases four electrons but one H2 consumes only two; one Cl2 releases two. The ratios follow electron balance, not the initial salt formula alone.'))],
brine,
[balance('Chlorine anode',[(2,'Cl',-1)],[(1,'Cl2',0),(2,'e',-1)]),balance('Water reduction',[(2,'H2O',0),(2,'e',-1)],[(1,'H2',0),(2,'OH',-1)]),balance('Water electrolysis overall',[(2,'H2O',0)],[(2,'H2',0),(1,'O2',0)]),num('Hydroxide concentration',.024/.2,.12)])

def cyanide_substitution(arrows=False):
 b=text(55,220,'N',24)+text(145,220,'C',24)
 for yy in [204,212,220]:b+=line(73,yy,126,yy)
 b+=pair(30,212,False)+pair(168,212,False)+text(151,180,'−',20)
 b+=text(340,220,'C',24)+text(470,220,'Br',24)+line(355,212,445,212)
 b+=text(340,115,'H',22)+line(340,133,340,193)+text(340,318,'H',22)+line(340,233,340,293)
 b+=text(240,220,'CH3CH2',20)+line(290,212,325,212)
 if arrows:b+=curly((168,212),(205,145),(280,150),(325,204))+curly((400,212),(415,265),(460,265),(470,234))
 return svg(b,'Cyanide carbon attacks a primary halogenoalkane')
add(729,'A substitution builds one extra carbon into the chain','R3.4',
r'1-Bromopropane reacts with cyanide, CN−, by the concerted SN2 pathway. Cyanide attacks through its carbon atom. The diagram gives a condensed ethyl group attached to the electrophilic CH2 centre and shows the cyanide lone pair. Ignore competing pathways and solvent effects.',
[P('Write the substitution equation and give the product’s carbon skeleton and functional-group name.',A(r'$\mathrm{CH_3CH_2CH_2Br+CN^-\rightarrow CH_3CH_2CH_2CN+Br^-}$.'),A('The product has four carbons in its principal chain and is butanenitrile.'),R('Cyanide contributes a carbon atom; replacing Br by CN does not leave the original carbon count unchanged.')),
 P('Describe the two curly arrows, the approach direction and whether a free carbocation is an intermediate.',R('The donor arrow begins at cyanide’s carbon lone pair and ends at the carbon bearing Br.'),R('The C–Br bonding pair moves to Br; attack is from the side opposite the C–Br bond.'),R('Bond formation and bond breaking occur in one concerted step; there is a transition state, not a separately formed carbocation intermediate.')),
 P('Explain the distinction between a transition state and an intermediate, and account for all charges in the net equation.',R('A transition state is a maximum-energy arrangement along the reaction coordinate, not an isolable species occupying an energy minimum.'),R('An intermediate would be a discrete species formed in one step and consumed in another; that is not the stated SN2 path.'),R('The total −1 charge moves from the nucleophile to bromide; the nitrile product is neutral and no free electron is released.'))],
cyanide_substitution(),
[balance('Cyanide substitution carbon/charge',[(1,'C3H7Br',0),(1,'CN',-1)],[(1,'C4H7N',0),(1,'Br',-1)]),num('Cyanide carbon valence electrons',4+1+5,10),num('New principal-chain carbons',3+1,4)],
cyanide_substitution(True))

def tert_halide():
 b=text(320,220,'C',25)+text(470,220,'Cl',25)+line(337,211,445,211)
 for x,y,lab in [(180,220,'CH3'),(320,105,'CH3'),(320,335,'CH3')]:
  b+=line(320+(x-320)*.15,211+(y-211)*.15,x+(320-x)*.22,y+(211-y)*.22)+text(x,y+8,lab,23)
 return svg(b,'Tertiary halogenoalkane before reaction with water')
def cation_capture():
 body=tertiary_cation().split('</svg>')[0]
 body+=text(520,220,'O',24)+text(520,125,'H',22)+line(520,145,520,194)+text(595,265,'H',22)+line(538,226,578,252)
 body+=pair(492,213,False)+pair(533,185)+curly((492,213),(430,140),(370,150),(329,211))
 return body+text(320,395,'A water lone pair supplies both electrons in the new C–O bond.',14)+'</svg>'
add(730,'A tertiary substitution passes through an oxonium ion','R3.4',
r'2-Chloro-2-methylpropane reacts with water by an SN1 pathway. A carbocation is formed before water attacks. The final organic product is 2-methylpropan-2-ol. Include the proton-transfer step needed after water attack; do not use hydroxide as the attacking species in this specified mechanism.',
[P('Describe the first electron-pair movement and draw or describe the carbocation, including its charge and carbon bonding.',R('The C–Cl bonding pair moves to chlorine, so the C–Cl bond breaks heterolytically.'),A(r'$\mathrm{(CH_3)_3CCl\rightarrow (CH_3)_3C^++Cl^-}$.'),R('The positively charged central carbon has three sigma bonds and an empty orbital; it is approximately trigonal planar.')),
 P('Explain water attack and identify the immediate product, including the oxygen charge.',R('A lone pair on the water oxygen is donated to the carbocation carbon.'),A(r'$\mathrm{(CH_3)_3C^++H_2O\rightarrow (CH_3)_3COH_2^+}$.'),R('The attacking oxygen now has three bonds and one lone pair, giving an oxonium ion with formal charge +1.')),
 P('Write the final proton-transfer step and the overall equation with water. Explain why omitting this final step gives the wrong final organic charge.',A(r'$\mathrm{(CH_3)_3COH_2^++H_2O\rightarrow (CH_3)_3COH+H_3O^+}$.'),A(r'Overall: $\mathrm{(CH_3)_3CCl+2H_2O\rightarrow (CH_3)_3COH+H_3O^++Cl^-}$.'),R('Loss of a proton returns the alcohol oxygen to two bonds and two lone pairs; the isolated alcohol is neutral, not an oxonium ion.'))],
tert_halide(),
[balance('Tertiary ionization',[(1,'C4H9Cl',0)],[(1,'C4H9',1),(1,'Cl',-1)]),balance('Water capture',[(1,'C4H9',1),(1,'H2O',0)],[(1,'C4H11O',1)]),balance('Oxonium deprotonation',[(1,'C4H11O',1),(1,'H2O',0)],[(1,'C4H10O',0),(1,'H3O',1)]),num('Oxonium oxygen formal charge',6-2-3,1)],
cation_capture())

def stereo_panel(cx,leftlow,rightlow,label):
 cy=195;b=text(cx,cy,'C',22)+text(cx,62,label,16)
 b+=line(cx-13,cy-12,cx-46,cy-45)+text(cx-55,cy-53,'CH3',17)
 b+=line(cx+13,cy-12,cx+46,cy-45)+text(cx+55,cy-53,'C2H5',17)
 # Solid wedge points from the stereocentre toward the observer.
 b+=f'<path d="M{cx-5} {cy+13}L{cx-55} {cy+70}L{cx-37} {cy+79}Z" fill="#111"/>'
 b+=text(cx-50,cy+105,leftlow,18)
 # Hashed wedge recedes; widening crossbars are confined to the bond.
 for i in range(1,8):
  t=i/8;x=cx+6+42*t;y=cy+13+61*t;w=1+7*t
  b+=line(x-w,y+w*.7,x+w,y-w*.7)
 b+=text(cx+56,cy+105,rightlow,18)
 return b
add(731,'Recognizing inversion from three-dimensional structures','R3.4',
r'An optically active sample of 2-bromobutane undergoes substitution with hydroxide. For this question the reaction is known to follow only an SN2 pathway; no inference from solvent or rate data is required. The reactant and candidate alcohol products P and Q are shown with the same two carbon groups held in the plane. A solid wedge points towards the observer and a hashed wedge points away. No R/S descriptors are needed.',
[P('Select the product consistent with the specified pathway and explain the stereochemical change.',A('Q is consistent with SN2 inversion.'),R('The entering hydroxy group approaches from the side opposite the departing C–Br bond.'),R('With the two in-plane carbon groups held fixed, the positions of H and the entering group reverse their towards/away arrangement.')),
 P('Explain why P represents retention in this comparison and why optical activity alone does not identify the reaction mechanism.',R('P replaces Br by OH in the same away-pointing position while H remains towards the observer, retaining the arrangement shown.'),R('Optical activity establishes a non-racemic chiral sample, not a unique pathway for every possible reaction.'),R('Secondary halogenoalkanes can follow different substitution pathways; the pure SN2 condition is an explicit premise here.')),
 P('Write the net ionic equation and account for oxygen bonding and charge in the neutral product.',A(r'$\mathrm{CH_3CHBrCH_2CH_3+OH^-\rightarrow CH_3CHOHCH_2CH_3+Br^-}$.'),R('Oxygen donates a lone pair to make C–O while retaining its O–H bond.'),R('The alcohol oxygen has two bonds and two lone pairs and is neutral; the overall −1 charge is carried by bromide.'))],
svg(stereo_panel(115,'H','Br','Reactant')+stereo_panel(320,'H','OH','P')+stereo_panel(525,'OH','H','Q')+text(320,385,'Solid wedge: towards observer; hashed wedge: away.',15),'Substitution at a stereogenic carbon'),
[balance('Secondary hydroxide substitution',[(1,'C4H9Br',0),(1,'OH',-1)],[(1,'C4H10O',0),(1,'Br',-1)]),num('Stereocentre distinct substituent types',len(set(['H','CH3','C2H5','Br'])),4),num('Alcohol oxygen formal charge',6-4-2,0)])

extent=lambda t,tau:1-math.exp(-t/tau)
add(732,'The leaving-group comparison must keep the carbon skeleton fixed','R3.4',
r'Comparable hydrolysis experiments use CH3CH2Cl, CH3CH2Br and CH3CH2I at the same concentration, temperature and solvent composition. The plotted fractions reacted are experimental models for this comparison, not a request to infer rate laws. Their carbon–halogen bond enthalpies are 338, 276 and 238 kJ mol−1 respectively. A separately added AgNO3 test detects halide released after a fixed reaction period.',
[P('Rank the hydrolysis rates from the plots and explain the trend using leaving-group evidence.',A('CH3CH2I reacts fastest, then CH3CH2Br, then CH3CH2Cl.'),R('The C–I bond is the weakest of the supplied set and is broken more readily in the controlled comparison.'),R('I− is a better leaving group than Br−, which is better than Cl−; all three substrates share the same carbon structure, making the comparison meaningful.')),
 P('Write the net hydrolysis equation for the bromide and the ionic equation for detecting its released halide.',A(r'$\mathrm{CH_3CH_2Br+OH^-\rightarrow CH_3CH_2OH+Br^-}$.'),A(r'$\mathrm{Ag^++Br^-\rightarrow AgBr(s)}$.'),R('The precipitate detects halide released into solution; it is not evidence that silver directly replaces bromine on the organic molecule.')),
 P('Explain why these data cannot establish a solvent effect or distinguish SN1 from SN2 by themselves.',R('The solvent is held constant, so the experiment contains no controlled comparison between solvents.'),R('The displayed extent curves and bond data do not by themselves specify a complete rate law or reveal an intermediate.'),R('Changing several substrate features simultaneously would confound the leaving-group comparison; the fixed ethyl skeleton avoids that error.'))],
curve('Controlled hydrolysis extent comparison',lambda t:extent(t,180),(0,400),'Time / s','Fraction reacted',(0,1.1),extra=[('',[(t,extent(t,70)) for t in range(0,401,2)]),('',[(t,extent(t,25)) for t in range(0,401,2)])]).replace('</svg>',text(155,128,'I',15)+text(250,130,'Br',15)+text(500,160,'Cl',15)+'</svg>'),
[balance('Bromoethane hydrolysis',[(1,'C2H5Br',0),(1,'OH',-1)],[(1,'C2H6O',0),(1,'Br',-1)]),balance('Halide test',[(1,'Ag',1),(1,'Br',-1)],[(1,'AgBr',0)]),truth('Same-time extents preserve supplied order',extent(80,25)>extent(80,70)>extent(80,180))])

def alkene_dbr(arrows=False):
 b=text(105,248,'CH3',23)+text(270,248,'CH',23)+text(445,248,'CH2',23)+line(136,238,245,238)+line(296,231,410,231)+line(296,241,410,241)
 b+=text(335,115,'D',24)+text(485,115,'Br',24)+line(353,105,458,105)
 if arrows:b+=curly((351,231),(290,200),(295,130),(332,127))+curly((405,105),(420,60),(475,65),(484,91))
 return svg(b,'Propene reacts with deuterium bromide')
add(733,'Tracing deuterium through an unsymmetrical addition','R3.4',
r'Propene reacts with DBr, where D is hydrogen-2. Treat D+ chemically as H+ for this mechanism and ignore isotope effects. Two carbocation pathways are possible. No rearrangement occurs. The more stable carbocation pathway gives the major product.',
[P('Describe the first pair of curly arrows and identify the more stable carbocation, including the location of D.',R('A pair from the C=C bond is donated to D; the D–Br bonding pair moves to Br.'),A(r'The more stable intermediate is $\mathrm{CH_3C^+(H)CH_2D}$, with D on the terminal carbon.'),R('Its positive carbon is secondary; adding D to the middle carbon instead would leave a less stable primary carbocation at the end.')),
 P('Identify the nucleophile in the second step and draw or give the condensed formula of the major organic product.',A('Br− attacks by donating a bromide lone pair to the positively charged carbon.'),A(r'Major product $\mathrm{CH_3CH(Br)CH_2D}$.'),R('The more substituted carbocation is stabilized by electron donation from adjacent alkyl groups; the reasoning concerns the intermediate, rather than an unsupported preference for a product name.')),
 P('Give the minor product and explain how both products preserve carbon valence four while retaining all six original ordinary hydrogen atoms.',A(r'Minor product $\mathrm{CH_3CH(D)CH_2Br}$.'),R('In each pathway the carbon receiving D gains one sigma bond as the double bond becomes a single bond; carbon still has total bond order four.'),R('The original six ordinary hydrogens remain, and D plus Br are added across the former double bond; no hydrogen is displaced in this addition.'))],
alkene_dbr(),
[balance('Isotope-labelled addition',[(1,'C3H6',0),(1,'DBr',0)],[(1,'C3H6DBr',0)]),balance('Ionization bookkeeping',[(1,'C3H6',0),(1,'DBr',0)],[(1,'C3H6D',1),(1,'Br',-1)]),num('Secondary cation carbon sigma bonds',2+1,3)],
alkene_dbr(True))

def hydronium_attack():
 b=text(125,210,'CH2',24)+text(285,210,'CH2',24)+line(160,194,250,194)+line(160,206,250,206)
 b+=text(480,210,'O',24)+text(480,115,'H',22)+line(480,134,480,183)+text(580,210,'H',22)+line(498,201,560,201)+text(480,310,'H',22)+line(480,226,480,284)
 b+=pair(453,202,False)+text(508,177,'+',22)
 return svg(b,'Alkene and hydronium before acid-catalysed hydration')
add(734,'The water oxygen enters while the acid catalyst returns','R3.4',
r'Ethene is hydrated in an acidic aqueous mixture. The reactive water is enriched in oxygen-18; treat its oxygen as 18O for tracing and ignore isotope exchange after product formation. Hydronium provides a proton in the first step. The final alcohol is neutral. No special acid reagent or electrophile-generation recipe is required.',
[P('Describe the first electron-pair movements and write the carbocation-forming equation.',R('A C=C electron pair moves toward a proton on H3O+.'),R('The electrons in that O–H bond move back onto oxygen, so the proton donor becomes water.'),A(r'$\mathrm{C_2H_4+H_3O^+\rightarrow C_2H_5^++H_2O}$.')),
 P('Explain attack by labelled water and give the charged intermediate and neutral organic product, retaining the oxygen label.',R('A lone pair on labelled water oxygen is donated to the carbocation carbon.'),A(r'Intermediate $\mathrm{C_2H_5{}^{18}OH_2^+}$; neutral product $\mathrm{C_2H_5{}^{18}OH}$.'),R('Oxygen has three bonds and +1 formal charge in the intermediate, then two bonds and no charge after deprotonation.')),
 P('Write the proton-transfer step in words or an equation, and explain which species is a catalyst and which supplies the product oxygen.',A('A water molecule accepts a proton from the protonated alcohol, producing neutral labelled ethanol and regenerating H3O+.'),R('Hydronium is regenerated, so it is the acid catalyst rather than a net reactant.'),R('The nucleophilic labelled water supplies the alcohol oxygen; the hydronium oxygen from the first step is not transferred into the carbon skeleton in this traced pathway.'))],
hydronium_attack(),
[balance('Hydronium protonation',[(1,'C2H4',0),(1,'H3O',1)],[(1,'C2H5',1),(1,'H2O',0)]),balance('Water capture atom/charge',[(1,'C2H5',1),(1,'H2O',0)],[(1,'C2H7O',1)]),balance('Catalyst regeneration',[(1,'C2H7O',1),(1,'H2O',0)],[(1,'C2H6O',0),(1,'H3O',1)]),num('Net water molecules consumed',2-1,1)])

def benzene_diagram(solution=False):
 cx,cy,r=320,235,95;pts=[(cx+r*math.sin(i*math.pi/3),cy-r*math.cos(i*math.pi/3)) for i in range(6)]
 b=''
 for i in range(6):b+=line(*pts[i],*pts[(i+1)%6])
 for i in ([2,4] if solution else [0,2,4]):
  a,c=pts[i],pts[(i+1)%6];aa=(cx+(a[0]-cx)*.82,cy+(a[1]-cy)*.82);cc=(cx+(c[0]-cx)*.82,cy+(c[1]-cy)*.82);b+=line(*aa,*cc)
 if solution:
  b+=line(320,140,286,95)+text(279,82,'H',20)+line(320,140,355,95)+text(361,82,'E',20)+text(430,184,'+',24)
  b+=text(178,93,'B',20)+pair(197,85,False)
  b+=curly((197,85),(223,51),(254,55),(274,69))
  b+=curly((303,117.5),(335,100),(374,123),(361.136,163.75))
 else:
  b+=text(320,75,'E+',24)+curly((353.732,176.575),(392,110),(352,82),(320,92))
 b+=text(320,394,'E+ is supplied as NO2+; its generation is not part of the question.',14)
 return svg(b,'Sigma-complex deprotonation and aromatic restoration' if solution else 'Benzene attacks a supplied charged electrophile')
add(735,'Restoring aromaticity completes electrophilic substitution','R3.4',
r'Benzene reacts with a supplied nitronium electrophile, $E^+=\mathrm{NO_2^+}$. The diagram shows the initial electron-pair attack. Formation of the electrophile is outside this question. A neutral base B with an available lone pair removes a proton from the sigma complex.',
[P('Describe the electron-pair origin in the first step and the bonding and charge of the sigma complex.',R('An electron pair from a benzene carbon–carbon pi bond is donated to E+ to form a C–E sigma bond.'),R('The attacked carbon temporarily has four sigma bonds: two ring bonds, H and E; it is no longer part of a continuous six-electron aromatic ring.'),A('The intermediate has overall charge +1, delocalized over the remaining conjugated part of the ring; it is not the final neutral product.')),
 P('Describe the two electron-pair movements during proton removal and state both products of that step.',R('A base lone pair moves toward the H attached to the carbon bearing E.'),R('The C–H bonding pair returns to the ring to form the missing pi bond, restoring aromaticity.'),A('Products are substituted benzene, C6H5E, and BH+; the proton leaves, not a neutral H atom or hydride.')),
 P('Write the net reaction for E+ = NO2+ and explain why the overall process is substitution rather than addition.',A(r'$\mathrm{C_6H_6+NO_2^+\rightarrow C_6H_5NO_2+H^+}$, with the proton accepted by B in the actual final step.'),R('One ring H is replaced by NO2 and the aromatic pi system is restored.'),R('Stopping at an addition-like sigma complex would retain the positive, non-aromatic intermediate instead of completing the favourable aromatic restoration.'))],
benzene_diagram(),
[balance('Net nitronium substitution',[(1,'C6H6',0),(1,'NO2',1)],[(1,'C6H5NO2',0),(1,'H',1)]),balance('Sigma-complex formation',[(1,'C6H6',0),(1,'NO2',1)],[(1,'C6H6NO2',1)]),num('Sigma complex attacked-carbon bond count',2+1+1,4)],
benzene_diagram(True))

def finish():
 assert len(QUESTIONS)==35 and [q['number'] for q in QUESTIONS]==list(range(701,736))
 assert collections.Counter(q['level'] for q in QUESTIONS)=={'sl':14,'ahl':21}
 assert all(q['difficulty']=='hard' and q['calculator'] for q in QUESTIONS)
 assert len({q['stem'] for q in QUESTIONS})==35 and len({q['title'] for q in QUESTIONS})==35
 for q in QUESTIONS:
  for p,g in zip(q['parts'],q['markScheme']):assert p['marks']==sum(int(s['code'][1:]) for s in g['steps'])
  for t in [q['stem'],*[p['prompt'] for p in q['parts']],*[s['text'] for g in q['markScheme'] for s in g['steps']]]:
   assert not re.search(r'[\x00-\x08\x0b-\x1f]',t),(q['id'],'control character')
  q['verification']['notes']+=' Credit valid alternative chemical explanations and balanced equivalent forms. Apply error carried forward for later calculations only when the earlier value remains chemically admissible; do not credit an invalid mechanism or impossible species.'
 out=ROOT/'content/ib/chemistry-2026-expansion/mechanisms.json';out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(QUESTIONS,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
 report=dict(status='author self-review passed; separate review pending',questions=35,levels=dict(collections.Counter(q['level'] for q in QUESTIONS)),difficulty='hard',diagramCount=sum(bool(q.get('diagramSvg')) for q in QUESTIONS),workedMechanismDiagrams=sum(bool(q.get('markSchemeDiagramSvg')) for q in QUESTIONS),marks=sum(q['marks'] for q in QUESTIONS),specification='Chemistry first assessment 2025, current R3.1–R3.4; shared SL/AHL split follows official guide and repository blueprint.',officialGuide='https://www.ibo.org/globalassets/new-structure/university-admission/pdfs/subject-guides/chemistry-guide.pdf',provenance='Original syllabus-authored practice and instructional M/A/R allocation, not official past-paper content or an official IB markscheme.',limits=['Separate AI review and rendered diagram checks are release requirements.','This is not human IB examiner moderation.'],records=REVIEWS,sha256=hashlib.sha256(out.read_bytes()).hexdigest())
 path=ROOT/'docs/ib-2026-chemistry/mechanisms-author-review.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
 print(json.dumps({k:report[k] for k in ['questions','levels','diagramCount','workedMechanismDiagrams','marks']}))
if __name__=='__main__':finish()
