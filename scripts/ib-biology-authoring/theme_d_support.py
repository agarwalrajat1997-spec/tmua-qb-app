"""Deterministic original Biology Theme D authoring and diagram helpers."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import math
import random
import re
from theme_c_support import A, R, M, P, T, txt, line, arrow, box, SVG, graph, num

ROOT=Path(__file__).resolve().parents[2]
TOPICS={'D1.1':'DNA replication','D1.2':'Protein synthesis','D1.3':'Mutation and gene editing','D2.1':'Cell and nuclear division','D2.2':'Gene expression','D2.3':'Water potential','D3.1':'Reproduction','D3.2':'Inheritance','D3.3':'Homeostasis','D4.1':'Natural selection','D4.2':'Stability and change','D4.3':'Climate change'}

class Bank:
    def __init__(self):self.qs=[];self.ledger=[];self.checks=[]
    def add(self,code,title,stem,*,parts=None,options=None,reason='',level='sl',difficulty='medium',kind='structured',diagram=None,worked=None,family=None,notes=''):
        n=len(self.qs)+1
        assert code in TOPICS and level in ('sl','ahl')
        q={'id':f'ib-bio-d-{n:03d}','subject':'biology','topicId':'continuity-change','collectionId':'biology-continuity-change','number':n,'title':title,'subtopic':TOPICS[code],'syllabusCode':code,'level':level,'questionType':'multiple-choice' if options else kind,'difficulty':difficulty,'calculator':True,'stem':stem,'source':{'document':'Independent syllabus-authored practice','question':n},'verification':{'method':'Independent syllabus authoring, explicit biological marking points and displayed-data calculation checks','notes':f'Corrected March 2024 Biology guide, subtopic {code}; '+notes+' All datasets are constructed for practice. Original wording and diagrams.'},'status':'published'}
        if options:
            assert len(set(options))==4 and reason
            order=list(range(4));random.Random(q['id']).shuffle(order)
            q.update(marks=1,parts=[],options=[{'label':'ABCD'[i],'text':options[j]} for i,j in enumerate(order)],correctOption='ABCD'[order.index(0)])
            q['markScheme']=[{'part':'','steps':[{'code':'A1','text':q['correctOption']+'. '+reason}]}]
        else:
            assert parts
            q['parts']=[];q['markScheme']=[]
            for i,(prompt,points) in enumerate(parts):
                label=chr(97+i);marks=sum(int(c[1:]) for c,_ in points if c!='AG')
                q['parts'].append({'label':label,'prompt':prompt,'marks':marks})
                q['markScheme'].append({'part':label,'steps':[{'code':c,'text':s} for c,s in points]})
            q['marks']=sum(p['marks'] for p in q['parts'])
        if diagram:q['diagramSvg']=diagram
        if worked:q['markSchemeDiagramSvg']=worked
        self.qs.append(q);self.ledger.append({'id':q['id'],'family':family or title,'syllabusCode':code,'level':level,'scopeNotes':notes})
        return q
    def check(self,label,expression,value):
        result=eval(expression,{'__builtins__':{}},{'sum':sum,'sqrt':math.sqrt,'log':math.log})
        assert math.isclose(result,value,rel_tol=1e-9,abs_tol=1e-9),(label,result,value)
        self.checks.append({'id':self.qs[-1]['id'],'quantity':label,'expression':expression,'unroundedResult':result})
    def save(self):
        assert len(self.qs)==192,len(self.qs)
        assert Counter(q['syllabusCode'] for q in self.qs)==Counter({k:16 for k in TOPICS})
        # Balance answer locations without changing the correct text or distractor set.
        mcqs=[q for q in self.qs if q['questionType']=='multiple-choice']
        targets=list('ABCD')*(len(mcqs)//4)+list('ABCD')[:len(mcqs)%4]
        random.Random('biology-theme-d-balanced-answer-key').shuffle(targets)
        for q,target in zip(mcqs,targets):
            correct=next(o['text'] for o in q['options'] if o['label']==q['correctOption'])
            wrong=[o['text'] for o in q['options'] if o['label']!=q['correctOption']]
            random.Random('biology-theme-d-distractors-'+q['id']).shuffle(wrong)
            wrong.insert('ABCD'.index(target),correct)
            q['options']=[{'label':label,'text':text} for label,text in zip('ABCD',wrong)]
            q['markScheme'][0]['steps'][0]['text']=target+'. '+q['markScheme'][0]['steps'][0]['text'].split('. ',1)[1]
            q['correctOption']=target
        # A plotted dataset is part of the input, even if two introductions match.
        inputs=[json.dumps([q['stem'],q['parts'],q.get('diagramSvg'),q.get('options')],sort_keys=True) for q in self.qs]
        assert len(set(inputs))==192
        assert max(Counter(q['family'] for q in self.ledger).values())<=4
        out=ROOT/'content/ib/biology/continuity-change.json';out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(self.qs,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        report={'theme':'D: Continuity and change','questions':192,'coverage':dict(Counter(q['syllabusCode'] for q in self.qs)),'levels':dict(Counter(q['level'] for q in self.qs)),'types':dict(Counter(q['questionType'] for q in self.qs)),'difficulty':dict(Counter(q['difficulty'] for q in self.qs)),'source':'https://xmltwo.ibo.org/publications/EAD/2026_EN/GR4/GR4-Biology_EN.pdf','numericChecks':self.checks,'ledger':self.ledger,'sha256':sha256(out.read_bytes()).hexdigest(),'reviewStatus':'Author checks complete; independent review to follow.'}
        path=ROOT/'docs/ib-biology-reviews/theme-d-author.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print(json.dumps({k:v for k,v in report.items() if k not in ('numericChecks','ledger')},indent=2))

def gel(lanes,title='Constructed DNA fragment results'):
    """Lanes contain (name, list of band positions in arbitrary migration units)."""
    body=txt(380,25,'DNA fragment separation',18)+arrow(48,95,48,305)+txt(50,340,'Direction of migration',14,anchor='start')
    for i,(name,bands) in enumerate(lanes):
        x=140+i*140
        body+=txt(x,60,name,15)+f'<rect x="{x-40}" y="85" width="80" height="220" fill="#eef4f7" stroke="#647a89"/>'+line(x-22,99,x+22,99,'#2d3d49',5)
        for y in bands:body+=line(x-24,115+y*1.4,x+24,115+y*1.4,'#425d96',6)
    body+=txt(380,380,'Illustrated bands; positions are arbitrary, not a calibrated size scale.',13)
    return SVG(body,title,760,405)

def feedback_diagram():
    return SVG(box(30,110,150,65,'Blood glucose\nrises')+arrow(187,142,250,142)+box(255,110,180,65,'Pancreatic beta\ncells')+arrow(442,142,510,142)+box(515,110,210,65,'Insulin release')+arrow(620,185,620,245)+box(390,250,335,65,'Cell uptake and\nglycogen synthesis')+arrow(375,282,180,282)+box(30,250,150,65,'Blood glucose\nfalls'),'Glucose control feedback schematic',760,350)

def label_points(diagram, values):
    """Expose exact measured values used in numerical graph questions."""
    points=re.findall(r'<circle cx="([^"]+)" cy="([^"]+)" r="4"',diagram)
    assert len(points)==len(values)
    labels=''.join(txt(float(x),float(y)-11,num(value),13,anchor='start' if i==0 else 'end' if i==len(values)-1 else 'middle') for i,((x,y),value) in enumerate(zip(points,values)))
    return diagram.replace('</svg>',labels+'</svg>')
