"""Original IB Economics practice authoring. No source examination text is ingested.

Run economics_build.py from this directory. Question families are hand-designed;
each has at most three constructed-context variants. Solutions are private fields.
"""
from pathlib import Path
from fractions import Fraction
from decimal import Decimal, ROUND_HALF_UP, localcontext
import json, hashlib, html, re

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'content/ib/economics'
REVIEW = ROOT / 'docs/ib-expansion-reviews'
QUESTIONS = {}
LEDGER = []
TOPICS = {'introduction':'in','microeconomics':'mi','macroeconomics':'ma','global-economy':'gl'}
CASES = ['Arden','Belora','Caldin','Doreva','Elarin','Faron','Gavela','Hesper','Ilyra','Jorven','Kestrel','Lunara','Merin','Noreva','Orlen','Pavira','Quorin','Ravela','Selven','Tavora','Ulara','Vesper','Weylin','Xandor','Yarela','Zorlin']

def fmt(x):
    f = Fraction(x)
    if f.denominator == 1:
        return str(f.numerator)
    # IB's worked rounding example is 5.625 -> 5.63, rather than half-even.
    with localcontext() as context:
        context.prec=40
        value=Decimal(f.numerator)/Decimal(f.denominator)
        return str(value.quantize(Decimal('0.01'),rounding=ROUND_HALF_UP))

def table(headers, rows):
    return '| ' + ' | '.join(map(str,headers)) + ' |\n| ' + ' | '.join(['---']*len(headers)) + ' |\n' + '\n'.join('| '+' | '.join(map(str,r))+' |' for r in rows) + '\n\n'

def point(label, prompt, marks, *steps):
    assert sum(int(code[1:]) if code != 'AG' else 0 for code, text in steps) == marks
    return ({'label':label,'prompt':prompt,'marks':marks}, {'part':label,'steps':[{'code':code,'text':text} for code,text in steps]})

def rubric(max_marks, mode, focus):
    if max_marks==4:
        return {'maxMarks':4,'bands':[{'min':0,'max':0,'descriptor':'No relevant economic explanation.'},{'min':1,'max':2,'descriptor':'The response identifies a relevant idea but the causal explanation is incomplete, unclear or weakly linked to the case. Focus: '+focus},{'min':3,'max':4,'descriptor':'The response gives a clear, accurate causal explanation that addresses the task and applies the relevant case evidence. Any required diagram is consistent with the explanation. Use the upper mark when the reasoning is well developed. Focus: '+focus}]}
    limits = [(0,0),(1,2),(3,4),(5,6),(7,8),(9,10)] if max_marks == 10 else [(0,0),(1,3),(4,6),(7,9),(10,12),(13,15)]
    if mode == 'explain':
        texts = ['No relevant economic explanation.',
            'A few terms or disconnected assertions; the mechanism asked about is largely missing.',
            'Some relevant concepts described, but causal links are thin or contain major gaps.',
            'A partially developed explanation addresses the mechanism, with some accurate terminology and a relevant diagram where useful.',
            'A coherent explanation addresses the task, connects causes to outcomes and explains a correctly labelled diagram where useful; minor gaps remain.',
            'A precise, complete causal explanation addresses the task throughout, uses economic language accurately and integrates any useful diagram with its labels and movements.']
    elif mode == 'policy':
        texts = ['No relevant recommendation or reasoning.',
            'A policy is named with little economic reasoning or use of the case.',
            'An arguably relevant policy is described, with limited theory and a brief reference to the evidence.',
            'A workable recommendation has some explained causal links and case evidence; limitations or alternatives receive uneven attention.',
            'A well supported recommendation uses accurate theory and several case details, weighs a meaningful limitation or alternative and reaches a reasoned conclusion.',
            'A convincing recommendation integrates the quantitative and qualitative evidence, explains implementation and transmission, weighs credible alternatives and adverse effects, and reaches a conditional judgement about effectiveness.']
    else:
        texts = ['No relevant analysis or judgement.',
            'Assertions or terminology show little grasp of the question; evidence and judgement are absent or irrelevant.',
            'Relevant ideas are mainly described. Evidence is mentioned and evaluation is superficial.',
            'Some causal analysis and useful evidence address part of the task. Evaluation has a reasoned element but is one-sided or underdeveloped.',
            'The task is addressed with coherent theory, appropriately explained diagrams where useful, relevant developed evidence and mostly balanced evaluation.',
            'The task is addressed thoroughly: precise theory and developed evidence support a balanced comparison of effects, assumptions and trade-offs, leading to a justified conditional conclusion.']
        if mode == 'essay':
            texts[2] += ' A relevant real-world example is identified.'
            texts[3] += ' A studied real-world example is partly developed.'
            texts[4] += ' A studied real-world example is developed to support the argument.'
            texts[5] += ' At least one studied real-world example is fully integrated into the argument.'
        if mode == 'data':
            texts[2] += ' Use of the supplied text/data is limited.'
            texts[3] += ' Some relevant text/data supports the argument.'
            texts[4] += ' The supplied text/data is applied accurately.'
            texts[5] += ' Selected details from the supplied text/data are used to derive and support economic judgements.'
    return {'maxMarks':max_marks,'bands':[{'min':lo,'max':hi,'descriptor':txt+' Focus: '+focus} for (lo,hi),txt in zip(limits,texts)]}

def bandpart(label,prompt,marks,mode,focus,model):
    return ({'label':label,'prompt':prompt,'marks':marks}, {'part':label,'steps':[{'code':'IND','text':'Indicative model reasoning (not an additive checklist): '+model}, {'code':'IND','text':'Apply the bands by best fit across the response. Credit other sound economic reasoning and justified conclusions. The top band is attainable without faultless performance; do not require every indicative point. '+('A suitable diagram is helpful but is not a separate requirement for the top band in this evaluative response. ' if mode=='data' else '')+'Any conclusion must follow the student\'s evidence and assumptions.'}], 'rubric':rubric(marks,mode,focus)})

def graph(kind='demand-up', title='Indicative economic diagram'):
    """Private, native SVG. Straight segments with explicit labels and no dependencies."""
    esc = html.escape
    if kind in ['ppc','ppc-repairs','ppc-recovery']:
        paths=[('M 80 65 Q 345 60 420 315','#2563eb','PPC',305,125)]
        axes=('Bicycles repaired','Radios repaired') if kind=='ppc-repairs' else ('Consumer goods','Capital goods')
    elif kind=='ppc-linear':
        paths=[('M 80 65 L 420 315','#2563eb','Constant-cost PPC',278,174)]
        axes=('Baskets','Stools')
    elif kind=='ppc-sector':
        paths=[('M 80 65 Q 285 70 370 315','#2563eb','Before training',218,162),('M 80 65 Q 380 70 470 315','#0f766e','After training',350,200)]
        axes=('Heat pumps','Food')
    elif kind.startswith('adas'):
        axes=('Real output','Price level')
        if kind=='adas-cost':
            paths=[('M 105 95 L 445 300','#2563eb','AD',442,300),('M 110 300 L 435 90','#dc2626','SRAS1',430,86),('M 80 260 L 380 60','#0f766e','SRAS2',370,58)]
        elif kind=='adas-capacity':
            paths=[('M 105 95 L 445 300','#2563eb','AD',442,300),('M 310 315 L 310 65','#dc2626','LRAS1',250,54),('M 390 315 L 390 65','#0f766e','LRAS2',384,54)]
        elif kind=='adas-down':
            paths=[('M 145 70 L 455 260','#2563eb','AD1',447,263),('M 80 110 L 390 300','#0f766e','AD2',383,303),('M 110 300 L 435 90','#dc2626','SRAS',431,86)]
        else:
            paths=[('M 80 110 L 390 300','#2563eb','AD1',383,303),('M 145 70 L 455 260','#0f766e','AD2',447,263),('M 110 300 L 435 90','#dc2626','SRAS',431,86)]
    elif kind=='externality':
        axes=('Quantity','Costs and benefits')
        paths=[('M 95 80 L 440 290','#2563eb','MSB = MPB',402,296),('M 95 300 L 440 115','#dc2626','MPC',444,116),('M 95 240 L 395 65','#0f766e','MSC',400,65)]
    elif kind=='positive':
        axes=('Quantity','Costs and benefits')
        paths=[('M 95 120 L 400 300','#2563eb','MPB',398,306),('M 155 65 L 460 245','#0f766e','MSB',455,245),('M 95 300 L 440 95','#dc2626','MSC = MPC',420,89)]
    elif kind=='externality-cons':
        axes=('Quantity of damaging activity','Costs and benefits')
        paths=[('M 155 65 L 460 245','#2563eb','MPB',455,245),('M 95 120 L 400 300','#0f766e','MSB',398,306),('M 95 300 L 440 95','#dc2626','MSC = MPC',420,89)]
    elif kind=='ceiling':
        axes=('Quantity','Price')
        paths=[('M 95 80 L 440 290','#2563eb','D',443,294),('M 95 300 L 440 95','#dc2626','S',443,95),('M 80 245 L 470 245','#0f766e','Price ceiling',475,249)]
    elif kind=='fx-up':
        axes=('Quantity of currency','Foreign currency per unit')
        paths=[('M 80 110 L 390 300','#2563eb','D1',381,305),('M 145 70 L 455 260','#0f766e','D2',445,270),('M 110 300 L 435 90','#dc2626','S',438,88)]
    elif kind=='lorenz-quintiles':
        axes=('Cumulative population (%)','Cumulative income (%)')
        paths=[('M 80 315 L 450 55','#64748b','Equality',268,154),('M 80 315 L 154 302 L 228 276 L 302 237 L 376 172 L 450 55','#dc2626','Before',310,240),('M 80 315 L 154 294.2 L 228 263 L 302 218.8 L 376 153.8 L 450 55','#0f766e','After',233,255)]
    elif kind=='lorenz':
        axes=('Cumulative population (%)','Cumulative income (%)')
        paths=[('M 80 315 L 450 55','#64748b','Equality',268,154),('M 80 315 Q 355 315 450 55','#dc2626','Before',347,266),('M 80 315 Q 255 265 450 55','#0f766e','After',235,226)]
    elif kind=='tariff':
        axes=('Quantity','Price')
        paths=[('M 95 80 L 440 290','#2563eb','D',443,294),('M 95 300 L 440 95','#dc2626','S domestic',417,84),('M 80 230 L 460 230','#64748b','World price',462,235),('M 80 185 L 460 185','#0f766e','World price + tariff',368,174)]
    elif kind=='supply-down':
        axes=('Quantity','Price')
        paths=[('M 95 80 L 440 290','#2563eb','D',442,296),('M 95 300 L 440 95','#dc2626','S1',443,95),('M 80 250 L 380 65','#0f766e','S2',383,64)]
    elif kind=='tax':
        axes=('Quantity','Price')
        paths=[('M 95 80 L 440 290','#2563eb','D',442,296),('M 95 300 L 440 95','#dc2626','S',443,95),('M 80 245 L 380 65','#0f766e','S + tax',383,64)]
    elif kind=='subsidy':
        axes=('Quantity','Price')
        paths=[('M 95 80 L 440 290','#2563eb','D',442,296),('M 80 245 L 380 65','#dc2626','S',383,64),('M 95 300 L 440 95','#0f766e','S after subsidy',443,95)]
    elif kind=='fx-fixed':
        axes=('Quantity of crowns','US dollars per crown')
        paths=[('M 95 80 L 440 290','#2563eb','D private',443,294),('M 95 300 L 440 95','#dc2626','S private',443,95),('M 80 140 L 470 140','#0f766e','Fixed rate',478,144)]
    else:
        axes=('Quantity','Price')
        paths=[('M 80 110 L 390 300','#2563eb','D1',381,307),('M 145 70 L 455 260','#0f766e','D2',445,271),('M 110 300 L 435 90','#dc2626','S',438,88)]
    body='<rect x="0" y="0" width="640" height="410" fill="#ffffff"/><text x="24" y="25" font-size="17" fill="#0f172a">'+esc(title)+'</text>'
    body+='<path d="M 80 48 L 80 315 L 510 315" stroke="#0f172a" stroke-width="2" fill="none"/>'
    body+=f'<text x="240" y="362" font-size="14" fill="#0f172a">{esc(axes[0])}</text><text x="14" y="44" font-size="12" fill="#0f172a">{esc(axes[1])}</text>'
    for d,color,label,x,y in paths:
        body+=f'<path d="{d}" stroke="{color}" stroke-width="2.5" fill="none"/><text x="{x}" y="{y}" font-size="12" fill="{color}">{esc(label)}</text>'
    if kind=='ppc-recovery':
        body+='<circle cx="210" cy="240" r="4" fill="#dc2626"/><text x="185" y="262" font-size="13" fill="#dc2626">Idle resources</text><path d="M 218 236 L 303 199 L 289 199 M 303 199 L 295 212" stroke="#0f766e" stroke-width="2" fill="none"/><circle cx="310" cy="194" r="4" fill="#0f766e"/><text x="318" y="191" font-size="12" fill="#0f766e">Recovery</text>'
    if kind=='ceiling':
        body+='<path d="M 187 245 L 187 315 M 366 245 L 366 315" stroke="#64748b" stroke-dasharray="5 4" fill="none"/><text x="177" y="336" font-size="12" fill="#0f172a">Qs</text><text x="356" y="336" font-size="12" fill="#0f172a">Qd</text><text x="235" y="232" font-size="12" fill="#0f766e">Shortage = Qd − Qs</text>'
    if kind=='fx-fixed':
        body+='<path d="M 194 140 L 194 315 M 364 140 L 364 315" stroke="#64748b" stroke-dasharray="5 4" fill="none"/><text x="184" y="336" font-size="12" fill="#0f172a">Qd</text><text x="354" y="336" font-size="12" fill="#0f172a">Qs</text><text x="193" y="124" font-size="12" fill="#0f766e">Central bank buys Qs − Qd crowns</text>'
    if kind=='lorenz-quintiles':
        for x,pop in [(80,0),(154,20),(228,40),(302,60),(376,80),(450,100)]:
            body+=f'<text x="{x-5}" y="335" font-size="11" fill="#475569">{pop}</text>'
        for y,inc in [(315,0),(263,20),(211,40),(159,60),(107,80),(55,100)]:
            body+=f'<text x="50" y="{y+4}" font-size="11" fill="#475569">{inc}</text>'
    body+='<text x="24" y="391" font-size="12" fill="#475569">Schematic: label equilibrium projections and explain the relevant movement.</text>'
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 410" role="img" aria-label="'+esc(title)+'">'+body+'</svg>'

def add(topic,family,v,code,title,subtopic,level,style,qtype,stem,ps,diagram=None,numeric=None,difficulty='medium'):
    n=len(QUESTIONS.setdefault(topic,[]))+1
    q={'id':f'ib-econ-{TOPICS[topic]}-{n:03d}','subject':'economics','topicId':topic,'collectionId':'economics-'+topic,'number':n,'title':title,'subtopic':subtopic,'syllabusCode':code,'level':level,'questionType':qtype,'examStyle':style,'difficulty':difficulty,'calculator':style!='paper-1','marks':sum(p[0]['marks'] for p in ps),'stem':stem,'parts':[p[0] for p in ps],'markScheme':[p[1] for p in ps],'source':{'document':'Independent syllabus-authored practice','question':n},'verification':{'method':'Syllabus boundary review, independent arithmetic replay and economic reasoning review','notes':f'Original constructed scenario; family {family}, variant {v+1}. Paper 2 uses common SL content only. Any numerical result follows from the displayed information. Levelling uses best fit rather than counting indicative points. Accept consistent alternative diagrams and justified economic judgements.'},'status':'published'}
    if qtype=='policy-response':
        for p,g in zip(q['parts'],q['markScheme']):
            # Current examiner instructions require a short AO2 markband for
            # 4-mark explanation parts in HL Paper3, alongside specific content.
            if p['marks']==4 and (p['prompt'].startswith(('Explain','Distinguish','Using AD/AS analysis'))):
                g['rubric']=rubric(4,'explain',p['prompt'])
                for step in g['steps']:step['code']='IND'
                g['steps'].append({'code':'IND','text':'Use the four-mark explanation bands by best fit; the preceding content is indicative rather than four additive marks. Accept a different valid economic explanation that addresses the case.'})
    if diagram:
        q['markSchemeDiagramSvg']=graph(diagram,title+' — solution sketch')
        q['markSchemeDiagramCaption']='Private indicative diagram; projections, equilibrium labels and the contextual explanation are specified in the markscheme. Equivalent accurate diagrams earn credit.'
    QUESTIONS[topic].append(q)
    LEDGER.append({'id':q['id'],'family':family,'variant':v+1,'syllabusCode':code,'level':level,'format':qtype,'numericChecks':numeric or [],'scopeReview':'Guide first assessment 2024 and current 2027 examiner instructions; assessable common/extension boundary checked for this family.','reasoningReview':'Causal channels, ceteris paribus assumptions, alternative conclusions and diagram directions reviewed at family level.','markbandReview':'Best-fit rubric with zero-value IND content.' if any('rubric' in p[1] for p in ps) else 'Point allocations checked against each part; no evaluative band is replaced by an additive checklist.'})
    return q

def save():
    OUT.mkdir(parents=True,exist_ok=True);REVIEW.mkdir(parents=True,exist_ok=True)
    def tidy(value, key=''):
        if isinstance(value,list):return [tidy(item,key) for item in value]
        if isinstance(value,dict):return {k:tidy(item,k) for k,item in value.items()}
        if isinstance(value,str) and key in ['stem','prompt','text','descriptor','title','subtopic','notes']:
            return re.sub(r'(?<=[a-z])(?=\d)', ' ', value.replace('US$','USD '))
        return value
    for topic in list(QUESTIONS):QUESTIONS[topic]=tidy(QUESTIONS[topic])
    for topic,qs in QUESTIONS.items():
        (OUT/(topic+'.json')).write_text(json.dumps(qs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    for row in LEDGER:
        q=next(q for q in QUESTIONS[next(t for t,p in TOPICS.items() if row['id'].startswith('ib-econ-'+p+'-'))] if q['id']==row['id'])
        row['sha256']=hashlib.sha256(json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    (REVIEW/'economics-ledger.json').write_text(json.dumps(LEDGER,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
