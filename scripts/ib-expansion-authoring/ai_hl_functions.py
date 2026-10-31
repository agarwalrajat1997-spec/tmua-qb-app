from ai_hl_common import *
def build():
 for v in range(4):
  p=12+v;fee=5+v;tax=1.08+.01*v;target=tax*(p*20+fee)
  add('fn',1,v,'Ticket checkout composition','Composite functions in context','2.7',f'A booking for $n$ tickets costs $f(n)={p}n+{fee}$ before tax. The checkout function is $g(x)={tax:g}x$. Only whole numbers $n\\geq0$ are permitted.',[
   P('Find $(g\\circ f)(n)$ and interpret the order.',M('Apply the booking price first, then tax.'),A(f'$(g\\circ f)(n)={tax:g}({p}n+{fee})$.'),R('Tax applies to the ticket charge and booking fee.')),
   P(f'Find the ticket count for a checkout total of {target:g}.',M(f'Solve ${tax:g}({p}n+{fee})={target:g}$.'),A('$n=20$ tickets.')),
   P('For comparison only, extend the pricing formula algebraically to real inputs. Calculate the formal expression $f(g(n))$ and compare it with the checkout rule. Explain why it is not generally a valid ticket-booking operation on the original domain.',A(f'The formal algebraic extension gives $f(g(n))={p*tax:g}n+{fee}$.'),R(f'The fee is not taxed in this order, so the checkout exceeds this expression by {fee*(tax-1):g} currency units.'),R('For a whole-number n, g(n) need not be a whole number, so it may lie outside the original ticket-count domain of f. The formal extension is not the booking operation.'))],{'checkout20':target,'orderDifference':fee*(tax-1)})
  h=2+v;k=5+v;y=k+36
  add('fn',2,v,'Inverting a sensor branch','Inverse and restricted domain','2.7',f'A sensor uses $f(x)=(x-{h})^2+{k}$ for $x\\geq {h}$.',[
   P('Find the range and the inverse, including its domain.',A(f'Range of $f$: $y\\geq{k}$.'),M('Swap input and output and take the positive square-root branch.'),A(f'$f^{{-1}}(x)={h}+\\sqrt{{x-{k}}}$ for $x\\geq{k}$.')),
   P(f'Find $f^{{-1}}({y})$ and explain why the negative branch is excluded.',A(f'$f^{{-1}}({y})={h+6}$.'),R(f'The negative branch gives an input below {h}, outside the restricted sensor domain.')),
   P('Explain why the unrestricted quadratic has no inverse function on all real inputs.',R('Two inputs equally spaced from the vertex have the same output.'))],{'inverseAtTarget':h+6})
  a=7+v;b=.18+.02*v;target=60;t=math.log(target/a)/b
  add('fn',3,v,'Inverting a growth monitor','Exponential inverse','2.7',f'A monitor model is $f(t)={a}e^{{{b:g}t}}$ for $0\\leq t\\leq20$.',[
   P('Find the inverse and its domain.',M('Divide the output by $a$ and take natural logarithms.'),A(f'$f^{{-1}}(x)=\\ln(x/{a})/{b:g}$.'),A(f'Domain ${a}\\leq x\\leq {a}e^{{20({b:g})}}$; the upper endpoint is approximately ${sf(a*math.exp(20*b))}$.')),
   P('Find when the output reaches 60 and explain the meaning of the inverse value.',M(f'Evaluate $\\ln(60/{a})/{b:g}$.'),A(f'$t={sf(t)}$ time units.'),R('The inverse returns the elapsed time corresponding to a measured output.'))],{'time60':t,'rangeMaximum':a*math.exp(20*b)})
  s=2+v;h=1+v;d=3;diag=plot(curves=[lambda x:x*x],points=[(1,1,'P')],xmin=0,xmax=3,ymin=0,ymax=10)
  add('fn',4,v,'Relocating a reference graph','Graph transformations','2.8',f'The diagram shows the reference curve $y=f(x)=x^2$ and point P. A new curve is $g(x)={s}f(x-{h})+3$.',[
   P('Describe an ordered sequence of transformations from $f$ to $g$.',R(f'A vertical stretch of factor {s}.'),R(f'Then a translation by $({h},3)$; reversing the vertical stretch and vertical translation changes the result.')),
   P('Find the image of P and the vertex of the new curve.',A(f'P maps to $({1+h},{s+3})$.'),A(f'The vertex is $({h},3)$.')),
   P('Find all real intersections of $g$ with the line $y=15$.',M(f'${s}(x-{h})^2=12$.'),A(f'$x={sf(h-math.sqrt(12/s))}$ and ${sf(h+math.sqrt(12/s))}$.'),R('Both square-root signs are required because no domain restriction is imposed.'))],{'leftIntersection':h-math.sqrt(12/s),'rightIntersection':h+math.sqrt(12/s)},diagram=diag)
  a=2+v;h=3
  add('fn',5,v,'Order in a calibration shift','Composite transformations','2.8',f'Let $f(x)=e^x$. Operation S multiplies all output values by {a}; operation T translates a graph upwards by 3.',[
   P('Write the functions obtained by S then T, and by T then S.',A(f'S then T gives ${a}e^x+3$.'),A(f'T then S gives ${a}(e^x+3)$.')),
   P('Find the constant difference between these outputs.',M('Subtract the two expressions with the same input.'),A(f'T then S exceeds S then T by {3*a-3}.')),
   P('Find each range and explain the difference using the horizontal asymptotes.',A('S then T has range $(3,\\infty)$.'),A(f'T then S has range $({3*a},\\infty)$.'),R('Each vertical translation is scaled only when it is applied before the stretch.'))],{'outputDifference':3*a-3})
  initial=240+20*v;half=8+v;k=math.log(2)/half;t=half*math.log(initial/30)/math.log(2)
  add('fn',6,v,'Tracer decay calibration','Half-life model','2.9',f'A tracer has initial amount {initial} mg and half-life {half} hours. It is modelled by $M(t)=Ae^{{-kt}}$, $t\\geq0$.',[
   P('Find $A$ and $k$, then state the amount after two half-lives.',A(f'$A={initial}$.'),M(f'$e^{{-{half}k}}=1/2$.'),A(f'$k={sf(k)}$ per hour.'),A(f'After {2*half} hours the amount is {initial/4:g} mg.')),
   P('Find when the amount first falls to 30 mg.',M(f'Solve ${initial}e^{{-kt}}=30$ using unrounded $k$.'),A(f'$t={sf(t)}$ hours.')),
   P('Explain what the model predicts about an exactly zero amount.',R('The amount approaches zero but remains positive at every finite model time.'),R('Physical detection limits and discrete particles limit that interpretation.'))],{'decayConstant':k,'time30':t})
  ambient=18+v;initial=90;at5=55+v;k=-math.log((at5-ambient)/(initial-ambient))/5;time=-math.log((30-ambient)/(initial-ambient))/k
  add('fn',7,v,'Cooling with a background level','Offset exponential modelling','2.9',f'A liquid cools according to $T(t)=B+Ae^{{-kt}}$ in a room held at {ambient} degrees Celsius. Initially it is 90 degrees; after 5 minutes it is {at5} degrees.',[
   P('Determine $B,A,k$.',A(f'$B={ambient}$.'),A(f'$A={90-ambient}$.'),M(f'$({at5}-{ambient})/(90-{ambient})=e^{{-5k}}$.'),A(f'$k={sf(k)}$ per minute.')),
   P('Find when the liquid reaches 30 degrees.',M('Solve the calibrated exponential equation at $T=30$.'),A(f'$t={sf(time)}$ minutes.')),
   P('A prediction is needed for an outdoor room with changing temperature. Explain a limitation.',R('The constant asymptote assumes fixed ambient temperature.'),R('Changing room temperature requires a different model or updated observations.'))],{'coolingConstant':k,'time30':time})
  a=20+v;b=6+v;x=math.exp((50-a)/b)
  add('fn',8,v,'Logarithmic response scale','Natural logarithmic model','2.9',f'A response is modelled by $R(x)={a}+{b}\\ln x$, where the input $x>0$.',[
   P('Find the response at $x=1$ and the input producing response 50.',A(f'$R(1)={a}$.'),M(f'$\\ln x=(50-{a})/{b}$.'),A(f'$x={sf(x)}$.')),
   P('Find the change in response when any positive input is doubled.',M('Subtract $R(x)$ from $R(2x)$ using logarithm laws.'),A(f'The increase is ${b}\\ln2={sf(b*math.log(2))}$.')),
   P('Explain why the same absolute increase in input has less effect at larger inputs.',R('The logarithmic graph becomes flatter as the positive input increases.'),R('A fixed absolute increase is a smaller multiplicative change at a larger input.'))],{'inputFor50':x,'doublingIncrease':b*math.log(2)})
  amp=3+.2*v;mid=12;period=365;phase=80+v*5;b=2*math.pi/period
  add('fn',9,v,'Daylight through a year','Sinusoidal parameters','2.9',f'Daylight hours are modelled by $D(t)={mid}+{amp:g}\\sin({sf(b,8)}(t-{phase}))$, with exact angular frequency $2\\pi/365$ and $0\\leq t\\leq365$.',[
   P('State the amplitude, period and range.',A(f'Amplitude {amp:g} hours.'),A('Period 365 days.'),A(f'Range $[{mid-amp:g},{mid+amp:g}]$ hours.')),
   P('Find the first day of maximum daylight.',M('Set the sine argument equal to $\\pi/2$.'),A(f'$t={phase+365/4:g}$ days.')),
   P('Find the total length of time in the year for which daylight exceeds 12 hours.',M('The sine is positive on half of each full period.'),A('182.5 days.')),
   P('Explain a limitation if the same parameters are used at a different latitude.',R('Latitude affects the seasonal amplitude and may change whether the sinusoidal approximation is reasonable.'))],{'firstMaximumDay':phase+365/4,'aboveMidlineDays':182.5})
  amp=1.5+.1*v;mid=3;period=12;phase=1+.2*v;threshold=3.8;alpha=math.asin((threshold-mid)/amp);t1=phase+alpha*period/(2*math.pi);t2=phase+(math.pi-alpha)*period/(2*math.pi)
  add('fn',10,v,'Safe harbour access window','Sinusoidal inequality investigation','2.9',f'Harbour depth is $H(t)=3+{amp:g}\\sin(\\pi(t-{phase:g})/6)$ metres, where $0\\leq t\\leq12$ hours. A vessel requires depth at least 3.8 m.',[
   P('Find the maximum and minimum depths, and the first high tide.',A(f'Maximum {mid+amp:g} m and minimum {mid-amp:g} m.'),M('High tide occurs at sine argument $\\pi/2$.'),A(f'First high tide $t={phase+3:g}$ hours.')),
   P('Find the two boundary times of the access window in this interval.',M(f'Solve $\\sin(\\pi(t-{phase:g})/6)=0.8/{amp:g}$.'),A(f'Principal angle {sf(alpha)} radians.'),M('Use both $\\alpha$ and $\\pi-\\alpha$ in the first positive half-cycle.'),A(f'Boundary times {sf(t1)} and {sf(t2)} hours.')),
   P('State the complete access interval and its duration.',A(f'${sf(t1)}\\leq t\\leq {sf(t2)}$.'),A(f'Duration {sf(t2-t1)} hours.')),
   P('Depth measurements have uncertainty $\\pm0.10$ m. Describe a conservative decision rule.',R('Require model depth at least 3.9 m to allow for a 0.10 m downward error.'),R('This narrows the safe interval around high tide.'),R('The actual uncertainty and vessel clearance policy should be checked before applying the model.'))],{'boundary1':t1,'boundary2':t2,'duration':t2-t1})
  L=1200+100*v;C=5+v;k=.3+.02*v;at0=L/(1+C);target=.8*L;t=math.log(C/.25)/k
  add('fn',11,v,'A capacity-limited visitor model','Logistic investigation','2.9',f'Visitor registrations follow $N(t)={L}/(1+{C}e^{{-{k:g}t}})$ for $t\\geq0$, with time in weeks.',[
   P('Find the initial number and the carrying capacity.',M('Evaluate $N(0)$.'),A(f'Initial registrations {sf(at0)}.'),A(f'Carrying capacity {L}.')),
   P('Find when registrations reach 80% of capacity.',M(f'Solve $1+{C}e^{{-{k:g}t}}=1.25$.'),M(f'$e^{{-{k:g}t}}=0.25/{C}$.'),A(f'$t={sf(t)}$ weeks.')),
   P('Find the time at which the logistic curve is halfway to capacity, then compare the two waiting times.',M('At $N=L/2$, $Ce^{-kt}=1$.'),A(f'Half-capacity time {sf(math.log(C)/k)} weeks.'),A(f'Additional time from half to 80% is {sf(math.log(4)/k)} weeks.')),
   P('Explain why the logistic model is preferable to unrestricted exponential growth here, and give one possible weakness.',R('It has a finite limiting registration count.'),R('A venue or finite target population can impose such a capacity.'),R('The capacity and response rate may change with advertising, cancellations or venue policy.'))],{'initial':at0,'time80':t,'timeHalf':math.log(C)/k})
  L=800+100*v;N0=100;N4=300+20*v;C=L/N0-1;k=-math.log((L/N4-1)/C)/4
  add('fn',12,v,'Estimating logistic parameters','Logistic calibration','2.9',f'A community adoption model is $N(t)=L/(1+Ce^{{-kt}})$ with known capacity $L={L}$. Observations are $N(0)=100$ and $N(4)={N4}$.',[
   P('Determine $C$ and $k$.',M('$C=L/N(0)-1$.'),A(f'$C={C:g}$.'),M(f'$e^{{-4k}}=({L}/{N4}-1)/{C:g}$.'),A(f'$k={sf(k)}$.')),
   P('Predict $N(8)$ and state whether this is interpolation or extrapolation.',M('Substitute $t=8$ using unrounded fitted parameters.'),A(f'$N(8)={sf(L/(1+C*math.exp(-8*k)))}$.'),R('This is extrapolation beyond the observed time interval.')),
   P('Suggest a useful additional observation for testing the carrying-capacity assumption.',R('Collect later observations near the proposed saturation level.'),R('Check whether they flatten near the proposed capacity rather than continuing to grow.'))],{'C':C,'k':k,'prediction8':L/(1+C*math.exp(-8*k))})
  c=5+v;breakpoint=4;b=(2*breakpoint+c-breakpoint**2)/breakpoint
  add('fn',13,v,'Joining two charging regimes','Piecewise continuity','2.9',f'A battery indicator is $f(t)=2t+{c}$ for $0\\leq t<4$ and $f(t)=t^2+bt$ for $4\\leq t\\leq8$.',[
   P('Find $b$ so that the model is continuous at $t=4$.',M('Equate the left-hand value with the right-hand value at 4.'),A(f'$8+{c}=16+4b$.'),A(f'$b={b:g}$.')),
   P('For this value of $b$, find the first time the indicator reaches 30.',M('The first branch never reaches 30 on its stated interval.'),M(f'Solve $t^2+({b:g})t=30$ on $[4,8]$.'),A(f'$t={sf((-b+math.sqrt(b*b+120))/2)}$.')),
   P('Does continuity imply a physically smooth change of rate? Explain.',R('No; matching values alone does not match slopes at the join.'),R(f'The left slope is 2 and the right slope at 4 is {8+b:g}.'))],{'joinParameter':b,'time30':(-b+math.sqrt(b*b+120))/2})
  rate=2.5+.25*v;base=8+v;second=1.5+.1*v;bill=base+rate*10+second*8
  add('fn',14,v,'A two-tier delivery tariff','Piecewise inverse in context','2.9',f'A delivery charge is $C(d)={base}+{rate:g}d$ for $0\\leq d\\leq10$ km, then $C(d)={base+10*rate:g}+{second:g}(d-10)$ for $d>10$.',[
   P('Verify that the charge is continuous at 10 km.',A(f'The first formula gives {base+10*rate:g}.'),A(f'The second formula gives the same value at the boundary.')),
   P(f'Find the distance for a charge of {bill:g}.',M('The charge exceeds the 10 km boundary charge, so use the second branch.'),M(f'Solve ${base+10*rate:g}+{second:g}(d-10)={bill:g}$.'),A('$d=18$ km.')),
   P('Write a piecewise formula for the inverse, stating the charge intervals.',A(f'$d=(C-{base})/{rate:g}$ for ${base}\\leq C\\leq {base+10*rate:g}$.'),A(f'$d=10+(C-{base+10*rate:g})/{second:g}$ for $C>{base+10*rate:g}$.'),R('Every allowed charge has one distance because both branch slopes are positive.'))],{'charge18':bill,'boundaryCharge':base+10*rate})
  a=2.4+.2*v;b=1.3+.1*v;intercept=math.log(a);pred=a*12**b
  add('fn',15,v,'Allometric energy model','Log-log linearization','2.10',f'A log-log regression gives $\\ln E={intercept:.12g}+{b:g}\\ln m$, where $m>0$ is body mass and $E$ is daily energy use. Use the displayed intercept as exact.',[
   P('Write the corresponding power model.',M('Exponentiate both sides.'),A(f'$E=e^{{{intercept:.12g}}}m^{{{b:g}}}\\approx {sf(math.exp(float(f"{intercept:.12g}")))}m^{{{b:g}}}$.')),
   P('Predict the energy use for mass 12 and the factor change when mass doubles.',M('Substitute mass 12 into the power model.'),A(f'Prediction {sf(pred)} energy units.'),A(f'Doubling multiplier $2^{{{b:g}}}={sf(2**b)}$.')),
   P('Explain the meaning of the slope on this log-log graph.',R(f'A 1% increase in mass gives approximately a {b:g}% increase in energy for small relative changes.'),R('The slope is a power exponent, rather than a fixed energy increase per mass unit.'))],{'exponent':b,'coefficient':a,'prediction12':pred,'doublingFactor':2**b})
  intercept=1.8+.1*v;slope=.23+.02*v;time=(math.log(100)-intercept)/slope
  add('fn',16,v,'Semi-log sensor trace','Semi-log exponential interpretation','2.10',f'A sensor trace is linear when $\\ln S$ is plotted against $t$: $\\ln S={intercept:g}+{slope:g}t$.',[
   P('Write $S$ as an exponential function of $t$.',M('Exponentiate the linear equation.'),A(f'$S=e^{{{intercept:g}}}e^{{{slope:g}t}}$.')),
   P('Find the initial signal, doubling time and time at which $S=100$.',A(f'Initial signal {sf(math.exp(intercept))}.'),M('Solve $e^{bt}=2$ for doubling.'),A(f'Doubling time {sf(math.log(2)/slope)}.'),M('Set $\\ln100=a+bt$.'),A(f'Time {sf(time)}.')),
   P('Explain what a constant slope on the semi-log graph says about growth.',R('The multiplicative growth factor over equal time intervals is constant.'))],{'initial':math.exp(intercept),'doublingTime':math.log(2)/slope,'time100':time})
  c=10+v;xs=[0,1,2,3];obs=[c,c+5,c+13,c+23];f=lambda x:c+3*x+1.5*x*x;g=lambda x:c*1.5**x;sse1=sum((y-f(x))**2 for x,y in zip(xs,obs));sse2=sum((y-g(x))**2 for x,y in zip(xs,obs))
  add('fn',17,v,'Comparing two demand models','Residual-based model investigation','2.9',f'Demand observations at times $t=0,1,2,3$ are respectively ${obs}$. Two candidate models are $Q(t)={c}+3t+1.5t^2$ and $E(t)={c}(1.5)^t$.',[
   P('Calculate the residuals (observed minus predicted) for each model.',M('Evaluate each model at all four observed times.'),A(f'Quadratic residuals $[{", ".join(sf(y-f(x)) for x,y in zip(xs,obs))}]$.'),A(f'Exponential residuals $[{", ".join(sf(y-g(x)) for x,y in zip(xs,obs))}]$.')),
   P('Use the sums of squared residuals to choose the better fit to these data.',M('Square and add residuals for each candidate.'),A(f'$SS_Q={sf(sse1)}$.'),A(f'$SS_E={sf(sse2)}$.'),R(f'Choose {"Q" if sse1<sse2 else "E"}, because it has the smaller residual sum for these observations.')),
   P('Predict demand at time 6 using both models.',A(f'$Q(6)={sf(f(6))}$.'),A(f'$E(6)={sf(g(6))}$.')),
   P('Explain why the residual comparison alone is insufficient for a time-6 decision.',R('Time 6 is outside the observation interval.'),R('A good local fit does not establish the correct long-term growth mechanism.'),R('Further observations or contextual capacity constraints are needed.'))],{'quadraticSSE':sse1,'exponentialSSE':sse2,'quadratic6':f(6),'exponential6':g(6)})
  a=1+v;b=2;c=4;f=lambda x:a*x**3+b*x*x+c
  add('fn',18,v,'Calibrating a cubic response','Polynomial modelling','2.5',f'A response has form $f(x)=ax^3+bx^2+c$. Measurements give $f(0)=4$, $f(1)={f(1)}$ and $f(2)={f(2)}$.',[
   P('Find $a,b,c$.',A('$c=4$.'),M(f'$a+b={a+b}$ and $8a+4b={8*a+4*b}$.'),M('Solve the two simultaneous linear equations.'),A(f'$a={a}, b=2, c=4$.')),
   P('Predict $f(1.5)$ and classify the prediction.',M('Substitute into the fitted cubic.'),A(f'$f(1.5)={sf(f(1.5))}$.'),R('This is interpolation between measured input values.')),
   P('Explain why exactly fitting three observations need not establish this functional form.',R('Other function families can pass through the same three points; measurement error and additional data matter.'))],{'coefficientA':a,'coefficientB':b,'prediction1p5':f(1.5)})
  a=4+v;b=12+v;c=2;target=a+2;root=b/2-c
  add('fn',19,v,'A saturation response introduced','Rational model and domain','2.9',f'A proposed response model is $R(x)={a}+{b}/(x+2)$, used only for $x\\geq0$.',[
   P('State the contextual range and limiting response.',A(f'Range $({a},{a+b/2:g}]$.'),A(f'The response tends to {a} as $x$ increases without bound.')),
   P(f'Find the input for response {target}.',M(f'Solve ${b}/(x+2)=2$.'),A(f'$x={root:g}$.')),
   P('Find the inverse, including its contextual domain.',M('Isolate the denominator and solve for the original input.'),A(f'$R^{{-1}}(y)={b}/(y-{a})-2$.'),A(f'Domain ${a}<y\\leq {a+b/2:g}$.')),
   P('Explain why the algebraic vertical asymptote is not a reachable input here.',R('The asymptote is at $x=-2$, outside the contextual domain $x\\geq0$.'))],{'inputForTarget':root,'maximumResponse':a+b/2})
  a=80+10*v;b=4+v;cost=20;opt=(a-cost)/(2*b);maxprofit=(a-b*opt-cost)*opt
  add('fn',20,v,'Pricing within a sales model','Quadratic decision modelling','2.6',f'A shop models unit price by $p(q)={a}-{b}q$ for quantity $q\\geq0$. Unit cost is 20; fixed costs are ignored. Treat $q$ as continuous for the optimization.',[
   P('Find the physically meaningful quantity domain and write profit as a function of quantity.',A(f'$0\\leq q\\leq {sf(a/b)}$ from the nonnegative-price condition.'),M('Profit is quantity times unit margin.'),A(f'$\\Pi(q)=({a}-20)q-{b}q^2$.')),
   P('Find the profit-maximizing quantity and maximum profit.',M('Use the quadratic vertex or a numerical maximum on the allowed interval.'),A(f'$q={sf(opt)}$.'),A(f'Maximum profit {sf(maxprofit)}.')),
   P('Explain why a whole-item decision requires a further check.',R('The continuous optimum may not be an integer.'),R('Evaluate the neighbouring feasible integer quantities and select the larger profit.'))],{'continuousOptimum':opt,'maximumProfit':maxprofit})
  xs=np.array([1.,2.,3.,4.,5.]);ys=(3+v)*xs**1.4+np.array([.2,-.3,.4,-.2,.1]);ys=np.array([float(f"{z:.6f}") for z in ys]);co=np.polyfit(np.log(xs),np.log(ys),1);a=math.exp(co[1]);b=co[0];pred=a*xs**b;ss=float(sum((ys-pred)**2))
  add('fn',21,v,'Choosing a transformed regression','Power fit investigation','2.10',f'An experiment records inputs $[1,2,3,4,5]$ and outputs $[{", ".join(f"{y:.6f}" for y in ys)}]$. Fit a straight line to $(\\ln x,\\ln y)$; use the displayed outputs as the data.',[
   P('Find the log-linear regression equation and hence the power model.',M('Transform every positive input and output using natural logarithms.'),M('Regress $\\ln y$ on $\\ln x$.'),A(f'$\\ln y={sf(co[1])}+{sf(b)}\\ln x$.'),A(f'$y={sf(a)}x^{{{sf(b)}}}$; retain unrounded regression parameters.')),
   P('Calculate the sum of squared residuals on the original output scale.',M('Predict each output using the fitted power model.'),M('Subtract each prediction from the observed output and square.'),A(f'Original-scale residual sum {sf(ss)}.')),
   P('Predict the output at input 3.5 and at input 20.',A(f'At 3.5: {sf(a*3.5**b)}.'),A(f'At 20: {sf(a*20**b)}.')),
   P('Explain why the two predictions warrant different confidence and why log-scale least squares is a modelling choice.',R('Input 3.5 is interpolation, whereas 20 is substantial extrapolation.'),R('The fitted line minimizes squared errors in log output, not in original output.'),R('That choice gives a relative-error interpretation and should be checked against the experiment.'))],{'regressionIntercept':co[1],'regressionSlope':b,'coefficient':a,'originalSSE':ss,'prediction3p5':a*3.5**b,'prediction20':a*20**b})
  L=100+10*v;K=4+v;y=60;lo=59;hi=61;inv=lambda y:K*y/(L-y)
  add('fn',22,v,'Uncertain saturation inversion','Inverse sensitivity investigation','2.7',f'A sensor output is $S(x)={L}x/({K}+x)$ for concentration $x\\geq0$. A reading of 60 has uncertainty $\\pm1$ output unit.',[
   P('State the range and find the inverse.',A(f'Range $0\\leq S<{L}$.'),M('Multiply out $S(K+x)=Lx$ and collect the terms in $x$.'),A(f'$x={K}S/({L}-S)$.')),
   P('Find the concentration estimate and the interval allowed by the uncertain reading.',M('Evaluate the inverse at 60.'),A(f'Estimate {sf(inv(y))}.'),M('The inverse is increasing, so invert endpoints 59 and 61.'),A(f'Allowed concentration interval $[{sf(inv(lo))},{sf(inv(hi))}]$.')),
   P('Compare the concentrations at outputs 90% and 95% of capacity.',A(f'At 90%: {9*K}.'),A(f'At 95%: {19*K}.'),R('A five percentage point output increase more than doubles this concentration.')),
   P('Explain a measurement concern near saturation.',R('The inverse becomes very steep as the reading approaches the capacity.'),R('Small output uncertainty then produces a large concentration uncertainty.'))],{'estimate':inv(y),'lower':inv(lo),'upper':inv(hi),'at90':9*K,'at95':19*K})
  L=1000+100*v;C=9;k=.4+.02*v;N0=L/10;t=8;log=L/(1+C*math.exp(-k*t));exp=N0*math.exp(k*t)
  add('fn',23,v,'Two population forecasts','Exponential versus logistic investigation','2.9',f'Two models for a colony are $E(t)={N0:g}e^{{{k:g}t}}$ and $G(t)={L}/(1+9e^{{-{k:g}t}})$, for $t\\geq0$.',[
   P('Verify that the models have the same initial population and compare their limiting behaviours.',A(f'$E(0)=G(0)={N0:g}$.'),R('The exponential model is unbounded.'),A(f'The logistic model approaches {L}.')),
   P('Calculate both predictions after eight time units.',M('Evaluate each formula with unrounded exponential values.'),A(f'$E(8)={sf(exp)}$.'),A(f'$G(8)={sf(log)}$.')),
   P('Find when each model first reaches half the logistic capacity.',M(f'For E solve $e^{{{k}t}}=5$.'),A(f'$t_E={sf(math.log(5)/k)}$.'),M(f'For G solve $9e^{{-{k}t}}=1$.'),A(f'$t_G={sf(math.log(9)/k)}$.')),
   P('A measured late population remains close to capacity. Assess the evidence and suggest a further check.',R('It is consistent with the logistic asymptote and conflicts with indefinite exponential growth.'),R('One late observation does not establish a fixed capacity.'),R('Collect repeated late observations and investigate resource availability or migration.'))],{'exponential8':exp,'logistic8':log,'expHalfTime':math.log(5)/k,'logisticHalfTime':math.log(9)/k})
  A0=25+v;B=7+.5*v;delay=.4+.1*v;f=lambda t:A0+B*math.cos(math.pi*t/6);g=lambda t:f(t-delay)+2
  add('fn',24,v,'Delayed seasonal demand','Transformation forecast investigation','2.8',f'An old demand model is $f(t)={A0}+{B:g}\\cos(\\pi t/6)$. A changed season is modelled by $g(t)=f(t-{delay:g})+2$, with $0\\leq t\\leq12$.',[
   P('Describe the changes and state the new range.',R(f'The demand pattern is delayed by {delay:g} months.'),R('The baseline is increased by 2 units.'),A(f'New range $[{A0+2-B:g},{A0+2+B:g}]$.')),
   P('Find the time of maximum demand and the new demand at month 6.',A(f'Maximum occurs at month {delay:g}.'),M('Evaluate the shifted cosine at 6.'),A(f'$g(6)={sf(g(6))}$.')),
   P('A planner instead uses $f(t)+2$ at month 6. Calculate the prediction error and explain its cause.',M('Subtract the planner prediction from the shifted-model prediction.'),A(f'Error {sf(g(6)-(f(6)+2))} demand units.'),R('The planner adjusts the baseline but ignores the timing change.')),
   P('Explain how observations could test the two changes separately.',R('Timing of peaks and troughs tests the horizontal shift.'),R('The midpoint between maximum and minimum tests the changed baseline.'),R('Several cycles are preferable because one unusual season can distort either estimate.'))],{'shiftedMonth6':g(6),'plannerError':g(6)-(f(6)+2),'maximumTime':delay})
  a=5+v;b=2+.2*v;join=3;at=a*join;L=at+20;k=b/20;f=lambda t:a*t if t<3 else L-20*math.exp(-k*(t-3));target=L-5;time=3+math.log(4)/k
  add('fn',25,v,'Changing a production regime','Piecewise model investigation','2.9',f'A production total is $P(t)={a}t$ for $0\\leq t<3$, then $P(t)=L-20e^{{-k(t-3)}}$ for $t\\geq3$. The join is continuous. Immediately after the join the rate of increase is {b:g} units per day.',[
   P('Find $L$ using continuity.',M('Match the two values at $t=3$.'),A(f'${3*a}=L-20$.'),A(f'$L={L}$.')),
   P('Use the given rate to find $k$. The derivative of the second formula is $20ke^{-k(t-3)}$.',M('At $t=3$, the given derivative is $20k$.'),A(f'$k={k:g}$.')),
   P(f'Find when the total reaches {target} units.',M(f'Solve ${L}-20e^{{-{k}(t-3)}}={target}$ on the second branch.'),M('$e^{-k(t-3)}=1/4$.'),A(f'$t={sf(time)}$ days.')),
   P('State the long-term total and assess whether the join describes a smooth change of rate.',A(f'Long-term total {L} units.'),R(f'The left rate is {a}, whereas the right rate is {b:g}.'),R('The values join continuously but the rates differ, representing an abrupt regime change.'),R('A gradual transition would require a different joining function or additional data.'))],{'capacity':L,'k':k,'targetTime':time})
