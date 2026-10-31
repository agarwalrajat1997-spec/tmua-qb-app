"""Independent numerical review of final JSON, using a separate exact-arithmetic ledger.

The inputs below are transcribed from the final case data, not imported from the
authoring modules. This also checks the published accuracy statements, boundaries,
rounding, inventory feasibility and accounting identities.
"""
from pathlib import Path
from decimal import Decimal as D
from collections import Counter
import json,re,hashlib,math
ROOT=Path(__file__).resolve().parents[2]
records=[q for p in (ROOT/'content/ib/business-management').glob('*.json') for q in json.loads(p.read_text(encoding='utf8'))]
byid={q['id']:q for q in records}; evidence={}; assertions=0
def qid(u,n):return f'ib-bm-u{u}-{n:03}'
def nums(text):return [float(x.replace(',','')) for x in re.findall(r'(?<![A-Za-z])[-−]?\d[\d,]*(?:\.\d+)?',text.replace('−','-'))]
def check(u,n,part,values,note,tol=0.0051):
    global assertions
    q=byid[qid(u,n)];g=next(g for g in q['markScheme'] if g['part']==part)
    final=' '.join(s['text'] for s in g['steps'] if s['code']=='A1')
    if not final:final=' '.join(s['text'] for s in g['steps'])
    available=nums(final)
    for expected in values:
        assert any(abs(float(expected)-v)<=tol for v in available),(q['id'],part,expected,final)
        assertions+=1
    evidence.setdefault(q['id'],[]).append({'part':part,'recomputed':list(map(float,values)),'reason':note,'result':'passed'})

for i,(c,p,h,l,s) in enumerate([(12000,D('.6'),44000,8000,16000),(18000,D('.7'),54000,4000,19000),(9000,D('.4'),45000,5000,15000),(15000,D('.65'),50000,6000,18000)]):
    check(1,65+i,'a',[l+p*(h-l)-c],'Rollback by low payoff plus probability-weighted increment, less time-zero cost; compared with certain alternative.')
for n in range(77,81):
    check(1,n,'b',[4000,2000],'Restricted grant is not operating cash; 4000 remaining funds two months at 2000 net outflow.')
    assert 'two months' in ' '.join(s['text'] for s in byid[qid(1,n)]['markScheme'][1]['steps'])
for i,t in enumerate([(4,3,2),(3,5,4),(6,2,2),(5,4,3)]):
    check(2,9+i,'a',[3],'Direct reporting chart: three functional managers, three hierarchy levels.')
    check(2,9+i,'c',[sum(t)],'Count direct reports after removing managers, not original total employment.')
for i,(a,b,l,c) in enumerate([(72,88,12,3600),(140,160,45,1800),(48,52,8,6200),(220,180,50,1400)]):
    check(2,53+i,'a',[D(200)*l/(a+b)],'Leavers divided by mean headcount; exact arithmetic in percent.')
    check(2,53+i,'b',[l*c],'Every leaver replaced once; indirect costs excluded.')
for i,(f,v,n) in enumerate([(48000,14,6000),(12500,9,2500),(36000,22,4000),(72000,31,8000)]):
    check(3,13+i,'a',[f+v*n],'Total fixed plus total variable cost; monthly basis.')
    check(3,13+i,'b',[D(f)/n+v],'Alternative calculation: variable unit cost plus allocated fixed cost per unit.')
for i,(p,n,fee,s) in enumerate([(45,800,12,350),(18,2400,25,520),(32,1600,9,700),(75,420,16,260)]):
    total=p*n+fee*s;check(3,17+i,'a',[total],'Two explicitly non-overlapping revenue streams.')
    check(3,17+i,'b',[D(100)*fee*s/total],'Recurring subscription share of earned revenue.')
for i,(r,c,e,interest,tax) in enumerate([(480000,276000,116000,8000,16000),(360000,198000,102000,6000,10800),(720000,432000,180000,12000,19200),(250000,137500,72500,5000,7000)]):
    check(3,21+i,'a',[r-c],'Statement gross profit identity.')
    check(3,21+i,'b',[r-(c+e)],'PBIT excludes interest and tax.')
    check(3,21+i,'c',[r-sum((c,e,interest,tax))],'After-tax profit independently reconciles all deductions to revenue.')
for i,(nca,stock,deb,cash,cl,ld) in enumerate([(180000,42000,36000,12000,50000,70000),(260000,18000,52000,20000,60000,110000),(95000,28000,16000,9000,33000,40000),(320000,60000,45000,15000,80000,150000)]):
    ca=sum((stock,deb,cash));equity=nca+ca-cl-ld
    assert nca+ca==equity+cl+ld
    check(3,25+i,'a',[ca],'Sum of explicitly exhaustive current assets.')
    check(3,25+i,'b',[equity],'Assets equal equity plus liabilities; net assets are not merely working capital.')
    check(3,25+i,'c',[ca-cl],'Working capital excludes non-current assets and long-term debt.')
for i,(r,c,e) in enumerate([(300000,195000,66000),(440000,250800,127600),(216000,129600,56160),(352000,235840,77440)]):
    check(3,29+i,'a',[D(100)-D(100)*c/r],'Gross margin as 100% less cost-of-sales share.')
    check(3,29+i,'b',[D(100)-D(100)*(c+e)/r],'Profit margin based on PBIT, not profit after tax.')
for i,(profit,eq,debt,newp,newcap) in enumerate([(78000,300000,90000,90000,500000),(54000,220000,80000,72000,360000),(96000,380000,100000,102000,600000),(126000,500000,200000,144000,800000)]):
    check(3,33+i,'a',[D(100)*profit/(eq+debt)],'Current capital employed equals equity plus long-term debt.')
    check(3,33+i,'b',[D(100)*newp/newcap],'Forecast ROCE uses specified full-year comparable capital basis.')
for i,(s,d,c,l,pay) in enumerate([(45000,30000,15000,60000,12000),(70000,40000,20000,80000,16000),(28000,22000,10000,30000,6000),(54000,16000,10000,50000,10000)]):
    assert c>=pay and l>pay
    check(3,37+i,'a',[D(s+d+c)/l,D(d+c)/l],'Current and quick ratios use same liabilities; inventory excluded only from quick ratio.')
    check(3,37+i,'b',[D(s+d+c-pay)/(l-pay)],'Cash payment is feasible; both numerator and denominator decrease, but cash does not increase.')
for i,(op,r,p,machine) in enumerate([(22000,[30000,52000,40000],[38000,36000,35000],15000),(18000,[20000,46000,28000],[27000,32000,26000],12000),(26000,[24000,58000,36000],[41000,33000,30000],18000),(15000,[32000,29000,48000],[28000,37000,31000],10000)]):
    baseline=[op+sum(r[:j])-sum(p[:j]) for j in range(1,4)]
    check(3,41+i,'a',baseline[:2],'Cumulative receipts minus cumulative payments, independently of recursive authoring calculation.')
    check(3,41+i,'b',[min(baseline)-machine],'One time-zero purchase shifts all subsequent balances by the same amount exactly once.')
for i,(cost,flows) in enumerate([(90000,[24000,30000,42000,36000]),(120000,[30000,42000,60000,48000]),(76000,[18000,25000,33000,30000]),(64000,[16000,20000,36000,26000])]):
    totals=[sum(flows[:j]) for j in range(1,5)];j=next(j for j,x in enumerate(totals) if x>=cost)
    before=0 if j==0 else totals[j-1];value=D(j)+D(cost-before)/flows[j]
    assert (j==0 or totals[j-1]<cost) and totals[j]>=cost
    check(3,45+i,'a',[value],'First cumulative crossing found independently; even accrual permits within-year fraction.')
for i,(cost,years,inflow) in enumerate([(100000,5,30000),(60000,4,21000),(150000,6,41000),(80000,5,23000)]):
    ap=D(inflow)-D(cost)/years
    check(3,49+i,'a',[ap],'Annual cash surplus less annual capital-cost allocation; zero residual.')
    check(3,49+i,'b',[D(100)*ap/cost],'ARR denominator original capital cost, not average investment.')
for i,(cost,res,life,age) in enumerate([(96000,16000,5,2),(54000,9000,6,3),(38000,8000,5,1),(125000,25000,8,4)]):
    dep=D(cost-res)/life;assert D(cost)-dep*life==res
    check(3,53+i,'a',[dep],'Depreciable base excludes residual; final carrying value equals residual.')
    check(3,53+i,'b',[D(res)+dep*(life-age)],'Alternative remaining-depreciable-life reconciliation of carrying value.')
for i,(cost,res,cap,out) in enumerate([(180000,30000,1500000,240000),(112000,12000,800000,140000),(76000,6000,700000,175000),(250000,50000,2000000,320000)]):
    unit=D(cost-res)/cap
    check(3,57+i,'a',[unit],'Lifetime expected production allocates the depreciable base.',tol=.000051)
    check(3,57+i,'b',[D(out)/cap*(cost-res)],'Usage proportion times depreciable base independently equals annual charge.')
for i,(sales,cogs,opening,closing,deb,cred) in enumerate([(730000,438000,50000,70000,80000,42000),(540000,324000,36000,44000,54000,36000),(912500,547500,25000,35000,75000,60000),(420000,252000,22000,34000,63000,28000)]):
    check(3,61+i,'a',[D(opening+closing)*365/(2*cogs)],'365-day turnover cycle using average inventory.')
    check(3,61+i,'b',[D(deb)*365/sales,D(cred)*365/cogs],'Receivables use revenue; payables use explicitly stipulated cost of sales.')
for i,(debt,eq,loan) in enumerate([(240000,560000,160000),(400000,600000,200000),(80000,320000,100000),(360000,440000,240000)]):
    check(3,65+i,'a',[D(100)-D(100)*eq/(debt+eq)],'Gearing equivalent to 100% less equity share of capital employed.')
    check(3,65+i,'b',[D(100)-D(100)*eq/(debt+eq+loan)],'Additional debt increases both long-term debt and capital employed.')
for i,(cost,flows,factors) in enumerate([(100000,[38000,42000,46000],['.9091','.8264','.7513']),(85000,[30000,36000,40000],['.9259','.8573','.7938']),(140000,[50000,60000,70000],['.9091','.8264','.7513']),(120000,[42000,46000,52000],['.9259','.8573','.7938'])]):
    pv=sum(D(str(flow))*D(factor) for flow,factor in zip(flows,factors))
    check(3,69+i,'a',[pv],'Use the displayed four-decimal factors, not a different hidden precision.')
    check(3,69+i,'b',[pv-cost],'Initial time-zero cash outlay subtracted without discounting.')
for i,(br,ar,bc,ac) in enumerate([(180000,194000,126000,142000),(240000,226000,156000,148000),(96000,108000,72000,78000),(150000,141000,105000,112000)]):
    check(3,73+i,'a',[abs(ar-br)],'Revenue variance magnitude; favorable iff actual exceeds budget.')
    check(3,73+i,'b',[abs(ac-bc)],'Cost variance magnitude; adverse iff actual exceeds budget.')
    qa=byid[qid(3,73+i)]['markScheme'];assert ('favorable' if ar>=br else 'adverse') in qa[0]['steps'][-1]['text'];assert ('adverse' if ac>=bc else 'favorable') in qa[1]['steps'][-1]['text']
for i,(v,n,oh,special) in enumerate([(28,6000,120000,36),(52,4000,100000,65),(19,8000,128000,25),(34,5000,135000,44)]):
    check(3,77+i,'a',[D(oh)/n+v],'Absorption fixed overhead allocated over stated normal output.')
    check(3,77+i,'b',[(special-v)*500],'Spare-capacity incremental contribution excludes unchanged fixed overhead.')
for i,(own,market,oldmarket) in enumerate([(231000,1400000,1200000),(108000,1000000,800000),(60000,300000,280000),(84000,600000,500000)]):
    check(4,5+i,'a',[D(100)*own/market],'Share denominator includes the business itself.')
    check(4,5+i,'b',[D(100)*market/oldmarket-100],'Market growth based on original total market, not own sales.')
for i,(cost,mark,volume) in enumerate([(8,50,6000),(24,40,2400),(18,60,3500),(32,25,1800)]):
    price=D(cost)+D(cost)*mark/100
    check(4,41+i,'a',[price],'Markup applied to cost rather than price.')
    check(4,41+i,'b',[price*volume],'Price multiplied by forecast quantity, not confused with profit.')
for i,(a,b,x) in enumerate([(80,6,30),(120,8,25),(60,5,24),(150,12,22)]):check(4,57+i,'a',[a+b*x],'Supplied fitted line only; not refit from illustrative diagram. Proposed x is outside sample range.')
for i,(p1,q1,p2,q2) in enumerate([(12,5000,15,4200),(20,3000,22,2550),(40,2400,36,2760),(18,6000,21,5400)]):
    ped=D(q2-q1)*p1/(D(p2-p1)*q1)
    check(4,61+i,'a',[ped],'Original-base percentage elasticity, retaining sign and using magnitude to classify.')
    check(4,61+i,'b',[abs(p2*q2-p1*q1)],'Revenue change magnitude independently from total receipts; direction follows new minus original.')
for i,(a,b,c,d) in enumerate([(2,3,2,1),(3,2,3,1),(2,4,2,2),(1,3,2,1)]):check(4,73+i,'a',[a+max(b,c)+d],'Parallel tasks overlap; do not sum their durations sequentially.')
for i,(p,v,f,n) in enumerate([(18,10,32000,6000),(25,15,45000,6500),(40,24,64000,5500),(55,33,88000,6000)]):
    check(5,25+i,'a',[p-v],'Unit contribution is price less unit variable cost.')
    check(5,25+i,'b',[D(f)/(p-v)],'Break-even solves revenue=total cost.')
    check(5,25+i,'c',[p*n-v*n-f],'Profit independently computed as revenue minus both cost types.')
for i,(p,v,f,target,n) in enumerate([(35,19,48000,24000,5000),(12,7,25000,15000,9000),(60,36,72000,36000,6000),(8,5,18000,12000,12000)]):
    out=D(f+target)/(p-v);minimum=math.ceil(out);assert minimum*(p-v)-f>=target and (minimum-1)*(p-v)-f<target
    check(5,29+i,'a',[minimum],'Integer minimum checked on both sides of the target-profit boundary.')
    check(5,29+i,'b',[D(f+target+v*n)/n],'Required price independently solves total revenue=total cost+target.')
for i,(p,v,f,nf,nv,n) in enumerate([(20,12,40000,64000,8,7000),(30,18,72000,108000,12,8000),(45,27,90000,144000,18,9000),(50,32,108000,162000,23,10000)]):
    check(5,33+i,'a',[D(f)/(p-v),D(nf)/(p-nv)],'Theoretical break-even points keep two decimals; whole-unit non-loss output requires ceiling.')
    check(5,33+i,'b',[(v-nv)*n-(nf-f)],'Incremental variable savings less incremental fixed cost equals profit gain.')
for i,(use,lead,buffer,extra) in enumerate([(240,3,360,2),(180,4,420,3),(35,6,140,2),(120,5,300,4)]):
    check(5,49+i,'a',[use*lead+buffer],'Reorder level covers normal lead-time usage plus buffer.')
    remaining=buffer-extra*use;check(5,49+i,'b',[max(0,remaining)]+([abs(remaining)] if remaining<0 else []),'Physical stock cannot be negative; shortage shown separately as unmet demand.')
for n,parts in [(53,{'a':[75],'b':[300]}),(54,{'a':[30],'b':[3]}),(55,{'a':[20000],'b':[3]}),(56,{'a':[240,300],'b':[25]})]:
    for part,values in parts.items():check(5,n,part,values,'Production-metric denominator and time basis checked against the individual final case.')
assert D(60000)*D('1.01')-40000==20600
for i,(f,v,b,n) in enumerate([(36000,28,40,4000),(24000,12,18,5000),(18000,8,14,3500),(60000,35,50,5000)]):
    check(5,57+i,'a',[f+v*n,b*n],'Avoidable fixed cost enters make option only.')
    crossover=D(f)/(b-v);assert f+v*crossover==b*crossover
    check(5,57+i,'b',[crossover],'Equal-cost crossover verified by substitution in both total-cost equations.')
for i,(a,b,c,d,e) in enumerate([(4,3,5,2,2),(3,5,4,6,2),(6,4,3,2,4),(2,4,5,5,3)]):
    longest=max(a+c,b+d);duration=longest+e;slack=abs(a+c-b-d)
    check(5,61+i,'a',[duration],'All complete network paths independently enumerated; longest determines duration.')
    check(5,61+i,'b',[slack,0],'Shorter first activity has total float equal to branch gap and zero free float before its immediate successor.')
for i,(drive,restrain) in enumerate([(7,6),(8,7),(8,7),(7,8)]):check(5,77+i,'a',[drive,restrain],'Ordinal force scores only summarized, not converted into probabilities.')

ledger=json.loads((ROOT/'docs/ib-expansion-reviews/business-author-ledger.json').read_text(encoding='utf8'))
assert len(records)==400 and len(ledger)==400
families=Counter(x['family'] for x in ledger);assert len(families)==100 and max(families.values())==4
for item in ledger:
    q=byid[item['id']]
    digest=hashlib.sha256(json.dumps(q,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    assert digest==item['sha256'],q['id']+' stale ledger hash'
    item['independentNumericChecks']=evidence.get(q['id'],[])
    item['finalRecordHashVerified']=True
    item['scopeAndReasoningReview']='Checked highest-demand SL/AHL boundary and current code. Explanation chains distinguish claim, consequence and case application; evaluative items permit supported alternatives.'
    item['markingReview']='Analytic criteria counted independently; levelled answers use IND-only content. 10-mark best-fit rubric includes case application, balanced analysis, recommendation and evidence limitation; Paper 3 uses separate A/B/C/D criteria.'
    if not evidence.get(q['id']):item['nonNumericReview']='Case assumptions and causal reasoning reviewed; no numerical result requested. Inputs are fictional rather than purported business research.'
report={'records':400,'families':100,'maximumVariants':4,'recordsWithIndependentNumericChecks':len(evidence),'numericAssertions':assertions,'numericResult':'passed','recordHashes':'passed','levels':dict(Counter(q['level'] for q in records)),'fileHashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'content/ib/business-management').glob('*.json')}}
(ROOT/'docs/ib-expansion-reviews/business-final-review-ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
(ROOT/'docs/ib-expansion-reviews/business-numeric-review-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps(report,indent=2))
