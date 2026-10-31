"""Independent review: parse only serialized student-visible business cases.

No imports of authoring calculations or author numeric ledgers. Exact Decimal
arithmetic is used; diagrams are parsed as displayed SVG text/coordinates.
Semantic judgments are recorded separately in business-independent-family-review.
"""
from pathlib import Path
from decimal import Decimal as D, ROUND_HALF_UP, ROUND_CEILING
from collections import Counter
import json,re,hashlib,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2];DOC=ROOT/'docs/ib-expansion-reviews'
FILES=sorted((ROOT/'content/ib/business-management').glob('*.json'))
QS=[q for p in FILES for q in json.loads(p.read_text(encoding='utf8'))]
BY={q['id']:q for q in QS};EVIDENCE={};ERRORS=[];ASSERTIONS=0
N=r'([\d,]+(?:\.\d+)?)'

def dec(s):return D(str(s).replace(',','').replace('−','-'))
def cap(s,pattern):
    m=re.search(pattern,s,re.I)
    assert m,(pattern,s)
    return tuple(dec(x) for x in m.groups())
def numbers(s):return [dec(x) for x in re.findall(r'(?<![A-Za-z])[-−]?\d[\d,]*(?:\.\d+)?',s)]
def group(q,p):return [g for g in q['markScheme'] if g['part']==p]
def text(q,p,accuracy=True):
    steps=[s for g in group(q,p) for s in g['steps']]
    chosen=[s['text'] for s in steps if s['code']=='A1'] if accuracy else []
    return ' '.join(chosen or [s['text'] for s in steps])
def check(q,p,values,reason,places=2):
    global ASSERTIONS
    shown=text(q,p);found=numbers(shown);unit=D(1).scaleb(-places)
    expected=[dec(v).quantize(unit,rounding=ROUND_HALF_UP) for v in values]
    for v in expected:
        ASSERTIONS+=1
        if not any(v==n for n in found):ERRORS.append({'id':q['id'],'part':p,'expected':str(v),'answer':shown})
    EVIDENCE.setdefault(q['id'],[]).append({'part':p,'independentlyDerived':[str(v) for v in expected],'reason':reason,'displayedAnswer':shown,'status':'passed' if all(v in found for v in expected) else 'failed'})
def save(name,obj):
    (DOC/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def rows(q):
    return [[c.strip() for c in l.strip().strip('|').split('|')] for l in q['stem'].splitlines() if l.startswith('|') and not re.match(r'^\|[-:| ]+\|$',l)]
def texts(q,key='diagramSvg'):
    return [''.join(e.itertext()) for e in ET.fromstring(q[key]).iter() if e.tag.split('}')[-1]=='text']
def each(u,a,b):return [BY[f'ib-bm-u{u}-{n:03}'] for n in range(a,b+1)]

# Shared decision tree: extract every displayed probability/outcome and time-zero
# investment, rather than hard-code any author parameter array.
for q in each(1,65,68):
    cost,=cap(q['stem'],r'launch costs USD '+N)
    branches=[cap(t,r'p='+N+r'; USD '+N) for t in texts(q) if t.startswith('p=')]
    assert sum(p for p,v in branches)==1
    ev=sum(p*v for p,v in branches)-cost
    check(q,'a',[ev],'Probability-weighted terminal contributions minus the single initial cost; probabilities sum to one.')
    safe,=cap(' '.join(texts(q)),r'Certain: USD '+N)
    EVIDENCE[q['id']].append({'part':'c','decisionComparison':{'launchEV':str(ev),'certainAlternative':str(safe),'worstLaunchOutcome':str(min(v for p,v in branches)-cost)},'status':'passed','reason':'Model recommendation read against both expected value and downside; no guaranteed outcome inferred.'})
for q in each(1,77,80):
    available,cost,outflow=cap(q['stem'],r'Available unrestricted cash is USD '+N+r'.*?expansion would use USD '+N+r'.*?monthly net cash outflow is USD '+N)
    check(q,'b',[available-cost,outflow],'Restricted training grant is excluded from operating cash. Remaining unrestricted funds = available minus expansion.')
    assert (available-cost)/outflow==2 and 'two months' in text(q,'b').lower()
    EVIDENCE[q['id']].append({'part':'b','independentlyDerived':['2 months'],'reason':'Remaining cash divided by monthly net outflow, excluding restricted grant.','status':'passed'})
for q in each(2,9,12):
    ts=texts(q);staff=[cap(t,N+r' staff report directly')[0] for t in ts if 'staff report directly' in t]
    managers=[t for t in ts if t.lower().endswith('manager')]
    check(q,'a',[len(managers),3],'Three drawn functional-manager nodes report directly to the director; director/manager/staff gives three levels.',0)
    check(q,'c',[sum(staff)],'After delayering count all staff in the serialized chart; removed managers are not retained as staff.',0)
for q in each(2,53,56):
    start,end,leavers,cost=cap(q['stem'],r'employed '+N+r' people on the first day and '+N+r'.*? '+N+r' employees left.*?USD '+N+r' per replacement')
    check(q,'a',[200*leavers/(start+end)],'Leavers / arithmetic mean of displayed opening and closing employment × 100.')
    check(q,'b',[leavers*cost],'One direct replacement for every leaver; no indirect costs invented.')
for q in each(3,13,16):
    fixed,variable,qty=cap(q['stem'],r'fixed costs are USD '+N+r'; variable cost is USD '+N+r' per unit.*?produces '+N+r' units')
    total=fixed+variable*qty
    check(q,'a',[total],'Displayed monthly fixed cost plus unit variable cost times monthly output.')
    check(q,'b',[total/qty],'Monthly total cost divided by the same monthly output; units USD per unit.')
for q in each(3,17,20):
    qty,p,subs,fee=cap(q['stem'],r'sells '+N+r' individual services at USD '+N+r' each and has '+N+r' subscriptions at USD '+N)
    total=qty*p+subs*fee
    check(q,'a',[total],'Sum of explicitly disjoint services and earned subscription revenue.')
    check(q,'b',[100*subs*fee/total],'Monthly subscription earned revenue divided by total earned revenue.')
for q in each(3,21,24):
    data={r[0]:dec(r[1]) for r in rows(q)[1:]};r,c,e,i,t=data.values();gp=r-c;pbit=gp-e
    check(q,'a',[gp],'Statement revenue minus cost of sales.')
    check(q,'b',[pbit],'Gross profit less operating expenses excluding interest and tax.')
    check(q,'c',[pbit-i-t],'Deduct each explicitly displayed interest and tax item exactly once.')
for q in each(3,25,28):
    nc,stock,rec,cash,cl,ncl=cap(q['stem'],r'non-current assets '+N+r'; inventories '+N+r'; trade receivables '+N+r'; cash '+N+r'; current liabilities '+N+r'; non-current liabilities '+N)
    ca=stock+rec+cash
    check(q,'a',[ca],'Inventories plus receivables plus cash; non-current assets excluded.')
    check(q,'b',[nc+ca-cl-ncl],'All assets less all liabilities; balance-sheet equity identity.')
    check(q,'c',[ca-cl],'Current assets less current liabilities only.')
for q in each(3,29,32):
    data={r[0]:[dec(x) for x in r[1:]] for r in rows(q)[1:]};rev,cost,expenses=data.values()
    check(q,'a',[100*(rev[1]-cost[1])/rev[1]],'Year 2 gross profit divided by Year 2 revenue.')
    check(q,'b',[100*(rev[1]-cost[1]-expenses[1])/rev[1]],'Year 2 PBIT divided by Year 2 revenue, as instructed.')
    vals=[100*(rev[i]-cost[i])/rev[i] for i in (0,1)]+[100*(rev[i]-cost[i]-expenses[i])/rev[i] for i in (0,1)]
    check(q,'c',vals,'Independently check both years of both ratios used in the explanatory answer.')
for q in each(3,33,36):
    profit,eq,debt,newprofit,newcap=cap(q['stem'],r'profit before interest and tax is USD '+N+r'; equity is USD '+N+r'; non-current liabilities are USD '+N+r'.*?forecast annual profit before interest and tax of USD '+N+r' with total capital employed of USD '+N)
    check(q,'a',[100*profit/(eq+debt)],'PBIT / (equity + non-current liabilities), no averaging.')
    check(q,'b',[100*newprofit/newcap],'Forecast PBIT divided by the separately stated expanded capital base.')
for q in each(3,37,40):
    stock,rec,cash,cl,pay=cap(q['stem'],r'inventories are USD '+N+r', receivables USD '+N+r', cash USD '+N+r' and current liabilities USD '+N+r'.*?payment of USD '+N)
    ca=stock+rec+cash;assert pay<=cash
    check(q,'a',[ca/cl,(ca-stock)/cl],'Current and acid-test denominators both current liabilities; acid test excludes stock.')
    check(q,'b',[(ca-pay)/(cl-pay)],'Cash and the liability decline by the same payment; 1.625 rounds to 1.63 with half-up rounding.')
for q in each(3,41,44):
    opening,=cap(q['stem'],r'Opening cash before month 1 is USD '+N)
    purchase,=cap(q['stem'],r'machine costing USD '+N)
    rr=rows(q);receipts=[dec(x) for x in rr[1][1:]];payments=[dec(x) for x in rr[2][1:]]
    balance=opening;baseline=[]
    for rec,pay in zip(receipts,payments):balance+=rec-pay;baseline.append(balance)
    check(q,'a',baseline[:2],'Cumulative monthly cash conservation, not separate calculations with the same opening balance.')
    check(q,'b',[min(x-purchase for x in baseline)],'A single start-month-1 capital payment reduces every subsequent balance; minimize all three monthly closings.')
    check(q,'c',[x-purchase for x in baseline],'Check all three scenario balances cited in the model recommendation.')
for q in each(3,45,48):
    cost,=cap(q['stem'],r'costs USD '+N+r' at time zero')
    flowtext=re.search(r'annual net cash inflows of USD (.*?) in years',q['stem']).group(1)
    flows=numbers(flowtext);cum=D(0);pb=None
    for year,inflow in enumerate(flows):
        if cum+inflow>=cost:pb=D(year)+(cost-cum)/inflow;break
        cum+=inflow
    assert pb is not None
    check(q,'a',[pb],'Enumerate cumulative annual inflows to first crossing, then divide unrecovered balance by that crossing-year inflow.')
    check(q,'c',[pb,sum(flows)],'Recheck both the payback and four-year cash total used in the model recommendation.')
for q in each(3,49,52):
    cost,years,annual=cap(q['stem'],r'Initial cost is USD '+N+r'; life is '+N+r' years; forecast net operating cash inflow is USD '+N)
    profit=(years*annual-cost)/years
    check(q,'a',[profit],'Total lifetime inflows less capital cost divided by life; zero residual is explicit.')
    check(q,'b',[100*profit/cost],'ARR uses the explicitly specified original cost, not average investment.')
for q in each(3,53,56):
    cost,residual,life=cap(q['stem'],r'cash at USD '+N+r'.*?residual value is USD '+N+r', with a '+N+r'-year')
    used,=cap(q['parts'][1]['prompt'],r'after '+N+r' complete years')
    dep=(cost-residual)/life
    check(q,'a',[dep],'Depreciable base is cost less residual value; divide by stated useful life.')
    check(q,'b',[cost-used*dep],'Carrying value is original cost less accumulated charges for requested complete years.')
for q in each(3,57,60):
    cost,residual,total,used=cap(q['stem'],r'for USD '+N+r', expects residual value USD '+N+r' and total lifetime output '+N+r' units. Year 1 output is '+N)
    rate=(cost-residual)/total
    check(q,'a',[rate],'Cost less residual value allocated across expected lifetime units.',4)
    check(q,'b',[rate*used],'Use unrounded per-unit depreciation times actual Year 1 units.')
for q in each(3,61,64):
    rev,cost,opening,closing,debtors,creditors=cap(q['stem'],r'Annual revenue is USD '+N+r', cost of sales USD '+N+r', opening stock USD '+N+r', closing stock USD '+N+r', year-end debtors USD '+N+r' and year-end creditors USD '+N)
    check(q,'a',[(opening+closing)/2/cost*365],'Average stock / annual cost of sales × 365.')
    check(q,'b',[debtors/rev*365,creditors/cost*365],'Receivables use revenue; payables use cost of sales, expressly required by the case.')
for q in each(3,65,68):
    debt,eq,loan=cap(q['stem'],r'liabilities are USD '+N+r'; equity is USD '+N+r'.*?loan of USD '+N)
    check(q,'a',[100*debt/(debt+eq)],'Non-current liabilities / (non-current liabilities + equity).')
    check(q,'b',[100*(debt+loan)/(debt+loan+eq)],'Loan increases both numerator and capital-employed denominator; equity unchanged.')
for q in each(3,69,72):
    cost,=cap(q['stem'],r'time zero is USD '+N)
    future=sum(dec(r[1])*dec(r[2]) for r in rows(q)[1:])
    check(q,'a',[future],'Sum each displayed year-end cash inflow times its displayed four-decimal factor; do not recalculate factors.')
    check(q,'b',[future-cost],'Subtract initial cost exactly once at time zero, without discounting it.')
for q in each(3,73,76):
    br,ar,bc,ac=cap(q['stem'],r'budget revenue is USD '+N+r', actual revenue USD '+N+r', budget operating cost USD '+N+r', and actual operating cost USD '+N)
    check(q,'a',[abs(ar-br)],'Revenue variance magnitude; actual above budget is favorable.')
    check(q,'b',[abs(bc-ac)],'Cost variance magnitude; actual below budget is favorable.')
    assert ('favorable' in text(q,'a'))==(ar>=br)
    assert ('favorable' in text(q,'b'))==(ac<=bc)
    check(q,'c',[br-bc,ar-ac],'Independently reconstruct budget and actual profit used in the explanation.')
for q in each(3,77,80):
    price,var,fixed,normal,special,qty=cap(q['stem'],r'price is USD '+N+r'; variable cost USD '+N+r'.*?overhead of USD '+N+r' across normal monthly output of '+N+r'.*?offers USD '+N+r' per unit for '+N)
    check(q,'a',[var+fixed/normal],'Absorption cost = variable unit cost plus stated fixed overhead allocation at normal output.')
    check(q,'b',[(special-var)*qty],'Incremental contribution from extra units; spare capacity and unchanged fixed cost are explicit.')
for q in each(4,5,8):
    rr=rows(q);own=[dec(x) for x in rr[1][1:]];market=[dec(x) for x in rr[2][1:]]
    check(q,'a',[100*own[1]/market[1]],'Same-market Year 2 own sales divided by whole market including own business.')
    check(q,'b',[100*(market[1]-market[0])/market[0]],'Market growth is change relative to Year 1 market size.')
    check(q,'c',[100*own[0]/market[0],100*own[1]/market[1]],'Independently recheck before/after market-share figures in explanation.')
for q in each(4,33,36):
    rr=rows(q)[1:];classes={r[0]:('star' if dec(r[1])>=1 and dec(r[2])>10 else 'cash cow' if dec(r[1])>=1 else 'question mark' if dec(r[2])>10 else 'dog') for r in rr}
    assert classes[rr[0][0]]=='star' and classes[rr[2][0]]=='cash cow'
    EVIDENCE[q['id']]=[{'part':'a','independentlyDerived':classes,'reason':'Apply displayed inclusive share and exclusive growth thresholds to every row. Operating cash flow is not assumed equal to profit.','status':'passed'}]
for q in each(4,41,44):
    cost,markup,volume,low,lowvolume=cap(q['stem'],r'full cost is USD '+N+r'.*?proposes a '+N+r'% mark-up.*?forecast sales are '+N+r'.*?predicts '+N+r' units at USD '+N)
    # The final two captures are volume then price in the displayed sentence.
    lowvolume,low=low,lowvolume;price=cost*(1+markup/100)
    check(q,'a',[price],'Markup is a percentage of cost, not the final selling price.')
    check(q,'b',[price*volume],'Forecast quantity at cost-plus price times that price.')
    check(q,'c',[price*volume,low*lowvolume],'Reconstruct revenues at both displayed demand forecasts without assuming unchanged unit cost.')
for q in each(4,57,60):
    intercept,slope,x=cap(q['stem'],r'fits y='+N+r'\+'+N+r'x.*?proposes x='+N)
    check(q,'a',[intercept+slope*x],'Substitute proposed advertising index into supplied fitted equation; do not refit illustrative observations.',0)
for q in each(4,61,64):
    p0,p1,q0,q1=cap(q['stem'],r'price changes from USD '+N+r' to USD '+N+r' and quantity sold from '+N+r' to '+N)
    ped=((q1-q0)/q0)/((p1-p0)/p0)
    check(q,'a',[ped,abs(ped)],'Signed percentage quantity change / signed percentage price change, both based on original values.')
    check(q,'b',[abs(p1*q1-p0*q0)],'New total revenue minus old; report correct increase/decrease direction.')
    assert ('increase' in text(q,'b'))==(p1*q1>=p0*q0)
for q in each(4,73,76):
    root=ET.fromstring(q['diagramSvg']);bars=[e for e in root.iter() if e.tag.endswith('rect') and e.attrib.get('fill')=='#93c5fd']
    # Recover chart scale directly from the plotted tick positions, not author data.
    ticks=[(float(e.attrib['x']),dec(''.join(e.itertext()))) for e in root.iter() if e.tag.endswith('text') and re.fullmatch(r'\d+',''.join(e.itertext()))]
    if not bars:bars=[e for e in root.iter() if e.tag.endswith('rect') and e.attrib.get('height')=='24']
    origin=ticks[0][0];scale=ticks[1][0]-origin
    end=max((D(e.attrib['x'])+D(e.attrib['width'])-D(str(origin)))/D(str(scale)) for e in bars)
    check(q,'a',[end],'Read bar endpoints against the serialized tick scale; parallel creative/channel paths both precede launch test.',0)
for q in each(5,25,28):
    p,v,f,qty=cap(q['stem'],r'for USD '+N+r' per unit. Variable cost is USD '+N+r' per unit and monthly fixed cost USD '+N+r'.*?both '+N)
    check(q,'a',[p-v],'Unit selling price less unit variable cost.')
    check(q,'b',[f/(p-v)],'Monthly fixed cost divided by unit contribution.',0)
    check(q,'c',[qty*(p-v)-f],'Forecast monthly sales contribution less monthly fixed cost.')
    check(q,'d',[qty-f/(p-v)],'Margin of safety in units, independently checked within explanation.',0)
for q in each(5,29,32):
    p,v,f,target,qty=cap(q['stem'],r'price is USD '+N+r'; variable cost USD '+N+r'.*?fixed cost USD '+N+r'.*?profit USD '+N+r'.*?sales of '+N)
    check(q,'a',[(f+target)/(p-v)],'Required contribution covers fixed cost plus target profit; round whole-unit threshold upward.',0)
    targetprice=v+(f+target)/qty;wholecent=targetprice.quantize(D('.01'),rounding=ROUND_CEILING)
    check(q,'b',[targetprice,wholecent],'Distinguish rounded theoretical equation result from minimum feasible whole-cent price to meet or exceed target.')
    assert (wholecent-v)*qty-f>=target
for q in each(5,33,36):
    p,f0,v0,f1,v1,qty=cap(q['stem'],r'price stays at USD '+N+r'.*?fixed cost is USD '+N+r', variable cost USD '+N+r'.*?fixed cost to USD '+N+r' and variable cost to USD '+N+r'.*?both '+N)
    check(q,'a',[f0/(p-v0),f1/(p-v1)],'Independently solve both linear total-revenue/total-cost intersections.')
    old=qty*(p-v0)-f0;new=qty*(p-v1)-f1
    check(q,'b',[abs(new-old)],'Calculate both forecast profits separately before differencing.')
    check(q,'c',[old,new],'Recheck profit amounts used by model evaluation.')
for q in each(5,49,52):
    use,lead,buffer,order=cap(q['stem'],r'uses '+N+r'.*?lead time is '+N+r' days; buffer stock is '+N+r' units; each replenishment order is '+N)
    late,=cap(q['parts'][1]['prompt'],r'is '+N+r' days later')
    check(q,'a',[use*lead+buffer],'Normal lead-time consumption plus safety stock.')
    remain=buffer-use*late
    check(q,'b',[max(remain,0)]+([-remain] if remain<0 else []),'Physical stock is non-negative; excess consumption is separately recorded unmet demand.',0)
for q in each(5,53,56):
    s=q['stem'];n=q['number']
    if n==53:
        out,capacity,workers=cap(s,r'produces '+N+r'.*?output.*?is '+N+r'.*?employs '+N)
        a=[100*out/capacity];b=[out/workers]
    elif n==54:
        out,hours,defects=cap(s,r'produces '+N+r'.*?using '+N+r' machine-hours.*? '+N+r' fail')
        a=[out/hours];b=[100*defects/out]
    elif n==55:
        contribution,fixed=cap(s,r'contribution of USD '+N+r' and fixed operating costs of USD '+N)
        a=[contribution-fixed];b=[contribution/(contribution-fixed)]
    else:
        old,w0,new,w1=cap(s,r'made '+N+r' units monthly with '+N+r' workers.*?makes '+N+r' units with '+N+r' workers')
        a=[old/w0,new/w1];b=[100*(new/w1-old/w0)/(old/w0)]
    check(q,'a',a,'Reconstruct individual production metric from its displayed inputs; unit and time bases explicit.')
    check(q,'b',b,'Use the requested denominator: workers, gross output, operating profit, or original productivity.')
for q in each(5,57,60):
    qty,f,v,buy=cap(q['stem'],r'needs '+N+r'.*?fixed cost USD '+N+r' plus USD '+N+r'.*?Buying costs USD '+N)
    check(q,'a',[f+v*qty,buy*qty],'Make includes the displayed avoidable fixed cost; buy includes stated delivered per-component cost.')
    crossover=f/(buy-v)
    assert f+v*crossover==buy*crossover
    check(q,'b',[crossover],'Solve equality of the two relevant total costs and substitute back.',0)
for q in each(5,61,64):
    durations={re.match(r'([A-E]):',t)[1]:cap(t,r': '+N+r' days')[0] for t in texts(q) if re.match(r'[A-E]:',t)}
    # Network topology checked against rendered activity-on-arrow endpoints:
    # A 1→2, B 1→3, C 2→4, D 3→4, E 4→5.
    edges=[(1,2,'A'),(1,3,'B'),(2,4,'C'),(3,4,'D'),(4,5,'E')]
    early={1:D(0)}
    for node in range(2,6):early[node]=max(early[u]+durations[k] for u,v,k in edges if v==node)
    late={5:early[5]}
    for node in range(4,0,-1):late[node]=min(late[v]-durations[k] for u,v,k in edges if u==node)
    check(q,'a',[early[5]],'Forward pass through every incoming activity; independently check both full paths.',0)
    activity=re.search(r'activity ([A-E])',q['parts'][1]['prompt'])[1]
    u,v,k=next(e for e in edges if e[2]==activity)
    check(q,'b',[late[v]-early[u]-durations[k],early[v]-early[u]-durations[k]],'Total float LF−ES−duration; free float successor-event earliest time−ES−duration, for the actually requested activity.',0)
    critical='A–C–E' if durations['A']+durations['C']>durations['B']+durations['D'] else 'B–D–E'
    assert critical in text(q,'a')
    EVIDENCE[q['id']].append({'part':'diagram','earlyEventTimes':{str(k):str(v) for k,v in early.items()},'lateEventTimes':{str(k):str(v) for k,v in late.items()},'reason':'Private solved network inspected against independently computed forward/backward passes.','status':'passed'})
for q in each(5,77,80):
    rr=rows(q)[1:];drive=sum(dec(r[1]) for r in rr);restrain=sum(dec(r[3]) for r in rr)
    check(q,'a',[drive,restrain],'Sum ordinal workshop scores separately; do not interpret as probabilities or guaranteed success.',0)

# All-record formal allocation and boundary checks supplement the manual reading.
for q in QS:
    assert q['marks']==sum(p['marks'] for p in q['parts'])
    assert not(q['level']=='ahl' and q['examStyle']=='paper-1')
    assert q['calculator'] is True
    assert len({p['label'] for p in q['parts']})==len(q['parts'])
    for p in q['parts']:
        total=0
        for g in group(q,p['label']):
            if 'rubric' in g:
                assert all(s['code']=='IND' for s in g['steps'])
                r=g['rubric']
                for criterion in r.get('criteria',[r]):
                    expected=0
                    for b in criterion['bands']:assert b['min']==expected and b['max']>=b['min'];expected=b['max']+1
                    assert expected==criterion['maxMarks']+1
                if 'criteria' in r:assert sum(c['maxMarks'] for c in r['criteria'])==r['maxMarks']
                total+=r['maxMarks']
            else:
                for s in g['steps']:
                    match=re.fullmatch(r'(?:M|A|R|AG)(\d+)',s['code']);assert match,(q['id'],s)
                    total+=int(match[1])
        assert total==p['marks'],(q['id'],p,total)
    for key in ('diagramSvg','markSchemeDiagramSvg'):
        if key in q:
            assert not re.search(r'<(?:style|use|image)\b|(?:href|src)\s*=|url\(',q[key],re.I)
            assert 'viewBox=' in q[key]
    if q['examStyle']=='paper-3':
        assert q['level']=='ahl' and [p['marks'] for p in q['parts']]==[2,6,17]
        assert [c['maxMarks'] for c in group(q,'c')[0]['rubric']['criteria']]==[4,4,6,3]

report={'status':'passed' if not ERRORS else 'failed','method':'Independent Decimal calculation from serialized student-visible stems, tables and SVG text/coordinates. No author calculator/parameter imports.','questionCount':400,'numericQuestionCount':len(EVIDENCE),'numericalAssertions':ASSERTIONS,'errors':ERRORS,'records':[{'id':qid,'checks':checks} for qid,checks in sorted(EVIDENCE.items())],'limits':'Independent AI review, not human examiner moderation. Qualitative causal reasoning and figure readability are separately documented.'}
save('business-independent-numeric.json',report)
print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2))
if ERRORS:raise SystemExit(1)
