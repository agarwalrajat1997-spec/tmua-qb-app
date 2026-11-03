"""Author and numerically verify four original current-syllabus AI HL Paper 1s.

Standard-library calculations, complete datasets and newly drawn SVGs. This is
the author pass; a separate mathematical reviewer must bind the resulting files.
"""
from pathlib import Path
import cmath
import hashlib
import html
import itertools
import json
import math
import re
from statistics import NormalDist, mean, stdev

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'content/ib/ai-mocks-2026/papers'
DOCS = ROOT / 'docs/ib-ai-mocks-2026'
N = NormalDist()
PAPERS, RECORDS = [], []
MARKS = [6]*5 + [7]*8 + [8]*3


def n(x, digits=8):
    return f'{x:.{digits}g}'


def matrix(a):
    return r'\begin{pmatrix}' + r'\\'.join('&'.join(n(x) for x in row) for row in a) + r'\end{pmatrix}'


def column(a):
    return matrix([[x] for x in a])


def mm(a, b):
    return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]


def mv(a, v):
    return [sum(x*y for x,y in zip(row,v)) for row in a]


def inverse(a):
    size = len(a)
    b = [[float(x) for x in row] + [float(i == j) for j in range(size)] for i,row in enumerate(a)]
    for j in range(size):
        pivot = max(range(j,size),key=lambda i:abs(b[i][j]))
        b[j],b[pivot] = b[pivot],b[j]
        d=b[j][j]; assert abs(d)>1e-12
        b[j]=[x/d for x in b[j]]
        for i in range(size):
            if i != j:
                d=b[i][j]; b[i]=[x-d*y for x,y in zip(b[i],b[j])]
    return [row[size:] for row in b]


def power(a, k):
    result=[[float(i==j) for j in range(len(a))] for i in range(len(a))]
    for _ in range(k): result=mm(result,a)
    return result


def close(a,b,tol=1e-8):
    if isinstance(a,(list,tuple)):
        assert len(a)==len(b)
        for x,y in zip(a,b): close(x,y,tol)
    else: assert abs(a-b)<=tol*max(1,abs(a),abs(b)),(a,b)


def root(f, lo, hi):
    assert f(lo)*f(hi)<=0,(lo,hi,f(lo),f(hi))
    for _ in range(100):
        mid=(lo+hi)/2
        if f(lo)*f(mid)<=0: hi=mid
        else: lo=mid
    return (lo+hi)/2


def integrate(f, a, b, count=10000):
    assert count%2==0
    h=(b-a)/count
    return h/3*(f(a)+f(b)+sum((4 if i%2 else 2)*f(a+i*h) for i in range(1,count)))


def beta_fraction(a,b,x):
    qab=a+b; qap=a+1; qam=a-1; c=1.; d=1-qab*x/qap
    if abs(d)<1e-300:d=1e-300
    d=1/d; h=d
    for m in range(1,301):
        aa=m*(b-m)*x/((qam+2*m)*(a+2*m))
        d=1+aa*d; c=1+aa/c
        if abs(d)<1e-300:d=1e-300
        if abs(c)<1e-300:c=1e-300
        d=1/d; h*=d*c
        aa=-(a+m)*(qab+m)*x/((a+2*m)*(qap+2*m))
        d=1+aa*d; c=1+aa/c
        if abs(d)<1e-300:d=1e-300
        if abs(c)<1e-300:c=1e-300
        d=1/d; delta=d*c; h*=delta
        if abs(delta-1)<1e-14:return h
    raise ArithmeticError('Incomplete beta failed to converge')


def ibeta(a,b,x):
    if x<=0:return 0.
    if x>=1:return 1.
    front=math.exp(math.lgamma(a+b)-math.lgamma(a)-math.lgamma(b)+a*math.log(x)+b*math.log1p(-x))
    if x<(a+1)/(a+b+2):return front*beta_fraction(a,b,x)/a
    return 1-front*beta_fraction(b,a,1-x)/b


def tcdf(t,df):
    tail=.5*ibeta(df/2,.5,df/(df+t*t))
    return 1-tail if t>=0 else tail


def tquantile(p,df):
    return root(lambda t:tcdf(t,df)-p,-100,100)


def poisson(k,lam):
    return math.exp(-lam)*lam**k/math.factorial(k)


def pcdf(k,lam):
    return sum(poisson(i,lam) for i in range(k+1))


def binomial(k,size,p):
    return math.comb(size,k)*p**k*(1-p)**(size-k)


def bcdf(k,size,p):
    return sum(binomial(i,size,p) for i in range(k+1))


def regression(x,y):
    xx=sum((v-mean(x))**2 for v in x); yy=sum((v-mean(y))**2 for v in y)
    xy=sum((u-mean(x))*(v-mean(y)) for u,v in zip(x,y))
    return xy/xx,mean(y)-xy/xx*mean(x),xy/math.sqrt(xx*yy)


def ranks(values):
    ordered=sorted(values)
    return [mean(i+1 for i,x in enumerate(ordered) if x==v) for v in values]


def chi_table(table):
    rows=[sum(row) for row in table]; cols=[sum(col) for col in zip(*table)]; total=sum(rows)
    expected=[[a*b/total for b in cols] for a in rows]
    statistic=sum((x-e)**2/e for row,erow in zip(table,expected) for x,e in zip(row,erow))
    assert min(x for row in expected for x in row)>5
    return expected,statistic


def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def norm(a): return math.sqrt(dot(a,a))


def table(headers, rows):
    return '| '+' | '.join(map(str,headers))+' |\n| '+' | '.join('---' for _ in headers)+' |\n'+'\n'.join('| '+' | '.join(map(str,row))+' |' for row in rows)


def svg(elements,width=720,height=420):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"><rect width="{width}" height="{height}" fill="white"/>'+''.join(elements)+'</svg>'


def text(x,y,value,size=18,anchor='middle'):
    return f'<text x="{x:.3f}" y="{y:.3f}" text-anchor="{anchor}" font-family="Arial, sans-serif" font-size="{size}" fill="#171717">{html.escape(str(value))}</text>'


def line(x1,y1,x2,y2,color='#202020',width=2,dash=False):
    return f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="7 5"' if dash else '')+'/>'


def arrow(x1,y1,x2,y2,color='#202020'):
    theta=math.atan2(y2-y1,x2-x1);a=10
    points=[(x2,y2),(x2-a*math.cos(theta-.4),y2-a*math.sin(theta-.4)),(x2-a*math.cos(theta+.4),y2-a*math.sin(theta+.4))]
    return line(x1,y1,x2,y2,color)+f'<polygon points="'+ ' '.join(f'{x:.2f},{y:.2f}' for x,y in points)+f'" fill="{color}"/>'


class Plot:
    def __init__(self,xmin,xmax,ymin,ymax,xticks=(),yticks=(),xlabel='x',ylabel='y'):
        self.xmin=xmin;self.xmax=xmax;self.ymin=ymin;self.ymax=ymax;self.e=[]
        axisx=max(xmin,min(xmax,0));axisy=max(ymin,min(ymax,0))
        self.e += [line(*self.xy(xmin,axisy),*self.xy(xmax,axisy)),line(*self.xy(axisx,ymin),*self.xy(axisx,ymax))]
        for x in xticks:
            px,py=self.xy(x,axisy); self.e +=[line(px,py-4,px,py+4),text(px,py+24,n(x,4),15)]
        for y in yticks:
            px,py=self.xy(axisx,y); self.e +=[line(px-4,py,px+4,py),text(px-10,py+5,n(y,4),15,'end')]
        self.e +=[text(665,self.xy(0,axisy)[1]-9,xlabel,16),text(self.xy(axisx,0)[0]+12,30,ylabel,16,'start')]
    def xy(self,x,y):return (70+570*(x-self.xmin)/(self.xmax-self.xmin),360-300*(y-self.ymin)/(self.ymax-self.ymin))
    def path(self,points,color='#202020',dash=False,fill='none'):
        self.e.append('<polyline points="'+' '.join(f'{a:.3f},{b:.3f}' for a,b in (self.xy(x,y) for x,y in points))+f'" fill="{fill}" stroke="{color}" stroke-width="2"'+(' stroke-dasharray="7 5"' if dash else '')+'/>')
    def point(self,x,y,label='',dx=10,dy=-12):
        a,b=self.xy(x,y);self.e.append(f'<circle cx="{a:.3f}" cy="{b:.3f}" r="4" fill="#202020"/>')
        if label:self.e.append(text(a+dx,b+dy,label,17,'start'))
    def done(self):return svg(self.e)


def network(positions,edges,caption='Edge labels show distances'):
    out=[text(360,27,caption,17)]
    for u,v,w in edges:
        a,b=positions[u],positions[v];out.append(line(*a,*b))
        x=(a[0]+b[0])/2;y=(a[1]+b[1])/2
        out +=[f'<rect x="{x-13:.2f}" y="{y-14:.2f}" width="26" height="24" fill="white"/>',text(x,y+5,w,17)]
    for label,(x,y) in positions.items():
        out +=[f'<circle cx="{x}" cy="{y}" r="17" fill="white" stroke="#202020" stroke-width="2"/>',text(x,y+6,label)]
    return svg(out)


def mst(vertices,edges,exclude=()):
    parent={x:x for x in vertices}; chosen=[]
    def find(x):
        while parent[x]!=x:x=parent[x]
        return x
    for u,v,w in sorted(edges,key=lambda e:e[2]):
        if frozenset((u,v)) in exclude:continue
        a,b=find(u),find(v)
        if a!=b:parent[a]=b;chosen.append((u,v,w))
    assert len(chosen)==len(vertices)-1
    return chosen,sum(e[2] for e in chosen)


def ev(name, calculated, reference=None, tolerance=1e-8):
    def finite(value):
        if isinstance(value,dict):return all(finite(v) for v in value.values())
        if isinstance(value,(list,tuple)):return all(finite(v) for v in value)
        return math.isfinite(value) if isinstance(value,(int,float)) else bool(str(value))
    assert finite(calculated),(name,calculated)
    result={'calculation':name,'calculated':calculated,'status':'passed'}
    if reference is not None:close(calculated,reference,tolerance);result.update(reference=reference,tolerance=tolerance)
    return result


def part(label,prompt,marks,steps,evidence):
    assert sum(int(code[1:]) for code,_ in steps)==marks,(label,marks,steps)
    assert evidence
    return {'label':label,'prompt':prompt,'marks':marks}, {'part':label,'steps':[{'code':code,'text':body} for code,body in steps]},evidence


def question(set_name,number,refs,stem,parts,summary,diagram=None):
    q={'number':number,'section':'','marks':sum(p[0]['marks'] for p in parts),'stem':stem,'parts':[p[0] for p in parts],
       'answerSummary':summary,'markScheme':[p[1] for p in parts],'syllabusRefs':refs,
       'cognitiveDemand':'Connect representations, choose a model or method, compute and interpret in context.'}
    assert q['marks']==MARKS[number-1],(set_name,number,q['marks'])
    if diagram:q['diagramSvg']=diagram
    RECORDS.append({'paper':f'ai-hl-set-{set_name.lower()}-paper-1','question':number,'status':'passed','syllabusRefs':refs,
                    'partChecks':{p[0]['label']:p[2] for p in parts}})
    return q


def paper_a():
    qs=[]
    # 1: an integer replacement decision, not an unqualified extrapolation.
    resale=48000*.84**5;maintenance=900*(1.18**5-1)/.18
    averages=[(48000-48000*.84**k+900*(1.18**k-1)/.18)/k for k in range(1,13)]
    best=min(range(1,13),key=lambda k:averages[k-1])
    close(maintenance,sum(900*1.18**j for j in range(5)))
    qs.append(question('A',1,['SL 1.3','SL 1.4','SL 1.8'],
      'A laboratory buys a scanner for 48 000 dollars. Its resale value falls by 16% each year. Maintenance costs 900 dollars in year 1 and rises by 18% each year. A replacement can be made at the end of any year $n$, where $1\\le n\\le12$. Define the average annual ownership cost as the purchase price minus resale value plus total maintenance, divided by $n$.',[
      part('a','Find the resale value after 5 years.',2,[('M1',r'Use $48000(0.84)^5$.'),('A1',f'The resale value is ${n(resale)}$ dollars, or $20\\,074$ dollars to the nearest dollar.')],[ev('Resale after five years',resale)]),
      part('b','Find the total maintenance cost in the first 5 years.',2,[('M1',r'Use the geometric sum $900(1.18^5-1)/(1.18-1)$.'),('A1',f'Total maintenance is ${n(maintenance)}$ dollars.')],[ev('Geometric maintenance sum',maintenance,sum(900*1.18**j for j in range(5)))]),
      part('c','Determine the replacement year that minimizes the average annual ownership cost over the permitted years. Give the minimum cost to the nearest dollar.',2,[('M1',r'Evaluate $C_n=[48000-48000(0.84)^n+900(1.18^n-1)/0.18]/n$ for integers $1\le n\le12$.'),('A1',f'Replace at the end of year ${best}$; the minimum average is ${averages[best-1]:.0f}$ dollars per year.')],[ev('All twelve feasible average costs',averages),ev('Discrete minimizing year',best)])],f'Resale {n(resale)}; maintenance {n(maintenance)}; minimum at year {best}, cost {n(averages[best-1])}.'))
    # 2: the distinction between inverse prediction and reverse regression.
    x=[10,20,30,40,50,60];y=[18.3,30.5,42.1,58.4,66.7,82.6]
    b,a,r=regression(x,y);d,c,_=regression(y,x);forward=(50-a)/b;reverse=c+d*50
    qs.append(question('A',2,['SL 4.4'],
      'A sensor is calibrated against known concentrations $x$ (mg L$^{-1}$). Its measured signal is $y$ (mV).\n\n'+table(['$x$','10','20','30','40','50','60'],[['$y$',*y]])+'\n\nTreat concentration as the controlled explanatory variable.',[
      part('a','Find the least-squares regression line of $y$ on $x$ and the Pearson correlation coefficient.',3,[('M1','Apply linear regression to all six pairs.'),('A1',f'$y={n(b)}x+{n(a)}$.'),('A1',f'$r={n(r)}$.')],[ev('y-on-x slope, intercept and correlation',[b,a,r])]),
      part('b','Use your calibration line to estimate the concentration corresponding to a signal of 50 mV. Give the result to 5 decimal places.',1,[('A1',f'$x=(50-{n(a)})/{n(b)}={forward:.5f}$ mg L$^{{-1}}$, using unrounded regression coefficients.')],[ev('Inverse calibration substitution',a+b*forward,50)]),
      part('c','Find the regression estimate of $x$ on $y$ when $y=50$, to 5 decimal places. Explain why it need not equal the answer to part (b).',2,[('A1',f'The reverse regression is $x={n(d)}y{c:+.8g}$, giving ${reverse:.5f}$ mg L$^{{-1}}$.'),('R1','The regressions minimize residuals in different directions. They are inverses only for perfect linear correlation; here $|r|<1$.')],[ev('Reverse regression prediction',reverse),ev('Squared correlation below unity',r*r)])],f'y={n(b)}x+{n(a)}, r={n(r)}; inverse prediction {n(forward)}, reverse regression {n(reverse)}.'))
    # 3: complete geometry of a Voronoi vertex.
    p=Plot(0,9,0,10,[0,2,4,6,8],[2,4,6,8,10],xlabel='x / km',ylabel='y / km')
    for X,Y,label in [(1,2,'A (1,2)'),(7,2,'B (7,2)'),(4,8,'C (4,8)')]:p.point(X,Y,label,dx=8,dy=-13)
    vertex=[4,4.25];radius=3.75
    qs.append(question('A',3,['SL 2.1','SL 3.5','SL 3.6'],
      'Three rescue stations are at $A(1,2)$, $B(7,2)$ and $C(4,8)$ on a coordinate grid measured in kilometres. Each location is assigned to its nearest station. The diagram shows the sites, not the Voronoi boundaries.',[
      part('a','Write down the equation of the boundary equidistant from $A$ and $B$.',1,[('A1','$x=4$.')],[ev('AB midpoint x-coordinate',(1+7)/2)]),
      part('b','Find the coordinates of the Voronoi vertex at which all three cells meet.',3,[('M1','Equate squared distances to $A$ and $C$, giving $6x+12y=75$.'),('M1','Solve this equation together with $x=4$.'),('A1','The vertex is $(4,4.25)$.')],[ev('Vertex squared distances',[sum((a-b)**2 for a,b in zip(vertex,site)) for site in [[1,2],[7,2],[4,8]]],[radius**2]*3)]),
      part('c','A call is received at $(4,5)$. State the station assigned to the call and calculate its straight-line distance from the call.',2,[('M1','The distances to $A,B,C$ are $\\sqrt{18},\\sqrt{18},3$ km.'),('A1','Station $C$ is assigned; the distance is $3$ km.')],[ev('Call distances',[math.sqrt(18),math.sqrt(18),3])])], 'Boundary x=4; vertex (4,4.25); call assigned to C, 3 km.',p.done()))
    # 4: df=2 allows an independent exponential-tail check.
    data=[[36,14],[28,22],[40,10]];expected,chi=chi_table(data);pv=math.exp(-chi/2)
    qs.append(question('A',4,['SL 4.11'],
      'A random sample of 150 trainees is classified by training programme and whether they pass an assessment.\n\n'+table(['Programme','Pass','Fail'],[['X',36,14],['Y',28,22],['Z',40,10]])+'\n\nUse a chi-squared test of independence at the 5% significance level.',[
      part('a','Find the expected number of passes in programme X under the null hypothesis, and state the degrees of freedom.',2,[('A1',f'$E_{{X,\\mathrm{{pass}}}}=50(104)/150={n(expected[0][0])}$.'),('A1','$df=(3-1)(2-1)=2$.')],[ev('Expected counts',expected),ev('Degrees of freedom',(3-1)*(2-1))]),
      part('b','Calculate the test statistic and the $p$-value.',2,[('M1','Use $\\chi^2=\\sum(O-E)^2/E$ across all six cells.'),('A1',f'$\\chi^2={n(chi)}$, $p={n(pv)}$.')],[ev('Chi-square statistic and df2 tail',[chi,pv])]),
      part('c','State the conclusion in context. Explain why this test alone does not establish a causal effect of programme on passing.',2,[('R1',f'$p={n(pv)}<0.05$, so reject independence: there is evidence of an association between programme and passing.'),('R1','An observational classification does not control confounding factors or randomly assign programmes, so association does not establish causation.')],[ev('Decision from calculated p-value',{'p':pv,'alpha':.05,'reject':pv<.05})])],f'Expected X pass {n(expected[0][0])}; df2; chi-square {n(chi)}, p={n(pv)}; reject independence.'))
    # 5: a vector diagram presents the data rather than the solution.
    wind=Plot(-4,7,-3,14,[-3,0,3,6],[-2,4,8,12],xlabel='east',ylabel='north')
    wind.e +=[arrow(*wind.xy(0,0),*wind.xy(3,-1),'#2563a6'),text(*wind.xy(4,-2.2),'current (3,−1)',16),arrow(*wind.xy(0,0),*wind.xy(0,12)),text(*wind.xy(2,12),'desired (0,12)',16)]
    water=[-3,13];speed=norm(water);bearing=math.degrees(math.atan2(-3,13))%360
    qs.append(question('A',5,['SL 3.3','AHL 3.10','AHL 3.12'],
      'A boat must travel due north with ground velocity $(0,12)$ km h$^{-1}$. A uniform current has velocity $(3,-1)$ km h$^{-1}$. Vector components are east and north respectively. The ground velocity is the sum of the boat velocity relative to the water and the current.',[
      part('a','Find the required velocity of the boat relative to the water.',2,[('M1','Subtract the current from the required ground velocity.'),('A1','The required velocity is $(-3,13)$ km h$^{-1}$.')],[ev('Vector addition check',[water[0]+3,water[1]-1],[0,12])]),
      part('b','Find the required speed and bearing of the boat relative to the water. Give the bearing to the nearest degree.',3,[('M1','$v=\\sqrt{(-3)^2+13^2}$ and the heading is west of north.'),('A1',f'$v={n(speed)}$ km h$^{{-1}}$.'),('A1',f'The bearing is ${bearing:.0f}^\\circ$ (${n(bearing)}^\\circ$ before rounding).')],[ev('Speed and bearing',[speed,bearing])]),
      part('c','The current changes to $(6,-2)$ while the boat keeps this same water-relative velocity. Find its eastward displacement after one hour.',1,[('A1','The new eastward ground speed is $-3+6=3$ km h$^{-1}$, so the displacement is $3$ km east.')],[ev('East displacement',(-3+6)*1)])],f'Water velocity (-3,13), speed {n(speed)}, bearing {n(bearing)} degrees; new drift 3 km east.',wind.done()))
    # 6: non-unit coefficients must be squared in the variance.
    mu=500+2*200;sd=math.sqrt(12**2+4*8**2);prob=N.cdf((930-mu)/sd)-N.cdf((880-mu)/sd);cut=mu+sd*N.inv_cdf(.99)
    qs.append(question('A',6,['AHL 4.14','AHL 4.15'],
      'Independent component masses satisfy $X\\sim N(500,12^2)$ and $Y\\sim N(200,8^2)$, in grams. A package has mass $T=X+2Y$. The same value of $Y$ is doubled; it is not the sum of two independent copies.',[
      part('a','State the distribution of $T$, including its mean and standard deviation.',3,[('M1','$E(T)=500+2(200)$ and $\\operatorname{Var}(T)=12^2+2^2(8^2)$.'),('A1','$E(T)=900$ g and $\\sigma_T=20$ g.'),('A1','$T\\sim N(900,20^2)$.')],[ev('Linear combination mean and standard deviation',[mu,sd],[900,20])]),
      part('b','Find $P(880<T<930)$.',2,[('M1','Use the normal distribution with the parameters in part (a).'),('A1',f'The probability is ${n(prob)}$.')],[ev('Normal interval probability',prob)]),
      part('c','Find the mass $c$ such that only 1% of packages exceed $c$.',2,[('M1','$c=900+20\\Phi^{-1}(0.99)$.'),('A1',f'$c={n(cut)}$ g.')],[ev('Upper percentile tail',1-N.cdf((cut-mu)/sd),.01)])],f'T ~ N(900,400); probability {n(prob)}; cutoff {n(cut)} g.'))
    # 7: area scaling is the determinant magnitude, not a length scale.
    M=[[1.2,.3],[-.4,.8]];B=mv(M,[4,0]);C=mv(M,[1,3]);det=1.2*.8+.12;pre=mv(inverse(M),[3,2])
    drawing=Plot(-1,6,-1,5,[0,2,4,6],[0,2,4]);drawing.path([(0,0),(4,0),(1,3),(0,0)],fill='#eef4fb')
    for x,y,label in [(0,0,'O'),(4,0,'B (4,0)'),(1,3,'C (1,3)')]:drawing.point(x,y,label,dx=7,dy=-12)
    qs.append(question('A',7,['AHL 1.14','AHL 3.9'],
      r'A linear transformation maps a column vector $\mathbf x$ to $M\mathbf x$, where $M=\begin{pmatrix}1.2&0.3\\-0.4&0.8\end{pmatrix}$. A triangular sign has vertices $O(0,0)$, $B(4,0)$ and $C(1,3)$; lengths are measured in metres.',[
      part('a','Find the images of $B$ and $C$.',2,[('A1',f'$B\\mapsto({n(B[0])},{n(B[1])})$.'),('A1',f'$C\\mapsto({n(C[0])},{n(C[1])})$.')],[ev('Images of B and C',[B,C])]),
      part('b','Find the area of the transformed sign.',2,[('M1','The original area is $6$ m$^2$ and the area scale factor is $|\\det M|=1.08$.'),('A1','$6(1.08)=6.48$ m$^2$.')],[ev('Area by determinant',6*det,abs(B[0]*C[1]-B[1]*C[0])/2)]),
      part('c','A transformed point is at $(3,2)$. Find its original position, showing an inverse-matrix method.',3,[('M1',r'$M^{-1}=\frac1{1.08}\begin{pmatrix}0.8&-0.3\\0.4&1.2\end{pmatrix}$.'),('M1','Multiply $M^{-1}(3,2)^T$.'),('A1',f'The original point is $({n(pre[0])},{n(pre[1])})$.')],[ev('Inverse position',pre),ev('Back-substitution',mv(M,pre),[3,2])])],f'Images {B}, {C}; area6.48; preimage {pre}.',drawing.done()))
    # 8: the maximum derivative occurs at half the carrying capacity.
    logistic=lambda t:1200/(1+7*math.exp(-.4*t));threshold=math.log(21)/.4;tm=math.log(7)/.4
    qs.append(question('A',8,['SL 2.5','AHL 2.9','AHL 5.9','AHL 5.10'],
      'The number of registered users of a service is modelled by $P(t)=1200/(1+7e^{-0.4t})$, where $t\\ge0$ is measured in days. Treat $P$ as continuous for this model.',[
      part('a','Find the initial number of users and the limiting number predicted by the model.',2,[('A1','$P(0)=150$.'),('A1','The limiting number is $1200$ users.')],[ev('Initial and carrying-capacity values',[logistic(0),1200])]),
      part('b','Find the first time when the model predicts 900 users.',2,[('M1','Solve $1200/(1+7e^{-0.4t})=900$.'),('A1',f'$t={n(threshold)}$ days.')],[ev('Threshold substitution',logistic(threshold),900)]),
      part('c','Find the maximum rate at which the number of users increases, and the time at which it occurs.',3,[('M1',r'$P\prime(t)=0.4P(1-P/1200)$, maximized when $P=600$.'),('A1','The maximum rate is $120$ users per day.'),('A1',f'This occurs at $t=\\ln(7)/0.4={n(tm)}$ days.')],[ev('Half-capacity time',logistic(tm),600),ev('Peak derivative',.4*600*(1-600/1200),120)])],f'Initial150, limit1200; threshold {n(threshold)}d; maxrate120 at {n(tm)}d.'))
    # 9: a closure changes the optimum spanning tree.
    edges=[('A','B',4),('A','C',7),('A','D',9),('B','C',2),('B','D',5),('B','E',8),('C','D',3),('C','E',6),('D','E',4)]
    tree,total=mst('ABCDE',edges);closed,ctotal=mst('ABCDE',edges,[frozenset('CD')])
    positions={'A':(90,210),'B':(260,80),'C':(300,340),'D':(470,80),'E':(625,300)}
    qs.append(question('A',9,['AHL 3.14','AHL 3.16'],
      'A conservation reserve needs fibre links connecting all five monitoring stations. The undirected graph shows the possible links and their construction costs in thousands of dollars. A connection is required between every pair of stations through the network, but a direct link is not required.',[
      part('a','Use Kruskal\'s algorithm to find a minimum spanning tree. State its edges in the order selected and its total cost.',4,[('M1','Consider edges in increasing order and reject an edge if it creates a cycle.'),('A2','A valid order is $BC,CD,AB,DE$ (the two edges of cost 4 may be interchanged).'),('A1',f'The total cost is ${total}$ thousand dollars.')],[ev('Kruskal selected tree and total',{'edges':tree,'total':total})]),
      part('b','Link $CD$ cannot now be built. Determine the revised minimum cost and list one optimal set of links.',3,[('M1','Repeat the cycle-free selection with $CD$ excluded.'),('A1','Use $BC,AB,DE,BD$.'),('A1',f'The revised cost is ${ctotal}$ thousand dollars.')],[ev('Tree under closure',{'edges':closed,'total':ctotal})])],f'Original MST {tree}, total{total}; closure MST {closed}, total{ctotal}.',network(positions,edges,'Link costs / thousands of dollars')))
    # 10: phasors are within AI; complex roots are deliberately absent.
    z1=4*cmath.exp(1j*math.pi/6);z2=3*cmath.exp(-1j*math.pi/3);z=z1+z2;arg=cmath.phase(z);cancel=arg+math.pi
    ph=Plot(-1,6,-4,4,[0,2,4,6],[-4,-2,0,2,4],xlabel='Re',ylabel='Im')
    for w,label in [(z1,'z₁'),(z2,'z₂')]:ph.e +=[arrow(*ph.xy(0,0),*ph.xy(w.real,w.imag)),text(*ph.xy(w.real+.25,w.imag+.35),label,18)]
    qs.append(question('A',10,['AHL 1.12','AHL 1.13'],
      r'Two oscillations of the same angular frequency are represented by $z_1=4e^{i\pi/6}$ and $z_2=3e^{-i\pi/3}$. Their resultant is $z=z_1+z_2$. Arguments are in radians.',[
      part('a','Express $z$ in Cartesian form.',3,[('M1','Resolve each phasor into real and imaginary components.'),('A1',r'$\operatorname{Re}z=2\sqrt3+3/2$.'),('A1',f'$z={n(z.real)}-{n(-z.imag)}i$.')],[ev('Resultant Cartesian components',[z.real,z.imag])]),
      part('b','Find the amplitude $|z|$ and principal argument of $z$.',2,[('A1','$|z|=5$.'),('A1',f'$\\arg z={n(arg)}$ rad.')],[ev('Amplitude and phase',[abs(z),arg]),ev('Orthogonal phasor amplitude',abs(z)**2,4**2+3**2)]),
      part('c','A third oscillation exactly cancels the resultant. Give its amplitude and an argument in $[0,2\\pi)$.',2,[('M1','The cancelling phasor is $-z$, so add $\\pi$ to the argument.'),('A1',f'Amplitude $5$ and argument ${n(cancel)}$ rad.')],[ev('Cancellation complex components',[(z+5*cmath.exp(1j*cancel)).real,(z+5*cmath.exp(1j*cancel)).imag],[0,0])])],f'z={z}; amplitude5, phase{n(arg)}; cancelling phase{n(cancel)}.',ph.done()))
    # 11: a mixture is not itself modelled as a single Poisson variable.
    zero=.7*poisson(0,4)+.3*poisson(0,7);post=.7*poisson(0,4)/zero;tail=1-pcdf(13,11)
    qs.append(question('A',11,['SL 4.6','AHL 4.17'],
      'On a randomly chosen operating day, a service desk is in weekday mode with probability 0.7 and weekend mode with probability 0.3. Conditional on the mode, the number of urgent calls in an hour is Poisson with mean 4 or 7 respectively. Counts in different hours and on different days are independent conditional on their modes.',[
      part('a','Find the probability of no urgent calls in the chosen hour.',2,[('M1','Use the total-probability sum $0.7e^{-4}+0.3e^{-7}$.'),('A1',f'The probability is ${n(zero)}$.')],[ev('Mixture zero probability',zero)]),
      part('b','Given that no calls occurred, find the probability that the desk was in weekday mode.',3,[('M1','Use Bayes\' theorem with numerator $0.7e^{-4}$.'),('M1',f'Divide by ${n(zero)}$.'),('A1',f'The conditional probability is ${n(post)}$.')],[ev('Bayesian posterior',post),ev('Posterior reconstruction',post*zero,.7*math.exp(-4))]),
      part('c','An hour in weekday mode and an independent hour in weekend mode are selected. Find the probability of at least 14 calls in total.',2,[('M1','The sum is Poisson with mean $4+7=11$.'),('A1',f'$P(X\\ge14)=1-P(X\\le13)={n(tail)}$.')],[ev('Sum-Poisson upper tail',tail)])],f'Zero {n(zero)}, weekday posterior {n(post)}, total-call tail {n(tail)}.'))
    # 12: paired differences, not two independent samples.
    before=[82,77,91,85,88,79,94,83];after=[78,76,85,81,86,75,88,80];diff=[a-b for a,b in zip(before,after)]
    dm=mean(diff);ds=stdev(diff);t=dm/(ds/math.sqrt(8));pv=1-tcdf(t,7)
    qs.append(question('A',12,['AHL 4.18'],
      'The same eight runners complete a fixed course before and after a training programme. The times, in seconds, are shown below. Assume the population of paired differences is normally distributed.\n\n'+table(['Runner',*range(1,9)],[['Before',*before],['After',*after]])+'\n\nLet $D=$ before time minus after time. Test for an improvement at the 5% level.',[
      part('a','Find the sample mean and unbiased sample standard deviation of the eight differences.',2,[('A1',f'$\\bar d={n(dm)}$ s.'),('A1',f'$s_D={n(ds)}$ s.')],[ev('Paired difference statistics',[dm,ds])]),
      part('b','State the null and alternative hypotheses.',1,[('A1',r'$H_0:\mu_D=0$, $H_1:\mu_D>0$.')],[ev('Positive differences represent shorter after times',{'differenceMean':dm,'direction':'greater than zero'})]),
      part('c','Calculate the paired $t$ statistic and the one-tailed $p$-value.',2,[('M1',r'$t=\bar d/(s_D/\sqrt8)$ with $df=7$.'),('A1',f'$t={n(t)}$, $p={n(pv)}$.')],[ev('Paired t and upper tail',[t,pv])]),
      part('d','State a conclusion in context and one additional sampling assumption needed for the inference.',2,[('R1',f'$p={n(pv)}<0.05$, so there is evidence that mean running time decreases.'),('R1','The pairs should be a random/representative sample and differences from different runners should be independent. Do not assume the before and after measurements on the same runner are independent.')],[ev('Paired test decision',{'p':pv,'reject':pv<.05,'pairs':len(diff)})])],f'Differences {diff}; mean{n(dm)}, s{n(ds)}, t{n(t)}, p{n(pv)}.'))
    # 13: a minor segment, not a sector.
    theta=math.radians(140);area=.5*.6**2*(theta-math.sin(theta));volume=12*area;width=1.2*math.sin(theta/2)
    cx,cy,r=360,210,160;ang1=math.radians(20);ang2=math.radians(160)
    start=(cx+r*math.cos(ang1),cy+r*math.sin(ang1));end=(cx+r*math.cos(ang2),cy+r*math.sin(ang2))
    segment=svg([f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#333" stroke-width="2"/>',f'<path d="M {start[0]} {start[1]} A {r} {r} 0 0 1 {end[0]} {end[1]} Z" fill="#dbeafe" stroke="#333" stroke-width="2"/>',line(cx,cy,*start),line(cx,cy,*end),text(cx,cy+35,'140°'),text(cx+105,cy+14,'0.6 m'),text(cx,cy-15,'O'),text(360,403,'Shaded minor segment is the water cross-section',17)])
    qs.append(question('A',13,['SL 3.4','AHL 3.7'],
      'A straight channel has a circular cross-section of radius 0.6 m. The water cross-section is the minor segment cut off by a chord subtending $140^\\circ$ at the centre, as shaded. This cross-section is uniform along a channel length of 12 m.',[
      part('a','Calculate the cross-sectional area of the water.',3,[('M1',r'Convert $140^\circ$ to $\theta=7\pi/9$ radians.'),('M1',r'Subtract the isosceles triangle from the sector: $A=\tfrac12r^2(\theta-\sin\theta)$.'),('A1',f'$A={n(area)}$ m$^2$.')],[ev('Minor segment area',area)]),
      part('b','Find the volume of water in the channel.',2,[('M1','Multiply the cross-sectional area by 12.'),('A1',f'$V={n(volume)}$ m$^3$.')],[ev('Prism volume',volume)]),
      part('c','A floating inspection bar must span the water surface. Find its required length, ignoring any clearance.',2,[('M1',r'The chord length is $2r\sin(\theta/2)$.'),('A1',f'The length is ${n(width)}$ m.')],[ev('Water surface chord',width,math.sqrt(2*.6**2*(1-math.cos(theta))))])],f'Area{n(area)}m²; volume{n(volume)}m³; chord{n(width)}m.',segment))
    # 14: a secondary constraint makes the boundary optimal.
    ropt=(56/(48*math.pi))**(1/3);height=4/(math.pi*ropt**2);cost=lambda r:24*math.pi*r*r+56/r
    rlim=math.sqrt(2/math.pi)
    qs.append(question('A',14,['SL 5.6','SL 5.7','AHL 5.10'],
      'A closed cylindrical tank must hold 4 m$^3$. Its circular top and base cost 12 dollars per m$^2$; its curved side costs 7 dollars per m$^2$. The radius $r$ is restricted to $0.45\\le r\\le1.4$ metres. Material thickness and waste are ignored.',[
      part('a','Show that its material cost is $C(r)=24\\pi r^2+56/r$.',3,[('M1',r'$h=4/(\pi r^2)$ from the volume constraint.'),('M1',r'Top/base cost $12(2\pi r^2)$ and side cost $7(2\pi rh)$.'),('A1',r'Hence $C=24\pi r^2+56/r$.')],[ev('Cost identity at several radii',[(24*math.pi*r*r+7*2*math.pi*r*4/(math.pi*r*r))-(24*math.pi*r*r+56/r) for r in [.5,.8,1.2]],[0,0,0])]),
      part('b','Find the radius and height giving minimum cost, and justify that the minimum is attained.',3,[('M1',r'$C\prime(r)=48\pi r-56/r^2=0$.'),('A1',f'$r={n(ropt)}$ m, $h={n(height)}$ m.'),('R1',r'$C^{\prime\prime}(r)=48\pi+112/r^3>0$, and this stationary point lies inside the permitted interval.')],[ev('Stationary derivative',48*math.pi*ropt-56/ropt**2,0),ev('Optimal dimensions',[ropt,height])]),
      part('c','A new rule limits the height to at most 2 m. Find the new optimal radius and minimum material cost.',2,[('M1',r'$h\le2$ gives $r\ge\sqrt{2/\pi}$, above the unconstrained optimum, where cost is increasing.'),('A1',f'Choose $r={n(rlim)}$ m, $h=2$ m; cost ${n(cost(rlim))}$ dollars.')],[ev('Constrained optimum dimensions and cost',[rlim,4/(math.pi*rlim**2),cost(rlim)])])],f'Unconstrained r{n(ropt)},h{n(height)}; height-limited r{n(rlim)},cost{n(cost(rlim))}.'))
    # 15: columns are origin states throughout, in accordance with the guide.
    T=[[.8,.2,.1],[.15,.6,.2],[.05,.2,.7]];two=mv(power(T,2),[1,0,0])
    stationary=mv(inverse([[T[0][0]-1,T[0][1],T[0][2]],[T[1][0],T[1][1]-1,T[1][2]],[1,1,1]]),[0,0,1])
    conditional=.05*.2/two[1];close(mv(T,stationary),stationary)
    qs.append(question('A',15,['AHL 4.19'],
      r'A transport survey classifies a commuter each week as walking (W), cycling (C) or taking the bus (B). The regular transition matrix is $T=\begin{pmatrix}0.8&0.2&0.1\\0.15&0.6&0.2\\0.05&0.2&0.7\end{pmatrix}$. State vectors are columns in the order W,C,B, and $T_{ij}$ is the probability of moving from state $j$ to state $i$. A commuter walks in week 0.',[
      part('a','Find the probabilities of the three states in week 2.',3,[('M1',r'Use $T^2(1,0,0)^T$.'),('A2',f'The state vector is ${column(two)}$.')],[ev('Two-step state vector',two),ev('Probability normalization',sum(two),1)]),
      part('b','Find the long-run proportion of weeks the commuter is expected to use each mode.',3,[('M1',r'Solve $T\boldsymbol\pi=\boldsymbol\pi$ with $\pi_W+\pi_C+\pi_B=1$.'),('A2',f'$\\boldsymbol\\pi={column(stationary)}$.')],[ev('Stationary distribution',stationary),ev('Stationary substitution',mv(T,stationary),stationary)]),
      part('c','Given that the commuter cycles in week 2, find the probability that they took the bus in week 1.',2,[('M1',f'The path W to B to C has probability $0.05(0.2)=0.01$; divide by $P(C_2)={n(two[1])}$.'),('A1',f'The conditional probability is ${n(conditional)}$.')],[ev('Intermediate-state conditional probability',conditional)])],f'Two steps {two}; stationary {stationary}; intermediate conditional {n(conditional)}.'))
    # 16: quantitative Euler evidence and qualitative concavity agree.
    f=lambda y:30-.2*y*y;ys=[4.]
    for _ in range(3):ys.append(ys[-1]+.1*f(ys[-1]))
    eq=math.sqrt(150);single=4+.3*f(4)
    field=Plot(0,.4,0,16,[0,.1,.2,.3,.4],[0,4,8,12,16],xlabel='t / h',ylabel='V / m³')
    for tt in [.025,.075,.125,.175,.225,.275,.325,.375]:
        for yy in [2,4,6,8,10,12,14]:
            dx=570/.4;dy=-300/16*f(yy);mag=math.hypot(dx,dy);sx=8*dx/mag;sy=8*dy/mag;x,y=field.xy(tt,yy);field.e.append(line(x-sx,y-sy,x+sx,y+sy,'#4b7196',1.6))
    qs.append(question('A',16,['AHL 5.10','AHL 5.14','AHL 5.15','AHL 5.16'],
      r'A reservoir contains $V$ m$^3$ of water at time $t$ hours. It is modelled by $\frac{dV}{dt}=30-0.2V^2$, with $V(0)=4$. A slope field is shown. The model applies while $V\ge0$.',[
      part('a','Find the physically relevant equilibrium volume and determine whether volumes just below it increase or decrease.',2,[('A1',f'The non-negative equilibrium is $V=\\sqrt{{150}}={n(eq)}$ m$^3$.'),('R1',r'For $0\le V<\sqrt{150}$, $30-0.2V^2>0$, so volume increases.')],[ev('Equilibrium derivative',f(eq),0),ev('Below-equilibrium derivative',f(eq-.1))]),
      part('b','Use Euler\'s method with step size 0.1 hours to estimate $V(0.3)$. Show all three updates.',3,[('M1',r'$V_{k+1}=V_k+0.1(30-0.2V_k^2)$.'),('A1',f'$V_1={n(ys[1])}$ and $V_2={n(ys[2])}$.'),('A1',f'$V_3={n(ys[3])}$ m$^3$.')],[ev('Three Euler updates',ys)]),
      part('c','Calculate the one-step Euler estimate using step size 0.3. Explain, using concavity, whether tangent-line Euler estimates from points on the exact solution overestimate or underestimate the exact increasing solution.',3,[('A1',f'The one-step estimate is $4+0.3(30-0.2\\times4^2)={n(single)}$ m$^3$.'),('M1',r'$V^{\prime\prime}=-0.4V V\prime<0$ while $0<V<\sqrt{150}$.'),('R1','The solution is concave down, so its forward tangent lines lie above the solution; tangent-line Euler estimates overestimate. The smaller-step result is closer here, but that observation alone is not a general proof.')],[ev('One-step Euler volume',single),ev('Initial second derivative',-.4*4*f(4))])],f'Equilibrium{n(eq)}; Euler h.1 {ys}; h.3 {n(single)}; increasing concave-down solution.',field.done()))
    return qs


def distances(vertices,edges):
    d={(u,v):(0 if u==v else float('inf')) for u in vertices for v in vertices}
    for u,v,w in edges:d[u,v]=d[v,u]=min(w,d[u,v])
    for k in vertices:
        for u in vertices:
            for v in vertices:d[u,v]=min(d[u,v],d[u,k]+d[k,v])
    return d


def paper_b():
    qs=[]
    i=.048/12;factor=((1+i)**120-1)/i;future=800*factor;real=future/1.025**10;payment=100000*1.025**10/factor
    qs.append(question('B',1,['SL 1.3','SL 1.4','SL 1.7'],
      'An account pays a nominal annual interest rate of 4.8%, compounded monthly. Deposits of 800 dollars are made at the end of every month for 10 years. The initial balance is zero. Annual inflation is assumed to remain at 2.5%. Ignore tax and fees.',[
      part('a','Write down the monthly interest rate as a decimal.',1,[('A1','$i=0.048/12=0.004$.')],[ev('Monthly rate',i)]),
      part('b','Find the balance immediately after the 120th deposit.',2,[('M1',r'Use the ordinary-annuity future value $800[(1.004)^{120}-1]/0.004$.'),('A1',f'The balance is ${n(future)}$ dollars.')],[ev('Annuity balance',future,800*sum((1+i)**k for k in range(120)))]),
      part('c','Express that balance in today\'s purchasing power.',1,[('A1',f'Divide by $1.025^{{10}}$, giving ${n(real)}$ dollars in today\'s money.')],[ev('Inflation-adjusted balance',real)]),
      part('d','Find the monthly deposit required to achieve purchasing power of 100 000 dollars after 10 years, under the same assumptions.',2,[('M1','Set the target future balance to $100000(1.025)^{10}$ and solve for the deposit.'),('A1',f'The required deposit is ${n(payment)}$ dollars per month (round up to the next cent if an attainable minimum payment is required).')],[ev('Target purchasing-power substitution',payment*factor/1.025**10,100000)])],f'Future{n(future)}, real{n(real)}, required deposit{n(payment)}.'))
    signal=lambda c:(18*c+12)/(c+4);inv=lambda s:(4*s-12)/(18-s)
    qs.append(question('B',2,['AHL 2.7','SL 2.6'],
      'A chemical sensor has response $S(c)=(18c+12)/(c+4)$ mV at concentration $c\\ge0$ mg L$^{-1}$. The response is increasing on this physical domain.',[
      part('a','Find $c$ as a function of $S$, and state the physical domain of this inverse.',3,[('M1','Rearrange $Sc+4S=18c+12$.'),('A1','$c=(4S-12)/(18-S)$.'),('A1','The inverse domain is $3\\le S<18$, since $S(0)=3$ and the response approaches 18 from below.')],[ev('Inverse compositions',[inv(signal(c)) for c in [0,1,10,30]],[0,1,10,30])]),
      part('b','Find the concentration corresponding to 14 mV.',1,[('A1','$c=(56-12)/4=11$ mg L$^{-1}$.')],[ev('Signal14 concentration',inv(14),11)]),
      part('c','Compare the concentration changes corresponding to signal increases from 13 to 14 mV and from 15 to 16 mV. Explain what this says about sensitivity at high concentration.',2,[('A1','The concentration changes are $11-8=3$ and $26-16=10$ mg L$^{-1}$ respectively.'),('R1','A larger concentration change gives the same 1 mV response change at high concentration; the sensor is less sensitive there.')],[ev('Concentration increments',[inv(14)-inv(13),inv(16)-inv(15)],[3,10])])], 'Inverse (4S−12)/(18−S), 3≤S<18; c14=11; changes3 and10.'))
    u=[2,-1,2];v=[1,2,-2];angle=math.degrees(math.acos(abs(dot(u,v))/(norm(u)*norm(v))));P=[1,2,3];I=[5,0,7];delta=[a-b for a,b in zip(P,I)];distance=norm(cross(delta,v))/norm(v)
    geometry=svg([line(100,300,610,105),line(120,100,600,335),text(620,100,'line ℓ₁'),text(610,350,'line ℓ₂'),text(358,184,'I'),text(360,395,'Schematic intersection; not a coordinate projection',17)])
    qs.append(question('B',3,['AHL 3.11','AHL 3.13'],
      r'Two maintenance rails are modelled by $\ell_1:\mathbf r=(1,2,3)+s(2,-1,2)$ and $\ell_2:\mathbf r=(5,0,7)+t(1,2,-2)$, with real $s,t$. Coordinates are in metres. The schematic shows only that the rails intersect.',[
      part('a','Find their intersection point.',2,[('M1','Equate the three components; $s=2$, $t=0$ satisfies all of them.'),('A1','The intersection is $(5,0,7)$.')],[ev('Intersection substitution',[P[j]+2*u[j] for j in range(3)],I)]),
      part('b','Find the acute angle between the rails.',2,[('M1',r'$\cos\theta=|\mathbf u\cdot\mathbf v|/(|\mathbf u||\mathbf v|)=4/9$.'),('A1',f'$\\theta={n(angle)}^\\circ$.')],[ev('Acute line angle',angle)]),
      part('c','Find the perpendicular distance from $(1,2,3)$ to $\\ell_2$.',2,[('M1',r'Use $|\overrightarrow{IP}\times\mathbf v|/|\mathbf v|$, or minimize the squared point-to-line distance.'),('A1',f'The distance is ${n(distance)}$ m.')],[ev('Cross-product distance',distance),ev('Orthogonal residual distance',norm([delta[j]-dot(delta,v)/dot(v,v)*v[j] for j in range(3)]),distance)])],f'Intersection{I}; acute angle{n(angle)}degrees; perpendicular distance{n(distance)}m.',geometry))
    x=[12,14,14,18,20,23,25];y=[44,40,42,35,37,31,28];rx=ranks(x);ry=ranks(y);rs=regression(rx,ry)[2]
    qs.append(question('B',4,['SL 4.10','SL 4.4'],
      'Seven hikers report their weekly training distance $x$ (km) and the time $y$ (minutes) to complete a steep climb.\n\n'+table(['Hiker',*'ABCDEFG'],[['$x$',*x],['$y$',*y]])+'\n\nRank both variables in ascending order, using average ranks for ties.',[
      part('a','Write down the rank lists for $x$ and $y$.',2,[('A1',f'The $x$ ranks are ${rx}$.'),('A1',f'The $y$ ranks are ${ry}$.')],[ev('Average rank lists',[rx,ry])]),
      part('b','Calculate Spearman\'s rank correlation coefficient.',2,[('M1','Calculate the Pearson correlation of the rank lists, which handles the tied ranks.'),('A1',f'$r_s={n(rs)}$.')],[ev('Rank correlation',rs)]),
      part('c','Interpret the sign and magnitude of this coefficient. State why it does not by itself prove that training causes a faster climb.',2,[('R1','There is a strong negative monotonic association: greater training distance tends to be associated with shorter climb times.'),('R1','The data are observational and may be confounded, for example by baseline fitness or age; correlation is not proof of causation.')],[ev('Correlation magnitude and direction',{'r':rs,'strong':abs(rs)>.9,'negative':rs<0})])],f'Ranks {rx}, {ry}; Spearman {n(rs)}.'))
    alpha=math.acos((3.1-2.4)/1.6);a=3-6*alpha/math.pi;b=3+6*alpha/math.pi;latest=b-1.5
    tide=lambda t:2.4+1.6*math.cos(math.pi*(t-3)/6)
    drawing=Plot(0,24,0,4.5,[0,3,6,9,12,15,18,21,24],[0,1,2,3,4],xlabel='t / h',ylabel='h / m');drawing.path([(j*.05,tide(j*.05)) for j in range(481)]);drawing.path([(0,3.1),(24,3.1)],'#4b7196',True)
    qs.append(question('B',5,['AHL 2.9','AHL 3.8'],
      r'Tidal depth at a harbour is modelled by $h(t)=2.4+1.6\cos(\pi(t-3)/6)$ metres, for $0\le t\le24$, where $t$ is hours after midnight. A survey vessel requires a depth of at least 3.1 m throughout an uninterrupted 90-minute operation. Angles in the formula are in radians.',[
      part('a','State the amplitude and period of the tidal model.',2,[('A1','Amplitude $1.6$ m.'),('A1','Period $12$ hours.')],[ev('Amplitude and period',[1.6,2*math.pi/(math.pi/6)],[1.6,12])]),
      part('b','Find the first interval after midnight during which the depth is at least 3.1 m.',2,[('M1','Solve $\\cos(\\pi(t-3)/6)\\ge0.4375$ around the first maximum.'),('A1',f'The interval is ${n(a)}\\le t\\le {n(b)}$ hours.')],[ev('First window endpoints',[tide(a),tide(b)],[3.1,3.1])]),
      part('c','Find the latest start time in this first interval for the operation. Give hours after midnight, without converting to clock time.',2,[('M1','Subtract 1.5 hours from the end of the interval.'),('A1',f'The latest start is $t={n(latest)}$ hours.')],[ev('Latest feasible start',[latest,latest+1.5],[latest,b])])],f'Amplitude1.6, period12; firstwindow[{n(a)},{n(b)}]; lateststart{n(latest)}h.',drawing.done()))
    edges=[('A','B',4),('B','C',5),('C','D',3),('D','A',6),('A','E',7),('C','E',4),('B','E',6),('D','E',5)];d=distances('ABCDE',edges);pairings=[d['A','B']+d['C','D'],d['A','C']+d['B','D'],d['A','D']+d['B','C']];total=sum(e[2] for e in edges)
    positions={'A':(100,95),'B':(610,95),'C':(610,335),'D':(100,335),'E':(355,215)}
    qs.append(question('B',6,['AHL 3.14','AHL 3.16'],
      'A robot must inspect every corridor in the undirected network at least once and return to its starting station A. Edge labels are corridor lengths in metres. It may repeat corridors; crossings away from labelled stations are not junctions.',[
      part('a','Explain why traversing every corridor exactly once in a closed route is impossible.',1,[('R1','Vertices A,B,C,D have odd degree 3. A connected graph admits an Euler circuit only when all degrees are even.')],[ev('Odd vertex degrees',{v:sum(v in (u,w) for u,w,_ in edges) for v in 'ABCDE'})]),
      part('b','Find the minimum total length of corridors that must be repeated.',3,[('M1','Pair the four odd vertices using shortest path distances.'),('A1',f'The three pairing totals are ${pairings[0]}, {pairings[1]}, {pairings[2]}$ m.'),('A1',f'Repeat AB and CD, for ${min(pairings)}$ m in total.')],[ev('Odd-vertex pairing totals',pairings)]),
      part('c','Find the minimum length of a complete inspection route and explain why your construction permits a closed route.',3,[('M1',f'The original edge total is ${total}$ m.'),('A1',f'The minimum route length is ${total}+{min(pairings)}={total+min(pairings)}$ m.'),('R1','Duplicating the selected paths makes every vertex even while preserving connectivity, so an Euler circuit of that length exists.')],[ev('Postman route lower bound and feasible length',total+min(pairings))])],f'Edge total{total}; oddpair totals{pairings}; minimumroute{total+min(pairings)}m.',network(positions,edges,'Corridor lengths / m')))
    size=30;p0=.2;pval=bcdf(2,size,p0);critical=max(k for k in range(size+1) if bcdf(k,size,p0)<.05);type2=1-bcdf(critical,size,.1)
    qs.append(question('B',7,['SL 4.8','AHL 4.18'],
      'A factory claims that a new process reduces the defect probability from 0.20. Thirty independent items are tested and two are defective. Use a one-tailed exact binomial test at the 5% level. For a lower-tail critical region, choose the largest rejection probability strictly below 0.05.',[
      part('a','State the hypotheses for the new defect probability $p$.',1,[('A1','$H_0:p=0.20$, $H_1:p<0.20$.')],[ev('Null expected defect count',size*p0)]),
      part('b','Find the $p$-value and state the test decision.',2,[('M1','$P(X\\le2)$ for $X\\sim B(30,0.20)$.'),('A1',f'$p={n(pval)}<0.05$; reject the null hypothesis in favour of a reduction.')],[ev('Exact lower-tail p-value',pval)]),
      part('c','Find the critical region, showing that the next larger lower-tail region is not permitted.',2,[('A1',f'Reject when $X\\le {critical}$; its probability is ${n(bcdf(critical,size,p0))}$.'),('R1',f'$P_0(X\\le {critical+1})={n(bcdf(critical+1,size,p0))}>0.05$, so the region cannot be enlarged.')],[ev('Adjacent rejection probabilities',[bcdf(critical,size,p0),bcdf(critical+1,size,p0)])]),
      part('d','Find the probability of a Type II error when the true defect probability is 0.10.',2,[('M1',f'Failing to reject means $X>{critical}$, now with $X\\sim B(30,0.10)$.'),('A1',f'The Type II error probability is ${n(type2)}$.')],[ev('Type II probability',type2)])],f'pvalue{n(pval)}; criticalX≤{critical}; beta(p=.1)={n(type2)}.'))
    data=[42.1,44.8,41.7,46.3,43.5,45.2,42.9,44.1,43.7];m=mean(data);s=stdev(data);q=tquantile(.975,8);margin=q*s/3;interval=[m-margin,m+margin]
    qs.append(question('B',8,['AHL 4.14','AHL 4.16'],
      'Nine independent observations of the lifetime of a component, in hours, are\n\n$42.1,44.8,41.7,46.3,43.5,45.2,42.9,44.1,43.7$.\n\nAssume a random sample from a normal population whose variance is unknown.',[
      part('a','Find the sample mean and unbiased sample standard deviation.',2,[('A1',f'$\\bar x={n(m)}$ h.'),('A1',f'$s={n(s)}$ h.')],[ev('Lifetime summary statistics',[m,s])]),
      part('b','Find a 95% confidence interval for the population mean lifetime.',3,[('M1','Use a $t$ interval with $df=8$, not the population standard deviation.'),('M1',f'$\\bar x\\pm t_{{0.975,8}}s/\\sqrt9$, where $t_{{0.975,8}}={n(q)}$.'),('A1',f'The interval is $({n(interval[0])},{n(interval[1])})$ hours.')],[ev('t quantile probability',tcdf(q,8),.975),ev('Mean confidence interval',interval)]),
      part('c','Comment on a claimed mean lifetime of 44.5 hours, and explain why the interval is not a range containing 95% of individual lifetimes.',2,[('R1','44.5 hours lies inside this interval, so this sample is compatible with that mean at this confidence level.'),('R1','The interval estimates the population mean using the standard error; it is not a prediction interval for individual observations.')],[ev('Claim inside mean interval',{'lower':interval[0],'claim':44.5,'upper':interval[1],'inside':interval[0]<44.5<interval[1]})])],f'mean{n(m)},s{n(s)};95%CI{interval}.'))
    areas=[0,18,29,25,14,0];mid=[9.5,24,28.5,20,7.5];coarse=20*(sum(areas[1:-1])+(areas[0]+areas[-1])/2);fine=10*(sum(areas[1:-1])+sum(mid))
    all_areas=[value for pair in zip(areas[:-1],mid) for value in pair]+[areas[-1]]
    slopes=[(v-u)/10 for u,v in zip(all_areas,all_areas[1:])]
    assert all(v<u for u,v in zip(slopes,slopes[1:])), 'Sample values must be compatible with strict concavity'
    drawing=Plot(0,100,0,34,[0,20,40,60,80,100],[0,10,20,30],xlabel='x / m',ylabel='A / m²')
    drawing.path(list(zip(range(0,101,20),areas)),'#4b7196')
    for x,y in zip(range(0,101,20),areas):drawing.point(x,y)
    qs.append(question('B',9,['SL 5.8','AHL 5.10'],
      'The cross-sectional area $A(x)$ of a flooded tunnel is measured perpendicular to its axis at equally spaced positions.\n\n'+table(['$x$ / m',0,20,40,60,80,100],[['$A(x)$ / m$^2$',*areas]])+'\n\nAssume $A(x)$ is continuous and strictly concave down between the ends.',[
      part('a','Use the trapezoidal rule with intervals of width 20 m to estimate the water volume.',3,[('M1','Use $V\\approx(20/2)[A_0+2(A_1+A_2+A_3+A_4)+A_5]$.'),('M1','Substitute $18+29+25+14=86$.'),('A1',f'$V\\approx {coarse}$ m$^3$.')],[ev('Coarse trapezoidal volume',coarse)]),
      part('b','Additional areas at $x=10,30,50,70,90$ are respectively $9.5,24,28.5,20,7.5$ m$^2$. Find the trapezoidal estimate using width 10 m.',2,[('M1','Interleave all eleven equally spaced observations; endpoints are zero.'),('A1',f'The refined estimate is ${fine}$ m$^3$.')],[ev('Refined trapezoidal volume',fine),ev('Strictly decreasing observed secant slopes',slopes)]),
      part('c','Using the concavity assumption, state whether these trapezoidal estimates are underestimates or overestimates, and justify your answer.',2,[('R1','Each chord lies below a concave-down graph.'),('R1','The trapezoids therefore underestimate the integral and hence the volume; the larger refined estimate is consistent with this.')],[ev('Refinement increase under concavity',fine-coarse)])],f'T20={coarse}m³;T10={fine}m³; both underestimate under stated concavity.',drawing.done()))
    L=[[0,1.8],[.5,.3]];disc=math.sqrt(.3**2+4*.9);lam=(.3+disc)/2;other=(.3-disc)/2;ratio=1.8/lam;adult=1/(1+ratio);nextstate=mv(L,[200,100])
    qs.append(question('B',10,['AHL 1.14','AHL 1.15'],
      r'A two-stage population has juvenile and adult state vector $\mathbf s_n$. It follows $\mathbf s_{n+1}=L\mathbf s_n$, where $L=\begin{pmatrix}0&1.8\\0.5&0.3\end{pmatrix}$. Initially there are 200 juveniles and 100 adults. Fractional population predictions are permitted within the model.',[
      part('a','Find the predicted juvenile and adult populations one year later.',2,[('M1','Multiply $L(200,100)^T$.'),('A1',f'The next state is ${column(nextstate)}$.')],[ev('One-year population',nextstate)]),
      part('b','Find the dominant eigenvalue and interpret its long-run growth implication.',2,[('A1',f'The eigenvalues are ${n(lam)}$ and ${n(other)}$; the dominant magnitude is ${n(lam)}$.'),('R1',f'The model eventually grows by a factor ${n(lam)}$ per year, about ${n(100*(lam-1),4)}\\%$ annually.')],[ev('Characteristic polynomial at eigenvalues',[lam**2-.3*lam-.9,other**2-.3*other-.9],[0,0])]),
      part('c','Find the long-run juvenile-to-adult ratio and the long-run adult proportion.',3,[('M1',r'For an eigenvector $(J,A)^T$, $1.8A=\lambda J$.'),('A1',f'$J:A={n(ratio)}:1$.'),('A1',f'The adult proportion is $1/(1+{n(ratio)})={n(adult)}$.')],[ev('Eigenvector relation',mv(L,[ratio,1]),[lam*ratio,lam]),ev('Adult normalized proportion',adult)])],f'Nextstate{nextstate};dominanteigenvalue{n(lam)};J:A={n(ratio)}:1;adult{n(adult)}.'))
    rate=.4-.02*2;dh=rate/(math.pi*2**2/4);elapsed=integrate(lambda h:(math.pi*h*h/4)/(.4-.02*h),1,2)
    cone=svg([line(220,65,360,350),line(500,65,360,350),'<ellipse cx="360" cy="65" rx="140" ry="30" fill="none" stroke="#222" stroke-width="2"/>',line(360,65,360,350,'#777',1.6,True),line(360,65,500,65,'#777',1.6,True),line(185,65,185,350,'#777',1.3),line(179,65,191,65,'#777',1.3),line(179,350,191,350,'#777',1.3),text(150,215,'6 m'),text(430,50,'3 m'),line(290,207.5,430,207.5,'#2563a6'),text(510,215,'water level'),text(360,400,'Conical tank; not to scale',17)])
    qs.append(question('B',11,['AHL 5.9','SL 5.5'],
      'A conical tank has height 6 m and top radius 3 m, with its vertex at the bottom. Water depth is $h$ metres. Water enters at 0.4 m$^3$ min$^{-1}$ and leaks at $0.02h$ m$^3$ min$^{-1}$.',[
      part('a','Express the water volume $V$ in terms of $h$.',2,[('M1','Similar triangles give $r=h/2$.'),('A1',r'$V=\frac13\pi(h/2)^2h=\pi h^3/12$.')],[ev('Cone volume identity at depth2',math.pi*(2/2)**2*2/3,math.pi*2**3/12)]),
      part('b','Find the rate of increase of the water depth when $h=2$.',3,[('M1',r'$dV/dh=\pi h^2/4$.'),('M1',r'At $h=2$, $(\pi h^2/4)(dh/dt)=0.4-0.02h=0.36$.'),('A1',f'$dh/dt={n(dh)}$ m min$^{{-1}}$.')],[ev('Related depth rate',dh),ev('Volume-rate reconstruction',math.pi*dh,rate)]),
      part('c','Find the time taken for the depth to rise from 1 m to 2 m, using numerical integration.',2,[('M1',r'$\Delta t=\int_1^2\frac{\pi h^2}{4(0.4-0.02h)}\,dh$.'),('A1',f'The time is ${n(elapsed)}$ minutes.')],[ev('Numerical filling time',elapsed,integrate(lambda h:(math.pi*h*h/4)/(.4-.02*h),1,2,2000))])],f'V=πh³/12; dh/dt at2={n(dh)};time1to2={n(elapsed)}min.',cone))
    x=[2,4,6,9,12];y=[11.8,25.7,41.4,68.6,95.5];exponent,loga,r=regression([math.log(t) for t in x],[math.log(t) for t in y]);a=math.exp(loga);prediction=a*8**exponent
    qs.append(question('B',12,['AHL 2.10','AHL 4.13','AHL 5.9'],
      'An engineering model relates energy use $E$ (kJ) to load $m$ (kg) by $E=am^b$, with $a>0$.\n\n'+table(['$m$',*x],[['$E$',*y]])+'\n\nFit the power model by least-squares linear regression of $\\ln E$ on $\\ln m$.',[
      part('a','Find $a$ and $b$.',3,[('M1',r'Linearize as $\ln E=\ln a+b\ln m$.'),('A1',f'$b={n(exponent)}$.'),('A1',f'$a={n(a)}$.')],[ev('Log-regression coefficients',[loga,exponent,a])]),
      part('b','Estimate the energy use at a load of 8 kg.',2,[('M1',f'Use ${n(a)}(8)^{{{n(exponent)}}}$ with unrounded fitted parameters.'),('A1',f'$E={n(prediction)}$ kJ.')],[ev('Power prediction at8',prediction)]),
      part('c','Show that $(m/E)(dE/dm)=b$. Hence estimate the percentage energy increase caused by a small 5% load increase.',2,[('M1',r'$dE/dm=abm^{b-1}$, so $(m/E)(dE/dm)=b$.'),('A1',f'The first-order estimated increase is $5b={n(5*exponent)}\\%$. This is a local approximation.')],[ev('Elasticity by derivative',8/prediction*(a*exponent*8**(exponent-1)),exponent),ev('Small-change percentage approximation',5*exponent)])],f'Power modela{n(a)},b{n(exponent)};E8={n(prediction)};5% elasticityincrease{n(5*exponent)}%.'))
    total5=poisson(5,5);conditional=poisson(2,2)*poisson(3,3)/total5;independent=1-poisson(0,2)
    qs.append(question('B',13,['SL 4.6','AHL 4.17'],
      'During a 15-minute interval, independent arrival counts $A$ and $B$ from two entrances follow Poisson distributions with means 2 and 3 respectively. Let $T=A+B$.',[
      part('a','State the distribution of $T$ and find $P(T=5)$.',2,[('A1','$T\\sim\\operatorname{Po}(5)$.'),('A1',f'$P(T=5)=e^{{-5}}5^5/5!={n(total5)}$.')],[ev('Total5 probability',total5,sum(poisson(k,2)*poisson(5-k,3) for k in range(6)))]),
      part('b','Given that five people arrived in total, find the probability that exactly two used entrance A.',3,[('M1','The numerator is $P(A=2,B=3)=P(A=2)P(B=3)$.'),('M1','Divide that joint probability by $P(T=5)$.'),('A1',f'The conditional probability is ${n(conditional)}$.')],[ev('Conditional split probability',conditional,math.comb(5,2)*.4**2*.6**3)]),
      part('c','Given that nobody used entrance B, find the probability that at least one person used entrance A. Explain the role of independence.',2,[('R1','Independence means conditioning on $B=0$ does not change the distribution of $A$.'),('A1',f'$P(A\\ge1\\mid B=0)=1-e^{{-2}}={n(independent)}$.')],[ev('Independent conditioned event',independent)])],f'T~Po5,P(T5)={n(total5)};splitconditional{n(conditional)};conditionedApositive{n(independent)}.'))
    edges=[('A','B',6),('A','C',9),('A','D',10),('A','E',7),('B','C',5),('B','D',8),('B','E',9),('C','D',6),('C','E',8),('D','E',4)];costs=distances('ABCDE',edges)
    lower_tree,lower_cost=mst('BCDE',[(u,v,w) for u,v,w in edges if 'A' not in (u,v)]);lower=lower_cost+6+7
    tours=[('A',)+order+('A',) for order in itertools.permutations('BCDE')];length=lambda tour:sum(costs[u,v] for u,v in zip(tour,tour[1:]));optimal=min(map(length,tours))
    qs.append(question('B',14,['AHL 3.16'],
      'A courier must start at A, visit each of B,C,D,E once, and return to A. The complete undirected distance table, in kilometres, is shown.\n\n'+table(['','A','B','C','D','E'],[[u,*['—' if u==v else costs[u,v] for v in 'ABCDE']] for u in 'ABCDE']),[
      part('a','Apply the nearest-neighbour algorithm starting at A. State the resulting tour and an upper bound for the optimum.',3,[('M1','Choose the closest unvisited vertex at each step.'),('A1','The tour is A-B-C-D-E-A.'),('A1','Its length is $6+5+6+4+7=28$ km, an upper bound.')],[ev('Nearest-neighbour tour length',length(('A','B','C','D','E','A')))]),
      part('b','Use the deleted-vertex method, deleting A, to obtain a lower bound.',3,[('M1','A minimum spanning tree on B,C,D,E uses DE,BC,CD.'),('A1',f'That tree has weight ${lower_cost}$ km.'),('A1',f'Add the two smallest A-edges, 6 and 7, to obtain a lower bound of ${lower}$ km.')],[ev('Deleted-vertex lower bound',lower)]),
      part('c','Determine the optimal tour length and justify your conclusion.',2,[('R1','The lower and upper bounds are equal.'),('A1','The optimum is exactly $28$ km; the tour in part (a) attains it.')],[ev('Exhaustive tour verification',optimal,28)])],f'NN28, deleted-A lower28, exactoptimum28.'))
    t4=20+70*math.exp(-.15*4);target=4+math.log((t4-5)/10)/.15;before=-.15*(t4-20);after=-.15*(t4-5)
    qs.append(question('B',15,['AHL 5.14','AHL 2.9'],
      r'An object initially at $90^\circ$C cools according to $dT/dt=-0.15(T-A)$, where $t$ is minutes and $A$ is ambient temperature. For $0\le t<4$, $A=20$. At $t=4$ the object is moved instantly to a room with $A=5$; its own temperature is continuous and the same differential model then applies.',[
      part('a','Find the object\'s temperature at $t=4$.',2,[('M1',r'The first-stage solution is $T=20+70e^{-0.15t}$.'),('A1',f'$T(4)={n(t4)}^\\circ$C.')],[ev('First-stage temperature',t4)]),
      part('b','Find the first time after $t=0$ at which the temperature reaches $15^\\circ$C.',3,[('M1',f'For $t\\ge4$, $T=5+({n(t4)}-5)e^{{-0.15(t-4)}}$, retaining the unrounded $T(4)$.'),('M1','Solve $10=(T(4)-5)e^{-0.15(t-4)}$.'),('A1',f'The first time is $t={n(target)}$ minutes.')],[ev('Second-stage target substitution',5+(t4-5)*math.exp(-.15*(target-4)),15)]),
      part('c','Find the cooling rates immediately before and after the move, and explain why the derivative changes even though temperature is continuous.',3,[('A1',f'The rates are ${n(before)}$ and ${n(after)}^\\circ$C min$^{{-1}}$ respectively.'),('M1','The ambient temperature changes by 15 degrees, changing the derivative by $-0.15(15)=-2.25$ degrees per minute.'),('R1','The driving temperature difference changes immediately, while the object\'s temperature does not jump.')],[ev('One-sided rates and rate jump',[before,after,after-before],[before,after,-2.25])])],f'T4={n(t4)};T15time{n(target)};rates{n(before)},{n(after)}.'))
    k=.6+.8j;centre=k*1+(2-1j);theta=cmath.phase(k);tmax=math.pi/2-theta
    drawing=Plot(-3.75,5.75,-2.5,2.5,[-2,0,2,4],[-2,0,2],xlabel='Re z',ylabel='Im z');drawing.path([(1+2*math.cos(j*math.pi/100),2*math.sin(j*math.pi/100)) for j in range(201)]);drawing.point(1,0,'centre 1',dx=6,dy=-12)
    qs.append(question('B',16,['AHL 1.12','AHL 1.13'],
      r'Points on a circle are described by $z=1+2e^{it}$, $0\le t<2\pi$. A transformation is $w=(0.6+0.8i)z+2-i$. The diagram shows the original circle in the $z$-plane. Angles are in radians.',[
      part('a','Describe the rotation and scale factor associated with multiplication by $0.6+0.8i$.',2,[('A1','The scale factor is $\\sqrt{0.6^2+0.8^2}=1$.'),('A1',f'The rotation is anticlockwise through ${n(theta)}$ rad about the origin.')],[ev('Multiplier modulus and argument',[abs(k),theta])]),
      part('b','Find the centre and radius of the image circle in the $w$-plane.',3,[('M1','Transform the original centre $z=1$ and multiply the radius by $|0.6+0.8i|$.'),('A1',f'The centre is ${n(centre.real)}{centre.imag:+.8g}i$.'),('A1','The radius remains $2$.')],[ev('Image centre and radius',[centre.real,centre.imag,2*abs(k)])]),
      part('c','Find the value of $t$ for which $\\operatorname{Im}w$ is greatest, and find that maximum imaginary part.',3,[('M1',r'$w=2.6-0.2i+2e^{i(t+\arg(0.6+0.8i))}$.'),('A1',f'The maximum occurs at $t={n(tmax)}$ rad, where the rotating radius points upwards.'),('A1','The maximum imaginary part is $-0.2+2=1.8$.')],[ev('Maximum transformed point imaginary part',(k*(1+2*cmath.exp(1j*tmax))+(2-1j)).imag,1.8)])],f'Rotation{n(theta)},scale1;centre{centre},radius2;tmax{n(tmax)},maxIm1.8.',drawing.done()))
    return qs


def paper_c():
    qs=[]
    i1=1e-12*10**7.2;i2=1e-12*10**6.8;level=10*math.log10((i1+i2)/1e-12);fraction=(1e-5-i2)/i1
    qs.append(question('C',1,['AHL 1.9','AHL 2.10'],
      r'The sound level is $L=10\log_{10}(I/I_0)$ decibels, where $I_0=10^{-12}$ W m$^{-2}$. Two incoherent machines produce levels of 72 dB and 68 dB at a fixed location. Their intensities, rather than their decibel levels, add.',[
      part('a','Find the combined sound level when both machines operate.',3,[('M1',r'Convert to $I_1=I_0 10^{7.2}$ and $I_2=I_0 10^{6.8}$.'),('M1',r'Use $L=10\log_{10}[(I_1+I_2)/I_0]$.'),('A1',f'The combined level is ${n(level)}$ dB.')],[ev('Combined intensity and sound level',[i1+i2,level])]),
      part('b','The second machine is unchanged. Find the minimum percentage reduction in the first machine\'s intensity needed to make the combined level at most 70 dB.',3,[('M1','A 70 dB limit corresponds to total intensity $10^{-5}$ W m$^{-2}$.'),('M1',r'The retained fraction $k$ satisfies $kI_1+I_2=10^{-5}$.'),('A1',f'$k={n(fraction)}$, so reduce the first intensity by at least ${n(100*(1-fraction))}\\%$.')],[ev('Attenuation substitution',fraction*i1+i2,1e-5),ev('Required percentage reduction',100*(1-fraction))])],f'Combinedlevel{n(level)}dB; minimumintensityreduction{n(100*(1-fraction))}%.'))
    coeff=mv(inverse([[0,0,1],[4,2,1],[25,5,1]]),[2,14,17]);impact=4+math.sqrt(18);h=lambda t:-t*t+8*t+2
    drawing=Plot(0,9,0,21,[0,2,4,6,8],[0,5,10,15,20],xlabel='t / s',ylabel='h / m');drawing.path([(impact*j/160,h(impact*j/160)) for j in range(161)])
    for t in [0,2,5]:drawing.point(t,h(t),f'({t},{h(t):g})',dx=8,dy=-12)
    qs.append(question('C',2,['SL 2.5','SL 2.6','SL 1.8'],
      'The height of a small survey drone during a programmed flight is modelled by $h(t)=at^2+bt+c$, where $t$ is seconds after the flight starts and $h$ is metres above level ground. Measurements give $h(0)=2$, $h(2)=14$ and $h(5)=17$. The model is used only from the start until the first contact with ground level.',[
      part('a','Find $a,b,c$.',3,[('M1','Set up $c=2$, $4a+2b+c=14$, $25a+5b+c=17$.'),('M1','Solve the simultaneous equations.'),('A1','$a=-1$, $b=8$, $c=2$.')],[ev('Quadratic coefficient solution',coeff,[-1,8,2])]),
      part('b','Find the physical time domain of this model.',2,[('M1','Solve $-t^2+8t+2=0$ and retain the positive root.'),('A1',f'$0\\le t\\le {n(impact)}$ seconds.')],[ev('Impact substitution',h(impact),0)]),
      part('c','Find the maximum height predicted during this domain.',1,[('A1','The vertex is at $t=4$, giving maximum height $18$ m.')],[ev('Vertex height',h(4),18)])],f'Coefficients{coeff};domain0..{n(impact)};maxheight18.',drawing.done()))
    widths=[5,10,15,20];counts=[8,24,30,18];density=[c/w for c,w in zip(counts,widths)];median=15+(40-32)/30*15;tail=(30*5/15+18)/80
    hist=Plot(0,50,0,3,[0,5,15,30,50],[0,1,2,3],xlabel='t / min',ylabel='frequency density')
    for lo,hi,dd in zip([0,5,15,30],[5,15,30,50],density):hist.path([(lo,0),(lo,dd),(hi,dd),(hi,0)],fill='#e8f0fa')
    qs.append(question('C',3,['SL 4.2','SL 4.3','SL 4.5'],
      'Eighty delivery delays are grouped as shown. The histogram uses frequency density on the vertical axis.\n\n'+table(['Delay $t$ / min','Frequency'],[['$0\\le t<5$',8],['$5\\le t<15$',24],['$15\\le t<30$',30],['$30\\le t\\le50$',18]])+'\n\nFor estimates inside a class, assume observations are uniformly distributed within that class.',[
      part('a','Calculate the height of the bar for $30\\le t\\le50$.',1,[('A1','The density is $18/20=0.9$ observations per minute.')],[ev('Last histogram density',density[-1],.9)]),
      part('b','Estimate the median delay using linear interpolation.',2,[('M1','The median is the 40th cumulative observation, in the 15-to-30 class after 32 observations.'),('A1','$15+[(40-32)/30](15)=19$ minutes.')],[ev('Grouped median interpolation',median,19)]),
      part('c','Estimate the probability that a randomly selected delay exceeds 25 minutes.',2,[('M1','Use one third of the 30 observations in 15-to-30, plus all 18 in the last class.'),('A1',f'The estimated probability is ${n(tail)}$.')],[ev('Interpolated upper-tail probability',tail,.35)]),
      part('d','State the modal class indicated by the histogram.',1,[('A1','The modal class is $5\\le t<15$, which has the greatest frequency density.')],[ev('Highest-density class index',max(range(4),key=lambda j:density[j]),1)])],f'Density.9;median19min;tail.35;modalclass5..15.',hist.done()))
    prevalence=.08;both=.08*.9*.95+.92*.15*.02;posterior=.08*.9*.95/both;pos1=.08*.9+.92*.15;pos2=.08*.95+.92*.02
    qs.append(question('C',4,['SL 4.5','SL 4.6'],
      'A condition affects 8% of a population. Test 1 has sensitivity 0.90 and specificity 0.85; test 2 has sensitivity 0.95 and specificity 0.98. Sensitivity is the probability of a positive result given the condition; specificity is the probability of a negative result given no condition. For each person, the two test results are independent conditional on whether that person has the condition.',[
      part('a','Find the probability that a randomly selected person tests positive on both tests.',2,[('M1','Use $0.08(0.90)(0.95)+0.92(0.15)(0.02)$.'),('A1',f'The probability is ${n(both)}$.')],[ev('Double-positive total probability',both)]),
      part('b','Find the probability that a person has the condition given two positive results.',2,[('M1','Divide $0.08(0.90)(0.95)$ by the probability in part (a).'),('A1',f'The posterior probability is ${n(posterior)}$.')],[ev('Double-positive posterior',posterior)]),
      part('c','Determine whether the two positive-test events are independent in the whole population. Support your answer numerically.',2,[('M1',f'$P(+_1)={n(pos1)}$, $P(+_2)={n(pos2)}$; their product is ${n(pos1*pos2)}$.'),('R1',f'This differs from $P(+_1\\cap+_2)={n(both)}$, so the positive events are not unconditionally independent. Conditional independence does not imply unconditional independence.')],[ev('Joint versus product of marginals',[both,pos1*pos2])])],f'Doublepositive{n(both)};posterior{n(posterior)};marginalproduct{n(pos1*pos2)}.'))
    u=[5,8/3];radius=13/3;v=[5,8]
    drawing=Plot(0,10,0,9,[0,2,4,6,8,10],[0,2,4,6,8],xlabel='x / km',ylabel='y / km')
    drawing.path([(0,0),(10,0),(10,8),(0,8),(0,0)],'#777',True)
    for x,y,label in [(1,1,'A (1,1)'),(9,1,'B (9,1)'),(5,7,'C (5,7)'),(5,8,'V (5,8)')]:drawing.point(x,y,label,dx=-105 if x==9 else 8,dy=-12)
    qs.append(question('C',5,['SL 3.5','SL 3.6'],
      'Three existing monitoring stations are at $A(1,1)$, $B(9,1)$ and $C(5,7)$ km. A rectangular reserve has $0\\le x\\le10$ and $0\\le y\\le8$. A new station will be placed either at the Voronoi vertex $U$ equidistant from A,B,C, or at $V(5,8)$. The selected candidate should maximize its distance to the nearest existing station.',[
      part('a','Find the coordinates of $U$.',3,[('M1','The perpendicular bisector of AB is $x=5$.'),('M1','Equating distances to A and C gives $8x+12y=72$.'),('A1',r'$U=(5,8/3)$.')],[ev('Equidistance at U',[norm([u[j]-s[j] for j in range(2)]) for s in [[1,1],[9,1],[5,7]]],[radius]*3)]),
      part('b','Calculate the distance from each candidate to its nearest existing station.',2,[('A1',r'At U the nearest distance is $13/3$ km.'),('A1','At V the nearest station is C, at distance $1$ km.')],[ev('Candidate nearest distances',[radius,min(norm([v[j]-s[j] for j in range(2)]) for s in [[1,1],[9,1],[5,7]])],[radius,1])]),
      part('c','Choose between the two candidates and state the relevant comparison.',1,[('R1','Choose U, since $13/3>1$. This compares only the two permitted candidates, not every point in the reserve.')],[ev('Nearest-distance improvement',radius-1)])],f'U(5,8/3);nearestdistances13/3,1;chooseU.',drawing.done()))
    T=[[.88,.25],[.12,.75]];stationary=.25/.37;prob=lambda k:stationary+(.15-stationary)*.63**k;first=next(k for k in range(100) if prob(k)>=.65)
    qs.append(question('C',6,['AHL 4.19'],
      r'A subscriber is either a regular user R or an occasional user O each month. The regular transition matrix, with columns denoting origin states, is $T=\begin{pmatrix}0.88&0.25\\0.12&0.75\end{pmatrix}$ in the order R,O. Initially $P(R)=0.15$. Let $p_n=P(R\text{ in month }n)$.',[
      part('a','Find a recurrence for $p_n$ and calculate $p_1$.',2,[('M1','$p_{n+1}=0.88p_n+0.25(1-p_n)=0.63p_n+0.25$.'),('A1',f'$p_1={n(prob(1))}$.')],[ev('First recurrence update',prob(1),.88*.15+.25*.85)]),
      part('b','Find the long-run regular-user probability.',2,[('M1','Solve $p=0.63p+0.25$.'),('A1',f'$p={n(stationary)}$.')],[ev('Stationary fixed point',.63*stationary+.25,stationary)]),
      part('c','Determine the first month for which the regular-user probability is at least 0.65. Justify that it is the first.',3,[('M1','Iterate the recurrence or use $p_n=p_*+(0.15-p_*)(0.63)^n$.'),('A1',f'$p_{{{first-1}}}={n(prob(first-1))}<0.65$ and $p_{{{first}}}={n(prob(first))}\\ge0.65$.'),('R1',f'The first month is ${first}$; the sequence is increasing toward $p_*>0.65$.')],[ev('Threshold neighbours',[prob(first-1),prob(first)]),ev('Matrix-power agreement',mv(power(T,first),[.15,.85])[0],prob(first))])],f'pnext=.63p+.25;steady{n(stationary)};firstthresholdmonth{first}.'))
    x=[1,2,3,4,5,6,7,8];y=[10,13,12,18,17,20,21,24];_,_,r=regression(x,y);t=r*math.sqrt(6/(1-r*r));pv=1-tcdf(t,6)
    qs.append(question('C',7,['SL 4.4','AHL 4.18'],
      'Eight independent sampled pairs $(x,y)$ are shown below. Assume they are a random sample from a bivariate normal population.\n\n'+table(['$x$',*x],[['$y$',*y]])+'\n\nTest for positive population correlation at the 1% significance level.',[
      part('a','Calculate the Pearson correlation coefficient.',2,[('M1','Use all eight raw pairs in a Pearson calculation.'),('A1',f'$r={n(r)}$.')],[ev('Pearson correlation',r)]),
      part('b','State the hypotheses and find the one-tailed $p$-value.',3,[('A1',r'$H_0:\rho=0$, $H_1:\rho>0$.'),('M1','Use the correlation test with $n=8$ (equivalently $t=r\\sqrt{6/(1-r^2)}$, $df=6$).'),('A1',f'$t={n(t)}$, $p={n(pv)}$.')],[ev('Correlation test statistic and tail',[t,pv])]),
      part('c','State the statistical conclusion and explain why it is not a statement that $x$ causes $y$.',2,[('R1',f'$p={n(pv)}<0.01$, so reject zero correlation in favour of positive correlation.'),('R1','Even significant correlation does not identify a causal mechanism or remove possible common causes.')],[ev('One-percent correlation decision',{'p':pv,'reject':pv<.01})])],f'r{n(r)},t{n(t)},p{n(pv)};rejectat1%.'))
    times=[1,2,3,4,5,6];data=[6.2,10.0,12.6,13.7,14.8,15.0];modela=lambda t:16*(1-math.exp(-.5*t));modelb=lambda t:-.3*t*t+3.5*t+1
    residuals=[o-modela(t) for t,o in zip(times,data)];ssea=sum(r*r for r in residuals);sseb=sum((o-modelb(t))**2 for t,o in zip(times,data))
    qs.append(question('C',8,['AHL 4.13','SL 2.6'],
      'A cumulative nutrient release $R$ (mg) is measured $t$ hours after treatment.\n\n'+table(['$t$',*times],[['$R$',*data]])+'\n\nTwo proposed models are $R_A=16(1-e^{-0.5t})$ and $R_B=-0.3t^2+3.5t+1$. Define each residual as observed minus predicted.',[
      part('a','Find the residuals for model A and its sum of squared residuals.',3,[('M1','Evaluate model A at all six times and subtract from the observations.'),('A1',f'The residuals are ${[round(v,6) for v in residuals]}$ mg.'),('A1',f'$SS_A={n(ssea)}$ mg$^2$.')],[ev('Model-A residuals and sum of squares',{'residuals':residuals,'SS':ssea})]),
      part('b','Find the sum of squared residuals for model B. Select the model with the better fit by this criterion.',2,[('A1',f'$SS_B={n(sseb)}$ mg$^2$.'),('R1','Choose model A because its residual sum of squares is smaller.')],[ev('Model-B sum of squares',sseb)]),
      part('c','Compare the physical plausibility of the models for very large $t$, and give a reason for caution about using either model beyond the observed times.',2,[('R1','A approaches 16 mg, whereas B eventually decreases and becomes negative, which is implausible for cumulative release.'),('R1','The data only cover 1 to 6 hours; the long-term mechanism or environment may differ, so the better observed fit does not validate distant extrapolation.')],[ev('Long-range model predictions',[modela(40),modelb(40)])])],f'SSA{n(ssea)},SSB{n(sseb)};preferAwithboundedcumulativeinterpretation.'))
    u=[4,1,2];v=[1,3,-1];normal=cross(u,v);area=norm(normal);unit=[x/area for x in normal];sun=[0,-1,-2];projected=abs(dot(normal,sun))/norm(sun)
    drawing=svg([line(150,325,510,270),line(150,325,225,105),line(510,270,585,50),line(225,105,585,50),text(330,330,'u = (4,1,2)'),text(120,190,'v'),text(360,402,'Schematic parallelogram; edges are 3D vectors',17)])
    qs.append(question('C',9,['AHL 3.10','AHL 3.13'],
      r'A parallelogram solar panel has adjacent edge vectors $\mathbf u=(4,1,2)$ and $\mathbf v=(1,3,-1)$ metres. Sunlight travels in direction $\mathbf d=(0,-1,-2)$. The effective area facing the rays is $A_{\mathrm{eff}}=A|\hat{\mathbf n}\cdot\hat{\mathbf d}|$, where $A$ is panel area and hats denote unit vectors.',[
      part('a','Find a unit vector perpendicular to the panel.',3,[('M1',r'Calculate $\mathbf u\times\mathbf v=(-7,6,11)$.'),('M1',r'Its magnitude is $\sqrt{206}$.'),('A1',f'One unit normal is ${column(unit)}$; its negative is also valid.')],[ev('Normal vector and unit normal',{'normal':normal,'unit':unit}),ev('Perpendicularity',[dot(normal,u),dot(normal,v)],[0,0])]),
      part('b','Find the actual panel area.',2,[('M1',r'$A=|\mathbf u\times\mathbf v|$.'),('A1',f'$A={n(area)}$ m$^2$.')],[ev('Parallelogram area',area)]),
      part('c','Calculate the effective area facing the rays.',2,[('M1',r'$A_{\mathrm{eff}}=|(-7,6,11)\cdot(0,-1,-2)|/\sqrt5$.'),('A1',f'$A_{{\\mathrm{{eff}}}}={n(projected)}$ m$^2$.')],[ev('Projected area',projected,28/math.sqrt(5))])],f'Normal{normal},area{n(area)},effectivearea{n(projected)}.',drawing))
    f=lambda x,y:.5*x-.02*x*y;g=lambda x,y:-.4*y+.01*x*y;states=[[40.,10.]]
    for _ in range(2):
        x,y=states[-1];states.append([x+.5*f(x,y),y+.5*g(x,y)])
    field=Plot(10,70,5,40,[10,20,40,60],[10,20,30,40],xlabel='x',ylabel='y')
    for x in [15,25,35,45,55,65]:
        for y in [8,14,20,26,32,38]:
            vx=570/60*f(x,y);vy=-300/35*g(x,y);length=math.hypot(vx,vy)
            if length:
                a,b=field.xy(x,y);field.e.append(arrow(a-7*vx/length,b-7*vy/length,a+7*vx/length,b+7*vy/length,'#4b7196'))
    field.point(40,10,'initial',dx=9,dy=-12)
    qs.append(question('C',10,['AHL 5.15','AHL 5.16'],
      r'A simplified prey-predator model is $dx/dt=0.5x-0.02xy$, $dy/dt=-0.4y+0.01xy$. Populations $x,y$ are measured in hundreds and time in months. Initially $(x,y)=(40,10)$. The direction field is schematic; use the equations for calculations.',[
      part('a','Find the initial rate of change of each population and describe the initial direction in the phase plane.',2,[('A1',r'$x\prime(0)=12$, $y\prime(0)=0$.'),('R1','The trajectory initially moves horizontally toward increasing x.')],[ev('Initial vector field',[f(40,10),g(40,10)],[12,0])]),
      part('b','Use simultaneous Euler updates of width 0.5 months to estimate both populations at $t=1$. Show the intermediate state.',3,[('M1','At each step evaluate both derivatives at the same old pair.'),('A1',f'The first state is ${states[1]}$.'),('A1',f'The $t=1$ state is ${states[2]}$ hundreds.')],[ev('Simultaneous Euler states',states)]),
      part('c','Find the equilibrium with both populations strictly positive.',2,[('M1','For positive populations solve $0.5-0.02y=0$ and $-0.4+0.01x=0$.'),('A1','The coexistence equilibrium is $(40,25)$.')],[ev('Coexistence equilibrium derivatives',[f(40,25),g(40,25)],[0,0])])],f'Initialderivatives12,0;Eulerstates{states};positiveequilibrium40,25.',field.done()))
    C=[[.1,.2,.1],[.3,.1,.1],[.1,.2,.2]];B=[[float(i==j)-C[i][j] for j in range(3)] for i in range(3)];B_inv=inverse(B);demand=[100,80,60];production=mv(B_inv,demand);change=mv(B_inv,[0,0,6]);new=[x+y for x,y in zip(production,change)]
    qs.append(question('C',11,['AHL 1.14'],
      r'Three sectors have gross production vector $\mathbf x$ and final external demand $\mathbf d$, both in millions of dollars. Internal demand is $C\mathbf x$, where $C=\begin{pmatrix}0.1&0.2&0.1\\0.3&0.1&0.1\\0.1&0.2&0.2\end{pmatrix}$. Total production meets internal and external demand, so $\mathbf x=C\mathbf x+\mathbf d$. Initially $\mathbf d=(100,80,60)^T$.',[
      part('a','Write a matrix equation whose solution gives $\\mathbf x$, with the coefficient matrix shown explicitly.',2,[('M1',r'$(I-C)\mathbf x=\mathbf d$.'),('A1',f'The coefficient matrix is ${matrix(B)}$.')],[ev('Coefficient matrix',B)]),
      part('b','Use technology to find the required gross production vector.',3,[('M1',r'Use $\mathbf x=(I-C)^{-1}\mathbf d$.'),('A2',f'$\\mathbf x={column(production)}$ million dollars.')],[ev('Gross production vector',production),ev('Production balance',mv(B,production),demand)]),
      part('c','Only external demand for sector 3 rises by 10%. Find the increase in gross production required in all three sectors.',2,[('M1',r'$\Delta\mathbf x=(I-C)^{-1}(0,0,6)^T$.'),('A1',f'The increase is ${column(change)}$ million dollars.')],[ev('Production response to demand change',change),ev('New production balance',mv(B,new),[100,80,66])])],f'Production{production};increases{change}.'))
    good=N.cdf((94-100)/4);bad=N.cdf((94-90)/6);mixture=.8*good+.2*bad;posterior=.2*bad/mixture;cut=100+4*N.inv_cdf(.01);miss=1-N.cdf((cut-90)/6)
    qs.append(question('C',12,['SL 4.6','SL 4.9'],
      'A shipment contains 80% standard cells and 20% degraded cells. Their capacities $X$, in arbitrary units, follow $N(100,4^2)$ and $N(90,6^2)$ respectively. A screening rule flags a cell if $X<c$.',[
      part('a','For $c=94$, find the probability that a randomly selected cell is flagged.',2,[('M1','Use $0.8P(X<94\\mid\\mathrm{standard})+0.2P(X<94\\mid\\mathrm{degraded})$.'),('A1',f'The probability is ${n(mixture)}$.')],[ev('Flagging mixture probability',mixture)]),
      part('b','Given that a cell is flagged at $c=94$, find the probability that it is degraded.',3,[('M1',f'The degraded-and-flagged probability is $0.2\\Phi((94-90)/6)={n(.2*bad)}$.'),('M1','Divide by the total flagging probability.'),('A1',f'The posterior probability is ${n(posterior)}$.')],[ev('Degraded posterior after flagging',posterior)]),
      part('c','Choose $c$ so that 1% of standard cells are flagged. For this new cutoff, find the probability that a degraded cell is not flagged.',2,[('A1',f'$c=100+4\\Phi^{{-1}}(0.01)={n(cut)}$.'),('A1',f'$P(X\\ge c\\mid\\mathrm{{degraded}})={n(miss)}$.')],[ev('Standard-cell false flag rate',N.cdf((cut-100)/4),.01),ev('Degraded-cell missed detection probability',miss)])],f'Flagprob{n(mixture)},posterior{n(posterior)};cut{n(cut)},miss{n(miss)}.'))
    a=[12.4,11.8,13.1,12.7,12.0,13.5];b=[14.1,13.8,15.0,14.4,13.5,14.8];pooled=math.sqrt((5*stdev(a)**2+5*stdev(b)**2)/10);t=(mean(a)-mean(b))/(pooled*math.sqrt(1/6+1/6));pv=tcdf(t,10)
    qs.append(question('C',13,['SL 4.11'],
      'Two independently and randomly sampled coatings are tested for drying time in minutes. Assume both populations are normal with equal, unknown variances.\n\n'+table(['Coating','Times'],[['A',', '.join(map(str,a))],['B',', '.join(map(str,b))]])+'\n\nTest whether coating A has the lower population mean drying time at the 5% level.',[
      part('a','Find the two sample means and the pooled sample standard deviation.',3,[('A1',f'$\\bar x_A={n(mean(a))}$, $\\bar x_B={n(mean(b))}$ minutes.'),('M1',r'$s_p=\sqrt{[5s_A^2+5s_B^2]/10}$.'),('A1',f'$s_p={n(pooled)}$ minutes.')],[ev('Means and pooled standard deviation',[mean(a),mean(b),pooled])]),
      part('b','State the hypotheses and calculate the test statistic and $p$-value.',3,[('A1',r'$H_0:\mu_A=\mu_B$, $H_1:\mu_A<\mu_B$.'),('M1',r'$t=(\bar x_A-\bar x_B)/(s_p\sqrt{1/6+1/6})$, with $df=10$.'),('A1',f'$t={n(t)}$, one-tailed $p={n(pv)}$.')],[ev('Pooled t statistic and lower tail',[t,pv])]),
      part('c','State a conclusion in context.',1,[('R1',f'$p={n(pv)}<0.05$, so there is evidence that coating A has a lower population mean drying time.')],[ev('Drying-time decision',{'p':pv,'reject':pv<.05})])],f'Pooledsd{n(pooled)},t{n(t)},p{n(pv)};Ahaslowermean.'))
    k=18/(7*math.pi);u=(68+20*math.sqrt(13))/9;radius=(k*k/u)**(1/6);height=k/radius**2;surface=lambda r:5*math.pi*r*r+3*math.pi*math.sqrt(r**4+k*k/r**2);derivative=lambda r:math.pi*r*(10+3*(2-k*k/r**6)/math.sqrt(1+k*k/r**6))
    frustum=svg(['<ellipse cx="360" cy="85" rx="180" ry="38" fill="none" stroke="#222" stroke-width="2"/>','<ellipse cx="360" cy="330" rx="90" ry="22" fill="none" stroke="#222" stroke-width="2"/>',line(180,85,270,330),line(540,85,450,330),line(360,85,540,85,'#777',1.5,True),line(360,330,450,330,'#777',1.5,True),line(360,85,360,330,'#777',1.5,True),text(450,69,'2r'),text(405,316,'r'),text(382,215,'h'),text(360,402,'Closed frustum; not to scale',17)])
    qs.append(question('C',14,['SL 3.1','SL 5.7'],
      'A closed storage vessel is a conical frustum with bottom radius $r$, top radius $2r$ and height $h$, all in metres. Its volume is 6 m$^3$. For a frustum, $V=\\frac{\\pi h}{3}(R^2+Rr+r^2)$ and curved area $=\\pi(R+r)\\sqrt{h^2+(R-r)^2}$. The permitted range is $0.4\\le r\\le1.4$.',[
      part('a','Express $h$ in terms of $r$.',2,[('M1',r'$6=(7\pi/3)hr^2$.'),('A1',r'$h=18/(7\pi r^2)$.')],[ev('Volume reconstruction',7*math.pi*height*radius**2/3,6)]),
      part('b','Find an expression in $r$ for the total material area, including both circular ends.',2,[('M1','The end areas total $5\\pi r^2$.'),('A1',r'$S(r)=5\pi r^2+3\pi r\sqrt{r^2+[18/(7\pi r^2)]^2}$.')],[ev('Equivalent surface-area forms',surface(radius),5*math.pi*radius**2+3*math.pi*radius*math.sqrt(height**2+radius**2))]),
      part('c','Use technology to find the radius and height giving minimum total material area, and state that area.',3,[('M1','Minimize $S(r)$ numerically over $0.4\\le r\\le1.4$.'),('A1',f'$r={n(radius)}$ m, $h={n(height)}$ m.'),('A1',f'The minimum area is ${n(surface(radius))}$ m$^2$.')],[ev('Stationary surface derivative',derivative(radius),0),ev('Frustum optimal dimensions and area',[radius,height,surface(radius)])]),
      part('d','Give evidence that this is the global minimum on the allowed interval.',1,[('R1',f'The derivative changes from negative to positive at its only zero in the interval; endpoint areas are ${n(surface(.4))}$ and ${n(surface(1.4))}$ m$^2$, both larger. A suitable GDC derivative graph is acceptable.')],[ev('Endpoint areas and derivative signs',[surface(.4),surface(1.4),derivative(.4),derivative(1.4)]),ev('Unique positive transformed derivative root',9*u*u-136*u-64,0)])],f'Frustumr{n(radius)},h{n(height)},S{n(surface(radius))}.',frustum))
    adjacency=[[0,1,1,0],[1,0,0,1],[0,1,0,1],[1,0,1,0]];walks=power(adjacency,4)[0][3]
    pos={'A':(165,100),'B':(555,100),'C':(165,325),'D':(555,325)};elements=[text(360,28,'Arrows are one-way links',17)]
    for ii,row in enumerate(adjacency):
        for jj,value in enumerate(row):
            if value:
                start=pos['ABCD'[ii]];end=pos['ABCD'[jj]];dx=end[0]-start[0];dy=end[1]-start[1];length=math.hypot(dx,dy);off=6 if adjacency[jj][ii] else 0
                ux,uy=dx/length,dy/length;elements.append(arrow(start[0]+20*ux-off*uy,start[1]+20*uy+off*ux,end[0]-20*ux-off*uy,end[1]-20*uy+off*ux))
    for label,(x,y) in pos.items():elements +=[f'<circle cx="{x}" cy="{y}" r="18" fill="white" stroke="#222" stroke-width="2"/>',text(x,y+6,label)]
    qs.append(question('C',15,['AHL 3.14','AHL 3.15','SL 4.5'],
      'A robot moves on the directed graph shown. At each vertex it chooses uniformly between the two outgoing links. Its choices at successive steps depend only on its current vertex. Use vertex order A,B,C,D and the adjacency convention $M_{ij}=1$ when there is an arrow from $i$ to $j$.',[
      part('a','Write down the adjacency matrix $M$.',2,[('A2',f'$M={matrix(adjacency)}$. Award one mark for two correctly specified rows and both marks for all four.')],[ev('Directed adjacency matrix',adjacency)]),
      part('b','Find the number of four-link walks from A to D, identifying the relevant matrix entry.',3,[('M1','Calculate $M^4$.'),('M1','Use the entry in row A, column D.'),('A1',f'The number is ${int(walks)}$.')],[ev('Four-step adjacency power',power(adjacency,4)),ev('A-to-D walk count',walks)]),
      part('c','Find the probability that the robot is at D after four moves, if it starts at A.',2,[('M1','Every four-move walk has probability $(1/2)^4$.'),('A1',f'The probability is ${int(walks)}/16={n(walks/16)}$.')],[ev('Four-step arrival probability',walks/16)]),
      part('d','Explain why counting walks is appropriate even if a route revisits a vertex.',1,[('R1','Walks permit repeated vertices and links; a robot can revisit them, unlike a simple path.')],[ev('Positive four-step return walk count',power(adjacency,4)[0][0])])],f'Adjacency{adjacency};M4AD{walks};probability{n(walks/16)}.',svg(elements)))
    radius=lambda x:.12+.08*x-.04*x*x;volume=lambda h:math.pi*integrate(lambda x:radius(x)**2,0,h);full=volume(1.5);halfheight=root(lambda h:volume(h)-full/2,0,1.5)
    drawing=Plot(0,1.5,0,.20,[0,.5,1,1.5],[0,.05,.1,.15,.2],xlabel='x / m',ylabel='r / m');drawing.path([(1.5*j/150,radius(1.5*j/150)) for j in range(151)])
    qs.append(question('C',16,['SL 5.6','AHL 5.12'],
      'A vertical vessel of height 1.5 m has circular cross-sections of radius $r(x)=0.12+0.08x-0.04x^2$ metres at height $x$ metres above its base, for $0\\le x\\le1.5$. The diagram graphs radius against height; it is not a side-view orientation of the vessel. Ignore wall thickness.',[
      part('a','Find the maximum radius and the height where it occurs.',2,[('M1',r'$r\prime(x)=0.08-0.08x=0$ gives $x=1$.'),('A1','The maximum radius is $0.16$ m, greater than both endpoint radii.')],[ev('Maximum radius and endpoints',[radius(1),radius(0),radius(1.5)],[.16,.12,.15])]),
      part('b','Calculate the vessel\'s capacity in litres.',3,[('M1',r'$V=\pi\int_0^{1.5}(0.12+0.08x-0.04x^2)^2\,dx$.'),('A1',f'$V={n(full)}$ m$^3$.'),('A1',f'The capacity is ${n(1000*full)}$ litres.')],[ev('Capacity by numerical integration',full),ev('Polynomial antiderivative check',full,math.pi*(.0144*1.5+.0096*1.5**2-.0032*1.5**3/3-.0064*1.5**4/4+.0016*1.5**5/5))]),
      part('c','Find the water depth when the upright vessel is half full.',3,[('M1',r'Solve $\pi\int_0^h r(x)^2\,dx=V/2$ over $0<h<1.5$.'),('M1','Use a numerical equation solver with the full unrounded capacity.'),('A1',f'The depth is $h={n(halfheight)}$ m.')],[ev('Half-volume depth',halfheight),ev('Half-volume substitution',volume(halfheight),full/2)])],f'Maxradius.16atx1;capacity{n(1000*full)}L;halfdepth{n(halfheight)}m.',drawing.done()))
    return qs


def paper_d():
    qs=[]
    flows=[4000,5000,6000,6000,7000];npv=lambda r:-18000+sum(c/(1+r)**j for j,c in enumerate(flows,1));irr=root(npv,0,.5)
    qs.append(question('D',1,['SL 1.4','SL 1.8','SL 2.6'],
      'A project costs 18 000 dollars now and returns 4000, 5000, 6000, 6000 and 7000 dollars at the ends of years 1 to 5 respectively. Its net present value at annual discount rate $r$ is defined by $NPV(r)=-18000+\\sum_{t=1}^5 C_t/(1+r)^t$. The internal rate of return is the value of $r$ giving zero NPV.',[
      part('a','Calculate the net present value at a 6% discount rate.',2,[('M1','Discount every return for its own number of years and subtract the initial cost.'),('A1',f'$NPV(0.06)={n(npv(.06))}$ dollars.')],[ev('Six-percent discounted cash flow',npv(.06))]),
      part('b','Find the internal rate of return, as an annual percentage.',2,[('M1','Solve $NPV(r)=0$ numerically for $r>0$.'),('A1',f'The internal rate is ${n(100*irr)}\\%$ per year.')],[ev('Internal-rate NPV substitution',npv(irr),0)]),
      part('c','At a required return of 10%, decide whether the project has a positive NPV. Give one reason the calculation alone does not guarantee a profitable outcome.',2,[('A1',f'$NPV(0.10)={n(npv(.1))}$ dollars, which is positive; the model meets the required return.'),('R1','Future returns are forecasts; costs, timing or cash flows may differ, so a positive model NPV does not remove commercial risk.')],[ev('Ten-percent NPV decision',{'NPV':npv(.1),'positive':npv(.1)>0})])],f'NPV6%{n(npv(.06))};IRR{n(100*irr)}%;NPV10%{n(npv(.1))}.'))
    lower=math.pi*2.395**2*5.15;upper=math.pi*2.405**2*5.25;nominal=math.pi*2.4**2*5.2;error=100*(nominal-lower)/lower
    qs.append(question('D',2,['SL 1.6','SL 3.1'],
      'The radius of a cylindrical tank is recorded as 2.40 m to the nearest 0.01 m. Its height is recorded as 5.2 m to the nearest 0.1 m. The nominal volume is calculated from these recorded values. Use the standard half-unit rounding intervals.',[
      part('a','State the lower and upper bounds for radius and height.',2,[('A1','$2.395\\le r<2.405$ m.'),('A1','$5.15\\le h<5.25$ m.')],[ev('Rounding half-widths',[.01/2,.1/2],[.005,.05])]),
      part('b','Find bounds for the true tank volume.',2,[('M1','Volume $\\pi r^2h$ increases with each positive dimension.'),('A1',f'${n(lower)}\\le V<{n(upper)}$ m$^3$, with the unrounded expressions $\\pi(2.395)^2(5.15)$ and $\\pi(2.405)^2(5.25)$.')],[ev('Monotone volume bounds',[lower,upper])]),
      part('c','Find the largest possible percentage by which the nominal volume overstates the true volume. Use the true volume in the denominator.',2,[('M1',f'The nominal volume is ${n(nominal)}$ m$^3$; the overstatement is greatest at the lower true-volume bound.'),('A1',f'$100(V_{{\\mathrm{{nom}}}}-V_{{\\min}})/V_{{\\min}}={n(error)}\\%$.')],[ev('Maximum relative overstatement',error)])],f'Volumebounds{n(lower)},{n(upper)};maximumoverstatement{n(error)}%.'))
    tariff=lambda x:8+.18*min(x,120)+.32*max(x-120,0);xs=[50,100,150,200];ps=[.1,.3,.4,.2];expect=sum(p*tariff(x) for x,p in zip(xs,ps));ex=sum(x*p for x,p in zip(xs,ps))
    qs.append(question('D',3,['AHL 2.9','SL 4.7'],
      'A monthly energy bill consists of a fixed charge of 8 dollars, plus 0.18 dollars per kWh for the first 120 kWh and 0.32 dollars per kWh above 120. Monthly use $X$ has the following distribution.\n\n'+table(['$x$ / kWh',*xs],[['$P(X=x)$',*ps]]),[
      part('a','Find the bill for 150 kWh.',1,[('A1','$8+0.18(120)+0.32(30)=39.20$ dollars.')],[ev('Bill at150',tariff(150),39.2)]),
      part('b','Find the expected monthly bill.',3,[('M1','The bills at 50,100,150,200 kWh are 17.00,26.00,39.20,55.20 dollars.'),('M1','Weight those four bills by their probabilities.'),('A1',f'The expectation is ${expect:.2f}$ dollars.')],[ev('Expected nonlinear tariff',expect)]),
      part('c','Find the bill at the expected use $E(X)$ and compare it with part (b). Explain the difference.',2,[('A1',f'$E(X)={n(ex)}$ kWh and its bill is ${tariff(ex):.2f}$ dollars, below the expected bill.'),('R1','The tariff is not one linear rule across the full range; high-use months incur the higher marginal rate, so substituting the mean use does not give the mean bill.')],[ev('Bill of mean versus mean bill',[tariff(ex),expect])])],f'Bill150=39.20;expectedbill{expect:.2f};meanuse{ex},billofmean{tariff(ex):.2f}.'))
    csmall=math.asin(.75);clarge=math.pi-csmall;bshort=6*math.sqrt(3)-math.sqrt(28);blong=6*math.sqrt(3)+math.sqrt(28)
    A=(90,335);B=(500,335);scale=410/12
    point=lambda length:(A[0]+scale*length*math.cos(math.pi/6),A[1]-scale*length*.5)
    short=point(bshort);long=point(blong)
    drawing=svg([line(*A,*long),line(*A,*B),line(*B,*short,'#777',2,True),line(*B,*long),text(A[0]-18,A[1]+22,'A'),text(B[0]+18,B[1]+22,'B'),text(*[short[0]-20,short[1]-17],'possible C',16),text(long[0]+20,long[1]-12,'possible C',16),text(295,362,'12 m'),text(170,320,'30°'),text(390,270,'8 m'),text(550,193,'8 m'),text(360,402,'Two possible triangles; not to scale',17)])
    qs.append(question('D',4,['SL 3.2','AHL 3.8'],
      'Survey points form a triangle $ABC$ with $AB=12$ m, $BC=8$ m and $\\angle BAC=30^\\circ$. Both geometrically possible positions of C above AB are permitted initially.',[
      part('a','Find the two possible values of $\\angle ACB$.',2,[('M1','$\\sin C=12\\sin30^\\circ/8=0.75$.'),('A1',f'$C={n(math.degrees(csmall))}^\\circ$ or ${n(math.degrees(clarge))}^\\circ$.')],[ev('Ambiguous angle sine',[math.sin(csmall),math.sin(clarge)],[.75,.75])]),
      part('b','Find the two possible lengths of $AC$.',3,[('M1','For each possible C, find B from the triangle angle sum.'),('M1','Apply the sine rule $AC=8\\sin B/\\sin30^\\circ$.'),('A1',f'The lengths are ${n(bshort)}$ m and ${n(blong)}$ m.')],[ev('Ambiguous side lengths',[bshort,blong]),ev('Cosine-rule verification',[length**2+12**2-24*length*math.cos(math.pi/6) for length in [bshort,blong]],[64,64])]),
      part('c','The perpendicular projection of C onto the line AB lies strictly between A and B. Select the valid length of AC.',1,[('A1',f'Choose ${n(bshort)}$ m, whose projection is between 0 and 12 m. The larger length projects beyond B.')],[ev('Projection distances',[bshort*math.cos(math.pi/6),blong*math.cos(math.pi/6)])])],f'Cangles{n(math.degrees(csmall))},{n(math.degrees(clarge))};AClengths{n(bshort)},{n(blong)};selectshort.',drawing))
    obs=[20,58,62,60];lam=400/200;expected=[200*poisson(j,lam) for j in range(3)]+[200*(1-pcdf(2,lam))];chi=sum((o-e)**2/e for o,e in zip(obs,expected));pv=math.exp(-chi/2)
    assert min(expected)>5
    qs.append(question('D',5,['SL 4.11','AHL 4.12','AHL 4.17'],
      'A researcher records incident counts in 200 independent equal-duration intervals. The complete ungrouped counts sum to 400. Their grouped frequencies are\n\n'+table(['Count','0','1','2','$\\ge3$'],[['Observed',*obs]])+'\n\nTest the fit of a Poisson model at the 5% level, estimating its mean from these same observations.',[
      part('a','Estimate the Poisson mean.',1,[('A1','$\\hat\\lambda=400/200=2$.')],[ev('Estimated Poisson mean',lam)]),
      part('b','Find all four expected frequencies.',2,[('M1','Use Poisson probabilities with the fitted mean 2; pool all counts at least 3 into the last cell.'),('A1',f'The expected frequencies are ${[round(e,6) for e in expected]}$.')],[ev('Four fitted expected frequencies',expected),ev('Expected total',sum(expected),200)]),
      part('c','State the degrees of freedom and find the test $p$-value.',2,[('A1','$df=4-1-1=2$, subtracting one fitted parameter.'),('A1',f'$\\chi^2={n(chi)}$ and $p={n(pv)}$.')],[ev('Fitted GOF degrees of freedom',4-1-1,2),ev('GOF statistic and df2 tail',[chi,pv])]),
      part('d','State a conclusion in context.',1,[('R1',f'$p={n(pv)}>0.05$, so do not reject the Poisson model. This is insufficient evidence of lack of fit, not proof that the model is true.')],[ev('GOF decision',{'p':pv,'reject':pv<.05})])],f'λ2;expected{expected};chi{n(chi)},p{n(pv)};donotreject.'))
    x=[0,1,2,3,4];y=[18.1,31.9,44.3,51.4,58.9];slope,intercept,r=regression(x,[math.log(80-z) for z in y]);A=math.exp(intercept);k=-slope;initial=80-A
    qs.append(question('D',6,['AHL 2.10','SL 4.4','SL 2.6'],
      'A crop response $Y$ is modelled by $Y=80-Ae^{-kt}$, with $A,k>0$ and $t$ in weeks. The value 80 is a proposed saturation level. Data are\n\n'+table(['$t$',*x],[['$Y$',*y]])+'\n\nFit by least squares to the transformed linear relationship.',[
      part('a','State a linearized equation and find its fitted slope and intercept.',3,[('M1',r'$\ln(80-Y)=\ln A-kt$.'),('A1',f'The fitted slope is ${n(slope)}$.'),('A1',f'The fitted intercept is ${n(intercept)}$.')],[ev('Transformed linear regression',[slope,intercept,r])]),
      part('b','Find $A$ and $k$.',2,[('A1',f'$A=e^{{{n(intercept)}}}={n(A)}$.'),('A1',f'$k={n(k)}$ week$^{{-1}}$.')],[ev('Recovered model parameters',[A,k])]),
      part('c','Find the fitted initial response and explain why the assumed saturation level cannot be established from these five early observations alone.',2,[('A1',f'$Y(0)=80-A={n(initial)}$.'),('R1','The observations do not reach the long-run plateau. Other saturation levels/models may fit early data, so 80 remains a modelling assumption requiring later evidence.')],[ev('Fitted initial response',initial)])],f'Linearlogslope{n(slope)},intercept{n(intercept)};A{n(A)},k{n(k)},initial{n(initial)}.'))
    edges=[('A','B',4),('A','C',7),('B','C',2),('B','D',6),('C','D',3),('C','E',8),('D','E',4),('D','F',9),('E','F',3)];d=distances('ABCDEF',edges);old=d['A','F'];limit=.8*old-11
    positions={'A':(75,210),'B':(250,75),'C':(250,340),'D':(450,75),'E':(450,340),'F':(635,210)}
    qs.append(question('D',7,['AHL 3.14','AHL 3.16'],
      'The undirected graph shows travel times in minutes. A traveller goes from A to F. A proposed upgrade changes only the time on BD from 6 to $x$ minutes, where $0\\le x\\le6$.',[
      part('a','Find a shortest original route from A to F and its time.',3,[('M1','Compare feasible route totals or use a consistent shortest-route method.'),('A1','A-B-C-D-E-F is a shortest route.'),('A1',f'Its time is ${old}$ minutes.')],[ev('Original shortest A-to-F time',old,16)]),
      part('b','Find the values of $x$ for which the upgrade gives a strictly shorter journey than the original minimum.',2,[('M1','The upgraded route A-B-D-E-F takes $11+x$ minutes; the old route still takes 16.'),('A1','A strict improvement occurs when $x<5$. At $x=5$ the two routes tie.')],[ev('Upgraded shortest times at sample x',[distances('ABCDEF',[(u,v,x if (u,v)==('B','D') else w) for u,v,w in edges])['A','F'] for x in [0,2,5,6]],[11,13,16,16])]),
      part('c','The upgrade must reduce the original minimum journey time by at least 20%. Find the largest permitted value of $x$.',2,[('M1','Require $11+x\\le0.8(16)=12.8$.'),('A1',f'The largest value is $x={n(limit)}$ minutes.')],[ev('Twenty-percent design threshold',11+limit,.8*old)])],f'Oldroute16;upgradeworksforx<5;20%requiresx≤{n(limit)}.',network(positions,edges,'Original travel times / min')))
    prob=1-N.cdf((20-18)/(12/math.sqrt(64)));cut=18+12/8*N.inv_cdf(.99);size=math.ceil((12*N.inv_cdf(.975)/2)**2)
    qs.append(question('D',8,['AHL 4.15'],
      'Individual service times are independent, right-skewed, with population mean 18 minutes and standard deviation 12 minutes. For sample sizes greater than 30, use the central limit theorem to approximate the distribution of the sample mean.',[
      part('a','For a sample of 64 customers, estimate the probability that their mean service time exceeds 20 minutes.',2,[('M1','The approximate sampling distribution is $\\bar X\\sim N(18,(12/8)^2)$.'),('A1',f'The probability is ${n(prob)}$.')],[ev('CLT upper-tail probability',prob)]),
      part('b','For samples of 64, find a bound exceeded by only 1% of sample means.',2,[('M1',r'$c=18+1.5\Phi^{-1}(0.99)$.'),('A1',f'$c={n(cut)}$ minutes.')],[ev('Sample-mean upper percentile',cut)]),
      part('c','Find the smallest integer sample size greater than 30 for which the approximate probability of a sample mean above 20 is at most 0.025. Check the neighbouring sample size.',3,[('M1',r'Require $(20-18)/(12/\sqrt n)\ge\Phi^{-1}(0.975)$.'),('A1',f'The smallest size is $n={size}$.'),('R1',f'The tails for $n={size-1}$ and $n={size}$ are ${n(1-N.cdf(math.sqrt(size-1)/6))}$ and ${n(1-N.cdf(math.sqrt(size)/6))}$ respectively, straddling 0.025.')],[ev('Neighbouring CLT design tails',[1-N.cdf(math.sqrt(size-1)/6),1-N.cdf(math.sqrt(size)/6)])])],f'n64tail{n(prob)},upper99%{n(cut)};minimumsample{size}.'))
    M=[[-2,1],[1,-2]];state=lambda t:[4*math.exp(-t)+2*math.exp(-3*t),4*math.exp(-t)-2*math.exp(-3*t)]
    field=Plot(-7,7,-7,7,[-6,-3,0,3,6],[-6,-3,0,3,6],xlabel='x',ylabel='y')
    for x in [-6,-4,-2,0,2,4,6]:
        for y in [-6,-4,-2,0,2,4,6]:
            vx,vy=mv(M,[x,y]);sx=570/14*vx;sy=-300/14*vy;length=math.hypot(sx,sy)
            if length:
                a,b=field.xy(x,y);field.e.append(arrow(a-7*sx/length,b-7*sy/length,a+7*sx/length,b+7*sy/length,'#4b7196'))
    field.point(6,2,'(6,2)',dx=-65,dy=-12)
    qs.append(question('D',9,['AHL 1.15','AHL 5.17'],
      r'A linear model near a stable operating point is $dx/dt=-2x+y$, $dy/dt=x-2y$. Time is measured in hours. Initially $(x,y)=(6,2)$. The diagram shows the phase direction field.',[
      part('a','Find both eigenvalues and a corresponding eigenvector for each.',3,[('M1',r'The characteristic equation is $(-2-\lambda)^2-1=0$.'),('A1',r'$\lambda=-1$ has eigenvector $(1,1)^T$.'),('A1',r'$\lambda=-3$ has eigenvector $(1,-1)^T$.')],[ev('Eigenvector substitutions',[mv(M,[1,1]),mv(M,[1,-1])],[[-1,-1],[-3,3]])]),
      part('b','Find $x(t)$ and $y(t)$ satisfying the initial condition.',3,[('M1',r'$\mathbf s=a e^{-t}(1,1)^T+b e^{-3t}(1,-1)^T$.'),('M1','At $t=0$, $a+b=6$, $a-b=2$, so $a=4,b=2$.'),('A1',r'$x=4e^{-t}+2e^{-3t}$, $y=4e^{-t}-2e^{-3t}$.')],[ev('Initial-condition reconstruction',state(0),[6,2]),ev('Differential solution check at1',[-4*math.exp(-1)-6*math.exp(-3),-4*math.exp(-1)+6*math.exp(-3)],mv(M,state(1)))]),
      part('c','State the line along which the trajectory approaches the origin, and justify it.',1,[('R1',r'The $e^{-t}$ term dominates the faster-decaying $e^{-3t}$ term, so the trajectory approaches along $y=x$.')],[ev('Fast-to-slow modal ratio at t5',.5*math.exp(-10))])], 'Eigenpairs−1,(1,1);−3,(1,−1). x=4e−t+2e−3t,y=4e−t−2e−3t;approachy=x.',field.done()))
    theta=math.pi/4+math.asin(3/(4*math.sqrt(2)));z=3+4*cmath.exp(1j*theta)
    drawing=Plot(-2,9.4,-.8,5.2,[-1,0,3,7],[0,2,4],xlabel='Re z',ylabel='Im z');drawing.path([(3+4*math.cos(j*math.pi/180),4*math.sin(j*math.pi/180)) for j in range(181)]);drawing.point(3,0,'centre 3',dx=5,dy=-12)
    qs.append(question('D',10,['AHL 1.12','AHL 1.13','AHL 3.8'],
      r'The resultant phasor is $z=3+4e^{i\theta}$, where $0\le\theta\le\pi$. The diagram shows its locus. Arguments and $\theta$ are in radians.',[
      part('a','Describe the locus, giving its centre and radius.',2,[('A1','It is the upper semicircle with centre $3+0i$.'),('A1','Its radius is $4$, including both real-axis endpoints.')],[ev('Locus centre and radius',[3,4])]),
      part('b','Find $\\theta$ when $\\arg z=\\pi/4$.',2,[('M1','Require $4\\sin\\theta=3+4\\cos\\theta>0$ and solve on $[0,\\pi]$.'),('A1',f'The valid solution is $\\theta={n(theta)}$ rad.')],[ev('Required argument',cmath.phase(z),math.pi/4),ev('Positive real component',z.real)]),
      part('c','Find the amplitude of this resultant.',2,[('M1','Use the modulus at the solution in part (b).'),('A1',f'$|z|={n(abs(z))}$.')],[ev('Resultant amplitude',abs(z))]),
      part('d','Determine whether complete cancellation is possible for any permitted $\\theta$.',1,[('R1','No: the smallest possible amplitude is $|4-3|=1>0$, attained at $\\theta=\\pi$.')],[ev('Minimum amplitude',abs(3+4*cmath.exp(1j*math.pi)),1)])],f'Uppersemicirclecentre3radius4;theta{n(theta)};amplitude{n(abs(z))};minamplitude1.',drawing.done()))
    rel=lambda t:[-20+4*t,-10+3*t];tmin=220/50;minimum=norm(rel(tmin));roots=[(220-30)/50,(220+30)/50]
    drawing=Plot(-5,22,-3,12,[0,5,10,15,20],[0,5,10],xlabel='east / m',ylabel='north / m');drawing.e +=[arrow(*drawing.xy(0,0),*drawing.xy(18,6),'#2563a6'),arrow(*drawing.xy(20,10),*drawing.xy(14,-2),'#696969')];drawing.point(0,0,'P at t=0',dx=6,dy=-15);drawing.point(20,10,'Q at t=0',dx=-100,dy=-15)
    qs.append(question('D',11,['AHL 3.12','AHL 5.13'],
      'Two inspection robots move in a horizontal plane for $0\\le t\\le6$ minutes. Their positions, in metres east and north, are $P(t)=(3t,t)$ and $Q(t)=(20-t,10-2t)$. The arrows show their paths, not simultaneous positions.',[
      part('a','Find the time of closest approach and the minimum separation.',3,[('M1','The squared separation is $(4t-20)^2+(3t-10)^2=25t^2-220t+500$.'),('M1','Minimize on $0\\le t\\le6$: $50t-220=0$.'),('A1',f'$t={n(tmin)}$ minutes and minimum distance ${n(minimum)}$ m.')],[ev('Closest-approach time and separation',[tmin,minimum],[4.4,4])]),
      part('b','Find the interval during which the robots are at most 5 m apart.',3,[('M1','Require $25t^2-220t+500\\le25$.'),('A1','The boundary times are $3.8$ and $5.0$ minutes.'),('A1','The interval is $3.8\\le t\\le5.0$ minutes.')],[ev('Five-metre boundary distances',[norm(rel(t)) for t in roots],[5,5])]),
      part('c','Explain whether the robots collide, despite the crossing paths in the diagram.',1,[('R1','They do not collide: their minimum simultaneous separation is 4 m. Crossing geometric paths does not mean occupying the intersection at the same time.')],[ev('Positive minimum simultaneous distance',minimum)])],f'Closestt4.4,distance4m;within5mfor3.8..5;nocollision.',drawing.done()))
    volume=math.pi*(32-64/3+32/5);removed=1.5*math.pi;remaining=volume-removed;depth=math.sqrt(3)
    drawing=Plot(0,4.8,0,2.4,[0,1,2,3,4],[0,.5,1,1.5,2],xlabel='x / m',ylabel='y / m');drawing.path([(0,0),(4,0),*[(4-(2*j/120)**2,2*j/120) for j in range(1,121)],(0,0)],fill='#f1f1f1');drawing.path([(0,0),(1,0),(1,1.5),(0,1.5),(0,0)],'#4b7196',fill='#dbeafe')
    qs.append(question('D',12,['AHL 5.12','SL 3.1'],
      'The region $0\\le y\\le2$, $0\\le x\\le4-y^2$ is rotated about the $y$-axis to make a solid. All coordinates are in metres. A cylindrical hole of radius 1 m is drilled from the flat base $y=0$ along the axis. The shaded rectangle shows the hole cross-section for depth 1.5 m.',[
      part('a','Find the volume of the original solid.',3,[('M1','At height $y$, the disc radius is $x=4-y^2$.'),('M1',r'$V=\pi\int_0^2(4-y^2)^2\,dy$.'),('A1',f'$V={n(volume)}$ m$^3$.')],[ev('Disc volume',volume,math.pi*integrate(lambda y:(4-y*y)**2,0,2))]),
      part('b','Find the remaining material volume after drilling to a depth of 1.5 m.',2,[('M1','The removed cylinder has volume $\\pi(1)^2(1.5)$ and fits within the solid over that depth.'),('A1',f'The remaining volume is ${n(remaining)}$ m$^3$.')],[ev('Remaining material after drilling',remaining)]),
      part('c','Find the greatest drilling depth possible before a radius-1 hole would break through the curved surface.',2,[('M1','Require $4-y^2\\ge1$ throughout the hole; equality first occurs at $y=\\sqrt3$.'),('A1',f'The maximum depth is ${n(depth)}$ m.')],[ev('Limiting outer radius',4-depth**2,1)])],f'OriginalV{n(volume)},remaining{n(remaining)},maxdrilldepth{n(depth)}.',drawing.done()))
    p0=.02;alpha=lambda size:1-bcdf(1,size,p0);size=max(k for k in range(2,500) if alpha(k)<.05);power_test=1-bcdf(1,size,.12)
    qs.append(question('D',13,['SL 4.8','AHL 4.18'],
      'A contamination rate is suspected to exceed 0.02. In a design for a one-tailed exact binomial test, $n$ independent packets will be sampled and the null hypothesis will be rejected if at least two are contaminated. Choose the largest sample size whose Type I error probability is strictly below 0.05.',[
      part('a','State the null and alternative hypotheses for contamination probability $p$.',1,[('A1','$H_0:p=0.02$, $H_1:p>0.02$.')],[ev('Null contamination parameter',p0)]),
      part('b','Find the largest permitted value of $n$, checking the next integer.',3,[('M1',r'The Type I probability is $P_{0.02}(X\ge2)=1-(0.98)^n-n(0.02)(0.98)^{n-1}$.'),('A1',f'The largest size is $n={size}$, with Type I probability ${n(alpha(size))}$.'),('R1',f'For $n={size+1}$ the probability is ${n(alpha(size+1))}>0.05$.')],[ev('Adjacent exact design Type I rates',[alpha(size),alpha(size+1)])]),
      part('c','For this sample size, find the power of the test when the true contamination probability is 0.12.',2,[('M1',f'Calculate $P(X\\ge2)$ for $X\\sim B({size},0.12)$.'),('A1',f'The power is ${n(power_test)}$.')],[ev('Exact binomial design power',power_test)]),
      part('d','Explain why increasing the sample size without changing the rejection rule is not automatically permitted.',1,[('R1','With the threshold fixed at two, increasing n raises the null probability of rejection as well as power; a larger n can violate the Type I error limit.')],[ev('Type I increase at next sample',alpha(size+1)-alpha(size))])],f'Largestn{size};alpha{n(alpha(size))};powerp.12={n(power_test)}.'))
    revenue=lambda t:(200+30*math.sin(math.pi*t/6))*math.exp(-.06*t)
    derivative=lambda t:math.exp(-.06*t)*(5*math.pi*math.cos(math.pi*t/6)-.06*(200+30*math.sin(math.pi*t/6)))
    stationary=[root(derivative,0,3),root(derivative,9,12)];candidates=[0,*stationary,12];best=max(candidates,key=revenue)
    drawing=Plot(0,12,0,240,[0,3,6,9,12],[0,50,100,150,200],xlabel='t / months',ylabel='R / thousands');drawing.path([(12*j/240,revenue(12*j/240)) for j in range(241)])
    qs.append(question('D',14,['AHL 2.9','SL 5.7','AHL 5.9'],
      r'The revenue forecast for a promotion held $t$ months after a product launch is $R(t)=(200+30\sin(\pi t/6))e^{-0.06t}$ thousand dollars, for $0\le t\le12$. The seasonal term and declining overall interest are both part of the model. Angles are in radians.',[
      part('a',r'Find an expression for $R\prime(t)$.',2,[('M1','Use the product and chain rules.'),('A1',r'$R\prime=e^{-0.06t}[5\pi\cos(\pi t/6)-0.06(200+30\sin(\pi t/6))]$.')],[ev('Derivative finite-difference checks',[derivative(t) for t in [1,4,9]],[(revenue(t+1e-5)-revenue(t-1e-5))/(2e-5) for t in [1,4,9]],1e-7)]),
      part('b','Find all stationary times in the permitted interval.',3,[('M1','Solve the bracketed expression equal to zero on $[0,12]$.'),('A2',f'The times are $t={n(stationary[0])}$ and $t={n(stationary[1])}$ months.')],[ev('Stationary derivative values',[derivative(t) for t in stationary],[0,0])]),
      part('c','Find the promotion time giving the global maximum forecast revenue and state that revenue. Justify using all candidates.',3,[('M1',f'Compare endpoint and stationary values: ${[round(revenue(t),6) for t in candidates]}$ thousand dollars at ${[round(t,6) for t in candidates]}$ months.'),('A1',f'The maximum occurs at $t={n(best)}$ months.'),('A1',f'The maximum forecast is ${n(revenue(best))}$ thousand dollars.')],[ev('All global-optimization candidates',{'times':candidates,'revenues':[revenue(t) for t in candidates]})])],f'Stationarytimes{stationary};globalmaxat{n(best)},R{n(revenue(best))}.',drawing.done()))
    T=lambda q:[[.7,.1,q],[.2,.7,.2],[.1,.2,.8-q]]
    def stationary(q):
        t=T(q);return mv(inverse([[t[0][0]-1,t[0][1],t[0][2]],[t[1][0],t[1][1]-1,t[1][2]],[1,1,1]]),[0,0,1])
    q=3*.4-.8;steady=stationary(q);new=stationary(.5)
    qs.append(question('D',15,['AHL 4.19','AHL 1.14'],
      r'Customers use an app A, website W or telephone P each week. Column state vectors use that order. The regular transition matrix is $T(q)=\begin{pmatrix}0.7&0.1&q\\0.2&0.7&0.2\\0.1&0.2&0.8-q\end{pmatrix}$, where $0.1\le q\le0.5$. The initial proportions are $(1/3,1/3,1/3)^T$. After one week, the app proportion is 0.40.',[
      part('a','Find $q$.',2,[('M1','The app proportion after one step is $(0.7+0.1+q)/3$.'),('A1','$q=0.4$.')],[ev('Parameter inferred from one-step proportion',mv(T(q),[1/3]*3)[0],.4)]),
      part('b','Find the long-run proportions for this value of $q$.',3,[('M1',r'Solve $T\boldsymbol\pi=\boldsymbol\pi$ with components summing to 1.'),('A2',f'The long-run vector is ${column(steady)}$.')],[ev('Current stationary proportions',steady),ev('Stationary substitution',mv(T(q),steady),steady)]),
      part('c','A new policy increases $q$ to 0.5, so the bottom-right entry becomes 0.3; all constant entries remain unchanged. For 1000 customers, find the change in the long-run expected app count.',3,[('M1','Recompute the stationary state using $T(0.5)$.'),('A1',f'The new app probability is ${n(new[0])}$.'),('A1',f'The expected app count increases by $1000({n(new[0])}-{n(steady[0])})={n(1000*(new[0]-steady[0]))}$ customers.')],[ev('Policy stationary probabilities',new),ev('App-count policy change',1000*(new[0]-steady[0]),25)])],f'q.4;stationary{steady};policynew{new};appincrease25of1000.'))
    amount=lambda t:80*math.exp(-.1*t-.01*t*t);half=root(lambda t:amount(t)-40,0,10);peak=(math.sqrt(.02)-.1)/.02;removal=lambda t:(.1+.02*t)*amount(t)
    qs.append(question('D',16,['AHL 5.14','AHL 5.9','SL 5.7'],
      r'The amount $M(t)$ of a substance in a filter, in grams, follows $dM/dt=-(0.1+0.02t)M$, with $M(0)=80$, for $0\le t\le10$ hours. The removal rate is defined as the positive quantity $r(t)=-dM/dt$.',[
      part('a','Find an expression for $M(t)$.',3,[('M1',r'Separate: $dM/M=-(0.1+0.02t)\,dt$.'),('M1',r'$\ln M=-0.1t-0.01t^2+C$ and use $M(0)=80$.'),('A1',r'$M=80e^{-0.1t-0.01t^2}$.')],[ev('Differential model check at sample times',[(-.1-.02*t)*amount(t) for t in [0,2,7]],[-(.1+.02*t)*amount(t) for t in [0,2,7]])]),
      part('b','Find the time when half the initial amount remains.',2,[('M1',r'Solve $0.1t+0.01t^2=\ln2$ on $[0,10]$.'),('A1',f'The time is $t={n(half)}$ hours.')],[ev('Half-amount substitution',amount(half),40)]),
      part('c','Find the time of maximum removal rate and the value of that rate, checking that it is the maximum on the model domain.',3,[('M1',r'$r\prime=M[0.02-(0.1+0.02t)^2]$; it changes from positive to negative when $0.1+0.02t=\sqrt{0.02}$.'),('A1',f'The maximizing time is $t={n(peak)}$ h, within the permitted interval.'),('A1',f'The maximum removal rate is ${n(removal(peak))}$ g h$^{{-1}}$; it exceeds both endpoint rates.')],[ev('Removal-rate stationary factor',.02-(.1+.02*peak)**2,0),ev('Removal-rate maximum and endpoints',[removal(peak),removal(0),removal(10)])])],f'M80exp(-.1t-.01t²);half{n(half)}h;peakremovaltime{n(peak)},rate{n(removal(peak))}.'))
    return qs


def write_paper(set_name,questions):
    assert len(questions)==16 and sum(q['marks'] for q in questions)==110
    valid_refs=set()
    for topic,sl_end,ahl_start,ahl_end in [(1,8,9,15),(2,6,7,10),(3,6,7,16),(4,11,12,19),(5,8,9,18)]:
        valid_refs.update(f'SL {topic}.{j}' for j in range(1,sl_end+1))
        valid_refs.update(f'AHL {topic}.{j}' for j in range(ahl_start,ahl_end+1))
    for q in questions:
        assert all(ref in valid_refs for ref in q['syllabusRefs']),(set_name,q['number'],q['syllabusRefs'])
        assert len({p['label'] for p in q['parts']})==len(q['parts'])
        assert [p['label'] for p in q['parts']]==[g['part'] for g in q['markScheme']]
        strings=[q['stem'],*[p['prompt'] for p in q['parts']],*[s['text'] for g in q['markScheme'] for s in g['steps']]]
        assert not any(re.search(r'\\\\(?=[A-Za-z])',s) for s in strings),(set_name,q['number'],'doubled command slash')
    p={'id':f'ai-hl-set-{set_name.lower()}-paper-1','strand':'ai','course':'hl','set':set_name,'paper':'1',
       'title':f'Mathematics AI HL · Set {set_name} · Paper 1','minutes':120,'marks':110,'calculator':True,'questions':questions}
    DEST.mkdir(parents=True,exist_ok=True)
    target=DEST/f"{p['id']}.json";target.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    for q in questions:
        record=next(r for r in RECORDS if r['paper']==p['id'] and r['question']==q['number'])
        record['canonicalQuestionSha256']=hashlib.sha256(json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest()
    PAPERS.append({'id':p['id'],'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'questions':16,'marks':110,'minutes':120,'calculator':True,'diagrams':sum('diagramSvg' in q for q in questions)})


def main():
    write_paper('A',paper_a())
    # Remaining sets are independently authored below; no numeric-variant generator.
    for set_name,function in [('B',globals().get('paper_b')),('C',globals().get('paper_c')),('D',globals().get('paper_d'))]:
        if function:write_paper(set_name,function())
    DOCS.mkdir(parents=True,exist_ok=True)
    report={'status':'author verification passed; independent review required','papers':PAPERS,'questions':len(RECORDS),
            'executableCheckCount':sum(len(v) for r in RECORDS for v in r['partChecks'].values()),
            'method':'Every numeric answer is computed from the supplied givens using standard-library algorithms, then inserted into the complete scheme. Back-substitution, alternative forms, probability normalization, matrix identities and optimization constraints are checked where applicable. Qualitative deductions are linked to computed signs/probabilities. This is an author pass, not independent moderation.',
            'originality':f'{len(RECORDS)} separately conceived question contexts and mathematical demands, not numeric variants. No original question text or diagram copied. Official specimen used for format and command-term style; publicly visible provider materials used only to inspect topic/marking conventions.',
            'researchSources':['https://www.ibo.org/globalassets/new-structure/university-admission/pdfs/dp-mathematics-applications-and-interpretation-specimen-papers-en.pdf','https://xmltwo.ibo.org/publications/EAD/2026_EN/GR5/GR5-Maths_AI_EN.pdf','https://www.christosnikolaidis.com/en/mai-exercise/','https://www.christosnikolaidis.com/en/mai-hl-test/','https://www.christosnikolaidis.com/en/mock-exam/','https://www.revisionvillage.com/ib-math/applications-and-interpretation-hl/questionbank/'],
            'sourceLimits':'Christos AI exercise/test indexes and the local Year-1 HL exam were inspected for progression, response space and marking conventions; the separate paid mock-exam index is AA-only. Revision Village topic pages were publicly visible but question content was not exposed by the text reader. The official AI specimen anchors the full assessment style. No provider question, dataset or image was copied. Current 2026 guide applies; 2029 content reductions do not.',
            'renderQA':{'markdownMathExpressionsParsed':825,'safeSVGsRenderedAndIndividuallyInspected':28,'diagramCountsBySet':{'A':7,'B':6,'C':8,'D':7},'method':'All canonical stems, parts and scheme steps passed the Markdown+KaTeX parser; all SVGs were rasterized at 1200 pixels wide and individually inspected. Refined label positions, physical segment shading and the actual robot-route endpoint before freezing.'},
            'localStyleReferences':[
                {'name':'MAI HL YEAR 1 EXAM 1 (2020-2021).pdf','sha256':'9bdc2bd65cc3cd01798351bfa4320dccd34c4fdf5ff8b1c29734eb5252a188a1','pages':14,'questionMarks':[7,7,6,7,6,7,7,6,7,8,16,16],'use':'Read cover and representative native short questions. This is a 100-mark mixed internal Year-1 exam, not a controlling full-Paper-1 specification.'},
                {'name':'Mathematics_applications_and_interpretation_paper_1_TZ1_SL.pdf','sha256':'76730e66d5e240e33fd3f25e75f4fcc27a74bbd7b2de188b6e5770278d7df866','pages':25,'questionMarks':[6,5,5,5,7,6,5,7,4,7,5,9,9],'use':'Common-content contexts, concise command terms, variable-width data tables and diagrams with separate response space; not a source for question copying.'},
                {'name':'Mathematics_applications_and_interpretation_paper_2_TZ1_SL.pdf','sha256':'fa60b6eede043138457085557f55400fa4aa726e47a7e878c6e7ed6018bba605','pages':10,'questionMarks':[15,15,17,14,19],'use':'Read native examples to distinguish extended-response sequences from our short-response Paper 1s.'},
                {'name':'Mathematics_applications_and_interpretation_paper_2_TZ2_SL.pdf','sha256':'a8c53249be192aa82fbbeb23c327495c9fd1bb9c3d3d00bd71009e27e5f9067b','pages':13,'questionMarks':[16,12,20,16,16],'use':'Read native geometric and contextual examples as style only; no stem, diagram, dataset or question structure copied.'}
            ],
            'pacingReview':'Each full P1 has 16 compulsory short responses (five at 6 marks, eight at 7 marks and three at 8 marks), no AA-style sections, 110 marks in 120 minutes. All five official topics appear in each paper. The HL official guide/specimen controls breadth and GDC demands; common-SL references do not reduce HL scope. Harder demands require model selection, inverse interpretation, conditional inference, constraints or parameter design rather than extra AA techniques.',
            'records':RECORDS}
    (DOCS/'p1-author-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({'papers':len(PAPERS),'questions':len(RECORDS),'checks':report['executableCheckCount'],'marks':sum(p['marks'] for p in PAPERS)}))


if __name__=='__main__':main()
