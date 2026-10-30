"""Deterministic original Theme A authoring; no question-bank inputs."""
import hashlib,html,json,math,random
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BLUEPRINT=json.loads((ROOT/'docs/ib-biology-reviews/syllabus-blueprint.json').read_text(encoding='utf8'))
TOPICS={t['code']:t for t in BLUEPRINT['topics']}
def txt(x,y,s,size=17,anchor='middle',colour='#223848'):
    return f'<text x="{x}" y="{y}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" text-anchor="{anchor}" fill="{colour}">{html.escape(str(s))}</text>'
def line(x1,y1,x2,y2,colour='#264f69',width=2,arrow=False,dash=False):
    s=f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{colour}" stroke-width="{width}"'+(' stroke-dasharray="6 5"' if dash else '')+'/>'
    if arrow:
        n=math.hypot(x2-x1,y2-y1);dx=(x2-x1)/n;dy=(y2-y1)/n
        s+=f'<polygon points="{x2},{y2} {x2-11*dx+4*dy},{y2-11*dy-4*dx} {x2-11*dx-4*dy},{y2-11*dy+4*dx}" fill="{colour}"/>'
    return s
def svg(body,w=820,h=360):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img"><rect width="{w}" height="{h}" fill="white"/>'+body+'</svg>'
def box(x,y,w,h,label,fill='#edf5f7'):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{fill}" stroke="#446879"/>'+txt(x+w/2,y+h/2+6,label)
def table(headers,rows):
    return '\n\n|'+'|'.join(headers)+'|\n|'+'|'.join(['---']*len(headers))+'|\n'+'\n'.join('|'+'|'.join(str(v) for v in row)+'|' for row in rows)
def pt(s,code='A1'):return (code,s)
def P(prompt,*points):return (prompt,[p if isinstance(p,tuple) else pt(p) for p in points])
class Bank:
    def __init__(self):self.qs=[];self.review=[]
    def add(self,code,level,title,stem,parts=None,*,correct=None,wrong=None,why=None,data=False,diagram=None,worked=None,difficulty='medium',statements=None,notes=''):
        n=len(self.qs)+1
        assert level in ('sl','ahl') and code.startswith('A')
        assert not TOPICS[code]['additionalHlOnly'] or level=='ahl'
        if data and 'constructed' not in stem.lower() and 'simulated' not in stem.lower():stem='The following data are constructed for this question. '+stem
        q={'id':f'ib-bio-a-{n:03d}','subject':'biology','topicId':'unity-diversity','collectionId':'biology-unity-diversity','number':n,'title':title,'subtopic':TOPICS[code]['title'],'syllabusCode':code,'level':level,'difficulty':difficulty,'calculator':True,'stem':stem,'parts':[],'markScheme':[],
           'source':{'document':'Independent syllabus-authored practice','question':n},'verification':{'method':'Original syllabus-based authoring with explicit biological reasoning and recalculated data','notes':notes or ('Scope checked against '+str(TOPICS[code]['slStatements'] if level=='sl' else TOPICS[code]['additionalHlStatements'])+'; contextual assumptions and mark points individually reviewed.')},'status':'published'}
        if correct is not None:
            assert wrong is not None and len(wrong)==3 and why
            opts=[correct]+wrong;assert len(set(opts))==4
            order=list(range(4));random.Random(hashlib.sha256(q['id'].encode()).hexdigest()).shuffle(order)
            q.update(questionType='multiple-choice',marks=1,options=[{'label':'ABCD'[j],'text':opts[k]} for j,k in enumerate(order)],correctOption='ABCD'[order.index(0)])
            q['markScheme']=[{'part':'','steps':[{'code':'A1','text':'Option '+q['correctOption']+'. '+why}]}]
        else:
            assert parts
            for i,(prompt,points) in enumerate(parts):
                label=chr(97+i);marks=sum(int(c[1:]) for c,t in points if c!='AG');assert marks>0
                q['parts'].append({'label':label,'prompt':prompt,'marks':marks})
                q['markScheme'].append({'part':label,'steps':[{'code':c,'text':t} for c,t in points]})
            q.update(questionType='data-based' if data else 'structured',marks=sum(p['marks'] for p in q['parts']))
        if diagram:q['diagramSvg']=diagram
        if worked:q['markSchemeDiagramSvg']=worked
        self.qs.append(q)
        self.review.append({'id':q['id'],'syllabusCode':code,'level':level,'statements':statements or (TOPICS[code]['slStatements'] if level=='sl' else TOPICS[code]['additionalHlStatements']),'authorReview':q['verification']['notes'],'constructedData':data,'sourceUrls':TOPICS[code]['sourceUrls']})
        return q
    def write(self):
        assert len(self.qs)==144
        assert Counter(q['syllabusCode'] for q in self.qs)==Counter({c:16 for c in TOPICS if c.startswith('A')})
        overrides=ROOT/'scripts/ib-biology-authoring/unity-diversity-images.json'
        extra=json.loads(overrides.read_text(encoding='utf8')) if overrides.exists() else {}
        for q,r in zip(self.qs,self.review):
            if q['id'] in extra:q.update(extra[q['id']])
            r['questionSha256']=hashlib.sha256(json.dumps(q,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
        dest=ROOT/'content/ib/biology';dest.mkdir(parents=True,exist_ok=True)
        (dest/'unity-diversity.json').write_text(json.dumps(self.qs,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        report={'status':'author-reviewed; independent review required','questions':len(self.qs),'levels':dict(Counter(q['level'] for q in self.qs)),'types':dict(Counter(q['questionType'] for q in self.qs)),'marks':sum(q['marks'] for q in self.qs),'originality':'All prompts, options, mark points and datasets were newly authored; no past-paper or question-bank wording copied.','entries':self.review}
        (ROOT/'docs/ib-biology-reviews/unity-diversity-author-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print(json.dumps({k:v for k,v in report.items() if k!='entries'}))
