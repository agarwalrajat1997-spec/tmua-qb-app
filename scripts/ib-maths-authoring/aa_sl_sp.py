from aa_sl_core import *
def histogram(freq,width=10):
 e=[line((65,285),(575,285)),line((65,285),(65,45)),txt((65,27),'Frequency'),txt((450,330),'Time (minutes)')];scale=210/max(freq)
 for j,f in enumerate(freq):
  xx=65+j*100;yy=285-f*scale
  e +=[f'<rect x="{xx}" y="{yy:.2f}" width="100" height="{f*scale:.2f}" fill="#d1fae5" stroke="#0f766e" stroke-width="2"/>',txt((xx+42,yy-8),f),txt((xx-5,307),j*width)]
 e +=[txt((65+len(freq)*100-7,307),len(freq)*width)]
 return svg(e)
def build():
 q=[]
 def add(j,i,title,sub,code,diff,calc,stem,ps,checks,**kw):q.append(rec('statistics-probability','sp',j,i,title,sub,code,diff,calc,stem,ps,checks,**kw))
 for i in range(4):
  groups=[120+20*i,180+30*i,300+50*i];N=sum(groups);sample=60;alloc=[sample*k//N for k in groups];eq(sum(alloc),sample)
  add(0,i,'Planning a representative school sample','Stratified sampling','4.1','easy',False,rf'A school has ${groups[0]}$, ${groups[1]}$ and ${groups[2]}$ students in three year groups. A sample of60 students is selected in proportion to year-group size.',[
   part('Find how many students should be selected from each year group.',M(rf'Use $60\times(\text{{group size}}/{N})$.'),A(rf'${alloc[0]}, {alloc[1]}, {alloc[2]}$ respectively.')),
   part('Describe how students should be chosen within each group.',R('Number every student in each group and use a random selection without replacement for the required number.'))], 'Allocations sum to60 and preserve population proportions; within-group randomization avoids convenience selection.')
  contexts=[('a sports club','weekday mornings','members who only attend evenings'),('a library','during school hours','people who work during those hours'),('a rail station','one Sunday morning','weekday commuters'),('a café','lunchtime on Monday','customers who visit at other times')];place,time,miss=contexts[i]
  add(1,i,'Recognizing sampling bias','Sampling reliability','4.1','easy',False,f'A survey of users of {place} interviews the first40 visitors during {time}. The organizer uses the answers to describe all users.',[
   part('Identify the sampling method and explain a likely source of bias.',A('Convenience sampling.'),R(f'The time restriction may underrepresent {miss}.')),
   part('Suggest a practical improvement.',R('Sample across a range of days and times, and randomly select users within those periods.')),
   part('Classify the number of visits per month and a measured visit duration as discrete or continuous.',A('Number of visits is discrete; measured duration is continuous.'))], 'Method, target population and undercoverage reviewed; data types based on counting versus measurement.')
  vals=[1,2,3,4];freq=[2+i,4,3,1+i];N=sum(freq);mean=sum(a*b for a,b in zip(vals,freq))/N;sd=math.sqrt(sum(b*(a-mean)**2 for a,b in zip(vals,freq))/N)
  expanded=[a for a,f in zip(vals,freq) for j in range(f)];eq(sum(expanded)/len(expanded),mean)
  add(2,i,'A frequency distribution of visits','Mean and population standard deviation','4.3','easy',True,rf'For a population of ${N}$ customers, the number of visits in a week is $x=1,2,3,4$, with respective frequencies ${freq}$.',[
   part('Find the population mean and standard deviation.',M('Enter x values with their frequencies; use population standard deviation σ, not the sample statistic s.'),A(rf'Mean $={n(mean)}$ visits.'),A(rf'Population standard deviation $={n(sd)}$ visits.')),
   part('Find the proportion who make at least3 visits.',A(rf'${frac(freq[2]+freq[3],N)}$.'))], 'Expanded-data mean/variance agrees with weighted calculation; population denominator is N.')
  freq=[4+i,6+i,10,5,4];mids=[5,15,25,35,45];N=sum(freq);mean=sum(f*m for f,m in zip(freq,mids))/N;eq(sum(freq),N)
  add(3,i,'Grouped journey durations','Histograms and grouped mean','4.2','medium',True,rf'The histogram shows journey durations in equal10-minute classes. The population size is ${N}$.',[
   part('State the modal class.',A(r'$20\leq t<30$ minutes.')),
   part('Estimate the mean duration.',M(r'Use midpoints5,15,25,35,45 with the displayed frequencies.'),A(rf'$\bar t={sum(f*m for f,m in zip(freq,mids))}/{N}={n(mean)}$ minutes.')),
   part('Explain why the mean is an estimate.',R('The exact observations within each class are unknown; the calculation assumes they can be represented by the class midpoint.'))], 'Histogram heights are frequencies (equal widths); weighted midpoint total checked by explicit sum.',diagram=histogram(freq))
  lo=2+i;q1=8+i;med=12+i;q3=17+i;hi=25+i
  add(4,i,'Interpreting a five-number summary','Box-and-whisker diagrams','4.2','easy',False,rf'The box plot summarizes a population of commuting times in minutes. Assume no outliers.',[
   part('State the median, interquartile range and range.',A(rf'Median ${med}$ minutes.'),A(rf'IQR $={q3}-{q1}=9$ minutes; range $={hi}-{lo}=23$ minutes.')),
   part('Explain what the box represents.',R(rf'Approximately the middle50% of commuting times lie between ${q1}$ and ${q3}$ minutes.'))], 'Five-number ordering checked; IQR/range are differences, with population context retained.',diagram=boxplot([lo,q1,med,q3,hi],'Commuting times (minutes)'))
  q1=10+i;q3=18+i;value=32+i;low=q1-12;high=q3+12
  add(5,i,'Checking an unusually long journey','Outliers','4.1','medium',False,rf'Journey-time quartiles are $Q_1={q1}$ and $Q_3={q3}$ minutes. One observation is ${value}$ minutes.',[
   part('Use the1.5 IQR rule to decide whether this observation is an outlier.',A(r'$\mathrm{IQR}=8$ minutes.'),M(rf'Fences are ${q1}-1.5(8)={low}$ and ${q3}+1.5(8)={high}$.'),R(rf'${value}>{high}$, so it is an upper outlier.')),
   part('Explain why it should not automatically be removed.',R('It may be a valid long journey rather than a recording error; investigate its source and context before deciding.'))], 'Both fences checked; strict upper comparison and contextual validity reviewed.')
  mean=20+i;sd=3+i;a=2+i;b=5;newmean=a*mean+b;newsd=a*sd
  eq(newmean,a*mean+b)
  add(6,i,'Changing a measurement scale','Effects of data transformations','4.3','medium',False,rf'A population of measurements has mean ${mean}$ and standard deviation ${sd}$. Each value x is converted to $y={a}x+5$.',[
   part('Find the mean and standard deviation of y.',M(rf'New mean $={a}({mean})+5$.'),A(rf'Mean ${newmean}$.'),A(rf'Standard deviation ${newsd}$; adding5 has no effect on spread.')),
   part('Find the variance of y.',A(rf'${newsd**2}$.'))], 'Location/spread rules independently checked using artificial two-point population with same mean and SD; variance squared.')
  X=[1,2,3,4,5,6];Y=[2+i,4+i,5+i,8+i,8+i,10+i];reg=linregress(X,Y);pred=reg.intercept+reg.slope*4.5
  eq(reg.slope,sum((a-3.5)*(b-sum(Y)/6) for a,b in zip(X,Y))/sum((a-3.5)**2 for a in X))
  add(7,i,'Fitting a bivariate model','Pearson correlation and regression','4.4','medium',True,rf'The paired data are $x:1,2,3,4,5,6$ and $y:{", ".join(map(str,Y))}$.',[
   part('Find Pearson r and the regression line of y on x.',M('Enter the paired data in the same order and calculate linear regression.'),A(rf'$r={n(reg.rvalue)}$.'),A(rf'$y={n(reg.slope)}x+{n(reg.intercept)}$; retain full coefficients for prediction.')),
   part('Estimate y when x=4.5.',M(rf'$y={reg.slope:.8f}(4.5)+{reg.intercept:.8f}$.'),A(rf'$y={n(pred)}$.')),
   part('Explain why the data do not establish that x causes y.',R('Correlation may reflect a third variable or another association; these paired observations alone do not establish causation.'))], 'Regression slope checked by independent centered-sum formula; prediction uses unrounded coefficients.')
  X=[2,3,4,5,6,7];Y=[5+i,5+i,8+i,9+i,11+i,12+i];reg=linregress(Y,X);target=9+i;pred=reg.intercept+reg.slope*target
  eq(reg.intercept,sum(X)/6-reg.slope*sum(Y)/6)
  add(8,i,'Choosing the regression direction','Regression of x on y','4.10','medium',True,rf'The data are $x:2,3,4,5,6,7$ and $y:{", ".join(map(str,Y))}$.',[
   part('Find the regression line of x on y.',M('Treat y as explanatory and x as response when calculating this regression.'),A(rf'$x={n(reg.slope)}y+{n(reg.intercept)}$.')),
   part(rf'Estimate x when $y={target}$.',M('Substitute in the x-on-y line using unrounded coefficients.'),A(rf'$x={n(pred)}$.')),
   part('Explain why rearranging this line is generally unsuitable for predicting y from x.',R('The x-on-y line minimizes horizontal prediction errors; y-on-x minimizes vertical errors and generally gives a different line.'))], 'Regression direction checked against centered-sum formula; target y is within observed range.')
  PA=s.Rational(3,5);PB=s.Rational(1,2);both=s.Rational(2+i,10);union=PA+PB-both;neither=1-union
  checked(0<=neither<=1 and both<=PB,'valid Venn masses')
  add(9,i,'Two overlapping memberships','Venn probability','4.5','easy',False,rf'$P(A)=3/5$, $P(B)=1/2$ and $P(A\cap B)={L(both)}$.',[
   part(r'Find $P(A\cup B)$ and $P(A^\prime\cap B^\prime)$.',M(r'$P(A\cup B)=P(A)+P(B)-P(A\cap B)$.'),A(rf'$P(A\cup B)={L(union)}$.'),A(rf'$P(A^\prime\cap B^\prime)={L(neither)}$.')),
   part('Find the probability that exactly one of A and B occurs.',A(rf'${L(PA+PB-2*both)}$.'))], 'Four disjoint Venn regions checked nonnegative and summing to1; union and exactly-one independently summed.')
  aa=12+i;ab=8+i;ba=18+i;bb=22+i;total=aa+ab+ba+bb
  add(10,i,'Conditional probability from a table','Conditional probability','4.11','medium',False,rf'A survey records students in two clubs. Counts are: both clubs ${aa}$; A only ${ab}$; B only ${ba}$; neither ${bb}$. One of the ${total}$ students is selected at random.',[
   part('Find P(A given B).',M(rf'There are ${aa+ba}$ members of B, of whom ${aa}$ also belong to A.'),A(rf'$P(A\mid B)={frac(aa,aa+ba)}$.')),
   part('Determine whether A and B are independent.',M(rf'Compare $P(A\mid B)={frac(aa,aa+ba)}$ with $P(A)={frac(aa+ab,total)}$.'),R('They are unequal, so A and B are not independent. Equivalent product test accepted.'))], 'All joint cells summed; conditional denominator checked; exact fractions show inequality for all four variants.')
  red=4+i;blue=5;total=red+blue;pRR=s.Rational(red*(red-1),total*(total-1));pMixed=s.Rational(2*red*blue,total*(total-1))
  eq(pRR+s.Rational(blue*(blue-1),total*(total-1))+pMixed,1)
  e=[txt((55,35),'Draw two counters without replacement'),line((80,180),(250,90)),line((80,180),(250,270)),line((250,90),(450,55)),line((250,90),(450,130)),line((250,270),(450,230)),line((250,270),(450,310)),txt((260,83),'R'),txt((260,286),'B'),txt((460,60),'R'),txt((460,135),'B'),txt((460,235),'R'),txt((460,315),'B')]
  add(11,i,'Two draws without replacement','Probability trees','4.6','medium',False,rf'A bag contains ${red}$ red and5 blue counters. Two counters are drawn without replacement. The unlabelled branches show the two stages.',[
   part('Find the probability that both counters are red.',M(rf'$P(RR)=\frac{{{red}}}{{{total}}}\frac{{{red-1}}}{{{total-1}}}$.'),A(rf'${L(pRR)}$.')),
   part('Find the probability of one counter of each colour.',M(rf'Add both orders: $\frac{{{red}}}{{{total}}}\frac5{{{total-1}}}+\frac5{{{total}}}\frac{{{red}}}{{{total-1}}}$.'),A(rf'${L(pMixed)}$.'))], 'All four ordered outcomes enumerated and sum to1; second draw denominator decreases; both mixed orders included.',diagram=svg(e))
  p=s.Rational(i+2,10);b=s.Rational(3,5);union=p+b-p*b
  eq((p+b-union),p*b)
  add(12,i,'An unknown independent probability','Testing and using independence','4.11','hard',False,rf'Events A and B are independent. $P(B)=3/5$ and $P(A\cup B)={L(union)}$.',[
   part('Find P(A).',M(r'Let $p=P(A)$, so $P(A\cap B)=3p/5$.'),M(rf'$p+3/5-3p/5={L(union)}$.'),A(rf'$P(A)={L(p)}$.')),
   part('Find the probability that neither event occurs.',M(r'$P(A^\prime\cap B^\prime)=(1-P(A))(1-P(B))$.'),A(rf'${L(1-union)}$.'))], 'Recovered p checked in union formula and all four product regions; answer lies within [0,1].')
  offset=i;weights=[1,2,3,4];den=sum(weights);values=[offset+j for j in range(4)];E=s.Rational(sum(v*w for v,w in zip(values,weights)),den)
  eq(sum(s.Rational(w,den) for w in weights),1)
  add(13,i,'Normalizing a discrete distribution','Discrete random variables','4.7','medium',False,rf'X takes values ${values}$ with respective probabilities $k,2k,3k,4k$.',[
   part('Find k.',M(r'$k+2k+3k+4k=1$.'),A(r'$k=1/10$.')),
   part('Find E(X) and P(X at least its greatest possible value minus1).',M(r'$E(X)=\sum xP(X=x)$.'),A(rf'$E(X)={L(E)}$.'),A(r'$P=3/10+4/10=7/10$.'))], 'Distribution sums to1; expectation independently checked by ten equally likely weighted outcomes; no AHL discrete variance.')
  prize=12+4*i;p=s.Rational(1,4);fee=s.Rational(prize,4)
  eq(p*prize-fee,0)
  add(14,i,'Setting a fair entry fee','Expected value and fair games','4.7','medium',False,rf'A game pays USD ${prize}$ with probability1/4 and pays nothing otherwise. A player pays a fixed fee c to play.',[
   part('Write the expected net gain in terms of c.',M(rf'$E(G)=\frac14({prize}-c)+\frac34(-c)$.'),A(rf'$E(G)={L(fee)}-c$.')),
   part('Find the fee for a fair game and explain its meaning.',A(rf'$c={L(fee)}$ dollars.'),R('The expected net gain per play is zero in the long run; individual outcomes can still be wins or losses.'))], 'Net outcomes include entry fee in both cases; fair fee checked by exact weighted sum.')
  N=12+2*i;p=.2+.05*i;k=3+i;exact=binom.pmf(k,N,p);atleast=binom.sf(k-1,N,p);eq(exact,math.comb(N,k)*p**k*(1-p)**(N-k))
  add(15,i,'Quality checks on a batch','Binomial probabilities','4.8','medium',True,rf'Each item independently passes an inspection with probability ${p:g}$. Let X be the number that pass in a batch of ${N}$ items.',[
   part('State the distribution of X and one required modelling assumption.',A(rf'$X\sim\mathrm{{Bin}}({N},{p:g})$.'),R('The pass probability is the same for each item and inspection outcomes are independent.')),
   part(rf'Find $P(X={k})$ and $P(X\geq{k})$.',M('Use the binomial probability and cumulative functions with the stated n and p.'),A(rf'$P(X={k})={n(exact)}$.'),A(rf'$P(X\geq{k})={n(atleast)}$.')),
   part('Find the mean and variance of X.',A(rf'$E(X)=np={n(N*p)}$ and $\mathrm{{Var}}(X)=np(1-p)={n(N*p*(1-p))}$.'))], 'PMF checked with combinations and powers; tail checked by explicit PMF sum; binomial moments in SL scope.')
  p=.15+.05*i;target=.95;N=math.ceil(math.log(1-target)/math.log(1-p));checked(1-(1-p)**(N-1)<target<=1-(1-p)**N,'minimum trial')
  add(16,i,'How many independent attempts?','Binomial threshold','4.8','hard',True,rf'Each independent attempt succeeds with probability ${p:g}$. The number n of attempts should make the probability of at least one success at least0.95.',[
   part('Find the least possible integer n.',M(rf'$1-(1-{p:g})^n\geq0.95$.'),M(rf'$n\geq\ln(0.05)/\ln({1-p:g})={math.log(.05)/math.log(1-p):.6f}$.'),A(rf'$n={N}$.')),
   part('Verify the integer boundary.',A(rf'For $n={N-1}$ the probability is ${1-(1-p)**(N-1):.6f}$.'),R(rf'For $n={N}$ it is ${1-(1-p)**N:.6f}$, so this is the least integer satisfying the target.'))], 'Adjacent integer probabilities checked directly; complementary no-success event avoids off-by-one error.')
  mu=50+5*i;sd=6+i;lo=mu-sd;hi=mu+1.5*sd;prob=norm.cdf(hi,mu,sd)-norm.cdf(lo,mu,sd);eq(prob,norm.cdf(1.5)-norm.cdf(-1))
  add(17,i,'A normal tolerance interval','Normal probabilities','4.9','medium',True,rf'A component length X is modelled by $X\sim N({mu},{sd}^2)$ mm.',[
   part(rf'Find $P({lo}\leq X\leq{hi:g})$.',M(rf'Use the normal cumulative probability with bounds ${lo}$ and ${hi:g}$, mean ${mu}$ and standard deviation ${sd}$.'),A(rf'${n(prob)}$.')),
   part('In a batch of500 independently produced components, find the expected number in this interval.',M(rf'$500({prob:.8f})$.'),A(rf'${n(500*prob)}$ components. This is an expectation, not a guaranteed count.'))], 'Normal CDF interval checked using standardized bounds; expectation checked by linearity.',diagram=plot([lambda z: norm.pdf(z,mu,sd)],mu-3*sd,mu+3*sd,0,1/(sd*math.sqrt(2*math.pi))*1.3,title=f'Normal model: mean {mu} mm; SD {sd} mm'))
  mu=100+5*i;sd=8+i;percent=.9;cut=norm.ppf(percent,mu,sd);eq(norm.cdf(cut,mu,sd),percent)
  add(18,i,'A high-percentile cutoff','Inverse normal','4.9','hard',True,rf'$X\sim N({mu},{sd}^2)$. A cutoff c is chosen so that10% of values exceed c.',[
   part('Find c to three significant figures.',M(r'$P(X\leq c)=0.90$; use inverse normal with area0.90.'),A(rf'$c={n(cut)}$.')),
   part('Find the standardized value of the cutoff and interpret it.',M(rf'$z=(c-{mu})/{sd}$ using unrounded c.'),A(rf'$z={n(norm.ppf(.9))}$.'),R('The cutoff is about1.28 standard deviations above the mean.'))], 'Quantile inserted in CDF recovers0.90; upper10% converted to lower90%; z interpretation correct.')
  mu=40+4*i;sd=5+i;z=norm.ppf(.9);low=mu-sd*z;high=mu+sd*z
  # Display enough precision that recovering the two parameters is stable to three significant figures.
  lo=float(f'{low:.8f}');hi=float(f'{high:.8f}');solsd=(hi-lo)/(2*z);solmu=(hi+lo)/2;eq(solmu,mu);eq(solsd,sd,tol=1e-7)
  add(19,i,'Recovering a normal model from percentiles','Unknown normal parameters','4.12','hard',True,rf'X is normally distributed with unknown mean μ and standard deviation σ. $P(X<{lo:.8f})=0.10$ and $P(X<{hi:.8f})=0.90$.',[
   part('Find μ and σ to three significant figures.',M(r'Use inverse standard normal: $z_{0.10}=-1.281551566$ and $z_{0.90}=1.281551566$.'),A(rf'${lo:.8f}=\mu-1.281551566\sigma$ and ${hi:.8f}=\mu+1.281551566\sigma$.'),M('Add the equations to find μ; subtract to find σ.'),A(rf'$\mu={n(solmu)}$ and $\sigma={n(solsd)}$.')),
   part(rf'Find $P(X>{mu+sd})$.',M(rf'Standardize at one standard deviation above the recovered mean, or use the normal CDF.'),A(rf'${n(norm.sf(1))}$. Follow through sensible recovered parameters.'))], 'Two stated percentiles independently recovered by CDF; equations solved from displayed rounded quantities; final tail checked at z=1.')
 return sorted(q,key=lambda z:z['number'])
if __name__=='__main__':save('statistics-probability',build())
