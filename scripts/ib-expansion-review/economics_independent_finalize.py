"""Bind the independent semantic, arithmetic and diagram review to final bytes."""
from pathlib import Path
from collections import Counter
import json,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/ib-expansion-reviews'
def read(name):return json.loads((OUT/name).read_text(encoding='utf8'))
numeric=read('economics-independent-numeric.json');figures=read('economics-independent-schema-figures.json');assert numeric['status']==figures['status']=='passed'
ledger=read('economics-ledger.json');family_by_id={r['id']:r for r in ledger};figure_by_id={r['id']:r for r in figures['perRecord']}
notes={}
def add(prefix,items):
    for i,item in enumerate(items,1):notes[prefix+f'{i:02}']=item
add('intro-',[
 'Scarcity is relative to competing wants; clinic opportunity cost uses three forgone screenings rather than the unchanged wage bill.',
 'Land, produced capital, skilled labour and entrepreneurial risk are distinguished; second-hand ownership and delegated management do not reclassify factors.',
 'Radio sacrifices are 6,12,18 for equal bicycle increments; marginal opportunity cost is increasing and per-unit cost differs from total sacrifice.',
 'Fixed 3:6 input requirements imply a straight frontier and two baskets per stool; both intercepts use the same resource constraint.',
 'Restored utilization is actual growth inside unchanged potential; demand weakness or permanent labour loss is treated only in the staged final application.',
 'Sector-specific skill growth rotates only the heat-pump intercept; the alternative transferable-skill condition can change the food intercept in final part.',
 'Real labour and monetary wages flow oppositely; saving is a leakage and capital investment an injection, with imports or bank liquidity qualifying transmission.',
 'Planned circular-flow injections equal leakages in every numerical case; this does not imply full employment, fairness or sustainability.',
 'Market and administrative water allocation both involve scarcity and opportunity cost; drought and needs-based access alter feasible outcomes.',
 'Testability distinguishes positive statements from normative value judgments; truth or majority support does not determine the classification.',
 'Festival demand and service quality confound the price experiment; comparison groups and random assignment improve identification without proving perfect control.',
 'A conditional model is tested under its assumptions; changed staffing/service times are distinguished from repeated failures under matching conditions.',
 'Equal payments and need-based fairness are distinct; eligibility error and access costs qualify an equitable intention.',
 'Price coordination, deficient aggregate spending and circular resource use are separate mechanisms; no claim that recycling removes opportunity cost.'
])
add('micro-structured-',[
 'Rail and bicycles can be complements; demand shifts right, with supply responsiveness and safe-route access qualifying the outcome.',
 'Input costs shift pottery supply left rather than demand; the staged simultaneous demand decline makes quantity fall but price ambiguous.',
 'Below-equilibrium posted prices create excess demand; price rations and incentivizes supply unless a later legal cap blocks adjustment.',
 'Initial-base PED and actual revenue growth are distinguished; elastic quantity response to a price cut raises revenue by 3.50%.',
 'Negative YED identifies an inferior good; it is an income shift, not evidence of an upward own-price demand curve.',
 'Short/long-run PES reflect time and adjustable capacity; this common-content task does not require a manufactured-versus-primary-product comparison.',
 'A binding rent ceiling expands demand and contracts supply, with uneven access and maintenance effects; complementary subsidies or queues do not erase scarcity.',
 'A floor with a purchase guarantee creates surplus procurement and fiscal/storage costs; producer receipts are not a net-welfare measure.',
 'Legal tax remittance and economic incidence differ; relative elasticities, substitutes and evasion determine outcomes.',
 'A producer subsidy shifts supply down; ownership, authorization, liquidity and installer capacity can prevent equitable take-up.',
 'Production damage requires MSC above MPC and MSB=MPB, giving excessive private output; monitoring and seasonal damage qualify standards.',
 'Vaccination external benefits require MSB above MPB; trust, appointments and travel can bind even with low fees.',
 'Broadcast warning service is non-rival/non-excludable within coverage; a coded version changes excludability and public finance need not imply state production.',
 'Income/substitution effects and diminishing marginal utility are AHL; inferior-good or relative-price changes are staged qualifications.',
 'Diminishing marginal returns holds a factor fixed; higher wages and altered plant scale are distinct causes or changed assumptions.',
 'Numerical surplus is AHL; triangles use correct price intercepts, and producer surplus is not profit net of fixed cost.',
 'Bounded rationality/defaults are AHL; practical opt-out freedom and affordability affect whether enrolment improves welfare.',
 'Adverse selection concerns hidden pre-contract risk; post-contract maintenance is moral hazard and screening has costs.',
 'Perfect competition price-taking and rising-MC profit choice are conditional on entry and shutdown assumptions; licensing can prevent normal-profit adjustment.',
 'All allowed discrete revenues/profits were enumerated; the revenue maximum differs from the maximum-profit quantity.',
 'Oligopoly interdependence is not proof of collusion; non-price quality gains and switching barriers may coexist.',
 'Unequal resource ownership and human-capital access transmit income gains unevenly; digital exclusion and discrimination require distinct responses.'
])
add('micro-essay-',[
 'Indirect tax analysis covers wedge, price/quantity and incidence; evaluation compares actual studied packaging policies, switching finance and enforcement.',
 'Rent-control evaluation distinguishes incumbent benefit from new-applicant access, duration and complementary public construction.',
 'Common-access fishery rivalry, non-exclusion and intertemporal stock effects support comparison of rights, quotas and monitoring across jurisdictions.',
 'Public-good financing is separated from effective procurement, coverage and maintenance; private contracted production remains possible.',
 'AHL oligopoly analysis weighs scale/innovation against exclusion and power; concentration alone is not collusion or lack of contestability.',
 'AHL choice architecture is compared with financial incentives; transparent freedom, affordability and persistence inform the judgment.'
])
add('micro-data-',[
 'Refill festival demand shifts right and resin-cost supply shifts left; quantity effect is ambiguous. Controlled PED is not evidence of the policy demand shift.',
 'Storm destruction shifts supply left; storage can reduce perishability but cannot instantly replace a harvest or biological growing time.',
 'Car-use consumption damage uses MPB above MSB. Bus subsidies work differently at full peak capacity and with spare off-peak seats.',
 'Literacy benefits spill to children/others; fee subsidies, childcare and scarce teachers are separate monetary and non-price constraints.',
 'Wetland absorption is a rival common resource. Formal collection substitutes away from damaging disposal; uniform charges have distributional/coverage risks.',
 'A broadcast alert is a public service distinct from a rival private filter; standards address production damage and require credible monitoring.'
])
add('micro-policy-',[
 'Tax wedge, receipts and no-externality loss are model calculations; actual external damage can justify a corrective policy with transition support.',
 'Subsidy buyer price and producer receipt differ; fiscal spending is not automatically welfare gain, and renters/installer constraints matter.',
 'Constant aggregate damage gives efficient output and welfare triangle; firm heterogeneity and measurement costs qualify output versus emissions charging.',
 'All monopoly schedule outputs were compared; marginal and average costs are distinct and access/innovation judgments are not inferred from profit alone.',
 'Ceiling quantities, legal sales and conditional foreign procurement are distinct; low prices do not ensure access for every household.',
 'Alternative fully adjusted plant scales indicate economies of scale; average incremental cost is not exact MC and does not contradict short-run diminishing returns.'
])
add('macro-structured-',[
 'Expenditure GDP excludes transfers and imported output; data-selection and arithmetic marks are distinct.',
 'GNI adds net resident factor income from abroad; outward payments lower GNI relative to GDP.',
 'Deflation converts the index to a ratio; CPI and GDP-deflator coverage differs.',
 'Both output and population growth enter real GDP per person; billion/million conversion is explicit.',
 'A cyclical downturn concerns actual activity and labour demand; hysteresis may reduce potential in the staged alternative.',
 'Confidence shifts AD right; imports leak from domestic demand and near-capacity supply changes output/price proportions.',
 'Imported input costs shift SRAS left; appreciation, contracts and energy substitution qualify magnitude or timing.',
 'Electricity/logistics raise potential capacity; demand, maintenance and complementary skills determine utilization.',
 'Measured unemployment uses the active labour force; discouraged workers affect interpretation and are not added to its denominator.',
 'Positive but slower CPI growth is disinflation; fixed nominal claims redistribute purchasing power under unexpected inflation.',
 'Expected real interest uses the explicitly approximate relation; debt/confidence constrain transmission.',
 'Lorenz movement toward equality reduces measured Gini, but real income levels and coverage determine poverty and welfare.',
 'Relative poverty can increase with a rising median while a fixed real basic-needs threshold is unchanged; local costs and non-income services qualify it.',
 'AHL marginal income bands are applied separately; average and marginal rates are distinguished explicitly.',
 'AHL multiplier uses all given leakages and includes the initial expenditure; actual effects remain conditional on capacity and behavior.',
 'AHL open-market liquidity and bond-yield mechanism is explained without awarding a mark merely for an optional diagram instruction.',
 'AHL Phillips-curve movement is conditional on expectations; supply shocks and natural-rate changes are not movements on one fixed curve.',
 'Apprenticeships target structural mismatch, but vacancies, transport and completion matter; demand expansion alone does not create missing skills.'
])
add('macro-essay-',[
 'Cost-push inflation creates a policy conflict; duration, expectations and structural unemployment qualify priorities.',
 'Real per-capita output is an incomplete welfare measure; composition, distribution, environment and services determine gains.',
 'Lower rates transmit through spending and AD but debt, credit risk and effective lower bounds can weaken the response.',
 'AHL multiplier/crowding-out evaluation contrasts timely useful spending, capacity benefits, lags and financing risks.',
 'Market-based and interventionist supply measures are matched to competition, infrastructure or mobility constraints rather than ranked unconditionally.',
 'Progressive redistribution and opportunity policies have different timing and implementation/incentive effects; discrimination can persist after schooling.'
])
add('macro-data-',[
 'Weaker exports shift AD left; timely maintenance can offset weak demand, with heavy debt limiting monetary transmission.',
 'Fuel shock shifts SRAS left; targeted transfers protect income without pretending to remove the supply cause, and broad transfers may add AD pressure.',
 'Overseas tourism is a service export; spare rooms support early recovery, then staffing/airport bottlenecks constrain further demand support.',
 'Vacancies plus skill gaps imply structural mismatch; apprenticeships and travel support address different barriers.',
 'Mean PPP/real output gains can coexist with deprivation; cash redistribution and health/education services address different horizons.',
 'Clean-energy investment has imported-input leakage and engineer opportunity cost; long-run reliability gains require maintenance and complementary skills.'
])
add('macro-policy-',[
 'AHL fixed-price multiplier spending, debt ratio and additional-interest bill are distinct; greater import leakage lowers the modeled output gain.',
 'AHL tax bands and tax-exclusive consumption charge are separate; eight Lorenz cumulative values are assessed as four before/after pairs, then plotted.',
 'AHL weighted CPI uses fixed base quantities and expenditure weights; expected real interest uses an explicit approximation and policy weighs supply-shock costs.',
 'AHL debt stock versus deficit flow is explicit; overall deficit includes interest once, and ratio change is percentage points rather than percent growth.'
])
add('global-structured-',[
 'Trade gives capital/technology access and scale opportunities but domestic adjustment and complementary skills/logistics determine distribution of benefits.',
 'AHL comparative advantage uses relative opportunity costs and strict internal terms-of-trade bounds, not absolute-output rankings.',
 'Small-country non-prohibitive tariff raises domestic output and lowers imports; partial pass-through or prohibitive levels are staged qualifications.',
 'Binding quota raises domestic price; free licences create private rents, while auctioning and non-binding demand change who gains.',
 'Infant-industry learning needs credible future competitiveness and review; permanent protection and available training alternatives weaken the case.',
 'FTA, customs union and common-market features are distinguished; common monetary institutions are an additional integration feature.',
 'AHL trade creation replaces high-cost domestic supply, diversion replaces cheaper outsiders; private price reductions do not alone prove welfare gain.',
 'Currency quotation is USD per crown, so receipt conversion divides; depreciation raises import-dependent costs.',
 'Investment inflows shift currency demand under common 4.5 exchange determinants; this does not require AHL account-link analysis.',
 'Overvalued fixed parity creates excess domestic-currency supply; buying crowns uses finite foreign reserves and is distinct from devaluation.',
 'Signed goods and all non-goods net entries determine current account; a deficit label is not a second accuracy award for the same signed result.',
 'Remittances, FDI and debt forgiveness have distinct accounts; domestic GDP, imported spending and resident factor income are not conflated.',
 'AHL persistent-deficit financing and foreign-currency debt expose servicing/refinancing risk; productive use and currency denomination qualify it.',
 'AHL Marshall-Lerner uses absolute elasticity sum and initially balanced trade; a J recovery is not guaranteed under weak responses.',
 'Sustainability requires intergenerational resources, not current extraction GDP alone; reinvestment and irreversible damage must be distinguished.',
 'PPP average income, health and education are distinct dimensions; composite weights and national averages can hide unequal capability.',
 'Low-income/saving/investment feedback is conditional; credit needs viable markets, appropriate timing and accessible collateral.',
 'Processing exports may diversify value added but remain exposed to the same crop; power, customs and credible markets constrain success.'
])
add('global-essay-',[
 'Temporary trade protection is evaluated against learning spillovers, credible exit, consumer/downstream cost and retaliation.',
 'AHL integration evaluation includes creation/diversion and possible monetary-union trade-offs, with uneven regional adjustment.',
 'AHL fixed-versus-floating evaluation weighs reserve/monetary constraints, trade structure and foreign-currency balance sheets.',
 'Composite development indices widen coverage but weights, data gaps and average scores can conceal different local needs.',
 'Diversification requires skills, logistics and a genuinely different risk base; staged alternative conditions replace contradictory baseline features.',
 'FDI versus aid is evaluated through domestic linkages, governance, repatriation and recurrent financing rather than a universal ranking.'
])
add('global-data-',[
 'Commodity demand shock reduces farm/export income; processing needs roads and markets while transfers meet immediate needs.',
 'Lower holiday-service demand reduces currency demand; depreciation raises imported input costs and may help tourism subject to capacity and responsiveness.',
 'PPP averages and composite ranks do not locate water/school deprivation; components and disaggregated evidence support allocation.',
 'School grants fund capital but girls need travel/water/care access and recurrent teacher/maintenance resources.',
 'Common-content FTA access, paperwork and scale effects are evaluated without requiring AHL trade creation/diversion.',
 'Development indebtedness/port-loan barriers are common 4.9; no mandatory AHL persistent-current-account framework is imposed.'
])
add('global-policy-',[
 'AHL tariff quantities, consumer/producer trapezia, receipts and two distortion triangles reconcile under a non-prohibitive small-country model.',
 'AHL comparative advantage raises potential combined output, but the specified trade bundles need not be preferred by every economy or worker.',
 'AHL immediate import repricing and later stated volume scenario are separate; PED sum is a conditional criterion, not an exact discrete forecast.',
 'AHL poverty–environment feedback is contextual; all programmes fit the first budget exactly but exceed the second, requiring priorities or phasing.'
])

files={};records=[]
for p in sorted((ROOT/'content/ib/economics').glob('*.json')):
    raw=p.read_bytes();assert b'\r' not in raw and not raw.startswith(b'\xef\xbb\xbf');files[p.name]=hashlib.sha256(raw).hexdigest()
    for q in json.loads(raw):
        row=family_by_id[q['id']];family=row['family'];assert family in notes
        canonical=hashlib.sha256(json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest();assert canonical==row['sha256']
        fig=figure_by_id[q['id']];assert fig['schema']==fig['promptPrivacy']=='passed'
        n=numeric['records'].get(q['id'],[])
        record={'id':q['id'],'status':'passed','family':family,'sha256':canonical,'scope':{'status':'passed','syllabusCode':q['syllabusCode'],'level':q['level'],'paper':q['examStyle']},'semanticReview':notes[family],'variantEvidenceReviewed':row.get('variantEvidence','Displayed numeric inputs and their resulting quantities were checked; no merely renamed qualitative duplicate accepted.'),'variantCausalInterpretation':row.get('variantReasoning'),'markingReview':'Distinct analytic requirements or task/variant-bound best-fit bands; no separate additive marks for IND guidance. Full response allocations and calculator conditions checked.','numericReview':{'status':'passed' if n else 'not-requested','parts':len(n),'reference':'economics-independent-numeric.json#records/'+q['id'],'coverage':'All explicit numerical requests reconstructed from public serialized data.' if n else 'No explicit calculation request; economic causal reasoning and any stated numeric illustration reviewed semantically.'},'diagramReview':fig['diagram'],'readMethod':'Family baseline plus every subsequent variant field delta, including all stems, prompts, scheme changes and rubric focus; repeated rubric wording separately checked across every record.'}
        records.append(record)
assert len(records)==360 and len(notes)==122 and len({r['id'] for r in records})==360
report={'status':'passed','questionCount':360,'reviewer':'Independent second authoring agent; not a human IB examiner or IB endorsement','canonicalFiles':files,'canonicalization':'Files: exact UTF-8 LF bytes without BOM. Records: Unicode JSON with sorted keys and compact separators, SHA-256.','families':122,'numericCoverage':{'records':numeric['recordsReconstructed'],'parts':numeric['partsWithNumericalRequests'],'assertions':numeric['independentResultAssertions']},'semanticCoverage':{'records':360,'families':122,'method':'All family baselines and every variant delta read; source boundaries and marking demands cross-checked with current official guide and 2027 examiner instructions.'},'diagramCoverage':{'rendered':148,'distinctDesigns':21,'visuallyInspectedDesigns':21,'method':'Every SVG freshly rasterized; all 21 distinct content/label designs visually inspected on three new contact sheets. Text and geometry mapping checked for every record.','reference':'economics-independent-schema-figures.json'},'officialSources':['https://xmltwo.ibo.org/publications/EAD/2026_EN/GR3/GR3-Econ_EN_24.pdf','https://ibpublishing.ibo.org/exinst/apps/exinst/index.html?chapter=3&doc=EX_instructions_2027_e&part=10'],'fixesReference':'economics-independent-fixes.json','limitations':['Fictional practice cases are not official examination papers or empirical policy evidence.','Paper 1 real-world examples are supplied by the student; this review does not certify an exhaustive list of historical examples.','Diagram sketches are explicitly schematic; geometric direction/labels were reviewed, not a claim that all schematic coordinates reproduce quantitative model parameters.','The review is bound to the listed hashes; later substantive edits require re-review.'],'records':records}
(OUT/'economics-independent-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['records','officialSources','limitations']},indent=2))
