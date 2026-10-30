"""Regenerate the full bank, including linked decision sections and review ledger."""
from ai_sl_core import *
import ai_sl_number,ai_sl_functions,ai_sl_geometry,ai_sl_statistics,ai_sl_calculus
def extend(q,*parts):
 for prompt,steps in parts:
  label=chr(97+len(q['parts']));q['parts'].append(dict(label=label,prompt=prompt,marks=len(steps)));q['markScheme'].append(dict(part=label,steps=[dict(code=c,text=z) for c,z in steps]))
def replace_parts(q,parts):
 q['parts']=[];q['markScheme']=[];extend(q,*parts)
def enrich(q):
 f=(q['number']-1)//4;i=(q['number']-1)%4;t=q['topicId']
 if t=='number-algebra':
  easy={0,1,13,14,17};hard={8,9,10,11,12,15,16,18}
  if f==8:
   V=10000+1000*i;r=.055+.005*i;infl=.025+.002*i;N=6+i;other=.045+.004*i;B=V*(1+other)**N/(1+infl)**N
   extend(q,P(f'Another account offers {100*other:g}% annually with the same inflation. Find its real value after {N} years and recommend an account based only on real return.',M(f'$B_2={V}(1+{other:g})^{{{N}}}/(1+{infl:g})^{{{N}}}$.'),A(f'USD {money(B)}.'),R('Choose the original account because it produces the greater real value over the same period.')))
  if f==9:
   V=16000+2000*i;r=.06+.006*i;N=36+12*i;j=r/12;pm=V*j/(1-(1+j)**-N);N2=N-12;pm2=V*j/(1-(1+j)**-N2);saving=N*pm-N2*pm2
   extend(q,P(f'An alternative repays the same loan over {N2} months at the same rate. Find its monthly payment and the total interest saved.',M(f'Use the same financial-solver settings with $N={N2}$.'),A(f'Alternative monthly payment USD {money(pm2)}.'),M(f'Compare total payments: ${N}({pm:.8f})-{N2}({pm2:.8f})$.'),A(f'Interest saving USD {money(saving)}.')))
  if f==10:
   V=24000+2000*i;r=.072+.006*i;j=r/12;paid=12+6*i;pm=V*j/(1-(1+j)**-60);B=V*(1+j)**paid-pm*((1+j)**paid-1)/j;saved=(60-paid)*pm-B
   extend(q,P('If the borrower settles the loan immediately after that payment, find the future interest avoided, assuming no settlement fee.',M('Compare the sum of the remaining scheduled payments with the outstanding balance.'),A(f'USD {money(saved)}.')),P('Give one practical consideration, apart from the interest saved, relevant to early settlement.',R('For example, whether paying the balance leaves enough accessible money for other needs; accept another specific relevant consideration.')))
  if f==11:
   D=150+25*i;j=(.036+.006*i)/12;N=48+12*i;target=20000+2000*i;needed=target*j/((1+j)**N-1)
   extend(q,P(f'The saver instead wants USD {target} after the same period. Find the required end-of-month deposit.',M(f'Financial solver: $PV=0$, $FV={target}$, $N={N}$ and the same monthly interest; solve for PMT.'),A(f'Deposit magnitude USD {money(needed)} per month.')),P('To ensure the target is reached when deposits are in whole cents, state how the payment should be rounded and why.',A(f'Pay USD {math.ceil((needed-1e-10)*100)/100:.2f} each month.'),R('Round upwards to the next cent; rounding down would make the final balance slightly below the target.')))
  if f==12:
   D=200+30*i;j=.004+.0005*i;target=13000+1000*i;N=math.ceil(math.log(1+target*j/D)/math.log(1+j));N0=math.ceil(target/D)
   extend(q,P('Compare this with saving the same monthly amount in a zero-interest account.',M(f'At zero interest, solve ${D}N\\geq{target}$ for the least integer N.'),A(f'{N0} monthly deposits.'),R(f'The interest-paying account reaches the target {N0-N} months earlier.')))
 elif t=='functions':
  easy={0,2,4,10,13};hard={5,6,7,8,9,14,15}
  if f==2:
   a=1.4+.2*i;b=6+i;v=30+5*i;y=a*v+b
   replace_parts(q,[P(f'Find $f^{{-1}}({y:g})$, explaining what this value represents.',M(f'Solve ${a:g}x+{b}={y:g}$ for the original reading.'),A(f'$f^{{-1}}({y:g})={v}$: an original reading of {v} produces this displayed value.')),P('State the domain of the inverse.',M('Find the displayed values corresponding to original readings 0 and 100.'),A(f'${b}\\leq x\\leq{100*a+b:g}$.')),P('Describe the geometrical relationship between the graphs of f and its inverse.',R('They are reflections of each other in the line y=x.'))])
   q['verification']['notes']='Numerical inverse use, output-domain endpoints and graphical reflection only; no general algebraic inverse derivation. '+q['verification']['notes']
  if f==5:
   a=-1-i;b=8+2*i;c=10+i;pred=a*16+b*4+c
   extend(q,P(f'An independent observation at x=4 is {pred+2}. Find the residual (observed minus predicted) and explain its sign.',A('Residual $=2$.'),R('The positive residual means the model underestimates the observation by 2 units.')))
  if f==6:
   a=2+i;b=20+2*i;s=2+i;v=(a+b)/2;profit=lambda x:-s*(x-a)*(x-b);L=math.floor(v);U=math.ceil(v);candidates=[L,U] if L!=U else [L-1,L,L+1]
   comparisons=', '.join(f'$P({x})={profit(x):g}$' for x in candidates)
   extend(q,P('Find a whole-number sales level giving the greatest profit, with supporting comparisons.',M('Compare the adjacent integers around the continuous vertex; when the vertex itself is an integer, include it and its two neighbours.'),A(f'{comparisons} USD; choose {L} batches. Accept {U} if the maximum values tie.')))
  if f==7:
   a=180+20*i;r=1.18+.02*i;actual=a*r**8*.95;pred=a*r**8
   extend(q,P(f'A later observation at t=8 is {actual:.8f}. Find the model\'s percentage error relative to this observation, and state whether it overestimates.',M(f'$100\\lvert {pred:.8f}-{actual:.8f}\\rvert/{actual:.8f}$.'),A(f'${n(100/19)}\\%$.'),R('It overestimates because the predicted value exceeds the observed value.')))
  if f==8:
   amb=18+i;ex=60+5*i;r=.78+.02*i;t1=math.log(30/ex)/math.log(r);t2=math.log(10/ex)/math.log(r)
   extend(q,P(f'Find how long the model temperature remains between {amb+10} °C and {amb+30} °C.',M(f'Find the earlier time when $T={amb+30}$: $t={n(t1)}$ minutes.'),A(f'Duration $={n(t2-t1)}$ minutes.')),P('Explain why the temperature never reaches the surrounding temperature in finite time according to this model.',R('The exponential term is positive for every finite t, so T always remains above the surrounding temperature.')))
  if f==15:
   base=8+i;r=2+i;r2=1+.25*i;budget=base+5*r+8*r2
   extend(q,P(f'Find the greatest usage affordable with a budget of USD {budget:g}.',M(f'The budget exceeds the five-unit charge; solve ${base+5*r}+{r2:g}(x-5)={budget:g}$.'),A('$x=13$ units.')),P('Explain the meaning of the change in gradient at x=5.',R('The marginal cost falls after 5 units because each additional unit is charged at the lower rate.')))
 elif t=='geometry-trigonometry':
  easy={0,6,8,12,14};hard={2,4,11,15,17,18,19}
  if f==6:
   # Keep the fully evaluated triangle private; unknown height must not appear on the question.
   q['markSchemeDiagramSvg']=q.pop('diagramSvg')
  if f==2:
   side=10+2*i;h=12+i;sl=math.hypot(h,side/2);faces=2*side*sl;rate=18+2*i
   extend(q,P(f'Only the four triangular faces are painted, at USD {rate} per m². Find the painting cost, to the nearest dollar.',M(f'Painted area is the total surface area minus base area: $2({side})l$.'),A(f'USD {round(faces*rate)}.')))
  if f==4:
   r=4+i;h=9+i;vol=math.pi*r*r*h+2*math.pi*r**3/3;flow=1.8+.2*i
   extend(q,P(f'Water enters the empty tank at a constant {flow:g} m³ per minute. Estimate the time to fill it.',M('Divide the total tank volume by the volume supplied per minute.'),A(f'${n(vol/flow)}$ minutes.')),P('Give one reason the actual filling time could differ.',R('For example, the flow rate may vary, or the quoted dimensions may be approximate; accept a specific relevant reason.')))
  if f==11:
   d1=12+2*i;d2=9+i;b1=35+5*i;b2=115+5*i;E=d1*math.sin(math.radians(b1))+d2*math.sin(math.radians(b2));N=d1*math.cos(math.radians(b1))+d2*math.cos(math.radians(b2));B=math.degrees(math.atan2(E,N))%360;dist=math.hypot(E,N)
   extend(q,P('Find the bearing required to travel directly back to the starting point, to one decimal place.',A(f'${(B+180)%360:05.1f}^\\circ$.')),P('Find the distance saved by returning directly rather than retracing both legs.',M('Subtract the direct distance from the two-leg distance.'),A(f'${n(d1+d2-dist)}$ km.')))
  if f==15:
   a=6+2*i;b=8+2*i;vx=a/2;vy=b/2
   q['parts'][3]['prompt']='Write the equation of the boundary between sites B and C, and state which part of the bisector is a Voronoi edge.'
   q['parts'][3]['marks']+=1
   q['markScheme'][3]['steps'].append(dict(code='R1',text=f'The Voronoi edge is the ray $x\\geq {a/2:g}$ on this line; below this x-value site A is closer.'))
   extend(q,P(f'A point P is at $({vx+.5:g},{vy-.5:g})$. Determine which site is nearest, giving squared-distance values.',M('Calculate the squared distance to A, B and C.'),A(f'$PA^2={(vx+.5)**2+(vy-.5)**2:g}$, $PB^2={(vx+.5-a)**2+(vy-.5)**2:g}$, $PC^2={(vx+.5)**2+(vy-.5-b)**2:g}$.'),R('B is nearest because its squared distance is the least.')))
  if f==18:
   W=12+2*i;H=10+2*i;radius=math.hypot(W/2,H/2)
   extend(q,P('Find the greatest distance from a point in the lower-left cell to its service site.',M('The furthest point is the cell corner at the centre of the original rectangle.'),A(f'Distance $=\\sqrt{{({W/2:g})^2+({H/2:g})^2}}={n(radius)}$ km.')))
 elif t=='statistics-probability':
  easy={0,1,2,5,11};hard={6,8,13,14,17,18,19}
  if f==12:
   probs=[.4,.3-.02*i,.2,.1+.02*i];fee=8+i;E=sum(x*p for x,p in zip([0,5,15,30],probs));plays=200+50*i;gain=plays*(fee-E)
   extend(q,P(f'The organizer expects {plays} plays at the stated fee. Find the expected total net income before other costs.',M(f'Expected net income per play is ${fee}-E(X)$.'),A(f'USD {money(gain)}.')),P('Explain why the actual total income may differ from the expectation.',R('The payouts are random, and expectation is a long-run average rather than a guaranteed outcome.')))
  if f==13:
   N=12+2*i;p=.35+.05*i;k=5+i;prob=sum(binom_p(N,p,j) for j in range(k,N+1));groups=80+10*i
   extend(q,P(f'There are {groups} independent groups of {N} trials. Estimate the number of groups with at least {k} successes.',M('Multiply the tail probability from the earlier part by the number of groups.'),A(f'{round(groups*prob)} groups, to the nearest whole number.')))
 elif t=='calculus':
  easy={0,1,2,5,8};hard={11,12,13,14,15,16,17,19}
  if f==13:
   p=70+10*i;c=10+2*i;k=.5+.1*i;fixed=300+50*i;opt=(p-c)/(2*k);profit=lambda x:(p-c)*x-k*x*x-fixed;L=math.floor(opt);U=math.ceil(opt);candidates=[L,U] if L!=U else [L-1,L,L+1]
   group=q['markScheme'][-1];group['steps'][0]['text']='Compare the integers immediately around the continuous optimum; if the optimum is integral, include it and its two neighbours.'
   group['steps'][1]['text']=', '.join(f'$P({x})={money(profit(x))}$' for x in candidates)+f'; choose {L if profit(L)>=profit(U) else U} units. Accept either if the maximum values tie.'
 q['difficulty']='easy' if f in easy else 'hard' if f in hard else 'medium'
 q['marks']=sum(p['marks'] for p in q['parts']);q['examStyle']='extended-response' if q['marks']>=8 else 'short-response'
 for e in LEDGER:
  if e['id']==q['id']:e['marks']=q['marks'];e['difficulty']=q['difficulty'];e['examStyle']=q['examStyle'];e['linkedPartsReview']='Extra comparison/decision sections recalculated from original unrounded quantities' if q['marks']>=8 else 'Short response method and interpretation reviewed'
 return q
def main():
 LEDGER.clear()
 for module in [ai_sl_number,ai_sl_functions,ai_sl_geometry,ai_sl_statistics,ai_sl_calculus]:
  qs=module.build();qs=[enrich(q) for q in qs];save(qs[0]['topicId'],qs)
 report()
 print('Total',len(LEDGER),'records; families',len({e['family'] for e in LEDGER}),'styles',dict(Counter(e['examStyle'] for e in LEDGER)))
if __name__=='__main__':main()
