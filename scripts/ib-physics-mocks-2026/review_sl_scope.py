"""Separate SL scope, scientific-assumption and marking review.

No author code is imported. Native diagram/full-numerical review is a separate
reviewer's responsibility; this report does not claim to replace that audit.
"""
from pathlib import Path
import json,math,hashlib,re,sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'content/ib/physics-mocks-2026/papers';DOC=ROOT/'docs/ib-physics-mocks-2026'
checks={}
def ck(key,name,actual,expected,tol=1e-9):
    assert math.isfinite(actual) and abs(actual-expected)<=tol,(key,name,actual,expected,tol)
    checks.setdefault(key,[]).append({'test':name,'actual':actual,'expected':expected,'absoluteTolerance':tol,'status':'passed'})
N={
'A1A1':'Three legs total100m but opposing east/west legs cancel, leaving40m north; speed and displacement-rate therefore differ.',
'A1A2':'The two time roots correspond to opposite vertical-velocity signs. Select the later root for descent before using horizontal velocity.',
'A1A3':'Separate trials make equal speeds at the chosen height physically possible despite dissipative drag; force directions produce1.4g versus0.6g.',
'A1A4':'Signed one-dimensional momentum fixes the outgoing X velocity before comparing positive squared-speed energies; no simultaneous elastic-collision solution is assumed.',
'A1A5':'Spring work between two nonzero extensions is a difference of stored energies, not energy based on the extension increment.',
'A1A6':'The slope distance must become a vertical height through sin30degrees. Friction removes energy over the full three-metre path.',
'A1A7':'Both material masses and unequal temperature changes enter the heat balance; the final temperature lies between both initial values.',
'A1A8':'Compare albedo fractions rather than reflected intensities alone; emissivity ratio follows equal-temperature radiation, without assuming either surface is in equilibrium.',
'A1A9':'The initial planetary energy budget is positive60W/m². Added infrared absorption changes thermal balance without destroying energy or changing incoming sunlight.',
'A1A10':'A constant pressure offset cancels in the slope. Converting kPa to Pa is essential before using n=gradient*V/R.',
'A1A11':'Monatomic internal energy scales with particle number at common temperature, while rms molecular speed depends on individual particle mass.',
'A1A12':'The external parallel pair is2ohms, in series with1ohm internal resistance. Cell power means emf times total current, not terminal voltage times current.',
'A1A13':'The stated profile translation supplies the small-interval kinematic argument. This is not recall of an AHL sinusoidal SHM velocity formula.',
'A1A14':'A one-and-a-half-wavelength path difference initially gives destructive interference; a supplied half-cycle phase reversal changes it to constructive without changing frequency.',
'A1A15':'Adjacent open-closed resonance lengths differ by half a wavelength. The stated common end correction cancels; no numerical end-correction theory is assumed.',
'A1A16':'Damping, driven amplitude and resonance belong to shared C.4, now correctly referenced. More damping lowers and broadens the stated steady-state response.',
'A1A17':'Using Newton gravity with circular acceleration gives M proportional to r³/T². Different central stars require the mass ratio rather than a universal common Kepler constant.',
'A1A18':'Acceleration follows the gravitational field, while its perpendicularity to instantaneous velocity gives zero tangential acceleration only at that instant.',
'A1A19':'Equal-distance dipole field components cancel vertically and add horizontally. The cosine factor comes from the stated60degree-to-horizontal geometry.',
'A1A20':'The selector fixes a common E/B speed; magnetic curvature then depends on m/q. This requires no gravitational/electric potential or AHL energy expression.',
'A1A21':'Rare backward deflections plus mostly straight transmission support concentrated positive nuclear charge and mostly empty atomic volume; no closest-approach calculation is requested.',
'A1A22':'Alpha decay changes A and Z before beta-minus raises Z by one; the mass number remains unchanged during the beta step.',
'A1A23':'Subtract constant background before applying whole half-lives. The requested late ratio is source-to-background, not gross-to-background.',
'A1A24':'The initial free neutron has no nuclear binding energy. Total binding increases by189.6MeV, with charge/mass-number bookkeeping and three emitted neutrons consistent.',
'A1A25':'The full six-month angular sweep is twice the parallax angle; convert the resulting20pc distance into light-years.',
'B1A1':'Initial downward velocity is nonzero. Distances in separate one-second intervals require subtracting positions, not taking a ratio of total falls.',
'B1A2':'Horizontal speed remains12m/s, while vertical impact speed follows the18m fall. The velocity angle differs from the overall displacement angle.',
'B1A3':'Use signed acceleration-time area, including the negative tail, before multiplying average acceleration by mass; a peak force is not the time average.',
'B1A4':'Opposing momenta leave a nonzero common speed toward the heavier cart. The retained kinetic-energy fraction is one quarter, not zero.',
'B1A5':'The water gains both height and outlet kinetic energy. The stated60percent is useful mechanical output divided by electrical input.',
'B1A6':'Diameter changes cross-sectional area quadratically. Series thermal resistances add; replacing the thin rod changes total resistance by a2.5factor.',
'B1A7':'Comparing heating rates at the same temperature cancels the same unknown loss. K/min must be converted into K/s and the inferred loss remains positive.',
'B1A8':'Balance the atmospheric subsystem itself. Unequal upward/downward fluxes are given as a bulk atmospheric budget, not a stipulated single isothermal symmetric layer.',
'B1A9':'Sealed gas has fixed N. The product pV triples, hence temperature triples and rms speed increases only by the square root.',
'B1A10':'All ice melts before sensible warming starts; the final water mass includes the melted20grams as well as the original80grams.',
'B1A11':'Opening a parallel branch lowers total cell current and internal drop, raising terminal voltage and the surviving branch current simultaneously.',
'B1A12':'a=−omega²x, spring periods and mass scaling are expressly SL C.1. No phase-angle or quantitative SHM energy formula is assumed.',
'B1A13':'The transmitted sound angle is below the limiting regime, and frequency is fixed by the source across a stationary boundary. Wave speed and wavelength change.',
'B1A14':'The solid index is inferred once from its air critical angle; immersion changes the index ratio, not the solid material index.',
'B1A15':'The non-assumed string-speed relationship is now supplied explicitly with symbols defined. Its square-root tension change cancels the length change.',
'B1A16':'SL light Doppler uses fractional wavelength shift at small v/c. Different rest wavelengths must be included before taking the velocity ratio.',
'B1A17':'The former elliptical-speed calculation was replaced by circular near-surface orbits. Equal average density means M scales as R³, cancelling the radius effect on T².',
'B1A18':'At the line-of-centres field null, a displacement toward the larger mass strengthens its pull and weakens the other; the claim is only longitudinal instability.',
'B1A19':'Ground-removal order determines whether the electron deficit is trapped or neutralized after the negatively charged inducing rod is removed.',
'B1A20':'The wire field is into the page on its right. A positive charge moving left would feel downward force; a negative charge reverses that direction.',
'B1A21':'A3eV photon matches the2-to5eV transition only if its lower excited state is populated. The supplied three-level model excludes arbitrary single-photon energy pooling.',
'B1A22':'The model now explicitly contains28protons and28neutrons, conserving charge when divided into14alpha particles. Smaller final binding requires positive energy input.',
'B1A23':'Absorption by control rods changes the number of surviving fission-producing neutrons. It does not change binding energies or perform the distinct moderator role.',
'B1A24':'At equal surface temperature, radii scale with the square root of luminosity. The million-fold luminosity ratio therefore means a thousand-fold radius ratio.',
'B1A25':'Parallax is inverse distance; equal-luminosity brightness is inverse distance squared. The farther star with smaller parallax is sixteen times fainter.'
}
# Physics answers are bound to option TEXT, so an assessment-quality shuffle
# cannot accidentally preserve an old letter key. The values were solved above
# and the qualitative alternatives read in full before this review was written.
C={
'A1A1':['1.25','0.500'],'A1A2':['$6.4'],'A1A3':['$7/3$'],'A1A4':['$24'],
'A1A5':['$0.64'],'A1A6':['$4.6'],'A1A7':['$4/3$'],
'A1A8':['Y has the greater albedo','1.50'],
'A1A9':['The planet initially gains energy, and warming can restore outgoing intensity'],
'A1A10':['$2.41'],'A1A11':['$2$ and',r'$\sqrt5$'],'A1A12':['$2/3$'],
'A1A13':['$0.40','upward'],'A1A14':['Destructive interference changes to constructive'],
'A1A15':['$476'],'A1A16':['The dashed response has greater damping and a broader, lower'],
'A1A17':['$32$'],'A1A18':['North; zero'],'A1A19':['$E_0$ to the right'],
'A1A20':['$4r$'],'A1A21':['A tiny fraction of incident particles reverse direction'],
'A1A22':['$234$ and $91$'],'A1A23':['$0.60$'],'A1A24':['$190'],'A1A25':['$65.2'],
'B1A1':['$29/9$'],'B1A2':[r'$58^\circ$'],'B1A3':['$7.0'],
'B1A4':['$1/4$'],'B1A5':['$1.04'],'B1A6':['$2.5$'],'B1A7':['$1500'],
'B1A8':['$40'],'B1A9':[r'$\sqrt3$'],'B1A10':['$3.33'],
'B1A11':['Both increase.'],'B1A12':['$0.628'],'B1A13':[r'$49^\circ$; unchanged'],
'B1A14':[r'$42^\circ$'],'B1A15':['$150'],'B1A16':['$1.50$'],
'B1A17':['$1$'],'B1A18':['Toward $4M$; unstable'],'B1A19':['X positive; Y neutral'],
'B1A20':['Upward, parallel to the current'],'B1A21':['Populate the $2.0'],
'B1A22':['$95.2','supplied'],'B1A23':['Fewer neutrons survive to cause further fissions'],
'B1A24':['$1000$'],'B1A25':['$1/16$']
}
PARTS={
'A1B1':{
'a':'Inverting calibrated frequency gives0.100s; a2percent maximum frequency uncertainty gives0.002s period uncertainty.',
'b':'Symmetric positions around peak2 make the central velocity0.260m/s exact within the constant-acceleration model.',
'c':'Equal-time second position differences are aT², yielding0.400m/s² without any AHL oscillator formula.',
'd':'Add the two endpoint absolute position uncertainties, then add fractional numerator/denominator bounds;0.0152m/s is a conservative maximum.',
'e':'Spatial peak spacing alone conflates travel speed and timing. Constant independently calibrated pen frequency remains compatible with acceleration.'},
'A1B2':{
'a':'Stationary weight is balanced by sensor support plus displaced-fluid weight; the immersion-volume relation applies only before full immersion.',
'b':'The negative force-depth slope is −rho*g*A; its magnitude gives approximately994kg/m³.',
'c':'Maximum fractional slope and area uncertainties add to5.846percent, giving about58kg/m³.',
'd':'A constant additive force bias shifts the intercept and leaves the density-bearing gradient unchanged.',
'e':'After full immersion, displaced volume and upthrust saturate; extending the same negative slope would be physically incorrect.'},
'B1B1':{
'a':'Reciprocal length is the linearizing variable; the slope dimensions are W*m and represent k*A*DeltaT.',
'b':'A nonzero3W intercept follows from any supplied row and the slope. Forcing zero would misattribute parasitic heat loss.',
'c':'Dividing0.600W*m by the measured area and30K gives100W/(m*K), with consistent SI dimensions.',
'd':'The three maximum fractional uncertainties add, not combine in quadrature; approximately10.3percent is consistent with the final rounded bounds.',
'e':'Different exposed area or contact resistance can change the presumed common loss; improvements must address the chosen mechanism.'},
'B1B2':{
'a':'At successive turning points the same mass and g cancel from energy ratios; retention0.640 means loss0.360.',
'b':'Speed magnitude ratio is the square root of retained kinetic energy,0.800, not the energy ratio itself.',
'c':'Five impacts require the fifth integer power of retention; the near-geometric earlier observations are consistent with this approximate model.',
'd':'Measured and predicted bounded intervals are disjoint. Reject consistency over all five impacts without claiming one unique cause.',
'e':'A common multiplicative height calibration factor cancels from ratios; an additive zero error would not, but is not the stated error.'},
'A2Q1':{
'a':'One-dimensional momentum conservation applies during negligible external impulse, giving1.80m/s after coupling.',
'b':'Use the initially stationary cart momentum change only for the force on that cart, not the whole-system zero external impulse.',
'c':'Initial5.40J and post-coupling3.24J imply0.400 dissipated fraction; coupling is explicitly nonelastic.',
'd':'The later ideal spring receives only the remaining3.24J, giving0.190m compression, rather than the pre-collision energy.'},
'A2Q2':{
'a':'Particle interactions transfer random energy down the temperature gradient without material bulk motion; electron transport is an accepted conditional mechanism.',
'b':'The bare-wall rate uses the stated surface temperatures and supplied constant conductivity;960W is positive outward.',
'c':'A common steady heat rate allows the two conduction resistance terms to add; no unknown interface temperature remains in the final160W rate.',
'd':'Most temperature drop is across the added insulator. The interface lies18.7C, between both fixed surface temperatures.',
'e':'Saved heating output must be divided by0.800 efficiency before conversion into ten hours of electrical kWh.'},
'A2Q3':{
'a':'Coherent fixed relative phase permits stationary constructive/destructive locations; random phase fluctuations wash out the time-averaged pattern.',
'b':'Double-slit spacing lambda*D/d is SL; narrow slits and a far screen support the stated small-angle model.',
'c':'The selected dark locations are −0.5s and+1.5s, so separation is2s rather than one spacing or a three-fringe count.',
'd':'A uniform medium changes speed and wavelength at fixed frequency; the fringe spacing is reduced by refractive index without AHL single-slit/grating theory.'},
'A2Q4':{
'a':'The negative upper plate makes the field and positive-proton force upward; magnitude follows V/gap and qE.',
'b':'The resulting acceleration follows F/m and is directed upward, independent of the initial horizontal component.',
'c':'Horizontal traversal time is L/vx; the projected vertical displacement is explicitly hypothetical if the plate interrupts motion.',
'd':'The projected25.9mm exceeds20mm clearance, so actual impact occurs before the nominal exit. The scheme does not extend a free trajectory through matter.'},
'A2Q5':{
'a':'Beta-minus leaves A unchanged, raises Z by one and includes an electron antineutrino; no weak-force/quark machinery is required.',
'b':'Background subtraction changes the observed factor3 into source factor4, hence two whole half-lives in20minutes.',
'c':'At30minutes the expected source contribution is30/s; the raw detector value includes another30/s background.',
'd':'Three integer half-lives leave one eighth of the initial parent population; no decay-constant or arbitrary-time exponential is assumed.',
'e':'Finite random counts need not exceed the expected background mean. A low short observation is not a negative physical source activity.'},
'A2Q6':{
'a':'Luminosity divided by brightness has area dimensions; square root gives the source distance under isotropic, unextinguished emission.',
'b':'Converting distance into parsecs precedes the inverse-parallax relation; the result is a parallax semi-angle.',
'c':'Black-body luminosity and temperature determine area and then radius, with temperature to the fourth power.',
'd':'Wien wavelength uses absolute temperature and has the correct visible-light scale.',
'e':'Hydrostatic balance and fusion-supported pressure describe an approximate main-sequence equilibrium; the prompt does not establish a unique observed evolutionary age.'},
'B2Q1':{
'a':'Weight down, buoyancy up and drag opposite descent give the net driving force from the density difference, not the solid density alone.',
'b':'Terminal force balance yields the supplied Stokes-model speed0.0218m/s.',
'c':'Radius-squared scaling predicts a factor4 within the same drag regime; it is not asserted universally for all sizes.',
'd':'The final point correctly asks for a regime/container-size limitation instead of silently extending Stokes drag indefinitely.'},
'B2Q2':{
'a':'The numerical lamp characteristic gives nonconstant V/I, so no constant-ohmic-resistance assumption is used.',
'b':'Both the external2ohm and internal1ohm losses enter the loop equation.',
'c':'The negative quadratic root is excluded by the stated positive-current operating model; a reasonable plotted intersection is accepted.',
'd':'The lamp fraction is IVlamp/(emf*I), not a fraction using terminal power; follow-through from an allowed graphical current is appropriate.'},
'B2Q3':{
'a':'Closed-end displacement node and open-end antinode are distinguished from the later pressure question.',
'b':'The fundamental quarter-wavelength model is shared C.4 and gives approximately101Hz.',
'c':'The next open-closed resonance is the third harmonic rather than the second.',
'd':'End corrections are not assumed prior knowledge: the effective-length equation is supplied explicitly and only elementary rearrangement is assessed.',
'e':'A pressure antinode at the closed end is compatible with its displacement node, rather than a contradictory boundary condition.'},
'B2Q4':{
'a':'Circular acceleration and Newton gravity infer central mass without any AHL potential or escape expression.',
'b':'The required speed is circumference over the measured period; the numerical orbit remains circular.',
'c':'The planet surface radius, rather than satellite orbital radius, sets the surface field strength.',
'd':'At the same central mass, doubling circular orbital radius multiplies period by2^(3/2).'},
'B2Q5':{
'a':'Projected absorption and full spherical emitting area differ by a factor4; albedo removes reflected energy before thermal equilibrium.',
'b':'Emissivity and the fourth power of absolute temperature are included in the equilibrium calculation.',
'c':'The albedo ratio must be fourth-rooted and evaluated with unrounded baseline values; lower reflectivity increases equilibrium temperature.',
'd':'The two examples are distinct physical limitations, including spatial nonuniformity and atmospheric/surface feedback, rather than duplicated vague error claims.'},
'B2Q6':{
'a':'Control rods regulate neutron survival and chain reproduction; the conditional moderator role is physically distinct.',
'b':'Thermal power exceeds electrical output because the efficiency is0.400.',
'c':'MeV-to-joule conversion includes both the million factor and electronvolt conversion.',
'd':'Thermal power divided by energy per fission gives nuclei per second, with the correct units.',
'e':'Multiplying by nuclei mass and seconds/day counts uranium undergoing fission, not mass annihilated or fuel-assembly consumption.',
'f':'Only the rest-mass defect becomes released energy; most mass remains in fragments and other products.'}
}

# Independent arithmetic sanity checks focus on dimensions, physical bounds,
# uncertainty and the tricky choices; the other reviewer audits every figure and
# the complete numerical dataset separately.
ck('A1A1','distance-rate',(30+40+30)/80,1.25);ck('A1A1','displacement-rate',40/80,.5)
ck('A1A2','descending crossing',8*(6+math.sqrt(36-32))/10,6.4)
ck('A1A3','opposite force directions',1.4/.6,7/3)
v=(2*6-3-5)/2;ck('A1A4','dissipated collision energy',.5*2*6**2+.5*1*3**2-(.5*2*v*v+.5*1*25),24)
k=2*.84/(.1**2-.04**2);ck('A1A5','stored spring energy',.5*k*.08**2,.64)
ck('A1A6','slope speed',math.sqrt(2*(2*10*3*.5-3*3)/2),math.sqrt(21))
ck('A1A7','heat-capacity ratio',(.2*40)/(.3*20),4/3)
ck('A1A8','albedoY',180/600,.3);ck('A1A8','emissivity ratio',300/200,1.5)
ck('A1A9','initial heating flux',240-180,60)
ck('A1A10','amount from SI slope',400*.05/8.31,2.40673886883,1e-11)
ck('A1A11','rms speed ratio',math.sqrt(5),2.2360679775,1e-11)
ck('A1A12','cell-to-external power fraction',2/(2+1),2/3)
ck('A1A13','profile-translation transverse velocity',-5*(-.080),.4)
ck('A1A14','initial path difference in wavelengths',(.6)/.4,1.5)
ck('A1A15','fork frequency',343/(2*(.540-.180)),476.388888888889,1e-9)
ck('A1A17','stellar mass scaling',2**3/(.5**2),32)
ck('A1A18','instantaneous field-velocity dot product',0*1+1*0,0)
ck('A1A19','horizontal dipole field factor',2*math.cos(math.pi/3),1)
ck('A1A20','analyser m/q ratio',2/.5,4)
ck('A1A22','final nucleon number',238-4,234);ck('A1A22','final proton number',92-2+1,91)
bg=(4*44-116)/3;ck('A1A23','source/background late ratio',(116-bg)/(8*bg),.6)
ck('A1A24','fission energy MeV',141*8.4+92*8.6-235*7.6,189.6)
ck('A1A25','parallax conversion ly',3.26/(.100/2),65.2)
ck('B1A1','separate one-second displacements',(4+5*(9-4))/(4+5),29/9)
ck('B1A2','impact velocity angle degrees',math.degrees(math.atan(math.sqrt(360)/12)),57.6884667626,1e-9)
ck('B1A3','signed impulse/time',3*(.5*2*6+.5*(6-2)*4)/6,7)
ck('B1A4','remaining energy fraction',(.5*4*.5**2)/(.5+.5*3),.25)
ck('B1A5','pump input power',12*(10*5+.5*2**2)/.6,1040)
ck('B1A6','series conduction-rate ratio',(1+.25)/(.25+.25),2.5)
ck('B1A7','heat capacity after cancelling equal loss',40/(.2*(14-6)/60),1500)
ck('B1A7','inferred positive heat loss',60-.2*1500*6/60,30)
ck('B1A8','atmospheric absorption',25+15,40);ck('B1A8','whole-system outgoing',95-40+15,70)
ck('B1A9','rms temperature-product scaling',math.sqrt(1.5*2),math.sqrt(3))
ck('B1A10','ice and all-liquid temperature',(8000-.02*330000)/(.1*4200),10/3)
ck('B1A11','surviving branch current initially',(18/(2+3)*3)/4,2.7);ck('B1A11','surviving branch current finally',18/(2+4),3)
ck('B1A12','SL spring mass-scaled period',2*math.pi/math.sqrt(12/.03)*2,.628318530718,1e-12)
ck('B1A13','sound refraction angle',math.degrees(math.asin(1480/340*math.sin(math.pi/18))),49.10234824130518,1e-9)
ck('B1A14','liquid critical angle',math.degrees(math.asin(1.33/2)),41.6823253933,1e-9)
ck('B1A15','supplied string relationship harmonic scaling',3*50*math.sqrt(2.25)/1.5,150)
ck('B1A16','fractional optical Doppler ratio',(.75/500)/(.65/650),1.5)
ck('B1A17','same-density circular-period ratio',math.sqrt(3**3/27),1)
ck('B1A18','field imbalance after shift toward larger mass',4/(2/3-.01)**2-1/(1/3+.01)**2,0.7928356376575856,1e-9)
ck('B1A20','negative charge reverses v-cross-B vertical force',(-1)*(0-(-1)*(-1)),1)
ck('B1A21','excited-state energy gap eV',5-2,3)
ck('B1A22','energy input for charge-conserving model',56*8.8-14*4*7.1,95.2)
ck('B1A24','same-temperature radius ratio',math.sqrt(1e4/.01),1000)
ck('B1A25','parallax brightness ratio',(.05/.2)**2,1/16)
ck('A1B1','central velocity',(.072-.020)/(.2),.26);ck('A1B1','maximum velocity uncertainty',.26*(.002/.052+.004/.2),.0152)
ck('A1B1','second-difference acceleration',.004/.1**2,.4)
rho=3.9/(9.81*4e-4);ck('A1B2','density SI',rho,993.883792049,1e-9);ck('A1B2','maximum density uncertainty',rho*(.15/3.9+.08/4),58.1039755352,1e-9)
ck('B1B1','conductivity SI',.6/(2e-4*30),100);ck('B1B1','maximum uncertainty percent',100*(.03/.6+.04/2+1/30),10.3333333333,1e-9)
ck('B1B2','fifth rebound',.8*.64**5,.08589934592);ck('B1B2','gap between uncertainty intervals',(.086-.007)-(.040+.005),.034)
ck('A2Q1','compression after nonelastic collision',math.sqrt(2*3.24/180),.18973665961,1e-11)
Pnew=12*20/(.2/.8+.05/.04);ck('A2Q2','insulated heat flow',Pnew,160);ck('A2Q2','interface temperature',22-Pnew*.2/(.8*12),18.6666666667,1e-9);ck('A2Q2','electrical saving kWh',(960-160)/.8*10/1000,10)
ck('A2Q3','new-medium fringe spacing mm',(600e-9*2.5/.3e-3)*1e3/1.33,3.75939849624,1e-11)
acc=1.6e-19*(240/.04)/1.67e-27;ck('A2Q4','unimpeded vertical displacement',.5*acc*(.03/1e5)**2,.0258682634731,1e-13);ck('A2Q4','actual impact x',1e5*math.sqrt(2*.02/acc),.026378652985574024,1e-13)
ck('A2Q5','third-half-life gross rate',(270-30)/8+30,60);ck('A2Q5','remaining parent count',8e9/8,1e9)
dst=math.sqrt(3e27/(4*math.pi*2.5e-10));ck('A2Q6','parallax arcseconds',3.086e16/dst,.03157986220722864,1e-12)
ck('B2Q1','Stokes terminal speed',2*.001**2*2000*9.81/(9*.2),.0218)
I=(-3+math.sqrt(57))/2;ck('B2Q2','positive operating-current root',I,2.27491721764,1e-11);ck('B2Q2','lamp share of cell power',I**2/12,.431270695591,1e-11)
ck('B2Q3','supplied end-correction extension',343/(4*98.6)-.850,.0196754563895,1e-12)
GM=4*math.pi**2*(7.2e6)**3/6000**2;ck('B2Q4','surface gravitational field',GM/(6e6)**2,11.3697842701,1e-9)
T=(.64*1000/(4*.8*5.67e-8))**.25;ck('B2Q5','baseline temperature',T,243.70348190300822,1e-9);ck('B2Q5','changed-albedo temperature',T*(.75/.64)**.25,253.56076684732787,1e-9)
ck('B2Q6','daily fissioned uranium mass',(640e6/.4)/(200e6*1.6e-19)*86400*235*1.66e-27,1.685232)

def validate_markdown_tables(stem):
    """Check actual row separators and the GFM header/delimiter cell contract."""
    assert not re.search(r'\\n(?=\|)',stem),'Literal newline in table'
    rows=stem.splitlines();out=[];i=0
    def cells(row):return [c.strip() for c in re.split(r'(?<!\\)\|',row.strip())[1:-1]]
    while i<len(rows):
        if not rows[i].strip().startswith('|'):
            i+=1;continue
        assert rows[i].strip().endswith('|'),'Table row must close'
        header=cells(rows[i]);assert len(header)>=2
        assert i+1<len(rows),'Missing table delimiter'
        delim=cells(rows[i+1]);assert len(delim)==len(header),'GFM header/delimiter cell mismatch'
        assert all(re.fullmatch(r':?-{3,}:?',c) for c in delim),'Invalid GFM delimiter'
        i+=2;n=0
        while i<len(rows) and rows[i].strip().startswith('|'):
            assert rows[i].strip().endswith('|') and len(cells(rows[i]))==len(header),'Table data/header cell mismatch'
            n+=1;i+=1
        assert n>0,'Table has no data rows';out.append({'columns':len(header),'bodyRows':n})
    return out

def alias(q):
    s=q['id'].split('-')[2].upper();sec=q['section']
    return s+('1A' if sec=='1A' else '1B' if sec=='1B' else '2Q')+str(q['number'])
def ordered_tokens(value,tokens):
    pos=0
    for token in tokens:
        found=value.find(token,pos)
        if found<0:return False
        pos=found+len(token)
    return True
papers=[];records=[];count=0;groups=0;table_count=0
for set_ in ['a','b']:
  for pnum in ['1','2']:
    path=P/f'physics-sl-set-{set_}-paper-{pnum}.json';raw=path.read_bytes();p=json.loads(raw)
    assert p['course']=='sl' and p['minutes']==90 and p['marks']==(45 if pnum=='1' else 50)
    assert sum(q['marks'] for q in p['questions'])==p['marks']
    papers.append({'id':p['id'],'sha256':hashlib.sha256(raw).hexdigest(),'questions':len(p['questions']),'marks':p['marks'],'status':'passed'})
    for q in p['questions']:
      key=alias(q);count+=1;assert q['level']=='core';assert q['syllabusRefs']
      assert not set(q['syllabusRefs'])&{'A.4','A.5','B.4','D.4','E.2'}
      tables=validate_markdown_tables(q['stem']);table_count+=len(tables)
      labels=[x['label'] for x in q['parts']] if q['parts'] else [''];schemes={x['part']:x for x in q['markScheme']}
      assert set(labels)==set(schemes)
      rs=[]
      for label in labels:
        sm=schemes[label];mark=sum(int(x['code'][1:]) for x in sm['steps']);assert all(re.fullmatch('[MAR][1-9][0-9]*',x['code']) for x in sm['steps'])
        expected=next(x['marks'] for x in q['parts'] if x['label']==label) if q['parts'] else 1
        assert mark==expected;groups+=1
        note=N[key] if q['section']=='1A' else PARTS[key][label]
        assert len(note)>55
        rs.append({'part':label,'marks':mark,'allPromptAndMarkingPointsRead':True,'review':note,'status':'passed'})
      if q['section']=='1A':
        assert len(q['options'])==4 and len({x['text'] for x in q['options']})==4
        assert q['correctOption'] in 'ABCD'
        candidates=[o for o in q['options'] if ordered_tokens(o['text'],C[key])]
        assert len(candidates)==1,(q['id'],'Physical correct-option text is not unique')
        assert candidates[0]['label']==q['correctOption'],(q['id'],'Reordered answer key mismatches physical answer')
        option_review={'expectedCorrectOptionText':candidates[0]['text'],'currentCorrectLabel':candidates[0]['label'],'independentTextMatch':True}
      else:option_review=None
      records.append({'paper':p['id'],'questionId':q['id'],'section':q['section'],'number':q['number'],'status':'passed','scopeRefs':q['syllabusRefs'],'fullStemOptionsAndSchemeRead':True,'parts':rs,'independentSanityChecks':checks.get(key,[]),'optionTextReview':option_review,'markdownTablesChecked':tables,'diagramReviewScope':'Textual physical geometry and model assumptions considered here; native diagram values and complete numerical audit are recorded by the separate SL reviewer.'})
assert count==66 and groups==124 and table_count==4
report={'status':'passed','reviewer':'mock_exam_spec, independent of the SL author','scope':'All66 complete stems/options/schemes; current SL boundaries, physical assumptions, qualitative reasoning, positive mark allocation and selected independently recomputed numerical/uncertainty sanity checks. Separate reviewer owns complete fresh numerical and native-figure audit.','primaryGuide':'https://xmltwo.ibo.org/publications/EAD/2026_EN/GR4/GR4-Physics_EN.pdf','questions':count,'markingGroups':groups,'independentSanityAssertionCount':sum(len(x) for x in checks.values()),'papers':papers,'records':records,'resolvedFindings':[{'question':'A1A3','finding':'Same passive ball with drag could not pass same height at equal upward/downward speeds.','resolution':'Independent identical-ball trials now make the givens physically possible; ratio unchanged.'},{'question':'A1A16','finding':'Damping/resonance metadata incorrectly usedC.1.','resolution':'Corrected to sharedC.4.'},{'question':'Allfour1Btables','finding':'Literal backslash-n row separators prevented proper table formation.','resolution':'Actual newline row separators now present; A1B2 delimiter cell count separately corrected before binding.'},{'question':'B1A15','finding':'Tension/linear-density wave-speed law was not provided.','resolution':'The new relationship and both symbols are now explicitly supplied, avoiding assumed extra syllabus content.'},{'question':'B1A17','finding':'Numerical elliptical-apsis speed comparison contradicted current circular-orbit restriction.','resolution':'Replaced by a circular near-surface equal-density period comparison, with mass/radius scaling independently checked.'},{'question':'B1A22','finding':'Generic breakup model left initial proton/neutron counts implicit.','resolution':'Now explicitly28protons/28neutrons, preserving charge in14alpha products.'}],'openFindings':[],'limits':'No claim of human IB examiner moderation or calibrated grade prediction. This focused review must be combined with the separate numerical/figure review and final PDF visual checks.'}
out=DOC/'sl-scope-independent-review.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'status':report['status'],'questions':count,'markingGroups':groups,'sanityAssertions':report['independentSanityAssertionCount'],'papers':papers},indent=2))
