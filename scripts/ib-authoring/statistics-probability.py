from pathlib import Path
_HERE = Path(__file__).resolve().parent
import json, math, re, os, itertools, statistics
from fractions import Fraction as F
import numpy as np
from scipy.stats import norm, binom
from scipy.optimize import brentq
import sympy as sy
BASE=(_HERE.parents[1] / 'content/ib/math-aa-hl')
REF=json.loads(Path(str(_HERE / 'reference-metadata' / 'IB Mathematics AA HL Questionbank - Statistics & Probability.json')).read_text())
OUT={}
CHECKS=[]
def f(x):
 if isinstance(x,F):return str(x.numerator) if x.denominator==1 else rf'\frac{{{x.numerator}}}{{{x.denominator}}}'
 return fmt_number(float(x),6)
def fmt_number(x,digits):
 value=format(x,f'.{digits}g')
 if 'e' in value:
  mantissa,exponent=value.split('e');return mantissa+rf'\times10^{{{int(exponent)}}}'
 return value
def ans(x):
 if isinstance(x,F):return f(x)
 return fmt_number(float(x),3)
def frac(a,b):return f(F(a,b))
def table(head,rows):return '\n\n| '+' | '.join(map(str,head))+' |\n| '+' | '.join(['---']*len(head))+' |\n'+'\n'.join('| '+' | '.join(map(str,row))+' |' for row in rows)+'\n'
def rowtable(labels,*rows):return table(labels,rows)
def part(label,prompt,marks,*steps):return {'label':label,'prompt':prompt,'marks':marks,'steps':[{'code':c,'text':t} for c,t in steps]}
def tidy_prose(text):
 chunks=re.split(r'(\$\$[\s\S]*?\$\$|\$[^$]*?\$)',text)
 for i in range(0,len(chunks),2):
  chunks[i]=re.sub(r'([A-Za-z])(?=\d)',r'\1 ',chunks[i])
  chunks[i]=re.sub(r'(\d)(?=[A-Za-z])(?!st\b|nd\b|rd\b|th\b|s\b)',r'\1 ',chunks[i])
 return ''.join(chunks)
def Q(n,title,sub,calc,stem,parts,notes='New numerical data; displayed calculations recomputed in the authoring script.',diagram=None):
 stem=tidy_prose(stem)
 for p in parts:
  p['prompt']=tidy_prose(p['prompt'])
  for step in p['steps']:step['text']=tidy_prose(step['text'])
 marks=sum(p['marks'] for p in parts)
 if marks != REF[n-1]['marks']:raise ValueError(('source total',n,marks,REF[n-1]['marks']))
 groups=[]
 for p in parts:
  assert sum(0 if s['code']=='AG' else int(s['code'][1:]) for s in p['steps'])==p['marks'],(n,p)
  groups.append({'part':p['label'],'steps':p['steps']})
 obj={'id':rf'ib-aa-sp-{n:03}','subject':'math-aa-hl','topicId':'statistics-probability','collectionId':'statistics-probability','number':n,'title':title,'subtopic':sub,'difficulty':REF[n-1]['difficulty'],'calculator':calc,'marks':marks,'stem':stem,'parts':[{k:p[k] for k in ['label','prompt','marks']} for p in parts if p['label']],'markScheme':groups,'source':{'document':'IB Mathematics AA HL Questionbank - Statistics & Probability.pdf','question':n},'verification':{'method':'numerical and reasoned','notes':notes},'status':'published'}
 if diagram:obj['diagramSvg']=diagram
 OUT[n]=obj
 return obj
def save():
 p=BASE/'statistics-probability.json';tmp=p.with_suffix('.tmp')
 with open(tmp,'w') as h:json.dump([OUT[k] for k in sorted(OUT)],h,ensure_ascii=False,indent=2);h.flush();os.fsync(h.fileno())
 os.replace(tmp,p)
def reg(x,y):
 x=np.array(x,dtype=float);y=np.array(y,dtype=float);a=float(np.sum((x-x.mean())*(y-y.mean()))/np.sum((x-x.mean())**2));b=float(y.mean()-a*x.mean());r=float(np.corrcoef(x,y)[0,1]);return a,b,r

def venn(a='A',b='B',regions=('p','r','q','s')):
 p,r,q,s=regions
 return rf'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 220" role="img" aria-label="Venn diagram"><rect x="10" y="10" width="500" height="200" fill="white" stroke="#222"/><circle cx="210" cy="110" r="85" fill="none" stroke="#222"/><circle cx="320" cy="110" r="85" fill="none" stroke="#222"/><text x="170" y="40" font-size="17">{a}</text><text x="350" y="40" font-size="17">{b}</text><text x="175" y="115" font-size="17">{p}</text><text x="260" y="115" font-size="17">{r}</text><text x="350" y="115" font-size="17">{q}</text><text x="465" y="180" font-size="17">{s}</text><text x="20" y="32" font-size="17">U</text></svg>'
def boxplot(vals,labels=None):
 lo,q1,med,q3,hi=vals;labs=labels or list(map(str,vals));mn=min(lo,0);mx=hi+max(2,(hi-lo)*.05);scale=lambda v:50+420*(v-mn)/(mx-mn)
 svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 175" role="img" aria-label="Box and whisker plot">'
 svg+=rf'<line x1="{scale(lo)}" y1="65" x2="{scale(hi)}" y2="65" stroke="#222"/>'
 svg+=rf'<rect x="{scale(q1)}" y="40" width="{scale(q3)-scale(q1)}" height="50" fill="white" stroke="#222"/>'
 for v,l in zip(vals,labs):svg+=rf'<line x1="{scale(v)}" y1="40" x2="{scale(v)}" y2="90" stroke="#222"/><text x="{scale(v)}" y="120" text-anchor="middle" font-size="15">{l}</text>'
 return svg+'</svg>'
def curve(points,xlabel='x',ylabel='Cumulative frequency'):
 xmax=max(x for x,y in points);ymax=max(y for x,y in points);X=lambda x:55+440*x/xmax;Y=lambda y:265-220*y/ymax
 s='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 550 330" role="img" aria-label="Cumulative frequency graph">'
 for x,y in points:
  s+=rf'<line x1="{X(x)}" y1="45" x2="{X(x)}" y2="265" stroke="#ddd"/><text x="{X(x)}" y="285" text-anchor="middle" font-size="13">{x}</text>'
 for y in np.linspace(0,ymax,9):s+=rf'<line x1="55" y1="{Y(y)}" x2="495" y2="{Y(y)}" stroke="#ddd"/><text x="48" y="{Y(y)+4}" text-anchor="end" font-size="12">{f(y)}</text>'
 s+='<line x1="55" y1="45" x2="55" y2="265" stroke="#222"/><line x1="55" y1="265" x2="495" y2="265" stroke="#222"/>'
 s+='<polyline points="'+' '.join(rf'{X(x)},{Y(y)}' for x,y in points)+'" fill="none" stroke="#222" stroke-width="2"/>'
 s+=rf'<text x="270" y="315" text-anchor="middle" font-size="14">{xlabel}</text><text x="55" y="24" font-size="14">{ylabel}</text></svg>'
 return s
D='Descriptive statistics';P='Probability';R='Discrete random variables';B='Binomial distribution';N='Normal distribution';C='Continuous random variables';L='Bivariate statistics'
# 1-7
Q(1,'A club scoring table',D,False,'Twenty-four players each make five attempts at a target. Their scores are recorded below.'+table(['Score','0','1','2','3','4','5'],[['Frequency','2','3','$k$','7','4','2']]),[
 part('a','Find $k$.',1,('A1','$k=24-(2+3+7+4+2)=6$.')),
 part('b','A player is chosen at random. Find the probability that their score is at least 3.',2,('M1','There are $7+4+2=13$ qualifying players.'),('A1',r'$P(X\geq3)=\frac{13}{24}$.')),
 part('c','Find the mean score.',2,('M1',r'$\bar x=\frac{0(2)+1(3)+2(6)+3(7)+4(4)+5(2)}{24}$.'),('A1',r'$\bar x=\frac{62}{24}=\frac{31}{12}$.'))])
Q(2,'Normalising a discrete distribution',R,False,'The distribution of $X$ is given below.'+table(['$x$','1','2','3','4'],[['$P(X=x)$','$q$','$2q$','$3q$','$4q$']]),[
 part('a','Find $q$.',3,('M1','Use the fact that the probabilities add to 1.'),('A1','$q+2q+3q+4q=10q=1$.'),('A1',r'$q=\frac1{10}$.')),
 part('b','Find $E(X)$.',3,('M1',r'$E(X)=\sum xP(X=x)$.'),('A1',r'$E(X)=\frac{1+4+9+16}{10}$.'),('A1','$E(X)=3$.'))])
data=[12,15,18,20,22,24,26,28,30,32,35,38];med=25;q1=19;q3=31
Q(3,'Reading a stem-and-leaf plot',D,False,r'The times in minutes that a group of learners spend reading are shown in the stem-and-leaf plot. The key is $2\mid4=24$ minutes.'+table(['Stem','Leaves'],[['1','2 5 8'],['2','0 2 4 6 8'],['3','0 2 5 8']])+'\nA boxplot of the same data has lower quartile labelled $q$, median labelled $m$ and upper quartile labelled $p$. The interquartile range is 12 minutes.',[
 part('a','(i) State the number of learners. (ii) Find the median.',3,('A1','There are 12 learners.'),('M1','The central observations are 24 and 26.'),('A1','$m=(24+26)/2=25$ minutes.')),
 part('b','(i) Find $q$. (ii) Find $p$.',3,('A1','$q=(18+20)/2=19$.'),('M1','The interquartile range gives $p-19=12$.'),('A1','$p=31$.'))],diagram=boxplot([12,19,25,31,38],['12','q','m','p','38']))
Q(4,'Upper outlier boundary',D,False,'The boxplot shows the number of messages sent by a group of students in one hour.',[
 part('a','Find the interquartile range.',2,('M1',r'$\mathrm{IQR}=11-5$.'),('A1',r'$\mathrm{IQR}=6$.')),
 part('b','One student sent $k$ messages, where $k>11$. Given that this is an outlier, find the least possible integer value of $k$.',4,('M1',r'Upper outlier boundary $=Q_3+1.5\mathrm{IQR}$.'),('A1','$11+1.5(6)=20$.'),('R1','An upper outlier must be strictly greater than 20.'),('A1','$k=21$.'))],diagram=boxplot([1,5,7,11,16]))
Q(5,'Geometric probabilities',R,False,'A geometric sequence has $u_1=27$ and $u_4=1$. A discrete random variable has $P(X=j)=kr^{j-1}$ for $j=1,2,3$, where $r$ is the common ratio of the sequence.',[
 part('a','Find $r$.',2,('M1','$27r^3=1$.'),('A1','$r=1/3$.')),
 part('b','Find $k$.',4,('M1','$k+kr+kr^2=1$.'),('A1','$k(1+1/3+1/9)=1$.'),('A1','$13k/9=1$.'),('A1','$k=9/13$.'))])
Q(6,'Reconstructing a boxplot',D,False,'A dataset has minimum 14, lower quartile 20 and median 25. The lower outlier boundary is 11 and the maximum is 30.',[
 part('a','Find the interquartile range.',2,('M1',r'$20-1.5\mathrm{IQR}=11$.'),('A1',r'$\mathrm{IQR}=6$.')),
 part('b','Sketch a labelled box-and-whisker plot.',3,('A1','$Q_3=20+6=26$.'),('A1','Draw a box from 20 to 26 with a median line at 25.'),('A1','Whiskers end at 14 and 30, on a linear labelled scale.')),
 part('c','Describe the skewness suggested by the boxplot.',1,('R1','Negatively skewed: the lower side is more spread out and the median is closer to the upper quartile.'))])
Q(7,'Normal symmetry without a calculator',N,False,'$X$ is normally distributed with mean 80. It is given that $P(X<73)=0.18$.',[
 part('a','State $P(X>87)$.',1,('A1','$0.18$ by symmetry about80.')),
 part('b','Find $P(73<X<80)$.',2,('M1','The probability below the mean is 0.5.'),('A1','$0.5-0.18=0.32$.')),
 part('c','Find $P(73<X<87)$.',2,('M1','The limits are equally spaced about 80; use symmetry.'),('A1','$2(0.32)=0.64$.'))])
# 8
x=[4.5,5.8,6.6,7.2,7.6,8.1,8.5,9.1];y=[145,139,133,130,125,120,117,115];a,b,r=reg(y,x)
Q(8,'Recovering data and reverse regression',L,True,'A study records sleep $S$ (hours) and a measurement $B$. The mean point is $(7.175,128)$.'+table(['$S$','4.5','$a$','6.6','7.2','7.6','8.1','8.5','9.1'],[['$B$','145','139','133','$b$','125','120','117','115']]),[
 part('a','Find $a$ and $b$.',3,('M1','Use each mean multiplied by 8 to find its column total.'),('A1','$a=8(7.175)-51.6=5.8$.'),('A1','$b=8(128)-894=130$.')),
 part('b','Find the regression line of $S$ on $B$.',2,('M1','Regress sleep on the measurement, with $B$ as the explanatory variable.'),('A1',rf'$S={ans(a)}B+{ans(b)}$.')),
 part('c','Use the model to estimate the maximum sleep for which the predicted measurement is at least 132.',1,('A1',rf'At $B=132$, $S={ans(a*132+b)}$ hours; the negative slope makes this the maximum.'))])
# 9 cumulative
freq=[12,28,80,48,24,8];cf=np.cumsum(freq);pts=[(100,0),(150,12),(200,40),(250,120),(300,168),(350,192),(400,200)]
q1=200+10/80*50;q3=250+30/48*50;q85=300+2/24*50
Q(9,'Grouped water-use data',D,True,'Two hundred households record daily water use in litres. Use straight-line interpolation between plotted cumulative-frequency points.'+table(['Water use $w$','Frequency'],[[r'$100<w\le150$',12],[r'$150<w\le200$',28],[r'$200<w\le250$',80],[r'$250<w\le300$',48],[r'$300<w\le350$','$p$'],[r'$350<w\le400$',8]]),[
 part('a','(i) Find $p$. (ii) State the modal class.',2,('A1','$p=200-176=24$.'),('A1',r'$200<w\le250$.')),
 part('b','Estimate the interquartile range.',2,('M1',rf'$Q_1={f(q1)}$, $Q_3={f(q3)}$ from cumulative frequencies 50 and 150.'),('A1',rf'$\mathrm{{IQR}}={ans(q3-q1)}$ litres.')),
 part('c','Fifteen per cent of households use more than $q$ litres. Estimate $q$.',2,('M1','Read cumulative frequency $0.85(200)=170$.'),('A1',rf'$q=300+\frac2{{24}}(50)={ans(q85)}$ litres.'))],diagram=curve(pts,'Water use (litres)'))
Q(10,'Range and quartiles from a boxplot',D,False,'The boxplot represents commute times in minutes. The range is 28 and the interquartile range is 12.',[
 part('a','State the median.',1,('A1','The median is 18 minutes.')),
 part('b','Find $p$ and $q$.',4,('M1','$p-7=28$.'),('A1','$p=35$.'),('M1','$q-11=12$.'),('A1','$q=23$.'))],diagram=boxplot([7,11,18,23,35],['7','11','18','q','p']))
# histogram expressed exact frequency table, same reading skill via SVG
vals=[10,20,30,40,50,60];fr=[10,20,45,40,30,15];svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 530 300" role="img" aria-label="Frequency diagram">'
for i,(v,c) in enumerate(zip(vals,fr)):
 X=65+i*65;H=c*4;svg+=rf'<rect x="{X}" y="{250-H}" width="55" height="{H}" fill="#ddd" stroke="#222"/><text x="{X+27}" y="{240-H}" text-anchor="middle" font-size="14">{c}</text><text x="{X+27}" y="275" text-anchor="middle" font-size="14">{v}</text>'
svg+='<text x="65" y="25" font-size="15">Frequency</text><text x="420" y="295" font-size="13">Hours</text></svg>'
Q(11,'Working-hour frequencies',D,False,'The frequency diagram shows weekly hours worked by 160 employees, rounded to the nearest 10 hours. Use the median-of-halves convention for quartiles.',[
 part('a','State the modal working time.',1,('A1','30 hours.')),
 part('b','Find the median working time.',3,('M1','There are 160 values, so use the 80th and 81st.'),('A1','The cumulative frequencies are 10, 30, 75, 115, 145, 160; both central values are 40.'),('A1','Median $=40$ hours.')),
 part('c','Find the lower quartile and interquartile range.',2,('A1','$Q_1=30$ (40th and 41st values).'),('A1','$Q_3=50$, so IQR $=50-30=20$ hours.'))],diagram=svg)
Q(12,'Retirement ages and outliers',D,False,'A study of professional athletes produces the following boxplot of retirement ages.',[
 part('a','Describe the skewness.',1,('R1','The distribution is negatively skewed: the lower tail is longer.')),
 part('b','Find the interquartile range.',2,('M1',r'$\mathrm{IQR}=36-30$.'),('A1',r'$\mathrm{IQR}=6$ years.')),
 part('c','An athlete retires at age 20. Determine whether this is an outlier.',3,('M1',r'Lower boundary $=Q_1-1.5\mathrm{IQR}$.'),('A1','$30-1.5(6)=21$.'),('R1','$20<21$, so the retirement age is a lower outlier.'))],diagram=boxplot([22,30,34,36,39]))
Q(13,'Guessing on a multiple-choice test',B,True,'A test has 25 independent questions, each with five options and one correct answer. A learner guesses every answer at random. Let $X$ be the number correct.',[
 part('a','Find $E(X)$.',2,('M1',r'$X\sim B(25,0.2)$ and $E(X)=np$.'),('A1','$E(X)=5$.')),
 part('b','Find (i) $P(X=3)$; (ii) $P(X>3)$.',4,('M1',r'$P(X=3)=\binom{25}{3}(0.2)^3(0.8)^{22}$.'),('A1',rf'${ans(binom.pmf(3,25,.2))}$.'),('M1',r'$P(X>3)=1-P(X\le3)$.'),('A1',rf'${ans(binom.sf(3,25,.2))}$.'))])
Q(14,'Independent events with equal regions',P,False,r'Events $A$ and $B$ are independent, with $P(A\cap B)=P(A\cap B^{\prime})=0.2$.',[
 part('a','Find $P(A)$.',2,('M1','Add the two disjoint parts of $A$.'),('A1','$P(A)=0.2+0.2=0.4$.')),
 part('b',r'Find (i) $P(B)$; (ii) $P(A\cup B)$.',4,('M1','$0.2=P(A)P(B)=0.4P(B)$.'),('A1','$P(B)=0.5$.'),('M1',r'$P(A\cup B)=P(A)+P(B)-P(A\cap B)$.'),('A1','$0.4+0.5-0.2=0.7$.'))])
Q(15,'Completing probability regions',P,False,r'The diagram represents events with $P(A)=0.45$, $P(A\cap B)=0.15$ and $P(A\cup B)=0.8$.',[
 part('a','State $r$.',1,('A1','$r=0.15$.')),
 part('b','Find $p$, $q$ and $s$.',4,('A1','$p=0.45-0.15=0.3$.'),('M1','The union is the sum of the three interior regions.'),('A1','$q=0.8-0.45=0.35$.'),('A1','$s=1-0.8=0.2$.')),
 part('c','Find $P(B)$.',2,('M1','$P(B)=q+r$.'),('A1','$P(B)=0.35+0.15=0.5$.'))],diagram=venn())
Q(16,'Recovering a missing race time',D,False,'The mean time for the first four runners is 12.4 seconds. After a fifth time is included, the mean becomes 12.8 seconds. Find the fifth runner’s time.',[part('','',4,('M1','Total time of the first four runners is $4(12.4)$.'),('A1','This total is $49.6$ seconds.'),('M1','Subtract this from the new total $5(12.8)$.'),('A1','The fifth time is $64-49.6=14.4$ seconds.'))])
# regression helper individual datasets and tasks
def basicreg(n,title,x,y,xlabel,ylabel,target,marks=(4,3),context=''):
 a,b,r=reg(x,y)
 p1=part('a',rf'Find the regression line ${ylabel}=a{xlabel}+b$. Hence estimate ${ylabel}$ when ${xlabel}={target}$.',marks[0],('A1',rf'$a={ans(a)}$.'),('A1',rf'$b={ans(b)}$.'),('M1',rf'Substitute ${xlabel}={target}$ in the regression line.'),('A1',rf'Predicted ${ylabel}={ans(a*target+b)}$.'))
 p2=part('b','Find Pearson’s correlation coefficient'+(' and describe the correlation.' if marks[1]>1 else '.'),marks[1],*([('A1',rf'$r={ans(r)}$.')] + ([('R1',rf'The correlation is {"positive" if r>0 else "negative"}.')] if marks[1]>=2 else []) + ([('R1','It is strong, since $|r|$ is close to 1.')] if marks[1]>=3 else [])))
 return Q(n,title,L,True,context+table([rf'${xlabel}$']+x,[[rf'${ylabel}$']+y]),[p1,p2])
basicreg(17,'Height and mass regression',[158,163,168,173,178,183],[56.2,60.1,63.7,66.0,70.8,72.5],'x','y',166,context='The heights $x$ cm and masses $y$ kg of six students are recorded. ')
basicreg(18,'Temperature and drink sales',[17,19,22,25,27,30],[42,48,60,67,81,89],'T','N',24,marks=(4,1),context='A kiosk records temperature $T$ in °C and drinks sold $N$. ')
Q(19,'Conditional probability outside a set',P,False,r'Events satisfy $P(A)=0.4$, $P(B)=0.7$ and $P(A\cap B)=0.25$.',[
 part('a','Find $r,p,q,s$.',4,('A1','$r=0.25$.'),('A1','$p=0.4-0.25=0.15$.'),('A1','$q=0.7-0.25=0.45$.'),('A1','$s=1-(0.15+0.25+0.45)=0.15$.')),
 part('b',r'Find $P(A\mid B^{\prime})$.',2,('M1',r'$P(A\mid B^{\prime})=\frac{P(A\cap B^{\prime})}{P(B^{\prime})}$.'),('A1','$0.15/0.3=0.5$.'))],diagram=venn())
Q(20,'Symmetric normal intervals',N,False,'$X$ is normal with mean 150 and $P(132<X<168)=0.6$.',[
 part('a','State $P(X>168)$.',1,('A1','$(1-0.6)/2=0.2$ by symmetry.')),
 part('b','Find $P(X<168)$.',2,('M1','The two tails have equal probability $(1-0.6)/2=0.2$.'),('A1','$P(X<168)=0.8$.')),
 part('c',r'Find $P(X>132\mid X<168)$.',2,('M1','Use the probability of the interval divided by $P(X<168)$.'),('A1','$0.6/0.8=0.75$.'))])
Q(21,'Testing independence',P,False,r'$P(A)=0.4$, $P(B)=0.6$ and $P(A\cup B)=0.76$.',[
 part('a',r'Find $P(A\cap B)$.',2,('M1',r'$P(A\cap B)=P(A)+P(B)-P(A\cup B)$.'),('A1','$0.4+0.6-0.76=0.24$.')),
 part('b','Determine whether $A$ and $B$ are independent.',2,('M1','$P(A)P(B)=0.4(0.6)=0.24$.'),('R1',r'This equals $P(A\cap B)$, so the events are independent.'))])
Q(22,'Scaling a dataset',D,False,'Ten observations have sum 70 and population variance 3. Each observation is multiplied by 4.',[
 part('a','Find the original mean.',2,('M1','Mean = total divided by number of observations.'),('A1','$70/10=7$.')),
 part('b','Find the new mean and new variance.',3,('A1','New mean $=4(7)=28$.'),('M1','Variance is multiplied by the square of the scale factor.'),('A1','New variance $=4^2(3)=48$.'))])
Q(23,'Two draws without replacement',P,False,'A bag holds 6 blue and 4 red counters. Two counters are drawn without replacement.',[
 part('a','Draw a tree diagram, labelling all branch probabilities.',3,('A1','First draw: $P(B)=6/10$, $P(R)=4/10$.'),('A1','After blue: blue $5/9$, red $4/9$.'),('A1','After red: blue $6/9$, red $3/9$.')),
 part('b','Find the probability of exactly one blue counter.',3,('M1','Add the disjoint paths blue-red and red-blue.'),('A1',r'$\frac6{10}\frac49+\frac4{10}\frac69=\frac{48}{90}$.'),('A1',r'$\frac8{15}$.'))])
x=[20,45,75,110,140,175];y=[3.2,5.9,8.6,13.1,15.8,20.3];a,b,r=reg(x,y)
Q(24,'Distance and fuel',L,True,'A vehicle’s distance $x$ km and fuel use $y$ litres are recorded.'+table(['$x$']+x,[['$y$']+y]),[
 part('a','Find Pearson’s correlation coefficient.',2,('M1','Use paired values in a correlation calculation.'),('A1',rf'$r={ans(r)}$.')),
 part('b','Find $a$ and $b$ in the regression line $y=ax+b$.',2,('A1',rf'$a={ans(a)}$.'),('A1',rf'$b={ans(b)}$.')),
 part('c','Estimate fuel use for a distance of 60 km.',2,('M1',rf'$y={f(a)}(60)+{f(b)}$.'),('A1',rf'${ans(60*a+b)}$ litres.'))])
x=[.6,.85,1.05,1.2,1.45,1.65,1.85,2.1];y=[13.1,12.8,12.4,12.3,11.9,11.5,11.3,11.0];a,b,r=reg(x,y)
Q(25,'Interpreting a training regression',L,True,'Eight runners record training hours per day $h$ and sprint times $t$ seconds.'+table(['$h$']+x,[['$t$']+y]),[
 part('a','Find $r$ and describe the correlation.',2,('A1',rf'$r={ans(r)}$.'),('R1','There is a strong negative linear correlation.')),
 part('b','Find the gradient $m$ of the regression of $t$ on $h$.',1,('A1',rf'$m={ans(a)}$ seconds per hour.')),
 part('c','A runner trains an extra 20 minutes daily. Estimate the reduction in their time and give one reason the prediction may be inaccurate.',3,('M1','Twenty minutes is $1/3$ hour; predicted change is $m/3$.'),('A1',rf'The predicted reduction is ${ans(-a/3)}$ seconds.'),('R1','The association need not be causal; fitness, training quality or other differences may affect the runner’s result.'))])
Q(26,'Complement of an intersection',P,False,'For a randomly selected snack, the probability it is nut-free is 0.7, the probability it is large is 0.3, and the probability it is nut-free or large is 0.85. Find the probability that it is not both nut-free and large.',[part('','',6,('M1','Let $N$ mean nut-free and $L$ mean large; use the addition rule.'),('A1',r'$P(N\cup L)=P(N)+P(L)-P(N\cap L)$.'),('M1','Rearrange to obtain the intersection.'),('A1',r'$P(N\cap L)=0.7+0.3-0.85=0.15$.'),('M1','Take the complement of the intersection, not the intersection of complements.'),('A1','$1-0.15=0.85$.'))])
Q(27,'Recovering event probabilities',P,False,r'$P(A\cap B)=0.12$, $P((A\cup B)^{\prime})=0.25$, and $P(A\mid B)=0.3$.',[
 part('a','Find $P(B)$.',2,('M1','$0.3=0.12/P(B)$.'),('A1','$P(B)=0.4$.')),
 part('b','Find $P(A)$.',2,('M1','$P(A)+0.4-0.12=0.75$.'),('A1','$P(A)=0.47$.')),
 part('c','Are $A$ and $B$ independent?',2,('A1','$P(A)P(B)=0.47(0.4)=0.188$.'),('R1',r'No, since $0.188\ne0.12$.'))])
Q(28,'Exclusive or independent events',P,False,r'$P(A)=0.3$ and $P(A\cup B)=0.72$. Find $P(B)$ in each separate case.',[
 part('a','$A$ and $B$ are mutually exclusive.',2,('M1',r'$P(A\cap B)=0$.'),('A1','$P(B)=0.72-0.3=0.42$.')),
 part('b','$A$ and $B$ are independent.',4,('M1',r'$P(A\cap B)=0.3P(B)$.'),('A1','$0.72=0.3+P(B)-0.3P(B)$.'),('M1','$0.7P(B)=0.42$.'),('A1','$P(B)=0.6$.'))])
Q(29,'Two constraints on a distribution',R,False,'$X$ has the following distribution.'+table(['$x$','1','2','3','5'],[['$P(X=x)$','$p$','$q$','0.25','$r$']]),[
 part('a','Given $P(X>2)=0.55$, find $r$.',2,('M1','$0.25+r=0.55$.'),('A1','$r=0.3$.')),
 part('b','Given $E(X)=2.95$, find $p$ and $q$.',4,('M1','$p+q=0.45$ from total probability.'),('M1','$p+2q+3(0.25)+5(0.3)=2.95$, so $p+2q=0.7$.'),('A1','$q=0.25$.'),('A1','$p=0.2$.'))])
Q(30,'Venn diagram and conditional probability',P,False,r'$P(A)=0.55$, $P(A\cap B)=0.2$ and $P(A\cup B)=0.85$. In the diagram $p$ denotes the A-only region and $q$ the B-only region.',[
 part('a','Find $q$ and $p$.',3,('M1','Subtract the known whole-set probabilities from the appropriate region totals.'),('A1','$q=0.85-0.55=0.3$.'),('A1','$p=0.55-0.2=0.35$.')),
 part('b',r'Find $P(B^{\prime})$.',2,('M1','$P(B)=0.3+0.2=0.5$.'),('A1',r'$P(B^{\prime})=0.5$.')),
 part('c',r'Find $P(A\mid B^{\prime})$.',2,('M1',r'Divide the A-only region by $P(B^{\prime})$.'),('A1','$0.35/0.5=0.7$.'))],diagram=venn(regions=('p','0.2','q','0.15')))
save()
# 31-45
Q(31,'De Morgan’s law and conditioning',P,False,r'$A$ and $B$ are events with $P(A^{\prime}\cup B^{\prime})=0.82$ and $P(B^{\prime})=0.55$.',[
 part('a',r'Draw a two-set Venn diagram and shade $A^{\prime}\cup B^{\prime}$.',1,('A1',r'Shade all of the universal set except the overlap $A\cap B$.')),
 part('b',r'Find $P(A\mid B)$.',3,('A1',r'$P(A\cap B)=1-0.82=0.18$.'),('M1',r'$P(A\mid B)=0.18/(1-0.55)$.'),('A1',r'$P(A\mid B)=0.4$.'))],diagram=venn(regions=('','','','')))
pts=[(0,0),(10,16),(20,40),(30,80),(40,112),(50,144),(60,160)]
Q(32,'Reading cumulative frequency',D,True,'The cumulative-frequency graph shows completion times in minutes for 160 students. Use straight-line interpolation.',[
 part('a','State the median completion time.',1,('A1','At cumulative frequency 80, the median is 30 minutes.')),
 part('b','Find the probability that a randomly selected student took less than 40 minutes.',2,('M1','The cumulative frequency at 40 is 112.'),('A1','$112/160=0.7$.')),
 part('c','Ninety per cent took more than $k$ minutes. Find $k$.',3,('M1','The lower 10% correspond to cumulative frequency $16$.'),('M1','Read the time where the graph reaches 16.'),('A1','$k=10$ minutes.'))],diagram=curve(pts,'Time (minutes)'))
Q(33,'Shifting and scaling data',D,False,'A dataset has mean 18 and standard deviation 3.5. Consider each transformation separately.',[
 part('a','Six is added to each observation. Find the new mean and standard deviation.',3,('A1','New mean $=18+6=24$.'),('R1','Adding a constant does not alter deviations from the mean.'),('A1','The standard deviation remains 3.5.')),
 part('b','Each original observation is multiplied by 4. Find the new mean and variance.',3,('A1','New mean $=4(18)=72$.'),('M1','New variance $=4^2(3.5)^2$.'),('A1','The new variance is 196.'))])
x=[1,2,3,4,6,7];y=[7,11,14,18,24,29];a,b,r=reg(x,y)
Q(34,'Sales growth and slope',L,True,'A shop records cumulative notebooks sold $y$ at the end of day $x$.'+table(['$x$']+x,[['$y$']+y]),[
 part('a','Find $a$ and $b$ in $y=ax+b$, and interpret the gradient.',4,('M1','Regress cumulative sales on the day number.'),('A1',rf'$a={ans(a)}$.'),('A1',rf'$b={ans(b)}$.'),('R1',rf'The gradient predicts an increase of approximately ${ans(a)}$ notebooks in cumulative sales per additional day.')),
 part('b','Estimate sales by the end of day 5, to the nearest notebook.',2,('M1',rf'$y={f(a)}(5)+{f(b)}={f(a*5+b)}$.'),('A1',rf'{round(a*5+b)} notebooks.'))])
data=[4.2,7.6,9.4,12.8,15.0,17.6,20.2,23.8,28.4,40.0];mean=np.mean(data);q1=9.4;q3=23.8;iqr=q3-q1
Q(35,'Call-duration summary',D,True,'The durations of ten help-desk calls in minutes are:\n\n'+', '.join(map(str,data))+'. Use the median-of-halves convention for quartiles. The median is labelled $p$ on a boxplot.',[
 part('a','Find the mean duration.',2,('M1',rf'The total is ${f(sum(data))}$; divide by 10.'),('A1',rf'Mean $={ans(mean)}$ minutes.')),
 part('b','Find $p$ and the interquartile range.',3,('A1','$p=(15.0+17.6)/2=16.3$.'),('M1','$Q_1=9.4$, $Q_3=23.8$.'),('A1',r'$\mathrm{IQR}=14.4$ minutes.')),
 part('c','Calls longer than $r$ minutes are upper outliers. Find $r$.',2,('M1',r'$r=Q_3+1.5\mathrm{IQR}$.'),('A1','$r=23.8+1.5(14.4)=45.4$ minutes.'))])
basicreg(36,'Temperature and hot-drink sales',[7,10,13,16,19,22,25],[180,169,151,143,126,109,100],'T','N',18,marks=(4,2),context='A café records average temperature $T$ in °C and hot drinks sold $N$ on seven days. ')
x=[0,1,2,3];freq=[7,5,4,2];mean=sum(i*j for i,j in zip(x,freq))/sum(freq);var=sum(j*(i-mean)**2 for i,j in zip(x,freq))/sum(freq)
Q(37,'A missing frequency',D,True,'The table gives overtime hours worked by a group of employees. The mean is $19/18$ hours.'+table(['Hours','0','1','2','3'],[['Frequency','7','$k$','4','2']]),[
 part('a','Find $k$.',2,('M1',r'$\frac{k+14}{k+13}=\frac{19}{18}$, so $18k+252=19k+247$.'),('A1','$k=5$.')),
 part('b','Find the population standard deviation.',2,('M1',r'$\sigma=\sqrt{\frac{5+4(4)+2(9)}{18}-(19/18)^2}$.'),('A1',rf'$\sigma={ans(math.sqrt(var))}$ hours.'))])
vals=[1,3,5,7];freq=[3,5,6,2];mean=sum(v*c for v,c in zip(vals,freq))/16;var=sum(v*v*c for v,c in zip(vals,freq))/16-mean**2
Q(38,'Statistics from a frequency table',D,True,'Use the following frequency table.'+table(['Value']+vals,[['Frequency']+freq]),[
 part('a','Find (i) the mode; (ii) the range.',3,('A1','The mode is 5.'),('M1','Range = maximum minus minimum.'),('A1','$7-1=6$.')),
 part('b','Find (i) the mean; (ii) the population variance.',4,('M1',r'$\bar x=\frac{3+15+30+14}{16}$.'),('A1',rf'Mean $={ans(mean)}$.'),('M1',r'$\operatorname{Var}=\frac{3+45+150+98}{16}-\bar x^2$.'),('A1',rf'Variance $={ans(var)}$.'))])
pts=[(0,0),(1,8),(2,24),(3,48),(4,72),(5,88),(6,96)]
Q(39,'Distances from an ogive',D,True,'The graph shows cumulative frequencies for distances travelled by 96 pupils. Use straight-line interpolation.',[
 part('a','Find the median distance.',2,('M1','Read the distance at cumulative frequency $96/2=48$.'),('A1','The median is 3 km.')),
 part('b','Find the number travelling between 2 km and 4 km.',3,('A1','Cumulative frequencies are 24 and 72.'),('M1','Subtract the lower cumulative frequency from the upper one.'),('A1','$72-24=48$ pupils.')),
 part('c','Find the percentage travelling more than 4.5 km.',2,('M1','The cumulative frequency at 4.5 is 80, so 16 travel further.'),('A1',r'$\frac{16}{96}(100)=16\frac23\%$.'))],diagram=curve(pts,'Distance (km)'))
Q(40,'Normal tails and a percentile',N,True,r'$X\sim N(60,12^2)$.',[
 part('a',r'Sketch the normal density and shade the region representing $P(X\ge54)$.',2,('A1','Draw a bell-shaped curve centred at 60 and mark 54 to the left of the mean.'),('A1','Shade the full area under the curve to the right of 54.')),
 part('b',r'Find $P(X\ge54)$.',2,('M1','$z=(54-60)/12=-0.5$.'),('A1',rf'$P(X\ge54)={ans(norm.sf(-.5))}$.')),
 part('c',r'Find $k$ such that $P(X\le k)=0.85$.',2,('M1',r'$k=60+12\Phi^{-1}(0.85)$.'),('A1',rf'$k={ans(60+12*norm.ppf(.85))}$.'))])
Q(41,'Solving an independence equation',P,False,r'$A$ and $B$ are independent, with $P(A)=0.36$ and $P(A\cup B)=0.8$. Find $P(B)$.',[part('','',5,('M1','Set $p=P(B)$ and use the addition rule.'),('A1',r'$0.8=0.36+p-P(A\cap B)$.'),('M1',r'Independence gives $P(A\cap B)=0.36p$.'),('A1','$0.44=0.64p$.'),('A1','$p=11/16=0.6875$.'))])
Q(42,'Same or different colours',P,False,'A box holds 9 green and 3 blue counters. Two are drawn without replacement.',[
 part('a','Find the probability the counters have the same colour.',3,('M1','Add green-green and blue-blue probabilities.'),('A1',r'$\frac9{12}\frac8{11}+\frac3{12}\frac2{11}=\frac{78}{132}$.'),('A1',r'$\frac{13}{22}$.')),
 part('b','Find the probability they have different colours.',2,('M1','Take the complement.'),('A1',r'$1-\frac{13}{22}=\frac9{22}$.'))])
Q(43,'Competition scores',D,False,'Forty-eight players obtain the following scores in a target competition.'+table(['Score','0','1','2','3','4','5'],[['Frequency','3','6','9','12','11','7']]),[
 part('a','Find the probability a selected player scores at least 3.',2,('M1','There are $12+11+7=30$ qualifying players.'),('A1','$30/48=5/8$.')),
 part('b','Find the mean score.',2,('M1',r'$\bar x=\frac{6+18+36+44+35}{48}$.'),('A1',r'$\bar x=\frac{139}{48}$.'))])
Q(44,'Complements and conditioning',P,False,r'$P(A)=0.62$ and $P(A\cap B)=0.18$.',[
 part('a',r'Find $P(A\cap B^{\prime})$.',2,('M1','Subtract the overlap from $P(A)$.'),('A1','$0.62-0.18=0.44$.')),
 part('b',r'Given $P(A^{\prime}\cap B^{\prime})=0.22$, find $P(A\mid B^{\prime})$.',4,('M1',r'Partition $B^{\prime}$ into its A and non-A regions.'),('A1',r'$P(B^{\prime})=0.44+0.22=0.66$.'),('M1',r'$P(A\mid B^{\prime})=\frac{0.44}{0.66}$.'),('A1','$2/3$.'))])
Q(45,'Normal interquartile range',N,True,r'$X\sim N(100,18^2)$. Find the interquartile range of $X$.',[part('','',6,('M1','The quartiles have cumulative probabilities 0.25 and 0.75.'),('A1',rf'$z_1={f(norm.ppf(.25))}$, $z_3={f(norm.ppf(.75))}$.'),('M1','Convert each standard-normal quartile using $x=100+18z$.'),('A1',rf'$Q_1={f(100+18*norm.ppf(.25))}$ and $Q_3={f(100+18*norm.ppf(.75))}$.'),('M1','Subtract $Q_1$ from $Q_3$.'),('A1',rf'$\mathrm{{IQR}}={ans(36*norm.ppf(.75))}$.'))])
# 46-60
Q(46,'A fair coin game',R,False,'A biased coin shows heads with probability 0.6. A player pays USD 18 to toss it once. Heads earns no payout; tails earns a payout of USD $k$. Find $k$ if the game is fair.',[part('','',5,('M1','Fairness means expected net gain is zero.'),('A1','Net gains are $-18$ and $k-18$.'),('M1','$0.6(-18)+0.4(k-18)=0$.'),('A1','$0.4k-18=0$.'),('A1','$k=45$.'))])
x=[0,1,2,3,4];y=[28000,25600,23400,21100,19000];a,b,r=reg(x,y);value=26000*.91**6
Q(47,'Depreciation and regression',L,True,'On 1 January 2025, Mina buys a car for USD 26,000. Its value falls by 9% each complete year. A second car’s value after $t$ years is recorded below.'+table(['$t$']+x,[['Value (USD)']+y]),[
 part('a','Find Mina’s car value on 1 January 2031.',3,('M1','Six complete years have elapsed.'),('A1','$V=26000(0.91)^6$.'),('A1',rf'$V={value:.2f}$ USD.')),
 part('b','Fit a linear model to the second car’s data. Estimate the difference in the cars’ values on 1 January 2031.',3,('A1',rf'The second model is $V={ans(a)}t+{ans(b)}$.'),('M1',rf'At $t=6$, its predicted value is ${a*6+b:.2f}$ USD.'),('A1',rf'Mina’s car is worth ${value-(a*6+b):.2f}$ USD more under these models.'))])
Q(48,'Interpreting cooling data',L,True,'A room cools after a heater is switched off. The measurements are:'+table(['$t$ (hours)','0','3','6','9','12','15'],[['$T$ (°C)','24.0','20.8','16.9','13.4','10.2','6.5']])+'\n'+r'A fitted model is $T=-1.17t+24.0$ for $0\le t\le15$.',[
 part('a','State (i) the independent variable; (ii) the highest recorded temperature.',2,('A1','Elapsed time $t$ is the independent variable.'),('A1','24.0°C.')),
 part('b','Choose the most appropriate correlation coefficient: $0.998$, $0.3$, $0$, $-0.3$, $-0.998$.',2,('R1','Temperature decreases almost linearly with time.'),('A1',r'$r\approx-0.998$.')),
 part('c','Use the model to predict the temperature decrease over a 3-hour interval.',2,('M1','Multiply the magnitude of the gradient by 3.'),('A1','$1.17(3)=3.51$°C.'))])
sd=5/norm.ppf(.88)
Q(49,'Finding a normal standard deviation',N,True,'$X$ is normally distributed with mean 20. The probability that $20<X<25$ is 0.38.',[
 part('a','Find $P(X>25)$.',2,('M1','The area above the mean is 0.5.'),('A1','$0.5-0.38=0.12$.')),
 part('b','Find the standard deviation.',5,('M1','$P(X<25)=0.88$.'),('A1',rf'$z=\Phi^{{-1}}(0.88)={f(norm.ppf(.88))}$.'),('M1',r'$\frac{25-20}{\sigma}=z$.'),('A1',r'$\sigma=5/z$.'),('A1',rf'$\sigma={ans(sd)}$.'))])
Q(50,'A fair target game',R,False,'An archer takes one shot. Probabilities and net scores are shown below. A fair game has expected net score zero.'+table(['Outcome','A','B','C','Miss'],[['Probability','0.1','0.2','0.4','$p$'],['Net score','12','6','2','$-k$']]),[
 part('a','Find the probability of missing.',3,('M1','Add the probabilities of the three scoring regions.'),('A1',r'$P(\text{hit})=0.1+0.2+0.4=0.7$.'),('A1','$p=1-0.7=0.3$.')),
 part('b','Find $k$ for a fair game.',4,('M1','Set expected net score equal to zero.'),('A1','$12(0.1)+6(0.2)+2(0.4)-0.3k=0$.'),('A1','$3.2=0.3k$.'),('A1','$k=32/3$.'))])
p=norm.sf((4.8-5)/.12)
Q(51,'Normal heights and a binomial sample',N,True,r'Animal heights are modelled by $H\sim N(5.0,0.12^2)$ metres. Heights of sampled animals are independent.',[
 part('a',r'Find $P(H\ge4.8)$.',2,('M1',r'$z=\frac{4.8-5.0}{0.12}$.'),('A1',rf'$p={ans(p)}$.')),
 part('b','Ten animals are selected. Find the probability that more than eight are at least 4.8 m tall.',3,('M1',rf'$Y\sim B(10,{f(p)})$.'),('M1','$P(Y>8)=P(Y=9)+P(Y=10)$; use the unrounded $p$.'),('A1',rf'${ans(binom.sf(8,10,p))}$.'))])
Q(52,'Three consequences of event data',P,False,r'$P(A)=0.6$, $P(A\cap B)=0.18$ and $P(A^{\prime}\cap B^{\prime})=0.16$.',[
 part('a',r'Find $P(A\cap B^{\prime})$.',2,('M1','Subtract the overlap from $A$.'),('A1','$0.6-0.18=0.42$.')),
 part('b',r'Find (i) $P(A\cup B)$; (ii) $P(B)$; (iii) $P(A\mid B^{\prime})$.',4,('A1',r'$P(A\cup B)=0.84$.'),('A1','$P(B)=0.84-0.6+0.18=0.42$.'),('M1',r'$P(A\mid B^{\prime})=\frac{0.42}{0.42+0.16}$.'),('A1','$21/29$.'))])
Q(53,'An algebraic probability parameter',P,False,r'$P(A)=3k$, $P(B)=k$, $P(A\cap B)=k^2/2$ and $P(A\cup B)=0.96875$.',[
 part('a','Find $k$.',3,('M1','$4k-k^2/2=0.96875$.'),('A1','The roots are $k=0.25$ and $k=7.75$.'),('R1','Reject 7.75 because a probability would exceed 1; $k=0.25$.')),
 part('b',r'Find $P(A^{\prime}\cap B)$.',3,('M1',r'Use $P(B)-P(A\cap B)$.'),('A1','$0.25-(0.25)^2/2=0.21875$.'),('A1',r'$P(A^{\prime}\cap B)=7/32$.'))])
vals=[1,3,5,7];freq=[2,4,6,3];mean=sum(v*c for v,c in zip(vals,freq))/sum(freq);extra=[2,10];allvals=sum(([v]*c for v,c in zip(vals,freq)),[])+extra
Q(54,'Correcting an omitted pair of values',D,True,'The table records goals scored by players. The mean is $13/3$.'+table(['Goals','1','3','5','7'],[['Players','2','4','$k$','3']]),[
 part('a','Find $k$.',3,('M1',r'$\frac{2+12+5k+21}{9+k}=\frac{13}{3}$.'),('A1','$105+15k=117+13k$.'),('A1','$k=6$.')),
 part('b','Two omitted players scored 2 and 10 goals. Find the corrected mean and population standard deviation.',3,('M1','Add both values and increase the total frequency from 15 to 17.'),('A1',rf'The corrected mean is $77/17={ans(np.mean(allvals))}$.'),('A1',rf'$\sigma=\sqrt{{439/17-(77/17)^2}}={ans(np.std(allvals))}$.'))])
freq=[10,40,50,65,45,30];mean=sum(v*c for v,c in zip([20,60,100,140,180,220],freq))/240
Q(55,'Grouped screen-time survey',D,True,'The boxplot summarises the screen times of240 students. It is known that 50 students spend at most 80 minutes daily. The grouped table is incomplete.'+table(['Daily minutes $x$','Frequency'],[[r'$0\le x\le40$',10],[r'$40<x\le80$','$p$'],[r'$80<x\le120$',50],[r'$120<x\le160$',65],[r'$160<x\le200$',45],[r'$200<x\le240$','$q$']])+'\nThe sample was chosen using a random-number generator to select student IDs.',[
 part('a','State the median.',1,('A1','132 minutes.')),
 part('b','Find $p$ and $q$.',2,('A1','$p=50-10=40$.'),('A1','$q=240-(10+40+50+65+45)=30$.')),
 part('c',r'State the midpoint of $80<x\le120$ and estimate the mean.',3,('A1','The midpoint is 100.'),('M1',r'Use $\sum f\times\text{midpoint}/240$.'),('A1',rf'Estimated mean $={ans(mean)}$ minutes.')),
 part('d','Name the sampling method.',1,('A1','Simple random sampling.'))],diagram=boxplot([0,88,132,180,240]))
Q(56,'Conditional probability from a union',P,False,r'$P(A)=0.4$, $P(B)=0.55$, $P(A\cup B)=0.75$. Find $P(A\mid B)$.',[part('','',5,('M1','Use the addition rule to obtain the intersection.'),('A1',r'$P(A\cap B)=0.4+0.55-0.75=0.2$.'),('M1',r'$P(A\mid B)=P(A\cap B)/P(B)$.'),('A1','$0.2/0.55$.'),('A1','$4/11$.'))])
Q(57,'Expectation determines two probabilities',R,False,'The distribution below has $E(X)=2.7$. Find $a$ and $b$.'+table(['$x$','1','2','3','4'],[['$P(X=x)$','0.15','$a$','0.25','$b$']]),[part('','',5,('M1','Total probability gives $a+b=0.6$.'),('M1','Expectation gives $0.15+2a+0.75+4b=2.7$.'),('A1','$2a+4b=1.8$.'),('A1','$b=0.3$.'),('A1','$a=0.3$.'))])
Q(58,'Proving independence of a complement',P,False,r'$P(A\cup B)=0.8$, $P(A\cap B)=0.3$ and $P(A\mid B)=0.5$.',[
 part('a','Find $P(B)$.',2,('M1','$0.5=0.3/P(B)$.'),('A1','$P(B)=0.6$.')),
 part('b','Find $P(A)$.',2,('M1','$P(A)+0.6-0.3=0.8$.'),('A1','$P(A)=0.5$.')),
 part('c',r'Show that $A^{\prime}$ and $B$ are independent.',2,('A1',r'$P(A^{\prime}\cap B)=0.6-0.3=0.3$.'),('R1',r'$P(A^{\prime})P(B)=0.5(0.6)=0.3$, equal to the intersection.'))])
n=50;p=.06
Q(59,'Defective components in boxes',B,True,'Each component is independently defective with probability 0.06. A box contains 50 components. Let $X$ count defectives in a box.',[
 part('a',r'Find (i) $P(X=1)$; (ii) $P(X\ge2)$.',4,('M1',r'$X\sim B(50,0.06)$ and $P(X=1)=50(0.06)(0.94)^{49}$.'),('A1',rf'${ans(binom.pmf(1,n,p))}$.'),('M1',r'$P(X\ge2)=1-P(X\le1)$.'),('A1',rf'${ans(binom.sf(1,n,p))}$.')),
 part('b',r'Given $X\ge2$, find $P(X\le4\mid X\ge2)$.',2,('M1',r'$\frac{P(2\le X\le4)}{P(X\ge2)}$.'),('A1',rf'${ans((binom.cdf(4,n,p)-binom.cdf(1,n,p))/binom.sf(1,n,p))}$.')),
 part('c','Four boxes are ordered. Find the probability that there are between 1 and 14 defective components inclusive.',2,('M1',r'$Y\sim B(200,0.06)$; calculate $P(1\le Y\le14)$.'),('A1',rf'${ans(binom.cdf(14,200,p)-binom.pmf(0,200,p))}$.'))])
Q(60,'The smaller of two dice',R,False,'Two fair four-sided dice, numbered 1 to 4, are rolled independently. Let $X$ be the smaller score.'+table(['$x$','1','2','3','4'],[['$P(X=x)$','$p$','5/16','$q$','1/16']]),[
 part('a','Find $p$ and $q$.',3,('M1',r'Count ordered outcomes, or use $P(X\ge k)=((5-k)/4)^2$.'),('A1','$p=1-(3/4)^2=7/16$.'),('A1','$q=(2/4)^2-(1/4)^2=3/16$.')),
 part('b','Find $E(X)$.',3,('M1',r'Use $\sum xP(X=x)$.'),('A1','$E(X)=(7+10+9+4)/16$.'),('A1','$E(X)=15/8$.'))])
save()
# 61-74
Q(61,'Two regression lines and their intersection',L,False,'An agency records apartment area $A$ square metres and monthly rent $R$ USD. The areas have lower quartile 65 and upper quartile 95. The regression lines are $A=0.2R-20$ and $R=3A+280$.',[
 part('a','Find the smallest area not classified as a lower outlier.',3,('A1',r'$\mathrm{IQR}=95-65=30$.'),('M1','Lower boundary $=65-1.5(30)$.'),('A1','20 square metres.')),
 part('b','Estimate the area when rent is USD 500.',2,('M1','Use the regression of $A$ on $R$.'),('A1','$A=0.2(500)-20=80$ square metres.')),
 part('c','Find the mean rent.',2,('M1',r'The means lie on both lines: $\bar A=0.2(3\bar A+280)-20$.'),('A1',r'$\bar A=90$ and $\bar R=550$ USD.'))],notes='Regression slopes have product 0.6, within [0,1]. Source slopes had product above 1, so the variant corrects this inconsistency while retaining the tested method.')
Q(62,'A probability parameter and expectation',R,False,'The distribution of $X$ is shown below.'+table(['$x$','0','1','2','4'],[['$P(X=x)$','$p$','0.2','$2p$','0.35']]),[
 part('a','Find $p$.',3,('M1','The probabilities sum to one.'),('A1','$3p+0.55=1$.'),('A1','$p=0.15$.')),
 part('b','Find $E(X)$.',3,('M1',r'Use $\sum xP(X=x)$.'),('A1','$E(X)=0+0.2+2(0.3)+4(0.35)$.'),('A1','$E(X)=2.2$.'))])
x=[35,45,55,65,75,85,95];y=[540,670,790,940,1050,1210,1320];a,b,r=reg(x,y);fixed=350;variable=6;threshold=(fixed-b)/(a-variable);needed=math.floor(threshold)+1
Q(63,'Revenue, costs and profit',L,True,'A café records customers $x$ and daily revenue $y$ USD.'+table(['$x$']+x,[['$y$']+y])+'\n'+rf'Daily fixed costs are USD {fixed}; serving each customer costs USD {variable}.',[
 part('a','Find Pearson’s $r$ and interpret it.',3,('M1','Calculate correlation from the paired data.'),('A1',rf'$r={ans(r)}$.'),('R1','There is a strong positive linear association.')),
 part('b','State the regression line of $y$ on $x$.',1,('A1',rf'$y={ans(a)}x+{ans(b)}$.')),
 part('c','Estimate revenue for 72 customers, to the nearest USD.',2,('M1',rf'$y={f(a)}(72)+{f(b)}$.'),('A1',rf'USD {round(72*a+b)}.')),
 part('d','Does the model predict a profit for 40 customers? Justify.',2,('A1',rf'Revenue ${ans(a*40+b)}$ and cost $350+6(40)=590$ USD.'),('R1',rf'The predicted profit is USD {a*40+b-590:.2f}, so {"yes" if a*40+b>590 else "no"}.')),
 part('e','Find a profit expression and the least whole number of customers needed for a positive profit.',4,('M1','Profit = revenue minus total cost.'),('A1',rf'$P(x)={ans(a-variable)}x{ans(b-fixed):s}$.'),('M1',rf'Positive profit requires $x>{f(threshold)}$.'),('A1',rf'At least {needed} customers.'))])
Q(64,'Disjoint probability regions',P,False,r'$P(A^{\prime}\cap B)=P(A\cap B^{\prime})=0.25$ and $P(A\cap B)=0.15$.',[
 part('a',r'Find $P(A^{\prime}\cap B^{\prime})$.',2,('M1','Subtract all three interior regions from 1.'),('A1','$1-0.25-0.25-0.15=0.35$.')),
 part('b',r'Find $P(B^{\prime})$.',2,('M1','Add A-only and neither.'),('A1','$0.25+0.35=0.6$.')),
 part('c',r'Find $P(A^{\prime}\mid B^{\prime})$.',2,('M1',r'Use $P(A^{\prime}\cap B^{\prime})/P(B^{\prime})$.'),('A1','$0.35/0.6=7/12$.'))])
mu=45;sd=6;limit=53;cdf=norm.cdf((limit-mu)/sd);k=mu+sd*norm.ppf(cdf-.45)
Q(65,'A normal interval with an unknown endpoint',N,True,'Task completion time $T$ is normally distributed with mean 45 minutes and standard deviation 6 minutes.',[
 part('a','Find $P(T<53)$.',3,('M1','$z=(53-45)/6$.'),('M1',r'$P(T<53)=\Phi(8/6)$.'),('A1',rf'${ans(cdf)}$.')),
 part('b','Given $P(k<T<53)=0.45$, find $k$.',4,('M1','Subtract 0.45 from $P(T<53)$.'),('A1',rf'$P(T<k)={ans(cdf-.45)}$.'),('M1',rf'$k=45+6\Phi^{{-1}}({f(cdf-.45)})$.'),('A1',rf'$k={ans(k)}$ minutes.'))])
Q(66,'A second moment and variance',R,False,'$X$ has the following distribution.'+table(['$x$','-1','0','2','3'],[['$P(X=x)$','0.2','0.3','$p$','0.1']]),[
 part('a','Find $p$.',1,('A1','$p=1-0.2-0.3-0.1=0.4$.')),
 part('b','Find $E(X^2)$.',2,('M1','$E(X^2)=1(0.2)+0+4(0.4)+9(0.1)$.'),('A1','$E(X^2)=2.7$.')),
 part('c',r'Find $\operatorname{Var}(X)$.',3,('A1','$E(X)=-0.2+0.8+0.3=0.9$.'),('M1',r'$\operatorname{Var}(X)=E(X^2)-[E(X)]^2$.'),('A1','$2.7-0.9^2=1.89$.'))])
Q(67,'Student subjects and dependent selections',P,False,'Of 32 students, 20 study chemistry $C$, 15 study physics $P$, and 5 study neither. The Venn labels are $p$ for chemistry only, $q$ for physics only, $r$ for both and $s$ for neither.',[
 part('a','Find $s,r,p,q$.',5,('A1','$s=5$.'),('M1','The union has $32-5=27$ students.'),('A1','$r=20+15-27=8$.'),('A1','$p=20-8=12$.'),('A1','$q=15-8=7$.')),
 part('b',r'Find $P(P\mid C)$ and determine whether the subjects are independent.',5,('M1','Condition on the 20 chemistry students.'),('A1',r'$P(P\mid C)=8/20=2/5$.'),('A1','$P(P)=15/32$.'),('M1','Compare $2/5$ and $15/32$.'),('R1','They differ, so the events are not independent.')),
 part('c','Two distinct students are selected in order. Find the probability that the first studies only chemistry and the second only physics.',4,('M1','The first probability is $12/32$.'),('A1','There remain 31 students, including all 7 physics-only students.'),('M1','Multiply $12/32$ by $7/31$.'),('A1','$21/248$.'))],diagram=venn('C','P'))
Q(68,'Choosing a loaded die',P,False,'A bag contains six dice: five fair six-sided dice and one die with a 6 on every face. Two dice are selected without replacement and rolled.',[
 part('a','Find the probability both scores are 6.',3,('M1','The probability of including the loaded die is $2/6=1/3$; otherwise it is $2/3$.'),('A1','$P(66)=(1/3)(1/6)+(2/3)(1/36)$.'),('A1','$P(66)=2/27$.')),
 part('b','Given both scores are 6, find the probability the loaded die was selected.',2,('M1','Use $(1/3)(1/6)/P(66)$.'),('A1',r'$P(\text{loaded}\mid66)=3/4$.'))])
Q(69,'Inferring a return rate',P,False,'An online shop has return probability $p$. A reviewer is observed with probability 0.9 after a return and 0.6 after no return.',[
 part('a','Draw a fully labelled probability tree.',2,('A1','First branches: return $p$, no return $1-p$.'),('A1','After return, review/no review: $0.9,0.1$; after no return: $0.6,0.4$.')),
 part('b',r'Given $P(\text{return}\mid\text{review})=0.25$, find $p$.',4,('M1',r'$P(\text{review})=0.9p+0.6(1-p)$.'),('M1',r'$\frac{0.9p}{0.9p+0.6(1-p)}=0.25$.'),('A1','$0.9p=0.075p+0.15$.'),('A1','$p=2/11$.'))])
pts=[(0,0),(20,8),(40,24),(60,40),(80,64),(100,80),(120,112),(140,136),(160,152),(180,160)]
# quantiles median100, q1=60, q3=126.6667; CF70=52 CF130=124
Q(70,'Cumulative frequencies and a boxplot',D,True,'A survey records daily screen time in minutes for 160 students. Use straight-line interpolation on the graph.',[
 part('a','Find the median screen time.',2,('M1','Median corresponds to cumulative frequency 80.'),('A1','100 minutes.')),
 part('b','Find the number of students within 30 minutes of the median.',3,('A1','The interval is 70 to 130 minutes.'),('M1','Read cumulative frequencies 52 and 124.'),('A1','$124-52=72$ students.')),
 part('c','Only 5% exceed $k$ minutes. Find $k$.',3,('M1','Use cumulative frequency $0.95(160)=152$.'),('M1','Read the matching horizontal coordinate.'),('A1','$k=160$ minutes.')),
 part('d','State the percentile represented by the upper edge of the box in a boxplot.',1,('A1','The75th percentile (upper quartile).')),
 part('e','Find the lower quartile $p$ and the interquartile range.',4,('M1','Quartiles occur at cumulative frequencies 40 and 120.'),('A1','$p=60$.'),('A1',r'$Q_3=120+(8/24)(20)=126\frac23$.'),('A1',r'$\mathrm{IQR}=66\frac23$ minutes.')),
 part('f','Find the lower outlier boundary $r$.',3,('M1',r'$r=Q_1-1.5\mathrm{IQR}$.'),('A1','$r=60-1.5(200/3)$.'),('A1','$r=-40$ minutes, so no non-negative screen time is a lower outlier.'))],diagram=curve(pts,'Screen time (minutes)'))
# two mathematically admissible roots explicitly requested to fix source ambiguity
Q(71,'An independence equation with a repeated root',P,False,r'Independent events $A,B$ satisfy $P(A\cap B^{\prime})=0.16$ and $P(A^{\prime}\cap B)=0.36$. Let $x=P(A\cap B)$.',[
 part('a','Express $P(A)$ and $P(B)$ in terms of $x$.',2,('A1','$P(A)=x+0.16$.'),('A1','$P(B)=x+0.36$.')),
 part('b','Find $x$.',2,('M1','$x=(x+0.16)(x+0.36)$, giving $x^2-0.48x+0.0576=0$.'),('A1','$(x-0.24)^2=0$, so $x=0.24$.')),
 part('c',r'Find $P(B\mid A)$.',2,('M1','Use independence or $0.24/(0.24+0.16)$.'),('A1',r'$P(B\mid A)=0.6$.'))])
x=[40,50,60,70,80,90,100,110,120,130];y=[1030,1170,1310,1460,1580,1730,1850,2000,2140,2260];a,b,r=reg(x,y);price=31.5;needed=math.floor(b/(price-a))+1
Q(72,'Production-cost regression',L,True,'A workshop records daily production $x$ and total cost $y$ USD.'+table(['$x$']+x,[['$y$']+y])+'\n'+rf'Each item sells for USD {price:.2f}.',[
 part('a','Find the regression line $y=ax+b$.',2,('A1',rf'$a={ans(a)}$.'),('A1',rf'$b={ans(b)}$.')),
 part('b','Interpret the gradient and intercept.',2,('R1',rf'The gradient predicts an additional USD {a:.2f} cost per extra item.'),('R1',rf'The intercept predicts fixed daily cost of about USD {b:.2f}; this is an extrapolated interpretation.')),
 part('c','Estimate the cost of producing 100 items.',2,('M1','Substitute $x=100$ in the model.'),('A1',rf'USD {a*100+b:.2f}.')),
 part('d','Find the least daily production giving a positive modelled profit.',3,('M1',rf'$31.5x>{f(a)}x+{f(b)}$.'),('A1',rf'$x>{f(b/(31.5-a))}$.'),('A1',rf'{needed} items.')),
 part('e','Comment on using this model (i) for 1000 items; (ii) to predict production when cost is USD 1900.',4,('R1','1000 lies far beyond the observed production range 40–130.'),('R1','Such extrapolation is unreliable; capacity or economies of scale may change costs.'),('R1','The fitted line predicts cost from production, not production from cost.'),('R1','For (ii), fit the regression of $x$ on $y$ rather than invert this regression.'))])
n=60;p=.07
Q(73,'At least one defective toy',B,True,'Each toy is independently defective with probability 0.07. Sixty toys are selected; $X$ is the defective count.',[
 part('a','Find $E(X)$.',2,('M1',r'$X\sim B(60,0.07)$; use $np$.'),('A1','$E(X)=4.2$.')),
 part('b',r'Find $P(X\ge1)$.',3,('M1','Use the complement $1-P(X=0)$.'),('A1','$1-(0.93)^{60}$.'),('A1',rf'${ans(binom.sf(0,n,p))}$.')),
 part('c','Given at least one is defective, find the probability at most four are defective.',3,('M1',r'The numerator is $P(1\le X\le4)$.'),('M1',r'$\frac{P(X\le4)-P(X=0)}{1-P(X=0)}$.'),('A1',rf'${ans((binom.cdf(4,n,p)-binom.pmf(0,n,p))/binom.sf(0,n,p))}$.'))])
Q(74,'Selecting a valid probability root',P,False,r'$P(A)=k$, $P(B)=2k$, $P(A\cap B)=4k^2-0.12$, and $P(A\cup B)=0.66$. Find $k$.',[part('','',5,('M1','$0.66=3k-(4k^2-0.12)$.'),('A1','$4k^2-3k+0.54=0$.'),('A1','The roots are $k=0.3$ and $k=0.45$.'),('R1','For $k=0.45$, the intersection is $0.69>P(A)=0.45$, impossible.'),('A1','Therefore $k=0.3$.'))])
# 75-90
Q(75,'Choosing a bag with a biased coin',P,False,'Bag A contains 5 red and 3 green balls. Bag B contains 3 red and 2 green balls. A coin shows heads with probability $2/5$. Heads selects bag A; tails selects bag B.',[
 part('a','A ball is selected independently from each bag. Find the probability the colours differ.',4,('M1','Consider red-green and green-red.'),('A1','Their probabilities are $(5/8)(2/5)$ and $(3/8)(3/5)$.'),('M1','Add these disjoint cases.'),('A1','$19/40$.')),
 part('b','Draw the fully labelled tree for the coin-and-one-ball experiment.',4,('A1','Coin branches $H=2/5$, $T=3/5$.'),('A1','Bag A branches red $5/8$, green $3/8$.'),('A1','Bag B branches red $3/5$, green $2/5$.'),('A1','The tree shows all four terminal paths $HR,HG,TR,TG$.')),
 part('c','Find the probability the selected ball is red.',4,('M1','Use total probability over the chosen bags.'),('A1','$P(HR)=(2/5)(5/8)=1/4$.'),('A1','$P(TR)=(3/5)(3/5)=9/25$.'),('A1','$P(R)=1/4+9/25=61/100$.')),
 part('d','Given the ball is red, find the probability the coin showed heads.',3,('M1',r'Use $P(H\cap R)/P(R)$.'),('A1','$(1/4)/(61/100)$.'),('A1','$25/61$.'))])
mu=4.2;sd=.6;tail=.06;w=mu+sd*norm.ppf(tail);low=3.0
Q(76,'A conditional lower normal tail',N,True,'Packet masses $W$ grams follow $N(4.2,0.6^2)$. A packet is small if $W<w$. Exactly 6% are small.',[
 part('a','Find $w$.',3,('M1','$P(W<w)=0.06$.'),('M1',r'$w=4.2+0.6\Phi^{-1}(0.06)$.'),('A1',rf'$w={ans(w)}$ grams.')),
 part('b','A small packet is selected. Find the probability it weighs at least 3.0 grams.',3,('M1',r'The required event is $3.0\le W<w$ conditional on $W<w$.'),('M1',r'$\frac{0.06-P(W<3.0)}{0.06}$.'),('A1',rf'${ans((.06-norm.cdf((3-mu)/sd))/.06)}$.'))])
def linear_rv(n,title,probs,base,unit):
 vals=list(range(1,len(probs)+1));ex=sum(v*p for v,p in zip(vals,probs));ex2=sum(v*v*p for v,p in zip(vals,probs));vx=ex2-ex**2
 Q(n,title,R,True,'The number of passengers $X$ has this distribution.'+table(['$x$']+vals,[['$P(X=x)$']+probs])+'\n'+rf'The journey charge is USD {base:.2f} plus USD {unit:.2f} per passenger. Let $Y$ be the charge. It is given that $\operatorname{{Var}}(X)={f(vx)}$.',[
  part('a','Find $E(Y)$.',4,('M1',r'Use $E(X)=\sum xP(X=x)$.'),('A1',rf'$E(X)={ans(ex)}$.'),('M1',rf'$Y={base}+{unit}X$, so $E(Y)={base}+{unit}E(X)$.'),('A1',rf'$E(Y)={ans(base+unit*ex)}$ USD.')),
  part('b',r'Find $\operatorname{Var}(Y)$.',2,('M1',rf'$\operatorname{{Var}}(Y)=({unit})^2\operatorname{{Var}}(X)$.'),('A1',rf'$\operatorname{{Var}}(Y)={ans(unit**2*vx)}$ USD$^2$.'))])
linear_rv(77,'A toll charged per passenger',[.12,.38,.32,.18],5.2,1.4)
def normal_two(n,title,lo,plo,hi,phi,marks,context):
 zl,zh=norm.ppf(plo),norm.ppf(phi);s=(hi-lo)/(zh-zl);m=lo-s*zl
 steps=[('M1',rf'Convert the lower cumulative probability to $z_L=\Phi^{{-1}}({plo})={f(zl)}$.'),('A1',rf'${lo}=\mu+({f(zl)})\sigma$.'),('M1',rf'Convert the upper cumulative probability to $z_H=\Phi^{{-1}}({phi})={f(zh)}$.'),('A1',rf'${hi}=\mu+({f(zh)})\sigma$.'),('A1',rf'$\sigma=({hi}-{lo})/({f(zh-zl)})={ans(s)}$.'),('A1',rf'$\mu={lo}-({f(zl)})\sigma={ans(m)}$.')]
 if marks==7:steps.insert(4,('M1','Subtract the two equations to eliminate the mean.'))
 Q(n,title,N,True,context+rf' The variable is normally distributed. It is known that $P(X<{lo})={plo}$ and $P(X<{hi})={phi}$. Find $\mu$ and $\sigma$.',[part('','',marks,*steps)])
 return m,s
normal_two(78,'Tree heights from two percentiles',2.2,.02,2.9,.85,6,'Let $X$ be the height in metres of a dwarf tree.')
mu=502;sd=18;lo=465;target=.002;z=norm.ppf(target)
Q(79,'Adjusting a filling machine',N,True,'Filled bag masses $X$ grams are normally distributed. A bag is underweight if it weighs less than 465 g.',[
 part('a',r'Initially $\mu=502$ and $\sigma=18$. Find the underweight probability.',2,('M1',r'$P(X<465)=\Phi((465-502)/18)$.'),('A1',rf'${ans(norm.cdf((lo-mu)/sd))}$.')),
 part('b',r'Keeping $\sigma=18$, find the mean that makes the underweight probability 0.002. Round to the nearest gram.',3,('M1',rf'$\Phi^{{-1}}(0.002)={f(z)}$.'),('M1',rf'$(465-\mu)/18={f(z)}$.'),('A1',rf'$\mu={ans(lo-18*z)}$, or {round(lo-18*z)} g.')),
 part('c',r'Instead keep $\mu=502$ and change the standard deviation to achieve the same probability. Round to the nearest gram.',3,('M1',rf'$(465-502)/\sigma={f(z)}$.'),('M1',rf'$\sigma=-37/({f(z)})$.'),('A1',rf'$\sigma={ans(-37/z)}$, or {round(-37/z)} g.'))])
mu=15;upper=17;prob=.08;sd=(upper-mu)/norm.ppf(1-prob)
Q(80,'Finding a spread from an upper tail',N,True,r'Insect lengths $L$ mm follow $N(15,\sigma^2)$.',[
 part('a','State $P(L>15)$.',1,('A1','$0.5$ by symmetry.')),
 part('b',r'Given $P(L>17)=0.08$, find (i) $\sigma$; (ii) $P(L<13.5)$.',5,('M1','$P(L<17)=0.92$.'),('A1',rf'$(17-15)/\sigma=\Phi^{{-1}}(0.92)={f(norm.ppf(.92))}$.'),('A1',rf'$\sigma={ans(sd)}$ mm.'),('M1',r'$P(L<13.5)=\Phi((13.5-15)/\sigma)$.'),('A1',rf'${ans(norm.cdf((13.5-mu)/sd))}$.'))])
normal_two(81,'Race times from tail information',210,.25,260,.85,6,'Let $X$ be the time in minutes to finish a race.')
n=300;p=.55;m=n*p;v=n*p*(1-p);lo=math.floor(m-math.sqrt(v))+1;hi=math.ceil(m+math.sqrt(v))-1
Q(82,'Within one standard deviation',B,True,'A coin shows tails with probability 0.55. It is tossed independently 300 times; $X$ is the number of tails.',[
 part('a','Find the mean and variance of $X$.',3,('M1',r'$X\sim B(300,0.55)$.'),('A1','$E(X)=300(0.55)=165$.'),('A1',r'$\operatorname{Var}(X)=300(0.55)(0.45)=74.25$.')),
 part('b','Find the probability that $X$ is less than one standard deviation away from its mean.',3,('M1',rf'$\sigma=\sqrt{{74.25}}={f(math.sqrt(v))}$; require $|X-165|<\sigma$.'),('A1',rf'The integer range is ${lo}\le X\le{hi}$.'),('A1',rf'$P={ans(binom.cdf(hi,n,p)-binom.cdf(lo-1,n,p))}$.'))])
def reverse_reg(n,x,y,target,title):
 a,b,r=reg(y,x)
 Q(n,title,L,True,'Scores in two assessments are recorded as paired values $x,y$.'+table(['$x$']+x,[['$y$']+y]),[
  part('a','Find the regression line of $x$ on $y$ in the form $x=ay+b$.',2,('A1',rf'$a={ans(a)}$.'),('A1',rf'$b={ans(b)}$.')),
  part('b','The two regression lines intersect at $(p,q)$. Find $p,q$.',2,('A1',rf'$p=\bar x={f(np.mean(x)) if n==83 else ans(np.mean(x))}$.'),('A1',rf'$q=\bar y={f(np.mean(y)) if n==83 else ans(np.mean(y))}$.')),
  part('c',rf'Estimate $x$ for a student who scored $y={target}$, to the nearest mark.',2,('M1','Use the regression of $x$ on $y$ rather than invert the other regression.'),('A1',rf'$x={ans(a*target+b)}$, hence {round(a*target+b)} marks.'))])
reverse_reg(83,[4,7,10,11,14,17,21,26],[6,9,11,14,16,19,22,25],12,'Recovering an absent score')
reverse_reg(84,[72,81,88,95,103,110],[75,79,92,96,106,112],99,'Aptitude-test regression')
mu=250;sd=18;a=225;b=275;pa=norm.cdf((a-mu)/sd);ps=norm.cdf((b-mu)/sd)-pa
Q(85,'A normal standard-size category',N,True,'Animal masses $W$ g follow $N(250,18^2)$. A mass below 225 g is small, above 275 g is large, and all others are standard.',[
 part('a','Find the probability an animal is small.',3,('M1','Standardise: $z=(225-250)/18$.'),('M1',r'$P(W<225)=\Phi(z)$.'),('A1',rf'${ans(pa)}$.')),
 part('b','Find the probability it is standard.',3,('M1',r'The event is $225\le W\le275$.'),('M1',r'$P=\Phi(25/18)-\Phi(-25/18)$.'),('A1',rf'${ans(ps)}$.')),
 part('c','Find the expected number of standard animals in 400 independent selections.',3,('M1','The standard count is binomial with success probability from (b).'),('M1','$E(X)=400p$.'),('A1',rf'$E(X)={ans(400*ps)}$.')),
 part('d','Find the minimum sample size for an expected standard count of at least 120.',3,('M1',r'$Np\ge120$.'),('A1',rf'$N\ge{f(120/ps)}$.'),('A1',rf'$N={math.ceil(120/ps)}$.'))])
linear_rv(86,'A ferry surcharge per passenger',[.15,.25,.35,.25],7.5,1.8)
p=.6
Q(87,'A fixed number and a last success',B,True,'A coin shows heads with probability 0.6. Tosses are independent.',[
 part('a','Find the probability of at least five heads in eight tosses.',2,('M1',r'$H\sim B(8,0.6)$; calculate $1-P(H\le4)$.'),('A1',rf'${ans(binom.sf(4,8,p))}$.')),
 part('b','Find the probability that the fourth tail occurs on the eighth toss.',4,('M1','There must be three tails among the first seven tosses and a tail on toss eight.'),('A1',r'The number of first-seven arrangements is $\binom73$.'),('M1',r'$P=\binom73(0.4)^3(0.6)^4(0.4)$.'),('A1',rf'${ans(math.comb(7,3)*.4**4*.6**4)}$.'))])
weights=[.4,.35,.25];defects=[.03,.04,.09];pd=sum(w*d for w,d in zip(weights,defects))
Q(88,'Bayes’ theorem for machines',P,True,'Three machines produce a factory’s output.'+table(['Machine','Output proportion','Defective probability'],[['A',.4,.03],['B',.35,.04],['C',.25,.09]]),[
 part('a','Find the probability a randomly selected item is defective.',3,('M1','Use total probability over the three machines.'),('A1','$0.4(0.03)+0.35(0.04)+0.25(0.09)$.'),('A1',rf'$P(D)={ans(pd)}$.')),
 part('b','Given an item is defective, find the probability it came from C.',3,('M1',r'Use $P(C\cap D)/P(D)$.'),('A1',rf'$0.25(0.09)/{ans(pd)}$.'),('A1',rf'${ans(.25*.09/pd)}$.'))])
normal_two(89,'Task times from two percentiles',9,.08,24,.8,7,'Let $X$ be completion time in minutes.')
Q(90,'Independent language electives',P,False,r'Students may study Italian $I$, German $G$, both or neither. The probability of both is 0.3. The probability of only Italian exceeds the probability of only German by 0.1. Let $x=P(\text{only German})$.',[
 part('a','Label the three interior regions of a Venn diagram in terms of $x$.',2,('A1','German only is $x$ and Italian only is $x+0.1$.'),('A1','The overlap is 0.3.')),
 part('b','Given the two subjects are independent, find $P(G)$.',4,('M1','$P(G)=x+0.3$ and $P(I)=x+0.4$.'),('M1','Independence gives $(x+0.3)(x+0.4)=0.3$.'),('A1','$x^2+0.7x-0.18=0$, so $x=0.2$ or $-0.9$.'),('A1','Reject the negative probability; $P(G)=0.5$.'))],diagram=venn('I','G',('x+0.1','0.3','x','')))
save()
# 91-105
faces=[1,3,3,5,5,5];totals={k:0 for k in [2,4,6,8,10]}
for u,v in itertools.product(faces,repeat=2):totals[u+v]+=1
Q(91,'Sum of specially labelled dice',R,False,'Each of two independent fair six-sided dice has faces numbered $1,3,3,5,5,5$. Let $X$ be their sum.',[
 part('a','Construct the probability distribution of $X$.',3,('M1','Count the 36 equally likely ordered pairs of faces.'),('A1','Possible sums are $2,4,6,8,10$, with counts $1,4,10,12,9$.'),('A1',r'Probabilities respectively are $\frac1{36},\frac19,\frac5{18},\frac13,\frac14$.')),
 part('b','Find $E(X)$.',3,('M1','The expectation of one die is $(1+3+3+5+5+5)/6$.'),('A1','This is $11/3$.'),('A1','$E(X)=2(11/3)=22/3$.'))])
mu=60;sd=15;lo=65;hi=80;threshold=75;pg=.12;ps=.18
Q(92,'Tree-height categories and samples',N,True,'Tree heights $H$ m follow $N(60,15^2)$. Independent trees are sampled. The tallest 12% are giant and the shortest 18% are small.',[
 part('a',r'Find (i) $P(65<H<80)$; (ii) $P(H\ge75)$.',3,('M1','Use standardised bounds $(h-60)/15$ in the normal distribution.'),('A1',rf'(i) $\Phi(20/15)-\Phi(5/15)={ans(norm.cdf(20/15)-norm.cdf(5/15))}$.'),('A1',rf'(ii) $1-\Phi(1)={ans(norm.sf(1))}$.')),
 part('b','Find (i) the giant lower boundary; (ii) the small upper boundary.',4,('M1','Giant boundary has cumulative probability 0.88.'),('A1',rf'$60+15\Phi^{{-1}}(0.88)={ans(60+15*norm.ppf(.88))}$ m.'),('M1','Small boundary has cumulative probability 0.18.'),('A1',rf'$60+15\Phi^{{-1}}(0.18)={ans(60+15*norm.ppf(.18))}$ m.')),
 part('c','Four trees are selected. Find the probability of exactly two giant and two small trees.',4,('M1','Choose the two positions occupied by giant trees.'),('A1',r'There are $\binom42=6$ orders.'),('M1','$P=6(0.12)^2(0.18)^2$.'),('A1',rf'${ans(6*.12**2*.18**2)}$.')),
 part('d','Eighteen trees are selected. Find the probabilities of (i) no giant trees; (ii) at least three giant trees.',4,('M1',r'$G\sim B(18,0.12)$.'),('A1',rf'(i) $(0.88)^{{18}}={ans(.88**18)}$.'),('M1',r'(ii) $1-P(G\le2)$.'),('A1',rf'${ans(binom.sf(2,18,.12))}$.'))])
x=[.4,.7,1.0,1.3,1.6,1.9];y=[1.1,1.6,2.05,2.48,3.0,3.4];a,b,r=reg(x,y);target=3.8
Q(93,'Power laws from logarithmic regression',L,True,'The table contains logarithms of positive variables.'+table([r'$\ln x$']+x,[[r'$\ln y$']+y])+r' Model the relationship by $\ln y=a\ln x+b$.',[
 part('a','Find $a$ and $b$.',3,('M1',r'Regress the recorded $\ln y$ values on the recorded $\ln x$ values.'),('A1',rf'$a={ans(a)}$.'),('A1',rf'$b={ans(b)}$.')),
 part('b','Estimate $y$ when $x=3.8$.',3,('M1',rf'$\ln y={f(a)}\ln(3.8)+{f(b)}$.'),('M1','Exponentiate the resulting value.'),('A1',rf'$y={ans(math.exp(a*math.log(target)+b))}$.')),
 part('c','Write the model as $y=px^q$ and find $p,q$.',6,('M1','Take logarithms of $y=px^q$.'),('A1',r'$\ln y=\ln p+\ln(x^q)$.'),('A1',r'$\ln y=q\ln x+\ln p$.'),('R1','Match the slope and intercept with the regression line.'),('A1',rf'$q=a={ans(a)}$.'),('A1',rf'$p=e^b={ans(math.exp(b))}$.'))])
x=sy.symbols('x');density=sy.Rational(1,18)*(x-1)*(4-x);ex=sy.integrate(x*density,(x,1,4));ex2=sy.integrate(x*x*density,(x,1,4));# integral density=1/4? correct coefficient2/9
# beta(2,2) on [1,4] density 2/9*(x-1)*(4-x)
density=sy.Rational(2,9)*(x-1)*(4-x);ex=sy.integrate(x*density,(x,1,4));ex2=sy.integrate(x*x*density,(x,1,4));vx=sy.simplify(ex2-ex**2);lower=ex-sy.sqrt(vx);pr=sy.integrate(density,(x,lower,ex));assert sy.integrate(density,(x,1,4))==1
Q(94,'Moments of a quadratic density',C,True,r'$X$ has density $f(x)=\frac29(x-1)(4-x)$ for $1<x<4$, and zero otherwise.',[
 part('a','Find $E(X)$.',2,('M1',r'$E(X)=\int_1^4\frac29x(x-1)(4-x)\,dx$.'),('A1','$E(X)=5/2$.')),
 part('b',r'Find $\operatorname{Var}(X)$.',3,('M1',r'$E(X^2)=\int_1^4\frac29x^2(x-1)(4-x)\,dx$.'),('A1','$E(X^2)=67/10$.'),('A1',r'$\operatorname{Var}(X)=67/10-(5/2)^2=9/20$.')),
 part('c',r'Find $P(\mu-\sigma<X<\mu)$.',3,('A1',r'$\mu=2.5$, $\sigma=\sqrt{9/20}$.'),('M1',r'Integrate $\frac29(x-1)(4-x)$ from $2.5-\sqrt{9/20}$ to $2.5$.'),('A1',rf'$P={ans(float(pr))}$.'))],notes='SymPy verifies density normalization, exact E(X)=5/2, E(X²)=67/10, variance9/20 and the stated interval integral.')
weights=[.5,.3,.2];passes=[.95,.9,.82];pp=sum(w*p for w,p in zip(weights,passes))
Q(95,'Supplier probabilities after inspection',P,True,'Components are sourced independently with the following proportions and pass rates.'+table(['Supplier','Proportion','Pass probability'],[['X',.5,.95],['Y',.3,.9],['Z',.2,.82]]),[
 part('a','Find the probability a selected component passes.',3,('M1','Use total probability.'),('A1','$P(S)=0.5(0.95)+0.3(0.9)+0.2(0.82)$.'),('A1',rf'$P(S)={ans(pp)}$.')),
 part('b','Given it passes, find the probability it came from Z.',2,('M1',rf'$P(Z\mid S)=0.2(0.82)/{f(pp)}$.'),('A1',rf'${ans(.2*.82/pp)}$.')),
 part('c','Given it fails, find the probability it came from X.',3,('M1',r'$P(X\cap S^{\prime})=0.5(0.05)$.'),('M1',rf'$P(X\mid S^{{\prime}})=0.025/(1-{f(pp)})$.'),('A1',rf'${ans(.025/(1-pp))}$.'))])
# equal sd; lower tail probability supplied consistent exact z1.1
pupper=float(norm.cdf(1.1));sd=6/norm.ppf(pupper)
Q(96,'Two normal distributions with a shared spread',N,True,rf'$X\sim N(140,\sigma^2)$ and $Y\sim N(110,\sigma^2)$.',[
 part('a','Find $k$ such that $P(Y>k)=P(X<k)$.',2,('M1','Equal opposite tails require $k-110=140-k$.'),('A1','$k=125$.')),
 part('b',rf'Given $P(X>134)={pupper:.8f}$, find $P(98<Y<116)$.',5,('M1',rf'$P(X<134)=1-{pupper:.8f}$.'),('A1',r'$(134-140)/\sigma\approx-1.1$.'),('A1',rf'$\sigma\approx{ans(sd)}$.'),('M1',r'$P=\Phi((116-110)/\sigma)-\Phi((98-110)/\sigma)$.'),('A1',rf'$P={ans(norm.cdf(6/sd)-norm.cdf(-12/sd))}$.'))])
rain=.35;trainrain=.85;traindry=.25;pt=rain*trainrain+(1-rain)*traindry
Q(97,'Weather and commuting costs',P,True,'On each workday, Sam uses either a bicycle or a train. Rain probability is 0.35. Given rain, the train probability is 0.85; given dry weather, it is 0.25. Days are independent.',[
 part('a','Find the probability Sam takes the train on a randomly chosen day.',4,('M1','Partition by rainy and dry weather.'),('A1',r'$P(R\cap T)=0.35(0.85)=0.2975$.'),('A1',r'$P(R^{\prime}\cap T)=0.65(0.25)=0.1625$.'),('A1',rf'$P(T)={ans(pt)}$.')),
 part('b','Given Sam takes the train, find the rain probability.',3,('M1',r'Use $P(R\cap T)/P(T)$.'),('A1','$0.2975/0.46$.'),('A1',rf'${ans(.2975/pt)}$.')),
 part('c','Find the probability of using the train on exactly three of five workdays.',3,('M1',r'$X\sim B(5,0.46)$.'),('M1',r'$P(X=3)=\binom53(0.46)^3(0.54)^2$.'),('A1',rf'${ans(binom.pmf(3,5,pt))}$.')),
 part('d','Sam works five days a week for 46 weeks. A train day costs USD 2.40 and cycling is free. Find the expected annual cost.',5,('M1','The number of workdays is $5(46)=230$.'),('A1','Expected train days $=230(0.46)=105.8$.'),('M1','Multiply expected train days by the cost per train day.'),('A1','$105.8(2.4)$.'),('A1','Expected cost = USD 253.92.'))])
mu=46;sd=7;tall=52;above=60;pt=norm.sf((tall-mu)/sd);pa=norm.sf((above-mu)/sd)
Q(98,'Conditional heights and a large sample',N,True,'Flower heights $H$ cm follow $N(46,7^2)$. Flowers over 52 cm are tall. Heights are independent.',[
 part('a','Find (i) the probability a flower is tall; (ii) the probability it exceeds 60 cm, given it is tall.',6,('M1',r'$p=P(H>52)=1-\Phi(6/7)$.'),('A1',rf'$p={ans(pt)}$.'),('M1','The conditional event uses $P(H>60)/P(H>52)$.'),('A1',rf'$P(H>60)=1-\Phi(2)={ans(pa)}$.'),('M1','Divide, using unrounded probabilities.'),('A1',rf'$P(H>60\mid H>52)={ans(pa/pt)}$.')),
 part('b','Find the probability two selected flowers are both tall.',3,('R1','Selections are independent.'),('M1','The required probability is $p^2$.'),('A1',rf'${ans(pt**2)}$.')),
 part('c','Of 450 selected flowers, find (i) the probability at least 90 are tall; (ii) the expected tall count.',6,('M1',rf'$X\sim B(450,{f(pt)})$, retaining the unrounded $p$.'),('M1',r'$P(X\ge90)=1-P(X\le89)$.'),('A1',rf'${ans(binom.sf(89,450,pt))}$.'),('M1','Use $E(X)=np$.'),('A1',rf'$450({ans(pt)})$ using unrounded $p$.'),('A1',rf'$E(X)={ans(450*pt)}$.'))])
Q(99,'Choosing a destination from travel mode',P,False,'A traveller visits either city A or city B. When visiting A, the probability of driving is $2/3$. When visiting B, the probability of flying is $4/5$. The overall probability of driving is $2/5$.',[
 part('a','Find the probability of visiting A.',4,('M1','Let $p=P(A)$; then $P(B)=1-p$.'),('A1',r'$P(\text{drive}\mid B)=1/5$.'),('M1',r'$\frac23p+\frac15(1-p)=\frac25$.'),('A1','$p=3/7$.')),
 part('b','Given the traveller flies, find the probability the destination is A.',3,('M1',r'$P(A\cap F)=(3/7)(1/3)=1/7$.'),('M1','$P(F)=1-2/5=3/5$.'),('A1',r'$P(A\mid F)=(1/7)/(3/5)=5/21$.'))])
# 100 normal mean proportional sd and concave payout optimization
z=norm.ppf(.2);mu=10/(1+z/5);sd=mu/5;p1=.2;p3=norm.sf((14-mu)/sd);p2=1-p1-p3;bopt=p2/(2*p3);copt=8-bopt**2;amax=(p2*bopt+p3*copt)/p1
assert copt>0
Q(100,'Designing a fair balance game',N,True,r'A balance time $X$ seconds is normally distributed with mean $\mu>0$ and standard deviation $\mu/5$. It is given that $P(X<10)=0.2$. In a free game, the player’s net payout is $a<0$ for $X<10$, $b\ge0$ for $10\le X\le14$, and $c\ge0$ for $X>14$.',[
 part('a','Find the mean and standard deviation, to four significant figures.',4,('M1',r'$\frac{10-\mu}{\mu/5}=\Phi^{-1}(0.2)$.'),('A1',rf'$10=\mu(1+({f(z)})/5)$.'),('A1',rf'$\mu={mu:.4g}$ seconds.'),('A1',rf'$\sigma=\mu/5={sd:.4g}$ seconds.')),
 part('b','Find the three payout probabilities. Given $c=8-b^2$ and the game is fair, find the maximum possible value of $|a|$.',8,('A1',rf'$P(D=a)=0.2$, $P(D=b)={ans(p2)}$, $P(D=c)={ans(p3)}$.'),('M1','Fairness requires $0.2a+p_2b+p_3c=0$.'),('A1','$|a|=(p_2b+p_3(8-b^2))/0.2$.'),('M1',r'Differentiate with respect to $b$: $\frac{d|a|}{db}=(p_2-2p_3b)/0.2$.'),('A1',rf'The stationary value is $b=p_2/(2p_3)={ans(bopt)}$.'),('R1','The second derivative is $-2p_3/0.2<0$, giving a maximum.'),('A1',rf'$c=8-b^2={ans(copt)}>0$, so this solution satisfies the payout restrictions.'),('A1',rf'Maximum $|a|={ans(amax)}$ USD.'))],notes='Normal probabilities and the constrained concave optimum computed numerically; b,c positivity checked.')
probs=[.08,.2,.3,.25,.12,.05];vals=list(range(6));ex=sum(v*p for v,p in zip(vals,probs));vx=sum(v*v*p for v,p in zip(vals,probs))-ex**2
Q(101,'A subscription with extra devices',R,True,'A subscription costs USD 18 plus USD 3.50 per additional device. Let $X$ be the additional-device count.'+table(['$x$','0','1','2','3','4','5'],[['$P(X=x)$','.08','.20','$p$','.25','.12','$q$']])+'\n'+rf'It is given that $P(X<4)=0.83$, $E(X)={ex:.2f}$ and $\operatorname{{Var}}(X)={vx:.4f}$. Let $Y$ be the monthly cost.',[
 part('a','Find $p$ and $q$.',4,('M1','$0.08+0.20+p+0.25=0.83$.'),('A1','$p=0.30$.'),('M1','The remaining probabilities add to $1-0.83=0.17$.'),('A1','$q=0.17-0.12=0.05$.')),
 part('b',r'Find $E(Y)$ and $\operatorname{Var}(Y)$ to two decimal places.',4,('M1','$Y=18+3.5X$; hence $E(Y)=18+3.5E(X)$.'),('A1',rf'$E(Y)={18+3.5*ex:.2f}$ USD.'),('M1',r'$\operatorname{Var}(Y)=3.5^2\operatorname{Var}(X)$.'),('A1',rf'$\operatorname{{Var}}(Y)={3.5**2*vx:.2f}$ USD$^2$.'))])
Q(102,'Selecting damaged cartons',P,False,'Of 80 cartons, 10 contain a damaged item. Two cartons are selected without replacement.',[
 part('a','Find the probability neither carton contains damage.',2,('M1',r'$\frac{70}{80}\frac{69}{79}$.'),('A1',rf'${frac(70*69,80*79)}$.')),
 part('b','Find the probability both contain damage.',2,('M1',r'$\frac{10}{80}\frac9{79}$.'),('A1',rf'${frac(90,80*79)}$.')),
 part('c','Find the probability exactly one contains damage.',2,('M1',r'$2\frac{10}{80}\frac{70}{79}$.'),('A1',rf'${frac(1400,80*79)}$.'))])
pts=[(20,0),(40,12),(60,32),(80,64),(100,84),(120,96)];freq=[12,20,32,20,12];mid=[30,50,70,90,110];mean=sum(v*c for v,c in zip(mid,freq))/96;sd=math.sqrt(sum(v*v*c for v,c in zip(mid,freq))/96-mean**2)
Q(103,'Grouped stem lengths',D,True,'The cumulative-frequency graph shows the lengths of 96 stems in centimetres. Treat the variable as continuous and use linear interpolation. The grouped table is also shown.'+table(['Length $l$','Frequency'],[[r'$20<l\le40$',12],[r'$40<l\le60$','$p$'],[r'$60<l\le80$',32],[r'$80<l\le100$','$q$'],[r'$100<l\le120$',12]]),[
 part('a','Find (i) the median; (ii) the percentage of stems at least 60 cm long.',4,('M1','The median is read at cumulative frequency 48.'),('A1','Median $=70$ cm.'),('M1','At least 60 cm gives $96-32=64$ stems.'),('A1',r'$100(64/96)=66.7\%$ to 3 s.f.')),
 part('b','Find $p$ and $q$.',4,('M1','For $p$, subtract cumulative frequencies at 40 and 60.'),('A1','$p=32-12=20$.'),('M1','For $q$, subtract cumulative frequencies at 80 and 100.'),('A1','$q=84-64=20$.')),
 part('c','Estimate the mean and population standard deviation using class midpoints.',3,('M1','Use midpoints $30,50,70,90,110$ with the class frequencies.'),('A1',rf'Estimated mean $={ans(mean)}$ cm.'),('A1',rf'Estimated standard deviation $={ans(sd)}$ cm.')),
 part('d','A stem is mature if it is at least 60 cm. Given a mature stem, find the probability its length is at least 90 cm.',4,('M1','The conditioning group contains 64 stems.'),('A1','Cumulative frequency at 90 is $64+(20/2)=74$.'),('M1','There are $96-74=22$ stems at least 90 cm.'),('A1','$22/64=11/32$.'))],diagram=curve(pts,'Stem length (cm)'))
# 104 m threshold
valid=[m for m in range(1000) if 4*(6/(18+m))*(1-6/(18+m))<.5];minm=min(valid)
Q(104,'A variance bound for sampling with replacement',B,True,'A bag has 6 blue, 12 green and $m$ red counters, where $m$ is a non-negative integer. Four counters are drawn independently with replacement. Let $X$ count blue counters.',[
 part('a','State the probability the first counter is blue.',1,('A1','$p=6/(18+m)$.')),
 part('b',r'Find the smallest $m$ such that $\operatorname{Var}(X)<0.5$.',5,('M1',r'$X\sim B(4,p)$, so $4p(1-p)<0.5$.'),('A1','$p^2-p+1/8>0$.'),('M1',r'Since $0<p\le1/3$, require $p<(1-1/\sqrt2)/2$.'),('A1',rf'$m>6/((1-1/\sqrt2)/2)-18={f(6/((1-1/math.sqrt(2))/2)-18)}$.'),('A1',rf'The least integer is $m={minm}$; substitution confirms {minm-1} fails and {minm} satisfies the strict bound.'))])
xv=[0,2,4,6,8];yv=[180,207,237,267,298];a,b,r=reg(xv,yv);initial=420;tobs=5;obs=390;k=-math.log(obs/initial)/tobs;root=brentq(lambda t:a*t+b-initial*math.exp(-k*t),0,30)
Q(105,'Comparing linear and exponential populations',L,True,'At the start of 2020, a farm begins tracking two bird populations. Chicken count $c$ after $t$ years is recorded below.'+table(['$t$']+xv,[['$c$']+yv])+'\nDuck count is modelled by $d=420e^{-kt}$. After five years there are 390 ducks.',[
 part('a','Find the regression equation $c=at+b$.',3,('M1','Fit the least-squares line to chicken count against time.'),('A1',rf'$a={ans(a)}$.'),('A1',rf'$b={ans(b)}$.')),
 part('b','Estimate the chicken count after six years, to the nearest bird.',2,('M1','Substitute $t=6$ in the regression line.'),('A1',rf'${ans(6*a+b)}$, hence {round(6*a+b)} chickens.')),
 part('c','Find the initial duck count.',3,('M1','The start of 2020 is $t=0$.'),('A1','$d=420e^0$.'),('A1','420 ducks.')),
 part('d','Find $k$.',3,('M1','$390=420e^{-5k}$.'),('M1',r'$k=-\ln(390/420)/5$.'),('A1',rf'$k={ans(k)}$.')),
 part('e','Find the calendar year during which the modelled populations are equal.',4,('M1',rf'Solve ${f(a)}t+{f(b)}=420e^{{-{f(k)}t}}$ with unrounded coefficients.'),('A1',rf'$t={ans(root)}$ years.'),('M1','Add the elapsed time to the start of 2020.'),('A1',rf'The crossing occurs during {2020+math.floor(root)}.'))])
save()
# 106-115
mu=6.2;sd=.9;threshold=7;upper=7.8;p=norm.sf((threshold-mu)/sd);cond=norm.sf((upper-mu)/sd)/p;alow=mu+sd*norm.ppf(norm.cdf((threshold-mu)/sd)/9)
Q(106,'Pumpkin masses and conditional selection',N,True,r'Pumpkin masses $W$ kg follow $N(6.2,0.9^2)$. Purchases are independent.',[
 part('a',r'Find $P(W>7)$.',2,('M1',r'$P(W>7)=1-\Phi((7-6.2)/0.9)$.'),('A1',rf'${ans(p)}$.')),
 part('b','Five customers buy pumpkins in order. Find the probability that only the last three buy pumpkins over 7 kg.',3,('M1','The required ordered pattern is not-heavy, not-heavy, heavy, heavy, heavy.'),('M1',r'$P=(1-p)^2p^3$; no combination factor is needed.'),('A1',rf'${ans((1-p)**2*p**3)}$.')),
 part('c',r'(i) Given $W>7$, find $P(W>7.8\mid W>7)$. (ii) Of three independently selected pumpkins over 7 kg, find the probability exactly two exceed 7.8 kg.',7,('M1',r'For (i), divide $P(W>7.8)$ by $P(W>7)$.'),('A1',rf'$P(W>7.8)={ans(norm.sf((upper-mu)/sd))}$.'),('A1',rf'The conditional probability is $q={ans(cond)}$.'),('M1',r'For (ii), $Y\sim B(3,q)$.'),('A1',r'$P(Y=2)=\binom32q^2(1-q)$.'),('M1','Substitute the unrounded conditional probability.'),('A1',rf'${ans(binom.pmf(2,3,cond))}$.')),
 part('d',r'Find $a$ given $P(W\le a)=\frac18P(a<W\le7)$.',4,('M1',r'Let $u=P(W\le a)$; then $u=(P(W\le7)-u)/8$.'),('A1',r'$9u=P(W\le7)$.'),('M1',r'$a=6.2+0.9\Phi^{-1}(P(W\le7)/9)$.'),('A1',rf'$a={ans(alow)}$ kg.'))])
def weather(n,title,initial,dry_dry,rain_rain,eventthird,conditionalfirst):
 dd=dry_dry;rd=1-rain_rain;pD2=initial*dd+(1-initial)*rd;pD3=pD2*dd+(1-pD2)*rd
 jointDD=initial*(dd*dd+(1-dd)*rd)
 target=pD3 if eventthird=='dry' else 1-pD3
 cond=jointDD/pD3 if conditionalfirst=='dry' else (initial-jointDD)/(1-pD3)
 Q(n,title,P,True,rf'Weather is classified as dry (D) or rainy (R). The first-day probability of dry weather is {initial}. Given a dry day, the next day is dry with probability {dd}; given a rainy day, the next day is rainy with probability {rain_rain}. Weather depends only on the preceding day.',[
  part('a','Draw a fully labelled tree for the first three days.',4,('A1',rf'Day 1 branches: D {initial}, R {1-initial:.2f}.'),('A1',rf'After any D, branches are D {dd}, R {1-dd:.2f}.'),('A1',rf'After any R, branches are D {rd:.2f}, R {rain_rain}.'),('A1','Repeat these conditional branches at day 3 to show all eight paths.')),
  part('b',rf'Find the probability that day 3 is {eventthird}.',3,('M1',rf'$P(D_2)={initial}({dd})+{1-initial:.2f}({rd:.2f})={f(pD2)}$.'),('M1',rf'$P(D_3)={f(pD2)}({dd})+(1-{f(pD2)})({rd:.2f})={f(pD3)}$.'),('A1',rf'The required probability is ${ans(target)}$.')),
  part('c',rf'Given day 3 is {conditionalfirst}, find the probability day 1 was dry.',4,('M1',rf'$P(D_1\cap D_3)={initial}[({dd})^2+({1-dd:.2f})({rd:.2f})]={f(jointDD)}$.' if conditionalfirst=='dry' else rf'$P(D_1\cap R_3)={initial}[({dd})({1-dd:.2f})+({1-dd:.2f})({rain_rain})]={f(initial-jointDD)}$.'),('A1',rf'The required joint probability is ${ans(jointDD if conditionalfirst=="dry" else initial-jointDD)}$.'),('M1',rf'Divide by $P(D_3)$.' if conditionalfirst=='dry' else rf'Divide by $P(R_3)=1-P(D_3)={f(1-pD3)}$.'),('A1',rf'${ans(cond)}$.'))])
weather(107,'Three-day weather probabilities',.75,.7,.8,'rainy','dry')
lo=14;plo=.05;hi=32;phi=.78;zl=norm.ppf(plo);zh=norm.ppf(phi);sd=(hi-lo)/(zh-zl);mu=lo-zl*sd;p=norm.sf((42-mu)/sd);n=14
Q(108,'Normal consumption and team probabilities',N,True,r'Weekly consumption $X$ is modelled by a normal distribution. Five per cent of employees have $X<14$ and 22% have $X>32$. Different employees are independent.',[
 part('a',r'Form two equations in $\mu,\sigma$ and find both parameters to one decimal place.',6,('M1',r'Use cumulative probabilities 0.05 and 0.78.'),('A1',rf'$14=\mu+({f(zl)})\sigma$.'),('A1',rf'$32=\mu+({f(zh)})\sigma$.'),('M1','Subtract the equations and solve.'),('A1',rf'$\sigma={sd:.1f}$.'),('A1',rf'$\mu={mu:.1f}$.')),
 part('b',r'Find $P(X>42)$.',2,('M1',r'$P(X>42)=1-\Phi((42-\mu)/\sigma)$ using unrounded parameters.'),('A1',rf'$p={ans(p)}$.')),
 part('c','For a team of 14, find (i) the probability at least three have consumption above 42; (ii) given at least one does, the probability fewer than three do.',5,('M1',r'$Y\sim B(14,p)$.'),('A1',rf'(i) $1-P(Y\le2)={ans(binom.sf(2,n,p))}$.'),('M1','For (ii), the numerator is $P(Y=1)+P(Y=2)$.'),('M1',r'Divide this by $1-P(Y=0)$.'),('A1',rf'${ans((binom.cdf(2,n,p)-binom.pmf(0,n,p))/binom.sf(0,n,p))}$.'))])
weather(109,'Conditional weather on the first day',.85,.75,.7,'dry','rainy')
lo=14;plo=.18;hi=20;phi=.85;sd=(hi-lo)/(norm.ppf(phi)-norm.ppf(plo));mu=lo-sd*norm.ppf(plo)
Q(110,'Battery-life parameters and binomial mode',N,True,r'Battery lifetimes $T$ hours are normal. It is known that $P(T>20)=0.15$ and $P(T<14)=0.18$.',[
 part('a',r'Find $\mu$ and $\sigma$ to two significant figures.',6,('M1',r'$P(T<20)=0.85$.'),('A1',rf'$20=\mu+({f(norm.ppf(.85))})\sigma$.'),('M1',r'Use the lower percentile as a second equation.'),('A1',rf'$14=\mu+({f(norm.ppf(.18))})\sigma$.'),('A1',rf'$\sigma={sd:.2g}$ hours.'),('A1',rf'$\mu={mu:.2g}$ hours.')),
 part('b','Twenty-four independent batteries are selected. Let $X$ count lifetimes above 20 hours. Find (i) $E(X)$; (ii) $P(X=5)$; (iii) the most likely value of $X$.',6,('M1',r'$X\sim B(24,0.15)$.'),('A1',r'$E(X)=24(0.15)=3.6$.'),('M1',r'$P(X=5)=\binom{24}5(0.15)^5(0.85)^{19}$.'),('A1',rf'${ans(binom.pmf(5,24,.15))}$.'),('M1','The binomial mode is the integer part of $(24+1)(0.15)=3.75$.'),('A1','The most likely value is 3.'))])
weights=[.5,1/3,1/6];mus=[8.5,7.8,9.3];sds=[.4,.35,.6];probs=[norm.cdf((8.4-m)/s)-norm.cdf((8.1-m)/s) for m,s in zip(mus,sds)];den=sum(w*p for w,p in zip(weights,probs))
Q(111,'A mixture of normal populations',N,True,r'Plant varieties A, B and C occur in the ratio $3:2:1$. Their stem lengths are normal with parameters shown below.'+table(['Variety','Mean (cm)','Standard deviation (cm)'],[['A',8.5,.4],['B',7.8,.35],['C',9.3,.6]])+r' A plant selected at random has length between 8.1 and 8.4 cm. Find the probability it is variety A.',[part('','',6,('M1','Let $E$ denote the measured interval. Prior probabilities are $1/2,1/3,1/6$.'),('A1',rf'$P(E\mid A)={ans(probs[0])}$.'),('A1',rf'$P(E\mid B)={ans(probs[1])}$, $P(E\mid C)={ans(probs[2])}$.'),('M1',rf'$P(E)=\frac12P(E\mid A)+\frac13P(E\mid B)+\frac16P(E\mid C)={f(den)}$.'),('M1',r'$P(A\mid E)=\frac{(1/2)P(E\mid A)}{P(E)}$.'),('A1',rf'${ans(.5*probs[0]/den)}$.'))])
mu=520;sd=10;below=norm.cdf(-1);v=mu+sd*norm.ppf(.65);cond=norm.sf(1.5)/norm.sf(-1);pbad=norm.cdf(-1.5)
Q(112,'Bottle volumes through several probability models',N,True,r'Bottle volumes $V$ mL follow $N(520,10^2)$, independently.',[
 part('a',r'Find $P(V<510)$.',2,('M1',r'$P(V<510)=\Phi(-1)$.'),('A1',rf'${ans(below)}$.')),
 part('b',r'Find $v$ such that $P(V>v)=0.35$.',2,('M1',r'$v=520+10\Phi^{-1}(0.65)$.'),('A1',rf'$v={ans(v)}$ mL.')),
 part('c',r'Find $P(V>535\mid V>510)$.',3,('M1','Use the ratio of the two upper-tail probabilities.'),('M1',r'$P=\frac{1-\Phi(1.5)}{1-\Phi(-1)}$.'),('A1',rf'${ans(cond)}$.')),
 part('d','For 250 bottles, find the expected number within two standard deviations of the mean, to the nearest integer.',4,('M1',r'The interval is $500<V<540$.'),('A1',rf'$p=\Phi(2)-\Phi(-2)={ans(norm.cdf(2)-norm.cdf(-2))}$.'),('M1','Expected count is $250p$.'),('A1',f'{round(250*(norm.cdf(2)-norm.cdf(-2)))} bottles.')),
 part('e','A pack contains 24 bottles. Find the probability at least four have volume below 505 mL.',4,('M1',rf'$p=P(V<505)=\Phi(-1.5)={f(pbad)}$.'),('A1',r'$X\sim B(24,p)$.'),('M1',r'$P(X\ge4)=1-P(X\le3)$.'),('A1',rf'${ans(binom.sf(3,24,pbad))}$.'))])
roots=[brentq(lambda p:binom.pmf(5,8,p)-.2,1e-8,5/8),brentq(lambda p:binom.pmf(5,8,p)-.2,5/8,1-1e-8)]
Q(113,'Finding two binomial success probabilities',B,True,'A player independently wins game A with probability 0.75 and plays it six times. In game B, the win probability is $p$ and the player makes eight independent attempts.',[
 part('a','Find the probability of exactly three wins in game A.',2,('M1',r'$P=\binom63(0.75)^3(0.25)^3$.'),('A1',rf'${ans(binom.pmf(3,6,.75))}$.')),
 part('b','Write the probability of exactly five wins in game B in terms of $p$.',2,('M1','Choose the five winning positions among eight.'),('A1',r'$\binom85p^5(1-p)^3=56p^5(1-p)^3$.')),
 part('c','Find all values of $p$ for which this probability is 0.2.',3,('M1',r'Solve $56p^5(1-p)^3=0.2$ on $0<p<1$.'),('A1',rf'$p={ans(roots[0])}$.'),('A1',rf'$p={ans(roots[1])}$.'))])
probs=[F(math.comb(9-j,2),math.comb(9,3)) for j in range(1,8)];multipliers=[F(4),F(3),F(2),F(1),F(1,2),F(1,4),F(0)];factor=sum(p*m for p,m in zip(probs,multipliers));k=F(7)/factor
Q(114,'A fair first-winning-card game',R,False,r'There are $n$ face-down cards, three marked WIN. A player draws without replacement until obtaining WIN.',[
 part('a','Find the probability the game ends on draw 2.',2,('M1','The first draw must lose, then the next must win.'),('A1',r'$\frac{n-3}{n}\frac3{n-1}$.')),
 part('b','When $n=9$, find the probability the game ends on draw 7.',2,('M1',r'All six losing cards must precede the first WIN, or use $P(T=7)=\binom22/\binom93$.'),('A1',r'$1/84$.')),
 part('c',r'For $n=9$, entry costs USD 7. Payouts for ending on draws $1,2,3,4,5,6,7$ are respectively $4k,3k,2k,k,k/2,k/4,0$ USD. Find $k$ for a fair game.',7,('M1',r'$P(T=j)=\binom{9-j}{2}/\binom93$ for $j=1,\ldots,7$.'),('A1',r'The probabilities are $28,21,15,10,6,3,1$, each divided by 84.'),('M1','Expected payout must equal the entry fee 7.'),('A1',r'$\frac{k}{84}(4(28)+3(21)+2(15)+10+6/2+3/4)=7$.'),('M1','Collect the coefficients of $k$.'),('A1',rf'${ans(factor)}k=7$.'),('A1',rf'$k={ans(k)}$ USD.'))])
mu=5.1;sd=.6;elite=norm.cdf((4.7-mu)/sd)-norm.cdf((4.3-mu)/sd);box=binom.pmf(1,6,elite);midprob=.72;# 3Pbelow=4Pabove, so upper=(1-mid)*3/7=.12
upper_tail=(1-midprob)*3/7;b=mu+sd*norm.ppf(1-upper_tail);iqr=.45;k=iqr/(2*norm.ppf(.75))
Q(115,'Nested binomial models for landing times',N,True,r'Drone landing time $T$ seconds follows $N(5.1,0.6^2)$. Drones with $4.3<T<4.7$ are elite. Drones are independent.',[
 part('a','Find the percentage of drones taking more than 5.4 seconds.',2,('M1',r'$P(T>5.4)=1-\Phi(0.5)$.'),('A1',rf'${ans(100*norm.sf(.5))}\%$.')),
 part('b','Find the elite probability.',2,('M1',r'$p=\Phi((4.7-5.1)/0.6)-\Phi((4.3-5.1)/0.6)$.'),('A1',rf'$p={ans(elite)}$.')),
 part('c','Six drones are placed in a box. Find the probability of exactly one elite drone.',2,('M1',r'$q=\binom61p(1-p)^5$.'),('A1',rf'$q={ans(box)}$.')),
 part('d','Eighteen independent boxes are chosen. Find the probability that at least nine contain exactly one elite drone.',2,('M1',r'$Y\sim B(18,q)$; calculate $1-P(Y\le8)$.'),('A1',rf'${ans(binom.sf(8,18,box))}$.')),
 part('e',r'$P(a<T<b)=0.72$ and $3P(T<a)=4P(T>b)$. Drones taking more than $b$ seconds are faulty. Find $b$.',4,('M1','Let $u=P(T>b)$; then $P(T<a)=4u/3$.'),('A1','$u+4u/3=0.28$, giving $u=0.12$.'),('M1',r'$b=5.1+0.6\Phi^{-1}(0.88)$.'),('A1',rf'$b={ans(b)}$ seconds.')),
 part('f','A new model has normal landing time with standard deviation $k$ and interquartile range 0.45 seconds. Find $k$.',4,('M1','Standard normal quartiles are opposite with magnitude $z_{0.75}$.'),('A1',r'$\mathrm{IQR}=2\Phi^{-1}(0.75)k$.'),('M1',r'$k=0.45/(2\Phi^{-1}(0.75))$.'),('A1',rf'$k={ans(k)}$ seconds.'))])
save()
# 116-126
Q(116,'Correcting a survey and finding two unions',P,False,r'A café surveys preferences for tea $T$ and coffee $C$. The probability of liking only tea is 0.12.',[
 part('a','Initially, only-coffee probability is reported as 0.28 and neither probability as 0.25. Find (i) the probability of both; (ii) the probability of neither, given the customer does not like tea.',6,('M1','All four disjoint regions must total 1.'),('A1',r'$P(T\cap C)=1-0.12-0.28-0.25$.'),('A1',r'$P(T\cap C)=0.35$.'),('M1',r'$P(T^{\prime})=0.28+0.25=0.53$.'),('M1',r'Divide the neither region by $P(T^{\prime})$.'),('A1',r'$P(C^{\prime}\mid T^{\prime})=25/53$.')),
 part('b','The only-coffee probability is corrected to 0.21. (i) Show that the events are independent if the union probability is 0.37. (ii) Find the other possible union probability giving independence.',7,('A1','For union 0.37 the overlap is $0.37-0.12-0.21=0.04$.'),('R1','$P(T)P(C)=(0.12+0.04)(0.21+0.04)=0.04$, equal to the overlap.'),('M1','Let $z$ be the overlap. Independence requires $(z+0.12)(z+0.21)=z$.'),('A1','$z^2-0.67z+0.0252=0$.'),('A1','The roots are $z=0.04,0.63$.'),('M1','The other union is $z+0.12+0.21$.'),('A1',r'$P(T\cup C)=0.96$.'))])
pX=norm.cdf((26-22)/2.4)-norm.cdf((19-22)/2.4);zl=norm.ppf(.04);zh=norm.ppf(.82);syy=11/(zh-zl);my=38-zl*syy;py=.6;k=norm.ppf(.8);comparison=sum(binom.pmf(i,2,pX)*binom.pmf(j,2,py) for i in range(3) for j in range(3) if i>j)
Q(117,'Acceptance rates for two normal alloys',N,True,r'Alloy X sample masses follow $N(22,2.4^2)$ grams. A sample is accepted if its mass is between 19 g and 26 g. Independent samples are used throughout.',[
 part('a','Find the acceptance probability for alloy X.',2,('M1',r'$p_X=\Phi(4/2.4)-\Phi(-3/2.4)$.'),('A1',rf'$p_X={ans(pX)}$.')),
 part('b',r'Alloy Y masses are normal with mean $\mu_Y$ and standard deviation $\sigma_Y$. Given $P(Y<38)=0.04$, form an equation connecting its parameters.',2,('M1',r'$(38-\mu_Y)/\sigma_Y=\Phi^{-1}(0.04)$.'),('A1',rf'$\mu_Y=38+{f(-zl)}\sigma_Y$.')),
 part('c',r'Also $P(Y>49)=0.18$. Find a second equation and hence $\mu_Y,\sigma_Y$.',3,('A1',rf'$\mu_Y=49-{f(zh)}\sigma_Y$.'),('A1',rf'$\sigma_Y={ans(syy)}$ grams.'),('A1',rf'$\mu_Y={ans(my)}$ grams.')),
 part('d',r'Alloy Y is accepted within $k$ standard deviations of its mean, with probability 0.6. (i) Find $k$. (ii) Of nine Y samples, find the probability more than six are accepted.',6,('M1',r'$P(-k<Z<k)=0.6$.'),('A1',r'Each tail is 0.2, so $\Phi(k)=0.8$.'),('A1',rf'$k={ans(k)}$.'),('M1',r'$U\sim B(9,0.6)$.'),('M1',r'$P(U>6)=1-P(U\le6)$.'),('A1',rf'${ans(binom.sf(6,9,.6))}$.')),
 part('e','Two samples of each alloy are taken. Find the probability more X samples than Y samples are accepted.',5,('M1',r'Let $A\sim B(2,p_X)$, $B\sim B(2,0.6)$ independently.'),('A1','The qualifying pairs $(A,B)$ are $(1,0),(2,0),(2,1)$.'),('M1',r'$P=2p_X(1-p_X)(0.4)^2+p_X^2[(0.4)^2+2(0.6)(0.4)]$.'),('A1',rf'The separate contributions are ${ans(2*pX*(1-pX)*.4**2)}$ and ${ans(pX**2*(.4**2+2*.6*.4))}$.'),('A1',rf'$P={ans(comparison)}$.'))])
Q(118,'Two products and customer groups',P,True,r'Each customer buys a veggie wrap, a halloumi wrap, or both. The probabilities of buying a veggie wrap $V$ and halloumi wrap $H$ are 0.68 and 0.57 respectively. Different customers make their choices independently.',[
 part('a','Find the probabilities of (i) both wraps; (ii) only halloumi.',5,('M1',r'Every customer buys at least one, so $P(V\cup H)=1$.'),('M1','Use the addition rule.'),('A1',r'$P(V\cap H)=0.68+0.57-1=0.25$.'),('M1','Subtract the overlap from $P(H)$.'),('A1',r'$P(\text{only }H)=0.57-0.25=0.32$.')),
 part('b','For 500 customers, find (i) the expected veggie-wrap sales; (ii) the probability more than 350 veggie wraps are sold.',4,('M1',r'$X\sim B(500,0.68)$.'),('A1','$E(X)=340$.'),('M1',r'$P(X>350)=1-P(X\le350)$.'),('A1',rf'${ans(binom.sf(350,500,.68))}$.')),
 part('c','Forty per cent of customers are loyalty members, and 70% of members buy halloumi. Find (i) the probability a customer is a member and buys halloumi; (ii) the halloumi probability for a non-member.',6,('M1','Multiply member probability by the conditional halloumi probability.'),('A1',r'$P(M\cap H)=0.4(0.7)$.'),('A1',r'$P(M\cap H)=0.28$.'),('M1',r'$P(M^{\prime}\cap H)=0.57-0.28=0.29$.'),('M1',r'Divide by $P(M^{\prime})=0.6$.'),('A1',r'$P(H\mid M^{\prime})=29/60$.'))])
sd=30/norm.ppf(.9);small=norm.cdf((140-180)/sd);box=binom.cdf(2,16,small)
Q(119,'Symmetric mass probabilities and nested boxes',N,True,r'Fruit masses $M$ grams are normally distributed. The table gives three disjoint regions.'+table(['Mass interval','$M<150$',r'$150\le M\le210$','$M>210$'],[['Probability','0.1','$k$','0.1']]),[
 part('a',r'(i) Find $k$. (ii) Show that the mean is $\mu=180$.',3,('A1','$k=0.8$.'),('M1','The equal tails place 150 and 210 symmetrically about the mean.'),('A1',r'$\mu=(150+210)/2=180$.')),
 part('b',r'Find $P(M<140)$.',5,('M1',r'$P(M<210)=0.9$.'),('A1',rf'$(210-180)/\sigma=\Phi^{{-1}}(0.9)={f(norm.ppf(.9))}$.'),('A1',rf'$\sigma={ans(sd)}$ grams.'),('M1',r'$P(M<140)=\Phi((140-180)/\sigma)$.'),('A1',rf'$p={ans(small)}$.')),
 part('c','Sixteen independent fruits are packed in a box. Find the probability a box has at most two fruits below 140 g.',3,('M1',r'$X\sim B(16,p)$.'),('M1',r'Calculate $P(X\le2)$ with unrounded $p$.'),('A1',rf'$q={ans(box)}$.')),
 part('d','A crate has 18 independent boxes. Find (i) the expected number with at most two small fruits; (ii) the probability at least 16 boxes have this property.',5,('M1',r'$Y\sim B(18,q)$.'),('A1',rf'$E(Y)=18q={ans(18*box)}$.'),('M1',r'$P(Y\ge16)=1-P(Y\le15)$.'),('A1',r'$P(Y\ge16)=\binom{18}{16}q^{16}(1-q)^2+18q^{17}(1-q)+q^{18}$.'),('A1',rf'${ans(binom.sf(15,18,box))}$.'))])
driveprob=norm.cdf((35-18)/4)-norm.cdf((25-18)/4);ferrycdf=float(norm.cdf(1));sd=4;ferryshort=norm.cdf((25-28)/4);ontime=norm.cdf((25-18)/4)*norm.cdf((35-28)/4)+driveprob*ferryshort
Q(120,'Two possible ferry departures',N,True,r'A traveller leaves home at 07:35. Drive time $D$ minutes follows $N(18,4^2)$. Ferries leave at 08:00 and 08:10. Ferry duration $F$ is independent of driving and follows $N(28,\sigma^2)$. The traveller must arrive by 08:35.',[
 part('a','Find the probability the drive takes between 25 and 35 minutes.',2,('M1',r'$P(25<D<35)=\Phi(17/4)-\Phi(7/4)$.'),('A1',rf'${ans(driveprob)}$.')),
 part('b',rf'Given $P(F<32)={ferrycdf:.9f}$, find $\sigma$ to one significant figure.',3,('M1',r'$(32-28)/\sigma=\Phi^{-1}(P(F<32))$.'),('A1',r'The standard-normal value is approximately 1.'),('A1',r'$\sigma=4$ minutes.')),
 part('c','Find the probability the ferry takes less than 25 minutes.',2,('M1',r'$P(F<25)=\Phi((25-28)/4)$.'),('A1',rf'${ans(ferryshort)}$.')),
 part('d','Find the probability of arriving on time.',4,('M1',r'First ferry: $D\le25$ and $F\le35$.'),('A1',r'Second ferry: $25<D\le35$ and $F\le25$.'),('M1',r'$P=P(D\le25)P(F\le35)+P(25<D\le35)P(F\le25)$.'),('A1',rf'$P={ans(ontime)}$.')),
 part('e','For 220 workdays, find the expected number of on-time arrivals, to the nearest day.',2,('M1','Multiply the daily probability by 220.'),('A1',f'{round(220*ontime)} days.'))])
pa=[.064,.288,.432,.216];pb=[.216,.432,.288,.064];joint=sum(pa[i]*pb[j] for i in range(4) for j in range(4) if i+j>4);numerator=(pa[2]+pa[3])*pb[3]
Q(121,'Combining two independent match totals',R,True,r'Ari and Bea each play three independent matches per day. Their daily win totals $A,B$ have the distributions below. The players’ results and different days are independent.'+table(['Wins','0','1','2','3'],[['$P(A=a)$','$p$','.288','.432','.216'],['$P(B=b)$','.216','.432','.288','.064']]),[
 part('a','Find $p$.',2,('M1','The A probabilities total 1.'),('A1','$p=1-0.288-0.432-0.216=0.064$.')),
 part('b','State the probability Ari wins all three matches in a day. For five days, find the probability Ari wins all three on exactly three days.',4,('A1','The daily probability is 0.216.'),('M1',r'$Y\sim B(5,0.216)$.'),('M1',r'$P(Y=3)=\binom53(0.216)^3(0.784)^2$.'),('A1',rf'${ans(binom.pmf(3,5,.216))}$.')),
 part('c','Find $E(B)$.',3,('M1',r'Use $\sum bP(B=b)$.'),('A1','$0(0.216)+1(0.432)+2(0.288)+3(0.064)$.'),('A1','$E(B)=1.2$.')),
 part('d',r'On one day, find (i) $P(A+B>4)$; (ii) $P(B=3\mid A+B>4)$.',6,('M1','Possible pairs for total greater than 4 are $(2,3),(3,2),(3,3)$.'),('A1','$P=0.432(0.064)+0.216(0.288)+0.216(0.064)$.'),('A1',rf'(i) ${ans(joint)}$.'),('M1','For (ii), retain pairs $(2,3),(3,3)$.'),('A1','$P(B=3,A+B>4)=(0.432+0.216)(0.064)=0.041472$.'),('A1',rf'(ii) ${ans(numerator/joint)}$.'))])
pwin=F(7,22)
Q(122,'Inferring a bag and repeated winning attempts',R,True,r'A variable $X$ has the following distribution and $E(X)=5/6$.'+table(['$x$','0','1','2'],[['$P(X=x)$','$p$','$q$','$5/33$']])+r' It counts red balls in two draws without replacement from a bag containing 12 balls and at least two of each of the colours red and black.',[
 part('a','Find exact $q$ and $p$.',4,('M1','$q+2(5/33)=5/6$.'),('A1','$q=35/66$.'),('M1','$p=1-q-5/33$.'),('A1','$p=7/22$.')),
 part('b','State the probability of two red balls, explain the probability of two black balls, and find the number $k$ of black balls.',5,('A1',r'$P(\text{two red})=5/33$.'),('R1','Two black means zero red, so it is the event $X=0$.'),('A1',r'$P(\text{two black})=7/22$.'),('M1',r'$k(k-1)/(12\cdot11)=7/22$, so $k(k-1)=42$.'),('A1','$k=7$ (reject $-6$).')),
 part('c','The bag is reset after each two-ball game. A player wins with two black balls. Find the probability of exactly three wins in ten games.',2,('M1',r'$P=\binom{10}3(7/22)^3(15/22)^7$.'),('A1',rf'${ans(binom.pmf(3,10,float(pwin)))}$.')),
 part('d','Find the probability the third win occurs on game nine.',4,('M1','There must be two wins in the first eight games and a win in the ninth.'),('A1',r'There are $\binom82$ arrangements for the first eight.'),('M1',r'$P=\binom82(7/22)^3(15/22)^6$.'),('A1',rf'${ans(math.comb(8,2)*float(pwin)**3*(1-float(pwin))**6)}$.'))])
Q(123,'Waiting for the first green marble',R,False,r'A bag has $n$ marbles, exactly two green. Marbles are drawn without replacement until the first green appears.',[
 part('a','Find probabilities that the first green appears on (i) draw 1; (ii) draw 2.',4,('M1','There are two winning marbles among $n$.'),('A1','$P(T=1)=2/n$.'),('M1','First draw non-green, then green.'),('A1',r'$P(T=2)=\frac{n-2}{n}\frac2{n-1}$.')),
 part('b','For $n=7$, find probabilities that it appears on draws 3 and 6.',4,('M1',r'$P(T=3)=\frac57\frac46\frac25$.'),('A1','$P(T=3)=4/21$.'),('M1',r'$P(T=6)=\frac57\frac46\frac35\frac24\frac13\frac22$.'),('A1','$P(T=6)=1/21$.')),
 part('c',r'For $n=7$, a game costs USD 9. Payouts on draws $1,2,3,4,5,6$ are $5k,4k,3k,2k,k,0$ USD. Find $k$ for a fair game.',7,('M1',r'$P(T=j)=(7-j)/\binom72$ for $1\le j\le6$.'),('A1','The probabilities are $6,5,4,3,2,1$ divided by 21.'),('M1','Fairness requires expected payout 9.'),('A1',r'$\frac{k}{21}(5(6)+4(5)+3(4)+2(3)+2)=9$.'),('A1','The weighted payout coefficient is $70/21=10/3$.'),('M1','Solve $(10/3)k=9$ by dividing9 by $10/3$.'),('A1','$k=27/10=2.7$ USD.'))])
mu=120;sd=7/norm.ppf(.96);k=mu+sd*norm.ppf(.35);conditional=(norm.cdf((121-mu)/sd)-.35)/.65
Q(124,'A selected normal subpopulation',N,True,r'Pencil lengths $L$ mm follow $N(120,\sigma^2)$.',[
 part('a',r'Find $P(120-2\sigma<L<120+\sigma)$.',3,('M1','Standardise both endpoints.'),('A1',r'$P=\Phi(1)-\Phi(-2)$.'),('A1',rf'${ans(norm.cdf(1)-norm.cdf(-2))}$.')),
 part('b',r'Given $P(L<127)=0.96$, find $\sigma$.',3,('M1',r'$(127-120)/\sigma=\Phi^{-1}(0.96)$.'),('M1',r'$\sigma=7/\Phi^{-1}(0.96)$.'),('A1',rf'$\sigma={ans(sd)}$ mm.')),
 part('c',r'A pencil is large if $L\ge k$, with probability 0.65. Find $k$.',3,('M1',r'$P(L<k)=0.35$.'),('M1',r'$k=120+\sigma\Phi^{-1}(0.35)$.'),('A1',rf'$k={ans(k)}$ mm.')),
 part('d','(i) Given a large pencil, find the probability it is shorter than 121 mm. (ii) Eighteen large pencils are selected independently; find the probability at least four are shorter than 121 mm.',6,('M1',r'$q=P(k\le L<121)/P(L\ge k)$.'),('M1',r'$q=(\Phi((121-120)/\sigma)-0.35)/0.65$.'),('A1',rf'$q={ans(conditional)}$.'),('M1',r'$Y\sim B(18,q)$.'),('M1',r'$P(Y\ge4)=1-P(Y\le3)$.'),('A1',rf'${ans(binom.sf(3,18,conditional))}$.'))])
Q(125,'A logarithmic probability density',C,False,r'$X$ has density $f(x)=\frac{4\ln x}{x^3}$ for $x\ge1$, and zero otherwise.',[
 part('a',r'Find $P(X<e^2)$ exactly.',5,('M1',r'Integrate $4\ln x\,x^{-3}$ from 1 to $e^2$.'),('A1',r'For integration by parts choose $u=\ln x$, $dv=4x^{-3}dx$, giving $du=dx/x$, $v=-2x^{-2}$.'),('M1',r'An antiderivative is $-2\ln x/x^2+2\int x^{-3}dx$.'),('A1',r'This simplifies to $-(2\ln x+1)/x^2$.'),('A1',r'$P(X<e^2)=1-5e^{-4}$.')),
 part('b',r'Find $P(X\ge e^2)$ exactly.',2,('M1','Take the complement of part (a).'),('A1',r'$5e^{-4}$.'))],notes='Differentiating -(2lnx+1)/x² yields 4lnx/x³; density nonnegative for x≥1 and integrates to1 on [1,∞).')
sd=18/norm.ppf(.9);p=norm.cdf((18-48)/sd);vv=p*(1-p);lo=(1+math.sqrt(1-16*vv))/2;hi=(1+math.sqrt(1-12*vv))/2
Q(126,'Battery lifetimes and a variance inequality',N,True,r'A battery lifetime $E$ months is normal with mean 48 and standard deviation $\sigma$. Ten per cent last longer than 66 months. A battery lasting less than 18 months is defective. All batteries are independent.',[
 part('a',r'Find $\sigma$.',4,('M1',r'$P(E<66)=0.9$.'),('A1',rf'$z=\Phi^{{-1}}(0.9)={f(norm.ppf(.9))}$.'),('M1',r'$\sigma=(66-48)/z$.'),('A1',rf'$\sigma={ans(sd)}$ months.')),
 part('b','Find the defective probability.',2,('M1',r'$p=\Phi((18-48)/\sigma)$.'),('A1',rf'$p={ans(p)}$.')),
 part('c','For 600 batteries, find (i) the probability at least five are defective; (ii) the probability at least nine are defective, given at least five; (iii) the expected defective count, to the nearest integer.',7,('M1',r'$D\sim B(600,p)$.'),('A1',rf'(i) $P(D\ge5)={ans(binom.sf(4,600,p))}$.'),('M1',r'For (ii), divide $P(D\ge9)$ by $P(D\ge5)$.'),('A1',rf'$P(D\ge9)={ans(binom.sf(8,600,p))}$.'),('A1',rf'(ii) ${ans(binom.sf(8,600,p)/binom.sf(4,600,p))}$.'),('M1','For (iii), use $600p$.'),('A1',f'{round(600*p)} batteries.')),
 part('d',r'A second brand has defective probability $k$, where $0.5<k<1$. Each brand is sampled 600 times. Find $k$ such that $3\operatorname{Var}(D)<\operatorname{Var}(D_2)<4\operatorname{Var}(D)$.',5,('M1',r'Cancel 600 to obtain $3p(1-p)<k(1-k)<4p(1-p)$.'),('A1',rf'Using unrounded $p$, the lower and upper bounds on $k(1-k)$ are ${ans(3*vv)}$ and ${ans(4*vv)}$.'),('M1',r'Solve the boundary quadratics with roots $k=(1\pm\sqrt{1-4c})/2$.'),('R1',r'On $k>0.5$, $k(1-k)$ decreases, so the larger variance bound gives the smaller $k$ boundary.'),('A1',rf'${ans(lo)}<k<{ans(hi)}$.'))])
save()
# 127-133
from scipy.integrate import quad
lower=-math.log(math.log(2)+1/16)/math.log(2);ex=quad(lambda x:x*2**(-x),lower,4)[0];ex2=quad(lambda x:x*x*2**(-x),lower,4)[0]
Q(127,'An unknown lower endpoint',C,True,r'The density of $X$ is $f(x)=2^{-x}$ for $a\le x\le4$, and zero otherwise, where $a>0$.',[
 part('a','Find $a$.',5,('M1',r'$\int_a^4 2^{-x}\,dx=1$.'),('A1',r'An antiderivative is $-2^{-x}/\ln2$.'),('A1',r'$(2^{-a}-1/16)/\ln2=1$.'),('M1',r'$a=-\ln(\ln2+1/16)/\ln2$.'),('A1',rf'$a={ans(lower)}$.')),
 part('b','Find the variance of $X$.',3,('M1',rf'$E(X)=\int_a^4 x2^{{-x}}\,dx={f(ex)}$.'),('M1',rf'$E(X^2)=\int_a^4 x^2 2^{{-x}}\,dx={f(ex2)}$.'),('A1',rf'$\operatorname{{Var}}(X)=E(X^2)-E(X)^2={ans(ex2-ex**2)}$.'))],notes='Scipy quadrature verifies density integral1 and computes both moments at the logarithmic endpoint.')
pa=norm.sf(5/3);pb=norm.sf(-1.5);bayes=2*pa/(2*pa+pb)
Q(128,'Combining two normal populations',N,True,r'Type A bulbs have lifetimes $N(16,3^2)$ months. Type B lifetimes follow $N(25,\sigma^2)$ months. Independent purchases are type A with probability $2/3$ and type B with probability $1/3$. A bulb is long-lasting if its lifetime exceeds 21 months.',[
 part('a','Find the probability a type A bulb is long-lasting.',2,('M1',r'$P(A>21)=1-\Phi((21-16)/3)$.'),('A1',rf'${ans(pa)}$.')),
 part('b',rf'Given $P(B<21)={norm.cdf(-1.5):.9f}$, find $\sigma$.',4,('M1',r'Standardise: $P(Z<-4/\sigma)=P(B<21)$.'),('A1',r'$-4/\sigma=\Phi^{-1}(P(B<21))=-1.5$ approximately.'),('M1',r'$\sigma=(-4)/(-1.5)$.'),('A1',r'$\sigma=8/3=2.67$ months.')),
 part('c','Given that a purchased bulb is long-lasting, find the probability it is type A.',6,('M1',r'Use the disjoint cases A and B for long-lasting event $L$.'),('A1',rf'$P(L\mid B)=1-{norm.cdf(-1.5):.9f}={ans(pb)}$.'),('M1',r'$P(L)=\tfrac23P(L\mid A)+\tfrac13P(L\mid B)$.'),('A1',rf'$P(L)={ans((2*pa+pb)/3)}$.'),('M1',r'$P(A\mid L)=\frac{(2/3)P(L\mid A)}{P(L)}$.'),('A1',rf'${ans(bayes)}$.')),
 part('d','Twelve long-lasting bulbs are chosen independently. Find the probability at least two are type A.',3,('M1',r'$Y\sim B(12,P(A\mid L))$.'),('M1',r'$P(Y\ge2)=1-P(Y=0)-P(Y=1)$.'),('A1',rf'${ans(binom.sf(1,12,bayes))}$.'))])
Q(129,'Quartiles of a V-shaped density',C,False,r'$T$ has density $f(t)=|t-4|/9$ for $1\le t\le7$, and zero otherwise.',[
 part('a','Sketch the density, labelling its vertex and endpoint heights.',2,('A1',r'Two line segments join $(1,1/3)$ to $(4,0)$ to $(7,1/3)$.'),('A1',r'The density is zero outside $[1,7]$; label both axes.')),
 part('b','Find the lower quartile and the interquartile range, exactly.',5,('M1',r'$\int_1^{Q_1}(4-t)/9\,dt=1/4$.'),('A1',r'By subtracting the triangle from total left-half area, $1/2-(4-Q_1)^2/18=1/4$.'),('A1',r'$Q_1=4-3/\sqrt2$; choose the root below 4.'),('R1',r'Symmetry about 4 gives $Q_3=4+3/\sqrt2$.'),('A1',r'$\mathrm{IQR}=3\sqrt2$.'))],notes='The two triangular areas total1; direct integration of the quartile expression gives1/4.')
Q(130,'Integrating a trigonometric density',C,False,r'$X$ has density $f(x)=\frac{\pi x}{36}\sin(\pi x/6)$ for $0\le x\le6$, and zero otherwise. Find $P(0\le X\le4)$ exactly.',[
 part('','',7,('M1',r'$P=\int_0^4\frac{\pi x}{36}\sin(\pi x/6)\,dx$.'),('M1',r'Use integration by parts with $u=x$, $dv=(\pi/36)\sin(\pi x/6)dx$.'),('A1',r'$du=dx$, $v=-\cos(\pi x/6)/6$.'),('A1',r'An antiderivative is $-x\cos(\pi x/6)/6+\sin(\pi x/6)/\pi$.'),('M1',r'Evaluate at 4 and subtract the value at 0.'),('A1',r'$-\frac46\cos(2\pi/3)+\frac1\pi\sin(2\pi/3)$.'),('A1',r'$P=\frac13+\frac{\sqrt3}{2\pi}$.'))],notes='Symbolic differentiation verifies the antiderivative; its increment from0 to6 is1.')
Q(131,'Optimising a binomial probability',B,False,r'$X\sim B(12,p)$, where $0<p<1$.',[
 part('a','Write $P(X=9)$ in terms of $p$.',2,('M1',r'Use $P(X=r)=\binom nrp^r(1-p)^{n-r}$.'),('A1',r'$P(X=9)=220p^9(1-p)^3$.')),
 part('b','Find the value of $p$ that maximises this probability, and the resulting expected value of $X$.',6,('M1',r'Differentiate $g(p)=220p^9(1-p)^3$.'),('A1',r'$g\prime(p)=220p^8(1-p)^2(9-12p)$.'),('M1',r'For an interior stationary point solve $9-12p=0$.'),('A1',r'$p=3/4$.'),('R1',r'$g\prime$ is positive before $3/4$ and negative after it, so this is the maximum.'),('A1',r'$E(X)=12(3/4)=9$.'))])
Q(132,'Course choices and sampling without replacement',P,False,r'Of 36 students, 22 study chemistry ($C$), 18 study physics ($P$), and 5 study neither.',[
 part('a','Draw a Venn diagram containing all four region frequencies.',5,('M1',r'$n(C\cup P)=36-5=31$.'),('A1',r'$n(C\cap P)=22+18-31=9$.'),('A1','Chemistry only: $22-9=13$.'),('A1','Physics only: $18-9=9$.'),('A1','Put 5 outside both sets, inside a rectangle representing all36 students.')),
 part('b',r'Find $P(C\mid P\prime)$ and determine whether $C$ and $P\prime$ are independent.',5,('M1',r'$n(P\prime)=36-18=18$.'),('A1',r'$P(C\mid P\prime)=13/18$.'),('M1',r'Compare with $P(C)=22/36$.'),('A1',r'$P(C)=11/18\ne13/18$.'),('R1',r'The events are not independent because the conditional and unconditional probabilities differ.')),
 part('c','Two students are selected without replacement. Find the probability at least one studies physics.',4,('M1','Use the complement: neither selected student studies physics.'),('A1',r'$P(\text{neither})=(18/36)(17/35)$.'),('M1',r'$P(\text{at least one})=1-(18/36)(17/35)$.'),('A1',r'$53/70$.'))])
px=27/80;py=norm.cdf(2)-norm.cdf(-2);cond=.2*py/(.8*px+.2*py)
Q(133,'Two delivery services and transformed charges',C,True,r'Standard delivery time $X$ hours has density $f(x)=x/10$ for $0\le x\le a$, and $f(x)=(10-x)/40$ for $a<x\le10$, zero otherwise. It is known that $P(X\le a)=0.2$. Express delivery time $Y$ is normal with mean 2 hours. Delivery times are independent.',[
 part('a','Show that $a=2$ and $E(X)=4$.',4,('M1',r'$\int_0^a x/10\,dx=a^2/20=0.2$.'),('A1',r'$a=2$ since $a\ge0$.'),('M1',r'$E(X)=\int_0^2x^2/10\,dx+\int_2^{10}x(10-x)/40\,dx$.'),('A1',r'$E(X)=4/15+56/15=4$.')),
 part('b',r'Find $P(1\le X\le3)$.',3,('M1',r'Split at2: $P=\int_1^2x/10\,dx+\int_2^3(10-x)/40\,dx$.'),('A1',r'$P=3/20+3/16$.'),('A1',r'$P=27/80=0.3375$.')),
 part('c',r'Given $E(X^2)=62/3$, find $\operatorname{Var}(X)$.',1,('A1',r'$62/3-4^2=14/3$.')),
 part('d',rf'Given $P(Y\ge {2+.5*norm.ppf(.8):.9f})=0.2$, find the standard deviation of $Y$.',3,('M1',r'The stated endpoint is the80th percentile.'),('M1',r'$\sigma_Y=(2.420810617-2)/\Phi^{-1}(0.8)$.'),('A1',r'$\sigma_Y=0.500$ hours.')),
 part('e',r'Find $P(1\le Y\le3)$.',1,('A1',rf'$\Phi(2)-\Phi(-2)={ans(py)}$.')),
 part('f','A customer independently chooses standard with probability0.8 and express with probability0.2. Given a delivery takes between1 and3 hours, find the probability it was express.',3,('M1',r'$P(1\le T\le3)=0.8(27/80)+0.2P(1\le Y\le3)$.'),('M1',r'Apply Bayes: numerator $0.2P(1\le Y\le3)$ divided by the total.'),('A1',rf'${ans(cond)}$.')),
 part('g',r'The standard charge is $C_X=1.2X+0.8$ USD. Find $E(C_X)$ and $\operatorname{Var}(C_X)$.',3,('M1',r'$E(C_X)=1.2E(X)+0.8$ and $\operatorname{Var}(C_X)=1.2^2\operatorname{Var}(X)$.'),('A1',r'$E(C_X)=5.6$ USD.'),('A1',r'$\operatorname{Var}(C_X)=6.72$ USD$^2$.')),
 part('h',r'The express charge is $C_Y=sY+t$, $s>0$. Its mean is1 USD less than the standard charge and its variance is $1/42$ of the standard-charge variance. Find $s,t$.',3,('M1',r'$s^2(0.5)^2=6.72/42=0.16$.'),('A1',r'$s=0.8$ using $s>0$.'),('A1',r'$2s+t=4.6$, so $t=3$.'))],notes='Piecewise density integrates1, is continuous at2, and symbolic moments are4 and62/3. Mixture and affine moments computed independently.')
save()
# 134-141
p=norm.sf(2/3);sd2=80/norm.ppf(.9);market=norm.sf(10/sd2)/.9
Q(134,'Sorting two fruit populations',N,True,r'Orchard A fruit weights $W$ grams follow $N(300,60^2)$. Orchard B weights $V$ follow $N(420,\sigma^2)$. Fruit weights are independent.',[
 part('a','For orchard A find (i) $P(250<W<340)$; (ii) the expected number weighing more than340 g in a sample of160; (iii) the probability that at least45 of these160 fruits weigh more than340 g.',6,('M1',r'(i) $\Phi((340-300)/60)-\Phi((250-300)/60)$.'),('A1',rf'${ans(norm.cdf(2/3)-norm.cdf(-5/6))}$.'),('M1',r'(ii) $160P(W>340)=160[1-\Phi(2/3)]$.'),('A1',rf'${ans(160*p)}$ fruits.'),('M1',r'(iii) $Z\sim B(160,1-\Phi(2/3))$; use $P(Z\ge45)=1-P(Z\le44)$.'),('A1',rf'${ans(binom.sf(44,160,p))}$.')),
 part('b',r'Orchard B discards all fruits below340 g; this is10% of its production. (i) Find $\sigma$. (ii) Of240 independently selected fruits that have passed this check, find the expected number weighing more than430 g.',6,('M1',r'(i) $(340-420)/\sigma=\Phi^{-1}(0.1)$.'),('M1',r'$\sigma=-80/\Phi^{-1}(0.1)$.'),('A1',rf'$\sigma={ans(sd2)}$ g.'),('M1',r'(ii) $P(V>430\mid V\ge340)=P(V>430)/0.9$.'),('A1',rf'$P(V>430\mid V\ge340)={ans(market)}$.'),('A1',rf'Expected count $=240({ans(market)})={ans(240*market)}$.'))])
Q(135,'Comparing two score distributions',R,False,r'Independent scores $X$ and $Y$ have the distributions below. In the distribution of $Y$, both $q$ and $s$ are strictly positive.'+table(['Score','1','2','3','4'],[['$P(X=x)$','$p$','$2p$','$3p$','$4p$'],['$P(Y=y)$','$q$','$1/5$','$s$','$3/10$']]),[
 part('a','Find $p$.',2,('M1',r'$p+2p+3p+4p=1$.'),('A1',r'$p=1/10$.')),
 part('b','Find $E(X)$.',2,('M1',r'$E(X)=(1+4+9+16)/10$.'),('A1',r'$E(X)=3$.')),
 part('c','Find the range of possible values of $s$.',3,('M1',r'$q+s=1-1/5-3/10=1/2$.'),('A1',r'$q=1/2-s>0$ implies $s<1/2$.'),('A1',r'$0<s<1/2$.')),
 part('d','Find the range of possible values of $E(Y)$.',3,('M1',r'$E(Y)=q+2/5+3s+12/10$.'),('A1',r'$E(Y)=21/10+2s$.'),('A1',r'$21/10<E(Y)<31/10$.')),
 part('e','Given $P(X=Y)=27/100$, find $E(Y)$.',5,('M1',r'Independence gives $P(X=Y)=\sum_{j=1}^4P(X=j)P(Y=j)$.'),('A1',r'$P(X=Y)=q/10+1/25+3s/10+3/25$.'),('M1',r'Substitute $q=1/2-s$: $21/100+s/5=27/100$.'),('A1',r'$s=3/10$ and $q=1/5$.'),('A1',r'$E(Y)=21/10+2(3/10)=27/10$.'))])
Q(136,'Unknown frequency from a moment ratio',R,False,r'A game score has the frequency table below, where $a$ is a positive integer.'+table(['Score','-3','-1','0','2'],[['Frequency','2','$a$','2','2']]),[
 part('a','Find expressions for the mean and variance in terms of $a$.',4,('M1',r'$E(X)=(-6-a+4)/(a+6)$.'),('A1',r'$E(X)=-(a+2)/(a+6)$.'),('M1',r'$E(X^2)=(18+a+8)/(a+6)$; subtract the square of the mean.'),('A1',r'$\operatorname{Var}(X)=\frac{a+26}{a+6}-\frac{(a+2)^2}{(a+6)^2}=\frac{4(7a+38)}{(a+6)^2}$.')),
 part('b','The ratio of the mean to the variance is $-2:13$. Find $a$.',3,('M1',r'$-\frac{(a+2)(a+6)}{4(7a+38)}=-2/13$, giving $13a^2+48a-148=0$.'),('A1',r'$(a-2)(13a+74)=0$, so $a=2$ or $-74/13$.'),('R1',r'$a=2$ since a frequency must be a positive integer.'))])
Q(137,'Combining independent journey stages',C,True,rf'A walking time $W$ minutes is normal. It satisfies $P(W<7)={norm.cdf(-1):.9f}$ and $P(W>12)={norm.sf(1.5):.9f}$. An independent waiting time $T$ has density $f(t)=at$ for $0\le t\le4$, and zero otherwise.',[
 part('a','Find the mean and variance of $W$.',4,('M1',r'$(7-\mu)/\sigma=\Phi^{-1}(0.158655254)\approx-1$.'),('A1',r'$(12-\mu)/\sigma=\Phi^{-1}(1-0.066807201)\approx1.5$.'),('M1',r'Subtract: $5=2.5\sigma$, so $\sigma=2$.'),('A1',r'$E(W)=9$ minutes and $\operatorname{Var}(W)=4$ minutes$^2$.')),
 part('b',r'Find $a$, $E(T)$ and $\operatorname{Var}(T)$.',5,('M1',r'$\int_0^4at\,dt=8a=1$.'),('A1',r'$a=1/8$.'),('M1',r'$E(T)=\int_0^4t^2/8\,dt$.'),('A1',r'$E(T)=8/3$.'),('A1',r'$E(T^2)=\int_0^4t^3/8\,dt=8$, so $\operatorname{Var}(T)=8-(8/3)^2=8/9$.')),
 part('c',r'After a timetable change the waiting time becomes $3T+1$. The train journey takes exactly12 minutes. Find the mean and variance of the total time from the start of walking to arrival.',5,('M1',r'Total $J=W+3T+13$.'),('A1',r'$E(3T+1)=3(8/3)+1=9$.'),('A1',r'$E(J)=9+9+12=30$ minutes.'),('M1',r'Independence implies $\operatorname{Var}(J)=\operatorname{Var}(W)+9\operatorname{Var}(T)$.'),('A1',r'$\operatorname{Var}(J)=4+9(8/9)=12$ minutes$^2$.'))])
Q(138,'A piecewise density and moving limits',C,False,r'$X$ has density $f(x)=3px$ for $0\le x\le2$ and $f(x)=p(8-x)$ for $2<x\le8$, zero otherwise.',[
 part('a','Find $p$.',3,('M1',r'$\int_0^2 3px\,dx+\int_2^8p(8-x)\,dx=1$.'),('A1',r'$6p+18p=1$.'),('A1',r'$p=1/24$.')),
 part('b','Find $P(X<4)$.',3,('M1',r'$P(X<4)=\int_0^2x/8\,dx+\int_2^4(8-x)/24\,dx$.'),('A1',r'$P=1/4+5/12$.'),('A1',r'$P=2/3$.')),
 part('c',r'Find $a$, where $2/3<a<4/3$, such that $P(a<X<4)=2P(3a<X<4)$.',7,('R1',r'The bounds imply $a<2$ and $2<3a<4$; use the appropriate piece on each interval.'),('M1',r'$P(a<X<4)=2/3-\int_0^a x/8\,dx=2/3-a^2/16$.'),('M1',r'$P(3a<X<4)=\int_{3a}^4(8-x)/24\,dx=1-a+3a^2/16$.'),('A1',r'$2/3-a^2/16=2-2a+3a^2/8$.'),('A1',r'$21a^2-96a+64=0$.'),('M1',r'$a=(48\pm8\sqrt{15})/21$.'),('A1',r'$a=(48-8\sqrt{15})/21$; the other root is outside the stated range.'))])
rr=F(15,64);bf=F(25,64)
Q(139,'Alternating draws with different winning colours',P,False,r'A bag has three green and five blue counters. Ada and Ben alternate drawing one counter, replacing it after every draw. Ada goes first and wins on green; Ben wins on blue. Play stops at the first win.',[
 part('a','Find the probability Ada wins on her first turn.',1,('A1',r'$3/8$.')),
 part('b','Find the probability Ada wins on her second turn.',2,('M1',r'Ada must first draw blue, Ben green, then Ada green.'),('A1',r'$(5/8)(3/8)(3/8)=45/512$.')),
 part('c','Find the probability Ben wins on one of his first three turns.',4,('M1',r'One failed pair of turns has probability $r=(5/8)(3/8)=15/64$.'),('A1',r'Ben wins in the first pair with probability $(5/8)(5/8)=25/64$.'),('M1',r'Add the disjoint possibilities: $(25/64)(1+r+r^2)$.'),('A1',rf'${ans(bf*(1+rr+rr**2))}$.')),
 part('d','Find the probability Ben eventually wins.',4,('M1',r'Sum the geometric series $\frac{25}{64}\sum_{j=0}^{\infty}(15/64)^j$.'),('R1',r'The ratio satisfies $|15/64|<1$, so the series converges.'),('A1',r'$P=\frac{25/64}{1-15/64}$.'),('A1',r'$P=25/49$.'))])
Q(140,'A probability parameter and transformed variance',R,False,r'$X$ has the probability distribution below.'+table(['$x$','0','2','4'],[['$P(X=x)$','$7/10-2a$','$3/10-a$','$3a$']]),[
 part('a','Find the possible values of $a$.',2,('M1',r'Nonnegative probabilities require $a\ge0$, $a\le7/20$ and $a\le3/10$.'),('A1',r'$0\le a\le3/10$; the probabilities then total1 and are at most1.')),
 part('b',r'For $a=1/10$, find $\operatorname{Var}(5-3X)$.',6,('A1',r'The probabilities are $1/2,1/5,3/10$.'),('M1',r'$E(X)=0(1/2)+2(1/5)+4(3/10)=8/5$.'),('M1',r'$E(X^2)=4(1/5)+16(3/10)=28/5$.'),('A1',r'$\operatorname{Var}(X)=28/5-(8/5)^2=76/25$.'),('M1',r'$\operatorname{Var}(5-3X)=(-3)^2\operatorname{Var}(X)$.'),('A1',r'$684/25$.'))])
target=binom.cdf(1,12,.45)
Q(141,'Recovering integer binomial parameters',B,True,rf'$X\sim B(n,p)$ has $E(X)=5.4$ and $P(X\le1)={target:.7f}$, rounded to seven decimal places.',[
 part('a','Find the least possible value of $n$.',2,('M1',r'$np=5.4$ and $p\le1$ imply $n\ge5.4$.'),('A1',r'The smallest integer is6.')),
 part('b','Find $n$ and $p$.',5,('M1',r'Substitute $p=5.4/n$.'),('A1',r'$P(X\le1)=(1-5.4/n)^n+5.4(1-5.4/n)^{n-1}$.'),('M1',r'Solve over integer $n\ge6$, or solve continuously then check the neighbouring integers.'),('A1',rf'The values at $n=11,12,13$ are respectively ${binom.cdf(1,11,5.4/11):.7f}$, ${target:.7f}$, ${binom.cdf(1,13,5.4/13):.7f}$; only12 matches.'),('A1',r'$n=12$ and $p=5.4/12=0.45$.'))],notes='Scipy binomial CDF checks the supplied rounded probability and neighbouring integer n; the CDF increases to its Poisson limit for fixed positive mean.')
save()
# 142-149
q=4/7;within=sum(binom.pmf(k,12,q) for k in (6,7,8));above=sum(binom.pmf(k,12,q) for k in (7,8))
Q(142,'A spinner game played in alternating turns',P,True,r'A spinner has four equal regions, one marked WIN and three marked CONTINUE. Independent spins alternate between Ana and Bo, with Ana first. The game ends when a player spins WIN.',[
 part('a','Find the probability Ana wins on her second turn.',2,('M1',r'The first two spins must be CONTINUE and the third WIN.'),('A1',r'$(3/4)^2(1/4)=9/64$.')),
 part('b','Give the probabilities that Ana wins on turns1,2,3,4 of her own.',2,('M1',r'The probability for turn $k$ is $(1/4)(9/16)^{k-1}$.'),('A1',r'$1/4,\ 9/64,\ 81/1024,\ 729/16384$.')),
 part('c','State the common ratio of this sequence.',1,('A1',r'$9/16$.')),
 part('d','Explain why the sum to infinity exists.',1,('R1',r'The sequence is geometric and its ratio has absolute value less than1.')),
 part('e','Find the probability Ana eventually wins.',3,('M1',r'Add the mutually exclusive winning-turn probabilities.'),('M1',r'$P(\text{Ana wins})=\frac{1/4}{1-9/16}$.'),('A1',r'$4/7$.')),
 part('f','They play12 independent games. Let $X$ be the number Ana wins. Given that $X$ is within one standard deviation of its mean, find the probability that $X$ exceeds its mean.',7,('M1',r'$X\sim B(12,4/7)$.'),('A1',r'$\mu=48/7$ and $\sigma=\sqrt{12(4/7)(3/7)}=12/7$.'),('A1',r'$36/7\le X\le60/7$ allows exactly $X=6,7,8$.'),('M1',r'Among these, $X>48/7$ means7 or8.'),('A1',rf'$P(6\le X\le8)={ans(within)}$ and $P(7\le X\le8)={ans(above)}$.'),('M1',r'Divide $P(7\le X\le8)$ by $P(6\le X\le8)$.'),('A1',rf'${ans(above/within)}$.')),
 part('g','A new spinner has eight equal regions. Find how many must be marked WIN so that the first player wins with probability $2/3$.',5,('M1',r'Let a single-spin win probability be $p$.'),('A1',r'The first-player win probability is $p\sum_{j=0}^{\infty}(1-p)^{2j}$.'),('M1',r'It equals $p/[1-(1-p)^2]=1/(2-p)$.'),('A1',r'$1/(2-p)=2/3$ gives $p=1/2$.'),('A1',r'$8p=4$ regions must be WIN.'))])
median=brentq(lambda x:x**4+8*x-16,0,2)
Q(143,'Determining and using a polynomial density',C,True,r'$X$ has density $f(x)=x^3/a+1/b$ for $0\le x\le2$, zero otherwise, where $a,b>0$. It is given that $P(X\le1)=9/32$.',[
 part('a','Find $a$ and $b$.',5,('M1',r'Normalisation gives $4/a+2/b=1$.'),('M1',r'The stated probability gives $1/(4a)+1/b=9/32$.'),('A1',r'Doubling the second equation and subtracting from the first gives $7/(2a)=7/16$.'),('A1',r'$a=8$.'),('A1',r'$1/b=9/32-1/32=1/4$, so $b=4$.')),
 part('b','Find $E(X)$.',2,('M1',r'$E(X)=\int_0^2(x^4/8+x/4)\,dx=[x^5/40+x^2/8]_0^2$.'),('A1',r'$E(X)=13/10$.')),
 part('c','Find the variance of $X$.',2,('M1',r'$E(X^2)=\int_0^2(x^5/8+x^2/4)\,dx=2$.'),('A1',r'$\operatorname{Var}(X)=2-(13/10)^2=31/100$.')),
 part('d','Find the median.',3,('M1',r'$\int_0^m(x^3/8+1/4)\,dx=1/2$.'),('A1',r'$m^4+8m-16=0$.'),('A1',rf'The unique root in $[0,2]$ is $m={ans(median)}$.')),
 part('e','Ten independent values of $X$ are observed. Find the expected number that are at least1, and the probability at least four are at least1.',3,('A1',r'$Y\sim B(10,23/32)$, so $E(Y)=10(23/32)=115/16$.'),('M1',r'$P(Y\ge4)=1-P(Y\le3)$.'),('A1',rf'${ans(binom.sf(3,10,23/32))}$.'))])
Q(144,'Random labels and repeated derangements',P,False,r'Six distinct cards labelled A,B,C,D,E,F are randomly placed into six corresponding labelled slots, one card per slot. Every arrangement is equally likely.',[
 part('a','Find the probability that no card is in its corresponding slot.',6,('M1',r'There are $6!=720$ equally likely arrangements.'),('M1',r'Use inclusion–exclusion on the events that individual cards match their slots.'),('A1',r'For a chosen set of $k$ matching cards there are $(6-k)!$ arrangements, and $\binom6k$ choices of that set.'),('A1',r'The number with no matches is $6!-\binom61 5!+\binom62 4!-\binom63 3!+\binom64 2!-\binom65 1!+\binom66 0!$.'),('A1',r'Equivalently, $720-720+360-120+30-6+1=265$.'),('A1',r'$P(\text{no matches})=265/720=53/144$.')),
 part('b','This experiment is repeated independently144 times. Find the mean and variance of the number of arrangements with no matches.',5,('M1',r'$Y\sim B(144,53/144)$.'),('M1',r'$E(Y)=144(53/144)$.'),('A1',r'$E(Y)=53$.'),('M1',r'$\operatorname{Var}(Y)=144(53/144)(91/144)$.'),('A1',r'$\operatorname{Var}(Y)=4823/144$.'))])
Q(145,'Symmetry and quartiles of a cosine density',C,False,r'$X$ has density $f(x)=h\cos(\pi x/18)$ for $-9\le x\le9$, zero otherwise, where $h>0$.',[
 part('a','Find $h$.',4,('M1',r'$\int_{-9}^9h\cos(\pi x/18)\,dx=1$.'),('A1',r'An antiderivative is $(18h/\pi)\sin(\pi x/18)$.'),('A1',r'$(18h/\pi)(1-(-1))=1$.'),('A1',r'$h=\pi/36$.')),
 part('b','State the mean, median and mode.',3,('A1',r'The mean is0 by symmetry about0.'),('A1',r'The median is0 because each half has probability $1/2$.'),('A1',r'The mode is0, the unique maximum of the cosine density on this interval.')),
 part('c','Find $P(-3<X<0)$ and hence the interquartile range.',6,('M1',r'$P(-3<X<0)=\int_{-3}^0(\pi/36)\cos(\pi x/18)\,dx$.'),('A1',r'$=\tfrac12[\sin(\pi x/18)]_{-3}^0$.'),('A1',r'$=\tfrac12(0-(-1/2))=1/4$.'),('R1',r'As $P(X<0)=1/2$, this gives $Q_1=-3$.'),('A1',r'Symmetry gives $Q_3=3$.'),('A1',r'$\mathrm{IQR}=3-(-3)=6$.')),
 part('d',r'Find $P(X\ge-3\mid X\le3)$.',3,('M1',r'$P=\frac{P(-3\le X\le3)}{P(X\le3)}$.'),('A1',r'The numerator is $1/2$ and denominator is $3/4$.'),('A1',r'$P=2/3$.'))])
p1,p2,p3,p4=F(1,6),F(1,6),F(1,4),F(5,12);psum=3*p1*p4**2+6*p2*p3*p4+p3**3;pmed=3*p4**2*(1-p4)+p4**3;nmin=math.floor(math.log(.03)/math.log(7/12))+1
Q(146,'Four ball values and repeated sampling',R,True,r'A bag contains12 balls: two numbered1, two numbered2, three numbered3 and five numbered4. Balls are drawn independently with replacement. Let $X$ be the number on one draw.',[
 part('a','Find $E(X)$.',2,('M1',r'$E(X)=[1(2)+2(2)+3(3)+4(5)]/12$.'),('A1',r'$35/12$.')),
 part('b','For three draws, find (i) the probability the sum is9; (ii) the probability the median is4.',6,('M1',r'For (i), the unordered triples are $(1,4,4),(2,3,4),(3,3,3)$.'),('A1',r'Their permutation counts are3,6,1.'),('A1',rf'$P=3(1/6)(5/12)^2+6(1/6)(1/4)(5/12)+(1/4)^3={ans(psum)}$.'),('M1',r'For (ii), the median is4 exactly when at least two draws are4.'),('M1',r'$P=\binom32(5/12)^2(7/12)+(5/12)^3$.'),('A1',rf'${ans(pmed)}$.')),
 part('c','In18 draws, find the probability that fewer than seven balls numbered3 are drawn.',3,('M1',r'$Y\sim B(18,1/4)$.'),('A1',r'Fewer than seven means $Y\le6$.'),('A1',rf'$P(Y\le6)={ans(binom.cdf(6,18,.25))}$.')),
 part('d','Find the least number of draws such that the probability of at least one4 exceeds0.97.',3,('M1',r'$1-(7/12)^n>0.97$.'),('M1',r'$n>\ln(0.03)/\ln(7/12)$ because division reverses the inequality.'),('A1',rf'The least integer is $n={nmin}$.')),
 part('e','Another bag contains balls numbered1,2,3,4. In20 independent draws with replacement, the expected counts of2 and3 are5 and7.5, and the variance of the count of1 is $35/16$. Find the least possible total number of balls and the number of4s in that smallest bag.',8,('M1',r'Let the four draw probabilities be $q_1,q_2,q_3,q_4$.'),('A1',r'$q_2=5/20=1/4$ and $q_3=7.5/20=3/8$.'),('M1',r'$20q_1(1-q_1)=35/16$.'),('A1',r'$q_1=1/8$ or $7/8$.'),('R1',r'Reject $7/8$ since $7/8+1/4+3/8>1$.'),('A1',r'$q_4=1-1/8-1/4-3/8=1/4$.'),('M1',r'The integer counts must have ratio $1:2:3:2$.'),('A1',r'The smallest bag has8 balls, including two4s.'))])
Q(147,'Three-valued draws and a second bag',R,True,r'A bag has two balls numbered1, four numbered3 and six numbered6. All draws are independent with replacement. Let $X$ denote the number drawn.',[
 part('a','Find $E(X)$.',2,('M1',r'$E(X)=1(1/6)+3(1/3)+6(1/2)$.'),('A1',r'$25/6$.')),
 part('b','In three draws, find (i) the probability the sum is10; (ii) the probability the median is3.',6,('M1',r'(i) The only unordered triple is $(1,3,6)$, with six permutations.'),('A1',r'$P=6(1/6)(1/3)(1/2)=1/6$.'),('M1',r'(ii) Separate exactly three3s, exactly two3s, and one of each value.'),('A1',r'The first two contributions are $(1/3)^3+3(1/3)^2(2/3)$.'),('M1',r'Add $6(1/6)(1/3)(1/2)$ for one of each.'),('A1',r'$P=1/27+2/9+1/6=23/54$.')),
 part('c','In15 draws, find the probability more than four1s are drawn.',3,('M1',r'$Y\sim B(15,1/6)$.'),('M1',r'$P(Y>4)=1-P(Y\le4)$.'),('A1',rf'${ans(binom.sf(4,15,1/6))}$.')),
 part('d','Find the least number of draws such that the probability of at least one6 exceeds0.95.',3,('M1',r'$1-(1/2)^n>0.95$.'),('M1',r'$n>\ln(0.05)/\ln(1/2)=4.321928\ldots$.'),('A1',r'$n=5$.')),
 part('e','A second bag contains balls numbered1,3,6. In12 independent draws with replacement, the expected count of1s is6 and the variance of the count of3s is $8/3$. Find the least possible total number of balls and the number of6s in that bag.',7,('M1',r'$12q_1=6$ gives $q_1=1/2$.'),('M1',r'$12q_3(1-q_3)=8/3$.'),('A1',r'$q_3(1-q_3)=2/9$, so $q_3=1/3$ or $2/3$.'),('R1',r'Reject $2/3$ because $q_1+q_3>1$.'),('A1',r'$q_6=1-1/2-1/3=1/6$.'),('M1',r'The minimum integer count ratio is $3:2:1$.'),('A1',r'The smallest bag contains6 balls, of which one is numbered6.'))])
Q(148,'Random quadratic roots and conditional probability',N,True,r'$A\sim N(0,1)$. Consider $x^2+2Ax+4=0$.',[
 part('a','Find the values of $A$ for which the equation has two distinct real roots.',2,('M1',r'The discriminant must satisfy $(2A)^2-16>0$.'),('A1',r'$|A|>2$.')),
 part('b','Find the probability the equation has two distinct real roots.',3,('M1',r'$P(|A|>2)=P(A<-2)+P(A>2)$.'),('A1',r'By normal symmetry this is $2[1-\Phi(2)]$.'),('A1',rf'${ans(2*norm.sf(2))}$.')),
 part('c','Given that there are two distinct real roots, find the probability that the root with smaller absolute value has absolute value less than1.',9,('R1',r'The product of the roots is4, so both roots have the same sign.'),('M1',r'Write their absolute values as $t$ and $4/t$, with $0<t<2$.'),('A1',r'The absolute value of their sum is $2|A|=t+4/t$.'),('M1',r'Consider $g(t)=(t+4/t)/2$.'),('A1',r'$g\prime(t)=1/2-2/t^2<0$ for $0<t<2$.'),('R1',r'Therefore $t<1$ is equivalent to $|A|>g(1)=5/2$.'),('M1',r'The required conditional probability is $P(|A|>5/2)/P(|A|>2)$.'),('A1',r'$=\frac{1-\Phi(5/2)}{1-\Phi(2)}$.'),('A1',rf'${ans(norm.sf(2.5)/norm.sf(2))}$.'))])
nmin=next(n for n in range(4,100) if binom.sf(3,n,.25)>.5)
Q(149,'Waiting for a fourth collectible',R,True,r'Each packet independently contains a collectible with probability $1/4$. Let $X$ be the number of packets opened up to and including the fourth collectible.',[
 part('a','Find $P(X=4)$ and $P(X=5)$.',3,('A1',r'$P(X=4)=(1/4)^4=1/256$.'),('M1',r'For $X=5$, exactly three of the first four packets contain a collectible, and packet5 does.'),('A1',r'$P(X=5)=\binom43(1/4)^4(3/4)=3/256$.')),
 part('b',r'Show that $P(X=n)=\frac{(n-1)(n^2+an+b)}{1536}(3/4)^{n-4}$ for $n\ge4$, and find $a,b$.',5,('M1',r'The first $n-1$ packets must contain exactly three collectibles.'),('A1',r'There are $\binom{n-1}3$ choices of their positions.'),('M1',r'Multiply by the probability of the required sequence, including the final collectible: $\binom{n-1}3(1/4)^4(3/4)^{n-4}$.'),('A1',r'$=\frac{(n-1)(n-2)(n-3)}{1536}(3/4)^{n-4}$.'),('A1',r'$(n-2)(n-3)=n^2-5n+6$, hence $a=-5,b=6$.')),
 part('c',r'For $n\ge5$, simplify $P(X=n)/P(X=n-1)$.',4,('M1',r'Divide the consecutive probability formulas.'),('A1',r'The polynomial ratio is $\frac{(n-1)(n-2)(n-3)}{(n-2)(n-3)(n-4)}$.'),('A1',r'The power ratio is $3/4$.'),('A1',r'$\frac{P(X=n)}{P(X=n-1)}=\frac{3(n-1)}{4(n-4)}$.')),
 part('d','Find all modes of $X$, justifying your answer.',5,('M1',r'The probability increases when the ratio in(c) is greater than1.'),('A1',r'$3(n-1)>4(n-4)$ gives $n<13$.'),('A1',r'At $n=13$ the ratio is1, so $P(X=13)=P(X=12)$.'),('R1',r'For $n>13$ the ratio is less than1, so probabilities decrease thereafter.'),('A1',r'The modes are12 and13.')),
 part('e','Find the least integer $N$ such that the probability of obtaining at least four collectibles in $N$ packets exceeds0.5.',3,('M1',r'Let $Y\sim B(N,1/4)$ and require $P(Y\ge4)>0.5$.'),('A1',rf'For $N={nmin-1}$ the probability is ${ans(binom.sf(3,nmin-1,.25))}$; for $N={nmin}$ it is ${ans(binom.sf(3,nmin,.25))}$.'),('A1',rf'The least $N$ is ${nmin}$.'))])
save()
print('Saved',len(OUT),'statistics/probability variants')
# Independent assertions of representative exact results and every schema/source mapping.
def verify():
 for n,obj in OUT.items():
  assert obj['source']['question']==n and obj['number']==n
  assert obj['marks']==REF[n-1]['marks'] and obj['difficulty']==REF[n-1]['difficulty']
  assert obj['marks']==sum(int(step['code'][1:]) for g in obj['markScheme'] for step in g['steps'])
  for g in obj['markScheme']:
   if obj['parts']:
    p=next(p for p in obj['parts'] if p['label']==g['part'])
    assert p['marks']==sum(int(t['code'][1:]) for t in g['steps'])
  raw=json.dumps(obj,ensure_ascii=False)
  assert all(ord(c)>=32 or c in '\n\r\t' for c in raw)
 assert set(OUT)==set(range(1,150))
 # Exact polynomial and moment identities.
 x=sy.symbols('x',real=True)
 assert sy.integrate(sy.Rational(2,9)*(x-1)*(4-x),(x,1,4))==1
 assert sy.integrate(x*sy.Rational(2,9)*(x-1)*(4-x),(x,1,4))==sy.Rational(5,2)
 assert sy.integrate(x*x*sy.Rational(2,9)*(x-1)*(4-x),(x,1,4))==sy.Rational(67,10)
 assert sy.integrate(x/10,(x,0,2))+sy.integrate((10-x)/40,(x,2,10))==1
 assert sy.integrate(x*x/10,(x,0,2))+sy.integrate(x*(10-x)/40,(x,2,10))==4
 assert sy.integrate(x**3/10,(x,0,2))+sy.integrate(x*x*(10-x)/40,(x,2,10))==sy.Rational(62,3)
 assert sy.integrate(x**3/8+sy.Rational(1,4),(x,0,2))==1
 assert sy.integrate(x*(x**3/8+sy.Rational(1,4)),(x,0,2))==sy.Rational(13,10)
 assert sy.integrate(x*x*(x**3/8+sy.Rational(1,4)),(x,0,2))==2
 assert sy.integrate(sy.pi*x/36*sy.sin(sy.pi*x/6),(x,0,6))==1
 assert sy.simplify(sy.integrate(sy.pi*x/36*sy.sin(sy.pi*x/6),(x,0,4))-sy.Rational(1,3)-sy.sqrt(3)/(2*sy.pi))==0
 assert sy.integrate(sy.pi/36*sy.cos(sy.pi*x/18),(x,-9,9))==1
 assert sy.integrate(sy.pi/36*sy.cos(sy.pi*x/18),(x,-3,0))==sy.Rational(1,4)
 assert sy.integrate(4*sy.log(x)/x**3,(x,1,sy.oo))==1
 assert sy.simplify(sy.integrate(4*sy.log(x)/x**3,(x,1,sy.exp(2)))-(1-5*sy.exp(-4)))==0
 assert sy.integrate(x/8,(x,0,2))+sy.integrate((8-x)/24,(x,2,8))==1
 aq=(48-8*math.sqrt(15))/21
 assert 2/3<aq<4/3 and abs((2/3-aq*aq/16)-2*(1-aq+3*aq*aq/16))<1e-12
 al=-math.log(math.log(2)+1/16)/math.log(2)
 assert al>0 and abs(quad(lambda t:2**(-t),al,4)[0]-1)<1e-12
 assert sum(math.comb(9-j,2) for j in range(1,8))==math.comb(9,3)
 assert sum(range(1,7))==math.comb(7,2)
 assert sum(all(v!=i for i,v in enumerate(perm)) for perm in itertools.permutations(range(6)))==265
 # Independent enumeration of three-draw scores and medians.
 for vals,pr,target,total,medv,medprob in [([1,2,3,4],[F(1,6),F(1,6),F(1,4),F(5,12)],9,F(275,1152),4,F(325,864)),([1,3,6],[F(1,6),F(1,3),F(1,2)],10,F(1,6),3,F(23,54))]:
  dist=dict(zip(vals,pr));ps=F(0);pm=F(0)
  for seq in itertools.product(vals,repeat=3):
   prob=math.prod(dist[v] for v in seq)
   if sum(seq)==target:ps+=prob
   if sorted(seq)[1]==medv:pm+=prob
  # Compare with direct formula retained in authored working.
  if len(vals)==4:
   assert ps==3*pr[0]*pr[3]**2+6*pr[1]*pr[2]*pr[3]+pr[2]**3
   assert pm==3*pr[3]**2*(1-pr[3])+pr[3]**3
  else:assert ps==total and pm==medprob
 # Negative-binomial modes and binomial integer threshold are independently enumerated.
 pmf=[math.comb(n-1,3)*(.25**4)*(.75**(n-4)) for n in range(4,100)]
 assert [i+4 for i,p in enumerate(pmf) if abs(p-max(pmf))<1e-14]==[12,13]
 threshold=next(n for n in range(4,100) if binom.sf(3,n,.25)>.5)
 assert binom.sf(3,threshold-1,.25)<=.5<binom.sf(3,threshold,.25)
 for probs in [[.12,.38,.32,.18],[.15,.25,.35,.25],[.08,.2,.3,.25,.12,.05],[.064,.288,.432,.216],[.216,.432,.288,.064],[1/6,1/6,1/4,5/12],[1/6,1/3,1/2]]:
  assert all(0<=p<=1 for p in probs) and abs(sum(probs)-1)<1e-12
 return True
assert verify()
print('Verified149 source mappings/mark totals; symbolic densities/moments, discrete enumerations and binomial thresholds passed')
