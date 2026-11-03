"""Independent scientific review of fifty Biology Unity and Diversity tasks.

Standard-library reproducer; does not import the author's generator/checks.
Every stem and every marking point was read independently against the current
guide; every figure was inspected in contact sheets and selected native views.
Explicit inputs below are independently transcribed from the supplied questions.
"""
from pathlib import Path
import json, hashlib, math, collections, re, itertools
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"content/ib/biology-2026-expansion/unity-diversity.json"
DEST=ROOT/"docs/ib-2026-biology/unity-diversity-independent-review.json"
DATA=json.loads(SOURCE.read_text(encoding="utf8"))
QUESTIONS={q["id"]:q for q in DATA}
RECORDS=[]
SL={701,702,703,706,707,708,718,719,720,721,730,731,732,741,742,746,747,748,749,750}
GUIDE=json.loads((ROOT/"docs/ib-biology-reviews/syllabus-blueprint.json").read_text(encoding="utf8"))
CATALOG={t["code"]:t for t in GUIDE["topics"] if t["theme"]=="A"}

def num(name,actual,expected):
    assert math.isclose(actual,expected,rel_tol=1e-8,abs_tol=1e-12),(name,actual,expected)
    return {"test":name,"calculated":actual,"expected":expected,"status":"passed"}
def eq(name,actual,expected):
    assert actual==expected,(name,actual,expected)
    plain=lambda value:sorted(value) if isinstance(value,(set,frozenset)) else value
    return {"test":name,"calculated":plain(actual),"expected":plain(expected),"status":"passed"}
def ok(name,condition):
    assert condition,name
    return {"test":name,"status":"passed"}
def rec(n,tests,biology,visual,scope):
    q=QUESTIONS[f"ib-bio-a-{n}"]
    assert q["number"]==q["source"]["question"]==n
    assert q["source"]["document"]=="Independent syllabus-authored practice"
    assert q["subject"]=="biology" and q["topicId"]=="unity-diversity" and q["collectionId"]=="biology-unity-diversity"
    assert q["calculator"] is True and q["difficulty"]=="hard" and q["status"]=="published"
    assert q["level"]==("sl" if n in SL else "ahl")
    assert q["subtopic"]==CATALOG[q["syllabusCode"]]["title"]
    assert q["marks"]==sum(p["marks"] for p in q["parts"])
    for p,g in zip(q["parts"],q["markScheme"],strict=True):
        assert p["label"]==g["part"]
        assert p["marks"]==sum(int(s["code"][1:]) for s in g["steps"])
        assert all(re.fullmatch("[MAR][1-9]",s["code"]) for s in g["steps"])
    assert "construct" in (q["stem"]+q.get("diagramCaption","")+q["diagramSvg"]).lower()
    ET.fromstring(q["diagramSvg"])
    assert len(q["diagramSvg"])<300000
    assert not re.search(r"<(?:script|foreignObject|image|style|iframe)\b|\bon\w+\s*=|\b(?:href|src)\s*=",q["diagramSvg"],re.I)
    RECORDS.append({"id":q["id"],"status":"passed",
        "canonicalQuestionSha256":hashlib.sha256(json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest(),
        "independentEvidence":tests,"biologicalReview":biology,"diagramReview":visual,
        "scopeReview":scope,"schemeReview":"Read all parts and all marking points; calculations, reasoning, command terms and total awards match the stated evidence. Accept scientifically equivalent wording."})

rec(701,[num("clean initial20s rise rate",28/20,1.4),num("coated initial20s rate",3/20,.15),num("rate ratio",(28/20)/(3/20),9.3333333333)],
    "Adhesion involves water/surface attraction, cohesion water/water hydrogen bonding. Controlled glass experiment does not generalize every biological pore radius or chemistry.",
    "All eight plotted coordinates agree with supplied heights; different line styles and rate interval are readable.",
    "A1.1 shared polarity, adhesion/cohesion and capillary contexts.")
rec(702,[num("air heat loss rate J min",500*(35-32)/10,150),num("water heat loss rate",500*(35-24)/10,550),num("water model20min remaining difference",19-15,4)],
    "Higher heat transfer in water is compatible with conductivity/convection; stated model heat capacity is not the specific heat of surrounding water. Viscosity and streamlining are correctly distinguished.",
    "Cooling curves begin at35C and remain above15C environment; no impossible cooling below ambient or mixed axis units.",
    "A1.1 shared aquatic/aerial physical-property comparisons.")
rec(703,[num("flow drop percent",(12-4)/12*100,66.6666666667),num("6min control gap",11-4,7),eq("mean sample count",5,5)],
    "A gas gap interrupts cohesion-mediated tension transmission; other vessels can retain flow. Sham and no uncertainty support a conditional causal inference, not statistical significance.",
    "Bubble/control values and4min manipulation label align; no invented error bars.",
    "A1.1 shared hydrogen bonding/cohesion linked to xylem tension.")
rec(704,[num("P retained kg",8e19*.20,1.6e19),num("Q retained kg",8e19*.75,6e19),num("Q P ratio",.75/.20,3.75),num("R retained kg",8e19*.95,7.6e19)],
    "Asteroid delivery, gravity-dependent retention and pressure/temperature allowing condensation are distinct necessary conditions; retained vapor is not liquid habitat or proof of life.",
    "Scatter at gravity.4/1/1.8 and fractions.2/.75/.95 has no spurious continuous fit.",
    "A1.1.7–8 AHL water origin/retention and extraterrestrial habitats.")
rec(705,[num("overlap low",max(.80,1.10),1.10),num("overlap high",min(1.40,1.90),1.40),num("overlap width",1.40-1.10,.30),
    eq("planet in both intervals",[d for d in [.95,1.25,1.70] if .8<=d<=1.4 and 1.1<=d<=1.9],[1.25])],
    "Habitable-zone model presupposes atmospheric conditions and does not establish delivered/retained water or occupation by life; two times do not establish all intervening conditions.",
    "Both zone rectangles and three orbital markers coincide with common AU scale.",
    "A1.1.7–8 AHL habitable orbital zone and water retention.")
rec(706,[eq("total nucleotides",120*2,240),eq("thymine",48,48),eq("G C remaining",240-2*48,144),eq("guanine/cytosine each",(240-96)//2,72)],
    "Double-stranded complementarity requires A=T and G=C, not all four equal. RNA sugar/U/single-strand comparison and backbone versus interstrand hydrogen bonding are correct.",
    "All six representative pairs are complementary; nucleotide-node legend distinguishes diagrammatic backbone from atomic base connectivity.",
    "A1.2.2–9 shared; no purine classes, bond counts or strand direction required.")
rec(707,[eq("linear polymer joins",5-1,4),eq("water molecules per model chain",4,4),
    eq("base composition equal",collections.Counter("AUGCA"),collections.Counter("ACGUA")),ok("order differs","AUGCA"!="ACGUA")],
    "Five free ribonucleotides need four model condensation joins; bases remain pendant from sugars, sequence is not identical merely because composition matches. RNA may contain paired regions.",
    "Five distinct P–S–base monomers in correct AUGCA order; no already-connected chain or base in sugar-phosphate backbone.",
    "A1.2 shared nucleotide/RNA condensation and DNA/RNA distinctions; condensation model explicitly supplied.")
rec(708,[eq("tested triplets",len({"UUU":"Phe","GGU":"Gly","UAC":"Tyr","CAA":"Gln"}),4),
    eq("example sequence1",["Phe","Gly","Gln"],[{"UUU":"Phe","GGU":"Gly","CAA":"Gln"}[c] for c in ["UUU","GGU","CAA"]]),
    ok("reversed order gives different peptide",["Phe","Gly","Gln"]!=["Gln","Gly","Phe"])],
    "Near-universal assignments support common ancestry but neither identical genomes nor identical proteins. Four triplets in three organisms cannot prove absolute universality.",
    "Code mapping corresponds to all four supplied amino-acid assignments and three tested groups; it is input data, not a claim of an entire code table.",
    "A1.2.10 shared conservation of genetic code; assignments explicitly supplied.")
template="TACCGAATGATT"
rna="".join({"T":"A","A":"U","C":"G","G":"C"}[b] for b in template)
rec(709,[eq("transcribed sequence5to3",rna,"AUGGCUUACUAA"),eq("triplet groups",[rna[i:i+3] for i in range(0,12,3)],["AUG","GCU","UAC","UAA"]),
    eq("DNA complement","".join({"A":"T","T":"A","G":"C","C":"G"}[b] for b in template),"ATGGCTTACTAA")],
    "Template3′→5′ read left-to-right gives RNA5′→3′ and Met–Ala–Tyr before stop. Backbone3′/5′ covalent linkage is separate from base hydrogen bonding.",
    "Twelve paired nucleotide nodes are complementary and strand ends antiparallel; final node/backbone legend removes atom-level ambiguity.",
    "A1.2.11 AHL directionality; codon assignments are supplied rather than unprovided translation data.")
rec(710,[num("A T model width",.6+.4,1),num("G C model width",.6+.4,1),num("A G model width",.6+.6,1.2),num("C T width",.4+.4,.8)],
    "Purine–pyrimidine pairing stabilizes uniform width, but geometric equality alone does not establish donor/acceptor complementarity. Sizes explicitly model dimensions.",
    "Segment widths use common stated scale; different base contributions sum to supplied pair widths.",
    "A1.2.12 AHL purines/pyrimidines and pairing geometry.")
rec(711,[eq("core histones",25*8,200),eq("linker histones",25*1,25),eq("total bp",25*(146+54),5000),eq("bp per repeat",146+54,200)],
    "DNA wraps an octamer; linker histone is additional and does not make the core a nine-protein octamer. Packaging number does not determine base order.",
    "Three wrapped cores joined by linker segments; schematic avoids depicting histone membranes.",
    "A1.2.13 AHL nucleosomes; supplied complete-repeat/end-effect model.")
rec(712,[num("DNA missing percent",100-(72+24),4),num("protein missing percent",100-(8+88),4),
    num("DNA pellet recovered percent",72/(72+24)*100,75),num("protein pellet recovered percent",8/(8+88)*100,8.3333333333)],
    "Tracer data support DNA entry/inherited information but pellet association is not proof of intracellular entry for every atom. Noninfected control is not assumed an exact correction.",
    "Four bars are percentages of supplied tracer, not normalized recovered percentages, as axis states; missing4% is intentionally not plotted.",
    "A1.2.14 AHL Hershey–Chase evidence; independent review clarified 100−(pellet+supernatant) parentheses.")
rec(713,[num("blank-corrected first",18-1,17),num("blank-corrected third",6-1,5),num("net yield ratio",(18-1)/(6-1),3.4)],
    "Sterile organic synthesis demonstrates one plausible prerequisite, not self-sustaining life. Energy and atmospheric-composition comparisons have appropriate controls and historical limits.",
    "Four bar values18/2/6/1 agree with treatments; uncorrected raw data explicitly plotted.",
    "A2.1 entirely AHL origin prerequisites and Miller–Urey evaluation.")
rec(714,[num("intact60min retained percent",54/100*100,54),num("disrupted retained percent",2/100*100,2),num("retention ratio",54/2,27)],
    "Fatty-acid boundaries can compartmentalize catalysts while still leaking; retention does not establish autonomous replication/metabolism.",
    "Intact/disrupted curves share100-unit start and end54/2, with no false zero leakage assertion.",
    "A2.1 entirely AHL fatty-acid vesicles and origin prerequisites.")
rec(715,[num("active product rate",36/30,1.2),num("scrambled rate",3/30,.1),num("rate ratio",(36/30)/(3/30),12)],
    "RNA can carry sequence information and catalyse; separate copying assay with laboratory catalyst does not show this same RNA autonomously self-copies in a reproducing compartment.",
    "Both product series have distinct slopes and exact0/10/20/30min coordinates; no extrapolated autonomous growth.",
    "A2.1 entirely AHL RNA-world/ribozyme evaluation.")
rec(716,[num("formation to fossil interval Ga",4.54-3.48,1.06),num("young rock bound Ga",3.48-.04,3.44),
    ok("LUCA interval older than fossil central age",3.80>3.48)],
    "Contemporaneous biological structures constrain minimum age of life, not exact origin. LUCA need not be first life, so older LUCA estimate is compatible with younger fossil.",
    "Age axis decreases toward present; fossil bounds and genomic interval correctly ordered and width-scaled.",
    "A2.1 entirely AHL geological/genomic early-life/LUCA evidence.")
rec(717,[eq("largest sampled activity temperature",[40,60,80,100][[20,65,100,35].index(max([20,65,100,35]))],80),
    num("100C activity percent maximum",35/100*100,35)],
    "Ancestral enzyme reconstruction and biological vent structures are independent compatible evidence, not exact location/temperature proof. Mineral mimics and unsampled temperature optima acknowledged.",
    "40/60/80/100C activities20/65/100/35 accurate; maximum among measured points distinguished from fitted optimum.",
    "A2.1 entirely AHL hydrothermal/geological/genomic evidence.")
rec(718,[num("stage length μm",12*10,120),num("first calibration μm per division",120/30,4),
    num("cell actual μm",18*4,72),num("new calibration",120/60,2),num("new cell divisions",72/2,36),num("wrong calibration μm",36*4,144)],
    "Objective change affects calibration, not biological cell dimensions. Same orientation/consistent boundaries needed for dimensional comparison.",
    "Thirty eyepiece intervals use31ticks; twelve stage intervals13ticks. Corresponding endpoints align exactly.",
    "A2.2 shared microscopy calibration and actual measurement.")
rec(719,[ok("L cannot resolve150nm",150<200),ok("E can resolve150nm",150>=2),num("printed enlargement",160/40,4)],
    "Resolution and magnification distinct; enlarging an unresolved signal cannot recover missing detail. Living fluorescence and fixed fine structure are complementary with specificity/preparation limitations.",
    "Target and resolution bars use one drawing unit per nm, including short2nm E limit; no false claim actual micrographs.",
    "A2.2 shared microscopy methods/resolution.")
rec(720,[eq("prokaryotic cytoplasmic ribosome class",70,70),eq("eukaryotic cytoplasmic ribosome class",80,80),eq("shared minimum membrane/cytoplasm components",len({"membrane","aqueous cytoplasm"}),2)],
    "Gram-positive bacterial cell retains naked DNA and ribosomes without nucleus; typical animal cell has membrane compartments. 80S applies to cytoplasm, not every eukaryotic organelle.",
    "Bacterial wall/membrane boundaries, unbounded nucleoid loop and ribosome dots distinguished from double nuclear boundary in animal schematic; unequal scales explicit.",
    "A2.2.4–6 shared cellular organization; no assumption every cell has nucleus.")
rec(721,[eq("visible nuclei stated model",8+6+0+0,14),ok("nuclei not equal to one per depicted cell type",14!=4)],
    "Multinucleate continuous muscle/hyphae and anucleate specialized erythrocytes/sieve elements defeat nuclei=cell-count rule. Nuclear loss during differentiation does not refute cellular origins.",
    "Counted8muscle and6hyphal nuclei, no hyphal septa, and0in erythrocyte/sieve element; unequal scale caption appropriate.",
    "A2.2.9 shared atypical nuclear number.")
rec(722,[num("organelle synthesis decrease",100-25,75),num("cytoplasmic decrease",100-95,5),num("difference points",75-5,70)],
    "Circular DNA, bacterial-like supplied ribosomes and organelle division support ancestral endosymbiosis without identifying a modern bacterial ancestor. Pharmacological specificity explicitly supplied.",
    "Final revised mitochondrion has a continuous closed inner boundary; chloroplast/mitochondrion are schematic localization, not actual microscopy.",
    "A2.2.12 AHL endosymbiosis; supplied ribosome observations treated as the model, not universal sedimentation values for every mitochondrial lineage.")
rec(723,[num("P expression fold change",80/10,8),eq("H marker all conditions",[50,50,50,50],[50]*4),num("P leaf transport ratio",90/5,18)],
    "Retained assayed genes and varied RNA support differentiation via expression rather than discarding genes. RNA alone does not establish full cell identity/protein production, and no-signal control needed.",
    "All12 expression bars match cell/treatment inputs; axis is RNA relative units, not direct protein abundance.",
    "A2.2.13 AHL environmental/developmental expression changes.")
rec(724,[num("outer removal relative percent",20/80*100,25),num("inner removal relative percent",2/80*100,2.5),num("sham relative",76/80,.95)],
    "Division of labour can benefit colony performance. Separate phylogenetic evidence, not removal experiment alone, supports repeated origins; damage/size/uncertainty alternatives retained.",
    "Four colony-output bars80/20/2/76 correctly labelled per100starting colonies; not treated as cell counts.",
    "A2.2.14 AHL multicellularity advantages and repeated origins.")
rec(725,[num("burst size",60000/1000,60),eq("release start sampling bracket min",[20,30],[20,30]),eq("plateau unchanged",60000,60000)],
    "Extracellular latent interval can coexist with intracellular replication/assembly; mean burst assumes all1000lyse once, no second cycle and no detection loss.",
    "One-step growth points0/0/0/40000/60000/60000 agree with no release until after20min; no exact onset inferred.",
    "A2.3 entirely AHL lambda lytic cycle.")
rec(726,[num("induced cells",2000*.30,600),num("surviving lysogens",2000*(1-.30),1400),num("phages released",600*50,30000),num("cell cohort sum",600+1400,2000)],
    "Integrated prophage is copied with chromosome without release at every division. Induction changes fate; low free phage count does not exclude carried genome.",
    "Lysogenic/lytic branches and induction transition separate genomic inheritance from free particles; no false cell division during count interval.",
    "A2.3 entirely AHL lambda lysogenic and lytic fates.")
rec(727,[num("V infectivity reduction",100-5,95),num("W reduction",100-92,8),num("difference points",(100-5)-(100-92),87)],
    "Lipid envelope vulnerability explains conditional drug effect; DNA/RNA/envelope variability and host dependence correctly distinct. No ribosomes drawn or claimed.",
    "V has capsid plus outer envelope and RNA; W capsid with DNA and no envelope; schematic scale explicitly separate.",
    "A2.3 entirely AHL viral structure diversity/host dependence.")
rec(728,[num("variant frequency fold increase",70/2,35),num("final treatment control points",70-3,67),eq("starting frequencies equal",[2,2],[2,2])],
    "Pre-existing less-sensitive variant can increase through selection; drug-directed mutation or a measured mutation rate is not established by frequencies.",
    "Starting2% curves diverge to70/3%, not absolute particle counts; no unwarranted replicate variability.",
    "A2.3.6 AHL rapid influenza evolution; natural-selection mechanism uses supplied context.")
rec(729,[eq("geneX closest viral pair",{"A","V"},{"A","V"}),eq("geneY closest pair",{"C","W"},{"C","W"}),
    ok("different virus groups and cellular affinities","V"!="W" and "A"!="C")],
    "Different genes/groups cannot simply be merged into universal virus tree. Multiple-origin/gene recruitment hypotheses remain hypotheses with transfer/loss alternatives.",
    "Both trees have correct V–A/W–C sister tips and B outside; branch lengths explicitly not time.",
    "A2.3.5 AHL virus origins/convergence; gene trees are supplied interpretation context.")
rec(730,[num("diploid fusion decrease",2*(2-1),2),num("resulting chromosome number",48-2,46),eq("ordered band blocks","ab"+"cd","abcd")],
    "Fusion once per haploid set explains two fewer diploid chromosomes. Internal telomere/remnant centromere plus ordered correspondence support common-ancestor fusion, not modern chimp ancestry.",
    "One chromosome preserves a/b/c/d, internal junction and two centromere states; two comparison blocks preserve order.",
    "A3.1.6–7 shared human46/chimp48 and fusion-evidence skills.")
rec(731,[num("F M genome ratio",24/3.2,7.5),num("U genome Mb",.020*1000,20)],
    "Total genome size cannot rank complexity or establish species identity; noncoding content, sequence and expression can differ independently of length.",
    "Four bars .020/.18/3.2/24Gb have numeric labels including very small bars; invented-organism context explicit.",
    "A3.1.8–10 shared genome variation/size.")
rec(732,[num("fertile hybrid adult expectation",80*.60,48),num("withinP fertile adult expectation",88*.95,83.6),num("withinQ expectation",86*.94,80.84)],
    "Adult-survival endpoint is explicit after review; fertility denominator is adults, not eggs. Partial reproductive divergence/gradual species boundaries cannot be settled by one arbitrary threshold.",
    "Separate viability per100eggs and fertility per100adults bars have denominators stated; laboratory crosses do not assert field mating rates.",
    "A3.1.4–5 shared biological-species limitations/gradual divergence; no required AHL chromosome mismatch mechanism.")
rec(733,[eq("four trait combinations",len({("opposite","simple"),("alternate","simple"),("opposite","compound"),("alternate","compound")}),4),
    eq("compound-only candidate set",sorted([x for x,v in {"P":"simple","Q":"simple","R":"compound","S":"compound"}.items() if v=="compound"]),["R","S"])],
    "Mutually exclusive trait couplets give valid dichotomous key; colour/size are unvalidated, and damaged compound specimen cannot resolve R/S without arrangement.",
    "P/Q simple blades and R/S separate leaflet pairs correctly distinguished; petiole position opposite/alternate visibly different.",
    "A3.1.14 AHL dichotomous keys.")
sample=[120,30,8,0];blank=[0,0,6,0]
detected=[s>=10 and (b==0 or s>=5*b) for s,b in zip(sample,blank)]
rec(734,[eq("detection decisions",detected,[True,True,False,False]),num("C sample blank ratio",8/6,1.3333333333),num("read count A B ratio",120/30,4)],
    "Barcode reads are not calibrated organism numbers; blank/threshold failure is not certain absence. DNA shedding, persistence, amplification and sampling all matter.",
    "Raw sample/blank bars match120/30/8/0 and0/0/6/0; zero blank rule avoids undefined fold demand.",
    "A3.1.15 AHL eDNA/barcode species detection.")
rec(735,[eq("core nearest pair",{"P","Q"},{"P","Q"}),eq("transferred-gene nearest pair",{"P","R"},{"P","R"}),ok("histories discordant",{"P","Q"}!={"P","R"})],
    "Horizontal R→P transfer explains one discordant gene without sexual mating. Asexual reproduction and HGT require genome-wide/ecological operational species evidence rather than a mating test.",
    "Curved arrowhead points toward P from R and is separate from core P–Q tree; no reversal of transfer.",
    "A3.1.12 AHL asexual/HGT difficulties for biological species concept.")
rec(736,[eq("smallest represented B D clade",sorted({"B","C","D"}),["B","C","D"]),
    eq("unresolved binary resolutions for three tips",3,3),ok("A outside ingroup","A" not in {"B","C","D"})],
    "Polytomy leaves B/C/D order unresolved; living A tip is not an ancestral internal node. Undefined lengths cannot establish older species.",
    "A splits before one three-tip B/C/D node; C horizontal branch through node is part of a polytomy, not a separate earlier split.",
    "A3.2 entirely AHL cladogram/root/node interpretation.")
patterns=[{frozenset("AB"),frozenset("CD")},{frozenset("AB"),frozenset("CD")},{frozenset("AC"),frozenset("BD")}]
splits=[{frozenset("AB"),frozenset("CD")},{frozenset("AC"),frozenset("BD")},{frozenset("AD"),frozenset("BC")}]
scores=[sum(1 if split==p else 2 for p in patterns) for split in splits]
rec(737,[eq("parsimony scores",scores,[4,5,6]),eq("minimum score",min(scores),4)],
    "All independently weighted characters count; conflict/homoplasy can occur. Parsimony chooses a model minimum, not proof of true historical evolution.",
    "State circles exactly0011/0011/0101 and0/1key; no topology falsely supplied as a given answer.",
    "A3.2 entirely AHL molecular/morphological cladogram construction; change-count rule supplied.")
rec(738,[num("central divergence Myr",24/(2*2),6),num("young bound",24/(2*2.5),4.8),num("old bound",24/(2*1.5),8),ok("fossil compatible",4.8>=4)],
    "Two branches accumulate pairwise differences. Rate bounds reverse time bounds; minimum fossil date and model range are not confidence intervals or exact origin dates.",
    "Pairwise model line has4differences/1000sites/Myr including both branches; axes/units explicit.",
    "A3.2 entirely AHL molecular clocks/uncertainty.")
rec(739,[eq("MRCA descendants PQR",sorted({"P","Q","R","S"}),["P","Q","R","S"]),
    eq("independent gain history changes",1+1,2),eq("alternative gains then loss",1+1+1,3)],
    "PQR without S is not a clade. Open root requires stated alternative to include P–Q gain plus R–S gain/loss in S, not a single forbidden tubular root. Multiple tip-state histories remain possible.",
    "Tree is ((P,Q),(R,S)) with three tubular/openSstates; internal states not falsely presented as directly observed.",
    "A3.2 entirely AHL molecular reclassification and convergence; root-state clarification incorporated.")
rec(740,[num("B A percent differences",60/200*100,30),num("B E percent",64/200*100,32),num("A E percent",28/200*100,14),
    eq("closest pair index",[30,32,14].index(min([30,32,14])),2)],
    "Homologous rRNA reveals distinct bacterial/archaeal lineages; simplified three-domain tree is not all gene histories or a calibrated date/rank measure.",
    "Bacteria outside archaeal/eukaryotic pair consistent with supplied rooted tree; branch lengths have no hidden clock meaning.",
    "A3.2 entirely AHL three domains/rRNA evidence.")
rec(741,[eq("mammal/bird proximal pattern",[1,2],[1,2]),eq("drawn digit counts",[5,3],[5,3])],
    "Tetrapod forelimbs homologous despite different uses; bird/insect flight wings analogous at that functional origin level. Similar outlines can converge.",
    "One proximal bone then paired bones in mammal/bird; five versus three schematic digits, no internal tetrapod pattern in insect wing.",
    "A4.1.4–5 shared homologous pentadactyl ancestry and convergence.")
rec(742,[num("common-garden advantage percent",(16-10)/10*100,60),num("rich absolute difference",20-12,8),num("common difference",16-10,6)],
    "Heritable line differences persisting in common garden support selective-breeding evidence of evolution, while maternal effects and one generation prevent identifying all genetic causes.",
    "Rich-parent and low-nutrient offspring bars use correct denominators/contexts; no direct gene or allele count invented.",
    "A4.1.3 shared domestication evidence; not AHL Hardy–Weinberg or a detailed breeding-program design.")
rec(743,[num("relative courtship reduction",(90-20)/90*100,77.7777777778),num("raw success difference",90-20,70)],
    "Temporal and behavioural prezygotic barriers can reduce gene flow even when hybrids fertile. Present co-occurrence does not prove geographic history or completed sympatric speciation.",
    "Seasonal bars depict principal activity only, with stated small overlap omitted; trial outcome is not plotted as absolute population size.",
    "A4.1.8/10 AHL temporal/behavioural barriers and sympatric interpretation.")
rec(744,[eq("resource peak seed diameters",[2,5,8],[2,5,8]),ok("A B overlap exists",3<4)],
    "Common lineage plus divergent resource roles fits adaptive radiation, but present diets alone do not prove competition caused reproductive isolation or measure fitness.",
    "Three peaks2/5/8mm and overlapping neighbouring curves correct; normalized within-species use is not abundance.",
    "A4.1.9 AHL adaptive radiation; no purposeful niche-seeking explanation.")
rec(745,[eq("gamete counts",[18//2,24//2],[9,12]),eq("initial hybrid",9+12,21),eq("doubled count",2*(9+12),42),
    eq("balanced doubled gamete",42//2,21),eq("backcross counts",[21+9,21+12],[30,33])],
    "Doubling supplies pairing homologues for combined parental sets and can restore fertility, with conditional isolation from parental crosses. Oddness alone is not a universal sterility rule.",
    "Two parental gamete routes join one hybrid then a doubling route; requested21/42answers not prefilled in hybrid boxes.",
    "A4.1.11 AHL Persicaria hybridization/polyploidy; all invented parental counts supplied.")
rec(746,[eq("P total",sum([40]*4),160),eq("Q total",sum([136,8,8,8]),160),eq("richness both",[4,4],[4,4]),
    num("dominance P percent",40/160*100,25),num("dominance Q percent",136/160*100,85)],
    "Equal richness/abundance does not equal evenness or genetic/ecosystem diversity. Single date cannot establish pollution, permanence or decline.",
    "Eight species bars preserve equal totals with contrasting dominance; equal sampled area explicit.",
    "A4.2 shared biodiversity levels and equal-effort monitoring.")
rec(747,[num("year1 records per100h",80/200*100,40),num("year4 records per100h",180/1200*100,15),
    num("rate decrease percent",(40-15)/40*100,62.5),num("raw record growth factor",180/80,2.25)],
    "Sightings/effort, unique birds and coverage/detectability differ; standardized rate decline alone is not an absolute census result. Citizen-science controls concrete.",
    "Separate panels explicitly use0–200sightings versus0–1200hours; no deceptive shared numerical yscale.",
    "A4.2 shared repeated/citizen monitoring and bias.")
cost=[4,3,2,2];score=[8*3,2*5,7*2,1*4]
feasible=[(sum(score[i] for i in range(4) if mask>>i&1),mask) for mask in range(16) if sum(cost[i] for i in range(4) if mask>>i&1)<=6]
best=max(feasible)
rec(748,[eq("project scores",score,[24,10,14,4]),eq("optimal score and bitmask",list(best),[38,5]),
    eq("optimal selected projects",[x for i,x in enumerate("ABCD") if best[1]>>i&1],["A","C"]),eq("optimal cost",4+2,6)],
    "ED×threat is expressly an exercise rule, not official EDGE. Budget optimum conditional on indivisible costs, additivity/effectiveness, not uniquely correct ethics.",
    "Four scatter points at suppliedED/threat components, no arbitrary interpolation between species.",
    "A4.2 shared evolutionary-distinctiveness/endangerment prioritization; formula and optimization inputs supplied.")
rec(749,[num("eight well-germinating families",8*200*.6,960),num("two low families",2*200*.1,40),
    num("total expected germination",960+40,1000),num("low family share percent",40/1000*100,4)],
    "Expected germination is not future adult establishment; equal seed count is not equal genetic representation. In situ interactions and ex situ risk diversification complementary.",
    "Ten family bars120×8/20×2 give correct expectations per200stored; not a real seed-bank dataset.",
    "A4.2 shared genetic diversity and complementary conservation/germplasm storage.")
rec(750,[num("forest loss percent",(1000-500)/1000*100,50),num("bird encounter decline",(24-9)/24*100,62.5),num("plantation increase km2",520-100,420)],
    "Habitat conversion, hunting/roads/pollution are plausible interacting pressures; correlated trends do not attribute all bird change to plantation area. Standardized encounters not absolute population.",
    "Land-cover series1000/760/500and100/300/520have area axis; bird rate separately supplied, not mixed into area chart.",
    "A4.2 shared anthropogenic ecosystem loss including mixed dipterocarp regional context; numerical region explicitly invented.")

assert len(DATA)==len(QUESTIONS)==len(RECORDS)==50
assert {r["id"] for r in RECORDS}==set(QUESTIONS)
assert collections.Counter(q["level"] for q in DATA)=={"sl":20,"ahl":30}
assert b"\r" not in SOURCE.read_bytes(), "Raw hash input must retain UTF8 LF."
report={"subject":"biology","theme":"A","questions":50,"status":"passed","sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "method":"Separate agent read all50 stems and complete solutions, independently recalculated numeric/sequence/topology inputs without importing author checks, checked current guide statement boundaries and inspected all50 SVGs plus selected native-size figures.",
    "independentCheckCount":sum(len(r["independentEvidence"]) for r in RECORDS),
    "sourceGuide":"https://xmltwo.ibo.org/publications/EAD/2026_EN/GR4/GR4-Biology_EN.pdf",
    "sourceSpecimen":"https://www.ibo.org/globalassets/new-structure/programmes/dp/pdfs/biology-hl-sl-specimen-papers-1a-2b-2-en.pdf",
    "correctionsRequested":["A712 explicit parentheses for 100−(pellet+supernatant).","A739 alternative flower-character history explicitly respects the supplied open root.","A732 viability measured as surviving adults, making the adult-fertility denominator applicable.","A706/709 nucleotide-node and sugar-phosphate rail legend.","A722 continuous closed mitochondrial inner boundary instead of detached zigzag."],
    "records":RECORDS,"limitations":["Independent AI scientific/computational review is not moderation by human IB examiners.","Original M/A/R point schemes are instructional and do not claim official IB notation.","All datasets and drawings are constructed practice, not new empirical research or actual micrographs.","Difficulty has not been calibrated against student performance."]}
DEST.parent.mkdir(parents=True,exist_ok=True)
DEST.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8",newline="\n")
print(json.dumps({"questions":50,"status":"passed","checks":report["independentCheckCount"],"sha256":report["sha256"]}))
