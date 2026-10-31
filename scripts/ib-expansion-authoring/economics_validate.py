"""Independent replay of serialized Economics content (does not import authoring).

Checks structure, official format boundaries, displayed-table arithmetic, private
SVG syntax and every arithmetic expression in the author ledger. Reports exact
hashes so a later change invalidates the reviewed snapshot.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as F
import ast, math, json, hashlib, re, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/ib-expansion-reviews'
qs=[q for path in sorted((ROOT/'content/ib/economics').glob('*.json')) for q in json.loads(path.read_text(encoding='utf-8'))]
ledger=json.loads((OUT/'economics-ledger.json').read_text(encoding='utf-8'));byid={q['id']:q for q in qs}
errors=[];replays=[]

def require(test,msg):
    if not test:errors.append(msg)

def ev(node):
    if isinstance(node,ast.Expression):return ev(node.body)
    if isinstance(node,ast.Constant) and isinstance(node.value,(int,float)):return F(str(node.value))
    if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.USub,ast.UAdd)):return -ev(node.operand) if isinstance(node.op,ast.USub) else ev(node.operand)
    if isinstance(node,ast.BinOp):
        a,b=ev(node.left),ev(node.right)
        if isinstance(node.op,ast.Add):return a+b
        if isinstance(node.op,ast.Sub):return a-b
        if isinstance(node.op,ast.Mult):return a*b
        if isinstance(node.op,ast.Div):return a/b
    raise ValueError('Only ordinary numerical arithmetic is accepted')

def rows(stem):
    return [[cell.strip() for cell in line.strip().strip('|').split('|')] for line in stem.splitlines() if line.startswith('|') and not line.startswith('| ---')]

def group(q,label):return next(g for g in q['markScheme'] if g['part']==label)

def answer_has(q,label,value,desc):
    value=F(value);text=' '.join(s['text'] for s in group(q,label)['steps']).replace('−','-')
    forms=[str(value.numerator)] if value.denominator==1 else [f'{float(value):.2f}',str(value)]
    compact=text.replace(' ','').replace(',','')
    require(any(x in compact for x in forms),f'{q["id"]}: displayed-input replay missing {desc} = {value}')
    replays.append({'id':q['id'],'part':label,'derivation':desc,'exactResult':str(value),'decimalResult':float(value),'source':'reparsed serialized question stimulus'})

for path in (ROOT/'content/ib/economics').glob('*.json'):
    require(b'\r' not in path.read_bytes(),f'{path.name}: must use UTF-8 LF')

for q in qs:
    ident=q['id'];parts=q['parts'];schemes=q['markScheme'];style=q['examStyle'];typ=q['questionType']
    require(q['calculator']==(style!='paper-1'),ident+': calculator condition')
    require(sum(p['marks'] for p in parts)==q['marks'],ident+': part totals')
    require(len(parts)==len(schemes),ident+': scheme coverage')
    for p,g in zip(parts,schemes):
        require(p['label']==g['part'],ident+': scheme label')
        if 'rubric' in g:
            r=g['rubric'];require(all(s['code']=='IND' for s in g['steps']),ident+': non-IND rubric guidance')
            require(r['maxMarks']==p['marks'],ident+': rubric maximum')
            bands=r['bands'];covered=[n for b in bands for n in range(b['min'],b['max']+1)]
            require(covered==list(range(p['marks']+1)),ident+': rubric gaps/overlap')
        else:
            val=sum(0 if s['code']=='AG' else int(s['code'][1:]) for s in g['steps'])
            require(val==p['marks'],ident+': point allocation')
    if typ=='essay':require([p['label'] for p in parts]==['a','b'] and [p['marks'] for p in parts]==[10,15],ident+': full Paper1 format')
    if typ=='data-response':
        require([p['label'] for p in parts]==list('abcdefg') and [p['marks'] for p in parts]==[4,5,4,4,4,4,15],ident+': full Paper2 format')
        require(q['level']=='sl',ident+': Paper2 extension content')
    if typ=='policy-response':require(sum(p['marks'] for p in parts[:-1])==20 and parts[-1]['label']=='b' and parts[-1]['marks']==10 and q['level']=='ahl',ident+': full HL Paper3 format')
    if q['syllabusCode'] in ['2.4','2.10','2.11','2.12']:require(q['level']=='ahl',ident+': wholly HL subtopic')
    for field in ['diagramSvg','markSchemeDiagramSvg']:
        if field in q:
            svg=q[field];ET.fromstring(svg)
            require('viewBox=' in svg and not re.search(r'<(?:script|image|style|use|foreignObject)\b|(?:href|src)\s*=|url\s*\(',svg,re.I),ident+': SVG safety')

for row in ledger:
    q=byid[row['id']]
    digest=hashlib.sha256(json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    require(digest==row['sha256'],row['id']+': stale author hash')
    for check in row['numericChecks']:
        actual=ev(ast.parse(check['expression'],mode='eval'));expected=F(str(check['expected']))
        require(abs(float(actual-expected))<1e-8,row['id']+': ledger arithmetic '+check['expression'])
    row['arithmeticReplay']='All listed expressions recomputed independently with exact rational arithmetic; '+str(len(row['numericChecks']))+' expression(s).'

# Full Paper2 arithmetic is independently reconstructed directly from the tables.
for q in qs:
    if q['questionType']!='data-response':continue
    rr=rows(q['stem'])
    if q['topicId']=='microeconomics':
        r=[r for r in rr if r[0] in ['Initial','New']];p0,q0=map(F,r[0][1:]);p1,q1=map(F,r[1][1:])
        pc=(p1-p0)/p0*100;qc=(q1-q0)/q0*100
        answer_has(q,'b',pc,'percentage price change from initial price')
        answer_has(q,'b',qc/pc,'PED from initial-value percentages')
    elif q['topicId']=='macroeconomics':
        data={r[0]:F(r[1]) for r in rr if r[0] in ['Nominal GDP (billion crowns)','GDP deflator (base year=100)','Population (million)']}
        real=data['Nominal GDP (billion crowns)']/data['GDP deflator (base year=100)']*100
        answer_has(q,'b',real,'real GDP in billion crowns')
        answer_has(q,'b',real/data['Population (million)']*1000,'real GDP per capita in crowns')
    else:
        data={r[0]:F(r[1]) for r in rr if r[0] in ['Goods exports','Goods imports','Net services','Net primary income','Net current transfers']}
        goods=data['Goods exports']-data['Goods imports'];ca=goods+data['Net services']+data['Net primary income']+data['Net current transfers']
        answer_has(q,'b',goods,'goods trade balance in billion crowns')
        answer_has(q,'b',ca,'current-account balance in billion crowns')

# Independently solve the serialized inverse curves, rather than using variant
# indices or variables from the authoring program.
for q in qs:
    if q['questionType']!='policy-response':continue
    st=q['stem'];r=next(x for x in ledger if x['id']==q['id']);family=r['family']
    if family in ['micro-policy-01','micro-policy-02','micro-policy-03','micro-policy-05']:
        match=re.search(r'P=(\d+)−Q.*?P=(\d+)\+Q',st)
        A,B=map(F,match.groups());Q=(A-B)/2;P=(A+B)/2
        answer_has(q,'a(i)',Q,'unregulated equilibrium quantity')
        answer_has(q,'a(i)',P,'unregulated equilibrium price')
        if family=='micro-policy-05':
            ceiling=F(re.search(r'maximum price is set at ([\d.]+)',st).group(1));qs0=ceiling-B;qd0=A-ceiling
            answer_has(q,'a(ii)',qs0,'quantity supplied at ceiling');answer_has(q,'a(ii)',qd0,'quantity demanded at ceiling')
            answer_has(q,'a(iii)',qd0-qs0,'shortage at ceiling');answer_has(q,'a(iii)',ceiling*qs0,'legal sales revenue')
            answer_has(q,'a(iv)',ceiling*(qd0-qs0),'conditional procurement cost')
        else:
            W=F(re.search(r'(?:tax of|subsidy of|external damage of) (\d+)',st).group(1));newQ=(A-B+(W if family=='micro-policy-02' else -W))/2
            answer_has(q,'a(ii)',newQ,'post-policy or efficient quantity')
            if family=='micro-policy-01':
                answer_has(q,'a(ii)',A-newQ,'taxed consumer price');answer_has(q,'a(ii)',B+newQ,'taxed producer net price')
                answer_has(q,'a(iii)',W*newQ,'tax revenue');answer_has(q,'a(iv)',W*(Q-newQ)/2,'no-externality welfare loss')
            elif family=='micro-policy-02':
                answer_has(q,'a(ii)',A-newQ,'subsidized buyer price');answer_has(q,'a(ii)',B+newQ,'producer receipt')
                answer_has(q,'a(iii)',W*newQ,'subsidy expenditure');answer_has(q,'a(iv)',(A-newQ)*newQ-P*Q,'buyer expenditure change')
            else:
                answer_has(q,'a(iii)',W*(Q-newQ)/2,'externality welfare loss');answer_has(q,'a(iv)',W*newQ,'corrective-tax revenue')
    elif family=='micro-policy-04':
        data=[list(map(F,rr)) for rr in rows(st) if rr[0].isdigit()];trs=[a*b for a,b,c in data];profits=[a*b-c for a,b,c in data]
        answer_has(q,'a(i)',profits[2],'Q3 profit from serialized table')
        answer_has(q,'a(ii)',max(profits),'maximum listed profit')
        answer_has(q,'a(iii)',trs[3]-trs[2],'MR from Q3 to Q4')
        answer_has(q,'a(iii)',data[3][2]-data[2][2],'MC from Q3 to Q4')
    elif family=='global-policy-01':
        A,B=map(F,re.search(r'P=(\d+)−Q.*?P=(\d+)\+Q',st).groups());W,T=map(F,re.search(r'World price is (\d+).*?tariff is (\d+)',st).groups());P=W+T
        qs0=W-B;qd0=A-W;qs1=P-B;qd1=A-P
        answer_has(q,'a(i)',qd0-qs0,'free-trade imports');answer_has(q,'a(ii)',qd1-qs1,'post-tariff imports')
        answer_has(q,'a(iii)',T*(qd1-qs1),'tariff revenue');answer_has(q,'a(iii)',(qd0+qd1)*T/2,'consumer surplus loss')
        answer_has(q,'a(iv)',(qs0+qs1)*T/2,'producer surplus gain');answer_has(q,'a(iv)',T*((qs1-qs0)+(qd0-qd1))/2,'national welfare loss')
    r['displayedInputReplay']=[x for x in replays if x['id']==q['id']]

counts=Counter(q['topicId'] for q in qs);forms=Counter(q['questionType'] for q in qs);families=Counter(r['family'] for r in ledger)
require(dict(counts)=={'global-economy':100,'introduction':40,'macroeconomics':100,'microeconomics':120},'Target topic counts')
require(len(families)>=120 and max(families.values())<=3,'Family diversity requirement')
require(forms['essay']>=40 and forms['data-response']>=40,'Full-paper format counts')
report={'subject':'economics','records':len(qs),'topicCounts':dict(counts),'formatCounts':dict(forms),'levelCounts':dict(Counter(q['level'] for q in qs)),'families':len(families),'maximumVariants':max(families.values()),'arithmeticExpressionChecks':sum(len(r['numericChecks']) for r in ledger),'displayedInputReplays':len(replays),'svgCount':sum('markSchemeDiagramSvg' in q for q in qs),'errors':errors,'scope':'Serialized record checks plus displayed-input reconstruction for every full Paper2 numerical part and inverse-curve policy calculations. Other numerical families additionally replayed from exact arithmetic ledgers; causal and level-boundary reasoning reviewed per authored family.','hashes':{q['id']:hashlib.sha256(json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest() for q in qs}}
(OUT/'economics-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
(OUT/'economics-ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
(OUT/'economics-numeric-replay.json').write_text(json.dumps(replays,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:v for k,v in report.items() if k!='hashes'},ensure_ascii=False,indent=2))
raise SystemExit(1 if errors else 0)
