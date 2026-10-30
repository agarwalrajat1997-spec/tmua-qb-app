"""Original Biology Theme C authoring utilities, isolated from the other banks."""
from collections import Counter
from hashlib import sha256
from html import escape
from pathlib import Path
from xml.etree import ElementTree
import json
import math
import random
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = 'https://xmltwo.ibo.org/publications/EAD/2026_EN/GR4/GR4-Biology_EN.pdf'
TOPICS = {
 'C1.1':'Enzymes and metabolism', 'C1.2':'Cell respiration', 'C1.3':'Photosynthesis',
 'C2.1':'Chemical signalling', 'C2.2':'Neural signalling',
 'C3.1':'Integration of body systems', 'C3.2':'Defence against disease',
 'C4.1':'Populations and communities', 'C4.2':'Transfers of energy and matter',
}
SL_LAST = {'C1.1':10,'C1.2':6,'C1.3':8,'C2.1':0,'C2.2':7,'C3.1':16,'C3.2':18,'C4.1':18,'C4.2':22}

def P(prompt, *points): return (prompt, list(points))
def A(s): return ('A1', s)
def R(s): return ('R1', s)
def M(s): return ('M1', s)
def T(headers, rows):
    return '\n\n|'+'|'.join(headers)+'|\n|'+'|'.join('---' for _ in headers)+'|\n'+'\n'.join('|'+'|'.join(map(str,row))+'|' for row in rows)
def num(x, sf=3):
    s=format(x,f'.{sf}g')
    return s
def txt(x,y,s,size=16,anchor='middle',colour='#18324b'):
    return f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="{size}" text-anchor="{anchor}" fill="{colour}">{escape(str(s))}</text>'
def line(x1,y1,x2,y2,colour='#18324b',width=2,dash=None):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{colour}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>'
def arrow(x1,y1,x2,y2,colour='#18324b',width=2):
    theta=math.atan2(y2-y1,x2-x1);d=9
    return line(x1,y1,x2,y2,colour,width)+line(x2,y2,x2-d*math.cos(theta-.45),y2-d*math.sin(theta-.45),colour,width)+line(x2,y2,x2-d*math.cos(theta+.45),y2-d*math.sin(theta+.45),colour,width)
def box(x,y,w,h,label,colour='#edf4f8'):
    labels=label.split('\n')
    size=min(16,(w-16)/(max(1,max(map(len,labels),default=1))*.55))
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{colour}" stroke="#527188" stroke-width="1.7"/>'+''.join(txt(x+w/2,y+h/2+(i-(len(labels)-1)/2)*22+5,s,size) for i,s in enumerate(labels))
def SVG(body,title,w=760,h=390):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img"><title>{escape(title)}</title><rect width="{w}" height="{h}" fill="#ffffff"/>{body}</svg>'
def graph(xs,series,xlabel,ylabel,title,*,xlim=None,ylim=None,xticks=None,yticks=None,note='Constructed data; lines connect plotted means.',w=760,h=420):
    """Series are (legend, y values, colour), with exact, labelled tick scales."""
    xmin,xmax=xlim or (min(0,min(xs)),max(xs))
    ymin,ymax=ylim or (0,max(y for _,ys,_ in series for y in ys)*1.1)
    X=lambda x:90+(x-xmin)/(xmax-xmin)*(w-140)
    Y=lambda y:h-105-(y-ymin)/(ymax-ymin)*(h-190)
    body=txt(90,26,ylabel,16,anchor='start')
    for x in xticks if xticks is not None else [xmin+(xmax-xmin)*i/4 for i in range(5)]:
        body+=line(X(x),Y(ymin),X(x),Y(ymin)+5)+txt(X(x),Y(ymin)+25,num(x),13)
    for y in yticks if yticks is not None else [ymin+(ymax-ymin)*i/4 for i in range(5)]:
        body+=line(85,Y(y),X(xmax),Y(y),'#e0e8ed',1)+txt(76,Y(y)+5,num(y),13,anchor='end')
    body+=line(90,Y(ymax),90,Y(ymin))+line(90,Y(ymin),X(xmax),Y(ymin))
    for i,(label,ys,colour) in enumerate(series):
        assert len(xs)==len(ys)
        body+='<polyline points="'+' '.join(f'{X(x):.3f},{Y(y):.3f}' for x,y in zip(xs,ys))+'" fill="none" stroke="'+colour+'" stroke-width="2.7"/>'
        for x,y in zip(xs,ys): body+=f'<circle cx="{X(x)}" cy="{Y(y)}" r="4" fill="{colour}"/>'
        lx=110+i*230
        body+=line(lx,53,lx+24,53,colour,3)+txt(lx+32,58,label,14,anchor='start')
    body+=txt(w/2,h-48,xlabel,16)+txt(w/2,h-16,note,13)
    return SVG(body,title,w,h)
def pathway(nodes,labels=None,title='Constructed pathway model',feedback=None):
    """Max four compact nodes; arrow enzyme labels do not state the requested inference."""
    n=len(nodes);w=760;bw=125;gap=(w-80-n*bw)/(n-1);y=145
    body=''
    for i,node in enumerate(nodes):
        x=40+i*(bw+gap);body+=box(x,y,bw,70,node)
        if i<n-1:
            body+=arrow(x+bw+5,y+35,x+bw+gap-7,y+35)
            if labels:body+=txt(x+bw+gap/2,y+82 if feedback and i==0 else y+14,labels[i],14)
    if feedback:
        body+=line(w-40-bw/2,y-8,w-40-bw/2,75,'#a04f3f')+line(w-40-bw/2,75,40+bw+gap/2,75,'#a04f3f')+line(40+bw+gap/2,75,40+bw+gap/2,y+20,'#a04f3f')+line(40+bw+gap/2-9,y+20,40+bw+gap/2+9,y+20,'#a04f3f',3)
        body+=txt(380,55,feedback,15)
    return SVG(body,title,760,300)

def phagocytosis_svg():
    """Cell boundaries distinguish an external particle from an enclosed vesicle."""
    body=''
    # The indentation is extracellular; membrane arms extend around its bacterium.
    body+='<path d="M185 130 C160 85 85 85 50 135 C10 205 70 265 130 250 C160 245 180 230 190 200 L165 195 C145 220 120 205 120 175 C120 145 145 135 165 150 Z" fill="#e8f1f6" stroke="#416b84" stroke-width="3"/>'
    body+='<ellipse cx="80" cy="190" rx="20" ry="25" fill="#aacbdd" stroke="#416b84"/>'
    body+='<rect x="153" y="162" width="32" height="19" rx="9" fill="#d39553" stroke="#805326" stroke-width="2"/>'
    body+=txt(120,42,'1. Membrane surrounds particle',15)+txt(167,95,'Bacterium',14)+arrow(169,102,169,155)
    body+=arrow(220,175,280,175)
    # Enclosed phagosome is separated from cytoplasm by its own membrane.
    body+='<circle cx="385" cy="175" r="78" fill="#e8f1f6" stroke="#416b84" stroke-width="3"/><ellipse cx="350" cy="207" rx="20" ry="25" fill="#aacbdd" stroke="#416b84"/><circle cx="416" cy="177" r="29" fill="#ffffff" stroke="#416b84" stroke-width="2"/><rect x="400" y="168" width="32" height="19" rx="9" fill="#d39553" stroke="#805326" stroke-width="2"/><circle cx="376" cy="128" r="13" fill="#d9c3df" stroke="#775185" stroke-width="2"/>'
    body+=txt(385,42,'2. Particle inside a vesicle',15)+txt(385,295,'Lysosome',14)+arrow(384,278,377,144)+txt(470,242,'Vesicle',14)+arrow(467,226,439,198)
    body+=arrow(490,175,550,175)
    # A larger digestive vesicle contains fragments and enzymes after fusion.
    body+='<circle cx="655" cy="175" r="78" fill="#e8f1f6" stroke="#416b84" stroke-width="3"/><ellipse cx="619" cy="207" rx="20" ry="25" fill="#aacbdd" stroke="#416b84"/><circle cx="681" cy="170" r="35" fill="#f2e7f4" stroke="#775185" stroke-width="2"/>'
    for x,y in [(664,151),(694,147),(704,174),(665,191),(690,193)]:body+=f'<circle cx="{x}" cy="{y}" r="3.5" fill="#775185"/>'
    for x,y in [(670,169),(684,160),(689,180)]:body+=line(x,y,x+8,y+5,'#b66a30',4)
    body+=txt(655,42,'3. Lysosome fusion and digestion',15)+txt(655,295,'Enzymes act within the vesicle',14)
    body+=txt(380,350,'Original schematic sequence; organelle sizes are not to scale.',14)
    return SVG(body,'Original phagocyte sequence showing engulfment, an enclosed vesicle and lysosomal digestion',780,380)

class Bank:
    def __init__(self):
        self.qs=[]; self.ledger=[]; self.calcs=[]
        self.option_slots=[0]*6+[1]*6+[2]*5+[3]*5
        rng=random.Random(20261030)
        rng.shuffle(self.option_slots)
        while any(self.option_slots[i]==self.option_slots[i+1]==self.option_slots[i+2] for i in range(20)):
            rng.shuffle(self.option_slots)
    def add(self,code,title,stem,*,refs,parts=None,options=None,reason='',kind='structured',difficulty='medium',diagram=None,worked=None,family=None,notes=''):
        n=len(self.qs)+1
        level='ahl' if any(int(s)>SL_LAST[code] for s in refs) else 'sl'
        q={'id':f'ib-bio-c-{n:03d}','subject':'biology','topicId':'interaction-interdependence','collectionId':'biology-interaction-interdependence','number':n,'title':title,'subtopic':TOPICS[code],'syllabusCode':code,'level':level,'questionType':'multiple-choice' if options else kind,'difficulty':difficulty,'calculator':True,'stem':stem,'source':{'document':'Independent syllabus-authored practice','question':n},'verification':{'method':'Original syllabus-linked authoring with explicit mark reconciliation and displayed-data calculations','notes':f'Guide statements: '+', '.join(code+'.'+str(r) for r in refs)+'. '+notes+' Original text, constructed data and self-drawn schematic artwork; no licensed question bank adapted.'},'status':'published'}
        if options:
            assert len(options)==4 and len(set(options))==4
            shift=self.option_slots[sum(q['questionType']=='multiple-choice' for q in self.qs)]
            vals=options[-shift:]+options[:-shift] if shift else options[:];key='ABCD'[shift]
            q.update(marks=1,parts=[],options=[{'label':k,'text':v} for k,v in zip('ABCD',vals)],correctOption=key,markScheme=[{'part':'','steps':[{'code':'A1','text':key+'. '+reason}]}])
        else:
            assert parts
            q['parts']=[];q['markScheme']=[]
            for i,(prompt,points) in enumerate(parts):
                assert points
                label=chr(97+i)
                q['parts'].append({'label':label,'prompt':prompt,'marks':len(points)})
                q['markScheme'].append({'part':label,'steps':[{'code':c,'text':s} for c,s in points]})
            q['marks']=sum(p['marks'] for p in q['parts'])
        if diagram:q['diagramSvg']=diagram
        if worked:q['markSchemeDiagramSvg']=worked
        self.qs.append(q)
        self.ledger.append({'id':q['id'],'syllabusCode':code,'statements':[code+'.'+str(x) for x in refs],'level':level,'family':family or title,'editorialChecks':['question and accepted responses reconciled','distinct positive marking points','scope and difficulty considered separately']})
        return q
    def calc(self,label,expression,result,units='',tolerance=1e-8):
        """Record a reproducible numerical check immediately after its owning question."""
        actual=eval(expression,{'__builtins__':{}},{'sum':sum,'sqrt':math.sqrt,'log':math.log,'exp':math.exp})
        assert math.isclose(actual,result,rel_tol=tolerance,abs_tol=tolerance),(label,actual,result)
        self.calcs.append({'id':self.qs[-1]['id'],'quantity':label,'displayedDataExpression':expression,'unroundedResult':actual,'units':units})
    def save(self):
        assert len(self.qs)==144,len(self.qs)
        assert Counter(q['syllabusCode'] for q in self.qs)==Counter({k:16 for k in TOPICS})
        assert max(Counter(x['family'] for x in self.ledger).values())<=4
        assert len({q['stem'] for q in self.qs})==144
        for q in self.qs:
            assert sum(int(p['code'][1:]) for g in q['markScheme'] for p in g['steps'])==q['marks']
            for p,g in zip(q['parts'],q['markScheme']):assert p['label']==g['part'] and p['marks']==sum(int(s['code'][1:]) for s in g['steps'])
            for key in ('diagramSvg','markSchemeDiagramSvg'):
                if key in q:
                    ElementTree.fromstring(q[key]);assert 'viewBox=' in q[key]
                    assert not re.search(r'<(?:script|style|image|foreignObject|animate|set)\b|\bon\w+=|(?:href|src)=|url\(',q[key],re.I)
            for s in [q['stem']]+[p['prompt'] for p in q['parts']]+[s['text'] for g in q['markScheme'] for s in g['steps']]:
                assert s.count('$')%2==0,(q['id'],s)
                assert not re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]',s)
        out=ROOT/'content/ib/biology/interaction-interdependence.json';out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(self.qs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        report={'theme':'C: Interaction and interdependence','source':SOURCE,'sourceEdition':'March 2024 corrected guide, first assessment 2025','count':144,'coverage':dict(Counter(q['syllabusCode'] for q in self.qs)),'levels':dict(Counter(q['level'] for q in self.qs)),'types':dict(Counter(q['questionType'] for q in self.qs)),'difficulty':dict(Counter(q['difficulty'] for q in self.qs)),'diagramFields':sum(k in q for q in self.qs for k in ('diagramSvg','markSchemeDiagramSvg')),'distinctFamilies':len(set(x['family'] for x in self.ledger)),'maxParameterizedVariants':max(Counter(x['family'] for x in self.ledger).values()),'numericChecks':self.calcs,'ledger':self.ledger,'questionJsonSha256':sha256(out.read_bytes()).hexdigest(),'reviewStatus':'Author checks complete. Independent review is pending; rendered author inspection is recorded separately.'}
        rd=ROOT/'docs/ib-biology-reviews';rd.mkdir(parents=True,exist_ok=True)
        (rd/'theme-c-author.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:v for k,v in report.items() if k not in ('ledger','numericChecks')},indent=2))
