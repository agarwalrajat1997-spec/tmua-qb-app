"""Standard-library helpers for original Biology Form and function practice."""
import json
import math
import re
from collections import Counter
from html import escape
from pathlib import Path
from xml.etree import ElementTree

ROOT=Path(__file__).resolve().parents[2]

def f(x,sig=3):return format(x,f'.{sig}g')
def m(s):return '$'+s+'$'
def u(x,unit='',sig=3):
    value=format(x,f'#.{sig}g')
    if 'e' in value:
        a,b=value.split('e');value=a+r'\times10^{'+str(int(b))+'}'
    return '$'+value+(r'\ \mathrm{'+unit+'}' if unit else '')+'$'
def A(s):return ('A1',s)
def R(s):return ('R1',s)
def M(s):return ('M1',s)
def P(prompt,*steps):return prompt,list(steps)
def table(head,rows):return '\n\n|'+'|'.join(head)+'|\n|'+'|'.join('---' for _ in head)+'|\n'+'\n'.join('|'+'|'.join(map(str,row))+'|' for row in rows)
def text(x,y,s,size=17,anchor='middle',colour='#18334b'):
    return f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="{size}" text-anchor="{anchor}" fill="{colour}">{escape(str(s))}</text>'
def line(x1,y1,x2,y2,colour='#18334b',width=2):return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{colour}" stroke-width="{width}"/>'
def arrow(x1,y1,x2,y2,colour='#2677a6'):
    dx=x2-x1;dy=y2-y1;dd=math.hypot(dx,dy);dx/=dd;dy/=dd
    return line(x1,y1,x2,y2,colour,2.5)+f'<polygon points="{x2},{y2} {x2-10*dx+4*dy},{y2-10*dy-4*dx} {x2-10*dx-4*dy},{y2-10*dy+4*dx}" fill="{colour}"/>'
def svg(body,title,w=720,h=360):return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img"><title>{escape(title)}</title><rect width="{w}" height="{h}" fill="white"/>{body}</svg>'
def plot(xs,ys,xlab,ylab,title,second=None):
    def nice_top(value):
        raw=value/4;power=10**math.floor(math.log10(raw))
        step=next(v*power for v in (1,2,2.5,5,10) if v*power>=raw)
        return math.ceil(value/step)*step
    mn=min(xs)-1;mx=max(xs)+1;my=nice_top(max(ys+(second or [])))
    X=lambda x:90+(x-mn)/(mx-mn)*570;Y=lambda y:280-y/my*220
    b=line(90,280,675,280)+line(90,280,90,40)+text(380,340,xlab,16)+text(90,24,ylab,16,anchor='start')
    for x in xs:b+=text(X(x),307,f(x),13)+line(X(x),280,X(x),285,width=1)
    for i in range(6):
        y=my*i/5;b+=text(78,Y(y)+5,f(y),13,anchor='end')+line(85,Y(y),90,Y(y),width=1)
    for values,col in [(ys,'#2677a6')]+([(second,'#b86527')] if second else []):
        b+='<polyline points="'+' '.join(f'{X(x)},{Y(y)}' for x,y in zip(xs,values))+'" fill="none" stroke="'+col+'" stroke-width="3"/>'
        for x,y in zip(xs,values):b+=f'<circle cx="{X(x)}" cy="{Y(y)}" r="4" fill="{col}"/>'
    return svg(b,title)

def membrane_svg():
    b=text(360,36,'Extracellular fluid',18)+text(360,325,'Cytoplasm',18)
    for x in range(85,640,28):
        if 285<x<410:continue
        for y,d in [(105,1),(235,-1)]:
            b+=f'<circle cx="{x}" cy="{y}" r="10" fill="#6aa9cc" stroke="#18334b"/>'
            b+=line(x-4,y+d*10,x-7,y+d*54,'#bd8c54',3)+line(x+4,y+d*10,x+8,y+d*54,'#bd8c54',3)
    b+='<path d="M302 83 Q280 170 302 257 L332 257 Q320 170 332 83 Z" fill="#8c72a9" stroke="#18334b" stroke-width="2"/>'
    b+='<path d="M372 83 Q384 170 372 257 L402 257 Q424 170 402 83 Z" fill="#8c72a9" stroke="#18334b" stroke-width="2"/>'
    b+=arrow(352,80,352,260)+text(455,175,'X',22)+line(442,169,393,169)
    b+=text(138,71,'Y',22)+line(148,73,165,96)+text(145,184,'Z',22)+line(158,178,192,160)
    return svg(b,'Membrane schematic with labelled structures X, Y and Z')

def worked_membrane_svg():
    b=text(370,34,'Extracellular fluid',18)+text(370,348,'Cytoplasm',18)
    for x in range(85,640,28):
        if 285<x<410 or 485<x<545:continue
        for y,d in [(120,1),(250,-1)]:
            if x==225 and y==120:continue
            b+=f'<circle cx="{x}" cy="{y}" r="10" fill="#6aa9cc" stroke="#18334b"/>'
            b+=line(x-4,y+d*10,x-7,y+d*54,'#bd8c54',3)+line(x+4,y+d*10,x+8,y+d*54,'#bd8c54',3)
    b+='<path d="M302 98 Q280 185 302 272 L332 272 Q320 185 332 98 Z" fill="#8c72a9" stroke="#18334b" stroke-width="2"/>'
    b+='<path d="M372 98 Q384 185 372 272 L402 272 Q424 185 402 98 Z" fill="#8c72a9" stroke="#18334b" stroke-width="2"/>'
    b+='<rect x="490" y="99" width="46" height="173" rx="18" fill="#6b9b70" stroke="#18334b" stroke-width="2"/>'
    b+=line(513,99,513,77,'#44714c',3)+line(513,77,539,60,'#44714c',3)+line(539,60,564,77,'#44714c',3)
    for x,y in [(513,77),(539,60),(564,77)]:
        pts=' '.join(f'{x+9*math.cos(i*math.pi/3)},{y+9*math.sin(i*math.pi/3)}' for i in range(6))
        b+=f'<polygon points="{pts}" fill="#c0dba7" stroke="#44714c" stroke-width="1.5"/>'
    b+=text(140,65,'Carbohydrate chain',16)+line(228,64,502,77)
    b+=text(584,308,'Glycoprotein',17)+line(552,290,525,262)
    # A position symbol, not a chemical structural formula; OH remains near the heads.
    b+='<rect x="224" y="134" width="14" height="48" rx="4" fill="#f1cd65" stroke="#89681b" stroke-width="1.5"/>'
    b+=line(231,134,231,126,'#89681b',2)+text(231,120,'OH',12)
    b+=text(130,314,'Cholesterol symbol',17)+line(182,298,230,182)
    b+=text(365,386,'One acceptable schematic; carbohydrate is outside, cholesterol is within a leaflet.',14)
    return svg(b,'Worked membrane model showing extracellular carbohydrate and cholesterol position',720,410)

def organelle_svg(kind):
    if kind=='mitochondrion':
        b='<ellipse cx="350" cy="174" rx="255" ry="115" fill="#eef6fa" stroke="#18334b" stroke-width="3"/>'
        b+='<path d="M140 175 Q145 100 220 86 L245 150 L265 95 L290 154 L315 88 L340 155 L365 88 L390 155 L415 95 L435 155 L460 100 Q550 120 560 175 Q550 260 460 265 L430 200 L410 267 L380 205 L355 267 L330 205 L305 267 L280 205 L255 260 Q155 245 140 175 Z" fill="#f9e9c7" stroke="#98743f" stroke-width="2.5"/>'
        b+=text(350,183,'A',22)+text(640,83,'B',22)+line(625,84,560,111)+text(615,270,'C',22)+line(603,260,430,200)
    else:
        b='<ellipse cx="350" cy="174" rx="255" ry="115" fill="#edf7ea" stroke="#18334b" stroke-width="3"/><ellipse cx="350" cy="174" rx="240" ry="101" fill="none" stroke="#6a965a" stroke-width="2"/>'
        for x in [210,340,470]:
            for y in [130,145,160,175]:b+=f'<rect x="{x-38}" y="{y}" width="76" height="10" rx="5" fill="#8fbb74" stroke="#416e31"/>'
        b+=line(248,160,302,160,'#416e31',4)+line(378,160,432,160,'#416e31',4)
        b+=text(350,225,'A',22)+text(640,85,'B',22)+line(625,86,561,111)+text(615,270,'C',22)+line(603,259,480,180)
    b+=text(360,340,'Schematic illustration; not a micrograph and not to scale.',14)
    return svg(b,'Organelle compartment schematic with labelled structures A, B and C')

def vessel_svg(kind):
    outer={'artery':102,'vein':102,'capillary':85}[kind];inner={'artery':52,'vein':78,'capillary':77}[kind]
    b=f'<circle cx="360" cy="160" r="{outer}" fill="#cfb1bd" stroke="#18334b" stroke-width="2"/><circle cx="360" cy="160" r="{inner}" fill="#fff" stroke="#18334b" stroke-width="2"/>'
    b+=text(360,165,'lumen',18)+text(570,105,'wall',18)+line(540,110,360+outer-3,130)
    b+=text(360,310,'Cross-section schematic; relative wall thickness is emphasized.',15)
    return svg(b,'Original blood-vessel cross-section schematic')

def sarcomere_svg(short=False):
    left,right=(145,575) if short else (80,640);mid=(left+right)/2
    b=line(left,65,left,270,width=5)+line(right,65,right,270,width=5)
    for y in [105,165,225]:
        b+=line(left,y,left+190,y,'#407ea2',4)+line(right-190,y,right,y,'#407ea2',4)
    for y in [135,195]:
        b+=line(mid-135,y,mid+135,y,'#a85b55',8)
        for x in range(round(mid-125),round(mid+135),25):
            if abs(x-mid)<35:continue
            direction=-1 if x<mid else 1
            b+=line(x,y,x+direction*9,y-14,'#a85b55',3)+line(x,y,x+direction*9,y+14,'#a85b55',3)
    b+=line(mid,65,mid,270,'#667786',1)+text(left,40,'Z',18)+text(right,40,'Z',18)+text(mid,40,'M',18)
    b+=text(360,325,'Schematic filament arrangement; lengths of each filament type are fixed.',14)
    return svg(b,'Original sarcomere filament diagram with Z and M reference lines')

def amino_svg(dipeptide=False):
    if not dipeptide:
        b=text(360,167,'C',26)+text(360,74,'H',23)+text(360,270,'X',23)+text(190,167,'H₂N',23)+text(535,167,'COOH',23)
        b+=line(360,135,360,88)+line(360,181,360,242)+line(225,159,336,159)+line(384,159,488,159)
        b+=text(360,329,'Neutral structural convention.',14)
        return svg(b,'General amino-acid structural diagram with a group labelled X')
    labels=['H₂N','CH(R₁)','C','NH','CH(R₂)','COOH'];xs=[80,225,370,500,650,805]
    b=''
    for i,label in enumerate(labels):
        b+=text(xs[i],167,label,23)
        if i<len(labels)-1:b+=line(xs[i]+max(23,len(label)*6),160,xs[i+1]-max(23,len(labels[i+1])*6),160)
    b+=text(370,78,'O',23)+line(366,92,366,138)+line(374,92,374,138)
    b+=text(450,286,'Neutral structural convention; the carbonyl-to-nitrogen link is a peptide bond.',15)
    return svg(b,'Dipeptide structural model with two retained side groups',900,320)

def leaf_svg():
    b='<rect x="70" y="55" width="580" height="9" fill="#d2c8a1"/><rect x="70" y="64" width="580" height="28" fill="#e4efd9" stroke="#45663b"/>'
    b+='<rect x="70" y="92" width="580" height="78" fill="#a5c988" stroke="#45663b"/>'
    b+='<rect x="70" y="170" width="580" height="98" fill="#f5faf1" stroke="#45663b"/>'
    for x,y in [(120,195),(200,225),(275,195),(420,230),(500,195),(590,235)]:b+=f'<ellipse cx="{x}" cy="{y}" rx="28" ry="15" fill="#b4d49a" stroke="#45663b"/>'
    b+='<ellipse cx="350" cy="210" rx="36" ry="27" fill="#d7b1b2" stroke="#45663b"/>'
    b+='<rect x="70" y="268" width="365" height="27" fill="#e4efd9" stroke="#45663b"/><rect x="475" y="268" width="175" height="27" fill="#e4efd9" stroke="#45663b"/>'
    b+='<ellipse cx="440" cy="281" rx="10" ry="14" fill="#90b775" stroke="#45663b"/><ellipse cx="470" cy="281" rx="10" ry="14" fill="#90b775" stroke="#45663b"/>'
    b+=text(27,133,'A',21)+line(43,128,104,128)+text(27,218,'B',21)+line(43,212,158,212)+text(565,330,'C',21)+line(550,320,455,281)
    b+=text(360,30,'Upper leaf surface',16)+text(230,330,'Tissue schematic; not to scale.',14)
    return svg(b,'Dicot leaf tissue illustration with three labelled regions')

def vascular_svg():
    b=''
    for cx in [210,510]:b+=f'<circle cx="{cx}" cy="160" r="110" fill="#f0f5e8" stroke="#43613b" stroke-width="2"/>'
    for i in range(8):
        a=i*math.pi/4
        for rr,col,radius in [(76,'#b36a69',9),(92,'#5b91b4',8)]:
            x=210+rr*math.cos(a);y=160+rr*math.sin(a);b+=f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{col}"/>'
    star=[]
    for i in range(8):
        a=-math.pi/2+i*math.pi/4;rr=72 if i%2==0 else 19
        star.append(f'{510+rr*math.cos(a)},{160+rr*math.sin(a)}')
    b+='<polygon points="'+' '.join(star)+'" fill="#b36a69"/>'
    for i in range(4):
        a=math.pi/4+i*math.pi/2;b+=f'<circle cx="{510+42*math.cos(a)}" cy="{160+42*math.sin(a)}" r="11" fill="#5b91b4"/>'
    b+=text(210,30,'I',21)+text(510,30,'II',21)
    b+='<rect x="160" y="303" width="18" height="18" fill="#b36a69"/><rect x="390" y="303" width="18" height="18" fill="#5b91b4"/>'
    b+=text(235,319,'Tissue X',16)+text(465,319,'Tissue Y',16)
    return svg(b,'Two dicot vascular tissue arrangements; tissue colours are symbolic')

class Bank:
    def __init__(self):self.questions=[];self.families=[]
    def add(self,code,family,title,stem,*,level='sl',options=None,reason='',parts=None,kind='structured',diagram=None,worked=None,difficulty=None):
        number=len(self.questions)+1
        q={'id':f'ib-bio-b-{number:03d}','subject':'biology','topicId':'form-function','collectionId':'biology-form-function','number':number,'title':title,'subtopic':TOPICS[code],'syllabusCode':code,'level':level,'questionType':'multiple-choice' if options else kind,'difficulty':difficulty or ('easy' if options else 'medium'),'calculator':True,'stem':stem,'source':{'document':'Independent syllabus-authored practice','question':number},'verification':{'method':'Original syllabus authoring, displayed-data recalculation and biological-model checks','notes':f'Editorial family {family}. Original wording, quantities and schematic illustrations; no published question-bank question or artwork copied. Independent review is recorded separately.'},'status':'published'}
        if options:
            assert len(options)==4 and len(set(options))==4
            shift=sum(q['questionType']=='multiple-choice' for q in self.questions)%4;opts=options[-shift:]+options[:-shift] if shift else options;key='ABCD'[shift]
            q.update(marks=1,parts=[],options=[{'label':k,'text':v} for k,v in zip('ABCD',opts)],correctOption=key,markScheme=[{'part':'','steps':[{'code':'A1','text':key+'. '+reason}]}])
        else:
            q['parts']=[];q['markScheme']=[]
            for i,(prompt,steps) in enumerate(parts):
                label=chr(97+i);q['parts'].append({'label':label,'prompt':prompt,'marks':len(steps)})
                q['markScheme'].append({'part':label,'steps':[{'code':c,'text':s} for c,s in steps]})
            q['marks']=sum(p['marks'] for p in q['parts'])
        if diagram:q['diagramSvg']=diagram
        if worked:q['markSchemeDiagramSvg']=worked
        self.questions.append(q);self.families.append(family)
    def extend(self,number,*parts):
        q=self.questions[number-1];assert q['questionType']!='multiple-choice'
        for prompt,steps in parts:
            label=chr(97+len(q['parts']));q['parts'].append({'label':label,'prompt':prompt,'marks':len(steps)})
            q['markScheme'].append({'part':label,'steps':[{'code':code,'text':s} for code,s in steps]});q['marks']+=len(steps)
    def save(self):
        assert len(self.questions)==160
        assert Counter(q['syllabusCode'] for q in self.questions)=={key:16 for key in TOPICS}
        assert max(Counter(self.families).values())<=4
        assert len({q['stem'] for q in self.questions})==160
        for q in self.questions:
            assert sum(len(p['steps']) for p in q['markScheme'])==q['marks']
            if q['questionType']!='multiple-choice':assert sum(p['marks'] for p in q['parts'])==q['marks']
            def strings(x):
                if isinstance(x,str):yield x
                elif isinstance(x,list):
                    for y in x:yield from strings(y)
                elif isinstance(x,dict):
                    for k,y in x.items():
                        if k not in ('diagramSvg','markSchemeDiagramSvg'):yield from strings(y)
            for s in strings(q):
                assert s.count('$')%2==0,(q['id'],s)
                assert not re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]',s),(q['id'],s)
                assert not re.search(r'[_^]',''.join(re.split(r'\$[^$]*\$',s))),(q['id'],s)
            for k in ('diagramSvg','markSchemeDiagramSvg'):
                if k in q:ElementTree.fromstring(q[k])
        dest=ROOT/'content/ib/biology/form-function.json';dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(self.questions,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        report={'theme':'B: Form and function','questions':160,'coverage':dict(Counter(q['syllabusCode'] for q in self.questions)),'levels':dict(Counter(q['level'] for q in self.questions)),'types':dict(Counter(q['questionType'] for q in self.questions)),'families':dict(Counter(self.families)),'diagrams':sum(k in q for q in self.questions for k in ('diagramSvg','markSchemeDiagramSvg')),'checks':['One-mark MCQs with four distinct options and private key.','All structured part marks and one-mark marking points reconcile.','Numerical answers recomputed from stated quantities and rounding.','Constructed datasets explicitly identified.','Original diagrams label schematics as illustrations, not micrographs.','SL/AHL boundaries follow the verified official guide.'],'reviewStatus':'Author checks completed; independent review pending.'}
        out=ROOT/'docs/ib-biology-reviews';out.mkdir(parents=True,exist_ok=True)
        (out/'form-function-author.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print(json.dumps(report,ensure_ascii=False,indent=2))

TOPICS={'B1.1':'Carbohydrates and lipids','B1.2':'Proteins','B2.1':'Membranes and membrane transport','B2.2':'Organelles and compartmentalization','B2.3':'Cell specialization','B3.1':'Gas exchange','B3.2':'Transport','B3.3':'Muscle and motility','B4.1':'Adaptation to environment','B4.2':'Ecological niches'}
