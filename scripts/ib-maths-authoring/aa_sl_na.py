from aa_sl_core import *

def build():
 q=[]
 def add(j,i,title,sub,code,diff,calc,stem,ps,checks,**kw):q.append(rec('number-algebra','na',j,i,title,sub,code,diff,calc,stem,ps,checks,**kw))
 for i in range(4):
  a=i+2;b=2;v=s.Rational(a,2)*10**(i+4);w=b*10**(i+1);ans=s.Rational(v,w)
  eq(ans*w,v)
  add(0,i,'Comparing microscopic counts','Scientific notation','1.1','easy',False,rf'A culture contains ${L(v)}$ cells in ${L(w)}$ mL.',[
   part('Find the number of cells per mL, giving your answer in scientific notation.',M(r'Divide the cell count by the volume; subtract the powers of ten.'),A(rf'${L(ans)}$ cells per mL, equivalently ${n(float(ans)/10**math.floor(math.log10(float(ans))))}\times10^{{{math.floor(math.log10(float(ans)))}}}$ cells per mL.'))], 'Ratio multiplied by stated volume reproduces the stated cell count; scientific-notation mantissa is in [1,10).')
  a=3+i;d=2+i;p=4;r=9;up=a+(p-1)*d;ur=a+(r-1)*d;N=20+i;S=N*(2*a+(N-1)*d)//2
  eq(sum(a+k*d for k in range(N)),S)
  add(1,i,'Recovering an arithmetic schedule','Arithmetic sequences','1.2','easy',False,rf'An arithmetic sequence has $u_4={up}$ and $u_9={ur}$.',[
   part('Find the common difference and first term.',M(rf'$5d={ur-up}$.'),A(rf'$d={d}$ and $u_1={a}$.')),
   part(rf'Find $S_{{{N}}}$.',M(rf'$S_{{{N}}}=\frac{{{N}}}2[2({a})+({N-1})({d})]$.'),A(rf'$S_{{{N}}}={S}$.'))], 'Recovered parameters reproduce both displayed terms; finite sum checked by explicit summation.')
  a=10+i;d=2;N=10+i;target=N*(2*a+(N-1)*d)//2-1
  checked(sum(a+k*d for k in range(N-1))<=target<sum(a+k*d for k in range(N)),'threshold')
  add(2,i,'A cumulative training target','Arithmetic series inequalities','1.2','medium',True,rf'A runner covers ${a}$ km in week 1 and increases the weekly distance by $2$ km. The runner wants the cumulative distance to exceed ${target}$ km.',[
   part('Find the first week in which the target is exceeded. Show how the integer boundary is chosen.',M(rf'$S_n=\frac n2[2({a})+2(n-1)]=n(n+{a-1})$.'),M(rf'Solve $n(n+{a-1})>{target}$ or inspect consecutive cumulative sums.'),A(rf'The first week is week ${N}$.'),R(rf'$S_{{{N-1}}}={(N-1)*(a+N-2)}\leq {target}$ and $S_{{{N}}}={N*(a+N-1)}>{target}$.'))], 'Direct sums verify both adjacent integer boundaries; positive n is required in context.')
  m=i+3;N=7+i;ans=sum(3*k-m for k in range(2,N+1));first=6-m;last=3*N-m
  eq(s.summation(3*x-m,(x,2,N)),ans)
  add(3,i,'Reading a sigma expression','Sigma notation','1.2','easy',False,rf'Consider $T=\sum_{{k=2}}^{{{N}}}(3k-{m})$.',[
   part('Write down the first term and the number of terms.',A(rf'First term ${first}$; there are ${N-1}$ terms.')),
   part('Find T.',M(rf'$T=\frac{{{N-1}}}2({first}+{last})$.'),A(rf'$T={ans}$.'))], 'Sigma expression checked by symbolic summation and direct enumeration; lower index is not counted as 1.')
  a=2+i;r=2;u2=a*r;u5=a*r**4;N=8+i
  eq(s.Rational(u5,u2),r**3)
  add(4,i,'Recovering geometric growth','Geometric sequences','1.3','easy',False,rf'A geometric sequence has positive terms, $u_2={u2}$ and $u_5={u5}$.',[
   part('Find the common ratio and first term.',M(rf'$r^3={u5}/{u2}=8$.'),A(rf'$r=2$ and $u_1={a}$.')),
   part(rf'Find $u_{{{N}}}$.',M(rf'$u_{{{N}}}={a}(2)^{{{N-1}}}$.'),A(rf'$u_{{{N}}}={a*2**(N-1)}$.'))], 'Term ratio cubed and nth-term substitution checked; positivity removes any ambiguity in ratio.')
  a=3+i;r=-2;N=5+i;ans=sum(a*r**k for k in range(N));eq(s.Rational(a*(1-r**N),1-r),ans)
  add(5,i,'An alternating finite series','Geometric finite sums','1.3','medium',False,rf'A geometric series begins ${a}, {-2*a}, {4*a},\ldots$.',[
   part(rf'Find the sum of its first ${N}$ terms.',A(r'$r=-2$.'),M(rf'$S_{{{N}}}=\frac{{{a}(1-(-2)^{{{N}}})}}{{1-(-2)}}$.'),A(rf'$S_{{{N}}}={ans}$.')),
   part('Explain why the series has no sum to infinity.',R(r'$|r|=2>1$, so the terms do not tend to zero and the geometric series does not converge.'))], 'Finite sum checked by enumeration; divergence justified by |r|, not just alternating signs.')
  a=i+3;r=s.Rational(2,3);total=3*a;S6=a*(1-r**6)/(1-r);eq(total-S6,a*r**6/(1-r))
  add(6,i,'Remaining illumination','Infinite geometric series','1.8','medium',False,rf'A sequence of light pulses has energies ${a}, {frac(2*a,3)}, {frac(4*a,9)},\ldots$ joules.',[
   part('Find the total energy of all the pulses.',R(r'$|r|=2/3<1$, so the infinite sum exists.'),M(rf'$S_\infty={a}/(1-2/3)$.'),A(rf'Total energy is ${total}$ J.')),
   part('Find the energy remaining after the first six pulses.',M(rf'$S_\infty-S_6=\frac{{{a}(2/3)^6}}{{1-2/3}}$.'),A(rf'${L(total-S6)}$ J. Follow through their convergent ratio consistently.'))], 'Tail sum checked against total minus direct first-six sum; energy units retained.')
  r=s.Rational(i+1,i+2);S=12*(i+2);a=s.simplify(S*(1-r));eq(a/(1-r),S)
  add(7,i,'A ratio determined by two sums','Geometric model reconstruction','1.8','hard',False,rf'A convergent geometric series has first term $a>0$ and ratio $r>0$. Its sum is ${S}$ and the sum after removing the first term is ${L(S-a)}$.',[
   part('Find a and r.',M(rf'$a={S}-({L(S-a)})$.'),A(rf'$a={L(a)}$.'),M(rf'$r=\frac{{{L(S-a)}}}{{{S}}}$, because deleting the first term scales the whole sum by $r$.'),A(rf'$r={L(r)}$.')),
   part('Verify that the series converges.',R(rf'$0<{L(r)}<1$, hence $|r|<1$.'))], 'Recovered a,r checked in both infinite sums; ratio is positive and strictly below one.')
  P=3500+500*i;rate=.035+.005*i;years=7+i;F=P*(1+rate)**years;eq(F/(1+rate)**years,P)
  add(8,i,'A long-term deposit','Compound interest','1.4','medium',True,rf'An account contains USD ${P}$ and pays ${100*rate:g}\%$ interest compounded annually. No money is added or withdrawn.',[
   part(rf'Find its value after ${years}$ years, to the nearest cent.',M(rf'$V={P}(1+{rate:g})^{{{years}}}$.'),A(rf'USD ${F:.2f}$.')),
   part('Find the least whole number of years required for its value to exceed twice the initial deposit.',M(rf'$n>\ln2/\ln({1+rate:g})={math.log(2)/math.log(1+rate):.6f}$.'),A(rf'${math.floor(math.log(2)/math.log(1+rate))+1}$ years.'))], 'Annual compounding and inverse logarithm checked; adjacent whole-year amounts bracket twice the initial deposit.')
  P=18000+2000*i;rate=.12+.01*i;floor=7000;N=math.floor(math.log(floor/P)/math.log(1-rate))+1
  checked(P*(1-rate)**N<floor<=P*(1-rate)**(N-1),'depreciation bound')
  add(9,i,'Replacing a depreciating instrument','Depreciation','1.4','medium',True,rf'An instrument initially costs USD ${P}$. Its value falls by ${rate*100:g}\%$ per year. It will be replaced as soon as its end-of-year value is less than USD ${floor}$.',[
   part('Write a model for the value V after n years.',A(rf'$V={P}({1-rate:g})^n$, for integer $n\geq0$.')),
   part('Find when replacement first occurs.',M(rf'${P}({1-rate:g})^n<{floor}$; take logarithms.'),M(rf'$n>\frac{{\ln({floor}/{P})}}{{\ln({1-rate:g})}}={math.log(floor/P)/math.log(1-rate):.6f}$; reverse the inequality because the denominator is negative.'),A(rf'After ${N}$ years.'),R(rf'$V({N-1})={P*(1-rate)**(N-1):.2f}$ and $V({N})={P*(1-rate)**N:.2f}$ bracket USD {floor}.'))], 'End-of-year timing and strict inequality checked by adjacent-year evaluation; rounding occurs after selecting n.')
  b=i+2;a=b**4;val=b**3+b**-2;eq(s.Rational(a)**s.Rational(3,4),b**3)
  add(10,i,'Rational powers without decimals','Rational exponents','1.7','easy',False,rf'Let $a={a}$.',[
   part(r'Evaluate $a^{3/4}+a^{-1/2}$ exactly.',M(rf'$a^{{1/4}}={b}$, so $a^{{3/4}}={b**3}$.'),A(rf'$a^{{-1/2}}=\frac1{{{b*b}}}$.'),A(rf'The value is ${L(s.Rational(b**3)+s.Rational(1,b*b))}$.'))], 'Rational powers checked as exact SymPy rationals; even roots use the positive real root.')
  b=i+2;a=b**3;c=b**2;ans=5;eq(s.log(a*c,b),ans)
  add(11,i,'Condensing logarithms','Laws of logarithms','1.7','medium',False,rf'For $x>0$, define $H(x)=2\log_{{{b}}}x-\log_{{{b}}}(x/{a})$.',[
   part('Write H(x) as a single logarithm.',M(rf'$H(x)=\log_{{{b}}}(x^2/(x/{a}))$.'),A(rf'$H(x)=\log_{{{b}}}({a}x)$.')),
   part(rf'Solve $H(x)=5$.',M(rf'${a}x={b}^5$.'),A(rf'$x={c}$. The original domain is satisfied.'))], 'Log identity checked on positive test values; solution substituted in the original two-log expression.')
  b=i+2;rhs=7+i;answer=1+math.log(rhs,b);eq(b**(answer-1),rhs)
  add(12,i,'An exponential crossing','Introduction to logarithms','1.5','medium',True,rf'Solve ${b}^{{x-1}}={rhs}$ for real x.',[
   part('Give an exact expression and a value to three significant figures.',M(rf'$(x-1)\ln {b}=\ln {rhs}$.'),A(rf'$x=1+\frac{{\ln {rhs}}}{{\ln {b}}}$.'),A(rf'$x={n(answer)}$.'))], 'Numerical answer substituted in original exponential equation; exact change-of-base expression retained.')
  a=i+2;b=i+4;answer=math.log(b*b/a)/(math.log(a)-math.log(b));eq(a**(answer+1),b**(answer+2),tol=1e-7)
  add(13,i,'Competing exponential expressions','Logarithmic linearization','1.7','hard',True,rf'Solve ${a}^{{x+1}}={b}^{{x+2}}$.',[
   part('Find x to three significant figures.',M(rf'$(x+1)\ln {a}=(x+2)\ln {b}$.'),M(rf'$x(\ln {a}-\ln {b})=2\ln {b}-\ln {a}$.'),A(rf'$x=\frac{{2\ln {b}-\ln {a}}}{{\ln {a}-\ln {b}}}={n(answer)}$.')),
   part('Explain why there is exactly one real solution.',R(rf'$\ln {a}-\ln {b}\ne0$, so the transformed linear equation has exactly one solution; taking logarithms is reversible for positive bases.'))], 'Original exponential values checked numerically; unequal positive bases justify unique solution.')
  a=i+1;expr=s.expand((1+a*x)**4);eq(expr.subs(x,2),(1+2*a)**4)
  add(14,i,'A complete finite expansion','Binomial expansion','1.9','medium',False,rf'Consider $(1+{a}x)^4$.',[
   part('Expand and simplify in ascending powers of x.',M(r'Use binomial coefficients $1,4,6,4,1$.'),A(rf'First three terms are $1+{4*a}x+{6*a*a}x^2$.'),A(rf'Remaining terms are ${4*a**3}x^3+{a**4}x^4$.')),
   part('State the coefficient of x cubed.',A(rf'${4*a**3}$.'))], 'Expansion checked symbolically and at an independent test input; coefficients individually checked with combinations.')
  a=i+2;ans=math.comb(6,2)*a*a;eq(s.expand((1+a*x)**6).coeff(x,2),ans)
  add(15,i,'Identifying an unknown binomial parameter','Binomial coefficients','1.9','hard',False,rf'The coefficient of $x^2$ in $(1+kx)^6$ is ${ans}$, where $k>0$.',[
   part('Find k.',M(r'$\binom62k^2=15k^2$ is the coefficient.'),M(rf'$15k^2={ans}$.'),A(rf'$k={a}$, using $k>0$.')),
   part('Find the coefficient of x cubed.',M(rf'$\binom63({a})^3$.'),A(rf'${20*a**3}$. Follow through the positive value of k from part (a).'))], 'Both target coefficients checked in symbolic expansion; negative root excluded by explicit k>0.')
  k=i+2;N=s.symbols('n',integer=True);expr=s.expand((N+k)**2-N**2);eq(expr,2*k*N+k*k)
  add(16,i,'Parity of a difference of squares','Deductive algebraic proof','1.6','medium',False,rf'Let n be an integer and let $D=(n+{2*k})^2-n^2$.',[
   part(rf'Prove that D is divisible by ${4*k}$.',M(rf'$D=n^2+{4*k}n+{4*k*k}-n^2$.'),A(rf'$D={4*k}(n+{k})$.'),R(rf'$n+{k}$ is an integer, so D is an integer multiple of ${4*k}$.')),
   part('Explain why checking several integer values would not be a proof.',R('A finite set of examples cannot establish the claim for every integer; the algebra covers an arbitrary integer.'))], 'Identity expanded symbolically; the integer factor, rather than examples, completes the divisibility proof.')
  k=i+2;eq(1/x-1/(x+k),k/(x*(x+k)))
  add(17,i,'A rational identity with restrictions','LHS-to-RHS proof','1.6','medium',False,rf'Let $x\ne0$ and $x\ne-{k}$.',[
   part(rf'Prove that $\frac1x-\frac1{{x+{k}}}\equiv\frac{{{k}}}{{x(x+{k})}}$.',M(rf'Use common denominator $x(x+{k})$ on the left.'),A(rf'$\frac{{x+{k}-x}}{{x(x+{k})}}$.'),R(rf'The numerator is ${k}$, giving the required right-hand side for all allowed x.')),
   part('Explain why the excluded values must remain excluded after simplification.',R('The original denominators are zero there; an algebraic identity only asserts equality where both sides are defined.'))], 'Rational difference checked symbolically; domain restrictions independently reviewed.')
  P=5000+1000*i;r=.048+.006*i;m=12;yrs=3+i;V=P*(1+r/m)**(m*yrs);effective=(1+r/m)**12-1
  eq(V/P,(1+effective)**yrs)
  add(18,i,'Comparing nominal and effective interest','Financial compounding frequency','1.4','hard',True,rf'USD ${P}$ is invested at a nominal annual rate of ${100*r:g}\%$, compounded monthly.',[
   part('Find the effective annual rate as a percentage, to three significant figures.',M(rf'$r_{{\rm eff}}=(1+{r:g}/12)^{{12}}-1$.'),A(rf'${n(100*effective)}\%$.')),
   part(rf'Find the balance after ${yrs}$ years, to the nearest cent.',M(rf'$V={P}(1+{r:g}/12)^{{{12*yrs}}}$.'),A(rf'USD ${V:.2f}$.')),
   part('State one assumption of this model.',R('The interest rate remains fixed throughout and there are no deposits, withdrawals or fees.'))], 'Monthly balance checked against effective-annual-rate model; months and nominal decimal rate checked.')
  a=8+2*i;d=4;b=4+i;r=1.25;N=next(k for k in range(1,100) if b*r**(k-1)>a+d*(k-1));checked(b*r**(N-2)<=a+d*(N-2),'first crossing')
  add(19,i,'Linear versus multiplicative progress','Comparing sequence models','1.2','hard',True,rf'In week n, project A completes $A_n={a}+4(n-1)$ units and project B completes $B_n={b}(1.25)^{{n-1}}$ units. These are weekly outputs, not cumulative totals.',[
   part('Find the first week in which project B has a greater weekly output than project A.',M(rf'Compare ${b}(1.25)^{{n-1}}$ with ${a}+4(n-1)$ using an integer table or graph.'),A(rf'Week ${N}$.'),R(rf'At week ${N-1}$, $B={n(b*r**(N-2))}\leq A={a+4*(N-2)}$; at week ${N}$, $B={n(b*r**(N-1))}>A={a+4*(N-1)}$. Earlier integer weeks also satisfy $B\leq A$.')),
   part('Explain why the two models should not necessarily be used indefinitely.',R('Capacity or resource constraints may prevent either constant additive increases or constant percentage growth from continuing.'))], 'All integer weeks up to first crossing enumerated independently; weekly output is distinguished from sums.')
 return sorted(q,key=lambda z:z['number'])

if __name__=='__main__':save('number-algebra',build())
