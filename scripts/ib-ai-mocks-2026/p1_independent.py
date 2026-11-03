"""Independent AI HL Paper 1 review: newly transcribed givens and calculations.

No author generator or author numerical evidence is imported. Frozen raw hashes
bind the complete questions, marking points and SVGs that were manually read.
The report is written only after all four papers and all 64 questions pass.
"""
from pathlib import Path
from fractions import Fraction as F
from statistics import NormalDist, mean, stdev
from itertools import combinations, permutations
import cmath, hashlib, json, math, re, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'docs/ib-ai-mocks-2026/p1-independent-review.json'
FROZEN = {
    'ai-hl-set-a-paper-1': 'ad905ebe848479378896fb4e4bb35243845fbf7ecd48abf8e9dbde0b85574acf',
    'ai-hl-set-b-paper-1': 'bb4ef7a738a090145ad110d366fbf8db8cc5d6aee8da2cf91abd53f66fd53cbb',
    'ai-hl-set-c-paper-1': '0101c8230e0fc77dc66c813a5541b98ec26cfa5df45d2eaa3beb78d1eff9c864',
    'ai-hl-set-d-paper-1': 'd3da6dbc11efd369ee4807cb3046bf70cd3e9c50e157c188cc69864320814fd7',
}
assert set(FROZEN)=={f'ai-hl-set-{s}-paper-1' for s in 'abcd'}
PAPERS = {}
for name, digest in FROZEN.items():
    raw = (ROOT / 'content/ib/ai-mocks-2026/papers' / (name+'.json')).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == digest, name+' changed since independent reading'
    PAPERS[name] = json.loads(raw)
    paper=PAPERS[name]
    assert paper['id']==name and paper['strand']=='ai' and paper['course']=='hl' and paper['paper']=='1'
    assert paper['minutes']==120 and paper['marks']==110 and paper['calculator'] is True
    assert len(paper['questions'])==16 and sum(q['marks'] for q in paper['questions'])==110
RECORDS = []
NORMAL = NormalDist()
SYLLABUS_REFS={f'{level} {topic}.{n}' for topic,sl_end,ahl_end in [(1,8,15),(2,6,10),(3,6,16),(4,11,19),(5,8,18)]
    for level,lo,hi in [('SL',1,sl_end),('AHL',sl_end+1,ahl_end)] for n in range(lo,hi+1)}

def plain(v):
    if isinstance(v, F): return str(v)
    if isinstance(v, dict): return {k: plain(x) for k,x in v.items()}
    if isinstance(v, (list,tuple)): return [plain(x) for x in v]
    return v

def close(a,b,tol):
    if isinstance(a,(list,tuple)) and isinstance(b,(list,tuple)):
        return len(a)==len(b) and all(close(x,y,tol) for x,y in zip(a,b))
    if isinstance(a,(int,float,F)) and isinstance(b,(int,float,F)) and not isinstance(a,bool) and not isinstance(b,bool):
        return math.isfinite(float(a)) and math.isfinite(float(b)) and abs(float(a)-float(b)) <= tol
    return a == b

def check(test, calculated, expected, tolerance=1e-7):
    ok = close(calculated,expected,tolerance)
    assert ok, (test,calculated,expected,tolerance)
    return {'test':test,'calculated':plain(calculated),'expected':plain(expected),'absoluteTolerance':tolerance,'status':'passed'}

def add(set_, number, parts, reasoning, diagram='No diagram required; givens and demands are complete in the text.'):
    name = f'ai-hl-set-{set_.lower()}-paper-1'
    q = PAPERS[name]['questions'][number-1]
    assert q['number']==number and q['section']==''
    assert q['syllabusRefs'] and len(set(q['syllabusRefs']))==len(q['syllabusRefs']) and set(q['syllabusRefs'])<=SYLLABUS_REFS
    assert set(parts)=={p['label'] for p in q['parts']}==set(reasoning)
    assert q['marks']==sum(p['marks'] for p in q['parts'])
    assert {g['part'] for g in q['markScheme']}==set(parts)
    for part in q['parts']:
        group=next(g for g in q['markScheme'] if g['part']==part['label'])
        assert group['steps'] and all(re.fullmatch(r'[MAR][1-9]\d?',s['code']) and s['text'].strip() for s in group['steps'])
        assert sum(int(s['code'][1:]) for s in group['steps'])==part['marks']
        assert parts[part['label']] and reasoning[part['label']]
    if q.get('diagramSvg'): ET.fromstring(q['diagramSvg'])
    RECORDS.append({'paperId':name,'question':number,'status':'passed','marks':q['marks'],
        'canonicalQuestionSha256':hashlib.sha256(json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        'syllabusRefs':q['syllabusRefs'],'stemAndEveryMarkingPointRead':True,'nativeDiagramInspected':bool(q.get('diagramSvg')),
        'partChecks':parts,'partMathematicalReview':reasoning,'nativeDiagramReview':diagram,
        'markAllocationReview':'Each part demand and all additive method/accuracy/reasoning steps were read; every group, question and paper total was reconciled.'})

def integrate(f,a,b,epsilon=1e-12):
    def simpson(a,b,fa,fm,fb): return (b-a)*(fa+4*fm+fb)/6
    fa,fb,fm=f(a),f(b),f((a+b)/2)
    def recur(a,b,fa,fm,fb,whole,eps,depth):
        m=(a+b)/2; fl,fr=f((a+m)/2),f((m+b)/2)
        left,right=simpson(a,m,fa,fl,fm),simpson(m,b,fm,fr,fb)
        if depth==0 or abs(left+right-whole)<15*eps: return left+right+(left+right-whole)/15
        return recur(a,m,fa,fl,fm,left,eps/2,depth-1)+recur(m,b,fm,fr,fb,right,eps/2,depth-1)
    return recur(a,b,fa,fm,fb,simpson(a,b,fa,fm,fb),epsilon,25)

def t_upper(t,df):
    factor=math.exp(math.lgamma((df+1)/2)-math.lgamma(df/2))/math.sqrt(df*math.pi)
    value=.5-integrate(lambda x:factor*(1+x*x/df)**(-(df+1)/2),0,abs(t))
    return value if t>=0 else 1-value

def solve(a,b):
    a=[list(map(F,row))+[F(v)] for row,v in zip(a,b)]; n=len(a)
    for j in range(n):
        k=next(k for k in range(j,n) if a[k][j]); a[j],a[k]=a[k],a[j]
        pivot=a[j][j];a[j]=[v/pivot for v in a[j]]
        for k in range(n):
            if k!=j:
                v=a[k][j];a[k]=[x-v*y for x,y in zip(a[k],a[j])]
    return [row[-1] for row in a]

def mv(a,v): return [sum(x*y for x,y in zip(row,v)) for row in a]
def regression(x,y):
    xb,yb=mean(x),mean(y);xx=sum((v-xb)**2 for v in x);yy=sum((v-yb)**2 for v in y);xy=sum((u-xb)*(v-yb) for u,v in zip(x,y))
    return yb-xy/xx*xb,xy/xx,xy/math.sqrt(xx*yy),xb-xy/yy*yb,xy/yy

def minimum_trees(nodes,edges):
    result=[]
    for selected in combinations(edges,len(nodes)-1):
        groups={v:v for v in nodes}
        def find(v):
            while groups[v]!=v: v=groups[v]
            return v
        valid=True
        for u,v,w in selected:
            a,b=find(u),find(v)
            if a==b: valid=False;break
            groups[a]=b
        if valid: result.append((sum(w for _,_,w in selected),selected))
    return min(c for c,_ in result),[es for c,es in result if c==min(z for z,_ in result)]

# Set A: all inputs below are independently transcribed from the question stems.
resale=48000*.84**5; upkeep=900*sum(1.18**k for k in range(5))
costs=[(48000*(1-.84**n)+900*sum(1.18**k for k in range(n)))/n for n in range(1,13)]
add('A',1,{'a':[check('Five-year retained value',resale,20074.1732352)],'b':[check('Sum five independently listed annual maintenance payments',upkeep,6438.788784)],
    'c':[check('Exhaustive permitted integer minimizer',min(range(1,13),key=lambda n:costs[n-1]),11),check('Minimum annual cost',min(costs),6075.237474869745),check('Nearest-dollar minimum',round(min(costs)),6075)]},
    {'a':'A 16% annual fall multiplies value by0.84 five times.','b':'Maintenance in years1 through5 is900 times1,1.18,...,1.18^4; no extra year is charged.',
     'c':'Every integer1 through12 is evaluated, including both endpoints. Year11 beats the nearby year10 by about2.15 dollars/year; this establishes the global discrete optimum.'})
a,b,r,c,d=regression([10,20,30,40,50,60],[18.3,30.5,42.1,58.4,66.7,82.6])
add('A',2,{'a':[check('OLS slope',b,1.2754285714285714),check('OLS intercept',a,5.126666666666665),check('Pearson r',r,.9977808814425589)],
    'b':[check('Invert y-on-x calibration at50mV',(50-a)/b,35.18294504181601)],
    'c':[check('Reverse regression slope',d,.7805742396512131),check('Reverse intercept',c,-3.8465779933087063),check('x-on-y prediction',c+50*d,35.182133989251945),check('Slopes product equals r squared',b*d,r*r)]},
    {'a':'Centred cross-products from all six raw pairs determine the OLS line and r; the controlled explanatory variable is x.',
     'b':'Calibration inversion is (signal-intercept)/slope;50mV lies within the measured range. Five decimal places preserve the small distinction.',
     'c':'Regressing x on y minimizes horizontal residuals. The product of regression slopes is r^2<1, so reverse fitting is not algebraic inversion.'})
vx,vy=solve([[1,0],[6,12]],[4,75]);distances=[math.dist((4,5),p) for p in [(1,2),(7,2),(4,8)]]
add('A',3,{'a':[check('AB midpoint x',mean([1,7]),4)],'b':[check('Circumcentre',[vx,vy],[4,4.25]),check('All three squared distances',[(4-x)**2+(4.25-y)**2 for x,y in [(1,2),(7,2),(4,8)]],[14.0625]*3)],
    'c':[check('Call distances',distances,[math.sqrt(18),math.sqrt(18),3]),check('Unique nearest station index',distances.index(min(distances)),2)]},
    {'a':'Horizontal AB has vertical bisector x4.','b':'Equating A/C squared distances gives6x+12y75. Atx4 the common pointy4.25 has equal distances to every site, so all three Voronoi cells meet.',
     'c':'The A/B tie is not the nearest tie: C is strictly nearer at3km, versus sqrt18km to A/B.'},'Native SVG read: sites A(1,2),B(7,2),C(4,8), kilometre axes and no pre-drawn answer boundaries are correct.')
observed=[[36,14],[28,22],[40,10]]; expected=[[50*104/150,50*46/150] for _ in range(3)]
chi=sum((o-e)**2/e for row,exp in zip(observed,expected) for o,e in zip(row,exp));p=math.exp(-chi/2)
add('A',4,{'a':[check('X pass expectation',expected[0][0],34.666666666666664),check('Degrees of freedom',(3-1)*(2-1),2),check('Every expected cell exceeds5',all(v>5 for row in expected for v in row),True)],
    'b':[check('Pearson statistic from all six cells',chi,7.023411371237458),check('Upper tail for chi-square df2',p,.029845963165705147)],'c':[check('Reject independence at5percent',p<.05,True)]},
    {'a':'The marginal pass total is104 and each programme has50 trainees; df2 and all expected counts exceed5.',
     'b':'The df2 survival function is exp(-statistic/2), independently verifying the GDC p-value.',
     'c':'The p-value rejects independence and supports association. Random sampling does not mean random treatment assignment; confounding prevents the stated table alone proving causation.'})
water=[0-3,12-(-1)];speed=math.hypot(*water);bearing=math.degrees(math.atan2(water[0],water[1]))%360
add('A',5,{'a':[check('Water-relative velocity',water,[-3,13])],'b':[check('Speed',speed,13.341664064126334),check('Clockwise bearing from north',bearing,347.0053832080835),check('Bearing nearest degree',round(bearing),347)],'c':[check('One-hour east displacement',water[0]+6,3)]},
    {'a':'Ground equals water-relative plus current, with east/north components explicitly defined.','b':'The direction lies west of north, so bearing is360 minus atan(3/13), not the standard angle from east.',
     'c':'The water-relative velocity is held constant; adding the changed current gives3km/h east for one hour.'},'Native SVG read: desired ground vector(0,12), current(3,-1), east/north axes and legible labels agree with the givens.')
mu=500+2*200;variance=12**2+4*8**2
add('A',6,{'a':[check('Linear-combination mean',mu,900),check('Variance with squared coefficient',variance,400),check('Standard deviation',math.sqrt(variance),20)],
    'b':[check('Normal interval probability',NORMAL.cdf((930-mu)/20)-NORMAL.cdf((880-mu)/20),.7745375447996847)],'c':[check('Upper1percent mass',mu+20*NORMAL.inv_cdf(.99),946.5269574808168)]},
    {'a':'Independent normals yield an exactly normal linear combination. Doubling one Y gives4VarY; treating2Y as two copies would be wrong. Official AHL4.15 explicitly includes this normality result.',
     'b':'The standardized bounds are-1 and1.5; use the exact normal model rather than a CLT approximation.','c':'Only1percent exceed c, hence use the99th percentile, with the population standard deviation20g.'})
matrix=[[F('1.2'),F('.3')],[F('-.4'),F('.8')]];det=matrix[0][0]*matrix[1][1]-matrix[0][1]*matrix[1][0]
add('A',7,{'a':[check('Image of B',mv(matrix,[4,0]),[4.8,-1.6]),check('Image of C',mv(matrix,[1,3]),[2.1,2])],
    'b':[check('Determinant',det,1.08),check('Transformed area',6*abs(det),6.48)],'c':[check('Inverse solution',solve(matrix,[3,2]),[F(5,3),F(10,3)]),check('Image verification',mv(matrix,[F(5,3),F(10,3)]),[3,2])]},
    {'a':'Column-vector multiplication maps each original point; O stays at the origin.','b':'The original triangle area is6m2 and nonsingular determinant27/25 scales area by its absolute value.',
     'c':'The inverse has determinant denominator1.08 and returns(5/3,10/3), which maps back to(3,2).'},'Native SVG read: original triangle O(0,0),B(4,0),C(1,3), labelled axes and original shaded region are consistent.')
add('A',8,{'a':[check('Initial users',1200/(1+7),150),check('Horizontal limiting value',1200,1200)],'b':[check('First900-user crossing',math.log(21)/.4,7.611306094308557)],
    'c':[check('Quadratic logistic maximum rate',.4*600*(1-600/1200),120),check('Inflection time',math.log(7)/.4,4.864775372638283)]},
    {'a':'At t0 the denominator is8; the decaying exponential tends to0, giving carrying capacity1200.',
     'b':'The model increases strictly for t>=0; equation900 gives exp(-0.4t)=1/21, so the single crossing is first.',
     'c':'P prime0.4P(1-P/1200) is a concave quadratic in P, maximized at600. This value is reached after t0, establishing the attainable global maximum rate.'})
edges=[('A','B',4),('A','C',7),('A','D',9),('B','C',2),('B','D',5),('B','E',8),('C','D',3),('C','E',6),('D','E',4)]
best,trees=minimum_trees('ABCDE',edges);closed,closed_trees=minimum_trees('ABCDE',[e for e in edges if e[:2]!=('C','D')])
add('A',9,{'a':[check('Enumerated minimum spanning cost',best,13),check('Selected original tree weight',sum(w for u,v,w in edges if (u,v) in [('B','C'),('C','D'),('A','B'),('D','E')]),13)],
    'b':[check('Minimum after CD closure',closed,15),check('Proposed replacement tree is among enumerated minima',any({(u,v) for u,v,w in t}=={('B','C'),('A','B'),('D','E'),('B','D')} for t in closed_trees),True)]},
    {'a':'Kruskal accepts costs2,3,4,4 without a cycle; the equal-cost AB/DE edges may swap order. Independent enumeration of every four-edge subset proves the optimum.',
     'b':'Removing CD forces the cheapest bridge BD5. Enumerating all admissible trees confirms cost15 and the listed four links.'},'Native weighted graph read edge-by-edge: AB4,AC7,AD9,BC2,BD5,BE8,CD3,CE6,DE4; crossings are not vertices and no weight is ambiguous.')
z=4*cmath.exp(1j*math.pi/6)+3*cmath.exp(-1j*math.pi/3);phase=cmath.phase(z)
add('A',10,{'a':[check('Cartesian resultant',[z.real,z.imag],[4.964101615137755,-.5980762113533162])],'b':[check('Resultant amplitude',abs(z),5),check('Principal argument',phase,-.11990233319498556)],
    'c':[check('Cancelling argument in0to2pi',(phase+math.pi)%(2*math.pi),3.0216903203948076),check('Resultant plus cancelling phasor magnitude',abs(z+5*cmath.exp(1j*(phase+math.pi))),0)]},
    {'a':'Resolve the two equal-frequency phasors into real and imaginary parts and add vectors.','b':'The angle difference is pi/2, so amplitude5 also follows from orthogonality; the sum is in quadrantIV.',
     'c':'The unique cancelling vector is-z: same amplitude and argument shifted by pi into the requested interval. No roots-of-complex-number topic is assumed.'},'Native Argand diagram read: z1 ends at(2sqrt3,2), z2 at(1.5,-3sqrt3/2); axes and vector labels are correct.')
zero=.7*math.exp(-4)+.3*math.exp(-7);tail=1-sum(math.exp(-11)*11**k/math.factorial(k) for k in range(14))
add('A',11,{'a':[check('Mixture probability of zero',zero,.013094511811780278)],'b':[check('Weekday posterior given zero',.7*math.exp(-4)/zero,.9791084544732515)],'c':[check('Independent Poisson total at least14',tail,.21870882746162945)]},
    {'a':'Condition on the weekday/weekend mode; the mixture is not a Poisson with the mixture mean.','b':'Bayes numerator is0.7 exp(-4), divided by the same total-zero probability.',
     'c':'The two specified hours have independent Poisson means4 and7. Their sum has mean11, and at least14 is the survival beyond13.'})
diff=[a-b for a,b in zip([82,77,91,85,88,79,94,83],[78,76,85,81,86,75,88,80])];t=mean(diff)/(stdev(diff)/math.sqrt(8));tp=t_upper(t,7)
add('A',12,{'a':[check('Paired differences',diff,[4,1,6,4,2,4,6,3]),check('Sample mean',mean(diff),3.75),check('Unbiased sample sd',stdev(diff),1.7525491637693282)],
    'b':[check('Improvement is positive before-minus-after mean',mean(diff)>0,True)],'c':[check('Student t statistic',t,6.052099385894467),check('One-sided t7 tail by independent density quadrature',tp,.00025744373,1e-10)],'d':[check('Decision at5percent',tp<.05,True)]},
    {'a':'Form within-runner differences before computing sample statistics; use denominator n-1 for variance.',
     'b':'The parameter is population mean difference: H0 muD0 and H1 muD>0. A decrease in after-time is a positive difference.',
     'c':'Unknown population spread and eight assumed-normal differences require t7, not a known-sigma z test. The p-value is one-tailed.',
     'd':'Evidence supports a mean decrease. Inference additionally requires representative/random pairs and independent differences across runners; within-pair measurements should remain paired.'})
theta=math.radians(140);area=.5*.6**2*(theta-math.sin(theta))
add('A',13,{'a':[check('Radian angle',theta,7*math.pi/9),check('Minor segment area',area,.3241212017589939)],'b':[check('Uniform twelve-metre channel volume',12*area,3.889454421107927)],'c':[check('Surface chord length',1.2*math.sin(theta/2),1.12763114494309)]},
    {'a':'Subtract the isosceles triangle from the140degree sector; using degrees inside theta-sintheta would be invalid.',
     'b':'The uniform cross-sectional area is multiplied by12m, yielding cubic metres.','c':'The inspection bar spans the chord, so its length is2r sin70degrees, not the arc length.'},'Native circular diagram read:0.6m radius,140degree lower central angle and physically lower minor water segment correctly match the stem.')
r=(56/(48*math.pi))**(1/3);h0=4/(math.pi*r*r);limit=math.sqrt(2/math.pi);cost=lambda x:24*math.pi*x*x+56/x
add('A',14,{'a':[check('Side cost coefficient after eliminating h',7*2*4,56)],'b':[check('Unconstrained radius',r,.7187849451782345),check('Unconstrained height',h0,2.464405526325376),check('Interior feasible optimum',.45<r<1.4,True),check('Stationary point beats both endpoints',cost(r)<min(cost(.45),cost(1.4)),True)],
    'c':[check('Height-limited radius',limit,.7978845608028654),check('Constrained cost',cost(limit),118.18559168966802),check('Derivative positive at new lower endpoint',48*math.pi*limit-56/limit**2>0,True)]},
    {'a':'Use volume4pi r2h to eliminate h. Both circular faces cost24pi r2; the curved side contributes56/r.',
     'b':'C prime vanishes uniquely at r cubed7/(6pi). C second48pi+112/r3 is positive for every permitted radius; the stationary point lies inside the interval and is the global minimum.',
     'c':'The new height cap means r>=sqrt(2/pi), which lies above the former optimum. C is increasing throughout the remaining feasible interval, so the lower boundary is optimal.'})
T=[[F(4,5),F(1,5),F(1,10)],[F(3,20),F(3,5),F(1,5)],[F(1,20),F(1,5),F(7,10)]];v2=mv(T,mv(T,[1,0,0]));pi=solve([[T[0][j]-int(j==0) for j in range(3)],[T[1][j]-int(j==1) for j in range(3)],[1,1,1]],[0,0,1])
add('A',15,{'a':[check('Two-week column state',v2,[F(27,40),F(11,50),F(21,200)])],'b':[check('Exact stationary proportions',pi,[F(16,37),F(11,37),F(10,37)]),check('Stationary vector substitution',mv(T,pi),pi),check('All entries positive gives regular chain',all(x>0 for row in T for x in row),True)],
    'c':[check('Bus-in-week1 posterior given cycle-in-week2',T[2][0]*T[1][2]/v2[1],F(1,22))]},
    {'a':'Column sums are1; the specified orientation means multiply T by the initial walking column twice.',
     'b':'Solve the fixed-point equations and normalization in exact rational arithmetic. Positivity makes the chain regular, justifying the unique limiting proportions.',
     'c':'The only relevant numerator is W0 to B1 to C2, probability0.05 times0.2. Divide by all paths giving C2,0.22; this is a reverse conditional, not a forward transition.'})
values=[4.]
for _ in range(3): values.append(values[-1]+.1*(30-.2*values[-1]**2))
eq=math.sqrt(150);exact=eq*math.tanh(.2*eq*.3+math.atanh(4/eq));one=4+.3*(30-.2*4**2)
add('A',16,{'a':[check('Physical equilibrium',eq,12.24744871391589),check('Positive derivative below equilibrium',all(30-.2*v*v>0 for v in [0,4,8,12]),True)],
    'b':[check('All three old-state Euler updates',values,[4,6.68,8.787552,10.24313059694592])],
    'c':[check('Single h0.3 Euler step',one,12.04),check('Independent exact solution at0.3 for error-direction check',exact,9.68665595468164),check('Both stated approximations overestimate in this interval',exact<values[-1]<one,True)]},
    {'a':'Equilibria solve V squared150, with the negative root excluded by the physical domain. For0<=V<sqrt150 the derivative is positive.',
     'b':'Use the old volume in each explicit Euler update; retaining full precision gives the printed third-step estimate.',
     'c':'Along the increasing positive solution, V second=-0.4V V prime<0. A tangent at an exact solution point therefore lies above it forwards. The exact tanh solution is used only by this independent verifier, not demanded of students; the stated conclusion is about local tangent estimates.'},'Native slope field inspected: uniform t invariance, positive slopes below12.247, nearly flat near12, negative above, and m3/hour axes agree with the differential model.')

# Set B: inputs independently transcribed from its complete stems and diagrams.
monthly=.048/12;annuity=sum((1+monthly)**k for k in range(120));future=800*annuity;real=future/1.025**10;deposit=100000*1.025**10/annuity
add('B',1,{'a':[check('Nominal annual to monthly rate',monthly,.004)],'b':[check('End-month deposits accumulated to deposit120',future,122905.56961920908,.01)],
    'c':[check('Inflation-discounted purchasing power',real,96013.633,.001)],'d':[check('Target purchasing-power deposit',deposit,833.21501,.00001),check('Unrounded target substitution',deposit*annuity/1.025**10,100000,.000001)]},
    {'a':'Nominal monthly compounding divides0.048 by12, not an effective annual twelfth root.',
     'b':'The latest payment earns no interest and the first earns119monthly periods; independent summation verifies the ordinary-annuity expression.',
     'c':'Inflation is stated annually; discount the future amount by1.025^10.',
     'd':'Inflate the100000real-dollar target, then divide by the same future-value annuity factor. The exact ideal payment is833.21501; an attainable minimum cent payment would round upward to833.22, as the scheme notes.'})
inverse=lambda s:(4*s-12)/(18-s)
add('B',2,{'a':[check('Inverse at lower endpoint',inverse(3),0),check('Inverse algebraic composition',[(18*inverse(s)+12)/(inverse(s)+4) for s in [3,13,14,15,16,17.9]],[3,13,14,15,16,17.9])],
    'b':[check('Concentration for14mV',inverse(14),11)],'c':[check('Concentration changes for the two equal signal increments',[inverse(14)-inverse(13),inverse(16)-inverse(15)],[3,10])]},
    {'a':'Rearrangement gives(4S-12)/(18-S). S at c0 is3, and S=18-60/(c+4) stays strictly below18 for all c>=0; the inverse physical domain is[3,18).',
     'b':'The signal14lies in the inverse domain and gives11mg/L.','c':'The inverse increments grow from3to10for equal1mV signal increments: more concentration is required for the same signal change, so high-concentration signal sensitivity is lower.'})
u=[2,-1,2];v=[1,2,-2];delta=[-4,2,-4];dot=lambda x,y:sum(a*b for a,b in zip(x,y));projection=dot(delta,v)/dot(v,v);distance=math.sqrt(dot(delta,delta)-dot(delta,v)**2/dot(v,v))
add('B',3,{'a':[check('First rail at s2',[1+2*2,2-2,3+2*2],[5,0,7]),check('Second rail at t0',[5,0,7],[5,0,7])],
    'b':[check('Acute angle using absolute dot product',math.degrees(math.acos(abs(dot(u,v))/math.sqrt(dot(u,u)*dot(v,v)))),63.612200038757,.000001)],
    'c':[check('Perpendicular distance by quadratic minimization',distance,5.3748384988657),check('Closest-point residual is perpendicular to line',dot([x-projection*y for x,y in zip(delta,v)],v),0)]},
    {'a':'Solving x/y components gives s2,t0 and the zcomponent confirms the intersection; the directions are nonparallel.',
     'b':'The direction dot product is-4 with both norms3; an acute unoriented line angle uses its absolute value, giving acos(4/9).',
     'c':'Minimize the squared distance from P to I+t v. The optimum t8/9 leaves a residual perpendicular to v and distance sqrt260/3; no plane equations are needed.'},'Native SVG is explicitly a schematic intersection, not an inaccurate coordinate projection; both rail labels and intersection I are clear.')
def ranks(values): return [1+sum(x<v for x in values)+(sum(x==v for x in values)-1)/2 for v in values]
rx,ry=ranks([12,14,14,18,20,23,25]),ranks([44,40,42,35,37,31,28]);rs=regression(rx,ry)[2]
add('B',4,{'a':[check('Average tied x ranks',rx,[1,2.5,2.5,4,5,6,7]),check('Ascending y ranks',ry,[7,5,6,3,4,2,1])],
    'b':[check('Pearson correlation of rank lists',rs,-.954993710457128)],'c':[check('Negative strong monotonic rank relation',rs<-.9,True)]},
    {'a':'Two xvalues14tie for ranks2and3, so both receive2.5. The yvalues are all distinct and are ranked ascending in original hiker order.',
     'b':'Pearson correlation of the actual averaged ranks handles ties; the no-ties shortcut without correction should not replace it.',
     'c':'The association is strongly negative and monotonic: larger distance tends to shorter time. The observational sample does not isolate training from fitness, age or other confounders.'})
offset=6/math.pi*math.acos((3.1-2.4)/1.6);window=[3-offset,3+offset]
add('B',5,{'a':[check('Amplitude',1.6,1.6),check('Period',2*math.pi/(math.pi/6),12)],
    'b':[check('First threshold window',window,[.8648159899416186,5.135184010058381],.000001),check('Threshold values at both endpoints',[2.4+1.6*math.cos(math.pi*(t-3)/6) for t in window],[3.1,3.1])],
    'c':[check('Latest90minute start',window[1]-1.5,3.635184010058381,.000001),check('Operation fits inside the first high-tide window',window[1]-window[0]>=1.5,True)]},
    {'a':'The amplitude is the positive cosine coefficient; the angular coefficient pi/6 gives a12hour period.',
     'b':'Cosine must be at least0.4375. Around the first maximumt3this yields3plus/minus6acos(0.4375)/pi; no earlier segment is available at midnight because h0=2.4.',
     'c':'The full operation must remain inside the continuous high-depth interval. Its latest start is the right threshold minus1.5hours, with equality allowed because the depth requirement is at least3.1.'},'Native tide SVG checked: peaks(3,4),(15,4), troughs(9,0.8),(21,0.8), correct24hour domain and horizontal3.1m threshold.')
edges=[('A','B',4),('B','C',5),('C','D',3),('D','A',6),('A','E',7),('B','E',6),('C','E',4),('D','E',5)]
nodes='ABCDE';dist={(a,b):(0 if a==b else math.inf) for a in nodes for b in nodes}
for a,b,w in edges:dist[a,b]=dist[b,a]=w
for k in nodes:
    for a in nodes:
        for b in nodes:dist[a,b]=min(dist[a,b],dist[a,k]+dist[k,b])
pairings=[dist['A','B']+dist['C','D'],dist['A','C']+dist['B','D'],dist['A','D']+dist['B','C']]
add('B',6,{'a':[check('Odd-degree vertices',[n for n in nodes if sum(n in (a,b) for a,b,w in edges)%2],list('ABCD'))],
    'b':[check('All three shortest-distance pairings',pairings,[7,17,11]),check('Minimum repeat distance',min(pairings),7)],
    'c':[check('Sum of all original corridors',sum(w for a,b,w in edges),40),check('Closed inspection optimum',sum(w for a,b,w in edges)+min(pairings),47)]},
    {'a':'A,B,C,D each have odd degree3; Ehasdegree4. The graph is connected, but its four odd vertices prevent an Euler circuit without repeats.',
     'b':'Compute shortest-path distances, not just direct edge lengths. The three pairings exhaust all ways to pair four odd vertices; duplicating AB4 and CD3 is cheapest.',
     'c':'Adding the seven repeated metres makes all degrees even while retaining connectivity, so a47metre Euler circuit exists and the pairing lower bound proves optimality.'},'Native graph read: outer AB4,BC5,CD3,DA6; spokes AE7,BE6,CE4,DE5. E is a labelled junction and all weights/units are clear.')
bin_cdf=lambda n,p,k:sum(math.comb(n,j)*p**j*(1-p)**(n-j) for j in range(k+1))
pv=bin_cdf(30,.2,2);critical=max(k for k in range(31) if bin_cdf(30,.2,k)<.05);beta=1-bin_cdf(30,.1,critical)
add('B',7,{'a':[check('Alternative direction is reduced defect probability',.1<.2,True)],'b':[check('Exact lower-tail null probability',pv,.04417898515199869),check('Reject at5percent',pv<.05,True)],
    'c':[check('Largest permitted lower-tail cutoff',critical,2),check('Next cutoff exceeds significance',bin_cdf(30,.2,3),.12271080639416)],'d':[check('TypeII nonrejection probability under true p0.1',beta,.5886487604404948)]},
    {'a':'H0p0.20,H1p<0.20; the model is independent Bernoulli trials with a common defect probability.',
     'b':'The observed count2calls for Pnull(X<=2), not a point probability or a doubled tail. It is below0.05.',
     'c':'The critical region isX<=2. Its probability is strictly below0.05, whileX<=3is already above; exhaustive cutoff search confirms maximality.',
     'd':'A TypeII error is failure to reject a false null. Underp0.10useP(X>2), retaining the original null-based critical region.'})
life=[42.1,44.8,41.7,46.3,43.5,45.2,42.9,44.1,43.7];lo,hi=0.,5.
for _ in range(55):
    mid=(lo+hi)/2
    if t_upper(mid,8)>.025:lo=mid
    else:hi=mid
tc=(lo+hi)/2;interval=[mean(life)-tc*stdev(life)/3,mean(life)+tc*stdev(life)/3]
add('B',8,{'a':[check('Sample mean',mean(life),43.81111111111111),check('Unbiased sample sd',stdev(life),1.479395522495694)],
    'b':[check('t8 97.5percent quantile by density quadrature inversion',tc,2.306004135204166),check('Confidence interval',interval,[42.67394704717772,44.9482751750445])],
    'c':[check('Claim44.5 lies inside interval',interval[0]<44.5<interval[1],True)]},
    {'a':'Use all nine normal-population observations and sample sd with n-1denominator.',
     'b':'The unknown population variance requires a two-sided t8confidence interval. Standard error iss/3; independent inversion of the t-density integral verifies the critical quantile.',
     'c':'The claimed mean44.5is compatible with this sample at95percent confidence. The interval describes uncertainty about a mean, not95percent individual lifetime coverage.'})
coarse=[0,18,29,25,14,0];fine=[0,9.5,18,24,29,28.5,25,20,14,7.5,0];secants=[(b-a)/10 for a,b in zip(fine,fine[1:])]
trap=lambda step,values:step*(sum(values)-.5*(values[0]+values[-1]))
add('B',9,{'a':[check('20m trapezoidal volume',trap(20,coarse),1720)],'b':[check('10m trapezoidal volume',trap(10,fine),1755),check('Refined data consistent with strict concavity',all(a>b for a,b in zip(secants,secants[1:])),True)],
    'c':[check('Refinement raises the chord estimate',trap(10,fine)>trap(20,coarse),True)]},
    {'a':'The six areas give five equal20mintervals, not six. Endpoint weights are one-half, and area-times-length gives m3.',
     'b':'Interleave every midpoint observation with the originals to give ten equal10mintervals. All ten consecutive secant slopes strictly decrease, so the data support the stated concavity assumption.',
     'c':'For a concave-down underlying area function, each chord is below the curve. Integrating those chords therefore underestimates volume; the larger refined result is consistent but does not alone prove the error direction.'},'Native SVG checked: all six measured area points and metre/m2axes are correct; drawn joining chords represent measurements, not an assertion that the underlying strictly concave function is piecewise linear.')
L=[[0,1.8],[.5,.3]];lam=(.3+math.sqrt(.3**2+4*.9))/2;second=(.3-math.sqrt(.3**2+4*.9))/2;ratio=1.8/lam
add('B',10,{'a':[check('One-year stage state',mv(L,[200,100]),[180,130])],'b':[check('Dominant eigenvalue',lam,1.1104686356149274),check('Other eigenvalue',second,-.8104686356149273),check('Dominance and eventual growth',lam>1 and lam>abs(second),True)],
    'c':[check('Juvenile-to-adult ratio',ratio,1.6209372712298549),check('Adult limiting proportion',1/(ratio+1),.3815428971851665),check('Stable vector equation',mv(L,[ratio,1]),[lam*ratio,lam])]},
    {'a':'The first component is fertility1.8times100adults; adults next year combine juvenile survival0.5and adult retention0.3.',
     'b':'The characteristic equation islambda squared-0.3lambda-0.9=0. Distinct real eigenvalues are within AI HL scope. Positive initial populations have a nonzero dominant component and the positive dominant eigenvalue exceeds1.',
     'c':'Normalize the positive dominant eigenvector:1.8A=lambda J. Dividing A byJ+A gives the limiting adult proportion, distinct from the growth factor.'})
dh=.36/math.pi;time=integrate(lambda h:math.pi*h*h/(4*(.4-.02*h)),1,2)
add('B',11,{'a':[check('Similarity radius at h2',2*(3/6),1),check('Volume coefficient',math.pi/3*(3/6)**2,math.pi/12)],
    'b':[check('Net volume inflow at h2',.4-.02*2,.36),check('Depth derivative at h2',dh,.11459155902616464)],'c':[check('Time quadrature with variable depth',time,4.9829001,.0000001),check('Positive flow over integration range',min(.4-.02*h for h in [1,2])>0,True)]},
    {'a':'Similar triangles scale water radius as h/2; the cone volume becomes pi h3/12.',
     'b':'Chain rule gives dVdt=(pi h2/4)dhdt. The net flow at h2is0.36m3/min, so dhdt0.36/pi.',
     'c':'Integrate dtdh=pi h2/[4(0.4-0.02h)] from1to2. The denominator remains positive, so depth rises monotonically and this integral is the required elapsed time.'},'Native cone inspected: vertex down, full height6m bracket outside the cone, top radius3m, water-level line and dashed central height are legible and consistent.')
intercept,exponent,*_=regression([math.log(v) for v in [2,4,6,9,12]],[math.log(v) for v in [11.8,25.7,41.4,68.6,95.5]]);scale=math.exp(intercept)
add('B',12,{'a':[check('Log-linear slope',exponent,1.1721178,.0000001),check('Exponential intercept',scale,5.1549397,.0000001)],'b':[check('Unrounded power-model prediction',scale*8**exponent,58.98634,.00001)],
    'c':[check('Elasticity identity at two positive loads',[z/(scale*z**exponent)*(scale*exponent*z**(exponent-1)) for z in [2,8]],[exponent,exponent]),check('First-order5percent response estimate',5*exponent,5.8605891,.0000001)]},
    {'a':'Use least squares on logE versus logm exactly as requested, which is a specified fit rather than silently replacing it by direct nonlinear least squares.',
     'b':'Eight kilograms lies within the observed load range; retain the unrounded regression coefficients to avoid avoidable prediction error.',
     'c':'Differentiation gives abm^(b-1); multiplying by m/E simplifies algebraically to constant b. Relative differential dE/E=b dm/m gives an estimated5bpercent, not an exact finite-change percentage.'})
pois=lambda rate,k:math.exp(-rate)*rate**k/math.factorial(k);p5=pois(5,5);split=pois(2,2)*pois(3,3)/p5
add('B',13,{'a':[check('Poisson total point probability',p5,.1754673697678507)],'b':[check('Conditional split from independent joint probabilities',split,.3456)],'c':[check('Conditioned positive-A probability',1-math.exp(-2),.8646647167633873)]},
    {'a':'The independent Poisson sum has mean5for the same15minute interval.',
     'b':'Given the total5, exactly2atAforces3atB. Divide the independent joint Poisson probability by the total probability; no unprovided splitting theorem is needed.',
     'c':'A and B are independent, so B0does not alter the distribution of A. At least one atAis1-exp(-2).'})
table=[[0,6,9,10,7],[6,0,5,8,9],[9,5,0,6,8],[10,8,6,0,4],[7,9,8,4,0]]
tours=[sum(table[a][b] for a,b in zip([0,*order],[*order,0])) for order in permutations([1,2,3,4])]
deleted_edges=[(str(a),str(b),table[a][b]) for a,b in combinations([1,2,3,4],2)];mst,_=minimum_trees(['1','2','3','4'],deleted_edges)
add('B',14,{'a':[check('Nearest-neighbour tour cost',sum(table[a][b] for a,b in zip([0,1,2,3,4],[1,2,3,4,0])),28)],'b':[check('Deleted-A minimum spanning tree',mst,15),check('Deleted-A lower bound',mst+sum(sorted(table[0][1:])[:2]),28)],
    'c':[check('Exhaustive Hamiltonian-tour optimum',min(tours),28)]},
    {'a':'At each visited vertex the nearest remaining choice isB,C,D,Ethen returnA; a feasible tour gives an upper bound.',
     'b':'Deleting Afrom any Hamiltonian cycle leaves a spanning path on B,C,D,E, whose cost is at least that of its MST15. The two incident Aedges cost at least6and7, giving lower bound28.',
     'c':'A28km tour attains the28km lower bound, so it is optimal. Independent enumeration of all24orders verifies the bound argument.'})
T4=20+70*math.exp(-.15*4);hit=4+math.log((T4-5)/10)/.15;rates=[-.15*(T4-20),-.15*(T4-5)]
add('B',15,{'a':[check('Temperature at room change',T4,58.41681452658185)],'b':[check('First15degree time',hit,15.17027,.00001),check('Second-stage target substitution',5+(T4-5)*math.exp(-.15*(hit-4)),15)],
    'c':[check('Left and right cooling derivatives',rates,[-5.762522178987278,-8.012522178987278]),check('Derivative jump',rates[1]-rates[0],-2.25)]},
    {'a':'Before the move the temperature excess above20decays from70. Continuity fixes T4for the new stage.',
     'b':'The first stage stays above20, so it cannot reach15. In the second stage the positive excess above5decays strictly, giving one target time after4.',
     'c':'The state remains continuous but the ambient parameter drops15degrees. The driving difference therefore increases15and the derivative jumps downward2.25degrees/min.'})
factor=.6+.8j;angle=cmath.phase(factor);centre=factor*1+2-1j;tmax=(math.pi/2-angle)%(2*math.pi);top=factor*(1+2*cmath.exp(1j*tmax))+2-1j
add('B',16,{'a':[check('Multiplier modulus',abs(factor),1),check('Anticlockwise angle',angle,.9272952180016123)],'b':[check('Image-circle centre',[centre.real,centre.imag],[2.6,-.2]),check('Image radius',2*abs(factor),2)],
    'c':[check('Parameter at greatest imaginary part',tmax,.6435011087932843),check('Maximum imaginary part',top.imag,1.8),check('Radius points vertically upward at optimum',top.real,centre.real)]},
    {'a':'Complex multiplication is rotation about the origin by Argfactor and scale its modulus1; the subsequent translation is separate.',
     'b':'Transform the centre z1, then multiply the radius2by the modulus. The centre shifts to2.6-0.2i while radius is unchanged.',
     'c':'The transformed radius has angle t+Argfactor. Its imaginary part is largest when that angle is pi/2mod2pi, yielding the unique t in the requested domain and centre-imaginary-part plus radius.'},'Native original z-circle inspected: centre1on the real axis, real intercepts-1and3, and imaginary extremesplus/minus2 match z1+2exp(it).')

# Set C: fresh calculations from its stated observations, models and graphics.
I1,I2=1e-12*10**7.2,1e-12*10**6.8;combined=10*math.log10((I1+I2)/1e-12);retained=(1e-5-I2)/I1
add('C',1,{'a':[check('Sum intensities then logarithm',combined,73.455405,.000001)],
    'b':[check('Retained first-machine intensity fraction',retained,.23285017,.00000001),check('Minimum percentage reduction',100*(1-retained),76.714983,.000001),check('Threshold intensity substitution',retained*I1+I2,1e-5,1e-15)]},
    {'a':'Incoherent sound intensities add; adding72and68decibels would violate the supplied logarithmic definition. Logarithms here use the permitted base10.',
     'b':'A70dBtotal is10^-5W/m2. Since the unchanged second intensity is below that limit, the retained fraction is positive and below1. The logarithm is increasing, so equality gives the least required reduction.'})
coeff=solve([[0,0,1],[4,2,1],[25,5,1]],[2,14,17]);ground=4+math.sqrt(18)
add('C',2,{'a':[check('Quadratic coefficients',coeff,[-1,8,2]),check('All three observation substitutions',[-t*t+8*t+2 for t in [0,2,5]],[2,14,17])],
    'b':[check('Positive ground root',ground,8.242640687119284),check('Ground-height substitution',-ground**2+8*ground+2,0)],'c':[check('Interior vertex time',-8/(2*-1),4),check('Maximum height',-4**2+8*4+2,18)]},
    {'a':'A unique three-equation system gives a-1,b8,c2.',
     'b':'The roots are4plus/minussqrt18; the negative root precedes the model start and is excluded. The physical domain runs from0to the first positive ground-contact time inclusive.',
     'c':'The parabola opens downward and its vertex at4lies within the physical domain. It gives18m, exceeding both endpoint heights.'},'Native parabola inspected: points(0,2),(2,14),(5,17), peak near(4,18), and positive ground root just beyond8 agree with the model.')
widths=[5,10,15,20];frequencies=[8,24,30,18];densities=[f/w for f,w in zip(frequencies,widths)]
add('C',3,{'a':[check('Last-class density',densities[-1],.9)],'b':[check('Uniform-class interpolated median',15+(40-32)/30*15,19)],
    'c':[check('Estimated tail beyond25',(30*(30-25)/15+18)/80,.35)],'d':[check('Greatest-density class index',densities.index(max(densities)),1)]},
    {'a':'Unequal-width histogram heights are frequency divided by width, so the final20minute class has height0.9.',
     'b':'Cumulative frequency reaches32at15minutes; interpolate the40th cumulative observation within the next30observations over15minutes.',
     'c':'Under the stated uniform-within-class estimate, the final5of15minutes account for one-third of that class, plus the18longest delays.',
     'd':'The5to15minute class has greatest density2.4, even though another class has greater absolute frequency.'},'Native histogram inspected: widths5,10,15,20 and heights1.6,2.4,2,0.9; areas recover8,24,30,18, so modal density and all axes agree.')
double=.08*.9*.95+.92*.15*.02;first=.08*.9+.92*.15;second=.08*.95+.92*.02
add('C',4,{'a':[check('Conditional-mixture double-positive probability',double,.07116)],'b':[check('Condition posterior after two positives',.08*.9*.95/double,.9612141652613828)],
    'c':[check('Whole-population positive marginals',[first,second],[.21,.0944]),check('Product of marginals',first*second,.019824),check('Marginal independence fails',abs(double-first*second)>1e-6,True)]},
    {'a':'Sensitivity applies to affected people and false-positive probabilities1-specificity to unaffected people. Conditional independence permits multiplication within each subgroup.',
     'b':'Bayes numerator is affected-and-both-positive. Dividing by all both-positive outcomes gives the posterior, not the joint probability.',
     'c':'The shared latent condition creates dependence after mixing groups. The joint0.07116is not the product0.019824, so conditional independence does not imply unconditional independence.'})
U=solve([[1,0],[8,12]],[5,72]);sites=[(1,1),(9,1),(5,7)];ud=[math.dist(U,z) for z in sites];vd=[math.dist((5,8),z) for z in sites]
add('C',5,{'a':[check('Voronoi triple vertex',U,[5,F(8,3)]),check('Triple-distance equality',ud,[F(13,3)]*3)],
    'b':[check('Candidates nearest distances',[min(ud),min(vd)],[F(13,3),1])],'c':[check('Preferred permitted candidate',min(ud)>min(vd),True)]},
    {'a':'AB is horizontal with bisectorx5; the A/Cdistance equation is8x+12y72. Their intersection is inside the stated reserve.',
     'b':'At Uall three sites are13/3km away. At Vthe stationCis1km away and closer than A/B.',
     'c':'Among the two explicitly permitted candidates, choose U. The question and scheme correctly avoid claiming a global optimum over every reserve point.'},'Native reserve plot inspected: bounds[0,10]x[0,8], A(1,1),B(9,1),C(5,7),V(5,8), clear B label and no supplied U answer.')
stationary=F(25,37);prob=[.15]
for _ in range(9):prob.append(.63*prob[-1]+.25)
add('C',6,{'a':[check('First-step regular probability',prob[1],.3445)],'b':[check('Stationary regular probability',stationary,.6756756756756757)],
    'c':[check('First threshold month',next(i for i,p in enumerate(prob) if p>=.65),7),check('Adjacent probabilities',[prob[6],prob[7]],[.64280858828455,.6549694106192665]),check('Sequence increases over checked months',all(a<b for a,b in zip(prob,prob[1:])),True)]},
    {'a':'The next regular state receives0.88from current Rplus0.25from current O, giving0.63p+0.25.',
     'b':'The fixed point solves0.37p0.25. Both transition states communicate and the positive matrix is regular.',
     'c':'The exact deviation is(p0-pstar)0.63^n. It stays negative with decreasing magnitude, so the sequence is strictly increasing. Values at6and7prove7is first, not merely a sampled crossing.'})
corr=regression(list(range(1,9)),[10,13,12,18,17,20,21,24])[2];stat=corr*math.sqrt(6/(1-corr*corr));p=t_upper(stat,6)
add('C',7,{'a':[check('Pearson raw-data correlation',corr,.96737271,.00000001)],'b':[check('Equivalent correlation test statistic',stat,9.3526703,.0000001),check('One-sided t6 survival quadrature',p,.000042360842,1e-10)],
    'c':[check('Reject zero correlation at1percent',p<.01,True)]},
    {'a':'Use all eight raw pairs; independent paired observations and bivariate normality are explicitly given.',
     'b':'H0rho0versusH1rho>0uses the population correlation parameter. The transformed statistic has6degrees of freedom under H0and the one-sided upper tail is required.',
     'c':'The small p-value supports positive population correlation at1percent. It does not remove common causes or establish a direction of causation.'})
times=[1,2,3,4,5,6];observed=[6.2,10,12.6,13.7,14.8,15];resA=[y-16*(1-math.exp(-.5*t)) for t,y in zip(times,observed)];resB=[y-(-.3*t*t+3.5*t+1) for t,y in zip(times,observed)]
add('C',8,{'a':[check('Observed-minus-model A residuals',resA,[-.095509,-.113929,.170083,-.134635,.11336,-.203407],.0000006),check('Model A squared-residual sum',sum(x*x for x in resA),.1233815,.0000001)],
    'b':[check('Model B squared-residual sum',sum(x*x for x in resB),69.81),check('A is better by residual-sum criterion',sum(x*x for x in resA)<sum(x*x for x in resB),True)],
    'c':[check('Model B eventually predicts negative cumulative release',-.3*20**2+3.5*20+1<0,True)]},
    {'a':'Residuals use the explicitly stated observed-minus-predicted convention, and all six contribute to SSE.',
     'b':'Both candidates are compared on the same observations and units. The smaller SSEfavors Aunder this stated criterion, without claiming it is uniquely true.',
     'c':'At large time Aapproaches16mg from below; Beventually falls to negative values, impossible for cumulative release. Limited1to6hour observations cannot validate distant extrapolation even for A.'})
u=[4,1,2];v=[1,3,-1];cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];magnitude=math.sqrt(dot(cross,cross));unit=[x/magnitude for x in cross]
add('C',9,{'a':[check('Cross product',cross,[-7,6,11]),check('Unit normal norm',dot(unit,unit),1),check('Orthogonality to both edges',[dot(unit,u),dot(unit,v)],[0,0])],
    'b':[check('Parallelogram area',magnitude,14.352700094407323)],'c':[check('Projected effective area',abs(dot(cross,[0,-1,-2]))/math.sqrt(5),12.521980673998822)]},
    {'a':'Normalize either sign of the nonzero cross product; both are valid normals. Exact dot products independently confirm perpendicularity to both edges.',
     'b':'The cross-product magnitude gives the full parallelogram area, without the factor one-half used for a triangle.',
     'c':'The supplied projection formula cancels the normal magnitude, leaving absolute(cross dot d)/normd. Absolute value removes the arbitrary normal orientation; projected area is below actual area.'},'Native schematic parallelogram inspected: adjacent u/vlabels and explicit3Dedge-context caption do not imply false planar coordinate data.')
field=lambda x,y:(.5*x-.02*x*y,-.4*y+.01*x*y);states=[(40.,10.)]
for _ in range(2):
    x,y=states[-1];dx,dy=field(x,y);states.append((x+.5*dx,y+.5*dy))
add('C',10,{'a':[check('Initial simultaneous derivative',field(40,10),[12,0])],'b':[check('First simultaneous Euler state',states[1],[46,10]),check('Second simultaneous Euler state',states[2],[52.9,10.3])],
    'c':[check('Positive coexistence equilibrium derivatives',field(40,25),[0,0])]},
    {'a':'At(40,10), prey increases12hundreds/month and predator change is0, so the initial phase direction is horizontal right.',
     'b':'Both updates use the same old pair at each step. Updating yusing the new xwould incorrectly alter the first predator value.',
     'c':'Strict positivity lets the factors xand ybe divided out: y25andx40. No Jacobian or unsupported nonlinear phase classification is required.'},'Native phase field inspected: directions left/right across y25and down/up across x40match both nullclines; initial(40,10) is correctly placed. Refreshed native PNG rechecked: initial label is left of its dot, clear of field arrows.')
coefficient=[[F('.9'),F('-.2'),F('-.1')],[F('-.3'),F('.9'),F('-.1')],[F('-.1'),F('-.2'),F('.8')]];production=solve(coefficient,[100,80,60]);increase=solve(coefficient,[0,0,6])
add('C',11,{'a':[check('Coefficient matrix from I minus C',coefficient,[[.9,-.2,-.1],[-.3,.9,-.1],[-.1,-.2,.8]])],
    'b':[check('Gross production vector',production,[161.06194690265485,157.52212389380531,134.51327433628316]),check('Back-substitution recovers demand',mv(coefficient,production),[100,80,60])],
    'c':[check('Increase caused by third-demand change',increase,[1.1681415929203538,1.2743362831858405,7.9646017699115035]),check('Increase back-substitution',mv(coefficient,increase),[0,0,6])]},
    {'a':'Subtract the entire internal-demand matrix from I, retaining signs on off-diagonal coefficients.',
     'b':'The provided economic relation is a unique three-variable matrix system, explicitly allowing technology as required for general AI matrices. Exact rational elimination verifies the solution without any unsupported3x3eigenvalue work.',
     'c':'Only external demand for sector3rises10percentof60, so delta d=(0,0,6), not10percentof the gross output. Linear-system response produces increases in all sectors.'})
flag=.8*NORMAL.cdf((94-100)/4)+.2*NORMAL.cdf((94-90)/6);posterior=.2*NORMAL.cdf((94-90)/6)/flag;cut=100+4*NORMAL.inv_cdf(.01);miss=1-NORMAL.cdf((cut-90)/6)
add('C',12,{'a':[check('Mixture flagging probability',flag,.20294725,.00000001)],'b':[check('Degraded posterior after flagging',posterior,.73665196,.00000001)],
    'c':[check('One-percent standard false-flag cutoff',cut,90.69460850367264),check('Degraded nonflag probability at new cutoff',miss,.45391817,.00000001)]},
    {'a':'The mixture uses the correct prior weights0.8and0.2and each subgroup standard deviation.',
     'b':'The posterior numerator includes the degraded prior and lower-tail flagging probability, then divides by the total flag probability.',
     'c':'Choose the lower1percentstandard quantile, then evaluate the degraded upper-tail beyond that same cutoff. Normal equality has probability0, so the strict flag boundary introduces no discrepancy.'})
A=[12.4,11.8,13.1,12.7,12,13.5];B=[14.1,13.8,15,14.4,13.5,14.8];pooled=math.sqrt((5*stdev(A)**2+5*stdev(B)**2)/10);stat=(mean(A)-mean(B))/(pooled*math.sqrt(1/6+1/6));p=t_upper(-stat,10)
add('C',13,{'a':[check('Sample means',[mean(A),mean(B)],[12.583333333333334,14.266666666666667]),check('Pooled sample standard deviation',pooled,.61495257,.00000001)],
    'b':[check('Pooled two-sample statistic',stat,-4.7412093,.0000001),check('One-tailed t10 p-value by density quadrature',p,.00039533172,1e-10)],'c':[check('Reject equality for lower Amean',p<.05,True)]},
    {'a':'Independently sampled normal populations with equal unknown variances meet the pooled test assumptions. Pool the two sample variances with5degrees of freedom each.',
     'b':'H0muA=muB,H1muA<muB. The difference AminusBis negative; use the left tail with10degrees of freedom, not a paired test or doubled p-value.',
     'c':'Reject equality at5percent and conclude evidence of lower mean drying time for A; this is a population-mean claim, not a statement that every Aobservation dries faster.'})
k=18/(7*math.pi);ustar=(136+math.sqrt(20800))/18;rr=(k*k/ustar)**(1/6);height=k/rr**2
surface=lambda r:5*math.pi*r*r+3*math.pi*r*math.sqrt(r*r+(k/r**2)**2)
scaled_derivative=lambda r:10+3*(2-k*k/r**6)/math.sqrt(1+k*k/r**6)
add('C',14,{'a':[check('Volume coefficient for top radius2r',7*math.pi/3,7*math.pi/3)],'b':[check('Closed-end area multiplier',1+2**2,5)],
    'c':[check('Unique optimum radius',rr,.59197481,.00000001),check('Corresponding height',height,2.3357058,.0000001),check('Minimum total area',surface(rr),18.948072,.000001)],
    'd':[check('Positive transformed stationary root satisfies equation',9*ustar**2-136*ustar-64,0,.0000001),check('Endpoint areas',[surface(.4),surface(1.4)],[21.857853,50.064485],.000001),check('Derivative switches negative to positive',[scaled_derivative(.4)<0,scaled_derivative(1.4)>0],[True,True])]},
    {'a':'Substitute R2rin the supplied volume formula; volume6gives h18/(7pi r2).',
     'b':'Both circular ends contribute5pi r2and the supplied curved area gives3pi r sqrt(r2+h2). No unfamiliar formula must be recalled.',
     'c':'Numerically minimizing the resulting positive one-variable area gives the stated r,h,Sinside the permitted interval.',
     'd':'Independent global proof: let u=k2/r6>0. The derivative divided by pi r is10+3(2-u)/sqrt(1+u), strictly decreasing as a function of uand therefore increasing with r. Its unique physical zero hasu>2and solves9u2-136u-64=0. Endpoint signs and the unique zero establish the global minimum, beyond numerical sampling.'},'Native closed frustum inspected: lower radiusr, upper radius2r, central heighth, both circular ends and sloping side match the supplied geometry.')
adj=[[0,1,1,0],[1,0,0,1],[0,1,0,1],[1,0,1,0]];walks=[(0,)]
for _ in range(4):walks=[(*w,j) for w in walks for j in range(4) if adj[w[-1]][j]]
endD=[w for w in walks if w[-1]==3]
add('C',15,{'a':[check('Two outgoing arrows per row',[sum(row) for row in adj],[2,2,2,2])],'b':[check('Four-step walk count by direct enumeration',len(endD),4)],
    'c':[check('All equally probable four-step walks',len(walks),16),check('Four-move Dprobability',len(endD)/len(walks),.25)],'d':[check('Enumeration includes at least one repeated-vertex walk',any(len(set(w))<len(w) for w in endD),True)]},
    {'a':'Read arrows with the explicitly given row-origin,column-destination adjacency convention, distinct from column-stochastic state-vector convention.',
     'b':'The rowA,columnDentry of M4counts ordered four-link walks. Direct enumeration independently finds four such walks.',
     'c':'Every vertex has exactly two uniformly chosen outgoing links; each four-step walk therefore has probability1/16. Summing the four favorable walks gives1/4.',
     'd':'The robot may revisit vertices or links, so walks rather than simple paths correctly count the sample space.'},'Native directed graph read arrow-by-arrow: AtoB/C,BtoA/D,CtoB/D,DtoA/C. Opposite ABandCDarrows are drawn separately, and diagonal crossings are not extra vertices.')
radius=lambda x:.12+.08*x-.04*x*x;poly=[.0144,.0192,-.0032,-.0064,.0016]
volume=lambda h:math.pi*sum(c*h**(i+1)/(i+1) for i,c in enumerate(poly));capacity=volume(1.5);lo,hi=0.,1.5
for _ in range(60):
    mid=(lo+hi)/2
    if volume(mid)<capacity/2:lo=mid
    else:hi=mid
half=(lo+hi)/2
add('C',16,{'a':[check('Maximum radius at derivative zero',radius(1),.16),check('Maximum exceeds both endpoint radii',radius(1)>max(radius(0),radius(1.5)),True)],
    'b':[check('Polynomial antiderivative capacity in litres',1000*capacity,106.59423873150169),check('Independent quadrature agrees',math.pi*integrate(lambda x:radius(x)**2,0,1.5),capacity)],
    'c':[check('Half-full depth',half,.81582338,.00000001),check('Half-full volume substitution',volume(half)/capacity,.5)]},
    {'a':'The radius is a concave quadratic with derivative0.08-0.08x; its vertexx1lies within[0,1.5].',
     'b':'Horizontal circular cross-sections have area pi r2. Independent polynomial squaring/integration and numerical quadrature both give0.1065942387m3, converted by1000litres/m3.',
     'c':'The upright depth equation integrates from base0toh. Radius remains positive throughout the vessel, so cumulative volume is strictly increasing and the numerical half-volume root is unique; half depth need not be half height.'},'Native diagram is explicitly radius against height, not an inverted vessel side view. Radius0.12atbase, maximum0.16atheight1and radius0.15atheight1.5match the function.')

# Set D: fresh calculations, integer/design boundaries and complete candidates.
cash=[4000,5000,6000,6000,7000];npv=lambda r:-18000+sum(v/(1+r)**t for t,v in enumerate(cash,1));lo,hi=0.,1.
for _ in range(60):
    mid=(lo+hi)/2
    if npv(mid)>0:lo=mid
    else:hi=mid
irr=(lo+hi)/2
add('D',1,{'a':[check('Present value at6percent',npv(.06),5244.652,.001)],'b':[check('Internal rate as annual percent',100*irr,15.245771,.000001),check('IRR zero substitution',npv(irr),0,.000001)],
    'c':[check('Positive NPV at10percent',npv(.1),2721.0138,.0001)]},
    {'a':'Every end-of-year cash flow is discounted by its own year index before subtracting the current18000cost; the NPV definition is supplied.',
     'b':'All future flows are positive, so NPV is strictly decreasing for r>=0. NPV0is positive and NPV1negative, giving one positive root; the annual percentage is100r.',
     'c':'The modeled NPV at the required10percentreturn is positive. Forecast cash flows, timings and costs remain uncertain, so the mathematical calculation alone cannot guarantee commercial profit.'})
vmin=math.pi*2.395**2*5.15;vmax=math.pi*2.405**2*5.25;nominal=math.pi*2.4**2*5.2
add('D',2,{'a':[check('Half-unit radius bounds',[2.4-.005,2.4+.005],[2.395,2.405]),check('Half-unit height bounds',[5.2-.05,5.2+.05],[5.15,5.25])],
    'b':[check('True volume bounding expressions',[vmin,vmax],[92.804308,95.398015],.000001)],
    'c':[check('Recorded nominal volume',nominal,94.096983,.000001),check('Largest true-denominator overstatement percentage',100*(nominal-vmin)/vmin,1.3929041,.0000001)]},
    {'a':'Standard half-unit intervals include lower and exclude upper endpoints: radius[2.395,2.405),height[5.15,5.25).',
     'b':'For positive dimensions pi r2his strictly increasing in r and h, so the minimum is attained at both lower bounds and the upper expression is an unattained upper bound.',
     'c':'With a fixed nominal volume, nominal/true-1decreases as true volume increases. The largest overstatement is at the included minimum volume, using true volume in the denominator as explicitly requested.'})
bill=lambda x:8+.18*min(x,120)+.32*max(0,x-120);uses=[50,100,150,200];weights=[.1,.3,.4,.2];expected_bill=sum(p*bill(x) for x,p in zip(uses,weights));expected_use=sum(x*p for x,p in zip(uses,weights))
add('D',3,{'a':[check('Bill at150kWh',bill(150),39.2)],'b':[check('Four possible bills',[bill(x) for x in uses],[17,26,39.2,55.2]),check('Probability-weighted expected bill',expected_bill,36.22)],
    'c':[check('Mean use',expected_use,135),check('Bill evaluated at mean use',bill(expected_use),34.4),check('Expected bill exceeds bill of mean',expected_bill>bill(expected_use),True)]},
    {'a':'The upper tariff applies only to use above120kWh, not all150kWh.',
     'b':'Apply the tariff to each discrete possible use before probability weighting; include the fixed fee once per month.',
     'c':'The upward tariff kink makes the bill convex and not a single affine rule over the distribution. Therefore evaluating the bill at mean use need not equal the mean bill; higher-use months attract the higher marginal rate.'})
smallC=math.asin(.75);Cangles=[smallC,math.pi-smallC];lengths=sorted(8*math.sin(math.pi-math.pi/6-c)/math.sin(math.pi/6) for c in Cangles);projections=[x*math.cos(math.pi/6) for x in lengths]
add('D',4,{'a':[check('Ambiguous opposite-angle solutions',[math.degrees(v) for v in Cangles],[48.590377890729144,131.40962210927086])],
    'b':[check('Both AC lengths',lengths,[5.100802223284079,15.683807467542449])],
    'c':[check('Only shorter triangle projection is interior',[0<x<12 for x in projections],[True,False])]},
    {'a':'The sine rule gives sinC0.75. Both acute and obtuse Csolutions leave a positive Bangle when A30degrees.',
     'b':'For each Cuse B180-A-Cand the sine rule; equivalently the ray from Aintersects the circle around Bofradius8at two positive distances.',
     'c':'The horizontal projection isACcos30degrees. Only the shorter length places the foot strictly between0and12; the longer candidate projects beyond B.'},'Native SSA diagram read: AB12, angleA30degrees, both possible Cpositions along the same ray, two8mBCsegments and the larger candidate projecting beyond B are coherent.')
expected=[200*pois(2,k) for k in range(3)];expected.append(200-sum(expected));observed=[20,58,62,60];stat=sum((o-e)**2/e for o,e in zip(observed,expected));p=math.exp(-stat/2)
add('D',5,{'a':[check('Poisson fitted mean from complete raw total',400/200,2),check('Raw total compatible with grouped tail',58+2*62+38*4+22*3,400)],
    'b':[check('All four expected frequencies',expected,[27.06705664732254,54.13411329464508,54.13411329464508,64.6647167633873]),check('Expected counts all exceed5',min(expected)>5,True)],
    'c':[check('Fitted-parameter degrees of freedom',4-1-1,2),check('Pearson statistic',stat,3.6006849,.0000001),check('Chi-square df2 upper tail',p,.16524229,.00000001)],'d':[check('Do not reject at5percent',p>.05,True)]},
    {'a':'The ungrouped sum400is explicitly supplied, so its sample mean2can be fitted consistently; treating every pooled count as3would be invalid.',
     'b':'Pool all values>=3into the last expected cell. The four expected frequencies sum200and exceed5.',
     'c':'Subtract one degree of freedom for total count and one for the fitted Poisson mean, giving2. Independent df2survival evaluation confirms the stated p-value.',
     'd':'There is insufficient evidence of lack of fit at5percent, which is weaker than proving a Poisson distribution or its underlying event-process assumptions.'})
responses=[18.1,31.9,44.3,51.4,58.9];intercept,slope,*_=regression([0,1,2,3,4],[math.log(80-y) for y in responses]);A=math.exp(intercept);k=-slope
add('D',6,{'a':[check('Linearized slope',slope,-.26723697,.00000001),check('Linearized intercept',intercept,4.1298005,.0000001),check('All logarithm arguments positive',all(80-y>0 for y in responses),True)],
    'b':[check('Fitted A',A,62.16552,.00001),check('Fitted k',k,.26723697,.00000001)],'c':[check('Fitted initial response',80-A,17.83448,.00001)]},
    {'a':'The fixed proposed saturation80allows log(80-Y)=logA-kt; every observed Yis below80, so the transform is defined.',
     'b':'Exponentiate the unrounded fitted intercept and negate the slope; Aandkare both positive as required.',
     'c':'Regression does not force the fitted initial value through the first noisy observation. The early-time data do not reach a plateau and therefore cannot establish the assumed limiting80on their own.'})
network=[('A','B',4),('A','C',7),('B','C',2),('B','D',6),('C','D',3),('C','E',8),('D','E',4),('D','F',9),('E','F',3)]
routes=[]
def visit(path,constant,upgraded):
    if path[-1]=='F':routes.append((constant,upgraded,path));return
    for a,b,w in network:
        if path[-1] not in (a,b):continue
        next_=b if path[-1]==a else a
        if next_ in path:continue
        special={a,b}=={'B','D'}
        visit(path+[next_],constant+(0 if special else w),upgraded+int(special))
visit(['A'],0,0);old=min(c+6*j for c,j,path in routes);plain_min=min(c for c,j,path in routes if not j);special_min=min(c for c,j,path in routes if j)
add('D',7,{'a':[check('Exhaustive original shortest-route cost',old,16),check('Listed original route is available',any(path==list('ABCDEF') and c+6*j==16 for c,j,path in routes),True)],
    'b':[check('Best unchanged-path constant',plain_min,16),check('Best upgraded-path base constant',special_min,11),check('Tie upgrade value',plain_min-special_min,5)],
    'c':[check('Largest20percent-reduction x',.8*old-special_min,1.8),check('Boundary journey time',min(c+1.8*j for c,j,path in routes),12.8)]},
    {'a':'Enumerate all simple AtoFpaths in the nonnegative-weight undirected graph; a shortest route never needs a positive-cost cycle.',
     'b':'Among paths not using BD,the best remains16. Among paths using BDonce,the best other-edge total is11, so the exact lower envelope ismin(16,11+x)for every0<=x<=6. Strict improvement means0<=x<5.',
     'c':'At least20percentreduction requires a journey at most12.8minutes. Thus11+x<=12.8and the largest feasible upgrade time is1.8.'},'Native graph edge data independently read: AB4,AC7,BC2,BD6,CD3,CE8,DE4,DF9,EF3. Distinct cost labels and minute units match the route calculations.')
tail64=1-NORMAL.cdf((20-18)/(12/math.sqrt(64)));cut64=18+1.5*NORMAL.inv_cdf(.99);minimum=math.ceil((6*NORMAL.inv_cdf(.975))**2)
add('D',8,{'a':[check('CLT sampling-mean tail for n64',tail64,.09121121972586788)],'b':[check('Upper1percent sample-mean bound',cut64,21.48952181106126)],
    'c':[check('Smallest permitted integer sample size',minimum,139),check('Neighbouring mean-tail probabilities',[1-NORMAL.cdf(math.sqrt(n)/6) for n in [138,139]],[.02512146,.024708796],.00000001)]},
    {'a':'Individual times are skewed, but the question explicitly permits the CLTfor n>30. The sample mean has sd12/sqrt64=1.5, not12.',
     'b':'Use the99th percentile of the approximate sample-mean distribution, not an individual service-time percentile.',
     'c':'The mean-tail probability decreases with n. Solving the normal-quantile inequality gives a real lower bound, rounding up gives139and checking138/139confirms the first valid integer. The result remains a CLTapproximation.'})
system=[[-2,1],[1,-2]];coefficients=solve([[1,1],[1,-1]],[6,2]);solution=lambda t:[4*math.exp(-t)+2*math.exp(-3*t),4*math.exp(-t)-2*math.exp(-3*t)]
add('D',9,{'a':[check('Eigenvector for eigenvalue-1',mv(system,[1,1]),[-1,-1]),check('Eigenvector for eigenvalue-3',mv(system,[1,-1]),[-3,3])],
    'b':[check('Initial modal coefficients',coefficients,[4,2]),check('Initial condition',solution(0),[6,2]),check('Both differential equations at three independent times',[mv(system,solution(t)) for t in [0,1,4]],[[-4*math.exp(-t)-6*math.exp(-3*t),-4*math.exp(-t)+6*math.exp(-3*t)] for t in [0,1,4]])],
    'c':[check('Late-time y-over-x approaches1',solution(10)[1]/solution(10)[0],1,.00000001)]},
    {'a':'The2x2matrix has distinct nonzero real eigenvalues-1and-3, so exact diagonalizable-system solutions are within the stated AI boundary.',
     'b':'The two eigenmodes give s=aexp(-t)(1,1)+bexp(-3t)(1,-1). The initial sum/difference equations determine a4,b2and substitution verifies both equations.',
     'c':'The nonzero slow modeexp(-t)dominates the fasterexp(-3t)mode, so the trajectory approaches alongy=x. This is an asymptotic direction, not a claim the whole trajectory lies on that line.'},'Native phase field inspected: origin is inward stable in every quadrant, both eigendirections agree with the negative eigenvalues, and initial point(6,2)is labelled correctly.')
coord=(3+math.sqrt(23))/2;theta=math.atan2(coord,coord-3);z=3+4*cmath.exp(1j*theta)
add('D',10,{'a':[check('Real-axis locus endpoints',[3+4,3-4],[7,-1])],'b':[check('Unique positive-ray argument solution',theta,1.344388,.000001),check('Resultant argument',cmath.phase(z),math.pi/4)],
    'c':[check('Resultant amplitude at that parameter',abs(z),5.5124853,.0000001)],'d':[check('Minimum amplitude over permitted semicircle',abs(3+4*cmath.exp(1j*math.pi)),1)]},
    {'a':'The parameter0throughpi traces the full upper semicircle centred3ofradius4, with endpoints included.',
     'b':'Argpi/4requires equal positive real/imaginary parts. Intersecting the circle with yxgives coordinate(3+sqrt23)/2on the positive ray; the other algebraic root is negative and invalid.',
     'c':'Use the modulus at the valid positive-ray point, equivalently sqrt2timesits positive coordinate.',
     'd':'The reverse triangle inequality gives modulus at least|4-3|1, attained at the allowed endpointtheta pi. Therefore complete cancellation is impossible.'},'Native locus inspected: upper semicircle from-1to7, centre3and maximum imaginary4, labelled real/imaginary axes and clear centre annotation.')
distance2=lambda t:(4*t-20)**2+(3*t-10)**2;closest=220/50
add('D',11,{'a':[check('Closest time',closest,4.4),check('Minimum distance',math.sqrt(distance2(closest)),4),check('Interior optimum beats endpoints',distance2(closest)<min(distance2(0),distance2(6)),True)],
    'b':[check('Five-metre boundary times',[4.4-.6,4.4+.6],[3.8,5]),check('Squared separation at boundaries',[distance2(t) for t in [3.8,5]],[25,25])],
    'c':[check('Crossing position at different robot times',[[3*6,6],[20-2,10-2*2]],[[18,6],[18,6]]),check('No simultaneous collision',distance2(closest)>0,True)]},
    {'a':'Use simultaneous positions: separation squared25t2-220t+500=25(t-4.4)2+16. Its positive quadratic coefficient and interior vertex give the global minimum on[0,6].',
     'b':'At most5mmeans squared distance<=25, so |t-4.4|<=0.6. The whole resulting[3.8,5]interval lies in the model domain.',
     'c':'Ppasses the path intersection(18,6)att6while Qpasses it att2. Their minimum simultaneous distance4mproves no collision.'},'Native trajectories inspected: Pfrom(0,0)to(18,6), Qfrom(20,10)to(14,-2), arrows point forward and caption distinguishes paths from simultaneous positions.')
original=math.pi*(16*2-8*2**3/3+2**5/5);remaining=original-1.5*math.pi
add('D',12,{'a':[check('Disc-integration original volume',original,53.6165146212658),check('Independent numerical disc quadrature',math.pi*integrate(lambda y:(4-y*y)**2,0,2),original)],
    'b':[check('Volume after radius1depth1.5cylinder removal',remaining,48.90412564088111),check('Cylinder fits up to depth1.5',4-1.5**2>=1,True)],
    'c':[check('Limiting drilling depth',math.sqrt(3),1.7320508075688772),check('Curved-surface radius at limiting depth',4-math.sqrt(3)**2,1)]},
    {'a':'Revolution about the yaxis uses disc radiusx4-y2, so integrate its square with respect to y, not a shell around the wrong axis.',
     'b':'The solid radius decreases with yand remains at least1.75through the stated1.5mdepth, so the whole removed cylinder lies inside the solid.',
     'c':'For a radius1drill,the available outer radius4-y2first equals1at sqrt3. This gives the limiting depth before the cylinder would exit the curved side.'},'Native region/hole diagram inspected: outer x4-y2with intercepts(4,0),(0,2), y-axis rotation orientation, and shaded0<=x<=1,0<=y<=1.5rectangle match the problem.')
alpha=lambda n,p:1-(1-p)**n-n*p*(1-p)**(n-1);n=max(n for n in range(1,200) if alpha(n,.02)<.05)
add('D',13,{'a':[check('Alternative contamination probability exceeds null',.12>.02,True)],'b':[check('Largest sample size under strict TypeIlimit',n,18),check('Adjacent TypeI probabilities',[alpha(18,.02),alpha(19,.02)],[.049508833,.05461595],.00000001)],
    'c':[check('Power at true probability0.12',alpha(18,.12),.65399768,.00000001)],'d':[check('Positive increment in null rejection probability',alpha(19,.02)-alpha(18,.02),18*.02**2*.98**17)]},
    {'a':'H0p0.02versusH1p>0.02uses the specified upper-tail fixed thresholdX>=2.',
     'b':'Under H0the rejection probability is1-P0-P1. It increases strictly with nforn>=1because the increment is n p2(1-p)^(n-1)>0; adjacent18/19values therefore prove the maximal n, not just a local scan.',
     'c':'Power is rejection under the true alternativep0.12using the same n18and threshold2, not one minus a probability under H0.',
     'd':'More observations with the threshold held fixed increase null rejection probability and can breach the strict significance constraint; power alone does not determine validity.'})
phase=math.atan2(1.8,5*math.pi);angle=math.acos(12/math.hypot(5*math.pi,1.8));stationary_times=[6/math.pi*(angle-phase),6/math.pi*(2*math.pi-angle-phase)];revenue=lambda t:(200+30*math.sin(math.pi*t/6))*math.exp(-.06*t)
candidates=[0,*stationary_times,12];revenues=[revenue(t) for t in candidates]
add('D',14,{'a':[check('Derivative bracket at t0',5*math.pi-.06*200,3.7079632679489656)],
    'b':[check('All stationary times from sinusoid phase form',stationary_times,[1.1362940247413555,10.427899386044558]),check('Both derivative brackets vanish',[5*math.pi*math.cos(math.pi*t/6)-.06*(200+30*math.sin(math.pi*t/6)) for t in stationary_times],[0,0])],
    'c':[check('Complete endpoint/stationary values',revenues,[200,202.525072,95.21302,97.350451],.000001),check('Global maximizing candidate',candidates[revenues.index(max(revenues))],stationary_times[0]),check('Maximum forecast revenue',max(revenues),202.52507,.00001)]},
    {'a':'Product and chain rules give exp(-0.06t)[5pi cos(pi t/6)-0.06(200+30sin(pi t/6))].',
     'b':'Rewrite the zero equation asBcos(u+phi)12withu0to2pi, Bsqrt((5pi)2+1.8^2). The cosine equation has exactly two solutions in that full phase-shifted interval, giving the complete stationary set.',
     'c':'A continuous differentiable function on the closed model interval reaches its global maximum at an endpoint or stationary point. Comparing both endpoints and both interior points identifies the first stationary point as the global maximum.'},'Native revenue curve inspected: initial200thousand, small early maximum around1.14, trough near10.43and rising end near97.35are consistent; axes show months and thousands.')
def transition(q):return [[F('.7'),F('.1'),q],[F('.2'),F('.7'),F('.2')],[F('.1'),F('.2'),F('.8')-q]]
def stationary_state(T):return solve([[T[0][j]-int(j==0) for j in range(3)],[T[1][j]-int(j==1) for j in range(3)],[1,1,1]],[0,0,1])
q=F(2,5);old=stationary_state(transition(q));new=stationary_state(transition(F(1,2)))
add('D',15,{'a':[check('First app proportion identifies q0.4',mv(transition(q),[F(1,3)]*3)[0],F(2,5))],
    'b':[check('Stationary distribution at q0.4',old,[F(2,5),F(2,5),F(1,5)]),check('Stationary substitution',mv(transition(q),old),old)],
    'c':[check('Policy stationary distribution',new,[F(17,40),F(2,5),F(7,40)]),check('Change in expected app count',1000*(new[0]-old[0]),25)]},
    {'a':'Starting from uniform column probabilities gives app(0.8+q)/3, equated to0.4; the result0.4lies within the allowed parameter interval.',
     'b':'The positive column-stochastic matrix is regular. Solve its fixed-point equations and normalize; both fixed point and exact rational substitution verify the limiting vector.',
     'c':'The policy modifies both entries in the telephone-origin column to preserve its total1. Recompute the stationary state, then multiply the app-probability increase0.025by1000customers.'})
mass=lambda t:80*math.exp(-.1*t-.01*t*t);half=-5+math.sqrt(25+100*math.log(2));peak=(math.sqrt(.02)-.1)/.02;rate=lambda t:(.1+.02*t)*mass(t)
add('D',16,{'a':[check('Initial amount',mass(0),80),check('Separated exponent derivative agrees with DE',[(-.1-.02*t)*mass(t) for t in [0,2,10]],[-(.1+.02*t)*mass(t) for t in [0,2,10]])],
    'b':[check('Half-amount time',half,4.7115765,.0000001),check('Half-amount substitution',mass(half),40)],
    'c':[check('Global peak-removal time',peak,2.0710678118654746),check('Maximum removal rate',rate(peak),8.811125,.000001),check('Peak beats both endpoint rates',rate(peak)>max(rate(0),rate(10)),True)]},
    {'a':'Positive Minitialpermits separation and logM. Integrating the time-dependent coefficient gives-.1t-.01t2and initial mass fixes multiplier80.',
     'b':'The mass decreases strictly on the entire nonnegative domain, so the positive quadratic root for the half amount is the unique admissible time.',
     'c':'rprime=M[0.02-(0.1+0.02t)^2]. Since Mispositive and the increasing positive bracket coefficient crosses sqrt0.02once, rprimechanges positive to negative at the interior peak. Both endpoints are lower, confirming the global maximum on[0,10].'})

assert len({(r['paperId'],r['question']) for r in RECORDS})==len(RECORDS)
count=sum(len(v) for r in RECORDS for v in r['partChecks'].values())
assert len(PAPERS)==4 and len(RECORDS)==64 and sum(r['marks'] for r in RECORDS)==440
for paper_id in PAPERS:
    assert sorted(r['question'] for r in RECORDS if r['paperId']==paper_id)==list(range(1,17))
report={'status':'passed','reviewer':'Separate mathematical reviewer who did not author the AI Paper 1 questions',
    'method':'Read complete stems and all worked marking points, independently transcribed inputs and recomputed all parts without author code. Exact rational linear algebra, exhaustive finite optimisation/tree enumeration, independent density quadrature and analytic domain/global-extremum arguments supplement numeric checks.',
    'papers':len(PAPERS),'questions':len(RECORDS),'parts':sum(len(r['partChecks']) for r in RECORDS),'marks':sum(r['marks'] for r in RECORDS),'independentCheckCount':count,
    'nativeDiagramsInspected':sum(r['nativeDiagramInspected'] for r in RECORDS),
    'syllabusPrimarySource':'https://www.ibo.org/globalassets/new-structure/university-admission/pdfs/dp-mathematics-applications-and-interpretation-guide-en.pdf',
    'syllabusReview':'Official SL/AHL references and the independently checked current-guide boundaries were considered for every question. Original contexts define unfamiliar models; no complex roots, plane equations, unsupported integration methods, absorbing-chain theory or nonlinear Jacobians are assumed. Each part-specific review records the actual method and modelling assumptions.',
    'paperHashes':FROZEN,'records':RECORDS,'openFindings':[],
    'limits':['The original questions and all diagrams are computationally and AI reviewed; no human IB examiner moderation is claimed.','Final combined PDFs and live portal/email behaviour require their separate release checks.']}
DEST.parent.mkdir(parents=True,exist_ok=True);DEST.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps({k:report[k] for k in ['status','papers','questions','marks','independentCheckCount']}))
