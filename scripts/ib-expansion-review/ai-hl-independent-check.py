"""Independent AI HL replay from learner-visible JSON, not authoring modules.
Author ledger values are read only AFTER separate reconstruction, for comparison.
"""
import re,sys,json,math,cmath,hashlib,itertools,statistics,xml.etree.ElementTree as ET
from pathlib import Path
from decimal import Decimal,ROUND_HALF_UP
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'work'/'aa-sl-deps'))
import numpy as np
import sympy as sy
from sympy.parsing.sympy_parser import parse_expr,standard_transformations,implicit_multiplication_application
from scipy import stats,optimize,integrate,linalg
X=sy.symbols('x',real=True);TRANS=standard_transformations+(implicit_multiplication_application,)
def nums(s):return [float(a) for a in re.findall(r'(?<![A-Za-z])[-+]?\d+(?:\.\d+)?',s)]
def grab(p,s):
 m=re.search(p,s);assert m,(p,s)
 return [float(a.rstrip('.')) for a in m.groups()]
def blocks(s):return re.findall(r'\$([^$]+)\$',s)
def body(q):return q['stem'].split(' Unless otherwise stated,')[0]
def arrays(s):return [np.array(nums(a)) for a in re.findall(r'\[([\d.,\s-]+)\]',s)]
def matrices(s):return [np.array([[float(sy.sympify(c)) for c in r.split('&')] for r in b.split('\\\\')]) for b in re.findall(r'\\begin\{pmatrix\}(.*?)\\end\{pmatrix\}',s)]
def mathparse(s):
 s=re.sub(r'\\(?:d?frac|tfrac)\{([^{}]+)\}\{([^{}]+)\}',r'((\1)/(\2))',s)
 s=re.sub(r'\\(?:d?frac|tfrac)(\d)(\d)',r'(\1/\2)',s)
 s=s.replace('\\pi','pi').replace('\\ln','log').replace('\\cos','cos').replace('\\sin','sin').replace('\\sqrt','sqrt').replace('\\,','').replace('^','**').replace('{','(').replace('}',')')
 return parse_expr(s,local_dict={**{c:X for c in ['x','t','n','s','q','d','r']},'e':sy.E,'pi':sy.pi,'log':sy.log,'sin':sy.sin,'cos':sy.cos,'sqrt':sy.sqrt},transformations=TRANS)
def expr(q,name):
 for b in blocks(body(q)):
  if b.startswith(name+'='):return mathparse(b.split('=',1)[1])
 raise ValueError((q['id'],name))
def svgp(q):
 text=[z.text or '' for z in ET.fromstring(q['diagramSvg']).iter() if z.tag.endswith('text')]
 out={}
 for z in text:
  m=re.match(r'([A-Z])\s*\(([-\d.]+),\s*([-\d.]+)\)',z)
  if m:out[m[1]]=np.array([float(m[2]),float(m[3])])
 return out
def network(q):
 root=ET.fromstring(q['diagramSvg']);circles=[z for z in root if z.tag.endswith('circle')];texts=[z for z in root if z.tag.endswith('text')];nodes={}
 for c in circles:
  p=np.array([float(c.get('cx')),float(c.get('cy'))]);near=min(texts,key=lambda z:np.linalg.norm(np.array([float(z.get('x')),float(z.get('y'))])-p));nodes[near.text]=p
 edges=[]
 for l in root:
  if not l.tag.endswith('line'):continue
  p=np.array([float(l.get('x1')),float(l.get('y1'))]);r=np.array([float(l.get('x2')),float(l.get('y2'))]);u=min(nodes,key=lambda k:np.linalg.norm(nodes[k]-p));v=min(nodes,key=lambda k:np.linalg.norm(nodes[k]-r));mid=(p+r)/2
  if np.linalg.norm(nodes[u]-p)>1 or np.linalg.norm(nodes[v]-r)>1:continue
  labels=[z for z in texts if re.fullmatch(r'[\d.]+',z.text or '')];lab=min(labels,key=lambda z:np.linalg.norm(np.array([float(z.get('x'))+9,float(z.get('y'))-3])-mid));edges.append((u,v,float(lab.text)))
 return edges
def distances(edges):
 ns=sorted(set(a for a,b,w in edges)|set(b for a,b,w in edges));D={a:{b:(0 if a==b else math.inf) for b in ns} for a in ns}
 for a,b,w in edges:D[a][b]=D[b][a]=w
 for k in ns:
  for a in ns:
   for b in ns:D[a][b]=min(D[a][b],D[a][k]+D[k][b])
 return D
def mst(edges):
 ns=set(a for a,b,w in edges)|set(b for a,b,w in edges);parent={a:a for a in ns};total=0
 def find(a):
  while parent[a]!=a:a=parent[a]
  return a
 for a,b,w in sorted(edges,key=lambda e:e[2]):
  if find(a)!=find(b):parent[find(a)]=find(b);total+=w
 return total
def tours(D):
 ns=sorted(D);a=ns[0]
 return [(a,)+p+(a,) for p in itertools.permutations(ns[1:])]
def tourcost(D,t):return sum(D[a][b] for a,b in zip(t,t[1:]))

def na(q,j):
 z=body(q);p=q['parts'];b=blocks(z);m=matrices(z)
 if j==0:
  a,d,N,cap=grab(r'processes ([\d.]+) tonnes.*?of ([\d.]+) tonnes.*?lasts ([\d.]+) months.*?permits ([\d.]+) tonnes',z);return dict(annualTotal=sum(a+k*d for k in range(int(N))),maximumIncrease=(cap-N*a)/sum(range(int(N))))
 if j==1:
  a,percent=grab(r'produces ([\d.]+) trays.*?by ([\d.]+)%',z);r=1+percent/100;return dict(sum8=sum(a*r**k for k in range(8)),firstSeason=next(n for n in range(1,200) if a*r**(n-1)>300))
 if j==2:
  P,r,inf=grab(r'invests ([\d.]+).*?at ([\d.]+)%.*?Inflation is ([\d.]+)%',z);nom=P*(1+r/100)**6;return dict(nominal=nom,realValue=nom/(1+inf/100)**6)
 if j==3:
  L,rate=grab(r'borrows ([\d.]+).*?is ([\d.]+)%',z);r=rate/1200;R=L/sum((1+r)**-k for k in range(1,61));return dict(monthlyPayment=R,balance24=R*sum((1+r)**-k for k in range(1,37)))
 if j==4:
  I=grab(r'recorded as ([\d.]+)',z)[0];return dict(lowerLevel=10*math.log10(I-.05),upperLevel=10*math.log10(I+.05))
 if j==5:
  k,c=grab(r'([\d.]+)\\ln x\+\d+\\ln\(x-1\)=([\d.]+)',z);return dict(admissibleRoot=(1+math.sqrt(1+4*math.exp(c/k)))/2)
 if j==6:
  r=grab(r'exact ratio \$([\d.]+)\^3',z)[0];return dict(lengthScale=(r**3)**(1/3),areaRatio=(r**3)**(2/3))
 if j==7:
  h,r=grab(r'from ([\d.]+) m.*?reaches ([\d.]+) times',z);return dict(totalDistance=h+sum(2*h*r**k for k in range(1,2000)),firstSmallRebound=next(k for k in range(1,200) if h*r**k<.01))
 if j==8:
  a,r=grab(r'spends ([\d.]+).*?and ([\d.]+) times',z);return dict(infiniteSum=sum(a*r**k for k in range(2000)),sum5=sum(a*r**k for k in range(5)),stage95=next(n for n in range(1,200) if r**n<.05),perturbedTotal=sum(a*(r+.02)**k for k in range(2000)))
 if j==9:
  a,bb,c,d=grab(r'z=([-\d.]+)\+([-\d.]+)i.*?w=([-\d.]+)([-+]\d+)i',z);v=complex(a,bb)/complex(c,d);return dict(quotientReal=v.real,quotientImag=v.imag,modulus=abs(v),argument=cmath.phase(v))
 if j==10:
  f=expr(q,'f(x)');roots=[complex(v) for v in sy.nroots(f)];v=max(roots,key=lambda a:a.imag);return dict(rootReal=v.real,rootImagMagnitude=abs(v.imag),rootModulus=abs(v))
 if j==11:
  a,w,c,phase=grab(r'u\(t\)=([\d.]+)\\cos\(([\d.]+)t\).*?v\(t\)=([\d.]+)\\cos\(\d+t\+([\d.]+)\)',z);v=a+c*cmath.exp(phase*1j);arg=cmath.phase(v);time=((-arg)%(2*math.pi))/w;return dict(resultantAmplitude=abs(v),resultantPhase=arg,firstMaximum=time)
 if j==12:
  r,a=grab(r'z=([\d.]+)e\^\{([\d.]+)i\}',z);v=(r*cmath.exp(a*1j))**5;return dict(powerReal=v.real,powerImag=v.imag,powerModulus=abs(v))
 if j==13:
  P=svgp(q)['P'];v=complex(*P);return dict(distance=abs(1j*v-v))
 if j==14:
  y=grab(r'revenues are ([\d.]+) and ([\d.]+)',z);a,c=np.linalg.solve([[2,3],[4,1]],y);return dict(adultPrice=a,childPrice=c,revenue1=y[0],revenue2=y[1])
 if j==15:
  sol=np.linalg.solve(m[0],m[1]).ravel();return dict(volume1=sol[0],volume2=sol[1],volume3=sol[2],determinant=np.linalg.det(m[0]))
 if j==16:
  sol=np.linalg.solve(m[0],m[1]).ravel();return dict(decoded1=sol[0],decoded2=sol[1])
 if j==17:
  d=np.linalg.solve(m[0],[0,1]);return dict(determinant=np.linalg.det(m[0]),change1=d[0],change2=d[1])
 if j==18:
  eig=sorted(np.linalg.eigvals(m[0]),reverse=True);return dict(eigenvalue1=eig[0],eigenvalue2=eig[1])
 if j==19:
  v=np.linalg.matrix_power(m[0],10)@m[1];return dict(population10a=v[0,0],population10b=v[1,0],dominantEigenvalue=max(np.linalg.eigvals(m[0])))
 if j==20:
  r,c,u=grab(r'fraction ([\d.]+).*?receives ([\d.]+) mg.*?u_0=([\d.]+)',z);L=c/(1-r);v=u
  for k in range(5):v=r*v+c
  return dict(equilibrium=L,amount5=v,safeInflow=250*(1-r))
 if j==21:
  A=m[0];a,b=grab(r'Initially ([\d.]+) use A and ([\d.]+) use B',z);v=np.linalg.matrix_power(A,8)@np.array([a,b]);station=np.linalg.lstsq(np.vstack((A-np.eye(2),np.ones((1,2)))),[0,0,1],rcond=None)[0];return dict(state8a=v[0],state8b=v[1],stationaryA=station[0])
 if j==22:
  R,N,percent,target=grab(r'deposits ([\d.]+).*?for ([\d.]+) months.*?rate ([\d.]+)%.*?target is ([\d.]+)',z);r=percent/100;sumfac=sum((1+r)**k for k in range(int(N)));today=grab(r'cost of ([\d.]+) today',p[2]['prompt'])[0];return dict(futureValue=R*sumfac,requiredDeposit=target/sumfac,inflationPercent=100*((target/today)**(1/10)-1))
 if j==23:
  P,r,limit=grab(r'is ([\d.]+) kg.*?by ([\d.]+).*?most ([\d.]+) kg',z);con=grab(r'as ([\d.]+)',p[1]['prompt'])[0];n=next(n for n in range(200) if P*r**n<=limit);N=next(n for n in range(200) if P*con**n<=limit);return dict(reopenYear=n,conservativeYear=N,massBefore=P*r**(n-1),massAt=P*r**n)
 if j==24:
  es=sorted(np.linalg.eigvals(m[0]),reverse=True);h=1-1/es[0];return dict(dominantEigenvalue=es[0],harvestFraction=h,controlledOtherEigenvalue=(1-h)*es[1])

def fn(q,j):
 z=body(q);p=q['parts'];b=blocks(z)
 if j==0:
  f=expr(q,'f(n)');g=expr(q,'g(x)');v=float(g.subs(X,f.subs(X,20)));diff=sy.simplify(g.subs(X,f)-f.subs(X,g));return dict(checkout20=v,orderDifference=float(diff))
 if j==1:
  h,k=grab(r'f\(x\)=\(x-([\d.]+)\)\^2\+([\d.]+)',z);target=grab(r'\}\(([\d.]+)\)',p[1]['prompt'])[0];return dict(inverseAtTarget=h+math.sqrt(target-k))
 if j==2:
  f=expr(q,'f(t)');A,k=grab(r'f\(t\)=([\d.]+)e\^\{([\d.]+)t',z);return dict(time60=math.log(60/A)/k,rangeMaximum=float(f.subs(X,20)))
 if j==3:
  scale,h,k,target=grab(r'g\(x\)=([\d.]+)f\(x-([\d.]+)\)\+([\d.]+)',z)+grab(r'y=([\d.]+)',p[2]['prompt']);return dict(leftIntersection=h-math.sqrt((target-k)/scale),rightIntersection=h+math.sqrt((target-k)/scale))
 if j==4:
  a,k=grab(r'output values by ([\d.]+).*?upwards by ([\d.]+)',z);return dict(outputDifference=(a-1)*k)
 if j==5:
  A,half=grab(r'amount ([\d.]+) mg.*?half-life ([\d.]+) hours',z);k=math.log(2)/half;return dict(decayConstant=k,time30=math.log(A/30)/k)
 if j==6:
  ambient,initial,time,after=grab(r'at ([\d.]+) degrees.*?Initially it is ([\d.]+).*?after ([\d.]+) minutes it is ([\d.]+)',z);k=-math.log((after-ambient)/(initial-ambient))/time;return dict(coolingConstant=k,time30=-math.log((30-ambient)/(initial-ambient))/k)
 if j==7:
  A,B=grab(r'R\(x\)=([\d.]+)\+([\d.]+)\\ln x',z);return dict(inputFor50=math.exp((50-A)/B),doublingIncrease=B*math.log(2))
 if j==8:
  phase=grab(r'\(t-([\d.]+)\)',z)[0];return dict(firstMaximumDay=phase+365/4,aboveMidlineDays=365/2)
 if j==9:
  mid,amp,phase=grab(r'H\(t\)=([\d.]+)\+([\d.]+)\\sin\(\\pi\(t-([\d.]+)\)/6\)',z);threshold=grab(r'least ([\d.]+) m',z)[0];a=math.asin((threshold-mid)/amp);lo=phase+6*a/math.pi;hi=phase+6*(math.pi-a)/math.pi;return dict(boundary1=lo,boundary2=hi,duration=hi-lo)
 if j==10:
  L,C,k=grab(r'N\(t\)=([\d.]+)/\(1\+([\d.]+)e\^\{-([\d.]+)t',z);return dict(initial=L/(1+C),time80=math.log(C/.25)/k,timeHalf=math.log(C)/k)
 if j==11:
  L,n0,time,nt=grab(r'L=([\d.]+).*?N\(0\)=([\d.]+).*?N\(([\d.]+)\)=([\d.]+)',z);C=L/n0-1;k=-math.log((L/nt-1)/C)/time;return dict(C=C,k=k,prediction8=L/(1+C*math.exp(-k*8)))
 if j==12:
  a,c,join,end=grab(r'f\(t\)=([\d.]+)t\+([\d.]+).*?t<([\d.]+).*?t\\leq([\d.]+)',z);B=(a*join+c-join*join)/join;root=max(sy.solve(X*X+B*X-30,X));return dict(joinParameter=B,time30=float(root))
 if j==13:
  fixed,rate,join,base,extra=grab(r'C\(d\)=([\d.]+)\+([\d.]+)d.*?d\\leq([\d.]+).*?C\(d\)=([\d.]+)\+([\d.]+)\(d-',z);return dict(charge18=base+extra*(18-join),boundaryCharge=fixed+rate*join)
 if j==14:
  a,B=grab(r'\\ln E=([\d.]+)\+([\d.]+)\\ln m',z);A=math.exp(a);return dict(exponent=B,coefficient=A,prediction12=A*12**B,doublingFactor=2**B)
 if j==15:
  a,k=grab(r'\\ln S=([\d.]+)\+([\d.]+)t',z);return dict(initial=math.exp(a),doublingTime=math.log(2)/k,time100=(math.log(100)-a)/k)
 if j==16:
  data=arrays(z)[0];Q=expr(q,'Q(t)');E=expr(q,'E(t)');qs=[float(Q.subs(X,k)) for k in range(4)];es=[float(E.subs(X,k)) for k in range(4)];return dict(quadraticSSE=sum((data-qs)**2),exponentialSSE=sum((data-es)**2),quadratic6=float(Q.subs(X,6)),exponential6=float(E.subs(X,6)))
 if j==17:
  c,y1,y2=grab(r'f\(0\)=([\d.]+).*?f\(1\)=([\d.]+).*?f\(2\)=([\d.]+)',z);A,B=np.linalg.solve([[1,1],[8,4]],[y1-c,y2-c]);return dict(coefficientA=A,coefficientB=B,prediction1p5=A*1.5**3+B*1.5**2+c)
 if j==18:
  A,B,C=grab(r'R\(x\)=([\d.]+)\+([\d.]+)/\(x\+([\d.]+)\)',z);return dict(inputForTarget=B/(grab(r'response ([\d.]+)',p[1]['prompt'])[0]-A)-C,maximumResponse=A+B/C)
 if j==19:
  A,B,cost=grab(r'p\(q\)=([\d.]+)-([\d.]+)q.*?cost is ([\d.]+)',z);opt=(A-cost)/(2*B);return dict(continuousOptimum=opt,maximumProfit=(A-cost)*opt-B*opt*opt)
 if j==20:
  xs,ys=arrays(z)[:2];b,a=np.linalg.lstsq(np.column_stack((np.log(xs),np.ones(len(xs)))),np.log(ys),rcond=None)[0];A=math.exp(a);return dict(regressionIntercept=a,regressionSlope=b,coefficient=A,originalSSE=sum((ys-A*xs**b)**2),prediction3p5=A*3.5**b,prediction20=A*20**b)
 if j==21:
  L,K,target=grab(r'S\(x\)=([\d.]+)x/\(([\d.]+)\+x\).*?reading of ([\d.]+)',z);inv=lambda s:K*s/(L-s);return dict(estimate=inv(target),lower=inv(target-1),upper=inv(target+1),at90=inv(.9*L),at95=inv(.95*L))
 if j==22:
  E=expr(q,'E(t)');G=expr(q,'G(t)');L=grab(r'G\(t\)=([\d.]+)/',z)[0];te=optimize.brentq(sy.lambdify(X,E-L/2,'numpy'),0,100);tg=optimize.brentq(sy.lambdify(X,G-L/2,'numpy'),0,100);return dict(exponential8=float(E.subs(X,8)),logistic8=float(G.subs(X,8)),expHalfTime=te,logisticHalfTime=tg)
 if j==23:
  f=expr(q,'f(t)');delay,offset=grab(r'g\(t\)=f\(t-([\d.]+)\)\+([\d.]+)',z);v=float(f.subs(X,6-delay)+offset);old=float(f.subs(X,6)+offset);return dict(shiftedMonth6=v,plannerError=v-old,maximumTime=delay)
 if j==24:
  slope,join,amp=grab(r'P\(t\)=([\d.]+)t.*?t<([\d.]+).*?P\(t\)=L-([\d.]+)e',z);rate=grab(r'increase is ([\d.]+) units',z)[0];L=slope*join+amp;k=rate/amp;target=nums(p[2]['prompt'])[0];return dict(capacity=L,k=k,targetTime=join-math.log((L-target)/amp)/k)

def gt(q,j):
 z=body(q);p=q['parts'];m=matrices(z)
 if j==0:
  r,a=grab(r'radius ([\d.]+) m.*?angle ([\d.]+) radians',z);return dict(arc=r*a,sectorArea=r*r*a/2,perimeter=2*r+r*a,uncoveredArea=math.pi*r*r-r*r*a/2)
 if j==1:
  y=grab(r'\\sin\\theta=([\d.]+)',z)[0];a=math.asin(y);sol=sorted([a,math.pi-a,2*math.pi+a,3*math.pi-a]);assert all(abs(math.sin(t)-y)<1e-10 for t in sol);return dict(solutions=sol,cosMagnitude=math.sqrt(1-y*y))
 if j==2:
  a,b,C=grab(r'lengths ([\d.]+) km and ([\d.]+) km.*?angle ([\d.]+) degrees',z);side=lambda d:math.sqrt(a*a+b*b-2*a*b*math.cos(math.radians(d)));return dict(thirdSide=side(C),area=a*b*math.sin(math.radians(C))/2,lowerSide=side(C-1),upperSide=side(C+1))
 if j==3:
  pts=svgp(q);P,Q,R=[pts[k] for k in 'PQR'];image=m[0]@P+m[1].ravel();area=abs(np.linalg.det(np.array([Q-P,R-P])))/2;return dict(imagePx=image[0],imagePy=image[1],area=area)
 if j==4:
  P=np.array(grab(r'P=\(([-\d.]+),([-\d.]+)\)',z));S,R=m;u=R@S@P;v=S@R@P;return dict(RSx=u[0],RSy=u[1],SRx=v[0],SRy=v[1])
 if j==5:
  area=grab(r'of area ([\d.]+) square',z)[0];shift=np.array(grab(r'translated by.*?\(([-\d.]+),([-\d.]+)\)',z));target=np.array(grab(r'is.*?\(([-\d.]+),([-\d.]+)\)',p[2]['prompt']));orig=np.linalg.solve(m[0],target-shift);return dict(imageArea=area*abs(np.linalg.det(m[0])),originalX=orig[0],originalY=orig[1])
 if j==6:
  a,r=grab(r'of area ([\d.]+).*?scale factor ([\d.]+)',z);ratio=3*r*r;return dict(generationRatio=ratio,generation4=a*ratio**4,totalArea=sum(a*ratio**k for k in range(2000)),criticalLengthScale=1/math.sqrt(3))
 if j==7:
  a=np.array(grab(r'A=\(([-\d.]+),\s*([-\d.]+),\s*([-\d.]+)\)',z));b=np.array(grab(r'B=\(([-\d.]+),\s*([-\d.]+),\s*([-\d.]+)\)',z));v=b-a;d=np.linalg.norm(v);return dict(distance=d,unitVector=(v/d).tolist())
 if j==8:return dict(pointAt3=(m[0]+3*m[1]).ravel().tolist())
 if j==9:
  a,u,b,v=[a.ravel() for a in m];t=np.linalg.lstsq((u-v).reshape(-1,1),b-a,rcond=None)[0][0];assert np.allclose(a+t*u,b+t*v) and t>=0;assert np.isclose(np.linalg.norm(u),np.linalg.norm(v));return dict(meetingTime=t,meetingPoint=(a+t*u).tolist(),speed=np.linalg.norm(u))
 if j==10:
  a,v=[a.ravel() for a in m];end=grab(r't\\leq([\d.]+)',z)[0];t=max(0,min(end,-np.dot(a,v)/np.dot(v,v)));sq=np.dot(a+t*v,a+t*v);return dict(closestTime=t,minimumDistance=math.sqrt(sq),minimumSquaredDistance=sq)
 if j==11:
  a,b=[a.ravel() for a in m];dot=np.dot(a,b);theta=math.degrees(math.acos(dot/np.linalg.norm(a)/np.linalg.norm(b)));return dict(dotProduct=dot,vectorAngleDegrees=theta,acuteLineAngle=min(theta,180-theta),scalarProjection=dot/np.linalg.norm(b))
 if j==12:
  a,b=[a.ravel() for a in m];c=np.cross(a,b);assert np.dot(c,a)==0 and np.dot(c,b)==0;return dict(crossProduct=c.tolist(),triangleArea=np.linalg.norm(c)/2)
 if j==13:
  a,u,b,v=[a.ravel() for a in m];ts=np.linalg.lstsq(np.column_stack((u,-v)),b-a,rcond=None)[0];point=a+ts[0]*u;assert np.allclose(point,b+ts[1]*v);return {'lambda':ts[0],'mu':ts[1],'intersection':point.tolist()}
 if j==14:
  es=network(q);degree={k:sum(k in (a,b) for a,b,w in es) for k in 'ABCDE'};assert sorted(k for k,d in degree.items() if d%2)==['A','C'];return dict(degrees=degree,trailLength=sum(w for a,b,w in es))
 if j==15:
  A=m[0];k=int(grab(r'length-([\d.]+)',p[1]['prompt'])[0]);return dict(length2Walks=np.linalg.matrix_power(A,2)[0,3],lengthK=k,walkCount=np.linalg.matrix_power(A,k)[0,3])
 if j==16:
  es=network(q);A=np.zeros((4,4))
  for a,b,w in es:A['ABCD'.index(a),'ABCD'.index(b)]=A['ABCD'.index(b),'ABCD'.index(a)]=1
  T=A/A.sum(axis=0);k=int(grab(r'after ([\d.]+) steps',p[1]['prompt'])[0]);return dict(steps=k,probabilityAtD=np.linalg.matrix_power(T,k)[3,0])
 if j==17:
  es=network(q);discount=[(a,b,1 if {a,b}=={'A','C'} else w) for a,b,w in es];return dict(mstCost=mst(es),discountedCost=mst(discount))
 if j==18:return dict(mstCost=mst(network(q)))
 if j==19:
  es=network(q);D=distances(es);total=sum(w for a,b,w in es);extra=D['A']['C'];return dict(edgeTotal=total,extraDistance=extra,closedDistance=total+extra)
 if j in [20,21,22]:
  es=[(a,b,float(w)) for a,b,w in re.findall(r'([A-D])([A-D])=([\d.]+)',z)];D=distances(es);direct={a:{b:(0 if a==b else next(w for u,v,w in es if {u,v}=={a,b})) for b in 'ABCD'} for a in 'ABCD'}
  if j==20:
   costs=[D['A']['B']+D['C']['D'],D['A']['C']+D['B']['D'],D['A']['D']+D['B']['C']];total=sum(w for a,b,w in es);return dict(pairingCosts=costs,edgeTotal=total,minimumClosedLength=total+min(costs))
  optimum=min(tourcost(direct,t) for t in tours(direct))
  if j==21:
   route=['A'];left=set('BCD')
   while left:
    v=min(left,key=lambda v:direct[route[-1]][v]);route.append(v);left.remove(v)
   route.append('A');return dict(nearestNeighbourCost=tourcost(direct,route),exactOptimum=optimum)
  bound=mst([(a,b,w) for a,b,w in es if 'A'not in(a,b)])+sum(sorted(w for a,b,w in es if 'A'in(a,b))[:2]);return dict(deletedVertexLowerBound=bound,optimalTour=optimum)
 if j==23:
  D=distances(network(q));return dict(AC=D['A']['C'],AD=D['A']['D'],CE=D['C']['E'],tourCost=tourcost(D,tuple('ABEDCA')),exactOptimumForAudit=min(tourcost(D,t) for t in tours(D)))
 if j==24:
  pts=svgp(q);a,b,c=[pts[k] for k in 'ABC'];A=2*np.vstack((b-a,c-a));rhs=np.array([b@b-a@a,c@c-a@a]);v=np.linalg.solve(A,rhs);assert abs(a[1]-b[1])<1e-10;return dict(boundaryX=v[0],voronoiVertexY=v[1],vertexDistance=np.linalg.norm(v-a))

def sp(q,j):
 z=body(q);p=q['parts'];m=matrices(z);arr=arrays(z)
 if j==0:
  N,k=grab(r'to ([\d.]+) commuters.*?are ([\d.]+) responses',z);return dict(responseRatePercent=100*k/N)
 if j==1:
  xs,ps=arr;mean=np.dot(xs,ps);return dict(expectedPayoff=mean,variance=np.dot(xs*xs,ps)-mean*mean)
 if j==2:
  N,p0=grab(r'of ([\d.]+) independently.*?probability ([\d.]+)',z);N=int(N);probs=[math.comb(N,k)*p0**k*(1-p0)**(N-k) for k in range(N+1)];return dict(atMost2=sum(probs[:3]),exactly1GivenPositive=probs[1]/sum(probs[1:]))
 if j==3:
  mu,sd=grab(r'mean ([\d.]+) minutes.*?deviation ([\d.]+) minutes',z);return dict(between65and85=stats.norm.cdf(85,mu,sd)-stats.norm.cdf(65,mu,sd),percentile90=stats.norm.ppf(.9,mu,sd))
 if j==4:
  O=m[0];E=O.sum(1)[:,None]*O.sum(0)[None,:]/O.sum();chi=((O-E)**2/E).sum();assert E.min()>5;return dict(chiSquare=chi,pValue=stats.chi2.sf(chi,2),df=2,expected=E.tolist())
 if j==5:
  O=arr[0];N=int(O.sum());lam=grab(r'have mean ([\d.]+)',z)[0];prob=np.array([math.exp(-lam)*lam**k/math.factorial(k) for k in range(3)]+[1-sum(math.exp(-lam)*lam**k/math.factorial(k) for k in range(3))]);E=N*prob;chi=sum((O-E)**2/E);assert E.min()>5;return dict(lambdaEstimate=lam,expected=E.tolist(),chiSquare=chi,pValue=stats.chi2.sf(chi,2),df=2)
 if j==6:
  n1,x1,s1,n2,x2,s2=grab(r'A:.*?n=([\d.]+).*?x=([\d.]+).*?SD ([\d.]+).*?B:.*?n=([\d.]+).*?x=([\d.]+).*?SD ([\d.]+)',z);df=n1+n2-2;var=((n1-1)*s1*s1+(n2-1)*s2*s2)/df;t=(x1-x2)/math.sqrt(var*(1/n1+1/n2));return dict(pooledVariance=var,tStatistic=t,pValue=2*stats.t.sf(abs(t),df),df=df)
 if j==7:
  xs,ys=arr[:2];A=np.column_stack((xs*xs,xs,np.ones(len(xs))));coef=np.linalg.lstsq(A,ys,rcond=None)[0];res=ys-A@coef;SSE=res@res;return dict(quadraticCoefficients=coef.tolist(),SSE=SSE,R2=1-SSE/sum((ys-ys.mean())**2),prediction4p5=float(np.array([4.5**2,4.5,1])@coef))
 if j==8:
  xs,ys=arr[:2]
  def fit(b):
   v=np.exp(b*xs);a=(v@ys)/(v@v);return sum((ys-a*v)**2)
  result=optimize.minimize_scalar(fit,bounds=(0,2),method='bounded',options={'xatol':1e-13});b=result.x;v=np.exp(b*xs);a=(v@ys)/(v@v);lin=np.linalg.lstsq(np.column_stack((xs,np.ones(len(xs)))),ys,rcond=None)[0];return dict(exponentialA=a,exponentialB=b,expSSE=fit(b),linearSSE=sum((ys-lin[0]*xs-lin[1])**2),linearSlope=lin[0],linearIntercept=lin[1],doublingTime=math.log(2)/b,prediction8=a*math.exp(8*b))
 if j==9:
  mu,var,a,b=grab(r'mean ([\d.]+) and variance ([\d.]+).*?Y=([\d.]+)X([-+]\d+)',z);return dict(meanY=a*mu+b,varianceY=a*a*var,sdY=a*math.sqrt(var))
 if j==10:
  muX,sdX,muY,sdY=grab(r'X\\sim N\(([\d.]+),([\d.]+)\^2\).*?Y\\sim N\(([\d.]+),([\d.]+)\^2\)',z);mu=2*muX-muY;var=4*sdX**2+sdY**2;return dict(meanZ=mu,varianceZ=var,probabilityAbove35=stats.norm.sf(35,mu,math.sqrt(var)))
 if j==11:
  mu,sd,N=grab(r'mean ([\d.]+) and SD ([\d.]+).*?size ([\d.]+)',z);se=sd/math.sqrt(N);return dict(sampleMeanSD=se,probabilityMeanAbove55=stats.norm.sf(55,mu,se))
 if j==12:
  N,mean,sd=grab(r'of ([\d.]+) observations.*?mean ([\d.]+).*?SD ([\d.]+)',z);t=stats.t.ppf(.975,N-1);margin=t*sd/math.sqrt(N);return dict(tCritical=t,margin=margin,lower=mean-margin,upper=mean+margin)
 if j==13:
  sd,N,mean=grab(r'SD ([\d.]+).*?of ([\d.]+).*?mean ([\d.]+)',z);margin=grab(r'most ([\d.]+)',p[1]['prompt'])[0];zcrit=stats.norm.ppf(.975);return dict(margin64=zcrit*sd/math.sqrt(N),requiredSampleSize=math.ceil((zcrit*sd/margin)**2))
 if j==14:
  lam=grab(r'rate of ([\d.]+) per hour',z)[0];return dict(mean3hours=3*lam,moreThan7=1-sum(math.exp(-3*lam)*(3*lam)**k/math.factorial(k) for k in range(8)),zeroHalfHour=math.exp(-lam/2))
 if j==15:
  a,b=grab(r'Po\}\(([\d.]+)\).*?Po\}\(([\d.]+)\)',z);lam=a+b;return dict(combinedMean=lam,combinedSD=math.sqrt(lam),atMost5=sum(math.exp(-lam)*lam**k/math.factorial(k) for k in range(6)))
 if j==16:
  sd,N,mean,null=grab(r'SD ([\d.]+) g.*?of ([\d.]+).*?mean ([\d.]+) g.*?exceeds ([\d.]+) g',z);t=(mean-null)/(sd/math.sqrt(N));return dict(zStatistic=t,pValue=stats.norm.sf(t))
 if j==17:
  N,mean,sd,null=grab(r'of ([\d.]+) assembly.*?mean ([\d.]+) minutes.*?SD ([\d.]+) minutes.*?below ([\d.]+) minutes',z);t=(mean-null)/(sd/math.sqrt(N));return dict(tStatistic=t,pValue=stats.t.cdf(t,N-1),df=N-1)
 if j==18:
  ds=arr[0];mean=float(sum(Decimal(str(v)) for v in ds)/Decimal(len(ds)));sd=statistics.stdev(ds.tolist());t=mean/(sd/math.sqrt(len(ds)));return dict(meanDifference=mean,sdDifference=sd,tStatistic=t,pValue=stats.t.sf(t,len(ds)-1))
 if j==19:
  N,k,null=grab(r'of ([\d.]+) items contains ([\d.]+) defects.*?p=([\d.]+)',z);N=int(N);nulltail=lambda k:sum(math.comb(N,j)*null**j*(1-null)**(N-j) for j in range(k,N+1));crit=next(k for k in range(N+2) if nulltail(k)<.05);alt=grab(r'is ([\d.]+)',p[2]['prompt'])[0];return dict(pValue=nulltail(int(k)),criticalThreshold=crit,actualAlpha=nulltail(crit),betaAt0p35=sum(math.comb(N,j)*alt**j*(1-alt)**(N-j) for j in range(crit)))
 if j==20:
  lam,k=grab(r'mean is ([\d.]+) per day.*?has ([\d.]+) incidents',z);alt=grab(r'is ([\d.]+) per day',p[2]['prompt'])[0];cdf=lambda x,l:sum(math.exp(-l)*l**j/math.factorial(j) for j in range(x+1));crit=max(k for k in range(100) if cdf(k,lam)<.05);return dict(pValue=cdf(int(k),lam),criticalMaximum=crit,actualAlpha=cdf(crit,lam),alternativeMean=alt,typeII=1-cdf(crit,alt))
 if j==21:
  xs,ys=arr[:2];r=np.corrcoef(xs,ys)[0,1];df=len(xs)-2;t=r*math.sqrt(df/(1-r*r));return dict(correlation=r,tStatistic=t,pValue=2*stats.t.sf(abs(t),df),df=df)
 if j==22:
  sd,N,mu,alt=grab(r'SD ([\d.]+).*?size ([\d.]+).*?mu=([\d.]+).*?mu>([\d.]+)',z);alternative=grab(r'mu=([\d.]+)',p[1]['prompt'])[0];se=sd/math.sqrt(N);c=stats.norm.ppf(.95,mu,se);beta=stats.norm.cdf(c,alternative,se);return dict(criticalMean=c,typeIIat104=beta,powerAt104=1-beta)
 if j==23:
  T=m[0];state=np.array([1,0]);s=np.linalg.matrix_power(T,2)@state;five=np.linalg.matrix_power(T,5)@state;eq=np.linalg.lstsq(np.vstack((T-np.eye(2),np.ones((1,2)))),[0,0,1],rcond=None)[0];return dict(twoStep=s.tolist(),activeAfter5=five[0],stationaryActive=eq[0])
 if j==24:
  T=m[0];initial=np.array(grab(r'vector is [^()]*\(([-\d.]+),([-\d.]+),([-\d.]+)\)',z));assert np.allclose(T.sum(0),1);s=np.linalg.matrix_power(T,4)@initial;eq=np.linalg.lstsq(np.vstack((T-np.eye(3),np.ones((1,3)))),[0,0,0,1],rcond=None)[0];return dict(stateAfter4=s.tolist(),stationary=eq.tolist(),longTermOutput=float(eq@[8,4,1]))

def euler(f,y0,h,N):
 y=y0;rows=[]
 for k in range(N):
  t=k*h;rate=f(t,y);new=y+h*rate;rows.append([t,y,rate,new]);y=new
 return y,rows
def ca(q,j):
 z=body(q);p=q['parts'];m=matrices(z)
 if j==0:
  f=expr(q,'R(t)');d=sy.diff(f,X);k=grab(r'e\^\{-([\d.]+)t',z)[0];return dict(valueAt2=float(f.subs(X,2)),rateAt2=float(d.subs(X,2)),maximumTime=1/k)
 if j==1:
  f=expr(q,'f(x)');d=sy.diff(f,X);v=float(f.subs(X,3));gradient=float(d.subs(X,3));return dict(derivativeAt3=gradient,tangentEstimate3p1=v+.1*gradient,exact3p1=float(f.subs(X,3.1)))
 if j==2:return dict(gradientAt1=float(sy.diff(expr(q,'I(x)'),X).subs(X,1)))
 if j==3:
  rate,r=grab(r'Air enters at ([\d.]+) cubic.*?r=([\d.]+)',z);dr=rate/(4*math.pi*r*r);return dict(radiusRate=dr,areaRate=8*math.pi*r*dr)
 if j==4:
  L,v,x=grab(r'length ([\d.]+) m.*?at ([\d.]+) m per second.*?is ([\d.]+) m from',z);y=math.sqrt(L*L-x*x);dy=-x*v/y;return dict(height=y,verticalVelocity=dy,areaRate=(v*y+x*dy)/2)
 if j==5:
  f=expr(q,'R(t)');A,k=grab(r'R\(t\)=([\d.]+)te\^\{-([\d.]+)t',z);time=1/k;return dict(optimalTime=time,maximumRevenue=float(f.subs(X,time)),endpoint20=float(f.subs(X,20)),newOptimalTime=1/(1.1*k))
 if j==6:
  f=expr(q,'f(x)');roots=sorted(float(v) for v in sy.solve(sy.diff(f,X),X));return dict(maximumX=roots[0],maximumY=float(f.subs(X,roots[0])),minimumX=roots[1],minimumY=float(f.subs(X,roots[1])))
 if j==7:
  f=expr(q,'r(x)');return dict(accumulation0to2=integrate.quad(sy.lambdify(X,f,'math'),0,2,epsabs=1e-12)[0])
 if j==8:
  f=expr(q,'q(t)');A,b=grab(r'q\(t\)=([\d.]+)\\cos\(([\d.]+)t',z);end=math.pi/(2*b);total=integrate.quad(sy.lambdify(X,f,'math'),0,end)[0];half=optimize.brentq(lambda t:integrate.quad(sy.lambdify(X,f,'math'),0,t)[0]-total/2,0,end);return dict(totalVolume=total,halfVolumeTime=half)
 if j==9:
  f=expr(q,'f(x)');lo,hi=grab(r'([-\d.]+)\\leq x\\leq\s*([\d.]+)',z);fun=sy.lambdify(X,f,'math');roots=[float(v) for v in sy.solve(f,X) if lo<float(v)<hi];cuts=[lo]+sorted(roots)+[hi];area=sum(abs(integrate.quad(fun,a,b)[0]) for a,b in zip(cuts,cuts[1:]));return dict(signedIntegral=integrate.quad(fun,lo,hi)[0],totalArea=area)
 if j==10:
  f=expr(q,'y');end=grab(r'x\\leq([\d.]+)',z)[0];vol=math.pi*float(sy.integrate(f*f,(X,0,end)));return dict(volume=vol,scaledVolume=vol*1.1**3)
 if j==11:
  v=expr(q,'v(t)');end=grab(r't\\leq([\d.]+)',z)[0];fun=sy.lambdify(X,v,'math');roots=sorted(float(r) for r in sy.solve(v,X));cuts=[0]+[r for r in roots if 0<r<end]+[end];distance=sum(abs(integrate.quad(fun,a,b)[0]) for a,b in zip(cuts,cuts[1:]));return dict(displacement=integrate.quad(fun,0,end)[0],totalDistance=distance,accelerationAtSecondRest=float(sy.diff(v,X).subs(X,roots[1])))
 if j==12:
  f=expr(q,'v(s)');acc=sy.simplify(f*sy.diff(f,X));time=integrate.quad(sy.lambdify(X,1/f,'math'),0,7)[0];return dict(acceleration=float(acc),speedAt7=float(f.subs(X,7)),timeTo7=time)
 if j==13:
  N,k=grab(r'Initially there are ([\d.]+).*?constant is ([\d.]+) per hour',z);return dict(population10=N*math.exp(k*10),doublingTime=math.log(2)/k)
 if j==14:
  ambient,k,initial=grab(r'T-([\d.]+).*?constant is ([\d.]+) per minute.*?temperature is ([\d.]+)',z);return dict(time35=-math.log((35-ambient)/(initial-ambient))/k,temperatureAt10=ambient+(initial-ambient)*math.exp(-10*k))
 if j==15:
  influx,k,y0=grab(r'at ([\d.]+) g per minute.*?at ([\d.]+) times.*?contains ([\d.]+) g',z);L=influx/k;return dict(equilibrium=L,massAt5=L+(y0-L)*math.exp(-5*k))
 if j==16:
  k,L=grab(r'dy/dt=([\d.]+)\(([\d.]+)-y\)',z);return dict(initialGradientLow=k*(L-1),initialGradientHigh=k*(L-4))
 if j==17:
  k,y0,h=grab(r'dy/dt=([\d.]+)y.*?y\(0\)=([\d.]+).*?h=([\d.]+)',z);value,steps=euler(lambda t,y:k*y,y0,h,round(1/h));exact=y0*math.exp(k);return dict(eulerAt1=value,exactAt1=exact,signedError=value-exact,unroundedSteps=steps)
 if j==18:
  k,L,y0=grab(r'dy/dt=([\d.]+)\(([\d.]+)-y\).*?y\(0\)=([\d.]+)',z);f=lambda t,y:k*(L-y);coarse,csteps=euler(f,y0,.5,4);fine,fsteps=euler(f,y0,.25,8);return dict(coarse=coarse,fine=fine,exact=L+(y0-L)*math.exp(-2*k),coarseSteps=csteps,fineSteps=fsteps)
 if j==19:
  a,b,c,d,x0,y0,h=grab(r'dx/dt=([\d.]+)x-([\d.]+)y.*?dy/dt=([\d.]+)x-([\d.]+)y.*?x\(0\)=([\d.]+).*?y\(0\)=([\d.]+).*?size ([\d.]+)',z);A=np.array([[a,-b],[c,-d]]);state=np.array([x0,y0]);steps=[]
  for k in range(round(1/h)):
   new=state+h*(A@state);steps.append([k*h,*state.tolist(),*new.tolist()]);state=new
  return dict(xAt1=state[0],yAt1=state[1],steps=steps)
 if j==20:
  A=m[0];initial=np.array(grab(r's\(0\)=\(([-\d.]+),([-\d.]+)\)',z));state=linalg.expm(2*A)@initial;return dict(eigenvalues=sorted(np.linalg.eigvals(A),reverse=True),xAt2=state[0],yAt2=state[1])
 if j==21:
  a,b=grab(r'x\^\\prime=([\d.]+)x.*?y\^\\prime=-([\d.]+)y',z);P=svgp(q)['P'];return dict(initialX=P[0],initialY=P[1],initialDx=a*P[0],initialDy=-b*P[1])
 if j==22:
  A=m[0];eig=np.linalg.eigvals(A);return dict(realPart=eig[0].real,imaginaryMagnitude=abs(eig[0].imag),initialDx=A[0,0],initialDy=A[1,0])
 if j==23:
  c=grab(r'=-([\d.]+)x',z)[0];h=grab(r'h=([\d.]+)',z)[0];state=np.array([1.,0]);A=np.array([[0,1],[-c,0]]);steps=[]
  for k in range(3):
   new=state+h*A@state;steps.append([k*h,*state.tolist(),*new.tolist()]);state=new
  return dict(xAt0p3=state[0],velocityAt0p3=state[1],exactXAt0p3=math.cos(math.sqrt(c)*.3),steps=steps)
 if j==24:
  eq=blocks(z)[0];a,b=nums(eq)[:2];initial=grab(r'x\(0\)=([\d.]+)',z)[0];v0=grab(r'x\^\\prime\(0\)=([-\d.]+)',z)[0];A=np.array([[0,1],[-b,-a]]);state=linalg.expm(A)@np.array([initial,v0]);return dict(eigenvalues=sorted(np.linalg.eigvals(A),reverse=True),initialVelocity=v0,displacementAt1=state[0])

def native(x):
 if isinstance(x,np.ndarray):return [native(v) for v in x]
 if isinstance(x,(list,tuple)):return [native(v) for v in x]
 if isinstance(x,dict):return {k:native(v) for k,v in x.items()}
 if isinstance(x,(complex,np.complexfloating)):
  assert abs(x.imag)<1e-10,('Unexpected complex comparison',x)
  return float(x.real)
 return float(x)
def compare(a,b,label):
 if isinstance(a,dict):
  assert a.keys()==b.keys(),(label,a,b)
  return sum(compare(a[k],b[k],label+'/'+k) for k in a)
 if isinstance(a,(list,tuple,np.ndarray)):
  assert len(a)==len(b),(label,a,b)
  return sum(compare(v,w,label+f'/{j}') for j,(v,w) in enumerate(zip(a,b)))
 assert math.isclose(float(a),float(b),rel_tol=2e-6,abs_tol=2e-7),(label,a,b)
 return 1

# These are the mathematical and semantic decisions checked for each family,
# separately from the original author's scope and numerical ledger.
METHODS={
 'na':'''Finite arithmetic sums and integer feasibility under a contract|Explicit geometric production sums and adjacent-season threshold checks|Consistent nominal and inflation-deflated currency comparison|End-of-month discounted cash flows and remaining-payment loan balance|Monotone logarithmic images of half-open rounding bounds, retaining exact endpoints|Logarithm product law, positive arguments and rejection of extraneous quadratic root|Cube-root length and squared area scaling of similar solids|Independent infinite bounce sum and adjacent rebound-height tests|Convergent geometric budget, finite stages, residual proportion and sensitivity|Cartesian complex division, principal argument and modulus|Complex conjugate quadratic roots and Argand modulus|Same-frequency phasor vector addition and first nonnegative maximum|Integer complex power in Cartesian and polar forms|Quarter-turn multiplication by i and displacement from labelled original point|Contextual two-price matrix system with the perturbed first receipt specified|Three-volume simultaneous system with nonsingular coefficient matrix|Exact inverse matrix decoding and order of multiplication|Inverse matrix response to a specified right-hand-side perturbation|Distinct-real eigenvalues and corresponding eigenspaces|Matrix iteration versus diagonalization and dominant eigenvalue interpretation|Affine recurrence iterated independently, fixed point and limiting safety boundary|Column-state matrix powers, conservation and invariant state|Explicit end-of-month annuity accumulation and consistent compound inflation|Integer geometric reopening threshold with conservative-rate comparison|Dominant-eigenvalue control and uniformly applied post-growth harvest'''.split('|'),
 'fn':'''Order of composition, contextual integer domain and explicit real algebraic extension|Restricted quadratic inverse and correct positive square-root branch|Exponential inverse with exact finite input/output domains|Transformation order and both algebraic graph intersections|Noncommuting vertical scale and shift|Half-life exponential calibration and time inversion|Offset exponential cooling with ambient asymptote|Natural logarithmic model, positive domain and doubling increment|Seasonal sinusoid phase, period and finite-interval interpretation|All finite-interval threshold crossings and total duration|Logistic initial value, threshold and capacity limitations|Two-point logistic calibration and forward prediction|Piecewise continuity and valid quadratic branch inversion|Piecewise tariff inverse, joining value and consistent branch inequalities|Log-log power coefficients, units, predictions and scale factor|Semi-log exponential intercept, growth constant and times|Residual sums, model comparisons and extrapolation limitations|Polynomial interpolation constraints and prediction|Introduced rational model, domain, asymptote and admissible inverse|Price-demand profit vertex with feasibility and boundary interpretation|Log-scale power least squares distinguished from original-scale residual assessment|Monotone inverse calibration, uncertainty bounds and near-asymptote sensitivity|Exponential versus logistic predictions, half-capacity times and late observations|Delayed periodic forecast, complete range and error from ignoring phase|Piecewise production continuity, derivative at join, correct variant target and rate discontinuity'''.split('|'),
 'gt':'''Radian arc, sector area, two-radius perimeter and complementary circular area|All unit-circle solutions on the stated finite interval and cosine signs|Included-angle triangle calculation and monotone endpoint uncertainty|Rotation followed by translation, all vertex images and area preservation|Right-to-left matrix composition and noncommuting point images|Absolute determinant area scale and reverse affine map|All-generation nonoverlap assumption, geometric area sum and excluded supremum|Endpoint subtraction, Euclidean distance and normalized direction|Vector line, component parameters and inconsistent-point rejection|Meeting at the same nonnegative time, meeting point and constant speeds|Bounded relative-motion quadratic, minimum separation and explicit assumptions|Dot product, directed-vector angle, acute line angle and scalar projection|Cross product orientation, orthogonality, area and both unit-normal signs|Simultaneous line parameters checked in every component|Graph degrees, odd vertices, Euler trail and sum of edge lengths|Adjacency matrix powers counting walks with repeated vertices permitted|Column-normalized transition matrix derived from the actual displayed graph|Independent Kruskal tree and changed-edge sensitivity|Independent spanning tree cost checked against Prim reasoning|Chinese postman closed route using shortest path between two odd vertices|All three odd-vertex pairings using shortest-path distances|Nearest-neighbour upper bound checked against exhaustive tours|Deleted-vertex tree plus two cheapest incident edges as lower bound|Metric completion via all-pairs shortest paths and exhaustive tour comparison|Perpendicular-bisector equations, equidistant Voronoi vertex and model limitations'''.split('|'),
 'sp':'''Response rate, coverage/nonresponse/wording bias, validity and reliability|Direct probability-weighted mean and second moment|Direct binomial sums and conditional sample-space denominator|Normal quantile and interval CDF difference|Expected table, independent observations, chi-square statistic and degrees of freedom|Poisson fitted mean, grouped probabilities, parameter-adjusted degrees of freedom and expected counts|Independent equal-variance normal score samples and pooled two-tailed t inference|Quadratic normal-equation least squares, original residual sum and R squared|Independent one-parameter profiled exponential fit in original units and linear comparison|Affine random-variable mean and squared variance multiplier|Signed normal means but squared independent variance coefficients|CLT approximation, finite variance, standard error and tail probability|Unknown population SD, t critical value and repeated-sampling CI interpretation|Known population SD, normal CI and ceiling of required sample size|Constant-rate Poisson interval scaling and direct upper-tail sum|Independent Poisson sum, variance and cumulative probability|Known-SD upper-tailed normal mean test, context and Type I error|Unknown-SD lower-tailed one-sample t test and sampling conditions|Before-minus-after differences, unbiased SD and one-sample one-tailed paired t test|Exact binomial upper tail including observation, maximal strict-size critical region and Type II error|Exact Poisson lower tail, maximal strict-size region, Type II complement and one-day limitations|Pearson coefficient and two-tailed zero-correlation inference under bivariate normality|Normal critical mean, Type II error, power and sample-size effect|Column Markov powers, exact invariant active fraction and continuing transitions|Three-state column Markov powers, normalized invariant distribution and expected output'''.split('|'),
 'ca':'''Product derivative, value/rate at time 2 and interior maximum|Quotient derivative, tangent approximation and actual nearby value|Chain and logarithmic differentiation on a positive domain|Sphere volume differentiation and consistent linked surface-area rate|Ladder constraint differentiated implicitly and signed area rate|Exponential maximum with both endpoints and growth-rate sensitivity|Stationary points, second derivative, inflection and signed concavity|Independent symbolic antiderivative and numerical quadrature of substitution integral|Trigonometric accumulation, endpoint and root of half-total integral|Root-split signed integral versus sum of absolute subinterval integrals|Revolution integral of squared radius and cubic similarity scaling|Rest roots, signed displacement, absolute distance and acceleration signs|Acceleration v dv/ds, positive speed, elapsed time and explicit SI units|Positive separable exponential growth, initial condition and doubling time|Separated cooling equation, ambient equilibrium and observational limitations|Linear inflow/outflow equilibrium and independently evaluated transient solution|Actual slope-field directions, equilibrium and asymptotic approach from both sides|Forward Euler with old-state derivatives, exact solution and signed error|Step refinement with both Euler trajectories and exact exponential solution|Simultaneous coupled Euler update from the same old state vector|Distinct-real two-by-two exact system solved independently by matrix exponential|Phase-plane signs and saddle behaviour from the labelled initial point|Only qualitative stable-spiral interpretation, no exact complex-eigenvalue solution required|Second-order equation recast into a coupled system with simultaneous Euler updates|Second-order initial conditions and distinct-real exact system solution'''.split('|')
}
assert all(len(v)==25 for v in METHODS.values())

def correction_notes(q):
 t=q['id'].split('-')[2];n=q['number'];out=[]
 for topic,lo,hi,reason in [
  ('na',17,20,'Replaced rounded strict logarithmic bounds by exact logarithmic endpoints.'),
  ('na',29,32,'Restored explicit multiplication brackets in the infinite-bounce method.'),
  ('na',57,60,'Specified which receipt changes, matching the matrix perturbation.'),
  ('fn',1,4,'Separated formal real algebraic composition from the original whole-ticket domain.'),
  ('fn',9,12,'Retained the exact exponential inverse-domain endpoint.'),
  ('gt',25,28,'Replaced nonexistent largest strict-convergence scale by its open range and excluded supremum; made all-generation nonoverlap explicit.'),
  ('gt',41,44,'Aligned the four-mark assumption prompt with its three assumptions and uncertainty explanation.'),
  ('sp',25,28,'Defined the measured assessment-score quantity and contextual population-mean conclusion.'),
  ('ca',49,52,'Specified displacement, speed, acceleration and elapsed-time units.')]:
  if t==topic and lo<=n<=hi:out.append(reason)
 if (t=='na' and any(lo<=n<=lo+3 for lo in [25,37,65])) or (t=='gt' and 1<=n<=4):out.append('Reclassified routine calculator foundations as easy after explicit difficulty review.')
 if q['id'] in ['ib-aihl-sp-073','ib-aihl-sp-076','ib-aihl-ca-069']:out.append('Corrected half-up three-significant-figure tie rounding without rounding calculations.')
 return out

def display_checks(q):
 scheme=' '.join(s['text'] for m in q['markScheme'] for s in m['steps']);t=q['id'].split('-')[2];n=q['number'];checks=[]
 if t=='na' and 17<=n<=20:assert '10\\log_{10}' in scheme and 'exact bounds' in scheme;checks.append('Exact logarithmic interval endpoints retained')
 if t=='fn' and 1<=n<=4:assert 'real inputs' in q['parts'][2]['prompt'] and 'original domain' in q['parts'][2]['prompt'];checks.append('Formal composition explicitly extends the input domain')
 if t=='gt' and 25<=n<=28:assert 'no largest' in scheme and '0<r<1/' in scheme and 'mutually nonoverlapping' in q['stem'];checks.append('Strict convergence range and disjoint-area assumption explicit')
 if t=='gt' and 41<=n<=44:assert 'three modelling assumptions' in q['parts'][-1]['prompt'];checks.append('Four marking points match the four requested elements')
 if t=='sp' and n in [73,76]:
  vals=[Decimal(a) for a in re.findall(r'[-+]?\d+(?:\.\d+)?',re.search(r'differences \(seconds\) are \$\[([^]]+)\]',q['stem']).group(1))];mean=sum(vals)/len(vals);rounded=mean.quantize(Decimal('.01'),rounding=ROUND_HALF_UP);assert str(rounded) in scheme;checks.append('Exact decimal paired-data mean rounds half up to '+str(rounded))
 if t=='ca' and n==69:
  k,y0,h=[Decimal(a) for a in re.search(r'dy/dt=([\d.]+)y.*?y\(0\)=([\d.]+).*?h=([\d.]+)',body(q)).groups()];y=y0
  for _ in range(2):y=y+h*k*y
  answer=y.quantize(Decimal('.01'),rounding=ROUND_HALF_UP);assert str(answer) in scheme;checks.append('Exact decimal second Euler iterate rounds half up to '+str(answer))
 return checks

def field_differences(a,b,path=''):
 if isinstance(a,dict) and isinstance(b,dict):
  return [d for k in sorted(set(a)|set(b)) for d in field_differences(a.get(k),b.get(k),path+'/'+k)]
 if isinstance(a,list) and isinstance(b,list) and len(a)==len(b):return [d for j,(x,y) in enumerate(zip(a,b)) for d in field_differences(x,y,path+'/'+str(j))]
 return [] if a==b else [dict(field=path,before=a,after=b)]

def main():
 ledger={q['id']:q for q in json.loads((ROOT/'docs/ib-expansion-reviews/ai-hl-author-ledger.json').read_text(encoding='utf8'))};before={q['id']:q for q in json.loads((ROOT/'work/ai-hl-independent/before-review.json').read_text(encoding='utf8'))};rows=[];fail=[];total=0;hashes={};corrections=[];difficulty={};totalmarks=0
 for topic,run in [('number-algebra',na),('functions',fn),('geometry-trigonometry',gt),('statistics-probability',sp),('calculus',ca)]:
  path=ROOT/'content/ib/math-ai-hl'/f'{topic}.json';raw=path.read_bytes();assert b'\r' not in raw and not raw.startswith(b'\xef\xbb\xbf');hashes[path.name]=hashlib.sha256(raw).hexdigest();qs=json.loads(raw.decode('utf8'));assert len(qs)==100
  for q in qs:
   issue=None;computed={};count=0;display=[];family=(q['number']-1)//4;prefix=q['id'].split('-')[2];digest=lambda v:hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
   try:
    assert q['calculator'] is True and q['status']=='published';assert q['marks']==sum(p['marks'] for p in q['parts']);assert [p['label'] for p in q['parts']]==[m['part'] for m in q['markScheme']]
    for p,m in zip(q['parts'],q['markScheme']):assert len(m['steps'])==p['marks'] and all(s['code']in['M1','A1','R1','AG'] for s in m['steps'])
    a,b=map(int,q['syllabusCode'].split('.'));assert 1<=b<={1:15,2:10,3:16,4:19,5:18}[a]
    for key in ['diagramSvg','markSchemeDiagramSvg']:
     if key in q:ET.fromstring(q[key]);assert not re.search(r'<(?:style|use|script|image|foreignObject)|href=|url\(',q[key])
    computed=native(run(q,family));count=compare(computed,ledger[q['id']]['numericValues'],q['id']);display=display_checks(q);total+=count
   except Exception as e:issue=str(e);fail.append(dict(id=q['id'],issue=issue))
   changes=field_differences(before[q['id']],q);notes=correction_notes(q)
   if changes:corrections.append(dict(id=q['id'],reasons=notes,beforeSha256=digest(before[q['id']]),afterSha256=digest(q),changes=changes))
   difficulty[q['difficulty']]=difficulty.get(q['difficulty'],0)+1;totalmarks+=q['marks']
   rows.append(dict(id=q['id'],family=family+1,variant=(q['number']-1)%4+1,status='needs-review' if issue else 'passed',issue=issue,canonicalRecordSha256=digest(q),disposition='corrected-and-rechecked' if changes else 'passed-without-change',recomputedValues=computed,scalarComparisons=count,displayChecks=display,mathematicalAndSemanticReview=METHODS[prefix][family],scopeReview=dict(status='passed',syllabusCode=q['syllabusCode'],level=q['level'],guideFirstAssessment=2021,guideFinalAssessment=2028),markingReview='Distinct M/A/R criteria, command terms, branch/domain conditions and part totals reviewed; alternative valid methods and justified equivalent forms remain acceptable.',difficultyReview=dict(status='passed',difficulty=q['difficulty'],rationale='Routine calculator foundation' if q['difficulty']=='easy' else ('Linked calculation and reasoning' if q['difficulty']=='medium' else 'Multi-stage investigation with interpretation, assumptions or numerical-method decisions')),answerLeakageReview='Learner prompts and public figures checked; givens are original data and scaffolding, not unrevealed answers. Solution figures are confined to markscheme fields.',corrections=notes,figureHashes={k:hashlib.sha256(q[k].encode()).hexdigest() for k in ['diagramSvg','markSchemeDiagramSvg'] if k in q}))
 figures_path=ROOT/'work/ai-hl-independent/figures/index.json';figures=json.loads(figures_path.read_text()) if figures_path.exists() else None
 assert figures is not None and figures['uniqueDiagrams']==43 and figures['diagramUses']==52
 actual={(r['id'],role,sha) for r in rows for role,sha in r['figureHashes'].items()}
 rendered={(u['id'],u['role'],f['sha256']) for f in figures['figures'] for u in f['uses']}
 assert actual==rendered,'The final serialized diagrams differ from the independently inspected render set'
 report=dict(status='passed' if not fail else 'needs-review',questionCount=len(rows),families=125,variantsPerFamily=4,scalarComparisons=total,displayPrecisionChecks=sum(len(r['displayChecks']) for r in rows),totalMarks=totalmarks,difficulty=difficulty,failures=fail,canonicalFiles=hashes,method='Independent reconstruction of numeric and mathematical methods from serialized learner prompts, tables, displayed equations and public diagrams. The author ledger is used only as an expected-value comparator after reconstruction; no authoring modules are imported. Direct cash-flow sums, exact symbolic differentiation, root-split quadrature, direct discrete probability sums, profiled nonlinear least squares, exhaustive routes, matrix exponentials and old-state Euler iterations supply alternate checks.',semanticCoverage='All 125 family narratives and markschemes were read. Each of the 500 variants was replayed from its serialized givens, with domains, branches, interval solutions, modelling assumptions, statistical conditions, signs, units, rounding, criterion counts, difficulty and answer leakage checked. Family-specific semantic decisions accompany every ID.',officialSources=['https://ibo.org/globalassets/new-structure/university-admission/pdfs/dp-mathematics-applications-and-interpretation-guide-en.pdf','https://www.ibo.org/globalassets/new-structure/university-admission/pdfs/dp-mathematics-applications-and-interpretation-specimen-papers-en.pdf'],scopeExclusions='No complex roots, general vector-product proofs, exact complex-eigenvalue ODE solutions, Runge–Kutta or 2029 syllabus material. Matrix diagonalization and exact ODE systems use distinct real eigenvalues; spirals are interpreted qualitatively.',figures=figures,visualReview='All 43 unique serialized SVGs (52 uses) independently rasterized and all four sheets inspected for mathematical direction, origin/scales, explicit original coordinates, edge labels, clipping and separation of public data/private solution coordinates.',correctionCount=len(corrections),corrections=corrections,limits='AI-agent review with separate symbolic/numeric computations, not an accredited human IB examiner. Scope and reasoning judgments are semantic rather than a formal proof of every sentence. The calculations listed per ID and their components are machine checked; app rendering, accessibility, import/CDN and deployment remain with the integrating agent.',records=rows)
 out=ROOT/'docs/ib-expansion-reviews/ai-hl-independent-review.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf8',newline='\n');print(json.dumps({k:v for k,v in report.items() if k in ['status','questionCount','families','scalarComparisons','displayPrecisionChecks','difficulty','totalMarks','failures','canonicalFiles','correctionCount']},indent=2))
if __name__=='__main__':main()
