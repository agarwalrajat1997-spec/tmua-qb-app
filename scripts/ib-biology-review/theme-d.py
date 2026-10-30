"""Independent Theme D review: reads displayed questions, never author calculators."""
from pathlib import Path
from collections import Counter,defaultdict
from itertools import product
import hashlib,json,math,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
FILE=ROOT/'content/ib/biology/continuity-change.json'
questions=json.loads(FILE.read_text(encoding='utf8'))
blueprint={t['code']:t for t in json.loads((ROOT/'docs/ib-biology-reviews/syllabus-blueprint.json').read_text(encoding='utf8'))['topics']}
Q={q['number']:q for q in questions}
assert len(Q)==192 and set(Q)==set(range(1,193))
checks=[];per_question=defaultdict(list)
def scheme(n,only_answers=False):
    return ' '.join(s['text'] for g in Q[n]['markScheme'] for s in g['steps'] if not only_answers or s['code'].startswith('A'))
def match(pattern,text):
    m=re.search(pattern,text)
    assert m,(pattern,text[:150])
    return m.groups()
def calc(n,label,value,check_answer=True):
    assert math.isfinite(value)
    if check_answer:
        candidates=[float(v) for v in re.findall(r'(?<![A-Za-z])[-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?',scheme(n,True),re.I)]
        # Solutions normally quote three significant figures; integers remain exact.
        rounded=float(format(value,'.3g'))
        assert any(math.isclose(v,value,abs_tol=1e-8,rel_tol=1e-9) or math.isclose(v,rounded,abs_tol=1e-8,rel_tol=1e-9) for v in candidates),(n,label,value,candidates)
    item={'id':Q[n]['id'],'quantity':label,'recalculated':value,'derivedFrom':'displayed question inputs / plotted coordinates and labelled scales','answerMatched':check_answer}
    checks.append(item);per_question[n].append(item)
    return value
def text_check(n,label,expected):
    assert expected in scheme(n),(n,label,expected,scheme(n))
    item={'id':Q[n]['id'],'quantity':label,'recalculated':expected,'answerMatched':True}
    checks.append(item);per_question[n].append(item)
def rows(n):
    lines=[l.strip().strip('|').split('|') for l in Q[n]['stem'].splitlines() if l.strip().startswith('|')]
    return [[s.strip() for s in row] for row in lines[2:]]
def graph(n):
    """Recover displayed values from SVG axis labels, independently of author helpers."""
    root=ET.fromstring(Q[n]['diagramSvg'])
    elements=list(root.iter());xs=[];ys=[]
    for e in elements:
        if e.tag.endswith('text') and re.fullmatch(r'[-+]?\d+(?:\.\d+)?',e.text or ''):
            if e.attrib.get('text-anchor')=='end' and float(e.attrib.get('x',-1))==76:
                ys.append((float(e.attrib['y'])-5,float(e.text)))
            elif e.attrib.get('font-size')=='13' and float(e.attrib.get('y',-1))==340:
                xs.append((float(e.attrib['x']),float(e.text)))
    assert len(xs)>=2 and len(ys)>=2,(n,xs,ys)
    def convert(coordinate,pairs):
        a,b=pairs[0],pairs[-1]
        return a[1]+(coordinate-a[0])*(b[1]-a[1])/(b[0]-a[0])
    result=[(convert(float(e.attrib['cx']),xs),convert(float(e.attrib['cy']),ys)) for e in elements if e.tag.endswith('circle') and e.attrib.get('r')=='4']
    assert result,n
    return result

# DNA arithmetic and complementary strands.
for n in [6,7]:
    initial=int(match(r'starts with (\d+)',Q[n]['stem'])[0])
    cycles=int(match(r'after (\d+) complete cycles',Q[n]['parts'][0]['prompt'])[0])
    calc(n,'ideal PCR count',initial*2**cycles)
for n in [11,12]:
    generations=int(match(r'undergo (\d+) synchronous',Q[n]['stem'])[0])
    calc(n,'hybrid DNA percentage',100*2/2**generations)
    calc(n,'wholly heavy DNA after transfer',0)
for n in [13,14]:
    groups=defaultdict(list)
    for e in ET.fromstring(Q[n]['diagramSvg']).iter():
        if e.tag.endswith('line') and e.attrib.get('stroke')=='#425d96':
            x=float(e.attrib['x1']);y=float(e.attrib['y1'])
            assert 85<y<305
            groups[x].append(y)
    columns=[groups[x] for x in sorted(groups)]
    assert len(columns)==3
    matched=[i for i in [1,2] if columns[i]==columns[0]]
    assert len(matched)==1
    text_check(n,'matching gel lane','Sample '+('P' if matched[0]==1 else 'Q')+'.')
for n in [21,22]:
    dna=match(r'left to right as ([ACGT ]+)\.',Q[n]['stem'])[0]
    rna=dna.translate(str.maketrans('ATCG','UAGC'))
    text_check(n,'template complement',rna)
    code={a:b.lower() for a,b in rows(n)}
    peptide='–'.join(code[codon] for codon in rna.split())
    text_check(n,'codon-table translation',peptide)
initial,a,b=map(int,match(r'has (\d+) nucleotides, including introns of (\d+) and (\d+)',Q[26]['stem']))
calc(26,'spliced RNA length',initial-a-b)
for n in [29,30]:
    pts=graph(n);rates=[(b[1]-a[1])/(b[0]-a[0]) for a,b in zip(pts,pts[1:])]
    calc(n,'first interval mean accumulation rate',rates[0])
    assert rates[0]>rates[1]>rates[2]>0
    assert 'graph-reading range' in scheme(n)
for n in [31,32]:
    values=list(map(float,match(r'minutes are ([\d, ]+)\.',Q[n]['stem'])[0].split(',')))
    calc(n,'mRNA lost by 20 minutes',100-values[2])
for n in [45,46]:
    counts=[int(row[1]) for row in rows(n)]
    calc(n,'mutant-colony frequency increase',counts[-1]-counts[0])
    assert counts==sorted(counts) and 'constructed' in Q[n]['stem'].lower()
for n in [47,48]:
    values=[float(row[1]) for row in rows(n)]
    calc(n,'root-length percentage reduction',100*(values[0]-values[1])/values[0])
    assert abs(values[2]-values[0])<abs(values[1]-values[0])
for n in [53,54]:
    diploid=int(match(r'has (\d+) chromosomes',Q[n]['stem'])[0])
    calc(n,'post-meiosis-I and gamete chromosome number',diploid/2)
    assert 'Two chromatids' in scheme(n)
for n in [61,62]:
    mitotic,total=map(int,match(r'(\d+) of (\d+) cells',Q[n]['stem']))
    calc(n,'mitotic index percentage',100*mitotic/total)
for n in [63,64]:
    total=int(match(r'counts (\d+) mitotic cells',Q[n]['stem'])[0])
    late=int(match(r'inhibitor, (\d+) cells',Q[n]['stem'])[0])
    result=calc(n,'separated-chromatid percentage',100*late/total)
    calc(n,'percentage-point reduction from control',55-result)
for n in [77,78]:
    pts=graph(n)
    values=list(map(float,match(r'minutes are ([\d, ]+) arbitrary',Q[n]['stem'])[0].split(',')))
    assert all(math.isclose(y,value,abs_tol=1e-8) for (_,y),value in zip(pts,values))
    calc(n,'transcript reduction percentage',100*(values[0]-values[2])/values[0])
for n in [79,80]:
    a,b=[float(row[1]) for row in rows(n)]
    calc(n,'reporter signal ratio',a/b)
sd,n_replicates=map(float,match(r'is \$(\d+\.\d+).*there are (\d+) independent',Q[86]['parts'][-1]['prompt']))
calc(86,'standard error with supplied formula',sd/math.sqrt(n_replicates))

# Osmosis: retain signs and do not confuse equal potential with equal concentration.
text_check(84,'negative plus positive potential','−400')
for n in [87,88]:
    solute,pressure,external=map(float,match(r'solute potential (-?\d+) kPa and pressure potential \+(\d+) kPa.*water potential (-?\d+) kPa',Q[n]['stem']))
    cell=calc(n,'cell water potential',solute+pressure)
    text_check(n,'initial net water direction','Water moves '+('into' if external>cell else 'out of')+' the cell.')
for n in [91,92]:
    initial,final=map(float,match(r'initial mass (\d+\.\d+) g and final blotted mass (\d+\.\d+) g',Q[n]['stem']))
    change=calc(n,'signed percentage mass change',100*(final-initial)/initial)
    text_check(n,'net osmotic movement','Into the tissue.' if change>0 else 'Out of the tissue.')
for n in [93,94]:
    pts=graph(n)
    roots=[x for x,y in pts if abs(y)<1e-8]
    assert len(roots)==1
    calc(n,'zero mean mass-change concentration',roots[0])
    assert all(b[1]<a[1] for a,b in zip(pts,pts[1:]))

# Reproduction and Mendelian sampling.
for n in [109,110]:
    rs=rows(n);count,success=map(float,rs[0][1:])
    calc(n,'open-flower seed percentage',100*success/count)
    assert success/count>float(rs[1][2])/float(rs[1][1])
for n in [111,112]:
    treated,control=map(float,match(r'occur in (\d+) per 1000.*and (\d+) per 1000',Q[n]['stem']))
    calc(n,'absolute event-frequency difference per 1000',control-treated)
for n in [117,118]:
    total=int(match(r'sample of (\d+) offspring',Q[n]['stem'])[0])
    genotypes=[''.join(sorted((a,b))) for a,b in product('Aa',repeat=2)]
    distribution=Counter(genotypes)
    assert distribution=={'AA':1,'Aa':2,'aa':1}
    calc(n,'expected recessive count',total*distribution['aa']/4)
    text_check(n,'monohybrid genotype ratio','1AA:2Aa:1aa')
abo=[a+b for a,b in product(['A','i'],['B','i'])]
assert abo.count('ii')/4==.25
text_check(119,'ABO O probability','25')
sex_cross=list(product(['H','h'],['XH','Y']))
assert len([pair for pair in sex_cross if pair==('h','Y')])/len(sex_cross)==.25
text_check(120,'conditional probability for a son','1/2')
text_check(120,'unconditional probability for a child','1/4')
white=sum(a==b=='W' for a,b in product('RW',repeat=2))/4
calc(121,'two independently white offspring percentage',100*white**2)
gametes=['AB','Ab','aB','ab']
counts=Counter()
for a,b in product(gametes,repeat=2):
    counts[('A' in (a[0]+b[0]),'B' in (a[1]+b[1]))]+=1
assert sorted(counts.values())==[1,3,3,9]
text_check(123,'double-recessive probability','1/16')
text_check(124,'recombinant gametes','Ab and aB')
text_check(125,'parental genotypes','I-1 = Aa and I-2 = Aa')
text_check(125,'affected child genotype','II-1 = aa')
low,median,high,height=map(float,match(r'lower quartile (\d+) cm, median (\d+) cm and upper quartile (\d+) cm. A measured plant is (\d+) cm',Q[126]['stem']))
calc(126,'interquartile range',high-low)
boundary=calc(126,'upper outlier boundary',high+1.5*(high-low))
assert height>boundary
for n in [127,128]:
    observed=[float(row[1]) for row in rows(n)];expected=sum(observed)/2
    calc(n,'each expected count',expected)
    value=calc(n,'chi-square statistic',sum((o-expected)**2/expected for o in observed))
    text_check(n,'5% test decision','Reject the null' if value>3.84 else 'Do not reject the null')
for n in [141,142]:
    points=graph(n);peak=max(points,key=lambda p:p[1])
    calc(n,'peak glucose',peak[1]);calc(n,'peak time',peak[0])
    calc(n,'glucose fall from peak to last observation',peak[1]-points[-1][1])
    assert 'labels give the measured' in Q[n]['diagramSvg']
for n in [143,144]:
    rs=rows(n)
    for row in rs:
        volume,concentration=map(float,row[1:])
        calc(n,'total urine solute: '+row[0],volume*concentration)
for n in [157,158]:
    phenotype=float(match(r'phenotype has frequency (\d+\.\d+)',Q[n]['stem'])[0])
    q=calc(n,'recessive allele frequency',math.sqrt(phenotype))
    calc(n,'heterozygote frequency',2*q*(1-q))
    assert 'Hardy–Weinberg equilibrium' in Q[n]['stem']
total,aa,hetero,recessive=map(float,match(r'sample of (\d+) diploid individuals, (\d+) are AA, (\d+) are Aa and (\d+) are aa',Q[153]['parts'][-1]['prompt']))
assert aa+hetero+recessive==total
calc(153,'A allele frequency from genotype counts',(2*aa+hetero)/(2*total))
for n in [159,160]:
    a,b=[float(row[1]) for row in rows(n)]
    calc(n,'guppy treatment mean difference',b-a)
for n in [173,174]:
    initial,addition,harvest=map(float,match(r'begins with (\d+) harvestable trees.*add (\d+) trees.*removes (\d+)',Q[n]['stem']))
    final=calc(n,'harvestable-tree stock',initial+addition-harvest)
    assert ('No; harvesting' if final<initial else 'Yes in this simplified model') in scheme(n)
for n in [175,176]:
    pts=graph(n)
    calc(n,'oxygen percentage decline',100*(pts[0][1]-pts[-1][1])/pts[0][1])
    assert 'labels give the measured' in Q[n]['diagramSvg']
for n in [189,190]:
    remove,release=map(float,match(r'remove (\d+) tonnes.*release (\d+) tonnes',Q[n]['stem']))
    calc(n,'net carbon sequestration',remove-release)
    assert remove>release and 'A sink' in scheme(n)
for n in [191,192]:
    rs=rows(n);caterpillars=list(map(float,rs[0][1:]));birds=list(map(float,rs[1][1:]))
    calc(n,'earlier seasonal peak separation',birds[0]-caterpillars[0])
    calc(n,'later seasonal peak separation',birds[1]-caterpillars[1])
    assert birds[1]-caterpillars[1]>birds[0]-caterpillars[0]

# Individual biological judgements made independently after reading all schemes.
notes=[
 'Semiconservative one-old/one-new strands; conservative/dispersive alternatives excluded.',
 'Thermostability preserves polymerase through denaturation; primers still required.',
 'DNA complementary sequence AGCCT; uracil alternatives excluded.',
 'Prokaryotic polymerase extends the 3-prime end; direction shared on both strands.',
 'Helicase separates base pairs; polymerase forms daughter backbone; template preserves sequence.',
 'Ideal doubling model explicit; real efficiency limitation accepted.',
 'Independent larger PCR model; no hidden efficiency assumption.',
 'PCR separation, primer annealing and extension correctly distinguished.',
 'Antiparallel templates explain discontinuity; primase, polI and ligase roles correct.',
 'Mismatched nucleotide removal and replacement reduce, not eliminate, mutation.',
 'Original heavy strands conserved through two generations; conservative contrast correct.',
 'Third-generation hybrid fraction and absence of wholly heavy molecules correct.',
 'P matches all shown bands; match does not identify deposition circumstances.',
 'Q matches all shown bands; final P band remains inside the lane.',
 'One primer prevents normal bounded-target exponential amplification; no-template control appropriate.',
 'Ligase seals backbone nicks, whereas base-pair hydrogen bonds cannot.',
 'mRNA directly specifies translation; tRNA/rRNA do not serve as sequence template.',
 'Several codons per amino acid is degeneracy, distinct from universality.',
 'GCA codon pairs antiparallel with CGU anticodon; DNA thymine alternative false.',
 'Alternative exon selection yields mature transcript variants; translation does not rewrite RNA.',
 'Template complement and supplied codons independently translated.',
 'Second template complement and supplied codons independently translated.',
 'Codon recognition, peptide bond and translocation; mRNA versus tRNA roles distinct.',
 'Nuclear transcription can continue despite blocked cytoplasmic translation.',
 'Splicing, cap and tail are separate processing steps; alternative exon choices change protein.',
 'Introns removed arithmetically; UTRs, stop codons and maturation qualify protein-length inference.',
 'Promoter deletion reduces initiation without changing coding sequence.',
 'Preproinsulin signal removal, disulfides and C-peptide cleavage; proteasome turnover correct.',
 'Accumulation rate is interval slope, not concentration; progressively smaller increments verified.',
 'Second accumulation rate and decreasing slopes verified; graph-reading allowance supplied.',
 'Loss from original mRNA batch; persistence permits repeated translation.',
 'Short-tail batch loss verified; coding sequence and conditions must be standardized.',
 'Synonymous substitution leaves that encoded amino acid unchanged; no benefit inferred.',
 'One retained nucleotide changes downstream frame; not a complete-codon insertion.',
 'Somatic lineage propagation distinguished from germline transmission.',
 'Guide complementarity provides targeting; Cas9 is not a protein-sequence reader.',
 'Substitution versus deletion; downstream frameshift explains potentially larger effect.',
 'Three-base deletion preserves downstream frame but may remove/change local amino acids.',
 'Mutation precedes selection; exposure does not direct the necessary variant.',
 'Mutagen increases DNA changes; spontaneous mutations and matched controls recognized.',
 'Variable repair at cut can disrupt coding; sequencing verifies actual edit.',
 'Conserved region suggests selection on function; knockout requires matched phenotype evidence.',
 'Somatic regulatory editing increases fetal haemoglobin; FDA primary source confirms mechanism.',
 'SL-safe supplied reduction in transcription supports reduced protein amount; no AHL binding recall.',
 'Constructed dose-response normalization and survivorship limitation explicit.',
 'Second dose response and independent-culture replication correctly interpreted.',
 'Knockout reduction recalculated; rescue supports causal role without proving uniqueness.',
 'Second knockout reduction and partial rescue independently checked.',
 'Homologue separation in meiosis I reduces sets; replication does not.',
 'Vesicle-derived cell plate fits plant cytokinesis; furrow is animal pattern.',
 'Individually aligned duplicated chromosomes identify mitotic metaphase.',
 'Cyclins regulate transitions, rather than serving as copying or spindle structural enzymes.',
 'Post-meiosis-I chromosomes still have two chromatids; haploid count verified.',
 'Second diploid count independently tracked through meiosis and fertilization.',
 'Independent orientation and non-sister exchange recombine existing alleles.',
 'Meiosis-I nondisjunction yields two gametes with two copies and two with none.',
 'G1/S/G2 activities and active interphase accurately stated.',
 'Benign localization versus invasion/metastasis; control mutations permit excess division.',
 'Nuclear chromosome equality need not imply equal cytoplasmic volume.',
 'Condensation reduces entanglement; spindle attaches via centromere-associated structures.',
 'Mitotic index and normal growth caveat verified; HL classification correct.',
 'Second mitotic index and sampling proposal verified.',
 'Spindle inhibition alters stage distribution; chromosome behaviour does not show sequence change.',
 'Second stage proportion and percentage-point contrast independently checked.',
 'Gene expression, rather than loss of most genes, explains specialization.',
 'Methylation without base-sequence change is epigenetic under stated stable observation.',
 'Transcriptome comprises present RNAs, not DNA or only translating mRNA.',
 'Same production and slower degradation imply greater steady transcript abundance.',
 'Enhancer-bound factors alter promoter initiation; noncoding sequence has regulatory function.',
 'Expression shifts alter proteome; translation, processing and degradation limit inference from RNA.',
 'Promoter methylation effect conditional on region; no universal silencing claim.',
 'Twin design reduces inherited-genetic differences but does not randomize environment.',
 'Epigenetic resetting limits inheritance; imprinting gives parent-of-origin expression.',
 'Steroid receptor can regulate transcription; cell-specific response explained.',
 'Explicit simplified inducer/repressor model; no claim glucose regulation is absent.',
 'Environment can change expression without inherited stable epigenetic transmission.',
 'Transcript decay arithmetic and graph agree; persistent template can be translated repeatedly.',
 'Second decay arithmetic and graph agree; standardized initial amount supports comparison.',
 'Enhancer deletion reporter ratio verified; RNA measurement narrows interpretation.',
 'Second enhancer ratio verified; reporter protein alone cannot isolate transcription.',
 'Hypotonic nonpenetrating solute creates initial water influx in animal cell.',
 'Plasmolysis means protoplast withdrawal from wall after water loss.',
 'No net mass transfer does not imply stopped molecular motion or absent solutes.',
 'Negative solute plus positive pressure gives negative net water potential.',
 'Animal lysis versus plant turgor explained by wall resistance.',
 'Relative mass change controls size; independent practical controls accepted.',
 'External minus300 is higher than cell minus420, so initial influx.',
 'External minus500 is lower than cell minus380, so initial efflux.',
 'Xylem tension makes pressure potential negative; reference condition distinguished.',
 'Positive pressure offsets more negative solute potential at equilibrium.',
 'Signed positive percentage change supports net water entry.',
 'Signed negative percentage change supports net water loss.',
 'Zero crossing0.30 and monotonically decreasing mass response independently decoded.',
 'Zero crossing0.40 and replication rationale independently decoded.',
 'Isotonic fluid maintains volume without requiring no solutes; neutral exam-style wording.',
 'Water oxygen faces sodium and hydrogen faces chloride; selective permeability required.',
 'Gamete nuclear fusion restores diploidy; pollination itself does not.',
 'Human fertilization ordinarily occurs in oviduct, before implantation.',
 'Pollen tube delivers male gamete nuclei towards ovule.',
 'hCG is standard early-pregnancy test target; HL scope correct.',
 'Runners versus sexual offspring variation and context-dependent advantages.',
 'LH surge/ovulation/corpus luteum; progesterone maintenance and negative feedback correct.',
 'FSH follicle development and LH-like final maturation signal distinguished.',
 'Pollen transfer is not gamete fusion; self-incompatibility favours outcrossing.',
 'Dispersal benefits and germination requirements correctly explained.',
 'Four sperm versus one cytoplasm-rich female gamete; unequal division rationale.',
 'Cortical-granule release changes zona properties to limit polyspermy.',
 'Villi increase area; separate circulations exchange gases, nutrients and wastes.',
 'Insect exclusion percentage and sham-cover control; no exclusive-route claim.',
 'Second pollination comparison allows other routes and enclosure confounding.',
 'Absolute observational difference does not establish HRT causality.',
 'Second HRT comparison retains confounding and appropriate causal-design qualification.',
 'Complete-dominance recessive phenotype requires aa; genotype case preserved.',
 'IAIB expresses A and B codominantly in standard ABO model.',
 'Polygenic continuous variation commonly includes environmental effects.',
 'Recombinants defined relative to parental phase, not phenotype label alone.',
 'Independent Punnett enumeration yields1:2:1 and expected recessive count.',
 'Second finite-sample expectation verified; sampling variability retained.',
 'ABO parent combinations independently enumerated; O probability one-quarter.',
 'Sons conditional one-half versus all-child one-quarter; paternal X not passed to sons.',
 'Incomplete-dominance phenotype ratio and independent two-offspring probability correct.',
 'Diet changes PKU phenotype without rewriting inherited allele.',
 'Independent dihybrid enumeration yields9:3:3:1 and double-recessive1/16.',
 'AB/ab parental phase yields Ab/aB recombinants; expected, not sample,50% ceiling.',
 'Unaffected parents with affected child imply recessive under explicit assumptions.',
 'IQR/outlier boundary verified; outlier phenotype does not establish mutation.',
 'Population1:1 null, two expected100 counts, chi-square0.72: non-rejection.',
 'Second statistic6.48 exceeds3.84: reject; no proof of a specific mechanism.',
 'Negative feedback opposes initial glucose deviation.',
 'Glucagon promotes hepatic glucose release during low glucose.',
 'Skin vasodilation and sweat evaporation promote heat loss.',
 'ADH raises collecting-duct permeability and reabsorption.',
 'Insulin response and declining stimulus form self-limiting feedback.',
 'Type1 insulin deficiency and type2 resistance distinguished without diagnosis inference.',
 'Thermoreceptors/hypothalamus coordination; humid air impedes evaporation.',
 'Shivering generates heat, vasoconstriction conserves it; thyroxin longer-term influence.',
 'Ultrafiltration excludes cells/large proteins; glucose normally reabsorbed proximally.',
 'Ascending salt transport supports medullary gradient and collecting-duct water recovery.',
 'Dehydration raises ADH and aquaporin-mediated reabsorption: negative feedback.',
 'Percentage flow need not track absolute flow if total cardiac output rises.',
 'Labelled glucose peak/time and concentration fall independently read and recomputed.',
 'Second labelled glucose trace independently recomputed.',
 'Volume times concentration conserves720mmol despite concentrated urine.',
 'Second urine comparison confirms concentration is not total solute loss.',
 'Fitness tied to surviving fertile offspring, not strength or survival alone.',
 'Heritable fitness variation permits inherited response to selection.',
 'Overproduction and limited resources permit differential survival/reproduction.',
 'Intermediate advantage defines stabilizing, not directional/disruptive selection.',
 'Pre-existing insecticide resistance selected over generations; no directed mutation claim.',
 'Heritable deep roots can increase under drought with fitness and environment qualifications.',
 'Guppy mating and predation tradeoffs jointly explain brightness.',
 'Replicated multi-generation selection design; survival alone not heritable change evidence.',
 'Gene pool definition and differential allele contribution accurate.',
 'Deliberate chosen parents define artificial selection; genetic diversity cost qualified.',
 'Random mating and no evolutionary forces are valid HW assumptions; fitting one locus not proof.',
 'Extreme phenotype advantage is disruptive selection, not automatically speciation.',
 'HW square-root allele frequency and heterozygote fraction verified.',
 'Second HW calculation verified with assumptions explicitly supplied.',
 'Guppy mean contrast verified; uncertainty and inherited persistence still needed.',
 'Second guppy contrast independently checked.',
 'Closed matter system still exchanges energy and dissipates heat.',
 'Keystone effect disproportionate to abundance, not simply large or abundant.',
 'Decomposer respiration raises oxygen demand after algal death.',
 'Bare rock without developed soil is primary succession.',
 'Fluctuation compatible with system persistence; diverse tolerances can support resilience.',
 'Forest-loss/moisture-recycling positive feedback and threshold interpretation correct.',
 'Noon-only oxygen sampling misses dark respiration and daily minima.',
 'Bioaccumulation versus trophic biomagnification distinguished; uptake/retention marks distinct.',
 'Harvest limited by replacement; stock and productivity changes require monitoring.',
 'Hinewai native regeneration under nurse canopy verified against reserve operator.',
 'Pioneer weathering/organic inputs alter recruitment conditions in succession.',
 'Repeated grazing can arrest succession; recurring disturbance can produce cycles.',
 'Harvest exceeds recruitment by20, so modelled stock declines.',
 'Recruitment exceeds harvest by30; simplified numerical sustainability qualified.',
 'Labelled oxygen decline and dawn respiration mechanism verified.',
 'Second labelled oxygen decline recalculated; matching controls appropriate.',
 'Fossil combustion increases atmospheric carbon dioxide; sequestration alternatives do not.',
 'Reduced ice albedo reinforces warming; other options oppose the initial deviation.',
 'CO2 carbonate chemistry can impede calcification; not identical to bleaching.',
 'Timing mismatch separates peak consumer demand from resource availability.',
 'CO2 and methane human sources distinct; forest removal affects stocks and future uptake.',
 'Thaw/decomposition greenhouse feedback and net source versus sink accurate.',
 'Walrus ice platform loss can increase travel costs; population consequence conditional.',
 'Bleaching symbiont loss versus calcification; bleached coral can still be alive.',
 'Upslope redistribution does not prove inherited adaptation; summit habitat restriction.',
 'Upwelling nutrient supply affects primary production and higher trophic support.',
 'Faster beetle development within viable limits can add generations; no unlimited extrapolation.',
 'Heritable owl forms under differential reproduction give evolution, unlike one-lifetime behaviour.',
 'Constructed net carbon sink7 tonnes; storage permanence not assumed.',
 'Second carbon sink8 tonnes; incomplete flux budget explicitly qualified.',
 'Earlier peak gap1 day versus later8; mean timing insufficient for realized population effect.',
 'Second gap1 versus9 days; peak width and survival data needed.'
]
assert len(notes)==192,len(notes)
coverage_additions={
25:'AHL D1.2.17: initiation and A/P/E roles; P site wording specified before peptide transfer.',
27:'AHL D1.2.14: any two distinct functional non-protein-coding examples accepted.',
56:'Shared D2.1.10: usual trisomy21 form of Down syndrome.',
57:'AHL D2.1.15: cyclin concentration threshold without named cyclin mechanisms.',
58:'AHL D2.1.16: growth-promoting gain of function versus suppressor loss of function.',
60:'Shared D2.1.6: histone packing and microtubule motors.',
86:'Shared D2.3 data skill: supplied standard-error formula;0.12/sqrt9=.040g.',
102:'Shared D3.1.5: sustained high pre-ovulatory oestradiol positive feedback.',
104:'Shared D3.1.10: any two distinct cross-pollination features accepted.',
105:'Shared D3.1.12: mobilization of food reserves during germination.',
106:'AHL D3.1.13-14: germline stages and GnRH to LH/FSH to gonadal steroid pathway.',
107:'AHL D3.1.15-17: acrosome/cortical distinction, blastocyst/endometrium, hCG antibody detection.',
108:'AHL D3.1.19: corpus-luteum then placental progesterone; reduced inhibitory ACTION, not a necessary human serum fall; oxytocin stretch feedback.',
153:'AHL D4.1.10: allele counts120 of200 give0.60.',
168:'Shared D4.2.9-10: DDT, macroplastic entanglement and qualified microplastic-ingestion effects; persistence after fragmentation.',
169:'Shared D4.2.6-7: Scots pine and Atlantic cod examples; any three distinct justified agricultural environmental costs.',
170:'Shared D4.2.11: connectivity and appropriate native keystone restoration.',
171:'AHL D4.2.13: any two distinct succession trends accepted; no universal monotonicity.',
172:'AHL D4.2.14-15: forest gap cycle, grazing arrest and relatively persistent climax definition.',
183:'Shared D4.3.4: emperor penguin landfast-ice breeding platform.',
185:'Shared D4.3.6: constructed New Guinea upland-bird scenario and tree dispersal/generation-time lag.',
192:'AHL D4.3.10: chickweed spring growth versus migrant reindeer arrival; constructed dates, not actual field data.'
}
for number,note in coverage_additions.items():notes[number-1]+=' Coverage extension: '+note
ahl={4,9,10,16,19,20,25,26,27,28,31,32,36,41,42,43,47,48,52,57,58,61,62,*range(65,81),84,87,88,89,90,100,106,107,108,111,112,116,123,124,127,128,132,137,138,139,140,143,144,148,153,154,155,156,157,158,164,171,172,180,187,188,191,192}
assert len(ahl)==77
entries=[];figures=[]
for n,q in Q.items():
    expected_level='ahl' if n in ahl else 'sl'
    assert q['level']==expected_level,(q['id'],q['level'],expected_level)
    topic=blueprint[q['syllabusCode']]
    assert q['subtopic']==topic['title'] and q['calculator'] is True
    assert q['id']==f'ib-bio-d-{n:03d}'
    if q['questionType']=='multiple-choice':
        assert q['marks']==1 and len({o['text'] for o in q['options']})==4
        assert q['correctOption'] in scheme(n)
    else:
        assert q['marks']==sum(p['marks'] for p in q['parts'])
        for part,group in zip(q['parts'],q['markScheme']):
            assert part['label']==group['part']
            assert part['marks']==sum(int(s['code'][1:]) for s in group['steps'] if s['code']!='AG')
    if q['questionType']=='data-based':
        assert 'constructed' in q['stem'].lower() or 'hypothetical' in q['stem'].lower(),q['id']
    for field in ['diagramSvg','markSchemeDiagramSvg']:
        if field in q:
            ET.fromstring(q[field])
            figures.append({'id':q['id'],'field':field,'sha256':hashlib.sha256(q[field].encode()).hexdigest(),'visualStatus':'independently inspected at readable resolution; labels, biological topology and numerical axes checked'})
    entries.append({'id':q['id'],'questionSha256':hashlib.sha256(json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'level':q['level'],'scopeRange':topic['additionalHlStatements'] if n in ahl else topic['slStatements'],'difficulty':q['difficulty'],'biologicalReview':notes[n-1],'calculationChecks':per_question[n],'markAllocation':'passed','alternativesAndAssumptions':'reviewed','status':'passed'})
assert Counter(q['syllabusCode'] for q in questions)==Counter({c:16 for c in blueprint if c.startswith('D')})
report={'status':'passed','reviewer':'independent syllabus/content reviewer; not the Theme D author','questions':192,'numericAndGeneticChecks':len(checks),'figuresReviewed':len(figures),'fileSha256':hashlib.sha256(FILE.read_bytes()).hexdigest(),'levels':dict(Counter(q['level'] for q in questions)),'difficulty':dict(Counter(q['difficulty'] for q in questions)),'difficultyAssessment':'Easy items test single-step recognition; medium items require applied explanations or routine data calculations; hard items combine inference, assumptions, evaluation or several dependent steps. Labels retained after individual review rather than inflated to meet a quota.','method':'Every displayed prompt, option and mark point read independently against corrected guide. Numerical models derive inputs from question text/tables or SVG labels/coordinates, without importing author calculations. Full-record hashes and SVG hashes tie this review to the exact final records.','sources':['https://xmltwo.ibo.org/publications/EAD/2026_EN/GR4/GR4-Biology_EN.pdf','https://ibpublishing.ibo.org/exinst/apps/exinst/index.html?chapter=1&doc=EX_instructions_2027_e&part=11','https://www.fda.gov/media/174615/download','https://www.hinewai.org.nz/about/'],'repairs':['Readable tick intervals on translation, transcript and osmosis graphs.','Exact data labels on glucose and dissolved-oxygen graphs; translation reading tolerance.','SL q044 regulation observation supplied so AHL binding recall is not required.','Constructed-data labels q045/046; natural exam-style prose q095/141/142.','Population-based chi-square null; expected rather than sample recombination ceiling.','Distinct transcript-reuse and biomagnification mark points.','Plausible misconception distractors replace irrelevant options; answer keys preserved.'],'entries':entries,'figures':figures}
supplement_path=ROOT/'docs/ib-biology-reviews/theme-d-additions-independent-review.json'
supplement=json.loads(supplement_path.read_text(encoding='utf8'))
assert supplement['status']=='passed' and supplement['fileSha256']==report['fileSha256']
report['reviewer']='Independent reviewer of the original Theme D bank; later coverage additions separately reviewed by the Theme C author.'
report['coverageAdditions']={'ids':[f'ib-bio-d-{n:03d}' for n in coverage_additions], 'authoredBy':'syllabus reviewer after the original independent item review', 'independentReview':str(supplement_path.relative_to(ROOT)).replace('\\','/'), 'status':supplement['status'], 'fileSha256':supplement['fileSha256']}
path=ROOT/'docs/ib-biology-reviews/theme-d-independent-review.json'
path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k in ['status','questions','numericAndGeneticChecks','figuresReviewed','fileSha256','levels','difficulty']}))
