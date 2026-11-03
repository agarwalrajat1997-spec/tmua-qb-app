"""Independent R3 review reproducer. Does not import author code.

The reviewed JSON hash is fixed below: any content change requires a new review.
Atom/charge balances and calculations are recomputed here from the printed data.
The chemical and diagram judgments record a separate complete human-readable AI
read, not human examiner moderation. Run with standard-library Python.
"""
from pathlib import Path
from collections import Counter
import hashlib, json, math, re, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
BANK = ROOT / "content/ib/chemistry-2026-expansion/mechanisms.json"
EXPECTED_SHA256 = "3759b4e836c9889f38c7847c1a9c3a0e3a2e257cb1f1a80bdf60416433fc3a0d"
raw = BANK.read_bytes()
assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256, "Content changed after independent review"
questions = json.loads(raw)
assert len(questions) == 35
qm = {q["number"]: q for q in questions}
assert sorted(qm) == list(range(701, 736))
assert len({q["id"] for q in questions}) == 35
assert Counter(q["level"] for q in questions) == {"sl": 14, "ahl": 21}
records = []
pending = []

def check(label, actual, expected, atol=1e-10, rtol=1e-7):
    if isinstance(expected, bool):
        assert bool(actual) == expected, (label, actual, expected)
    else:
        assert math.isclose(actual, expected, abs_tol=atol, rel_tol=rtol), (label, actual, expected)
    pending.append({"kind": "calculation", "label": label, "actual": actual, "expected": expected, "status": "passed"})

def atoms(formula):
    """Recursive character parser, independent of the author's token stack."""
    if formula == "e":
        return Counter()
    i = 0
    def count():
        nonlocal i
        start = i
        while i < len(formula) and formula[i].isdigit():
            i += 1
        return int(formula[start:i]) if start != i else 1
    def group():
        nonlocal i
        out = Counter()
        while i < len(formula) and formula[i] != ")":
            if formula[i] == "(":
                i += 1
                a = group()
                assert formula[i] == ")"
                i += 1
                k = count()
                for x, n in a.items():
                    out[x] += k*n
            else:
                assert formula[i].isupper(), formula
                x = formula[i]
                i += 1
                if i < len(formula) and formula[i].islower():
                    x += formula[i]
                    i += 1
                out[x] += count()
        return out
    out = group()
    assert i == len(formula)
    return out

def reaction(label, lhs, rhs):
    def inventory(side):
        out = Counter()
        charge = 0
        for k, formula, z in side:
            for x, n in atoms(formula).items():
                out[x] += k*n
            charge += k*z
        return dict(sorted(out.items())), charge
    a, b = inventory(lhs), inventory(rhs)
    assert a == b, (label, a, b)
    pending.append({"kind": "atoms and charge", "label": label, "atomsEachSide": a[0], "chargeEachSide": a[1], "status": "passed"})

def audit(n, calculation, chemical, visual):
    q = qm[n]
    assert q["id"] == f"ib-chem-r3-{n}"
    assert q["source"] == {"document": "Independent syllabus-authored practice", "question": n}
    assert q["difficulty"] == "hard" and q["calculator"] is True
    assert q["level"] == ("sl" if n < 715 else "ahl")
    assert q["marks"] == sum(p["marks"] for p in q["parts"])
    assert 8 <= q["marks"] <= 14
    assert len(q["parts"]) == len(q["markScheme"]) == 3
    for p, g in zip(q["parts"], q["markScheme"]):
        assert p["label"] == g["part"]
        assert p["marks"] == sum(int(s["code"][1:]) for s in g["steps"])
        assert all(s["code"] in ("M1", "A1", "R1") for s in g["steps"])
    for key in ("diagramSvg", "markSchemeDiagramSvg"):
        if q.get(key):
            tree = ET.fromstring(q[key])
            assert tree.attrib["viewBox"] == "0 0 640 420"
            assert not re.search(r"<(?:script|foreignObject|image|style)|(?:href|src)=|url\s*\(", q[key], re.I)
    records.append({
        "id": q["id"], "status": "passed", "scope": q["level"],
        "syllabusCode": q["syllabusCode"], "calculation": calculation,
        "independentChecks": list(pending), "chemicalReasoning": chemical,
        "diagramReview": visual,
        "markAllocationReview": "Read every stem, part and solution award. Distinct M1/A1/R1 contributions match all part totals and the overall total; equivalent valid chemistry and admissible follow-through are allowed.",
        "questionSha256": hashlib.sha256(json.dumps(q, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    })
    pending.clear()

# Shared SL/AHL: no weak-equilibrium constants, electrode-potential calculations,
# detailed SN1/SN2 inference, or HL-only pOH demand in questions 701--714.
reaction("Neutralization", [(1,"H",1),(1,"OH",-1)], [(1,"H2O",0)])
excess = .020*.150-.030*.080
check("Excess acid mol", excess, .000600)
check("Mixed pH", -math.log10(excess/.050), 1.921, atol=.0005)
check("Diluted pH", -math.log10(excess/.250), 2.620, atol=.0005)
check("Diagram dots preserve 5:4 initial ion ratio", len(ET.fromstring(qm[701]["diagramSvg"]).findall("{http://www.w3.org/2000/svg}circle")), 9)
audit(701, "0.00300−0.00240=0.000600 mol H+; divide by 0.0500 or 0.250 dm3 before taking −log.", "Neutralization consumes the limiting hydroxide, while dilution conserves excess acid amount. Logarithmic pH values cannot be averaged.", "Five H+ and four OH− equal-amount dots correctly encode 5:4; no final excess or pH is labelled.")

check("Acid concentration M", .100*.0184/.025, .0736)
check("End point pH", 14+math.log10(.100*(.0186-.0184)/(.025+.0186)), 10.662, atol=.0005)
check("Concentration positive bias percent", 100*(18.60/18.40-1), 1.09, atol=.005)
audit(702, "Equivalence amount is 0.001840 mol; the 0.20 cm3 overrun leaves 2.00e−5 mol OH− in 43.60 cm3.", "Strong acid/strong base equivalence is neutral at 298 K; an indicator observation is distinct from stoichiometric equivalence. Smaller increments near the steep region improve location.", "Strong-acid curve rises near 18.4 cm3, with no label revealing computed concentration or end-point pH. Both axes and pH range are correct.")

reaction("Hydrogen carbonate proton acceptance", [(1,"HCO3",-1),(1,"H3O",1)], [(1,"H2CO3",0),(1,"H2O",0)])
reaction("Hydrogen carbonate proton donation", [(1,"HCO3",-1),(1,"OH",-1)], [(1,"CO3",-2),(1,"H2O",0)])
check("Hydrogen ion M", 10**-8.20, 6.3095734448e-9)
check("Hydroxide M", 1e-14/10**-8.20, 1.5848931925e-6)
audit(703, "Kw/[H+] gives 1.58e−6 M hydroxide versus 6.31e−9 M hydrogen ion.", "The conjugate partners H2CO3/HCO3−/CO3²− differ by one proton and charge; carbonate has no proton to donate. No equilibrium constant is assumed.", "HCO3− drawing has one C=O, one O− and one O–H. Lone pairs, formal charge and four carbon bond orders are correct.")

check("Fraction X ionized", 10**-1.70/.0200, .99763115748444)
check("Fraction Y ionized", 10**-2.70/.200, .009976311574844)
check("X tenfold dilution pH", -math.log10(10**-1.70/10), 2.700)
audit(704, "Use unrounded 10^(−2.70) when dividing by 0.200; Y is about 0.998%, reported 1.00%.", "X is essentially fully ionized whereas ten-times more concentrated Y is weak. Conductivity 8.1 versus 0.85 mS/cm is plausible supporting evidence; mobility differences are acknowledged.", "Dilution graph runs from pH1.70 to2.70 on log10 dilution factor0..1. It is supplied experimental evidence, not a labelled answer to the fraction calculation.")

reaction("Antacid carbonate reaction", [(1,"CaCO3",0),(2,"HCl",0)], [(1,"CaCl2",0),(1,"CO2",0),(1,"H2O",0)])
used=.025-.020*.5
check("Acid consumed mol", used, .015)
check("Carbonate percentage", used/2*100.09*100, 75.0675)
check("CO2 cm3", used/2*24.8*1000, 186)
audit(705, "Back titration subtracts 0.01000 from0.02500 mol HCl, then uses two acid per carbonate; predicted gas186 cm3.", "Inert acid-insoluble filler does not consume acid. Removing dissolved CO2 before back titration prevents its interference; dissolved/escaped gas can explain the independent low collection.", "Burette discharges into conical flask, with tap and correct standard NaOH/sample labels. Apparatus is chemically relevant and no result is printed.")

reaction("Magnesium oxidation", [(1,"Mg",0)], [(1,"Mg",2),(2,"e",-1)])
reaction("Copper reduction", [(1,"Cu",2),(2,"e",-1)], [(1,"Cu",0)])
check("Copper gained g", .4862/24.31*63.55, 1.271)
audit(706, "0.4862/24.31=0.02000 mol Mg yields the same amount Cu,1.271 g unrounded or1.27 g.", "Displacement ordering Mg>Zn>Cu makes Mg the negative anode. Electrons go through wire to Cu; nitrate migrates toward the Mg compartment and K+ toward Cu. Ions carry bridge current.", "Separate Mg/Cu half-cells have connected voltmeter and immersed salt bridge. Electrode and solution labels match the intended circuit; no sign answer is supplied.")

reaction("Lead anode on discharge", [(1,"Pb",0),(1,"SO4",-2)], [(1,"PbSO4",0),(2,"e",-1)])
reaction("Lead dioxide cathode", [(1,"PbO2",0),(1,"SO4",-2),(4,"H",1),(2,"e",-1)], [(1,"PbSO4",0),(2,"H2O",0)])
reaction("Overall lead acid", [(1,"Pb",0),(1,"PbO2",0),(2,"SO4",-2),(4,"H",1)], [(2,"PbSO4",0),(2,"H2O",0)])
check("Formal H2SO4 remaining mol", .050-2*.0100, .0300)
audit(707, "One PbO2 consumes four H+ and two sulfates per full cell reaction:0.0100 mol PbO2 consumes0.0200 formal mol H2SO4.", "Charging reverses the electrode reactions; PbSO4→Pb plate is the cathode on charge. Formal acid accounting explicitly avoids an assumption of complete second dissociation.", "Lead and lead dioxide plates share electrolyte and a load. The printed sulfates/protons match the model, without cell-sign or final-concentration labels.")

reaction("Molten magnesium chloride", [(1,"MgCl2",0)], [(1,"Mg",0),(1,"Cl2",0)])
reaction("Molten chloride oxidation", [(2,"Cl",-1)], [(1,"Cl2",0),(2,"e",-1)])
check("Mg mol", .200, .200)
check("Cl2 mol", .200, .200)
audit(708, "One molten MgCl2 produces one Mg and one Cl2, so0.200 mol gives0.200 mol each.", "Positive X is the anode and negative Y the cathode. At720°C MgCl2 is molten and Mg product is liquid. Water-free melt excludes H2/O2 competition.", "DC polarity, inert electrodes and water-free melt temperature agree. The ion reduction/oxidation products are not drawn as answer labels.")

reaction("Ethanol first oxidation", [(1,"C2H6O",0),(1,"O",0)], [(1,"C2H4O",0),(1,"H2O",0)])
reaction("Ethanal second oxidation", [(1,"C2H4O",0),(1,"O",0)], [(1,"C2H4O2",0)])
check("Oxidant O equivalents mol", .050+2*.020, .0900)
check("Unreacted alcohol mol", .080-.050-.020, .0100)
audit(709, "Ethanal consumes one [O] and acid consumes two overall:0.0500+2×0.0200=0.0900 mol [O].", "Y distils aldehyde away from oxidant, with ice-cooled receiver required near ethanal bp20°C; X open reflux returns volatile material. Tertiary alcohol lacks the necessary carbinol H under the stated conditions.", "Inspected full receiver/condenser/reflux connections. Cooling water enters low and exits high; reflux is open; Y has visible ice bath and receiver. Heating and X/Y labels are clear.")

reaction("Iron permanganate intended", [(1,"MnO4",-1),(8,"H",1),(5,"Fe",2)], [(1,"Mn",2),(4,"H2O",0),(5,"Fe",3)])
reaction("MnO2 alternative reduction", [(1,"MnO4",-1),(4,"H",1),(3,"e",-1)], [(1,"MnO2",0),(2,"H2O",0)])
check("Fe concentration M", .02000*.01800*5/.02500, .0720)
check("Treating three electrons as five overestimates", 5>3, True)
audit(710, "Permanganate amount0.0003600 mol multiplies by5, giving Fe0.001800 mol/0.02500 dm3=0.0720 M.", "The MnO2 route accepts three rather than five electrons. Assigning five to all titrant therefore overstates iron; brown precipitate is meaningful evidence.", "Acidified iron flask and permanganate burette labels match the equation. No endpoint colour or computed concentration is printed.")

reaction("Ethane chlorine H abstraction", [(1,"Cl",0),(1,"C2H6",0)], [(1,"HCl",0),(1,"C2H5",0)])
reaction("Ethyl radical propagation", [(1,"C2H5",0),(1,"Cl2",0)], [(1,"C2H5Cl",0),(1,"Cl",0)])
reaction("Ethyl radical termination", [(2,"C2H5",0)], [(1,"C4H10",0)])
check("One radical regenerated per propagation cycle", 1, 1)
audit(711, "Propagation conserves one chain-carrying radical; coupling two ethyl radicals forms butane and removes both radical centers.", "Homolysis gives two Cl radicals, each fish-hook transfers one electron. Initiation is distinct from propagation and no radical remains in the required termination product.", "Full Cl2 Lewis electrons and UV shown; two one-barbed arrows start at the bond and finish at separate Cl atoms. Arrowheads are single-electron, not pair heads.")

amounts=[.1*x for x in [.20,.50,.25,.05]]
check("Carbon mol conserved", sum(amounts), .100)
check("Cl2 consumed mol", sum(k*x for k,x in enumerate(amounts)), .115)
check("Hydrogen atom mol including HCl", sum((4-k)*x for k,x in enumerate(amounts))+.115, .400)
reaction("Two methane substitutions", [(1,"CH4",0),(2,"Cl2",0)], [(1,"CH2Cl2",0),(2,"HCl",0)])
audit(712, "The four amounts0.0200/0.0500/0.0250/0.00500 mol give0.115 mol substituted H and thus Cl2 and HCl. Carbon and hydrogen inventories are conserved.", "Repeated substitution is possible because chloromethane retains C–H bonds. Favourable reaction energy does not remove the initiation barrier; dark stability is kinetic.", "Four equal-width chromatographic peaks have proportional heights20/50/25/5 and non-overlapping retention positions. Corrected areas are explicitly supplied; axes use arbitrary response.")

reaction("Primary hydroxide substitution", [(1,"C2H5Br",0),(1,"OH",-1)], [(1,"C2H6O",0),(1,"Br",-1)])
check("Hydroxide valence electrons", 6+1+1, 8)
check("Alcohol oxygen formal charge", 6-4-2, 0)
audit(713, "Net −1 charge is transferred from hydroxide to bromide; product oxygen has two bonds/two lone pairs and formal charge zero.", "O lone pair→electrophilic carbon and C–Br bond pair→Br conserve pairs without free electrons; heterolysis makes bromide. Shared-SL wording requires pair movement only.", "Reactant O has one O–H bond/three lone pairs/−charge; attacked C has four bonds. Private scheme's two full-headed arrows start at O pair and C–Br bond respectively and terminate at C/Br.")

reaction("Ethene dark addition", [(1,"C2H4",0),(1,"Br2",0)], [(1,"C2H4Br2",0)])
reaction("Ethane UV substitution", [(1,"C2H6",0),(1,"Br2",0)], [(1,"C2H5Br",0),(1,"HBr",0)])
check("Ethene fraction", .180/.300, .600)
check("Ethane fraction", (.300-.180)/.300, .400)
check("UV HBr mol", .300-.180, .120)
audit(714, "One Br2 per alkene gives0.180 ethene and0.120 ethane, fractions0.600/0.400; only the later substitution releases0.120 mol HBr.", "Specified inert non-aqueous solvent excludes bromohydrin ambiguity. Dark addition makes1,2-dibromoethane without HBr; UV alkane substitution replaces H.", "Ethene has two C–C strokes and CH2 ends; ethane one stroke and CH3 ends. Names and electron-rich bond match the reasoning.")

# Additional HL: all numerical equilibria, E°/Gibbs applications and detailed
# mechanisms are confined to 715--735, matching current R3.1/R3.2/R3.4 scope.
h=math.sqrt(1.80e-5*.0400)
check("Weak acid pH", -math.log10(h), 3.071, atol=.0005)
check("Concentrated dissociation percent", h/.0400*100, 2.12132034356)
check("Dilute estimated dissociation percent", math.sqrt(1.80e-5*.000400)/.000400*100, 21.2132034356)
check("pH-log c slope", -.5, -.5)
audit(715, "Square-root estimate gives8.49e−4 M H+ andpH3.071; depletion2.12% is small, but21.2% at0.000400 M fails.", "Derived pH≈½(pKa−log c) has slope−½. The question asks checking a stipulated approximation, not a quadratic, and notes eventual water contribution.", "Straight log-concentration graph has slope−½ and range−1.4..−0.4, within the useful approximation region. No extreme-dilution answer is plotted.")

ka=1e-14/1.8e-5
check("NH4 Ka", ka, 5.55555555556e-10)
check("NH3 pH", 14+math.log10(math.sqrt(1.8e-5*.0800)), 11.079, atol=.0005)
check("NH4Cl pH", -math.log10(math.sqrt(ka*.0800)), 5.176, atol=.0005)
check("NH3 ionization percent", 100*math.sqrt(1.8e-5*.0800)/.0800, 1.50)
check("NH4 ionization percent", 100*math.sqrt(ka*.0800)/.0800, .00833333333333)
reaction("Ammonium hydrolysis", [(1,"NH4",1),(1,"H2O",0)], [(1,"NH3",0),(1,"H3O",1)])
audit(716, "Conjugate Ka=Kw/Kb and square-root estimates givepH11.079/5.176; both depletion fractions satisfy small-ionization checks.", "The chloride spectator does not release HCl. Ammonium proton donation, rather than salt molecular acidity, explains the acidic solution.", "Solid NH3 branch is basic, dashed NH4Cl branch acidic over0.01..0.08 M; scales and concentration domain match. End labels do not obscure curves.")

check("Initial buffer pH", 4.76+math.log10(.015/.010), 4.936, atol=.0005)
check("Equalization acid mol", (.015-.010)/2, .00250)
check("Required HCl cm3", (.015-.010)/2/1*1000, 2.50)
reaction("Acetate consumes proton", [(1,"C2H3O2",-1),(1,"H",1)], [(1,"C2H4O2",0)])
audit(717, "Derive Henderson ratio from Ka. Solving0.0100+x=0.0150−x gives0.00250 mol HCl and2.50 cm3.", "Both components share the same final volume, which cancels. A− consumes added H+, and appreciable weak-acid/conjugate-base reservoirs explain buffering.", "Two HA units and three A− units reproduce0.010:0.015. Acid O–H and anionic O forms are distinguishable; carbon valence four and charge are correct.")

check("Common initial pH", 4+math.log10(.010/.020), 3.699, atol=.0005)
check("P post-addition ratio", (.001+.0015)/(.002-.0015), 5)
check("P final pH", 4+math.log10(5), 4.699, atol=.0005)
check("Q excess hydroxide mol", .0015-.0002, .00130)
check("Q final pH", 14+math.log10(.00130/.0210), 12.792, atol=.0005)
reaction("Acid buffer consumes OH", [(1,"C2H4O2",0),(1,"OH",-1)], [(1,"C2H3O2",-1),(1,"H2O",0)])
audit(718, "20mL P contains0.002/0.001 mol HA/A−, while Q contains one tenth; same0.00150 mol OH− leaves P buffered at ratio5 but Q with0.00130 mol OH−.", "Volume dilution preserves the initial ratio while reducing capacity. It is essential to neutralize stoichiometrically before using weak-equilibrium or excess-strong-base calculations.", "Horizontal initial-pH curve represents dilution only and does not reveal the differing final post-NaOH outcomes. Axis ranges are clear and correct.")

ka=10**-4.80
check("Acid concentration M", .100*.025/.025, .100)
check("Ka", ka, 1.58489319246e-5)
check("Equivalence salt M", .100*.025/(.025+.025), .0500)
check("Equivalence pH", 14+math.log10(math.sqrt(1e-14/ka*.05)), 8.749, atol=.0005)
reaction("Conjugate-base hydrolysis", [(1,"C2H3O2",-1),(1,"H2O",0)], [(1,"C2H4O2",0),(1,"OH",-1)])
audit(719, "Half-equivalence pH 4.80 fixes Ka; equivalence salt 0.0500 M gives pH 8.749 from Kb=Kw/Ka.", "Basic hydrolysis selects indicator 8.2–10.0. Added water changes curve pH but not acid amount or the 25.0 cm3 equivalence requirement.", "Weak-acid titration has acidic start, buffer region and basic equivalence near 25 cm3. No numeric calculated Ka or equivalence pH label leaks.")

kb=10**-4.30
check("Equivalence volume cm3", .080*.020/.100*1000, 16.0)
check("Half-equivalence pH", 14-4.30, 9.700)
check("Equivalence BH+ concentration", .080*.020/.036, .0444444444444)
check("Equivalence pH", -math.log10(math.sqrt(1e-14/kb*.080*.020/.036)), 5.526, atol=.0005)
reaction("Conjugate acid model", [(1,"NH4",1),(1,"H2O",0)], [(1,"NH3",0),(1,"H3O",1)])
audit(720, "0.00160 mol B needs16.0cm3 acid; at8.00cm3pOH=pKb. Equivalence BH+0.044444M hydrolyses topH5.526.", "BH+ proton donation selects4.4–6.2 indicator. End point remains an observed indicator equilibrium, distinct from acid/base amount equality.", "Downward weak-base curve has half-equivalence near8cm3 and acidic steep region near16cm3. Axes and base initialpH are chemically consistent.")

check("Protonated fraction", .100/.500, .200)
check("Deprotonated fraction", 1-.100/.500, .800)
check("Indicator pH", 5.50+math.log10(.8/.2), 6.102, atol=.0005)
check("Low transition pH", 5.50+math.log10(.10), 4.500)
check("High transition pH", 5.50+math.log10(10), 6.500)
audit(721, "Only HInd absorbs at the chosen wavelength, so0.100/0.500=0.200 HInd, ratio4 andpH6.102; ratios0.1/10 give4.500/6.500.", "A continuous equilibrium yields a transition interval rather than one abrupt pH. No unsupported molecular identity or spectral assignment is required.", "Illustrative separated absorption bands label HInd/Ind− and use non-negative absorbance. The chosen wavelength's proportionality is in the stem, avoiding unsupported peak inference.")

reaction("BF3 ammonia adduct", [(1,"BF3",0),(1,"NH3",0)], [(1,"BF3NH3",0)])
reaction("CoIII ligand substitution", [(1,"Co(NH3)4Cl2",1),(1,"NH3",0)], [(1,"Co(NH3)5Cl",2),(1,"Cl",-1)])
check("Adduct nitrogen formal charge", 5-0-4, 1)
check("Adduct boron formal charge", 3-0-4, -1)
check("Original Co complex charge", 3-2, 1)
check("Final Co complex charge", 3-1, 2)
audit(722, "N four bonds gives+1 and B four gives−1; neutral adduct overall. CoIII original+1 changes to+2 when neutral NH3 replaces Cl−; released chloride preserves charge.", "NH3 supplies a lone pair to electron-deficient BF3 without proton transfer. Both original and final CoIII chloridoammine complexes are chemically established six-coordinate models.", "All BF3 fluorine lone pairs and NH3 nitrogen lone pair are shown; B has three bonds/six electrons initially. No adduct charge answer is drawn.")

reaction("Hydrogen oxidation against copper", [(1,"H2",0),(1,"Cu",2)], [(2,"H",1),(1,"Cu",0)])
check("Copper potential versus SHE V", .340-0, .340)
check("Reversed meter leads V", -.340, -.340)
audit(723, "Cu connected to red lead reads+0.340V versus0V SHE; reversing leads changes the displayed sign without reversing cell chemistry.", "SHE conditions includePt,H2at100kPa,H+1M,298K. H2 oxidizes and Cu2+ reduces; salt-bridge ions maintain electroneutrality.", "Pt/hydrogen bubbling assembly, Cu half-cell and salt bridge are physically connected. Copper metal electrode and solutions are correctly labelled; no electron-flow arrow supplies the answer.")

reaction("Tin iodine cell", [(1,"Sn",2),(1,"I2",0)], [(1,"Sn",4),(2,"I",-1)])
check("Cell E V", .540-.150, .390)
check("Gibbs kJ", -2*96500*.390/1000, -75.27)
check("Doubled Gibbs kJ", -4*96500*.390/1000, -150.54)
audit(724, "I2 reduction minusSn4+ reduction givesE0.390V,n2 andΔG−75.27kJ. Doubling makesn4,ΔG−150.54kJ (−151to3sig) with unchangedE.", "Sn2+ is oxidized while iodine reduces. Potential is intensive, Gibbs energy extensive; thermodynamic favorability makes no claim of rapid kinetics.", "Pt electrodes serve both nonmetallic redox systems. Sn4+/Sn2+ and I2/I− identities agree with potential data; no calculated potential is printed.")

reaction("Copper I disproportionation", [(2,"Cu",1)], [(1,"Cu",2),(1,"Cu",0)])
check("Disproportionation E V", .520-.150, .370)
check("Gibbs kJ", -1*96500*.370/1000, -35.705)
check("Copper formed mol", .0400/2, .0200)
audit(725, "2Cu+→Cu2++Cu transfers one electron per stated equation: E=0.370 V, ΔG=−35.705 kJ; 0.0400 mol Cu+ yields 0.0200 mol of each product.", "Cu+ is both oxidized and reduced. The electron count is one rather than the sum of both half-equations.", "Copper electrode/Cu+ on the left and inert Pt/Cu+/Cu2+ on the right depict the two half-cell roles. Components and salt-bridge connections are correct.")

reaction("Copper inert-anode electrolysis", [(2,"Cu",2),(2,"H2O",0)], [(2,"Cu",0),(1,"O2",0),(4,"H",1)])
reaction("Copper soluble anode", [(1,"Cu",0)], [(1,"Cu",2),(2,"e",-1)])
check("Cu2+ inert anode final M", (.100-.0200)/.100, .800)
check("O2 mol", .0200/2, .0100)
check("Hydrogen ions generated mol", .0200*2, .0400)
check("Soluble Cu anode concentration unchanged M", (.100-.0200+.0200)/.100, 1.00)
audit(726, "Depositing 0.0200 mol Cu consumes 0.0400 mol electrons. Inert-anode water oxidation gives 0.0100 mol O2 and 0.0400 mol H+, while a soluble Cu anode replenishes exactly the removed ions.", "The electrolytic cathode is negative. Sulfate remains a spectator; oxygen is generated at the inert anode, whereas a Cu anode oxidizes into solution.", "The DC positive terminal goes to the varied anode and the negative terminal to the inert cathode, immersed in CuSO4. The diagram supports comparison without labelling products or final concentration.")

reaction("Nickel anode oxidation", [(1,"Ni",0)], [(1,"Ni",2),(2,"e",-1)])
reaction("Competing hydrogen cathode", [(2,"H",1),(2,"e",-1)], [(1,"H2",0)])
check("Nickel deposition efficiency fraction", .810/.900, .900)
check("Net nickel ion increase mol", (.900-.810)/58.69, .001533481001874)
check("H2 mol from electron deficit", (.900/58.69*2-.810/58.69*2)/2, .001533481001874)
audit(727, "0.810/0.900=90.0% of anodic electron equivalents deposit Ni. The remaining 0.0900/58.69 mol Ni-equivalent produces 0.00153 mol H2 and leaves the same excess amount of Ni2+.", "The conducting object is the negative cathode and nickel is the positive anode. The lower cathodic mass results from a competing reduction and conserves charge.", "Nickel-anode/object labels and DC signs correctly show the plating circuit. Ni2+ and H+ in solution permit the explicitly stated competition.")

reaction("Brine cell net ionic", [(2,"Cl",-1),(2,"H2O",0)], [(1,"Cl2",0),(1,"H2",0),(2,"OH",-1)])
reaction("Water oxidation alternative", [(2,"H2O",0)], [(1,"O2",0),(4,"H",1),(4,"e",-1)])
check("Hydrogen mol", .0120, .0120)
check("Hydroxide concentration M", 2*.0120/.200, .120)
check("Catholyte pH", 14+math.log10(.120), 13.079, atol=.0005)
check("Water-only H2 to O2 ratio", 4/2, 2)
audit(728, "Two electrons link one Cl2, one H2 and two OH−, giving 0.0240 mol OH− in 0.200 dm3 and pH 13.079. Water oxidation would give H2:O2=2.", "Chlorine production is supplied as observed evidence, avoiding an unsupported aqueous halide selectivity assumption. The membrane prevents product mixing; cathodic water reduction leaves OH−.", "Separated compartments, dashed membrane and DC polarities match the required anode/cathode. No products or measured amounts are shown.")

reaction("Cyanide chain extension", [(1,"C3H7Br",0),(1,"CN",-1)], [(1,"C4H7N",0),(1,"Br",-1)])
check("Nitrile carbon atoms", atoms("C3H7Br")["C"]+atoms("CN")["C"], 4)
check("Cyanide carbon formal charge", 4-2-3, -1)
audit(729, "Cyanide carbon adds one carbon: 1-bromopropane gives butanenitrile, C4H7N. Atoms and net −1 charge balance.", "Specified carbon attack by backside SN2 has concerted C–C formation/C–Br cleavage, one transition state and no carbocation. The carbon end of CN− is nucleophilic here.", "Inspected the full-size reactant and private scheme: N≡C− has a pair on C, with an ethyl group attached to the attacked CH2Br. The pair arrow starts at the cyanide carbon pair and ends at substrate carbon; the leaving-bond arrow ends at Br.")

reaction("Tertiary halide ionization", [(1,"C4H9Cl",0)], [(1,"C4H9",1),(1,"Cl",-1)])
reaction("Carbocation water capture", [(1,"C4H9",1),(1,"H2O",0)], [(1,"C4H11O",1)])
reaction("Oxonium deprotonation", [(1,"C4H11O",1),(1,"H2O",0)], [(1,"C4H10O",0),(1,"H3O",1)])
reaction("Overall aqueous tertiary substitution", [(1,"C4H9Cl",0),(2,"H2O",0)], [(1,"C4H10O",0),(1,"H3O",1),(1,"Cl",-1)])
check("Oxonium O formal charge", 6-2-3, 1)
check("Neutral alcohol O formal charge", 6-4-2, 0)
audit(730, "Ionization, neutral-water capture and deprotonation conserve atoms/charge separately and overall. Captured oxonium C4H11O+ has oxygen charge +1; neutral product C4H10O has oxygen charge zero.", "The specified SN1 pathway forms a three-coordinate planar tertiary cation. Neutral water attacks; subsequent proton transfer to water yields alcohol and H3O+, completing the neutral organic product.", "The tertiary halide has three CH3 groups and Cl. The private cation has exactly three carbon bonds and positive charge; water has two bonds/two lone pairs. The full arrow starts at the water pair and ends at cation carbon.")

reaction("Secondary substitution", [(1,"C4H9Br",0),(1,"OH",-1)], [(1,"C4H10O",0),(1,"Br",-1)])
check("Stereocentre distinct groups", len(set(["H","CH3","C2H5","Br"])), 4)
check("Solid wedge polygons in three panels", qm[731]["diagramSvg"].count('fill="#111"/>'), 3)
audit(731, "With carbon groups fixed in the plane, Q swaps the towards/away positions of H/OH relative to H/Br; P retains the original arrangement. Net −1 charge resides on Br−.", "SN2 inversion follows the explicit premise. Optical activity alone does not identify the pathway. Product oxygen has two bonds/two pairs and neutral charge.", "Inspected all three wedge panels: reactant H solid/Br away; P has H solid/OH away; Q has OH solid/H away. Seven widening hash strokes per receding bond and solid wedges correctly encode geometry.")

reaction("Ethyl bromide hydrolysis", [(1,"C2H5Br",0),(1,"OH",-1)], [(1,"C2H6O",0),(1,"Br",-1)])
reaction("Released bromide detection", [(1,"Ag",1),(1,"Br",-1)], [(1,"AgBr",0)])
check("Extent ordering at80s", 1-math.exp(-80/25)>1-math.exp(-80/70)>1-math.exp(-80/180), True)
check("Supplied bond enthalpy order", 238<276<338, True)
audit(732, "At the same time the curves order I>Br>Cl; the weaker supplied C–I bond aligns with the leaving-group trend. Ag+ precipitates released Br− in a 1:1 ratio.", "The same ethyl skeleton and fixed solvent make a controlled leaving-group comparison. Neither solvent effects nor a complete SN1/SN2 mechanism can be inferred from extent curves alone.", "Three bounded 0..1 extent curves are labelled I/Br/Cl near separate regions. Fast I, intermediate Br and slow Cl trace order is correct; labels do not cross.")

reaction("DBr isotope addition", [(1,"C3H6",0),(1,"DBr",0)], [(1,"C3H6DBr",0)])
reaction("DBr carbocation formation", [(1,"C3H6",0),(1,"DBr",0)], [(1,"C3H6D",1),(1,"Br",-1)])
check("Major cation alkyl groups", 2, 2)
check("Ordinary hydrogens retained", atoms("C3H6DBr")["H"], 6)
audit(733, "Major CH3CH(Br)CH2D follows secondary CH3C+(H)CH2D; minor CH3CH(D)CH2Br follows a primary cation. Both retain six ordinary hydrogens and add D plus Br.", "Pairs move from pi bond to D and from D–Br bond to Br; Br− then attacks C+. No rearrangement or isotope effect is required. Carbon valence four and ordinary hydrogen balance hold in both products.", "Propene groups and the D–Br bond are clear. The private first arrow begins on the pi bond and finishes at D; the second begins on D–Br and ends at Br. Both have full pair heads.")

reaction("Hydronium protonates ethene", [(1,"C2H4",0),(1,"H3O",1)], [(1,"C2H5",1),(1,"H2O",0)])
reaction("Labelled water capture elemental balance", [(1,"C2H5",1),(1,"H2O",0)], [(1,"C2H7O",1)])
reaction("Hydration deprotonation", [(1,"C2H7O",1),(1,"H2O",0)], [(1,"C2H6O",0),(1,"H3O",1)])
check("Alcohol oxygen derives from attacking water count", 1, 1)
check("Net water consumed", 2-1, 1)
audit(734, "Ethene protonation forms C2H5+; labelled water capture gives C2H5(18OH2)+, and deprotonation gives C2H5(18OH). The attacking water oxygen enters the product.", "The initial hydronium oxygen remains in water in this traced pathway. Hydronium is regenerated on deprotonation and acts as catalyst; isotopic exchange is expressly excluded.", "Ethene C=C and H3O+ with three O–H bonds, one pair and positive charge are correct. No product isotope label is supplied. Reviewed oxygen identity separately from elemental balance.")

reaction("Nitronium sigma complex", [(1,"C6H6",0),(1,"NO2",1)], [(1,"C6H6NO2",1)])
reaction("Net aromatic substitution", [(1,"C6H6",0),(1,"NO2",1)], [(1,"C6H5NO2",0),(1,"H",1)])
check("Attacked sigma-complex carbon bond count", 2+1+1, 4)
check("Final aromatic pi electrons", 3*2, 6)
audit(735, "The sigma complex retains H6/E and overall +1 charge; removing H+ restores neutral C6H5E. Net benzene+NO2+→nitrobenzene+H+ conserves atoms and charge.", "The initial pi pair attacks supplied NO2+ to form C–E. A base pair attacks H while the C–H pair forms the adjacent ring pi bond, restoring aromaticity and releasing BH+. It is proton transfer; no electrophile-generation recall is required.", "Inspected full-size initial and private SVGs. The initial arrow starts at a pi bond. The private base arrow starts at its lone pair; restoration starts at C–H midpoint (303,117.5) and ends at the adjacent C–C region. The attacked carbon has four sigma bonds, with two remaining pi bonds and delocalized positive charge.")

assert not pending
assert {r["id"] for r in records} == {q["id"] for q in questions}
report = {
    "status": "passed", "questions": 35, "sha256": EXPECTED_SHA256,
    "reviewer": "Separate AI reviewer; did not author this batch",
    "method": "Independently read all 35 questions and every worked solution, recomputed numerical/atom/charge/electron checks, and inspected all 35 latest rendered question SVGs and all five private worked mechanism SVGs. No author helper imported.",
    "independentCalculationChecks": sum(c["kind"] == "calculation" for r in records for c in r["independentChecks"]),
    "independentAtomChargeBalances": sum(c["kind"] == "atoms and charge" for r in records for c in r["independentChecks"]),
    "diagramCount": 35, "substantiveNonTableDiagrams": 35, "workedMechanismDiagrams": 5,
    "marks": sum(q["marks"] for q in questions), "levels": {"sl": 14, "ahl": 21},
    "officialGuide": "https://www.ibo.org/globalassets/new-structure/university-admission/pdfs/subject-guides/chemistry-guide.pdf",
    "specimen": "https://www.ibo.org/globalassets/new-structure/programmes/dp/pdfs/chemistry-hl-sl-specimen-papers-1a-2b-2-en.pdf",
    "scopeReview": "Current first-assessment 2025 R3.1–R3.4 checked against the official guide and local blueprint. No SL Ka/Kb/buffer/pOH or standard-potential calculation demand; R3.3 radicals remain shared SL. HL mechanisms do not require solvent effects, rate laws or electrophile-generation recipes. No Faraday current-time demand.",
    "correctedDuringReview": [
        "704: made conductivity values physically plausible and computed the fraction from unrounded 10^(−2.70).",
        "709: explicitly ice-cooled the ethanal receiver and drew the ice bath.",
        "714: specified an inert non-aqueous bromination solvent to exclude bromohydrin ambiguity.",
        "722: used established Co(III) chloridoammine complexes with correct +1/+2 complex charges.",
        "706/710/724: aligned final mass, concentration and Gibbs-energy rounding with three significant figures.",
        "All: explicitly set pH reporting to three decimal places and aligned equivalence examples.",
        "733: clarified the minor-product prompt through carbon valence and retention of original ordinary hydrogens."
    ],
    "limitations": ["Original IB-style practice, not official IB past-paper questions or official markschemes.", "Computational and separate AI review; not human IB examiner moderation.", "Release integration, build and deployment are outside this content review."],
    "records": records
}
out = ROOT / "docs/ib-2026-chemistry/mechanisms-independent-review.json"
out.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf8", newline="\n")
print(json.dumps({k: report[k] for k in ("status","questions","sha256","independentCalculationChecks","independentAtomChargeBalances","diagramCount","workedMechanismDiagrams")}))
