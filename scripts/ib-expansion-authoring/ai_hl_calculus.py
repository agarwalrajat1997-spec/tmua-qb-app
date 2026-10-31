from ai_hl_common import *
def euler(f,x0,y0,h,n):
 x=x0;y=y0;rows=[]
 for j in range(n):
  slope=f(x,y);yn=y+h*slope;rows.append([x,y,slope,yn]);x+=h;y=yn
 return y,rows
def coupled(f,g,x0,y0,h,n):
 x=x0;y=y0;rows=[]
 for j in range(n):
  dx=f(x,y);dy=g(x,y);xn=x+h*dx;yn=y+h*dy;rows.append([j*h,x,y,xn,yn]);x,y=xn,yn
 return x,y,rows
def build():
 for v in range(4):
  k=.3+.05*v;a=4+v;t=2;f=lambda x:a*x*math.exp(-k*x);df=lambda x:a*math.exp(-k*x)*(1-k*x)
  add('ca',1,v,'A transient treatment response','Product rule and tangent','5.9',f'A treatment response is $R(t)={a}te^{{-{k:g}t}}$ for $t\\geq0$.',[
   P('Differentiate R and calculate the rate at $t=2$.',M('Apply the product rule, differentiating both factors.'),A(f'$R^\\prime(t)={a}e^{{-{k:g}t}}(1-{k:g}t)$.'),A(f'$R^\\prime(2)={sf(df(2))}$ response units per time unit.')),
   P('Find the tangent equation at $t=2$.',M('Use point-slope form at $(2,R(2))$.'),A(f'$R-{sf(f(2))}={sf(df(2))}(t-2)$, using unrounded coefficients.')),
   P('Find when the response changes from increasing to decreasing.',M('Solve $1-kt=0$; the exponential factor is positive.'),A(f'$t={sf(1/k)}$.'),R('The derivative is positive before this time and negative after it.'))],{'valueAt2':f(2),'rateAt2':df(2),'maximumTime':1/k})
  a=10+v;b=2+v;x=3;f=lambda x:a*x/(b+x);df=lambda x:a*b/(b+x)**2
  add('ca',2,v,'Marginal response near saturation','Quotient rule','5.9',f'A concentration response is $f(x)={a}x/({b}+x)$ for $x\\geq0$.',[
   P('Find $f^\\prime(x)$ and $f^\\prime(3)$.',M('Apply the quotient rule.'),A(f'$f^\\prime(x)={a*b}/({b}+x)^2$.'),A(f'$f^\\prime(3)={sf(df(3))}$.')),
   P('Use a tangent approximation at 3 to estimate $f(3.1)$.',M('Use $f(3)+0.1f^\\prime(3)$.'),A(f'Estimate {sf(f(3)+.1*df(3))}.')),
   P('Determine whether this tangent estimate is above or below the exact value.',M(f'$f^{{\\prime\\prime}}(x)=-{2*a*b}/({b}+x)^3<0$ on the contextual domain.'),R('The graph is concave down, so the tangent estimate is above the exact value.'))],{'derivativeAt3':df(3),'tangentEstimate3p1':f(3)+.1*df(3),'exact3p1':f(3.1)})
  a=2+v;x=1;der=2*a/(a+1)
  add('ca',3,v,'Logarithmic composite index','Chain rule and logarithmic derivative','5.9',f'An index is $I(x)=\\ln({a}x^2+1)$ for all real $x$.',[
   P('Find the derivative and the tangent gradient at $x=1$.',M('Apply the chain rule to the logarithm.'),A(f'$I^\\prime(x)={2*a}x/({a}x^2+1)$.'),A(f'Gradient {sf(der)}.')),
   P('Find all stationary points and classify them using the derivative sign.',M('The denominator is positive; the derivative vanishes only at $x=0$.'),A('The stationary point is $(0,0)$.'),R('The derivative changes from negative to positive, so it is a minimum.')),
   P('State why there is no logarithm-domain restriction on real x.',R(f'The argument ${a}x^2+1$ is at least 1 and hence always positive.'))],{'gradientAt1':der})
  r=3+.5*v;rate=2+.2*v;dr=rate/(4*math.pi*r*r);dA=8*math.pi*r*dr
  add('ca',4,v,'Inflating a spherical balloon','Related rates for volume and area','5.9',f'A spherical balloon has volume $V=4\\pi r^3/3$ and area $A=4\\pi r^2$. Air enters at {rate:g} cubic centimetres per second. Consider the instant when $r={r:g}$ cm.',[
   P('Find the rate of increase of radius.',M('Differentiate volume with respect to time: $dV/dt=4\\pi r^2\\,dr/dt$.'),M('Substitute the given volume rate and radius.'),A(f'$dr/dt={sf(dr)}$ cm per second.')),
   P('Find the rate of increase of surface area.',M('$dA/dt=8\\pi r\\,dr/dt$.'),A(f'$dA/dt={sf(dA)}$ square centimetres per second.')),
   P('Explain how the radius growth rate changes as the balloon enlarges at the same volume inflow.',R('The radius rate is inversely proportional to $r^2$.'),R('It decreases as the balloon grows.'),R('The assumption of constant inflow must remain valid.'))],{'radiusRate':dr,'areaRate':dA})
  L=10+v;x=6;y=math.sqrt(L*L-x*x);dx=.4+.05*v;dy=-x*dx/y
  add('ca',5,v,'A sliding inspection ladder','Implicit related rates','5.9',f'A ladder of length {L} m leans against a vertical wall. Its foot is moving horizontally away at {dx:g} m per second. At the instant considered the foot is 6 m from the wall.',[
   P('Find the height of the top and its vertical velocity.',A(f'Height $y=\\sqrt{{{L*L}-36}}={sf(y)}$ m.'),M('Differentiate $x^2+y^2=L^2$ with respect to time.'),A('$x\\,dx/dt+y\\,dy/dt=0$.'),A(f'$dy/dt={sf(dy)}$ m per second.')),
   P('Explain the sign of your answer and find the rate at which the enclosed triangular area changes.',R('The negative sign means the top is descending.'),M('$d(xy/2)/dt=(y\\,dx/dt+x\\,dy/dt)/2$.'),A(f'Area rate {sf((y*dx+x*dy)/2)} square metres per second.')),
   P('State one physical limitation near the end of the motion.',R('The ideal model ignores slipping, ladder thickness and loss of contact; it should not be extrapolated through the ladder reaching the floor.'))],{'height':y,'verticalVelocity':dy,'areaRate':(y*dx+x*dy)/2})
  a=80+10*v;k=.2+.02*v;T=20;t=1/k;f=lambda t:a*t*math.exp(-k*t);df=lambda t:a*math.exp(-k*t)*(1-k*t)
  add('ca',6,v,'Optimal release of a product','Exponential optimization investigation','5.10',f'A daily revenue response is $R(t)={a}te^{{-{k:g}t}}$ for $0\\leq t\\leq20$ days after release.',[
   P('Find and solve the stationary-point equation.',M('Differentiate by the product and chain rules.'),A(f'$R^\\prime(t)={a}e^{{-{k:g}t}}(1-{k:g}t)$.'),M('Set the non-exponential factor equal to zero.'),A(f'$t={sf(t)}$ days.')),
   P('Use the second derivative to classify the stationary point.',M(f'$R^{{\\prime\\prime}}(t)={a}e^{{-{k:g}t}}({k*k:g}t-{2*k:g})$.'),A(f'At the stationary point $R^{{\\prime\\prime}}=-{a*k:g}/e<0$.'),R('It is a local maximum.')),
   P('Show that this is the global maximum on the model domain and calculate it.',M('Compare the stationary value with the two endpoint values.'),A(f'$R(0)=0$, $R(20)={sf(f(20))}$.'),A(f'Global maximum {sf(f(t))}.')),
   P('The decay parameter increases by 10%. Find the new optimal time and explain the direction of change.',A(f'New optimum {sf(1/(1.1*k))} days.'),R('A faster decay requires an earlier optimal time.'))],{'optimalTime':t,'maximumRevenue':f(t),'endpoint20':f(20),'newOptimalTime':1/(1.1*k)})
  a=2+v;f=lambda x:x**3-3*a*x;root=math.sqrt(a)
  add('ca',7,v,'Shape of a cubic profile','Second derivative and concavity','5.10',f'A profile is $f(x)=x^3-{3*a}x$.',[
   P('Find and classify both stationary points.',M(f'$f^\\prime(x)=3x^2-{3*a}=0$.'),A(f'$x=\\pm\\sqrt{{{a}}}$.'),M('$f^{\\prime\\prime}(x)=6x$.'),A(f'Local maximum at $(-\\sqrt{{{a}}},{sf(f(-root))})$, local minimum at $(\\sqrt{{{a}}},{sf(f(root))})$.')),
   P('Find the inflection point and the concavity intervals.',A('Inflection point $(0,0)$.'),R('The second derivative changes sign at zero.'),A('Concave down for $x<0$ and concave up for $x>0$.')),
   P('Explain why a zero second derivative alone is insufficient to identify an inflection point.',R('Concavity must change; the second derivative can be zero without changing sign.'))],{'maximumX':-root,'maximumY':f(-root),'minimumX':root,'minimumY':f(root)})
  a=2+v;upper=2;value=.5*math.log((a*upper*upper+1)/1)
  add('ca',8,v,'Accumulated logarithmic response','Integration by substitution','5.11',f'A response rate is $r(x)={a}x/({a}x^2+1)$ for $x\\geq0$.',[
   P('Find an antiderivative, explaining an appropriate substitution.',M(f'Let $u={a}x^2+1$, so $du={2*a}x\\,dx$.'),A('$\\int r(x)\\,dx=\\tfrac12\\ln u+C$.'),A(f'$\\tfrac12\\ln({a}x^2+1)+C$.')),
   P('Find the accumulated response from 0 to 2.',M('Evaluate the antiderivative at 2 and 0.'),A(f'Accumulation $\\tfrac12\\ln({4*a+1})={sf(value)}$.')),
   P('The accumulated response starts at 5 when $x=0$. Write its function.',M('Use the initial condition to find the constant.'),A(f'$F(x)=5+\\tfrac12\\ln({a}x^2+1)$.'))],{'accumulation0to2':value})
  a=5+v;b=.5+.1*v;end=math.pi/(2*b);val=a/b
  add('ca',9,v,'Accumulation during a pulse','Trigonometric integration','5.11',f'A flow rate is $q(t)={a}\\cos({b:g}t)$ litres per minute for $0\\leq t\\leq \\pi/({2*b:g})$.',[
   P('Find the volume delivered over the pulse.',M('Integrate the rate over the stated interval.'),A(f'Antiderivative $({a}/{b:g})\\sin({b:g}t)$.'),A(f'Volume {sf(val)} litres.')),
   P('Find the time by which half the volume has been delivered.',M('The accumulated fraction is $\\sin(bt)$.'),M('Solve $\\sin(bt)=1/2$ within the pulse interval.'),A(f'$t=\\pi/(6({b:g}))={sf(math.pi/(6*b))}$ minutes.')),
   P('Explain why no second inverse-sine solution is admissible.',R('The pulse domain ends at argument $\\pi/2$, before the supplementary-angle solution.'))],{'totalVolume':val,'halfVolumeTime':math.pi/(6*b)})
  a=1+.5*v;b=a+1;F=lambda x:x**3/3-a*a*x;signed=2*F(b);area=2*(F(b)-2*F(a))
  add('ca',10,v,'Signed integral and occupied area','Area with sign changes investigation','5.12',f'A cross-section is described by $f(x)=x^2-{a*a:g}$ on $-{b:g}\\leq x\\leq {b:g}$.',[
   P('Find the intercepts and state where the function is negative.',M('Solve $x^2-a^2=0$.'),A(f'Intercepts $x=\\pm{a:g}$.'),A(f'$f(x)<0$ on $(-{a:g},{a:g})$.')),
   P('Calculate the signed integral over the full interval.',M('Use antiderivative $x^3/3-a^2x$.'),M('Evaluate at the two interval endpoints.'),A(f'Signed integral {sf(signed)}.')),
   P('Calculate the total area between the curve and the x-axis.',M('Split the integral at both intercepts or use symmetry.'),M(f'Area $=2[-\\int_0^{{{a:g}}}f(x)dx+\\int_{{{a:g}}}^{{{b:g}}}f(x)dx]$.'),A(f'Total area {sf(area)} square units.')),
   P('Explain why taking the absolute value of the signed integral generally gives the wrong area.',R('Positive and negative contributions cancel before the absolute value is taken.'),R('Area requires reversing each negative contribution before adding.'),R(f'Here the signed-integral magnitude {sf(abs(signed))} differs from the total area {sf(area)}.'))],{'signedIntegral':signed,'totalArea':area})
  a=2+v;b=4;volume=math.pi*(a*b+a*a*b*b/2) # radius sqrt(a+a^2*x) on 0..4
  add('ca',11,v,'Designing a rotational vessel','Volume of revolution investigation','5.12',f'A vessel is formed by rotating $y=\\sqrt{{{a}+{a*a}x}}$ about the x-axis for $0\\leq x\\leq4$. All lengths are in centimetres.',[
   P('Find the two end radii and set up an exact volume integral.',A(f'End radii $\\sqrt{{{a}}}$ and $\\sqrt{{{a+4*a*a}}}$ cm.'),M('Use circular cross-section area $\\pi y^2$.'),A(f'$V=\\pi\\int_0^4({a}+{a*a}x)\\,dx$.')),
   P('Evaluate the volume.',M(f'Antiderivative ${a}x+({a*a}/2)x^2$.'),A(f'$V={a*4+a*a*8}\\pi={sf(volume)}$ cubic centimetres.')),
   P('All lengths are increased by 10%. Find the new volume and explain the scale factor.',R('A volume scales with the cube of the length factor.'),M('Multiply the original volume by $1.1^3$.'),A(f'New volume {sf(volume*1.1**3)} cubic centimetres.')),
   P('Wall thickness is ignored. Explain how this affects using the calculation as an internal capacity.',R('The curve must describe the inner radius for the integral to give capacity.'),R('If it describes the exterior, the calculated volume overestimates internal capacity.'),R('A wall-thickness model and compatible inner length would be needed.'),R('The solid-of-revolution assumption also excludes openings or internal components.'))],{'volume':volume,'scaledVolume':volume*1.1**3})
  a=1+.2*v;b=3+.2*v;T=5;vel=lambda t:(t-a)*(t-b);F=lambda t:t**3/3-(a+b)*t*t/2+a*b*t;disp=F(T);distance=F(a)-(F(b)-F(a))+(F(T)-F(b))
  add('ca',12,v,'A vehicle changing direction','Kinematics investigation','5.13',f'A vehicle has velocity $v(t)=(t-{a:g})(t-{b:g})$ metres per second on $0\\leq t\\leq5$. Its initial position is zero.',[
   P('Find the times of rest and direction of motion on each intervening interval.',A(f'Rest at $t={a:g},{b:g}$ seconds.'),R(f'Positive on $[0,{a:g})$, negative on $({a:g},{b:g})$, positive on $({b:g},5]$.')),
   P('Find the final displacement.',M('Integrate velocity from 0 to 5.'),A(f'Position antiderivative $t^3/3-({a+b:g}/2)t^2+{a*b:g}t$.'),A(f'Displacement {sf(disp)} m.')),
   P('Find the total distance travelled.',M('Split the integral at both rest times and reverse the negative contribution.'),A(f'Distance $F({a:g})-[F({b:g})-F({a:g})]+[F(5)-F({b:g})]$.'),A(f'Total distance {sf(distance)} m.')),
   P('Find the acceleration at the second rest time and explain whether the vehicle is speeding up immediately after it.',M(f'$a(t)=2t-{a+b:g}$.'),A(f'Acceleration there is {b-a:g} metres per second squared.'),R('Immediately afterwards both velocity and acceleration are positive, so speed is increasing.'),R('At the exact rest instant the speed is zero; the directional statement applies just after it.'))],{'displacement':disp,'totalDistance':distance,'accelerationAtSecondRest':b-a})
  c=4+v;s=7;speed=math.sqrt(c*s+9);acc=c/2
  add('ca',13,v,'Velocity given by position','Kinematic chain rule','5.13',f'A particle moving in the positive direction has speed $v(s)=\\sqrt{{{c}s+9}}$ for displacement $s\\geq0$, where $s$ is measured in metres and $v$ in metres per second.',[
   P('Find acceleration as a function of displacement.',M('Use $a=v\\,dv/ds$.'),A(f'$dv/ds={c}/(2\\sqrt{{{c}s+9}})$.'),A(f'$a={c}/2={acc:g}$ metres per second squared, constant.')),
   P('Find the speed at displacement 7 m and the time to reach that point from displacement zero.',A(f'Speed {sf(speed)} metres per second.'),M('Initial speed is 3 metres per second and acceleration is constant, so $v=3+at$.'),A(f'Time {sf((speed-3)/acc)} seconds.')),
   P('Explain why $dv/ds$ alone is not the acceleration.',R('It measures speed change per displacement unit, whereas acceleration is speed change per time unit.'))],{'acceleration':acc,'speedAt7':speed,'timeTo7':(speed-3)/acc})
  N0=150+20*v;k=.12+.02*v;t=10;N=N0*math.exp(k*t)
  add('ca',14,v,'Modelling bacterial growth','Separable growth equation','5.14',f'A bacterial population grows at a rate proportional to its current size. Initially there are {N0} bacteria; the proportionality constant is {k:g} per hour.',[
   P('Set up and solve the differential equation using separation.',A(f'$dN/dt={k:g}N$, $N(0)={N0}$.'),M('$dN/N=k\\,dt$ and integrate.'),A('$\\ln N=kt+C$ for a positive population.'),A(f'$N(t)={N0}e^{{{k:g}t}}$.')),
   P('Find the population after ten hours and the doubling time.',A(f'$N(10)={sf(N)}$.'),M('Set $e^{kt}=2$.'),A(f'Doubling time {sf(math.log(2)/k)} hours.')),
   P('Explain why the equation eventually requires modification.',R('The proportional growth assumption ignores limited nutrients and space.'))],{'population10':N,'doublingTime':math.log(2)/k})
  amb=20;initial=80+5*v;k=.08+.01*v;target=35;t=math.log((initial-amb)/(target-amb))/k
  add('ca',15,v,'Differential cooling model','Separation and model critique investigation','5.14',f'A sample has temperature $T$ degrees Celsius and cools at a rate proportional to $T-20$. The rate constant is {k:g} per minute and the initial temperature is {initial}.',[
   P('Form a differential equation with the correct sign and initial condition.',A(f'$dT/dt=-{k:g}(T-20)$.'),A(f'$T(0)={initial}$.'),R('The negative sign produces cooling when $T>20$.')),
   P('Solve the equation by separation.',M('$dT/(T-20)=-k\\,dt$.'),A('$\\ln|T-20|=-kt+C$.'),M('Use the initial temperature to determine the constant.'),A(f'$T(t)=20+{initial-20}e^{{-{k:g}t}}$.')),
   P('Find when the sample reaches 35 degrees.',M(f'Solve $15={initial-20}e^{{-{k:g}t}}$.'),A(f'$t={sf(t)}$ minutes.')),
   P('Explain why the model cannot predict cooling below 20 degrees, and name one change that could allow it.',R('The solution approaches the constant ambient temperature 20 from above.'),R('It does not cross the equilibrium under this autonomous equation.'),R('A lower or time-varying ambient temperature would require a changed model.'))],{'time35':t,'temperatureAt10':20+(initial-20)*math.exp(-10*k)})
  inflow=12+v;rate=.2+.02*v;y0=20;eq=inflow/rate;t=5;y=eq+(y0-eq)*math.exp(-rate*t)
  add('ca',16,v,'Dissolved material in a tank','Inflow-outflow differential equation','5.14',f'A well-mixed tank receives dissolved material at {inflow} g per minute and loses it at {rate:g} times its present mass per minute. Initially it contains 20 g. Tank volume is held constant.',[
   P('Set up the mass differential equation and find the equilibrium.',A(f'$dy/dt={inflow}-{rate:g}y$.'),M('Set the net rate equal to zero.'),A(f'Equilibrium mass {sf(eq)} g.')),
   P('Solve the initial-value problem by separation.',M('Write $dy/(y-L)=-k\\,dt$ with $L=$ equilibrium.'),A('$\\ln|y-L|=-kt+C$.'),M('Use $y(0)=20$.'),A(f'$y(t)={eq:.12g}+(20-{eq:.12g})e^{{-{rate:g}t}}$, retaining exact $L={inflow}/{rate:g}$.')),
   P('Find the mass after five minutes and describe its long-term behaviour.',A(f'$y(5)={sf(y)}$ g.'),R('It increases towards the equilibrium because the initial mass is below it.'),R('The difference from equilibrium decreases exponentially.')),
   P('State two assumptions behind the equation.',R('The tank is sufficiently well mixed that outflow concentration represents the tank.'),R('Inflow and removal parameters remain constant.'))],{'equilibrium':eq,'massAt5':y})
  k=.5+.1*v;L=3;f=lambda x,y:k*(L-y);diag=slopefield(f,xmax=3,ymax=5)
  add('ca',17,v,'Reading a treatment slope field','Slope-field interpretation','5.15',f'The diagram shows a slope field for $dy/dt={k:g}(3-y)$. Consider solutions starting at $y(0)=1$ and $y(0)=4$.',[
   P('Use the field to describe the initial direction and eventual behaviour of each solution.',R('From y=1 the segments slope upwards, so the solution initially increases.'),R('From y=4 the segments slope downwards, so the solution initially decreases.'),R('Both approach the horizontal equilibrium y=3.')),
   P('Find the initial gradients for the two solutions.',M('Substitute the two initial y-values into the differential equation.'),A(f'Gradients {2*k:g} and {-k:g}, respectively.')),
   P('Explain whether either solution crosses the equilibrium in the model.',M('The general non-equilibrium solution is $y=3+Ce^{-kt}$.'),R('Its deviation from 3 retains its initial sign, so neither crosses.')),
   P('State one limitation of judging a solution from a finite slope-field drawing.',R('The drawing samples only a finite set of points; numerical or analytic work is needed for precise values.'))],{'initialGradientLow':2*k,'initialGradientHigh':-k},diagram=diag)
  k=.6+.1*v;f=lambda t,y:k*y;y,rows=euler(f,0,2,.25,4);exact=2*math.exp(k);err=y-exact
  add('ca',18,v,'Euler estimate of growth','Euler method investigation','5.16',f'Use forward Euler\'s method for $dy/dt={k:g}y$, $y(0)=2$, from $t=0$ to $t=1$ with step size $h=0.25$.',[
   P('Write the recurrence and give the four successive y-values.',M('$y_{n+1}=y_n+0.25ky_n$.'),A(f'Step 1: {sf(rows[0][3])}.'),A(f'Step 2: {sf(rows[1][3])}.'),A(f'Steps 3 and 4: {sf(rows[2][3])}, {sf(rows[3][3])}; retain unrounded values at each step.')),
   P('Find the exact value at 1 and the signed Euler error.',M('The exact solution is $y=2e^{kt}$.'),A(f'Exact value {sf(exact)}.'),A(f'Euler minus exact = {sf(err)}.')),
   P('Use the shape of the solution to explain the error direction.',R('The positive exponential solution is concave up.'),R('Each forward tangent step lies below the curve locally.'),R('The Euler result therefore underestimates here.')),
   P('Explain a reasonable way to improve and assess the numerical estimate.',R('Repeat with a smaller step and compare the endpoint estimates.'),R('Retain unrounded working so observed changes reflect discretization rather than premature rounding.'))],{'eulerAt1':y,'exactAt1':exact,'signedError':err,'unroundedSteps':rows})
  k=.7+.1*v;f=lambda t,y:k*(5-y);coarse,rc=euler(f,0,1,.5,4);fine,rf=euler(f,0,1,.25,8);exact=5-4*math.exp(-2*k)
  add('ca',19,v,'Checking numerical step size','Euler refinement investigation','5.16',f'A process obeys $dy/dt={k:g}(5-y)$ with $y(0)=1$. Estimate $y(2)$ by forward Euler, using step sizes 0.5 and 0.25.',[
   P('Write a recurrence valid for either step size, and calculate both endpoint estimates.',M('$y_{n+1}=y_n+hk(5-y_n)$.'),M('Use 4 steps for $h=0.5$ and 8 steps for $h=0.25$.'),A(f'Coarse estimate {sf(coarse)}.'),A(f'Fine estimate {sf(fine)}.')),
   P('The exact solution is $y=5-4e^{-kt}$. Calculate each absolute error.',M('Evaluate the exact value at $t=2$.'),A(f'Exact value {sf(exact)}.'),A(f'Coarse absolute error {sf(abs(coarse-exact))}; fine absolute error {sf(abs(fine-exact))}.')),
   P('Explain the direction of both errors and assess the refinement.',R('The solution rises towards 5 and is concave down.'),R('Forward tangent steps overestimate for these stable step sizes.'),R('The smaller step gives a closer endpoint estimate in this calculation.')),
   P('Explain why agreement of two numerical estimates alone is not a universal proof of accuracy.',R('Both computations can share the same model or implementation error.'),R('Step-size comparison should be combined with a valid numerical method and checks of qualitative behaviour.'))],{'coarse':coarse,'fine':fine,'exact':exact,'coarseSteps':rc,'fineSteps':rf})
  a=.4+.05*v;b=.2;f=lambda x,y:a*x-b*y;g=lambda x,y:.1*x-.3*y;x,y,rows=coupled(f,g,20,10,.5,2)
  add('ca',20,v,'Two interacting populations numerically','Coupled Euler investigation','5.16',f'Two population indices obey $dx/dt={a:g}x-0.2y$ and $dy/dt=0.1x-0.3y$, with $x(0)=20$, $y(0)=10$. Use simultaneous forward Euler steps of size 0.5.',[
   P('Find both initial rates and the state after the first step.',A(f'Initial rates {sf(f(20,10))}, {sf(g(20,10))}.'),M('Update both variables using their old values at $t=0$.'),A(f'At $t=0.5$: $x={sf(rows[0][3])}$, $y={sf(rows[0][4])}$.')),
   P('Continue to $t=1$.',M('Recalculate both rates using the state at 0.5.'),A(f'At $t=1$: $x={sf(x)}$, $y={sf(y)}$.')),
   P('Explain why updating y using the newly updated x in the same step is not this Euler procedure.',R('Forward Euler evaluates the entire vector derivative at the old time and old state.'),R('Using a new component produces a different numerical scheme.')),
   P('Interpret the interaction terms and give two cautions about prediction.',R('The term -0.2y reduces the instantaneous x growth rate.'),R('The term +0.1x raises the instantaneous y growth rate.'),R('Indices must stay physically meaningful; a negative numerical population signals a modelling or step-size problem.'),R('Parameters and interactions are assumed constant.'),R('Numerical accuracy should be checked with a smaller step.'))],{'xAt1':x,'yAt1':y,'steps':rows})
  l1=.3+.05*v;l2=-.5;A0=np.array([[(l1+l2)/2,(l1-l2)/2],[(l1-l2)/2,(l1+l2)/2]]);t=2;x=4*math.exp(l1*t)+2*math.exp(l2*t);y=4*math.exp(l1*t)-2*math.exp(l2*t)
  add('ca',21,v,'Exact coupled growth modes','Distinct-real coupled differential equations','5.17',f'A system obeys $s^\\prime=As$, where $A={mat([[round(z,4) for z in row] for row in A0])}$ and $s(0)=(6,2)^T$.',[
   P('Find the eigenvalues and corresponding eigenvectors.',M('Solve the characteristic equation or verify the symmetric and antisymmetric modes.'),A(f'$\\lambda_1={l1:g}$ with $(1,1)^T$.'),A('$\\lambda_2=-0.5$ with $(1,-1)^T$.')),
   P('Find the exact solution satisfying the initial state.',M('Use $s=C_1e^{\\lambda_1t}v_1+C_2e^{\\lambda_2t}v_2$.'),A('$C_1+C_2=6$, $C_1-C_2=2$.'),A('$C_1=4$, $C_2=2$.'),A(f'$x=4e^{{{l1:g}t}}+2e^{{-0.5t}}$, $y=4e^{{{l1:g}t}}-2e^{{-0.5t}}$.')),
   P('Find the state at time 2 and the long-term ratio of its components.',M('Evaluate both exact components at 2.'),A(f'$s(2)={vec([sf(x),sf(y)])}$.'),R('The positive symmetric mode dominates, so x:y tends to 1:1.')),
   P('Classify the equilibrium and explain its stability.',A('The origin is a saddle.'),R('One eigenvalue is positive and the other is negative.'),R('Only initial states exactly on the stable eigendirection approach the origin.'),R('A nonzero positive-eigenvalue component grows away.'))],{'eigenvalues':[l1,l2],'xAt2':x,'yAt2':y})
  a=.5+.1*v;b=.8;f=lambda x,y:a*x;g=lambda x,y:-b*y;segments=[]
  for x0 in np.linspace(-3,3,9):
   for y0 in np.linspace(-3,3,9):
    dx=f(x0,y0);dy=g(x0,y0);norm=math.hypot(dx,dy)
    if norm:segments.append((x0-.1*dx/norm,y0-.1*dy/norm,x0+.1*dx/norm,y0+.1*dy/norm))
  diag=plot(xmin=-4,xmax=4,ymin=-4,ymax=4,segments=segments,points=[(1,2,'P')],equal=True)
  add('ca',22,v,'A saddle phase portrait','Phase-plane investigation','5.17',f'The diagram shows local line directions for $x^\\prime={a:g}x$, $y^\\prime=-0.8y$, including initial point P. Time arrows are to be determined from the equations.',[
   P('Read the initial coordinates at P and find its initial derivative vector.',A('P is $(1,2)$.'),M('Substitute into the two differential equations.'),A(f'Initial derivative $({a:g},-1.6)$.')),
   P('Write the trajectory through P as a time-parametrized solution.',M('Solve the independent exponential equations.'),A(f'$x=e^{{{a:g}t}}$, $y=2e^{{-0.8t}}$.')),
   P('Identify the stable and unstable eigendirections and classify the origin.',A('The y-axis is stable; the x-axis is unstable.'),R('The eigenvalues have opposite signs.'),A('The origin is a saddle.')),
   P('Describe the forward path through P and assess the claim that every nearby trajectory approaches the origin.',R('The path moves rightwards and downwards in quadrant I.'),R('Its y-coordinate tends to zero while x increases without bound.'),R('The claim is false; only the stable eigendirection approaches the origin.'),R('The small-distance appearance of a drawn segment alone does not establish stability.'))],{'initialX':1,'initialY':2,'initialDx':a,'initialDy':-1.6},diagram=diag)
  decay=.2+.05*v;omega=1+.2*v;A0=[[-decay,-omega],[omega,-decay]]
  add('ca',23,v,'Damped rotational dynamics','Complex-eigenvalue phase behaviour','5.17',f'A coupled system has matrix $A={mat(A0)}$. Its eigenvalues are $-{decay:g}\\pm {omega:g}i$. Exact complex-eigenvalue solutions are not required.',[
   P('Classify the origin and describe forward trajectories.',R('The real part of both eigenvalues is negative.'),A('The origin is a stable spiral.'),R('Nonzero trajectories spiral towards the origin as time increases.')),
   P('Determine the initial direction of motion from $(1,0)$.',M('Multiply A by $(1,0)^T$.'),A(f'Initial derivative $(-{decay:g},{omega:g})$.'),R('The positive vertical component gives anticlockwise rotation.')),
   P('Explain what changes if the real part becomes positive while the imaginary part remains nonzero.',A('The origin becomes an unstable spiral.'),R('Trajectories spiral away rather than towards the origin.'))],{'realPart':-decay,'imaginaryMagnitude':omega,'initialDx':-decay,'initialDy':omega})
  omega=1+.2*v;f=lambda x,y:y;g=lambda x,y:-omega*omega*x;xx,yy,rows=coupled(f,g,1,0,.1,3)
  add('ca',24,v,'Numerical motion of an oscillator','Second-order Euler investigation','5.18',f'An oscillator obeys $x^{{\\prime\\prime}}=-{omega*omega:g}x$, with $x(0)=1$, $x^\\prime(0)=0$. Let $y=x^\\prime$ and use simultaneous forward Euler with $h=0.1$.',[
   P('Rewrite the equation as a coupled first-order system and calculate the first step.',A(f'$x^\\prime=y$, $y^\\prime=-{omega*omega:g}x$.'),M('Use the old x and y values in both updates.'),A(f'At 0.1: $x=1$, $y={-omega*omega*.1:g}$.')),
   P('Continue to time 0.3.',M('Apply two more simultaneous updates.'),A(f'At 0.2: x={sf(rows[1][3])}, y={sf(rows[1][4])}.'),A(f'At 0.3: x={sf(xx)}, y={sf(yy)}.')),
   P('The exact displacement is $\\cos(\\omega t)$. Compare the displacement estimate at 0.3 with the exact value.',M(f'Evaluate $\\cos({omega:g}(0.3))$.'),A(f'Exact displacement {sf(math.cos(.3*omega))}.'),A(f'Euler minus exact = {sf(xx-math.cos(.3*omega))}.')),
   P('State the exact phase-portrait type and explain a caution about long Euler simulations.',R('Purely imaginary eigenvalues give closed elliptical trajectories; in suitably scaled coordinates these are circles.'),R('Forward Euler can distort amplitude over many steps.'),R('A smaller step and comparison with the known exact motion are useful checks.'))],{'xAt0p3':xx,'velocityAt0p3':yy,'exactXAt0p3':math.cos(.3*omega),'steps':rows})
  r1=-1-.2*v;r2=-3-.2*v;a=-(r1+r2);b=r1*r2;C1=3;C2=-1;x0=2;y0=C1*r1+C2*r2;value=C1*math.exp(r1)-math.exp(r2)
  add('ca',25,v,'Damped displacement with real modes','Exact second-order investigation','5.18',f'A displacement satisfies $x^{{\\prime\\prime}}+{a:g}x^\\prime+{b:g}x=0$, with $x(0)=2$ and $x^\\prime(0)={y0:g}$.',[
   P('Rewrite this as a first-order matrix system using $y=x^\\prime$.',A('$x^\\prime=y$.'),A(f'$y^\\prime=-{b:g}x-{a:g}y$.'),A(f'System matrix ${mat([[0,1],[-b,-a]])}$.')),
   P('Find the distinct real eigenvalues and write the general displacement solution.',M(f'Solve $r^2+{a:g}r+{b:g}=0$.'),A(f'$r_1={r1:g}$ and $r_2={r2:g}$.'),A(f'$x=C_1e^{{{r1:g}t}}+C_2e^{{{r2:g}t}}$.')),
   P('Apply both initial conditions and calculate $x(1)$.',M('$C_1+C_2=2$ and $r_1C_1+r_2C_2=x^\\prime(0)$.'),A('$C_1=3$, $C_2=-1$.'),A(f'$x(1)={sf(value)}$.')),
   P('Describe the long-term behaviour of x and y and classify the equilibrium.',R('Both real eigenvalues are negative.'),A('The origin is a stable node.'),R('Both displacement and velocity tend to zero.'),R('The slower-decaying mode associated with the eigenvalue closer to zero dominates at late times.'))],{'eigenvalues':[r1,r2],'initialVelocity':y0,'displacementAt1':value})
