"""Original AI SL practice authoring. All figures are deterministic Python SVGs."""
import json, math, html, hashlib, statistics, re
from pathlib import Path
from collections import Counter
from statistics import NormalDist
from decimal import Decimal, ROUND_HALF_UP
ROOT=Path(__file__).resolve().parents[2]
LEDGER=[]
def n(v):
    d=Decimal(str(float(v)))
    if not d:return '0'
    return format(d.quantize(Decimal(1).scaleb(d.adjusted()-2),rounding=ROUND_HALF_UP),'f')
def tick(v):
    if abs(v-round(v))<1e-8:return str(round(v))
    return f'{v:.2f}'.rstrip('0').rstrip('.')
def money(v): return str(Decimal(str(float(v))).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))
def eq(a,b,tol=1e-8):
    assert math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol),(a,b)
def check(c,z): assert c,z
def M(z):return ('M1',z)
def A(z):return ('A1',z)
def R(z):return ('R1',z)
def P(z,*steps):return (z,steps)
def table(headers,rows):return '\n\n| '+' | '.join(map(str,headers))+' |\n| '+' | '.join('---' for _ in headers)+' |\n'+'\n'.join('| '+' | '.join(map(str,row))+' |' for row in rows)+'\n\n'
def bisect(f,a,b):
    assert f(a)*f(b)<=0,(a,b,f(a),f(b))
    for _ in range(90):
        c=(a+b)/2
        if f(a)*f(c)<=0:b=c
        else:a=c
    return (a+b)/2
def integral(f,a,b,N=2000):
    h=(b-a)/N
    return h/3*(f(a)+f(b)+4*sum(f(a+h*i) for i in range(1,N,2))+2*sum(f(a+h*i) for i in range(2,N,2)))
def binom_p(n_,p,k):return math.comb(n_,k)*p**k*(1-p)**(n_-k)
def linreg(xs,ys):
    xb=statistics.mean(xs);yb=statistics.mean(ys)
    Sxx=sum((a-xb)**2 for a in xs);Syy=sum((b-yb)**2 for b in ys);Sxy=sum((a-xb)*(b-yb) for a,b in zip(xs,ys))
    m=Sxy/Sxx;return m,yb-m*xb,Sxy/math.sqrt(Sxx*Syy)
def ranks(a):return [1+sum(x<v for x in a)+(sum(x==v for x in a)-1)/2 for v in a]
def t_cdf(v,df):
    c=math.exp(math.lgamma((df+1)/2)-math.lgamma(df/2))/math.sqrt(df*math.pi)
    return .5+integral(lambda u:c*(1+u*u/df)**(-(df+1)/2),0,v)
def rec(topic,short,fam,i,title,sub,code,stem,parts,checks,diagram=None,answer_diagram=None,diff='medium'):
    num=fam*4+i+1; ps=[];ms=[]
    for j,(p,ss) in enumerate(parts):
        label=chr(97+j);ps.append(dict(label=label,prompt=p,marks=len(ss)));ms.append(dict(part=label,steps=[dict(code=c,text=z) for c,z in ss]))
    q=dict(id=f'ib-aisl-{short}-{num:03d}',subject='math-ai-sl',topicId=topic,collectionId=f'ai-sl-{topic}',number=num,title=title,subtopic=sub,syllabusCode=code,level='sl',difficulty=diff,calculator=True,marks=sum(p['marks'] for p in ps),stem=stem,parts=ps,markScheme=ms,source=dict(document='Independent syllabus-authored practice',question=num),status='published',examStyle='extended-response' if sum(p['marks'] for p in ps)>=8 else 'short-response',verification=dict(method='Independent standard-library numerical and mathematical checks',notes=checks+' Rounding is to three significant figures unless otherwise specified.'))
    if diagram:q['diagramSvg']=diagram
    if answer_diagram:q['markSchemeDiagramSvg']=answer_diagram
    LEDGER.append(dict(id=q['id'],family=f'{short}-{fam+1:02d}',variant=i+1,syllabusCode=code,scope='AI SL first assessment 2021; final assessment 2028',marks=q['marks'],markCheck='Every M1/A1/R1 is one mark; part and question totals asserted',calculatorCheck='Calculator permitted; setup and interpretation explicitly marked',answerCheck=checks,diagramCheck='Python deterministic coordinates, standalone SVG XML and safety checked' if diagram or answer_diagram else 'No diagram needed',status='author-checked'))
    return q
def svg(es,w=640,h=360,label='Mathematical diagram'):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(label)}">'+''.join(es)+'</svg>'
def line(a,b,c='#334155',dash=False):return f'<line x1="{a[0]:.3f}" y1="{a[1]:.3f}" x2="{b[0]:.3f}" y2="{b[1]:.3f}" stroke="{c}" stroke-width="2"'+(' stroke-dasharray="6 5"' if dash else '')+'/>'
def txt(p,z,size=14):return f'<text x="{p[0]:.2f}" y="{p[1]:.2f}" font-family="Arial, sans-serif" font-size="{size}" fill="#0f172a">{html.escape(str(z))}</text>'
def dot(p):return f'<circle cx="{p[0]:.3f}" cy="{p[1]:.3f}" r="4" fill="#0f766e"/>'
def plot(fs,x0,x1,y0,y1,points=(),title='',xlabel='x',ylabel='y'):
    def p(x,y):return (60+520*(x-x0)/(x1-x0),300-245*(y-y0)/(y1-y0))
    es=[txt((60,24),title,16),line((60,300),(590,300)),line((60,300),(60,48)),txt((500,345),xlabel),txt((12,42),ylabel)]
    for k in range(6):
        a=x0+(x1-x0)*k/5;b=y0+(y1-y0)*k/5
        es +=[txt((p(a,y0)[0]-8,322),tick(a),11),txt((8,p(x0,b)[1]+4),tick(b),11),line(p(a,y0),p(a,y1),'#e2e8f0'),line(p(x0,b),p(x1,b),'#e2e8f0')]
    if y0<0<y1:es +=[line(p(x0,0),p(x1,0),'#64748b')]
    if x0<0<x1:es +=[line(p(0,y0),p(0,y1),'#64748b')]
    for j,f in enumerate(fs):
        seg=[]
        def flush():
            if len(seg)>1:es.append('<polyline points="'+' '.join(f'{a:.3f},{b:.3f}' for a,b in seg)+'" fill="none" stroke="'+['#0f766e','#b45309'][j%2]+'" stroke-width="2.6"/>')
        for k in range(701):
            x=x0+(x1-x0)*k/700
            try:y=f(x)
            except (ValueError,ZeroDivisionError,OverflowError):y=math.nan
            if math.isfinite(y) and y0<=y<=y1:seg.append(p(x,y))
            else:flush();seg=[]
        flush()
    for x,y,z in points:es +=[dot(p(x,y)),txt((p(x,y)[0]+6,p(x,y)[1]-8),z,12)]
    return svg(es)
def triangle(a,b,C):
    coords=[(0,0),(a,0),(b*math.cos(math.radians(C)),b*math.sin(math.radians(C)))];xx=[z[0] for z in coords];yy=[z[1] for z in coords];sc=min(440/(max(xx)-min(xx)),220/max(yy));ps=[(90+(u-min(xx))*sc,285-v*sc) for u,v in coords]
    es=[line(ps[j],ps[(j+1)%3]) for j in range(3)]
    for j,l in enumerate('ABC'):es +=[txt((ps[j][0]-10,ps[j][1]+(-10 if j==2 else 23)),l)]
    es +=[txt(((ps[0][0]+ps[1][0])/2,320),f'{a:g}'),txt(((ps[0][0]+ps[2][0])/2-40,(ps[0][1]+ps[2][1])/2),f'{b:g}'),txt((ps[0][0]+30,ps[0][1]-15),f'{C:g}°')]
    return svg(es,label='Triangle ABC with stated side lengths and included angle')
def sector(r,deg):
    a=math.radians(deg);O=(230,190);rr=135;E=(O[0]+rr*math.cos(a),O[1]-rr*math.sin(a));S=(O[0]+rr,O[1]);return svg([f'<path d="M {O[0]} {O[1]} L {S[0]} {S[1]} A {rr} {rr} 0 {int(deg>180)} 0 {E[0]:.3f} {E[1]:.3f} Z" fill="#e0f2f1" stroke="#0f766e" stroke-width="2"/>',txt((210,215),'O'),txt((280,214),f'r = {r:g}'),txt((252,176),f'{deg:g}°')])
def boxplot(vals,label=''):
    lo,q1,med,q3,hi=vals;span=hi-lo;p=lambda v:(65+500*(v-lo)/span,160);es=[txt((65,40),label),line(p(lo),p(hi))]
    es +=[f'<rect x="{p(q1)[0]:.3f}" y="125" width="{p(q3)[0]-p(q1)[0]:.3f}" height="70" fill="#e0f2f1" stroke="#0f766e" stroke-width="2"/>',line((p(med)[0],125),(p(med)[0],195))]
    for v in vals:es +=[line((p(v)[0],145),(p(v)[0],175)) if v in (lo,hi) else '',txt((p(v)[0]-8,225),v)]
    return svg(es,h=280)
def save(topic,qs):
    qs.sort(key=lambda q:q['number'])
    assert len(qs)==80 and len({q['id'] for q in qs})==80
    for q in qs:
        assert q['marks']==sum(p['marks'] for p in q['parts'])
        for p,m in zip(q['parts'],q['markScheme']):assert len(m['steps'])==p['marks']
        for f in ['diagramSvg','markSchemeDiagramSvg']:
            if f in q:
                import xml.etree.ElementTree as ET
                ET.fromstring(q[f]);assert not re.search(r'<(?:script|style|use|image|foreignObject)|href=|url\(',q[f])
    path=ROOT/'content'/'ib'/'math-ai-sl'/f'{topic}.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(qs,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(topic,len(qs),'figures',sum('diagramSvg'in q for q in qs))
def report():
    path=ROOT/'docs'/'ib-maths-reviews';path.mkdir(parents=True,exist_ok=True)
    (path/'ai-sl-ledger.json').write_text(json.dumps(LEDGER,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    fs={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'content'/'ib'/'math-ai-sl').glob('*.json'))}
    (path/'ai-sl-hashes.json').write_text(json.dumps(dict(questionCount=len(LEDGER),files=fs,ledgerSha256=hashlib.sha256((path/'ai-sl-ledger.json').read_bytes()).hexdigest()),indent=2)+'\n',encoding='utf-8')
    qs=[q for p in sorted((ROOT/'content'/'ib'/'math-ai-sl').glob('*.json')) for q in json.loads(p.read_text(encoding='utf-8'))]
    overview=dict(course='Mathematics: applications and interpretation SL',syllabus='First assessment 2021; final assessment 2028; excludes first-assessment-2029 revision',provenance='Original independently syllabus-authored practice; no copied question wording or artwork',sources=['https://ibo.org/globalassets/new-structure/university-admission/pdfs/dp-mathematics-applications-and-interpretation-guide-en.pdf','https://www.ibo.org/globalassets/new-structure/university-admission/pdfs/dp-mathematics-applications-and-interpretation-specimen-papers-en.pdf','https://www.ibo.org/programmes/diploma-programme/assessment-and-exams/sample-exam-papers/'],assessment=dict(paper1='Technology required; 90 minutes; 80 marks; short response',paper2='Technology required; 90 minutes; 80 marks; extended response',paper3='Not an AI SL assessment'),questionCount=len(qs),familyCount=100,maximumVariantsPerFamily=4,topicCounts=dict(Counter(q['topicId'] for q in qs)),difficultyCounts=dict(Counter(q['difficulty'] for q in qs)),styles=dict(Counter(q['examStyle'] for q in qs)),calculatorRequiredCount=sum(q['calculator'] for q in qs),questionDiagrams=sum('diagramSvg'in q for q in qs),solutionDiagrams=sum('markSchemeDiagramSvg'in q for q in qs),syllabusCodes={t:sorted({q['syllabusCode'] for q in qs if q['topicId']==t},key=lambda c:float(c)) for t in {q['topicId'] for q in qs}},scopeReview=['Integer powers and numerical logarithms; no logarithm laws, infinite geometric series, complex numbers or matrices.','Financial solver questions use end-of-period payments and independently verified recurrence balances.','Functions use numerical inverse concept, models fitted through given observations, degree sinusoidal features; no general inverse derivation or nonlinear regression.','Degree sectors, right-triangle 3D geometry, unique sine-rule triangles, perpendicular bisectors and Voronoi boundaries with the correct edge/ray restrictions.','Chi-square expected counts exceed5 and degrees of freedom exceed1; goodness-of-fit df=categories-1; t-tests pooled, unpaired, unknown equal variances, normal populations.','Analytic derivatives/integrals use integer powers; no chain/product/quotient rules, transcendental derivatives, ODEs or kinematics exam questions.'],markingReview='Distinct M1 method, A1 result and R1 reasoning criteria. Every part and question mark sum is asserted; no marks for merely copying given answers. Equivalent forms and correct follow-through accepted when the changed value preserves the demand.',precisionReview='Unrounded working retained; three significant figures use decimal half-up rounding with explicit trailing zeros. Currency overrides to cents and integer counts are rounded as instructed.',files=fs,authorLedger='ai-sl-ledger.json',numericReview='ai-sl-numeric-review.json',independentReview='ai-sl-independent-review.json')
    (path/'ai-sl-author-review.json').write_text(json.dumps(overview,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
