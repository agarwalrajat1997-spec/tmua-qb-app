from aa_sl_core import *
def build():
 q=[]
 def add(j,i,title,sub,code,diff,calc,stem,ps,checks,**kw):q.append(rec('functions','fn',j,i,title,sub,code,diff,calc,stem,ps,checks,**kw))
 for i in range(4):
  m=i+2;c=3-i;xa=-1;xb=3;ya=m*xa+c;yb=m*xb+c;eq((yb-ya)/(xb-xa),m)
  add(0,i,'Reconstructing a straight line','Straight-line equations','2.1','easy',False,rf'A line passes through $A(-1,{ya})$ and $B(3,{yb})$.',[
   part('Find the equation of the line.',M(rf'$m=({yb}-({ya}))/(3-(-1))={m}$.'),M(rf'$y-{ya}={m}(x+1)$.'),A(rf'$y={m}x+{c}$.')),
   part('Find its x-intercept.',A(rf'$(-{frac(c,m)},0)$.' if c>0 else rf'$({frac(-c,m)},0)$.'))], 'Both point coordinates substituted in line; x-intercept checked by y=0.')
  k=i+1;A0=(0,0);B=(4,4*k);mid=(2,2*k);slope=-s.Rational(1,k)
  eq(slope*k,-1)
  add(1,i,'A perpendicular bisector','Perpendicular lines','2.1','medium',False,rf'The points A and B are $(0,0)$ and $(4,{4*k})$.',[
   part('Find the midpoint of AB.',A(rf'$M=(2,{2*k})$.')),
   part('Find the perpendicular bisector of AB.',M(rf'Gradient of AB is ${k}$, so the perpendicular gradient is $-{frac(1,k)}$.'),M(rf'The line passes through $(2,{2*k})$.'),A(rf'$y-{2*k}=-{frac(1,k)}(x-2)$. Equivalent forms accepted.'))], 'Midpoint averaged componentwise; product of perpendicular gradients equals -1; resulting line passes through midpoint.')
  a=i+1;b=i+4
  add(2,i,'Domain of a combined expression','Domain and function notation','2.2','medium',False,rf'Let $f(x)=\frac{{\sqrt{{x-{a}}}}}{{x-{b}}}$.',[
   part('State the largest real domain of f.',M(rf'Require $x-{a}\geq0$ and $x-{b}\ne0$.'),A(rf'$[{a},{b})\cup({b},\infty)$.')),
   part(rf'Find $f({a})$ and explain why $f({b})$ does not exist.',A(rf'$f({a})=0$.'),R(rf'At $x={b}$ the denominator is zero, so the expression is undefined.'))], 'Square-root radicand and denominator restrictions checked independently; included lower endpoint evaluated.')
  h=i+1;k=2-i;end=h+3
  eq((end-h)**2+k,9+k)
  add(3,i,'Range on a restricted domain','Quadratic domain and range','2.2','easy',False,rf'$f(x)=(x-{h})^2+({k})$ for ${h}\leq x\leq{end}$.',[
   part('State the range of f.',M(rf'On this domain, $0\leq(x-{h})^2\leq9$.'),A(rf'$[{k},{k+9}]$.')),
   part('Explain whether f has an inverse on this domain.',R('Yes: f is strictly increasing on the stated interval, so each output comes from exactly one input.'))], 'Endpoint outputs and monotonicity on the right-hand branch checked; range closed at both ends.')
  a=i+2;b=3;f=a*x-b;g=x*x+1;comp=s.expand(f.subs(x,g));rev=s.expand(g.subs(x,f));checked(s.expand(comp-rev)!=0,'noncommutation')
  add(4,i,'Order of composition','Composite functions','2.5','easy',False,rf'Let $f(x)={a}x-3$ and $g(x)=x^2+1$.',[
   part('Find (f∘g)(x).',M(rf'$f(g(x))={a}(x^2+1)-3$.'),A(rf'${L(comp)}$.')),
   part('Find (g∘f)(x), and show that the two compositions are different.',A(rf'$g(f(x))=({a}x-3)^2+1$.'),R(rf'At $x=0$, $f(g(0))={a-3}$ whereas $g(f(0))=10$; hence they differ.'))], 'Both compositions checked by symbolic substitution and at x=0; composition order explicit.')
  a=i+2;b=i+1;inv=(b+x)/(x-a);f=(a*x+b)/(x-1);eq(s.cancel(f.subs(x,inv)),x)
  add(5,i,'Inverse of a rational function','Inverse functions','2.5','hard',False,rf'$f(x)=\frac{{{a}x+{b}}}{{x-1}}$, with $x\ne1$.',[
   part('Find the range of f.',M(rf'$f(x)={a}+\frac{{{a+b}}}{{x-1}}$, whose second term is never zero.'),A(rf'The range is $\mathbb R\setminus\{{{a}\}}$.')),
   part('Find f inverse and its domain.',M(rf'From $y(x-1)={a}x+{b}$, obtain $x(y-{a})=y+{b}$.'),A(rf'$f^{{-1}}(x)=\frac{{x+{b}}}{{x-{a}}}$.'),A(rf'Its domain is $x\ne{a}$.'))], 'Inverse composition simplifies to x; forbidden values checked and domain/range interchanged.')
  h=i+1;k=3+i;expr=s.expand((x-h)**2-k);eq(expr,(x-h)**2-k)
  add(6,i,'Completing the square','Quadratic vertex form','2.6','easy',False,rf'Let $f(x)={L(expr)}$.',[
   part('Express f in completed-square form.',M(rf'Group $x^2-{2*h}x=(x-{h})^2-{h*h}$.'),A(rf'$f(x)=(x-{h})^2-{k}$.')),
   part('State the vertex and axis of symmetry.',A(rf'Vertex $({h},-{k})$; axis $x={h}$.'))], 'Expansion of vertex form checked symbolically; minimum value and axis verified.')
  a=i+1;b=a+3;expr=s.expand((x-a)*(x-b))
  add(7,i,'A quadratic inequality','Quadratic equations and inequalities','2.7','medium',False,rf'Solve ${L(expr)}\leq0$.',[
   part('Give the full solution set.',M(rf'Factor to $(x-{a})(x-{b})\leq0$.'),R('The upward-opening quadratic is non-positive between its roots, including the roots.'),A(rf'${a}\leq x\leq {b}$.'))], 'Roots substituted and signs sampled in all three intervals; inclusive inequality retains both roots.')
  b=4+2*i;bound=s.Rational(b*b,4)
  add(8,i,'When a quadratic has no real roots','Discriminant','2.7','medium',False,rf'The equation $x^2-{b}x+k=0$ has no real solutions.',[
   part('Find the possible values of k.',M(rf'The discriminant is ${b*b}-4k$.'),R('No real roots requires a strictly negative discriminant.'),A(rf'$k>{L(bound)}$.')),
   part(rf'Describe the roots when $k={L(bound)}$.',A(rf'A repeated real root $x={b//2}$.'))], 'Discriminant and completed-square minimum agree; strict versus equality boundary reviewed.')
  k=i+1;poly=x*x;linear=2*k*x+3*k*k;roots=[-k,3*k];eq(poly.subs(x,-k),linear.subs(x,-k));eq(poly.subs(x,3*k),linear.subs(x,3*k))
  add(9,i,'Intersections of a curve and line','Graphical and algebraic intersections','2.10','medium',False,rf'The curve is $y=x^2$ and the line is $y={2*k}x+{3*k*k}$.',[
   part('Find both points of intersection.',M(rf'$x^2-{2*k}x-{3*k*k}=0$.'),M(rf'$(x+{k})(x-{3*k})=0$.'),A(rf'$(-{k},{k*k})$ and $({3*k},{9*k*k})$.')),
   part('State where the curve lies below the line.',A(rf'$-{k}<x<{3*k}$.'))], 'Both coordinates substituted into original equations; strict below-line interval checked by sign.')
  h=i+1;k=1-i;f=lambda z:2/(z-h)+k
  add(10,i,'Sketching a translated reciprocal','Key features and sketches of graphs','2.4','medium',False,rf'Let $f(x)=\frac2{{x-{h}}}+({k})$.',[
   part('State both asymptotes.',A(rf'$x={h}$ and $y={k}$.')),
   part('Sketch the graph, labelling both asymptotes and one point on each branch.',M(rf'Use the two reciprocal branches with centre $({h},{k})$.'),A(rf'For example, $({h-1},{k-2})$ and $({h+1},{k+2})$ are correctly placed.'),A('The right branch is above the horizontal asymptote, the left below it, and both approach the correct asymptotes.'))], 'Plotted coordinates calculated from exact function; branches separated at pole; solution graph generated.',answer_diagram=plot([f],-4,8,-6,7,[(h-1,k-2,f'({h-1}, {k-2})'),(h+1,k+2,f'({h+1}, {k+2})')],[h],[k],'Solution sketch'))
  a=i+2;b=2*i+1;constant=a+b
  add(11,i,'Reading a rational asymptote','Rational function structure','2.8','medium',False,rf'$g(x)=\frac{{{a}x+{b}}}{{x-1}}$.',[
   part(rf'Show that $g(x)={a}+\frac{{{constant}}}{{x-1}}$.',M(rf'Write numerator as ${a}(x-1)+{constant}$.'),R('Dividing by x−1 gives the required identity for x≠1.')),
   part('Find the intercepts and asymptotes.',A(rf'x-intercept $(-{frac(b,a)},0)$; y-intercept $(0,-{b})$.'),A(rf'Asymptotes $x=1$ and $y={a}$.'))], 'Polynomial division identity and both intercepts checked by substitution; numerator nonzero at excluded pole.')
  a=80+20*i;r=1.18+.02*i;after=a*r**5;time=math.log(2)/math.log(r)
  eq(a*math.exp(math.log(r)*5),after)
  add(12,i,'A growing membership model','Exponential functions and modelling','2.9','medium',True,rf'A club models its membership by $N(t)={a}({r:g})^t$, where t is years after opening.',[
   part('Interpret the two constants in the model.',A(rf'Initial membership is ${a}$.'),A(rf'Membership increases by ${(r-1)*100:.0f}\%$ each year.')),
   part('Find the predicted membership after five years, to the nearest whole person.',M(rf'$N(5)={a}({r:g})^5$.'),A(rf'${round(after)}$ people.')),
   part('Find the time at which the model predicts twice the initial membership.',M(rf'$({r:g})^t=2$.'),A(rf'$t=\ln2/\ln({r:g})={n(time)}$ years.'))], 'Exponential and exp-log forms cross-checked; membership rounding separated from unrounded doubling time.')
  h=i+1;k=i-1;f=lambda z:math.log(z-h)+k
  add(13,i,'Sketching a logarithmic transformation','Logarithmic functions','2.9','medium',False,rf'Let $f(x)=\ln(x-{h})+({k})$.',[
   part('State its domain, range and vertical asymptote.',A(rf'Domain $x>{h}$; range $\mathbb R$.'),A(rf'Vertical asymptote $x={h}$.')),
   part('Sketch f, labelling the point where the logarithm argument equals 1.',M('Use an increasing logarithmic curve entirely to the right of the vertical asymptote.'),A(rf'Label $({h+1},{k})$ and approach the asymptote downwards.'))], 'Domain from positive log argument; labelled point evaluated exactly; solution SVG samples function on valid domain only.',answer_diagram=plot([f],-1,8,-5,5,[(h+1,k,f'({h+1}, {k})')],[h],title='Solution sketch'))
  a=i+1;root=brentq(lambda z:math.exp(-z)-z/a,.01,5)
  eq(math.exp(-root),root/a)
  add(14,i,'A graphical solution without a closed form','Technology equation solving','2.10','hard',True,rf'Consider the equation $e^{{-x}}=x/{a}$ for $x>0$.',[
   part('Find the solution to three significant figures, stating the graphs you use.',M(rf'Graph $y=e^{{-x}}$ and $y=x/{a}$ and find their intersection.'),A(rf'$x={n(root)}$.')),
   part('Explain why there is only one positive solution.',R('For x>0, the exponential decreases strictly and the straight line increases strictly.'),R('At x=0 the exponential is larger; for sufficiently large x the line is larger, so exactly one intersection occurs.'))], 'Root obtained by bracketed numerical solver and original residual checked below 1e-8; monotonicity gives uniqueness.')
  a=i+2;b=i+4;poly=(s.exp(x)-a)*(s.exp(x)-b)
  add(15,i,'A quadratic in an exponential','Analytic exponential equations','2.10','hard',False,rf'Solve $e^{{2x}}-{a+b}e^x+{a*b}=0$.',[
   part('Find every real solution exactly.',M(r'Let $u=e^x>0$.'),A(rf'$u^2-{a+b}u+{a*b}=(u-{a})(u-{b})$.'),M(rf'$e^x={a}$ or $e^x={b}$.'),A(rf'$x=\ln {a}$ or $x=\ln {b}$.'))], 'Both positive exponential roots and their logarithms substituted symbolically; quadratic has no additional roots.')
  a=i+2;px=3;py=5;xx=px+a;yy=-2*py+1
  eq(xx-a,px)
  add(16,i,'Tracking a point under transformations','Graph transformations','2.11','medium',False,rf'The point P(3,5) lies on $y=f(x)$. Define $g(x)=-2f(x-{a})+1$.',[
   part('Find the corresponding point on the graph of g.',M(rf'Set $x-{a}=3$.'),A(rf'$x={L(xx)}$.'),M(r'$y=-2(5)+1$.'),A(rf'The point is $({L(xx)},-9)$.')),
   part('Describe the vertical transformations.',A('Reflection in the x-axis and vertical stretch of factor 2, followed by translation 1 unit upwards.'))], 'New input maps back exactly to original input; output transformation applied in stated order.')
  h=i+1;k=2+i
  add(17,i,'Choosing a branch for an inverse','Restricted quadratic inverse','2.5','hard',False,rf'$f(x)=(x-{h})^2+{k}$ is defined for $x\geq{h}$.',[
   part('Find f inverse, including its domain and range.',M(rf'From $y-{k}=(x-{h})^2$, use $x-{h}\geq0$.'),A(rf'$f^{{-1}}(x)={h}+\sqrt{{x-{k}}}$.'),A(rf'Domain $x\geq{k}$ and range $y\geq{h}$.')),
   part('Explain how the two graphs are related.',R('They are reflections of each other in the line y=x; the domain and range swap.'))], 'Positive square-root branch enforced by original restriction; inverse composition and endpoints checked.')
  u=12+2*i;g=2;T=u/2;H=u*u/8
  eq(u*T-2*T*T,0)
  add(18,i,'Height from a quadratic model','Quadratic modelling','2.6','hard',False,rf'A model for a ball height is $h(t)={u}t-2t^2$ metres, where t is seconds and $0\leq t\leq {T:g}$.',[
   part('Find the greatest height and the time at which it occurs using completed-square form.',M(rf'$h(t)=-2(t-{u/4:g})^2+{H:g}$.'),A(rf'The maximum is ${H:g}$ m at $t={u/4:g}$ s.')),
   part('Find the time interval during which the ball is above half its maximum height.',M(rf'$(t-{u/4:g})^2<{H/4:g}$.'),A(rf'${frac(u,4)}-\frac{{{u}\sqrt2}}{{8}}<t<{frac(u,4)}+\frac{{{u}\sqrt2}}{{8}}$ seconds.'),R('Both boundary times lie in the physical domain; the strict inequality excludes the boundary times.'))], 'Vertex checked algebraically; half-height roots substituted and confirmed inside stated flight domain.')
  f=lambda z:(i+1)*z+3 if z<=4 else 4*(i+1)+3+2*(z-4)
  total=f(7);eq(f(4),4*(i+1)+3)
  add(19,i,'A two-stage delivery charge','Piecewise graph interpretation','2.3','medium',False,rf'A delivery costs USD 3 plus USD ${i+1}$ per km for the first 4 km, then USD 2 per additional km. Distance d may be any real number with $d\geq0$.',[
   part('Write a piecewise function C(d) for the charge.',A(rf'$C(d)=3+{i+1}d$ for $0\leq d\leq4$.'),A(rf'$C(d)={4*(i+1)+3}+2(d-4)$ for $d>4$.')),
   part('Find the cost for a 7 km delivery and explain what happens to the graph at d=4.',A(rf'USD ${total}$.'),R(rf'The pieces meet at $(4,{4*(i+1)+3})$; there is no jump because the second rule includes the full charge for the first 4 km.'))], 'Piecewise rules checked at join and 7 km; endpoints and charge units explicit.')
 return sorted(q,key=lambda z:z['number'])
if __name__=='__main__':save('functions',build())
