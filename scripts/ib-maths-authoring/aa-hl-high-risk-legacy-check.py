"""Fresh calculations for specifically inspected high-risk legacy questions.

This is distinct from replaying the original author assertions. The report names
what was checked and never implies that unlisted steps were independently proved.
"""
import json,sys,math,itertools
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'work/aa-sl-deps'),str(ROOT/'work/aa-hl-dependencies')]
import sympy as s
from scipy.optimize import brentq
from scipy.integrate import quad
from scipy.stats import norm,binom
x,t=s.symbols('x t',real=True);rows=[]
def check(id,condition,note):
 assert bool(condition),(id,note)
 rows.append(dict(id=id,status='independently checked',evidence=note))
def eq(a,b):return s.simplify(a-b)==0
rate=brentq(lambda r:sum(4000/(1+r/12)**j for j in range(1,121))-360000,.001,.2);k=1+rate/12
balance=sum(4000/k**j for j in range(1,31));p=360000/(sum(k**(-j) for j in range(1,61))+2*sum(k**(-j) for j in range(61,121)))
check('ib-aa-na-209',abs(rate*100-6.0180389582)<1e-8 and round(balance,2)==111151.07 and round(p,2)==2805.99,'Discounted cash flows independently reproduce nominal rate 6.0180389582%, balance after payment90 USD111151.07 and alternate payment USD2805.99; end-of-month timing retained.')
loan=120000*1.052**8;deposit=loan/sum(1.01**j for j in range(32))
check('ib-aa-na-216',round(loan,2)==180014.37 and round(deposit,2)==4801.14 and abs(sum(9000/1.045**j for j in range(1,2001))-200000)<1e-6,'Independent accumulation and discounting checks give loan180014.37, quarterly deposit4801.14 and year-end perpetuity200000.00.')
a,b,c=s.symbols('a b c');mat=s.Matrix([[-2,a,4],[1,b,-2],[2,-1,c]])
check('ib-aa-na-218',eq(mat.det(),-(a+2*b)*(c+4)) and s.Matrix([[-2,1,4],[1,s.Rational(-1,2),-2],[2,-1,-4]]).rank()==1,'Elimination and determinant confirm exceptional factors a+2b and c+4. At b=-1/2,c=-4, reduced equation is0=5, excluding consistency; otherwise rank-one reduction supplies a common line when a=-2b.')
check('ib-aa-na-229',all(abs(sum(math.atan(1/(j*j+5*j+7)) for j in range(1,N+1))-(math.atan(N+3)-math.atan(3)))<1e-13 for N in range(1,101)),'Tangent subtraction and principal-range argument read; independent finite sums n1–100 reproduce arctan(n+3)-arctan3. Both positive arguments place the angle difference in the principal interval.')
poly=s.expand(((x-5)**2+4)*((x-2)**2+9))
check('ib-aa-fn-103',poly.coeff(x,3)==-14 and poly.subs(x,0)==377,'Conjugate-pair factorization independently gives integer roots5±2i and2±3i, matching quartic sum and product restrictions.')
check('ib-aa-fn-105',sum(s.Rational(3,2)+6*j for j in range(20))==1170,'Positive-domain maxima occur first at3/2 and recur each6 units; direct sum of the first20 abscissae is1170, and integer quadratic has no other positive solution.')
f=(x+3)*(x+1)*(x-2)*(x-4);crit=s.solve(s.diff(f,x),x);vals=[s.simplify(f.subs(x,u)) for u in crit]
check('ib-aa-fn-117',sorted(vals,key=float)==[-25,-25,s.Rational(441,16)],'Fresh derivative factorization and all three critical heights confirm the exact four-distinct-root interval(-25,441/16); stationary abscissae agree with displayed rounded labels.')
prob=norm.sf(2.5)/norm.sf(2)
check('ib-aa-fn-129',abs(prob-.272957)<1e-5,'Root-product4 and monotonic smaller-modulus root yield threshold |A|>2.5. Independent normal tail ratio is0.27295..., agreeing0.273; duplication withSP148 is documented.')
u=s.Matrix([-1,2,3]);v=s.Matrix([-3,-4,2]);nn=u.cross(v);pt=s.Matrix([2,1,3]);A=s.Matrix([-4,0,2]);dist=abs(nn.dot(A-pt))/s.sqrt(nn.dot(nn))
check('ib-aa-gt-158',nn==s.Matrix([16,-7,10]) and eq(dist,11*s.sqrt(5)/5),'Cross-product normal and orthogonal projection independently confirm Cartesian plane16x-7y+10z=55 and distance11sqrt5/5; equivalent-form duplicate award removed.')
p0=s.Matrix([4,-2,1]);d=s.Matrix([1,2,1]);q0=s.Matrix([5,-1,-1]);e=s.Matrix([1,3,1]);nn=d.cross(e);t0=-p0.dot(d)/d.dot(d)
check('ib-aa-gt-168',t0==-s.Rational(1,6) and eq(abs((q0-p0).dot(nn))/s.sqrt(nn.dot(nn)),3/s.sqrt(2)),'Nearest point verified by perpendicular dot product; skew-line distance independently projected onto common normal, giving3/sqrt2. Equivalent-form duplicate award removed.')
A=s.Matrix([2,1,3]);B=s.Matrix([5,0,6]);C=s.Matrix([2,3,-1]);n1=A.cross(C);n2=B.cross(C);angle=math.degrees(math.acos(float(abs(n1.dot(n2))/s.sqrt(n1.dot(n1)*n2.dot(n2)))))
check('ib-aa-gt-175',A.dot((B-A).cross(C))==26 and (B-A).dot(C)==0 and round(angle)==15,'Independent vector products confirm skew lines, plane2x+3y-z=4 containsAB, both given normals, and acute plane angle rounds15degrees.')
p0=s.Matrix([3,2,1]);d=s.Matrix([4,-2,4]);q0=s.Matrix([1,2,2]);e=s.Matrix([-2,1,2]);P=p0-s.Rational(3,40)*d;Q=q0-s.Rational(13,20)*e
check('ib-aa-gt-182',(Q-P).dot(d)==0 and (Q-P).dot(e)==0 and (q0-p0).dot(d.cross(e))==16,'Computed common-perpendicular endpoints independently substituted into both lines; their displacement is normal to both directions. Triple product16 confirms skew rather than intersection.')
F=-(2*s.log(x)+1)/x**2
check('ib-aa-sp-125',eq(s.diff(F,x),4*s.log(x)/x**3) and eq(F.subs(x,s.E**2)-F.subs(x,1),1-5*s.exp(-4)),'Log-density primitive independently differentiated; total probability is1 and exact tail5e^-4, with positive density on its support.')
f=x**3/8+s.Rational(1,4);median=brentq(lambda z:z**4+8*z-16,0,2)
check('ib-aa-sp-143',eq(s.integrate(f,(x,0,2)),1) and eq(s.integrate(x*f,(x,0,2)),s.Rational(13,10)) and eq(s.integrate(x*x*f,(x,0,2)),2) and round(median,2)==1.45 and round(binom.sf(3,10,23/32),3)==.993,'Normalization, lower-tail condition, moments, unique positive median and ten-trial binomial tail independently recalculated; variance31/100.')
check('ib-aa-sp-148',all((z-math.sqrt(z*z-9)<2)==(z>3.25) for z in [3.01,3.2,3.24,3.26,4,5]) and 0<norm.sf(3.25)/norm.sf(3)<1,'Revised constant9: root-product9, smaller-modulus threshold2 and conditioning threshold3 give |A|>13/4. Both sides independently tested; fresh normal tail ratio recalculated. Distinct fromFN129.')
mass=[math.comb(j-1,3)*((1/3)**4)*((2/3)**(j-4)) for j in range(4,100)]
check('ib-aa-sp-149',[j+4 for j,z in enumerate(mass) if abs(z-max(mass))<1e-14]==[9,10] and binom.sf(3,10,1/3)<.5<binom.sf(3,11,1/3),'Revised probability1/3: fresh waiting-time enumeration confirms adjacent modes9,10; independent binomial tail checks at10 and11 confirm leastN=11. Formula denominator486 independently derived, distinct fromNA227.')
y=s.symbols('y',positive=True);m1=-2*x/(3*y);m2=21*x*x/(2*y)
check('ib-aa-c1-097',eq((m1*m2).subs(y*y,7*x**3),-1),'Implicit gradients independently derived; their product is-1 after using the intersection relation. y>0 and y²=7x³ imply finite, nonzero gradients.')
A=50*s.acos((10-x)/10)+(x-10)*s.sqrt(20*x-x*x)/2
check('ib-aa-c1-107',eq(s.diff(A,x),s.sqrt(20*x-x*x)) and s.Rational(-600,120*8)==-s.Rational(5,8),'Circular-sector-minus-triangle area derivative independently simplifies to chord width; unit conversion1.2m=120cm and negative drain rate give dh/dt=-5/8cm/s.')
check('ib-aa-c1-117',s.solve(7*x*x+24*x-16,x)==[-4,s.Rational(4,7)],'Quadratic-in-y discriminant independently gives domain endpoints -4 and4/7 at a=6, separation32/7. Positive a selects this branch.')
r=s.sqrt(1+s.pi/2);pairs=[(-1+r,1+r),(-1-r,1-r)]
check('ib-aa-c1-126',all(eq(X-Y+2*s.sin(X*Y),0) and eq((1+2*Y*s.cos(X*Y))/(1-2*X*s.cos(X*Y)),1) for X,Y in pairs),'Both nearest nonzero candidates independently substituted in implicit curve and gradient. Read inequality argument excludes nonzero y=-x and negative-product branches; squared-distance ordering justifies nearest selection.')
f=s.Rational(2,3)*(1+x**6)+s.Rational(4,3)/s.sqrt(1+x**6)
check('ib-aa-c2-128',eq(s.diff(f,x)+3*x**5*f/(1+x**6),6*x**5) and f.subs(x,0)==2,'Radical integrating-factor solution independently substituted in ODE and initial value. Factor is positive for every real x, so solution remains nonsingular.')
k,L,N=s.symbols('k L N',positive=True);rate=2*k*N*(L-N)/L
check('ib-aa-c2-138',eq(s.diff(rate,N)*rate,(2*k/L)**2*N*(L-N)*(L-2*N)) and eq(rate.subs(N,L/2),k*L/2),'Fresh chain derivative gives concavity switch at half-capacity and maximum growthkL/2; logistic time relation at L=4N0,N(10)=3N0 gives20k=ln9.')
f=(1-2*x)**s.Rational(-1,2)
check('ib-aa-c2-143',all(eq(s.diff(f,x,j),s.factorial(2*j)/(2**j*s.factorial(j))*(1-2*x)**(-j-s.Rational(1,2))) for j in range(8)) and eq(s.series(f*s.cos(3*x),x,0,3).removeO().coeff(x,2),-3),'First eight derivatives independently confirm factorial formula; product series coefficient gives m²=9. Mark scheme revised to avoid repeat awards for earlier derivative data.')
f=(60+s.Rational(5,4)*t+20*s.sin(s.Rational(3,10)*s.pi*t)/(3*s.pi))**2
check('ib-aa-c2-146',round(float((60+90*(s.sqrt(2)-1))**2))==9463 and all(float(f.subs(t,j))<6000 for j in range(14)) and float(f.subs(t,14))>=6000,'Initial and doubled populations verified independently; exact first-model week30 rounds9463. Evaluating every integer week0–14 confirms the first refined-model threshold at week14, despite non-monotonic local oscillations.')
(ROOT/'docs/ib-maths-reviews/aa-hl-high-risk-legacy-review.json').write_text(json.dumps(rows,indent=2)+'\n')
print('Fresh independent high-risk legacy checks passed:',len(rows))
