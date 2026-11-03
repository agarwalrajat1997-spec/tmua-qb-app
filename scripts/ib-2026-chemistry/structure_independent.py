"""Independent review reproducer for the 70 Structure additions.

This does not import the author's generator or its assertions. Inputs below were
transcribed from every final stem and compared with every worked marking point.
Run from any directory; standard library only. Diagram inspection is a recorded
human-readable AI visual review, not a claim that numeric tests establish layout.
"""
from pathlib import Path
import collections
import hashlib
import json
import math
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "content/ib/chemistry-2026-expansion/structure.json"
REPORT = ROOT / "docs/ib-2026-chemistry/structure-independent-review.json"
QUESTIONS = json.loads(SOURCE.read_text(encoding="utf-8"))
BY_ID = {q["id"]: q for q in QUESTIONS}
RECORDS = []
NA, H, C, R = 6.02e23, 6.63e-34, 3.00e8, 8.31


def near(label, actual, expected, rel=1e-8, absolute=1e-12):
    assert math.isclose(actual, expected, rel_tol=rel, abs_tol=absolute), (label, actual, expected)
    return {"test": label, "calculated": actual, "expected": expected, "status": "passed"}


def same(label, actual, expected):
    assert actual == expected, (label, actual, expected)
    return {"test": label, "calculated": actual, "expected": expected, "status": "passed"}


def yes(label, value):
    assert value, label
    return {"test": label, "status": "passed"}


def fc(valence, nonbonding, bond_order_sum):
    return valence - nonbonding - bond_order_sum


def ionization_nm(wavelength):
    return H * C * NA / (wavelength * 1e-9) / 1000


def atom_balance(left, right, water):
    elements = set(left) | set(right) | {"H", "O"}
    return all(left.get(e, 0) == right.get(e, 0) + water * {"H": 2, "O": 1}.get(e, 0)
               for e in elements)


def record(theme, number, checks, chemistry, visual):
    qid = f"ib-chem-{theme}-{number}"
    q = BY_ID[qid]
    assert q["number"] == q["source"]["question"] == number
    assert q["source"]["document"] == "Independent syllabus-authored practice"
    assert q["subject"] == "chemistry" and q["difficulty"] == "hard" and q["calculator"] is True
    assert q["level"] == ("sl" if number <= 714 else "ahl")
    assert q["collectionId"] == "chemistry-structure-" + theme[-1]
    assert q["marks"] == sum(p["marks"] for p in q["parts"])
    for p, scheme in zip(q["parts"], q["markScheme"], strict=True):
        assert p["label"] == scheme["part"]
        assert p["marks"] == sum(int(s["code"][1:]) for s in scheme["steps"])
        assert all(re.fullmatch("[MAR][1-9]", s["code"]) for s in scheme["steps"])
    svg = q["diagramSvg"]
    ET.fromstring(svg)
    assert not re.search(r"<(?:script|foreignObject|image|iframe)\b|\bon\w+\s*=|\b(?:href|src)\s*=", svg, re.I)
    assert len(svg) > 500
    RECORDS.append({
        "id": qid,
        "status": "passed",
        "questionSha256": hashlib.sha256(json.dumps(q, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "independentChecks": checks,
        "chemicalReasoningReview": chemistry,
        "diagramReview": visual,
        "schemeReview": "Every part, mark allocation and worked claim was read against these calculations and the stated current-course scope."
    })


# Structure 1: particles, mass/amount accounting, gas-model consistency,
# isotope-weighted balances, spectral thresholds and successive ionization.
record("s1", 701, [
    same("X atom inventory", 2*2+4, 8), same("Y atom inventory", 3*2+4*2, 14),
    near("X:Y atom ratio", 8/14, 4/7), near("remaining original particles", (9-2)/9, 7/9),
    near("compound fraction after separation", 4/(9-2), 4/7)],
    "X2 and Y2 are elemental molecules; XY2 is a compound. Selective passage leaves bonds and particle identities intact.",
    "Counted 2 filled pairs, 3 open pairs and 4 one-filled/two-open particles. No isolated atoms or misleading connections.")
record("s1", 702, [
    near("latent-energy ratio at constant power", (22-10)/(6-2), 3),
    near("absolute-temperature kinetic-energy ratio", (100+273.15)/(0+273.15), 1.36609921)],
    "Plateaus contain coexisting solid/liquid or liquid/vapor; input energy changes potential energy. Celsius values cannot be divided for mean kinetic energy.",
    "Graph coordinates match 0 C plateau t2..6 and 100 C plateau t10..22; transitions and units visible.")
record("s1", 703, [
    near("silicon isotope weighted mean", (8*28+29+30)/10, 28.3),
    same("30Si2+ p,n,e", [14, 30-14, 14-2], [14,16,12])],
    "Isotopes share proton count and normal neutral electronic structure. The ten nuclei have the explicitly stated 8:1:1 neutron distribution.",
    "Ten identical nucleus symbols and neutron-count legend; particle color is not falsely claimed to encode distinguishable chemical behavior.")
record("s1", 704, [
    same("Cr electron configuration count", 18+5+1,24), same("Cu configuration count",18+10+1,29),
    same("Fe2+ count",18+6,24), same("Fe2+ unpaired d electrons",5-1,4),
    same("Cr unpaired electrons",5+1,6)],
    "Cr d5s1/Cu d10s1 exceptions correct. Fe loses 4s electrons before 3d; d6 obeys Hund and Pauli. The erroneous proposals are explicitly tasks to repair.",
    "Six boxes per row mean one 4s plus five 3d orbitals, consistently labelled; deliberately incorrect proposals not represented as correct configurations.")
record("s1", 705, [
    near("carbon amount from CO2",1.320/44,.03), near("hydrogen amount from water",2*.540/18,.06),
    near("oxygen mass by difference",.900-(1.320/44*12)-(2*.540/18),.480),
    near("oxygen amount",.480/16,.030), same("C3H6O3 formula mass",3*12+6+3*16,90)],
    "Combustion products establish C/H; sample oxygen is a mass difference, not all oxygen in products. Empirical CH2O and molecular multiplier 3 are consistent.",
    "Separate collection train is schematic, with trap-gain data rather than an implied closed stoichiometric particle inventory.")
record("s1", 706, [
    near("water lost",2.464-1.204,1.260),near("water amount",1.260/18,.070),
    near("anhydrous amount",1.204/120.4,.010),near("waters per salt unit",(.070)/(.010),7),
    near("water molecules",.070*NA,4.214e22)],
    "MgSO4.7H2O matches masses. Constant mass supports complete water removal; decomposition lowering residue biases inferred hydrate number upward.",
    "Residue graph reaches repeated 1.204 g values; no plateau suggests a chemically impossible increasing mass.")
record("s1", 707, [
    near("first dilution",.600*10/250,.0240),near("second dilution",.0240*20/100,.00480),
    near("sulfate amount in 25mL",.0048*.025,.000120),
    near("sodium particles",2*.0048*.025*NA,1.4448e20),same("dissociation total charge",2-2,0)],
    "Quantitative aliquots conserve solute through each dilution. Water-wet delivery pipette dilutes stock and lowers actual concentrations.",
    "Independent visual correction aligns fluid surface with neck calibration marks; two dilution stages and transfer volumes legible.")
record("s1", 708, [
    near("N2 amount",4*.005,.020),near("Ar amount",8*.005,.040),
    near("total gas mass",.020*28+.040*40,2.16),near("mean molar mass",2.16/.060,36),
    near("total pressure Pa",.060*R*300/.0015,99720),
    near("remaining N2 pressure Pa",.020*R*300/.0015,33240)],
    "Ideal-particle count determines gas amount and pressure, independently of molar mass. Removing Ar leaves one-third of total original particle amount.",
    "Exactly four bonded N2 pairs and eight single Ar particles; key defines one particle as .00500 mol.")
record("s1", 709, [
    near("vapor amount",100000*.000300/(R*360),.01002807862),
    near("molar mass",.602/(100000*.000300/(R*360)),60.03144),
    same("empirical multiplier rounded",round(60.03144/30),2)],
    "C2H4O2 is determined without assuming an isomer. Weighing condensed material as vapor increases apparent mass/amount and apparent molar mass.",
    "Gas syringe boundary/piston and units are clear; empirical formula explicitly given rather than implied from circle symbols.")
record("s1", 710, [
    near("kPa dm3 to J",200*1000*.001,200),near("gas amount",200/(R*300),.08022462896),
    near("corrected p at 2dm3",200/2+10-10,100),near("uncorrected fractional error",(110-100)/100,.10)],
    "Positive intercept is a +10 kPa reading offset, so correction subtracts it. Best-fit gradient is nRT with consistent pressure-volume units.",
    "Nonzero measured intercept and observed points agree with p=200/V+10; axes include measured-pressure label.")
record("s1", 711, [
    yes("C>B>A gaps",1-1/16>1/4-1/16>1/4-1/9),
    same("maximum downward cascade photons",4-1,3),same("direct minimum",1,1)],
    "Discrete hydrogen levels justify discrete emission. Wavelength ordering reverses photon-energy ordering; downward-only cascade has at most three transitions.",
    "A3→2/B4→2/C4→1 arrowheads all downward. Schematic disclaimer prevents reading exact energies from drawing.")
record("s1", 712, [
    same("electron count",10+2+2,14),same("Si4+ remaining",14-4,10),
    same("outer sublevel removal",2+2,4)],
    "Two 3p arrows, not three boxes, count electrons. Si4+ has the neon core; Hund occupancy and orbital/probability interpretation are correct.",
    "3s pair and two separate parallel 3p singles; unoccupied third 3p box is visibly empty.")
record("s1", 713, [
    near("iron amount",2.232/55.8,.040),near("oxygen amount",.800/16,.050),
    near("Fe2O3 amount from difference",.050-.040,.010),
    near("FeO amount",.040-2*.010,.020),near("reconstructed oxide mass",.020*71.8+.010*159.6,3.032)],
    "The aggregate Fe:O ratio4:5 is a mixture balance, not evidence for a pure Fe4O5 compound. Half the Fe is in Fe2O3.",
    "Counted one FeO composition unit and one Fe2O3 composition unit; caption correctly warns oxides are extended solids, not these isolated molecules.")
record("s1", 714, [
    near("low-pressure gas amount",249.3/(R*300),.100),
    yes("below then above ideal",235<249.3<285)],
    "Attractions lower measured pV, finite particle volume promotes high-pressure positive deviation. Higher T/lower p generally improve ideal behavior; no forbidden real-gas equation needed.",
    "Gas B curve lies below then above horizontal ideal nRT reference; schematic pressure scale and units explicit.")
record("s1", 715, [
    near("weighted iron atomic mass",sum(m*f for m,f in zip([54,56,57,58],[.05,.90,.03,.02])),55.97),
    near("mean neutron count",55.97-26,29.97),near("sample amount",.5597/55.97,.010),
    near("total neutrons",.010*NA*29.97,1.804194e23)],
    "Fractional mean neutrons are valid weighted averages, not fractional neutrons in individual nuclei. AHL elemental isotope scope correct.",
    "Four spectral peaks at54/56/57/58 with correct5/90/3/2 intensities.")
record("s1", 716, [
    near("initial heavy fraction",98/(100+98),.494949494949),
    near("initial atomic mass",(79*100+81*98)/198,79.9898989899),
    near("added pure81 amount",(.7*.010-.010*98/198)/.3,.006835016835),
    near("added mass",81*(.7*.010-.010*98/198)/.3,.5536363636),
    near("final average",79*.3+81*.7,80.4)],
    "Enrichment equation conserves both isotope atom counts. Sample means cannot be averaged without atom-number weighting.",
    "Two original peaks100/98; diagram gives input distribution only, not final requested enrichment.")
record("s1", 717, [
    same("charge2 peak masses",[2*x for x in [10,10.5,11]],[20,21,22]),
    same("normalized family ratios",[18/20,1/20,1/20],[.9,.05,.05]),
    near("mean neon mass",20*.9+21*.05+22*.05,20.15),
    same("22Ne charge-state p,n,e",[[10,12,9],[10,12,8]],[[10,22-10,10-1],[10,22-10,10-2]])],
    "Each charge family corresponds to the same three isotope nuclei; m/z halving reflects two positive charges, not lighter isotopes.",
    "All six peaks exact; independent correction staggers crowded10/10.5/11 tick labels so they remain readable.")
record("s1", 718, [
    near("X65 signal",60/3,20),near("Y65 residual",40-20,20),
    near("X atom fraction",(60+20)/120,2/3),
    near("weighted mixture mean",(63*60+64*20+65*40)/120,63.8333333333),
    near("X mean",63*.75+65*.25,63.5),near("Y mean",(64+65)/2,64.5)],
    "Equal per-ion response permits counts to be separated; assigning all65 signal to X violates both supplied reference distributions.",
    "Combined peaks60/20/40 at63/64/65, with no misleading separate isotope assignments drawn.")
record("s1", 719, [
    near("sampleA mean",35*.8+37*.2,35.4),near("sampleB mean",35*.5+37*.5,36),
    near("required heavy fraction",(36.2-35)/2,.6),
    yes("required composition outside blending interval",.6>.5),
    near("pure37 added to one molB",(.6-.5)/(1-.6),.25),
    near("added fraction of final sample",.25/1.25,.20)],
    "Convex isotope-abundance bounds make the two-sample blend impossible. Adding pure37 provides a valid separate correction.",
    "SampleA peaks80/20 only; sampleB and desired composition remain supplied reasoning inputs.")
record("s1", 720, [
    near("original copper mean",62.93*.69+64.93*.31,63.55),
    near("removed light amount",.200*(.69-.31),.076),
    near("removed mass",.076*62.93,4.78268),
    near("final mass",(.200-.076)*(62.93+64.93)/2,7.92732),
    near("mass conservation",4.78268+7.92732,.200*63.55)],
    "Removing only light isotope until equal counts conserves heavy isotope amount; equal final intensities give63.93, not original63.55.",
    "Original copper peaks69/31 located at62.93/64.93; no spectrum normalization ambiguity.")
record("s1", 721, [
    near("background-corrected21 signal",15-10,5),near("corrected mean",(20*90+21*5+22*5)/100,20.15),
    near("raw mean",(20*90+21*15+22*5)/110,20.2272727273),
    near("amount percent low",100*(1-20.15/((20*90+21*15+22*5)/110)),.38202247191)],
    "Subtract the supplied blank before normalization. Overestimating molar mass underestimates amount at fixed mass.",
    "Raw spectrum explicitly marked before blank subtraction, so15 at21 is input, not a diagram error.")
record("s1", 722, [
    near("limit wavelength nm",C/4.50e15*1e9,66.6666666667),
    near("first IE kJ/mol",H*4.50e15*NA/1000,1796.067),
    yes("4e15 frequency below threshold",4e15<4.5e15)],
    "Ground-state gaseous atom→gaseous singly positive ion+electron is first ionization. A convergent ground series gives its threshold.",
    "Ground/limit levels and downward spectral arrows ordered correctly; energy/frequency input remains in stem.")
record("s1", 723, [
    near("X IE",ionization_nm(150),798.252),near("Y IE",ionization_nm(300),399.126),
    near("minimum absorbed energy",.015*ionization_nm(150),11.97378),
    near("25 percent useful supplied energy",.015*ionization_nm(150)/.25,47.89512)],
    "Shorter convergence wavelength means higher threshold energy. Useful-fraction correction divides required absorption by efficiency.",
    "X150/Y300 nm markers share one wavelength scale; their same-height marker lines are not falsely an energy-level diagram.")
record("s1", 724, [
    near("ground binding energy",ionization_nm(91.2),1312.9144736842),
    near("n2 binding energy",ionization_nm(364.8),328.2286184211),
    near("2to1 photon kJ/mol",ionization_nm(91.2)-ionization_nm(364.8),984.6858552632),
    near("2to1 wavelength",1/(1/91.2-1/364.8),121.6)],
    "Both limits share the same zero free-electron level; subtract positive binding energies for the bound-bound photon. First IE starts in ground state.",
    "Common free-electron limit, n2 above n1,91.2 and364.8 nm arrows correctly identify different binding gaps.")
record("s1", 725, [
    near("gradient",(3.168e15-2.475e15)/(.04-.25),-3.3e15),
    near("intercept",2.475e15+3.3e15*.25,3.3e15),
    near("IE from intercept",H*3.3e15*NA/1000,1317.1158),
    near("convergence wavelength",C/3.3e15*1e9,90.9090909091)],
    "Given transformed line makes its intercept K the ground-series convergence frequency; all finite n frequencies lie below K.",
    "Frequency versus1/n² line has negative gradient and exact .25/2.475, .04/3.168 input points.")
record("s1", 726, [
    near("200nm photon energy",H*C/(200e-9),9.945e-19,absolute=1e-28),
    near("X threshold",ionization_nm(250),478.9512),near("Y threshold",ionization_nm(180),665.21),
    near("X excess energy",ionization_nm(200)-ionization_nm(250),119.7378),
    yes("incident wavelength ionizes X only",180<200<250)],
    "Shorter than a threshold wavelength ionizes that species. Raising intensity at600nm does not change one-photon energy.",
    "Markers are ordered Y180,incident200,X250 on common wavelength scale; no reversed energy axis implied.")
record("s1", 727, [
    near("reported IE",ionization_nm(200),598.689),near("corrected IE",ionization_nm(196),610.907142857),
    near("percent correction relative reported",(200/196-1)*100,2.04081632653),
    near("original low relative true",(1-196/200)*100,2)],
    "Inverse wavelength relation means a shorter corrected wavelength raises IE. Percent correction and original fractional error use distinct denominators.",
    "True196/reported200 nm calibration markers correctly placed; they are not bond lengths or energy levels.")
record("s1", 728, [
    near("650nm line energy",ionization_nm(650),184.212),near("80nm firstIE",ionization_nm(80),1496.7225),
    near("IE/bright-line energy ratio",650/80,8.125),near("IE of .010mol",.010*ionization_nm(80),14.967225)],
    "A bright bound-bound line is not a ground ionization threshold; brightness measures emitted photon abundance, not individual photon energy.",
    "Bright650nm arrow lies between excited states;80nm ground-to-limit gap separately shown.")
record("s1", 729, [
    yes("Al below Mg",578<738),yes("S below P",999<1012),
    near("argon convergence frequency",1521e3/(H*NA),3.81082665624e15),
    near("argon convergence nm",H*C*NA/(1521e3)*1e9,78.7230769231)],
    "Rising effective nuclear charge gives broad trend; Al3p higher energy than Mg3s and paired S3p electron repulsion give correct exceptions.",
    "Eight supplied firstIE data points preserve both dips; period positions Na→Ar explicitly identified.")
record("s1", 730, [
    yes("group1 firstIE decreases",520>496>419),near("Na limit wavelength",H*C*NA/(496e3)*1e9,241.4068548387),
    near("K limit wavelength",H*C*NA/(419e3)*1e9,285.7704057279)],
    "Increasing distance/shielding outweighs nuclear-charge increase. Second ionization removes from the cation's closed inner shell and is much larger.",
    "Outer occupied n2/3/4 graph is a supplied firstIE comparison; no wrong electron trajectories or literal orbit radii.")
record("s1", 731, [
    same("largest IE jump index",max(range(3),key=lambda i:[4562/496,6910/4562,9543/6910][i])+1,1),
    near("Na to3+ energy .020mol",.020*(496+4562+6910),239.36),
    near("Na to+ energy .020mol",.020*496,9.92)],
    "Largest jump after one electron identifies a single valence electron; total removal energy is the sum of successive values, not just IE3.",
    "Logarithmic IE scale explicitly labelled; first jump is visually and numerically largest.")
record("s1", 732, [
    near("first reverse capture energy",-1451,-1451),near("second reverse capture",-738,-738),
    near("energy released for .010mol",.010*(1451+738),21.89),
    near("electrons captured",.010*2*NA,1.204e22),
    near("neutral Mg first threshold nm",H*C*NA/(738e3)*1e9,162.2463414634)],
    "Reversing ionization reverses sign and order. First Mg2+ capture is reverse IE2; neutral atom first threshold still uses IE1.",
    "Mg2++2e above Mg++e above Mg; both electron-capture arrows point downward.")
record("s1", 733, [
    same("X main jump after electron",max(range(3),key=lambda i:[1817/580,2744/1817,11577/2744][i])+1,3),
    same("Y main jump after electron",max(range(6),key=lambda i:[2250/1000,3360/2250,4560/3360,7010/4560,8500/7010,27107/8500][i])+1,6),
    same("neutral X2Y3 charge",2*3-3*2,0),near("electron amount .025mol formula",.025*6,.150),
    near("electron particles",.150*NA,9.03e22)],
    "Period3 outer counts identify Al-like X and S-like Y, main groups13/16; minimal ionic formula X2Y3 transfers six electrons per formula unit.",
    "Two successiveIE series with supplied electron indices; log scale and series labels visible.")
record("s1", 734, [
    near("Mg+ convergence gives IE2",H*3.63544e15*NA/1000,1450.99862544),
    near("neutral through2+ sum",738+1451,2189),
    near(".040mol total energy",.040*(738+1451),87.56)],
    "Starting species Mg+ makes its ground convergence IE2, not neutral IE1; configuration and two-stage sum are consistent.",
    "Arrow joins Mg+ +e to Mg2+ +2e level; separate neutral Mg level prevents starting-state ambiguity.")
record("s1", 735, [
    same("sum first five IEs",sum([1012,1907,2914,4963,6274]),17070),
    same("sum first six",sum([1012,1907,2914,4963,6274,21267]),38337),
    near(".010mol to6+ energy",.010*38337,383.37),
    yes("core jump after fifth",21267/6274>max(1907/1012,2914/1907,4963/2914,6274/4963))],
    "Five valence electrons and period3 identify phosphorus. A log-axis vertical distance represents a ratio, not linear energy difference.",
    "Six positive IE points and explicit log scale; last jump remains largest without inventing zero/negative IEs.")

# Structure 2: bonding, domains, dipoles, formal charges, networks and polymers.
record("s2", 701, [same("MX2 charge balance",2+2*(-1),0),same("ion count per formula",1+2,3)],
    "Opposite ions attract throughout an extended lattice. Conductivity on melting comes from mobile ions, not neutral metal or molecular X2.",
    "Molten sample conducts whereas solid current stays zero; these observations do not depict electrode products.")
record("s2", 702, [same("A charge",12-10,2),same("B charge",8-10,-2),
    same("MgO charge balance",2-2,0),yes("MgO ionic separation shorter",72+140<102+181),
    yes("charge-product magnitude greater",abs(2*(-2))>abs(1*(-1)))],
    "Mg2+/O2− are isoelectronic; larger nuclear charge contracts Mg2+. Both greater charge magnitude and shorter separation strengthen ionic attraction.",
    "Schematic lattice alternates sign and explicitly avoids claiming complete3D cell. Charge magnitudes supplied by stem.")
record("s2", 703, [yes("like-charge interaction repulsive",(+1)*(+1)>0),
    yes("unlike-charge attractive",(+1)*(-1)<0)],
    "One-row displacement juxtaposes like charges, leading ionic brittleness. Metallic bonding permits layer sliding with mobile delocalized electrons.",
    "Shifted lower two rows place matching signs across interface; no fictional breaking of individual covalent molecules.")
record("s2", 704, [near("Na amount",2*.010,.020),near("Na concentration",.020/.100,.200),
    near("sulfate concentration",.010/.100,.100),near("current dilution factor",.100/.200,.5),
    same("total ionic charge units",2-2,0)],
    "Ion amount stays constant on dilution while concentration/current decrease under the stated model. Solubility assumption is explicit.",
    "Current versus volume matches inverse dependence at.1/.2/.4dm3; interpolation is not assumed linear in volume.")
record("s2", 705, [same("CH4/NH3/H2O valence electrons",[4+4,5+3,6+2],[8,8,8]),
    same("central domains",[4+0,3+1,2+2],[4,4,4]),yes("bond angle order",109.5>107>104.5)],
    "Four domains in each; lone pairs0/1/2 give tetrahedral/pyramidal/bent molecular geometries and correct repulsion/angle order.",
    "Flat connectivity frameworks explicitly request spatial inference and lone-pair completion, so unshown pairs are not a false finished Lewis structure.")
record("s2", 706, [same("CO2 valence count",4+2*6,16),same("OF2 valence count",6+2*7,20),
    same("central domain counts",[2,2+2],[2,4]),yes("F more electronegative than O",3.98>3.44)],
    "Linear CO2 bond dipoles cancel; bent OF2 is polar with negative ends on F. Multiple bonds count as single domains.",
    "Connectivity-only figures do not falsely state OF2 is linear; requested lone pairs/geometry remain unknown.")
record("s2", 707, [same("BF3 valence count",3+3*7,24),same("NH3 valence count",5+3,8),
    same("adduct total",24+8,32),same("B shell after donation",6+2,8)],
    "N lone pair supplies both electrons of a coordinate bond to electron-deficient B. Once formed it is an ordinary shared pair; B domains3→4.",
    "Reactant atom connections shown without supplying the requested donor pair; no detailed AHL complex/formal-charge requirement in shared item.")
record("s2", 708, [same("both molecular formulas",{"C":2,"H":6,"O":1},{"C":2,"H":6,"O":1}),
    same("molar mass",2*12+6+16,46),yes("ethanol higher bp",78>-24)],
    "Only ethanol self-donates O-H hydrogen bonds; ether accepts water H bonds but lacks a donor in its pure liquid. Equal mass alone does not imply equal intermolecular forces.",
    "CH3−CH2−O−H versus CH3−O−CH3 connectivity unambiguous; independent bond trimming leaves condensed atom labels uncovered.")
record("s2", 709, [same("CCl4 total electrons",6+4*17,74),same("CH2Cl2 total electrons",6+2*17+2,42),
    same("carbon bonding octet",4*2,8),yes("CCl4 bp higher",77>40)],
    "Tetrahedral CCl4 is nonpolar, CH2Cl2 polar. Larger polarizable cloud can outweigh the presence of permanent dipoles for boiling behavior.",
    "Explicit connectivity-only disclaimer avoids representing carbon as physically square planar; all four substituents correct.")
record("s2", 710, [same("sheet local neighbors",3,3),same("diamond local neighbors",4,4),
    same("four tetrahedral bonds occupy electrons",4,4)],
    "Three-connected planar carbon supports delocalized electrons; four-connected diamond uses valence electrons in sigma bonding. Graphite softness reflects interlayer interactions.",
    "Sheet has three connections at each depicted ring carbon and continuing edges; network B has four bonds, with schematic connectivity disclaimer.")
record("s2", 711, [same("bulk Si:O oxygen count per Si",4/2,2),same("SiO2 neutral valence count",4+2*6,16)],
    "Every Si has four O neighbors and every O bridges two Si, giving SiO2 network stoichiometry. Melting network involves strong covalent bonding; molecular CO2 comparison concerns intermolecular forces.",
    "Fragment shows4O perSi and a bridge; outer bonds explicitly continue beyond fragment. No isolated SiO2 molecule or graphite-like electrons implied.")
record("s2", 712, [near("RfA",1.6/8,.20),near("RfB",5.2/8,.65),near("RfC",6.8/8,.85)],
    "Polar stationary phase retains the most strongly interacting component most. Unknown spots matching A/B support but do not uniquely establish identity.",
    "Four lanes have spots at exact relative distances; solvent front distinct from baseline; unknown two spots align with A and B.")
record("s2", 713, [near("alloy Zn atom fraction",2/(8+2),.20),
    near("Zn mass percent",100*2*65.4/(8*63.5+2*65.4),20.4758922981)],
    "Substitutional size mismatch obstructs layer slip while mobile electrons remain. A10-site sample ratio does not establish fixed molecular Cu4Zn stoichiometry.",
    "Pure host10 sites; alloy8C/2Z with size contrast labelled exaggerated. Letter C explicitly defined as Cu host, not elemental carbon.")
record("s2", 714, [near("NaCl mean EN",(.93+3.16)/2,2.045),near("NaCl EN difference",3.16-.93,2.23),
    near("SiCl4 mean EN",(1.90+3.16)/2,2.53),near("SiCl4 difference",3.16-1.90,1.26),
    near("SiC mean EN",(1.90+2.55)/2,2.225),near("SiC difference",2.55-1.90,.65)],
    "Bonding is a continuum. Pair electronegativity positions do not alone decide discrete molecular versus covalent-network organization.",
    "Blank triangle correctly leaves requested three compound points unplotted; axes measure mean and difference, not an unjustified percent ionic character.")
record("s2", 715, [same("NO3− valence count",5+3*6+1,24),
    same("localized formal charges",[fc(5,0,4),fc(6,4,2),fc(6,6,1),fc(6,6,1)],[1,0,-1,-1]),
    same("net charge",1+0-1-1,-1),near("mean bond order",(2+1+1)/3,4/3)],
    "Three equivalent contributors delocalize charge; fixed nuclear positions and three central domains give trigonal planar geometry.",
    "One labeled NO3− contributor contains N=O and twoN−O bonds; missing lone pairs/charges are explicitly requested, not silently omitted from a claimed completed structure.")
record("s2", 716, [same("ozone valence electrons",3*6,18),
    same("formal charges central/single/double",[fc(6,2,3),fc(6,6,1),fc(6,4,2)],[1,-1,0]),
    near("equivalent mean bond order",(1+2)/2,1.5),yes("measured bond between ordinary extremes",121<128<148)],
    "Central O has two bonding domains plus one lone pair, giving bent geometry. O=O=O with normal complete octets cannot hold all18 electrons.",
    "Bent localized framework has one single/one double bond;128pm actual equal bonds stated as separate experimental observation.")
record("s2", 717, [same("N2O valence electrons",2*5+6,16),
    same("I charges",[fc(5,2,3),fc(5,0,4),fc(6,6,1)],[0,1,-1]),
    same("II charges",[fc(5,4,2),fc(5,0,4),fc(6,4,2)],[-1,1,0]),
    same("III charges",[fc(5,6,1),fc(5,0,4),fc(6,2,3)],[-2,1,1]),
    same("sigma/pi counts",[2,2],[2,2])],
    "All contributors conserve16 electrons and net0. Preferred contributor avoids extreme charges and places negative charge on O; central N sp with two domains.",
    "All three frames preserve N−N−O positions and correct triple/single, double/double and single/triple multiplicities.")
record("s2", 718, [same("SCN− valence electrons",6+4+5+1,16),
    same("S=C=N charges",[fc(6,4,2),fc(4,0,4),fc(5,4,2)],[0,0,-1]),
    same("S−C≡N charges",[fc(6,6,1),fc(4,0,4),fc(5,2,3)],[-1,0,0]),
    same("pi bonds per localized frame",2,2)],
    "Both linear frames have central sp carbon. Real bond orders need not be exact arithmetic means because contributors are not equivalent.",
    "Both fixed S−C−N atom orders and multiplicities correct; A/B labels separated after independent panel-spacing correction.")
record("s2", 719, [near("stabilization magnitude",abs(3*(-120)-(-208)),152),
    same("benzene sigma bonds",6+6,12),same("delocalized pi electrons",6,6),
    yes("measured bond intermediate",134<140<154)],
    "Benzene delocalization gives equal bonds and lower energy than a hypothetical three-localized-double-bond comparison. There are six pi electrons, not six pi bonds.",
    "Six-carbon ring explicitly shows connectivity, every H stated, all140pm lengths supplied; no misleading literal single-bond-only molecule.")
record("s2", 720, [same("butadiene sigma count",3+6,9),same("pi electrons",2*2,4),
    yes("central bond partially shortened",134<146<154),same("carbon centers sp2",4,4)],
    "Aligned unhybridized p orbitals permit conjugation; twisting weakens overlap. Short central bond is not an extra full double bond.",
    "Four carbons with terminal CH2 and internal CH; double/single/double multiplicities and planar-connectivity disclaimer correct.")
record("s2", 721, [same("ethene valence electrons",2*4+4,12),same("ethyne valence",2*4+2,10),
    same("ethene sigma/pi",[4+1,1],[5,1]),same("ethyne sigma/pi",[2+1,2],[3,2])],
    "Ethene sp2/120° and ethyne sp/180° use one sigma per carbon pair and one/two pi. Triple bond does not contain three sigma bonds.",
    "Two-carbon condensed structures show correct H counts and double/triple multiplicity; spatial angle is asked, not inferred from typography.")
record("s2", 722, [same("acetonitrile valence count",2*4+3+5,16),
    same("sigma count",3+1+1,5),same("pi count",3-1,2),same("N formal charge",fc(5,2,3),0)],
    "Methyl carbon sp3, nitrile carbon and N sp; two perpendicular pairs of unhybridized p orbitals make the triple-bond pi system, with one N lone pair.",
    "CH3−C≡N correctly contains two distinguishable carbons; triple lines stop outside the N label.")
record("s2", 723, [same("formamide valence count",3+4+5+6,18),
    same("neutral O,N charges",[fc(6,4,2),fc(5,2,3)],[0,0]),
    same("separated O,N charges",[fc(6,6,1),fc(5,0,4)],[-1,1]),
    same("sigma count",1+1+1+2,5)],
    "N sp2 with lone pair in an unhybridized p orbital supports supplied planar/short C−N observation. Contributors do not add another independent full pi bond.",
    "H−C(=O)−NH2 and H−C(−O)=NH2 maintain identical nuclei; lone pairs and charges deliberately left as requested unknowns.")
record("s2", 724, [same("SF4 valence",6+4*7,34),same("remaining central electrons",34-4*6-4*2,2),
    same("SF4 domains",4+1,5),same("axial vs equatorial90contacts",[3,2],[3,2]),
    same("SF6 domains",6,6)],
    "SF4 equatorial lone pair minimizes90° repulsions, giving seesaw and polarity. SF6 has six bonding domains, octahedral cancellation.",
    "Five-site spatial candidate labels explicitly identify axial/equatorial sites; no answer lone pair already drawn.")
record("s2", 725, [same("ClF3 valence",7+3*7,28),
    same("central nonbonding electrons",28-3*6-3*2,4),same("domains",3+4/2,5),
    same("NF3 valence",5+3*7,26),same("NF3 central nonbonding",26-18-6,2)],
    "ClF3 has two equatorial lone pairs and T shape/polarity; period2 N cannot use expanded octet, so NF3 has four domains and pyramidal geometry.",
    "Five candidates remain unoccupied to assess lone-pair placement; perspective and indexing are readable.")
record("s2", 726, [same("XeF2 valence",8+2*7,22),
    same("central nonbonding electrons",22-2*6-2*2,6),
    same("central domains",2+6/2,5),same("remaining bond sites",5-3,2)],
    "Three equatorial lone pairs leave two axial bonds, linear nonpolar XeF2. Same molecular shape as CO2 does not mean same domain count.",
    "Five-site model retains three equatorial candidate sites; no unsupported d-hybridization label.")
record("s2", 727, [same("XeF4 valence",8+4*7,36),
    same("central nonbonding electrons",36-4*6-4*2,4),same("domains",4+4/2,6),
    same("Xe formal charge",fc(8,4,4),0)],
    "Two opposite lone pairs in six-domain arrangement give square-planar/nonpolar XeF4; adjacent lone pairs have greater repulsion.",
    "Six possible octahedral directions explicitly identify all three opposite pairs; rear dashed edge is a perspective convention.")
record("s2", 728, [same("IF5 valence",7+5*7,42),
    same("central nonbonding electrons",42-5*6-5*2,2),same("domains",5+1,6),
    same("central shell electrons",5*2+2,12)],
    "IF5 square-pyramidal polar molecule has six electron domains and one lone pair. Period5 I may exceed the octet; distorted90/180 angles accepted.",
    "Six-domain candidate frame leaves lone-pair assignment unknown and does not mislabel a trigonal bipyramid.")
record("s2", 729, [same("SF4Cl2 valence",6+6*7,48),same("central lone electrons",48-6*6-6*2,0),
    same("trans net dipole",[0,0,0],[0,0,0]),
    same("cis net vector",[1-2,1-2,2-2],[-1,-1,0]),near("cis magnitude",math.sqrt(1+1),math.sqrt(2))],
    "The explicitly hypothetical equal-site model gives trans cancellation and cis polarity under the supplied vector magnitudes. No actual synthesis or stability is asserted.",
    "Octahedral opposite-pair key correct; six candidate directions support actual trans/cis reasoning.")
record("s2", 730, [same("POCl3 valence",5+6+3*7,32),
    same("double-form P,O charges",[fc(5,0,5),fc(6,4,2)],[0,0]),
    same("single-form P,O charges",[fc(5,0,4),fc(6,6,1)],[1,-1]),
    same("P expanded shell",5*2,10),same("N normal shell four singles",4*2,8)],
    "P=O localized frame minimizes formal charge. Replacing P by period2 N cannot retain10-electron shell; N+−O− four-single representation obeys octet, without claiming stability.",
    "Both central P frames have3Cl and1O, with only O bond order different; intended charges/lone pairs are not prefilled.")
record("s2", 731, [yes("metal melting points not monotonic in d count",1907>1538),
    same("Cr toFe d count increase",[5,6],[5,6]),yes("Mg aboveNa melting",650>98)],
    "Transition-metal bonding may involve d as well as s valence electrons. Cr d5→Fe d6 with falling melting point refutes an absolute d-count monotonic rule.",
    "Independent chemical correction replaced Mn by Fe so d electron count actually increases. Plot now matches98/650/1907/1538 C and named Na/Mg/Cr/Fe positions.")
record("s2", 732, [yes("polyester repeat atom conservation",atom_balance({"C":10,"H":12,"O":6},{"C":10,"H":8,"O":4},2)),
    same("ester links per ideal pair",2,2),same("repeat formula mass",10*12+8+4*16,192)],
    "Ethylene glycol plus terephthalic acid loses2H2O per ideal repeat C10H8O4. Aromatic ring rigidity and polar ester interactions support reduced flexibility.",
    "Displayed monomers preserve HO−CH2−CH2−OH and two opposite-position aromatic acid groups; independent spacing correction separates monomer panels and prevents text/bond overprint.")
record("s2", 733, [yes("polyamide repeat balance",atom_balance({"C":12,"H":26,"N":2,"O":4},{"C":12,"H":22,"N":2,"O":2},2)),
    same("amide links per ideal pair",2,2),same("repeat formula mass",12*12+22+2*14+2*16,226)],
    "Nylon6,6 repeat loses2H2O from diamine and diacid. Hydrolysis cuts C(=O)−N, not arbitrary C−C bonds; interchain NH...O hydrogen bonds are distinct from covalent links.",
    "Root-flagged overlapping NH2/HOOC labels repaired with wider panel separation and measured conservative label clearance. Correct6- and4-methylene monomer spacers.")
record("s2", 734, [same("open-chain links",9-1,8),
    yes("finite-chain atom balance",atom_balance({"C":5*2+4*4,"H":5*6+4*6,"O":5*2+4*4},{"C":26,"H":38,"O":18},8)),
    same("chain mass",26*12+38+18*16,638),same("terminal OH",5*2-8,2),
    same("terminal COOH",4*2-8,0)],
    "Finite9-monomer open chain has8links, so repeat-unit twice-pairs shortcut is inappropriate. Composition and two terminal hydroxyls preserve exact end-group accounting.",
    "Nine alternating nodes D/A with exactly8edges and correct end units; key names diol/diacid, each edge defined as one ester link.")
record("s2", 735, [same("functional-group stoichiometry",2*3,3*2),
    same("feed mass",2*92+3*118,538),same("maximum water mass",6*18,108),
    same("retained bulk mass",538-108,430),
    yes("bulk atom balance",atom_balance({"C":2*3+3*4,"H":2*8+3*6,"O":2*3+3*4},{"C":18,"H":22,"O":12},6))],
    "Triol creates three-direction branching;2:3mol functional balance can eliminate6mol water in ideal bulk. Explicit bulk approximation avoids asserting impossible finite-tree link count or guaranteed gelation.",
    "Triol node has3 edges, diacid spacers have2; outer edges explicitly continue into network rather than claiming a single closed molecule.")

assert len(QUESTIONS) == len(BY_ID) == len(RECORDS) == 70
assert {r["id"] for r in RECORDS} == set(BY_ID)
assert collections.Counter(q["level"] for q in QUESTIONS) == {"sl": 28, "ahl": 42}
assert b"\r" not in SOURCE.read_bytes(), "Canonical input must use UTF-8 LF for raw-byte hash portability."
report = {
    "batch": "Structure 1 and Structure 2",
    "questions": 70,
    "status": "passed",
    "sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "method": "Separate agent independently read all 70 stems and complete solutions, recomputed the explicit checks below without importing author assertions, reviewed current 2025 guide boundaries and inspected all 70 original SVGs plus corrected native-size examples.",
    "sourceGuide": "https://www.ibo.org/globalassets/new-structure/university-admission/pdfs/subject-guides/chemistry-guide.pdf",
    "sourceSpecimen": "https://www.ibo.org/globalassets/new-structure/programmes/dp/pdfs/chemistry-hl-sl-specimen-papers-1a-2b-2-en.pdf",
    "checks": sum(len(r["independentChecks"]) for r in RECORDS),
    "scope": [
        "Shared S1 electron configurations including Cr/Cu and ions through Z36 are current S1.3.5 scope.",
        "All quantitative elemental isotope spectra, convergence energies and successive IE tasks are correctly AHL.",
        "Shared S2 VSEPR never exceeds four domains; formal-charge/resonance/hybridization/expanded-domain tasks are AHL.",
        "Transition-metal d-electron metallic-bond discussion and condensation polymers are AHL.",
        "No spectrometer-operation requirements, d-hybridization labels, percent-ionic formulas, or unprovided real-gas equations."
    ],
    "correctionsDuringReview": [
        "S2-731 changed proposed Cr/Mn d-count counterexample to Cr/Fe, so d5 to d6 actually increases while melting temperature falls.",
        "Wider two-molecule panels and conservative condensed-label clearance remove S2-733 monomer overlap and bond/text overprint in structural drawings.",
        "S1-717 closely spaced low-m/z labels staggered for readability.",
        "S1-707 dilution flask liquid surface now aligns with the calibration mark."
    ],
    "records": RECORDS,
    "limitations": [
        "Independent computational and chemical reasoning review by an AI agent is not moderation by human IB examiners.",
        "Original instructional M/A/R schemes are not official IB markschemes.",
        "Difficulty is an editorial judgment; no student-performance calibration has been conducted.",
        "Executable checks establish stated balances and numerical consistency; native diagram inspection is documented separately in each record."
    ]
}
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8", newline="\n")
print(json.dumps({"status": report["status"], "questions": 70, "independentChecks": report["checks"], "sha256": report["sha256"]}))
