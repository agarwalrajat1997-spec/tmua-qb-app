"""Original practice authoring. No source-paper text or figures are embedded."""
import json, math, html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'content/ib/chemistry-2025-practice'
QUESTIONS=[]
TOPICS={'S1':('structure-1',['Introduction to the particulate nature of matter','The nuclear atom','Electron configurations','Counting particles by mass: The mole','Ideal gases']), 'S2':('structure-2',['The ionic model','The covalent model','The metallic model','From models to materials']), 'S3':('structure-3',['The periodic table: Classification of elements','Functional groups: Classification of organic compounds']), 'R1':('reactivity-1',['Measuring enthalpy changes','Energy cycles in reactions','Energy from fuels','Entropy and spontaneity']), 'R2':('reactivity-2',['How much? The amount of chemical change','How fast? The rate of chemical change','How far? The extent of chemical change']), 'R3':('reactivity-3',['Proton transfer reactions','Electron transfer reactions','Electron sharing reactions','Electron-pair sharing reactions'])}
def base(code,level,title,stem,kind,difficulty,figure=None):
    theme,sub=code.split('.'); topic,titles=TOPICS[theme]
    n=801+sum(q['topicId']==topic for q in QUESTIONS)
    q=dict(id=f'ib-chem-{theme.lower()}-{n}',number=n,subject='chemistry',topicId=topic,collectionId='chemistry-'+topic,syllabusCode=code,subtopic=titles[int(sub)-1],level=level,title=title,stem=stem,questionType=kind,difficulty=difficulty,calculator=True,source=dict(document='Independent syllabus-authored practice',question=n),verification=dict(method='Author derivation and automated schema, rendering and numerical checks',notes='Original practice for the first-assessment-2025 syllabus. Marking points are instructional; equivalent chemically valid explanations and appropriate error-carried-forward working are accepted. Separate human examiner moderation has not been performed.'),status='published')
    if figure:q['diagramSvg']=figure
    return q
def mc(code,level,title,stem,options,answer,explanation,difficulty='medium',figure=None):
    q=base(code,level,title,stem,'multiple-choice',difficulty,figure)
    # Rotate authored options deterministically to avoid answer-position bias.
    shift=len(QUESTIONS)%4; options=options[shift:]+options[:shift]; answer=(answer-shift)%4
    q.update(marks=1,parts=[],options=[dict(label=chr(65+i),text=s) for i,s in enumerate(options)],correctOption=chr(65+answer),markScheme=[dict(part='',steps=[dict(code='A1',text=f'**{chr(65+answer)}.** '+explanation)])],answerSummary=chr(65+answer))
    QUESTIONS.append(q);return q
def wr(code,level,title,stem,parts,kind='structured',difficulty='hard',figure=None):
    q=base(code,level,title,stem,kind,difficulty,figure);q['parts']=[];q['markScheme']=[]
    for i,(prompt,steps) in enumerate(parts):
        label=chr(97+i);steps=[dict(code=c,text=t) for c,t in steps];marks=sum(int(s['code'][1:]) for s in steps if s['code'] not in ('AG','IND'))
        q['parts'].append(dict(label=label,prompt=prompt,marks=marks));q['markScheme'].append(dict(part=label,steps=steps))
    q['marks']=sum(p['marks'] for p in q['parts']);QUESTIONS.append(q);return q
def table(headers,rows):return '\n\n| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(map(str,r))+' |' for r in rows)+'\n\n'
def svg(body,w=720,h=380):return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img"><rect width="{w}" height="{h}" fill="white"/>'+body+'</svg>'
def text(x,y,s,size=18,anchor='middle',color='#172b4d'):
    return f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="{size}" text-anchor="{anchor}" fill="{color}">{html.escape(str(s))}</text>'
def line(x1,y1,x2,y2,color='#243b53',width=2,dash=''):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>'
def plot(series,xlabel,ylabel,xlim=None,ylim=None,title='Constructed data',sticks=False,annotate=False,xticks=None,yticks=None):
    # series: label, [(x,y),...], colour. All dimensions and labels kept within canvas.
    pts=[p for _,arr,_ in series for p in arr];xmin,xmax=xlim or (min(p[0] for p in pts),max(p[0] for p in pts));ymin,ymax=ylim or (0,max(p[1] for p in pts)*1.15)
    sx=lambda x:95+570*(x-xmin)/(xmax-xmin);sy=lambda y:285-200*(y-ymin)/(ymax-ymin)
    b=text(380,28,title,20)+line(95,85,95,285)+line(95,285,665,285)
    for x in xticks or [xmin+(xmax-xmin)*i/5 for i in range(6)]:
        b+=line(sx(x),285,sx(x),290)+text(round(sx(x),2),311,f'{x:.3g}',14)
    for y in yticks or [ymin+(ymax-ymin)*i/5 for i in range(6)]:
        b+=line(90,sy(y),665,sy(y),'#dce4ec',1)+text(83,round(sy(y)+5,2),f'{y:.3g}',14,'end')
    for j,(label,arr,col) in enumerate(series):
        if sticks:
            for x,y in arr:
                b+=line(round(sx(x),2),sy(0),round(sx(x),2),round(sy(y),2),col,3)
                if annotate:b+=text(round(sx(x),2),round(sy(y)-10,2),f'{x:g}: {y:g}',14)
        else:
            b+=f'<polyline points="'+ ' '.join(f'{sx(x):.2f},{sy(y):.2f}' for x,y in arr)+f'" fill="none" stroke="{col}" stroke-width="2.5"/>'
            for x,y in arr:b+=f'<circle cx="{sx(x):.2f}" cy="{sy(y):.2f}" r="3.5" fill="{col}"/>'
        if label:b+=line(120+j*220,55,148+j*220,55,col,3)+text(158+j*220,60,label,15,'start')
    b+=text(380,348,xlabel,17)+text(18,185,ylabel,15,'start') if len(ylabel)<6 else text(380,348,xlabel,17)+text(95,77,ylabel,15,'start')
    return svg(b)
def energy(reactant,peak,product,cat=None):
    vals=[reactant,peak,product]+([cat] if cat is not None else []);lo=min(vals)-25;hi=max(vals)+20
    sy=lambda e:285-210*(e-lo)/(hi-lo)
    b=line(90,70,90,295)+line(90,295,665,295)+text(90,45,'Potential energy / kJ mol⁻¹',17,'start')+text(380,344,'Reaction coordinate',17)
    for label,x,e in [('Reactants',170,reactant),('Products',575,product)]:b+=line(x-45,sy(e),x+45,sy(e))+text(x,sy(e)+25,label,16)+text(x,sy(e)-12,str(e),16)
    b+=f'<path d="M 215 {sy(reactant):.2f} C 280 {sy(reactant):.2f}, 290 {sy(peak):.2f}, 355 {sy(peak):.2f} S 460 {sy(product):.2f},530 {sy(product):.2f}" stroke="#186c93" stroke-width="3" fill="none"/>'+text(355,sy(peak)-10,str(peak),16)
    if cat is not None:b+=f'<path d="M 215 {sy(reactant):.2f} C 280 {sy(reactant):.2f},290 {sy(cat):.2f},355 {sy(cat):.2f} S 460 {sy(product):.2f},530 {sy(product):.2f}" stroke="#ae5b22" stroke-width="3" fill="none" stroke-dasharray="6 4"/>'+text(355,sy(cat)+24,str(cat)+' (catalysed)',15)
    return svg(b)
def tlc(spots,front=8):
    b=text(360,28,'Thin-layer chromatogram',20)+f'<rect x="180" y="55" width="360" height="250" fill="#f8fafc" stroke="#65758b"/>'
    y=lambda d:280-24*d
    b+=line(190,280,530,280)+text(550,285,'baseline',15,'start')+line(190,y(front),530,y(front),'#186c93',2,'5 4')+text(550,y(front)+5,'front',15,'start')
    for i,(label,d) in enumerate(spots):
        x=250+i*110;b+=f'<circle cx="{x}" cy="{y(d)}" r="8" fill="#186c93"/>'+text(x,y(d)-15,label,17)+text(x,330,f'{d:g} cm',17)
    b+=text(360,366,f'Solvent front: {front:g} cm from baseline',17);return svg(b)
def orbital(occupancies):
    b=text(360,38,'Orbital occupation',21);x=100
    for label,boxes in occupancies:
        width=48*len(boxes);b+=text(x+width/2,115,label,19)
        for j,occ in enumerate(boxes):b+=f'<rect x="{x+j*48}" y="145" width="44" height="48" fill="none" stroke="#243b53" stroke-width="2"/>'+text(x+j*48+22,179,occ,25)
        x+=width+40
    return svg(b,720,240)
def save(theme):
    OUT.mkdir(parents=True,exist_ok=True);qs=[q for q in QUESTIONS if q['syllabusCode'].startswith(theme)]
    (OUT/(theme.lower()+'.json')).write_text(json.dumps(qs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(theme,len(qs))
def molecule(atoms,bonds,title='Displayed connectivity; geometry not implied'):
    b=text(360,30,title,19)
    for a,c,order in bonds:
        x1,y1,_=atoms[a];x2,y2,_=atoms[c];dx=x2-x1;dy=y2-y1;length=math.hypot(dx,dy);ux,uy=dx/length,dy/length
        for j in range(order):
            off=(j-(order-1)/2)*7
            b+=line(x1+ux*25-uy*off,y1+uy*25+ux*off,x2-ux*25-uy*off,y2-uy*25+ux*off,width=2.5)
    for x,y,a in atoms:b+=text(x,y+7,a,22)
    return svg(b,720,300)
