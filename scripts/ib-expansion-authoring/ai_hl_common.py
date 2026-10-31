"""Original AI HL authoring helpers. Course: first assessment 2021, final 2028.

No questions or numeric data are imported from published question banks.
"""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import sys, math, json, hashlib, html, re
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'work' / 'aa-sl-deps'))
import numpy as np
from scipy import stats, integrate, optimize
LEDGER=[]
FAMILIES={}
TOPICS={'na':'number-algebra','fn':'functions','gt':'geometry-trigonometry','sp':'statistics-probability','ca':'calculus'}
SCOPE={
 '1.2':'arithmetic sequences, series and applications','1.3':'geometric sequences, series and applications','1.4':'compound interest and real investment values','1.6':'rounding bounds and measurement error','1.7':'amortization and end-of-period annuities using technology','1.9':'laws of natural and common logarithms','1.10':'rational exponents','1.11':'convergent infinite geometric series','1.12':'Cartesian complex arithmetic, quadratic solutions and Argand diagrams','1.13':'polar/exponential complex forms, integer powers and same-frequency phasor addition','1.14':'matrix operations, inverses and real-life systems','1.15':'distinct-real 2-by-2 eigenvalues, eigenvectors, diagonalization and matrix powers',
 '2.5':'linear, quadratic, exponential, cubic and direct/inverse-variation models','2.6':'fitting, testing and using contextual models','2.7':'composite functions and inverses with domain restriction','2.8':'ordered transformations of function graphs','2.9':'half-life, logarithmic, shifted sinusoidal, logistic and piecewise models, and introduced contextual models','2.10':'log-log and semi-log linearization and interpretation',
 '3.3':'applications of triangle trigonometry in context','3.6':'Voronoi sites, vertices, cells and boundaries','3.7':'radian measure and circular geometry','3.8':'unit-circle trigonometry and the Pythagorean identity','3.9':'matrix transformations, determinants and iterative fractal design','3.10':'vector components, magnitudes and normalization','3.11':'vector and parametric line equations','3.12':'relative vector motion, intersections and closest approach','3.13':'scalar/vector products, projections, angles and areas','3.15':'adjacency matrices, walk counts and graph transition matrices','3.16':'Euler routes, MST algorithms, Chinese postman pairings and travelling-salesman bounds',
 '4.7':'discrete random variables and expectation','4.8':'binomial distribution','4.9':'normal distribution and quantiles','4.11':'chi-square independence and pooled two-sample t-tests','4.12':'valid/reliable data collection and goodness-of-fit degrees of freedom with fitted parameters','4.13':'nonlinear least-squares regression, residual sums and coefficient of determination','4.14':'linear random-variable transformations and independent variance combinations','4.15':'linear combinations of normal variables and the central limit theorem','4.16':'normal/t confidence intervals according to known/unknown population SD','4.17':'Poisson model, constant-rate independence and sums','4.18':'normal, t, matched-pairs, one-tailed binomial/Poisson and zero-correlation tests; critical regions and Type I/II errors','4.19':'column Markov transition matrices, powers and steady distributions',
 '5.9':'chain/product/quotient differentiation and related rates','5.10':'second derivatives, concavity, inflection and stationary-point classification','5.11':'standard antiderivatives and inspection/substitution','5.12':'signed areas and volumes of revolution','5.13':'displacement, speed, acceleration and total distance','5.14':'contextual differential equations and separation of variables','5.15':'slope-field interpretation','5.16':'forward Euler for scalar and simultaneously updated coupled systems','5.17':'phase portraits and real-distinct coupled-system solutions','5.18':'second-order equations represented as coupled first-order systems, numerical and exact real-distinct solutions'
}
def sf(x,n=3):
    # Remove binary arithmetic noise far beyond the requested precision before
    # decimal half-up display (for example 2.6449999999999996 -> 2.645).
    # All subsequent calculations still use the original unrounded values.
    d=Decimal(format(float(x),'.14g'))
    if not d: return '0.00'
    q=Decimal(1).scaleb(d.copy_abs().adjusted()-n+1)
    z=d.quantize(q,rounding=ROUND_HALF_UP)
    return format(z,'f')
def m(x): return '$'+str(x)+'$'
def mat(a): return r'\begin{pmatrix}'+r'\\'.join('&'.join(str(x) for x in row) for row in a)+r'\end{pmatrix}'
def vec(a): return mat([[x] for x in a])
def P(prompt,*steps):
    return {'prompt':prompt,'steps':[{'code':s[0],'text':s[1]} for s in steps]}
def M(t): return ('M1',t)
def A(t): return ('A1',t)
def R(t): return ('R1',t)
def clean_text(s):
    def replace(match):
        value=float(match.group())
        return f'{value:.10g}' if abs(value-round(value,8))<1e-12 else match.group()
    return re.sub(r'\d+\.\d{13,}',replace,s)
def add(topic,family,v,title,sub,code,stem,parts,values=None,diagram=None,private=None,scope=None):
    n=4*(family-1)+v+1
    qs=[]; schemes=[]
    for i,p in enumerate(parts):
        label=chr(97+i); count=len(p['steps'])
        qs.append({'label':label,'prompt':clean_text(p['prompt']),'marks':count})
        schemes.append({'part':label,'steps':[{'code':s['code'],'text':clean_text(s['text'])} for s in p['steps']]})
    marks=sum(p['marks'] for p in qs)
    q={'id':f'ib-aihl-{topic}-{n:03d}','subject':'math-ai-hl','topicId':TOPICS[topic],'collectionId':'ai-hl-'+TOPICS[topic],'number':n,'title':title,'subtopic':sub,'syllabusCode':code,'level':'ahl' if int(code.split('.')[1])>({'na':8,'fn':6,'gt':6,'sp':11,'ca':8}[topic]) else 'sl','difficulty':'hard' if marks>=12 else 'medium','calculator':True,'marks':marks,'stem':stem+' Unless otherwise stated, give numerical answers exactly or to three significant figures.','parts':qs,'markScheme':schemes,'source':{'document':'Independent syllabus-authored practice','question':n},'verification':{'method':'Deterministic Python author calculation; Decimal ROUND_HALF_UP display; per-record numerical and syllabus ledger; subsequent independent review required','notes':f'Original family {topic}-{family:02d}, variant {v+1}. Unrounded numeric working is retained in the author ledger. Primary scope {code}; '+(scope or sub)+'.'},'status':'published','examStyle':'problem-solving' if marks>=12 else ('extended-response' if marks>=8 else 'short-response')}
    q['stem']=clean_text(q['stem'])
    if (topic=='na' and family in [7,10,17]) or (topic=='gt' and family==1):
        q['difficulty']='easy' # Routine calculator foundations within the HL bank.
    if diagram:q.update(diagramSvg=diagram,diagramCaption='Original mathematical diagram; use the labelled data and the shown axis scales.')
    if private:q.update(markSchemeDiagramSvg=private,markSchemeDiagramCaption='Private solution sketch.')
    FAMILIES.setdefault(topic,{}).setdefault(family,[]).append(q)
    LEDGER.append({'id':q['id'],'family':f'{topic}-{family:02d}','variant':v+1,'syllabusCode':code,'level':q['level'],'scopeRationale':f'The first-assessment-2021 AI guide section {code} includes {SCOPE[code]}. This record examines '+(scope or sub)+'.','scopeStatus':'author-confirmed against official course guide','marks':marks,'numericValues':values or {},'figureHashes':{k:hashlib.sha256(q[k].encode()).hexdigest() for k in ['diagramSvg','markSchemeDiagramSvg'] if k in q}})
    return q
def svg(body,w=600,h=380):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="white"/>'+body+'</svg>'
def text(x,y,s,size=16):return f'<text x="{x}" y="{y}" font-family="Arial" font-size="{size}" fill="#172a3a">{html.escape(str(s))}</text>'
def line(x,y,a,b,c='#334155',width=2):return f'<line x1="{x:.3f}" y1="{y:.3f}" x2="{a:.3f}" y2="{b:.3f}" stroke="{c}" stroke-width="{width}"/>'
def network(edges,coords=None):
    coords=coords or {'A':(80,80),'B':(300,50),'C':(520,100),'D':(450,290),'E':(150,290)}
    b=''
    for u,w,c in edges:
        x,y=coords[u]; a,z=coords[w];b+=line(x,y,a,z)+f'<rect x="{(x+a)/2-14}" y="{(y+z)/2-15}" width="35" height="23" fill="white"/>'+text((x+a)/2-9,(y+z)/2+3,c)
    for k,(x,y) in coords.items():b+=f'<circle cx="{x}" cy="{y}" r="15" fill="#e0f2fe" stroke="#075985"/>'+text(x-5,y+5,k)
    return svg(b)
def plot(curves=(),points=(),xmin=0,xmax=10,ymin=0,ymax=10,xlabel='x',ylabel='y',segments=(),labels=(),equal=False):
    sx=480/(xmax-xmin);sy=270/(ymax-ymin)
    if equal:sx=sy=min(sx,sy)
    left=60+(480-sx*(xmax-xmin))/2
    X=lambda x:left+sx*(x-xmin);Y=lambda y:320-sy*(y-ymin)
    axY=Y(0 if ymin<=0<=ymax else ymin);axX=X(0 if xmin<=0<=xmax else xmin)
    b=line(X(xmin),axY,X(xmax)+8,axY)+line(axX,Y(ymin),axX,Y(ymax)-8)+text(X(xmax)+12,axY+20,xlabel)+text(axX-30,Y(ymax)-15,ylabel)
    xticks=list(range(math.ceil(xmin),math.floor(xmax)+1)) if xmax-xmin<=15 else np.linspace(xmin,xmax,6)
    yticks=list(range(math.ceil(ymin),math.floor(ymax)+1)) if ymax-ymin<=15 else np.linspace(ymin,ymax,6)
    for x in xticks:b+=line(X(x),axY,X(x),axY+5)+text(X(x)-6,axY+22,f'{x:g}',11)
    for y in yticks:
        if y!=0:b+=line(axX-5,Y(y),axX,Y(y))+text(axX-30,Y(y)+4,f'{y:g}',11)
    for f in curves:
        xy=[(X(float(x)),Y(float(f(x)))) for x in np.linspace(xmin,xmax,161)]
        b+='<path d="'+' '.join(('M' if j==0 else 'L')+f'{x:.2f},{y:.2f}' for j,(x,y) in enumerate(xy))+'" fill="none" stroke="#0369a1" stroke-width="2.5"/>'
    for x,y,label in points:
        label=f'{label} ({x:g}, {y:g})'
        labelwidth=len(label)*7
        tx=X(x)-labelwidth-8 if (x<0 and xmin<0) or X(x)>425 else X(x)+8
        b+=f'<circle cx="{X(x):.2f}" cy="{Y(y):.2f}" r="4" fill="#b45309"/>'+f'<rect x="{tx-2:.2f}" y="{Y(y)-22:.2f}" width="{labelwidth+4}" height="17" fill="white"/>'+text(tx,Y(y)-9,label,14)
    for x,y,a,z in segments:b+=line(X(x),Y(y),X(a),Y(z),'#64748b',1.5)
    for x,y,s in labels:b+=text(X(x),Y(y),s,14)
    return svg(b)
def slopefield(f,xmax=3,ymax=5):
    seg=[]
    for x in np.linspace(0,xmax,9):
      for y in np.linspace(0,ymax,9):
        d=float(f(x,y)); dx=.08/math.sqrt(1+d*d);dy=d*dx
        seg.append((x-dx,y-dy,x+dx,y+dy))
    return plot(xmax=xmax,ymax=ymax,segments=seg)
def write(limit=100):
    out=ROOT/'content'/'ib'/'math-ai-hl';out.mkdir(parents=True,exist_ok=True)
    for topic,name in TOPICS.items():
        arr=sorted([q for qs in FAMILIES[topic].values() for q in qs if q['number']<=limit],key=lambda q:q['number'])
        assert len(arr)==limit,(topic,len(arr))
        (out/(name+'.json')).write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    d=ROOT/'docs'/'ib-expansion-reviews';d.mkdir(parents=True,exist_ok=True)
    rows=[r for r in LEDGER if int(r['id'][-3:])<=limit]
    (d/'ai-hl-author-ledger.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2,default=lambda x:float(x))+'\n',encoding='utf8',newline='\n')
