"""Independent Theme D numerical review using displayed scenario inputs.
The reviewer did not call the authoring module or reuse its helper functions.
"""
import json, math, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
qs=json.loads((ROOT/'content/ib/physics-hl/fields.json').read_text(encoding='utf-8'))
expected={}
def record(n,*values):expected[n]=values
G=6.67e-11;k=8.99e9;e=1.60e-19;mp=1.67e-27
for j in range(2):
    b=30*j
    am,ar=[(3,2),(5,3)][j];record(b+1,am/ar**2)
    M,R=[(4.8e24,5.6e6),(7.2e23,3.2e6)][j];record(b+2,G*M/R**2,4*G*M/R**2)
    h=[1,2][j];record(b+3,(1+h)**-2)
    mu=[3.2e14,4.8e14][j];record(b+4,mu,mu/G)
    r=[7e6,9e6][j];record(b+5,-mu/r)
    r1,r2=[(6e6,1.2e7),(8e6,2e7)][j];m=[85,120][j];record(b+6,m*((-mu/r2)-(-mu/r1)))
    r=[8e6,1.1e7][j];record(b+7,math.sqrt(mu/r),math.sqrt(4*math.pi**2*r**3/mu)/60)
    r1,r2=[(7.5e6,1.5e7),(9e6,2.7e7)][j];m=[220,350][j];record(b+8,-mu*m/(2*r2)+mu*m/(2*r1))
    M1,M2,L=[(4e20,9e20,5e6),(9e20,16e20,7e6)][j];record(b+10,L*math.sqrt(M1)/(math.sqrt(M1)+math.sqrt(M2)))
    r0=[6e6,8e6][j];dr=1e5;record(b+12,-mu/(r0*r0-dr*dr))
    ratio=[.98,.96][j];record(b+14,math.sqrt(1/ratio))
    q1,q2,r=[(2e-9,6e-9,.12),(4e-9,9e-9,.18)][j];record(b+15,k*q1*q2/r**2)
    q,L=[(3e-9,.4),(5e-9,.6)][j];field=8*k*q/L**2;record(b+16,field,e*field)
    q,r=[(8e-9,.15),(12e-9,.24)][j];record(b+17,k*q/r,-2*e*k*q/r)
    R,V=[(.1,1800),(.15,2400)][j];record(b+19,V*R/k,V/R)
    gap,V=[(.025,150),(.04,240)][j];record(b+21,V/gap,3e-9*V)
    q,m,field=[(2e-6,.003,450),(3e-6,.004,600)][j];record(b+22,q*field,q*field/m)
    record(b+23,[7,11][j])
    slope=[.0045,.0072][j];record(b+28,slope,slope/k)
    q1,q2,r=[(5e-9,-8e-9,.25),(7e-9,-9e-9,.3)][j];record(b+29,k*q1*q2/r)
    b=60+20*j
    B,v=[(.18,2.4e6),(.24,3e6)][j];record(b+2,mp*v/(e*B),2*mp*v/(e*B))
    field,Bs,Ba,r=[(1.8e4,.06,.2,.12),(2.4e4,.08,.25,.1)][j];record(b+3,field/Bs,field/(Bs*Ba*r))
    field,u,L=[(2400,3.2e5,.12),(3200,4e5,.16)][j]
    t=L/u;vx=e*field*t/mp;record(b+4,t,.5*vx*t,math.degrees(math.atan(vx/u)))
    B,I,L,angle=[(.35,2.4,.18,60),(.42,3.2,.15,30)][j];record(b+7,B*I*L*math.sin(math.radians(angle)),B*I*L)
    r1,r2=[(4,6),(3,5)][j];record(b+9,(r2/r1)**2)
    angle=[30,60][j];N,B,A=[(80,.25,.012),(120,.18,.018)][j];record(b+11,B*A*math.cos(math.radians(90-angle)))
    turns=[60,90][j];t1,t2=[(.012,.036),(.02,.05)][j];p1,p2=[(.0012,.0036),(.002,.005)][j];record(b+12,turns*(p1-p2)/(t2-t1))
    B,L,v=[(.45,.24,3.2),(.6,.18,4.5)][j];voltage=B*L*v;record(b+13,voltage)
    R=[1.8,2.4][j];I=voltage/R;record(b+14,I,B*I*L,voltage**2/R)
    N,phi,T=[(100,.0018,.12),(150,.0012,.08)][j];record(b+16,2*math.pi*N*phi/T)
    N,B,h,w,v=[(30,.35,.12,.08,.4),(40,.28,.15,.1,.5)][j];record(b+17,N*B*h*w,N*B*h*v,w/v,3*w/v,4*w/v)
    nt,na,den=[(3,2,4),(4,3,2)][j];record(b+20,nt*na/den)

def reported_values(q):
    # Read only the published key/explanation or worked marking, never distractors.
    s=' '.join(z['text'] for g in q['markScheme'] for z in g['steps'])
    if q['questionType']=='multiple-choice':
        s+=' '+next(o['text'] for o in q['options'] if o['label']==q['correctOption'])
    pat=r'(?<![\w.])([+-]?(?:\d+(?:\.\d*)?|\.\d+))(?:\\times10\^\{([+-]?\d+)\})?'
    return [float(m[0])*10**int(m[1] or 0) for m in re.findall(pat,s)]

checks=0
for n,vs in expected.items():
    reported=reported_values(qs[n-1])
    for v in vs:
        assert any(math.isclose(v,x,rel_tol=.005,abs_tol=1e-24) for x in reported),(n,v,reported)
        checks+=1
for q in qs:
    assert q['marks']==sum(int(s['code'][1:]) for g in q['markScheme'] for s in g['steps'])
    if q['parts']:
        assert q['marks']==sum(x['marks'] for x in q['parts'])
        assert {p['label'] for p in q['parts']}=={g['part'] for g in q['markScheme']}
    if q['questionType']=='multiple-choice':
        assert len(q['options'])==4 and len({o['text'] for o in q['options']})==4
        assert q['correctOption'] in [x['label'] for x in q['options']]
    if q['syllabusCode']=='D.4':assert q['level']=='ahl'
    assert not any(ord(c)<32 and c not in '\n\r\t' for c in json.dumps(q,ensure_ascii=False))

report=f"""Independent subject review of Theme D — 100/100 records

Reviewer: Theme A author; distinct from the Theme D author.
Coverage: ib-phy-d-001 through ib-phy-d-100, including all fifty families and both numerical variants.

Method
Read the complete builder and every family, the generated record inventory, marking criteria,
all option sets, and the SVG constructions. Independently recomputed {checks} quantitative
outcomes across {len(expected)} numerical records from the displayed inputs using a separate
review script that does not import the authoring module. Compared to the stored correct
answers/marking with tolerance for their displayed three-significant-figure rounding.
Symbolic and qualitative questions were checked analytically, including all 44 MCQ keys
and plausible distractors. Verified discrete mark totals and part labels for all 100.

Physics checks
Newtonian gravity: inverse-square distance measured from centre; outward radius versus
altitude; attractive field cancellation between two sources; potential reference at infinity;
negative radial potential gradient; orbital speed/period and total energy; escape-speed ratio.
Electrostatics: vector versus scalar superposition; opposite electron force; signed work and
potential energy; conducting interiors and surface normals; charge quantisation; equipotential
direction; inverse-square data transformations.
Magnetism: right-hand rule and negative-charge reversal; current attraction/repulsion;
qvB centripetal motion; E/B selection; electric deflection and kinetic energy; isotope-radius
ratio after equal accelerating voltage.
Induction: angle to plane versus normal; flux versus flux linkage; signed Faraday law;
rod polarity; magnetic drag and electrical heating; Lenz-law current sense from the specified
viewpoint; sinusoidal phase; separate entry/exit intervals; constant linked flux; qualitative
self-induction.

Corrections applied to builder and regenerated JSON
- D002/D032: surface-field diagram now places the evaluated point on the planet surface.
- D006/D008/D036/D038: two-radius questions now show two distinct concentric radii.
- D012/D042: potential-gradient plots are zoomed to the sampled interval rather than compressing
  both readings into a narrow strip at the far edge of a large blank plot.
- D016/D046: midpoint solution uses the actual positive/negative point-charge pair and two
  parallel midpoint-field contributions; it no longer depicts a uniform parallel-plate field.
- D019/D049: precise surface potential is supplied in text, so a three-significant-figure
  numerical answer does not depend on extracting an unlabelled graph ordinate.
- D030/D060: conductor sketches distinguish a solid conductor from an empty conducting shell.
- D071/D091: explicit coil-plane and normal angles replace a generic rotating-coil sketch.
- D073/D093: open-circuit rod drawing includes a visible circuit break.
- D074/D094: closed-circuit rod drawing includes a resistor rather than an unlabelled wire.
- D078/D098: translating loop is shown in a perpendicular uniform field, with no rotation axis.
- D079/D099: self-induction uses a current-and-linked-field coil sketch rather than a rotation diagram.
- D012/D017/D020/D021 and D042/D047/D050/D051 relabelled medium: their short calculations
  do not become hard merely because they involve AHL potential content.
- Numerical formatter now emits proper LaTeX scientific notation when three-significant-figure
  formatting switches to exponent form (for example, 6.32 times 10^3 instead of 6.32e+03).
- Removed inward-acceleration arrows from question orbit sketches, keeping the given velocity.
  Coil question sketches use unknown normal angle theta and neutral setup captions; formula
  cues and self-induction explanation are reserved for marking guidance.
- Coil-scaling wording explicitly refers to coil planes perpendicular to the field; self-induction
  wording specifies changing current magnitude with direction fixed.

Scope
Checked against the corrected first-assessment-2025 IB guide boundary supplied by the syllabus
reviewer. D.4 is entirely AHL. D.1/D.2 potential/energy tasks are AHL. D.3 acceleration through
a supplied potential difference and isotope charge-to-mass tasks may remain core (B.5 work per
charge and D.3 electric acceleration); electrostatic shielding and conductor field tasks may
also remain core. No correction was needed to those classifications.

Outcome and limits
No incorrect numerical final answer, unique MCQ key, force/field direction in the explanations,
or mark total remained in this review. Numerical checks complement the analytical review;
they do not prove prose correctness. SVG semantics/directions were inspected in source. A subsequent complete D/E rendered
visual review is recorded separately in diagram-visual-de.txt, with exact hash coverage.
This review does not claim IB moderation or experimental provenance of the constructed data.

Record coverage
"""
for q in qs:
    suffix=f"{len(expected[q['number']])} recomputed numerical outcomes" if q['number'] in expected else 'symbolic/conceptual derivation checked'
    report+=f"{q['id']} | {q['syllabusCode']} | {q['title']} | {suffix}; marking, level, options and available SVG checked\n"
(ROOT/'docs/ib-physics-reviews/fields-cross-review.txt').write_text(report,encoding='utf-8')
print(f'Reviewed {len(qs)} records; {checks} independent numerical checks in {len(expected)} records.')
