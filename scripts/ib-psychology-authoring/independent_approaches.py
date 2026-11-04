"""Bind an actual independent reading of BIO/COG 80 and 32 native/mobile figures.

The fixed reviewed hashes deliberately prevent this script from approving edits.
All interpretive observations below were written after the complete stems, IND
answers and best-fit rubrics were read. This is AI review, not examiner moderation.
"""
from pathlib import Path
import hashlib
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
REVIEWER = 'mock_pdf_inventory'
GUIDE = 'https://ibo.org/globalassets/new-structure/university-admission/pdfs/subject-guides/psychology-first-assessment-2027-guide-sbs.pdf'
REVIEWED_FILES = {
    'content/ib/psychology/biological-approach.json': 'a89a1991b93bdbc4f5eb3987d98ea16304b1d57a9f7c8b0689f9d331ed0f7e30',
    'content/ib/psychology/cognitive-approach.json': 'ce55f6f44eeb20683d3b6752701314aea9662251ffccac5c801a08920cbd0f68',
}

# One independently reasoned observation for every complete question and scheme.
BIO = [
    'The rodent-navigation illustration models a selected spatial-learning process, not the complete experience of navigating a human city. The explanation makes control useful while retaining language, experience and social-context limits on translation.',
    'A neurotransmitter mechanism can explain one component of behaviour without establishing an exhaustive explanation. The worked example separates a useful biological level of analysis from the unjustified claim that psychological meaning and context add nothing.',
    'The answer correctly treats fMRI as an indirect blood-oxygen-related signal compared between task conditions. It does not equate a highlighted area with a photograph of a thought, exclusive localization or experimental proof of causation.',
    'Cortisol is used as a chemical messenger contributing to stress-related processes through receptor-mediated activity. The example allows bodily state and coping context to influence behaviour and avoids assigning a unique inevitable action to a hormone.',
    'The diathesis-stress explanation requires a vulnerability interacting with demands, not a deterministic label or a diagnosis inferred from a stressful event. Protective resources and different outcomes under comparable demands are explicitly compatible with the model.',
    'Inheritance is presented as a possible source of variation in dispositions, with developmental environments affecting expression. The scheme correctly rejects treating population heritability as the percentage of an individual behaviour caused by genes.',
    'The revised speech example names left inferior frontal regions, including Broca-associated areas and their connections. Fluent-production difficulties can illustrate functional specialization while the network caveat avoids a one-region-one-behaviour claim.',
    'Practice of an unfamiliar two-handed rhythm is a coherent example of experience-related plasticity. Improved coordination is distinguished from direct observation of new neurons or proof that unlimited recovery or general transfer must follow.',
    'Given Z blocks the return carrier, the proposed mechanism is reduced recycling of M after release, potentially extending availability in the gap. It is neither evidence that Z manufactures M nor sufficient evidence for a clinical benefit; the answer retains those limits.',
    'Adult A differs from B in stated vulnerability and support while both encounter a demanding job. The application identifies the interaction and protective factors without diagnosing either adult or claiming the case comparison isolates a single biological cause.',
    'The poster includes one threat circuit while excluding interpretation and experience. The answer explains why this is an incomplete reductionist account, yet preserves the possibility that a threat-related circuit contributes to the response.',
    'Improvement after injury and supported speech practice is compatible with adaptation, reorganization or compensation. The scheme does not infer restoration of the original tissue from a behavioural timeline or promise recovery for every injured person.',
    'Repeated tactile-pattern recognition with spoken feedback supplies relevant developmental experience. Plasticity offers a mechanism for changing processing, but the fictional sequence does not establish a precise anatomical increase or a fixed outcome for all children.',
    'An early sensory-discrimination animal task can inform a selected developmental mechanism. The answer properly separates this limited contribution from modelling human childhood as a whole and includes welfare and species-context constraints.',
    'Inherited capacities may contribute to acquiring language, but a particular language depends on communication opportunities and experience. The scheme does not confuse a general biological capacity with inheriting vocabulary, accent or a predetermined developmental endpoint.',
    'The contrasting fluent-production and comprehension difficulties support investigating distinguishable language components. The answer is conditional on the fictional profiles and avoids inferring an exact lesion site, complete independence or a clinical diagnosis from two descriptions.',
    'The same proposed messenger M is placed in trusted-friend and unfamiliar-rival situations. The response correctly treats altered attention as interacting with the meaning of cues, rather than translating M into a universal trust or affiliation effect.',
    'A brain injury can contribute to altered inhibition and thereby affect interactions. The worked account correctly leaves room for expectations, communication and circumstances, so neither every disagreement nor the whole family relationship is reduced to the injury.',
    'The supplied receptor model explicitly gives increased activity for R1 on A and decreased activity for R2 on B. The scheme uses those opposite effects to explain receptor dependence, without inferring that one messenger must excite every cell or produce one whole-person action.',
    'Resemblance in an adoption scenario is compatible with inherited dispositions but is not a genetic experiment establishing a particular causal pathway. Different relationships and developmental opportunities remain relevant; a single family story cannot estimate heritability.',
    'The movement sequence changes from effortful separate actions to more fluent performance with feedback and practice. Plasticity is an appropriate explanatory hypothesis, while the answer correctly avoids converting this observation into a measurement of synapses or tissue.',
    'Word retrieval uses A and B while planning uses B and C in the given model. The shared B supports overlap and the differing components support specialization; localization therefore does not require isolated modules or one anatomical location for every complete behaviour.',
    'Landmark navigation in an animal task does not directly test reading instruction in children. The answer identifies the missing bridge between the selected mechanism, species and educational outcome, rather than dismissing all animal evidence or accepting an instructional claim automatically.',
    'A reading-related brain measure is insufficient to justify giving every learner one exercise. The answer distinguishes measurement from an effective intervention and retains language experience, support and diverse needs as relevant to responsible educational use.',
    'A biological mechanism relevant to low mood can support a partial account, but treatment response is not by itself proof of an original chemical deficiency. The essay weighs this causal inference against contextual explanations and the responsibilities of communicating uncertainty.',
    'Reliability of an imaging signal does not establish what psychological construct it measures or why a group difference arose. The essay correctly separates measurement validity from causal direction and recommends converging designs rather than reading causation from scan contrast.',
    'A change in recorded prevalence is compatible with environmental exposure, recognition or diagnostic changes as well as other possibilities. Population heritability does not identify the cause of a temporal shift or show that the same individual outcome is fixed.',
    'Animal research can offer causal control over selected processes while creating welfare responsibilities and translation limits. The essay develops necessity, replacement, reduction and refinement alongside scientific usefulness instead of treating potential human benefit as automatic permission.',
    'Initial language specialization after a child injury and later plasticity are compatible rather than contradictory. The essay allows adaptation and individual variation while avoiding the stronger unsupported claims that regions are interchangeable or developmental plasticity guarantees recovery.',
    'The developmental transition is used to evaluate an interaction between vulnerability, demands and protective support. The answer treats the model as a testable probabilistic account, not a label that explains any outcome after the fact or excludes change.',
    'Child imaging raises task-comprehension, movement, assent, privacy and individual-prediction issues. The answer links these to valid interpretation and responsible communication without implying that a group signal diagnoses a child or measures future ability without error.',
    'An animal social-development model requires operational meanings for the behaviour under study and evidence for translation. The essay balances controlled comparison with welfare and human-context differences, rather than calling the animal response a complete human attachment experience.',
    'Chemical signals may influence attention or arousal in relationships across different timescales. The answer distinguishes these contributions from the social interpretation of a friend or rival and rejects calling a messenger a single-purpose trust chemical.',
    'Arousal is not identical to an aggressive act, and a biological correlate does not explain every interpersonal conflict. The essay distinguishes a deliberately narrow methodological focus from the claim of a complete cause and gives social interpretation a coherent role.',
    'Genetic prediction of relationship tendencies must remain probabilistic and sensitive to the population and environment used to validate it. The essay develops privacy, consent and stigma risks without treating predictive association as destiny or a moral judgment.',
    'An empathy task and its imaging contrast operationalize selected aspects of a broad construct. The answer identifies reverse inference and task-ecology limits, so a pattern associated with empathy cannot simply label an individual as empathic in everyday life.',
    'That experience can change neural systems does not validate every educational product described as brain based. The essay requires evidence for the particular teaching method and outcomes such as understanding and transfer, distinguishing mechanism plausibility from intervention efficacy.',
    'Acquiring a route, retrieving it and remembering actions can engage distinguishable processes and overlapping networks. The answer correctly rejects treating activation in one navigation task as the exclusive storage site or a universal explanation of all memory.',
    'A genetic contribution to variation in learning is compatible with substantial developmental and educational change. The essay considers expectation effects and responsibility when communicating potential, rejecting the inference that heritable differences establish fixed instructional limits.',
    'Controlled animal learning can clarify selected causal mechanisms, but language-rich classrooms involve additional processes and context. The essay weighs scientific control, translation and welfare rather than assuming either complete equivalence or zero relevance to human learning.',
]
COG = [
    'The arbitrary duration example illustrates adjustment from an initial reference rather than a relevant evidential starting point. The explanation does not assume the estimate is wrong merely because a number appeared first; it identifies insufficient evidence-based revision.',
    'The neutral sound is paired with food that elicits salivation, making the sound a conditioned stimulus and anticipatory salivation a conditioned response. The account distinguishes stimulus association from changing a voluntary action through its consequences.',
    'Separating instructions from symbols can consume limited working-memory resources through avoidable search. Integrating them is a coherent cognitive-load example, with prior knowledge and task demands qualifying the prediction rather than assuming all effort is harmful.',
    'The working-memory illustration describes coordinated verbal and visuospatial processing as a model with testable implications. It does not turn theoretical components into literal anatomical boxes or treat naming a component as an explanation without a process link.',
    'Selecting supportive examples while overlooking contrary information is a confirmation-bias mechanism even if the favoured belief happens to be true. The answer correctly locates the bias in evidence evaluation rather than simply in a false conclusion.',
    'Familiar word recognition can be relatively automatic while unfamiliar interpretation calls for deliberate processing. The scheme avoids the common false equivalence of fast with irrational and slow with correct; expertise and task demands matter.',
    'Reinforcement increases a behaviour and punishment decreases it; positive and negative refer to adding or removing a consequence. The worked account classifies consequences by their observed function rather than pleasant intentions or the everyday meaning of negative.',
    'A restaurant schema supports efficient expectations but may supply a false detail in an unfamiliar self-service setting. The example permits revision through experience and does not imply that all remembering is fictional or that schemas can never be useful.',
    'An unrelated twelve-hour example can anchor the workshop estimate despite available staffing and task evidence. The answer explains the reference-and-adjustment process without inventing the correct duration or assuming every estimate near twelve is necessarily biased.',
    'A chime repeatedly preceding an unpleasant procedure can later elicit tension without that procedure. The answer uses an associative explanation for the given fictional sequence and does not propose inducing distress as a student practical or confuse the tension with an operant action.',
    'The proposed leaflet places explanations beside their symbols, reducing split attention for a novice. The scheme explains why this may free resources for understanding, while prior expertise and the actual complexity of the task remain relevant boundary conditions.',
    'Interpreting an ambiguous message as threatening may prioritize danger cues, which could reinforce the initial interpretation. The answer treats this feedback loop as a hypothesis requiring evidence, not proof supplied by arrows or a denial that real danger can exist.',
    'The teacher records stopping puzzles but omits persistence and improvement. This is selective evidence consistent with confirmation bias; the answer does not infer the child lacks ability or claim the teacher must consciously intend a biased judgment.',
    'A familiar project response may be automatic while a new constraint justifies deliberate checking. The application uses the changed task demand rather than treating adolescent age, automaticity or speed alone as evidence of defective reasoning.',
    'Completion becomes more frequent after repeated reminders stop, which fits negative reinforcement because an aversive consequence is removed. The answer correctly distinguishes this functional increase from punishment and does not assume that the reminders are added as a reward.',
    'A library schema based on fiction may shape a child’s first interpretation of a wildlife explanation book. Discussion and contrasting examples can revise that expectation; the answer does not infer a fixed developmental stage or exact age threshold from the case.',
    'An early unequal proposal can become a reference even before task and availability evidence is considered. Anchoring is a possible explanation for limited revision, while relevant skills and legitimate bargaining remain alternatives rather than every unequal outcome being classified as bias.',
    'The revised family-call tone begins neutral; unexpected loud feedback elicits an automatic startle. Tone-elicited tension after pairing is distinguished from voluntary muting, which would be negatively reinforced if removing the aversive sound makes muting more frequent. This resolves the original US ambiguity.',
    'Conversation, several message threads and unfamiliar booking instructions create concurrent cognitive demands. The answer explains limited processing resources without equating an attentional failure with lack of care or inferring a clinical deficit from an everyday scenario.',
    'A memory failure can arise from encoding, temporary maintenance or retrieval differences. The model supplies hypotheses to distinguish with task manipulations, while forgetting alone is correctly treated as insufficient to identify which process failed.',
    'Testing only striped examples does not challenge the belief that stripes are necessary for a Luma. A non-striped candidate could falsify that hypothesis, but the answer appropriately leaves the actual unknown rule unspecified rather than inventing it.',
    'A familiar procedure may run automatically despite a changed constraint. Deliberate comparison with the current requirement is useful here, but the scheme does not claim deliberate processing guarantees the right answer or that automatic expertise has no value.',
    'Added tokens followed by more submissions meet the functional definition of positive reinforcement in the fictional case. The answer distinguishes an increase in that behaviour from proof of intrinsic interest, understanding or lasting educational benefit.',
    'Prior visits to ticketed museums can support a reconstructed memory of a desk absent from this exhibition. Schema-consistent inference is plausible, while suggestion or source confusion remain alternatives; the case does not prove all recollection is inaccurate.',
    'A preferred well-being explanation can bias the scrutiny given to benefits, failures and alternatives. The essay treats fair evaluation as revisable evidence assessment, avoiding both uncritical belief and the assumption that a negative or skeptical conclusion is automatically unbiased.',
    'Deliberation can improve some health-related judgments, but expertise, information quality and available time affect its value. The essay rejects the universal claim that slower thought is better and distinguishes an organized comparison from unproductive repeated worry.',
    'Consequences can help establish and maintain a habit, but an initial increase need not survive a changed schedule or preserve personal goals. The essay develops autonomy and responsibilities without equating compliance with health benefit or assuming reinforcement explains the whole behaviour.',
    'Schemas can shape how people interpret and report well-being without making their experience unreal. The essay connects prior expectations to construct measurement and responsible interpretation, while allowing situational causes and evidence that challenges an initial account.',
    'An early developmental label or first performance can become a reference that is not revised enough after progress. The essay distinguishes that bias from legitimate prior information and explains how subsequent evidence and assessment changes should affect judgment.',
    'Associations between cues and emotionally significant experiences can contribute to developmental responses. The essay considers context, other pathways and change, correctly avoiding the inference that extinction necessarily erases the original learning or that conditioning explains all emotional development.',
    'Age can covary with experience, knowledge and task familiarity, so cognitive load is not read directly from a birthday. The essay distinguishes avoidable presentation demands from productive effort and develops conditional educational implications rather than a uniform developmental rule.',
    'A developmental cognitive model needs specified processes and predictions that can be distinguished from alternatives. Merely renaming age differences as stages does not explain them; the essay links explanatory value to testable tasks and recognizes model simplification.',
    'Two people can selectively recall examples supporting different interpretations of a delay. The essay explains a possible maintenance cycle in conflict while preserving competing demands and genuine differences in values; disagreement alone is not sufficient evidence of confirmation bias.',
    'Fluent interpersonal routines can be useful, with deliberate checking especially valuable when cues or assumptions change. The essay considers targeted reflection without suggesting constant analysis improves every relationship or that prolonged rumination necessarily resolves a disagreement.',
    'Cooperation can be influenced by consequences only when the relevant behaviour actually changes. The essay weighs this functional explanation against meaning, autonomy and social goals, so a psychological mechanism does not by itself justify manipulation or coercion.',
    'Relationship schemas can organize interpretation efficiently yet misfit a new person or situation. The essay makes revision and perspective important without blaming someone for an adverse experience or implying social conditions are only products of their expectations.',
    'An unrelated earlier score can bias marking, while a criterion-linked response example can be a legitimate standard. The essay explains this distinction through relevance to present evidence rather than claiming all initial reference points are improper anchors.',
    'Emotional associations with classroom cues can affect participation, but this is a partial account of learning. The essay considers supportive changes, prior experiences and cognitive explanations rather than treating every classroom behaviour as a conditioned reflex.',
    'Reducing unnecessary search can help learning, but minimizing every cognitive demand can remove productive processing. The essay evaluates understanding, retention and transfer instead of treating a feeling of ease or immediate task completion as a sufficient learning outcome.',
    'A memory model earns explanatory value by predicting differences across appropriately contrasting tasks. The essay distinguishes a useful simplified process account from a literal map of brain boxes, and acknowledges that similar outcomes can sometimes fit competing models.',
]

# Scientific and layout observations from all32 exact native1200/mobile360 pairs.
FIGURES = {
    'bio-009': 'Release, gap and return-carrier boxes preserve the stated mechanism; no receptor or reuptake answer label is added. Text, box edges and the constructed-stimulus footer are clear at both sizes.',
    'bio-010': 'Adult A and B occupy separate boxes and the demanding new job is common to both; no invented outcome is pictured. The vulnerability/support labels remain fully contained and legible at360px.',
    'bio-011': 'Included one threat circuit is explicitly separated from excluded interpretations and experience. This depicts the claim to evaluate rather than endorsing it; both two-box labels and footer are unclipped.',
    'bio-012': 'Initial injury, supported practice and later improvement appear in temporal order, without an anatomical recovery claim or causal arrow. All three rows are readable in the native and phone-width versions.',
    'bio-013': 'Touch, spoken instruction/feedback and repeated recognition reproduce the fictional learning sequence. No measured brain growth is plotted; spacing and text fit are clear in both rendered files.',
    'bio-016': 'The opposite fluent-production and comprehension profiles are copied accurately into separate child boxes. Neither box assigns a brain lesion or diagnosis, and the shorter two-box layout has no clipping.',
    'bio-017': 'Same M, trusted-friend cue and unfamiliar-rival cue are visibly distinct givens. The schematic does not add a trust hormone or deterministic behavioural outcome; all labels remain readable on mobile.',
    'bio-019': 'M is available to both receptors; R1 on A increases activity and R2 on B decreases it. The opposite signs are correct and no extra cell-wide excitation claim is implied by arrows or geometry.',
    'bio-021': 'New separate movements, practice with feedback and later fluency form the stated performance sequence. The schematic adds no neuronal counts or anatomical data; heading, boxes and footer are clean.',
    'bio-022': 'Word retrieval contains A/B, planning B/C, and the last box notes interaction. The shared component B is consistent across tasks; these are explicitly fictional components rather than a false brain atlas.',
    'bio-023': 'Landmarks/navigation in an animal task and proposed reading instruction are separate boxes, leaving the inferential bridge for the student. No animal photograph or fabricated empirical result is used.',
    'bio-024': 'One measure, one exercise for every learner, and omitted language/support match the proposal being evaluated. The figure shows the problem givens rather than a validated teaching recommendation.',
    'bio-026': 'The two research questions correctly separate what a scan represents from why a difference arose. The heading wraps without overlap, and neither box presents an imaging correlation as a causal result.',
    'bio-031': 'Understanding/assent, task/imaging signal and privacy/use of findings match the child-project issues. No diagnostic brain image is implied; the two-line heading and all body labels fit clearly.',
    'bio-037': 'Biological plasticity, a proposed method and the goal of understanding/transfer remain three different steps in the inference. The display does not claim the intervention works; both sizes are legible.',
    'bio-038': 'Learning a route, retrieving a familiar route and remembering actions/events are kept distinct. No exclusive memory store is drawn, and the three equal boxes are a conceptual comparison, not quantitative evidence.',
    'cog-009': 'The twelve-hour example is explicitly unrelated while task/staffing evidence is separate. No correct duration is invented; the reference, evidence and judgment boxes are fully readable at360px.',
    'cog-010': 'The chime precedes the unpleasant procedure, initial tension occurs during it, and the later chime occurs without it. The order preserves the classical-conditioning case without adding a deliberate behaviour.',
    'cog-011': 'The current leaflet separates instructions and symbols while the proposal puts explanations beside symbols. This faithfully contrasts presentation demands, with no invented achievement score or effect size.',
    'cog-012': 'Interpretation, prioritized danger cues and a proposed reinforcing feedback are labelled as a cognitive proposal. The lower text wraps safely and does not turn the proposal into an observed causal cycle.',
    'cog-013': 'The initial belief, recorded stopping occasions and omitted persistence/improvement are correctly distinguished. The diagram exposes the supplied evidence-selection pattern without asserting the child lacks ability.',
    'cog-015': 'Prompt completion is followed by reminders stopping, then more frequent completion. That displayed sequence supports the intended removal/increase distinction; no misleading punishment label appears.',
    'cog-016': 'Fiction-oriented prior expectation, a wildlife explanation book and contrasting discussion are in the stated order. The boxes add no developmental age claim, and all text remains within boundaries.',
    'cog-017': 'An unequal first proposal precedes consideration of tasks and availability, with later revisions near the proposal. No numeric split or rightful allocation is invented; this preserves the anchoring inference.',
    'cog-018': 'The final repaired image shows a neutral call tone, unexpected loud feedback and voluntary muting as distinct givens. It does not print US/UR/CS/CR answers, and every line including the long feedback label is clear.',
    'cog-019': 'Conversation, several message threads and unfamiliar booking instructions accurately represent concurrent demands. Equal boxes are not quantitative capacity claims; the long labels fit at native and360px sizes.',
    'cog-022': 'A familiar automatic procedure, a changed constraint and a deliberate applicability check remain distinct. The image adds no claim that one processing mode is always better, and spacing is unclipped.',
    'cog-024': 'Prior ticketed visits, this exhibition without a desk and a later desk recollection preserve the inconsistency to explain. The wrapped heading and all three rows remain legible without an actual museum photograph.',
    'cog-025': 'Preferred well-being belief, mixed available accounts and selective serious attention are separated. The interrogative final box leaves the evaluation to the student rather than supplying a conclusion as data.',
    'cog-029': 'The early reference is followed by new tasks/progress and the question of revision. No numerical developmental trajectory or fixed child trait is pictured; native and mobile text are fully contained.',
    'cog-033': 'Little-concern and competing-demands interpretations of one delay remain distinct perspectives. Different recalled examples are stated without making either view true; the long body labels are readable.',
    'cog-037': 'The unrelated prior score and legitimate criterion-linked example are explicitly contrasted with present work evidence. This supports the intended relevance distinction without banning all reference standards.',
}

SOURCES = {
    'imaging': ('https://www.nature.com/articles/35084005', 'Primary Nature2001 indexed abstract independently read: simultaneous neural recordings and BOLD comparisons support the caution that fMRI is an indirect signal, not a photograph of a thought. No numerical result from this study is attributed to the fictional stimulus.'),
    'inheritance': ('https://pubmed.ncbi.nlm.nih.gov/25985137/', 'Primary2015 meta-analysis abstract independently read. Twin-based population variation estimates do not allocate an individual behaviour into genetic and environmental percentages; no empirical heritability number is fabricated in the question.'),
    'plasticity': ('https://pubmed.ncbi.nlm.nih.gov/10716738/', 'Primary Maguire2000 abstract independently checked. Structural volume associations motivate a cautious plasticity discussion but do not validate every fictional task, reveal synaptic counts or establish universal educational transfer.'),
    'anchor': ('https://pubmed.ncbi.nlm.nih.gov/17835457/', 'Primary Tversky/Kahneman1974 abstract independently read: adjustment from an anchor is a judgment mechanism, with useful heuristics distinguished from systematic error. The practice scenarios are original and contain no copied task data.'),
    'load': ('https://onlinelibrary.wiley.com/doi/10.1207/s15516709cog1202_4', 'Primary Sweller1988 abstract independently checked: limited processing resources and schema acquisition motivate task-specific load explanations. The answer does not equate all mental effort with extraneous load.'),
    'confirmation': ('https://journals.sagepub.com/doi/10.1080/17470216008416717', 'Primary Wason1960 indexed abstract independently read: exclusively confirming instances may fail to discriminate a favoured hypothesis from alternatives. The fictional Luma and judgment cases are not copied empirical findings.'),
}

# Exact raster bytes actually inspected; a render change needs a new visual review.
REVIEWED_FIGURE_HASHES = {
    "ib-psy-bio-009": [
        "02166f025fe76f986b9bfd40b015a30b48123647005a6b2edef4141ee152657f",
        "1cee6a5b62422ee2c259450a8a16caa5dcba3857eee959da60e3f2ab1bc1bdd3",
        "6a2bc558c6ceebb010be313234df83ef7d32afb95a655a75696a705597709371"
    ],
    "ib-psy-bio-010": [
        "07c2df1f5271a92c6ef769932614e1d497e13ac19c107c7c6c40b2f945e12c6d",
        "d93241f8cab9ff00f4b887d9ff79e0a71680b3a74672ebb11db4b56fb6ef3f73",
        "daf66840cad57ded320eaf9a4313086c1e804a0f398b6b55bbcfce43c92c10db"
    ],
    "ib-psy-bio-011": [
        "b66c04d409827c529c5d7d3bd8233f3957364abcb2f9a220ee04f50ad5bedd45",
        "9c1e09885f6c984c4d4dae5a4961fa53f30a727a71ee17de6746251e36cf495d",
        "31d9da04d7462fdf8a02a565aab6e8ee636d3a92adbd5dbb12e9d365b915dadf"
    ],
    "ib-psy-bio-012": [
        "07fec9150773b7bcbd859881cbf22ce8471eebb107cbaa3842236c2df72a2b65",
        "3d64aabf5139fb85f5260be2289f84eb3d341d8b17e6cddac6fadfc261a82004",
        "ea423054562b2efbf59d093bd2cedcdb33b18ec97c479378422308e7d8bbd80d"
    ],
    "ib-psy-bio-013": [
        "d2e3f465fa9ee90be1283e9ceb7c5833092452e6c592fa46ac6abe985e6e4bf1",
        "f14dd8c238ef77e79401ab13f5e5d0763368844d4f900c6b6f7b76ef2b76cdb5",
        "41f917c7d91bd19288ed99fdd9bf9404317cbaed5769be75aa520e7b333a5a2c"
    ],
    "ib-psy-bio-016": [
        "eb000f5e4ec85b881c6dd78632044bf8a553b4399af2f7a563f43a9797161009",
        "6552ca6cc3532545912ffd6089234fdc7578e31620cf513f0e4757be76ac0fc8",
        "190efa751ac24830dacd7f8b7d51ad7bcbbf47157a18eb66cd262f3c3c3c315b"
    ],
    "ib-psy-bio-017": [
        "8679b8d96fd59ed876911694dd3d1e3b31165adfc7f88f6d1b98968d677aa89c",
        "f2f4dc30e3b78b4bf57c3882b50af350d8b9f9c9055e0bc82538d238938011b9",
        "5a1ed65eeb28f71596a233e5bde383c8b43a9103d7a938d80541624d0fa2ab2d"
    ],
    "ib-psy-bio-019": [
        "6e7be3dcf6e810511f656914f99678a9d459253e2df67eb4e7e16137ef337f28",
        "025e248df4a0204dbb02027d8b894e58f8803c1cfa1bacd11a09dc8601b94351",
        "d1f5ddd55b119f9ae5a92a03b7cd7f590e763b7d40dc33f187ce182a1b5aef8c"
    ],
    "ib-psy-bio-021": [
        "2c2e863403f7815bbaaed5fbef49e34c9e48451b55922c56c16653db06a2eaef",
        "887f52feaac7d399de345e8c7dfad7de37594aac58a873c72901eac31a3a00ae",
        "50d5210b25cc81579f16a4386433b67ac70ce614acbdf5c61a7a3c75082210cb"
    ],
    "ib-psy-bio-022": [
        "6b0992d12bb643fbd7b4f0a4d166c11ef0dce4bc1db46becea3ce0005ebcf565",
        "ab4c64eee255285cc8aa381f44055d706f52f5a80c13e910a753b08b67d6ea16",
        "14482af3ec8a7b40fc24ef31473d7214c91e88b4f2ee52319eb7fe288b181a88"
    ],
    "ib-psy-bio-023": [
        "c470883beb78e0d6d614e5648d93cfd81ddcdc978507d067fa723062bc2026be",
        "fffd50767a4930e912854a6ce2013f60aa05dd858bb51a7f392915247a5dec09",
        "9bb66ba1dd8cb249036025229001f74c0a96d86fcc9b49de16777ec03d68f509"
    ],
    "ib-psy-bio-024": [
        "383e8d5aef0b37c7239f31bc8b5db440949e96e00268f6fb361b5d7a9525e846",
        "58ca6a3281767629c1fc1c8415bd7d10706977afcaca60fa976e02086976da7e",
        "6e732a77caa6e7d33eda90c3ebcf86a4d1580fc985aeea0b3ee697cd75af9e6a"
    ],
    "ib-psy-bio-026": [
        "d93511e3bd1093e284db431f22340fe7d1a1c7f8b2a45599237f420b61a58a08",
        "1ae03f6c677781442aac4be24c3bf3130c7a32575182dfee1229469d81181f3a",
        "133606527c610c3d499bdd431a1ccd197a5ec6c61712e5eaf9a5c1adbfcee2d0"
    ],
    "ib-psy-bio-031": [
        "9ac36b44dbc16ab242b7de8a7e65ce6fed53dd6cc9641332706b9cd0df3a4fa3",
        "f43a8e035549e18f9aa24cc35f23384967f10bf6d9fb4b98f15d5709c534e09e",
        "bb06eaafe29a97c0a3ccd2e877d716d8fe80a8aa43453764b6703dcdfed3569c"
    ],
    "ib-psy-bio-037": [
        "c987917170f47c523dd0b2ab508fe32cad0e579ec50e77edc792898e329cb8de",
        "a7ef9b78d422684f3d89434bc3272ea028049247e202220b18e6182120787e2f",
        "b9d35eaaf102b0964e0ce517fb5d2ad44ae090313d18b3dd740bc88ca2b7dcb2"
    ],
    "ib-psy-bio-038": [
        "ade6e87d0178de6c69ccc2108bc97f73e9cbec3f2a009da88f2fe0ed2d45e213",
        "16d4d4a9667535f483780929da73f461449d61b6e69de2a5861c5de9c643dcad",
        "c610486cb113ee420c633f2bc5e6b07a10aaac645a0f8bd87ae8c72a28a913e0"
    ],
    "ib-psy-cog-009": [
        "ba5acafa0f6d89a7cb7ef779fa7fba865348d7fca7b5b43c2891902a453398da",
        "a7eec1b0bb2708e06dd73a3efb9099ce6d5ac277b830e6352589c461ab67655c",
        "15955a26305bd32600de568c1d8299703f62517db792097b186974897aedef47"
    ],
    "ib-psy-cog-010": [
        "8ca801253c9d7f3d5d07e8300803e1604825ff82d4774f97c28c84c6be3ae394",
        "868fc0befd74c353a21cce7d17a41cb13a94cf4f0248c437d09e6e7a9f790359",
        "318148150050ed3c60312ed2e6c74d07e7e6b75d7c6c61287e951f89f75edb03"
    ],
    "ib-psy-cog-011": [
        "c84a36e0a04eb5e441ed08f2dd2cb415cef0a9af78822f4ee422acd1b3efb77e",
        "0312edf2cdca500c9ee8f86c7be0dd0c3429683cbf2095b8c8d1ce20b5e86039",
        "db58858a3212658db84436648e5b249851ad95ddc2983534165bcbfb45cb1332"
    ],
    "ib-psy-cog-012": [
        "68ce7c096c86f1724bcd426c9b31ca367e61b7479d0542c1055958730b962097",
        "574c367040a1b0e126dc3b554b895f7c1b6ab26b5a6b40b26383c56346d50b87",
        "3adea2e0878f9ce1f84389ce891875bb66d1ccfae66ec12396b673e314eeebc6"
    ],
    "ib-psy-cog-013": [
        "f656fccd983a7d1671d5f169d3c3c43f5d399116bdffc524b23273294ae880b4",
        "c44e13481979870a5dabec024f119ed09796b9482bac0fe1eae20a70f7a094b8",
        "4dde2e35ebed6dc97256b5a34667b6842e6644dfb8fe4bbf48291ffc49034468"
    ],
    "ib-psy-cog-015": [
        "26c1f2cd6a5b0335b5d8be95010735fabee0119ac80482b1cef72012d517643e",
        "dbc5cde450eba4092a353f1d9cb60e6c93489ba89bf49a9f8eb2dfd7421fd83c",
        "083ee4ed8612653fc5cb7d096bc96a6d39e7fc591bf5bd48c2b4aff2eaea2950"
    ],
    "ib-psy-cog-016": [
        "e94edf4ceeb75ee9171b0fa20c34baf680c152cb56b3de1b66d05e5e88f04418",
        "bdc7fb7f393268ec54ce3be42bc56eefe4241761a418d205225faba1fa19675b",
        "3d81cf0ad81a906590d3515e0793509bca3216faecf20b0aacca2fac5b03a828"
    ],
    "ib-psy-cog-017": [
        "2e01e3bc33ea756ad268e52f1325e592538b4ca9afc53d42ef0a54045dc66d42",
        "fd71abbe520541c9247fb0887b37e777d2071970f7154d46c447cdea3e516a90",
        "b04a8476969d0d8c9396edbee9738f7057f5c2b78866f56439d66c424a90cc30"
    ],
    "ib-psy-cog-018": [
        "1db45dd0a2c152e51317fa765427ae7ba20534bbd84e07852712628bd32bdcbb",
        "156ede2fca6fc19e2585bfe68c5f21b0bf0c10588dea3c19bda71d0ed896d61d",
        "4f255179244016cf24c6b9fca97588167a90b51babea1f49f0c97ba49fcab8e9"
    ],
    "ib-psy-cog-019": [
        "369f303445d02ec445639cef342a841fae897d01ad312a41d380365ae5fcb575",
        "eef9b6c0778a09afc27c735badec662134004e9f47c0d5c84ff36510b03f3198",
        "020401c6fc12a0e6b105c88f918e39f21aa32b4c475693af344155e0de18e064"
    ],
    "ib-psy-cog-022": [
        "beb9bf6384a9558e0a7a2e92911dc956f4f2caf09abe19dcf199b199b8fe892f",
        "7d75fa5624c8fd1b7917e5d28a04e3700db694d8dbb6891e4cb9774a17f4395d",
        "b757ec5db908f4d019677fdc634e426a73b07134d38ac0bc8b4369d48432671a"
    ],
    "ib-psy-cog-024": [
        "6e6e94fd876e9fb3bd3f16455b2ba761553f5a3cc2e220382627303956e9e130",
        "77a26aafc749b26a58125a9b7b76de5c021c51b6a489a1afb10d91f07378d43b",
        "8e88060f5d8367d271f2966c6d17743f766b504836e7b1b2145a7bb98ed0afee"
    ],
    "ib-psy-cog-025": [
        "636e2d21d4fbfc4c031732212bc41a8e92fd2fc993c58353b4885476ab0e84fe",
        "ae50ca40bf242dce4b3355b5c9d469984f44c23b28079233c5aa62cc0a039f29",
        "4b25673cf8fd6954e00485ce2eb70d8e7a0b421162cb39e97ec3dbd781f05806"
    ],
    "ib-psy-cog-029": [
        "78a58814d577890ccf03dabba7d351edb973fa70657ee7392b531f4580744102",
        "d418e223a81b877fa017a999cd48f0c18add2061891f8c2f1f333bcec0d89cc3",
        "8897c32b9f2c710710b811f3a8a3e01466555251ee9c9379e174cf246f697687"
    ],
    "ib-psy-cog-033": [
        "7c691ec13c04e73b8a14ff31b0c26ec05a91925c4b89ca61145d69a140259d83",
        "2082d6dccb161d9371e8d39ff4d3d78c4d7a491ecfb4ce29182830fabc348fa6",
        "b9219ba0f4a93989f08feea0b0c6afd16b799c2a3a565fda9df720de954f49e7"
    ],
    "ib-psy-cog-037": [
        "dc325f04d49dd74cf27408759ecf862ddc1a1520279a33223a5551dd368841dc",
        "389596428b262db9e20b5b0d9d0ebd4722987f67e5cdc0d75acac43ec8dc592e",
        "c14d5d9aed14565123cc7e156a2d9fda408ebd5451851ae927eb7a500643aede"
    ]
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def qhash(q):
    return sha(json.dumps(q, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())

def source_checks(q):
    checks = [{'url': GUIDE, 'note': 'Scope cross-checked against the official2027 terminology and assessment mapping retained in the reviewed content contract: this is shared SL/HL Paper1 conceptual/application practice, not HL direct data analysis or legacy study-recall examination.'}]
    key = None
    if q['id'].startswith('ib-psy-bio-'):
        if q['syllabusCode'] == 'BIO.03': key = 'imaging'
        elif q['syllabusCode'] == 'BIO.06': key = 'inheritance'
        elif q['syllabusCode'] == 'BIO.08': key = 'plasticity'
    else:
        key = {'COG.01': 'anchor', 'COG.03': 'load', 'COG.05': 'confirmation'}.get(q['syllabusCode'])
    if key:
        url, note = SOURCES[key]
        checks.append({'url': url, 'note': note})
    return checks

def validate_rubric(q, section):
    maximum = {'p1-a':4, 'p1-b':6, 'p1-c':15}[section]
    assert q['marks'] == maximum
    assert len(q['markScheme']) == 1 and q['markScheme'][0]['part'] == ''
    scheme = q['markScheme'][0]
    assert all(s['code'] == 'IND' for s in scheme['steps'])
    assert len(scheme['steps']) >= (4 if maximum == 15 else 2)
    assert len(' '.join(s['text'] for s in scheme['steps']).split()) >= {4:70,6:100,15:220}[maximum]
    rub = scheme['rubric']
    assert rub['maxMarks'] == maximum
    covered = []
    for b in rub['bands']:
        assert isinstance(b['min'], int) and isinstance(b['max'], int) and b['min'] <= b['max']
        assert len(b['descriptor']) >= 20
        covered.extend(range(b['min'], b['max']+1))
    assert covered == list(range(maximum+1)), (q['id'], covered)
    return sha(json.dumps(rub,sort_keys=True,separators=(',',':')).encode())

def main():
    contract = json.loads((ROOT/'docs/ib-psychology-reviews/content-contract.json').read_text(encoding='utf-8'))
    assert contract['firstAssessment'] == 2027
    index = json.loads((ROOT/'docs/ib-psychology-reviews/native-diagram-index.json').read_text(encoding='utf-8'))
    fig_records = [r for r in index['records'] if r['questionId'].startswith(('ib-psy-bio-','ib-psy-cog-'))]
    assert len(fig_records) == 32 and len({r['questionId'] for r in fig_records}) == 32
    figures = {r['questionId']:r for r in fig_records}
    records, files, all_ids, all_stems = [], [], [], []
    rubric_hashes = {}
    for filename, expected_sha in REVIEWED_FILES.items():
        data = (ROOT/filename).read_bytes()
        assert sha(data) == expected_sha, 'Edited content requires fresh independent reading: '+filename
        assert b'\r' not in data
        qs = json.loads(data)
        assert len(qs) == 40
        token = 'bio' if 'biological' in filename else 'cog'
        notes = BIO if token == 'bio' else COG
        assert len(notes) == 40 and len(set(notes)) == 40
        assert [q['id'] for q in qs] == [f'ib-psy-{token}-{n:03}' for n in range(1,41)]
        assert [q['number'] for q in qs] == list(range(1,41))
        assert sum(q['difficulty']=='medium' for q in qs)==20 and sum(q['difficulty']=='hard' for q in qs)==20
        assert {q['context'] for q in qs[8:]} == set(contract['contexts'])
        files.append({'file':filename, 'sha256':expected_sha, 'questions':40})
        for n,(q,reasoning) in enumerate(zip(qs,notes),1):
            section = 'p1-a' if n<=8 else 'p1-b' if n<=24 else 'p1-c'
            assert q['examSection']==section and q['examStyle']=='paper-1'
            assert q['subject']=='psychology' and q['firstAssessment']==2027 and q['level']=='sl'
            assert q['parts']==[] and q['calculator'] is False
            assert len(reasoning)>100
            assert all(c in contract['concepts'] for c in q['concepts'])
            if section=='p1-c':
                assert any(c in q['stem'].lower() for c in q['concepts']), q['id']
            rubric_hashes.setdefault(section,set()).add(validate_rubric(q,section))
            record = {'questionId':q['id'], 'questionSha256':qhash(q), 'status':'passed', 'reviewer':REVIEWER,
                'fullQuestionAndSchemeRead':True, 'reasoning':reasoning,
                'numericChecks':[], 'assessment':{'examSection':section,'marks':q['marks'],'scopeChecked':True},
                'sourceChecks':source_checks(q), 'openFindings':[]}
            if q.get('diagramSvg'):
                r = figures[q['id']]
                assert r['questionSha256']==qhash(q)
                assert [r[k] for k in ['svgSha256','nativePngSha256','mobilePngSha256']] == REVIEWED_FIGURE_HASHES[q['id']], 'Changed render requires fresh visual review: '+q['id']
                assert r['svgSha256']==sha(q['diagramSvg'].encode())
                key=f'{token}-{n:03}'
                assert key in FIGURES
                root=ET.fromstring(q['diagramSvg'])
                vb=[float(v) for v in root.attrib['viewBox'].split()]
                assert vb[0:2]==[0,0] and vb[2]==360 and vb[3]>0
                for e in root.iter():
                    assert e.tag.split('}')[-1] in {'svg','rect','text','tspan','line','path','circle','polygon','polyline','g'}
                    assert not any(k.lower().startswith('on') or k.endswith('href') for k in e.attrib)
                    if e.tag.endswith('rect'):
                        x,y,w,h=(float(e.attrib.get(a,0)) for a in ['x','y','width','height'])
                        assert x>=0 and y>=0 and x+w<=vb[2] and y+h<=vb[3]
                assert 'Constructed conceptual stimulus, not research data.' in ''.join(root.itertext())
                for role in ['native','mobile']:
                    p=(ROOT/r[f'{role}PngPath']).resolve()
                    assert ROOT.resolve() in p.parents
                    assert sha(p.read_bytes())==r[f'{role}PngSha256']
                assert q['diagramUrl'].endswith('/'+r['svgSha256']+'.svg')
                record['figureReview']={k:r[k] for k in ['svgSha256','nativePngSha256','mobilePngSha256']}
                record['figureReview'].update({'nativePngPath':r['nativePngPath'],'mobilePngPath':r['mobilePngPath'],
                    'scientificGeometryChecked':True,'legible':True,'reasoning':FIGURES[key],
                    'nativeInspected':True,'mobile360Inspected':True})
            else:
                assert q['id'] not in figures
            records.append(record);all_ids.append(q['id']);all_stems.append(q['stem'])
    assert len(records)==80 and len(set(all_ids))==80 and len(set(all_stems))==80
    assert sum('figureReview' in r for r in records)==32
    assert all(len(x)==1 for x in rubric_hashes.values())
    report={'status':'passed','reviewer':REVIEWER,'questions':80,'files':files,'records':records,
        'method':{'fullStemsAndAllIndicativeAnswerParagraphsRead':80,'bestFitRubricsReadAndCoverageChecked':80,
            'native1200FiguresInspected':32,'mobile360FiguresInspected':32,
            'mobileContactSheetsInspected':6,'numericAssertions':0,
            'numericRationale':'These80 shared Paper1 questions contain conceptual fictional scenarios and schematics, not quantitative datasets requiring inferential calculation. No mathematical test count is invented.',
            'automaticChecks':'Fixed raw-content hashes, exact IDs/section/marks, non-additive IND marking and complete rubric-band coverage, per-question and figure/index/PNG/CDN bindings, safe XML and rectangle bounds.',
            'limits':'Independent AI conceptual/scientific and visual review; not human IB-examiner moderation. Primary abstracts or indexed primary abstracts were checked as specified, not assumed full-text access.'},
        'resolvedFindings':[
            {'questionId':'ib-psy-bio-007','finding':'Localization illustration needed anatomical specificity.','resolution':'Left inferior frontal language regions including Broca-associated areas and connections are now named, with network limits retained; revised paragraphs reread.'},
            {'questionId':'ib-psy-bio-008','finding':'Optional breadth improvement after repeated navigation illustrations.','resolution':'Unfamiliar two-handed rhythm practice now supplies a distinct, scientifically coherent plasticity illustration; revised paragraphs reread.'},
            {'questionId':'ib-psy-cog-018','finding':'Previously meaningful pleasant messages were not a clean unconditioned-stimulus example.','resolution':'Replaced with initially neutral family-call tone paired with unexpected loud feedback and automatic startle; all US/UR/CS/CR and operant-muting distinctions reread and repaired native/mobile SVG inspected.'}
        ],'openFindings':[]}
    out=ROOT/'docs/ib-psychology-reviews/approaches-independent.json'
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'passed','questions':80,'nativeFigures':32,'mobileFigures':32,'files':files,'reportSha256':sha(out.read_bytes())}))

if __name__=='__main__':
    main()
