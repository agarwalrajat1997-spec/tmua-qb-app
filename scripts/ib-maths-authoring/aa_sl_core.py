"""Independent AA SL authoring utilities. SVGs are calculated here in Python."""
import json, math, hashlib, html, sys, re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'work'/'aa-sl-deps'))
import sympy as s
from scipy.integrate import quad
from scipy.optimize import brentq, minimize_scalar
from scipy.stats import binom, norm, linregress

x=s.symbols('x', real=True)
t=s.symbols('t', real=True)
LEDGER=[]
def L(v): return s.latex(s.sympify(v))
def n(v):
    d=Decimal(str(float(v)))
    if not d:return '0'
    return format(d.quantize(Decimal(1).scaleb(d.adjusted()-2),rounding=ROUND_HALF_UP),'f')
def frac(a,b): return L(s.Rational(a,b))
def eq(a,b,tol=1e-8):
    if isinstance(a,(s.Expr,int)) and isinstance(b,(s.Expr,int)):
        assert s.simplify(a-b)==0,(a,b)
    else: assert math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol),(a,b)
def checked(condition,message):
    assert bool(condition), message
def M(text): return ('M1',text)
def A(text): return ('A1',text)
def R(text): return ('R1',text)
def part(prompt,*steps): return (prompt,steps)
def rec(topic,short,family,i,title,sub,code,diff,calc,stem,parts,checks,diagram=None,answer_diagram=None):
    number=4*family+i+1
    qs=[]; ms=[]
    for j,(prompt,steps) in enumerate(parts):
        label=chr(97+j)
        qs.append(dict(label=label,prompt=prompt,marks=len(steps)))
        ms.append(dict(part=label,steps=[dict(code=c,text=z) for c,z in steps]))
    q=dict(id=f'ib-aasl-{short}-{number:03d}',subject='math-aa-sl',topicId=topic,
        collectionId=f'aa-sl-{topic}',number=number,title=title,subtopic=sub,difficulty=diff,
        calculator=calc,marks=sum(p['marks'] for p in qs),stem=stem,parts=qs,markScheme=ms,
        source=dict(document='Independent syllabus-authored practice',question=number),status='published',
        syllabusCode=code,level='sl',examStyle='extended-response' if sum(p['marks'] for p in qs)>=8 else 'short-response',
        verification=dict(method='Independent symbolic/numeric and mathematical reasoning checks',notes='Displayed parameters were recalculated; see the per-record AA SL author-review ledger. '+checks))
    if diagram:q['diagramSvg']=diagram
    if answer_diagram:q['markSchemeDiagramSvg']=answer_diagram
    LEDGER.append(dict(id=q['id'],family=f'{short}-{family+1:02d}',variant=i+1,syllabusCode=code,scope='SL content checked against first-assessment-2021 AA guide',marks=q['marks'],partMarkTotals='checked',marking='one distinct M1/A1/R1 point per awarded mark; given answers do not earn accuracy marks',reasoningReview=checks,calculatorReview='GDC calculations supported by explicit setup and precision' if calc else 'exact arithmetic, manageable values and analytic method',diagramReview='Python coordinate geometry; labels and viewBox checked' if diagram or answer_diagram else 'not required',status='author-checked'))
    return q

def svg(elements,w=620,h=360):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="Mathematical diagram">'+''.join(elements)+'</svg>'
def line(a,b,color='#334155',dash=False):
    return f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" stroke="{color}" stroke-width="2"'+(' stroke-dasharray="6 5"' if dash else '')+'/>'
def txt(p,z,size=15):return f'<text x="{p[0]:.2f}" y="{p[1]:.2f}" font-family="Arial, sans-serif" font-size="{size}" fill="#0f172a">{html.escape(str(z))}</text>'
def dot(p):return f'<circle cx="{p[0]:.2f}" cy="{p[1]:.2f}" r="3.5" fill="#0f766e"/>'
def plot(funcs,xmin=-4,xmax=4,ymin=-3,ymax=8,points=(),vlines=(),hlines=(),title=''):
    W,H=620,360
    def p(a,b):return (55+(a-xmin)/(xmax-xmin)*520,310-(b-ymin)/(ymax-ymin)*265)
    e=[txt((55,24),title,16)]
    axis_y=0 if ymin<=0<=ymax else ymin
    axis_x=0 if xmin<=0<=xmax else xmin
    e += [line(p(xmin,axis_y),p(xmax,axis_y)),txt((585,p(axis_x,axis_y)[1]+5),'x')]
    e += [line(p(axis_x,ymin),p(axis_x,ymax)),txt((p(axis_x,axis_y)[0]+8,43),'y')]
    def ticks(lo,hi):
        raw=(hi-lo)/7;unit=10**math.floor(math.log10(raw));step=next(k*unit for k in [1,2,5,10] if k*unit>=raw)
        return [j*step for j in range(math.ceil(lo/step),math.floor(hi/step)+1)]
    for a in ticks(xmin,xmax):
        if a:e +=[line(p(a,axis_y-.08*(ymax-ymin)/10),p(a,axis_y+.08*(ymax-ymin)/10)),txt((p(a,axis_y)[0]-8,p(a,axis_y)[1]+19),f'{a:g}',12)]
    for b in ticks(ymin,ymax):
        if b:e +=[txt((p(axis_x,b)[0]-33,p(axis_x,b)[1]+4),f'{b:g}',12)]
    for a in vlines:e +=[line(p(a,ymin),p(a,ymax),'#64748b',True)]
    for b in hlines:e +=[line(p(xmin,b),p(xmax,b),'#64748b',True)]
    for idx,f in enumerate(funcs):
        seg=[]
        def flush():
            if len(seg)>1:e.append('<polyline points="'+' '.join(f'{a:.2f},{b:.2f}' for a,b in seg)+'" fill="none" stroke="'+['#0f766e','#b45309','#7c3aed'][idx%3]+'" stroke-width="2.5"/>')
        for k in range(801):
            a=xmin+(xmax-xmin)*k/800
            try:b=float(f(a))
            except (ValueError,ZeroDivisionError,OverflowError):b=float('nan')
            if math.isfinite(b) and ymin<=b<=ymax:
                z=p(a,b)
                if seg and abs(z[1]-seg[-1][1])>H/2:flush();seg=[]
                seg.append(z)
            else:flush();seg=[]
        flush()
    for a,b,label in points:e +=[dot(p(a,b)),txt((p(a,b)[0]+7,p(a,b)[1]-9),label,13)]
    return svg(e)
def triangle(a,b,C,labels=None):
    # a,b are lengths meeting at origin; C is included angle in degrees.
    coords=[(0,0),(a,0),(b*math.cos(math.radians(C)),b*math.sin(math.radians(C)))]
    xx=[p[0] for p in coords]; yy=[p[1] for p in coords];sc=min(450/(max(xx)-min(xx)),220/max(yy))
    pts=[(85+(u-min(xx))*sc,290-v*sc) for u,v in coords]
    e=[line(pts[j],pts[(j+1)%3]) for j in range(3)]
    for j,z in enumerate(labels or ['A','B','C']):e += [txt((pts[j][0]-10,pts[j][1]+(-12 if j==2 else 23)),z)]
    e += [txt(((pts[0][0]+pts[1][0])/2,317),f'{a:g}'),txt(((pts[0][0]+pts[2][0])/2-38,(pts[0][1]+pts[2][1])/2),f'{b:g}'),txt((pts[0][0]+28,pts[0][1]-15),f'{C:g}°'),txt((380,25),'Diagram to stated scale',12)]
    return svg(e)
def sector(radius,theta,chord=False):
    O=(180,190); rr=130;end=(O[0]+rr*math.cos(theta),O[1]-rr*math.sin(theta));start=(O[0]+rr,O[1])
    e=[line(O,start),line(O,end),f'<path d="M {start[0]} {start[1]} A {rr} {rr} 0 {int(theta>math.pi)} 0 {end[0]:.3f} {end[1]:.3f}" fill="none" stroke="#0f766e" stroke-width="3"/>',txt((O[0]-22,O[1]+20),'O'),txt((O[0]+55,O[1]+22),f'r = {radius:g}'),txt((O[0]+30,O[1]-15),f'θ = {theta:.3g} rad')]
    if chord:e += [line(start,end,'#b45309')]
    return svg(e)
def boxplot(vals,label=''):
    lo,q1,med,q3,hi=map(float,vals);xmin=lo-(hi-lo)*.15;xmax=hi+(hi-lo)*.15
    def p(v):return (65+(v-xmin)/(xmax-xmin)*500,160)
    e=[txt((65,40),label),line(p(lo),p(hi))]
    for v in [lo,hi]:e +=[line((p(v)[0],140),(p(v)[0],180))]
    e +=[f'<rect x="{p(q1)[0]:.2f}" y="125" width="{p(q3)[0]-p(q1)[0]:.2f}" height="70" fill="#e0f2f1" stroke="#0f766e" stroke-width="2"/>',line((p(med)[0],125),(p(med)[0],195))]
    for v in vals:e +=[txt((p(float(v))[0]-9,225),v,13)]
    return svg(e,h=280)

def save(topic,questions):
    from aa_sl_enrich import enrich
    questions=enrich(topic,questions)
    def clean(v):
        if isinstance(v,str):
            if v.startswith('<svg'):return v
            return ''.join(z if j%2 else re.sub(r'(\d)(?=[A-Za-z])',r'\1 ',re.sub(r'([A-Za-z])(?=\d)',r'\1 ',z)) for j,z in enumerate(re.split(r'(\$[^$]*\$)',v)))
        if isinstance(v,list):return [clean(z) for z in v]
        if isinstance(v,dict):return {k:(z if k in ['code','part','label'] else clean(z)) for k,z in v.items()}
        return v
    # Restrict prose cleanup to visible prose; identifiers, codes and SVG attributes must stay byte-stable.
    for question in questions:
        for field in ['title','subtopic','stem','parts','markScheme','verification']:question[field]=clean(question[field])
    path=ROOT/'content'/'ib'/'math-aa-sl'/f'{topic}.json';path.parent.mkdir(parents=True,exist_ok=True)
    assert len(questions)==80
    assert len({q['id'] for q in questions})==80
    for q in questions:
        assert q['marks']==sum(p['marks'] for p in q['parts'])
        assert all(len(ms['steps'])==p['marks'] for p,ms in zip(q['parts'],q['markScheme']))
        for field in ['diagramSvg','markSchemeDiagramSvg']:
            if field in q:
                import xml.etree.ElementTree as ET
                ET.fromstring(q[field]);assert not any(z in q[field] for z in ['<style','<use','url(','<script','href='])
    path.write_text(json.dumps(questions,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(topic,len(questions),'diagrams',sum('diagramSvg'in q for q in questions),sum('markSchemeDiagramSvg'in q for q in questions))
