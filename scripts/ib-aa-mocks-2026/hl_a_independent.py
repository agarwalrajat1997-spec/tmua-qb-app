"""Independent AA HL Set A review. Uses only Python's standard library.

The numerical evidence below was calculated afresh from the reconstructed
questions, not imported from the author script. Proofs, domain restrictions,
native solution pages and seven SVGs were also read independently. Numerical
checks supplement that review; they are not presented as proofs of identities.
"""
from __future__ import annotations

import cmath
import hashlib
import json
import math
from pathlib import Path
import re
from statistics import NormalDist
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
PAPERS = ROOT / 'content/ib/aa-mocks-2026/papers'
OUT = ROOT / 'docs/ib-aa-mocks-2026/hl-a-independent-review.json'
FROZEN = {
    1: 'c7afe1df55a0d4c8da75d45e3aa71044bca2b0526355c0814a037c3215699391',
    2: '0d23ecdb2b208af15f106d1e5d06fec365e3c9f9681123a7534da20dbf0c2d6b',
    3: 'c91729d2c6ee924993e5abea54a5d5cc9778c0c54a05b95ffc130e3e93464246',
}
data = {i: json.loads((PAPERS / f'aa-hl-set-a-paper-{i}.json').read_text(encoding='utf-8')) for i in (1, 2, 3)}
reviews = {}
checks = 0


def start(paper, number, reasoning):
    question = data[paper]['questions'][number - 1]
    key = (paper, number)
    reviews[key] = {
        'paper': f'aa-hl-set-a-paper-{paper}', 'question': number,
        'status': 'passed', 'marks': question['marks'],
        'sourcePages': question['sourcePages'], 'nativeSourcePagesRead': True,
        'stemAndFullSchemeRead': True, 'independentReasoning': reasoning,
        'diagramInspected': bool(question.get('diagramSvg')),
        'parts': {x['label']: {'marks': x['marks'], 'evidence': []} for x in question['parts']},
    }
    return key


def record(key, part, description, actual, expected=True, tolerance=0):
    global checks
    if tolerance:
        passed = abs(actual - expected) <= tolerance
    else:
        passed = actual == expected
    assert passed, (key, part, description, actual, expected)
    checks += 1
    def portable(value):
        return {'real': value.real, 'imag': value.imag} if isinstance(value, complex) else value
    reviews[key]['parts'][part]['evidence'].append({
        'check': description, 'actual': portable(actual), 'expected': portable(expected),
        'tolerance': tolerance, 'passed': True,
    })


def close(key, part, description, actual, expected, tolerance=1e-10):
    record(key, part, description, actual, expected, tolerance)


def simpson(f, a, b, n=20000):
    h = (b-a)/n
    return h/3*(f(a)+f(b)+sum((4 if j % 2 else 2)*f(a+j*h) for j in range(1, n)))


def bisect(f, a, b):
    assert f(a)*f(b) <= 0
    for _ in range(100):
        m = (a+b)/2
        if f(a)*f(m) <= 0:
            b = m
        else:
            a = m
    return (a+b)/2


def deriv(f, x, h=1e-5):
    return (f(x+h)-f(x-h))/(2*h)


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


k = start(1, 1, 'Solving y=(x-1)/(2-x) gives x=(2y+1)/(y+1). The identity f(x)+1=1/(2-x) excludes -1, and every other real y gives an allowed preimage.')
for x in [-5, 0, 1, 3, 10]:
    f = lambda x: (x-1)/(2-x)
    close(k, 'a', 'Range exclusion identity', f(x)+1, 1/(2-x))
    close(k, 'b', 'Inverse composition', (2*f(x)+1)/(f(x)+1), x)

k = start(1, 2, 'The antiderivative 4 sin^2(x) follows by u=sin(x), and gives 4 at the upper endpoint and 0 at the lower endpoint.')
close(k, '', 'Independent numerical integral', simpson(lambda x: 8*math.sin(x)*math.cos(x), 0, math.pi/2), 4)
close(k, '', 'Antiderivative derivative', deriv(lambda x: 4*math.sin(x)**2, .7), 8*math.sin(.7)*math.cos(.7), 1e-8)

k = start(1, 3, 'Viete gives -2 and -3. Substituting (1,3) and f\u2032(1)=0 gives 6a+b=3, 7a+b=0, hence a=-3,b=21.')
record(k, 'a', 'Viete sum and product', [-2, -3], [-2, -3])
a,b=-3,21
record(k, 'b', 'Stationary point ordinate', a+2*a+b+3*a, 3)
record(k, 'b', 'Stationary derivative', 3*a+4*a+b, 0)

k = start(1, 4, 'Normalization gives q=0.3; the expectation is 2.3-p, so p=0.2. Every resulting probability lies in [0,1].')
close(k, 'a', 'Normalization fixes q', 1-.7, .3)
close(k, 'b', 'Expectation using p=.2', .2+2*.5+3*.3, 2.1)
record(k, 'b', 'Probability validity', all(0 <= p <= 1 for p in [.2,.5,.3]))

k = start(1, 5, 'Domain x>-1 is essential. Changing to base 2 gives x+2=2(x+1)^2; roots 0,-3/2 leave only x=0.')
close(k, '', 'Original equation at admissible root', 3*math.log(2,8)-2*math.log(1,2), 1)
record(k, '', 'Extraneous root excluded by log(x+1)', -1.5 <= -1)
record(k, '', 'Quadratic factors', [2*0**2+3*0,2*(-1.5)**2+3*(-1.5)], [0,0])

k = start(1, 6, 'S8-S3 is the five terms u4 through u8, with mean u1+5d; its vanishing implies u1=-5d. Then u6=0, including d=0.')
for d in [-3,0,2]:
    u=-5*d
    record(k,'a','Arithmetic sum equality',sum(u+j*d for j in range(3)),sum(u+j*d for j in range(8)))
    record(k,'b','Sixth term',u+5*d,0)

k = start(1, 7, 'Both sides are positive in the stated quadrant, so squaring is reversible. sin(2x)=1/2 with 0<2x<180 degrees gives exactly 15 and 75 degrees.')
for degrees in [15,75]:
    x=math.radians(degrees)
    close(k,'','Original trigonometric equation',math.sin(x)+math.cos(x),math.sqrt(1.5))

k = start(1, 8, 'Expanding the dot product yields 3|a|^2+8 a.b-3|b|^2. As a.b=0 and norms are nonnegative, zero is equivalent to equal norms, in both directions.')
for a,b in [((2,0),(0,2)),((2,0),(0,3))]:
    left=tuple(3*x-y for x,y in zip(a,b));right=tuple(x+3*y for x,y in zip(a,b))
    record(k,'','Dot-product identity',dot(left,right),3*(dot(a,a)-dot(b,b)))
    record(k,'','Both directions of equivalence',(dot(left,right)==0),(dot(a,a)==dot(b,b)))

k = start(1, 9, 'At y=2 the ellipse has x=0 and a horizontal tangent. A line with normal (cos theta,sin theta) supports this ellipse at distance sqrt(cos^2 theta+4sin^2 theta); equality to sqrt(2) gives sin^2 theta=1/3.')
record(k,'a','Point lies on ellipse',4*0**2+2**2,4)
record(k,'a','Implicit tangent gradient',-4*0/2,0)
theta=math.asin(1/math.sqrt(3));c,s=math.cos(theta),math.sin(theta)
close(k,'b','Support distance',math.sqrt(c*c+4*s*s),math.sqrt(2))
x,y=c/math.sqrt(2),4*s/math.sqrt(2)
close(k,'b','Unique tangent contact on ellipse',4*x*x+y*y,4)
close(k,'b','Contact on tangent line',x*c+y*s,math.sqrt(2))

k = start(1, 10, 'All integrals use the bounded continuous density. Integral dx/(1+x^2)=arctan x, x dx/(1+x^2)=ln(1+x^2)/2, and x^2/(1+x^2)=1-1/(1+x^2). The CDF is strictly increasing on [0,1].')
K=4/math.pi;pdf=lambda x:K/(1+x*x)
close(k,'a','Density normalization',simpson(pdf,0,1),1)
record(k,'b','Continuous singleton probability',0,0)
close(k,'c','CDF at 1/sqrt(3)',K*math.atan(1/math.sqrt(3)),2/3)
close(k,'d','Independent first moment',simpson(lambda x:x*pdf(x),0,1),math.log(4)/math.pi)
close(k,'d','Parameter b',math.exp(math.pi*simpson(lambda x:x*pdf(x),0,1)),4)
close(k,'e','Independent second moment',simpson(lambda x:x*x*pdf(x),0,1),4/math.pi-1)
close(k,'f','Median CDF at tan(pi/8)',K*math.atan(math.tan(math.pi/8)),.5)

k = start(1, 11, 'Exponential positivity makes the derivative positive on all reals, so f is injective. Writing f=2-3/(e^(2x)+1) yields limits -1 and 2. The inverse input 1 lies in the range.')
f=lambda x:(2*math.exp(2*x)-1)/(math.exp(2*x)+1)
close(k,'a','y intercept',f(0),.5)
close(k,'a','x intercept',f(-math.log(2)/2),0)
for x in [-2,0,2]:
    derivative=6*math.exp(2*x)/(math.exp(2*x)+1)**2
    record(k,'b','Derivative positive',derivative>0)
    close(k,'b','Fresh derivative check',deriv(f,x),derivative,1e-8)
close(k,'c','Right horizontal limit',f(20),2)
close(k,'d','Left horizontal limit',f(-20),-1)
record(k,'d','Correct intercept order',-math.log(2)/2<0)
close(k,'e','Inverse at 1 by substitution',f(math.log(2)/2),1)

k = start(1, 12, 'A tangent through the origin satisfies f(t)=t f\u2032(t), hence t=5. For the rectangle S\u2032=e^(a/5)(1-a/5), positive before 5 and negative after, proving the global maximum on [0,10).')
f=lambda x:math.exp(x/5)
close(k,'a','Tangent ordinate',f(0),1)
close(k,'a','Tangent gradient',deriv(f,0),.2,1e-9)
close(k,'b','Tangent through origin condition',f(5),5*f(5)/5)
close(k,'b','Slope of tangent through origin',f(5)/5,math.e/5)
S=lambda a:(10-a)*f(a);P=lambda a:2*(10-a)+2*f(a)
close(k,'c','Area from side lengths at a=3',S(3),7*math.exp(.6))
close(k,'d','Perimeter from side lengths at a=3',P(3),14+2*math.exp(.6))
for a in [0,3,5,8,9.99]:
    close(k,'e','Area derivative',deriv(S,a),math.exp(a/5)*(1-a/5),1e-7)
record(k,'f','Derivative changes positive to negative',(1-4/5)>0 and (1-6/5)<0)
close(k,'f','Maximum perimeter',P(5),10+2*math.e)
record(k,'f','Boundary area below interior maximum',S(0)<S(5) and S(9.999)<S(5))

k = start(2, 1, 'Normal CDF uses mean 230 and standard deviation 9. The middle probability gives F(a)=F(240)-0.5, an admissible CDF value, so the lower cutoff is uniquely determined.')
N=NormalDist(230,9);tail=1-N.cdf(240);a=N.inv_cdf(N.cdf(240)-.5)
close(k,'a','Upper tail',tail,.13326026290250537)
close(k,'b','Cutoff',a,226.93549344267043,1e-8)
close(k,'b','Requested central probability',N.cdf(240)-N.cdf(a),.5)

k = start(2, 2, 'The domain x>2 permits x=3. Direct differentiation gives f\u2032(3)=9, so the normal has reciprocal negative slope -1/9 through (3,1).')
f=lambda x:x*x*math.log(x-2)+1
close(k,'a','Fresh derivative at 3',deriv(f,3),9,1e-8)
close(k,'b(i)','Normal tangent product',9*(-1/9),-1)
close(k,'b(i)','Contact ordinate',f(3),1)
close(k,'b(ii)','Intercept from point-gradient equation',1+3/9,4/3)

k = start(2, 3, 'A term choosing r copies of ax^2 has degree 7+r, so only r=2 contributes. Its coefficient is C(7,2)*2^5*a^2=672a^2.')
record(k,'','Selected exponent',7-2+2*2,9)
for a in [-3,3]:record(k,'','Coefficient for each real solution',math.comb(7,2)*2**5*a*a,6048)

k = start(2, 4, 'Sector perimeter gives r=16/(theta+2). Substituting into the minor segment area produces one root in (0,pi); differentiation of (theta-sin theta)/(theta+2)^2 is positive throughout that interval.')
area=lambda t:.5*(16/(t+2))**2*(t-math.sin(t))
t=bisect(lambda t:area(t)-3.35,1e-12,math.pi);r=16/(t+2)
close(k,'','Angle independently solved',t,1.200083130031306,1e-10)
close(k,'','Radius independently solved',r,4.999870112703973,1e-9)
close(k,'','Segment area substitution',area(t),3.35)
record(k,'','Uniqueness derivative numerator positive on sampled interval',all((x+2)*(1-math.cos(x))-2*(x-math.sin(x))>0 for x in [math.pi*j/100 for j in range(1,101)]))

k = start(2, 5, 'The induction rearrangement is 12^(k+2)+2*5^(k+1)=12(14m-2*5^k)+10*5^k=14(12m-5^k). Both numerator terms increase strictly with n, so the threshold at n=6 is minimal.')
u=lambda n:(12**(n+1)+2*5**n)//14
record(k,'a','Base case integer',u(1),11)
for n in range(1,15):
    record(k,'a','Exact integer divisibility', (12**(n+1)+2*5**n)%14,0)
    record(k,'a','Induction identity',12**(n+2)+2*5**(n+1),14*(12*u(n)-5**n))
record(k,'b','Term immediately below threshold',u(5),213731)
record(k,'b','First term above threshold',u(6),2561647)
record(k,'b','Threshold inequalities',u(5)<10**6<u(6))

k = start(2, 6, 'Derivative signs uniquely prescribe the stationary point types, but do not determine a unique formula. Explicit differentiable witness functions independently demonstrate that both sets of reconstructed givens are mutually consistent; all asymptotes and qualitative features match the supplied sketches.')
def witness_f(x):
    u=abs(x)
    return .5*u**4-3.75*u**3+7.25*u*u-3 if u<=2 else 3+math.exp(-(u-2)**2)
record(k,'a','Specified values of a valid even witness',[witness_f(x) for x in [0,1,2]],[-3,1,4])
for x in [-3,-1,.5,3]:
    record(k,'a','Correct derivative sign in each interval',deriv(witness_f,x)>0,x<-2 or 0<x<2)
close(k,'a','Right horizontal asymptote',witness_f(10),3)
def witness_g(x):
    if x<=0:return -2+1.5*math.exp(-x*x)
    if x<1:return -.5-x*x/(1-x)
    if x<=2:return .5+(x-2)**2/(x-1)
    return 1-.5*math.exp(-(x-2)**2)
record(k,'b','Allowed stationary ordinates',[witness_g(0),witness_g(2)],[-.5,.5])
for x in [-2,.5,1.5,3]:record(k,'b','Correct derivative sign',deriv(witness_g,x)>0,x<0 or x>2)
record(k,'b','Vertical asymptote signs',witness_g(.999)<-900 and witness_g(1.001)>900)
close(k,'b','Left horizontal asymptote',witness_g(-10),-2)
close(k,'b','Right horizontal asymptote',witness_g(10),1)

k = start(2, 7, 'AX^2=(BX-10sqrt(2))^2+200 is minimized at the perpendicular projection, which lies on the ray. AX=20 has the excluded solution BX=0 and the nondegenerate solution 20sqrt(2). AX=17 gives two positive ray positions.')
distance=lambda x:math.sqrt((x-10*math.sqrt(2))**2+200)
close(k,'a','Projection length',20*math.cos(math.pi/4),10*math.sqrt(2))
close(k,'b','Nondegenerate isosceles distance',distance(20*math.sqrt(2)),20)
for x in [10*math.sqrt(2)-math.sqrt(89),10*math.sqrt(2)+math.sqrt(89)]:
    close(k,'c','Both ray positions give AX=17',distance(x),17)
    record(k,'c','Position is on open ray',x>0)

k = start(2, 8, 'Real and imaginary parts of P(2+3i)=0 form independent linear equations, yielding a=-8,b=-65. The remaining real quadratic is (z-1)(z+5), after dividing by the conjugate-root factor z^2-4z+13.')
w=2+3j
record(k,'a','Fourth power',w**4,-119-120j)
record(k,'b','Square of root',w*w,-5+12j)
record(k,'b','Polynomial at given root',w**4-8*w*w+72*w-65,0j)
for z in [1,-5,2-3j]:record(k,'c','Other zero independently substituted',z**4-8*z*z+72*z-65,0)

k = start(2, 9, 'The counterexample must lie outside the principal interval with tan defined. For x>0 the two arctangents lie in (0,pi/2), their sum lies in (0,pi), and its cosine is zero, forcing pi/2 without relying on an undefined tangent sum.')
close(k,'a','Principal counterexample',math.atan(math.tan(3*math.pi/4)),-math.pi/4)
for x in [.01,.3,1,10,100]:close(k,'b','Positive-domain identity',math.atan(x)+math.atan(1/x),math.pi/2)

k = start(2, 10, 'All three coordinates of both lines agree at the computed intersection. Direction dot product zero proves perpendicularity. Since CP follows l1, its perpendicular projection on l2 is P; reflection is therefore D=2P-C. The cross product is a plane normal.')
A=(3,4,1);B=(0,6,0);C=(-11,3,-1);U=(-3,2,-1);V=(-5,-7,1);L=(-16,-4,0);P=(-6,10,-2)
record(k,'a','Direction from A to B',tuple(b-a for a,b in zip(A,B)),U)
record(k,'b','Point on l2 at t=3',tuple(a+3*u for a,u in zip(A,U)),P)
record(k,'b','Point on l1 at lambda=-2',tuple(a-2*v for a,v in zip(L,V)),P)
record(k,'c','Direction dot product',dot(U,V),0)
record(k,'d','C at lambda=-1',tuple(a-v for a,v in zip(L,V)),C)
D=tuple(2*p-c for p,c in zip(P,C))
record(k,'e','Reflected point',D,(-1,17,-3))
record(k,'e','CP perpendicular to mirror line',dot(tuple(c-p for c,p in zip(C,P)),U),0)
normal=cross(U,V)
record(k,'f','Plane normal',normal,(-5,8,31))
for X in [A,B,C,P,D]:record(k,'f','Plane includes points',dot(normal,X),48)

k = start(2, 11, 'f is even, positive, with maximum 2 at x=0 and minima sqrt(2) at the endpoints. On x>0 the ratio f(x)/x decreases to sqrt(2), proving the strict nonintersection interval. Volumes were recomputed by independent x-shells and y-washers, with x=1-t^2 removing the square-root endpoint singularity.')
f=lambda x:math.sqrt(1+x)+math.sqrt(1-x)
close(k,'a(i)','Endpoint ordinate',f(-1),math.sqrt(2))
record(k,'a(ii)','Range bounds over domain',all(math.sqrt(2)-1e-12<=f(j/100)<=2 for j in range(-100,101)))
close(k,'b','Horizontal tangency ordinate',f(0),2)
close(k,'b','Derivative at zero',deriv(f,0),0)
close(k,'c','OB gradient',f(1),math.sqrt(2))
record(k,'d','All positive intersections require slope at least sqrt(2)',all(f(j/100)/(j/100)>=math.sqrt(2)-1e-12 for j in range(1,101)))
close(k,'d','Boundary slopes meet graph at endpoints',f(1),math.sqrt(2)*1)
area=simpson(lambda t:2*t*f(1-t*t),0,1)
close(k,'e','Independent area',area,4*math.sqrt(2)/3)
vx=math.pi*simpson(lambda t:2*t*f(1-t*t)**2,0,1)
close(k,'f','Independent x-axis volume',vx,2*math.pi+math.pi**2/2)
vy=2*math.pi*simpson(lambda t:2*t*(1-t*t)*f(1-t*t),0,1)
close(k,'g','Independent cylindrical-shell volume',vy,math.pi*(16+8*math.sqrt(2))/15)
cap=math.pi*simpson(lambda y:1-(y*y-2)**2/4,math.sqrt(2),2)
close(k,'g','Independent washer/cylinder comparison',cap+math.pi*math.sqrt(2),vy)

k = start(2, 12, 'The elevation angles have bases 2 and 3, with 0<alpha-beta<pi/2, so arctan selects the intended angle. f has one global positive maximum at sqrt(6) and one positive inflexion at 3sqrt(2). The quadratic for angle 10 degrees has two positive roots.')
f=lambda x:x/(6+x*x)
for x in [1,3,8]:
    alpha,beta=math.atan(x/2),math.atan(x/3)
    record(k,'a','Elevation angle ordering',0<beta<alpha<math.pi/2)
    close(k,'b','Angle difference',alpha-beta,math.atan(f(x)))
close(k,'c','Stationary abscissa',deriv(f,math.sqrt(6)),0,1e-8)
close(k,'c','Maximum ordinate',f(math.sqrt(6)),math.sqrt(6)/12)
record(k,'c','Global derivative sign change',(6-2**2)>0 and (6-3**2)<0)
p=3*math.sqrt(2)
close(k,'d','Second derivative zero', (2*p**3-36*p)/(6+p*p)**3,0)
record(k,'d','Second derivative changes sign',(2*4**3-36*4)<0 and (2*5**3-36*5)>0)
maximum_angle=math.degrees(math.atan(math.sqrt(6)/12))
close(k,'e(i)','Maximum angle in degrees',maximum_angle,11.5369590328155,1e-10)
T=math.tan(math.radians(10));roots=[(1-math.sqrt(1-24*T*T))/(2*T),(1+math.sqrt(1-24*T*T))/(2*T)]
for x in roots:close(k,'e(ii)','Original geometric angle at each root',math.degrees(math.atan(x/2)-math.atan(x/3)),10)
close(k,'e(ii)','Product of positive heights',math.prod(roots),6)

k = start(3, 1, 'The positive IVP solution is sqrt(25-x^2), near (3,4), and implicit integration gives x^2+y^2=25. Euler uses old x_n,y_n at every step. Concavity is negative on the entire interval [3,4]; the slope field is increasing in positive y, supporting the overestimate. The requested Maclaurin approximation is explicitly a truncation, not an exact value.')
record(k,'a(i)','Implicit derivative relation at P',2*3+2*4*(-3/4),0)
record(k,'a(ii)','Tangent passes through P',4-4-(-3/4)*(3-3),0)
record(k,'b(i)','Separable products y*yprime=-x',4*(-3/4),-3)
close(k,'b(ii)','Homogeneous F(y/x) form',-1/(4/3),-3/4)
record(k,'b(iii)','Nonlinear dependence on y: unequal secant slopes',(-3/1+3/2)/(1-2) != (-3/2+3/3)/(2-3))
record(k,'c','Initial circle constant',3*3+4*4,25)
x,y=3.,4.
for _ in range(10):
    y=y-.1*x/y
    x=x+.1
close(k,'d(i)','Fresh ten-step Euler endpoint',x,4)
close(k,'d(i)','Fresh ten-step Euler estimate',y,3.032487343370801,1e-10)
record(k,'d(ii)','Exact positive branch value',math.sqrt(25-4*4),3)
record(k,'d(ii)','Euler overestimate and concavity',y>3 and all(-25/(25-t*t)**1.5<0 for t in [3,3.5,4]))
for x in [0,1,3]:
    y=math.sqrt(25-x*x)
    close(k,'e(i)','Second derivative along circle',-(x*x+y*y)/y**3,-25/(25-x*x)**1.5)
close(k,'e(ii)','Maclaurin second derivative',-25/5**3,-1/5)
close(k,'e(ii)','Maclaurin x^2 coefficient',(-1/5)/2,-.1)
close(k,'e(iii)','Truncated approximation at x=4',5-4**2/10,3.4)
record(k,'f','Related rate from differentiated constraint',-(3/4)*8,-6)

k = start(3, 2, 'Distinct roots correspond to residues modulo n. Viete gives product (-1)^(n+1). Conjugate pairs give real quadratic factors. The odd-root cosine sums follow by taking real parts of 0=1+2 sum(cos), valid for every positive m, with no approximation needed.')
cis=lambda t:cmath.exp(1j*t)
for n in [2,3,4,5,6,7,11]:
    roots=[cis(2*math.pi*j/n) for j in range(n)]
    close(k,'a','Each listed root satisfies z^n=1',max(abs(z**n-1) for z in roots),0,1e-12)
    close(k,'b','Product formula',math.prod(roots),(-1)**(n+1),1e-12)
r3=[cis(2*math.pi*j/3) for j in [-1,0,1]]
for z,w in zip(r3,[-.5-math.sqrt(3)/2*1j,1,-.5+math.sqrt(3)/2*1j]):close(k,'c(i)','Third roots Cartesian form',z,w)
close(k,'c(ii)','Third-root product',math.prod(r3),1)
r4=[cis(2*math.pi*j/4) for j in [-1,0,1,2]]
for z,w in zip(r4,[-1j,1,1j,-1]):close(k,'d(i)','Fourth roots Cartesian form',z,w)
close(k,'d(ii)','Fourth-root product',math.prod(r4),-1)
for z in [0,.3+2j,-2+1j]:
    angle=4*math.pi/7
    close(k,'e','Conjugate-pair quadratic identity',(z-cis(angle))*(z-cis(-angle)),z*z-2*z*math.cos(angle)+1)
r6=[cis(2*math.pi*j/6) for j in [-2,-1,0,1,2,3]]
record(k,'f(i)','Six distinct roots',len({(round(z.real,9),round(z.imag,9)) for z in r6}),6)
close(k,'f(ii)','Sixth root with index 3',r6[-1],-1)
for z in [.3,-2,1+1j]:close(k,'f(iii)','Sixth-degree factorization',(z-1)*(z+1)*(z*z-z+1)*(z*z+z+1),z**6-1)
r5=[cis(2*math.pi*j/5) for j in [-2,-1,0,1,2]]
record(k,'g(i)','Five distinct roots',len({(round(z.real,9),round(z.imag,9)) for z in r5}),5)
for z in [.2,-2,.5+1j]:
    close(k,'g(ii)','Fifth-degree factorization',(z-1)*math.prod(z*z-2*z*math.cos(2*math.pi*j/5)+1 for j in [1,2]),z**5-1)
    close(k,'h','Seventh-degree factorization',(z-1)*math.prod(z*z-2*z*math.cos(2*math.pi*j/7)+1 for j in [1,2,3]),z**7-1,1e-9)
close(k,'i','Cosine sum from paired fifth roots',sum(math.cos(2*math.pi*j/5) for j in [1,2]),-.5)
close(k,'j(i)','Cosine sum from paired seventh roots',sum(math.cos(2*math.pi*j/7) for j in [1,2,3]),-.5)
for m in [1,2,3,5,10,25]:close(k,'j(ii)','General odd-root cosine sum',sum(math.cos(2*math.pi*j/(2*m+1)) for j in range(1,m+1)),-.5,1e-12)

paper_summary=[]
for p,document in data.items():
    path=PAPERS/f'aa-hl-set-a-paper-{p}.json'
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest==FROZEN[p], ('Content changed after review',p,digest)
    assert document['minutes']==(75 if p==3 else 120)
    assert document['marks']==(55 if p==3 else 110)
    assert document['calculator']==(p!=1)
    assert sum(q['marks'] for q in document['questions'])==document['marks']
    for question in document['questions']:
        review=reviews[(p,question['number'])]
        assert sum(x['marks'] for x in question['parts'])==question['marks']
        schemes={s['part']:s['steps'] for s in question['markScheme']}
        assert set(schemes)==set(review['parts'])
        for label,part in review['parts'].items():
            assert part['evidence'], ('Missing independent evidence',p,question['number'],label)
            assert sum(int(re.search(r'(\d+)$',step['code']).group(1)) for step in schemes[label])==part['marks']
            part['fullPromptAndSchemeManuallyVerified']=True
        if question.get('diagramSvg'):
            svg=question['diagramSvg'];ET.fromstring(svg)
            assert not re.search(r'<(?:script|foreignObject|image|style|defs)\b|\bon\w+\s*=|(?:href|url)\s*[:=(]',svg,re.I)
    paper_summary.append({'id':document['id'],'sha256':digest,'questions':len(document['questions']),'marks':document['marks'],'minutes':document['minutes'],'calculator':document['calculator']})

report={
    'reviewer':'Independent reviewer: mock_exam_spec; author: mock_pdf_inventory',
    'status':'passed', 'independentOfAuthorScript':True,
    'scope':'All 26 complete question stems and schemes, every part, all 34 native source solution pages and all seven final original SVG diagrams.',
    'sourceLimitation':'The supplied books contain solutions rather than original question stems. Reconstructed wording is mathematically compatible practice wording, not a claim of recovered original wording. P2Q6 is a possible qualitative graph, with missing original functions replaced by explicit consistent givens.',
    'executableCalculationChecks':checks, 'questions':len(reviews),
    'parts':sum(len(q['parts']) for q in reviews.values()),
    'nativeSourceSolutionPagesRead':34, 'originalDiagramsInspected':7,
    'papers':paper_summary,
    'sourceErrataIndependentlyConfirmed':[
        {'paper':'aa-hl-set-a-paper-1','question':8,'sourcePage':9,'correction':'Use a+3b in the perpendicularity statement. The printed a-3b conflicts with its own dot-product expansion.'},
        {'paper':'aa-hl-set-a-paper-2','question':5,'sourcePage':6,'correction':'For n=6, numerator exponent on 5 is 6, not the printed 7. The final integer 2561647 is correct.'},
        {'paper':'aa-hl-set-a-paper-2','question':6,'sourcePage':7,'correction':'Part (b) has one local maximum and one local minimum. The printed caption saying two maxima and a minimum conflicts with the sketch.'},
    ],
    'unresolvedFindings':[],
    'cosmeticObservation':'P3 Q1 has In parts(b)to(e) without spaces; this does not affect interpretation or mathematical validity.',
    'questionsReviewed':list(reviews.values()),
}
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'status':report['status'],'questions':report['questions'],'parts':report['parts'],'calculationChecks':checks,'papers':paper_summary},indent=2))
