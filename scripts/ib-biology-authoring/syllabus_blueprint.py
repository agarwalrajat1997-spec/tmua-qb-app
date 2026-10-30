"""Original factual authoring map checked against the corrected official IB guide."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
GUIDE='https://xmltwo.ibo.org/publications/EAD/2026_EN/GR4/GR4-Biology_EN.pdf'
EXAM='https://ibpublishing.ibo.org/exinst/apps/exinst/index.html?chapter=1&doc=EX_instructions_2027_e&part=11'
TOPICS=[]
def add(code,title,sl_end,total,shared,ahl='',limits='',skills='',pages=''):
    TOPICS.append({'code':code,'title':title,'theme':code[0],
        'slStatements':f'{code}.1-{sl_end}' if sl_end else None,
        'additionalHlStatements':f'{code}.{sl_end+1}-{total}' if total>sl_end else None,
        'additionalHlOnly':sl_end==0,
        'sharedConcepts':shared.split('|') if shared else [],
        'additionalHlConcepts':ahl.split('|') if ahl else [],
        'limitsAndExclusions':limits.split('|') if limits else [],
        'dataAndExperimentalSkills':skills.split('|') if skills else [],
        'guidePrintedPages':pages,'sourceUrls':[GUIDE]})

add('A1.1','Water',6,8,
    'Aqueous origin and medium of life|Water polarity and intermolecular hydrogen bonding|Cohesion, xylem tension and surface habitats|Adhesion and capillary action|Solvent roles in transport and metabolism|Buoyancy, viscosity, thermal conductivity and specific heat: aquatic versus aerial habitats',
    'Asteroid delivery of water; retention through gravity and condensation|Liquid water, habitable orbital zone and search for extraterrestrial life',
    'Origin hypotheses restricted to asteroids; retention restricted to gravity and temperatures allowing condensation|Named organism common or scientific names acceptable',
    'Represent partial charges and hydrogen bonds between water molecules|Compare physical-property data with biological adaptations', '34-35')
add('A1.2','Nucleic acids',10,15,
    'DNA inheritance in living organisms|Nucleotide components; schematic phosphate, pentose and base|Covalent sugar-phosphate chain|DNA/RNA bases|RNA condensation polymer|Antiparallel complementary DNA strands and hydrogen bonds|DNA/RNA strand, base and sugar differences|Complementarity in copying and expression|Sequence diversity and information capacity|Near-universal genetic code as ancestry evidence',
    '5-prime/3-prime direction and linkages|Purine-pyrimidine pairs and uniform helix width|Nucleosomes: eight core histones, DNA and linker histone|Hershey-Chase evidence|Chargaff data and falsification of a repeating tetranucleotide model',
    'SL: do not require recall of purine/pyrimidine lengths or hydrogen-bond numbers|DNA drawing need not be helical|No memorized example of genetic-code conservation required',
    'Nucleotide/RNA/DNA diagrams|Ribose versus deoxyribose sketch|HL molecular visualization of nucleosomes|Evaluate tracer and base-composition evidence','35-38')
add('A2.1','Origins of cells',0,9,'',
    'Early atmospheric conditions and abiotic carbon chemistry|Self-sustaining cellular life versus viruses|Catalysis, replication, assembly and compartmentalization as prerequisites|Miller-Urey evaluation|Fatty-acid vesicles|RNA-world hypothesis and ribozymes|Shared code/genes and LUCA|Evidence used to date early cells/LUCA|Hydrothermal-vent fossil and genomic evidence',
    'Entire subtopic AHL|Distinguish plausible hypotheses from proof; laboratory synthesis of organics is not creation of life',
    'Experimental controls and contamination|Evaluate model atmosphere and geological evidence|Distinguish first life from last common ancestor','38-39')
add('A2.2','Cell structure',11,14,
    'Cell theory|Light microscopy preparation, calibration and measurement|Electron microscopy, freeze fracture, cryo-EM and fluorescence|Common cellular features|Gram-positive bacterial organization|Eukaryotic compartments and cytoskeleton|Functions of unicellular life|Animal/fungal/plant differences|Atypical nuclear number|Cell/structure recognition|Annotated biological drawings',
    'Endosymbiotic origins and evidence|Differentiation through altered expression|Repeated origins and advantages of multicellularity',
    'Bacterial model: Gram-positive eubacteria; detailed unusual prokaryotic variations excluded|Do not present generated artwork as a micrograph|Atypical examples: aseptate hyphae, skeletal muscle, erythrocytes, sieve-tube elements',
    'Magnification and actual-size conversion|Eyepiece calibration and scale bars|Microscopy methods and resolution|Recognition/drawing from legitimate micrographs or explicitly labelled schematics','39-41')
add('A2.3','Viruses',0,6,'',
    'Acellular organization, nucleic acid and capsid|DNA/RNA and envelope diversity|Lambda lytic cycle|Lambda lysogenic cycle|Multiple origins and convergent parasitism hypotheses|Rapid evolution in influenza and HIV',
    'Entire subtopic AHL|Examples: lambda phage, coronaviruses and HIV; rapid-evolution examples influenza and HIV|Do not imply all viruses contain both RNA and DNA or all are enveloped',
    'Interpret infection-cycle diagrams, time-series and selection evidence','41-42')
add('A3.1','Diversity of organisms',11,15,
    'Organism diversity and variation|Binomial naming|Species concepts and gradual divergence|Chromosome-number diversity|Karyograms and human chromosome-2 fusion evidence|Genome variation within and between species|Genome size versus complexity|Genome sequencing applications and changing cost',
    'Asexual reproduction/horizontal transfer challenges to species concept|Chromosome-number compatibility in hybrid fertility|Dichotomous keys|Environmental DNA barcoding',
    'Recall chromosome counts only humans46/chimpanzees48; supply others|Dichotomous keys and eDNA are AHL|Simple limitations of species concept can be shared; asexual/HGT detail is AHL',
    'Classify chromosomes by length, banding and centromere|Extract genome-size data|Construct keys and interpret eDNA at HL','42-44')
add('A3.2','Classification and cladistics',0,9,'',
    'Classification purposes and ranked-taxonomy limitations|Evolutionary classification and clades|Molecular sequence evidence|Molecular clocks and uncertainty|Cladogram construction/parsimony|Root, nodes, terminal branches and relationships|Reclassification with new evidence|Three domains from rRNA evidence',
    'Entire subtopic AHL|Reclassification case-study details need not be memorized|Cladogram branch length represents time/change only when explicitly defined',
    'Sequence comparisons|Cladogram reading and simple construction|Evaluate molecular-clock assumptions','44-45')
add('A4.1','Evolution and speciation',7,11,
    'Population-level heritable change|Sequence evidence|Domestication as evidence|Homology including pentadactyl limbs|Analogy and convergence|Splitting species versus gradual within-lineage change|Reproductive isolation and differential selection, including Congo-separated Pan populations',
    'Allopatric/sympatric and geographic/behavioural/temporal isolation|Adaptive radiation|Prezygotic barriers and hybrid sterility|Hybridization/polyploidy in plant speciation, including Persicaria',
    'SL can assess geographical reproductive isolation; named modes and broader mechanisms AHL|Acquired non-heritable individual change is not population evolution',
    'Compare sequence and anatomical evidence|Interpret constructed population/isolation data','45-47')
add('A4.2','Conservation of biodiversity',8,8,
    'Genetic, species and ecosystem diversity|Limits of species-number estimates|Anthropogenic extinction|Anthropogenic ecosystem loss|Repeated survey evidence and citizen science|Population growth, overuse, habitat loss, pollution and introduced species|Complementary in situ/ex situ measures and germplasm storage|EDGE prioritization',
    '', 'All shared|Corrected extinction cases: North Island giant moa; Caribbean monk seal; another locally or regionally relevant extinct species|Ecosystem case: Southeast Asian mixed dipterocarp forest plus another relevant loss|Historical non-human mass-extinction mechanisms outside this subtopic',
    'Richness/evenness from data|Sampling-effort controls and repeated surveys|Evaluate conservation tradeoffs and methodological bias','47-48')

add('B1.1','Carbohydrates and lipids',13,13,
    'Carbon bonding and molecular diversity|Condensation/hydrolysis|Pentoses/hexoses and glucose properties|Starch/glycogen storage|Cellulose structure|ABO glycoprotein recognition|Lipid hydrophobicity|Triglyceride/phospholipid formation|Saturated and unsaturated fatty acids|Adipose storage/insulation|Amphipathic bilayers|Steroid permeability',
    '', 'All shared|Steroid examples oestradiol and testosterone|Lipids are not polymers of identical repeated monomers',
    'Recognize sugar rings and steroid structures|Draw/interpret molecular models|Use metric prefixes','48-50')
add('B1.2','Proteins',5,12,
    'General amino acid|Peptide condensation|Essential/nonessential dietary amino acids|Sequence diversity|Temperature/pH denaturation',
    'R-group chemistry|Primary structure and folding|Alpha helices/beta sheets|Tertiary interactions|Hydrophobic/polar positioning|Quaternary and conjugated proteins|Globular/fibrous form-function',
    'No named essential/nonessential amino acids required|No named R-groups required except cysteine for disulfides|Examples: insulin, collagen and haemoglobin',
    'Draw amino acid/dipeptide|Interpret denaturation results|Reason from molecular environment','50-52')
add('B2.1','Membranes and membrane transport',10,17,
    'Amphipathic bilayer assembly and barrier|Simple diffusion|Integral/peripheral proteins|Osmosis and aquaporins|Channels and facilitated diffusion|ATP-driven pumps|Selective permeability|Extracellular glycoproteins/glycolipids|Fluid mosaic drawing including cholesterol',
    'Fatty acids and fluidity|Temperature-dependent cholesterol effects|Endocytosis/exocytosis|Ligand/voltage-gated channels|Na/K exchange pumps|Na-dependent glucose cotransport|Cell-adhesion molecules',
    'No detailed catalog of CAMs or cell junctions required|Cholesterol presence in SL model does not make detailed fluidity modulation SL',
    'Label membrane regions|Interpret transport/fluidity experiments|Distinguish direct from indirect ATP dependence','52-54')
add('B2.2','Organelles and compartmentalization',3,9,
    'Organelles and fractionation|Nucleus separates transcription from translation and permits RNA processing|Concentrated reactants/enzymes and separated incompatible reactions; lysosomes/phagocytic vacuoles',
    'Mitochondrial cristae, matrix and intermembrane space|Chloroplast thylakoids/stroma|Nuclear envelope/pores and division|Free versus bound ribosomes/RER|Golgi processing/secretion|Vesicles and clathrin',
    'SL RNA-processing advantage does not require HL molecular splicing detail|Golgi restricted to processing/secretion|Guide treats ribosomes and plasma membrane as organelles; cytoplasm, wall and cytoskeleton are not organelles in its convention',
    'Interpret fractionation or labelled compartment diagrams|Link ultrastructure to process location','54-55')
add('B2.3','Cell specialization',6,10,
    'Embryonic differentiation and gradients|Stem-cell self-renewal/differentiation|Adult niches|Toti/pluri/multipotency|Specialized cell-size range|Surface-area:volume scaling',
    'Flattening, microvilli and invagination|TypeI/typeII pneumocytes|Cardiac and skeletal muscle comparison|Human gamete adaptations',
    'Adult niches: two examples enough|Gamete adaptations limited to humans|Pneumocytes: thin typeI and surfactant secretory vesicles in typeII',
    'Cubic size/area/volume models and limitations|Compare cell dimensions and microstructure','55-56')
add('B3.1','Gas exchange',10,13,
    'Size and exchange constraints|Permeable thin moist large surfaces|Ventilation/perfusion gradients|Mammalian alveoli/surfactant|Ventilation muscles|Lung volumes|Leaf tissues and exchange|Dicot leaf plan|Transpiration|Stomatal density',
    'Foetal/adult haemoglobin and cooperative binding|Bohr effect|Oxygen dissociation curves',
    'Lungs restricted to mammalian alveolar model|Leaf transverse sections: dicot|Detailed Hb affinity mechanisms AHL',
    'Tidal/vital/reserve volume measurements|Leaf plan drawings|Stomatal counts and replication|HL dissociation-curve analysis','56-58')
add('B3.2','Transport',10,18,
    'Capillary exchange adaptations|Artery/vein structure|Arterial pressure|Pulse|Venous return|Coronary occlusion and epidemiology|Transpiration cohesion-tension|Xylem structure|Dicot stem/root plans',
    'Tissue-fluid formation/return|Lymphatic return|Single/double circulation|Heart architecture: cardiac muscle, sinoatrial pacemaker, atria, ventricles, valves, septum and coronary vessels|Cardiac cycle initiated by sinoatrial node; pressure data|Root pressure|Phloem/companion-cell adaptations',
    'Vascular tissue plans refer to dicots|Correlation cannot establish a dietary cause of coronary disease|General transpiration tension is shared; water-potential calculations are D2.3 AHL',
    'Vessel recognition|Pulse and epidemiological data|Plant tissue plans|HL systolic/diastolic graphs and circulation tracing','58-60')
add('B3.3','Muscle and motility',0,10,'',
    'Movement in motile/sessile organisms|Sliding filaments|Titin and antagonists|Motor units|Skeleton leverage|Hip joint|Joint range|Intercostal antagonists|Locomotion purposes|Marine-mammal swimming adaptations',
    'Entire subtopic AHL|Hip bones femur/pelvis required; individual muscle/ligament names not required',
    'Sarcomere diagrams|Measure joint angles/range with images or goniometer|Compare locomotor adaptations','60-61')
add('B4.1','Adaptation to environment',8,8,
    'Habitat|Abiotic adaptations including dune grass/mangrove|Distribution and tolerance|Limiting factor|Coral-reef conditions|Temperature/rainfall biome distributions|Six terrestrial biomes|Named desert/rainforest adaptations',
    '', 'All shared|Biomes: tropical forest, temperate forest, taiga, grassland, tundra, hot desert|Coral factors: depth,pH,salinity,clarity,temperature',
    'Transects with abiotic measurements|Interpret tolerance and biome graphs','61-62')
add('B4.2','Ecological niches',13,13,
    'Biotic/abiotic niche|Oxygen tolerance groups|Photoautotrophy|Holozoic nutrition|Mixotrophy|Saprotrophy|Archaeal nutritional diversity|Hominid teeth and diet|Herbivory and plant defence|Predator/prey adaptations|Forest light strategies|Fundamental/realized niche|Competitive exclusion',
    '', 'All shared|Corrected archaea statement: no named examples required|No detailed prokaryotic photosynthesis pathways|Oxygen groups limited to tolerance of presence/absence',
    'Infer diet from model/digital skulls|Interpret exclusion experiments and niche distributions','62-64')

add('C1.1','Enzymes and metabolism',10,17,
    'Catalysis and metabolic networks|Anabolic/catabolic examples|Globular active sites|Induced fit|Motion and collisions|Specificity/denaturation|Temperature,pH,substrate effects|Rate measurements|Activation-energy profiles',
    'Intracellular/extracellular reactions|Metabolic heat|Linear/cyclic pathways|Allosteric noncompetitive inhibition|Competitive inhibition/statins|Isoleucine feedback|Irreversible mechanism-based inhibition/penicillin',
    'Do not classify competition/allostery as SL merely because graphs are supplied unless all required information is given as a novel context',
    'Rates from initial slopes/experiments|Interpret limiting-substrate and activation-energy graphs|Controls and uncertainty','64-66')
add('C1.2','Cell respiration',6,17,
    'ATP energy transfer and uses|ATP/ADP interconversion|Respiration as ATP-producing carbon-compound breakdown|Aerobic/anaerobic comparison|Variables affecting respiration|Respiration-rate measurement',
    'NAD redox|Glycolysis|Lactate and ethanol NAD regeneration|Link reaction|Krebs cycle|Reduced-NAD electron transfer|Proton gradient and chemiosmosis|Oxygen terminal acceptor|Lipid/carbohydrate substrates',
    'No names of glycolytic intermediates|Krebs intermediate names only citrate/oxaloacetate|No ETC complex names|Avoid universal fixed aerobic ATP yield',
    'Respirometry and rate data|Control temperature/mass|Interpret oxygen/CO2 and inhibitor data','66-69')
add('C1.3','Photosynthesis',8,19,
    'Light-to-chemical energy|CO2 to carbohydrates, water source of hydrogen|Water-derived oxygen|Pigment chromatography|Absorption spectra|Absorption/action comparison|Limiting-factor experiments|Greenhouse/FACE experiments',
    'Photosystems and pigment arrays|PSII photolysis|Cyclic/noncyclic chemiosmosis|PSI and NADP reduction|Thylakoid process locations|Rubisco/RuBP/GP|TP production|RuBP regeneration|Product biosynthesis|Light/Calvin interdependence',
    'Paper or thin-layer chromatography acceptable|Calvin intermediates RuBP,GP,TP required; no individual regeneration reactions|No downstream biosynthetic pathway details',
    'Rf calculation|Absorption/action graphs|O2/CO2 rates|Experimental limiting-factor and FACE evaluation','69-72')
add('C2.1','Chemical signalling',0,14,'',
    'Ligands and specific receptors|Quorum sensing/Vibrio fischeri|Hormones,transmitters,cytokines,Ca|Chemical classes and signal ranges|Membrane/intracellular receptors|Signal transduction|Acetylcholine ion channels|G-protein receptors|Adrenaline/cAMP|Tyrosine kinase receptors|Intracellular transcription regulation|Oestradiol/progesterone targets|Positive/negative feedback',
    'Entire subtopic AHL|Oestradiol example limited to hypothalamic GnRH cells; progesterone to endometrium|One positive and one negative feedback example sufficient|Scientific precision note: guide C2.1.4 appears to misname gaseous nitric oxide as nitrous oxide; do not reproduce that nomenclature error',
    'Interpret receptor/pathway diagrams and intervention experiments','72-73')
add('C2.2','Neural signalling',7,16,
    'Neuron organization|Resting potential and Na/K pumping|Propagated action potentials|Speed differences by axon size/myelination|Chemical synapse direction|Ca-triggered transmitter release|Excitatory acetylcholine response',
    'Voltage-gated depolarization/repolarization|Local currents|Oscilloscope traces|Saltatory conduction|Neonicotinoids/cocaine|Inhibition/hyperpolarization|Summation|Pain receptors|Emergent consciousness',
    'Chemical rather than electrical synapses|SL knows action potentials exist, not detailed channel sequence|Trace-event interpretation is AHL',
    'Shared r and R-squared interpretation|HL pulse frequency and membrane-potential traces','73-75')
add('C3.1','Integration of body systems',16,23,
    'System hierarchy/emergence|Nervous,endocrine and transport integration|Brain/spinal cord|Sensory/motor pathways and nerves|Pain reflex|Cerebellum|Melatonin/circadian rhythms|Adrenaline|Hypothalamus/pituitary|Heart-rate baro/chemoreceptor feedback|Ventilation feedback|CNS/ENS control of digestion',
    'Seedling tropisms|Shoot phototropism|Phytohormones|Auxin efflux|Acid growth|Auxin/cytokinin coordination|Ethylene positive feedback',
    'No detailed slow-transmitter learning mechanisms|No anterior/posterior pituitary mechanism comparison|Peristalsis: voluntary entry/exit versus involuntary ENS|No specific other tropisms required',
    'Nerve cross-sections/reflex diagrams|Feedback evidence|HL seedling angle data, precision and controls','75-78')
add('C3.2','Defence against disease',18,18,
    'Pathogens|Skin/mucosal barriers|Clotting|Innate/adaptive contrast|Phagocytosis|Lymphocytes/antigens|Helper-T activation of B cells|Plasma-cell clones|Memory|HIV|Antibiotic selectivity/resistance|Zoonoses|Vaccination|Herd immunity|COVID data',
    '', 'All shared|No skin diagram required|Innate components beyond phagocytes not required|Clotting limited to platelets,factors,thrombin,fibrinogen/fibrin and trapping erythrocytes|Do not treat antibiotic resistance as directed mutation',
    'Percentage change versus percentage difference|Evaluate infection/vaccine data and confounding|Medical contexts educational, not treatment advice','78-80')
add('C4.1','Populations and communities',18,18,
    'Populations and reproductive interaction|Random sampling|Quadrats|Capture-mark-recapture/Lincoln index|Carrying capacity|Density feedback and growth|Communities and species interactions|Competition/predation/mutualism/parasitism|Interspecific competition|Chi-square association|Predator-prey regulation|Top-down/bottom-up control|Allelopathy/antibiotics',
    '', 'All shared|SD formula memorization not required|Association does not prove interaction or causation|CMR assumptions must be explicit and evaluated',
    'Quadrat estimates and spread|Lincoln calculation|Growth/predator-prey graphs|2x2 species-association chi-square','80-83')
add('C4.2','Transfers of energy and matter',22,22,
    'Open ecosystems|Sunlight and exceptions|Food-chain energy|Food webs|Decomposers|Autotrophy/photo/chemo|Heterotrophy|Respiration and carbon balance|Trophic levels and energy losses|Energy pyramids and efficiency|Primary/secondary production|Carbon fluxes and reservoirs|Carbon cycle and decomposition|Recycling elements',
    '', 'All shared|Detailed nitrogen and other nutrient cycles not required|Food-web arrows point in direction of energy/biomass transfer|Energy flows; matter cycles',
    'Food webs and energy pyramids|Transfer-efficiency and productivity calculations|Carbon budgets and flux diagrams','83-85')

add('D1.1','DNA replication',5,9,
    'Replication purposes|Semiconservative copying/complementarity|Helicase/general polymerase|PCR primers,Taq,temperature cycles|Gel separation and profiling',
    '5-prime/3-prime polymerization|Leading/lagging and primers|Primase,polI,polIII,ligase|PolIII proofreading',
    'Detailed enzyme system restricted to prokaryotes|Shared PCR does include primers despite replication primase detail being AHL',
    'DNA profile/gel interpretation|PCR cycle reasoning|Evaluate false-match probability and markers','85-86')
add('D1.2','Protein synthesis',11,19,
    'Transcription/RNA polymerase|Template pairing and stability|Gene expression switching|Translation|mRNA/ribosomes/tRNA|Codon/anticodon|Triplet,degenerate,universal code|Codon-table use|Elongation and peptide bonding|Point mutation effects',
    'Directionality|Promoters/transcription factors|Noncoding DNA|RNA splicing,cap,polyA|Alternative splicing|Translation initiation/A-P-E sites|Polypeptide maturation/preproinsulin|Proteasomes',
    'SL focus elongation rather than initiation/termination|No named transcription factors|Noncoding examples regulators,introns,telomeres,rRNA/tRNA genes|No specific alternative-splicing example required',
    'Codon translation and mutation comparison|RNA-processing diagrams|Preproinsulin maturation','86-88')
add('D1.3','Mutation and gene editing',7,10,
    'Substitution,insertion,deletion|SNP and genetic-code redundancy|Frameshift consequences|Mutagens/replication-repair errors|Mutation randomness|Germline/somatic consequences|Mutation as original variation source',
    'Knockout experiments|CRISPR-Cas9 editing|Conserved-sequence hypotheses',
    'No detailed knockout techniques|No native prokaryotic CRISPR role required|One successful editing example required|Do not assume every substitution alters phenotype',
    'Sequence alignment|Evaluate knockout inference,controls and ethical limitations','88-90')
add('D2.1','Cell and nuclear division',11,17,
    'Cell division|Cytokinesis in animals/plants|Unequal division|Mitosis/meiosis roles|Predivision replication|Condensation/microtubules|Mitosis phases and recognition|Meiotic reduction|Nondisjunction/Down syndrome|Random orientation/crossing-over',
    'Proliferation contexts|G1/S/G2 and cycle|Interphase biosynthesis|Cyclin thresholds/checkpoints|Oncogene/tumour-suppressor mutations|Benign/malignant,invasion/metastasis and mitotic index',
    'No individual cyclin role details|Skin structure not required|Shared chromosome counts are distinct from AHL cell-cycle regulation',
    'Mitosis recognition from drawings or genuine images|Meiotic chromosome tracking|HL mitotic-index calculation','90-92')
add('D2.2','Gene expression',0,11,'',
    'Expression and phenotype|Promoters/enhancers/factors|mRNA lifetime|Differentiation/epigenesis|Genome,transcriptome,proteome|DNA/histone methylation|Epigenetic inheritance|Environmental effects|Gametic reset/imprinting and hybrids|Twin studies|Hormone and bacterial biochemical regulation',
    'Entire subtopic AHL|No molecular detail for histone-methylation effects|Epigenetic changes need not change DNA sequence|Twin comparison limited to environmental expression effects|One hormone and one bacterial biochemical example',
    'Expression data and controls|Twin-study confounding|Interpret methylation/transcription relationships','92-93')
add('D2.3','Water potential',7,11,
    'Solvation|Hypo/hyper/isotonic solutions|Osmotic cell movement|Plant tissue mass/length changes|Animal-cell swelling/crenation|Turgor/plasmolysis|Isotonic medical fluids',
    'Potential-energy definition|Higher-to-lower potential|Solute+pressure components|Plant tissue response via potentials',
    'SL use solute concentration for direction, not water concentration|SD/SE formula memorization not required|Reference pure water at atmospheric pressure and20C; kPa|Pressure generally positive in cells but xylem tension negative',
    'Percentage mass/length changes,isotonic interpolation|SD/SE/error bars|HL psi_w=psi_s+psi_p','93-95')
add('D3.1','Reproduction',12,20,
    'Sexual/asexual tradeoffs|Meiosis/fertilization|Gamete differences|Human reproductive anatomy|Menstrual hormones/feedback|Human fertilization|IVF hormones|Flowering-plant sex|Insect flower|Cross-pollination|Self-incompatibility|Seed dispersal/germination',
    'Puberty endocrine pathway|Gametogenesis|Acrosomal/cortical reactions|Blastocyst/implantation|hCG tests|Placenta|Pregnancy/childbirth hormones|HRT evidence/confounding',
    'No embryonic stage names beyond blastocyst required|Placental structural detail restricted to villous exchange area|Use precise male-typical/female-typical anatomy wording without assuming all individuals identical',
    'Reproductive anatomy/flower diagrams|Hormone cycles|Evaluate observational versus randomized evidence','95-97')
add('D3.2','Inheritance',15,21,
    'Haploid gametes/diploid inheritance|Plant crosses|Genotype/phenotype|Dominance|Plasticity|PKU|SNP/multiple alleles|ABO|Incomplete/codominance|Sex chromosomes|Haemophilia|Pedigrees|Continuous/polygenic variation|Box plots/outliers',
    'Independent assortment/unlinked genes|Dihybrid grids|Genomic loci|Linkage|Recombinants|Genetic chi-square tests',
    'AHL dihybrids restricted to two unlinked autosomal genes for standard ratios|Linked alleles should be shown on homologous chromosome lines|ABO alleles I^A,I^B,i|X-linked alleles superscript on X',
    'Pedigrees/monohybrids|1.5IQR outlier rule|HL testcross and p=.05 chi-square','97-100')
add('D3.3','Homeostasis',6,11,
    'Regulated internal variables|Negative feedback|Insulin/glucagon|Type1/type2 diabetes|Thermoregulatory sensors,hypothalamus,thyroxin|Human heat-loss/production mechanisms',
    'Kidney excretion/osmoregulation|Ultrafiltration and proximal reabsorption|Loop of Henle|ADH/aquaporin collecting-duct regulation|Activity-dependent blood redistribution',
    'Thermoregulatory mechanism detail humans only|Loop of Henle limited to ascending Na transport and medullary gradient facilitating collecting-duct reabsorption|Educational physiology; no individualized diagnosis/treatment',
    'Feedback and glucose curves|HL renal concentration/flow interpretation','100-102')
add('D4.1','Natural selection',8,15,
    'Selection and paradigm shift|Mutation/sexual variation|Overproduction/competition|Abiotic selection|Fitness and differential reproduction|Heritability|Sexual selection|Endler guppy experiments',
    'Gene pools|Allele frequencies|Neo-Darwinian selection|Directional,disruptive,stabilizing selection|Hardy-Weinberg calculation/conditions|Deliberate artificial selection',
    'Unintended antibiotic resistance is natural selection, not artificial selection|Shared domestication evidence in A4.1 differs from AHL detailed D4.1 selection treatment',
    'Experimental-selection interpretation|HL p+q=1 and p²+2pq+q²=1|Human allele-frequency database example','102-103')
add('D4.2','Stability and change',11,15,
    'Dynamic ecosystem stability|Energy,nutrients,diversity and climatic tolerance|Amazon tipping risk|Mesocosms|Keystone species|Sustainable harvest|Agriculture impacts|Eutrophication/BOD|Biomagnification|Plastics|Rewilding',
    'Succession causes|Primary succession trends|Cyclical succession|Climax/arrested succession',
    'Rewilding example Hinewai Reserve|Harvest examples one terrestrial plant and one marine fish|Biomagnification examples DDT/mercury|Closed mesocosm still exchanges energy',
    'Percentage habitat change|Sustainable harvest budgets|Mesocosm controls|HL succession sequences','103-105')
add('D4.3','Climate change',8,12,
    'Anthropogenic CO2/methane|Positive feedbacks|Boreal carbon tipping|Polar ice habitat|Ocean upwelling|Poleward/upslope ranges|Coral acidification/bleaching|Carbon sequestration',
    'Phenology cues|Phenological mismatch|Insect generations|Evolution under changed climate',
    'Anthropogenic drivers restricted to CO2/methane|Corrected .1 NOS paragraph removed; .8 NOS label removed|Examples: emperor penguin,walrus,New Guinea birds,North American trees; HL Arctic chickweed/reindeer and great tit/caterpillars,spruce bark beetle,tawny owl',
    'Interpret climate/range time series and uncertainty|Distinguish ecological redistribution from heritable evolution','105-107')

assert len(TOPICS)==40 and len({x['code'] for x in TOPICS})==40
blueprint={
    'subject':'biology','firstAssessment':2025,'verifiedOn':'2026-10-30',
    'guideVersion':'Published February2023; May2023 and March2024 updates; current2027 examiner instructions link this version',
    'primarySources':[{'url':GUIDE,'role':'Corrected official guide','pdfPages':133}, {'url':EXAM,'role':'Current official examiner instructions identify version'}],
    'accessNote':'Official indexed PDF was accessed through its link from the2027 examiner instructions. Direct-download challenge was not bypassed. No third-party question-bank text or images used.',
    'themes':[{'code':'A','title':'Unity and diversity','topicId':'unity-diversity','questions':144}, {'code':'B','title':'Form and function','topicId':'form-function','questions':160}, {'code':'C','title':'Interaction and interdependence','topicId':'interaction-interdependence','questions':144}, {'code':'D','title':'Continuity and change','topicId':'continuity-change','questions':192}],
    'levelPolicy':'sl means shared SL/HL material; ahl means a response actually requires additional higher-level understanding. Difficulty alone never changes tier.',
    'assessment':{'calculatorAllPapers':True,'sourcePages':'110-113',
        'sl':{'paper1':{'minutes':90,'marks':55,'paper1A':30,'paper1B':25,'weightPercent':36},'paper2':{'minutes':90,'marks':50,'sectionA':34,'sectionB':16,'extendedChoice':'one of two','weightPercent':44}},
        'hl':{'paper1':{'minutes':120,'marks':75,'paper1A':40,'paper1B':35,'weightPercent':36},'paper2':{'minutes':150,'marks':80,'sectionA':48,'sectionB':32,'extendedChoice':'two of three','weightPercent':44}},
        'paper1B':'Four syllabus-related data questions across the themes; 1A and1B completed together without interruption',
        'mcq':'One mark each, no deduction for a wrong response',
        'internal':{'marks':24,'weightPercent':20,'hours':10},
        'bookletNote':'Do not invent a Biology data-booklet entitlement; provide any formula, table or reference data needed by original practice questions.'},
    'markingPolicy':['Use original analytic mark points and explicit acceptable alternatives where appropriate.','Separate calculation method, result and biological reasoning when separately assessed.','Our A/M/R codes are portal authoring conventions, not claims of official IB markscheme notation.','Use command terms consistently; explain requires causal reasoning, evaluate requires limitations/strengths, compare requires paired statements.','Data must be sufficient to justify the awarded answer; uncertainty and causal limitations must not be suppressed.'],
    'commandTermIntent':{'state':'brief fact/value','outline':'brief account','describe':'detailed observations or account','explain':'account with mechanisms or causes','calculate':'numerical result with working','compare':'paired similarities','compare and contrast':'paired similarities and differences','deduce':'conclusion from supplied evidence','evaluate':'weigh strengths and limitations','discuss':'balanced supported review','suggest':'plausible proposal','design':'workable method or model','draw':'accurate labelled representation','sketch':'labelled essential shape and features'},
    'authoringRules':['All question wording and markschemes must be original.','Label constructed/simulated datasets explicitly.','Generated images are schematics, never claimed real micrographs or observations.','Use intact axes, units, scale bars and direction labels; do not reveal the tested answer through a caption.','Do not infer statistical significance only from overlapping or non-overlapping unspecified error bars.','Supply critical values and assumptions when asking statistical tests.','Use reliable biology even where a guide simplification or apparent typo could mislead.'],
    'topics':TOPICS}
dest=ROOT/'docs/ib-biology-reviews';dest.mkdir(parents=True,exist_ok=True)
(dest/'syllabus-blueprint.json').write_text(json.dumps(blueprint,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'topics':len(TOPICS),'whollyAhl':[x['code'] for x in TOPICS if x['additionalHlOnly']]}))
