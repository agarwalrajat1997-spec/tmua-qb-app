"""Original 2026 AA HL enrichment. Re-running writes only this new batch."""
import json, math, html, sys
from pathlib import Path
import sympy as S
from scipy.stats import norm,binom
from scipy.integrate import quad
from scipy.optimize import brentq
ROOT=Path(__file__).resolve().parents[2]
X=S.symbols('x',real=True)
Q=[]; CHECKS=[]
def eq(a,b): assert S.simplify(a-b)==0,(a,b)
def near(a,b): assert math.isclose(float(a),float(b),rel_tol=1e-9,abs_tol=1e-9),(a,b)
def M(t):return ('M1',t)
def A(t):return ('A1',t)
def R(t):return ('R1',t)
def P(prompt,*steps):return (prompt,steps)
def svg(e,title="Mathematical diagram"):
 return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 380" role="img" aria-label="'+html.escape(title,quote=True)+'"><rect width="640" height="380" fill="white"/>'+''.join(e)+'</svg>'
def text(x,y,t,size=15):return f'<text x="{x:.2f}" y="{y:.2f}" font-family="Arial, sans-serif" font-size="{size}" fill="#111">{html.escape(str(t))}</text>'
def line(x,y,u,v,dash=False):return f'<line x1="{x:.2f}" y1="{y:.2f}" x2="{u:.2f}" y2="{v:.2f}" stroke="#111" stroke-width="1.6"'+(' stroke-dasharray="6 5"' if dash else '')+'/>'
def plot(fs,box=(-3,3,-3,6),labels=None,points=(),title=""):
 if not isinstance(fs,(list,tuple)):fs=[fs]
 a,b,c,d=box
 def pt(x,y):return 58+(x-a)/(b-a)*520,326-(y-c)/(d-c)*270
 e=[text(58,25,title,16)]
 ox,oy=pt(0,0)
 if c<=0<=d:e +=[line(58,oy,585,oy),text(596,oy+5,'x',13)]
 if a<=0<=b:e +=[line(ox,326,ox,45),text(ox+8,46,'y',13)]
 step=max(1,math.ceil((b-a)/8))
 for x in range(math.ceil(a/step)*step,math.floor(b)+1,step):
  if x and c<=0<=d:
   u,v=pt(x,0);e +=[line(u,v-3,u,v+3),text(u-4,v+18,x,11)]
 for y in range(math.ceil(c),math.floor(d)+1):
  if y and a<=0<=b and (d-c)<=20:
   u,v=pt(0,y);e +=[line(u-3,v,u+3,v),text(u-26,v+4,y,11)]
 for k,f in enumerate(fs):
  seg=[]
  def flush():
   if len(seg)>1:e.append('<polyline fill="none" stroke="#111" stroke-width="2"'+(' stroke-dasharray="6 4"' if k else '')+' points="'+' '.join(f'{u:.2f},{v:.2f}' for u,v in seg)+'"/>')
  for j in range(321):
   x=a+(b-a)*j/320
   try:y=float(f(x))
   except (ValueError,OverflowError,ZeroDivisionError):y=float('nan')
   if math.isfinite(y) and c<=y<=d:
    z=pt(x,y)
    if seg and abs(z[1]-seg[-1][1])>100:flush();seg=[]
    seg.append(z)
   else:flush();seg=[]
  flush()
  if labels:e.append(text(370,45+20*k,labels[k],13))
 for x,y,label in points:
  u,v=pt(x,y);e +=[f'<circle cx="{u:.2f}" cy="{v:.2f}" r="3.5" fill="#111"/>',text(u+7,v-8,label,13)]
 return svg(e,title or 'Coordinate graph; solid and dashed curves identified in the question')
def dots(points,title='Data plot',connect=False,values=True):
 a=min(x for x,y in points);b=max(x for x,y in points);c=min(0,min(y for x,y in points));d=max(y for x,y in points)
 if a==b:b=a+1
 if c==d:d=c+1
 def pt(x,y):return 65+(x-a)/(b-a)*500,320-(y-c)/(d-c)*245
 e=[text(50,25,title,16),line(55,320,585,320),line(55,320,55,55)]
 if connect:e.append('<polyline points="'+' '.join(f'{pt(x,y)[0]:.2f},{pt(x,y)[1]:.2f}' for x,y in points)+'" fill="none" stroke="#111" stroke-width="1.6"/>')
 for x,y in points:
  u,v=pt(x,y);e +=[f'<circle cx="{u:.2f}" cy="{v:.2f}" r="4" fill="#111"/>',text(u-8,343,x,11)]
  if values:e.append(text(u+7,v-9,f'{y:g}',12))
 return svg(e,title)
def argand(zs,title="Argand diagram",circle=None):
 e=[text(35,25,title,16),line(55,190,590,190),line(320,340,320,48),text(595,185,'Re',13),text(330,48,'Im',13)]
 scale=42
 if circle:
  cx,cy,r=circle;e.append(f'<circle cx="{320+scale*cx:.2f}" cy="{190-scale*cy:.2f}" r="{r*scale:.2f}" fill="none" stroke="#111" stroke-width="1.7"/>')
 for z,label in zs:
  z=complex(z);u=320+scale*z.real;v=190-scale*z.imag
  e +=[line(320,190,u,v),f'<circle cx="{u:.2f}" cy="{v:.2f}" r="3" fill="#111"/>',text(u+7,v-8,label,13)]
 return svg(e,title)
def shape(coords,edges,labels,title="Diagram not to scale"):
 # Coordinates are display positions; all mathematical data are stated explicitly.
 e=[text(30,25,title,16)]
 for i,j in edges:e.append(line(*coords[i],*coords[j]))
 for (u,v),label in zip(coords,labels):
  e +=[f'<circle cx="{u}" cy="{v}" r="3" fill="#111"/>',text(u+7,v-9,label)]
 e.append(text(30,361,'Schematic; use the stated coordinates and measurements.',12))
 return svg(e,title)
def add(topic,title,sub,code,stem,parts,diagram=None,calc=False,diff='hard',style=None,evidence='Exact algebra and domain conditions checked.'):
 prefix={'number-algebra':'na','functions':'fn','geometry-trigonometry':'gt','statistics-probability':'sp','calculus-1':'c1','calculus-2':'c2'}[topic]
 num=701+sum(q['collectionId']==topic for q in Q)
 ps=[];ms=[]
 for j,(prompt,steps) in enumerate(parts):
  label=chr(97+j);ps.append(dict(label=label,prompt=prompt,marks=len(steps)))
  ms.append(dict(part=label,steps=[dict(code=c,text=t) for c,t in steps]))
 marks=sum(p['marks'] for p in ps)
 code_topic,code_n=map(int,code.split('.'));slmax={1:9,2:11,3:8,4:12,5:11}
 q=dict(id=f'ib-aa-{prefix}-{num}',subject='math-aa-hl',topicId='calculus' if topic.startswith('calculus') else topic,collectionId=topic,number=num,title=title,subtopic=sub,syllabusCode=code,level='ahl' if code_n>slmax[code_topic] else 'sl',difficulty=diff,calculator=calc,examStyle=style or ('extended-response' if marks>=8 else 'short-response'),marks=marks,stem=stem,parts=ps,markScheme=ms,source=dict(document='Independent syllabus-authored practice',question=num),verification=dict(method='Symbolic/numerical author checks and full worked derivation',notes=evidence+' Accept equivalent methods and exact forms. Retain unrounded working; give non-exact answers to 3 significant figures unless specified. Follow through valid later work after an earlier error unless it removes the demand.'),answerSummary=' '.join(g['steps'][-1]['text'] for g in ms),status='published')
 if diagram:q.update(diagramSvg=diagram,diagramCaption='Original mathematical diagram. '+('Schematic; not to scale.' if 'Schematic;' in diagram else 'Use exact values stated in the question; do not measure the drawing.'))
 Q.append(q);CHECKS.append(dict(id=q['id'],title=title,syllabusCode=code,evidence=evidence))
 return q

# NUMBER AND ALGEBRA: twenty different structures.
add('number-algebra','A rotation that first returns to the positive axis','Complex numbers','1.14',
 r'Let $z=1+i\sqrt3$. The Argand diagram shows $O$, $1$ and $z$.',
 [P(r'Write $z$ in modulus–argument form and find $z^3$.',M(r'$|z|=2$ and $\arg z=\pi/3$.'),A(r'$z=2\operatorname{cis}(\pi/3)$.'),A(r'$z^3=8\operatorname{cis}\pi=-8$.')),
 P(r'Find the least positive integer $n$ for which $z^n$ is positive real. Hence find this value of $z^n$.',M(r'Positive real requires $n\pi/3=2k\pi$.'),R(r'The least positive solution is $n=6$.'),A(r'$z^6=64$.'))],argand([(1,'1'),(1+3**.5*1j,'z')]),diff='medium')
eq((1+S.sqrt(3)*S.I)**6,64)
add('number-algebra','Roots forming a triangle','Complex numbers','1.14',r'The three roots of $w^3=-8$ are plotted on a circle centred at $O$.',
 [P('Find all three roots in exact Cartesian form.',M(r'$-8=8\operatorname{cis}(\pi+2k\pi)$.'),A(r'Arguments are $\pi/3,\pi,5\pi/3$, each with modulus $2$.'),A(r'$1+i\sqrt3,\ -2,\ 1-i\sqrt3$.')),
 P('Find the exact area of the triangle with these roots as vertices.',M(r'The vertical base has length $2\sqrt3$.'),M('Its perpendicular distance from the third vertex is 3.'),A(r'Area $=\frac12(2\sqrt3)(3)=3\sqrt3$.'))],argand([(1+3**.5*1j,'A'),(-2,'B'),(1-3**.5*1j,'C')],circle=(0,0,2)),diff='medium')
add('number-algebra','Recovering a real cubic from one complex root','Complex numbers','1.14',r'The polynomial $p(w)=w^3+aw^2+bw+5$, where $a,b\in\mathbb R$, has a root $2+i$.',
 [P('Find the other roots, explaining the use of real coefficients.',R(r'$2-i$ is also a root by the conjugate-root property.'),M(r'The product of the three roots is $-5$, and $(2+i)(2-i)=5$.'),A(r'The remaining root is $-1$.')),
 P('Find a and b by expanding a factorization of p.',M(r'$p(w)=(w+1)((w-2)^2+1)$.'),A(r'$p(w)=w^3-3w^2+w+5$.'),A(r'$a=-3,\ b=1$.'))],argand([(2+1j,'2+i'),(2-1j,'conjugate')]),diff='medium')
eq((X+1)*((X-2)**2+1),X**3-3*X**2+X+5)
add('number-algebra','An Apollonius circle and a nearest point','Complex numbers','1.13',r'A complex number $z=x+iy$ satisfies $|z-2|=2|z+1|$. The points $-1$, $2$ and $P=3+4i$ are shown.',
 [P('Show that the locus is a circle, and state its centre and radius.',M(r'$(x-2)^2+y^2=4((x+1)^2+y^2)$.'),A(r'$(x+2)^2+y^2=4$.'),A(r'Centre $-2$, radius $2$.')),
 P('Find the minimum possible value of the distance from z to P.',M(r'The distance from $P$ to the centre is $\sqrt{5^2+4^2}=\sqrt{41}$.'),R(r'$P$ is outside the circle; the nearest point lies on the centre–$P$ line.'),A(r'Minimum distance $=\sqrt{41}-2$.'))],argand([(-1,'-1'),(2,'2'),(3+4j,'P')]),diff='medium')
add('number-algebra','When a quotient is imaginary','Complex numbers','1.12',r'Let $z=x+iy\ne-1$. The number $(z-1)/(z+1)$ is purely imaginary, with zero allowed.',
 [P('Find an equation for the locus of z and state its excluded point.',M(r'Multiply numerator and denominator by $x+1-iy$.'),A(r'The real numerator is $x^2+y^2-1$; the denominator is nonzero.'),A(r'$x^2+y^2=1$, excluding $(-1,0)$.')),
 P(r'Find all possible z when $\operatorname{Im}z=\frac12$.',M(r'$x^2=1-\frac14=\frac34$.'),A(r'$z=\frac{\sqrt3}{2}+\frac i2$ or $z=-\frac{\sqrt3}{2}+\frac i2$.'),R('Both satisfy the original quotient condition and neither is the excluded point.'))],argand([(-1,'excluded'),(1,'1')],circle=(0,0,1)),diff='medium')
add('number-algebra','A recurrence approaches a target','Sequences and series','1.3',r'A sequence is defined by $u_0=8$ and $u_{n+1}=\frac34u_n+6$. The first five terms are plotted.',
 [P(r'Show that $u_n=24-16(\frac34)^n$.',M(r'The fixed point solves $L=\frac34L+6$, so $L=24$.'),M(r'$u_{n+1}-24=\frac34(u_n-24)$ with $u_0-24=-16$.'),A(r'Thus $u_n-24=-16(\frac34)^n$.')),
 P(r'Find the least n such that $|u_n-24|<0.5$, justifying the integer choice.',M(r'$16(3/4)^n<0.5$, so $n>\ln(1/32)/\ln(3/4)=12.047\ldots$.'),A('$n=13$.'),R(r'At $n=12$ the error exceeds $0.5$; at $13$ it is smaller.'))],dots([(n,24-16*.75**n) for n in range(5)],'First five terms'),calc=True,diff='medium')
assert 16*.75**12>.5>16*.75**13
add('number-algebra','Arithmetic terms become geometric','Sequences and series','1.3',r'Three increasing positive numbers $a,b,c$ form an arithmetic sequence and have sum $18$. The numbers $a,b,c+2$ form a geometric sequence.',
 [P('Find a, b and c exactly.',A('$b=6$ and $a+c=12$.'),M(r'$6^2=a(c+2)=a(14-a)$.'),A(r'$a=7\pm\sqrt{13}$.'),R(r'Increasing order selects $a=7-\sqrt{13}$, hence $c=5+\sqrt{13}$.')),
 P('Find the common ratio of the geometric sequence and show that it exceeds 1.',M(r'$r=6/(7-\sqrt{13})=(7+\sqrt{13})/6$.'),A(r'$r=(7+\sqrt{13})/6$.'),R(r'$\sqrt{13}>0$ gives $r>7/6>1$.'))],dots([(1,7-math.sqrt(13)),(2,6),(3,5+math.sqrt(13))],'The arithmetic sequence',values=False),diff='hard')
add('number-algebra','A telescoping sum with an integer threshold','Binomial theorem and counting','1.11',r'For $N\ge1$, let $S_N=\sum_{r=1}^N\frac1{r(r+2)}$.',
 [P('Use partial fractions to obtain an exact expression for S_N.',M(r'$\frac1{r(r+2)}=\frac12(\frac1r-\frac1{r+2})$.'),M('Cancel all interior terms in the sum.'),A(r'$S_N=\frac34-\frac1{2(N+1)}-\frac1{2(N+2)}$.')),
 P(r'Find the least N for which $S_N>0.7$.',M(r'The inequality becomes $N^2-17N-28>0$.'),A('$N=19$.'),R(r'$S_{18}=0.698684\ldots<0.7<S_{19}=0.701190\ldots$ and the terms added are positive.'))],dots([(n,sum(1/(r*(r+2)) for r in range(1,n+1))) for n in range(1,7)],'Early partial sums'),calc=True)
assert sum(1/(r*(r+2)) for r in range(1,19))<.7<sum(1/(r*(r+2)) for r in range(1,20))
add('number-algebra','A binomial approximation with a direction of error','Binomial theorem and counting','1.10',r'Let $f(x)=(1-2x)^{-1/2}$. The graph shows $f$ on a small positive interval.',
 [P('Find the first four nonzero terms of the Maclaurin expansion using the binomial theorem, and state the open interval on which this binomial expansion is valid.',M(r'Use $(1+u)^p=1+pu+\frac{p(p-1)}2u^2+\frac{p(p-1)(p-2)}6u^3+\cdots$.'),A(r'$f(x)=1+x+\frac32x^2+\frac52x^3+\cdots$.'),A(r'$|x|<\frac12$.')),
 P(r'Use the expansion through $x^3$ to approximate $1/\sqrt{0.96}$. Explain whether it is an overestimate or underestimate.',M('$1-2x=0.96$ gives $x=0.02$.'),A('$1+0.02+0.0006+0.00002=1.02062$.'),R('All omitted coefficients and powers are positive at this x, so the approximation is an underestimate.'))],plot(lambda x:(1-2*x)**-.5,(0,.3,.9,1.7),title='f(x) on 0 ≤ x ≤ 0.3'),diff='medium')
eq(S.series((1-2*X)**S.Rational(-1,2),X,0,4).removeO(),1+X+S.Rational(3,2)*X**2+S.Rational(5,2)*X**3)
add('number-algebra','Cancelling a coefficient without cancelling the next','Binomial theorem and counting','1.9',r'The coefficient of $x^2$ in $(1+2x)^8(1-kx)$ is zero.',
 [P('Find k.',M(r'In $(1+2x)^8$, the coefficients of $x$ and $x^2$ are $16$ and $\binom82 2^2=112$.'),M('$112-16k=0$.'),A('$k=7$.')),
 P('Find the coefficient of x cubed in the same product.',M(r'The original cubic coefficient is $\binom83 2^3=448$.'),M('The product gives $448-7(112)$.'),A('$-336$.'))],diff='medium')
eq(S.expand((1+2*X)**8*(1-7*X)).coeff(X,3),-336)
add('number-algebra','A conditional committee choice','Binomial theorem and counting','1.10',r'A committee of five is chosen uniformly from six girls and five boys. Two of the girls are school captains.',
 [P('Find the number of committees containing exactly three girls.',M(r'Choose the girls and boys separately: $\binom63\binom52$.'),A('$20\\times10=200$.'),R('Each unordered committee is counted exactly once.')),
 P('Given that the committee has exactly three girls, find the probability that at least one captain is chosen.',M(r'Use the complement: $\binom43/\binom63=4/20$ contains no captain.'),A(r'$1-\frac4{20}=\frac45$.'),R('Conditioning fixes the number of girls; the boy choices cancel from the ratio.'))],shape([(95,185),(315,100),(315,265),(535,100),(535,265)],[(0,1),(0,2),(1,3),(2,4)],['5 chosen','3 girls','other','captain?',''],'Conditioning on the committee composition'),diff='medium')
add('number-algebra','A weighted geometric sum proved by induction','Proof and mathematical induction','1.15',r'Let $T_n=\sum_{r=1}^n r2^r$.',
 [P(r'Prove by induction that $T_n=(n-1)2^{n+1}+2$ for all positive integers n.',A('For $n=1$, both sides equal 2.'),M(r'Assume $T_k=(k-1)2^{k+1}+2$.'),M(r'$T_{k+1}=T_k+(k+1)2^{k+1}=[(k-1)+(k+1)]2^{k+1}+2$.'),A(r'$T_{k+1}=k2^{k+2}+2$, the required formula for $k+1$.'),R('The base case and induction step establish the claim.')),
 P(r'Hence find $\lim_{n\to\infty}T_n/(n2^{n+1})$.',M(r'The ratio is $1-\frac1n+\frac{2}{n2^{n+1}}$.'),A('$1$.'))],dots([(r,r*2**r) for r in range(1,6)],'Terms r·2^r'))
for n in range(1,12):assert sum(r*2**r for r in range(1,n+1))==(n-1)*2**(n+1)+2
add('number-algebra','Logarithms with a parameter and ordered solutions','Exponents and logarithms','1.7',r'Positive numbers x and y satisfy $\log_2x+\log_4y=p$ and $xy=32$.',
 [P('Express x and y in terms of p.',M(r'Let $a=\log_2x$, $b=\log_2y$, so $a+b/2=p$ and $a+b=5$.'),A('$a=2p-5$, $b=10-2p$.'),A(r'$x=2^{2p-5}$ and $y=2^{10-2p}$.')),
 P(r'Find all p for which $x>y>1$.',M(r'$x>y$ requires $2p-5>10-2p$.'),M(r'$y>1$ requires $10-2p>0$.'),A(r'$\frac{15}{4}<p<5$.'))],plot([lambda p:2*p-5,lambda p:10-2*p],(2,6,-3,8),labels=['log₂ x','log₂ y'],title='Logarithms as functions of p'),diff='medium')
add('number-algebra','A parameter changes solvability','Proof and mathematical induction','1.16',r'The system is $x+y+z=3$, $x+2y+3z=6$, $2x+3y+(k+4)z=10$.',
 [P('Determine the values of k for which the system has no solution or a unique solution.',M('Subtract the sum of the first two equations from the third.'),A('$kz=1$.'),R('$k=0$ gives a contradiction, so there is no solution. For $k\\ne0$, z is fixed and then x,y are uniquely fixed.')),
 P('For the unique-solution case, express x, y and z in terms of k.',A(r'$z=1/k$.'),M(r'The second minus the first gives $y+2z=3$.'),A(r'$(x,y,z)=(1/k,\ 3-2/k,\ 1/k)$.'))],diff='hard')
add('number-algebra','A real-axis image on the unit circle','Complex numbers','1.13',r'For real z, define $w=(z-i)/(z+i)$.',
 [P('Prove that w lies on the unit circle.',M(r'$|z-i|=\sqrt{z^2+1}=|z+i|$ for real z.'),A('$|w|=1$.'),R('The denominator never vanishes when z is real.')),
 P(r'Find w when $z=\sqrt3$, then find the real z for which $\arg w=-\pi/2$.',M(r'At $z=\sqrt3$, multiply by $\sqrt3-i$ to obtain $w=\frac12-\frac{\sqrt3}2i$.'),A(r'The argument is $-\pi/3$.'),M(r'For argument $-\pi/2$, unit modulus implies $w=-i$, so $z-i=-i(z+i)$.'),A('$z=1$.'))],argand([(1,'1'),(-1,'-1'),(1j,'i'),(-1j,'-i')],circle=(0,0,1)))
eq((S.sqrt(3)-S.I)/(S.sqrt(3)+S.I),S.Rational(1,2)-S.sqrt(3)*S.I/2)
add('number-algebra','Alternation and an error tolerance','Sequences and series','1.8',r'A geometric series has first term 18 and sum to infinity 12. The first six partial sums are plotted.',
 [P('Find the common ratio and an expression for the nth partial sum.',M(r'$18/(1-r)=12$.'),A(r'$r=-1/2$.'),A(r'$S_n=12(1-(-1/2)^n)$.')),
 P(r'Find the least n such that $|S_n-12|<0.01$, and state whether that partial sum is above or below 12.',M(r'$12(1/2)^n<0.01$ gives $n>\log_2(1200)=10.228\ldots$.'),A('$n=11$.'),R(r'For odd n, $(-1/2)^n<0$, so $S_{11}>12$.'))],dots([(n,12*(1-(-.5)**n)) for n in range(1,7)],'Alternating partial sums',True),calc=True,diff='medium')
assert 12*.5**10>.01>12*.5**11
add('number-algebra','A rigorous growth bound and its limitation','Proof and mathematical induction','1.15',r'For $x\ge0$, consider the statement $(1+x)^n\ge1+nx$ for positive integers n.',
 [P('Prove the statement by induction.',A('At $n=1$ equality holds.'),M(r'Assuming $(1+x)^k\ge1+kx$, multiply by $1+x\ge1$.'),A(r'$(1+x)^{k+1}\ge1+(k+1)x+kx^2\ge1+(k+1)x$.'),R('This completes the induction.')),
 P(r'Find the first integer n for which this bound guarantees $(1.02)^n\ge3$. Compare it with the actual least n, found using logarithms.',M(r'The bound guarantees $1+0.02n\ge3$, so $n\ge100$.'),A('The bound first guarantees the claim at n=100.'),M(r'The exact condition is $n\ge\ln3/\ln1.02=55.477\ldots$.'),A('The actual least n is 56; the bound is sufficient but not necessary.'))],plot([lambda t:1.02**t,lambda t:1+.02*t],(0,60,0,4),labels=['1.02^n','1+0.02n'],title='Growth and its linear lower bound'),calc=True)
assert 1.02**55<3<=1.02**56
add('number-algebra','Four roots and their projections','Complex numbers','1.14',r'The four solutions of $z^4=16i$ lie on a circle centred at O.',
 [P('Find all four roots in modulus–argument form.',M(r'$16i=16\operatorname{cis}(\pi/2+2k\pi)$.'),A(r'$z=2\operatorname{cis}(\pi/8+k\pi/2)$.'),R('$k=0,1,2,3$ gives all four distinct roots.')),
 P('Find the largest real part of a root, in exact radical form.',M(r'The largest projection is $2\cos(\pi/8)$.'),M(r'$\cos^2(\pi/8)=(1+\cos(\pi/4))/2$.'),A(r'The largest real part is $\sqrt{2+\sqrt2}$.'))],argand([],circle=(0,0,2)),diff='medium')
add('number-algebra','A rational generating function','Binomial theorem and counting','1.11',r'For $|x|<1/2$, write $1/((1-x)(1-2x))=\sum_{n=0}^{\infty}a_nx^n$.',
 [P('Use partial fractions to find a_n.',M(r'$\frac1{(1-x)(1-2x)}=-\frac1{1-x}+\frac2{1-2x}$.'),M('Expand both geometric series, with their common convergence condition.'),A(r'$a_n=2^{n+1}-1$.')),
 P(r'Find $\sum_{n=0}^Na_n$ exactly.',M(r'$\sum_{n=0}^N(2^{n+1}-1)=2(2^{N+1}-1)-(N+1)$.'),A(r'$2^{N+2}-N-3$.'),R('The subtraction includes N+1 constant terms.'))],dots([(n,2**(n+1)-1) for n in range(6)],'First six coefficients'))
eq(-1/(1-X)+2/(1-2*X),1/((1-X)*(1-2*X)))
add('number-algebra','Divisibility and the parity of a quotient','Proof and mathematical induction','1.15',r'For positive integers n, define $b_n=(7^n-1)/6$.',
 [P('Prove by induction that b_n is an integer.',A('$b_1=1$.'),M(r'$7^{k+1}-1=7(7^k-1)+6$.'),A(r'$b_{k+1}=7b_k+1$, an integer if $b_k$ is an integer.'),R('Induction establishes integrality for every positive n.')),
 P('Determine exactly when b_n is odd, giving a proof.',M(r'$b_n=1+7+7^2+\cdots+7^{n-1}$.'),R('Every term is odd, so the parity of the sum is the parity of the number of terms.'),A('b_n is odd exactly when n is odd.'))],dots([(n,(7**n-1)//6) for n in range(1,5)],'Initial values of b_n'))
for n in range(1,20):assert ((7**n-1)//6)%2==n%2

# FUNCTIONS: domains, parameters, inverse branches and graphical reasoning.
add('functions','A moving horizontal line meets a cubic','Quadratic and polynomial functions','2.12',r'Let $f(x)=x^3-3x+2$. A sketch of f is provided.',
 [P(r'Solve $f(x)\ge0$ exactly.',M(r'$f(x)=(x-1)^2(x+2)$.'),R('The squared factor is nonnegative and does not change sign at x=1.'),A(r'$x\in[-2,\infty)$.')),
 P('Determine all k for which f(x)=k has three distinct real solutions.',M(r'$f^{\prime}(x)=3x^2-3$, so the stationary x-values are $-1,1$.'),A('$f(-1)=4$ and $f(1)=0$.'),R('Exactly three distinct intersections occur when $0<k<4$.'))],plot(lambda x:x**3-3*x+2,(-3,3,-3,7)),diff='medium')
add('functions','A cancelled factor leaves a missing point','Rational functions','2.13',r'For $x\ne-2$, let $f(x)=(2x^2+3x-2)/(x+2)$. The graph is a straight line with a missing point.',
 [P('Simplify f and state its range.',M(r'$2x^2+3x-2=(2x-1)(x+2)$.'),A(r'$f(x)=2x-1$ for $x\ne-2$.'),R(r'The range is $\mathbb R\setminus\{-5\}$ because the excluded input alone gives output $-5$.')),
 P(r'Solve $f(x)\le3$, preserving the original domain restriction.',M(r'$2x-1\le3$ gives $x\le2$.'),A(r'$(-\infty,-2)\cup(-2,2]$.'),R('Cancelling a factor does not restore the original excluded input.'))],plot(lambda x:2*x-1,(-4,4,-9,7)).replace('</svg>','<circle cx="188" cy="258.5" r="5" fill="white" stroke="#111" stroke-width="1.5"/></svg>'),diff='medium')
add('functions','A rational range from a discriminant','Rational functions','2.13',r'Let $f(x)=(x^2+1)/(x-1)$, where $x\ne1$.',
 [P('Find both asymptotes.',M(r'Division gives $f(x)=x+1+2/(x-1)$.'),A(r'The vertical asymptote is $x=1$.'),A(r'The oblique asymptote is $y=x+1$.')),
 P('Find the exact range of f by considering the equation f(x)=k.',M(r'This equation is $x^2-kx+(1+k)=0$.'),M(r'Real x requires $k^2-4k-4\ge0$.'),A(r'$k\le2-2\sqrt2$ or $k\ge2+2\sqrt2$.'),R('The quadratic never has x=1 as a root, since substitution gives 2; no extra values are lost.'))],plot(lambda x:(x*x+1)/(x-1),(-4,5,-8,10)))
add('functions','An inverse and its fixed points','Function notation and inverses','2.2',r'$f(x)=(x-2)^2+2$ is defined for $x\ge2$.',
 [P('Find the inverse, including its domain.',M(r'$y-2=(x-2)^2$ and $x-2\ge0$.'),A(r'$f^{-1}(x)=2+\sqrt{x-2}$.'),A(r'Its domain is $x\ge2$.')),
 P('Find all intersections of the graphs of f and its inverse. Justify why no off-diagonal intersections exist.',M(r'Solve $f(x)=x$: $(x-2)(x-3)=0$.'),A('The points are $(2,2)$ and $(3,3)$.'),R(r'f is strictly increasing. If $y=f(x)>x$, then $f(y)>f(x)=y$, contradicting $f(y)=x$; the case y<x is similar.'))],plot([lambda x:(x-2)**2+2,lambda x:2+math.sqrt(x-2),lambda x:x],(2,5,2,8),labels=['f','inverse','y=x']))
add('functions','Composition changes the permitted inputs','Function notation and inverses','2.2',r'Let $f(x)=\ln x$ and $g(x)=\sqrt{4-x}$, each with its maximal real domain.',
 [P('Find a formula and domain for f composed with g.',M(r'$(f\circ g)(x)=\ln\sqrt{4-x}=\frac12\ln(4-x)$.'),R('The square root must be strictly positive before taking its logarithm.'),A('$x<4$.')),
 P('Find a formula and domain for g composed with f, and explain why the two domains differ.',M(r'$(g\circ f)(x)=\sqrt{4-\ln x}$.'),A(r'$0<x\le e^4$.'),R('The first composition requires g(x)>0; the second requires x>0 and f(x)≤4. The intermediate input conditions differ.'))],plot([lambda x:math.log(x),lambda x:math.sqrt(4-x)],(.1,4,-3,3),labels=['f','g']),diff='medium')
add('functions','An absolute-value inequality from two branches','Graph transformations','2.15',r'The graphs of $y=|x^2-4|$ and $y=3x$ are shown.',
 [P('Find all their intersection x-coordinates exactly.',R('Since the left side is nonnegative, every solution has x≥0.'),M(r'For $0\le x\le2$, solve $4-x^2=3x$, giving $x=1$.'),M(r'For $x\ge2$, solve $x^2-4=3x$, giving $x=4$.'),A('The intersections have x=1 and x=4.')),
 P(r'Hence solve $|x^2-4|\le3x$.',M('Compare the branches between and outside the intersection points.'),A('$1\\le x\\le4$.'),R('Both endpoints are included because equality is allowed.'))],plot([lambda x:abs(x*x-4),lambda x:3*x],(-2,5,-1,16),labels=['|x²−4|','3x']),diff='medium')
add('functions','Taking a reciprocal introduces a second exclusion','Graph transformations','2.16',r'Let $f(x)=(x-2)/(x+1)$, $x\ne-1$, and define $g(x)=1/f(x)$.',
 [P('State g in simplified form and give its full domain.',M(r'$g(x)=(x+1)/(x-2)$.'),A(r'The domain excludes $x=-1$ and $x=2$.'),R('The first exclusion belongs to f; the second comes from f(x)=0.')),
 P('Find the range of g, explaining both exclusions.',M(r'$g(x)=1+3/(x-2)$ cannot equal 1.'),M('The only input giving g(x)=0 would be x=-1, which is excluded.'),A(r'The range is $\mathbb R\setminus\{0,1\}$.'))],plot(lambda x:(x+1)/(x-2),(-4,6,-5,7)),diff='medium')
add('functions','Even and odd parts of an exponential','Graph transformations','2.14',r'Define $g(x)=(e^x+e^{-x})/2$ and $h(x)=(e^x-e^{-x})/2$.',
 [P('Show that g is even, h is odd, and g squared minus h squared equals 1.',R(r'$g(-x)=g(x)$ and $h(-x)=-h(x)$ by substitution.'),M(r'$g^2-h^2=[(e^x+e^{-x})^2-(e^x-e^{-x})^2]/4$.'),A(r'$g^2-h^2=1$.')),
 P('Solve g(x)=2 exactly.',M(r'Writing $u=e^x>0$ gives $u+1/u=4$.'),A(r'$u=2\pm\sqrt3$.'),A(r'$x=\pm\ln(2+\sqrt3)$.'))],plot([lambda x:(math.exp(x)+math.exp(-x))/2,lambda x:(math.exp(x)-math.exp(-x))/2],(-2,2,-4,4),labels=['g','h']))
add('functions','How many roots can a logarithmic equation have?','Exponential and logarithmic functions','2.10',r'Consider $\ln x=kx$, where $x>0$ and k is real.',
 [P(r'Find the maximum of $h(x)=\ln x/x$.',M(r'$h^{\prime}(x)=(1-\ln x)/x^2$.'),A(r'The stationary point is $x=e$, with $h(e)=1/e$.'),R('The derivative changes from positive to negative, so this is the global maximum.')),
 P('State the number of distinct roots of the original equation for every possible k.',R(r'h increases from $-\infty$ to $1/e$ on $(0,e]$ and decreases towards 0 from above after e.'),A(r'For $k<0$: one root; for $k=0$: one root at x=1.'),A(r'For $0<k<1/e$: two; for $k=1/e$: one; for $k>1/e$: none.'))],plot(lambda x:math.log(x)/x,(.2,8,-1,.5)))
add('functions','An exponential inequality becomes a quadratic','Exponential and logarithmic functions','2.10',r'Let $F(x)=4^x-5(2^x)+4$.',
 [P('Find all zeros of F exactly.',M(r'Put $u=2^x>0$, so $u^2-5u+4=(u-1)(u-4)$.'),A('$u=1$ or $u=4$.'),A('$x=0$ or $x=2$.')),
 P(r'Solve $F(x)\le0$ and explain the effect of the substitution on the inequality.',M(r'The quadratic is nonpositive for $1\le u\le4$.'),R(r'$2^x$ is strictly increasing, so the order of the interval endpoints is preserved.'),A(r'$0\le x\le2$.'))],plot(lambda x:4**x-5*2**x+4,(-2,3,-3,7)),diff='medium')
add('functions','A cubic has a repeated root','Quadratic and polynomial functions','2.12',r'The polynomial $p(x)=x^3-6x^2+cx-8$ has a repeated real root a.',
 [P('Use the sum and product of the roots to find all possibilities for a.',M(r'Write the roots as a,a,b. Then $2a+b=6$, $a^2b=8$.'),M(r'$a^2(6-2a)=8$, so $(a-2)^2(a+1)=0$.'),A('$a=2$ or $a=-1$.')),
 P('Find the corresponding values of c and the complete factorization in each case.',M(r'Use $c=a^2+2ab$.'),A(r'If a=2, b=2 and c=12, so $p(x)=(x-2)^3$.'),A(r'If a=-1, b=8 and c=-15, so $p(x)=(x+1)^2(x-8)$.'))],plot([lambda x:(x-2)**3,lambda x:(x+1)**2*(x-8)],(-3,9,-30,30),labels=['one possible cubic','another possible cubic']))
eq(S.expand((X-2)**3),X**3-6*X**2+12*X-8)
add('functions','Two inverse branches of the same curve','Function notation and inverses','2.2',r'$f(x)=x+1/x$ for $x>0$.',
 [P('Explain why f has no inverse on its full domain, and find its range.',M(r'$f^{\prime}(x)=1-1/x^2$ changes sign at x=1.'),A(r'The minimum is $f(1)=2$, and the range is $[2,\infty)$.'),R('For example f(2)=f(1/2), so f is not one-to-one.')),
 P('Find the inverse for the restriction x≥1, and the inverse for the restriction 0<x≤1.',M(r'From $y=x+1/x$, solve $x^2-yx+1=0$.'),A(r'For x≥1, the inverse is $(y+\sqrt{y^2-4})/2$.'),A(r'For 0<x≤1, it is $(y-\sqrt{y^2-4})/2$; both have input domain y≥2.'))],plot(lambda x:x+1/x,(.15,5,0,8)))
add('functions','An involution and repeated compositions','Rational functions','2.13',r'Let $f(x)=(x+2)/(x-1)$, where $x\ne1$.',
 [P('Show that f is its own inverse, including the domain check.',M(r'$f(f(x))=\frac{(x+2)+2(x-1)}{(x+2)-(x-1)}$.'),A(r'$f(f(x))=x$.'),R('f(x)=1 has no solution, so the second composition is defined for every original input.')),
 P('Find the fixed points and solve f composed 101 times applied to x equals 4.',M(r'$f(x)=x$ gives $x^2-2x-2=0$.'),A(r'The fixed points are $1\pm\sqrt3$.'),M('Pairs of compositions cancel, so the 101st composition is f.'),A('$f(x)=4$ gives x=2.'))],plot([lambda x:(x+2)/(x-1),lambda x:x],(-4,6,-6,8),labels=['f','y=x']))
add('functions','A root where the curve touches the axis','Quadratic and polynomial functions','2.12',r'A monic cubic f has zeros at x=1 and x=3 and satisfies $f^{\prime}(1)=0$.',
 [P('Find f in factorized form.',R('The zero x=1 is repeated because both f(1) and its derivative vanish.'),M('A monic cubic has exactly three roots counted with multiplicity.'),A(r'$f(x)=(x-1)^2(x-3)$.')),
 P('Find and classify both stationary points, giving exact coordinates.',M(r'$f^{\prime}(x)=(x-1)(3x-7)$.'),A(r'The stationary points are $(1,0)$ and $(7/3,-32/27)$.'),R('The derivative signs are +,−,+, giving a local maximum at x=1 and a local minimum at x=7/3.'))],plot(lambda x:(x-1)**2*(x-3),(-1,4,-5,5)),diff='medium')
eq(((X-1)**2*(X-3)).subs(X,S.Rational(7,3)),-S.Rational(32,27))
add('functions','Counting intersections through a nonnegative variable','Graph transformations','2.16',r'The equation $|x|=x^2+c$ is considered for real c.',
 [P(r'Put $t=|x|$. Explain how nonnegative solutions t determine the number of x-solutions.',M(r'The equation becomes $t^2-t+c=0$ with $t\ge0$.'),R('Each t>0 gives two x-values, ±t; t=0 gives only one x-value.'),A(r'The quadratic roots are $(1\pm\sqrt{1-4c})/2$ when c≤1/4.')),
 P('Find the number of distinct real x-solutions for every c.',R('For c<0 there is one positive t and one negative t, hence 2 x-solutions.'),A('For c=0: t=0,1, giving 3 solutions.'),A('For 0<c<1/4: two positive t-values, giving 4 solutions.'),A('For c=1/4: one positive double t-root, giving 2 solutions; for c>1/4: no solutions.'))],plot([lambda x:abs(x),lambda x:x*x+.1],(-1.5,1.5,-.2,2.5),labels=['|x|','x²+0.1']))
add('functions','A reflection and a horizontal transformation','Graph transformations','2.16',r'$f(x)=3-(x-1)^2/3$ is defined on $[-2,4]$. Let $g(x)=-2f(3-x)+1$.',
 [P('Find the domain and range of g, and the image of the vertex of f.',M(r'$-2\le3-x\le4$ gives $-1\le x\le5$.'),A(r'Since f ranges from 0 to 3, g ranges from $-5$ to 1.'),A('The vertex (1,3) maps to (2,−5).')),
 P('Find the exact zeros of g and verify that they belong to its domain.',M(r'$g(x)=0$ requires $3-(2-x)^2/3=1/2$.'),A(r'$x=2\pm\sqrt{30}/2$.'),R('Both are between −1 and 5, so both are valid.'))],plot(lambda x:3-(x-1)**2/3,(-2,4,-.5,4)),diff='medium')
add('functions','Two logarithms impose an interval','Exponential and logarithmic functions','2.10',r'Let $h(x)=\ln(x-1)+\ln(5-x)$.',
 [P(r'State the domain and solve $h(x)=\ln3$.',A('$1<x<5$.'),M(r'$(x-1)(5-x)=3$, giving $x^2-6x+8=0$.'),A('$x=2$ or $x=4$, both within the domain.')),
 P(r'Solve $h(x)\ge\ln3$ and find the maximum value of h.',M(r'The product is $4-(x-3)^2$.'),A(r'The inequality holds for $2\le x\le4$.'),A(r'The maximum is $\ln4$ at x=3.'))],plot(lambda x:math.log(x-1)+math.log(5-x),(1.05,4.95,-3,2)),diff='medium')
add('functions','One composition is an identity but the other is not','Function notation and inverses','2.2',r'Let $f(x)=\sqrt{x+1}$ for $x\ge-1$, and $g(x)=x^2-1$ for all real x.',
 [P('Find f composed with g and g composed with f, with domains.',M(r'$(f\circ g)(x)=\sqrt{x^2}=|x|$ for all real x.'),A(r'$(g\circ f)(x)=x$ for $x\ge-1$.'),R('The square root is the nonnegative root; it is not equal to x for negative x.')),
 P('Specify a restriction of g that makes f and g inverses, and justify it.',M('Restrict g to inputs x≥0.'),A(r'Then g maps $[0,\infty)$ onto $[-1,\infty)$, matching f’s domain and range in reverse.'),R('Both compositions become identities on their respective domains.'))],plot([lambda x:math.sqrt(x+1),lambda x:x*x-1],(-.99,3,-2,6),labels=['f','g']),diff='medium')
add('functions','Recovering an exponential from a shifted asymptote','Exponential and logarithmic functions','2.10',r'A model has form $f(x)=ab^x+c$, where a>0 and b>1. Its horizontal asymptote is y=2, and its graph passes through (0,5) and (2,14).',
 [P('Find a, b and c.',A('$c=2$.'),M('$a+c=5$ and $ab^2+c=14$.'),A('$a=3$, $b=2$.')),
 P('Find the inverse with its domain, then solve f(x)=50.',M(r'From $y=3(2^x)+2$, obtain $x=\log_2((y-2)/3)$.'),A(r'$f^{-1}(x)=\log_2((x-2)/3)$ for x>2.'),A('$f(x)=50$ gives x=4.'))],plot(lambda x:3*2**x+2,(-3,3,0,30),points=[(0,5,'(0,5)'),(2,14,'(2,14)')]),diff='medium')
add('functions','The order of two transformations matters','Function notation and inverses','2.2',r'Let $f(x)=x^2$ and $g(x)=2x+1$.',
 [P('Find all x where the two compositions agree.',M(r'$(f\circ g)(x)=4x^2+4x+1$ and $(g\circ f)(x)=2x^2+1$.'),M(r'Their difference is $2x(x+2)$.'),A('They agree at x=−2 and x=0.')),
 P('Determine where the first composition is at least the second, and explain why agreement at two points does not make the functions equal.',M(r'Solve $2x(x+2)\ge0$.'),A(r'$x\le-2$ or $x\ge0$.'),R('Equality of functions requires equal outputs at every input; for example at x=1 the two outputs are 9 and 3.'))],plot([lambda x:(2*x+1)**2,lambda x:2*x*x+1],(-3,2,0,18),labels=['f composed with g','g composed with f']),diff='medium')

def scene3(points,edges,labels,planes=(),title='Projection of the stated spatial configuration'):
 # A single linear camera preserves all incidence and collinearity relationships.
 projected={name:(p[0]-.65*p[1],.35*p[0]+.5*p[1]-p[2]) for name,p in points.items()}
 xs=[p[0] for p in projected.values()];ys=[p[1] for p in projected.values()]
 cx=(max(xs)+min(xs))/2;cy=(max(ys)+min(ys))/2
 scale=min(490/max(1e-6,max(xs)-min(xs)),245/max(1e-6,max(ys)-min(ys)))
 positions={name:(320+(x-cx)*scale,190+(y-cy)*scale) for name,(x,y) in projected.items()}
 e=[text(30,25,title,15)]
 for face in planes:
  e.append('<polygon points="'+' '.join(f'{positions[n][0]:.2f},{positions[n][1]:.2f}' for n in face)+'" fill="#f4f4f4" stroke="#777" stroke-width="1"/>')
 for a,b,dashed in edges:e.append(line(*positions[a],*positions[b],dashed))
 for name,label in labels.items():
  u,v=positions[name]
  if isinstance(label,tuple):label,dx,dy=label
  else:dx,dy=7,-9
  e.append(f'<circle cx="{u:.2f}" cy="{v:.2f}" r="3" fill="#111"/>')
  e.append(text(u+dx,v+dy,label,13))
 e.append(text(30,361,'Perspective projection; use the stated 3D coordinates, not apparent lengths.',12))
 return svg(e,title)

# GEOMETRY AND TRIGONOMETRY. Spatial drawings preserve the stated incidences.
spatial=lambda labels:shape([(100,270),(300,310),(260,105),(500,160)],[(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)],labels,'Spatial configuration')
add('geometry-trigonometry','The foot of a perpendicular on a spatial line','Vectors, lines and planes','3.14',r'The line L is $\mathbf r=(1,2,3)+t(2,-1,2)$. Let $P=(4,1,0)$.',
 [P('Find the point H on L for which PH is perpendicular to L.',M(r'With $\mathbf d=(2,-1,2)$, use $(P-A-t\mathbf d)\cdot\mathbf d=0$.'),A(r'$t=((3,-1,-3)\cdot(2,-1,2))/9=1/9$.'),A(r'$H=(11/9,17/9,29/9)$.')),
 P('Find the exact distance from P to L, explaining why this is the minimum distance.',M(r'$|P-A|^2=19$ and the squared projection is $1/9$.'),A(r'$PH=\sqrt{170}/3$.'),R('Any other point on L forms a right triangle with PH, giving a strictly longer hypotenuse.'))],spatial(['A','line L','P','H (unknown)']))
add('geometry-trigonometry','Intersection and angle of two lines','Vectors, lines and planes','3.15',r'$L_1:\mathbf r=(1,0,2)+t(1,2,-1)$ and $L_2:\mathbf r=(3,1,0)+u(-1,1,1)$.',
 [P('Show that the lines intersect and find the intersection.',M(r'The x and y equations give $t+u=2$, $2t-u=1$.'),A('$t=u=1$; both z-values are 1.'),A('The intersection is (2,2,1).')),
 P('Find the angle between the lines.',M(r'The direction-vector dot product is $-1+2-1=0$.'),A(r'The angle is $\pi/2$.'),R('Both direction vectors are nonzero, so zero dot product establishes perpendicularity.'))],spatial(['L₁ base','L₂ base','directions','intersection?']),diff='medium')
add('geometry-trigonometry','Skew lines and a minimum distance','Vectors, lines and planes','3.15',r'$L_1:\mathbf r=(t,0,0)$ and $L_2:\mathbf r=(0,1+u,1-u)$.',
 [P('Prove that the lines are skew.',M('Their directions (1,0,0) and (0,1,−1) are not parallel.'),M('An intersection would require 1+u=0 and 1−u=0 simultaneously.'),R('These conditions are inconsistent, so nonparallel, nonintersecting lines are skew.')),
 P('By minimizing the squared distance between general points on the lines, find their minimum distance.',M(r'$D^2=t^2+(1+u)^2+(1-u)^2=t^2+2u^2+2$.'),A('The minimum squared distance is 2, attained at t=u=0.'),A(r'The minimum distance is $\sqrt2$.'))],spatial(['x-axis','L₁ point','L₂ point','L₂ direction']))
add('geometry-trigonometry','A plane through three intercepts','Vectors, lines and planes','3.17',r'$A=(1,0,0)$, $B=(0,2,0)$ and $C=(0,0,3)$.',
 [P('Find a Cartesian equation of plane ABC.',M(r'$\overrightarrow{AB}=(-1,2,0)$, $\overrightarrow{AC}=(-1,0,3)$.'),A(r'$\overrightarrow{AB}\times\overrightarrow{AC}=(6,3,2)$.'),A(r'$6x+3y+2z=6$.')),
 P('Find the area of triangle ABC and the perpendicular distance from O to its plane.',M(r'The normal vector has magnitude $\sqrt{36+9+4}=7$.'),A(r'Triangle area $=7/2$.'),A(r'Distance $=|0-6|/7=6/7$.'))],spatial(['O','A(1,0,0)','C(0,0,3)','B(0,2,0)']),diff='medium')
add('geometry-trigonometry','Reflecting a point in a plane','Vectors, lines and planes','3.18',r'$P=(3,2,1)$ and the plane $\Pi$ has equation $x+2y+2z=0$.',
 [P('Find the foot H of the perpendicular from P to the plane.',M(r'A perpendicular line is $P+\lambda(1,2,2)$.'),M(r'Substitution gives $9+9\lambda=0$, so $\lambda=-1$.'),A('$H=(2,0,−1)$.')),
 P('Find the reflection of P in the plane and the distance from P to the plane.',M('H is the midpoint of P and its reflection, so P′=2H−P.'),A('$P^{\\prime}=(1,-2,-3)$.'),A(r'$PH=\sqrt{1+4+4}=3$.'))],spatial(['plane Π','H','P','reflection?']))
add('geometry-trigonometry','The line shared by two planes','Vectors, lines and planes','3.18',r'Two planes are $x+y+z=4$ and $x-y+z=0$.',
 [P('Find a vector equation for their line of intersection.',M('Subtract the equations to obtain y=2.'),A('$x+z=2$.'),A(r'$\mathbf r=(0,2,2)+t(1,0,-1)$.')),
 P('Find the acute angle between the planes, in degrees.',M(r'Normals are $(1,1,1)$ and $(1,-1,1)$.'),M(r'$\cos\theta=|1-1+1|/(\sqrt3\sqrt3)=1/3$.'),A(r'$\theta=70.5^\circ$ to 3 significant figures.'))],spatial(['Π₁','Π₂','intersection line','normal vectors']),calc=True,diff='medium')
add('geometry-trigonometry','Paths cross but particles do not collide','Vectors, lines and planes','3.14',r'For $t\ge0$, particles have positions $\mathbf a(t)=(t,2t,1)$ and $\mathbf b(t)=(4-t,t,1)$. Distances are in metres and t is in seconds.',
 [P('Show that the geometric paths intersect, but that the particles do not collide.',M(r'Use independent path parameters: $s=4-u$, $2s=u$, giving $s=4/3$, $u=8/3$.'),A(r'The paths cross at $(4/3,8/3,1)$.'),R('The particles reach that point at different times; simultaneous x equality gives t=2 whereas simultaneous y equality gives t=0.')),
 P('Find their minimum separation and the time when it occurs.',M(r'$D^2=(2t-4)^2+t^2=5t^2-16t+16$.'),A(r'The minimum occurs at $t=8/5$.'),A(r'$D_{\min}=\sqrt{16/5}=4/\sqrt5$ metres.'),R('The coefficient of t squared is positive and 8/5 belongs to t≥0, so this is the global minimum.'))],plot([lambda x:2*x,lambda x:4-x],(0,4,0,8),labels=['path a in xy plane','path b in xy plane']))
add('geometry-trigonometry','A vector angle determines two parameters','Vectors, lines and planes','3.13',r'Let $\mathbf a=(1,k,1)$ and $\mathbf b=(1,-1,2)$.',
 [P('Find k when the vectors are perpendicular.',M(r'$\mathbf a\cdot\mathbf b=3-k$.'),A('$k=3$.'),R('The zero dot-product condition applies because both vectors are nonzero.')),
 P(r'Find all k when the angle is $60^\circ$, checking any roots introduced by squaring.',M(r'$3-k=\frac12\sqrt{6(k^2+2)}$.'),M(r'Squaring gives $k^2+12k-12=0$.'),A(r'$k=-6\pm4\sqrt3$.'),R('Both values are less than 3, so the original left side is positive and both satisfy the unsquared equation.'))],spatial(['O','a','b','angle at O']))
add('geometry-trigonometry','An area condition in three dimensions','Vectors, lines and planes','3.16',r'$A=(0,0,0)$, $B=(1,2,0)$ and $C=(2,0,k)$.',
 [P('Find the area of triangle ABC in terms of k.',M(r'$\overrightarrow{AB}\times\overrightarrow{AC}=(2k,-k,-4)$.'),A(r'The magnitude is $\sqrt{5k^2+16}$.'),A(r'Area $=\frac12\sqrt{5k^2+16}$.')),
 P('Find all k giving area 3. Explain geometrically why opposite values give the same area.',M('$5k^2+16=36$.'),A('$k=\\pm2$.'),R('Changing the sign of k reflects C across the xy-plane while fixing A and B, preserving area.'))],spatial(['A','B','C(k>0 schematic)','reflection of C']),diff='medium')
add('geometry-trigonometry','A combined trigonometric wave','Trigonometric identities','3.10',r'$f(x)=\sqrt3\sin x+\cos x$, for $0\le x<2\pi$.',
 [P(r'Express f in the form $R\sin(x+\alpha)$, with $R>0$ and $0<\alpha<\pi/2$.',M(r'Compare $R\cos\alpha=\sqrt3$ and $R\sin\alpha=1$.'),A('$R=2$.'),A(r'$\alpha=\pi/6$, so $f(x)=2\sin(x+\pi/6)$.')),
 P('Solve f(x)=1 on the specified interval.',M(r'$\sin(x+\pi/6)=1/2$.'),A(r'$x=0$ or $x=2\pi/3$.'),R(r'$2\pi$ is excluded by the stated upper endpoint; no other solutions lie in the interval.'))],plot(lambda x:3**.5*math.sin(x)+math.cos(x),(0,2*math.pi,-2.5,2.5)),diff='medium')
add('geometry-trigonometry','Two acute angles combine exactly','Trigonometric identities','3.10',r'Acute angles A and B satisfy $\tan A=1/2$ and $\tan B=1/3$.',
 [P('Find A+B exactly.',M(r'$\tan(A+B)=\frac{1/2+1/3}{1-1/6}=1$.'),R('Since A and B are acute, their sum is in (0,π); positive tangent places the sum in the first quadrant.'),A(r'$A+B=\pi/4$.')),
 P('Find tan(A−B) and sin(A+B) exactly.',M(r'$\tan(A-B)=\frac{1/2-1/3}{1+1/6}$.'),A(r'$\tan(A-B)=1/7$.'),A(r'$\sin(A+B)=\sqrt2/2$.'))],shape([(90,290),(325,290),(325,170),(390,290),(555,290),(555,235)],[(0,1),(1,2),(2,0),(3,4),(4,5),(5,3)],['A','2','1','B','3','1'],'Reference right triangles'),diff='medium')
add('geometry-trigonometry','Dividing by cosine loses solutions','Trigonometric functions and equations','3.10',r'Solve $\sin2x=\cos x$ for $0\le x<2\pi$.',
 [P('Find all exact solutions.',M(r'$2\sin x\cos x-\cos x=\cos x(2\sin x-1)=0$.'),A(r'$\cos x=0$ gives $x=\pi/2,3\pi/2$.'),A(r'$\sin x=1/2$ gives $x=\pi/6,5\pi/6$.')),
 P('A student divides the equation by cos x and obtains only two answers. Explain the error and state the missing answers.',R('Division is invalid when cos x=0, and those values satisfy the original equation.'),A(r'The missing answers are $\pi/2$ and $3\pi/2$.'),R('Factorization retains the zero-factor case and therefore provides a complete solution.'))],plot([lambda x:math.sin(2*x),lambda x:math.cos(x)],(0,2*math.pi,-1.3,1.3),labels=['sin 2x','cos x']),diff='medium')
add('geometry-trigonometry','A reciprocal trigonometric equation','Trigonometric functions and equations','3.9',r'For $0<x<\pi$, let $f(x)=2\sin x+\csc x$.',
 [P('Solve f(x)=3 exactly.',M(r'Let $s=\sin x>0$. Then $2s+1/s=3$ implies $(2s-1)(s-1)=0$.'),A(r'$s=1/2$ or $s=1$.'),A(r'$x=\pi/6,\pi/2,5\pi/6$.')),
 P('Find the minimum value of f and all points where it is attained.',M(r'For s>0, $2s+1/s\ge2\sqrt2$, with equality when $2s=1/s$.'),A(r'The minimum is $2\sqrt2$.'),A(r'It occurs at $s=1/\sqrt2$, hence $x=\pi/4,3\pi/4$.'))],plot(lambda x:2*math.sin(x)+1/math.sin(x),(.1,math.pi-.1,2,7)))
add('geometry-trigonometry','A principal inverse changes the graph','Trigonometric functions and equations','3.9',r'Let $h(x)=\arcsin(\sin3x)$ on $0\le x\le\pi/2$. The principal range of arcsine is $[-\pi/2,\pi/2]$.',
 [P('Give a piecewise expression for h.',M(r'For $0\le3x\le\pi/2$, the principal value is $3x$.'),A(r'$h(x)=3x$ for $0\le x\le\pi/6$.'),A(r'$h(x)=\pi-3x$ for $\pi/6\le x\le\pi/2$.')),
 P('Solve h(x)=x, checking both branches.',M('On the first branch 3x=x gives x=0.'),M(r'On the second branch $\pi-3x=x$ gives $x=\pi/4$.'),A(r'The complete set is $\{0,\pi/4\}$.'))],plot(lambda x:math.asin(math.sin(3*x)),(0,math.pi/2,-2,2)))
add('geometry-trigonometry','A chord and its minor segment','Geometry and measurement','3.4',r'A circle has radius 5 cm. A chord AB is 3 cm from its centre O.',
 [P('Find the chord length and the minor central angle θ, in radians.',M('A perpendicular from O bisects the chord; the half-chord is √(25−9)=4.'),A('AB=8 cm.'),A(r'$\theta=2\arccos(3/5)$.')),
 P('Find the exact area of the minor segment bounded by AB and its minor arc.',M(r'Sector area $=\frac12(25)\theta=25\arccos(3/5)$.'),M('Triangle area = (1/2)(8)(3)=12.'),A(r'Segment area $=25\arccos(3/5)-12$ cm$^2$.'))],shape([(320,110),(140,280),(500,280),(320,280)],[(0,1),(0,2),(1,2),(0,3)],['O','A','B','3 cm'],'Chord in a circle'),diff='medium')
add('geometry-trigonometry','A cone, its net and an inscribed sphere','Geometry and measurement','3.4',r'A right circular cone has base radius 6 cm and height 8 cm. A sphere touches the base and the curved surface internally.',
 [P('Find the angle, in radians, of the sector forming the curved-surface net.',M('The slant height is √(6²+8²)=10 cm.'),M('The sector arc length equals the base circumference, 12π.'),A(r'The sector angle is $12\pi/10=6\pi/5$.')),
 P('Find the sphere radius, deriving the needed relation from a central cross-section.',M('Let the sphere radius be r. Its centre is 8−r from the apex along the axis.'),M(r'The half-apex angle α has $\sin\alpha=6/10$; tangency requires $r=(8-r)\sin\alpha$.'),A('$r=3$ cm.'))],shape([(320,65),(125,310),(515,310),(320,310),(320,218)],[(0,1),(0,2),(1,2),(0,3)],['apex','base rim','base rim','base centre','sphere centre'],'Axial cross-section of a cone'))
add('geometry-trigonometry','Two triangles satisfy the same measurements','Trigonometric ratios','3.2',r'In triangle ABC, $A=30^\circ$, $a=6$ cm and $b=10$ cm, using the standard opposite-side notation.',
 [P('Find both possible values of c exactly.',M(r'The cosine rule gives $36=100+c^2-10\sqrt3\,c$.'),M(r'Solve $c^2-10\sqrt3\,c+64=0$.'),A(r'$c=5\sqrt3\pm\sqrt{11}$ cm.')),
 P('The perimeter exceeds 25 cm. Identify the correct value of c and find the area exactly.',R('The condition is c>9. Only $5\\sqrt3+\\sqrt{11}$ exceeds 9.'),M(r'Area $=\frac12bc\sin A=\frac52c$.'),A(r'Area $=\frac52(5\sqrt3+\sqrt{11})$ cm$^2$.'))],shape([(105,300),(530,300),(405,100)],[(0,1),(1,2),(2,0)],['A=30°','B','C'],'Ambiguous triangle; one possible configuration'))
add('geometry-trigonometry','A cyclic quadrilateral fixes its diagonal','Trigonometric ratios','3.2',r'A cyclic quadrilateral ABCD has side lengths AB=3, BC=4, CD=5 and DA=6. The diagonal AC has length x.',
 [P('Use the cosine rule in the two triangles to find x exactly.',M(r'$\cos B=(25-x^2)/24$, $\cos D=(61-x^2)/60$.'),R(r'Opposite angles in a cyclic quadrilateral sum to $\pi$, so $\cos D=-\cos B$.'),A(r'$24(61-x^2)=-60(25-x^2)$, giving $x=\sqrt{247/7}$.')),
 P('Find the area of ABCD exactly.',M(r'$\cos B=-3/7$, so $\sin B=2\sqrt{10}/7$; also $\sin D=\sin B$.'),M(r'Area $=\frac12(3\cdot4+5\cdot6)\sin B$.'),A(r'Area $=6\sqrt{10}$ square units.'))],shape([(110,245),(250,80),(530,180),(400,315)],[(0,1),(1,2),(2,3),(3,0),(0,2)],['A','B','C','D'],'Cyclic quadrilateral; schematic'))
add('geometry-trigonometry','Two observations determine a wave and its first maximum','Sinusoidal models','3.10',r'$y=a\sin2t+b\cos2t$, where $t\ge0$. It is known that $y(0)=3$ and $y(\pi/4)=4$.',
 [P(r'Find a and b, then write y as $R\sin(2t+\alpha)$ with $0<\alpha<\pi/2$.',A('$a=4$, $b=3$.'),M(r'$R=\sqrt{4^2+3^2}=5$, $\tan\alpha=3/4$.'),A(r'$y=5\sin(2t+\arctan(3/4))$.')),
 P('Find the first time when y reaches its maximum and state that maximum.',M(r'$2t+\alpha=\pi/2$ at the first maximum.'),A(r'$t=(\pi/2-\arctan(3/4))/2=0.464$ to 3 significant figures.'),A('The maximum value is 5.'))],plot(lambda t:4*math.sin(2*t)+3*math.cos(2*t),(0,math.pi,-6,6)),calc=True,diff='medium')
add('geometry-trigonometry','A tetrahedron links area, height and volume','Vectors, lines and planes','3.16',r'A tetrahedron has vertices O=(0,0,0), B=(2,1,0), C=(0,3,1) and D=(1,0,4).',
 [P('Find the area of triangle OBC and a normal vector to its plane.',M(r'$\overrightarrow{OB}\times\overrightarrow{OC}=(1,-2,6)$.'),A(r'A normal is $(1,-2,6)$, of magnitude $\sqrt{41}$.'),A(r'The triangle area is $\sqrt{41}/2$.')),
 P('Find the perpendicular height from D to plane OBC and hence the tetrahedron volume.',M(r'The plane is $x-2y+6z=0$.'),A(r'The height is $|1+24|/\sqrt{41}=25/\sqrt{41}$.'),M('Use V=(1/3)×base area×height.'),A(r'$V=25/6$ cubic units.'))],spatial(['O','B','C','D']))
assert S.Matrix([2,1,0]).cross(S.Matrix([0,3,1]))==S.Matrix([1,-2,6])

# STATISTICS AND PROBABILITY: original data, conditional reasoning and densities.
def tree(labels):
 return shape([(65,190),(260,90),(260,285),(495,60),(495,135),(495,245),(495,320)],[(0,1),(0,2),(1,3),(1,4),(2,5),(2,6)],labels,'Probability tree; branch data are stated in the question')
add('statistics-probability','Tracing a defect back to its factory','Probability and conditional probability','4.13',r'Factories A, B and C supply 50%, 30% and 20% of items. Their defect probabilities are 0.02, 0.04 and 0.05 respectively. Items are selected independently from this mixed supply.',
 [P('Find the probability an item is defective and the probability it came from C given that it is defective.',M(r'$P(D)=0.5(0.02)+0.3(0.04)+0.2(0.05)=0.032$.'),M(r'$P(C\mid D)=0.2(0.05)/0.032$.'),A(r'$P(C\mid D)=5/16=0.3125$.')),
 P('Given that two independently selected items are both defective, find the probability at least one came from C.',R('Independence of selection makes the two factory labels conditionally independent after conditioning on their separate defect events.'),M(r'The complement is $(1-5/16)^2=(11/16)^2$.'),A(r'$1-121/256=135/256$.'))],tree(['supply','factory','other','defect','not defect','defect','not defect']))
add('statistics-probability','Two positive tests on one person','Probability and conditional probability','4.13',r'A condition affects 1% of a population. A test has sensitivity 0.95 and specificity 0.90. Conditional on whether a person has the condition, repeated tests are independent.',
 [P('Find the probability a person has the condition given one positive result.',M(r'$P(+)=0.01(0.95)+0.99(0.10)=0.1085$.'),M(r'$P(D\mid+)=0.0095/0.1085$.'),A('$P(D\\mid+)=0.0876$ to 3 significant figures.')),
 P('Find the corresponding probability given two positive results, and explain why squaring the first posterior is invalid.',M(r'$P(++\mid D)=0.95^2$ and $P(++\mid D^c)=0.10^2$.'),A(r'$P(D\mid++)=\frac{0.01(0.95)^2}{0.01(0.95)^2+0.99(0.10)^2}=0.477$ to 3 significant figures.'),R('The two results share the same underlying disease status. Conditional independence does not imply unconditional independence, and Bayes must update using both likelihoods.'))],tree(['person','condition .01','no condition .99','+ .95','− .05','+ .10','− .90']),calc=True)
add('statistics-probability','Conditioning an urn count','Discrete random variables','4.14',r'Two balls are drawn without replacement from four red and three blue balls. X is the number of red balls drawn. It is known that X≥1.',
 [P('Find the conditional distribution of X.',M(r'There are $\binom72=21$ pairs: 6 RR, 12 RB and 3 BB.'),M('Conditioning excludes the 3 BB pairs, leaving 18 equally likely pairs.'),A(r'$P(X=1\mid X\ge1)=2/3$, $P(X=2\mid X\ge1)=1/3$.')),
 P('Find the conditional mean and variance of X.',M(r'$E(X\mid X\ge1)=1(2/3)+2(1/3)=4/3$.'),M(r'$E(X^2\mid X\ge1)=2/3+4/3=2$.'),A(r'Variance $=2-(4/3)^2=2/9$.'))],tree(['two draws','first red','first blue','red','blue','red','blue']),diff='medium')
add('statistics-probability','A linear transformation changes the variance quadratically','Discrete random variables','4.14',r'X takes values −1, 0, 1 and 2 with probabilities k, 2k, 3k and 4k. Let Y=3X−2.',
 [P('Find k, the mean of X and its variance.',A('$k=0.1$ by normalization.'),M(r'$E(X)=-0.1+0+0.3+0.8=1$ and $E(X^2)=0.1+0.3+1.6=2$.'),A(r'$\operatorname{Var}(X)=2-1^2=1$.')),
 P('Find the mean and variance of Y, explaining why the constant −2 does not affect variance.',A('$E(Y)=3(1)−2=1$.'),A(r'$\operatorname{Var}(Y)=3^2\operatorname{Var}(X)=9$.'),R('Subtracting a constant shifts every outcome and the mean by the same amount, leaving deviations unchanged.'))],dots([(-1,.1),(0,.2),(1,.3),(2,.4)],'Probability mass function'),diff='medium')
add('statistics-probability','The price of a minimum-prize guarantee','Discrete random variables','4.14',r'A game pays X dollars, where X is 0, 4 or 10 with probabilities 0.5, 0.3 and 0.2. An optional guarantee changes the payout to Y=max(X,2).',
 [P('Find the fair entry fee for the original game and the variance of its payout.',M('$E(X)=0(0.5)+4(0.3)+10(0.2)=3.2$.'),A('The fair fee is 3.20 dollars.'),M('$E(X^2)=16(0.3)+100(0.2)=24.8$.'),A(r'$\operatorname{Var}(X)=24.8-3.2^2=14.56$.')),
 P('Find the fair additional price for the guarantee and explain which outcomes create its value.',M('$E(Y)=2(0.5)+4(0.3)+10(0.2)=4.2$.'),A('The fair additional price is 4.2−3.2=1 dollar.'),R('Only the zero-payout event changes; its increase of 2 occurs with probability 0.5.'))],dots([(0,.5),(4,.3),(10,.2)],'Original payouts and probabilities'),diff='medium')
add('statistics-probability','A symmetric parabolic density','Continuous random variables','4.14',r'X has density $f(x)=kx(2-x)$ on $0\le x\le2$, and zero otherwise.',
 [P('Find k and the mean of X.',M(r'$1=k\int_0^2(2x-x^2)\,dx=4k/3$.'),A('$k=3/4$.'),R('The density is symmetric about x=1, so E(X)=1.')),
 P(r'Find $\operatorname{Var}(X)$ and $P(|X-1|<1/2)$.',M(r'$E(X^2)=\frac34\int_0^2(2x^3-x^4)\,dx=6/5$.'),A(r'Variance $=6/5-1=1/5$.'),M(r'Integrate $\frac34x(2-x)$ from 1/2 to 3/2.'),A(r'The probability is $11/16$.'))],plot(lambda x:.75*x*(2-x),(0,2,0,1)))
eq(S.integrate(S.Rational(3,4)*X*(2-X),(X,S.Rational(1,2),S.Rational(3,2))),S.Rational(11,16))
add('statistics-probability','A triangular distribution and a high percentile','Continuous random variables','4.14',r'X has density $f(x)=kx$ for $0\le x\le1$, $f(x)=k(2-x)$ for $1<x\le2$, and zero otherwise.',
 [P('Find k and P(X>1.5).',M('The triangular density has base 2 and height k, so its total area is k.'),A('$k=1$.'),A(r'$P(X>1.5)=\frac12(0.5)(0.5)=1/8$.')),
 P('Find the 90th percentile exactly, explaining which branch contains it.',R('Symmetry gives P(X≤1)=1/2, so the 90th percentile q exceeds 1.'),M(r'$P(X>q)=(2-q)^2/2=0.1$.'),A(r'$q=2-1/\sqrt5$.'))],plot(lambda x:x if x<=1 else 2-x,(0,2,0,1.2)),diff='medium')
add('statistics-probability','A lifetime model with a median','Continuous random variables','4.14',r'A lifetime X in hours has density $f(x)=\lambda e^{-\lambda x}$ for $x\ge0$, with λ>0. Its median is 3 hours.',
 [P('Find λ and the probability the lifetime exceeds 9 hours.',M(r'$P(X>t)=\int_t^\infty\lambda e^{-\lambda x}\,dx=e^{-\lambda t}$.'),A(r'$e^{-3\lambda}=1/2$, so $\lambda=\ln2/3$.'),A(r'$P(X>9)=(1/2)^3=1/8$.')),
 P('Find P(X>12 | X>9) by using the definition of conditional probability, and interpret the result.',M(r'$P(X>12\mid X>9)=P(X>12)/P(X>9)$.'),A(r'$e^{-12\lambda}/e^{-9\lambda}=e^{-3\lambda}=1/2$.'),R('After surviving 9 hours, the probability of surviving another 3 hours equals the original probability of surviving 3 hours under this model.'))],plot(lambda x:math.log(2)/3*math.exp(-math.log(2)/3*x),(0,15,0,.3)),diff='medium')
add('statistics-probability','Capping a continuous payout creates a point probability','Continuous random variables','4.14',r'X is uniform on [0,4]. Let Y=min(X,2).',
 [P('Find P(Y=2) and explain why Y cannot have an ordinary continuous density alone.',M('Y=2 whenever X≥2.'),A('$P(Y=2)=1/2$.'),R('A single point has positive probability, so a density alone, which gives zero probability to every single point, cannot describe Y.')),
 P('Find the mean and variance of Y by splitting at X=2.',M(r'$E(Y)=\int_0^2x/4\,dx+2P(X\ge2)=3/2$.'),M(r'$E(Y^2)=\int_0^2x^2/4\,dx+4P(X\ge2)=8/3$.'),A(r'$\operatorname{Var}(Y)=8/3-9/4=5/12$.'))],plot(lambda x:min(x,2),(0,4,0,3),title='Payout Y as a function of X'))
add('statistics-probability','Two percentiles determine a normal distribution','Binomial and normal distributions','4.12',r'$X\sim N(\mu,\sigma^2)$ with σ>0. It is known that P(X<50)=0.10 and P(X<80)=0.90.',
 [P('Find μ and σ.',R('Symmetry places μ halfway between the two percentiles, so μ=65.'),M(r'$(80-65)/\sigma=\Phi^{-1}(0.90)=1.281551\ldots$.'),A('$σ=11.7$ to 3 significant figures.')),
 P('Find P(X>80 | X>65) without further numerical integration.',M('The event X>80 is a subset of X>65.'),A('$P(X>80\\mid X>65)=0.10/0.50=0.20$.'),R('The value follows from the given percentile and normal symmetry.'))],plot(lambda x:math.exp(-.5*((x-65)/11.704)**2),(25,105,0,1.2)),calc=True,diff='medium')
add('statistics-probability','Comparing two independent production measurements','Binomial and normal distributions','4.14',r'Independent measurements satisfy $A\sim N(100,4^2)$ and $B\sim N(102,3^2)$. Let D=A−B. You may use the fact that the difference of independent normal variables is normal, with the means subtracting and the variances adding.',
 [P('State the distribution of D and find P(A>B).',M('Independent normal differences are normal; the means subtract and the variances add.'),A(r'$D\sim N(-2,25)$.'),A(r'$P(D>0)=1-\Phi(0.4)=0.345$ to 3 significant figures.')),
 P('Find the probability the measurements differ by at most 5.',M(r'The event is $-5\le D\le5$.'),M('The standardized bounds are −0.6 and 1.4.'),A(r'$\Phi(1.4)-\Phi(-0.6)=0.645$ to 3 significant figures.'))],plot(lambda x:math.exp(-.5*((x+2)/5)**2),(-17,13,0,1.2)),calc=True)
add('statistics-probability','The smallest sample likely to include a rare type','Binomial and normal distributions','4.8',r'Each independently selected item has probability 0.12 of being type T. X is the number of type T items in a sample of n.',
 [P('Find the least n for which P(X≥1)>0.95.',M(r'$1-0.88^n>0.95$, so $n>\ln0.05/\ln0.88=23.434\ldots$.'),A('$n=24$.'),R('n=23 fails the strict inequality and n=24 satisfies it.')),
 P('For this sample size, find P(X=1 | X≥1).',M(r'$P(X=1)=24(0.12)(0.88)^{23}$.'),M(r'Divide by $1-0.88^{24}$, since X=1 is a subset of X≥1.'),A(r'$P(X=1\mid X\ge1)=0.160$ to 3 significant figures.'))],dots([(n,1-.88**n) for n in [5,10,15,20,25]],'Probability of at least one type T'),calc=True,diff='medium')
assert 1-.88**23<=.95<1-.88**24
add('statistics-probability','Equal binomial probabilities determine the parameter','Binomial and normal distributions','4.8',r'$X\sim B(5,p)$, where 0<p<1. It is known that P(X=1)=P(X=2).',
 [P('Find p exactly.',M(r'$5p(1-p)^4=10p^2(1-p)^3$.'),R('The stated domain permits division by 5p(1−p)³.'),A('$1-p=2p$, so p=1/3.')),
 P('Find P(X≥3) exactly.',M(r'Sum the probabilities for 3, 4 and 5 successes.'),A(r'They are $40/243$, $10/243$ and $1/243$.'),A(r'$P(X\ge3)=17/81$.'))],dots([(x,float(binom.pmf(x,5,1/3))) for x in range(6)],'Shape of the binomial distribution (probability scale omitted)',values=False),diff='medium')
add('statistics-probability','Independent copies and a repeated copy','Discrete random variables','4.14',r'X and Y are independent with the same distribution: P(0)=1/4, P(1)=1/2 and P(2)=1/4. Let U=X+Y and V=2X.',
 [P('Find the means and variances of U and V.',M(r'$E(X)=1$, $E(X^2)=3/2$, so $\operatorname{Var}(X)=1/2$.'),A(r'$E(U)=E(V)=2$.'),M(r'Enumerating U gives probabilities $(1,4,6,4,1)/16$ at 0,1,2,3,4, so $E(U^2)=5$.'),A(r'$\operatorname{Var}(U)=5-2^2=1$, whereas $\operatorname{Var}(V)=4\operatorname{Var}(X)=2$.')),
 P('Find P(U=2) and P(V=2), and explain the difference.',M('U=2 arises from (0,2), (1,1) and (2,0).'),A(r'$P(U=2)=1/16+1/4+1/16=3/8$; $P(V=2)=P(X=1)=1/2$.'),R('Adding an independent copy spreads outcomes differently from scaling the same random outcome.'))],tree(['sum','X=0 or 2','X=1','Y completes 2','other','Y=1','other']),diff='medium')
add('statistics-probability','The larger of two uniform measurements','Continuous random variables','4.14',r'U and V are independent uniform random variables on [0,1]. Let M=max(U,V). The distribution function is defined by $F_M(m)=P(M\le m)$.',
 [P('Find the distribution function and density of M for 0<m<1.',R('M≤m requires both U≤m and V≤m.'),A(r'$F_M(m)=m^2$ by independence.'),A(r'$f_M(m)=2m$ for 0<m<1, zero outside [0,1].')),
 P('Find the mean of M and its median exactly.',M(r'$E(M)=\int_0^1m(2m)\,dm$.'),A(r'$E(M)=2/3$.'),A(r'The median q satisfies $q^2=1/2$, so $q=1/\sqrt2$.'))],plot(lambda m:m*m,(0,1,0,1.2),title='Distribution function of the maximum'))
add('statistics-probability','A joint table and a dependent payout','Probability and conditional probability','4.14',r'The joint probabilities are P(X=0,Y=0)=0.4, P(0,1)=0.1, P(1,0)=0.2 and P(1,1)=0.3. Let W=3X+2Y.',
 [P('Determine whether X and Y are independent, with numerical evidence.',M('$P(X=1)=0.5$ and $P(Y=1)=0.4$.'),A('$P(X=1,Y=1)=0.3$, whereas 0.5×0.4=0.2.'),R('The unequal joint and marginal-product probabilities prove dependence.')),
 P('Find the mean and variance of W directly from its distribution.',M('W takes 0,2,3,5 with probabilities 0.4,0.1,0.2,0.3.'),A('$E(W)=2.3$ and $E(W^2)=9.7$.'),A(r'$\operatorname{Var}(W)=9.7-2.3^2=4.41$.'))],dots([(0,.4),(2,.1),(3,.2),(5,.3)],'Payout values from the four joint events'))
add('statistics-probability','A regression line survives a change of origin','Correlation and regression','4.4',r'For data $(x,y)=(1,5),(2,7),(3,12),(4,13),(5,18)$, use least-squares regression of y on x.',
 [P('Find the regression line and the residual at (3,12).',M(r'$\bar x=3$, $\bar y=11$, $S_{xx}=10$, $S_{xy}=32$.'),A(r'The line is $\hat y=1.4+3.2x$.'),A(r'At x=3, predicted y=11, so the residual is $12-11=1$.')),
 P('Every y-value is increased by 20. State the new regression line and the effect on the correlation coefficient, with reasons.',M('Adding 20 changes the mean y by 20 but leaves all deviations from that mean unchanged.'),A(r'The line becomes $\hat y=21.4+3.2x$.'),R('The correlation coefficient is unchanged because centered sums and standard deviations are unchanged.'))],dots([(1,5),(2,7),(3,12),(4,13),(5,18)],'Observed data'),calc=True,diff='medium')
add('statistics-probability','A mean depends on how two groups are weighted','Descriptive statistics','4.3',r'A school has 60 students in group A with mean travel time 12 minutes and 40 in group B with mean 18 minutes. A researcher reports 15 minutes by averaging the two group means.',
 [P('Find the correct school mean and explain the error in the report.',M('Total travel time is 60×12+40×18=1440 minutes.'),A('The overall mean is 1440/100=14.4 minutes.'),R('A simple average of group means assigns equal weight to unequal group sizes.')),
 P('A proportional stratified sample of 20 is planned. State how many to select from each group and describe a random selection method that avoids convenience bias.',A('Select 12 from A and 8 from B.'),M('Number all students in each group and use a random-number generator to select the required number without replacement.'),R('Random selection within each stratum gives every student the same sampling fraction and avoids selecting only readily available students.'))],dots([(1,12),(2,18)],'Group mean travel times; group sizes are stated in the question'),diff='medium')
add('statistics-probability','Choosing a threshold to maximize an expected prize','Continuous random variables','4.14',r'X has density f(x)=2x on [0,1]. Before observing X, a player chooses t in [0,1]. The prize is t dollars if X≥t and zero otherwise.',
 [P('Find the expected prize as a function of t.',M(r'$P(X\ge t)=\int_t^1 2x\,dx=1-t^2$.'),M('The nonzero prize t is multiplied by its probability.'),A(r'$E(t)=t(1-t^2)$.')),
 P('Find the optimal t and the maximum expected prize, checking endpoints.',M(r'$E^{\prime}(t)=1-3t^2=0$ gives $t=1/\sqrt3$.'),R('The derivative changes + to −; both endpoint prizes have expectation zero.'),A(r'The maximum expectation is $2/(3\sqrt3)$ dollars.'))],plot(lambda x:2*x,(0,1,0,2.3)))
add('statistics-probability','Evidence that leaves the prior unchanged','Probability and conditional probability','4.13',r'Urn A is selected with probability 1/3 and contains three red balls and one blue. Urn B is selected with probability 2/3 and contains one red and three blue. Two balls are drawn without replacement from the selected urn.',
 [P('Given two red balls, find the probability A was selected.',M(r'$P(RR\mid A)=(3/4)(2/3)=1/2$ and $P(RR\mid B)=0$.'),A('$P(RR)=1/6$.'),R('Two red balls are impossible from B, so the posterior probability of A is 1.')),
 P('Given exactly one red and one blue, find the posterior probability of A and explain the result.',M(r'$P(\text{one of each}\mid A)=3/6=1/2$ and the same probability holds for B.'),A(r'$P(A\mid\text{one of each})=\frac{(1/3)(1/2)}{(1/3)(1/2)+(2/3)(1/2)}=1/3$.'),R('The evidence has equal likelihood under both urns, so it does not change the prior odds.'))],tree(['choose urn','A: prior 1/3','B: prior 2/3','red','blue','red','blue']))

# CALCULUS I: analytical and spatial reasoning, with explicit global checks.
add('calculus-1','A tangent and concavity on an implicit curve','Differentiation','5.14',r'The curve $x^2+xy+y^2=7$ passes through P=(1,2).',
 [P('Find the tangent and normal at P.',M(r'$2x+y+(x+2y)y^{\prime}=0$, hence at P, $y^{\prime}=-4/5$.'),A(r'Tangent: $y-2=-\frac45(x-1)$.'),A(r'Normal: $y-2=\frac54(x-1)$.')),
 P('Find the second derivative at P and describe the local concavity.',M(r'Differentiating again gives $2+2y^{\prime}+2(y^{\prime})^2+(x+2y)y^{\prime\prime}=0$.'),A(r'At P, $y^{\prime\prime}=-42/125$.'),R('The second derivative is negative, so the local branch is concave down at P.'))],plot(lambda x:(-x+math.sqrt(28-3*x*x))/2,(-2,2.8,0,4),points=[(1,2,'P')]))
add('calculus-1','A draining cone changes its surface at a different rate','Applications of differentiation','5.14',r'Water occupies a cone whose radius r is half its depth h. The volume decreases at 2 cubic centimetres per second. At one instant h=4 cm.',
 [P('Find the rate of change of h at that instant.',M(r'$V=\frac13\pi r^2h=\pi h^3/12$.'),M(r'$-2=(\pi h^2/4)\,dh/dt$.'),A(r'$dh/dt=-1/(2\pi)$ cm s$^{-1}$.')),
 P('Find the rate of change of the circular water-surface area and interpret its sign.',M(r'$A=\pi r^2=\pi h^2/4$, so $dA/dt=(\pi h/2)\,dh/dt$.'),A(r'$dA/dt=-1$ cm$^2$ s$^{-1}$.'),R('The negative sign means the exposed circular surface is shrinking.'))],shape([(320,325),(170,110),(470,110),(320,110)],[(0,1),(0,2),(1,2),(0,3)],['cone apex','water edge','water edge','h; radius h/2'],'Water in a conical vessel'))
add('calculus-1','The largest symmetric rectangle under a parabola','Applications of differentiation','5.8',r'A rectangle has its lower side on the x-axis and its upper vertices on $y=9-x^2$. It is symmetric about the y-axis and lies above the x-axis.',
 [P('Express its area in terms of the positive x-coordinate a of its upper-right vertex, stating the domain.',M('The width is 2a and the height is 9−a².'),A(r'$A(a)=2a(9-a^2)$.'),A('$0\\le a\\le3$.')),
 P('Find the maximum area exactly and justify its global nature.',M(r'$A^{\prime}(a)=18-6a^2=0$ gives $a=\sqrt3$.'),A(r'The maximum area is $12\sqrt3$.'),R('The derivative changes from positive to negative at √3; both endpoint areas are zero.'))],plot(lambda x:9-x*x,(-3.2,3.2,0,10)),diff='medium')
add('calculus-1','A costed cylinder does not have equal height and diameter','Applications of differentiation','5.14',r'An open cylindrical tank has volume $500\pi$ cm$^3$. Its base costs 3 units per cm$^2$ and its curved wall costs 1 unit per cm$^2$. Ignore thickness.',
 [P('Show that the total cost can be written in terms of radius r as C=3πr²+1000π/r.',M(r'From $\pi r^2h=500\pi$, $h=500/r^2$.'),M(r'Cost = $3(\pi r^2)+2\pi rh$.'),A(r'$C(r)=3\pi r^2+1000\pi/r$, r>0.')),
 P('Find the radius giving minimum cost and express the corresponding height in terms of r.',M(r'$C^{\prime}(r)=6\pi r-1000\pi/r^2=0$, so $r^3=500/3$.'),A(r'$r=(500/3)^{1/3}$ cm and $h=3r$.'),R(r'$C^{\prime\prime}(r)=6\pi+2000\pi/r^3>0$ for r>0, so the stationary point is the unique global minimum.'))],shape([(180,120),(460,120),(180,305),(460,305)],[(0,1),(0,2),(1,3),(2,3)],['rim','r','base','h'],'Open cylinder; axial outline'))
add('calculus-1','A parameter must remove a first-order term','Limits and continuity','5.13',r'For real a, consider $L=\lim_{x\to0}(e^{2x}-1-ax)/x^2$.',
 [P('Find the only a for which L is finite, giving a justification.',M(r'$\lim_{x\to0}(e^{2x}-1-ax)/x=2-a$.'),R('If 2−a is nonzero, division by the additional x cannot have a finite two-sided limit.'),A('$a=2$.')),
 P('For this value of a, evaluate L using l’Hôpital’s rule, stating why the rule applies at each stage.',M(r'The initial quotient is 0/0; differentiate to get $(2e^{2x}-2)/(2x)$.'),M(r'This is again 0/0; differentiating gives $4e^{2x}/2$.'),A('$L=2$.'))],plot(lambda x:(math.exp(2*x)-1-2*x)/(x*x),(-.5,.5,1,3.6)))
eq(S.limit((S.exp(2*X)-1-2*X)/X**2,X,0),2)
add('calculus-1','Two tangents from a point below a parabola','Applications of differentiation','5.3',r'Two tangents are drawn from P=(0,−4) to the parabola y=x².',
 [P('Find both tangents and their points of contact.',M(r'The tangent at x=a is $y=2ax-a^2$.'),M('Passing through P requires −a²=−4, so a=±2.'),A('The tangents are y=4x−4 at (2,4) and y=−4x−4 at (−2,4).')),
 P('Find the area enclosed by the two tangents and the parabola.',M(r'By symmetry the area is $2\int_0^2[x^2-(4x-4)]\,dx$.'),M(r'This is $2\int_0^2(x-2)^2\,dx$.'),A(r'The area is $16/3$ square units.'))],plot([lambda x:x*x,lambda x:4*x-4,lambda x:-4*x-4],(-2.5,2.5,-5,7),labels=['parabola','right tangent','left tangent']),diff='medium')
add('calculus-1','First principles and parallel normals','Differentiation','5.12',r'Let f(x)=x³−2x.',
 [P('Derive f prime from first principles.',M(r'$f^{\prime}(x)=\lim_{h\to0}[(x+h)^3-2(x+h)-x^3+2x]/h$.'),M(r'The quotient simplifies to $3x^2+3xh+h^2-2$.'),A(r'$f^{\prime}(x)=3x^2-2$.')),
 P('Find all points where the normal is parallel to y=−x.',M('A normal slope of −1 requires tangent slope 1.'),M('$3x^2−2=1$ gives x=±1.'),A('The points are (1,−1) and (−1,1).'))],plot(lambda x:x**3-2*x,(-2,2,-5,5)),diff='medium')
add('calculus-1','The vertical gap between two turning points','Applications of differentiation','5.7',r'For k>0, f(x)=x³−3kx. The vertical distance between its local maximum and minimum is 32.',
 [P('Express the stationary coordinates in terms of k.',M(r'$f^{\prime}(x)=3(x^2-k)=0$, so $x=\pm\sqrt k$.'),A(r'Local maximum $(-\sqrt k,2k^{3/2})$.'),A(r'Local minimum $(\sqrt k,-2k^{3/2})$.')),
 P('Find k and the zeros of f for this value of k.',M(r'$4k^{3/2}=32$, so $k=4$.'),M(r'$f(x)=x(x^2-12)$.'),A(r'The zeros are $-2\sqrt3,0,2\sqrt3$.'))],plot(lambda x:x**3-12*x,(-4,4,-22,22)),diff='medium')
add('calculus-1','A variable appears in both base and exponent','Differentiation','5.14',r'f(x)=x^x for x>0.',
 [P('Use logarithmic differentiation to find f prime.',M(r'Let y=x^x. Then $\ln y=x\ln x$.'),M(r'$y^{\prime}/y=\ln x+1$.'),A(r'$f^{\prime}(x)=x^x(\ln x+1)$.')),
 P('Find the global minimum and show that the graph is convex on its full domain.',M(r'The derivative vanishes at $x=e^{-1}$, and changes from negative to positive.'),A(r'The global minimum value is $e^{-1/e}$.'),M(r'$f^{\prime\prime}(x)=x^x[(\ln x+1)^2+1/x]$.'),R('Every factor is positive for x>0, so the graph is strictly convex.'))],plot(lambda x:x**x,(.03,2,0,4.5)))
add('calculus-1','A sliding ladder accelerates downward','Applications of differentiation','5.14',r'A ladder of length 10 m rests against a vertical wall. Its foot moves away from the wall at a constant 0.5 m s$^{-1}$. Let x be the foot’s distance from the wall and y its height.',
 [P('When x=6, find y and its rate of change.',A('$y=\\sqrt{100-36}=8$ m.'),M(r'From $x^2+y^2=100$, $dy/dt=-(x/y)(dx/dt)$.'),A(r'$dy/dt=-3/8$ m s$^{-1}$.')),
 P('Find the downward acceleration of the top at that instant.',M(r'Differentiate $x\dot x+y\dot y=0$: $\dot x^2+\dot y^2+y\ddot y=0$, since $\ddot x=0$.'),M(r'$\ddot y=-[(1/2)^2+(-3/8)^2]/8$.'),A(r'$\ddot y=-25/512$ m s$^{-2}$.'),R('The negative acceleration means the downward speed is increasing.'))],shape([(140,310),(500,310),(140,80)],[(0,1),(0,2),(1,2)],['wall–ground','foot x','top y'],'Ladder of fixed length 10 m'))

# CALCULUS II: exact integration, dynamic models, series and numerical comparison.
add('calculus-2','A logarithmic integral becomes a density moment','Integration','5.16',r'Let $I=\int_0^1x\ln(1+x)\,dx$.',
 [P('Evaluate I exactly using integration by parts.',M(r'Take $u=\ln(1+x)$ and $dv=x\,dx$, giving $I=[x^2\ln(1+x)/2]_0^1-\frac12\int_0^1x^2/(1+x)\,dx$.'),M(r'Use $x^2/(1+x)=x-1+1/(1+x)$.'),A(r'$I=\frac12\ln2-\frac12(\frac12-1+\ln2)=1/4$.')),
 P(r'A probability density is $f(x)=c\ln(1+x)$ on [0,1]. Find c and its mean.',M(r'$\int_0^1\ln(1+x)\,dx=2\ln2-1$.'),A(r'$c=1/(2\ln2-1)$.'),A(r'The mean is $cI=1/[4(2\ln2-1)]$.'))],plot(lambda x:math.log(1+x),(0,1,0,.9)))
eq(S.integrate(X*S.log(1+X),(X,0,1)),S.Rational(1,4))
add('calculus-2','The same region rotates about two different axes','Applications of integration','5.17',r'R is bounded by y=ln x, y=0 and x=e, with 1≤x≤e.',
 [P('Find the volume when R rotates about the x-axis.',M(r'$V_x=\pi\int_1^e(\ln x)^2\,dx$.'),M(r'An antiderivative is $x[(\ln x)^2-2\ln x+2]$ by repeated integration by parts.'),A(r'$V_x=\pi(e-2)$.')),
 P('Find the volume when R rotates about the y-axis, using integration with respect to y.',M(r'For 0≤y≤1, the region runs from x=e^y to x=e.'),M(r'The cross-section is an annulus with area $\pi(e^2-e^{2y})$.'),A(r'$V_y=\pi\int_0^1(e^2-e^{2y})\,dy=\pi(e^2+1)/2$.'))],plot(lambda x:math.log(x),(0,3,-.2,1.5),title='Region below ln x between x=1 and x=e'))
eq(S.integrate(S.exp(2)-S.exp(2*X),(X,0,1)),(S.exp(2)+1)/2)
add('calculus-2','A logistic model has its fastest growth halfway up','Differential equations','5.18',r'A population y satisfies $dy/dx=y(1-y/4)$ and y(0)=1.',
 [P('Solve for y by separation of variables.',M(r'$1/[y(1-y/4)]=1/y+1/(4-y)$.'),M(r'$\ln(y/(4-y))=x+C$ on the solution branch 0<y<4.'),A(r'$y=4/(1+3e^{-x})$.')),
 P('Find when y first reaches 3, and when its growth rate is greatest.',M(r'For y=3, $e^{-x}=1/9$, hence $x=\ln9$.'),M(r'The growth function $y-y^2/4$ is a concave quadratic maximized at y=2.'),A(r'Maximum growth occurs at $x=\ln3$, with $dy/dx=1$.'))],plot(lambda x:4/(1+3*math.exp(-x)),(0,6,0,4.5)),calc=True,style='problem-solving')
add('calculus-2','A homogeneous differential equation needs a substitution','Differential equations','5.18',r'For x>0, $dy/dx=(x+y)/x$ and y(1)=2. Use the substitution y=vx.',
 [P('Find an explicit solution.',M(r'$dy/dx=v+x\,dv/dx$; substitution gives $v+xv^{\prime}=1+v$.'),M(r'$v^{\prime}=1/x$, so $v=\ln x+C$.'),A(r'$y=x(\ln x+2)$ using y(1)=2.')),
 P('Find the positive x-intercept and the minimum point of this solution.',M(r'y=0 gives $\ln x=-2$, so $x=e^{-2}$.'),M(r'$y^{\prime}=\ln x+3=0$ gives $x=e^{-3}$.'),A(r'The minimum is $(e^{-3},-e^{-3})$, since $y^{\prime\prime}=1/x>0$.'))],plot(lambda x:x*(math.log(x)+2),(.005,1,-.2,2.2)))
add('calculus-2','Checking Euler estimates against an exact solution','Differential equations','5.18',r'$y^{\prime}=x-y$, y(0)=1. Estimate y(1) by Euler’s method, retaining full precision.',
 [P('Use step size h=0.5 for two steps.',M(r'Update $y_{n+1}=y_n+0.5(x_n-y_n)$.'),A('$y(0.5)\\approx1+0.5(0-1)=0.5$.'),A('$y(1)\\approx0.5+0.5(0.5-0.5)=0.5$.')),
 P(r'Verify the exact solution $y=x-1+2e^{-x}$, then compare the errors for h=0.5 and a single h=1 step.',M(r'The derivative is $1-2e^{-x}=x-y$, and y(0)=1.'),A(r'The exact value is $2/e=0.735758\ldots$.'),M('The h=1 estimate is 1+1(0−1)=0.'),A('Absolute errors are 0.236 for h=0.5 and 0.736 for h=1, to 3 significant figures; the two-step estimate is closer in this example.'))],plot(lambda x:x-1+2*math.exp(-x),(0,1,0,1.2)),calc=True,diff='medium')
add('calculus-2','Multiplying two series before integrating','Maclaurin series','5.19',r'Let $f(x)=\ln(1+x)/(1+x)$ for |x|<1.',
 [P('Find the Maclaurin expansion of f through the x³ term.',M(r'Use $\ln(1+x)=x-x^2/2+x^3/3+\cdots$ and $(1+x)^{-1}=1-x+x^2-x^3+\cdots$.'),M('Multiply and collect equal powers.'),A(r'$f(x)=x-\frac32x^2+\frac{11}{6}x^3+O(x^4)$.')),
 P(r'Use this expansion to approximate $\int_0^{0.1}f(x)\,dx$, and give an exact expression for the same integral.',M(r'Termwise integration gives $a^2/2-a^3/2+11a^4/24$ at a=0.1.'),A('The approximation is 0.00454583 (6 significant figures).'),M(r'Use $u=\ln(1+x)$; $du=dx/(1+x)$.'),A(r'The exact integral is $\frac12[\ln(1.1)]^2$.'))],plot(lambda x:math.log(1+x)/(1+x),(0,.4,0,.3)),calc=True)
eq(S.series(S.log(1+X)/(1+X),X,0,4).removeO(),X-S.Rational(3,2)*X**2+S.Rational(11,6)*X**3)
add('calculus-2','A reduction relation avoids a fourth-power expansion','Integration','5.16',r'For positive integers n, define $I_n=\int_0^{\pi/2}\sin^n x\,dx$.',
 [P(r'Use integration by parts to prove $I_n=\frac{n-1}{n}I_{n-2}$ for n≥2.',M(r'Write $I_n=\int\sin^{n-1}x\sin x\,dx$ and integrate the final sine factor.'),M(r'The boundary term vanishes, giving $I_n=(n-1)\int_0^{\pi/2}\sin^{n-2}x\cos^2x\,dx$.'),A(r'$I_n=(n-1)(I_{n-2}-I_n)$, so $nI_n=(n-1)I_{n-2}$.')),
 P(r'Hence evaluate $\int_0^{\pi/2}\sin^4x\cos^2x\,dx$ exactly.',M(r'$I_0=\pi/2$, so $I_4=3\pi/16$ and $I_6=5\pi/32$.'),M('The required integral is I₄−I₆.'),A(r'The value is $\pi/32$.'))],plot(lambda x:math.sin(x)**4*math.cos(x)**2,(0,math.pi/2,0,.2)))
add('calculus-2','A convergent improper integral with a tail estimate','Integration','5.16',r'Consider $J=\int_1^\infty(\ln x)/x^2\,dx$. Interpret this as a limit of integrals with finite upper endpoint B.',
 [P('Evaluate J and justify convergence.',M(r'Integration by parts gives $\int_1^B(\ln x)/x^2\,dx=1-(\ln B+1)/B$.'),M(r'$\ln B/B\to0$ by l’Hôpital’s rule, and 1/B→0.'),A('$J=1$, so the integral converges.')),
 P('Find the exact error if the upper endpoint is replaced by e², and explain the sign.',M(r'The omitted tail is $(\ln B+1)/B$.'),A(r'At $B=e^2$, the error is $3/e^2$.'),R('The finite integral underestimates J because the integrand is nonnegative on [1,∞).'))],plot(lambda x:math.log(x)/x**2,(1,10,0,.2)))
add('calculus-2','Area and volume between an odd pair of curves','Applications of integration','5.17',r'R is the union of the two bounded regions enclosed by y=x and y=x³.',
 [P('Find the total area of R.',M(r'The intersections satisfy $x(x^2-1)=0$, so x=−1,0,1.'),M(r'By symmetry, area $=2\int_0^1(x-x^3)\,dx$.'),A(r'The total area is $1/2$.')),
 P('Find the volume obtained when the whole of R rotates about the x-axis.',M(r'For both signs of x, the outer radius is |x| and inner radius is |x³|.'),M(r'$V=2\pi\int_0^1(x^2-x^6)\,dx$.'),A(r'$V=8\pi/21$.'))],plot([lambda x:x,lambda x:x**3],(-1.2,1.2,-1.5,1.5),labels=['y=x','y=x³']),diff='medium')
add('calculus-2','An equation determines its own power-series coefficients','Maclaurin series','5.19',r'An analytic function satisfies y prime=y+x and y(0)=1. Write $y=\sum_{n=0}^{\infty}a_nx^n$.',
 [P('Find a₀ through a₄ by comparing coefficients.',A('$a_0=1$ and $a_1=a_0=1$.'),M(r'Coefficient of x: $2a_2=a_1+1$, giving a₂=1.'),M(r'For n≥2, $(n+1)a_{n+1}=a_n$.'),A(r'$a_3=1/3$, $a_4=1/12$.')),
 P(r'Verify that $y=2e^x-x-1$ is the exact solution and that its expansion agrees.',M(r'Its derivative $2e^x-1$ equals y+x and it has y(0)=1.'),M(r'Expand $2(1+x+x^2/2+x^3/6+x^4/24+\cdots)-x-1$.'),A(r'$y=1+x+x^2+x^3/3+x^4/12+\cdots$, agreeing with the coefficients.'))],plot(lambda x:2*math.exp(x)-x-1,(-1,1,0,4)),calc=True,style='problem-solving')

# Independent visual audit: replace generic spatial sketches by incidence-correct
# projections, and complete the circular/ambiguity constructions.
qbyid={q['id']:q for q in Q}
def replace_figure(suffix,drawing):qbyid['ib-aa-'+suffix]['diagramSvg']=drawing
def vecadd(a,b,k=1):return tuple(x+k*y for x,y in zip(a,b))
base=(1,2,3);direction=(2,-1,2);foot=vecadd(base,direction,1/9)
replace_figure('gt-701',scene3({'L0':vecadd(base,direction,-1),'L1':vecadd(base,direction,2),'A':base,'H':foot,'P':(4,1,0)},[('L0','L1',False),('P','H',True)],{'A':('A',-30,20),'H':('H',8,-18),'P':'P','L1':'L'}))
a=(1,0,2);da=(1,2,-1);b=(3,1,0);db=(-1,1,1)
replace_figure('gt-702',scene3({'A0':vecadd(a,da,-1),'A1':vecadd(a,da,2),'B0':vecadd(b,db,-1),'B1':vecadd(b,db,2),'I':(2,2,1)},[('A0','A1',False),('B0','B1',False)],{'A0':'L1','B0':'L2','I':'intersection'}))
replace_figure('gt-703',scene3({'A0':(-2,0,0),'A1':(2,0,0),'B0':(0,-.5,2.5),'B1':(0,2.5,-.5),'O':(0,0,0),'H':(0,1,1)},[('A0','A1',False),('B0','B1',False),('O','H',True)],{'A1':'L1','B0':'L2','O':'O','H':'Q on L2'}))
replace_figure('gt-704',scene3({'O':(0,0,0),'A':(1,0,0),'B':(0,2,0),'C':(0,0,3)},[(a,b,False) for a,b in [('O','A'),('O','B'),('O','C'),('A','B'),('B','C'),('A','C')]],{'O':'O','A':'A','B':'B','C':'C'},[('A','B','C')]))
pp={'P':(3,2,1),'H':(2,0,-1),'R':(1,-2,-3)};u=(2,-1,0);v=(2,0,-1)
for i,(a,b) in enumerate([(-1,-1),(1,-1),(1,1),(-1,1)]):pp['F'+str(i)]=vecadd(vecadd(pp['H'],u,a),v,b)
replace_figure('gt-705',scene3(pp,[('P','R',True)],{'P':'P','H':'H','R':'reflection'},[('F0','F1','F2','F3')]))
pp={};anchor=(0,2,2);dline=(1,0,-1)
for panel,u in [('A',(1,-1,0)),('B',(1,1,0))]:
 for i,(a,b) in enumerate([(-1.7,-1),(1.7,-1),(1.7,1),(-1.7,1)]):pp[panel+str(i)]=vecadd(vecadd(anchor,dline,a),u,b)
pp.update({'I0':vecadd(anchor,dline,-2),'I1':vecadd(anchor,dline,2)})
replace_figure('gt-706',scene3(pp,[('I0','I1',False)],{'A0':'plane 1','B3':'plane 2','I1':'intersection'},[('A0','A1','A2','A3'),('B0','B1','B2','B3')]))
replace_figure('gt-708',svg([text(35,25,'Two vectors from a common origin; angle depends on k',15),line(130,280,440,255),line(130,280,360,90),text(450,258,'a = (1,k,1)',14),text(365,85,'b = (1,-1,2)',14),text(105,303,'O',15),'<path d="M200 274 A70 70 0 0 0 183 235" fill="none" stroke="#111"/>',text(211,241,'angle',13),text(30,361,'Directions are schematic; determine angles from the given vectors.',12)]))
pp={'A':(0,0,0),'B':(1,2,0),'C':(2,0,1),'R':(2,0,-1),'F0':(-1,-1,0),'F1':(3,-1,0),'F2':(3,3,0),'F3':(-1,3,0)}
replace_figure('gt-709',scene3(pp,[('A','B',False),('A','C',False),('B','C',False),('A','R',True),('B','R',True),('C','R',True)],{'A':'A','B':'B','C':'C (k > 0)','R':'reflected C'},[('F0','F1','F2','F3')],title='Reflection in the xy-plane; an illustrative positive k'))
replace_figure('gt-715',svg([text(30,25,'Chord and minor segment of the given circle',16),'<circle cx="320" cy="180" r="125" fill="none" stroke="#111" stroke-width="1.7"/>',line(220,255,420,255),line(320,180,220,255),line(320,180,420,255),line(320,180,320,255,True),text(324,172,'O'),text(204,277,'A'),text(425,277,'B'),text(327,224,'3 cm'),text(240,210,'5 cm',13),'<path d="M310 255V245H320" fill="none" stroke="#111"/>',text(30,361,'Circle geometry is drawn proportionally; angle and segment area are unknown.',12)]))
replace_figure('gt-716',svg([text(30,25,'Cone axial section with the inscribed sphere section',16),line(320,60,140,300),line(320,60,500,300),line(140,300,500,300),line(320,60,320,300,True),'<circle cx="320" cy="210" r="90" fill="none" stroke="#111" stroke-width="1.7"/>',text(327,55,'apex'),text(331,210,'centre'),line(320,325,500,325),text(390,346,'6 cm',14),line(100,60,100,300),text(50,185,'8 cm',14),text(30,361,'The section circle is tangent to both sides and the base.',12)]))
cshort=5*math.sqrt(3)-math.sqrt(11);clong=5*math.sqrt(3)+math.sqrt(11)
replace_figure('gt-717',svg([text(30,25,'Both possible triangles satisfy the stated measurements',15),line(70,310,70+40*clong,310),line(70,310,70+200*math.sqrt(3),110),line(70+40*clong,310,70+200*math.sqrt(3),110),line(70+40*cshort,310,70+200*math.sqrt(3),110,True),text(52,333,'A'),text(70+40*cshort-7,335,'B1'),text(70+40*clong-7,335,'B2'),text(75+200*math.sqrt(3),102,'C'),text(116,299,'30 deg',13),text(220,190,'10 cm',13),text(390,236,'6 cm',13),text(507,214,'6 cm',13),text(30,361,'The two base lengths are to be found; both triangles are shown.',12)]))
circR=math.sqrt((3*4+5*6)*(3*5+4*6)*(3*6+4*5))/(4*6*math.sqrt(10));angles=[math.radians(150)]
for side in [3,4,5]:angles.append(angles[-1]+2*math.asin(side/(2*circR)))
cp=[(320+125*math.cos(a),190+125*math.sin(a)) for a in angles]
els=[text(30,25,'Cyclic quadrilateral with the given side lengths',16),'<circle cx="320" cy="190" r="125" fill="none" stroke="#777"/>']
for i in range(4):
 j=(i+1)%4;els+=[line(*cp[i],*cp[j]),text(cp[i][0]+7,cp[i][1]-8,'ABCD'[i]),text((cp[i][0]+cp[j][0])/2,(cp[i][1]+cp[j][1])/2-8,[3,4,5,6][i],13)]
els +=[line(*cp[0],*cp[2],True),text((cp[0][0]+cp[2][0])/2+8,(cp[0][1]+cp[2][1])/2,'x',14)]
replace_figure('gt-718',svg(els,'Cyclic quadrilateral; all vertices lie on one circle'))
replace_figure('gt-720',scene3({'O':(0,0,0),'B':(2,1,0),'C':(0,3,1),'D':(1,0,4)},[(a,b,a=='O' and b=='C') for a,b in [('O','B'),('O','C'),('O','D'),('B','C'),('B','D'),('C','D')]],{'O':'O','B':'B','C':'C','D':'D'},[('O','B','C')]))
els=[text(30,25,'Factory and defect events for one selected item',16)]
for name,prior,defect,mid in [('A','0.5','0.02',90),('B','0.3','0.04',190),('C','0.2','0.05',290)]:
 els +=[line(70,190,250,mid),text(160,(190+mid)/2-8,prior,13),text(255,mid+4,name,15)]
 for label,prob,dy in [('defect',defect,-30),('not defect',str(1-float(defect)),30)]:
  els +=[line(275,mid,480,mid+dy),text(380,mid+dy/2-7,prob,13),text(487,mid+dy+4,label,13)]
els +=[text(30,207,'supply',13)]
replace_figure('sp-701',svg(els,'Three factories, each with defective and non-defective outcomes'))
sx=lambda x:58+(x+3.3)/6.6*520
sy=lambda y:326-y/10*270
rectangle=plot(lambda x:9-x*x,(-3.3,3.3,0,10),title='One admissible rectangle; a is a variable')
extra='<polygon points="'+' '.join(f'{sx(x):.2f},{sy(y):.2f}' for x,y in [(-1.5,0),(1.5,0),(1.5,6.75),(-1.5,6.75)])+'" fill="none" stroke="#111" stroke-width="1.7"/>'+text(sx(1.5)+8,sy(0)-8,'a',14)
replace_figure('c1-703',rectangle.replace('</svg>',extra+'</svg>'))
replace_figure('c1-704',svg([text(30,25,'Open cylindrical tank with radius r and height h',16),'<ellipse cx="315" cy="90" rx="105" ry="30" fill="none" stroke="#111"/>',line(210,90,210,285),line(420,90,420,285),'<ellipse cx="315" cy="285" rx="105" ry="30" fill="none" stroke="#111"/>',line(315,90,420,90),line(455,90,455,285),text(364,80,'r',15),text(465,190,'h',15),text(30,361,'Open top; base material costs three times the wall material per unit area.',12)]))
replace_figure('c1-710',shape([(210,320),(450,320),(210,0+80)],[(0,1),(0,2),(1,2)],['wall-ground','foot x','top y'],'Ladder of fixed length 10 m'))

def save():
 assert len(Q)==100,len(Q)
 from collections import Counter
 assert Counter(q['topicId'] for q in Q)=={t:20 for t in ['number-algebra','functions','geometry-trigonometry','statistics-probability','calculus']}
 out=ROOT/'content/ib/math-2026-expansion';out.mkdir(parents=True,exist_ok=True)
 (out/'aa-hl.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 reviews=ROOT/'docs/ib-2026-maths';reviews.mkdir(parents=True,exist_ok=True)
 (reviews/'aa-hl-author-review.json').write_text(json.dumps(dict(course='math-aa-hl',questions=100,diagrams=sum('diagramSvg' in q for q in Q),method='100 explicitly authored problems; worked algebra, selected symbolic assertions, domain/branch checks; independent audit required separately.',records=CHECKS),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps(dict(course='AA HL',questions=len(Q),diagrams=sum('diagramSvg' in q for q in Q),difficulty=dict(Counter(q['difficulty'] for q in Q)))))
if __name__=='__main__':save()
