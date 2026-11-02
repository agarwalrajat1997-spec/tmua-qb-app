"""Original AI SL 2026 expansion. Deterministic authoring and numerical audit.
The question set is current-course (first assessment 2021), not the 2029 revision.
"""
import json, math, statistics, html
from pathlib import Path
from collections import Counter
R=Path(__file__).resolve().parents[2]
Q=[]; AUD=[]; counts=Counter()
T={'na':'number-algebra','fn':'functions','gt':'geometry-trigonometry','sp':'statistics-probability','ca':'calculus'}
def s(t): return html.escape(str(t))
def svg(body,title='Diagram'):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 380" role="img" aria-label="{s(title)}"><rect width="640" height="380" fill="white"/><g fill="none" stroke="#111" stroke-width="1.8">{body}</g></svg>'
def txt(x,y,t,size=15,anchor='middle'):
    return f'<text x="{x:.2f}" y="{y:.2f}" fill="#111" stroke="none" font-family="Arial,sans-serif" font-size="{size}" text-anchor="{anchor}">{s(t)}</text>'
def ytext(t):
    return '<text x="17" y="192" transform="rotate(-90 17 192)" fill="#111" stroke="none" font-family="Arial,sans-serif" font-size="13" text-anchor="middle">'+s(t)+'</text>'
def plot(title, pts=None, fn=None, domain=(0,10), yrange=None, xlabel='x',ylabel='y', scatter=False, extra=None):
    pts=pts or []
    if fn: pts=[(domain[0]+(domain[1]-domain[0])*i/180,fn(domain[0]+(domain[1]-domain[0])*i/180)) for i in range(181)]
    lo,hi=domain
    if yrange is None:
        vals=[p[1] for p in pts]
        if extra: vals.extend(y for _,ep in extra for _,y in ep)
        ylo=min(0,min(vals)); yhi=max(vals); pad=max((yhi-ylo)*.12,max(abs(yhi),abs(ylo))*.05,1e-8); yrange=(ylo,yhi+pad)
    yl,yh=yrange
    X=lambda x:110+460*(x-lo)/(hi-lo); Y=lambda y:320-245*(y-yl)/(yh-yl)
    b=txt(320,25,title,17)+f'<path d="M110 65V320H580"/>'+txt(325,370,xlabel)+ytext(ylabel)
    for i in range(6):
        x=lo+(hi-lo)*i/5;y=yl+(yh-yl)*i/5
        b+=f'<path d="M{X(x):.2f} 320v5M105 {Y(y):.2f}h5"/>'+txt(X(x),344,f'{x:.3g}',12)
        if not (yl<0<yh and abs(y)<.05*(yh-yl)): b+=txt(101,Y(y)+4,f'{y:.3g}',12,'end')
    if yl<0<yh:b+=f'<path stroke-dasharray="4 4" d="M110 {Y(0):.2f}H570"/>'+txt(101,Y(0)+4,'0',12,'end')
    if pts:
        if not scatter:b+='<polyline points="'+' '.join(f'{X(x):.2f},{Y(y):.2f}' for x,y in pts)+'"/>'
        if scatter or not fn:
            for x,y in pts:b+=f'<circle cx="{X(x):.2f}" cy="{Y(y):.2f}" r="3.5" fill="#111"/>'
    if extra:
        for label,ep in extra:
            b+='<polyline stroke-dasharray="6 4" points="'+' '.join(f'{X(x):.2f},{Y(y):.2f}' for x,y in ep)+'"/>'
            b+=txt(X(ep[-1][0]),Y(ep[-1][1])-10,label,13)
    return svg(b,title)
def bars(title,values,labels=None,ylabel='Frequency'):
    labels=labels or [str(i) for i in range(len(values))]; mx=max(values)*1.15
    b=txt(320,25,title,17)+'<path d="M65 60V320H590"/>'+ytext(ylabel)
    w=480/len(values)
    for i,v in enumerate(values):
        x=80+i*w;y=320-v/mx*235
        b+=f'<rect x="{x:.1f}" y="{y:.1f}" width="{w*.72:.1f}" height="{320-y:.1f}" fill="#e8e8e8"/>'+txt(x+w*.36,342,labels[i],12)+txt(x+w*.36,y-8,f'{v:.3g}',12)
    return svg(b,title)
def geom(title,pts,edges,labels=None,notes=None):
    xs=[p[0] for p in pts];ys=[p[1] for p in pts]
    scale=min(420/max(max(xs)-min(xs),1),230/max(max(ys)-min(ys),1))
    xoff=320-scale*(min(xs)+max(xs))/2
    X=lambda x:xoff+scale*x;Y=lambda y:300-scale*(y-min(ys))
    b=txt(320,25,title,17)
    for i,j in edges:b+=f'<path d="M{X(pts[i][0]):.1f} {Y(pts[i][1]):.1f}L{X(pts[j][0]):.1f} {Y(pts[j][1]):.1f}"/>'
    for i,(x,y) in enumerate(pts):b+=f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="3" fill="#111"/>'+txt(X(x)+9,Y(y)-12,(labels or [])[i] if labels else chr(65+i),14,'start')
    if notes:
        for i,n in enumerate(notes):b+=txt(320,335+i*19,n,13)
    return svg(b,title)
def flow(title,labels):
    b=txt(320,25,title,17)
    w=520/len(labels)
    for i,l in enumerate(labels):
        x=60+i*w;b+=f'<rect x="{x:.1f}" y="130" width="{w-16:.1f}" height="80"/>'+txt(x+(w-16)/2,164,l,13)
        if i<len(labels)-1:b+=f'<path d="M{x+w-15:.1f} 170h16m-5 -5l5 5-5 5"/>'
    b+=txt(320,285,'Read the timing and units given in the question.',13)
    return svg(b,title)
def table(rows,heads):
    return '\n\n| '+' | '.join(map(str,heads))+' |\n| '+' | '.join(['---']*len(heads))+' |\n'+'\n'.join('| '+' | '.join(map(str,r))+' |' for r in rows)+'\n\n'
def P(prompt,*steps):return (prompt,list(steps))
def M(t):return ('M1',t)
def A(t):return ('A1',t)
def Rr(t):return ('R1',t)
def add(t,title,sub,code,stem,parts,diagram,checks,summary=None):
    counts[t]+=1;n=700+counts[t];qid=f'ib-aisl-{t}-{n}'
    ps=[];ms=[]
    for i,(prompt,steps) in enumerate(parts):
        lab=chr(97+i);marks=sum(int(c[1:]) for c,_ in steps)
        ps.append(dict(label=lab,prompt=prompt,marks=marks));ms.append(dict(part=lab,steps=[dict(code=c,text=x) for c,x in steps]))
    tested=[]
    for label,actual,expected in checks:
        if isinstance(actual,bool): assert actual==expected,(qid,label,actual,expected)
        else: assert math.isclose(actual,expected,rel_tol=2e-6,abs_tol=2e-6),(qid,label,actual,expected)
        tested.append(dict(check=label,actual=actual,expected=expected,status='passed'))
    q=dict(id=qid,subject='math-ai-sl',topicId=T[t],collectionId='ai-sl-'+T[t],number=n,title=title,subtopic=sub,syllabusCode=code,level='sl',difficulty='medium' if counts[t]%2 else 'hard',calculator=True,marks=sum(x['marks'] for x in ps),stem=stem,parts=ps,markScheme=ms,source=dict(document='Independent syllabus-authored practice',question=n),status='published',examStyle='extended-response',diagramSvg=diagram,diagramCaption='Original mathematical diagram; use the stated data for calculations.',answerSummary=summary or ' '.join(x[1] for _,steps in parts for x in steps if x[0].startswith('A')),verification=dict(method='Author mathematical review and deterministic numerical checks',notes='Checked against current AI SL scope; diagram built from stated quantities. Audit: docs/ib-2026-maths/ai-sl-author-review.json.'))
    assert len(checks)>0 and len(ps)>=2
    Q.append(q);AUD.append(dict(id=qid,distinctProblem=title,checks=tested,scope='Current AI SL, first assessment 2021',review='Author self-review; independent review is a separate release gate.'))
def loan(PV,r,n):return PV*r/(1-(1+r)**(-n))
def bal(PV,r,A,n):return PV*(1+r)**n-A*((1+r)**n-1)/r
def bisect(f,a,b):
    assert f(a)*f(b)<=0
    for _ in range(100):
        m=(a+b)/2
        if f(a)*f(m)<=0:b=m
        else:a=m
    return (a+b)/2
def simpson(f,a,b,n=2000):
    h=(b-a)/n;return h/3*(f(a)+f(b)+4*sum(f(a+(2*i-1)*h) for i in range(1,n//2+1))+2*sum(f(a+2*i*h) for i in range(1,n//2)))
def mean(xs):return sum(xs)/len(xs)
def corr(x,y):
    ax=mean(x);ay=mean(y);return sum((a-ax)*(b-ay) for a,b in zip(x,y))/math.sqrt(sum((a-ax)**2 for a in x)*sum((b-ay)**2 for b in y))
N=statistics.NormalDist()

# NUMBER AND ALGEBRA — twenty distinct financial/numerical structures.
add('na','Extending a stepped auditorium','Sequences and series','1.2',
r'An auditorium has an arithmetic sequence of seats per row. Row 1 has 18 seats and row 6 has 33 seats. The sketch shows the first six rows.',
[P('Find the common difference and the number of seats in row 20.',M('Use $18+5d=33$.'),A('$d=3$ and $u_{20}=75$.')),
 P('Find the total capacity of the first 20 rows.',M('$S_{20}=20(18+75)/2$.'),A('$930$ seats.')),
 P('The fire certificate permits at most 1050 seats. Decide whether two more rows, following the pattern, can be added.',M('Rows 21 and 22 contain 78 and 81 seats.'),A('The proposed total is $1089$.'),Rr('It exceeds the limit by 39, so both rows cannot be added.'))],
bars('Seats in the first six rows',[18,21,24,27,30,33],list('123456'),'Seats'),
[('arithmetic sum',sum(18+3*k for k in range(20)),930),('extension',sum(18+3*k for k in range(22)),1089)])

n=math.ceil(math.log(.1)/math.log(.72));rem=800*.72**8
add('na','Flushing a storage tank','Sequences and series','1.3',
r'A tank initially contains 800 litres of contaminated water. Each complete flushing cycle removes 28% of the water present, after which the amount remaining is measured. No water is added during these cycles.',
[P('Write a formula for the amount remaining after $n$ cycles.',M('Each cycle multiplies the remaining amount by $1-0.28$.'),A('$V_n=800(0.72)^n$.')),
 P('Find the least number of complete cycles needed to leave less than 80 litres.',M('Solve $800(0.72)^n<80$.'),A('$n=8$; after 7 cycles there are about $80.2$ litres.')),
 P('Find the total amount removed in these eight cycles. Explain why summing eight equal removals would be incorrect.',M('Subtract the final amount from the initial amount.'),A(f'${800-rem:.6g}$ litres.'),Rr('Each removal is 28% of a decreasing amount, so the removed volumes are not equal.'))],
plot('Water remaining after each complete cycle',pts=[(i,800*.72**i) for i in range(6)],domain=(0,5),xlabel='Completed cycles',ylabel='Litres'),
[('threshold integer',n,8),('seven cycles above bound',800*.72**7>80,True),('mass balance',rem+(800-rem),800)])

eff=(1+.048/12)**12-1;v1=7000*(1+.048/12)**60;v2=7000*1.05**5
add('na','Comparing two advertised savings rates','Compound interest and depreciation','1.4',
r'Bank A advertises 4.8% nominal annual interest compounded monthly. Bank B pays 5.0% effective annual interest. A student invests 7000 currency units for five years without withdrawals.',
[P('Find Bank A’s effective annual interest rate.',M('Use $(1+0.048/12)^{12}-1$.'),A(f'${100*eff:.6g}\\%$.')),
 P('Calculate the maturity value at each bank.',M('Use 60 monthly periods for A and five annual periods for B.'),A(f'A: ${v1:.2f}$; B: ${v2:.2f}$.')),
 P('Bank B charges a single fee at maturity. Find the greatest fee that would leave B at least as good as A.',M('Subtract the two maturity values.'),A(f'${v2-v1:.2f}$ currency units; use unrounded balances before rounding.'),Rr('A greater fee would remove B’s advantage.'))],
flow('Two savings choices',['7000 invested','A: monthly','B: yearly','5-year maturity']),
[('effective-rate reconstruction',(1+eff)**5,(1+.048/12)**60),('B advantage positive',v2>v1,True)])

pay=loan(28000,.005,48);b12=bal(28000,.005,pay,12)
add('na','A loan and an early settlement','Annuities and loans','1.7',
r'A loan of 28000 is repaid by 48 equal monthly payments. Interest is 6% nominal per year compounded monthly. Payments occur at the end of each month. There are no fees.',
[P('Find the monthly payment.',M('Use $28000=A[1-(1.005)^{-48}]/0.005$.'),A(f'$A={pay:.2f}$. Retain the unrounded payment in later work.')),
 P('Find the balance immediately after the twelfth payment.',M('Use $B_{12}=28000(1.005)^{12}-A[(1.005)^{12}-1]/0.005$.'),A(f'${b12:.2f}$.')),
 P('The borrower settles the balance immediately after payment 12. Find the interest saved compared with completing the original schedule.',M('Compare $48A-28000$ with $12A+B_{12}-28000$.'),A(f'${36*pay-b12:.2f}$ saved.'),Rr('The settlement is after payment 12, so that payment must not be counted again.'))],
plot('Balance immediately after monthly payment',pts=[(i,bal(28000,.005,pay,i)) for i in range(0,49,6)],domain=(0,48),xlabel='Payments completed',ylabel='Balance'),
[('final amortisation',bal(28000,.005,pay,48),0),('balance recurrence',bal(28000,.005,pay,12),bal(28000,.005,pay,11)*1.005-pay)])

fv=1200*(1.04**8-1)/.04;dep=15000*.04/(1.04**8-1)
add('na','Saving at the end of each year','Annuities and loans','1.7',
r'A family deposits 1200 into an account at the end of each year for eight years. Interest is 4% effective per year. The eighth deposit has just been made.',
[P('Explain why the first deposit earns seven years of interest, and write the accumulated-value sum.',Rr('The first deposit is at the end of year 1 and the valuation is at the end of year 8.'),A('$1200(1+1.04+\\cdots+1.04^7)$.')),
 P('Find the account balance.',M('Use the finite geometric sum.'),A(f'${fv:.2f}$.')),
 P('Find the equal annual deposit needed to reach 15000 with the same timing. State an appropriate whole-unit standing order.',M('Solve $15000=D(1.04^8-1)/0.04$.'),A(f'$D={dep:.2f}$; a standing order of {math.ceil(dep)} ensures the target is reached.'),Rr('Round upwards because rounding down would miss the target.'))],
flow('Deposit timing',['Year 1: 1200','Year 2: 1200','...','Year 8: 1200']),
[('annuity sum',sum(1200*1.04**k for k in range(8)),fv),('required deposit',dep*sum(1.04**k for k in range(8)),15000)])

v7=36000*.85**3*.92**4;k=math.ceil(math.log(10000/(36000*.85**3))/math.log(.92))
add('na','A machine with changing depreciation','Compound interest and depreciation','1.4',
r'A machine costs 36000. Its value depreciates by 15% at the end of each of the first three years and by 8% at each subsequent year-end.',
[P('Find its value immediately after year 3 and after year 7.',M('Use different multipliers for the two periods.'),A(f'Year 3: ${36000*.85**3:.2f}$; year 7: ${v7:.2f}$.')),
 P('Find the first year-end at which the value is below 10000.',M('Solve $36000(0.85)^3(0.92)^k<10000$ for an integer $k\\geq0$.'),A(f'$k={k}$ subsequent years; first below 10000 at year {3+k}.')),
 P('A manager applies 23% depreciation every year by adding the percentages. Explain the error.',Rr('The rates apply in different years, not simultaneously to the same original value.'),Rr('Successive percentage changes multiply the current value; their percentages cannot simply be added.'))],
plot('Machine value at year-end',pts=[(i,36000*.85**min(i,3)*.92**max(0,i-3)) for i in range(9)],domain=(0,8),xlabel='Years',ylabel='Value'),
[('threshold previous',36000*.85**3*.92**(k-1)>=10000,True),('threshold attained',36000*.85**3*.92**k<10000,True)])

lower=18.35*12.65;upper=18.45*12.75
add('na','Can a rounded area guarantee enough paint?','Accuracy and approximation','1.6',
r'A rectangular wall is measured as 18.4 m by 12.7 m, each correct to the nearest 0.1 m. One tin covers exactly 47 square metres. Ignore wastage.',
[P('State the bounds for each true length and hence the bounds for the wall area.',M('Use half a rounding unit on each measurement.'),A(f'$18.35\\leq L<18.45$, $12.65\\leq W<12.75$; ${lower:.4f}\\leq A<{upper:.4f}$ square metres.')),
 P('A contractor buys five tins. Decide whether these are guaranteed sufficient.',M('Five tins cover $5(47)=235$ square metres.'),Rr(f'The upper area bound is {upper:.4f}, which is above 235, so five tins are not guaranteed sufficient.')),
 P('Find the least number of tins that guarantees sufficient coverage.',M('Use the upper bound, rather than the rounded measured area.'),A('$6$ tins.'))],
geom('Measured rectangular wall',[(0,0),(18.4,0),(18.4,12.7),(0,12.7)],[(0,1),(1,2),(2,3),(3,0)],['A','B','C','D'],['AB = 18.4 m; BC = 12.7 m','Both measurements to nearest 0.1 m']),
[('five tins insufficient',upper>235,True),('six tins enough',6*47>upper,True)])

joules=2.4e6*1.6e-4*86400;kwh=joules/3.6e6
add('na','A sensor network and its battery','Accuracy and approximation','1.1',
r'A monitoring network contains $2.4\times10^6$ sensors. Each sensor uses $1.6\times10^{-4}$ joules per reading and makes one reading each second. A battery stores 10 kWh, of which 90% is usable. Use $1\text{ kWh}=3.6\times10^6\text{ J}$.',
[P('Find the energy required for one day, in joules in scientific notation.',M('Multiply the number of sensors by energy per reading and 86400 seconds.'),A('$3.31776\\times10^7$ J.')),
 P('Decide whether one battery can power the network for a full day.',M('The requirement is $9.216$ kWh; usable battery energy is $9$ kWh.'),Rr('It cannot: the shortfall is $0.216$ kWh.')),
 P('Find the greatest whole number of sensors this battery could power for one day at the same sampling rate.',M('Solve $n(1.6\\times10^{-4})(86400)\\leq9(3.6\\times10^6)$; evaluate the integer boundary without floating-point round-off.'),A('$2343750$ sensors.'))],
flow('Daily energy budget',['Sensors','1 reading/s','86400 s','90% usable']),
[('daily kWh',kwh,9.216),('network total',joules,33177600),('exact maximum sensors',(9*3600000*100000)//(16*86400),2343750)])

add('na','Recovering three ticket prices','Systems of equations','1.8',
r'A venue sells adult, student and child tickets at fixed prices $a,s,c$. Three groups pay as follows.'+table([(2,3,1,79),(1,2,4,70),(3,1,2,80)],['Adults','Students','Children','Total paid']),
[P('Write a system of three equations for the prices.',A('$2a+3s+c=79$.'),A('$a+2s+4c=70$ and $3a+s+2c=80$.')),
 P('Solve the system and find the cost of two adult and two child tickets.',M('Solve the simultaneous equations using technology or elimination.'),A('$a=18$, $s=12$, $c=7$.'),A('The requested cost is $2(18)+2(7)=50$.')),
 P('A fourth group of one adult and two students paid 40. Explain why this is inconsistent with the pricing model.',M('The model predicts $18+2(12)=42$.'),Rr('The 2-unit discrepancy indicates a discount, an error, or a failure of the assumption of fixed prices.'))],
bars('Payments by the three groups',[79,70,80],['Group 1','Group 2','Group 3'],'Paid'),
[('group1',2*18+3*12+7,79),('group2',18+2*12+4*7,70),('group3',3*18+12+2*7,80)])

comb=10*math.log10(10**7+10**6.5)
add('na','Combining sound sources','Accuracy and approximation','1.5',
r'The sound level $L$ decibels is defined by $L=10\log_{10}(I/I_0)$, where $I_0$ is a fixed reference intensity. Two independent machines produce levels of 70 dB and 65 dB at the same point. Their intensities add.',
[P('Express each intensity as a multiple of $I_0$.',M('Rearrange the logarithmic definition.'),A('$I_1=10^7I_0$ and $I_2=10^{6.5}I_0$.')),
 P('Calculate the combined sound level.',M('Add intensities before taking the logarithm.'),A(f'${comb:.6g}$ dB.')),
 P('An engineer claims the combined level is 135 dB. Explain the error and determine the level produced by two identical 70 dB machines.',Rr('Decibels are logarithmic; adding levels does not add intensities.'),M('Use $10\\log_{10}(2\\times10^7)$.'),A(f'${10*math.log10(2e7):.6g}$ dB.'))],
bars('Individual sound levels',[70,65],['Machine 1','Machine 2'],'dB (log scale)'),
[('combined intensity recovery',10**(comb/10),1e7+10**6.5)])

add('na','An increasing maintenance budget','Sequences and series','1.2',
r'A school budgets 18000 for maintenance in year 1, increasing the annual budget by 1500 each year. A reserve of 180000 funds these annual budgets, with no interest earned.',
[P('Write an expression for the budget in year $n$ and for total spending through year $n$.',M('Use an arithmetic sequence with first term 18000 and difference 1500.'),A('$u_n=18000+1500(n-1)$; $S_n=\\frac n2[36000+1500(n-1)]$.')),
 P('Find the greatest number of complete years the reserve can fund.',M('Compare cumulative totals with 180000.'),A('$S_7=157500$ and $S_8=186000$, so 7 complete years.')),
 P('Find the additional money needed to fund year 8, and explain why dividing the reserve by 18000 overestimates the number of years.',A('$186000-180000=6000$.'),Rr('Later annual budgets exceed 18000, so ten identical first-year budgets are not a valid model.'))],
bars('Annual maintenance budgets',[18000+1500*i for i in range(8)],[str(i) for i in range(1,9)],'Budget'),
[('seven years',sum(18000+1500*i for i in range(7)),157500),('eight years',sum(18000+1500*i for i in range(8)),186000)])

add('na','Recycling a cooling fluid','Sequences and series','1.3',
r'A process recovers 82% of its cooling fluid after each use. Initially 500 litres are available. The recovered fluid is reused immediately, and no new fluid is added. Count the first use as use 1.',
[P('Find the volume available for use 6.',M('Five recoveries have occurred before use 6.'),A(f'$500(0.82)^5={500*.82**5:.6g}$ litres.')),
 P('Find the total volume passed through the process during the first ten uses.',M('Use $500[1-(0.82)^{10}]/(1-0.82)$.'),A(f'${500*(1-.82**10)/.18:.6g}$ litres.')),
 P('Find the first use for which less than 100 litres is available. Explain why the total processed volume can exceed 500 litres.',M('Solve $500(0.82)^{n-1}<100$ and choose the least integer.'),A(f'Use {math.floor(math.log(.2)/math.log(.82))+2}.'),Rr('The same recovered fluid is counted again on each use; this does not create new fluid.'))],
plot('Volume before each use',pts=[(i,500*.82**(i-1)) for i in range(1,9)],domain=(1,8),xlabel='Use number',ylabel='Litres'),
[('sum by iteration',sum(500*.82**i for i in range(10)),500*(1-.82**10)/.18)])

add('na','Repeated replacement in a saline tank','Sequences and series','1.3',
r'A 200-litre tank contains 12 kg of dissolved salt. Each cycle removes 40 litres of well-mixed solution and replaces it with 40 litres of pure water. Mixing is complete before the next cycle.',
[P('Explain why the mass of salt is multiplied by 0.8 each cycle.',M('The removed fraction of the mixture is $40/200=0.2$.'),Rr('The same fraction of salt is removed, leaving 80%; pure water adds no salt.')),
 P('Find the salt concentration after six cycles in grams per litre.',M('Mass is $12(0.8)^6$ kg; divide by 200 and convert kilograms to grams.'),A(f'${60*.8**6:.6g}$ g/L.')),
 P('Find the least number of cycles needed to reduce the concentration below 5 g/L.',M('Solve $60(0.8)^n<5$.'),A(f'${math.ceil(math.log(5/60)/math.log(.8))}$ cycles.'))],
flow('One replacement cycle',['200 L mixed','Remove 40 L','Add pure water','Mix again']),
[('salt six cycles',12*.8**6,3.145728),('threshold cycles',math.ceil(math.log(5/60)/math.log(.8)),12)])

add('na','Cash price versus instalments','Annuities and loans','1.7',
r'A bicycle has a cash price of 1800. An instalment plan requires a 300 deposit immediately and 24 end-of-month payments of 70. To compare the offers, use a monthly discount rate of 0.4%.',
[P('Find the total paid under the instalment plan.',M('Include the deposit and all 24 payments.'),A('$300+24(70)=1980$.')),
 P('Find the present value of the instalment plan.',M('Discount the payment annuity: $300+70[1-(1.004)^{-24}]/0.004$.'),A(f'${300+70*(1-1.004**-24)/.004:.2f}$.')),
 P('Find the greatest monthly payment that would make the plan no more expensive than the cash price on this basis.',M('Solve $300+A[1-(1.004)^{-24}]/0.004=1800$.'),A(f'The exact limiting payment is $1500(0.004)/[1-(1.004)^{{-24}}]$, approximately {1500*.004/(1-1.004**-24):.6f}; the greatest payment in whole cents is 65.67.'),Rr('Nominal total paid and present value answer different comparisons because timing matters.'))],
flow('Cash-flow timing',['Now: 300','Month 1: 70','...','Month 24: 70']),
[('present value direct',300+sum(70/1.004**k for k in range(1,25)),300+70*(1-1.004**-24)/.004)])

add('na','A weighted cost-of-living index','Accuracy and approximation','1.6',
r'A fixed basket allocates 40% of expenditure to food, 35% to housing and 25% to travel. Over a year the corresponding prices rise by 8%, 3% and 12%. The quantities in the basket remain fixed.',
[P('Find the percentage increase in the cost of this basket.',M('Weight the price multipliers: $0.40(1.08)+0.35(1.03)+0.25(1.12)$.'),A('$1.0725$, giving a $7.25\\%$ increase.')),
 P('A household spent 2400 per month on this basket last year. Find the new monthly cost and the annual increase.',M('Multiply 2400 by 1.0725.'),A('New cost $2574$; annual increase $12(174)=2088$.')),
 P('An analyst uses the unweighted mean increase of the three categories. Quantify the error in the predicted new monthly cost.',M('The unweighted increase is $(8+3+12)/3=7.666\\ldots\\%$.'),A('It predicts $2584$, which is $10$ too high per month.'),Rr('The spending shares are unequal, so equal weighting is unsuitable.'))],
bars('Basket expenditure weights',[40,35,25],['Food','Housing','Travel'],'Percent'),
[('weighted multiplier',.4*1.08+.35*1.03+.25*1.12,1.0725),('unweighted cost',2400*(1+(.08+.03+.12)/3),2584)])

r=.006;pv=12000;regular=loan(pv,r,36);over=regular+75;term=math.log(over/(over-pv*r))/math.log(1+r);lastn=math.ceil(term);pre=bal(pv,r,over,lastn-1);last=pre*(1+r)
add('na','Overpaying a monthly loan','Annuities and loans','1.7',
r'A loan of 12000 charges 0.6% interest per month. The original plan has 36 equal end-of-month payments. Instead, the borrower pays 75 more than the original payment each month until a smaller final payment clears the loan.',
[P('Find the original monthly payment and the increased payment.',M('Use the present value of a 36-payment annuity.'),A(f'Original ${regular:.2f}$; increased ${over:.2f}$. Use unrounded values.')),
 P('Find the month in which the loan is cleared and the final payment.',M('Solve for the non-integer term, then calculate the balance after the preceding whole number of payments.'),A(f'Term is {term:.6g} months; clear in month {lastn} with final payment ${last:.2f}$.')),
 P('Find the interest saved compared with the original plan.',M('New total is $(n-1)A+$ final payment.'),A(f'Interest saved: ${36*regular-((lastn-1)*over+last):.2f}$.'),Rr('Do not treat the final payment as a full increased instalment.'))],
plot('Balance under the original payment schedule',pts=[(i,bal(pv,r,regular,i)) for i in range(0,37,4)],domain=(0,36),xlabel='Months',ylabel='Original balance'),
[('last positive balance',pre>0,True),('full final overpayment unnecessary',last<over,True)])

withdraw=90000*.035/(1-1.035**-12)
add('na','Drawing down a retirement fund','Annuities and loans','1.7',
r'A retirement fund contains 90000. It earns 3.5% effective interest annually. Equal withdrawals are made at the end of each year for twelve years, leaving a zero balance immediately after withdrawal 12.',
[P('Find the annual withdrawal.',M('Use $90000=W[1-(1.035)^{-12}]/0.035$.'),A(f'${withdraw:.2f}$.')),
 P('Find the balance immediately after withdrawal 5.',M('Accumulate the original fund and subtract the accumulated first five withdrawals.'),A(f'${bal(90000,.035,withdraw,5):.2f}$.')),
 P('Annual inflation is 2.5%. Find the purchasing power of the final withdrawal in today’s currency units, and explain the loss in purchasing power.',M('Divide the final nominal withdrawal by $1.025^{12}$.'),A(f'${withdraw/1.025**12:.2f}$ in today’s currency units.'),Rr('A fixed nominal withdrawal buys less when the price level rises.'))],
flow('Retirement withdrawal timeline',['90000 now','Year 1: W','...','Year 12: W']),
[('fund exhausted',bal(90000,.035,withdraw,12),0),('annuity due',90000*1.035,93150)])

rate=(1.6)**(1/6)-1;double=math.log(2)/math.log(1+rate)
add('na','Growth measured across unequal intervals','Compound interest and depreciation','1.5',
r'A community’s electricity storage capacity rises from 250 MWh to 400 MWh in six years. A model assumes the same percentage growth at each year-end.',
[P('Find the annual percentage growth rate.',M('Solve $250(1+r)^6=400$.'),A(f'${100*rate:.6g}\\%$.')),
 P('Find the first year-end at which capacity is at least 500 MWh.',M('Solve $250(1+r)^n\\geq500$.'),A(f'$n\\geq{double:.6g}$, so year {math.ceil(double)}.')),
 P('A linear model instead adds 25 MWh each year. Compare the predictions after 12 years and explain one limitation shared by both models.',M('Exponential model: $250(1.6)^2$; linear model: $250+12(25)$.'),A('$640$ MWh versus $550$ MWh.'),Rr('Both assume the historic pattern continues despite possible funding, land or technology constraints.'))],
plot('Observed capacity endpoints',pts=[(0,250),(6,400)],domain=(0,12),yrange=(0,700),xlabel='Years',ylabel='MWh'),
[('growth endpoint',250*(1+rate)**6,400),('12-year capacity',250*(1+rate)**12,640)])

add('na','A profit estimate with rounded inputs','Accuracy and approximation','1.6',
r'A small manufacturer reports revenue of 84 thousand and cost of 79 thousand, each rounded to the nearest thousand. Profit is revenue minus cost.',
[P('Find the interval containing the true profit.',M('Use $83.5\\leq R<84.5$ and $78.5\\leq C<79.5$, in thousands.'),A('$4<P<6$ thousand; both endpoints are excluded.')),
 P('The reported profit is 5000. Find a sharp upper bound for its percentage error, measured relative to the true profit.',M('The greatest possible limiting relative error occurs as true profit approaches 4000.'),A('$100(5000-4000)/4000=25\\%$ is an upper bound; the actual error is less than this.')),
 P('Decide whether the business can guarantee profit of at least 4500 from these reports alone.',Rr('A true profit between 4000 and 4500 is consistent with the rounded figures.'),Rr('Therefore the guarantee cannot be made.'))],
bars('Rounded financial report (thousands)',[84,79],['Revenue','Cost'],'Thousands'),
[('profit infimum',83.5-79.5,4),('relative-error supremum',(5-4)/4,.25)])

add('na','Which currency-conversion order is cheaper?','Systems of equations','1.8',
r'A traveller converts $x$ units of currency A into currency B. Service P deducts a fee of 12 A first, then converts the remainder at 1.18 B per A. Service Q converts at 1.16 B per A, then deducts a fee of 5 B. Assume $x>12$.',
[P('Write expressions for the amount received from each service.',A('$P(x)=1.18(x-12)$.'),A('$Q(x)=1.16x-5$.')),
 P('Find the amount at which the two services give the same result.',M('Solve $1.18x-14.16=1.16x-5$.'),A('$x=458$ A; both give $526.28$ B.')),
 P('The traveller needs at least 1000 B. Find the minimum amount of A required using each service, and choose the cheaper one.',M('Solve $P(x)=1000$ and $Q(x)=1000$ separately.'),A(f'Unrounded thresholds are {1000/1.18+12:.6f} A for P and {1005/1.16:.6f} A for Q; minimum whole-cent payments are 859.46 A and 866.38 A respectively.'),Rr('P requires less A for this target, so choose P; round upwards to ensure the target.'))],
plot('Currency received by the two services',fn=lambda x:1.18*(x-12),domain=(100,900),xlabel='Currency A paid',ylabel='Currency B received',extra=[('Q',[(100,111),(900,1039)])]),
[('intersection P',1.18*(458-12),526.28),('intersection Q',1.16*458-5,526.28)])

# FUNCTIONS — calibration, inverse questions, model choice and restrictions.
add('fn','Calibrating a moisture sensor','Linear models','2.1',
r'A sensor gives a reading $y$ when the soil moisture is $x$ percent. Calibration measurements are $(10,2.4)$ and $(35,7.9)$. Assume a linear model, valid only for $5\leq x\leq45$.',
[P('Find the calibration equation.',M('Gradient is $(7.9-2.4)/(35-10)=0.22$.'),A('$y=0.22x+0.2$.')),
 P('Find the moisture corresponding to a reading of 6.25.',M('Solve $6.25=0.22x+0.2$.'),A('$x=27.5\\%$.')),
 P('A reading of 11 is obtained. Find the model’s implied moisture and explain why the reading cannot be reliably converted using this calibration.',M('The implied value is $(11-0.2)/0.22$.'),A('$49.1\\%$ to three significant figures.'),Rr('It lies outside the calibration domain; this is extrapolation beyond the stated validity.'))],
plot('Sensor calibration data',pts=[(10,2.4),(35,7.9)],domain=(0,50),xlabel='Moisture (%)',ylabel='Sensor reading'),
[('calibration point',.22*35+.2,7.9),('inverse',.22*27.5+.2,6.25)])

add('fn','An arch and a tall delivery vehicle','Quadratic models','2.6',
r'An arch is modelled by $h(x)=a(x-4)^2+8$ metres, with ground level $h=0$. Its left foot is at $x=0$ and its right foot at $x=8$. A rectangular vehicle is centred under the arch, is 3 m wide and 6.8 m high.',
[P('Find $a$.',M('Use $0=16a+8$.'),A('$a=-0.5$.')),
 P('Determine the clearance above the upper corners of the vehicle.',M('Corners are at $x=4\\pm1.5$; evaluate $h(2.5)$.'),A('The arch height is $6.875$ m, giving $0.075$ m clearance.')),
 P('A safety rule requires 0.20 m clearance at both upper corners. Find the greatest permitted vehicle width at height 6.8 m.',M('Solve $-0.5(x-4)^2+8=7.0$.'),A('The half-width is $\\sqrt2$ m, so maximum width is $2\\sqrt2=2.83$ m.'),Rr('The proposed 3 m width passes physically but fails the safety clearance.'))],
plot('Arch cross-section',fn=lambda x:-.5*(x-4)**2+8,domain=(0,8),yrange=(0,9),xlabel='Horizontal position (m)',ylabel='Height (m)',extra=[('vehicle',[(2.5,0),(2.5,6.8),(5.5,6.8),(5.5,0)])]),
[('corner height',-.5*(2.5-4)**2+8,6.875),('safety boundary',-.5*(math.sqrt(2))**2+8,7)])

k=math.log(.6)/10;t=math.log(10/60)/k
add('fn','Cooling with a non-zero background','Exponential models','2.6',
r'A drink cools in a room at 20 degrees Celsius. Its temperature after $t$ minutes is $T(t)=20+Ae^{kt}$. Initially it is 80 degrees Celsius, and after 10 minutes it is 56 degrees Celsius.',
[P('Find $A$ and $k$.',M('Use $T(0)=80$ and $36=60e^{10k}$.'),A(f'$A=60$, $k={k:.7f}$.')),
 P('Find when the drink first reaches 30 degrees Celsius.',M('Solve $10=60e^{kt}$.'),A(f'$t={t:.6g}$ minutes.')),
 P('Explain whether this model predicts the drink reaching 20 degrees Celsius in a finite time.',Rr('The exponential term is positive for every finite time.'),Rr('The temperature approaches 20 from above but never equals it at a finite time in this model.'))],
plot('Cooling model data',pts=[(0,80),(10,56)],domain=(0,40),yrange=(0,90),xlabel='Minutes',ylabel='Temperature (C)'),
[('cooling data',20+60*math.exp(k*10),56),('target',20+60*math.exp(k*t),30)])

add('fn','A boat and a tidal access window','Sinusoidal models','2.6',
r'The water depth at a harbour is $D(t)=4+2\cos[30(t-3)^\circ]$ metres, where $t$ is hours after midnight, $0\leq t\leq24$. The angle supplied to cosine is in degrees. A boat needs a depth of at least 5 m.',
[P('State the maximum depth, minimum depth and tidal period.',A('Maximum $6$ m and minimum $2$ m.'),M('The period is $360/30$.'),A('$12$ hours.')),
 P('Find all access intervals during the first 24 hours.',M('Solve $\\cos[30(t-3)^\\circ]\\geq0.5$.'),A('$1\\leq t\\leq5$ and $13\\leq t\\leq17$.')),
 P('The boat arrives at 06:30 and needs 90 minutes continuously above the minimum depth. Find the earliest time it can begin entering.',Rr('The first access interval has ended, and the next begins at 13:00.'),A('13:00; 90 minutes fits before 17:00.'))],
plot('Tidal depth over one day',fn=lambda t:4+2*math.cos(math.pi/6*(t-3)),domain=(0,24),yrange=(0,7),xlabel='Hours after midnight',ylabel='Depth (m)'),
[('access boundary1',4+2*math.cos(math.pi/6*(1-3)),5),('access boundary2',4+2*math.cos(math.pi/6*(5-3)),5)])

add('fn','Ticket demand and a revenue target','Quadratic models','2.6',
r'For ticket prices $p$ between 5 and 25, demand is modelled by $q=600-20p$, where $q$ is tickets sold. Revenue is $R=pq$. The venue can seat at most 360 people.',
[P('Write the revenue model and find its maximum over the stated price domain.',M('$R(p)=600p-20p^2$.'),M('Find the vertex or use a graph.'),A('Maximum revenue $4500$ at $p=15$.')),
 P('Find the range of prices giving revenue at least 4000.',M('Solve $600p-20p^2\\geq4000$.'),A('$10\\leq p\\leq20$.')),
 P('Taking the seating capacity into account, state the price interval satisfying both conditions, assuming demand must not exceed capacity.',M('$600-20p\\leq360$ gives $p\\geq12$.'),A('$12\\leq p\\leq20$.'),Rr('Prices below 12 meet the revenue target in the unconstrained model but require more seats than available.'))],
plot('Revenue against ticket price',fn=lambda p:600*p-20*p*p,domain=(5,25),yrange=(0,5000),xlabel='Price',ylabel='Revenue'),
[('revenue maximum',600*15-20*15**2,4500),('constraint',600-20*12,360)])

add('fn','A stepped mobile-data tariff','Model interpretation and limitations','2.7',
r'A monthly data plan costs 18 for up to 4 GB. Above 4 GB it costs an additional 3.50 per GB, charged continuously for fractions of a GB. A second plan costs 2.80 per GB with no fixed fee. Let usage be $x\geq0$.',
[P('Write a piecewise cost function $C(x)$ for the first plan.',A('$C(x)=18$ for $0\\leq x\\leq4$.'),A('$C(x)=18+3.5(x-4)$ for $x>4$.')),
 P('Find all usages for which the two plans cost the same.',M('Check the flat section and the section above 4 separately.'),A('The flat-section candidate $18/2.8=6.43$ is outside its domain; on the upper section $3.5x+4=2.8x$ gives a negative value.'),Rr('There are no equal costs for $x\\geq0$.')),
 P('Decide which plan is cheaper for every valid usage and justify using the two sections.',M('For $x\\leq4$, $2.8x\\leq11.2<18$; for $x>4$, $C(x)-2.8x=0.7x+4>0$.'),Rr('The second plan is always cheaper.'))],
plot('Two mobile-data tariffs',fn=lambda x:18 if x<=4 else 18+3.5*(x-4),domain=(0,12),yrange=(0,50),xlabel='Data usage (GB)',ylabel='Monthly cost',extra=[('Plan 2',[(0,0),(12,33.6)])]),
[('upper section difference',18+3.5*(10-4)-2.8*10,11),('no feasible crossing',-4/.7<0,True)])

add('fn','Lighting a studio wall','Model interpretation and limitations','2.6',
r'The illumination from one lamp is modelled by $E(d)=k/d^2$ lux at distance $d>0$ metres. At 2 m it gives 180 lux. A second identical lamp contributes 45 lux at the point being considered.',
[P('Find $k$ and the illumination from the first lamp at 3 m.',M('Use $180=k/4$.'),A('$k=720$ and $E(3)=80$ lux.')),
 P('Find the greatest distance from the first lamp at which the combined illumination is at least 125 lux.',M('Solve $720/d^2+45\\geq125$ with $d>0$.'),A('$d\\leq3$ m, so greatest distance 3 m.')),
 P('A designer doubles the distance from one lamp and claims the illumination halves. Explain the actual change.',M('$E(2d)=k/(4d^2)=E(d)/4$.'),Rr('It falls to one quarter, a 75% reduction.'))],
plot('Illumination from one lamp',fn=lambda d:720/d**2,domain=(1,6),yrange=(0,800),xlabel='Distance (m)',ylabel='Illumination (lux)'),
[('calibration',720/2**2,180),('combined threshold',720/3**2+45,125)])

add('fn','A cubic reservoir model','Model interpretation and limitations','2.6',
r'The stored volume in a reservoir over a six-hour operation is modelled by $V(t)=at^3+bt^2+120$, in cubic metres. Measurements give $V(2)=168$ and $V(4)=264$. The model is only intended for $0\leq t\leq6$.',
[P('Find $a$ and $b$.',M('Use $8a+4b=48$ and $64a+16b=144$.'),A('$a=-1.5$ and $b=15$.')),
 P('Use technology to find the maximum stored volume on the model’s domain.',M('Find the greatest value of $-1.5t^3+15t^2+120$ on $[0,6]$.'),A('The volume is increasing on this domain; maximum is $336$ cubic metres at $t=6$.')),
 P('The reservoir capacity is 300 cubic metres. Find when this is first reached and explain the consequence for the model afterwards.',M('Solve $-1.5t^3+15t^2+120=300$ in $[0,6]$.'),A(f'$t={bisect(lambda t:-1.5*t**3+15*t*t-180,4,6):.6g}$ hours.'),Rr('Without overflow or a change in operation, the model cannot represent stored volume beyond capacity.'))],
plot('Reservoir volume model',fn=lambda t:-1.5*t**3+15*t*t+120,domain=(0,6),yrange=(0,370),xlabel='Time (h)',ylabel='Volume (m3)'),
[('measurement1',-1.5*8+15*4+120,168),('measurement2',-1.5*64+15*16+120,264),('endpoint maximum',-1.5*216+15*36+120,336)])

xs=[0,1,2,3];ys=[40,51,65,82];lin=lambda x:40+14*x;ex=lambda x:40*1.27**x;sse1=sum((y-lin(x))**2 for x,y in zip(xs,ys));sse2=sum((y-ex(x))**2 for x,y in zip(xs,ys))
add('fn','Choosing between growth models','Model interpretation and limitations','2.7',
r'A culture is measured at four equally spaced times. Two proposed models are $L(t)=40+14t$ and $E(t)=40(1.27)^t$.'+table(zip(xs,ys),['Time','Observed population']),
[P('Find the residual at $t=2$ for each model, using observed minus predicted.',M('Evaluate both models at $t=2$.'),A(f'Linear residual $-3$; exponential residual ${65-ex(2):.6g}$.')),
 P('Calculate the sum of squared residuals for each model and choose the better fit by this criterion.',M('Square and sum all four observed-minus-predicted differences.'),A(f'Linear: ${sse1:.6g}$; exponential: ${sse2:.6g}$.'),Rr('The exponential model has the smaller sum, so it fits these observations better.')),
 P('Explain why this comparison does not establish that exponential growth continues indefinitely.',Rr('Only a short observed interval has been fitted.'),Rr('Resources, competition or other mechanisms can alter growth outside that interval.'))],
plot('Observed culture counts',pts=list(zip(xs,ys)),domain=(0,3),xlabel='Time',ylabel='Population',scatter=True),
[('linear SSE',sse1,18),('exponential fit better',sse2<sse1,True)])

tallow=math.log(8/50)/math.log(.82)
add('fn','A medicine concentration threshold','Exponential models','2.6',
r'After a single dose, a medicine concentration is modelled by $C(t)=50(0.82)^t$ milligrams per litre, where $t$ is in hours. A laboratory procedure requires the concentration to be at most 8 mg/L. No further doses are given.',
[P('Find the percentage fall per hour and the half-life.',A('The fall is $18\\%$ per hour.'),M('Solve $50(0.82)^t=25$.'),A(f'Half-life ${math.log(.5)/math.log(.82):.6g}$ hours.')),
 P('Find the earliest time the laboratory condition is satisfied.',M('Solve $50(0.82)^t\\leq8$.'),A(f'$t\\geq{tallow:.6g}$ hours.')),
 P('Measurements are taken only at whole hours. Find the first acceptable measurement time and the concentration then.',M('Round the threshold time upwards.'),A(f'Hour {math.ceil(tallow)}; concentration ${50*.82**math.ceil(tallow):.6g}$ mg/L.'),Rr('Rounding to the nearest hour could schedule the test before the threshold.'))],
plot('Concentration after one dose',fn=lambda t:50*.82**t,domain=(0,14),xlabel='Time (h)',ylabel='Concentration (mg/L)'),
[('threshold reconstruction',50*.82**tallow,8),('hour before fails',50*.82**(math.ceil(tallow)-1)>8,True)])

add('fn','Reading volume from a spherical tank','Model interpretation and limitations','2.3',
r'For a spherical tank of radius 3 m, the volume of liquid when its depth is $h$ metres is $V(h)=\pi h^2(3-h/3)$, with $0\leq h\leq6$.',
[P('Find the tank’s capacity and the volume at depth 2 m.',M('Evaluate the model at $h=6$ and $h=2$.'),A(f'Capacity $36\\pi={36*math.pi:.6g}$ cubic metres; $V(2)=28\\pi/3={28*math.pi/3:.6g}$ cubic metres.')),
 P('Use technology to find the depth when the tank contains 80 cubic metres.',M('Solve $\\pi h^2(3-h/3)=80$ within $[0,6]$.'),A(f'$h={bisect(lambda h:math.pi*h*h*(3-h/3)-80,0,6):.6g}$ m.')),
 P('Explain why this physical volume-depth model has an inverse on its stated domain.',Rr('Each higher depth gives a strictly greater volume between empty and full.'),Rr('Consequently every permissible volume corresponds to one depth.'))],
plot('Spherical tank volume-depth calibration',fn=lambda h:math.pi*h*h*(3-h/3),domain=(0,6),xlabel='Depth (m)',ylabel='Volume (m3)'),
[('sphere capacity',math.pi*36*(3-2),4/3*math.pi*27),('mid-depth half volume',math.pi*9*(3-1),18*math.pi)])

add('fn','A seasonal daylight model','Sinusoidal models','2.6',
r'Daylight hours in a town are modelled by $H(d)=12+3\sin[\frac{360}{365}(d-80)^\circ]$, where $d$ is the day number, $0\leq d<365$. The angle supplied to sine is in degrees.',
[P('State the amplitude and explain the meaning of the vertical shift.',A('Amplitude is 3 hours.'),Rr('The model oscillates around a mean of 12 daylight hours.')),
 P('Find the two day numbers when the daylight is 13.5 hours.',M('Solve $\\sin[(360/365)(d-80)^\\circ]=0.5$ in the stated domain.'),A('$d=110.416\\ldots$ and $232.083\\ldots$.')),
 P('Find the duration of the period in which there are at least 13.5 daylight hours. Explain why an answer of exactly 122 calendar days overstates the precision of this model.',M('Subtract the two boundary day numbers.'),A('$121.667$ days.'),Rr('The continuous model and its fitted parameters are approximate; integer calendar counting depends on how partial boundary days are treated.'))],
plot('Seasonal daylight',fn=lambda d:12+3*math.sin(2*math.pi/365*(d-80)),domain=(0,365),yrange=(8,16),xlabel='Day number',ylabel='Daylight (h)'),
[('first crossing',12+3*math.sin(2*math.pi/365*(80+365/12-80)),13.5),('duration',365/3,121.66666666666667)])

add('fn','Printing costs with a capacity limit','Linear models','2.5',
r'A printing business charges 8 per poster. A job costs a fixed 420 plus 3.20 per poster to produce. The printer can make at most 150 posters for one job.',
[P('Write cost, revenue and profit functions for $n$ posters.',A('$C(n)=420+3.2n$, $R(n)=8n$.'),A('$P(n)=4.8n-420$, for integer $0\\leq n\\leq150$.')),
 P('Find the least order size that produces a profit of at least 100.',M('Solve $4.8n-420\\geq100$.'),A('$n\\geq108.333\\ldots$, so 109 posters.')),
 P('The customer will pay at most 1100 total. Determine the greatest profit possible for this job.',M('$8n\\leq1100$ gives $n\\leq137.5$, so the largest allowed integer is 137.'),A('$P(137)=237.60$.'),Rr('The budget, rather than the 150-poster printer capacity, is the binding restriction.'))],
plot('Cost and revenue for a print job',fn=lambda n:420+3.2*n,domain=(0,150),xlabel='Posters',ylabel='Currency units',extra=[('Revenue',[(0,0),(150,1200)])]),
[('minimum profit order',4.8*109-420,103.2),('budget constrained profit',4.8*137-420,237.6)])

x=[0,1,2,3,4];y=[12,17,20,21,20]
add('fn','Fitting a quadratic to a display stand','Quadratic models','2.6',
r'The height $y$ centimetres of a decorative display is measured at horizontal positions $x$ decimetres.'+table(zip(x,y),['x (dm)','y (cm)'])+r'Use a quadratic model $y=ax^2+bx+c$.',
[P('Determine the quadratic model from the data.',M('Use quadratic regression or solve using three independent data points.'),A('$y=-x^2+6x+12$; all five points satisfy it.')),
 P('Find the maximum height and its position.',M('Use the vertex of the parabola.'),A('Maximum $21$ cm at $x=3$ dm.')),
 P('The usable display must be at least 18 cm high. Find the usable horizontal interval within $0\\leq x\\leq4$.',M('Solve $-x^2+6x+12\\geq18$.'),A('$3-\\sqrt3\\leq x\\leq4$, approximately $1.27\\leq x\\leq4$.'),Rr('The upper algebraic root exceeds the measured domain and must be restricted to 4.'))],
plot('Display measurements',pts=list(zip(x,y)),domain=(0,4),yrange=(0,24),xlabel='Horizontal position (dm)',ylabel='Height (cm)',scatter=True),
[('all five fit',all(-a*a+6*a+12==b for a,b in zip(x,y)),True),('vertex',-9+18+12,21)])

cross=bisect(lambda t:300*1.08**t-(300+35*t),1,20)
add('fn','When does percentage growth overtake a fixed increase?','Exponential models','2.5',
r'Two funds both start at 300. Fund E grows by 8% per year, so $E(t)=300(1.08)^t$. Fund L increases by 35 each year, so $L(t)=300+35t$. Use continuous models for $0\leq t\leq20$.',
[P('Compare the balances after five years.',M('Evaluate each model at $t=5$.'),A(f'$E(5)={300*1.08**5:.6g}$ and $L(5)=475$; L is larger.')),
 P('Apart from $t=0$, find when the balances are equal.',M('Solve $300(1.08)^t=300+35t$ numerically for $t>0$.'),A(f'$t={cross:.6g}$ years.')),
 P('Find the first whole year-end when Fund E is larger and explain why a graph window ending at year 5 could mislead.',M('Test consecutive integers around the positive intersection.'),A(f'Year {math.floor(cross)+1}.'),Rr('The eventual crossing is outside that window, so early observations alone hide the compounding effect.'))],
plot('Two ways of growing a fund',fn=lambda t:300*1.08**t,domain=(0,20),xlabel='Years',ylabel='Balance',extra=[('Linear',[(0,300),(20,1000)])]),
[('positive crossing',300*1.08**cross,300+35*cross),('linear five years',300+35*5,475)])

add('fn','A suspended cable and a clearance zone','Quadratic models','2.7',
r'A cable between supports at $x=0$ and $x=12$ is modelled by $h(x)=0.08(x-6)^2+4.2$ metres. A safety zone is needed wherever the cable is less than 5 m above the ground.',
[P('Find the support height and the minimum cable height.',M('Evaluate $h(0)$ and identify the vertex.'),A('Supports: $7.08$ m; minimum: $4.2$ m.')),
 P('Find the horizontal length of the safety zone.',M('Solve $0.08(x-6)^2+4.2<5$.'),A('$6-\\sqrt{10}<x<6+\\sqrt{10}$; length $2\\sqrt{10}=6.32$ m.')),
 P('The supports are raised equally, so the entire cable model shifts upwards. Find the least vertical increase needed to remove this safety zone.',M('The lowest point must reach at least 5 m.'),A('$5-4.2=0.8$ m.'),Rr('Raising only one support would not be represented by a simple uniform vertical shift.'))],
plot('Suspended cable',fn=lambda x:.08*(x-6)**2+4.2,domain=(0,12),yrange=(0,8),xlabel='Horizontal distance (m)',ylabel='Height (m)'),
[('support height',.08*36+4.2,7.08),('clearance boundary',.08*math.sqrt(10)**2+4.2,5)])

add('fn','Joining two temperature calibrations','Linear models','2.7',
r'A device converts a raw reading $x$ to temperature using $T(x)=2x+5$ for $0\leq x\leq20$, and $T(x)=ax+b$ for $20<x\leq50$. The conversion must be continuous at $x=20$, and $T(50)=90$.',
[P('Find $a$ and $b$.',M('Continuity gives $20a+b=45$; the second calibration gives $50a+b=90$.'),A('$a=1.5$, $b=15$.')),
 P('Find the raw reading corresponding to a temperature of 60.',M('Since 60 is above the joining temperature 45, use the second branch.'),A('$x=(60-15)/1.5=30$.')),
 P('Explain why using $T=2x+5$ for every reading gives a biased high-temperature estimate. Quantify the error at $x=40$.',M('At 40 the unrestricted first line gives 85, while the correct branch gives 75.'),A('It overestimates by 10 degrees.'),Rr('Above 20 its gradient is too large, and the difference grows with the raw reading.'))],
plot('Continuous two-stage calibration',fn=lambda x:2*x+5 if x<=20 else 1.5*x+15,domain=(0,50),xlabel='Raw reading',ylabel='Temperature'),
[('join',1.5*20+15,45),('end calibration',1.5*50+15,90),('inverse branch',1.5*30+15,60)])

add('fn','Interpreting a graph with a restricted inverse','Model interpretation and limitations','2.3',
r'A solar collector’s output is modelled by $P(t)=-(t-6)^2+36$ kilowatts, where $t$ is hours after 06:00 and $0\leq t\leq12$.',
[P('Find all times at which output is 27 kW.',M('Solve $(t-6)^2=9$.'),A('$t=3$ and $t=9$, corresponding to 09:00 and 15:00.')),
 P('Explain why the output function does not have a single-valued inverse on its entire domain.',Rr('The same output can occur at two different times.'),Rr('For example, 27 kW occurs at both $t=3$ and $t=9$.')),
 P('For the afternoon interval $6\\leq t\\leq12$, use technology to find when output is 20 kW and explain why there is only one answer.',M('Solve $-(t-6)^2+36=20$ on $[6,12]$.'),A('$t=10$, corresponding to 16:00.'),Rr('The afternoon graph is strictly decreasing, so each permitted output is reached once.'))],
plot('Daily solar output model',fn=lambda t:-(t-6)**2+36,domain=(0,12),yrange=(0,40),xlabel='Hours after 06:00',ylabel='Output (kW)'),
[('equal morning output',-(3-6)**2+36,27),('inverse evening',6+math.sqrt(36-27),9)])

add('fn','A quadratic rainfall-response model','Quadratic models','2.7',
r'Crop yield is modelled by $Y(r)=-0.02r^2+2r+18$ tonnes per hectare, where $r$ is additional irrigation in millimetres, $0\leq r\leq80$. Water costs 0.30 currency units per millimetre per hectare, and crop revenue is 2 currency units per tonne.',
[P('Find the irrigation that maximizes yield and the corresponding yield.',M('Find the vertex of the yield curve.'),A('$r=50$ mm; $Y=68$ tonnes per hectare.')),
 P('Write the net-return model and find the irrigation that maximizes net return.',M('$N(r)=2Y(r)-0.30r=-0.04r^2+3.7r+36$.'),A('The maximizing irrigation is $46.25$ mm.')),
 P('Find the gain in net return from using this irrigation instead of the yield-maximizing amount. Explain why the two optima differ.',M('Compare $N(46.25)$ with $N(50)$.'),A('$0.5625$ currency units per hectare.'),Rr('Additional yield must be weighed against the additional water cost; the highest yield need not give the greatest return.'))],
plot('Yield response to irrigation',fn=lambda r:-.02*r*r+2*r+18,domain=(0,80),xlabel='Irrigation (mm)',ylabel='Yield (tonnes/ha)'),
[('yield optimum',-.02*50**2+2*50+18,68),('net gain',(-.04*46.25**2+3.7*46.25+36)-(-.04*50**2+3.7*50+36),.5625)])

add('fn','An exponential model with a delayed starting clock','Exponential models','2.7',
r'A monitoring app begins recording three hours after a culture was created. The app’s fitted model is $N(t)=240(1.12)^t$, where $t$ is hours since the app started. Let $u$ be hours since the culture was created.',
[P('Express the model in terms of $u$ and find the modelled population at creation.',M('The clocks satisfy $t=u-3$.'),A(f'$N=240(1.12)^{{u-3}}$; at creation $240(1.12)^{{-3}}={240/1.12**3:.6g}$.')),
 P('Find when the population first reaches 500, measured from culture creation.',M('Solve $240(1.12)^{u-3}=500$.'),A(f'$u=3+\\log(500/240)/\\log(1.12)={3+math.log(500/240)/math.log(1.12):.6g}$ hours.')),
 P('Explain why the population-at-creation estimate is less secure than an estimate one hour after the app started.',Rr('Creation predates the recorded data, so that estimate extrapolates backwards.'),Rr('The early growth conditions may have differed from those during recording.'))],
plot('App population model',fn=lambda t:240*1.12**t,domain=(0,10),xlabel='Hours since app began',ylabel='Population'),
[('clock alignment',240*1.12**(3-3),240),('target clock',240*1.12**math.log(500/240,1.12),500)])

# GEOMETRY — exact site diagrams, triangles, circle measurements and solids.
def circlefig(title,r=5,theta=90,inner=0,notes=None):
    cx=320;cy=190;scale=115/r;rad=math.radians(theta)
    x=cx+115*math.cos(rad);y=cy-115*math.sin(rad)
    b=txt(320,25,title,17)
    if inner:
        ri=inner*scale;ix=cx+ri*math.cos(rad);iy=cy-ri*math.sin(rad)
        b+=f'<path d="M435 {cy}A115 115 0 {int(theta>180)} 0 {x:.2f} {y:.2f}L{ix:.2f} {iy:.2f}A{ri:.2f} {ri:.2f} 0 {int(theta>180)} 1 {cx+ri:.2f} {cy}Z"/>'
        b+=f'<path stroke-dasharray="4 4" d="M{cx} {cy}L{cx+ri:.2f} {cy}M{cx} {cy}L{ix:.2f} {iy:.2f}"/>'
    else:
        b+=f'<circle cx="{cx}" cy="{cy}" r="115"/><path d="M{cx} {cy}L435 {cy}M{cx} {cy}L{x:.2f} {y:.2f}"/>'
        b+=f'<path stroke-dasharray="5 4" d="M435 {cy}L{x:.2f} {y:.2f}"/>'+txt(446,cy+4,'A',14)+txt(x,y-12,'B',14)+txt(cx-11,cy+17,'O',14)
    b+=txt(380,212,f'r = {r:g}',14)+txt(355,174,f'{theta:g} degrees',13)
    if inner:b+=txt(320,330,f'Inner radius = {inner:g}',14)
    if notes:
        for i,n in enumerate(notes):b+=txt(320,350+18*i,n,13)
    return svg(b,title)
def stadium():
    b=txt(320,26,'Running track plan',17)
    b+='<path d="M160 100H480A80 80 0 0 1 480 260H160A80 80 0 0 1 160 100Z"/>'
    b+='<path stroke-dasharray="6 4" d="M160 95.2H480A84.8 84.8 0 0 1 480 264.8H160A84.8 84.8 0 0 1 160 95.2Z"/>'
    b+='<path d="M160 180V100"/>'+txt(199,145,'20 m',14)
    b+=txt(320,86,'Straight section: 80 m',14)+txt(320,315,'Dashed outer boundary: 1.2 m beyond inner boundary',14)
    return svg(b,'Stadium-shaped running track')
def vor(title,sites,bounds=(0,12,0,10),extra=None):
    xl,xh,yl,yh=bounds;sc=min(470/(xh-xl),240/(yh-yl));left=320-sc*(xh-xl)/2
    X=lambda x:left+sc*(x-xl);Y=lambda y:310-sc*(y-yl)
    b=txt(320,24,title,17)+f'<rect x="{left:.2f}" y="{Y(yh):.2f}" width="{sc*(xh-xl):.2f}" height="{sc*(yh-yl):.2f}"/>'
    for i,(px,py) in enumerate(sites):
        poly=[(xl,yl),(xh,yl),(xh,yh),(xl,yh)]
        for j,(qx,qy) in enumerate(sites):
            if i==j:continue
            a=2*(qx-px);bb=2*(qy-py);c=qx*qx+qy*qy-px*px-py*py;new=[]
            for z in range(len(poly)):
                p=poly[z-1];q=poly[z];fp=a*p[0]+bb*p[1]-c;fq=a*q[0]+bb*q[1]-c
                if (fp<=1e-9)!=(fq<=1e-9):
                    u=fp/(fp-fq);new.append((p[0]+u*(q[0]-p[0]),p[1]+u*(q[1]-p[1])))
                if fq<=1e-9:new.append(q)
            poly=new
            if not poly:break
        b+='<polygon points="'+' '.join(f'{X(x):.2f},{Y(y):.2f}' for x,y in poly)+'"/>'
        b+=f'<circle cx="{X(px):.2f}" cy="{Y(py):.2f}" r="4" fill="#111"/>'+txt(X(px)+7,Y(py)-9,f'{chr(65+i)} ({px:g},{py:g})',12,'start')
    if extra:
        for label,(x,y) in extra:b+=f'<circle cx="{X(x):.2f}" cy="{Y(y):.2f}" r="4" fill="white"/>'+txt(X(x)+8,Y(y)+17,label,12,'start')
    b+=txt(320,360,'Coordinates in kilometres; straight-line distance applies.',13)
    return svg(b,title)

c=math.sqrt(120**2+95**2-2*120*95*math.cos(math.radians(48)));area=.5*120*95*math.sin(math.radians(48))
add('gt','Surveying a triangular riverside plot','Trigonometry and bearings','3.2',
r'From point A, two boundaries to B and C have lengths 120 m and 95 m, with included angle $48^\circ$. The third boundary BC follows a straight riverbank.',
[P('Find the length BC.',M('Use the cosine rule with the included angle.'),A(f'$BC={c:.6g}$ m.')),
 P('Find the area of the triangular plot.',M('Use $\\frac12(120)(95)\\sin48^\\circ$.'),A(f'${area:.6g}$ square metres.')),
 P('Only AB and AC need fencing. Fencing costs 18 per metre and the entire plot needs treatment costing 0.65 per square metre. Find the total cost.',M('Combine $18(120+95)$ with $0.65$ times the unrounded area.'),A(f'${18*215+.65*area:.2f}$ currency units.'),Rr('The river boundary is excluded from the fencing but not from the area.'))],
geom('Triangular riverside plot',[(0,0),(120,0),(95*math.cos(math.radians(48)),95*math.sin(math.radians(48)))],[(0,1),(1,2),(2,0)],['A','B','C'],['AB = 120 m; AC = 95 m; angle BAC = 48 degrees']),
[('cosine distance',c,math.hypot(120-95*math.cos(math.radians(48)),95*math.sin(math.radians(48)))),('area determinant',area,.5*120*95*math.sin(math.radians(48)))])

east=8*math.sin(math.radians(35))+11*math.sin(math.radians(125));north=8*math.cos(math.radians(35))+11*math.cos(math.radians(125));dist=math.hypot(east,north);bearing=math.degrees(math.atan2(east,north))%360
add('gt','A two-leg coastal navigation route','Trigonometry and bearings','3.3',
r'A boat travels 8 km on a bearing of $035^\circ$, then 11 km on a bearing of $125^\circ$. Bearings are measured clockwise from north. Ignore currents.',
[P('Find the boat’s final east and north displacements from its starting point.',M('Use east components $d\\sin\\theta$ and north components $d\\cos\\theta$.'),A(f'East ${east:.6g}$ km; north ${north:.6g}$ km.')),
 P('Find the straight-line distance and bearing from the start to the final point.',M('Use Pythagoras and a quadrant-aware bearing calculation.'),A(f'Distance ${dist:.6g}$ km; bearing ${bearing:.6g}^\\circ$.')),
 P('Find the bearing for the direct return journey and the distance saved compared with retracing the route.',M('Reverse the bearing by $180^\\circ$ and compare distance with 19 km.'),A(f'Return bearing ${(bearing+180)%360:.6g}^\\circ$; distance saved ${19-dist:.6g}$ km.'))],
geom('Boat route (north upwards)',[(0,0),(8*math.sin(math.radians(35)),8*math.cos(math.radians(35))),(east,north)],[(0,1),(1,2),(2,0)],['Start','Turn','Finish'],['Legs: 8 km at 035 degrees, then 11 km at 125 degrees']),
[('perpendicular legs',dist,math.sqrt(8**2+11**2)),('bearing reconstruction',dist*math.sin(math.radians(bearing)),east)])

x=50*math.tan(math.radians(31))/(math.tan(math.radians(44))-math.tan(math.radians(31)));h=x*math.tan(math.radians(44))
add('gt','Measuring a tower from two ground positions','Trigonometry and bearings','3.3',
r'Two points P and Q lie on level ground on the same straight line from a tower’s base B. Q is 50 m farther from B than P. The angles of elevation of the top are $44^\circ$ from P and $31^\circ$ from Q. Instrument height is negligible.',
[P('Let $BP=x$. Write two equations connecting the tower height $h$ with $x$.',A('$h=x\\tan44^\\circ$.'),A('$h=(x+50)\\tan31^\\circ$.')),
 P('Find the tower height.',M('Equate the two expressions and solve for $x$.'),A(f'$x={x:.6g}$ m and $h={h:.6g}$ m.')),
 P('Explain how a 1.5 m instrument height at both points changes the height calculation.',Rr('The trigonometry gives the height above the common instrument level.'),A(f'Add 1.5 m to get ${h+1.5:.6g}$ m; the inferred horizontal distances are unchanged.'))],
geom('Two observation points',[(0,0),(x,0),(x+50,0),(0,h)],[(0,3),(1,3),(2,3),(0,2)],['B','P','Q','Top'],['PQ = 50 m; elevations at P and Q: 44 and 31 degrees']),
[('two height equations',x*math.tan(math.radians(44)),(x+50)*math.tan(math.radians(31)))])

diag=math.sqrt(8**2+6**2+3**2)
add('gt','A cable across a rectangular hall','Geometry and measurement','3.1',
r'A hall measures 8 m long, 6 m wide and 3 m high. A cable runs directly from one floor corner to the opposite ceiling corner. Installation needs an additional 0.8 m of cable at each end.',
[P('Find the length of the direct cable segment.',M('First find the floor diagonal, $\\sqrt{8^2+6^2}=10$.'),A(f'The spatial diagonal is $\\sqrt{{109}}={diag:.6g}$ m.')),
 P('Find the angle the direct segment makes with the floor.',M('Use $\\tan\\theta=3/10$.'),A(f'${math.degrees(math.atan(.3)):.6g}^\\circ$.')),
 P('Cable is sold in whole metres. Find the least length to buy and the unused length.',M('Add both installation allowances before rounding upwards.'),A(f'Buy {math.ceil(diag+1.6)} m; unused length is ${math.ceil(diag+1.6)-diag-1.6:.6g}$ m.'))],
geom('Hall cable projection',[(0,0),(10,0),(10,3)],[(0,1),(1,2),(2,0)],['Floor corner','Floor projection','Ceiling corner'],['Floor projection = diagonal of an 8 m by 6 m rectangle','Vertical height = 3 m']),
[('3D diagonal',diag**2,109),('triangle slope',math.tan(math.atan(.3)),.3)])

add('gt','Capacity and coating of a grain silo','Geometry and measurement','3.1',
r'A silo consists of a cylinder of radius 2.5 m and height 8 m topped by a cone of the same radius and vertical height 3 m. The base is circular and flat. Grain occupies the cylindrical part and half the conical volume.',
[P('Find the silo’s total capacity.',M('Add $\\pi(2.5)^2(8)$ and $\\frac13\\pi(2.5)^2(3)$.'),A(f'${56.25*math.pi:.6g}$ cubic metres.')),
 P('Find the percentage of total capacity occupied by the grain.',M('Grain volume is $50\\pi+3.125\\pi=53.125\\pi$.'),A(f'${100*53.125/56.25:.6g}\\%$.')),
 P('Find the external area to be coated, excluding the base and internal join.',M('Cone slant height is $\\sqrt{2.5^2+3^2}$.'),M('Area is $2\\pi(2.5)(8)+\\pi(2.5)\\sqrt{2.5^2+3^2}$.'),A(f'${40*math.pi+2.5*math.pi*math.hypot(2.5,3):.6g}$ square metres.'))],
geom('Vertical silo cross-section',[(-2.5,0),(2.5,0),(2.5,8),(0,11),(-2.5,8)],[(0,1),(1,2),(2,3),(3,4),(4,0),(2,4)],['','','','',''],['Radius 2.5 m; cylinder height 8 m; cone height 3 m']),
[('capacity',math.pi*2.5**2*8+math.pi*2.5**2*3/3,56.25*math.pi),('cone slant',math.hypot(2.5,3)**2,15.25)])

add('gt','A running track and its outside lane','Geometry and measurement','3.4',
r'A running track consists of two straight sections each 80 m long joined by two semicircles of radius 20 m. The outer lane boundary is everywhere 1.2 m outside the inner boundary.',
[P('Find the inner boundary’s length.',M('The two semicircles form one full circle.'),A(f'$160+40\\pi={160+40*math.pi:.6g}$ m.')),
 P('Find the additional distance around the outer boundary.',M('The straights remain 80 m; only the semicircle radii increase.'),A(f'$2\\pi(1.2)={2.4*math.pi:.6g}$ m.')),
 P('Find the area of the strip between these boundaries.',M('Use the difference of two stadium areas: $2(80)(1.2)+\\pi(21.2^2-20^2)$.'),A(f'${192+math.pi*(21.2**2-400):.6g}$ square metres.'),Rr('Using circumference difference times width alone would omit the long straight strips.'))],
stadium(),
[('length increment',2*math.pi*21.2-2*math.pi*20,2.4*math.pi),('strip area',192+math.pi*(21.2**2-400),1.2*(160+40*math.pi)+math.pi*1.2**2)])

add('gt','A sector-shaped fountain surround','Geometry and measurement','3.4',
r'A sector-shaped flower bed has outer radius 8 m, inner radius 5 m and angle $110^\circ$. The bed is an annular sector: the smaller sector is removed from the larger one.',
[P('Find the area of the flower bed.',M('Use $\\frac{110}{360}\\pi(8^2-5^2)$.'),A(f'${110/360*math.pi*39:.6g}$ square metres.')),
 P('Find the total boundary length of the bed.',M('Add both arcs and two radial segments of length 3.'),A(f'$\\frac{{110}}{{360}}2\\pi(8+5)+6={110/360*2*math.pi*13+6:.6g}$ m.')),
 P('Edging is sold in 2 m lengths. Find the least number needed if lengths may be cut and pieces joined without wastage at joins.',M('Divide the total boundary length by 2 and round upwards.'),A(f'${math.ceil((110/360*2*math.pi*13+6)/2)}$ lengths.'))],
circlefig('Annular-sector flower bed',8,110,5),
[('area difference',110/360*math.pi*8**2-110/360*math.pi*5**2,110/360*math.pi*39)])

add('gt','A straight shortcut across a circular bay','Trigonometry and bearings','3.4',
r'Two points A and B lie on a circular shoreline of radius 6 km. They subtend an angle of $75^\circ$ at the centre O. A path follows the shorter circular arc; a ferry travels along the straight chord AB.',
[P('Find the length of the shoreline path.',M('Use $75/360$ of the circumference.'),A(f'${75/360*2*math.pi*6:.6g}$ km.')),
 P('Find the ferry distance using triangle AOB.',M('Use the cosine rule or two right triangles.'),A(f'$AB=12\\sin37.5^\\circ={12*math.sin(math.radians(37.5)):.6g}$ km.')),
 P('A person walks at 5 km/h. The ferry travels at 12 km/h but requires 15 minutes waiting. Find which route is faster and the time difference.',M('Walking time is arc/5; ferry time is chord/12 plus 0.25 hour.'),A(f'Walking: ${75/360*2*math.pi*6/5:.6g}$ h; ferry: ${math.sin(math.radians(37.5))+.25:.6g}$ h.'),Rr(f'The ferry is faster by ${60*(75/360*2*math.pi*6/5-math.sin(math.radians(37.5))-.25):.6g}$ minutes.'))],
circlefig('Circular bay route',6,75,notes=['A and B are the ends of the radii shown.']),
[('chord cosine check',math.sqrt(72-72*math.cos(math.radians(75))),12*math.sin(math.radians(37.5)))])

add('gt','Filling a cone-shaped hopper','Geometry and measurement','3.1',
r'A cone-shaped hopper has its vertex at the bottom, height 4 m and top radius 2 m. It contains 12 cubic metres of material, with a horizontal surface. For a filled depth $h$, similar triangles give radius $r=h/2$.',
[P('Write the material volume as a function of depth.',M('Substitute $r=h/2$ into $V=\\frac13\\pi r^2h$.'),A('$V=\\pi h^3/12$.')),
 P('Find the filled depth and the vertical space remaining.',M('Solve $\\pi h^3/12=12$.'),A(f'$h={(144/math.pi)**(1/3):.6g}$ m; space ${4-(144/math.pi)**(1/3):.6g}$ m.')),
 P('Explain why half the hopper’s height does not correspond to half its capacity, and find the fraction of capacity at half height.',M('Volume is proportional to $h^3$.'),A('At half height the fraction is $(1/2)^3=1/8$.'),Rr('The radius also halves, so all three linear factors affect the volume.'))],
geom('Conical hopper cross-section',[(0,0),(-2,4),(2,4)],[(0,1),(1,2),(2,0)],['Vertex','Top rim','Top rim'],['Full height 4 m; full radius 2 m','Horizontal material surface; radius = half depth']),
[('full hopper capacity',math.pi*4**3/12,math.pi*2**2*4/3),('12m3 depth',math.pi*((144/math.pi)**(1/3))**3/12,12)])

add('gt','A frustum-shaped storage vessel','Geometry and measurement','3.1',
r'A vessel is a conical frustum with lower radius 2 m, upper radius 3 m and height 4 m. Use $V=\frac{\pi h}{3}(R^2+Rr+r^2)$ and curved area $A=\pi(R+r)\ell$, where $\ell$ is slant height. The vessel is open at the top.',
[P('Find its volume.',M('Substitute $R=3,r=2,h=4$ into the supplied formula.'),A(f'$V=76\\pi/3={76*math.pi/3:.6g}$ cubic metres.')),
 P('Find its external surface area, including its circular base.',M('Slant height is $\\sqrt{4^2+(3-2)^2}=\\sqrt{17}$.'),M('Add curved area and base: $5\\pi\\sqrt{17}+4\\pi$.'),A(f'${5*math.pi*math.sqrt(17)+4*math.pi:.6g}$ square metres.')),
 P('A coating covers 12 square metres per litre. Allow 15% extra for wastage. Find the least whole litres to buy.',M('Multiply the area by 1.15, divide by 12 and round upwards.'),A(f'${math.ceil((5*math.pi*math.sqrt(17)+4*math.pi)*1.15/12)}$ litres.'))],
geom('Frustum axial section',[(-2,0),(2,0),(3,4),(-3,4)],[(0,1),(1,2),(2,3),(3,0)],['','','',''],['Lower radius 2 m; upper radius 3 m; height 4 m','The top is open.']),
[('slant Pythagoras',math.sqrt(17)**2,4**2+1**2),('frustum formula',76*math.pi/3,4*math.pi/3*(9+6+4))])

add('gt','Locating a relay halfway through a warehouse','Geometry and measurement','3.1',
r'Two devices in a warehouse have coordinates $A=(1,2,1)$ and $B=(9,8,5)$, in metres. A relay is placed at their midpoint M. A wall socket is at $S=(5,0,0)$.',
[P('Find the coordinates of M and the distance AB.',M('Average corresponding coordinates and use the three-dimensional distance formula.'),A('$M=(5,5,3)$; $AB=\\sqrt{116}=10.8$ m to three significant figures.')),
 P('Find the direct distance from the socket to the relay.',M('$SM=\\sqrt{(5-5)^2+(5-0)^2+(3-0)^2}$.'),A('$SM=\\sqrt{34}=5.83$ m.')),
 P('The cable must run along the floor from S to the point directly below M, then vertically up. Find the additional cable compared with a direct connection.',M('Floor length is 5 m and vertical length is 3 m.'),A(f'Additional length $8-\\sqrt{{34}}={8-math.sqrt(34):.6g}$ m.'),Rr('A route constrained to surfaces is longer than the straight spatial segment.'))],
geom('Socket and relay vertical section',[(0,0),(5,0),(5,3)],[(0,1),(1,2),(2,0)],['S','Below M','M'],['Floor separation 5 m; relay height 3 m']),
[('AB squared',(9-1)**2+(8-2)**2+(5-1)**2,116),('SM squared',5**2+3**2,34)])

add('gt','A pitched roof and tile orders','Trigonometry and bearings','3.3',
r'A symmetrical pitched roof covers a rectangular building 12 m long and 8 m wide. The ridge is 2.4 m above the eaves and runs along the 12 m length. Ignore overhangs.',
[P('Find the sloping length from eave to ridge and the roof pitch angle.',M('Use a right triangle with horizontal run 4 m and rise 2.4 m.'),A(f'Slope length ${math.hypot(4,2.4):.6g}$ m; pitch ${math.degrees(math.atan(.6)):.6g}^\\circ$.')),
 P('Find the total roof area.',M('There are two sloping rectangles, each 12 m long.'),A(f'${24*math.hypot(4,2.4):.6g}$ square metres.')),
 P('Tiles cover 0.18 square metres each. Allow 8% extra and buy packs of 20. Find the least number of packs.',M('Use area times 1.08, divide by $0.18(20)$, then round up.'),A(f'${math.ceil(24*math.hypot(4,2.4)*1.08/(.18*20))}$ packs.'))],
geom('Roof cross-section',[(0,0),(8,0),(4,2.4)],[(0,1),(1,2),(2,0)],['Eave','Eave','Ridge'],['Building width 8 m; ridge rise 2.4 m','Ridge length perpendicular to section: 12 m']),
[('sloping rectangle area',24*math.hypot(4,2.4),12*8/math.cos(math.atan(.6)))])

area1=.5*60*85*math.sin(math.radians(70));area2=.5*70*85*math.sin(math.radians(55))
add('gt','Dividing an irregular quadrilateral','Modelling with geometry','3.2',
r'A quadrilateral ABCD is divided by diagonal AC, which is 85 m long. The sides AB and AD are 60 m and 70 m. Angles BAC and CAD are $70^\circ$ and $55^\circ$, on opposite sides of AC.',
[P('Find the area of ABCD.',M('Add the areas of triangles ABC and ACD using the included angles.'),A(f'${area1+area2:.6g}$ square metres.')),
 P('Find the two unknown boundary lengths BC and CD.',M('Apply the cosine rule separately in the two triangles.'),A(f'$BC={math.sqrt(60**2+85**2-2*60*85*math.cos(math.radians(70))):.6g}$ m; $CD={math.sqrt(70**2+85**2-2*70*85*math.cos(math.radians(55))):.6g}$ m.')),
 P('A path follows the diagonal AC. Explain why including AC when calculating the exterior perimeter is an error.',Rr('AC is internal to the quadrilateral, separating two triangles.'),Rr('The exterior perimeter consists only of AB, BC, CD and DA.'))],
geom('Two triangles sharing a diagonal',[(0,0),(60*math.cos(math.radians(70)),60*math.sin(math.radians(70))),(85,0),(70*math.cos(math.radians(55)),-70*math.sin(math.radians(55)))],[(0,1),(1,2),(2,3),(3,0),(0,2)],['A','B','C','D'],['AC = 85 m; AB = 60 m; AD = 70 m','Angles BAC = 70 degrees and CAD = 55 degrees']),
[('triangle additivity',area1+area2,.5*85*(60*math.sin(math.radians(70))+70*math.sin(math.radians(55))))])

add('gt','A wheelchair ramp with a landing','Trigonometry and bearings','3.3',
r'A ramp rises 0.72 m. Regulations allow a maximum slope of 1 vertical to 12 horizontal. A horizontal landing of length 1.5 m is required at the top. The available horizontal space is 10.0 m.',
[P('Find the minimum horizontal run of the sloping part and its inclination.',M('A 1:12 slope requires run $12(0.72)$.'),A(f'Run $8.64$ m; inclination ${math.degrees(math.atan(1/12)):.6g}^\\circ$.')),
 P('Determine whether the ramp and landing fit into the available space.',M('Total horizontal space is $8.64+1.5=10.14$ m.'),Rr('They do not fit; the shortfall is 0.14 m.')),
 P('If the landing cannot change, find the greatest rise that can be accommodated within 10.0 m.',M('The sloping run can be at most $10-1.5=8.5$ m.'),A('$8.5/12=0.7083\\ldots$ m.'),Rr('The existing 0.72 m rise exceeds this, so another layout is needed.'))],
geom('Ramp and horizontal landing',[(0,0),(8.64,.72),(10.14,.72),(8.64,0)],[(0,1),(1,2),(0,3),(3,1)],['Start','Top','Landing end','Projection'],['Rise 0.72 m; maximum slope 1:12','Horizontal landing length 1.5 m']),
[('horizontal requirement',12*.72+1.5,10.14),('max rise',8.5/12*12,8.5)])

add('gt','A service boundary between two clinics','Perpendicular bisectors','3.5',
r'Two clinics are at $A=(2,2)$ and $B=(10,6)$ on a rectangular district $0\leq x\leq12$, $0\leq y\leq10$, in kilometres. Patients use the nearer clinic, measured by straight-line distance.',
[P('Find the equation of the boundary where patients are equally far from A and B.',M('The midpoint is $(6,4)$ and AB has gradient $1/2$.'),A('The perpendicular bisector is $y=-2x+16$.')),
 P('Determine which clinic serves $P=(8,7)$.',M('Squared distances are $AP^2=61$ and $BP^2=5$.'),A('Clinic B.')),
 P('Find the area of B’s service region inside the district.',M('The boundary meets the top at $(3,10)$ and right side at $(12,-8)$ outside the district; within the district it meets the bottom at $(8,0)$.'),M('B’s area is the trapezium to the right: $\\frac12[(12-3)+(12-8)](10)$.'),A('$65$ square kilometres.'))],
vor('Two-clinic service diagram',[(2,2),(10,6)]),
[('bisector equidistance',(6-2)**2+(4-2)**2,(6-10)**2+(4-6)**2),('B area',.5*(9+4)*10,65)])

add('gt','The point shared by three emergency-service cells','Voronoi diagrams','3.6',
r'Fire stations are at $A=(2,2)$, $B=(10,2)$ and $C=(6,8)$, in kilometres. The illustrated Voronoi diagram assigns each location to its nearest station.',
[P('Find the boundary equation between A and B.',M('AB is horizontal and its midpoint has $x=6$.'),A('$x=6$.')),
 P('Find the Voronoi vertex shared by all three cells.',M('On $x=6$, equate squared distances to A and C: $16+(y-2)^2=(y-8)^2$.'),A('$y=11/3$, so vertex $(6,11/3)$.')),
 P('Find its distance to the nearest station and explain why this distance is the same for all three stations.',M('Use $\\sqrt{16+(11/3-2)^2}$.'),A('$13/3=4.33$ km.'),Rr('The vertex lies on pairwise perpendicular bisectors, so all three distances are equal.'))],
vor('Three-station Voronoi diagram',[(2,2),(10,2),(6,8)]),
[('vertex distance A',math.hypot(4,11/3-2),13/3),('vertex distance C',8-11/3,13/3)])

add('gt','Adding a new parcel collection point','Voronoi diagrams','3.6',
r'Existing collection points are $A=(2,2)$, $B=(10,2)$ and $C=(6,8)$. A new point is proposed at $D=(6,4)$. A resident is at $P=(6,3)$. All coordinates are in kilometres.',
[P('Find the resident’s nearest existing collection point and distance.',M('Compare $PA=PB=\\sqrt{17}$ with $PC=5$.'),A('A and B are equally nearest, at $\\sqrt{17}=4.12$ km.')),
 P('After D opens, find the resident’s nearest collection point and the reduction in distance.',M('$PD=1$ km.'),A(f'D is nearest; reduction $\\sqrt{{17}}-1={math.sqrt(17)-1:.6g}$ km.')),
 P('Find the new boundary between C and D and explain which parts of existing cells can change when D is added.',M('CD is vertical, with midpoint $(6,6)$.'),A('The new C–D boundary lies on $y=6$.'),Rr('Only locations closer to D than to every existing point transfer to D; all other locations keep their previous nearest existing point.'))],
vor('Collection points after adding D',[(2,2),(10,2),(6,8),(6,4)],extra=[('P',(6,3))]),
[('P existing',math.hypot(6-2,3-2),math.sqrt(17)),('CD boundary',abs(6-8),abs(6-4))])

add('gt','Nearest-station rainfall estimation','Voronoi diagrams','3.6',
r'A rectangular farming district is $0\leq x\leq12$, $0\leq y\leq8$, in kilometres. Rain stations are at $A=(3,4)$ and $B=(9,4)$, recording 42 mm and 66 mm respectively. Rainfall at each point is estimated from its nearest station.',
[P('Find the cell boundary and estimated rainfall at $(7,1)$.',M('The equal-distance boundary is the perpendicular bisector of AB.'),A('$x=6$; $(7,1)$ lies in B’s cell, so estimate 66 mm.')),
 P('Estimate the district-wide mean rainfall using the cell areas.',M('Each cell has area $6(8)=48$ square kilometres.'),A('Area-weighted mean $(42+66)/2=54$ mm.')),
 P('A third station is added at $(6,4)$ and records 90 mm. Find the new cell boundaries and the revised district-wide mean.',M('New vertical boundaries are $x=4.5$ and $x=7.5$.'),M('Cell widths are 4.5, 3 and 4.5 km.'),A('Mean $[4.5(42)+3(90)+4.5(66)]/12=63$ mm.'))],
vor('Original rainfall station cells',[(3,4),(9,4)],bounds=(0,12,0,8)),
[('revised mean',(4.5*42+3*90+4.5*66)/12,63),('area total',(4.5+3+4.5)*8,96)])

add('gt','Choosing between two Voronoi vertices','Voronoi diagrams','3.6',
r'A hazardous-material store must be placed at one of two permitted Voronoi vertices. The sites representing settlements are $A=(0,0)$, $B=(8,0)$, $C=(4,6)$ and $D=(12,6)$, in kilometres. Candidate vertices are $V=(4,5/3)$ and $W=(8,13/3)$. Maximize the distance to the nearest settlement.',
[P('Verify that V is equally far from A, B and C.',M('Calculate squared distances.'),A('Each is $169/9$, so the common distance is $13/3$ km.')),
 P('Find the nearest-settlement distance at W.',M('Squared distances from W to B, C and D are each $169/9$.'),A('Nearest distance is again $13/3$ km; A is farther away.')),
 P('Decide whether the distance criterion distinguishes the candidates, and identify one additional practical factor that could decide the location.',Rr('The minimum distances tie, so this criterion alone cannot distinguish them.'),Rr('For example, consider prevailing winds, road access, groundwater, or flood risk; state one relevant factor.'))],
vor('Permitted store vertices',[(0,0),(8,0),(4,6),(12,6)],bounds=(-1,13,-1,9),extra=[('V',(4,5/3)),('W',(8,13/3))]),
[('V radius',math.hypot(4,5/3),13/3),('W radius B',13/3,math.hypot(8-4,13/3-6)),('D distance',math.hypot(8-12,13/3-6),13/3)])

add('gt','How moving a site changes a service boundary','Perpendicular bisectors','3.5',
r'Two delivery hubs are at $A=(2,3)$ and $B=(10,3)$ in a district $0\leq x\leq12$, $0\leq y\leq8$. Hub B is moved 2 km east to $B_1=(12,3)$. Each location is served by the nearer hub.',
[P('Find the original and new service boundaries.',M('The original midpoint of AB has $x=6$; the new midpoint of $AB_1$ has $x=7$.'),A('Original boundary $x=6$; new boundary $x=7$.')),
 P('Find the area transferred from B’s service region to A’s.',M('The strip between boundaries is 1 km wide and 8 km high.'),A('$8$ square kilometres.')),
 P('A customer at $(6.5,7)$ says that moving B farther away increased their distance to the hub that serves them. Check this claim.',M('Originally B serves them, with distance $\\sqrt{3.5^2+4^2}$; afterwards A serves them, with distance $\\sqrt{4.5^2+4^2}$.'),A(f'Original ${math.hypot(3.5,4):.6g}$ km; new ${math.hypot(4.5,4):.6g}$ km.'),Rr('The claim is correct even though the assigned hub changes.'))],
vor('Original delivery regions',[(2,3),(10,3)],bounds=(0,12,0,8),extra=[('Customer',(6.5,7))]),
[('area transferred',(7-6)*8,8),('customer farther',math.hypot(4.5,4)>math.hypot(3.5,4),True)])

# STATISTICS AND PROBABILITY — data quality, distributions and permitted SL tests.
def hist(title,bins,frequencies):
    xmax=bins[-1];heights=[f/(bins[i+1]-bins[i]) for i,f in enumerate(frequencies)];mx=max(heights)*1.2
    b=txt(320,25,title,17)+'<path d="M70 65V320H580"/>'
    for i,v in enumerate(heights):
        x=70+500*bins[i]/xmax;w=500*(bins[i+1]-bins[i])/xmax;y=320-235*v/mx
        b+=f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{320-y:.2f}" fill="#e8e8e8"/>'+txt(x+w/2,y-9,f'{v:g}',12)
    for x in bins:b+=txt(70+500*x/xmax,344,x,12)
    return svg(b+txt(320,371,'Waiting time (minutes)')+ytext('Frequency density'),title)
def venn():
    b=txt(320,26,'Student memberships',17)+'<rect x="65" y="55" width="510" height="260"/><circle cx="270" cy="180" r="90"/><circle cx="370" cy="180" r="90"/>'
    b+=txt(217,170,'L',18)+txt(423,170,'I',18)+txt(320,185,'30',17)
    b+=txt(205,289,'Total in L: 68',14)+txt(440,289,'Total in I: 54',14)+txt(490,80,'120 total',14)
    return svg(b,'Language and instrument membership Venn diagram')
def boxplot(title,summaries,labels,domain):
    lo,hi=domain;X=lambda v:80+480*(v-lo)/(hi-lo);b=txt(320,25,title,17)
    for j,(mn,q1,med,q3,mx) in enumerate(summaries):
        y=115+115*j
        b+=f'<path d="M{X(mn):.2f} {y}H{X(mx):.2f}M{X(mn):.2f} {y-12}v24M{X(mx):.2f} {y-12}v24"/><rect x="{X(q1):.2f}" y="{y-26}" width="{X(q3)-X(q1):.2f}" height="52" fill="white"/><path d="M{X(med):.2f} {y-26}v52"/>'
        b+=txt(50,y+5,labels[j],13)
        for v in [mn,q1,med,q3,mx]:b+=txt(X(v),y+45,v,12)
    return svg(b+txt(320,360,'Values on the same linear scale',13),title)
def binpmf(n,p,k):return math.comb(n,k)*p**k*(1-p)**(n-k)
def ttail(t,df):
    coef=math.gamma((df+1)/2)/(math.sqrt(df*math.pi)*math.gamma(df/2))
    return .5-simpson(lambda z:coef*(1+z*z/df)**(-(df+1)/2),0,t)

def waiting_cumulative():
    X=lambda t:75+25*t;Y=lambda f:320-4*f
    b=txt(320,25,'Cumulative patient waiting times',17)+'<path d="M75 60V320H590"/>'+txt(325,370,'Waiting time (minutes)')+ytext('Cumulative frequency')
    for t in [0,5,10,15,20]:b+=f'<path d="M{X(t)} 320v5"/>'+txt(X(t),344,t,12)
    for f in [0,15,30,45,60]:b+=f'<path d="M70 {Y(f)}h5"/>'+txt(65,Y(f)+4,f,12,'end')
    ps=[(0,0),(5,10),(10,30),(15,50),(20,60)]
    b+='<polyline points="'+' '.join(f'{X(t)},{Y(f)}' for t,f in ps)+'"/>'
    for t,f in ps:b+=f'<circle cx="{X(t)}" cy="{Y(f)}" r="3" fill="#111"/>'
    return svg(b,'Cumulative-frequency graph with linear interpolation between class boundaries')

add('sp','Reading a cumulative-frequency graph','Sampling and descriptive statistics','4.2',
r'The cumulative-frequency graph summarizes the waiting times of 60 patients. Its straight segments join $(0,0),(5,10),(10,30),(15,50),(20,60)$, where the first coordinate is minutes. Use linear interpolation between class boundaries.',
[P('Estimate the median and both quartiles.',M('Read cumulative frequencies 15, 30 and 45; interpolate on the relevant straight segments.'),A('$Q_1=6.25$, median $10$, and $Q_3=13.75$ minutes.')),
 P('Find the interquartile range and the proportion who waited at least 10 minutes.',M('Subtract quartiles and use the complement of the cumulative frequency at 10.'),A('$IQR=7.50$ minutes; proportion $(60-30)/60=0.50$.')),
 P('Estimate the mean using the four equal-width classes, and explain why the exact mean is unavailable.',M('Class frequencies are $10,20,20,10$; use midpoints $2.5,7.5,12.5,17.5$.'),A('Estimated mean $=(10(2.5)+20(7.5)+20(12.5)+10(17.5))/60=10$ minutes.'),Rr('The individual waiting times within each class are not supplied, so midpoint and interpolation calculations are estimates.'))],
waiting_cumulative(),
[('frequency total',10+20+20+10,60),('midpoint weighted mean',(25+150+250+175)/60,10),('lower quartile interpolation',5+(15-10)*5/20,6.25),('upper quartile interpolation',10+(45-30)*5/20,13.75)])

add('sp','A stratified school survey','Sampling and descriptive statistics','4.1',
r'A school has 420 junior, 300 middle and 180 senior students. A survey will select 90 students, using proportional stratified random sampling. A previous online poll received responses from 60 junior, 20 middle and 10 senior students.',
[P('Find the required sample size in each stratum.',M('The sampling fraction is $90/900=0.1$.'),A('Junior 42, middle 30, senior 18.')),
 P('Of the previous poll respondents, 42 junior, 10 middle and 3 senior students supported a proposal. Compare the unweighted respondent support rate with an estimate weighted by the school’s stratum proportions.',M('Unweighted rate is $55/90$; weighted rate uses $420/900,300/900,180/900$.'),A(f'Unweighted ${100*55/90:.6g}\\%$; weighted ${100*(420/900*.7+300/900*.5+180/900*.3):.6g}\\%$.')),
 P('Explain why weighting the previous poll does not remove all its possible bias.',Rr('Respondents volunteered rather than being randomly selected within each stratum.'),Rr('Supporters may be more likely to respond, so within-stratum response bias can remain.'))],
bars('School population by stratum',[420,300,180],['Junior','Middle','Senior'],'Students'),
[('sample total',42+30+18,90),('weighted support',420/900*.7+300/900*.5+180/900*.3,83/150)])

add('sp','Changing the scale of a test score','Sampling and descriptive statistics','4.3',
r'A test has mean score 48 and standard deviation 7.5. The exam board converts every score $x$ to $y=1.2x+8$. A score of at least 80 on the converted scale earns a distinction.',
[P('Find the converted mean and standard deviation.',M('The mean transforms by the full affine rule; standard deviation is multiplied only by the positive scale factor.'),A('Mean $65.6$; standard deviation $9$.')),
 P('Find the minimum original score corresponding to a distinction. Original scores are whole numbers.',M('Solve $1.2x+8\\geq80$.'),A('$x\\geq60$, so minimum 60.')),
 P('Explain whether adding 8 points to every score changes the spread or the number of standard deviations between a score and the mean.',Rr('Adding a constant shifts all scores and the mean equally, leaving pairwise differences unchanged.'),Rr('It therefore does not change the standard deviation or standardized relative position.'))],
flow('Linear score conversion',['Original x','Multiply by 1.2','Add 8','Converted y']),
[('converted mean',1.2*48+8,65.6),('converted sd',1.2*7.5,9),('threshold',1.2*60+8,80)])

add('sp','Comparing two box plots carefully','Sampling and descriptive statistics','4.2',
r'Two delivery services have the five-number summaries shown in the box plots, measured in minutes. Assume the summaries describe the samples accurately.',
[P('Find the interquartile range for each service.',M('Subtract the lower quartile from the upper quartile.'),A('A: $34-22=12$ min; B: $32-24=8$ min.')),
 P('Use the $1.5\\times IQR$ rule to decide whether a new delivery time of 49 minutes is an upper outlier for either service.',M('Upper fences are $34+1.5(12)=52$ and $32+1.5(8)=44$.'),A('49 is not an upper outlier for A, but is one for B.')),
 P('A manager says that B has a lower mean because it has a lower median. Explain whether the box plots establish this.',Rr('A median does not determine the mean; the values within each quartile are not supplied.'),Rr('The claimed ordering of means cannot be established from these summaries alone.'))],
boxplot('Delivery-time box plots',[(15,22,28,34,48),(18,24,27,32,42)],['A','B'],(10,55)),
[('upper fence A',34+1.5*(34-22),52),('upper fence B',32+1.5*(32-24),44)])

x=[1,2,3,4,5,6];y=[12,15,16,20,21,24];mx=mean(x);my=mean(y);slope=sum((a-mx)*(b-my) for a,b in zip(x,y))/sum((a-mx)**2 for a in x);inter=my-slope*mx
add('sp','A regression line and a missed observation','Correlation and regression','4.4',
r'A tutor records weekly independent study time $x$ hours and a short quiz score $y$ for six students.'+table(zip(x,y),['x','y']),
[P('Find the least-squares regression line of $y$ on $x$ and Pearson’s correlation coefficient.',M('Use linear regression with study time as explanatory variable.'),A(f'$y={slope:.6g}x+{inter:.6g}$; $r={corr(x,y):.6g}$.')),
 P('A seventh student studies 4.5 hours and scores 19. Find the prediction and residual.',M('Substitute $x=4.5$ and use observed minus predicted.'),A(f'Predicted ${slope*4.5+inter:.6g}$; residual ${19-(slope*4.5+inter):.6g}$.')),
 P('Explain why predicting a score for 15 hours of study is less reliable, and why the correlation does not show that extra study alone causes higher marks.',Rr('15 hours lies far outside the observed range 1–6 hours.'),Rr('Other factors such as prior attainment or motivation could influence both study time and scores.'))],
plot('Study time and quiz scores',pts=list(zip(x,y)),domain=(0,7),xlabel='Study hours',ylabel='Quiz score',scatter=True),
[('regression through mean',slope*mx+inter,my),('regression residual sum',sum(b-(slope*a+inter) for a,b in zip(x,y)),0)])

add('sp','Why reversing a regression is not the same fit','Correlation and regression','4.4',
r'A sample of trees has diameter $x$ centimetres and height $y$ metres. Technology gives the regression of height on diameter as $y=0.42x+3.6$, and the regression of diameter on height as $x=2.10y-4.8$. Observed diameters range from 10 to 40 cm.',
[P('Predict the height of a tree of diameter 25 cm.',M('Use the regression with height as the response variable.'),A('$y=0.42(25)+3.6=14.1$ m.')),
 P('Predict the diameter of a tree of height 15 m. Compare it with the value obtained by reversing the first regression equation.',M('Correct regression: $x=2.10(15)-4.8=26.7$.'),A('Reversing the first line gives $(15-3.6)/0.42=27.1429\\ldots$ cm.')),
 P('Explain why the two answers differ and which prediction should be used.',Rr('The two regressions minimize squared errors in different response variables.'),Rr('Use 26.7 cm because diameter is being predicted from height; the lines need not be algebraic inverses.'))],
plot('Height-on-diameter fitted line',fn=lambda x:.42*x+3.6,domain=(10,40),xlabel='Diameter (cm)',ylabel='Height (m)'),
[('height prediction',.42*25+3.6,14.1),('diameter prediction',2.1*15-4.8,26.7)])

rx=[1,2.5,2.5,4,5,6];ry=[2,1,3,4,6,5];rs=corr(rx,ry)
add('sp','Spearman correlation with tied ranks','Correlation and regression','4.10',
r'Six café locations are ranked for footfall and customer satisfaction. Rank 1 means the lowest value. Two footfall values tie for positions 2 and 3.'+table(zip(['A','B','C','D','E','F'],[1,'tie','tie',4,5,6],ry),['Café','Footfall rank','Satisfaction rank']),
[P('State the rank assigned to each tied footfall observation and explain why.',M('Average the occupied ranks 2 and 3.'),A('Both receive rank 2.5.')),
 P('Use technology to find Spearman’s rank correlation coefficient.',M('Calculate Pearson correlation on the two lists of ranks, including 2.5 twice.'),A(f'$r_s={rs:.6g}$.')),
 P('Interpret this result and explain why it does not mean that about 84% of cafés have matching ranks.',Rr('There is a strong positive association between footfall rank and satisfaction rank.'),Rr('A correlation coefficient is not a proportion of matching observations or a percentage accuracy.'))],
plot('Rank pairs including ties',pts=list(zip(rx,ry)),domain=(0,7),yrange=(0,7),xlabel='Footfall rank',ylabel='Satisfaction rank',scatter=True),
[('tied rank sum',sum(rx),21),('rank association positive',rs>.8,True)])

add('sp','Memberships and conditional probabilities','Probability','4.6',
r'In a group of 120 students, 68 study a language L, 54 play an instrument I and 30 do both. One student is selected at random.',
[P('Find the numbers in L only, I only and neither.',M('Subtract the intersection from each set and use inclusion-exclusion.'),A('L only 38, I only 24, neither 28.')),
 P(r'Find $P(I\mid L)$ and $P(L\mid I)$.',M('Use the appropriate conditioning group for each denominator.'),A('$P(I\\mid L)=30/68=15/34$; $P(L\\mid I)=30/54=5/9$.')),
 P('Determine whether L and I are independent.',M('Compare $P(I\\mid L)=15/34$ with $P(I)=54/120=0.45$.'),Rr('They differ, so the events are not independent.'))],
venn(),
[('partition',38+30+24+28,120),('independence fails',30/120!=68/120*54/120,True)])

post=.3*.08/(.3*.08+.7*.02)
def supplier_tree():
    b=txt(320,25,'Supplier and fault probability tree',17)
    b+='<path d="M80 190L285 105M80 190L285 275M305 105L515 65M305 105L515 145M305 275L515 235M305 275L515 315"/>'
    for x,y,label in [(180,128,'0.30'),(180,245,'0.70'),(285,95,'A'),(285,265,'B'),(410,70,'0.08'),(410,145,'0.92'),(410,240,'0.02'),(410,315,'0.98'),(550,70,'Fault'),(550,150,'No fault'),(550,240,'Fault'),(550,320,'No fault')]:
        b+=txt(x,y,label,14)
    return svg(b,'Two-stage supplier and fault probability tree')

add('sp','Finding the likely source of a faulty part','Probability','4.6',
r'A factory obtains 30% of parts from supplier A and 70% from B. Independently chosen parts from A have an 8% fault rate; those from B have a 2% fault rate. One part is selected at random and found faulty.',
[P('Find the probability that a randomly selected part is faulty.',M('Add the two disjoint faulty branches, $0.30(0.08)+0.70(0.02)$.'),A('$0.038$.')),
 P('Find the probability that the faulty part came from A.',M('Divide the A-and-faulty branch by the overall fault probability.'),A(f'$0.024/0.038={post:.6g}$.')),
 P('A manager says B must supply most faulty parts because it supplies most parts. Evaluate this claim using an expected batch of 10000.',M('Expected faulty counts are $3000(0.08)=240$ from A and $7000(0.02)=140$ from B.'),Rr('A supplies more of the faulty parts despite supplying fewer parts overall.'))],
supplier_tree(),
[('fault rate',.3*.08+.7*.02,.038),('posterior',post,12/19)])

add('sp','Drawing two coloured counters without replacement','Probability','4.6',
r'A bag contains 5 red, 3 blue and 2 green counters. Two counters are drawn without replacement.',
[P('Find the probability that both counters have the same colour.',M('Add $\\frac5{10}\\frac4{9}+\\frac3{10}\\frac2{9}+\\frac2{10}\\frac1{9}$.'),A('$28/90=14/45$.')),
 P('Given that the counters have the same colour, find the probability that both are red.',M('Divide the red-red probability $20/90$ by $28/90$.'),A('$5/7$.')),
 P('A second bag has the same colour proportions but 100 counters. Explain why the probability of matching colours is different, and calculate it.',M('Use counts 50, 30 and 20 with denominator $100(99)$.'),A('$(50(49)+30(29)+20(19))/9900=37/99$.'),Rr('Without replacement, the first draw changes the smaller bag’s proportions more substantially.'))],
bars('Counters in the bag',[5,3,2],['Red','Blue','Green'],'Counters'),
[('small match',(5*4+3*2+2*1)/90,14/45),('large match',(50*49+30*29+20*19)/9900,37/99)])

add('sp','Designing a fair fundraising game','Probability','4.7',
r'A game uses a spinner with outcomes 0, 1, 2 and 3 having probabilities 0.40, 0.30, 0.20 and 0.10. The gross prize is 0, 2, 5 or 12 currency units respectively. A player pays an entry fee F.',
[P('Find the expected gross prize.',M('Compute $0(0.4)+2(0.3)+5(0.2)+12(0.1)$.'),A('$2.8$ currency units.')),
 P('Find the entry fee that makes the game fair to the player. Find the organiser’s expected profit from 250 plays if the actual fee is 3.50.',M('A fair fee equals the expected gross prize; profit per play is fee minus expected prize.'),A('Fair fee $2.80$; expected total organiser profit $250(0.7)=175$.')),
 P('Explain why an expected profit of 175 does not guarantee a profit on one set of 250 plays.',Rr('The number of large prizes is random, so actual payouts fluctuate.'),Rr('Expected value is a long-run average, not a guaranteed outcome of one batch.'))],
bars('Spinner outcome probabilities',[.4,.3,.2,.1],['0','1','2','3'],'Probability'),
[('probability total',.4+.3+.2+.1,1),('expected gross',2*.3+5*.2+12*.1,2.8)])

add('sp','Recovering a binomial model from its moments','Binomial and normal distributions','4.8',
r'The number X of successful scans in a fixed batch is modelled by a binomial distribution with mean 12 and variance 3. Each scan is assumed to have the same success probability and to be independent.',
[P('Find the number of scans $n$ and success probability $p$.',M('Use $np=12$ and $np(1-p)=3$.'),A('$1-p=1/4$, so $p=0.75$ and $n=16$.')),
 P('Find the probability that at least 14 scans succeed.',M('Calculate $P(X\\geq14)$ for $X\\sim B(16,0.75)$ using technology.'),A(f'${sum(binpmf(16,.75,k) for k in range(14,17)):.6g}$.')),
 P('Explain how a shared scanner malfunction could make the binomial model unsuitable.',Rr('The malfunction can cause several scan failures together, violating independence.'),Rr('It can also change the success probability within the batch.'))],
flow('Unknown binomial scan model',['n scans','Success chance p','Mean: 12','Variance: 3']),
[('mean',16*.75,12),('variance',16*.75*.25,3),('PMF total',sum(binpmf(16,.75,k) for k in range(17)),1)])

pgroup=1-binpmf(8,.12,0)-binpmf(8,.12,1)
add('sp','Escalation rules for independent inspection groups','Binomial and normal distributions','4.8',
r'Each item independently has probability 0.12 of needing repair. Items are inspected in groups of 8. A group is escalated if at least two items need repair. Four independently formed groups are inspected.',
[P('Find the probability that one group is escalated.',M('For $X\\sim B(8,0.12)$ use $1-P(X=0)-P(X=1)$.'),A(f'${pgroup:.6g}$.')),
 P('Find the probability that at least one of the four groups is escalated.',M('Use the complement: $1-(1-p)^4$, where $p$ is the probability from part (a).'),A(f'${1-(1-pgroup)**4:.6g}$.')),
 P('Explain why using $P(Y\\geq8)$ with $Y\\sim B(32,0.12)$ does not answer part (b).',Rr('One group can contain two repairs even if the total across all groups is less than eight.'),Rr('The escalation rule depends on how repairs are grouped, not only on the total number.'))],
bars('One-group repair-count probabilities',[binpmf(8,.12,k) for k in range(5)],[str(k) for k in range(5)],'Probability'),
[('one group complement',pgroup,sum(binpmf(8,.12,k) for k in range(2,9))),('four-group complement',1-(1-pgroup)**4,1-(binpmf(8,.12,0)+binpmf(8,.12,1))**4)])

cut=72+8*N.inv_cdf(.9);prob=N.cdf((80-72)/8)-N.cdf((64-72)/8)
add('sp','A normal-distribution award threshold','Binomial and normal distributions','4.9',
r'Scores on an assessment are modelled by a normal distribution with mean 72 and standard deviation 8. The top 10% receive an award. Use the continuous model before any rounding.',
[P('Find the score threshold for an award.',M('Use the 90th percentile of $N(72,8^2)$.'),A(f'${cut:.6g}$.')),
 P('Find the probability of a score between 64 and 80.',M('Evaluate the normal probability between these two bounds.'),A(f'${prob:.6g}$.')),
 P('There are 240 candidates. Estimate the number scoring at least 80 and explain why rounding the award threshold to 82 before calculating the top 10% changes the intended proportion.',M('Use $240P(X\\geq80)$.'),A(f'Expected number ${240*(1-N.cdf(1)):.6g}$, about 38 candidates.'),Rr('The rounded threshold defines a different tail area from the exact 90th percentile.'))],
plot('Assessment score density',fn=lambda x:math.exp(-.5*((x-72)/8)**2)/(8*math.sqrt(2*math.pi)),domain=(48,96),xlabel='Score',ylabel='Density'),
[('90th percentile',N.cdf((cut-72)/8),.9),('central probability',prob,2*N.cdf(1)-1)])

pa=1-N.cdf((90-80)/10);pb=1-N.cdf((90-85)/5);total=.6*pa+.4*pb
add('sp','A shipment drawn from two normal populations','Binomial and normal distributions','4.9',
r'60% of bolts come from machine A, whose breaking strength is normal with mean 80 kN and standard deviation 10 kN. The other 40% come from B, with mean 85 kN and standard deviation 5 kN. A bolt is chosen randomly from the combined output.',
[P('Find the probability that a bolt from each machine has strength above 90 kN.',M('Evaluate the two normal upper-tail probabilities separately.'),A(f'For A: ${pa:.6g}$; for B: ${pb:.6g}$.')),
 P('Find the overall probability of strength above 90 kN and the probability that such a bolt came from B.',M('Weight the upper-tail probabilities by 0.6 and 0.4.'),A(f'Overall ${total:.6g}$; conditional B probability ${.4*pb/total:.6g}$.')),
 P('Explain why averaging the two standard deviations is not a valid method for finding the combined probability.',Rr('The combined population is a mixture of two distributions, with different means as well as spreads.'),Rr('Its tail probability must be obtained from the weighted component probabilities; the mixture need not be normal.'))],
plot('Breaking-strength density from machine A',fn=lambda x:math.exp(-.5*((x-80)/10)**2)/(10*math.sqrt(2*math.pi)),domain=(50,110),xlabel='Strength (kN)',ylabel='A density'),
[('equal tail standard positions',pa,pb),('conditional B',.4*pb/total,.4)])

obs=[[30,20,10],[20,30,10]];stat=sum((o-20)**2/20 for o in [30,20,10,20,30,10]) # replaced below with true expected table
expected=[[25,25,10],[25,25,10]];stat=sum((obs[i][j]-expected[i][j])**2/expected[i][j] for i in range(2) for j in range(3));pchi=math.exp(-stat/2)
add('sp','Testing transport preference across two campuses','Hypothesis testing','4.11',
r'Independent random samples of 60 students from each of two campuses report their preferred transport. Test independence at the 5% significance level.'+table([('North',30,20,10),('South',20,30,10)],['Campus','Bus','Bicycle','Walk']),
[P('State the null and alternative hypotheses and find the expected frequencies.',A('$H_0$: transport preference is independent of campus; $H_1$: they are associated.'),M('Use row total times column total divided by 120.'),A('Expected row at each campus: $25,25,10$.')),
 P('Find the chi-square statistic, degrees of freedom and p-value.',M('Sum $(O-E)^2/E$ and use $(2-1)(3-1)=2$ degrees of freedom.'),A(f'$\\chi^2={stat:.6g}$, $df=2$, $p={pchi:.6g}$.')),
 P('State the conclusion in context and check the expected-frequency condition.',Rr(f'$p={pchi:.6g}>0.05$, so do not reject independence; there is insufficient evidence of an association.'),Rr('Every expected frequency is at least 10, so the greater-than-5 condition is met.'))],
bars('Observed transport counts',[30,20,10,20,30,10],['N bus','N bike','N walk','S bus','S bike','S walk'],'Students'),
[('chi-square statistic',stat,4),('df2 survival',pchi,math.exp(-2)),('expected total',sum(map(sum,expected)),120)])

gofobs=[26,18,35,21];gofstat=sum((o-25)**2/25 for o in gofobs);gofp=math.erfc(math.sqrt(gofstat/2))+math.sqrt(2*gofstat/math.pi)*math.exp(-gofstat/2)
add('sp','Testing a spinner with four equally likely outcomes','Hypothesis testing','4.11',
r'A spinner is claimed to have four equally likely outcomes. It is spun independently 100 times, giving counts 26, 18, 35 and 21. No parameters are estimated from the data. Use a chi-square goodness-of-fit test at 5%.',
[P('State the hypotheses and expected counts.',A('$H_0$: each outcome has probability 0.25; $H_1$: at least one probability differs.'),M('Multiply 100 by 0.25.'),A('Expected counts $25,25,25,25$.')),
 P('Find the test statistic, degrees of freedom and p-value.',M('Use $\\sum(O-E)^2/E$ and $df=4-1$.'),A(f'$\\chi^2={gofstat:.6g}$, $df=3$, $p={gofp:.6g}$.')),
 P('Give a conclusion and explain why the largest count alone is not a complete test of the claim.',Rr('The p-value exceeds 0.05, so there is insufficient evidence against equally likely outcomes.'),Rr('The chi-square statistic incorporates deviations in all four categories; a high single count must be assessed relative to the full sampling pattern.'))],
bars('Spinner outcome counts',gofobs,['1','2','3','4'],'Observed count'),
[('GOF statistic',gofstat,6.64),('expected greater than five',25>5,True)])

ta=[18,20,19,21,22,20];tb=[15,18,17,16,19,17];tv=(mean(ta)-mean(tb))/math.sqrt(2/6+2/6);tp=ttail(tv,10)
add('sp','Comparing two independent training groups','Hypothesis testing','4.11',
r'Two independent random samples complete different training programmes. Their performance scores are shown. Assume the populations are normal with equal variances. Test at 5% whether programme A has the larger population mean.'+table(zip(ta,tb),['Programme A','Programme B']),
[P('State the hypotheses and find the sample means.',A('$H_0:\\mu_A=\\mu_B$; $H_1:\\mu_A>\\mu_B$.'),M('Calculate each mean from the six scores.'),A('$\\bar x_A=20$, $\\bar x_B=17$.')),
 P('Carry out a pooled two-sample t-test using technology. Give the statistic and one-sided p-value.',M('The pooled variance is 2; $t=(20-17)/\\sqrt{2/6+2/6}$, with $df=10$.'),A(f'$t={tv:.6g}$; $p={tp:.6g}$.')),
 P('State the conclusion and explain why treating the rows as matched pairs would be inappropriate.',Rr('Reject $H_0$ because $p<0.05$; there is evidence that A’s population mean is larger.'),Rr('The samples are independent and no matching of subjects is described; rows do not create genuine pairs.'))],
plot('Training scores by group',pts=[(1+.04*i,v) for i,v in enumerate(ta)]+[(2+.04*i,v) for i,v in enumerate(tb)],domain=(.5,2.7),yrange=(14,23),xlabel='Group A near 1; group B near 2',ylabel='Score',scatter=True),
[('A sample variance',statistics.variance(ta),2),('B sample variance',statistics.variance(tb),2),('t statistic',tv,3*math.sqrt(1.5))])

add('sp','A p-value at two significance levels','Hypothesis testing','4.11',
r'A pre-planned pooled, unpaired two-sample t-test compares the mean lifetimes of two brands of lamp. The alternative is that the population means differ. Technology reports a two-sided p-value of 0.032. All required sampling and distribution assumptions are satisfied.',
[P('State the null and alternative hypotheses, and give the decision at the 5% level.',A('$H_0:\\mu_A=\\mu_B$ and $H_1:\\mu_A\\ne\\mu_B$.'),Rr('$0.032<0.05$, so reject $H_0$.')),
 P('Give the decision at the 1% level and explain why the two decisions are consistent.',Rr('$0.032>0.01$, so do not reject $H_0$ at 1%.'),Rr('The 1% level demands stronger evidence; a result can meet 5% without meeting 1%.')),
 P('A report says, “There is a 3.2% probability that the brands have equal mean lifetimes.” Explain the error.',Rr('The p-value is calculated assuming the null hypothesis is true.'),Rr('It measures how unusual results at least as extreme would be under that assumption; it is not the probability that the null hypothesis is true.'))],
bars('Decision thresholds and reported p-value',[.01,.032,.05],['1% level','p-value','5% level'],'Probability'),
[('5 percent decision',.032<.05,True),('1 percent decision',.032>.01,True)])

add('sp','An unknown probability in a discrete model','Probability','4.7',
r'A repair time X, in hours, has values 1, 2, 4 and 6 with probabilities $0.20$, $a$, $0.45-a$ and $0.35$ respectively. The mean repair time is 3.8 hours.',
[P('Find $a$ and verify that the resulting probabilities form a valid distribution.',M('Use $0.2+2a+4(0.45-a)+6(0.35)=3.8$.'),A('$a=0.15$; probabilities $0.20,0.15,0.30,0.35$ are nonnegative and sum to 1.')),
 P('Find the probability that a repair takes more than 2 hours and the conditional probability it takes 6 hours, given it takes more than 2 hours.',M('The conditioning event has probability $0.30+0.35=0.65$.'),A('$P(X>2)=0.65$; $P(X=6\\mid X>2)=0.35/0.65=7/13$.')),
 P('A repair company promises that at least 70% of repairs finish within 4 hours. Assess the promise using this model.',M('$P(X\\leq4)=0.20+0.15+0.30=0.65$.'),Rr('The model predicts only 65%, so it does not support the 70% promise.'))],
flow('Repair-time probability model',['1 h: 0.20','2 h: a','4 h: 0.45 - a','6 h: 0.35']),
[('expected repair time',.2+2*.15+4*.3+6*.35,3.8),('distribution sum',.2+.15+.3+.35,1)])

# CALCULUS — no SL kinematics; polynomial rules, optimisation and positive areas.
def diff(f,x):return (f(x+.0001)-f(x-.0001))/.0002

add('ca','Comparing average and instantaneous filling rates','Gradients and rates of change','5.3',
r'The volume of water in a tank is modelled by $V(t)=200+18t+3t^2$ litres for $0\leq t\leq6$, where $t$ is minutes after filling begins.',
[P('Find the instantaneous filling rate at $t=4$, including units.',M('$V\\prime(t)=18+6t$.'),A('$V\\prime(4)=42$ litres per minute.')),
 P('Find the average rate of increase from $t=0$ to $t=6$.',M('Use $[V(6)-V(0)]/6$.'),A('$36$ litres per minute.')),
 P('Find when the instantaneous rate equals this average rate, and explain why it occurs before $t=4$.',M('Solve $18+6t=36$.'),A('$t=3$ minutes.'),Rr('The rate is increasing linearly, and its value at the middle of the interval is its average over the interval.'))],
plot('Tank volume during filling',fn=lambda t:200+18*t+3*t*t,domain=(0,6),xlabel='Time (min)',ylabel='Volume (L)'),
[('derivative check',diff(lambda t:200+18*t+3*t*t,4),42),('secant rate',((200+18*6+3*36)-200)/6,36)])

add('ca','Tangent and normal to a landscaping profile','Polynomial differentiation','5.4',
r'A landscape profile is $y=0.2x^2-0.8x+3$, in metres, for $0\leq x\leq6$. A support is to follow the normal to the curve at $x=4$.',
[P('Find the point on the profile at $x=4$ and the tangent gradient there.',M('$y\\prime=0.4x-0.8$ and evaluate $y(4)$.'),A('Point $(4,3)$; tangent gradient $0.8$.')),
 P('Find the equation of the normal.',M('Normal gradient is the negative reciprocal, $-1.25$.'),A('$y-3=-1.25(x-4)$.')),
 P('Find where this normal meets ground level $y=0$, and state whether that point lies within the model’s horizontal domain.',M('Solve $-3=-1.25(x-4)$.'),A('$x=6.4$.'),Rr('It lies outside $0\\leq x\\leq6$, so the ground connection is beyond the modelled section.'))],
plot('Landscape profile',fn=lambda x:.2*x*x-.8*x+3,domain=(0,6),xlabel='Horizontal distance (m)',ylabel='Height (m)'),
[('tangent derivative',diff(lambda x:.2*x*x-.8*x+3,4),.8),('normal intersection',-1.25*(6.4-4)+3,0)])

add('ca','Fencing three sides beside a river','Optimisation','5.7',
r'A farmer has 120 m of fencing for three sides of a rectangular enclosure beside a straight river. The fourth side needs no fence. Let each perpendicular side have length $x$ metres.',
[P('Express the unfenced-side length and enclosure area in terms of $x$, with a suitable domain.',M('The fenced sides give $2x+y=120$.'),A('$y=120-2x$ and $A=120x-2x^2$, for $0<x<60$.')),
 P('Use differentiation to find the dimensions giving the maximum area.',M('$A\\prime=120-4x=0$ gives $x=30$.'),A('Dimensions 30 m by 60 m; area $1800$ square metres.'),Rr('The derivative changes from positive to negative at 30, so this is a maximum.')),
 P('A vehicle requires a 4 m gate within one perpendicular side. If the gate replaces fencing and its width is additional to the 120 m fence supply, find the new maximum area.',M('The total enclosed three-side length becomes 124, so $A=x(124-2x)$.'),A('Maximum at $x=31$, $y=62$; area $1922$ square metres.'))],
geom('Three fenced sides and a river',[(0,0),(60,0),(60,30),(0,30)],[(0,1),(1,2),(3,0)],['A','B','C','D'],['AD = BC = x; AB = y; CD is the river boundary','Fencing available: 120 m']),
[('max derivative',120-4*30,0),('gate maximum',31*62,1922)])

root=(30-math.sqrt(300))/6
add('ca','Cutting an open box from card','Optimisation','5.7',
r'Identical squares of side $x$ cm are cut from each corner of a 20 cm by 10 cm card. The remaining flaps are folded up to make an open rectangular box.',
[P('Write the box volume and a suitable domain.',M('The dimensions are $x$, $20-2x$ and $10-2x$.'),A('$V=x(20-2x)(10-2x)=200x-60x^2+4x^3$, for $0<x<5$.')),
 P('Use differentiation to find the cut size giving maximum volume.',M('$V\\prime=200-120x+12x^2$; solve $V\\prime=0$ and reject the root outside the domain.'),A(f'$x=(30-10\\sqrt3)/6={root:.6g}$ cm.'),Rr('The derivative changes from positive to negative at this valid root.')),
 P('Find the maximum volume and the percentage increase over using 1 cm corner squares.',M('Evaluate the original volume formula at the maximizing cut size and at $x=1$.'),A(f'Maximum ${root*(20-2*root)*(10-2*root):.6g}$ cubic centimetres; increase ${100*(root*(20-2*root)*(10-2*root)/144-1):.6g}\\%$.'))],
geom('Card before folding',[(0,0),(20,0),(20,10),(0,10)],[(0,1),(1,2),(2,3),(3,0)],['A','B','C','D'],['20 cm by 10 cm card','Remove x by x squares from all four corners']),
[('stationary cut',200-120*root+12*root*root,0),('one cm box',1*18*8,144)])

rr=(500/math.pi)**(1/3);hh=500/(math.pi*rr**2)
add('ca','Minimizing material for an open cylindrical container','Optimisation','5.7',
r'An open cylindrical container must hold 500 cubic centimetres. Its radius is $r$ cm and its height is $h$ cm. The base and curved side use the same material; there is no lid.',
[P(r'Show that the surface area can be written $S(r)=\pi r^2+1000/r$, for $r>0$.',M('Use $h=500/(\\pi r^2)$ from the volume constraint.'),M('Substitute into $S=\\pi r^2+2\\pi rh$ and simplify.')),
 P('Find the radius and height minimizing surface area.',M('$S\\prime=2\\pi r-1000r^{-2}$; set equal to zero.'),A(f'$r={rr:.6g}$ cm and $h={hh:.6g}$ cm.'),Rr('For positive r, multiplying the derivative by positive r squared preserves its sign. Its sign is that of $2\\pi r^3-1000$, which changes from negative to positive at this radius.')),
 P('Explain the relationship between optimal height and radius and find the minimum area.',M('The stationary equation gives $2\\pi r^3=1000$, hence $h=r$.'),A(f'Minimum area ${math.pi*rr**2+1000/rr:.6g}$ square centimetres.'))],
geom('Open cylinder axial cross-section',[(-2,0),(2,0),(2,4),(-2,4)],[(0,1),(1,2),(3,0)],['','','',''],['Width = 2r; height = h','Open top; fixed volume 500 cubic centimetres']),
[('volume constraint',math.pi*rr*rr*hh,500),('area derivative',2*math.pi*rr-1000/rr**2,0),('optimal ratio',hh/rr,1)])

add('ca','A stationary point outside the operating range','Optimisation','5.6',
r'A workshop’s daily profit is $P(x)=-x^3+12x^2-36x+100$, where $x$ is production in hundreds of items. For contractual reasons it must operate with $1\leq x\leq3$.',
[P('Find all stationary values of $x$ for the polynomial.',M('$P\\prime=-3x^2+24x-36=-3(x-2)(x-6)$.'),A('$x=2$ and $x=6$.')),
 P('Determine the greatest daily profit on the permitted domain.',M('Compare $P(1)=75$, $P(2)=68$ and $P(3)=73$.'),A('Greatest permitted profit is 75 at $x=1$.')),
 P('Explain why selecting the stationary point $x=6$ as the answer would be incorrect even though it is a local maximum of the polynomial.',Rr('$x=6$ is outside the permitted interval $[1,3]$.'),Rr('A constrained optimum must consider the permitted endpoints as well as stationary points inside the domain.'))],
plot('Profit over the permitted operating interval',fn=lambda x:-x**3+12*x*x-36*x+100,domain=(1,3),yrange=(60,80),xlabel='Production (hundreds)',ylabel='Profit'),
[('stationary2',-3*4+24*2-36,0),('endpoint1',-1+12-36+100,75),('endpoint3',-27+108-108+100,73)])

add('ca','Using a rate graph to compare production levels','Gradients and rates of change','5.2',
r'The derivative of cumulative production F is $F\prime(t)=t^2-6t+8$ units per hour, for $0\leq t\leq5$. The derivative graph is shown. The quantity F here represents a net production balance and can decrease.',
[P('Find the intervals on which F is increasing and decreasing.',M('Factor $F\\prime=(t-2)(t-4)$ and determine signs.'),A('Increasing for $0<t<2$ and $4<t<5$; decreasing for $2<t<4$.')),
 P('Classify the stationary points of F.',Rr('At $t=2$ the derivative changes positive to negative, giving a local maximum.'),Rr('At $t=4$ it changes negative to positive, giving a local minimum.')),
 P('A student says F is zero at both 2 and 4 because the graph crosses the axis there. Explain the mistake.',Rr('The plotted graph is of the derivative, not F.'),Rr('The crossings show zero rates of change, not zero values of the cumulative balance.'))],
plot('Derivative of the net production balance',fn=lambda t:t*t-6*t+8,domain=(0,5),yrange=(-2,9),xlabel='Time (h)',ylabel='F prime (units/h)'),
[('rate roots',2**2-6*2+8,0),('middle rate',3**2-6*3+8,-1),('end increasing',5**2-6*5+8,3)])

add('ca','Accumulated water supply and average flow','Definite integration','5.5',
r'Water enters a reservoir at rate $q(t)=12+3t-t^2/4$ cubic metres per hour, for $0\leq t\leq8$. The reservoir initially contains 100 cubic metres and has no outflow during this period.',
[P('Find the volume entering over the eight hours.',M('Set up $\\int_0^8(12+3t-t^2/4)\\,dt$.'),M('An antiderivative is $12t+1.5t^2-t^3/12$.'),A('$448/3=149.333\\ldots$ cubic metres.')),
 P('Find the final stored volume and the average inflow rate.',M('Add the initial volume; divide entering volume by eight for the average rate.'),A('Final $748/3=249.333\\ldots$ cubic metres; average $56/3=18.6667\\ldots$ cubic metres per hour.')),
 P('Explain why $q(8)$ multiplied by eight does not give the entering volume.',Rr('The rate changes over the interval.'),Rr('Using the final rate treats all eight hours as though the flow had always been 20 cubic metres per hour.'))],
plot('Reservoir inflow rate',fn=lambda t:12+3*t-t*t/4,domain=(0,8),xlabel='Time (h)',ylabel='Flow (m3/h)'),
[('inflow integral',simpson(lambda t:12+3*t-t*t/4,0,8),448/3),('final rate',12+24-16,20)])

add('ca','Estimating the area of a pond','Trapezoidal rule','5.8',
r'A surveyor measures the width of a pond perpendicular to a 60 m baseline at equal 10 m intervals. The widths are in metres.'+table(zip([0,10,20,30,40,50,60],[0,12,18,20,15,9,0]),['Distance along baseline','Pond width']),
[P('Use the trapezoidal rule to estimate the pond’s area.',M('Use $\\frac{10}{2}[0+0+2(12+18+20+15+9)]$.'),A('$740$ square metres.')),
 P('The average water depth is estimated at 1.4 m. Estimate the pond volume and the litres of water it contains.',M('Multiply the estimated area by depth and use 1000 litres per cubic metre.'),A('$1036$ cubic metres, or $1.036\\times10^6$ litres.')),
 P('Explain why halving the baseline interval may improve the estimate but does not by itself remove uncertainty in the volume.',Rr('More cross-sections can represent curved pond edges more accurately.'),Rr('The average-depth estimate and measurement errors remain sources of uncertainty.'))],
plot('Measured pond widths',pts=list(zip([0,10,20,30,40,50,60],[0,12,18,20,15,9,0])),domain=(0,60),xlabel='Baseline distance (m)',ylabel='Width (m)'),
[('trapezoid area',sum(10*(a+b)/2 for a,b in zip([0,12,18,20,15,9],[12,18,20,15,9,0])),740)])

add('ca','Trapezoids on a curved cross-section','Trapezoidal rule','5.8',
r'The cross-sectional depth of a water channel is $d(x)=4-0.1x^2$ metres, for $-4\leq x\leq4$. The depth is positive throughout this interval.',
[P('Estimate the cross-sectional area using four trapezoids of equal width.',M('Use $x=-4,-2,0,2,4$ with depths $2.4,3.6,4,3.6,2.4$.'),M('The sum is $2[0.5(2.4)+3.6+4+3.6+0.5(2.4)]$.'),A('$A_T=27.2$ square metres.')),
 P('Find the exact model area by integration and the percentage error in the trapezoidal estimate.',M('Evaluate $\\int_{-4}^4(4-0.1x^2)\\,dx$.'),A('Exact area $416/15=27.7333\\ldots$ square metres.'),M('Divide the absolute difference by the exact area and multiply by 100.'),A('The estimate is low by $8/15$ square metres, giving $25/13=1.92308\\ldots\\%$ error.')),
 P('Use the shape of the graph to explain the direction of error.',Rr('The straight chords joining adjacent points lie below the concave-down curve.'),Rr('Therefore the trapezoids underestimate the positive area.'))],
plot('Channel depth model',fn=lambda x:4-.1*x*x,domain=(-4,4),yrange=(0,5),xlabel='Horizontal position (m)',ylabel='Depth (m)'),
[('four trapezoids',2*(1.2+3.6+4+3.6+1.2),27.2),('exact area',simpson(lambda x:4-.1*x*x,-4,4),416/15)])

add('ca','Recovering a total from its marginal model','Polynomial differentiation','5.3',
r'A firm’s total production cost C satisfies $C\prime(x)=0.06x^2-1.2x+18$, where $x$ is the number of units made. The fixed cost is $C(0)=250$. Consider $0\leq x\leq30$.',
[P('Find the total cost function.',M('Integrate each term and include a constant.'),A('$C(x)=0.02x^3-0.6x^2+18x+250$.')),
 P('Find the total cost of making 20 units and the cost of increasing production from 20 to 21 units.',M('Evaluate $C(20)$ and $C(21)-C(20)$.'),A('$C(20)=530$; additional cost $18.62$.')),
 P(r'Compare this additional cost with $C\prime(20)$ and explain the difference.',M('$C\\prime(20)=18$.'),Rr('The derivative is the instantaneous marginal cost at exactly 20 units; the finite one-unit change averages the changing marginal cost over $20\\leq x\\leq21$.'))],
plot('Marginal cost model',fn=lambda x:.06*x*x-1.2*x+18,domain=(0,30),xlabel='Units produced',ylabel='Marginal cost'),
[('total at20',.02*20**3-.6*20**2+18*20+250,530),('one unit additional',(.02*21**3-.6*21**2+18*21+250)-530,18.62),('marginal integral',simpson(lambda x:.06*x*x-1.2*x+18,20,21),18.62)])

add('ca','A rate model with an unknown initial amount','Definite integration','5.5',
r'A chemical process adds a substance to a vessel at rate $r(t)=6t^2-4t+5$ grams per minute, for $0\leq t\leq3$. There is no loss. At $t=2$ the vessel contains 45 grams.',
[P('Find the amount added during the first two minutes.',M('Evaluate $\\int_0^2(6t^2-4t+5)\\,dt$.'),A('$18$ grams.')),
 P('Find the initial amount and the amount at $t=3$.',M('Subtract the first-two-minute addition from 45, then add the first-three-minute addition.'),A('Initial amount $27$ grams; amount at 3 minutes $78$ grams.')),
 P('Explain why integrating the rate without using an observed amount cannot determine the total amount in the vessel.',Rr('The integral determines changes in amount.'),Rr('An initial or reference amount is needed to determine the additive constant.'))],
plot('Addition rate in the vessel',fn=lambda t:6*t*t-4*t+5,domain=(0,3),xlabel='Time (min)',ylabel='Addition rate (g/min)'),
[('two minute addition',simpson(lambda t:6*t*t-4*t+5,0,2),18),('three minute total',27+simpson(lambda t:6*t*t-4*t+5,0,3),78)])

add('ca','An area requirement for a curved sign','Definite integration','5.5',
r'A sign occupies the region under $y=6-x^2$ and above the horizontal axis from $x=0$ to $x=a$, where $0<a<\sqrt6$. Distances are in metres. The required sign area is 8 square metres.',
[P('Write an equation satisfied by $a$.',M('Set $\\int_0^a(6-x^2)\\,dx=8$.'),A('$6a-a^3/3=8$.')),
 P('Use technology to find $a$ within its physical domain.',M('Solve the cubic on $0<a<\\sqrt6$.'),A(f'$a={bisect(lambda a:6*a-a**3/3-8,0,math.sqrt(6)):.6g}$ m.')),
 P('Explain why roots outside this domain cannot be used, and determine whether the required area is feasible.',Rr('Beyond $\\sqrt6$ the curve is below the horizontal axis and does not define the stated positive sign region.'),M('The greatest possible area is $\\int_0^{\\sqrt6}(6-x^2)dx=4\\sqrt6$.'),Rr('$4\\sqrt6\\approx9.80>8$, so the requested area is feasible.'))],
plot('Positive curved sign profile',fn=lambda x:6-x*x,domain=(0,math.sqrt(6)),yrange=(0,7),xlabel='Horizontal distance (m)',ylabel='Height (m)'),
[('maximum positive area',simpson(lambda x:6-x*x,0,math.sqrt(6)),4*math.sqrt(6))])

add('ca','A fixed-area garden with unequal fencing costs','Optimisation','5.7',
r'A rectangular garden has area 96 square metres. One pair of opposite sides has fencing costing 18 per metre; the other pair costs 8 per metre. Let $x$ be the length of each expensive side.',
[P('Write the total fencing cost as a function of $x$.',M('The other dimension is $96/x$.'),A('$C(x)=36x+1536/x$, for $x>0$.')),
 P('Use differentiation to find the dimensions minimizing the cost.',M('$C\\prime=36-1536x^{-2}=0$.'),A(f'Expensive sides ${math.sqrt(1536/36):.6g}$ m; other sides ${96/math.sqrt(1536/36):.6g}$ m.'),Rr('The derivative changes from negative to positive, giving a minimum.')),
 P('Explain why a square garden is not optimal and find the saving compared with a square.',M('A square has side $\\sqrt{96}$ and cost $52\\sqrt{96}$.'),A(f'Saving ${52*math.sqrt(96)-(36*math.sqrt(1536/36)+1536/math.sqrt(1536/36)):.6g}$.'),Rr('The expensive sides should be shorter, even though this increases the cheaper sides.'))],
geom('Fixed-area rectangular garden',[(0,0),(12,0),(12,8),(0,8)],[(0,1),(1,2),(2,3),(3,0)],['A','B','C','D'],['AB and CD cost 18 per metre; AD and BC cost 8 per metre','Area = 96 square metres; expensive-side length = x']),
[('optimal derivative',36-1536/(1536/36),0),('optimal area',math.sqrt(1536/36)*(96/math.sqrt(1536/36)),96)])

add('ca','A tangent approximation for a calibration curve','Polynomial differentiation','5.4',
r'A measuring device’s output is $f(x)=x^3/10+2x+5$, for $0\leq x\leq5$. Near $x=2$, an engineer uses the tangent line to approximate the output.',
[P('Find the tangent line at $x=2$.',M('$f(2)=9.8$ and $f\\prime(x)=0.3x^2+2$, so $f\\prime(2)=3.2$.'),A('$L(x)=9.8+3.2(x-2)$.')),
 P('Use the tangent line to estimate $f(2.2)$ and find the absolute error.',M('The tangent estimate is $10.44$; evaluate the actual cubic at 2.2.'),A('$f(2.2)=10.4648$; absolute error $0.0248$.')),
 P('Explain from the graph why the tangent underestimates near $x=2$, and why it should not be assumed reliable at $x=5$.',Rr('The curve bends upward near the contact point, so it lies above its tangent nearby.'),Rr('A tangent uses local slope information; far from the contact point the curve’s changing slope can create a large error.'))],
plot('Calibration curve and local tangent',fn=lambda x:x**3/10+2*x+5,domain=(0,5),xlabel='Input',ylabel='Output',extra=[('Tangent',[(0,3.4),(5,19.4)])]),
[('derivative finite difference',diff(lambda x:x**3/10+2*x+5,2),3.2),('tangent error',2.2**3/10+4.4+5-(9.8+3.2*.2),.0248)])

add('ca','Optimising an advertisement with a minimum margin','Optimisation','5.7',
r'A rectangular poster has total area 600 square centimetres. The printed region must leave 2 cm margins at the left and right and 3 cm at the top and bottom. Let the poster width be $x$ cm.',
[P('Write the printed area in terms of $x$ and give a suitable domain.',M('Poster height is $600/x$; printed dimensions are $x-4$ and $600/x-6$.'),A('$A(x)=624-6x-2400/x$, with $4<x<100$.')),
 P('Find the poster dimensions that maximize printed area.',M('$A\\prime=-6+2400x^{-2}=0$.'),A('Width $20$ cm and height $30$ cm.'),Rr('The derivative is positive before 20 and negative after 20, so this is a maximum.')),
 P('Find the fraction of the poster that is printed and compare the width-to-height ratio with the ratio of total horizontal to total vertical margins.',M('Printed region is $16\\times24=384$ square centimetres.'),A('Printed fraction $384/600=0.64$; poster ratio $20:30=2:3$, equal to the margin ratio $4:6$.'))],
geom('Poster and required margins',[(0,0),(20,0),(20,30),(0,30)],[(0,1),(1,2),(2,3),(3,0)],['','','',''],['Total area 600 cm2; left/right margins 2 cm each','Top/bottom margins 3 cm each; poster width x']),
[('stationary width',-6+2400/20**2,0),('printed fraction',(20-4)*(30-6)/600,.64)])

add('ca','A zero derivative without a local maximum','Gradients and rates of change','5.6',
r'A temperature adjustment profile is $T(x)=(x-2)^3+18$ over $0\leq x\leq4$. The graph is shown. This is a mathematical calibration model, not a temperature-time experiment.',
[P('Find the stationary point.',M('$T\\prime(x)=3(x-2)^2=0$ gives $x=2$.'),A('The stationary point is $(2,18)$.')),
 P('Explain why this stationary point is neither a local maximum nor a local minimum.',M('$T\\prime(x)>0$ on both sides of 2.'),Rr('The function increases through the point rather than changing from increasing to decreasing or vice versa.')),
 P(r'Find the minimum and maximum on the stated domain, and explain why solving $T\prime=0$ alone misses both.',M('Evaluate $T(0)=10$ and $T(4)=26$.'),A('Minimum 10 at $x=0$; maximum 26 at $x=4$.'),Rr('For a restricted closed interval, endpoints must also be considered.'))],
plot('Cubic calibration profile',fn=lambda x:(x-2)**3+18,domain=(0,4),yrange=(8,28),xlabel='Input x',ylabel='Adjusted value'),
[('flat point derivative',diff(lambda x:(x-2)**3+18,2),0),('endpoint range',(4-2)**3+18,26)])

add('ca','Finding an unknown coefficient from an accumulated output','Definite integration','5.5',
r'A pump supplies water at rate $q(t)=at^2+4$ litres per minute over $0\leq t\leq3$, where $a>0$. The total supplied over the three minutes is 30 litres.',
[P('Find $a$.',M('Use $\\int_0^3(at^2+4)\\,dt=9a+12=30$.'),A('$a=2$.')),
 P('Find when the supply rate is 12 litres per minute.',M('Solve $2t^2+4=12$ within the stated domain.'),A('$t=2$ minutes.')),
 P('Find the fraction of the total supply delivered in the final minute, and explain why it exceeds one third.',M('Evaluate $\\int_2^3(2t^2+4)\\,dt=50/3$.'),A('Fraction $(50/3)/30=5/9$.'),Rr('The rate increases with time, so the final equal-duration interval supplies more than the average interval.'))],
flow('Unknown-coefficient pump model',['Initial rate: 4','q(t) = at squared + 4','0 to 3 minutes','Total: 30 L']),
[('total supplied',simpson(lambda t:2*t*t+4,0,3),30),('last minute',simpson(lambda t:2*t*t+4,2,3),50/3)])

half=bisect(lambda t:2*t+t*t/2-15,0,6)
add('ca','When has half the total amount arrived?','Definite integration','5.5',
r'A delivery system supplies material at rate $q(t)=2+t$ tonnes per hour for $0\leq t\leq6$. There is no supply before $t=0$.',
[P('Find the total material supplied over six hours.',M('Evaluate $\\int_0^6(2+t)\\,dt$.'),A('$30$ tonnes.')),
 P('Find the time by which half this total has been supplied.',M('Solve $\\int_0^t(2+u)\\,du=15$, giving $2t+t^2/2=15$.'),A(f'$t=-2+\\sqrt{{34}}={-2+math.sqrt(34):.6g}$ hours.')),
 P('Explain why half the total does not arrive by the halfway time $t=3$, and calculate the fraction that has arrived then.',M('At $t=3$, the supplied amount is $6+4.5=10.5$ tonnes.'),A('$10.5/30=0.35$.'),Rr('The increasing rate puts more of the total into the later hours.'))],
plot('Material supply rate',fn=lambda t:2+t,domain=(0,6),xlabel='Time (h)',ylabel='Supply (tonnes/h)'),
[('total area',simpson(lambda t:2+t,0,6),30),('half delivery equation',2*(-2+math.sqrt(34))+(-2+math.sqrt(34))**2/2,15)])

add('ca','A slope limit on a polynomial path','Polynomial differentiation','5.3',
r'A path profile is $h(x)=0.002x^3-0.03x^2+0.15x+1$ metres, for $0\leq x\leq10$. Its gradient must be at most 0.10 for a certain maintenance vehicle. The gradient is nonnegative throughout this domain.',
[P('Find the gradient function and its smallest value.',M('$h\\prime(x)=0.006x^2-0.06x+0.15=0.006(x-5)^2$.'),A('Smallest gradient 0 at $x=5$.')),
 P('Find the section on which the gradient is at most 0.10.',M('Solve $0.006(x-5)^2\\leq0.10$.'),A('$5-\\sqrt{50/3}\\leq x\\leq5+\\sqrt{50/3}$, approximately $0.918\\leq x\\leq9.08$ m.')),
 P('Can the vehicle follow the entire modelled path without exceeding the limit? Justify with a calculation.',M('At either endpoint the gradient is $0.006(25)=0.15$.'),Rr('No. The two end sections exceed the 0.10 limit even though the central section meets it.'))],
plot('Gradient along the path',fn=lambda x:.006*(x-5)**2,domain=(0,10),yrange=(0,.18),xlabel='Distance x (m)',ylabel='Gradient'),
[('derivative finite difference',diff(lambda x:.002*x**3-.03*x*x+.15*x+1,2),.006*(2-5)**2),('gradient bound',.006*math.sqrt(50/3)**2,.1)])

# Current-course corrections and concise publication rules.
for q in Q:
    if q['syllabusCode']=='2.7':q['syllabusCode']='2.6'
    if q['topicId']=='functions' and q['syllabusCode']=='2.3':q['syllabusCode']='2.2'
    q['stem']+='\n\nUse technology where appropriate. Retain unrounded values until the final answer; give non-exact numerical answers to three significant figures unless money or another precision is specified.'
assert len(Q)==100 and counts==Counter({'na':20,'fn':20,'gt':20,'sp':20,'ca':20}),counts
assert len({q['id'] for q in Q})==100
out=R/'content/ib/math-2026-expansion/ai-sl.json';out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(Q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
review={'course':'math-ai-sl','date':'2026-11-02','status':'author self-review complete; independent review required before release','questions':100,'medium':50,'hard':50,'diagrams':100,'topicCounts':dict(counts),'specification':'First assessment 2021, course through November 2028','officialGuide':'https://ibo.org/globalassets/new-structure/university-admission/pdfs/dp-mathematics-applications-and-interpretation-guide-en.pdf','originality':'100 independently authored problem structures; no official question text reused','checks':AUD,'marking':'Distinct M1/A1/R1 steps; all part totals derived from steps; valid alternative methods and correct follow-through should receive credit where the altered values remain valid.','limitations':'Author and computational review are not moderation by a human IB examiner. Diagrams are original SVG and need final portal rendering review.'}
rp=R/'docs/ib-2026-maths/ai-sl-author-review.json';rp.parent.mkdir(parents=True,exist_ok=True);rp.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'questions':len(Q),'diagrams':sum(bool(q.get('diagramSvg')) for q in Q),'topicCounts':dict(counts),'numericalAssertions':sum(len(a['checks']) for a in AUD)}))
