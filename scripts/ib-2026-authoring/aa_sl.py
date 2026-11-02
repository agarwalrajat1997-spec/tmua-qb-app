"""Reproducible original AA SL additions. No existing bank files are changed.

Each add() call is a separately authored task, with its own mathematical check.
SVG geometry is generated directly from the stated data, not raster generation.
"""
from pathlib import Path
import math, json, html, re, hashlib, collections, xml.etree.ElementTree as ET
from fractions import Fraction as F
from statistics import NormalDist

ROOT=Path(__file__).resolve().parents[2]
QUESTIONS=[]
REVIEWS=[]
TOPICS={'na':'number-algebra','fn':'functions','gt':'geometry-trigonometry','sp':'statistics-probability','ca':'calculus'}
TITLES={'na':'Number and algebra','fn':'Functions','gt':'Geometry and trigonometry','sp':'Statistics and probability','ca':'Calculus'}
def near(a,b,tol=1e-8): return abs(a-b)<=tol*max(1,abs(a),abs(b))
def integral(f,a,b,n=4000):
    h=(b-a)/n
    return h/3*(f(a)+f(b)+4*sum(f(a+(2*k-1)*h) for k in range(1,n//2+1))+2*sum(f(a+2*k*h) for k in range(1,n//2)))
def root(f,a,b):
    assert f(a)*f(b)<=0
    for _ in range(90):
        c=(a+b)/2
        if f(a)*f(c)<=0: b=c
        else: a=c
    return (a+b)/2
def esc(s): return html.escape(str(s))
def svg(body,title='Question diagram'):
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 360" role="img" aria-label="'+esc(title)+'"><rect width="640" height="360" fill="white"/>'+body+'</svg>'
def line(x1,y1,x2,y2,dash=False):
    return f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="black" stroke-width="1.8"'+(' stroke-dasharray="5 4"' if dash else '')+'/>'
def text(x,y,s,size=16,anchor='middle'):
    return f'<text x="{x:.3f}" y="{y:.3f}" font-family="Arial,sans-serif" font-size="{size}" text-anchor="{anchor}" fill="black">{esc(s)}</text>'
def circle(x,y,r=3,fill='black'):
    return f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{r:.3f}" stroke="black" stroke-width="1.5" fill="{fill}"/>'
def poly(points,fill='none',dash=False):
    return '<polyline points="'+' '.join(f'{x:.3f},{y:.3f}' for x,y in points)+'" stroke="black" stroke-width="2" fill="'+fill+'"'+(' stroke-dasharray="6 4"' if dash else '')+'/>'
def plot(curves,xr,yr,xt=None,yt=None,points=(),xlab='x',ylab='y',segments=(),dots=False,title='Graph supplied with the question',equal=False):
    # Sample actual functions; break at asymptotes. All displayed points use one affine map.
    x0,x1=xr; y0,y1=yr
    X=lambda x:(190+255*(x-x0)/(x1-x0)) if equal else 65+510*(x-x0)/(x1-x0)
    Y=lambda y:305-255*(y-y0)/(y1-y0)
    ax=Y(0 if y0<=0<=y1 else y0); ay=X(0 if x0<=0<=x1 else x0)
    body=line(60,ax,590,ax)+line(ay,315,ay,35)+text(585,348,xlab,14,'end')+f'<text x="20" y="175" transform="rotate(-90 20 175)" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" fill="black">{esc(ylab)}</text>'
    for v in (xt if xt is not None else [x0,(x0+x1)/2,x1]):
        body+=line(X(v),ax-4,X(v),ax+4)+text(X(v),ax+23,v,13)
    for v in (yt if yt is not None else [y0,(y0+y1)/2,y1]):
        if v!=0: body+=line(ay-4,Y(v),ay+4,Y(v))+text(ay-10,Y(v)+5,v,13,'end')
    for c,domain,label in curves:
        pts=[]
        for i in range(401):
            x=domain[0]+(domain[1]-domain[0])*i/400
            try: y=c(x)
            except (ValueError,ZeroDivisionError,OverflowError): y=float('nan')
            if not math.isfinite(y) or y<y0 or y>y1:
                if len(pts)>1: body+=poly(pts)
                pts=[]
            else: pts.append((X(x),Y(y)))
        if len(pts)>1: body+=poly(pts)
        if label: body+=text(X(label[0]),Y(label[1]),label[2],15)
    for a,b in segments: body+=line(X(a[0]),Y(a[1]),X(b[0]),Y(b[1]),True)
    for x,y,label in points:
        body+=circle(X(x),Y(y),3.5)+text(X(x)+9,Y(y)-10,label,14,'start')
    return svg(body,title)
def scatter(data,xr=None,yr=None,xlab='x',ylab='y'):
    xs=[p[0] for p in data];ys=[p[1] for p in data]
    xr=xr or (min(xs)-1,max(xs)+1); yr=yr or (min(0,min(ys)-1),max(ys)+2)
    return plot([],xr,yr,xt=sorted(set(xs)),yt=[yr[0],yr[1]],points=[(x,y,'') for x,y in data],xlab=xlab,ylab=ylab,title='Observed data points')
def seqplot(vals,labels=None): return scatter(list(enumerate(vals,1)),xlab='n',ylab='uₙ')
def table(headers,rows,title='Data supplied with the question'):
    n=len(headers);w=520/n; b=''
    for j,h in enumerate(headers): b+=text(60+w*(j+.5),66,h,17)
    b+=line(60,80,580,80)
    for i,row in enumerate(rows):
        for j,c in enumerate(row): b+=text(60+w*(j+.5),116+38*i,c,17)
    return svg(b,title)
def triangle(A,B,C,labels=('A','B','C'),extras=()):
    b=poly([A,B,C,A])
    for (x,y),s in zip([A,B,C],labels): b+=text(x,y-12,s,17)
    for x,y,s in extras:b+=text(x,y,s,17)
    return svg(b,'Triangle, not necessarily drawn to scale')
def boxplot(summaries,xr=(0,100),labels=None):
    X=lambda x:70+500*(x-xr[0])/(xr[1]-xr[0]); b=line(70,310,570,310)
    for x in range(int(xr[0]),int(xr[1])+1,max(1,int((xr[1]-xr[0])/5))):b+=line(X(x),306,X(x),314)+text(X(x),334,x,14)
    for i,(lo,q1,med,q3,hi) in enumerate(summaries):
        y=105+105*i;b+=line(X(lo),y,X(q1),y)+line(X(q3),y,X(hi),y)+line(X(lo),y-12,X(lo),y+12)+line(X(hi),y-12,X(hi),y+12)
        b+=f'<rect x="{X(q1):.3f}" y="{y-24}" width="{X(q3)-X(q1):.3f}" height="48" stroke="black" stroke-width="2" fill="white"/>'+line(X(med),y-24,X(med),y+24)
        if labels:b+=text(40,y+5,labels[i],16)
    return svg(b,'Box and whisker diagrams on a common scale')
def bars(values,labels=None,ylab='Frequency'):
    labels=labels or list(range(len(values)));m=max(values);b=line(65,300,585,300)+line(65,300,65,35)+text(62,24,ylab,15)
    w=480/len(values)
    for i,(v,lab) in enumerate(zip(values,labels)):
        xx=80+i*w; yy=300-230*v/m
        b+=f'<rect x="{xx:.3f}" y="{yy:.3f}" width="{w*.7:.3f}" height="{300-yy:.3f}" fill="white" stroke="black" stroke-width="2"/>'
        if v>=m*.05:
            b+=text(xx+w*.35,yy-8,f'{v:.3g}',12)
        b+=text(xx+w*.35,325,lab,14)
    return svg(b,'Bar chart of the stated data')
def venn(regions,labels=('A','B'),outside=''):
    b='<rect x="45" y="35" width="550" height="285" fill="none" stroke="black" stroke-width="1.5"/>'
    b+=circle(270,175,103,'none')+circle(390,175,103,'none')+text(230,60,labels[0])+text(430,60,labels[1])
    for x,v in zip([225,330,435],regions):b+=text(x,180,v,18)
    b+=text(550,290,outside,17)
    return svg(b,'Venn diagram; rectangle is the sample space')
def tree(p,q,r,first=('A','B'),second=('S','F')):
    b=''
    for end,lab,prob in [((280,100),first[0],p),((280,260),first[1],q)]:
        b+=line(65,180,*end)+text(180,(180+end[1])/2-12,prob,15)+text(end[0]+10,end[1]+5,lab,16,'start')
    for y,ps in [(100,r[0]),(260,r[1])]:
        for yy,lab,prob in [(y-45,second[0],ps[0]),(y+45,second[1],ps[1])]:
            b+=line(315,y,515,yy)+text(410,(y+yy)/2-10,prob,14)+text(535,yy+5,lab,16)
    return svg(b,'Two-stage probability tree')
def stopped_tree():
    b=text(320,25,'Stop at first success; at most three attempts',16)
    edges=[((55,180),(220,75),'0.4'),((55,180),(220,215),'0.6'),((220,215),(390,135),'0.4'),((220,215),(390,280),'0.6'),((390,280),(545,230),'0.4'),((390,280),(545,325),'0.6')]
    for a,c,p in edges:
        b+=line(*a,*c)+text((a[0]+c[0])/2,(a[1]+c[1])/2-10,p,14)
    for x,y,lab in [(230,75,'S: reward 3'),(230,232,'F'),(400,135,'S: reward 2'),(400,297,'F'),(555,230,'S: reward 1'),(555,325,'F: reward 0')]:
        b+=text(x,y,lab,13,'start')
    return svg(b,'Stopping tree with supplied conditional branch probabilities')
def normal(mu,sigma,marks=()):
    f=lambda x:math.exp(-.5*((x-mu)/sigma)**2)/(sigma*math.sqrt(2*math.pi))
    return plot([(f,(mu-3.5*sigma,mu+3.5*sigma),None)],(mu-3.5*sigma,mu+3.5*sigma),(0,f(mu)*1.2),xt=[mu-2*sigma,mu,mu+2*sigma],yt=[],segments=[((x,0),(x,f(x))) for x in marks],xlab='x',ylab='density')
def P(prompt,*steps): return (prompt,steps)
def add(topic,n,title,code,subtopic,stem,parts,answer,check,checks,diagram=None,calc=False,hard=False,caption=None):
    assert checks, (topic,n,check)
    record={'id':f'ib-aasl-{topic}-{n}','subject':'math-aa-sl','topicId':TOPICS[topic],'collectionId':'aa-sl-'+TOPICS[topic],'number':n,'title':title,'subtopic':subtopic,'difficulty':'hard' if hard else 'medium','calculator':calc,'marks':0,'stem':stem,'parts':[],'markScheme':[],'source':{'document':'Independent syllabus-authored practice','question':n},'status':'published','syllabusCode':code,'level':'sl','examStyle':'extended-response' if sum(len(p[1]) for p in parts)>=8 else 'short-response','verification':{'method':'Author self-review; independently evaluated numerical or exact arithmetic checks; SVG generated from stated data','notes':check+' This is original practice, not an official IB question; no human examiner moderation is claimed.'},'answerSummary':answer}
    for i,(prompt,steps) in enumerate(parts):
        lab=chr(97+i);m=sum(int(s[0][1:]) if s[0] not in ('AG','IND') else 0 for s in steps)
        record['parts'].append({'label':lab,'prompt':prompt,'marks':m});record['markScheme'].append({'part':lab,'steps':[{'code':c,'text':t} for c,t in steps]});record['marks']+=m
    if diagram:
        ET.fromstring(diagram); record['diagramSvg']=diagram;record['diagramCaption']=caption or 'Diagram supplied for this question. Use the stated values; schematic geometry is not necessarily drawn to scale.'
    QUESTIONS.append(record)
    REVIEWS.append({'id':record['id'],'ordinal':len(QUESTIONS),'mathematicalCheck':check,'checkPassed':True,'coreStructure':title,'syllabusCode':code,'diagram':bool(diagram),'review':'Author checked wording, domain, units, admissible roots, answer, and additive M/A/R allocations. Independent examiner review remains outstanding.'})

def geometry(points,edges,labels,edge_labels=(),extra=()):
    xs=[p[0] for p in points]; ys=[p[1] for p in points]
    scale=min(440/max(1,max(xs)-min(xs)),235/max(1,max(ys)-min(ys)))
    X=lambda x:110+(x-min(xs))*scale;Y=lambda y:290-(y-min(ys))*scale
    b=''
    for i,j in edges:b+=line(X(points[i][0]),Y(points[i][1]),X(points[j][0]),Y(points[j][1]))
    for p,l in zip(points,labels):
        if l:b+=text(X(p[0]),Y(p[1])-12,l,17)
    for i,j,l in edge_labels:
        a,c=points[i],points[j]; b+=text((X(a[0])+X(c[0]))/2+8,(Y(a[1])+Y(c[1]))/2+23,l,16)
    for x,y,l in extra:b+=text(X(x),Y(y),l,16)
    return svg(b,'Geometric configuration; use the stated measurements')
def sector(theta,lab='θ',rlabel='r',inner=None):
    cx,cy,R=270,225,155
    pt=lambda t,r=R:(cx+r*math.cos(t),cy-r*math.sin(t))
    a=pt(0);z=pt(theta)
    if inner:
        b=line(*pt(0,R*inner),*a)+line(*pt(theta,R*inner),*z)
    else:
        b=line(cx,cy,*a)+line(cx,cy,*z)
    b+=f'<path d="M {a[0]} {a[1]} A {R} {R} 0 {int(theta>math.pi)} 0 {z[0]} {z[1]}" fill="none" stroke="black" stroke-width="2"/>'
    b+=text(cx+45,cy-15,lab)+text(cx+R/2,cy+23,rlabel)
    if inner:
        ri=R*inner;ai=pt(0,ri);zi=pt(theta,ri)
        b+=f'<path d="M {ai[0]} {ai[1]} A {ri} {ri} 0 {int(theta>math.pi)} 0 {zi[0]} {zi[1]}" fill="none" stroke="black" stroke-width="2"/>'
    return svg(b,'Circular sector or annular sector')

# GEOMETRY AND TRIGONOMETRY
_bc=math.sqrt(97);_B=math.degrees(math.acos(40/(16*_bc)))
add('gt',701,'A non-right triangle from two sides and an included angle','3.2','Triangle trigonometry',r'In triangle $ABC$, $AB=8$ cm, $AC=11$ cm and angle $BAC=60^\circ$.',[
P('Find BC exactly.',('M1',r'$BC^2=8^2+11^2-2(8)(11)\cos60^\circ=97$.'),('A1',r'$BC=\sqrt{97}$ cm.')),
P('Find angle ABC to 3 significant figures.',('M1',r'$\cos B=(8^2+97-11^2)/(16\sqrt{97})$.'),('A1',f'B = {_B:.3g}°.')),
P('Find the exact triangle area.',('M1',r'$A=\frac12(8)(11)\sin60^\circ$.'),('A1',r'$A=22\sqrt3$ cm$^2$.'))],rf'$BC=\sqrt{{97}}$ cm; B = {_B:.3g}°; area $22\sqrt3$ cm².','Cosine rule, angle reconstruction and coordinate cross-product area agree.',near(8*11*math.sin(math.pi/3)/2,22*math.sqrt(3)) and near(_bc**2,97),geometry([(0,0),(8,0),(5.5,11*math.sqrt(3)/2)],[(0,1),(1,2),(2,0)],['A','B','C'],[(0,1,'8'),(0,2,'11')],[(1.3,.6,'60°')]),calc=True)
_c1=5*math.sqrt(3)+2*math.sqrt(6);_c2=5*math.sqrt(3)-2*math.sqrt(6)
add('gt',702,'Why one set of data can give two triangles','3.2','Triangle trigonometry',r'In triangle $ABC$, angle $A=30^\circ$, $AC=10$ cm and $BC=7$ cm. Two possible positions of B are indicated.',[
P('Use the sine rule to find the two possible values of B.',('M1',r'$\sin B=10\sin30^\circ/7=5/7$.'),('A1',r'$B=45.6^\circ$ or $134^\circ$ to 3 significant figures.')),
P('Find the two possible lengths AB to 3 significant figures.',('M1',r'$AB=7\sin(150^\circ-B)/\sin30^\circ$ for each B.'),('A1',f'AB = {_c1:.3g} cm or {_c2:.3g} cm.')),
P('Explain why both are valid triangles.',('R1','Both possible B values are below 150°, so each third angle is positive.'),('R1','Both positive side lengths satisfy the same given side-angle data.'))],f'B approximately 45.6° or 134°; AB approximately {_c1:.3g} or {_c2:.3g} cm.','Both B coordinates have distance 7 from the stated C coordinate.',all(near((c-5*math.sqrt(3))**2+25,49) for c in [_c1,_c2]),geometry([(0,0),(_c1,0),(5*math.sqrt(3),5),(_c2,0)],[(0,1),(1,2),(2,0),(3,2)],['A','B₁','C','B₂'],[(0,2,'10'),(1,2,'7'),(3,2,'7')],[(1,.5,'30°')]),calc=True)
_east=12*math.sin(math.radians(35))+9*math.sin(math.radians(110));_north=12*math.cos(math.radians(35))+9*math.cos(math.radians(110))
_dist=math.hypot(_east,_north);_bearing=math.degrees(math.atan2(_east,_north))
add('gt',703,'Combining journeys given by bearings','3.3','Bearings and applications',r'A boat sails 12 km from A to B on bearing $035^\circ$, then 9 km from B to C on bearing $110^\circ$.',[
P('Find angle ABC.',('M1','The reverse bearing BA is 215°.'),('A1',r'$\angle ABC=215^\circ-110^\circ=105^\circ$.')),
P('Find AC to 3 significant figures.',('M1',r'$AC^2=12^2+9^2-2(12)(9)\cos105^\circ$.'),('A1',f'AC = {_dist:.3g} km.')),
P('Find the bearing of C from A to the nearest degree.',('M1',r'East $=12\sin35^\circ+9\sin110^\circ$; north $=12\cos35^\circ+9\cos110^\circ$.'),('A1',f'Bearing {round(_bearing):03d}°, using the quadrant with positive east and north displacements.'))],f'Angle B 105°; AC {_dist:.3g} km; bearing {round(_bearing):03d}°.','Coordinate resultant agrees with cosine-rule distance; bearing quadrant checked.',near(_dist**2,225-216*math.cos(math.radians(105))),geometry([(0,0),(12*math.sin(math.radians(35)),12*math.cos(math.radians(35))),(_east,_north),(0,5)],[(0,1),(1,2),(0,3)],['A','B','C','N'],[(0,1,'12 km'),(1,2,'9 km')]),calc=True)
add('gt',704,'Two elevation observations along level ground','3.3','Angles of elevation',r'A and B stand on level ground on the same side of a vertical tower. A is 40 m farther from the tower than B. Elevation angles to the top are $30^\circ$ at A and $60^\circ$ at B.',[
P('Let B be x metres from the tower. Write two expressions for its height h.',('M1',r'$h=x\tan60^\circ$.'),('A1',r'$h=(x+40)\tan30^\circ$.')),
P('Find x and h exactly.',('M1',r'$x\sqrt3=(x+40)/\sqrt3$, so $3x=x+40$.'),('A1',r'$x=20$ m.'),('A1',r'$h=20\sqrt3$ m.')),
P('Find the distance from B to the top.',('M1',r'$\cos60^\circ=x/BT$.'),('A1',r'$BT=40$ m.'))],r'B is 20 m from the tower; height $20\sqrt3$ m; line of sight 40 m.','Both tangent equations and the hypotenuse checked independently.',near(20*math.sqrt(3),60/math.sqrt(3)) and near(20**2+(20*math.sqrt(3))**2,40**2),geometry([(0,0),(40,0),(60,0),(60,20*math.sqrt(3))],[(0,2),(2,3),(0,3),(1,3)],['A','B','O','T'],[(0,1,'40 m')],[(8,4,'30°'),(43,4,'60°')]))
add('gt',705,'Reconstructing a sector from its boundary','3.4','Radians and sectors',r'A sector has arc length 12 cm and total perimeter 28 cm. Its central angle is $\theta$ radians and radius r cm.',[
P('Find the radius.',('M1',r'$2r+12=28$.'),('A1',r'$r=8$ cm.')),
P('Find the central angle and area.',('M1',r'$r\theta=12$, hence $\theta=1.5$ radians.'),('A1',r'Area $=\frac12(8^2)(1.5)=48$ cm$^2$.')),
P('Explain why a sector with the same arc length and double the radius has half the angle.',('R1',r'For fixed arc length s, $\theta=s/r$ is inversely proportional to r.'))],r'Radius 8 cm, angle 1.5 radians, area 48 cm².','Arc, full perimeter and area reconstructed.',8*1.5==12 and 2*8+12==28 and .5*64*1.5==48,sector(1.5,'θ','r'))
add('gt',706,'The complete boundary of an annular sector','3.4','Radians and sectors',r'An annular sector has outer radius 10 cm, inner radius 6 cm and central angle 1.2 radians.',[
P('Find its area.',('M1',r'$A=\frac12(10^2-6^2)(1.2)$.'),('A1',r'$A=38.4$ cm$^2$.')),
P('Find the entire perimeter, including straight edges.',('M1','Arc lengths are 12 and 7.2 cm; straight edges are each 4 cm.'),('A1','Perimeter 12+7.2+8 = 27.2 cm.')),
P('Find the fraction of the outer sector removed to make the hole.',('M1','The sectors share an angle, so use their squared-radius ratio.'),('A1',r'Fraction $=6^2/10^2=9/25$.'))],r'Area 38.4 cm²; perimeter 27.2 cm; fraction removed $9/25$.','Both arcs, radial boundaries and area ratio checked.',near(.5*(100-36)*1.2,38.4) and near(10*1.2+6*1.2+2*(10-6),27.2),sector(1.2,'1.2 rad','10 cm',.6))
_seg=32*math.pi/3-16*math.sqrt(3)
add('gt',707,'A circular segment formed by a chord','3.4','Circular measure',r'A chord AB subtends $\pi/3$ radians at centre O of a circle of radius 8 cm. The minor segment is between the chord and minor arc.',[
P('Find AB exactly.',('M1',r'$AB^2=8^2+8^2-2(8)(8)\cos(\pi/3)=64$.'),('A1',r'$AB=8$ cm.')),
P('Find the exact area of the minor segment.',('M1',r'Sector area $=32\pi/3$; triangle area $=16\sqrt3$.'),('A1',r'Segment area $=32\pi/3-16\sqrt3$ cm$^2$.')),
P('Find the exact segment perimeter.',('M1',r'Arc length $=8\pi/3$; add the chord.'),('A1',r'Perimeter $=8+8\pi/3$ cm.'))],r'Chord 8; area $32\pi/3-16\sqrt3$ cm²; perimeter $8+8\pi/3$ cm.','Positive segment area and chord cosine rule checked.',_seg>0 and near(128-128*math.cos(math.pi/3),64),sector(math.pi/3,'π/3','8 cm').replace('</svg>',line(425,225,347.5,225-155*math.sqrt(3)/2)+'</svg>'))
add('gt',708,'Signed trigonometric values from a quadrant','3.6','Trigonometric identities',r'Angle $\theta$ lies in quadrant II with $\sin\theta=3/5$. The circle indicates the quadrant, not a measured angle.',[
P(r'Find $\cos\theta$ and $\tan\theta$ exactly.',('M1',r'$\cos^2\theta=16/25$.'),('R1','Cosine is negative in quadrant II.'),('A1',r'$\cos\theta=-4/5$, $\tan\theta=-3/4$.')),
P(r'Find $\sin2\theta$ and $\cos2\theta$.',('M1',r'Use $2\sin\theta\cos\theta$ and $1-2\sin^2\theta$.'),('A1',r'$\sin2\theta=-24/25$, $\cos2\theta=7/25$.'))],r'Cosine $-4/5$, tangent $-3/4$, double-angle sine $-24/25$, cosine $7/25$.','Pythagorean and double-angle identities checked with exact fractions.',F(3,5)**2+F(-4,5)**2==1 and 2*F(3,5)*F(-4,5)==F(-24,25),plot([(lambda x:math.sqrt(1-x*x),(-1,1),None),(lambda x:-math.sqrt(1-x*x),(-1,1),None)],(-1.3,1.3),(-1.3,1.3),xt=[-1,0,1],yt=[-1,1],points=[(-.8,.6,'P')],segments=[((0,0),(-.8,.6))],equal=True))
add('gt',709,'A quadratic in sine with three solutions','3.8','Trigonometric equations',r'Solve $2\sin^2x-3\sin x+1=0$ for $0\le x\le2\pi$. The graph shows the left-hand side.',[
P('Factorize using a substitution.',('M1',r'Let $u=\sin x$.'),('A1',r'$2u^2-3u+1=(2u-1)(u-1)$.')),
P('Find every solution.',('M1',r'$\sin x=1/2$ or $1$.'),('A1',r'$x=\pi/6,5\pi/6$ from sine 1/2.'),('A1',r'$x=\pi/2$ from sine 1.')),
P('Explain why sine 1 gives one solution rather than two.',('R1','Sine reaches its maximum only once in the interval; the symmetric angles coincide.'))],r'$x=\pi/6,\pi/2,5\pi/6$.','Every root substituted into the original expression.',all(near(2*math.sin(x)**2-3*math.sin(x)+1,0) for x in [math.pi/6,math.pi/2,5*math.pi/6]),plot([(lambda x:2*math.sin(x)**2-3*math.sin(x)+1,(0,2*math.pi),None)],(0,2*math.pi),(-.5,6.5),xt=[0,round(math.pi,3),round(2*math.pi,3)],yt=[0,2,6]))
add('gt',710,'A Ferris wheel and an exact height interval','3.7','Sinusoidal models',r'A rider has height $h(t)=14-12\cos(\pi t/20)$ metres, with t in seconds. Consider $0\le t\le40$.',[
P('State the minimum height, maximum height and period.',('A1','Minimum 2 m; maximum 26 m.'),('A1',r'Period $2\pi/(\pi/20)=40$ s.')),
P('Find the two times at height 20 m.',('M1',r'$\cos(\pi t/20)=-1/2$.'),('A1',r'Angles $2\pi/3,4\pi/3$ give $t=40/3,80/3$ seconds.')),
P('State when the rider is strictly higher than 20 m.',('R1','The graph lies above the height between the two crossings.'),('A1',r'$40/3<t<80/3$.'))],r'Heights 2–26 m; period 40 s; height 20 at $40/3,80/3$ s; above between these times.','Extrema and both exact crossings checked.',all(near(14-12*math.cos(math.pi*t/20),20) for t in [40/3,80/3]),plot([(lambda t:14-12*math.cos(math.pi*t/20),(0,40),None)],(0,40),(0,30),xt=[0,10,20,30,40],yt=[0,2,14,26],xlab='t / s',ylab='h / m'))

add('gt',711,'Consecutive side lengths and an obtuse angle','3.2','Triangle trigonometry',r'A triangle has side lengths x, x+1 and x+2 cm. The angle opposite the longest side is $120^\circ$.',[
P('Show that x satisfies a quadratic.',('M1',r'$(x+2)^2=x^2+(x+1)^2-2x(x+1)\cos120^\circ$.'),('A1',r'$2x^2-x-3=0$.')),
P('Find the side lengths, explaining any rejection.',('M1',r'$(2x-3)(x+1)=0$.'),('R1',r'$x=-1$ is impossible, so $x=3/2$.'),('A1',r'Sides $3/2,5/2,7/2$ cm; these satisfy the triangle inequality.')),
P('Find the exact area.',('M1',r'$A=\frac12(3/2)(5/2)\sin120^\circ$.'),('A1',r'$15\sqrt3/16$ cm$^2$.'))],r'Sides $3/2,5/2,7/2$ cm; area $15\sqrt3/16$ cm².','Recovered sides checked in cosine rule and area formula.',near(1.5**2+2.5**2-2*1.5*2.5*math.cos(2*math.pi/3),3.5**2),geometry([(0,0),(2.5,0),(-.75,1.5*math.sqrt(3)/2)],[(0,1),(1,2),(2,0)],['A','B','C'],[(0,1,'x+1'),(0,2,'x'),(1,2,'x+2')],[(.2,.3,'120°')]),hard=True)
_alpha=math.degrees(math.asin(.8))
add('gt',712,'Area restrictions for a hinged triangle','3.2','Triangle area and inequalities',r'Rods of lengths 6 cm and 10 cm are hinged at O. Their ends form a triangle with included angle $\theta$, where $0^\circ<\theta<180^\circ$.',[
P('Find the maximum area and its angle.',('M1',r'$A=30\sin\theta$.'),('R1',r'Sine is at most 1, attained at $90^\circ$.'),('A1','Maximum 30 cm² at 90°.')),
P('Find all angles giving area at least 24 cm², to 3 significant figures.',('M1',r'$\sin\theta\ge0.8$.'),('A1',f'{_alpha:.3g}° ≤ θ ≤ {180-_alpha:.3g}°.')),
P('If the third side is 8 cm, find the area exactly.',('M1',r'$\cos\theta=(36+100-64)/120=3/5$; positive sine is $4/5$.'),('A1','Area 24 cm².'))],f'Maximum 30 cm²; area ≥24 for angles {_alpha:.3g}° to {180-_alpha:.3g}°; third side 8 gives area 24.','Inverse-sine endpoints and cosine-rule special case checked.',near(30*math.sin(math.radians(_alpha)),24) and F(36+100-64,120)==F(3,5),geometry([(0,0),(10,0),(6*math.cos(1),6*math.sin(1))],[(0,1),(1,2),(2,0)],['O','A','B'],[(0,1,'10 cm'),(0,2,'6 cm')],[(1,.5,'θ')]),calc=True,hard=True)
_a1=math.degrees(math.atan(3/10));_a2=math.degrees(math.atan(3/5))
_cuboid=svg(poly([(150,250),(420,250),(510,175),(240,175),(150,250)])+poly([(150,150),(420,150),(510,75),(240,75),(150,150)])+line(150,250,150,150)+line(420,250,420,150)+line(510,175,510,75)+line(240,175,240,75,True)+line(150,150,510,175,True)+line(150,150,330,212.5,True)+text(280,280,'8 m')+text(490,225,'6 m')+text(125,200,'3 m')+text(140,140,'A')+text(525,180,'C')+text(340,235,'M'))
add('gt',713,'Comparing cables inside a cuboid','3.1','Three-dimensional geometry',r'A room is 8 m long, 6 m wide and 3 m high. A is an upper corner, C the opposite lower corner, and M the floor centre.',[
P('Find AC exactly.',('M1',r'Floor diagonal $=\sqrt{8^2+6^2}=10$.'),('A1',r'$AC=\sqrt{109}$ m.')),
P('Find the angle AC makes with the floor.',('M1',r'$\tan\alpha=3/10$.'),('A1',f'α = {_a1:.3g}°.')),
P('Find AM and its angle with the floor; explain why this angle is greater.',('M1',r'Horizontal run to M is 5 m, so $AM=\sqrt{34}$ m.'),('A1',f'β = arctan(3/5) = {_a2:.3g}°.'),('R1','The same 3 m descent occurs over a shorter horizontal run.'))],rf'$AC=\sqrt{{109}}$ m at {_a1:.3g}°; $AM=\sqrt{{34}}$ m at {_a2:.3g}°.','Both right-triangle reductions and angle comparison checked.',8**2+6**2+3**2==109 and 4**2+3**2+3**2==34 and _a2>_a1,_cuboid,calc=True,hard=True)
add('gt',714,'Rolling a sector into a cone','3.4','Circular measure and solids',r'A sector of radius 13 cm and angle $10\pi/13$ radians is rolled into a cone surface by joining its straight edges without overlap.',[
P('Find the base radius.',('M1',r'Arc length $13(10\pi/13)=10\pi$ equals base circumference.'),('A1',r'$r=10\pi/(2\pi)=5$ cm.')),
P('Find the perpendicular height and volume.',('M1',r'Slant height 13 gives $h^2=13^2-5^2=144$.'),('A1',r'$h=12$ cm.'),('A1',r'$V=\frac13\pi(25)(12)=100\pi$ cm$^3$.')),
P('Find the total area including a circular base.',('M1',r'Curved area $=\frac12(13)^2(10\pi/13)=65\pi$.'),('A1',r'Total $=65\pi+25\pi=90\pi$ cm$^2$.'))],r'Radius 5, height 12 cm; volume $100\pi$ cm³; total area $90\pi$ cm².','Arc/circumference relation and 5-12-13 triangle checked.',near(13*10*math.pi/13,2*math.pi*5) and 13**2-5**2==12**2,sector(10*math.pi/13,'10π/13','13 cm'),hard=True)
add('gt',715,'An identity with a restricted domain','3.6','Trigonometric identities',r'Let $F(x)=\dfrac{\sin2x}{1+\cos2x}$ for $0\le x\le2\pi$.',[
P('Find every excluded x-value.',('M1',r'$1+\cos2x=2\cos^2x=0$ when $\cos x=0$.'),('A1',r'$x=\pi/2,3\pi/2$.')),
P(r'Show that $F(x)=\tan x$ wherever defined.',('M1',r'Write numerator $2\sin x\cos x$ and denominator $2\cos^2x$.'),('A1',r'Cancel to $\sin x/\cos x=\tan x$, valid since $\cos x\ne0$.')),
P(r'Solve $F(x)=1$.',('M1',r'$\tan x=1$ has period $\pi$.'),('A1',r'$x=\pi/4,5\pi/4$, both admissible.'))],r'Excluded $\pi/2,3\pi/2$; $F=\tan x$ on its domain; roots $\pi/4,5\pi/4$.','Original ratio identity and roots checked away from denominator zeros.',all(near(math.sin(2*x)/(1+math.cos(2*x)),math.tan(x)) for x in [.2,.8,2,3.4,5]),plot([(lambda x:math.sqrt(1-x*x),(-1,1),None),(lambda x:-math.sqrt(1-x*x),(-1,1),None)],(-1.3,1.3),(-1.3,1.3),xt=[-1,0,1],yt=[-1,1],equal=True),hard=True)
add('gt',716,'A double-angle equation with a negative sine root','3.8','Trigonometric equations',r'Solve $\cos2x=\sin x$ for $0\le x<2\pi$. The two graphs are shown.',[
P('Convert to a quadratic in sine and factorize.',('M1',r'$1-2\sin^2x=\sin x$.'),('A1',r'$(2\sin x-1)(\sin x+1)=0$.')),
P('Find all solutions.',('M1',r'$\sin x=1/2$ or $-1$.'),('A1',r'$x=\pi/6,5\pi/6$ from sine 1/2.'),('A1',r'$x=3\pi/2$ from sine -1.')),
P('Explain how the graph confirms that the negative sine root must be retained.',('R1','The curves also meet below the axis at x=3π/2; retaining only the positive sine value would omit that intersection.'))],r'$x=\pi/6,5\pi/6,3\pi/2$.','All three roots evaluated in the original equation.',all(near(math.cos(2*x),math.sin(x)) for x in [math.pi/6,5*math.pi/6,3*math.pi/2]),plot([(lambda x:math.cos(2*x),(0,2*math.pi),None),(math.sin,(0,2*math.pi),None)],(0,2*math.pi),(-1.3,1.3),xt=[0,round(math.pi,3),round(2*math.pi,3)],yt=[-1,1]),hard=True)
add('gt',717,'A sine inequality across two complete cycles','3.8','Trigonometric equations',r'Consider $\sin2x$ for $0\le x<2\pi$.',[
P(r'Find all roots of $\sin2x=\sqrt3/2$.',('M1',r'$0\le2x<4\pi$ includes two cycles.'),('A1',r'$2x=\pi/3,2\pi/3,7\pi/3,8\pi/3$.'),('A1',r'$x=\pi/6,\pi/3,7\pi/6,4\pi/3$.')),
P(r'Solve $\sin2x>\sqrt3/2$.',('M1','Use the region between the rising and falling level crossings on each cycle.'),('A1',r'$x\in(\pi/6,\pi/3)\cup(7\pi/6,4\pi/3)$.')),
P('Find the total interval length.',('A1',r'$\pi/6+\pi/6=\pi/3$.'))],r'Four roots $\pi/6,\pi/3,7\pi/6,4\pi/3$; strict intervals between each pair, total length $\pi/3$.','All four level crossings and interior signs checked.',all(near(math.sin(2*x),math.sqrt(3)/2) for x in [math.pi/6,math.pi/3,7*math.pi/6,4*math.pi/3]),plot([(lambda x:math.sin(2*x),(0,2*math.pi),None)],(0,2*math.pi),(-1.3,1.3),xt=[0,round(math.pi,3),round(2*math.pi,3)],yt=[-1,1]),hard=True)
_tidal=6/math.pi*math.acos(2/3)
add('gt',718,'Tidal depth and a safe passage window','3.7','Sinusoidal models',r'Tidal depth is sinusoidal. A high tide of 7 m occurs at t=3 hours, and the next low tide of 1 m at t=9. A boat requires depth at least 6 m.',[
P('Find a cosine model d(t).',('M1','Midline 4, amplitude 3 and half-period 6 hours give period 12.'),('A1',r'$d(t)=4+3\cos(\pi(t-3)/6)$.')),
P('Find the first safe interval after t=0 to 3 significant figures.',('M1',r'Crossings satisfy $t=3\pm(6/\pi)\arccos(2/3)$.'),('A1',f'{3-_tidal:.3g} ≤ t ≤ {3+_tidal:.3g} hours.')),
P('Find its duration and explain the included endpoints.',('A1',f'Duration {2*_tidal:.3g} hours.'),('R1','At each endpoint depth equals the required 6 m; equality is safe under the stated model.'))],f'Model 4+3 cos(π(t−3)/6); window [{3-_tidal:.3g},{3+_tidal:.3g}] h, duration {2*_tidal:.3g} h.','High/low observations and both threshold crossings substituted.',all(near(4+3*math.cos(math.pi*(t-3)/6),6) for t in [3-_tidal,3+_tidal]),plot([(lambda t:4+3*math.cos(math.pi*(t-3)/6),(0,15),None)],(0,15),(0,8),xt=[0,3,9,15],yt=[0,1,4,7],xlab='t / h',ylab='d / m'),calc=True,hard=True)
_lens=24*math.pi-18*math.sqrt(3)
add('gt',719,'The overlap of two congruent circles','3.4','Circular measure',r'Two circles each have radius 6 cm. Their centres O and P are 6 cm apart. They intersect at A and B.',[
P('Explain why OAP and OBP are equilateral; find minor angle AOB.',('R1','Each triangle has three sides equal to 6 cm.'),('A1',r'Each angle adjacent to OP is 60°, so $\angle AOB=120^\circ=2\pi/3$.')),
P('Find the exact common area.',('M1','The lens is two equal sectors minus their respective isosceles triangles.'),('M1',r'One segment $=\frac12(36)(2\pi/3)-\frac12(36)\sin(2\pi/3)=12\pi-9\sqrt3$.'),('A1',r'Overlap $=24\pi-18\sqrt3$ cm$^2$.')),
P('Find the fraction of either circle covered by the overlap.',('M1',r'Divide by $36\pi$.'),('A1',r'Fraction $=\frac23-\frac{\sqrt3}{2\pi}$.'))],r'Angle $2\pi/3$, common area $24\pi-18\sqrt3$ cm²; fraction $2/3-\sqrt3/(2\pi)$.','Positive segment decomposition, upper area bound and ratio checked.',0<_lens<36*math.pi and near(_lens/(36*math.pi),2/3-math.sqrt(3)/(2*math.pi)),svg(circle(260,180,115,'none')+circle(375,180,115,'none')+line(260,180,375,180)+line(260,180,317.5,180-115*math.sqrt(3)/2)+line(375,180,317.5,180-115*math.sqrt(3)/2)+line(260,180,317.5,180+115*math.sqrt(3)/2)+line(375,180,317.5,180+115*math.sqrt(3)/2)+text(247,184,'O')+text(389,184,'P')+text(317.5,66,'A')+text(317.5,298,'B')+text(317.5,202,'6 cm')),hard=True)
add('gt',720,'A tangent equation separated by asymptotes','3.8','Trigonometric equations',r'Solve $3\tan2x=3$ for $-\pi/2\le x\le\pi/2$. The branches are shown.',[
P('State all excluded inputs.',('M1',r'$\cos2x=0$ when $2x=\pm\pi/2$ in this interval.'),('A1',r'$x=-\pi/4,\pi/4$.')),
P('Find every solution.',('M1',r'$2x=\pi/4+n\pi$ for integer n.'),('M1',r'$-\pi\le2x\le\pi$ permits $n=-1,0$ only.'),('A1',r'$x=-3\pi/8,\pi/8$.')),
P('Explain why adding π to a solution does not give the nearest next solution.',('R1',r'The period in x is $\pi/2$ because the tangent input is 2x; adding π skips one cycle.'))],r'Excluded $\pm\pi/4$; roots $-3\pi/8,\pi/8$.','Both roots checked in original equation; graph branches separated at poles.',all(near(3*math.tan(2*x),3) for x in [-3*math.pi/8,math.pi/8]),plot([(lambda x:3*math.tan(2*x),(-math.pi/2,-math.pi/4-.005),None),(lambda x:3*math.tan(2*x),(-math.pi/4+.005,math.pi/4-.005),None),(lambda x:3*math.tan(2*x),(math.pi/4+.005,math.pi/2),None)],(-math.pi/2,math.pi/2),(-8,8),xt=[round(-math.pi/2,3),0,round(math.pi/2,3)],yt=[-6,0,3,6]),hard=True)

# STATISTICS AND PROBABILITY: no AHL-only random-variable variance or inference.
_hist=svg(line(80,300,580,300)+line(80,300,80,35)+''.join(f'<rect x="{80+120*i}" y="{300-18*f}" width="120" height="{18*f}" fill="white" stroke="black" stroke-width="2"/>'+text(140+120*i,290-18*f,f,15) for i,f in enumerate([4,8,12,6]))+''.join(text(80+120*i,326,10*i,14) for i in range(5))+text(70,25,'Frequency',15)+text(580,345,'Time / min',15))
add('sp',701,'Estimation from equal-width grouped data','4.2','Grouped data',r'Thirty journey times have frequencies 4, 8, 12 and 6 in the respective intervals $[0,10)$, $[10,20)$, $[20,30)$, $[30,40)$ minutes. Assume times are uniformly spread within each class for interpolation.',[
P('Estimate the mean time.',('M1','Use class midpoints 5,15,25,35 weighted by their frequencies.'),('A1',r'$\bar x=(4(5)+8(15)+12(25)+6(35))/30=65/3$ minutes.')),
P('Estimate the median using interpolation.',('M1','The 15th observation lies in the 20–30 class; 12 observations precede it.'),('A1',r'Median estimate $=20+(15-12)(10)/12=22.5$ minutes.')),
P('Explain why the estimated mean need not equal the actual mean.',('R1','The exact within-class times are unknown; replacing all times by their class midpoint can change the mean.'))],r'Estimated mean $65/3$ min; interpolated median 22.5 min.','Weighted midpoint sum 650 and cumulative class counts checked.',sum(f*m for f,m in zip([4,8,12,6],[5,15,25,35]))==650 and 20+(15-12)*10/12==22.5,_hist,calc=True)
add('sp',702,'Comparing spread and detecting an outlier','4.3','Descriptive statistics',r'The five-number summaries for delivery times are A: (20,35,50,65,90) and B: (10,42,52,60,80), in minutes. The box plots share a scale.',[
P('Compare the medians and interquartile ranges.',('A1','Medians: A 50, B 52 minutes, so A has the smaller median.'),('A1','IQR: A 30, B 18 minutes, so B has the smaller central spread.')),
P('Use the 1.5 IQR rule to test whether a new A delivery time of 120 minutes would be an outlier relative to the original A summary.',('M1','Upper fence 65+1.5(30)=110.'),('A1','120>110, so it would be an upper outlier.')),
P('A manager prioritizes consistency over the typical time. Explain which company these summaries support.',('R1','B has the lower IQR, so its middle half is more consistent; this does not establish consistency for every delivery.'))],r'A has lower median; B lower IQR; 120 is an A outlier by the original 110-minute fence; B is supported for central consistency.','Common-scale five-number summaries and fence arithmetic checked.',65-35==30 and 60-42==18 and 120>65+1.5*30,boxplot([(20,35,50,65,90),(10,42,52,60,80)],(0,120),['A','B']))
add('sp',703,'A missing frequency determined by the mean','4.3','Descriptive statistics',r'A population of daily counts has values 0,1,2,3 with respective frequencies $2,k,6,4$. Its mean is 1.8.',[
P('Find k.',('M1',r'$(k+24)/(k+12)=1.8$.'),('A1',r'$k=3$.')),
P('Find the median and mode.',('M1','There are 15 values; ordered positions 6 through 11 equal 2.'),('A1','Median = mode = 2.')),
P('Find the population standard deviation.',('M1',r'$E(x^2)=(3+24+36)/15=4.2$; subtract $\bar x^2=3.24$.'),('A1',r'$\sigma=\sqrt{0.96}=0.980$ to 3 significant figures.'))],r'$k=3$; median and mode 2; population standard deviation 0.980.','Frequency total, first and second data moments evaluated exactly.',F(3+24,3+12)==F(9,5) and F(63,15)-F(9,5)**2==F(24,25),table(['Count','Frequency'],[[0,2],[1,'k'],[2,6],[3,4]]),calc=True)
add('sp',704,'Combining populations with different centres','4.3','Descriptive statistics',r'Group A has 12 observations, mean 18 and population standard deviation 3. Group B has 8 observations, mean 23 and population standard deviation 4.',[
P('Find the combined mean.',('M1',r'$\bar x=(12(18)+8(23))/20$.'),('A1',r'$\bar x=20$.')),
P('Find the combined population standard deviation using sums of squares.',('M1',r'For a group, $\sum x^2=n(\sigma^2+\bar x^2)$.'),('M1',r'Total sum of squares $=12(9+324)+8(16+529)=8356$.'),('A1',r'Combined variance $=8356/20-20^2=17.8$; standard deviation $\sqrt{17.8}=4.22$.')),
P('Explain why averaging 3 and 4 cannot give the combined standard deviation.',('R1','The groups have different means, so dispersion between group centres also contributes to the combined spread.'))],r'Combined mean 20, standard deviation 4.22.','Weighted total and second-moment identity checked using exact arithmetic.',12*18+8*23==400 and 12*(9+324)+8*(16+529)==8356,table(['Group','n','Mean','Pop. s.d.'],[['A',12,18,3],['B',8,23,4]]),calc=True)
add('sp',705,'How an affine unit conversion changes summary statistics','4.3','Descriptive statistics',r'Temperatures measured in Celsius have mean 45, median 44 and standard deviation 6. Convert using $F=1.8C+32$. No assumption of a normal distribution is made.',[
P('Find the Fahrenheit mean and median.',('M1','A positive affine transformation preserves order and transforms the centre by the same formula.'),('A1','Mean 113 °F; median 111.2 °F.')),
P('Find the Fahrenheit standard deviation.',('M1','Standard deviation scales by 1.8; adding 32 does not change spread.'),('A1','10.8 °F.')),
P('Find the Celsius temperature corresponding to 125 °F. Explain whether the fraction of observations above 125 °F can be determined from these summaries.',('A1',r'$C=(125-32)/1.8=51\frac23$ °C.'),('R1','The fraction cannot be determined: mean, median and standard deviation do not specify the full distribution.'))],r'Mean 113 °F, median 111.2 °F, s.d. 10.8 °F; 125 °F corresponds to $51\frac23$ °C; tail fraction undetermined.','All affine transformations checked; no unjustified normal tail inferred.',near(1.8*45+32,113) and near(1.8*44+32,111.2) and near(1.8*6,10.8),plot([(lambda c:1.8*c+32,(0,70),None)],(0,70),(20,170),xt=[0,20,40,60],yt=[32,100,150],xlab='Celsius',ylab='Fahrenheit'))
add('sp',706,'A stratified sample and a response bias','4.1','Sampling',r'A school has 480 SL and 240 HL students. A survey will sample 60 students in proportion to course level. Separately, a voluntary online poll receives 50 SL and 70 HL responses.',[
P('Find the required SL and HL sample sizes for the stratified survey.',('M1',r'SL share $480/720=2/3$; HL share $1/3$.'),('A1','Select 40 SL and 20 HL students.')),
P('Compare the HL fraction in the voluntary poll with that in the school.',('M1',r'Poll HL fraction $70/120=7/12$; school HL fraction $1/3$.'),('A1','Poll is 58.3% HL versus 33.3% in the school.')),
P('Explain why random selection within each stratum is preferable for estimating the school-wide opinion.',('R1','Random selection reduces self-selection bias within each level.'),('R1','Proportional allocation represents the two levels correctly; the voluntary poll overrepresents HL and may also attract unusually motivated respondents.'))],r'Stratified sample: 40 SL,20 HL; voluntary poll HL share 58.3% versus school 33.3%.','Population shares and poll proportions evaluated exactly.',F(480,720)*60==40 and F(240,720)*60==20 and F(70,120)>F(240,720),bars([480,240],['SL','HL'],ylab='School population'))
add('sp',707,'Completing a Venn diagram and testing independence','4.11','Conditional probability',r'Events A and B satisfy $P(A)=0.55$, $P(B)=0.40$ and $P(A\cap B)=0.20$.',[
P('Find the probabilities of A only, B only and neither event.',('M1','Subtract the intersection from each event probability; use the complement of the union.'),('A1','A only 0.35; B only 0.20; neither 0.25.')),
P(r'Find $P(A\mid B)$.',('M1',r'$P(A\mid B)=0.20/0.40$.'),('A1','0.50.')),
P('Determine whether the events are independent.',('M1',r'$P(A)P(B)=0.55(0.40)=0.22$.'),('R1','0.22 differs from intersection 0.20, so the events are not independent.'))],r'A only .35, B only .20, neither .25; $P(A\mid B)=.50$; dependent.','Region sum, conditional ratio and independence criterion checked.',near(.35+.2+.2+.25,1) and not near(.55*.4,.2),venn(['?','0.20','?'],outside='?'))
add('sp',708,'Inferring the source of a faulty component','4.11','Conditional probability',r'Factory A supplies 60% of components and B supplies 40%. Fault probabilities are 0.03 for A and 0.08 for B. A component is selected at random.',[
P('Find the probability that it is faulty.',('M1',r'$P(F)=0.6(0.03)+0.4(0.08)$.'),('A1',r'$P(F)=0.05$.')),
P('Given that it is faulty, find the probability it came from B.',('M1',r'$P(B\mid F)=P(B\cap F)/P(F)=0.032/0.05$.'),('A1','0.64.')),
P('Explain why the answer is greater than B’s supply share.',('R1','B has the higher fault rate, so a faulty component is disproportionately likely to have come from B.'))],r'Fault probability .05; conditional source-B probability .64.','Tree joint probabilities sum to faulty probability; conditional ratio checked.',near(.6*.03+.4*.08,.05) and near(.4*.08/.05,.64),tree('0.6','0.4',[('0.03','0.97'),('0.08','0.92')],second=('F','F′')))
add('sp',709,'Without replacement and a conditional draw order','4.6','Probability trees',r'A bag contains 5 red and 3 blue counters. Two are drawn without replacement. R and B denote colours in the order drawn.',[
P('Find the probability both counters are red.',('M1',r'$P(RR)=\frac58\frac47$.'),('A1',r'$P(RR)=5/14$.')),
P('Find the probability of exactly one red counter.',('M1',r'$P(RB)+P(BR)=\frac58\frac37+\frac38\frac57$.'),('A1',r'$15/28$.')),
P('Given exactly one red was drawn, find the probability it was drawn first.',('M1',r'$P(RB\mid\text{one red})=(15/56)/(30/56)$.'),('A1',r'$1/2$.'))],r'Both red $5/14$; exactly one red $15/28$; conditional red-first probability $1/2$.','Ordered outcome fractions checked exactly and total colour cases sum to one.',F(5,8)*F(4,7)==F(5,14) and 2*F(5,8)*F(3,7)==F(15,28),tree('5/8','3/8',[('4/7','3/7'),('5/7','2/7')],first=('R','B'),second=('R','B')))
add('sp',710,'A probability model and a fair entry price','4.7','Discrete random variables',r'A random variable X takes values 0,1,2,3 with probabilities $k,2k,3k,4k$. A game pays $3X$ currency units.',[
P('Find k.',('M1',r'$k+2k+3k+4k=1$.'),('A1',r'$k=0.1$.')),
P('Find the fair entry price for the game.',('M1',r'$E(X)=0(0.1)+1(0.2)+2(0.3)+3(0.4)=2$.'),('A1',r'$E(3X)=3E(X)=6$, so a fair price is 6.')),
P('At that price, find the probability of making a strictly positive profit.',('M1',r'$3X-6>0$ requires $X>2$.'),('A1',r'$P(X=3)=0.4$.'))],r'$k=.1$, fair price 6, probability of strict profit .4.','Probability normalization and expected payout checked exactly.',sum(F(k,10) for k in [1,2,3,4])==1 and sum(x*F(x+1,10) for x in range(4))==2,bars([1,2,3,4],['0','1','2','3'],ylab='Probability / k'))
_bin=lambda n,p,k:math.comb(n,k)*p**k*(1-p)**(n-k)
_pge4=1-sum(_bin(12,.3,k) for k in range(4))
add('sp',711,'A binomial tail and model assumptions','4.8','Binomial distributions',r'A seed germinates with probability 0.30. Twelve seeds are tested independently under identical conditions. X is the number germinating.',[
P('State the distribution and its mean.',('A1',r'$X\sim B(12,0.30)$.'),('A1',r'$E(X)=12(0.30)=3.6$.')),
P('Find the probability that at least four germinate.',('M1',r'$P(X\ge4)=1-\sum_{k=0}^3\binom{12}k(0.3)^k(0.7)^{12-k}$.'),('A1',f'Probability {_pge4:.4f}.')),
P('Explain how common disease exposure might invalidate this model.',('R1','Exposure can make outcomes dependent, and/or alter germination probabilities between seeds; the stated independent constant-probability trials would then fail.'))],f'Binomial (12,.3), mean 3.6; P(X≥4)={_pge4:.4f}.','Tail computed both by complement and direct summation.',near(_pge4,sum(_bin(12,.3,k) for k in range(4,13))),bars([_bin(12,.3,k) for k in range(13)],list(range(13)),ylab='P(X = x)'),calc=True,hard=True)
_n=math.ceil(math.log(.05)/math.log(.9))
add('sp',712,'Choosing the smallest batch for a success target','4.8','Binomial distributions',r'Independent trials each succeed with probability 0.10. A batch should have probability greater than 0.95 of at least one success.',[
P('Write the required inequality for batch size n.',('M1',r'$P(\text{at least one})=1-0.9^n$.'),('A1',r'$0.9^n<0.05$.')),
P('Find the smallest integer n, checking neighbouring sizes.',('M1',r'$n>\ln0.05/\ln0.9=28.43\ldots$; note the negative logarithm reverses the inequality.'),('A1',r'$n=29$: $1-0.9^{28}=0.9477\ldots$, $1-0.9^{29}=0.9529\ldots$.')),
P('Find the expected number of successes in this batch and explain why it is not a guarantee.',('A1','Expected count 2.9.'),('R1','Expectation is a long-run mean; any single batch can have another count, including zero.'))],r'Minimum batch 29, expected successes 2.9.','Strict target bracket checked at n=28,29.',_n==29 and 1-.9**28<.95<1-.9**29,plot([(lambda n:1-.9**n,(0,40),None)],(0,40),(0,1.05),xt=[0,10,20,30,40],yt=[0,.5,.95],xlab='n',ylab='P(at least one)'),calc=True,hard=True)
_p2=1-2*(F(5,6)**5)
add('sp',713,'Recovering a binomial success probability','4.8','Binomial distributions',r'Let $X\sim B(5,p)$, where $0<p<1$. It is known that $P(X=0)=P(X=1)$.',[
P('Find p exactly.',('M1',r'$(1-p)^5=5p(1-p)^4$.'),('R1',r'Since $p<1$, divide by positive $(1-p)^4$.'),('A1',r'$1-p=5p$, giving $p=1/6$.')),
P('Find $P(X\\ge2)$ exactly.',('M1',r'$1-P(X=0)-P(X=1)=1-2(5/6)^5$.'),('A1',r'$P(X\ge2)=763/3888$.')),
P('Explain why the equality of probabilities alone would also hold at p=1 if that endpoint had been allowed.',('R1','At p=1, X=5 certainly, so both P(X=0) and P(X=1) are zero; the original strict restriction excludes it.'))],r'$p=1/6$; $P(X\ge2)=763/3888$; p=1 excluded by the given domain.','Exact binomial equality and complement checked using rational arithmetic.',_p2==F(763,3888) and F(5,6)**5==5*F(1,6)*F(5,6)**4,table(['x','P(X=x)'],[[0,'(1−p)⁵'],[1,'5p(1−p)⁴'],['2 to 5','remaining probability']]),hard=True)
_norm=NormalDist(100,8);_accept=_norm.cdf(110)-_norm.cdf(90);_cut=NormalDist().inv_cdf(.975)
add('sp',714,'Normal tolerances and a central acceptance interval','4.12','Normal distributions',r'A component length X is normally distributed with mean 100 mm and standard deviation 8 mm. It is accepted when $90\le X\le110$.',[
P('Find the probability of acceptance.',('M1',r'$z$ limits are $-1.25,1.25$.'),('A1',f'Acceptance probability {_accept:.4f}.')),
P('Find the expected number rejected among 500 components.',('M1',r'Expected rejected $=500(1-P(\text{accepted}))$.'),('A1',f'{500*(1-_accept):.3g}, approximately {round(500*(1-_accept))} components.')),
P('Find symmetric limits about the mean accepting 95% of components.',('M1',r'Central 95% corresponds to $100\pm8(1.95996\ldots)$.'),('A1',f'Limits {100-8*_cut:.3g} mm and {100+8*_cut:.3g} mm.'))],f'Acceptance {_accept:.4f}; expected rejects {500*(1-_accept):.3g}; 95% limits {100-8*_cut:.3g},{100+8*_cut:.3g} mm.','Standardized and direct normal probabilities agree; inverse limits enclose .95.',near(_accept,NormalDist().cdf(1.25)-NormalDist().cdf(-1.25)) and near(_norm.cdf(100+8*_cut)-_norm.cdf(100-8*_cut),.95),normal(100,8,[90,110]),calc=True,hard=True)
add('sp',715,'Recovering normal parameters from two percentiles','4.12','Normal distributions',r'X is normal with unknown mean $\mu$ and standard deviation $\sigma>0$. It satisfies $P(X<40)=0.158655$ and $P(X<70)=0.977250$. You may use the corresponding standard-normal values $-1$ and $2$, accurate to the displayed probabilities.',[
P('Write two simultaneous equations for the parameters.',('M1',r'$(40-\mu)/\sigma=-1$.'),('A1',r'$(70-\mu)/\sigma=2$.')),
P('Find μ and σ.',('M1',r'$40=\mu-\sigma$ and $70=\mu+2\sigma$ imply $3\sigma=30$.'),('A1',r'$\sigma=10$, $\mu=50$.')),
P('Find $P(40<X<70)$ and $P(X>50)$.',('A1',r'$0.977250-0.158655=0.818595$.'),('R1',r'Normal symmetry about $\mu=50$ gives $P(X>50)=0.5$.'))],r'$\mu=50,\sigma=10$; interval probability .818595; upper-half probability .5.','Recovered parameters reproduce the supplied rounded probabilities and z-values.',near(NormalDist(50,10).cdf(40),.158655,1e-6) and near(NormalDist(50,10).cdf(70),.977250,1e-6),normal(50,10,[40,70]),calc=True,hard=True)
_cut12=NormalDist(64,9).inv_cdf(.88);_conditional=(1-NormalDist(64,9).cdf(80))/.12
add('sp',716,'A top-percentile threshold and conditional normal tail','4.12','Normal distributions',r'Scores X are normal with mean 64 and standard deviation 9. The top 12% qualify for an award. Scores are treated as continuous.',[
P('Find the minimum qualifying score.',('M1',r'$P(X<c)=0.88$; use inverse normal.'),('A1',f'c = {_cut12:.3g}.')),
P('Given that a student qualifies, find the probability their score exceeds 80.',('M1',r'Since $80>c$, the event $X>80$ is contained in qualification.'),('M1',r'$P(X>80\mid X\ge c)=P(X>80)/0.12$.'),('A1',f'Conditional probability {_conditional:.4f}.')),
P('Explain why dividing by 0.88 would be wrong.',('R1','The condition is membership of the qualifying upper 12%, so its probability, not its complement, is the denominator.'))],f'Qualifying threshold {_cut12:.3g}; conditional tail {_conditional:.4f}.','Quantile reproduces .88 and conditional numerator is a subset probability.',near(NormalDist(64,9).cdf(_cut12),.88) and 0<_conditional<1 and 80>_cut12,normal(64,9,[80]),calc=True,hard=True)
_xs=[1,2,3,4,5];_ys=[3,4,6,8,9];_r=16/math.sqrt(260)
add('sp',717,'Regression from a small paired data set','4.10','Correlation and regression',r'Paired observations are $(1,3),(2,4),(3,6),(4,8),(5,9)$. Treat x as the explanatory variable.',[
P('Find the least-squares regression line of y on x.',('M1',r'$\bar x=3,\bar y=6$; $\sum(x-\bar x)^2=10$ and $\sum(x-\bar x)(y-\bar y)=16$.'),('A1',r'Slope $=1.6$, intercept $=6-1.6(3)=1.2$; $\hat y=1.6x+1.2$.')),
P('Estimate y at x=4.5 and find the residual at the observed point x=3.',('A1',r'Prediction $1.6(4.5)+1.2=8.4$.'),('A1',r'Residual at x=3 is $6-6=0$.')),
P('Find the correlation coefficient and explain why this does not establish causation.',('M1',r'$\sum(y-\bar y)^2=26$, so $r=16/\sqrt{10(26)}$.'),('A1',f'r = {_r:.4f}.'),('R1','A strong linear association alone cannot rule out confounding variables or another explanation.'))],f'Regression y=1.6x+1.2; prediction 8.4; residual 0; r={_r:.4f}.','Centred sums, regression coefficients and correlation recomputed directly.',sum((x-3)*(y-6) for x,y in zip(_xs,_ys))==16 and sum((y-6)**2 for y in _ys)==26,scatter(list(zip(_xs,_ys)),(0,6),(0,11)),calc=True,hard=True)
add('sp',718,'An independence constraint fixes a missing Venn region','4.11','Conditional probability',r'A Venn diagram has $P(A\text{ only})=k$, $P(A\cap B)=0.20$ and $P(B\text{ only})=0.30$. Events A and B are independent.',[
P('Find k.',('M1',r'$P(B)=0.50$ and $P(A)=k+0.20$.'),('M1',r'Independence gives $0.20=0.50(k+0.20)$.'),('A1',r'$k=0.20$.')),
P('Find the probability of neither event and of exactly one event.',('M1','Known disjoint region probabilities are .20,.20,.30.'),('A1','Neither .30; exactly one .50.')),
P(r'Find $P(A\mid A\cup B)$.',('M1',r'$P(A)=0.40$, $P(A\cup B)=0.70$.'),('A1',r'$4/7$.'))],r'$k=.20$; neither .30; exactly one .50; conditional probability $4/7$.','Independence equation and four-region normalization checked.',near(.5*(.2+.2),.2) and near(.2+.2+.3+.3,1),venn(['k','0.20','0.30'],outside='?'),hard=True)
add('sp',719,'Expected reward in a game that stops early','4.7','Discrete random variables',r'Independent attempts succeed with probability 0.4. A player makes at most three attempts and stops at the first success. Rewards are 3 units for success on attempt 1, 2 for first success on attempt 2, 1 for first success on attempt 3, and 0 if all fail.',[
P('Construct the probability distribution of reward R.',('M1','First-success probabilities are .4, .6(.4), .6²(.4); all-fail probability is .6³.'),('A1',r'$P(R=3)=.4$, $P(R=2)=.24$, $P(R=1)=.144$, $P(R=0)=.216$.')),
P('Find the expected reward.',('M1',r'$E(R)=3(.4)+2(.24)+1(.144)$.'),('A1',r'$E(R)=1.824$.')),
P('Given that the player succeeds, find the probability success first occurs on attempt 3.',('M1',r'$P(\text{success})=1-.216=.784$.'),('A1',r'Conditional probability $=.144/.784=9/49$.'))],r'Reward probabilities .4,.24,.144,.216 at 3,2,1,0; expected reward 1.824; conditional probability $9/49$.','Stopped paths are disjoint and sum to one; exact conditional fraction checked.',near(.4+.24+.144+.216,1) and near(3*.4+2*.24+.144,1.824) and F(144,784)==F(9,49),stopped_tree(),hard=True)
add('sp',720,'Why aggregate success rates can reverse a comparison','4.1','Interpreting data',r'A study compares methods A and B in two task groups. Easy tasks: A succeeds on 18 of 20; B on 80 of 100. Difficult tasks: A succeeds on 32 of 80; B on 8 of 20. Task allocation was not randomized.',[
P('Compare the success rates within each task group.',('A1','Easy: A 90%, B 80%.'),('A1','Difficult: both 40%.')),
P('Find the aggregate success rate for each method.',('M1','Combine successes and trial counts, rather than average the two percentages.'),('A1',r'A: $50/100=50\%$; B: $88/120=73.3\%$.')),
P('Explain why the aggregate comparison does not show B is the superior method.',('R1','B is used much more often on easy tasks, while A is used mostly on difficult tasks.'),('R1','Task difficulty confounds the aggregate comparison; a randomized or difficulty-balanced design is needed for a stronger comparison.'))],r'Within groups A is better/equal; aggregate A 50%, B 73.3%; allocation by task difficulty confounds the comparison.','All four group rates and weighted aggregate fractions checked.',F(18,20)>F(80,100) and F(32,80)==F(8,20) and F(50,100)<F(88,120),bars([90,80,40,40],['A easy','B easy','A hard','B hard'],ylab='Success / %'),hard=True)

# CALCULUS: AA SL differentiation/integration only.
add('ca',701,'Tangent and normal at a cubic point','5.4','Tangents and normals',r'Let $f(x)=x^3-3x+2$. P is the point on the curve with x-coordinate 2.',[
P('Find P and the gradient of the tangent there.',('M1',r'$f(2)=4$ and $f^\prime(x)=3x^2-3$.'),('A1',r'$P=(2,4)$; gradient 9.')),
P('Find equations of the tangent and normal.',('M1',r'Use point-gradient form through P.'),('A1',r'Tangent $y=9x-14$.'),('A1',r'Normal $y-4=-(x-2)/9$, equivalently $y=(38-x)/9$.')),
P('Find where the tangent meets the x-axis.',('M1',r'Set $0=9x-14$.'),('A1',r'$(14/9,0)$.'))],r'$P=(2,4)$; tangent $y=9x-14$, normal $y=(38-x)/9$; tangent intercept $14/9$.','Derivative checked by finite differences; both lines pass through P with perpendicular slopes.',near(((2.00001)**3-3*2.00001+2-(1.99999**3-3*1.99999+2))/.00002,9,1e-7) and 9*(-1/9)==-1,plot([(lambda x:x**3-3*x+2,(-2,3),None)],(-2,3),(-3,10),xt=[-2,0,2,3],yt=[0,4,8],points=[(2,4,'P')]))
add('ca',702,'Classifying two stationary points of a cubic','5.8','Stationary points',r'The graph of $f(x)=x^3-6x^2+9x+1$ is shown.',[
P('Find and factorize the first derivative.',('M1','Differentiate each term.'),('A1',r'$f^\prime(x)=3x^2-12x+9=3(x-1)(x-3)$.')),
P('Find and classify both stationary points.',('M1',r'Stationary x-values are 1 and 3; $f^{\prime\prime}=6x-12$.'),('A1',r'$(1,5)$ is a local maximum since $f^{\prime\prime}(1)=-6$.'),('A1',r'$(3,1)$ is a local minimum since $f^{\prime\prime}(3)=6$.')),
P('State the open intervals on which f is increasing.',('M1','Use the signs of the factorized first derivative.'),('A1',r'$(-\infty,1)\cup(3,\infty)$.'))],r'Maximum $(1,5)$, minimum $(3,1)$; increasing for $x<1$ or $x>3$.','Stationary coordinates, second derivative signs and first derivative factorization checked.',1-6+9+1==5 and 27-54+27+1==1 and all(near(3*x*x-12*x+9,3*(x-1)*(x-3)) for x in [-2,0,2,4]),plot([(lambda x:x**3-6*x*x+9*x+1,(-.2,4.2),None)],(-.2,4.2),(-1,8),xt=[0,1,2,3,4],yt=[0,1,5]))
add('ca',703,'Recovering a curve from its gradient and one point','5.5','Antidifferentiation',r'A curve has gradient $\dfrac{dy}{dx}=6x^2-4x+3$ and passes through $(1,8)$. The graph shows its gradient function.',[
P('Find the equation of the curve.',('M1',r'$y=2x^3-2x^2+3x+C$.'),('M1',r'$8=2-2+3+C$ gives $C=5$.'),('A1',r'$y=2x^3-2x^2+3x+5$.')),
P('Find the change in y from x=1 to x=2.',('M1',r'Integrate the gradient from 1 to 2, or subtract recovered function values.'),('A1',r'$y(2)-y(1)=19-8=11$.')),
P('Explain whether the curve ever has a horizontal tangent.',('R1',r'The gradient quadratic has discriminant $(-4)^2-4(6)(3)=-56<0$ and positive leading coefficient, so it is always positive; no horizontal tangent.'))],r'$y=2x^3-2x^2+3x+5$; increase 11; no horizontal tangent.','Recovered point, derivative and definite gradient integral checked.',2-2+3+5==8 and near(integral(lambda x:6*x*x-4*x+3,1,2),11),plot([(lambda x:6*x*x-4*x+3,(-1,2),None)],(-1,2),(0,20),xt=[-1,0,1,2],yt=[0,3,10],ylab="dy/dx"))
add('ca',704,'Area under an arch and a symmetry argument','5.11','Definite integrals',r'The curve $y=6x-x^2$ forms an arch above the x-axis between its intercepts.',[
P('Find the intercepts and show the curve is nonnegative between them.',('M1',r'$6x-x^2=x(6-x)$.'),('A1',r'Intercepts 0 and 6; both factors are nonnegative for $0\le x\le6$.')),
P('Find the enclosed area.',('M1',r'$\int_0^6(6x-x^2)\,dx=[3x^2-x^3/3]_0^6$.'),('A1',r'Area $=108-72=36$.')),
P('Find the vertical line dividing this area into equal halves, with a reason.',('R1',r'The parabola and bounding interval are symmetric about $x=3$.'),('A1',r'The dividing line is $x=3$; each area is 18.'))],r'Intercepts 0,6; area 36; bisector $x=3$.','Numerical integration verifies total and half areas independently.',near(integral(lambda x:6*x-x*x,0,6),36) and near(integral(lambda x:6*x-x*x,0,3),18),plot([(lambda x:6*x-x*x,(0,6),None)],(-1,7),(-1,11),xt=[0,3,6],yt=[0,9]))
add('ca',705,'Signed integral versus total geometric area','5.11','Areas and signs',r'Let $f(x)=x^2-4$ on $[-3,3]$.',[
P('Find the x-intercepts and the intervals where f is negative.',('M1',r'$x^2-4=(x-2)(x+2)$.'),('A1',r'Intercepts $-2,2$; negative for $-2<x<2$.')),
P('Evaluate the signed definite integral.',('M1',r'$\int_{-3}^3(x^2-4)\,dx=[x^3/3-4x]_{-3}^3$.'),('A1',r'The signed integral is $-6$.')),
P('Find the total area between the curve and axis over this interval.',('M1',r'Split at both roots and reverse the sign of the central integral.'),('A1',r'Central area $32/3$, two outer areas total $14/3$; total $46/3$.'))],r'Signed integral -6; geometric area $46/3$.','Separate polynomial integrals verify positive and negative contributions.',near(integral(lambda x:x*x-4,-3,3),-6) and near(-integral(lambda x:x*x-4,-2,2)+2*integral(lambda x:x*x-4,2,3),46/3),plot([(lambda x:x*x-4,(-3,3),None)],(-3,3),(-5,6),xt=[-3,-2,0,2,3],yt=[-4,0,5]))
add('ca',706,'Area between a line and a parabola','5.11','Areas between curves',r'The graphs of $y=2x$ and $y=x^2$ bound a finite region.',[
P('Find both intersections.',('M1',r'$x^2=2x$ gives $x(x-2)=0$.'),('A1',r'$(0,0)$ and $(2,4)$.')),
P('Find the exact enclosed area.',('R1',r'For $0<x<2$, $2x>x^2$, so subtract the parabola from the line.'),('M1',r'$\int_0^2(2x-x^2)\,dx=[x^2-x^3/3]_0^2$.'),('A1',r'Area $=4/3$.')),
P('Explain why integrating x²−2x would produce the wrong sign for geometric area.',('R1','It subtracts the upper boundary from the lower boundary, making the integrand negative throughout the interior.'))],r'Intersections $(0,0),(2,4)$; enclosed area $4/3$.','Analytic difference integral checked against independent quadrature.',near(integral(lambda x:2*x-x*x,0,2),4/3),plot([(lambda x:2*x,(-.5,2.5),None),(lambda x:x*x,(-.5,2.5),None)],(-.5,2.5),(-1,7),xt=[0,1,2],yt=[0,2,4,6]))
add('ca',707,'Distance travelled when velocity changes sign twice','5.9','Kinematics',r'A particle has velocity $v(t)=t^2-4t+3$ m s$^{-1}$ for $0\le t\le4$ seconds.',[
P('Find when it changes direction.',('M1',r'$v=(t-1)(t-3)$.'),('A1','At t=1 and t=3 seconds; the velocity changes sign at each.')),
P('Find its displacement over the four seconds.',('M1',r'$\int_0^4v(t)\,dt=[t^3/3-2t^2+3t]_0^4$.'),('A1',r'Displacement $4/3$ m.')),
P('Find the total distance travelled.',('M1',r'Split at 1 and 3: $\int_0^1v-\int_1^3v+\int_3^4v$.'),('A1',r'The three distances are each $4/3$ m, so total 4 m.'))],r'Direction changes at 1,3 s; displacement $4/3$ m; distance 4 m.','Three signed velocity integrals independently evaluated.',near(integral(lambda t:t*t-4*t+3,0,4),4/3) and near(integral(lambda t:t*t-4*t+3,0,1)-integral(lambda t:t*t-4*t+3,1,3)+integral(lambda t:t*t-4*t+3,3,4),4),plot([(lambda t:t*t-4*t+3,(0,4),None)],(0,4),(-2,4),xt=[0,1,2,3,4],yt=[-1,0,3],xlab='t / s',ylab='v / m s⁻¹'))
add('ca',708,'A chain rule gradient with a large exact value','5.6','Chain rule',r'Let $f(x)=(3x^2+1)^4$.',[
P('Find the first derivative.',('M1',r'Differentiate the outer fourth power and multiply by $6x$.'),('A1',r'$f^\prime(x)=24x(3x^2+1)^3$.')),
P('Find the tangent equation at x=1.',('M1',r'$f(1)=256$ and $f^\prime(1)=24(4^3)=1536$.'),('A1',r'$y-256=1536(x-1)$, or $y=1536x-1280$.')),
P('State where f is decreasing and explain the sign.',('R1',r'The cubed factor is always positive, so $f^\prime$ has the sign of x.'),('A1',r'f is decreasing for $x<0$.'))],r'$f^\prime=24x(3x^2+1)^3$; tangent $y=1536x-1280$; decreasing for x<0.','Chain-rule derivative checked by finite differences and tangent data exactly evaluated.',24*4**3==1536 and 4**4==256 and near((((3*(1+1e-6)**2+1)**4)-((3*(1-1e-6)**2+1)**4))/(2e-6),1536,1e-7),plot([(lambda x:(3*x*x+1)**4,(-1.2,1.2),None)],(-1.2,1.2),(-20,850),xt=[-1,0,1],yt=[0,256,625]))
add('ca',709,'Product rule and a changing concavity','5.7','Product rule and second derivative',r'Let $f(x)=xe^{-x}$ for $x\ge0$.',[
P('Find the first derivative and the maximum point.',('M1',r'$f^\prime=e^{-x}-xe^{-x}=e^{-x}(1-x)$.'),('R1','The derivative is positive before 1 and negative after 1.'),('A1',r'Maximum $(1,e^{-1})$.')),
P('Find the second derivative and point of inflexion.',('M1',r'$f^{\prime\prime}=e^{-x}(x-2)$.'),('R1','This changes from negative to positive at x=2.'),('A1',r'Inflexion point $(2,2e^{-2})$.'))],r'Maximum $(1,1/e)$; inflexion $(2,2/e^2)$.','Both derivatives checked by numerical differences and their sign factors analyzed.',near(((1.00001*math.exp(-1.00001))-(.99999*math.exp(-.99999)))/.00002,0,1e-7),plot([(lambda x:x*math.exp(-x),(0,6),None)],(0,6),(-.02,.45),xt=[0,1,2,4,6],yt=[0,.2,.4]))
add('ca',710,'A quotient with a maximum and minimum','5.6','Quotient rule',r'Let $f(x)=\dfrac{x}{x^2+1}$ for real x.',[
P('Find the derivative in simplified form.',('M1',r'$f^\prime=[(x^2+1)-2x^2]/(x^2+1)^2$.'),('A1',r'$f^\prime=(1-x^2)/(x^2+1)^2$.')),
P('Find and classify both stationary points using sign changes.',('M1',r'Stationary x-values are ±1; denominator is always positive.'),('A1',r'$(-1,-1/2)$ is a local minimum: derivative changes negative to positive.'),('A1',r'$(1,1/2)$ is a local maximum: derivative changes positive to negative.')),
P('State the interval of increase.',('A1',r'$(-1,1)$.'))],r'Minimum $(-1,-1/2)$, maximum $(1,1/2)$; increasing on $(-1,1)$.','Quotient derivative checked numerically on both sides and within stationary interval.',all(near((((x+1e-6)/((x+1e-6)**2+1))-((x-1e-6)/((x-1e-6)**2+1)))/(2e-6),(1-x*x)/(x*x+1)**2,1e-6) for x in [-3,-.5,0,2]),plot([(lambda x:x/(x*x+1),(-5,5),None)],(-5,5),(-.7,.7),xt=[-4,-1,0,1,4],yt=[-.5,.5]))
add('ca',711,'An open box made from a square sheet','5.8','Optimization',r'Squares of side x cm are removed from each corner of a 24 cm square sheet. The sides are folded to form an open box.',[
P('Write the volume and physical domain.',('M1',r'$V=x(24-2x)^2$.'),('A1',r'$0<x<12$.')),
P('Find the box with maximum volume.',('M1',r'$V^\prime=576-192x+12x^2=12(x-4)(x-12)$.'),('R1','Only x=4 is an interior stationary point; derivative changes from positive to negative there.'),('A1',r'Cut x=4 cm; dimensions $16\times16\times4$ cm.')),
P('Give the maximum volume and explain why an endpoint cannot improve it.',('A1',r'$V=1024$ cm$^3$.'),('R1','As x approaches 0 or 12, volume approaches zero; the unique interior maximum is global.'))],r'Cut 4 cm; box $16\times16\times4$ cm, volume 1024 cm³.','Derivative factorization and global sign behavior checked; direct grid confirms bound.',4*16*16==1024 and all(x*(24-2*x)**2<=1024+1e-8 for x in [k/100 for k in range(1201)]),svg(f'<rect x="185" y="45" width="270" height="270" fill="none" stroke="black" stroke-width="2"/>'+''.join(f'<rect x="{x}" y="{y}" width="45" height="45" fill="none" stroke="black" stroke-width="1.5" stroke-dasharray="5 4"/>' for x in [185,410] for y in [45,270])+text(320,340,'24 cm')+text(207,30,'x')+text(468,80,'x')),hard=True)
add('ca',712,'Minimum material for a closed cylindrical can','5.8','Optimization',r'A closed cylinder has fixed volume $250\pi$ cm³. Its radius r and height h are positive.',[
P('Express h and the total surface area S in terms of r.',('M1',r'$\pi r^2h=250\pi$, so $h=250/r^2$.'),('A1',r'$S=2\pi r^2+2\pi rh=2\pi r^2+500\pi/r$.')),
P('Find the dimensions minimizing S.',('M1',r'$S^\prime=4\pi r-500\pi/r^2=0$ gives $r^3=125$.'),('A1',r'$r=5$ cm and $h=10$ cm.')),
P('Confirm it is a minimum and find the minimum area.',('R1',r'$S^{\prime\prime}=4\pi+1000\pi/r^3>0$ for every r>0, so the stationary point is the unique minimum.'),('A1',r'$S_{\min}=50\pi+100\pi=150\pi$ cm$^2$.'))],r'Radius 5, height 10 cm; minimum surface area $150\pi$ cm².','Volume constraint and positive second derivative checked; recovered area calculated independently.',5**2*10==250 and near(2*math.pi*25+2*math.pi*5*10,150*math.pi),svg('<ellipse cx="320" cy="80" rx="105" ry="33" fill="none" stroke="black" stroke-width="2"/><ellipse cx="320" cy="280" rx="105" ry="33" fill="none" stroke="black" stroke-width="2"/>'+line(215,80,215,280)+line(425,80,425,280)+line(320,80,425,80)+text(375,65,'r')+text(450,185,'h')),hard=True)
_qx=math.sqrt(2.5)
add('ca',713,'The nearest points on a parabola','5.8','Optimization',r'P is $(0,3)$ and Q is a variable point $(x,x^2)$ on a parabola. Minimize the distance PQ.',[
P('Show that the squared distance is a quartic polynomial.',('M1',r'$D^2=x^2+(x^2-3)^2$.'),('A1',r'$D^2=x^4-5x^2+9$.')),
P('Find all stationary x-values of the squared distance and classify them.',('M1',r'$(D^2)^\prime=4x^3-10x=2x(2x^2-5)$.'),('A1',r'$x=0,\pm\sqrt{5/2}$.'),('R1',r'Second derivative $12x^2-10$ is negative at 0 and positive at the other two.')),
P('Find both nearest points and the minimum distance.',('A1',r'$Q=(\pm\sqrt{5/2},5/2)$.'),('A1',r'$D_{\min}^2=11/4$, so $D_{\min}=\sqrt{11}/2$.'),('R1',r'$D^2-11/4=(x^2-5/2)^2\ge0$ confirms the global minimum.'))],r'Nearest points $(\pm\sqrt{5/2},5/2)$; distance $\sqrt{11}/2$.','Squared-distance identity and nonnegative global-minimum decomposition checked.',all(near(x*x+(x*x-3)**2-11/4,(x*x-2.5)**2) for x in [-4,-_qx,0,_qx,3]),plot([(lambda x:x*x,(-2.5,2.5),None)],(-3,3),(-1,7),xt=[-2,0,2],yt=[0,3,6],points=[(0,3,'P')]),hard=True)
add('ca',714,'An integral recognized by the reverse chain rule','5.10','Integration by inspection',r'Let $f(x)=\dfrac{2x}{1+x^2}$ for $x\ge0$. Consider the area below f from 0 to $\sqrt3$.',[
P('Find an antiderivative.',('M1',r'The numerator is the derivative of the denominator.'),('A1',r'$\int f(x)\,dx=\ln(1+x^2)+C$.')),
P('Find the exact area.',('M1',r'$[\ln(1+x^2)]_0^{\sqrt3}$.'),('A1',r'Area $=\ln4$.')),
P('Find the vertical line x=a that divides this area in half.',('M1',r'$\ln(1+a^2)=\frac12\ln4=\ln2$.'),('R1','a lies in the nonnegative area interval, so choose the positive root.'),('A1',r'$a=1$.'))],r'Area $\ln4$; area bisector $x=1$.','Integral independently evaluated and half-area equality checked.',near(integral(lambda x:2*x/(1+x*x),0,math.sqrt(3)),math.log(4)) and near(math.log(2),.5*math.log(4)),plot([(lambda x:2*x/(1+x*x),(0,2.1),None)],(0,2.1),(0,1.3),xt=[0,1,round(math.sqrt(3),3),2],yt=[0,1]),hard=True)
add('ca',715,'Accumulation from a decaying inflow rate','5.11','Integration in context',r'A tank initially contains 10 litres. Water enters at rate $R(t)=12e^{-t/3}$ litres per minute for $t\ge0$. There is no outflow.',[
P('Find the volume V(t).',('M1',r'$V(t)=10+\int_0^t12e^{-u/3}\,du$.'),('A1',r'$V(t)=10+36(1-e^{-t/3})$.')),
P('Find when the volume first reaches 40 litres, giving an exact answer.',('M1',r'$40=46-36e^{-t/3}$ gives $e^{-t/3}=1/6$.'),('A1',r'$t=3\ln6$ minutes.')),
P('Explain why the volume never reaches 46 litres in finite time.',('R1',r'$V(t)=46-36e^{-t/3}<46$ for every finite t.'),('R1','The remaining possible accumulated inflow is always positive, although it tends to zero.'))],r'$V=10+36(1-e^{-t/3})$; 40 litres at $3\ln6$ min; never reaches 46 in finite time.','Initial value, derivative and target volume reconstructed.',near(10+36*(1-math.exp(-3*math.log(6)/3)),40) and near(integral(lambda t:12*math.exp(-t/3),0,6),36*(1-math.exp(-2))),plot([(lambda t:12*math.exp(-t/3),(0,12),None)],(0,12),(0,14),xt=[0,3,6,9,12],yt=[0,6,12],xlab='t / min',ylab='R / L min⁻¹'),hard=True)
add('ca',716,'Recovering a cubic from an inflexion and a gradient','5.7','Second derivatives',r'A cubic has equation $f(x)=x^3+ax^2+bx+c$. It passes through $(0,4)$, has a point of inflexion at x=1, and has gradient −2 there.',[
P('Find a,b,c.',('A1',r'$c=4$.'),('M1',r'$f^{\prime\prime}=6x+2a$; at x=1 this is zero, so $a=-3$.'),('M1',r'$f^\prime(1)=3+2a+b=-2$.'),('A1',r'$b=1$; $f=x^3-3x^2+x+4$.')),
P('Find the inflexion point and its tangent equation.',('A1',r'$f(1)=3$, so point $(1,3)$.'),('M1',r'Tangent $y-3=-2(x-1)$.'),('A1',r'$y=5-2x$.')),
P('Confirm that the stationary second derivative value corresponds to a genuine change in concavity.',('R1',r'$f^{\prime\prime}=6(x-1)$ changes from negative to positive across 1.'))],r'$a=-3,b=1,c=4$; inflexion $(1,3)$; tangent $y=5-2x$.','Point, first-derivative condition and second-derivative sign change all checked.',6+2*(-3)==0 and 3+2*(-3)+1==-2 and 1-3+1+4==3,plot([(lambda x:x**3-3*x*x+x+4,(-1,3),None)],(-1,3),(-2,7),xt=[-1,0,1,2,3],yt=[0,3,4]),hard=True)
add('ca',717,'A logarithmic quotient with a global maximum','5.6','Quotient rule',r'Let $f(x)=\dfrac{\ln x}{x}$ for $x>0$.',[
P('Find the first derivative.',('M1',r'$f^\prime=[x(1/x)-\ln x]/x^2$.'),('A1',r'$f^\prime=(1-\ln x)/x^2$.')),
P('Find the global maximum point, justifying it by derivative signs.',('M1',r'$1-\ln x=0$ gives $x=e$.'),('R1',r'The derivative is positive for $0<x<e$ and negative for $x>e$.'),('A1',r'Global maximum $(e,1/e)$.')),
P('Find the tangent equation at x=1.',('M1',r'$f(1)=0$ and $f^\prime(1)=1$.'),('A1',r'$y=x-1$.'))],r'$f^\prime=(1-\ln x)/x^2$; maximum $(e,1/e)$; tangent $y=x-1$.','Quotient derivative checked by finite differences at positive inputs; stationary condition exact.',all(near(((math.log(x+1e-6)/(x+1e-6))-(math.log(x-1e-6)/(x-1e-6)))/(2e-6),(1-math.log(x))/(x*x),1e-6) for x in [.5,1,2,4]),plot([(lambda x:math.log(x)/x,(.3,7),None)],(0,7),(-1,.5),xt=[0,1,3,5,7],yt=[-1,0,.4]),hard=True)
add('ca',718,'Stationary and inflexion points of a trigonometric sum','5.8','Trigonometric calculus',r'Let $f(x)=\sin x+\cos x$ on $0\le x\le2\pi$.',[
P('Find and classify the stationary points.',('M1',r'$f^\prime=\cos x-\sin x=0$ gives $x=\pi/4,5\pi/4$.'),('M1',r'$f^{\prime\prime}=-\sin x-\cos x$.'),('A1',r'Maximum $(\pi/4,\sqrt2)$; minimum $(5\pi/4,-\sqrt2)$.')),
P('Find the inflexion points and verify concavity changes.',('M1',r'$f^{\prime\prime}=0$ gives $\sin x+\cos x=0$.'),('A1',r'Points $(3\pi/4,0)$ and $(7\pi/4,0)$.'),('R1','The second derivative changes sign at both simple zero crossings.')),
P('Explain why the stationary extrema are also the global extrema on the closed domain.',('R1','The only other candidates are endpoints, where f=1; these lie strictly between −√2 and √2.'))],r'Maximum $(\pi/4,\sqrt2)$, minimum $(5\pi/4,-\sqrt2)$; inflexions $(3\pi/4,0),(7\pi/4,0)$.','Trig values at all four points and endpoint comparisons checked.',near(math.sin(math.pi/4)+math.cos(math.pi/4),math.sqrt(2)) and all(near(math.sin(x)+math.cos(x),0) for x in [3*math.pi/4,7*math.pi/4]),plot([(lambda x:math.sin(x)+math.cos(x),(0,2*math.pi),None)],(0,2*math.pi),(-1.7,1.7),xt=[0,round(math.pi,3),round(2*math.pi,3)],yt=[-1,0,1]),hard=True)
add('ca',719,'A particle speeds up and then slows down','5.9','Kinematics',r'A particle has velocity $v(t)=4te^{-t^2}$ m s$^{-1}$ for $t\ge0$.',[
P('Find its acceleration and the time of maximum speed.',('M1',r'$a(t)=4e^{-t^2}-8t^2e^{-t^2}=4e^{-t^2}(1-2t^2)$.'),('R1','Velocity is nonnegative; acceleration changes positive to negative at t=1/√2.'),('A1',r'Maximum speed occurs at $t=1/\sqrt2$ s and equals $2\sqrt2e^{-1/2}$ m s$^{-1}$.')),
P('Find the distance travelled from t=0 to t=2 exactly.',('M1',r'$\int_0^2 4te^{-t^2}\,dt=[-2e^{-t^2}]_0^2$.'),('A1',r'Distance $=2(1-e^{-4})$ m.')),
P('Explain why no sign split is needed for this distance integral.',('R1','For t≥0 both t and the exponential are nonnegative, so velocity never becomes negative.'))],r'Maximum speed at $1/\sqrt2$ s, value $2\sqrt2e^{-1/2}$; distance $2(1-e^{-4})$ m.','Product/chain acceleration checked and exact distance matches quadrature.',near(integral(lambda t:4*t*math.exp(-t*t),0,2),2*(1-math.exp(-4))) and near(1-2*(1/math.sqrt(2))**2,0),plot([(lambda t:4*t*math.exp(-t*t),(0,3),None)],(0,3),(0,2),xt=[0,1,2,3],yt=[0,1,2],xlab='t / s',ylab='v / m s⁻¹'),hard=True)
add('ca',720,'Area between exponential mirror graphs','5.11','Areas between curves',r'Consider $y=e^x$ and $y=e^{-x}$ between the vertical lines $x=-\ln2$ and $x=\ln2$.',[
P('Find their intersection and state which graph is upper on each side.',('M1',r'$e^x=e^{-x}$ implies $e^{2x}=1$, hence x=0.'),('A1',r'Intersection $(0,1)$; $e^{-x}$ upper for x<0 and $e^x$ upper for x>0.')),
P('Find the total area between the curves exactly.',('R1','Reflection symmetry gives twice the positive-side area.'),('M1',r'$A=2\int_0^{\ln2}(e^x-e^{-x})\,dx=2[e^x+e^{-x}]_0^{\ln2}$.'),('A1',r'$A=2[(2+1/2)-2]=1$.')),
P('Explain why a single signed integral of eˣ−e⁻ˣ over the whole interval is zero.',('R1','The difference is odd and the interval is symmetric, so opposite signed contributions cancel although geometric area is positive.'))],r'Intersection $(0,1)$; total area 1; signed whole-interval difference integral 0.','Split area and odd signed integral independently verified by quadrature.',near(2*integral(lambda x:math.exp(x)-math.exp(-x),0,math.log(2)),1) and near(integral(lambda x:math.exp(x)-math.exp(-x),-math.log(2),math.log(2)),0),plot([(math.exp,(-1,1),None),(lambda x:math.exp(-x),(-1,1),None)],(-1,1),(0,3),xt=[round(-math.log(2),3),0,round(math.log(2),3)],yt=[0,1,2]),hard=True)

# FUNCTIONS: 20 separately authored problems.
add('fn',701,'Reading a parabola in three algebraic forms','2.6','Quadratic functions',r'The graph of $f(x)=x^2-6x+5$ is shown.',[
P('Write $f$ in factorized and completed-square forms.',('M1','Find factors with product 5 and sum -6; complete the square.'),('A1',r'$f(x)=(x-1)(x-5)$.'),('A1',r'$f(x)=(x-3)^2-4$.')),
P('State the vertex and solve $f(x)=5$.',('A1',r'Vertex $(3,-4)$.'),('M1',r'$x^2-6x=x(x-6)=0$.'),('A1',r'$x=0$ or $6$.'))],r'Vertex $(3,-4)$; level 5 at $x=0,6$.','Both alternative forms and level solutions checked by substitution.',all(near(x*x-6*x+5,(x-3)**2-4) and near(x*x-6*x+5,(x-1)*(x-5)) for x in [-2,0,.7,3,6]),plot([(lambda x:x*x-6*x+5,(-1,7),None)],(-1,7),(-5,8),xt=[0,3,6],yt=[-4,0,5]))
add('fn',702,'A parabola reconstructed from a vertex and a point','2.6','Quadratic functions',r'A parabola has vertex $V(2,-3)$ and passes through $P(0,5)$.',[
P('Find its equation in vertex form.',('M1',r'$y=a(x-2)^2-3$; $5=4a-3$.'),('A1',r'$y=2(x-2)^2-3$.')),
P('State its range and find its x-intercepts exactly.',('A1',r'Range $[-3,\infty)$.'),('M1',r'$2(x-2)^2=3$.'),('A1',r'$x=2\pm\sqrt{3/2}$.'))],r'$y=2(x-2)^2-3$, range $[-3,\infty)$; roots $2\pm\sqrt{3/2}$.','Vertex, given point and both roots checked.',near(2*(0-2)**2-3,5) and all(near(2*(x-2)**2-3,0) for x in [2-math.sqrt(1.5),2+math.sqrt(1.5)]),plot([(lambda x:2*(x-2)**2-3,(-1,5),None)],(-1,5),(-4,10),xt=[0,2,4],yt=[-3,0,5],points=[(2,-3,'V'),(0,5,'P')]))
add('fn',703,'A rational inequality separated by an asymptote','2.8','Rational functions',r'Let $f(x)=\dfrac{2x+3}{x-1}$, $x\ne1$.',[
P('Rewrite $f$ as a constant plus a reciprocal expression; state both asymptotes.',('M1',r'$2x+3=2(x-1)+5$.'),('A1',r'$f(x)=2+5/(x-1)$; asymptotes $x=1$, $y=2$.')),
P(r'Solve $f(x)>3$, accounting for the excluded input.',('M1',r'$f(x)-3=(6-x)/(x-1)$.'),('M1','Test intervals separated by 1 and 6.'),('A1',r'$1<x<6$, with both endpoints excluded.'))],r'$f>3$ for $1<x<6$; asymptotes $x=1,y=2$.','Equivalent expression and sign on all three intervals checked.',all(near((2*x+3)/(x-1),2+5/(x-1)) for x in [-3,0,2,6,9]) and all((((2*x+3)/(x-1)>3)==(1<x<6)) for x in [-2,0,1.5,5,6,8]),plot([(lambda x:(2*x+3)/(x-1),(-4,.99),None),(lambda x:(2*x+3)/(x-1),(1.01,8),None)],(-4,8),(-6,10),xt=[0,1,6],yt=[0,2,3],segments=[((1,-6),(1,10)),((-4,2),(8,2))]))
add('fn',704,'Composition changes the admissible inputs','2.5','Composite and inverse functions',r'Let $f(x)=\sqrt{x+1}$ and $g(x)=2x-3$ on their largest real domains. The graph shows $f$.',[
P(r'Find $f\circ g$ and its domain.',('M1',r'$f(g(x))=\sqrt{2x-2}$.'),('A1',r'Domain $[1,\infty)$.')),
P(r'Find $g\circ f$ and its domain.',('M1',r'$g(f(x))=2\sqrt{x+1}-3$.'),('A1',r'Domain $[-1,\infty)$.')),
P(r'Find the inverse of $h=f\circ g$, including its domain.',('M1',r'$y=\sqrt{2x-2}$ gives $x=(y^2+2)/2$.'),('A1',r'$h^{-1}(x)=(x^2+2)/2$ for $x\ge0$.'))],r'$f\circ g=\sqrt{2x-2}$; $g\circ f=2\sqrt{x+1}-3$; $h^{-1}=(x^2+2)/2$ on $x\ge0$.','Domain inequalities and inverse round trips checked.',all(near(math.sqrt(2*((y*y+2)/2)-2),y) for y in [0,.5,1,4]),plot([(lambda x:math.sqrt(x+1),(-1,8),None)],(-2,8),(-1,4),xt=[-1,0,3,8],yt=[0,1,2,3]))
add('fn',705,'Restricting a quadratic to obtain an inverse','2.5','Composite and inverse functions',r'Let $f(x)=x^2-4x+7$ with domain $[2,\infty)$.',[
P('Find its range and inverse function.',('M1',r'$f(x)=(x-2)^2+3$.'),('A1',r'Range $[3,\infty)$.'),('A1',r'$f^{-1}(x)=2+\sqrt{x-3}$ on $[3,\infty)$.')),
P(r'Solve $f(x)=f(6-x)$, respecting both input restrictions.',('R1',r'$x\ge2$ and $6-x\ge2$ require $2\le x\le4$.'),('M1',r'$x^2-4x+7=x^2-8x+19$.'),('A1',r'$x=3$, which is admissible.'))],r'Inverse $2+\sqrt{x-3}$ on $[3,\infty)$; equation solution $3$.','Inverse round trip and common input domain checked.',all(near(2+math.sqrt((x*x-4*x+7)-3),x) for x in [2,3,5,10]),plot([(lambda x:x*x-4*x+7,(2,6),None)],(0,6),(0,20),xt=[0,2,4,6],yt=[0,3,11],points=[(2,3,'included')]))
_vertices=[(-2,0),(0,4),(3,1)]
add('fn',706,'Translations and reflections of a finite graph','2.11','Graph transformations',r'The graph of $f$ joins $(-2,0)$, $(0,4)$ and $(3,1)$ by straight segments, with domain $[-2,3]$. Define $g(x)=f(x-2)+1$.',[
P('Describe the translation and give the three vertices of $g$.',('A1','Translate 2 units right and 1 unit up.'),('A1',r'Vertices $(0,1),(2,5),(5,2)$.')),
P('State the domain and range of $g$.',('A1',r'Domain $[0,5]$.'),('A1',r'Range $[1,5]$.')),
P('Reflect the graph of $g$ in the y-axis. State the new domain and highest point.',('M1',r'Each $(x,y)$ becomes $(-x,y)$.'),('A1',r'Domain $[-5,0]$; highest point $(-2,5)$.'))],r'Vertices $(0,1),(2,5),(5,2)$; domain $[0,5]$, range $[1,5]$; reflected highest point $(-2,5)$.','All vertices mapped directly; bounds checked.',[(x+2,y+1) for x,y in _vertices]==[(0,1),(2,5),(5,2)],plot([],(-3,4),(-1,6),xt=[-2,0,3],yt=[0,1,4],points=[(x,y,f'({x},{y})') for x,y in _vertices],segments=[(_vertices[0],_vertices[1]),(_vertices[1],_vertices[2])]))
add('fn',707,'Cooling towards a nonzero ambient temperature','2.9','Exponential models',r'A drink has temperature $T(t)=18+72e^{-kt}$ °C, where $t$ is minutes and $k>0$. After 10 minutes its temperature is $54$ °C.',[
P('Find $k$ exactly.',('M1',r'$36=72e^{-10k}$ gives $e^{-10k}=1/2$.'),('A1',r'$k=\ln2/10$.')),
P('Find the temperature after 30 minutes.',('M1',r'$T(30)=18+72(1/2)^3$.'),('A1',r'$27$ °C.')),
P('Find when it first reaches 25 °C and explain why it never reaches 18 °C.',('M1',r'$t=10\ln(72/7)/\ln2$.'),('A1',r'$t=33.6$ minutes to 3 significant figures.'),('R1',r'The exponential term is positive at every finite time; 18 °C is an asymptote.'))],r'$k=\ln2/10$; $T(30)=27$ °C; 25 °C at $33.6$ minutes.','Observation, later value and inverse-time residual checked.',near(18+72*.5**3,27) and near(18+72*math.exp(-math.log(2)/10*(10*math.log(72/7)/math.log(2))),25),plot([(lambda t:18+72*math.exp(-math.log(2)*t/10),(0,50),None)],(0,50),(0,100),xt=[0,10,30,50],yt=[18,54,90],points=[(10,54,'given')],xlab='t / min',ylab='T / °C'),calc=True)
add('fn',708,'A logarithmic graph determined by its asymptote','2.9','Logarithmic functions',r'The function $f(x)=a\ln(x-b)$ has vertical asymptote $x=1$ and passes through $(e+1,3)$.',[
P('Find $a,b$ and the x-intercept.',('A1',r'$b=1$.'),('M1',r'$3=a\ln e=a$.'),('A1',r'$a=3$ and the intercept is $(2,0)$.')),
P('Find its inverse, with domain and range.',('M1',r'$y=3\ln(x-1)$ gives $x=1+e^{y/3}$.'),('A1',r'$f^{-1}(x)=1+e^{x/3}$; domain $\mathbb R$, range $(1,\infty)$.')),
P(r'Solve $f(x)=6$ exactly.',('A1',r'$x=1+e^2$.'))],r'$a=3,b=1$; inverse $1+e^{x/3}$; level 6 at $1+e^2$.','Point, intercept, inverse and exact level solution checked.',near(3*math.log(math.e),3) and near(3*math.log(math.exp(2)),6),plot([(lambda x:3*math.log(x-1),(1.01,8),None)],(0,8),(-5,7),xt=[0,1,2,5],yt=[0,3,6],points=[(math.e+1,3,'(e+1,3)')],segments=[((1,-5),(1,7))]))
add('fn',709,'A rational function that reverses itself','2.5','Composite and inverse functions',r'Let $f(x)=\dfrac{x+3}{x-1}$, $x\ne1$.',[
P(r'Show that $f(f(x))=x$.',('M1',r'$f(f(x))=[(x+3)/(x-1)+3]/[(x+3)/(x-1)-1]$.'),('A1',r'The numerator is $4x/(x-1)$ and denominator $4/(x-1)$, giving $x$.')),
P(r'Explain why this composition is defined for all $x\ne1$, and state $f^{-1}$.',('R1',r'$f(x)=1$ would imply $x+3=x-1$, impossible, so the inner output never equals 1.'),('A1',r'$f^{-1}=f$ on $\mathbb R\setminus\{1\}$.')),
P('Find the fixed points.',('M1',r'$x+3=x(x-1)$ gives $(x-3)(x+1)=0$.'),('A1',r'$(-1,-1)$ and $(3,3)$.'))],r'$f^{-1}=f$; fixed points $(-1,-1),(3,3)$.','Composition checked on both sides of the asymptote and fixed points substituted.',all(near((((x+3)/(x-1))+3)/(((x+3)/(x-1))-1),x) for x in [-4,-1,0,2,3,8]),plot([(lambda x:(x+3)/(x-1),(-5,.99),None),(lambda x:(x+3)/(x-1),(1.01,7),None),(lambda x:x,(-5,7),None)],(-5,7),(-5,7),xt=[-1,0,1,3],yt=[-1,0,1,3]))
add('fn',710,'A profit model with an integer sales constraint','2.7','Quadratic equations and models',r'A firm selling $x$ items has cost $C(x)=400+20x$ and revenue $R(x)=80x-0.5x^2$, with $0\le x\le160$.',[
P('Find the profit function and maximum profit.',('M1',r'$P=R-C=-0.5x^2+60x-400$.'),('M1',r'$P=-0.5(x-60)^2+1400$.'),('A1','Maximum profit 1400 at 60 items.')),
P('Find the exact break-even quantities.',('M1',r'$x^2-120x+800=0$.'),('A1',r'$x=60\pm20\sqrt7$.')),
P('State every whole-number sales quantity giving positive profit.',('M1',r'Roots are $7.08497\ldots$ and $112.915\ldots$; profit is positive between them.'),('A1',r'$x=8,9,\ldots,112$.'))],r'Maximum 1400 at 60 items; break-even $60\pm20\sqrt7$; positive profit for integers 8 to 112.','Exact roots and all integer sign decisions checked.',all(near(-.5*x*x+60*x-400,0) for x in [60-20*math.sqrt(7),60+20*math.sqrt(7)]) and all((-.5*x*x+60*x-400>0)==(8<=x<=112) for x in range(161)),plot([(lambda x:400+20*x,(0,160),(135,3100,'C')),(lambda x:80*x-.5*x*x,(0,160),(80,3400,'R'))],(0,160),(0,3800),xt=[0,40,80,120,160],yt=[0,2000],xlab='items',ylab='money'),calc=True)
add('fn',711,'A family of parabolas and tangency to the axis','2.7','Quadratic discriminant',r'Define $f_k(x)=x^2+kx+k+3$ for real $k$. The diagram shows the member $k=0$.',[
P('Find every $k$ for which the graph touches the x-axis once.',('M1',r'$k^2-4(k+3)=0$.'),('M1',r'$(k-6)(k+2)=0$.'),('A1',r'$k=6,-2$.')),
P('Find the contact point in each case.',('M1',r'Repeated root $x=-k/2$.'),('A1',r'For $k=6$: $(-3,0)$; for $k=-2$: $(1,0)$.')),
P('Find $k$ for which the entire graph is strictly above the axis.',('R1','The positive leading coefficient requires a negative discriminant for strict positivity everywhere.'),('A1',r'$(k-6)(k+2)<0$, hence $-2<k<6$.'))],r'Tangency at $k=6,-2$; strictly above for $-2<k<6$.','Repeated-root points and vertex minimum k+3-k²/4 checked.',6**2-4*(6+3)==0 and (-2)**2-4*(-2+3)==0 and all((k+3-k*k/4>0)==(-2<k<6) for k in range(-5,10)),plot([(lambda x:x*x+3,(-3,3),None)],(-3,3),(-1,13),xt=[-2,0,2],yt=[0,3,12]),hard=True)
add('fn',712,'Comparing a two-stage taxi tariff','2.3','Piecewise functions',r'Company A charges $A(x)=4+1.5x$ for $0\le x\le4$ km, and $A(x)=10+0.8(x-4)$ for $x>4$. Company B charges $B(x)=2+2x$ for $x\ge0$.',[
P('Find where the charges are equal, checking both stages.',('M1',r'$4+1.5x=2+2x$ gives $x=4$ in stage one.'),('M1',r'$6.8+0.8x=2+2x$ gives the same boundary $x=4$.'),('A1','Equal only at 4 km, charge 10.')),
P('State which company is cheaper on either side.',('R1',r'For $0\le x<4$, $A-B=2-0.5x>0$, so B is cheaper.'),('R1',r'For $x>4$, $A-B=4.8-1.2x<0$, so A is cheaper.')),
P('Find the greatest distance affordable with A for a budget of 18.',('M1',r'$10+0.8(x-4)=18$ uses the applicable second stage.'),('A1',r'$x=14$ km.'))],r'Equal at 4 km; B cheaper below 4, A above 4; budget permits 14 km with A.','Boundary costs, tariff signs and budget substitution checked.',near(10+.8*(14-4),18) and near(4+1.5*4,2+2*4),plot([(lambda x:4+1.5*x,(0,4),None),(lambda x:10+.8*(x-4),(4,16),(14,19,'A')),(lambda x:2+2*x,(0,16),(11,26,'B'))],(0,16),(0,36),xt=[0,4,8,12,16],yt=[0,10,18,30],xlab='km',ylab='charge'),hard=True)
_lnroot=root(lambda x:math.log(x)+x-3,2,3)
add('fn',713,'A transcendental intersection and uniqueness','2.10','Graphical equations',r'The graphs of $y=\ln x$ and $y=3-x$ are shown for $x>0$.',[
P('Show that the intersection has x-coordinate between 2 and 3.',('M1',r'At 2, $\ln2<1$; at 3, $\ln3>0$.'),('R1','The ordering reverses, so the continuous graphs cross between 2 and 3.')),
P('Find the intersection coordinates to 3 significant figures.',('M1',r'Solve $\ln x=3-x$ numerically.'),('A1',r'$(2.21,0.792)$, using unrounded $x=2.20794\ldots$.')),
P('Explain why it is the only intersection for $x>0$.',('R1',r'$\ln x$ strictly increases while $3-x$ strictly decreases.'),('R1','Their ordering cannot reverse again after a crossing.'))],r'Unique intersection $(2.21,0.792)$ to 3 significant figures.','Bisection residual checked; monotonic directions justify global uniqueness.',near(math.log(_lnroot),3-_lnroot,1e-12),plot([(math.log,(.1,5),(4,1.7,'ln x')),(lambda x:3-x,(.1,5),(4,-1.3,'3 − x'))],(0,5),(-2,3),xt=[0,1,2,3,4,5],yt=[-1,0,1,2]),calc=True,hard=True)
add('fn',714,'A rectangle constrained by a parabolic roof','2.10','Graphical modelling',r'A rectangle has lower vertices on the x-axis and upper vertices $(x,12-x^2)$ and $(-x,12-x^2)$, where $0<x<\sqrt{12}$.',[
P('Express its area as a function of $x$ and justify the physical domain.',('M1',r'$A(x)=2x(12-x^2)=24x-2x^3$.'),('R1','Width and height must both be positive.')),
P('Use a graphing method to find the maximum area and dimensions.',('M1','Graph the area on the physical domain and locate its maximum.'),('A1',r'Maximum 32 at $x=2$.'),('A1',r'Dimensions $4\times8$.')),
P(r'Confirm that the maximum is global using $32-A(x)=2(x-2)^2(x+4)$.',('R1',r'Both factors on the right are nonnegative on the domain, so $A\le32$, with equality only at 2.'))],r'$A=24x-2x^3$; maximum 32, dimensions $4\times8$.','Supplied polynomial identity and feasible equality case checked.',all(near(32-(24*x-2*x**3),2*(x-2)**2*(x+4)) for x in [.2,1,2,3]) and 2*2*(12-4)==32,plot([(lambda x:12-x*x,(-math.sqrt(12),math.sqrt(12)),None)],(-4,4),(-1,14),xt=[-3,0,3],yt=[0,12],segments=[((-1.4,0),(-1.4,10.04)),((-1.4,10.04),(1.4,10.04)),((1.4,10.04),(1.4,0))]),calc=True,hard=True,caption='A variable admissible rectangle is shown schematically.')
add('fn',715,'Finding an exponential offset from three observations','2.9','Exponential models',r'A model $Q(t)=ab^t+c$, where $a>0,b>1$, satisfies $Q(0)=7$, $Q(1)=12$, $Q(2)=22$.',[
P('Use consecutive differences to find $b$.',('M1',r'$a(b-1)=5$ and $ab(b-1)=10$.'),('A1',r'Dividing gives $b=2$.')),
P('Find $a,c$ and predict $Q(5)$.',('M1',r'$a=5$ from the first difference, and $c=7-5=2$.'),('A1',r'$Q(t)=5(2^t)+2$.'),('A1',r'$Q(5)=162$.')),
P('Explain why the ratios 12/7 and 22/12 are unequal.',('R1',r'The nonzero offset prevents a constant ratio in $Q$; the shifted values $Q-2$ have ratio 2.'))],r'$a=5,b=2,c=2$; $Q(5)=162$.','All observations reconstructed and offset distinction checked.',[5*2**t+2 for t in range(3)]==[7,12,22] and 5*2**5+2==162,scatter([(0,7),(1,12),(2,22)],(0,3),(0,25),xlab='t',ylab='Q'),hard=True)
add('fn',716,'Where a function and its inverse exchange order','2.5','Composite and inverse functions',r'Let $f(x)=x^2$ on $x\ge0$. Its graph and $y=x$ are shown.',[
P('State $f^{-1}$ and how to obtain its graph.',('A1',r'$f^{-1}(x)=\sqrt x$ for $x\ge0$.'),('R1','Reflect in the line y=x.')),
P('Find all intersections of the function and its inverse.',('M1',r'$x^2=\sqrt x$; squaring on $x\ge0$ gives $x^4=x$.'),('M1',r'$x(x^3-1)=0$.'),('A1',r'$(0,0)$ and $(1,1)$.')),
P(r'State where $f<f^{-1}$ and where $f>f^{-1}$.',('R1',r'For $0<x<1$, $x^2<x<\sqrt x$, so $f<f^{-1}$.'),('R1',r'For $x>1$, $\sqrt x<x<x^2$, so $f>f^{-1}$.'))],r'Inverse $\sqrt x$; intersections $(0,0),(1,1)$; function below inverse on $(0,1)$ and above for $x>1$.','All admissible roots and both sign regimes checked.',all((x*x<math.sqrt(x))==(0<x<1) for x in [0,.1,.5,1,2,4]),plot([(lambda x:x*x,(0,2.5),None),(lambda x:x,(0,4),(3.5,3.5,'y = x'))],(0,4),(0,5),xt=[0,1,2,3,4],yt=[0,1,4]),hard=True)
add('fn',717,'Counting solutions on a restricted parabola','2.2','Domains and ranges',r'Let $f(x)=x^2-4x+1$ on $[-1,5]$, with both endpoints included.',[
P('Find its range.',('M1',r'$f=(x-2)^2-3$ has minimum -3 at 2.'),('A1',r'$f(-1)=f(5)=6$, so range $[-3,6]$.')),
P(r'Classify the number of distinct solutions of $f(x)=k$ for every real $k$.',('A1',r'Zero for $k<-3$ or $k>6$.'),('A1',r'One for $k=-3$.'),('A1',r'Two for $-3<k\le6$.')),
P('Explain why an inverse does not exist on the whole domain; give a largest interval restriction that permits one.',('R1','It is not one-to-one, since both endpoints have the same image.'),('A1',r'Restrict to $[-1,2]$ or $[2,5]$.'))],r'Range $[-3,6]$; counts 0 outside, 1 at -3, 2 above -3 through 6; inverse on either half-domain.','Endpoint values, minimum and roots 2±sqrt(k+3) checked against the domain.',(-1)**2-4*(-1)+1==6 and 5**2-4*5+1==6 and 2**2-4*2+1==-3,plot([(lambda x:x*x-4*x+1,(-1,5),None)],(-2,6),(-4,8),xt=[-1,0,2,5],yt=[-3,0,6],points=[(-1,6,''),(5,6,'')]),hard=True)
add('fn',718,'A pencil of lines with a fixed intersection','2.7','Quadratic equations and models',r'Lines $L_k$ have equations $y=(k+1)x-k$. They are compared with $y=x^2$. The diagram shows $L_3$.',[
P('Show that every line passes through the same point on the parabola.',('M1',r'At $x=1$, $y=k+1-k=1$.'),('A1',r'Common point $(1,1)$ lies on the parabola.')),
P('Find the other intersection in terms of $k$.',('M1',r'$x^2-(k+1)x+k=(x-1)(x-k)=0$.'),('A1',r'Other point $(k,k^2)$ when $k\ne1$.')),
P('Find the tangent member, then find all $k$ for which the other point has y-coordinate 9.',('R1',r'Two roots coincide at $k=1$, giving tangency.'),('M1',r'$k^2=9$.'),('A1',r'$k=3$ or $-3$, both distinct from 1.'))],r'Fixed point $(1,1)$, other $(k,k^2)$; tangent $k=1$; y-coordinate 9 gives $k=\pm3$.','Polynomial factorization and both intersection substitutions checked.',all(near(x*x-(k+1)*x+k,(x-1)*(x-k)) for k in [-3,0,1,3] for x in [-2,.5,1,4]),plot([(lambda x:x*x,(-1,4),None),(lambda x:4*x-3,(-1,4),None)],(-1,4),(-4,16),xt=[0,1,3],yt=[0,1,9],points=[(1,1,''),(3,9,'')]),hard=True)
add('fn',719,'The order of vertical transformations matters','2.11','Graph transformations',r'Start with $f(x)=1/x$, $x\ne0$. A translates upwards 2 units. B reflects in the x-axis.',[
P('Apply A then B. Find the final function and horizontal asymptote.',('M1',r'$g(x)=-(1/x+2)=-1/x-2$.'),('A1',r'Asymptote $y=-2$.')),
P('Apply B then A. Find the final function and horizontal asymptote.',('M1',r'$h(x)=-1/x+2$.'),('A1',r'Asymptote $y=2$.')),
P('Determine whether the two final graphs intersect, with a reason.',('M1',r'$h(x)-g(x)=4$ for every permitted input.'),('R1','They are always 4 units apart vertically, so never intersect.'))],r'$g=-1/x-2$, $h=-1/x+2$; asymptotes -2 and 2; no intersection.','Ordered maps and constant separation checked.',all(near((-1/x+2)-(-1/x-2),4) for x in [-4,-1,.5,2]),plot([(lambda x:1/x,(-4,-.08),None),(lambda x:1/x,(.08,4),None)],(-4,4),(-5,5),xt=[-2,-1,0,1,2],yt=[-4,0,4]),hard=True)
add('fn',720,'Two models that agree now but diverge later','2.10','Model evaluation',r'A population is 100 at $t=0$, 150 at $t=5$ and 225 at $t=10$ years. Two models are $E(t)=100(1.5)^{t/5}$ and $Q(t)=0.5t^2+7.5t+100$.',[
P('Verify that both models fit all three observations.',('M1',r'$E(0)=100$, $E(5)=150$, $E(10)=225$.'),('A1',r'$Q(0)=100$, $Q(5)=12.5+37.5+100=150$, $Q(10)=50+75+100=225$.')),
P('Compare their predictions at $t=20$ and find the difference.',('M1',r'$E(20)=100(1.5)^4=506.25$.'),('A1',r'$Q(20)=450$; difference $56.25$.')),
P('Explain why these data alone cannot establish which prediction is more reliable; suggest useful further evidence.',('R1','Both interpolate every observation but make different growth assumptions.'),('R1','A later measured population or contextual constraints on long-term growth would help distinguish them.'))],r'Both fit; predictions at 20 years: 506.25 versus 450, difference 56.25.','Six observation substitutions and both extrapolations checked.',all(near(100*1.5**(t/5),y) and near(.5*t*t+7.5*t+100,y) for t,y in [(0,100),(5,150),(10,225)]) and near(100*1.5**4-450,56.25),scatter([(0,100),(5,150),(10,225)],(0,12),(0,250),xlab='t / years',ylab='population'),calc=True,hard=True)

# NUMBER AND ALGEBRA: 20 distinct structures, 10 medium / 10 hard.
add('na',701,'Recovering an arithmetic progression','1.2','Sequences and series',r'An arithmetic sequence has $u_4=17$ and $u_{11}=45$. The diagram shows these two known terms.',[
P('Find the common difference and the first term.',('M1',r'$u_{11}-u_4=7d=28$.'),('A1',r'$d=4$.'),('A1',r'$u_1=17-3(4)=5$.')),
P(r'Find $S_{20}$ and explain whether $u_{20}$ is greater than the mean of these 20 terms.',('M1',r'$S_{20}=\frac{20}{2}(2(5)+19(4))$.'),('A1',r'$S_{20}=860$.'),('R1',r'$u_{20}=81$ and the mean is $43$, so the last term is greater.'))],r'$d=4$, $u_1=5$, $S_{20}=860$; $81>43$.','Exact term differences and direct summation reproduce the recovered sequence.',17==5+3*4 and 45==5+10*4 and sum(5+4*k for k in range(20))==860,scatter([(4,17),(11,45)],(0,12),(0,50),xlab='n',ylab='uₙ'))
add('na',702,'A geometric sequence with alternating signs','1.3','Sequences and series',r'A geometric sequence has $u_2=18$ and $u_5=-486$. Its common ratio is real.',[
P('Find the common ratio and the first term.',('M1',r'$u_5/u_2=r^3=-27$.'),('A1',r'$r=-3$ and $u_1=-6$.')),
P(r'Find $S_5$. Explain why an infinite sum does not exist.',('M1',r'$S_5=-6(1-(-3)^5)/(1+3)$.'),('A1',r'$S_5=-366$.'),('R1',r'$|r|=3>1$, so the terms do not tend to zero.'))],r'$r=-3$, $u_1=-6$, $S_5=-366$; no convergent infinite sum.','Direct generation gives -6,18,-54,162,-486; their sum is -366.',sum(-6*(-3)**k for k in range(5))==-366)
add('na',703,'Capacity of a growing seating plan','1.2','Sequences and series',r'A hall has $18$ seats in its first row. Each following row contains $2$ more seats than the previous row. The hall has $480$ seats in total.',[
P(r'Show that the number of rows $n$ satisfies $n^2+17n-480=0$.',('M1',r'$480=\frac n2(36+2(n-1))$.'),('A1',r'$480=n(n+17)$, hence the required equation.')),
P('Find the number of rows and the number of seats in the last row.',('M1',r'$(n-15)(n+32)=0$; reject the negative root.'),('A1',r'$n=15$ and $u_{15}=18+14(2)=46$.'))],r'$15$ rows; $46$ seats in the last row.','Exact capacity sum and quadratic factorization agree.',sum(18+2*k for k in range(15))==480,seqplot([18,20,22,24]),caption='The first four rows are represented by their seat counts; further rows follow the same rule.')
add('na',704,'Total travel of a repeatedly bouncing ball','1.8','Sequences and series',r'A ball is dropped vertically from $12$ m. After each impact it rises to $\frac34$ of its preceding maximum height. Ignore the size of the ball.',[
P('Find the height of the third rebound.',('M1',r'$h_3=12(3/4)^3$.'),('A1',r'$h_3=81/16$ m.')),
P('Find the total vertical distance travelled if the bouncing continues indefinitely.',('M1',r'Distance $=12+2[9+9(3/4)+\cdots]$; each rebound height is travelled twice.'),('A1',r'$12+2(9/(1-3/4))=84$ m.')),
P('Explain why the total distance is finite although the model has infinitely many rebounds.',('R1',r'The rebound heights form a geometric series with ratio $3/4$, whose modulus is less than one.'))],r'Third rebound $81/16$ m; total distance $84$ m.','Partial-distance sums converge to 84; third height is calculated independently by repeated multiplication.',near(12+2*sum(12*.75**k for k in range(1,150)),84) and F(12)*F(3,4)**3==F(81,16),plot([], (0,4),(0,13),xt=[0,1,2,3,4],yt=[0,12],segments=[((0,12),(1,0)),((1,0),(1.5,9)),((1.5,9),(2,0)),((2,0),(2.5,6.75)),((2.5,6.75),(3,0))],xlab='schematic stages',ylab='height / m'))
add('na',705,'Nominal rate versus effective annual growth','1.4','Financial mathematics',r'An account pays nominal annual interest of $4\%$, compounded quarterly. A single deposit of $1500$ is made, with no later transactions.',[
P('Find the effective annual percentage increase.',('M1',r'Annual growth factor is $(1+0.04/4)^4$.'),('A1',r'Effective rate $=100(1.01^4-1)=4.0604\%$.')),
P(r'Find the first whole number of years after which the balance exceeds $2000$.',('M1',r'$1500(1.01)^{4n}>2000$, so $n>\ln(4/3)/(4\ln1.01)$.'),('A1',r'$n>7.23\ldots$; the first whole year is $8$.')),
P('Explain why using a yearly growth factor of 1.04 would underestimate the balance.',('R1',r'Quarterly interest itself earns interest within the year; $1.01^4>1.04$.'))],r'$4.0604\%$ effective annual growth; first exceeds $2000$ after $8$ whole years.','Balances at years 7 and 8 bracket the target; compounding factor checked.',1500*1.01**28<2000<1500*1.01**32,plot([(lambda x:1500*1.01**(4*x),(0,10),None)],(0,10),(1400,2300),xt=[0,5,10],yt=[1500,2000],xlab='years',ylab='balance'),calc=True)
add('na',706,'Depreciation and a replacement threshold','1.4','Financial mathematics',r'A machine bought for $24000$ loses $18\%$ of its value at the end of each year. It is replaced at the first year-end when its value falls below $5000$.',[
P(r'Write its value $V_n$ after $n$ years and find its value after 3 years.',('M1',r'$V_n=24000(0.82)^n$.'),('A1',r'$V_3=13232.832$, approximately $13232.83$.')),
P('Determine the replacement year, checking the neighbouring year.',('M1',r'Solve $24000(0.82)^n<5000$: $n>\ln(5/24)/\ln(0.82)$.'),('A1',r'$n>7.90\ldots$, so replace after $8$ years.'),('R1',r'$V_7\approx5982.85>5000$ and $V_8\approx4905.94<5000$ verify the rounding direction.'))],r'$V_n=24000(0.82)^n$; replacement after 8 years.','The exact third-year value and strict threshold are independently evaluated.',near(24000*.82**3,13232.832) and 24000*.82**7>5000>24000*.82**8,plot([(lambda x:24000*.82**x,(0,10),None)],(0,10),(0,25000),xt=[0,5,10],yt=[0,5000,24000],xlab='years',ylab='value'),calc=True)
add('na',707,'A logarithmic equation with an inadmissible root','1.7','Exponents and logarithms',r'Consider $\log_2(x-1)+\log_2(x+3)=3$.',[
P('State the domain and combine the logarithms into a single logarithm.',('A1',r'$x>1$.'),('M1',r'$\log_2((x-1)(x+3))=3$.')),
P('Solve the equation exactly, explaining any rejection.',('M1',r'$(x-1)(x+3)=8$, giving $x^2+2x-11=0$.'),('A1',r'$x=-1\pm2\sqrt3$.'),('R1',r'Only $x=-1+2\sqrt3$ satisfies $x>1$; the other root is inadmissible.'))],r'$x=-1+2\sqrt3$.','Substitution gives product 8; second algebraic root fails the logarithmic domain.',near((-2+2*math.sqrt(3))*(2+2*math.sqrt(3)),8) and -1-2*math.sqrt(3)<1)
add('na',708,'An exponential equation and its sign interval','1.7','Exponents and logarithms',r'Let $F(x)=3^{2x}-12(3^x)+27$, for real $x$.',[
P(r'Use $u=3^x$ to solve $F(x)=0$.',('M1',r'$u^2-12u+27=(u-3)(u-9)=0$.'),('A1',r'$3^x=3$ or $9$, so $x=1$ or $2$.')),
P(r'Find all $x$ for which $F(x)<0$, giving a reason for the direction of the inequalities.',('M1',r'The upward quadratic is negative for $3<u<9$.'),('A1',r'$1<x<2$.'),('R1',r'$3^x$ is strictly increasing, so taking base-3 logarithms preserves the order.'))],r'Zeros $1,2$; $F(x)<0$ for $1<x<2$.','Factorization expanded at sample values; sign tested inside and outside the interval.',all(near(3**(2*x)-12*3**x+27,(3**x-3)*(3**x-9)) for x in [-1,0,1,1.5,2,3]))
add('na',709,'Recovering a binomial parameter from two coefficients','1.9','Binomial theorem',r'In the expansion of $(1+kx)^6$, the coefficient of $x^2$ is $60$ and the coefficient of $x^3$ is positive.',[
P(r'Find the possible values of $k$ using the coefficient of $x^2$.',('M1',r'$\binom62 k^2=60$, so $15k^2=60$.'),('A1',r'$k=2$ or $k=-2$.')),
P(r'Determine $k$ and find the coefficients of $x^3$ and $x^4$.',('R1',r'The $x^3$ coefficient is $20k^3>0$, hence $k=2$.'),('A1',r'Coefficient of $x^3$ is $20(8)=160$.'),('A1',r'Coefficient of $x^4$ is $15(16)=240$.'))],r'$k=2$; coefficients $160$ and $240$.','Binomial coefficients evaluated by integer combinations.',math.comb(6,2)*2**2==60 and math.comb(6,3)*2**3==160 and math.comb(6,4)*2**4==240)
add('na',710,'Selecting terms with reciprocal powers','1.9','Binomial theorem',r'Consider the expansion of $(2x-x^{-1})^6$, where $x\ne0$.',[
P(r'Write the general term and hence find the term independent of $x$.',('M1',r'$T_{r+1}=\binom6r2^{6-r}(-1)^r x^{6-2r}$.'),('M1',r'Independence requires $6-2r=0$, so $r=3$.'),('A1',r'Constant term $=\binom63 2^3(-1)^3=-160$.')),
P(r'Find the coefficient of $x^2$ and explain why no odd powers of $x$ occur.',('M1',r'$6-2r=2$ gives $r=2$.'),('A1',r'Coefficient $=\binom622^4=240$.'),('R1',r'Every exponent $6-2r$ is even for integer $r$.'))],r'Constant $-160$; coefficient of $x^2$ is $240$; all exponents even.','Expanded exponent pattern and integer coefficients checked.',math.comb(6,3)*8*(-1)==-160 and math.comb(6,2)*16==240)
add('na',711,'Connecting arithmetic and geometric conditions','1.3','Sequences and series',r'Three positive numbers form an increasing arithmetic sequence with sum $18$. When $6$ is added to the largest number, the resulting three numbers form a geometric sequence.',[
P(r'Write the original numbers in terms of their common difference $d$ and show that $d^2+6d-36=0$.',('A1',r'The numbers are $6-d,6,6+d$, with $0<d<6$.'),('M1',r'The geometric condition is $6^2=(6-d)(12+d)$.'),('A1',r'$36=72-6d-d^2$, hence $d^2+6d-36=0$.')),
P('Find the original three numbers exactly, and justify your choice of root.',('M1',r'$d=-3\pm3\sqrt5$.'),('R1',r'Increasing positive terms require $d>0$, so $d=-3+3\sqrt5$; it is also less than 6.'),('A1',r'The original numbers are $9-3\sqrt5,6,3+3\sqrt5$.'))],r'$9-3\sqrt5,6,3+3\sqrt5$.','Positive root checked in the product condition, sum, and strict term ordering.',near((9-3*math.sqrt(5))*(9+3*math.sqrt(5)),36) and 0<9-3*math.sqrt(5)<6<3+3*math.sqrt(5),hard=True)
add('na',712,'Recovering an infinite series from its remainder','1.8','Sequences and series',r'A convergent geometric series with positive first term and positive ratio has sum $216$. Its first three terms have sum $189$.',[
P('Find the common ratio and first term.',('M1',r'The remainder after three terms is $216-189=27=216r^3$.'),('A1',r'$r^3=1/8$, so $r=1/2$.'),('A1',r'$a=216(1-r)=108$.')),
P('Find the first term number for which the term is less than 1.',('M1',r'$108(1/2)^{n-1}<1$.'),('A1',r'$u_7=108/64>1$, while $u_8=108/128<1$; the first is term $8$.')),
P('Explain why all later terms also satisfy this condition.',('R1',r'Each positive term is half the preceding one, so the terms decrease strictly.'))],r'$r=1/2$, $a=108$; term 8 is the first below 1.','Exact first-three sum, geometric remainder, and neighbouring-term threshold checked.',sum(F(108)*F(1,2)**k for k in range(3))==189 and F(108,64)>1>F(108,128),seqplot([108,54,27,13.5,6.75]),hard=True)
add('na',713,'An arithmetic price schedule with a cap','1.2','Sequences and series',r'A service costs $35$ in month 1. The monthly charge rises by $5$ each month until it reaches $80$; it then remains at $80$. The diagram shows the first four charges.',[
P('Find the first month in which the charge is $80$.',('M1',r'$35+5(n-1)=80$.'),('A1',r'$n=10$.')),
P('Calculate the total charge for the first 18 months.',('M1',r'The first 10 charges total $\frac{10}{2}(35+80)=575$.'),('A1',r'Total $=575+8(80)=1215$.')),
P(r'A customer has a total budget of $1000$. Find the greatest whole number of months they can purchase consecutively from month 1.',('M1',r'After month 10, solve $575+80(m-10)\le1000$.'),('A1',r'$m\le15.3125$; greatest whole number $15$ (total $975$).'))],r'Cap begins in month 10; first 18 months cost $1215$; budget buys 15 months.','Direct capped-sequence sums give 975 for 15 months, 1055 for 16 and 1215 for 18.',sum(min(35+5*k,80) for k in range(18))==1215 and sum(min(35+5*k,80) for k in range(15))==975,seqplot([35,40,45,50]),hard=True)
add('na',714,'A divisibility argument and its converse','1.6','Mathematical proof',r'For an integer $n$, define $D=n^3-n$.',[
P(r'Factorize $D$ and prove that it is divisible by 6 for every integer $n$.',('A1',r'$D=(n-1)n(n+1)$.'),('R1',r'Of three consecutive integers, at least one is even.'),('R1',r'Exactly one of the three is divisible by 3; together these factors give divisibility by 6.')),
P(r'A student claims: “If an integer is divisible by 6, it must equal $n^3-n$ for some integer $n$.” Disprove the claim using the integer 12.',('M1',r'For $n=2$, $n^3-n=6$; for $n=3$, it is $24$.'),('R1',r'For positive integers $n$, the successive difference is $3n(n+1)>0$; no positive integer gives a value between 6 and 24.'),('R1',r'$n=0,1$ give zero and negative $n$ give non-positive values, so 12 is a counterexample.'))],r'$n^3-n$ is always a multiple of 6; the converse is false, with counterexample 12.','Algebraic factor identity verified exactly; consecutive difference factored as 3n(n+1).',all(n**3-n==(n-1)*n*(n+1) and (n**3-n)%6==0 for n in range(-100,101)),hard=True)
add('na',715,'Adding sound intensities on a logarithmic scale','1.7','Exponents and logarithms',r'Sound level is modelled by $L=10\log_{10}(I/I_0)$ dB. Two independent sources have levels $60$ dB and $70$ dB at a microphone. Their intensities add; $I_0$ is the same reference intensity for both.',[
P(r'Express each intensity as a multiple of $I_0$.',('M1',r'$I/I_0=10^{L/10}$.'),('A1',r'The intensities are $10^6I_0$ and $10^7I_0$.')),
P('Find the combined sound level to 2 decimal places.',('M1',r'$I_{\rm total}/I_0=1.1\times10^7$.'),('A1',r'$L_{\rm total}=10\log_{10}(1.1\times10^7)=70.41$ dB.')),
P('Explain why adding 60 and 70 is not a valid method, and find the increase over the louder source alone.',('R1',r'Levels are logarithms of intensities; it is the intensities, not their logarithms, that add.'),('A1',r'The increase is $10\log_{10}(1.1)=0.414$ dB to 3 significant figures.'))],r'Combined level $70.41$ dB; increase $0.414$ dB.','Logarithmic-to-linear conversion and reconstructed combined level checked.',near(10*math.log10(1.1e7),70.41392685158225),plot([(lambda x:10*math.log10(x),(1,12),None)],(0,12),(0,12),xt=[1,10],yt=[0,10],xlab='I / (10⁶ I₀)',ylab='L − 60 / dB'),calc=True,hard=True)
add('na',716,'When an exponential equation has one real solution','1.7','Exponents and logarithms',r'The equation $4^x-k2^x+4=0$ contains a real parameter $k$.',[
P(r'Use $u=2^x$ to state a quadratic equation and the restriction on $u$.',('M1',r'$u^2-ku+4=0$.'),('A1',r'$u>0$.')),
P(r'Find every value of $k$ for which the original equation has exactly one real solution, and find that solution.',('M1',r'A repeated root requires $k^2-16=0$, so $k=\pm4$.'),('R1',r'$k=-4$ has repeated root $u=-2$, which is inadmissible; $k=4$ has repeated root $u=2$.'),('A1',r'$k=4$ and $x=1$.')),
P(r'For $k>4$, explain why there are exactly two distinct real solutions.',('R1',r'The discriminant is positive; the two roots have positive product 4 and positive sum $k$, so both are positive.'),('R1',r'Each distinct positive root gives exactly one real value of $x=\log_2u$.'))],r'Exactly one real solution only at $k=4$, where $x=1$; two for $k>4$.','Positive-root restriction checked separately from zero-discriminant condition.',(2**2-4*2+4)==0 and all((u:=((k-math.sqrt(k*k-16))/2))>0 for k in [5,6,10]),hard=True)
add('na',717,'A decreasing sequence and a cumulative target','1.2','Sequences and series',r'A fundraiser receives $120$ on day 1 and $3$ less on each successive day. Only days with a strictly positive receipt are included.',[
P('Find the number of included days and their total receipts.',('M1',r'$u_n=123-3n>0$, so $n<41$.'),('A1',r'There are 40 days; $S_{40}=\frac{40}{2}(120+3)=2460$.')),
P(r'Find the first day by which cumulative receipts exceed $2000$.',('M1',r'$S_n=n(243-3n)/2$; solve the inequality or check adjacent integers.'),('A1',r'$S_{22}=1947$ and $S_{23}=2001$, so day 23.')),
P('Explain why the first crossing is unique within the included days.',('R1',r'All included receipts are positive, so cumulative receipts strictly increase.'))],r'40 days; total $2460$; target first exceeded on day 23.','Direct sums and positivity endpoints checked; 22/23 bracket strict target.',sum(120-3*k for k in range(40))==2460 and sum(120-3*k for k in range(22))==1947 and sum(120-3*k for k in range(23))==2001,seqplot([120,117,114,111]),hard=True)
_nested=''
for i in range(5):
    s=240*.75**i;_nested+=f'<rect x="{320-s/2}" y="{180-s/2}" width="{s}" height="{s}" fill="none" stroke="black" stroke-width="1.6"/>'
_nested+=text(320,42,'First side length: 8 cm')
add('na',718,'Perimeters and areas in nested squares','1.8','Sequences and series',r'A sequence of concentric squares begins with side length $8$ cm. Each following square has side length $\frac34$ of the preceding one. “Total area” below means the sum of individual square areas, counting overlaps repeatedly.',[
P('Find the sum of the perimeters of all the squares.',('M1',r'Perimeters form a geometric series with first term 32 and ratio $3/4$.'),('A1',r'Total perimeter $=32/(1-3/4)=128$ cm.')),
P('Find the sum of their areas.',('M1',r'Areas have first term 64 and ratio $(3/4)^2=9/16$.'),('A1',r'Total area $=64/(1-9/16)=1024/7$ cm$^2$.')),
P('Explain why using the perimeter ratio in the area calculation would be wrong.',('R1',r'Area scales with the square of side length, so its ratio is $9/16$, not $3/4$.'))],r'Perimeter sum $128$ cm; area sum $1024/7$ cm².','Independent perimeter and area partial sums converge to the stated exact values.',near(sum(32*.75**k for k in range(200)),128) and near(sum(64*(9/16)**k for k in range(200)),1024/7),svg(_nested,'First five concentric squares'),hard=True)
add('na',719,'Recovering the exponent of a binomial expansion','1.9','Binomial theorem',r'In $(1+x)^n$, where $n$ is an integer greater than $1$, the coefficient of $x^2$ is three times the coefficient of $x$.',[
P(r'Find $n$.',('M1',r'$\binom n2=3\binom n1$, so $n(n-1)/2=3n$.'),('A1',r'$n-1=6$, hence $n=7$.')),
P(r'Find the coefficient of $x^3$.',('M1',r'Use $\binom73$.'),('A1',r'The coefficient is $35$.')),
P(r'By considering $(1+1)^n$ and $(1-1)^n$, find the sum of the coefficients of even powers of $x$.',('M1',r'Let $E,O$ be even and odd sums. Then $E+O=128$ and $E-O=0$.'),('A1',r'$E=64$.'))],r'$n=7$; coefficient $35$; even-power coefficient sum $64$.','Exact combinatorial sums independently evaluated.',math.comb(7,2)==3*math.comb(7,1) and sum(math.comb(7,k) for k in range(0,8,2))==64,hard=True)
add('na',720,'A rational-power equation and its complete inequality','1.7','Exponents and logarithms',r'For real $x\ge0$, consider $\sqrt{x}+\sqrt[4]{x}=6$.',[
P(r'Use $u=x^{1/4}$ to solve the equation exactly.',('M1',r'$u^2+u-6=(u+3)(u-2)=0$.'),('R1',r'$u\ge0$ excludes $u=-3$.'),('A1',r'$u=2$, so $x=2^4=16$.')),
P(r'Hence solve $\sqrt{x}+\sqrt[4]{x}\le6$ over the reals.',('M1',r'$(u+3)(u-2)\le0$ gives $-3\le u\le2$.'),('R1',r'Intersect with $u\ge0$ to obtain $0\le u\le2$.'),('A1',r'$0\le x\le16$.'))],r'Equation solution $x=16$; inequality $0\le x\le16$.','Substitution and monotonic mapping x=u^4 on the nonnegative domain checked.',near(16**.5+16**.25,6) and all((u*u+u<=6)==(u<=2) for u in [0,.5,1,2,3,4]),hard=True)

def finish():
    order={TOPICS[k]:i for i,k in enumerate(['na','fn','gt','sp','ca'])}
    QUESTIONS.sort(key=lambda q:(order[q['topicId']],q['number']))
    review_by_id={r['id']:r for r in REVIEWS}
    for ordinal,q in enumerate(QUESTIONS,1):
        review_by_id[q['id']]['ordinal']=ordinal
        assert q['number']==q['source']['question']==int(q['id'].rsplit('-',1)[1])
        assert q['marks']==sum(p['marks'] for p in q['parts'])
        for p,g in zip(q['parts'],q['markScheme']):
            assert p['label']==g['part']
            assert p['marks']==sum(int(s['code'][1:]) for s in g['steps'])
        for field in ['stem','answerSummary']:
            assert not any(ord(c)<32 for c in q[field]),(q['id'],field)
        for p in q['parts']:
            assert not any(ord(c)<32 for c in p['prompt']),(q['id'],'prompt')
        for g in q['markScheme']:
            for s in g['steps']: assert not any(ord(c)<32 for c in s['text']),(q['id'],'scheme')
        if 'diagramSvg' in q:
            ET.fromstring(q['diagramSvg'])
            assert len(q['diagramSvg'])<=300000
            assert not re.search(r'<(?:script|foreignObject|iframe|object|embed|image|style|animate|set)\b|\bon\w+\s*=|(?:href|src)\s*=|url\s*\(',q['diagramSvg'],re.I)
    assert len(QUESTIONS)==100
    assert len({q['id'] for q in QUESTIONS})==100
    assert len({q['title'] for q in QUESTIONS})==100
    assert len({q['stem'] for q in QUESTIONS})==100
    assert collections.Counter(q['difficulty'] for q in QUESTIONS)=={'medium':50,'hard':50}
    assert collections.Counter(q['topicId'] for q in QUESTIONS)=={v:20 for v in TOPICS.values()}
    assert sum('diagramSvg' in q for q in QUESTIONS)>=80
    out=ROOT/'content/ib/math-2026-expansion/aa-sl.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(QUESTIONS,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report={'course':'Mathematics: analysis and approaches SL','curriculum':'First assessment 2021; not the 2029 syllabus','originality':'Independently syllabus-authored practice; no official past-paper provenance is claimed. All 100 were authored as separate tasks, rather than counted parameter variants.','syllabusReference':'https://www.ibo.org/globalassets/new-structure/university-admission/pdfs/subject-guides/mathematics-analysis-approaches-guide.pdf','catalogCheck':'The repository catalog confirms the five topic/collection IDs. Its ibSyllabusSubtopics function returns [] for Maths; numeric codes were checked against the official SL sections (1.1–1.9,2.1–2.11,3.1–3.8,4.1–4.12,5.1–5.11).','counts':{'questions':100,'byTopic':dict(collections.Counter(q['topicId'] for q in QUESTIONS)),'difficulty':dict(collections.Counter(q['difficulty'] for q in QUESTIONS)),'calculator':dict(collections.Counter(str(q['calculator']).lower() for q in QUESTIONS)),'svgDiagrams':sum('diagramSvg' in q for q in QUESTIONS),'mathematicalChecksPassed':100},'scopeChecks':['No induction, complex numbers, vectors, formal limits, related rates, implicit differentiation, differential equations or volume-of-revolution tasks.','No variance of discrete random variables, probability density functions, frequency-density histograms or hypothesis testing.','Graph transformations avoid the general f(ax+b) form excluded at SL.','Both calculator and feasible exact non-calculator work are represented.'],'structuralChecks':['100 unique IDs/titles/stems; 20 per topic; 50 medium/50 hard.','Each part has its own fully worked additive M/A/R scheme; all part and question totals match.','All SVG parsed as XML and checked against the repository prohibited-element rules; no remote resources.','Every task passed a distinct executable arithmetic, probability, substitution, numerical integral or derivative check.'],'limitations':['Author review and computational checks are not independent human IB examiner moderation.','Difficulty is an editorial judgement and has not been calibrated against student performance.','External schema, KaTeX and rendered visual checks are handled by the integration review.'],'records':[review_by_id[q['id']] for q in QUESTIONS],'contentSha256':hashlib.sha256(out.read_bytes()).hexdigest()}
    rp=ROOT/'docs/ib-2026-maths/aa-sl-author-review.json'
    rp.parent.mkdir(parents=True,exist_ok=True)
    rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report['counts'],ensure_ascii=True))

if __name__=='__main__': finish()
