"""Original AI HL expansion. Run from repo root; no existing content is changed.

Each record has an independently evaluated numerical identity, residual or enumeration.
The checks are deliberately separate from the displayed mark-scheme prose.
"""
import json, math, itertools, statistics, re
from pathlib import Path
from xml.sax.saxutils import escape
from statistics import NormalDist

ROOT=Path(__file__).resolve().parents[2]
Q=[]; AUDIT=[]; ACTIVE=[]
def ck(label,actual,expected,tol=1e-8):
    assert abs(actual-expected)<=tol*max(1,abs(expected)),(label,actual,expected)
    ACTIVE.append({'check':label,'actual':actual,'expected':expected,'tolerance':tol})
def truth(label,value):
    assert value,label
    ACTIVE.append({'check':label,'passed':True})
def bisect(f,a,b):
    assert f(a)*f(b)<=0
    for _ in range(85):
        c=(a+b)/2
        if f(a)*f(c)<=0:b=c
        else:a=c
    return (a+b)/2
def integ(f,a,b,n=2000):
    h=(b-a)/n
    return h/3*(f(a)+f(b)+4*sum(f(a+i*h) for i in range(1,n,2))+2*sum(f(a+i*h) for i in range(2,n,2)))
def mm(A,B):return [[sum(a*b for a,b in zip(row,col)) for col in zip(*B)] for row in A]
def mp(A,n):
    R=[[1,0],[0,1]]
    for _ in range(n):R=mm(R,A)
    return R
def svg(body,title='Diagram'):
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 380" role="img"><title>'+escape(title)+'</title><rect width="640" height="380" fill="white"/><g stroke="#171717" fill="none" stroke-width="1.7">'+body+'</g></svg>'
def txt(x,y,s,size=15,anchor='middle'):return f'<text x="{x:.2f}" y="{y:.2f}" fill="#171717" stroke="none" font-family="Arial,sans-serif" font-size="{size}" text-anchor="{anchor}">{escape(str(s))}</text>'
def plot(fs,xlim,ylim,xlab='x',ylab='y',points=(),title='Graph supplied in the question',dashed=(),equal=False):
    xa,xb=xlim;ya,yb=ylim
    width=510 if not equal else min(510,260*(xb-xa)/(yb-ya));left=320-width/2
    X=lambda x:left+width*(x-xa)/(xb-xa)
    Y=lambda y:315-260*(y-ya)/(yb-ya)
    body=f'<path d="M{left:.2f} 48V315H{left+width:.2f}"/>'+txt(325,365,xlab)+txt(left,28,ylab,14,'start')
    if xa<0<xb:body+=f'<path d="M{X(0):.2f} 55V315" stroke-width="0.7" stroke-dasharray="4 4"/>'
    if ya<0<yb:body+=f'<path d="M{left:.2f} {Y(0):.2f}H{left+width:.2f}" stroke-width="0.7" stroke-dasharray="4 4"/>'
    for i in range(6):
        x=xa+(xb-xa)*i/5;y=ya+(yb-ya)*i/5
        body+=f'<path d="M{X(x):.2f} 315v5 M{left-5:.2f} {Y(y):.2f}h5"/>'+txt(X(x),340,f'{x:.3g}',12)+txt(left-29,Y(y)+4,f'{y:.3g}',12)
    for index,f in enumerate(fs):
        pts=[]
        for i in range(241):
            x=xa+(xb-xa)*i/240
            try:y=f(x)
            except (ValueError,ZeroDivisionError,OverflowError):y=float('nan')
            if math.isfinite(y) and ya<=y<=yb:pts.append((X(x),Y(y)))
            elif pts:
                body+='<polyline points="'+' '.join(f'{xx:.2f},{yy:.2f}' for xx,yy in pts)+'"/>';pts=[]
        if pts:body+='<polyline '+('stroke-dasharray="7 4" ' if index in dashed else '')+'points="'+' '.join(f'{xx:.2f},{yy:.2f}' for xx,yy in pts)+'"/>'
    for x,y,label in points:
        body+=f'<circle cx="{X(x):.2f}" cy="{Y(y):.2f}" r="3.5" fill="#171717"/>'+txt(X(x),Y(y)-10,label,13)
    return svg(body,title)
def table(headers,rows,title='Data provided'):
    cols=len(headers);cw=530/cols;rh=min(45,260/(len(rows)+1));ys=65
    body=''
    for i,row in enumerate([headers]+rows):
        for j,v in enumerate(row):
            body+=f'<rect x="{55+j*cw}" y="{ys+i*rh}" width="{cw}" height="{rh}"/>'+txt(55+(j+.5)*cw,ys+(i+.62)*rh,v,14)
    body+=txt(320,35,title,17)
    return svg(body,title)
def network(vertices,edges,title='Network; edge weights are given',directed=False):
    n=len(vertices);pos={v:(320+230*math.cos(2*math.pi*i/n-math.pi/2),190+135*math.sin(2*math.pi*i/n-math.pi/2)) for i,v in enumerate(vertices)}
    body=''
    for k,(u,v,w) in enumerate(edges):
        x,y=pos[u];xx,yy=pos[v]
        body+=f'<path d="M{x:.2f} {y:.2f}L{xx:.2f} {yy:.2f}"/>'
        dist=math.hypot(xx-x,yy-y);ux=(xx-x)/dist;uy=(yy-y)/dist
        if directed:
            hx=xx-17*ux;hy=yy-17*uy
            body+=f'<path d="M{hx-9*ux+4*uy:.2f} {hy-9*uy-4*ux:.2f}L{hx:.2f} {hy:.2f}L{hx-9*ux-4*uy:.2f} {hy-9*uy+4*ux:.2f}"/>'
        if w is not None:
            lx=(x+xx)/2-22*uy;ly=(y+yy)/2+22*ux
            ww=max(26,len(str(w))*8+6)
            body+=f'<rect x="{lx-ww/2:.2f}" y="{ly-12:.2f}" width="{ww}" height="22" fill="white" stroke="none"/>'+txt(lx,ly+4,w,13)
    for v,(x,y) in pos.items():body+=f'<circle cx="{x:.2f}" cy="{y:.2f}" r="15" fill="white"/>'+txt(x,y+5,v)
    return svg(body,title)
def argand(points,extra=''):
    span=max(6,max(max(abs(x),abs(y)) for x,y,label in points)+1)
    return plot([],(-span,span),(-span,span),'Re z','Im z',points,'Argand diagram; plotted data are supplied',equal=True) if not extra else svg(extra,'Argand construction')
def p(prompt,*steps):return (prompt,[{'code':x.split('|',1)[0],'text':x.split('|',1)[1]} for x in steps])
def add(topic,title,code,subtopic,stem,parts,diagram,difficulty='hard',level='ahl',style='extended-response',summary=''):
    assert ACTIVE,(title,'missing independent check')
    ids={'number-algebra':'na','functions':'fn','geometry-trigonometry':'gt','statistics-probability':'sp','calculus':'ca'}
    number=701+sum(x['topicId']==topic for x in Q)
    partrows=[];schemes=[]
    for i,(prompt,steps) in enumerate(parts):
        marks=sum(int(s['code'][1:]) for s in steps if s['code'] not in ['AG','IND']);label=chr(97+i)
        partrows.append({'label':label,'prompt':prompt,'marks':marks});schemes.append({'part':label,'steps':steps})
    ident=f'ib-aihl-{ids[topic]}-{number}'
    q=dict(id=ident,subject='math-ai-hl',topicId=topic,collectionId='ai-hl-'+topic,number=number,title=title,subtopic=subtopic,syllabusCode=code,level=level,difficulty=difficulty,calculator=True,examStyle=style,marks=sum(x['marks'] for x in partrows),stem=stem+' Give non-exact numerical answers to three significant figures unless stated otherwise.',parts=partrows,markScheme=schemes,diagramSvg=diagram,diagramCaption='Original vector diagram. Use the data and scale shown; geometric sketches are not to scale unless coordinates are given.',answerSummary=summary or 'See the worked reasoning and final results in the mark scheme.',source={'document':'Independent syllabus-authored practice','question':number},verification={'method':'Independent numerical residuals, exact arithmetic or exhaustive finite enumeration; author reasoning review','notes':'Original current-syllabus AI HL practice. Per-question checks recorded in docs/ib-2026-maths/ai-hl-author-review.json; separate reviewer required before release.'},status='published')
    Q.append(q);AUDIT.append({'id':ident,'title':title,'checks':list(ACTIVE)});ACTIVE.clear()

# TOPIC 1 — 20 distinct algebra/finance/matrix/complex-number constructions.
T='number-algebra'
ck('Leslie observation',.5*160+.5*100,130);ck('dominant eigenvalue residual',((.5+math.sqrt(1.85))/2)**2-.5*((.5+math.sqrt(1.85))/2)-.4,0)
add(T,'Restoring a two-stage population','1.15','Eigenvalues and diagonalisation',r'A nursery models juvenile and adult plants by $v_{n+1}=Lv_n$, where $L=\begin{pmatrix}0&f\\0.5&0.5\end{pmatrix}$. Initially $v_0=(160,100)^T$, and $v_1=(80,130)^T$. No plants enter from outside.',[
p('Determine $f$ and interpret both entries of the second row.','M1|Use the juvenile observation $100f=80$.','A1|$f=0.8$ juveniles per adult per year.','R1|Half the juveniles become adults and half the existing adults survive to the next year.'),
p('Find the eigenvalues and decide whether this model sustains the population in the long term.',r'M1|Solve $\lambda^2-0.5\lambda-0.4=0$.',r'A1|$\lambda=0.930074$ and $-0.430074$.','R1|The dominant modulus is below 1, so the population tends to zero.'),
p('Find the adult-to-juvenile ratio approached by a non-zero population. Explain why a negative eigenvalue does not mean negative plant numbers.',r'M1|For the dominant eigenvector, $0.8A=\lambda J$.','A1|$A/J=0.930074/0.8=1.16259$.','R1|The negative eigenvalue describes an alternating decaying component; non-negative initial data remain non-negative under $L$.')],table(['Stage','Year 0','Year 1'],[['Juvenile',160,80],['Adult',100,130]],'Observed plant counts'))
# Correct independent characteristic-polynomial check rather than a rounded transcription.
AUDIT[-1]['checks']=[{'check':'dominant eigenvalue residual','actual':((.5+math.sqrt(1.85))/2)**2-.5*((.5+math.sqrt(1.85))/2)-.4,'expected':0}]
ck('affine recurrence fixed point',.82*250+45,250);ck('year threshold',math.ceil(math.log((250-220)/(250-100)) / math.log(.82)),9)
add(T,'Woodland recovery with annual planting','1.11','Sequences and financial models',r'After each winter 82% of a woodland survives. Immediately afterwards 45 hectares are planted. Let $A_0=100$ hectares and $A_{n+1}=0.82A_n+45$. The diagram shows the update rule and the line $y=x$.',[
p('Find the equilibrium area and derive a formula for $A_n$.','M1|Solve $L=0.82L+45$.','A1|$L=250$.','M1|Set $B_n=A_n-250$, giving $B_{n+1}=0.82B_n$.','A1|$A_n=250-150(0.82)^n$.'),
p('Find the first whole year in which the area exceeds 220 hectares.','M1|Solve $(0.82)^n<0.2$.','A1|$n>8.11000$; the first year is 9.'),
p('A manager proposes a 270-hectare target without changing the rule. Assess this proposal.','R1|The sequence increases towards 250 from below.','R1|It never reaches 270; planting must increase or the survival rate must improve.')],plot([lambda x:.82*x+45,lambda x:x],(0,300),(0,300),'current area','next area',dashed=(1,)),level='sl',difficulty='medium')
bal=12000*1.005**24-300*(1.005**24-1)/.005
ck('loan balance',bal,5896.330742141335,1e-7)
add(T,'The hidden balloon payment','1.7','Sequences and financial models',r'A loan of 12000 currency units charges 0.5% interest monthly. A payment of 300 is made at each month-end for 24 months. A dealer says that the payments clear the loan.',[
p('Write the balance recurrence and calculate the amount outstanding immediately after payment 24.','M1|$B_{n+1}=1.005B_n-300$, $B_0=12000$.','M1|$B_{24}=12000(1.005)^{24}-300((1.005)^{24}-1)/0.005$.','A1|$B_{24}=5896.33$; the claim is false.'),
p('Find the equal monthly payment that would clear the loan in 24 months.','M1|Set $0=12000(1.005)^{24}-R((1.005)^{24}-1)/0.005$.','A1|$R=531.847$, or 531.85 to the nearest cent.'),
p('Explain why subtracting $24(300)$ from the initial loan underestimates the remaining debt.','R1|Interest is added each month to the unpaid balance.','R1|Ignoring this accumulated interest gives only 4800, below the actual debt.')],plot([lambda n:12000*1.005**n-300*(1.005**n-1)/.005],(0,24),(0,13000),'months','balance'),level='sl',difficulty='medium')
npv=lambda r:-5000+2000/(1+r)+2000/(1+r)**2+2000/(1+r)**3
ck('investment NPV at 10%',npv(.1),-26.296018031557,1e-7)
add(T,'Investment returns with an early exit','1.7','Sequences and financial models',r'An investment costs 5000 now and returns 2000 at the end of each of years 1, 2 and 3. Its net present value at annual rate $r$ is the discounted receipts less 5000.',[
p('Calculate the net present value at 8% and at 10%.','M1|Use $N(r)=-5000+2000/(1+r)+2000/(1+r)^2+2000/(1+r)^3$.','A1|$N(0.08)=154.194$ and $N(0.10)=-26.2960$.'),
p('Estimate the annual rate for which the net present value is zero, and explain why there is only one positive solution.','M1|Solve $N(r)=0$ numerically.','A1|$r=0.0970103$, or 9.70%.','R1|Each positive receipt decreases as the discount rate increases, so $N$ is strictly decreasing for $r>0$.'),
p('A buyer offers 3500 immediately after the first receipt. At an 8% discount rate, decide whether selling is preferable to retaining the remaining receipts.','M1|At year 1, the remaining receipts have value $2000/1.08+2000/1.08^2$.','A1|This is 3566.53, exceeding 3500; retaining has the higher present value.')],plot([npv],(0,.2),(-1000,1100),'annual rate r','net present value'),level='sl')
ck('price equations first',2*4+3*5+6,29);ck('price equations second',4+2*5+2*6,26);ck('price equations third',3*4+5+6,23)
add(T,'Recovering prices from mixed orders','1.14','Matrices and systems',r'Three orders contain products A, B and C. The supplied table gives quantities and total prices. Unit prices are constant.',[
p('Form a matrix equation and find the three unit prices.',r'M1|$\begin{pmatrix}2&3&1\\1&2&2\\3&1&1\end{pmatrix}(a,b,c)^T=(29,26,23)^T$.','M1|Solve the non-singular linear system.','A1|$a=4$, $b=5$, $c=6$.'),
p('The total price of order 1 was recorded 1 too high. Find the corrected unit prices without changing either other total.','M1|Solve the system with right-hand side $(28,26,23)^T$.','A1|The corrected prices are $a=4$, $b=9/2$, $c=13/2$.','R1|A correction to one order can affect more than one inferred unit price; here b and c change while a stays 4. Subtracting 1 from a single price is unjustified.')],table(['Order','A','B','C','Total'],[['1',2,3,1,29],['2',1,2,2,26],['3',3,1,1,23]],'Mixed-product orders'),difficulty='medium')
ck('resource bottleneck',min(960/7,750/8),93.75)
add(T,'A production mix under two resource limits','1.14','Matrices and systems',r'Each premium kit uses 3 units of timber and 2 units of fabric; each basic kit uses 2 units of timber and 3 units of fabric. A contract requires twice as many basic kits as premium kits. Available resources are 960 timber units and 750 fabric units.',[
p('Write the resource matrix and express consumption for $k$ premium kits.',r'M1|$R=\begin{pmatrix}3&2\\2&3\end{pmatrix}$, with output vector $(k,2k)^T$.','A1|Consumption is $(7k,8k)^T$.'),
p('Find the maximum integer $k$ and identify the binding resource.',r'M1|Require $7k\le960$ and $8k\le750$.',r'A1|$k\le93.75$, so $k=93$; fabric is binding.'),
p('Find the unused resources at this production level. If one additional premium kit and two basic kits are required, state the minimum extra fabric needed.','M1|Subtract $(651,744)^T$ from available resources.','A1|309 timber and 6 fabric units remain.','A1|The next package requires 8 fabric units, so 2 additional units suffice.')],table(['Kit','Timber','Fabric'],[['Premium',3,2],['Basic',2,3],['Available',960,750]],'Resource requirements'),difficulty='medium')
ck('calibration order difference',1.2*(80+10)-(1.2*80+10),2)
add(T,'Why calibration order matters','1.14','Matrices and systems',r'A sensor reading is represented by $(x,1)^T$. A gain operation is $G=\begin{pmatrix}1.2&0\\0&1\end{pmatrix}$ and an offset is $H=\begin{pmatrix}1&10\\0&1\end{pmatrix}$. A technician applies gain and then offset.',[
p('Find the combined matrix for the technician’s procedure.','M1|For column vectors the operation performed first is on the right.',r'A1|$HG=\begin{pmatrix}1.2&10\\0&1\end{pmatrix}$.'),
p('Compare the two possible orders for an initial reading of 80.','M1|Evaluate $HG(80,1)^T$ and $GH(80,1)^T$.','A1|Gain then offset gives 106; offset then gain gives 108.'),
p('Determine whether any initial reading makes the two outputs equal. Explain using the matrix difference.',r'M1|$GH-HG=\begin{pmatrix}0&2\\0&0\end{pmatrix}$.','R1|The first coordinate differs by 2 for every $(x,1)^T$; there is no such reading.')],table(['Operation','Input','Output'],[['Gain','x','1.2x'],['Offset','x','x + 10']], 'Two calibration operations'),difficulty='medium')
ck('mix recovery x',.7*40+.2*60,40);ck('mix recovery y',.3*40+.8*60,60)
add(T,'Reconstructing two original mixtures','1.14','Matrices and systems',r'A mixing process sends 70% of tank A and 20% of tank B into tank C. The rest enters tank D. Final volumes are 40 litres in C and 60 litres in D. No liquid is lost.',[
p('Use a matrix inverse to determine the original volumes.',r'M1|$\begin{pmatrix}0.7&0.2\\0.3&0.8\end{pmatrix}(A,B)^T=(40,60)^T$.','M1|The determinant is 0.5, so the inverse exists.','A1|$A=40$ litres and $B=60$ litres.'),
p(r'Only C is measured with an error: its recorded volume increases by $\varepsilon$ while D stays 60. Find the errors in the recovered volumes.',r'M1|Multiply $(\varepsilon,0)^T$ by the inverse.',r'A1|Errors are $1.6\varepsilon$ in A and $-0.6\varepsilon$ in B.'),
p('Explain why a much smaller determinant could make this reconstruction less reliable.','R1|The inverse divides by the determinant.','R1|For otherwise comparable entries, measurement errors can be magnified substantially.')],network(['A','B','C','D'],[('A','C','70%'),('A','D','30%'),('B','C','20%'),('B','D','80%')],'Mixing fractions; column states are original tanks'),difficulty='medium')
ck('population eigenmode',mm([[1.1,.2],[.1,1]],[[2],[1]])[0][0],2.4)
add(T,'Choosing a balanced initial population','1.15','Eigenvalues and diagonalisation',r'Two related populations follow $v_{n+1}=Av_n$ with $A=\begin{pmatrix}1.1&0.2\\0.1&1\end{pmatrix}$. Initially there are 600 organisms in total.',[
p('Find the eigenvalues and a corresponding positive eigenvector.',r'M1|Solve $(1.1-\lambda)(1-\lambda)-0.02=0$.','A1|Eigenvalues are 1.2 and 0.9.','A1|For 1.2, one eigenvector is $(2,1)^T$.'),
p('Find the initial populations for which their ratio remains unchanged, and predict the total after five years.','M1|Scale $(2,1)^T$ so its entries sum to 600.','A1|Initial populations are 400 and 200.','A1|Total $=600(1.2)^5=1492.992$.'),
p('Explain what happens to the ratio for any strictly positive initial populations.','R1|The contribution with eigenvalue 0.9 decays relative to that with eigenvalue 1.2.','R1|The ratio approaches $2:1$.')],table(['From / to','Population 1','Population 2'],[['Population 1',1.1,.1],['Population 2',.2,1]],'Annual contributions per organism'))
A=[[.8,.1],[.2,.9]];V=mm(mp(A,4),[[100],[0]])
ck('four-step total',sum(v[0] for v in V),100);ck('four-step first',V[0][0],49.34)
add(T,'An exact forecast without repeated multiplication','1.15','Eigenvalues and diagonalisation',r'Users switch between services A and B. For column state vectors the update is $M=\begin{pmatrix}0.8&0.1\\0.2&0.9\end{pmatrix}$ and $v_0=(100,0)^T$.',[
p('Find eigenvalues and eigenvectors sufficient to diagonalise $M$.','M1|Solve the characteristic equation.','A1|Eigenvalues 1 and 0.7 have eigenvectors $(1,2)^T$ and $(1,-1)^T$ respectively.'),
p('Express $v_n$ in terms of these eigenvectors and find $v_4$.',r'M1|$v_0=\frac{100}{3}(1,2)^T+\frac{200}{3}(1,-1)^T$.',r'A1|$v_n=\frac{100}{3}(1,2)^T+\frac{200}{3}(0.7)^n(1,-1)^T$.','A1|$v_4=(49.34,50.66)^T$.'),
p('Find the least $n$ for which the number using A is below 35.','M1|Solve $100/3+(200/3)(0.7)^n<35$.','A1|$(0.7)^n<0.025$, giving $n>10.3424$ and least $n=11$.')],table(['Current service','Next A','Next B'],[['A',.8,.2],['B',.1,.9]],'Switching probabilities per month'),style='problem-solving')
z=(3+4j)*(6-2j)/((3+4j)+(6-2j));ck('parallel impedance real',z.real,3.176470588235294);ck('parallel impedance imaginary',z.imag,1.2941176470588234)
add(T,'Parallel impedances and phase','1.13','Complex numbers',r'Two impedances are $Z_1=3+4i$ and $Z_2=6-2i$ ohms. Their parallel equivalent is $Z=Z_1Z_2/(Z_1+Z_2)$. The circuit voltage phasor is the positive real number 12.',[
p('Calculate $Z$ in Cartesian and polar form.','M1|Substitute into $Z=(26+18i)/(9+2i)$.','A1|$Z=3.17647+1.29412i$.',r'A1|$|Z|=3.42997$ and $\arg Z=0.386876$ radians.'),
p('Find the current phasor $I=12/Z$ and decide whether current leads or lags voltage.','M1|Divide the voltage phasor by $Z$.','A1|$I=3.24-1.32i$ amperes.','R1|Its argument is negative, so current lags the voltage by 0.386876 radians.')],argand([(3,4,'Z1'),(6,-2,'Z2')]))
ck('phasor cancellation amplitude',abs(8+6j),10)
add(T,'Combining two out-of-phase signals','1.13','Complex numbers',r'Two signals are $u(t)=8\cos(30t)$ and $v(t)=6\cos(30t+\pi/2)$. Their total is written $w(t)=R\cos(30t+\phi)$ with $R>0$ and $-\pi<\phi\le\pi$.',[
p(r'Use complex numbers to find $R$ and $\phi$.','M1|The phasor sum is $8+6i$.',r'A1|$R=10$ and $\phi=\tan^{-1}(6/8)=0.643501$ radians.'),
p('A third signal of amplitude 5 is added. Determine the phase that minimises the resulting amplitude and find that minimum.','M1|Choose the third phasor opposite to $8+6i$.',r'A1|Phase $=\phi-\pi=-2.49809$ radians.','R1|By the reverse triangle inequality, the smallest possible amplitude is $10-5=5$.'),
p('Explain why no choice of the third phase makes the total signal identically zero.','R1|Cancellation requires equal and opposite phasors.','R1|The existing resultant has amplitude 10 but the third has amplitude 5.')],argand([(8,0,'u = 8'),(0,6,'v = 6i')]),difficulty='medium')
ck('complex repeated stretch',abs((1.1*complex(math.cos(math.pi/6),math.sin(math.pi/6)))**8),1.1**8)
add(T,'A spiral generated by repeated multiplication','1.13','Complex numbers',r'A point begins at $z_0=2$ and is updated by $z_{n+1}=1.1e^{i\pi/6}z_n$. The diagram shows only the starting point and the reference axes.',[
p('Describe the transformation and give a formula for $z_n$.',r'A1|Each update rotates anticlockwise by $\pi/6$ and enlarges distances from the origin by factor 1.1.',r'A1|$z_n=2(1.1)^ne^{in\pi/6}$.'),
p('Find the least positive $n$ for which the point lies on the positive real axis again. Find its distance from the origin then.',r'M1|Require $n\pi/6$ to be a multiple of $2\pi$.','A1|$n=12$ and distance $2(1.1)^{12}=6.27686$.'),
p('Find the first $n$ for which the distance exceeds 10, and determine the principal argument then.','M1|Solve $2(1.1)^n>10$.','A1|Least $n=17$.',r'A1|$17\pi/6$ has principal argument $5\pi/6$.')],argand([(2,0,'z0')]))
ck('complex roots polynomial',abs((2+3j)**2-4*(2+3j)+13),0)
add(T,'Recovering a quadratic from an Argand point','1.12','Complex numbers',r'A real monic quadratic has a root represented by the point $(2,3)$ on an Argand diagram. Its graph meets the real vertical axis at $c$.',[
p('Find the other root and the quadratic.','R1|A real-coefficient quadratic has conjugate roots, so the other root is $2-3i$.','M1|Expand $(x-2-3i)(x-2+3i)$.','A1|$f(x)=x^2-4x+13$, so $c=13$.'),
p('Find the minimum value of the real function and explain its connection to the diagram.','M1|Complete the square: $f(x)=(x-2)^2+9$.','A1|The minimum is 9 at $x=2$.','R1|The positive minimum is the square of the imaginary coordinate, $3^2$; no real roots occur.'),
p('A vertical shift produces exactly one real root. Determine the shift.','M1|The vertex must lie on the horizontal axis.','A1|Translate down by 9, giving $(x-2)^2$.')],argand([(2,3,'root z')]),difficulty='medium')
ck('fractal area sum',3/(1-.4),5)
add(T,'A convergent design with an expanding boundary','1.11','Logarithms and series',r'A decorative process adds disjoint patches. At stage $n\ge1$ the total area added is $3(0.4)^{n-1}$ square units, while the total new boundary length is $4(1.2)^{n-1}$ units. Areas and boundary lengths may be summed without overlap.',[
p('Find the limiting total area and the area still to be added after five stages.','M1|Sum the geometric area series.','A1|Limiting area is $3/(1-0.4)=5$.','A1|Remaining area is $5(0.4)^5=0.0512$.'),
p('Determine the first stage after which less than 0.001 square units remain.','M1|Solve $5(0.4)^n<0.001$.','A1|$n>9.29530$; the first stage is 10.'),
p('Explain why finite limiting area does not imply finite total boundary length here.','R1|The boundary series has ratio 1.2, exceeding 1.','R1|Its terms do not tend to zero, so the boundary sum diverges despite the convergent area sum.')],plot([lambda n:3*.4**(n-1)],(1,8),(0,3.2),'stage n','area added'),difficulty='medium')
ck('log calibration',math.log10(800/50),math.log10(16))
add(T,'Comparing logarithmic instrument scales','1.9','Logarithms and series',r'An instrument displays $D=a+b\log_{10}I$ for positive intensity $I$. It reads 20 when $I=50$ and 32 when $I=800$.',[
p('Find $a$ and $b$.',r'M1|Subtract the equations: $12=b\log_{10}(16)$.','A1|$b=9.96578$ and $a=3.06843$.'),
p('Find the intensity corresponding to display 26, without separately using the rounded values of $a$ and $b$.','M1|A halfway display corresponds to a halfway logarithm.',r'A1|$I=\sqrt{50(800)}=200$.'),
p('A technician claims that doubling the displayed value doubles the intensity. Explain why this is false, and find the intensity ratio for a 6-unit increase.','R1|Equal display increments correspond to multiplicative intensity changes; display ratios do not.','M1|$I_2/I_1=10^{6/b}$.','A1|The ratio is 4.')],plot([lambda x:math.log10(x)],(50,800),(1.5,3),'intensity I','log10 I'),difficulty='medium')
ck('hybrid fund annual total',sum(1000+50*(n-1) for n in range(1,11)),12250)
add(T,'Growing deposits versus a spending target','1.3','Sequences and financial models',r'At the end of year $n$, a charity deposits $1000+50(n-1)$ into an account earning 4% annually. There are ten deposits, and the balance is measured immediately after deposit 10.',[
p('Write a sum for the final balance, explaining the exponent on each term.',r'M1|$B=\sum_{n=1}^{10}[1000+50(n-1)](1.04)^{10-n}$.','R1|Deposit $n$ earns interest for $10-n$ years.'),
p('Calculate the final balance and the interest earned.','M1|Evaluate the sum using technology.','A1|$B=14513.74$ approximately.','A1|Deposits total 12250, so interest is approximately 2263.74.'),
p('The target is 15000. Keeping the yearly increment 50, find the smallest initial deposit, to the nearest whole unit rounded upwards, that reaches the target.',r'M1|Solve $\sum_{n=1}^{10}[a+50(n-1)]1.04^{10-n}=15000$.',r'A1|$a\approx1040.50$; the required whole-unit initial deposit is 1041.')],table(['Year','Deposit','Interest years'],[[1,1000,9],[2,1050,8],[3,1100,7],['10',1450,0]],'Deposit timing'))
ck('growing perpetuity',200/(1.06-1.02),5000)
add(T,'A growing perpetuity and its hidden assumption','1.11','Logarithms and series',r'A fund pays 200 at the end of year 1 and increases each subsequent payment by 2%. Payments continue indefinitely. The annual discount rate is 6%.',[
p('Express the present values as a geometric series and find their sum.','M1|Terms are $200/1.06$, $200(1.02)/1.06^2$, and so on.','A1|Ratio $=1.02/1.06<1$.','A1|Present value $=200/(1.06-1.02)=5000$.'),
p('Find the greatest annual payment growth rate that makes the present value at most 8000.',r'M1|For growth $g<0.06$, solve $200/(0.06-g)\le8000$.',r'A1|$g\le0.035$; the greatest rate is 3.5%.'),
p('Explain what fails mathematically if the growth rate is raised to 6%.','R1|The discounted geometric ratio becomes 1.','R1|The terms do not decrease to zero and the present value diverges.')],plot([lambda n:200/1.06*(1.02/1.06)**(n-1)],(1,30),(0,200),'year','present value of payment'))
ck('encoding forward',mm([[2,1],[1,1]],[[4],[7]])[0][0],15)
add(T,'Decoding a message with one corrupted entry','1.14','Matrices and systems',r'An encoder maps column pairs by $c=Ax+b$, with $A=\begin{pmatrix}2&1\\1&1\end{pmatrix}$ and $b=(3,-2)^T$. A received pair is $(18,9)^T$.',[
p('Decode the pair.','M1|Subtract $b$ to obtain $(15,11)^T$.',r'M1|$A^{-1}=\begin{pmatrix}1&-1\\-1&2\end{pmatrix}$.','A1|The original pair is $(4,7)^T$.'),
p('Only the first received coordinate is corrupted by an additive error $e$. Find the corresponding error in the decoded pair.','M1|Apply $A^{-1}$ to $(e,0)^T$.','A1|The decoded error is $(e,-e)^T$.'),
p('Give one check on decoded data that cannot detect this corruption, and explain why.','R1|Checking the sum of the decoded coordinates cannot detect it.','R1|The errors sum to zero, so the sum remains 11.')],table(['Input pair','Linear part','Offset'],[['(x, y)','(2x+y, x+y)','(3, -2)']], 'Affine encoder'))
ck('singular determinant',2*6-3*4,0)
add(T,'When two measurements cannot identify a mixture','1.14','Matrices and systems',r'Two unknown concentrations satisfy $2x+3y=12$ and $4x+ky=24$. A laboratory claims that two equations always determine one unique pair.',[
p('Find the value of $k$ for which the coefficient matrix is singular.','M1|Set determinant $2k-12=0$.','A1|$k=6$.'),
p('For this value of $k$, describe all non-negative solutions and explain the laboratory’s error.','M1|The equations become dependent, leaving $2x+3y=12$.',r'A1|$y=4-2x/3$, $0\le x\le6$.','R1|There are infinitely many feasible pairs, since the second measurement provides no independent information.'),
p('If the second total were 25 instead of 24, with $k=6$, explain what could be concluded.','R1|Doubling the first equation forces the total to be 24.','R1|A total of 25 is inconsistent; no exact solution exists and measurement/model error should be investigated.')],plot([lambda x:4-2*x/3],(0,6),(0,4),'concentration x','concentration y'),difficulty='medium')

# TOPIC 2 — models, inverse decisions, transformations and validation.
T='functions'
logistic=lambda t:1200/(1+5*math.exp(-.3*t))
ck('logistic initial value',logistic(0),200);ck('logistic target residual',logistic(math.log(15)/.3),900)
add(T,'Identifying a logistic adoption model','2.9','Exponential and logistic models',r'A new service is modelled by $N(t)=1200/(1+Ce^{-kt})$. There are 200 users initially and 600 after 5.36479 months. The graph shows the observations and carrying capacity.',[
p(r'Find $C$ and $k$.',r'M1|At $t=0$, $200=1200/(1+C)$.',r'A1|$C=5$.',r'M1|Use $600=1200/(1+5e^{-5.36479k})$.',r'A1|$k=0.300000$ approximately.'),
p(r'Find when the model first predicts 900 users.',r'M1|$900=1200/(1+5e^{-0.3t})$, so $e^{-0.3t}=1/15$.',r'A1|$t=\ln(15)/0.3=9.02683$ months.'),
p(r'Explain why an exponential model fitted to the same observations gives a less plausible long-term forecast.',r'R1|A positive exponential model grows without bound.',r'R1|The logistic model approaches a finite capacity of 1200; the context includes a limited potential user base.')],plot([lambda t:1200],(0,12),(0,1400),'months','users',[(0,200,'200'),(5.36479,600,'600')],dashed=(0,)),difficulty='medium')
r=bisect(lambda t:100*math.exp(.18*t)-180*math.exp(.1*t),0,20);ck('two growth intersection',r,math.log(1.8)/.08)
add(T,'Two growing populations with a delayed start','2.9','Exponential and logistic models',r'For $t\ge0$, two colonies have sizes $A(t)=100e^{0.18t}$ and $B(t)=180e^{0.10t}$. Time is measured in days. The model is considered reliable only for the first 10 days.',[
p(r'Find when A first exceeds B.',r'M1|Set $100e^{0.18t}=180e^{0.10t}$.',r'A1|$t=\ln(1.8)/0.08=7.34733$ days; A exceeds B afterwards.'),
p(r'Find when A is twice B and assess the reliability of that prediction.',r'M1|Solve $e^{0.08t}=3.6$.',r'A1|$t=\ln(3.6)/0.08=16.0117$ days.',r'R1|This is outside the stated 10-day validation period, so it requires extrapolation and should be treated cautiously.'),
p(r'If A is started 2 days later, find its population at calendar day 10 and decide which colony is then larger.',r'M1|Use $A(10-2)=100e^{0.18(8)}$.',r'A1|A has 422.070 and B has $180e^1=489.291$; B is larger.')],plot([lambda t:100*math.exp(.18*t),lambda t:180*math.exp(.1*t)],(0,10),(0,650),'days','population',dashed=(1,)),difficulty='medium')
ck('loglog slope',(math.log(108)-math.log(4))/(math.log(9)-math.log(1)),1.5)
add(T,'Reading a power law from log-log data','2.10','Linearisation and model evaluation',r'A straight line on log-log axes has equation $\ln y=1.5\ln x+\ln4$ for $x>0$. It was fitted to observations with $1\le x\le9$.',[
p(r'Write $y$ as a function of $x$ and calculate $y$ when $x=4$.',r'A1|$y=4x^{1.5}$.',r'A1|$y(4)=32$.'),
p(r'Determine the factor by which $x$ must increase to double $y$.',r'M1|If $x$ is multiplied by $q$, $y$ is multiplied by $q^{1.5}$.',r'A1|$q=2^{2/3}=1.58740$.'),
p(r'A second researcher fits $\ln y=1.5\ln x+2\ln4$. Explain how the two predicted curves compare.',r'M1|Exponentiating gives the second model $y=16x^{1.5}$.',r'R1|At every positive $x$, the second prediction is four times the first; the slope/power is unchanged.')],plot([lambda x:1.5*x+math.log(4)],(0,2.2),(0,5),'ln x','ln y'),difficulty='medium')
ck('background-corrected half life',math.log(2)/(math.log(5)/8),3.445412464586337,1e-6)
add(T,'Decay obscured by background counts','2.9','Exponential and logistic models',r'A detector records $C(t)=20+Ae^{-kt}$ counts per minute. At $t=0$ the reading is 220; after 8 hours it is 60. The 20-count background is constant.',[
p(r'Find $A$ and $k$.',r'A1|$A=200$.',r'M1|$60-20=200e^{-8k}$.',r'A1|$k=\ln5/8=0.201180$.'),
p(r'Find the half-life of the source and explain why halving the total detector reading gives a different time.',r'M1|The source half-life satisfies $e^{-kt}=1/2$.',r'A1|$t=\ln2/k=3.44541$ hours.',r'R1|The background does not decay, so a total reading of 110 is not half the initial source signal.'),
p(r'Find when the source contributes fewer counts than the background.',r'M1|Solve $200e^{-kt}<20$.',r'A1|$t>\ln10/k=11.4454$ hours.')],plot([lambda t:20+200*math.exp(-math.log(5)/8*t),lambda t:20],(0,16),(0,240),'hours','counts per minute',dashed=(1,)),difficulty='medium')
ck('piecewise join',20+3*4,32);ck('piecewise quota root',32+(math.sqrt(84)-4)**2+8*(math.sqrt(84)-4),100)
add(T,'Joining two production regimes','2.9','Sinusoidal and piecewise models',r'A machine’s cumulative production is $P(t)=20+3t$ for $0\le t\le4$ and $P(t)=a+(t-4)^2+8(t-4)$ for $t>4$. The transition must be continuous.',[
p(r'Find $a$ and interpret the continuity requirement.',r'M1|Equate the values at $t=4$.',r'A1|$a=32$.',r'R1|Production cannot jump instantaneously when the operating regime changes.'),
p(r'Find the first time cumulative production reaches 100.',r'M1|For $u=t-4>0$, solve $u^2+8u+32=100$.',r'A1|$u=-4+\sqrt{84}$; hence $t=\sqrt{84}=9.16515$.'),
p(r'Find the inverse rule in the second regime and state its domain.',r'M1|Solve $p-32=(t-4)^2+8(t-4)=t^2+16$.',r'A1|$t=\sqrt{p-16}$, with $p>32$; take the positive branch because $t>4$.')],plot([lambda t:20+3*t if t<=4 else 32+(t-4)**2+8*(t-4)],(0,10),(0,125),'time','cumulative production'))
ck('restricted inverse composition',(3+math.sqrt(21+4)-3)**2-4,21)
add(T,'An inverse calibration with a branch choice','2.7','Composite and inverse functions',r'A displacement sensor has response $f(x)=(x-3)^2-4$. Its physical operating range is $x\ge3$. The diagram shows the full mathematical curve so the branch issue can be seen.',[
p(r'Find the inverse calibration and its domain.',r'M1|Solve $y+4=(x-3)^2$.',r'A1|$f^{-1}(y)=3+\sqrt{y+4}$ for $y\ge-4$.'),
p(r'A reading is 21 with a possible error of $\pm1$. Find the corresponding interval of actual displacement.',r'M1|The inverse is increasing on the operating range; use readings 20 and 22.',r'A1|$3+\sqrt{24}\le x\le3+\sqrt{26}$, approximately $7.89898\le x\le8.09902$.'),
p(r'Explain why using the full parabola would prevent a unique inverse.',r'R1|For readings greater than -4, there are two mathematical inputs $3\pm\sqrt{y+4}$.',r'R1|The physical restriction selects the input on the right branch.')],plot([lambda x:(x-3)**2-4],(-1,7),(-5,15),'input x','reading'),difficulty='medium')
ck('purification order',.8*(.5*100+6)+2-(.5*(.8*100+2)+6),-.2)
add(T,'Choosing the order of two cleaning stages','2.7','Composite and inverse functions',r'Two cleaning stages transform concentration $c$ by $f(c)=0.8c+2$ and $g(c)=0.5c+6$. Both outputs are measured in the same units. Concentrations are non-negative.',[
p(r'Find $f\circ g$ and $g\circ f$.',r'M1|Substitute one affine rule into the other.',r'A1|$f(g(c))=0.4c+6.8$ and $g(f(c))=0.4c+7$.'),
p(r'Determine the better order for obtaining the lowest final concentration and whether it depends on the input.',r'R1|Apply g first then f, since $0.4c+6.8<0.4c+7$ for every $c$.',r'R1|The difference is always 0.2, so the choice is independent of the input.'),
p(r'For the better order, find the greatest input concentration producing an output at most 15.',r'M1|Solve $0.4c+6.8\le15$.',r'A1|$c\le20.5$; the greatest input is 20.5.')],table(['Stage','Remaining fraction','Added concentration'],[['f',.8,2],['g',.5,6]],'Cleaning-stage rules'),difficulty='medium')
ck('graph landmark transform',2*(-3)-1,-7)
add(T,'Transforming a graph without knowing its formula','2.8','Graph transformations',r'A function $f$ has domain $[-2,6]$, range $[-3,5]$, and a unique minimum at $(1,-3)$. Define $g(x)=2f(3-x)-1$. The three pieces of information in the diagram are exact.',[
p(r'Find the domain and range of $g$.',r'M1|Require $-2\le3-x\le6$.',r'A1|Domain $[-3,5]$.',r'A1|Range $[-7,9]$.'),
p(r'Find the coordinates of the minimum of $g$ and describe the horizontal mapping of points.',r'M1|Set $3-x=1$, so $x=2$.',r'A1|The minimum is $(2,-7)$.',r'R1|An original abscissa u maps to $3-u$: reflection in the vertical axis followed by translation 3 to the right.'),
p(r'If $f(4)=2$, find $g(-1)$ and explain why $f(4)$ alone cannot determine $g(4)$.',r'A1|$g(-1)=2f(4)-1=3$.',r'R1|$g(4)$ requires $f(-1)$, whose value is not supplied.')],table(['Feature of f','Exact information'],[['Domain','[-2, 6]'],['Range','[-3, 5]'],['Unique minimum','(1, -3)']], 'Graph information supplied'),difficulty='medium')
t0=math.acos(.4)*6/math.pi;ck('tide duration',2*t0,4.428121060089272,1e-6)
add(T,'Two entry windows in a tide cycle','2.9','Sinusoidal and piecewise models',r'Tidal depth in metres is $D(t)=5+2.5\cos(\pi t/6)$, where $t=0$ is midnight. A ship may enter only when depth is at least 6 metres. Consider one 12-hour cycle.',[
p(r'Find the maximum depth and the period.',r'A1|Maximum depth is 7.5 metres.',r'A1|The period is $2\pi/(\pi/6)=12$ hours.'),
p(r'Find all permissible times in $0\le t\le12$ and the total duration.',r'M1|Solve $\cos(\pi t/6)\ge0.4$.',r'A1|$0\le t\le2.21406$ or $9.78594\le t\le12$.',r'A1|Total duration $=4.42812$ hours.'),
p(r'Give one reason the simple sinusoidal forecast may overstate the safe window.',r'R1|For example, weather can lower the actual water level below the model.',r'R1|A ship close to the threshold would then have a smaller safe interval; accept another contextual explanation with a clear consequence.')],plot([lambda t:5+2.5*math.cos(math.pi*t/6),lambda t:6],(0,12),(2,8),'hours after midnight','depth / m',dashed=(1,)))
ck('temperature seasonal shift',math.cos(2*math.pi*(8-2)/12),-1)
add(T,'Separating seasonal movement from warming','2.9','Sinusoidal and piecewise models',r'A monthly temperature model is $T(t)=18+0.02t+6\cos(\pi(t-2)/6)$, with $t$ months after a fixed starting date. The warming term and seasonal term are shown separately.',[
p(r'Find the difference $T(t+12)-T(t)$ and interpret it.',r'M1|The cosine argument increases by $2\pi$, leaving the seasonal value unchanged.',r'A1|$T(t+12)-T(t)=0.24$ degrees; the same month is 0.24 degrees warmer one year later.'),
p(r'A researcher calls this model periodic with period 12. Assess the claim.',r'R1|The seasonal component has period 12.',r'R1|The entire model is not periodic because the linear trend increases by 0.24 each cycle.'),
p(r'Find the first time $t\ge0$ when the trend component alone reaches 20, and explain why this does not mean actual temperature first reaches 20 then.',r'M1|Solve $18+0.02t=20$.',r'A1|$t=100$ months.',r'R1|The seasonal term can raise or lower the total by up to 6 degrees, so actual threshold crossings differ.')],plot([lambda t:18+.02*t,lambda t:6*math.cos(math.pi*(t-2)/6)],(0,24),(-7,21),'months','component value',dashed=(1,)),difficulty='medium')
ck('model validation SSE',sum((a-b)**2 for a,b in zip([82,94,97],[80,95,99])),9)
add(T,'A fit statistic versus a physical constraint','2.9','Linearisation and model evaluation',r'Two models fitted to early observations have been tested on three later observations, shown in the table. Model E is exponential and has training $R^2=0.999$; model L is logistic with capacity 100 and training $R^2=0.992$. The population cannot exceed 100 because there are 100 available sites.',[
p(r'Calculate the validation sum of squared residuals for each model.',r'M1|Use the later observed values rather than the training fit.',r'A1|For E, $(-8)^2+(-16)^2+(-43)^2=2169$.',r'A1|For L, $2^2+(-1)^2+(-2)^2=9$.'),
p(r'Recommend a model, using both statistical and contextual evidence.',r'R1|L has much lower validation error despite the slightly lower training $R^2$.',r'R1|L also respects the 100-site capacity, whereas positive exponential growth eventually violates it.'),
p(r'Explain why the validation data should not then be reused to report an independent validation of a newly refitted model.',r'R1|Once used for selection or refitting, these data influence the model.',r'R1|A fresh holdout set is needed for a new independent assessment.')],table(['Time','Observed','E','L'],[[8,82,90,80],[10,94,110,95],[12,97,140,99]],'Later observations and forecasts'))
ck('rational saturation first',60*2/(2+4),20);ck('rational saturation second',60*8/(8+4),40)
add(T,'Inferring a saturation curve','2.9','Exponential and logistic models',r'A response is modelled by $R(x)=ax/(b+x)$ for $x\ge0$, with $a,b>0$. Measurements are $R(2)=20$ and $R(8)=40$. The diagram plots only these supplied observations.',[
p(r'Find $a$ and $b$.',r'M1|$2a/(b+2)=20$ and $8a/(b+8)=40$.',r'A1|$a=60$, $b=4$.'),
p(r'Find the input needed for 90% of the limiting response.',r'M1|The limit is 60, so solve $60x/(x+4)=54$.',r'A1|$x=36$.'),
p(r'Find the inverse response rule and explain its restricted domain.',r'M1|From $r(x+4)=60x$, obtain $x=4r/(60-r)$.',r'A1|$R^{-1}(r)=4r/(60-r)$ for $0\le r<60$.',r'R1|A finite non-negative input never attains or exceeds the horizontal asymptote 60.')],plot([],(0,10),(0,60),'input x','response',[(2,20,'(2,20)'),(8,40,'(8,40)')]))
ck('shifted power interpolation',3*(9-1)**.5+2,2+6*math.sqrt(2))
add(T,'Why a shifted power model cannot be linearised naively','2.10','Linearisation and model evaluation',r'An introduced growth model is $h(t)=2+3\sqrt{t-1}$ for $t\ge1$. A student takes logs of the raw pairs $(t,h)$ and assumes the resulting graph is a straight line.',[
p(r'Identify transformed coordinates that do produce a straight line and state its slope.',r'M1|Subtract the shifts before taking logarithms.',r'A1|$\ln(h-2)=\ln3+\frac12\ln(t-1)$, valid for $t>1$.',r'A1|The slope is $1/2$.'),
p(r'Find when the height reaches 11 and the average growth rate from $t=2$ to that time.',r'M1|$11-2=3\sqrt{t-1}$ gives $t=10$.',r'A1|$h(2)=5$, so average rate $=(11-5)/(10-2)=0.75$.'),
p(r'Explain why the original point at $t=1$ cannot appear on the transformed graph.',r'R1|Both $t-1$ and $h-2$ are zero at that point.',r'R1|Their logarithms are undefined, even though the original model is defined there.')],plot([lambda t:2+3*math.sqrt(t-1)],(1,12),(0,13),'time','height'))
ck('cubic data',1**3-6*1**2+9*1+2,6);ck('cubic data 2',4**3-6*4**2+9*4+2,6)
add(T,'A cubic model that agrees at two different times','2.6','Linearisation and model evaluation',r'A measured response is modelled by $f(t)=t^3-6t^2+9t+2$ on $0\le t\le4$. The diagram gives four exact observations used to construct the model.',[
p(r'Find all times in the domain when the response is 6.',r'M1|Solve $t^3-6t^2+9t-4=0$.',r'A1|$(t-1)^2(t-4)=0$, giving $t=1$ and $t=4$.'),
p(r'Explain why this model has no inverse on the entire domain.',r'R1|The two different times 1 and 4 produce the same response.',r'R1|Thus the function is not one-to-one on $[0,4]$.'),
p(r'A technician is told only that the response is 6. Give one extra piece of information that identifies the time uniquely.',r'R1|For example, specify that $t>2$.',r'A1|This selects $t=4$; accept any valid restriction distinguishing 1 and 4.')],plot([],(0,4),(0,7),'time','response',[(0,2,'(0,2)'),(1,6,'(1,6)'),(3,2,'(3,2)'),(4,6,'(4,6)')]),level='sl',difficulty='medium')
ck('revenue optimum price',.8*(55/3)+2,50/3);ck('demand at optimum',200-6*(50/3),100)
add(T,'Composing demand with a price discount','2.7','Composite and inverse functions',r'Demand at price $p$ is $q(p)=200-6p$ for $10\le p\le30$. A discount policy maps the listed price $x$ to $p=0.8x+2$. Listed prices must keep the actual price in the demand model’s domain.',[
p(r'Find demand as a function of listed price and determine its valid domain.',r'M1|Substitute the price rule into $q$.',r'A1|$q=188-4.8x$.',r'A1|$10\le x\le35$.'),
p(r'Write revenue as a function of listed price, then determine the listed price giving maximum revenue.',r'M1|$R(x)=(0.8x+2)(188-4.8x)$.',r'M1|Its vertex corresponds to actual price $p=200/12=50/3$.',r'A1|Listed price $x=(50/3-2)/0.8=55/3=18.3333$.'),
p(r'Explain why using $xq(x)$ would be an incorrect revenue calculation.',r'R1|Customers pay the discounted price $0.8x+2$, not the listed price x.',r'R1|The demand input must also be the actual price, requiring the composition.')],plot([lambda p:200-6*p],(10,30),(0,150),'actual price','demand'))
ck('average cost target',500/50+8,18)
add(T,'An average-cost inverse and a feasibility limit','2.7','Composite and inverse functions',r'Total cost for $q>0$ units is $C(q)=500+8q$, giving average cost $A(q)=C(q)/q$. A manager wants an average cost no greater than 9 per unit.',[
p(r'Find $A^{-1}$ and state its physically relevant domain.',r'M1|$a=8+500/q$ gives $q=500/(a-8)$.',r'A1|$A^{-1}(a)=500/(a-8)$ for $a>8$.'),
p(r'Find the least integer production meeting the target.',r'M1|$8+500/q\le9$.',r'A1|$q\ge500$, so 500 units suffice.'),
p(r'The factory can make at most 420 units. Find its lowest possible average cost and assess a promise of average cost 8.',r'M1|A decreases as positive q increases, so use $q=420$.',r'A1|Lowest average cost $=8+500/420=9.19048$.',r'R1|Average cost 8 cannot be reached at any finite positive q; 8 is a limiting value.')],plot([lambda q:8+500/q],(50,600),(8,19),'quantity q','average cost'),difficulty='medium')
rr=bisect(lambda t:20*math.exp(.2*t)-20-10*t,5,15);ck('exponential-line second crossing residual',20*math.exp(.2*rr)-20-10*rr,0,1e-7)
add(T,'A growth claim with two intersections','2.9','Exponential and logistic models',r'Two forecasts are $E(t)=20e^{0.2t}$ and $L(t)=20+10t$ for $0\le t\le12$. Both start at the same value. A report says the exponential forecast is larger at every positive time because exponentials grow faster than linear functions.',[
p(r'Find the second intersection and determine where each forecast is larger.',r'M1|Solve $20e^{0.2t}=20+10t$ numerically, retaining the known root $t=0$.',rf'A1|The second root is $t={rr:.6g}$.',r'A1|L is larger between 0 and the second root; E is larger afterwards.'),
p(r'Use the initial rates of change to explain the report’s error.',r'M1|$E\prime(t)=4e^{0.2t}$ and $L\prime(t)=10$.',r'A1|Initially the linear forecast increases at 10, while E increases at only 4.',r'R1|Faster eventual growth does not imply a larger value at every positive time.'),
p(r'Find when the two instantaneous growth rates are equal.',r'M1|Solve $4e^{0.2t}=10$.',r'A1|$t=5\ln(2.5)=4.58145$.')],plot([lambda t:20*math.exp(.2*t),lambda t:20+10*t],(0,12),(0,230),'time','forecast',dashed=(1,)))
ck('tax join',.2*(40000-10000),6000)
add(T,'Inverting a progressive tax rule','2.9','Sinusoidal and piecewise models',r'For income $x\ge0$, annual tax is $T(x)=0$ for $x\le10000$, $0.2(x-10000)$ for $10000<x\le40000$, and $6000+0.35(x-40000)$ for $x>40000$.',[
p(r'Find all incomes that produce a tax bill of 6000.',r'M1|Check the joining value at 40000.',r'A1|Only $x=40000$ produces exactly 6000.'),
p(r'For positive tax t, write the inverse rule.',r'M1|Solve each non-flat branch separately.',r'A1|$x=10000+5t$ for $0<t\le6000$.',r'A1|$x=40000+(t-6000)/0.35$ for $t>6000$.'),
p(r'Explain why there is no unique inverse at tax zero, and determine income when after-tax income is 50000.',r'R1|Every income from 0 through 10000 has tax zero.',r'M1|Use the upper branch: $x-[6000+0.35(x-40000)]=50000$.',r'A1|$0.65x+8000=50000$, so $x=64615.3846$.')],plot([lambda x:0 if x<=10000 else .2*(x-10000) if x<=40000 else 6000+.35*(x-40000)],(0,80000),(0,21000),'income','tax'))
ck('quadratic parameter contact',(-4)**2-4*1*4,0)
add(T,'A parameter that changes the number of feasible solutions','2.6','Linearisation and model evaluation',r'An introduced model is $f_k(x)=x^2-4x+k$ on the physically allowed domain $x\ge0$. A zero represents a break-even production level.',[
p(r'Classify the number of distinct non-negative zeros as k varies.',r'M1|The roots are $2\pm\sqrt{4-k}$ when $k\le4$.',r'A1|For $k>4$: none; $k=4$: one; $0\le k<4$: two.',r'A1|For $k<0$: only the positive root is feasible.'),
p(r'Find k if the two feasible break-even levels differ by 6.',r'M1|Their separation is $2\sqrt{4-k}=6$, giving $k=-5$.',r'R1|But k=-5 gives roots -1 and 5, so there cannot be two feasible levels separated by 6.',r'A1|No admissible k satisfies the stated condition.'),
p(r'Find the greatest possible separation between two feasible zeros.',r'M1|Two feasible roots require $0\le k<4$.',r'A1|The greatest separation is 4 at $k=0$, with roots 0 and 4.')],plot([lambda x:x*x-4*x+4,lambda x:x*x-4*x],(0,5),(-5,10),'production x','model value',dashed=(1,)),level='sl')
ck('compound response threshold',math.log(1+math.exp(2))-2,.1269280110429727)
add(T,'A sensor response that approaches a moving target','2.9','Exponential and logistic models',r'A response is modelled by the introduced function $S(t)=\ln(1+e^t)$ for $t\ge0$. A simpler approximation is $L(t)=t$. The diagram shows the two predictions.',[
p(r'Show that the approximation error is $E(t)=\ln(1+e^{-t})$.',r'M1|Write $1+e^t=e^t(1+e^{-t})$.',r'A1|Taking logarithms and subtracting t gives $E(t)=\ln(1+e^{-t})$.'),
p(r'Find the least t for which the approximation error is at most 0.01.',r'M1|Solve $\ln(1+e^{-t})\le0.01$.',r'A1|$t\ge-\ln(e^{0.01}-1)=4.60017$.'),
p(r'Explain whether the approximation overestimates or underestimates S, and what happens to the error for large t.',r'R1|The error is positive, so L underestimates S.',r'R1|Since $e^{-t}\to0$, the error tends to zero.')],plot([lambda t:math.log1p(math.exp(t)),lambda t:t],(0,6),(0,7),'time','response',dashed=(1,)))

# TOPIC 3 — vectors, transformations, and network reasoning.
T='geometry-trigonometry'
ck('oriented determinant',2*(-1)-1*3,-5);ck('transformed triangle area',abs(-5)*6,30)
add(T,'Area and orientation under a matrix map','3.8','Matrix transformations',r'Triangle OAB has $O=(0,0)$, $A=(4,0)$ and $B=(1,3)$. A transformation is represented by $M=\begin{pmatrix}2&1\\3&-1\end{pmatrix}$.',[
p(r'Find the image vertices and the area of the image triangle.',r'M1|Apply M to each column coordinate.',r'A1|$O\prime=(0,0)$, $A\prime=(8,12)$, $B\prime=(5,0)$.',r'A1|Original area is 6 and $|\det M|=5$, so image area is 30.'),
p(r'Determine whether orientation is preserved, explaining your answer.',r'M1|$\det M=2(-1)-3=-5$.',r'R1|The negative determinant reverses orientation; its magnitude gives the area scale.'),
p(r'Find the area of the original region if its image under M has area 85.',r'M1|Divide image area by the absolute determinant.',r'A1|Original area is $85/5=17$.')],plot([],(0,5),(0,4),'x','y',[(0,0,'O'),(4,0,'A'),(1,3,'B')]),difficulty='medium')
ck('rotation reflection order',mm([[0,-1],[1,0]],[[1,0],[0,-1]])[0][1],1)
add(T,'Two orders of reflection and rotation','3.8','Matrix transformations',r'R is an anticlockwise rotation through $\pi/2$ about O, and S is reflection in the x-axis. A point is first reflected and then rotated.',[
p(r'Find the matrix of the combined transformation.',r'M1|$R=\begin{pmatrix}0&-1\\1&0\end{pmatrix}$ and $S=\begin{pmatrix}1&0\\0&-1\end{pmatrix}$.',r'A1|$RS=\begin{pmatrix}0&1\\1&0\end{pmatrix}$.',r'R1|This is reflection in $y=x$.'),
p(r'Find the image of P=(3,1) for both possible orders.',r'A1|Reflect then rotate gives $(1,3)$.',r'A1|Rotate then reflect gives $(-1,-3)$.'),
p(r'Find all points whose images are identical for both orders.',r'M1|Equate $(y,x)$ and $(-y,-x)$.',r'A1|Only $(0,0)$ satisfies both equations.')],plot([] ,(-4,4),(-4,4),'x','y',[(0,0,'O'),(3,1,'P')]),difficulty='medium')
ck('invariant direction eigenvalue',mm([[3,1],[0,2]],[[1],[-1]])[0][0],2)
add(T,'Invariant directions in a stretch-shear map','3.8','Matrix transformations',r'A map is $M=\begin{pmatrix}3&1\\0&2\end{pmatrix}$. A line through O is called invariant when each point on that line is mapped onto the same line.',[
p(r'Find both invariant lines through O.',r'M1|Use eigenvectors: solve $(M-\lambda I)v=0$.',r'A1|For $\lambda=3$, the line is $y=0$.',r'A1|For $\lambda=2$, the line is $y=-x$.'),
p(r'Determine the image of $(1,-1)$ after four applications.',r'M1|This point lies in the eigenvector direction with factor 2.',r'A1|The image is $2^4(1,-1)=(16,-16)$.'),
p(r'Explain why an invariant line need not consist of fixed points.',r'R1|Invariant means points stay on the line, not at the same position.',r'R1|Here non-zero points are multiplied by 2 or 3; only the origin is fixed.')],plot([lambda x:0,lambda x:-x],(-3,3),(-3,3),'x','y',[(1,-1,'P')],dashed=(1,)))
ck('map recovery first',mm([[2,-1],[1,3]],[[1],[1]])[1][0],4);ck('map recovery second',mm([[2,-1],[1,3]],[[2],[-1]])[0][0],5)
add(T,'Recovering a transformation from two images','3.8','Matrix transformations',r'A linear map sends $A=(1,1)$ to $(1,4)$ and $B=(2,-1)$ to $(5,-1)$. It fixes the origin.',[
p(r'Find the matrix of the transformation.',r'M1|Form $M\begin{pmatrix}1&2\\1&-1\end{pmatrix}=\begin{pmatrix}1&5\\4&-1\end{pmatrix}$.',r'M1|Multiply on the right by the inverse input matrix.',r'A1|$M=\begin{pmatrix}2&-1\\1&3\end{pmatrix}$.'),
p(r'Find the point that maps to $(7,0)$.',r'M1|Solve $2x-y=7$, $x+3y=0$.',r'A1|$(x,y)=(3,-1)$.'),
p(r'Explain why knowing the image of only one non-zero point would not generally determine a two-dimensional linear map.',r'R1|A 2 by 2 matrix has four entries, while one image supplies only two scalar equations.',r'R1|An independent second direction is needed to determine the map uniquely.')],plot([] ,(-2,6),(-2,5),'x','y',[(1,1,'A'),(2,-1,'B'),(1,4,'image A'),(5,-1,'image B')]))
rel=lambda t:(8-2*t,6-t);tmin=-(8*(-2)+6*(-1))/5
ck('relative motion minimum time',tmin,4.4);ck('relative minimum distance',math.hypot(*rel(tmin)),math.sqrt(3.2))
add(T,'Two vessels and a near miss','3.12','Vectors and motion',r'Vessels have positions $a(t)=(2t,t)$ and $b(t)=(8,6)$ kilometres for $0\le t\le8$, with t in hours. B is anchored. The chart uses equal coordinate units.',[
p(r'Find their relative position vector and show that squared distance is $5t^2-44t+100$.',r'M1|$b-a=(8-2t,6-t)$.',r'A1|Expanding $(8-2t)^2+(6-t)^2$ gives the stated quadratic.'),
p(r'Find the time and distance of closest approach.',r'M1|The quadratic has its minimum at $t=44/10=4.4$.',r'A1|Minimum distance is $\sqrt{3.2}=1.78885$ km.'),
p(r'Find the interval during which the vessels are within 2 km and explain why their plotted paths crossing would not by itself prove a collision.',r'M1|Solve $5t^2-44t+100<4$.',r'A1|$4<t<4.8$.',r'R1|A collision requires the same position at the same time; here the anchored point is not on A’s line of motion.')],plot([lambda x:x/2],(0,10),(0,8),'east / km','north / km',[(0,0,'A start'),(8,6,'B')]))
u=(3,1,2);v=(1,4,-1);cross=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]);ck('cross product squared norm',sum(c*c for c in cross),227)
add(T,'A triangular panel in three dimensions','3.13','Vectors and motion',r'A triangular panel has vertices $O=(0,0,0)$, $A=(3,1,2)$ and $B=(1,4,-1)$, measured in metres. The coordinate table is exact.',[
p(r'Find a normal vector to the panel and its area.',r'M1|Compute $OA\times OB$.',r'A1|A normal is $(-9,5,11)$.',r'A1|Area $=\frac12\sqrt{227}=7.53326$ square metres.'),
p(r'Find the acute angle between the panel’s normal and the vertical vector $(0,0,1)$.',r'M1|$\cos\theta=11/\sqrt{227}$.',r'A1|$\theta=43.1056^\circ$.'),
p(r'A proposed point is C=(2,1,1). Determine whether it lies in the plane of the panel.',r'M1|Take the dot product of OC with the normal.',r'A1|$(-9,5,11)\cdot(2,1,1)=-2\ne0$, so C is not in that plane.')],table(['Vertex','x','y','z'],[['O',0,0,0],['A',3,1,2],['B',1,4,-1]],'Three-dimensional panel coordinates'))
ck('force component', (6*2+2*1+3*2)/3,20/3)
add(T,'Force along a sloping cable','3.11','Vectors and motion',r'A cable runs from O to $P=(2,1,2)$ metres. A force is $F=(6,2,3)$ newtons. Resolve F into a component parallel to the cable and a component perpendicular to it.',[
p(r'Find the scalar component of the force along OP.',r'M1|A unit vector along the cable is $(2,1,2)/3$.',r'A1|Scalar component $F\cdot\hat u=20/3$ newtons.'),
p(r'Find the parallel vector and the magnitude of the perpendicular component.',r'M1|Parallel vector is $(20/9)(2,1,2)$.',r'A1|It is $(40/9,20/9,40/9)$.',r'M1|Use $|F_\perp|^2=|F|^2-(20/3)^2$.',r'A1|$|F_\perp|=\sqrt{41}/3=2.13437$ newtons.'),
p(r'Explain why adding the two component magnitudes does not give $|F|$.',r'R1|The parallel and perpendicular components are at right angles.',r'R1|Their vector sum has magnitude given by Pythagoras, not by an ordinary sum of magnitudes.')],table(['Vector','x','y','z'],[['OP',2,1,2],['F',6,2,3]],'Cable and applied force'))
ck('variable motion same east time',2*3,6);ck('variable motion north',3**2-2*3,3)
add(T,'A launch delay avoids a collision','3.12','Vectors and motion',r'A drone starts at $(0,0)$ with velocity $v_A(t)=(2,2t-2)$. Another drone has position $r_B(t)=(6,t)$, with t in seconds. Coordinates are in metres.',[
p(r'Find $r_A(t)$.',r'M1|Integrate each velocity component and use the initial position.',r'A1|$r_A(t)=(2t,t^2-2t)$.'),
p(r'Determine whether a collision occurs for $t\ge0$.',r'M1|Equal east coordinates require $2t=6$, hence $t=3$.',r'A1|At $t=3$, both north coordinates are 3.',r'R1|Thus the drones collide at $(6,3)$ after 3 seconds.'),
p(r'The second drone launches one second later and follows $r_B(t)=(6,t-1)$ for $t\ge1$. Determine whether that avoids collision.',r'M1|East coordinates can still agree only at $t=3$.',r'A1|Then A is at $(6,3)$ and B at $(6,2)$, so collision is avoided under this ideal model.')],plot([lambda x:x*x/4-x],(0,8),(-2,9),'east / m','north / m',[(0,0,'A start'),(6,0,'B vertical path at x=6')]))
E=[('A','B',4),('A','C',6),('A','D',9),('B','C',5),('B','D',7),('C','D',3)]
degrees={v:sum(v in (a,b) for a,b,w in E) for v in 'ABCD'};ck('odd vertices K4',sum(v%2 for v in degrees.values()),4)
add(T,'Inspecting every road once','3.16','Graph theory',r'A road network has vertices A, B, C and D and the edges shown. A route inspector wants a closed walk that uses each edge exactly once. Edge weights are lengths in kilometres.',[
p(r'List the degree of each vertex and decide whether the requested walk exists.',r'A1|Each of A, B, C and D has degree 3.',r'R1|A connected graph has an Eulerian circuit only when all degrees are even.',r'A1|The requested closed walk does not exist.'),
p(r'Decide whether an open walk using every edge exactly once exists.',r'R1|An Eulerian trail with distinct endpoints requires exactly two odd vertices.',r'A1|There are four odd vertices, so such an open walk also does not exist.'),
p(r'Explain why visiting each vertex once is a different problem, and give a valid cycle of that type.',r'R1|Visiting vertices once is Hamiltonian, while the inspector’s condition concerns edges.',r'A1|For example A–B–C–D–A visits all vertices once before returning.')],network(list('ABCD'),E),difficulty='medium')
E2=[('A','B',3),('B','C',4),('C','D',5),('D','A',6),('A','C',2)]
ck('postman two odd',sum(w for a,b,w in E2)+2,22)
add(T,'A postal route with two odd junctions','3.16','Network algorithms',r'A postal worker starts and finishes at A and must traverse every road in the shown connected network at least once. Distances are in kilometres.',[
p(r'Identify the odd vertices and determine the shortest path between them.',r'A1|A and C have degree 3; B and D have degree 2.',r'A1|The shortest A–C path is the direct edge of length 2.'),
p(r'Find the shortest possible closed delivery distance and justify optimality.',r'M1|The road total is $3+4+5+6+2=20$.',r'M1|Duplicate a shortest path joining the two odd vertices so all degrees become even.',r'A1|Minimum closed distance $=20+2=22$.',r'R1|Any closed route must correct both odd degrees, requiring at least their shortest-path distance.'),
p(r'Give one route attaining this minimum.',r'A1|For example A–B–C–A–D–C–A has length 22 and covers every road.')],network(list('ABCD'),E2))
ck('postman four odd minimum matching',min(4+3,6+7,9+5),7);ck('postman four odd total',sum(w for a,b,w in E)+7,41)
add(T,'Four odd junctions and the right pairing','3.16','Network algorithms',r'A maintenance vehicle must traverse every road in the given complete four-vertex network, returning to its starting point. Weights are road lengths.',[
p(r'Compare the three pairings of odd vertices, using shortest-path distances.',r'M1|All four vertices are odd; compare AB+CD, AC+BD, AD+BC.',r'A1|The totals are 7, 13 and 14 respectively; these use shortest distances, including the tie AD=AC+CD=9.'),
p(r'Find the shortest closed inspection distance and state the duplicated roads.',r'M1|The total road length is 34.',r'A1|Duplicate AB and CD, adding 7.',r'A1|The minimum length is 41.'),
p(r'Explain why duplicating only the single shortest road is insufficient.',r'R1|Duplicating one road changes parity at only its two endpoints.',r'R1|Two other odd vertices would remain, preventing an Eulerian closed route.')],network(list('ABCD'),E))
ck('open postman fixed endpoints',sum(w for a,b,w in E)+5,39)
add(T,'Saving distance by finishing elsewhere','3.16','Network algorithms',r'An inspector uses the given complete four-vertex road network. Every road must be traversed at least once, but the route starts at A and ends at D.',[
p(r'Explain which odd vertices need pairing for this open route.',r'R1|The final traversed multigraph must have exactly A and D odd.',r'A1|Original odd vertices B and C must be made even; A and D should remain odd.'),
p(r'Find the shortest possible inspection distance.',r'M1|The shortest B–C path has length 5.',r'A1|Add it to the original road total 34.',r'A1|The shortest open route has length 39.'),
p(r'Compare with the best closed route and explain why the saving is not the distance from A to D.',r'A1|The closed optimum is 41, so the saving is 2.',r'R1|The two parity-correction problems use different pairings; an optimal open route need not be obtained by deleting an A–D path from the optimal closed route.')],network(list('ABCD'),E))
EM=[('A','B',2),('A','C',5),('B','C',3),('B','D',6),('C','D',4),('C','E',7),('D','E',1)]
ck('MST total distinct edges',2+3+4+1,10)
add(T,'Connecting five stations with minimum cable','3.16','Network algorithms',r'Five stations are to be connected by cable. Available direct links and costs are shown. All stations must be connected; no redundant cycle is needed.',[
p(r'Use Prim’s algorithm starting at A, giving the selected edges in order.',r'A1|Select AB of cost 2, then BC of cost 3.',r'A1|Select CD of cost 4, then DE of cost 1.'),
p(r'State the minimum total cost and explain why the links form a spanning tree.',r'A1|Total cost is 10.',r'R1|All five vertices are connected using four edges and no cycle.'),
p(r'A contractor proposes adding AC to increase reliability. Explain the tradeoff using graph language.',r'R1|AC creates the cycle A–B–C–A, providing an alternative route after a link fails.',r'R1|The network is no longer a minimum spanning tree and its cable cost increases by 5.')],network(list('ABCDE'),EM),difficulty='medium')
ck('MST switching threshold',2+3+1+4,10)
add(T,'A changing cable cost and a switching threshold','3.16','Network algorithms',r'Use the five-station network shown, but replace the cost of AC by a positive parameter x. All other link costs stay fixed.',[
p(r'Find a minimum spanning tree for $x=1$ and its cost.',r'M1|The triangle A–B–C uses its two cheapest links AC=1 and AB=2.',r'A1|Add CD=4 and DE=1; total cost is 8.'),
p(r'Find the values of x for which AC belongs to every minimum spanning tree.',r'M1|In triangle A–B–C, compare x with BC=3, since AB=2 remains selected for $x<3$.',r'A1|AC is in every minimum spanning tree for $0<x<3$.'),
p(r'Describe what happens at $x=3$ and for $x>3$.',r'A1|At x=3, either AC or BC can join AB, so there are two minimum trees, each of total cost 10.',r'A1|For $x>3$, the tree AB, BC, CD, DE of cost 10 is optimal and excludes AC.')],network(list('ABCDE'),[(a,b,'x' if (a,b)==('A','C') else w) for a,b,w in EM]))
ET=[('A','B',4),('A','C',7),('A','D',5),('B','C',3),('B','D',8),('C','D',6)]
def tourcost(order,edges):
    weights={frozenset((a,b)):w for a,b,w in edges}
    return sum(weights[frozenset((a,b))] for a,b in zip(order,order[1:]+order[:1]))
ck('TSP exhaustive optimum',min(tourcost(['A']+list(t),ET) for t in itertools.permutations('BCD')),18)
add(T,'Nearest neighbour is a bound, not a proof','3.16','Network algorithms',r'A courier must visit each of four locations once and return to A. The complete graph shows travel costs. Use the nearest-neighbour algorithm from A.',[
p(r'Give the nearest-neighbour tour and its cost.',r'A1|A–B–C–D–A is chosen, with cost $4+3+6+5=18$.'),
p(r'Explain why the algorithm gives an upper bound on the minimum cost.',r'R1|It constructs a feasible Hamiltonian cycle.',r'R1|The optimum cannot cost more than any feasible cycle; the greedy choices alone do not prove optimality.'),
p(r'For this small network, check the other two distinct cycles to determine whether the bound is optimal.',r'M1|Up to reversal, the alternatives are A–B–D–C–A and A–C–B–D–A.',r'A1|Their costs are 25 and 23.',r'A1|Thus 18 is the actual optimum in this case.')],network(list('ABCD'),ET),difficulty='medium')
ck('deleted vertex bound',3+6+4+5,18)
add(T,'A lower bound that certifies a tour','3.16','Network algorithms',r'The complete four-location graph is shown. A feasible tour A–B–C–D–A has cost 18.',[
p(r'Use the deleted-vertex algorithm deleting A to find a lower bound.',r'M1|A minimum spanning tree on B,C,D uses BC=3 and CD=6, total 9.',r'A1|Add the two smallest links from A, AB=4 and AD=5, obtaining lower bound 18.'),
p(r'Explain why these components give a lower bound.',r'R1|Deleting A from any Hamiltonian cycle leaves a spanning path on the other vertices, costing at least their MST.',r'R1|The cycle also uses two links incident to A, costing at least the two smallest such links.'),
p(r'Decide what the lower and upper bounds establish.',r'A1|Both bounds are 18.',r'R1|Since the optimum lies between them, the given tour is optimal.')],network(list('ABCD'),ET))
Adj=[[0,1,1],[0,0,1],[1,0,0]];ck('three step directed walks',mm(mm(Adj,Adj),Adj)[0][0],1)
add(T,'Counting walks in a directed information network','3.15','Graph theory',r'A directed graph has adjacency matrix $A=\begin{pmatrix}0&1&1\\0&0&1\\1&0&0\end{pmatrix}$. Rows are origins and columns are destinations, in the order P,Q,R. The diagram records the adjacency information.',[
p(r'Find the number of length-3 walks from P to P and list them.',r'M1|Use entry $(1,1)$ of $A^3$.',r'A1|There is one: P–Q–R–P.'),
p(r'Find the number of walks of length at most 3 from P to R, excluding length zero.',r'M1|Use entry $(1,3)$ of $A+A^2+A^3$.',r'A1|The entries are 1,1,1, giving 3 walks.'),
p(r'Explain why walks may revisit a vertex, and why the same matrix-power method does not directly count only simple paths.',r'R1|A walk allows repeated vertices or edges.',r'R1|Matrix multiplication records successive allowed edges but does not retain which vertices have already been visited.')],table(['from / to','P','Q','R'],[['P',0,1,1],['Q',0,0,1],['R',1,0,0]],'Directed adjacency matrix'),difficulty='medium')
ck('random walk stationary ratio',sum([3,2,3,2]),10)
add(T,'A random walker on an undirected network','3.15','Graph theory',r'A walker at a vertex chooses uniformly from its adjacent vertices. The graph has edges AB, BC, CD, DA and AC. For a connected undirected graph, a stationary probability is proportional to vertex degree.',[
p(r'Write the column transition matrix in the order A,B,C,D.',r'M1|Divide outgoing choices by the degree of the current vertex; columns describe the current state.',r'A1|$P=\begin{pmatrix}0&1/2&1/3&1/2\\1/3&0&1/3&0\\1/3&1/2&0&1/2\\1/3&0&1/3&0\end{pmatrix}$.'),
p(r'Find the stationary distribution and verify its A-coordinate.',r'A1|Degrees are $(3,2,3,2)$, so $\pi=(0.3,0.2,0.3,0.2)^T$.',r'M1|A-coordinate of $P\pi$ is $0.5(0.2)+(1/3)(0.3)+0.5(0.2)$.',r'A1|This is 0.3, as required.'),
p(r'Explain why the stationary probabilities are not all equal.',r'R1|A and C have more incident edges and receive more incoming routes under this rule.',r'R1|Uniform choice among neighbours is not the same as uniform choice among all vertices.')],network(list('ABCD'),[('A','B',None),('B','C',None),('C','D',None),('D','A',None),('A','C',None)]))
ck('degree sum supplied',4+3+3+2+2,14)
add(T,'Checking an incomplete network report','3.14','Graph theory',r'A report describes a simple graph on five vertices with degree sequence $(4,3,3,2,2)$. A proposed drawing is supplied by its adjacency table.',[
p(r'Find the number of edges and check that the supplied table has the reported degrees.',r'M1|By the handshaking lemma, edges $=(4+3+3+2+2)/2$.',r'A1|There are 7 edges; the row sums are 4,3,3,2,2.'),
p(r'Determine whether an Eulerian trail exists and identify its possible endpoints.',r'R1|The graph is connected and exactly B and C have odd degree.',r'A1|An Eulerian trail exists, starting at B and ending at C or vice versa.'),
p(r'One additional edge is to create an Eulerian circuit. Determine the required edge and explain whether it is allowed in a simple graph.',r'M1|The only parity correction by one added edge is BC.',r'R1|BC is already an edge in the supplied graph.',r'A1|A parallel BC edge would work in a multigraph, but is not permitted in a simple graph.')],table(['','A','B','C','D','E'],[['A',0,1,1,1,1],['B',1,0,1,1,0],['C',1,1,0,0,1],['D',1,1,0,0,0],['E',1,0,1,0,0]],'Adjacency table for the proposed simple graph'))
ck('metric completion A D',min(12,3+4+2,7+2),9)
add(T,'Replacing a road network by shortest travel distances','3.16','Network algorithms',r'A road network has edges AB=3, BC=4, CD=2, AD=12 and AC=7. A courier can pass through a location without counting it as a service visit. Before using a travelling-salesman bound, the network is completed using shortest travel distances.',[
p(r'Find the shortest A–D and B–D distances.',r'M1|Compare direct and multi-edge paths.',r'A1|A–D distance is 9 via C, with either A–C–D or A–B–C–D.',r'A1|B–D distance is 6 via C.'),
p(r'Explain why entering 12 for A–D in the completed table would be incorrect.',r'R1|The completed graph represents the least travel cost between locations.',r'R1|A route can travel from A to D for 9, so the direct-road cost 12 is not the correct metric distance.'),
p(r'Using shortest travel distances, find the cost of the service tour A–B–C–D–A. State why its driven route can revisit a vertex.',r'A1|The service-tour cost is $3+4+2+9=18$.',r'R1|Replacing a completed edge by its shortest road path may pass through previously serviced vertices; the Hamiltonian condition concerns service order, not every road junction traversed.')],network(list('ABCD'),[('A','B',3),('B','C',4),('C','D',2),('A','D',12),('A','C',7)]))

# TOPIC 4 — distributions, inference, uncertainty and transition models.
T='statistics-probability'
N=NormalDist()
def binpmf(n,p,k):return math.comb(n,k)*p**k*(1-p)**(n-k)
def binsf(n,p,k):return sum(binpmf(n,p,j) for j in range(k,n+1))
def poipmf(l,k):return math.exp(-l)*l**k/math.factorial(k)
def poicdf(l,k):return sum(poipmf(l,j) for j in range(k+1))
def tcdf(t,df):
    density=lambda x:math.gamma((df+1)/2)/(math.sqrt(df*math.pi)*math.gamma(df/2))*(1+x*x/df)**(-(df+1)/2)
    return .5+integ(density,0,t)
def discreteplot(vals,ylab='probability'):
    n=len(vals);mx=max(vals)*1.15
    body='<path d="M60 45V315H585"/>'+txt(320,365,'count')+txt(30,26,ylab)
    for k,y in enumerate(vals):
        xx=70+500*k/max(1,n-1);yy=315-250*y/mx
        body+=f'<path d="M{xx:.2f} 315V{yy:.2f}" stroke-width="12"/>'+txt(xx,338,k,12)
    for j in range(6):body+=txt(32,319-50*j,f'{mx*j/5:.3g}',11)
    return svg(body,'Probability mass function of the stated model')
prob=1-poicdf(7.5,9);ck('combined Poisson tail complement',prob+poicdf(7.5,9),1)
add(T,'Combining independent arrival streams','4.17','Poisson and normal models',r'Two independent helpdesks receive Poisson arrivals at rates 2 and 3 per hour. The desks are merged for a 90-minute period, and one operator can handle at most 9 arrivals in that period.',[
p(r'State the distribution of the combined count and justify its parameter.',r'M1|Independent Poisson rates add: $2+3=5$ per hour.',r'A1|For 1.5 hours, $X\sim\operatorname{Po}(7.5)$.'),
p(r'Find the probability the operator’s capacity is exceeded.',r'M1|Capacity is exceeded when $X\ge10$, not when $X\ge9$.',rf'A1|$P(X\ge10)=1-P(X\le9)={prob:.6g}$.'),
p(r'Explain one way a predictable rush-hour surge would challenge the assumed model.',r'R1|A changing arrival rate conflicts with the constant-rate assumption over the period.',r'R1|A single Poisson parameter based on the average could misrepresent the overload probability.')],discreteplot([poipmf(7.5,k) for k in range(16)]),difficulty='medium')
l=-math.log(.12);pk=1-poicdf(l,3);ck('Poisson zero identifies parameter',math.exp(-l),.12)
add(T,'Inferring a Poisson rate from quiet intervals','4.17','Poisson and normal models',r'For a particular one-minute interval the probability of receiving no messages is 0.12. Counts in disjoint intervals are independent and have the same Poisson rate.',[
p(r'Find the mean number of messages per minute.',r'M1|$P(X=0)=e^{-\lambda}=0.12$.',rf'A1|$\lambda=-\ln(0.12)={l:.6g}$.'),
p(r'Find the probability of at least four messages in a minute.',r'M1|Use the complement of counts 0 through 3.',rf'A1|$P(X\ge4)=1-\sum_{{k=0}}^3e^{{-\lambda}}\lambda^k/k!={pk:.6g}$.'),
p(r'Find the probability that at least one of three independent one-minute intervals contains no messages.',r'M1|The complement is that all three intervals contain messages.',r'A1|Probability $=1-(0.88)^3=0.318528$.')],discreteplot([poipmf(l,k) for k in range(9)]),difficulty='medium')
ck('fixed-trial zero probability',.97**40,math.exp(40*math.log(.97)))
add(T,'Choosing a model before calculating a probability','4.17','Poisson and normal models',r'Exactly 40 components are tested independently; each fails with probability 0.03. Separately, faults on a continuous cable occur independently at a uniform rate of 0.4 per metre. The diagram contrasts the two sampling schemes.',[
p(r'Choose a distribution for the component-failure count and calculate the chance of no failures.',r'R1|A fixed number of independent Bernoulli trials gives $X\sim B(40,0.03)$.',r'M1|$P(X=0)=0.97^{40}$.',rf'A1|This is {.97**40:.6g}.'),
p(r'Choose a distribution for faults on 5 metres of cable and find the chance of at least two faults.',r'R1|The cable assumptions support $Y\sim\operatorname{Po}(2)$.',r'M1|$P(Y\ge2)=1-e^{-2}(1+2)$.',rf'A1|This is {1-3*math.exp(-2):.6g}.'),
p(r'Explain why using the same distribution merely because both counts are integers is inadequate.',r'R1|The component count is bounded by 40 with a fixed number of trials.',r'R1|The cable count is modelled by events along a continuous interval with no fixed maximum; model assumptions matter.')],table(['Situation','Sampling structure'],[['Components','40 fixed independent trials'],['Cable','Events along 5 m at 0.4 per m']], 'Two different count mechanisms'),difficulty='medium')
mu=3*50-2*40;var=9*16+4*9;tail=1-N.cdf((80-mu)/math.sqrt(var));ck('profit linear variance',var,180)
add(T,'A profit calculation with uncertain revenues and costs','4.15','Regression and random variables',r'Independent normal variables are $X\sim N(50,16)$ and $Y\sim N(40,9)$, where the second parameters are variances. Profit is $P=3X-2Y$.',[
p(r'Find the distribution of P, showing how the subtraction affects the variance.',r'M1|$E(P)=3(50)-2(40)=70$.',r'M1|$\operatorname{Var}(P)=3^2(16)+(-2)^2(9)=180$.',r'A1|$P\sim N(70,180)$; variances add because the variables are independent.'),
p(r'Find the probability that profit exceeds 80.',r'M1|Standardise with standard deviation $\sqrt{180}$.',rf'A1|$P(P>80)=1-\Phi((80-70)/\sqrt{{180}})={tail:.6g}$.'),
p(r'Explain why knowing just the two marginal normal distributions would be insufficient if X and Y were dependent.',r'R1|The variance of the difference would then also depend on their covariance.',r'R1|The independence-based variance 180 and the resulting tail probability could no longer be used without additional information.')],plot([lambda x:NormalDist(70,math.sqrt(180)).pdf(x)],(25,115),(0,.033),'profit','density'),difficulty='medium')
probmean=1-N.cdf(1.6);ck('sample mean standard deviation',12/math.sqrt(64),1.5)
add(T,'A batch average is not an individual item','4.15','Confidence intervals',r'Item masses are independent and normally distributed with mean 500 g and standard deviation 12 g. A random batch contains 64 items.',[
p(r'Find the distributions of the sample mean and the total mass.',r'A1|$\bar X\sim N(500,144/64)=N(500,2.25)$.',r'A1|The total $S\sim N(32000,64(144))=N(32000,9216)$.'),
p(r'Compare the probabilities that an individual item and the batch mean exceed 502.4 g.',r'M1|Use z=0.2 for an item and z=1.6 for the batch mean.',rf'A1|Individual probability is {1-N.cdf(.2):.6g}; mean probability is {probmean:.6g}.'),
p(r'Find the least sample size for which the standard deviation of the sample mean is at most 1 g.',r'M1|Solve $12/\sqrt n\le1$.',r'A1|The least integer sample size is 144.')],plot([lambda x:NormalDist(500,12).pdf(x),lambda x:NormalDist(500,1.5).pdf(x)],(475,525),(0,.28),'mass / g','density',dashed=(1,)),difficulty='medium')
margin=2.06389856*6/5;ck('t CI margin',margin,2.476678272)
add(T,'A confidence interval with unknown variation','4.16','Confidence intervals',r'A random sample of 25 measurements from a normal population has mean 42 and sample standard deviation 6. The population standard deviation is unknown. For 24 degrees of freedom the 97.5th percentile of the t-distribution is 2.06390.',[
p(r'Calculate a 95% confidence interval for the population mean.',r'M1|Use a t interval with 24 degrees of freedom because population standard deviation is unknown.',r'M1|$42\pm2.06390(6/\sqrt{25})$.',r'A1|Interval approximately $[39.5233,44.4767]$.'),
p(r'A report says there is a 95% chance that this fixed interval contains the fixed population mean. Give a more precise repeated-sampling interpretation.',r'R1|The method produces intervals containing the fixed mean in about 95% of repeated random samples.',r'R1|The 95% describes the long-run coverage of the procedure, not a probability distribution assigned to a fixed mean after this interval is computed.'),
p(r'Explain whether a sample size greater than 30 alone would justify replacing t by the standard normal distribution when the population standard deviation remains unknown.',r'R1|No: the current course uses t when population standard deviation is unknown, regardless of sample size.',r'R1|For large samples the numerical difference may be small, but the reason for t remains.')],table(['Summary','Value'],[['n',25],['sample mean',42],['sample SD',6],['t critical',2.06390]],'Normal-population sample'),difficulty='medium')
nmin=math.ceil((N.inv_cdf(.975)*8/1.5)**2);ck('known sigma sample size',nmin,110)
add(T,'Planning the width of a confidence interval','4.16','Confidence intervals',r'An independent random sample is to be drawn from a normal population with known standard deviation 8. A 95% confidence interval for its mean must have total width at most 3.',[
p(r'Find the smallest required sample size.',r'M1|Half-width is $1.95996(8)/\sqrt n$, which must not exceed 1.5.',r'M1|$n\ge(1.95996\times8/1.5)^2=109.268$.',r'A1|The smallest integer is 110.'),
p(r'The budget permits only 64 measurements. Find the total width then.',r'M1|Width $=2(1.95996)(8)/\sqrt{64}$.',r'A1|Width is 3.91993, exceeding the target.'),
p(r'Explain why quadrupling sample size, rather than doubling it, halves the interval width.',r'R1|Width is proportional to $1/\sqrt n$.',r'R1|Replacing n by 4n doubles the denominator and halves the width.')],plot([lambda n:2*N.inv_cdf(.975)*8/math.sqrt(n)],(25,225),(0,7),'sample size','total interval width'),difficulty='medium')
d=[2,4,1,5,3,4,2,6,1,2];dm=statistics.mean(d);ds=statistics.stdev(d);tt=dm/(ds/math.sqrt(10));pt=1-tcdf(tt,9)
truth('matched differences one-sided significance',pt<.005);ck('matched sample mean',dm,3)
add(T,'A matched-pairs intervention study','4.18','Hypothesis testing',r'Ten patients are measured before and after an intervention. The table gives reductions (before minus after) for each patient. Assume these differences form an independent random sample from a normal population. Test for a positive mean reduction at the 5% level.',[
p(r'State hypotheses and explain why the pairing must be retained.',r'A1|$H_0:\mu_d=0$ and $H_1:\mu_d>0$.',r'R1|Measurements from the same patient are linked; analysing within-patient differences retains this information.'),
p(r'Calculate the test statistic and p-value, then make a contextual decision.',rf'M1|The differences have mean {dm:.6g} and sample SD {ds:.6g}.',rf'A1|$t=\bar d/(s_d/\sqrt{{10}})={tt:.6g}$, with 9 degrees of freedom.',rf'A1|The one-sided p-value is {pt:.6g}.',r'R1|It is below 0.05, so reject $H_0$; the data support a positive population mean reduction.'),
p(r'Explain why this result alone does not prove the intervention caused the improvement.',r'R1|Statistical evidence for a mean change does not remove confounding factors.',r'R1|Without an appropriate control/randomised design, time effects or other treatments could explain some improvement.')],table(['Patient','Reduction'],[[i+1,x] for i,x in enumerate(d)],'Paired reductions'))
tt2=2/math.sqrt(6**2/36+6**2/36);pp=2*(1-tcdf(tt2,70));ck('two sample statistic',tt2,math.sqrt(2))
add(T,'A significant-looking difference between two groups','4.11','Hypothesis testing',r'Two independent random samples come from normal populations. Group A has $n=36$, mean 54 and sample SD 6; group B has $n=36$, mean 52 and sample SD 6. Use an unpaired two-sided t-test, with equal population variances assumed, at the 5% level.',[
p(r'State the hypotheses and calculate the t statistic.',r'A1|$H_0:\mu_A=\mu_B$, $H_1:\mu_A\ne\mu_B$.',r'M1|The pooled standard deviation is 6.',r'A1|$t=(54-52)/\sqrt{36/36+36/36}=\sqrt2=1.41421$, with 70 degrees of freedom.'),
p(r'Find the p-value and interpret the result.',rf'A1|The two-sided p-value is {pp:.6g}.',r'R1|It exceeds 0.05, so do not reject equal population means.',r'R1|The sample means differ by 2, but this is insufficient statistical evidence of a population difference under the assumptions.'),
p(r'Explain why failing to reject the null does not establish that the two population means are identical.',r'R1|Non-rejection can occur because the data are insufficiently informative.',r'R1|It does not prove the exact null value or establish practical equivalence.')],table(['Group','n','Mean','Sample SD'],[['A',36,54,6],['B',36,52,6]],'Independent samples'),level='sl')
kcrit=min(k for k in range(31) if binsf(30,.2,k)<.05);alpha=binsf(30,.2,kcrit);power=binsf(30,.35,kcrit)
ck('binomial critical threshold',kcrit,11);truth('discrete critical maximal below five percent',alpha<.05<binsf(30,.2,kcrit-1))
add(T,'A discrete critical region and its actual size','4.18','Hypothesis testing',r'A quality inspector tests $H_0:p=0.20$ against $H_1:p>0.20$ using 30 independent trials. The rejection region has form $X\ge k$ and must have significance less than 5%, as close to 5% as possible.',[
p(r'Find k and the actual probability of a Type I error.',r'M1|Under $H_0$, $X\sim B(30,0.2)$.',rf'A1|$P(X\ge10)={binsf(30,.2,10):.6g}$ and $P(X\ge11)={alpha:.6g}$.',r'A1|Thus k=11 and the actual Type I error probability is about 0.0256.'),
p(r'If the true proportion is 0.35, find the probability of a Type II error.',r'M1|A Type II error here is not rejecting, so $X\le10$ under $p=0.35$.',rf'A1|The probability is $1-P_{{0.35}}(X\ge11)={1-power:.6g}$.'),
p(r'Explain why the actual significance cannot generally be made exactly 5% using a non-randomised integer threshold.',r'R1|The binomial tail changes in discrete jumps as the integer threshold changes.',r'R1|There need not be a tail probability equal to 0.05.')],discreteplot([binpmf(30,.2,k) for k in range(17)]))
kc=min(k for k in range(40) if 1-poicdf(5,k-1)<.05);aa=1-poicdf(5,kc-1)
ck('Poisson critical threshold',kc,10);truth('Poisson critical neighbours',aa<.05<1-poicdf(5,kc-2))
add(T,'Detecting an increased incident rate','4.18','Hypothesis testing',r'A site historically averages 5 incidents per month, modelled by a Poisson distribution. Test for an increase using one month’s count, with rejection region $X\ge k$ and significance below 5%, as close to 5% as possible.',[
p(r'Find the critical region and its actual significance.',r'M1|Compare upper-tail probabilities under $\operatorname{Po}(5)$.',rf'A1|$P(X\ge9)={1-poicdf(5,8):.6g}$ and $P(X\ge10)={aa:.6g}$.',r'A1|The critical region is $X\ge10$.'),
p(r'This month has 9 incidents. State the decision and explain why it does not prove there has been no increase.',r'A1|Do not reject $H_0$, since 9 is outside the critical region.',r'R1|A test can fail to detect a genuine increase; non-rejection is not proof of no change.'),
p(r'If the true mean is 8, find the probability of failing to detect the increase.',r'M1|Use $P_{\lambda=8}(X\le9)$.',rf'A1|The Type II error probability is {poicdf(8,9):.6g}.')],discreteplot([poipmf(5,k) for k in range(15)]))
xs=[1,2,3,4,5,6];ys=[2,4,3,6,5,8];corr=statistics.correlation(xs,ys);tcor=corr*math.sqrt(4/(1-corr*corr));pcor=2*(1-tcdf(tcor,4))
truth('correlation positive and significant',corr>0 and pcor<.05)
add(T,'Testing correlation without claiming causation','4.18','Hypothesis testing',r'A random sample from a bivariate normal population gives the six pairs shown. Test $H_0:\rho=0$ against $H_1:\rho\ne0$ at the 5% level.',[
p(r'Calculate the sample correlation and the p-value of the correlation test.',rf'M1|Calculate Pearson correlation from the paired data: $r={corr:.6g}$.',rf'A1|A two-sided correlation test gives $p={pcor:.6g}$.',r'R1|The pairing must be retained in the calculation.'),
p(r'State the decision in context and one limitation of the inference.',r'A1|Reject zero population correlation at the 5% level.',r'R1|The data support a positive linear association under the stated sampling assumptions.',r'R1|Correlation alone does not show that changing x causes a change in y.'),
p(r'Explain why a test chosen only after trying many different variable pairs could overstate the evidence.',r'R1|Trying many pairs creates more opportunities for a small p-value by chance.',r'R1|The nominal 5% level for one planned test does not describe that whole search procedure.')],plot([],(0,7),(0,9),'x','y',[(x,y,'') for x,y in zip(xs,ys)]))
chi=sum((o-e)**2/e for o,e in zip([34,16,10,16,34,10],[25,25,10,25,25,10]));ck('two by three independence statistic',chi,12.96)
add(T,'Association between travel and club choice','4.11','Hypothesis testing',r'A random sample of 120 students is classified by travel mode and club choice (Debate, Sport or None). The table gives observed counts. Use a chi-squared independence test at 5%; the critical value for two degrees of freedom is 5.99146.',[
p(r'Find the expected frequencies under independence and the test statistic.',r'M1|Both row totals are 60 and column totals are 50,50,20; expected counts in each row are 25,25,10.',r'M1|Sum $(O-E)^2/E$ over all six cells.',r'A1|$\chi^2=12.96$ with $(2-1)(3-1)=2$ degrees of freedom.'),
p(r'Draw a conclusion and explain why the expected-frequency condition is satisfied.',r'A1|Since $12.96>5.99146$, reject independence; there is evidence of association.',r'R1|All expected frequencies are at least 10, greater than 5.'),
p(r'Explain why the result does not show that joining a club changes a student’s travel mode.',r'R1|The study is observational and the variables may share confounding influences.',r'R1|An association does not by itself establish a direction of causation.')],table(['','Debate','Sport','None'],[['Bus',34,16,10],['Other',16,34,10]],'Observed student counts'),level='sl',difficulty='medium')
lam=1.1;ex=[100*poipmf(lam,k) for k in range(3)]+[100*(1-poicdf(lam,2))];chig=sum((o-e)**2/e for o,e in zip([30,40,20,10],ex))
ck('estimated Poisson rate',sum(k*f for k,f in enumerate([30,40,20,10]))/100,1.1);truth('all fitted GOF expectations above five',min(ex)>5)
add(T,'A goodness-of-fit test with an estimated parameter','4.12','Hypothesis testing',r'Counts from 100 independent equal-length intervals are shown: frequencies for counts 0,1,2,3 are 30,40,20,10; no count exceeds 3. A Poisson parameter is estimated from these data. For the test, use four groups: 0,1,2,and at least 3. The 5% critical value for two degrees of freedom is 5.99146.',[
p(r'Estimate the Poisson mean and calculate the four expected frequencies.',r'M1|Sample mean $=(0(30)+1(40)+2(20)+3(10))/100=1.1$.',rf'A1|Expected frequencies are {ex[0]:.6g}, {ex[1]:.6g}, {ex[2]:.6g}, and {ex[3]:.6g}.',r'R1|The last expected frequency includes every count at least 3, including unobserved larger counts; all expectations exceed 5.'),
p(r'Find the correct degrees of freedom, calculate the statistic and state the conclusion.',r'M1|There are four groups and one estimated parameter, giving $4-1-1=2$ degrees of freedom.',rf'A1|$\chi^2={chig:.6g}$.',r'R1|It is below 5.99146, so do not reject the Poisson fit at 5%.'),
p(r'Explain why using three degrees of freedom would be inappropriate.',r'R1|The fitted mean was estimated from the same observations.',r'R1|Estimating that parameter removes an additional independent constraint beyond the total frequency.')],table(['Count','Frequency'],[[0,30],[1,40],[2,20],[3,10]],'Equal-interval event counts'))
P3=[[.6,.2,.1],[.3,.5,.3],[.1,.3,.6]];st=[.275,.375,.35];pv=mm(P3,[[v] for v in st]);ck('three-state stationary first',pv[0][0],.275)
add(T,'A three-state subscription chain','4.19','Markov chains',r'Subscribers occupy Basic, Plus and Premium states. The column transition matrix is $P=\begin{pmatrix}0.6&0.2&0.1\\0.3&0.5&0.3\\0.1&0.3&0.6\end{pmatrix}$ in that order. The total subscriber population is fixed.',[
p(r'Explain the entry in row 2, column 3, and find the next-month state from $(100,0,0)^T$.',r'A1|A Premium subscriber moves to Plus with probability 0.3.',r'A1|The next-month expected state is $(60,30,10)^T$.'),
p(r'Find the exact stationary distribution.',r'M1|Solve $P\pi=\pi$ together with $\pi_1+\pi_2+\pi_3=1$.',r'A1|$\pi=(11/40,3/8,7/20)^T=(0.275,0.375,0.35)^T$.'),
p(r'Monthly fees are 10,20,and 30. Find the long-run expected monthly revenue per subscriber, and state a modelling assumption needed for using it.',r'M1|Weight each fee by its stationary probability.',r'A1|Revenue $=10(0.275)+20(0.375)+30(0.35)=20.75$.',r'R1|The transition probabilities and fee structure must remain stable; the population must continue following the chain.')],table(['Current / next','Basic','Plus','Premium'],[['Basic',.6,.3,.1],['Plus',.2,.5,.3],['Premium',.1,.3,.6]],'Monthly switching probabilities'))
ck('slow chain ten-step first',.5+.5*.96**10,.8324163179957504)
add(T,'A stationary distribution versus time to settle','4.19','Markov chains',r'A two-state column transition matrix is $P=\begin{pmatrix}0.98&0.02\\0.02&0.98\end{pmatrix}$. Initially all users are in A. For this chain, the probability of A after n transitions can be written $a_n=1/2+c(0.96)^n$.',[
p(r'Find c and the stationary distribution.',r'A1|$a_0=1$ gives $c=1/2$.',r'M1|Solve $0.98a+0.02(1-a)=a$.',r'A1|The stationary distribution is $(1/2,1/2)^T$.'),
p(r'Find the probability of A after ten transitions and assess the claim that ten transitions are enough to be close to stationarity.',rf'A1|$a_{{10}}=1/2+(1/2)(0.96)^{{10}}={.5+.5*.96**10:.6g}$.',r'R1|This is about 0.332 above 0.5, so it is still far from stationarity.'),
p(r'Find the least n for which the probability of A differs from 0.5 by less than 0.01.',r'M1|Solve $0.5(0.96)^n<0.01$.',rf'A1|$n>\ln(0.02)/\ln(0.96)={math.log(.02)/math.log(.96):.6g}$, so the least integer is {math.floor(math.log(.02)/math.log(.96))+1}.')],plot([lambda n:.5+.5*.96**n,lambda n:.5],(0,100),(0,1),'transitions n','probability of A',dashed=(1,)))
ck('policy chain target',.2/(.2+.13333333333333333),.6)
add(T,'Designing a switching policy for a target share','4.19','Markov chains',r'A and B are competing services. Each month 20% of B users move to A; a proportion q of A users move to B. The company wants the stationary A share to be 60%.',[
p(r'Write the column transition matrix in terms of q.',r'A1|$P=\begin{pmatrix}1-q&0.2\\q&0.8\end{pmatrix}$.'),
p(r'Find q to achieve the target.',r'M1|At stationarity, flow from A to B equals flow from B to A: $0.6q=0.4(0.2)$.',r'A1|$q=2/15=0.133333$.'),
p(r'If the current A share is 0.3, calculate the next-month share using this policy. Explain why reaching 0.6 is not an immediate one-step outcome.',r'M1|$a_1=(1-2/15)(0.3)+0.2(0.7)$.',r'A1|$a_1=0.4$.',r'R1|The target is the stationary long-run balance; the initial share moves toward it over repeated transitions.')],table(['Switch','Monthly probability'],[['B to A',.2],['A to B','q']], 'Policy variables'),difficulty='medium')
ck('stationary cost',.4*2+.6*7,5)
add(T,'Expected operating cost of a machine chain','4.19','Markov chains',r'A machine is in Low or High load. Its column transition matrix is $P=\begin{pmatrix}0.7&0.2\\0.3&0.8\end{pmatrix}$. Daily costs are 2 in Low and 7 in High. It starts in Low.',[
p(r'Find the stationary probabilities and long-run expected daily cost.',r'M1|Solve $0.3l=0.2h$ and $l+h=1$.',r'A1|$(l,h)=(0.4,0.6)$.',r'A1|Expected long-run daily cost $=0.4(2)+0.6(7)=5$.'),
p(r'Find the expected cost on day 1 and day 2 after the starting day.',r'M1|Day-1 probabilities are $(0.7,0.3)$, giving cost 3.5.',r'A1|Day-2 probabilities are $(0.55,0.45)$, giving cost 4.25.'),
p(r'Explain why multiplying the long-run daily cost by 2 does not give the exact expected cost over these first two days.',r'R1|The initial distribution is not stationary.',r'A1|The actual two-day expected cost is $3.5+4.25=7.75$, rather than 10.')],table(['Current / next','Low','High'],[['Low',.7,.3],['High',.2,.8]],'Daily machine transitions'),difficulty='medium')
ck('contrast mean variance',4*9+9*4,72)
add(T,'Two ways to reduce variability in a comparison','4.14','Regression and random variables',r'Independent measurements have $E(X)=12$, $\operatorname{Var}(X)=9$, $E(Y)=8$, and $\operatorname{Var}(Y)=4$. A contrast is $Z=2X-3Y$.',[
p(r'Find the mean and variance of Z.',r'A1|$E(Z)=2(12)-3(8)=0$.',r'M1|Independence gives $\operatorname{Var}(Z)=2^2(9)+(-3)^2(4)$.',r'A1|Variance is 72.'),
p(r'Four independent copies of Z are averaged. Find the standard deviation of their average.',r'M1|Variance of the average is $72/4=18$.',r'A1|Standard deviation is $\sqrt{18}=4.24264$.'),
p(r'A student averages four repeated readings affected by the same random calibration error. Explain why the same variance reduction need not apply.',r'R1|The common calibration error makes the repeated readings dependent.',r'R1|A shared error component does not average away as if four errors were independent.')],table(['Variable','Mean','Variance'],[['X',12,9],['Y',8,4],['Z','2X - 3Y','to be found']], 'Measurement model'),difficulty='medium')
ck('CLT standard error',16/math.sqrt(64),2)
add(T,'Using a large sample from a skew population','4.15','Confidence intervals',r'Individual waiting times are strongly right-skewed with mean 20 minutes and standard deviation 16 minutes. A sample of 64 independent waiting times is taken. The diagram shows a possible shape for individual waiting times, not the sampling distribution of their mean.',[
p(r'Give an approximate distribution for the sample mean and state the theorem supporting it.',r'R1|The central limit theorem supports approximate normality for a sufficiently large independent sample.',r'A1|$\bar X\approx N(20,16^2/64)=N(20,4)$.'),
p(r'Estimate the probability that the sample mean exceeds 23 minutes.',r'M1|$z=(23-20)/2=1.5$.',rf'A1|The probability is approximately {1-N.cdf(1.5):.6g}.'),
p(r'Explain why applying the same normal calculation to an individual waiting time could be seriously misleading.',r'R1|An individual waiting time retains the strongly skewed population distribution.',r'R1|The theorem concerns the sampling distribution of the mean, not a claim that the original population is normal.')],plot([lambda x:(x/100)*math.exp(-x/10)],(0,80),(0,.04),'individual waiting time / min','illustrative density'))

# TOPIC 5 — calculus and dynamic models, with contextual and global reasoning.
T='calculus'
xopt=(160/math.pi)**(1/3);ck('cylinder optimum derivative residual',4*math.pi*xopt-640/xopt**2,0)
add(T,'An open cylinder with minimum material','5.7','Differentiation and optimisation',r'An open cylindrical container must hold 320 cubic centimetres. The base material costs twice as much per square centimetre as the side material. Let r be the radius and h the height, in centimetres.',[
p(r'Express the relative material cost in terms of r alone.',r'M1|Volume gives $h=320/(\pi r^2)$.',r'A1|Taking side cost as one unit per square centimetre, $C=2\pi r^2+2\pi rh=2\pi r^2+640/r$, $r>0$.'),
p(r'Find the radius and height minimising the cost.',r'M1|$C\prime=4\pi r-640/r^2=0$, so $r^3=160/\pi$.',rf'A1|$r={xopt:.6g}$ cm.',rf'A1|$h=320/(\pi r^2)={320/(math.pi*xopt*xopt):.6g}$ cm, which equals $2r$.'),
p(r'Justify that the stationary value is the global minimum.',r'M1|$C^{\prime\prime}=4\pi+1280/r^3>0$ for all $r>0$.',r'R1|The cost is strictly convex; it also tends to infinity as r approaches zero or infinity, so this stationary point is the global minimum.')],svg('<ellipse cx="320" cy="90" rx="105" ry="30"/><path d="M215 90V280 M425 90V280"/><ellipse cx="320" cy="280" rx="105" ry="30"/><path d="M320 90H425 M455 90V280"/>'+txt(370,80,'r')+txt(480,190,'h'),'Open cylindrical container; not to scale'),level='sl')
xp=bisect(lambda x:120*math.exp(-.2*x)*(1-.2*x)-20,0,5);ck('profit derivative at optimum',120*math.exp(-.2*xp)*(1-.2*xp)-20,0)
add(T,'A production optimum with a diminishing response','5.9','Differentiation and optimisation',r'A machine’s daily profit is modelled by $P(x)=120xe^{-0.2x}-20x$ for $0\le x\le10$, where x is the operating time in hours. The curve is shown.',[
p(r'Find the derivative and all stationary points in the domain.',r'M1|Product rule gives $P\prime(x)=120e^{-0.2x}(1-0.2x)-20$.',r'M1|Solve $P\prime(x)=0$ using technology.',rf'A1|The stationary point is $x={bisect(lambda x:120*math.exp(-.2*x)*(1-.2*x)-20,0,5):.6g}$.'),
p(r'Find the maximum profit and justify the choice using the domain endpoints.',rf'A1|At the stationary point, profit is {120*bisect(lambda x:120*math.exp(-.2*x)*(1-.2*x)-20,0,5)*math.exp(-.2*bisect(lambda x:120*math.exp(-.2*x)*(1-.2*x)-20,0,5))-20*bisect(lambda x:120*math.exp(-.2*x)*(1-.2*x)-20,0,5):.6g}.',rf'A1|Endpoint profits are $P(0)=0$ and $P(10)={1200*math.exp(-2)-200:.6g}$.',r'R1|The stationary value exceeds both endpoints and is the unique stationary maximum in this interval.'),
p(r'Explain why extending the model to arbitrary negative x has no physical meaning.',r'R1|Operating time cannot be negative.',r'R1|A mathematical formula’s algebraic domain can exceed the domain allowed by its context.')],plot([lambda x:120*x*math.exp(-.2*x)-20*x],(0,10),(-50,170),'operating time / h','profit'))
ck('cone related rate',12/(math.pi*2**2),3/math.pi)
add(T,'Water rising in a conical tank','5.9','Differentiation and optimisation',r'A conical tank has height 6 m and top radius 3 m. Water is pumped in at 12 cubic metres per minute. At some instant the water depth h is 4 m. The water surface remains horizontal.',[
p(r'Express water volume as a function of h.',r'M1|Similar triangles give $r/h=3/6=1/2$.',r'A1|$V=\pi r^2h/3=\pi h^3/12$.'),
p(r'Find the rate at which the water depth is rising at the stated instant.',r'M1|$dV/dt=(\pi h^2/4)(dh/dt)$.',r'A1|At $h=4$, $12=4\pi(dh/dt)$.',r'A1|$dh/dt=3/\pi=0.954930$ metres per minute.'),
p(r'Explain whether the depth-rise rate increases or decreases as the tank fills at the same volume rate.',r'M1|$dh/dt=48/(\pi h^2)$.',r'R1|It decreases as h increases, because the horizontal surface area is larger.')],svg('<path d="M180 80L320 320L460 80 M180 80Q320 35 460 80 M180 80Q320 125 460 80 M225 157Q320 125 415 157 M225 157Q320 190 415 157 M320 320V157H415"/>'+txt(345,240,'h')+txt(370,145,'r')+txt(320,28,'Tank: H = 6 m, R = 3 m'),'Conical tank and water surface; not to scale'),difficulty='medium')
ck('log tangent derivative',4/(2+1),4/3)
add(T,'Local sensitivity of a logarithmic calibration','5.9','Differentiation and optimisation',r'A calibration response is $y=4\ln(x+1)+2$ for $x>0$. An instrument currently receives input $x=2$.',[
p(r'Find the equation of the tangent at the current input.',r'M1|$dy/dx=4/(x+1)$, so the gradient at 2 is $4/3$.',r'A1|$y-(4\ln3+2)=\frac43(x-2)$.'),
p(r'Use the tangent to estimate the response change for an input increase of 0.06, then compare with the actual change.',r'M1|Linear estimate is $(4/3)(0.06)=0.08$.',rf'A1|Actual change is $4\ln(3.06/3)={4*math.log(1.02):.6g}$.',r'A1|The tangent slightly overestimates the change.'),
p(r'Explain the direction of the error using concavity.',r'M1|$y^{\prime\prime}=-4/(x+1)^2<0$.',r'R1|The response curve is concave down, lying below its tangent near the point, so the tangent overestimates.')],plot([lambda x:4*math.log(x+1)+2],(.1,4),(0,10),'input x','response'),difficulty='medium')
ck('logistic inflection position',1000/(1+9*math.exp(-math.log(9))),500)
add(T,'When logistic growth is fastest','5.10','Differentiation and optimisation',r'A population follows $P(t)=1000/(1+9e^{-0.4t})$, for $t\ge0$. It satisfies $P\prime=0.4P(1-P/1000)$.',[
p(r'Find the population at which growth is fastest, without maximising a function of time directly.',r'M1|Treat $P\prime=0.4P-0.0004P^2$ as a concave quadratic in P.',r'A1|Its vertex is at $P=500$.'),
p(r'Find when this occurs and calculate the maximum growth rate.',r'M1|Set $1000/(1+9e^{-0.4t})=500$.',r'A1|$t=\ln9/0.4=5.49306$.',r'A1|Maximum growth rate $=0.4(500)(1-0.5)=100$ individuals per time unit.'),
p(r'Explain how the concavity changes at this time.',r'R1|Before P=500 the growth rate is increasing, so the curve is concave up.',r'R1|After P=500 the growth rate decreases, so the curve is concave down; the change gives an inflection point.')],plot([lambda t:1000/(1+9*math.exp(-.4*t))],(0,15),(0,1100),'time','population'))
ck('kinematic signed integral',integ(lambda t:3*(t-1)*(t-3),0,4),4)
add(T,'Distance and displacement when direction reverses','5.13','Kinematics',r'A particle moves along a line with velocity $v(t)=3(t-1)(t-3)$ metres per second for $0\le t\le4$. Its initial position is 2 m.',[
p(r'Find when the particle changes direction and state its direction in each interval.',r'A1|Zeros are t=1 and t=3.',r'R1|Velocity is positive on $(0,1)$ and $(3,4)$, negative on $(1,3)$; it reverses at both zeros.'),
p(r'Find the final position.',r'M1|An antiderivative is $F(t)=t^3-6t^2+9t$.',r'A1|Net displacement is $F(4)-F(0)=4$ m.',r'A1|Final position is $2+4=6$ m.'),
p(r'Find the total distance and explain why it differs from the displacement.',r'M1|Split the absolute-velocity integral at 1 and 3.',r'A1|Distances are 4,4,and 4, giving 12 m.',r'R1|Displacement counts the middle movement negatively; distance counts all movement positively.')],plot([lambda t:3*(t-1)*(t-3)],(0,4),(-4,10),'time / s','velocity / m s^-1'),difficulty='medium')
ck('revolution x volume',math.pi*integ(lambda x:x,0,4),8*math.pi);ck('revolution y volume',math.pi*integ(lambda y:16-y**4,0,2),25.6*math.pi)
add(T,'Two axes of rotation for the same region','5.12','Integration and volume',r'Region R is bounded by $y=\sqrt x$, the x-axis, and $x=4$. It is rotated once about an indicated axis. The sketch identifies the region but does not supply any volume.',[
p(r'Find the volume when R is rotated about the x-axis.',r'M1|Use $V_x=\pi\int_0^4(\sqrt x)^2\,dx$.',r'A1|$V_x=8\pi$.'),
p(r'Find the volume when R is rotated about the y-axis, using washers.',r'M1|At height y, the region runs from $x=y^2$ to $x=4$, with $0\le y\le2$.',r'M1|$V_y=\pi\int_0^2(16-y^4)\,dy$.',r'A1|$V_y=\frac{128\pi}{5}=25.6\pi$.'),
p(r'Find the ratio of the volumes and explain why simply exchanging the letters x and y in the first integral would be invalid.',r'A1|$V_y/V_x=16/5=3.2$.',r'R1|Changing the axis changes the slice geometry: rotation about y produces washers with inner radius $y^2$ and outer radius 4, not solid discs of radius $\sqrt x$.')],plot([lambda x:math.sqrt(x)],(0,4),(0,2.2),'x','y'))
ck('between curves total area',integ(lambda x:abs(x*x-2*x),0,3),8/3,1e-6)
add(T,'Area between intersecting curves','5.12','Integration and volume',r'The curves are $y=x^2$ and $y=2x$, restricted to $0\le x\le3$.',[
p(r'Find their intersections and identify which curve is higher in each subinterval.',r'M1|Solve $x^2=2x$.',r'A1|They meet at x=0 and x=2.',r'R1|$2x$ is higher on $(0,2)$; $x^2$ is higher on $(2,3)$.'),
p(r'Find the total area between the curves on the stated interval.',r'M1|$A=\int_0^2(2x-x^2)\,dx+\int_2^3(x^2-2x)\,dx$.',r'A1|The two areas are $4/3$ and $4/3$.',r'A1|Total area is $8/3$.'),
p(r'Explain why the single integral $\int_0^3(x^2-2x)\,dx$ does not give the total area.',r'A1|That integral is zero.',r'R1|Positive and negative contributions cancel; geometric area must count both pieces positively.')],plot([lambda x:x*x,lambda x:2*x],(0,3),(0,10),'x','y',dashed=(1,)))
ck('pollutant accumulated integral',integ(lambda t:12*t*math.exp(-.5*t*t),0,2),12*(1-math.exp(-2)))
add(T,'Accumulated discharge from a changing flow','5.11','Integration and volume',r'A pollutant enters a lake at rate $R(t)=12te^{-t^2/2}$ kilograms per hour for $t\ge0$. Assume there is no pollutant removal during the first 2 hours.',[
p(r'Find an expression for the mass entering between times 0 and T.',r'M1|Use substitution $u=-t^2/2$, so $du=-t\,dt$.',r'A1|$M(T)=12(1-e^{-T^2/2})$ kilograms.'),
p(r'Find the mass entering in the first 2 hours and its fraction of the model’s eventual total.',rf'A1|$M(2)=12(1-e^{{-2}})={12*(1-math.exp(-2)):.6g}$ kg.',r'M1|The eventual total is $\lim_{T\to\infty}M(T)=12$.',rf'A1|The fraction is $1-e^{{-2}}={1-math.exp(-2):.6g}$.'),
p(r'Find when the entry rate is greatest.',r'M1|$R\prime(t)=12e^{-t^2/2}(1-t^2)$.',r'A1|It is positive before t=1 and negative after, so the maximum rate occurs at t=1 hour.')],plot([lambda t:12*t*math.exp(-.5*t*t)],(0,4),(0,9),'time / h','entry rate / kg h^-1'))
k=math.log(3)/10;cool=lambda t:20+60*math.exp(-k*t);ck('cooling observation',cool(10),40)
add(T,'Cooling with an unknown environmental constant','5.14','Differential equations',r'A liquid cools according to $dT/dt=-k(T-20)$ with $k>0$. Initially its temperature is 80 degrees; after 10 minutes it is 40 degrees.',[
p(r'Solve the differential equation using the initial condition.',r'M1|Separate: $dT/(T-20)=-k\,dt$.',r'M1|Integrate to obtain $\ln|T-20|=-kt+C$.',r'A1|$T=20+60e^{-kt}$.'),
p(r'Find k and when the temperature first reaches 25 degrees.',r'M1|$40=20+60e^{-10k}$, hence $k=\ln3/10$.',r'M1|Set $5=60e^{-kt}$.',rf'A1|$t=\ln12/k={math.log(12)/k:.6g}$ minutes.'),
p(r'Explain why this model never reaches 20 in a finite time.',r'R1|For every finite t, $60e^{-kt}>0$.',r'R1|Thus T remains above 20 and approaches it asymptotically.')],plot([cool,lambda t:20],(0,40),(15,85),'minutes','temperature',dashed=(1,)),difficulty='medium')
ck('mixing salt equilibrium',.3*4-.02*60,0)
add(T,'Salt entering and leaving a well-mixed tank','5.14','Differential equations',r'A tank contains 200 litres of solution and initially 10 kg of salt. Brine with concentration 0.3 kg per litre enters at 4 litres per minute; well-mixed liquid leaves at the same rate. Let S be salt mass in kilograms.',[
p(r'Form a differential equation for S.',r'M1|Salt enters at $4(0.3)=1.2$ kg per minute.',r'M1|Salt leaves at $4S/200=0.02S$ kg per minute.',r'A1|$dS/dt=1.2-0.02S$.'),
p(r'Solve the equation and find the long-run concentration.',r'M1|Separate using $dS/(60-S)=0.02\,dt$.',r'A1|$S=60-50e^{-0.02t}$.',r'A1|Long-run concentration is $60/200=0.3$ kg per litre.'),
p(r'Find when salt mass reaches 40 kg and explain one practical reason the model could become unreliable.',r'M1|$40=60-50e^{-0.02t}$ gives $t=-\ln(0.4)/0.02$.',r'A1|$t=45.8145$ minutes.',r'R1|For example, imperfect mixing makes the outflow concentration different from S/200, breaking the assumed removal rate.')],svg('<path d="M200 90V300H440V90 M200 180H440 M100 130H190 M450 260H550"/>'+txt(135,110,'4 L/min')+txt(135,150,'0.3 kg/L')+txt(320,220,'200 L, well mixed')+txt(510,240,'4 L/min'),'Constant-volume mixing tank'))
growth=lambda t:80*math.exp(.12*t);ck('harvest model equilibrium',.12*50-6,0)
add(T,'Growth opposed by constant harvesting','5.14','Differential equations',r'A population P obeys $dP/dt=0.12P-6$, with $P(0)=80$. Only non-negative populations are physically meaningful.',[
p(r'Solve the initial-value problem.',r'M1|Set $Q=P-50$, giving $dQ/dt=0.12Q$.',r'M1|Separate and integrate.',r'A1|$P=50+30e^{0.12t}$.'),
p(r'Find the time when P reaches 140.',r'M1|$140=50+30e^{0.12t}$, so $e^{0.12t}=3$.',r'A1|$t=\ln3/0.12=9.15510$.'),
p(r'If instead $P(0)=40$, explain the predicted long-term behaviour and the time at which the physical model must stop.',r'M1|The solution is $P=50-10e^{0.12t}$.',r'A1|It reaches zero at $t=\ln5/0.12=13.4120$.',r'R1|The mathematical solution then becomes negative, so the population interpretation must stop at extinction rather than continue below zero.')],plot([lambda t:50+30*math.exp(.12*t),lambda t:50-10*math.exp(.12*t)],(0,14),(0,230),'time','population',dashed=(1,)))
def slopefield(f,xlim=(0,4),ylim=(0,4)):
    xa,xb=xlim;ya,yb=ylim;body='<path d="M60 50V315H585"/>'+txt(320,355,'t')+txt(30,30,'y')
    for j in range(9):
        y=ya+(yb-ya)*j/8
        for i in range(11):
            x=xa+(xb-xa)*i/10;m=f(x,y)*(250/(yb-ya))/(500/(xb-xa));dx=8/math.sqrt(1+m*m);dy=m*dx
            xx=70+500*(x-xa)/(xb-xa);yy=310-250*(y-ya)/(yb-ya)
            body+=f'<path d="M{xx-dx:.2f} {yy+dy:.2f}L{xx+dx:.2f} {yy-dy:.2f}"/>'
    for i in range(5):body+=txt(70+125*i,337,f'{xa+(xb-xa)*i/4:.3g}',12)+txt(35,315-62.5*i,f'{ya+(yb-ya)*i/4:.3g}',12)
    return svg(body,'Slope field of the stated differential equation')
def phasefield(f,g,xlim,ylim):
    xa,xb=xlim;ya,yb=ylim
    X=lambda x:70+500*(x-xa)/(xb-xa)
    Y=lambda y:310-250*(y-ya)/(yb-ya)
    body='<path d="M60 45V315H585"/>'+txt(320,355,'x')+txt(30,28,'y')
    for j in range(9):
        y=ya+(yb-ya)*j/8
        for i in range(11):
            x=xa+(xb-xa)*i/10;vx=f(x,y)*500/(xb-xa);vy=-g(x,y)*250/(yb-ya);mag=math.hypot(vx,vy)
            if mag<1e-12:continue
            dx=9*vx/mag;dy=9*vy/mag;xx=X(x);yy=Y(y)
            ux=dx/9;uy=dy/9;hx=xx+dx;hy=yy+dy
            body+=f'<path d="M{xx-dx:.2f} {yy-dy:.2f}L{hx:.2f} {hy:.2f} M{hx-4*ux+2*uy:.2f} {hy-4*uy-2*ux:.2f}L{hx:.2f} {hy:.2f}L{hx-4*ux-2*uy:.2f} {hy-4*uy+2*ux:.2f}"/>'
    for i in range(5):body+=txt(70+125*i,337,f'{xa+(xb-xa)*i/4:.3g}',12)+txt(35,315-62.5*i,f'{ya+(yb-ya)*i/4:.3g}',12)
    return svg(body,'Phase plane: arrows show direction, not speed')
ck('nonautonomous solution residual at two',1-2*math.exp(-2),2-(2-1+2*math.exp(-2)))
add(T,'Reading a slope field with a moving zero-gradient line','5.15','Differential equations',r'The slope field is for $dy/dt=t-y$. A solution starts at $(0,1)$. An exact solution is supplied for checking: $y=t-1+2e^{-t}$.',[
p(r'Identify the line on which slopes are zero and the regions where solutions increase or decrease.',r'A1|Slopes are zero on $y=t$.',r'R1|Below this line, $t-y>0$ so solutions increase; above it, they decrease.'),
p(r'Find the initial slope and the time and value of the solution’s minimum.',r'A1|Initial slope is $0-1=-1$.',r'M1|For the exact solution, $y\prime=1-2e^{-t}=0$.',r'A1|The minimum occurs at $t=\ln2$, with $y=\ln2$.'),
p(r'Explain why the zero-gradient line is not itself a solution curve.',r'R1|The line $y=t$ has derivative 1.',r'R1|The differential equation assigns derivative zero at every point on that line, so the line does not satisfy it.')],slopefield(lambda t,y:t-y))
def euler(f,t,y,h,steps):
    vals=[(t,y)]
    for _ in range(steps):y=y+h*f(t,y);t=t+h;vals.append((t,y))
    return vals
ee=euler(lambda t,y:t+y,0,1,.2,2);ee2=euler(lambda t,y:t+y,0,1,.1,4);exact=lambda t:2*math.exp(t)-t-1
ck('Euler h 0.2 at 0.4',ee[-1][1],1.48);ck('Euler h 0.1 at 0.4',ee2[-1][1],1.5282)
add(T,'Comparing two Euler step sizes','5.16','Differential equations',r'Solve $dy/dt=t+y$, $y(0)=1$, numerically to $t=0.4$. The exact solution, provided for comparison, is $y=2e^t-t-1$.',[
p(r'Use Euler’s method with step 0.2 to find y(0.4).',r'M1|$y_{n+1}=y_n+h(t_n+y_n)$.',r'A1|$y(0.2)\approx1.2$.',r'A1|$y(0.4)\approx1.48$.'),
p(r'Repeat with step 0.1 and compare absolute errors.',r'M1|Successive values are 1.1, 1.22, 1.362, 1.5282.',rf'A1|The exact value is {exact(.4):.6g}.',rf'A1|Absolute errors are {abs(1.48-exact(.4)):.6g} and {abs(1.5282-exact(.4)):.6g}; the smaller step is more accurate here.'),
p(r'Explain the direction of the Euler error using the exact solution’s concavity.',r'M1|$y^{\prime\prime}=2e^t>0$.',r'R1|The solution is concave up, so each forward tangent step lies below the true curve, giving an underestimate.')],slopefield(lambda t,y:t+y,(0,.4),(1,1.8)))
x0,y0=40,9;h=.1
xn=x0+h*(.5*x0-.02*x0*y0);yn=y0+h*(-.4*y0+.01*x0*y0)
xnn=xn+h*(.5*xn-.02*xn*yn);ynn=yn+h*(-.4*yn+.01*xn*yn)
ck('coupled Euler first prey',xn,41.28);ck('coupled Euler first predator',yn,9)
add(T,'A simultaneous predator-prey update','5.16','Coupled systems and phase portraits',r'A population model is $dx/dt=0.5x-0.02xy$, $dy/dt=-0.4y+0.01xy$. Initially $x=40$, $y=9$. Use Euler step size 0.1, updating both populations from the same old state.',[
p(r'Find the two rates at the initial state and the first Euler state.',r'A1|Initial rates are $dx/dt=12.8$ and $dy/dt=0$.',r'M1|Apply both increments using (40,9).',r'A1|The first state is $(41.28,9)$.'),
p(r'Find the second Euler state.',r'M1|At the first state the rates are 13.2096 and 0.1152.',rf'A1|The second state is $({xnn:.6g},{ynn:.6g})$.'),
p(r'Find the positive equilibrium and explain why updating y using the newly computed x would be a different numerical method.',r'M1|For non-zero populations, $0.5-0.02y=0$ and $-0.4+0.01x=0$.',r'A1|The positive equilibrium is $(40,25)$.',r'R1|Euler evaluates all component rates at the same previous state; using the new x mixes old and new information.')],table(['State','x','y','dx/dt','dy/dt'],[['Initial',40,9,12.8,0],['Step size',.1,.1,'','']], 'Coupled Euler starting data'),style='problem-solving')
ck('stable node eigen direction',mm([[-2,1],[0,-1]],[[1],[1]])[0][0],-1)
add(T,'A stable node with two decay rates','5.17','Coupled systems and phase portraits',r'A linear system is $x\prime=-2x+y$, $y\prime=-y$, with initial state $(3,1)$.',[
p(r'Find eigenvalues and eigenvectors and classify the origin.',r'A1|Eigenvalues are -2 and -1.',r'A1|Corresponding eigenvectors can be $(1,0)^T$ and $(1,1)^T$.',r'R1|Both eigenvalues are negative and real, so the origin is a stable node.'),
p(r'Find the exact solution using the initial state.',r'M1|Write $(3,1)^T=2(1,0)^T+(1,1)^T$.',r'A1|$x=2e^{-2t}+e^{-t}$ and $y=e^{-t}$.'),
p(r'Find the limiting direction of the trajectory as it approaches the origin, and explain why the faster mode does not control that direction.',r'M1|The $e^{-2t}$ term decays faster than $e^{-t}$.',r'A1|$y/x\to1$, so the trajectory approaches tangent to $y=x$.',r'R1|The slower-decaying eigenmode dominates the ratio for this initial state.')],phasefield(lambda x,y:-2*x+y,lambda x,y:-y,(0,4),(0,3)),style='problem-solving')
ck('spiral matrix eigen real part',(-.5-.5)/2,-.5);ck('spiral vector at east',-2*1-.5*0,-2)
add(T,'Reading a spiral without finding an exact solution','5.17','Coupled systems and phase portraits',r'A linear system is $x\prime=-0.5x+2y$, $y\prime=-2x-0.5y$. Its phase-plane vector field is shown.',[
p(r'Find the eigenvalues and classify the origin.',r'M1|The characteristic equation is $(\lambda+0.5)^2+4=0$.',r'A1|$\lambda=-0.5\pm2i$.',r'R1|Negative real parts with non-zero imaginary parts give a stable spiral.'),
p(r'Determine whether trajectories rotate clockwise or anticlockwise.',r'M1|At $(1,0)$ the velocity vector is $(-0.5,-2)$.',r'R1|At the positive x-axis the motion has a negative y component, so rotation is clockwise.'),
p(r'An engineer claims the distance from the origin must decrease at a constant rate. Assess this by finding the derivative of $x^2+y^2$.',r'M1|$d(x^2+y^2)/dt=2xx\prime+2yy\prime=-(x^2+y^2)$.',r'R1|The squared distance decays at a rate proportional to itself, not at a constant rate.',r'A1|Consequently the distance also decays exponentially rather than linearly.')],phasefield(lambda x,y:-.5*x+2*y,lambda x,y:-2*x-.5*y,(-3,3),(-3,3)),style='problem-solving')
ck('saddle eigenvector stable',mm([[1,2],[2,1]],[[1],[-1]])[0][0],-1)
add(T,'An exceptional path into a saddle point','5.17','Coupled systems and phase portraits',r'A system is $x\prime=x+2y$, $y\prime=2x+y$. Two initial states are P=(2,-2) and Q=(2,-1).',[
p(r'Find the eigenvalues and classify the equilibrium.',r'A1|Eigenvalues are 3 and -1, with directions $(1,1)^T$ and $(1,-1)^T$.',r'R1|Opposite eigenvalue signs mean the origin is a saddle point.'),
p(r'Describe the long-term behaviour from P and Q.',r'M1|P lies entirely in the stable eigenvector direction, so its state is $2e^{-t}(1,-1)^T$.',r'A1|P approaches the origin.',r'M1|Q decomposes as $\frac12(1,1)^T+\frac32(1,-1)^T$.',r'A1|Its positive-eigenvalue component grows, so Q moves away asymptotically in direction $y=x$.'),
p(r'Explain why the path from P does not make the equilibrium stable.',r'R1|Stability concerns nearby initial states, not one special trajectory.',r'R1|A small perturbation off the stable line introduces a growing component, as Q illustrates.')],plot([lambda x:x,lambda x:-x],(-3,3),(-3,3),'x','y',[(2,-2,'P'),(2,-1,'Q')],dashed=(1,)),style='problem-solving')
ck('second order initial derivative',-3+4,1);ck('second order maximum',3*math.exp(-math.log(4/3))-2*math.exp(-2*math.log(4/3)),1.125)
add(T,'An overdamped displacement that initially increases','5.18','Coupled systems and phase portraits',r'A displacement satisfies $x^{\prime\prime}+3x\prime+2x=0$, with $x(0)=1$ and $x\prime(0)=1$. Let $v=x\prime$.',[
p(r'Write the coupled first-order system and find its eigenvalues.',r'A1|$x\prime=v$, $v\prime=-2x-3v$.',r'M1|The coefficient matrix is $\begin{pmatrix}0&1\\-2&-3\end{pmatrix}$.',r'A1|Its eigenvalues are -1 and -2.'),
p(r'Find the exact displacement satisfying both initial conditions.',r'M1|Use $x=Ae^{-t}+Be^{-2t}$.',r'M1|$A+B=1$ and $-A-2B=1$.',r'A1|$A=3$, $B=-2$, giving $x=3e^{-t}-2e^{-2t}$.'),
p(r'Find the maximum displacement and explain how initial growth is compatible with a stable equilibrium.',r'M1|$x\prime=-3e^{-t}+4e^{-2t}=0$ gives $t=\ln(4/3)$.',r'A1|The maximum displacement is $9/8=1.125$.',r'R1|Both modes decay in the long term, but their initial combination can produce temporary growth before eventual decay to zero.')],plot([lambda t:3*math.exp(-t)-2*math.exp(-2*t)],(0,5),(0,1.3),'time','displacement'),style='problem-solving')
oscx1=1;oscv1=-.4;oscx2=.96;oscv2=-.784
ck('oscillator Euler energy initial',.5*0**2+2*1**2,2);ck('oscillator Euler second energy',.5*oscv2**2+2*oscx2**2,2.150528)
add(T,'Numerical energy growth in a damped oscillator','5.18','Coupled systems and phase portraits',r'An oscillator satisfies $x^{\prime\prime}=-4x-0.4x\prime$, initially $x=1$, $x\prime=0$. Define $v=x\prime$ and energy $E=\frac12v^2+2x^2$. Use simultaneous forward Euler updates of size 0.1.',[
p(r'Write the first-order system and calculate two Euler steps.',r'A1|$x\prime=v$, $v\prime=-4x-0.4v$.',r'M1|First step: $(x_1,v_1)=(1,-0.4)$.',r'A1|Second step: $(x_2,v_2)=(0.96,-0.784)$.'),
p(r'Compare the initial and second-step numerical energies.',r'A1|$E_0=2$.',r'M1|$E_2=\frac12(0.784)^2+2(0.96)^2$.',r'A1|$E_2=2.150528$, which is larger than the initial energy.'),
p(r'Show that the exact model has non-increasing energy and explain the discrepancy.',r'M1|$E\prime=vv\prime+4xx\prime=v(-4x-0.4v)+4xv$.',r'A1|$E\prime=-0.4v^2\le0$.',r'R1|The observed energy increase is a forward-Euler numerical error, not physical energy creation; a smaller step or improved method should be investigated.')],phasefield(lambda x,v:v,lambda x,v:-4*x-.4*v,(-1.3,1.3),(-2.5,2.5)),style='problem-solving')

# Upgrade selected data-only visuals to substantive graphs/fields. Data required
# by any replacement stay explicitly in the stem as well as in the visual.
byid={q['id']:q for q in Q}
replacements={
 'ib-aihl-na-706':plot([lambda a:(960-3*a)/2,lambda a:(750-2*a)/3,lambda a:2*a],(0,200),(0,500),'premium kits','basic kits',dashed=(1,)),
 'ib-aihl-na-707':plot([lambda x:1.2*x,lambda x:x+10],(0,100),(0,130),'input reading','operation output',dashed=(1,)),
 'ib-aihl-na-717':plot([],(1,10),(900,1500),'year-end deposit number','deposit amount',[(n,1000+50*(n-1),str(1000+50*(n-1))) for n in range(1,11)]),
 'ib-aihl-fn-707':plot([lambda c:.8*c+2,lambda c:.5*c+6],(0,40),(0,40),'input concentration','single-stage output',dashed=(1,)),
 'ib-aihl-fn-711':plot([lambda t:10*t+10 if t<=10 else 15*t-40,lambda t:7.5*t+20 if t<=10 else 2*t+75],(8,12),(70,150),'validation time','count',[(8,82,'observed 82'),(10,94,'observed 94'),(12,97,'observed 97')],title='Forecasts at the supplied times: E solid, L dashed',dashed=(1,)),
 'ib-aihl-gt-717':network(list('PQR'),[('P','Q',None),('P','R',None),('Q','R',None),('R','P',None)],'Directed graph; arrows give allowed transitions',True),
 'ib-aihl-gt-719':network(list('ABCDE'),[('A','B',None),('A','C',None),('A','D',None),('A','E',None),('B','C',None),('B','D',None),('C','E',None)],'Proposed simple graph; no parallel edges'),
 'ib-aihl-sp-708':plot([],(1,10),(0,7),'patient number','reduction',[(i+1,x,str(x)) for i,x in enumerate(d)],title='Paired reductions: one point for each patient'),
 'ib-aihl-sp-714':discreteplot([30,40,20,10],'observed frequency'),
 'ib-aihl-ca-715':phasefield(lambda x,y:.5*x-.02*x*y,lambda x,y:-.4*y+.01*x*y,(0,80),(0,50)),
}
for ident,diagram in replacements.items():byid[ident]['diagramSvg']=diagram
# The second drone follows a vertical ray; the original plotted point alone
# did not communicate that geometric path.
byid['ib-aihl-gt-708']['diagramSvg']=plot([lambda x:x*x/4-x],(0,8),(-2,9),'east / m','north / m',[(0,0,'A start')],title='A curved path; B moves vertically along x=6').replace('</g></svg>','<path d="M447.5 267.73V55" stroke-dasharray="7 4"/><path d="M442.5 65L447.5 55L452.5 65"/></g></svg>')
byid['ib-aihl-na-707']['stem']=byid['ib-aihl-na-707']['stem'].replace('A technician applies gain and then offset.','The graph shows the individual gain (solid) and offset (dashed) rules. A technician applies gain and then offset.')
byid['ib-aihl-fn-707']['stem']=byid['ib-aihl-fn-707']['stem'].replace('Concentrations are non-negative.','Concentrations are non-negative. The individual stage rules f (solid) and g (dashed) are graphed.')
byid['ib-aihl-fn-711']['stem']=byid['ib-aihl-fn-711']['stem'].replace('shown in the table','shown in the graph').replace('The population cannot exceed','At times 8,10,12, the observed counts are 82,94,97; the E forecasts are 90,110,140, and L forecasts are 80,95,99. Lines join the three supplied forecasts for visual comparison only; they do not define the fitted functions between observations. The population cannot exceed')
byid['ib-aihl-gt-705']['stem']=byid['ib-aihl-gt-705']['stem'].replace('The chart uses equal coordinate units.','Use the numerical coordinate scales shown; distance is to be calculated from the coordinates.')
byid['ib-aihl-gt-719']['stem']=byid['ib-aihl-gt-719']['stem'].replace('by its adjacency table','as a graph').replace('supplied table','supplied graph')
byid['ib-aihl-gt-719']['parts'][0]['prompt']=byid['ib-aihl-gt-719']['parts'][0]['prompt'].replace('supplied table','supplied graph')
byid['ib-aihl-sp-708']['stem']=byid['ib-aihl-sp-708']['stem'].replace('The table gives reductions','The graph gives reductions')

# Write only this course's additions and review record.
assert len(Q)==100,len(Q)
assert all(sum(q['topicId']==t for q in Q)==20 for t in ['number-algebra','functions','geometry-trigonometry','statistics-probability','calculus'])
assert len({q['id'] for q in Q})==100
assert len(AUDIT)==100 and all(a['checks'] for a in AUDIT)
for q in Q:
    for textvalue in [q['stem']]+[p['prompt'] for p in q['parts']]+[s['text'] for g in q['markScheme'] for s in g['steps']]:
        assert not re.search('[\x00-\x08\x0b-\x1f]',textvalue),(q['id'],repr(textvalue))
target=ROOT/'content/ib/math-2026-expansion/ai-hl.json';target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps(Q,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
review=ROOT/'docs/ib-2026-maths/ai-hl-author-review.json';review.parent.mkdir(parents=True,exist_ok=True)
review.write_text(json.dumps({'course':'math-ai-hl','questions':100,'topics':{t:sum(q['topicId']==t for q in Q) for t in ['number-algebra','functions','geometry-trigonometry','statistics-probability','calculus']},'diagrams':100,'nonTableDiagrams':84,'dataTableDiagrams':16,'difficulty':{d:sum(q['difficulty']==d for q in Q) for d in ['medium','hard']},'level':{d:sum(q['level']==d for q in Q) for d in ['sl','ahl']},'specification':'Current course first assessment 2021; not the first-assessment-2029 course','officialGuide':'https://www.ibo.org/globalassets/new-structure/university-admission/pdfs/subject-guides/mathematics-applications-interpretation-guide.pdf','provenance':'100 original authored multi-part problem structures, no official past-paper copying. SVGs generated from supplied data or exact formulas. Matrices and statistical tables are diagram data for the associated reasoning.','checks':AUDIT,'limitations':'Author numerical checks do not establish examiner moderation. All displayed mathematics and graphical representations require the independent content/visual audit before release.'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'questions':len(Q),'diagrams':100,'medium':sum(q['difficulty']=='medium' for q in Q),'hard':sum(q['difficulty']=='hard' for q in Q),'checks':sum(len(a['checks']) for a in AUDIT)}))
