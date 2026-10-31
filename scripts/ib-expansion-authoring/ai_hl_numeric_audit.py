"""Separate author numerical audit. Does not import the generation modules.

Uses iteration, residual equations, direct probability sums and quadrature to
cross-check the author ledger. Independent cross-review is still required.
"""
from pathlib import Path
import json,sys,math,hashlib,itertools
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'work'/'aa-sl-deps'))
import numpy as np
import mpmath as mp
from scipy import optimize,linalg
mp.mp.dps=40
rows=json.loads((ROOT/'docs/ib-expansion-reviews/ai-hl-author-ledger.json').read_text(encoding='utf8'))
results=[]
def normalcdf(x,mu=0,sd=1):return float((1+mp.erf((x-mu)/(sd*mp.sqrt(2))))/2)
def binpmf(k,n,p):return math.comb(n,k)*p**k*(1-p)**(n-k)
def bincdf(k,n,p):return sum(binpmf(j,n,p) for j in range(k+1))
def poipmf(k,lam):return math.exp(-lam)*lam**k/math.factorial(k)
def poicdf(k,lam):return sum(poipmf(j,lam) for j in range(k+1))
def tcdf(x,df):
 tail=float(mp.betainc(df/2,.5,0,df/(df+x*x),regularized=True))/2
 return 1-tail if x>=0 else tail
def quantile(cdf,p,lo=-20,hi=20):return optimize.brentq(lambda x:cdf(x)-p,lo,hi,xtol=1e-13)
def seq(u,r,c,n):
 for _ in range(n):u=u*r+c
 return u
def matrixiterate(T,x,n):
 for _ in range(n):x=T@x
 return x
def checks(topic,f,v):
 d={}
 if topic=='na':
  if f==1:
   a=120+15*v;inc=18+2*v;total=sum(a+j*inc for j in range(12));d={'annualTotal':total,'maximumIncrease':(total-100-12*a)/sum(range(12))}
  elif f==2:
   a=65+5*v;r=1.14+.01*v;terms=[a*r**j for j in range(200)];d={'sum8':sum(terms[:8]),'firstSeason':next(j+1 for j,x in enumerate(terms) if x>300)}
  elif f==3:
   p=18000+1000*v;r=.045+.003*v;nom=seq(p,1+r,0,6);real=nom/seq(1,1.025,0,6);d={'nominal':nom,'realValue':real}
  elif f==4:
   loan=48000+2000*v;i=(.06+.004*v)/12;pay=loan/sum((1+i)**-k for k in range(1,61));d={'monthlyPayment':pay,'balance24':seq(loan,1+i,-pay,24)}
  elif f==5:
   x=6.2+.2*v;d={'lowerLevel':float(10*mp.log10(x-.05)),'upperLevel':float(10*mp.log10(x+.05))}
  elif f==6:
   c=6+v;d={'admissibleRoot':optimize.brentq(lambda x:3*math.log(x)+3*math.log(x-1)-c,1+1e-9,100)}
  elif f==7:d={'lengthScale':1.3+.1*v,'areaRatio':((1.3+.1*v)**3)**(2/3)}
  elif f==8:
   h=2.5+.2*v;r=.65+.03*v;d={'totalDistance':h+2*sum(h*r**n for n in range(1,1000)),'firstSmallRebound':next(n for n in range(1,1000) if h*r**n<.01)}
  elif f==9:
   a=900+100*v;r=.6+.03*v;tot=sum(a*r**j for j in range(1000));d={'infiniteSum':tot,'sum5':sum(a*r**j for j in range(5)),'stage95':next(n for n in range(1,100) if sum(a*r**j for j in range(n))>.95*tot),'perturbedTotal':sum(a*(r+.02)**j for j in range(1000))}
  elif f==10:
   z=np.linalg.solve(np.array([[2,1+v],[-1-v,2]]),np.array([3+v,4]));d={'quotientReal':z[0],'quotientImag':z[1],'modulus':math.hypot(*z),'argument':math.atan2(z[1],z[0])}
  elif f==11:
   z=np.roots([1,-2*(2+v),(2+v)**2+9])[0];d={'rootReal':z.real,'rootImagMagnitude':abs(z.imag),'rootModulus':abs(z)}
  elif f==12:
   a=4+v;b=3+v;p=.6+.1*v;C=a+b*math.cos(p);S=-b*math.sin(p);amp=math.hypot(C,S);phase=math.atan2(-S,C);d={'resultantAmplitude':amp,'resultantPhase':phase,'firstMaximum':quantile(lambda t:(2*t+phase)/(2*math.pi),1,0,4)}
  elif f==13:
   z=1+0j;factor=(1.2+.1*v)*complex(math.cos(.4+.05*v),math.sin(.4+.05*v))
   for _ in range(5):z*=factor
   d={'powerReal':z.real,'powerImag':z.imag,'powerModulus':abs(z)}
  elif f==14:d={'distance':math.sqrt(2*((2+v)**2+9))}
  elif f==15:
   T=np.array([[2,3],[4,1]]);rev=T@np.array([12+v,8+v]);sol=np.linalg.solve(T,rev);d={'adultPrice':sol[0],'childPrice':sol[1],'revenue1':rev[0],'revenue2':rev[1]}
  elif f==16:
   T=np.array([[1,2,1],[2,1,3],[3,2,2]]);rhs=T@np.array([4+v,5+v,6+v]);x=np.linalg.solve(T,rhs);d={'volume1':x[0],'volume2':x[1],'volume3':x[2],'determinant':7}
  elif f==17:
   x=np.linalg.solve([[2,1],[1,1]],[2*(1+v)+5+v,1+v+5+v]);d={'decoded1':x[0],'decoded2':x[1]}
  elif f==18:
   T=np.array([[2,3],[1,4+v]]);c=np.linalg.solve(T,[0,1]);d={'determinant':2*(4+v)-3,'change1':c[0],'change2':c[1]}
  elif f==19:
   ev=sorted(np.linalg.eigvals([[3+v,1],[1,3+v]]));d={'eigenvalue1':ev[1],'eigenvalue2':ev[0]}
  elif f==20:
   l=1.1+.02*v;T=np.array([[(l+.7)/2,(l-.7)/2],[(l-.7)/2,(l+.7)/2]]);x=matrixiterate(T,np.array([80+10*v,40.]),10);d={'population10a':x[0],'population10b':x[1],'dominantEigenvalue':max(np.linalg.eigvals(T))}
  elif f==21:
   r=.72+.03*v;c=90+10*v;d={'equilibrium':seq(100,r,c,1000),'amount5':seq(100,r,c,5),'safeInflow':250-r*250}
  elif f==22:
   a=.8-.02*v;b=.15+.01*v;T=np.array([[a,b],[1-a,1-b]]);x=matrixiterate(T,np.array([600.,400.]),8);s=matrixiterate(T,np.array([1.,0.]),1000);d={'state8a':x[0],'state8b':x[1],'stationaryA':s[0]}
  elif f==23:
   R=180+20*v;i=.004+.0002*v;factor=seq(0,1+i,1,120);d={'futureValue':seq(0,1+i,R,120),'requiredDeposit':35000/factor,'inflationPercent':100*optimize.brentq(lambda j:28000*(1+j)**10-35000,0,.1)}
  elif f==24:
   u=1000+100*v;r=.91+.01*v;first=lambda r:next(n for n in range(1000) if u*r**n<=400);n=first(r);d={'reopenYear':n,'conservativeYear':first(r+.005),'massBefore':u*r**(n-1),'massAt':u*r**n}
  elif f==25:
   rho=1.04+.01*v;h=optimize.brentq(lambda h:(1-h)*rho-1,0,.5);d={'dominantEigenvalue':rho,'harvestFraction':h,'controlledOtherEigenvalue':(1-h)*.6}
 elif topic=='fn':
  if f==1:d={'checkout20':(1.08+.01*v)*((12+v)*20+5+v),'orderDifference':(5+v)*(.08+.01*v)}
  elif f==2:d={'inverseAtTarget':8+v}
  elif f==3:
   a=7+v;b=.18+.02*v;d={'time60':optimize.brentq(lambda t:a*math.exp(b*t)-60,0,20),'rangeMaximum':a*math.exp(20*b)}
  elif f==4:
   s=2+v;h=1+v;d={'leftIntersection':optimize.brentq(lambda x:s*(x-h)**2-12,h-5,h),'rightIntersection':optimize.brentq(lambda x:s*(x-h)**2-12,h,h+5)}
  elif f==5:d={'outputDifference':3*(2+v)-3}
  elif f==6:
   N=240+20*v;half=8+v;k=quantile(lambda k:1-math.exp(-k*half),.5,0,1);d={'decayConstant':k,'time30':optimize.brentq(lambda t:N*math.exp(-k*t)-30,0,100)}
  elif f==7:
   amb=18+v;k=optimize.brentq(lambda k:amb+(90-amb)*math.exp(-5*k)-(55+v),0,1);d={'coolingConstant':k,'time30':optimize.brentq(lambda t:amb+(90-amb)*math.exp(-k*t)-30,0,100)}
  elif f==8:
   a=20+v;b=6+v;d={'inputFor50':optimize.brentq(lambda x:a+b*math.log(x)-50,.01,1000),'doublingIncrease':b*(math.log(4)-math.log(2))}
  elif f==9:d={'firstMaximumDay':80+5*v+365/4,'aboveMidlineDays':365/2}
  elif f==10:
   amp=1.5+.1*v;phase=1+.2*v;fun=lambda t:3+amp*math.sin(math.pi*(t-phase)/6)-3.8;t1=optimize.brentq(fun,phase,phase+3);t2=optimize.brentq(fun,phase+3,phase+6);d={'boundary1':t1,'boundary2':t2,'duration':t2-t1}
  elif f==11:
   L=1200+100*v;C=5+v;k=.3+.02*v;fun=lambda t:L/(1+C*math.exp(-k*t));d={'initial':fun(0),'time80':optimize.brentq(lambda t:fun(t)-.8*L,0,100),'timeHalf':optimize.brentq(lambda t:fun(t)-.5*L,0,100)}
  elif f==12:
   L=800+100*v;C=L/100-1;k=optimize.brentq(lambda k:L/(1+C*math.exp(-4*k))-(300+20*v),0,2);d={'C':C,'k':k,'prediction8':L/(1+C*math.exp(-8*k))}
  elif f==13:
   b=(8+5+v-16)/4;d={'joinParameter':b,'time30':optimize.brentq(lambda t:t*t+b*t-30,4,8)}
  elif f==14:d={'charge18':8+v+(2.5+.25*v)*10+(1.5+.1*v)*8,'boundaryCharge':8+v+(2.5+.25*v)*10}
  elif f==15:
   a=2.4+.2*v;b=1.3+.1*v;d={'exponent':b,'coefficient':a,'prediction12':float(mp.exp(mp.log(a)+b*mp.log(12))),'doublingFactor':float(mp.exp(b*mp.log(2)))}
  elif f==16:
   a=1.8+.1*v;b=.23+.02*v;d={'initial':float(mp.exp(a)),'doublingTime':optimize.brentq(lambda t:math.exp(b*t)-2,0,20),'time100':optimize.brentq(lambda t:math.exp(a+b*t)-100,0,30)}
  elif f==17:
   c=10+v;xs=range(4);ys=[c,c+5,c+13,c+23];f1=lambda x:c+3*x+1.5*x*x;f2=lambda x:c*1.5**x;d={'quadraticSSE':sum((y-f1(x))**2 for x,y in zip(xs,ys)),'exponentialSSE':sum((y-f2(x))**2 for x,y in zip(xs,ys)),'quadratic6':f1(6),'exponential6':f2(6)}
  elif f==18:
   a=1+v;A=np.array([[1,1],[8,4]]);x=np.linalg.solve(A,[a+2,8*a+8]);d={'coefficientA':x[0],'coefficientB':x[1],'prediction1p5':x[0]*1.5**3+x[1]*1.5**2+4}
  elif f==19:d={'inputForTarget':(12+v)/2-2,'maximumResponse':4+v+(12+v)/2}
  elif f==20:
   a=80+10*v;b=4+v;sol=optimize.minimize_scalar(lambda x:-((a-20)*x-b*x*x),bounds=(0,a/b),method='bounded',options={'xatol':1e-12});d={'continuousOptimum':sol.x,'maximumProfit':-sol.fun}
  elif f==21:
   x=np.arange(1.,6.);y=np.array([float(f'{z:.6f}') for z in (3+v)*x**1.4+np.array([.2,-.3,.4,-.2,.1])]);B=np.column_stack([np.ones(5),np.log(x)]);co=np.linalg.lstsq(B,np.log(y),rcond=None)[0];a=math.exp(co[0]);b=co[1];d={'regressionIntercept':co[0],'regressionSlope':b,'coefficient':a,'originalSSE':sum((y-a*x**b)**2),'prediction3p5':a*3.5**b,'prediction20':a*20**b}
  elif f==22:
   L=100+10*v;K=4+v;inv=lambda y:optimize.brentq(lambda x:L*x/(K+x)-y,0,1000);d={'estimate':inv(60),'lower':inv(59),'upper':inv(61),'at90':inv(.9*L),'at95':inv(.95*L)}
  elif f==23:
   L=1000+100*v;k=.4+.02*v;d={'exponential8':(L/10)*math.exp(8*k),'logistic8':L/(1+9*math.exp(-8*k)),'expHalfTime':optimize.brentq(lambda t:(L/10)*math.exp(k*t)-L/2,0,20),'logisticHalfTime':optimize.brentq(lambda t:L/(1+9*math.exp(-k*t))-L/2,0,20)}
  elif f==24:
   a=25+v;b=7+.5*v;shift=.4+.1*v;fun=lambda t:a+b*math.cos(math.pi*t/6);d={'shiftedMonth6':fun(6-shift)+2,'plannerError':fun(6-shift)-fun(6),'maximumTime':shift}
  elif f==25:
   L=3*(5+v)+20;k=(2+.2*v)/20;d={'capacity':L,'k':k,'targetTime':optimize.brentq(lambda t:L-20*math.exp(-k*(t-3))-(L-5),3,40)}
 elif topic=='gt':
  if f==1:
   r=4+.5*v;a=1.2+.1*v;d={'arc':r*a,'sectorArea':r*r*a/2,'perimeter':r*(2+a),'uncoveredArea':(2*math.pi-a)*r*r/2}
  elif f==2:
   c=.2+.1*v;a=math.asin(c);d={'solutions':[a,math.pi-a,2*math.pi+a,3*math.pi-a],'cosMagnitude':math.cos(a)}
  elif f==3:
   a=8+v;b=12+v;c=65+5*v;side=lambda C:abs(complex(a,0)-b*complex(math.cos(math.radians(C)),math.sin(math.radians(C))));d={'thirdSide':side(c),'area':a*b*math.sin(math.radians(c))/2,'lowerSide':side(c-1),'upperSide':side(c+1)}
  elif f==4:d={'imagePx':v,'imagePy':4,'area':2}
  elif f==5:d={'RSx':-3,'RSy':2*(2+v),'SRx':-3*(2+v),'SRy':2}
  elif f==6:d={'imageArea':10*(2+v),'originalX':4/(2+v),'originalY':4}
  elif f==7:
   r=.4+.02*v;q=3*r*r;d={'generationRatio':q,'generation4':100*q**4,'totalArea':sum(100*q**j for j in range(1000)),'criticalLengthScale':math.sqrt(1/3)}
  elif f==8:
   x=np.array([-3-v,5+v,2]);mag=np.linalg.norm(x);d={'distance':mag,'unitVector':(x/mag).tolist()}
  elif f==9:d={'pointAt3':[7,v-1,15]}
  elif f==10:d={'meetingTime':3+v,'meetingPoint':[2*(3+v),2+3+v],'speed':math.hypot(2,1)}
  elif f==11:
   b=np.array([12.+v,8.]);u=np.array([-2.,-1.]);sol=optimize.minimize_scalar(lambda t:float((b+t*u)@(b+t*u)),bounds=(0,10),method='bounded',options={'xatol':1e-12});d={'closestTime':sol.x,'minimumDistance':math.sqrt(sol.fun),'minimumSquaredDistance':sol.fun}
  elif f==12:
   a=np.array([2+v,1,3]);b=np.array([1,4,-1]);dot=a@b;angle=math.degrees(math.atan2(np.linalg.norm(np.cross(a,b)),dot));d={'dotProduct':int(dot),'vectorAngleDegrees':angle,'acuteLineAngle':min(angle,180-angle),'scalarProjection':dot/np.linalg.norm(b)}
  elif f==13:
   a=2+v;cross=np.array([3,-3*a,2*a]);d={'crossProduct':cross.tolist(),'triangleArea':np.linalg.norm(cross)/2}
  elif f==14:d={'lambda':2,'mu':3,'intersection':[3+v,4,5]}
  elif f==15:d={'degrees':{'A':3,'B':2,'C':3,'D':2,'E':2},'trailLength':33+6*v}
  elif f==16:
   A=np.array([[0,1,1,0],[1,0,1,1],[1,1,0,1],[0,1,1,0]]);walks=np.array([1,0,0,0]);n=3+v
   for _ in range(n):walks=walks@A
   d={'length2Walks':2,'lengthK':n,'walkCount':int(walks[3])}
  elif f==17:
   nbrs={0:[1,2],1:[0,2,3],2:[0,1,3],3:[1,2]};p=np.array([1.,0,0,0]);n=2+v
   for _ in range(n):p=np.array([sum(p[j]/len(nbrs[j]) for j in nbrs[i]) for i in range(4)])
   d={'steps':n,'probabilityAtD':p[3]}
  elif f in [18,19]:d={'mstCost':14+4*v,**({'discountedCost':11+3*v} if f==18 else {})}
  elif f==20:d={'edgeTotal':37+8*v,'extraDistance':7+2*v,'closedDistance':44+10*v}
  elif f==21:d={'pairingCosts':[9+2*v,15+2*v,12+2*v],'edgeTotal':36+6*v,'minimumClosedLength':45+8*v}
  elif f==22:d={'nearestNeighbourCost':19+4*v,'exactOptimum':19+4*v}
  elif f==23:d={'deletedVertexLowerBound':22+4*v,'optimalTour':22+4*v}
  elif f==24:
   # Enumerate all simple physical paths, independently of the author's Floyd-Warshall method.
   e=[('A','B',4+v),('B','C',3+v),('C','D',5+v),('D','E',4+v),('E','A',6+v),('B','E',2+v)];W={(a,b):c for a,b,c in e};W.update({(b,a):c for a,b,c in e})
   def shortest(a,b):
    values=[]
    for n in range(4):
     for middle in itertools.permutations([x for x in 'ABCDE' if x not in [a,b]],n):
      p=(a,)+middle+(b,)
      if all((x,y) in W for x,y in zip(p,p[1:])):values.append(sum(W[x,y] for x,y in zip(p,p[1:])))
    return min(values)
   tour='ABEDCA';cost=sum(shortest(a,b) for a,b in zip(tour,tour[1:]));best=min(sum(shortest(a,b) for a,b in zip(('A',)+p+('A',),(('A',)+p+('A',))[1:])) for p in itertools.permutations('BCDE'));d={'AC':shortest('A','C'),'AD':shortest('A','D'),'CE':shortest('C','E'),'tourCost':cost,'exactOptimumForAudit':best}
  elif f==25:d={'boundaryX':5+v,'voronoiVertexY':23/8,'vertexDistance':math.hypot(3,7/8)}
 elif topic=='sp':
  if f==1:d={'responseRatePercent':100*(150+10*v)/(240+20*v)}
  elif f==2:
   p=.15+.02*v;mu=-4*p+10*(.5-p);var=p*(-4-mu)**2+.5*mu**2+(.5-p)*(10-mu)**2;d={'expectedPayoff':mu,'variance':var}
  elif f==3:
   n=18+v;p=.12+.01*v;d={'atMost2':bincdf(2,n,p),'exactly1GivenPositive':binpmf(1,n,p)/(1-binpmf(0,n,p))}
  elif f==4:
   mu=75+v;s=8+.5*v;d={'between65and85':normalcdf(85,mu,s)-normalcdf(65,mu,s),'percentile90':quantile(lambda x:normalcdf(x,mu,s),.9,50,120)}
  elif f==5:
   O=np.array([[24+v,36-v,30],[40-v,25+v,25]]);E=np.outer(O.sum(axis=1),O.sum(axis=0))/O.sum();chi=float(sum(((O-E)**2/E).flat));d={'chiSquare':chi,'pValue':math.exp(-chi/2),'df':2,'expected':E.tolist()}
  elif f==6:
   lam=1.5+.05*v;O=np.array([25+v,40,30,25-v]);E=120*np.array([poipmf(0,lam),poipmf(1,lam),poipmf(2,lam),1-poicdf(2,lam)]);chi=float(sum((O-E)**2/E));d={'lambdaEstimate':lam,'expected':E.tolist(),'chiSquare':chi,'pValue':math.exp(-chi/2),'df':2}
  elif f==7:
   n1=14+v;n2=16+v;df=n1+n2-2;pool=((n1-1)*25+(n2-1)*36)/df;t=(4+v)/math.sqrt(pool*(1/n1+1/n2));d={'pooledVariance':pool,'tStatistic':t,'pValue':2*(1-tcdf(abs(t),df)),'df':df}
  elif f==8:
   x=np.arange(6.);y=(8+v)+2*x+.7*x*x+np.array([.2,-.3,.1,.2,-.4,.2]);X=np.column_stack([x*x,x,np.ones(6)]);co=np.linalg.lstsq(X,y,rcond=None)[0];ss=sum((y-X@co)**2);d={'quadraticCoefficients':co.tolist(),'SSE':ss,'R2':1-ss/sum((y-y.mean())**2),'prediction4p5':co@[4.5**2,4.5,1]}
  elif f==9:
   x=np.arange(5.);y=np.array([float(f'{z:.6f}') for z in (12+v)*np.exp(.35*x)+np.array([.2,-.2,.3,-.1,.2])]);sol=optimize.least_squares(lambda c:c[0]*np.exp(c[1]*x)-y,[12+v,.35],xtol=1e-14,ftol=1e-14,gtol=1e-13);a,b=sol.x;X=np.column_stack([x,np.ones(5)]);co=np.linalg.lstsq(X,y,rcond=None)[0];d={'exponentialA':a,'exponentialB':b,'expSSE':sum(sol.fun**2),'linearSSE':sum((y-X@co)**2),'linearSlope':co[0],'linearIntercept':co[1],'doublingTime':math.log(2)/b,'prediction8':a*math.exp(8*b)}
  elif f==10:d={'meanY':(2+v)*(40+v)-5,'varianceY':(2+v)**2*(9+v),'sdY':(2+v)*math.sqrt(9+v)}
  elif f==11:
   mu=26+2*v;d={'meanZ':mu,'varianceZ':40,'probabilityAbove35':1-normalcdf(35,mu,math.sqrt(40))}
  elif f==12:
   se=12/math.sqrt(40+5*v);d={'sampleMeanSD':se,'probabilityMeanAbove55':1-normalcdf(55,52+v,se)}
  elif f==13:
   n=12+v;mean=48+.5*v;s=4+.2*v;t=quantile(lambda x:tcdf(x,n-1),.975);margin=t*s/math.sqrt(n);d={'tCritical':t,'margin':margin,'lower':mean-margin,'upper':mean+margin}
  elif f==14:
   sd=8+v;z=quantile(normalcdf,.975);d={'margin64':z*sd/8,'requiredSampleSize':math.ceil((z*sd/1.5)**2)}
  elif f==15:
   rate=2+.25*v;d={'mean3hours':3*rate,'moreThan7':1-poicdf(7,3*rate),'zeroHalfHour':poipmf(0,rate/2)}
  elif f==16:
   lam=7+.5*v;d={'combinedMean':lam,'combinedSD':math.sqrt(lam),'atMost5':poicdf(5,lam)}
  elif f==17:
   z=2+.3*v;d={'zStatistic':z,'pValue':1-normalcdf(z)}
  elif f==18:
   n=15+v;t=(19.2-.1*v-20)/(1.4/math.sqrt(n));d={'tStatistic':t,'pValue':tcdf(t,n-1),'df':n-1}
  elif f==19:
   xs=[1.2+.15*v,2.1+.15*v,.6+.15*v,1.8+.15*v,2.4+.15*v,1.1+.15*v,.9+.15*v,1.7+.15*v];mean=sum(xs)/8;s=math.sqrt(sum((x-mean)**2 for x in xs)/7);t=mean/(s/math.sqrt(8));d={'meanDifference':mean,'sdDifference':s,'tStatistic':t,'pValue':1-tcdf(t,7)}
  elif f==20:
   n=40+5*v;obs=13+v;k=next(k for k in range(n+1) if 1-bincdf(k-1,n,.2)<.05);d={'pValue':1-bincdf(obs-1,n,.2),'criticalThreshold':k,'actualAlpha':1-bincdf(k-1,n,.2),'betaAt0p35':bincdf(k-1,n,.35)}
  elif f==21:
   lam=6+v;obs=2+v;k=max(k for k in range(30) if poicdf(k,lam)<.05);alt=3+v/2;d={'pValue':poicdf(obs,lam),'criticalMaximum':k,'actualAlpha':poicdf(k,lam),'alternativeMean':alt,'typeII':1-poicdf(k,alt)}
  elif f==22:
   x=np.arange(1.,9.);y=np.array([2.,4.,3.,6.,5.,8.,7.,10.])+np.array([0,v*.2,0,-v*.1,0,v*.1,0,0]);xc=x-x.mean();yc=y-y.mean();r=float(xc@yc)/math.sqrt(float(xc@xc)*float(yc@yc));t=r*math.sqrt(6/(1-r*r));d={'correlation':r,'tStatistic':t,'pValue':2*(1-tcdf(abs(t),6)),'df':6}
  elif f==23:
   se=10/math.sqrt(25+5*v);c=100+quantile(normalcdf,.95)*se;beta=normalcdf(c,104,se);d={'criticalMean':c,'typeIIat104':beta,'powerAt104':1-beta}
  elif f==24:
   a=.8-.02*v;b=.3+.02*v;T=np.array([[a,b],[1-a,1-b]]);x=matrixiterate(T,np.array([1.,0]),5);ss=matrixiterate(T,np.array([1.,0]),1000);d={'twoStep':(T@(T@np.array([1.,0]))).tolist(),'activeAfter5':x[0],'stationaryActive':ss[0]}
  elif f==25:
   e=.02*v;T=np.array([[.6+e,.2,.1],[.3-e,.5,.3],[.1,.3,.6]]);x=matrixiterate(T,np.array([.5,.3,.2]),4);ss=matrixiterate(T,np.array([.5,.3,.2]),1000);d={'stateAfter4':x.tolist(),'stationary':ss.tolist(),'longTermOutput':float(ss@[8,4,1])}
 elif topic=='ca':
  if f==1:
   a=4+v;k=.3+.05*v;fun=lambda x:a*x*mp.exp(-k*x);d={'valueAt2':float(fun(2)),'rateAt2':float(mp.diff(fun,2)),'maximumTime':1/k}
  elif f==2:
   a=10+v;b=2+v;fun=lambda x:a*x/(b+x);der=float(mp.diff(fun,3));d={'derivativeAt3':der,'tangentEstimate3p1':fun(3)+.1*der,'exact3p1':fun(3.1)}
  elif f==3:d={'gradientAt1':float(mp.diff(lambda x:mp.log((2+v)*x*x+1),1))}
  elif f==4:
   r=3+.5*v;rate=2+.2*v;dr=rate/float(mp.diff(lambda x:4*mp.pi*x**3/3,r));d={'radiusRate':dr,'areaRate':float(mp.diff(lambda x:4*mp.pi*x*x,r))*dr}
  elif f==5:
   L=10+v;x=6.;dx=.4+.05*v;fun=lambda x:mp.sqrt(L*L-x*x);y=float(fun(x));dy=float(mp.diff(fun,x))*dx;d={'height':y,'verticalVelocity':dy,'areaRate':float(mp.diff(lambda x:x*fun(x)/2,x))*dx}
  elif f==6:
   a=80+10*v;k=.2+.02*v;fun=lambda t:a*t*math.exp(-k*t);sol=optimize.minimize_scalar(lambda t:-fun(t),bounds=(0,20),method='bounded',options={'xatol':1e-12});d={'optimalTime':sol.x,'maximumRevenue':-sol.fun,'endpoint20':fun(20),'newOptimalTime':1/(1.1*k)}
  elif f==7:
   a=2+v;x=math.sqrt(a);fun=lambda t:t**3-3*a*t;d={'maximumX':-x,'maximumY':fun(-x),'minimumX':x,'minimumY':fun(x)}
  elif f==8:
   a=2+v;d={'accumulation0to2':float(mp.quad(lambda x:a*x/(a*x*x+1),[0,2]))}
  elif f==9:
   a=5+v;b=.5+.1*v;total=float(mp.quad(lambda t:a*mp.cos(b*t),[0,mp.pi/(2*b)]));half=optimize.brentq(lambda t:float(mp.quad(lambda s:a*mp.cos(b*s),[0,t]))-total/2,0,math.pi/(2*b));d={'totalVolume':total,'halfVolumeTime':half}
  elif f==10:
   a=1+.5*v;b=a+1;fun=lambda x:x*x-a*a;d={'signedIntegral':float(mp.quad(fun,[-b,-a,a,b])),'totalArea':float(mp.quad(lambda x:abs(fun(x)),[-b,-a,a,b]))}
  elif f==11:
   a=2+v;vol=float(mp.quad(lambda x:mp.pi*(a+a*a*x),[0,4]));d={'volume':vol,'scaledVolume':vol*1.331}
  elif f==12:
   a=1+.2*v;b=3+.2*v;fun=lambda t:(t-a)*(t-b);d={'displacement':float(mp.quad(fun,[0,a,b,5])),'totalDistance':float(mp.quad(lambda t:abs(fun(t)),[0,a,b,5])),'accelerationAtSecondRest':float(mp.diff(fun,b))}
  elif f==13:
   c=4+v;fun=lambda s:mp.sqrt(c*s+9);speed=float(fun(7));acc=float(fun(7)*mp.diff(fun,7));d={'acceleration':acc,'speedAt7':speed,'timeTo7':float(mp.quad(lambda s:1/fun(s),[0,7]))}
  elif f==14:
   N=150+20*v;k=.12+.02*v;d={'population10':float(mp.odefun(lambda t,y:k*y,0,N)(10)),'doublingTime':math.log(2)/k}
  elif f==15:
   initial=80+5*v;k=.08+.01*v;sol=mp.odefun(lambda t,y:-k*(y-20),0,initial);t=optimize.brentq(lambda t:float(sol(t))-35,0,50);d={'time35':t,'temperatureAt10':float(sol(10))}
  elif f==16:
   inp=12+v;k=.2+.02*v;sol=mp.odefun(lambda t,y:inp-k*y,0,20);d={'equilibrium':inp/k,'massAt5':float(sol(5))}
  elif f==17:d={'initialGradientLow':(.5+.1*v)*2,'initialGradientHigh':-(.5+.1*v)}
  elif f==18:
   k=.6+.1*v;seqs=[];y=2
   for j in range(4):z=y*(1+k/4);seqs.append([j/4,y,k*y,z]);y=z
   exact=float(mp.exp(k)*2);d={'eulerAt1':y,'exactAt1':exact,'signedError':y-exact,'unroundedSteps':seqs}
  elif f==19:
   k=.7+.1*v;coarse=5-4*(1-.5*k)**4;fine=5-4*(1-.25*k)**8;d={'coarse':coarse,'fine':fine,'exact':float(mp.odefun(lambda t,y:k*(5-y),0,1)(2))}
  elif f==20:
   a=.4+.05*v;T=np.eye(2)+.5*np.array([[a,-.2],[.1,-.3]]);x=matrixiterate(T,np.array([20.,10]),2);d={'xAt1':x[0],'yAt1':x[1]}
  elif f==21:
   l=.3+.05*v;A=np.array([[(l-.5)/2,(l+.5)/2],[(l+.5)/2,(l-.5)/2]]);s=linalg.expm(2*A)@np.array([6.,2.]);d={'eigenvalues':[l,-.5],'xAt2':s[0],'yAt2':s[1]}
  elif f==22:d={'initialX':1,'initialY':2,'initialDx':.5+.1*v,'initialDy':-1.6}
  elif f==23:d={'realPart':-(.2+.05*v),'imaginaryMagnitude':1+.2*v,'initialDx':-(.2+.05*v),'initialDy':1+.2*v}
  elif f==24:
   o=1+.2*v;T=np.eye(2)+.1*np.array([[0,1],[-o*o,0]]);s=matrixiterate(T,np.array([1.,0]),3);d={'xAt0p3':s[0],'velocityAt0p3':s[1],'exactXAt0p3':float(mp.cos(.3*o))}
  elif f==25:
   r1=-1-.2*v;r2=-3-.2*v;a=-(r1+r2);b=r1*r2;vel=3*r1-r2;A=np.array([[0,1],[-b,-a]]);s=linalg.expm(A)@np.array([2.,vel]);d={'eigenvalues':[r1,r2],'initialVelocity':vel,'displacementAt1':s[0]}
 return d
def compare(actual,expected,label):
 if isinstance(expected,dict):
  assert actual==expected,(label,actual,expected);return
 if isinstance(expected,list):
  assert np.allclose(actual,expected,atol=2e-7,rtol=2e-7),(label,actual,expected);return
 if isinstance(expected,complex):
  assert abs(expected.imag)<1e-10
  expected=expected.real
 assert math.isclose(float(actual),float(expected),rel_tol=2e-7,abs_tol=2e-7),(label,actual,expected)
for row in rows:
 topic,f=row['family'].split('-');f=int(f);v=row['variant']-1;expect=checks(topic,f,v);assert expect,row['id']
 for key,value in expect.items():compare(row['numericValues'][key],value,row['id']+':'+key)
 results.append({'id':row['id'],'family':row['family'],'numericStatus':'passed','checkedValues':list(expect),'method':'Separate iteration, residual equation, direct probability sum, least-squares system, quadrature or matrix exponential; no generator import'})
out={'records':len(results),'checks':sum(len(r['checkedValues']) for r in results),'status':'passed','rows':results,'bankHashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'content/ib/math-ai-hl').glob('*.json'))}}
(ROOT/'docs/ib-expansion-reviews/ai-hl-numeric-audit.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['rows','bankHashes']}))
