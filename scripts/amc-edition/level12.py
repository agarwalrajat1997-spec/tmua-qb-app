from content_core import *
from cmath import exp,pi
def make(k):
 R=random.Random(12007+k);m=k%5;j=k//5;out=[]
 def add(*x):out.append(item(12,x[0],k,*x[1:]))
 # Roots of unity on a changing selection of arcs of a regular polygon.
 n=R.choice([8,10,12,15,18]);D=R.sample(range(1,n),3+j);A=sorted({x for d in D for x in (d,(-d)%n)});r=R.choice(range(n));z=exp(2j*pi/n)
 def eligible(a,b):return [True,a!=b,a!=b and (a+b)%n!=0][j] and [((a+b)%n==r),((a-b)%n==r),(2*a+b)%n==r,(a+2*b)%n==r,(a+b)%n in {0,r}][m]
 Z=lambda a,b:[z**(a+b),z**(a-b),z**(2*a+b),z**(a+2*b),z**(a+b)][m]
 v=sum(eligible(a,b) for a,b in product(A,repeat=2));ck=sum(any(abs(Z(a,b)-z**q)<1e-7 for q in ([0,r] if m==4 else [r])) for a,b in product(A,repeat=2) if [True,a!=b,abs(z**a-z**(-b))>1e-7 and a!=b][j]);what=[f'xy = ζ^{r}',f'x/y = ζ^{r}',f'x²y = ζ^{r}',f'xy² = ζ^{r}',f'xy is either 1 or ζ^{r}'][m];counts=[sum(eligible(a,b) for b in A) for a in A]
 add('phase-wheel',ALG,'Roots of unity',4,f'Let ζ = exp(2πi/{n}). A switch can show any power ζ^a for a in {{{join(A)}}}. Settings are ordered. '+(['The two switches may show the same value. ','The two switches must show different values. ','The two values must neither be equal nor be complex conjugates. '][j])+f'How many settings (x,y) satisfy {what}?',v,ck,f'Powers of ζ agree exactly when their exponents agree modulo {n}. For each first exponent in the order given, count second exponents giving the required residue of '+['a+b','a−b','2a+b','a+2b','a+b'][m]+f'. The counts are {join(counts)}, for {v} ordered settings.',[len(A),len(A)**2,v*2])
 # Trace sequences for quadratics. Independent integer-matrix exponentiation, never use key.
 u,v=R.sample(range(1,6+j),2);sign=R.choice([-1,1]);v*=sign;s=u+v;p=u*v;h=R.randrange(3,7);seq=[2,s]
 for _ in range(h+2):seq.append(s*seq[-1]-p*seq[-2])
 values=[u**h+v**h,(u**h-v**h)**2,(u**(h+1)+v**(h+1))*(u**(h-1)+v**(h-1)),(u**h+v**h)**2,(u**(h+2)+v**(h+2))-p*(u**h+v**h)]
 a=abs(values[m]);checks=[seq[h],seq[h]**2-4*p**h,seq[h+1]*seq[h-1],seq[2*h] if False else seq[h]**2,seq[h+2]-p*seq[h]];required=[f'|α^{h}+β^{h}|',f'(α^{h}−β^{h})²',f'|(α^{h+1}+β^{h+1})(α^{h-1}+β^{h-1})|',f'(α^{h}+β^{h})²',f'|(α^{h+2}+β^{h+2})−({p})(α^{h}+β^{h})|'][m]
 add('quadratic-echoes',SEQ,'Symmetric power sums',3,[f'The roots of t² − ({s})t + ({p}) = 0 are α and β.',f'Numbers α and β have sum {s} and square sum {s*s-2*p}.',f'The monic quadratic with roots α, β has f(0)={p} and f(1)={1-s+p}.'][j]+f' Compute {required}.',a,abs(checks[m]),(['',f'From (α+β)²−(α²+β²)=2αβ, their product is {p}. ',f'Writing f(t)=t²−St+P, f(0) gives P and f(1)=1−S+P gives S. '][j])+f'By Vieta, α+β={s} and αβ={p}. Set S₀=2, S₁={s}; multiplying the root equation gives Sₙ=({s})Sₙ₋₁−({p})Sₙ₋₂. Up to S{h+2} the values are {join(seq[:h+3])}. '+[f'Take |S{h}|.',f'Use S{h}²−4({p})^{h}.',f'Multiply S{h+1} and S{h-1} and take the absolute value.',f'Square S{h}.',f'Take |S{h+2}−({p})S{h}|.'][m]+f' This gives {a}.',[abs(seq[h]),abs(seq[h-1]),abs(seq[h+1]),a+abs(p)])
 # Logarithmic strips expressed with variable bases, verified by integer-only exponent inequalities.
 base=R.choice([2,3,5]);e1=R.randint(1,3);e2=e1+R.randint(1,2);top=R.randint(25,50);offset=R.randint(1,6);mult=R.choice([2,3,4]);man=lambda x:next(i for i in range(12) if base**(i+1)>x);lamb=[lambda a,b:a==b,lambda a,b:a+b==3,lambda a,b:b-a==1,lambda a,b:(a+b)%2==0,lambda a,b:b==2*a][m];ask=['A = B','A + B = 3','B − A = 1','A + B is even','B = 2A'][m]
 by=collections.Counter()
 for a0,b0 in product(range(9),repeat=2):
  if not lamb(a0,b0):continue
  low=max(1,base**a0-offset,(base**b0+mult-1)//mult);hi=min(top,base**(a0+1)-1-offset,(base**(b0+1)-1)//mult);by[a0]+=sum(1 for x in range(low,hi+1) if [True,x%2==1,math.gcd(x,6)==1][j])
 val=sum(by.values());chk=sum(lamb(man(x+offset),man(mult*x)) and [True,x%2==1,math.gcd(x,6)==1][j] for x in range(1,top+1))
 add('log-windows',ALG,'Logarithms and integer intervals',4,f'For integers 1 ≤ x ≤ {top}, set A = ⌊log base {base} of (x + {offset})⌋ and B = ⌊log base {base} of ({mult}x)⌋. How many {["integers","odd integers","integers relatively prime to 6"][j]} x satisfy {ask}?',val,chk,f'To have (A,B)=(a,b) requires {base}^a ≤ x+{offset} < {base}^(a+1) and {base}^b ≤ {mult}x < {base}^(b+1). Intersect those intervals with 1 ≤ x ≤ {top} for each allowed pair. The nonzero counts grouped by a are '+(', '.join(f'a={a}: {v}' for a,v in by.items() if v) or 'none')+f'. Their sum is {val}.',[top-val,top//2,val*2])
 # Trigonometric intersections on half-open intervals; use congruences, cross-check independent numeric roots on exact rational grid.
 a,b=R.sample(range(1,8),2);shift=R.choice([F(1,6),F(1,4),F(1,3),F(1,2)]);T=j+1
 # sin(a θ) = sin(b θ + shift π) or cos, sign flips, etc. Coordinates measured in units of π.
 kind=[('sin','sin',1),('cos','cos',1),('sin','cos',1),('sin','sin',-1),('cos','cos',-1)][m];fl,fr,sg=kind
 # Convert both sides to sine, taking account of minus signs by adding π.
 cL=F(1,2) if fl=='cos' else F(0);cR=shift+(F(1,2) if fr=='cos' else 0)+(1 if sg==-1 else 0)
 roots=set();parts=[]
 for coef,off in [(a-b,cR-cL),(a+b,1-cL-cR)]:
  s={F(off+2*t,coef) for t in range(-80,81) if 0<=F(off+2*t,coef)<2*T and [True,F(off+2*t,coef)%2<1,F(off+2*t,coef)%1!=0][j]};roots|=s;parts.append(len(s))
 den=math.lcm(4*shift.denominator*abs(a-b),4*shift.denominator*(a+b));fn1=getattr(math,fl);fn2=getattr(math,fr);ck=sum(abs(fn1(a*math.pi*h/den)-sg*fn2(math.pi*(b*h/den+float(shift))))<1e-8 for h in range(2*T*den) if [True,F(h,den)%2<1,F(h,den)%1!=0][j]);v=len(roots)
 add('wave-intersections',TRIG,'Trigonometric equations',4,f'How many distinct real angles θ in 0 ≤ θ < {2*T}π {["","and sin θ ≥ 0, excluding odd multiples of π,","that are not integer multiples of π"][j]} satisfy {fl}({a}θ) = '+('−' if sg==-1 else '')+f'{fr}({b}θ + {fmt(shift)}π)?',v,ck,f'Write both sides as sine: cos t = sin(t+π/2), and −sin t = sin(t+π). In units x=θ/π the phase offsets are {cL} and {cR}. Equal sines have equal arguments modulo 2π or supplementary arguments modulo 2π. Thus ({a-b})x = {cR-cL} + 2n or ({a+b})x = {1-cL-cR} + 2n. In the stated interval these yield {parts[0]} and {parts[1]} values; {sum(parts)-v} occur in both. The count is {v}.',[sum(parts),parts[0],parts[1],v*2])
 # Polynomial coefficients from distinguishable physical choices, independent convolution / exhaustive combinations.
 groups=[(R.randint(1,4), R.randint(1,3)) for _ in range(3+j)];sumw=sum(a*b for a,b in groups);t=R.randint(3,max(4,sumw-2));degs=[a for a,b in groups for _ in range(b)];hist=[1]
 for a,b in groups:
  h=[0]*(len(hist)+a*b)
  for i,x in enumerate(hist):
   for u in range(b+1):h[i+a*u]+=x*math.comb(b,u)
  hist=h
 mods=R.choice([3,4,5]);res=t%mods;pred=[lambda s:s==t,lambda s:s<=t,lambda s:s%mods==res,lambda s:t-1<=s<=t+1,lambda s:s>=sumw-t][m];ans=sum(num for s,num in enumerate(hist) if pred(s));G=collections.Counter({0:1})
 for d in degs:
  old=G.copy()
  for s,c in old.items():G[s+d]+=c
 ck=sum(v for s,v in G.items() if pred(s));ask=[f'the coefficient of x^{t}',f'the sum of all coefficients through degree {t}',f'the sum of coefficients whose degree leaves remainder {res} modulo {mods}',f'the sum of the coefficients in degrees {t-1}, {t}, and {t+1}',f'the sum of coefficients of degree at least {sumw-t}'][m]
 add('coefficient-desk',CNT,'Generating functions',4,'For the polynomial P(x) = '+' · '.join(f'(1+x^{a})^{b}' for a,b in groups)+f', what is {ask}?',ans,ck,'For a factor (1+x^s)^r, choosing j copies of x^s adds sj to the degree in C(r,j) ways. Start with coefficient list [1] and add these shifted lists for each factor. The nonzero (degree: coefficient) terms meeting the required condition are '+(', '.join(f'{s}: {num}' for s,num in enumerate(hist) if num and pred(s)) or 'none')+f'. Their sum is {ans}.',[2**len(degs),hist[t],sum(hist[:t]),ans//2])
 # Interior lattice beneath two varying lines, exact floor sums vs integer point enumeration.
 w=R.randrange(6,13);p=R.randrange(2,7);q=R.randrange(2,7);c=R.randrange(2,6);d=R.randrange(3,7);sl=R.choice([1,2,3]);off=R.randrange(1,5)
 def bounds(x):
  top=min(F(p*x+c,q),F(sl*(w-x)+d,3));return max(0,math.floor(top))
 condition=lambda x,y:[True,(x+y)%2==0,y>=2,x%2==1,y%2==1][m] and [True,x!=y,x+y<=w][j]
 counts=[]
 for x in range(1,w):
  h=bounds(x)
  counts.append(sum(condition(x,y) for y in range(1,h+1)))
 ck=sum(1 for x in range(1,w) for y in range(1,50) if q*y<=p*x+c and 3*y<=sl*(w-x)+d and condition(x,y));ans=sum(counts);rule=['',' and x+y must be even',' and y must be at least 2',' and x must be odd',' and y must be odd'][m]
 add('canopy-points',GEO,'Lattice point bounds',3,f'Count the integer pairs with 1 ≤ x < {w}, y ≥ 1, {q}y ≤ {p}x + {c}, and 3y ≤ {sl}({w}−x)+{d}{rule}{["",", excluding points on y=x",f", restricted further to x+y≤{w}"][j]}.',ans,ck,f'At each x the last possible y is the floor of the smaller of the two upper bounds. For x=1,…,{w-1} these heights are {join(bounds(x) for x in range(1,w))}. Applying the remaining condition gives column counts {join(counts)}, totalling {ans}.',[sum(bounds(x) for x in range(1,w)),ans//2,ans+w])
 # Random walk under modular boundary. Matrix/DP vs explicit paths.
 M=R.choice([5,6,7,8]);moves=R.sample(range(1,M),2+(j==2));N=R.choice([4,5,6]);s=R.randrange(M);end=R.choice([x for x in range(M) if x!=s]);veto=R.choice([x for x in range(M) if x not in(s,end)]); movesBy=[moves if j!=1 or i%2==0 else [(-h)%M for h in moves] for i in range(N)]
 def good(p):return [p[-1]==end,p[-1]==end and veto not in p,end not in p[:-1] and p[-1]==end,sum(x==end for x in p)==1,p[-1]!=s and veto not in p][m]
 n0=0
 for route in product(*movesBy):
  pos=s;ps=[]
  for b in route:pos=(pos+b)%M;ps.append(pos)
  n0+=int(good(ps))
 states={(s,0,False,False):1}
 for i in range(N):
  nxt=collections.Counter()
  for (p,h,v,early),num in states.items():
   for delta in movesBy[i]:
    nx=(p+delta)%M;nxt[(nx,min(2,h+(nx==end)),v or nx==veto,early or (nx==end and i<N-1))]+=num
  states=nxt
 n2=sum(num for (pos,h,v,early),num in states.items() if [pos==end,pos==end and not v,pos==end and not early,h==1,pos!=s and not v][m]);den=len(moves)**N;goal=[f'finish at {end}',f'finish at {end} without landing on {veto}',f'first land on {end} on the final move',f'land on {end} exactly once',f'finish away from {s} and never land on {veto}'][m]
 add('modular-walk',PRO,'Finite-state probability',4,f'A token starts on space {s} of a clockwise ring numbered 0 through {M-1}. Each move independently advances by one of {{{join(moves)}}} spaces with equal probability. {["","On even-numbered moves reverse the direction (move counterclockwise) instead.",""][j]} After {N} moves, what is the probability that it will {goal}?',F(n0,den),F(n2,den),f'Count move strings, all {den} equally likely. Begin with one at {s}. At each move, send each count to (position + jump) mod {M} for every listed jump, tracking visits to {end} and {veto} as required. After {N} moves, qualifying strings by final position 0,…,{M-1} are '+join(sum(num for (pos,h,v,early),num in states.items() if pos==t and [pos==end,pos==end and not v,pos==end and not early,h==1,pos!=s and not v][m]) for t in range(M))+f'. Divide their sum {n0} by {den} to obtain {F(n0,den)}.',[F(den-n0,den),F(1,M),F(1,len(moves)),F(n0,den+1)])
 # Gaussian integer products, exact recurrence and conjugate checks.
 terms=[(R.randrange(1,5),R.choice([-3,-2,-1,1,2,3])) for _ in range(2+j)];zv=1+0j;x,y=1,0;steps=[]
 for a,b in terms:
  zv*=complex(a,b);x,y=x*a-y*b,x*b+y*a;steps.append((x,y))
 norm=x*x+y*y;req=['the squared modulus of z','|Re(z) − Im(z)|','|Re(z²)|','|Im(z²)|','the squared distance from z to 1+i'][m];vals=[norm,abs(x-y),abs(x*x-y*y),abs(2*x*y),(x-1)**2+(y-1)**2];other=[math.prod(a*a+b*b for a,b in terms),round(abs(zv.real-zv.imag)),round(abs((zv*zv).real)),round(abs((zv*zv).imag)),round(abs(zv-(1+1j))**2)]
 add('gaussian-stamps',ALG,'Complex multiplication',3,'Let z = '+' · '.join(f'({a} '+('+' if b>0 else '−')+f' {abs(b)}i)' for a,b in terms)+f'. What is {req}?',vals[m],other[m],f'For (x+iy)(a+ib), the new pair is (xa−yb, xb+ya). Starting at (1,0), the pairs after each multiplication are {join(steps)}. '+[f'Use x²+y².',f'Subtract the two coordinates and take absolute value.',f'The real part of the square is x²−y².',f'The imaginary part of the square is 2xy.',f'Subtract (1,1) and sum the squared coordinates.'][m]+f' This gives {vals[m]}.',[abs(x)+abs(y),norm,abs(x*y),abs(x+y)])
 # Polynomial remainders: direct powers reduced mod quadratic vs interpolation at two distinct roots.
 a,b=R.sample([1,2,3,4],2);powers=R.sample(range(2,8+j),3);coefs=R.sample([-3,-2,-1,1,2,3],3)
 f=lambda x:sum(c*x**p for c,p in zip(coefs,powers));u=F(f(a)-f(b),a-b);v=f(a)-u*a;rem=collections.Counter(dict(zip(powers,coefs)))
 for n in range(max(powers),1,-1):
  t=rem[n];rem[n-1]+=(a+b)*t;rem[n-2]-=a*b*t
 func=lambda x,y:[abs(x),abs(y),abs(x+y),abs(x-y),abs(2*x+y)][m];val=func(u,v);ask=['|U|','|V|','|U+V|','|U−V|','|2U+V|'][m]
 add('remainder-interpolation',ALG,'Polynomial remainders',4,'When '+' + '.join(f'({c})x^{p}' for c,p in zip(coefs,powers))+(f' is divided by (x−{a})(x−{b})' if j!=1 else f' is divided by x²−{a+b}x+{a*b}')+f', the remainder is Ux+V. Find {ask}.',val,func(rem[1],rem[0]),f'At either root of the divisor the remainder equals the original polynomial. Thus {a}U+V={f(a)}, {b}U+V={f(b)}. Subtraction gives U={u}, then V={v}. Substitution into {ask} gives {val}.',[abs(u),abs(v),abs(u+v),abs(u-v)])
 # Congruence sieves with powers; CRT count vs direct enumeration. Varies degree, local residue sets and residues allowed.
 p,q=R.sample([3,5,7,11],2);h=2+(k%3);a,b=R.sample(range(1,6),2);poly=lambda x:x**h+a*x+b
 A=set(R.sample(range(p),min(2+j,p-1)));B=set(R.sample(range(q),min(1+j,q-1)));U=[x for x in range(p) if poly(x)%p in A];V=[x for x in range(q) if poly(x)%q in B];ls=p*q;counts=[len(U)*len(V),len(U)*(q-len(V)),p*len(V)+q*len(U)-2*len(U)*len(V),ls-(p-len(U))*(q-len(V)),(p-len(U))*(q-len(V))];cond=lambda x,y:[x and y,x and not y,x!=y,x or y,not(x or y)][m];ck=sum(bool(cond(poly(x)%p in A,poly(x)%q in B)) for x in range(ls));what=['both lamps glow','only P glows','exactly one lamp glows','at least one lamp glows','neither lamp glows'][m]
 add('crt-screens',NT,'Chinese remainder theorem',4,f'For 0 ≤ n < {p*q}, put t=n^{h}+{a}n+{b}. Lamp P glows if t modulo {p} belongs to {{{join(sorted(A))}}}; lamp Q glows if t modulo {q} belongs to {{{join(sorted(B))}}}. For how many integers n is it true that {what}?',counts[m],ck,f'Testing residues modulo {p} gives eligible n residues {{{join(U)}}}; modulo {q} they are {{{join(V)}}}. Each ordered residue pair occurs once by the Chinese remainder theorem. There are {len(U)} P choices and {p-len(U)} non-P choices, with {len(V)} Q choices and {q-len(V)} non-Q choices. Combine the disjoint categories for “{what}” to get {counts[m]}.',[ls-counts[m],len(U)*len(V),p+q,counts[m]+1])
 return out
