from content_core import *
def make(k):
 R=random.Random(10073+k);m=k%5;j=k//5;out=[]
 def add(*x):out.append(item(10,x[0],k,*x[1:]))
 # Broken skyline leads to polygon perimeter, area, roof changes and rectangles.
 hs=[R.randint(1,6) for _ in range(5+j)];cells={(i,y) for i,h in enumerate(hs) for y in range(h)};n=len(hs);A=sum(hs);walls=hs[0]+hs[-1]+sum(abs(x-y) for x,y in zip(hs,hs[1:]));P=2*n+walls
 rect=sum(min(hs[a:b+1]) for a in range(n) for b in range(a,n));big=max((b-a+1)*min(hs[a:b+1]) for a in range(n) for b in range(a,n))
 valid=[(a,b,c) for a in range(n) for b in range(a,n) for c in range(1,max(hs)+1) if all((x,c-1) in cells for x in range(a,b+1))];ask=['the perimeter of the union','the total length of vertical exterior edges','the number of axis-parallel rectangles with integer vertices, positive area, bottom side on the baseline, and wholly inside the skyline','the largest possible area of an axis-parallel rectangle with integer vertices and bottom on the baseline inside the skyline','the area of the missing part of the smallest enclosing rectangle with sides parallel to the grid'][m]
 v=[P,walls,rect,big,n*max(hs)-A][m];chk=[sum((x+u,y+w) not in cells for x,y in cells for u,w in [(1,0),(-1,0),(0,1),(0,-1)]),sum((x+u,y) not in cells for x,y in cells for u in [-1,1]),len(valid),max((b-a+1)*c for a,b,c in valid),sum((x,y) not in cells for x in range(n) for y in range(max(hs)))][m]
 exp=[f'Top and bottom contribute {2*n}. The two end heights and the absolute adjacent height changes total {walls}.',f'The visible vertical pieces are the two ends and the steps between neighbours: {hs[0]} + {hs[-1]} + '+ ' + '.join(str(abs(a-b)) for a,b in zip(hs,hs[1:]))+'.',f'Fix the consecutive column interval. Its minimum height counts the possible tops. Summing by leftmost column gives {join(sum(min(hs[a:b+1]) for b in range(a,n)) for a in range(n))}.',f'For each left column, maximise width times the minimum height up to the right column. The best areas with those left endpoints are {join(max((b-a+1)*min(hs[a:b+1]) for b in range(a,n)) for a in range(n))}.',f'The bounding box has area {n} × {max(hs)}. The columns themselves total {A}.'][m]
 add('roofline',GEO,'Coordinate geometry and dissection',2+m//2,f'Consecutive unit-width columns stand on one horizontal baseline. From left to right their heights are {join(hs)}. What is {ask}?',v,chk,exp+f' The result is {v}.',[A,P,walls,big],square_art({(x,max(hs)-1-y) for x,y in cells}))
 # Routes on a grid with a chosen forbidden arrangement, parity or joint waypoint condition.
 W,H=R.choice([(4,4),(5,3),(5,4),(6,4)]);inner=[(x,y) for x in range(1,W) for y in range(1,H)];S=sorted(R.sample(inner,2+j));paths=[]
 for east in combinations(range(W+H),W):
  p={(0,0)};x=y=0
  for t in range(W+H):
   if t in east:x+=1
   else:y+=1
   p.add((x,y))
  paths.append(p)
 f=[lambda n:n==0,lambda n:n==1,lambda n:n>=1,lambda n:n%2==0,lambda n:n==2][m]; ways=collections.Counter(len(set(S)&p) for p in paths);v=sum(c for n,c in ways.items() if f(n))
 grid={(0,0):[1]+[0]*len(S)}
 for x in range(W+1):
  for y in range(H+1):
   if not(x or y):continue
   old=[sum(grid.get(t,[0]*(len(S)+1))[i] for t in [(x-1,y),(x,y-1)]) for i in range(len(S)+1)];grid[x,y]=([0]+old[:-1]) if (x,y) in S else old
 counts=grid[W,H];ask=['none','exactly one','at least one','an even number (possibly zero)','exactly two'][m]
 add('marked-crossings',CNT,'Lattice paths and states',3,f'A courier moves from (0,0) to ({W},{H}) in unit steps north or east. The marked intersections are {join(S)}. How many routes visit {ask} of the marked intersections?',v,sum(x for i,x in enumerate(counts) if f(i)),f'At each point keep counts for 0, 1, … marked visits. Add the arrays from west and south; at a marked point shift all counts up one place. Starting with one route at (0,0), the destination array is [{join(counts)}]. Select the entries for {ask}, giving {v}.',[sum(counts),counts[0],counts[1]])
 # Subsets of divisors: exponents with inequality/dependency; confirm using exact divisors.
 a,b,c=[R.randint(1,4) for _ in range(3)];p,q,r=R.sample([2,3,5,7],3);N=p**a*q**b*r**c
 def rule(i,jj,h):return [i==jj,jj<h,(i+jj+h)%2==0,i>=1 and jj!=h,i+jj==h][m] and [True,i+jj+h>=3,(i==0 or h==0)][j]
 ds=[p**i*q**jj*r**h for i in range(a+1) for jj in range(b+1) for h in range(c+1) if rule(i,jj,h)];by=[sum(rule(i,jj,h) for jj in range(b+1) for h in range(c+1)) for i in range(a+1)]
 def vpow(d,prime):
  z=0
  while d%prime==0:d//=prime;z+=1
  return z
 divs={d for h in range(1,math.isqrt(N)+1) if N%h==0 for d in [h,N//h]};ck=sum(rule(*(vpow(d,z) for z in [p,q,r])) for d in divs);pred=['u = v','v < w','u + v + w is even','u is positive and v ≠ w','u + v = w'][m]
 add('divisor-lock',NT,'Divisor exponents',3,f'A lock accepts positive divisors of {p}^{a} · {q}^{b} · {r}^{c}. Write a divisor as {p}^u · {q}^v · {r}^w. How many accepted divisors satisfy {pred}{["",", with at least three prime factors counted with multiplicity",f", without being divisible by both {p} and {r}"][j]}?',len(ds),ck,f'Unique factorisation gives 0 ≤ u ≤ {a}, 0 ≤ v ≤ {b}, 0 ≤ w ≤ {c}. For u = 0 through {a}, enumerate v and count w meeting {pred}. The counts {join(by)} add to {len(ds)}.',[(a+1)*(b+1)*(c+1),len(ds)+a,len(ds)-1])
 # Absolute-value landscape. Weights and spacings vary and targeting different features changes the method.
 pts=sorted(R.sample(range(-6,10),3+j));weights=[R.choice([1,1,2,3]) for _ in pts];L=pts[0]-3;U=pts[-1]+4;fn=lambda x:sum(w*abs(x-a) for a,w in zip(pts,weights));tab={x:fn(x) for x in range(L,U+1)};lo=min(tab.values());T=R.choice(sorted(set(tab.values())));mns=[x for x,vv in tab.items() if vv==lo];slope=-sum(weights);cur=fn(L);tab2={L:cur}
 for x in range(L,U):
  if x in pts:slope+=2*weights[pts.index(x)]
  cur+=slope;tab2[x+1]=cur
 agg=lambda d:[min(d.values()),sum(v==min(d.values()) for v in d.values()),sum(v==T for v in d.values()),sum(v<=T for v in d.values()),max(d.values())-min(d.values())][m]
 expr=' + '.join(f'{w}|x − ({a})|' for a,w in zip(pts,weights));ask=['the minimum of F','the number of minimising integers',f'the number of solutions to F(x) = {T}',f'the number of integers with F(x) ≤ {T}','the range (maximum minus minimum) of F'][m];v=agg(tab)
 add('weighted-stations',ALG,'Piecewise linear functions',3,f'For integers {L} ≤ x ≤ {U}, let F(x) = {expr}. What is {ask}?',v,agg(tab2),f'At x = {L} the value is {tab[L]}. Moving one unit right changes the value by (weight at or left of x) minus (weight to the right). Thus the slope increases by twice a station’s weight as it is crossed. In increasing x order the values are {join(tab.values())}. Reading the requested statistic gives {v}.',[lo,len(mns),T,U-L+1])
 # Short constrained words, inclusion/complement and transitions.
 letters=('A','B','C');n=5+j;bad=R.choice(['AA','AB','BC','CC','BA']);chosen=R.choice(letters);pred=[lambda s:s.count(chosen)==2,lambda s:s[0]==s[-1],lambda s:len(set(s))==3,lambda s:s.count(chosen)%2==1,lambda s:s[0]!=s[-1] and chosen in s][m]
 words=[''.join(w) for w in product(letters,repeat=n)];extra=lambda s:[True,s[0]!=chosen,s[-1]!=chosen][j];acc=[s for s in words if bad not in s and pred(s) and extra(s)]
 @lru_cache(None)
 def rec(i,prev,first,num,mask):
  if i==n:return int([num==2,prev==first,mask==7,num%2==1,prev!=first and num>0][m] and [True,first!=chosen,prev!=chosen][j])
  return sum(rec(i+1,c,first or c,num+(c==chosen),mask|1<<letters.index(c)) for c in letters if prev+c!=bad)
 by=[sum(s[0]==x for s in acc) for x in letters];ask=[f'use {chosen} exactly twice','have equal first and last letters','use all three letters',f'use {chosen} an odd number of times',f'have different end letters and use {chosen} at least once'][m]
 add('signal-book',CNT,'Restricted strings',4,f'An antenna transmits a string of {n} letters chosen from A, B and C. The adjacent pair {bad} is forbidden. '+(['',f'The first letter cannot be {chosen}. ',f'The last letter cannot be {chosen}. '][j])+f'How many transmissions {ask}?',len(acc),rec(0,'','',0,0),f'Build one letter at a time. Retain the first and last letters, the number of {chosen} letters, and the set of letters used. From each state append A, B or C except a letter forming {bad}; sum states that {ask}. The counts by initial A, B, C are {join(by)}; their sum is {len(acc)}.',[3**n,3**(n-1),len(acc)+sum(by[:1])])
 # Progressive instalment schedules with irregular gaps and precise percentages.
 deposit=R.choice([1600,2000,2400]);rates=R.sample([F(1,4),F(1,5),F(1,10),F(1,8),F(1,2)],3);fees=R.sample([12,16,20,24,32],3);ops=R.sample(['charge','rebate','bonus'],3)
 def step(x,t,f,h):return {'charge':x*(1-f)-h,'rebate':(x-h)*(1+f),'bonus':x*(1+f)+h}[t]
 desc=lambda t,f,h:{'charge':f'deduct {100*f}% of the balance, then deduct {h}','rebate':f'deduct {h}, then increase the remainder by {100*f}%','bonus':f'increase the balance by {100*f}%, then add {h}'}[t]
 vals=[F(deposit)];forms=[(F(1),F(0))]
 for t,f,h in zip(ops,rates,fees):
  vals.append(step(vals[-1],t,f,h));a0,b0=forms[-1];v0=step(0,t,f,h);a1=step(1,t,f,h)-v0;forms.append((a1*a0,a1*b0+v0))
 if m==0:what='What is the final balance?';prefix=f'The starting balance is {deposit}.';ans=vals[3];ck=forms[-1][0]*deposit+forms[-1][1]
 elif m==1:what='What was the starting balance?';prefix=f'The final balance is {fmt(vals[-1])}.';ans=F(deposit);ck=(vals[-1]-forms[-1][1])/forms[-1][0]
 elif m==2:what='What is the absolute change between the starting and ending balances?';prefix=f'The starting balance is {deposit}.';ans=abs(vals[3]-deposit);ck=abs((forms[3][0]-1)*deposit+forms[3][1])
 elif m==3:what='What was the balance immediately after the first step?';prefix=(f'The final balance is {fmt(vals[3])}.' if j!=2 else f'After all three steps, the balance is shared equally between two accounts. One account receives {fmt(vals[3]/2)}.');ans=vals[1];ck=forms[1][0]*((vals[-1]-forms[-1][1])/forms[-1][0])+forms[1][1]
 else:what='By how much would the ending balance increase if the starting balance increased by 80?';prefix='';ans=80*forms[-1][0];v2=F(deposit+80)
 if m==4:
  for t,f,h in zip(ops,rates,fees):v2=step(v2,t,f,h)
  ck=v2-vals[-1]
 sol=f'If the initial balance is x, the three ending balances have coefficients (multiplier, constant) {join((fmt(a),fmt(b)) for a,b in forms[1:])}. Multiply before adding a fixed charge unless the step says otherwise. '+(f'Working forwards or solving the last linear expression, the four balances are {join(vals)}. ' if m!=4 else f'Fixed additions cancel in a difference, so multiply 80 by {fmt(forms[3][0])}. ')+f'The requested value is {fmt(ans)}.'
 add('ledger-machine',AR,'Successive percentage changes',2,f'A theatre keeps exact fractional credits. {prefix} Its three steps in order are: '+'; '.join(desc(t,f,h) for t,f,h in zip(ops,rates,fees))+'. '+what,ans,ck,sol,[vals[1],vals[2],abs(vals[3]-vals[2]),deposit])
 # Rational probability of two irregular dice under conditioning, independent count by convolution.
 A=R.sample(range(1,12),5);B=R.sample(range(1,12),4+j);q0=R.choice([9,10,11,12,13]);D=lambda a,b:[a+b>=q0,a%2!=b%2,b>=a,abs(a-b)<=4,(a*b)%3==0][m];event=lambda a,b:[a>b,a+b>=q0,(a+b)%2==0,a*b%2==0,a<b][m];pairs=list(product(A,B));den=sum(D(a,b) for a,b in pairs);num=sum(D(a,b) and event(a,b) for a,b in pairs);bys=[(sum(D(a,b) and event(a,b) for b in B),sum(D(a,b) for b in B)) for a in A];pred=[f'the sum is at least {q0}','the labels have opposite parity','the second label is at least the first','the labels differ by at most four','the product is divisible by three'][m];target=['the first label is larger',f'the sum is at least {q0}','the sum is even','the product is even','the second label is larger'][m]
 ck=F(sum(sum(D(a,b) and event(a,b) for a in A) for b in B),sum(sum(D(a,b) for a in A) for b in B))
 add('conditioned-spinners',PRO,'Conditional sample spaces',3,f'Two independent fair spinners have equally sized sectors labelled respectively [{join(A)}] and [{join(B)}]. Given that {pred}, what is the probability that {target}?',F(num,den),ck,f'All ordered sector pairs start equally likely. For first labels in the order listed, the (successful, eligible) counts are {join(bys)}. Add the numerators and denominators separately: {num}/{den} = {F(num,den)}.',[F(num,len(pairs)),F(den-num,den),F(1,2),F(1,3)])
 # Modular rings with different allowed residues; time overlap or exact one cycle.
 p,q=R.sample([4,5,6,7,8,9],2);A=set(R.sample(range(p),1+j));B=set(R.sample(range(q),2));L=math.lcm(p,q);stop=L*(1+j)+R.randrange(3,L);f=lambda a,b:[a and b,a!=b,a or b,a and not b,b and not a][m];s=[n for n in range(L) if f(n%p in A,n%q in B)];full,tail=divmod(stop,L);ans=full*len(s)+sum(x<tail for x in s);ck=sum(f(n%p in A,n%q in B) for n in range(stop));cond=['both are lit','exactly one is lit','at least one is lit','only amber is lit','only green is lit'][m]
 add('residue-beacons',NT,'Overlapping residue classes',3,f'At integer times 0 through {stop-1}, amber lights when the time modulo {p} is in {{{join(sorted(A))}}}, and green lights when the time modulo {q} is in {{{join(sorted(B))}}}. At how many times is this true: {cond}?',ans,ck,f'The complete pattern repeats after lcm({p},{q}) = {L}. Within one cycle the qualifying residues are {join(s) or "none"}. There are {full} whole cycles and a tail of length {tail}, giving {full} × {len(s)} + {sum(x<tail for x in s)} = {ans}.',[stop-ans,len(s),full*len(s)])
 # Quadratic with known integer roots: a sign diagram and bounded integer cases.
 roots=sorted(R.sample(range(-7,9),3));a,b,c=roots;lo=a-3;hi=c+3;sig=R.choice([-1,1]); exps=[(1,1,1),(2,1,1),(1,2,2)][j];f=lambda x:sig*(x-a)**exps[0]*(x-b)**exps[1]*(x-c)**exps[2];cond=[lambda v:v>=0,lambda v:v<0,lambda v:v==0,lambda v:v>0,lambda v:v<=0][m];sign=['≥','<','=','>','≤'][m];chosen=[x for x in range(lo,hi+1) if cond(f(x))];chunks=[(lo,a-1),(a,a),(a+1,b-1),(b,b),(b+1,c-1),(c,c),(c+1,hi)];good=[(u,vv) for u,vv in chunks if u<=vv and cond(f(u))];v=sum(vv-u+1 for u,vv in good)
 # For the zero-set ask for an aggregate rather than a trivial constant.
 if m==2: v=sum(x*x for x in roots);chk=sum(x*x for x in chosen);ask='What is the sum of the squares of all solutions?'
 else:chk=len(chosen);ask='How many integer solutions are there?'
 add('sign-lanterns',ALG,'Integer polynomial inequalities',3,(['All factors below are simple. ','The first root has even multiplicity. ','Only the first root has odd multiplicity. '][j])+f'An integer x is restricted to [{lo},{hi}] and satisfies {sig}(x − ({a}))^{exps[0]}(x − ({b}))^{exps[1]}(x − ({c}))^{exps[2]} {sign} 0. '+ask,v,chk,f'The sign can change only at {join(roots)}. It changes at roots of odd multiplicity only and is zero at each root. Intersect the qualifying pieces with the integer domain: {join(chosen) or "no values"}. '+(f'Squaring and adding gives {v}.' if m==2 else f'Counting gives {v}.'),[hi-lo+1,len(chosen),sum(abs(x) for x in roots)])
 # Area and boundary of nonrectangular lattice triangles; determinants vs shoelace.
 A=(R.randrange(-4,1),R.randrange(-2,2));B=(R.randrange(4,9),R.randrange(0,4));C=(R.randrange(-1,4),R.randrange(5,10));pts=[A,B,C]
 cross=lambda u,v:u[0]*v[1]-u[1]*v[0];sub=lambda u,v:(u[0]-v[0],u[1]-v[1]);D=abs(cross(sub(B,A),sub(C,A)));bd=sum(math.gcd(abs(x),abs(y)) for x,y in [sub(B,A),sub(C,B),sub(A,C)]);I=(D-bd+2)//2
 def inside(P):
  vals=[cross(sub(v,u),sub(P,u)) for u,v in zip(pts,pts[1:]+pts[:1])];return 0 if min(vals)<0<max(vals) else (1 if 0 in vals else 2)
 result=collections.Counter(inside((x,y)) for x in range(min(p[0] for p in pts),max(p[0] for p in pts)+1) for y in range(min(p[1] for p in pts),max(p[1] for p in pts)+1));D2=abs(sum(cross(u,v) for u,v in zip(pts,pts[1:]+pts[:1])))
 asks=['twice the area','the number of lattice points on its boundary, counting vertices only once','the number of lattice points strictly inside it','the total number of lattice points on or inside it','the sum of the three triangle areas formed by joining any one interior point to its vertices'][m];ans=[D,bd,I,I+bd,F(D,2)][m];chk=[D2,result[1],result[2],result[1]+result[2],F(D2,2)][m]
 exp=f'The vertices are {A}, {B}, {C}. The determinant of B−A and C−A has absolute value {D}, twice the area. '+(f'Each edge contributes gcd(|Δx|,|Δy|) boundary points when its last endpoint is excluded. This totals {bd}. ' if m in(1,2,3) else '')+(f'Pick’s formula gives interior = (twice area − boundary + 2)/2 = {I}. ' if m in(2,3) else '')+('The three pieces partition exactly the original triangle. ' if m==4 else '')+f'The requested quantity is {fmt(ans)}.'
 add('survey-triangle',GEO,'Lattice coordinates',3,([f'A triangle has vertices A{A}, B{B} and C{C} on the unit coordinate grid.',f'Starting at A{A}, a surveyor walks by the vector {sub(B,A)} to B and then {sub(C,B)} to C, before closing the triangle.',f'A survey plot has A{A}, B{B}. Its third vertex is the reflection of ({-C[0]}, {C[1]}) across the y-axis.'][j])+f' What is {asks}?',ans,chk,exp,[D,F(D,2),bd,I,I+bd])
 return out
