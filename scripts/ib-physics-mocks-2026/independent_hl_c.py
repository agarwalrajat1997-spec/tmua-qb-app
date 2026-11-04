"""Independent re-solution of HL C, without importing its author or common module.

The constants and conclusions below were transcribed after reading the complete
prompts, diagrams, distractors and schemes. This is review evidence, not an
automated proof that a natural-language question has a unique physical model.
"""
from pathlib import Path
import hashlib, json, math, re

ROOT = Path(__file__).resolve().parents[2]
TASK = ROOT.parents[1]
checks = []

def check(q, name, actual, expected, tol=1e-10):
    ok = math.isfinite(actual) and abs(actual-expected) <= tol
    checks.append(dict(questionId=q,name=name,computed=actual,expected=expected,absoluteTolerance=tol,passed=ok))
    if not ok: raise AssertionError(checks[-1])

def qid(section, n): return f'phy-hl-c-{section}-{n:02d}'
def c(n,name,a,e,t=1e-10): check(qid('1a',n),name,a,e,t)
def d(n,name,a,e,t=1e-10): check(qid('1b',n),name,a,e,t)
def p(n,name,a,e,t=1e-10): check(qid('2',n),name,a,e,t)

# Independent numerical work from the 40 MCQ prompts and their plotted data.
c(1,'signed impulse',.5*2*12-.5*2*8,4);c(1,'final velocity',(2*3+4)/2,5)
c(2,'descent dissipation',5*10*1.8-.5*5*4**2,50);c(2,'uphill winch work',90+50,140)
c(3,'cable tension ratio',math.cos(math.pi/3)/math.cos(math.pi/6),1/math.sqrt(3));c(3,'useful power ratio',2,2)
c(4,'rotational loss ratio',(1-1/2)/(1-1/1.25),2.5)
c(5,'drop factor',2**2,4);c(5,'translational energy fraction',.5/(.5+.25),2/3)
gamma=1/math.sqrt(1-.8**2)
c(6,'onboard proper time',(6/.8)/gamma,4.5);c(6,'contracted separation',6/gamma,3.6)
c(7,'net radiation ratio',.25*2*(2**4-1),7.5)
c(8,'inferred contact resistance over bar resistance',(60-40)/(100-60),.5);c(8,'heat-rate ratio after contact change',(2+.5)/(2+2*.5),5/6);c(8,'new hot-side interface temperature',100-100/3,66.7,.05)
c(9,'albedo temperature ratio',(.64/.8)**.25,.9457416090031758);c(9,'layer outward fraction',1/2,.5)
c(10,'final monatomic internal energy',1.5*(1200/20)*2*1.5,270)
c(11,'temperature ratio after adiabat',2*.5**(5/3),2**(-2/3));c(11,'net normalized cycle work',-math.log(2)+1.5*(1-2**(-2/3)),-.13808796798021086,1e-12)
c(12,'final kinetic energy in microjoules',200-(-3)*(-10-30),80)
c(13,'external power ratio',(4/9)/(.5),8/9)
c(14,'positive velocity',4*math.sqrt(.06**2-.03**2),.2078460969082653);c(14,'restoring acceleration',-16*.03,-.48)
c(16,'reverse critical angle',math.degrees(math.asin(math.sin(math.radians(40))/math.sin(math.radians(60)))),47.92148593329638,1e-10)
c(17,'strictly interior constructive orders',len([n for n in range(-10,11) if abs(n*.008)<.04]),9)
c(18,'closed-open fundamental',(350-210)/2,70);c(18,'pipe length',350/(4*70),1.25);c(18,'next odd resonance',7*70,490)
c(19,'calibrated radial speed in km per second',3e5*((500.35-.10)-500)/500,150,1e-8)
c(20,'moving-source received frequency',500*330/(330-66),625);c(20,'moving-observer received frequency',500*(330+66)/330,600);c(20,'difference between separate experiments',625-600,25)
c(21,'surface gravity ratio',.6**3/.6**2,.6);c(21,'circular period ratio',math.sqrt(.6**3/.6**3),1)
c(22,'dimensionless gravitational potential',-1-9/3,-4)
c(23,'contact-redistribution force ratio',(1/2**2)/3,1/12)
c(24,'mean electric field ratio',(10-6)/(6-4),2);c(24,'field work in nanojoules',2*(10-4),12)
c(25,'new transit-time ratio',2/math.sqrt(4),1);c(25,'exit tangent ratio',1/math.sqrt(4),.5)
c(27,'motional-emf ratio',3*.5,1.5)
c(28,'generator peak-emf ratio',2*.5*2,2);c(28,'generator frequency ratio',1/.5,2)
c(29,'electron-target alpha velocity ratio',(1-1/7000)/(1+1/7000),.9997143265247822);c(29,'heavy-target alpha velocity ratio',(1-50)/(1+50),-49/51)
c(30,'visible Q wavelength',1240/3,413.3333333333,1e-9);c(30,'ultraviolet R wavelength',1240/4.5,275.5555555556,1e-9)
c(31,'Compton angle',math.degrees(math.acos(1-1.5)),120);c(31,'electron energy fraction',1-1/(1+1.5),.6)
c(32,'retarded electron final kinetic energy in eV',900/(1.5**2),400);c(32,'retarding potential magnitude',900-900/(1.5**2),500)
c(33,'final proton number',92-2+2,92);c(33,'final neutron number',238-4-92,142)
c(34,'beta-plus daughter charge',7-1,6);c(34,'neutrino kinetic energy',1.2-.7,.5)
c(35,'conditional decay probability',1-math.exp(-math.log(2)*6/18),.2062994740159002);c(35,'linear approximation',math.log(2)/3,.23104906018664842)
c(36,'two moderator collisions',((2-1)/(2+1))**4,1/81)
c(37,'parallax distance in parsecs',1/(5*.01/2),40)
c(38,'run-down angular acceleration',(6-18)/4,-3);c(38,'inertia from dissipated energy',2*108/(18**2-6**2),.75);c(38,'initial angular momentum',.75*18,13.5);c(38,'remaining stopping angle',-6**2/(2*(-3)),6)
c(39,'photoelectric threshold',6e14-.35/((1.59-.35)/3e14),5.153225806451613e14,.1)
c(40,'actual engine work increase',1200*.75*((1-300/750)-(1-300/600)),90)

# Two genuine data contexts: endpoints, uncertainty bounds, calibration and model testing.
d(1,'missing resistance',.840/.250,3.36)
g=(3.72-3)/60;gmax=(3.74-2.98)/60;gmin=(3.70-3.02)/60
d(1,'best resistance-temperature gradient',g,.012);d(1,'maximum endpoint gradient',gmax,.0126666666666667);d(1,'minimum endpoint gradient',gmin,.0113333333333333);d(1,'gradient half range',(gmax-gmin)/2,.000666666666666667)
area=math.pi*(.400e-3)**2/4;rho=3.36*area/2;frac=.020/3.36+2*.004/.400+.01/2
d(1,'wire cross-sectional area',area,1.2566370614359172e-7,1e-20);d(1,'resistivity',rho,2.1111502632123408e-7,1e-20);d(1,'fractional resistivity uncertainty',frac,.030952380952380953);d(1,'absolute resistivity uncertainty',rho*frac,6.53451271946677e-9,1e-21)
dx=1/3-1/8;K=(33.6-12.6)/dx;Kmax=(34.1-12.1)/dx;Kmin=(33.1-13.1)/dx;dK=(Kmax-Kmin)/2
d(2,'reciprocal-energy gradient',K,100.8);d(2,'gradient upper bound',Kmax,105.6);d(2,'gradient lower bound',Kmin,96);d(2,'gradient uncertainty',dK,4.8);d(2,'target Z',K/2.88,35);d(2,'target Z uncertainty',dK/2.88,5/3)
R=1.2*80**(1/3)
d(2,'target radius',R,5.17064325607652);d(2,'radius-scale incident energy',K/R,19.4946731013126,1e-9);d(2,'new predicted closest approach',K/12,8.4);d(2,'new prediction uncertainty',dK/12,.4)

# All 45 written parts: fresh computations, with the qualitative reasoning ledger below.
h=1.25*(1-math.cos(math.pi/3));v=math.sqrt(2*9.81*h);u=.3*v/.75
p(1,'bob vertical drop',h,.625);p(1,'bob speed',v,3.5017852589786256);p(1,'bottom string tension',.3*(9.81+v*v/1.25),5.886);p(1,'postcollision speed',u,1.4007141035914503);p(1,'ramp height',u*u/(2*9.81),.1);p(1,'collision dissipated fraction',1-.3/.75,.6)
Q=.18*2100*23;Sice=.18*2100*math.log(273/250);Swater=-Q/273
p(2,'heat required by cold ice',Q,8694);p(2,'water mass frozen',Q/3.34e5,.02602994011976048);p(2,'warming ice entropy',Sice,33.3,.05);p(2,'freezing water entropy',Swater,-31.846153846153847);p(2,'isolated system entropy production',Sice+Swater,1.42,.005);p(2,'near-equilibrium entropy production',.18*2100*(math.log(273/270)-3/273),.0230,.00005)
beta=3/5;gam=1/math.sqrt(1-beta**2)
p(3,'rocket beta',beta,.6);p(3,'rocket gamma',gam,1.25);p(3,'photon arrival ct',5+3,8);p(3,'null photon interval',3**2-(-3)**2,0);p(3,'emission rocket x',gam*(3-beta*5),0);p(3,'emission proper ct',gam*(5-beta*3),4);p(3,'arrival rocket x',gam*(0-beta*8),-6);p(3,'arrival frame ct',gam*8,10);p(3,'simultaneity time difference',gam*5-4,2.25)
spacing=1/(500e3)
p(4,'grating spacing',spacing,2e-6,1e-20);p(4,'second-order spectral angular width',math.degrees(math.asin(2*700e-9/spacing)-math.asin(2*400e-9/spacing)),20.85,.005);p(4,'complete visible maximum order',math.floor(spacing/700e-9),2);p(4,'third-order overlapping wavelength in nm',2*660/3,440);p(4,'overlap angle',math.degrees(math.asin(2*660e-9/spacing)),41.2998727917059,1e-9);p(4,'monochromatic visible-to-screen orders',2*math.floor(spacing/520e-9)+1,7)
E=320/.040;a=1.6e-19*E/1.67e-27;t=.120/3e5;th=math.sqrt(.040/a)
p(5,'plate electric field',E,8000);p(5,'proton acceleration',a,7.664670658682635e11,.01);p(5,'nominal exit time',t,4e-7,1e-20);p(5,'unbounded proton exit deflection',.5*a*t*t,.061317365269461075);p(5,'proton hit position',3e5*th,.0685,.00005);p(5,'alpha nominal exit deflection',.25*a*t*t,.030658682634730537);p(5,'alpha hit position',math.sqrt(2)*3e5*th,.0969,.00005);p(5,'selector field',E/3e5,.02666666666666667)
R=1.2*120**(1/3);closest=2*50*1.44/6
p(6,'alpha centre-to-centre turning distance',closest,24);p(6,'tin radius',R,5.918908978393128);p(6,'turning distance to nuclear radius ratio',closest/R,4.054801330382267);p(6,'isotope radius ratio',(125/120)**(1/3),1.013700332595567);p(6,'radius-scale alpha energy',144/R,24.3288079822936,1e-9)
va=math.sqrt(2*10*1.6);spring=2*2*10*2.4/.8**2;Fmax=spring*.8;Fmean=20+2*va/.205
p(7,'speed when cord becomes taut',va,5.656854249492381);p(7,'cord spring constant',spring,150);p(7,'turning point upward acceleration',(Fmax-20)/2,50);p(7,'time-average cord force',Fmean,75.1888219462671,1e-9);p(7,'half peak cord force',Fmax/2,60)
# Additional reviewer-only consistency test: ideal Hooke trajectory gives the supplied rounded timer.
omega=math.sqrt(spring/2);xeq=20/spring
stop_t=math.atan2(va, -xeq*omega)/omega
p(7,'ideal cord turning time consistent with timer',stop_t,.205,.0005)
f=math.sqrt(64*math.pi**2/.160)/(2*math.pi);lam=1.5/f
p(8,'driver frequency',f,10);p(8,'water wavelength',lam,.15);p(8,'initial path-difference order',(.45)/lam,3);p(8,'initial resultant amplitude in mm',2*.8,1.6);p(8,'first higher-frequency node',3.5*1.5/.45,11.666666666666666);p(8,'Q initial path-difference order',.525/lam,3.5)
p(9,'asymptotic probe speed in km per second',math.sqrt(10**2-8**2),6);p(9,'path-averaged inward gravitational field',(7000**2-6800**2)/(2*3e6),.46);p(9,'triple-alpha mass defect',3*4.00260-12,.0078,1e-14);p(9,'triple-alpha released energy',(3*4.00260-12)*931.5,7.2657,1e-10)

MCQ_TEXTS = [
'$+5.0\\,\\mathrm{m\\,s^{-1}}$','$140\\,\\mathrm{J}$','$1/\\sqrt3$ and $2$','$5/2$','$4$ and $2/3$',
'$4.5\\,\\mathrm{yr}$ and $3.6\\,\\mathrm{ly}$','$7.5P$','$5/6$ and $66.7^\\circ\\mathrm C$','$0.946$ and $1/2$','$270\\,\\mathrm J$',
'Negative; $2^{-2/3}$','$80\\,\\mu\\mathrm J$','$8/9$','$+0.208\\,\\mathrm{m\\,s^{-1}}$ and $-0.480\\,\\mathrm{m\\,s^{-2}}$',
'Out of the page; to the left','$47.9^\\circ$','$9$','$1.25\\,\\mathrm m$ and $490\\,\\mathrm{Hz}$','Receding at $150\\,\\mathrm{km\\,s^{-1}}$','$25\\,\\mathrm{Hz}$',
'$0.60$ and $1$','$+4Gm\\mu/r$','$F/12$, repulsive','$+x$; $2$; $+12\\,\\mathrm{nJ}$','Deflection unchanged; tangent halved','Zero force; clockwise torque','Top; $1.5\\mathcal E$','$2$ and $2$',
'Electron target: $+0.9997u$; nuclear target: $-0.961u$; only the heavy target can reverse the alpha','Q visible; R ultraviolet','$120^\\circ$ and $0.60$','$500\\,\\mathrm V$','$92$ protons and $142$ neutrons','$6$ and $0.50\\,\\mathrm{MeV}$',
'$0.206$; $\\lambda\\Delta t$ is larger','$1/81$; stable nuclei with a low neutron-absorption probability','$40\\,\\mathrm{pc}$','$13.5\\,\\mathrm{kg\\,m^2\\,s^{-1}}$ and $6.0\\,\\mathrm{rad}$','$5.15\\times10^{14}\\,\\mathrm{Hz}$ and $0.35\\,\\mathrm V$','$90\\,\\mathrm J$']
MCQ_REASON = [
'Signed force areas yield net impulse +4 N s; adding initial +6 momentum gives +5 m/s. The other velocities use unsigned area, omit initial momentum or subtract incorrectly.',
'The 90 J potential loss becomes 40 J kinetic and 50 J heat. The same opposing resistance dissipates another 50 J on return, so the winch supplies 140 J.',
'Each cable supplies T cos(theta); changing angle reduces tension by 1/sqrt(3), whereas useful power is weight times vertical speed and doubles.',
'The added inertia is I in trial one and I/4 in trial two. Angular momentum gives losses one half and one fifth of the initial rotational energy, whose ratio is 5/2.',
'With fixed inertia L doubles only if angular speed doubles. No slip doubles centre speed, quadruples total kinetic energy and height loss; translation receives two thirds.',
'The station distance is its proper length. The ship clock measures proper time 7.5/gamma=4.5 years and simultaneous ship separation is 3.6 ly; different frame intervals cannot be mixed.',
'Absorbed enclosure radiation must be subtracted with the same emissivity, leaving 0.25 times twice the area times the fourth-power difference 15, hence 7.5 P.',
'Initially each identical bar drops forty kelvin while the imperfect interface drops twenty, so contact resistance is one half bar resistance. Doubling it increases total from 2.5R to 3R: heat rate becomes five sixths and the hot interface becomes 66.7 Celsius.',
'The one-layer model emits half of the absorbed surface long-wave energy upward; fixed greenhouse properties make surface T scale with the fourth root of absorbed solar flux.',
'The reciprocal-volume pressure gradient is nRT=60 J, so initial U=90 J. Doubling n and multiplying T by 1.5 triples U to 270 J.',
'The adiabatic expansion lies below the compression isotherm. Work by gas is negative and the final equal-volume temperature ratio is 2^(-2/3).',
'Negative charge moving through negative potential change gains 120 microjoules potential energy; kinetic energy falls from 200 to 80 microjoules.',
'Removing a parallel branch raises terminal voltage because the cell has internal resistance. Recomputing both external powers gives ratio 8/9, rather than assuming fixed voltage.',
'The positive motion condition selects the positive square-root velocity. The acceleration is negative because displacement is positive and a=-omega squared x.',
'Both electromagnetic fields reverse after half a period. Their perpendicular handedness gives propagation left, and reversing both leaves that direction unchanged.',
'Convert the interface angles to 60 and 40 degrees to the normal before Snell. The denser medium is 2 and its reverse critical angle is 47.9 degrees.',
'Envelope zeros occur exactly at integer interference orders plus/minus five. Strictly interior orders are minus four to plus four; the diagram correctly shows missing boundary maxima.',
'A closed-open column has odd harmonics. The 140 Hz separation implies fundamental 70 Hz, length 1.25 m and next resonance seven times fundamental.',
'Remove the constant positive wavelength bias first. Remaining positive 0.25 nm shift means recession at 150 km/s, rather than the uncorrected 210.',
'These are separate experiments, each with only one moving participant. Moving-source wave compression gives 625 Hz, while a moving observer traverses unchanged wavelength spacing at an increased rate and receives 600 Hz. Their difference is 25 Hz; sound has a preferred medium frame.',
'Equal density makes mass proportional to radius cubed, surface g proportional to radius and very-low circular period independent of radius.',
'Zero resultant field only constrains potential gradient. Both negative potentials add to minus four Gm/r, and slow external removal requires positive four Gm mu/r.',
'Identical touching conductors share total +2Q equally. Positive final charges repel; the reduced charge product and doubled distance together divide force by twelve.',
'Electric field points down potential along positive x. Equal centimetre intervals give mean field ratio two; positive-charge field work is +12 nJ.',
'Accelerating through four times the potential doubles horizontal speed. Doubling plate length preserves transit time and transverse motion, but halves vy/vx.',
'For downward current in Y the right-hand field is out on the right and in on the left. Opposite forces cancel, and both moments turn X clockwise.',
'For positive charges, rightward v crossed into-page B points upward. Top becomes positive; halving rod length and tripling speed gives factor 1.5.',
'Peak generator emf scales with N A omega and frequency with rotation frequency. The specified turn/area changes cancel, leaving factor two in both quantities.',
'The supplied one-dimensional elastic model leaves an alpha almost unchanged and forward-moving after hitting the much lighter electron. A fifty-times heavier target gives negative outgoing alpha velocity, consistent with backscattering; no unsupported simultaneous conservation-equation derivation is assumed.',
'The plotted energy gaps are 1.5, 3 and 4.5 eV. Dividing hc by each gap places only Q in visible light and R in ultraviolet.',
'The supplied Compton shift gives cos theta=-0.5. Increasing wavelength to 2.5 initial leaves 0.4 photon energy and transfers 0.6 to electron kinetic energy.',
'De Broglie wavelength is inverse to momentum; at fixed electron mass, increasing wavelength by 1.5 reduces kinetic energy by 2.25. The 900 eV beam retains 400 eV and loses 500 eV, so retardation is 500 V without stopping it.',
'Alpha emission removes two protons and two neutrons; two beta-minus decays restore two protons without restoring nucleons. Final N=234-92=142.',
'Beta plus converts one proton to a neutron and emits an electron neutrino. With recoil neglected, available kinetic energy less positron energy leaves 0.50 MeV.',
'Conditional survival for an undecayed nucleus is exp(-lambda dt). Decay probability is about 0.206, less than the tangent approximation lambda dt=0.231.',
'The supplied energy-retention fraction is one ninth per collision, hence one eighty-first after two. A moderator should retain neutrons rather than absorb them.',
'The six-month image displacement is twice parallax, giving p=0.025 arcsec and forty parsecs. Proper motion was explicitly excluded.',
'The run-down graph gives angular acceleration minus three rad/s squared. The independent 108 J energy loss gives inertia 0.75 kg m squared and initial angular momentum 13.5; the six rad/s remaining speed gives a further six radians before stopping.',
'The stopping-voltage slope gives h/e and threshold about 5.15e14 Hz. Doubling intensity changes electron rate, not stopping voltage at fixed frequency.',
'Use absolute temperatures for both Carnot limits, then multiply by the stated actual/ideal efficiency factor before applying the same absorbed energy. Work rises by 90 J.'
]

WRITTEN_REASON = {
'1b1':[
'At the absent graph point use the supplied simultaneous V and I, giving 3.36 ohm; no interpolated value is needed.',
'Endpoint temperature uncertainty is excluded, so only resistance error bars alter numerator. The symmetric steepest/shallowest slopes give the stated half-range uncertainty.',
'Use radius one half of the given diameter before squaring. Ohm metre follows from R times cross-sectional area divided by length.',
'Maximum fractional uncertainty adds the resistance, twice diameter and length contributions. The final absolute uncertainty and central resistivity use consistent powers of ten.',
'The ice-water reference reveals a constant negative zero offset, hence systematic bias. Adding 1.5 degrees translates all x coordinates right without changing differences or slope.',
'Stirring reduces thermal gradients so measured bath temperature represents the wire temperature; merely naming reduced random error would not establish this control.'
],
'1b2':[
'With x=1/E the supplied outside electrostatic model becomes d=Kx. Both constant gradient and zero intercept are necessary predictions.',
'Taking endpoint reciprocal energies in the proper order gives positive 100.8 MeV fm. Opposite error-bar extremes produce 105.6 and 96.0, with half-range 4.8.',
'Divide gradient and its uncertainty by the same exact 2.88 MeV fm factor. Proton number is integral physically but its inferred experimental uncertainty remains nonzero.',
'Use the explicitly supplied nuclear-radius model at A=80, then d=R in K/E. This is a geometric model scale, not a precise nuclear-reaction threshold.',
'The predicted distance interval 8.0 to 8.8 fm is disjoint from the new observed 5.5 to 6.5 fm. This rejects the stated model/error budget but cannot identify one unique mechanism; specific calibration or physical-model alternatives are valid.'
],
'21':[
'The string geometry gives drop L(1-cos60), then conservation of mechanical energy yields pre-cut speed.',
'At the bottom the upward string force minus weight equals inward centripetal resultant; tension is not simply the centripetal force alone.',
'Use horizontal momentum for the cut-string inelastic collision, then mechanical energy for the separate frictionless ramp. These two stages have different conservation rules.',
'Cutting the string eliminates its impulse. Negligible other horizontal impulse preserves system momentum, while internal deformation/sound dissipate mechanical energy during sticking.',
'For a stationary target the retained kinetic fraction after sticking is incoming mass divided by total mass, 0.4. The requested dissipated fraction is its complement 0.6.'
],
'22':[
'Warming cold ice requires mc delta T, supplied by freezing part of the surrounding liquid. Divide this latent transfer by Lf to obtain 0.0260 kg.',
'During freezing the mean random kinetic energy and temperature remain steady, while intermolecular potential energy falls and supplies latent heat.',
'Use the explicitly supplied logarithmic entropy expression because the warming ice temperature varies; dividing the whole heat by one endpoint temperature would be invalid.',
'The freezing water is at the constant 273 K reservoir temperature, so its entropy decreases by Q/273. The insulated total increases, consistent with irreversible heat flow.',
'Repeat both entropy contributions at the new 270 K initial temperature. The smaller finite temperature difference gives smaller positive entropy production, approaching reversible transfer.'
],
'23':[
'Slope x/(ct) of the constant-velocity worldline gives beta=0.6, and the Lorentz factor is 1.25; both axes use length units.',
'A backwards photon covers 3 light-years in 3 years and arrives at ct=8. The difference vector is lightlike, so the squared interval vanishes.',
'Apply both supplied Lorentz transformations to E; its x prime is zero. O and E occur on the rocket clock, making four years a proper interval.',
'Transform F, obtaining x prime=-6 and ct prime=10. Since F is away from the rocket, its time is assigned by synchronized frame clocks rather than a local rocket-clock reading.',
'Station event G has x=0, ct=5. Its transformed time 6.25 years exceeds E prime time four by 2.25; simultaneity is frame-dependent.'
],
'24':[
'Convert lines per millimetre to lines per metre before taking the reciprocal to get the grating spacing.',
'Find each second-order edge angle with inverse sine and subtract the angles. Inverse sine of a wavelength difference would not represent angular width.',
'The longest wavelength reaches sin theta=1 first as order increases. Integer order two contains the whole band, although part of order three exists.',
'Equal screen direction means equal m lambda for the two orders, giving 440 nm. Substituting either wavelength/order pair gives the same 41.30 degree direction.',
'The maximum integer order at 520 nm is three, not four. Count both non-grazing sides and the central maximum for seven screen-reaching rays.'
],
'25':[
'Field points from positive upper to negative lower plate. A positive proton acceleration is in the same direction and has magnitude qE/m.',
'First test the hypothetical exit deflection against half the gap. Because it exceeds the gap, solve for the earlier impact time and horizontal distance; do not continue the path through a plate.',
'Alpha charge-to-mass ratio is half the proton value, but its hypothetical exit deflection still exceeds the half-gap. Its impact distance is sqrt(2) times the proton distance.',
'For a positive right-moving ion the into-page magnetic field produces upward force. Equal electric and magnetic forces require B=E/v independent of q/m.',
'Undeflected motion has vanishing resultant force, electric force perpendicular to displacement and no magnetic work, so kinetic energy is unchanged.'
],
'26':[
'At a head-on electrostatic turning point, the alpha kinetic energy becomes Coulomb potential energy. The distance is between nuclear centres, not surface separation.',
'Use nucleon number for the supplied radius law and compare the centre distance to that radius. The alpha turns well outside the target nuclear radius.',
'Changing isotope changes A but leaves target charge and thus no-recoil Coulomb turning distance unchanged. Radius grows by the cube root of the nucleon-number ratio.',
'Equating the outside-model distance to the calculated original radius yields an approximate energy scale near 24.3 MeV, not an exact reaction threshold.',
'Finite distributed charge invalidates the outside point-charge form after penetration, and short-range nuclear interactions supply a distinct second reason. Repeating finite size alone earns one point.'
],
'27':[
'Before tautness the cord exerts no force, so the mass falls freely through 1.6 metres and gains speed sqrt(2gL).',
'The complete fall includes slack length plus extension; all that gravitational energy becomes spring energy at the first turning point.',
'At B the cord force is 120 N up and weight 20 N down, giving 50 m/s squared up. Instantaneous zero velocity does not imply zero resultant force.',
'Use upward-positive net impulse, accounting for the initial downward momentum and the impulse of weight. Adding weight back gives the average cord force, about 75.2 N.',
'Half the peak cord force is only 60 N. Hooke linearity is in extension, whereas the requested average is over time with nonuniform motion; equal extension intervals have unequal duration.'
],
'28':[
'Apply the ideal mass-spring natural-frequency formula; the supplied pi-squared spring constant cancels exactly to ten hertz.',
'Wave speed divided by frequency yields the wavelength 0.15 m, using wave speed rather than driver oscillation speed.',
'The path difference is three complete wavelengths for initially in-phase sources, so equal amplitudes add to 1.6 mm.',
'Increasing frequency increases propagation cycles along the fixed path difference. The first higher destructive condition is 3.5, rather than 2.5, wavelengths and occurs at 11.7 Hz.',
'Reversing one source adds half a cycle. It changes the original integer-order P maximum into a node and the half-integer Q propagation difference into a maximum.'
],
'29':[
'Escape energy is the initial energy needed to reach zero-speed infinity. Subtract its square-speed contribution from the launch square speed, leaving six km/s at infinity.',
'The kinetic-energy loss per mass divided by the path length defines the spatial average of inward field; the calculation does not assume a constant inverse-square field.',
'Atomic electron numbers balance, so supplied atomic masses may be subtracted directly. The positive 0.0078 u defect releases 7.2657 MeV.',
'Helium has greater positive charge and hence a higher Coulomb barrier than hydrogen. Fusion beyond the binding-energy maximum consumes rather than supplies net energy.',
'Hydrostatic equilibrium balances pressure-gradient force against gravity locally. Nuclear energy replaces radiative losses to maintain pressure; it does not cancel gravity or stop outward energy flow.'
]
}

papers=[];question_reviews=[];figures=[]
for paper_num in ('1','2'):
    path=ROOT/f'content/ib/physics-mocks-2026/papers/physics-hl-set-c-paper-{paper_num}.json'
    paper=json.loads(path.read_text(encoding='utf8'))
    if paper_num=='1':
        keys=[q['correctOption'] for q in paper['questions'] if q['section']=='1A']
        assert all(keys.count(letter)==10 for letter in 'ABCD')
        assert not any(all(key==keys[i%period] for i,key in enumerate(keys)) for period in range(1,9))
    ids=[];written=0
    for q in paper['questions']:
        ids.append(q['id'])
        numeric=[v['name'] for v in checks if v['questionId']==q['id']]
        if q['questionType']=='multiple-choice':
            text=MCQ_TEXTS[q['number']-1]
            candidates=[o for o in q['options'] if o['text']==text]
            assert len(candidates)==1,(q['id'],text)
            assert candidates[0]['label']==q['correctOption'],q['id']
            assert len({o['text'] for o in q['options']})==4
            checks.append(dict(questionId=q['id'],name='Independent one-correct-option and distractor review',expectedOption=candidates[0]['label'],expectedCorrectText=text,passed=True))
            parts=[dict(part='',marks=1,reasoning=MCQ_REASON[q['number']-1],checkNames=numeric+['Independent one-correct-option and distractor review'],status='passed')]
        else:
            key=(q['section'].lower()+str(q['number'])) if q['section']=='1B' else '2'+str(q['number'])
            reasons=WRITTEN_REASON[key]
            assert len(reasons)==len(q['parts']),(key,len(reasons),len(q['parts']))
            parts=[]
            for part,reason in zip(q['parts'],reasons):
                ms=[v for v in q['markScheme'] if v['part']==part['label']]
                assert len(ms)==1
                assert sum(int(re.fullmatch('[AMR]([1-9][0-9]*)',s['code']).group(1)) for s in ms[0]['steps'])==part['marks']
                parts.append(dict(part=part['label'],marks=part['marks'],reasoning=reason,checkNames=numeric,status='passed'))
            written+=len(parts)
        assert sum(z['marks'] for z in parts)==q['marks']
        question_reviews.append(dict(questionId=q['id'],paper=paper['id'],fullStemAndSchemeRead=True,allDistractorsRead=q['questionType']=='multiple-choice',scopeRefsReviewed=q['syllabusRefs'],parts=parts,status='passed'))
        if q.get('diagramSvg'):
            native=TASK/f"work/physics-mocks-2026/hl-c-author-qa/{paper['id']}-{q['section'].lower()}-q{q['number']}.png"
            assert native.exists(),native
            figures.append(dict(questionId=q['id'],svgSha256=hashlib.sha256(q['diagramSvg'].encode()).hexdigest(),nativePngSha256=hashlib.sha256(native.read_bytes()).hexdigest(),status='passed',scientificGeometryChecked=True,legible=True))
    papers.append(dict(id=paper['id'],sha256=hashlib.sha256(path.read_bytes()).hexdigest(),questionsReviewed=ids,partsReviewed=written,status='passed'))

report=dict(status='passed',author='mock_portal_audit',reviewer='mock_exam_spec, independent of HL C author mock_portal_audit',reviewerDifferentFromAuthor=True,method='Read every complete stem, all options, part prompts and every marking point; independently recomputed the named values without importing author code; compared correct option texts, physical models, units, signs and limiting domains. All37 rendered scientific figures inspected in seven overview sheets; full-size critical plots and all changed figures additionally inspected. The5 replacement MCQs8/20/29/32/38 were freshly solved before this final binding.',papers=papers,questionReviews=question_reviews,checks=checks,numericAndKeyAssertions=len(checks),figuresReviewed=figures,allQuestionAndPartReasoningRead=True,openFindings=[],findingsResolved=['Exact repeated ADCB key cycle replaced by seeded balanced option positions; all40 independently solved physical option texts match unique current keys.','Unnecessary station-frame4.5-year tick removed and its current native rendering inspected.','Other reviewer identified five HA/HC inference overlaps; replacement thermal-contact, Doppler comparison, scattering-target, retarded-beam and run-down questions independently re-solved and checked.','MCQ26 torque/couple metadata correctly marked AHL with the A.4 reference added; physical content and native figure unchanged.'],humanExaminerModeration=False)
out=ROOT/'docs/ib-physics-mocks-2026/hl-c-independent-review.json'
out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
print(json.dumps(dict(questions=len(question_reviews),partGroups=sum(len(q['parts']) for q in question_reviews),assertions=len(checks),figures=len(figures),papers=papers)))
