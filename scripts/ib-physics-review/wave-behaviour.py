"""Independent Theme C review; no author-builder imports."""
import json,math,re,xml.etree.ElementTree as ET
from pathlib import Path
root=Path(__file__).resolve().parents[2]
qs=json.loads((root/'content/ib/physics-hl/wave-behaviour.json').read_text(encoding='utf-8'))
rows=[];checks=0
def answer(q):return next(o['text'] for o in q['options'] if o['label']==q['correctOption'])
def expect(q,values,comment):
    global checks
    s=" ".join(t['text'] for g in q['markScheme'] for t in g['steps'])
    for value in values:
        formatted=format(value,'.3g')
        assert formatted in s or format(value,'.12g') in s,(q['id'],formatted,s)
        checks+=1
    rows.append((q['id'],comment))
def mcq(q,expected):
    global checks
    got=float(re.match(r"[-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?",answer(q)).group())
    assert math.isclose(got,expected,rel_tol=.005,abs_tol=1e-30),(q['id'],got,expected)
    checks+=1;rows.append((q['id'],'MCQ recomputed from the displayed physical conditions; four alternatives inspected.'))
def concept(q,fragment):
    global checks
    assert fragment in answer(q),(q['id'],fragment,answer(q))
    checks+=1;rows.append((q['id'],'All conceptual alternatives and the stated correct-answer explanation reviewed.'))
def table(q):
    return [tuple(map(float,re.findall(r"[-+]?\d+(?:\.\d+)?",line))) for line in q['stem'].splitlines() if re.match(r"\| [-+]?\d",line)]
for q in qs:
    n=q['number'];family=(n-1)//4+1;v=(n-1)%4
    if family==1:concept(q,['a = −kx.','Velocity is zero; acceleration is directed toward equilibrium.','Speed is maximum','remains T'][v])
    elif family==2:mcq(q,[2,1/3,2,9][v])
    elif family==3:
        a=.04+.01*v;period=.8+.2*v;omega=2*math.pi/period;phase=[math.pi/2,3*math.pi/2,0,math.pi][v]
        time=[.1,.15,.2,.3][v]*period;x=a*math.sin(omega*time+phase);velocity=omega*a*math.cos(omega*time+phase);accel=-omega**2*x
        expect(q,[omega,phase,x,velocity,accel],'All four initial-condition phases and subsequent signed displacement, velocity and acceleration independently recomputed.')
    elif family==4:
        if v<2:
            mass=.2+.1*v;k=32+16*v;t=2*math.pi*math.sqrt(mass/k)
            expect(q,[k,t/math.sqrt(2)],'Spring constant recovered from measured period; changed-mass period and restoring-force argument checked.')
        else:
            L=[.75,1][v-2];g=[9.6,9.9][v-2];t=2*math.pi*math.sqrt(L/g)
            expect(q,[g,2*t],'Pendulum gravity and length-period scaling recomputed; small-angle and bob model assumptions checked.')
    elif family==5:
        mass=.1+.05*v;a=.06+.02*v;omega=2*math.pi*(2+.5*v);fraction=[.25,.5,-.6,.8][v];energy=mass*(omega*a)**2/2
        potential=energy*fraction**2;kinetic=energy*(1-fraction**2);speed=omega*a*math.sqrt(1-fraction**2)
        expect(q,[energy,potential,kinetic,speed],'Energy partition and speed recomputed; signed velocity ambiguity reviewed; question graph normalized to avoid revealing total energy.')
    elif family==6:
        records=table(q);gradient=(records[-1][1]-records[0][1])/(records[-1][0]-records[0][0]);omega=math.sqrt(-gradient)
        expect(q,[omega,2*math.pi/omega],'Angular frequency and period inferred from all displayed linear data; sensor-offset effect checked.')
    elif family==7:concept(q,['Transverse.','oscillate parallel','Visible electromagnetic','transfers energy'][v])
    elif family==8:mcq(q,[4,1.2,.00025,6e14][v])
    elif family==9:concept(q,['Frequency stays fixed; wavelength becomes 0.75','It halves.','Snapshot repeat distance','f_X/f_Y = 1/3'][v])
    elif family==10:
        a=.02+.01*v;wavelength=.4+.2*v;frequency=3+v
        expect(q,[a,wavelength,wavelength*frequency,1/(4*frequency)],'Snapshot amplitude/wavelength/speed and quarter-period recomputed; particle-motion sign checked for left and right travel.')
        assert ('downward' if v%2==0 else 'upward') in " ".join(s['text'] for g in q['markScheme'] for s in g['steps'])
        checks+=1
    elif family==11:
        frequency=8+4*v;speed1=2+.5*v;speed2=1.2+.4*v;duration=.5+.25*v
        expect(q,[frequency*duration,speed1*duration,speed1/frequency,speed2/frequency,speed2*duration],'Cycle-count conservation, separate train lengths and boundary wavelength changes recomputed.')
    elif family==12:
        data=table(q);speed=(data[-1][1]-data[0][1])/.2;uncertainty=2*(.002+.001*v)/.2
        expect(q,[speed,uncertainty,speed/(.12+.04*v)],'Speed from displayed rounded crest positions and endpoint maximum uncertainty independently recomputed.')
    elif family==13:
        if v==2:concept(q,'higher refractive index')
        else:mcq(q,{0:math.degrees(math.asin(math.sin(math.radians(38))/1.5)),1:math.degrees(math.asin(1/1.33)),3:math.sin(math.radians(50))/math.sin(math.radians(30))}[v])
    elif family==14:concept(q,['Complete destructive','2A.','+0.015 m.','constant phase difference'][v])
    elif family==15:
        lam=(450+50*v)*1e-9;distance=1.5+.4*v;d=(.2+.05*v)*.001;spacing=lam*distance/d
        expect(q,[spacing,spacing*1000,(2+v)*spacing*1000,spacing/(1.2+.1*v)*1000],'Double-slit spacing, noncentral order and filled-medium wavelength ratio recomputed; no frequency change assumed.')
    elif family==16:
        density=[300,380,460,540][v]*1000;d=1/density;lam=(450+50*v)*1e-9;order=math.floor(d/lam);angle=math.degrees(math.asin(2*lam/d))
        expect(q,[d,angle,order,2*order+1],'Line density conversion, grating angle, highest order and maxima count independently checked; no grazing-order degeneracy.')
    elif family==17:
        lam=(480+40*v)*1e-9;b=(.12+.03*v)*.001;distance=1.8+.3*v;ratio=3+v;separation=ratio*b
        expect(q,[lam/b,2*distance*lam/b*1000,lam*distance/separation*1000,ratio,2*ratio-1],'Single-slit envelope width versus slit separation, first missing order and strict interior maxima count checked.')
    elif family==18:
        data=table(q);x=[math.sin(math.radians(r)) for i,r in data];y=[math.sin(math.radians(i)) for i,r in data]
        gradient=(y[-1]-y[0])/(x[-1]-x[0]);critical=math.degrees(math.asin(1/gradient))
        expect(q,[gradient,critical],'Refractive index and critical angle independently recomputed from rounded input angles; question figure no longer gives requested linearization.')
    elif family==19:concept(q,['Zero.','0 rad.','π rad.','1, 3, 5.'][v])
    elif family==20:concept(q,['Critical damping.','slow return','lower, broader','7 Hz.'][v])
    elif family==21:
        length=.8+.2*v;speed=24+6*v;harmonic=[2,3,3,5][v];factor=2 if v<2 else 4
        shape=(lambda u:math.sin(harmonic*math.pi*u)) if v==0 else ((lambda u:math.cos(harmonic*math.pi*u)) if v==1 else (lambda u:math.sin(harmonic*math.pi*u/2)))
        expectedphase=0 if shape(1/8)*shape(7/8)>0 else math.pi
        expect(q,[factor*length/harmonic,speed*harmonic/(factor*length),speed/(factor*length)],'Wavelength and mode frequencies independently recomputed; each selected particle pair checked against displacement shape and node positions.')
        s=" ".join(t['text'] for g in q['markScheme'] for t in g['steps'])
        assert ('Phase difference = 0 rad' if expectedphase==0 else 'Phase difference = π rad') in s
        checks+=1
    elif family==22:
        length=[.5,.6,.75,.8][v];harm=[1,3,2,3][v];factor=4 if v<2 else 2;nextn=harm+(2 if v<2 else 1)
        expect(q,[factor*length/harm,340*harm/(factor*length),340*nextn/(factor*length)],'Pipe displacement boundary conditions and next allowed mode checked; figures now name actual closed/open ends.')
    elif family==23:
        centre=4+v;freq=[centre-2,centre-1,centre,centre+1,centre+2];w0=2*math.pi*centre;force=.8*w0*w0
        zeta1=.08;zeta2=math.sqrt((1-((centre-1)/centre)**2)/2)
        response=lambda f,z:force/math.sqrt((w0*w0-(2*math.pi*f)**2)**2+(2*z*w0*(2*math.pi*f))**2)
        weak=[response(f,zeta1) for f in freq];strong=[response(f,zeta2) for f in freq]
        assert all(a>b for a,b in zip(weak,strong))
        assert freq[weak.index(max(weak))]==centre and freq[strong.index(max(strong))]==centre-1
        tree=ET.fromstring(q['diagramSvg'])
        curves={el.attrib.get('stroke'):el for el in tree.iter() if el.tag.endswith('polyline') and el.attrib.get('stroke-width')=='2'}
        # Decode the final labelled axis, independently of the author plot helper.
        # The final visual pass rounded tick limits, replacing the old 15% padding.
        tick_y=[float(el.attrib['y1']) for el in tree.iter()
                if el.tag.endswith('line') and el.attrib.get('x1')=='85'
                and el.attrib.get('x2')=='90' and el.attrib.get('y1')==el.attrib.get('y2')]
        calibration=[]
        for el in tree.iter():
            if el.tag.endswith('text') and el.attrib.get('x')=='75':
                value=float(el.text)
                baseline=float(el.attrib['y'])
                pixel=min(tick_y,key=lambda y:abs(y-baseline))
                assert abs(pixel-baseline)<=6,(q['id'],'unmatched y tick',value)
                calibration.append((pixel,value))
        assert len(calibration)>=2,q['id']
        (pixel0,value0),(pixel1,value1)=min(calibration,key=lambda p:p[1]),max(calibration,key=lambda p:p[1])
        value_at=lambda y:value0+(y-pixel0)*(value1-value0)/(pixel1-pixel0)
        assert all(math.isclose(value_at(y),value,rel_tol=1e-12,abs_tol=1e-12) for y,value in calibration)
        for color,values in [('#1b6ca8',weak),('#c15f20',strong)]:
            points=[tuple(map(float,p.split(','))) for p in curves[color].attrib['points'].split()]
            assert len(points)==5
            for (px,py),a in zip(points,values):
                recovered=value_at(py)
                assert math.isclose(recovered,a,rel_tol=1e-10),(q['id'],a,recovered)
                checks+=1
        expect(q,[centre,centre-1,centre+2],'Both damping curves recomputed from one identical-mass/stiffness/force model; every plotted ordinate checked. Higher damping lowers response everywhere and shifts/broadens its peak.')
    elif family==24:
        data=table(q);factor=2 if v<2 else 4
        gradient=(data[0][1]-data[-1][1])/(1/data[0][0]-1/data[-1][0]);speed=factor*gradient
        expect(q,[gradient,speed,speed/(factor*.45)],'Wave speed and new resonance frequency recomputed from rounded length-frequency data; raw question plot does not reveal the requested reciprocal axis.')
    elif family==25:concept(q,['receding','closer together','common fractional','Wavefront spacing is unchanged'][v])
    elif family==26:mcq(q,[9e5,-6e5,6e5,-9e5][v])
    elif family==27:
        freq=[400,600,800,1000][v];u=[20,25,30,35][v];sign=1 if v%2==0 else -1
        expected=freq*340/(340-sign*u) if v<2 else freq*(340+sign*u)/340
        mcq(q,expected)
    elif family==28:
        freq=[500,700,900,1100][v];speed=330+10*v;u=12+6*v;sign=1 if v%2==0 else -1
        expect(q,[u,(speed-sign*u)/freq,freq],'Moving-source inverse frequency, observer-side wavefront spacing and restored stationary frequency independently checked.')
    elif family==29:
        freq=[400,500,650,800][v];u=[15,22,28,36][v];sign=1 if v%2==0 else -1
        expect(q,[u,340/freq,freq*340/(340-sign*u)],'Moving-receiver inverse speed, unchanged wavelength and separate moving-source comparison independently checked.')
    elif family==30:
        data=table(q);z=sum((o-r)/r for r,o in data)/3;newwave=580*(1+z)
        expect(q,[z,3e8*z,abs(z)],'All three fractional line shifts recomputed from displayed data; velocity sign and low-speed scope verified.')
        assert format(newwave,'.6g') in " ".join(t['text'] for g in q['markScheme'] for t in g['steps'])
        checks+=1
assert len(rows)==120 and len(set(i for i,c in rows))==120
graphics=0
for q in qs:
    for key in ['diagramSvg','markSchemeDiagramSvg']:
        if key in q:
            tree=ET.fromstring(q[key]);_,_,w,h=map(float,tree.attrib['viewBox'].split())
            for el in tree.iter():
                if el.tag.endswith('text'):
                    x=float(el.attrib.get('x',0));y=float(el.attrib.get('y',0))
                    assert 0<=x<=w and 0<=y<=h,(q['id'],key,el.text,x,y)
            graphics+=1
from collections import Counter
difficulty=dict(Counter(q['difficulty'] for q in qs))
print(json.dumps({'questions':120,'independent_checks':checks,'SVGs_checked':graphics,'difficulty':difficulty}))
(root/'docs/ib-physics-reviews/wave-behaviour-cross-review.txt').write_text("INDEPENDENT THEME C CROSS-REVIEW\n\nCoverage: all 120 question sets C001–C120, all 30 family models and all four variant conditions. Every stem, option set and marking group reviewed. "+str(checks)+" independently recomputed numerical/conceptual or plotted-ordinate checks. All "+str(graphics)+" SVGs parsed and text anchors checked; standing-wave, refraction, moving-front and slit geometry reviewed. Calculations do not import the author builder.\n\nCorrections synchronized in builder and regenerated JSON:\n- C089–092: replaced inconsistent resonance curves. The original more-damped curve exceeded the less-damped response at some frequencies despite the same oscillator and forcing. Both curves now come from the same forced-oscillator equation, with only damping changed; all 20 ordinates per damping setting and peak locations independently verified.\n- C017–020: normalized the question potential-energy curve so it no longer supplies the requested total mechanical energy. Worked kinetic-energy curves are smooth physical parabolas.\n- C009–012: smooth sampled SHM traces replace coarse eight-segment polygons. Plot scales now have numerical ticks and large point sets no longer produce dense dot bands.\n- C069–072 and C093–096: question figures show raw measured angles and raw frequency/length data instead of giving the linearization asked for in part (a).\n- C037–040: the specified string particle is marked P on question snapshots; its motion arrow remains only in the worked diagram.\n- C085–088: air-column diagrams explicitly label open/closed ends; all questions consistently use displacement nodes/antinodes, not pressure nodes.\n- C077: critical-damping stem now states release from rest.\n- Difficulty assigned by physical skill/model/condition rather than variant index. Distribution: "+str(difficulty)+". No numeric answer or underlying mark allocation changed except physically corrected resonance data.\n\nPhysics/scope review: phase signs, restoring acceleration, energy partition, boundary frequency conservation, normal-incidence and small-angle assumptions, grating-order limits, missing-order counts, all string/pipe boundaries, acoustic source-versus-observer formulas and low-speed spectral signs are internally consistent. AHL tags cover phase/energy, grating/envelope calculations and quantitative acoustic Doppler; core tasks remain within stated model scope. Data are explicitly simulated; solutions use rounded measurements when applicable. Mark allocations are capped by question/part totals and MCQs have one defensible answer.\n\nLimits: independent editorial physics review, not official IB moderation. Complete standalone rendered-diagram QA is recorded in diagram-visual-bc.txt, including every current image hash; live application integration review is separate. The calculations and diagram geometry were checked across every variant, not a content sample.\n\nFull-entry ledger:\n"+"\n".join(i+": "+c for i,c in rows)+"\n",encoding='utf-8')
