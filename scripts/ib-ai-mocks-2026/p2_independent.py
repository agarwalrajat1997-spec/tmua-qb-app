"""Independent review of all 24 AI HL P2 questions; no author imports.

Numerical calculations are rebuilt from the complete question stems and the
nine independently inspected diagrams. Contextual and analytic judgments are
recorded separately from executable numeric assertions.
"""
from __future__ import annotations
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
TASK=ROOT.parent.parent
sys.path.insert(0,str(TASK/'work/ai-mocks-2026/python-deps'))
import numpy as np
from scipy import integrate,optimize,stats

PAPERS=ROOT/'content/ib/ai-mocks-2026/papers'
data={s:json.loads((PAPERS/f'ai-hl-set-{s.lower()}-paper-2.json').read_text(encoding='utf-8')) for s in 'ABCD'}
reviews={};count=0


def start(set_name,n,reasoning):
    key=f'{set_name}{n}';q=data[set_name]['questions'][n-1]
    reviews[key]={'id':key,'status':'passed','completeStemAndSchemeRead':True,'marks':q['marks'],'syllabusRefs':q['syllabusRefs'],'reasoning':reasoning,'diagramInspected':bool(q.get('diagramSvg')),'parts':{p['label']:{'marks':p['marks'],'evidence':[]} for p in q['parts']}}
    return key


def plain(v):
    if isinstance(v,np.ndarray):return v.tolist()
    if isinstance(v,np.generic):return v.item()
    if isinstance(v,complex):return {'real':v.real,'imag':v.imag}
    if isinstance(v,(tuple,list)):return [plain(x) for x in v]
    return v


def ck(k,p,name,actual,expected=True,tol=0):
    global count
    if tol:passed=bool(np.allclose(actual,expected,atol=tol,rtol=0))
    else:passed=plain(actual)==plain(expected)
    actual=plain(actual);expected=plain(expected)
    assert passed,(k,p,name,actual,expected)
    count+=1;reviews[k]['parts'][p]['evidence'].append({'type':'executable','check':name,'actual':actual,'expected':expected,'absoluteTolerance':tol,'passed':True})


def near(k,p,name,actual,expected,tol=5e-5):ck(k,p,name,actual,expected,tol)
def why(k,p,rationale):reviews[k]['parts'][p]['evidence'].append({'type':'analytic/contextual review','rationale':rationale,'reviewed':True})
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def length(a):return math.sqrt(dot(a,a))
def area(poly):return abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(poly,poly[1:]+poly[:1])))/2


def shortest(names,edges):
    d={a:{b:0 if a==b else math.inf for b in names} for a in names}
    for a,b,w in edges:d[a][b]=d[b][a]=w
    for c in names:
        for a in names:
            for b in names:d[a][b]=min(d[a][b],d[a][c]+d[c][b])
    return d


def mst(names,edges):
    parent={a:a for a in names}
    def find(x):
        while parent[x]!=x:x=parent[x]
        return x
    used=[]
    for a,b,w in sorted(edges,key=lambda e:e[2]):
        if find(a)!=find(b):parent[find(a)]=find(b);used.append((a,b,w))
    assert len(used)==len(names)-1
    return used,sum(e[2] for e in used)


def steady(T):
    a=np.array(T,dtype=float)-np.eye(len(T));a[-1,:]=1
    b=np.zeros(len(T));b[-1]=1
    return np.linalg.solve(a,b)


k=start('A',1,'Solar-minus-load is concave down on the daylight interval, positive at noon and negative at each endpoint, so its two crossings delimit the sole surplus. Integrals have units kWh. An initially empty battery cannot supply the earlier morning deficit even when its later recoverable energy is ample.')
P=lambda t:80*math.sin(math.pi*(t-6)/12);D=lambda t:35+2*(t-12);f=lambda t:P(t)-D(t)
r1=optimize.brentq(f,6,12);r2=optimize.brentq(f,12,18)
ck(k,'a','Solar peak and endpoints',[P(12),P(6),round(P(18),10)],[80.,0.,0.])
near(k,'b','First crossing',r1,7.237942);near(k,'b','Second crossing',r2,15.84945)
ck(k,'b','Single surplus sign pattern',f(6)<0<f(12) and f(18)<0)
surplus=integrate.quad(f,r1,r2)[0];short1=integrate.quad(lambda t:-f(t),6,r1)[0];short2=integrate.quad(lambda t:-f(t),r2,18)[0]
near(k,'c','Surplus energy',surplus,254.5372)
near(k,'d','Both positive deficits',short1+short2,63.38224)
near(k,'d','Net-energy identity',surplus-short1-short2,integrate.quad(f,6,18)[0],1e-8)
near(k,'e','Deliverable later surplus',.8*surplus,203.6298)
ck(k,'e','Timing defeats energy-only claim',short1>0 and .8*surplus>short1+short2)
why(k,'e','The battery is empty before the first crossing. Energy generated later cannot retroactively remove that earlier grid requirement. No assumption about unmodelled night-time demand is needed to refute the claim.')

k=start('A',2,'The network diagram was independently transcribed as eleven undirected edges, total61. Connectivity and degree parity determine the postman corrections; removing EF changes which vertices are odd.')
edges=[('A','B',4),('A','C',7),('A','D',9),('B','C',3),('B','E',6),('B','F',10),('C','D',4),('C','E',5),('D','E',2),('D','F',8),('E','F',3)]
_,treeweight=mst('ABCDEF',edges);d=shortest('ABCDEF',edges)
ck(k,'a','Independent Kruskal tree weight',treeweight,16)
ck(k,'b','Shortest A-F',d['A']['F'],13)
ck(k,'b','Exhibited A-B-E-F length',4+6+3,13)
degrees={a:sum(a in e[:2] for e in edges) for a in 'ABCDEF'}
ck(k,'c','Odd vertices',[a for a in degrees if degrees[a]%2],['A','F'])
ck(k,'c','All-edge total',sum(e[2] for e in edges),61)
ck(k,'c','Closed postman lower bound and augmentation',61+d['A']['F'],74)
ck(k,'d','Open endpoint parity fits original graph',degrees['A']%2==degrees['F']%2==1 and all(degrees[a]%2==0 for a in 'BCDE'))
ck(k,'d','Euler trail length',sum(e[2] for e in edges),61)
reduced=[e for e in edges if e[:2]!=('E','F')];d2=shortest('ABCDEF',reduced)
ck(k,'e','New odd vertices',[a for a in 'ABCDEF' if sum(a in e[:2] for e in reduced)%2],['A','E'])
ck(k,'e','New closed postman optimum',sum(e[2] for e in reduced)+d2['A']['E'],68)
why(k,'e','Removing a required edge changes both the base inspection obligation and the minimum parity-correction path; subtracting3 from74 would give71, not68.')

k=start('A',3,'The before-minus-after sign makes improvement a positive mean. Population sigma is unknown, so the paired differences use one-sample t, df9. Correcting overstated after-times increases every difference by1.5; it does not alter dispersion. Observational before/after improvement is not by itself causal evidence.')
dif=np.array([4,-1,7,3,8,0,6,5,9,2],float);mean=float(dif.mean());sd=float(dif.std(ddof=1));se=sd/math.sqrt(10);tt=mean/se;pv=stats.t.sf(tt,9)
near(k,'a','Difference mean',mean,4.3);near(k,'a','Unbiased SD',sd,3.335,5e-4);near(k,'a','Estimated standard error',se,1.054619)
near(k,'b','Paired t statistic',tt,4.0773);near(k,'b','One-tailed p',pv,.001384594,1e-9);ck(k,'b','Reject at5%',pv<.05)
critical=stats.t.ppf(.975,9);ci=(mean-critical*se,mean+critical*se)
near(k,'c','t critical value',critical,2.262157);near(k,'c','Mean CI',ci,[1.914285,6.685715])
why(k,'c','A repeated-sampling confidence interval concerns the population mean difference; it does not contain95% of individual changes and is not a probability statement that the fixed mean lies in this realized interval.')
corr=dif+1.5
near(k,'d','Corrected mean',corr.mean(),5.8);near(k,'d','Unchanged sample SD',corr.std(ddof=1),sd,1e-12)
near(k,'d','Corrected t',corr.mean()/se,5.499614);near(k,'d','Corrected p',stats.t.sf(corr.mean()/se,9),.000190188,1e-9)
why(k,'e','No randomized untreated comparison is described. Practice or changed conditions could explain some change; two linked reasons in the scheme support the two reasoning marks.')

k=start('A',4,'This is a nonnegative stage matrix, not a transition matrix. Reproduction may exceed1. A positive dominant eigenvector determines composition. At q=0 both eigenvalues have equal modulus, but both are below1, so eventual extinction still follows; no regular-Markov assumption is needed.')
M=np.array([[0,1.8],[.4,.4]]);state=np.array([240.,120.]);s1=M@state;s2=M@s1
near(k,'a','First two states',[s1,s2],[[216,144],[259.2,144]],1e-9)
why(k,'a','The lower-right .4 is annual adult survival/retention, not juvenile recruitment.')
eigs=np.linalg.eigvals(M);lam=max(eigs);other=min(eigs)
near(k,'b','Eigenvalues',[lam,other],[1.07178,-.6717798])
for value in eigs:near(k,'b','Eigenvector substitution',M@np.array([1.8/value,1]),value*np.array([1.8/value,1]),1e-10)
vec=np.array([1.8/lam,1]);vec/=vec.sum();near(k,'c','Normalized eventual composition',vec,[.626789,.373211])
ck(k,'c','Strict modulus dominance',lam>abs(other))
totals=[]
for n in range(17):totals.append(float(state.sum()));state=M@state
ck(k,'d','First threshold over all earlier years',next(n for n,t in enumerate(totals) if t>1000),16)
near(k,'d','Adjacent totals',totals[-2:],[976.3631,1046.512],5e-4)
near(k,'e','Replacement parameter',1-.72,.28,1e-12)
for q in [0,.1,.279]:ck(k,'e','All eigenvalue moduli below1 below threshold',max(abs(np.linalg.eigvals([[0,1.8],[.4,q]])))<1)
ck(k,'e','Growth side above threshold',max(np.linalg.eigvals([[0,1.8],[.4,.3]]))>1)
why(k,'f','The secondary eigencomponent alternates because its eigenvalue is negative; its size relative to the dominant component decays since its modulus is smaller. Constant vital rates omit environmental/resource changes.')

k=start('A',5,'The floor and wall areas have units m2; volume fixes h=60/w2. The unconstrained strictly convex cost minimum is infeasible. The actual optimum is the left boundary sqrt20. The price threshold follows from the increasing cube-root stationary width.')
C=lambda w:100*w*w+10800/w;w0=54**(1/3);wmin=math.sqrt(20)
for w in [3,5,6]:near(k,'a','Volume and material model',50*(2*w*w)+30*(6*w*(60/w**2)),C(w),1e-9)
near(k,'b','Unconstrained stationary width',w0,3.779763);ck(k,'b','Global strict convexity',all(200+21600/w**3>0 for w in [.01,1,4,100]))
near(k,'c','Infeasible unconstrained height',60/w0**2,4.199737)
ck(k,'c','Feasible width interval and excluded stationary point',w0<wmin<=6)
near(k,'d','Optimal dimensions',[wmin,2*wmin,60/wmin**2],[4.472136,8.944272,3])
near(k,'d','Unrounded constrained minimum',C(wmin),4414.953,5e-4);ck(k,'d','Nearest-dollar minimum',round(C(wmin)),4415)
ck(k,'d','Cost increasing over feasible interval',all(200*w-10800/w**2>0 for w in np.linspace(wmin,6,101)))
near(k,'e','First feasible stationary wall price',200*wmin**3/360,49.6904)

k=start('A',6,'Compare positions at the same time, not geometric path intersections at independent times. Squared separation is a strictly convex quadratic; its stationary point lies inside the modelled interval. Alert endpoints are excluded because the rule is strictly less than1km.')
r=np.array([-9,2,-2.]);v=np.array([4,-1,.6]);vp=np.array([3,1,.4]);vq=np.array([-1,2,-.2])
near(k,'a','Initial separation',np.linalg.norm(r),9.433981)
ck(k,'b','Relative initial position',r,[-9,2,-2]);ck(k,'b','Relative velocity',v,[4,-1,.6])
coef=(dot(v,v),2*dot(r,v),dot(r,r));near(k,'c','Distance-squared coefficients',coef,[17.36,-78.4,89],1e-10)
t=-dot(r,v)/dot(v,v);sep=np.linalg.norm(r+t*v)
near(k,'c','Minimum time and separation',[t,sep],[2.258065,.6956083])
ck(k,'c','Global minimum lies inside time domain',0<t<4 and sep<np.linalg.norm(r) and sep<np.linalg.norm(r+4*v))
roots=np.sort(np.roots([coef[0],coef[1],coef[2]-1]));near(k,'d','Alert boundary times',roots,[2.085638,2.430491]);near(k,'d','Alert duration',roots[1]-roots[0],.3448532)
why(k,'d','The quadratic opens upward; the interval is open at both equality times and lies entirely in[0,4].')
near(k,'e','Velocity dot product',dot(vp,vq),-1.08,1e-12);near(k,'e','Squared speeds',[dot(vp,vp),dot(vq,vq)],[10.16,5.04],1e-12)
near(k,'e','Angle in degrees',math.degrees(math.acos(dot(vp,vq)/(length(vp)*length(vq)))),98.68054)
ck(k,'f','No simultaneous 3D collision',sep>0)
why(k,'f','A projected crossing suppresses altitude and may occur at different traversal times; the strictly positive global3D separation rules out collision.')

k=start('B',1,'Every annual net receipt is positive, so discounted receipts decrease strictly with the discount rate. Cash flows are explicitly nominal and year-end. Correct real growth divides gross factors; it is not exactly3%-2%.')
V=lambda r:-18000+sum((3200*1.03**(j-1)-900)/(1+r)**j for j in range(1,9))+2000/(1+r)**8
ck(k,'a','All annual net receipts positive',all(3200*1.03**(j-1)-900>0 for j in range(1,9)))
near(k,'a','Undiscounted cash-flow expression',V(0),sum(3200*1.03**(j-1)-900 for j in range(1,9))+2000-18000,1e-8)
near(k,'b','NPV at6%',V(.06),-444.6266);ck(k,'b','Nearest-dollar NPV',round(V(.06)),-445)
why(k,'b','Negative NPV fails the specified required effective return, conditional on the cash-flow forecasts.')
irr=optimize.brentq(V,0,1);near(k,'c','Internal rate of return',irr,.05434374,1e-8)
ck(k,'c','Strict decreasing witness',all(V(a)>V(b) for a,b in [(0,.02),(.04,.06),(.1,.2)]))
why(k,'c','A sum of positive discounted receipts is strictly decreasing for r>0. Together with a numerical sign change this gives a unique positive root.')
near(k,'d','Purchasing-power growth percent',100*(1.03/1.02-1),.9803922)
alternative=-18000+sum(2600/1.06**j for j in range(1,10));near(k,'e','Alternative NPV',alternative,-315.6001)
ck(k,'e','Both fail6%, alternative higher NPV',V(.06)<alternative<0)
why(k,'f','Forecast energy prices/savings and future maintenance/service life/resale are distinct uncertain inputs. Discounting changes timing values, not their uncertainty.')

k=start('B',2,'Euclidean bisectors bound a convex clipped Voronoi cell. Part(d) asks farthest from A within A cell, not the global toxic-waste maximin problem; the supplied polygon-maximum fact makes boundary vertices legitimate. Distance-only cells do not minimize time with unequal speeds.')
A=np.array([2.,2]);B=np.array([10.,2]);Csite=np.array([6.,8]);Voro=np.array([6,11/3]);polygon=[[0,0],[6,0],[6,11/3],[0,23/3]]
ck(k,'a','AB bisector midpoint x',float((A[0]+B[0])/2),6.)
near(k,'b','Three equal distances',[np.linalg.norm(Voro-site) for site in [A,B,Csite]],[13/3]*3,1e-10)
near(k,'b','AC bisector equation at common vertex',2*Voro[0]+3*Voro[1],23,1e-10)
near(k,'c','Clipped cell area',area(polygon),34,1e-10)
for x,y in polygon:ck(k,'c','Each listed vertex in cell and rectangle',0<=x<=12 and 0<=y<=10 and x<=6 and 2*x+3*y<=23+1e-10)
sq=[float(np.dot(np.array(p)-A,np.array(p)-A)) for p in polygon]
near(k,'d','All vertex squared distances',sq,[8,20,169/9,325/9],1e-10)
near(k,'d','Maximum cell distance',math.sqrt(max(sq)),6.009252)
point=np.array([5,4]);times=[np.linalg.norm(point-site)/speed*60 for site,speed in [(A,40),(B,80),(Csite,30)]]
near(k,'e','Response times in minutes',times,[5.408327,4.038874,8.246211]);ck(k,'e','Fastest centre differs from nearest',int(np.argmin(times)),1)

k=start('B',3,'Independent constant-rate Poisson streams combine by addition of means. The conditional binomial law is introduced in the question. Every count-tail direction and included endpoint is checked, and the requested discrete size is strictly below5%.')
near(k,'a','One-hour tail at least10',stats.poisson.sf(9,6),.08392402,1e-8)
near(k,'b','Conditional appointment fraction',2.4/6,.4,1e-12);near(k,'b','Conditional binomial tail',stats.binom.sf(2,5,.4),.31744,1e-12)
m=next(j for j in range(100) if stats.poisson.sf(j,12)<.01)
ck(k,'c','Minimum capacity',m,21);near(k,'c','Adjacent capacity tails',[stats.poisson.sf(21,12),stats.poisson.sf(20,12)],[.006065147,.01159774],1e-8)
near(k,'d','Eight-hour one-sided p',stats.poisson.sf(64,48),.01117098,1e-8);ck(k,'d','Reject5%',stats.poisson.sf(64,48)<.05)
why(k,'d','The test parameter is hourly lambda; the null eight-hour total mean is48, not6. The alternative is an increase.')
cut=next(j for j in range(200) if stats.poisson.sf(j-1,48)<.05)
ck(k,'e','Smallest rejection threshold',cut,61)
near(k,'e','Actual Type I size',stats.poisson.sf(60,48),.03950011,1e-8)
ck(k,'e','Next larger region violates size',stats.poisson.sf(59,48)>.05)
near(k,'e','Type II at hourly rate7',stats.poisson.cdf(60,56),.7309104,1e-7)
why(k,'e','A missed increase is X<=60 when the true eight-hour mean is56; it is not a posterior probability of H0.')

k=start('B',4,'The column convention is explicit and every matrix entry positive, so this is regular. Occupancy at each minute contributes to the visits sum; repeated visits remain counted. General3x3 steady-state solving is allowed; this does not ask for3x3 eigenvalue calculation.')
T=np.array([[.6,.2,.1],[.3,.5,.3],[.1,.3,.6]]);s=np.array([1000.,0,0]);one=T@s;two=T@one
near(k,'a','B to C transition',T[2,1],.3,1e-12);near(k,'a','One-minute expected counts',one,[600,300,100],1e-10)
near(k,'b','Two-minute counts',two,[430,360,210],1e-10)
pi=steady(T);near(k,'c','Normalized steady state',pi,[.275,.375,.35],1e-10);near(k,'c','Steady equation',T@pi,pi,1e-10)
ck(k,'d','Strict positivity gives regularity',bool(np.all(T>0)))
s=np.array([1.,0,0]);visits=0
for _ in range(5):s=T@s;visits+=s[2]
near(k,'e','Five-minute repeated visits per visitor',visits,1.23123,1e-10);near(k,'e','Aggregate expected visits',1000*visits,1231.23,1e-8)
new=T.copy();new[:,2]=[.25,.30,.45];pnew=steady(new)
near(k,'f','Updated steady state',pnew,[.3557692,.375,.2692308]);ck(k,'f','C occupancy decreases',pnew[2]<pi[2])

k=start('B',5,'The prescribed fit minimizes log-distance residuals. Reaction distance requires converting km/h to m/s. Both stopping-distance terms are increasing, giving a unique largest allowable speed within the observed range; an altered reaction time need not change the independently fitted braking law.')
speeds=np.array([20,30,40,50,60,70,80.]);dist=np.array([3.2,6.9,12.6,20.1,29.5,39.8,53.]);reg=stats.linregress(np.log(speeds),np.log(dist));b=reg.slope;kfit=math.exp(reg.intercept)
near(k,'a','Log fit intercept and slope',[reg.intercept,b],[-4.964212,2.036363]);near(k,'a','Power coefficient',kfit,.00698345,1e-8);near(k,'a','Log-data Pearson correlation',reg.rvalue,.9998259,1e-7)
model=lambda v:kfit*v**b
near(k,'b','65km/h braking prediction',model(65),34.34158);near(k,'b','80km/h original-scale residual',53-model(80),.5853497)
v1=optimize.brentq(lambda v:1.1*v/3.6+model(v)-50,20,80);v2=optimize.brentq(lambda v:.85*v/3.6+model(v)-50,20,80)
near(k,'c','First stopping-boundary speed',v1,61.89802);ck(k,'c','Monotone stopping function',kfit>0 and b>0 and 20<v1<80)
near(k,'d','Reduced-reaction boundary speed',v2,65.23683);ck(k,'d','Reaction-only reduction permits higher speed',v2>v1)
why(k,'d','The measured speed/braking pairs remain unchanged, so the fitted braking k and b remain fixed. Only the reaction-distance coefficient changes.')
why(k,'e','Icy-road friction changes the context and120km/h is extrapolation beyond20..80. The transformed least-squares target is squared residuals in ln(d), not in metres.')

k=start('B',6,'The given logistic expression starts below its carrying capacity and remains below it. The differential model is checked by substitution, not by demanding an out-of-scope logistic integration. Growth as a function of population is a concave quadratic with its reachable maximum at600.')
N=lambda t:1200/(1+11*math.exp(-.42*t));Np=lambda t:1200*11*.42*math.exp(-.42*t)/(1+11*math.exp(-.42*t))**2
ck(k,'a','Initial population',N(0),100.);near(k,'a','Long-time limit',N(100),1200,1e-10)
why(k,'a','1200 is the fixed-resource carrying capacity, not the starting count or an arbitrary growth rate.')
for t in [0,3,7,20]:near(k,'b','Derivative satisfies supplied logistic DE',Np(t),.42*N(t)*(1-N(t)/1200),1e-9)
peak=math.log(11)/.42;near(k,'c','Time of maximum growth',peak,5.709274);near(k,'c','Maximum instantaneous growth',Np(peak),126,1e-9)
ck(k,'c','Peak population and global quadratic sign',abs(N(peak)-600)<1e-9 and Np(peak)>Np(0) and Np(peak)>Np(20))
average=integrate.quad(N,5,10)[0]/5;near(k,'d','Mean population',average,799.7329);near(k,'d','Midpoint population',N(7.5),815.5646)
why(k,'d','The integral average need not equal a nonlinear function at the midpoint; this model supplies an explicit numerical counterexample.')
ck(k,'e','No finite-time overshoot',all(0<N(t)<1200 for t in [0,1,10,50]))
why(k,'e','The positive exponential makes the denominator greater than1 at every finite nonnegative time. A nutrient, space or environmental change can alter carrying capacity.')

k=start('C',1,'The piecewise mass-balance solution is continuous at the clean-water switch, but its derivative changes. The rising concave-down branch makes forward Euler overestimate here. Duration above threshold uses one root on each branch. Outlet concentration times volume-flow gives grams per hour.')
C1=lambda t:5-4*math.exp(-.1*t);C10=C1(10);C2=lambda t:C10*math.exp(-.1*(t-10))
near(k,'a','Exact initial and ten-hour concentrations',[C1(0),C10],[1,3.528482])
for t in [0,3,10]:near(k,'a','Original DE satisfied',.4*math.exp(-.1*t),.5-.1*C1(t),1e-12)
c=1.;euler=[c]
for _ in range(4):c+=2.5*(.5-.1*c);euler.append(c)
near(k,'b','All simultaneous Euler values',euler,[1,2,2.75,3.3125,3.734375],1e-12)
ck(k,'b','Euler overestimate and downward concavity',c>C10 and all(-.04*math.exp(-.1*t)<0 for t in [0,5,10]))
near(k,'c','Switch continuity',C2(10),C10,1e-12)
for t in [10,12,20]:near(k,'c','Clean-water DE',-.1*C2(t),-C10*.1*math.exp(-.1*(t-10)),1e-12)
up=-10*math.log(3/4);down=10+10*math.log(C10/2)
near(k,'d','Upward and downward threshold crossings',[up,down],[2.876821,15.67721]);near(k,'d','Total above-threshold duration',down-up,12.80039)
ck(k,'d','Crossings in correct regimes',0<up<10<down and C1(0)<2<C10)
removed=100*(integrate.quad(C1,0,10)[0]+integrate.quad(C2,10,20)[0])
near(k,'e','Outlet integral mass in grams',removed,4701.944,5e-4)
near(k,'e','Independent whole-system mass balance',1000+100*5*10-1000*C2(20),removed,1e-8)

k=start('C',2,'The supplied complete graph is metric and visits are explicitly scheduled, so shortest connections passing another site are not ambiguous. Nearest-neighbour is only an upper bound; deleted-vertex MST gives a lower bound. Closing CD requires metric completion. The final wording was corrected to best-known tour length, avoiding an unjustified assertion about the original optimum.')
names='ABCDE';table=np.array([[0,7,9,8,12],[7,0,6,10,9],[9,6,0,5,7],[8,10,5,0,6],[12,9,7,6,0]],float)
all_edges=[(names[i],names[j],float(table[i,j])) for i in range(5) for j in range(i+1,5)]
dist=shortest(names,all_edges)
ck(k,'a','Initial table already shortest-distance closure',all(dist[a][b]==table[names.index(a),names.index(b)] for a in names for b in names))
def nn(d):
    route=['A'];remaining=set('BCDE')
    while remaining:
        x=min(remaining,key=lambda v:(d[route[-1]][v],v));route.append(x);remaining.remove(x)
    route.append('A');return ''.join(route),sum(d[a][b] for a,b in zip(route,route[1:]))
ck(k,'a','Nearest-neighbour tour and weight',nn(dist),['ABCDEA',36.])
subset=[e for e in all_edges if 'A' not in e[:2]];_,mw=mst('BCDE',subset)
ck(k,'b','Deleted-A MST',mw,17.);ck(k,'b','Deleted-A lower bound',mw+7+8,32.)
why(k,'b','DeletingA from a Hamiltonian cycle leaves a spanning path; its weight is at least the MST. The removed connections cost at least the two cheapestA edges. Both inequalities point in the lower-bound direction.')
tour='ABCEDA';weight=sum(dist[a][b] for a,b in zip(tour,tour[1:]))
ck(k,'c','Improved feasible tour',weight,34.);ck(k,'c','Valid bounding interval',32<=weight<36)
closed_edges=[e for e in all_edges if set(e[:2])!=set('CD')];newdist=shortest(names,closed_edges)
ck(k,'d','New indirect C-D shortest distance',newdist['C']['D'],13.)
ck(k,'d','Only C-D distance changes',all(newdist[a][b]==dist[a][b] for a in names for b in names if set((a,b))!=set('CD')))
ck(k,'d','New nearest-neighbour upper bound',nn(newdist),['ABCEDA',34.])
new_subset=[(a,b,newdist[a][b]) for a,b,_ in subset];_,newmw=mst('BCDE',new_subset)
ck(k,'d','New deleted-A lower bound',newmw+7+8,34.)
ck(k,'e','Retained best-known tour avoids removed connection',all(set((a,b))!=set('CD') for a,b in zip(tour,tour[1:])))
why(k,'e','The revised question asks about the best known tour from(c). That34km route remains feasible. Parts(a–c) only established bounds32..34, so their reasoning alone must not claim that the old optimum was proved34.')
optimum=min(sum(dist[a][b] for a,b in zip(('A',)+p+('A',),p+('A',))) for p in itertools.permutations('BCDE'))
ck(k,'e','Additional reviewer-only enumeration of original optimum',optimum,34.)

k=start('C',3,'The supplied equal unknown population variance calls for the pooled two-sample t test, df25. The confidence interval in(c) deliberately uses only sampleA, so its df is11. A common additive timer correction does not affect the mean difference, but shifts the one-population interval. Repeated measurements are not independent sampling units.')
na,nb,ma,mb,sa,sb=12,15,52.4,55.,4.1,3.6
sp=math.sqrt(((na-1)*sa**2+(nb-1)*sb**2)/(na+nb-2));se=sp*math.sqrt(1/na+1/nb);t=(ma-mb)/se
near(k,'a','Pooled SD',sp,3.828054);near(k,'a','Difference standard error',se,1.482599)
near(k,'b','Lower-tail t statistic',t,-1.753677);near(k,'b','One-sided p',stats.t.cdf(t,25),.04586992,1e-8);ck(k,'b','Reject5% with25df',stats.t.cdf(t,25)<.05)
crit=stats.t.ppf(.975,11);ci=[ma-crit*sa/math.sqrt(na),ma+crit*sa/math.sqrt(na)]
near(k,'c','Single-populationA critical value',crit,2.200985);near(k,'c','Single-populationA mean interval',ci,[49.79498,55.00502])
near(k,'d','Test statistic after common bias correction',((ma+2)-(mb+2))/se,t,1e-12);near(k,'d','ShiftedA interval',[x+2 for x in ci],[51.79498,57.00502])
why(k,'d','Adding the same2minutes preserves each sample SD and the difference of means, hence the t statistic and p value. It shifts both endpoints ofA CI upward by2.')
why(k,'e','Within-operator repeats can be correlated, so multiplying the nominal sample size can artificially lower the standard error. More independent operators or per-operator summaries respect the sampling unit.')

k=start('C',4,'The prescribed regression is on ln(concentration), whereas residual comparisons are explicitly on the original scale. The constant background changes the physical long-term interpretation. Integrated concentration has concentration×time units; the time mean recovers concentration units.')
times=np.array([0,2,4,6,8,10.]);observed=np.array([120,86,62,46,33,24.]);reg=stats.linregress(times,np.log(observed));A=math.exp(reg.intercept);b=reg.slope
model1=lambda t:A*math.exp(b*t);model2=lambda t:8+112*math.exp(-.18*t)
near(k,'a','Log intercept and slope',[reg.intercept,b],[4.780068,-.1602743]);near(k,'a','Exponential coefficient',A,119.1124)
cross=math.log(30/A)/b;near(k,'b','30-unit crossing time',cross,8.603189);ck(k,'b','Below threshold after crossing',b<0 and model1(cross+.1)<30<model1(cross-.1))
ss1=sum((y-model1(t))**2 for t,y in zip(times,observed));ss2=sum((y-model2(t))**2 for t,y in zip(times,observed))
near(k,'c','Original-scale sums of squared residuals',[ss1,ss2],[1.752691,8.963826]);ck(k,'c','Model1 wins stated residual criterion',ss1<ss2)
why(k,'c','A smaller in-sample residual sum does not establish correct future background or ventilation assumptions. Log regression and original-scale least squares also have different objectives.')
half=math.log(2)/.18;near(k,'d','Excess-concentration half-life',half,3.850818)
near(k,'d','Excess halves, not total',model2(half)-8,(model2(0)-8)/2,1e-10);ck(k,'d','Total does not halve over that interval',model2(half)!=model2(0)/2)
integ=integrate.quad(model2,0,12)[0];near(k,'e','Integrated concentration',integ,646.4644);near(k,'e','Mean concentration',integ/12,53.87203)
why(k,'e','The integral is in concentration-unit hours, and division by12hours gives concentration units. The model is defined throughout the integration interval.')

k=start('C',5,'The affine command is within matrix transformations and complex multiplication; no complex roots are asked. Translating to the fixed point converts the recurrence to a geometric complex sequence. Its modulus determines the first integer proximity index, and its argument explains rotating contraction.')
mult=.6+.2j;trans=2-1j;z0=1+3j;z1=mult*z0+trans;z2=mult*z1+trans
near(k,'a','First complex position',z1,2+1j,1e-12);near(k,'a','Second complex position',z2,3+0j,1e-12)
M=np.array([[.6,-.2],[.2,.6]]);near(k,'b','Matrix matches complex multiplication',M@np.array([z0.real,z0.imag]),[(mult*z0).real,(mult*z0).imag],1e-12)
near(k,'b','Length scale',abs(mult),.6324555);near(k,'b','Rotation in degrees',math.degrees(math.atan2(.2,.6)),18.43495);near(k,'b','Area scale determinant',np.linalg.det(M),.4,1e-12)
fixed=trans/(1-mult);near(k,'c','Fixed position',fixed,5+0j,1e-12)
z=z0
for n in range(15):
    near(k,'d','Closed form against direct recurrence',z-fixed,mult**n*(z0-fixed),1e-10);z=mult*z+trans
n=next(n for n in range(100) if 5*abs(mult)**n<.05);ck(k,'e','First proximity index',n,11)
near(k,'e','Adjacent distances',[5*abs(mult)**10,5*abs(mult)**11],[.0512,.03238172])
why(k,'f','The multiplier has a nonzero non-pi argument and modulus below1, so displacement angle changes each step while distance contracts. A translation alone would not explain this.')

k=start('C',6,'All bearings use atan2(east,north), not the mathematical polar convention. The current must be subtracted from required shore velocity before enforcing water-relative speed. A positive quadratic root gives the unique travel time; closest point on the cable is checked within its finite segment.')
A=np.array([0,0,0.]);B=np.array([6,2,0.]);C=np.array([1,5,0.]);D=np.array([3,2,4.])
cross=np.cross(B-A,C-A);near(k,'a','Buoy cross product',cross,[0,0,28],1e-12);near(k,'a','Triangle area',np.linalg.norm(cross)/2,14,1e-12)
angle=math.degrees(math.acos(dot(B,D)/(length(B)*length(D))));near(k,'b','Sight-line angle',angle,49.76364)
shore=np.array([2,.5])+np.array([.2,.3]);near(k,'c','Shore-relative velocity',shore,[2.2,.8],1e-12);near(k,'c','Shore bearing clockwise from north',math.degrees(math.atan2(shore[0],shore[1])),70.01689)
roots=np.roots([6.12,3.4,-26]);travel=float(max(roots));water=np.array([1/travel-.2,5/travel-.3])
near(k,'d','Positive travel time',travel,1.802012);ck(k,'d','Exactly one positive time root',sum(roots>0),1)
near(k,'d','Relative-water speed condition',np.linalg.norm(water),2.5,1e-10)
near(k,'d','Water-relative velocity',water,[.3549352,2.474676]);near(k,'d','Required water heading',math.degrees(math.atan2(water[0],water[1])),8.162094)
near(k,'d','Current plus heading reaches target',(water+np.array([.2,.3]))*travel,[1,5],1e-10)
s=dot(C,B)/dot(B,B);foot=s*B
near(k,'e','Segment projection parameter',s,.4,1e-12);ck(k,'e','Projection inside segment',0<s<1)
near(k,'e','Closest cable point',foot,[2.4,.8,0],1e-12);near(k,'e','Minimum cable distance',np.linalg.norm(foot-C),4.427189)

k=start('D',1,'The demand and profit functions are distinct. Profit is contribution minus fixed cost. Its derivative changes sign once at33 on[0,100]. With demand capped by a price choice, feasible prices begin above33, so the constrained optimum moves to the capacity boundary rather than retaining the unconstrained price.')
q=lambda p:500*math.exp(-.04*p);profit=lambda p:(p-8)*q(p)-1200;dp=lambda p:q(p)*(1-.04*(p-8))
for p in [0,20,33,60]:near(k,'a','Profit model from revenue/cost',profit(p),p*q(p)-8*q(p)-1200,1e-9)
near(k,'a','Derivative against central difference',dp(20),(profit(20.00001)-profit(19.99999))/.00002,1e-5)
near(k,'b','Maximum price',33.,33.);near(k,'b','Demand at optimum',q(33),133.5677);near(k,'b','Maximum profit',profit(33),2139.191,5e-4)
ck(k,'b','Global derivative signs',dp(0)>0 and abs(dp(33))<1e-10 and dp(100)<0)
r1=optimize.brentq(profit,0,33);r2=optimize.brentq(profit,33,100)
near(k,'c','Profit roots',[r1,r2],[11.85636,87.51051]);ck(k,'c','Nonnegative profit interval',profit(33)>0 and profit(0)<0 and profit(100)<0)
bound=math.log(5)/.04;near(k,'d','Capacity price boundary',bound,40.23595);near(k,'d','Demand at constrained optimum',q(bound),100,1e-10);near(k,'d','Constrained profit',profit(bound),2023.595,5e-4)
ck(k,'d','Feasible region wholly decreasing',33<bound<100 and dp(bound)<0)
why(k,'e','Fixed cost subtracts a constant: derivative and unconstrained maximizing price are unchanged. Increasing the constant shrinks the superlevel set profit>=0 and can eliminate it.')

k=start('D',2,'The process starts sunny rather than stationary. Daily states are dependent, so exact path probabilities replace a binomial count model. Linearity of expectation still permits summing daily energy, and the resulting transient probabilities form a geometric sequence.')
T=np.array([[.75,.25],[.25,.75]]);p=1.
near(k,'a','Column-stochastic transition sums',T.sum(axis=0),[1,1],1e-12)
for n in range(11):
    near(k,'b','Geometric marginal at each day',p,.5+.5*.5**n,1e-12)
    if n==0:near(k,'a','One-step probability recurrence',.75*p+.25*(1-p),.5*p+.25,1e-12)
    p=.5*p+.25
near(k,'c','Steady distribution',steady(T),[.5,.5],1e-12);ck(k,'c','Positive matrix regularity',bool(np.all(T>0)))
prob=0
for path in itertools.product([0,1],repeat=3):
    if path.count(0)==2:
        old=0;v=1
        for state in path:v*=T[state,old];old=state
        prob+=v
near(k,'d','Exactly two sunny days by complete path enumeration',prob,.234375,1e-12)
energy=sum(10*(.5+.5*.5**n)+3*(.5-.5*.5**n) for n in range(1,11))
near(k,'e','Energy expectation from daily marginals',energy,68.49658);near(k,'e','Independent geometric-sum identity',energy,65+3.5*(1-.5**10),1e-12)
ck(k,'f','Independent stationary-binomial value differs',abs(prob-stats.binom.pmf(2,3,.5))>.1)
why(k,'f','Conditional sunny probability after sunny is.75, and the first three marginals are.75,.625,.5625 rather than a common.5. Both independence and identical-success assumptions fail.')

k=start('D',3,'Raw bivariate-normal data are supplied for the rho=0 technology test. A decreasing ranking can be perfect while linear correlation is not. An influential ninth point must be investigated for validity; neither deleting it automatically nor declaring causality is justified.')
x=np.array([12,14,16,18,20,22,24,26.]);y=np.array([10.4,9.8,9.7,8.8,8.6,8.2,7.9,7.4]);reg=stats.linregress(x,y);rr=reg.rvalue
near(k,'a','Linear coefficients',[reg.intercept,reg.slope],[12.83095,-.2095238]);near(k,'a','Pearson coefficient',rr,-.9903281,1e-7)
t=rr*math.sqrt(6/(1-rr*rr));pv=stats.t.cdf(t,6)
near(k,'b','Correlation test statistic',t,-17.48383);near(k,'b','Lower-tail p',pv,1.122767e-6,1e-12);ck(k,'b','Reject at1%',pv<.01)
near(k,'c','Spearman reverse ranking',stats.spearmanr(x,y).statistic,-1,1e-12)
why(k,'c','The oxygen sequence strictly decreases with temperature but has nonconstant slopes between points; ranks capture monotonic order whereas Pearson quantifies linearity.')
near(k,'d','21-degree prediction',reg.intercept+21*reg.slope,8.430952);near(k,'d','20-degree original residual',8.6-(reg.intercept+20*reg.slope),-.04047619)
newr=stats.pearsonr(np.append(x,40),np.append(y,12)).statistic;near(k,'e','Nine-pair Pearson correlation',newr,.246713)
why(k,'e','The extra observation reverses the sign, but removal requires checking error or population mismatch. The original independent-site observational association does not establish a causal effect.')

k=start('D',4,'Independent residents sampled separately by zone produce a valid comparison of travel distributions. All expected counts exceed5 and degrees of freedom are4 or2, so both tables satisfy current AI bounds. Equal allocation across unequal zone populations needs population weighting for an overall resident estimate.')
obs=np.array([[30,20,10],[18,25,17],[12,15,33]],float);chi,pv,df,expected=stats.chi2_contingency(obs,correction=False)
near(k,'a','Expected table',expected,np.full((3,3),20),1e-10);ck(k,'a','Expected counts strictly greater than5',bool(np.all(expected>5)))
near(k,'b','Independence statistic',chi,24.8,1e-10);ck(k,'b','Degrees of freedom',df,4);near(k,'b','Upper-tail p',pv,5.518909e-5,1e-11);ck(k,'b','Reject5%',pv<.05)
contributions=(obs-expected)**2/expected;index=np.unravel_index(np.argmax(contributions),contributions.shape)
ck(k,'c','Largest contribution index',[int(i) for i in index],[2,2]);near(k,'c','Largest contribution',contributions[index],8.45,1e-12)
ck(k,'c','Cycling observed above independence expectation',obs[index]>expected[index])
combined=np.vstack([obs[0],obs[1]+obs[2]]);newchi,newp,newdf,newexp=stats.chi2_contingency(combined,correction=False)
near(k,'d','Combined table',combined,[[30,20,10],[30,40,50]],1e-12);near(k,'d','Combined expected table',newexp,[[20,20,20],[40,40,40]],1e-10)
near(k,'d','New statistic',newchi,15,1e-10);ck(k,'d','New degrees of freedom',newdf,2);near(k,'d','New p',newp,.0005530844,1e-10)
why(k,'e','Sample weighting assigns one third to each zone although residents may not. A suitable estimate is sum_z(population_z/total_population)*(bus_count_z/60), using within-zone random samples.')

k=start('D',5,'The second-order equation is given, and both eigenvalues are distinct negative reals, within the exact-solution AI boundary. Initial displacement and velocity determine both coefficients. The Euler comparison uses the same old state in both updates.')
M=np.array([[0,1],[-2,-3.]])
near(k,'a','Matrix first derivative from initial state',M@np.array([4,-2]),[-2,-2],1e-12)
near(k,'b','Distinct negative eigenvalues',sorted(np.linalg.eigvals(M)),[-2,-1],1e-12)
for lam in [-1,-2]:near(k,'b','Corresponding eigenvectors',M@np.array([1,lam]),lam*np.array([1,lam]),1e-12)
why(k,'b','Both distinct eigenvalues are negative real, so all eigendirections decay and the origin is a stable node.')
xx=lambda t:6*math.exp(-t)-2*math.exp(-2*t);vv=lambda t:-6*math.exp(-t)+4*math.exp(-2*t)
near(k,'c','Initial state of exact solution',[xx(0),vv(0)],[4,-2],1e-12)
for t in [0,.4,1,5]:near(k,'c','Exact solution satisfies DE',6*math.exp(-t)-8*math.exp(-2*t)+3*vv(t)+2*xx(t),0,1e-10)
ck(k,'d','Positive decreasing factors on domain',all(6-2*math.exp(-t)>0 and -6+4*math.exp(-t)<0 for t in [0,.1,1,10]))
why(k,'d','For every t>=0, e^-t is in(0,1], making x positive and v negative. Both exponentials tend to0, so there is no displacement sign crossing.')
state=np.array([4.,-2.]);euler=[]
for _ in range(2):state=state+.2*(M@state);euler.append(state.copy())
near(k,'e','Simultaneous Euler states',euler,[[3.6,-2.4],[3.12,-2.4]],1e-12)
near(k,'e','Exact state at.4s',[xx(.4),vv(.4)],[3.123262,-2.224604]);ck(k,'e','Signs of two Euler errors',state[0]<xx(.4) and state[1]<vv(.4))

k=start('D',6,'The acute triangular region gives the common Voronoi vertex inside the domain. All boundary vertices of every clipped cell are checked, so the maximin conclusion is global rather than a circumcentre guess. The separate road restriction changes the candidate set.')
A=np.array([0.,0]);B=np.array([8.,0]);C=np.array([4.,6]);V=np.array([4,5/3]);poly=[[0,0],[4,0],[4,5/3],[2,3]]
near(k,'a','AB bisector coordinate',float((A[0]+B[0])/2),4.,1e-12)
near(k,'a','AC bisector evaluated at midpoint',2*2+3*3,13,1e-12)
near(k,'b','Common vertex bisector equations',[V[0],2*V[0]+3*V[1]],[4,13],1e-12)
near(k,'b','All three post distances',[np.linalg.norm(V-s) for s in [A,B,C]],[13/3]*3,1e-12)
ck(k,'b','Vertex in service triangle',V[1]>=0 and V[1]<=1.5*V[0] and V[1]<=12-1.5*V[0])
near(k,'c','ClippedA Voronoi area',area(poly),23/3,1e-12)
candidates=[A,B,C,(A+B)/2,(A+C)/2,(B+C)/2,V]
nearest=[min(float(np.linalg.norm(p-s)) for s in [A,B,C]) for p in candidates]
near(k,'d','All candidate nearest-post distances',nearest,[0,0,0,4,math.sqrt(13),math.sqrt(13),13/3],1e-12)
ck(k,'d','Common vertex strictly best candidate',int(np.argmax(nearest)),6)
why(k,'d','Within each convex clipped cell, the supplied distance-maximization fact reduces the search to its vertices. The union consists exactly of posts, side midpoints andV; hence all cell interiors/edges are covered by these bounds.')
near(k,'e','Base-road centre nearest-post distance',min(np.linalg.norm(np.array([4,0])-s) for s in [A,B,C]),4,1e-12)
ck(k,'e','No base point exceeds4',all(min(np.linalg.norm(np.array([x,0])-s) for s in [A,B,C])<=4 for x in np.linspace(0,8,101)))

# Structural and resolution gates run against the final, currently saved files.
catalog=json.loads((TASK/'work/ai-mocks-2026/specification.json').read_text(encoding='utf-8'))
valid_refs={ref for group in catalog['referenceCatalogue'].values() for ref in group}
records=[];diagram_count=0;part_count=0
for s,d in data.items():
    assert d['strand']=='ai' and d['course']=='hl' and d['paper']=='2'
    assert d['minutes']==120 and d['marks']==110 and d['calculator']
    assert len(d['questions'])==6 and sum(q['marks'] for q in d['questions'])==110
    for q in d['questions']:
        rev=reviews[f"{s}{q['number']}"]
        assert q['section']=='' and set(q['syllabusRefs'])<=valid_refs
        assert sum(p['marks'] for p in q['parts'])==q['marks']
        ms={m['part']:m['steps'] for m in q['markScheme']}
        assert set(ms)=={p['label'] for p in q['parts']}
        for p in q['parts']:
            part_count+=1
            assert sum(int(re.search(r'(\d+)$',step['code']).group(1)) for step in ms[p['label']])==p['marks']
            assert rev['parts'][p['label']]['evidence'],('Missing independent part evidence',s,q['number'],p['label'])
            rev['parts'][p['label']]['fullPromptAndSchemeRead']=True
        if q.get('diagramSvg'):
            ET.fromstring(q['diagramSvg']);diagram_count+=1
            assert not re.search(r'<(?:script|foreignObject|image|defs|style)\b|\bon\w+\s*=|(?:href|url)\s*[:=(]',q['diagramSvg'],re.I)
    path=PAPERS/f'ai-hl-set-{s.lower()}-paper-2.json'
    records.append({'id':d['id'],'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'questions':6,'parts':sum(len(q['parts']) for q in d['questions']),'marks':110,'minutes':120,'diagrams':sum(bool(q.get('diagramSvg')) for q in d['questions'])})

a5=data['A']['questions'][4];b1=data['B']['questions'][0];c2=data['C']['questions'][1]
a5d=' '.join(x['text'] for x in next(m for m in a5['markScheme'] if m['part']=='d')['steps'])
b1b=' '.join(x['text'] for x in next(m for m in b1['markScheme'] if m['part']=='b')['steps'])
c2e=next(p['prompt'] for p in c2['parts'] if p['label']=='e')
assert '4415' in a5d, 'A5 nearest-dollar correction not applied'
assert '-445' in b1b or '−445' in b1b, 'B1 nearest-dollar correction not applied'
assert 'known' in c2e.lower(), 'C2(e) original-optimality logic finding not resolved'
assert not any("\\'" in json.dumps(d,ensure_ascii=False) for d in data.values()),'Literal escaped apostrophe remains'

report={
 'status':'passed', 'reviewer':'mock_exam_spec; independent of p2_author.py',
 'method':'Read every complete stem, every part and every markscheme; solved afresh without importing author code; inspected all nine rendered SVG diagrams against the stated data; checked official AI scope and reference numbering.',
 'questions':24,'parts':part_count,'calculationAssertions':count,'diagramsVisuallyInspected':diagram_count,
 'diagramPreviewDirectory':'work/ai-mocks-2026/p2-independent-preview',
 'papers':records,'questionReviews':list(reviews.values()),
 'resolvedFindings':[
  {'question':'A5(d)','finding':'Nearest-dollar answer originally retained only an unrounded value.','resolution':'Author now explicitly shows4415 dollars; independently rounded4414.953415... to4415.'},
  {'question':'B1(b)','finding':'Nearest-dollar NPV originally retained only an unrounded value.','resolution':'Author now explicitly shows -445 dollars; independently recalculated -444.6266... .'},
  {'question':'C2(e)','finding':'Original wording claimed unchanged optimum without establishing the old optimum, since prior bounds only32..34.','resolution':'Question now asks about best known tour from(c); retained34km tour justifies that statement. Reviewer additionally enumerated all24 original tours, but does not use that extra fact to mask the earlier logical gap.'},
  {'question':'multiple prose fields','finding':'Escaped apostrophes could leave literal backslashes in PDF prose.','resolution':'Final canonical JSON has no backslash-apostrophe sequences.'}
  ,{'question':'B2,C6,D6 spatial diagrams','finding':'The root review requested matching horizontal and vertical kilometre scales.','resolution':'All three updated SVGs were independently rendered and visually re-inspected: coordinates, labels, triangular/rectangular geometry and equal physical axis scales are correct. Numerical question content and solutions remain unchanged.'}
 ],
 'unresolvedFindings':[],
 'limits':'This report verifies original question mathematics, scope, marking and SVGs. Final composed PDF layout and live portal delivery require their separate release checks.'
}
out=ROOT/'docs/ib-ai-mocks-2026/p2-independent-review.json';out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'status':report['status'],'questions':24,'parts':part_count,'calculationAssertions':count,'diagrams':diagram_count,'papers':records},indent=2))
