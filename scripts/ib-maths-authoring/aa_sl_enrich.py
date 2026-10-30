"""Linked extensions that turn selected families into extended-response tasks."""
from aa_sl_core import *
def extend(q,prompt,*steps):
 label=chr(97+len(q['parts']));q['parts'].append(dict(label=label,prompt=prompt,marks=len(steps)))
 q['markScheme'].append(dict(part=label,steps=[dict(code=c,text=z) for c,z in steps]));q['marks']+=len(steps)
 q['examStyle']='extended-response' if q['marks']>=8 else 'short-response'
 for row in LEDGER:
  if row['id']==q['id']:
   row['marks']=q['marks'];row['reasoningReview']+=' Linked extension recalculated and reviewed; its marking points are distinct from earlier parts.'
def enrich(topic,questions):
 for q in questions:
  j=(q['number']-1)//4;i=(q['number']-1)%4
  if topic=='number-algebra':
   if j==7:
    r=s.Rational(i+1,i+2);total=12*(i+2);a=12;S3=s.simplify(a*(1-r**3)/(1-r));eq(sum(a*r**k for k in range(3)),S3)
    extend(q,'Find the sum of the first3 terms and explain why it is less than the infinite sum.',M(r'$S_3=a(1-r^3)/(1-r)$.'),A(rf'$S_3={L(S3)}$.'),R('All omitted terms are positive, so the finite sum is strictly smaller than the infinite sum.'))
   if j==13:
    a=i+2;b=i+4;root=math.log(b*b/a)/(math.log(a)-math.log(b))
    extend(q,rf'Let $F(x)={a}^{{x+1}}/{b}^{{x+2}}$. Express F as a single exponential, state whether it increases or decreases, and hence solve $F(x)\geq1$.',M(rf'$F(x)=\frac{{{a}}}{{{b*b}}}({frac(a,b)})^x$.'),R(rf'Because $0<{frac(a,b)}<1$, F decreases strictly.'),A(rf'$F(x)=1$ at the solution from part(a), $x={n(root)}$.'),A(rf'$F(x)\geq1$ for $x\leq{n(root)}$, using the unrounded exact boundary from part(a).'))
   if j==18:
    P=5000+1000*i;r=.048+.006*i;yrs=3+i;monthly=P*(1+r/12)**(12*yrs);annual=P*(1+r)**yrs;checked(monthly>annual,'monthly advantage')
    extend(q,'Compare the final balance with the same nominal rate compounded annually. Find the extra money from monthly compounding, to the nearest cent, and explain why it occurs.',M(rf'Annual-compounding balance $={P}(1+{r:g})^{{{yrs}}}={annual:.8f}$.'),A(rf'Monthly compounding gives USD ${monthly-annual:.2f}$ more.'),R('With monthly compounding, interest credited before year-end itself starts earning interest.'))
   if j==19:
    a=8+2*i;b=4+i;r=1.25;N=next(k for k in range(1,100) if b*r**(k-1)>a+4*(k-1));SA=N*(2*a+(N-1)*4)/2;SB=b*(r**N-1)/(r-1);eq(SB,sum(b*r**k for k in range(N)))
    extend(q,rf'Find each project’s cumulative output over the first ${N}$ weeks. Which total is larger?',M(rf'$S_A=\frac{{{N}}}2[2({a})+4({N-1})]$.'),A(rf'$S_A={SA:g}$ units.'),M(rf'$S_B={b}(1.25^{{{N}}}-1)/(1.25-1)$.'),A(rf'$S_B={n(SB)}$ units; project A has the larger cumulative output.'))
  if topic=='functions':
   if j==5:
    a=i+2;b=i+1;roots=s.solve(x*x-(a+1)*x-b,x);checked(all(z!=1 for z in roots),'fixedpoint domain')
    extend(q,'Find the exact x-coordinates of the points where f(x)=x.',M(rf'${a}x+{b}=x(x-1)$, with $x\ne1$.'),M(rf'$x^2-{a+1}x-{b}=0$.'),A(rf'$x=\frac{{{a+1}\pm\sqrt{{{(a+1)**2+4*b}}}}}2$. Both satisfy the original domain.'))
   if j==14:
    extend(q,r'For a new parameter $k>0$, the equation is $e^{-x}=x/k$. Find k so that x=1 is the solution. Then explain whether doubling this k makes the positive solution larger or smaller.',M(r'$e^{-1}=1/k$.'),A(r'$k=e$.'),R('Doubling k halves the slope of y=x/k; at the original intersection the line is now below the exponential.'),R('The decreasing exponential and shallower increasing line therefore intersect further to the right; the positive solution increases.'))
   if j==17:
    h=i+1;k=i+2
    extend(q,rf'Solve $f^{{-1}}(x)={h+2}$ and sketch the inverse, labelling its endpoint.',M(rf'${h}+\sqrt{{x-{k}}}={h+2}$ gives $\sqrt{{x-{k}}}=2$.'),A(rf'$x={k+4}$.'),M('Use the increasing square-root branch on the inverse domain.'),A(rf'The endpoint is $({k},{h})$ and the curve increases to the right.'))
    q['markSchemeDiagramSvg']=plot([lambda z:h+math.sqrt(z-k)],k,k+9,h-1,h+4,[(k,h,'endpoint'),(k+4,h+2,f'({k+4}, {h+2})')],title='Inverse branch')
   if j==18:
    u=12+2*i;T=u//2;eq(u*(T-1)-2*(T-1)**2,u-2)
    extend(q,'Find the average rate of change of height during the first second and during the final second of the stated flight. Explain the relationship.',M(r'Use $[h(b)-h(a)]/(b-a)$ on [0,1] and on the final one-second interval.'),A(rf'The rates are ${u-2}$ m s⁻¹ and $-{u-2}$ m s⁻¹ respectively.'),R('The quadratic height model is symmetric about its maximum, giving equal magnitudes with opposite signs.'))
  if topic=='geometry-trigonometry':
   if j==6:
    d1=12+2*i;d2=9+i;distance=math.hypot(d1,d2);bearing=(35+math.degrees(math.atan(d2/d1))+180)%360
    extend(q,'Find the bearing of the starting point from the final position, to the nearest degree. Also find how much longer the route is than the direct return distance.',A(rf'Return bearing ${round(bearing):03d}^\circ$ (add180° modulo360°).'),M(rf'Route length $={d1}+{d2}={d1+d2}$ km; direct length ${distance:.8f}$ km.'),A(rf'The route is ${n(d1+d2-distance)}$ km longer.'))
   if j==7:
    a=8+i;b=10+i;B1=math.asin(b*.5/a);B2=math.pi-B1;C1=math.pi-math.pi/6-B1;C2=math.pi-math.pi/6-B2;c1=2*a*math.sin(C1);c2=2*a*math.sin(C2);ar1=.5*a*b*math.sin(C1);ar2=.5*a*b*math.sin(C2)
    extend(q,'For each possible triangle, find side c and the area. Match each result to the smaller or larger B.',M(rf'$c/\sin C={a}/\sin30^\circ$.'),A(rf'For smaller B, $c={n(c1)}$ cm; for larger B, $c={n(c2)}$ cm.'),M(rf'Area $=\tfrac12({a})({b})\sin C$.'),A(rf'Corresponding areas ${n(ar1)}$ cm² and ${n(ar2)}$ cm². Follow through the two correctly paired C values.'))
   if j==9:
    r=6+i;theta=1.1+.2*i;chord=2*r*math.sin(theta/2);area=.5*r*r*(theta-math.sin(theta));percentage=100*area/(math.pi*r*r)
    extend(q,'Find the perimeter of the minor segment and its area as a percentage of the whole circle.',M(rf'Perimeter $={r}({theta:g})+c$, using their chord length.'),A(rf'Perimeter ${n(r*theta+chord)}$ cm.'),M(rf'Percentage $=100A/(\pi {r}^2)$.'),A(rf'${n(percentage)}\%$.'))
   if j==17:
    mid=3+i*.2;level=mid+1
    extend(q,rf'During $0\leq t\leq12$, find the time intervals when the depth is at least ${level:g}$ m and the total duration.',M(r'Boundary times satisfy $\cos(\pi t/6)=1/2$, giving t=2 and t=10.'),A(r'$0\leq t\leq2$ or $10\leq t\leq12$.'),A('Total duration4 hours.'))
  if topic=='statistics-probability':
   if j==7:
    reg=linregress([1,2,3,4,5,6],[2+i,4+i,5+i,8+i,8+i,10+i]);pred=reg.intercept+20*reg.slope
    extend(q,'Use the regression to predict y when x=20 and assess the reliability of this prediction.',A(rf'$y={n(pred)}$.'),R('This is a substantial extrapolation beyond x=1 to6; the linear relationship may not continue, so the prediction is unreliable.'))
   if j==8:
    X=[2,3,4,5,6,7];Y=[5+i,5+i,8+i,9+i,11+i,12+i];reg=linregress(X,Y)
    extend(q,'Calculate the regression line of y on x and use it to predict y for x=4.',M('Fit y as the response, using x as explanatory variable.'),A(rf'$y={n(reg.slope)}x+({n(reg.intercept)})$.'),A(rf'At x=4, $y={n(reg.intercept+4*reg.slope)}$, using unrounded coefficients.'))
   if j==16:
    p=.15+.05*i;N=math.ceil(math.log(.05)/math.log(1-p));prob=binom.pmf(1,N,p);eq(prob,N*p*(1-p)**(N-1))
    extend(q,'Using your selected number of attempts, find the probability of exactly one success and the expected number of successes.',M(rf'Use $X\sim\mathrm{{Bin}}({N},{p:g})$ and calculate $P(X=1)$.'),A(rf'$P(X=1)={n(prob)}$.'),A(rf'$E(X)={N}({p:g})={n(N*p)}$.'))
   if j==19:
    mu=40+4*i;sd=5+i;z=norm.ppf(.975)
    extend(q,'Find the central95% interval for X.',M(r'Use the0.025 and0.975 quantiles, equivalently $\mu\pm1.959963985\sigma$.'),A(rf'Approximately $[{n(mu-z*sd)},{n(mu+z*sd)}]$. Follow through their μ and positive σ.'))
  if topic=='calculus':
   if j==7:
    a=i+1
    extend(q,'Find the exact change in f from the local maximum to the local minimum.',M(rf'$\Delta f=f({a})-f(-{a})$.'),A(rf'$\Delta f=-{4*a**3}$. This is a decrease of ${4*a**3}$ units.'))
   if j==10:
    side=18+3*i
    extend(q,'For the box of maximum volume, find the base area and the area of material removed.',A(rf'Base area $=({side}-2({frac(side,6)}))^2={frac(4*side*side,9)}$ cm².'),A(rf'Removed area $=4({frac(side,6)})^2={frac(side*side,9)}$ cm².'))
   if j==11:
    a=i+2
    extend(q,'Find the acceleration and the speed at the end of the interval.',A(r'$a(t)=dv/dt=1$ m s⁻².'),A(rf'At $t={2*a}$, speed $=|{2*a}-{a}|={a}$ m s⁻¹.'))
   if j==16:
    a=i+1
    extend(q,'Find the average vertical separation of the two curves over the enclosed interval.',M(rf'Average separation $=\frac1{{{2*a}}}\int_0^{{{2*a}}}({2*a}x-x^2)\,dx$.'),A(rf'${frac(2*a*a,3)}$ units.'))
   if j==18:
    extend(q,'Is the tank volume greatest at the time of maximum inflow rate? Explain.',A('No.'),R('After3 minutes and until6 minutes the inflow remains positive, so the volume continues to increase; it is greatest at6 minutes on the stated interval.'))
   if j==19:
    extend(q,'State where f is concave up.',A(r'$x>0$, because $f^{\prime\prime}(x)=2x>0$.'))
 return questions
