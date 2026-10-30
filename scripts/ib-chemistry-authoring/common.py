"""Shared deterministic authoring helpers; no external chemistry packages required."""
import hashlib
import html
import json
import math
import random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def f(value, sig=3):
    """Plain numeric form for ledgers and SVG labels."""
    return format(value, f'.{sig}g')

def v(value, sig=3):
    """Number for use inside dollar-delimited mathematics."""
    value = f(value, sig)
    if 'e' in value:
        mantissa, exponent = value.split('e')
        return mantissa + r'\times10^{' + str(int(exponent)) + '}'
    return value

def quantity(value, unit='', sig=3):
    return '$' + v(value, sig) + (r'\,\mathrm{' + unit + '}' if unit else '') + '$'

def step(text, code='A1'):
    return code, text

def p(prompt, *steps):
    return prompt, list(steps)

def text(x, y, label, size=16, anchor='middle', colour='#233442'):
    return f'<text x="{x:g}" y="{y:g}" text-anchor="{anchor}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" fill="{colour}">{html.escape(str(label))}</text>'

def line(x1, y1, x2, y2, colour='#31556b', width=2, arrow=False, dashed=False):
    shape=f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{colour}" stroke-width="{width}"'+(' stroke-dasharray="6 5"' if dashed else '')+'/>'
    if arrow:
        length=math.hypot(x2-x1,y2-y1);assert length>0
        dx,dy=(x2-x1)/length,(y2-y1)/length
        shape+=f'<polygon points="{x2:g},{y2:g} {x2-10*dx+4*dy:g},{y2-10*dy-4*dx:g} {x2-10*dx-4*dy:g},{y2-10*dy+4*dx:g}" fill="{colour}"/>'
    return shape

def svg(body, width=800, height=380):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img"><rect width="{width}" height="{height}" fill="white"/>'+body+'</svg>'

def graph(title, xlabel, ylabel, points, *, width=800, height=390, y_limits=None):
    """A labelled data graph. Use measured coordinates, never a hidden answer."""
    assert len(points) >= 2
    xmin=min(0,min(x for x,y in points)); xmax=max(x for x,y in points)
    ymin=min(0,min(y for x,y in points)); ymax=max(y for x,y in points)
    if y_limits is not None:
        ymin,ymax=y_limits
        assert all(ymin<=y<=ymax for x,y in points)
    assert xmax>xmin and ymax>ymin
    left, right, top, bottom=90,width-35,65,height-80
    X=lambda x:left+(x-xmin)/(xmax-xmin)*(right-left)
    Y=lambda y:bottom-(y-ymin)/(ymax-ymin)*(bottom-top)
    body=text(width/2,25,title,17)+text(width/2,height-16,xlabel,15)+text(left,48,ylabel,14,'start')
    x_intervals=5 if y_limits is not None else 4
    for i in range(x_intervals+1):
        xx=xmin+(xmax-xmin)*i/x_intervals
        body+=line(X(xx),top,X(xx),bottom,'#e7ecf0',1)+text(X(xx),bottom+25,f(xx),13)
    for i in range(5):
        yy=ymin+(ymax-ymin)*i/4
        body+=line(left,Y(yy),right,Y(yy),'#e7ecf0',1)+text(left-12,Y(yy)+4,f(yy),13,'end')
    body+=line(left,bottom,right+8,bottom,arrow=True)+line(left,bottom,left,top-8,arrow=True)
    coords=' '.join(f'{X(x):.3f},{Y(y):.3f}' for x,y in points)
    body+=f'<polyline points="{coords}" fill="none" stroke="#267f9a" stroke-width="2.5"/>'
    for x,y in points:
        body+=f'<circle cx="{X(x):.3f}" cy="{Y(y):.3f}" r="3.5" fill="#267f9a"/>'
    return svg(body,width,height)

class Bank:
    def __init__(self, theme, topic_id, subtopics):
        self.theme,self.topic_id,self.subtopics=theme,topic_id,subtopics
        self.questions=[]

    def add(self, code, level, difficulty, title, stem, *, parts=None,
            correct=None, distractors=None, reasoning=None, diagram=None,
            worked=None, summary=None, question_type='structured', notes=''):
        number=len(self.questions)+1
        assert code in self.subtopics and level in ('sl','ahl')
        assert difficulty in ('easy','medium','hard')
        q={'id':f'ib-chem-{self.theme.lower()}-{number:03d}', 'subject':'chemistry',
           'topicId':self.topic_id,'collectionId':'chemistry-'+self.topic_id,
           'number':number,'title':title,'subtopic':self.subtopics[code],
           'syllabusCode':code,'level':level,'difficulty':difficulty,'calculator':True,
           'stem':stem,'parts':[],'markScheme':[],
           'source':{'document':'Independent syllabus-authored practice','question':number},
           'verification':{'method':'Deterministic independent syllabus authoring with recalculated answers',
                           'notes':notes or 'Physical assumptions, chemical species and mark allocations checked in the authoring model.'},
           'status':'published'}
        if correct is not None:
            assert distractors is not None and len(distractors)==3 and reasoning
            options=[correct]+list(distractors)
            assert len(set(options))==4
            order=list(range(4))
            random.Random(hashlib.sha256((q['id']+stem).encode()).hexdigest()).shuffle(order)
            q['options']=[{'label':'ABCD'[j],'text':options[i]} for j,i in enumerate(order)]
            q['correctOption']='ABCD'[order.index(0)]
            q['questionType']='multiple-choice';q['marks']=1
            q['markScheme']=[{'part':'','steps':[{'code':'A1','text':'Option '+q['correctOption']+'. '+reasoning}]}]
        else:
            assert parts and question_type in ('structured','data-based')
            q['questionType']=question_type
            for i,(prompt,steps) in enumerate(parts):
                assert steps
                marks=sum(int(code[1:]) for code,t in steps if code!='AG')
                assert marks>0
                label=chr(ord('a')+i)
                q['parts'].append({'label':label,'prompt':prompt,'marks':marks})
                q['markScheme'].append({'part':label,'steps':[{'code':code,'text':t} for code,t in steps]})
            q['marks']=sum(part['marks'] for part in q['parts'])
        if diagram:q['diagramSvg']=diagram
        if worked:q['markSchemeDiagramSvg']=worked
        if summary:q['answerSummary']=summary
        self.questions.append(q)
        return q

    def write(self, expected):
        assert len(self.questions)==expected,(self.topic_id,len(self.questions),expected)
        directory=ROOT/'content/ib/chemistry';directory.mkdir(parents=True,exist_ok=True)
        path=directory/(self.topic_id+'.json')
        path.write_text(json.dumps(self.questions,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print(json.dumps({'collection':self.topic_id,'questions':len(self.questions),
            'levels':dict(Counter(q['level'] for q in self.questions)),
            'types':dict(Counter(q['questionType'] for q in self.questions)),
            'marks':sum(q['marks'] for q in self.questions)}))
