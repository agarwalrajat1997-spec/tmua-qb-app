"""Deterministic legacy corrections, honest review ledger and official-code enrichment.

Run after the six original builders and six aa-hl addition builders. IDs and
legacy source mappings are never changed. Mathematical limitations are recorded,
not replaced by a claim that structural validation proves every solution.
"""
from aa_hl_core import *
import re,hashlib,xml.etree.ElementTree as ET
from collections import Counter
OUT=ROOT/'docs/ib-maths-reviews';OUT.mkdir(exist_ok=True)
semantic_file=OUT/'aa-hl-high-risk-legacy-review.json'
SEMANTIC={r['id']:r for r in json.loads(semantic_file.read_text(encoding='utf8'))} if semantic_file.exists() else {}
FIXES={}
def steps(*ss):return [dict(code=c,text=z) for c,z in ss]
def assign(q,parts):
 q['parts']=[dict(label=chr(97+j),prompt=p,marks=len(ss)) for j,(p,ss) in enumerate(parts)]
 q['markScheme']=[dict(part=chr(97+j),steps=steps(*ss)) for j,(p,ss) in enumerate(parts)]
 q['marks']=sum(p['marks'] for p in q['parts'])
def fix(q,z):FIXES.setdefault(q['id'],[]).append(z)
def unicode_repair(z):
 chars='αβγδθλμπφωσΣΔ√∞≤≥≠≈±×÷→−–—’‘“”ôé°²³π'
 for repeat in range(2):
  for ch in chars:
   for encoding in ('cp1252','latin1'):
    try:bad=ch.encode('utf8').decode(encoding)
    except UnicodeError:continue
    z=z.replace(bad,ch)
 return z
def walk(obj):
 if isinstance(obj,str):return unicode_repair(obj)
 if isinstance(obj,list):return [walk(v) for v in obj]
 if isinstance(obj,dict):return {k:walk(v) for k,v in obj.items()}
 return obj
def code(q):
 c=q['collectionId'];sub=q['subtopic'].lower();z=(q['stem']+' '+str(q['parts'])+' '+str(q['markScheme'])).lower();title=q['title'].lower()
 if c=='number-algebra':
  if 'complex' in sub:
   return '1.14' if any(v in z for v in ['roots','de moivre','z^','powers','conjugate pair']) else ('1.13' if any(v in z for v in ['polar','argument','e^{i']) else '1.12')
  if 'counting' in sub:return '1.10'
  if 'system' in sub:return '1.16'
  if 'proof' in sub:return '1.15' if any(v in z for v in ['induct','contradiction','counterexample']) else '1.6'
  if 'binomial' in sub:
   return '1.11' if 'partial fractions' in title else ('1.10' if any(v in z for v in ['fractional','negative index','convergence','valid for','|x|','|2x|','|4x|','sqrt','approximation','binomial series']) else '1.9')
  if 'financial' in sub:return '1.4'
  if 'logarithm' in sub:return '1.7'
  if 'series' in sub:return '1.8' if 'infinity' in z or 'convergen' in z else ('1.2' if 'arithmetic' in z and 'geometric' not in z else '1.3')
 if c=='functions':
  if 'modulus' in sub:return '2.16'
  if 'polynomial' in sub:return '2.12'
  if 'discriminant' in sub:return '2.7'
  if 'linear' in sub:return '2.1'
  if 'quadratic' in sub:return '2.6'
  if 'rational' in sub:return '2.13' if any(v in z for v in ['oblique','x^2','x^{2}','x**2','x^{3}','x^3']) else '2.8'
  if 'transformation' in sub:return '2.16' if re.search(r'f\([^)]*(?:2x|3x|4x|2 x|3 x)[^)]*[+-]',z) or 'modulus' in z or '|f' in z else '2.11'
  if 'exponential' in sub:return '2.10' if 'solve' in z else '2.9'
  if 'inverse' in sub or 'composite' in sub:return '2.14' if any(v in z for v in ['restrict','even function','odd function','self-inverse']) else '2.5'
  return '2.3'
 if c=='geometry-trigonometry':
  if any(v in sub for v in ['plane','line-plane']):return '3.18' if any(v in z for v in ['intersect','angle','distance','reflect','perpendicular']) else '3.17'
  if any(v in sub for v in ['vector','skew','closest','perpendicular to']):
   if any(v in sub for v in ['product','area']):return '3.16'
   if any(v in sub for v in ['scalar','parallelogram']):return '3.13'
   if any(v in sub for v in ['line','motion','closest']):return '3.15' if 'skew' in z or 'intersect' in z else '3.14'
   return '3.12'
  if any(v in sub for v in ['inverse','reciprocal']):return '3.9'
  if any(v in sub for v in ['compound','repeated angle','triple-angle','identit']):return '3.10'
  if 'geometric series' in sub or 'sequences' in sub:return '1.8'
  if 'related rates' in sub:return '5.14'
  if 'optimization' in sub:return '5.14'
  if 'equation' in sub or 'inequalit' in sub:return '3.8'
  if any(v in sub for v in ['graph','periodic','modelling','transform','ferris','spring','circle modelling']):return '3.7'
  if 'ambiguous' in sub:return '3.5'
  if any(v in sub for v in ['circle','sector','grazing']):return '3.4'
  if 'exact' in sub:return '3.5'
  if 'three-dimensional' in sub:return '3.1'
  return '3.3'
 if c=='statistics-probability':
  if 'continuous' in sub:return '4.14'
  if 'discrete' in sub:return '4.14' if any(v in z for v in ['variance','var(','e(x^2)','e(x^{2})']) else '4.7'
  if 'binomial' in sub:return '4.8'
  if 'bivariate' in sub:return '4.10' if 'x on y' in z else '4.4'
  if 'normal' in sub:return '4.12' if any(v in z for v in ['unknown','find the mean','find $\\mu','find $\\sigma','find the standard deviation','find both','percentiles']) else '4.9'
  if 'descriptive' in sub:return '4.2' if any(v in z for v in ['boxplot','ogive','cumulative','quartile']) else '4.3'
  return '4.13' if any(v in z for v in ['bayes','supplier','machine','chosen bag','chosen die']) else '4.6'
 if c=='calculus-1':
  if 'first principles' in sub or 'higher' in sub:return '5.12'
  if 'hôpital' in sub:return '5.13'
  if 'implicit' in sub or 'related' in sub:return '5.14'
  if 'kinematic' in sub:return '5.9'
  if 'optimization' in sub:return '5.14' if any(v in z for v in ['implicit','rate','endpoint','semicircle','cone']) else '5.8'
  if 'stationary' in sub:return '5.8'
  if 'trigonometric' in sub:return '5.15' if any(v in z for v in ['arcsin','arccos','arctan','sec','cot','cosec']) else '5.6'
  if 'tangent' in sub:return '5.4'
  if 'inverse' in sub:return '5.6'
  return '5.7' if 'graph' in sub else '5.6'
 if c=='calculus-2':
  if 'differential' in sub:return '5.18'
  if 'maclaurin' in sub:return '5.19'
  if 'volume' in sub:return '5.17'
  if 'by parts' in sub or 'by substitution' in sub:return '5.16'
  if 'improper' in sub:return '5.16'
  if 'kinematic' in sub:return '5.9'
  return '5.15' if any(v in z for v in ['arctan','arcsin','arccos','partial fraction','sec^','cot']) else ('5.16' if any(v in z for v in ['by parts','substitution $u','substitution $t','let $u=']) else '5.11')
 raise ValueError(q['id'])
def extra_hl(q,k):
 z=json.dumps([q['stem'],q['parts'],q['markScheme']],ensure_ascii=False).lower()
 # Highest actual demand overrides a superficially SL topic label.
 if re.search(r'arcsin|arccos|arctan|\\sec|\\cot|\\cosec',z) and q['collectionId'].startswith('calculus'):return '5.15'
 if 'induction' in z and q['collectionId'] not in ('functions','statistics-probability'):return '1.15'
 if any(v in z for v in ['maclaurin','l’hôpital','lhopital']):return '5.19' if 'maclaurin' in z else '5.13'
 if any(v in z for v in ['implicit differentiation','differentiate implicitly']):return '5.14'
 if q['collectionId']=='statistics-probability' and any(v in z for v in ['density','variance of x','var(x)','\\operatorname{var}']):return '4.14' if 'binomial' not in q['subtopic'].lower() else '4.8'
 return k
def tank_svg():
 O=(250,150);r=110;bottom=(250,260);gmax=3*math.pi/4
 def edge(g,left):return (O[0]+(-1 if left else 1)*r*math.sin(g),O[1]+r*math.cos(g))
 lt=edge(gmax,True);rt=edge(gmax,False);le=edge(2*math.pi/3,True);re0=edge(math.pi/3,False)
 e=['<rect width="500" height="310" fill="white"/>']
 for pt,left in [(le,True),(re0,False)]:
  e.append(f'<path d="M250 260 A110 110 0 0 {1 if left else 0} {pt[0]:.3f} {pt[1]:.3f} L250 {pt[1]:.3f} Z" fill="#cde7f2"/>')
 e +=[f'<path d="M{lt[0]:.3f} {lt[1]:.3f} A110 110 0 1 0 {rt[0]:.3f} {rt[1]:.3f} Z" fill="none" stroke="#7a1f24" stroke-width="3"/>',line((250,lt[1]),bottom)]
 e +=[line(O,le,'#777777'),line(O,re0,'#777777'),txt((256,146),'O'),txt((75,90),'Left: β = 2π/3'),txt((348,206),'Right: α = π/3'),txt((190,285),'Radius 1.5 m'),txt((155,48),'Maximum angle 3π/4')]
 return svg(e,500,310)
ledger=[]
for coll,total in COUNTS.items():
 f=ROOT/'content/ib/math-aa-hl'/f'{coll}.json';items=json.loads(f.read_text(encoding='utf8'))
 assert len(items)==total+20,(coll,len(items))
 for q in items:
  original=json.dumps(q,ensure_ascii=False,sort_keys=True);repaired=walk(q)
  if repaired!=q:q.clear();q.update(repaired);fix(q,'Repaired UTF-8 text that had been mis-decoded as a legacy character encoding.')
  j=q['number']
  if coll=='number-algebra' and j==133:
   q['title']='Assigning distinct volunteers to labelled booths';q['stem']='Twelve labelled booths form three rows of four. Twelve distinct volunteers, including Asha and Ben, each occupy one booth.'
   assign(q,[('Find the number of assignments when Asha and Ben are both in the front row.',[M(r'Place Asha and Ben in $4\times3=12$ ordered ways.'),M(r'Arrange the other ten distinct volunteers in the remaining booths in $10!$ ways.'),A(rf'$12\times10!={12*math.factorial(10)}$.')]),('Now both must be in the middle row and non-adjacent, or both in the back row with at least two booths between them. Find the number of assignments.',[A(r'The middle row permits 6 ordered pairs; the back row permits 2.'),M(r'The cases are disjoint; multiply their total of 8 pairs by $10!$.'),A(rf'$8\times10!={8*math.factorial(10)}$.')])]);fix(q,'Replaced explicitly excluded identical-object permutations with all-distinct assignments. Ordered named positions enumerated independently (12, 6 and 2).')
  if coll=='calculus-1' and j==74:
   q['title']='A quadratic from a tangent condition';q['subtopic']='Tangents and normals';q['stem']=r'Let $f(t)=at^2+bt$. Its graph passes through $(3,4)$ and has tangent gradient 1 there. Find a and b.'
   q['markScheme']=[dict(part='',steps=steps(M(r'Substitute the point in $f$.'),A(r'$9a+3b=4$.'),M(r'Differentiate: $f\prime(t)=2at+b$.'),A(r'The gradient condition gives $6a+b=1$.'),M('Solve the two linear equations.'),A(r'$a=-1/9$, $b=5/3$.')))];fix(q,'Removed an examination-excluded continuity/differentiability test; the equivalent point and tangent conditions retain the intended linear-system reasoning. Both conditions checked exactly.')
  if coll=='calculus-1' and j==93:
   assign(q,[(r'Find $f\prime(5)$ and $f(5)$.',[A(r'$f\prime(5)=2$ from the tangent gradient.'),M(r'Substitute x=5 in $L_1$.'),A(r'$f(5)=13$.')]),(r'Show that the tangent gradient of g at P is 8.',[M(r'The chain rule gives $g\prime(x)=2x f\prime(x^2+1)$.'),A(r'At x=2 this becomes $g\prime(2)=4f\prime(5)=4(2)$.'),R('This evaluates to 8, establishing the given result by a valid chain-rule calculation.')]),(r'The tangent $L_2$ to g at P meets $L_1$ at Q. Find the y-coordinate of Q.',[A(r'$g(2)=f(5)=13$, so $P=(2,13)$.'),M(r'Use the point and gradient in the point-gradient equation.'),A(r'$L_2:y-13=8(x-2)$, equivalently $y=8x-3$.'),M(r'Equate $2x+3=8x-3$.'),A(r'$x_Q=1$.'),A(r'$y_Q=5$.')])]);fix(q,'Removed repeated gradient awards and equivalent-form tangent double credit; 17 marks revised to 12 distinct awards (3+3+6). The given gradient earns reasoning for establishing it, not accuracy for copying it.')
  if coll=='calculus-1' and j==22:
   q['diagramSvg']=q['diagramSvg'].replace('x="548.40" y="136.40"','x="374.40" y="128.40"').replace('x="492.80" y="216.86"','x="350.80" y="210.86"').replace('x="548.40" y="205.89"','x="385.40" y="193.89"');fix(q,'Moved graph labels inside the viewBox. Cubic derivative, quadratic roots 3 and 7, and acceleration line checked for mutual consistency.')
  if coll=='calculus-1' and j==120:
   q['diagramSvg']=tank_svg();fix(q,'Rebuilt truncated-circle SVG with Python trigonometric coordinates. Top chord is gamma=3pi/4, left sample beta=2pi/3, right alpha=pi/3; half-segment area, 2764 L, 2.96296e-4 rad/s and 12 min independently checked.')
  if coll=='calculus-2' and j==129:
   q['stem']=r'For $b>0$, let $J(b)=\int_0^b x^4e^{-2x}dx$. Define $I=\lim_{b\to\infty}J(b)$ if this finite limit exists.'
   q['title']='A finite integral followed by a limit';q['subtopic']='Integration by parts';fix(q,'Expressed the improper-integral task explicitly as a finite integral and limit, using examined integration-by-parts and limit techniques rather than requiring unfamiliar notation.')
  if coll=='geometry-trigonometry' and j in (158,168):
   if j==158:
    q['markScheme'][0]['steps']=steps(M('Take the cross product of the two plane directions.'),A(r'$\mathbf n=(16,-7,10)$.'),M('Use the fixed point to determine the Cartesian plane equation.'),A(r'$16x-7y+10z=55$.'),M(r'Use perpendicular projection $d=|\mathbf n\cdot A-55|/|\mathbf n|$.'),A(r'$d=99/(9\sqrt5)=11\sqrt5/5$.'))
   else:
    q['markScheme'][1]['steps']=steps(M('Take the cross product of the line directions.'),A(r'$\mathbf n=(-1,0,1)$.'),A(r'The joining vector is $\mathbf q-\mathbf p=(1,1,-2)$.'),M('Project the joining vector onto the common normal.'),A(r'$D=|(\mathbf q-\mathbf p)\cdot\mathbf n|/|\mathbf n|$.'),A(r'$D=3/\sqrt2=3\sqrt2/2\approx2.12$.'))
   for p in q['parts']:p['marks']=sum(int(z['code'][1:]) for g in q['markScheme'] if g['part']==p['label'] for z in g['steps'] if z['code']!='AG')
   q['marks']=sum(int(z['code'][1:]) for g in q['markScheme'] for z in g['steps'] if z['code']!='AG')
   fix(q,'Removed a second award for writing the same distance in an equivalent exact form; one final accuracy criterion remains.')
  if coll=='calculus-2' and j==143:
   q['markScheme'][1]['steps']=steps(A(r'At n=0 the formula equals f, establishing the base case.'),M(r'Assume the formula for n=k.'),M(r'Differentiate the assumed expression using the chain rule.'),A(r'The new multiplier is 2k+1 and new exponent is -k-3/2.'),A(r'$\frac{(2k)!(2k+1)}{2^k k!}=\frac{(2k+2)!}{2^{k+1}(k+1)!}$.'),R('This is the formula with n=k+1; the base case and inductive step prove it for all non-negative integers.'))
   q['markScheme'][2]['steps']=steps(M(r'Use the Maclaurin coefficients from the previously derived derivatives.'),A(r'$f(x)=1+x+\frac32x^2+O(x^3)$.'),A(r'$\cos(mx)=1-m^2x^2/2+O(x^4)$.'),M(r'The product coefficient gives $3/2-m^2/2=-3$.'),A(r'$m=3$ or $m=-3$.'))
   for p in q['parts']:p['marks']=len(next(g['steps'] for g in q['markScheme'] if g['part']==p['label']))
   q['marks']=sum(p['marks'] for p in q['parts']);fix(q,'Condensed induction and series steps into distinct awards; no fresh accuracy awards for repeating derivative data already obtained. 21 marks revised to14 (3+6+5).')
  if coll=='statistics-probability' and j==148:
   q['stem']=r'$A\sim N(0,1)$. Consider $x^2+2Ax+9=0$.'
   pcond=norm.sf(3.25)/norm.sf(3)
   assign(q,[(r'Find the values of A for which the equation has two distinct real roots.',[M(r'The discriminant requires $(2A)^2-36>0$.'),A(r'$|A|>3$.')]),(r'Find the probability that there are two distinct real roots.',[M(r'$P(|A|>3)=P(A<-3)+P(A>3)$.'),A(r'By normal symmetry this is $2[1-\Phi(3)]$.'),A(rf'${N(2*norm.sf(3))}$.')]),(r'Given two distinct real roots, find the probability that the root with smaller absolute value has absolute value less than 2.',[R('The root product is 9, so the roots have the same sign.'),M(r'Let their absolute values be t and 9/t, with $0<t<3$.'),A(r'$2|A|=t+9/t$.'),M(r'Differentiate $g(t)=(t+9/t)/2$.'),A(r'$g\prime(t)=1/2-9/(2t^2)<0$ for $0<t<3$.'),R(r'Thus t<2 is equivalent to $|A|>g(2)=13/4$.'),M(r'The required conditional probability is $P(|A|>13/4)/P(|A|>3)$.'),A(rf'The numerator and denominator are ${N(2*norm.sf(3.25))}$ and ${N(2*norm.sf(3))}$; use unrounded values.'),A(rf'The probability is ${N(pcond)}$.')])]);fix(q,'Changed constant4 to9 and conditional threshold1 to2 to remove mathematical duplication withFN129 while retaining ID and source mapping. Discriminant threshold3, conditional threshold13/4 and normal tail ratio independently recalculated.')
  if coll=='statistics-probability' and j==149:
   threshold=next(k for k in range(4,100) if binom.sf(3,k,1/3)>.5)
   q['stem']=r'Each packet independently contains a collectible with probability $1/3$. Let X be the number of packets opened up to and including the fourth collectible.'
   assign(q,[(r'Find $P(X=4)$ and $P(X=5)$.',[A(r'$P(X=4)=(1/3)^4=1/81$.'),M('For X=5, exactly three of the first four packets contain a collectible, followed by a final collectible.'),A(r'$P(X=5)=\binom43(1/3)^4(2/3)=8/243$.')]),(r'Show that $P(X=n)=\frac{(n-1)(n^2+an+b)}{486}(2/3)^{n-4}$ for $n\ge4$, and find a,b.',[R('The first n-1 packets must contain exactly three collectibles.'),M(r'There are $\binom{n-1}3$ choices of their positions.'),A(r'$P(X=n)=\binom{n-1}3(1/3)^4(2/3)^{n-4}$.'),A(r'$=\frac{(n-1)(n-2)(n-3)}{486}(2/3)^{n-4}$.'),R(r'Since $(n-2)(n-3)=n^2-5n+6$, the required constants are a=-5,b=6.')]),(r'For $n\ge5$, simplify $P(X=n)/P(X=n-1)$.',[M('Divide the consecutive probability formulas.'),A(r'The polynomial ratio is $(n-1)/(n-4)$ after cancellation.'),A(r'The remaining power ratio is $2/3$.'),A(r'$P(X=n)/P(X=n-1)=2(n-1)/[3(n-4)]$.')]),('Find every mode of X, justifying your answer.',[M('Compare the consecutive probability ratio with 1.'),A(r'$2(n-1)>3(n-4)$ gives n<10, so the probabilities increase through n=9.'),A('At n=10 the ratio is 1; probabilities at 9 and 10 are equal.'),R('For n>10 the ratio is below1, so probabilities decrease thereafter.'),A('The modes are 9 and 10.')]),(r'Find the least integer N for which the probability of at least four collectibles in N packets exceeds 0.5.',[M(r'Let $Y\sim B(N,1/3)$ and require $P(Y\ge4)>0.5$.'),A(rf'At N={threshold-1} and N={threshold}, the probabilities are ${N(binom.sf(3,threshold-1,1/3))}$ and ${N(binom.sf(3,threshold,1/3))}$ respectively.'),R(rf'Adding trials cannot reduce the event probability, so the least N is ${threshold}$.')])]);fix(q,'Changed success probability1/4 to1/3 to remove duplication withNA227. Recalculated entire probability law, coefficient denominator 486, adjacent modes9/10 and least sample-size tail threshold.')
  if j<=total:
   q['syllabusCode']=extra_hl(q,code(q));q['level']='ahl' if q['syllabusCode'] in AHL else 'sl';q['examStyle']='extended-response' if q['marks']>=9 else 'short-response'
  # Exact totals and SVG parsing cover every record; they do not certify the mathematics.
  award=sum(int(z['code'][1:]) for g in q['markScheme'] for z in g['steps'] if z['code']!='AG');assert award==q['marks'],q['id']
  if q['parts']:
   assert sum(p['marks'] for p in q['parts'])==award,q['id']
   for p in q['parts']:assert sum(int(z['code'][1:]) for g in q['markScheme'] if g['part']==p['label'] for z in g['steps'] if z['code']!='AG')==p['marks'],q['id']
  for key in ['diagramSvg','markSchemeDiagramSvg']:
   if key in q:
    ET.fromstring(q[key]);assert not re.search(r'<(?:style|use|image|script)\b|(?:href|src)\s*=|url\s*\(',q[key],re.I),q['id']
  for key in ['stem']:
   assert not re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]',q[key]),q['id']
  ledger.append(dict(id=q['id'],origin='legacy' if j<=total else 'original addition',syllabusCode=q['syllabusCode'],level=q['level'],markTotal=award,partTotals='checked',sourceMapping='retained' if j<=total else 'independent practice',scope='Legacy author assertions replayed; primary official-code classification uses deterministic content rules and the listed manual corrections. Fresh independent semantic coverage is limited to named high-risk entries; prior cross-review reports retain their stated coverage.' if j<=total else 'Individually authored and checked; see collection additions ledger and root independent review.',independentSemanticReview=SEMANTIC.get(q['id']),corrections=FIXES.get(q['id'],[]),recordSha256=hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=False).encode()).hexdigest()))
 f.write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(OUT/'aa-hl-record-review-ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(OUT/'aa-hl-corrections.json').write_text(json.dumps(FIXES,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(total=len(ledger),legacy=962,additions=120,corrections=len(FIXES),levels=dict(Counter(v['level'] for v in ledger))),indent=2))
