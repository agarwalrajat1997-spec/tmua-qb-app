from aa_sl_core import *
def build():
 q=[]
 def add(j,i,title,sub,code,diff,calc,stem,ps,checks,**kw):q.append(rec('geometry-trigonometry','gt',j,i,title,sub,code,diff,calc,stem,ps,checks,**kw))
 for i in range(4):
  a=i+1;P=(a,-2,3);Q=(a+3,2,15);dist=13
  eq(sum((v-u)**2 for u,v in zip(P,Q)),dist**2)
  add(0,i,'A segment in three dimensions','Three-dimensional coordinate geometry','3.1','easy',False,rf'$P=({a},-2,3)$ and $Q=({a+3},2,15)$.',[
   part('Find PQ.',M(r'$PQ=\sqrt{3^2+4^2+12^2}$.'),A(r'$PQ=13$.')),
   part('Find the midpoint of PQ.',A(rf'$({frac(2*a+3,2)},0,9)$.'))], 'Distance checked by squared coordinate differences; midpoint computed componentwise; no vector algebra required.')
  r=i+3;h=4*r;l=math.sqrt(r*r+h*h);V=s.Rational(4,3)*s.pi*r**3
  eq(float(V),math.pi*r*r*h/3)
  add(1,i,'A conical container','Volume and surface area','3.1','medium',True,rf'A right circular cone has radius ${r}$ cm and perpendicular height ${h}$ cm.',[
   part('Find its volume, to three significant figures.',M(rf'$V=\frac13\pi({r})^2({h})$.'),A(rf'${n(V)}\text{{ cm}}^3$.')),
   part('Find its total surface area, including the circular base.',M(rf'Slant height $l=\sqrt{{{r}^2+{h}^2}}={n(l)}$ cm.'),M(rf'$A=\pi({r})l+\pi({r})^2$; use the unrounded l.'),A(rf'${n(math.pi*r*l+math.pi*r*r)}\text{{ cm}}^2$.'))], 'Cone formula checked against stated perpendicular height; slant length verified with Pythagoras; base included.')
  k=i+1;eq((3*k)**2+(4*k)**2,(5*k)**2)
  add(2,i,'Exact right-triangle ratios','Right-angle trigonometry','3.2','easy',False,rf'A right triangle has perpendicular sides ${3*k}$ cm and ${4*k}$ cm. Angle θ is opposite the shorter side.',[
   part('Find the hypotenuse.',M(rf'$c^2={3*k}^2+{4*k}^2$.'),A(rf'$c={5*k}$ cm.')),
   part('Find sin θ and tan θ exactly.',A(r'$\sin\theta=3/5$ and $\tan\theta=3/4$.'))], 'Integer Pythagorean triple checked; opposite and adjacent sides matched to specified angle.',diagram=triangle(4*k,3*k,90,['O','B','A']))
  A0=35+5*i;B=65;side=8+i;C=180-A0-B;bb=side*math.sin(math.radians(B))/math.sin(math.radians(A0))
  eq(bb/math.sin(math.radians(B)),side/math.sin(math.radians(A0)))
  add(3,i,'Across an inaccessible bank','The sine rule','3.2','medium',True,rf'In triangle ABC, $A={A0}^\circ$, $B=65^\circ$ and the opposite side $a={side}$ m.',[
   part('Find angle C.',A(rf'$C={C}^\circ$.')),
   part('Find side b to three significant figures.',M(rf'$b/\sin65^\circ={side}/\sin{A0}^\circ$.'),A(rf'$b={n(bb)}$ m.'))], 'Angles sum to180; sine rule ratio cross-checked; AAS information gives a unique triangle.')
  a=7+i;b=10+i;angle=45+10*i;c=math.sqrt(a*a+b*b-2*a*b*math.cos(math.radians(angle)))
  eq(c*c,a*a+b*b-2*a*b*math.cos(math.radians(angle)))
  add(4,i,'A brace between two beams','The cosine rule','3.2','easy',True,rf'Two beams AB and AC have lengths ${a}$ m and ${b}$ m, with $\angle BAC={angle}^\circ$.',[
   part('Find BC.',M(rf'$BC^2={a}^2+{b}^2-2({a})({b})\cos{angle}^\circ$.'),A(rf'$BC={n(c)}$ m.')),
   part('Explain why the positive square root is used.',R('BC is a physical length, so it must be positive.'))], 'Cosine-rule length compared with Euclidean distance of Python triangle coordinates.',diagram=triangle(a,b,angle))
  a=8+2*i;b=10+2*i;angle=30+10*i;area=.5*a*b*math.sin(math.radians(angle))
  eq(2*area/(a*b),math.sin(math.radians(angle)))
  add(5,i,'Two angles with the same triangle area','Area and inverse sine','3.2','medium',True,rf'Two sides of a triangle have lengths ${a}$ cm and ${b}$ cm. Its area is ${area:.8f}$ cm². The included angle C satisfies $0^\circ<C<180^\circ$.',[
   part('Find both possible values of C, to three significant figures.',M(rf'$\sin C=2({area:.8f})/({a}\times{b})$.'),A(rf'$C={angle}^\circ$ or $C={180-angle}^\circ$ (allow rounding from stated area).')),
   part('Explain why the two angles produce the same area.',R(r'$\sin(180^\circ-C)=\sin C$, so the area formula gives the same value for supplementary included angles.'))], 'Stated area retained to8 decimals; both inverse-sine branches substituted and checked inside (0,180).')
  d1=12+2*i;d2=9+i;bearing1=35;bearing2=125;E=d1*math.sin(math.radians(bearing1))+d2*math.sin(math.radians(bearing2));N=d1*math.cos(math.radians(bearing1))+d2*math.cos(math.radians(bearing2));dist=math.hypot(E,N);bearing=math.degrees(math.atan2(E,N))%360
  eq(dist,math.sqrt(d1*d1+d2*d2))
  add(6,i,'A two-leg navigation route','Bearings','3.3','hard',True,rf'A boat sails ${d1}$ km on a bearing of $035^\circ$, then ${d2}$ km on a bearing of $125^\circ$.',[
   part('Find its distance from its starting point.',R('The two directions differ by90°, so the displacement legs are perpendicular.'),M(rf'$d=\sqrt{{{d1}^2+{d2}^2}}$.'),A(rf'$d={n(dist)}$ km.')),
   part('Find the bearing of the final position from the start, to the nearest degree.',M(rf'East displacement ${d1}\sin35^\circ+{d2}\sin125^\circ={E:.6f}$; north displacement ${d1}\cos35^\circ+{d2}\cos125^\circ={N:.6f}$.'),A(rf'Bearing ${round(bearing):03d}^\circ$. Accept $35^\circ+\tan^{{-1}}({d2}/{d1})$ as an alternative method.'))], 'Component distance checked against right-triangle distance; bearing computed with quadrant-aware atan2 and measured clockwise from north.')
  a=8+i;b=10+i;A0=30;B1=math.degrees(math.asin(b*.5/a));B2=180-B1;C1=150-B1;C2=150-B2
  checked(C1>0 and C2>0,'two SSA triangles')
  add(7,i,'The ambiguous sine-rule case','Two possible triangles','3.5','hard',True,rf'In triangle ABC, $A=30^\circ$, $a={a}$ cm and $b={b}$ cm.',[
   part('Find the two possible values of B.',M(rf'$\sin B={b}\sin30^\circ/{a}$.'),A(rf'$B={n(B1)}^\circ$ or ${n(B2)}^\circ$.')),
   part('Find the corresponding values of C and justify that two triangles exist.',A(rf'$C={n(C1)}^\circ$ or ${n(C2)}^\circ$, matched respectively to the two B values.'),R('Both C values are positive, and each set of angles sums to180°, so both configurations form a triangle.'))], 'Both sine branches substituted into sine rule; both remaining angles are positive; correct branch pairing verified.')
  r=4+i;theta=s.pi*(i+1)/6;arc=r*theta;area=s.Rational(1,2)*r*r*theta
  eq(area,arc*r/2)
  add(8,i,'A sector with exact angle','Arc and sector measures','3.4','easy',False,rf'A sector has radius ${r}$ cm and angle ${L(theta)}$ radians.',[
   part('Find its arc length and area exactly.',M(r'$s=r\theta$ and $A=\tfrac12r^2\theta$.'),A(rf'Arc length ${L(arc)}$ cm.'),A(rf'Area ${L(area)}$ cm².')),
   part('Find the perimeter of the sector.',A(rf'${L(2*r+arc)}$ cm.'))], 'Sector area checked as one-half radius times arc; perimeter includes both radii.',diagram=sector(r,float(theta)))
  r=6+i;theta=1.1+.2*i;area=.5*r*r*(theta-math.sin(theta));chord=2*r*math.sin(theta/2)
  eq(area,.5*r*r*theta-.5*r*r*math.sin(theta))
  add(9,i,'A circular segment','Sector minus triangle','3.4','hard',True,rf'A chord cuts off the minor segment of a circle of radius ${r}$ cm. The chord subtends ${theta:g}$ radians at the centre.',[
   part('Find the length of the chord.',M(rf'$c=2({r})\sin({theta:g}/2)$, by splitting the isosceles triangle.'),A(rf'$c={n(chord)}$ cm.')),
   part('Find the area of the minor segment.',M(rf'$A=\frac12({r})^2({theta:g})-\frac12({r})^2\sin({theta:g})$.'),A(rf'$A={n(area)}$ cm².'))], 'Segment area computed independently by sector-minus-triangle; angle belowπ assures minor segment.',diagram=sector(r,theta,chord=True))
  angles=[s.Rational(5,6)*s.pi,s.Rational(7,4)*s.pi,s.Rational(4,3)*s.pi,s.Rational(5,4)*s.pi];theta=angles[i]
  eq(s.sin(theta)**2+s.cos(theta)**2,1)
  add(10,i,'Exact values around the unit circle','Unit circle','3.5','easy',False,rf'Let $\theta={L(theta)}$.',[
   part('Find sin θ and cos θ exactly.',M('Identify the reference angle and quadrant before choosing signs.'),A(rf'$\sin\theta={L(s.sin(theta))}$.'),A(rf'$\cos\theta={L(s.cos(theta))}$.')),
   part('Find tan θ exactly.',A(rf'$\tan\theta={L(s.tan(theta))}$.'))], 'Exact trigonometric values satisfy unit-circle identity and quotient relation; quadrant signs checked.')
  triples=[(3,4,5),(5,12,13),(8,15,17),(7,24,25)];a,b,c=triples[i]
  eq(a*a+b*b,c*c)
  add(11,i,'Trigonometry with a quadrant restriction','Pythagorean identity and signs','3.6','medium',False,rf'$\sin\theta={frac(a,c)}$ and $\pi/2<\theta<\pi$.',[
   part('Find cos θ and tan θ exactly, without finding θ.',M(rf'$\cos^2\theta=1-({frac(a,c)})^2={frac(b*b,c*c)}$.'),R('θ is in quadrant II, so cosine and tangent are negative.'),A(rf'$\cos\theta=-{frac(b,c)}$ and $\tan\theta=-{frac(a,b)}$.'))], 'Pythagorean triple checked; quadrant restriction selects negative cosine before quotient.')
  a,b,c=triples[i];eq(s.Rational(2*a*b,c*c)**2+s.Rational(b*b-a*a,c*c)**2,1)
  add(12,i,'Double angles from one ratio','Double-angle identities','3.6','medium',False,rf'Angle α is acute and $\sin\alpha={frac(a,c)}$.',[
   part('Find cos α.',M(r'$\cos\alpha=+\sqrt{1-\sin^2\alpha}$ because α is acute.'),A(rf'$\cos\alpha={frac(b,c)}$.')),
   part('Find sin 2α and cos 2α exactly.',M(r'$\sin2\alpha=2\sin\alpha\cos\alpha$ and $\cos2\alpha=1-2\sin^2\alpha$.'),A(rf'$\sin2\alpha={frac(2*a*b,c*c)}$ and $\cos2\alpha={frac(c*c-2*a*a,c*c)}$.'))], 'Double-angle outputs checked against exact unit-circle identity; acute condition ensures positive cosine.')
  k=i+1;eq(s.trigsimp((1-s.cos(2*x))/s.sin(x)-2*s.sin(x)),0)
  add(13,i,'A scaled double-angle identity','Identity proof','3.6','medium',False,rf'Assume $\sin x\ne0$.',[
   part(rf'Prove $\frac{{{k}(1-\cos2x)}}{{\sin x}}\equiv{2*k}\sin x$.',M(r'Use $1-\cos2x=2\sin^2x$ on the left-hand side.'),A(rf'Left side becomes $\frac{{{2*k}\sin^2x}}{{\sin x}}$.'),R(rf'Cancel one factor of $\sin x$, valid because it is nonzero, giving ${2*k}\sin x$.')),
   part('Explain why x=0 is excluded from this identity as written.',R('The original left side has denominator zero at x=0, even though the simplified right side is defined there.'))], 'Identity checked by symbolic trigonometric reduction; cancellation domain explicitly justified.')
  k=i+1;sol=[s.pi/12+j*s.pi for j in range(2*k)]+[s.pi*5/12+j*s.pi for j in range(2*k)];checked(all(s.simplify(s.sin(2*z)-s.Rational(1,2))==0 for z in sol),'trig roots')
  add(14,i,'All roots on a finite trigonometric interval','Finite-interval sine equations','3.8','medium',False,rf'Solve $\sin(2x)=\frac12$ for $0\leq x\leq{2*k}\pi$.',[
   part('Give every solution exactly.',M(rf'$0\leq2x\leq{4*k}\pi$; reference angle $\pi/6$.'),A(r'$2x=\pi/6+2n\pi$ or $2x=5\pi/6+2n\pi$ within that finite interval.'),A(rf'$x=\pi/12+n\pi$ or $x=5\pi/12+n\pi$, where $n=0,1,\ldots,{2*k-1}$. This is a finite list of ${4*k}$ solutions.'))], 'Finite root list enumerated, each substituted, endpoints checked; finite indexing does not request unrestricted general solutions.')
  shift=i*s.pi/2;roots=[shift+s.pi/3,shift+s.pi,shift+5*s.pi/3];checked(all(s.simplify(2*s.cos(z-shift)**2+s.cos(z-shift)-1)==0 for z in roots),'quadratic trig')
  add(15,i,'A quadratic in cosine','Quadratic trigonometric equations','3.8','hard',False,rf'Solve $2\cos^2(x-({L(shift)}))+\cos(x-({L(shift)}))-1=0$ for ${L(shift)}\leq x\leq{L(shift+2*s.pi)}$.',[
   part('Find all solutions exactly.',M(r'Let $u=\cos(x-\text{shift})$ and factor: $(2u-1)(u+1)=0$.'),A(r'$u=1/2$ or $u=-1$.'),M(r'The shifted angle is $\pi/3,\pi,5\pi/3$ in $[0,2\pi]$.'),A(rf'$x={L(shift+s.pi/3)}, {L(shift+s.pi)}, {L(shift+5*s.pi/3)}$.'))], 'All three roots checked in original quadratic; interval shift includes neither extra endpoints nor omitted cosine=-1 root.')
  a=i+2;b=i+1;d=1;f=lambda z:a*math.sin(b*z)+d
  add(16,i,'Features of a sinusoidal curve','Circular function graphs','3.7','medium',False,rf'$f(x)={a}\sin({b}x)+1$.',[
   part('State the amplitude, period and range.',A(rf'Amplitude ${a}$ and period ${frac(2,b)}\pi$.'),A(rf'Range $[{1-a},{1+a}]$.')),
   part(rf'Sketch one full cycle for $0\leq x\leq{frac(2,b)}\pi$, labelling its maximum and minimum.',M('A smooth sine cycle starts and ends on the midline y=1, initially increasing.'),A(rf'Maximum $({L(s.pi/(2*b))},{1+a})$; minimum $({L(3*s.pi/(2*b))},{1-a})$.'),A('The graph has the correct amplitude, period and midline crossings.'))], 'Max/min coordinates evaluated exactly; Python plot uses same stated angular frequency and a full cycle.',answer_diagram=plot([f],0,2*math.pi/b,-a-1,a+3,[(math.pi/(2*b),a+1,'maximum'),(3*math.pi/(2*b),1-a,'minimum')],title='One complete cycle; x in radians'))
  low=1+i*.2;high=5+i*.2;mid=(low+high)/2;level=mid+1;eq(mid+2*math.cos(math.pi*2/6),level)
  add(17,i,'A tidal depth model','Trigonometric modelling','3.7','hard',True,rf'A harbour has maximum depth ${high:g}$ m at t=0 and minimum depth ${low:g}$ m six hours later. Depth varies sinusoidally with period12 hours.',[
   part('Write a cosine model for depth D(t).',M(rf'Midline $({high:g}+{low:g})/2={mid:g}$ and amplitude2.'),A(rf'$D(t)={mid:g}+2\cos(\pi t/6)$, with t in hours.')),
   part(rf'Find the first time after t=0 when the depth is ${level:g}$ m.',M(rf'$\cos(\pi t/6)=({level:g}-{mid:g})/2=1/2$.'),A(r'$t=2$ hours.')),
   part('State one limitation of the model.',R('Actual tides may have unequal heights or variable periods due to weather and other effects.'))], 'Extrema and first crossing substituted in model; decreasing first half-cycle guarantees first positive time.')
  b=i+1;left=-math.pi/(2*b);right=-left
  add(18,i,'One branch of tangent','Tangent graphs','3.7','medium',False,rf'Consider $y=\tan({b}x)$ for $-{frac(1,2*b)}\pi<x<{frac(1,2*b)}\pi$.',[
   part('State the vertical asymptotes and x-intercept.',A(rf'$x=-{frac(1,2*b)}\pi$ and $x={frac(1,2*b)}\pi$.'),A(r'The x-intercept is (0,0).')),
   part('Sketch the branch and state the period of the full tangent function.',M('A smooth increasing branch passes through the origin, tending to−∞ at the left asymptote and+∞ at the right.'),A(rf'Period ${frac(1,b)}\pi$.'))], 'Asymptote locations checked from cosine denominator zero; plot restricted to a single branch.',answer_diagram=plot([lambda z:math.tan(b*z)],left,right,-5,5,vlines=[left,right],title='Single tangent branch; x in radians'))
  d=20+5*i;distance=d/2;height=distance*math.sqrt(3);eq((distance+d)*math.tan(math.pi/6),height)
  tower_h=220;Ax=500-tower_h/math.tan(math.pi/6);Bx=500-tower_h/math.tan(math.pi/3)
  coords=[line((80,290),(550,290)),line((500,290),(500,70)),line((Ax,290),(500,70)),line((Bx,290),(500,70)),txt((Ax-5,315),'A'),txt((Bx-5,315),'B'),txt((495,315),'C'),txt((495,58),'T'),txt(((Ax+Bx)/2-35,340),f'AB = {d} m'),txt((Ax+30,277),'30°'),txt((Bx+22,268),'60°'),txt((65,30),'Elevation geometry',12)]
  add(19,i,'Surveying a vertical tower','Elevation and diagram construction','3.3','hard',False,rf'A and B lie on horizontal ground on the same side of the foot C of a vertical tower CT. B is ${d}$ m closer to C than A. The angles of elevation of T at A and B are $30^\circ$ and $60^\circ$.',[
   part('Draw a labelled diagram showing the observation points, tower and angles.',M('Place A,B,C in that order on one horizontal line, with CT vertical.'),A(rf'Label $AB={d}$ m and elevation angles30° at A and60° at B.')),
   part('Find the exact height of the tower.',M(rf'Let $BC=x$: $h=x\tan60^\circ=(x+{d})\tan30^\circ$.'),A(rf'$3x=x+{d}$, so $x={frac(d,2)}$.'),A(rf'$h={frac(d,2)}\sqrt3$ m.'))], 'Both tangent relations checked at solved distance; solution construction labels collinear points and elevation rays.',answer_diagram=svg(coords))
 return sorted(q,key=lambda z:z['number'])
if __name__=='__main__':save('geometry-trigonometry',build())
