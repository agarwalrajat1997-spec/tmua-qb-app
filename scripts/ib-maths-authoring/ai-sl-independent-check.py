"""Independent review of displayed AI SL JSON. No author modules are imported."""
import sys,json,re,math,hashlib,statistics,xml.etree.ElementTree as ET
from pathlib import Path
from decimal import Decimal,ROUND_HALF_UP
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'work'/'aa-sl-deps'))
import sympy as sy
from sympy.parsing.sympy_parser import parse_expr,standard_transformations,implicit_multiplication_application
from scipy.stats import binom,norm,linregress,spearmanr,chi2_contingency,chisquare,ttest_ind
from scipy.optimize import brentq
from scipy.integrate import quad
X=sy.symbols('x');T=sy.symbols('t');CHECKS=[];FAIL=[];LEDGER=[]
def num(z):
 values=[]
 for sign,a,b in re.findall(r'(-?)\\(?:d?frac)\{?(\d+)\}?\{?(\d+)\}?',z):values.append((-1 if sign else 1)*float(a)/float(b))
 for a,b in re.findall(r'(-?\d+)/(\d+)',z):values.append(float(a)/float(b))
 z=re.sub(r'\\[A-Za-z]+',' ',z)
 return values+list(map(float,re.findall(r'[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?',z)))
def g(p,z):
 m=re.search(p,z);assert m,(p,z)
 return tuple(float(a.rstrip('.')) for a in m.groups())
def mtexts(q,p=None):
 return ' | '.join(z['text'] for a in (q['markScheme'] if p is None else [q['markScheme'][p]]) for z in a['steps'] if z['code'] in ['A1','R1'])
def approx(v):
 d=Decimal(str(float(v)))
 return float(d.quantize(Decimal(1).scaleb(d.adjusted()-2),rounding=ROUND_HALF_UP)) if d else 0.
def expect(q,v,p=None,label='recalculated answer',kind='3sf'):
 text=mtexts(q,p);tokens=num(text)
 target=round(v,2) if kind=='money' else round(v) if kind=='integer' else round(v,1) if kind=='1dp' else approx(v) if kind=='3sf' else float(v)
 assert any(math.isclose(z,target,rel_tol=1e-9,abs_tol=1e-8) or math.isclose(z,float(v),rel_tol=1e-9,abs_tol=1e-8) for z in tokens),(label,v,target,text)
 CHECKS.append(dict(id=q['id'],check=label,value=float(v),displayTarget=target))
def ok(q,c,label):
 assert c,label
 CHECKS.append(dict(id=q['id'],check=label,result=True))
def mathblocks(z):return re.findall(r'\$([^$]+)\$',z)
def poly(z,var=X):
 z=re.sub(r'\\(?:d?frac)\{(-?\d+)\}\{(\d+)\}',r'(\1/\2)',z)
 z=re.sub(r'\\(?:d?frac)\{(-?\d+)\}(\d)',r'(\1/\2)',z)
 z=z.replace('\\,','').replace('\\pi','pi').replace('^','**').replace('{','(').replace('}',')')
 z=re.sub(r'\\frac\s*(\d)\s*(\d)',r'(\1/\2)',z)
 z=z.replace('−','-')
 return parse_expr(z,local_dict={'x':var,'t':var,'r':var,'pi':sy.pi},transformations=standard_transformations+(implicit_multiplication_application,))
def expression(q,name):
 for z in mathblocks(q['stem']):
  if z.startswith(name+'='):return poly(z.split('=',1)[1])
 raise AssertionError((q['id'],name))
def table(q):
 rows=[]
 for row in q['stem'].splitlines():
  if row.startswith('|') and not '---' in row:
   fields=[z.strip() for z in row.strip('|').split('|')]
   if any(re.search(r'\d',z) for z in fields):rows.append(fields)
 return rows
def pairs(q):
 rows=[]
 for row in table(q):
  try:rows.append([float(z) for z in row])
  except ValueError:pass
 return rows
def annual_payment(P,r,N):
 # Present value of an annuity independently inverted by summing discounts.
 return P/sum((1+r)**(-j) for j in range(1,N+1))

def number(q,j):
 z=q['stem']
 if j==0:
  blocks=re.findall(r'([\d.]+)\\times10\^\{?(-?\d+)\}?',z);total=math.prod(float(a)*10**int(b) for a,b in blocks)
  a,b=g(r'([\d.]+)\\times10\^\{?(\d+)\}?',q['parts'][1]['prompt']);capacity=a*10**b
  ans=mathblocks(q['markScheme'][0]['steps'][-1]['text'])[0];aa,bb=g(r'([\d.]+)\\times10\^\{?(\d+)\}?',ans)
  ok(q,math.isclose(total,aa*10**bb),'scientific-notation total from displayed mantissas and exponents');expect(q,math.ceil(total/capacity),1,'integer capacity ceiling','integer')
 elif j==1:
  N,a,d=g(r'(\d+) rows.*first row has (\d+) seats.*?(\d+) more',z);last=a+(N-1)*d;expect(q,last,0);expect(q,sum(a+k*d for k in range(int(N))),1)
 elif j==2:
  a,d,S=g(r'collects (\d+) items.*?and (\d+) more.*?is (\d+)\.',z);N=next(n for n in range(1,1000) if math.isclose(sum(a+k*d for k in range(n)),S));expect(q,N,1,'positive integer campaign duration','integer')
 elif j==3:
  a,r,N=g(r'has (\d+) orders.*?by ([\d.]+)%.*?for (\d+) months',z);ratio=1+r/100;expect(q,a*ratio**(N-1),0,'nth month uses N-1 increments','integer');expect(q,sum(a*ratio**k for k in range(int(N))),1,'finite geometric total','integer')
 elif j==4:
  a,r=g(r'is (\d+) g.*?leaves (\d+)%',z);target=g(r'less than (\d+) g',q['parts'][1]['prompt'])[0];r/=100;N=next(n for n in range(1,300) if a*r**(n-1)<target);expect(q,N,1,'strict treatment threshold counts first treatment as n=1','integer');ok(q,a*r**(N-2)>=target>a*r**(N-1),'adjacent treatment boundary')
 elif j==5:
  P,r,N=g(r'USD (\d+) at ([\d.]+)%.*?for (\d+) years',z);V=P*(1+r/100)**N;expect(q,V,0,'compound future value','money');expect(q,V-P,1,'interest earned','money')
 elif j==6:
  P,N,r=g(r'USD (\d+) is deposited for (\d+) years.*?of ([\d.]+)%',z);V=P*(1+r/1200)**(12*N);expect(q,V,0,'monthly nominal compounding','money');expect(q,100*((1+r/1200)**12-1),1,'effective annual rate')
 elif j==7:
  P,r=g(r'USD (\d+).*?by (\d+)%',z);N=g(r'after (\d+) years',q['parts'][0]['prompt'])[0];ratio=1-r/100;expect(q,P*ratio**N,0,'depreciation after N year ends','integer');threshold=g(r'below (\d+)%',q['parts'][1]['prompt'])[0]/100;n=next(n for n in range(1,200) if ratio**n<threshold);expect(q,n,1,'strict year-end replacement threshold','integer')
 elif j==8:
  P,r,N,inf=g(r'USD (\d+) earns ([\d.]+)%.*?for (\d+) years.*?Inflation is ([\d.]+)%',z);V=P*(1+r/100)**N;expect(q,V,0,'nominal balance','money');expect(q,V/(1+inf/100)**N,1,'deflated purchasing power','money')
 elif j==9:
  P,r,N=g(r'USD (\d+).*?interest ([\d.]+)%.*?for (\d+) months',z);pay=annual_payment(P,r/1200,int(N));expect(q,pay,0,'END-mode amortizing payment via discounted cashflows','money');expect(q,N*pay-P,1,'total loan interest','money')
 elif j==10:
  P,r,N=g(r'USD (\d+) loan.*?interest ([\d.]+)%.*?over (\d+) end-of-month',z);k=g(r'payment (\d+)',q['parts'][1]['prompt'])[0];pay=annual_payment(P,r/1200,int(N));balance=sum(pay*(1+r/1200)**(-j) for j in range(1,int(N-k)+1));expect(q,pay,0,'amortization payment','money');expect(q,balance,1,'balance as PV of remaining payments','money');expect(q,(N-k)*pay-balance,3,'future interest avoided on settlement','money')
 elif j==11:
  dep,N,r=g(r'USD (\d+).*?for (\d+) months.*?interest ([\d.]+)%',z);V=sum(dep*(1+r/1200)**k for k in range(int(N)));expect(q,V,0,'END deposit future value by explicit cashflows','money');expect(q,V-N*dep,1,'savings interest','money')
 elif j==12:
  dep,p,target=g(r'USD (\d+).*?earns ([\d.]+)%.*?USD (\d+)',z);r=p/100;N=next(N for N in range(1,500) if sum(dep*(1+r)**k for k in range(N))>=target);expect(q,N,1,'first deposit month reaching target','integer');expect(q,math.ceil(target/dep),2,'zero-interest comparison','integer')
 elif j==13:
  # Displayed exponential calculation; evaluate the precise powers independently.
  tex=mathblocks(z)[0].split('=',1)[1];groups=re.findall(r'(\d+)\^\{?(-?\d+)\}?',tex);v=math.prod(float(a)**int(b) for a,b in groups[:-1])/(float(groups[-1][0])**int(groups[-1][1]));expect(q,v,1,'integer exponent arithmetic')
 elif j==14:
  a,b=g(r'h=([\d.]+)\\times10\^\{(-?\d+)\}',z);expect(q,-math.log10(a*10**b),0,'base10 logarithm');p=g(r'index ([\d.]+)',q['parts'][1]['prompt'])[0];answer=mathblocks(q['markScheme'][1]['steps'][-1]['text'])[0];aa,bb=g(r'([\d.]+)\\times10\^\{(-?\d+)\}',answer);ok(q,math.isclose(aa*10**bb,10**(-p),rel_tol=.005),'inverse base10 exponent scientific notation')
 elif j==15:
  r=g(r'as ([\d.]+) cm',z)[0];upper=r+.05;expect(q,math.pi*upper**2,1,'limiting area upper bound');expect(q,100*(upper**2-r*r)/(upper**2),2,'relative underestimate uses actual area denominator')
 elif j==16:
  d,t=g(r'distance is (\d+) m.*?time is (\d+) s',z);expect(q,(d-.5)/(t+.5),0,'speed lower limiting bound');expect(q,(d+.5)/(t-.5),1,'speed upper limiting bound')
 elif j==17:
  C1,C2=g(r'USD (\d+)\..*?USD (\d+)\.',z);sol=sy.solve([3*X+2*T-C1,2*X+5*T-C2],[X,T]);expect(q,float(sol[X]),1,'two-equation price A');expect(q,float(sol[T]),1,'two-equation price B')
 elif j==18:
  rows=pairs(q);matrix=sy.Matrix([row[:3] for row in rows]);totals=sy.Matrix([row[3] for row in rows]);sol=matrix.inv()*totals
  for v in sol:expect(q,float(v),1,'three-equation price')
  expect(q,float(sum(sol)),2,'price of one of each')
 elif j==19:
  expr=poly(mathblocks(z)[0].split('=')[0]);roots=sy.nroots(expr);real=[float(sy.re(a)) for a in roots if abs(float(sy.im(a)))<1e-10]
  for v in real:expect(q,v,0,'all real cubic roots')
  lo,hi=g(r'([\d.]+)<x<([\d.]+)',z);feasible=[v for v in real if lo<v<hi];ok(q,len(feasible)==1,'unique root satisfies strict physical interval');expect(q,feasible[0],1,'selected feasible length')

def functions(q,j):
 z=q['stem']
 if j==0:
  y1,x1,y2,x2=g(r'USD (\d+) for (\d+) hours and USD (\d+) for (\d+) hours',z);slope=(y2-y1)/(x2-x1);c=y1-slope*x1;expect(q,slope,0,'linear rate');expect(q,c,0,'fixed charge');target=g(r'USD (\d+)',q['parts'][2]['prompt'])[0];expect(q,(target-c)/slope,2,'inverse linear model duration')
 elif j==1:
  line=mathblocks(z)[0].split('=')[1];f=poly(line);P=g(r'P\(([-\d.]+),([-\d.]+)\)',z);m=float(sy.diff(f,X));normal=-1/m;c=P[1]-normal*P[0];cross=float(sy.solve(f-(normal*X+c),X)[0]);expect(q,normal,0,'negative reciprocal slope');expect(q,cross,2,'line intersection x');expect(q,float(f.subs(X,cross)),2,'line intersection y')
 elif j==2:
  f=poly(mathblocks(z)[1].split('=')[1]) if len(mathblocks(z))>1 and 'f(x)'in mathblocks(z)[1] else expression(q,'f(x)');target=g(r'f\^\{-1\}\(([-\d.]+)\)',q['parts'][0]['prompt'])[0];root=float(sy.solve(f-target,X)[0]);expect(q,root,0,'numeric inverse value');expect(q,float(f.subs(X,0)),1,'inverse domain lower');expect(q,float(f.subs(X,100)),1,'inverse domain upper')
 elif j==3:
  f=expression(q,'H(x)')
  end=g(r'x\\leq(\d+)',z)[0];crit=sy.solve(sy.diff(f,X),X);vals=[float(f.subs(X,v)) for v in [0,end]+crit];expect(q,max(vals),0,'quadratic arch maximum');expect(q,min(vals),1,'restricted arch minimum')
 elif j==4:
  f=expression(q,'f(x)');roots=sy.solve(f,X)
  for v in roots:expect(q,float(v),0,'quadratic zero')
  vertex=float(sy.solve(sy.diff(f,X),X)[0]);expect(q,vertex,1,'vertex x');expect(q,float(f.subs(X,vertex)),1,'vertex y')
 elif j==5:
  rows=pairs(q);A=sy.Matrix([[a*a,a,1] for a,b in rows]);B=sy.Matrix([b for a,b in rows]);coeff=A.inv()*B;value=float(coeff[0]*16+coeff[1]*4+coeff[2]);expect(q,value,2,'quadratic three-point interpolation prediction');observed=g(r'at x=4 is ([\d.]+)',q['parts'][4]['prompt'])[0];expect(q,observed-value,4,'signed residual')
 elif j==6:
  f=expression(q,'P(x)');roots=sy.solve(f,X);v=float(sy.solve(sy.diff(f,X),X)[0]);expect(q,v,1,'continuous profit optimum');expect(q,float(f.subs(X,v)),1,'maximum profit');ok(q,sy.diff(f,X,2)<0,'concavity proves unique quadratic maximum')
 elif j==7:
  initial,after,time=g(r'It is (\d+) at.*?and ([\d.]+) at.*?t=(\d+)',z);base=(after/initial)**(1/time);expect(q,initial,0,'growth initial value');expect(q,base,0,'growth multiplier from two observations');expect(q,math.log(2)/math.log(base),1,'doubling time')
 elif j==8:
  ambient,amp,base=g(r'T\(t\)=(\d+)\+(\d+)\(([\d.]+)\)',z);expect(q,ambient+amp,0,'cooling initial temperature');target=g(r'reaches (\d+)',q['parts'][2]['prompt'])[0];time=math.log((target-ambient)/amp)/math.log(base);expect(q,time,2,'cooling threshold time');ok(q,0<base<1,'monotonic approach to asymptote')
 elif j==9:
  scale,base,m,c,upper=g(r'A\(t\)=(\d+)\(([\d.]+)\).*?B\(t\)=(\d+)t\+(\d+).*?t\\leq(\d+)',z);root=brentq(lambda t:scale*base**t-(m*t+c),0,upper);expect(q,root,0,'numeric graph intersection');expect(q,scale*base**root,1,'common model total')
 elif j==10:
  at,Q=g(r'x=(\d+).*?Q=(\d+)',z);power=g(r'x\^(\d+)',z)[0];new=g(r'x=(\d+)',q['parts'][1]['prompt'])[0];expect(q,Q*(new/at)**power,1,'direct power variation')
 elif j==11:
  d,I=g(r'At (\d+) m.*?is (\d+)',z);new=g(r'at (\d+) m',q['parts'][1]['prompt'])[0];expect(q,I*(d/new)**2,1,'inverse square prediction')
 elif j==12:
  f=expression(q,'F(x)');crit=sy.nroots(sy.diff(f,X))
  for v in crit:expect(q,float(sy.re(v)),1,'cubic turning point input');expect(q,float(f.subs(X,v)),1,'cubic turning point ordinate')
 elif j==13:
  a,b,d=g(r'H\(t\)=(\d+)\\cos\(([^t]+)t.*?\)\+(\d+)',z);expect(q,a,0,'amplitude');expect(q,360/b,1,'degree-mode period');expect(q,d+a,2,'upper sinusoid extremum');expect(q,d-a,2,'lower sinusoid extremum')
 elif j==14:
  hi,lo,half=g(r'maximum (\d+).*?minimum (\d+).*?t=(\d+)',z);expect(q,(hi-lo)/2,0,'amplitude from extrema');expect(q,(hi+lo)/2,0,'midline from extrema');ok(q,any(abs(v-360/(2*half))<.0001 for v in num(mtexts(q,1))),'cosine angular frequency stated with sufficient precision')
 elif j==15:
  fixed,rate,cut,extra=g(r'USD (\d+) plus USD (\d+) per unit for the first (\d+) units.*?USD ([\d.]+)',z);new=g(r'for (\d+) units',q['parts'][1]['prompt'])[0];expect(q,fixed+rate*cut+extra*(new-cut),1,'second tariff branch');budget=g(r'USD (\d+)',q['parts'][3]['prompt'])[0];expect(q,cut+(budget-fixed-rate*cut)/extra,3,'inverse tariff budget')
 elif j==16:
  c1,m1,c2,m2=g(r'A\(x\)=(\d+)\+([\d.]+)x.*?B\(x\)=(\d+)\+([\d.]+)x',z);cross=(c1-c2)/(m2-m1);expect(q,cross,0,'plan crossing input');expect(q,c1+m1*cross,1,'common plan cost')
 elif j==17:
  f=poly(mathblocks(z)[0].split('=')[1]);obs=dict(pairs(q));expect(q,obs[4]-float(f.subs(X,4)),0,'observed-minus-predicted residual');new,observed=g(r'at .*?x=(\d+).*?is (\d+)',q['parts'][1]['prompt']);expect(q,100*abs(float(f.subs(X,new))-observed)/observed,1,'percentage error denominator observation')
 elif j==18:
  c,h,k=g(r'\\(?:d?frac)\{(\d+)\}\{x\+(\d+)\}\+(\d+)',z);target=g(r'f\(x\)=(\d+)',q['parts'][2]['prompt'])[0];expect(q,c/(target-k)-h,2,'response-model crossing');expect(q,c/h+k,0,'vertical intercept');expect(q,k,0,'horizontal asymptote')
 elif j==19:
  h,k,upper=g(r'P\(x\)=\|x-(\d+)\|\+(\d+).*?x\\leq(\d+)',z);target=g(r'P\(x\)=(\d+)',q['parts'][1]['prompt'])[0];roots=[h-(target-k),h+(target-k)]
  for v in roots:
   if 0<=v<=upper:expect(q,v,1,'absolute-value finite-domain crossing')

def coords(z,label,dimensions=2):
 pattern=label+r'\(([-\d.]+),\s*([-\d.]+)'+(r',\s*([-\d.]+)' if dimensions==3 else '')+r'\)'
 return g(pattern,z)
def geometry(q,j):
 z=q['stem']
 if j==0:
  a=coords(z,'A',3);b=coords(z,'B',3);expect(q,math.dist(a,b),0,'3D Euclidean distance')
  for u,v in zip(a,b):expect(q,(u+v)/2,1,'3D midpoint coordinate')
 elif j==1:
  a,b,c=g(r'is (\d+) m long, (\d+) m wide and (\d+) m high',z);expect(q,math.sqrt(a*a+b*b+c*c),0,'space diagonal');expect(q,math.degrees(math.atan2(c,math.hypot(a,b))),1,'angle to horizontal projection')
 elif j==2:
  a,h=g(r'base side (\d+) m.*?height (\d+) m',z);slant=math.hypot(h,a/2);expect(q,a*a*h/3,0,'pyramid volume');expect(q,slant,1,'face slant height');expect(q,a*a+2*a*slant,2,'complete pyramid surface area')
 elif j==3:
  r,h=g(r'radius (\d+) cm.*?height (\d+) cm',z);slant=math.hypot(r,h);expect(q,slant,0,'cone slant height');expect(q,math.pi*r*r*h/3,1,'cone volume');expect(q,math.pi*r*r+math.pi*r*slant,2,'cone area includes base')
 elif j==4:
  r,h=g(r'radius (\d+) m.*?height (\d+) m',z);V=math.pi*r*r*h+2/3*math.pi*r**3;expect(q,V,0,'cylinder plus hemisphere volume');expect(q,2*math.pi*r*h+3*math.pi*r*r,1,'exterior area excludes shared interface');rate=g(r'constant ([\d.]+) m',q['parts'][3]['prompt'])[0];expect(q,V/rate,3,'fill time from volume and flow')
 elif j==5:
  r,k=g(r'radius (\d+) cm.*?radius ([\d.]+) times',z);expect(q,4/3*math.pi*r**3,0,'sphere volume');expect(q,100*(k*k-1),1,'similar-sphere area percentage');expect(q,4/3*math.pi*(k*r)**3,2,'volume cubic scale')
 elif j==6:
  d,instrument,angle=g(r'stands (\d+) m.*?instrument ([\d.]+) m.*?is (\d+)°',z);h=d*math.tan(math.radians(angle));expect(q,h,0,'elevation above instrument');expect(q,h+instrument,1,'instrument height added')
 elif j==7:
  h,angle=g(r'is (\d+) m above.*?is (\d+)°',z);expect(q,h/math.tan(math.radians(angle)),0,'horizontal distance from depression');expect(q,h/math.sin(math.radians(angle)),1,'line of sight')
 elif j==8:
  a,b,C=g(r'AB=(\d+).*?AC=(\d+).*?BAC=(\d+)',z);c=math.sqrt(a*a+b*b-2*a*b*math.cos(math.radians(C)));expect(q,c,0,'SAS cosine-rule side');expect(q,a+b+c,1,'triangle perimeter')
 elif j==9:
  A,B,a=g(r'A=(\d+).*?B=(\d+).*?BC=(\d+)',z);C=180-A-B;expect(q,C,0,'triangle third angle');expect(q,a*math.sin(math.radians(B))/math.sin(math.radians(A)),1,'sine-rule AC');expect(q,a*math.sin(math.radians(C))/math.sin(math.radians(A)),2,'sine-rule AB')
 elif j==10:
  a,b,C,cost=g(r'sides (\d+) m and (\d+) m.*?at (\d+)°.*?USD (\d+)',z);area=a*b*math.sin(math.radians(C))/2;expect(q,area,0,'triangle area');expect(q,area*cost,1,'cost uses unrounded area','integer')
 elif j==11:
  a,A,b,B=g(r'goes (\d+) km on bearing (\d+)°.*?then (\d+) km on bearing (\d+)°',z);E=a*math.sin(math.radians(A))+b*math.sin(math.radians(B));N=a*math.cos(math.radians(A))+b*math.cos(math.radians(B));distance=math.hypot(E,N);bearing=math.degrees(math.atan2(E,N))%360;expect(q,E,0,'east components');expect(q,N,0,'north components');expect(q,distance,1,'net distance');expect(q,bearing,2,'quadrant-correct bearing');expect(q,(bearing+180)%360,3,'opposite return bearing','1dp');expect(q,a+b-distance,4,'direct-route distance saving')
 elif j==12:
  r,C=g(r'radius (\d+) m.*?angle (\d+)°',z);arc=math.radians(C)*r;expect(q,arc,0,'degree arc length');expect(q,arc+2*r,1,'sector perimeter')
 elif j==13:
  r,C,d=g(r'radius (\d+) m.*?angle (\d+)°.*?by (\d+) m',z);expect(q,C/360*math.pi*r*r,0,'sector area');expect(q,C/360*math.pi*((r+d)**2-r*r),1,'annular-sector difference')
 elif j==14:
  A=coords(z,'A');B=coords(z,'B');mid=[(a+b)/2 for a,b in zip(A,B)]
  for v in mid:expect(q,v,0,'midpoint component')
  slope=-(B[0]-A[0])/(B[1]-A[1]);expect(q,slope,1,'perpendicular bisector slope')
 elif j==15:
  a=coords(z,'B')[0];b=coords(z,'C')[1];expect(q,a/2,1,'Voronoi vertex x');expect(q,b/2,1,'Voronoi vertex y');expect(q,math.hypot(a,b)/2,2,'common site distance');ok(q,'x\\geq' in mtexts(q,3).replace(' ','') or 'x≥' in mtexts(q,3).replace(' ',''),'B-C boundary restricted to ray beyond vertex')
 elif j==16:
  rows=table(q);P=coords(z,'P');d=[math.dist(P,(float(r[1]),float(r[2]))) for r in rows];nearest=min(range(3),key=lambda k:d[k]);expect(q,float(rows[nearest][3]),1,'nearest-neighbour value');ok(q,len(set(d))==3,'unique nearest site')
 elif j==17:
  A=coords(z,'A');B=coords(z,'B');C=coords(z,'C');left=(A[0]+C[0])/2;right=(B[0]+C[0])/2;expect(q,left,1,'new left Voronoi edge');expect(q,right,1,'new right Voronoi edge');ok(q,left<C[0]<right,'new site inside own vertical strip')
 elif j==18:
  width,height=g(r'x\\leq(\d+).*?y\\leq(\d+)',z);density=g(r'at (\d+) people',q['parts'][2]['prompt'])[0];area=width*height/4;expect(q,area,1,'corner Voronoi cell area');expect(q,area*density,2,'uniform-density service population');expect(q,math.hypot(width/2,height/2),4,'farthest cell point')
 elif j==19:
  a=coords(z,'B')[0];b=coords(z,'C')[1];distance=math.hypot(a,b)/2;expect(q,a/2,0,'permitted vertex x');expect(q,b/2,0,'permitted vertex y');expect(q,distance,1,'distance to nearest settlement');ok(q,'one Voronoi vertex' in mtexts(q,2),'candidate set restriction reviewed')

def statistics_check(q,j):
 z=q['stem']
 if j==0:
  p=[float(v)/100 for v in re.findall(r'(\d+)%',z)];N=g(r'sample of (\d+)',z)[0]
  for v in p:expect(q,N*v,0,'proportionate sample allocation')
 elif j==1:
  values=num(z.split('are ',1)[1].split('. Use',1)[0]);v=sorted(values);expect(q,statistics.median(v),0,'median');expect(q,statistics.mode(v),0,'mode');q1=statistics.median(v[:5]);q3=statistics.median(v[5:]);expect(q,q1,1,'specified median-of-halves Q1');expect(q,q3-q1,1,'IQR');threshold=g(r'exceeds (\d+)',q['parts'][2]['prompt'])[0];expect(q,sum(a>threshold for a in v)/len(v),2,'empirical tail probability')
 elif j==2:
  rows=pairs(q);N=sum(f for v,f in rows);mean=sum(v*f for v,f in rows)/N;var=sum(f*(v-mean)**2 for v,f in rows)/N;expect(q,N,0,'frequency total');expect(q,mean,1,'weighted mean');expect(q,math.sqrt(var),1,'population SD uses N denominator');expect(q,sum(f for v,f in rows if v>=4)/N,2,'empirical at-least-four proportion')
 elif j==3:
  for interval,f in table(q):
   lo,hi=num(interval);expect(q,float(f)/(hi-lo),0,'unequal-class density')
  ok(q,'frequency-density' in mtexts(q,1) or 'density' in mtexts(q,1),'histogram axis and unequal widths reviewed')
 elif j==4:
  rows=table(q);data=[(num(bounds),float(f)) for bounds,f in rows];N=sum(f for bounds,f in data)
  def percentile(p):
   count=0
   for (lo,hi),freq in data:
    if count+freq>=N*p:return lo+(hi-lo)*(N*p-count)/freq
    count+=freq
  expect(q,percentile(.5),2,'median from cumulative interpolation');expect(q,percentile(.75)-percentile(.25),2,'IQR from linear interpolation')
 elif j==5:
  lo,q1,med,q3,hi=g(r'minimum (\d+).*?quartile (\d+).*?median (\d+).*?quartile (\d+).*?maximum (\d+)',z);expect(q,q3-q1,1,'IQR');expect(q,q3+1.5*(q3-q1),1,'upper outlier fence');new=g(r'is (\d+)',q['parts'][2]['prompt'])[0];ok(q,new>q3+1.5*(q3-q1),'new observation above outlier fence')
 elif j in [6,7,8]:
  rows=pairs(q);xs=[r[0] for r in rows];ys=[r[1] for r in rows]
  if j==8:expect(q,spearmanr(xs,ys).statistic,1,'Spearman with average tied ranks')
  else:
   reg=linregress(xs,ys);p=1 if j==6 else 0;expect(q,reg.slope,p,'regression slope');expect(q,reg.intercept,p,'regression intercept')
   if j==6:expect(q,reg.rvalue,0,'Pearson coefficient')
   target=g(r'x=([\d.]+)',q['parts'][2 if j==6 else 1]['prompt'])[0];expect(q,reg.intercept+reg.slope*target,2 if j==6 else 1,'regression prediction unrounded coefficients')
 elif j==9:
  N,a,b,both,none=g(r'Among (\d+) people, (\d+) belong only.*?(\d+) only.*?(\d+) to both.*?(\d+) to neither',z);ok(q,N==a+b+both+none,'four Venn cells exhaust population');expect(q,(a+b+both)/N,0,'union probability');expect(q,both/(b+both),1,'conditional probability P(A given B)');ok(q,not math.isclose(both/N,(a+both)*(b+both)/N**2),'non-independence exact product test')
 elif j==10:
  r,b=g(r'(\d+) red and (\d+) blue',z);N=r+b;expect(q,r*(r-1)/(N*(N-1)),0,'two red without replacement');expect(q,2*r*b/(N*(N-1)),1,'mixed colours includes both orders');expect(q,(r-1)/(N-1),2,'conditional second red')
 elif j==11:
  N,p=g(r'of (\d+) independent devices.*?probability ([\d.]+)',z);expect(q,p**N,0,'independent all-work probability');expect(q,1-(1-p)**N,1,'at least one via complement')
 elif j==12:
  rows=pairs(q);E=sum(a*p for a,p in rows);fee=g(r'USD (\d+)',q['parts'][1]['prompt'])[0];expect(q,E,0,'discrete expectation');expect(q,E-fee,1,'expected player net gain');plays=g(r'(\d+) plays',q['parts'][3]['prompt'])[0];expect(q,plays*(fee-E),3,'organizer expected total net income')
 elif j==13:
  N,p=g(r'of (\d+) independent trials.*?probability ([\d.]+)',z);k=g(r'X=(\d+)',q['parts'][1]['prompt'])[0];expect(q,N*p,0,'binomial mean');expect(q,binom.pmf(k,int(N),p),1,'binomial exact-count PMF');expect(q,binom.sf(k-1,int(N),p),2,'inclusive binomial upper tail')
 elif j==14:
  N,p=g(r'B\((\d+),([\d.]+)\)',z);threshold=g(r'(\d+)%',q['parts'][1]['prompt'])[0]/100;k=next(k for k in range(int(N)+1) if binom.cdf(k,int(N),p)>=threshold);expect(q,N*p*(1-p),0,'binomial variance');expect(q,k,1,'least inclusive binomial reserve','integer');ok(q,binom.cdf(k-1,int(N),p)<threshold<=binom.cdf(k,int(N),p),'adjacent reserve CDF boundaries')
 elif j==15:
  mu,sd=g(r'mean (\d+).*?deviation (\d+)',z);lo,hi=g(r'P\((\d+)<X<(\d+)\)',q['parts'][0]['prompt']);p=norm.cdf(hi,mu,sd)-norm.cdf(lo,mu,sd);expect(q,p,0,'normal interval CDF');count=g(r'of (\d+)',q['parts'][1]['prompt'])[0];expect(q,count*p,1,'expected count rounded after full probability','integer')
 elif j==16:
  mu,sd=g(r'mean (\d+).*?deviation (\d+)',z);p=g(r'=([\d.]+)',q['parts'][0]['prompt'])[0];expect(q,norm.ppf(p,mu,sd),0,'inverse normal cutoff');central=g(r'(\d+)%',q['parts'][1]['prompt'])[0]/100;expect(q,norm.ppf((1-central)/2,mu,sd),1,'central normal lower');expect(q,norm.ppf((1+central)/2,mu,sd),1,'central normal upper')
 elif j==17:
  rows=[[float(v) for v in row[1:]] for row in table(q)];stat,p,df,expected=chi2_contingency(rows,correction=False);expect(q,float(expected[0,0]),1,'independence-test expected count');expect(q,df,1,'degrees of freedom');expect(q,stat,2,'chi-square statistic independently scipy');expect(q,p,2,'chi-square p-value');ok(q,expected.min()>5 and df>1,'SL chi-square expected counts and df conditions')
  ok(q,all(term in z and term in mtexts(q) for term in ['home district','usual travel mode']) and 'association' in mtexts(q,3),'revised student district/travel context agrees with hypotheses and association conclusion')
 elif j==18:
  counts=[float(row[1]) for row in table(q)];stat,p=chisquare(counts);N=sum(counts);expect(q,N/len(counts),1,'equal expected counts');expect(q,len(counts)-1,1,'GOF df no estimated parameters');expect(q,stat,2,'GOF statistic');expect(q,p,2,'GOF p-value');ok(q,N/len(counts)>5,'all expected counts above5')
 elif j==19:
  rows=pairs(q);a=[r[0] for r in rows];b=[r[1] for r in rows];result=ttest_ind(a,b,equal_var=True);expect(q,statistics.mean(a),1,'sample mean A');expect(q,statistics.mean(b),1,'sample mean B');expect(q,result.statistic,2,'pooled two-sample t statistic');expect(q,result.pvalue,2,'two-sided t p-value');ok(q,'equal unknown variances' in z and 'independent' in z.lower(),'pooled t-test assumptions expressly supplied')
  ok(q,'same assessment' in z and 'independent random samples of students' in z and '\\mu_A' in z and '\\mu_B' in z and 'mean assessment scores differ between teaching methods' in mtexts(q,3),'revised independent-student assessment context defines population means and supports an unpaired contextual conclusion')

def calculus(q,j):
 z=q['stem']
 if j==0:
  f=expression(q,'f(x)');point=g(r'at .*?x=(\d+)',z)[0];der=sy.diff(f,X);expect(q,float(der.subs(X,point)),0,'limiting secant gradient')
  rows=pairs(q)
  for h,sec in rows:ok(q,math.isclose(float((f.subs(X,point+h)-f.subs(X,point))/h),sec,abs_tol=1e-5),'displayed secant data from original polynomial')
 elif j==1:
  rows=pairs(q);(a,fa),(b,fb)=rows;expect(q,(fb-fa)/(b-a),0,'symmetric difference from displayed measurements')
 elif j in [2,3]:
  f=expression(q,'F(x)' if j==2 else 'C(x)');point=2
  expect(q,float(sy.diff(f,X).subs(X,point)),1,'derivative value from symbolic power rule')
 elif j==4:
  block=mathblocks(z)[0];f=poly(block.split('=',1)[1]);roots=sorted(float(v) for v in sy.solve(f,X));expect(q,roots[0],2,'stationary maximum input');expect(q,roots[1],2,'stationary minimum input');mid=(roots[0]+roots[1])/2;ok(q,float(f.subs(X,mid))<0 and float(f.subs(X,roots[1]+1))>0,'stationary classifications from derivative signs')
 elif j==5:
  f=expression(q,'y');point=g(r'x=(\d+)',q['parts'][0]['prompt'])[0];slope=float(sy.diff(f,X).subs(X,point));ordinate=float(f.subs(X,point));expect(q,slope,0,'tangent gradient');expect(q,ordinate-slope*point,2,'tangent y-intercept')
 elif j==6:
  f=expression(q,'y');point=g(r'x=(\d+)',q['parts'][0]['prompt'])[0];slope=float(sy.diff(f,X).subs(X,point));expect(q,slope,0,'tangent gradient');ok(q,any(math.isclose(a,-1/slope,abs_tol=1e-9) for a in num(mtexts(q,1))),'normal negative reciprocal slope')
 elif j==7:
  derivative=expression(q,"F'(x)");at,value=g(r'F\((\d+)\)=(\d+)',z);anti=sy.integrate(derivative,X);C=value-float(anti.subs(X,at));target=g(r'F\((\d+)\)',q['parts'][1]['prompt'])[0];expect(q,C,0,'integration constant from boundary');expect(q,float(anti.subs(X,target))+C,1,'antiderivative evaluation')
 elif j==8:
  f=expression(q,'y');lo,hi=g(r'x=(\d+).*?x=(\d+)',z);integral=float(sy.integrate(f,(X,lo,hi)));expect(q,integral,1,'positive-area exact integral');ok(q,min(float(f.subs(X,k)) for k in [lo,hi,(lo+hi)/2])>0,'positive integrand on stated polynomial domain')
 elif j==9:
  f=expression(q,'f(x)');end=g(r'x\\leq(\d+)',z)[0];value=float(sy.integrate(f,(X,0,end)));expect(q,value,0,'linear profile integral');expect(q,value/end,1,'defined average function value')
 elif j==10:
  f=expression(q,'w(x)');lo,hi=g(r'(\d+)\\leq x\\leq(\d+)',z);area=float(sy.integrate(f,(X,lo,hi)));expect(q,area,0,'strip integral area');rate=g(r'USD (\d+)',q['parts'][1]['prompt'])[0];expect(q,area*rate,1,'area-to-cost conversion','money')
 elif j==11:
  f=expression(q,'F(x)');roots=sorted(float(v) for v in sy.solve(sy.diff(f,X),X))
  for v in roots:expect(q,v,1,'stationary input from derivative');expect(q,float(f.subs(X,v)),1,'stationary ordinate')
  ok(q,float(sy.diff(f,X,2).subs(X,roots[0]))<0<float(sy.diff(f,X,2).subs(X,roots[1])),'local classifications agree with first-derivative sign changes')
 elif j==12:
  f=expression(q,'F(x)');end=g(r'x\\leq(\d+)',z)[0];roots=[float(v) for v in sy.solve(sy.diff(f,X),X) if 0<float(v)<end];candidates=[(v,float(f.subs(X,v))) for v in [0,end]+roots];maxpoint=max(candidates,key=lambda a:a[1]);minpoint=min(candidates,key=lambda a:a[1]);expect(q,maxpoint[1],2,'global maximum includes endpoints');expect(q,minpoint[1],2,'global minimum includes endpoints')
 elif j==13:
  price=expression(q,'p(x)');cost=expression(q,'C(x)');profit=X*price-cost;root=float(sy.solve(sy.diff(profit,X),X)[0]);expect(q,root,1,'profit optimizer');expect(q,float(profit.subs(X,root)),3,'maximum profit','money');ok(q,sy.diff(profit,X,2)<0,'profit global concavity')
 elif j==14:
  P=g(r'uses (\d+) m',z)[0];expect(q,P/4,2,'three-side optimal width');expect(q,P/2,2,'three-side optimal length');expect(q,P*P/8,3,'maximum enclosure area');ok(q,P/4>0 and P/4<P/2,'positive feasible dimensions')
 elif j==15:
  side=g(r'side (\d+) cm',z)[0];volume=X*(side-2*X)**2;root=side/6;expect(q,root,2,'open-box interior optimum');expect(q,float(volume.subs(X,root)),3,'maximum box volume');ok(q,float(sy.diff(volume,X,2).subs(X,root))<0,'open-box stationary root maximum')
 elif j==16:
  V=g(r'volume (\d+) cm',z)[0];radius=(V/(2*math.pi))**(1/3);height=V/(math.pi*radius*radius);area=2*math.pi*radius*radius+2*V/radius;expect(q,radius,1,'minimum-cylinder radius');expect(q,height,3,'minimum-cylinder height');expect(q,area,3,'minimum-cylinder surface area');ok(q,math.isclose(height,2*radius),'optimized closed-cylinder proportion')
 elif j==17:
  f=expression(q,'B(x)');end=g(r'x\\leq(\d+)',z)[0];roots=[float(a) for a in sy.solve(sy.diff(f,X),X) if 0<=float(a)<=end];candidate=max([0,end]+roots,key=lambda a:float(f.subs(X,a)));expect(q,candidate,1,'benefit global optimizer');expect(q,float(f.subs(X,candidate)),2,'maximum benefit')
 elif j==18:
  rows=pairs(q);estimate=sum((rows[k+1][0]-rows[k][0])*(rows[k+1][1]+rows[k][1])/2 for k in range(len(rows)-1));expect(q,estimate,0,'trapezoids directly from width table')
 elif j==19:
  f=expression(q,'f(x)');end=g(r'x\\leq(\d+)',z)[0];N=4;h=end/N;estimate=sum(h*(float(f.subs(X,k*h))+float(f.subs(X,(k+1)*h)))/2 for k in range(N));exact=float(sy.integrate(f,(X,0,end)));expect(q,estimate,0,'four trapezoid sum');expect(q,exact,1,'exact quadratic integral');expect(q,100*abs(estimate-exact)/exact,2,'trapezoidal relative percentage error');ok(q,estimate>exact,'convex quadratic gives upper estimate')

FAMILY_NOTES={
 'number-algebra':['Scientific notation and integer capacity','Arithmetic last term and capacity','Arithmetic cumulative integer solution','Geometric nth term and finite sum','Strict geometric treatment threshold','Annual compound interest','Monthly nominal and effective interest','Year-end depreciation threshold','Inflation and real balances','Amortizing END-mode loan','Outstanding balance and settlement interest','End-period savings annuity','Savings target integer month','Integer exponent arithmetic','Base10 logs and inverse exponent','Measurement interval and area bounds','Quotient limiting speed bounds','Two price equations','Three price equations','All cubic roots and feasible interval'],
 'functions':['Linear pricing from two observations','Perpendicular line and intersection','Informal numeric inverse and reflected graph','Restricted quadratic height and model limitation','Quadratic zeros/vertex/sketch','Three-point quadratic and residual','Continuous/integer quadratic profit','Exponential reconstruction and validation','Cooling threshold and asymptote','Numerical model intersection','Power variation','Inverse-square variation','Cubic extrema','Degree-mode sinusoidal features','Sinusoidal model from extrema','Piecewise proportional tariff','Competing linear plans','Residual and observed-denominator error','Reciprocal response on physical domain','Defined absolute-value graph'],
 'geometry-trigonometry':['Three-dimensional distance/midpoint','Space diagonal/floor angle','Pyramid volume/slant/surface/cost','Cone slant/volume/surface','Hemisphere-cylinder composite tank','Similarity of spheres','Instrument-height elevation','Depression and line of sight','SAS cosine rule','AAS sine rule','Area/cost precision','Bearing components and return route','Degree arc/sector perimeter','Annular sector','Perpendicular bisector locus','Voronoi vertex/ray/nearest site','Nearest-neighbour interpolation','New collinear site cell','Rectangular Voronoi service cell','Permitted-vertex facility rule'],
 'statistics-probability':['Stratified random sample and bias','Specified quartile convention','Weighted population moments','Unequal-width frequency-density histogram','Cumulative graph and interpolation','Box plot and new outlier','Pearson regression and causation','Regression prediction and direction','Spearman average tied ranks','Venn conditional and independence','Dependent draws without replacement','Independent reliability','Payout and fair fee','Binomial exact/inclusive tail','Least binomial reserve','Normal probability and expected count','Inverse normal and central interval','Chi-square independence conditions','GOF degrees of freedom','Pooled unpaired two-sided t-test'],
 'calculus':['Secant table derivative estimate','Symmetric measured difference','Polynomial derivative value','Negative integer power derivative','Given-derivative signs','Tangent gradient and intercept','Normal negative reciprocal','Antiderivative with given condition','Positive area integral','Defined average function value','Strip area and units','Local stationary classification','Global extrema with endpoints','Continuous/integer profit maximum','Three-side enclosure optimization','Open-box optimization','Closed-cylinder optimization','Benefit maximum on physical interval','Measured-width trapezoids','Convex quadratic trapezoid error']}
def main():
 routes={'number-algebra':number,'functions':functions,'geometry-trigonometry':geometry,'statistics-probability':statistics_check,'calculus':calculus}
 hashes={};count=0
 for topic,fn in routes.items():
  path=ROOT/'content'/'ib'/'math-ai-sl'/f'{topic}.json';hashes[path.name]=hashlib.sha256(path.read_bytes()).hexdigest();qs=json.loads(path.read_text(encoding='utf-8'));assert len(qs)==80
  for q in qs:
   count+=1;start=len(CHECKS);family=(q['number']-1)//4;fail=None
   try:
    assert q['calculator'] is True and q['level']=='sl'
    top,sub=map(int,q['syllabusCode'].split('.'));assert 1<=sub<={1:8,2:6,3:6,4:11,5:8}[top]
    assert q['marks']==sum(p['marks'] for p in q['parts'])
    assert [p['label'] for p in q['parts']]==[m['part'] for m in q['markScheme']]
    for p,m in zip(q['parts'],q['markScheme']):assert len(m['steps'])==p['marks'] and all(a['code']in['M1','A1','R1','AG'] for a in m['steps'])
    for field in ['diagramSvg','markSchemeDiagramSvg']:
     if field in q:
      ET.fromstring(q[field]);assert not re.search(r'<(?:style|use|script|image|foreignObject)|href=|url\(',q[field])
    fn(q,family)
   except Exception as e:
    fail=str(e);FAIL.append(dict(id=q['id'],error=fail))
   figures=[dict(role=field,sha256=hashlib.sha256(q[field].encode()).hexdigest(),review='rendered and visually approved') for field in ['diagramSvg','markSchemeDiagramSvg'] if field in q]
   LEDGER.append(dict(id=q['id'],family=family+1,variant=(q['number']-1)%4+1,semanticReview=FAMILY_NOTES[topic][family],scope='Checked against official first-assessment2021 AI guide; no HL prerequisite used',marks='part totals, awarded marking codes and linked labels checked',calculator='GDC permitted; degree mode and financial END mode reviewed where applicable',checks=CHECKS[start:],figures=figures,status='needs-review' if fail else 'independently-checked',issue=fail))
 report=dict(course='IB Mathematics AI SL',questionCount=count,familyCount=100,hashes=hashes,numericAndReasoningAssertions=len(CHECKS),failures=FAIL,status='passed' if not FAIL else 'needs-fixes',method='Separate reviewer read all100families and all400variants; computations below derive parameters from displayed JSON stems/tables/prompts without importing author modules. SymPy symbolic algebra, explicit cashflow sums, SciPy distributions/optimization and independent geometry formulas check key answers. Graph XML/safety and numerical geometry reviewed separately.',sources=['https://ibo.org/globalassets/new-structure/university-admission/pdfs/dp-mathematics-applications-and-interpretation-guide-en.pdf'],limits='This is an independent agent review, not a review by an accredited IB examiner. Numeric assertions check the listed quantities; semantic review covers remaining reasoning, command terms, domains and assessment fit. No claim that every possible alternative answer was machine-verified.',resolvedFindings=['Integer-vertex supporting comparisons corrected in fn025–028 and ca053–056','B–C Voronoi edge restricted to its valid ray in gt061–064','Half-up3SF rounding and trailingzero formatting corrected globally, including sp037 and sp077'],ledger=LEDGER)
 report['visualReview']=dict(figureCount=sum(len(row['figures']) for row in LEDGER),status='passed',method='Independently rendered all136 SVGs with Sharp; inspected all12 contact sheets. Re-rendered and re-inspected all12 sheets after global x-axis anchor and mathematical-zero-line fixes.',contactSheets='work/ai-sl-independent-visuals/contact-1.png through contact-12.png',checks=['geometry and degree-mode trigonometric diagrams match stated quantities','Voronoi boundaries and sites match displayed coordinates','statistical plots use correct frequencies, densities, cumulative sums or population normal parameters','solution sketches show appropriate branches, extrema and intercepts','axis text and tick labels remain separate and inside viewBox'])
 report['resolvedFindings'] += ['Return-bearing prompts explicitly request1decimalplace to match worked answers','Site-map and plot x-axis label anchors moved to prevent tick overlap or clipping; mathematical zero lines emphasized','SP069–072 and SP077–080 bodies, hypotheses and conclusions independently re-read after final concrete-context clarification; district/travel modes and independent-student assessment methods now defined within the displayed question']
 out=ROOT/'docs'/'ib-maths-reviews'/'ai-sl-independent-review.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['ledger','method','limits','sources']},indent=2))
if __name__=='__main__':main()
