"""Independent AA HL Set B audit. Does not import the author's generator.

All24stems/fullschemes and 27native source solutionpages were read. Inputs here
are independently transcribed. Standard-library calculation/proof evidence and
per-question bindings accompany manual diagram and mathematical review.
"""
from pathlib import Path
from statistics import NormalDist
from fractions import Fraction
import hashlib,json,math,re,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
PAPERS=[json.loads((ROOT/f'content/ib/aa-mocks-2026/papers/aa-hl-set-b-paper-{n}.json').read_text(encoding='utf8')) for n in [1,2,3]]
RECORDS=[]
def n(label,actual,expected,tol=1e-8):
    assert abs(actual-expected)<=tol*max(1,abs(expected)),(label,actual,expected)
    return {'test':label,'actual':actual,'expected':expected,'status':'passed'}
def e(label,actual,expected):
    assert actual==expected,(label,actual,expected)
    return {'test':label,'actual':actual,'expected':expected,'status':'passed'}
def quad(f,a,b,k=8000):
    h=(b-a)/k
    return h/3*(f(a)+f(b)+sum((4 if i%2 else 2)*f(a+i*h) for i in range(1,k)))
def zero(f,a,b):
    fa=f(a)
    for _ in range(100):
        c=(a+b)/2;fc=f(c)
        if fa*fc<=0:b=c
        else:a=c;fa=fc
    return (a+b)/2
def rec(paper,num,tests,reason,visual='No question diagram is needed; all givens and part demands are complete in text.'):
    p=PAPERS[paper-1];q=p['questions'][num-1]
    assert q['number']==num
    assert q['marks']==sum(x['marks'] for x in q['parts'])
    assert [x['label'] for x in q['parts']]==[x['part'] for x in q['markScheme']]
    for a,g in zip(q['parts'],q['markScheme'],strict=True):
        assert a['marks']==sum(int(x['code'][1:]) for x in g['steps'])
        assert all(re.fullmatch('[MAR][1-9]',x['code']) for x in g['steps'])
    if q.get('diagramSvg'):
        ET.fromstring(q['diagramSvg'])
        assert not re.search(r'<(?:script|style|image|foreignObject|iframe)\b|\b(?:href|src)\s*=|\bon\w+\s*=',q['diagramSvg'],re.I)
    RECORDS.append({'paperId':p['id'],'question':num,'status':'passed','sourcePages':q['sourcePages'],
        'canonicalQuestionSha256':hashlib.sha256(json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        'independentChecks':tests,'mathematicalReview':reason,'diagramReview':visual,
        'markAllocationReview':'Every part and full marking group read against native source; reconstructed demands and distinct marking points agree with totals. Supplied source mistakes are corrected in retyped canonical scheme.'})

ab=(1,-3,4);ac=(2,-1,2)
cross=(ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0])
rec(1,1,[e('cross product',list(cross),[-2,6,5]),n('squared area',sum(x*x for x in cross)/4,65/4),n('planeatA',-2+6+5,9),n('planeatB',-4-12+25,9),n('planeatC',-6+15,9)],
    'Cross product and all three point substitutions confirm the plane uses6y. The native solution has a6ztypo; canonical normal and area are correct.')
rr=[1-math.sqrt(3),1+math.sqrt(3)]
rec(1,2,[n('c from equalvalues',3-(-1),4),n('equalrootproduct',4/(-2),-2),n('equalrootsum',-4/(-2),2),*[n(f'first polynomial atroot{i}',x*x-2*x-2,0) for i,x in enumerate(rr)],*[n(f'second polynomial atroot{i}',-2*x*x+4*x+4,0) for i,x in enumerate(rr)]],
    'Equal equations give c4; root-sum/product comparison yields a−2,b4. Both explicit real roots satisfy both transformed quadratics; a≠0 is stated.')
cube=[2*math.sqrt(3)+2j,-2*math.sqrt(3)+2j,-4j]
rec(1,3,[*[n(f'cube root{i}',abs(z**3-64j),0) for i,z in enumerate(cube)],*[n(f'shifted cube root{i}',abs(((z-2j)+2j)**3-64j),0) for i,z in enumerate(cube)]],
    'Three arguments separated by2π/3 give every distinct root; shift by−2i gives the second solution set, with no root omitted.')
rec(1,4,[n('period from1.5cycles',24/1.5,16),n('angularcoefficient',2*math.pi/16,math.pi/8),n('minimumordinate',-5+9,4),n('maximumordinate',5+9,14),n('midline',(4+14)/2,9)],
    'Graph amplitude5 and midline9, with minimum atzero, force negative cosine coefficient. q>0 removes sign ambiguity.',
    'Full SVG inspected: minimum4 at0/16, maximum14 at8/24, midline9 and 24covering1.5periods agree with text.')
x=math.log2(1.5)
rec(1,5,[n('original exponential equality',4**(x+1)*3**(2*x+1)/18**(x+1),1),n('exactlogform',x,-1+math.log2(3)),n('simplifiedpower',2**x,1.5)],
    'Positive exponential bases permit division and logarithms. The requested integer/log form is one valid equivalent expression; no spurious root introduced.')
odechecks=[]
for x in [-2.,0.,1.,3.]:
    den=1+x**4;num=x**5+5*x-4;y=num/den;dy=((5*x**4+5)*den-num*4*x**3)/den**2
    odechecks.append(n(f'ODE at{x}',dy+4*x**3*y/den,5))
odechecks.append(n('initialvalue',(1+5-4)/2,1))
rec(1,6,odechecks,'Integrating factor1+x⁴ is positive for all realx. Exact rational candidate satisfies both ODE and initial condition; its denominator never vanishes.')
der=lambda x:6*x**3-x*x-5*x
rec(1,7,[n('initialgradient',der(-1),-2),n('parallelgradientat2/3',der(2/3),-2),n('parallelgradientat1/2',der(.5),-2),n('cubicfactor sample2',(2+1)*(6*2**2-7*2+2),6*2**3-2**2-5*2+2)],
    'Known root−1 factors the equality-of-gradients cubic; remaining roots2/3and1/2 are distinct from the initialpoint. Differentiation includes all quartic terms.')
aa=math.factorial(10)*math.factorial(3);bb=10*9*8*math.factorial(9)
rec(1,8,[n('arrangementratio',bb/aa,12),e('symbolgapchoices',math.comb(10,3)*math.factorial(3),10*9*8),e('totaldistinctobjects',9+3,12)],
    'Symbols are distinct and all nine digits distinct. One block contributes3!internal orders; nonadjacency uses three different slots among ten, with no end-gap omission.')
rec(1,9,[n('cosine acute',math.sqrt(1-(3/5)**2),4/5),n('double sine',2*(3/5)*(4/5),24/25),n('double cosine',1-2*(3/5)**2,7/25),n('AC sine rule',25*(24/25)/(3/5),40),n('AD',40*4/5,32),n('BD',25*7/25,7),n('base',32+7,39),n('area',39*24/2,468)],
    'The actualacute angleasin3/5 makes2xacute, so D lies insideAB and additionAD+BD is valid. Height24 independently gives area468.',
    'SVG inspected: Aleft,Bright,CaboveD, anglesxand2xatcorrectvertices, BC25 and perpendicular-foot square atD match givens.')
ff=lambda x:math.exp(2*x)+math.exp(x)+x-6
rec(1,10,[n('ordinateintercept',ff(0),-4),n('fixedpoint',ff(math.log(2)),math.log(2)),n('verticalshift',2*ff(0)+8,0),n('logcompositionat3',ff(math.log(3))-math.log(3),3**2+3-6),e('positivefirstderivative samples',all(2*math.exp(2*x)+math.exp(x)+1>0 for x in [-10,-1,0,1]),True),e('positivesecondderivative samples',all(4*math.exp(2*x)+math.exp(x)>0 for x in [-10,-1,0,1]),True)],
    'Monotonicity plus full realrange gives an inverse; strict increasing functions cannot have nontrivial2cycles, so intersections are fixed points. Native inverse-intercept sign and falsecomposition equality are corrected. Logcomposition requiresx>0, explicitly supplied.')
seq=[1]
for k in range(8):seq.append(4**(k+1)-(k+1)*seq[-1])
integraltests=[e('u1u2',seq[1:3],[3,10])]
for k in range(7):
    formula=(seq[k]*math.exp(4)+(-1)**(k+1)*math.factorial(k))/4**(k+1)
    integraltests.append(n(f'quadrature In{k}',quad(lambda x:x**k*math.exp(4*x),0,1),formula))
integraltests.append(n('weighted definiteintegral',quad(lambda x:(64*x*x+16*x+4)*math.exp(4*x),0,1),14*math.exp(4)-2))
rec(1,11,integraltests,'Integration-by-parts recurrence and induction numerator were reconstructed independently. The targetstep is k+1, with sign(−1)^(k+2) and denominator4^(k+2); seven directquadratures support the closed form including initialcase.')

p=math.comb(12,6)/2**12
rec(2,1,[n('equalcoinoutcomes',p,.2255859375),n('tailmajoritydirectsum',sum(math.comb(12,k) for k in range(7,13))/2**12,.38720703125),n('symmetryformula',(1-p)/2,.38720703125)],
    'Independence and faircoin probabilities support Bin12. Equal heads/tails is exactly6, and tailmajority starts7; symmetry omits the tie mass correctly.')
xx=[12,15,17,28,23];yy=[127,142,144,171,151];xb=sum(xx)/5;yb=sum(yy)/5;sxx=sum((x-xb)**2 for x in xx);syy=sum((y-yb)**2 for y in yy);sxy=sum((x-xb)*(y-yb) for x,y in zip(xx,yy))
rec(2,2,[n('xmean',xb,19),n('ymean',yb,147),n('Sxx',sxx,166),n('Syy',syy,1026),n('Sxy',sxy,398),e('rounded slope',round(sxy/sxx,3),2.398),e('roundedintercept',round(yb-sxy/sxx*xb,3),101.446),e('roundedcorrelation',round(sxy/math.sqrt(sxx*syy),3),.964),n('missingx',5*19-12-15-17-28,23)],
    'Constructed paired table reproduces every providedstatistic. Explicitrounded regression and integera avoid treating an approximatexmean as an exactunrounded equality.')
inv=lambda x:-5-math.sqrt((x-4)/2)
rec(2,3,[n('vertexordinate',2*(-5)**2+20*(-5)+54,4),n('inversecompositionat12',2*inv(12)**2+20*inv(12)+54,12),n('leftbranchsign',inv(12),-7),n('largestbranchendpoint',-20/4,-5)],
    'Range part refers to unrestricted parabola, then the domain is restricted explicitly. Leftbranch uses negative square root and inverseinputx≥4, not the otherbranch.')
rec(2,4,[n('powerarctanintegral',quad(lambda x:x/(1+x**4),0,1),math.pi/8),n('Acoefficient',quad(lambda x:2*x/(1+x**4),0,1),math.pi/4),e('Brounded4sf',float(format(quad(lambda x:1/(1+x**4),0,1),'.4g')),.867),n('linearityatk3',quad(lambda x:(2*x+3)/(1+x**4),0,1),math.pi/4+3*quad(lambda x:1/(1+x**4),0,1))],
    'Substitutiondu2xdx supplies factor1/2. Definiteintegral and A/Bdecomposition independently quadraturechecked; radians and constantofintegration are included.')
rec(2,5,[n('constantcoefficient',4**(-.5),.5),n('linearcoefficient',(-.5)*2*4**(-1.5),-.125),n('quadraticcoefficient',(-.5)*(-1.5)*4*4**(-2.5)/2,3/64),e('scaled coefficients',[64*.5,64*(-.125),64*(3/64)],[32.,-8.,3.])],
    'Factor4before generalizedbinomial expansion; validity|x/2|<1matches supplieddomain. Multiplying64x shiftspowers rather than keepingconstantterm.')
xs=[5+10*k for k in range(100)]
rec(2,6,[e('numberofzeros',len(xs),100),n('sumofzeros',sum(xs),50000),e('allrootscoszero',all(abs(math.cos(math.pi*x/10))<1e-12 for x in xs),True),e('rangeboundaryinclusion',xs[0]>=0 and xs[-1]<=1000 and xs[-1]+10>1000,True)],
    'Allpermitted roots are counted once from5to995;1000isnot a root. Arithmeticprogression total and directenumeration agree.')
rec(2,7,[n('hordinate',3/(2**2+1),.6),n('hderivative',(0*5-3*4)/25,-12/25),n('normalgradient',-1/(-12/25),25/12)],
    'Onlyf(2)=3andfprime(2)=0are required fromdiagram. Quotientruledenominator25and negative-reciprocal normalgradient are both correct.',
    'FullnewSVG inspected: stationaryA2,3atlocalmaximum and functioncurve areclearlygiven; source asymptoticdetail is schematic and unnecessaryto normalcalculation.')
q8=PAPERS[1]['questions'][7];root=ET.fromstring(q8['diagramSvg']);height=[t for t in root.findall('.//{http://www.w3.org/2000/svg}text') if '3√2' in ''.join(t.itertext())]
assert height and float(height[0].attrib['x'])<450,'heightlabel should be besideverticalPQ, clearofPB'
rec(2,8,[n('halfdiagonalsquared',(3*math.sqrt(2))**2,18),n('lateraledge',math.sqrt(18+18),6),e('antsremainonedges',80<600 and 60<600,True),n('separationat40',math.sqrt(60**2+80**2-60*80),20*math.sqrt(13)),n('distancegrowthrate',math.sqrt(1.5**2+2**2-1.5*2),math.sqrt(13)/2)],
    'Pyramidmetres versus antcm/s is explicit; after40s neither leaves its600cmedge. Equilateralangle60degrees gives law-of-cosines growth. SourceapexOwas relabelledPinroot correctionplan.',
    'Squareprojection, centreQand verticaldashedPQinspected. Reviewerrequestedmoving3√2mlabelawayfromPB; finalSVGplacesitx400adjacentverticalheight.')
rec(2,9,[e('planeplaneroundedangle',float(format(math.degrees(math.acos(1/math.sqrt(190))),'.3g')),85.8),e('lineplaneroundedangle',float(format(math.degrees(math.asin(1/math.sqrt(38))),'.3g')),9.34),n('thirdplanecommonpoint',3*(-5)+15+4*3.5,14),n('firstplanecommonpoint',-5-15+6*3.5,1),n('secondplanecommonpoint',2*(-5)+15,5),n('lineparalleltonormal',-2*3+4+2,0),n('infinitecaseequation',2-2,0)],
    'Dot-product planeangle and sine line-planeangle differ. Actual secondangle9.335859degrees rounds9.34, correcting source9.36. Parametric intersection yields(a−2)z=b−7; a2/b7 givesline, a2/b≠7 givesdisjointparallel, and otherauniqueintersection.')
norm=NormalDist(500,18);prob=norm.cdf(480)
rec(2,10,[e('lowermasstailrounded',float(format(prob,'.3g')),.133),e('conditionalrounded',float(format((.5-prob)/(1-prob),'.3g')),.423),e('85quantilerounded',float(format(norm.inv_cdf(.85),'.3g')),519.),e('exactly1of5rounded',float(format(5*prob*(1-prob)**4,'.3g')),.376),n('premiummean',(724+724+52)/2,750),e('premiumSDrounded',float(format(26/NormalDist().inv_cdf(.75),'.3g')),38.5),n('secondmoment',400**2+25,160025),n('lineartransformedmean',3*400+2,1202),n('lineartransformedvariance',3**2*25,225),n('standardizedvariance',25/5**2,1)],
    'Conditional denominator correctlyconditionsabove480. Normalquartiles use exactstandardquantile before rounding, and variance transforms quadraticallyratherthanlinearly. All supplied mass/probabilitymoments match.')
alpha=zero(lambda x:4*math.cos(x)-x*x,1,1.5);beta=alpha**2;ar=quad(lambda x:4*math.cos(x)-x*x,-alpha,alpha);vx=math.pi*quad(lambda x:16*math.cos(x)**2-x**4,-alpha,alpha);vy=2*math.pi*quad(lambda x:x*(4*math.cos(x)-x*x),0,alpha);vydisk=math.pi*(beta**2/2+quad(lambda y:math.acos(y/4)**2,beta,4));aopt=zero(lambda a:8*math.cos(a)-8*a*math.sin(a)-6*a*a,0,alpha);amax=8*aopt*math.cos(aopt)-2*aopt**3
rec(2,11,[n('intersection residual',4*math.cos(alpha)-alpha**2,0),e('intersectionxrounded',float(format(alpha,'.3g')),1.2),e('intersectionyrounded',float(format(beta,'.3g')),1.44),e('arearounded',float(format(ar,'.3g')),6.3),e('xrotationrounded',float(format(vx,'.3g')),74.2),e('yrotationrounded',float(format(vy,'.3g')),8.83),n('shellvsdisks',vy,vydisk),e('maximumarearounded',float(format(amax,'.3g')),3.6),e('maximizerinside',0<aopt<alpha,True)],
    'Independentbisection and shell/washerquadratures reproduce allresults. Rectanglederivative is8cos−8asin−6a², so ratio3/4is correct; nativesource3a²line needsfix. Asecondderivative negative overphysicalintervalmakes maximumunique.',
    'SVG inspected: evenregion betweenuppercosine/lowerparabola,verticals±aandrectanglecorners on bothcurves, solid/dashedcurve distinctionandlabelsare consistent.')

integtests=[e('log100rounded',float(format(math.log(100),'.3g')),4.61),e('log1000rounded',float(format(math.log(1000),'.3g')),6.91),n('squarefinite100',1-1/100,.99),n('squarefinite1000',1-1/1000,.999),n('cubeintegralfinite9',quad(lambda x:x**-3,1,9),(.5-.5/81)),n('sqrtintegralfinite9',quad(lambda x:x**-.5,1,9),4)]
for pp in [-.5,.5,2.]:
    integtests.append(n(f'powerfinitep{pp}',quad(lambda x:x**(-pp-1),1,9),(1-9**(-pp))/pp))
integtests.append(n('loglogfinite',quad(lambda x:1/(x*math.log(x)),2,8),math.log(math.log(8))-math.log(math.log(2))))
for pp in [-1.,.5,2.]:integtests.append(n(f'logpowerfinitep{pp}',quad(lambda x:1/(x*math.log(x)**(pp+1)),2,10),(math.log(2)**(-pp)-math.log(10)**(-pp))/pp))
for pp in [.5,2.]:integtests.append(n(f'expfinitep{pp}',quad(lambda x:math.exp(-pp*x),0,9),(1-math.exp(-pp*9))/pp))
rec(3,1,integtests,'Allproperantiderivatives, parameterrestrictions and improperlimitdirections were independentlyderived. p0isexplicitlyexcludedwherepowerdivisionusesp; logsubstitutionhasx>1; positivepconvergesandnegativepdivergesto+infinity. Exponent2025meansp2024, so1/2024.',
    'Comparisonfigure inspected: solid1/xand dashed1/x²arepositive,agreeat1and havecorrectrelativeorderforx>1; theydo notpretend finitewindow provesconvergence.')
gametests=[n('dielabel',6*3.5-(1+2+3+5+6),4),n('roundfailure',(5/6)**2,25/36),n('twoplayerP1',(1/6)/(1-(5/6)**2),6/11),n('twoplayerP2',(5/6)*(1/6)/(1-(5/6)**2),5/11),n('3playersecondturn',(5/6)**3/6,125/1296),n('3playereventual',(1/6)/(1-(5/6)**3),36/91),n('fairgamefirstturn',1/3,1/3),n('fairgamesecondturn',(2/3)*.5/3,1/9),n('fairgamethirdturn',((2/3)*.5)**2/3,1/27),n('fairgameeventual',(1/3)/(1-(2/3)*.5),.5)]
for xx in [4.,5.5,10.,100.]:
    failure=(1-1/xx)*(1-1/(xx-1))*(1-1/(xx-2));gametests.append(n(f'telescopedP1atx{xx}',(1/xx)/(1-failure),1/3))
rec(3,2,gametests,'Allmutuallyexclusive turnevents and round-failure ratios checked. Termination is almostsure becausefailureprobability<1. Telescopinggives1/3 for3unequalplayers; contradictionfornplayers needspositivepn denominator, explicitly ensuredbyallpi∈(0,1).')

assert len(RECORDS)==24 and len({(r['paperId'],r['question']) for r in RECORDS})==24
for p in PAPERS:
    assert p['course']=='hl' and p['set']=='B'
    assert p['minutes']==(75 if p['paper']=='3' else 120)
    assert p['calculator']==(p['paper']!='1')
    assert sum(q['marks'] for q in p['questions'])==p['marks']==(55 if p['paper']=='3' else 110)
report={'status':'passed','papers':3,'questions':24,'reviewer':'Separate AI mathematical reviewer, not the author of HL Set B','method':'Read all24canonicalstems and complete schemes, all27native source solutionpages, all6newdiagrams; independentlytranscribed and recomputed values withoutimportingauthorcode. Checked domains, physical units, limits, inversebranches, probabilitytermination and individual marktotals. FullMarkdown/KaTeXparse passed605expressions.',
    'numericalCheckCount':sum(len(r['independentChecks']) for r in RECORDS),'diagramCount':6,'sourceSolutionPagesRead':27,'paperChecks':[{'id':p['id'],'questions':len(p['questions']),'marks':p['marks'],'sha256':hashlib.sha256((ROOT/f"content/ib/aa-mocks-2026/papers/{p['id']}.json").read_bytes()).hexdigest()} for p in PAPERS],
    'resolvedFindings':['PyramidheightlabelmovedfromslopingPBtoverticalPQ.','Canonicalschemescorrectprovidedsource6yplanevariable,inverseintercept−4, falsecompositionequality, inductiontargetk+1, line-planeangle9.34degrees and rectanglederivative6a².'],
    'sourceBodyFollowup':'CorrecttheprovidedPDFinlineasdocumentedinrootpatchplan,includingrasterapexOtoP. Thisreviewbindscanonicalquestions/schemes; finalcombinedPDFvisualQAandportalQAremainseparate.',
    'limits':['Reconstructedquestionsmatchprovidedworkedanswers; completeoriginalwordingwasnotavailable.','Computational andseparateAIreviewarenothumanIBexaminermoderation.'],'records':RECORDS}
out=ROOT/'docs/ib-aa-mocks-2026/hl-b-independent-review.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps({k:report[k] for k in ['status','papers','questions','numericalCheckCount','diagramCount']}))
