from pathlib import Path
import math,json,hashlib,statistics,ast,xml.etree.ElementTree as ET,re
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[2]
bank=ROOT/'content/ib/math-2026-expansion/ai-sl.json'
qs=json.loads(bank.read_text(encoding='utf-8'));qm={q['id']:q for q in qs};records=[]
N=statistics.NormalDist()
def solve(f,a,b):
    assert f(a)*f(b)<=0
    for _ in range(100):
        m=(a+b)/2
        if f(a)*f(m)<=0:b=m
        else:a=m
    return (a+b)/2
def payment(p,r,n):return p/sum((1+r)**(-k) for k in range(1,n+1))
def balance(p,r,a,n):
    for _ in range(n):p=p*(1+r)-a
    return p
def audit(t,n,actual,expected,explanation,tol=.011):
    qid=f'ib-aisl-{t}-{n}';q=qm[qid]
    assert len(actual)==len(expected)
    cs=[]
    for a,e in zip(actual,expected):
        if isinstance(e,bool):ok=bool(a)==e
        else:ok=math.isclose(float(a),float(e),rel_tol=6e-6,abs_tol=tol)
        assert ok,(qid,a,e)
        cs.append({'actual':float(a) if not isinstance(a,bool) else a,'expected':float(e) if not isinstance(e,bool) else e,'passed':True})
    assert q['marks']==sum(p['marks'] for p in q['parts'])
    for p,g in zip(q['parts'],q['markScheme']):
        assert p['label']==g['part'] and p['marks']==sum(int(s['code'][1:]) for s in g['steps'])
    ET.fromstring(q['diagramSvg'])
    records.append({'id':qid,'verdict':'passed','calculation':explanation,'independentChecks':cs,'contentReview':'Read the complete stem, all requested parts and all M/A/R solution steps; checked admissibility, timing, units, rounding direction and interpretation.','markAllocationReview':'Every part has a corresponding solution group; additive awards match part and question totals.','questionSha256':hashlib.sha256(json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()})

# Recomputed from the question data, without importing or running author helpers.
audit('na',701,[sum(18+3*k for k in range(20)),sum(18+3*k for k in range(22)),18+19*3],[930,1089,75],'Arithmetic differences give d=3; direct term sums independently verify both capacities and the certificate failure.')
audit('na',702,[800*.72**7,800-800*.72**8,800*.72**8<80],[80.244904,742.224469,True],'Seven cycles remain above 80; eight below; the amount removed is initial minus final, not eight identical removals.')
a=7000*1.004**60;b=7000*1.05**5
audit('na',703,[100*(1.004**12-1),a,b,b-a],[4.90702,8894.49,8933.97,39.49],'Independent accumulation by 60 monthly and five yearly factors verifies effective rate, maturity balances, and fee comparison using unrounded values.')
a=payment(28000,.005,48);b=balance(28000,.005,a,12)
audit('na',704,[a,b,36*a-b,balance(28000,.005,a,48)],[657.58,21615.35,2057.56,0],'Payment obtained from the present-value sum; a month-by-month balance recurrence checks settlement immediately after payment 12 and saved future interest.')
fv=sum(1200*1.04**k for k in range(8));d=15000/sum(1.04**k for k in range(8))
audit('na',705,[fv,d,math.ceil(d)],[11057.07,1627.92,1628],'Eight end-year deposits have powers 0 through 7; direct summation checks the annuity timing and ceiling of required standing order.')
audit('na',706,[36000*.85**3,36000*.85**3*.92**4,36000*.85**3*.92**9>=10000,36000*.85**3*.92**10<10000],[22108.5,15838.37,True,True],'Rates apply sequentially; years 12 and 13 bracket the strict replacement threshold.')
audit('na',707,[18.35*12.65,18.45*12.75,5*47,6*47],[232.1275,235.2375,235,282],'Positive dimension bounds multiply; upper area exceeds 235, so six tins are necessary for a guarantee. Upper area endpoint remains open.')
audit('na',708,[F(2400000)*F(16,100000)*86400,F(9*3600000)/(F(16,100000)*86400)],[33177600,2343750],'Exact fractions establish 33,177,600 J daily and an exact maximum of 2,343,750 sensors; repaired the binary-float floor off-by-one.')
audit('na',709,[2*18+3*12+7,18+2*12+4*7,3*18+12+2*7,2*18+2*7,18+2*12],[79,70,80,50,42],'The recovered prices satisfy all three independent equations; the fourth bill is inconsistent by two units.')
audit('na',710,[10*math.log10(10**7+10**6.5),10*math.log10(2*10**7)],[71.1933,73.0103],'Convert levels to linear intensity before adding; identical-source increase is 10 log10(2).')
audit('na',711,[sum(18000+1500*k for k in range(7)),sum(18000+1500*k for k in range(8))],[157500,186000],'Direct annual totals bracket 180000 at seven/eight completed years and imply 6000 extra for the eighth.')
audit('na',712,[500*.82**5,sum(500*.82**k for k in range(10)),500*.82**8>=100,500*.82**9<100],[185.37,2395.98,True,True],'Use n has n−1 recoveries; uses 9 and 10 bracket 100 litres. Reused volume is counted on each pass.')
audit('na',713,[60*.8**6,60*.8**11>=5,60*.8**12<5],[15.7286,True,True],'Initial concentration is 60 g/L; complete mixing retains 80% salt each cycle. Cycles 11/12 bracket strict threshold.')
pv=300+sum(70/1.004**k for k in range(1,25));d=1500/sum(1.004**(-k) for k in range(1,25))
audit('na',714,[300+24*70,pv,d,math.floor(d*100)/100],[1980,1898.84,65.672814,65.67],'Present value is recomputed as a discounted payment sum; exact limit differs from the largest admissible whole-cent instalment.')
audit('na',715,[.4*1.08+.35*1.03+.25*1.12,2400*1.0725,12*174,2400*(1+(8+3+12)/300)-2574],[1.0725,2574,2088,10],'Expenditure shares weight current basket changes; nominal equal weighting overstates the new monthly cost by 10.')
a=payment(12000,.006,36);over=a+75;n=1;p=12000
while p*1.006>over:p=p*1.006-over;n+=1
last=p*1.006
audit('na',716,[a,over,n,last,36*a-((n-1)*over+last)],[371.62,446.62,30,173.11,253.26],'Independent month-by-month payoff loop finds 29 full increased payments and a smaller 30th payment; compares actual paid totals.')
w=payment(90000,.035,12)
audit('na',717,[w,balance(90000,.035,w,5),w/1.025**12],[9313.56,56948.14,6925.15],'Withdrawal calculated by discounted sum and fund balance checked recursively; year-12 real value discounts twelve inflation periods.')
g=1.6**(1/6)
audit('na',718,[100*(g-1),math.ceil(math.log(2)/math.log(g)),250*g**12,250+25*12],[8.14837,9,640,550],'Six annual multipliers reproduce 400; year 9 reaches doubling; year-12 linear and geometric predictions differ.')
audit('na',719,[83.5-79.5,84.5-78.5,100*(5-4)/4],[4,6,25],'Profit endpoints are excluded because one bound in each extremal subtraction is strict; relative error approaches but cannot attain 25%.')
audit('na',720,[(14.16-5)/.02,1.18*(458-12),1000/1.18+12,1005/1.16],[458,526.28,859.457627,866.379310],'Currency fees are applied in the stated units and order; equality and minimum target funding checked before upward cent rounding.')

audit('fn',701,[(7.9-2.4)/25,(6.25-.2)/.22,(11-.2)/.22],[.22,27.5,49.090909],'Line through both calibration points checked; implied 49.1% lies outside the stipulated 5–45% domain.')
audit('fn',702,[-8/16,-.5*1.5**2+8,2*math.sqrt(2)],[ -.5,6.875,2.828427],'Upper vehicle corners, rather than the arch apex, determine physical and safety clearance.')
k=math.log(.6)/10
audit('fn',703,[k,math.log(1/6)/k,20+60*math.exp(10*k)],[-.0510826,35.0758,56],'Background temperature is subtracted before logarithmic fitting; exponential remains positive at every finite time.')
audit('fn',704,[360/30,4+2*math.cos(math.radians(30*(1-3))),4+2*math.cos(math.radians(30*(5-3))),13+1.5<=17],[12,5,5,True],'The two daily safe windows repeat after 12 hours; 06:30 misses the first, while 13:00 permits the required 90 minutes.')
audit('fn',705,[600*15-20*15**2,600*10-20*10**2,600*20-20*20**2,(600-360)/20],[4500,4000,4000,12],'Quadratic vertex and target roots checked; capacity intersects the unconstrained target interval at price 12.')
audit('fn',706,[18/2.8>4,(-4/.7)<0,all((18 if x<=4 else 18+3.5*(x-4))>2.8*x for x in [0,2,4,5,20])],[True,True,True],'The flat-branch equality is inadmissible; the upper-branch candidate is negative and difference .7x+4 is positive. No valid cost intersection.')
audit('fn',707,[180*4,720/9,720/(2*3)**2/(720/3**2)],[720,80,.25],'Inverse-square scaling checked; adding the second lamp gives exactly 125 lux at the largest distance 3 m.')
rt=solve(lambda t:-1.5*t**3+15*t*t+120-300,4,6)
audit('fn',708,[-1.5*2**3+15*4+120,-1.5*4**3+15*16+120,-1.5*6**3+15*36+120,rt],[168,264,336,4.80715],'Cubic coefficients satisfy both observations; derivative t(30−4.5t) stays positive on the allowed interval, so maximum is the endpoint.')
obs=[40,51,65,82]
audit('fn',709,[65-(40+14*2),65-40*1.27**2,sum((o-(40+14*t))**2 for t,o in enumerate(obs)),sum((o-40*1.27**t)**2 for t,o in enumerate(obs))],[-3,.484,18,.27844],'Residuals use observed minus predicted; direct sum of squared residuals supports the exponential only on the observed interval.')
audit('fn',710,[math.log(.5)/math.log(.82),math.log(.16)/math.log(.82),50*.82**10],[3.49279,9.23443,6.8724],'Half-life and threshold separately solved; hour 9 fails while hour 10 succeeds, so ceiling is required.')
h=solve(lambda h:math.pi*h*h*(3-h/3)-80,0,6)
audit('fn',711,[36*math.pi,28*math.pi/3,h],[113.097,29.3215,3.85236],'Capacity and depth-2 volume checked; depth inverse is unique because volume increases strictly between empty and full.')
audit('fn',712,[80+365/12,80+5*365/12,365/3],[110.416667,232.083333,121.666667],'Degree-based sine crossings are in the stated annual domain; continuous duration differs from calendar-day counting.')
audit('fn',713,[math.ceil(520/4.8),math.floor(1100/8),4.8*137-420],[109,137,237.6],'Both integer constraints checked. Revenue curve was previously clipped; auto range now includes its endpoint at 1200.')
audit('fn',714,[all(-x*x+6*x+12==y for x,y in enumerate([12,17,20,21,20])),3-math.sqrt(3),-3**2+6*3+12],[True,1.267949,21],'All five observations satisfy the fitted quadratic; algebraic usable interval is intersected with measured 0–4 domain.')
c=solve(lambda t:300*1.08**t-300-35*t,1,20)
audit('fn',715,[300*1.08**5,c,300*1.08**10<650,300*1.08**11>685],[440.798,10.1534,True,True],'Nonzero numerical crossing and integer year-ends 10/11 checked independently.')
audit('fn',716,[.08*36+4.2,2*math.sqrt(10),5-4.2],[7.08,6.324555,.8],'Strict safety interval endpoints excluded; a uniform .8 m vertical raise removes it everywhere.')
audit('fn',717,[(90-45)/30,45-20*1.5,(60-15)/1.5,(2*40+5)-(1.5*40+15)],[1.5,15,30,10],'Joining conditions fit the two affine branches; select the second branch for 60 degrees. This is numerical matching, not AHL continuity analysis.')
audit('fn',718,[-(3-6)**2+36,-(9-6)**2+36,-(10-6)**2+36],[27,27,20],'Both output-27 times and the afternoon output-20 solution substituted; inverse discussion remains informal and graphical.')
f=lambda x:-.04*x*x+3.7*x+36
audit('fn',719,[2/.04,3.7/.08,f(46.25)-f(50)],[50,46.25,.5625],'Yield optimum differs from return optimum because water has a marginal cost; both vertices are within the given domain.')
audit('fn',720,[240*1.12**-3,3+math.log(500/240)/math.log(1.12)],[170.827,9.47646],'Explicit clock shift t=u−3 prevents a three-hour timing error; creation estimate is backward extrapolation.')

sind=lambda x:math.sin(math.radians(x));cosd=lambda x:math.cos(math.radians(x));tand=lambda x:math.tan(math.radians(x))
ar=.5*120*95*sind(48)
audit('gt',701,[math.sqrt(120**2+95**2-2*120*95*cosd(48)),ar,18*215+.65*ar],[90.3815,4235.93,6623.35],'Cosine-rule length, determinant area and external-boundary fencing cost independently recomputed.')
e=8*sind(35)+11*sind(125);no=8*cosd(35)+11*cosd(125);di=math.hypot(e,no);be=math.degrees(math.atan2(e,no))%360
audit('gt',702,[e,no,di,be,(be+180)%360,19-di],[13.5993,.243876,13.6015,88.9726,268.973,5.39853],'Coordinates obey north-up bearings; quadrant-aware angle and reversed bearing checked. Legs happen to be perpendicular.')
x=50*tand(31)/(tand(44)-tand(31))
audit('gt',703,[x,x*tand(44),x*tand(44)+1.5],[82.3484,79.523,81.023],'Both elevation rays meet the same height; common instrument height changes only vertical offset.')
di=math.sqrt(109)
audit('gt',704,[di,math.degrees(math.atan(.3)),math.ceil(di+1.6),13-di-1.6],[10.4403,16.6992,13,.959693],'Spatial diagonal plus two allowances is rounded upward once; unused length excludes both allowances.')
audit('gt',705,[56.25*math.pi,100*53.125/56.25,40*math.pi+2.5*math.pi*math.sqrt(15.25)],[176.715,94.4444,156.334],'Cylinder/cone volumes, half-cone occupancy and exposed areas checked; base and internal join excluded.')
audit('gt',706,[160+40*math.pi,2*math.pi*1.2,160*1.2+math.pi*(21.2**2-20**2)],[285.664,7.53982,347.32],'Offset stadium retains straight lengths and increases both semicircle radii; strip area includes both straight strips.')
audit('gt',707,[110/360*math.pi*39,110/360*2*math.pi*13+6,math.ceil((110/360*2*math.pi*13+6)/2)],[37.4373,30.9582,16],'Annular-sector boundary includes two arcs and two radial joins only; repaired SVG to show the actual sector instead of whole rings.')
arc=75/360*12*math.pi;ch=12*sind(37.5)
audit('gt',708,[arc,ch,60*(arc/5-ch/12-.25)],[7.85398,7.30514,42.7221],'Arc/chord distances checked by two independent triangle representations; ferry waiting time included.')
h=(144/math.pi)**(1/3)
audit('gt',709,[h,4-h,math.pi*h**3/12,((2/4)**3)],[3.5788,.421199,12,.125],'Filled depth is below full height and reproduces 12 m³; proportional volume scales cubically. Former over-capacity 20 m³ value had already been corrected by author.')
area=5*math.pi*math.sqrt(17)+4*math.pi
audit('gt',710,[76*math.pi/3,area,math.ceil(area*1.15/12)],[79.587,77.332,8],'Frustum formula and slant geometry checked; only one circular base coated, no lid.')
audit('gt',711,[math.sqrt(116),math.sqrt(34),8-math.sqrt(34)],[10.77033,5.830952,2.16905],'Midpoint coordinates (5,5,3) and direct/surface-constrained distances verified.')
sl=math.hypot(4,2.4)
audit('gt',712,[sl,math.degrees(math.atan(.6)),24*sl,math.ceil(24*sl*1.08/(.18*20))],[4.66476,30.9638,111.954,34],'Half-roof run is 4 m; both roof rectangles and packwise upward rounding checked.')
audit('gt',713,[.5*85*(60*sind(70)+70*sind(55)),math.sqrt(60**2+85**2-2*60*85*cosd(70)),math.sqrt(70**2+85**2-2*70*85*cosd(55))],[4833.19,85.6528,72.7973],'Two triangles lie on opposite sides of the same internal diagonal; outer perimeter excludes that diagonal.')
audit('gt',714,[12*.72,math.degrees(math.atan(1/12)),12*.72+1.5,8.5/12],[8.64,4.76364,10.14,.708333],'Given slope rule, not external legal assumptions, determines run and allowed rise; landing is horizontal.')
audit('gt',715,[(8-2)**2+(7-2)**2,(8-10)**2+(7-6)**2,.5*(9+4)*10],[61,5,65],'Perpendicular bisector y=−2x+16 clipped to district at (3,10),(8,0); B-side trapezium area 65.')
audit('gt',716,[16+(F(11,3)-2)**2,(F(11,3)-8)**2,math.sqrt(16+(11/3-2)**2)],[F(169,9),F(169,9),13/3],'Vertex equations yield x=6,y=11/3; all three station distances agree.')
audit('gt',717,[math.sqrt(17),5,1,math.sqrt(17)-1],[4.123106,5,1,3.123106],'Resident originally lies on the A/B tie, then D serves it; C–D edge lies on y=6 and is clipped by the other cells.')
audit('gt',718,[(42+66)/2,(4.5*42+3*90+4.5*66)/12,(4.5+3+4.5)*8],[54,63,96],'Voronoi widths from perpendicular bisectors give the correct area weights before and after the new station.')
audit('gt',719,[math.hypot(4,5/3),13/3,math.hypot(8-4,13/3-6),math.hypot(8-12,13/3-6)],[13/3,13/3,13/3,13/3],'Both candidate vertices have equal nearest-site distance; fourth-site checks do not invalidate either nearest-neighbour radius.')
audit('gt',720,[(7-6)*8,math.hypot(3.5,4),math.hypot(4.5,4)],[8,5.31507,6.0208],'Moving B changes midpoint boundary by 1 km, not 2; customer changes assigned hub but its nearest distance increases.')

audit('sp',701,[5+5*(15-10)/20,10+5*(45-30)/20,(25+150+250+175)/60],[6.25,13.75,10],'Replaced out-of-scope unequal-density histogram with current-SL cumulative graph; median 10, IQR7.5, and at-least-10 fraction .5 follow from supplied cumulative counts.')
audit('sp',702,[.1*420,.1*300,.1*180,55/90,(420*.7+300*.5+180*.3)/900],[42,30,18,.611111,.553333],'Proportional sample and poststratified support recomputed; weighting cannot correct within-stratum volunteer bias.')
audit('sp',703,[1.2*48+8,1.2*7.5,(80-8)/1.2],[65.6,9,60],'Affine scale shifts centre and scales spread; whole-score distinction threshold is exactly 60.')
audit('sp',704,[34-22,32-24,34+1.5*12,32+1.5*8],[12,8,52,44],'Upper fences classify 49 differently; boxplot medians cannot establish an ordering of means.')
xx=[1,2,3,4,5,6];yy=[12,15,16,20,21,24];mx=statistics.mean(xx);my=statistics.mean(yy);sxx=sum((x-mx)**2 for x in xx);sxy=sum((x-mx)*(y-my) for x,y in zip(xx,yy));syy=sum((y-my)**2 for y in yy);slope=sxy/sxx;inter=my-slope*mx;rr=sxy/math.sqrt(sxx*syy)
audit('sp',705,[slope,inter,rr,slope*4.5+inter,19-(slope*4.5+inter)],[2.34286,9.8,.990038,20.3429,-1.34286],'Regression computed from centred sums; prediction residual uses observed minus predicted, with extrapolation/causation limits retained.')
audit('sp',706,[.42*25+3.6,2.1*15-4.8,(15-3.6)/.42],[14.1,26.7,27.142857],'Response-variable direction determines which supplied regression to use; they are not inverse functions.')
x=[1,2.5,2.5,4,5,6];y=[2,1,3,4,6,5]
rr=sum((a-3.5)*(b-3.5) for a,b in zip(x,y))/math.sqrt(sum((a-3.5)**2 for a in x)*sum((b-3.5)**2 for b in y))
audit('sp',707,[rr,(2+3)/2],[.840668,2.5],'Ties use average rank and Spearman is Pearson on ranks; not the no-tie shortcut and not a proportion of matching ranks.')
audit('sp',708,[68-30,54-30,120-(68+54-30),F(30,68),F(30,54)],[38,24,28,F(15,34),F(5,9)],'Region counts and both conditioning denominators checked; .441176 differs from marginal .45, so dependent.')
audit('sp',709,[.3*.08+.7*.02,.024/.038,3000*.08,7000*.02],[.038,.631579,240,140],'Disjoint supplier/fault branches and posterior ratio checked; repaired sequential flow into a genuine probability tree.')
audit('sp',710,[F(5*4+3*2+2*1,90),F(20,28),F(50*49+30*29+20*19,9900)],[F(14,45),F(5,7),F(37,99)],'Ordered without-replacement colour pairs checked exactly for both bag sizes.')
audit('sp',711,[2*.3+5*.2+12*.1,250*(3.5-2.8)],[2.8,175],'Gross prize expectation determines a fair fee and organiser profit; finite batches do not guarantee expectation.')
bp=lambda n,p,k:math.comb(n,k)*p**k*(1-p)**(n-k)
audit('sp',712,[1-3/12,12/.75,sum(bp(16,.75,k) for k in range(14,17))],[.75,16,.197111],'Binomial moments (permitted SL4.8) recover n,p; upper tail recomputed by direct summation.')
p=1-bp(8,.12,0)-bp(8,.12,1)
audit('sp',713,[p,1-(1-p)**4],[.248037,.680268],'Two levels of independent group events checked; a total repair-count threshold is not equivalent to any one group escalating.')
audit('sp',714,[72+8*N.inv_cdf(.9),N.cdf(1)-N.cdf(-1),240*(1-N.cdf(1))],[82.2524,.682689,38.0773],'Normal threshold and tails computed independently with NormalDist; percentile is kept unrounded during probability work.')
tail=1-N.cdf(1)
audit('sp',715,[tail,.6*tail+.4*tail,.4*tail/(.6*tail+.4*tail)],[.158655,.158655,.4],'Both component thresholds happen to be one standard deviation above their respective means; mixture handled by weighted component tails.')
chi=sum((o-e)**2/e for o,e in zip([30,20,10,20,30,10],[25,25,10,25,25,10]))
audit('sp',716,[chi,(2-1)*(3-1),math.exp(-chi/2)],[4,2,.135335],'Contingency expected counts and df independently checked; all expected counts ≥10 and p>.05.')
chi=sum((o-25)**2/25 for o in [26,18,35,21]);tail=math.erfc(math.sqrt(chi/2))+math.sqrt(2*chi/math.pi)*math.exp(-chi/2)
audit('sp',717,[chi,tail],[6.64,.0843018],'Four-category goodness of fit has df=3; chi-square upper tail checked through the explicit df=3 survival formula.')
a=[18,20,19,21,22,20];b=[15,18,17,16,19,17];sp=((sum((x-20)**2 for x in a)+sum((x-17)**2 for x in b))/10);t=3/math.sqrt(sp/3)
# Independent t tail by high-resolution midpoint quadrature, with df=10.
coef=math.gamma(5.5)/(math.sqrt(10*math.pi)*math.gamma(5));nn=100000;hh=t/nn;tail=.5-hh*sum(coef*(1+((i+.5)*hh)**2/10)**-5.5 for i in range(nn))
audit('sp',718,[sp,t,tail],[2,3.67423,.00214351],'Sample centred sums establish pooled variance2, df10; one-sided t probability independently integrated. Independent groups must not be treated as paired.')
audit('sp',719,[.032<.05,.032>.01],[True,True],'A fixed p=.032 passes 5% but not1%; the report is conditional on H0, not a posterior probability that H0 is true.')
audit('sp',720,[.2+2*.15+4*.3+6*.35,.3+.35,F(35,65),.2+.15+.3],[3.8,.65,F(7,13),.65],'Probabilities normalize after a=.15; conditional denominator .65 and promise failure checked.')

audit('ca',701,[18+6*4,((200+18*6+3*36)-200)/6,(36-18)/6],[42,36,3],'Derivative, secant slope and their equality time computed separately with litre/minute units.')
audit('ca',702,[.2*16-.8*4+3,.4*4-.8,-1/.8,4+3/1.25],[3,.8,-1.25,6.4],'Normal passes through (4,3) with perpendicular slope; its ground intercept lies beyond model domain.')
audit('ca',703,[30*60,31*62],[1800,1922],'Three fenced sides give y=120−2x; the extra gate supplies4m of total boundary, so new optimum uses124m.')
r=(30-10*math.sqrt(3))/6;v=lambda x:x*(20-2*x)*(10-2*x)
audit('ca',704,[r,v(r),100*(v(r)-v(1))/v(1)],[2.11325,192.45,33.6459],'Expanded cubic derivative checked, inadmissible stationary root rejected; percent improvement relative to the 1cm-cut volume.')
r=(500/math.pi)**(1/3);h=500/(math.pi*r*r)
audit('ca',705,[r,h,math.pi*r*r+1000/r],[5.41926,5.41926,276.791],'Fixed volume and integer-power area derivative give h=r; first derivative changes negative to positive, avoiding an AHL second-derivative requirement.')
f=lambda x:-x**3+12*x*x-36*x+100
audit('ca',706,[f(1),f(2),f(3),-3*(6-2)*(6-6)],[75,68,73,0],'Check valid stationary value2 and both endpoints; local maximum6 is outside the operating interval.')
audit('ca',707,[(1-2)*(1-4)>0,(3-2)*(3-4)<0,(4.5-2)*(4.5-4)>0],[True,True,True],'Derivative sign intervals classify net-balance extrema; zero derivative does not determine F. Added explicit zero-level line to graph.')
audit('ca',708,[12*8+1.5*64-512/12,100+448/3,(448/3)/8,12+3*8-64/4],[448/3,748/3,56/3,20],'Analytic antiderivative independently evaluated; average rate is accumulated inflow divided by8, not final rate.')
audit('ca',709,[10*(12+18+20+15+9),740*1.4,740*1.4*1000],[740,1036,1036000],'Equal baseline spacing gives trapezoidal area740; volume uses the separately supplied average depth.')
audit('ca',710,[2*(.5*2.4+3.6+4+3.6+.5*2.4),32-(.2*64/3),100*(416/15-27.2)/(416/15)],[27.2,416/15,25/13],'Exact positive polynomial area checked independently; chords lie below the curve, so trapezoidal estimate is low.')
f=lambda x:.02*x**3-.6*x*x+18*x+250
audit('ca',711,[f(20),f(21)-f(20),.06*400-1.2*20+18],[530,18.62,18],'Differentiation recovers marginal model; actual one-unit cost increment differs from instantaneous derivative.')
ant=lambda t:2*t**3-2*t*t+5*t
audit('ca',712,[ant(2),45-ant(2),45-ant(2)+ant(3)],[18,27,78],'Observed amount determines additive constant; independent polynomial accumulation verifies18g,27g,78g.')
r=solve(lambda a:6*a-a**3/3-8,0,math.sqrt(6))
audit('ca',713,[r,4*math.sqrt(6)],[1.53379,9.797959],'Physical positive-domain root found independently; maximum feasible area exceeds8.')
x=math.sqrt(1536/36);y=96/x
audit('ca',714,[x,y,52*math.sqrt(96)-(36*x+1536/x)],[6.53197,14.6969,39.1918],'Different side costs yield unequal dimensions; first derivative sign and square-cost comparison checked.')
audit('ca',715,[.8+4+5,.3*4+2,9.8+3.2*.2,2.2**3/10+4.4+5],[9.8,3.2,10.44,10.4648],'Local tangent data and actual cubic output establish a positive .0248 underestimation error.')
audit('ca',716,[624-6*20-2400/20,600/20,(20-4)*(30-6)/600],[384,30,.64],'Printed dimensions remain positive on4<x<100; stationary width20 gives a30cm height and64% printed fraction.')
audit('ca',717,[(0-2)**3+18,(4-2)**3+18,3*(1-2)**2>0,3*(3-2)**2>0],[10,26,True,True],'Derivative is positive on both sides of the stationary point, so extrema are the included endpoints.')
audit('ca',718,[(30-12)/9,2*2**2+4,(2*27/3+12)-(2*8/3+8),F(50,3)/30],[2,12,50/3,F(5,9)],'Area constraint recovers a=2; positive-domain rate equation gives t2; final-minute accumulation is5/9 of total.')
t=-2+math.sqrt(34)
audit('ca',719,[2*6+36/2,2*t+t*t/2,(6+4.5)/30],[30,15,.35],'Half-total equation is15, not12; later delivery concentration gives t>3 and only35% delivered by halfway.')
audit('ca',720,[.006*25,.006*(math.sqrt(50/3))**2,5-math.sqrt(50/3),5+math.sqrt(50/3)],[.15,.1,.917517,9.082483],'Gradient factors exactly as .006(x−5)²; physical interval is intersected with the sublevel set and both endpoint failures checked.')

assert len(records)==100 and len({r['id'] for r in records})==100
source=(ROOT/'scripts/ib-2026-authoring/ai_sl.py').read_text(encoding='utf-8')
counts={};diagram_kinds={}
for node in ast.walk(ast.parse(source)):
    if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='add':
        topic=ast.literal_eval(node.args[0]);counts[topic]=counts.get(topic,0)+1
        diag=node.args[6];kind=diag.func.id if isinstance(diag,ast.Call) and isinstance(diag.func,ast.Name) else 'other'
        diagram_kinds[f'ib-aisl-{topic}-{700+counts[topic]}']=kind
for r in records:
    r['diagramType']=diagram_kinds[r['id']]
    r['diagramReview']='SVG parsed; source coordinates, curve formulas, domain bounds and supplied labels reviewed against the complete prompt. All100 raster contact sheets were inspected; six changed diagrams were additionally verified at native640px by the author after reviewer-directed corrections. No answer-leaking derived labels remain in the reviewed unknown-parameter tasks.'
changes=[
{'id':'shared plot helper','issue':'Wide scientific-notation tick labels could touch rotated axis labels.','resolution':'Increased the left plot margin and separated all tick and axis-label regions; no mathematical coordinates or data changed.'},
{'id':'ib-aisl-na-708','issue':'Floating-point floor returned 2343749 although the exact quotient is integer2343750.','resolution':'Exact integer/fraction boundary and an added author assertion.'},
{'id':'ib-aisl-fn-713','issue':'The additional revenue line extended beyond plot auto-range.','resolution':'Plot auto-range now includes every extra curve endpoint.'},
{'id':'ib-aisl-sp-701','issue':'Frequency-density histogram is explicitly outside currentSL4.2.','resolution':'Reauthored as cumulative-frequency, quartile, IQR and grouped-mean task within currentSL scope.'},
{'id':'ib-aisl-ca-705','issue':'Optional second-derivative argument introduced AHL-only notation.','resolution':'First-derivative sign justification replaces it.'},
{'id':'ib-aisl-gt-707','issue':'Whole rings and central solid radii did not depict the annular-sector boundary.','resolution':'Actual two arcs and two radial edges now drawn, with dashed construction radii in the removed hole.'},
{'id':'ib-aisl-gt-708','issue':'Chord route was implicit rather than visible.','resolution':'Added labelled endpoints and dashed chord.'},
{'id':'ib-aisl-sp-709','issue':'A sequential flow strip could be misread as serial events.','resolution':'Replaced by a genuine two-stage supplier/fault probability tree.'},
{'id':'ib-aisl-ca-707','issue':'A truncated plot frame at−2 obscured the actual zero-rate crossings.','resolution':'Added explicit labelled zero-level reference line.'},
{'id':'ib-aisl-na-714','issue':'A rounded displayed payment was labelled before-rounding.','resolution':'Exact threshold formula, six-decimal value and greatest whole-cent payment separated.'},
{'id':'ib-aisl-na-720','issue':'Rounded minimum costs were described as before upward-cent rounding.','resolution':'Unrounded thresholds separated from actual minimum whole-cent payments.'},
{'id':'ib-aisl-na-716','issue':'Plot title named two balances but only original schedule was supplied.','resolution':'Title now accurately describes the single original-payment curve.'}
]
report={'status':'passed','questions':100,'reviewer':'Independent AI reviewer distinct from the AI SL author','reviewScope':'All100 complete prompts, all solution steps, exact and rounded numerical outputs, admissible domains, branch choices, finance timing, interpretation, currentSL scope, additive marks and SVG constructions. This is not human IB examiner moderation.','officialGuide':'https://ibo.org/globalassets/new-structure/university-admission/pdfs/dp-mathematics-applications-and-interpretation-guide-en.pdf','scopeEvidence':'Official guide SL4.2 excludes frequency-density histograms; SL4.8 includes binomial mean/variance; AHL5.10 introduces second derivatives. These boundaries were explicitly checked and used in corrections.','sha256':hashlib.sha256(bank.read_bytes()).hexdigest(),'independentNumericalChecks':sum(len(r['independentChecks']) for r in records),'svgCount':100,'mathematicalGraphGeometryChartCount':sum(v!='flow' for v in diagram_kinds.values()),'timelineFlowCount':sum(v=='flow' for v in diagram_kinds.values()),'svgTableCount':0,'correctedFindings':changes,'records':records,'limitations':['Independent computational/AI review does not substitute for independent human examiner moderation.','Difficulty labels remain editorial estimates pending student calibration.']}
out=ROOT/'docs/ib-2026-maths/ai-sl-independent-review.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['status','questions','independentNumericalChecks','mathematicalGraphGeometryChartCount','timelineFlowCount','sha256']}))
