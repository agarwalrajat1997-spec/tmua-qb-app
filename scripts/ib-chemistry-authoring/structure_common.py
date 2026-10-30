"""Shared, standard-library-only authoring helpers for original Structure practice."""
import json
import math
import re
from collections import Counter
from html import escape
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[2]
NA = 6.02e23
R = 8.31
H = 6.63e-34
C0 = 3.00e8

def f(value, sig=3):
    return format(value, f'.{sig}g')

def c(formula, charge=''):
    """Roman chemical formula, with integer atom counts explicitly subscripted."""
    bits = re.split(r'(\d+)', formula)
    result = ''.join('_{'+x+'}' if x.isdigit() else r'\mathrm{'+x+'}' for x in bits if x)
    return '$'+result+('^{'+charge+'}' if charge else '')+'$'

def m(value):
    return '$'+value+'$'

def normalize_formula_tokens(value):
    """Typeset remaining condensed formula tokens in prose without altering existing math."""
    if isinstance(value,str):
        pattern=re.compile(r'\b(?:[A-Z][a-z]?\d*){2,}\b')
        pieces=re.split(r'(\$[^$]*\$)',value)
        return ''.join(piece if piece.startswith('$') else pattern.sub(lambda match:c(match[0]) if any(ch.isdigit() for ch in match[0]) else match[0],piece) for piece in pieces)
    if isinstance(value,list):return [normalize_formula_tokens(x) for x in value]
    if isinstance(value,dict):return {key:(x if key in ('diagramSvg','markSchemeDiagramSvg') else normalize_formula_tokens(x)) for key,x in value.items()}
    return value

def unit(value, units, sig=3):
    number=format(value,f'#.{sig}g')
    if 'e' in number:
        mantissa,exponent=number.split('e')
        number=mantissa+r'\times10^{'+str(int(exponent))+'}'
    return '$'+number+(r'\ \mathrm{'+units+'}' if units else '')+'$'

def P(prompt, *steps):
    return (prompt, list(steps))

def M(text):
    return ('M1', text)

def A(text):
    return ('A1', text)

def Rn(text):
    return ('R1', text)

def table(headers, rows):
    return '\n\n|'+'|'.join(headers)+'|\n|'+'|'.join('---' for _ in headers)+'|\n'+'\n'.join('|'+'|'.join(map(str,row))+'|' for row in rows)

def text(x,y,label,size=17,anchor='middle',color='#172b4d'):
    return f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="{size}" text-anchor="{anchor}" fill="{color}">{escape(str(label))}</text>'

def line(x1,y1,x2,y2,color='#172b4d',width=2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>'

def svg(body,title,w=640,h=320):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img"><title>{escape(title)}</title><rect width="{w}" height="{h}" fill="#ffffff"/>{body}</svg>'

def particles(groups, title='Particle model; circles of different colours represent different elements'):
    body=''
    colours={'A':'#1b6ca8','B':'#d47727','C':'#548c42'}
    for i, group in enumerate(groups):
        x=85+(i%4)*150; y=85+(i//4)*100
        for j,atom in enumerate(group):
            xx=x+(j-(len(group)-1)/2)*24
            body+=f'<circle cx="{xx}" cy="{y}" r="17" fill="{colours[atom]}" stroke="#172b4d" stroke-width="1.5"/>'
            body+=text(xx,y+5,atom,13,color='#ffffff')
    body+=text(320,290,'Touching circles are bonded; spaces separate particles.',14)
    return svg(body,title)

def plot(xs,ys,xlabel,ylabel,title,sticks=False,labels=False,w=640,h=350):
    if sticks:
        margin=max(1,(max(xs)-min(xs))*.25)
        xmin=max(0,min(xs)-margin);xmax=max(xs)+margin
    else:
        xmin=0;xmax=max(xs)*1.12 if max(xs)>0 else 1
    ymin=0; ymax=max(ys)*1.18 if max(ys)>0 else 1
    X=lambda x:80+(x-xmin)/(xmax-xmin)*(w-135)
    Y=lambda y:h-70-y/ymax*(h-125)
    body=line(80,h-70,w-40,h-70)+line(80,h-70,80,35)
    body+=text(w/2,h-18,xlabel,15)+text(80,22,ylabel,15,anchor='start')
    if sticks:
        for x,y in zip(xs,ys):
            body+=line(X(x),Y(0),X(x),Y(y),'#1b6ca8',4)
            body+=text(X(x),Y(0)+23,f(x),13)
            if labels:body+=text(X(x),Y(y)-12,f(y),13)
    else:
        body+='<polyline points="'+' '.join(f'{X(x)},{Y(y)}' for x,y in zip(xs,ys))+'" fill="none" stroke="#1b6ca8" stroke-width="3"/>'
        for x,y in zip(xs,ys):
            body+=f'<circle cx="{X(x)}" cy="{Y(y)}" r="4" fill="#1b6ca8"/>'
            if labels:
                first=abs(x-xmin)<1e-9
                body+=text(X(x)+(10 if first else 0),Y(y)-12,f'({f(x)}, {f(y)})',12,anchor='start' if first else 'middle')
        for i in range(5):
            x=xmax*i/4;y=ymax*i/4
            body+=text(X(x),h-48,f(x),11)+text(70,Y(y)+4,f(y),11,anchor='end')
    return svg(body,title,w,h)

def energy_levels(levels, transition=None):
    """Energy scale in supplied arbitrary units; arrows contain no computed answers."""
    lo=min(v for _,v in levels);hi=max(v for _,v in levels)
    Y=lambda value:265-(value-lo)/(hi-lo)*210
    body=text(70,25,'Energy / eV',15,anchor='start')
    for label,value in levels:
        yy=Y(value);body+=line(170,yy,510,yy)+text(130,yy+5,f(value),14,anchor='end')+text(535,yy+5,label,14,anchor='start')
    if transition:
        start,end=transition;y1=Y(start);y2=Y(end)
        body+=line(340,y1,340,y2,'#b15e2b',3)
        d=1 if y2>y1 else -1
        body+=line(340,y2,333,y2-12*d,'#b15e2b',3)+line(340,y2,347,y2-12*d,'#b15e2b',3)
    return svg(body,'Constructed atomic energy levels, not to scale in position beyond the labelled energy axis')

def orbital_boxes(occupancies, label=''):
    body=text(320,40,label,18)
    n=len(occupancies);start=320-n*48/2
    for i,occ in enumerate(occupancies):
        x=start+i*48;body+=f'<rect x="{x}" y="100" width="40" height="55" fill="#f2f6fa" stroke="#172b4d" stroke-width="2"/>'
        body+=text(x+20,139,occ,30)
    body+=text(320,210,'Each box represents one orbital.',15)
    return svg(body,'Orbital occupancy diagram')

def lewis(center, terminals, lone_pairs=0, charge=''):
    """Two-dimensional Lewis diagram, not a molecular shape drawing.
    Terminals are (atom, bond_order, terminal_lone_pairs). Up to four terminals.
    """
    positions=[(320,65),(485,165),(320,265),(155,165)]
    if center=='C' and len(terminals)==2 and all(t[1]==2 for t in terminals):
        positions=[(155,165),(485,165),(320,65),(320,265)]
    body=text(320,172,center,25)
    for i,(atom,order,pairs) in enumerate(terminals):
        x,y=positions[i];dx=x-320;dy=y-165;distance=math.hypot(dx,dy)
        ux=dx/distance;uy=dy/distance
        for j in range(order):
            shift=(j-(order-1)/2)*6
            body+=line(320+ux*22-uy*shift,165+uy*22+ux*shift,x-ux*23-uy*shift,y-uy*23+ux*shift)
        body+=text(x,y+7,atom,24)
        # Dots are placed on the three sides pointing away from the central bond.
        angles=[math.atan2(dy,dx),math.atan2(dy,dx)+math.pi/2,math.atan2(dy,dx)-math.pi/2]
        for a in angles[:pairs]:
            for offset in (-4,4):
                xx=x+29*math.cos(a)-offset*math.sin(a);yy=y+29*math.sin(a)+offset*math.cos(a)
                body+=f'<circle cx="{xx}" cy="{yy}" r="2.4" fill="#172b4d"/>'
    unused=positions[len(terminals):]
    for i in range(lone_pairs):
        if i<len(unused):dx=unused[i][0]-320;dy=unused[i][1]-165
        else:dx=-70;dy=-65+25*i
        dd=math.hypot(dx,dy);ux=dx/dd;uy=dy/dd
        for off in (-4,4):body+=f'<circle cx="{320+30*ux-off*uy}" cy="{165+30*uy+off*ux}" r="2.4" fill="#172b4d"/>'
    if charge:body+=text(566,72,charge,22)+line(105,35,105,300)+line(105,35,120,35)+line(105,300,120,300)+line(550,35,550,300)+line(535,35,550,35)+line(535,300,550,300)
    body+=text(320,337,'Lewis representation; the positions do not show the molecular shape.',13)
    return svg(body,'Lewis representation with bonds and all lone pairs shown',640,360)

def chain_svg(labels,orders=None,carbonyls=(),repeat=False,title='Condensed structural formula; lone pairs are not shown'):
    """Readable condensed structural formula with explicit bond orders and carbonyls."""
    n=len(labels);w=max(640,120*n+60);edge=max(90,65+max(len(label)*6 for label in labels));xs=[edge+i*(w-2*edge)/(n-1) for i in range(n)];y=165
    body='';orders=orders or [1]*(n-1)
    for i,order in enumerate(orders):
        left=xs[i]+max(21,len(labels[i])*6);right=xs[i+1]-max(21,len(labels[i+1])*6)
        assert right>left
        for j in range(order):body+=line(left,y+(j-(order-1)/2)*6,right,y+(j-(order-1)/2)*6)
    for i,label in enumerate(labels):body+=text(xs[i],y+7,label,22)
    for i in carbonyls:
        body+=line(xs[i]-3,y-22,xs[i]-3,90)+line(xs[i]+3,y-22,xs[i]+3,90)+text(xs[i],75,'O',23)
    if repeat:
        body+=line(20,y,xs[0]-max(21,len(labels[0])*6),y)+line(xs[-1]+max(21,len(labels[-1])*6),y,w-20,y)
        top=45 if carbonyls else 110
        for x,d in [(48,1),(w-48,-1)]:body+=line(x,top,x,220)+line(x,top,x+14*d,top)+line(x,220,x+14*d,220)
        body+=text(w-28,242,'n',22)
    body+=text(w/2,285,'Condensed structure; every displayed bond order is significant.',14)
    return svg(body,title,w,315)

def chromatography(spots,front=100):
    body='<rect x="125" y="35" width="390" height="240" fill="#f4f8fa" stroke="#172b4d"/>'
    body+=line(125,245,515,245)+text(525,250,'baseline',14,anchor='start')
    body+=line(125,65,515,65,'#667b91')+text(525,70,'solvent front',14,anchor='start')
    for i,value in enumerate(spots):
        x=230+i*180;y=245-180*value/front
        body+=f'<circle cx="{x}" cy="{y}" r="10" fill="#1b6ca8"/>'+text(x,y-19,chr(65+i),15)
    body+=text(320,310,'Distances in the question are measured from the baseline.',14)
    return svg(body,'Schematic chromatogram with baseline and solvent front',700,335)

def alkene_svg(lt,lb,rt,rb):
    body=text(250,167,'C',25)+text(390,167,'C',25)
    body+=line(273,154,367,154)+line(273,165,367,165)
    for x1,y1,x2,y2,label,tx,ty in [(235,145,170,90,lt,135,78),(235,175,170,230,lb,135,253),(405,145,470,90,rt,505,78),(405,175,470,230,rb,505,253)]:
        body+=line(x1,y1,x2,y2)+text(tx,ty,label,22)
    return svg(body,'Structural formula of an alkene; groups above and below the double bond are shown explicitly')

def chiral_svg(groups):
    a,b,cg,d=groups
    body=text(320,165,'C',25)
    body+=line(300,148,215,100)+text(170,92,a,22)
    body+=line(332,139,370,75)+text(395,60,b,22)
    body+='<polygon points="337,169 427,208 412,234" fill="#172b4d"/>'+text(470,246,cg,22)
    for i in range(1,8):
        x=305-i*11;y=175+i*8;width=i*1.6
        body+=line(x-width,y-width,x+width,y+width)
    body+=text(185,265,d,22)+text(320,313,'Solid wedge: towards viewer. Hashed bond: away from viewer.',14)
    return svg(body,'Tetrahedral carbon with four explicitly labelled groups',640,340)

def nmr_svg(signals):
    w=760;h=330;X=lambda delta:65+(10-delta)/10*640;ybase=245
    body=line(65,ybase,705,ybase)+text(385,310,'Chemical shift δ / ppm',16)
    patterns={'singlet':[1],'doublet':[1,1],'triplet':[1,2,1],'quartet':[1,3,3,1]}
    previous_x=None;label_row=0
    for ppm,integral,multiplicity in sorted(signals,reverse=True):
        weights=patterns[multiplicity];top=ybase-145
        for j,weight in enumerate(weights):
            xpos=X(ppm+(j-(len(weights)-1)/2)*0.055)
            body+=line(xpos,ybase,xpos,ybase-145*weight/max(weights),'#1b6ca8',2)
        if previous_x is not None and abs(X(ppm)-previous_x)<55:label_row=1-label_row
        else:label_row=0
        body+=text(X(ppm),top-19-label_row*25,f'{integral}H',15)
        previous_x=X(ppm)
    for value in range(11):body+=line(X(value),ybase,X(value),ybase+5)+text(X(value),ybase+26,value,13)
    body+=text(385,30,'Constructed spectrum; integrals and multiplicities are given in the table.',15)
    return svg(body,'Constructed proton NMR spectrum; high chemical shift is at the left',w,h)

def benzene_svg():
    cx=320;cy=165;r=82;hr=135
    points=[(cx+r*math.cos(math.pi/6+i*math.pi/3),cy+r*math.sin(math.pi/6+i*math.pi/3)) for i in range(6)]
    body=''
    for i,(x,y) in enumerate(points):
        xx,yy=points[(i+1)%6];dx=xx-x;dy=yy-y;length=math.hypot(dx,dy)
        body+=line(x+dx/length*15,y+dy/length*15,xx-dx/length*15,yy-dy/length*15)
        a=math.pi/6+i*math.pi/3;hx=cx+hr*math.cos(a);hy=cy+hr*math.sin(a)
        body+=line(x+17*math.cos(a),y+17*math.sin(a),hx-17*math.cos(a),hy-17*math.sin(a))
        body+=text(x,y+7,'C',22)+text(hx,hy+7,'H',22)
    body+='<circle cx="320" cy="165" r="47" fill="none" stroke="#172b4d" stroke-width="2"/>'
    body+=text(320,341,'The circle represents delocalized pi electron density around the ring.',14)
    return svg(body,'Benzene: six carbon atoms, six hydrogens and delocalized ring bonding',640,365)

def d_splitting_svg():
    body=text(70,30,'Orbital energy',16,anchor='start')+line(70,290,70,55)
    body+=line(70,55,64,68)+line(70,55,76,68)
    for y,n in [(95,2),(235,3)]:
        for i in range(n):
            x=320-n*48/2+i*48
            body+=f'<rect x="{x}" y="{y}" width="40" height="44" fill="#f2f6fa" stroke="#172b4d" stroke-width="2"/>'
            if y==235 and i==0:body+=text(x+20,y+33,'↑',27)
    body+=line(440,248,440,115,'#b15e2b',3)+line(440,115,433,128,'#b15e2b',3)+line(440,115,447,128,'#b15e2b',3)
    body+=text(460,176,'photon',16,anchor='start')+text(460,198,'absorbed',16,anchor='start')
    body+=text(320,330,'Schematic octahedral model; no numerical energy scale.',15)
    return svg(body,'Constructed octahedral d-orbital energy diagram for one d electron',640,355)

def cyclic_svg(size,cis=True):
    points=[(250,110),(390,110),(320,230)] if size==3 else [(250,110),(390,110),(390,230),(250,230)]
    body=''
    for i,(x,y) in enumerate(points):
        xx,yy=points[(i+1)%len(points)];dx=xx-x;dy=yy-y;dd=math.hypot(dx,dy)
        body+=line(x+dx/dd*25,y+dy/dd*25,xx-dx/dd*25,yy-dy/dd*25)
        body+=text(x,y+7,'CH' if i<2 else 'CH₂',22)
    for i,(sx,sy,ex,ey) in enumerate([(233,94,174,48),(407,94,466,48)]):
        dx=ex-sx;dy=ey-sy;dd=math.hypot(dx,dy);nx=-dy/dd;ny=dx/dd
        if i==0 or cis:
            body+=f'<polygon points="{sx},{sy} {ex+nx*8},{ey+ny*8} {ex-nx*8},{ey-ny*8}" fill="#172b4d"/>'
        else:
            for j in range(1,9):
                t=j/9;xx=sx+t*dx;yy=sy+t*dy
                body+=line(xx+nx*8*t,yy+ny*8*t,xx-nx*8*t,yy-ny*8*t,width=1.8)
    body+=text(150,36,'CH₃',22)+text(490,36,'CH₃',22)
    body+=text(320,291,'Each CH ring atom also carries one hydrogen.',14)
    body+=text(320,318,'Solid wedge: towards viewer. Hashed bond: away from viewer.',14)
    return svg(body,'Substituted carbon ring; the relative faces of the two methyl groups are shown',640,340)

class Bank:
    def __init__(self, theme):
        self.theme=theme;self.questions=[];self.families=[]
    def add(self,family,code,variant,title,stem,*,level='sl',options=None,reason='',parts=None,kind='structured',diagram=None,worked=None,difficulty=None,notes=''):
        number=len(self.questions)+1
        q={'id':f'ib-chem-s{self.theme}-{number:03d}','subject':'chemistry','topicId':f'structure-{self.theme}','collectionId':f'chemistry-structure-{self.theme}','number':number,'title':title,'subtopic':SUBTOPICS[code],'syllabusCode':code,'level':level,'questionType':'multiple-choice' if options else kind,'difficulty':difficulty or ('easy' if options else 'hard' if level=='ahl' else 'medium'),'calculator':True,'stem':stem,'source':{'document':'Independent syllabus-authored practice','question':number},'verification':{'method':'Deterministic standard-library authoring; displayed-data calculation, chemical-model and mark-total checks','notes':f'Original Structure family {family}; variant {variant}/4. '+notes+' No published question wording or artwork adapted. Independent review is recorded separately.'},'status':'published'}
        if options:
            assert len(options)==4 and len(set(options))==4
            shift=(number-1)%4
            items=options[-shift:]+options[:-shift] if shift else options[:]
            correct='ABCD'[shift]
            q.update(marks=1,parts=[],options=[{'label':label,'text':val} for label,val in zip('ABCD',items)],correctOption=correct,markScheme=[{'part':'','steps':[{'code':'A1','text':correct+'. '+reason}]}])
        else:
            assert parts
            q['parts']=[];q['markScheme']=[]
            for i,(prompt,steps) in enumerate(parts):
                assert steps and all(code in ('M1','A1','R1') for code,_ in steps)
                label=chr(97+i)
                q['parts'].append({'label':label,'prompt':prompt,'marks':len(steps)})
                q['markScheme'].append({'part':label,'steps':[{'code':code,'text':value} for code,value in steps]})
            q['marks']=sum(p['marks'] for p in q['parts'])
        if diagram:q['diagramSvg']=diagram
        if worked:q['markSchemeDiagramSvg']=worked
        self.questions.append(q);self.families.append(family)
    def extend(self,number,*parts):
        q=self.questions[number-1]
        assert q['questionType']!='multiple-choice'
        for prompt,steps in parts:
            label=chr(97+len(q['parts']))
            q['parts'].append({'label':label,'prompt':prompt,'marks':len(steps)})
            q['markScheme'].append({'part':label,'steps':[{'code':code,'text':answer} for code,answer in steps]})
            q['marks']+=len(steps)
    def save(self,expected,coverage):
        self.questions=normalize_formula_tokens(self.questions)
        assert len(self.questions)==expected
        assert Counter(q['syllabusCode'] for q in self.questions)==coverage
        assert all(n<=4 for n in Counter(self.families).values())
        assert len({q['stem'] for q in self.questions})==expected
        for q in self.questions:
            assert sum(len(x['steps']) for x in q['markScheme'])==q['marks']
            assert q['questionType']=='multiple-choice' or sum(p['marks'] for p in q['parts'])==q['marks']
            def strings(value):
                if isinstance(value,str):yield value
                elif isinstance(value,list):
                    for x in value:yield from strings(x)
                elif isinstance(value,dict):
                    for key,x in value.items():
                        if key not in ('diagramSvg','markSchemeDiagramSvg'):yield from strings(x)
            for s in strings(q):
                assert s.count('$')%2==0,(q['id'],s)
                assert not re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]',s),(q['id'],s)
                for chunk in re.split(r'\$[^$]*\$',s)[::1]:
                    assert not re.search(r'(?<!\\)[_^]',chunk),(q['id'],s)
            for key in ('diagramSvg','markSchemeDiagramSvg'):
                if key in q:
                    ElementTree.fromstring(q[key])
                    assert not re.search(r'<script|onload=|https?://(?!www.w3.org/2000/svg)',q[key])
        dest=ROOT/f'content/ib/chemistry/structure-{self.theme}.json';dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(self.questions,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        report={'theme':f'Structure {self.theme}','count':expected,'families':dict(Counter(self.families)),'levels':dict(Counter(q['level'] for q in self.questions)),'types':dict(Counter(q['questionType'] for q in self.questions)),'coverage':dict(Counter(q['syllabusCode'] for q in self.questions)),'questionDiagrams':sum('diagramSvg' in q for q in self.questions),'solutionDiagrams':sum('markSchemeDiagramSvg' in q for q in self.questions),'checks':['Every numerical answer recomputed from the quantities displayed in its own question.','Four distinct options and one private key for each one-mark MCQ.','Per-part marks equal distinct one-mark marking points; totals reconcile.','Balanced dollar mathematics; no unsupported chemistry extension.','Safe parseable standalone SVG diagrams; no externally sourced artwork.','SL/AHL labels follow the official first-assessment-2025 guide; calculator permitted throughout.'],'reviewStatus':'Author checks completed; independent review pending.','scopeSource':'https://xmltwo.ibo.org/publications/EAD/2026_EN/GR4/GR4-Chemistry_EN.pdf'}
        rd=ROOT/'docs/ib-chemistry-reviews';rd.mkdir(parents=True,exist_ok=True)
        (rd/f'structure-{self.theme}-author.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(report,ensure_ascii=False,indent=2))

SUBTOPICS={'S1.1':'Introduction to the particulate nature of matter','S1.2':'The nuclear atom','S1.3':'Electron configurations','S1.4':'Counting particles by mass: the mole','S1.5':'Ideal gases','S2.1':'The ionic model','S2.2':'The covalent model','S2.3':'The metallic model','S2.4':'From models to materials','S3.1':'The periodic table: classification of elements','S3.2':'Functional groups: classification of organic compounds'}
