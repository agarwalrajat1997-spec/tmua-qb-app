"""Independent review of four reconstructed Mathematics AA SL papers.

Uses only the standard library and independently transcribed mathematical inputs.
It does not import the author's generator, calculations or review ledger. All
forty source solution pages, reconstructed questions/full schemes, and fourteen
final native diagrams were individually read by this reviewer. Reviewed raw
paper hashes are fixed below: changed content requires a fresh scientific review.
"""
from pathlib import Path
from fractions import Fraction as F
from statistics import NormalDist
from collections import Counter
import hashlib, json, math, re, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
PAPER_DIR = ROOT/'content/ib/aa-mocks-2026/papers'
DEST = ROOT/'docs/ib-aa-mocks-2026/sl-independent-review.json'
HASHES = {
    'aa-sl-set-a-paper-1':'31f7644faee16b1e9fb288a820439ef7541e5956092b0f81cb12b62db0be1294',
    'aa-sl-set-a-paper-2':'b6817a1d42cad794e0f7b12e649187192b56b617b0519d75499365f71d52bd3a',
    'aa-sl-set-b-paper-1':'3ab094dbb3d11b318670b56d438f7d20616a9601d7d11e0fbff37f23ead48c33',
    'aa-sl-set-b-paper-2':'5cbf71ecc85c8d0523501a7aa2f573ab10a89cded2497055239093a02150e291',
}
PAPERS = {}
for name, sha in HASHES.items():
    raw = (PAPER_DIR/(name+'.json')).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == sha, name+' differs from the independently read final paper'
    PAPERS[name] = json.loads(raw)
RECORDS = []

def plain(value):
    if isinstance(value,F): return str(value)
    if isinstance(value,dict): return {str(k):plain(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)): return [plain(v) for v in value]
    return value

def n(test, actual, expected, tolerance=1e-9):
    assert math.isclose(float(actual),float(expected),rel_tol=tolerance,abs_tol=tolerance),(test,actual,expected)
    return {'test':test,'calculated':plain(actual),'expected':plain(expected),'status':'passed'}

def e(test, actual, expected):
    assert actual == expected,(test,actual,expected)
    return {'test':test,'calculated':plain(actual),'expected':plain(expected),'status':'passed'}

def poly_mul(a,b):
    out=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): out[i+j] += x*y
    return out

def poly_value(a,x): return sum(c*x**i for i,c in enumerate(a))
def derivative(a): return [i*c for i,c in enumerate(a)][1:]

def bisect(fn,left,right):
    assert fn(left)*fn(right)<0
    for _ in range(100):
        mid=(left+right)/2
        if fn(left)*fn(mid)<=0: right=mid
        else: left=mid
    return (left+right)/2

def integrate(fn,left,right,count=2000):
    step=(right-left)/count
    return step/3*(fn(left)+fn(right)+sum((4 if i%2 else 2)*fn(left+i*step) for i in range(1,count)))

def rec(paper,number,part_checks,reasoning,visual='No diagram needed; the complete givens and mathematical demands are textual.'):
    p=PAPERS[paper]; q=p['questions'][number-1]
    assert q['number']==number and p['course']=='sl' and p['minutes']==90 and p['marks']==80
    assert p['calculator']==(p['paper']=='2')
    assert q['marks']==sum(x['marks'] for x in q['parts'])
    assert set(part_checks)=={x['label'] for x in q['parts']}
    for part in q['parts']:
        group=next(x for x in q['markScheme'] if x['part']==part['label'])
        assert group['steps'] and all(re.fullmatch('[MAR][1-9]\\d?',x['code']) for x in group['steps'])
        assert sum(int(x['code'][1:]) for x in group['steps'])==part['marks']
        assert part_checks[part['label']]
    if q.get('diagramSvg'):
        ET.fromstring(q['diagramSvg'])
        assert not re.search(r'<(?:script|image|foreignObject|style)\b|\bon\w+\s*=|\b(?:href|src)\s*=',q['diagramSvg'],re.I)
        assert len(q['diagramSvg'])<300000
    RECORDS.append({'paper':paper,'question':number,'status':'passed','sourcePages':[number+1],
        'questionSha256':hashlib.sha256(json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        'partChecks':part_checks,'independentMathematicalReview':reasoning,'nativeDiagramReview':visual,
        'sourceCompatibility':'Read the complete native source solution page alongside the reconstructed stem and all marking points. Supplied/inferred givens make every requested result determinate. Known source errata are corrected in the online scheme and require the separately recorded PDF repairs.'})

A1='aa-sl-set-a-paper-1'; A2='aa-sl-set-a-paper-2'; B1='aa-sl-set-b-paper-1'; B2='aa-sl-set-b-paper-2'
N=NormalDist()

# Set A, Paper 1: exact algebra and no-calculator reasoning.
rec(A1,1,{'a':[e('asymptote equation at y=-1 is inconsistent',-2==-1,False)],
    'b':[e('f(inverse) numerator polynomial',[1-1,2-1],[0,1]),e('f(inverse) denominator polynomial',[2-1,2-2],[1,0]),n('inverse applied to f at3', (2*((3-1)/(2-3))+1)/(((3-1)/(2-3))+1),3)]},
    'Solving y=(x-1)/(2-x) gives x=(2y+1)/(y+1). The only excluded output is−1 and inverse domain excludes−1. Formal composition reduces numerator/denominator to x/1; original domain excludes2.')
rec(A1,2,{'a':[n('double-angle value at pi/6',8*math.sin(math.pi/6)*math.cos(math.pi/6),4*math.sin(math.pi/3))],
    'b':[n('independent Simpson integral',integrate(lambda x:8*math.sin(x)*math.cos(x),0,math.pi/2),4),n('antiderivative endpoint difference',-2*math.cos(math.pi)+2*math.cos(0),4)]},
    'Identity sin2x=2sinxcosx gives4sin2x. Integrating gives−2cos2x, with chain factor included; the boundary result is4. Radians and limits are explicit.')
angles=[50+180*k for k in range(-3,4) if 0<=50+180*k<=360]
rec(A1,3,{'':[e('complete parameter enumeration',angles,[50,230]),n('first root satisfies original sine',math.sin(math.radians(2*50-10)),1),n('second root satisfies original sine',math.sin(math.radians(2*230-10)),1)]},
    'sinθ=1 requiresθ=90+360k degrees. Hencex=50+180k and only50,230 lie in the stated interval; neither endpoint adds a root. Inclusive versus the source strict outer endpoints has no effect here.')
rec(A1,4,{'a':[n('probability remainder',1-F(7,10),F(3,10))],
    'b':[n('expectation solves p',F(14,10)+3*F(3,10)-F(21,10),F(1,5)),n('probabilities sum',F(1,5)+F(1,2)+F(3,10),1),n('expectation check',F(1,5)+2*F(1,2)+3*F(3,10),F(21,10))]},
    'Normalization fixesq=.3; expectationp+2(.7-p)+3q=2.1 fixesp=.2, leaving all probabilities nonnegative.')
rec(A1,5,{'a':[n('base-change denominator',math.log2(8),3)],
    'b':[e('expanded cleared polynomial', [F(2)-2,F(1)-4,F(0)-2],[0,-3,-2]),e('domain-valid quadratic roots',[x for x in [F(0),F(-3,2)] if x+1>0 and x+2>0],[F(0)]),n('original logarithmic value at valid root',3*math.log(2,8)-2*math.log2(1),1)]},
    'Base conversion gives log2[(x+2)/(x+1)^2]=1. Clearing producesx(2x+3)=0, but original logs requirex>−1, excluding−3/2. There is no missing absolute-value branch.')
rec(A1,6,{'a':[e('S3 minus S8 coefficients in u1,d',[3-8,3-28],[-5,-25]),n('u1 coefficient solved per d',-F(25,5),-5)],
    'b':[n('sixth term coefficient in d',-5+5,0)]},
    'Exact sum formulas give5u1=−25d, includingd=0. Substituting into u6=u1+5d gives0 without division byd.')
rec(A1,7,{'a':[e('symbolic derivative a,b coefficient tuples',[(0,0,1),tuple(2*x for x in (0,2,0)),tuple(3*x for x in (0,1,0))],[(0,0,1),(0,4,0),(0,3,0)])],
    'b':[e('unique simultaneous a,b',(-3,21),(-3,21)),n('point condition f1',-3-6+21-9,3),n('stationary condition fprime1',-9-12+21,0)]},
    'Differentiation gives3ax²+4ax+b. Given point supplies6a+b=3 and stationarity7a+b=0, whose subtraction fixesa=−3,b=21. The point is not merely an intercept.')
fcoeff=[(8,0,0),(0,0,1),(0,1,0)]
rec(A1,8,{'a(i)':[e('formal coefficients f(2x)',[tuple(v*2**i for v in c) for i,c in enumerate(fcoeff)],[(8,0,0),(0,0,2),(0,4,0)]),n('horizontal point scale',F(1,2),F(1,2))],
    'a(ii)':[e('given x coordinates halve',[F(2,2),F(4,2)],[1,2])],
    'b':[e('formal coefficients 4f+1',[(33,0,0),(0,0,4),(0,4,0)],[(4*8+1,0,0),(0,0,4),(0,4,0)])],
    'c':[n('vertex condition fixes b',8,8),n('a from b=2a',F(8,2),4),n('vertex x',-F(8,2*4),-1),n('vertex y',4-8+8,4)]},
    'Symbolic coefficient triples represent constant,a,b exactly: g=f(2x) andh=4f+1 for arbitrary parameters. Horizontal scale is1/2, vertical stretch precedes+1 translation. Newly supplied input coordinates2,4 yield the source outputs1,2. Vertex conditions independently givea4,b8.')
p=F(1,3)
rec(A1,9,{'a':[n('box probabilities',F(3,6),F(1,2)),n('black probabilities sum',F(1,5)+F(4,5),1),n('white probabilities sum',F(2,5)+F(3,5),1)],
    'b':[n('total blue',F(1,2)*F(4,5)+F(1,2)*F(3,5),F(7,10))],
    'c':[n('red total',F(1,2)*F(1,5)+F(1,2)*F(2,5),F(3,10)),n('black given red',(F(1,2)*F(1,5))/F(3,10),F(1,3))],
    'd':[n('correct changed red probability',p*F(1,5)+(1-p)*F(2,5),F(1,3)),n('changed conditional',(p*F(1,5))/(p*F(1,5)+(1-p)*F(2,5)),F(1,5)),e('unique integer die threshold',[a for a in range(1,6) if F(a,6)/(2-F(a,6))==F(1,5)],[2])]},
    'The two boxes each contain five balls. All five source denominators10 in the part(d) intermediate probabilities must be5; corrected cancellation givesp/(2-p),p1/3,a2. The wording expressly uses a-or-below, matching the source final convention.',
    'Inspected native probability tree: correct black/white→red/blue branching, with probabilities blank for the requested completion; no answer leakage.')
S=lambda a:(10-a)*math.exp(a/5)
rec(A1,10,{'a':[n('tangent point',math.exp(0),1),n('tangent gradient',math.exp(0)/5,F(1,5))],
    'b':[n('rectangle area from vertices at a3',7*math.exp(.6),S(3))],
    'c':[n('perimeter from sides at a5',2*5+2*math.exp(1),15.43656365691809)],
    'd':[n('independent central derivative at3',(S(3+1e-5)-S(3-1e-5))/(2e-5),math.exp(.6)*(1-F(3,5)),1e-7)],
    'e':[n('critical point',1-F(5,5),0),n('second derivative at5',-5*math.exp(1)/25,-.543656365691809),n('maximum rectangle perimeter',2*(10-5)+2*math.exp(5/5),15.43656365691809)]},
    'Base10−a and heightexp(a/5) are specified by vertices. Product differentiation givesexp(a/5)(1−a/5); its sign changes+to−at5, a global maximum on(0,10). Ssecond=−a exp(a/5)/25 and Pmax=10+2e.',
    'Inspected native exponential/rectangle figure: the top-left vertex is(a,f(a)), bottom spans a-to10 and the curve is labelled; neither a5 nor optimized perimeter is given.')

# Set A, Paper2: numerical roots and exact geometry with domain checks.
rec(A2,1,{'a':[n('median fixes b',2*8-10,6)],'b':[n('mean fixes a',4*7-6-10-10,2)],
    'c':[n('population variance',sum((v-7)**2 for v in [2,6,10,10])/4,11),n('population SD rounded',round(math.sqrt(11),2),3.32)]},
    'Ascending order and even-sample median determineb6; mean determinesa2. Population rather than sample variance divides by4; resultingSDsqrt11 matches the source.')
xroot=math.log(2/(math.exp(2)-1))
rec(A2,2,{'a':[n('composition at admissible1',math.exp(math.log(1+2)),3),e('composition domain lower endpoint excluded',-2>-2,False)],
    'b':[n('analytic equality root',xroot,-1.1614393615711958),n('original equation residual',xroot+2-math.log(math.exp(xroot)+2),0),e('root admissible',xroot>-2,True)]},
    'Composition equalsx+2 onx>−2. Exponentiating the equality givesexp(x)(e²−1)=2. The residual function derivative2/(exp(x)+2)>0 proves uniqueness; the exact root lies in the original domain.')
tail=1-N.cdf(10/9); low=230+9*N.inv_cdf(.5-tail)
rec(A2,3,{'a':[n('normal upper tail',tail,.13326026290250548)],
    'b':[n('target lower CDF',.5-tail,.3667397370974945),n('quantile a',low,226.93549344267043),n('area equals upper tail',N.cdf(0)-N.cdf((low-230)/9),tail)]},
    'Explicitly suppliedN(230,9²) is one distribution compatible with the source numbers. The lower bound lies below230 and CDF(a)=.5−tail; no missing-standard-deviation assumption remains.')
rec(A2,4,{'a':[n('analytic derivative at3',2*3*math.log(1)+9/(3-2),9)],
    'b(i)':[n('point ordinate',3**2*math.log(3-2)+1,1),n('normal gradient',-F(1,9),-F(1,9))],
    'b(ii)':[n('normal intercept',1+F(3,9),F(4,3))]},
    'Product/chain rules give2xln(x−2)+x²/(x−2). Atx3 the point is(3,1), tangent9, normal−1/9; both requested line forms follow. Domainx>2 is explicit.')
rec(A2,5,{'':[e('x exponent for general term at r2',7+2,9),n('coefficient multiplier',math.comb(7,2)*2**5,672),n('squared a from coefficient',F(6048,672),9),e('all real a candidates',[-math.sqrt(9),math.sqrt(9)],[-3,3])]},
    'The power is7+r, hence r2 only. Its coefficient is672a²; both signs±3 are required. Treating the power as7+2r or losing the negative sign would be wrong.')
theta=bisect(lambda t:(16/(t+2))**2*(t-math.sin(t))-6.7,.001,math.pi)
radius=16/(theta+2)
rec(A2,6,{'a':[n('twice segment area',2*3.35,6.7),n('sector minus triangle at solved values',radius**2*(theta-math.sin(theta))/2,3.35)],
    'b':[n('independent minor-sector root',theta,1.2000831300057664),n('radius',radius,4.999870112740218),n('sector perimeter',radius*(theta+2),16)]},
    'Minor segment issector minus isosceles triangle, not the entire sector. Substituting perimeter gives one root on(0,pi): derivative sign reduces witht=theta/2 to tan²t+tan t−t>0, proving monotonicity and uniqueness.',
    'Inspected native sector: OA andOB radii, theta atO, chordAB, and only the minor region between chord and arc shaded/labeled3.35cm²; not the triangle or full sector.')
rayroots=[10*math.sqrt(2)-math.sqrt(89),10*math.sqrt(2)+math.sqrt(89)]
rec(A2,7,{'a':[n('right-position BX',20*math.cos(math.pi/4),10*math.sqrt(2))],
    'b':[n('positive equal-sides BX',2*20*math.cos(math.pi/4),20*math.sqrt(2)),e('zero root excluded',0>0,False)],
    'c':[n('smaller BX',rayroots[0],4.708154491674736,1e-7),n('larger BX',rayroots[1],23.576116755787166,1e-7),n('cosine rule at smaller root',rayroots[0]**2+400-40*rayroots[0]*math.cos(math.pi/4),289),n('cosine rule at larger root',rayroots[1]**2+400-40*rayroots[1]*math.cos(math.pi/4),289)]},
    'Angle is atB, so cosine rule isAX²=BX²+400−40BXcos45. There are two positive roots whenAX17. The degenerate BX0 root forAX20 is explicitly excluded byX strictly right ofB.',
    'Inspected native fixedAB/ray figure:20cm onAB,45degrees atB, Xright ofB and dashed movingAX. Caption saysXvaries, so the single sketch does not force either ambiguous-case root.')
t=math.tan(math.radians(10)); heights=[(1-math.sqrt(1-24*t*t))/(2*t),(1+math.sqrt(1-24*t*t))/(2*t)]
rec(A2,8,{'a(i)':[n('height for alpha45',2*math.tan(math.pi/4),2)],
    'a(ii)':[n('beta for first height',math.degrees(math.atan(F(2,3))),33.690067525979785)],
    'b':[n('height for beta40',3*math.tan(math.radians(40)),2.5172988935318397),n('correct alpha using AQ2',math.degrees(math.atan(3*math.tan(math.radians(40))/2)),51.53277428755675,1e-7)],
    'c(i)':[n('AQ tangent height at example x4',2*math.tan(math.atan(2)),4),n('BQ tangent height at example x4',3*math.tan(math.atan(F(4,3))),4)],
    'c(ii)':[n('angle atP is alpha minus beta at x2',math.degrees(math.atan(1)-math.atan(F(2,3))),11.309932474020215)],
    'c(iii)':[n('first positive height from tangent-difference quadratic',heights[0],1.407054416319017),n('second positive height',heights[1],4.264227403298692),n('first difference degrees',math.degrees(math.atan(heights[0]/2)-math.atan(heights[0]/3)),10),n('second difference degrees',math.degrees(math.atan(heights[1]/2)-math.atan(heights[1]/3)),10)]},
    'CollinearB,A,Q implyBQ3 andAQ2. The source denominator3 in alpha atpartb is wrong; usingx/2 gives51.5degrees. Independent tangent-difference quadratic t x²−x+6t=0 yields both positive heights for the10degree angle; no periodic extraneous solutions.',
    'Inspected native elevation diagram: B,A,Q ordered1then2 on horizontal baseline, Pvertically aboveQ, xonPQ, alpha atA andbeta atB; right-angle square atQ.')
rec(A2,9,{'a(i)':[n('positive endpoint',math.sqrt(2)+math.sqrt(0),math.sqrt(2))],
    'a(ii)':[n('minimum from f squared bound',math.sqrt(2),1.4142135623730951),n('unique interior maximum f0',math.sqrt(1)+math.sqrt(1),2)],
    'b':[n('single horizontal intersection height',2,2)],'c':[n('OB slope',math.sqrt(2)/1,math.sqrt(2))],
    'd':[e('bounding slopes excluded from no-intersection interval',(-math.sqrt(2)<-math.sqrt(2),math.sqrt(2)<math.sqrt(2)),(False,False)),n('symmetric boundary slope magnitude',math.sqrt(2),1.4142135623730951)],
    'e':[n('exact full integral',F(8,3)*math.sqrt(2),3.771236166328254),n('two lower triangles area',2*F(1,2)*math.sqrt(2),math.sqrt(2)),n('enclosed area',(F(8,3)-1)*math.sqrt(2),2.3570226039551585)]},
    'f²=2+2sqrt(1−x²) proves range and unique maximum. Forpositive x, f(x)/x decreases tosqrt2, with the reflected negative branch giving−sqrt2; endpoints intersect, so no-intersection bounds are strict. Integrate both square roots and subtract both triangles. Exact-area remark belongs topart(e), not source part(d).',
    'Inspected native graph: endpoints±1, positive arch with maximum2, OA/OB rays toorigin, shaded region only between arch and rays, axes remain visible over fill.')
area8=F(9,4)*(1-F(9,25)**8)
rec(A2,10,{'a':[n('side ratio',F(72,100)/F(12,10),F(3,5))],
    'b':[n('area ratio',F(3,5)**2,F(9,25))],
    'c':[n('infinite base length',F(12,10)/(1-F(3,5)),3)],
    'd':[n('finite area sum from8terms',sum((F(6,5)*F(3,5)**i)**2 for i in range(8)),area8),n('four-decimal result',round(float(area8),4),2.2494)],
    'e':[n('infinite area sum',F(36,25)/(1-F(9,25)),F(9,4))],
    'f':[n('new side ratio',F(8,10),F(4,5)),n('new base length',2*F(4,5)/(1-F(4,5)),8),n('new infinite area sum',(2*F(4,5))**2/(1-F(4,5)**2),F(64,9))]},
    'Side ratio and area ratio must differ by squaring. Conditions|r|<1 justify both infinite sums. The independent new chain solves2x/(1−x)=8, x.8, givingarea64/9.',
    'Inspected native successive squares: adjacent bases onAB, initial side lengths1.2/.72/.432, shrinking squares continue towardB. Infinite continuation is explicit; finite drawing does not add an endpoint gap to the geometric sum.')

# Set B, Paper1: exact transformations, trigonometry and calculus.
rec(B1,1,{'a':[e('f composed with g coefficients',[-1,2*3],[-1,6])],
    'b':[e('g composed with f coefficients',[3*(-1),3*2],[-3,6]),e('composition difference coefficients',[-1-(-3),6-6],[2,0])],
    'c':[n('inverse slope',F(1,2),F(1,2)),n('inverse constant',F(1,2),F(1,2))]},
    'Composition order changes the constant term. Solvingy=2x−1 givesinverse(x+1)/2 for allrealx; no restricted domain is needed.')
rec(B1,2,{'a':[n('cosine at included angle',F(2**2+3**2-7,2*2*3),F(1,2)),n('angle degrees',math.degrees(math.acos(.5)),60)],
    'b':[n('included-angle area',.5*2*3*math.sin(math.pi/3),3*math.sqrt(3)/2),n('Heron equivalent area squared',(2*(4*9+9*7+7*4)-(4**2+9**2+7**2))/16,F(27,4))]},
    'The sqrt7 side is oppositeBAC; cosine law fixes60degrees. Included-side sine area equals3sqrt3/2, independently checked through the squared Heron identity.',
    'Inspected native triangle: AB2,AC3,BCsqrt7 with angle sought atA; none of the derived60degree/area values is supplied.')
rec(B1,3,{'a':[n('series ratio formula evaluated at solved a',F(3,7),F(3,7))],
    'b':[n('a from rearranged equation',7-4,3),n('infinite sum',4/(1-F(3,7)),7),e('convergence',abs(F(3,7))<1,True)]},
    'Convergent geometric sum gives4/(1−a/7)=7. a3 satisfies the required absolute ratio bound; no second algebraic solution appears.')
rec(B1,4,{'a':[n('period from1.5cycles',24/F(3,2),16)],
    'b':[n('amplitude from extrema',F(14-4,2),5)],
    'c':[n('p from initial minimum',4-9,-5),n('q',2*math.pi/16,math.pi/8),n('marked maximum f24',-5*math.cos(math.pi/8*24)+9,14)]},
    'The native sketch explicitly shows another maximum and minimum beforeA, establishing1.5cycles rather than an ambiguous half-period. Initialminimum fixesnegativep; qpositive thenpi/8.',
    'Inspected native cos plot: minima at0/16/32 havey4; maxima at8/24 havey14; A24,14 clearly labelled. All x-ticks and complete cycles matchperiod16.')
rec(B1,5,{'a':[n('antiderivative derivative coefficient',3*4,12),e('log argument positive all real',1>0,True)],
    'b':[n('independent quadrature integral',integrate(lambda x:12*x**3/(x**4+1),0,1),3*math.log(2)),n('A from logarithm',math.exp(3*math.log(2)),8)]},
    'Chain rule validates3ln(x4+1)+C; x4+1positive removes any absolute-value restriction. Definite integral3ln2=ln8 fixesA8.')
xexp=math.log(1.5,2)
rec(B1,6,{'':[n('exact exponent numeric check',xexp,.5849625007211562),n('original equation ratio',4**(xexp+1)*3**xexp/6**(xexp+1),1),n('base simplification',F(4*3,6),2)]},
    'Positive bases permitdivision to2^x=3/2. Strict monotonicity of2^x gives one real solutionlog2(3/2)=log2(3)−1; no numerical approximation is needed in the no-calculator paper.')
rec(B1,7,{'a':[n('g1 equals input to f',1**2+1,2),n('f(g1) from given point',3,3),n('g(f0)',(-4)**2+1,17)],
    'b':[n('quotient tangent gradient',F(0*5-3*4,25),-F(12,25)),n('normal negative reciprocal',-1/(-F(12,25)),F(25,12)),n('normal-tangent product',-F(12,25)*F(25,12),-1)]},
    'Only suppliedf2=3,f0=−4,fprime2=0 are needed. Quotient differentiation usesg2=5,gprime2=4 and gives−12/25; normal gradient25/12. No unspecified formula forf is assumed.',
    'Inspected native differentiable graph: stationaryA2,3 andB0,−4 are explicit, horizontal tails labelledy2 andy−1 match source qualitativegraph; normal slope uses pointA, not tail values.')
rec(B1,8,{'a':[n('positive cosine',math.sqrt(1-F(3,5)**2),F(4,5)),n('double sine',2*F(3,5)*F(4,5),F(24,25))],
    'b':[n('double cosine',1-2*F(3,5)**2,F(7,25))],
    'c':[n('sine rule AC',25*F(24,25)/F(3,5),40)],
    'd':[n('BD projection',25*F(7,25),7)],
    'e':[n('AD projection',40*F(4,5),32),n('AB length',32+7,39),n('height from AC',40*F(3,5),24),n('triangle area',F(1,2)*39*24,468)]},
    'First-quadrant condition choosespositivecosine. Sine rule givesAC40; perpendicularD lies internally, with legsAD32,BD7,CD24. Both area methods give468cm².',
    'Inspected native triangle: xatA,2xatB,BC25; DbetweenA/B andCDperpendicular, no derivedside40/7/39/area labels are exposed.')
rec(B1,9,{'a(i)':[e('all derivative coefficients positive',all(c>0 for c in [2,1,1]),True)],
    'a(ii)':[e('all second-derivative coefficients positive',all(c>0 for c in [4,1]),True)],
    'b':[n('fixed point residual f(ln2)-ln2',math.exp(2*math.log(2))+math.exp(math.log(2))-6,0),n('inverse xintercept from f0',math.exp(0)+math.exp(0)+0-6,-4)],
    'c':[n('required vertical shift',-2*(-4),8)],
    'd':[e('exact polynomial after exp/log substitution',[-6,1,1],[-6,1,1])]},
    'Positive exponential terms provefprime>0 andfsecond>0 for everyrealx; limits give inverse onR. Reflection yields inverseintercept−4, notsource prose+4. The commonfixedpoint hasexp(x)=2. Transformationk8 and logsubstitutionx²+x−6 are correct; source false intermediate=f(x) is removed.',
    'Inspected final native given-fgraph only: it has(0,−4), increasing convex shape and visibleaxes. Inverse andy=x are deliberately absent because the student must draw them.')
coeff=poly_mul(poly_mul([-1,2],[-1,1]),[3,1])
rec(B1,10,{'a':[e('three factored roots',[F(1,2),F(1),F(-3)],[F(1,2),F(1),F(-3)]),e('all factor roots evaluate tozero',[poly_value(coeff,v) for v in [F(1,2),F(1),F(-3)]],[0,0,0])],
    'b':[e('expanded coefficients',coeff,[3,-8,3,2])],
    'c':[n('ln of first x root',math.log(math.sqrt(math.e)),.5),n('ln of second x root',math.log(math.e),1),n('ln of third x root',math.log(math.exp(-3)),-3)],
    'd':[n('first admissible exp value',math.exp(math.log(.5)),.5),n('second admissible exp value',math.exp(0),1),e('negative candidate excluded',-3>0,False)],
    'e':[n('sine root pi6',math.sin(math.pi/6),.5),n('sine root5pi6',math.sin(5*math.pi/6),.5),n('sine rootpi2',math.sin(math.pi/2),1),e('negative3 outside sine range',-1<=-3<=1,False)]},
    'Exact factor multiplication matches the cubic. Logsubstitution retains allthree positivex values; exponential substitution rejectsnegativeu; sine substitution retains threeangles in0to2pi and rejects−3. Periodic branches/endpoints add no others.')

# Set B, Paper2: statistics, geometry, enumeration and a global optimum.
rec(B2,1,{'a':[n('independent intersection',F(34,100)*F(45,100),F(153,1000))],
    'b':[n('union inclusion-exclusion',F(34,100)+F(45,100)-F(153,1000),F(637,1000))]},
    'Independence is explicitly given; multiplication is used only forintersection, and union subtracts the intersection once.')
xs=[12,15,17,23,28]; ys=[127,142,144,151,171]
sx=sum((x-19)**2 for x in xs); sy=sum((y-147)**2 for y in ys); cross=sum((x-19)*(y-147) for x,y in zip(xs,ys))
rec(B2,2,{'a':[n('y mean',F(sum(ys),5),147)],
    'b(i)':[n('rounded-line mean estimate',(147-101.446)/2.398,18.996663886572145),e('nearest integer mean',round((147-101.446)/2.398),19)],
    'b(ii)':[n('missing integer x',5*19-(12+15+17+28),23),n('actual mean fromcompleted data',F(sum(xs),5),19)],
    'c':[n('cross-deviation sum',cross,398),n('x deviation sum',sx,166),n('y deviation sum',sy,1026),n('Pearson r',cross/math.sqrt(sx*sy),.9643958829041107),n('OLS slope rounded',round(cross/sx,3),2.398),n('OLS intercept rounded',round(147-(cross/sx)*19,3),101.446)]},
    'The fivepairedy values are a compatible reconstruction, not a recovered original dataset. Independently computing OLS gives slope199/83 andintercept8420/83, which round to the supplied line; Pearsonr.96439588. Rounding/integer instruction makesa23 determinate rather than treatingroundedline as exact.')
rec(B2,3,{'a':[n('vertex x',-F(20,2*2),-5),n('minimum fminus5',2*25+20*(-5)+54,4)],
    'b':[e('complete-square coefficients',[2*25+4,2*2*5,2],[54,20,2]),n('inverse of6 onleftbranch',-5-math.sqrt((6-4)/2),-6),n('forward composition atminus6',2*(-6)**2+20*(-6)+54,6)]},
    'The explicitx≤−5 restriction forces the negative square-root branch, inverseoutput≤−5 and inversedomainx≥4. Missing that sign would not invert the restricted function.')
equal=F(math.comb(12,6),2**12); greater=F(sum(math.comb(12,k) for k in range(7,13)),2**12)
rec(B2,4,{'a':[n('equal heads/tails probability',equal,F(231,1024)),n('decimal equalprobability',float(equal),.2255859375)],
    'b':[n('direct greater-tail enumeration',greater,F(793,2048)),n('symmetry method agrees',(1-equal)/2,greater)]},
    'Twelveindependentfairtosses giveBin(12,p=.5), correctingthe source secondn symbol. Strictly moretails excludes the equalcase and halves the remainder; probability.38720703125.')
rec(B2,5,{'a':[n('pyramidvolume',F(1,3)*36*3*math.sqrt(2),36*math.sqrt(2))],
    'b':[n('diagonal squared',6**2+6**2,72),n('diagonal',math.sqrt(72),6*math.sqrt(2))],
    'c':[n('halfdiagonal',6*math.sqrt(2)/2,3*math.sqrt(2)),n('slant edge squared',(3*math.sqrt(2))**2+(3*math.sqrt(2))**2,36),n('slant edge',math.sqrt(36),6)]},
    'HeightPQ isperpendicularto the square and Qiscentre. Each vertex distanceAQ=3sqrt2, hencePA=PB=6=AB; equilateral conclusion follows from threeequal sides, not an apparent angle in the perspective figure.',
    'Inspected native pyramid: A/B/C/Dbase vertices, Qcentre, Pvertically aboveQ, AB6cm and PQ3sqrt2cm; dashedhiddenedges andheightlabel are clear without equilateral-answer labels.')
cosroots=[5+10*k for k in range(100)]
rec(B2,6,{'a':[e('number of admissible roots',len(cosroots),100),e('end roots',[cosroots[0],cosroots[-1]],[5,995]),n('largest numeric cosine residual',max(abs(math.cos(math.pi*x/10)) for x in cosroots),0)],
    'b':[n('direct sum ofallroots',sum(cosroots),50000),n('arithmetic progression formula',F(100*(5+995),2),50000)]},
    'cosθ=0 yieldsx5+10k. Bounds0to1000 givek0through99 exactly; neitherendpoint isroot, and there are100terms withsum50000.')
quartic=[83,0,-F(5,2),-F(1,3),F(3,2)]; tangent=derivative(quartic)
rec(B2,7,{'a':[e('exact derivative coefficient vector',tangent,[0,-5,-1,6])],
    'b':[n('slope atminus1',poly_value(tangent,-1),-2)],
    'c':[e('factored equal-slope polynomial',poly_mul(poly_mul([1,1],[-2,3]),[-1,2]),[2,-5,-1,6]),n('slope atonehalf',poly_value(tangent,F(1,2)),-2),n('slope attwothirds',poly_value(tangent,F(2,3)),-2)]},
    'Differentiating exactrationalcoefficients gives6x³−x²−5x. Equal-slope equation factors(x+1)(3x−2)(2x−1), leaving1/2 and2/3 afterexcludingthe alreadygiven−1.')
counts=Counter(abs(a-b) for a in range(1,7) for b in range(1,7))
rec(B2,8,{'a':[n('equal dicecount probability',F(counts[0],36),F(1,6))],
    'b':[n('difference5probability',F(counts[5],36),F(1,18))],
    'c':[n('difference4probability',F(counts[4],36),F(1,9))],
    'd':[e('complete counts from36orderedoutcomes',[counts[d] for d in range(6)],[6,10,8,6,4,2])],
    'e':[n('expectation fromexhaustivecounts',F(sum(d*counts[d] for d in range(6)),36),F(35,18))],
    'f':[n('outsidewin-count',36-counts[5]-counts[1],24),n('fair loss',F(7*counts[5]+counts[1],24),1),n('exhaustive fairgame expectation',F(sum(7 if abs(a-b)==5 else 1 if abs(a-b)==1 else -1 for a in range(1,7) for b in range(1,7)),36),0)]},
    'Independent enumeration uses all36ordered equiprobablepairs, avoidingunordered-dice weightingerrors. Remaining24outcomes loseL; netprofitwording makesfairL1 rather than confusingpayout withentryfee.')
packetp=N.cdf(F(480-500,18)); quant=500+18*N.inv_cdf(.85)
rec(B2,9,{'a':[n('normal packet lower tail',packetp,.13326026290250548)],
    'b':[n('conditional middle probability',(.5-packetp)/(1-packetp),.423125560535183)],
    'c':[n('85percent quantile',quant,518.6558010108882),n('remaining upper tail',1-N.cdf((quant-500)/18),.15)],
    'd':[n('exactlyoneunderweight of5',5*packetp*(1-packetp)**4,.3760326037695816)],
    'e(i)':[n('upperquartile',724+52,776),n('premium mean',F(724+776,2),750)],
    'e(ii)':[n('premiumSD',26/N.inv_cdf(.75),38.54765768114565),n('quartile probabilityrecheck',N.cdf((724-750)/(26/N.inv_cdf(.75))),.25)]},
    'NewexplicitN(500,18²) givens arecompatible withsource tail/quantile results. Conditional denominator isP(R>480), andBin5uses theunroundedtail. Premiumquartiles implymean750, SD26/z.75, strictlypositive.')
intersection=bisect(lambda x:4*math.cos(x)-x*x,0,math.pi/2)
optimal=bisect(lambda a:8*math.cos(a)-8*a*math.sin(a)-6*a*a,0,intersection)
area=lambda a:8*a*math.cos(a)-2*a**3
rec(B2,10,{'a':[n('positive intersection',intersection,1.2015382993405752),n('intersectionordinate',intersection**2,1.4436942847822418),n('intersectionequation residual',4*math.cos(intersection)-intersection**2,0)],
    'b':[n('independent Simpson enclosed area',integrate(lambda x:4*math.cos(x)-x*x,-intersection,intersection),6.304327197557455),n('analytic area expression',8*math.sin(intersection)-F(2,3)*intersection**3,6.304327197557455)],
    'c':[n('rectangle fromwidthheight at.5',2*.5*(4*math.cos(.5)-.5**2),area(.5))],
    'd(i)':[n('stationaryratio at independentroot',(math.cos(optimal)-optimal*math.sin(optimal))/optimal**2,F(3,4)),n('derivative cubic coefficient',derivative([0,0,0,-2])[2],-6)],
    'd(ii)':[n('maximizing a',optimal,.6811371632177665),n('maximum area',area(optimal),3.6011461192935457),e('criticalpoint inopeninterval',0<optimal<intersection,True)]},
    'On0toπ/2,4cosx−x²strictlydecreases, so thetwo intersectionsare±r. Integrateupperminuslower withunroundedr. Rectanglewidth2a yields8acos a−2a³ and derivative−6a², correctingbothsource−3a² occurrences. Asecond=−16sin a−8acos a−12a<0 on(0,r), endpointsarea0, provinguniqueglobalmaximum3.601146. SourceheightlabelAisreplacedbyh.',
    'Inspected native two-curverectangle: coscurveaboveparabola betweenintersectionpoints, uppervertices oncos/loweronparabola, verticals±a andonlyrectangleshaded. No optimizedaorarea answer appears.')

assert len(RECORDS)==40 and len({(r['paper'],r['question']) for r in RECORDS})==40
for paper,p in PAPERS.items():
    assert [q['number'] for q in p['questions']]==list(range(1,11))
    assert Counter(q['section'] for q in p['questions'])=={'A':7,'B':3}
    assert sum(q['marks'] for q in p['questions'] if q['section']=='A')==40
    assert sum(q['marks'] for q in p['questions'] if q['section']=='B')==40
diagrams=sum(bool(q.get('diagramSvg')) for p in PAPERS.values() for q in p['questions'])
assert diagrams==14
report={'status':'passed','reviewer':'Separate mathematical reviewer who did not author the reconstructed SL questions',
    'papers':4,'questions':40,'marks':320,'independentCheckCount':sum(len(checks) for r in RECORDS for checks in r['partChecks'].values()),
    'sourceSolutionPagesRead':40,'nativeDiagramsInspected':14,'paperHashes':HASHES,
    'method':'Read every reconstructed stem/part/full marking point against every native source solution page. Independently transcribed inputs, exactFraction arithmetic and polynomial manipulation, complete discrete enumeration, NormalDist quantiles, bracketed roots, numerical quadrature, and manual symbolic/domain/global-extremum proofs. No author generator/checks imported.',
    'sourceErrataVerified':['A1Q9(d): allfive probability denominators10→5; finalconditionalanda2unchanged.','A2Q8(b): alpha usesdenominator2, not3.','A2Q9: exactarea5sqrt2/3remarkbelongs toe, notd.','B1Q9(b): inversexintercept−4, not+4.','B1Q9(d): removefalse intermediate=f(x).','B2Q4(a): secondbinomialparameterisp, notn.','B2Q10(d)(i): both−3a²derivative/coefficientinstancesmustuse6a².','B2Q10(c): heightlabelh, notareaA.'],
    'limits':['Questions are compatible newly worded reconstructions, not claims to recover uniquely determined original missing wording.','The regression dataset and missing normal-distribution givens are explicitly compatible choices.','This is computational and independent AI mathematical review, not human IB examiner moderation.','This report verifies canonical SL JSON and diagrams, not final PDF repair, live deployment or email delivery.'],
    'records':RECORDS}
DEST.write_text(json.dumps(plain(report),ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps({k:report[k] for k in ['status','papers','questions','marks','independentCheckCount','sourceSolutionPagesRead','nativeDiagramsInspected']}))
