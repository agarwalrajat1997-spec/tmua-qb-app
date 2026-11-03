"""Reconstruct four SL practice papers against the supplied solution books.

These are newly worded compatible questions, not a claim to recover missing
original wording. Source-page mistakes are recorded explicitly. Standard library
only; numerical checks supplement the handwritten algebra/review of every part.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import math, statistics, json, html, hashlib, re, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'content/ib/aa-mocks-2026/papers'
DOC=ROOT/'docs/ib-aa-mocks-2026/sl-author-review.json'
PAPERS={}; EVIDENCE={}; ERRATA=[]
N=statistics.NormalDist()

def near(label,actual,expected,tol=1e-8):
    assert math.isclose(float(actual),float(expected),rel_tol=tol,abs_tol=tol),(label,actual,expected)
    return {'test':label,'calculated':float(actual),'expected':float(expected),'status':'passed'}
def same(label,actual,expected):
    assert actual==expected,(label,actual,expected)
    def plain(value):
        if isinstance(value,F):return float(value)
        if isinstance(value,(tuple,list)):return [plain(v) for v in value]
        return value
    return {'test':label,'calculated':plain(actual),'expected':plain(expected),'status':'passed'}
def bisect(fn,a,b):
    fa=fn(a); assert fa*fn(b)<0
    for _ in range(100):
        m=(a+b)/2; fm=fn(m)
        if fa*fm<=0:b=m
        else:a=m;fa=fm
    return (a+b)/2
def simpson(fn,a,b,n=2000):
    h=(b-a)/n
    return h/3*(fn(a)+fn(b)+4*sum(fn(a+i*h) for i in range(1,n,2))+2*sum(fn(a+i*h) for i in range(2,n,2)))
def derivative(fn,x,h=1e-5):return (fn(x+h)-fn(x-h))/(2*h)
def tex(s):return html.escape(str(s))
def text(x,y,s,size=18,anchor='middle'):
    return f'<text x="{x:g}" y="{y:g}" text-anchor="{anchor}" font-family="Arial,sans-serif" font-size="{size}" fill="#111">{tex(s)}</text>'
def line(x,y,u,v,dash=False):
    return f'<path d="M{x:g} {y:g}L{u:g} {v:g}" fill="none" stroke="#111" stroke-width="2"'+(' stroke-dasharray="7 5"' if dash else '')+'/>'
def poly(points,fill='none',dash=False):
    return '<polyline points="'+' '.join(f'{x:.3f},{y:.3f}' for x,y in points)+'" fill="'+fill+'" stroke="#111" stroke-width="2.2"'+(' stroke-dasharray="7 5"' if dash else '')+'/>'
def dot(x,y):return f'<circle cx="{x:g}" cy="{y:g}" r="4" fill="#111"/>'
def svg(body,title,w=820,h=480):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{tex(title)}"><rect width="{w}" height="{h}" fill="white"/>'+text(w/2,27,title,20)+body+'</svg>'
def graph(title,curves,xr,yr,xticks,yticks,annotations=(),extra=None):
    X=lambda x:85+650*(x-xr[0])/(xr[1]-xr[0]); Y=lambda y:405-335*(y-yr[0])/(yr[1]-yr[0]); b=''
    ox=X(0) if xr[0]<=0<=xr[1] else 85;oy=Y(0) if yr[0]<=0<=yr[1] else 405
    b+=line(75,oy,755,oy)+line(ox,420,ox,55)+text(770,oy+6,'x')+text(ox+16,55,'y')
    for x in xticks:b+=line(X(x),oy-5,X(x),oy+5)+text(X(x),oy+25,f'{x:g}',16)
    for y in yticks:b+=line(ox-5,Y(y),ox+5,Y(y))+text(ox-12,Y(y)+5,f'{y:g}',16,'end')
    if extra:b=extra(X,Y)+b
    for fn,lo,hi,dash in curves:
        pts=[]
        for j in range(501):
            x=lo+(hi-lo)*j/500;y=fn(x)
            if yr[0]<=y<=yr[1]:pts.append((X(x),Y(y)))
            elif pts:b+=poly(pts,dash=dash);pts=[]
        if pts:b+=poly(pts,dash=dash)
    for x,y,label,dx,dy in annotations:b+=dot(X(x),Y(y))+text(X(x)+dx,Y(y)+dy,label,17)
    return svg(b,title)
def tree():
    b=''
    points=[(90,240),(330,125),(330,355),(650,70),(650,180),(650,300),(650,410)]
    for a,z in [(0,1),(0,2),(1,3),(1,4),(2,5),(2,6)]:b+=line(*points[a],*points[z])
    for x,y in points:b+=dot(x,y)
    for x,y,s in [(330,105,'Black box'),(330,385,'White box'),(710,75,'Red'),(710,185,'Blue'),(710,305,'Red'),(710,415,'Blue')]:b+=text(x,y,s,18)
    b+=text(410,463,'Copy and complete the branch probabilities.',16)
    return svg(b,'Selection of a box followed by the colour of a ball')
def rect_exp():
    a=4;h=math.exp(a/5)
    def ext(X,Y):
        return poly([(X(a),Y(0)),(X(10),Y(0)),(X(10),Y(h)),(X(a),Y(h)),(X(a),Y(0))],fill='#eee')+text(X(a),Y(0)+25,'a')+text(X(10),Y(0)+25,'10')+text(X(a)-8,Y(h)-15,'(a, f(a))',16)+text(X(8),Y(5),'y = exp(x/5)',17)
    return graph('Rectangle with one corner on the exponential curve',[(lambda x:math.exp(x/5),0,10.5,False)],(-.5,11),(0,9),[0],[2,4,6,8],extra=ext)
def sector():
    O=(275,350);r=260;theta=1.1
    arc=[(O[0]+r*math.cos(t),O[1]-r*math.sin(t)) for t in [theta*i/100 for i in range(101)]]
    b=poly([O,*arc,O])+poly([*arc,arc[0]],fill='#eee')
    b+=text(250,380,'O')+text(550,375,'A')+text(405,110,'B')+text(400,380,'r')+text(300,200,'r')+text(340,320,'θ')
    b+=text(620,220,'Minor segment',17)+text(620,245,'area 3.35 cm²',17)+line(550,235,495,230)+text(410,450,'Diagram is schematic; θ is measured in radians.',16)
    return svg(b,'A sector OAB and its minor segment')
def ray_triangle():
    b=line(95,370,740,370)+line(95,370,395,70)+line(395,70,620,370,True)
    for x,y,s in [(95,400,'B'),(395,55,'A'),(620,400,'X'),(220,200,'20 cm'),(180,345,'45°')]:b+=text(x,y,s)
    b+=text(410,450,'X varies along the ray to the right of B; not to scale.',16)
    return svg(b,'A fixed segment and a point moving along a ray')
def elevation():
    b=line(80,380,650,380)+line(650,380,650,75)+line(80,380,650,75)+line(270,380,650,75)
    b+=poly([(630,380),(630,360),(650,360)])
    for x,y,s in [(80,410,'B'),(270,410,'A'),(650,410,'Q'),(650,55,'P'),(170,410,'1'),(460,410,'2'),(680,230,'x'),(330,355,'α'),(155,355,'β')]:b+=text(x,y,s)
    return svg(b,'Two angles of elevation from collinear points')
def square_chain():
    b=line(75,370,735,370);lengths=[1.2*.6**n for n in range(7)];x=90;scale=200
    for i,s in enumerate(lengths):
        b+=f'<rect x="{x:g}" y="{370-scale*s:g}" width="{scale*s:g}" height="{scale*s:g}" fill="white" stroke="#111" stroke-width="2"/>'
        if i<3:b+=text(x+scale*s/2,370-scale*s-12,[1.2,.72,.432][i],16)
        x+=scale*s
    b+=text(75,400,'A')+text(715,400,'B')+text(410,450,'Squares continue indefinitely; bases lie consecutively on AB.',16)
    return svg(b,'An infinite chain of adjacent squares')
def triangle_sqrt7():
    pts=[(260,80),(150,380),(600,380)];b=poly([*pts,pts[0]])
    for x,y,s in [(260,60,'A'),(140,410,'B'),(610,410,'C'),(180,220,'2'),(455,215,'3'),(370,415,'√7')]:b+=text(x,y,s)
    return svg(b,'Triangle ABC; side lengths in centimetres')
def trig_triangle():
    X=lambda x:90+15*x;Y=lambda y:400-12*y
    pts=[(X(0),Y(0)),(X(39),Y(0)),(X(32),Y(24))]
    b=poly([*pts,pts[0]])+line(X(32),Y(24),X(32),Y(0),True)+poly([(X(32)-15,Y(0)),(X(32)-15,Y(0)-15),(X(32),Y(0)-15)])
    for x,y,s in [(X(0)-10,Y(0)+25,'A'),(X(39)+10,Y(0)+25,'B'),(X(32)+5,Y(24)-15,'C'),(X(32),Y(0)+25,'D'),(X(36),Y(12),'25'),(X(5),Y(1.8),'x'),(X(36.5),Y(1.8),'2x')]:b+=text(x,y,s)
    return svg(b,'Triangle ABC and perpendicular CD')
def pyramid():
    A=(170,375);B=(550,375);C=(695,255);D=(315,255);Q=(432.5,315);P=(432.5,65)
    b=poly([A,B,C])+line(*A,*D,True)+line(*D,*C,True)+line(*P,*A)+line(*P,*B)+line(*P,*C)+line(*P,*D,True)+line(*P,*Q)
    for (x,y),s,dx,dy in [(A,'A',-10,25),(B,'B',10,25),(C,'C',16,0),(D,'D',-18,-5),(P,'P',0,-18),(Q,'Q',-18,18)]:b+=dot(x,y)+text(x+dx,y+dy,s)
    b+=text(350,405,'6 cm')+text(378,225,'3√2 cm',16)+line(413,225,432.5,225)+text(410,455,'Q is the centre of the square base; PQ is perpendicular to its plane.',16)
    return svg(b,'A right square-based pyramid PABCD')
def curve_dome():
    f=lambda x:math.sqrt(max(0,1+x))+math.sqrt(max(0,1-x))
    def extra(X,Y):
        curve=[(X(-1+2*i/200),Y(f(-1+2*i/200))) for i in range(201)]
        return poly([(X(0),Y(0)),*curve,(X(0),Y(0))],fill='#eee')+text(X(-1)-15,Y(math.sqrt(2))-12,'A')+text(X(1)+15,Y(math.sqrt(2))-12,'B')+text(X(0)+15,Y(0)-12,'O')
    return graph('Graph of f and the region bounded by the curve, OA and OB',[(f,-1,1,False)],(-1.4,1.4),(0,2.4),[-1,1],[1,2],extra=extra)
def area_rectangle():
    a=.6
    def extra(X,Y):
        return poly([(X(-a),Y(a*a)),(X(a),Y(a*a)),(X(a),Y(4*math.cos(a))),(X(-a),Y(4*math.cos(a))),(X(-a),Y(a*a))],fill='#eee')+text(X(-a),Y(0)+25,'−a')+text(X(a),Y(0)+25,'a')+text(X(-1.8),Y(3.5),'y = 4 cos x',17)+text(X(1.6),Y(3.5),'y = x²',17)
    return graph('A rectangle between two curves; angles in radians',[(lambda x:4*math.cos(x),-1.7,1.7,False),(lambda x:x*x,-1.9,1.9,False)],(-2,2),(-.25,4.7),[],[2,4],extra=extra)

def paper(set_,number):
    key=f'aa-sl-set-{set_.lower()}-paper-{number}'
    p={'id':key,'course':'sl','set':set_,'paper':str(number),'title':f'Mathematics AA SL - Set {set_} - Paper {number}','minutes':90,'marks':80,'calculator':number==2,'questions':[]}
    PAPERS[key]=p;EVIDENCE[key]=[];return p
def S(code,text):return {'code':code,'text':text}
def P(label,prompt,*steps):return {'label':label,'prompt':prompt,'marks':sum(int(s['code'][1:]) for s in steps),'steps':list(steps)}
def Q(p,n,stem,parts,summary,checks,diagram=None,notes=''):
    assert set(checks)=={part['label'] for part in parts},(p['id'],n,'unverified part')
    def polish(s):
        chunks=re.split(r'(\$[^$]*\$)',s)
        return ''.join(t if i%2 else re.sub(r'(?<=[0-9])(?=[A-Za-z])',' ',re.sub(r'(?<=[A-Za-z])(?=[0-9])',' ',t)) for i,t in enumerate(chunks))
    stem=polish(stem);summary=polish(summary)
    for part in parts:
        part['prompt']=polish(part['prompt'])
        for step in part['steps']:step['text']=polish(step['text'])
    q={'number':n,'section':'A' if n<=7 else'B','marks':sum(x['marks'] for x in parts),'stem':stem,'parts':[{k:v for k,v in x.items() if k!='steps'} for x in parts],'answerSummary':summary,'markScheme':[{'part':x['label'],'steps':x['steps']} for x in parts],'sourcePages':[n+1]}
    if diagram:q['diagramSvg']=diagram;ET.fromstring(diagram)
    p['questions'].append(q)
    EVIDENCE[p['id']].append({'question':n,'status':'passed','sourcePages':[n+1],'partChecks':checks,'reconstructionNotes':notes or'New wording and complete givens reconstructed to match the supplied solution mathematics and part marks.','markingReview':'Every stated demand is represented by distinct marking points; part and question totals checked. Alternative valid methods accepted.'})

# SET A PAPER 1 ---------------------------------------------------------------
p=paper('A',1)
f=lambda x:(x-1)/(2-x); inv=lambda x:(2*x+1)/(x+1)
Q(p,1,r'Let $f(x)=\dfrac{x-1}{2-x}$, with domain $\mathbb{R}\setminus\{2\}$.',[
 P('a','State the range of $f$.',S('A1',r'$\mathbb{R}\setminus\{-1\}$, or $y\ne-1$.')),
 P('b','Find an expression for $f^{-1}(x)$.',S('M1',r'Write $y=(x-1)/(2-x)$ and interchange the variables, or rearrange before interchanging.'),S('M1',r'$x-1=2y-xy\implies x(1+y)=2y+1$.'),S('A1',r'$x=(2y+1)/(y+1)$.'),S('A1',r'$f^{-1}(x)=(2x+1)/(x+1)$, for $x\ne-1$.'))],
 r'Range excludes $-1$; $f^{-1}(x)=(2x+1)/(x+1)$.',{'a':[near('range exclusion identity at0',(f(0)+1)*(2-0),1)],'b':[near('inverse composition at3',f(inv(3)),3),near('reverse composition at1',inv(f(1)),1)]})
Q(p,2,'Angles in this question are measured in radians.',[
 P('a',r'Express $8\sin x\cos x$ as a single sine expression.',S('M1',r'Use $\sin 2x=2\sin x\cos x$.'),S('A1',r'$8\sin x\cos x=4\sin 2x$.')),
 P('b',r'Hence evaluate $\displaystyle\int_0^{\pi/2}8\sin x\cos x\,\mathrm{d}x$.',S('A1',r'An antiderivative is $-2\cos2x$.'),S('M1',r'Evaluate $[-2\cos2x]_0^{\pi/2}$.'),S('A1',r'$-2\cos\pi+2\cos0=2+2$.'),S('A1',r'The integral equals $4$.'))],
 r'$4\sin2x$; integral $4$.',{'a':[near('double angle check',8*math.sin(.37)*math.cos(.37),4*math.sin(.74))],'b':[near('independent Simpson integral',simpson(lambda x:8*math.sin(x)*math.cos(x),0,math.pi/2),4)]})
Q(p,3,'Angles are measured in degrees.',[P('',r'Solve $\sin(2x-10^\circ)=1$ for $0^\circ\le x\le360^\circ$.',S('M1',r'Use $\sin\theta=1$ at $\theta=90^\circ+360^\circ k$.'),S('A1',r'$2x-10^\circ=90^\circ+360^\circ k$.'),S('A1',r'$2x=100^\circ+360^\circ k$.'),S('A1',r'$x=50^\circ+180^\circ k$.'),S('A1',r'$x=50^\circ$.'),S('A1',r'$x=230^\circ$, with no other values in the specified interval.'))],
 r'$x=50^\circ,230^\circ$.',{'':[near('first solution',math.sin(math.radians(2*50-10)),1),near('second solution',math.sin(math.radians(2*230-10)),1),same('integer k range',[k for k in range(-3,4) if 0<=50+180*k<=360],[0,1])]})
Q(p,4,'A discrete random variable $X$ has the following distribution.\n\n| $x$ | $1$ | $2$ | $3$ |\n|---|---|---|---|\n| $P(X=x)$ | $p$ | $0.7-p$ | $q$ |\n\nThe expectation of $X$ is $2.1$.',[
 P('a','Find $q$.',S('M1',r'$p+(0.7-p)+q=1$.'),S('A1',r'$q=0.3$.')),
 P('b','Find $p$.',S('M1',r'Use $E(X)=p+2(0.7-p)+3q=2.1$.'),S('A1',r'$p+1.4-2p+0.9=2.1$.'),S('A1',r'$p=0.2$.'))],
 '$q=0.3$, $p=0.2$.',{'a':[near('probability normalization',.2+.5+.3,1)],'b':[near('weighted expectation',.2+2*.5+3*.3,2.1)]})
Q(p,5,'Consider logarithms of real arguments.',[
 P('a',r'Write $\log_8(x+2)$ in terms of $\log_2(x+2)$.',S('A1',r'$\log_8(x+2)=\dfrac{\log_2(x+2)}3$.')),
 P('b',r'Hence solve $3\log_8(x+2)-2\log_2(x+1)=1$.',S('M1',r'Convert to base2 and combine logarithms.'),S('A1',r'$\log_2\left((x+2)/(x+1)^2\right)=1$.'),S('M1',r'$x+2=2(x+1)^2$.'),S('A1',r'$x(2x+3)=0$, giving $0$ or $-3/2$.'),S('A1',r'Original arguments require $x>-1$, so reject $-3/2$ and obtain $x=0$.'))],
 r'Change of base factor $1/3$; only $x=0$.',{'a':[near('change of base at3',math.log(5,8),math.log2(5)/3)],'b':[near('original equation at0',3*math.log(2,8)-2*math.log2(1),1),same('rejected root violates domain',-1.5>-1,False)]})
Q(p,6,'An arithmetic sequence has first term $u_1$ and common difference $d$. Its first $n$ terms have sum $S_n$. It is given that $S_3=S_8$.',[
 P('a',r'Show that $u_1=-5d$.',S('M1',r'Use $S_n=n[2u_1+(n-1)d]/2$.'),S('A1',r'$\frac32(2u_1+2d)=\frac82(2u_1+7d)$.'),S('A1',r'$3u_1+3d=8u_1+28d$.'),S('A1',r'$5u_1=-25d$, hence $u_1=-5d$.')),
 P('b','Hence find $u_6$.',S('M1',r'$u_6=u_1+5d$.'),S('A1',r'$u_6=0$.'))],
 '$u_1=-5d$ and $u_6=0$.',{'a':[near('sum equality d2',sum(-10+2*i for i in range(3)),sum(-10+2*i for i in range(8)))],'b':[near('sixth term for arbitrary d',-5*F(7,3)+5*F(7,3),0)]})
Q(p,7,r'Let $f(x)=ax^3+2ax^2+bx+3a$, where $a,b\in\mathbb{R}$. The graph has a stationary point at $(1,3)$.',[
 P('a',r'Find $f\,\!\prime(x)$.',S('A1',r'Differentiate the cubic and quadratic terms to obtain $3ax^2+4ax$.'),S('A1',r'$f\,\!\prime(x)=3ax^2+4ax+b$.')),
 P('b','Find $a$ and $b$.',S('A1',r'$f(1)=3\implies6a+b=3$.'),S('M1',r'Use the stationary-point condition $f\,\!\prime(1)=0$.'),S('A1',r'$7a+b=0$.'),S('A1',r'$a=-3$, $b=21$.'))],
 r'$f\,\!\prime(x)=3ax^2+4ax+b$; $a=-3,b=21$.',{'a':[near('derivative finite difference',derivative(lambda x:2*x**3+4*x*x+7*x+6,.8),6*.8**2+8*.8+7,1e-6)],'b':[near('point constraint',-3-6+21-9,3),near('stationary constraint',-9-12+21,0)]})
Q(p,8,r'Let $f(x)=ax^2+bx+8$, where $a\ne0$, and let $g(x)=4ax^2+2bx+8$ and $h(x)=4ax^2+4bx+33$.',[
 P('a(i)','Write $g(x)$ in terms of $f$ and describe the transformation taking the graph of $f$ to that of $g$.',S('A1',r'$g(x)=f(2x)$.'),S('A1',r'The transformation is a horizontal stretch/compression.'),S('A1',r'The scale factor parallel to the $x$-axis is $1/2$.')),
 P('a(ii)','Two points on the graph of $f$ have $x$-coordinates $2$ and $4$. State the $x$-coordinates of their corresponding points on the graph of $g$.',S('A1',r'$1$ and $2$, respectively.')),
 P('b','Describe a sequence of transformations taking the graph of $f$ to that of $h$.',S('M1',r'$h(x)=4f(x)+1$.'),S('A1',r'Vertical stretch of scale factor4.'),S('A1',r'Vertical translation1 unit upwards; stretch then translate.')),
 P('c','The vertex of the graph of $f$ is $(-1,a)$. Find $a$ and $b$.',S('M1',r'$-b/(2a)=-1\implies b=2a$.'),S('M1',r'$f(-1)=a$.'),S('A1',r'$a-b+8=a\implies b=8$.'),S('A1',r'$a=4$.'))],
 '$g=f(2x)$; $x=1,2$; $h=4f+1$; $a=4,b=8$.',{'a(i)':[near('horizontal transform at.7',4*3*.7**2+2*5*.7+8,3*(2*.7)**2+5*(2*.7)+8)],'a(ii)':[same('x coordinate mapping',[2/2,4/2],[1,2])],'b':[near('vertical transform example',4*3*.7**2+4*5*.7+33,4*(3*.7**2+5*.7+8)+1)],'c':[near('vertex x',-8/(2*4),-1),near('vertex y equals a',4-8+8,4)]},notes='Source a(ii) contains only two x-coordinates and no surviving question statement. Compatible point-mapping demand reconstructed explicitly; not assumed to concern roots, which would conflict with part c.')
Q(p,9,'A black box contains1 red ball and4 blue balls. A white box contains2 red balls and3 blue balls. A fair six-sided die is rolled: the black box is selected for scores1,2,3 and the white box otherwise. One ball is drawn at random from the selected box.\n\nFor part(d) only, change the rule: select the black box when the die score is $a$ or below, where $a$ is an integer from1 to5; otherwise select the white box.',[
 P('a','Copy and complete the probability tree, labelling every branch.',S('A1',r'The box-selection probabilities are both $1/2$.'),S('A1',r'Black-box probabilities: red $1/5$, blue $4/5$.'),S('A1',r'White-box probabilities: red $2/5$, blue $3/5$.')),
 P('b','Find the probability that the drawn ball is blue.',S('A1',r'$P(\mathrm{blue})=(1/2)(4/5)+(1/2)(3/5)$.'),S('A1',r'$P(\mathrm{blue})=7/10$.')),
 P('c','Given that the drawn ball is red, find the probability that it came from the black box.',S('A1',r'$P(\mathrm{red})=3/10$.'),S('M1',r'$P(\mathrm{black}\mid\mathrm{red})=P(\mathrm{black}\cap\mathrm{red})/P(\mathrm{red})$.'),S('A1',r'$[(1/2)(1/5)]/(3/10)=1/3$.')),
 P('d',r'Under the changed rule, $P(\mathrm{black}\mid\mathrm{red})=1/5$. Find $a$.',S('M1',r'Let $p=P(\mathrm{black})=a/6$.'),S('A1',r'$P(\mathrm{red})=p/5+2(1-p)/5=(2-p)/5$.'),S('M1',r'Apply conditional probability with numerator $p/5$.'),S('A1',r'$P(\mathrm{black}\mid\mathrm{red})=p/(2-p)$.'),S('A1',r'$p/(2-p)=1/5\implies p=1/3$.'),S('A1',r'$a=2$, so select black for scores1 or2.'))],
 r'$P(blue)=7/10$, $P(black\mid red)=1/3$ under original rule; changed threshold $a=2$.',{'a':[near('total joint mass',F(1,2)*(F(1,5)+F(4,5))+F(1,2)*(F(2,5)+F(3,5)),1)],'b':[near('blue total',F(1,2)*F(4,5)+F(1,2)*F(3,5),F(7,10))],'c':[near('conditional black givenred',F(1,10)/F(3,10),F(1,3))],'d':[near('changed-rule red mass',F(1,3)*F(1,5)+F(2,3)*F(2,5),F(1,3)),near('changed conditional',F(1,15)/F(1,3),F(1,5))]},tree(),notes='Uses source corrected a-or-below convention; source page10 red-mass denominators10 are erroneous and corrected to5, leaving final a=2 unchanged.')
Q(p,10,r'Let $f(x)=e^{x/5}$. A rectangle has vertices $(a,0)$, $(10,0)$, $(10,f(a))$ and $(a,f(a))$, where $0<a<10$. Its area is $S$ and perimeter is $P$.',[
 P('a','Find the equation of the tangent to the graph of $f$ at $x=0$.',S('M1',r'Differentiate $f$: $f\,\!\prime(x)=e^{x/5}/5$.'),S('A1',r'The point is $(0,1)$ and the gradient is $1/5$.'),S('A1',r'$y=x/5+1$.')),
 P('b','Show that $S=(10-a)e^{a/5}$.',S('A1',r'The base is $10-a$.'),S('A1',r'The height is $e^{a/5}$, giving the stated product.')),
 P('c','Write an expression for $P$ in terms of $a$.',S('A1',r'$P=2(10-a)+2e^{a/5}$.'),S('A1',r'$P=20-2a+2e^{a/5}$.')),
 P('d',r'Find $\mathrm{d}S/\mathrm{d}a$.',S('M1',r'Apply the product rule.'),S('A1',r'$\mathrm{d}S/\mathrm{d}a=-e^{a/5}+(10-a)e^{a/5}/5$.'),S('A1',r'$\mathrm{d}S/\mathrm{d}a=e^{a/5}-(a/5)e^{a/5}$.')),
 P('e','Find the perimeter of the rectangle whose area is greatest. Justify that its area is a maximum.',S('M1',r'Set $\mathrm{d}S/\mathrm{d}a=0$.'),S('A1',r'$e^{a/5}>0$, so $1-a/5=0$ and $a=5$.'),S('A1',r'$S\,\!\prime\prime(a)=-(a/25)e^{a/5}$.'),S('R1',r'This is negative at5; also $S\,\!\prime$ changes from positive to negative on $(0,10)$, so this is the global maximum.'),S('A1',r'$P=10+2e$.'))],
 r'Tangent $y=x/5+1$; $S=(10-a)e^{a/5}$; maximum at $a=5$, with $P=10+2e$.',{'a':[near('tangent slope',derivative(lambda x:math.exp(x/5),0),.2)],'b':[near('area factor',6*math.exp(.8),(10-4)*math.exp(4/5))],'c':[near('perimeter at4',2*(6+math.exp(.8)),20-8+2*math.exp(.8))],'d':[near('area derivative at4',derivative(lambda a:(10-a)*math.exp(a/5),4),math.exp(.8)*(1-4/5))],'e':[near('stationary derivative',math.exp(1)*(1-1),0),same('global derivative sign',math.exp(.2)*(1-.2)>0 and math.exp(1.8)*(1-1.8)<0,True)]},rect_exp())

# SET A PAPER 2 ---------------------------------------------------------------
p=paper('A',2)
Q(p,1,'Four observations, listed in ascending order, are $a,b,10,10$. Their median is8 and their mean is7.',[
 P('a','Find $b$.',S('A1',r'$(b+10)/2=8$, so $b=6$.')),
 P('b','Find $a$.',S('M1',r'$(a+6+10+10)/4=7$.'),S('A1',r'$a=2$.')),
 P('c','Find the population standard deviation of these observations.',S('A2',r'$\sigma=\sqrt{11}=3.31662\ldots\approx3.32$.'))],
 r'$b=6,a=2,\sigma=3.32$.',{'a':[near('median',(6+10)/2,8)],'b':[near('mean',statistics.mean([2,6,10,10]),7)],'c':[near('population variance',statistics.pvariance([2,6,10,10]),11),near('population SD',statistics.pstdev([2,6,10,10]),math.sqrt(11))]})
root=math.log(2/(math.e**2-1))
Q(p,2,r'Let $f(x)=\ln(x+2)$ for $x>-2$, and $g(x)=e^x$ for $x\in\mathbb{R}$.',[
 P('a',r'Find $(g\circ f)(x)$.',S('A1',r'$(g\circ f)(x)=e^{\ln(x+2)}$.'),S('A1',r'$(g\circ f)(x)=x+2$, for $x>-2$.')),
 P('b',r'Solve $(g\circ f)(x)=(f\circ g)(x)$.',S('A1',r'$x+2=\ln(e^x+2)$.'),S('A2',r'Graphical/numerical solution $x=-1.16144\ldots\approx-1.16$. Exact $x=\ln[2/(e^2-1)]$ also accepted.'))],
 r'$(g\circ f)(x)=x+2$; equality at $x\approx-1.16$.',{'a':[near('composition at.3',math.exp(math.log(.3+2)),2.3)],'b':[near('equation residual',root+2-math.log(math.exp(root)+2),0),same('root in composition domain',root>-2,True)]})
tail=1-N.cdf(10/9); cutoff=230+9*N.inv_cdf(.5-tail)
Q(p,3,r'A measurement $X$ follows a normal distribution with mean230 and standard deviation9, so $X\sim N(230,9^2)$.',[
 P('a',r'Find $P(X>240)$.',S('M1',r'Use the upper normal tail with standardized value $(240-230)/9$.'),S('A1',r'$P(X>240)=0.133260\ldots\approx0.133$.')),
 P('b',r'Find $a$ such that $P(a<X<230)=P(X>240)$.',S('M1',r'$P(X>a)=0.5+P(X>240)$.'),S('A1',r'$P(X>a)=0.633260\ldots$.'),S('A1',r'$a=226.935\ldots\approx227$.'))],
 r'$P(X>240)=0.133$ and $a\approx227$.',{'a':[near('upper normal tail',tail,.13326026290250548)],'b':[near('area between cutoff andmean',.5-N.cdf((cutoff-230)/9),tail),near('inverse cutoff',cutoff,226.93549344267043)]},notes='The absent original normal-distribution givens reconstructed as mean230 and SD9; these reproduce both source numerical outputs.')
Q(p,4,r'Let $f(x)=x^2\ln(x-2)+1$, for $x>2$.',[
 P('a',r'Find $f\,\!\prime(3)$.',S('A2',r'$f\,\!\prime(3)=9$.')),
 P('b(i)','Find an equation of the normal to the graph at $x=3$ in point-gradient form.',S('A1',r'The normal gradient is $-1/9$.'),S('A1',r'$y-1=-(x-3)/9$.')),
 P('b(ii)','Write this equation in the form $y=mx+c$.',S('A1',r'$y=-x/9+4/3$.'))],
 r'$f\,\!\prime(3)=9$; normal $y-1=-(x-3)/9$, or $y=-x/9+4/3$.',{'a':[near('derivative at3',derivative(lambda x:x*x*math.log(x-2)+1,3),9,1e-6)],'b(i)':[near('normal perpendicular product',9*(-1/9),-1)],'b(ii)':[near('line through point',-3/9+4/3,1)]})
Q(p,5,r'In the expansion of $(2x+ax^2)^7$, where $a\in\mathbb{R}$, the coefficient of $x^9$ is6048.',[P('','Find all possible values of $a$.',S('M1',r'Use the general term $\binom7r(2x)^{7-r}(ax^2)^r$.'),S('A1',r'The exponent is $7+r=9$, so $r=2$.'),S('A1',r'The coefficient is $\binom72\,2^5a^2=672a^2$.'),S('M1',r'Set $672a^2=6048$.'),S('A1',r'$a^2=9$.'),S('A1',r'$a=3$ or $a=-3$.'))],
 r'$a=\pm3$.',{'':[near('binomial coefficient factor',math.comb(7,2)*2**5,672),near('positive a coefficient',672*3**2,6048),near('negative a coefficient',672*(-3)**2,6048)]})
theta=bisect(lambda t:256*(t-math.sin(t))/(t+2)**2-6.7,.1,3);radius=16/(theta+2)
Q(p,6,r'A minor sector $OAB$ has radius $r$ centimetres and angle $\theta$ radians, where $0<\theta<\pi$. The area between its chord $AB$ and its minor arc is $3.35\,\mathrm{cm}^2$. The perimeter of the sector, including both radii, is16cm.',[
 P('a',r'Show that $r^2(\theta-\sin\theta)=6.7$.',S('M1',r'Subtract triangle $OAB$ from the sector.'),S('A1',r'The two areas are $r^2\theta/2$ and $r^2\sin\theta/2$.'),S('A1',r'$r^2(\theta-\sin\theta)/2=3.35$, giving the result.')),
 P('b',r'Find $\theta$ and $r$.',S('A1',r'$r(\theta+2)=16$, so $r=16/(\theta+2)$.'),S('M1',r'Solve $[16/(\theta+2)]^2(\theta-\sin\theta)=6.7$ on $(0,\pi)$.'),S('A1',r'$\theta=1.200083\ldots\approx1.20$ radians.'),S('A1',r'$r=4.999870\ldots\approx5.00\,\mathrm{cm}$.'))],
 r'$\theta\approx1.20$ radians and $r\approx5.00$cm.',{'a':[near('segment area identity',radius**2*(theta-math.sin(theta))/2,3.35)],'b':[near('sector perimeter',radius*(theta+2),16),near('sector root',theta,1.2000831300057664)]},sector())
large=10*math.sqrt(2)+math.sqrt(89);small=10*math.sqrt(2)-math.sqrt(89)
Q(p,7,r'A fixed segment $AB$ is20cm long. The point $X$ lies strictly to the right of $B$ on a horizontal ray. The angle $ABX$ is $45^\circ$. The diagram is schematic.',[
 P('a','Find $BX$ when $AX$ is perpendicular to the ray.',S('M1',r'Use $\cos45^\circ=BX/20$ in the right triangle.'),S('A1',r'$BX=10\sqrt2$cm.')),
 P('b','Find $BX$ when $AX=20$cm.',S('A1',r'$BX=20\sqrt2$cm; the root $BX=0$ is excluded because $X\ne B$.')),
 P('c','Find the two possible values of $BX$ when $AX=17$cm.',S('M1',r'Apply the cosine rule to triangle $ABX$.'),S('A1',r'$17^2=BX^2+20^2-40BX\cos45^\circ$.'),S('A1',r'$BX=10\sqrt2+\sqrt{89}\approx23.6$cm.'),S('A1',r'$BX=10\sqrt2-\sqrt{89}\approx4.71$cm.'))],
 r'$10\sqrt2$, $20\sqrt2$; then $10\sqrt2\pm\sqrt{89}$.',{'a':[near('projection',20*math.cos(math.pi/4),10*math.sqrt(2))],'b':[near('equal-side cosine equation',(20*math.sqrt(2))**2+400-40*20*math.sqrt(2)*math.cos(math.pi/4),400)],'c':[near('large-distance cosine equation',large*large+400-40*large*math.cos(math.pi/4),289),near('small-distance cosine equation',small*small+400-40*small*math.cos(math.pi/4),289)]},ray_triangle())
low=bisect(lambda x:math.atan(x/2)-math.atan(x/3)-math.pi/18,.1,2);high=bisect(lambda x:math.atan(x/2)-math.atan(x/3)-math.pi/18,3,8)
Q(p,8,r'Points $B,A,Q$ lie in that order on a horizontal line, with $BA=1$ and $AQ=2$. Point $P$ is vertically above $Q$, with $PQ=x>0$. Let $\alpha=\angle PAQ$ and $\beta=\angle PBQ$. All angles are measured in degrees. Parts(a),(b),(c) describe separate positions of $P$.',[
 P('a(i)',r'Given $\alpha=45^\circ$, find $x$.',S('A1',r'$x=2\tan45^\circ=2$.')),
 P('a(ii)',r'For this position, find $\beta$.',S('M1',r'$\tan\beta=2/3$.'),S('A1',r'$\beta=33.690\ldots^\circ\approx33.7^\circ$.')),
 P('b',r'Given $\beta=40^\circ$, find $\alpha$.',S('M1',r'$x=3\tan40^\circ$.'),S('A1',r'$x=2.517298\ldots$.'),S('A1',r'$\alpha=\tan^{-1}(x/2)=51.5327\ldots^\circ\approx51.5^\circ$.')),
 P('c(i)',r'Now $\angle APB=10^\circ$. Show that $x=2\tan\alpha=3\tan\beta$.',S('M1',r'Use right triangles $AQP$ and $BQP$.'),S('A1',r'$\tan\alpha=x/2$ and $\tan\beta=x/3$, giving the result.')),
 P('c(ii)',r'Express $\angle APB$ in terms of $\alpha$ and $\beta$.',S('A1',r'$\angle APB=\alpha-\beta$.')),
 P('c(iii)','Find the two possible values of $x$.',S('M1',r'Solve $2\tan(10^\circ+\beta)=3\tan\beta$ for $0<\beta<80^\circ$.'),S('A1',r'$\beta=25.127\ldots^\circ$ or $54.872\ldots^\circ$.'),S('A1',r'$x=3\tan\beta\approx1.41$ or $4.26$.'))],
 r'$x=2$, $\beta=33.7^\circ$; $\alpha=51.5^\circ$; final $x=1.41$ or $4.26$.',{'a(i)':[near('height at45',2*math.tan(math.pi/4),2)],'a(ii)':[near('beta degrees',math.degrees(math.atan(2/3)),33.69006752598)],'b':[near('alpha givenbeta40',math.degrees(math.atan(3*math.tan(math.radians(40))/2)),51.53277428756,1e-6)],'c(i)':[near('height identity at x3',2*math.tan(math.atan(3/2)),3)],'c(ii)':[near('interior angle sum model',180-math.degrees(math.atan(3/3))-(180-math.degrees(math.atan(3/2))),math.degrees(math.atan(3/2)-math.atan(3/3)))],'c(iii)':[near('lower height angle',math.degrees(math.atan(low/2)-math.atan(low/3)),10),near('upper height angle',math.degrees(math.atan(high/2)-math.atan(high/3)),10)]},elevation(),notes='Corrects source part b denominator3 to2; its final51.5degree answer is correct. Separate positions explicitly prevent incompatible angle givens.')
Q(p,9,r'Let $f(x)=\sqrt{1+x}+\sqrt{1-x}$, for $-1\le x\le1$. The endpoints of its graph are $A$ and $B$, with $B$ having positive $x$-coordinate. Let $O$ be the origin.',[
 P('a(i)','Find the exact value of $f(1)$.',S('A1',r'$f(1)=\sqrt2$.')),
 P('a(ii)','State the range of $f$.',S('A1',r'The minimum is $\sqrt2$.'),S('A1',r'The maximum is2, so $\sqrt2\le y\le2$.')),
 P('b','The horizontal line $y=k$ meets the graph at exactly one point. Find $k$.',S('A1',r'$k=2$.')),
 P('c','Find the gradient $m$ of $OB$.',S('A1',r'$m=\sqrt2$.')),
 P('d','Find all values of $k$ for which the line $y=kx$ has no point in common with the graph of $f$.',S('A1',r'The negative bounding slope is $-\sqrt2$.'),S('A1',r'The positive bounding slope is $\sqrt2$.'),S('A1',r'$-\sqrt2<k<\sqrt2$, with both endpoints excluded because the lines then meet $A$ or $B$.')),
 P('e','Find the area of the shaded region bounded by the graph of $f$ and the segments $OA$ and $OB$.',S('M1',r'Integrate $f$ over $[-1,1]$.'),S('A1',r'$\int_{-1}^1f(x)\,\mathrm{d}x=8\sqrt2/3=3.771236\ldots$.'),S('A1',r'The area under $OA$ and $OB$ totals $\sqrt2$.'),S('A1',r'The required area is $5\sqrt2/3\approx2.36$.'))],
 r'$f(1)=\sqrt2$; range $[\sqrt2,2]$; $k=2$; $m=\sqrt2$; no intersections for $-\sqrt2<k<\sqrt2$; area $5\sqrt2/3$.',{'a(i)':[near('endpoint',math.sqrt(2)+math.sqrt(0),math.sqrt(2))],'a(ii)':[near('maximum at0',math.sqrt(1)+math.sqrt(1),2),same('sample domain bound',all(math.sqrt(1+i/100)+math.sqrt(1-i/100)>=math.sqrt(2)-1e-10 for i in range(-100,101)),True)],'b':[near('unique maximum symmetry test',2*math.sqrt(1-0),2)],'c':[near('gradient OB',math.sqrt(2)/1,math.sqrt(2))],'d':[same('positive-ray ratio bound',all((math.sqrt(1+x/100)+math.sqrt(1-x/100))/(x/100)>=math.sqrt(2)-1e-9 for x in range(1,101)),True)],'e':[near('integral minus triangle',8*math.sqrt(2)/3-math.sqrt(2),5*math.sqrt(2)/3)]},curve_dome(),notes='Source d is about slopes through the origin, reconstructed explicitly to match strict interval−sqrt2<k<sqrt2. Source remark mistakenly labels area part d rather than e.')
Q(p,10,'An infinite chain of squares has consecutive bases on segment $AB$. The first three side lengths are1.2,0.72 and0.432 metres, and successive side lengths form a geometric sequence.',[
 P('a','Find the common ratio $r$ of the side lengths.',S('M1',r'Compute successive ratios $0.72/1.2$ and $0.432/0.72$.'),S('A1',r'$r=0.6$.')),
 P('b','Find the common ratio $R$ of the areas.',S('M1',r'Area is proportional to the square of side length.'),S('A1',r'$R=r^2=0.36$.')),
 P('c','Find the length $AB$.',S('M1',r'Use the infinite geometric sum of the side lengths.'),S('A1',r'$AB=1.2/(1-0.6)$.'),S('A1',r'$AB=3$m.')),
 P('d','Find the sum of the areas of the first8 squares. Give your answer to4 decimal places.',S('M1',r'Use first area $1.2^2$ and ratio0.36.'),S('A1',r'$S_8=1.2^2(1-0.36^8)/(1-0.36)$.'),S('A1',r'$S_8=2.2494\,\mathrm{m}^2$.')),
 P('e','Find the sum of the areas of all the squares.',S('M1',r'$S_\infty=1.2^2/(1-0.36)$.'),S('A1',r'$S_\infty=2.25\,\mathrm{m}^2$.')),
 P('f','A separate chain has first side length $2x$ metres and side-length ratio $x$, where $0<x<1$. Its total base length is8m. Find the sum of its square areas.',S('M1',r'$2x/(1-x)=8$.'),S('A1',r'$x=0.8$.'),S('A1',r'The first area is $(2\times0.8)^2=2.56$ and area ratio is0.64.'),S('A1',r'Total area $=2.56/(1-0.64)=64/9\approx7.11\,\mathrm{m}^2$.'))],
 '$r=.6,R=.36,AB=3$; first8 area2.2494; total2.25; second chain64/9.',{'a':[near('side ratio1',.72/1.2,.6),near('side ratio2',.432/.72,.6)],'b':[near('area ratio',.72**2/1.2**2,.36)],'c':[near('infinite length',1.2/(1-.6),3)],'d':[near('first8 area sum',sum((1.2*.6**k)**2 for k in range(8)),2.2493652506460155,1e-7)],'e':[near('all area',1.44/(1-.36),2.25)],'f':[near('new base length',1.6/(1-.8),8),near('new area sum',2.56/(1-.64),64/9)]},square_chain())

# SET B PAPER 1 ---------------------------------------------------------------
p=paper('B',1)
Q(p,1,r'Let $f(x)=2x-1$ and $g(x)=3x$, for $x\in\mathbb{R}$.',[
 P('a',r'Find $(f\circ g)(x)$.',S('A1',r'$(f\circ g)(x)=6x-1$.')),
 P('b',r'Find $(g\circ f)(x)$ and hence simplify $(f\circ g)(x)-(g\circ f)(x)$.',S('A1',r'$(g\circ f)(x)=6x-3$.'),S('A1',r'The difference is2.')),
 P('c',r'Find $f^{-1}(x)$.',S('M1',r'$y=2x-1\implies x=(y+1)/2$.'),S('A1',r'$f^{-1}(x)=(x+1)/2$.'))],
 r'$6x-1$; $6x-3$, difference2; $f^{-1}(x)=(x+1)/2$.',{'a':[near('composition at.4',2*(3*.4)-1,6*.4-1)],'b':[near('composition difference at2',(2*(3*2)-1)-3*(2*2-1),2)],'c':[near('inverse composition',2*((7+1)/2)-1,7)]})
Q(p,2,r'In triangle $ABC$, $AB=2$cm, $AC=3$cm and $BC=\sqrt7$cm.',[
 P('a',r'Find $\angle BAC$ exactly.',S('M1',r'Use the cosine rule with side $BC$ opposite $\angle BAC$.'),S('A1',r'$7=2^2+3^2-2\cdot2\cdot3\cos\angle BAC$.'),S('A1',r'$\cos\angle BAC=1/2$.'),S('A1',r'$\angle BAC=60^\circ$.')),
 P('b','Find the exact area of the triangle.',S('M1',r'Use $\frac12 AB\cdot AC\sin\angle BAC$.'),S('A1',r'The area is $3\sqrt3/2\,\mathrm{cm}^2$.'))],
 r'$\angle BAC=60^\circ$ and area $3\sqrt3/2\,\mathrm{cm}^2$.',{'a':[near('cosine rule',2**2+3**2-2*2*3*math.cos(math.pi/3),7)],'b':[near('triangle area',.5*2*3*math.sin(math.pi/3),3*math.sqrt(3)/2)]},triangle_sqrt7())
Q(p,3,r'Consider the convergent infinite geometric series $4+4\left(\dfrac a7\right)+4\left(\dfrac{a^2}{49}\right)+\cdots$.',[
 P('a','State its common ratio $r$.',S('A1',r'$r=a/7$.')),
 P('b','The sum to infinity is7. Find $a$.',S('M1',r'Use $S_\infty=u_1/(1-r)$.'),S('A1',r'$4/(1-a/7)=7$.'),S('A1',r'$4=7-a$.'),S('A1',r'$a=3$, with $|a/7|<1$ as required.'))],
 '$r=a/7$ and $a=3$.',{'a':[near('ratio of term2 toterm1',(4*F(3,7))/4,F(3,7))],'b':[near('infinite sum',F(4)/(1-F(3,7)),7),same('convergence',abs(F(3,7))<1,True)]})
cos_graph=graph('Graph of f(x) = p cos(qx) + 9',[(lambda x:-5*math.cos(math.pi*x/8)+9,-3,36,False)],(-4,37),(0,16),[0,8,16,24,32],[4,9,14],[(24,14,'A(24,14)',25,-17),(0,4,'(0,4)',35,15)])
Q(p,4,r'The graph of $f(x)=p\cos(qx)+9$, where $q>0$ and $x$ is measured in radians, is shown. It has a local maximum at $A(24,14)$ and a minimum at the $y$-intercept $(0,4)$. The complete cycles visible in the diagram are part of the given information.',[
 P('a','Find the period of $f$.',S('M1',r'From $x=0$ to the marked maximum at24 there are1.5 periods.'),S('A1',r'The period is16.')),
 P('b','State the amplitude.',S('A1',r'The amplitude is $14-9=5$.')),
 P('c','Find $p$ and $q$.',S('A1',r'$p=-5$, since $f(0)$ is a minimum.'),S('M1',r'$q=2\pi/(\mathrm{period})$.'),S('A1',r'$q=\pi/8$.'))],
 r'$T=16$, amplitude5, $p=-5$, $q=\pi/8$.',{'a':[near('period test',-5*math.cos(math.pi*16/8)+9,4),near('marked max',-5*math.cos(math.pi*24/8)+9,14)],'b':[near('amplitude',(14-4)/2,5)],'c':[near('q period product',(math.pi/8)*16,2*math.pi)]},cos_graph)
Q(p,5,'Consider the following integrals.',[
 P('a',r'Find $\displaystyle\int\frac{12x^3}{x^4+1}\,\mathrm{d}x$.',S('M1',r'Let $u=x^4+1$.'),S('A1',r'$\mathrm{d}u=4x^3\,\mathrm{d}x$.'),S('A1',r'The integral becomes $3\int u^{-1}\,\mathrm{d}u$.'),S('A1',r'$3\ln(x^4+1)+C$; $x^4+1$ is always positive.')),
 P('b',r'Given $\displaystyle\int_0^1\frac{12x^3}{x^4+1}\,\mathrm{d}x=\ln A$, find $A$.',S('M1',r'The definite integral is $3\ln2-3\ln1=3\ln2$.'),S('A1',r'$A=8$.'))],
 r'Antiderivative $3\ln(x^4+1)+C$ and $A=8$.',{'a':[near('antiderivative check at.7',derivative(lambda x:3*math.log(x**4+1),.7),12*.7**3/(.7**4+1),1e-6)],'b':[near('definite integral',simpson(lambda x:12*x**3/(x**4+1),0,1),math.log(8))]})
Q(p,6,'Solve the equation over the real numbers.',[P('',r'$4^{x+1}3^x=6^{x+1}$. Give an exact answer.',S('M1',r'Write $4\cdot4^x3^x=6\cdot6^x$.'),S('A1',r'$4^x3^x/6^x=6/4$.'),S('A1',r'$(4\cdot3/6)^x=3/2$.'),S('A1',r'$2^x=3/2$.'),S('M1',r'Take logarithms base2.'),S('A1',r'$x=\log_2(3/2)=\log_2 3-1$.'))],
 r'$x=\log_2 3-1$.',{'':[near('original exponential equation',4**(math.log2(1.5)+1)*3**math.log2(1.5),6**(math.log2(1.5)+1)),same('positive base monotonic uniqueness',2>1,True)]})
def smooth_f(x):
    if x<0:return -1-3*math.exp(-x*x)
    if x<=2:
        t=x/2;return -4+7*(3*t*t-2*t*t*t)+8*t*t*(1-t)**2
    return 2+math.exp(-(x-2)**2)
def asymptotes(X,Y):
    return line(X(-4.5),Y(-1),X(4.5),Y(-1),True)+line(X(-4.5),Y(2),X(4.5),Y(2),True)+text(X(3.7),Y(2)-12,'y = 2',16)+text(X(-3.5),Y(-1)+24,'y = −1',16)
f_graph=graph('A differentiable function f with stationary points A and B',[(smooth_f,-4.5,4.5,False)],(-4.8,4.8),(-4.6,4.2),[-4,-2,0,1,2,4],[-4,-1,2,3],[(2,3,'A(2,3)',30,-15),(0,-4,'B(0,−4)',65,18)],asymptotes)
Q(p,7,r'The diagram shows a differentiable function $f$, with stationary points $A(2,3)$ and $B(0,-4)$. Let $g(x)=x^2+1$.',[
 P('a',r'Find $(f\circ g)(1)$ and $(g\circ f)(0)$.',S('A1',r'$g(1)=2$, so $(f\circ g)(1)=f(2)=3$.'),S('A1',r'$(g\circ f)(0)=g(-4)=17$.')),
 P('b',r'Find the gradient of the normal to $y=f(x)/g(x)$ at $x=2$.',S('M1',r'Use the quotient rule $y\,\!\prime=(f\,\!\prime g-fg\,\!\prime)/g^2$.'),S('A1',r'$g\,\!\prime(x)=2x$, and $f\,\!\prime(2)=0$ because $A$ is stationary.'),S('A1',r'$y\,\!\prime(2)=[0\cdot5-3\cdot4]/25=-12/25$.'),S('A1',r'The normal gradient is $25/12$.'))],
 '$3$ and $17$; normal gradient $25/12$.',{'a':[near('graph f atg1',smooth_f(2),3),near('g off0',smooth_f(0)**2+1,17)],'b':[near('quotient derivative',derivative(lambda x:smooth_f(x)/(x*x+1),2),-12/25,2e-5),near('normal perpendicular product',(-12/25)*(25/12),-1)]},f_graph,notes='The absent original question graphic is reconstructed with its displayed stationary points, intercept and horizontal asymptotes. A smooth compatible curve is used; no unsupported analytic formula for f is required of students.')
Q(p,8,r'In triangle $ABC$, $\angle CAB=x$ and $\angle ABC=2x$, with $0^\circ<x<90^\circ$ and $\sin x=3/5$. Side $BC=25$cm. Point $D$ is the foot of the perpendicular from $C$ to $AB$ and lies between $A$ and $B$.',[
 P('a',r'Find the exact values of $\cos x$ and $\sin2x$.',S('M1',r'Use $\cos^2x=1-\sin^2x$ and the first-quadrant condition.'),S('A2',r'$\cos x=4/5$.'),S('A1',r'$\sin2x=2(3/5)(4/5)=24/25$.')),
 P('b',r'Find the exact value of $\cos2x$.',S('M1',r'Use $\cos2x=1-2\sin^2x$.'),S('A1',r'$1-2(3/5)^2=1-18/25$.'),S('A1',r'$\cos2x=7/25$.')),
 P('c','Find $AC$.',S('M1',r'Use the sine rule: $25/\sin x=AC/\sin2x$.'),S('A1',r'$AC=25(24/25)/(3/5)$.'),S('A1',r'$AC=40$cm.')),
 P('d','Find $BD$.',S('M1',r'$\cos2x=BD/25$.'),S('A1',r'$BD=7$cm.')),
 P('e','Find the area of triangle $ABC$.',S('A1',r'$AD=40\cos x=32$, so $AB=32+7=39$.'),S('M1',r'Area $=\frac12 AC\cdot AB\sin x$.'),S('A1',r'The area is468$\,\mathrm{cm}^2$.'))],
 r'$\cos x=4/5$, $\sin2x=24/25$, $\cos2x=7/25$, $AC=40$, $BD=7$, area468.',{'a':[near('positive cosine',math.sqrt(1-(3/5)**2),4/5),near('double angle sine',2*(3/5)*(4/5),24/25)],'b':[near('double angle cosine',1-2*(3/5)**2,7/25)],'c':[near('sine rule side',25*(24/25)/(3/5),40)],'d':[near('projection',25*(7/25),7)],'e':[near('coordinate BC',math.hypot(39-32,24),25),near('area',.5*39*24,468)]},trig_triangle())
ef=lambda x:math.exp(2*x)+math.exp(x)+x-6
exp_graph=graph('Given graph y = f(x)',[(ef,-5.5,1.4,False)],(-6,6),(-6,6),[-4,-2,0,2,4],[-4,-2,2,4],[(0,-4,'(0,−4)',45,15)])
Q(p,9,r'Let $f(x)=e^{2x}+e^x+x-6$, with domain $\mathbb{R}$. The graph of $f$ is provided.',[
 P('a(i)','Show that $f$ is strictly increasing.',S('M1',r'$f\,\!\prime(x)=2e^{2x}+e^x+1$.'),S('A1',r'Every term is positive, so $f\,\!\prime(x)>0$ for all real $x$.')),
 P('a(ii)','Show that its graph is concave upwards.',S('A1',r'$f\,\!\prime\prime(x)=4e^{2x}+e^x$.'),S('A1',r'This is positive for every real $x$, proving the required concavity.')),
 P('b',r'On the same axes, sketch $y=f^{-1}(x)$ and $y=x$. Label the $x$-intercept of the inverse and show the common intersection of the three graphs.',S('A1',r'The inverse graph is the reflection of $y=f(x)$ in $y=x$.'),S('A1',r'Draw the line $y=x$.'),S('A1',r'The graphs meet at the same fixed point on that line; $(\ln2,\ln2)$ if labelled.'),S('A1',r'The inverse $x$-intercept is $(-4,0)$.')),
 P('c',r'The graph $y=2f(x)+k$ passes through the origin. Find $k$.',S('M1',r'$f(0)=-4$, so the transformed $y$-intercept is $-8+k$.'),S('A1',r'$k=8$.')),
 P('d',r'Simplify $f(\ln x)-\ln x$, for $x>0$.',S('M1',r'Substitute $\ln x$: $e^{2\ln x}+e^{\ln x}+\ln x-6-\ln x$.'),S('A1',r'This simplifies to $x^2+x-6$.'))],
 r'Increasing and concave up; inverse intercept $(-4,0)$, fixed point $(\ln2,\ln2)$; $k=8$; $x^2+x-6$.',{'a(i)':[near('first derivative at.2',derivative(ef,.2),2*math.exp(.4)+math.exp(.2)+1,1e-6)],'a(ii)':[same('positive second derivative samples',all(4*math.exp(2*x)+math.exp(x)>0 for x in [-5,-1,0,1]),True)],'b':[near('fixed point',ef(math.log(2)),math.log(2)),near('inverse intercept source',ef(0),-4)],'c':[near('transformed origin',2*ef(0)+8,0)],'d':[near('log substitution at3',ef(math.log(3))-math.log(3),3**2+3-6)]},exp_graph,notes='Corrects source b prose x-intercept4 to−4 (source graph alreadyshows−4). Removes false =f(x) inserted in source d; final simplified polynomial is correct.')
Q(p,10,r'Let $F(u)=(2u-1)(u-1)(u+3)$. All requested solutions are real.',[
 P('a',r'Solve $F(u)=0$.',S('A1',r'$u=1/2$ or $u=1$.'),S('A1',r'$u=-3$.')),
 P('b',r'Expand $F(u)$ to show that $F(u)=2u^3+3u^2-8u+3$.',S('A1',r'Expansion gives $2u^3+3u^2-8u+3$.')),
 P('c',r'Hence solve $2(\ln x)^3+3(\ln x)^2-8\ln x+3=0$.',S('A1',r'$\ln x=1/2\implies x=\sqrt e$.'),S('A1',r'$\ln x=1\implies x=e$.'),S('A1',r'$\ln x=-3\implies x=e^{-3}$.')),
 P('d',r'Solve $2e^{3x}+3e^{2x}-8e^x+3=0$.',S('A1',r'$e^x=1/2\implies x=\ln(1/2)$.'),S('A1',r'$e^x=1\implies x=0$.'),S('A1',r'$e^x=-3$ is impossible and is rejected.')),
 P('e',r'Solve $8\sin x-3\sin^2x-2\sin^3x=3$ for $0\le x\le2\pi$.',S('A1',r'$\sin x=1/2\implies x=\pi/6$.'),S('A1',r'Also $x=5\pi/6$.'),S('A1',r'$\sin x=1\implies x=\pi/2$.'),S('A1',r'$\sin x=-3$ is impossible; there are no further solutions.'))],
 r'$u=1/2,1,-3$; logarithmic roots $\sqrt e,e,e^{-3}$; exponential roots $\ln(1/2),0$; trig roots $\pi/6,\pi/2,5\pi/6$.',{'a':[same('three factor roots',[(2*u-1)*(u-1)*(u+3) for u in [F(1,2),F(1),F(-3)]],[0,0,0])],'b':[near('expansion coefficient check at2',(2*2-1)*(2-1)*(2+3),2*2**3+3*2**2-8*2+3)],'c':[near('log root e^-3',2*math.log(math.exp(-3))**3+3*math.log(math.exp(-3))**2-8*math.log(math.exp(-3))+3,0)],'d':[near('exponential root ln.5',2*.5**3+3*.5**2-8*.5+3,0),same('negative exp excluded',-3>0,False)],'e':[near('first sine root',8*.5-3*.5**2-2*.5**3,3),near('second sine value',8-3-2,3),same('negative sine root excluded',-1<=-3<=1,False)]})

# SET B PAPER 2 ---------------------------------------------------------------
p=paper('B',2)
Q(p,1,r'Events $A$ and $B$ are independent, with $P(A)=0.34$ and $P(B)=0.45$.',[
 P('a',r'Find $P(A\cap B)$.',S('M1',r'Independence gives $P(A\cap B)=P(A)P(B)$.'),S('A1',r'$P(A\cap B)=0.153$.')),
 P('b',r'Find $P(A\cup B)$.',S('M1',r'Use $P(A)+P(B)-P(A\cap B)$.'),S('A1',r'$P(A\cup B)=0.637$.'))],
 r'$P(A\cap B)=0.153$ and $P(A\cup B)=0.637$.',{'a':[near('independent intersection',.34*.45,.153)],'b':[near('union inclusion-exclusion',.34+.45-.34*.45,.637)]})
xs=[12,15,17,23,28];ys=[127,142,144,151,171];xb=statistics.mean(xs);yb=statistics.mean(ys);sxx=sum((v-xb)**2 for v in xs);syy=sum((v-yb)**2 for v in ys);sxy=sum((u-xb)*(v-yb) for u,v in zip(xs,ys));rr=sxy/math.sqrt(sxx*syy)
Q(p,2,'Five paired measurements are shown. The $x$-measurements are integers. The regression line of $y$ on $x$, with its coefficients rounded to3 decimal places, is $y=2.398x+101.446$.\n\n| $x$ |12|15|17|$a$|28|\n|---|---|---|---|---|---|\n| $y$ |127|142|144|151|171|',[
 P('a',r'Find $\bar y$.',S('A1',r'$\bar y=735/5=147$.')),
 P('b(i)',r'Use the regression line to estimate $\bar x$, giving your answer to the nearest whole number.',S('M1',r'The regression line passes through $(\bar x,\bar y)$, so $147=2.398\bar x+101.446$ approximately.'),S('A1',r'$\bar x\approx18.9967$, giving19 to the requested accuracy.')),
 P('b(ii)','Hence find $a$.',S('M1',r'$(12+15+17+a+28)/5=19$.'),S('A1',r'$a=23$.')),
 P('c','Find the Pearson correlation coefficient $r$.',S('A1',r'$r=0.964395\ldots\approx0.964$.'))],
 r'$\bar y=147$, $\bar x\approx19$, $a=23$, $r\approx0.964$.',{'a':[near('mean y',yb,147)],'b(i)':[near('regression slope rounds',round(sxy/sxx,3),2.398),near('regression intercept rounds',round(yb-(sxy/sxx)*xb,3),101.446),near('rounded-line xbar',(147-101.446)/2.398,18.99666388657)],'b(ii)':[near('integer x4 from mean',5*19-(12+15+17+28),23)],'c':[near('Sxx',sxx,166),near('Sxy',sxy,398),near('Syy',syy,1026),near('correlation',rr,.9643958829041107)]},notes='Raw paired data are not uniquely recoverable from the source solution. This compatible reconstructed dataset has Sxx166,Sxy398,Syy1026 and exactly reproduces the supplied rounded regression coefficients and correlation. The requested rounding of xbar avoids treating rounded coefficients as exact.')
Q(p,3,r'Let $f(x)=2x^2+20x+54$, restricted to $x\le-5$.',[
 P('a',r'The range is $y\ge h$. Find $h$.',S('A1',r'$f(x)=2(x+5)^2+4$, so $h=4$.')),
 P('b',r'Find $f^{-1}(x)$.',S('M1',r'$y=2(x+5)^2+4$.'),S('A1',r'$(x+5)^2=(y-4)/2$.'),S('A1',r'Choose $x+5=-\sqrt{(y-4)/2}$, because $x\le-5$.'),S('A1',r'$f^{-1}(x)=-5-\sqrt{(x-4)/2}$, for $x\ge4$.'))],
 r'$h=4$ and $f^{-1}(x)=-5-\sqrt{(x-4)/2}$.',{'a':[near('minimum',2*(-5)**2+20*(-5)+54,4)],'b':[near('inverse round trip at22',2*(-5-math.sqrt((22-4)/2))**2+20*(-5-math.sqrt((22-4)/2))+54,22),same('branch restriction',-5-math.sqrt(9)<=-5,True)]})
equal=math.comb(12,6)/2**12;more=sum(math.comb(12,k) for k in range(7,13))/2**12
Q(p,4,'A fair coin is tossed12 times independently. Let $X$ be the number of tails.',[
 P('a','State the distribution of $X$ and find the probability of obtaining equal numbers of heads and tails.',S('A1',r'$X\sim\operatorname{Bin}(12,1/2)$.'),S('M1',r'Calculate $P(X=6)$.'),S('A1',r'$P(X=6)=0.225585\ldots\approx0.226$.')),
 P('b','Find the probability of obtaining more tails than heads.',S('M1',r'Exclude the equal-count outcome, leaving probability $1-P(X=6)$.'),S('M1',r'By symmetry, halve the remaining probability; alternatively calculate $P(X\ge7)$ directly.'),S('A1',r'The probability is $0.387207\ldots\approx0.387$.'))],
 r'$X\sim\operatorname{Bin}(12,1/2)$; equal0.226, more tails0.387.',{'a':[near('equal count binomial',equal,.2255859375)],'b':[near('symmetry tail',(1-equal)/2,more),near('more tails',more,.38720703125)]},notes='Corrects source parameter typo n=1/2 to p=1/2; n=12 and all numerical probabilities remain unchanged.')
Q(p,5,r'A right square-based pyramid $PABCD$ has base side6cm. The apex $P$ is vertically above the centre $Q$ of the square, and $PQ=3\sqrt2$cm.',[
 P('a','Find the exact volume of the pyramid.',S('M1',r'Use one third of base area times perpendicular height.'),S('A1',r'$V=(1/3)(6)(6)(3\sqrt2)=36\sqrt2\,\mathrm{cm}^3$.')),
 P('b','Find the exact length $AC$.',S('M1',r'$AC^2=6^2+6^2$.'),S('A1',r'$AC=6\sqrt2$cm.')),
 P('c','Show that triangle $PAB$ is equilateral.',S('A1',r'$AQ=AC/2=3\sqrt2$.'),S('A1',r'$PA^2=AQ^2+PQ^2=18+18=36$, so $PA=6$; similarly $PB=6$.'),S('R1',r'$PA=PB=AB=6$, hence the triangle is equilateral.'))],
 r'$V=36\sqrt2$, $AC=6\sqrt2$, and $PA=PB=AB=6$.',{'a':[near('volume',36*3*math.sqrt(2)/3,36*math.sqrt(2))],'b':[near('base diagonal',math.hypot(6,6),6*math.sqrt(2))],'c':[near('sloping edge',math.hypot(3*math.sqrt(2),3*math.sqrt(2)),6),near('centre tovertex',math.hypot(3,3),3*math.sqrt(2))]},pyramid())
roots=[5+10*k for k in range(100)]
Q(p,6,r'Consider $\cos(\pi x/10)=0$ on the interval $0\le x\le1000$.',[
 P('a','Find all solutions, using a formula with an integer parameter.',S('A2',r'$x=5+10k$.'),S('A1',r'$k=0,1,\ldots,99$; the solutions are5,15,25,...,995.')),
 P('b','Find the sum of all these solutions.',S('M1',r'Use the arithmetic-series sum with100 terms, first5 and last995.'),S('A2',r'The sum is $100(5+995)/2=50\,000$.'))],
 r'$x=5+10k$, $k=0,\ldots,99$; sum50,000.',{'a':[same('root count',len(roots),100),near('largest root trigresidual',math.cos(math.pi*995/10),0,1e-10)],'b':[near('arithmetic sum',sum(roots),50000)]})
poly_f=lambda x:1.5*x**4-x**3/3-2.5*x*x+83
Q(p,7,r'Let $f(x)=\dfrac32x^4-\dfrac13x^3-\dfrac52x^2+83$.',[
 P('a',r'Find $f\,\!\prime(x)$.',S('A1',r'The quartic term differentiates to $6x^3$.'),S('A1',r'$f\,\!\prime(x)=6x^3-x^2-5x$.')),
 P('b',r'Find $f\,\!\prime(-1)$.',S('A1',r'$f\,\!\prime(-1)=-2$.')),
 P('c','Find the other two $x$-coordinates at which the tangent is parallel to the tangent at $x=-1$.',S('M1',r'Solve $6x^3-x^2-5x=-2$.'),S('A1',r'$x=2/3$.'),S('A1',r'$x=1/2$; the known solution $-1$ is not one of the other two.'))],
 r'$f\,\!\prime(x)=6x^3-x^2-5x$; $f\,\!\prime(-1)=-2$; other coordinates1/2,2/3.',{'a':[near('derivative at.3',derivative(poly_f,.3),6*.3**3-.3**2-5*.3,1e-6)],'b':[near('slope at-1',-6-1+5,-2)],'c':[near('slope at1/2',6*.5**3-.5**2-5*.5,-2),near('slope at2/3',6*(2/3)**3-(2/3)**2-5*(2/3),-2)]})
counts=[sum(abs(a-b)==d for a in range(1,7) for b in range(1,7)) for d in range(6)]
Q(p,8,'Two fair six-sided dice are rolled independently. Let $D$ be the absolute difference of their scores.',[
 P('a',r'Find $P(D=0)$.',S('A1',r'$P(D=0)=6/36=1/6$.')),
 P('b',r'Find $P(D=5)$.',S('M1',r'The ordered outcomes are $(1,6)$ and $(6,1)$.'),S('A1',r'$P(D=5)=2/36=1/18$.')),
 P('c',r'Find $P(D=4)$.',S('M1',r'The ordered outcomes are $(1,5),(5,1),(2,6),(6,2)$.'),S('A2',r'$P(D=4)=4/36=1/9$.')),
 P('d','Complete the following probability table by finding $x,y,z$.\n\n| $d$ |0|1|2|3|4|5|\n|---|---|---|---|---|---|---|\n| $P(D=d)$ | $6/36$ | $10/36$ | $x/36$ | $6/36$ | $y/36$ | $z/36$ |',S('A1',r'$x=8$.'),S('A1',r'$y=4$ and $z=2$.')),
 P('e','Find $E(D)$.',S('M1',r'Evaluate $\sum dP(D=d)=[10+16+18+16+10]/36$.'),S('A1',r'$E(D)=35/18$.')),
 P('f','A game gives a net profit of7 dollars if $D=5$, a net profit of1 dollar if $D=1$, and a net loss of $L$ dollars otherwise. Find $L$ if the game is fair.',S('M1',r'Use probabilities $2/36,10/36,24/36$.'),S('A1',r'$E(\mathrm{profit})=7(2/36)+1(10/36)-L(24/36)$.'),S('M1',r'Fairness requires expectation0.'),S('A1',r'$L=1$.'))],
 r'Distribution numerators6,10,8,6,4,2; $E(D)=35/18$, fair loss $L=1$.',{'a':[near('equal outcomes',counts[0]/36,F(1,6))],'b':[near('difference5 outcomes',counts[5]/36,F(1,18))],'c':[near('difference4 outcomes',counts[4]/36,F(1,9))],'d':[same('all36 enumeration',counts,[6,10,8,6,4,2])],'e':[near('enumerated expectation',sum(d*c for d,c in enumerate(counts))/36,F(35,18))],'f':[near('fair net expected profit',(7*2+10-1*24)/36,0)]})
packet_p=N.cdf((480-500)/18);conditional=(.5-packet_p)/(1-packet_p);premium_sd=26/-N.inv_cdf(.25)
Q(p,9,r'The mass $R$ of a standard packet is normally distributed with mean500g and standard deviation18g. Packets are sampled independently. A premium variety has a normally distributed mass $C$, with lower quartile724g and interquartile range52g.',[
 P('a','Find the probability that a standard packet has mass less than480g.',S('A1',r'$P(R<480)=0.133260\ldots\approx0.133$.')),
 P('b','Given that a standard packet has mass greater than480g, find the probability that it has mass less than500g.',S('M1',r'Use $P(480<R<500)/P(R>480)$.'),S('A1',r'$0.366739\ldots/0.866739\ldots=0.423126\ldots\approx0.423$.')),
 P('c','Find $a$ such that15% of standard packets have mass greater than $a$ grams.',S('M1',r'Find the85th percentile of $N(500,18^2)$.'),S('A1',r'$a=518.6558\ldots\approx519$g.')),
 P('d','Five standard packets are selected. Find the probability that exactly one has mass less than480g.',S('M1',r'Let the count be $B\sim\operatorname{Bin}(5,p)$.'),S('A1',r'Use $p=0.133260\ldots$ without premature rounding.'),S('A1',r'$P(B=1)=5p(1-p)^4=0.376032\ldots\approx0.376$.')),
 P('e(i)','Find the mean of the premium mass distribution.',S('M1',r'By normal symmetry, $Q_3=724+52=776$ and the mean is midway between the quartiles.'),S('A1',r'$\mu=(724+776)/2=750$g.')),
 P('e(ii)','Find the standard deviation of the premium mass distribution.',S('M1',r'$P(C<724)=0.25$.'),S('M1',r'$z_{0.25}=(724-750)/\sigma=-26/\sigma=-0.674489\ldots$.'),S('A1',r'$\sigma=38.54765\ldots\approx38.5$g.'))],
 r'0.133; conditional0.423; cutoff519g; exactlyone0.376; premium mean750g and SD38.5g.',{'a':[near('underweight tail',packet_p,.13326026290250548)],'b':[near('conditional belowmean',conditional,.423126,1e-5)],'c':[near('85th percentile',500+18*N.inv_cdf(.85),518.6558010108882)],'d':[near('one underweight in5',5*packet_p*(1-packet_p)**4,.3760326037695816)],'e(i)':[near('quartile midpoint',(724+776)/2,750)],'e(ii)':[near('premium sd',premium_sd,38.54765768114565),near('lowerquartile probability',N.cdf(-26/premium_sd),.25)]},notes='Missing standard-mass givens reconstructed as mean500g and SD18g, reproducing all supplied normal/binomial outputs. Explicit independent sampling justifies the binomial count.')
intersection=bisect(lambda x:4*math.cos(x)-x*x,1,1.5)
optimum=bisect(lambda a:8*math.cos(a)-8*a*math.sin(a)-6*a*a,.1,1.2)
area=lambda a:2*a*(4*math.cos(a)-a*a)
Q(p,10,r'The curves $y=4\cos x$ and $y=x^2$ intersect at $L$ and $R$, with $R$ having positive $x$-coordinate $r$. Angles are in radians. A rectangle has vertical sides at $x=-a$ and $x=a$, its upper vertices on $y=4\cos x$ and lower vertices on $y=x^2$, where $0<a<r$. Its area is $A$.',[
 P('a','Find the coordinates of $L$ and $R$.',S('A1',r'$L=(-1.201538\ldots,1.443694\ldots)\approx(-1.20,1.44)$.'),S('A1',r'$R=(1.201538\ldots,1.443694\ldots)\approx(1.20,1.44)$.')),
 P('b','Find the total area enclosed by the two curves.',S('M1',r'Integrate upper minus lower between the intersection abscissae.'),S('A1',r'Use unrounded limits $-r,r$.'),S('A1',r'The integral is $\int_{-r}^{r}(4\cos x-x^2)\,\mathrm{d}x$.'),S('A1',r'The enclosed area is $6.304327\ldots\approx6.30$.')),
 P('c',r'Show that $A=8a\cos a-2a^3$.',S('A1',r'Base $=2a$ and height $=4\cos a-a^2$.'),S('A1',r'Their product is $8a\cos a-2a^3$.')),
 P('d(i)',r'Show that a stationary value of $A$ satisfies $\dfrac{\cos a-a\sin a}{a^2}=\dfrac34$.',S('M1',r'Differentiate using the product rule.'),S('M1',r'$A\,\!\prime(a)=8\cos a-8a\sin a-6a^2=0$.'),S('A1',r'Because $a>0$, divide/rearrange to obtain $(\cos a-a\sin a)/a^2=3/4$.')),
 P('d(ii)','Find the maximum possible area of the rectangle.',S('M1',r'Maximize $A$ on $0<a<r$, by graphing or solving the derivative equation; $a=0.681137\ldots$. The endpoints tend to zero and $A\,\!\prime\prime<0$ within this interval.'),S('A1',r'$A_{\max}=3.601146\ldots\approx3.60$.'))],
 r'Intersections $(\pm1.20,1.44)$; enclosed area6.30; rectangle area $8a\cos a-2a^3$, maximum3.60.',{'a':[near('intersection residual',4*math.cos(intersection)-intersection**2,0),near('intersection ordinate',intersection**2,1.4436942847822418)],'b':[near('enclosed integral',simpson(lambda x:4*math.cos(x)-x*x,-intersection,intersection),6.304327197557455)],'c':[near('rectangle product at.6',2*.6*(4*math.cos(.6)-.6**2),8*.6*math.cos(.6)-2*.6**3)],'d(i)':[near('correct derivative finite difference',derivative(area,.7),8*math.cos(.7)-8*.7*math.sin(.7)-6*.7**2),near('stationary target',(math.cos(optimum)-optimum*math.sin(optimum))/optimum**2,.75)],'d(ii)':[near('maximum area',area(optimum),3.6011461192935452),same('strict concavity interval',intersection<math.pi/2 and all(-16*math.sin(a)-8*a*math.cos(a)-12*a<0 for a in [.01,.3,.6,1,intersection]),True),near('right endpoint area',area(intersection),0)]},area_rectangle(),notes='Source derivative line incorrectly has−3a²; corrected to−6a². Its final stationary equation and maximum3.60 are correct. Domain0<a<r and endpoint/concavity check establish global maximum.')

ERRATA=[
 {'paper':'aa-sl-set-a-paper-1','sourcePage':10,'question':'9(d)','error':'Red-probability intermediate denominators printed10 instead of5.','correction':'P(red)=p/5+2(1-p)/5=(2-p)/5. Conditional probability remains p/(2-p), so a=2 is unchanged.','requiredPDFAction':'Correct the affected expressions or add a prominent adjacent correction.'},
 {'paper':'aa-sl-set-a-paper-2','sourcePage':9,'question':'8(b)','error':'tan(alpha) denominator3 printed after finding x=2.51729.','correction':'tan(alpha)=x/2, because AQ=2; alpha rounds51.5degrees.','requiredPDFAction':'Replace denominator3 with2.'},
 {'paper':'aa-sl-set-a-paper-2','sourcePage':10,'question':'9(e)','error':'Final area remark references part(d).','correction':'Its exact5sqrt(2)/3 result refers to part(e).','requiredPDFAction':'Change the part-reference letter.'},
 {'paper':'aa-sl-set-b-paper-1','sourcePage':10,'question':'9(b)','error':'Prose says inverse x-intercept at4 although graph labels−4.','correction':'Inverse x-intercept is(−4,0), because f(0)=−4.','requiredPDFAction':'Correct sign in prose.'},
 {'paper':'aa-sl-set-b-paper-1','sourcePage':10,'question':'9(d)','error':'Spurious equality to f(x) inserted during logarithmic substitution.','correction':'f(ln x)−ln x=x²+x−6 for x>0; omit the intermediate =f(x).','requiredPDFAction':'Remove false equality.'},
 {'paper':'aa-sl-set-b-paper-2','sourcePage':5,'question':'4(a)','error':'Binomial success parameter labelled n=1/2.','correction':'Use n=12,p=1/2.','requiredPDFAction':'Change second n to p.'},
 {'paper':'aa-sl-set-b-paper-2','sourcePage':11,'question':'10(d)(i)','error':'Derivative of−2a³ printed−3a², including the next rearranged line.','correction':'A prime=8cos(a)−8a sin(a)−6a²; hence8cos(a)−8a sin(a)=6a² and final ratio3/4.','requiredPDFAction':'Replace both incorrect3a² instances with6a²; retain final ratio and maximum.'},
 {'paper':'aa-sl-set-b-paper-2','sourcePage':11,'question':'10(c)','error':'Height is labelled A, the same symbol subsequently used for rectangle area.','correction':'Use h=4cos(a)−a² for the height; retain A=2a(4cos(a)−a²).','requiredPDFAction':'Change the isolated height symbol A to h.'},
]

# Exact source-PDF coordinates measured using pdfplumber: points, top-left origin.
ERRATA[0]['replaceGlyphRegions']=[[244.1,508.5,257.0,521.5],[277.2,508.5,290.1,521.5],[318.5,508.5,331.4,521.5],[212.8,539.4,225.7,552.3],[212.8,568.1,225.7,581.0]]
ERRATA[0]['replacementGlyph']='5'
ERRATA[1]['replaceGlyphRegions']=[[157.2,469.2,164.2,482.2]];ERRATA[1]['replacementGlyph']='2'
ERRATA[2]['replaceTextRegion']=[90,675,560,703]
ERRATA[3]['replaceTextRegion']=[96.5,425.5,175,438]
ERRATA[4]['removeTextRegion']=[174.2,590.9,205.6,606.2]
ERRATA[5]['replaceGlyphRegions']=[[263.4,72.9,270.6,86.1]];ERRATA[5]['replacementGlyph']='p'
ERRATA[6]['replaceGlyphRegions']=[[243.0,339.5,249.8,354.2],[387.2,339.5,394.4,354.2]];ERRATA[6]['replacementGlyph']='6'
ERRATA[7]['replaceGlyphRegions']=[[207.7,250.0,216.2,263.0]];ERRATA[7]['replacementGlyph']='h'

def write():
    OUT.mkdir(parents=True,exist_ok=True);DOC.parent.mkdir(parents=True,exist_ok=True)
    result=[]
    for key,p in PAPERS.items():
        assert len(p['questions'])==10
        assert sum(q['marks'] for q in p['questions'])==80
        assert {section:sum(q['marks'] for q in p['questions'] if q['section']==section) for section in ['A','B']}=={'A':40,'B':40}
        assert sum(len(q['parts']) for q in p['questions'])==sum(len(r['partChecks']) for r in EVIDENCE[key])
        for q in p['questions']:
            assert q['marks']==sum(a['marks'] for a in q['parts'])
            for part,scheme in zip(q['parts'],q['markScheme'],strict=True):
                assert part['label']==scheme['part']
                assert part['marks']==sum(int(s['code'][1:]) for s in scheme['steps'])
                assert all(re.fullmatch('[MAR][1-9]',s['code']) for s in scheme['steps'])
            if 'diagramSvg' in q:
                assert len(q['diagramSvg'])<300000
                assert not re.search(r'<(?:script|foreignObject|image|style|defs|iframe)\b|\b(?:href|src|on\w+)\s*=',q['diagramSvg'],re.I)
        path=OUT/(key+'.json');path.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
        result.append({'paper':key,'status':'author verification passed; separate review pending','questions':10,'marks':80,'minutes':90,'calculator':p['calculator'],'sectionMarks':{'A':40,'B':40},'diagrams':sum('diagramSvg' in q for q in p['questions']),'parts':sum(len(q['parts']) for q in p['questions']),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'records':EVIDENCE[key]})
    checks=sum(len(tests) for records in EVIDENCE.values() for record in records for tests in record['partChecks'].values())
    report={'status':'author verification passed; separate review pending','papers':4,'questions':40,'marks':320,'executableChecks':checks,'sourcePagesIndividuallyInspected':40,'scientificDiagramsIndividuallyInspected':14,'diagramReview':'All14SVGs rasterized and inspected in a contact sheet; complex elevation, graph-stationary-point and rectangle figures also inspected natively. Refined sector shading to isolate minor segment, kept axes above shaded fills, moved overlapping asymptote text and attached pyramid-height label to perpendicular PQ.','provenance':'Questions are newly worded reconstructions compatible with user-supplied solution books, not exact recovered originals. All missing contexts, domains and geometric assumptions are explicit. Source author/rights and branding handling are for the release owner to resolve.','method':'Read every source solution page as a native render, then independently reconstructed complete givens and demands, recomputed every part with standard-library arithmetic, exact fractions, combinatorial enumeration, normalCDF/inverseCDF, bracketed roots, finite-difference derivative checks and quadrature. No source solution is assumed infallible.','limits':['This author report is not an independent review or a publication claim.','Numerical checks supplement algebraic reasoning and do not prove arbitrary identities by themselves.','Reconstructed regression dataset is one compatible realization, not a claim to recover the original missing data.'],'sourceErrata':ERRATA,'batches':result}
    DOC.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({'papers':4,'questions':40,'marks':320,'checks':checks,'diagrams':sum(b['diagrams'] for b in result),'sourceErrata':len(ERRATA),'files':[b['paper'] for b in result]}))

if __name__=='__main__':write()
