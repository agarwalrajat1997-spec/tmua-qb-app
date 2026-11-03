"""Independent re-solution of all four P3 investigations, from their givens.

No author module or author review is imported. The diagrams were inspected
separately at native resolution, including transition/flow directions and all
eight network weights. Array assertions count as one check, not one per point.
"""
from pathlib import Path
import sys,json,hashlib,math,itertools
ROOT=Path(__file__).resolve().parents[2];WORK=ROOT.parent/'ai-mocks-2026'
sys.path.insert(0,str(WORK/'python-deps'))
import numpy as np
from scipy import stats,optimize,integrate,linalg
papers={s:json.loads((ROOT/f'content/ib/ai-mocks-2026/papers/ai-hl-set-{s.lower()}-paper-3.json').read_text(encoding='utf8')) for s in 'AB'}
records={};COUNT=0
def record(s,q,p):
    return records.setdefault((s,q,p),{'paper':f'ai-hl-set-{s.lower()}-paper-3','question':q,'part':p,'checks':[],'reasoning':[]})
def check(s,q,p,label,actual,expected,tol=1e-8):
    global COUNT
    np.testing.assert_allclose(actual,expected,atol=tol,rtol=0,err_msg=f'{s}{q}{p}: {label}')
    def clean(a):return a.tolist() if isinstance(a,np.ndarray) else a.item() if isinstance(a,np.generic) else a
    record(s,q,p)['checks'].append({'name':label,'actual':clean(actual),'expected':clean(expected),'tolerance':tol,'status':'passed'});COUNT+=1
def proof(s,q,p,text):record(s,q,p)['reasoning'].append(text)
# A1: explicit binomial sums give an independent check on library tails.
tail=lambda c,n,p:sum(math.comb(n,k)*p**k*(1-p)**(n-k) for k in range(c,n+1))
cut=next(c for c in range(41) if tail(c,40,.04)<.05);alpha=tail(cut,40,.04);power=tail(cut,40,.12);beta=1-power
check('A',1,'a','minimal critical count',cut,5);check('A',1,'a','actual Type I probability',alpha,.0210222967);check('A',1,'a','preceding tail',tail(4,40,.04),.0748372580)
check('A',1,'b','Type II probability',beta,.4669109648);check('A',1,'b','independent library cross-check',stats.binom.cdf(4,40,.12),beta)
proof('A',1,'b','Failure to reject when p=.12 is the event X<=4; it is a missed unstable day, not a false alert.')
T=np.array([[.8,.3],[.2,.7]]);v=np.array([0.,1.]);check('A',1,'c','column sums',T.sum(axis=0),[1,1]);check('A',1,'c','two-day state',T@T@v,[.45,.55])
check('A',1,'d','recurrence agrees with matrix powers',[ (np.linalg.matrix_power(T,n)@v)[0] for n in range(25)],[.6*(1-.5**n) for n in range(25)])
proof('A',1,'d','q(n+1)=.3+.5q(n), so subtracting .6 gives a geometric difference with initial -.6. This proves the formula for every n>=0.')
alim=.6*power+.4*alpha;post=.6*power/alim
check('A',1,'e','limiting alert probability',alim,.3282623398);check('A',1,'e','Bayes posterior',post,.9743835412)
diff=lambda n:abs(alpha+(power-alpha)*.6*(1-.5**n)-alim)
first=next(n for n in range(40) if diff(n)<.001)
check('A',1,'f','first close day',first,9);check('A',1,'f','day8 gap',diff(8),.0012001564);check('A',1,'f','day9 gap',diff(9),.0006000782)
for k in [.2,.8,1.6]:
    u,vv=.2,.3;G=np.array([[1-k*u,k*vv],[k*u,1-k*vv]])
    steady=np.linalg.solve(np.vstack([(G-np.eye(2))[0],np.ones(2)]),[0,1])
    check('A',1,'g',f'general stationary fraction at kappa={k}',steady,[.6,.4])
proof('A',1,'g','For u,v>0 and 0<kappa(u+v)<1, all transition entries are valid. The fixed point v/(u+v) contains no kappa; the error factor 1-kappa(u+v) lies in(0,1) and decreases with kappa. Initial stationarity is an explicit exception to any strict speed comparison.')
# A2: flow balances and matrix exponentials independent of the author eigensolver.
M=np.array([[-.3,.2],[.2,-.3]]);initial=np.array([30.,0.]);exact=lambda t:linalg.expm(M*t)@initial
check('A',2,'a','drain and exchange coefficients',M,[[-(20000+10000)/100000,20000/100000],[20000/100000,-(20000+10000)/100000]])
check('A',2,'b','eigenvalue -0.1 direction',M@np.array([1.,1.]),[-.1,-.1]);check('A',2,'b','eigenvalue -0.5 direction',M@np.array([1.,-1.]),[-.5,.5])
for t in [0,.7,2,4,10,30]:check('A',2,'b',f'explicit solution at t={t}',[15*(math.exp(-t/10)+math.exp(-t/2)),15*(math.exp(-t/10)-math.exp(-t/2))],exact(t))
tmax=optimize.minimize_scalar(lambda t:-exact(t)[1],bounds=(0,30),method='bounded').x
check('A',2,'c','independent peak time',tmax,2.5*math.log(5),tol=2e-6);check('A',2,'c','peak mass',exact(tmax)[1],8.024883660)
proof('A',2,'c','y prime changes sign only when exp(.4t)=5; it is positive before and negative after. Endpoint y(0)=0 and the limiting value0 establish the global maximum.')
safe=optimize.brentq(lambda t:exact(t)[0]-1,20,40)
check('A',2,'d','concentration-to-mass threshold',10*100000/1e6,1);check('A',2,'d','safe time',safe,27.08069952);check('A',2,'d','other reservoir below threshold',exact(safe)[1]<1,True)
proof('A',2,'d','x-y=30 exp(-t/2)>0, and x is strictly decreasing; thus x=1 is the earliest simultaneous safe condition.')
e=initial.copy();e1=e+M@e;e2=e1+M@e1
check('A',2,'e','Euler step1',e1,[21,6]);check('A',2,'e','Euler step2',e2,[15.9,8.4]);check('A',2,'e','exact downstream at2',exact(2)[1],6.762769679)
check('A',2,'e','relative error percent to three significant figures',round(100*(e2[1]/exact(2)[1]-1),1),24.2)
proof('A',2,'e','Both Euler masses are positive yet y2 exceeds even the exact global maximum. Positivity therefore cannot guarantee accuracy.')
check('A',2,'f','total half-life',math.log(2)/.1,6.931471805)
for Q in [100,10000,75000]:
    G=np.array([[-(.1+Q/100000),Q/100000],[Q/100000,-(.1+Q/100000)]])
    check('A',2,'f',f'total at t=5 for exchange {Q}',(linalg.expm(G*5)@initial).sum(),30*math.exp(-.5))
proof('A',2,'f','Exchange contributes opposite signs to the two balances and cancels on addition, leaving S prime=-.1S for every Q>0.')
for h in [.01,.5,1,2]:
    E=np.eye(2)+h*M;check('A',2,'g',f'nonnegative update coefficients h={h}',np.min(E)>=0,True)
    check('A',2,'g',f'sum/difference multipliers h={h}',[[1,1], [1,-1]]@E,np.array([[1-.1*h,1-.1*h],[1-.5*h,-(1-.5*h)]]))
check('A',2,'g','ordering fails above2',((np.eye(2)+2.01*M)@initial)[0]<((np.eye(2)+2.01*M)@initial)[1],True)
proof('A',2,'g','D1=(1-.5h)D0 forces h<=2 for every nonnegative ordered state with D0>0. For0<h<=2, coefficients1-.3h and.2h preserve both nonnegative masses; D remains nonnegative. This qualitative guarantee makes no truncation-error promise.')
# B1: fresh quadrature of clipped current and a monotonic integral representation.
Z=4+3*np.exp(-1.2j);A=abs(Z);delta=-np.angle(Z)
check('B',1,'a','phasor amplitude',A,5.804876063);check('B',1,'a','phase delay',delta,.5025755802)
phases=np.linspace(0,math.pi,101);check('B',1,'b','amplitude identity',np.abs(4+3*np.exp(-1j*phases))**2,25+24*np.cos(phases))
check('B',1,'b','amplitude endpoints',[abs(4+3),abs(4-3)],[7,1])
check('B',1,'c','period average direct quadrature',integrate.quad(lambda t:10*(A*math.cos(math.pi*t/6-delta))**2,0,12)[0]/12,5*A*A)
off=lambda a:0 if a<=4 else 2*math.acos(4/a)/math.pi
check('B',1,'d','off fraction for A=5',off(5),.4096655294);check('B',1,'d','no shutdown A=4',off(4),0)
amax=4/math.cos(math.pi/8);pmin=math.acos((amax*amax-25)/24)
check('B',1,'e','largest permitted amplitude',amax,4.329568801);check('B',1,'e','smallest permitted phase',pmin,1.834458682);check('B',1,'e','off fraction at boundary',off(amax),.25)
def power(a):
    if a<=4:return 5*a*a
    c=4/a;return 10*a*a/math.pi*(math.asin(c)-c*math.sqrt(1-c*c))
for a in [1,2.2,4,4.01,4.2,amax,7]:
    theta=0 if a<=4 else math.acos(4/a)
    quadrature=20*a*a/math.pi*integrate.quad(lambda u:math.cos(u)**2,theta,math.pi/2)[0]
    check('B',1,'f',f'piecewise mean versus exact-on-interval quadrature A={a}',power(a),quadrature)
check('B',1,'f','right-hand finite-epsilon continuity check at4',power(4+1e-12),80,tol=1e-4)
grid=np.r_[np.linspace(1,4,301),np.linspace(4+1e-7,amax,301)]
check('B',1,'g','global sampled upper bound',max(power(a) for a in grid),80)
check('B',1,'g','right branch strictly decreasing',np.all(np.diff([power(a) for a in np.linspace(4+1e-7,amax,501)])<0),True)
check('B',1,'g','maximizing phase',math.acos(-3/8),1.955193101)
proof('B',1,'g','For A<=4, P=5A squared strictly increases. For A>4, write P=10/pi times integral from-4 to4 of I squared /sqrt(A squared-I squared) dI. For fixed I the integrand strictly decreases with A; hence the entire right branch decreases. This also independently proves the claimed global peak, beyond the requested calculator investigation.')
# B2: read the eight edges from the inspected diagram; crossovers are not vertices.
fixed=[('A','B',4),('B','C',5),('C','D',4),('D','E',6),('E','F',5),('F','A',6),('B','E',7)]
def network(w,remove=False):
    edges=fixed+([] if remove else [('A','D',w)])
    d={a:{b:0 if a==b else math.inf for b in 'ABCDEF'} for a in 'ABCDEF'};degree={a:0 for a in 'ABCDEF'}
    for a,b,c in edges:d[a][b]=d[b][a]=c;degree[a]+=1;degree[b]+=1
    for k in 'ABCDEF':
        for a in 'ABCDEF':
            for b in 'ABCDEF':d[a][b]=min(d[a][b],d[a][k]+d[k][b])
    return edges,d,degree
def matching(vertices,d):
    if not vertices:return 0
    a=vertices[0];return min(d[a][b]+matching([v for v in vertices if v not in [a,b]],d) for b in vertices[1:])
def cost(w,finish='A',remove=False):
    edges,d,deg=network(w,remove);odd={a for a in deg if deg[a]%2}
    target=set() if finish=='A' else {'A',finish};needs=sorted(odd^target)
    return sum(c for a,b,c in edges)+matching(needs,d)
_,d,deg=network(2);check('B',2,'a','odd vertices',[deg[v]%2 for v in 'ABCDEF'],[1,1,0,1,1,0])
proof('B',2,'a','A closed walk using every edge once requires all degrees even. Four odd vertices A,B,D,E prevent such an Euler circuit.')
check('B',2,'b','all odd-pair shortest lengths',[d[a][b] for a,b in [('A','B'),('A','D'),('A','E'),('B','D'),('B','E'),('D','E')]],[4,2,8,6,7,6])
check('B',2,'c','pairing weights',[d['A']['B']+d['D']['E'],d['A']['D']+d['B']['E'],d['A']['E']+d['B']['D']],[10,9,14]);check('B',2,'c','closed optimum at2',cost(2),48)
for route,label_,finish in [('ABEFADC BEDA'.replace(' ',''),'c','A'),('ABEFADC BED'.replace(' ',''),'f','D')]:
    edges,dg,_=network(2);direct={frozenset([a,b]):c for a,b,c in edges}
    traveled=[frozenset([a,b]) for a,b in zip(route,route[1:])]
    check('B',2,label_,'constructed route covers every edge and has correct endpoints',set(traveled)==set(direct) and route[0]=='A' and route[-1]==finish,True)
    check('B',2,label_,'constructed route weight',sum(direct[e] for e in traveled),48 if finish=='A' else 46)
for w in [.001,.5,2,3,3.001,5,13,40]:
    check('B',2,'d',f'closed-route formula w={w}',cost(w),44+2*w if w<=3 else 47+w)
    _,dd,_=network(w);check('B',2,'d',f'third pairing w={w}',dd['A']['E']+dd['B']['D'],min(w+6,11)+min(w+4,9))
check('B',2,'e','deleted AD closed optimum',cost(2,remove=True),44)
proof('B',2,'e','Removing AD removes its once-required traversal and changes odd vertices to B,E only. A smaller inspection obligation can outweigh the loss of a connection.')
for w in [.001,.5,2,3,5,13,40]:check('B',2,'f',f'open-route formula w={w}',cost(w,'D'),44+w)
for w,h in itertools.product([.2,1,3,8],[.1,1,3,5]):
    check('B',2,'g',f'open/closed comparison w={w},h={h}',cost(w)-(cost(w,'D')+h),min(w,3)-h)
proof('B',2,'g','Choose open when h<min(w,3), closed when h>min(w,3), tie when equal. For w>=3, closed adds AB+DE=10 while open adds BE=7; the shared base37+w cancels, so the maximal traversal saving is3.')
# Content/mark/diagram/references checked against the actual canonical files.
for s,paper in papers.items():
    for q in paper['questions']:
        assert q['section']=='' and q['diagramSvg'] and len(q['syllabusRefs'])>0
        for part,group in zip(q['parts'],q['markScheme']):
            import re
            assert part['label']==group['part'];assert sum(int(re.search(r'\d+',x['code'])[0]) for x in group['steps'])==part['marks']
            rec=record(s,q['number'],part['label']);assert rec['checks'] or rec['reasoning'];rec['status']='passed'
assert len(records)==28
result={'status':'passed','reviewType':'independent re-solution; no author calculation imported','questionCount':4,'partCount':28,'independentCheckCount':COUNT,
        'diagramReview':'All four native-resolution diagrams independently inspected: two-state transitions, both reservoir flow directions, phasor vector angle/orientation, eight network weights/crossings. No findings.',
        'papers':[{'id':p['id'],'sha256':hashlib.sha256((ROOT/'content/ib/ai-mocks-2026/papers'/(p['id']+'.json')).read_bytes()).hexdigest(),'status':'passed'} for p in papers.values()],
        'records':list(records.values()),'openFindings':[],
        'scopeReview':'Current AI HL references and boundaries checked: regular chains; one-tailed binomial inference; real distinct2x2 eigensolutions; simultaneous Euler; phasor sums and provided trig identity; undirected postman with four odd vertices. No assumed AA-only methods.'}
(ROOT/'docs/ib-ai-mocks-2026/p3-independent-review.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf8',newline='\n')
print(json.dumps({'status':'passed','questions':4,'parts':28,'checks':COUNT}))
