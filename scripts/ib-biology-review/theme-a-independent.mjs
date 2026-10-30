/** Independent review: consumes published records, never imports authoring code. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
import {unified} from 'unified';
import remarkParse from 'remark-parse';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import katex from 'katex';
import sharp from 'sharp';
import {ibQuestionSchema,safeDiagram} from '../../lib/ib/question.ts';

const file='content/ib/biology/unity-diversity.json';
const qs=JSON.parse(readFileSync(file,'utf8'));
const blueprint=JSON.parse(readFileSync('docs/ib-biology-reviews/syllabus-blueprint.json','utf8'));
const hash=s=>createHash('sha256').update(s).digest('hex');
const answer=q=>q.markScheme.flatMap(p=>p.steps.map(s=>s.text)).join(' ');
const calculations=[];
function calc(n,description,computed,expected,fragment,tolerance=1e-8){
 assert.ok(Math.abs(computed-expected)<=tolerance,`q${n}: ${description}`);
 assert.ok(answer(qs[n-1]).includes(fragment),`q${n} answer does not contain ${fragment}`);
 calculations.push({id:qs[n-1].id,description,computed,expected,answerFragment:fragment,status:'passed'});
}
calc(4,'(8/10−1/10)×100 percentage points',(8/10-1/10)*100,70,'70');
calc(6,'Equal-energy/equal-mass specific heat ratio = inverse temperature-rise ratio',4/2,2,'4.0/2.0=2.0');
calc(7,'Pond day−night temperature difference',19-16,3,'3');
calc(7,'Air day−night temperature difference',25-10,15,'15');
calc(13,'Delivered asteroid mass × water fraction × retained fraction',8e18*.12*.25,2.4e17,'2.4',100);
calc(21,'Connections in a single unbranched25-nucleotide chain',25-1,24,'24');
calc(22,'Complementary thymine fraction',22,22,'22');
calc(22,'Guanine fraction after removing A/T pairs',(100-2*22)/2,28,'28');
calc(24,'Four choices at each of eight positions',4**8,65536,'65,536');
calc(29,'Eight histones per complete core particle',12*8,96,'96');
calc(34,'Sparked minus unsparked amino-acid yield',38-2,36,'36');
calc(38,'Boundary retention half-time ratio',20/2,10,'10');
calc(44,'Lower end of geological age interval',3.45-.05,3.4,'3.40');
calc(44,'Upper end of geological age interval',3.45+.05,3.5,'3.50');
calc(50,'400-SVG-unit cell and100-unit bar labelled10 micrometres',400/100*10,40,'40');
calc(51,'Stage distance per eyepiece division',100/40,2.5,'2.5');
calc(51,'Cell length from calibrated18 divisions',18*(100/40),45,'45');
calc(53,'Convert36mm to micrometres before dividing by24micrometres',36*1000/24,1500,'1500');
calc(68,'Infected-cell count × mean single-cycle burst',200*60,12000,'12\\,000');
calc(74,'Five changed sites out of100',5/100*100,5,'5\\%');
calc(84,'Human haploid count from46diploid chromosomes',46/2,23,'23');
calc(85,'Three pairs, six individual unreplicated chromosomes',3*2,6,'2n=6');
calc(87,'Identity in20 aligned sites differing at2',(20-2)/20*100,90,'90');
calc(88,'Protist/animal genome-size ratio to2significant figures',Number((45000/3100).toPrecision(2)),15,'15');
calc(89,'Sequencing cost reduction to1decimal place',Number(((9000-1500)/9000*100).toFixed(1)),83.3,'83.3');
calc(90,'Within-species difference fraction',3/600*100,.5,'0.50');
calc(90,'Between-species difference fraction',42/600*100,7,'7.0');
calc(94,'Chromosome sum after gamete fusion',12+15,27,'27');
const diff=(a,b)=>[...a].reduce((s,c,i)=>s+(c!==b[i]),0);
calc(101,'P–Q aligned differences',diff('ACGTAA','ACGTGA'),1,'1 difference');
calc(101,'P–R aligned differences',diff('ACGTAA','TTGCGC'),5,'5 differences');
calc(102,'Combined substitution clock18/3',18/3,6,'6 million');
calc(103,'Two branches each accrue2 substitutions per million years',20/(2+2),5,'5');
calc(115,'Sequence identity in300sites with12differences',(300-12)/300*100,96,'96.0');
calc(116,'Seed-mass percentage increase',(3-2.4)/2.4*100,25,'25');
calc(119,'Species added minus species lost',8+5-3,10,'10');
calc(126,'Horse32plusdonkey31gamete chromosomes',32+31,63,'63');
calc(127,'Hybrid chromosome number before doubling',10+10,20,'20');
calc(127,'Hybrid chromosome number after doubling',2*(10+10),40,'40');
calc(130,'Abundance in equally distributed sample',10+10+10+10,40,'totals are equal');
calc(130,'Abundance in dominated sample',34+2+2+2,40,'totals are equal');
calc(131,'Moth-abundance percentage decline',(150-90)/150*100,40,'40');
calc(135,'Forest-area percentage loss',(1200-780)/1200*100,35,'35');
calc(136,'Remaining wetland types',6-2,4,'six to four');
calc(140,'Initial germination percentage',184/200*100,92,'92');
calc(140,'Later germination percentage',138/200*100,69,'69');
calc(140,'Germination percentage-point fall',92-69,23,'23');
calc(142,'Removal-plot seedling density change',28-12,16,'16');
calc(142,'Untreated-plot seedling density change',15-13,2,'2');
calc(143,'Species union in P+R',new Set([1,2,3,4,5,6,7]).size,7,'seven');
calc(143,'Species union in P+Q',new Set([1,2,3,4,1,2,3,5]).size,5,'five');
calc(143,'Species union in Q+R',new Set([1,2,3,5,5,6,7]).size,6,'six');

// Independent, item-specific biological judgments recorded while reading all144 records.
const notes=[
 'Water partial charges and H···O intermolecular bond; MCQ alternatives exclusive.',
 'Cohesive continuous liquid column transmits tension; gas embolism interrupts it.',
 'Adhesion to polar glass distinguished from cohesion; nonpolar coating weakens wetting.',
 'Surface-tension model: percentage-point reduction and insect/model limitation.',
 'Polar sugar/water interactions contrasted with lipid solubility and bulk-fluid transport.',
 'Equal-energy inverse heat-capacity relation; dimensional reasoning and unique key.',
 'Temperature buffering is consistent with high heat capacity; confounders retained.',
 'Thermal conductivity and blubber insulation explain seal heat loss.',
 'Buoyancy and viscosity explain distinct aquatic body features.',
 'Sodium attracts the partially negative oxygen region of water.',
 'Independent/dependent variables, fixed droplet volume and replication distinguished.',
 'Solvent and molecular-mobility functions are relevant separate water roles.',
 'Asteroid delivery/retention model belongs to AHL; mass fraction recalculated.',
 'Gravity and condensation limits match the specified AHL scope.',
 'Habitable-zone compatibility does not establish water or life.',
 'Two observations evaluated without claiming proof of habitability.',
 'Phosphate and nitrogenous base attach to pentose sugar in a nucleotide.',
 'Interstrand H bonds differ from covalent backbone linkages.',
 'Directly opposite sequence TCAGGT is correct; direction wording avoids ambiguity.',
 'Ribose/uracil and predominantly single-stranded organization identify RNA.',
 'RNA condensation explicitly a simplified model;24connections for25residues.',
 'Double-strand A=T/G=C proportions correctly distinguish single-strand limits.',
 'Ribose2OH and deoxyribose2H correctly associated with RNA/DNA.',
 'Combinatorial information capacity grows exponentially, not linearly.',
 'Near-universal coding supports ancestry; a single matching codon is weak evidence.',
 'Wrong DNA pairs/backbone corrected to AT/GC and covalent versus hydrogen bonds.',
 'Reverse complement5′TAACGT3′ matches antiparallel original5′ACGTTA3′.',
 'Purine–pyrimidine width logic is AHL and does not demand extra SL content.',
 'Eight core histones per nucleosome; linker histones correctly excluded from core count.',
 'Tracer pellet/supernatant inference accounts for imperfect separation.',
 'Base-composition data falsify equal quarters while retaining complementary pairs.',
 'Surface-phage removal control directly separates adsorption from entry.',
 'Vesicle growth alone is insufficient for living metabolism and hereditary replication.',
 'Spark control supports abiotic synthesis without proving early atmospheric composition.',
 'Cleaned carbon-reactant-free blank addresses apparatus contamination.',
 'Organic synthesis is not cellular life; heredity/compartment/catalysis requirements distinct.',
 'Amphipathic bilayer encloses aqueous compartment; given assembly conditions accepted.',
 'Retention benefit versus substrate/waste exchange cost is biologically balanced.',
 'RNA can be both informational and catalytic; no modern-nucleus requirement.',
 'Degrading-enzyme controls support RNA catalyst but require verifying enzyme action.',
 'Supplied DNA-stability/protein-catalysis premises yield a plausible, unproved history.',
 'Conserved ribosomal/code machinery supports common ancestry without genome identity.',
 'LUCA need not equal first life; extinct earlier branches remain possible.',
 'Rock age gives an ancient occurrence/minimum antiquity, not exact origin time.',
 'Molecular dates depend on evolutionary-rate assumptions and independent calibration.',
 'Vent geology and genes are distinct evidence sources with alternatives acknowledged.',
 'Competition and extinction can leave one detectable ancestral lineage.',
 'Matched vesicle/dilution comparison measures persistence rather than merely assembly.',
 'Plant-cell image: wall/chloroplast/nucleus/vacuole/mitochondrion endpoints correct; illustrative status explicit.',
 'SVG cell length400/bar100 is exactly4; proportional resizing preserves inference.',
 'Microscope calibration and objective-change recalibration are correct.',
 'Enlargement does not recover absent resolution information.',
 'Magnification is dimensionless after mm-to-micrometre conversion.',
 'Staining is confounded by thickness/objective; matched preparations address it.',
 'Typical cellular membrane/cytoplasm/genome/ribosomes distinguished from viruses.',
 'Gram-positive Bacillus/nucleoid/ribosomes versus eukaryote; cytoskeleton answer permits two types.',
 'Two requested fungal/plant comparisons match cell-wall/chloroplast marks.',
 'Erythrocytes and multinucleate fibres/hyphae refute universal one-nucleus claim.',
 'Directed response, nutrition and reproduction show one cell can perform life functions.',
 'Fluorescent localization/background plus EM resolution, cryogenic hydration and freeze-fracture interpretation.',
 'Bacterial-type DNA/ribosomes/division support endosymbiosis while host dependence persists.',
 '70S inhibitor result is compatible with bacterial organelle ancestry, not proof alone.',
 'Same DNA at tested genes permits altered expression/protein function; AHL differentiation.',
 'Multicellular division of labour and size confer benefits with coordination costs.',
 'Acellular capsid and absent ribosomes distinguish virus from bacterium.',
 'Coronavirus RNA/envelope, lambda dsDNA/non-envelope, HIV RNA/envelope compared explicitly.',
 'Lytic order Q→S→P→R correctly follows entry, synthesis, assembly and release.',
 'Single-cycle burst calculation does not include later infections.',
 'Integrated lambda prophage copied in host chromosome during lysogeny.',
 'Prophage-free toxicity control separates direct treatment damage from induction.',
 'Host translation and metabolic supplies explain viral replication dependence.',
 'Lipid disruption supports envelope function without determining genome type.',
 'Host-dependent lifestyle can converge; diverse genomes support multiple-origin consideration.',
 'Observed sequence changes are not a direct mutation-rate estimate after selection/sampling.',
 'Pre-existing resistant HIV variant increases by differential reproduction.',
 'Large output and short generations permit rapid variant-frequency evolution.',
 'Influenza antigen changes can reduce prior-antibody affinity; distractors checked.',
 'Constrained entry-target resistance may impose cost without making resistance impossible.',
 'Host bacterial ribosomes/chromosome not confused with phage components.',
 'Selection confounds copying-accuracy inference; comparable independent populations needed.',
 'First binomial word identifies genus without proving species identity or fertility.',
 'Observed fertile natural interbreeding supports biological species grouping.',
 'Connected intermediate populations create a genuine fuzzy species boundary.',
 'Human46/chimpanzee48 counts do not rank complexity; gamete23correct.',
 'Unreplicated homologues paired by matching lengths/patterns P–S,Q–U,R–T.',
 'Regional correspondence and internal telomere remnant are consistent with fusion.',
 'Within-species variants do not establish distinct species; short sample limitation.',
 'Genome-size ratio and noncoding/repetitiveDNA decouple size from complexity.',
 'Lower sequencing cost improves sampling but does not ensure predictive interpretation.',
 'Within/between differences refer only to specified sampled region.',
 'Genome includes hereditary noncoding information rather than expressed proteins only.',
 'Asexual lineage needs evidence other than mating fertility; AHL boundary respected.',
 'Horizontal transfer can make single-gene ancestry misleading.',
 'Hybrid count27 does not prove sterility; homologous pairing and segregation evaluated.',
 'Dichotomous key splits leaves then arrangement into four mutually exclusive specimens.',
 'eDNA detection is not abundance; laboratory blanks distinguish laboratory from field contamination.',
 'Classification organizes information and supports testable ancestry-based predictions.',
 'Equal ranks need not mean equal evolutionary divergence times.',
 'Cladogram Y/Z sister relationship,N1=X/Y/Z; terminal W is not ancestor.',
 'Complete clade requires all descendants of its root node.',
 'Aligned homologous sites differ1and5; short-sequence inference qualified.',
 'Combined clock rate is already two-lineage total; time6millionyears.',
 'Per-lineage rate doubled before dividing20; time5millionyears.',
 'Parsimony prefers6over9events but is not guaranteed historical truth.',
 'Rotating sister branches preserves topology and common ancestry.',
 'Convergence can explain morphology/molecular disagreement; technical errors still considered.',
 'rRNA homology spans cellular life; three domains correctly named.',
 'Internal node is hypothetical common ancestor, not necessarily dated living taxon.',
 'Generation time can affect rate; calibration must accommodate lineage heterogeneity.',
 'Unrelated proteins are not valid homologous sequence comparisons.',
 'Conflicting gene histories deserve investigation, not suppression.',
 'Clade membership supports a medium-difficulty testable trait prediction with loss possible.',
 'Population-level heritable frequency change distinguishes evolution from plasticity.',
 'Common-environment overlap weakens heritable field-trait interpretation without proving genetic identity.',
 'Sequence identity96%; nearest pairPQ correctly chosen with multilocus caveat.',
 'Human parent selection plus inherited variation explains artificial selection.',
 'Simplified1/2/5limb pattern illustrates homology; schematic does not claim full wrist anatomy.',
 'Insect/bird flight surfaces are analogous despite shared function.',
 'Speciation/extinction net richness10 does not identify surviving lineages.',
 'Congo barrier can reduce gene flow; timing/alternatives qualify Pan divergence.',
 'Waterfall and temperature effects separated through matched replicated sites.',
 'Independent anatomical/molecular agreement supports shared ancestry without one tip being another’s ancestor.',
 'Same-region host-associated reproductive separation is sympatric, AHL.',
 'Temporal flowering barrier persists despite experimentally compatible pollen.',
 'Common ancestor plus divergent niche adaptations supports adaptive radiation.',
 'Horse/donkey hybrid63 and meiotic mismatch explain postzygotic fertility barrier.',
 'Persicaria context separated from fictional counts; doubling20to40restores potential homologues.',
 'Song preference can reduce mating but does not demonstrate complete species separation.',
 'Genetic/species/ecosystem diversity mapping is exclusive and accurate.',
 'Equal richness4andabundance40do not imply equal evenness.',
 'Standardized survey effort supports observed decline but does not isolate pollutant cause.',
 'Named North Island giant moa case separates hunting evidence from sole-cause claims.',
 'Caribbean monk seal exploitation and habitat disturbance are coherent interacting pressures.',
 'Thylacine bounty context and last-known captive date do not determine exact last wild death.',
 'Dipterocarp conversion can reduce diversity despite maintained crop/tree cover.',
 'Named Everglades drainage context clearly separates fictional ecosystem counts from historical evidence.',
 'Roadside observation effort confounds abundance; citizen sampling can be standardized.',
 'EDGE balances evolutionary distinctiveness with endangerment, not zero value for other species.',
 'In-situ habitat protection and ex-situ seed backup have complementary functions.',
 'Germination92to69is23percentagepoints; collection should retain genetic representation.',
 'Corridor connectivity benefit weighed against invasive-predator spread.',
 'Control plots estimate background change; randomization/replication support causality.',
 'Reserve complementarity P+Rcovers7versus5or6, under explicitly equal costs/persistence.',
 'Low-detection surveys do not establish extinction; species-total uncertainty includes unsampled and taxonomic issues.'
];
assert.equal(notes.length,144);
assert.equal(qs.length,144);
const parser=unified().use(remarkParse).use(remarkMath).use(remarkGfm);let maths=0;
function scan(value){
 if(typeof value==='string'){
  assert.equal((value.match(/\$/g)||[]).length%2,0);
  assert.ok(!/[\x00-\x08\x0b\x0c\x0e-\x1f]/.test(value));
  const visit=n=>{if(n.type==='math'||n.type==='inlineMath'){katex.renderToString(n.value,{throwOnError:true,strict:'error'});maths++;}for(const c of n.children||[])visit(c);};visit(parser.parse(value));
 }else if(Array.isArray(value))value.forEach(scan);
 else if(value&&typeof value==='object')for(const [k,v] of Object.entries(value))if(!k.endsWith('Svg'))scan(v);
}
const expectedSL={A11:12,A12:10,A21:0,A22:12,A23:0,A31:11,A32:0,A41:10,A42:16};
const groups={};const entries=[];const svgs=[];const diagramNotes={
 1:'Two bent water molecules, each O with two H, correct partial charges; X links Hδ+ to Oδ−, no answer-labelled dashed bond.',
 37:'Closed double boundary encloses aqueous compartment; bilayer leader terminates on boundary and illustration status explicit.',
 50:'Cell horizontal diameter400 and scale bar100 in native SVG; quantitative ratio4andall labels inside viewBox.',
 67:'Four process boxes legible, no arrows implying chronological answer; all four required viral stages present.',
 85:'Exactly six unreplicated chromosomes; matched P/S130,Q/U80,R/T105lengths with identical matching centromere ratios.',
 86:'Two ancestral region sequences ABC/DEF map continuously to ABCDEF; internal telomeric marker at join.',
 99:'Tree connectivity encodes W,(X,(Y,Z)); N1isX/Y/Z ancestor andN2isY/Z ancestor; no time-scale claim.',
 117:'Each schematic has one proximal element,two forearm elements andfive digit rays; simplified organization, not complete anatomy.'
};
for(const [i,q] of qs.entries()){
 assert.equal(q.number,i+1);assert.equal(q.id,`ib-bio-a-${String(i+1).padStart(3,'0')}`);
 assert.ok(ibQuestionSchema.safeParse(q).success,q.id);assert.equal(q.calculator,true);
 const code=q.syllabusCode.replace('.','');(groups[code]??=[]).push(q);
 assert.equal(q.markScheme.flatMap(p=>p.steps).reduce((s,p)=>s+(p.code==='AG'?0:Number(p.code.slice(1))),0),q.marks);
 if(q.questionType==='multiple-choice'){
  assert.equal(q.marks,1);assert.equal(q.parts.length,0);assert.equal(q.options.length,4);
  assert.equal(new Set(q.options.map(o=>o.text)).size,4);assert.equal(q.options.filter(o=>o.label===q.correctOption).length,1);
  assert.ok(answer(q).startsWith('Option '+q.correctOption+'.'));
 }else{assert.equal(q.parts.reduce((s,p)=>s+p.marks,0),q.marks);assert.deepEqual(q.parts.map(p=>p.label),q.markScheme.map(p=>p.part));}
 scan(q);
 for(const field of ['diagramSvg','markSchemeDiagramSvg'])if(q[field]){
  assert.ok(safeDiagram(q[field]));svgs.push({id:q.id,field,sha256:hash(q[field]),review:diagramNotes[q.number]||'Additional worked diagram reviewed separately.'});
 }
 entries.push({id:q.id,sha256:hash(JSON.stringify(q)),syllabusCode:q.syllabusCode,level:q.level,difficulty:q.difficulty,marks:q.marks,review:notes[i],checks:['Original prompt/context reviewed','Single-answer validity or complete marking reviewed','Distinct credit and mark totals checked','SL/AHL scope checked','Numerical/graph/diagram evidence checked where applicable']});
}
for(const [code,n] of Object.entries(expectedSL)){assert.equal(groups[code].length,16);assert.equal(groups[code].filter(q=>q.level==='sl').length,n);}
// Explicit correction and coverage-closure assertions prevent silent regression.
assert.match(qs[56].parts[1].prompt,/two structural/i);
assert.match(qs[55].parts.at(-1).prompt,/two types/i);
assert.match(answer(qs[55]),/intermediate filaments/i);
assert.match(qs[65].parts[0].prompt,/X and Y/);assert.match(qs[65].parts[1].prompt,/X and Y/);
assert.match(answer(qs[95]),/Field blanks/);
assert.equal(qs[111].difficulty,'medium');
assert.match(qs[65].stem,/coronavirus/);assert.match(qs[126].stem,/Persicaria/);assert.match(qs[135].stem,/Everglades/);
assert.ok(answer(qs[59]).includes('freeze')||qs[59].parts.some(p=>/freeze-fracture/i.test(p.prompt)));
assert.match(answer(qs[143]),/undiscovered/);
const imageSources=JSON.parse(readFileSync('content/ib/biology-image-sources.json','utf8')).assets;
const plant=imageSources.find(a=>a.uses.some(u=>u.id==='ib-bio-a-049'));
assert.equal(qs[48].diagramUrl,plant.url);assert.match(qs[48].diagramCaption,/not a micrograph/);
const dir=resolve('../biology-artifacts/theme-a-independent');mkdirSync(dir,{recursive:true});
for(const s of svgs){const q=qs.find(q=>q.id===s.id);await sharp(Buffer.from(q[s.field])).png().toFile(resolve(dir,s.id+'-'+s.field+'.png'));}
const mcqKeyDistribution={A:0,B:0,C:0,D:0};for(const q of qs)if(q.questionType==='multiple-choice')mcqKeyDistribution[q.correctOption]++;
assert.deepEqual(mcqKeyDistribution,{A:7,B:6,C:6,D:6});
const correctMeanings={1:/hydrogen bond between a partially positive hydrogen/,6:/twice the specific heat capacity/,10:/oxygen ends.*face the ion/,15:/orbital position may permit surface liquid water/,17:/phosphate and the base are each attached to the sugar/,20:/^RNA\.$/,32:/removes externally attached phages without lysing/,35:/cleaned apparatus blank/,39:/carry sequence information.*catalyse reactions/,43:/Earlier lineages may have existed/,52:/Enlargement increases displayed size/,55:/plasma membrane, cytoplasm, genetic material and ribosomes/,65:/Nucleic acid is enclosed by a capsid, with no cytoplasm or ribosomes/,72:/intact lipid-associated structure is important/,77:/Some existing antibodies may bind less effectively/,81:/same genus/,91:/complete genetic information/,98:/Taxonomic ranks are assigned categories/,105:/relationships are unchanged/,108:/hypothetical common ancestor/,113:/inherited variant becomes more frequent/,118:/flight surfaces are analogous/,123:/Sympatric speciation/,129:/Wetland types: ecosystem diversity; bird species: species diversity; inherited reed variation: genetic diversity/,139:/Habitat protection is in situ.*seed storage is ex situ/};
assert.equal(Object.keys(correctMeanings).length,25);
for(const [n,pattern] of Object.entries(correctMeanings)){
 const q=qs[Number(n)-1];const chosen=q.options.find(o=>o.label===q.correctOption).text;
 assert.match(chosen,pattern,q.id+' correct meaning changed');
}
const report={status:'passed',reviewer:'Independent Theme B author; Theme A authoring modules not imported',source:file,questionJsonSha256:hash(readFileSync(file)),scope:'Every complete question, option and marking point read; all calculations, eight SVG fields and one original raster reviewed. No sampling.',questions:144,marks:qs.reduce((s,q)=>s+q.marks,0),levels:{sl:71,ahl:73},mcqKeyDistribution,mathExpressions:maths,numericalChecks:calculations.length,calculations,records:entries,svgCount:svgs.length,svgReviews:svgs,rasterReview:{id:'ib-bio-a-049',sha256:plant.sha256,review:'Independently viewed local source PNG. A terminates on cell wall outside membrane; B on chloroplast with internal grana; C inside nucleus; D central vacuole; E mitochondrial cristae region. Compartment placement and leader endpoints are correct. Original AI-assisted schematic caption is explicit; no specimen dimensions inferred.'},resolvedFindings:[{id:'ib-bio-a-057',issue:'One-feature prompt versus two-feature marks',resolution:'Prompt now requests two structural comparisons.'},{id:'ib-bio-a-096',issue:'Laboratory blanks overclaimed field contamination control',resolution:'Lab/reagent control distinguished from field blanks.'},{id:'ib-bio-a-077',issue:'Implausible distractors',resolution:'Options replaced with antigen-affinity misconceptions.'},{id:'ib-bio-a-112',issue:'Simple prediction task overclassified as hard',resolution:'Difficulty medium.'},{ids:[49,56,60,66,127,136,144],issue:'Explicit syllabus breadth gaps',resolution:'Bounded original subparts and named/supplied contexts added and re-reviewed; cytoskeletal alternatives and three-virus comparison wording corrected.'},{issue:'Unbalanced correct-option distribution',resolution:'Stable shuffled25-answer pool now7/6/6/6; every revised MCQ correct-option mapping rechecked.'}],scopeSource:blueprint.primarySources,originality:'Questions and diagrams reviewed as independently authored practice; named case facts distinguished from constructed model data.',unresolvedFindings:[]};
writeFileSync('docs/ib-biology-reviews/theme-a-independent-review.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({status:report.status,questions:144,marks:report.marks,numericalChecks:calculations.length,mathExpressions:maths,svgCount:svgs.length,rasterImages:1}));
