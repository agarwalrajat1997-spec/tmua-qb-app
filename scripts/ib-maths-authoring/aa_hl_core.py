"""Original AA HL additions; exact, numeric and reasoning evidence is kept per record."""
import json, math, html, sys, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'work/aa-sl-deps'))
sys.path.insert(0,str(ROOT/'work/aa-hl-dependencies'))
import sympy as s
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.stats import norm, binom
x,t,n=s.symbols('x t n',real=True)
LEDGER=[]
COUNTS={'number-algebra':229,'functions':129,'geometry-trigonometry':182,'statistics-probability':149,'calculus-1':126,'calculus-2':147}
SHORT={'number-algebra':'na','functions':'fn','geometry-trigonometry':'gt','statistics-probability':'sp','calculus-1':'c1','calculus-2':'c2'}
def L(v):return s.latex(s.sympify(v))
def N(v):
    value=float(v)
    if value==0:return '0.00'
    power=math.floor(math.log10(abs(value)))
    if -3<=power<5:return f'{value:.{max(0,2-power)}f}'
    mant,exponent=f'{value:.2e}'.split('e')
    return mant+r'\times10^{'+str(int(exponent))+'}'
def M(z):return ('M1',z)
def A(z):return ('A1',z)
def R(z):return ('R1',z)
def P(z,*steps):return (z,steps)
def eq(a,b):assert s.simplify(a-b)==0,(a,b)
def near(a,b,tol=1e-8):assert math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol),(a,b)
def ck(a,z):assert bool(a),z
def rec(coll,family,i,title,sub,code,diff,calc,stem,parts,evidence,style=None,diagram=None,answer_diagram=None):
    def prime(z):
        z=re.sub(r'([A-Za-z)])((?:\\prime)+)',lambda m:m.group(1)+"'"*m.group(2).count('\\prime'),z)
        pieces=re.split(r'(\$[^$]*\$)',z)
        changes={'f prime(x)':"$f'(x)$",'dy/dx':r'$dy/dx$','S(n)':r'$S_n$','I(n)':r'$I_n$','I(0)':r'$I_0$','P(t)':r'$P(t)$','A(0)':r'$A(0)$','R(k)':r'$R_k$','E(X)':r'$E(X)$','Var(X)':r'$\operatorname{Var}(X)$','E(Y)':r'$E(Y)$','Var(Y)':r'$\operatorname{Var}(Y)$','cos(theta)':r'$\cos\theta$','sin theta':r'$\sin\theta$','cos(2 theta)':r'$\cos(2\theta)$','arcsin(sin theta)':r'$\arcsin(\sin\theta)$','arccos(cos(2 theta))':r'$\arccos(\cos(2\theta))$'}
        for j in range(0,len(pieces),2):
            for old,new in sorted(changes.items(),key=lambda kv:-len(kv[0])):pieces[j]=pieces[j].replace(old,new)
        return ''.join(pieces)
    stem=prime(stem)
    number=COUNTS[coll]+2*family+i+1
    ps=[];ms=[]
    for k,(prompt,steps) in enumerate(parts):
        label=chr(97+k);ps.append(dict(label=label,prompt=prime(prompt),marks=len(steps)))
        ms.append(dict(part=label,steps=[dict(code=c,text=prime(z)) for c,z in steps]))
    marks=sum(p['marks'] for p in ps)
    q=dict(id=f'ib-aa-{SHORT[coll]}-{number:03d}',subject='math-aa-hl',topicId='calculus' if coll.startswith('calculus') else coll,collectionId=coll,number=number,title=title,subtopic=sub,difficulty=diff,calculator=calc,marks=marks,stem=stem,parts=ps,markScheme=ms,source=dict(document='Independent syllabus-authored practice',question=number),status='published',syllabusCode=code,level='ahl' if code in AHL else 'sl',examStyle=style or ('extended-response' if marks>=9 else 'short-response'),verification=dict(method='Independent symbolic/numerical and reasoned author checks',notes=evidence+' Accept mathematically equivalent methods and forms. Accuracy marks following a method depend on a valid method. Follow through is available for correct later working from an earlier numerical error unless it trivializes the demand.'))
    if diagram:q['diagramSvg']=diagram
    if answer_diagram:q['markSchemeDiagramSvg']=answer_diagram
    LEDGER.append(dict(id=q['id'],origin='original addition',family=family+1,variant=i+1,syllabusCode=code,level=q['level'],assessment='Paper 3 investigation style' if q['examStyle']=='problem-solving' else ('Paper 2 technology' if calc else 'Paper 1 analytic'),marks=marks,review=evidence,marking='Distinct single M1/A1/R1 awards; part totals and question total recalculated',status='author-checked'))
    return q
AHL={f'{a}.{b}' for a,lo,hi in [(1,10,16),(2,12,16),(3,9,18),(4,13,14),(5,12,19)] for b in range(lo,hi+1)}
def svg(elements,w=620,h=360):return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="Mathematical diagram">'+''.join(elements)+'</svg>'
def line(a,b,color='#334155',dash=False):return f'<line x1="{a[0]:.3f}" y1="{a[1]:.3f}" x2="{b[0]:.3f}" y2="{b[1]:.3f}" stroke="{color}" stroke-width="2"'+(' stroke-dasharray="6 5"' if dash else '')+'/>'
def txt(p,z,size=14):return f'<text x="{p[0]:.3f}" y="{p[1]:.3f}" font-family="Arial, sans-serif" font-size="{size}" fill="#0f172a">{html.escape(str(z))}</text>'
def plot(f,xlim=(-3,3),ylim=(-3,6),points=(),asym=(),title=''):
    xmin,xmax=xlim;ymin,ymax=ylim
    def p(a,b):return (55+(a-xmin)/(xmax-xmin)*515,307-(b-ymin)/(ymax-ymin)*260)
    e=[txt((55,24),title,16)]
    if ymin<=0<=ymax:e+=[line(p(xmin,0),p(xmax,0)),txt((584,p(0,0)[1]+4),'x')]
    if xmin<=0<=xmax:e+=[line(p(0,ymin),p(0,ymax)),txt((p(0,0)[0]+7,43),'y')]
    for a in asym:e.append(line(p(a,ymin),p(a,ymax),'#64748b',True))
    for a in range(math.ceil(xmin),math.floor(xmax)+1):
        if ymin<=0<=ymax and a:e.append(txt((p(a,0)[0]-4,p(a,0)[1]+19),a,11))
    seg=[]
    def flush():
        if len(seg)>1:e.append('<polyline points="'+' '.join(f'{a:.3f},{b:.3f}' for a,b in seg)+'" fill="none" stroke="#0f766e" stroke-width="2.5"/>')
    for k in range(1001):
        a=xmin+(xmax-xmin)*k/1000
        try:b=float(f(a))
        except (ValueError,ZeroDivisionError,OverflowError):b=float('nan')
        if math.isfinite(b) and ymin<=b<=ymax:
            z=p(a,b)
            if seg and abs(z[1]-seg[-1][1])>140:flush();seg=[]
            seg.append(z)
        else:flush();seg=[]
    flush()
    for a,b,label in points:
        u,v=p(a,b);e +=[f'<circle cx="{u:.3f}" cy="{v:.3f}" r="3.5" fill="#0f766e"/>',txt((u+6,v-9),label,12)]
    return svg(e)
def argand(points,title='Argand diagram'):
    xmax=max(4,max(abs(complex(z).real) for _,z in points)+1);ymax=max(4,max(abs(complex(z).imag) for _,z in points)+1)
    def p(z):return (310+complex(z).real*240/xmax,185-complex(z).imag*135/ymax)
    e=[txt((30,22),title,16),line((50,185),(570,185)),line((310,330),(310,40)),txt((576,183),'Re'),txt((318,42),'Im')]
    for name,z in points:
        q=p(z);e +=[line((310,185),q,'#0f766e'),f'<circle cx="{q[0]:.3f}" cy="{q[1]:.3f}" r="3" fill="#0f766e"/>',txt((q[0]+7,q[1]-8),name)]
    return svg(e)
def save(coll,items):
    assert len(items)==20
    f=ROOT/'content/ib/math-aa-hl'/f'{coll}.json';a=json.loads(f.read_text(encoding='utf8'))[:COUNTS[coll]]
    assert [q['number'] for q in a]==list(range(1,COUNTS[coll]+1))
    f.write_text(json.dumps(a+items,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    d=ROOT/'docs/ib-maths-reviews';d.mkdir(exist_ok=True)
    (d/f'aa-hl-{coll}-additions-ledger.json').write_text(json.dumps([r for r in LEDGER if r['id'].split('-')[2]==SHORT[coll]],ensure_ascii=False,indent=2)+'\n',encoding='utf8')
