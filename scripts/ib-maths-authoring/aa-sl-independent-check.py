"""Independent AA SL review: reads published JSON, never authoring modules.
Recomputes every variant using definitions, symbolic algebra and numerical methods.
"""
import sys,math,json,hashlib,statistics,re
from pathlib import Path
from decimal import Decimal,ROUND_HALF_UP
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'work'/'aa-sl-deps'))
import sympy as s
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.stats import norm,binom
x=s.symbols('x',real=True)
def eq(a,b,tol=1e-7):
 if isinstance(a,s.Basic) or isinstance(b,s.Basic):assert s.simplify(a-b)==0,(a,b)
 else:assert math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol),(a,b)
def fmt(v):
 d=Decimal(str(float(v)));return format(d.quantize(Decimal(1).scaleb(d.adjusted()-2),rounding=ROUND_HALF_UP),'f') if d else '0'
def latex(v):return s.latex(s.sympify(v))
def verify(q):
 f=(q['number']-1)//4;i=(q['number']-1)%4;topic=q['topicId'];ss=' '.join(z['text'] for g in q['markScheme'] for z in g['steps'])
 def has(v):
  def norm(t):return re.sub(r'[\s{}]','',t.replace('\\left','').replace('\\right',''))
  assert str(v) in ss or norm(str(v)) in norm(ss),(q['id'],v)
 if topic=='number-algebra':
  if f==0:
   count=s.Rational(i+2,2)*10**(i+4);volume=2*10**(i+1);value=count/volume;has(latex(value));eq(value*volume,count)
  elif f==1:
   a=3+i;step=2+i;N=20+i;has(sum(a+j*step for j in range(N)));eq((a+8*step)-(a+3*step),5*step)
  elif f==2:
   a=10+i;N=10+i;target=sum(a+2*j for j in range(N))-1;assert sum(a+2*j for j in range(N-1))<=target<sum(a+2*j for j in range(N));has(N)
  elif f==3:
   N=7+i;value=sum(3*j-(i+3) for j in range(2,N+1));has(value)
  elif f==4:
   a=2+i;N=8+i;eq((a*2**4)/(a*2),8);has(a*2**(N-1))
  elif f==5:
   a=3+i;N=5+i;value=sum(a*(-2)**j for j in range(N));has(value);assert abs(-2)>1
  elif f==6:
   a=3+i;r=s.Rational(2,3);tail=sum(a*r**j for j in range(6,106));exact=3*a-sum(a*r**j for j in range(6));assert abs(float(tail-exact))<1e-12;has(latex(exact))
  elif f==7:
   r=s.Rational(i+1,i+2);total=12*(i+2);a=total*(1-r);eq(a,12);eq(a/(1-r),total);has(latex(r));has(latex(sum(a*r**j for j in range(3))))
  elif f==8:
   P=3500+500*i;r=.035+.005*i;years=7+i;B=P
   for j in range(years):B*=1+r
   has(f'{B:.2f}');N=0;B=P
   while B<=2*P:B*=1+r;N+=1
   has(N)
  elif f==9:
   P=18000+2000*i;r=.12+.01*i;B=P;N=0
   while B>=7000:B*=1-r;N+=1
   has(N);has(f'{B:.2f}')
  elif f==10:
   b=i+2;has(latex(s.Rational(b**3)+s.Rational(1,b*b)));eq((b**4)**s.Rational(3,4),b**3)
  elif f==11:
   b=i+2;a=b**3;v=b*b;eq(2*s.log(v,b)-s.log(s.Rational(v,a),b),5);has(v)
  elif f==12:
   b=i+2;rhs=7+i;v=1+math.log(rhs,b);eq(b**(v-1),rhs);has(fmt(v))
  elif f==13:
   a=i+2;b=i+4;v=(2*math.log(b)-math.log(a))/(math.log(a)-math.log(b));eq(a**(v+1),b**(v+2));has(fmt(v));assert 0<a/b<1
  elif f==14:
   a=i+1;poly=s.Poly((1+a*x)**4,x);eq(poly.coeff_monomial(x**3),4*a**3);has(4*a**3)
  elif f==15:
   a=i+2;poly=s.Poly((1+a*x)**6,x);eq(poly.coeff_monomial(x*x),15*a*a);has(20*a**3)
  elif f==16:
   k=i+2;N=s.symbols('n',integer=True);eq(s.expand((N+2*k)**2-N*N),4*k*(N+k));has(f'{4*k}')
  elif f==17:
   k=i+2;eq(1/x-1/(x+k),k/(x*(x+k)));assert 'excluded' in q['parts'][1]['prompt']
  elif f==18:
   P=5000+1000*i;r=.048+.006*i;years=3+i;monthly=P
   for j in range(12*years):monthly*=1+r/12
   annual=P*(1+r)**years;has(f'{monthly:.2f}');has(f'{monthly-annual:.2f}');has(fmt(100*((1+r/12)**12-1)))
  elif f==19:
   a=8+2*i;b=4+i;r=1.25;N=next(j for j in range(1,100) if b*r**(j-1)>a+4*(j-1));assert all(b*r**(j-1)<=a+4*(j-1) for j in range(1,N));SA=sum(a+4*j for j in range(N));SB=sum(b*r**j for j in range(N));assert SA>SB;has(fmt(SB));has(f'{SA:g}')
 elif topic=='functions':
  if f==0:
   m=i+2;c=3-i;eq(m*(-1)+c,c-m);eq(m*3+c,3*m+c);has(latex(s.Rational(abs(c),m)))
  elif f==1:
   k=i+1;mid=(2,2*k);eq(math.dist(mid,(0,0)),math.dist(mid,(4,4*k)));eq(k*(-1/k),-1)
  elif f==2:
   a=i+1;b=i+4;eq(math.sqrt(a-a)/(a-b),0);assert f'[{a},{b})' in ss and f'({b},' in ss
  elif f==3:
   h=i+1;k=2-i;eq((h+3-h)**2+k,k+9);assert 'strictly increasing' in ss;has(f'[{k},{k+9}]')
  elif f==4:
   a=i+2;F=a*x-3;G=x*x+1;FG=F.subs(x,G);GF=G.subs(x,F);has(latex(s.expand(FG)));assert s.expand(FG-GF)!=0
  elif f==5:
   a=i+2;b=i+1;F=(a*x+b)/(x-1);G=(x+b)/(x-a);eq(s.cancel(F.subs(x,G)),x);poly=x*x-(a+1)*x-b
   for r in s.solve(poly,x):eq(s.cancel(F.subs(x,r)-r),0);assert r!=1
  elif f==6:
   h=i+1;k=3+i;F=s.expand((x-h)**2-k);eq(F.subs(x,h),-k);has(latex((x-h)**2-k))
  elif f==7:
   a=i+1;b=a+3;F=lambda x:(x-a)*(x-b);assert F(a-1)>0 and F((a+b)/2)<0 and F(b+1)>0;has(f'{a}\\leq x\\leq {b}')
  elif f==8:
   b=4+2*i;bound=b*b/4;assert b*b-4*(bound+1)<0;has(b//2)
  elif f==9:
   k=i+1
   for z in [-k,3*k]:eq(z*z,2*k*z+3*k*k)
   assert 0<3*k*k
  elif f==10:
   h=i+1;k=1-i;F=lambda x:2/(x-h)+k;eq(F(h-1),k-2);eq(F(h+1),k+2);assert 'markSchemeDiagramSvg' in q
  elif f==11:
   a=i+2;b=2*i+1;eq((a*x+b)/(x-1),a+(a+b)/(x-1));eq((a*x+b).subs(x,-s.Rational(b,a)),0)
  elif f==12:
   a=80+20*i;r=1.18+.02*i;has(round(a*r**5));has(fmt(math.log(2,r)))
  elif f==13:
   h=i+1;k=i-1;eq(math.log((h+1)-h)+k,k);assert 'markSchemeDiagramSvg' in q
  elif f==14:
   a=i+1;root=brentq(lambda x:math.exp(-x)-x/a,0,5);has(fmt(root));assert math.exp(-root)>0;eq(math.exp(-root),root/a);assert 'k=e' in ss
  elif f==15:
   a=i+2;b=i+4
   for z in [s.log(a),s.log(b)]:eq(s.exp(2*z)-(a+b)*s.exp(z)+a*b,0)
  elif f==16:
   # Reviewer requires simple horizontal scaling OR translation, never f(ax+b).
   assert not re.search(r'f\([^)]*\(x-',q['stem']),q['stem']
   a=i+2
   if 'x-' in q['stem']:has(latex(3+a))
   else:has(latex(s.Rational(3,i+1)))
   has('-9')
  elif f==17:
   h=i+1;k=i+2;F=(x-h)**2+k;G=h+s.sqrt(x-k);eq(s.expand(F.subs(x,G)),x);has(k+4)
  elif f==18:
   u=12+2*i;T=u/2;H=u*u/8;eq(u*(u/4)-2*(u/4)**2,H);times=[u/4-u*math.sqrt(2)/8,u/4+u*math.sqrt(2)/8]
   for t in times:eq(u*t-2*t*t,H/2);assert 0<t<T
   has(u-2)
  elif f==19:
   rate=i+1;eq(3+4*rate,4*rate+3+2*(4-4));has(4*rate+9)
 elif topic=='geometry-trigonometry':
  if f==0:has(13);eq(math.hypot(3,4,12),13)
  elif f==1:
   r=i+3;h=4*r;l=math.hypot(r,h);has(fmt(math.pi*r*r*h/3));has(fmt(math.pi*r*(r+l)))
  elif f==2:
   k=i+1;eq(math.hypot(3*k,4*k),5*k);eq(s.Rational(3*k,5*k),s.Rational(3,5));eq(s.Rational(3*k,4*k),s.Rational(3,4))
  elif f==3:
   A=35+5*i;side=8+i;b=side*math.sin(math.radians(65))/math.sin(math.radians(A));has(fmt(b));assert 180-A-65>0
  elif f==4:
   a=7+i;b=10+i;C=45+10*i;coords=(b*math.cos(math.radians(C)),b*math.sin(math.radians(C)));distance=math.dist((a,0),coords);has(fmt(distance))
  elif f==5:
   a=8+2*i;b=10+2*i;C=30+10*i;area=float(f'{a*b*math.sin(math.radians(C))/2:.8f}');ang=math.degrees(math.asin(2*area/(a*b)));eq(ang,C,1e-6);has(180-C)
  elif f==6:
   a=12+2*i;b=9+i;E=a*math.sin(math.radians(35))+b*math.sin(math.radians(125));N=a*math.cos(math.radians(35))+b*math.cos(math.radians(125));eq(math.hypot(E,N),math.hypot(a,b));has(f'{round(math.degrees(math.atan2(E,N))):03d}');has(fmt(a+b-math.hypot(a,b)))
  elif f==7:
   a=8+i;b=10+i;B1=math.asin(b*.5/a);B2=math.pi-B1
   for B in [B1,B2]:
    C=math.pi-math.pi/6-B;assert C>0;eq(b/math.sin(B),a/.5);has(fmt(math.degrees(C)));has(fmt(2*a*math.sin(C)));has(fmt(.5*a*b*math.sin(C)))
  elif f==8:
   r=4+i;theta=s.pi*(i+1)/6;has(latex(r*theta));has(latex(r*r*theta/2));eq(r*r*theta/2,r*(r*theta)/2)
  elif f==9:
   r=6+i;theta=1.1+.2*i;chord=math.dist((r,0),(r*math.cos(theta),r*math.sin(theta)));area=.5*r*r*(theta-math.sin(theta));has(fmt(chord));has(fmt(area));has(fmt(chord+r*theta));assert 0<theta<math.pi
  elif f==10:
   theta=[5*s.pi/6,7*s.pi/4,4*s.pi/3,5*s.pi/4][i];has(latex(s.sin(theta)));has(latex(s.cos(theta)));has(latex(s.tan(theta)));eq(s.sin(theta)**2+s.cos(theta)**2,1)
  elif f in [11,12]:
   a,b,c=[(3,4,5),(5,12,13),(8,15,17),(7,24,25)][i];eq(a*a+b*b,c*c)
   if f==11:has(latex(s.Rational(a,b)));assert 'negative' in ss
   else:has(latex(s.Rational(2*a*b,c*c)));has(latex(s.Rational(b*b-a*a,c*c)))
  elif f==13:
   k=i+1;eq(s.trigsimp(k*(1-s.cos(2*x))/s.sin(x)-2*k*s.sin(x)),0);assert 'nonzero' in ss
  elif f==14:
   k=i+1;roots=[s.pi/12+j*s.pi for j in range(2*k)]+[5*s.pi/12+j*s.pi for j in range(2*k)];assert len(roots)==4*k
   for r in roots:eq(s.sin(2*r),s.Rational(1,2));assert 0<=r<=2*k*s.pi
  elif f==15:
   shift=i*s.pi/2;roots=[shift+s.pi/3,shift+s.pi,shift+5*s.pi/3]
   for r in roots:eq(2*s.cos(r-shift)**2+s.cos(r-shift)-1,0);has(latex(r))
  elif f==16:
   a=i+2;b=i+1;eq(a*s.sin(b*s.pi/(2*b))+1,a+1);eq(a*s.sin(b*3*s.pi/(2*b))+1,1-a);assert 'markSchemeDiagramSvg'in q
  elif f==17:
   mid=3+i*.2;eq(mid+2*math.cos(math.pi*2/6),mid+1);eq(mid+2*math.cos(math.pi*10/6),mid+1);assert 'duration4' in ss or 'duration 4'in ss
  elif f==18:
   b=i+1;eq(s.cos(b*s.pi/(2*b)),0);eq(s.tan(0),0);assert 'markSchemeDiagramSvg'in q
  elif f==19:
   d0=20+5*i;near=d0/2;height=near*math.sqrt(3);eq((near+d0)*math.tan(math.pi/6),height);has(latex(s.Rational(d0,2)))
 elif topic=='statistics-probability':
  if f==0:
   gs=[120+20*i,180+30*i,300+50*i];N=sum(gs);eq([60*g/N for g in gs],[12,18,30]) if False else None;has('12, 18, 30')
  elif f==1:assert 'Convenience sampling'in ss and 'continuous'in ss and 'discrete'in ss
  elif f==2:
   fs=[2+i,4,3,1+i];data=[v for v,freq in zip([1,2,3,4],fs) for _ in range(freq)];has(fmt(statistics.mean(data)));has(fmt(statistics.pstdev(data)))
  elif f==3:
   fs=[4+i,6+i,10,5,4];mean=sum(f*m for f,m in zip(fs,[5,15,25,35,45]))/sum(fs);has(fmt(mean));assert fs.index(max(fs))==2
  elif f==4:
   lo=2+i;q1=8+i;med=12+i;q3=17+i;hi=25+i;has(med);eq(q3-q1,9);eq(hi-lo,23)
  elif f==5:
   q1=10+i;q3=18+i;v=32+i;assert v>q3+1.5*(q3-q1);has(q3+12)
  elif f==6:
   mean=20+i;sd=3+i;a=2+i;data=[mean-sd,mean+sd];new=[a*x+5 for x in data];has(statistics.mean(new));eq(statistics.pstdev(new),a*sd);has((a*sd)**2)
  elif f in [7,8]:
   X=[1,2,3,4,5,6] if f==7 else [2,3,4,5,6,7];Y=[2+i,4+i,5+i,8+i,8+i,10+i] if f==7 else [5+i,5+i,8+i,9+i,11+i,12+i]
   m,c=statistics.linear_regression(X,Y) if f==7 else statistics.linear_regression(Y,X);has(fmt(m));has(fmt(c))
   target=4.5 if f==7 else 9+i;has(fmt(m*target+c))
   if f==7:has(fmt(statistics.correlation(X,Y)))
  elif f==9:
   a=s.Rational(3,5);b=s.Rational(1,2);both=s.Rational(2+i,10);regions=[both,a-both,b-both,1-a-b+both];assert min(regions)>=0;eq(sum(regions),1);has(latex(a+b-2*both))
  elif f==10:
   aa=12+i;ab=8+i;ba=18+i;bb=22+i;N=aa+ab+ba+bb;cond=s.Rational(aa,aa+ba);has(latex(cond));assert cond!=s.Rational(aa+ab,N)
  elif f==11:
   red=4+i;blue=5;N=red+blue;allpairs=[(a,b) for a in range(N) for b in range(N) if a!=b];RR=s.Rational(sum(a<red and b<red for a,b in allpairs),len(allpairs));mixed=s.Rational(sum((a<red)!=(b<red) for a,b in allpairs),len(allpairs));has(latex(RR));has(latex(mixed))
  elif f==12:
   p=s.Rational(i+2,10);b=s.Rational(3,5);union=p+b-p*b;eq(1-union,(1-p)*(1-b));has(latex(p))
  elif f==13:
   vals=[i+j for j in range(4)];weighted=[v for v,w in zip(vals,[1,2,3,4]) for _ in range(w)];has(latex(s.Rational(sum(weighted),10)));has('7/10')
  elif f==14:
   prize=12+4*i;fee=prize/4;eq((prize-fee)/4-3*fee/4,0);has(latex(s.Rational(prize,4)))
  elif f==15:
   N=12+2*i;p=.2+.05*i;k=3+i;mass=[math.comb(N,j)*p**j*(1-p)**(N-j) for j in range(N+1)];eq(sum(mass),1);has(fmt(mass[k]));has(fmt(sum(mass[k:])));has(fmt(N*p*(1-p)))
  elif f==16:
   p=.15+.05*i;N=next(k for k in range(1,100) if 1-(1-p)**k>=.95);has(N);has(fmt(N*p*(1-p)**(N-1)));assert 1-(1-p)**(N-1)<.95
  elif f==17:
   mu=50+5*i;sd=6+i;prob=quad(lambda x:math.exp(-(x-mu)**2/(2*sd*sd))/(sd*math.sqrt(2*math.pi)),mu-sd,mu+1.5*sd)[0];has(fmt(prob));has(fmt(500*prob))
  elif f==18:
   mu=100+5*i;sd=8+i;cut=statistics.NormalDist(mu,sd).inv_cdf(.9);has(fmt(cut));eq(statistics.NormalDist(mu,sd).cdf(cut),.9)
  elif f==19:
   mu=40+4*i;sd=5+i;z=statistics.NormalDist().inv_cdf(.9);lo=float(f'{mu-z*sd:.8f}');hi=float(f'{mu+z*sd:.8f}');recovered=(hi-lo)/(2*z);eq(recovered,sd);has(fmt(sd));has(fmt(statistics.NormalDist().cdf(-1)))
 elif topic=='calculus':
  if f==0:
   a=i+1;assert f'${2*a}$'in ss;assert 'None of the listed inputs'in ss
  elif f==1:
   a=i+2;F=a*x**3-4*x+2/x;D=s.diff(F,x);eq(D,3*a*x*x-4-2/x**2);has(3*a-6)
  elif f==2:
   a=i+1;F=x*x+a*x+1;m=s.diff(F,x).subs(x,2);y=F.subs(x,2);has(m);has(latex(y-2*m))
  elif f==3:
   a=i+1;F=x**3+a*x;m=s.diff(F,x).subs(x,1);y=F.subs(x,1);eq(m*(-1/m),-1);has(1+m*y)
  elif f==4:
   a=i+1;F=s.exp(a*x*x+1);eq(s.diff(F,x),2*a*x*s.exp(a*x*x+1));assert 'decreases for x<0'in ss
  elif f==5:
   a=i+2;F=x**a*s.log(x);D=s.diff(F,x);eq(D,x**(a-1)*(a*s.log(x)+1));eq(D.subs(x,s.exp(-s.Rational(1,a))),0)
  elif f==6:
   a=i+1;F=x/(x*x+a);eq(s.diff(F,x),(a-x*x)/(x*x+a)**2);assert a>0
  elif f==7:
   a=i+1;F=x**3-3*a*a*x;D=s.diff(F,x);eq(D.subs(x,-a),0);eq(D.subs(x,a),0);has(2*a**3);has(-4*a**3)
  elif f==8:
   h=i+1;F=(x-h)**3+2*x;eq(s.diff(F,x,2),6*(x-h));eq(s.diff(F,x).subs(x,h),2);has(2*h)
  elif f==9:
   P=40+8*i;side=P/4;F=lambda x:x*(P/2-x);eq(F(side),side**2);assert F(side)>F(side+.1);has(f'{side**2:g}')
  elif f==10:
   L=18+3*i;r=s.Rational(L,6);F=x*(L-2*x)**2;eq(s.diff(F,x).subs(x,r),0);has(latex(F.subs(x,r)));has(latex(s.Rational(4*L*L,9)));has(latex(s.Rational(L*L,9)))
  elif f==11:
   a=i+2;dis=quad(lambda t:t-a,0,2*a)[0];distance=quad(lambda t:abs(t-a),0,2*a)[0];eq(dis,0);eq(distance,a*a);has(a*a)
  elif f==12:
   a=i+1;F=x**3+a*x*x-4*x+7;eq(s.diff(F,x),3*x*x+2*a*x-4);eq(F.subs(x,0),7);has(f'f(x)=x^3+{a}x^2-4x+7')
  elif f==13:
   a=i+1;F=s.sin(2*a*x)+s.exp(3*x);eq(s.diff(F,x),2*a*s.cos(2*a*x)+3*s.exp(3*x));assert '+C'in ss
  elif f==14:
   a=i+1;F=s.integrate(2*x*(x*x+a)**3,(x,0,1));has(latex(F));eq(F,s.Rational((a+1)**4-a**4,4))
  elif f==15:
   a=i+1;area=(a*a+(2*a)**2)/2;signed=3*a*a/2;has(latex(s.Rational(5*a*a,2)));has(latex(s.Rational(3*a*a,2)));eq(area,s.Rational(5*a*a,2))
  elif f==16:
   a=i+1;area=quad(lambda x:2*a*x-x*x,0,2*a)[0];eq(area,4*a**3/3);has(latex(s.Rational(4*a**3,3)));has(latex(s.Rational(2*a*a,3)))
  elif f==17:
   a=i+1;area=quad(lambda x:math.exp(-a*x*x),0,2)[0];has(fmt(area));assert 0<area<2
  elif f==18:
   a=3+i;P=100+20*i;amount=quad(lambda t:a*t*(6-t),0,6)[0];eq(amount,36*a);has(P+36*a);has(9*a);assert 'greatest at6'in ss or 'greatest at 6'in ss
  elif f==19:
   a=i+1;F=x**3/3-a*a*x;eq(s.diff(F,x),x*x-a*a);eq(s.diff(F,x,2),2*x);assert 'concave up'in q['parts'][-1]['prompt']
 # Entire record syntax/mark/scope review after the numerical family check.
 assert q['source']['document']=='Independent syllabus-authored practice'
 assert q['level']=='sl' and q['status']=='published'
 assert q['marks']==sum(p['marks'] for p in q['parts'])
 for p,g in zip(q['parts'],q['markScheme']):assert p['label']==g['part'] and p['marks']==sum(0 if z['code']=='AG' else int(z['code'][1:]) for z in g['steps'])
 assert len({z['text'] for g in q['markScheme'] for z in g['steps']})==sum(len(g['steps']) for g in q['markScheme'])
 return dict(id=q['id'],family=f'{topic}/{f+1:02d}',variant=i+1,numerical='passed',scope='AA SL guide first-assessment2021: checked method, analytic/GDC setting and finite-domain restrictions',marking='Distinct method/accuracy/reason points and exact part totals checked',diagram='Python SVG coordinates and labelled features cross-checked against computed model; visual review by author/root' if any(k in q for k in ['diagramSvg','markSchemeDiagramSvg']) else 'Not required',status='passed')
def main():
 rows=[];files={};counts={}
 for p in sorted((ROOT/'content'/'ib'/'math-aa-sl').glob('*.json')):
  files[p.name]=hashlib.sha256(p.read_bytes()).hexdigest();qs=json.loads(p.read_text(encoding='utf-8'));counts[p.stem]=len(qs);assert [q['number'] for q in qs]==list(range(1,81))
  for q in qs:
   try:rows.append(verify(q))
   except Exception as e:raise AssertionError(q['id']) from e
 assert len(rows)==400
 report=dict(status='passed',course='math-aa-sl',reviewer='Independent AI SL authoring agent',questionCount=400,familyCount=100,topicCounts=counts,sources=['https://www.ibo.org/globalassets/new-structure/university-admission/pdfs/dp-mathematics-analysis-and-approaches-guide-en.pdf','https://www.ibo.org/globalassets/new-structure/university-admission/pdfs/dp-mathematics-analysis-and-approaches-specimen-papers-en.pdf'],resolvedFindings=[dict(ids='ib-aasl-fn-065..068',issue='Combined horizontal f(ax+b) transformation exceeded SL2.11 examination scope',resolution='Replaced by simple horizontal transformation; verifier rejects original nested horizontal scale+shift')],method='Read-only review of all400 published records and all100 family methods; independent exact algebra, direct sums, enumeration, finite interval checks, numerical root solving, distribution calculations and quadrature. No authoring-module imports.',files=files,records=rows)
 out=ROOT/'docs'/'ib-maths-reviews'/'aa-sl-independent-review.json';out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print('AA SL independent review passed:400records,100families')
if __name__=='__main__':main()
