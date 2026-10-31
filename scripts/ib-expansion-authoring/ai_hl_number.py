from ai_hl_common import *
def build():
 for v in range(4):
  a=120+15*v;d=18+2*v;n=12;total=n*(2*a+(n-1)*d)/2;cap=total-100
  add('na',1,v,'Phased recycling programme','Arithmetic investment investigation','1.2',f'A council processes {a} tonnes in month 1 and plans an increase of {d} tonnes each subsequent month. The plan lasts 12 months; the annual transport contract permits {int(cap)} tonnes.',[
   P('Write the month-$n$ model and calculate the planned month-12 amount.',M('$u_n=a+(n-1)d$.'),A(f'$u_n={a}+{d}(n-1)$.'),A(f'$u_{{12}}={a+11*d}$ tonnes.')),
   P('Calculate the annual total and determine whether the contract is adequate.',M('$S_{12}=12(2a+11d)/2$.'),A(f'Annual total {int(total)} tonnes.'),R(f'The contract is short by 100 tonnes; a larger contract is required.')),
   P('Find the largest whole-number monthly increase that satisfies the contract.',M(f'Solve $12({2*a}+11d)/2\\leq {int(cap)}$.'),A(f'$d\\leq {sf((cap/6-2*a)/11)}$.'),A(f'Largest integer increase {math.floor((cap/6-2*a)/11)} tonnes.')),
   P('Give one reason the arithmetic model may fail, and explain how actual monthly observations could improve it.',R('Limited staffing or seasonal supply can prevent a constant monthly increase.'),R('Compare observed changes or residuals against month to detect systematic departures.'),R('Refit or use a piecewise model once capacity or seasonality becomes evident.'))],{'annualTotal':total,'maximumIncrease':(cap/6-2*a)/11})
  a=65+5*v;r=1.14+.01*v;target=300;n=math.ceil(1+math.log(target/a)/math.log(r));s=a*(r**8-1)/(r-1)
  add('na',2,v,'Community seed production','Geometric sequences and threshold','1.3',f'A greenhouse produces {a} trays in its first season. Production is modelled as increasing by {100*(r-1):.0f}% each season.',[
   P('Find the total production over the first eight seasons.',M(f'$S_8={a}({r}^8-1)/({r}-1)$.'),A(f'{sf(s)} trays (model total).')),
   P('Find the first season in which production exceeds 300 trays.',M(f'Solve ${a}({r})^{{n-1}}>300$.'),A(f'$n> {sf(1+math.log(target/a)/math.log(r))}$ before integer selection.'),A(f'Season {n}; verify seasons {n-1} and {n} give {sf(a*r**(n-2))}, {sf(a*r**(n-1))}.')),
   P('Explain why extending this model indefinitely would be unreasonable.',R('The constant percentage growth eventually exceeds the greenhouse space or labour capacity.'),R('A capacity-limited model would then be needed.'))],{'sum8':s,'firstSeason':n})
  p=18000+1000*v;r=.045+.003*v;infl=.025;real=p*(1+r)**6/(1+infl)**6
  add('na',3,v,'Equipment replacement fund','Real investment value','1.4',f'A charity invests {p} currency units for six years at {100*r:g}% annual compound interest. Inflation is 2.5% annually.',[
   P('Find the nominal balance and its value in today\'s purchasing power.',M(f'Nominal balance $={p}(1+{r})^6$.'),A(f'{sf(p*(1+r)**6)} currency units.'),M('Deflate by dividing by $1.025^6$.'),A(f'Real value {sf(real)} currency units.')),
   P('Equipment costs 21000 today. Decide whether the fund will cover its inflation-adjusted cost.',M('Compare the real balance with 21000, or inflate the equipment price consistently.'),R(f'{"It will" if real>=21000 else "It will not"} cover the equipment; the real difference is {sf(real-21000)} currency units.'))],{'nominal':p*(1+r)**6,'realValue':real})
  loan=48000+2000*v;i=(.06+.004*v)/12;n=60;payment=loan*i/(1-(1+i)**-n);bal=loan*(1+i)**24-payment*((1+i)**24-1)/i
  add('na',4,v,'Electric van loan','Loan repayment and balance','1.7',f'A business borrows {loan} currency units. Interest is {1200*i:g}% nominal annually, compounded monthly. Sixty equal payments are made at month ends; no fees apply.',[
   P('Calculate the monthly repayment, retaining unrounded working.',M('Use $L=R(1-(1+i)^{-60})/i$ with the monthly rate.'),A(f'$i={i:.12g}$.'),A(f'$R={sf(payment)}$ currency units.')),
   P('Find the balance just after payment 24.',M('Accumulate the initial loan and subtract the accumulated 24-payment annuity.'),A(f'$B_{{24}}={sf(bal)}$ currency units.')),
   P('The business can pay an extra 5000 immediately after payment 24. Explain how this changes the remaining interest if regular payments continue.',R('The outstanding principal immediately falls by 5000.'),R('Future monthly interest is calculated on a smaller balance, so total interest falls.'),R('With unchanged payments, repayment finishes earlier; the final payment may be smaller.'))],{'monthlyPayment':payment,'balance24':bal})
  x=6.2+.2*v;lo=x-.05;hi=x+.05;vl=10*math.log10(lo);vh=10*math.log10(hi)
  add('na',5,v,'Sound meter precision','Bounds and logarithmic scales','1.6',f'A sound intensity ratio is recorded as {x:.1f}, correct to one decimal place. A level is defined by $L=10\\log_{{10}}I$.',[
   P('State the interval of possible intensity ratios.',A(f'${lo:.2f}\\leq I<{hi:.2f}$.')),
   P('Find the corresponding level interval and justify the endpoint order.',M('Apply the increasing logarithmic function to both bounds.'),A(f'$10\\log_{{10}}({lo:.2f})\\leq L<10\\log_{{10}}({hi:.2f})$ dB. The endpoint values are approximately {sf(vl)} and {sf(vh)} dB; retain the exact bounds for the interval.'),R('The logarithm is increasing for positive inputs.')),
   P('Explain why quoting the calculated central level to eight decimal places is misleading.',R('The input rounding permits a nonzero interval of levels.'),R('Extra displayed digits do not reduce measurement uncertainty.'))],{'lowerLevel':vl,'upperLevel':vh})
  c=6+v;root=(1+math.sqrt(1+4*math.exp(c/3)))/2
  add('na',6,v,'Chemical index inversion','Logarithm laws and domain','1.9',f'An index satisfies $3\\ln x+3\\ln(x-1)={c}$.',[
   P('State the real domain, then solve the equation.',A('$x>1$, since both logarithm arguments must be positive.'),M(f'$\\ln(x(x-1))={c}/3$.'),M(f'$x^2-x-e^{{{c}/3}}=0$.'),A(f'$x={sf(root)}$; the other quadratic root is negative and outside the domain.')),
   P('A technician combines the original logarithms as $3\\ln(2x-1)$. Explain the error.',R('The logarithm of a product is the sum of logarithms.'),A('The correct argument is $x(x-1)$, not the sum of the arguments.'))],{'admissibleRoot':root})
  scale=1.3+.1*v;mass=scale**3;area=scale**2
  add('na',7,v,'Scaling a storage capsule','Rational exponents','1.10',f'Geometrically similar capsules are made of the same material. The large capsule has {sf(mass)} times the small capsule\'s volume; use the exact ratio ${scale}^3$ in calculations.',[
   P('Find the length scale factor and surface-area ratio.',M('The length factor is the cube root of the volume ratio.'),A(f'Length factor ${scale}$.'),M('Square the length factor for area.'),A(f'Area ratio ${area:g}$.')),
   P('A designer claims that multiplying volume by $k$ multiplies area by $k^{3/2}$. Correct this claim.',R('Area scales as length squared and volume as length cubed.'),A('The correct area multiplier is $k^{2/3}$.'))],{'lengthScale':scale,'areaRatio':area})
  h=2.5+.2*v;r=.65+.03*v;dist=h+2*h*r/(1-r);k=math.ceil(math.log(.01/h)/math.log(r))
  add('na',8,v,'Instrument drop test','Infinite geometric distance','1.11',f'A test ball is dropped from {h:g} m. Each rebound reaches {r:g} times the preceding maximum height. Ignore air resistance during each flight.',[
   P('Find the total distance in the idealized infinite-bounce model.',M(f'Distance $={h}+2({h})({r}+{r}^2+\\cdots)$.'),M('Use a convergent geometric sum because $0<r<1$.'),A(f'Total distance {sf(dist)} m.')),
   P('Find the first rebound whose maximum height is less than 1 cm.',M(f'Solve ${h}({r})^n<0.01$.'),A(f'First rebound {k}, checking {sf(h*r**(k-1))} m and {sf(h*r**k)} m.')),
   P('Explain why infinite rebounds do not imply infinite total distance.',R('The rebound heights form a convergent geometric series.'),R('Its ratio has magnitude less than one.'))],{'totalDistance':dist,'firstSmallRebound':k})
  a=900+100*v;r=.6+.03*v;budget=a/(1-r);n=math.ceil(math.log(.05)/math.log(r))
  add('na',9,v,'Restoration grant cascade','Infinite series investigation','1.11',f'A restoration programme spends {a} currency units at stage 1 and {r:g} times the preceding expenditure at each later stage.',[
   P('Find the idealized total expenditure and the amount spent through stage 5.',M('Use $S_\\infty=a/(1-r)$.'),A(f'Total {sf(budget)}.'),M('Use $S_5=a(1-r^5)/(1-r)$.'),A(f'Five-stage sum {sf(a*(1-r**5)/(1-r))}.')),
   P('Find the least number of stages needed to spend more than 95% of the idealized total.',M('The unspent fraction after $n$ stages is $r^n$.'),M('Solve $r^n<0.05$.'),A(f'Least $n={n}$; neighbouring fractions {sf(r**(n-1))} and {sf(r**n)}.')),
   P('The ratio might be 0.02 larger than assumed. Recalculate the total and the percentage increase.',M(f'Replace $r$ by ${r+.02:g}$.'),A(f'New total {sf(a/(1-r-.02))}.'),A(f'Increase {sf(100*((1-r)/(1-r-.02)-1))}%.')),
   P('Explain two limitations of budgeting with an infinite sum.',R('Real programmes have finitely many stages or a minimum transaction size.'),R('The ratio may change with labour prices or project conditions.'))],{'infiniteSum':budget,'sum5':a*(1-r**5)/(1-r),'stage95':n,'perturbedTotal':a/(1-r-.02)})
  z=complex(3+v,4);w=complex(2,-1-v);q=z/w
  add('na',10,v,'Complex signal division','Cartesian complex arithmetic','1.12',f'Two signal coefficients are $z={z.real:g}+4i$ and $w=2-{1+v}i$.',[
   P('Find $z/w$ in Cartesian form, showing the use of a conjugate.',M(f'Multiply numerator and denominator by $2+{1+v}i$.'),A(f'Denominator ${4+(1+v)**2}$.'),A(f'$z/w={sf(q.real)}+({sf(q.imag)})i$.')),
   P('Find the modulus and principal argument of $z/w$, in radians.',M('Use modulus and two-coordinate argument, accounting for the quadrant.'),A(f'Modulus {sf(abs(q))}.'),A(f'Principal argument {sf(math.atan2(q.imag,q.real))} radians.'))],{'quotientReal':q.real,'quotientImag':q.imag,'modulus':abs(q),'argument':math.atan2(q.imag,q.real)})
  a=2+v;b=3;disc=-4*b*b
  add('na',11,v,'No real calibration setting','Quadratic roots and Argand interpretation','1.12',f'A calibration polynomial is $f(x)=x^2-{2*a}x+{a*a+b*b}$.',[
   P('Solve $f(x)=0$ over the complex numbers.',M(f'Discriminant $={4*a*a}-4({a*a+b*b})=-36$.'),M('Apply the quadratic formula with $\\sqrt{-36}=6i$.'),A(f'$x={a}\\pm3i$.')),
   P('State the minimum value of $f$ on the real line and relate this to the roots.',A(f'$f(x)=(x-{a})^2+9$.'),A('The real minimum is 9, so the real graph has no intercepts.')),
   P('Describe the symmetry and distance from the origin of the two Argand points.',R('They are conjugate points reflected in the real axis.'),A(f'Both are {sf(math.sqrt(a*a+9))} from the origin.'))],{'rootReal':a,'rootImagMagnitude':3,'rootModulus':math.sqrt(a*a+9)})
  a=4+v;b=3+v;phi=.6+.1*v;z=a+b*complex(math.cos(phi),math.sin(phi));amp=abs(z);phase=math.atan2(z.imag,z.real)
  add('na',12,v,'Combining vibration signals','Complex phasor addition','1.13',f'Two vibrations are $u(t)={a}\\cos(2t)$ and $v(t)={b}\\cos(2t+{phi:g})$.',[
   P('Use complex amplitudes to write $u(t)+v(t)=R\\cos(2t+\\alpha)$ with $R>0$ and $-\\pi<\\alpha\\leq\\pi$.',M(f'Add amplitudes ${a}+{b}e^{{{phi:g}i}}$.'),A(f'Cartesian result {sf(z.real)}+{sf(z.imag)}i.'),A(f'$R={sf(amp)}$.'),A(f'$\\alpha={sf(phase)}$ radians.')),
   P('Find the first maximum at a time $t\\geq0$.',M('A maximum requires $2t+\\alpha=2k\\pi$.'),A(f'$t={sf((2*math.pi-phase)/2)}$ for $k=1$.')),
   P('Explain why adding the two amplitudes gives an incorrect resultant amplitude.',R('The signals have different phases, so their maxima do not coincide.'),R('The complex amplitudes must be added as vectors.'))],{'resultantAmplitude':amp,'resultantPhase':phase,'firstMaximum':(2*math.pi-phase)/2})
  r=1.2+.1*v;theta=.4+.05*v;power=5;z=r**power*complex(math.cos(power*theta),math.sin(power*theta))
  add('na',13,v,'Repeated signal amplification','Integer powers in polar form','1.13',f'A signal is multiplied five times by $z={r:g}e^{{{theta:g}i}}$.',[
   P('Find $z^5$ in exponential and Cartesian form.',M('Raise the modulus to the fifth power and multiply the argument by five.'),A(f'$z^5={sf(r**5)}e^{{{5*theta:g}i}}$.'),A(f'Cartesian form ${sf(z.real)}+{sf(z.imag)}i$.')),
   P('Explain the geometric effects of one multiplication by $z$.',R(f'It scales distance from the origin by {r:g}.'),R(f'It rotates anticlockwise by {theta:g} radians.')),
   P('Determine whether the repeated signal remains bounded as the number of multiplications increases.',R(f'It is unbounded since the modulus multiplier {r:g} is greater than one.'))],{'powerReal':z.real,'powerImag':z.imag,'powerModulus':r**5})
  x=2+v;y=3;z=complex(x,y);q=z*1j
  diag=plot(points=[(x,y,'P')],xmin=-6,xmax=6,ymin=-6,ymax=6,xlabel='Re',ylabel='Im',equal=True)
  private=plot(points=[(x,y,'P'),(q.real,q.imag,'Q')],xmin=-6,xmax=6,ymin=-6,ymax=6,xlabel='Re',ylabel='Im',equal=True)
  add('na',14,v,'A rotated Argand point','Complex multiplication and geometry','1.12','The Argand diagram shows the coefficient $z$ at point P. Let $w=iz$.',[
   P('Read $z$ from the diagram and calculate $w$.',A(f'$z={x}+3i$.'),M('Multiply by $i$, using $i^2=-1$.'),A(f'$w=-3+{x}i$.')),
   P('Plot $w$ and describe the mapping from $z$ to $w$.',A(f'Point Q is $(-3,{x})$.'),R('A rotation of 90 degrees anticlockwise about the origin.')),
   P('Calculate the distance between the two complex points.',M('Use the modulus $|w-z|$.'),A(f'Distance {sf(abs(q-z))}.'))],{'distance':abs(q-z)},diagram=diag,private=private)
  a=12+v;b=8+v;T=np.array([[2,3],[4,1]]);prices=np.array([a,b]);revenue=T@prices
  add('na',15,v,'Festival sales receipts','Matrix systems in context','1.14',f'Two packages contain 2 adult and 3 child tickets, or 4 adult and 1 child ticket. Their revenues are {int(revenue[0])} and {int(revenue[1])} currency units.',[
   P('Write a matrix equation for the two unknown ticket prices.',A(f'${mat(T.tolist())}{vec(["a","c"])}={vec(revenue.tolist())}$.'),R('Columns represent adult and child prices in that order.')),
   P('Use an inverse matrix to find both prices.',M('Calculate the nonzero determinant $2-12=-10$.'),M('Multiply the revenue vector by the inverse coefficient matrix.'),A(f'Adult price {a}; child price {b}.')),
   P('The first receipt rises by 5 while the second receipt is unchanged. Find the changes in the two inferred prices.',M('Apply the same inverse to $(5,0)^T$.'),A('Adult price changes by -0.5; child price by 2.'))],{'adultPrice':a,'childPrice':b,'revenue1':int(revenue[0]),'revenue2':int(revenue[1])})
  T=np.array([[1,2,1],[2,1,3],[3,2,2]]);sol=np.array([4+v,5+v,6+v]);rhs=T@sol
  add('na',16,v,'Blending three nutrients','Three-variable matrix model','1.14',f'Three concentrates have nutrient columns in $A={mat(T.tolist())}$. A blend must supply $b={vec(rhs.tolist())}$ nutrient units; amounts are measured in litres.',[
   P('Explain the equation $Ax=b$ and find the required amounts.',R('The vector $x$ lists the three concentrate volumes, in column order.'),M('Use a numerical inverse or simultaneous-equation solver.'),A(f'$x={vec(sol.tolist())}$ litres.')),
   P('Check the second nutrient target and state one physical constraint on this solution.',M(f'Calculate $2({sol[0]})+{sol[1]}+3({sol[2]})$.'),A(f'The target is {rhs[1]} units.'),R('Every volume must be nonnegative; this solution satisfies that constraint.'))],{'volume1':int(sol[0]),'volume2':int(sol[1]),'volume3':int(sol[2]),'determinant':float(np.linalg.det(T))})
  p=1+v;K=np.array([[2,1],[1,1]]);x=np.array([p,5+v]);y=K@x
  add('na',17,v,'Two-symbol archive code','Matrix encoding and decoding','1.14',f'A pair of symbols is represented by a column vector $x$. It is encoded as $y=Kx$, where $K={mat(K.tolist())}$. The received vector is ${vec(y.tolist())}$.',[
   P('Find $K^{-1}$ and decode the received vector.',M('The determinant is $2(1)-1(1)=1$.'),A(f'$K^{{-1}}={mat([[1,-1],[-1,2]])}$.'),A(f'$x={vec(x.tolist())}$.')),
   P('An error adds $(1,0)^T$ to the received vector. Determine the error in the decoded symbols.',M('Apply $K^{-1}$ to the error vector.'),A('The decoded error is $(1,-1)^T$.')),
   P('Explain why knowledge of the encoding matrix makes this system unsuitable for secure encryption.',R('Anyone knowing $K$ can invert it and recover every symbol pair.'))],{'decoded1':int(x[0]),'decoded2':int(x[1])})
  k=4+v;det=2*k-3;T=[[2,3],[1,k]];x=[7+v,2+v];rhs=np.array(T)@x
  add('na',18,v,'Sensitivity in a survey model','Inverse matrix and perturbation','1.14',f'A survey model is $Ax=b$, with $A={mat(T)}$ and $b={vec(rhs.tolist())}$.',[
   P('Find the determinant and solve for $x$.',A(f'$\\det A={det}\\ne0$.'),M('Use $x=A^{-1}b$.'),A(f'$x={vec(x)}$.')),
   P('If only the second entry of $b$ increases by 1, find the changes in $x$.',M(f'$\\Delta x=A^{{-1}}(0,1)^T$.'),A(f'$\\Delta x={vec([f"-3/{det}",f"2/{det}"])}$.')),
   P('Explain why rounding $b$ before solving can change the inferred values.',R('An input perturbation is multiplied by the inverse matrix.'),R('The resulting output perturbation need not have the same size or direction.'))],{'determinant':det,'change1':-3/det,'change2':2/det})
  a=3+v;b=1;T=[[a,b],[b,a]]
  add('na',19,v,'Coupled production modes','Eigenvalues and eigenvectors','1.15',f'A discrete production model uses $A={mat(T)}$.',[
   P('Find the characteristic polynomial and both eigenvalues.',M(f'$\\det(A-\\lambda I)=({a}-\\lambda)^2-1$.'),A(f'Eigenvalues ${a+1}$ and ${a-1}$.')),
   P('Find a corresponding eigenvector for each eigenvalue.',M('Solve $(A-\\lambda I)v=0$ for each eigenvalue.'),A(f'For {a+1}, take $(1,1)^T$.'),A(f'For {a-1}, take $(1,-1)^T$.')),
   P('For a nonnegative initial state with nonzero total, explain which mode dominates after many steps.',R(f'The eigenvalue {a+1} has the larger modulus.'),R('Its $(1,1)^T$ mode grows fastest, so the two components become approximately equal in ratio.'),R('The difference mode grows more slowly than the total mode.'))],{'eigenvalue1':a+1,'eigenvalue2':a-1})
  l1=1.1+.02*v;l2=.7;A0=np.array([[(l1+l2)/2,(l1-l2)/2],[(l1-l2)/2,(l1+l2)/2]]);x=np.array([80+10*v,40]);xn=np.linalg.matrix_power(A0,10)@x
  add('na',20,v,'Two linked populations','Diagonalization investigation','1.15',f'Two populations obey $s_{{n+1}}=As_n$, with $A={mat([[round(z,4) for z in row] for row in A0])}$ and $s_0={vec(x.tolist())}$. Fractions of individuals are interpreted as expected counts.',[
   P('Show that $(1,1)^T$ and $(1,-1)^T$ are eigenvectors, and find the eigenvalues.',M('Multiply each proposed eigenvector by $A$.'),A(f'Row sum gives eigenvalue ${l1:g}$.'),A('Row difference gives eigenvalue $0.7$.')),
   P('Give matrices $P,D$ such that $A=PDP^{-1}$, then express $A^{10}$.',A(f'$P={mat([[1,1],[1,-1]])}$.'),A(f'$D={mat([[l1,0],[0,l2]])}$.'),M('$A^{10}=PD^{10}P^{-1}$.'),A(f'$D^{{10}}={mat([[sf(l1**10),0],[0,sf(l2**10)]])}$, retain exact powers when multiplying.')),
   P('Calculate the expected populations after ten steps.',M('Apply the power matrix to the unrounded initial state.'),A(f'$s_{{10}}={vec([sf(z) for z in xn])}$.')),
   P('Discuss the long-term ratio and the realism of this model.',R('The ratio tends to 1:1 because the symmetric mode dominates.'),R(f'The total grows without bound because {l1:g}>1.'),R('Finite resources eventually invalidate a constant matrix model.'))],{'population10a':xn[0],'population10b':xn[1],'dominantEigenvalue':l1})
  r=.72+.03*v;c=90+10*v;u0=100;eq=c/(1-r);u5=eq+(u0-eq)*r**5
  add('na',21,v,'Repeated water treatment','Affine recurrence investigation','1.11',f'A treatment tank retains fraction {r:g} of its contaminant each hour, then receives {c} mg from an inflow. Thus $u_{{n+1}}={r}u_n+{c}$, with $u_0=100$ mg.',[
   P('Calculate $u_1,u_2$ and explain why the sequence is not geometric.',A(f'$u_1={r*100+c:g}$ mg.'),A(f'$u_2={r*(r*100+c)+c:g}$ mg.'),R('The additive inflow means successive ratios are not constant.')),
   P('Find the equilibrium and show that $u_n-L=(u_0-L)r^n$.',M('Solve $L=rL+c$.'),A(f'$L={sf(eq)}$ mg.'),M('Subtract $L$ from the recurrence, obtaining $u_{n+1}-L=r(u_n-L)$.'),A('The deviations form a geometric sequence.')),
   P('Find $u_5$ and the limiting contaminant amount.',A(f'$u_5={sf(u5)}$ mg.'),R('$|r|<1$, so the deviation tends to zero.'),A(f'Limit {sf(eq)} mg.')),
   P('The safe equilibrium is 250 mg. Find the largest permitted hourly inflow for this retention fraction.',M('Require $c/(1-r)\\leq250$.'),A(f'$c\\leq {sf(250*(1-r))}$ mg per hour.'))],{'equilibrium':eq,'amount5':u5,'safeInflow':250*(1-r)})
  a=.8-.02*v;b=.15+.01*v;T=np.array([[a,b],[1-a,1-b]]);x=np.array([600,400]);x8=np.linalg.matrix_power(T,8)@x;eq=b/(1-a+b)
  add('na',22,v,'Mobility membership transfer','Matrix powers and invariant state','1.15',f'Each month members choose service A or B. The column transition matrix is $T={mat([[round(z,4) for z in row] for row in T])}$. Initially 600 use A and 400 use B; no member enters or leaves the system.',[
   P('Explain the entry in row 1, column 2, then calculate the state after one month.',R(f'A B-user has probability {b:g} of choosing A next month.'),M('Use $s_1=Ts_0$ with the given column convention.'),A(f'$s_1={vec([sf(z) for z in T@x])}$.')),
   P('Find the eigenvalues and explain the significance of the eigenvalue 1.',M('Use the characteristic polynomial or a matrix solver.'),A(f'Eigenvalues 1 and {sf(a-b)}.'),R('The eigenvalue 1 corresponds to a stationary distribution with total membership preserved.')),
   P('Calculate the expected state after eight months and the long-term fraction using A.',M('Use $T^8s_0$ without rounding intermediate powers.'),A(f'$s_8={vec([sf(z) for z in x8])}$.'),M('Solve $p=ap+b(1-p)$.'),A(f'Long-term A fraction {sf(eq)}.')),
   P('State two assumptions needed to use the long-term prediction.',R('The transition probabilities remain constant.'),R('Each next choice depends on the current service through the same transition model, with membership closed.'))],{'state8a':x8[0],'state8b':x8[1],'stationaryA':eq},scope='1.15 matrix powers linked with 4.19 Markov chains')
  deposit=180+20*v;i=.004+.0002*v;n=120;fv=deposit*((1+i)**n-1)/i;target=35000;needed=target*i/((1+i)**n-1)
  add('na',23,v,'A bursary savings decision','Annuity and inflation investigation','1.7',f'A parent deposits {deposit} currency units at the end of each month for 120 months. The account earns a monthly effective rate {100*i:g}%. The target is 35000 at month 120.',[
   P('Explain the timing of the first and last deposits, then calculate the accumulated balance.',R('The first deposit earns 119 months of interest.'),R('The last deposit earns no interest before the valuation.'),M('Use $F=R((1+i)^{120}-1)/i$.'),A(f'$F={sf(fv)}$.')),
   P('Find the minimum equal monthly deposit that reaches the target, rounded up to cents.',M('Rearrange the annuity equation for $R$.'),A(f'Unrounded monthly deposit {needed:.10f}.'),A(f'Minimum deposit {math.ceil(needed*100)/100:.2f}.')),
   P('The target represents a cost of 28000 today. Find the annual inflation rate that would make this cost exactly 35000 in ten years.',M('$28000(1+j)^{10}=35000$.'),A(f'$j={sf(100*((35000/28000)**.1-1))}$% per year.')),
   P('Explain two reasons the computed minimum deposit may not guarantee the bursary.',R('The interest rate may change during the ten years.'),R('The actual education cost may rise at a different rate from the assumed inflation.'),R('Fees or missed payments reduce the accumulated balance.'))],{'futureValue':fv,'requiredDeposit':needed,'inflationPercent':100*((35000/28000)**.1-1)})
  u=1000+100*v;r=.91+.01*v;threshold=400;n=math.ceil(math.log(threshold/u)/math.log(r));rhi=r+.005;nhi=math.ceil(math.log(threshold/u)/math.log(rhi))
  add('na',24,v,'Decommissioning uncertainty','Geometric threshold sensitivity','1.3',f'A pollutant mass is {u} kg immediately after a spill. At the end of each year it is multiplied by {r:g}. A site reopens only when the mass is at most 400 kg.',[
   P('Write the mass model and find the first reopening year.',A(f'$M_n={u}({r})^n$.'),M('Solve $M_n\\leq400$ and check adjacent integers.'),A(f'Year {n}; adjacent masses {sf(u*r**(n-1))}, {sf(u*r**n)} kg.')),
   P('The multiplier may be as large as '+f'{rhi:g}. Recalculate the conservative reopening year.',M(f'Use ${u}({rhi})^n\\leq400$.'),A(f'Year {nhi}.'),R('A larger retention multiplier slows removal, so this is the conservative case.')),
   P('Calculate the extra years of closure and discuss the sensitivity.',A(f'{nhi-n} additional years.'),R('Repeated compounding magnifies a small change in the annual multiplier.'),R('A decision should use the uncertainty range rather than only the central estimate.')),
   P('Give a practical check before reopening.',R('Measure actual remaining mass or concentration using a representative monitoring plan.'),R('Check that the measured quantity and legal threshold use compatible units and exposure assumptions.'),R('Update the model if observed removal differs systematically.'))],{'reopenYear':n,'conservativeYear':nhi,'massBefore':u*r**(n-1),'massAt':u*r**n})
  rho=1.04+.01*v;eta=.6;A0=np.array([[(rho+eta)/2,(rho-eta)/2],[(rho-eta)/2,(rho+eta)/2]]);harvest=1-1/rho
  add('na',25,v,'Sustainable linked harvest','Eigenvalue control investigation','1.15',f'A two-region resource follows $s_{{n+1}}=As_n$, where $A={mat([[round(z,4) for z in row] for row in A0])}$. After natural growth, a fixed fraction $h$ of each regional amount is removed.',[
   P('Write the new transition matrix and find its eigenvalues in terms of $h$.',A('The controlled matrix is $(1-h)A$.'),M('Scalar multiplication scales each eigenvalue.'),A(f'Eigenvalues $(1-h){rho:g}$ and $(1-h)0.6$.')),
   P('Find the harvest fraction for which the dominant eigenvalue is exactly 1.',M(f'Solve $(1-h){rho}=1$.'),A(f'$h={sf(harvest)}$, or {sf(100*harvest)}%.')),
   P('Explain the long-term behaviour when $h$ is slightly below and slightly above this value.',R('Below this value, the dominant eigenvalue exceeds 1, so a positive symmetric component grows.'),R('Above this value, both eigenvalue magnitudes are below 1 and amounts tend to zero.'),R('At the threshold the symmetric component remains while the difference component decays.')),
   P('Initially $s_0=(120,80)^T$. Find the limiting state at the threshold and discuss one limitation.',M('Decompose the state as $100(1,1)^T+20(1,-1)^T$.'),A('The limiting state is $(100,100)^T$.'),R('The model permits fractional amounts and assumes constant reproduction and movement, which may fail at low stocks.'),R('A dominant eigenvalue of 1 is a mathematical balance, not a guarantee against random depletion.'))],{'dominantEigenvalue':rho,'harvestFraction':harvest,'controlledOtherEigenvalue':eta/rho})
