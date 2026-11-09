from content_core import *
def make(k):
 R=random.Random(81031+k); m=k%5; j=k//5; out=[]
 def add(*args):out.append(item(8,args[0],k,*args[1:]))
 # A noncongruent tile figure. Count edges from two different representations.
 C=poly(k,R,7+k%6);n=len(C);adj=sum((x+1,y) in C for x,y in C)+sum((x,y+1) in C for x,y in C)
 bd=sum((x+a,y+b) not in C for x,y in C for a,b in ((1,0),(-1,0),(0,1),(0,-1)))
 edges=collections.Counter(tuple(sorted(e)) for x,y in C for e in [((x,y),(x+1,y)),((x+1,y),(x+1,y+1)),((x,y+1),(x+1,y+1)),((x,y),(x,y+1))])
 width=max(x for x,y in C)+1;height=max(y for x,y in C)+1
 asks=['How many unit edges border an empty space or the outside?','How many unit segments are shared by two tiles?','One matchstick covers a unit segment, even if two tiles use it. How many matchsticks draw the figure?','How many white unit squares must be filled to complete the smallest axis-parallel rectangular frame containing the tiles?','One unit of ribbon goes around each tile separately. How many units are saved by tracing only exposed edges instead?']
 ans=[4*n-2*adj,adj,4*n-adj,width*height-n,2*adj][m]; ck=[sum(i==1 for i in edges.values()),sum(i==2 for i in edges.values()),len(edges),sum((x,y) not in C for x in range(width) for y in range(height)),4*n-bd][m]
 sol=[f'{n} squares supply {4*n} sides. The {adj} shared sides were counted twice; removing both copies leaves {ans}.',f'The {n} tiles have {4*n} sides before joining. The boundary has {bd} unit edges. The other {4*n-bd} are counted twice, giving {ans} shared segments.',f'Start with 4 × {n} sides; the {adj} joins each duplicate one stick, leaving {ans}.',f'The frame is {width} by {height}, so its {width*height} cells include {n} filled cells. The difference is {ans}.',f'Each of the {adj} joins takes two formerly exposed sides inside. The saving is 2 × {adj} = {ans}.'][m]
 add('tile-studio',GEO,'Area and perimeter',2,'Each shaded tile is a unit square. '+asks[m],ans,ck,sol,[bd,adj,n,width*height],square_art(C))
 # Relays have varying connectivity and different mandatory/forbidden stations.
 layers=[['S'],list('ABC'),list('DEF'),list('GH'),['T']];E=set()
 for X,Y in zip(layers,layers[1:]):
  for a in X:E.add((a,R.choice(Y)))
  for b in Y:E.add((R.choice(X),b))
  for a,b in product(X,Y):
   if R.random()<.3:E.add((a,b))
 routes=[]
 for v in product(*layers[1:-1]):
  path=('S',)+v+('T',)
  if all(e in E for e in zip(path,path[1:])):routes.append(path)
 x=R.choice(layers[1]);y=R.choice(layers[2]);z=R.choice(layers[3]);cond=[f'pass through {y}',f'avoid {x}',f'visit both {x} and {z}',f'pass through {x} or {y} (including both)',f'visit exactly one of {y} and {z}'][m]
 yes=lambda p:[y in p,x not in p,x in p and z in p,x in p or y in p,(y in p)!=(z in p)][m]
 good=[p for p in routes if yes(p)]
 def dp(j,last,p):
  if j==len(layers):return int(yes(p))
  return sum(dp(j+1,b,p+(b,)) for b in layers[j] if (last,b) in E)
 chains=['–'.join(p[1:-1]) for p in good];sub='; '.join(chains) if chains else 'none'
 add('relay-map',CNT,'Counting routes',3,f'A relay travels from S to T along the drawn links, always from left to right. How many routes {cond}?',len(good),dp(1,'S',('S',)),f'List the three intermediate stations in order, rejecting a missing connection or a route that fails the condition. The qualifying triples are {sub}. Hence there are {len(good)} routes.',[len(routes),len(routes)-len(good),3,6],network(layers,sorted(E),None))
 # Distinct packets and offers, exact purchase vs overbuying; bounded independent enumeration.
 sizes=R.sample([3,4,5,6,7,8],3);cost=[R.randint(3,8) for _ in sizes];target=R.randint(12,20);cap=target+max(sizes)
 while True:
  cases=[(a,b,c) for a,b,c in product(range(cap//min(sizes)+1),repeat=3) if (q:=sum(i*j for i,j in zip((a,b,c),sizes)))>=target and q<=cap and [q==target,True,q==target and a>0,True,q==target][m]]
  if cases:break
  target+=1;cap=target+max(sizes)
 f=lambda v:sum(i*j for i,j in zip(v,cost)); mini=min(f(v) for v in cases);count=len(cases)
 if m==1:cases=[v for v in cases if sum(i*j for i,j in zip(v,sizes))<=target+max(sizes)];
 if m in (0,1,2): val=mini;goal=['exactly the target','at least the target','exactly the target and buy at least one A packet'][m];ask=f'What is the least cost to obtain {goal}?'
 elif m==3:val=min(sum(v) for v in cases);goal='at least the target';ask='What is the fewest packets that supply at least the target?'
 else:val=count;goal='exactly the target';ask='How many different packet-count triples supply exactly the target?'
 best=min(cases,key=(lambda v:sum(v)) if m==3 else f)
 level=cap+1; dpv={(0,False):0};ways=collections.Counter({0:1})
 for idx,(s,pr) in enumerate(zip(sizes,cost)):
  nxt={};nw=collections.Counter()
  for (q,has),c0 in dpv.items():
   for t in range((cap-q)//s+1):
    key=(q+t*s,has or (idx==0 and t>0));nxt[key]=min(nxt.get(key,10**5),c0+t*(1 if m==3 else pr))
  for q,v in ways.items():
   for t in range((cap-q)//s+1):nw[q+t*s]+=v
  dpv=nxt;ways=nw
 ck=ways[target] if m==4 else min(v for (q,h),v in dpv.items() if (q==target if m in(0,2) else q>=target) and (m!=2 or h))
 bestA=[]
 for a in range(cap//sizes[0]+1):
  l=[v for v in cases if v[0]==a];bestA.append(len(l) if m==4 else (min((sum(v) if m==3 else f(v)) for v in l) if l else '–'))
 add('packet-desk',AR,'Whole-number optimisation',3,(f'Packet sizes A,B,C are {join(sizes)} badges. '+[f'Individual costs are {join(cost)} credits.',f'Buying A+B, B+C, and A+C costs respectively {cost[0]+cost[1]}, {cost[1]+cost[2]}, and {cost[0]+cost[2]} credits. There are no bundle discounts.',f'A sample order of one of each packet costs {sum(cost)} credits. Removing A from that order saves {cost[0]}; replacing one B with one A changes its price by {cost[0]-cost[1]} credits (new minus old).'][j]+f' The target is {target} badges. '+ask),val,ck,(('' if j==0 else f'Recover the individual costs first: A, B, C cost {join(cost)}. '+('Half the sum of the three pair totals is the price of A+B+C; subtract the other pair to get each price. ' if j==1 else 'The saving gives A; subtract the replacement change from A to get B, then subtract A+B from the order total for C. '))+f'Fix the number a of A packets. For each a, try b from zero upward; c supplies the remainder. In order a = 0, 1, … the '+('counts' if m==4 else 'best attainable values')+f' are {join(bestA)}. '+(f'Add them to get {val}.' if m==4 else f'The smallest is {val}, attained by (A,B,C) = {best}.')+(' With positive costs or packet counts, a minimum never overshoots by a full largest packet: removing a packet would still meet the target.' if m in(1,3) else '')),[target,sum(best),mini,count])
 # Probability: coloured tiles bearing labels; parity, adjacency, comparison and replacement.
 a,b,c=R.sample(range(2,7),3);boxes=[(u,i) for u,s in zip('RGB',(a,b,c)) for i in range(1,s+1)]
 pred=[lambda x,y:x[0]==y[0],lambda x,y:x[1]==y[1],lambda x,y:x[0]!=y[0] and x[1]+y[1]==5,lambda x,y:x[1]<y[1],lambda x,y:x[1]%2==y[1]%2 and x[0]!=y[0]][m]
 pairs=(list(permutations(boxes,2)) if j==0 else list(product(boxes,repeat=2)) if j==1 else [(x,y) for x,y in permutations(boxes,2) if x[0]!='B']);fav=sum(pred(x,y) for x,y in pairs)
 mode=k//5;other=sum(sum(pred((u,i),(v,j)) for i in range(1,sz+1) for j in range(1,tz+1) if (mode==1 or (u,i)!=(v,j)) and (mode!=2 or u!='B')) for u,sz in zip('RGB',(a,b,c)) for v,tz in zip('RGB',(a,b,c)))
 by=[sum(pred(x,y) for x,y in pairs if x[0]==u) for u in 'RGB'];event=['both have the same colour','they have the same number','their colours differ and their numbers sum to 5','the second number is strictly larger than the first','their colours differ and their numbers have the same parity'][m]
 add('drawn-seals',PRO,'Counting equally likely outcomes',3,f'Red seals are numbered 1 to {a}, green 1 to {b}, and blue 1 to {c}. {["Two seals are drawn in order without replacement.","Draw twice, returning and mixing the first seal before the second draw.","Draw two seals without replacement. An observer tells you the first was not blue."][j]} What is the probability that {event}?',F(fav,len(pairs)),F(other,[(len(boxes)*(len(boxes)-1)),len(boxes)**2,(a+b)*(len(boxes)-1)][j]),f'Use ordered pairs: there are {len(pairs)} equally likely pairs under the stated drawing rule. For each possible first label, count eligible second seals satisfying the event. Grouping by first colour R,G,B gives {join(by)} favourable pairs. Their total {fav} divided by {len(pairs)} reduces to {F(fav,len(pairs))}.',[F(len(pairs)-fav,len(pairs)),F(fav,len(boxes)**2),F(1,3),F(1,2)])
 # Integer cards with two independent conditions and arbitrary digits.
 digs=sorted(R.sample(range(0,10),5));mod=R.choice([3,4,5,6,7]);rem=R.randrange(mod);rules=['the first digit is smaller than the last','the middle digit is the largest digit','the digits increase from left to right','the first and last digits have different parity','the middle digit is even'][m]
 def ok(a,b,c):return [a<c,b>max(a,c),a<b<c,(a-c)%2==1,b%2==0][m] and [True,a==min(t for t in digs if t>0) or c==max(digs),abs(a-c)>1][j]
 cases=[100*a+10*b+c for a,b,c in permutations(digs,3) if a and ok(a,b,c) and (100*a+10*b+c)%mod==rem];N=len(cases)
 ck=sum(len(set(s:=str(x)))==3 and all(int(t) in digs for t in s) and ok(*map(int,s)) for x in range(100+((rem-100)%mod),1000,mod))
 by=[sum(x//100==a for x in cases) for a in digs if a]
 add('code-press',NT,'Digits and remainders',3,f'A three-digit code is an ordinary three-digit number made from {join(digs)} without repeating a digit. It leaves remainder {rem} when divided by {mod}, and {rules}. {[""," The hundreds digit must also be the smallest available nonzero digit or the units digit must be the largest available digit (or both)."," Adjacent integers may not appear as the first and last digit."][j]} How many codes work?',N,ck,f'Fix the hundreds digit in turn ({join(d for d in digs if d)}). For each, permute two of the remaining digits, checking the comparison and remainder. The counts in that order are {join(by)}. The resulting codes are {join(sorted(cases)) or "none"}, so the count is {N}.',[len(digs),N+2,2*N])
 # Timetable with different day masks, counting event overlaps.
 days=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];X=set(R.sample(days,R.randrange(2,5)));Y=set(R.sample(days,R.randrange(2,6)));start=R.randrange(7);length=R.randint(16,34);cond=[X&Y,X-Y,Y-X,X^Y,X|Y][m]
 ix=lambda v:', '.join(d for d in days if d in v)
 qtxt=['both kiosks open','only amber opens','only blue opens','exactly one kiosk opens','at least one kiosk opens'][m];full,tail=divmod(length,7);part=[days[(start+i)%7] for i in range(tail)];N=full*len(cond)+sum(d in cond for d in part)
 add('market-calendar',SEQ,'Periodic patterns',2,f'The amber kiosk opens on {ix(X)} and the blue kiosk on {ix(Y)} every week. A festival lasts {length} consecutive days beginning on {days[start]} (day 1). On how many festival days does the following occur: {qtxt}?',N,sum(days[(start+i)%7] in cond for i in range(length)),f'The qualifying weekdays are {ix(cond) or "none"}. There are {full} complete weeks and {tail} days left. The tail is {join(part) or "empty"}, contributing {sum(d in cond for d in part)}. The total is {N}.',[full*len(cond),length-N,len(cond),length])
 # Weighing averages: irregular positive values in tabulated groups.
 vals=sorted(R.sample(range(1,12),4));freq=[R.randrange(1,5) for _ in vals];series=sorted(v for v,f in zip(vals,freq) for _ in range(f));total=len(series);sm=sum(series);mid=lambda s:F(s[(len(s)-1)//2]+s[len(s)//2],2)
 target=['mean score','median score','fraction of players with strictly above-average scores','mean of the remaining scores after removing one highest and one lowest score','difference between the highest score and the median score'][m]
 ava=F(sm,total);calc=[ava,mid(series),F(sum(x>ava for x in series),total),F(sm-vals[0]-vals[-1],total-2),vals[-1]-mid(series)][m]
 med=F(statistics.median(series));ck=[F(sum(v*f for v,f in zip(vals,freq)),sum(freq)),med,F(sum(f for v,f in zip(vals,freq) if total*v>sm),total),F(sum(series[1:-1]),total-2),vals[-1]-med][m];medpos=f'The middle positions are {(total+1)//2} and {total//2+1}; their entries are {series[(total-1)//2]} and {series[total//2]}.'
 explain=[f'Divide the score total {sm} by the {total} players.',medpos,f'The mean is {sm}/{total}. The scores above that threshold account for {sum(x>ava for x in series)} players out of {total}.',f'Subtract {vals[0]} and {vals[-1]} from the total {sm}, then divide by {total-2}.',medpos+f' Subtract this median from {vals[-1]}.'][m]
 add('scoreboard',PRO,'Averages and distributions',2,(f'A game scoreboard shows scores {join(vals)} with respectively {join(freq)} players.' if j==0 else f'The only possible scores are {join(vals)}. At or below these four scores the cumulative player counts are {join(itertools.accumulate(freq))}.' if j==1 else f'Two heats used scores {join(vals)}. The first heat had frequency counts {join(f//2 for f in freq)} and the second had {join(f-f//2 for f in freq)}. Pool the heats.')+f' What is the {target}?',calc,ck,(['','Subtract consecutive cumulative totals to recover counts '+join(freq)+'. ','Add heat counts column by column to get '+join(freq)+'. '][j])+explain+f' This gives {fmt(calc)}.',[ava,med,F(sm,total+1),F(vals[0]+vals[-1],2)])
 # Packing tiles bounded selection, generative structural restriction.
 weights=sorted(R.sample(range(1,11),6));target=R.randint(9,16);qual=lambda s:[True,weights[0] in s or weights[-1] in s,not (weights[1] in s and weights[3] in s)][j];sel=[s for s in combinations(weights,3) if qual(s) and [sum(s)%3==0,sum(s)>=target,s[-1]-s[0]<=6,s[0]+s[1]>s[2],sum(a%2 for a in s)==1][m]];N=len(sel)
 predtxt=['their sum is divisible by 3',f'their sum is at least {target}','the largest minus the smallest is at most 6','the three numbers can be lengths of a nondegenerate triangle','exactly one number is odd'][m]
 verify=0
 for mask in range(64):
  v=[x for i,x in enumerate(weights) if mask>>i&1]
  if len(v)==3 and qual(v):
   if [sum(v)%3==0,sum(v)>=target,max(v)-min(v)<=6,2*max(v)<sum(v),sum(x%2==1 for x in v)==1][m]:verify+=1
 by=[sum(t[0]==x for t in sel) for x in weights[:-2]]
 add('three-tags',CNT,'Organised casework',2,f'Six luggage tags show {join(weights)}. Choose three different tags; order does not matter. {["",f"A choice must contain at least one end of the sorted list ({weights[0]} or {weights[-1]}).",f"The tags {weights[1]} and {weights[3]} cannot travel together."][j]} How many choices satisfy this condition: {predtxt}?',N,verify,f'Fix the smallest tag. Its possible values are {join(weights[:-2])}. Pair two larger tags and test the stated condition; the four counts are {join(by)}. They are disjoint and sum to {N}.',[math.comb(6,3)-N,math.comb(5,2),math.comb(5,3),N*2])
 # Inverse operations; order and the operations themselves change.
 startval=R.randrange(2,11);actions=R.sample(['double','triple','add','square','subtract'],3);actions+=(['add'] if j==1 else ['square','subtract'] if j==2 else []);ds=[];a=startval;h=[a]
 for t in actions:
  d=R.randint(2,5)
  if t=='subtract' and a<=d:d=1
  ds.append(d);a={'double':2*a,'triple':3*a,'add':a+d,'square':a*a,'subtract':a-d}[t];h.append(a)
 names=[{'double':'double it','triple':'triple it','add':f'add {d}','square':'square it','subtract':f'subtract {d}'}[t] for t,d in zip(actions,ds)]
 rev=a
 for t,d in reversed(list(zip(actions,ds))):rev={'double':lambda:rev//2,'triple':lambda:rev//3,'add':lambda:rev-d,'square':lambda:math.isqrt(rev),'subtract':lambda:rev+d}[t]()
 add('reverse-machine',ALG,'Inverse operations',2,f'A machine starts with a positive integer. Its instructions, in order, are: '+', then '.join(names)+f'. All intermediate numbers are positive and the display ends at {a}. '+('What was on the display directly after the first instruction?' if k==8 else 'What was the starting number?'),h[1] if k==8 else startval,(h[-2::-1][-2] if k==8 else rev),f'Undo the operations in reverse order, using the positive square root whenever a square must be undone. The successive displays backwards are {join(reversed(h))}. Thus the initial number was {startval}; the first instruction gave {h[1]}.',[h[1],h[2],startval*2])
 # Symmetry of mosaics: independent orbit counting versus direct comparison across axes.
 n=R.choice([4,5,6]);cells={(x,y) for x in range(n) for y in range(n) if R.random()<.32};trans=[lambda x,y:(n-1-x,y),lambda x,y:(x,n-1-y),lambda x,y:(y,x),lambda x,y:(n-1-y,n-1-x),lambda x,y:(n-1-x,n-1-y)][m];image={trans(x,y) for x,y in cells};missing=image-cells;axis=['a vertical mirror line down the centre','a horizontal mirror line across the centre','reflection across the top-left to bottom-right diagonal','reflection across the top-right to bottom-left diagonal','a half-turn about the centre'][m];pairs=sum(1 for x in range(n) for y in range(n) if ((x,y) in cells)!=(trans(x,y) in cells))//2
 tile=''.join(f'<rect x="{5+x*18}" y="{5+y*18}" width="18" height="18" fill="{("#bc7630" if (x,y) in cells else "white")}" stroke="#586675"/>' for x in range(n) for y in range(n));art=svg(tile,'Grid with specified coloured squares',n*18+10,n*18+10)
 add('mirror-workshop',GEO,'Symmetry and transformations',2,f'Only blank squares may be coloured in this {n} by {n} mosaic. What is the fewest that must be coloured for the result to have symmetry under {axis}?',len(missing),pairs,f'Each coloured square needs a coloured partner. Comparing paired squares gives {pairs} mismatched pairs, each needing one addition. Pairs already alike and squares fixed by the symmetry need no change. Hence {pairs} additions suffice.',[len(cells),len(cells&image),len(missing)*2],art)
 return out
