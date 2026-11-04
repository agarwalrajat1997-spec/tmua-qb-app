"""Original, source-anchored hard Physics HL Set B; no question-bank imports."""
from common import *
import statistics,random,re

A=Author('hl','B')
G=6.67e-11;g=9.81;c0=3.00e8;e=1.602e-19;sig=5.67e-8;mu=1.66e-27
mcqs=[];data=[];written=[]
def src(page,q,focus,doc='9.pdf'):return anchor(doc,page,q,focus)
def ck(q,name,value,expected,tol=1e-8):return A.check(f'{q}: {name}',value,expected,tol)
def fig(body,h=280):return svg(body,600,h)
def dots(x,y,kind='out'):
    return circle(x,y,8)+(circle(x,y,2) if kind=='out' else line(x-4,y-4,x+4,y+4)+line(x-4,y+4,x+4,y-4))
def spring(x,y,length=110):
    pts=[(x,y),(x+12,y)]+[(x+12+i*(length-24)/12,y+(8 if i%2 else -8)) for i in range(13)]+[(x+length,y)]
    return '<polyline points="'+' '.join(f'{a:g},{b:g}' for a,b in pts)+'" fill="none" stroke="#202020" stroke-width="2"/>'
def two_boxes(left,right):return fig(rect(80,75,170,95,left)+rect(350,75,170,95,right)+arrow(265,120,335,120),230)
def mc(n,title,code,stem,opts,correct,solution,source,changes,figure=None,level='core'):
    q=A.mcq(n,title,code,stem,opts,correct,solution,source,changes,figure,level)
    q['verification']['notes']=f'Executable numerical/dimensional checks are named MCQ{n:02d} in hl-b-author-checks.json; all distractors are addressed in the worked reasoning.'
    mcqs.append(q);return q

# A: space, time and motion. Eight different physical inference structures.
s=(2+10)*2/2+10*2+(10+6)*2/2
ck('MCQ01','piecewise displacement / m',s,48)
mc(1,'Displacement from a changing acceleration','A.1',
 r'A glider has velocity $+2.0\,\mathrm{m\,s^{-1}}$ at $t=0$. Its acceleration follows the graph. What is its displacement between $t=0$ and $t=6.0\,\mathrm{s}$?',
 [r'$28.0\,\mathrm m$',r'$36.0\,\mathrm m$',r'$40.0\,\mathrm m$',r'$48.0\,\mathrm m$'],'D',
 r'The velocities at $t=0,2,4,6\,\mathrm s$ are $2,10,10,6\,\mathrm{m\,s^{-1}}$. Each stage has constant acceleration, so its displacement is mean velocity multiplied by two seconds. The total is $[(2+10)/2](2)+10(2)+[(10+6)/2](2)=48.0\,\mathrm m$. The area under the acceleration graph gives velocity change, not displacement; omitting a stage or the nonzero starting speed produces the other underestimates.',
 src(1,3,'Acceleration-time graph; replacing mean-force inference with two-stage displacement integration'),
 'New glider, nonzero initial velocity and three constant-acceleration stages; requires reconstructing a velocity history without calculus.',
 plot([(0,4),(2,4),(2,0),(4,0),(4,-2),(6,-2)],(0,6),(-2,4),'t / s','a / (m s⁻²)',[0,2,4,6],[-2,0,2,4]))

k=4.8/(12*(36-12));ck('MCQ02','parabolic maximum height / m',k*18**2,5.4)
mc(2,'A trajectory inferred from equal heights','A.1',
 r'A small ball is launched from $(x,y)=(0,0)$ and moves without air resistance. It passes through $(12.0\,\mathrm m,4.80\,\mathrm m)$ and $(24.0\,\mathrm m,4.80\,\mathrm m)$. What is its maximum height above its launch point?',
 [r'$4.80\,\mathrm m$',r'$5.40\,\mathrm m$',r'$7.20\,\mathrm m$',r'$9.60\,\mathrm m$'],'B',
 r'The equal-height points are symmetric about $x=18\,\mathrm m$. Writing $y=Kx(36-x)$ gives $K=4.80/(12\times24)=1/60\,\mathrm{m^{-1}}$. At the vertex $y_{\max}=18^2/60=5.40\,\mathrm m$. The lower value confuses a measured height with the vertex; doubling that height, or assuming the vertex is over one measurement point, fails the two supplied coordinates.',
 src(1,2,'Projectile motion and eliminating launch variables from two measured positions'),
 'New inverse-trajectory problem: two observations determine the parabola without a supplied launch speed or angle.',
 plot([(x,k*x*(36-x)) for x in range(37)],(0,36),(0,6),'x / m','y / m',[0,12,24,36],[0,2,4,6],[((12,4.8),'P',-15,-12),((24,4.8),'Q',8,-12)]))

ck('MCQ03','light glider energy fraction',.5*(3**2)/(.5*3**2+.5*3*1**2),.75)
mc(3,'Spring release and energy sharing','A.2',
 r'Two gliders of masses $m$ and $3m$ are initially at rest on a frictionless track, with a compressed spring between them. They are released. What fraction of the released spring energy becomes kinetic energy of the lighter glider?',
 [r'$\tfrac14$',r'$\tfrac13$',r'$\tfrac34$',r'$3$'],'C',
 r'Zero initial momentum gives $mv=3mu$, so the lighter glider has speed $3u$. Its energy is $\tfrac12m(3u)^2$, while that of the heavier glider is $\tfrac12(3m)u^2$. Their ratio is $3:1$, so the required fraction is $3/4$. The $1/4$ assigns the larger energy to the larger mass; $1/3$ confuses a ratio with a fraction of the total; $3$ is the energy ratio rather than a fraction.',
 src(2,4,'Momentum and kinetic-energy changes in a two-body interaction'),
 'Changes an inelastic collision into a zero-momentum spring release and asks for energy partition.',
 fig(rect(110,120,95,55,'m')+spring(205,147,150)+rect(355,120,130,55,'3m')+line(60,178,540,178)+text(300,75,'Initially at rest; spring compressed',16,'middle'),240))

ck('MCQ04','bottom/top tension ratio',(7+1)/2,4)
mc(4,'Tension through a vertical circle','A.2',
 r'A small mass moves on a light string around a complete vertical circle of radius $R$. Air resistance is negligible and the string remains taut. At the highest point its tension is $2mg$. What is the ratio of the tension at the lowest point to the tension at the highest point?',
 [r'$2$',r'$3$',r'$4$',r'$5$'],'C',
 r'At the top, $2mg+mg=mv_T^2/R$, giving $v_T^2=3gR$. Energy conservation through a drop $2R$ gives $v_B^2=7gR$. At the bottom $T_B-mg=mv_B^2/R$, so $T_B=8mg$ and $T_B/T_T=4$. Equal-speed assumptions omit the gravitational energy change; omitting the weight in either radial force balance gives the other incorrect ratios.',
 src(2,5,'Radial force balance at the top of a vertical circle'),
 'Requires linked top/bottom force balances and energy conservation rather than a single local force equation.',
 fig(circle(300,140,85)+line(300,140,300,55,True)+circle(300,55,7)+circle(300,225,7)+text(315,100,'R')+text(325,55,'top')+text(325,228,'bottom'),270))

flow=1200/(g*6+8**2/2);ck('MCQ05','water mass flow / kg s-1',flow,13.207131851199648)
mc(5,'Pump power with an outgoing jet','A.3',
 r'A motor uses $2.00\,\mathrm{kW}$ of electrical power and delivers $60.0\%$ of it to water. The water is raised by $6.00\,\mathrm m$ and leaves as a jet at $8.00\,\mathrm{m\,s^{-1}}$. The water entering the pump has negligible speed. Take $g=9.81\,\mathrm{m\,s^{-2}}$. What mass of water is delivered each second?',
 [r'$8.16\,\mathrm{kg\,s^{-1}}$',r'$13.2\,\mathrm{kg\,s^{-1}}$',r'$20.4\,\mathrm{kg\,s^{-1}}$',r'$37.5\,\mathrm{kg\,s^{-1}}$'],'B',
 r'The useful power is $1200\,\mathrm W=\dot m(gh+v^2/2)$. Thus $\dot m=1200/(58.86+32.0)=13.2\,\mathrm{kg\,s^{-1}}$. Omitting the outgoing kinetic energy gives $20.4$; using only kinetic energy gives $37.5$; applying efficiency to only one energy transfer is inconsistent.',
 src(2,6,'Input power, efficiency and lifting a continuous mass flow'),
 'Adds a significant outgoing kinetic-energy flux; efficiency must apply to the complete energy balance.',
 fig(rect(70,180,120,55,'pump')+arrow(190,205,270,205)+line(270,205,270,70)+arrow(270,70,460,70,'8.00 m s⁻¹')+line(490,70,490,205,True)+text(505,145,'6.00 m')+text(130,165,'2.00 kW input',14,'middle'),270))

ck('MCQ06','disk angular-speed fraction',.5/(.5+2*.25),.5)
ck('MCQ06','disk kinetic-energy fraction',(.5+2*.25)*.5**2/.5,.5)
mc(6,'Rotational capture without external torque','A.4',
 r'A uniform disc of mass $M$ and radius $R$ rotates freely about its central vertical axis. Two small stationary lumps, each of mass $M/4$, fall vertically and stick at opposite points on its rim. The lumps initially have zero angular momentum about the axis. Which row gives the final angular speed and final rotational kinetic energy as fractions of their initial values? Use $I_{\rm disc}=MR^2/2$.',
 [r'$\tfrac12,\ \tfrac12$',r'$\tfrac12,\ \tfrac14$',r'$\tfrac23,\ \tfrac23$',r'$1,\ 1$'],'A',
 r'The final moment of inertia is $MR^2$, twice the original. Angular momentum conservation gives $\omega_f=\omega_i/2$. Consequently $K_f/K_i=(I_f/I_i)(\omega_f/\omega_i)^2=1/2$. The $1/4$ treats inertia as unchanged; $2/3$ omits one lump; unchanged speed/energy would require an external angular impulse and ignores dissipative capture.',
 src(3,7,'Angular momentum versus rotational energy when moment of inertia changes'),
 'Specifies a computable disc capture with two stationary lumps rather than a person changing shape.',
 fig(circle(300,140,90)+circle(210,140,12,'')+circle(390,140,12,'')+line(300,140,390,140,True)+text(345,127,'R')+text(155,112,'M/4')+text(410,112,'M/4')+text(300,35,'View from above',15,'middle'),260),'ahl')

ck('MCQ07','time-dilation factor',1/math.sqrt(1-.8**2),5/3)
mc(7,'A transverse light clock','A.5',
 r'A light clock has two parallel mirrors a distance $L$ apart, measured in the clock rest frame. A pulse makes a round trip between them. The clock moves at $0.800c$ parallel to the mirrors relative to Earth. What time does an Earth observer measure for one round trip?',
 [r'$\dfrac{6L}{5c}$',r'$\dfrac{2L}{c}$',r'$\dfrac{10L}{3c}$',r'$\dfrac{18L}{5c}$'],'C',
 r'The proper interval is $\Delta\tau=2L/c$, since emission and return occur at the same place in the clock frame. With $\gamma=5/3$, Earth measures $\gamma\Delta\tau=10L/(3c)$. Dividing by $\gamma$ reverses time dilation; $2L/c$ is the proper interval; using a linear speed correction is incompatible with the diagonal light path.',
 src(4,8,'Worldlines and the relation of moving clocks to an Earth frame'),
 'Uses a transverse optical clock and a round-trip proper interval, not selection of a rocket worldline.',
 fig(line(180,65,420,65,width=5)+line(180,215,420,215,width=5)+arrow(280,195,280,85)+arrow(320,85,320,195)+line(155,65,155,215,True)+text(140,145,'L')+arrow(430,140,550,140,'0.800c')+text(300,30,'Light path in clock frame',14,'middle'),260),'ahl')

tau=900/(.8*c0*(5/3));ck('MCQ08','traveller clock interval / microsecond',tau*1e6,2.25)
mc(8,'Timing passage of a stationary platform','A.5',
 r'A platform is $900\,\mathrm m$ long in the Earth frame. A spacecraft travelling at $0.800c$ passes both ends. What time elapses on a single clock fixed in the spacecraft between its passage of the first end and the second end? Take $c=3.00\times10^8\,\mathrm{m\,s^{-1}}$.',
 [r'$1.80\,\mu\mathrm s$',r'$2.25\,\mu\mathrm s$',r'$3.75\,\mu\mathrm s$',r'$6.25\,\mu\mathrm s$'],'B',
 r'Earth measures $\Delta t=900/(0.800c)=3.75\,\mu\mathrm s$. Both events occur at the spacecraft clock, so its proper interval is $\Delta\tau=\Delta t/\gamma=2.25\,\mu\mathrm s$. Equivalently the platform contracts to $540\,\mathrm m$ in the spacecraft frame. $3.75$ is the Earth interval; $6.25$ applies time dilation in the wrong direction; $1.80$ applies an extra speed/contraction factor.',
 src(4,9,'Lengths and event times measured in Earth and spacecraft frames'),
 'Uses one travelling clock timing two Earth-fixed ends; requires identifying the proper interval.',
 fig(line(110,185,490,185,width=5)+line(110,170,110,200)+line(490,170,490,200)+text(300,225,'900 m in Earth frame',15,'middle')+rect(95,75,80,40,'clock')+arrow(185,95,330,95,'0.800c'),270),'ahl')

# B: particulate behaviour, energy flow and circuits.
ck('MCQ09','interface temperature / Celsius',20+80/5,36)
mc(9,'Unequal thermal resistances in series','B.1',
 r'Two rods of the same material and length are joined end to end. Their diameters are $d$ and $2d$. Their sides are insulated. The free end of the thin rod is maintained at $100^\circ\mathrm C$ and the free end of the thick rod at $20^\circ\mathrm C$. What is the steady interface temperature?',
 [r'$36^\circ\mathrm C$',r'$60^\circ\mathrm C$',r'$84^\circ\mathrm C$',r'$90^\circ\mathrm C$'],'A',
 r'Thermal resistance is $L/(kA)$, so the thin rod has four times the resistance of the thick rod. The $80\,\mathrm K$ drop divides $4:1$. The thick rod has a $16\,\mathrm K$ drop, placing the interface at $36^\circ\mathrm C$. $60$ assumes equal area; $84$ reverses the resistance ratio; $90$ treats diameter as a direct temperature ratio.',
 src(5,10,'Thermal conduction dependence on rod diameter'),
 'Replaces a single-rod diameter graph with an interface-temperature inference for two series conductors.',
 fig(rect(90,120,190,40)+rect(280,100,190,80)+text(80,148,'100°C',14,'end')+text(480,148,'20°C')+text(185,105,'diameter d',14,'middle')+text(375,85,'diameter 2d',14,'middle')+text(280,210,'insulated sides; equal lengths',14,'middle'),250))

heatcap=100/(.045+.015);ck('MCQ10','liquid specific heat capacity / J kg-1 K-1',heatcap/.4,12500/3)
mc(10,'Eliminating an unknown thermal loss','B.1',
 r'A $0.400\,\mathrm{kg}$ liquid sample is in a container of negligible heat capacity. At one temperature it cools at $0.0150\,\mathrm{K\,s^{-1}}$ with the heater off. At the same temperature, a $100\,\mathrm W$ heater makes it warm at $0.0450\,\mathrm{K\,s^{-1}}$. Heat loss depends only on temperature. What is the liquid specific heat capacity?',
 [r'$1.67\times10^3\,\mathrm{J\,kg^{-1}K^{-1}}$',r'$3.33\times10^3\,\mathrm{J\,kg^{-1}K^{-1}}$',r'$4.17\times10^3\,\mathrm{J\,kg^{-1}K^{-1}}$',r'$5.56\times10^3\,\mathrm{J\,kg^{-1}K^{-1}}$'],'C',
 r'Writing $C=mc$, the loss is $0.0150C$. During heating, $100-0.0150C=0.0450C$, so $C=1667\,\mathrm{J\,K^{-1}}$ and $c=4167\,\mathrm{J\,kg^{-1}K^{-1}}$. Ignoring loss gives $5556$; omitting the sample mass gives $1667$ with the wrong physical meaning; subtracting rather than adding the magnitudes of the slopes fails the energy balance.',
 src(6,11,'Calorimetry with constant heater power'),
 'Infers heat capacity from paired heating/cooling slopes, eliminating an unknown loss.',
 plot([(0,0),(40,1.8)],(0,40),(-.6,1.8),'time from reference / s','temperature change / K',[0,20,40],[-.6,0,.6,1.2,1.8],curve2=[(0,0),(40,-.6)]))

T=(224/(.7*sig))**.25;ck('MCQ11','one-layer surface temperature / K',T,274.08907793367985)
mc(11,'Radiation balance with partial infrared absorption','B.2',
 r'A planet surface is black in the infrared and absorbs a global mean solar intensity of $224\,\mathrm{W\,m^{-2}}$. A model atmosphere is transparent to sunlight, absorbs $60.0\%$ of the surface infrared radiation and emits equally upwards and downwards. There is no other energy transfer. What is the equilibrium surface temperature? Use $\sigma=5.67\times10^{-8}\,\mathrm{W\,m^{-2}K^{-4}}$.',
 [r'$252\,\mathrm K$',r'$274\,\mathrm K$',r'$291\,\mathrm K$',r'$310\,\mathrm K$'],'B',
 r'If surface emission is $S=\sigma T^4$, the atmosphere returns $0.60S/2=0.30S$. Surface balance gives $S=224+0.30S$, hence $S=320\,\mathrm{W\,m^{-2}}$ and $T=274\,\mathrm K$. Ignoring atmospheric return gives about $251\,\mathrm K$; returning all absorbed infrared downwards violates the stipulated equal emission split and overestimates temperature.',
 src(6,12,'Surface/atmosphere radiation energy balance'),
 'Requires deriving the partial-absorption back-radiation balance rather than choosing a labelled flux.',
 fig(line(100,220,510,220,width=4)+rect(100,80,410,45,'model atmosphere')+arrow(150,35,150,205,'224 W m⁻²',95,165)+arrow(310,205,310,135,'surface IR',375,190)+arrow(440,135,440,205,'returned IR',495,170)+text(300,252,'black surface',14,'middle'),280))

ck('MCQ12','final pressure / P', (1+4)/3,5/3)
ck('MCQ12','final temperature / initial T', (1+4)/2,2.5)
mc(12,'Connecting two rigid gas vessels','B.3',
 r'Two rigid, insulated vessels contain equal numbers of molecules of the same ideal monatomic gas. Initially, vessel 1 has volume $V$, pressure $P$ and temperature $T$. Vessel 2 has volume $2V$ and pressure $2P$. A valve is opened and equilibrium is reached without external work. Which row gives the final pressure and temperature?',
 [r'$\dfrac{5P}{3},\ \dfrac{5T}{2}$',r'$\dfrac{3P}{2},\ \dfrac{3T}{2}$',r'$\dfrac{5P}{3},\ 2T$',r'$\dfrac{5P}{2},\ \dfrac{5T}{2}$'],'A',
 r'Equal molecule numbers imply $T_2=4T$ because $p_2V_2=4PV$. Internal energy conservation gives $T_f=(T+4T)/2=2.5T$. Total volume is $3V$ and total molecule number is doubled, so $P_f=2NkT_f/(3V)=5P/3$. Arithmetic averaging of pressures is invalid for unequal volumes; the other rows fail either internal-energy conservation or the final gas law.',
 src(7,13,'Gas pressure, molecular energy and internal energy'),
 'Uses two unequal vessels and a conservation inference; neither final state variable is supplied.',two_boxes('V, P, T','2V, 2P'))

freeze=4200*8/334000;ck('MCQ13','fraction freezing',freeze,0.10059880239520957)
mc(13,'Recalescence of supercooled water','B.1',
 r'Liquid water is supercooled to $-8.0^\circ\mathrm C$ in an adiabatic vessel. A seed crystal triggers partial freezing, after which ice and water coexist at $0^\circ\mathrm C$. Assume constant liquid specific heat capacity $4200\,\mathrm{J\,kg^{-1}K^{-1}}$ and specific latent heat $3.34\times10^5\,\mathrm{J\,kg^{-1}}$. What fraction of the initial water mass freezes?',
 [r'$0.025$',r'$0.101$',r'$0.899$',r'$1.00$'],'B',
 r'Taking liquid water at $0^\circ\mathrm C$ as the enthalpy reference, the initial energy per kilogram is $-c(8.0)$ and the final energy per kilogram is $-fL$. Thus $f=c(8.0)/L=0.101$. Equivalently latent energy released by freezing warms the whole sample. $0.899$ is the fraction remaining liquid; complete freezing would release excess energy; $0.025$ does not balance the quoted sensible and latent energies.',
 src(7,14,'Internal energy change during freezing'),
 'Uses an adiabatic supercooling/partial-freezing energy balance instead of identifying signs in a phase change.')

ck('MCQ14','multiplicity ratio of independent systems',(4*16)/(2*8),4)
mc(14,'Total entropy of independent subsystems','B.4',
 r'Two weakly interacting subsystems have initial multiplicities $\Omega_1=2$ and $\Omega_2=8$. After an allowed energy redistribution they have $\Omega_1=4$ and $\Omega_2=16$. Using $S=k_{\rm B}\ln\Omega$, what is the change in total entropy?',
 [r'$k_{\rm B}\ln2$',r'$k_{\rm B}\ln4$',r'$k_{\rm B}\ln8$',r'$k_{\rm B}\ln32$'],'B',
 r'Independent multiplicities multiply: $\Omega_i=2\times8=16$ and $\Omega_f=4\times16=64$. Therefore $\Delta S=k_{\rm B}\ln(64/16)=k_{\rm B}\ln4$. Adding multiplicities rather than entropies, using only one subsystem, or confusing a final multiplicity with its ratio to the initial multiplicity gives the other results.',
 src(7,15,'Entropy and multiplicity'),
 'Tests composition of independent systems and an entropy difference, not solving a single Boltzmann equation.',two_boxes('Initially: Ω₁=2, Ω₂=8','Finally: Ω₁=4, Ω₂=16'),'ahl')

dS=-400/500+(400-120)/300;ck('MCQ15','universe entropy gain / J K-1',dS,2/15)
mc(15,'Entropy generated by an actual heat engine','B.4',
 r'In one cycle, an engine takes $400\,\mathrm J$ from a reservoir at $500\,\mathrm K$ and produces $120\,\mathrm J$ of work. Its other reservoir is at $300\,\mathrm K$. What is the entropy change of the two reservoirs together?',
 [r'$0$',r'$0.133\,\mathrm{J\,K^{-1}}$',r'$0.400\,\mathrm{J\,K^{-1}}$',r'$0.800\,\mathrm{J\,K^{-1}}$'],'B',
 r'The engine returns to its initial state and rejects $400-120=280\,\mathrm J$. Thus $\Delta S=-400/500+280/300=0.133\,\mathrm{J\,K^{-1}}$. Zero would require the reversible work $400(1-300/500)=160\,\mathrm J$; the other positive values omit one reservoir or use work as transferred heat.',
 src(8,16,'Carnot efficiency and reservoir temperatures'),
 'Replaces a Carnot ratio manipulation with a complete actual-cycle energy and entropy balance.',
 fig(rect(220,35,160,45,'500 K')+rect(220,125,160,45,'engine')+rect(220,220,160,45,'300 K')+arrow(300,80,300,125,'400 J',360,110)+arrow(300,170,300,220)+arrow(380,145,500,145,'120 J'),290),'ahl')

Pbefore=(12/(2+2))**2*2;Pafter=(12/(2+6))**2*6
ck('MCQ16','external power ratio after branch removed',Pafter/Pbefore,.75)
mc(16,'Disconnecting a load with internal resistance','B.5',
 r'A cell has emf $12.0\,\mathrm V$ and internal resistance $2.00\,\Omega$. The external load is a $3.00\,\Omega$ resistor in parallel with a $6.00\,\Omega$ resistor. The $3.00\,\Omega$ branch is disconnected. What is the new total external power divided by the original total external power?',
 [r'$\tfrac14$',r'$\tfrac12$',r'$\tfrac34$',r'$\tfrac43$'],'C',
 r'Initially $R_L=2\,\Omega$, $I=3\,\mathrm A$ and $P_L=I^2R_L=18\,\mathrm W$. Afterwards $R_L=6\,\Omega$, $I=1.5\,\mathrm A$ and $P_L=13.5\,\mathrm W$. The ratio is $3/4$. Applying the current ratio directly, holding terminal voltage fixed, or counting cell/internal power as load power gives incorrect ratios.',
 src(8,17,'Current division and Kirchhoff circuit reasoning'),
 'Adds cell internal resistance and compares useful powers before and after a circuit change.',
 fig(rect(80,130,130,45,'12.0 V; 2 Ω')+line(210,152,270,152)+line(270,152,270,70)+line(270,70,360,70)+rect(360,50,100,40,'3.00 Ω')+line(460,70,520,70)+line(270,152,270,220)+line(270,220,360,220)+rect(360,200,100,40,'6.00 Ω')+line(460,220,520,220)+line(520,70,520,220)+line(520,152,555,152)+line(555,152,555,260)+line(555,260,60,260)+line(60,260,60,152)+line(60,152,80,152),290))

# C: wave behaviour. Frequencies, envelopes, geometry and moving boundaries.
tfirst=math.acos(.5)/10;ck('MCQ17','first speed threshold time / s',tfirst,math.pi/30)
mc(17,'Time inferred from an SHM acceleration graph','C.1',
 r'An oscillator has the acceleration–displacement graph shown. It is released from rest at its positive maximum displacement. When does its speed first reach $\sqrt3/2$ of its maximum speed?',
 [r'$0.0524\,\mathrm s$',r'$0.105\,\mathrm s$',r'$0.157\,\mathrm s$',r'$0.314\,\mathrm s$'],'B',
 r'The slope is $-4/0.040=-100\,\mathrm{s^{-2}}=-\omega^2$, so $\omega=10\,\mathrm{rad\,s^{-1}}$. With $x=A\cos\omega t$, $v/v_{\max}=\sin\omega t$. The first solution of $\sin\omega t=\sqrt3/2$ is $t=(\pi/3)/10=0.105\,\mathrm s$. The other values correspond to different phase fractions, including the quarter- and half-period, rather than the specified first speed.',
 src(9,18,'Inferring angular frequency from an acceleration-displacement gradient'),
 'Adds the initial phase and a first-passage speed condition after extracting the graph gradient.',
 plot([(-.04,4),(.04,-4)],(-.04,.04),(-4,4),'x / m','a / (m s⁻²)',[-.04,0,.04],[-4,0,4]))

ck('MCQ18','oscillator kinetic-energy fraction',1-(.5/.75)**2,5/9)
mc(18,'Elastic energy is not total SHM potential energy','C.1',
 r'A mass hangs from a vertical spring. The equilibrium extension is $x_0$ and its oscillation amplitude about equilibrium is $0.750x_0$. At an instant when the actual spring extension is $1.50x_0$, what fraction of the total oscillation energy is kinetic energy? The spring remains stretched.',
 [r'$\tfrac19$',r'$\tfrac49$',r'$\tfrac59$',r'$\tfrac34$'],'C',
 r'The displacement from equilibrium is $y=1.50x_0-x_0=0.50x_0$, not the whole spring extension. Using the combined gravitational and elastic SHM potential, $K/E=1-y^2/A^2=1-(0.50/0.750)^2=5/9$. $4/9$ is the potential fraction; the other fractions arise from using absolute spring extension or a linear rather than squared energy relation.',
 src(10,19,'Spring oscillations: elastic potential energy and kinetic energy'),
 'Requires shifting the origin to equilibrium and distinguishing elastic energy from combined SHM potential energy.',
 fig(line(220,35,380,35,width=4)+line(300,35,300,45)+'<g transform="translate(300 45) rotate(90)">'+spring(0,0,115)+'</g>'+line(300,160,300,170)+rect(265,170,70,45,'m')+line(150,80,440,80,True)+text(450,85,'unstretched end',13)+line(150,140,440,140,True)+text(450,145,'equilibrium',13)+line(190,80,190,140,True)+text(170,115,'x₀')+text(300,255,'Instant shown: extension 1.50 x₀',14,'middle'),285))

theta_critical=math.asin(330/1500);footprint=2*.9*math.tan(theta_critical)
ck('MCQ19','critical-cone footprint diameter / m',footprint,1.8*.22/math.sqrt(1-.22**2))
foot=200*math.tan(theta_critical)
mc(19,'A critical cone for acoustic transmission','C.3',
 r'A point sound source is $0.900\,\mathrm m$ above a flat water surface. Sound speeds are $330\,\mathrm{m\,s^{-1}}$ in air and $1500\,\mathrm{m\,s^{-1}}$ in water. In a geometric-acoustics model, only incident rays inside a limiting cone can form propagating transmitted rays. What is the limiting diameter of this cone footprint on the water? Ignore diffraction and treat both media as non-dispersive.',
 [r'$0.198\,\mathrm m$',r'$0.203\,\mathrm m$',r'$0.396\,\mathrm m$',r'$0.406\,\mathrm m$'],'D',
 r'The critical angle to the normal obeys $\sin\theta_c=v_{\rm air}/v_{\rm water}=0.220$. The limiting radius is $h\tan\theta_c$, so the diameter is $2(0.900)\tan[\sin^{-1}(0.220)]=0.406\,\mathrm m$. $0.203$ is the radius; $0.396$ substitutes sine for tangent in the footprint geometry; $0.198$ combines that small-angle substitution with a radius/diameter error. Rays at the exact limit graze the boundary in water.',
 src(10,20,'Sound transmission across an air-water boundary'),
 'Creates a point-source critical-cone footprint problem, linking the speed-ratio condition with spatial geometry instead of repeating a refracted-angle calculation.',
 fig(line(70,250,530,250)+circle(300,50,6)+text(325,50,'source')+line(300,60,300,285,True)+line(300,50,300-foot,250)+line(300,50,300+foot,250)+line(205,50,205,250,True)+text(165,155,'0.900 m',14,'middle')+line(300-foot,290,300+foot,290)+text(300,315,'limiting diameter',14,'middle')+text(470,220,'air')+text(470,280,'water'),340))

nlimit=math.sin(math.radians(50))/math.sin(math.radians(40));ck('MCQ20','limiting immersion index',nlimit,1.19175359259421)
mc(20,'Changing the medium outside a prism','C.3',
 r'A transparent solid has a critical angle of $40.0^\circ$ when surrounded by air of refractive index $1.00$. A ray inside the solid meets a surface at $50.0^\circ$ to the normal. The solid is immersed in a liquid. What is the limiting liquid refractive index below which total internal reflection still occurs?',
 [r'$0.839$',r'$1.19$',r'$1.31$',r'$1.56$'],'B',
 r'The solid index is $n_s=1/\sin40^\circ$. At the limiting condition $n_\ell=n_s\sin50^\circ=1.19$; total internal reflection requires a liquid index strictly below this limit. $1.56$ is the solid index; $0.839$ reverses the ratio; using the old critical angle as unchanged ignores immersion.',
 src(10,21,'Critical angle and refractive index'),
 'Infers the solid index in one environment and applies a different boundary condition after immersion.')

ck('MCQ21','integer bright orders strictly inside central envelope',sum(abs(m)<3 for m in range(-10,11)),5)
intensity=[]
for j in range(601):
 x=-8+j*16/600;u=math.pi*x/6;en=(math.sin(u)/u)**2 if u else 1
 intensity.append((x,en*math.cos(math.pi*x/2)**2))
mc(21,'Missing interference orders','C.3',
 r'A double-slit pattern has adjacent interference maxima separated by $2.00\,\mathrm{mm}$ on a distant screen. The first single-slit diffraction minima are at $\pm6.00\,\mathrm{mm}$ from the centre. How many bright interference maxima lie strictly inside the central diffraction maximum?',
 [r'$3$',r'$5$',r'$6$',r'$7$'],'B',
 r'The possible interference maxima are $x=2m\,\mathrm{mm}$. Inside $-6<x<6$, the integers are $m=-2,-1,0,1,2$, giving five. The nominal orders at $\pm6\,\mathrm{mm}$ coincide with diffraction zeros and are missing. Seven counts those zeros as bright; six omits the central-order counting rule; three counts only one side and the centre.',
 src(11,22,'Interference fringe order and path difference'),
 'Adds finite-slit diffraction and missing orders, requiring simultaneous envelope and interference conditions.',
 plot(intensity,(-8,8),(0,1),'screen coordinate / mm','relative intensity',[-6,-4,-2,0,2,4,6],[0,.5,1]),'ahl')

ck('MCQ22','first noncentral wavelength coincidence angle / degree',math.degrees(math.asin(3/4.2)),45.58469140280703)
mc(22,'Coincident orders from two wavelengths','C.3',
 r'Light containing wavelengths $\lambda$ and $1.50\lambda$ is normally incident on a grating of slit separation $4.20\lambda$. At what positive angle is the first non-central maximum common to both wavelengths?',
 [r'$20.9^\circ$',r'$30.0^\circ$',r'$45.6^\circ$',r'$90.0^\circ$'],'C',
 r'Coincidence requires $m\lambda=n(1.50\lambda)$, so the smallest positive integer pair is $m=3,n=2$. Hence $\sin\theta=3\lambda/(4.20\lambda)=5/7$, giving $45.6^\circ$. Using the first order of either colour does not make the positions coincide; $90^\circ$ is not a solution of either relevant order.',
 src(11,23,'Diffraction grating spacing and allowed maxima'),
 'Uses an integer coincidence condition for two colours instead of only counting one-colour orders.',
 fig(line(260,50,260,235,width=4)+arrow(80,140,245,140,'λ and 1.50λ')+line(260,140,520,140,True)+arrow(275,140,500,60)+text(420,115,'θ')+text(270,265,'slit separation 4.20λ',14,'middle'),290),'ahl')

ck('MCQ23','stretched-string frequency ratio',2/math.sqrt(1.02),1.9802950859533486)
mc(23,'A stretched string conserves its mass','C.4',
 r'A uniform string is stretched so that its vibrating length increases by $2.00\%$ and its tension becomes four times the original value. Its mass is unchanged and remains uniformly distributed. The wave speed is $v=\sqrt{F/\mu}$, where $F$ is tension and $\mu$ is mass per unit length. What is the new fundamental frequency divided by the original fundamental frequency?',
 [r'$1.96$',r'$1.98$',r'$2.00$',r'$2.04$'],'B',
 r'For fixed total mass $m$, $\mu=m/L$ and $f=(1/2L)\sqrt{F/\mu}=\tfrac12\sqrt{F/(mL)}$. Therefore $f_2/f_1=\sqrt{4/1.02}=1.98$. Holding linear density fixed gives about $1.96$; ignoring length gives $2.00$; multiplying by the length change rather than dividing gives an increase that contradicts the wavelength change.',
 src(12,24,'Harmonic frequencies of a string fixed at both ends'),
 'Requires accounting for changed linear mass density as well as tension and length.',
 fig(line(90,100,480,100)+text(285,80,'L, tension F',15,'middle')+line(90,200,488,200)+text(285,180,'1.020 L, tension 4F',15,'middle')+text(300,260,'same string; same total mass',14,'middle'),290))

beat=40e3*((340+10)/(340-10)-1);ck('MCQ24','echo beat frequency / Hz',beat,2424.242424242423)
mc(24,'A Doppler shift on reflection','C.5',
 r'A stationary sonar source also receives the reflected wave from a target approaching directly at $10.0\,\mathrm{m\,s^{-1}}$. The source frequency is $40.0\,\mathrm{kHz}$ and wave speed in the medium is $340\,\mathrm{m\,s^{-1}}$. Reflection is coherent and elastic: it preserves frequency in the target rest frame. What beat frequency is formed between the emitted signal and its echo? Here beat frequency means the absolute difference of the two frequencies.',
 [r'$1.18\,\mathrm{kHz}$',r'$1.21\,\mathrm{kHz}$',r'$2.35\,\mathrm{kHz}$',r'$2.42\,\mathrm{kHz}$'],'D',
 r'The target first acts as a moving observer and then as a moving source: $f_{\rm echo}=f(v+u)/(v-u)$. The difference is $40.0[(350/330)-1]=2.42\,\mathrm{kHz}$. A single Doppler shift gives about $1.18$ or $1.21$; doubling only the observer shift gives $2.35$ and misses the second denominator.',
 src(12,25,'Doppler shifts and dependence on relative motion'),
 'Changes one-way light redshift into a two-stage acoustic reflection with a beat-frequency observable.',
 fig(rect(80,120,115,65,'sonar')+rect(440,110,80,85,'target')+arrow(210,125,420,125,'emitted')+arrow(420,175,210,175,'echo',315,205)+arrow(485,75,365,75,'10.0 m s⁻¹'),250),'ahl')

# D: fields. Distinguish local force, potential energy and induction.
ck('MCQ25','field-null potential coefficient',4/4+1/2,1.5)
ck('MCQ25','escape-speed squared coefficient',2*(4/4+1/2),3)
mc(25,'Escape from a zero-field point','D.1',
 r'Two fixed, isolated point masses $4M$ and $M$ are separated by $6a$. Point P lies between them where their gravitational fields cancel. What minimum speed must a small test particle have at P to escape to infinity? Ignore motion of the source masses.',
 [r'$0$',r'$\sqrt{GM/a}$',r'$\sqrt{3GM/(2a)}$',r'$\sqrt{3GM/a}$'],'D',
 r'Field cancellation requires $4M/r^2=M/(6a-r)^2$, so P is $4a$ from $4M$ and $2a$ from $M$. Its potential is $-4GM/(4a)-GM/(2a)=-3GM/(2a)$. Setting $v^2/2+\phi=0$ gives $v=\sqrt{3GM/a}$. Zero force locally does not mean zero potential or zero escape energy; the other roots omit a source or the factor of two from kinetic energy.',
 src(13,27,'Gravitational field cancellation between unequal masses'),
 'Requires first locating the null and then using the summed potential to determine escape energy.',
 fig(circle(100,130,32,'4M')+circle(500,130,20,'M')+line(132,130,480,130,True)+text(300,215,'separation 6a',15,'middle')+text(300,70,'P is between the masses',15,'middle'),260),'ahl')

ck('MCQ26','central-difference field magnitude / m s-2',(10000/40000),.25)
mc(26,'A local field from nonuniform potential data','D.1',
 r'Along a radial line, the gravitational potentials at $x=0$, $20\,\mathrm{km}$ and $40\,\mathrm{km}$ are $-30$, $-26$ and $-20\,\mathrm{kJ\,kg^{-1}}$. Use a central-difference estimate to find the gravitational field at $x=20\,\mathrm{km}$. Positive $x$ is to the right.',
 [r'$0.125\,\mathrm{m\,s^{-2}}$ left',r'$0.250\,\mathrm{m\,s^{-2}}$ left',r'$0.250\,\mathrm{m\,s^{-2}}$ right',r'$250\,\mathrm{m\,s^{-2}}$ left'],'B',
 r'The central gradient is $[(-20)-(-30)]\times10^3/(40\times10^3)=+0.250\,\mathrm{J\,kg^{-1}m^{-1}}$. Field is minus the potential gradient, so it is $0.250\,\mathrm{m\,s^{-2}}$ left. The rightward answer omits the minus sign; $250$ mixes kilometres with metres; $0.125$ doubles the baseline without changing the potential difference.',
 src(13,28,'Field strength inferred from equipotential spacing'),
 'Uses unequal potential increments and a specified central-difference estimate rather than force on a particular mass.',
 fig(line(130,60,130,210)+line(300,60,300,210)+line(470,60,470,210)+text(130,40,'−30 kJ kg⁻¹',14,'middle')+text(300,40,'−26 kJ kg⁻¹',14,'middle')+text(470,40,'−20 kJ kg⁻¹',14,'middle')+text(130,240,'0 km',14,'middle')+text(300,240,'20 km',14,'middle')+text(470,240,'40 km',14,'middle')+arrow(180,280,430,280,'positive x'),310),'ahl')

vc_test=4;vfragment=2*vc_test;vinf=math.sqrt(vfragment**2-2*vc_test**2)
ck('MCQ27','moving fragment speed / initial circular speed',vfragment/vc_test,2)
ck('MCQ27','speed at infinity / initial circular speed',vinf/vc_test,math.sqrt(2))
mc(27,'A fragment escaping after an orbital explosion','D.1',
 r'A satellite moves in a circular orbit at speed $v_c$ around a fixed spherical planet. A brief internal explosion splits it into two equal-mass fragments. One fragment is instantaneously at rest relative to the planet. What is the speed of the other fragment at infinity? Ignore interactions between the fragments, take their masses as negligible relative to the planet and neglect mass loss in the explosion.',
 [r'$0$',r'$v_c$',r'$\sqrt2\,v_c$',r'$2v_c$'],'C',
 r'During the brief explosion, momentum conservation gives $mv_c=(m/2)v$, so the moving fragment initially has speed $2v_c$. Circular motion before the explosion implies $GM/r=v_c^2$. Energy conservation for that fragment after the explosion gives $v_\infty^2=(2v_c)^2-2GM/r=2v_c^2$, hence $v_\infty=\sqrt2v_c$. Zero assumes it is only at escape speed; $v_c$ misses a kinetic-energy factor; $2v_c$ ignores work done against gravity. The explosion can convert internal energy into kinetic energy, so kinetic energy need not be conserved during the split.',
 src(14,29,'Gravitational energy and escape-speed scaling'),
 'Creates a circular-initial-orbit fragmentation problem: links impulse-stage momentum with subsequent escape-energy conservation without elliptical-orbit calculations.',
 fig(circle(280,150,95)+circle(280,150,25,'M')+circle(375,150,7)+line(280,150,375,150,True)+text(325,137,'r')+arrow(375,150,375,65,'v_c',405,105)+text(280,285,'Initial circular orbit before explosion',14,'middle'),315),'ahl')

ck('MCQ28','net isolated conductor charge before/after',1-1,0)
mc(28,'Separating conductors in an external field','D.2',
 r'Two identical neutral conducting spheres A and B touch each other on insulating supports. A negatively charged rod is held near A without touching it. The spheres are separated while the rod remains in place, and then the rod is removed. Which statement is correct?',
 [r'A and B are both positive.',r'A is negative and B is positive.',r'A is positive and B is negative, with equal charge magnitudes.',r'Both spheres return to zero net charge.'],'C',
 r'Electrons are repelled away from A into B while the spheres touch. Separation traps an electron deficit on A and an equal excess on B. No charge has entered or left the isolated two-sphere system, so their final net charges are equal and opposite. Both positive would violate charge conservation; reversing signs reverses electron repulsion; removal of the rod cannot transfer electrons across the later gap.',
 src(14,30,'Electrostatic induction and the order of conducting connections'),
 'Changes a grounded plate into two isolated spheres; conservation fixes both signs and charge magnitudes.',
 fig(rect(60,110,100,50,'− − −')+circle(285,135,50,'A')+circle(385,135,50,'B')+text(300,225,'Spheres initially touch; supports insulate',14,'middle'),260))

ck('MCQ29','electron speed ratio',math.sqrt((200+50)/200),math.sqrt(1.25))
mc(29,'Electron energy along an increasing potential','D.3',
 r'An electron has kinetic energy $200\,\mathrm{eV}$ at point P. It moves to point Q, whose electric potential is $50.0\,\mathrm V$ higher than that of P. Magnetic forces and energy losses are negligible. What is its speed at Q divided by its speed at P? Non-relativistic mechanics applies.',
 [r'$0.500$',r'$0.866$',r'$1.12$',r'$1.25$'],'C',
 r'For an electron, $\Delta U=q\Delta V=-50.0\,\mathrm{eV}$, so $K_Q=250\,\mathrm{eV}$. Since $v\propto\sqrt K$, the speed ratio is $\sqrt{250/200}=1.12$. $0.866$ uses a positive charge sign; $1.25$ is the energy ratio, not the speed ratio; $0.500$ incorrectly compares the potential change with the initial energy.',
 src(15,31,'Electron motion and electric-potential energy'),
 'Uses endpoint potential-energy conservation with the electron charge sign instead of a plate-impact trajectory.')

vvec=(1,1,0);Bvec=(0,0,1);charge=-1
ck('MCQ30','electron force x component for v=(1,1,0), B=(0,0,1)',charge*(vvec[1]*Bvec[2]-vvec[2]*Bvec[1]),-1)
ck('MCQ30','electron force y component for v=(1,1,0), B=(0,0,1)',charge*(vvec[2]*Bvec[0]-vvec[0]*Bvec[2]),1)
mc(30,'Two right-hand rules for an electron','D.2',
 r'A long straight wire carries conventional current to the right. An electron above the wire moves diagonally upwards and to the right in the page. What is the direction of the magnetic force on the electron at that instant?',
 [r'Diagonally upwards and to the left.',r'Diagonally upwards and to the right.',r'Diagonally downwards and to the left.',r'Diagonally downwards and to the right.'],'A',
 r'The field above a rightward current is out of the page. For a positive charge, $\mathbf v\times\mathbf B$ would be down and right. The electron reverses that force, giving up and left, perpendicular to its velocity. Down-right misses the negative charge; the other two directions are not perpendicular to the given velocity or use the wrong wire field.',
 src(15,32,'Magnetic field of a wire and force direction on a moving charge'),
 'Requires combining a wire field with an oblique negative-particle velocity, rather than one positive particle moving normally to the wire.',
 fig(arrow(80,220,520,220,'current')+circle(300,135,8)+text(277,125,'e⁻')+arrow(300,135,380,55,'v',395,62)+text(80,40,'Plane of page',14),270))

om1=3;om2=6;Pw1=om1**2/2;Pw2=om2**2/2
ck('MCQ31','energy per cycle ratio when frequency doubles',(Pw2*2*math.pi/om2)/(Pw1*2*math.pi/om1),2)
ck('MCQ31','mean resistive power ratio when frequency doubles',Pw2/Pw1,4)
mc(31,'Energy per cycle of a rotating generator','D.4',
 r'A coil rotates uniformly in a uniform magnetic field and is connected to a fixed resistor. Its inductance and internal resistance are negligible. Its rotation frequency is doubled while everything else is unchanged. Which row gives the new energy dissipated per rotation and the new mean power, as fractions of their original values?',
 [r'$1,\ 2$',r'$2,\ 4$',r'$4,\ 4$',r'$4,\ 8$'],'B',
 r'Peak emf is $NAB\omega$, so mean resistive power $\varepsilon_0^2/(2R)$ rises by four. A rotation lasts half as long, so energy per rotation rises by two. Equating energy-per-cycle and power ratios ignores the changed duration; treating emf as power gives the first row; the last row applies the frequency factor twice.',
 src(22,'9(d)','Induced emf, load current and transferred energy','f.pdf'),
 'Replaces qualitative induction damping with separate frequency scalings of cycle energy and average power.',
 plot([(x,math.cos(2*math.pi*x)) for x in [j/100 for j in range(101)]],(0,1),(-1,1),'fraction of one original rotation','flux linkage / (NAB)',[0,.25,.5,.75,1],[-1,0,1]),'ahl')

ck('MCQ32','midpoint magnetic-field ratio',(2+1)/(1+1),1.5)
ck('MCQ32','wire force per length ratio',2*1/(1*1),2)
mc(32,'Changing one current in two long wires','D.2',
 r'Two long parallel wires are perpendicular to the page, equally far from point P midway between them. Initially each carries current $I$, in opposite directions. One current is doubled. Which row gives the new magnetic field magnitude at P and the new force per unit length between the wires, as fractions of their original values?',
 [r'$\tfrac12,\ 2$',r'$1,\ 2$',r'$\tfrac32,\ 2$',r'$2,\ 4$'],'C',
 r'At the midpoint the two opposite-current fields point in the same direction, so their magnitudes add. The field changes from $2B_0$ to $3B_0$, a factor $3/2$. Force per unit length is proportional to $I_1I_2$, which doubles. Field cancellation would apply to equal currents in the same direction at a midpoint, not the stated opposite directions; neither quantity scales as the square of the changed current alone.',
 src(15,32,'Magnetic field around a long current-carrying wire'),
 'Uses superposition at a midpoint and the separate current-product force law.',
 fig(dots(150,140,'out')+dots(450,140,'in')+circle(300,140,3)+text(150,100,'I out',14,'middle')+text(450,100,'I into page',14,'middle')+text(300,125,'P',15,'middle')+line(160,140,440,140,True)+text(300,220,'equal distances from P',14,'middle'),260))

# E: nuclear and quantum physics, atomic spectra and stars.
levels=[0,2,5,8];diffs={levels[j]-levels[i] for i in range(4) for j in range(i+1,4)}
ck('MCQ33','distinct emission photon energies',len(diffs),5)
mc(33,'Counting distinct spectral energies','E.1',
 r'An atom has four energy levels at $0$, $2.0$, $5.0$ and $8.0\,\mathrm{eV}$. Every downward transition is allowed and an excited sample populates all three excited levels. How many distinct emission wavelengths are possible, and how many absorption wavelengths can a separate cold sample in its ground state absorb?',
 [r'$6,\ 3$',r'$5,\ 6$',r'$5,\ 3$',r'$3,\ 3$'],'C',
 r'The six level pairs have energy differences $2,5,8,3,6,3\,\mathrm{eV}$: only five are distinct because $3\,\mathrm{eV}$ occurs twice. Ground-state atoms absorb to the three higher levels, giving three wavelengths. Six counts transitions rather than distinct photon energies; three emission lines counts only direct transitions to the ground state; six absorption lines assumes initially excited atoms.',
 src(16,33,'Emission and absorption spectra from level transitions'),
 'Introduces degenerate energy differences and distinguishes populated excited emitters from cold absorbers.',
 fig(''.join(line(160,235-22*v,450,235-22*v)+text(130,240-22*v,f'{v:g} eV',14,'end') for v in levels),280))

ck('MCQ34','He+ 4 to2 energy / eV',13.6*4*(1/2**2-1/4**2),10.2)
ck('MCQ34','H 2 to1 energy / eV',13.6*(1-1/2**2),10.2)
mc(34,'Matching lines of hydrogen-like ions','E.1',
 r'The energies of a hydrogen-like ion are $E_n=-13.6Z^2/n^2\,\mathrm{eV}$. A $\mathrm{He}^+$ ion emits a photon in a transition from $n=4$ to $n=2$. Which hydrogen transition emits a photon of the same energy?',
 [r'$n=2\to n=1$',r'$n=3\to n=1$',r'$n=3\to n=2$',r'$n=4\to n=3$'],'A',
 r'For $\mathrm{He}^+$, $Z=2$ and the energy is $13.6(4)(1/4-1/16)=10.2\,\mathrm{eV}$. Hydrogen $2\to1$ has $13.6(1-1/4)=10.2\,\mathrm{eV}$. The other hydrogen transitions yield $12.1$, $1.89$ and $0.661\,\mathrm{eV}$, so matching only the difference in quantum numbers is invalid.',
 src(16,34,'Validity of a one-electron Bohr model'),
 'Compares quantitative transition energies of different one-electron atoms; the energy law is supplied.','', 'ahl')

ck('MCQ35','Compton electron energy fraction',1-2/3,1/3)
mc(35,'Energy partition in Compton scattering','E.2',
 r'A photon of initial wavelength $2\lambda_C$ scatters through $90^\circ$ from an electron initially at rest, where $\lambda_C=h/(m_ec)$. What fraction of the initial photon energy becomes electron kinetic energy?',
 [r'$\tfrac16$',r'$\tfrac13$',r'$\tfrac12$',r'$\tfrac23$'],'B',
 r'At $90^\circ$, the Compton shift is $\lambda_C$, so the outgoing wavelength is $3\lambda_C$. Its energy is therefore $2/3$ of the incident energy, leaving $1/3$ as electron kinetic energy. $2/3$ is the outgoing photon fraction; $1/2$ treats a fractional wavelength increase as the same energy fraction; $1/6$ is not consistent with energy conservation.',
 src(16,35,'Compton wavelength shift and scattering angle'),
 'Requires translating the wavelength shift into an energy fraction rather than angle/frequency signs.',
 fig(arrow(70,160,285,160,'2λC')+circle(300,160,7)+arrow(300,150,300,45,'scattered photon',415,65)+line(325,160,325,135)+line(325,135,300,135)+text(350,190,'electron initially at rest',14),250),'ahl')

ck('MCQ36','threshold/first frequency from stopping voltages',(3-2)/(3-1),.5)
mc(36,'Inferring work function without a slope graph','E.2',
 r'A metal has stopping potential $V$ under monochromatic light of frequency $f$. Under light of frequency $2f$, its stopping potential is $3V$. Both frequencies are above threshold. What is the work function of the metal?',
 [r'$\tfrac14hf$',r'$\tfrac13hf$',r'$\tfrac12hf$',r'$\tfrac23hf$'],'C',
 r'Einstein equations are $eV=hf-\phi$ and $3eV=2hf-\phi$. Subtracting gives $2eV=hf$, then $\phi=hf-eV=hf/2$. The other fractions cannot satisfy both equations simultaneously; intensity changes would change emission rate, not these maximum-energy relations.',
 src(17,36,'Photoelectric maximum kinetic energy versus light frequency'),
 'Infers the intercept from two stopping-potential ratios without a pre-drawn photoelectric graph.','', 'ahl')

tmix=-2*math.log(2/3)/math.log(2)
ck('MCQ37','mixture half-total time / T',tmix,1.1699250014423126)
ck('MCQ37','sum of normalized activity at predicted time',3*2**(-tmix)+2**(-tmix/2),2)
q=mc(37,'A mixture has no single isotope half-life','E.3',
 r'A detector measures two independently decaying radionuclides X and Y. Their half-lives are $T$ and $2T$. Initially their background-corrected count-rate contributions are $3R$ and $R$. Detector efficiencies remain constant. At what time is their combined corrected count rate $2R$?',
 [r'$1.00T$',r'$1.17T$',r'$1.50T$',r'$2.00T$'],'B',
 r'The total rate is $3R\,2^{-t/T}+R\,2^{-t/(2T)}$. Let $z=2^{-t/(2T)}$. The condition becomes $3z^2+z=2$, whose physical root is $z=2/3$. Hence $t/T=-2\ln(2/3)/\ln2=1.17$. The rate halves neither at the shorter nor longer component half-life; $1.50T$ incorrectly averages the half-lives instead of adding the two exponential rates.',
 src(20,37,'Separating contributions to a measured radioactive count rate','2.pdf'),
 'Uses two independently decaying components instead of one exponential plus a constant background; infers a non-integer half-total time.',
 plot([(t,3*2**(-t)) for t in [j/100 for j in range(201)]],(0,2),(0,3),'t / T','corrected component rate / R',[0,.5,1,1.5,2],[0,1,2,3],curve2=[(t,2**(-t/2)) for t in [j/100 for j in range(201)]]),'ahl')
q['diagramCaption']='Solid curve: X. Dashed curve: Y. The total is the sum, not either curve alone.'

lost=1-((2-1)/(2+1))**2;ck('MCQ38','neutron energy fraction transferred to deuteron',lost,8/9)
mc(38,'An elastic moderating collision','E.4',
 r'A neutron of mass $m$ collides head-on elastically with a stationary deuterium nucleus of mass $2m$. What fraction of the initial neutron kinetic energy is transferred to the nucleus? Treat the particles as free during the collision.',
 [r'$\tfrac19$',r'$\tfrac49$',r'$\tfrac89$',r'$1$'],'C',
 r'Momentum gives $u=v+2V$ and relative-speed reversal gives $u=V-v$. Hence $v=-u/3$ and $V=2u/3$. The nucleus gains $\tfrac12(2m)(2u/3)^2$, which is $8/9$ of $\tfrac12mu^2$. $1/9$ is the remaining neutron-energy fraction; $4/9$ omits the target mass factor; complete transfer requires equal masses in this head-on model.',
 src(18,38,'Neutron moderation in a controlled nuclear reaction'),
 'Replaces naming reactor components with a derived elastic-collision energy-transfer efficiency.',
 fig(circle(130,140,18,'n')+arrow(155,140,305,140,'u')+circle(420,140,35,'2m')+text(420,210,'initially at rest',14,'middle'),260))

ratio=math.sqrt(100/.01)*(20000/5000)**2;ck('MCQ39','stellar radius ratio',ratio,1600)
mc(39,'Radii inferred from an HR diagram','E.5',
 r'Star X has luminosity $100L_\odot$ and surface temperature $5000\,\mathrm K$. Star Y has luminosity $0.0100L_\odot$ and surface temperature $20000\,\mathrm K$. Both are well modelled as blackbodies. What is $R_X/R_Y$?',
 [r'$25$',r'$100$',r'$400$',r'$1600$'],'D',
 r'From $L=4\pi R^2\sigma T^4$, $R_X/R_Y=\sqrt{L_X/L_Y}(T_Y/T_X)^2=100(4)^2=1600$. The value $100$ omits temperature; $400$ uses its first power; $25$ reverses the temperature factor. The cool luminous star must be vastly larger than the hot faint one.',
 src(19,39,'HR positions, luminosity, temperature and stellar classification'),
 'Requires a quantitative radius ratio rather than identifying a white dwarf.',
 plot([], (30000,3000),(-3,3),'surface temperature / K','log₁₀(L / L☉)',[30000,20000,10000,5000],[-2,0,2],[((5000,2),'X',8,-10),((20000,-2),'Y',8,-10)]))

ck('MCQ40','stellar luminosity ratio',(.04/.02)**2/4,1)
ck('MCQ40','stellar radius ratio',math.sqrt(1)/2**2,.25)
mc(40,'Parallax, flux and temperature together','E.5',
 r'Stars A and B have parallaxes $0.0400$ and $0.0200$ arc-seconds. Their received bolometric fluxes are $F$ and $F/4$ respectively. Star B has twice the surface temperature of A. Assume both stars radiate as blackbodies and extinction is negligible. What is $R_B/R_A$?',
 [r'$\tfrac18$',r'$\tfrac14$',r'$\tfrac12$',r'$1$'],'B',
 r'B is twice as far away, so $L_B/L_A=(F_B/F_A)(d_B/d_A)^2=(1/4)(2)^2=1$. Equal luminosity and twice the temperature imply $R_B/R_A=(T_A/T_B)^2=1/4$. The other choices either confuse flux with luminosity or use a first-power temperature dependence.',
 src(19,40,'Parallax distance measurement'),
 'Combines parallax, inverse-square flux and thermal luminosity to infer a radius; no direct distance-only substitution.')

# Paper 1B: synthetic laboratory data, stated calibration models and bounded errors.
D=statistics.mean([18.42,18.48,18.44])+.06;dD=(18.48-18.42)/2+.02+.01
rho=6*.0264/(math.pi*(D*1e-3)**3);frac=.03/26.40+3*dD/D;drho=rho*frac
ck('1B01a','corrected mean diameter / mm',D,18.506666666666668)
ck('1B01a','conservative diameter uncertainty / mm',dD,.06)
ck('1B01b','density / kg m-3',rho,7954.643052298526)
ck('1B01b','absolute density uncertainty / kg m-3',drho,86.40801350692365)
ck('1B01c','density inferred from regression slope / kg m-3',6*4.10/math.pi*1000,7830.42320012125)
calfig=fig(rect(65,35,190,55,'18.42 / 18.48 / 18.44')+text(160,115,'sphere readings / mm',14,'middle')+rect(355,35,155,55,'−0.06 mm')+text(435,115,'closed-jaw reading',14,'middle')+text(300,160,'Independent batch calibration',16,'middle'),180)
calplot=plot([(0,.12),(6,24.72)],(0,6),(0,26),'D³ / cm³','m / g',[0,2,4,6],[0,5,10,15,20,25])
calfig=svg(calfig.split('>',1)[1].rsplit('</svg>',1)[0]+'<g transform="translate(0 180)">'+calplot.split('>',1)[1].rsplit('</svg>',1)[0]+'</g>',600,480)
q=A.written('1B',1,'A calibrated sphere-density measurement','A.1',
 r'''A student uses the following laboratory model data to measure the density of a metal sphere. Three caliper readings, in different orientations, are $18.42$, $18.48$ and $18.44\,\mathrm{mm}$. The closed-jaw reading is $-0.06\,\mathrm{mm}$. The instrument uncertainty of each displayed reading is $\pm0.02\,\mathrm{mm}$ and the uncertainty in the zero correction is $\pm0.01\,\mathrm{mm}$.

For this question, estimate the conservative absolute uncertainty in the corrected mean diameter by adding the half-range of the repeated readings, the $0.02\,\mathrm{mm}$ instrument uncertainty and the $0.01\,\mathrm{mm}$ zero-correction uncertainty. The mass is $(26.40\pm0.03)\,\mathrm g$.

A separate calibrated batch of the same nominal material gives the straight-line fit shown, with
$$\frac{m}{\mathrm g}=4.10\left(\frac{D}{\mathrm{cm}}\right)^3+0.12.$$
The mass instrument used for this batch has not had its zero offset removed.''',
 [('a',r'Calculate the corrected mean diameter and its conservative absolute uncertainty.',2),
 ('b',r'Use $\rho=6m/(\pi D^3)$ to calculate the sphere density and its absolute uncertainty. Add fractional uncertainties for products and powers. State an appropriately rounded result in SI units.',3),
 ('c',r'Determine the density represented by the gradient of the batch graph. Interpret the nonzero intercept in terms of the batch mass instrument.',2),
 ('d',r'The student repeats the same sphere measurements 100 times, using the same unaltered caliper. They claim that all contributions to the quoted diameter uncertainty can therefore be divided by ten. Evaluate the claim and state one measurement change that would address a systematic contribution.',3)],
 [('a',[('M1',r'Mean displayed diameter is $18.4467\,\mathrm{mm}$; subtract the negative zero reading to obtain $D=18.5067\,\mathrm{mm}$.'),('A1',r'Half-range is $0.030\,\mathrm{mm}$, so $\Delta D=0.030+0.020+0.010=0.060\,\mathrm{mm}$. Report $D=(18.51\pm0.06)\,\mathrm{mm}$.')]),
 ('b',[('M1',r'Convert mass to kilograms and diameter to metres, giving $\rho=7.95464\times10^3\,\mathrm{kg\,m^{-3}}$.'),('M1',r'$\Delta\rho/\rho=0.03/26.40+3(0.060/18.5067)=0.0108626$, so $\Delta\rho=86.4\,\mathrm{kg\,m^{-3}}$.'),('A1',r'An appropriate report is $(7.95\pm0.09)\times10^3\,\mathrm{kg\,m^{-3}}$, with uncertainty and central value rounded consistently. Accept equivalent justified rounding.')]),
 ('c',[('A1',r'Since gradient $=\pi\rho/6$, $\rho=(6/\pi)(4.10)=7.8304\,\mathrm{g\,cm^{-3}}=7.83\times10^3\,\mathrm{kg\,m^{-3}}$.'),('R1',r'The $+0.12\,\mathrm g$ intercept indicates a constant positive zero offset of the batch balance in the stated linear model, rather than extra density.')]),
 ('d',[('R1',r'Repetition can reduce independent random scatter in a mean, but does not justify dividing every uncertainty component by $\sqrt{100}$.'),('R1',r'A fixed zero offset/uncertainty and an instrument calibration or resolution limitation do not disappear simply through repeated identical readings.'),('A1',r'Use a calibrated reference object to redetermine the zero/calibration, or use an independently calibrated higher-resolution micrometer; state how this addresses the systematic contribution. Rotating the sphere addresses shape/orientation variation but alone does not remove a fixed zero offset.')])],
 src(1,'1','Caliper zero correction, sphere density and cubic uncertainty','x.pdf'),
 'New repeat-reading dataset and explicit conservative error convention; adds a batch mass-versus-diameter-cubed calibration and separates random from systematic uncertainty.',calfig)
q['syllabusRefs']=['A.1','Tools'];data.append(q)

times=[0,60,120,180,240];volumes=[48.0,37.6,29.8,24.3,20.1];base=8.0
kfoam=math.log((volumes[0]-base)/(volumes[-1]-base))/240
kmax=math.log((48.4-8.3)/(19.7-8.3))/240
ck('1B02b','endpoint decay constant / s-1',kfoam,.004981975006296838)
ck('1B02b','excess-volume half-life / s',math.log(2)/kfoam,139.13100320331995)
ck('1B02c','maximum k respecting common plateau bound',kmax,.005240679078800307)
ck('1B02c','minimum excess half-life / s',math.log(2)/kmax,132.26285566003787)
ck('1B02d','central prediction at360s / cm3',base+40*math.exp(-kfoam*360),14.655)
q=A.written('1B',2,'Testing an offset exponential foam model','E.3',
 r'''A student investigates a foam layer using the laboratory model data below. Time uncertainty is negligible. Every volume reading has absolute uncertainty $\pm0.4\,\mathrm{cm^3}$.

| $t/\mathrm s$ | 0 | 60 | 120 | 180 | 240 |
|---|---:|---:|---:|---:|---:|
| $V/\mathrm{cm^3}$ | 48.0 | 37.6 | 29.8 | 24.3 | 20.1 |

An independent long-duration measurement estimates a non-collapsing volume $V_\infty=(8.0\pm0.3)\,\mathrm{cm^3}$. The proposed model is
$$V(t)=V_\infty+U_0e^{-kt},\qquad k>0.$$
The student compares the collapsible excess $U=V-V_\infty$ with a radioactive population. The volume is a model analogue, not an actual count of radioactive nuclei.''',
 [('a',r'State a pair of graph axes that would test this model using a straight line. Explain why a graph of $\ln(V/\mathrm{cm^3})$ against $t$ would not be the appropriate test.',2),
 ('b',r'Use the central values at $t=0$ and $t=240\,\mathrm s$ to determine $k$ and the half-life of the excess volume $U$. Give the unit of $k$.',3),
 ('c',r'Using the quoted bounds on the first and last volume readings and on the common value $V_\infty$, determine the largest possible $k$ and hence the smallest possible excess-volume half-life. The same $V_\infty$ must be used at both times.',3),
 ('d',r'A later observation at $t=360\,\mathrm s$ is $(18.0\pm0.4)\,\mathrm{cm^3}$. Ignoring parameter uncertainty for this diagnostic comparison, calculate the model prediction and state what the discrepancy suggests about extrapolating the model.',2)],
 [('a',[('A1',r'Plot $\ln[(V-V_\infty)/\mathrm{cm^3}]$ vertically against $t/\mathrm s$ horizontally. The predicted gradient is $-k$ and intercept is $\ln(U_0/\mathrm{cm^3})$.'),('R1',r'The nonzero plateau must first be subtracted. $\ln(V_\infty+U_0e^{-kt})$ is not a linear function of time for a nonzero plateau.')]),
 ('b',[('M1',r'$U(0)=40.0\,\mathrm{cm^3}$ and $U(240)=12.1\,\mathrm{cm^3}$, so $k=\ln(40.0/12.1)/240$.'),('A1',r'$k=4.98\times10^{-3}\,\mathrm{s^{-1}}$.'),('A1',r'$t_{1/2}=\ln2/k=139\,\mathrm s$. This halves $U$, not total $V$.')]),
 ('c',[('R1',r'Maximize the ratio by taking first reading $48.4$, last reading $19.7$ and the common plateau $8.3\,\mathrm{cm^3}$. Raising the common plateau increases this ratio because the late excess is smaller.'),('A1',r'$k_{\max}=\ln[(48.4-8.3)/(19.7-8.3)]/240=5.24\times10^{-3}\,\mathrm{s^{-1}}$.'),('A1',r'$t_{1/2,\min}=\ln2/k_{\max}=132\,\mathrm s$. It is invalid to use two different plateau values at the two endpoints.')]),
 ('d',[('A1',r'$V(360)=8.0+40.0e^{-(0.004981975)(360)}=14.655\,\mathrm{cm^3}\approx14.7\,\mathrm{cm^3}$.'),('R1',r'The $3.35\,\mathrm{cm^3}$ central discrepancy is much larger than the stated single-reading uncertainty. In the stipulated diagnostic it challenges this extrapolation; a changing collapse rate, wrong plateau or changing foam structure could be investigated. A short good fit alone does not establish validity for all later times.')])],
 src(8,'3','Foam volume data, radioactive-decay analogy and extrapolation','x.pdf'),
 'New offset model and complete numerical dataset; asks for logarithmic transformation, a shared systematic parameter bound and an independent late-time model check rather than only reading a half-life.',
 scatter(list(zip(times,volumes)),(0,260),(5,50),'t / s','V / cm³',[0,60,120,180,240],[10,20,30,40,50],errors=[(0,.4)]*5),level='ahl')
q['syllabusRefs']=['E.3','Tools'];data.append(q)

def w(n,title,code,stem,parts,solutions,page,sourceq,changes,figure=None,level='core',refs=None):
 q=A.written('2',n,title,code,stem,parts,solutions,src(page,sourceq,title,'f.pdf'),changes,figure,level)
 q['verification']['notes']=f'Executable values for every numerical part are named P2Q{n:02d} in hl-b-author-checks.json; limiting cases and units are checked in the solutions.'
 if refs:q['syllabusRefs']=refs
 assert q['marks']==10
 written.append(q);return q

# Nine ten-mark structured questions. New models/data; all five themes.
gravity=30*g*math.sin(math.radians(5));drag=(.8*300/3-gravity)/3**2
p6=(gravity+drag*6**2)*6/.8;terminal=math.sqrt(gravity/drag)
ck('P2Q01a','uphill drag coefficient / kg m-1',drag,6.038896101040467)
ck('P2Q01b','input power at6m/s / W',p6,1822.8764604606945)
ck('P2Q01c','unpowered downhill terminal speed / m s-1',terminal,2.06093529252285)
ck('P2Q01d','high-speed speed factor for eightfold power',8**(1/3),2)
w(1,'An inspection trolley on an inclined rail','A.3',
 r'''A motorized inspection trolley of mass $30.0\,\mathrm{kg}$ moves up a rail inclined at $5.00^\circ$ to the horizontal. Rolling and aerodynamic resistance have resultant magnitude $F_r=bv^2$, opposite to the motion. The motor transfers $80.0\%$ of its electrical input power to mechanical power. At a steady uphill speed of $3.00\,\mathrm{m\,s^{-1}}$, input power is $300\,\mathrm W$. Take $g=9.81\,\mathrm{m\,s^{-2}}$.''',
 [('a',r'Determine $b$ and express its unit using fundamental SI units.',3),('b',r'Calculate the electrical input power required for a steady uphill speed of $6.00\,\mathrm{m\,s^{-1}}$.',3),('c',r'The trolley is now allowed to roll downhill with its motor disengaged. Determine its terminal speed under the same resistance model.',2),('d',r'For very large uphill speeds, explain how the steady speed changes when electrical input power is multiplied by eight. State the approximation required.',2)],
 [('a',[('M1',r'Steady mechanical power is $0.800(300)=240\,\mathrm W$, so driving force is $240/3=80.0\,\mathrm N$.'),('M1',r'Balance gives $80.0=30.0(9.81)\sin5^\circ+b(3.00)^2$.'),('A1',r'$b=6.04\,\mathrm{kg\,m^{-1}}$. Since $F=bv^2$, units are $(\mathrm{kg\,m\,s^{-2}})/(\mathrm{m^2s^{-2}})=\mathrm{kg\,m^{-1}}$.')]),
 ('b',[('M1',r'At $6.00\,\mathrm{m\,s^{-1}}$, gravitational force is still $25.650\,\mathrm N$, while resistance is $b(6.00)^2=217.400\,\mathrm N$.'),('M1',r'Mechanical power is $(25.650+217.400)(6.00)=1458.30\,\mathrm W$; divide by efficiency.'),('A1',r'Input power is $1.82\times10^3\,\mathrm W$ to three significant figures. It is not eight times $300\,\mathrm W$ because the gravitational term scales only linearly with speed.')]),
 ('c',[('M1',r'At terminal speed, $bv^2=mg\sin5.00^\circ$.'),('A1',r'$v=\sqrt{25.650/6.03890}=2.06\,\mathrm{m\,s^{-1}}$ downhill.')]),
 ('d',[('R1',r'If $bv^2\gg mg\sin5^\circ$, the required mechanical power is approximately $bv^3$.'),('A1',r'With unchanged efficiency, $v\propto P_{\rm in}^{1/3}$; multiplying power by eight approximately doubles steady speed.')])],
 1,'1','New inclined inspection system, efficiency and gravity; uses force balances in opposite directions and a high-speed limiting law instead of the source car graph.',
 fig(line(70,220,520,220-450*math.tan(math.radians(5)))+'<g transform="rotate(-5 300 200)">'+rect(245,150,110,50,'30.0 kg')+'</g>'+arrow(350,145,445,145-95*math.tan(math.radians(5)),'v uphill')+arrow(245,210,155,210+90*math.tan(math.radians(5)))+text(170,250,'resistance',14)+line(70,220,520,220,True)+text(480,207,'5.00°'),280),refs=['A.2','A.3'])

r1=7.2e7;T1=21600;mass=4*math.pi**2*r1**3/(G*T1**2);GM=G*mass;r2=1.6*r1
delta=GM*(1/r1-1/r2);avg=delta/(r2-r1);rgeom=math.sqrt(r1*r2)
ck('P2Q02a','central mass / kg',mass,4.7350425912272784e26,1e12)
ck('P2Q02b','outer orbital period / h',6*1.6**1.5,12.143146215046578)
ck('P2Q02c','potential difference / J kg-1',delta,164493406.68482265,1e-6)
ck('P2Q02c','average field magnitude / m s-2',avg,3.8077177473338577)
ck('P2Q02d','radius matching average field / m',rgeom,91073596.61284932,1e-6)
w(2,'Inferring a planet field from two orbits','D.1',
 r'''A probe of negligible mass moves in a circular orbit of radius $r_1=7.20\times10^7\,\mathrm m$ around an isolated spherical planet, with orbital period $6.00\,\mathrm h$. A second probe moves in a circular orbit of radius $r_2=1.60r_1$. There is no significant atmospheric drag. Use $G=6.67\times10^{-11}\,\mathrm{N\,m^2kg^{-2}}$.''',
 [('a',r'Determine the planet mass from the first orbit.',3),('b',r'Determine the second probe orbital period.',2),('c',r'Calculate $\phi(r_2)-\phi(r_1)$ and the magnitude of the mean radial field between these radii, defined by $\langle g\rangle=[\phi(r_2)-\phi(r_1)]/(r_2-r_1)$.',3),('d',r'Show that the local field magnitude equals this mean at radius $\sqrt{r_1r_2}$, and determine that radius.',2)],
 [('a',[('M1',r'Equate gravitational and centripetal acceleration: $GM/r_1^2=4\pi^2r_1/T_1^2$.'),('M1',r'Use $T_1=21600\,\mathrm s$ in $M=4\pi^2r_1^3/(GT_1^2)$.'),('A1',r'$M=4.74\times10^{26}\,\mathrm{kg}$.')]),
 ('b',[('M1',r'For the same central mass, $T_2/T_1=(r_2/r_1)^{3/2}=1.60^{3/2}$.'),('A1',r'$T_2=12.1\,\mathrm h$ to three significant figures.')]),
 ('c',[('M1',r'$\phi=-GM/r$, so $\Delta\phi=GM(1/r_1-1/r_2)>0$.'),('A1',r'$\Delta\phi=1.64\times10^8\,\mathrm{J\,kg^{-1}}$.'),('A1',r'$\langle g\rangle=\Delta\phi/(0.60r_1)=3.81\,\mathrm{m\,s^{-2}}$. The actual field direction is inward.')]),
 ('d',[('M1',r'$\langle g\rangle=GM[(r_2-r_1)/(r_1r_2)]/(r_2-r_1)=GM/(r_1r_2)$. Equating to $GM/r^2$ gives $r=\sqrt{r_1r_2}$.'),('A1',r'$r=9.11\times10^7\,\mathrm m$. It is the geometric, rather than arithmetic, mean radius.')])],
 4,'2','New probe orbits with supplied dimensional data; extends an approximate potential-gradient question into an exact mean-field location.',
 fig(circle(300,145,105)+circle(300,145,66)+circle(300,145,23,'M')+arrow(300,145,366,145,'r₁',340,130)+arrow(300,145,300,40,'r₂',325,75),280),'ahl')

lam=math.log(2)/(3*86400);N0=(300/60/.15)/lam;Nd=N0*(1-2**-3);Egamma=Nd*550e3*e
ck('P2Q03a','constant background / min-1',(318*93-168**2)/(318+93-2*168),18)
ck('P2Q03a','half-life / day',-3*math.log(2)/math.log((168-18)/(318-18)),3)
ck('P2Q03b','decay constant / s-1',lam,2.6741789373454678e-6)
ck('P2Q03b','initial parent nuclei',N0,12464885.153280646,1e-6)
ck('P2Q03c','daughter nuclei after9days',Nd,10906774.509120565,1e-6)
ck('P2Q03c','emitted gamma energy / J',Egamma,9.60995901998613e-7,1e-15)
ck('P2Q03d','cascade photon sum / keV',210+340,550)
w(3,'Separating background and nuclear decay','E.3',
 r'''An activated sample contains a parent nuclide P that decays to a stable daughter D. Initially no D is present. Laboratory model count rates at times $0$, $3.00$ and $6.00$ days are $318$, $168$ and $93.0\,\mathrm{min^{-1}}$. The observed rate is a single exponential plus a constant background. Detector calibration shows that $15.0\%$ of parent decays are recorded, including all geometric and detection effects.

Each parent decay releases a total of $550\,\mathrm{keV}$ as gamma radiation, either directly or in a two-photon cascade. Three possible photon energies are $210$, $340$ and $550\,\mathrm{keV}$. Use $1\,\mathrm{eV}=1.602\times10^{-19}\,\mathrm J$ and one day $=86400\,\mathrm s$.''',
 [('a',r'Determine the background rate and the parent half-life. Show how the equal time intervals constrain the background.',3),('b',r'Determine the decay constant in $\mathrm{s^{-1}}$ and the initial number of parent nuclei.',2),('c',r'Determine the number of daughter nuclei and the total emitted gamma energy after $9.00$ days.',3),('d',r'Draw a minimal energy-level diagram that can account for the three gamma energies. Explain why this is consistent with quantized nuclear energies.',2)],
 [('a',[('M1',r'For background $B$, the common three-day decay factor requires $(168-B)^2=(318-B)(93-B)$.'),('A1',r'This gives $B=18.0\,\mathrm{min^{-1}}$, so corrected rates are $300$, $150$ and $75.0\,\mathrm{min^{-1}}$.'),('A1',r'The corrected rate halves in each $3.00$-day interval; $t_{1/2}=3.00$ days.')]),
 ('b',[('A1',r'$\lambda=\ln2/(3.00\times86400)=2.67\times10^{-6}\,\mathrm{s^{-1}}$.'),('A1',r'$A_0=(300/60)/0.150=33.333\,\mathrm{s^{-1}}$ and $N_0=A_0/\lambda=1.25\times10^7$. Use unrounded $\lambda$ in this calculation.')]),
 ('c',[('M1',r'After three half-lives, $N_P=N_0/8$ and $N_D=7N_0/8$.'),('A1',r'$N_D=1.09\times10^7$ daughter nuclei.'),('A1',r'Total gamma energy is $N_D(550\times10^3)(1.602\times10^{-19})=9.61\times10^{-7}\,\mathrm J$. A two-photon cascade still carries total energy $550\,\mathrm{keV}$ per decay.')]),
 ('d',[('A1',r'Draw levels at $0$, $340$ and $550\,\mathrm{keV}$, with downward arrows $550\to0$, $550\to340$ and $340\to0$. The two-step route emits $210+340=550\,\mathrm{keV}$. An intermediate level at $210\,\mathrm{keV}$ is an equivalent minimal arrangement.'),('R1',r'Discrete photon energies correspond to fixed differences between allowed nuclear energy levels, rather than a continuum of possible nuclear energies.')])],
 5,'3(b,c)','New unknown-background inverse problem, calibrated decay efficiency and a direct/cascade gamma-energy account; no gold data copied.',
 scatter([(0,318),(3,168),(6,93)],(0,6),(0,340),'time / day','observed rate / min⁻¹',[0,3,6],[0,100,200,300]),refs=['E.1','E.3'])

C=100;Tf=375;dS=C*math.log(Tf/300)+C*math.log(Tf/450);Tr=math.sqrt(300*450);W=C*(750-2*Tr)
ck('P2Q04a','direct-contact equilibrium / K',Tf,(300+450)/2)
ck('P2Q04b','direct-contact entropy gain / J K-1',dS,4.082199452025518)
ck('P2Q04c','reversible common temperature / K',Tr,367.4234614174767)
ck('P2Q04c','maximum extracted work / J',W,1515.3077165046625)
ck('P2Q04d','entropy change if both end300K / J K-1',C*math.log(300/450),-40.54651081081644)
w(4,'Finite thermal bodies and maximum work','B.4',
 r'''Two solid blocks, each of constant heat capacity $C=100\,\mathrm{J\,K^{-1}}$, start at $300\,\mathrm K$ and $450\,\mathrm K$. They are thermally insulated from their surroundings; useful work can be transferred to an external ideal work store in the second arrangement. No phase changes occur. For either block, use the supplied relation
$$\Delta S=C\ln(T_f/T_i).$$
In a second arrangement, a reversible engine operates between the two blocks, extracting work until their temperatures are equal. The engine returns to its initial state.''',
 [('a',r'Find the final temperature if the blocks are simply placed in direct thermal contact, with no work extracted.',2),('b',r'Calculate their total entropy change in direct contact and explain its sign.',3),('c',r'For the reversible-engine arrangement, determine the common final temperature and the maximum work extracted.',3),('d',r'A proposed engine would leave both blocks at $300\,\mathrm K$ and deliver the entire reduction in block internal energy as work, without any other change. Explain why energy conservation alone does not validate this proposal.',2)],
 [('a',[('M1',r'No energy leaves, so $C(T_f-300)=C(450-T_f)$.'),('A1',r'$T_f=375\,\mathrm K$.')]),
 ('b',[('M1',r'$\Delta S=100\ln(375/300)+100\ln(375/450)$.'),('A1',r'$\Delta S=+4.08\,\mathrm{J\,K^{-1}}$.'),('R1',r'Direct heat transfer through a finite temperature difference is irreversible. The isolated system entropy increases, consistently with the second law.')]),
 ('c',[('M1',r'Reversibility requires zero total entropy change: $\ln(T_f/300)+\ln(T_f/450)=0$, hence $T_f^2=300(450)$.'),('A1',r'$T_f=367\,\mathrm K$ to three significant figures.'),('A1',r'$W_{\max}=C[300+450-2\sqrt{300(450)}]=1.52\times10^3\,\mathrm J$. The reversible final temperature is below the direct-contact arithmetic mean.')]),
 ('d',[('R1',r'Both blocks at $300\,\mathrm K$ would give total entropy change $100\ln(300/450)=-40.5\,\mathrm{J\,K^{-1}}$.'),('R1',r'With no other change, the engine cannot compensate this entropy decrease. Although a first-law energy balance could be written, the proposal violates the second law and exceeds the reversible maximum work.')])],
 8,'4','Replaces a qualitative microstate example with finite bodies and a supplied entropy model; requires distinguishing energy conservation from reversible maximum work.',
 fig(rect(70,45,170,70,'300 K; C = 100 J/K')+rect(360,45,170,70,'450 K; C = 100 J/K')+rect(220,175,160,50,'reversible engine')+arrow(445,125,380,200)+arrow(220,200,155,125)+arrow(300,225,300,285,'work',350,270),320),'ahl')

u=343*(43000-40000)/(43000+40000);Lref=math.hypot(1.2,.9);diff=Lref-1.2;fmin=343/(2*diff)
inc=math.degrees(math.atan(.6/.45));crit=math.degrees(math.asin(343/1480))
ck('P2Q05a','approach speed from reflected Doppler / m s-1',u,12.397590361445783)
ck('P2Q05b','reflected path length / m',Lref,1.5)
ck('P2Q05b','lowest destructive frequency / Hz',fmin,571.6666666666667)
ck('P2Q05c','incidence angle to normal / degree',inc,53.13010235415598)
ck('P2Q05c','critical angle / degree',crit,13.400521451182279)
soundfig=fig(line(70,187.5,530,187.5)+circle(150,75,6)+circle(450,75,6)+text(130,60,'S')+text(465,60,'D')+line(150,75,450,75)+line(150,75,300,187.5)+line(300,187.5,450,75)+line(300,120,300,235,True)+text(300,55,'1.20 m',15,'middle')+line(115,75,115,187.5,True)+text(78,140,'0.450 m',14,'middle')+text(495,225,'water',14)+text(495,170,'air',14)+text(315,210,'P'),265)
w(5,'An acoustic echo and a reflecting boundary','C.5',
 r'''A small vehicle approaches a stationary vertical wall. Its onboard source emits $40.0\,\mathrm{kHz}$ sound and its receiver detects a reflected frequency of $43.0\,\mathrm{kHz}$. The speed of sound in air is $343\,\mathrm{m\,s^{-1}}$. Treat reflection at the wall as preserving the frequency in the wall frame.

In a separate stationary arrangement, a sound source S and detector D are $1.20\,\mathrm m$ apart, both $0.450\,\mathrm m$ above a flat water surface. Sound reaches D directly and by reflection at P, midway horizontally between S and D. There is no phase change of the pressure wave at reflection. The sound speed in water is $1480\,\mathrm{m\,s^{-1}}$, and both media are non-dispersive.''',
 [('a',r'Determine the speed of the approaching vehicle, accounting for both stages of the reflected Doppler shift.',3),('b',r'For the stationary arrangement, determine the lowest positive frequency producing destructive interference of the direct and reflected pressure waves at D.',3),('c',r'Use wave refraction to decide whether a propagating transmitted ray in water exists for the ray SP at the same incident angle. Show your angular calculation.',3),('d',r'Within the stated non-dispersive model, can changing only the frequency restore a transmitted ray at that incident angle? Explain.',1)],
 [('a',[('M1',r'The wall receives $f_w=fv/(v-u)$ because the source approaches it.'),('M1',r'The moving receiver then detects $f_r=f_w(v+u)/v=f(v+u)/(v-u)$.'),('A1',r'$u=v(f_r-f)/(f_r+f)=343(43.0-40.0)/(43.0+40.0)=12.4\,\mathrm{m\,s^{-1}}$.')]),
 ('b',[('M1',r'The reflected length is $2\sqrt{0.600^2+0.450^2}=1.50\,\mathrm m$; path difference is $0.300\,\mathrm m$.'),('M1',r'With no reflection phase reversal, the lowest positive destructive frequency has path difference $\lambda/2$, so $\lambda=0.600\,\mathrm m$.'),('A1',r'$f=343/0.600=572\,\mathrm{Hz}$ to three significant figures.')]),
 ('c',[('M1',r'Incident angle to the normal is $\theta_i=\tan^{-1}(0.600/0.450)=53.1^\circ$.'),('M1',r'The critical angle is $\sin^{-1}(v_{\rm air}/v_{\rm water})=\sin^{-1}(343/1480)=13.4^\circ$.'),('A1',r'Since $53.1^\circ>13.4^\circ$, the geometric-acoustics model gives total internal reflection and no propagating refracted ray. Equivalently the required refracted sine would exceed one.')]),
 ('d',[('R1',r'No. The critical angle depends on the speed ratio, which is frequency-independent under the stated non-dispersive assumption. Frequency changes the interference condition, not this transmission condition.')])],
 9,'5','Adds a reflected two-stage Doppler inverse problem; stationary geometry is recomputed for the lowest interference order and tests frequency-independent refraction.',soundfig,'ahl',refs=['C.3','C.5'])

vsel=2.4e4/.08;mi=2*e*4200/vsel**2;ri=mi*vsel/(e*.2)
ck('P2Q06a','selected speed / m s-1',vsel,300000)
ck('P2Q06b','ion mass / kg',mi,1.4952e-26,1e-34)
ck('P2Q06b','mass in unified atomic units',mi/mu,9.00722891566265)
ck('P2Q06c','analyser orbit radius / m',ri,.14)
ck('P2Q06c','semicircle impact separation / m',2*ri,.28)
ck('P2Q06d','heavier-isotope speed ratio',math.sqrt(9/10),.9486832980505138)
ionfig=fig(line(100,170,275,170,width=4)+line(100,250,275,250,width=4)+text(180,158,'positive plate',13,'middle')+text(180,275,'negative plate',13,'middle')+arrow(55,210,350,210,'ions',65,195)+arrow(245,185,245,235,'E',260,215)+text(175,130,'Selector B: to be determined',13,'middle')+'<path d="M350 210 A80 80 0 0 0 350 50" fill="none" stroke="#202020" stroke-width="2"/>'+line(350,35,350,225,True)+dots(400,90,'in')+dots(440,175,'in')+text(475,120,'analyser',14,'middle')+text(475,142,'B into page',13,'middle')+text(300,310,'Schematic: not to scale',13,'middle'),335)
w(6,'An ion velocity selector and magnetic analyser','D.3',
 r'''Singly positive ions are accelerated from rest through $4.20\,\mathrm{kV}$. They enter crossed uniform fields: electric field $E=2.40\times10^4\,\mathrm{V\,m^{-1}}$ downwards and magnetic field of magnitude $0.0800\,\mathrm T$. Selected ions travel horizontally to the right without deflection.

After the selector, they enter a region containing only a uniform magnetic field of $0.200\,\mathrm T$ into the page. They follow a semicircle and hit a detector in the entry plane. Use $e=1.602\times10^{-19}\,\mathrm C$ and $1\,\mathrm u=1.66\times10^{-27}\,\mathrm{kg}$. Motion is non-relativistic.''',
 [('a',r'Determine the selected speed and the required direction of the selector magnetic field.',2),('b',r'Determine the selected ion mass and its approximate nucleon number, taking nuclear mass to be approximately $A\,\mathrm u$.',3),('c',r'Determine the separation of the detector impact point from the analyser entry point.',3),('d',r'Ions of a heavier isotope with the same charge are accelerated through the same potential difference. Explain whether they pass the selector, and toward which plate they initially deflect.',2)],
 [('a',[('A1',r'$qE=qvB$ gives $v=E/B=3.00\times10^5\,\mathrm{m\,s^{-1}}$.'),('R1',r'The electric force is downward. The magnetic force on a positive ion moving right must be upward, requiring magnetic field into the page.')]),
 ('b',[('M1',r'$qV=mv^2/2$ gives $m=2eV/v^2$.'),('A1',r'$m=1.50\times10^{-26}\,\mathrm{kg}$.'),('A1',r'$m/\mathrm u=9.007$, so the approximate nucleon number is $A=9$.')]),
 ('c',[('M1',r'The magnetic force supplies centripetal force: $evB=mv^2/r$, so $r=mv/(eB)$.'),('A1',r'$r=0.140\,\mathrm m$.'),('A1',r'The displacement after a semicircle in the entry plane is a diameter, $2r=0.280\,\mathrm m$, above the entry point for the stated field direction.')]),
 ('d',[('R1',r'At fixed $qV$, speed is proportional to $m^{-1/2}$, so a heavier isotope is slower than the selected speed and is not transmitted undeflected.'),('R1',r'Its upward magnetic force $qvB$ is smaller than the unchanged downward electric force $qE$; it initially deflects down toward the negative plate.')])],
 11,'6','Changes electrons and plate impact into isotope selection followed by a semicircular mass analyser; asks charge-sign directions and contamination rejection.',ionfig,refs=['D.2','D.3'])

dx=1200;dct=900;beta=.8;gamma=1/math.sqrt(1-beta**2)
interval=dct*dct-dx*dx;xp=gamma*(dx-beta*dct);ctp=gamma*(dct-beta*dx)
ck('P2Q07a','Minkowski interval / m2',interval,-630000)
ck('P2Q07b','transformed x / m',xp,800)
ck('P2Q07b','transformed ct / m',ctp,-100)
ck('P2Q07c','simultaneous-frame beta',dct/dx,.75)
ck('P2Q07c','simultaneous-frame separation / m',math.sqrt(-interval),793.7253933193772)
ck('P2Q07d','required causal signal speed / c',dx/dct,4/3)
w(7,'Reversed event order and causality','A.5',
 r'''In inertial frame S, event P is a flash at $x=0$, $ct=0$. Event Q is a separately programmed flash at $x=1200\,\mathrm m$, $ct=900\,\mathrm m$. Frame S′ moves at $+0.800c$ relative to S and its origin coincides with P. Use
$$x'=\gamma(x-\beta ct),\qquad ct'=\gamma(ct-\beta x),\qquad \gamma=(1-\beta^2)^{-1/2}.$$
Use the convention $(\Delta s)^2=(c\Delta t)^2-(\Delta x)^2$.''',
 [('a',r'Calculate the invariant interval between P and Q and classify their separation.',2),('b',r'Calculate the S′ coordinates of Q and state which flash occurs first in that frame.',3),('c',r'Determine the speed of a frame in which the flashes are simultaneous and the spatial separation of the flashes in that frame.',2),('d',r'Explain why the reversed time order creates no causal paradox, and why Q cannot have been triggered by a signal emitted at P.',3)],
 [('a',[('M1',r'$(\Delta s)^2=900^2-1200^2$.'),('A1',r'$(\Delta s)^2=-6.30\times10^5\,\mathrm{m^2}<0$, so the separation is spacelike.')]),
 ('b',[('M1',r'$\gamma=1/\sqrt{1-0.800^2}=5/3$.'),('A1',r'$x^{\prime}_Q=(5/3)(1200-0.800\times900)=800\,\mathrm m$.'),('A1',r'$ct^{\prime}_Q=(5/3)(900-0.800\times1200)=-100\,\mathrm m$. Since P remains at $ct^{\prime}=0$, Q occurs first in S′.')]),
 ('c',[('A1',r'Simultaneity requires $900-\beta(1200)=0$, so the frame speed is $+0.750c$.'),('A1',r'With $\Delta ct^{\prime\prime}=0$, invariance gives $\Delta x^{\prime\prime}=\sqrt{630000}=794\,\mathrm m$. Direct Lorentz transformation gives the same value.')]),
 ('d',[('R1',r'In S, light travels only $900\,\mathrm m$ during the time between the events, less than their $1200\,\mathrm m$ separation.'),('A1',r'A signal from P to Q would require speed $\Delta x/\Delta t=(4/3)c>c$, so no allowed causal signal connects them.'),('R1',r'Spacelike events have no causal ordering enforced by a light-speed-limited influence. Different inertial observers may reverse their time order without reversing any actual cause and effect.')])],
 13,'7','New flashes, explicit negative time coordinate and a causal-signalling test; derives the simultaneous separation as an invariant check.',
 plot([(0,0),(1300,1300)],(0,1400),(0,1400),'x / m','ct / m',[0,400,800,1200],[0,400,800,1200],[((0,0),'P',10,-10),((1200,900),'Q',10,-8)]),'ahl')

L=8e26;Ts=7200;Ms=1.4*2e30;Rs=math.sqrt(L/(4*math.pi*sig*Ts**4));fuel=.70*.12*Ms
energy=fuel*.007*c0**2*.98;life=energy/L/(365.25*86400);rate=L/(.98*26.7e6*e);loss=L/(.98*c0**2)
ck('P2Q08a','stellar radius / m',Rs,646373494.397406,1e-5)
ck('P2Q08b','usable hydrogen mass / kg',fuel,2.352e29,1e15)
ck('P2Q08b','photon-supported model lifetime / yr',life,5751882272.416151,1e-3)
ck('P2Q08c','fusion reaction rate / s-1',rate,1.9084910963642005e38,1e25)
ck('P2Q08d','total mass loss / kg s-1',loss,9070294784.5805,1e-3)
w(8,'A main-sequence energy budget','E.5',
 r'''A main-sequence star is modelled as a blackbody with luminosity $8.00\times10^{26}\,\mathrm W$, effective surface temperature $7200\,\mathrm K$ and mass $1.40M_\odot$, where $M_\odot=2.00\times10^{30}\,\mathrm{kg}$. Its initial hydrogen mass fraction is $0.700$. In this simplified lifetime model, $12.0\%$ of that hydrogen mass can undergo fusion, converting $0.700\%$ of the consumed hydrogen rest mass into energy. Neutrinos carry away $2.00\%$ of the released energy; the rest supplies the stated luminosity.

For a reaction-rate estimate, use $26.7\,\mathrm{MeV}$ total energy released per completed four-proton fusion chain. Use $\sigma=5.67\times10^{-8}\,\mathrm{W\,m^{-2}K^{-4}}$, $c=3.00\times10^8\,\mathrm{m\,s^{-1}}$, $1\,\mathrm{eV}=1.602\times10^{-19}\,\mathrm J$ and one year $=3.15576\times10^7\,\mathrm s$.''',
 [('a',r'Determine the stellar radius.',2),('b',r'Estimate the model main-sequence lifetime, assuming constant luminosity and the stated accessible fuel fraction.',3),('c',r'Determine the number of completed fusion chains per second needed to supply the luminosity.',2),('d',r'Calculate the rate of stellar mass loss due to all the escaping radiation and neutrinos. Then explain how a small increase in core fusion rate can be moderated by hydrostatic feedback in a stable main-sequence star.',3)],
 [('a',[('M1',r'Use $L=4\pi R^2\sigma T^4$.'),('A1',r'$R=\sqrt{8.00\times10^{26}/[4\pi(5.67\times10^{-8})(7200)^4]}=6.46\times10^8\,\mathrm m$.')]),
 ('b',[('M1',r'Accessible hydrogen mass is $0.700(0.120)(1.40)(2.00\times10^{30})=2.352\times10^{29}\,\mathrm{kg}$.'),('M1',r'Energy available to the photon luminosity is $0.980(0.00700)(2.352\times10^{29})c^2=1.45212\times10^{44}\,\mathrm J$.'),('A1',r'$t=E/L=1.81516\times10^{17}\,\mathrm s=5.75\times10^9$ years. This estimate assumes constant luminosity, composition/fuel accessibility as specified and the given mass-conversion fraction.')]),
 ('c',[('M1',r'Photon energy available per completed chain is $0.980(26.7\times10^6)(1.602\times10^{-19})\,\mathrm J$.'),('A1',r'Number of chains per second is $L/E_{\rm photon,chain}=1.91\times10^{38}\,\mathrm{s^{-1}}$. Do not treat the neutrino fraction as part of the observed photon luminosity.')]),
 ('d',[('A1',r'All escaping power is $L/0.980$, so $\dot m=L/(0.980c^2)=9.07\times10^9\,\mathrm{kg\,s^{-1}}$.'),('R1',r'An enhanced fusion rate heats the core and raises its pressure, tending to expand the star/core against gravity.'),('R1',r'Expansion cools the core and reduces the temperature-sensitive fusion rate, providing negative feedback around hydrostatic equilibrium. Accept an equivalent physically consistent account of pressure, gravity and temperature.')])],
 15,'8(c,d,e)','New stellar model separates accessible fuel, mass-conversion efficiency and neutrino losses; quantitative rate and hydrostatic-feedback tasks use no source solar numbers.',
 fig(circle(190,140,85)+text(190,135,'7200 K',18,'middle')+text(190,165,'1.40 M☉',16,'middle')+arrow(290,95,470,60,'photons: L')+arrow(290,180,470,225,'neutrinos')+text(190,260,'blackbody star model',14,'middle'),290),refs=['B.2','E.5'])

mcoil=.08;kspring=12;turns=200;area=4e-4;gradient=8;Rload=20;amplitude=.04
omega=math.sqrt(kspring/mcoil);period=2*math.pi/omega;factor=turns*area*gradient;damp=factor**2/Rload
emf=factor*omega*amplitude;Eratio=math.exp(-damp/mcoil*(10*period))
ck('P2Q09a','undamped period / s',period,.5130199320647456)
ck('P2Q09a','initial maximum speed / m s-1',omega*amplitude,.4898979485566356)
ck('P2Q09b','initial peak induced emf / V',emf,.31353468707624677)
ck('P2Q09c','magnetic damping coefficient / kg s-1',damp,.02048)
ck('P2Q09d','energy after10cycles fraction',Eratio,.2689227740035873)
ck('P2Q09d','dimensionless weak-damping ratio',damp/(2*mcoil*omega),.01045115623587489)
coilfig=fig(line(60,150,150,150)+spring(150,150,110)+rect(260,95,95,110,'coil')+line(355,115,430,115)+rect(430,95,95,40,'20.0 Ω')+line(525,115,545,115)+line(545,115,545,225)+line(545,225,355,225)+line(355,225,355,185)+arrow(280,65,420,65,'positive x')+text(300,275,'B normal to the coil; dB/dx = 8.00 T/m',14,'middle')+text(100,120,'spring',14),310)
w(9,'Quantifying electromagnetic damping','D.4',
 r'''A light rectangular coil attached to a horizontal spring oscillates along the $x$ direction. The total moving mass is $0.0800\,\mathrm{kg}$ and the spring constant is $12.0\,\mathrm{N\,m^{-1}}$. The initial amplitude is $0.0400\,\mathrm m$. Mechanical friction is negligible.

The coil has $200$ turns, each of area $4.00\times10^{-4}\,\mathrm{m^2}$. A static magnetic field is perpendicular to the coil, with constant spatial gradient $dB/dx=8.00\,\mathrm{T\,m^{-1}}$ across the operating region. Flux linkage is $NA B(x)$, where $x$ is the coil centre. The circuit resistance is $20.0\,\Omega$; self-inductance is negligible.

For weak damping with force $F=-bv$, use the supplied amplitude envelope
$$a(t)=a_0e^{-bt/(2m)}.$$
Use the undamped period to estimate elapsed time for a given number of cycles.''',
 [('a',r'Calculate the undamped period and initial maximum speed.',2),('b',r'Calculate the initial maximum induced emf.',2),('c',r'Using the rate of electrical energy dissipation and energy conservation, show that the magnetic damping coefficient is $b=(NA\,dB/dx)^2/R$. Calculate $b$ and justify the force direction.',3),('d',r'Estimate the fraction of initial oscillation energy remaining after ten cycles. Explain the limiting effect of disconnecting the external circuit.',3)],
 [('a',[('A1',r'$T=2\pi\sqrt{m/k}=0.513\,\mathrm s$.'),('A1',r'$\omega=\sqrt{k/m}=12.247\,\mathrm{rad\,s^{-1}}$ and $v_{\max}=\omega a_0=0.490\,\mathrm{m\,s^{-1}}$.')]),
 ('b',[('M1',r'Faraday law gives $|\varepsilon|=|d(NAB)/dt|=NA|dB/dx|\,|v|$.'),('A1',r'$\varepsilon_{\max}=(200)(4.00\times10^{-4})(8.00)(0.489898)=0.314\,\mathrm V$.')]),
 ('c',[('M1',r'$P_R=\varepsilon^2/R=(NA\,dB/dx)^2v^2/R$. This energy is taken from the oscillator; $Fv=-P_R$, so $F=-[(NA\,dB/dx)^2/R]v$.'),('A1',r'$b=(0.640)^2/20.0=0.02048\,\mathrm{kg\,s^{-1}}\approx0.0205\,\mathrm{kg\,s^{-1}}$.'),('R1',r'The force opposes velocity, as required by energy conservation and Lenz law. A force in the velocity direction would increase mechanical energy while also heating the resistor without a source.')]),
 ('d',[('M1',r'$E\propto a^2$, so $E(t)/E_0=e^{-bt/m}$ and $t\approx10T=5.1302\,\mathrm s$.'),('A1',r'$E/E_0=e^{-(0.02048)(5.1302)/0.0800}=0.269$. The small ratio $b/(2m\omega)\approx0.0105$ supports the weak-damping period approximation.'),('R1',r'For an open circuit, $R\to\infty$, induced current and magnetic damping tend to zero. A changing flux can still produce an emf, but there is negligible Joule energy dissipation in this idealized limit.')])],
 19,'9','Changes a qualitative spring-magnet setup into a translating coil in a specified field gradient; derives damping from power and tests a quantitative amplitude envelope.',coilfig,'ahl',refs=['C.1','D.4'])

# The primary code A.1 locates the experimental skills item in the portal;
# the author evidence explicitly records that density calibration itself is Tools.
data[0]['syllabusRefs']=['Tools']
data[0]['verification']['notes']='Experimental Tools question: caliper calibration, cubic density uncertainty, graph interpretation and systematic versus random uncertainty. A.1 is only the portal primary-category mapping; no kinematics content is claimed.'
mcqs[6]['diagramCaption']='Mirror separation is shown in the clock rest frame; the horizontal motion arrow refers to Earth.'
for q in data+written:
 q['markScheme'][0]['steps'][0]['text']+=' Marking guidance: credit a valid subsequent method after an earlier arithmetic or graph-reading error; do not penalize the same numerical error twice. Require a correct physical model and units, and allow consistent use of rounded intermediate values.'
# Keep the physical answers fixed while making their positions balanced and
# unpredictable. Each question also gets an independent distractor permutation.
answer_position_seed=2026110426
balanced_positions=[label for label in 'ABCD' for _ in range(10)]
random.Random(answer_position_seed).shuffle(balanced_positions)
physical_targets={}
for q,position in zip(mcqs,balanced_positions):
 correct_text=next(o['text'] for o in q['options'] if o['label']==q['correctOption'])
 physical_targets[q['id']]=correct_text
 distractors=[o['text'] for o in q['options'] if o['label']!=q['correctOption']]
 random.Random(answer_position_seed+1000+q['number']).shuffle(distractors)
 distractors.insert('ABCD'.index(position),correct_text)
 q['options']=[{'label':label,'text':value} for label,value in zip('ABCD',distractors)]
 q['correctOption']=position
 q['answerSummary']=f'{position}: {correct_text}'
 for group in q['markScheme']:
  for step in group['steps']:
   step['text']=re.sub(r'(Therefore choose )[ABCD](\.)',lambda m:m[1]+position+m[2],step['text'])
assert all(sum(q['correctOption']==label for q in mcqs)==10 for label in 'ABCD')
assert len(mcqs)==40 and len(data)==2 and len(written)==9
assert all(q['marks']==10 for q in data+written)
assert {q['syllabusCode'][0] for q in mcqs}==set('ABCDE')
assert {q['syllabusCode'][0] for q in written}==set('ABCDE')
papers=[paper('hl','B','1',mcqs+data),paper('hl','B','2',written)]
A.save_checks('hl-b')
report_path=DOCS/'hl-b-author-checks.json'
report=json.loads(report_path.read_text(encoding='utf8'))
def question_check_prefix(q):
 return ('MCQ' if q['section']=='1A' else '1B' if q['section']=='1B' else 'P2Q')+f'{q["number"]:02d}'
report.update(questionCount=51,parts=sum(len(q['parts']) for p in papers for q in p['questions']),marks=150,
 mcqAnswerPositionShuffle={'method':'Stable seeded balanced correct positions plus separate seeded distractor order per question; correct option texts and physical content preserved.','seed':answer_position_seed,'counts':{label:sum(q['correctOption']==label for q in mcqs) for label in 'ABCD'},'physicalCorrectTextsSha256':hashlib.sha256(json.dumps(physical_targets,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()},
 diagrams=sum('diagramSvg' in q for p in papers for q in p['questions']),
 sourceInventorySha256=hashlib.sha256((TASK/'sources/inventory.json').read_bytes()).hexdigest(),
 scientificNotes=['All inputs and diagrams were newly authored from the cited supplied pages, without importing question-bank questions.',
 'Each question is computationally checked here; independent scientific and native diagram reviews remain required before release.',
 'First paper includes forty one-mark MCQs plus two ten-mark data investigations; second has nine ten-mark structured questions.',
 'One density Tools question uses A.1 only as a portal category; its syllabusRefs correctly identify experimental Tools.'],
 papers=[{'id':p['id'],'sha256':hashlib.sha256((CONTENT/(p['id']+'.json')).read_bytes()).hexdigest(),'questions':len(p['questions']),'marks':p['marks'],'minutes':p['minutes']} for p in papers],
 questions=[{'id':q['id'],'section':q['section'],'number':q['number'],'questionSha256':hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest(),'sourceAnchors':q['sourceAnchors'],'checks':[x['name'] for x in A.checks if x['name'].startswith(question_check_prefix(q))]} for p in papers for q in p['questions']])
report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf8',newline='\n')
print(json.dumps({'papers':len(papers),'questions':51,'marks':150,'diagrams':report['diagrams'],'authorChecks':len(A.checks),'hashes':report['papers']}))
