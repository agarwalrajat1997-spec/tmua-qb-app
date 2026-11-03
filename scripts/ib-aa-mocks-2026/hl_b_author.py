"""Reconstruct HL Set B from the supplied solution books, with executable checks.

Question wording/givens are reconstructed, not asserted to be recovered originals.
Source page references and resolved mathematical errors remain in an internal ledger.
"""
from pathlib import Path
from fractions import Fraction as F
from statistics import NormalDist, mean
import json, math, html, hashlib, re
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'content/ib/aa-mocks-2026/papers'
DOC=ROOT/'docs/ib-aa-mocks-2026'
PAPERS=[]; RECORDS=[]; ERRATA=[]

def step(code,text): return {'code':code,'text':text}
def M(text,n=1):return step('M'+str(n),text)
def A(text,n=1):return step('A'+str(n),text)
def R(text,n=1):return step('R'+str(n),text)
def p(label,prompt,*steps):return {'label':label,'prompt':prompt,'marks':sum(int(s['code'][1:]) for s in steps),'steps':list(steps)}
def check(label,actual,expected,tol=1e-8):
    assert math.isclose(actual,expected,rel_tol=tol,abs_tol=tol),(label,actual,expected)
    return {'test':label,'actual':actual,'expected':expected,'status':'passed'}
def yes(label,value):
    assert value,label
    return {'test':label,'status':'passed'}
def question(n,section,stem,parts,pages,evidence,diagram=None):
    q={'number':n,'section':section,'marks':sum(x['marks'] for x in parts),'stem':stem,
       'parts':[{k:x[k] for k in ['label','prompt','marks']} for x in parts],
       'markScheme':[{'part':x['label'],'steps':x['steps']} for x in parts],
       'answerSummary':' '.join(s['text'] for x in parts for s in x['steps'] if s['code'][0]=='A'),
       'sourcePages':pages}
    if diagram:q['diagramSvg']=diagram
    RECORDS.append({'paper':CURRENT,'number':n,'sourcePages':pages,'status':'passed','checks':evidence,
       'reconstructionReview':'Read complete native source pages, reconstructed every supplied part and marking total, checked assumptions/domains and re-solved the resulting question.'})
    return q
def paper(number,questions):
    q={'id':f'aa-hl-set-b-paper-{number}','course':'hl','set':'B','paper':str(number),
       'title':f'Mathematics AA HL · Set B · Paper {number}','minutes':75 if number==3 else 120,
       'marks':55 if number==3 else 110,'calculator':number!=1,'questions':questions}
    assert sum(x['marks'] for x in questions)==q['marks'],(q['id'],sum(x['marks'] for x in questions))
    assert [x['number'] for x in questions]==list(range(1,len(questions)+1))
    PAPERS.append(q)
def svg(body,title,w=900,h=520):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(title)}"><rect width="{w}" height="{h}" fill="white"/>'+body+'</svg>'
def tx(x,y,t,size=19,anchor='middle'):
    return f'<text x="{x:g}" y="{y:g}" font-family="Arial,sans-serif" font-size="{size}" text-anchor="{anchor}" fill="#111">{html.escape(str(t))}</text>'
def ln(x,y,u,v,dash=False):
    return f'<path d="M{x:g} {y:g}L{u:g} {v:g}" stroke="#111" stroke-width="2" fill="none"'+(' stroke-dasharray="7 5"' if dash else '')+'/>'
def plot(series,xmin,xmax,ymin,ymax,title,xticks=(),yticks=(),extra=''):
    X=lambda x:90+720*(x-xmin)/(xmax-xmin);Y=lambda y:430-350*(y-ymin)/(ymax-ymin)
    ox=X(0) if xmin<=0<=xmax else 90; oy=Y(0) if ymin<=0<=ymax else 430
    body=tx(450,30,title,21)+ln(90,oy,820,oy)+ln(ox,70,ox,440)
    for x in xticks:body+=ln(X(x),oy-4,X(x),oy+4)+tx(X(x),oy+27,x,16)
    for y in yticks:body+=ln(ox-4,Y(y),ox+4,Y(y))+tx(ox-14,Y(y)+5,y,16,'end')
    body+=tx(840,oy+7,'x')+tx(ox+15,60,'y')
    for j,(name,fun,lo,hi) in enumerate(series):
        pts=[(lo+(hi-lo)*k/200,fun(lo+(hi-lo)*k/200)) for k in range(201)]
        pts=[(X(x),Y(y)) for x,y in pts if ymin<=y<=ymax]
        body+='<polyline points="'+' '.join(f'{x:.3f},{y:.3f}' for x,y in pts)+'" fill="none" stroke="#111" stroke-width="2.3"'+(' stroke-dasharray="7 5"' if j%2 else '')+'/>'
        body+=tx(580+j*120,60,name,17)
    return svg(body+extra,title)
def simpson(fun,a,b,n=12000):
    h=(b-a)/n
    return h/3*(fun(a)+fun(b)+sum((4 if k%2 else 2)*fun(a+k*h) for k in range(1,n)))
def bisect(fun,a,b):
    for _ in range(100):
        c=(a+b)/2
        if fun(a)*fun(c)<=0:b=c
        else:a=c
    return (a+b)/2

CURRENT='aa-hl-set-b-paper-1';Q=[]
Q.append(question(1,'A',r'Points $A(1,1,1)$, $B(2,-2,5)$ and $C(3,0,3)$ define a triangle in three-dimensional space.',[
 p('a',r'Find $\overrightarrow{AB}\times\overrightarrow{AC}$.',A(r'$\overrightarrow{AB}=(1,-3,4)$ and $\overrightarrow{AC}=(2,-1,2)$.',2),A(r'$\overrightarrow{AB}\times\overrightarrow{AC}=(-2,6,5)$.')),
 p('b','Find the exact area of triangle ABC.',M(r'$\text{Area}=\frac12|\overrightarrow{AB}\times\overrightarrow{AC}|$.'),A(r'$\text{Area}=\sqrt{65}/2$.')),
 p('c','Find a Cartesian equation of the plane through A, B and C.',M(r'A normal is $(-2,6,5)$, so $-2x+6y+5z=d$.'),A(r'At $A$, $d=-2+6+5=9$; hence $-2x+6y+5z=9$.'))], [2],
 [check('cross x',-3*2-4*(-1),-2),check('cross y',4*2-1*2,6),check('cross z',1*(-1)-(-3)*2,5),check('normal dotAB',-2+6*(-3)+5*4,0),check('plane constant',-2+6+5,9)]))
ERRATA.append({'paper':CURRENT,'pdfPage':2,'question':1,'issue':'Both plane equations print6z where6y is required.','correction':r'$-2x+6y+5z=d$ and $-2x+6y+5z=9$.'})
Q.append(question(2,'A',r'Let $f(x)=x^2+ax+b+2$ and $g(x)=ax^2+bx+c-1$, where $a\ne0$. It is given that $f(1)=g(1)$.',[
 p('a',r'Find $c$.',M(r'$1+a+b+2=a+b+c-1$.'),A(r'$c=4$.')),
 p('b',r'The equations $f(x)=b+4$ and $g(x)=-1$ have the same two roots. Find $a$ and $b$.',A(r'The equations reduce to $x^2+ax-2=0$ and $ax^2+bx+c=0$; equal root sums give $-a=-b/a$, so $b=a^2$.'),M(r'Equal root products give $-2=c/a$.'),A(r'With $c=4$, $a=-2$.'),A(r'$b=4$.'))],[3],
 [check('c equality',1-2+4+2,(-2)+4+4-1),check('sum constraint',4,(-2)**2),check('product constraint',4/(-2),-2)]))
Q.append(question(3,'A',r'In this question $\operatorname{cis}\theta=\cos\theta+i\sin\theta$.',[
 p('a',r'Find all three solutions of $z^3=64i$, expressing each in the form $a+bi$.',M(r'Write $z=r\operatorname{cis}\theta$ and $64i=64\operatorname{cis}(\pi/2)$.'),A(r'$r=4$.'),M(r'$3\theta=\pi/2+2k\pi$.'),A(r'$\theta=\pi/6+2k\pi/3$, $k=0,1,2$.'),A(r'Two roots are $2\sqrt3+2i$ and $-2\sqrt3+2i$.'),A(r'The third root is $-4i$.')),
 p('b',r'Hence solve $(z+2i)^3=64i$.',M(r'Subtract $2i$ from each root in part(a).'),A(r'$z=2\sqrt3,-2\sqrt3,-6i$.'))],[4],
 [check('root real component cubed',(complex(2*math.sqrt(3),2)**3).real,0),check('root imaginary component cubed',(complex(2*math.sqrt(3),2)**3).imag,64),check('third root cube',(((-4j)**3)/1j).real,64)]))
wave=plot([('h',lambda x:9-5*math.cos(math.pi*x/8),0,24)],0,26,0,16,'A periodic model',(0,8,16,24),(4,9,14))
Q.append(question(4,'A',r'The graph shows a periodic function $h(x)=p\cos(qx)+r$, where $q>0$. The curve starts at a minimum when $x=0$ and completes one and a half periods between $x=0$ and $x=24$.',[
 p('a','Find the period.',M(r'$24$ corresponds to $1.5$ periods.'),A(r'The period is $16$.')),
 p('b',r'Find $p$, $q$ and $r$.',A(r'The midline is $r=9$.'),M(r'The amplitude is $5$, with a minimum at $x=0$.'),A(r'$p=-5$.'),M(r'$q=2\pi/16$.'),A(r'$q=\pi/8$.'))],[5],
 [check('midline',(14+4)/2,9),check('amplitude',(14-4)/2,5),check('period',24/1.5,16)],wave))
Q.append(question(5,'A',r'Solve $4^{x+1}\,3^{2x+1}=18^{x+1}$, giving your answer in the form $a+\log_2 b$, where $a$ and $b$ are integers.',[
 p('',r'Show your algebraic working.',M(r'$4^x\cdot4\cdot3^{2x}\cdot3=18^x\cdot18$.'),M(r'$4^x3^{2x}/18^x=18/12$.'),A(r'$(36/18)^x=3/2$.'),A(r'$2^x=3/2$.'),M(r'Take logarithms to base2.'),A(r'$x=-1+\log_2 3$.'))],[6],
 [check('solution substitution ratio',4**math.log2(3)*3**(2*(math.log2(3)-1)+1)/18**math.log2(3),1)]))
Q.append(question(6,'A',r'The function $y(x)$ satisfies $\displaystyle\frac{dy}{dx}+\frac{4x^3}{1+x^4}y=5$ and $y(1)=1$.',[
 p('',r'Find $y$ in terms of $x$.',M(r'This is linear with $P(x)=4x^3/(1+x^4)$.'),A(r'The integrating factor is $e^{\int P(x)\,dx}=1+x^4$.'),M(r'$\frac{d}{dx}[(1+x^4)y]=5(1+x^4)$.'),A(r'Integrating gives $(1+x^4)y=x^5+5x+c$.',2),A(r'$2=1+5+c$, hence $c=-4$.'),A(r'$y=(x^5+5x-4)/(1+x^4)$, valid for all real$x$.'))],[7],
 [check('initial condition',(1+5-4)/2,1),check('IF derivative at2',4*2**3,32)]))
Q.append(question(7,'A',r'Let $f(x)=\frac32x^4-\frac13x^3-\frac52x^2+1$.',[
 p('a',r'Find the gradient of the tangent to the graph of $f$ at $x=-1$.',M(r'$f\prime(x)=6x^3-x^2-5x$.'),A(r'$f\prime(-1)=-2$.')),
 p('b',r'Find the other two values of $x$ at which the tangent is parallel to the tangent in part(a).',M(r'Solve $6x^3-x^2-5x+2=0$.'),M(r'The known root$-1$ gives factor$x+1$.'),A(r'$6x^3-x^2-5x+2=(x+1)(6x^2-7x+2)$.'),A(r'$x=2/3$.'),A(r'$x=1/2$.'))],[8],
 [check('known derivative',6*(-1)**3-(-1)**2-5*(-1),-2),check('otherroot1',6*(2/3)**3-(2/3)**2-5*(2/3),-2),check('otherroot2',6*(.5)**3-.5**2-5*.5,-2)]))
Q.append(question(8,'A',r'An arrangement uses each of the nine distinct digits 1 to 9 and each of three distinct symbols (dollar sign, at sign and hash sign) exactly once. Let $A$ be the number of arrangements in which the three symbols are consecutive. Let $B$ be the number in which no two symbols are consecutive.',[
 p('',r'By finding expressions for $A$ and $B$, show that $B=12A$.',M(r'For$A$, treat the three symbols as one block alongside nine digits.'),A(r'Arrange ten objects in$10!$ways.'),A(r'Arrange the symbols within their block in$3!$ways: $A=10!3!$.'),M(r'For$B$, the nine ordered digits make ten gaps; assign three distinct symbols to different gaps.'),A(r'The gap assignment has$10\cdot9\cdot8$possibilities.'),A(r'$B=10\cdot9\cdot8\cdot9!$.'),A(r'$B/A=(9\cdot8)/3!=12$, as required.'))],[9],
 [check('arrangement ratio',(10*9*8*math.factorial(9))/(math.factorial(10)*math.factorial(3)),12)]))
triangle=svg(tx(450,30,'Triangle ABC; D is the perpendicular foot',21)+ln(110,390,760,390)+ln(110,390,643.333,80)+ln(760,390,643.333,80)+ln(643.333,80,643.333,390,True)+tx(95,415,'A')+tx(780,415,'B')+tx(643,62,'C')+tx(644,420,'D')+tx(210,368,'x°')+tx(722,367,'2x°')+tx(740,220,'25')+ln(643.333,372,625.333,372)+ln(625.333,372,625.333,390),'Triangle with angles x and2x')
Q.append(question(9,'B',r'In triangle $ABC$, $\angle CAB=x^\circ$, $\angle ABC=2x^\circ$ and $BC=25$. Point $D$ is the foot of the perpendicular from $C$ to $AB$. It is given that $\sin x=3/5$ and $0<x<90$. The diagram is schematic.',[
 p('a',r'Find the exact values of $\cos x$ and $\sin 2x$.',M(r'Use$\sin^2x+\cos^2x=1$and the acute-angle condition.'),A(r'$\cos x=4/5$.',2),A(r'$\sin2x=2(3/5)(4/5)=24/25$.')),
 p('b',r'Find $\cos2x$ exactly.',M(r'$\cos2x=1-2\sin^2x$.'),A(r'$1-2(3/5)^2=1-18/25$.'),A(r'$\cos2x=7/25$.')),
 p('c',r'Find $AC$.',M(r'By the sine rule,$25/\sin x=AC/\sin2x$.'),A(r'$AC=25(24/25)/(3/5)$.'),A(r'$AC=40$.')),
 p('d',r'Find $AD$.',M(r'$AD/AC=\cos x$, with$AC=40$.',2),A(r'$AD=32$.')),
 p('e',r'Find $BD$.',M(r'$BD/BC=\cos2x$.'),A(r'$BD=25(7/25)=7$.')),
 p('f',r'Hence find $AB$ and the area of triangle $ABC$.',A(r'$AB=AD+BD=39$.'),M(r'Area$=\tfrac12(40)(39)\sin x$.'),A(r'Area$=468$.'))],[10],
 [check('AC sine rule',25*(24/25)/(3/5),40),check('AD',40*4/5,32),check('BD',25*7/25,7),check('triangle area',.5*40*39*3/5,468)],triangle))
Q.append(question(10,'B',r'The function $f:\mathbb R\to\mathbb R$ is defined by $f(x)=e^{2x}+e^x+x-6$.',[
 p('a(i)',r'Show that $f$ is strictly increasing on its domain.',M(r'$f\prime(x)=2e^{2x}+e^x+1$.'),A(r'Every term is positive, so$f\prime(x)>0$for every real$x$.')),
 p('a(ii)',r'Show that its graph is concave upwards everywhere.',A(r'$f\prime\prime(x)=4e^{2x}+e^x$.'),A(r'$f\prime\prime(x)>0$for all real$x$.')),
 p('b',r'On the same axes sketch $y=f(x)$, $y=f^{-1}(x)$ and $y=x$. Label the $y$-intercept of $f$ and the corresponding intercept of its inverse. Show qualitatively where all three meet.',A(r'The inverse is the reflection of$f$in$y=x$; correct increasing reflected shapes.',2),A(r'The two curves meet on$y=x$at their common fixed point.'),A(r'$f(0)=-4$, giving$(0,-4)$and inverse intercept$(-4,0)$.')),
 p('c',r'Find the exact coordinates of the common point of the three graphs, justifying why an intersection of $f$ and its inverse must lie on $y=x$.',M(r'Because$f$is strictly increasing, a nontrivial2-cycle is impossible; an intersection must satisfy$f(x)=x$.'),M(r'$e^{2x}+e^x-6=0$; put$u=e^x$.'),A(r'$(u-2)(u+3)=0$.'),A(r'Reject$u=-3$because$e^x>0$.'),A(r'The common point is$(\ln2,\ln2)$.')),
 p('d',r'The graph of $y=2f(x)+k$ passes through the origin. Find $k$.',M(r'$0=2f(0)+k=-8+k$.'),A(r'$k=8$.')),
 p('e',r'For $x>0$, simplify $f(\ln x)-\ln x$.',M(r'$e^{2\ln x}+e^{\ln x}+\ln x-6-\ln x$.'),A(r'$x^2+x-6$.'))],[11],
 [check('f0',1+1-6,-4),check('fixed point residual',math.exp(2*math.log(2))+math.exp(math.log(2))-6,0),check('shift',2*(-4)+8,0)]))
ERRATA.extend([{'paper':CURRENT,'pdfPage':11,'question':10,'issue':'Inverse graph prose gives x-intercept4 despite plotted-4.','correction':'The inverse x-intercept is -4.'},{'paper':CURRENT,'pdfPage':11,'question':10,'issue':'Part(e) inserts false equality f(lnx)-lnx=f(x).','correction':r'$f(\ln x)-\ln x=e^{2\ln x}+e^{\ln x}-6=x^2+x-6$, $x>0$.'}])
Q.append(question(11,'B',r'The sequence $(u_n)$ is defined by $u_0=1$ and $u_{n+1}=4^{n+1}-(n+1)u_n$ for $n=0,1,2,\ldots$. Also define $\displaystyle I_n=\int_0^1x^n e^{4x}\,dx$.',[
 p('a',r'Find $u_1$ and $u_2$.',A(r'$u_1=4-1=3$.'),A(r'$u_2=16-2(3)=10$.')),
 p('b',r'Find $I_0$ exactly.',A(r'$I_0=[e^{4x}/4]_0^1=(e^4-1)/4$.')),
 p('c',r'Use integration by parts to show that $I_{n+1}=e^4/4-(n+1)I_n/4$.',M(r'Choose$u=x^{n+1}$and$dv=e^{4x}dx$.'),A(r'$du=(n+1)x^n dx$and$v=e^{4x}/4$.'),A(r'$I_{n+1}=[x^{n+1}e^{4x}/4]_0^1-(n+1)I_n/4$.'),A(r'The boundary term is$e^4/4$, giving the stated recurrence.')),
 p('d(i)',r'Find $I_1$ exactly.',M(r'$I_1=e^4/4-I_0/4$.'),A(r'$I_1=(3e^4+1)/16$.')),
 p('d(ii)',r'Find $I_2$ exactly.',M(r'$I_2=e^4/4-2I_1/4$.'),A(r'$I_2=(5e^4-1)/32$.')),
 p('e',r'Hence evaluate $\displaystyle\int_0^1(64x^2+16x+4)e^{4x}\,dx$.',M(r'The integral is$64I_2+16I_1+4I_0$.'),A(r'Substitute the exact results.'),A(r'The value is$14e^4-2$.')),
 p('f',r'Prove by mathematical induction that $\displaystyle I_n=\frac{u_ne^4+(-1)^{n+1}n!}{4^{n+1}}$ for every integer $n\ge0$.',A(r'At$n=0$the expression is$(e^4-1)/4=I_0$.'),M(r'Assume the formula holds for$n=k$.'),A(r'The required next formula is$I_{k+1}=[u_{k+1}e^4+(-1)^{k+2}(k+1)!]/4^{k+2}$.'),M(r'Substitute the induction hypothesis in$I_{k+1}=e^4/4-(k+1)I_k/4$.'),A(r'The numerator becomes$[4^{k+1}-(k+1)u_k]e^4+(-1)^{k+2}(k+1)!=u_{k+1}e^4+(-1)^{k+2}(k+1)!$.'),R(r'The base case and implication$k\Rightarrow k+1$prove the result for all$n\ge0$.'))],[12,13],
 [check('u1',4-1,3),check('u2',16-2*3,10),check('I1 numerical',simpson(lambda x:x*math.exp(4*x),0,1),(3*math.exp(4)+1)/16),check('I2 numerical',simpson(lambda x:x*x*math.exp(4*x),0,1),(5*math.exp(4)-1)/32),check('weighted integral',simpson(lambda x:(64*x*x+16*x+4)*math.exp(4*x),0,1),14*math.exp(4)-2)]))
ERRATA.append({'paper':CURRENT,'pdfPage':13,'question':11,'issue':'Induction target prose repeats n=k.','correction':'Prove the statement for n=k+1.'})
paper(1,Q)

CURRENT='aa-hl-set-b-paper-2';Q=[]
Q.append(question(1,'A',r'A fair coin is tossed twelve times independently. Let $X$ be the number of tails.',[
 p('a',r'Find the probability that the numbers of heads and tails are equal.',A(r'$X\sim\operatorname{Bin}(12,1/2)$.'),M(r'Use$P(X=6)=\binom{12}{6}(1/2)^{12}$.'),A(r'$P(X=6)=0.2255859375\approx0.226$.')),
 p('b','Find the probability that there are more tails than heads.',M(r'By symmetry,$P(X\ge7)=[1-P(X=6)]/2$.',2),A(r'$P(X\ge7)=0.38720703125\approx0.387$.'))],[2],
 [check('equal counts binomial',math.comb(12,6)/2**12,.2255859375),check('upper tail',sum(math.comb(12,k) for k in range(7,13))/2**12,.38720703125)]))
xs=[12,15,17,28,23];ys=[127,142,144,171,151]
sxx=sum((x-19)**2 for x in xs);sxy=sum((x-19)*(y-147) for x,y in zip(xs,ys));syy=sum((y-147)**2 for y in ys)
Q.append(question(2,'A',r'The paired data are shown below. The unknown value $a$ is a whole number. A rounded equation of the least-squares regression line of $y$ on $x$ is $y=2.398x+101.446$.'+'\n\n|$x$|12|15|17|28|$a$|\n|---|---|---|---|---|---|\n|$y$|127|142|144|171|151|',[
 p('a',r'Find $\bar y$.',A(r'$\bar y=735/5=147$.')),
 p('b(i)',r'Use the regression line and the fact that $(\bar x,\bar y)$ lies on it to estimate $\bar x$, giving your result to the nearest whole number.',M(r'$147=2.398\bar x+101.446$using the rounded line.'),A(r'$\bar x\approx18.9967$, hence$\bar x=19$to the required precision.')),
 p('b(ii)',r'Hence find $a$.',M(r'$(12+15+17+28+a)/5=19$.'),A(r'$a=23$.')),
 p('c',r'Calculate the product-moment correlation coefficient.',A(r'$r=398/\sqrt{166\cdot1026}=0.96439588\ldots\approx0.964$.'))],[3],
 [check('y mean',mean(ys),147),check('x mean',mean(xs),19),check('regression slope',sxy/sxx,2.397590361445783),check('regression intercept',147-sxy/sxx*19,101.44578313253012),check('correlation',sxy/math.sqrt(sxx*syy),.9643958783584392,1e-7)]))
RECORDS[-1]['reconstructionReview']+=' The raw dataset was underdetermined by the source; this constructed compatible dataset reproduces every supplied rounded regression statistic and answer.'
Q.append(question(3,'A',r'Initially consider $f(x)=2x^2+20x+54$ for all real $x$.',[
 p('a',r'State the range of $f$.',A(r'The vertex is$(-5,4)$and the range is$[4,\infty)$.')),
 p('b',r'The domain is now restricted to $x\le k$. Explain why a restriction is needed for an inverse function, and find the largest possible value of $k$.',R(r'The unrestricted parabola fails the horizontal-line test; the left branch must not extend past its vertex.'),A(r'$k=-5$.')),
 p('c',r'Using this value of $k$, find $f^{-1}(x)$, stating its domain.',M(r'$y=2(x+5)^2+4$.'),A(r'$(x+5)^2=(y-4)/2$.'),A(r'Because$x\le-5$, take$x+5=-\sqrt{(y-4)/2}$.'),A(r'$f^{-1}(x)=-5-\sqrt{(x-4)/2}$, with$x\ge4$.'))],[4],
 [check('vertex',2*25+20*(-5)+54,4),check('inverse composition at22',2*(-8)**2+20*(-8)+54,22)]))
AA=simpson(lambda x:2*x/(1+x**4),0,1);BB=simpson(lambda x:1/(1+x**4),0,1)
Q.append(question(4,'A',r'All trigonometric inverse functions in this question use radians.',[
 p('a',r'Using the substitution $u=x^2$, find $\displaystyle\int\frac{x}{1+x^4}\,dx$.',M(r'$u=x^2$gives$du=2x\,dx$.'),A(r'The integral becomes$\frac12\int(1+u^2)^{-1}du$.'),A(r'This is$\frac12\arctan u+C$.'),A(r'$\frac12\arctan(x^2)+C$.')),
 p('b',r'Evaluate $\displaystyle\int_0^1\frac{x}{1+x^4}\,dx$.',A(r'$\frac12[\arctan(x^2)]_0^1=\pi/8\approx0.393$.')),
 p('c',r'Write $\displaystyle\int_0^1\frac{2x+k}{1+x^4}\,dx$ in the form $A+Bk$, and find numerical values of $A$ and $B$ to four significant figures.',M(r'Split by linearity into the$2x$term and the$k$term.'),M(r'$A=\int_0^1 2x/(1+x^4)dx$and$B=\int_0^1 1/(1+x^4)dx$.'),A(r'$A=\pi/4\approx0.7854$.'),A(r'$B\approx0.8670$.'))],[5],
 [check('A integral',AA,math.pi/4),check('B integral',BB,.866972987339911),check('part b',AA/2,math.pi/8)]))
Q.append(question(5,'A',r'Assume $|x|<2$.',[
 p('a',r'Find the first three terms, in ascending powers of $x$, of $(4+2x)^{-1/2}$.',M(r'Write$(4+2x)^{-1/2}=\frac12(1+x/2)^{-1/2}$.'),A(r'The linear coefficient inside the bracket is$-x/4$.'),A(r'The quadratic coefficient inside the bracket is$3x^2/32$.'),A(r'$(4+2x)^{-1/2}=\frac12-\frac{x}{8}+\frac{3x^2}{64}+\cdots$.')),
 p('b',r'Hence obtain the first three non-zero terms of $\displaystyle\frac{64x}{\sqrt{4+2x}}$.',M(r'Multiply the expansion in part(a)by$64x$.'),A(r'$32x-8x^2+3x^3+\cdots$.'))],[6],
 [check('constant',4**(-.5),.5),check('first derivative coefficient',-.5*2*4**(-1.5),-.125),check('quadratic coefficient',(-.5)*(-1.5)*4*4**(-2.5)/2,3/64)]))
roots=[5+10*k for k in range(100)]
Q.append(question(6,'A',r'Angles are measured in radians. Consider the equation $\cos(\pi x/10)=0$ for $0\le x\le1000$.',[
 p('',r'Find the sum of all solutions in this interval.',A(r'The solutions are$x=5+10k$.',2),A(r'The permitted integers are$k=0,1,\ldots,99$, giving100solutions.'),M(r'Sum the arithmetic progression$5,15,\ldots,995$.'),A(r'$S=100(5+995)/2=50000$.',2))],[7],
 [check('root count',len(roots),100),check('root sum',sum(roots),50000),check('endpoint root cos',math.cos(math.pi*995/10),0,1e-12)]))
def ff(x):
    if x<0:return -1-3*math.exp(-x*x)
    if x<=2:return -4+29*x*x/4-15*x**3/4+x**4/2
    return 2+math.exp(-(x-2)**2)
fgraph=plot([('f',ff,-4.5,4.5)],-5,5,-5,4.5,'A differentiable function f (schematic)',(-4,-2,0,1,2,4),(-4,-1,2,3),tx(594,118,'A (2, 3)',17))
Q.append(question(7,'A',r'The diagram shows a differentiable function $f$. Point $A(2,3)$ is a stationary maximum. Define $g(x)=x^2+1$ and $h(x)=f(x)/g(x)$.',[
 p('',r'Find an exact equation of the normal to the graph of $h$ at $x=2$.',A(r'$h(2)=f(2)/g(2)=3/5$.'),M(r'$h\prime=(f\prime g-fg\prime)/g^2$.'),A(r'$g\prime(2)=4$and$f\prime(2)=0$.'),A(r'$h\prime(2)=(0-3\cdot4)/25=-12/25$.'),M(r'The normal gradient is$25/12$.'),A(r'$y-3/5=(25/12)(x-2)$.'))],[8],
 [check('f atA',ff(2),3),check('h value',3/5,.6),check('quotient slope',-3*4/25,-12/25),check('normal perpendicular product',(-12/25)*(25/12),-1)],fgraph))
pyramid=svg(tx(450,30,'Square-based pyramid; lengths shown in metres',21)+ln(120,400,650,400)+ln(650,400,780,280)+ln(780,280,250,280)+ln(250,280,120,400)+ln(450,80,120,400)+ln(450,80,650,400)+ln(450,80,780,280)+ln(450,80,250,280)+ln(450,80,450,340,True)+ln(120,400,780,280,True)+tx(105,420,'A')+tx(665,423,'B')+tx(798,282,'C')+tx(238,275,'D')+tx(450,65,'P')+tx(465,362,'Q')+tx(365,430,'6 m')+tx(400,210,'3√2 m'),'Pyramid geometry and ant paths')
Q.append(question(8,'A',r'$ABCD$ is a square of side $6$ metres and $Q$ is its centre. Point $P$ is vertically above $Q$, with $PQ=3\sqrt2$ metres. Two ants start at $P$ simultaneously: one moves along $PA$ at $1.5\,\mathrm{cm\,s^{-1}}$, and the other along $PB$ at $2\,\mathrm{cm\,s^{-1}}$. Their speeds remain constant.',[
 p('a',r'Show that triangle $PAB$ is equilateral.',M(r'$AC=\sqrt{6^2+6^2}=6\sqrt2$, so$AQ=BQ=3\sqrt2$metres.'),A(r'$PA=\sqrt{(3\sqrt2)^2+(3\sqrt2)^2}=6$metres.'),A(r'Similarly$PB=6=AB$, so the triangle is equilateral.')),
 p('b',r'Find the rate at which the distance between the ants is increasing after $40$ seconds. Work in centimetres and seconds.',A(r'Let their travelled distances be$x,y$and separation$z$; $z^2=x^2+y^2-xy$because the included angle is$60^\circ$.'),M(r'Differentiate with respect to$t$.'),A(r'$2z\dot z=2x\dot x+2y\dot y-x\dot y-y\dot x$.'),A(r'At$t=40$, $x=60$, $y=80$and$z=20\sqrt{13}$cm.'),A(r'$\dot z=\sqrt{13}/2\,\mathrm{cm\,s^{-1}}\approx1.80\,\mathrm{cm\,s^{-1}}$.'))],[9],
 [check('slant edge metres',math.hypot(3*math.sqrt(2),3*math.sqrt(2)),6),check('separation cm',math.sqrt(60**2+80**2-60*80),20*math.sqrt(13)),check('separation rate',(2*60*1.5+2*80*2-60*2-80*1.5)/(40*math.sqrt(13)),math.sqrt(13)/2),yes('ants remain on6m edges after40s',80<600)],pyramid))
Q.append(question(9,'B',r'Three planes are defined by $\Pi_1:x-y+6z=1$, $\Pi_2:2x+y=5$, and $\Pi_3:3x+y+az=b$, where $a,b$ are real constants. Let $L=\Pi_1\cap\Pi_2$.',[
 p('a',r'Find the acute angle between $\Pi_1$ and $\Pi_2$, in degrees.',M(r'Use the normals$(1,-1,6)$and$(2,1,0)$.'),A(r'$\cos\theta=1/(\sqrt{38}\sqrt5)$.'),A(r'$\theta\approx85.8^\circ$.')),
 p('b',r'Find the acute angle between the positive $x$-axis and $\Pi_1$, in degrees.',M(r'For a line-plane angle use$\sin\theta=|\mathbf d\cdot\mathbf n|/(|\mathbf d||\mathbf n|)$with$\mathbf d=(1,0,0)$.'),A(r'$\sin\theta=1/\sqrt{38}$.'),A(r'$\theta\approx9.34^\circ$.')),
 p('c',r'Find a vector equation of $L$.',A(r'At$z=0$, $x=2,y=1$.'),A(r'$\mathbf r=(2,1,0)+\lambda(-2,4,1)$, $\lambda\in\mathbb R$.')),
 p('d',r'When $a=4$ and $b=14$, find the common point of all three planes.',A(r'The point is$(-5,15,3.5)$.')),
 p('e(i)',r'Use row operations or equivalent algebra to find $a$ and $b$ for which the three planes share infinitely many points.',M(r'Eliminate$x$from the second and third equations using the first.'),A(r'The equations reduce to$y-4z=1$and$4y+(a-18)z=b-3$.'),A(r'Hence$(a-2)z=b-7$.'),A(r'Infinitely many common points require$a=2,b=7$.')),
 p('e(ii)',r'For these values, state the set of common points.',A(r'It is$L:\mathbf r=(2,1,0)+\lambda(-2,4,1)$.')),
 p('f(i)',r'Find the conditions on $a,b$ for which there is no common point.',A(r'$a=2$.'),A(r'$b\ne7$.')),
 p('f(ii)',r'Under the conditions in part(f)(i), justify that $L$ is parallel to $\Pi_3$.',M(r'$(-2,4,1)\cdot(3,1,2)=-6+4+2=0$.'),A(r'The direction of$L$is perpendicular to the normal of$\Pi_3$; inconsistency shows$L$is not contained in$\Pi_3$, hence it is parallel and disjoint.'))],[10],
 [check('angle planes',math.degrees(math.acos(1/math.sqrt(190))),85.83967240612728,1e-7),check('line plane angle',math.degrees(math.asin(1/math.sqrt(38))),9.335859032003938,1e-7),check('point plane1',-5-15+6*3.5,1),check('point plane2',2*(-5)+15,5),check('point plane3',3*(-5)+15+4*3.5,14),check('direction plane1',-2-4+6,0),check('direction plane2',-4+4,0)]))
ERRATA.append({'paper':CURRENT,'pdfPage':10,'question':9,'issue':'Part(b) states9.36degrees althoughasin(1/sqrt38)=9.3358590...','correction':r'$\theta=\arcsin(1/\sqrt{38})\approx9.34^\circ$ to three significant figures.'})
N=NormalDist();under=N.cdf((480-500)/18);sig=26/N.inv_cdf(.75)
Q.append(question(10,'B',r'The mass $R$ of a standard packet, in grams, is normally distributed with mean $500$ and standard deviation $18$. Packet masses are independent.',[
 p('a',r'Find $P(R<480)$.',A(r'$P(R<480)=0.13326026\ldots\approx0.133$.')),
 p('b',r'Find $P(R<500\mid R>480)$.',M(r'$P(480<R<500)/P(R>480)$.'),A(r'$(0.5-0.13326026\ldots)/(1-0.13326026\ldots)\approx0.423$.')),
 p('c',r'Find $c$ such that $P(R>c)=0.15$.',M(r'Use the0.85quantile of$N(500,18^2)$.'),A(r'$c=518.6558\ldots\approx519$grams.')),
 p('d',r'Five standard packets are selected independently. Find the probability that exactly one has mass below $480$ grams.',M(r'Let$B$be the number below480g.'),A(r'$B\sim\operatorname{Bin}(5,0.13326026\ldots)$.'),A(r'$P(B=1)=5p(1-p)^4\approx0.376$.')),
 p('e(i)',r'The mass $C$ of a premium packet is also normal. Its lower quartile is $724$ grams and its interquartile range is $52$ grams. Find its mean.',M(r'The upper quartile is$776$and the normal distribution is symmetric.'),A(r'$\mu_C=(724+776)/2=750$grams.')),
 p('e(ii)',r'Find the standard deviation of $C$.',M(r'$P(C<724)=0.25$.'),M(r'$(724-750)/\sigma=\Phi^{-1}(0.25)=-0.67448975\ldots$.'),A(r'$\sigma=38.5477\ldots\approx38.5$grams.')),
 p('f(i)',r'A further normal random variable $X$ has $E(X)=400$ and $\operatorname{Var}(X)=25$. Find $E(X^2)$.',M(r'$\operatorname{Var}(X)=E(X^2)-[E(X)]^2$.'),A(r'$E(X^2)=25+400^2=160025$.')),
 p('f(ii)',r'Let $Y=3X+2$. Find $E(Y)$ and $\operatorname{Var}(Y)$.',M(r'$E(Y)=3E(X)+2$.'),A(r'$E(Y)=1202$.'),A(r'$\operatorname{Var}(Y)=9\operatorname{Var}(X)=225$.')),
 p('f(iii)',r'Let $Z=(X-400)/5$. State $E(Z)$ and $\operatorname{Var}(Z)$.',A(r'$E(Z)=0$.'),A(r'$\operatorname{Var}(Z)=1$.'))],[11],
 [check('under480',under,.1332602629025054),check('conditional',(0.5-under)/(1-under),.4231255605351831,1e-7),check('upper quantile',500+18*N.inv_cdf(.85),518.6558010109,1e-7),check('one packet',5*under*(1-under)**4,.3760326037695815,1e-6),check('premium sigma',sig,38.54765768114565,1e-6),check('EX2',25+400**2,160025),check('variance transform',9*25,225)]))
root=bisect(lambda x:4*math.cos(x)-x*x,1,1.5);h=root*root
area=simpson(lambda x:4*math.cos(x)-x*x,-root,root)
vx=math.pi*simpson(lambda x:16*math.cos(x)**2-x**4,-root,root)
vy=math.pi*(h*h/2+simpson(lambda y:math.acos(min(1,y/4))**2,h,4))
amax=bisect(lambda a:8*math.cos(a)-8*a*math.sin(a)-6*a*a,.1,1.1)
region=plot([('y=4cos x',lambda x:4*math.cos(x),-1.6,1.6),('y=x²',lambda x:x*x,-1.6,1.6)],-1.8,1.8,-.5,4.5,'An enclosed region and an inscribed rectangle',(-1,0,1),(0,2,4),ln(320,365,580,365)+ln(320,365,320,172)+ln(580,365,580,172)+ln(320,172,580,172)+tx(320,410,'−a')+tx(580,410,'a'))
Q.append(question(11,'B',r'The curves $y=4\cos x$ and $y=x^2$ enclose a finite region $R$ around the $y$-axis. Angles are in radians. A rectangle inside $R$ has vertical sides at $x=-a$ and $x=a$, with its upper vertices on $y=4\cos x$ and lower vertices on $y=x^2$. The diagram is schematic.',[
 p('a','Find the coordinates of the two intersections of the curves.',A(r'$(-1.201538\ldots,1.443694\ldots)\approx(-1.20,1.44)$.'),A(r'$(1.201538\ldots,1.443694\ldots)\approx(1.20,1.44)$.')),
 p('b',r'Find the area of $R$.',M(r'Integrate upper minus lower between the intersections.'),A(r'$\int_{-\alpha}^{\alpha}(4\cos x-x^2)dx$, where$\alpha$comes from part(a).'),A(r'Area$\approx6.30$.')),
 p('c',r'Find the volume generated when $R$ is rotated through $2\pi$ about the $x$-axis.',M(r'Use washers with outer radius$4\cos x$and inner radius$x^2$.'),A(r'$V_x=\pi\int_{-\alpha}^{\alpha}(16\cos^2x-x^4)dx$.'),A(r'$V_x\approx74.2$.')),
 p('d',r'Find the volume generated when $R$ is rotated through $2\pi$ about the $y$-axis.',A(r'The bounding squared radius is$y$below$\beta=\alpha^2$and$[\arccos(y/4)]^2$above it.'),M(r'Split the disk integral at$y=\beta$.'),A(r'$V_y=\pi\int_0^\beta y\,dy+\pi\int_\beta^4[\arccos(y/4)]^2dy$.'),A(r'$V_y\approx8.83$.')),
 p('e',r'Show that the area of the rectangle is $A(a)=8a\cos a-2a^3$, and state the physically relevant interval for $a$.',A(r'The base is$2a$and height$4\cos a-a^2$.'),A(r'$A=2a(4\cos a-a^2)=8a\cos a-2a^3$; a nondegenerate rectangle has$0<a<\alpha$.')),
 p('f(i)',r'Show that the value of $a$ for the maximum area satisfies $\displaystyle\frac{\cos a-a\sin a}{a^2}=\frac34$.',M(r'$A\prime(a)=8\cos a-8a\sin a-6a^2=0$.'),A(r'Rearrange to$8(\cos a-a\sin a)=6a^2$, then divide by$8a^2$.')),
 p('f(ii)',r'Find the maximum area of the rectangle.',M(r'Solve the stationary equation in the physical interval and check against the zero-area boundary cases.'),A(r'The maximum area is approximately$3.60$.'))],[12],
 [check('intersection equation residual',4*math.cos(root)-root**2,0),check('intersection x',root,1.201538,1e-6),check('enclosed area (source3sf)',area,6.30,8e-4),check('x rotation',vx,74.2,1e-3),check('y rotation',vy,8.83,1e-3),check('stationarity',8*math.cos(amax)-8*amax*math.sin(amax)-6*amax**2,0),check('max area',8*amax*math.cos(amax)-2*amax**3,3.60,1e-3)],region))
ERRATA.append({'paper':CURRENT,'pdfPage':12,'question':11,'issue':'Two derivative lines use-3a² instead of-6a²; final3/4condition remains correct.','correction':r'$A\prime(a)=8\cos a-8a\sin a-6a^2$ and $8\cos a-8a\sin a=6a^2$.'})
paper(2,Q)

CURRENT='aa-hl-set-b-paper-3';Q=[]
improper=plot([('y=1/x',lambda x:1/x,1,6),('y=1/x²',lambda x:1/(x*x),1,6)],0,6.5,0,1.2,'Comparing positive areas under two curves',(1,2,4,6),(.5,1))
Q.append(question(1,'',r'This question investigates convergence of improper integrals. Unless another restriction is given, $n>1$ and all logarithms are natural. An improper integral is interpreted as a limit of finite integrals, not by substituting infinity into an antiderivative.',[
 p('a(i)',r'Use your calculator to evaluate $\displaystyle\int_1^{100}\frac{dx}{x}$ and $\displaystyle\int_1^{1000}\frac{dx}{x}$ to three significant figures.',A(r'The values are$\ln100\approx4.61$and$\ln1000\approx6.91$.')),
 p('a(ii)',r'Evaluate $\displaystyle\int_1^{100}x^{-2}\,dx$ and $\displaystyle\int_1^{1000}x^{-2}\,dx$.',A(r'The values are$0.990$and$0.999$.')),
 p('b(i)',r'Show that $\displaystyle\int_1^n x^{-3}\,dx=\frac{n^2-1}{2n^2}$.',A(r'The antiderivative is$-1/(2x^2)$.'),A(r'The definite integral is$1/2-1/(2n^2)=(n^2-1)/(2n^2)$.')),
 p('b(ii)',r'Hence evaluate $\displaystyle\int_1^\infty x^{-3}\,dx$, explaining the limiting step.',A(r'$1/(2n^2)\to0$as$n\to\infty$.'),A(r'The improper integral converges to$1/2$.')),
 p('c(i)',r'Find $\displaystyle\int_1^n x^{-1/2}\,dx$ in terms of $n$.',M(r'Use the power rule with exponent$-1/2$.'),A(r'The antiderivative is$2\sqrt{x}$.'),A(r'The value is$2\sqrt n-2$.')),
 p('c(ii)',r'Determine whether $\displaystyle\int_1^\infty x^{-1/2}\,dx$ converges.',A(r'$2\sqrt n-2\to+\infty$, so the integral diverges.')),
 p('d(i)',r'For a real parameter $p\ne0$, find $\displaystyle\int_1^n x^{-(p+1)}\,dx$.',M(r'Integrate$x^{-p-1}$using the power rule.'),A(r'The antiderivative is$-x^{-p}/p$.'),A(r'The definite integral is$(1-n^{-p})/p$.')),
 p('d(ii)',r'For $p>0$, find $\displaystyle\int_1^\infty x^{-(p+1)}\,dx$ and justify convergence.',M(r'$n^{-p}\to0$for$p>0$.'),A(r'The value is$1/p$.')),
 p('d(iii)',r'State what happens to this improper integral when $p<0$.',A(r'For$p<0$, $(1-n^{-p})/p\to+\infty$, so it diverges.')),
 p('d(iv)',r'Evaluate $\displaystyle\int_1^\infty x^{-2025}\,dx$.',A(r'$p=2024$, so the result is$1/2024$.')),
 p('e(i)',r'For $x>1$, differentiate $y=\ln(\ln x)$.',A(r'$dy/dx=1/(x\ln x)$.')),
 p('e(ii)',r'For $n>2$, evaluate $\displaystyle\int_2^n\frac{dx}{x\ln x}$.',M(r'Use$\ln(\ln x)$as an antiderivative.'),A(r'The result is$\ln(\ln n)-\ln(\ln2)$.')),
 p('e(iii)',r'Determine whether $\displaystyle\int_2^\infty\frac{dx}{x\ln x}$ converges.',A(r'$\ln(\ln n)\to+\infty$, so the integral diverges.')),
 p('f(i)',r'For $x>1$ and $p\ne0$, use $u=\ln x$ to find $\displaystyle\int\frac{dx}{x(\ln x)^{p+1}}$.',M(r'$u=\ln x$gives$du=dx/x$.'),A(r'The integral becomes$\int u^{-p-1}du=-u^{-p}/p+C$.'),A(r'The result is$-1/[p(\ln x)^p]+C$.')),
 p('f(ii)',r'For $n>2$, evaluate $\displaystyle\int_2^n\frac{dx}{x(\ln x)^{p+1}}$.',A(r'$1/[p(\ln2)^p]-1/[p(\ln n)^p]$.')),
 p('f(iii)',r'For $p>0$, evaluate the corresponding improper integral from $2$ to infinity.',A(r'The term$(\ln n)^{-p}$tends to zero, giving$1/[p(\ln2)^p]$.')),
 p('f(iv)',r'State what happens when $p<0$.',A(r'The integral diverges to$+\infty$.')),
 p('g(i)',r'For $p>0$, find $\displaystyle\int e^{-px}\,dx$.',A(r'$-e^{-px}/p+C$.')),
 p('g(ii)',r'Evaluate $\displaystyle\int_0^n e^{-px}\,dx$.',A(r'$(1-e^{-pn})/p$.')),
 p('g(iii)',r'Hence evaluate $\displaystyle\int_0^\infty e^{-px}\,dx$.',A(r'$e^{-pn}\to0$and the integral equals$1/p$.'))],[2,3],
 [check('ln100',math.log(100),4.605170185988092),check('ln1000',math.log(1000),6.907755278982137),check('inverse square100',1-1/100,.99),check('inverse square1000',1-1/1000,.999),check('cube finite n4',simpson(lambda x:x**-3,1,4),15/32),check('sqrt finite n9',simpson(lambda x:x**-.5,1,9),4),check('general p3 n4',simpson(lambda x:x**-4,1,4),(1-4**-3)/3),check('log denominator finite',simpson(lambda x:1/(x*math.log(x)),2,5),math.log(math.log(5))-math.log(math.log(2))),check('log power p2 finite',simpson(lambda x:1/(x*math.log(x)**3),2,5),1/(2*math.log(2)**2)-1/(2*math.log(5)**2)),check('exponential finite p2',simpson(lambda x:math.exp(-2*x),0,5),(1-math.exp(-10))/2)],improper))
Q.append(question(2,'',r'A fair six-sided die has its faces labelled $1,2,3,5,6,m$, where the mean of the six labels is $3.5$. In the first game, players $P_1$ and $P_2$ take turns, starting with $P_1$. A player wins immediately on rolling the face labelled $m$; otherwise the next player rolls. All throws are independent. Unless a different game is specified, play continues until someone wins.',[
 p('a',r'Find $m$.',A(r'$m=6(3.5)-(1+2+3+5+6)=4$.')),
 p('b(i)',r'In the first game, find the probability $r$ that both players fail in one complete round.',A(r'$r=(5/6)^2=25/36$.')),
 p('b(ii)',r'Find each player\'s probability of eventually winning.',M(r'For$P_1$, sum$(1/6)[1+r+r^2+\cdots]$.'),A(r'$P(P_1\text{ wins})=(1/6)/(1-25/36)=6/11$.'),A(r'$P(P_2\text{ wins})=5/11$.')),
 p('c(i)',r'A third player $P_3$ joins and turns proceed $P_1,P_2,P_3,P_1,\ldots$, with the same winning rule. Find the probability that $P_1$ wins on their second turn.',A(r'The first three throws must fail, then$P_1$succeeds:$(5/6)^3(1/6)$.')),
 p('c(ii)',r'Find the probability that $P_1$ eventually wins in the three-player game.',M(r'First-turn success is$1/6$.'),A(r'The round-failure ratio is$(5/6)^3$.'),M(r'Sum the geometric series.'),A(r'$P(P_1\text{ wins})=(1/6)/(1-125/216)=36/91$.')),
 p('d',r'Generalize the probability that $P_1$ eventually wins to $n$ players taking turns with the same die rule.',A(r'$\displaystyle\frac{1/6}{1-(5/6)^n}$.')),
 p('e',r'A different two-player game gives $P_1$ a success probability $1/3$ on each of their turns and $P_2$ a success probability $1/2$ on each of theirs. Turns still alternate, with $P_1$ first. Find the probabilities that $P_1$ wins on their first, second and third turns, and show that the game is fair.',M(r'First-turn success is$1/3$.'),A(r'Second-turn success is$(2/3)(1/2)(1/3)=1/9$.'),M(r'The complete-round failure ratio is$(2/3)(1/2)=1/3$.'),A(r'Third-turn success is$1/27$and the series has first term$1/3$, ratio$1/3$.'),A(r'The eventual probability is$(1/3)/(1-1/3)=1/2$.'),A(r'Play terminates almost surely, so$P_2$also wins with probability$1/2$; the game is fair.')),
 p('f',r'In a three-player game the success probabilities on each turn are $1/x$, $1/(x-1)$ and $1/(x-2)$, respectively, with $x>3$. Find $P_1$\'s probability of eventually winning.',M(r'The first-turn success probability is$1/x$.'),A(r'The three failure probabilities are$(x-1)/x$, $(x-2)/(x-1)$and$(x-3)/(x-2)$.'),M(r'Multiply to find the round-failure ratio.'),A(r'The product telescopes to$(x-3)/x=1-3/x$.'),A(r'The sum is$(1/x)/[1-(1-3/x)]=1/3$.')),
 p('g',r'Now let $n$ players have success probabilities $p_i=1/(x-i+1)$ for $i=1,\ldots,n$. Assuming every $p_i$ lies strictly between $0$ and $1$, prove by contradiction that $p_1<1/n$.',M(r'Assume$p_1=1/x\ge1/n$. Since$x>0$, this implies$x\le n$.'),A(r'Then$0<x-n+1\le1$, where positivity follows from$p_n>0$.'),A(r'Hence$p_n=1/(x-n+1)\ge1$, contradicting$p_n<1$. Thus$p_1<1/n$.'))],[4,5],
 [check('die missing face',6*3.5-17,4),check('round ratio',(5/6)**2,25/36),check('P1 two players',(1/6)/(1-(5/6)**2),6/11),check('P2 two players',(5/6)*(1/6)/(1-(5/6)**2),5/11),check('second turn three players',(5/6)**3/6,125/1296),check('eventual threeplayers',(1/6)/(1-(5/6)**3),36/91),check('fair altered first',(1/3)/(1-1/3),.5),check('telescoping atx7',(6/7)*(5/6)*(4/5),4/7),check('eventual x7',(1/7)/(1-4/7),1/3)]))
paper(3,Q)

def emit():
    OUT.mkdir(parents=True,exist_ok=True);DOC.mkdir(parents=True,exist_ok=True)
    for paper_ in PAPERS:
        assert all(q['marks']>0 and q['parts'] for q in paper_['questions'])
        for q in paper_['questions']:
            assert len({p['label'] for p in q['parts']})==len(q['parts'])
            for part,group in zip(q['parts'],q['markScheme'],strict=True):
                assert part['label']==group['part'] and part['marks']==sum(int(s['code'][1:]) for s in group['steps'])
            if 'diagramSvg' in q:assert not re.search(r'<(?:script|style|foreignObject|image)\b|(?:href|src)=',q['diagramSvg'],re.I)
        (OUT/(paper_['id']+'.json')).write_text(json.dumps(paper_,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    report={'status':'passed','papers':3,'questions':sum(len(p['questions']) for p in PAPERS),'marks':sum(p['marks'] for p in PAPERS),'executableChecks':sum(len(r['checks']) for r in RECORDS),
        'reconstructionPolicy':'Complete questions reconstructed to match supplied solutions. Missing raw givens are made explicit and compatible, not claimed to be uniquely recovered source wording.',
        'sourceErrata':ERRATA,'records':RECORDS,
        'paperHashes':{p['id']:hashlib.sha256((OUT/(p['id']+'.json')).read_bytes()).hexdigest() for p in PAPERS}}
    (DOC/'hl-b-author-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:report[k] for k in ['status','papers','questions','marks','executableChecks']}))
if __name__=='__main__':emit()
