from aa_sl_core import *
def build():
 q=[]
 def add(j,i,title,sub,code,diff,calc,stem,ps,checks,**kw):q.append(rec('calculus','ca',j,i,title,sub,code,diff,calc,stem,ps,checks,**kw))
 for i in range(4):
  a=i+1;inputs=[a-.1,a-.01,a+.01,a+.1];outputs=[2*a-.1,2*a-.01,2*a+.01,2*a+.1]
  checked(outputs[0]<outputs[1]<2*a<outputs[2]<outputs[3],'two-sided trend')
  table='; '.join(f'x={u:.2f}, f(x)={v:.2f}' for u,v in zip(inputs,outputs))
  add(0,i,'Estimating a limit from nearby values','Numerical concept of a limit','5.1','easy',False,rf'A function has the following nearby values: {table}. Its graph follows the same trend closer to $x={a}$.',[
   part(rf'Estimate $\lim_{{x\to{a}}}f(x)$.',A(rf'${2*a}$.')),
   part(rf'Explain why the table alone does not determine $f({a})$.',R('None of the listed inputs equals the target input; a nearby trend does not specify the value assigned at that input.'))], 'Values approach same proposed limit from both sides; no formal limit manipulation or continuity test required.')
  a=i+2;f=a*x**3-4*x+s.Rational(2,1)/x;df=3*a*x*x-4-2/x**2;eq(s.diff(f,x),df)
  add(1,i,'A derivative with a reciprocal term','Power-rule differentiation','5.3','easy',False,rf'$f(x)={a}x^3-4x+\frac2x$, with $x\ne0$.',[
   part('Find f prime.',M(r'Write $2/x=2x^{-1}$ and apply the power rule term by term.'),A(rf'$f^\prime(x)={3*a}x^2-4-2x^{{-2}}$.')),
   part('Find the gradient at x=1.',A(rf'$f^\prime(1)={3*a-6}$.'))], 'Derivative checked symbolically and numerically with centered differences at an allowed input; pole excluded.')
  a=i+1;f=x*x+a*x+1;at=2;y=f.subs(x,at);m=s.diff(f,x).subs(x,at);eq(y,5+2*a)
  add(2,i,'A tangent at a specified point','Tangent equations','5.4','easy',False,rf'The curve is $y=x^2+{a}x+1$.',[
   part('Find the equation of its tangent at x=2.',M(rf'$dy/dx=2x+{a}$.'),A(rf'Tangent gradient ${m}$ and point $(2,{y})$.'),M(rf'$y-{y}={m}(x-2)$.'),A(rf'$y={m}x+({L(y-2*m)})$. Equivalent forms accepted.'))], 'Tangent line checked through the stated point with derivative-matched slope.')
  a=i+1;f=x**3+a*x;at=1;y=1+a;m=3+a;normal=-s.Rational(1,m)
  eq(m*normal,-1)
  add(3,i,'A normal and its intercept','Normal equations','5.4','medium',False,rf'The curve is $y=x^3+{a}x$.',[
   part('Find the normal at x=1.',M(rf'$dy/dx=3x^2+{a}$, so tangent gradient is ${m}$.'),A(rf'Normal gradient $=-{frac(1,m)}$.'),A(rf'$y-{y}=-{frac(1,m)}(x-1)$.')),
   part('Find where this normal meets the x-axis.',M(rf'Set $y=0$: $-{y}=-\frac{{x-1}}{{{m}}}$.'),A(rf'$({1+m*y},0)$.'))], 'Normal slope product−1 and line incidence checked; x-intercept substituted back in line.')
  a=i+1;f=s.exp(a*x*x+1);df=2*a*x*s.exp(a*x*x+1);eq(s.diff(f,x),df)
  add(4,i,'A nonlinear exponential composite','Increasing and decreasing functions','5.2','medium',False,rf'$f(x)=e^{{{a}x^2+1}}$.',[
   part('Differentiate f.',M(rf'The inner function ${a}x^2+1$ has derivative ${2*a}x$.'),A(rf'$f^\prime(x)={2*a}xe^{{{a}x^2+1}}$.')),
   part('Determine the intervals on which f decreases and increases.',R('The exponential factor is always positive, so the derivative has the sign of x.'),A(r'f decreases for x<0 and increases for x>0.'))], 'Symbolic chain-rule derivative verified; exponential positivity gives sign independently of numeric sampling.')
  a=i+2;f=x**a*s.log(x);df=a*x**(a-1)*s.log(x)+x**(a-1);eq(s.diff(f,x),df)
  add(5,i,'A power times a logarithm','Product rule','5.6','medium',False,rf'$f(x)=x^{{{a}}}\ln x$, for $x>0$.',[
   part('Find f prime in factorized form.',M(rf'Use product rule: ${a}x^{{{a-1}}}\ln x+x^{{{a}}}(1/x)$.'),A(rf'$f^\prime(x)=x^{{{a-1}}}({a}\ln x+1)$.')),
   part('Find the x-coordinate of the stationary point exactly.',M(rf'Since $x>0$, require ${a}\ln x+1=0$.'),A(rf'$x=e^{{-1/{a}}}$.'))], 'Product derivative checked symbolically; stationary solution substituted; x=0 is outside domain and not included.')
  a=i+1;f=x/(x*x+a);df=(a-x*x)/(x*x+a)**2;eq(s.diff(f,x),df)
  add(6,i,'A rational derivative','Quotient rule','5.6','medium',False,rf'$f(x)=\frac x{{x^2+{a}}}$.',[
   part('Differentiate f and simplify.',M(rf'$f^\prime(x)=\frac{{(x^2+{a})-x(2x)}}{{(x^2+{a})^2}}$.'),A(rf'$f^\prime(x)=\frac{{{a}-x^2}}{{(x^2+{a})^2}}$.')),
   part('State the interval on which f is increasing.',R('The denominator is strictly positive, so increasing requires a positive numerator.'),A(rf'$-\sqrt{{{a}}}<x<\sqrt{{{a}}}$.'))], 'Quotient derivative verified algebraically; denominator never zero; sign chart checked.')
  a=i+1;f=x**3-3*a*a*x;df=s.diff(f,x);d2=s.diff(f,x,2);eq(df,3*(x-a)*(x+a))
  add(7,i,'Classifying two stationary points','Local extrema','5.8','hard',False,rf'$f(x)=x^3-{3*a*a}x$.',[
   part('Find and classify both stationary points.',M(rf'$f^\prime(x)=3x^2-{3*a*a}=0$.'),A(rf'$x=-{a}$ or $x={a}$.'),M(r'$f^{\prime\prime}(x)=6x$; evaluate at each stationary input.'),A(rf'Local maximum $(-{a},{2*a**3})$ and local minimum $({a},-{2*a**3})$.')),
   part('State where f is decreasing.',R('The derivative is negative between its two roots.'),A(rf'$-{a}<x<{a}$.'))], 'Critical points and ordinates substituted; second derivative signs and full first-derivative sign chart agree.',answer_diagram=plot([s.lambdify(x,f,'math')],-2*a,2*a,-3*a**3,3*a**3,[(-a,2*a**3,'local maximum'),(a,-2*a**3,'local minimum')],title='Stationary-point sketch'))
  h=i+1;f=(x-h)**3+2*x;df=s.diff(f,x);d2=s.diff(f,x,2);eq(d2,6*(x-h))
  add(8,i,'An inflexion without a stationary point','Concavity and inflexion','5.8','medium',False,rf'$f(x)=(x-{h})^3+2x$.',[
   part('Find the point of inflexion and justify your answer.',M(rf'$f^{{\prime\prime}}(x)=6(x-{h})$.'),A(rf'Candidate point $({h},{2*h})$.'),R(rf'The second derivative changes from negative to positive at $x={h}$, so concavity changes there.')),
   part('Explain why this point is not stationary.',A(rf'$f^\prime({h})=2\ne0$.'))], 'Second derivative changes sign at candidate; nonzero first derivative confirms nonstationary inflexion.')
  P=40+8*i;side=P/4;maxarea=side*side;eq(s.diff(x*(P/2-x),x).subs(x,side),0)
  add(9,i,'Maximizing an enclosure','Area optimization','5.8','medium',False,rf'A rectangular enclosure uses ${P}$ m of fencing for all four sides. Let one side be x metres.',[
   part('Write the area A in terms of x and state the physical domain.',M(rf'The other side is ${P//2}-x$.'),A(rf'$A=x({P//2}-x)$, for $0<x<{P//2}$.')),
   part('Find the greatest possible area and justify that it is a maximum.',M(rf'$A^\prime={P//2}-2x=0$ gives $x={side:g}$.'),A(rf'The other side is also ${side:g}$ m, giving ${maxarea:g}$ m².'),R(r'$A^{\prime\prime}=-2<0$ throughout the domain, so this is the global maximum of the concave quadratic.'))], 'Area optimization checked via completed square and derivative; physical lengths positive.')
  side=18+3*i;f=x*(side-2*x)**2;root=s.Rational(side,6);V=f.subs(x,root);eq(s.diff(f,x).subs(x,root),0)
  add(10,i,'An open box cut from a square','Volume optimization','5.8','hard',False,rf'Squares of side x cm are cut from the corners of a square sheet of side ${side}$ cm. The sides are folded to make an open box.',[
   part('Write the box volume V(x) and its physical domain.',A(rf'$V=x({side}-2x)^2$ cm³.'),A(rf'$0<x<{frac(side,2)}$.')),
   part('Find the value of x maximizing the volume, and the maximum volume.',M(rf'$V^\prime=({side}-2x)({side}-6x)$.'),A(rf'The interior stationary input is $x={L(root)}$ cm; $x={frac(side,2)}$ is a degenerate endpoint.'),R(rf'$V^\prime$ changes from positive to negative at $x={L(root)}$; volume tends to0 at both physical boundaries.'),A(rf'Maximum volume ${L(V)}$ cm³.'))], 'Factored derivative and physical endpoint zeros checked; maximum independently agrees with numeric optimization.')
  a=i+2;v=t-a;F=t*t/2-a*t;end=2*a;disp=s.integrate(v,(t,0,end));distance=a*a;eq(disp,0);eq(s.integrate(-v,(t,0,a))+s.integrate(v,(t,a,end)),distance)
  add(11,i,'Distance despite zero displacement','Kinematics and signed velocity','5.9','hard',False,rf'A particle has velocity $v(t)=t-{a}$ m s⁻¹ for $0\leq t\leq{end}$ seconds.',[
   part('Find when the particle changes direction.',M(rf'$v(t)=0$ at $t={a}$.'),R('Velocity is negative before this time and positive afterwards, so direction changes.')),
   part('Find the displacement and total distance travelled over the interval.',M(rf'Displacement $=\int_0^{{{end}}}(t-{a})\,dt$.'),A(r'Displacement0 m.'),M(rf'Distance $=-\int_0^{{{a}}}(t-{a})\,dt+\int_{{{a}}}^{{{end}}}(t-{a})\,dt$.'),A(rf'Total distance ${distance}$ m.'))], 'Signed and absolute velocity integrals evaluated independently; zero velocity sign change distinguishes direction reversal.')
  a=i+1;derivative=3*x*x+2*a*x-4;f=x**3+a*x*x-4*x+7;eq(s.diff(f,x),derivative);eq(f.subs(x,0),7)
  add(12,i,'Recovering a function from its gradient','Antiderivative with a condition','5.5','easy',False,rf'$f^\prime(x)=3x^2+{2*a}x-4$ and $f(0)=7$.',[
   part('Find f(x).',M(r'Integrate each term and include a constant C.'),A(rf'$f(x)=x^3+{a}x^2-4x+C$.'),M(r'$f(0)=7$ implies $C=7$.'),A(rf'$f(x)=x^3+{a}x^2-4x+7$.'))], 'Proposed function differentiated to recover every derivative term and checked at boundary condition.')
  a=i+1;integrand=2*a*s.cos(2*a*x)+3*s.exp(3*x);anti=s.sin(2*a*x)+s.exp(3*x);eq(s.diff(anti,x),integrand)
  add(13,i,'Integrating two linear composites','Elementary integration','5.10','medium',False,rf'Find $\int\left({2*a}\cos({2*a}x)+3e^{{3x}}\right)\,dx$.',[
   part('Give the general antiderivative.',M(rf'Account for inner derivative ${2*a}$ when integrating cosine.'),A(rf'Cosine term integrates to $\sin({2*a}x)$.'),A(r'Exponential term integrates to $e^{3x}$.'),A(r'Include the arbitrary additive constant $+C$ with the sum of the two antiderivative terms.')),
   part('Explain why an arbitrary constant is required.',R('Any two antiderivatives differing by a constant have the same derivative.'))], 'Each antiderivative term independently differentiated; constant included exactly once in full answer.')
  a=i+1;integrand=2*x*(x*x+a)**3;anti=(x*x+a)**4/4;result=((1+a)**4-a**4)/4;eq(s.diff(anti,x),integrand);eq(s.integrate(integrand,(x,0,1)),s.Rational((1+a)**4-a**4,4))
  add(14,i,'A reverse-chain-rule integral','Integration by substitution','5.10','medium',False,rf'Evaluate $\int_0^1 2x(x^2+{a})^3\,dx$.',[
   part('Give the exact value, showing your method.',M(rf'Let $u=x^2+{a}$, so $du=2x\,dx$.'),A(rf'Bounds become $u={a}$ and $u={a+1}$.'),M(rf'$\int_{{{a}}}^{{{a+1}}}u^3du=[u^4/4]_{{{a}}}^{{{a+1}}}$.'),A(rf'${frac((1+a)**4-a**4,4)}$.'))], 'Substitution boundaries checked; exact result agrees with direct polynomial integration.')
  a=i+1;f=x-a;left=0;right=3*a;area=s.Rational(5,2)*a*a;signed=s.Rational(3,2)*a*a
  eq(s.integrate(-f,(x,0,a))+s.integrate(f,(x,a,right)),area)
  add(15,i,'Area across an axis crossing','Signed integrals and area','5.11','medium',False,rf'The line is $y=x-{a}$ on $0\leq x\leq{right}$.',[
   part('Find the total area enclosed by the line, x-axis and the two endpoint vertical lines.',M(rf'The line crosses at $x={a}$, so split the area there.'),M(rf'$A=-\int_0^{{{a}}}(x-{a})\,dx+\int_{{{a}}}^{{{right}}}(x-{a})\,dx$.'),A(rf'$A={L(area)}$ square units.')),
   part('Explain why the single signed integral gives a smaller result.',R('The integral counts the region below the x-axis negatively, whereas total area counts both regions positively.'),A(rf'The signed integral is ${L(signed)}$.'))], 'Area checked as sum of two triangle areas; signed integral differs by twice the negative-region area.',diagram=plot([lambda z:z-a],0,right,-a-1,2*a+1,[(a,0,f'({a}, 0)')],title='Line crossing the x-axis'))
  a=i+1;upper=2*a*x;lower=x*x;end=2*a;area=s.Rational(4,3)*a**3;eq(s.integrate(upper-lower,(x,0,end)),area)
  add(16,i,'An enclosed region between two curves','Areas between curves','5.11','hard',False,rf'The curves are $y={2*a}x$ and $y=x^2$.',[
   part('Find their intersection points.',M(rf'$x^2={2*a}x$ gives $x(x-{2*a})=0$.'),A(rf'$(0,0)$ and $({2*a},{4*a*a})$.')),
   part('Find the exact area enclosed by the two curves.',R(rf'The line is above the parabola for $0<x<{2*a}$.'),M(rf'$A=\int_0^{{{2*a}}}({2*a}x-x^2)\,dx$.'),A(rf'Antiderivative ${a}x^2-x^3/3$.'),A(rf'$A={L(area)}$ square units.'))], 'Intersections substituted in both curves; exact integral checked by numerical quadrature and positive-integrand sign.',diagram=plot([lambda z:2*a*z,lambda z:z*z],0,2*a,0,4*a*a+1,title='Line and parabola'))
  a=i+1;fun=lambda z:math.exp(-a*z*z);value=quad(fun,0,2)[0];eq(value,quad(lambda u:math.exp(-u*u),0,2*math.sqrt(a))[0]/math.sqrt(a))
  add(17,i,'A numerically evaluated area','Technology definite integration','5.5','medium',True,rf'A region is bounded by $y=e^{{-{a}x^2}}$, the x-axis, $x=0$ and $x=2$.',[
   part('Write an integral for its area and evaluate it to three significant figures.',M(rf'$A=\int_0^2 e^{{-{a}x^2}}\,dx$.'),M('Use numerical definite integration with lower bound0 and upper bound2.'),A(rf'$A={n(value)}$ square units.')),
   part('Explain why the area is positive and less than2.',R('For0<x≤2, the function lies strictly between0 and1, so the region lies inside the2-by-1 rectangle and has positive area.'))], 'Quadrature cross-checked after variable rescaling; area bounds verified without requiring a non-syllabus antiderivative.')
  a=3+i;P=100+20*i;rate=a*t*(6-t);acc=s.diff(rate,t);total=s.integrate(rate,(t,0,6));eq(acc.subs(t,3),0)
  add(18,i,'A changing inflow rate','Rate and accumulation','5.9','hard',False,rf'A tank initially contains ${P}$ litres. Water flows in at $R(t)={a}t(6-t)$ litres per minute for $0\leq t\leq6$. No water leaves.',[
   part('Find the time of maximum inflow rate and the maximum rate.',M(rf'$R^\prime(t)={6*a}-{2*a}t=0$.'),A(rf'$t=3$ minutes, maximum rate ${9*a}$ L min⁻¹.'),R(rf'$R^{{\prime\prime}}=-{2*a}<0$, and endpoint rates are0.')),
   part('Find the volume in the tank after6 minutes.',M(rf'$V(6)={P}+\int_0^6{a}t(6-t)\,dt$.'),A(rf'Integral is ${L(total)}$ litres.'),A(rf'Final volume ${L(P+total)}$ litres.'))], 'Rate maximum verified by concave quadratic; accumulated volume checked via exact integration and numerical quadrature; initial amount added once.')
  a=i+1;d=x*x-a*a;F=x**3/3-a*a*x;eq(s.diff(F,x),d)
  add(19,i,'Reading information from a derivative graph','Graphs of f and its derivatives','5.7','hard',False,rf'The graph shown is $y=f^\prime(x)=x^2-{a*a}$.',[
   part('State the x-coordinates of the local maximum and minimum of f, justifying each.',R(rf'At $x=-{a}$, $f^\prime$ changes from positive to negative.'),A(rf'f has a local maximum at $x=-{a}$.'),R(rf'At $x={a}$, $f^\prime$ changes from negative to positive.'),A(rf'f has a local minimum at $x={a}$.')),
   part('Find the x-coordinate of the point of inflexion of f.',M(r'$f^{\prime\prime}(x)=2x$ changes sign at0.'),A(r'$x=0$.')),
   part('Explain why the graph alone does not determine the y-coordinates of these points on f.',R('Adding any constant to f leaves its derivative unchanged, so the vertical position of f is not specified.'))], 'First-derivative sign chart and second-derivative sign change checked; derivative ordinate is not mistaken for f ordinate.',diagram=plot([lambda z:z*z-a*a],-2*a,2*a,-a*a-1,2*a*a+1,[(-a,0,f'(-{a}, 0)'),(a,0,f'({a}, 0)')],title="Graph of f′, not f"))
 return sorted(q,key=lambda z:z['number'])
if __name__=='__main__':save('calculus',build())
