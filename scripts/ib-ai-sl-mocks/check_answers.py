"""Independent course-content spot calculations covering every numbered question."""
from pathlib import Path
from statistics import NormalDist,linear_regression,correlation
from math import *
import json,re
r=Path(__file__).resolve().parents[2];d=r/'content/ib/ai-sl-mocks-2026/papers'
seen=set();nchecks=0
def check(k,n,part,*terms):
 global nchecks
 p=json.loads((d/('ai-sl-set-'+k[0]+'-paper-'+k[1]+'.json')).read_text(encoding='utf8'))
 q=p['questions'][n-1];s=' '.join(v['text'] for v in q['markScheme'][ord(part)-97]['steps']).replace('−','-').replace(' ','')
 for word in terms:
  if isinstance(word,float) and word.is_integer():word=int(word)
  assert str(word).replace(' ','').replace('−','-') in s,(k,n,part,word,s)
  nchecks+=1
 seen.add((k,n))
sf=lambda x:format(x,'.3g')
def pmt(p,rate,n):
 lo,hi=0,p
 for _ in range(90):
  mid=(lo+hi)/2;bal=p
  for i in range(n):bal=bal*(1+rate)-mid
  if bal>0:lo=mid
  else:hi=mid
 return (lo+hi)/2
def bi(n,p,k):return comb(n,k)*p**k*(1-p)**(n-k)
def clock(h):m=round(60*h)+360;return f'{m//60:02d}:{m%60:02d}'
def bisect(f,a,b):
 for _ in range(72):
  c=(a+b)/2
  if f(a)*f(c)<=0:b=c
  else:a=c
 return (a+b)/2
def normcdf(x):return .5*erfc(-x/sqrt(2))
check('a1',1,'b',round(1.235*.855,6),'No guarantee');check('a1',2,'b',sum(range(160,257,12)),sum(range(160,269,12)),'Week 10')
check('a1',3,'b',round((4.3-3.4)/.2,2));check('a1',4,'b',round(pi*7.5**2*128/360*3,3));check('a1',5,'a',17+1.5*(17-13),'outlier');check('a1',6,'b','12/21','4/7')
x=list(range(2,8));y=[4,5,7,8,11,13];a,b=linear_regression(x,y);check('a1',7,'a',sf(a),sf(b),sf(correlation(x,y)));check('a1',7,'b',sf(8-a*5-b))
check('a1',8,'a',sf(bi(18,.12,2)));check('a1',8,'b',sf(sum(bi(18,.12,k) for k in range(3,19))))
check('a1',9,'b','PA² = 10','PB² = 18','PC² = 5');check('a1',10,'b',24+12*4-1.5*16,'positive before 4')
l=pmt(9600,.005,36);check('a1',11,'a',f'{l:.2f}');check('a1',11,'b',round(36*l-9600));check('a1',12,'a',sum(a+b for a,b in zip([18,25,29,26],[25,29,26,20])));check('a1',12,'b',sf(600/198))
check('b1',1,'b',ceil((7.2e9*.84)/3e6));check('b1',2,'b',sf(84*.93**5),sf(84*.93**6))
buoy=hypot(2.8*sin(radians(40))-4.1*sin(radians(105)),2.8*cos(radians(40))-4.1*cos(radians(105)));check('b1',3,'a',sf(buoy));check('b1',3,'b',sf(5*buoy))
check('b1',4,'a',f'{sum(i*j for i,j in zip([1,3,6,10],[6,14,12,8]))/40:.2f}')
jt=bisect(lambda t:.8+6*t-4.9*t*t,1,2);check('b1',5,'b',sf(jt))
check('b1',6,'a',sf(normcdf((500-506)/3.8)));check('b1',6,'b',sf(bisect(lambda v:normcdf((v-506)/3.8)-.95,500,520)))
check('b1',7,'a',round(correlation([1,2,3,4,5],[2,4,1,3,5]),4))
vol=pi*1.6**2*11*.85;check('b1',8,'b',f'{vol*25:.2f}',ceil(1880/vol));check('b1',9,'b',sf(2*sqrt(8)),sf(sqrt(20)))
check('b1',10,'b',int((4-5*.3)/.1));check('b1',11,'b',18+8*2.5-2.5**2,'0.25');check('b1',12,'b','Reject H0 at 5%','At 1% do not reject H0')
lo=pmt(12000,.004,36);rent=sum(290*1.01**i for i in range(36));check('a2',1,'a',f'{lo:.2f}',round(36*lo));check('a2',1,'b',round(rent));check('a2',1,'d',round(36*lo-rent),round(rent-(36*lo-1050)))
tide=lambda t:3.6+1.4*cos(radians(30*t));cross=bisect(lambda x:tide(x)-3,0,6);check('a2',2,'b',clock(cross),clock(12-cross));check('a2',2,'e',clock(bisect(lambda x:tide(x)-3.2,0,6)-.75))
rows=[[46,24,10],[30,32,18]];chi=sum((rows[i][j]-t/2)**2/(t/2) for j,t in enumerate(map(sum,zip(*rows))) for i in range(2));check('a2',3,'c',sf(chi),sf(exp(-chi/2)));check('a2',3,'d','0.575','0.375')
v=lambda x:x*(30-2*x)*(24-2*x);u=bisect(lambda x:(v(x+.00001)-v(x-.00001)),4,5);check('a2',4,'c',f'{v(u):.2f}');check('a2',4,'d',sf(v(u)-v(4.5)));assert ceil(12000/(v(4.5)*.94))==10;check('a2',4,'e','Ten trays')
x=[20,30,40,50,60];y=[9,17,28,40,56];m,b=linear_regression(x,y);check('b2',1,'a',sf(m),sf(abs(b)),sf(correlation(x,y)));check('b2',1,'d',sf(bisect(lambda x:.2*x+.012*x*x-43,0,100)))
check('b2',2,'d',4-sqrt(1.25**2-1),4+sqrt(1.25**2-1));check('b2',2,'e','PB² = 18','PC² = 18','PD² = 5')
p=normcdf(-4/2.8);check('b2',3,'a',sf(p),sf(16*p));check('b2',3,'b',sf(sum(bi(16,p,k) for k in range(2,17))));check('b2',3,'d',floor(log(.7)/log(.98)))
# Simpson's rule is exact for the quadratic; independent of the published antiderivative.
powr=lambda t:2+1.2*t-.2*t*t
energy=lambda a,b:(b-a)*(powr(a)+4*powr((a+b)/2)+powr(b))/6
check('b2',4,'b',round(energy(0,6),2));check('b2',4,'d',round(.28*energy(0,2)+.42*energy(2,6),2));check('b2',4,'e',round(sum(19.2-.08*i for i in range(30)),2))
assert len(seen)==32;print('Passed',nchecks,'independent key checks across',len(seen),'questions.')
