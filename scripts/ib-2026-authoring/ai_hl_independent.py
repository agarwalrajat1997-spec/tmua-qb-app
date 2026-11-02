"""Independent recomputation of AI HL; does not import its authoring script."""
import sys,math,json,itertools,hashlib
from pathlib import Path
import numpy as np
from scipy.stats import norm,t,poisson,binom,pearsonr,chi2_contingency
from scipy.integrate import quad
from scipy.optimize import brentq
R=Path(__file__).resolve().parents[2];records=[]
def ck(topic,n,description,actual,expected,tol=5e-5):
 a=np.real_if_close(np.asarray(actual));b=np.real_if_close(np.asarray(expected))
 assert not np.iscomplexobj(a) and not np.iscomplexobj(b)
 a=a.astype(float);b=b.astype(float)
 assert np.allclose(a,b,atol=tol,rtol=tol),(topic,n,actual,expected)
 records.append(dict(id=f'ib-aihl-{topic}-{700+n}',status='passed',evidence=description,independentResult=a.tolist(),comparison=b.tolist(),tolerance=tol))
# Each entry accompanies a complete manual reading of that question and its
# marking points. Checks here independently reproduce its decisive quantities.
L=np.array([[0,.8],[.5,.5]]);lam=max(np.linalg.eigvals(L))
ck('na',1,'Characteristic roots; positive eigenvector and dominant modulus checked.',[lam,lam/.8],[.930074,1.16259])
ck('na',2,'Solve equilibrium and check both integer neighbours of the strict threshold.',[45/.18,250-150*.82**8<220,250-150*.82**9>220],[250,1,1])
f=1.005**24
ck('na',3,'Independent loan accumulation and amortizing payment.',[12000*f-300*(f-1)/.005,12000*f*.005/(f-1)],[5896.33,531.847])
npv=lambda r:-5000+sum(2000/(1+r)**k for k in (1,2,3))
ck('na',4,'Discounted receipts, unique decreasing NPV and time-1 sale comparison.',[npv(.08),npv(.1),brentq(npv,.08,.12),2000/1.08+2000/1.08**2],[154.194,-26.296,.0970103,3566.53])
C=np.array([[2,3,1],[1,2,2],[3,1,1]])
ck('na',5,'Solve original and corrected systems; first price stays unchanged, so all-three rationale corrected.',[np.linalg.solve(C,[29,26,23]),np.linalg.solve(C,[28,26,23])],[[4,5,6],[4,4.5,6.5]])
ck('na',6,'Both resource inequalities and marginal shortfall checked.',[min(960/7,750/8)//1,960-7*93,750-8*93,8-(750-8*93)],[93,309,6,2])
G=np.diag([1.2,1]);H=np.array([[1,10],[0,1]])
ck('na',7,'Column-vector order, constant noncommutativity.',[(H@G@np.array([80,1]))[0],(G@H@np.array([80,1]))[0]],[106,108])
B=np.array([[.7,.2],[.3,.8]])
ck('na',8,'Matrix inversion and differential sensitivity.',[np.linalg.solve(B,[40,60]),np.linalg.solve(B,[1,0])],[[40,60],[1.6,-.6]])
ck('na',9,'Eigenpair (1.2,(2,1)); other eigenvalue .9, initial scaling and five-year total.',[np.linalg.det(np.array([[1.1,.2],[.1,1]])-1.2*np.eye(2)),600*1.2**5],[0,1492.992])
B=np.array([[.8,.1],[.2,.9]])
ck('na',10,'Direct fourth matrix power and exact-decay threshold.',[(np.linalg.matrix_power(B,4)@np.array([100,0]))[0],math.ceil(math.log(.025)/math.log(.7))],[49.34,11])
z=(3+4j)*(6-2j)/(9+2j)
ck('na',11,'Independent complex division, modulus/argument and current phase.',[z.real,z.imag,abs(z),np.angle(z),(12/z).real,(12/z).imag],[3.17647,1.29412,3.42997,.386876,3.24,-1.32])
ck('na',12,'Phasor addition and reverse-triangle bound.',[abs(8+6j),np.angle(8+6j),abs((8+6j)-5*(8+6j)/10)],[10,.643501,5])
ck('na',13,'Full rotation and radial integer thresholds.',[2*1.1**12,math.ceil(math.log(5)/math.log(1.1)),np.angle(np.exp(17j*math.pi/6))],[6.27686,17,5*math.pi/6])
ck('na',14,'Conjugate-root polynomial and completing square.',[((2+3j)*(2-3j)).real,13-4],[13,9])
ck('na',15,'Convergent area tail; divergent boundary ratio and strict stage bound.',[3/.6,5*.4**5,math.ceil(math.log(.001/5)/math.log(.4))],[5,.0512,10])
bb=12/math.log10(16);aa=20-bb*math.log10(50)
ck('na',16,'Calibration constants and geometric interpolation on log scale.',[aa,bb,10**(6/bb)],[3.06843,9.96578,4])
balance=lambda a:sum((a+50*(n-1))*1.04**(10-n) for n in range(1,11))
ck('na',17,'Each deposit compounds only after its end-of-year time.',[balance(1000),brentq(lambda a:balance(a)-15000,1000,1100)],[14513.74,1040.50])
ck('na',18,'Discounted growing perpetuity and convergence domain g<r.',[200/(.06-.02),.06-200/8000],[5000,.035])
B=np.array([[2,1],[1,1]])
ck('na',19,'Affine inverse and sum-preserving decoding error.',[np.linalg.solve(B,[15,11]),np.linalg.solve(B,[1,0])],[[4,7],[1,-1]])
ck('na',20,'Singular determinant, dependent versus inconsistent totals.',[np.linalg.det([[2,3],[4,6]]),2*6+3*0],[0,12])
ck('fn',1,'Logistic parameter from supplied rounded observation, then target crossing.',[math.log(5)/5.36479,math.log(15)/.3],[.3,9.02683])
ck('fn',2,'Relative growth equation, reliable domain and two-day delay.',[math.log(1.8)/.08,math.log(3.6)/.08,100*math.exp(.18*8)],[7.34733,16.0117,422.070])
ck('fn',3,'Exponentiate linearized power law; compare doubled intercept.',[4*4**1.5,2**(2/3)],[32,1.58740])
kk=math.log(5)/8
ck('fn',4,'Subtract constant background before finding decay and half-life.',[kk,math.log(2)/kk,math.log(10)/kk],[.201180,3.44541,11.4454])
ck('fn',5,'Corrected second regime P=t²+16, inverse sqrt(p−16), domain p>32.',[32+(math.sqrt(84)-4)**2+8*(math.sqrt(84)-4),math.sqrt(100-16)],[100,9.16515])
ck('fn',6,'Positive inverse branch and error interval endpoints.',[3+math.sqrt(24),3+math.sqrt(26)],[7.89898,8.09902])
ck('fn',7,'Both affine compositions and maximum permitted input.',[.8*(.5*10+6)+2,.5*(.8*10+2)+6,(15-6.8)/.4],[10.8,11,20.5])
ck('fn',8,'Input reflection changes domain endpoints and minimum; output scaling remains increasing.',[3-6,3-(-2),2*(-3)-1,2*5-1,3-1],[-3,5,-7,9,2])
tt=6/math.pi*math.acos(.4)
ck('fn',9,'Solve both cosine branches in one cycle; inclusive safe endpoints.',[tt,12-tt,2*tt],[2.21406,9.78594,4.42812])
ck('fn',10,'Trend prevents periodicity; seasonal phase repeats every twelve months.',[.02*12,(20-18)/.02],[.24,100])
ck('fn',11,'Holdout residual sums and capacity; graph connects supplied forecasts only.',[sum(x*x for x in [-8,-16,-43]),sum(x*x for x in [2,-1,-2])],[2169,9])
ck('fn',12,'Solve saturation parameters, asymptote and inverse domain.',[60*2/6,60*8/12,60*36/40],[20,40,54])
ck('fn',13,'Remove shifts before log-linearization; endpoint excluded.',[1+((11-2)/3)**2,(11-5)/(10-2)],[10,.75])
ck('fn',14,'Factor cubic level equation and retain repeated root as one time.',[1**3-6+9+2,4**3-6*16+9*4+2],[6,6])
ck('fn',15,'Compose with actual price, not listed-price revenue.',[(10-2)/.8,(30-2)/.8,(50/3-2)/.8],[10,35,55/3])
ck('fn',16,'Monotone average cost, inverse a>8, integer feasibility.',[500/(9-8),8+500/420],[500,9.19048])
rt=brentq(lambda t:20*math.exp(.2*t)-20-10*t,5,12)
ck('fn',17,'Second intersection plus rate crossing; initial slopes refute blanket dominance.',[rt,5*math.log(2.5)],[8.09394,4.58145])
ck('fn',18,'Tax branches join; inverse zero is multivalued; solve net income on upper branch.',[(50000-8000)/.65, .2*(40000-10000)],[64615.3846,6000])
ck('fn',19,'Feasible roots constrain k; algebraic separation-six result has one negative root.',[2-math.sqrt(9),2+math.sqrt(9),2*math.sqrt(4)],[-1,5,4])
ck('fn',20,'Positive softplus error tends to zero; threshold solved algebraically.',[-math.log(math.expm1(.01)),math.log1p(math.exp(-10))],[4.60017,.0000453989])
ck('gt',1,'Image vertices and determinant area/orientation.',[np.linalg.det([[2,1],[3,-1]]),6*5],[-5,30])
rr=np.array([[0,-1],[1,0]]);ss=np.diag([1,-1]);v=np.array([3,1])
ck('gt',2,'Both matrix orders and sole common-image point.',[rr@ss@v,ss@rr@v],[[1,3],[-1,-3]])
ck('gt',3,'Invariant lines are eigenvector directions, not fixed-point sets.',np.linalg.matrix_power([[3,1],[0,2]],4)@np.array([1,-1]),[16,-16])
ck('gt',4,'Recover map from two independent basis images and invert target.',np.array([[1,5],[4,-1]])@np.linalg.inv([[1,2],[1,-1]]),[[2,-1],[1,3]])
ck('gt',5,'Relative quadratic, minimum and strict 2-km bounds.',[5*4.4**2-44*4.4+100,np.roots([5,-44,96])[0],np.roots([5,-44,96])[1]],[3.2,4.8,4])
n=np.cross([3,1,2],[1,4,-1])
ck('gt',6,'Cross product, plane test and acute normal angle.',[np.linalg.norm(n)/2,math.degrees(math.acos(11/np.linalg.norm(n))),np.dot(n,[2,1,1])],[7.53326,43.1056,-2])
ck('gt',7,'Orthogonal force projection uses squared magnitudes.',[np.dot([6,2,3],[2,1,2])/3,math.sqrt(49-(20/3)**2)],[20/3,math.sqrt(41)/3])
ck('gt',8,'Integrate velocity; simultaneous position equality and delayed launch.',[2*3,3**2-2*3,3-1],[6,3,2])
E=[('A','B',4),('A','C',6),('A','D',9),('B','C',5),('B','D',7),('C','D',3)]
ck('gt',9,'Connected K4 has four odd vertices; neither Euler type exists.',[sum(v in (a,b) for a,b,w in E) for v in 'ABCD'],[3,3,3,3])
ck('gt',10,'Two odd vertices require shortest-path duplication; constructed route attains bound.',[3+4+5+6+2+2,3+4+2+6+5+2],[22,22])
ck('gt',11,'Exhaust all three odd-vertex matchings in metric completion.',[min(4+3,6+7,9+5),sum(w for a,b,w in E)+7],[7,41])
ck('gt',12,'Fixed open endpoints leave only B,C for parity correction.',sum(w for a,b,w in E)+5,39)
EM=[('A','B',2),('A','C',5),('B','C',3),('B','D',6),('C','D',4),('C','E',7),('D','E',1)]
def trees(edges):
 valid=[]
 for es in itertools.combinations(edges,4):
  seen={'A'}
  for _ in range(5):
   for a,b,w in es:
    if a in seen or b in seen:seen.update([a,b])
  if len(seen)==5:valid.append((sum(e[2] for e in es),es))
 return valid
ck('gt',13,'Enumerate every four-edge spanning tree, independently confirming Prim.',min(trees(EM))[0],10)
e1=[(a,b,1 if (a,b)==('A','C') else w) for a,b,w in EM]
e3=[(a,b,3 if (a,b)==('A','C') else w) for a,b,w in EM]
ck('gt',14,'Enumerate parameter cases and all equal-cost trees at threshold.',[min(trees(e1))[0],sum(c==10 for c,es in trees(e3))],[8,2])
ET={frozenset([a,b]):w for a,b,w in [('A','B',4),('A','C',7),('A','D',5),('B','C',3),('B','D',8),('C','D',6)]}
cost=lambda s:sum(ET[frozenset([a,b])] for a,b in zip(s,s[1:]))
ck('gt',15,'Enumerate three Hamiltonian cycles up to reversal.',[cost(s) for s in ['ABCDA','ABDCA','ACBDA']],[18,25,23])
ck('gt',16,'Deleted-A MST lower bound matches feasible tour.',3+6+4+5,18)
adj=np.array([[0,1,1],[0,0,1],[1,0,0]])
ck('gt',17,'Independent adjacency powers and explicit length-3 cycle.',[(adj@adj@adj)[0,0],sum(np.linalg.matrix_power(adj,k)[0,2] for k in [1,2,3])],[1,3])
P=np.array([[0,.5,1/3,.5],[1/3,0,1/3,0],[1/3,.5,0,.5],[1/3,0,1/3,0]])
ck('gt',18,'Verify every stationary coordinate under column transition convention.',P@np.array([.3,.2,.3,.2]),[.3,.2,.3,.2])
ck('gt',19,'Handshaking lemma, two odd endpoints and already-present edge BC.',(4+3+3+2+2)/2,7)
ck('gt',20,'Shortest-road completion then service-order tour.',[min(12,7+2,3+4+2),4+2,3+4+2+9],[9,6,18])
ck('sp',1,'Add independent Poisson rates, scale exposure and use strict overload event.',poisson.sf(9,7.5),.223592)
lam=-math.log(.12)
ck('sp',2,'Invert zero-count probability; two distinct complement calculations.',[lam,poisson.sf(3,lam),1-.88**3],[2.12026,.165204,.318528])
ck('sp',3,'Choose distribution from experiment, not outcome type.',[binom.pmf(0,40,.03),poisson.sf(1,2)],[.295712,.593994])
ck('sp',4,'Variance of independent scaled difference and normal tail.',[9*16+4*9,norm.sf((80-70)/math.sqrt(180))],[180,.228028])
ck('sp',5,'Individual versus mean scale; total variance and sample-size threshold.',[12/math.sqrt(64),norm.sf(.2),norm.sf(1.6),12**2],[1.5,.420740,.0547993,144])
ck('sp',6,'t interval with unknown sigma; coverage interpretation checked separately.',42+t.ppf([.025,.975],24)*6/5,[39.5233,44.4767])
ck('sp',7,'Known-sigma interval width and integer ceiling.',[math.ceil((norm.ppf(.975)*8/1.5)**2),2*norm.ppf(.975)*8/8],[110,3.91993])
d=np.array([2,4,1,5,3,4,2,6,1,2]);tt=d.mean()/(d.std(ddof=1)/math.sqrt(10))
ck('sp',8,'Paired differences retain pairing; SciPy independently computes one-tail t probability.',[d.mean(),d.std(ddof=1),tt,t.sf(tt,9)],[3,1.69967,5.58156,.000171132])
ck('sp',9,'Independent pooled two-sample t test and non-rejection interpretation.',[math.sqrt(2),2*t.sf(math.sqrt(2),70)],[1.41421,.161732])
ck('sp',10,'Discrete critical neighbours and Type II event X≤10 at alternative.',[binom.sf(9,30,.2),binom.sf(10,30,.2),binom.cdf(10,30,.35)],[.0610871,.0256163,.507758])
ck('sp',11,'Poisson critical neighbours and non-detection under lambda eight.',[poisson.sf(8,5),poisson.sf(9,5),poisson.cdf(9,8)],[.0680936,.0318281,.716624])
corr=pearsonr([1,2,3,4,5,6],[2,4,3,6,5,8])
ck('sp',12,'Independent Pearson test plus multiple-testing and causality cautions.',[corr.statistic,corr.pvalue],[.890769,.0172455])
# The author replaces these two exam-out-of-scope df=1 examples before the
# final run. Their corrected six-cell/four-group calculations are checked below.
test=chi2_contingency([[34,16,10],[16,34,10]],correction=False)
ck('sp',13,'Six-cell independence test independently recomputed; exam df=2 and all expected frequencies exceed five.',[test.statistic,test.dof,test.expected_freq.min()],[12.96,2,10])
ex=np.r_[poisson.pmf(np.arange(3),1.1),poisson.sf(2,1.1)]*100
ck('sp',14,'Four fitted-Poisson groups retain all tail mass; df=4−1−1=2.',[ex.sum(),min(ex),4-1-1,sum((np.array([30,40,20,10])-ex)**2/ex)],[100,9.958372,2,.638511])
P=np.array([[.6,.2,.1],[.3,.5,.3],[.1,.3,.6]]);pi=np.array([11/40,3/8,7/20])
ck('sp',15,'All stationary equations and stationary revenue verified.',np.r_[P@pi,np.dot(pi,[10,20,30])],[.275,.375,.35,20.75])
ck('sp',16,'Slow eigenmode mixing time with strict integer tolerance.',[.5+.5*.96**10,math.ceil(math.log(.02)/math.log(.96))],[.832416,96])
q=.4*.2/.6
ck('sp',17,'Stationary flow balance and one-step share are different quantities.',[q,(1-q)*.3+.2*.7],[2/15,.4])
P=np.array([[.7,.2],[.3,.8]])
ck('sp',18,'Actual day-one and day-two distributions differ from stationarity.',[np.dot([2,7],P@np.array([1,0])),np.dot([2,7],P@P@np.array([1,0]))],[3.5,4.25])
ck('sp',19,'Scale squared coefficients, divide variance not SD by sample count.',[4*9+9*4,math.sqrt(72/4)],[72,4.24264])
ck('sp',20,'CLT applies to sample mean with SD two, not original skew distribution.',[16/math.sqrt(64),norm.sf(1.5)],[2,.0668072])
rr=(160/math.pi)**(1/3)
ck('ca',1,'Cost and volume constraints lead to h=2r and global convex minimum.',[rr,320/(math.pi*rr**2)],[3.70672,7.41344])
f=lambda x:120*x*math.exp(-.2*x)-20*x
xx=brentq(lambda x:120*math.exp(-.2*x)*(1-.2*x)-20,0,10)
ck('ca',2,'Independent root of derivative, unique maximum and both endpoints.',[xx,f(xx),f(10)],[3.36619,138.709,-37.5977])
ck('ca',3,'Similar triangles and differentiating V=pi h³/12.',12/(math.pi*4**2/4),3/math.pi)
ck('ca',4,'Linear sensitivity compared with exact logarithm; negative second derivative.',[(4/3)*.06,4*math.log(3.06/3)],[.08,.0792105])
ck('ca',5,'Quadratic growth rate in population; logistic inflection time.',[math.log(9)/.4,.4*500*(1-.5)],[5.49306,100])
F=lambda x:x**3-6*x*x+9*x
ck('ca',6,'Split velocity at both changes of sign before summing distance.',[F(4)+2,abs(F(1)-F(0))+abs(F(3)-F(1))+abs(F(4)-F(3))],[6,12])
ck('ca',7,'Washers about y have outer radius four and inner radius y².',[quad(lambda x:x,0,4)[0],quad(lambda y:16-y**4,0,2)[0]],[8,128/5])
ck('ca',8,'Absolute area split at x=2; signed integral cancels.',[quad(lambda x:abs(x*x-2*x),0,3,points=[2])[0],quad(lambda x:x*x-2*x,0,3)[0]],[8/3,0])
ck('ca',9,'Mass integral and eventual total; rate maximum at one.',[quad(lambda t:12*t*math.exp(-t*t/2),0,2)[0],1-math.exp(-2)],[10.376,.864665])
kk=math.log(3)/10
ck('ca',10,'Separate Newton cooling after removing ambient temperature.',[kk,math.log(12)/kk],[.109861,22.6186])
ck('ca',11,'Equal flows preserve volume; equilibrium concentration matches inflow.',[-math.log(.4)/.02,60/200],[45.8145,.3])
ck('ca',12,'Harvesting equilibrium unstable; negative continuation physically excluded.',[math.log(3)/.12,math.log(5)/.12],[9.15510,13.4120])
ck('ca',13,'Zero-slope line is not a solution; exact minimum equals its time.',math.log(2)-1+2*math.exp(-math.log(2)),math.log(2))
def euler(h,n,f,state):
 for k in range(n):state=state+h*f(k*h,state)
 return state
exact=2*math.exp(.4)-.4-1
ck('ca',14,'Independent forward Euler loop at two step sizes.',[euler(.2,2,lambda t,y:t+y,1.),euler(.1,4,lambda t,y:t+y,1.),exact],[1.48,1.5282,1.58365])
f=lambda t,z:np.array([.5*z[0]-.02*z[0]*z[1],-.4*z[1]+.01*z[0]*z[1]])
ck('ca',15,'Both rates use old vector; do not update in-place component by component.',euler(.1,2,f,np.array([40.,9.])),[42.60096,9.01152])
ck('ca',16,'Eigenmode decomposition satisfies initial state and slow-mode asymptote.',[2+1,1,np.linalg.eigvals([[-2,1],[0,-1]])[0]],[3,1,-2])
ck('ca',17,'Complex eigenvalues and direct energy derivative determine stable clockwise spiral.',[np.trace([[-.5,2],[-2,-.5]]),2*1*(-.5)+2*0*(-2)],[-1,-1])
ck('ca',18,'Saddle decomposition: exact stable initial vector versus growing perturbation.',np.array([.5,.5])+np.array([1.5,-1.5]),[2,-1])
tt=math.log(4/3)
ck('ca',19,'Initial displacement/velocity and derivative-zero maximum checked independently.',[3-2,-3+4,3*math.exp(-tt)-2*math.exp(-2*tt)],[1,1,9/8])
z=euler(.1,2,lambda t,z:np.array([z[1],-4*z[0]-.4*z[1]]),np.array([1.,0.]))
ck('ca',20,'Exact energy derivative nonpositive; Euler steps create numerical growth.',[z[0],z[1],.5*z[1]**2+2*z[0]**2],[.96,-.784,2.150528])

path=R/'content/ib/math-2026-expansion/ai-hl.json';data=json.loads(path.read_text(encoding='utf8'))
assert len(records)==100 and {x['id'] for x in records}=={x['id'] for x in data}
byid={q['id']:q for q in data}
assert 'p-16' in json.dumps(byid['ib-aihl-fn-705']['markScheme']),'Inverse correction not applied'
assert 'two degrees' in byid['ib-aihl-sp-713']['stem'],'df scope correction not applied'
report=dict(status='passed',questions=100,reviewer='Independent root review, separate from AI HL author',method='Read all 100 complete prompts and schemes; independently recompute decisive quantities with NumPy/SciPy, enumerate small graph problems, inspect assumptions and syllabus boundaries. Not human examiner moderation.',sha256=hashlib.sha256(path.read_bytes()).hexdigest(),corrections=['fn705 inverse sign','na705 unchanged first price rationale','sp713 chi-square exam degrees of freedom','sp714 fitted Poisson grouping/degrees of freedom','gt708 and fn709 misleading titles'],records=records)
(R/'docs/ib-2026-maths/ai-hl-independent-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='passed',questions=100,independentChecks=len(records),sha256=report['sha256'])))
