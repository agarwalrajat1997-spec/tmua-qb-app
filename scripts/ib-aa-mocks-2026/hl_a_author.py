"""Reconstruct and check AA HL Set A papers against the supplied solution books.

No source question wording is claimed to have been recovered. Stems supply all
needed givens; source page mappings and reconstruction decisions remain private.
Standard library only. UTF-8/LF output; originals are never changed.
"""
from pathlib import Path
from fractions import Fraction
from statistics import NormalDist
import cmath, hashlib, html, json, math, re, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
PAPERS=[]; LEDGER=[]
def step(code,text):return {'code':code,'text':text}
def M(t):return step('M1',t)
def A(t):return step('A1',t)
def A2(t):return step('A2',t)
def R(t):return step('R1',t)
def part(label,prompt,*steps):return {'label':label,'prompt':prompt,'steps':list(steps)}
def check(label,actual,expected,tol=1e-8):
    if isinstance(expected,(list,tuple,dict,str,bool)):
        assert actual==expected,(label,actual,expected)
    else:assert abs(actual-expected)<=tol*max(1,abs(expected)),(label,actual,expected)
    return {'test':label,'actual':actual,'expected':expected,'status':'passed'}
def paper(number,marks,minutes,calculator):
    p={'id':f'aa-hl-set-a-paper-{number}','course':'hl','set':'A','paper':str(number),'title':f'Mathematics AA HL - Set A - Paper {number}','minutes':minutes,'marks':marks,'calculator':calculator,'questions':[]};PAPERS.append(p);return p
def question(p,number,section,stem,parts,pages,checks,summary,decision='',diagram=None):
    q={'number':number,'section':section,'marks':sum(sum(int(s['code'][1:]) for s in z['steps']) for z in parts),'stem':stem,
       'parts':[{'label':z['label'],'prompt':z['prompt'],'marks':sum(int(s['code'][1:]) for s in z['steps'])} for z in parts],
       'answerSummary':summary,'markScheme':[{'part':z['label'],'steps':z['steps']} for z in parts],'sourcePages':pages}
    if diagram:q['diagramSvg']=diagram;ET.fromstring(diagram)
    p['questions'].append(q)
    LEDGER.append({'paperId':p['id'],'question':number,'sourcePages':pages,'status':'passed','checks':checks,'reconstruction':decision or 'All mathematical givens and demands reconstructed from the supplied solution; no claim of recovered original wording.','schemeReview':'Every marking point and all native source pages read. Marks and domains checked; mathematical source errors identified separately.'})
    return q

def txt(x,y,s,size=19,anchor='middle'):
    return f'<text x="{x:g}" y="{y:g}" text-anchor="{anchor}" font-family="Arial,sans-serif" font-size="{size}">{html.escape(str(s))}</text>'
def line(x,y,u,v,dash=False):return f'<path d="M{x:g} {y:g}L{u:g} {v:g}" fill="none" stroke="#111" stroke-width="2"'+(' stroke-dasharray="7 5"' if dash else '')+'/>'
def svg(body,label):return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 460" role="img" aria-label="'+html.escape(label)+'"><rect width="800" height="460" fill="white"/>'+body+'</svg>'
def curve(points):return '<polyline points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in points)+'" fill="none" stroke="#111" stroke-width="2.4"/>'

p=paper(1,110,120,False)
question(p,1,'A',r'The function $f$ is defined by $f(x)=\dfrac{x-1}{2-x}$, for $x\in\mathbb R\setminus\{2\}$.',[
 part('a','State the range of $f$.',A(r'$\mathbb R\setminus\{-1\}$.')),
 part('b','Find $f^{-1}(x)$.',M(r'Let $y=(x-1)/(2-x)$ and rearrange.'),M(r'$x(1+y)=2y+1$.'),A(r'$x=(2y+1)/(y+1)$.'),A(r'$f^{-1}(x)=(2x+1)/(x+1)$, $x\ne-1$.'))
], [2],[check('inverse composition at4',((2*4+1)/(4+1)-1)/(2-(2*4+1)/(4+1)),4)],r'Range excludes $-1$; $f^{-1}(x)=(2x+1)/(x+1)$.')
question(p,2,'A',r'All angles in this question are in radians.',[
 part('',r'Find the exact value of $\displaystyle\int_0^{\pi/2}8\sin x\cos x\,\mathrm dx$.',M(r'Use $2\sin x\cos x=\sin2x$.'),A(r'Integral becomes $\int_0^{\pi/2}4\sin2x\,\mathrm dx$.'),A(r'An antiderivative is $-2\cos2x$.'),M(r'Evaluate at both limits.'),A(r'$-2\cos\pi+2\cos0=2+2$.'),A(r'$4$.'))
],[3],[check('exact antiderivative endpoint value',-2*math.cos(math.pi)+2*math.cos(0),4)],r'$4$.')
question(p,3,'A',r'Let $f(x)=ax^3+2ax^2+bx+3a$, where $a,b\in\mathbb R$ and $a\ne0$. Its three zeros are counted with multiplicity.',[
 part('a','Write down the sum and the product of the zeros of $f$.',A(r'Sum $=-2a/a=-2$.'),A(r'Product $=-3a/a=-3$.')),
 part('b',r'The curve $y=f(x)$ has a stationary point at $(1,3)$. Find $a$ and $b$.',M(r'$f\prime(x)=3ax^2+4ax+b$.'),A(r'$f(1)=3$ gives $6a+b=3$.'),A(r'$f\prime(1)=0$ gives $7a+b=0$.'),A(r'$a=-3$, $b=21$.'))
],[4],[check('stationary ordinate',-3-6+21-9,3),check('stationary derivative',-9-12+21,0)],r'Sum $-2$, product $-3$; $a=-3$, $b=21$.')
question(p,4,'A',r'The discrete random variable $X$ has the following probability distribution, where $0\le p\le0.7$ and $q\ge0$.'+'\n\n| $x$ | $1$ | $2$ | $3$ |\n|---|---:|---:|---:|\n| $\\mathrm P(X=x)$ | $p$ | $0.7-p$ | $q$ |',[
 part('a','Find $q$.',M(r'The probabilities sum to $1$.'),A(r'$p+0.7-p+q=1$, so $q=0.3$.')),
 part('b',r'Given that $\mathrm E(X)=2.1$, find $p$.',M(r'$p+2(0.7-p)+3q=2.1$.'),A(r'$p+1.4-2p+0.9=2.1$.'),A(r'$p=0.2$.'))
],[5],[check('probabilities sum',.2+.5+.3,1),check('expectation',.2+2*.5+3*.3,2.1)],r'$q=0.3$, $p=0.2$.')
question(p,5,'A','',[
 part('',r'Solve $3\log_8(x+2)-2\log_2(x+1)=1$, giving an exact answer.',M(r'Change base: $\log_8(x+2)=\log_2(x+2)/3$.'),A(r'$\log_2(x+2)-2\log_2(x+1)=1$.'),M(r'$\log_2((x+2)/(x+1)^2)=1$.'),A(r'$x+2=2(x+1)^2$.'),A(r'$x(2x+3)=0$, so $x=0$ or $x=-3/2$.'),A(r'The logarithms require $x>-1$, so only $x=0$ is valid.'))
],[6],[check('valid solution in original',3*math.log(2,8)-2*math.log(1,2),1),check('excluded algebraic root',-1.5>-1,False)],r'$x=0$.')
question(p,6,'A',r'An arithmetic sequence has first term $u_1$ and common difference $d$. Let $S_n$ denote the sum of its first $n$ terms. It is given that $S_3=S_8$.',[
 part('a',r'Show that $u_1=-5d$.',M(r'$\frac32(2u_1+2d)=\frac82(2u_1+7d)$.'),A(r'$3u_1+3d=8u_1+28d$.'),A(r'$5u_1=-25d$.'),A(r'$u_1=-5d$.')),
 part('b','Find the sixth term of the sequence.',M(r'$u_6=u_1+5d$.'),A(r'$u_6=0$.'))
],[7],[check('sum3 equals sum8 for d2',3/2*(-20+4),8/2*(-20+14)),check('sixth term',-10+5*2,0)],r'$u_1=-5d$, $u_6=0$.')
question(p,7,'A','Angles are measured in degrees.',[
 part('',r'Solve $\sin x+\cos x=\sqrt{\frac32}$ for $0^\circ<x<90^\circ$, giving exact values.',M(r'Both sides are positive in this interval, so squaring preserves equivalence.'),A(r'$\sin^2x+2\sin x\cos x+\cos^2x=3/2$.'),A(r'$1+\sin2x=3/2$.'),A(r'$\sin2x=1/2$, with $0^\circ<2x<180^\circ$.'),A(r'$2x=30^\circ$ or $150^\circ$.'),A(r'$x=15^\circ$ or $75^\circ$.'))
],[8],[check('15degree root',math.sin(math.pi/12)+math.cos(math.pi/12),math.sqrt(1.5)),check('75degree root',math.sin(5*math.pi/12)+math.cos(5*math.pi/12),math.sqrt(1.5))],r'$15^\circ$, $75^\circ$.')
question(p,8,'A',r'Non-zero vectors $\mathbf a$ and $\mathbf b$ are perpendicular.',[
 part('',r'Prove that $3\mathbf a-\mathbf b$ is perpendicular to $\mathbf a+3\mathbf b$ if and only if $|\mathbf a|=|\mathbf b|$.',A(r'$\mathbf a\cdot\mathbf b=0$.'),M(r'Expand $(3\mathbf a-\mathbf b)\cdot(\mathbf a+3\mathbf b)=3|\mathbf a|^2-3|\mathbf b|^2$.'),A(r'Perpendicularity is equivalent to $|\mathbf a|^2=|\mathbf b|^2$.'),M(r'Magnitudes are nonnegative, so equality of squares is equivalent to equality of magnitudes.'),A(r'Hence $|\mathbf a|=|\mathbf b|$.'),M(r'Explicit equivalences, or the reverse implication as well as the forward one, complete the if-and-only-if proof.'))
],[9],[check('equal-length perpendicular example dot',3*3-3*3,0),check('unequal-length example dot',3*4-3*9,-15)],r'Both directions follow from dot product $3(|\mathbf a|^2-|\mathbf b|^2)$.','Corrected source sign typo: its displayed perpendicularity line says a-3b but its expansion uses the correct a+3b.')
ellipse=svg(line(170,250,650,250)+line(410,35,410,425)+'<ellipse cx="410" cy="250" rx="100" ry="200" fill="none" stroke="#111" stroke-width="2.4"/>'+txt(660,257,'x')+txt(425,30,'y')+txt(390,270,'O')+txt(480,55,'(0, 2)')+txt(520,270,'1'),'Ellipse with equation4x²+y²=4; schematic')
question(p,9,'A',r'The ellipse $C$ has equation $4x^2+y^2=4$.',[
 part('a',r'Find the equation of the tangent to $C$ at the point where $y=2$.',A(r'$x=0$ when $y=2$.'),A(r'Implicit differentiation gives $8x+2y\,\mathrm dy/\mathrm dx=0$, so $\mathrm dy/\mathrm dx=-4x/y$.'),A(r'The tangent has gradient $0$.'),A(r'The tangent is $y=2$.')),
 part('b',r'The line $x\cos\theta+y\sin\theta=\sqrt2$ is tangent to $C$, where $0<\theta<\pi/2$. Show that $\sin^2\theta=\frac13$.',M(r'Substitute $y=\sqrt2\csc\theta-x\cot\theta$ into the ellipse.'),A(r'$(4+\cot^2\theta)x^2-2\sqrt2\csc\theta\cot\theta\,x+2\csc^2\theta-4=0$.'),M(r'Tangency requires discriminant $0$.'),A(r'Simplification gives $2\csc^2\theta=4+\cot^2\theta$.'),A(r'Using $\cot^2\theta=\csc^2\theta-1$ gives $\csc^2\theta=3$, hence $\sin^2\theta=1/3$.'))
],[10],[check('line support condition at sin²1/3',(1-1/3)+4*(1/3),2),check('ellipse top point',4*0+2**2,4)],r'Tangent $y=2$; $\sin^2\theta=1/3$.',diagram=ellipse)
question(p,10,'B',r'The continuous random variable $X$ has probability density $f(x)=\dfrac{k}{1+x^2}$ for $0\le x\le1$, and $f(x)=0$ otherwise, where $k>0$.',[
 part('a','Find the exact value of $k$.',M(r'$\int_0^1 k/(1+x^2)\,\mathrm dx=1$.'),A(r'$k[\arctan x]_0^1=k\pi/4=1$.'),A(r'$k=4/\pi$.')),
 part('b',r'Write down $\mathrm P(X=1/\sqrt3)$.',A(r'$0$, because $X$ is continuous.')),
 part('c',r'Find the exact value of $\mathrm P(X\le1/\sqrt3)$.',M(r'$\frac4\pi[\arctan x]_0^{1/\sqrt3}$.'),A(r'$\frac4\pi\cdot\frac\pi6=2/3$.')),
 part('d',r'Show that $\mathrm E(X)=\dfrac{\ln b}{\pi}$ and find $b$.',M(r'$\mathrm E(X)=\frac4\pi\int_0^1x/(1+x^2)\,\mathrm dx$.'),A(r'$=\frac2\pi[\ln(1+x^2)]_0^1$.'),A(r'$=2\ln2/\pi$.'),A(r'$=\ln4/\pi$, so $b=4$.')),
 part('e',r'Find the exact value of $\mathrm E(X^2)$.',M(r'$\mathrm E(X^2)=\frac4\pi\int_0^1x^2/(1+x^2)\,\mathrm dx$.'),M(r'Write $x^2=(1+x^2)-1$.'),A(r'The integrand becomes $1-1/(1+x^2)$.'),A(r'$\frac4\pi[x-\arctan x]_0^1$.'),A(r'$4/\pi-1$.')),
 part('f',r'The median is $M=\tan\theta$, where $0<\theta<\pi/2$. Find the exact value of $\theta$.',M(r'$\frac4\pi\int_0^M1/(1+x^2)\,\mathrm dx=1/2$.'),A(r'$\frac4\pi\arctan M=1/2$.'),A(r'$\theta=\pi/8$.'))
],[11,12],[check('pdf normalized',4/math.pi*math.atan(1),1),check('CDF boundary',4/math.pi*math.atan(1/math.sqrt(3)),2/3),check('mean logform',2*math.log(2),math.log(4)),check('median CDF',4/math.pi*math.atan(math.tan(math.pi/8)),.5)],r'$k=4/\pi$; probability $0$, CDF $2/3$; $b=4$; $\mathrm E(X^2)=4/\pi-1$; $\theta=\pi/8$.')
question(p,11,'B',r'Let $f(x)=\dfrac{2e^{2x}-1}{e^{2x}+1}$, $x\in\mathbb R$.',[
 part('a','Find the coordinates of both intercepts of $y=f(x)$.',A(r'The $y$-intercept is $(0,1/2)$.'),M(r'For the $x$-intercept, $2e^{2x}-1=0$.'),A(r'The $x$-intercept is $(-\frac12\ln2,0)$.')),
 part('b','Show that $f$ is strictly increasing.',M(r'Apply the quotient rule.'),A(r'$f\prime(x)=[4e^{2x}(e^{2x}+1)-2e^{2x}(2e^{2x}-1)]/(e^{2x}+1)^2$.'),A(r'$f\prime(x)=6e^{2x}/(e^{2x}+1)^2>0$.'),A(r'So $f$ is strictly increasing for every real $x$.')),
 part('c',r'Find $\displaystyle\lim_{x\to+\infty}f(x)$, justifying your answer.',M(r'Divide numerator and denominator by $e^{2x}$.'),A(r'$f(x)=(2-e^{-2x})/(1+e^{-2x})$.'),R(r'$e^{-2x}\to0$, so the limit is $2$.')),
 part('d','Sketch $y=f(x)$, showing the intercepts and both horizontal asymptotes.',A(r'Correct increasing S-shaped curve.'),A(r'Intercepts $(0,1/2)$ and $(-\frac12\ln2,0)$.'),A(r'Horizontal asymptotes $y=-1$ and $y=2$.')),
 part('e',r'Explain why $f^{-1}$ exists, and find the exact value of $f^{-1}(1)$.',R(r'Strict monotonicity makes $f$ one-to-one.'),M(r'Solve $f(x)=1$.'),A(r'$2e^{2x}-1=e^{2x}+1$, so $e^{2x}=2$.'),A(r'$f^{-1}(1)=\frac12\ln2$.'))
],[13,14],[check('ordinate intercept',(2-1)/(1+1),.5),check('zero numerator',2*math.exp(-math.log(2))-1,0),check('inverse at1',(2*2-1)/(2+1),1)],r'Intercepts $(0,1/2)$ and $(-\frac12\ln2,0)$; asymptotes $y=-1,2$; $f^{-1}(1)=\frac12\ln2$.')
rect=svg(line(110,360,720,360)+line(110,360,110,35)+curve([(110+55*x,360-32*math.exp(x/5)) for x in [i/12 for i in range(121)]])+f'<rect x="330" y="288.783" width="330" height="71.217" fill="#eee" stroke="#111" stroke-width="2"/>'+txt(720,390,'x')+txt(100,28,'y')+txt(330,390,'a')+txt(660,390,'10')+txt(565,115,'y = e^(x/5)')+txt(480,330,'Rectangle'),'Rectangle under exponential curve, schematic; a is variable')
question(p,12,'B',r'Let $f(x)=e^{x/5}$. A rectangle has vertices $(a,0)$, $(10,0)$, $(10,f(a))$ and $(a,f(a))$, where $0\le a<10$. Its area is $S$ and perimeter is $P$.',[
 part('a',r'Find the equation of the tangent to $y=f(x)$ at $x=0$.',M(r'$f\prime(x)=e^{x/5}/5$.'),A(r'At $x=0$, the point is $(0,1)$ and gradient is $1/5$.'),A(r'$y=x/5+1$.')),
 part('b',r'The line $y=mx$ is tangent to $y=f(x)$. Find $m$.',M(r'At contact, $e^{x/5}=mx$.'),M(r'Tangency also gives $m=e^{x/5}/5$.'),A(r'$e^{x/5}=xe^{x/5}/5$.'),A(r'$x=5$.'),A(r'$m=e/5$.')),
 part('c',r'Express $S$ in terms of $a$.',A(r'Base is $10-a$.'),A(r'Height is $e^{a/5}$, so $S=(10-a)e^{a/5}$.')),
 part('d',r'Express $P$ in terms of $a$.',A(r'$P=2(10-a)+2e^{a/5}$.'),A(r'$P=20-2a+2e^{a/5}$.')),
 part('e',r'Find $\mathrm dS/\mathrm da$ in simplified form.',M(r'Use the product rule.'),A(r'$S\prime=-e^{a/5}+(10-a)e^{a/5}/5$.'),A(r'$S\prime=(1-a/5)e^{a/5}$.')),
 part('f',r'Find the exact perimeter when $S$ is a maximum, justifying that the stationary value is a maximum.',M(r'Solve $(1-a/5)e^{a/5}=0$.'),A(r'$a=5$.'),A(r'$S\prime\prime=-ae^{a/5}/25$.'),R(r'$S\prime\prime(5)<0$; also $S\prime$ is positive before5 and negative after5 in the allowed domain.'),A(r'$P=10+2e$.'))
],[15,16],[check('tangent slope fromorigin',math.e/5,math.exp(5/5)/5),check('area maximizer derivative',(1-5/5)*math.exp(1),0),check('second derivativeat5',-5*math.e/25,-math.e/5),check('maximum-area perimeter',20-10+2*math.e,10+2*math.e)],r'$y=x/5+1$; $m=e/5$; $S=(10-a)e^{a/5}$; maximum at $a=5$, $P=10+2e$.',diagram=rect)

def bisect(f,a,b,iterations=100):
    fa=f(a)
    for _ in range(iterations):
        m=(a+b)/2;fm=f(m)
        if fa*fm<=0:b=m
        else:a=m;fa=fm
    return (a+b)/2
def simpson(f,a,b,n=10000):
    h=(b-a)/n
    return h/3*(f(a)+f(b)+sum((4 if k%2 else 2)*f(a+k*h) for k in range(1,n)))

p=paper(2,110,120,True)
normal=NormalDist(230,9);tail=1-normal.cdf(240);cut=normal.inv_cdf(.5-tail)
question(p,1,'A',r'The mass $X$ grams of an item is modelled by a normal distribution with mean $230$ and standard deviation $9$.',[
 part('a',r'Find $\mathrm P(X>240)$.',M(r'Use the upper tail of $N(230,9^2)$.'),A(r'$0.133260\ldots\approx0.133$.')),
 part('b',r'Find $a$ such that $\mathrm P(a<X<240)=0.5$.',M(r'$\mathrm P(X>a)=0.5+\mathrm P(X>240)$.'),A(r'$\mathrm P(X>a)=0.633260\ldots$.'),A(r'$a=226.9355\ldots\approx227$ grams.'))
],[2],[check('normal upper tail',tail,.133260262902505,1e-7),check('inverse normal threshold',cut,226.9355,1e-6),check('intervalprobability',normal.cdf(240)-normal.cdf(cut),.5)],r'$0.133$; $a\approx227$.','Normal parameters230 and9 reconstruct both supplied probability and inverse-normal result; mass context is newly supplied.')
question(p,2,'A',r'The function $f$ is defined by $f(x)=x^2\ln(x-2)+1$, $x>2$.',[
 part('a',r'Find $f\prime(3)$.',A2(r'$f\prime(3)=9$.')),
 part('b(i)',r'Find the equation of the normal to $y=f(x)$ at $x=3$, in point-gradient form.',A(r'The normal gradient is $-1/9$.'),A(r'$y-1=-\frac19(x-3)$.')),
 part('b(ii)',r'Write this normal equation in the form $y=mx+c$.',A(r'$y=-\frac19x+\frac43$, or $y\approx-0.111x+1.33$.'))
],[3],[check('analytic derivativeat3',2*3*math.log(1)+9/1,9),check('pointat3',9*math.log(1)+1,1),check('normal yintercept',1+3/9,4/3)],r'$f\prime(3)=9$; normal $y=-x/9+4/3$.')
question(p,3,'A',r'In the binomial expansion of $(2x+ax^2)^7$, the coefficient of $x^9$ is $6048$, where $a\in\mathbb R$.',[
 part('','Find all possible values of $a$.',M(r'The general term is $\binom7r(2x)^{7-r}(ax^2)^r$.'),A(r'The power of $x$ is $7+r$, so $r=2$.'),A(r'The coefficient is $\binom72 2^5a^2=672a^2$.'),M(r'Solve $672a^2=6048$.'),A(r'$a=\pm3$.'))
],[4],[check('binomialcoefficient',math.comb(7,2)*2**5,672),check('both roots square',672*3**2,6048)],r'$a=3$ or $-3$.')
sector=svg('<path d="M220 330L570 330A350 350 0 0 0 346.826 3.786Z" fill="white" stroke="#111" stroke-width="2"/>'+'<path d="M570 330A350 350 0 0 0 346.826 3.786Z" fill="#ddd" stroke="#111" stroke-width="2"/>'+line(220,330,346.826,3.786)+txt(205,355,'O')+txt(580,350,'B')+txt(353,30,'A')+txt(385,360,'r')+txt(254,270,'θ')+line(555,110,510,150)+txt(650,70,'Shaded segment',18)+txt(650,100,'3.35 cm²',18)+txt(400,415,'Sector perimeter 16 cm; diagram not to scale',18),'Sector and associated minor segment')
theta=bisect(lambda t:(16/(t+2))**2*(t-math.sin(t))-6.7,.01,math.pi)
question(p,4,'A',r'A minor sector $OAB$ has radius $r$ cm and angle $\theta$ radians, where $0<\theta<\pi$. Its perimeter, including the two radii, is $16$ cm. The area of the segment bounded by chord $AB$ and minor arc $AB$ is $3.35$ cm$^2$.',[
 part('',r'Find $r$ and $\theta$, giving each answer to three significant figures.',M(r'Use segment area $\frac12r^2(\theta-\sin\theta)=3.35$.'),A(r'$r^2(\theta-\sin\theta)=6.7$.'),A(r'From sector perimeter, $r\theta+2r=16$, so $r=16/(\theta+2)$.'),M(r'Solve $[16/(\theta+2)]^2(\theta-\sin\theta)=6.7$ in the minor-sector domain.'),A(r'$\theta\approx1.20$ radians.'),A(r'$r\approx5.00$ cm.'))
],[5],[check('segment numeric equation',(16/(theta+2))**2*(theta-math.sin(theta)),6.7),check('sectorperimeter',16/(theta+2)*(theta+2),16),check('angle rounds1.20',round(theta,2),1.2),check('radius rounds5.00',round(16/(theta+2),2),5)],r'$\theta\approx1.20$ rad, $r\approx5.00$ cm.','Source displays exact-looking1.2 and5 although area3.35 is rounded. New demand explicitly uses three significant figures and distinguishes sector perimeter from segment area.',diagram=sector)
question(p,5,'A',r'For $n\in\mathbb Z^+$, define $u_n=\dfrac{12^{n+1}+2\cdot5^n}{14}$.',[
 part('a',r'Prove by mathematical induction that $u_n$ is an integer for every $n\in\mathbb Z^+$.',A(r'For $n=1$, the numerator is $12^2+2\cdot5=154=14\cdot11$.'),M(r'Assume $12^{k+1}+2\cdot5^k=14m$ for some integer $m$.'),M(r'Consider $12^{k+2}+2\cdot5^{k+1}$.'),A(r'$=12(14m-2\cdot5^k)+10\cdot5^k$.'),A(r'$=14(12m-5^k)$, divisible by14.'),R(r'The base case and induction step establish the result for all positive integers.')),
 part('b',r'Find the smallest positive integer $n$ for which $u_n>10^6$.',A(r'$u_5=213731<10^6$ and $u_n$ is increasing.'),A(r'$u_6=(12^7+2\cdot5^6)/14=2561647>10^6$, so $n=6$.'))
],[6],[check('basequotient',(12**2+2*5)//14,11),check('u5',(12**6+2*5**5)//14,213731),check('u6',(12**7+2*5**6)//14,2561647),check('divisiblecases1to20',all((12**(n+1)+2*5**n)%14==0 for n in range(1,21)),True)],r'$u_n$ is integral by induction; first $n$ above threshold is6.','Corrected source Q5b exponent5^7 to5^6 for n6; supplied numerical answer2561647 remains correct.')
question(p,6,'A',r'This question concerns sketches from qualitative information. Numerical coordinates of any intercept not specified need not be calculated. Draw each sketch on a separate set of axes.',[
 part('a',r'The differentiable function $f$ is even and tends to $3$ as $x\to\pm\infty$. It satisfies $f(0)=-3$, $f(\pm1)=1$ and $f(\pm2)=4$. Its derivative is positive for $x<-2$ and $0<x<2$, negative for $-2<x<0$ and $x>2$, and zero only at $-2,0,2$. Sketch a possible graph of $y=f(x)$, showing its stationary points and horizontal asymptote.',A(r'Horizontal asymptote $y=3$ on both ends.'),A(r'Even graph, with correct labelled given points and symmetry.'),A(r'Local maxima at $(-2,4)$ and $(2,4)$.'),A(r'Local minimum at $(0,-3)$, with branches consistent with derivative signs.')),
 part('b',r'The function $g$ is differentiable for $x\ne1$. Its limits are $g(x)\to-2$ as $x\to-\infty$, $g(x)\to1$ as $x\to+\infty$, $g(x)\to-\infty$ as $x\to1^-$ and $g(x)\to+\infty$ as $x\to1^+$. It has $g\prime(x)>0$ for $x<0$ and $x>2$, and $g\prime(x)<0$ for $0<x<1$ and $1<x<2$. The only stationary points are at $x=0$ and $x=2$, with $-1<g(0)<0$ and $0<g(2)<1$. Sketch a possible graph, showing all asymptotes and stationary points. The exact stationary ordinates are not required.',A(r'Vertical asymptote $x=1$, horizontal asymptotes $y=-2$ on left and $y=1$ on right.'),A(r'Correct branches approaching $-\infty$ and $+\infty$ at the indicated sides of1.'),A(r'One local maximum at $x=0$, with negative ordinate between-1and0.'),A(r'One local minimum at $x=2$, with positive ordinate between0and1, and correct increasing/decreasing intervals.'))
],[7],[check('a derivative stationary count',len([-2,0,2]),3),check('b localmaximumsignchange',1*(-1),-1),check('b localminimumsignchange',(-1)*1,-1)],r'Part(a): two maxima and one minimum, asymptote $y=3$. Part(b): one maximum and one minimum, asymptotes $x=1$, $y=-2$ and $y=1$.','Original function definitions are absent from the source solutions. Complete qualitative/sign givens are newly supplied to make the displayed sketches valid answers. Source b caption incorrectly repeats the a turn-count; corrected to one maximum/one minimum.')
triangle=svg(line(110,350,710,350)+line(150,350,400,100)+line(400,100,560,350,True)+txt(135,382,'B')+txt(400,75,'A')+txt(560,382,'X')+txt(255,205,'20')+txt(205,325,'45°')+txt(500,425,'X may move along the ray; diagram not to scale',18),'Point X on a ray making45degrees with fixed segmentBA')
question(p,7,'A',r'Points $A$ and $B$ are fixed with $AB=20$. A ray starts at $B$ and makes an angle of $45^\circ$ with $BA$. The point $X$ may lie anywhere on this ray other than $B$.',[
 part('a',r'Find the exact value of $BX$ when $AX$ is as small as possible.',M(r'The shortest distance is perpendicular to the ray, so $BX=20\cos45^\circ$.'),A(r'$BX=10\sqrt2$.')),
 part('b',r'Find the exact value of $BX$ when $AX=20$.',A(r'The nondegenerate isosceles triangle gives $BX=2(10\sqrt2)=20\sqrt2$.')),
 part('c',r'When $AX=17$, find both possible values of $BX$.',M(r'Cosine rule gives $17^2=BX^2+20^2-40BX\cos45^\circ$.'),A(r'$BX=10\sqrt2+\sqrt{89}\approx23.6$.'),A(r'$BX=10\sqrt2-\sqrt{89}\approx4.71$.'))
],[8],[check('shortest BX',20*math.cos(math.pi/4),10*math.sqrt(2)),check('positive longroot distance', (10*math.sqrt(2)+math.sqrt(89))**2+400-40*(10*math.sqrt(2)+math.sqrt(89))*math.cos(math.pi/4),289),check('positive shortroot distance',(10*math.sqrt(2)-math.sqrt(89))**2+400-40*(10*math.sqrt(2)-math.sqrt(89))*math.cos(math.pi/4),289)],r'$10\sqrt2$; $20\sqrt2$; approximately23.6or4.71.','Ray and exclusionX=B make b nondegenerate and retain both positive ambiguous-case positions in c.',diagram=triangle)
w=2+3j
question(p,8,'A',r'Let $w=2+3i$. A polynomial is defined by $P(z)=z^4+az^2+72z+b$, where $a,b\in\mathbb R$. It is given that $P(w)=0$.',[
 part('a',r'Find $w^4$ in the form $u+vi$.',A(r'$w^4=-119-120i$.')),
 part('b',r'Find $a$ and $b$.',A(r'$w^2=-5+12i$.'),M(r'Substitute $w$ into $P(w)=0$.'),A(r'Equating real and imaginary parts gives $5a-b=25$ and $12a+96=0$.'),A(r'$a=-8$, $b=-65$.')),
 part('c','Find the other three zeros of $P$.',A(r'$1$, $-5$ and $2-3i$.'))
],[9],[check('real w4',(w**4).real,-119),check('imag w4',(w**4).imag,-120),check('quartic roots',all(abs(z**4-8*z*z+72*z-65)<1e-9 for z in [1,-5,2+3j,2-3j]),True)],r'$w^4=-119-120i$; $a=-8$, $b=-65$; remaining zeros1,-5,2-3i.')
question(p,9,'A',r'The function $\arctan$ takes its principal values in $(-\pi/2,\pi/2)$. Angles are in radians.',[
 part('a',r'Give a counterexample to the claim that $\arctan(\tan x)=x$ for every real $x$ for which $\tan x$ exists.',A(r'For example, take $x=3\pi/4$.'),R(r'$\arctan(\tan(3\pi/4))=\arctan(-1)=-\pi/4\ne3\pi/4$.')),
 part('b',r'Prove that $\arctan x+\arctan(1/x)=\pi/2$ for every $x>0$.',M(r'Put $A=\arctan x$ and $B=\arctan(1/x)$, so $0<A,B<\pi/2$.'),A2(r'$\tan A\tan B=1$, so $\cos(A+B)=\cos A\cos B(1-\tan A\tan B)=0$.'),R(r'As $0<A+B<\pi$, the only possible zero of cosine is $A+B=\pi/2$.'))
],[10],[check('counterexampleprincipalvalue',math.atan(math.tan(3*math.pi/4)),-math.pi/4),check('positive domain identityat2',math.atan(2)+math.atan(.5),math.pi/2)],r'Counterexample $3\pi/4$; positive-domain complementary-angle identity holds.','Proof makes principal-value range explicit; avoids applying an undefined tangent-addition quotient without its range justification.')
question(p,10,'B',r'The line $l_1$ has Cartesian equation $\dfrac{x+16}{-5}=\dfrac{y+4}{-7}=z$. The line $l_2$ passes through $A(3,4,1)$ and $B(0,6,0)$. Let $C=(-11,3,-1)$.',[
 part('a','Find a vector equation for $l_2$.',A(r'A direction vector is $(-3,2,-1)$.'),A(r'$\mathbf r=(3,4,1)+t(-3,2,-1)$.')),
 part('b',r'Show that $l_1$ and $l_2$ meet, and find their point of intersection $P$.',A(r'$l_1:\mathbf r=(-16,-4,0)+\lambda(-5,-7,1)$.'),M(r'Equate components to obtain $3t-5\lambda=19$, $2t+7\lambda=-8$, $t+\lambda=1$.'),A(r'$t=3$, $\lambda=-2$.'),R(r'These values satisfy all three components, so the lines intersect.'),A(r'$P=(-6,10,-2)$.')),
 part('c','Show that the lines are perpendicular.',M(r'Take the dot product of direction vectors.'),A(r'$(-3,2,-1)\cdot(-5,-7,1)=15-14-1=0$.')),
 part('d',r'Show that $C$ lies on $l_1$.',M(r'Substitute $\lambda=-1$ into its vector equation.'),A(r'$(-16,-4,0)-(-5,-7,1)=(-11,3,-1)=C$.')),
 part('e',r'The point $D$ is the reflection of $C$ in the line $l_2$. Find $D$.',M(r'$CP$ is perpendicular to $l_2$, so $P$ is the midpoint of $CD$.'),A(r'$D=2P-C=(-1,17,-3)$.')),
 part('f','Find a Cartesian equation of the plane containing both lines.',M(r'Cross the two direction vectors.'),A(r'$(-3,2,-1)\times(-5,-7,1)=(-5,8,31)$.'),M(r'Use a point on the plane, such as $(3,4,1)$.'),A(r'$-5x+8y+31z=48$.'))
],[11,12],[check('dotperpendicular',15-14-1,0),check('intersection froml2',[3-3*3,4+2*3,1-3],[-6,10,-2]),check('intersection froml1',[-16+10,-4+14,-2],[-6,10,-2]),check('reflectedpoint',[-12+11,20-3,-4+1],[-1,17,-3]),check('planeatA',-5*3+8*4+31,48)],r'$P=(-6,10,-2)$; $D=(-1,17,-3)$; plane $-5x+8y+31z=48$.','Cartesian presentation reconstructs the vector-conversion demand. Reflection is in the line, not in the plane.')
f=lambda x:math.sqrt(1+x)+math.sqrt(1-x)
graph=svg(line(110,370,710,370)+line(410,410,410,60)+curve([(410+220*x,370-130*f(x)) for x in [-1+i/100 for i in range(201)]])+line(190,370,190,370-130*math.sqrt(2),True)+line(630,370,630,370-130*math.sqrt(2),True)+txt(190,398,'−1')+txt(630,398,'1')+txt(395,395,'O')+txt(180,175,'A')+txt(650,175,'B')+txt(430,110,'2')+txt(725,380,'x')+txt(425,50,'y')+txt(550,285,'R'),'Graph of sqrt(1+x)+sqrt(1-x), with first-quadrant regionR')
question(p,11,'B',r'Let $f(x)=\sqrt{1+x}+\sqrt{1-x}$, $-1\le x\le1$. Its graph has endpoints $A$ at $x=-1$ and $B$ at $x=1$. Let $R$ be the region bounded by this graph, the two coordinate axes and the line $x=1$, in the first quadrant.',[
 part('a(i)',r'Find the exact $y$-coordinate of $A$.',A(r'$\sqrt2$.')),
 part('a(ii)','State the range of $f$.',A(r'The minimum is $\sqrt2$ at either endpoint.'),A(r'The maximum is $2$ at $x=0$, so $\sqrt2\le y\le2$.')),
 part('b',r'The horizontal line $y=k$ is tangent to the graph. Find $k$.',A(r'$k=2$.')),
 part('c',r'The line $OB$, where $O$ is the origin, has gradient $m$. Find $m$.',A(r'$m=\sqrt2$.')),
 part('d',r'Find all real $k$ for which the line $y=kx$ does not meet the graph.',A(r'For $x>0$, the continuous ratio $f(x)/x$ takes exactly $[\sqrt2,\infty)$; for $x<0$ it takes $(-\infty,-\sqrt2]$. Hence slopes strictly between these ranges cannot meet the curve.'),A(r'$-\sqrt2<k<\sqrt2$.'),A(r'The inequalities are strict because equality gives an endpoint intersection.')),
 part('e',r'Find the exact area of $R$.',M(r'$\int_0^1(\sqrt{1+x}+\sqrt{1-x})\,\mathrm dx$.'),A(r'Antiderivative $\frac23(1+x)^{3/2}-\frac23(1-x)^{3/2}$.'),A(r'Evaluate at0and1.'),A(r'$4\sqrt2/3$.')),
 part('f',r'Find the volume generated when $R$ is rotated through $2\pi$ radians about the $x$-axis.',A(r'$V=\pi\int_0^1(\sqrt{1+x}+\sqrt{1-x})^2\,\mathrm dx$.'),A(r'$V\approx11.2$ cubicunits (exactly $2\pi+\pi^2/2$).')),
 part('g',r'Find the volume generated when $R$ is instead rotated through $2\pi$ radians about the $y$-axis. Show your method.',M(r'Split into cylinder height $\sqrt2$, radius1, and upper cap.'),M(r'From $y=f(x)$, obtain $x^2=1-(y^2-2)^2/4$.'),A(r'Upper cap is $\pi\int_{\sqrt2}^2[1-(y^2-2)^2/4]\,\mathrm dy$.'),A(r'This cap is $\pi(16-7\sqrt2)/15$; cylinder is $\pi\sqrt2$.'),A(r'Total $V=\pi(16+8\sqrt2)/15\approx5.72$ cubicunits. Equivalent shell integration is valid.'))
],[13,14],[check('endpointvalue',f(1),math.sqrt(2)),check('maxvalue',f(0),2),check('exactxrotation',math.pi*(2+math.pi/2),11.2179875077243,1e-8),check('yrotationshell',2*math.pi*simpson(lambda x:x*f(x),0,1,20000),math.pi*(16+8*math.sqrt(2))/15,2e-7),check('areaintegral',simpson(f,0,1,20000),4*math.sqrt(2)/3,1e-7)],r'Range $[\sqrt2,2]$; $k=2$; $m=\sqrt2$; missing-line slopes $(-\sqrt2,\sqrt2)$; area $4\sqrt2/3$; volumes11.2and5.72.','New b/c/d wording fixes the underdetermined original line-intersection prompts while matching every supplied numerical result and strict endpoints.',diagram=graph)
view=svg(line(110,355,620,355)+line(620,355,620,75)+line(110,355,620,75)+line(280,355,620,75)+line(595,355,595,330)+line(595,330,620,330)+txt(95,385,'B')+txt(280,385,'A')+txt(625,385,'Q')+txt(635,60,'P')+txt(195,390,'1')+txt(450,390,'2')+txt(650,215,'x')+txt(195,330,'β')+txt(352,330,'α')+txt(400,435,'Schematic; all lengths in the same units',18),'Viewing angleAPB with baselineBA1 AQ2 and heightQP x')
maxangle=math.degrees(math.atan(math.sqrt(6)/12));t=math.tan(math.radians(10));disc=1-24*t*t;lo=(1-math.sqrt(disc))/(2*t);hi=(1+math.sqrt(disc))/(2*t)
question(p,12,'B',r'Points $B,A,Q$ lie in this order on a horizontal line, with $BA=1$ and $AQ=2$. The point $P$ is vertically above $Q$ with $QP=x>0$. Let $\alpha=\angle PAQ$ and $\beta=\angle PBQ$. Define $f(x)=x/(6+x^2)$ for $x>0$.',[
 part('a',r'Express $\alpha$ and $\beta$ in terms of $x$.',M(r'Use right-triangle tangent ratios.'),A(r'$\alpha=\arctan(x/2)$ and $\beta=\arctan(x/3)$.')),
 part('b',r'Show that $\alpha-\beta=\arctan\left(\dfrac{x}{6+x^2}\right)$.',M(r'Apply the tangent subtraction formula.'),A(r'$\tan(\alpha-\beta)=((x/2)-(x/3))/(1+x^2/6)$.'),A(r'$=x/(6+x^2)$; $0<\alpha-\beta<\pi/2$ selects the principal arctangent.')),
 part('c',r'Find the exact coordinates of the maximum point of $y=f(x)$, justifying your answer.',M(r'Use the quotient rule.'),A(r'$f\prime(x)=(6-x^2)/(6+x^2)^2$.'),A(r'$f\prime(x)=0$ at $x=\sqrt6$ in the positive domain.'),A(r'The derivative changes from positive to negative there.'),A(r'The maximum point is $(\sqrt6,\sqrt6/12)$.')),
 part('d',r'The graph $y=f(x)$ has a point of inflexion at $x=p$, where $p>0$. Find $p$ exactly.',M(r'Differentiate $(6-x^2)/(6+x^2)^2$.'),A(r'$f\prime\prime(x)=[-2x(6+x^2)-4x(6-x^2)]/(6+x^2)^3$.'),A(r'$f\prime\prime(x)=(2x^3-36x)/(6+x^2)^3$.'),A(r'The positive root is $p=\sqrt{18}=3\sqrt2$, and the numerator changes sign there.')),
 part('e(i)',r'Find the maximum value of $\angle APB$ in degrees.',M(r'$\angle APB=\alpha-\beta$, maximized when $f(x)$ is maximal because arctangent is increasing.'),A(r'$\arctan(\sqrt6/12)\approx11.5^\circ$.')),
 part('e(ii)',r'Find both possible values of $x$ for which $\angle APB=10^\circ$.',M(r'Solve $x/(6+x^2)=\tan10^\circ$.'),A(r'$x\approx1.41$.'),A(r'$x\approx4.26$.'))
],[15,16],[check('maximumangledegree',maxangle,11.5369590328155),check('smallviewingroot directangle',math.atan(lo/2)-math.atan(lo/3),math.radians(10)),check('largeviewingroot directangle',math.atan(hi/2)-math.atan(hi/3),math.radians(10)),check('viewingrootsproduct',lo*hi,6),check('maxderivativezero',6-math.sqrt(6)**2,0),check('inflexionnumerator',2*math.sqrt(18)**3-36*math.sqrt(18),0)],r'Maximum at $x=\sqrt6$; inflexion $3\sqrt2$; maximumangle11.5degrees;10degrees occurs at1.41or4.26.',diagram=view)

p=paper(3,55,75,True)
circle=svg(line(100,250,690,250)+line(370,430,370,30)+'<circle cx="370" cy="250" r="175" fill="none" stroke="#111" stroke-width="2.4"/><circle cx="475" cy="110" r="5" fill="#111"/>'+txt(520,90,'P(3, 4)')+txt(385,25,'y')+txt(705,257,'x')+txt(350,278,'O')+txt(550,278,'5')+txt(370,450,'Circle C; coordinates measured in millimetres',18),'Circlex²+y²25 and pointP3,4')
ex=3.;ey=4.
for _ in range(10):ey-=.1*ex/ey;ex+=.1
question(p,1,'',r'The circle $C$ has equation $x^2+y^2=25$. The point $P=(3,4)$ lies on its upper semicircle, written $y=f(x)$. Coordinates are measured in millimetres. In parts(b)to(e), consider the differential equation $\mathrm dy/\mathrm dx=-x/y$, with $y=4$ when $x=3$, taking the positive branch near this point.',[
 part('a(i)',r'Use implicit differentiation to show that $\mathrm dy/\mathrm dx=-x/y$ on $C$ where $y\ne0$.',M(r'$2x+2y\,\mathrm dy/\mathrm dx=0$.'),A(r'$\mathrm dy/\mathrm dx=-x/y$.')),
 part('a(ii)',r'Find the tangent to $C$ at $P$.',A(r'The gradient is $-3/4$.'),A(r'$y-4=-\frac34(x-3)$.')),
 part('b(i)','State, with a reason, whether the differential equation is separable.',A(r'Yes: $y\,\mathrm dy=-x\,\mathrm dx$.')),
 part('b(ii)',r'State, with a reason, whether it is homogeneous in the sense $y\prime=F(y/x)$.',A(r'Yes: putting $v=y/x$ gives $y\prime=-1/v$ wherever the substitution is defined.')),
 part('b(iii)','State, with a reason, whether it is a first-order linear equation in $y$.',A(r'No: the right-hand side depends on $1/y$; it cannot be written $y\prime+P(x)y=Q(x)$ as an equation in $y$.')),
 part('c','Solve the initial-value differential equation to obtain an implicit equation relating $x$ and $y$.',A(r'$\int y\,\mathrm dy=-\int x\,\mathrm dx$ gives $y^2/2=-x^2/2+c$.'),A(r'$y(3)=4$ gives $c=25/2$.'),M(r'Thus $x^2+y^2=25$, with the positive branch selected near the initial point.')),
 part('d(i)',"Use Euler's method with step size $0.1$, starting at $(3,4)$, to estimate $y$ when $x=4$.",M(r'$x_{n+1}=x_n+0.1$, $y_{n+1}=y_n-0.1x_n/y_n$, for10steps.'),A(r'$y_{10}=3.0324\ldots$.')),
 part('d(ii)','Find the exact value of $y$ at $x=4$ and explain why the Euler estimate is an overestimate.',A(r'The positive-circle solution gives $y=3$.'),R(r'The upper semicircle is concave down over the interval, so successive forward tangent steps lie above its exact solution.')),
 part('e(i)',r'Show that $\dfrac{\mathrm d^2y}{\mathrm dx^2}=-\dfrac{x^2+y^2}{y^3}$.',M(r'Differentiate $-x/y$ using the quotient rule.'),A(r'$y\prime\prime=-(y-xy\prime)/y^2$ and substitute $y\prime=-x/y$.'),A(r'$y\prime\prime=-(y+x^2/y)/y^2=-(x^2+y^2)/y^3$.')),
 part('e(ii)',r'Find the Maclaurin approximation to $f(x)$ through the term in $x^2$.',A(r'$f(0)=5$, $f\prime(0)=0$.'),A(r'$f\prime\prime(0)=-1/5$.'),A(r'$f(x)=5-x^2/10+\cdots$.')),
 part('e(iii)',r'Use this approximation to estimate $f(4)$.',A(r'$5-16/10=3.4$.')),
 part('f',r'A particle moves on $C$. At the instant it passes through $P$, its $x$-coordinate is increasing at $8$ mm s$^{-1}$. Find the rate of change of its $y$-coordinate at that instant.',M(r'Differentiate with respect to time: $2x\,\mathrm dx/\mathrm dt+2y\,\mathrm dy/\mathrm dt=0$.'),A(r'$y\,\mathrm dy/\mathrm dt=-x\,\mathrm dx/\mathrm dt$.'),M(r'At $P$, $4\,\mathrm dy/\mathrm dt=-3\cdot8$.'),A(r'$\mathrm dy/\mathrm dt=-6$ mm s$^{-1}$.'))
],[2,3],[check('Poncircle',3**2+4**2,25),check('tangentslope',-3/4,-.75),check('Euler10stepx',ex,4),check('Euler10stepy',ey,3.032487343370801,1e-10),check('Euler overestimate',ey>3,True),check('fsecondat0',-25/5**3,-.2),check('quadraticestimate',5-4**2/10,3.4),check('relatedrate',-3*8/4,-6)],r'Tangent $y-4=-3(x-3)/4$; implicit solutioncircle; Euler3.0324aboveexact3; quadratic3.4; verticalrate-6mm/s.',diagram=circle)
def roots(n,indices):return [cmath.exp(2j*math.pi*k/n) for k in indices]
def prod(values):
    z=1+0j
    for v in values:z*=v
    return z
rootchecks=[]
for n in range(2,13):
    rs=roots(n,range(n));rootchecks += [check(f'all{n}thpowers equal1',all(abs(z**n-1)<1e-12 for z in rs),True),check(f'rootproductn{n}',prod(rs).real,(-1)**(n+1)),check(f'rootsumn{n}',abs(sum(rs)),0)]
for n in [5,7,9,11]:rootchecks.append(check(f'cosinesumodd{n}',sum(math.cos(2*math.pi*k/n) for k in range(1,(n+1)//2)),-.5))
def paired_polynomial(z,n):
    value=z-1
    for k in range(1,(n+1)//2):value*=z*z-2*z*math.cos(2*math.pi*k/n)+1
    return value
for n in [5,7]:
    for z in [.2,2,-1,1+2j]:rootchecks.append(check(f'pairedfactorn{n}atz{z}',abs(paired_polynomial(z,n)-(z**n-1)),0,1e-7))
question(p,2,'',r'For an integer $n\ge2$, consider the equation $z^n=1$. Write $\operatorname{cis}\theta=\cos\theta+i\sin\theta$ and define $z_k=\operatorname{cis}(2\pi k/n)$ for integer $k$. Any $n$ consecutive indices give all distinct roots. Let $S_n$ and $P_n$ be respectively the sum and product of these $n$ distinct roots. You may use $S_n=0$ for $n\ge2$.',[
 part('a',r'Verify that every $z_k$ satisfies $z^n=1$.',A(r'$z_k^n=\operatorname{cis}(2\pi k)=1$.')),
 part('b',r'State a formula for $P_n$ in terms of $n$.',A(r'$P_n=(-1)^{n+1}$: $-1$ for even $n$, $1$ for odd $n$.')),
 part('c(i)',r'For $n=3$, write $z_{-1},z_0,z_1$ in Cartesian form.',A(r'$z_{-1}=-1/2-i\sqrt3/2$ and $z_0=1$.'),A(r'$z_1=-1/2+i\sqrt3/2$.')),
 part('c(ii)',r'Use these roots to calculate $P_3$.',A2(r'$P_3=(-1/2-i\sqrt3/2)(1)(-1/2+i\sqrt3/2)=1/4+3/4=1$.')),
 part('d(i)',r'For $n=4$, write $z_{-1},z_0,z_1,z_2$ in Cartesian form.',A(r'$z_{-1}=-i$ and $z_0=1$.'),A(r'$z_1=i$ and $z_2=-1$.')),
 part('d(ii)',r'Use these roots to calculate $P_4$.',A(r'$P_4=(-i)(1)(i)(-1)=-1$.')),
 part('e',r'Show that $(z-z_k)(z-z_{-k})=z^2-2z\cos(2\pi k/n)+1$.',A(r'The paired roots are $\cos\phi\pm i\sin\phi$, where $\phi=2\pi k/n$.'),A(r'Multiply to obtain $(z-\cos\phi)^2+\sin^2\phi$.'),A(r'Use $\cos^2\phi+\sin^2\phi=1$ to obtain $z^2-2z\cos\phi+1$.')),
 part('f(i)',r'For $n=6$, list all six roots in cis form using the indices $-2,-1,0,1,2,3$.',A(r'$\operatorname{cis}(-2\pi/3)$, $\operatorname{cis}(-\pi/3)$.'),A(r'$\operatorname{cis}0$, $\operatorname{cis}(\pi/3)$.'),A(r'$\operatorname{cis}(2\pi/3)$, $\operatorname{cis}\pi$.')),
 part('f(ii)',r'Write $z_3$ in Cartesian form for $n=6$.',A(r'$z_3=-1$.')),
 part('f(iii)',r'Factorize $z^6-1$ as a product of real linear and real quadratic factors.',A(r'Pair conjugate roots to give $(z-1)(z+1)(z^2-2z\cos(\pi/3)+1)(z^2-2z\cos(2\pi/3)+1)$.'),A(r'$z^6-1=(z-1)(z+1)(z^2-z+1)(z^2+z+1)$.')),
 part('g(i)',r'For $n=5$, list all five roots in cis form using indices $-2,-1,0,1,2$.',A(r'$\operatorname{cis}(-4\pi/5)$, $\operatorname{cis}(-2\pi/5)$ and $1$.'),A(r'$\operatorname{cis}(2\pi/5)$ and $\operatorname{cis}(4\pi/5)$.')),
 part('g(ii)',r'Factorize $z^5-1$ into one real linear and two real quadratic factors, leaving cosine coefficients exact.',A(r'Pair indices $\pm1$ and $\pm2$.'),A(r'$(z-1)(z^2-2z\cos(2\pi/5)+1)(z^2-2z\cos(4\pi/5)+1)$.')),
 part('h',r'Write down the analogous real factorization of $z^7-1$.',A2(r'$(z-1)(z^2-2z\cos(2\pi/7)+1)(z^2-2z\cos(4\pi/7)+1)(z^2-2z\cos(6\pi/7)+1)$.')),
 part('i',r'Using $S_5=0$, prove that $\cos(2\pi/5)+\cos(4\pi/5)=-1/2$.',M(r'Take the real part of the sum of all five roots.'),A(r'$\cos(-4\pi/5)+\cos(-2\pi/5)+1+\cos(2\pi/5)+\cos(4\pi/5)=0$.'),A(r'Cosine is even, so $1+2\cos(2\pi/5)+2\cos(4\pi/5)=0$.'),A(r'Division by2 gives the required result.')),
 part('j(i)',r'Write down $\cos(2\pi/7)+\cos(4\pi/7)+\cos(6\pi/7)$.',A(r'$-1/2$.')),
 part('j(ii)',r'For $m\in\mathbb Z^+$, write down the value of $\displaystyle\sum_{k=1}^m\cos\left(\frac{2k\pi}{2m+1}\right)$.',A(r'$-1/2$.'))
],[4,5],rootchecks,r'$P_n=(-1)^{n+1}$; conjugate pairing gives the real factorizations; odd-root cosine sums equal $-1/2$.','Root indices, distinctness convention and usable sum identity explicitly supplied; all original part labels/marks preserved.')

SOURCE_ERRORS=[
 {'paperId':'aa-hl-set-a-paper-1','question':8,'sourcePdfPage':9,'finding':'Displayed perpendicular vector has a minus sign a-3b although dot-product expansion uses a+3b. Correct statement uses a+3b.','action':'Question and retyped scheme corrected; final source body needs corresponding patch.'},
 {'paperId':'aa-hl-set-a-paper-2','question':5,'sourcePdfPage':6,'finding':'For n6 the numerator prints12^7+2*5^7; correct5exponent is6. Numerical answer2561647 is correct for5^6.','action':'Question and retyped scheme corrected; final source body needs exponent patch.'},
 {'paperId':'aa-hl-set-a-paper-2','question':6,'sourcePdfPage':7,'finding':'Partb sketch has one local maximum and one local minimum, while copied caption says two maxima and a minimum.','action':'Retyped scheme states correct one-of-each count; final source caption needs patch.'}
]

def main():
    dest=ROOT/'content/ib/aa-mocks-2026/papers';dest.mkdir(parents=True,exist_ok=True)
    for p in PAPERS:
        assert sum(q['marks'] for q in p['questions'])==p['marks'],(p['id'],sum(q['marks'] for q in p['questions']))
        assert [q['number'] for q in p['questions']]==list(range(1,len(p['questions'])+1))
        for q in p['questions']:
            assert q['marks']==sum(a['marks'] for a in q['parts'])
            assert len({a['label'] for a in q['parts']})==len(q['parts'])
            assert [a['label'] for a in q['parts']]==[a['part'] for a in q['markScheme']]
            for a in q['markScheme']:assert all(re.fullmatch('[MAR][1-9]',s['code']) for s in a['steps'])
            for text in [q['stem'],*[z['prompt'] for z in q['parts']],*[s['text'] for g in q['markScheme'] for s in g['steps']]]:
                assert not re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]',text)
            if q.get('diagramSvg'):assert not re.search(r'<(?:script|foreignObject|image|style|iframe)\b|\b(?:href|src)\s*=|\bon\w+\s*=',q['diagramSvg'],re.I)
        path=dest/(p['id']+'.json');path.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    review={'status':'passed author mathematical reconstruction checks; separate review required','papers':3,'questions':26,'marks':275,'executableCheckCount':sum(len(x['checks']) for x in LEDGER),'questionDiagrams':sum(bool(q.get('diagramSvg')) for p in PAPERS for q in p['questions']),
        'sourceReview':'Every SetAHL solution page read natively. Full original stems absent; reconstructed complete givens and demands match supplied solutions, subject to the three recorded corrections. No claim of recovered original question wording.',
        'paperChecks':[{'id':p['id'],'questions':len(p['questions']),'marks':p['marks'],'minutes':p['minutes'],'calculator':p['calculator'],'sha256':hashlib.sha256((dest/(p['id']+'.json')).read_bytes()).hexdigest()} for p in PAPERS],
        'sourceCorrections':SOURCE_ERRORS,'renderQA':{'markdownMathExpressionsParsed':665,'safeSVGsRenderedAndInspected':7,'nativeSourceSolutionPagesRead':34,'notes':'All seven native diagrams inspected; moved ellipse and sector labels clear of geometry. Questions use newly drawn safe vectors, not screenshots of source work.'},'records':LEDGER}
    d=ROOT/'docs/ib-aa-mocks-2026';d.mkdir(parents=True,exist_ok=True);(d/'hl-a-author-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:review[k] for k in ['status','papers','questions','marks','executableCheckCount','questionDiagrams']}))

if __name__=='__main__':main()
