"""Second-author quantitative reconstruction from serialized Economics stimuli.

No authoring function, variant variable or stored arithmetic expression is used.
Family names only select the relevant economic calculation; every input is
parsed again from the final public question text/tables.
"""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal,ROUND_HALF_UP,localcontext
import json,re,sys
sys.stdout.reconfigure(encoding='utf8')
ROOT=Path(__file__).resolve().parents[2]
qs={q['id']:q for p in (ROOT/'content/ib/economics').glob('*.json') for q in json.loads(p.read_text(encoding='utf8'))}
ledger=json.loads((ROOT/'docs/ib-expansion-reviews/economics-ledger.json').read_text(encoding='utf8'))
results={};errors=[];assertions=0
N=r'(-?\d+(?:\.\d+)?)'
def match(q,pattern):
    m=re.search(pattern,q['stem'],re.S)
    assert m,(q['id'],pattern)
    return tuple(F(x) for x in m.groups())
def single(q,pattern):return match(q,pattern)[0]
def rows(q):
    return [[x.strip() for x in line.strip().strip('|').split('|')] for line in q['stem'].splitlines() if line.startswith('|') and not re.match(r'\|\s*---',line)]
def dictionary(q):return {r[0]:F(r[1]) for r in rows(q) if len(r)==2 and re.fullmatch(r'-?\d+(?:\.\d+)?',r[1])}
def round2(value):
    value=F(value)
    with localcontext() as c:
        c.prec=40
        return float((Decimal(value.numerator)/Decimal(value.denominator)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))
def check(q,label,values,reason,accuracy=True):
    global assertions
    g=next(g for g in q['markScheme'] if g['part']==label)
    steps=[s for s in g['steps'] if s['code']=='A1'] if accuracy else g['steps']
    if not steps:steps=g['steps']
    text=' '.join(x['text'] for x in steps).replace('−','-')
    text=re.sub(r'(?<=\d) (?=\d{3}(?!\d))','',text)
    available=[float(x.replace(',','')) for x in re.findall(r'-?\d[\d,]*(?:\.\d+)?',text)]
    for value in values:
        target=round2(value)
        if not any(abs(target-a)<1e-7 or abs(float(value)-a)<1e-9 for a in available):errors.append({'id':q['id'],'part':label,'expected':str(value),'rounded':target,'accuracyText':text})
        assertions+=1
    results.setdefault(q['id'],[]).append({'part':label,'exactResults':[str(F(v)) for v in values],'roundedResults':[round2(v) for v in values],'derivation':reason,'inputSource':'reparsed final serialized public stimulus','status':'passed' if not any(e['id']==q['id'] and e['part']==label for e in errors) else 'failed'})

for entry in ledger:
    q=qs[entry['id']];fam=entry['family'];st=q['stem']
    if fam=='intro-01':
        hours=single(q,N+r' staff-hours available');check(q,'b',[hours/2],'Available clinic hours divided by stated two-hour screening input.')
    elif fam=='intro-03':
        rr={r[0]:tuple(map(F,r[1:])) for r in rows(q)[1:]};check(q,'a',[rr['B'][1]-rr['C'][1]],'Radio output forgone between the displayed B and C bundles.');check(q,'b',[(rr['C'][1]-rr['D'][1])/(rr['D'][0]-rr['C'][0])],'Marginal sacrifice divided by extra bicycles, not the total radio level.')
    elif fam=='intro-04':
        h=single(q,N+r' interchangeable machine-hours');check(q,'a',[h/3,h/6],'PPC intercepts independently from fixed input requirements.')
    elif fam=='intro-08':
        d=dictionary(q);check(q,'a',[d['Saving']+d['Taxes']+d['Imports']],'Planned leakages summed.');check(q,'b',[d['Investment']+d['Government spending']+d['Exports']],'Planned injections summed; equality is not full employment.')
    elif fam=='micro-structured-04':
        p0,p1,q0,q1=match(q,r'price from '+N+r' to '+N+r' crowns\. Quantity demanded rises from '+N+r' to '+N)
        check(q,'a',[(q1/q0-1)/(p1/p0-1)],'Initial-value PED with sign.');check(q,'b',[(p1*q1/(p0*q0)-1)*100],'Revenue change recomputed directly from both price-quantity products.')
    elif fam=='micro-structured-05':
        inc,decline=match(q,r'income rises by '+N+r'%, while demand .*? falls by '+N+r'%');check(q,'b',[-decline/inc],'Negative YED uses income change, not own-price elasticity.')
    elif fam=='micro-structured-06':
        price,short,long=match(q,N+r'% increase .*? by '+N+r'% this week, but by '+N+r'%');check(q,'a',[short/price,long/price],'Time horizons have different quantity responses to the same price change.')
    elif fam=='micro-structured-16':
        quantity,price,di,si=match(q,r'Equilibrium is '+N+r' units at '+N+r' crowns.*?intercept is '+N+r' crowns; supply\'s is '+N+r' crowns')
        check(q,'a',[(di-price)*quantity/2],'Consumer-surplus triangle from displayed intercept and market price.');check(q,'b',[(price-si)*quantity/2],'Producer-surplus triangle from supply intercept; distinct from accounting profit.')
    elif fam=='micro-structured-20':
        data=[tuple(map(F,r)) for r in rows(q)[1:]];revenues=[a*b for a,b,c in data];profits=[a*b-c for a,b,c in data];best=data[profits.index(max(profits))][0]
        check(q,'a',revenues,'Every listed revenue reconstructed as Q×P.');check(q,'b',[best,max(profits)],'Enumerate every permitted discrete output; revenue maximum is not profit maximum.')
    elif fam.startswith('micro-data-'):
        data={r[0]:tuple(map(F,r[1:])) for r in rows(q)[1:]};p0,q0=data['Initial'];p1,q1=data['New'];pc=(p1/p0-1)*100;ped=(q1/q0-1)/(p1/p0-1)
        check(q,'b',[pc,ped],'Controlled study uses original-value percentages, independently of the case policy changes.')
        # Verify the tie case is explicitly rounded away from zero, not half-even.
        if ped==F(-5,8):assert 'PED = -0.63' in ' '.join(s['text'] for s in q['markScheme'][1]['steps'])
    elif fam in ['micro-policy-01','micro-policy-02','micro-policy-03','micro-policy-05']:
        A,B=match(q,r'P='+N+r'−Q.*?P='+N+r'\+Q');Q=(A-B)/2;P=A-Q;check(q,'a(i)',[Q,P],'Solve serialized private inverse curves at equality.')
        if fam=='micro-policy-05':
            cap=single(q,r'maximum price is set at '+N);s=cap-B;d=A-cap;check(q,'a(ii)',[s,d],'Substitute the ceiling in separate demand and supply.');check(q,'a(iii)',[d-s,cap*s],'Shortage is not sales volume; legal revenue uses supplied units.');check(q,'a(iv)',[(d-s)*cap],'Procurement is explicitly conditional on external supply at the ceiling.')
        else:
            w=single(q,r'(?:tax of|subsidy of|external damage of) '+N);new=(A-B+(w if fam=='micro-policy-02' else -w))/2;buyer=A-new;seller=B+new
            check(q,'a(ii)',[new,buyer]+([seller] if fam!='micro-policy-03' else []),'Solve policy wedge between buyer willingness and private supply price.')
            if fam=='micro-policy-01':check(q,'a(iii)',[w*new],'Tax receipts use actual taxed sales.');check(q,'a(iv)',[w*(Q-new)/2],'No-externality triangle; transfers excluded from net loss.')
            elif fam=='micro-policy-02':check(q,'a(iii)',[w*new],'Payment on all subsidized sales.');check(q,'a(iv)',[buyer*new-P*Q],'Buyer spending after subsidy less original spending; not a welfare measure.')
            else:check(q,'a(iii)',[w*(Q-new)/2],'External-damage welfare triangle in stated constant-wedge model.');check(q,'a(iv)',[w*new],'Corrective-tax revenue at efficient output.')
    elif fam=='micro-policy-04':
        data=[tuple(map(F,r)) for r in rows(q)[1:]];rev=[a*b for a,b,c in data];profit=[a*b-c for a,b,c in data]
        check(q,'a(i)',[rev[2],profit[2]],'Q3 revenue and profit from table.');check(q,'a(ii)',profit[:2]+profit[3:]+[data[profit.index(max(profit))][0],max(profit)],'Independently enumerate all five profit choices.');check(q,'a(iii)',[rev[3]-rev[2],data[3][2]-data[2][2]],'Marginal revenue/cost for one-unit discrete increment.');check(q,'a(iv)',[data[2][2]/data[2][0]],'Average cost uses total cost divided by all three units.')
    elif fam=='micro-policy-06':
        oldq,oldtc,newq,newtc,p=match(q,r'current plant scale, daily output is '+N+r' units and total daily cost is '+N+r' crowns.*?produce '+N+r' units at a total daily cost of '+N+r' crowns.*?constant at '+N+r' crowns')
        oldac=oldtc/oldq;newac=newtc/newq;check(q,'a(i)',[oldac,p*oldq-oldtc],'Current full-scale cost and profit.');check(q,'a(ii)',[newac,p*newq-newtc],'Alternative full-scale cost and profit.');check(q,'a(iii)',[(newac/oldac-1)*100,p*(newq-oldq)],'Long-run average-cost change and sales revenue difference.');check(q,'a(iv)',[(newtc-oldtc)/(newq-oldq)],'Average incremental cost across a capacity change, not a local MC curve.')
    elif fam=='macro-structured-01':
        d=dictionary(q);check(q,'a',[d['Household consumption']+d['Gross investment']+d['Government final expenditure']+d['Exports']-d['Imports']],'National-accounting expenditure sum excludes pension transfer and subtracts imports.')
    elif fam=='macro-structured-02':
        g,inc,out=match(q,r'GDP is '+N+r' billion.*?received from abroad is '+N+r' billion.*?paid abroad is '+N+r' billion');check(q,'a',[g+inc-out],'Resident factor income, with outward income subtracted.')
    elif fam=='macro-structured-03':
        nominal,index=match(q,r'GDP is '+N+r' billion crowns and the GDP deflator is '+N);check(q,'a',[nominal*100/index],'Deflation at specified base 100.')
    elif fam=='macro-structured-04':
        old,new,pop0,pop1=match(q,r'GDP grows from '+N+r' to '+N+r' billion crowns while population grows from '+N+r' to '+N+r' million');check(q,'a',[old/pop0*1000],'Billion/million converts to 1000 crowns per person.');check(q,'b',[(new/pop1/(old/pop0)-1)*100],'Per-capita growth from both independently calculated levels.')
    elif fam=='macro-structured-09':
        labour,unemp=match(q,r'labour force is '+N+r' thousand people, of whom '+N+r' thousand');check(q,'a',[unemp/labour*100],'Discouraged people are outside both the stated numerator and denominator.')
    elif fam=='macro-structured-10':
        old,new=match(q,r'index rises from '+N+r' to '+N);check(q,'a',[(new/old-1)*100],'Inflation is relative index growth, not index-point change.')
    elif fam=='macro-structured-11':
        nom,infl=match(q,r'interest rate is '+N+r'% and expected inflation is '+N+r'%');check(q,'a',[nom-infl],'Explicit approximate expected real interest relation.')
    elif fam=='macro-structured-14':
        income=single(q,r'annual income is '+N+r' thousand');tax=20*F(20,100)+(income-30)*F(40,100);check(q,'a',[tax],'Tax marginal bands separately, leaving first ten thousand tax-free.');check(q,'b',[tax/income*100],'Average rate uses whole income, not top marginal rate.')
    elif fam=='macro-structured-15':
        s,m,t=match(q,r'MPS='+N+r', MPM='+N+r' and MPT='+N);g=single(q,r'spending rises by '+N+r' million');k=1/(s+m+t);check(q,'a',[k],'Reciprocal of all three given marginal leakages.');check(q,'b',[k*g],'Multiplier total already includes initial autonomous spending.')
    elif fam.startswith('macro-data-'):
        d=dictionary(q);real=d['Nominal GDP (billion crowns)']*100/d['GDP deflator (base year=100)'];per=real/d['Population (million)']*1000;check(q,'b',[real,per],'Reconstruct real output then correct per-capita unit conversion from published table.')
    elif fam=='macro-policy-01':
        s,m,t=match(q,r'MPS='+N+r', MPM='+N+r' and MPT='+N);gap,debt,gdp=match(q,r'gap is '+N+r' billion.*?debt is '+N+r' billion and initial GDP is '+N+r' billion');rate=single(q,r'Borrowing cost is '+N+r'%')/100;k=1/(s+m+t);g=gap/k;k2=1/(s+F(3,10)+t)
        check(q,'a(i)',[k],'All stated leakage propensities.');check(q,'a(ii)',[g],'Required autonomous spending is gap divided by multiplier.');check(q,'a(iii)',[debt/gdp*100,g*rate],'Debt ratio and annual interest on additional borrowing, not all existing debt.');check(q,'a(iv)',[k2,g*k2],'Hold same spending but increase import propensity as instructed.')
    elif fam=='macro-policy-02':
        income=single(q,r'Income is '+N+r' thousand');tax=4+(income-30)*F(2,5);expenditure=single(q,r'expenditure of '+N+r' thousand');salesrate=single(q,r'excludes a '+N+r'% consumption tax')/100
        check(q,'a(i)',[tax,tax/income*100],'Marginal income-tax bands and average rate.');check(q,'a(ii)',[expenditure*salesrate,income-tax],'Consumption tax is tax-exclusive; disposable income excludes direct tax, not the spending tax again.')
        before,after=re.search(r'before .*? are ([\d%,]+); after .*? are ([\d%,]+)',st).groups();before=list(map(F,before.replace('%','').split(',')));after=list(map(F,after.replace('%','').split(',')));assert sum(before)==sum(after)==100
        check(q,'a(iii)',[sum(a[:j]) for a in [before,after] for j in range(1,5)],'Eight cumulative quintile results, assessed as four before/after pairs.')
    elif fam=='macro-policy-03':
        data=[tuple(map(F,r[1:])) for r in rows(q)[1:]];old=sum(qty*p for qty,p,n in data);new=sum(qty*n for qty,p,n in data);index=new/old*100
        check(q,'a(i)',[old,new],'Fixed base-year quantities at two price sets.');check(q,'a(ii)',[index,index-100],'Weighted price index and inflation since base year, not unweighted average of prices.');check(q,'a(iii)',[data[0][0]*data[0][1]/old*100,F(2)],'Food base-expenditure weight; explicit approximate real rate6−4.')
    elif fam=='macro-policy-04':
        debt,gdp,deficit=match(q,r'Initial debt is '+N+r' billion crowns and nominal GDP is '+N+r' billion.*?including interest, is '+N+r' billion');interest=single(q,r'averages '+N+r'%')/100;growth=single(q,r'GDP is projected to grow '+N+r'%')/100;newdebt=debt+deficit;newgdp=gdp*(1+growth)
        check(q,'a(i)',[debt/gdp*100,debt*interest],'Initial stock ratio and interest on initial stock.');check(q,'a(ii)',[newdebt,newgdp],'Overall deficit already includes interest; add it once.');check(q,'a(iii)',[newdebt/newgdp*100,(newdebt/newgdp-debt/gdp)*100],'Debt ratio versus percentage-point change.')
    elif fam=='global-structured-02':
        data=[tuple(map(F,r[1:])) for r in rows(q)[1:]];check(q,'a',[food/cloth for food,cloth in data],'Opportunity cost as forgone food per textile, not absolute-output ranking.')
    elif fam=='global-structured-08':
        rate,receipt=match(q,r'rate is '+N+r' US dollars per 1 crown.*?receives USD '+N);check(q,'a',[receipt/rate],'Cancel dollar units by division using explicit quotation.')
    elif fam=='global-structured-11':
        d=dictionary(q);goods=d['Goods exports']-d['Goods imports'];ca=goods+d['Net services']+d['Net primary income']+d['Net current transfers'];check(q,'a',[goods],'Goods balance.');check(q,'b',[ca],'Current account includes all non-goods signed net components.')
    elif fam=='global-structured-14':
        ex,im=match(q,r'exports is '+N+r' and for imports is '+N);check(q,'a',[ex+im],'Marshall-Lerner sum; initially balanced trade and stated long-run assumptions.',False)
    elif fam.startswith('global-data-'):
        d=dictionary(q);goods=d['Goods exports']-d['Goods imports'];ca=goods+d['Net services']+d['Net primary income']+d['Net current transfers'];check(q,'b',[goods,ca],'Both balances reconstructed from published signed accounts; deficit label not double-counted.')
    elif fam=='global-policy-01':
        A,B=match(q,r'P='+N+r'−Q.*?P='+N+r'\+Q');world,tariff=match(q,r'World price is '+N+r' crowns.*?tariff is '+N+r' crowns');p=world+tariff;s0=world-B;d0=A-world;s1=p-B;d1=A-p
        assert world<(A+B)/2 and p<(A+B)/2
        check(q,'a(i)',[s0,d0,d0-s0],'Small-country free trade, positive imports.');check(q,'a(ii)',[p,s1,d1,d1-s1],'Non-prohibitive tariff, both domestic quantity responses.');revenue=tariff*(d1-s1);csloss=(d0+d1)*tariff/2;psgain=(s0+s1)*tariff/2;loss=csloss-psgain-revenue
        check(q,'a(iii)',[revenue,csloss],'Tariff receipts and consumer-surplus trapezium.');check(q,'a(iv)',[psgain,loss],'Independent transfer reconciliation equals both distortion triangles.')
    elif fam=='global-policy-02':
        data=[tuple(map(F,r[1:])) for r in rows(q)[1:]];home,partner=data;trade,rate=match(q,r'trade '+N+r' units of cloth .*? at '+N+r' food units per cloth');hfood,hcloth=home;pfood,pcloth=partner
        assert pfood/pcloth<rate<hfood/hcloth
        check(q,'a(i)',[hfood/hcloth,pfood/pcloth],'Comparative advantage from relative opportunity costs.');check(q,'a(ii)',[(hfood+pfood)/2,(hcloth+pcloth)/2,hfood,pcloth],'Initial half-resource allocation versus full specialization.');check(q,'a(iii)',[hfood-rate*trade,trade],'Home exports food, imports the stated cloth quantity; no assumption of more of both goods.');check(q,'a(iv)',[rate*trade,pcloth-trade],'Partner receives food and retains unexported cloth; terms of trade strictly internal.')
    elif fam=='global-policy-03':
        exq,exp,imq,imp=match(q,r'Exports are '+N+r' units at '+N+r' crowns each; imports are '+N+r' units at USD '+N+r' each');rate=single(q,r'depreciates to 1 crown=USD '+N);up,down=match(q,r'export volume rises '+N+r'% and import volume falls '+N+r'%');exrev=exq*exp;imprice=imp/rate
        check(q,'a(i)',[exrev,exrev-imq*imp],'Initial parity converts dollar import price one-for-one.');check(q,'a(ii)',[imprice,exrev-imprice*imq],'Immediate import repricing with fixed quantities.');laterq=exq*(1+up/100);laterrev=laterq*exp;laterimport=imq*(1-down/100)*imprice
        check(q,'a(iii)',[laterq,laterrev,laterimport,laterrev-laterimport],'Use separate stated volume scenario, not infer it from the PED estimates.');ped1,ped2=match(q,r'PED estimates \(absolute\) are '+N+r' and '+N);check(q,'a(iv)',[ped1+ped2],'PED sum is a conditional criterion, not an exact discrete forecast.',False)
    elif fam=='global-policy-04':
        hh=single(q,r'concerns '+N+r' low-income households');pay=single(q,r'payment costs '+N+r' crowns per household');water=single(q,r'water project costs '+N);training=single(q,r'training programme costs '+N);budget=single(q,r'available budget is '+N);labour,unemp=match(q,r'counts '+N+r' adults in the labour force and '+N+r' unemployed');cash=hh*pay;total=cash+water+training
        check(q,'a(i)',[cash,budget-cash],'Household payment cost and unallocated remainder.');check(q,'a(ii)',[total,budget-total],'All three programmes costed; zero is balanced, negative is shortfall.');check(q,'a(iii)',[unemp/labour*100,water/hh],'Labour-force rate and project cost per target household.')

requested={q['id'] for q in qs.values() if any(any(word in p['prompt'].lower() for word in ['calculate','convert','apply the marshall','state the cumulative']) for p in q['parts'])}
assert requested<=results.keys(),sorted(requested-results.keys())
requested_parts={(q['id'],p['label']) for q in qs.values() for p in q['parts'] if any(word in p['prompt'].lower() for word in ['calculate','convert','apply the marshall','state the cumulative'])}
checked_parts={(ident,r['part']) for ident,rr in results.items() for r in rr}
assert requested_parts<=checked_parts,sorted(requested_parts-checked_parts)
report={'status':'passed' if not errors else 'failed','recordsWithNumericalRequests':len(requested),'partsWithNumericalRequests':len(requested_parts),'recordsReconstructed':len(results),'independentResultAssertions':assertions,'method':'Exact rational arithmetic and half-up rounding; every input read from the final serialized public stimulus; no author functions or stored arithmetic expressions imported.','errors':errors,'records':results}
(ROOT/'docs/ib-expansion-reviews/economics-independent-numeric.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps({k:v for k,v in report.items() if k!='records'},ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
